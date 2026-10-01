from app.extensions import db


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.ForeignKey("customer.id"), nullable=False)
    total_pence = db.Column(db.Integer, nullable=False)
