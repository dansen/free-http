"""
版本信息
"""

VERSION = "0.1.9"

# 从版本字符串生成版本信息元组
VERSION_INFO = tuple(map(int, VERSION.split('.')))  # 主版本号, 次版本号, 修订号
