from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Size, create_async_session
from schemas import SizeInDBSchema


class CRUDSize(object):

    @staticmethod
    @create_async_session
    async def get(size_id: int = None,
                  session: AsyncSession = None) -> SizeInDBSchema | None:
        sizes = await session.execute(
            select(Size)
            .where(Size.id == size_id)
        )
        if sizesF := sizes.first():
            return SizeInDBSchema(**sizesF[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[SizeInDBSchema]:
        sizes = await session.execute(
            select(Size)
            .order_by(Size.id)
        )
        return [SizeInDBSchema(**size[0].__dict__) for size in sizes]

    @staticmethod
    @create_async_session
    async def update(sizes: SizeInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Size)
            .where(Size.id == sizes.id)
            .values(**sizes.dict())
        )
        await session.commit()
