"""Добавить категории

Revision ID: e7f787bb57d6
Revises: ddf80c5a1de4
Create Date: 2023-08-18 11:31:51.000554

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from models import create_sync_session, Category
from sqlalchemy.exc import IntegrityError

# revision identifiers, used by Alembic.
revision = 'e7f787bb57d6'
down_revision = 'ddf80c5a1de4'
branch_labels = None
depends_on = None

values = [
    'Ланчи',
    'Хот-доги 🌭',
    'Донеры',
    'Картофель 🍟',
]


@create_sync_session
def upgrade(session: Session = None) -> None:
    for value in values:
        value = Category(name=value)
        session.add(value)
        try:
            session.commit()
        except IntegrityError as e:
            print(e)


@create_sync_session
def downgrade(session: Session = None) -> None:
    for value in values:
        session.execute(
            sa.delete(Category)
            .where(Category.name == value)
        )
        session.commit()
