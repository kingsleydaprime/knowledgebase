"""Solve and draw the past-paper answers (artificial-intelligence/mock-exam-1.md and question-bank.md).

    python3 scripts/diagrams/ai_question_bank.py      # run from the vault root

Every number in the question bank's solutions is computed here and asserted before
anything is drawn: the 2025/26 SSG 518 exam (8-puzzle A*, the bridge crossing, mutual
information, alpha-beta) and the recurring SSG 503 calculation questions (cryptarithms,
missionaries and cannibals, Nim, alpha-beta, search orders, entropy tables, the leaf
classification and the loaded coin). Output: artificial-intelligence/images/qb-*.svg.
"""
import heapq
import itertools
import math
import os
import sys
from collections import deque
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, FONT, save_dot, flowchart  # noqa: E402
from artificial_intelligence import OUT, ORANGE  # noqa: E402
from ai_heuristic import misplaced, manhattan, moves, GOAL8  # noqa: E402
from ai_games import alphabeta, leaves_seen, pruned, backed_up, draw_game_tree, minimax  # noqa: E402

log2 = math.log2


# ---------- 2025/26 Q4a: 8-puzzle by A* with misplaced tiles ----------

START8 = (1, 2, 3, 4, 8, 0, 7, 6, 5)


def astar8(h):
    c = itertools.count()
    g, par = {START8: 0}, {START8: None}
    heap = [(h(START8), h(START8), next(c), START8)]
    done, gen = [], []
    while heap:
        f, hh, _, s = heapq.heappop(heap)
        if s in done:
            continue
        done.append(s)
        if s == GOAL8:
            path, n = [], s
            while n:
                path.append(n)
                n = par[n]
            return done, gen, path[::-1]
        for t in moves(s):
            if t == par[s] or t in done:
                continue
            ng = g[s] + 1
            if t not in g or ng < g[t]:
                g[t], par[t] = ng, s
                gen.append((s, t, ng, h(t)))
                heapq.heappush(heap, (ng + h(t), h(t), next(c), t))


def fmt(s):
    return ''.join(str(x) if x else '_' for x in s)


# ---------- 2025/26 Q4b and SSG 503: river and bridge crossings ----------

def bridge():
    items = ('goat', 'lion', 'yam')

    def safe(side):
        return not ({'lion', 'goat'} <= side or {'goat', 'yam'} <= side)
    start, goal = (frozenset(items), 'L'), (frozenset(), 'R')
    par, q = {start: None}, deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            break
        left, man = s
        here = left if man == 'L' else frozenset(items) - left
        for take in [None] + sorted(here):
            nl = set(left)
            if take:
                nl.discard(take) if man == 'L' else nl.add(take)
            nm = 'R' if man == 'L' else 'L'
            nl = frozenset(nl)
            alone = nl if nm == 'R' else frozenset(items) - nl
            if safe(set(alone)) and (nl, nm) not in par:
                par[(nl, nm)] = s
                q.append((nl, nm))
    path, n = [], goal
    while n:
        path.append(n)
        n = par[n]
    return path[::-1]


def missionaries():
    start, goal = (3, 3, 1), (0, 0, 0)

    def ok(m, c):
        return (m == 0 or m >= c) and (3 - m == 0 or 3 - m >= 3 - c)
    par, q = {start: None}, deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            break
        m, c, b = s
        for dm, dc in [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]:
            nm, nc = (m - dm, c - dc) if b else (m + dm, c + dc)
            if 0 <= nm <= 3 and 0 <= nc <= 3 and ok(nm, nc) and (nm, nc, 1 - b) not in par:
                par[(nm, nc, 1 - b)] = s
                q.append((nm, nc, 1 - b))
    path, n = [], goal
    while n:
        path.append(n)
        n = par[n]
    return path[::-1]


# ---------- entropy and mutual information ----------

