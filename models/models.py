from datetime import datetime

from sqlalchemy import Column, TIMESTAMP, VARCHAR, Float, Integer, Boolean, Text, ForeignKey, CHAR, BigInteger, SmallInteger
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Size(Base):
    __tablename__ = 'sizes'

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    products = relationship("Product", back_populates="sizes")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    products = relationship("Product", back_populates="category")


class SubCategory(Base):
    __tablename__ = 'sub_categories'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(Text)

    products = relationship("Product", back_populates="sub_categories")


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    description = Column(Text)
    price = Column(Float)
    image_url = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'))
    size_id = Column(Integer, ForeignKey('sizes.id'))

    category = relationship("Category", back_populates="products")
    sub_categories = relationship("SubCategory", back_populates="products")
    sizes = relationship("Size", back_populates="products")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    customer_name = Column(Text)
    customer_email = Column(Text)
    order_date = Column(TIMESTAMP, default=datetime.now())
    total_amount = Column(Float)



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    referred_by_id = Column(Integer, ForeignKey('referrals.id'))



class OrderDetail(Base):
    __tablename__ = 'order_details'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    subtotal = Column(Float)

    product = relationship("Product")





class Referrals(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    referring_user_id = Column(Integer, ForeignKey('users.id'))
    referred_user_id = Column(Integer, ForeignKey('users.id'))


