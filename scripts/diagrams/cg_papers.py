"""Solve the computer-graphics papers: question bank, checkpoints and mock exams.

    python3 scripts/diagrams/cg_papers.py      # run from the vault root

Every number in computer-graphics/question-bank.md, checkpoint-1..3.md and
mock-exam-1..3.md is computed here with the methods the lessons teach, and
asserted, so a typo in a paper fails this script. It also draws the answer
pictures for the drawing questions (files prefixed paper-).
Output: computer-graphics/images/paper-*.svg.
"""
import math
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, GRID, PIX, TRUE, ACCENT, Svg  # noqa: E402
from computer_graphics import (Axes, PixelGrid, ORANGE, OUT, bresenham_trace,  # noqa: E402
                               bresenham_with_p, dda_points, half_up, outline)

GREY = '#9aa5b1'
PURPLE = '#7c3aed'


def close(a, b, eps=5e-3):
    if isinstance(a, (tuple, list)):
        return len(a) == len(b) and all(close(x, y, eps) for x, y in zip(a, b))
    return abs(a - b) <= eps


def r3(v):
    return tuple(round(float(x), 3) for x in v) if isinstance(v, (tuple, list)) else round(float(v), 3)


# ---------- maths, as the lessons state it ----------

def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def row_apply(p, M):
    """Row-vector convention: [x y 1] M, then divide by w."""
    v = [p[0], p[1], 1]
    x, y, w = (sum(v[k] * M[k][j] for k in range(3)) for j in range(3))
    return (x / w, y / w)


def col_apply(M, p):
    v = list(p) + [1]
    out = [sum(M[i][k] * v[k] for k in range(len(v))) for i in range(len(v))]
    return tuple(o / out[-1] for o in out[:-1])


def rot_row(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, s, 0], [-s, c, 0], [0, 0, 1]]


def T2_row(tx, ty):
    return [[1, 0, 0], [0, 1, 0], [tx, ty, 1]]


def S2_row(sx, sy):
    return [[sx, 0, 0], [0, sy, 0], [0, 0, 1]]


def T3(tx, ty, tz):
    return [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]]


def S3(sx, sy, sz):
    return [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]]


def Rz3(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def cubic(P, t):
    a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t ** 2 * (1 - t), t ** 3
    return tuple(a * P[0][i] + b * P[1][i] + c * P[2][i] + d * P[3][i] for i in range(len(P[0])))


def quad(P, t):
    a, b, c = (1 - t) ** 2, 2 * t * (1 - t), t ** 2
    return tuple(a * P[0][i] + b * P[1][i] + c * P[2][i] for i in range(len(P[0])))


def lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def casteljau(P, t):
    levels = [list(P)]
    while len(levels[-1]) > 1:
        prev = levels[-1]
        levels.append([lerp(prev[i], prev[i + 1], t) for i in range(len(prev) - 1)])
    return levels


def split(P, t):
    L = casteljau(P, t)
    return [lv[0] for lv in L], [lv[-1] for lv in reversed(L)]


def end_conditions(p0, v0, p3, v1):
    p1 = tuple(a + b / F(3) for a, b in zip(p0, v0))
    p2 = tuple(a - b / F(3) for a, b in zip(p3, v1))
    return [tuple(p0), p1, p2, tuple(p3)]


def code(p, win):
    xmin, ymin, xmax, ymax = win
    x, y = p
    return ('1' if y > ymax else '0') + ('1' if y < ymin else '0') + ('1' if x > xmax else '0') + ('1' if x < xmin else '0')


def cohen_sutherland(p1, p2, win):
    """Returns (codes at the start, result) where result is None (rejected) or the clipped segment."""
    xmin, ymin, xmax, ymax = win
    start = (code(p1, win), code(p2, win))
    a, b = tuple(map(F, p1)), tuple(map(F, p2))
    while True:
        ca, cb = code(a, win), code(b, win)
        if ca == cb == '0000':
            return start, (a, b)
        if int(ca, 2) & int(cb, 2):
            return start, None
        out = ca if ca != '0000' else cb
        (x1, y1), (x2, y2) = a, b
        if out[0] == '1':
            x, y = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1), ymax
        elif out[1] == '1':
            x, y = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1), ymin
        elif out[2] == '1':
            x, y = xmax, y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
        else:
            x, y = xmin, y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
        if out == ca:
            a = (x, y)
        else:
            b = (x, y)


def liang_barsky(p0, p1, win):
    xmin, ymin, xmax, ymax = win
    dx, dy = F(p1[0] - p0[0]), F(p1[1] - p0[1])
    ps = [-dx, dx, -dy, dy]
    qs = [F(p0[0] - xmin), F(xmax - p0[0]), F(p0[1] - ymin), F(ymax - p0[1])]
    tE, tL = F(0), F(1)
    for p, q in zip(ps, qs):
        if p == 0:
            if q < 0:
                return ps, qs, None, None, None
        elif p < 0:
            tE = max(tE, q / p)
        else:
            tL = min(tL, q / p)
    if tE > tL:
        return ps, qs, tE, tL, None
    pt = lambda t: (p0[0] + t * dx, p0[1] + t * dy)  # noqa: E731
    return ps, qs, tE, tL, (pt(tE), pt(tL))


def midpoint_circle_trace(r):
    """The first octant from (0, r), with p before each step, as note 09 tabulates it."""
    x, y, p = 0, r, 1 - r
    rows = [(x, y, p)]
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * x + 1 - 2 * y
        if x > y:
            break
        rows.append((x, y, p))
    return rows


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(v):
    m = math.sqrt(dot(v, v))
    return tuple(x / m for x in v)


def seg_distance(p, a, b):
    ab = (b[0] - a[0], b[1] - a[1])
    t = dot((p[0] - a[0], p[1] - a[1]), ab) / dot(ab, ab)
    t = max(0, min(1, t))
    q = (a[0] + t * ab[0], a[1] + t * ab[1])
    return t, q, math.dist(p, q)


SQ3 = math.sqrt(3) / 2


