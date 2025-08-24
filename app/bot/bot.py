import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import asyncio
from app.bot.handlers.start import router as start_router
from app.bot.handlers.habits import router as habits_router
from app.bot.services.api_client import ApiClient

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env")

# Создаем объекты
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def main():
    logger.info("Starting bot...")
    

    dp["api_client"] = ApiClient()
    
 
    dp.include_router(start_router)
    dp.include_router(habits_router)
    
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Closing bot...")
        await dp["api_client"].close()

if __name__ == "__main__":
    asyncio.run(main())