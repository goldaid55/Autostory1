import asyncio
import logging
from datetime import datetime
from account_manager import AccountManager
from story_manager import StoryManager
from story_scheduler import StoryScheduler
from story_queue import StoryQueue
from config import PROXY_SETTINGS, POSTING_START_HOUR, POSTING_END_HOUR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoryBot:
    def __init__(self):
        self.account_manager = AccountManager()
        self.story_manager = StoryManager()
        self.scheduler = StoryScheduler(POSTING_START_HOUR, POSTING_END_HOUR)
        
    async def setup_account(self, phone: str, proxy=None):
        """Настройка аккаунта"""
        return await self.account_manager.add_account(phone, proxy)
        
    async def schedule_stories(self, phone: str, media_dir: str, mentions_file: str, link: str):
        """Планирование публикации историй для аккаунта"""
        # Создаем очередь для аккаунта
        queue = StoryQueue(phone)
        queue.load_media_files(media_dir)
        queue.load_mentions(mentions_file)
        queue.set_link(link)
        
        # Получаем клиент
        client = await self.account_manager.get_client(phone)
        if not client:
            raise ValueError(f"Аккаунт не найден: {phone}")
            
        # Рассчитываем время публикации
        posting_times = self.scheduler.calculate_intervals(len(queue.media_files))
        
        # Планируем публикации
        for media_file, post_time in zip(queue.media_files, posting_times):
            delay = self.scheduler.get_delay_seconds(post_time)
            
            # Планируем задачу
            asyncio.create_task(self._post_delayed_story(
                client,
                media_file,
                queue.mentions,
                queue.link,
                delay
            ))
            
    async def _post_delayed_story(self, client, media_file, mentions, link, delay):
        """Публикация истории с задержкой"""
        await asyncio.sleep(delay)
        try:
            await self.story_manager.post_story(
                client,
                media_file,
                mentions=mentions,
                link=link
            )
            logger.info(f"История опубликована: {media_file}")
        except Exception as e:
            logger.error(f"Ошибка при публикации истории: {e}")

async def main():
    bot = StoryBot()
    
    # Пример использования
    phone = '+1234567890'
    await bot.setup_account(phone, PROXY_SETTINGS)
    
    await bot.schedule_stories(
        phone,
        media_dir='stories',
        mentions_file='mentions.txt',
        link='https://example.com'
    )
    
    # Держим бота запущенным
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())