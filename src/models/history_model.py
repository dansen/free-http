import json
import logging
from datetime import datetime
import os

class HistoryModel:
    def __init__(self):
        self.history_file = "data/history.json"
        self.logger = logging.getLogger(__name__)
        os.makedirs("data", exist_ok=True)
        
        # 确保历史文件存在
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f)
    
    def add_history(self, method, url, headers, body, timeout):
        """添加一条历史记录"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            history_item = {
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
                "timeout": timeout,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            history.insert(0, history_item)  # 新记录插入到最前面
            
            # 只保留最近100条记录
            if len(history) > 100:
                history = history[:100]
            
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Added history record: {method} {url}")
            
        except Exception as e:
            self.logger.error(f"Failed to add history: {str(e)}")
    
    def get_history(self):
        """获取所有历史记录"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to get history: {str(e)}")
            return []
    
    def clear_history(self):
        """清空历史记录"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f)
            self.logger.info("History cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear history: {str(e)}")
