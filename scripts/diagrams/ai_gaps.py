"""Diagrams and checks for the AI lessons the past papers asked for (artificial-intelligence/).

    python3 scripts/diagrams/ai_gaps.py      # run from the vault root

Covers: ways of knowing (01-02), combinatorial explosion and Mancala (01-08), river-crossing
puzzles (02-11), hill climbing 2 (03-08), Nim (04-06), constraint satisfaction (05-01) and
cryptarithmetic (05-02, 05-03). Every number the lessons quote is asserted here before
drawing. Output: artificial-intelligence/images/gp-*.svg.
"""
import itertools
import math
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, ACCENT, FONT, Svg, save_dot, flowchart  # noqa: E402
from artificial_intelligence import OUT, ORANGE  # noqa: E402
from ai_question_bank import nim_value, nim_moves, crypt, bridge, missionaries  # noqa: E402

# ---------- 01-08 combinatorial explosion ----------


def explosion_numbers():
    rows = [(n, n ** 2, 2 ** n) for n in (10, 20, 30, 40)]
    assert rows == [(10, 100, 1024), (20, 400, 1_048_576), (30, 900, 1_073_741_824), (40, 1600, 1_099_511_627_776)]
    assert [3 ** n for n in (1, 2, 3, 10)] == [3, 9, 27, 59_049]
    # Mancala (ayo): at most 6 choices a move.
    assert 6 ** 10 == 60_466_176 and 6 ** 20 == 3_656_158_440_062_976
    secs = 6 ** 20 / 1_000_000                                    # a million positions a second
    assert round(secs / (3600 * 24 * 365)) == 116                  # about 116 years
    assert round(6 ** 10 / 1_000_000) == 60                        # about a minute for 10 moves
    # Effective branching factor 4 after a heuristic prunes 2 of 6 moves.
    assert 4 ** 10 == 1_048_576 and round(6 ** 10 / 4 ** 10) == 58


# ---------- 02-11 river crossings ----------

def bridge_states():
    items = ('goat', 'lion', 'yam')
    legal = []
    for mask in itertools.product((0, 1), repeat=3):
        start = {it for it, m in zip(items, mask) if m == 0}
        for man in 'LR':
            alone = start if man == 'R' else set(items) - start
            if not ({'lion', 'goat'} <= alone or {'goat', 'yam'} <= alone):
                legal.append((frozenset(start), man))
    return legal


def mc_states():
    legal = []
    for m in range(4):
        for c in range(4):
            for b in (0, 1):
                if (m == 0 or m >= c) and (3 - m == 0 or 3 - m >= 3 - c):
                    legal.append((m, c, b))
    return legal


def draw_bridge():
    states = bridge_states()
    path = bridge()
    on = set(zip(path, path[1:]))

    def name(s):
        left, man = s
        l_items = sorted(left) + (['man'] if man == 'L' else [])
        r_items = sorted({'goat', 'lion', 'yam'} - left) + (['man'] if man == 'R' else [])
        return (', '.join(l_items) or 'nothing') + ' | ' + (', '.join(r_items) or 'nothing')
    ids = {s: f's{k}' for k, s in enumerate(states)}
    lines = ['graph { bgcolor="white"; pad=0.2; nodesep=0.3; ranksep=0.35; rankdir=TB;',
             f'node [fontname="{FONT}", fontsize=11, shape=box, style="rounded,filled", fillcolor="#dbeafe", color="{INK}"];',
             f'edge [color="{INK}"];']
    for s in states:
        fill = '#d1fae5' if s == path[0] else '#fde68a' if s == path[-1] else '#dbeafe'
        lines.append(f'{ids[s]} [label="{name(s)}", fillcolor="{fill}"];')
    seen = set()
    for a in states:
        for b in states:
            if a[1] == b[1] or frozenset((a, b)) in seen:
                continue
            diff = a[0] ^ b[0]
            side_items = a[0] if a[1] == 'L' else frozenset({'goat', 'lion', 'yam'}) - a[0]
            if len(diff) <= 1 and diff <= side_items | (b[0] if b[1] == 'L' else frozenset()) and (
                    (a[1] == 'L' and b[0] <= a[0]) or (a[1] == 'R' and a[0] <= b[0])):
                seen.add(frozenset((a, b)))
                hl = (a, b) in on or (b, a) in on
                lines.append(f'{ids[a]} -- {ids[b]}' + (f' [color="{ORANGE}", penwidth=3]' if hl else '') + ';')
    lines.append('}')
    save_dot('\n'.join(lines).replace('graph {', 'graph {', 1), 'gp-bridge-states.svg',
             'Every legal state of the goat, yam and lion puzzle, written as start side then far side, joined by single crossings; '
             'the 7-crossing solution from everything on the start side to everything on the far side is drawn in orange', OUT)


