from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
import json

class ResponsePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 状态码显示
        self.status_label = QLabel("Status: ")
        
        # 响应内容
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.response_text)
        
    def update_response(self, response):
        if response:
            self.status_label.setText(f"Status: {response['status']}")
            try:
                # 尝试格式化 JSON 响应
                json_response = json.loads(response['text'])
                formatted_response = json.dumps(json_response, indent=2, ensure_ascii=False)
                self.response_text.setText(formatted_response)
            except:
                # 如果不是 JSON 格式，直接显示原文
                self.response_text.setText(response['text'])
        else:
            self.status_label.setText("Status: Error")
            self.response_text.setText("请求失败，请检查网络连接或URL是否正确") 