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


# ---------- Mock 4 ----------

from ai_question_bank import nim_value, nim_moves  # noqa: E402

M4_A = [(1, 1), (2, 2), (5, 4)]
M4_B = [(4, 6), (6, 5), (6, 7)]
M4_NEW = (4, 4)
M4_SCORES = [(0.95, 1), (0.9, 1), (0.8, 0), (0.7, 1), (0.6, 1), (0.5, 0), (0.4, 1), (0.3, 0), (0.2, 0), (0.1, 0)]
M4_CONFUSION = {"TP": 30, "FN": 10, "FP": 20, "TN": 40}
M4_GRAPH = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"], "D": ["B", "C", "E"], "E": ["D"]}
M4_PUZZLE = (1, 2, 3, 7, 4, 6, 0, 5, 8)        # rows 1 2 3 / 7 4 6 / _ 5 8
M4_RAW = {("morning", "attend"): Fr(3, 8), ("morning", "absent"): Fr(1, 8),
          ("afternoon", "attend"): Fr(1, 8), ("afternoon", "absent"): Fr(1, 8),
          ("evening", "attend"): Fr(1, 8), ("evening", "absent"): Fr(0)}


def jugs53():
    start, par, q = (0, 0), {(0, 0): None}, deque([(0, 0)])
    while q:
        a, b = s = q.popleft()
        if a == 4:
            path = []
            while s is not None:
                path.append(s)
                s = par[s]
            return path[::-1]
        pab, pba = min(a, 3 - b), min(b, 5 - a)
        for t in ((5, b), (a, 3), (0, b), (a, 0), (a - pab, b + pab), (a + pba, b - pba)):
            if t not in par:
                par[t] = s
                q.append(t)


def graph_bfs(g, start):
    order, seen, q = [], {start}, deque([start])
    while q:
        n = q.popleft()
        order.append(n)
        for m in g[n]:
            if m not in seen:
                seen.add(m)
                q.append(m)
    return order


def graph_dfs(g, start):
    order = []

    def go(n):
        order.append(n)
        for m in g[n]:
            if m not in order:
                go(m)
    go(start)
    return order


def roc_points(scored):
    P = sum(1 for _, y in scored if y)
    N = len(scored) - P
    pts, tp, fp = [(0.0, 0.0)], 0, 0
    for _, y in sorted(scored, reverse=True):
        if y:
            tp += 1
        else:
            fp += 1
        pts.append((fp / N, tp / P))
    auc = sum((x2 - x1) * (y1 + y2) / 2 for (x1, y1), (x2, y2) in zip(pts, pts[1:]))
    return pts, auc


def check_mock_4():
    # Q1: KNN
    pts = [(p, "A") for p in M4_A] + [(p, "B") for p in M4_B]
    ds = sorted((dist(M4_NEW, p), c) for p, c in pts)
    assert [(round(d, 3), c) for d, c in ds[:4]] == [(1.0, "A"), (2.0, "B"), (2.236, "B"), (2.828, "A")]
    k1, k3 = ds[0][1], max("AB", key=lambda c: sum(1 for _, x in ds[:3] if x == c))
    assert (k1, k3) == ("A", "B")

    # Q2: ROC and kappa
    roc, auc = roc_points(M4_SCORES)
    assert round(auc, 2) == 0.84, auc
    c = M4_CONFUSION
    n = sum(c.values())
    po = Fr(c["TP"] + c["TN"], n)
    ap, pp = c["TP"] + c["FN"], c["TP"] + c["FP"]
    pe = Fr(ap * pp + (n - ap) * (n - pp), n * n)
    assert (po, pe) == (Fr(7, 10), Fr(1, 2)) and (po - pe) / (1 - pe) == Fr(2, 5)

    # Q3: BFS and DFS on the small graph
    assert graph_bfs(M4_GRAPH, "A") == list("ABCDE") and graph_dfs(M4_GRAPH, "A") == list("ABDCE")

    # Q4: puzzle heuristics, jugs, genetic algorithm
    assert (misplaced(M4_PUZZLE), manhattan(M4_PUZZLE)) == (4, 4), (misplaced(M4_PUZZLE), manhattan(M4_PUZZLE))
    jug = jugs53()
    assert len(jug) - 1 == 6 and jug[-1][0] == 4, jug
    pop = {"11001": 25, "01010": 10, "10100": 20, "00111": 7}
    assert all(int(k, 2) == v for k, v in pop.items()) and sum(pop.values()) == 62
    assert round(25 / 62, 4) == 0.4032
    a, b = "11001", "10100"
    assert (a[:3] + b[3:], b[:3] + a[3:]) == ("11000", "10101")

    # Q5: a broken table, normalised
    tot = sum(M4_RAW.values())
    assert tot == Fr(7, 8)
    joint = {k: v / tot for k, v in M4_RAW.items()}
    px, py = {}, {}
    for (x, y), p in joint.items():
        px[x] = px.get(x, 0) + p
        py[y] = py.get(y, 0) + p
    assert px == {"morning": Fr(4, 7), "afternoon": Fr(2, 7), "evening": Fr(1, 7)}
    assert py == {"attend": Fr(5, 7), "absent": Fr(2, 7)}
    hx, hy, hxy = H(px.values()), H(py.values()), H(joint.values())
    i = hx + hy - hxy
    assert (round(hx, 4), round(hy, 4), round(hxy, 4), round(i, 4)) == (1.3788, 0.8631, 2.1281, 0.1138), (hx, hy, hxy, i)

    # Q6: Nim from 6, MAX first
    assert nim_value((6,), "MAX") == 1 and nim_moves((6,)) == [(5, 1), (4, 2)]
    print("mock 4: all numbers check")
    return roc, auc