# ---------- pictures ----------

def grid_pic(pts, cols, rows, name, title, line=None, ox=0, oy=0, cell=26):
    s = Svg(60 + cols * cell, 50 + rows * cell, title)
    g = PixelGrid(s, cols, rows, cell, left=40, top=15)
    for i in range(cols + 1):
        s.line(g.left + i * cell, g.top, g.left + i * cell, g.top + rows * cell, GRID, 1)
    for j in range(rows + 1):
        s.line(g.left, g.top + j * cell, g.left + cols * cell, g.top + j * cell, GRID, 1)
    for x in range(cols):
        s.text(g.px(x), g.top + rows * cell + 15, str(x + ox), 10)
    for y in range(rows):
        s.text(g.left - 8, g.py(y) + 4, str(y + oy), 10, anchor='end')
    for x, y in pts:
        g.pixel(x - ox, y - oy)
    if line:
        (a, b), (c, d) = line
        g.true_line(a - ox, b - oy, c - ox, d - oy)
    s.save(name, OUT)


def panels(shapes, name, title, xr, yr, sc=30, inner=None):
    """shapes: list of (panel title, ghost pts, image pts, point labels).
    inner: optional list, per panel, of (ghost segment, image segment) pairs, such as a square's dividing lines."""
    n = len(shapes)
    w_one = (xr[1] - xr[0]) * sc + 50
    s = Svg(w_one * n + 10, (yr[1] - yr[0]) * sc + 75, title)
    for i, (ptitle, ghost, img, labs) in enumerate(shapes):
        A = Axes(s, 35 + i * w_one, 30 + (yr[1] - yr[0]) * sc, sc, xr, yr)
        A.seg((xr[0], 0), (xr[1], 0), GREY, 1)
        A.seg((0, yr[0]), (0, yr[1]), GREY, 1)
        A.poly(ghost, GREY, 1.5, dash='4 3')
        A.poly(img, ACCENT, 2.5, fill='#d1fae5')
        for gseg, iseg in (inner[i] if inner else []):
            A.seg(*gseg, GREY, 1, '4 3')
            A.seg(*iseg, ACCENT, 1.8)
        for p, lab in zip(img, labs):
            A.dot(p, ACCENT, 3.5)
            A.label(p, lab, 6, -6, INK, 'start', 11, 'bold')
        s.text(35 + i * w_one + (xr[1] - xr[0]) * sc / 2, 18, ptitle, 13, INK, weight='bold')
    s.save(name, OUT)


def clip_pic(win, lines, name, title, xr, yr, sc=28):
    s = Svg((xr[1] - xr[0]) * sc + 70, (yr[1] - yr[0]) * sc + 55, title)
    A = Axes(s, 40, 20 + (yr[1] - yr[0]) * sc, sc, xr, yr)
    xmin, ymin, xmax, ymax = win
    A.poly([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)], INK, 2, fill='#eff6ff')
    for lab, p, q, res in lines:
        A.seg(p, q, GREY, 1.5, '4 3')
        if res:
            A.seg(res[0], res[1], ACCENT, 3.5)
        A.label(p, lab, -4, -6, INK, 'end', 11, 'bold')
    s.save(name, OUT)


def curve_pic(P, name, title, xr, yr, extra=(), sc=40, labels=None):
    s = Svg((xr[1] - xr[0]) * sc + 70, (yr[1] - yr[0]) * sc + 55, title)
    A = Axes(s, 40, 20 + (yr[1] - yr[0]) * sc, sc, xr, yr)
    A.poly(P, GREY, 1.5, close=False, dash='5 4')
    pts = [cubic(P, i / 80) for i in range(81)]
    A.poly(pts, TRUE, 2.5, close=False)
    for i, p in enumerate(P):
        A.dot(p, INK, 4)
        A.label(p, (labels or [f'P{i}' for i in range(4)])[i], 7, -7, INK, 'start', 12, 'bold')
    for p, lab, col in extra:
        A.dot(p, col, 4.5)
        A.label(p, lab, 7, 15, col, 'start', 11, 'bold')
    s.save(name, OUT)


# ======================================================================
# MOCK EXAM 1: the real SSG 511 2025/26 paper
# ======================================================================

