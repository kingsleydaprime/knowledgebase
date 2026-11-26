"""Solve and draw the AI mock exams (artificial-intelligence/mock-exam-2.md onwards).

    python3 scripts/diagrams/ai_mocks.py      # run from the vault root

Every number in the mock exams' questions and worked answers is computed here and
asserted before anything is drawn. Mock Exam 1 is the real 2025/26 paper; its numbers
live in ai_question_bank.py. Output: artificial-intelligence/images/mock*-*.svg.
"""
import heapq
import itertools
import math
import os
import sys
from collections import deque
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, FONT, save_dot  # noqa: E402
from artificial_intelligence import OUT, ORANGE  # noqa: E402
from ai_heuristic import manhattan, misplaced, moves, GOAL8  # noqa: E402
from ai_games import alphabeta, leaves_seen, pruned, backed_up, draw_game_tree, minimax  # noqa: E402
from ai_question_bank import puzzle_label  # noqa: E402


def H(ps):
    return -sum(float(p) * math.log2(p) for p in ps if p)


# ---------- Mock 2 ----------

M2_RIPE = {"X": [(2, 7), (3, 8), (4, 9)], "Y": [(7, 2), (8, 3), (9, 1)]}
M2_NEW = (5, 5)
M2_CONFUSION = {"TP": 45, "FN": 15, "FP": 10, "TN": 30}
M2_ERRORS = [0.2, 0.5, 0.1, 0.4, 0.3]
M2_JOINT = {  # p(x, y): X = how you travel, Y = when you arrive
    ("bus", "early"): Fr(1, 4), ("keke", "early"): Fr(1, 8), ("walk", "early"): Fr(1, 8),
    ("bus", "late"): Fr(1, 8), ("keke", "late"): Fr(1, 4), ("walk", "late"): Fr(1, 8),
}
M2_PUZZLE = (2, 3, 0, 1, 5, 6, 4, 7, 8)       # rows 2 3 _ / 1 5 6 / 4 7 8
M2_LEAVES = [8, 7, 5, 14, 14, 14, 1, 3, 1, 7, 12, 13, 15, 13, 8, 10]
M2_TREE = [[[M2_LEAVES[0:2], M2_LEAVES[2:4]], [M2_LEAVES[4:6], M2_LEAVES[6:8]]],
           [[M2_LEAVES[8:10], M2_LEAVES[10:12]], [M2_LEAVES[12:14], M2_LEAVES[14:16]]]]


def mean(pts):
    return tuple(Fr(sum(c), len(pts)) for c in zip(*pts))


def dist(a, b):
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def astar8(start, h):
    """A* with ties broken by smaller h, then insertion order. Returns (expanded, generated, path)."""
    c = itertools.count()
    g, par = {start: 0}, {start: None}
    heap = [(h(start), h(start), next(c), start)]
    done, gen = [], []
    while heap:
        f, hh, _, s = heapq.heappop(heap)
        if s in done:
            continue
        done.append(s)
        if s == GOAL8:
            path = [s]
            while par[path[-1]]:
                path.append(par[path[-1]])
            return done, gen, path[::-1]
        for t in moves(s):
            if t == par[s]:
                continue                       # never move the blank straight back
            if t not in g or g[s] + 1 < g[t]:
                g[t], par[t] = g[s] + 1, s
                gen.append((s, t, g[t], h(t)))
                heapq.heappush(heap, (g[t] + h(t), h(t), next(c), t))


def hanoi_bfs(n=3):
    """States: a tuple giving each disc's peg (disc 0 smallest). Returns the shortest move list."""
    start, goal = (0,) * n, (2,) * n
    par, q = {start: None}, deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            path = []
            while s is not None:
                path.append(s)
                s = par[s]
            return path[::-1], len(par)
        for d in range(n):
            if any(s[e] == s[d] for e in range(d)):      # a smaller disc sits on top
                continue
            for peg in range(3):
                if peg != s[d] and not any(s[e] == peg for e in range(d)):
                    t = s[:d] + (peg,) + s[d + 1:]
                    if t not in par:
                        par[t] = s
                        q.append(t)


