import asyncio
import logging
from database import Database
from story_manager import StoryManager
from account_manager import AccountManager

logger = logging.getLogger(__name__)

class StoryWorker:
    def __init__(self):
        self.db = Database()
        self.story_manager = StoryManager()
        self.account_manager = AccountManager(self.db)
        
    async def process_pending_stories(self):
        """Обработка ожидающих публикации историй"""
        stories = self.db.get_pending_stories()
        
        for story in stories:
            try:
                # Получаем клиент для аккаунта
                client = await self.account_manager.get_client(story[1])
                if not client:
                    logger.error(f"Не удалось получить клиент для {story[1]}")
                    continue
                    
                # Публикуем историю
                await self.story_manager.post_story(
                    client,
                    story[2],  # media_path
                    mentions=story[3].split(',') if story[3] else None,
                    link=story[4]
                )
                
                # Обновляем статус
                self.db.update_story_status(story[0], 'published')
                logger.info(f"История {story[0]} опубликована")
                
            except Exception as e:
                logger.error(f"Ошибка при публикации истории {story[0]}: {e}")
                self.db.update_story_status(story[0], 'error')
                
    async def run(self):
        """Основной цикл обработчика"""
        while True:
            try:
                await self.process_pending_stories()
            except Exception as e:
                logger.error(f"Ошибка в обработчике: {e}")
            
            await asyncio.sleep(60)  # Проверяем каждую минуту