def mock1():
    # Q1(b): Bresenham, m > 1, A(1,1) to B(3,11)
    pts, ps, moved = bresenham_trace(1, 1, 3, 11)
    assert ps == [-6, -2, 2, -14, -10, -6, -2, 2, -14, -10], ps
    assert pts == [(1, 1), (1, 2), (1, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (3, 9), (3, 10), (3, 11)], pts
    bresenham_with_p(1, 1, 3, 11, 8, 12, 24, 'paper-m1-bresenham-1-1-to-3-11.svg',
                     'Bresenham from (1,1) to (3,11), slope 5: y steps every time; p is written beside each row and '
                     'x moves only on the rows outlined in orange, where p was 0 or more',
                     pts, ps, offset=(0, 0), left=40)

    # Q1(c): the particle. P0=(0,0,0), P3=(4,0,2), v0=(6,0,0), v1=(0,0,3)
    P = end_conditions((0, 0, 0), (6, 0, 0), (4, 0, 2), (0, 0, 3))
    assert P == [(0, 0, 0), (2, 0, 0), (4, 0, 1), (4, 0, 2)], P
    assert cubic(P, F(1, 2)) == (F(11, 4), 0, F(5, 8))           # (2.75, 0, 0.625)
    for t in (F(0), F(1, 3), F(1, 2), F(1)):                       # x = 6t - 2t^3, z = 3t^2 - t^3
        x, _, z = cubic(P, t)
        assert x == 6 * t - 2 * t ** 3 and z == 3 * t ** 2 - t ** 3
    first, second = split(P, F(1, 2))
    assert first == [(0, 0, 0), (1, 0, 0), (2, 0, F(1, 4)), (F(11, 4), 0, F(5, 8))], first
    # B1(t) = B(t/2) agrees with the first-half curve
    for t in (F(1, 4), F(3, 5)):
        assert cubic(first, t) == cubic(P, t / 2)

    # Q2: the subdivided square, row vectors
    pts = {'A': (-1, -1), 'B': (-1, 1), 'C': (1, 1), 'D': (1, -1)}
    mids = {'top': (0, 1), 'bottom': (0, -1), 'left': (-1, 0), 'right': (1, 0), 'centre': (0, 0)}
    Ma = rot_row(60)
    Mb = [[1, 0, 0], [1, 3, 0], [0, 0, 1]]
    Mc = [[1, 0, 0.5], [0, 1, 0], [0, 0, 1]]
    ia = {k: r3(row_apply(p, Ma)) for k, p in pts.items()}
    assert ia == {'A': (0.366, -1.366), 'B': (-1.366, -0.366), 'C': (-0.366, 1.366), 'D': (1.366, 0.366)}, ia
    ib = {k: r3(row_apply(p, Mb)) for k, p in pts.items()}
    assert ib == {'A': (-2, -3), 'B': (0, 3), 'C': (2, 3), 'D': (0, -3)}, ib
    ic = {k: r3(row_apply(p, Mc)) for k, p in pts.items()}
    assert ic == {'A': (-2, -2), 'B': (-2, 2), 'C': (0.667, 0.667), 'D': (0.667, -0.667)}, ic
    assert {k: r3(row_apply(p, Mb)) for k, p in mids.items()} == {
        'top': (1, 3), 'bottom': (-1, -3), 'left': (-1, 0), 'right': (1, 0), 'centre': (0, 0)}
    assert {k: r3(row_apply(p, Mc)) for k, p in mids.items()} == {
        'top': (0, 1), 'bottom': (0, -1), 'left': (-2, 0), 'right': (0.667, 0), 'centre': (0, 0)}
    order = ['A', 'B', 'C', 'D']
    ghost = [pts[k] for k in order]
    divs = [((0, -1), (0, 1)), ((-1, 0), (1, 0))]
    inner = [[(d, tuple(row_apply(q, M) for q in d)) for d in divs] for M in (Ma, Mb, Mc)]
    panels([('(a) rotate 60°', ghost, [row_apply(pts[k], Ma) for k in order], ["A'", "B'", "C'", "D'"]),
            ('(b) x + y, 3y', ghost, [row_apply(pts[k], Mb) for k in order], ["A'", "B'", "C'", "D'"]),
            ('(c) divide by 1 + 0.5x', ghost, [row_apply(pts[k], Mc) for k in order], ["A'", "B'", "C'", "D'"])],
           'paper-m1-q2-square.svg',
           'The square A(-1,-1), B(-1,1), C(1,1), D(1,-1), dashed grey, and its image in green under each matrix, '
           'with row vectors: (a) turned 60 degrees anticlockwise about the origin; (b) sheared to (x + y, 3y), a '
           'parallelogram from y = -3 to 3; (c) divided by w = 1 + 0.5x, so the left side grows to x = -2 and the '
           'right side shrinks to x = 0.667, a trapezium; the two dividing lines go with it',
           (-3, 3), (-3, 4), sc=26, inner=inner)

    # Q4: the cone. Column vectors: M = T(1,4,-3) Rz(135) S(2, 2*sqrt2, 2)
    k = 2 * math.sqrt(2)
    M = matmul(T3(1, 4, -3), matmul(Rz3(135), S3(2, k, 2)))
    assert close(col_apply(M, (0, 1, 0)), (-1, 2, -3)) and close(col_apply(M, (0, 0, 0)), (1, 4, -3))
    assert close(col_apply(M, (0.5, 0, 0)), (1 - 0.707, 4 + 0.707, -3))      # base rim: radius 1 now
    assert close(math.dist(col_apply(M, (0.5, 0, 0)), (1, 4, -3)), 1)
    assert close(math.dist(col_apply(M, (0, 0, 0.5)), (1, 4, -3)), 1)
    want = [[-1.414, -2, 0, 1], [1.414, -2, 0, 4], [0, 0, 2, -3], [0, 0, 0, 1]]
    assert close(M, want), M

    # Q5(b): Cohen-Sutherland, window A(-3,1) to C(2,6)
    win = (-3, 1, 2, 6)
    lines = [('P1P2', (-6, 1), (-4, 5)), ('P3P4', (-4, 2), (-1, 7)), ('P5P6', (-2, 3), (1, 2)),
             ('P7P8', (0, 7), (3, 2)), ('P9P10', (4, 5), (5, 2))]
    res = {lab: cohen_sutherland(p, q, win) for lab, p, q in lines}
    assert res['P1P2'] == (('0001', '0001'), None)
    assert res['P3P4'][0] == ('0001', '1000') and close(res['P3P4'][1], ((-3, 3.667), (-1.6, 6)))
    assert res['P5P6'] == (('0000', '0000'), ((-2, 3), (1, 2)))
    assert res['P7P8'][0] == ('1000', '0010') and close(res['P7P8'][1], ((0.6, 6), (2, 3.667)))
    assert res['P9P10'] == (('0010', '0010'), None)
    clip_pic(win, [(lab, p, q, res[lab][1]) for lab, p, q in lines], 'paper-m1-q5-clipping.svg',
             'The window from (-3,1) to (2,6) with the five lines dashed; the kept parts in green: P3P4 from (-3, 3.67) '
             'to (-1.6, 6), all of P5P6, and P7P8 from (0.6, 6) to (2, 3.67); P1P2 and P9P10 are rejected',
             (-7, 6), (0, 8))

    # Q6: the program's three use cases
    assert bresenham_trace(2, 8, 4, 2)[0] == [(2, 8), (2, 7), (3, 6), (3, 5), (3, 4), (4, 3), (4, 2)]
    assert bresenham_trace(5, 0, 5, 4)[0] == [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4)]
    print('mock 1 ok')


# ======================================================================
# MOCK EXAM 2
# ======================================================================

