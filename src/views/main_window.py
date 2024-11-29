from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from .components.request_panel import RequestPanel
from .components.response_panel import ResponsePanel
from controllers.request_controller import RequestController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTTP Client")
        self.setMinimumSize(800, 600)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 创建控制器
        self.controller = RequestController()
        
        # 创建请求和响应面板
        self.request_panel = RequestPanel()
        self.response_panel = ResponsePanel()
        
        # 添加到布局
        layout.addWidget(self.request_panel)
        layout.addWidget(self.response_panel)
        
        # 连接信号
        self.request_panel.send_request.connect(self.handle_request)
        
    def handle_request(self, method, url, headers, body):
        response = self.controller.send_request(method, url, headers, body)
        self.response_panel.update_response(response) 