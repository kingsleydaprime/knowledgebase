"""Solve and draw the puzzles in artificial-intelligence/02-uninformed-search/12-water-jugs-and-tower-of-hanoi.md.

    python3 scripts/diagrams/ai_puzzles.py      # run from the vault root

Breadth-first search solves the water-jug puzzles and the Tower of Hanoi; every number the lesson
and its quiz quote (shortest solutions, reachable states, impossible targets, 2^n - 1 and 3^n) is
asserted before anything is drawn. Output: artificial-intelligence/images/pz-*.svg.
"""
import math
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, Svg  # noqa: E402
from artificial_intelligence import OUT  # noqa: E402

BLUE = '#2563eb'
WATER = '#93c5fd'
ORANGE = '#f59e0b'
GREY = '#6b7280'
LIGHT = '#e5e7eb'
DISC = ['#f59e0b', '#059669', '#7c3aed', '#dc2626']   # smallest first


# ---------- water jugs ----------

def jug_moves(s, A, B):
    a, b = s
    pab, pba = min(a, B - b), min(b, A - a)
    return [(f'Fill the {A}-litre jug', (A, b)), (f'Fill the {B}-litre jug', (a, B)),
            (f'Empty the {A}-litre jug', (0, b)), (f'Empty the {B}-litre jug', (a, 0)),
            (f'Pour the {A}-litre into the {B}-litre', (a - pab, b + pab)),
            (f'Pour the {B}-litre into the {A}-litre', (a + pba, b - pba))]


def jug_bfs(A, B, goal):
    """Shortest list of (action, state) reaching `goal` litres in the A-litre jug, plus every reachable state."""
    start = (0, 0)
    par, q = {start: None}, deque([start])
    found = None
    while q:
        s = q.popleft()
        if s[0] == goal and found is None:
            found = s
        for act, t in jug_moves(s, A, B):
            if t not in par:
                par[t] = (s, act)
                q.append(t)
    if found is None:
        return None, set(par)
    path, s = [], found
    while par[s]:
        prev, act = par[s]
        path.append((act, s))
        s = prev
    return [('Start', start)] + path[::-1], set(par)


# ---------- Tower of Hanoi ----------

def hanoi_bfs(n):
    """State: the peg (0, 1, 2) of each disc, smallest first. Returns the shortest path and all states."""
    start, goal = (0,) * n, (2,) * n
    par, q = {start: None}, deque([start])
    while q:
        s = q.popleft()
        for d in range(n):
            if any(s[e] == s[d] for e in range(d)):           # a smaller disc is on top of d
                continue
            for peg in range(3):
                if peg != s[d] and not any(s[e] == peg for e in range(d)):
                    t = s[:d] + (peg,) + s[d + 1:]
                    if t not in par:
                        par[t] = s
                        q.append(t)
    path, s = [], goal
    while s is not None:
        path.append(s)
        s = par[s]
    return path[::-1], set(par)


def hanoi_neighbours(s):
    n = len(s)
    out = []
    for d in range(n):
        if any(s[e] == s[d] for e in range(d)):
            continue
        for peg in range(3):
            if peg != s[d] and not any(s[e] == peg for e in range(d)):
                out.append(s[:d] + (peg,) + s[d + 1:])
    return out


def checks():
    out = {}
    path, reach = jug_bfs(7, 4, 6)
    assert [s for _, s in path] == [(0, 0), (7, 0), (3, 4), (3, 0), (0, 3), (7, 3), (6, 4)], path
    assert len(reach) == 22 and all(a in (0, 7) or b in (0, 4) for a, b in reach)   # every edge point, nothing inside
    out['jug'] = (path, reach)
    # quiz: 9 and 4 litres, 6 in the big jug: 8 actions
    p94, _ = jug_bfs(9, 4, 6)
    assert len(p94) - 1 == 8 and p94[-1][1] == (6, 4)
    # quiz: 6 and 4 litres can never measure 3 (every amount is a multiple of gcd(6, 4) = 2)
    p64, r64 = jug_bfs(6, 4, 3)
    assert p64 is None and all(a % 2 == 0 and b % 2 == 0 for a, b in r64) and math.gcd(6, 4) == 2
    # quiz: pouring the 7-litre jug (5 L) into the 4-litre jug (1 L) moves 3 L
    assert dict(jug_moves((5, 1), 7, 4))['Pour the 7-litre into the 4-litre'] == (2, 4)
    # the Tower of Hanoi
    for n in (1, 2, 3, 4, 5):
        hp, hs = hanoi_bfs(n)
        assert len(hp) - 1 == 2 ** n - 1 and len(hs) == 3 ** n, (n, len(hp), len(hs))
    hp, hs = hanoi_bfs(3)
    assert hp == [(0, 0, 0), (2, 0, 0), (2, 1, 0), (1, 1, 0), (1, 1, 2), (0, 1, 2), (0, 2, 2), (2, 2, 2)], hp
    # recursion: moves(n) = 2 moves(n - 1) + 1
    assert all(2 * (2 ** (n - 1) - 1) + 1 == 2 ** n - 1 for n in range(1, 11))
    # the state space's corners have 2 moves, every other state 3
    degs = sorted(len(hanoi_neighbours(s)) for s in hs)
    assert degs.count(2) == 3 and degs.count(3) == 24
    out['hanoi'] = (hp, hs)
    return out


