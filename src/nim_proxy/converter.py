import json
import uuid
from typing import Any, Optional, Dict, List
from pydantic import BaseModel

class AnthropicToOpenAIConverter:
    @staticmethod
    def convert_messages(anthropic_messages: List[Dict[str, Any]], enable_thinking: bool = False) -> List[Dict[str, Any]]:
        result = []
        for msg in anthropic_messages:
            role = msg.get("role")
            content = msg.get("content")
            
            if isinstance(content, str):
                result.append({"role": role, "content": content})
            elif isinstance(content, list):
                text_parts = []
                for block in content:
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        # Convert tool use to OpenAI style assistant message
                        result.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [{
                                "id": block.get("id"),
                                "type": "function",
                                "function": {
                                    "name": block.get("name"),
                                    "arguments": json.dumps(block.get("input", {}))
                                }
                            }]
                        })
                    elif block.get("type") == "tool_result":
                        # Convert tool result to OpenAI tool role
                        result.append({
                            "role": "tool",
                            "tool_call_id": block.get("tool_use_id"),
                            "content": block.get("content", "")
                        })
                
                if text_parts:
                    result.append({"role": role, "content": "\n\n".join(text_parts)})
        
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
