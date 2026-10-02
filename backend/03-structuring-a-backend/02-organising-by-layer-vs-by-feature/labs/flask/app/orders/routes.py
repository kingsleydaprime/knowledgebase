from flask import render_template, request

from . import bp, services


@bp.post("/")
def place_order():
    body = request.get_json()
    order = services.place_order(body["customer_id"], body["total_pence"])
    return {"id": order.id, "total_pence": order.total_pence}, 201


@bp.get("/")
def list_orders():
    return render_template("orders/list.html", orders=services.list_orders())
