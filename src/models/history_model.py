import json
import logging
from datetime import datetime
import sqlite3
from pathlib import Path
from src.models.config_model import ConfigModel

class HistoryModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        config = ConfigModel()
        self.db_path = Path(config.get_app_data_path()) / 'history.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        
    def init_db(self):
        """初始化数据库"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # 创建历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method TEXT NOT NULL,
                    url TEXT NOT NULL,
                    headers TEXT,
                    body TEXT,
                    timeout INTEGER DEFAULT 30,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_history(self, method, url, headers, body, timeout):
        """添加一条历史记录"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # 插入新记录
                cursor.execute('''
                    INSERT INTO history (method, url, headers, body, timeout)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    method, 
                    url,
                    json.dumps(headers) if headers else None,
                    json.dumps(body) if body else None,
                    timeout
                ))
                
                # 只保留最近100条记录
                cursor.execute('''
                    DELETE FROM history 
                    WHERE id NOT IN (
                        SELECT id FROM history 
                        ORDER BY created_at DESC 
                        LIMIT 100
                    )
                ''')
                
                conn.commit()
                self.logger.info(f"Added history record: {method} {url}")
                
        except Exception as e:
            self.logger.error(f"Failed to add history: {str(e)}")
    
    def get_history(self):
        """获取所有历史记录"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT method, url, headers, body, timeout, created_at
                    FROM history
                    ORDER BY created_at DESC
                ''')
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        "method": row[0],
                        "url": row[1],
                        "headers": json.loads(row[2]) if row[2] else {},
                        "body": json.loads(row[3]) if row[3] else {},
                        "timeout": row[4],
                        "timestamp": row[5]
                    })
                    
                return history
                
        except Exception as e:
            self.logger.error(f"Failed to get history: {str(e)}")
            return []
    
    def clear_history(self):
        """清空历史记录"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM history')
                conn.commit()
                self.logger.info("History cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear history: {str(e)}")
