import csv
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from api_token import ADMIN_ID

router = Router()


# 📦 Состояния FSM
class BroadcastState(StatesGroup):
    waiting_for_content = State()
    waiting_for_confirmation = State()

# 🚀 Команда начала рассылки


@router.message(Command("hamada"))
async def hamada_handler(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Чиро ба ҳама равон кардан лозим аст? Нависед:")
    await state.set_state(BroadcastState.waiting_for_content)

# ✍️ Получаем текст рассылки


@router.message(BroadcastState.waiting_for_content, F.from_user.id == ADMIN_ID)
async def receive_broadcast_content(message: Message, state: FSMContext):
    await state.update_data(content=message)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ҳа", callback_data="broadcast_confirm")],
        [InlineKeyboardButton(text="❌ Не", callback_data="broadcast_cancel")]
    ])

    await message.answer(
        f"Шумо мехоҳед чунин паёмро ба ҳама равон кунед?\n\n{message.text}",
        reply_markup=keyboard
    )
    await state.set_state(BroadcastState.waiting_for_confirmation)

# ✅ Подтверждение


@router.callback_query(F.data == "broadcast_confirm", BroadcastState.waiting_for_confirmation)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await callback.message.edit_text(callback.message.text + "✅")
    # await callback.message.edit_reply_markup(None)
    data = await state.get_data()
    message = data["content"]

    with open('users.csv') as f:
        reader = csv.reader(f)
        USER_IDS = set(int(row[0]) for row in reader)
        # for row in reader:
        #     print(row)

    await bot.send_message(ADMIN_ID, "📤 Рассылка началась...")

    success = 0
    for uid in USER_IDS:
        try:
            if message.content_type == "text":
                await bot.send_message(uid, message.text)
            elif message.content_type in ["voice", "video"]:
                await bot.copy_message(uid, from_chat_id=callback.message.chat.id, message_id=message.message_id)
            success += 1
        except Exception as e:
            logging.exception(f"Error while sending message to {uid}")

    await bot.send_message(ADMIN_ID, f"✅ Рассылка окончена.\nУспешно: {success} из {len(USER_IDS)}")
    await state.clear()



# ❌ Отмена


@router.callback_query(F.data == "broadcast_cancel", BroadcastState.waiting_for_confirmation)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.edit_text(callback.message.text + "❌")
    await callback.message.edit_reply_markup(None)
    await callback.answer("🚫 Рассылка отменена.")
    await bot.send_message(ADMIN_ID, "Рассылка отменена.")
    await state.clear()
