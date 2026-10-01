"""audit.py — constructor injection, a composition root, and the scope bug in Python."""
import asyncio
from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass
class AuditLog:
    entries: list[str] = field(default_factory=list)


class AuditServiceWithUserField:
    """BUG: built once at startup, but stores per-request data on itself."""

    def __init__(self, log: AuditLog):
        self.log = log
        self.current_user = "nobody"

    async def record(self, action: str) -> None:
        await asyncio.sleep(0.005)  # any await lets another request run in between
        self.log.entries.append(f"{self.current_user}: {action}")


class AuditService:
    """FIX 1: request data is an argument."""

    def __init__(self, log: AuditLog):
        self.log = log

    async def record(self, user: str, action: str) -> None:
        await asyncio.sleep(0.005)
        self.log.entries.append(f"{user}: {action}")


# FIX 2: a context variable — each asyncio task sees its own value (Python's AsyncLocalStorage).
current_user: ContextVar[str] = ContextVar("current_user", default="nobody")


class ContextAuditService:
    def __init__(self, log: AuditLog):
        self.log = log

    async def record(self, action: str) -> None:
        await asyncio.sleep(0.005)
        self.log.entries.append(f"{current_user.get()}: {action}")


def compose():
    """The composition root: the only place that knows the concrete classes."""
    log = AuditLog()
    return log, AuditServiceWithUserField(log), AuditService(log), ContextAuditService(log)
