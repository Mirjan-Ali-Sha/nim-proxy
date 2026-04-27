import uuid
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from .config import settings
from .provider import NIMProvider
from .converter import AnthropicToOpenAIConverter
from .sse import SSEBuilder
from .router import ModelRouter
from .optimizations import try_optimize
from loguru import logger

app = FastAPI(title="NVIDIA NIM Claude Proxy")
provider = NIMProvider()

@app.get("/")
@app.head("/")
async def root():
    return {"status": "ok", "proxy": "nim-proxy"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/v1/models")
async def list_models():
    return {
        "data": [
            {"id": "claude-3-opus-20240229", "type": "model"},
            {"id": "claude-3-5-sonnet-20240620", "type": "model"},
            {"id": "claude-3-haiku-20240307", "type": "model"}
        ]
    }

@app.get("/v1/users/me")
async def mock_user_me():
    return {
        "id": "user_01ABC",
        "email": "mirjanalisha@gmail.com",
        "full_name": "Mirjan Ali Sha",
        "capabilities": ["can_use_claude_code", "can_use_billing"]
    }

@app.get("/v1/organizations")
async def mock_orgs():
    return {
        "data": [{
            "id": "org_01XYZ",
            "name": "NIM Proxy Org",
            "role": "admin",
            "capabilities": ["can_use_billing"]
        }]
    }

@app.post("/v1/messages")
async def create_message(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # 1. Try Optimizations
    optimized = try_optimize(body)
    if optimized:
        return JSONResponse(optimized)

    # 2. Resolve Model
    claude_model = body.get("model", "")
    nim_model = ModelRouter.resolve(claude_model)
    logger.info(f"Routing {claude_model} -> {nim_model}")

    # 3. Handle Streaming
    stream = body.get("stream", False)
    
    # 4. Convert Messages & Tools
    openai_messages = AnthropicToOpenAIConverter.convert_messages(
        body.get("messages", []), 
        enable_thinking=settings.ENABLE_THINKING
    )
    system = body.get("system")
    if system:
        system_msg = AnthropicToOpenAIConverter.convert_system_prompt(system)
        if system_msg:
            openai_messages.insert(0, system_msg)
            
    tools = None
    if "tools" in body:
        tools = AnthropicToOpenAIConverter.convert_tools(body["tools"])

    # Extract Generation Parameters
    temperature = body.get("temperature", settings.DEFAULT_TEMPERATURE)
    top_p = body.get("top_p", settings.DEFAULT_TOP_P)
    max_tokens = body.get("max_tokens", settings.DEFAULT_MAX_TOKENS)
    
    thinking = body.get("thinking")
    reasoning_effort = settings.DEFAULT_REASONING_EFFORT
    if thinking and isinstance(thinking, dict):
        budget = thinking.get("budget_tokens", 0)
        if budget > 2000: reasoning_effort = "high"
        elif budget > 1000: reasoning_effort = "medium"
        else: reasoning_effort = "low"
    
    reasoning_effort = body.get("reasoning_effort", reasoning_effort)

    # 5. Call NIM API with Strict Fallback
    async def try_call(model_to_use: str):
        extra_body = {
            "chat_template_kwargs": {
                "enable_thinking": settings.ENABLE_THINKING,
                "clear_thinking": False
            }
        } if "z-ai" in model_to_use else {}

        if not stream:
            return await provider.chat(
                model=model_to_use,
                messages=openai_messages,
                tools=tools,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                reasoning_effort=reasoning_effort,
                frequency_penalty=body.get("frequency_penalty", 0),
                presence_penalty=body.get("presence_penalty", 0),
                extra_body=extra_body
            )
        else:
            return provider.stream_chat(
                model=model_to_use,
                messages=openai_messages,
                tools=tools,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                reasoning_effort=reasoning_effort,
                frequency_penalty=body.get("frequency_penalty", 0),
                presence_penalty=body.get("presence_penalty", 0),
                extra_body=extra_body
            )

    result = await try_call(nim_model)
    
    if not stream:
        if "error" in result:
            logger.warning(f"Primary model {nim_model} failed. Falling back...")
            result = await try_call(settings.MODEL_FALLBACK)
            if "error" in result:
                return JSONResponse({"error": {"type": "api_error", "message": result["error"]}}, status_code=502)
        
        return JSONResponse(AnthropicToOpenAIConverter.convert_response(result, claude_model))

    async def event_generator(stream_result):
        message_id = f"msg_{uuid.uuid4()}"
        sse = SSEBuilder(message_id, claude_model)
        yield sse.message_start()
        
        state = {"text_started": False, "index": 0}
        fallback_triggered = False
        
        async def handle_stream(s):
            async for chunk in s:
                if "error" in chunk:
                    yield chunk
                    break
                events = process_chunk(chunk, sse, state)
                for event in events:
                    yield event

        async for item in handle_stream(stream_result):
            if isinstance(item, dict) and "error" in item:
                if not fallback_triggered:
                    logger.warning(f"Stream error on {nim_model}. Attempting fallback...")
                    fallback_triggered = True
                    fallback_stream = await try_call(settings.MODEL_FALLBACK)
                    async for f_item in handle_stream(fallback_stream):
                        if isinstance(f_item, dict) and "error" in f_item: break
                        yield f_item
                    break
                else:
                    yield sse.format_event("error", {"type": "error", "error": {"message": item["error"]}})
                    break
            yield item

        if state["text_started"]:
            yield sse.content_block_stop(state["index"])
        yield sse.message_delta("end_turn")
        yield sse.message_stop()

    def process_chunk(chunk, sse, state):
        events = []
        choices = chunk.get("choices", [])
        if not choices: return events
            
        delta = choices[0].get("delta", {})
        
        # 1. Handle Reasoning (Native)
        reasoning = delta.get("reasoning_content")
        if reasoning:
            if not sse.thinking_started:
                if not state["text_started"]:
                    events.append(sse.start_thinking_block())
                    sse.thinking_started = True 
                else:
                    events.append(sse.content_block_delta(state["index"], "text_delta", f"\n<think>\n{reasoning}"))
                    return events
            
            if sse.thinking_started:
                if state["text_started"]:
                    events.append(sse.content_block_delta(state["index"], "text_delta", reasoning))
                else:
                    events.append(sse.emit_thinking_delta(reasoning))

        # 2. Handle Tool Calls
        tool_calls = delta.get("tool_calls")
        if tool_calls:
            if sse.thinking_started:
                if state["text_started"]:
                    events.append(sse.content_block_delta(state["index"], "text_delta", "\n</think>\n\n"))
                else:
                    events.append(sse.stop_thinking_block())
                    state["index"] += 1
                sse.thinking_started = False
            
            for tc in tool_calls:
                if tc.get("id"):
                    events.append(sse.content_block_start(state["index"], "tool_use", id=tc["id"], name=tc["function"].get("name", "")))
                if tc["function"].get("arguments"):
                    events.append(sse.content_block_delta(state["index"], "input_json_delta", tc["function"]["arguments"]))
            return events

        # 3. Handle Content
        content = delta.get("content")
        if content:
            if sse.thinking_started:
                if state["text_started"]:
                    events.append(sse.content_block_delta(state["index"], "text_delta", "\n</think>\n\n"))
                else:
                    events.append(sse.stop_thinking_block())
                    state["index"] += 1
                sse.thinking_started = False
            
            if not state["text_started"]:
                events.append(sse.content_block_start(state["index"], "text"))
                state["text_started"] = True
            
            events.append(sse.content_block_delta(state["index"], "text_delta", content))

        return events

    return StreamingResponse(event_generator(result), media_type="text/event-stream")
