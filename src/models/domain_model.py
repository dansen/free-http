import sqlite3
import json
from pathlib import Path

class DomainModel:
    def __init__(self):
        self.db_path = Path.home() / '.free-http' / 'domains.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        
    def init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
    def add_domain(self, name, domain):
        """添加新域名"""
        # 移除域名末尾的斜杠
        domain = domain.rstrip('/')
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO domains (name, domain) VALUES (?, ?)',
                         (name, domain))
            conn.commit()
            return cursor.lastrowid
            
    def update_domain(self, id, name, domain):
        """更新域名"""
        # 移除域名末尾的斜杠
        domain = domain.rstrip('/')
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE domains SET name = ?, domain = ? WHERE id = ?',
                         (name, domain, id))
            conn.commit()
            
    def delete_domain(self, id):
        """删除域名"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM domains WHERE id = ?', (id,))
            conn.commit()
            
    def get_all_domains(self):
        """获取所有域名"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, domain, is_active FROM domains')
            return [{'id': row[0], 'name': row[1], 'domain': row[2], 'is_active': bool(row[3])} 
                    for row in cursor.fetchall()]
            
    def set_active_domain(self, id):
        """设置活动域名"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            # 先将所有域名设置为非活动
            cursor.execute('UPDATE domains SET is_active = 0')
            # 设置指定域名为活动
            cursor.execute('UPDATE domains SET is_active = 1 WHERE id = ?', (id,))
            conn.commit()
            
    def get_active_domain(self):
        """获取当前活动域名"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, domain FROM domains WHERE is_active = 1')
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'name': row[1], 'domain': row[2]}
            return None
