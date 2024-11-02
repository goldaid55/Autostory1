import json
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH

class AccountManager:
    def __init__(self):
        self.accounts = {}
        self.load_accounts()
        
    def load_accounts(self):
        """Загружает данные аккаунтов из файла"""
        try:
            with open('accounts.json', 'r') as f:
                self.accounts = json.load(f)
        except FileNotFoundError:
            pass
            
    def save_accounts(self):
        """Сохраняет данные аккаунтов в файл"""
        with open('accounts.json', 'w') as f:
            json.dump(self.accounts, f)
            
    async def add_account(self, phone: str, proxy=None):
        """Добавляет новый аккаунт"""
        # Используем StringSession для сохранения сессии в строке
        client = TelegramClient(StringSession(), API_ID, API_HASH, proxy=proxy)
        await client.start(phone)
        
        # Сохраняем строку сессии
        session_string = client.session.save()
        
        self.accounts[phone] = {
            'session': session_string,
            'proxy': proxy
        }
        self.save_accounts()
        return client
    
    async def get_client(self, phone: str):
        """Получает клиент для аккаунта"""
        if phone not in self.accounts:
            return None
        
        account = self.accounts[phone]
        # Создаем клиент из сохраненной строки сессии
        client = TelegramClient(
            StringSession(account['session']),
            API_ID,
            API_HASH,
            proxy=account['proxy']
        )
        await client.start()
        return client