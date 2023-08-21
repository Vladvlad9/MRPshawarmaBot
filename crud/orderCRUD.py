from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Order, create_async_session
from schemas import OrderInDBSchema, OrderSchema


class CRUDOrder(object):

    @staticmethod
    @create_async_session
    async def add(order: OrderSchema, session: AsyncSession = None) -> OrderInDBSchema | None:
        order = Order(
            **order.dict()
        )
        session.add(order)
        try:
            await session.commit()
        except IntegrityError:
            pass
        else:
            await session.refresh(order)
            return OrderInDBSchema(**order.__dict__)

    @staticmethod
    @create_async_session
    async def delete(order_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Order)
            .where(Order.id == order_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get_all(user_id: int, session: AsyncSession = None) -> list[OrderInDBSchema]:
        if user_id:
            orders = await session.execute(
                select(Order).where(Order.user_id == user_id)
                .order_by(Order.id)
            )
        else:
            orders = await session.execute(
                select(Order)
                .order_by(Order.id)
            )
        return [OrderInDBSchema(**order[0].__dict__) for order in orders]

    @staticmethod
    @create_async_session
    async def get(user_id: int = None,
                  product_id: int = None,
                  session: AsyncSession = None) -> OrderInDBSchema | None:
        if product_id:
            orders = await session.execute(
                select(Order)
                .where(Order.user_id == user_id).where(Order.product_id == product_id)
            )
        else:
            orders = await session.execute(
                select(Order)
                .where(Order.user_id == user_id)
            )
        if order := orders.first():
            return OrderInDBSchema(**order[0].__dict__)

    @staticmethod
    @create_async_session
    async def update(order: OrderInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Order)
            .where(Order.id == order.id)
            .values(**order.dict())
        )
        await session.commit()
