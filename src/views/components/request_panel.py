from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                            QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox,
                            QInputDialog)
from PyQt6.QtCore import pyqtSignal
import json

class RequestPanel(QWidget):
    send_request = pyqtSignal(str, str, dict, str)
    save_api = pyqtSignal(str, str, str, dict, dict)  # name, method, url, headers, body
    api_deleted = pyqtSignal(str)  # name
    api_renamed = pyqtSignal(str, str)  # old_name, new_name
    
    # 常用 Content-Type
    CONTENT_TYPES = {
        'application/json': '{"Content-Type": "application/json"}',
        'application/x-www-form-urlencoded': '{"Content-Type": "application/x-www-form-urlencoded"}',
        'multipart/form-data': '{"Content-Type": "multipart/form-data"}',
        'text/plain': '{"Content-Type": "text/plain"}',
        'text/html': '{"Content-Type": "text/html"}',
        'text/xml': '{"Content-Type": "text/xml"}',
    }
    
    # 常用 Headers 模板
    HEADER_TEMPLATES = {
        'Default': '''{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0"
}''',
        'JSON': '''{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0"
}''',
        'Form': '''{
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0"
}''',
        'Token Auth': '''{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0",
    "Authorization": "Bearer your-token-here"
}''',
        'Basic Auth': '''{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0",
    "Authorization": "Basic your-base64-credentials"
}''',
        'API Key': '''{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0",
    "X-API-Key": "your-api-key-here"
}''',
        'XML': '''{
    "Content-Type": "application/xml",
    "Accept": "application/xml",
    "User-Agent": "FreeHttp/1.0"
}''',
        'Multipart Form': '''{
    "Content-Type": "multipart/form-data",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0"
}''',
        'GraphQL': '''{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0",
    "X-Request-Type": "GraphQL"
}''',
        'No Auth': '''{
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FreeHttp/1.0"
}'''
    }
    
    def __init__(self):
        super().__init__()
        self.current_api_name = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # HTTP 方法选择和 URL 输入
        method_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('https://api.example.com/v1/resource')
        method_layout.addWidget(self.method_combo)
        method_layout.addWidget(self.url_input)
        
        # Headers 部分
        headers_layout = QHBoxLayout()
        headers_label = QLabel("Headers:")
        self.headers_template_combo = QComboBox()
        self.headers_template_combo.addItems(list(self.HEADER_TEMPLATES.keys()))
        self.headers_template_combo.currentTextChanged.connect(self.on_header_template_changed)
        headers_layout.addWidget(headers_label)
        headers_layout.addWidget(self.headers_template_combo)
        
        self.headers_input = QTextEdit()
        self.headers_input.setMaximumHeight(100)
        self.headers_input.setPlaceholderText('{"Content-Type": "application/json"}')
        
        # Content-Type 快速选择
        content_type_layout = QHBoxLayout()
        content_type_label = QLabel("Content-Type:")
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(list(self.CONTENT_TYPES.keys()))
        self.content_type_combo.currentTextChanged.connect(self.on_content_type_changed)
        content_type_layout.addWidget(content_type_label)
        content_type_layout.addWidget(self.content_type_combo)
        
        # Body
        body_layout = QVBoxLayout()
        body_label = QLabel("Request Body:")
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText('''// JSON 示例
{
    "key": "value",
    "array": [1, 2, 3],
    "nested": {
        "field": "value"
    }
}

// Form 示例
key1=value1&key2=value2

// Text 示例
Plain text content''')
        
        body_layout.addWidget(body_label)
        body_layout.addWidget(self.body_input)
        
        # Send 按钮和 Save 按钮的布局
        buttons_layout = QHBoxLayout()
        
        # 新建按钮
        self.new_button = QPushButton("New API")
        self.new_button.clicked.connect(self.on_new_clicked)
        
        self.send_button = QPushButton("Send Request")
        self.send_button.clicked.connect(self.on_send_clicked)
        self.save_button = QPushButton("Save API")
        self.save_button.clicked.connect(self.on_save_clicked)
        
        buttons_layout.addWidget(self.new_button)
        buttons_layout.addWidget(self.send_button)
        buttons_layout.addWidget(self.save_button)
        
        # 添加所有组件到布局
        layout.addLayout(method_layout)
        layout.addLayout(headers_layout)
        layout.addWidget(self.headers_input)
        layout.addLayout(content_type_layout)
        layout.addLayout(body_layout)
        layout.addLayout(buttons_layout)
        
        # 设置默认 headers
        self.headers_input.setText(self.HEADER_TEMPLATES['Default'])
        
    def on_header_template_changed(self, template_name):
        """当选择 headers 模板时更新 headers 输入框"""
        self.headers_input.setText(self.HEADER_TEMPLATES[template_name])
        
    def on_content_type_changed(self, content_type):
        """当选择 Content-Type 时更新 headers"""
        try:
            current_headers = json.loads(self.headers_input.toPlainText() or '{}')
            current_headers['Content-Type'] = content_type
            self.headers_input.setText(json.dumps(current_headers, indent=4))
        except json.JSONDecodeError:
            # 如果当前 headers 不是有效的 JSON，直接设置新的
            self.headers_input.setText(self.CONTENT_TYPES[content_type])
    
    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
        
    def is_json_content_type(self, headers):
        content_type = headers.get('Content-Type', '').lower()
        return 'application/json' in content_type
        
    def validate_json(self, text):
        if not text:
            return True, None
        try:
            json.loads(text)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)
        
    def on_send_clicked(self):
        method = self.method_combo.currentText()
        url = self.url_input.text()
        
        # 验证 URL
        if not url:
            self.show_error("错误", "请输入URL")
            return
            
        # 验证并解析 headers
        try:
            headers = json.loads(self.headers_input.toPlainText() or '{}')
            if not isinstance(headers, dict):
                self.show_error("错误", "Headers 必须是一个 JSON 对象")
                return
        except json.JSONDecodeError as e:
            self.show_error("Headers 格式错误", f"Headers 不是有效的 JSON 格式: {str(e)}")
            return
            
        # 获取请求体
        body = self.body_input.toPlainText()
        
        # 如果 Content-Type 是 application/json，验证 body 是否为有效的 JSON
        if self.is_json_content_type(headers):
            if body == '':
                self.show_error("Body 格式错误", "Body 不能为空")
                return
            is_valid, error = self.validate_json(body)
            if not is_valid:
                self.show_error("Body 格式错误", f"Body 不是有效的 JSON 格式: {error}")
                return
        
        self.send_request.emit(method, url, headers, body) 
    
    def on_new_clicked(self):
        """创建新的API"""
        # 获取新API名称
        name, ok = QInputDialog.getText(self, 'New API', 'Enter API name:')
        if not ok or not name:
            return
            
        self.current_api_name = name
        self.method_combo.setCurrentText('GET')
        self.url_input.clear()
        self.headers_input.setText(self.HEADER_TEMPLATES['Default'])
        self.body_input.clear()

    def on_save_clicked(self):
        """保存当前API到数据库"""
        if not self.current_api_name:
            self.show_error("错误", "请先创建新API或选择已有API")
            return

        method = self.method_combo.currentText()
        url = self.url_input.text()

        # 验证URL
        if not url:
            self.show_error("错误", "请输入URL")
            return

        # 验证并解析headers
        try:
            headers = json.loads(self.headers_input.toPlainText() or '{}')
            if not isinstance(headers, dict):
                self.show_error("错误", "Headers 必须是一个 JSON 对象")
                return
        except json.JSONDecodeError as e:
            self.show_error("Headers 格式错误", f"Headers 不是有效的 JSON 格式: {str(e)}")
            return

        # 验证并解析body
        body_text = self.body_input.toPlainText()
        if self.is_json_content_type(headers) and body_text:
            is_valid, error = self.validate_json(body_text)
            if not is_valid:
                self.show_error("Body 格式错误", f"Body 不是有效的 JSON 格式: {error}")
                return
            body = json.loads(body_text) if body_text else {}
        else:
            # 对于非JSON内容，将body存储为字典格式
            body = {"content": body_text} if body_text else {}

        # 发出保存信号
        self.save_api.emit(self.current_api_name, method, url, headers, body)

    def load_api(self, api_data):
        """加载API数据到界面"""
        self.current_api_name = api_data['name']
        self.method_combo.setCurrentText(api_data['method'])
        self.url_input.setText(api_data['url'])
        self.headers_input.setText(json.dumps(api_data['headers'], indent=4))
        
        # 处理body的显示
        body = api_data['body']
        if isinstance(body, dict):
            if 'content' in body and not self.is_json_content_type(api_data['headers']):
                # 非JSON内容，直接显示content字段
                self.body_input.setText(body['content'])
            else:
                # JSON内容，格式化显示
                self.body_input.setText(json.dumps(body, indent=4))
        else:
            self.body_input.setText(str(body) if body else '')

    def clear_api(self):
        """清空当前API信息"""
        self.current_api_name = None
        self.method_combo.setCurrentText('GET')
        self.url_input.clear()
        self.headers_input.setText(self.HEADER_TEMPLATES['Default'])
        self.body_input.clear()

    def on_api_deleted(self, api_name):
        """当API被删除时，如果是当前API则清空界面"""
        if api_name == self.current_api_name:
            self.clear_api()

    def on_api_renamed(self, old_name, new_name):
        """当API被重命名时更新当前API名称"""
        if old_name == self.current_api_name:
            self.current_api_name = new_name