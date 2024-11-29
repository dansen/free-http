import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class HttpClient:
    def send_request(self, method, url, headers=None, body=None):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body if body else None,
                verify=False,
                timeout=30
            )
            return response
        except requests.exceptions.SSLError as e:
            raise Exception(f"SSL 证书验证失败: {str(e)}")
        except requests.exceptions.Timeout:
            raise Exception("请求超时")
        except requests.exceptions.ConnectionError:
            raise Exception("连接错误，请检查网络或URL是否正确")
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}") 