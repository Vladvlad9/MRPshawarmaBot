from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Category, create_async_session
from schemas import CategoryInDBSchema


class CRUDCategory(object):

    @staticmethod
    @create_async_session
    async def get(category_id: int = None,
                  session: AsyncSession = None) -> CategoryInDBSchema | None:
        categories = await session.execute(
            select(Category)
            .where(Category.id == category_id)
        )
        if category := categories.first():
            return CategoryInDBSchema(**category[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[CategoryInDBSchema]:
        categories = await session.execute(
            select(Category)
        )
        return [CategoryInDBSchema(**category[0].__dict__) for category in categories]

