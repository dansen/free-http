import requests
from utils.http_client import HttpClient

class RequestController:
    def __init__(self):
        self.http_client = HttpClient()
    
    def send_request(self, method, url, headers, body):
        try:
            return self.http_client.send_request(method, url, headers, body)
        except Exception as e:
            print(f"Error sending request: {e}")
            return None 