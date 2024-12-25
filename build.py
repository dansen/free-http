import os
import sys
import shutil
from src.version import VERSION

def clean_build():
    """清理构建文件"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build():
    """构建应用"""
    clean_build()
    
    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--name=FreeHttp',
        '--windowed',  # 不显示控制台窗口
        '--noconfirm',  # 覆盖输出目录
        '--clean',  # 在构建之前清理
        '--onefile',  # 打包成单个文件
        '--exclude-module=PyQt6',  # 排除 PyQt6
        '--paths=src',  # 添加源代码目录到Python路径
        '--hidden-import=src.models',  # 添加隐式导入
        '--hidden-import=src.views',
        '--hidden-import=src.controllers',
        'src/main.py'  # 入口文件
    ]
    
    # 执行打包命令
    os.system(' '.join(cmd))
    
    print(f"\nBuild completed! Version: {VERSION}")
    print("Executable can be found in the 'dist' directory")

if __name__ == '__main__':
    build()
