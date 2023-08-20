"""Добавить подкатегории

Revision ID: a89ebbc623a6
Revises: e7f787bb57d6
Create Date: 2023-08-18 12:15:25.523471

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from models import create_sync_session, SubCategory
from sqlalchemy.exc import IntegrityError


# revision identifiers, used by Alembic.
revision = 'a89ebbc623a6'
down_revision = 'e7f787bb57d6'
branch_labels = None
depends_on = None


values = [
    'Ланч Бокс Острый',
    'Ланч Бокс Сырный',
    'Ланч Бокс Терияки',
    'Гриль Дог',
    'Хот-дог в булочке',
    'Донер Классический 🌯',
    'Донер Сырный 🧀',
    'Донер Грибной 🍄',
    'Донер Греческий 🫒',
    'Донер Фри 🍟',
    'Донер Гавайский  🏄‍♂️',
    'Донер Цезарь 🥙',
    'Донер Фалафель 🌱',
    'Донер Бульбаш 🥔',
    'Донер Терияки 🥡',
    'Донер Америка 🏈',
    'Донер Гриль 🍗',
    'Картофель фри',
]


@create_sync_session
def upgrade(session: Session = None) -> None:
    for value in values:
        value = SubCategory(name=value)
        session.add(value)
        try:
            session.commit()
        except IntegrityError as e:
            print(e)


@create_sync_session
def downgrade(session: Session = None) -> None:
    for value in values:
        session.execute(
            sa.delete(SubCategory)
            .where(SubCategory.name == value)
        )
        session.commit()
