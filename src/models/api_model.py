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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS apis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    method TEXT NOT NULL,
                    url TEXT NOT NULL,
                    headers TEXT,
                    body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_api(self, name, method, url, headers=None, body=None):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM apis WHERE name = ?', (name,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE apis 
                    SET method = ?, url = ?, headers = ?, body = ?
                    WHERE name = ?
                ''', (method, url, 
                      json.dumps(headers) if headers else None,
                      json.dumps(body) if body else None,
                      name))
                api_id = existing[0]
            else:
                cursor.execute('''
                    INSERT INTO apis (name, method, url, headers, body)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, method, url, 
                      json.dumps(headers) if headers else None,
                      json.dumps(body) if body else None))
                api_id = cursor.lastrowid
            
            conn.commit()
            return api_id

    def get_all_apis(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM apis ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [{
                'id': row[0],
                'name': row[1],
                'method': row[2],
                'url': row[3],
                'headers': json.loads(row[4]) if row[4] else {},
                'body': json.loads(row[5]) if row[5] else {}
            } for row in rows]

    def get_api_by_id(self, api_id):
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM apis WHERE id = ?', (api_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'method': row[2],
                    'url': row[3],
                    'headers': json.loads(row[4]) if row[4] else {},
                    'body': json.loads(row[5]) if row[5] else {}
                }
            return None
