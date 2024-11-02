import asyncio
from datetime import datetime, timedelta
import random
import os
from typing import List, Dict

class StoryScheduler:
    def __init__(self, start_hour: int, end_hour: int):
        self.start_hour = start_hour
        self.end_hour = end_hour
        
    def calculate_intervals(self, story_count: int) -> List[datetime]:
        """Рассчитывает время публикации для каждой истории"""
        now = datetime.now()
        start_time = now.replace(hour=self.start_hour, minute=0, second=0)
        
        if now.hour >= self.end_hour:
            start_time += timedelta(days=1)
            
        end_time = start_time.replace(hour=self.end_hour)
        total_minutes = (end_time - start_time).total_seconds() / 60
        interval = total_minutes / story_count
        
        posting_times = []
        current_time = start_time
        
        for _ in range(story_count):
            posting_times.append(current_time)
            current_time += timedelta(minutes=interval)
            
        return posting_times
    
    @staticmethod
    def get_delay_seconds(target_time: datetime) -> int:
        """Вычисляет задержку в секундах до времени публикации"""
        now = datetime.now()
        delay = (target_time - now).total_seconds()
        return max(0, int(delay))