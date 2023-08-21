"""добавлние продуктов

Revision ID: 696211eea28e
Revises: a89ebbc623a6
Create Date: 2023-08-21 23:28:46.286547

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from models import create_sync_session, Product
from sqlalchemy.exc import IntegrityError


# revision identifiers, used by Alembic.
revision = '696211eea28e'
down_revision = 'a89ebbc623a6'
branch_labels = None
depends_on = None

values = {
    'Ланч Бокс Острый': {"description": "Горчичный соус, Соус чесночный, Картофель-фри, Томат, Огурец маринованный, Халапеньо, Мясо",
                         "price": 9,
                         "size": 1,
                         "image_url": "Ланч Бокс Острый",
                         "category_id": 1,
                         "sub_category_id": 1},
    'Ланч Бокс Сырный': {"description": "Сырный соус, Соус чесночный, Картофель-фри, Томат, Огурец маринованый, Сыр, Мясо",
                         "price": 9,
                         "size": 1,
                         "image_url": "Ланч Бокс Сырный",
                         "category_id": 1,
                         "sub_category_id": 2
    },
    'Гриль Дог': {"description": "Сырный соус, Соус чесночный, Картофель-фри, Томат, Огурец маринованый, Сыр, Мясо",
                         "price": 8,
                         "size": 1,
                         "image_url": "Гриль Дог",
                         "category_id": 2,
                         "sub_category_id": 4
    },
    'Донер Классик': {"description": "Соус чесночный, Мясо, Капуста, Огурец маринованный, Томат, Лавашо",
                         "price": 8,
                         "size": 1,
                         "image_url": "Донер Классик",
                         "category_id": 3,
                         "sub_category_id": 6
    },
'Картофель фри': {"description": "Соус чесночный, Мясо, Капуста, Огурец маринованный, Томат, Лавашо",
                         "price": 8,
                         "size": 1,
                         "image_url": "Картофель фри",
                         "category_id": 4,
                         "sub_category_id": 18
    }
}


@create_sync_session
def upgrade(session: Session = None) -> None:
    for value, item in values.items():
        value = Product(description=item['description'],
                        price=item['price'],
                        size_id=item['size'],
                        image_url=item['image_url'],
                        category_id=item['category_id'],
                        sub_category_id=item['sub_category_id'])
        session.add(value)
        try:
            session.commit()
        except IntegrityError as e:
            print(e)


@create_sync_session
def downgrade(session: Session = None) -> None:
    for value in values:
        session.execute(sa.delete(Product).where(Product.id == value)
        )
        session.commit()
