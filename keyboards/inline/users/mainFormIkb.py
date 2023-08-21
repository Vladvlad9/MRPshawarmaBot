import logging

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData

from config import CONFIG
from crud import CRUDSubCategory, CRUDProduct
from crud.categoryCRUD import CRUDCategory
from crud.orderDetailCRUD import CRUDOrderDetail
from crud.sizeCRUD import CRUDSize
from crud.userCRUD import CRUDUsers
from loader import bot
from schemas import OrderDetailSchema

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
    async def main_ikb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Меню",
                                         callback_data=main_cb.new("Menu", "getMenu", 0, 0, 0)),

                ],
                [
                    InlineKeyboardButton(text="Корзина",
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
                    text = "Здравствуйте!\n" \
                           "Чтобы сделать заказ перейдите в раздел меню"
                    await callback.message.edit_text(text=text,
                                                     reply_markup=await MainForms.main_ikb())

                elif data.get("target") == "myProfile":
                    if data.get("action") == "getProfile":
                        user = await CRUDUsers.get(user_id=callback.from_user.id)
                        text = ("Профиль\n\n"
                                f"Количество совершенных покупок - {user.purchase_quantity}\n\n"
                                f"Реферальная ссылка - ")
                        await callback.message.edit_text(text=text,
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
                                photo = open(f'image/{product.image_url}.jpg', 'rb')

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
                                                                                                   id=sub_category_id))

                    elif data.get('action') == 'ProductsPage':
                        page = int(data.get('id'))
                        get_state_data = await state.get_data()
                        product = await CRUDProduct.get(category_id=int(get_state_data['category_id']),
                                                        sub_category_id=int(get_state_data['sub_category_id']))
                        try:
                            photo = open(f'image/{product.image_url}.jpg', 'rb')

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
                        count = int(data.get('id'))

                        get_state_data = await state.get_data()
                        product = await CRUDProduct.get(category_id=int(get_state_data['category_id']),
                                                        sub_category_id=int(get_state_data['sub_category_id']))
                        orderDetails = await CRUDOrderDetail.get(user_id=callback.from_user.id)

                        if orderDetails:
                            orderDetailsProduct = await CRUDOrderDetail.get(user_id=callback.from_user.id,
                                                                            product_id=product.id)
                            if orderDetailsProduct:
                                orderDetailsProduct.quantity = count
                                orderDetailsProduct.subtotal = product.price * count

                                await CRUDOrderDetail.update(orderDetail=orderDetailsProduct)
                                text = "Обновили товар в корзине"


                                await callback.message.delete()
                                await callback.message.answer(text=f"Вы успешно {text} !",
                                                              reply_markup=await MainForms.main_ikb())
                        else:
                            text = "Добавили товар в корзину"
                            await CRUDOrderDetail.add(orderDetail=OrderDetailSchema(
                                user_id=callback.from_user.id,
                                product_id=product.id,
                                quantity=count,
                                subtotal=product.price * count
                            ))
                        await callback.message.delete()
                        await callback.message.answer(text=f"Вы успешно {text} !",
                                                      reply_markup=await MainForms.main_ikb())

                elif data.get('target') == "Basket":
                    if data.get('action') == "getBasket":
                        basket = await CRUDOrderDetail.get_all(user_id=callback.from_user.id)
                        if basket:
                            textBasket = await MainForms.check(get_basket=basket)
                            await callback.message.edit_text(text=textBasket,
                                                             reply_markup=await MainForms.back_ikb(target="Main",
                                                                                                   action="")
                                                             )
                        else:
                            text = "Ваша корзина пуста!\n" \
                                   "Добавьте в меню"
                            await callback.message.edit_text(text=text,
                                                             reply_markup=await MainForms.back_ikb(
                                                                 target="Main",
                                                                 action=""
                                                             ))
