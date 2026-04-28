import json
from typing import Any, Dict

class SSEBuilder:
    def __init__(self, message_id: str, model: str):
        self.message_id = message_id
        self.model = model
        self.next_index = 0
        self.thinking_started = False

    def format_event(self, event_type: str, data: Dict) -> str:
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    def start_thinking_block(self) -> str:
        self.thinking_started = True
        return self.content_block_start(self.next_index, "thinking", thinking="")

    def emit_thinking_delta(self, content: str) -> str:
        return self.content_block_delta(self.next_index, "thinking_delta", content)

    def stop_thinking_block(self) -> str:
        self.thinking_started = False
        res = self.content_block_stop(self.next_index)
        self.next_index += 1
        return res

    def start_text_block(self) -> str:
        return self.content_block_start(self.next_index, "text")

    def stop_text_block(self) -> str:
        res = self.content_block_stop(self.next_index)
        self.next_index += 1
        return res

    def start_tool_block(self, id: str, name: str) -> str:
        return self.content_block_start(self.next_index, "tool_use", id=id, name=name)

    def stop_tool_block(self) -> str:
        res = self.content_block_stop(self.next_index)
        self.next_index += 1
        return res

    def message_start(self) -> str:
        return self.format_event(
            "message_start",
            {
                "type": "message_start",
                "message": {
                    "id": self.message_id,
                    "type": "message",
                    "role": "assistant",
                    "model": self.model,
                    "content": [],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                },
            },
        )

    def content_block_start(self, index: int, block_type: str, **kwargs) -> str:
        data = {
            "type": "content_block_start",
            "index": index,
            "content_block": {"type": block_type, **kwargs},
        }
        return self.format_event("content_block_start", data)

    def content_block_delta(self, index: int, delta_type: str, content: str) -> str:
        data = {
            "type": "content_block_delta",
            "index": index,
            "delta": {"type": delta_type, content.replace("_delta", ""): content if "_delta" not in delta_type else content},
        }
        # Special handling for text_delta vs input_json_delta
        if delta_type == "text_delta":
            data["delta"] = {"type": "text_delta", "text": content}
        elif delta_type == "input_json_delta":
            data["delta"] = {"type": "input_json_delta", "partial_json": content}
        elif delta_type == "thinking_delta":
            data["delta"] = {"type": "thinking_delta", "thinking": content}

        return self.format_event("content_block_delta", data)

    def content_block_stop(self, index: int) -> str:
        return self.format_event("content_block_stop", {"type": "content_block_stop", "index": index})

    def message_delta(self, stop_reason: str = "end_turn") -> str:
        return self.format_event(
            "message_delta",
            {"type": "message_delta", "delta": {"stop_reason": stop_reason, "stop_sequence": None}, "usage": {"output_tokens": 0}},
        )

    def message_stop(self) -> str:
        return self.format_event("message_stop", {"type": "message_stop"})
