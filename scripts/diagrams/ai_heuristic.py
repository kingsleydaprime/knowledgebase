"""Draw the heuristic-search diagrams (artificial-intelligence/03-heuristic-search) and assert every number.

    python3 scripts/diagrams/ai_heuristic.py      # run from the vault root

Implements generate-and-test, greedy best-first search, A*, beam search, hill climbing,
simulated annealing's acceptance rule and one generation of a genetic algorithm, and runs
each on the lessons' own examples: the Lagos-to-Abuja map with straight-line distances to
Abuja as the heuristic, the small A* graph from the SSG 518 search slides, an 8-puzzle,
a one-dimensional hill landscape, and the classic "maximise x squared" genetic algorithm.
Conventions (stated in the lessons): ties are broken alphabetically; best-first methods
test for the goal when a node is taken off the frontier. Output: artificial-intelligence/images/hs-*.svg.
"""
import heapq
import itertools
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, ACCENT, FONT, Svg  # noqa: E402
from artificial_intelligence import ROADS, POS, OUT, ORANGE, NODE_FILL, START_FILL, GOAL_FILL, save_neato, cost  # noqa: E402
from ai_search import graph_from, MAP, ucs  # noqa: E402

GREY = '#9ca3af'

# Straight-line distances to Abuja, km, rounded. Chosen to be close to the real
# geography while staying admissible and consistent for the lesson map.
H = {'Lagos': 525, 'Ibadan': 450, 'Benin': 370, 'Akure': 360, 'Ilorin': 300, 'Lokoja': 165, 'Abuja': 0}

# The A* example from the SSG 518 Introduction to Search slides.
SLIDE_G = graph_from({('S', 'A'): 1, ('S', 'B'): 4, ('A', 'C'): 2, ('B', 'C'): 1, ('C', 'G'): 3, ('B', 'G'): 6})
SLIDE_H = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'G': 0}


# ---------- best-first family ----------

def best_first(g, h, start, goal, mode):
    """mode 'greedy' (f = h), 'astar' (f = g + h) or 'ucs' (f = g). Goal test on removal.
    Returns path, cost, list of expanded nodes, and a trace of (popped, f, frontier)."""
    def f(gc, n):
        return h[n] if mode == 'greedy' else gc + h[n] if mode == 'astar' else gc
    best, parent, done, expanded, trace = {start: 0}, {start: None}, set(), [], []
    heap = [(f(0, start), start)]
    while heap:
        fv, node = heapq.heappop(heap)
        if node in done or fv > f(best[node], node):
            continue
        done.add(node)
        expanded.append(node)
        if node == goal:
            path = []
            n = node
            while n:
                path.append(n)
                n = parent[n]
            return path[::-1], best[node], expanded, trace
        for child, d in g[node].items():
            nc = best[node] + d
            if child in done:
                continue
            if child not in best or nc < best[child]:
                if mode == 'greedy' and child in best:
                    continue  # greedy keeps the first path it found to a node
                best[child], parent[child] = nc, node
                heapq.heappush(heap, (f(nc, child), child))
        front = sorted((f(best[n], n), n) for n in best if n not in done)
        trace.append((node, fv, front))
    return None, None, expanded, trace


def true_cost_to(goal):
    return {n: ucs(MAP, n, goal)[1] for n in MAP}


def beam(g, h, start, goal, k):
    """Beam search: breadth-first by levels, keeping only the k best (lowest h) new states per level."""
    level, parent, seen, levels = [start], {start: None}, {start}, [[start]]
    while level:
        cand = []
        for node in level:
            for child in g[node]:
                if child not in seen and child not in [c for c, _ in cand]:
                    cand.append((child, node))
        cand.sort(key=lambda cp: (h[cp[0]], cp[0]))
        keep = cand[:k]
        for child, par in keep:
            parent[child] = par
            seen.add(child)
        level = [c for c, _ in keep]
        levels.append(level)
        if goal in level:
            path, n = [], goal
            while n:
                path.append(n)
                n = parent[n]
            return path[::-1], levels
    return None, levels


# ---------- 8-puzzle ----------

GOAL8 = (1, 2, 3, 4, 5, 6, 7, 8, 0)
START8 = (1, 2, 3, 0, 4, 6, 7, 5, 8)   # small example for the heuristic calculation
DEEP8 = (1, 3, 6, 5, 0, 7, 4, 8, 2)    # 12 moves from the goal, for counting expansions


