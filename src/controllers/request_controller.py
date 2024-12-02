import asyncio
from utils.http_client import HttpClient

class RequestController:
    def __init__(self):
        self.http_client = HttpClient()
    
    async def send_request(self, method, url, headers, body, timeout=30):
        try:
            # 创建带有指定超时时间的新客户端
            client = HttpClient(timeout=timeout)
            return await client.send_request(method, url, headers, body)
        except Exception as e:
            print(f"Error sending request: {e}")
            return None