def draw_mock_4(roc, auc):
    # Q1: classification versus clustering
    s = Svg(640, 300, 'Classification versus clustering. Left, classification: the training points carry labels, '
                      'class A as blue circles and class B as orange squares, and the classifier learns a boundary '
                      'between them. Right, clustering: the same kind of points with no labels, grouped into two '
                      'clusters by similarity alone, each circled')
    for ox, title in ((20, 'Classification: labelled, learn a boundary'), (330, 'Clustering: unlabelled, find groups')):
        s.rect(ox, 40, 290, 230, '#ffffff', stroke='#d1d5db')
        s.text(ox + 145, 28, title, size=13, weight='bold')
    A = [(1, 1), (1.5, 2.2), (2.3, 1.4), (2.6, 2.6), (1.2, 3.0)]
    B = [(5, 5), (5.6, 4.1), (4.4, 5.8), (6.0, 5.6), (5.1, 6.4)]

    def P(ox, x, y):
        return ox + 20 + x * 37, 260 - y * 30
    for x, y in A:
        px_, py_ = P(20, x, y)
        s.circle(px_, py_, 6, BLUE)
    for x, y in B:
        px_, py_ = P(20, x, y)
        s.rect(px_ - 6, py_ - 6, 12, 12, ORANGE_C)
    a1, a2 = P(20, 0.3, 6.6), P(20, 6.8, 0.6)
    s.line(a1[0], a1[1], a2[0], a2[1], color=INK, width=2, dash='6 4')
    s.text(a2[0] - 4, a2[1] - 10, 'boundary', size=11.5, anchor='end')
    s.text(P(20, 1.8, 0)[0], 262, 'class A', size=11.5, color=BLUE, weight='bold')
    s.text(P(20, 5.3, 0)[0], 262, 'class B', size=11.5, color=ORANGE_C, weight='bold')
    for x, y in A + B:
        px_, py_ = P(330, x, y)
        s.circle(px_, py_, 6, '#9ca3af')
    for (cx, cy), lab in (((1.85, 2.05), 'cluster 1'), ((5.25, 5.4), 'cluster 2')):
        px_, py_ = P(330, cx, cy)
        s.add(f'<ellipse cx="{px_:.1f}" cy="{py_:.1f}" rx="52" ry="44" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 4"/>')
        s.text(px_, py_ + 60, lab, size=11.5, weight='bold')
    s.save('mock4-classify-vs-cluster.svg', OUT)

    # Q2: ROC curve
    s = Svg(420, 380, f'An ROC curve for a classifier scored on ten cases: the curve steps from (0, 0) up and to the right to '
                      f'(1, 1), staying well above the dashed diagonal of random guessing; the area under it is {auc:.2f}')
    ox, oy, W = 70, 320, 280
    s.line(ox, oy, ox + W, oy, width=1.5)
    s.line(ox, oy, ox, oy - W, width=1.5)
    for k in range(0, 6):
        v = k / 5
        s.text(ox + v * W, oy + 18, f'{v:.1f}', size=11, color=GREY)
        s.text(ox - 8, oy - v * W + 4, f'{v:.1f}', size=11, color=GREY, anchor='end')
    s.text(ox + W / 2, oy + 40, 'false positive rate', size=12.5, weight='bold')
    s.add(f'<text x="{ox - 44}" y="{oy - W / 2}" transform="rotate(-90 {ox - 44} {oy - W / 2})" '
          f'font-family="{FONT}" font-size="12.5" font-weight="bold" text-anchor="middle" fill="{INK}">true positive rate</text>')
    s.line(ox, oy, ox + W, oy - W, color=GREY, width=1.5, dash='5 4')
    s.text(ox + W * 0.72, oy - W * 0.62, 'random guessing (area 0.5)', size=11, color=GREY, anchor='start')
    xy = ' '.join(f'{ox + x * W:.1f},{oy - y * W:.1f}' for x, y in roc)
    s.add(f'<polygon points="{ox},{oy} {xy} {ox + W},{oy}" fill="{BLUE}" fill-opacity="0.12"/>')
    s.add(f'<polyline points="{xy}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
    s.text(ox + W * 0.45, oy - W * 0.3, f'area under curve = {auc:.2f}', size=12.5, color=BLUE, weight='bold')
    s.save('mock4-roc.svg', OUT)

    # Q3: state space versus search tree
    lines = ['digraph { bgcolor="white"; pad=0.2; compound=true; nodesep=0.3; ranksep=0.4;',
             f'node [fontname="{FONT}", fontsize=13, shape=circle, style=filled, fillcolor="#dbeafe", color="{INK}", width=0.4];',
             f'edge [color="{INK}", arrowhead=none];',
             'subgraph cluster_g { label="State space: 5 states"; fontname="' + FONT + '"; fontsize=13; color="#d1d5db";',
             'A; B; C; D; E; A -> B; A -> C; B -> D; C -> D; D -> E; }',
             'subgraph cluster_t { label="Search tree to depth 3: states repeat"; fontname="' + FONT + '"; fontsize=13; color="#d1d5db";']
    tree, ids = [], {}

    def grow(n, depth, path):
        nid = f't{len(ids)}'
        ids[nid] = n
        fill = '#fde68a' if n in path else '#dbeafe'
        lines.append(f'{nid} [label="{n}", fillcolor="{fill}"];')
        if depth < 3:
            for m in M4_GRAPH[n]:
                cid = grow(m, depth + 1, path + [n])
                lines.append(f'{nid} -> {cid};')
        return nid
    grow("A", 0, [])
    lines.append('} }')
    counts = {}
    for v in ids.values():
        counts[v] = counts.get(v, 0) + 1
    assert len(ids) == 17 and (counts["A"], counts["B"], counts["C"]) == (3, 5, 5), (len(ids), counts)
    save_dot('\n'.join(lines), 'mock4-space-vs-tree.svg',
             'Left: a state space of five states, A joined to B and C, B and C both joined to D, and D joined to E. '
             'Right: the search tree from A down to depth 3 has 17 nodes, because the same state appears once for every '
             'path to it: A appears 3 times and B and C 5 times each; nodes repeating a state already on their own path are shaded '
             'yellow', OUT)

    # Q6: Nim from 6, MAX first
    lines = ['digraph { bgcolor="white"; pad=0.2; nodesep=0.3; ranksep=0.45;',
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
    add((6,), 'MAX')
    lines.append('}')
    assert len(seen) == 8, len(seen)
    save_dot('\n'.join(lines), 'mock4-nim.svg',
             'The Nim game tree from one stack of 6, MAX to move first: 6 splits to 5-1 or 4-2; 5-1 splits to 4-1-1 or '
             '3-2-1, and 4-2 to 3-2-1; 4-1-1 leads to 3-1-1-1 and then the terminal 2-1-1-1-1, while 3-2-1 leads to the '
             'terminal 2-2-1-1. Each state shows whose turn it is and its minimax value; the root value is 1, so MAX wins', OUT)


ORANGE_C = '#f59e0b'
BLUE = '#2563eb'
GREY = '#6b7280'


if __name__ == "__main__":
    draw_mock_2(*check_mock_2())
    draw_mock_3(check_mock_3())
    draw_mock_4(*check_mock_4())
