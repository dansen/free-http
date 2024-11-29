import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
import qasync
import asyncio

def main():
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = MainWindow()
    window.show()
    
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main() 