def table_info(cells):
    """cells: {(row, col): p}. Returns total, row marginals, col marginals, H(rows), H(cols), H(joint), I."""
    tot = sum(cells.values())
    pr, pc = {}, {}
    for (r, c), p in cells.items():
        pr[r] = pr.get(r, 0) + p
        pc[c] = pc.get(c, 0) + p

    def H(ps):
        return -sum(float(p) * log2(p) for p in ps if p > 0)
    i = sum(float(p) * log2(p / (pr[r] * pc[c])) for (r, c), p in cells.items() if p > 0)
    return tot, pr, pc, H(pr.values()), H(pc.values()), H(cells.values()), i


EXAM_Q5 = {('F', 'S'): Fr(1, 12), ('F', 'G'): Fr(1, 12), ('F', 'O'): Fr(1, 6),
           ('P', 'S'): Fr(1, 6), ('P', 'G'): Fr(1, 12), ('P', 'O'): Fr(1, 12),
           ('D', 'S'): Fr(1, 12), ('D', 'G'): Fr(1, 6), ('D', 'O'): Fr(0)}
PAPER_1920 = [('*', '*', Fr(1, 8)), ('1', 'a', Fr(1, 16)), ('0', 'b', Fr(1, 8)), ('1', 'c', Fr(1, 2)), ('0', 'd', Fr(1, 16)),
              ('0', 'a', Fr(1, 4)), ('1', 'b', Fr(1, 8)), ('0', 'c', Fr(1, 4)), ('1', 'd', Fr(1, 2))]


def coin(p):
    return -(p * log2(p) + (1 - p) * log2(1 - p))


# ---------- cryptarithms ----------

def crypt(words, res):
    letters = sorted(set(''.join(words) + res))
    lead = {w[0] for w in words + [res]}
    sols = []
    for perm in itertools.permutations(range(10), len(letters)):
        m = dict(zip(letters, perm))
        if any(m[ch] == 0 for ch in lead):
            continue

        def v(w):
            return int(''.join(str(m[ch]) for ch in w))
        if sum(v(w) for w in words) == v(res):
            sols.append(m)
    return sols


# ---------- Nim (7 tokens, MIN first; utility 1 if MAX wins) ----------

