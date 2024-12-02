import aiohttp
import asyncio
import chardet

class HttpClient:
    def __init__(self, timeout=30):
        self.timeout = timeout

    async def send_request(self, method, url, headers=None, body=None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=body if body else None,
                    verify_ssl=False,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    status = response.status
                    # 读取原始字节数据
                    content = await response.read()
                    
                    # 检测编码
                    encoding = response.get_encoding()
                    if not encoding:
                        detected = chardet.detect(content)
                        encoding = detected['encoding'] or 'utf-8'
                    
                    # 使用检测到的编码解码内容
                    text = content.decode(encoding, errors='replace')
                    
                    return {'status': status, 'text': text}
                    
        except aiohttp.ClientSSLError as e:
            return {
                'status': 495,  # SSL Certificate Error
                'text': f"SSL 证书验证失败: {str(e)}"
            }
        except asyncio.TimeoutError:
            return {
                'status': 408,  # Request Timeout
                'text': f"请求超时 (超过 {self.timeout} 秒)"
            }
        except aiohttp.ClientConnectorError:
            return {
                'status': 503,  # Service Unavailable
                'text': "连接错误，请检查网络或URL是否正确"
            }
        except Exception as e:
            return {
                'status': 500,  # Internal Server Error
                'text': f"请求失败: {str(e)}"
            }