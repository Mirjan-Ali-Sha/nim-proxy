import json
import uuid
from typing import Any, Optional, Dict, List
from pydantic import BaseModel
from .config import settings

class AnthropicToOpenAIConverter:
    @staticmethod
    def convert_messages(anthropic_messages: List[Dict[str, Any]], enable_thinking: bool = False) -> List[Dict[str, Any]]:
        result = []
        for msg in anthropic_messages:
            role = msg.get("role")
            content = msg.get("content")
            
            # Simple string content
            if isinstance(content, str):
                result.append({"role": role, "content": content})
                continue

            # Complex list content
            if isinstance(content, list):
                openai_msg = {"role": role, "content": ""}
                tool_calls = []
                text_parts = []
                reasoning_parts = []
                
                for block in content:
                    b_type = block.get("type")
                    if b_type == "text":
                        text_parts.append(block.get("text", ""))
                    elif b_type == "thinking":
                        # Try to restore as reasoning_content for models that support it
                        reasoning_parts.append(block.get("thinking", ""))
                    elif b_type == "tool_use":
                        tool_calls.append({
                            "id": block.get("id"),
                            "type": "function",
                            "function": {
                                "name": block.get("name"),
                                "arguments": json.dumps(block.get("input", {}))
                            }
                        })
                    elif b_type == "tool_result":
                        # Tool results must be individual messages in OpenAI
                        result.append({
                            "role": "tool",
                            "tool_call_id": block.get("tool_use_id"),
                            "content": str(block.get("content", ""))
                        })
                
                # Combine text parts
                full_text = "\n\n".join(text_parts).strip()
                reasoning_text = "\n\n".join(reasoning_parts).strip()
                
                if role == "assistant":
                    # Check if ANY configured model is a reasoning model
                    target_models = [settings.MODEL_OPUS, settings.MODEL_SONNET, settings.MODEL_HAIKU]
                    is_reasoning_model = any(any(kw in str(m).lower() for kw in ["deepseek", "glm", "qwq", "reasoning"]) for m in target_models)
                    
                    if reasoning_text:
                        if is_reasoning_model:
                            openai_msg["reasoning_content"] = reasoning_text
                        else:
                            # Fallback to tags for standard models
                            full_text = f"<think>\n{reasoning_text}\n</think>\n\n{full_text}".strip()
                    
                    if tool_calls:
                        openai_msg["content"] = full_text if full_text else None
                        openai_msg["tool_calls"] = tool_calls
                        result.append(openai_msg)
                    elif full_text or (reasoning_text and is_reasoning_model):
                        openai_msg["content"] = full_text if full_text else ""
                        result.append(openai_msg)
                elif role == "user" and full_text:
                    openai_msg["content"] = full_text
                    result.append(openai_msg)
        
        return result

    @staticmethod
    def convert_response(openai_resp: Dict[str, Any], claude_model: str) -> Dict[str, Any]:
        choices = openai_resp.get("choices", [])
        if not choices:
            return {"error": "No choices in OpenAI response"}
        
        choice = choices[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        reasoning = message.get("reasoning_content")
        
        anthropic_content = []
        if reasoning:
            # Wrap reasoning in tags for compatibility
            anthropic_content.append({"type": "text", "text": f"<think>\n{reasoning}\n</think>\n\n"})
        if content:
            anthropic_content.append({"type": "text", "text": content})
            
        # Handle tool calls
        tool_calls = message.get("tool_calls", [])
        for tc in tool_calls:
            anthropic_content.append({
                "type": "tool_use",
                "id": tc.get("id"),
                "name": tc.get("function", {}).get("name"),
                "input": json.loads(tc.get("function", {}).get("arguments", "{}"))
            })

        return {
            "id": openai_resp.get("id", f"msg_{uuid.uuid4()}"),
            "type": "message",
            "role": "assistant",
            "model": claude_model,
            "content": anthropic_content,
            "stop_reason": "end_turn" if choice.get("finish_reason") == "stop" else "tool_use" if tool_calls else "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": openai_resp.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": openai_resp.get("usage", {}).get("completion_tokens", 0)
            }
        }

    @staticmethod
    def convert_tools(tools: List[Any]) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {})
                }
            } for t in tools
        ]

    @staticmethod
    def convert_system_prompt(system_prompt: Any) -> Optional[Dict[str, Any]]:
        if not system_prompt:
            return None
        
        content = ""
        if isinstance(system_prompt, str):
            content = system_prompt
        elif isinstance(system_prompt, list):
            content = "\n\n".join([b.get("text", "") for b in system_prompt if b.get("type") == "text"])
            
        if not content:
            return None
            
        return {"role": "system", "content": content}
