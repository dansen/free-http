from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                            QPushButton, QMenu, QLabel, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont
import json
import logging

class HistoryItem(QWidget):
    def __init__(self, method, url, timestamp, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 顶部布局：方法和时间戳
        top_layout = QHBoxLayout()
        
        # 请求方法标签
        method_label = QLabel(method)
        method_label.setStyleSheet(f"""
            QLabel {{
                color: {self.get_method_color(method)};
                font-weight: bold;
                padding: 2px 5px;
                border-radius: 3px;
                background: {self.get_method_bg_color(method)};
            }}
        """)
        top_layout.addWidget(method_label)
        
        # 时间戳标签
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
            }
        """)
        top_layout.addWidget(time_label)
        top_layout.addStretch()
        
        # URL标签
        url_label = QLabel(url)
        url_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 12px;
            }
        """)
        url_label.setWordWrap(True)
        
        layout.addLayout(top_layout)
        layout.addWidget(url_label)
        
    def get_method_color(self, method):
        """获取请求方法的文字颜色"""
        colors = {
            'GET': '#1E7F3C',
            'POST': '#8C4B00',
            'PUT': '#0055AA',
            'DELETE': '#AA0000',
            'PATCH': '#6B2E96',
            'HEAD': '#1E7F3C',
            'OPTIONS': '#1E7F3C'
        }
        return colors.get(method, '#333333')
        
    def get_method_bg_color(self, method):
        """获取请求方法的背景颜色"""
        colors = {
            'GET': '#E8F5E9',
            'POST': '#FFF3E0',
            'PUT': '#E3F2FD',
            'DELETE': '#FFEBEE',
            'PATCH': '#F3E5F5',
            'HEAD': '#E8F5E9',
            'OPTIONS': '#E8F5E9'
        }
        return colors.get(method, '#F5F5F5')

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
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("历史记录")
        title_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 清空按钮
        self.clear_button = QPushButton("清空")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #666666;
                padding: 5px;
            }
            QPushButton:hover {
                color: #E53935;
            }
        """)
        self.clear_button.clicked.connect(self.clear_history)
        title_layout.addWidget(self.clear_button)
        
        layout.addLayout(title_layout)
        
        # 创建列表控件
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #EEEEEE;
                padding: 0px;
            }
            QListWidget::item:selected {
                background-color: #F5F5F5;
            }
            QListWidget::item:hover {
                background-color: #FAFAFA;
            }
        """)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
        # 加载历史记录
        self.refresh_history()
        
    def refresh_history(self):
        """刷新历史记录列表"""
        self.list_widget.clear()
        history = self.history_model.get_history()
        
        for item in history:
            list_item = QListWidgetItem(self.list_widget)
            history_widget = HistoryItem(
                method=item['method'],
                url=item['url'],
                timestamp=item['timestamp']
            )
            list_item.setSizeHint(history_widget.sizeHint())
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, history_widget)
            
    def on_item_clicked(self, item):
        """处理列表项点击事件"""
        history_data = item.data(Qt.ItemDataRole.UserRole)
        if history_data:
            self.history_selected.emit(history_data)
            self.logger.info(f"Selected history: {history_data['method']} {history_data['url']}")
            
    def clear_history(self):
        """清空历史记录"""
        self.history_model.clear_history()
        self.refresh_history()
        self.logger.info("History cleared")
