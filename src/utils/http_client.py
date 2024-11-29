import aiohttp
import asyncio

class HttpClient:
    async def send_request(self, method, url, headers=None, body=None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=body if body else None,
                    verify_ssl=False,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    status = response.status
                    text = await response.text()
                    return {'status': status, 'text': text}
                    
        except aiohttp.ClientSSLError as e:
            raise Exception(f"SSL 证书验证失败: {str(e)}")
        except asyncio.TimeoutError:
            raise Exception("请求超时")
        except aiohttp.ClientConnectorError:
            raise Exception("连接错误，请检查网络或URL是否正确")
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}") 