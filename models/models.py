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
    category_id = Column(Integer, ForeignKey('categories.id'))
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'))
    size_id = Column(Integer, ForeignKey('sizes.id'))
    description = Column(Text)
    price = Column(Float)
    image_url = Column(Text)

    category = relationship("Category", back_populates="products")
    sub_categories = relationship("SubCategory", back_populates="products")
    sizes = relationship("Size", back_populates="products")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    userName = Column(Text)
    user_id = Column(Integer)
    order_date = Column(TIMESTAMP, default=datetime.now())
    total_amount = Column(Float)
    phone = Column(Text)
    time = Column(Text)
    description = Column(Text)
    confirm = Column(Boolean)
    bankcard = Column(Boolean)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    purchase_quantity = Column(Integer)


class OrderDetail(Base):
    __tablename__ = 'order_details'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    subtotal = Column(Float)

    product = relationship("Product")


class Referrals(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    referring_user_id = Column(Integer, ForeignKey('users.id'))
    referred_user_id = Column(Integer, ForeignKey('users.id'))


