from flask import request

from . import bp, services


@bp.post("/")
def create_customer():
    customer = services.create_customer(request.get_json()["email"])
    return {"id": customer.id, "email": customer.email}, 201
