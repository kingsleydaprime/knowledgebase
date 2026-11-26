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


# ---------- Checkpoint 2: a fresh graph, a fresh tree, a fresh puzzle ----------

CP2_GRAPH = {
    ("S", "A"): 3, ("S", "B"): 2, ("A", "C"): 6, ("A", "D"): 4, ("A", "G"): 10,
    ("B", "C"): 9, ("B", "E"): 1, ("C", "G"): 3, ("D", "E"): 1, ("D", "G"): 7,
}

CP2_TREE = {  # node: children, left to right
    "R": ["P", "Q"], "P": ["T", "U", "V"], "Q": ["W", "X"],
    "U": ["Y", "Z"], "W": ["K"], "X": ["L", "M"],
}


def bfs_graph(roads, start, goal):
    """Graph-search BFS, neighbours alphabetical, goal test when generated (the lessons' convention)."""
    nb = neighbours(roads)
    parent, q = {start: None}, deque([start])
    while q:
        n = q.popleft()
        for m in sorted(nb[n]):
            if m not in parent:
                parent[m] = n
                if m == goal:
                    path = [m]
                    while parent[path[-1]]:
                        path.append(parent[path[-1]])
                    return path[::-1]
                q.append(m)


def dfs_graph(roads, start, goal):
    """Recursive DFS, neighbours alphabetical, a visited node is never visited again."""
    nb = neighbours(roads)
    visited = set()

    def go(path):
        visited.add(path[-1])
        if path[-1] == goal:
            return path
        for m in sorted(nb[path[-1]]):
            if m not in visited:
                found = go(path + [m])
                if found:
                    return found
    return go([start])


def ucs_trace(roads, start, goal):
    """UCS with an explicit frontier dict; ties broken alphabetically; goal test when taken off.
    Returns (order taken off, cost, path, every cost the goal had on the frontier)."""
    nb = neighbours(roads)
    g, parent, done, order, goal_costs = {start: 0}, {start: None}, set(), [], []
    frontier = {start}
    while frontier:
        n = min(frontier, key=lambda x: (g[x], x))
        frontier.remove(n)
        done.add(n)
        order.append(n)
        if n == goal:
            path = [n]
            while parent[path[-1]]:
                path.append(parent[path[-1]])
            return order, g[n], path[::-1], goal_costs
        for m, w in sorted(nb[n].items()):
            if m in done:
                continue
            if m not in g or g[n] + w < g[m]:
                g[m], parent[m] = g[n] + w, n
                frontier.add(m)
                if m == goal:
                    goal_costs.append(g[m])


def tree_bfs(tree, root):
    order, q = [], deque([root])
    while q:
        n = q.popleft()
        order.append(n)
        q.extend(tree.get(n, []))
    return order


def tree_dls(tree, node, limit, goal=None, order=None):
    """Depth-first visit order down to `limit`; stops at `goal`. Returns (order, found, cutoff)."""
    order = [] if order is None else order
    order.append(node)
    if node == goal:
        return order, True, False
    if limit == 0:
        return order, False, bool(tree.get(node))
    cut = False
    for c in tree.get(node, []):
        _, found, c_cut = tree_dls(tree, c, limit - 1, goal, order)
        if found:
            return order, True, False
        cut = cut or c_cut
    return order, False, cut


def soldiers_bfs():
    """3 soldiers and 2 boys; the boat carries 1 soldier, or 1 or 2 boys. Everyone must cross."""
    start, goal = (3, 2, 0), (0, 0, 1)   # (soldiers on start bank, boys on start bank, boat side)
    loads = [(1, 0), (0, 1), (0, 2)]
    par, q = {start: None}, deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            path = []
            while s is not None:
                path.append(s)
                s = par[s]
            return path[::-1]
        sold, boys, side = s
        for ds, db in loads:
            if side == 0 and ds <= sold and db <= boys:
                t = (sold - ds, boys - db, 1)
            elif side == 1 and ds <= 3 - sold and db <= 2 - boys:
                t = (sold + ds, boys + db, 0)
            else:
                continue
            if t not in par:
                par[t] = s
                q.append(t)


def check_checkpoint_2():
    # Section 01 refreshers
    assert 6 ** 3 == 216
    # Q: nodes below the root, b = 3, d = 5
    assert sum(3 ** k for k in range(1, 6)) == 363
    # IDS versus BFS, b = 3, d = 4
    ids = sum((4 - k + 1) * 3 ** k for k in range(1, 5))
    bfs = sum(3 ** k for k in range(1, 5))
    assert (ids, bfs) == (174, 120)
    # bidirectional, b = 10, d = 8
    assert sum(10 ** k for k in range(1, 9)) == 111_111_110
    assert 2 * sum(10 ** k for k in range(1, 5)) == 22_220

    # The tree
    assert tree_bfs(CP2_TREE, "R") == list("RPQTUVWXYZKLM")
    dfs_order, _, _ = tree_dls(CP2_TREE, "R", 99)
    assert dfs_order == list("RPTUYZVQWKXLM")
    dls2, found, cut = tree_dls(CP2_TREE, "R", 2)
    assert dls2 == list("RPTUVQWX") and not found and cut
    _, found_m, cut_m = tree_dls(CP2_TREE, "R", 2, goal="M")
    assert not found_m and cut_m                      # M at depth 3: cutoff
    _, found_n, cut_n = tree_dls(CP2_TREE, "R", 5, goal="N")
    assert not found_n and not cut_n                  # N not in the tree: standard failure
    visits = []
    for limit in range(0, 10):
        order, found, _ = tree_dls(CP2_TREE, "R", limit, goal="L")
        visits.append(len(order))
        if found:
            break
    assert visits == [1, 3, 8, 12] and sum(visits) == 24, visits

    # The graph
    assert bfs_graph(CP2_GRAPH, "S", "G") == ["S", "A", "G"]
    assert path_cost(CP2_GRAPH, ["S", "A", "G"]) == 13
    d = dfs_graph(CP2_GRAPH, "S", "G")
    assert d == ["S", "A", "C", "B", "E", "D", "G"] and path_cost(CP2_GRAPH, d) == 27
    order, cost, path, goal_costs = ucs_trace(CP2_GRAPH, "S", "G")
    assert order == list("SBAEDCG"), order
    assert (cost, path) == (11, ["S", "B", "E", "D", "G"])
    assert goal_costs == [13, 11], goal_costs         # G first joins the frontier at 13
    assert dijkstra(CP2_GRAPH, "S", "G")[0] == 11
    # the cheapest 3-road-or-fewer routes all cost more than 11
    short = [path_cost(CP2_GRAPH, p) for p in all_simple_paths(CP2_GRAPH, "S", "G") if len(p) - 1 <= 3]
    assert min(short) == 12

    # Soldiers and boys
    sol = soldiers_bfs()
    assert len(sol) - 1 == 13, len(sol) - 1
    print("checkpoint 2: all numbers check")


if __name__ == "__main__":
    check_checkpoint_1()
    check_checkpoint_2()
