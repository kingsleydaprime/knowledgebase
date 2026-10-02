"""fees.py — open (a dict of functions) and closed (an Enum with an exhaustive match)."""
from enum import Enum
from typing import Callable, assert_never

# Open for extension: a new method is a new entry; no existing rule is edited.
OPEN_RULES: dict[str, Callable[[int], int]] = {
    "card": lambda amount_kobo: amount_kobo * 29 // 1000,
    "transfer": lambda _: 50,
}


class Method(Enum):
    CARD = "card"
    TRANSFER = "transfer"


def fee(method: Method, amount_kobo: int) -> int:
    match method:
        case Method.CARD:
            return amount_kobo * 29 // 1000
        case Method.TRANSFER:
            return 50
        case _:
            assert_never(method)  # a type checker errors here if a member is unhandled
