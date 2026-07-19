import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Здати телефон у ремонт")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Ласкаво просимо до Mobibox!\n\nОберіть дію:",
        reply_markup=menu
    )

@dp.message(F.text == "🔧 Здати телефон у ремонт")
async def repair(message: Message):
    await message.answer("Введіть ваше ім'я:")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
