from PyQt6.QtWidgets import (QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                            QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox,
                            QInputDialog, QMenu, QSpinBox)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QFont
import json
from urllib.parse import urlparse, urljoin

class RequestPanel(QWidget):
    send_request = pyqtSignal(str, str, dict, str, int)
    save_api = pyqtSignal(str, str, str, dict, dict, int)  # name, method, url, headers, body, timeout
    api_deleted = pyqtSignal(str)  # name
    api_renamed = pyqtSignal(str, str)  # old_name, new_name
    status_message = pyqtSignal(str, int)  # message, timeout
    
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
        self.current_api_data = None  # 存储当前API的数据，用于比较变化
        self.allow_auto_save = True  # 控制是否允许自动保存
        self.domain_model = None  # 域名管理模型
        self.init_ui()
        self.setup_auto_save()
        
    def set_domain_model(self, domain_model):
        """设置域名管理模型"""
        self.domain_model = domain_model
        self.refresh_domain_button()
        
    def refresh_domain_button(self):
        """刷新域名按钮文本"""
        if not self.domain_model:
            self.domain_button.setText("选择域名")
            return
            
        active_domain = self.domain_model.get_active_domain()
        if active_domain:
            self.domain_button.setText(f"{active_domain['name']}")
        else:
            self.domain_button.setText("选择域名")
            
    def show_domain_menu(self):
        """显示域名选择菜单"""
        if not self.domain_model:
            return
            
        menu = QMenu(self)
        # 添加"无域名"选项
        no_domain_action = menu.addAction("无域名")
        no_domain_action.triggered.connect(lambda: self.on_domain_selected(None))
        menu.addSeparator()
        
        # 添加所有域名
        domains = self.domain_model.get_all_domains()
        for domain in domains:
            action = menu.addAction(f"{domain['name']} ({domain['domain']})")
            action.triggered.connect(lambda checked, d=domain: self.on_domain_selected(d))
            
        # 在按钮下方显示菜单
        menu.exec(self.domain_button.mapToGlobal(self.domain_button.rect().bottomLeft()))
        
    def on_domain_selected(self, domain):
        """当选择域名时"""
        from urllib.parse import urlparse, urljoin
        current_url = self.url_input.text().strip()
        
        if domain:
            self.domain_model.set_active_domain(domain['id'])
            self.domain_button.setText(domain['name'])
            
            # 更新URL
            if current_url:
                # 解析当前URL
                parsed_url = urlparse(current_url)
                if not parsed_url.scheme and not current_url.startswith('http'):
                    # 如果是相对路径，直接拼接
                    # 处理域名末尾和路径开头的斜杠
                    domain_part = domain['domain'].rstrip('/')
                    path_part = current_url.lstrip('/')
                    self.url_input.setText(f"{domain_part}/{path_part}" if path_part else domain_part)
                else:
                    # 如果是完整URL，替换协议、主机和端口部分
                    if not parsed_url.scheme:
                        current_url = 'http://' + current_url
                        parsed_url = urlparse(current_url)
                    
                    # 获取路径部分（包括查询参数和片段）
                    path = parsed_url.path
                    if parsed_url.query:
                        path += '?' + parsed_url.query
                    if parsed_url.fragment:
                        path += '#' + parsed_url.fragment
                    
                    # 处理域名末尾和路径的斜杠
                    domain_part = domain['domain'].rstrip('/')
                    path_part = path.lstrip('/')
                    
                    # 拼接新URL
                    if not path_part:
                        self.url_input.setText(domain_part)
                    else:
                        self.url_input.setText(f"{domain_part}/{path_part}")
            else:
                # URL为空时直接使用域名
                self.url_input.setText(domain['domain'].rstrip('/'))
            
            self.status_message.emit(f"已设置域名: {domain['name']}", 2000)
        else:
            # 清除活动域名
            domains = self.domain_model.get_all_domains()
            if domains:
                self.domain_model.set_active_domain(None)
            self.domain_button.setText("选择域名")
            
            # 如果URL包含当前域名，则移除域名部分，保留路径
            if current_url:
                active_domain = self.domain_model.get_active_domain()
                if active_domain:
                    domain_url = active_domain['domain'].rstrip('/')
                    if current_url.startswith(domain_url):
                        path = current_url[len(domain_url):].lstrip('/')
                        self.url_input.setText(f"/{path}" if path else "/")
            
            self.status_message.emit("已清除域名", 2000)
        
    def setup_auto_save(self):
        """设置自动保存触发器"""
        # 监听URL变化
        self.url_input.textChanged.connect(self.trigger_auto_save)
        # 监听方法变化
        self.method_combo.currentTextChanged.connect(self.trigger_auto_save)
        # 监听headers变化
        self.headers_input.textChanged.connect(self.trigger_auto_save)
        # 监听body变化
        self.body_input.textChanged.connect(self.trigger_auto_save)
        # 监听超时时间变化
        self.timeout_input.valueChanged.connect(self.trigger_auto_save)

    def trigger_auto_save(self):
        """触发自动保存"""
        if not self.current_api_name or not self.allow_auto_save:
            return

        # 触发自动保存
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)  # 单次触发
        self.save_timer.timeout.connect(self.auto_save)
        self.save_timer.start(500)  # 500毫秒后触发

    def auto_save(self):
        """自动保存当前API"""
        if not self.current_api_name or not self.allow_auto_save:
            return

        method = self.method_combo.currentText()
        url = self.url_input.text()

        try:
            headers = json.loads(self.headers_input.toPlainText() or '{}')
            if not isinstance(headers, dict):
                self.status_message.emit("Headers must be a JSON object", 3000)
                return
        except json.JSONDecodeError as e:
            self.status_message.emit(f"Invalid JSON in headers: {str(e)}", 3000)
            return

        # 验证并解析body
        body_text = self.body_input.toPlainText()
        try:
            if self.is_json_content_type(headers) and body_text:
                is_valid, error = self.validate_json(body_text)
                if not is_valid:
                    self.status_message.emit(f"Invalid JSON in body: {error}", 3000)
                    return
                body = json.loads(body_text) if body_text else {}
            else:
                body = {"content": body_text} if body_text else {}

            # 获取超时设置
            timeout = self.timeout_input.value()

            # 检查数据是否有变化
            current_data = {
                'method': method,
                'url': url,
                'headers': headers,
                'body': body,
                'timeout': timeout
            }
            
            if self.current_api_data and self.is_data_equal(current_data, self.current_api_data):
                return

            # 发出保存信号
            self.save_api.emit(self.current_api_name, method, url, headers, body, timeout)
            self.current_api_data = current_data.copy()  # 更新当前数据
            self.status_message.emit("API saved", 1000)
        except Exception as e:
            self.status_message.emit(f"Failed to save API: {str(e)}", 3000)

    def is_data_equal(self, data1, data2):
        """比较两个API数据是否相同"""
        print("[Data Compare] Checking if API data has changed:")
        
        if data1['method'] != data2['method']:
            print(f"[Data Compare] Method changed: {data1['method']} -> {data2['method']}")
            return False
            
        if data1['url'] != data2['url']:
            print(f"[Data Compare] URL changed: {data1['url']} -> {data2['url']}")
            return False
            
        if data1['headers'] != data2['headers']:
            print("[Data Compare] Headers changed:")
            print(f"Old headers: {json.dumps(data1['headers'], indent=2)}")
            print(f"New headers: {json.dumps(data2['headers'], indent=2)}")
            return False
            
        if data1['body'] != data2['body']:
            print("[Data Compare] Body changed:")
            print(f"Old body: {json.dumps(data1['body'], indent=2)}")
            print(f"New body: {json.dumps(data2['body'], indent=2)}")
            return False
            
        if data1['timeout'] != data2['timeout']:
            print(f"[Data Compare] Timeout changed: {data1['timeout']} -> {data2['timeout']}")
            return False
            
        print("[Data Compare] No changes detected")
        return True
        
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)  # 设置边距为8px
        self.setLayout(main_layout)
        
        # 创建等宽编程字体和按钮字体
        code_font = QFont("Consolas, Courier New, monospace")
        code_font.setPointSize(10)
        button_font = QFont("Segoe UI", 10)

        # 创建域名选择按钮
        self.domain_button = QPushButton("选择域名")
        self.domain_button.setFont(button_font)
        self.domain_button.setFixedWidth(120)
        self.domain_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                text-align: left;
            }
            QPushButton:hover {
                border-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #f8f9fa;
            }
        """)
        self.domain_button.clicked.connect(self.show_domain_menu)
        
        # 创建域名按钮布局
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(self.domain_button)
        
        # 添加超时设置
        timeout_label = QLabel("Timeout:")
        timeout_label.setFont(QFont("Segoe UI", 10))
        self.timeout_input = QSpinBox()
        self.timeout_input.setFont(QFont("Segoe UI", 10))
        self.timeout_input.setMinimum(1)
        self.timeout_input.setMaximum(300)
        self.timeout_input.setValue(30)
        self.timeout_input.setSuffix(" s")
        self.timeout_input.setFixedWidth(100)
        self.timeout_input.setStyleSheet("""
            QSpinBox {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                min-height: 25px;
            }
            QSpinBox:hover {
                border-color: #3498db;
            }
            QSpinBox:focus {
                border-color: #3498db;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background: transparent;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #f0f0f0;
            }
            QSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid #636e72;
            }
            QSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #636e72;
            }
        """)
        
        domain_layout.addWidget(timeout_label)
        domain_layout.addWidget(self.timeout_input)
        domain_layout.addStretch()
        
        main_layout.addLayout(domain_layout)
        
        # HTTP 方法选择和 URL 输入
        method_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        self.method_combo.setFont(button_font)
        self.method_combo.setFixedWidth(100)
        self.method_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox:pressed {
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #636e72;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dcdde1;
                selection-background-color: #3498db;
                selection-color: white;
                background-color: white;
            }
        """)
        
        self.url_input = QLineEdit()
        self.url_input.setFont(QFont("Segoe UI", 11))  # 使用更大的字体
        self.url_input.setMinimumHeight(32)  # 设置最小高度
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.url_input.setPlaceholderText('https://api.example.com/v1/resource')
        
        method_layout.addWidget(self.method_combo)
        method_layout.addWidget(self.url_input)
        main_layout.addLayout(method_layout)
        
        # Headers 部分
        headers_layout = QVBoxLayout()
        headers_label_layout = QHBoxLayout()
        headers_label = QLabel("Headers")
        headers_label.setFont(button_font)
        
        # 添加Headers模板选择
        self.headers_template_combo = QComboBox()
        self.headers_template_combo.addItems(list(self.HEADER_TEMPLATES.keys()))
        self.headers_template_combo.setFixedWidth(150)
        self.headers_template_combo.setFont(QFont("Segoe UI", 10))
        self.headers_template_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #636e72;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dcdde1;
                selection-background-color: #3498db;
                selection-color: white;
                background-color: white;
            }
        """)
        self.headers_template_combo.currentTextChanged.connect(self.on_header_template_changed)
        
        # 添加Content-Type选择
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(list(self.CONTENT_TYPES.keys()))
        self.content_type_combo.setFixedWidth(200)
        self.content_type_combo.setFont(QFont("Segoe UI", 10))
        self.content_type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #636e72;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dcdde1;
                selection-background-color: #3498db;
                selection-color: white;
                background-color: white;
            }
        """)
        self.content_type_combo.currentTextChanged.connect(self.on_content_type_changed)
        
        headers_label_layout.addWidget(headers_label)
        headers_label_layout.addWidget(self.headers_template_combo)
        headers_label_layout.addWidget(self.content_type_combo)
        headers_label_layout.addStretch()
        
        self.headers_input = QPlainTextEdit()
        self.headers_input.setFont(code_font)
        self.headers_input.setMinimumHeight(120)  # 增加headers区域的最小高度
        self.headers_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        headers_layout.addLayout(headers_label_layout)
        headers_layout.addWidget(self.headers_input)
        
        main_layout.addLayout(headers_layout)
        
        # Body
        body_layout = QVBoxLayout()
        body_label = QLabel("Request Body:")
        self.body_input = QPlainTextEdit()
        self.body_input.setFont(code_font)
        self.body_input.setMinimumHeight(200)
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
        
        # Send 按钮布局
        buttons_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Send Request")
        self.send_button.setFont(button_font)
        self.send_button.setMinimumHeight(36)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2475a8;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.send_button.clicked.connect(self.on_send_clicked)
        
        buttons_layout.addWidget(self.send_button)
        
        # 添加所有组件到布局
        main_layout.addLayout(body_layout)
        main_layout.addLayout(buttons_layout)
        
        # 设置默认 headers
        self.headers_input.setPlainText(self.HEADER_TEMPLATES['Default'])
        
    def on_header_template_changed(self, template_name):
        """当选择 headers 模板时更新 headers 输入框"""
        self.headers_input.setPlainText(self.HEADER_TEMPLATES[template_name])
        
    def on_content_type_changed(self, content_type):
        """当选择 Content-Type 时更新 headers"""
        try:
            current_headers = json.loads(self.headers_input.toPlainText() or '{}')
            current_headers['Content-Type'] = content_type
            self.headers_input.setPlainText(json.dumps(current_headers, indent=4))
        except json.JSONDecodeError:
            # 如果当前 headers 不是有效的 JSON，直接设置新的
            self.headers_input.setPlainText(self.CONTENT_TYPES[content_type])
    
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
        
        # 获取超时时间
        timeout = self.timeout_input.value()
        
        self.send_request.emit(method, url, headers, body, timeout)
    
    def load_api(self, api_data):
        """加载API数据到界面"""
        # 暂时禁用自动保存
        self.allow_auto_save = False
        
        self.current_api_name = api_data['name']
        self.current_api_data = {
            'method': api_data['method'],
            'url': api_data['url'],
            'headers': api_data['headers'],
            'body': api_data['body'],
            'timeout': api_data['timeout']
        }
        
        # 设置基本字段
        self.method_combo.setCurrentText(api_data['method'])
        self.url_input.setText(api_data['url'])
        self.headers_input.setPlainText(json.dumps(api_data['headers'], indent=4))
        
        # 设置超时时间
        timeout = api_data.get('timeout', 30)  # 如果没有timeout字段，使用默认值30
        self.timeout_input.setValue(int(timeout))  # 确保是整数
        
        # 处理body的显示
        body = api_data['body']
        if isinstance(body, dict):
            if 'content' in body and not self.is_json_content_type(api_data['headers']):
                # 非JSON内容，直接显示content字段
                self.body_input.setPlainText(body['content'])
            else:
                # JSON内容，格式化显示
                self.body_input.setPlainText(json.dumps(body, indent=4))
        
        # 重新启用自动保存
        QTimer.singleShot(100, self.enable_auto_save)
    
    def enable_auto_save(self):
        """重新启用自动保存"""
        print("[Auto Save] Auto save enabled")
        self.allow_auto_save = True

    def clear_api(self):
        """清空当前API信息"""
        self.allow_auto_save = False
        self.current_api_name = None
        self.current_api_data = None
        self.method_combo.setCurrentText('GET')
        self.url_input.clear()
        self.headers_input.setPlainText(self.HEADER_TEMPLATES['Default'])
        self.body_input.clear()
        self.allow_auto_save = True

    def on_api_deleted(self, api_name):
        """当API被删除时，如果是当前API则清空界面"""
        if api_name == self.current_api_name:
            self.clear_api()

    def on_api_renamed(self, old_name, new_name):
        """当API被重命名时更新当前API名称"""
        if old_name == self.current_api_name:
            self.current_api_name = new_name