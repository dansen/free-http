from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, 
    QHBoxLayout, QStackedWidget, QSplitter, 
    QMenuBar, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import qasync

from src.models.api_model import ApiModel
from src.models.domain_model import DomainModel
from src.views.components.request_panel import RequestPanel
from src.views.components.response_panel import ResponsePanel
from src.views.components.sidebar import SideBar
from src.views.components.icon_sidebar import IconSideBar
from src.views.components.loading_spinner import LoadingSpinner
from src.views.dialogs.domain_dialog import DomainDialog
from src.controllers.request_controller import RequestController
import asyncio
from src.version import VERSION

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"Free Http v{VERSION}")
        self.resize(1360, 960)
        
        # 创建状态栏
        self.statusBar().showMessage("Ready")
        
        # 初始化模型
        self.api_model = ApiModel()
        self.domain_model = DomainModel()
        
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
        
        # 设置域名管理模型
        self.request_panel.set_domain_model(self.domain_model)
        
        # 连接信号
        self.request_panel.send_request.connect(self.handle_request)
        self.request_panel.save_api.connect(self.api_sidebar.add_api)
        self.request_panel.status_message.connect(self.show_status_message)
        
        # 连接 API 侧边栏的信号
        self.api_sidebar.api_selected.connect(self.request_panel.load_api)
        self.api_sidebar.api_deleted.connect(self.request_panel.on_api_deleted)
        self.api_sidebar.api_renamed.connect(self.request_panel.on_api_renamed)
        
        # 添加面板到右侧布局
        right_layout.addWidget(self.request_panel, stretch=3)
        right_layout.addWidget(self.response_panel, stretch=2)
        
        # 添加组件到分割器
        self.splitter.addWidget(self.api_sidebar)
        self.splitter.addWidget(right_widget)
        
        # 设置分割器的初始大小
        self.splitter.setSizes([300, 980])  # 左侧宽度300，右侧宽度980
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建加载动画
        self.loading_spinner = LoadingSpinner(self)
        self.loading_spinner.resize(100, 100)
        self.loading_spinner.move(
            (self.width() - self.loading_spinner.width()) // 2,
            (self.height() - self.loading_spinner.height()) // 2
        )

    @qasync.asyncSlot(str, str, dict, str, int)
    async def handle_request(self, method, url, headers, body, timeout):
        """处理API请求"""
        # 显示加载动画
        self.loading_spinner.start()
        
        # 重置响应面板状态
        self.response_panel.update_response({
            'status': 0,
            'status_text': 'Sending Request...',
            'headers': {},
            'text': ''
        })
        
        try:
            # 发送请求
            response = await self.controller.send_request(method, url, headers, body, timeout)
            
            if response:
                # 更新响应面板
                self.response_panel.update_response({
                    'status': response.get('status', 'Unknown'),
                    'status_text': response.get('status_text', ''),
                    'headers': response.get('headers', {}),
                    'text': response.get('text', '')
                })
        finally:
            # 停止加载动画
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

    def show_status_message(self, message, timeout=3000):
        """在状态栏显示消息
        
        Args:
            message: 要显示的消息
            timeout: 消息显示时间（毫秒），默认3秒
        """
        self.statusBar().showMessage(message, timeout)
        
    def show_domain_dialog(self):
        dialog = DomainDialog(self.domain_model, self)
        dialog.domain_changed.connect(self.on_domain_changed)
        dialog.exec()
        
    def on_domain_changed(self):
        # 当域名改变时更新状态栏
        active_domain = self.domain_model.get_active_domain()
        if active_domain:
            self.statusBar().showMessage(f"Active Domain: {active_domain['name']} ({active_domain['domain']})")
        else:
            self.statusBar().showMessage("No active domain set")

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        
        # 添加退出菜单项到File菜单
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")  # 添加快捷键
        exit_action.triggered.connect(self.close)  # 连接到窗口的close方法
        file_menu.addAction(exit_action)
        
        # 添加域名管理菜单项
        domain_action = QAction("Manage Domains", self)
        domain_action.triggered.connect(self.show_domain_dialog)
        edit_menu.addAction(domain_action)