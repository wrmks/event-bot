from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import logging
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

events = {
    1: {
        'title': '🌟 Встреча команды',
        'date': '2025-04-15',
        'limit': 10,
        'attendees': []
    }
}

def event_kb(event_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📝 Записаться", callback_data=f"signup_{event_id}")],
        [InlineKeyboardButton("👥 Участники", callback_data=f"list_{event_id}")]
    ])

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Привет! Доступные события:")
    for eid, ev in events.items():
        await message.answer(
            f"{ev['title']}\n📅 {ev['date']}\n👥 {len(ev['attendees'])}/{ev['limit']}",
            reply_markup=event_kb(eid)
        )

@dp.callback_query_handler(lambda c: c.data.startswith("signup_"))
async def signup(callback: types.CallbackQuery):
    eid = int(callback.data.split('_')[1])
    user = callback.from_user.full_name
    event = events[eid]

    if user in event['attendees']:
        await callback.answer("Ты уже записан.")
    elif len(event['attendees']) >= event['limit']:
        await callback.answer("Мест больше нет.")
    else:
        event['attendees'].append(user)
        await callback.answer("Записан!")

    await callback.message.edit_text(
        f"{event['title']}\n📅 {event['date']}\n👥 {len(event['attendees'])}/{event['limit']}",
        reply_markup=event_kb(eid)
    )

@dp.callback_query_handler(lambda c: c.data.startswith("list_"))
async def list_attendees(callback: types.CallbackQuery):
    eid = int(callback.data.split('_')[1])
    attendees = events[eid]['attendees']
    if attendees:
        text = '\n'.join([f"– {name}" for name in attendees])
    else:
        text = "Пока никто не записался."
    await callback.message.answer(f"👥 Участники:\n{text}")
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
