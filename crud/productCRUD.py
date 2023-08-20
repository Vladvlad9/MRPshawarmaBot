from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Product, create_async_session
from schemas import ProductInDBSchema


class CRUDProduct(object):

    @staticmethod
    @create_async_session
    async def get(
            product_id: int = None,
            category_id: int = None,
            sub_category_id: int = None,
            session: AsyncSession = None) -> ProductInDBSchema | None:

        if product_id:
            products = await session.execute(
                select(Product).where(Product.id == product_id)
            )
        else:
            products = await session.execute(
                select(Product)
                .where(Product.sub_category_id == sub_category_id).where(Product.category_id == category_id)
            )
        if product := products.first():
            return ProductInDBSchema(**product[0].__dict__)


