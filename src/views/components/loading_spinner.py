from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.hide()
        
    def init_ui(self):
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # 创建标签并设置居中对齐
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # 设置动画
        self.movie = QMovie("src/assets/loading.gif")
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)  # 缓存所有帧
        
        # 获取GIF的大小
        self.movie.jumpToFrame(0)  # 跳到第一帧
        size = self.movie.currentImage().size()
        self.setFixedSize(size)  # 设置窗口大小为GIF大小
        self.label.setFixedSize(size)  # 设置标签大小为GIF大小
        
        # 设置动画到标签
        self.label.setMovie(self.movie)
        
        # 设置窗口透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
    def start(self):
        self.movie.start()
        self.show()
        
    def stop(self):
        self.movie.stop()
        self.hide()