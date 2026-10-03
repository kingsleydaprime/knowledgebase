"""What an API style costs, counted: REST requests and bytes, a GraphQL-style query with the N+1 problem and
batching, Protocol Buffers' varints, and synchronous chains. The same numbers as the TypeScript lab."""
import json
import math
from typing import Callable

Selection = dict  # field → True, or a nested selection
FIELD_TYPES = {"Order.customer": "Customer", "Order.items": "Item", "Item.product": "Product"}


def compact(value) -> str:
    """JSON as JavaScript's JSON.stringify writes it. json.dumps puts a space after every ',' and ':' by default."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


class Db:
    """A tiny shop database that counts its queries."""

    def __init__(self, shop: dict):
        self.queries = 0
        self.customers = {c["id"]: c for c in shop["customers"]}
        self.products = {p["id"]: p for p in shop["products"]}
        self.orders = {o["id"]: o for o in shop["orders"]}

    def find(self, table: str, ids: list[str]) -> list[dict]:
        """One query for any number of rows: SELECT … WHERE id IN (…)."""
        self.queries += 1
        rows = getattr(self, table)
        return [rows[i] for i in ids]


class RestApi:
    """One resource per URL, always returned whole. Counts requests and bytes sent."""

    def __init__(self, db: Db):
        self.db, self.requests, self.bytes = db, 0, 0

    def get(self, path: str) -> dict:
        _, kind, id_ = path.split("/")
        if kind not in ("orders", "customers", "products"):
            raise LookupError(f"404 {path}")
        body = self.db.find(kind, [id_])[0]
        self.requests += 1
        self.bytes += len(compact(body))
        return body


def order_screen_rest(api: RestApi, order_id: str) -> tuple[dict, int]:
    """The order first (round trip 1), then its customer and products together (round trip 2)."""
    order = api.get(f"/orders/{order_id}")
    customer = api.get(f"/customers/{order['customerId']}")
    products = [api.get(f"/products/{i['productId']}") for i in order["items"]]
    screen = {
        "id": order["id"],
        "totalPence": order["totalPence"],
        "customer": {"name": customer["name"]},
        "items": [{"quantity": i["quantity"], "product": {"name": p["name"]}} for i, p in zip(order["items"], products)],
    }
    return screen, 2


Resolvers = dict[str, Callable[[list[dict]], list]]


def execute(values: list[dict], selection: Selection, resolvers: Resolvers, type_: str) -> list[dict]:
    """Runs a selection over every object at one level of the query at once, so a resolver sees them all."""
    outs: list[dict] = [{} for _ in values]
    for field, sub in selection.items():
        resolver = resolvers.get(f"{type_}.{field}")
        children = resolver(values) if resolver else [v[field] for v in values]
        if sub is True:
            for out, child in zip(outs, children):
                out[field] = child
        elif children and isinstance(children[0], list):  # a list field: all its elements form the next level
            flat = [c for cs in children for c in cs]
            done = iter(execute(flat, sub, resolvers, FIELD_TYPES[f"{type_}.{field}"]))
            for out, cs in zip(outs, children):
                out[field] = [next(done) for _ in cs]
        else:
            for out, result in zip(outs, execute(children, sub, resolvers, FIELD_TYPES[f"{type_}.{field}"])):
                out[field] = result
    return outs


def resolvers(db: Db, batched: bool) -> Resolvers:
    """One query per parent (the N+1 problem), or one query for the whole level."""
    def one_each(table: str, key: str):
        return lambda parents: [db.find(table, [p[key]])[0] for p in parents]

    def all_at_once(table: str, key: str):
        def resolve(parents):
            ids = list(dict.fromkeys(p[key] for p in parents))  # each ID once, in first-seen order
            rows = dict(zip(ids, db.find(table, ids)))
            return [rows[p[key]] for p in parents]
        return resolve

    make = all_at_once if batched else one_each
    return {"Order.customer": make("customers", "customerId"), "Item.product": make("products", "productId")}


def varint(n: int) -> bytes:
    """Base-128: 7 bits a byte, low bits first, top bit set if more follow. Python ints never overflow."""
    if n < 0:
        raise ValueError("varint takes a whole number from 0")
    out = bytearray()
    while True:
        byte, n = n & 0x7F, n >> 7
        out.append(byte | 0x80 if n else byte)
        if not n:
            return bytes(out)


def encode_order_summary(id_: int, customer: str, total_pence: int) -> bytes:
    text = customer.encode("utf-8")
    return (varint(1 << 3 | 0) + varint(id_)
            + varint(2 << 3 | 2) + varint(len(text)) + text
            + varint(3 << 3 | 0) + varint(total_pence))


def chain(services: list[tuple[float, float]]) -> dict:
    """(availability, ms) for each call in a row."""
    return {"availability": math.prod(a for a, _ in services),
            "sequential_ms": sum(ms for _, ms in services),
            "parallel_ms": max(ms for _, ms in services)}