def mock2():
    # Q1(b): Bresenham 0 < m < 1, A(2,3) to B(12,7)
    pts, ps, moved = bresenham_trace(2, 3, 12, 7)
    assert ps == [-2, 6, -6, 2, -10, -2, 6, -6, 2, -10], ps
    assert pts == [(2, 3), (3, 3), (4, 4), (5, 4), (6, 5), (7, 5), (8, 5), (9, 6), (10, 6), (11, 7), (12, 7)], pts
    bresenham_with_p(2, 3, 12, 7, 11, 5, 30, 'paper-m2-bresenham-2-3-to-12-7.svg',
                     'Bresenham from (2,3) to (12,7), slope 0.4: x steps every time; p is written under each column '
                     'and y moves only on the columns outlined in orange, where p was 0 or more',
                     pts, ps, offset=(2, 3))

    # Q1(c): particle in 2D. P0=(1,2), v0=(9,3); P3=(10,2), v1=(3,-6)
    P = end_conditions((1, 2), (9, 3), (10, 2), (3, -6))
    assert P == [(1, 2), (4, 3), (9, 4), (10, 2)], P
    assert cubic(P, F(1, 2)) == (F(25, 4), F(25, 8))              # (6.25, 3.125)
    first, second = split(P, F(1, 2))
    assert second == [(F(25, 4), F(25, 8)), (8, F(13, 4)), (F(19, 2), 3), (10, 2)], second
    L = casteljau(P, F(1, 2))
    assert L[1] == [(F(5, 2), F(5, 2)), (F(13, 2), F(7, 2)), (F(19, 2), 3)] and L[2] == [(F(9, 2), 3), (8, F(13, 4))]
    for t in (F(1, 4), F(2, 3)):
        assert cubic(second, t) == cubic(P, (1 + t) / 2)
    curve_pic(P, 'paper-m2-q1c-particle.svg',
              'The particle path: control points P0(1,2), P1(4,3), P2(9,4), P3(10,2) with the control polygon dashed; '
              'the curve leaves P0 towards P1 and arrives at P3 from P2, passing B(1/2) = (6.25, 3.125)',
              (0, 11), (0, 5), extra=[((6.25, 3.125), 'B(½)', ACCENT)], sc=40)

    # Q2: triangle P(1,1), Q(4,1), R(1,3), row vectors
    tri = [(1, 1), (4, 1), (1, 3)]
    Ma = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
    Mb = [[1, 0, 0], [0.5, 1, 0], [0, 0, 1]]
    Mc = [[-1, 0, 0], [0, 1, 0], [4, 0, 1]]
    assert [row_apply(p, Ma) for p in tri] == [(1, 1), (1, 4), (3, 1)]
    assert [row_apply(p, Mb) for p in tri] == [(1.5, 1), (4.5, 1), (2.5, 3)]
    assert [row_apply(p, Mc) for p in tri] == [(3, 1), (0, 1), (3, 3)]
    labs = ["P'", "Q'", "R'"]
    panels([('(a) swap x and y', tri, [row_apply(p, Ma) for p in tri], labs),
            ('(b) x + 0.5y', tri, [row_apply(p, Mb) for p in tri], labs),
            ('(c) 4 − x', tri, [row_apply(p, Mc) for p in tri], labs)],
           'paper-m2-q2-triangle.svg',
           'The triangle P(1,1), Q(4,1), R(1,3), dashed grey, and its image in green: (a) reflected in the line y = x '
           'to (1,1), (1,4), (3,1); (b) sheared in x by half of y to (1.5,1), (4.5,1), (2.5,3); (c) reflected in the '
           'line x = 2 to (3,1), (0,1), (3,3)',
           (0, 5), (0, 5), sc=30)

    # Q3: clip coordinates (4, -2, 1, 2) -> NDC (2, -1, 0.5): x outside [-1, 1], so clipped
    ndc = (F(4, 2), F(-2, 2), F(1, 2))
    assert ndc == (2, -1, F(1, 2)) and not (-1 <= ndc[0] <= 1)
    # and (1, -0.5, 1.5, 2) -> (0.5, -0.25, 0.75), inside; viewport 1920 x 1080 -> pixel (1440, 675) with y down
    ndc = (F(1, 2), F(-1, 4), F(3, 4))
    assert ((ndc[0] + 1) / 2 * 1920, (1 - ndc[1]) / 2 * 1080) == (1440, 675)

    # Q4: cylinder radius 1, height 2 along +y from the origin -> axis along +x, base (3,1,2), radius 0.5, height 4
    M = matmul(T3(3, 1, 2), matmul(Rz3(-90), S3(0.5, 2, 0.5)))
    assert close(col_apply(M, (0, 0, 0)), (3, 1, 2)) and close(col_apply(M, (0, 2, 0)), (7, 1, 2))
    assert close(math.dist(col_apply(M, (1, 0, 0)), (3, 1, 2)), 0.5)
    assert close(M, [[0, 2, 0, 3], [-0.5, 0, 0, 1], [0, 0, 0.5, 2], [0, 0, 0, 1]]), M

    # Q5(b): Liang-Barsky, (-1,7) to (11,1), window [0,8] x [2,6]
    ps, qs, tE, tL, seg = liang_barsky((-1, 7), (11, 1), (0, 2, 8, 6))
    assert ps == [-12, 12, 6, -6] and qs == [-1, 9, 5, -1], (ps, qs)
    assert (tE, tL) == (F(1, 6), F(3, 4)), (tE, tL)
    assert seg == ((1, 6), (8, F(5, 2))), seg
    clip_pic((0, 2, 8, 6), [('start (-1,7)', (-1, 7), (11, 1), seg)], 'paper-m2-q5-liang-barsky.svg',
             'Liang-Barsky on the line from (-1,7) to (11,1) against the window x 0 to 8, y 2 to 6: it enters at '
             't = 1/6, the point (1, 6) on the top edge, and leaves at t = 3/4, the point (8, 2.5) on the right edge',
             (-2, 12), (0, 8))

    # Q6: the paper's program, run on its three use cases
    def circle(xc, yc, r):
        pixels = set()

        def plot8(x, y):
            for a, b in ((x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)):
                pixels.add((xc + a, yc + b))
        x, y, p = 0, r, 1 - r
        plot8(x, y)
        while x < y:
            x += 1
            if p < 0:
                p += 2 * x + 1
            else:
                y -= 1
                p += 2 * (x - y) + 1
            if x <= y:
                plot8(x, y)
        return sorted(pixels)
    c5 = circle(0, 0, 5)
    assert {(5, 0), (0, -5), (-5, 0), (3, 4), (4, 3)} <= set(c5) and len(c5) == 28
    assert {(x + 20, y + 15) for x, y in c5} == set(circle(20, 15, 5)) and (23, 19) in c5 + circle(20, 15, 5)
    assert circle(0, 0, 1) == [(-1, 0), (0, -1), (0, 1), (1, 0)]
    assert [p for *_, p in midpoint_circle_trace(5)][:3] == [-4, -1, 4]
    # Q6: midpoint circle use cases
    assert [(x, y) for x, y, _ in midpoint_circle_trace(5)] == [(0, 5), (1, 5), (2, 5), (3, 4)]
    assert [(x, y) for x, y, _ in midpoint_circle_trace(1)] == [(0, 1)]
    print('mock 2 ok')


