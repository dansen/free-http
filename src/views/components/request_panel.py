from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                            QLineEdit, QTextEdit, QPushButton, QLabel)
from PyQt6.QtCore import pyqtSignal

class RequestPanel(QWidget):
    send_request = pyqtSignal(str, str, dict, str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # HTTP 方法选择
        method_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        self.url_input = QLineEdit()
        method_layout.addWidget(self.method_combo)
        method_layout.addWidget(self.url_input)
        
        # Headers
        headers_label = QLabel("Headers (JSON):")
        self.headers_input = QTextEdit()
        self.headers_input.setMaximumHeight(100)
        self.headers_input.setPlaceholderText('{"Content-Type": "application/json"}')
        
        # Body
        body_label = QLabel("Request Body:")
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText('{"key": "value"}')
        
        # Send 按钮
        self.send_button = QPushButton("Send Request")
        self.send_button.clicked.connect(self.on_send_clicked)
        
        # 添加所有组件到布局
        layout.addLayout(method_layout)
        layout.addWidget(headers_label)
        layout.addWidget(self.headers_input)
        layout.addWidget(body_label)
        layout.addWidget(self.body_input)
        layout.addWidget(self.send_button)
        
    def on_send_clicked(self):
        method = self.method_combo.currentText()
        url = self.url_input.text()
        try:
            headers = eval(self.headers_input.toPlainText() or '{}')
        except:
            headers = {}
        body = self.body_input.toPlainText()
        
        self.send_request.emit(method, url, headers, body) 