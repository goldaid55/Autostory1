import asyncio
import logging
from ui import BotUI
from story_worker import StoryWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Запускаем UI в отдельном потоке
    ui = BotUI()
    
    # Запускаем обработчик историй
    worker = StoryWorker()
    asyncio.create_task(worker.run())
    
    # Запускаем UI
    ui.run()

if __name__ == '__main__':
    asyncio.run(main())