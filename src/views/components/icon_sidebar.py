from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QLabel
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal, Qt, QSize

class IconSideBar(QWidget):
    api_list_clicked = pyqtSignal()
    history_list_clicked = pyqtSignal()
    current_view = None

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedWidth(60)  # 固定宽度

        # API 列表图标
        self.api_list_btn = self.create_icon_button(
            "src/assets/icons/api_list.png", 
            "API列表"
        )
        layout.addWidget(self.api_list_btn)

        # 历史记录图标
        self.history_btn = self.create_icon_button(
            "src/assets/icons/history.png", 
            "历史记录"
        )
        layout.addWidget(self.history_btn)

        # 添加弹簧，将图标固定在顶部
        layout.addStretch(1)

        # 绑定点击事件
        self.api_list_btn.clicked.connect(self.toggle_api_list)
        self.history_btn.clicked.connect(self.toggle_history_list)

    def create_icon_button(self, icon_path, tooltip):
        btn = QPushButton()
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(40, 40))
        btn.setFixedSize(50, 50)
        btn.setStyleSheet("""
            QPushButton { 
                border: none; 
                background-color: transparent; 
                padding: 5px; 
            }
            QPushButton:hover { 
                background-color: #e0e0e0; 
                border-radius: 5px; 
            }
            QPushButton:checked {
                background-color: #c0c0c0;
            }
        """)
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        return btn

    def toggle_api_list(self):
        # 取消其他按钮的选中状态
        self.history_btn.setChecked(False)
        self.api_list_btn.setChecked(True)
        self.current_view = 'api'
        self.api_list_clicked.emit()

    def toggle_history_list(self):
        # 取消其他按钮的选中状态
        self.api_list_btn.setChecked(False)
        self.history_btn.setChecked(True)
        self.current_view = 'history'
        self.history_list_clicked.emit()
