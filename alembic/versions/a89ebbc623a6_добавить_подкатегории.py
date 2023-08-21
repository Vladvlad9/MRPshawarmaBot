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


values = {
    'Ланч Бокс Острый': 1,
    'Ланч Бокс Сырный': 1,
    'Ланч Бокс Терияки': 1,
    'Гриль Дог': 2,
    'Хот-дог в булочке': 2,
    'Донер Классический 🌯': 3,
    'Донер Сырный 🧀': 3,
    'Донер Грибной 🍄': 3,
    'Донер Греческий 🫒': 3,
    'Донер Фри 🍟': 3,
    'Донер Гавайский  🏄‍♂️': 3,
    'Донер Цезарь 🥙': 3,
    'Донер Фалафель 🌱': 3,
    'Донер Бульбаш 🥔': 3,
    'Донер Терияки 🥡': 3,
    'Донер Америка 🏈': 3,
    'Донер Гриль 🍗': 3,
    'Картофель фри': 4,
}


@create_sync_session
def upgrade(session: Session = None) -> None:
    for value, item in values.items():
        value = SubCategory(name=value, category_id=item)
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