def check_mock_2():
    # Q1: nearest mean
    mx, my = mean(M2_RIPE["X"]), mean(M2_RIPE["Y"])
    assert (mx, my) == ((3, 8), (8, 2))
    dx, dy = dist(M2_NEW, mx), dist(M2_NEW, my)
    assert round(dx, 3) == 3.606 and round(dy, 3) == 4.243 and dx < dy   # class X

    # Q2: kappa, MAE, RMSE
    c = M2_CONFUSION
    n = sum(c.values())
    po = Fr(c["TP"] + c["TN"], n)
    actual_pos, pred_pos = c["TP"] + c["FN"], c["TP"] + c["FP"]
    pe = Fr(actual_pos * pred_pos + (n - actual_pos) * (n - pred_pos), n * n)
    kappa = (po - pe) / (1 - pe)
    assert (po, pe) == (Fr(3, 4), Fr(51, 100)) and round(float(kappa), 4) == 0.4898
    mae = sum(M2_ERRORS) / len(M2_ERRORS)
    rmse = math.sqrt(sum(e * e for e in M2_ERRORS) / len(M2_ERRORS))
    assert round(mae, 4) == 0.3 and round(rmse, 4) == 0.3317

    # Q3: bidirectional, b = 4, d = 10
    assert sum(4 ** k for k in range(1, 11)) == 1_398_100
    assert 2 * sum(4 ** k for k in range(1, 6)) == 2_728

    # Q4: the 8-puzzle by A* with Manhattan distance
    assert (misplaced(M2_PUZZLE), manhattan(M2_PUZZLE)) == (6, 6)
    done, gen, path = astar8(M2_PUZZLE, manhattan)
    assert len(path) - 1 == 6 and len(done) == 7 and len(gen) == 10, (len(path), len(done), len(gen))
    assert sum(1 for _, b, g, h in gen if b not in path and g + h == 8) == 4   # four side branches, all f = 8
    # Q4b: Tower of Hanoi, 3 discs
    moves_list, reachable = hanoi_bfs(3)
    assert len(moves_list) - 1 == 7 and reachable == 27

    # Q5: entropy and mutual information
    px, py = {}, {}
    for (x, y), p in M2_JOINT.items():
        px[x] = px.get(x, 0) + p
        py[y] = py.get(y, 0) + p
    assert sum(M2_JOINT.values()) == 1
    assert px == {"bus": Fr(3, 8), "keke": Fr(3, 8), "walk": Fr(1, 4)} and py == {"early": Fr(1, 2), "late": Fr(1, 2)}
    hx, hy, hxy = H(px.values()), H(py.values()), H(M2_JOINT.values())
    i = hx + hy - hxy
    assert (round(hx, 4), round(hy, 4), round(hxy, 4), round(i, 4)) == (1.5613, 1.0, 2.5, 0.0613), (hx, hy, hxy, i)

    # Q6: alpha-beta
    v, log = alphabeta(M2_TREE)
    assert v == minimax(M2_TREE) == 12
    assert pruned(log) == [(0, 0, 1, 1), (0, 1, 1), (1, 0, 0, 1), (1, 1, 1)]
    assert len(leaves_seen(log)) == 10
    _, vals = backed_up(M2_TREE)
    assert (vals[(0,)], vals[(1,)]) == (7, 12)
    print("mock 2: all numbers check")
    return done, gen, path, log


def draw_mock_2(done, gen, path, log):
    on_path = set(path)
    lines = ['digraph { bgcolor="white"; pad=0.2; nodesep=0.15; ranksep=0.35;',
             f'node [shape=plaintext, fontname="{FONT}", fontsize=11];', f'edge [color="{INK}", arrowsize=0.6];']
    ids = {M2_PUZZLE: 'n0'}
    lines.append(f'n0 [label={puzzle_label(M2_PUZZLE, 0, manhattan(M2_PUZZLE), True)}];')
    for k, (a, b, g, h) in enumerate(gen, 1):
        ids[b] = f'n{k}'
        lines.append(f'n{k} [label={puzzle_label(b, g, h, b in on_path)}];')
        style = f' [color="{ORANGE}", penwidth=2.5]' if a in on_path and b in on_path else ''
        lines.append(f'{ids[a]} -> n{k}{style};')
    lines.append('}')
    save_dot('\n'.join(lines), 'mock2-8puzzle-astar.svg',
             'The A star search tree for Mock 2, using Manhattan distance: from 2 3 blank, 1 5 6, 4 7 8, the six-move '
             'solution path is shaded yellow and joined by orange arrows; every node on it has f equal to 6, and each '
             'node shows g, h and f', OUT)
    abvals = {e[1]: e[4] for e in log if e[0] == 'node'}
    draw_game_tree(M2_TREE, 'mock2-alphabeta.svg',
                   'The Mock 2 tree solved with alpha-beta: four levels MAX, MIN, MAX, MIN over sixteen leaves; the two MIN '
                   'nodes under the root are 7 and 12, so the root is 12; the fourth leaf (14), the MIN node over 1 and 3, '
                   'the tenth leaf (7) and the MIN node over 8 and 10 are pruned and greyed out',
                   values=abvals, pruned_paths=pruned(log), xgap=44)


