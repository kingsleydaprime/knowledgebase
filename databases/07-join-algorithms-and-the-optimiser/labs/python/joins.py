"""The three join algorithms, written out, each counting its work; and the arithmetic of two classic estimation
failures. Rows are (key, value) pairs; every join returns (outer value, inner value) pairs for matching keys."""
from collections import defaultdict


def nested_loop(outer: list, inner: list) -> tuple[list, int]:
    """For every outer row, look at every inner row: N × M comparisons."""
    out, comparisons = [], 0
    for ok, ov in outer:
        for ik, iv in inner:
            comparisons += 1
            if ok == ik:
                out.append((ov, iv))
    return out, comparisons


def index_nested_loop(outer: list, inner_sorted: list) -> tuple[list, int]:
    """The inner side has an index (here, a sorted list searched by bisection): about N × log₂ M steps."""
    keys = [k for k, _ in inner_sorted]
    out, steps = [], 0
    for ok, ov in outer:
        lo, hi = 0, len(keys)
        while lo < hi:  # find the first inner key >= ok
            steps += 1
            mid = (lo + hi) // 2
            if keys[mid] < ok:
                lo = mid + 1
            else:
                hi = mid
        while lo < len(keys) and keys[lo] == ok:
            out.append((ov, inner_sorted[lo][1]))
            lo += 1
    return out, steps


def hash_join(outer: list, inner: list) -> tuple[list, int]:
    """Build a hash table on the inner (smaller) side, then probe it once per outer row: N + M operations.
    Equality only: a hash table can't answer 'less than'."""
    table = defaultdict(list)
    for ik, iv in inner:  # build
        table[ik].append(iv)
    out = []
    for ok, ov in outer:  # probe
        out.extend((ov, iv) for iv in table.get(ok, []))
    return out, len(inner) + len(outer)


def merge_join(outer_sorted: list, inner_sorted: list) -> tuple[list, int]:
    """Both sides sorted by key: walk them together like merging two sorted lists, about N + M steps."""
    out, steps, i, j = [], 0, 0, 0
    while i < len(outer_sorted) and j < len(inner_sorted):
        steps += 1
        ok, ik = outer_sorted[i][0], inner_sorted[j][0]
        if ok < ik:
            i += 1
        elif ok > ik:
            j += 1
        else:
            j_end = j
            while j_end < len(inner_sorted) and inner_sorted[j_end][0] == ok:  # every inner row with this key
                out.append((outer_sorted[i][1], inner_sorted[j_end][1]))
                j_end += 1
            i += 1  # the next outer row may have the same key, so j stays where the group starts
    return out, steps


def independent_estimate(rows: int, *selectivities: float) -> float:
    """What a planner assumes for `a AND b` without extended statistics: the selectivities multiply."""
    estimate = rows
    for s in selectivities:
        estimate *= s
    return estimate


def rows_read_for_page(offset: int, limit: int, keyset: bool) -> int:
    """OFFSET reads and discards every skipped row; keyset pagination (WHERE id > last_seen) starts at the right place."""
    return limit if keyset else offset + limit
