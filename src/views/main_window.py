from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, 
    QHBoxLayout, QStackedWidget, QSplitter, 
    QMenuBar, QMenu, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import qasync
import os
import json
from loguru import logger

from src.models.api_model import ApiModel
from src.models.domain_model import DomainModel
from src.models.config_model import ConfigModel
from src.models.history_model import HistoryModel
from src.views.components.request_panel import RequestPanel
from src.views.components.response_panel import ResponsePanel
from src.views.components.sidebar import SideBar
from src.views.components.history_sidebar import HistorySideBar
from src.views.components.icon_sidebar import IconSideBar
from src.views.components.loading_spinner import LoadingSpinner
from src.views.dialogs.domain_dialog import DomainDialog
from src.controllers.request_controller import RequestController
import asyncio
from src.version import VERSION
from PyQt6.QtWidgets import QApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        logger.info("Initializing MainWindow...")
        
        self.setWindowTitle(f"Free Http v{VERSION}")
        self.resize(1360, 960)
        
        # 使窗口居中显示
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y-40)
        
        # 创建状态栏
        self.statusBar().showMessage("Ready")
        
        # 初始化模型
        self.api_model = ApiModel()
        self.domain_model = DomainModel()
        self.config_model = ConfigModel()
        self.history_model = HistoryModel()
        
        self.update_window_title()
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 创建图标侧边栏
        self.icon_sidebar = IconSideBar()
        main_layout.addWidget(self.icon_sidebar)
        
        # 连接图标侧边栏信号
        self.icon_sidebar.api_list_clicked.connect(self.show_api_list)
        self.icon_sidebar.history_list_clicked.connect(self.show_history)
        
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
        
        # 创建历史记录侧边栏
        self.history_sidebar = HistorySideBar(self.history_model)
        self.history_sidebar.hide()  # 默认隐藏
        self.history_sidebar.history_selected.connect(self.on_history_selected)

        # 创建左侧栈式布局容器
        self.left_stack = QStackedWidget()
        self.left_stack.addWidget(self.api_sidebar)
        self.left_stack.addWidget(self.history_sidebar)
        
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
        self.request_panel.add_api.connect(self.api_sidebar.add_api)
        self.request_panel.status_message.connect(self.show_status_message)
        
        # 连接 API 侧边栏的信号
        self.api_sidebar.api_selected.connect(self.request_panel.load_api)
        self.api_sidebar.api_deleted.connect(self.request_panel.on_api_deleted)
        self.api_sidebar.api_renamed.connect(self.request_panel.on_api_renamed)
        
        # 添加面板到右侧布局
        right_layout.addWidget(self.request_panel, stretch=3)
        right_layout.addWidget(self.response_panel, stretch=2)
        
        # 添加组件到分割器
        self.splitter.addWidget(self.left_stack)
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
        logger.info(f"Sending request: {method} {url}")
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request body: {body}")
        
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
                
                logger.info(f"Request completed: {response.get('status', 'Unknown')} {response.get('status_text', '')}")
                logger.debug(f"Response headers: {response.get('headers', {})}")
                
                # 添加到历史记录
                try:
                    headers_dict = json.loads(headers)
                except:
                    headers_dict = headers
                    
                try:
                    body_dict = json.loads(body)
                except:
                    body_dict = body
                    
                self.history_model.add_history(
                    method=method,
                    url=url,
                    headers=headers_dict,
                    body=body_dict,
                    timeout=timeout
                )
                logger.info(f"Added to history: {method} {url}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            self.response_panel.update_response({
                'status': 'Error',
                'status_text': str(e),
                'headers': {},
                'text': str(e)
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
        """在状态栏显示消息"""
        logger.debug(f"Status message: {message}")
        self.statusBar().showMessage(message, timeout)
        
    def show_domain_dialog(self):
        """显示域名管理对话框"""
        logger.info("Opening domain management dialog")
        dialog = DomainDialog(self.domain_model, self)
        dialog.domain_changed.connect(self.on_domain_changed)
        dialog.exec()
        
    def on_domain_changed(self):
        """当域名改变时更新状态栏"""
        active_domain = self.domain_model.get_active_domain()
        if active_domain:
            logger.info(f"Active domain changed: {active_domain['name']} ({active_domain['domain']})")
            self.statusBar().showMessage(f"Active Domain: {active_domain['name']} ({active_domain['domain']})")
        else:
            logger.info("No active domain set")
            self.statusBar().showMessage("No active domain set")
            
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        settings_menu = menubar.addMenu("Settings")
        
        # 添加退出菜单项到File菜单
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")  # 添加快捷键
        exit_action.triggered.connect(self.close)  # 连接到窗口的close方法
        file_menu.addAction(exit_action)
        
        # 添加域名管理菜单项
        domain_action = QAction("Manage Domains", self)
        domain_action.triggered.connect(self.show_domain_dialog)
        edit_menu.addAction(domain_action)
        
        # 添加配置文件路径设置菜单项
        config_action = QAction("Set Config Path", self)
        config_action.triggered.connect(self.show_config_path_dialog)
        settings_menu.addAction(config_action)
        
        # 添加应用数据路径设置菜单项
        app_data_action = QAction("Set App Data Path", self)
        app_data_action.triggered.connect(self.show_app_data_path_dialog)
        settings_menu.addAction(app_data_action)

    def show_config_path_dialog(self):
        """显示配置文件路径设置对话框"""
        current_path = self.config_model.get_config_path()
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDirectory(os.path.dirname(current_path))
        file_dialog.selectFile(os.path.basename(current_path))
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                new_path = selected_files[0]
                self.config_model.set_config_path(new_path)
                self.show_status_message(f"Config path set to: {new_path}")
                
    def show_app_data_path_dialog(self):
        """显示应用数据路径设置对话框"""
        current_path = self.config_model.get_app_data_path()
        dir_dialog = QFileDialog(self)
        dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
        if current_path:
            dir_dialog.setDirectory(current_path)
            
        if dir_dialog.exec():
            selected_dirs = dir_dialog.selectedFiles()
            if selected_dirs:
                new_path = selected_dirs[0]
                self.config_model.set_app_data_path(new_path)
                self.show_status_message(f"App data path set to: {new_path}")
                self.update_window_title()
                
                # 提示用户重启应用
                QMessageBox.information(
                    self,
                    "Restart Required",
                    "The application needs to be restarted for the new app data path to take effect."
                )

    def update_window_title(self):
        """更新窗口标题，显示版本和应用数据路径"""
        app_data_path = self.config_model.get_app_data_path()
        self.setWindowTitle(f"Free Http v{VERSION} - {app_data_path}")

    def show_api_list(self):
        """显示API列表"""
        logger.debug("Switching to API list view")
        self.left_stack.setCurrentWidget(self.api_sidebar)
        self.request_panel.show()
        self.response_panel.show()
        
        # 重新加载当前API的数据
        if self.request_panel.current_api_name:
            logger.info(f"Reloading current API: {self.request_panel.current_api_name}")
            # 获取当前API数据
            api_data = self.api_sidebar.get_api_data(self.request_panel.current_api_name)
            if api_data:
                # 暂时禁用自动保存
                self.request_panel.allow_auto_save = False
                # 重新加载API数据
                self.request_panel.load_api(api_data)
                # 重新启用自动保存
                self.request_panel.allow_auto_save = True
                logger.debug(f"API data reloaded: {api_data}")

    def show_history(self):
        """显示历史记录"""
        logger.debug("Switching to history view")
        self.left_stack.setCurrentWidget(self.history_sidebar)
        self.history_sidebar.refresh_history()
        self.request_panel.show()
        self.response_panel.show()

    def on_history_selected(self, history_data):
        """处理历史记录选择事件"""
        logger.info(f"Loading history: {history_data['method']} {history_data['url']}")
        logger.debug(f"History data: {history_data}")
        
        # 重置响应结果
        self.response_panel.update_response({
            'status': 0,
            'status_text': '',
            'headers': {},
            'text': ''
        })
        
        # 暂时禁用自动保存
        self.request_panel.allow_auto_save = False
        
        # 加载历史记录数据
        self.request_panel.method_combo.setCurrentText(history_data["method"])
        self.request_panel.url_input.setText(history_data["url"])
        self.request_panel.headers_input.setPlainText(json.dumps(history_data["headers"], indent=2))
        self.request_panel.body_input.setPlainText(json.dumps(history_data["body"], indent=2))
        self.request_panel.timeout_input.setValue(history_data["timeout"])
        
        # 重新启用自动保存
        self.request_panel.allow_auto_save = True