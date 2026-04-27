import time
from typing import Dict, Any, Optional
from .config import settings

def try_optimize(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not settings.ENABLE_OPTIMIZATIONS:
        return None
        
    messages = body.get("messages", [])
    if not messages:
        return None
        
    last_msg = messages[-1].get("content", "")
    if isinstance(last_msg, list):
        last_msg = " ".join([b.get("text", "") for b in last_msg if b.get("type") == "text"])
        
    # 1. Quota Probes
    if "This is a probe" in last_msg or "quota" in last_msg.lower():
        return {
            "id": f"opt_{int(time.time())}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Quota probe successful. You have sufficient balance."}],
            "model": body.get("model"),
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 10}
        }
        
    # 2. Title Generation
    if "Generate a concise title" in last_msg or "thread title" in last_msg.lower():
        return {
            "id": f"opt_{int(time.time())}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "NIM Proxy Session"}],
            "model": body.get("model"),
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 50, "output_tokens": 5}
        }
        
    return None
