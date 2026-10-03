"""Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps.
The same numbers as the TypeScript lab."""
from dataclasses import dataclass

SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class Assumptions:
    daily_active_users: int
    writes_per_user_per_day: float
    reads_per_user_per_day: float
    peak_to_average: float
    bytes_per_write: int
    kept_for_days: int
    bytes_per_read: int


def estimate(a: Assumptions) -> dict:
    writes = a.daily_active_users * a.writes_per_user_per_day / SECONDS_PER_DAY
    reads = a.daily_active_users * a.reads_per_user_per_day / SECONDS_PER_DAY
    return {
        "writes_per_second": {"average": writes, "peak": writes * a.peak_to_average},
        "reads_per_second": {"average": reads, "peak": reads * a.peak_to_average},
        "reads_per_write": a.reads_per_user_per_day / a.writes_per_user_per_day,
        "storage_bytes": a.daily_active_users * a.writes_per_user_per_day * a.bytes_per_write * a.kept_for_days,
        "peak_egress_bytes_per_second": reads * a.peak_to_average * a.bytes_per_read,
    }


def human_bytes(n: float) -> str:
    """Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB"."""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while n >= 1000 and i < len(units) - 1:
        n /= 1000
        i += 1
    # f"{910.0:.2g}" is "9.1e+02": round to two figures first, then print without an exponent.
    return f"{float(f'{n:.2g}'):g} {units[i]}"


class Leaderboard:
    """Each player's best score, and a Fenwick tree of how many players have each score."""

    def __init__(self, max_score: int):
        self.max_score = max_score
        self._best: dict[str, int] = {}
        self._tree = [0] * (max_score + 2)
        self.steps = 0

    @property
    def players(self) -> int:
        return len(self._best)

    def submit(self, player: str, score: int) -> bool:
        # bool is a subclass of int in Python, so True would otherwise pass as a score of 1.
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= self.max_score:
            raise ValueError(f"score must be a whole number from 0 to {self.max_score}, got {score!r}")
        old = self._best.get(player)
        if old is not None and score <= old:
            return False
        if old is not None:
            self._add(old, -1)
        self._add(score, +1)
        self._best[player] = score
        return True

    def rank(self, player: str) -> int | None:
        score = self._best.get(player)
        if score is None:
            return None
        self.steps = 0
        return 1 + self.players - self._count_at_most(score)

    def _add(self, score: int, delta: int) -> None:
        i = score + 1
        while i < len(self._tree):
            self._tree[i] += delta
            i += i & -i

    def _count_at_most(self, score: int) -> int:
        count, i = 0, score + 1
        while i > 0:
            count += self._tree[i]
            self.steps += 1
            i -= i & -i
        return count


def rank_by_scan(scores, mine: int) -> tuple[int, int]:
    higher = steps = 0
    for s in scores:
        steps += 1
        if s > mine:
            higher += 1
    return 1 + higher, steps
