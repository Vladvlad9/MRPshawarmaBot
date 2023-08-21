import asyncio
import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from config import CONFIG
from crud import CRUDSubCategory, CRUDProduct, CRUDOrder
from crud.categoryCRUD import CRUDCategory
from crud.orderDetailCRUD import CRUDOrderDetail
from crud.sizeCRUD import CRUDSize
from crud.userCRUD import CRUDUsers
from loader import bot
from schemas import OrderDetailSchema, OrderSchema
from states.users.userStates import UserStates
import re
import logging
main_cb = CallbackData("main", "target", "action", "id", "editId", "newId")


class MainForms:

    @staticmethod
    async def check(get_basket: list):
        text2 = ""
        count = 1
        res_sum = 0
        for i in get_basket:
            product = await CRUDProduct.get(product_id=i.product_id)
            sub_category = await CRUDSubCategory.get(sub_category_id=product.sub_category_id)
            res_sum += i.subtotal
            text2 += f"Товар № {count}\n" \
                     f"Название - {sub_category.name}\n" \
                     f"Цена - {product.price}\n" \
                     f"Количество - {i.quantity}\n\n"
            count += 1
        return text2 + f"К оплате {res_sum}\n\n"

    @staticmethod
    async def order(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None):
        user = await CRUDUsers.get(user_id=callback.from_user.id)
        basket = await CRUDOrderDetail.get_all(user_id=user.id)
        textBasket = await MainForms.check(get_basket=basket)

        getDataState = await state.get_data()
        getCard = "Картой" if getDataState['bankcard'] == "yes" else "Наличными"

        text = f"Данные вашего заказа:\n\n"\
               f"Имя - <b>{getDataState['userName']}</b>\n"\
               f"Телефон - <b>{getDataState['phone']}</b>\n"\
               f"Время - <b>{getDataState['time']}</b>\n"\
               f"Оплата - {getCard}\n"\
               f"<tg-spoiler>----------------------------"\
               f"</tg-spoiler>\n\n"\
               f"{textBasket}"

        if callback:
            await callback.message.edit_text(text=text,
                                             reply_markup=await MainForms.confirmation_ikb(),
                                             parse_mode="HTML")
        else:
            await message.answer(text=text,
                                 reply_markup=await MainForms.confirmation_ikb(),
                                 parse_mode="HTML")

    @staticmethod
    async def main_ikb(user_id: int) -> InlineKeyboardMarkup:
        user = await CRUDUsers.get(user_id=user_id)
        basket = await CRUDOrderDetail.get_all(user_id=user.id)
        basket_text = "Корзина"
        if basket:
            basket_text = f"Корзина ({len(basket)})"

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Меню",
                                         callback_data=main_cb.new("Menu", "getMenu", 0, 0, 0)),

                ],
                [
                    InlineKeyboardButton(text=basket_text,
                                         callback_data=main_cb.new("Basket", "getBasket", 0, 0, 0)),
                ],
                [
                    InlineKeyboardButton(text="👤Мой профиль",
                                         callback_data=main_cb.new("myProfile", "getProfile", 0, 0, 0)),
                    InlineKeyboardButton(text="🆘Мне нужна помощь",
                                         callback_data=main_cb.new("help", "getHelp", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def category_ikb() -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=category.name,
                                                         callback_data=main_cb.new("Menu", "Category", category.id, 0,
                                                                                   0))
                                ]
                                for category in await CRUDCategory.get_all()
                            ] + [
                                [
                                    InlineKeyboardButton(text='← Назад',
                                                         callback_data=main_cb.new("Main", "", 0, 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def sub_category_ikb(category_id) -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=sub_category.name,
                                                         callback_data=main_cb.new("Menu", "Product",
                                                                                   sub_category.id, category_id, 0))
                                ]
                                for sub_category in await CRUDSubCategory.get_all(category_id=category_id)
                            ] + [
                                [
                                    InlineKeyboardButton(text='← Назад',
                                                         callback_data=main_cb.new("Menu", "getMenu", category_id, 0,
                                                                                   0))
                                ]
                            ]
        )

    @staticmethod
    async def description_pizza_ikb(
            price=0,
            page: int = 1,
            category_id=0,
            sub_category_id=0,
            count: int = 1) -> InlineKeyboardMarkup:

        size_id = 350

        price = float(price) * page

        if page == 1:
            prev_page = 1
            next_page = page + 1
        else:
            prev_page = page - 1
            next_page = page + 1

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"Цена: {price:.2f}",
                                         callback_data=main_cb.new("", 0, 0, 0, 0)),
                    InlineKeyboardButton(text=f"Размер: {size_id}",
                                         callback_data=main_cb.new("", 0, 0, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="➖",
                                         callback_data=main_cb.new(target="Menu",
                                                                   action="ProductsPage",
                                                                   id=prev_page,
                                                                   editId=0,
                                                                   newId=0)),
                    InlineKeyboardButton(text=str(page),
                                         callback_data=main_cb.new(0, 0, count, category_id, sub_category_id)),
                    InlineKeyboardButton(text="➕",
                                         callback_data=main_cb.new(target="Menu",
                                                                   action="ProductsPage",
                                                                   id=next_page,
                                                                   editId=0,
                                                                   newId=0))
                ],
                [
                    InlineKeyboardButton(text="➕ В Корзину",
                                         callback_data=main_cb.new(target="Menu",
                                                                   action="InBasket",
                                                                   id=page,
                                                                   editId=0,
                                                                   newId=0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Menu", "Category", category_id, sub_category_id, 0))
                ]
            ]
        )

    @staticmethod
    async def basket_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Оформить",
                                         callback_data=main_cb.new("Basket", "PlaceInOrder", id, 0, 0)),
                    InlineKeyboardButton(text="Редактировать",
                                         callback_data=main_cb.new("Basket", "EditBasket", id, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new("Main", "", id, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def editBasket_ikb(user_id: int) -> InlineKeyboardMarkup:
        dataBasket = {}
        user = await CRUDUsers.get(user_id=user_id)
        baskets = await CRUDOrderDetail.get_all(user_id=user.id)

        for basket in baskets:
            product = await CRUDProduct.get(product_id=basket.product_id)
            subCategory = await CRUDSubCategory.get(sub_category_id=product.sub_category_id)
            if "Product" in dataBasket:
                dataBasket["Product"] += [{
                    "name": subCategory.name,
                    "quantity": basket.quantity,
                    "id": subCategory.id,
                    "basket_id": basket.id,
                    "product_id": basket.product_id
                }]
            else:
                dataBasket["Product"] = [{
                    "name": subCategory.name,
                    "quantity": basket.quantity,
                    "id": subCategory.id,
                    "basket_id": basket.id,
                    "product_id": basket.product_id
                }]

        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=item['name'],
                                                         callback_data=main_cb.new("Basket", "EdShowName",
                                                                                   item['id'],
                                                                                   0, 0)),

                                    InlineKeyboardButton(text=f"Кол-во {item['quantity']}",
                                                         callback_data=main_cb.new("Basket", "editQuantity",
                                                                                   item['basket_id'],
                                                                                   item['product_id'],
                                                                                   0)),
                                    InlineKeyboardButton(text="Удалить",
                                                         callback_data=main_cb.new("Basket", "editDelete",
                                                                                   item['basket_id'], 0, 0))
                                ]
                                for basket, items in dataBasket.items() for item in items
                            ] + [
                                [
                                    InlineKeyboardButton(text='← Назад',
                                                         callback_data=main_cb.new("Basket", "getBasket", 0, 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def skip_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Пропустить",
                                         callback_data=main_cb.new("Basket", "Confirmation", 0, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Basket", "Confirmation", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def confirmation_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Оформить",
                                         callback_data=main_cb.new("Basket", "SendingAdmins", 0, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="Изменить данные",
                                         callback_data=main_cb.new("Basket", "PlaceInOrder", 0, 0, 0))
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=main_cb.new("Basket", "Confirmation", 0, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def confirmAdmin_ikb(user_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Подтвердить", callback_data=main_cb.new("Admins", "Confirm", user_id, 0, 0)),
                    InlineKeyboardButton(text="Написать", callback_data=main_cb.new("Admins", "WriteUser", user_id, 0, 0)),
                ]
            ]
        )

    @staticmethod
    async def bankCard_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Да", callback_data=main_cb.new("Basket", "BankCard", "yes", 0, 0)),
                    InlineKeyboardButton(text="Нет", callback_data=main_cb.new("Basket", "BankCard", "no", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def back_ikb(target: str, action: str, id: int = 0) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=main_cb.new(target, action, id, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def process(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith("main"):
                data = main_cb.parse(callback_data=callback.data)

                if data.get("target") == "Main":
                    await state.finish()
                    text = "Здравствуйте!\n" \
                           "Чтобы сделать заказ перейдите в раздел меню"
                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForms.main_ikb(user_id=callback.from_user.id))

                elif data.get("target") == "myProfile":
                    if data.get("action") == "getProfile":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        text = ("Профиль\n\n"
                                f"Количество совершенных покупок - {user.purchase_quantity}\n\n"
                                f'<code>https://t.me/MyPersonalUladIslauTestBot?start={callback.from_user.id}</code>')
                        await callback.message.edit_text(text=text,
                                                         parse_mode="HTML",
                                                         reply_markup=await MainForms.back_ikb(target="Main",
                                                                                               action=""))

                elif data.get("target") == "Menu":
                    if data.get("action") == "getMenu":
                        text = "Выберите категорию из списка ⬇️"
                        if await CRUDCategory.get_all():
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await MainForms.category_ikb())
                        else:
                            await callback.message.edit_text(text="Товар временно отсутствует")

                    elif data.get('action') == "Category":
                        category_id = int(data.get('id'))
                        subCategory = await CRUDSubCategory.get_all(category_id=category_id)

                        if subCategory:
                            await state.update_data(category_id=category_id)

                            text = "Нажмите на нужный товар чтобы увидеть подробности"
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await MainForms.sub_category_ikb(
                                                                 category_id=category_id)
                                                             )
                        else:
                            await callback.message.delete()
                            await callback.message.answer(text="Товар временно отсутствует",
                                                          reply_markup=await MainForms.back_ikb(target="Menu",
                                                                                                action="getMenu",
                                                                                                id=category_id))

                    elif data.get('action') == "Product":
                        sub_category_id = int(data.get('id'))
                        category_id = int(data.get('editId'))

                        await state.update_data(sub_category_id=sub_category_id)
                        product = await CRUDProduct.get(category_id=category_id, sub_category_id=sub_category_id)

                        if product:
                            try:
                                photo = open(f'/opt/git/MRPshawarmaBot/image/{product.image_url}.jpg', 'rb')

                                await callback.message.delete()
                                await callback.message.answer_photo(photo=photo,
                                                                    caption=f"_Название: <b>__</b>\n\n"
                                                                            f"Состав: <b>{product.description}</b>\n\n",
                                                                    reply_markup=await MainForms.description_pizza_ikb(
                                                                        price=int(product.price)

                                                                    ),
                                                                    parse_mode="HTML")
                            except FileNotFoundError as e:
                                print(e)
                                await callback.message.delete()
                                await callback.message.answer(text=f"_Название: <b>__</b>\n\n"
                                                                   f"Состав: <b>{product.description}</b>\n\n",
                                                              reply_markup=await MainForms.description_pizza_ikb(
                                                                  price=int(product.price)),
                                                              parse_mode="HTML"
                                                              )
                        else:
                            await callback.message.edit_text(text="Товар временно отсутствует",
                                                             reply_markup=await MainForms.back_ikb(target="Menu",
                                                                                                   action="Category",
                                                                                                   id=category_id))

                    elif data.get('action') == 'ProductsPage':
                        page = int(data.get('id'))
                        get_state_data = await state.get_data()
                        product = await CRUDProduct.get(category_id=int(get_state_data['category_id']),
                                                        sub_category_id=int(get_state_data['sub_category_id']))
                        try:
                            photo = open(f'/opt/git/MRPshawarmaBot/image/{product.image_url}.jpg', 'rb')

                            await callback.message.delete()
                            await callback.message.answer_photo(photo=photo,
                                                                caption=f"Название: <b>__</b>\n\n"
                                                                        f"Состав: <b>{product.description}</b>\n\n",
                                                                reply_markup=await MainForms.description_pizza_ikb(
                                                                    page=page,
                                                                    price=int(product.price)
                                                                ),
                                                                parse_mode="HTML")
                        except FileNotFoundError as e:
                            print(e)
                            await callback.message.delete()
                            await callback.message.answer(text=f"_Название: <b>__</b>\n\n"
                                                               f"Состав: <b>{product.description}</b>\n\n",
                                                          parse_mode="HTML",
                                                          reply_markup=await MainForms.description_pizza_ikb(
                                                              page=page,
                                                              price=int(product.price))
                                                          )

                    elif data.get('action') == 'InBasket':
                        try:
                            count = int(data.get('id'))
                            get_state_data = await state.get_data()
                            product = await CRUDProduct.get(category_id=1,
                                                            sub_category_id=1)
                            logging.info(f'cat: {int(get_state_data["category_id"])}')
                            logging.info(f"sub_cat: {int(get_state_data['sub_category_id'])}")

                            orderDetails = await CRUDOrderDetail.get(user_id=callback.from_user.id)

                            orderDetailsProduct = await CRUDOrderDetail.get(user_id=callback.from_user.id,
                                                                            product_id=product.id)
                            if orderDetailsProduct:
                                orderDetailsProduct.quantity = count
                                orderDetailsProduct.subtotal = product.price * count

                                await CRUDOrderDetail.update(orderDetail=orderDetailsProduct)
                                text = "Обновили товар в корзине"

                                await callback.message.delete()
                                await callback.message.answer(text=f"Вы успешно {text} !",
                                                              reply_markup=await MainForms.main_ikb(
                                                                  user_id=callback.from_user.id))
                            else:
                                texts = "Добавили товар в корзину"
                                user = await CRUDUsers.get(user_id=callback.from_user.id)
                                await CRUDOrderDetail.add(orderDetail=OrderDetailSchema(
                                    user_id=user.id,
                                    product_id=product.id,
                                    quantity=count,
                                    subtotal=product.price * count
                                ))
                                await callback.message.delete()
                                await callback.message.answer(text=f"Вы успешно {texts} !",
                                                              reply_markup=await MainForms.main_ikb(
                                                                  user_id=callback.from_user.id))
                        except Exception as e:
                            logging.error(f'Error in add basket: {e}')

                elif data.get('target') == "Basket":
                    if data.get('action') == "getBasket":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        basket = await CRUDOrderDetail.get_all(user_id=user.id)
                        if basket:
                            textBasket = await MainForms.check(get_basket=basket)
                            await callback.message.edit_text(text=textBasket,
                                                             reply_markup=await MainForms.basket_ikb()
                                                             )
                        else:
                            text = "Ваша корзина пуста!\n" \
                                   "Добавьте в меню"
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await MainForms.back_ikb(
                                                                 target="Main",
                                                                 action=""
                                                             ))

                    elif data.get('action') == "PlaceInOrder":
                        await state.finish()
                        await callback.message.edit_text(text="Введите ваше Имя",
                                                         reply_markup=await MainForms.back_ikb(target="Basket",
                                                                                               action="getBasket"))
                        await UserStates.USERNAME.set()

                    elif data.get('action') == "BankCard":
                        await state.update_data(bankcard=data.get('id'))
                        await callback.message.edit_text(text="Уточните детали заказа",
                                                         reply_markup=await MainForms.skip_ikb())
                        await UserStates.DESCRIPTION.set()

                    elif data.get('action') == "Confirmation":
                        await state.update_data(description="Без описания")
                        await MainForms.order(callback=callback, state=state)

                    elif data.get('action') == "SendingAdmins":
                        getDataState = await state.get_data()
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        user.purchase_quantity += 1
                        await CRUDUsers.update(user=user)
                        get_numer = 0
                        try:
                            bankCard = True if getDataState['bankcard'] == "yes" else False
                            get_numer = await CRUDOrder.add(order=OrderSchema(user_id=callback.from_user.id,
                                                                              userName=getDataState['userName'],
                                                                              total_amount=0,
                                                                              phone=getDataState['phone'],
                                                                              time=getDataState['time'],
                                                                              description=getDataState['description'],
                                                                              bankcard=bankCard
                                                                              )
                                                            )
                            await callback.message.edit_text(text=f"Вы успешно оформили заказ <b>№{get_numer.id}</b>\n"
                                                                  "Как только заказ будет готов вам придет сообщение",
                                                             reply_markup=await MainForms.main_ikb(user_id=callback.from_user.id),
                                                             parse_mode="HTML")

                        except Exception as e:
                            print(f'add order error {e}')
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        basket = await CRUDOrderDetail.get_all(user_id=user.id)
                        textBasket = await MainForms.check(get_basket=basket)

                        text = f"Новая заявка № {get_numer.id}!\n\n" \
                               f"Имя - <b>{getDataState['userName']}</b>\n"\
                               f"Телефон - <code>{getDataState['phone']}</code>\n"\
                               f"Время - <b>{getDataState['time']}</b>\n"\
                               f"<tg-spoiler>----------------------------"\
                               f"</tg-spoiler>\n\n"\
                               f"{textBasket}"

                        tasks = []
                        for user in CONFIG.BOT.ADMINS:
                            tasks.append(bot.send_message(chat_id=user,
                                                          text=text,
                                                          reply_markup=await MainForms.confirmAdmin_ikb(
                                                              user_id=callback.from_user.id
                                                          ))
                                         )

                        await asyncio.gather(*tasks, return_exceptions=True)
                        await state.finish()

                    elif data.get('action') == "EditBasket":
                        await state.finish()
                        await callback.message.edit_text(text="Редактирование корзины",
                                                         reply_markup=await MainForms.editBasket_ikb(
                                                             user_id=callback.from_user.id)
                                                         )

                    elif data.get('action') == "EdShowName":
                        subCategory = await CRUDSubCategory.get(sub_category_id=int(data.get('id')))
                        await callback.answer(text=subCategory.name)

                    elif data.get('action') == "editDelete":
                        await CRUDOrderDetail.delete(orderDetail_id=int(data.get('id')))
                        await callback.answer(text="Вы удалили товар!")
                        await callback.message.edit_text("Редактирование корзины",
                                                         reply_markup=await MainForms.editBasket_ikb(
                                                             user_id=callback.from_user.id))

                    elif data.get('action') == "editQuantity":
                        await state.update_data(basket_id=int(data.get('id')))
                        await state.update_data(product_id=int(data.get('editId')))

                        await callback.message.edit_text("Введите количество!")
                        await UserStates.Quantity.set()

                elif data.get('target') == "Admins":
                    if data.get('action') == "Confirm":
                        await bot.send_message(chat_id=int(data.get('id')),
                                               text="Ваш заказ готовиться!")

                    elif data.get('action') == "WriteUser":
                        await state.update_data(user_id=int(data.get('id')))
                        await callback.message.answer(text="Напишите что бы ответить пользователю",
                                                      reply_markup=await MainForms.back_ikb(target="Main",
                                                                                               action=""))
                        await UserStates.WriteUser.set()

        if message:
            await message.delete()

            try:
                await bot.delete_message(
                    chat_id=message.from_user.id,
                    message_id=message.message_id - 1
                )
            except BadRequest:
                pass

            if state:
                if await state.get_state() == "UserStates:USERNAME":
                    await state.update_data(userName=message.text)
                    await message.answer(text="Введите ваш номер телефона",
                                         reply_markup=await MainForms.back_ikb(target="Basket",
                                                                               action="PlaceInOrder"))
                    await UserStates.Phone.set()

                elif await state.get_state() == "UserStates:Phone":
                    try:
                        phone_number = message.text
                        if phone_number[0] in "+":
                            phone_number = phone_number[1:]

                        if re.match(r"^(?:375|80)[0-9]{9}$", phone_number):
                            await state.update_data(phone=message.text)
                            await message.answer(text="Уточните, к какому времени вы хотели бы забрать заказ?",
                                                 reply_markup=await MainForms.back_ikb(target="",
                                                                                       action=""))
                            await UserStates.Time.set()
                        else:
                            await message.answer(text="Номер телефона введен не верно",
                                                 reply_markup=await MainForms.back_ikb(target="Basket",
                                                                                       action="PlaceInOrder"))
                            await UserStates.Phone.set()
                    except Exception as e:
                        print(f"Phone number error - {e}")

                        await message.answer(text="Номер телефона введен не верно",
                                             reply_markup=await MainForms.back_ikb(target="Basket",
                                                                                   action="PlaceInOrder"))
                        await UserStates.Phone.set()

                elif await state.get_state() == "UserStates:Time":
                    await state.update_data(time=message.text)
                    await message.answer(text="Оплата картой?",
                                         reply_markup=await MainForms.bankCard_ikb())

                elif await state.get_state() == "UserStates:DESCRIPTION":
                    await state.update_data(description=message.text)
                    await MainForms.order(message=message, state=state)

                elif await state.get_state() == "UserStates:Quantity":
                    if message.text.isdigit():
                        getStateData = await state.get_data()
                        product = await CRUDProduct.get(product_id=int(getStateData['product_id']))
                        order_details = await CRUDOrderDetail.get(basket_id=getStateData['basket_id'])
                        order_details.quantity = int(message.text)
                        order_details.subtotal = int(message.text) * product.price
                        await CRUDOrderDetail.update(orderDetail=order_details)
                        await message.answer(text="Редактирование корзины",
                                             reply_markup=await MainForms.editBasket_ikb(user_id=message.from_user.id))
                        await state.finish()
                    else:
                        await message.answer(text="Введите число!",
                                             reply_markup=await MainForms.back_ikb(target="Basket",
                                                                                   action="EditBasket"))
                        await UserStates.Quantity.set()

                elif await state.get_state() == "UserStates:WriteUser":
                    getStateData = await state.get_data()
                    await bot.send_message(chat_id=int(getStateData['user_id']),
                                           text=message.text)

                    await state.finish()
