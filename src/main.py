import sys
import os
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
import qasync
import asyncio

# 添加src目录到Python路径
src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, os.path.dirname(src_path))

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