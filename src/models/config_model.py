"""
配置文件管理模型
"""
import json
import os
from pathlib import Path

class ConfigModel:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigModel, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.config_path = str(Path.home() / "free-http-config.json")
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            # 如果配置文件不存在，创建默认配置
            default_config = {
                "version": 1,
                "app_data_path": str(Path.home() / ".free-http"),
                "theme": "light",
                "language": "en",
                "request_timeout": 30
            }
            self.save_config(default_config)
            return default_config
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
            
    def save_config(self, config):
        """保存配置到文件
        
        Args:
            config: 要保存的配置字典
        """
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            self.config = config
            
            # 确保应用数据目录存在
            app_data_path = self.get_app_data_path()
            if app_data_path:
                os.makedirs(app_data_path, exist_ok=True)
                
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get_config_path(self):
        """获取当前配置文件路径"""
        return self.config_path
        
    def set_config_path(self, path):
        """设置新的配置文件路径
        
        Args:
            path: 新的配置文件路径
        """
        old_config = self.config
        self.config_path = path
        # 尝试加载新路径的配置
        new_config = self._load_config()
        if not new_config:
            # 如果新路径加载失败，使用旧配置
            self.save_config(old_config)
            
    def get_app_data_path(self):
        """获取应用数据目录路径"""
        return self.config.get("app_data_path")
        
    def set_app_data_path(self, path):
        """设置应用数据目录路径
        
        Args:
            path: 新的应用数据目录路径
        """
        self.config["app_data_path"] = path
        self.save_config(self.config)
