
import asyncio
import json
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 911749743
DATA_FILE = "repairs.json"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


def load_repairs():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_repairs(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_number(data):
    if not data:
        return 1001
    return max(int(x) for x in data.keys()) + 1


class Repair(StatesGroup):
    name = State()
    phone = State()
    model = State()
    problem = State()


class CheckStatus(StatesGroup):
    number = State()


menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Здати телефон у ремонт")],
        [KeyboardButton(text="📦 Перевірити статус ремонту")]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Ласкаво просимо до Mobibox!", reply_markup=menu)


@dp.message(F.text == "🔧 Здати телефон у ремонт")
async def repair(message: Message, state: FSMContext):
    await state.set_state(Repair.name)
    await message.answer("Введіть ім'я:")


@dp.message(Repair.name)
async def r_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Repair.phone)
    await message.answer("Телефон:")


@dp.message(Repair.phone)
async def r_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(Repair.model)
    await message.answer("Модель:")


@dp.message(Repair.model)
async def r_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(Repair.problem)
    await message.answer("Опишіть несправність:")


@dp.message(Repair.problem)
async def r_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    data = await state.get_data()

    repairs = load_repairs()
    num = next_number(repairs)

    repairs[str(num)] = {
        "name": data["name"],
        "phone": data["phone"],
        "model": data["model"],
        "problem": data["problem"],
        "status": "Прийнято"
    }
    save_repairs(repairs)

    await bot.send_message(
        ADMIN_ID,
        f"📥 Нова заявка #{num}\n\n"
        f"👤 {data['name']}\n"
        f"📞 {data['phone']}\n"
        f"📱 {data['model']}\n"
        f"🛠 {data['problem']}"
    )

    await message.answer(
        f"✅ Заявку прийнято.\nНомер: #{num}\n"
        "Збережіть його для перевірки статусу.",
        reply_markup=menu
    )
    await state.clear()


@dp.message(F.text == "📦 Перевірити статус ремонту")
async def check(message: Message, state: FSMContext):
    await state.set_state(CheckStatus.number)
    await message.answer("Введіть номер заявки (наприклад 1001):")


@dp.message(CheckStatus.number)
async def check_num(message: Message, state: FSMContext):
    repairs = load_repairs()
    num = message.text.replace("#", "")
    if num in repairs:
        r = repairs[num]
        await message.answer(
            f"📦 Заявка #{num}\n"
            f"📱 {r['model']}\n"
            f"Статус: {r['status']}",
            reply_markup=menu
        )
    else:
        await message.answer("Заявку не знайдено.", reply_markup=menu)
    await state.clear()


@dp.message(Command("status"))
async def status(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Приклад: /status 1001 Готовий")
        return
    num = parts[1].replace("#", "")
    new_status = parts[2]
    repairs = load_repairs()
    if num not in repairs:
        await message.answer("Номер не знайдено.")
        return
    repairs[num]["status"] = new_status
    save_repairs(repairs)
    await message.answer(f"Статус #{num} оновлено на: {new_status}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
'''
path="/mnt/data/main.py"
Path(path).write_text(code,encoding="utf-8")
print(path)
