from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, 
    QListWidgetItem, QSizePolicy, QMenu,
    QMessageBox, QInputDialog, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QCursor, QKeyEvent, QFont
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

        # 创建按钮字体
        button_font = QFont("Segoe UI", 10)

        # 新建API按钮
        self.new_api_button = QPushButton("New API")
        self.new_api_button.setFont(button_font)
        self.new_api_button.setMinimumHeight(32)
        self.new_api_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
        """)
        self.new_api_button.clicked.connect(self.create_new_api)
        layout.addWidget(self.new_api_button)

        # 列表展示区域
        self.list_widget = QListWidget()
        self.list_widget.keyPressEvent = self.handle_key_press
        
        # 设置更大的字体
        list_font = QFont("Segoe UI, Arial")
        list_font.setPointSize(11)
        self.list_widget.setFont(list_font)
        
        # 设置项目高度和样式
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 2px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                min-height: 25px;
                border-radius: 3px;
                margin: 1px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f1f2f6;
                color: #2d3436;
            }
            QListWidget::item:selected:hover {
                background-color: #2980b9;
                color: white;
            }
        """)
        
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

    def handle_key_press(self, event: QKeyEvent):
        """处理键盘事件"""
        if event.key() == Qt.Key.Key_F2:
            current_item = self.list_widget.currentItem()
            if current_item:
                self.rename_api(current_item)
        else:
            # 确保其他键盘事件正常工作
            QListWidget.keyPressEvent(self.list_widget, event)
