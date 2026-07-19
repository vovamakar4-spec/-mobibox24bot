import asyncio
import json
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 911749743

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

DB_FILE = "repairs.json"


def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_id": 1000, "repairs": {}}, f)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class RepairForm(StatesGroup):
    name = State()
    phone = State()
    model = State()
    problem = State()


menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Здати телефон у ремонт")],
        [KeyboardButton(text="📦 Перевірити статус")]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Вітаємо у Mobibox!\n\nОберіть дію:",
        reply_markup=menu
    )


@dp.message(F.text == "🔧 Здати телефон у ремонт")
async def repair_start(message: Message, state: FSMContext):
    await state.set_state(RepairForm.name)
    await message.answer("👤 Введіть ваше ім'я:")


@dp.message(RepairForm.name)
async def repair_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RepairForm.phone)
    await message.answer("📞 Введіть номер телефону:")


@dp.message(RepairForm.phone)
async def repair_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(RepairForm.model)
    await message.answer("📱 Введіть модель телефону:")


@dp.message(RepairForm.model)
async def repair_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(RepairForm.problem)
    await message.answer("🛠 Опишіть несправність:")@dp.message(RepairForm.problem)
async def repair_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)

    user_data = await state.get_data()

    db = load_db()
    db["last_id"] += 1
    repair_id = str(db["last_id"])

    db["repairs"][repair_id] = {
        "name": user_data["name"],
        "phone": user_data["phone"],
        "model": user_data["model"],
        "problem": user_data["problem"],
        "status": "Прийнято"
    }

    save_db(db)

    await bot.send_message(
        ADMIN_ID,
        f"🆕 Нова заявка №{repair_id}\n\n"
        f"👤 {user_data['name']}\n"
        f"📞 {user_data['phone']}\n"
        f"📱 {user_data['model']}\n"
        f"🛠 {user_data['problem']}"
    )

    await message.answer(
        f"✅ Вашу заявку прийнято!\n\n"
        f"📦 Номер заявки: {repair_id}\n"
        f"Використайте кнопку «📦 Перевірити статус» для перевірки."
    )

    await state.clear()


@dp.message(F.text == "📦 Перевірити статус")
async def status_start(message: Message):
    await message.answer("Введіть номер заявки:")


@dp.message(Command("status"))
async def admin_status(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.answer("Приклад:\n/status 1001 Готовий")
        return

    repair_id = parts[1]
    new_status = parts[2]

    db = load_db()

    if repair_id not in db["repairs"]:
        await message.answer("❌ Заявку не знайдено.")
        return

    db["repairs"][repair_id]["status"] = new_status
    save_db(db)

    await message.answer(f"✅ Статус заявки №{repair_id} змінено на: {new_status}")


@dp.message()
async def check_status(message: Message):
    if not message.text.isdigit():
        return

    db = load_db()

    repair = db["repairs"].get(message.text)

    if not repair:
        await message.answer("❌ Заявку не знайдено.")
        return

    await message.answer(
        f"📦 Заявка №{message.text}\n\n"
        f"📱 {repair['model']}\n"
        f"📊 Статус: {repair['status']}"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
