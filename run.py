import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import Config
from app.handlers import router

from forDB.db_service import DB

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery



logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if event.message:
            await self.log_message(event.message)
        elif event.callback_query:
            await self.log_callback(event.callback_query)

        result = await handler(event, data)
        return result

    async def log_message(self, message: Message):
        log_data = {
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
            "text": message.text,
        }
        logger.info(f"Получено сообщение: {log_data}")

    async def log_callback(self, callback: CallbackQuery):
        log_data = {
            "username": callback.from_user.username,
            "data": callback.data,
        }
        logger.info(f"Получен коллбэк: {log_data}")


bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()
dp.update.middleware(LoggingMiddleware())

# НАСТРОЙКА ЛОГГИРОВАНИЯ
def setup_logging():
    logging.getLogger().handlers = []

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    setup_logging() # Выключить по готовности (Замедляет работу)
    try:
        asyncio.run(DB.create_tables())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is dead")
        