# ---------- 03-08 hill climbing 2 ----------

LAND2 = [1, 3, 5, 5, 5, 8, 10, 12, 9, 6, 7, 7, 7, 5, 3]   # shoulder at 2-4, global max 7, flat local max 10-12


def hc(x, sideways=0):
    path, side = [x], 0
    while True:
        nb = [n for n in (x - 1, x + 1) if 0 <= n < len(LAND2)]
        best = max(nb, key=lambda n: (LAND2[n], n))
        if LAND2[best] > LAND2[x]:
            x, side = best, 0
        elif LAND2[best] == LAND2[x] and side < sideways and best not in path:
            x, side = best, side + 1
        else:
            return path
        path.append(x)


def hill_checks():
    assert hc(0) == [0, 1, 2]                       # stops at the start of the shoulder
    assert hc(0, sideways=3) == [0, 1, 2, 3, 4, 5, 6, 7]   # sideways moves cross the shoulder to the top
    assert hc(11) == [11]                            # flat local maximum: no uphill, sideways goes nowhere better
    assert hc(11, sideways=3)[-1] in (10, 12) and LAND2[hc(11, sideways=3)[-1]] == 7
    assert max(LAND2) == 12 and LAND2.index(12) == 7
    # Simple vs steepest-ascent vs stochastic on a state of value 5 with neighbours 6, 9, 7 (in that order).
    nbrs = [6, 9, 7]
    simple = next(v for v in nbrs if v > 5)
    steepest = max(nbrs)
    uphill = [v for v in nbrs if v > 5]
    assert simple == 6 and steepest == 9 and len(uphill) == 3


def draw_landscape2():
    s = Svg(700, 300, 'A landscape over states 0 to 14 with values 1, 3, 5, 5, 5, 8, 10, 12, 9, 6, 7, 7, 7, 5, 3: a shoulder (a flat '
                      'stretch of 5 at states 2 to 4 that rises again), the global maximum 12 at state 7, and a flat local maximum of 7 '
                      'at states 10 to 12')
    x0, y0, dx, dy = 40, 250, 44, 16
    s.line(x0 - 10, y0, x0 + 14 * dx + 20, y0)
    pts = [(x0 + i * dx, y0 - v * dy) for i, v in enumerate(LAND2)]
    s.path('M ' + ' L '.join(f'{x:.0f} {y:.0f}' for x, y in pts), ACCENT, width=3)
    for i, (x, y) in enumerate(pts):
        s.circle(x, y, 5, ACCENT)
        s.text(x, y - 10, LAND2[i], size=12)
        s.text(x, y0 + 18, i, size=12, color='#374151')
    for i, t in ((3, 'shoulder'), (7, 'global max'), (11, 'flat local max')):
        x, y = pts[i]
        s.text(x, y - 28, t, size=12, color='#b45309', weight='bold')
    s.save('gp-landscape-shoulder.svg', OUT)


# ---------- 04-06 Nim ----------

def nim_checks():
    assert nim_moves((7,)) == [(6, 1), (5, 2), (4, 3)]
    assert nim_value((7,), 'MIN') == 1
    # Who wins with perfect play, for n tokens, the first player to move being MIN.
    table = {n: ('MAX' if nim_value((n,), 'MIN') == 1 else 'MIN') for n in range(1, 11)}
    assert table == {1: 'MAX', 2: 'MAX', 3: 'MIN', 4: 'MAX', 5: 'MIN', 6: 'MIN', 7: 'MAX', 8: 'MIN', 9: 'MIN', 10: 'MAX'}

    def states(s=(7,), out=None):
        out = set() if out is None else out
        out.add(s)
        for k in nim_moves(s):
            states(k, out)
        return out
    st = states()
    assert len(st) == 14 and sorted(s for s in st if not nim_moves(s)) == [(2, 1, 1, 1, 1, 1), (2, 2, 1, 1, 1), (2, 2, 2, 1)]
    return table


# ---------- 05-01 map colouring ----------

REGIONS = ['Lagos', 'Ogun', 'Oyo', 'Osun', 'Ekiti', 'Ondo']   # the order the lesson assigns them
BORDERS = [('Lagos', 'Ogun'), ('Ogun', 'Oyo'), ('Ogun', 'Osun'), ('Ogun', 'Ondo'), ('Oyo', 'Osun'),
           ('Osun', 'Ondo'), ('Osun', 'Ekiti'), ('Ondo', 'Ekiti')]