def nim_moves(state):
    out = set()
    for i, n in enumerate(state):
        for a in range(1, (n + 1) // 2):
            if a != n - a:
                out.add(tuple(sorted(state[:i] + state[i + 1:] + (a, n - a), reverse=True)))
    return sorted(out, reverse=True)


def nim_value(state, player, memo=None):
    memo = {} if memo is None else memo
    key = (state, player)
    if key in memo:
        return memo[key]
    kids = nim_moves(state)
    if not kids:                                  # player to move cannot move, so loses
        v = 1 if player == 'MIN' else 0
    else:
        vals = [nim_value(k, 'MAX' if player == 'MIN' else 'MIN', memo) for k in kids]
        v = max(vals) if player == 'MAX' else min(vals)
    memo[key] = v
    return v


# ---------- search orders on the 2015/16 tree ----------

TREE1516 = {'A': [('B', 1), ('C', 3)], 'B': [('D', 1), ('E', 1)], 'C': [('G', 1), ('H', 2)], 'D': [('F', 1)],
            'F': [('K', 2), ('L', 2)], 'H': [('I', 1), ('J', 1)]}


def kids(n):
    return TREE1516.get(n, [])


def order_bfs(goal='G'):
    out, q = [], deque(['A'])
    while q:
        n = q.popleft()
        out.append(n)
        if n == goal:
            return out
        q.extend(k for k, _ in kids(n))


def order_dfs(goal='G'):
    out = []

    def go(n):
        out.append(n)
        if n == goal:
            return True
        return any(go(k) for k, _ in kids(n))
    go('A')
    return out


def order_ucs(goal='G'):
    out, heap = [], [(0, 'A')]
    while heap:
        c, n = heapq.heappop(heap)
        out.append((n, c))
        if n == goal:
            return out
        for k, d in kids(n):
            heapq.heappush(heap, (c + d, k))


def order_ids(goal='G'):
    rounds = []
    for lim in range(10):
        out = []

        def go(n, d):
            out.append(n)
            if n == goal:
                return True
            return d < lim and any(go(k, d + 1) for k, _ in kids(n))
        found = go('A', 0)
        rounds.append(out)
        if found:
            return rounds


# ---------- assertions ----------

TREE_2526 = [[[[10, 5], [7, 11]], [[12, 8], [9, 8]]], [[[5, 12], [11, 12]], [[9, 8], [7, 10]]]]
TREE_1920 = [[[6, 5], [8, 10]], [[2, 1], [15, 18]]]


def check():
    # 2025/26 Q4a.
    assert misplaced(START8) == 3 and manhattan(START8) == 5
    done, gen, path = astar8(misplaced)
    assert len(path) - 1 == 5 and len(done) == 7 and len(gen) == 14
    assert [fmt(s) for s in path] == ['12348_765', '12348576_', '1234857_6', '1234_5786', '12345_786', '12345678_']
    assert [misplaced(s) for s in path] == [3, 3, 3, 2, 1, 0]
    assert fmt(done[2]) == '1234_8765'                                  # the side branch A* tries and drops
    done2, gen2, path2 = astar8(manhattan)
    assert path2 == path and len(done2) == 6 and len(gen2) == 11
    # 2025/26 Q4b.
    p = bridge()
    assert len(p) - 1 == 7
    assert [sorted(left) for left, _ in p] == [['goat', 'lion', 'yam'], ['lion', 'yam'], ['lion', 'yam'], ['yam'],
                                              ['goat', 'yam'], ['goat'], ['goat'], []]
    # 2025/26 Q5.
    tot, pr, pc, hy, hx, hxy, i = table_info(EXAM_Q5)
    assert tot == Fr(11, 12)
    norm = {k: v / tot for k, v in EXAM_Q5.items()}
    tot, pr, pc, hy, hx, hxy, i = table_info(norm)
    assert tot == 1 and pr == {'F': Fr(4, 11), 'P': Fr(4, 11), 'D': Fr(3, 11)} and pc == {'S': Fr(4, 11), 'G': Fr(4, 11), 'O': Fr(3, 11)}
    assert round(hx, 4) == 1.5726 and round(hy, 4) == 1.5726 and round(hxy, 4) == 2.9140 and round(i, 4) == 0.2313
    assert round(hx + hy - hxy, 4) == round(i, 4)
    filled = {**EXAM_Q5, ('D', 'O'): Fr(1, 12)}                   # if the 0 was meant to be 1/12
    tot, pr, pc, hy2, hx2, hxy2, i2 = table_info(filled)
    assert tot == 1 and round(hx2, 4) == 1.585 and round(hxy2, 4) == 3.085 and round(i2, 4) == 0.085
    # 2025/26 Q6.
    v, log = alphabeta(TREE_2526)
    assert v == 8 and len(leaves_seen(log)) == 12
    assert pruned(log) == [(0, 1, 1), (1, 0, 0, 1), (1, 1, 1, 1)]
    _, vals = backed_up(TREE_2526)
    assert vals[(0,)] == 7 and vals[(1,)] == 8 and [vals[(0, 0)], vals[(0, 1)], vals[(1, 0)], vals[(1, 1)]] == [7, 8, 11, 8]
    # SSG 503 2019/20: alpha-beta, Nim, cryptarithm, entropy table, missionaries.
    v, log = alphabeta(TREE_1920)
    assert v == 6 and leaves_seen(log) == [6, 5, 8, 2, 1] and pruned(log) == [(0, 1, 1), (1, 1)]
    assert nim_value((7,), 'MIN') == 1                                   # MAX wins with perfect play
    assert nim_moves((7,)) == [(6, 1), (5, 2), (4, 3)]
    assert crypt(['BASE', 'BALL'], 'GAMES') == [{'A': 4, 'B': 7, 'E': 3, 'G': 1, 'L': 5, 'M': 9, 'S': 8}]
    assert 7483 + 7455 == 14938
    cells = {(x, y): p for x, y, p in PAPER_1920}
    assert sum(cells.values()) == 2
    half = {k: v / 2 for k, v in cells.items()}
    tot, px, py, hx, hy, hxy, i = table_info(half)
    assert px == {'*': Fr(1, 16), '1': Fr(19, 32), '0': Fr(11, 32)}
    assert round(hx, 4) == 1.2261 and round(hy, 4) == 2.0888 and hxy == 2.8125 and round(i, 4) == 0.5024
    mc = missionaries()
    assert len(mc) - 1 == 11
    # The textbook sequence printed in the bank: start-bank (M, C) after each crossing, every state legal.
    seq = [(3, 3), (3, 1), (3, 2), (3, 0), (3, 1), (1, 1), (2, 2), (0, 2), (0, 3), (0, 1), (0, 2), (0, 0)]
    for k, ((m0, c0), (m1, c1)) in enumerate(zip(seq, seq[1:])):
        moved = abs(m1 - m0) + abs(c1 - c0)
        assert 1 <= moved <= 2 and ((m1 <= m0 and c1 <= c0) if k % 2 == 0 else (m1 >= m0 and c1 >= c0))
        for m, c in ((m1, c1), (3 - m1, 3 - c1)):
            assert m == 0 or m >= c
    # SSG 503 2012-2017: RED + ROE = DEER, SEND + MORE, CROSS + ROADS.
    assert crypt(['RED', 'ROE'], 'DEER') == [{'D': 1, 'E': 8, 'O': 0, 'R': 9}] and 981 + 908 == 1889
    assert len(crypt(['SEND', 'MORE'], 'MONEY')) == 1 and 9567 + 1085 == 10652
    assert len(crypt(['CROSS', 'ROADS'], 'DANGER')) == 1 and 96233 + 62513 == 158746
    # SSG 503 2015/16 Q1 search orders.
    assert order_bfs() == list('ABCDEG')
    assert order_dfs() == list('ABDFKLECG')
    assert order_ucs() == [('A', 0), ('B', 1), ('D', 2), ('E', 2), ('C', 3), ('F', 3), ('G', 4)]
    assert order_ids() == [['A'], ['A', 'B', 'C'], ['A', 'B', 'D', 'E', 'C', 'G']]
    # Loaded coin.
    assert [round(coin(p), 3) for p in (0.1, 0.2, 0.3, 0.4)] == [0.469, 0.722, 0.881, 0.971] and coin(0.5) == 1
    # Leaf chart: centroids read off the chart (approximate), and the three samples.
    cents = {'Class 1': (10, 11), 'Class 2': (12, 4.5), 'Class 3': (31, 16.5)}
    samples = {'a': (14, 6.5), 'b': (10, 13.5), 'c': (35, 18)}
    near = {s: min(cents, key=lambda k: math.dist(p, cents[k])) for s, p in samples.items()}
    assert near == {'a': 'Class 2', 'b': 'Class 1', 'c': 'Class 3'}
    assert round(math.dist(samples['a'], cents['Class 2']), 2) == 2.83 and round(math.dist(samples['a'], cents['Class 1']), 2) == 6.02
    return vals


# ---------- drawing ----------

def puzzle_label(s, g, h, highlight=False):
    rows = []
    for r in range(3):
        cells = ''.join(f'<TD WIDTH="16" HEIGHT="16">{s[r * 3 + c] if s[r * 3 + c] else " "}</TD>' for c in range(3))
        rows.append(f'<TR>{cells}</TR>')
    colour = '#fde68a' if highlight else '#ffffff'
    return (f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="{colour}">{"".join(rows)}'
            f'<TR><TD COLSPAN="3" BORDER="0"><FONT POINT-SIZE="10">g={g} h={h} f={g + h}</FONT></TD></TR></TABLE>>')


def draw_8puzzle():
    done, gen, path = astar8(misplaced)
    on_path = set(path)
    lines = ['digraph { bgcolor="white"; pad=0.2; nodesep=0.15; ranksep=0.35;',
             f'node [shape=plaintext, fontname="{FONT}", fontsize=11];', f'edge [color="{INK}", arrowsize=0.6];']
    ids = {START8: 'n0'}
    lines.append(f'n0 [label={puzzle_label(START8, 0, misplaced(START8), True)}];')
    for k, (a, b, g, h) in enumerate(gen, 1):
        ids[b] = f'n{k}'
        lines.append(f'n{k} [label={puzzle_label(b, g, h, b in on_path)}];')
        style = f' [color="{ORANGE}", penwidth=2.5]' if a in on_path and b in on_path else ''
        lines.append(f'{ids[a]} -> n{k}{style};')
    lines.append('}')
    save_dot('\n'.join(lines), 'qb-8puzzle-astar.svg',
             'The A star search tree for the exam 8-puzzle, using misplaced tiles: from 1 2 3, 4 8 blank, 7 6 5, the solution path '
             'of five moves is shaded yellow and joined by orange arrows; each node shows g, h and f', OUT)


def draw_nim():
    lines = ['digraph { bgcolor="white"; pad=0.2; nodesep=0.25; ranksep=0.45;',
             f'node [fontname="{FONT}", fontsize=12, style="rounded,filled", shape=box, color="{INK}"];', f'edge [color="{INK}"];']
    seen = {}

    def add(state, player):
        key = (state, player)
        if key in seen:
            return seen[key]
        nid = f'n{len(seen)}'
        seen[key] = nid
        v = nim_value(state, player)
        fill = '#dbeafe' if player == 'MAX' else '#fde68a'
        lines.append(f'{nid} [label="{"-".join(map(str, state))}\\n{player} to move\\nvalue {v}", fillcolor="{fill}"];')
        for k in nim_moves(state):
            lines.append(f'{nid} -> {add(k, "MAX" if player == "MIN" else "MIN")};')
        return nid
    add((7,), 'MIN')
    lines.append('}')
    save_dot('\n'.join(lines), 'qb-nim.svg',
             'The Nim game tree from one stack of 7, MIN to move first; each state shows the stacks, whose turn it is, and its '
             'minimax value (1 means MAX wins); the root value is 1, so MAX wins with perfect play', OUT)


def draw_1516():
    lines = ['digraph { bgcolor="white"; pad=0.2; nodesep=0.35; ranksep=0.4;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style=filled, fillcolor="#dbeafe", color="{INK}"];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}", dir=none];', 'G [fillcolor="#fde68a"];']
    for p, ks in TREE1516.items():
        for k, d in ks:
            lines.append(f'{p} -> {k} [label=" {d}"];')
    lines.append('}')
    save_dot('\n'.join(lines), 'qb-1516-tree.svg',
             'The 2015/16 SSG 503 tree: A to B costs 1 and A to C 3; B to D 1 and B to E 1; C to G 1 and C to H 2; D to F 1; '
             'F to K 2 and F to L 2; H to I 1 and H to J 1; G is the goal', OUT)


if __name__ == '__main__':
    vals = check()
    flowchart([('Data collection', 'data'), ('Feature choice', 'prog'), ('Model choice', 'prog'),
               ('Training the classifier', 'prog'), ('Evaluating the classifier', 'fixed')], 'qb-pr-steps.svg',
              'The steps in pattern recognition: data collection, feature choice, model choice, training the classifier, '
              'then evaluating the classifier, after which the process terminates', OUT, rankdir='LR')
    draw_8puzzle()
    draw_nim()
    draw_1516()
    v, log = alphabeta(TREE_2526)
    abvals = {e[1]: e[4] for e in log if e[0] == 'node'}
    draw_game_tree(TREE_2526, 'qb-2526-alphabeta.svg',
                   'The 2025/26 exam tree solved with alpha-beta: four levels MAX, MIN, MAX, MIN over sixteen leaves; the two MIN nodes '
                   'under the root are 7 and 8, so the root is 8; the MIN node over leaves 9 and 8, the tenth leaf (12) and the '
                   'last leaf (10) are pruned and greyed out',
                   values=abvals, pruned_paths=pruned(log), xgap=44)
    v, log = alphabeta(TREE_1920)
    abvals = {e[1]: e[4] for e in log if e[0] == 'node'}
    draw_game_tree(TREE_1920, 'qb-1920-alphabeta.svg',
                   'The 2019/20 SSG 503 tree solved with alpha-beta: root A is 6; the leaf 10 under E and the whole subtree G '
                   'with leaves 15 and 18 are pruned', values=abvals, pruned_paths=pruned(log), xgap=60)
