from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMenu
from PyQt6.QtCore import pyqtSignal
import json
import logging

class HistorySideBar(QWidget):
    history_selected = pyqtSignal(dict)  # 发送选中的历史记录
    
    def __init__(self, history_model):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.history_model = history_model
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建列表控件
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # 清空历史按钮
        self.clear_button = QPushButton("清空历史")
        self.clear_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_button)
        
        # 加载历史记录
        self.refresh_history()
        
    def refresh_history(self):
        """刷新历史记录列表"""
        self.list_widget.clear()
        history = self.history_model.get_history()
        
        for item in history:
            list_item = QListWidgetItem(f"{item['method']} {item['url']} ({item['timestamp']})")
            list_item.setData(1, item)  # 存储完整的历史记录数据
            self.list_widget.addItem(list_item)
            
    def on_item_double_clicked(self, item):
        """处理列表项双击事件"""
        history_data = item.data(1)
        if history_data:
            self.history_selected.emit(history_data)
            self.logger.info(f"Selected history: {history_data['method']} {history_data['url']}")
            
    def clear_history(self):
        """清空历史记录"""
        self.history_model.clear_history()
        self.refresh_history()
        self.logger.info("History cleared")
