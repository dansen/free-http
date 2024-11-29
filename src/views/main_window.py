from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from .components.request_panel import RequestPanel
from .components.response_panel import ResponsePanel
from .components.loading_spinner import LoadingSpinner
from controllers.request_controller import RequestController
import asyncio
import qasync

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
        
        # 创建加载动画
        self.loading_spinner = LoadingSpinner(self)
        
        # 添加到布局
        layout.addWidget(self.request_panel)
        layout.addWidget(self.response_panel)
        
        # 连接信号
        self.request_panel.send_request.connect(self.handle_request)
        
    def center_loading_spinner(self):
        geometry = self.geometry()
        x = geometry.x() + (geometry.width() - self.loading_spinner.width()) // 2
        y = geometry.y() + (geometry.height() - self.loading_spinner.height()) // 2
        self.loading_spinner.move(x, y)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center_loading_spinner()
        
    @qasync.asyncSlot(str, str, dict, str)
    async def handle_request(self, method, url, headers, body):
        self.loading_spinner.start()
        try:
            response = await self.controller.send_request(method, url, headers, body)
            if response:
                self.response_panel.update_response(response)
        finally:
            self.loading_spinner.stop() 