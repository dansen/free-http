import sqlite3
import json
from pathlib import Path

class ApiModel:
    def __init__(self):
        self.db_path = Path.home() / '.free-http' / 'apis.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # 检查是否存在旧表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apis'")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # 检查是否有需要的列
                cursor.execute("PRAGMA table_info(apis)")
                columns = cursor.fetchall()
                has_timeout = any(col[1] == 'timeout' for col in columns)
                has_last_selected = any(col[1] == 'last_selected' for col in columns)
                
                if not has_timeout or not has_last_selected:
                    # 备份旧表
                    cursor.execute("ALTER TABLE apis RENAME TO apis_backup")
                    
                    # 创建新表
                    cursor.execute('''
                        CREATE TABLE apis (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE NOT NULL,
                            method TEXT NOT NULL,
                            url TEXT NOT NULL,
                            headers TEXT,
                            body TEXT,
                            timeout INTEGER DEFAULT 30,
                            last_selected DATETIME,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # 迁移数据
                    cursor.execute('''
                        INSERT INTO apis (id, name, method, url, headers, body, timeout, created_at)
                        SELECT id, name, method, url, headers, body, 
                               COALESCE(timeout, 30),
                               created_at
                        FROM apis_backup
                    ''')
                    
                    # 删除旧表
                    cursor.execute("DROP TABLE apis_backup")
            else:
                # 创建新表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS apis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        method TEXT NOT NULL,
                        url TEXT NOT NULL,
                        headers TEXT,
                        body TEXT,
                        timeout INTEGER DEFAULT 30,
                        last_selected DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
            conn.commit()

    def save_api(self, name, method, url, headers=None, body=None, timeout=30):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM apis WHERE name = ?', (name,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE apis 
                    SET method = ?, url = ?, headers = ?, body = ?, timeout = ?
                    WHERE name = ?
                ''', (method, url, 
                      json.dumps(headers) if headers else None,
                      json.dumps(body) if body else None,
                      timeout,
                      name))
                api_id = existing[0]
            else:
                cursor.execute('''
                    INSERT INTO apis (name, method, url, headers, body, timeout)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, method, url, 
                      json.dumps(headers) if headers else None,
                      json.dumps(body) if body else None,
                      timeout))
                api_id = cursor.lastrowid
            
            conn.commit()
            return api_id

    def get_all_apis(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, method, url, headers, body, timeout 
                FROM apis 
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            return [{
                'id': row[0],
                'name': row[1],
                'method': row[2],
                'url': row[3],
                'headers': json.loads(row[4]) if row[4] else {},
                'body': json.loads(row[5]) if row[5] else {},
                'timeout': int(row[6]) if row[6] is not None else 30
            } for row in rows]

    def get_api_by_id(self, api_id):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, method, url, headers, body, timeout 
                FROM apis 
                WHERE id = ?
            ''', (api_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'method': row[2],
                    'url': row[3],
                    'headers': json.loads(row[4]) if row[4] else {},
                    'body': json.loads(row[5]) if row[5] else {},
                    'timeout': int(row[6]) if row[6] is not None else 30
                }
            return None

    def delete_api(self, api_id):
        """删除指定ID的API"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM apis WHERE id = ?', (api_id,))
            conn.commit()
            return cursor.rowcount > 0  # 返回是否删除成功

    def rename_api(self, api_id, new_name):
        """重命名API
        
        Args:
            api_id: API的ID
            new_name: 新的名称
            
        Returns:
            bool: 是否重命名成功
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE apis SET name = ? WHERE id = ?', (new_name, api_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            # 如果名称已存在，会触发唯一约束错误
            return False

    def update_last_selected(self, api_id):
        """更新最后选择的API"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            # 先清除所有的 last_selected
            cursor.execute('UPDATE apis SET last_selected = NULL')
            # 设置新的 last_selected
            cursor.execute('''
                UPDATE apis 
                SET last_selected = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (api_id,))
            conn.commit()

    def get_last_selected_api(self):
        """获取最后选择的API"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, method, url, headers, body, timeout 
                FROM apis 
                WHERE last_selected IS NOT NULL
                ORDER BY last_selected DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'method': row[2],
                    'url': row[3],
                    'headers': json.loads(row[4]) if row[4] else {},
                    'body': json.loads(row[5]) if row[5] else {},
                    'timeout': int(row[6]) if row[6] is not None else 30
                }
            return None
