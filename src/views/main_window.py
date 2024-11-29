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
        
        # 创建内容切换区域
        self.content_stacked_widget = QStackedWidget()
        
        # 创建 API 列表侧边栏
        self.api_sidebar = SideBar()
        self.content_stacked_widget.addWidget(self.api_sidebar)
        
        # 创建历史记录侧边栏
        self.history_sidebar = SideBar()
        self.content_stacked_widget.addWidget(self.history_sidebar)
        
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
        self.splitter.addWidget(self.content_stacked_widget)
        self.splitter.addWidget(right_widget)
        
        # 连接图标侧边栏信号
        self.icon_sidebar.api_list_clicked.connect(self.show_api_list)
        self.icon_sidebar.history_list_clicked.connect(self.show_history_list)
        
        # 连接侧边栏列表点击信号
        self.api_sidebar.list_widget.itemClicked.connect(self.handle_api_list_click)
        self.history_sidebar.list_widget.itemClicked.connect(self.handle_history_list_click)
        
        # 连接请求面板信号
        self.request_panel.send_request.connect(self.handle_request)
        
        # 默认显示 API 列表
        self.show_api_list()

    def show_api_list(self):
        self.api_sidebar.show_api_list()
        self.content_stacked_widget.setCurrentWidget(self.api_sidebar)

    def show_history_list(self):
        self.history_sidebar.show_history_list()
        self.content_stacked_widget.setCurrentWidget(self.history_sidebar)

    def handle_api_list_click(self, item):
        # 根据选择的 API 更新请求面板
        api_name = item.text()
        print(f"Selected API: {api_name}")
        # TODO: 根据 API 名称填充请求面板
        
    def handle_history_list_click(self, item):
        # 根据历史记录更新请求面板
        history_item = item.text()
        print(f"Selected History: {history_item}")
        # TODO: 根据历史记录填充请求面板

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