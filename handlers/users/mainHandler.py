import logging

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BadRequest

from crud.referralCRUD import CRUDReferral
from crud.userCRUD import CRUDUsers
from keyboards.inline.users.mainFormIkb import main_cb, MainForms
from loader import dp, bot
from schemas import UserSchema, ReferralSchema
from states.users.userStates import UserStates


@dp.message_handler(commands=['start'], state=UserStates.all_states)
async def stateStart(message: types.Message):
    try:
        text = "Здравствуйте!\n" \
               "Чтобы сделать заказ перейдите в раздел меню"
        user = await CRUDUsers.get(user_id=message.from_user.id)
        await message.answer(text=text,
                             reply_markup=await MainForms.main_ikb(user_id=message.from_user.id))
    except Exception as e:
        logging.error(f'Error in new_topic_cmd: {e}')


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    await message.delete()
    text = "Здравствуйте!\n" \
           "Чтобы сделать заказ перейдите в раздел меню"
    user = await CRUDUsers.get(user_id=message.from_user.id)

    if not user:
        new_user = await CRUDUsers.add(user=UserSchema(user_id=message.from_user.id,
                                                       purchase_quantity=0))
        if message.get_args():
            user_id = await CRUDUsers.get(user_id=int(message.get_args()))
            await CRUDReferral.add(referral=ReferralSchema(referring_user_id=user_id.id,
                                                           referred_user_id=new_user.id)
                                   )

            await bot.send_message(chat_id=int(message.get_args()),
                                   text="По вашей реферальной ссылке зарегистрировались")
            # сделать тут счетчик для новый и сколько осталось для акции

    await message.answer(text=text, reply_markup=await MainForms.main_ikb(user_id=message.from_user.id))


@dp.callback_query_handler(main_cb.filter())
@dp.callback_query_handler(main_cb.filter(), state=UserStates.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await MainForms.process(callback=callback, state=state)


@dp.message_handler(state=UserStates.all_states, content_types=["text"])
async def process_message(message: types.Message, state: FSMContext):
    await MainForms.process(message=message, state=state)