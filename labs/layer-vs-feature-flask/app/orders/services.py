from app.extensions import db
from app.users.services import get_customer

from .models import Order


def place_order(customer_id: int, total_pence: int) -> Order:
    customer = get_customer(customer_id)
    order = Order(customer_id=customer.id, total_pence=total_pence)
    db.session.add(order)
    db.session.commit()
    return order


def list_orders() -> list[Order]:
    return db.session.scalars(db.select(Order)).all()