# ---------- drawings ----------

def jug(s, x, y, cap, level, scale, w):
    h = cap * scale
    s.rect(x, y + h - level * scale, w, level * scale, WATER)
    s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
    for k in range(1, cap):
        s.line(x, y + h - k * scale, x + 5, y + h - k * scale, color=GREY, width=1)
    s.text(x + w / 2, y + h + 16, f'{level}', size=13, weight='bold', color=BLUE)


def draw_jug_steps(path):
    cols = 4
    rows = math.ceil(len(path) / cols)
    s = Svg(640, 60 + rows * 210, 'The 7-litre and 4-litre jug puzzle solved in six actions: start empty (0, 0); fill the '
                                  '7-litre jug (7, 0); pour it into the 4-litre jug (3, 4); empty the 4-litre jug (3, 0); '
                                  'pour the 7-litre into the 4-litre (0, 3); fill the 7-litre jug (7, 3); pour the 7-litre '
                                  'into the 4-litre until it is full, leaving exactly 6 litres (6, 4)')
    for i, (act, (a, b)) in enumerate(path):
        cx, cy = 20 + (i % cols) * 155, 30 + (i // cols) * 210
        s.rect(cx, cy, 145, 195, '#ffffff', stroke=LIGHT)
        s.text(cx + 72, cy + 18, f'{i}. ' + ('start' if i == 0 else 'action ' + str(i)), size=12, weight='bold')
        jug(s, cx + 22, cy + 48, 7, a, 14, 44)
        jug(s, cx + 82, cy + 90, 4, b, 14, 40)
        short = {'Start': 'empty jugs', 'Fill the 7-litre jug': 'fill 7 L', 'Fill the 4-litre jug': 'fill 4 L',
                 'Empty the 7-litre jug': 'empty 7 L', 'Empty the 4-litre jug': 'empty 4 L',
                 'Pour the 7-litre into the 4-litre': 'pour 7 L → 4 L', 'Pour the 4-litre into the 7-litre': 'pour 4 L → 7 L'}
        s.text(cx + 72, cy + 34, short[act], size=11.5, color=GREY)
        s.text(cx + 72, cy + 190, f'({a}, {b})', size=12.5, weight='bold', color=ORANGE if a == 6 else INK)
    s.save('pz-jugs-steps.svg', OUT)


def draw_jug_space(path, reach):
    s = Svg(520, 320, 'Every state of the 7-litre and 4-litre jug puzzle as a grid of (a, b), with a the litres in the 7-litre '
                      'jug and b in the 4-litre jug. Only 22 of the 40 grid points can ever be reached: exactly the points on the edges of '
                      'the grid, because after any action at least one jug is empty or full. The six-action solution is drawn '
                      'as orange arrows from (0, 0) to (6, 4)')
    ox, oy, sc = 70, 260, 52
    for a in range(8):
        s.text(ox + a * sc, oy + 22, a, size=12, color=GREY)
    for b in range(5):
        s.text(ox - 16, oy - b * sc + 4, b, size=12, color=GREY, anchor='end')
    s.text(ox + 3.5 * sc, oy + 44, 'a: litres in the 7-litre jug', size=12.5, weight='bold')
    s.text(ox - 40, oy - 2 * sc - 30, 'b: 4-litre jug', size=12.5, weight='bold', anchor='start')
    for a in range(8):
        for b in range(5):
            x, y = ox + a * sc, oy - b * sc
            if (a, b) in reach:
                s.circle(x, y, 7, BLUE)
            else:
                s.circle(x, y, 3, LIGHT)
    pts = [st for _, st in path]
    for (a1, b1), (a2, b2) in zip(pts, pts[1:]):
        x1, y1, x2, y2 = ox + a1 * sc, oy - b1 * sc, ox + a2 * sc, oy - b2 * sc
        d = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        x1, y1, x2, y2 = x1 + 9 * ux, y1 + 9 * uy, x2 - 10 * ux, y2 - 10 * uy
        s.line(x1, y1, x2, y2, color=ORANGE, width=3)
        ang = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - 9 * math.cos(ang - 0.4), y2 - 9 * math.sin(ang - 0.4))
        p2 = (x2 - 9 * math.cos(ang + 0.4), y2 - 9 * math.sin(ang + 0.4))
        s.add(f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{ORANGE}"/>')
    gx, gy = ox + 6 * sc, oy - 4 * sc
    s.add(f'<circle cx="{gx}" cy="{gy}" r="12" fill="none" stroke="{ORANGE}" stroke-width="2.5"/>')
    s.text(gx, gy - 18, 'goal (6, 4)', size=12, weight='bold', color=ORANGE)
    s.save('pz-jugs-space.svg', OUT)


def pegs(s, x, y, state, n, w=150):
    for p in range(3):
        px = x + 25 + p * 50
        s.line(px, y, px, y + 70, color=GREY, width=3)
        s.text(px, y + 92, 'ABC'[p], size=12, weight='bold')
    s.line(x, y + 70, x + w, y + 70, color=INK, width=3)
    for p in range(3):
        stack = [d for d in range(n - 1, -1, -1) if state[d] == p]          # biggest at the bottom
        for k, d in enumerate(stack):
            dw = 18 + d * 10
            px = x + 25 + p * 50
            s.add(f'<rect x="{px - dw / 2:.1f}" y="{y + 56 - k * 14}" width="{dw}" height="12" rx="3" fill="{DISC[d]}" '
                  f'stroke="{INK}" stroke-width="1"/>')


def draw_hanoi_steps(hp):
    names = ['small', 'medium', 'large']
    s = Svg(660, 300, 'The Tower of Hanoi with three discs solved in seven moves: small to C, medium to B, small to B, large '
                      'to C, small to A, medium to C, small to C. Each panel shows the pegs after one move')
    for i, st in enumerate(hp):
        cx, cy = 10 + (i % 4) * 162, 20 + (i // 4) * 140
        if i == 0:
            cap = 'start'
        else:
            d = next(k for k in range(3) if st[k] != hp[i - 1][k])
            cap = f'{i}. {names[d]} {"ABC"[hp[i - 1][d]]} → {"ABC"[st[d]]}'
        s.text(cx + 75, cy + 10, cap, size=12, weight='bold')
        pegs(s, cx, cy + 20, st, 3)
    s.save('pz-hanoi-steps.svg', OUT)


def draw_hanoi_space(hp, hs):
    """The 27 states laid out as a Sierpinski triangle: the largest disc picks the corner."""
    corner = {0: (0.0, 0.0), 1: (1.0, 0.0), 2: (0.5, -math.sqrt(3) / 2)}   # A bottom-left, B bottom-right, C top

    def pos(st):
        x, y, size, mapping = 0.0, 0.0, 1.0, {0: 0, 1: 1, 2: 2}
        for d in range(len(st) - 1, -1, -1):          # largest disc first
            size /= 2
            p = st[d]
            cx, cy = corner[mapping[p]]
            x += cx * size
            y += cy * size
            o1, o2 = [q for q in range(3) if q != p]   # inside this sub-triangle, the other two pegs swap corners
            mapping = dict(mapping)
            mapping[o1], mapping[o2] = mapping[o2], mapping[o1]
        return x, y
    W, ox, oy = 560, 60, 470
    P = {st: (ox + pos(st)[0] * W, oy + pos(st)[1] * W) for st in hs}
    for a_ in hs:                                     # every move must join two neighbouring points
        for b_ in hanoi_neighbours(a_):
            assert math.dist(P[a_], P[b_]) < 0.2 * W, (a_, b_)
    s = Svg(620, 520, 'The whole state space of the three-disc Tower of Hanoi: 27 states, each joined to the states one move '
                      'away, form a triangle of triangles. The three corners are all discs on peg A, on peg B and on peg C. '
                      'The shortest solution, seven moves, runs straight along the left edge from all-on-A (bottom left) to '
                      'all-on-C (top), shown in orange')
    on_path = set(zip(hp, hp[1:])) | set(zip(hp[1:], hp))
    for a in hs:
        for b in hanoi_neighbours(a):
            if a < b:
                (x1, y1), (x2, y2) = P[a], P[b]
                hot = (a, b) in on_path
                s.line(x1, y1, x2, y2, color=ORANGE if hot else GREY, width=4 if hot else 1.4)
    for st, (x, y) in P.items():
        s.circle(x, y, 6, ORANGE if st in hp else BLUE)
    s.text(P[(0, 0, 0)][0], P[(0, 0, 0)][1] + 24, 'all on A (start)', size=12.5, weight='bold', anchor='start')
    s.text(P[(1, 1, 1)][0], P[(1, 1, 1)][1] + 24, 'all on B', size=12.5, weight='bold', anchor='end')
    s.text(P[(2, 2, 2)][0], P[(2, 2, 2)][1] - 14, 'all on C (goal)', size=12.5, weight='bold', color=ORANGE)
    s.save('pz-hanoi-space.svg', OUT)


if __name__ == '__main__':
    out = checks()
    print('puzzles: all numbers check')
    draw_jug_steps(out['jug'][0])
    draw_jug_space(*out['jug'])
    draw_hanoi_steps(out['hanoi'][0])
    draw_hanoi_space(*out['hanoi'])
