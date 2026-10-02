"""practices.py — a token bucket with an injected clock, and stdlib logging that writes
redacted JSON lines with a request ID taken from a context variable."""
import json
import logging
import math
import re
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")


class TokenBucket:
    def __init__(self, capacity: float, per_second: float, clock):
        self.capacity, self.per_second, self.clock = capacity, per_second, clock
        self.buckets: dict[str, tuple[float, float]] = {}

    def take(self, key: str) -> tuple[bool, int]:
        """Returns (allowed, retry_after_seconds)."""
        now = self.clock()
        tokens, at = self.buckets.get(key, (self.capacity, now))
        tokens = min(self.capacity, tokens + (now - at) * self.per_second)
        if tokens >= 1:
            self.buckets[key] = (tokens - 1, now)
            return True, 0
        self.buckets[key] = (tokens, now)
        return False, math.ceil((1 - tokens) / self.per_second)


SECRET = re.compile(r"token|password|secret|authorization|card", re.I)


class JsonFormatter(logging.Formatter):
    """One JSON object per line. Extra fields come from `logger.info(msg, extra={...})`."""

    def format(self, record: logging.LogRecord) -> str:
        fields = getattr(record, "fields", {})
        entry = {"level": record.levelname, "msg": record.getMessage(), "requestId": request_id.get()}
        entry.update({k: "[redacted]" if SECRET.search(k) else v for k, v in fields.items()})
        return json.dumps(entry)


def make_logger(stream) -> logging.Logger:
    logger = logging.getLogger("shop")
    logger.handlers.clear()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
