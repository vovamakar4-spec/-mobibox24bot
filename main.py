import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 911749743

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


class Repair(StatesGroup):
    name = State()
    phone = State()
    model = State()
    problem = State()


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
async def repair(message: Message, state: FSMContext):
    await state.set_state(Repair.name)
    await message.answer("👤 Введіть ваше ім'я:")


@dp.message(Repair.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Repair.phone)
    await message.answer("📞 Введіть номер телефону:")


@dp.message(Repair.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Repair.model)
    await message.answer("📱 Введіть модель телефону:")


@dp.message(Repair.model)
async def get_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(Repair.problem)
    await message.answer("🛠 Опишіть несправність:")


@dp.message(Repair.problem)
async def get_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)

    data = await state.get_data()

    text = (
        "📥 Нова заявка\n\n"
        f"👤 Ім'я: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📱 Модель: {data['model']}\n"
        f"🛠 Несправність:\n{data['problem']}"
    )

    await bot.send_message(ADMIN_ID, text)

    await message.answer(
        "✅ Дякуємо!\n\n"
        "Вашу заявку прийнято.\n"
        "Майстер зв'яжеться з вами найближчим часом.",
        reply_markup=menu
    )

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