# ---------- Mock 3 ----------

from svgkit import ACCENT, Svg, flowchart  # noqa: E402
from ai_checkpoints import best_first, true_costs, neighbours  # noqa: E402

M3_P = [2, 3, 3, 11, 12]
M3_Q = [6, 7, 7, 8, 8]
M3_X = 9
M3_UCS = {("S", "A"): 4, ("S", "B"): 1, ("A", "B"): 2, ("A", "C"): 5, ("B", "C"): 8,
          ("B", "D"): 4, ("C", "G"): 3, ("A", "G"): 12, ("D", "G"): 9}
M3_ASTAR = {("S", "A"): 1, ("S", "B"): 4, ("A", "B"): 2, ("A", "C"): 5,
            ("B", "C"): 1, ("B", "D"): 5, ("C", "G"): 3, ("D", "G"): 1}
M3_H = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "G": 0}
M3_LAND = [2, 5, 3, 4, 4, 4, 7, 9, 12, 5, 6, 6, 6, 4, 2]
M3_SOURCE = [Fr(1, 2), Fr(1, 4), Fr(1, 8), Fr(1, 8)]
M3_JOINT = {("rain", "jam"): Fr(3, 8), ("rain", "clear"): Fr(1, 8),
            ("dry", "jam"): Fr(1, 8), ("dry", "clear"): Fr(3, 8)}
M3_TREE = [[5, 9, 7], [2, 11, 8], [10, 4, 12]]


def gaussian(vals, x):
    m = sum(vals) / len(vals)
    v = sum((a - m) ** 2 for a in vals) / len(vals)
    return m, v, math.exp(-(x - m) ** 2 / (2 * v)) / math.sqrt(2 * math.pi * v)


def check_mock_3():
    # Q2: Gaussian versus Parzen window
    mp, vp, dp = gaussian(M3_P, M3_X)
    mq, vq, dq = gaussian(M3_Q, M3_X)
    assert (round(mp, 4), round(vp, 4), round(mq, 4), round(vq, 4)) == (6.2, 18.96, 7.2, 0.56)
    assert (round(dp, 4), round(dq, 4)) == (0.0745, 0.0295) and dp > dq          # Gaussian says P
    parzen = [sum(1 for a in c if M3_X - 1 <= a <= M3_X + 1) / (len(c) * 2) for c in (M3_P, M3_Q)]
    assert parzen == [0.0, 0.2]                                                    # Parzen says Q
    near = sorted([(abs(a - M3_X), "P") for a in M3_P] + [(abs(a - M3_X), "Q") for a in M3_Q])[:2]
    assert near == [(1, "Q"), (1, "Q")] and min(abs(a - M3_X) for a in M3_P) == 2    # nearest points are Q's 8s

    # Q3: uniform-cost search, and iterative deepening counts
    assert best_first(M3_UCS, "S", "G", lambda g, n: g) == (list("SBADCG"), 11, list("SBACG"))
    assert sum((3 - k + 1) * 5 ** k for k in range(1, 4)) == 190 and sum(5 ** k for k in range(1, 4)) == 155

    # Q4: greedy versus A*, h admissible and consistent; the landscape; annealing
    tc = true_costs(M3_ASTAR, "G")
    nb = neighbours(M3_ASTAR)
    assert all(M3_H[n] <= tc[n] for n in tc) and all(M3_H[a] <= w + M3_H[b] for a in nb for b, w in nb[a].items())
    assert best_first(M3_ASTAR, "S", "G", lambda g, n: M3_H[n]) == (list("SBDG"), 10, list("SBDG"))
    assert best_first(M3_ASTAR, "S", "G", lambda g, n: g + M3_H[n]) == (list("SABCG"), 7, list("SABCG"))
    L = M3_LAND
    is_peak = [all(L[i] >= L[j] for j in (i - 1, i + 1) if 0 <= j < len(L)) for i in range(len(L))]
    assert [i for i, p in enumerate(is_peak) if p] == [1, 3, 4, 8, 10, 11, 12]   # where plain hill climbing stops (3, 4: the shoulder)
    assert L.index(max(L)) == 8 and L[3:6] == [4, 4, 4] and L[6] > 4 and L[2] < 4     # shoulder at 3-5
    assert L[10:13] == [6, 6, 6] and L[9] < 6 and L[13] < 6                         # flat local maximum
    assert (round(math.exp(-3 / 5), 4), round(math.exp(-3 / 1), 4)) == (0.5488, 0.0498)

    # Q5: entropy
    assert H(M3_SOURCE) == 1.75
    px = {"rain": Fr(1, 2), "dry": Fr(1, 2)}
    hxy = H(M3_JOINT.values())
    assert sum(M3_JOINT.values()) == 1 and round(hxy, 4) == 1.8113
    assert round(hxy - H(px.values()), 4) == 0.8113                     # H(Y|X)
    assert round(1 + 1 - hxy, 4) == 0.1887                              # I(X;Y), with H(X) = H(Y) = 1

    # Q6: minimax and alpha-beta
    v, log = alphabeta(M3_TREE)
    assert v == minimax(M3_TREE) == 5
    assert pruned(log) == [(1, 1), (1, 2), (2, 2)] and leaves_seen(log) == [5, 9, 7, 2, 10, 4]
    print("mock 3: all numbers check")
    return log


