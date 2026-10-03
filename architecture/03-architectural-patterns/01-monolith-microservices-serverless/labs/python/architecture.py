"""The arithmetic behind choosing a monolith, microservices or serverless, and a modular-monolith boundary
checker. The same numbers as the TypeScript lab."""
import math
from dataclasses import dataclass, field

MASK = 0xFFFFFFFF


def coordination_links(people: int) -> int:
    return people * (people - 1) // 2


def release_breaks(changes: int, p: float) -> float:
    return 1 - (1 - p) ** changes


def extract(calls_per_request: int, network_ms: float, call_availability: float) -> tuple[float, float]:
    """(added ms, chance every call succeeds) when a module moves behind the network."""
    return calls_per_request * network_ms, call_availability ** calls_per_request


@dataclass(frozen=True)
class Pricing:
    per_million_requests: float
    per_gb_second: float


def serverless_monthly(requests: float, ms: float, memory_gb: float, price: Pricing) -> float:
    return requests / 1e6 * price.per_million_requests + requests * (ms / 1000) * memory_gb * price.per_gb_second


def break_even_requests(server_monthly: float, ms: float, memory_gb: float, price: Pricing) -> float:
    return server_monthly / (price.per_million_requests / 1e6 + (ms / 1000) * memory_gb * price.per_gb_second)


def cold_share(per_minute: float, warm_minutes: float) -> float:
    return math.exp(-per_minute * warm_minutes)


def simulate_cold_share(per_minute: float, warm_minutes: float, requests: int, seed: int) -> float:
    a = seed & MASK

    def random() -> float:  # mulberry32, as in week 1's lab
        nonlocal a
        a = (a + 0x6D2B79F5) & MASK
        t = ((a ^ (a >> 15)) * (a | 1)) & MASK
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & MASK)) & MASK
        return (t ^ (t >> 14)) / 4294967296

    cold = sum(-math.log(1 - random()) / per_minute > warm_minutes for _ in range(requests))
    return cold / requests


@dataclass
class Module:
    name: str
    imports: list[str] = field(default_factory=list)


def boundary_violations(modules: list[Module]) -> list[str]:
    """Imports that reach inside another module instead of going through its public face."""
    names = {m.name for m in modules}
    return [f"{m.name} → {imp}" for m in modules for imp in m.imports
            if (target := imp.split("/")[0]) != m.name and target in names and "/" in imp]


def find_cycle(modules: list[Module]) -> list[str] | None:
    deps = {m.name: [d for d in dict.fromkeys(i.split("/")[0] for i in m.imports) if d != m.name] for m in modules}
    state: dict[str, str] = {}
    path: list[str] = []

    def visit(name: str) -> list[str] | None:
        if state.get(name) == "done":
            return None
        if state.get(name) == "visiting":
            return path[path.index(name):] + [name]  # back to a module on the path
        state[name] = "visiting"
        path.append(name)
        for d in deps.get(name, []):
            if cycle := visit(d):
                return cycle
        path.pop()
        state[name] = "done"
        return None

    for m in modules:
        if cycle := visit(m.name):
            return cycle
    return None