# ======================================================================
# MOCK EXAM 3
# ======================================================================

def mock3():
    # Q1(b): midpoint circle r = 11, centre (3, 4)
    rows = midpoint_circle_trace(11)
    assert rows == [(0, 11, -10), (1, 11, -7), (2, 11, -2), (3, 11, 5), (4, 10, -6), (5, 10, 5),
                    (6, 9, 0), (7, 8, -1), (8, 8, 16)], rows
    octant = [(x, y) for x, y, _ in rows]
    s = Svg(440, 430, 'The first octant of the midpoint circle with radius 11 about the origin, from (0,11) to (8,8): '
                      'the pixels in blue, each showing the p that chose it; y drops on the pixels outlined in orange')
    g = PixelGrid(s, 13, 13, 28, left=40, top=15)
    g.draw()
    pts = [(11 * math.sin(a / 60 * math.pi / 4), 11 * math.cos(a / 60 * math.pi / 4)) for a in range(61)]
    s.path('M ' + ' L '.join(f'{g.px(x):.1f} {g.py(y):.1f}' for x, y in pts), TRUE, 2)
    for i, (x, y, _) in enumerate(rows):
        g.pixel(x, y)
        if i > 0:
            if y < rows[i - 1][1]:
                outline(g, x, y)
            s.text(g.px(x), g.py(y) + 4, str(rows[i - 1][2]).replace('-', '−'), 10, '#ffffff', weight='bold')
    s.text(s.w / 2, s.h - 8, 'Number in each pixel: the p that chose it. Orange outline: y dropped (p ≥ 0).', 11)
    s.save('paper-m3-circle-r11.svg', OUT)
    # shifted to the centre (3, 4), with the eight mirrors of (7, 8)
    assert [(x + 3, y + 4) for x, y in octant] == [(3, 15), (4, 15), (5, 15), (6, 15), (7, 14), (8, 14), (9, 13), (10, 12), (11, 12)]
    mirrors = sorted({(a + 3, b + 4) for a, b in ((7, 8), (8, 7), (-7, 8), (-8, 7), (7, -8), (8, -7), (-7, -8), (-8, -7))})
    assert mirrors == [(-5, -3), (-5, 11), (-4, -4), (-4, 12), (10, -4), (10, 12), (11, -3), (11, 11)], mirrors

    # Q1(c): P0(0,0), P1(1,4), P2(5,4), P3(6,0)
    P = [(0, 0), (1, 4), (5, 4), (6, 0)]
    for t in (F(0), F(1, 4), F(1, 2), F(1)):    # x = 3t + 9t^2 - 6t^3, y = 12t - 12t^2
        x, y = cubic(P, t)
        assert x == 3 * t + 9 * t ** 2 - 6 * t ** 3 and y == 12 * t - 12 * t ** 2
    L = casteljau(P, F(1, 4))
    assert L[1] == [(F(1, 4), 1), (2, 4), (F(21, 4), 3)]
    assert L[2] == [(F(11, 16), F(7, 4)), (F(45, 16), F(15, 4))]
    assert L[3] == [(F(39, 32), F(9, 4))]                         # B(1/4) = (1.21875, 2.25)
    # velocity: B'(t) = (3 + 18t - 18t^2, 12 - 24t)
    vel = lambda t: (3 + 18 * t - 18 * t ** 2, 12 - 24 * t)  # noqa: E731
    assert vel(0) == (3, 12) == (3 * (P[1][0] - P[0][0]), 3 * (P[1][1] - P[0][1]))
    assert vel(1) == (3, -12) == (3 * (P[3][0] - P[2][0]), 3 * (P[3][1] - P[2][1]))
    assert vel(F(1, 2)) == (F(15, 2), 0)
    curve_pic(P, 'paper-m3-q1c-curve.svg',
              'The cubic with control points P0(0,0), P1(1,4), P2(5,4), P3(6,0): it rises from P0 towards P1, is '
              'level at its top B(1/2) = (3, 3), and comes down into P3 from P2; B(1/4) = (1.22, 2.25) is marked',
              (0, 7), (0, 5), extra=[((F(39, 32), F(9, 4)), 'B(¼)', ACCENT), ((3, 3), 'B(½)', PURPLE)], sc=44)
    assert cubic(P, F(1, 2)) == (3, 3)

    # Q2: rotate 90 anticlockwise about (2,2), then scale x by 2 about the origin, row vectors
    tri = [(2, 2), (4, 2), (2, 3)]
    M = matmul(matmul(matmul(T2_row(-2, -2), rot_row(90)), T2_row(2, 2)), S2_row(2, 1))
    assert close(M, [[0, 1, 0], [-2, 0, 0], [8, 0, 1]]), M
    img = [r3(row_apply(p, M)) for p in tri]
    assert img == [(4, 2), (4, 4), (2, 2)], img
    panels([('rotate 90° about (2,2), then 2× in x', tri, img, ["A'", "B'", "C'"])],
           'paper-m3-q2-composite.svg',
           'The triangle A(2,2), B(4,2), C(2,3), dashed grey, and its image in green after a 90 degree anticlockwise '
           'turn about (2,2) and then doubling x: A\'(4,2), B\'(4,4), C\'(2,2)',
           (0, 6), (0, 5), sc=40)

    # Q3: Blinn-Phong. N=(0,0,1), L=(0,0.6,0.8), V=(0,0,1), shininess 8
    N, Lv, V = (0, 0, 1), (0, 0.6, 0.8), (0, 0, 1)
    H = norm(tuple(a + b for a, b in zip(Lv, V)))
    assert close(H, (0, 0.316, 0.949))
    assert close(dot(N, Lv), 0.8)
    assert close(dot(N, H) ** 8, 0.656)
    assert close(0.7 * 0.8 + 0.3 * dot(N, H) ** 8, 0.757)         # kd = 0.7, ks = 0.3

    # Q4: rotate P(3,2,1) by 90 deg about the axis through (1,2,0) parallel to z
    M = matmul(T3(1, 2, 0), matmul(Rz3(90), T3(-1, -2, 0)))
    assert close(col_apply(M, (3, 2, 1)), (1, 4, 1))
    assert close(M, [[0, -1, 0, 3], [1, 0, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]]), M
    assert close(col_apply(M, (1, 2, 5)), (1, 2, 5))                # points on the axis stay put

    # Q5(b): Cohen-Sutherland against (10,10)-(50,40)
    win = (10, 10, 50, 40)
    lines = [('L1', (0, 20), (30, 50)), ('L2', (20, 15), (45, 35)), ('L3', (55, 5), (60, 45))]
    res = {lab: cohen_sutherland(p, q, win) for lab, p, q in lines}
    assert res['L1'][0] == ('0001', '1000') and res['L1'][1] == ((10, 30), (20, 40)), res['L1']
    assert res['L2'] == (('0000', '0000'), ((20, 15), (45, 35)))
    assert res['L3'] == (('0110', '1010'), None)
    clip_pic(win, [(lab, p, q, res[lab][1]) for lab, p, q in lines], 'paper-m3-q5-clipping.svg',
             'The window from (10,10) to (50,40) and three lines: L1 from (0,20) to (30,50) keeps (10,30) to (20,40); '
             'L2 is inside and kept whole; L3 lies right of the window and is rejected',
             (0, 62), (0, 52), sc=7)
    print('mock 3 ok')