def draw_mock_3(log):
    flowchart([('Scanner captures the fingerprint', 'data'),
               ('Preprocessing: enhance contrast, binarise, thin the ridges', 'prog'),
               ('Feature extraction: minutiae (ridge endings and bifurcations)', 'prog'),
               ('Matching against each student\'s enrolled template', 'prog'),
               ('Decision: match, mark present; no match, scan again', 'prog'),
               ('Attendance record saved and reported to the lecturer', 'fixed')], 'mock3-fingerprint-system.svg',
              'A fingerprint attendance system as a block diagram: a scanner captures the print; preprocessing enhances, binarises '
              'and thins the ridges; feature extraction finds the minutiae; the minutiae are matched against each student\'s '
              'enrolled template; a match marks the student present, no match asks for another scan; the attendance record is '
              'saved and reported to the lecturer', OUT)
    title = ('A landscape over states 0 to 14 with values 2, 5, 3, 4, 4, 4, 7, 9, 12, 5, 6, 6, 6, 4, 2: a local maximum of 5 '
             'at state 1, a shoulder (a flat stretch of 4 at states 3 to 5 that rises again), the global maximum 12 at state 8, '
             'and a flat local maximum of 6 at states 10 to 12')
    s = Svg(700, 300, title)
    x0, y0, dx, dy = 40, 250, 44, 16
    s.line(x0 - 10, y0, x0 + 14 * dx + 20, y0)
    pts = [(x0 + i * dx, y0 - v * dy) for i, v in enumerate(M3_LAND)]
    s.path('M ' + ' L '.join(f'{x:.0f} {y:.0f}' for x, y in pts), ACCENT, width=3)
    for i, (x, y) in enumerate(pts):
        s.circle(x, y, 5, ACCENT)
        s.text(x, y - 10, M3_LAND[i], size=12)
        s.text(x, y0 + 18, i, size=12, color='#374151')
    for i, t in ((1, 'local max'), (4, 'shoulder'), (8, 'global max'), (11, 'flat local max')):
        x, y = pts[i]
        s.text(x, y - 28, t, size=12, color='#b45309', weight='bold')
    s.save('mock3-landscape.svg', OUT)
    abvals = {e[1]: e[4] for e in log if e[0] == 'node'}
    draw_game_tree(M3_TREE, 'mock3-alphabeta.svg',
                   'The Mock 3 tree solved with alpha-beta: a MAX root over three MIN nodes with leaves 5, 9, 7; 2, 11, 8; and '
                   '10, 4, 12; the MIN nodes are 5, 2 and 4, so the root is 5; the leaves 11 and 8 under the second MIN node '
                   'and the leaf 12 under the third are pruned and greyed out',
                   values=abvals, pruned_paths=pruned(log), xgap=60)


if __name__ == "__main__":
    draw_mock_2(*check_mock_2())
    draw_mock_3(check_mock_3())
