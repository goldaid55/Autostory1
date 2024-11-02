from typing import List, Dict
import json
import os

class StoryQueue:
    def __init__(self, account_phone: str):
        self.account_phone = account_phone
        self.media_files: List[str] = []
        self.mentions: List[str] = []
        self.link: str = ""
        self.queue_file = f'queues/{account_phone}_queue.json'
        
    def load_media_files(self, directory: str):
        """Загружает медиафайлы из указанной директории"""
        self.media_files = [
            os.path.join(directory, f) for f in os.listdir(directory)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4'))
        ]
        self.save_queue()
        
    def load_mentions(self, mentions_file: str):
        """Загружает список упоминаний из файла"""
        with open(mentions_file, 'r', encoding='utf-8') as f:
            self.mentions = [line.strip() for line in f if line.strip()]
        self.save_queue()
            
    def set_link(self, link: str):
        """Устанавливает ссылку для историй"""
        self.link = link
        self.save_queue()
        
    def save_queue(self):
        """Сохраняет очередь в файл"""
        os.makedirs('queues', exist_ok=True)
        data = {
            'media_files': self.media_files,
            'mentions': self.mentions,
            'link': self.link
        }
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_queue(self):
        """Загружает очередь из файла"""
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.media_files = data.get('media_files', [])
                self.mentions = data.get('mentions', [])
                self.link = data.get('link', "")