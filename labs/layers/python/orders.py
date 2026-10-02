"""orders.py — three layers; domain errors are exceptions, mapped to HTTP in one place."""
from dataclasses import dataclass


class EmptyOrderError(Exception):
    pass


class OutOfStockError(Exception):
    def __init__(self, sku: str):
        super().__init__(f"out of stock: {sku}")
        self.sku = sku


@dataclass
class Item:
    sku: str
    quantity: int


class Repository:
    """The only code that knows how stock and orders are stored."""

    def __init__(self, stock: dict[str, int]):
        self.stock = stock
        self.orders: list[list[Item]] = []

    def stock_of(self, sku: str) -> int:
        return self.stock.get(sku, 0)

    def reserve(self, sku: str, quantity: int) -> None:
        self.stock[sku] -= quantity

    def create(self, items: list[Item]) -> int:
        self.orders.append(items)
        return len(self.orders)


class Service:
    """Business rules. Knows nothing about HTTP."""

    def __init__(self, repo: Repository):
        self.repo = repo

    def place(self, items: list[Item]) -> int:
        if not items:
            raise EmptyOrderError("an order needs at least one item")
        for item in items:
            if self.repo.stock_of(item.sku) < item.quantity:
                raise OutOfStockError(item.sku)
        for item in items:
            self.repo.reserve(item.sku, item.quantity)
        return self.repo.create(items)


def create_order(service: Service, body: dict) -> tuple[int, dict]:
    """The controller: HTTP in, HTTP out. In FastAPI this mapping would be an exception handler."""
    items = [Item(i["sku"], i["quantity"]) for i in body.get("items", [])]
    try:
        return 201, {"id": service.place(items)}
    except EmptyOrderError as e:
        return 400, {"error": str(e)}
    except OutOfStockError as e:
        return 409, {"error": str(e), "sku": e.sku}