def misplaced(s):
    return sum(1 for i, t in enumerate(s) if t and t != GOAL8[i])


def manhattan(s):
    tot = 0
    for i, t in enumerate(s):
        if t:
            j = GOAL8.index(t)
            tot += abs(i // 3 - j // 3) + abs(i % 3 - j % 3)
    return tot


def moves(s):
    i = s.index(0)
    r, c = divmod(i, 3)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < 3 and 0 <= cc < 3:
            j = rr * 3 + cc
            t = list(s)
            t[i], t[j] = t[j], t[i]
            yield tuple(t)


def astar8(start, h):
    counter = itertools.count()
    g = {start: 0}
    heap = [(h(start), next(counter), start)]
    done = set()
    expanded = 0
    while heap:
        f, _, s = heapq.heappop(heap)
        if s in done:
            continue
        done.add(s)
        if s == GOAL8:
            return g[s], expanded
        expanded += 1
        for t in moves(s):
            ng = g[s] + 1
            if t not in g or ng < g[t]:
                g[t] = ng
                heapq.heappush(heap, (ng + h(t), next(counter), t))
    return None, expanded


# ---------- local search ----------

LAND = [2, 4, 6, 5, 4, 4, 4, 7, 9, 11, 10, 8, 6]   # value at x = 0..12


def hill_climb(x):
    path = [x]
    while True:
        nb = [n for n in (x - 1, x + 1) if 0 <= n < len(LAND)]
        best = max(nb, key=lambda n: (LAND[n], -n))
        if LAND[best] <= LAND[x]:
            return path
        x = best
        path.append(x)


def accept_prob(delta, t):
    return 1.0 if delta > 0 else math.exp(delta / t)


def ga_generation():
    pop = ['01101', '11000', '01000', '10011']
    fit = [int(s, 2) ** 2 for s in pop]
    total = sum(fit)
    probs = [f / total for f in fit]
    kids = ['0110' + '0', '1100' + '1', '11' + '011', '10' + '000']   # crossover 1|2 at 4, 2|4 at 2
    kfit = [int(s, 2) ** 2 for s in kids]
    return pop, fit, total, probs, kids, kfit


# ---------- assertions ----------

def check():
    # Lesson 01: h is admissible and consistent on the map.
    real = true_cost_to('Abuja')
    assert real == {'Lagos': 790, 'Ibadan': 660, 'Benin': 500, 'Akure': 450, 'Ilorin': 520, 'Lokoja': 200, 'Abuja': 0}
    assert all(H[n] <= real[n] for n in MAP)
    assert all(H[a] <= d + H[b] for a in MAP for b, d in MAP[a].items())
    # Lesson 02: generate-and-test finds 37 on the 28th test.
    tests = 0
    for n in range(10, 100):
        tests += 1
        a, b = divmod(n, 10)
        if a + b == 10 and a * b == 21:
            break
    assert n == 37 and tests == 28
    assert [n for n in range(10, 100) if sum(divmod(n, 10)) == 10 and math.prod(divmod(n, 10)) == 21] == [37, 73]
    # Lesson 03: greedy on the map and on the slides graph.
    p, c, exp, tr = best_first(MAP, H, 'Lagos', 'Abuja', 'greedy')
    assert p == ['Lagos', 'Benin', 'Lokoja', 'Abuja'] and c == 830 and exp == ['Lagos', 'Benin', 'Lokoja', 'Abuja']
    assert tr[0][2] == [(370, 'Benin'), (450, 'Ibadan')]
    assert tr[1][2] == [(165, 'Lokoja'), (360, 'Akure'), (450, 'Ibadan')]
    p, c, exp, _ = best_first(SLIDE_G, SLIDE_H, 'S', 'G', 'greedy')
    assert p == ['S', 'B', 'G'] and c == 10 and exp == ['S', 'B', 'G']
    qg = graph_from({('S', 'X'): 2, ('S', 'Y'): 9, ('X', 'G'): 4, ('Y', 'G'): 2})
    qh = {'S': 6, 'X': 4, 'Y': 1, 'G': 0}
    assert best_first(qg, qh, 'S', 'G', 'greedy')[1] == 11 and best_first(qg, qh, 'S', 'G', 'astar')[1] == 6
    # Lesson 02 quiz: digits sum 6, product 8 -> 24 on the 15th test.
    assert next(n for n in range(10, 100) if sum(divmod(n, 10)) == 6 and math.prod(divmod(n, 10)) == 8) == 24 and 24 - 10 + 1 == 15
    # Lesson 04: A* and UCS on the slides graph.
    p, c, exp, tr = best_first(SLIDE_G, SLIDE_H, 'S', 'G', 'astar')
    assert p == ['S', 'A', 'C', 'G'] and c == 6 and exp == ['S', 'A', 'C', 'G']
    assert tr[0][2] == [(5, 'A'), (7, 'B')]
    assert tr[1][2] == [(5, 'C'), (7, 'B')]
    assert tr[2][2] == [(6, 'G'), (7, 'B')]
    p, c, exp, _ = best_first(SLIDE_G, SLIDE_H, 'S', 'G', 'ucs')
    assert p == ['S', 'A', 'C', 'G'] and c == 6 and exp == ['S', 'A', 'C', 'B', 'G']
    assert all(SLIDE_H[a] <= d + SLIDE_H[b] for a in SLIDE_G for b, d in SLIDE_G[a].items())
    # Lesson 05: A* on the map.
    p, c, exp, tr = best_first(MAP, H, 'Lagos', 'Abuja', 'astar')
    assert p == ['Lagos', 'Ibadan', 'Akure', 'Lokoja', 'Abuja'] and c == 790
    assert exp == ['Lagos', 'Ibadan', 'Ilorin', 'Akure', 'Benin', 'Lokoja', 'Abuja']
    assert tr[0][2] == [(580, 'Ibadan'), (700, 'Benin')]
    assert tr[1][2] == [(590, 'Ilorin'), (700, 'Akure'), (700, 'Benin')]
    assert tr[2][2] == [(700, 'Akure'), (700, 'Benin'), (810, 'Abuja')]
    assert tr[3][2] == [(700, 'Benin'), (755, 'Lokoja'), (810, 'Abuja')]
    assert tr[4][2] == [(755, 'Lokoja'), (810, 'Abuja')]
    assert tr[5][2] == [(790, 'Abuja')]
    # An inadmissible heuristic misleads A*: Akure overestimated at 700 (true 450).
    bad = dict(H, Akure=700)
    p, c, _, _ = best_first(MAP, bad, 'Lagos', 'Abuja', 'astar')
    assert c == 810 and p == ['Lagos', 'Ibadan', 'Ilorin', 'Abuja']
    _, _, exp, tr = best_first(MAP, bad, 'Lagos', 'Abuja', 'astar')
    assert exp == ['Lagos', 'Ibadan', 'Ilorin', 'Benin', 'Lokoja', 'Abuja']
    assert tr[2][2] == [(700, 'Benin'), (810, 'Abuja'), (1040, 'Akure')] and (795, 'Lokoja') in tr[3][2]
    # Lesson 06: 8-puzzle heuristics.
    assert misplaced(START8) == 3 and manhattan(START8) == 3
    assert misplaced(DEEP8) == 6 and manhattan(DEEP8) == 10
    d0, e0 = astar8(DEEP8, lambda s: 0)
    d1, e1 = astar8(DEEP8, misplaced)
    d2, e2 = astar8(DEEP8, manhattan)
    assert d0 == d1 == d2 == 12 and (e0, e1, e2) == (2327, 119, 36)
    assert all(manhattan(t) >= misplaced(t) for t in [START8, DEEP8, GOAL8])
    q1 = (2, 1, 3, 4, 5, 6, 8, 7, 0)
    assert misplaced(q1) == 4 and manhattan(q1) == 4
    assert manhattan((0, 2, 3, 4, 5, 6, 7, 8, 1)) == 4 and misplaced((0, 2, 3, 4, 5, 6, 7, 8, 1)) == 1
    return d0, e0, e1, e2


def check_local():
    # Lesson 07: hill climbing.
    assert hill_climb(0) == [0, 1, 2]
    assert hill_climb(7) == [7, 8, 9]
    assert hill_climb(5) == [5]
    assert max(LAND) == 11 and LAND.index(11) == 9
    # Lesson 08: beam search on the map.
    p, levels = beam(MAP, H, 'Lagos', 'Abuja', 2)
    assert levels == [['Lagos'], ['Benin', 'Ibadan'], ['Lokoja', 'Ilorin'], ['Abuja', 'Akure']] and p == ['Lagos', 'Benin', 'Lokoja', 'Abuja']
    p1, levels1 = beam(MAP, H, 'Lagos', 'Abuja', 1)
    assert levels1 == [['Lagos'], ['Benin'], ['Lokoja'], ['Abuja']]
    # Lesson 09: simulated annealing acceptance.
    assert round(accept_prob(-1, 10), 3) == 0.905
    assert round(accept_prob(-1, 1), 3) == 0.368
    assert round(accept_prob(-1, 0.1), 6) == 0.000045
    assert round(accept_prob(-3, 10), 3) == 0.741 and round(accept_prob(-3, 1), 3) == 0.050
    # Lesson 10: genetic algorithm generation.
    pop, fit, total, probs, kids, kfit = ga_generation()
    assert fit == [169, 576, 64, 361] and total == 1170
    assert [round(p, 3) for p in probs] == [0.144, 0.492, 0.055, 0.309]
    assert kids == ['01100', '11001', '11011', '10000'] and kfit == [144, 625, 729, 256]
    assert sum(kfit) == 1754 and max(kfit) == 729
    # Section 03 quiz numbers.
    land_q = [1, 3, 5, 8, 6, 9, 2]
    x = 0
    while True:
        nb = [n for n in (x - 1, x + 1) if 0 <= n < len(land_q)]
        b = max(nb, key=lambda n: land_q[n])
        if land_q[b] <= land_q[x]:
            break
        x = b
    assert x == 3                                                    # hill-climbing quiz
    assert round(accept_prob(-2, 4), 2) == 0.61 and round(accept_prob(-2, 1), 2) == 0.14   # annealing quiz
    assert 20 / (10 + 20 + 30 + 40) == 0.2                           # roulette quiz
    assert '10110'[:2] + '01001'[2:] == '10001' and '01001'[:2] + '10110'[2:] == '01110'   # crossover quiz
    assert int('11001', 2) ** 2 == 625


# ---------- drawing ----------

def map_with_h(name, title, highlight=None):
    hl = {frozenset(e) for e in zip(highlight or [], (highlight or [])[1:])}
    lines = ['graph { bgcolor="white"; pad=0.3; splines=line;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, margin="0.12,0.06"];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="#374151", penwidth=1.4];']
    for city, (x, y) in POS.items():
        fill = START_FILL if city == 'Lagos' else GOAL_FILL if city == 'Abuja' else NODE_FILL
        lines.append(f'"{city}" [pos="{x * 72:.0f},{y * 72:.0f}!", fillcolor="{fill}", label="{city}\\nh = {H[city]}"];')
    for (a, b), d in ROADS.items():
        st = f', color="{ORANGE}", penwidth=3.5' if frozenset((a, b)) in hl else ''
        lines.append(f'"{a}" -- "{b}" [label=" {d}"{st}];')
    lines.append('}')
    save_neato('\n'.join(lines), name, title)


def slide_graph(name, title, highlight=None):
    pos = {'S': (0, 1.2), 'A': (1.4, 2.2), 'B': (1.4, 0.2), 'C': (2.8, 1.6), 'G': (4.2, 0.8)}
    hl = {frozenset(e) for e in zip(highlight or [], (highlight or [])[1:])}
    lines = ['graph { bgcolor="white"; pad=0.3; splines=line;',
             f'node [fontname="{FONT}", fontsize=13, shape=circle, style=filled, color="{INK}", penwidth=1.2, width=0.75, fixedsize=true];',
             f'edge [fontname="{FONT}", fontsize=13, color="{INK}", fontcolor="#374151", penwidth=1.4];']
    for n, (x, y) in pos.items():
        fill = START_FILL if n == 'S' else GOAL_FILL if n == 'G' else NODE_FILL
        lines.append(f'"{n}" [pos="{x * 80:.0f},{y * 80:.0f}!", fillcolor="{fill}", label="{n}\\nh={SLIDE_H[n]}"];')
    seen = set()
    for a, nb in SLIDE_G.items():
        for b, d in nb.items():
            e = frozenset((a, b))
            if e in seen:
                continue
            seen.add(e)
            st = f', color="{ORANGE}", penwidth=3.5' if e in hl else ''
            lines.append(f'"{a}" -- "{b}" [label="  {d}  "{st}];')
    lines.append('}')
    save_neato('\n'.join(lines), name, title)


def puzzle(name, title, state, labels=None):
    s = Svg(560, 230, title)
    for k, (st, cap) in enumerate([(state, labels[0] if labels else 'Start'), (GOAL8, labels[1] if labels else 'Goal')]):
        x0 = 40 + k * 280
        s.text(x0 + 90, 26, cap, size=14, weight='bold')
        for i, t in enumerate(st):
            r, c = divmod(i, 3)
            x, y = x0 + c * 60, 40 + r * 60
            wrong = k == 0 and t and t != GOAL8[i]
            fill = '#ffffff' if t == 0 else ('#fde68a' if wrong else NODE_FILL)
            s.rect(x, y, 56, 56, fill, stroke=INK, width=1.2)
            if t:
                s.text(x + 28, y + 36, t, size=22, weight='bold')
    s.save(name, OUT)


def landscape(name, title, marks=None):
    w, h = 640, 300
    s = Svg(w, h, title)
    x0, y0, dx, dy = 50, 250, 45, 18
    s.line(x0 - 10, y0, x0 + 12 * dx + 20, y0)
    pts = [(x0 + i * dx, y0 - v * dy) for i, v in enumerate(LAND)]
    s.path('M ' + ' L '.join(f'{x:.0f} {y:.0f}' for x, y in pts), ACCENT, width=3)
    for i, (x, y) in enumerate(pts):
        s.circle(x, y, 5, ACCENT)
        s.text(x, y - 10, LAND[i], size=12)
        s.text(x, y0 + 18, i, size=12, color='#374151')
    s.text(x0 + 6 * dx, y0 + 40, 'state x (neighbours are x − 1 and x + 1); height = value to maximise', size=12, color='#374151')
    for i, text in (marks or []):
        x, y = pts[i]
        s.text(x, y - 28, text, size=12, color='#b45309', weight='bold')
    s.save(name, OUT)


if __name__ == '__main__':
    d0, e0, e1, e2 = check()
    print(f'8-puzzle deep example: depth {d0}; expanded UCS {e0}, misplaced {e1}, manhattan {e2}')
    check_local()
    map_with_h('hs-map-h.svg', 'The road map with each city labelled by its straight-line distance to Abuja: Lagos 525, Ibadan 450, '
               'Benin 370, Akure 360, Ilorin 300, Lokoja 165, Abuja 0')
    map_with_h('hs-greedy-route.svg', 'Greedy best-first search follows the smallest h: Lagos to Benin to Lokoja to Abuja, 830 km, highlighted',
               highlight=['Lagos', 'Benin', 'Lokoja', 'Abuja'])
    map_with_h('hs-astar-route.svg', 'A star returns Lagos to Ibadan to Akure to Lokoja to Abuja, 790 km, highlighted',
               highlight=['Lagos', 'Ibadan', 'Akure', 'Lokoja', 'Abuja'])
    slide_graph('hs-slide-graph.svg', 'The A star example from the course slides: S to A costs 1, S to B 4, A to C 2, B to C 1, C to G 3, '
                'B to G 6; heuristics S 5, A 4, B 3, C 2, G 0')
    slide_graph('hs-slide-astar.svg', 'A star finds S to A to C to G, cost 6, highlighted', highlight=['S', 'A', 'C', 'G'])
    puzzle('hs-8puzzle-small.svg', 'An 8-puzzle start state 1 2 3, blank 4 6, 7 5 8, next to the goal 1 2 3, 4 5 6, 7 8 blank; '
           'tiles 4, 5 and 8 are out of place and shaded', START8)
    puzzle('hs-8puzzle-deep.svg', 'An 8-puzzle start state 1 3 6, 5 blank 7, 4 8 2, twelve moves from the goal 1 2 3, 4 5 6, 7 8 blank; '
           'the six misplaced tiles are shaded', DEEP8)
    landscape('hs-landscape.svg', 'A one-dimensional landscape over states 0 to 12 with values 2, 4, 6, 5, 4, 4, 4, 7, 9, 11, 10, 8, 6: '
              'a local maximum of 6 at state 2, a flat plateau of 4 at states 4 to 6, and the global maximum 11 at state 9',
              marks=[(2, 'local max'), (5, 'plateau'), (9, 'global max')])
