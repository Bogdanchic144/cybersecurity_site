import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import Config

TOKEN = Config.BOT_TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот временно отключён на тех. работы, попробуйте позже.")

@dp.message()
async def any_message(message: types.Message):
    await message.answer("Ведутся технические работы. Бот скоро вернётся!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

