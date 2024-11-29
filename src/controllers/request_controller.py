import asyncio
from utils.http_client import HttpClient

class RequestController:
    def __init__(self):
        self.http_client = HttpClient()
    
    async def send_request(self, method, url, headers, body):
        try:
            return await self.http_client.send_request(method, url, headers, body)
        except Exception as e:
            print(f"Error sending request: {e}")
            return None 