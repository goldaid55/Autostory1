import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot_data.db')
        self.create_tables()
        
    def create_tables(self):
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            phone TEXT PRIMARY KEY,
            session TEXT,
            proxy_addr TEXT,
            proxy_port INTEGER,
            proxy_username TEXT,
            proxy_password TEXT,
            added_date TIMESTAMP
        )''')
        
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS story_queue (
            id INTEGER PRIMARY KEY,
            account_phone TEXT,
            media_path TEXT,
            mentions TEXT,
            link TEXT,
            scheduled_time TIMESTAMP,
            status TEXT,
            FOREIGN KEY (account_phone) REFERENCES accounts(phone)
        )''')
        
        self.conn.commit()
        
    def add_account(self, phone: str, session: str, proxy_data: dict):
        self.conn.execute('''
        INSERT OR REPLACE INTO accounts 
        (phone, session, proxy_addr, proxy_port, proxy_username, proxy_password, added_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (phone, session, proxy_data.get('addr'), proxy_data.get('port'),
              proxy_data.get('username'), proxy_data.get('password'),
              datetime.now()))
        self.conn.commit()
        
    def get_account(self, phone: str):
        cursor = self.conn.execute('SELECT * FROM accounts WHERE phone = ?', (phone,))
        return cursor.fetchone()
        
    def get_all_accounts(self):
        cursor = self.conn.execute('SELECT * FROM accounts')
        return cursor.fetchall()
        
    def add_story_task(self, account_phone: str, media_path: str, mentions: str,
                      link: str, scheduled_time: datetime):
        self.conn.execute('''
        INSERT INTO story_queue 
        (account_phone, media_path, mentions, link, scheduled_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (account_phone, media_path, mentions, link, scheduled_time, 'pending'))
        self.conn.commit()
        
    def get_pending_stories(self):
        cursor = self.conn.execute('''
        SELECT * FROM story_queue 
        WHERE status = 'pending' AND scheduled_time <= ?
        ''', (datetime.now(),))
        return cursor.fetchall()
        
    def update_story_status(self, story_id: int, status: str):
        self.conn.execute('''
        UPDATE story_queue SET status = ? WHERE id = ?
        ''', (status, story_id))
        self.conn.commit()