COLOURS = ['red', 'green', 'blue']


def nbrs(r):
    return [b for a, b in BORDERS if a == r] + [a for a, b in BORDERS if b == r]


def backtrack(forward=False):
    log, tries = [], [0]

    def go(i, assign, domains):
        if i == len(REGIONS):
            return dict(assign)
        r = REGIONS[i]
        for c in domains[r]:
            tries[0] += 1
            if any(assign.get(n) == c for n in nbrs(r)):
                log.append((r, c, 'clash'))
                continue
            log.append((r, c, 'ok'))
            assign[r] = c
            nd = {k: list(v) for k, v in domains.items()}
            dead = False
            if forward:
                for n in nbrs(r):
                    if n not in assign and c in nd[n]:
                        nd[n].remove(c)
                        if not nd[n]:
                            dead = True
            if not dead:
                res = go(i + 1, assign, nd)
                if res:
                    return res
            del assign[r]
            log.append((r, c, 'undo'))
        return None
    res = go(0, {}, {r: list(COLOURS) for r in REGIONS})
    return res, log, tries[0]


def csp_checks():
    res, log, tries = backtrack()
    assert res == {'Lagos': 'red', 'Ogun': 'green', 'Oyo': 'red', 'Osun': 'blue', 'Ekiti': 'green', 'Ondo': 'red'}
    assert all(res[a] != res[b] for a, b in BORDERS)
    assert tries == 13 and [e for e in log if e[2] == 'undo'] == [('Ekiti', 'red', 'undo')]
    assert [e[1] for e in log if e[0] == 'Ondo' and e[2] == 'clash'] == ['red', 'green', 'blue']
    res2, log2, tries2 = backtrack(forward=True)
    assert res2 == res and tries2 == 7 and not any(e[0] == 'Ondo' and e[2] == 'clash' for e in log2)
    assert 3 ** 6 == 729
    return res, log, tries


def draw_regions(res=None):
    pos = {'Lagos': (0.2, 0.2), 'Ogun': (0.9, 1.0), 'Oyo': (1.2, 2.4), 'Osun': (2.2, 1.9), 'Ondo': (3.0, 0.9), 'Ekiti': (3.4, 2.1)}
    fills = {'red': '#fecaca', 'green': '#bbf7d0', 'blue': '#bfdbfe'}
    from artificial_intelligence import save_neato
    lines = ['graph { bgcolor="white"; pad=0.3; splines=line;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];',
             f'edge [color="{INK}", penwidth=1.4];']
    for r, (x, y) in pos.items():
        fill = fills[res[r]] if res else '#e5e7eb'
        lab = f'{r}\\n({res[r]})' if res else r
        lines.append(f'"{r}" [pos="{x * 72:.0f},{y * 72:.0f}!", fillcolor="{fill}", label="{lab}"];')
    for a, b in BORDERS:
        lines.append(f'"{a}" -- "{b}";')
    lines.append('}')
    name = 'gp-southwest-coloured.svg' if res else 'gp-southwest.svg'
    title = ('The six south-western states coloured with three colours so no two neighbours match: Lagos red, Ogun green, Oyo red, '
             'Osun blue, Ondo red, Ekiti green') if res else (
        'The six south-western states as a constraint graph: Lagos joined to Ogun; Ogun to Oyo, Osun and Ondo; Oyo to Osun; '
        'Osun to Ondo and Ekiti; Ondo to Ekiti. Each line means the two states share a border')
    save_neato('\n'.join(lines), name, title)


# ---------- 05-02 / 05-03 cryptarithmetic ----------

