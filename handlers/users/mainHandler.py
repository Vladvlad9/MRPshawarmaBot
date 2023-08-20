from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BadRequest

from keyboards.inline.users.mainFormIkb import main_cb, MainForms
from loader import dp, bot
from states.users.userStates import UserStates


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    await message.delete()
    text = "Здравствуйте!\n" \
           "Чтобы сделать заказ перейдите в раздел меню"
    await message.answer(text=text, reply_markup=await MainForms.main_ikb())


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=UserStates.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForms.process(callback=callback, state=state)


@dp.message_handler(state=UserStates.all_states, content_types=["text"])
async def process_message(message: types.Message, state: FSMContext):
    await MainForms.process(message=message, state=state)