import csv
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

from api_token import API_TOKEN, ADMIN_ID, GROUP_ID, CHANNEL_ID
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


    buttons = [
        InlineKeyboardButton(text='Дарсҳо📕', callback_data='lessons'),
        InlineKeyboardButton(text='Курси Барномасозӣ🧑🏻‍💻', callback_data='course_info'),
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])

    await message.answer("*Салом Дустам!*👋\n\nТу инҷо нохост наомадаӣ.\n*Мо шодем ки ту бо мо ҳастӣ!*\n\nМарҳамат тугмаи лозимиро пахш кун:", reply_markup=keyboard, parse_mode='Markdown')

@dp.callback_query(F.data == 'lessons')
async def lesson_1(call: CallbackQuery):
    print('in lessons')
    chat_member = await bot.get_chat_member(CHANNEL_ID, call.from_user.id)

    if chat_member.status != 'member':
        buttons = [
            [InlineKeyboardButton(text='Обуна шудан✍🏻', url=f'https://t.me/amirilifee')],
            [InlineKeyboardButton(text="Санҷидан✅", callback_data='check_subs')]
        ]
        kb = InlineKeyboardMarkup(inline_keyboard = buttons)
        await bot.send_message(call.from_user.id,"*Дустам*,\n\n _Барои дарсро гирифтан, ба мо обуна шудан лозим_ 😀", reply_markup=kb, parse_mode='Markdown')

    else:
        button = [
            [KeyboardButton(text="Гузаштан ба Дарси 2✍🏻")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True, one_time_keyboard=True)
        await bot.copy_message(call.message.chat.id, GROUP_ID, 19, reply_markup=keyboard)

@dp.message(F.text == "Гузаштан ба Дарси 2✍🏻")
async def lesson_2(message: Message):
    chat_member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)

    if chat_member.status != 'member':
        buttons = [
            [InlineKeyboardButton(text='Обуна шудан✍🏻', url=f'https://t.me/amirilifee')],
            [InlineKeyboardButton(text="Санҷидан✅", callback_data='check_subs')]
        ]
        kb = InlineKeyboardMarkup(inline_keyboard = buttons)
        await bot.send_message(message.from_user.id,"*Дустам*,\n\n _Барои дарсро гирифтан, ба мо обуна шудан лозим_ 😀", reply_markup=kb, parse_mode='Markdown')

    else:
        keyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text="Дарси 3🤯")]],resize_keyboard=True, one_time_keyboard=True)

        await bot.copy_message(message.chat.id, GROUP_ID, 20, reply_markup=keyboard)

@dp.message(F.text == "Дарси 3🤯")
async def lesson_3(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Гирифтани курс бо скидка -50с✅")]], resize_keyboard=True, one_time_keyboard=True)
    await bot.copy_message(message.chat.id, GROUP_ID, 21, reply_markup=keyboard)


@dp.message(F.text == "Гирифтани курс бо скидка -50с✅")
async def lesson_4(message: Message):
    button = InlineKeyboardButton(text="Маълумот дар бораи курс✍🏻", callback_data='course_info')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await bot.copy_message(message.chat.id, GROUP_ID, 22, reply_markup = keyboard)

@dp.callback_query(F.data == 'course_info')
async def course_info(call: CallbackQuery):

    message = call.message

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

@dp.callback_query(F.data == 'check_subs')
async def check_subs(call: CallbackQuery):
    chat_member = await bot.get_chat_member(CHANNEL_ID, call.from_user.id)
    if chat_member.status == 'member':
        await bot.send_message(call.from_user.id, "*Шуморо дар рӯйхати обуначиён мебинем!*\n\nАкнун /start -ро пахш карда, ба дарс шурӯъ кунед", parse_mode='Markdown')
    else:
        await bot.send_message(call.from_user.id,"Абача подписаться кн, бги дарсора, мурдаи чии ть. /start")


dp.include_router(router)


async def main():
    print('Bot Started')
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
