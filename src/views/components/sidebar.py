from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, 
    QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt

class SideBar(QWidget):
    api_list_clicked = pyqtSignal(str)
    history_list_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # 设置初始宽度和大小策略
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 列表展示区域
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # 列表项点击事件
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)

    def show_api_list(self):
        self.list_widget.clear()
        # 示例 API 列表
        apis = [
            "GitHub API",
            "Weather API",
            "Random User API",
            "JSON Placeholder API"
        ]
        for api in apis:
            item = QListWidgetItem(api)
            self.list_widget.addItem(item)

    def show_history_list(self):
        self.list_widget.clear()
        # 示例历史记录
        histories = [
            "GET https://api.github.com/users",
            "POST https://jsonplaceholder.typicode.com/posts",
            "PUT https://api.example.com/users/1"
        ]
        for history in histories:
            item = QListWidgetItem(history)
            self.list_widget.addItem(item)

    def on_list_item_clicked(self, item):
        # 发送信号
        self.api_list_clicked.emit(item.text())
