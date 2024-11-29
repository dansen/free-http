from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, 
    QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from models.api_model import ApiModel

class SideBar(QWidget):
    api_selected = pyqtSignal(dict)  # 发送选中的API数据

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

        # 列表展示区域
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # 列表项点击事件
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)
        
        # 加载API列表
        self.load_api_list()

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