def crypt_checks():
    # BASE + BALL reasoning: 2L - 9c1 = 10c2 has no solution with c1 = 1 (parity), and L = 5 is the only usable value.
    assert [(L, c1, c2) for L in range(10) for c1 in (0, 1) for c2 in (0, 1) if 2 * L - 9 * c1 == 10 * c2] == [(0, 0, 0), (5, 0, 1)]
    cases = [(B, c3) for B in range(10) for c3 in (0, 1) if 0 <= 2 * B + c3 - 10 <= 9
             and 0 <= 2 * (2 * B + c3 - 10) + 1 - 10 * c3 <= 9
             and len({B, 2 * B + c3 - 10, 2 * (2 * B + c3 - 10) + 1 - 10 * c3, 1, 5}) == 5]
    assert cases == [(7, 0)]
    # Lesson 01-08 extra numbers.
    assert round(10 ** 12 / (3600 * 24 * 365)) == 31710 and round(math.sqrt(2), 2) == 1.41
    assert 3 ** 4 == 81 and 6 ** 4 == 1296
    assert crypt(['SEND', 'MORE'], 'MONEY') == [{'D': 7, 'E': 5, 'M': 1, 'N': 6, 'O': 0, 'R': 8, 'S': 9, 'Y': 2}]
    assert crypt(['BASE', 'BALL'], 'GAMES') == [{'A': 4, 'B': 7, 'E': 3, 'G': 1, 'L': 5, 'M': 9, 'S': 8}]
    assert crypt(['RED', 'ROE'], 'DEER') == [{'D': 1, 'E': 8, 'O': 0, 'R': 9}]
    assert crypt(['CROSS', 'ROADS'], 'DANGER') == [{'A': 5, 'C': 9, 'D': 1, 'E': 4, 'G': 7, 'N': 8, 'O': 2, 'R': 6, 'S': 3}]
    # Size of the blind search for SEND + MORE: 8 letters to place among 10 digits.
    assert math.perm(10, 8) == 1_814_400
    # quiz: TO + GO = OUT
    assert crypt(['TO', 'GO'], 'OUT') == [{'G': 8, 'O': 1, 'T': 2, 'U': 0}] and 21 + 81 == 102


def draw_red_roe_tree():
    src = f'''digraph {{ bgcolor="white"; pad=0.25; nodesep=0.3; ranksep=0.45;
node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", fillcolor="#dbeafe", color="{INK}"];
edge [fontname="{FONT}", fontsize=11, color="{INK}"];
root [label="RED + ROE = DEER\\nD = 1 (the final carry)", fillcolor="#fde68a"];
u0 [label="units, no carry (c1 = 0)\\n1 + E = R\\nso R = E + 1"];
u1 [label="units, carry (c1 = 1)\\n1 + E = R + 10\\nE = 9, R = 0\\nR leads a number: fail", fillcolor="#f3f4f6", color="#9ca3af", fontcolor="#6b7280"];
t0 [label="tens, no carry (c2 = 0)\\nE + O = E\\nso O = 0"];
t1 [label="tens, carry (c2 = 1)\\nE + O = E + 10\\nO = 10: fail", fillcolor="#f3f4f6", color="#9ca3af", fontcolor="#6b7280"];
h [label="hundreds, carry out = D = 1\\nR + R = E + 10\\n2(E + 1) = E + 10\\nE = 8, R = 9", fillcolor="#d1fae5"];
root -> u0; root -> u1; u0 -> t0; u0 -> t1; t0 -> h;
}}'''
    save_dot(src, 'gp-red-roe-tree.svg',
             'The search tree for RED plus ROE equals DEER, branching on the carry out of each column: D is 1; the units column with '
             'a carry fails because R would be 0; with no carry R is E plus 1; the tens column with a carry fails because O would be '
             '10; with no carry O is 0; the hundreds column then gives E equals 8 and R equals 9', OUT)


def draw_knowing():
    flowchart([
        ('Sensing\\n(the sense organs are stimulated)', 'data'),
        ('Perception\\n(interpreting what was sensed)', 'prog'),
        ('Knowing: recall, calculation\\nor reasoning', 'prog'),
        ('Decision and action', 'fixed'),
    ], 'gp-knowing-loop.svg', 'How a person turns the environment into action: sensing, then perception, then knowing by recall, '
       'calculation or reasoning, then a decision and an action', OUT, rankdir='LR')
    flowchart([
        ('Data\\n(raw facts and figures)', 'data'),
        ('Information\\n(processed, organised data)', 'prog'),
        ('Knowledge\\n(information with rules for applying it)', 'fixed'),
    ], 'gp-data-knowledge.svg', 'The data to knowledge continuum: data, raw facts and figures, becomes information when processed '
       'and organised, and information becomes knowledge when it comes with rules for applying it', OUT, rankdir='LR')


if __name__ == '__main__':
    explosion_numbers()
    hill_checks()
    table = nim_checks()
    res, log, tries = csp_checks()
    crypt_checks()
    assert len(bridge_states()) == 10 and len(bridge()) - 1 == 7
    assert len(mc_states()) == 20 and len(missionaries()) - 1 == 11
    draw_knowing()
    draw_bridge()
    draw_landscape2()
    draw_regions()
    draw_regions(res)
    draw_red_roe_tree()
