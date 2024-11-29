from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, 
    QHBoxLayout, QStackedWidget, QSplitter
)
from PyQt6.QtCore import Qt
from .components.request_panel import RequestPanel
from .components.response_panel import ResponsePanel
from .components.loading_spinner import LoadingSpinner
from .components.icon_sidebar import IconSideBar
from .components.sidebar import SideBar
from controllers.request_controller import RequestController
import asyncio
import qasync

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTTP Client")
        self.setMinimumSize(1200, 800)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 创建图标侧边栏
        self.icon_sidebar = IconSideBar()
        main_layout.addWidget(self.icon_sidebar)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)  # 设置分割线宽度为1像素
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background: #CCCCCC;
            }
        """)
        main_layout.addWidget(self.splitter)
        
        # 创建 API 列表侧边栏
        self.api_sidebar = SideBar()
        
        # 创建右侧内容区域
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # 创建控制器
        self.controller = RequestController()
        
        # 创建请求和响应面板
        self.request_panel = RequestPanel()
        self.response_panel = ResponsePanel()
        
        # 创建加载动画
        self.loading_spinner = LoadingSpinner(self)
        
        # 添加到右侧布局
        right_layout.addWidget(self.request_panel)
        right_layout.addWidget(self.response_panel)
        
        # 将内容区域和右侧面板添加到分割器
        self.splitter.addWidget(self.api_sidebar)
        self.splitter.addWidget(right_widget)
        
        # 连接信号
        self.request_panel.send_request.connect(self.handle_request)
        self.request_panel.save_api.connect(self.api_sidebar.add_api)
        self.api_sidebar.api_selected.connect(self.request_panel.load_api)

    @qasync.asyncSlot(str, str, dict, str)
    async def handle_request(self, method, url, headers, body):
        self.loading_spinner.start()
        try:
            response = await self.controller.send_request(method, url, headers, body)
            if response:
                self.response_panel.update_response(response)
        finally:
            self.loading_spinner.stop()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center_loading_spinner()

    def center_loading_spinner(self):
        geometry = self.geometry()
        x = geometry.x() + (geometry.width() - self.loading_spinner.width()) // 2
        y = geometry.y() + (geometry.height() - self.loading_spinner.height()) // 2
        self.loading_spinner.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)
        # 设置分割器初始大小
        total_width = self.splitter.width()
        self.splitter.setSizes([300, total_width - 300])