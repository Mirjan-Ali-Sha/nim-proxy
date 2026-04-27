import httpx
import asyncio
import json

async def test_proxy():
    url = "http://localhost:8082/v1/messages"
    headers = {
        "x-api-key": "sk-ant-dummy",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello, are you working through NIM?"}
        ],
        "stream": True
    }

    print("🚀 Sending test request to proxy...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    print(f"❌ Error: {response.status_code}")
                    print(await response.aread())
                    return

                print("📥 Receiving stream:")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if data["type"] == "content_block_delta":
                            text = data["delta"].get("text", "")
                            print(text, end="", flush=True)
                        elif data["type"] == "message_stop":
                            print("\n✅ Test Complete!")
    except Exception as e:
        print(f"❌ Connection Failed: {str(e)}")

if __name__ == "__main__":
    print("Starting test...")
    asyncio.run(test_proxy())
