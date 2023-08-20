from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import SubCategory, create_async_session
from schemas import SubCategoryInDBSchema


class CRUDSubCategory(object):

    @staticmethod
    @create_async_session
    async def get(sub_category_id: int = None,
                  session: AsyncSession = None) -> SubCategoryInDBSchema | None:
        sub_categories = await session.execute(
            select(SubCategory)
            .where(SubCategory.id == sub_category_id)
        )
        if sub_category := sub_categories.first():
            return SubCategoryInDBSchema(**sub_category[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(category_id:int, session: AsyncSession = None) -> list[SubCategoryInDBSchema]:
        sub_categories = await session.execute(
            select(SubCategory).where(SubCategory.category_id == category_id)
        )
        return [SubCategoryInDBSchema(**sub_category[0].__dict__) for sub_category in sub_categories]

