from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import OrderDetail, create_async_session
from schemas import OrderDetailSchema, OrderDetailInDBSchema


class CRUDOrderDetail(object):

    @staticmethod
    @create_async_session
    async def add(orderDetail: OrderDetailSchema, session: AsyncSession = None) -> OrderDetailInDBSchema | None:
        orderDetails = OrderDetail(
            **orderDetail.dict()
        )
        session.add(orderDetails)
        try:
            await session.commit()
        except IntegrityError:
            pass
        else:
            await session.refresh(orderDetails)
            return OrderDetailInDBSchema(**orderDetails.__dict__)

    @staticmethod
    @create_async_session
    async def delete(orderDetail_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(OrderDetail)
            .where(OrderDetail.id == orderDetail_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get_all(user_id: int,session: AsyncSession = None) -> list[OrderDetailInDBSchema]:
        if user_id:
            orderDetails = await session.execute(
                select(OrderDetail).where(OrderDetail.user_id == user_id)
                .order_by(OrderDetail.id)
            )
        else:
            orderDetails = await session.execute(
                select(OrderDetail)
                .order_by(OrderDetail.id)
            )
        return [OrderDetailInDBSchema(**orderDetail[0].__dict__) for orderDetail in orderDetails]

    @staticmethod
    @create_async_session
    async def get(basket_id: int = None,
                  user_id: int = None,
                  product_id: int = None,
                  session: AsyncSession = None) -> OrderDetailInDBSchema | None:
        if basket_id:
            orderDetails = await session.execute(
                select(OrderDetail)
                .where(OrderDetail.id == basket_id)
            )
        elif product_id:
            orderDetails = await session.execute(
                select(OrderDetail)
                .where(OrderDetail.user_id == user_id).where(OrderDetail.product_id == product_id)
            )
        else:
            orderDetails = await session.execute(
                select(OrderDetail)
                .where(OrderDetail.user_id == user_id)
            )
        if orderDetail := orderDetails.first():
            return OrderDetailInDBSchema(**orderDetail[0].__dict__)

    @staticmethod
    @create_async_session
    async def update(orderDetail: OrderDetailInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(OrderDetail)
            .where(OrderDetail.id == orderDetail.id)
            .values(**orderDetail.dict())
        )
        await session.commit()
