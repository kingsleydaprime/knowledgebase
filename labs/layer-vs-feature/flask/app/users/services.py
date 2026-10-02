from app.extensions import db

from .models import Customer


def create_customer(email: str) -> Customer:
    customer = Customer(email=email)
    db.session.add(customer)
    db.session.commit()
    return customer


def get_customer(customer_id: int) -> Customer:
    return db.get_or_404(Customer, customer_id)