# ======================================================================
# CHECKPOINTS
# ======================================================================

def checkpoints():
    # ---- Checkpoint 1: lessons 01-08 ----
    assert 1280 * 720 * 24 // 8 == 2_764_800
    assert 2 ** 10 == 1024
    assert 120 // 40 == 3
    # slope types: (2,3) to (6,11)
    dx, dy = 4, 8
    assert (F(dy, dx), max(dx, dy), F(dx, max(dx, dy))) == (2, 8, F(1, 2))
    # DDA (0,0) to (7,3)
    pts, exact = dda_points(0, 0, 7, 3)
    assert pts == [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2), (6, 3), (7, 3)], pts
    # Bresenham (1,2) to (9,5): p values and pixels
    pts, ps, _ = bresenham_trace(1, 2, 9, 5)
    assert ps == [-2, 4, -6, 0, -10, -4, 2, -8], ps
    assert pts == [(1, 2), (2, 2), (3, 3), (4, 3), (5, 4), (6, 4), (7, 4), (8, 5), (9, 5)], pts
    # Bresenham steep (1,0) to (4,7)
    pts, ps, _ = bresenham_trace(1, 0, 4, 7)
    assert ps == [-1, 5, -3, 3, -5, 1, -7], ps
    assert pts == [(1, 0), (1, 1), (2, 2), (2, 3), (3, 4), (3, 5), (4, 6), (4, 7)], pts
    # hexagon vertex at 60 degrees, centre (50,50), r = 20
    assert close((50 + 20 * math.cos(math.radians(60)), 50 + 20 * math.sin(math.radians(60))), (60, 67.32))
    # dashed: pixel index 13 with on=4, off=3
    assert 13 % 7 == 6 and not (13 % 7 < 4)
    assert [k for k in range(12) if k % 7 < 4] == [0, 1, 2, 3, 7, 8, 9, 10]
    # supersampling
    assert F(3, 4) == 0.75

    # ---- Checkpoint 2: lessons 01-14 ----
    assert [(x, y) for x, y, _ in midpoint_circle_trace(6)] == [(0, 6), (1, 6), (2, 6), (3, 5), (4, 4)]
    assert [p for *_, p in midpoint_circle_trace(6)] == [-5, -2, 3, 0, 1]
    assert 3 - 2 * 9 == -15
    assert (2 + F(1, 3) * 0, F(8 - 2, 4 - 1)) and (2 + (2 - 1) * F(6, 3)) == 4     # scan-line: x = 2 + (y-1)*2
    win = (10, 10, 40, 30)
    assert [code(p, win) for p in ((5, 35), (45, 20), (20, 5), (25, 20))] == ['1001', '0010', '0100', '0000']
    assert int('0101', 2) & int('0110', 2) == 0b0100
    st, seg = cohen_sutherland((2, 3), (12, 9), (4, 2, 10, 8))
    assert st == ('0001', '1010') and seg == ((4, F(21, 5)), (10, F(39, 5))), (st, seg)  # (4, 4.2) to (10, 7.8)
    ps, qs, tE, tL, seg = liang_barsky((1, 2), (11, 7), (3, 1, 9, 6))
    assert (tE, tL) == (F(1, 5), F(4, 5)) and seg == ((3, 3), (9, 6)), (tE, tL, seg)
    assert (7 - 2, 3 - (-1)) == (5, 4) and close(math.sqrt(41), 6.403)
    assert lerp((4, 8), (12, 0), F(1, 4)) == (6, 6)
    a, b = (1, 2, 2), (2, 0, 1)
    assert dot(a, b) == 4 and close(math.degrees(math.acos(4 / (3 * math.sqrt(5)))), 53.40)
    assert close(dot((0, 1, 0), norm((1, 1, 0))), 0.7071)
    A, B, C = (1, 0, 0), (0, 2, 0), (0, 0, 3)
    ab, ac = tuple(y - x for x, y in zip(A, B)), tuple(y - x for x, y in zip(A, C))
    assert (ab, ac, cross(ab, ac)) == ((-1, 2, 0), (-1, 0, 3), (6, 3, 2))
    tri = [(1, 1), (4, 1), (1, 3)]
    M = matmul(matmul(T2_row(-1, -1), S2_row(2, 2)), T2_row(1, 1))
    assert [row_apply(p, M) for p in tri] == [(1, 1), (7, 1), (1, 5)]
    assert row_apply((5, 7), [[1, 0, 0], [0, 1, 0], [3, -2, 1]]) == (8, 5)
    M = matmul(matmul(T2_row(-2, -1), rot_row(90)), T2_row(2, 1))
    assert close(M, [[0, 1, 0], [-1, 0, 0], [3, -1, 1]]) and close(row_apply((4, 1), M), (2, 3))

    # ---- Checkpoint 3: lessons 01-20 ----
    assert quad([(0, 0), (4, 6), (8, 0)], F(1, 2)) == (4, 3)
    t = F(1, 3)
    assert [(1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t ** 2 * (1 - t), t ** 3] == [F(8, 27), F(12, 27), F(6, 27), F(1, 27)]
    assert end_conditions((1, 1), (9, 0), (7, 4), (0, -6)) == [(1, 1), (4, 1), (7, 6), (7, 4)]
    assert cubic([(0, 0), (2, 4), (6, 4), (8, 0)], F(1, 2)) == (4, 3)
    P = [(0, 0), (2, 6), (8, 6), (10, 0)]
    L = casteljau(P, F(1, 2))
    assert L[1] == [(1, 3), (5, 6), (9, 3)] and L[2] == [(3, F(9, 2)), (7, F(9, 2))] and L[3] == [(5, F(9, 2))]
    assert split(P, F(1, 2))[0] == [(0, 0), (1, 3), (3, F(9, 2)), (5, F(9, 2))]
    assert seg_distance((1, 7), (0, 0), (8, 6)) == (0.5, (4.0, 3.0), 5.0)
    assert lerp((0, 0), (8, 4), F(1, 4)) == (2, 1) and lerp((0, 0), (8, 4), F(3, 4)) == (6, 3)
    assert dot((0, 0, -1), (0, 0.6, 0.8)) == -0.8          # facing the eye: kept
    assert dot((0, 0, -1), (0, 0.6, -0.8)) == 0.8          # facing away: culled
    curve_pic(P, 'paper-cp3-casteljau.svg',
              'de Casteljau at t = 1/2 on P0(0,0), P1(2,6), P2(8,6), P3(10,0): the control polygon dashed, the curve '
              'in red, and the curve point B(1/2) = (5, 4.5) in green',
              (0, 10), (0, 7), extra=[((5, 4.5), 'B(½) = (5, 4.5)', ACCENT)], sc=36)
    print('checkpoints ok')


# ======================================================================
# QUESTION BANK (assignment and supplementary questions, plus new ones)
# ======================================================================

def bank():
    # A-6: DDA (20,10) to (30,18), and Bresenham on the same line
    pts, exact = dda_points(20, 10, 30, 18)
    assert [float(y) for _, y in exact] == [10, 10.8, 11.6, 12.4, 13.2, 14, 14.8, 15.6, 16.4, 17.2, 18]
    assert [y for _, y in pts] == [10, 11, 12, 12, 13, 14, 15, 16, 16, 17, 18]
    bpts, bps, _ = bresenham_trace(20, 10, 30, 18)
    assert bps == [6, 2, -2, 14, 10, 6, 2, -2, 14, 10], bps
    assert bpts == pts, (bpts, pts)                          # the two agree on this line
    grid_pic(pts, 12, 10, 'paper-qb-dda-20-10-to-30-18.svg',
             'DDA and Bresenham from (20,10) to (30,18) light the same eleven pixels: y = 10, 11, 12, 12, 13, 14, 15, '
             '16, 16, 17, 18 for x = 20 to 30', line=((20, 10), (30, 18)), ox=20, oy=9)

    # A-7: the cross
    assert bresenham_trace(10, 10, 50, 50)[0] == [(10 + i, 10 + i) for i in range(41)]
    assert bresenham_trace(50, 10, 10, 50)[0] == [(50 - i, 10 + i) for i in range(41)]
    assert bresenham_trace(50, 10, 10, 50)[1][:3] == [40, 40, 40]

    # A-8: hexagon centre (100,100), r = 50
    verts = [(100 + 50 * math.cos(math.radians(60 * i)), 100 + 50 * math.sin(math.radians(60 * i))) for i in range(6)]
    assert [(half_up(x), half_up(y)) for x, y in verts] == [(150, 100), (125, 143), (75, 143), (50, 100), (75, 57), (125, 57)]

    # A-9: dashed rectangle, on = 4, off = 3, pattern carried round the corners
    perim = 2 * (150 + 100)
    assert perim == 500 and sum(1 for k in range(perim) if k % 7 < 4) == 287

    # B-1 (ii): row vectors [[1,0,0],[1,2,0],[0,0,1]] on A(-1,1), B(1,1), C(1,-1), D(-1,-1)
    sq = [(-1, 1), (1, 1), (1, -1), (-1, -1)]
    assert [row_apply(p, [[1, 0, 0], [1, 2, 0], [0, 0, 1]]) for p in sq] == [(0, 2), (2, 2), (0, -2), (-2, -2)]
    assert [r3(row_apply(p, rot_row(30))) for p in sq] == [(-1.366, 0.366), (0.366, 1.366), (1.366, -0.366), (-0.366, -1.366)]

    # B-3: column vectors
    Tl, R90 = [[1, 0, -5], [0, 1, 0], [0, 0, 1]], [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    Mc = matmul(Tl, R90)
    assert Mc == [[0, -1, -5], [1, 0, 0], [0, 0, 1]]
    assert [col_apply(Mc, p) for p in ((0, 0), (1, 0), (0, 1))] == [(-5, 0), (-5, 1), (-6, 0)]
    Td = [[-2, 0, 4], [2, 2, 2], [0, 0, 1]]
    assert [col_apply(Td, p) for p in ((0, 0), (1, 0), (0, 1))] == [(4, 2), (2, 4), (4, 4)]

    # B-7 (5): Cohen-Sutherland, window (50,10)-(80,40)
    win = (50, 10, 80, 40)
    r1 = cohen_sutherland((40, 15), (75, 45), win)
    r2 = cohen_sutherland((70, 20), (100, 10), win)
    assert r1[0] == ('0001', '1000') and close(r1[1], ((50, 23.571), (69.167, 40))), r1
    assert r2[0] == ('0000', '0010') and close(r2[1], ((70, 20), (80, 16.667))), r2
    clip_pic(win, [('P1', (40, 15), (75, 45), r1[1]), ('P3', (70, 20), (100, 10), r2[1])],
             'paper-qb-b7-clipping.svg',
             'The window (50,10) to (80,40); P1P2 is cut at the left edge (50, 23.57) and the top edge (69.17, 40); '
             'P3P4 starts inside and is cut at the right edge (80, 16.67)', (35, 105), (0, 50), sc=6)

    # B-8: P0=(1,0,1), P3=(5,2,4), v0=(6,0,0), v1=(0,0,3)
    P = end_conditions((1, 0, 1), (6, 0, 0), (5, 2, 4), (0, 0, 3))
    assert P == [(1, 0, 1), (3, 0, 1), (5, 2, 3), (5, 2, 4)], P
    assert cubic(P, F(1, 2)) == (F(15, 4), 1, F(17, 8))
    assert split(P, F(1, 2))[0] == [(1, 0, 1), (2, 0, 1), (3, F(1, 2), F(3, 2)), (F(15, 4), 1, F(17, 8))]

    # B-9: P0(0,0), P1(2,0), P2(0,2), P3(4,4)
    L = casteljau([(0, 0), (2, 0), (0, 2), (4, 4)], F(1, 2))
    assert L[1] == [(1, 0), (1, 1), (2, 3)] and L[2] == [(1, F(1, 2)), (F(3, 2), 2)] and L[3] == [(F(5, 4), F(5, 4))]

    # B-10: P0=(0,0), v0=(6,0); P3=(0,4), v1=(-12,0)
    P = end_conditions((0, 0), (6, 0), (0, 4), (-12, 0))
    assert P == [(0, 0), (2, 0), (4, 4), (0, 4)], P
    assert cubic(P, F(1, 2)) == (F(9, 4), 2)
    first, second = split(P, F(1, 2))
    assert second == [(F(9, 4), 2), (F(5, 2), 3), (2, 4), (0, 4)], second
    L = casteljau(P, F(1, 2))
    assert L[1] == [(1, 0), (3, 2), (2, 4)] and L[2] == [(2, 1), (F(5, 2), 3)]
    curve_pic(P, 'paper-qb-b10-particle.svg',
              'B-10: control points P0(0,0), P1(2,0), P2(4,4), P3(0,4), the control polygon dashed and the curve in '
              'red; it leaves P0 heading right, swings out to x = 2.25 at B(1/2) = (2.25, 2), and arrives at P3 '
              'heading left', (0, 5), (0, 5), extra=[((F(9, 4), 2), 'B(½)', ACCENT)], sc=50)

    # B-11 (b): A(2,2) to B(9,2) and the swapped A'(2,2) to B'(2,9)
    pts, ps, _ = bresenham_trace(2, 2, 9, 2)
    assert pts == [(x, 2) for x in range(2, 10)] and ps == [-7] * 7
    pts, ps, _ = bresenham_trace(2, 2, 2, 9)
    assert pts == [(2, y) for y in range(2, 10)] and ps == [-7] * 7

    # Supplementary 2, 6
    assert [(x + 2, y + 3) for x, y in ((0, 0), (5, 0), (5, 5))] == [(2, 3), (7, 3), (7, 8)]
    P = [(0, 5), (1, 7), (5, -2), (6, 1)]                     # a = b = 1, as Curves 3 does
    assert 3 * (P[1][1] - P[0][1]) / (3 * (P[1][0] - P[0][0])) == 2
    assert 3 * (P[3][1] - P[2][1]) / (3 * (P[3][0] - P[2][0])) == 3
    assert cubic(P, F(1, 2)) == (3, F(21, 8))

    # new: frame buffer for 1920 x 1080 at 32 bpp, and 60 Hz
    assert 1920 * 1080 * 32 // 8 == 8_294_400 and close(1000 / 60, 16.667)
    # new: midpoint circle r = 7
    assert midpoint_circle_trace(7) == [(0, 7, -6), (1, 7, -3), (2, 7, 2), (3, 6, -3), (4, 6, 6), (5, 5, 7)]
    # new: z-buffer at one pixel, smaller z is nearer
    frags = [('red', 0.7), ('green', 0.4), ('blue', 0.55)]
    depth, colour = 1.0, 'background'
    for c, z in frags:
        if z < depth:
            depth, colour = z, c
    assert (colour, depth) == ('green', 0.4)
    # new: Lambert with unit vectors
    assert close(max(0, dot((0, 0, 1), norm((0, 3, 4)))), 0.8)
    # new: perspective divide
    assert (4 / 2, -2 / 2, 1 / 2) == (2, -1, 0.5)
    # new: mipmap levels for 1024 x 1024
    assert int(math.log2(1024)) + 1 == 11
    print('bank ok')


if __name__ == '__main__':
    mock1()
    mock2()
    mock3()
    checkpoints()
    bank()
