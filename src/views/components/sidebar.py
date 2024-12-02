from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, 
    QListWidgetItem, QSizePolicy, QMenu,
    QMessageBox, QInputDialog, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QCursor
from models.api_model import ApiModel

class SideBar(QWidget):
    api_selected = pyqtSignal(dict)  # 发送选中的API数据
    api_deleted = pyqtSignal(str)    # 发送被删除的API名称
    api_renamed = pyqtSignal(str, str)  # 发送API的旧名称和新名称

    def __init__(self):
        super().__init__()
        # 设置初始宽度和大小策略
        self.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.api_model = ApiModel()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 新建API按钮
        new_api_button = QPushButton("New API")
        new_api_button.clicked.connect(self.create_new_api)
        layout.addWidget(new_api_button)

        # 列表展示区域
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # 列表项点击事件
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self.rename_api)
        
        # 添加右键菜单
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # 加载API列表
        self.load_api_list()

    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.list_widget.itemAt(position)
        if item is None:
            return

        menu = QMenu()
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        action = menu.exec(QCursor.pos())
        
        if action == delete_action:
            self.delete_api(item)
        elif action == rename_action:
            self.rename_api(item)

    def rename_api(self, item):
        """重命名选中的API"""
        old_name = item.text()
        api_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 输入新名称
        new_name, ok = QInputDialog.getText(
            self, 'Rename API',
            'Enter new name:',
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            if self.api_model.rename_api(api_id, new_name):
                item.setText(new_name)
                self.api_renamed.emit(old_name, new_name)
            else:
                QMessageBox.warning(
                    self,
                    "Rename Failed",
                    f'Failed to rename API. The name "{new_name}" might already exist.'
                )

    def delete_api(self, item):
        """删除选中的API"""
        api_name = item.text()
        api_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 确认对话框
        reply = QMessageBox.question(
            self, 'Delete API',
            f'Are you sure you want to delete "{api_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.api_model.delete_api(api_id):
                row = self.list_widget.row(item)
                self.list_widget.takeItem(row)
                self.api_deleted.emit(api_name)
                
    def load_api_list(self):
        """从数据库加载API列表"""
        self.list_widget.clear()
        apis = self.api_model.get_all_apis()
        for api in apis:
            item = QListWidgetItem(api['name'])
            item.setData(Qt.ItemDataRole.UserRole, api['id'])  # 存储API ID
            self.list_widget.addItem(item)

    def on_list_item_clicked(self, item):
        """当API列表项被点击时触发"""
        api_id = item.data(Qt.ItemDataRole.UserRole)
        api_data = self.api_model.get_api_by_id(api_id)
        if api_data:
            self.api_selected.emit(api_data)

    def add_api(self, name, method, url, headers, body):
        """添加新的API到列表"""
        api_id = self.api_model.save_api(name, method, url, headers, body)
        self.load_api_list()  # 重新加载列表

    def create_new_api(self):
        """创建新的API"""
        name, ok = QInputDialog.getText(self, 'New API', 'Enter API name:')
        if ok and name:
            # 检查名称是否已存在
            apis = self.api_model.get_all_apis()
            if any(api['name'] == name for api in apis):
                QMessageBox.warning(
                    self,
                    "Create Failed",
                    f'An API with the name "{name}" already exists.'
                )
                return
            
            # 创建新API
            api_id = self.api_model.save_api(
                name=name,
                method='GET',
                url='',
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "FreeHttp/1.0"
                },
                body={}
            )
            
            # 重新加载列表并选中新创建的API
            self.load_api_list()
            
            # 找到并选中新创建的API项
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == api_id:
                    self.list_widget.setCurrentItem(item)
                    self.on_list_item_clicked(item)
                    break
