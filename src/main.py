import os
import sys
from loguru import logger

# 添加项目根目录到 Python 路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from PyQt6.QtWidgets import QApplication
from src.views.main_window import MainWindow
import qasync
import asyncio

def setup_logger():
    """配置loguru日志格式"""
    # 移除默认的处理器
    logger.remove()
    # 添加新的处理器，使用自定义格式
    if sys.stderr is not None:
        logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}.py:{line} - {message}", level="DEBUG")
    # 替换模块名中的点号为斜杠
    logger.configure(patcher=lambda record: record.update(name=record["name"].replace(".", "/")))

def main():
    """应用程序入口"""
    # 配置日志
    setup_logger()
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    try:
        # 创建事件循环
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        # 运行事件循环
        with loop:
            sys.exit(loop.run_forever())
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()