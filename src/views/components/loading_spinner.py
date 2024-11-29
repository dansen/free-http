from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.hide()
        
    def init_ui(self):
        self.label = QLabel(self)
        self.movie = QMovie("src/assets/loading.gif")
        self.label.setMovie(self.movie)
        self.setFixedSize(100, 100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def start(self):
        self.movie.start()
        self.show()
        
    def stop(self):
        self.movie.stop()
        self.hide() 