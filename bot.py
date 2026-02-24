import asyncio
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

BASE_URL = "https://kmt.kemobl.ru/Studentu-fx3ifzdiool1km80bra3c7/Raspisanie-zanyatij-sds6lyy3puj6e7uocr20i3/"

GROUPS = [
    "МР-24"
]

def get_schedule(group, date):
    params = {
        "group": group,
        "date": date.strftime("%d.%m.%Y")
    }

    response = requests.get(BASE_URL, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    lessons = []
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            time = cols[0].text.strip()
            subject = cols[1].text.strip()
            teacher = cols[2].text.strip()
            room = cols[3].text.strip()

            lessons.append(f"{time} {subject} {teacher} {room}")

    if not lessons:
        return "Занятий нет."

    return "\n".join(lessons)

def group_keyboard():
    keyboard = []
    for group in GROUPS:
        keyboard.append(
            [InlineKeyboardButton(text=group, callback_data=f"group_{group}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def day_keyboard(group):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data=f"today_{group}"),
            InlineKeyboardButton(text="📅 Завтра", callback_data=f"tomorrow_{group}")
        ]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Выберите группу:", reply_markup=group_keyboard())

@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    data = call.data

    if data.startswith("group_"):
        group = data.replace("group_", "")
        await call.message.answer(
            f"Группа {group}. Выберите день:",
            reply_markup=day_keyboard(group)
        )

    elif data.startswith("today_") or data.startswith("tomorrow_"):
        parts = data.split("_")
        day_type = parts[0]
        group = parts[1]

        if day_type == "today":
            date = datetime.now()
        else:
            date = datetime.now() + timedelta(days=1)

        schedule = get_schedule(group, date)

        await call.message.answer(
            f"{group} | {date.strftime('%d.%m.%Y')}\n\n{schedule}"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
