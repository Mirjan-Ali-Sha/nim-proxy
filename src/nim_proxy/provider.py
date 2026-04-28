import httpx
import json
import uuid
from typing import AsyncGenerator, Dict, Any, List
from .config import settings
from loguru import logger

class NIMProvider:
    def __init__(self):
        self.api_key = settings.NVIDIA_NIM_API_KEY
        self.base_url = "https://integrate.api.nvidia.com/v1"

    async def stream_chat(self, model: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] = None, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        if tools:
            payload["tools"] = tools

        # Remove any anthropic-specific flags that might have leaked into kwargs
        payload.pop("beta", None)
        
        if settings.VERBOSE:
            logger.debug(f"NIM Request Payload: {json.dumps({k:v for k,v in payload.items() if k != 'messages'}, indent=2)}")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers=headers) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"NIM API error: {response.status_code} - {error_text.decode()}")
                        yield {"error": f"NIM API error: {response.status_code}"}
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                yield json.loads(data_str)
                            except json.JSONDecodeError:
                                logger.error(f"Failed to decode NIM SSE data: {data_str}")
            except Exception as e:
                logger.error(f"NIM API Connection Error ({type(e).__name__}): {str(e)}")
                yield {"error": f"Connection error: {type(e).__name__}"}

    async def chat(self, model: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        if tools:
            payload["tools"] = tools

        payload.pop("beta", None)
        if settings.VERBOSE:
            logger.debug(f"NIM Request Payload: {json.dumps({k:v for k,v in payload.items() if k != 'messages'}, indent=2)}")

        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                if response.status_code != 200:
                    logger.error(f"NIM API error: {response.status_code} - {response.text}")
                    return {"error": f"NIM API error: {response.status_code}"}
                return response.json()
            except Exception as e:
                logger.error(f"NIM API Connection Error ({type(e).__name__}): {str(e)}")
                return {"error": f"Connection error: {type(e).__name__}"}
