import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.filters import CommandStart
import csv
from datetime import datetime

from api_token import API_TOKEN, ADMIN_ID, GROUP_ID
from admin import router

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    filename='bot.log', filemode='w', encoding='utf-8')

# Хранилище состояний для отслеживания кнопки "Хочу купить"
user_states = {}


@dp.message(CommandStart())
async def start_handler(message: Message):


    user_data = [message.from_user.id, message.from_user.full_name, message.from_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]

    with open('users.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        with open('users.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            if not any(row[0] == str(message.from_user.id) for row in reader):
                writer.writerow(user_data)

    await bot.copy_message(message.chat.id, GROUP_ID, 10)

    if message.chat.id not in user_states:
        asyncio.create_task(delayed_messages(message.chat.id))


async def delayed_messages(chat_id: int):
    await asyncio.sleep(180)  # 5 минут
    media = []
    for msg_id in range(11, 16):
        msg = await bot.forward_message(chat_id=ADMIN_ID, from_chat_id=GROUP_ID, message_id=msg_id, disable_notification=True)
        media.append(InputMediaPhoto(
            media=msg.photo[-1].file_id, caption='✅ Каме аз отзывҳои шогирдони ман баъди хатми курс' if msg_id == 15 else None))
        await msg.delete()

    await bot.send_media_group(chat_id, media)

    await asyncio.sleep(60)  # ещё 5 минут (итого 10 минут от старта)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Дохил шудан мехоҳам!🎓",
                             callback_data="buy_course")
    ]])
    await bot.copy_message(chat_id, GROUP_ID, 16, reply_markup=kb)
    user_states[chat_id] = {'bought': False}

    await asyncio.sleep(600)  # 10 минут после инфы о курсе
    if not user_states.get(chat_id, {}).get('bought'):
        # ID кружочка с рассказом о курсе
        await bot.copy_message(chat_id, GROUP_ID, 17)


@dp.callback_query(F.data == "buy_course")
async def buy_callback(call: CallbackQuery):

    await bot.copy_message(call.message.chat.id, GROUP_ID, 18)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Харид ✅", callback_data=f"bought:{call.message.chat.id}")
    ]])

    await bot.send_message(ADMIN_ID, f"{call.message.chat.username} мехоҳад шогирд шавад", reply_markup=kb)
    await call.answer()


@dp.callback_query(F.data.startswith("bought:"))
async def bought_callback(call: CallbackQuery):
    user_id = int(call.data.split(":")[1])
    user_states[user_id]['bought'] = True
    await call.message.edit_text(call.message.text + "✅")
    await call.message.edit_reply_markup(reply_markup=None)

dp.include_router(router)


async def main():
    print('Bot Started')
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
