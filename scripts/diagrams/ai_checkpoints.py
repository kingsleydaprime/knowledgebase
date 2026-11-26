"""Solve the AI checkpoint exams (artificial-intelligence/checkpoint-*.md).

    python3 scripts/diagrams/ai_checkpoints.py      # run from the vault root

Every number in the checkpoints' questions and worked answers is computed here and
asserted, so a typo in a paper fails this script. The maps and puzzles are fresh
ones made for the checkpoints, not the lessons' own examples.
"""
import heapq
import itertools
import math
from collections import deque


# ---------- Checkpoint 1, Question 9: the Enugu to Port Harcourt map ----------
# Made-up road distances in km, chosen for hand tracing.

SE_ROADS = {
    ("Enugu", "Awka"): 60, ("Enugu", "Okigwe"): 80, ("Awka", "Onitsha"): 45,
    ("Awka", "Owerri"): 110, ("Okigwe", "Owerri"): 55, ("Okigwe", "Aba"): 120,
    ("Onitsha", "Owerri"): 100, ("Owerri", "Port Harcourt"): 95,
    ("Owerri", "Aba"): 30, ("Aba", "Port Harcourt"): 60,
}


def neighbours(roads):
    nb = {}
    for (a, b), d in roads.items():
        nb.setdefault(a, {})[b] = d
        nb.setdefault(b, {})[a] = d
    return nb


def path_cost(roads, path):
    nb = neighbours(roads)
    return sum(nb[a][b] for a, b in zip(path, path[1:]))


def all_simple_paths(roads, start, goal):
    nb = neighbours(roads)
    out = []

    def go(path):
        if path[-1] == goal:
            out.append(path)
            return
        for n in sorted(nb[path[-1]]):
            if n not in path:
                go(path + [n])
    go([start])
    return out


def dijkstra(roads, start, goal):
    nb = neighbours(roads)
    heap, seen = [(0, [start])], set()
    while heap:
        d, path = heapq.heappop(heap)
        if path[-1] == goal:
            return d, path
        if path[-1] in seen:
            continue
        seen.add(path[-1])
        for n, w in nb[path[-1]].items():
            if n not in seen:
                heapq.heappush(heap, (d + w, path + [n]))


# ---------- Checkpoint 1, Question 8: the water jugs ----------

def jug_moves(s, cap=(4, 3)):
    a, b = s
    A, B = cap
    pour_ab = min(a, B - b)
    pour_ba = min(b, A - a)
    return {
        "fill the 4-litre jug": (A, b), "fill the 3-litre jug": (a, B),
        "empty the 4-litre jug": (0, b), "empty the 3-litre jug": (a, 0),
        "pour the 4-litre jug into the 3-litre jug": (a - pour_ab, b + pour_ab),
        "pour the 3-litre jug into the 4-litre jug": (a + pour_ba, b - pour_ba),
    }


def jug_bfs(start=(0, 0), goal_a=2):
    q, par = deque([start]), {start: None}
    while q:
        s = q.popleft()
        if s[0] == goal_a:
            path = []
            while s is not None:
                path.append(s)
                s = par[s][0] if par[s] else None
            return path[::-1]
        for _, t in jug_moves(s).items():
            if t not in par:
                par[t] = (s,)
                q.append(t)


def check_checkpoint_1():
    # Q9: path costs on the south-east map
    given = ["Enugu", "Awka", "Owerri", "Port Harcourt"]
    assert path_cost(SE_ROADS, given) == 265
    paths = all_simple_paths(SE_ROADS, "Enugu", "Port Harcourt")
    costs = {tuple(p): path_cost(SE_ROADS, p) for p in paths}
    best = min(costs.values())
    best_paths = [p for p, c in costs.items() if c == best]
    assert best == 225 and best_paths == [("Enugu", "Okigwe", "Owerri", "Aba", "Port Harcourt")]
    assert dijkstra(SE_ROADS, "Enugu", "Port Harcourt") == (225, list(best_paths[0]))
    fewest = min(len(p) for p in paths) - 1
    assert fewest == 3
    three_road = sorted(c for p, c in costs.items() if len(p) - 1 == 3)
    assert three_road == [230, 260, 265], three_road  # the cheapest 3-road route costs 230 > 225
    # the four options offered in the multiple-choice part
    options = {
        ("Enugu", "Okigwe", "Owerri", "Port Harcourt"): 230,
        ("Enugu", "Okigwe", "Aba", "Port Harcourt"): 260,
        ("Enugu", "Okigwe", "Owerri", "Aba", "Port Harcourt"): 225,
        ("Enugu", "Awka", "Onitsha", "Owerri", "Port Harcourt"): 300,
    }
    for p, c in options.items():
        assert costs[p] == c, (p, costs[p])

    # Q8: water jugs, shortest solution is 6 actions
    sol = jug_bfs()
    assert len(sol) - 1 == 6  # shortest solution
    # both 6-action sequences printed in the worked answer are legal and reach 2 litres
    for seq in ([(0, 0), (0, 3), (3, 0), (3, 3), (4, 2), (0, 2), (2, 0)],
                [(0, 0), (4, 0), (1, 3), (1, 0), (0, 1), (4, 1), (2, 3)]):
        assert all(t in jug_moves(s).values() for s, t in zip(seq, seq[1:])), seq
        assert seq[-1][0] == 2

    # Q11: counting combinations
    assert 4 ** 5 == 1024
    # Q12: game tree, b = 4, 8 moves ahead, 1,000 positions a second
    assert 4 ** 8 == 65_536 and 4 ** 8 / 1000 == 65.536
    assert 3 ** 8 == 6_561
    assert round(4 ** 8 / 3 ** 8, 2) == 9.99 and round(4 ** 8 / 3 ** 8, 5) == 9.98872
    # Q13: a computer 1,024 times faster for one hour
    assert 2 ** 30 * 1024 == 2 ** 40          # exponential: n goes from 30 to 40
    assert math.isqrt(1000 ** 2 * 1024) == 32_000 and 32_000 ** 2 == 1000 ** 2 * 1024  # quadratic: 1,000 -> 32,000
    print("checkpoint 1: all numbers check")


if __name__ == "__main__":
    check_checkpoint_1()
