from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout
from PyQt6.QtGui import QFont
import json

class ResponsePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 状态栏布局
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # 响应内容
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setFont(QFont("Consolas, Courier New, monospace"))
        layout.addWidget(self.response_text)
        
    def update_response(self, response):
        if response:
            status = response['status']
            # 根据状态码设置不同的样式
            if 200 <= status < 300:
                status_color = "#28a745"  # 绿色
                bg_color = "#f0fff4"  # 浅绿色背景
            elif status == 408:  # 超时
                status_color = "#dc3545"  # 红色
                bg_color = "#fff5f5"  # 浅红色背景
            elif 400 <= status < 500:
                status_color = "#ffc107"  # 黄色
                bg_color = "#fffff0"  # 浅黄色背景
            elif 500 <= status < 600:
                status_color = "#dc3545"  # 红色
                bg_color = "#fff5f5"  # 浅红色背景
            else:
                status_color = "#6c757d"  # 灰色
                bg_color = "#f8f9fa"  # 浅灰色背景
                
            # 获取状态描述
            status_text = {
                408: "Request Timeout",
                495: "SSL Certificate Error",
                503: "Service Unavailable",
                500: "Internal Server Error"
            }.get(status, "")
            
            if status_text:
                status_display = f"Status: {status} ({status_text})"
            else:
                status_display = f"Status: {status}"
            
            # 设置状态标签
            self.status_label.setText(status_display)
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {status_color};
                    padding: 5px 10px;
                    border: 1px solid {status_color};
                    border-radius: 3px;
                    background-color: {bg_color};
                }}
            """)
            
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
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    padding: 5px 10px;
                    border: 1px solid #dc3545;
                    border-radius: 3px;
                    background-color: #fff5f5;
                }
            """)
            self.response_text.setText("请求失败，请检查网络连接或URL是否正确")