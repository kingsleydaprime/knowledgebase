"""Structured output with Pydantic: one class is the schema sent to the model, the parser, the
validator and the type your code uses."""
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)  # strict: 655.5 is not an int, "450" is not an int
    description: str
    amount_cents: int


class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)  # extra="forbid" → "additionalProperties": false
    vendor: str
    invoice_number: str
    currency: Literal["GBP", "USD", "EUR", "NGN"]           # an enum in the schema
    due_date: date = Field(json_schema_extra={"description": "ISO 8601 date, YYYY-MM-DD"})
    line_items: list[LineItem]
    total_cents: int

    @model_validator(mode="after")
    def items_add_up(self) -> "Invoice":
        """The invariant no schema can express."""
        total = sum(item.amount_cents for item in self.line_items)
        if total != self.total_cents:
            raise ValueError(f"line items add up to {total} cents but total_cents is {self.total_cents}")
        return self


def json_object_text(text: str) -> str:
    """Models asked for JSON often wrap it in chatter or a fence. Take the outermost {...}."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("no JSON object in the reply")
    return text[start:end + 1]


def describe(error: ValidationError) -> str:
    """Pydantic's errors, as short sentences a model can act on."""
    return "; ".join(f"{'.'.join(map(str, e['loc'])) or 'invoice'}: {e['msg']}" for e in error.errors())


@dataclass
class Reply:
    text: str
    finish_reason: Literal["stop", "length", "other"] = "stop"
    refusal: str | None = None


@dataclass
class Outcome:
    invoice: Invoice | None
    attempts: int
    reason: Literal["ok", "refused", "invalid"]
    detail: str = ""


SYSTEM = ("Extract the invoice as JSON matching this schema. Amounts are integers in cents. "
          "Reply with only the JSON object.\n" + json.dumps(Invoice.model_json_schema()))


def extract_invoice(model: Callable[[list[dict]], Reply], document: str, max_attempts: int = 3) -> Outcome:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": document}]
    problem = ""
    for attempt in range(1, max_attempts + 1):
        reply = model(messages)
        if reply.refusal:  # retrying won't change a refusal: check it before parsing
            return Outcome(None, attempt, "refused", reply.refusal)
        if reply.finish_reason == "length":
            problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object"
        else:
            try:
                # validate the JSON text directly: in strict mode, "2026-10-15" is a valid date in JSON
                # (that's how JSON spells a date) but not as a Python string. Bad JSON is a ValidationError too.
                return Outcome(Invoice.model_validate_json(json_object_text(reply.text)), attempt, "ok")
            except ValidationError as e:
                problem = describe(e)
            except ValueError as e:
                problem = str(e)
        # feed back exactly what was wrong; a bare "try again" tends to repeat the mistake
        messages += [{"role": "assistant", "content": reply.text},
                     {"role": "user", "content": f"Your reply had these problems: {problem}. Return the corrected JSON object only."}]
    return Outcome(None, max_attempts, "invalid", problem)
