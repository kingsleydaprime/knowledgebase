"""Draw the pictures for computer-graphics Vectors 1-3 and Curves 1-2 and 5 as small SVG files.

    python3 scripts/diagrams/cg_vectors_curves.py      # run from the vault root

Every picture is computed from the same formula the lesson teaches (B - A, the
line P(t) = A + t(B - A), the dot and cross products, de Casteljau, the Bernstein
weights), and each one asserts the lesson's worked numbers before it draws, so
a picture can't disagree with the text. Files are prefixed vec- and curve-.
Output: computer-graphics/images/*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, PIX, TRUE, ACCENT, Svg  # noqa: E402
from computer_graphics import Axes, ORANGE, OUT, lerp, de_casteljau_levels  # noqa: E402

GREY = '#9aa5b1'
PURPLE = '#7c3aed'


# ---------- the maths, exactly as the lessons state it ----------

def sub(b, a):
    return tuple(x - y for x, y in zip(b, a))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(k, v):
    return tuple(k * x for x in v)


def length(v):
    return math.sqrt(sum(x * x for x in v))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def line_point(a, b, t):
    """P(t) = A + t(B - A)."""
    return add(a, scale(t, sub(b, a)))


def close(p, q, eps=1e-9):
    return all(abs(x - y) < eps for x, y in zip(p, q))


def quad_bezier(p0, p1, p2, t):
    """C(t) = (1 - t)^2 P0 + 2(1 - t)t P1 + t^2 P2."""
    w = ((1 - t) ** 2, 2 * (1 - t) * t, t * t)
    return tuple(w[0] * a + w[1] * b + w[2] * c for a, b, c in zip(p0, p1, p2))


def bezier(ps, t):
    n = len(ps) - 1
    out = [0.0] * len(ps[0])
    for i, p in enumerate(ps):
        w = math.comb(n, i) * (1 - t) ** (n - i) * t ** i
        out = [o + w * c for o, c in zip(out, p)]
    return tuple(out)


# ---------- arrows ----------

def arrow_marker(s, name, color):
    s.add(f'<defs><marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
          f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>')


def varrow(A, a, b, color=INK, width=2.4, dash=None):
    """Arrow on axes A from point a to point b, marker in the arrow's own colour."""
    mid = 'm' + color.strip('#')
    if mid not in A.s.markers:
        arrow_marker(A.s, mid, color)
        A.s.markers.add(mid)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    A.s.add(f'<line x1="{A.X(a[0]):.1f}" y1="{A.Y(a[1]):.1f}" x2="{A.X(b[0]):.1f}" y2="{A.Y(b[1]):.1f}" '
            f'stroke="{color}" stroke-width="{width}"{d} marker-end="url(#{mid})"/>')


def new_svg(w, h, title):
    s = Svg(w, h, title)
    s.markers = set()
    return s


def sarrow(s, x1, y1, x2, y2, color=INK, width=2.4):
    mid = 'm' + color.strip('#')
    if mid not in s.markers:
        arrow_marker(s, mid, color)
        s.markers.add(mid)
    s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
          f'stroke-width="{width}" marker-end="url(#{mid})"/>')


# ---------- Vectors 1: points, vectors and the journey from A to B ----------

A0, B0 = (1, 2), (4, 6)


def vec_a_to_b():
    ab = sub(B0, A0)
    assert ab == (3, 4) and length(ab) == 5
    ang = math.degrees(math.atan2(ab[1], ab[0]))
    assert round(ang, 1) == 53.1
    s = new_svg(470, 360, 'The vector from A (1, 2) to B (4, 6) is B minus A = (3, 4): 3 across and 4 up. '
                          'Its length is 5 by Pythagoras and it makes about 53.1 degrees with the x-axis')
    A = Axes(s, 50, 315, 42, (0, 9), (0, 7))
    A.seg(A0, (4, 2), ORANGE, 2, '6 4')
    A.seg((4, 2), B0, ACCENT, 2, '6 4')
    varrow(A, A0, B0, TRUE, 2.8)
    A.dot(A0, INK)
    A.dot(B0, INK)
    A.label(A0, 'A (1, 2)  tail', -10, -6, anchor='end', weight='bold')
    A.label(B0, 'B (4, 6)  head', 10, 4, weight='bold')
    A.label((2.5, 2), 'x₂ − x₁ = 3', 0, 20, ORANGE, 'middle', 12, 'bold')
    A.label((4, 4), 'y₂ − y₁ = 4', 8, 4, ACCENT, 'start', 12, 'bold')
    A.label((2.5, 4), '|AB| = 5', -14, -4, TRUE, 'end', 12, 'bold')
    A.label(A0, 'θ ≈ 53.1°', 34, -6, INK, 'start', 11)
    s.text(235, 350, 'AB = B − A = (4 − 1, 6 − 2) = (3, 4). Head minus tail.', 12)
    s.save('vec-a-to-b.svg', OUT)


def vec_point_vs_vector():
    v = (3, 4)
    starts = [(1, 2), (6, 0), (0, 0)]
    ends = [add(p, v) for p in starts]
    assert ends == [(4, 6), (9, 4), (3, 4)]
    s = new_svg(560, 380, 'The same vector (3, 4), meaning 3 right and 4 up, drawn from three starting points: '
                          'from (1, 2) it lands on (4, 6), from (6, 0) on (9, 4), and from the origin on (3, 4), '
                          'which is why a vector from the origin looks like a point')
    A = Axes(s, 50, 330, 38, (-1, 10), (-1, 7))
    cols = (TRUE, PIX, ACCENT)
    for p, q, c in zip(starts, ends, cols):
        varrow(A, p, q, c, 2.6)
        A.dot(p, INK, 4)
        A.label(p, f'start {p}', 8, 4, c, 'start', 11, 'bold')
        A.label(q, f'lands on {q}', 6, -6, c, 'start', 11, 'bold')
    s.text(280, 22, 'One journey, (3, 4) = "3 right, 4 up", from three different starts', 12, weight='bold')
    s.text(280, 370, 'From the origin (green) the vector and the point it lands on have the same numbers.', 11)
    s.save('vec-point-vs-vector.svg', OUT)


def vec_ab_vs_ba():
    ab, ba = sub(B0, A0), sub(A0, B0)
    assert ba == (-3, -4) and ba == scale(-1, ab)
    s = new_svg(560, 330, 'AB = B minus A = (3, 4) points from A to B; BA = A minus B = (minus 3, minus 4) points '
                          'from B back to A. Same length 5, opposite direction')
    for k, (p, q, name, val, c) in enumerate(((A0, B0, 'AB = B − A', '(3, 4)', TRUE),
                                             (B0, A0, 'BA = A − B', '(−3, −4)', PIX))):
        A = Axes(s, 35 + k * 280, 285, 36, (0, 6), (0, 7), ticks=False)
        varrow(A, p, q, c, 2.8)
        A.dot(A0, INK)
        A.dot(B0, INK)
        A.label(A0, 'A', -8, 16, anchor='end', weight='bold', size=13)
        A.label(B0, 'B', 8, 4, weight='bold', size=13)
        s.text(A.X(3), 30, f'{name} = {val}', 13, c, weight='bold')
        s.text(A.X(3), 312, 'length 5', 12)
    s.save('vec-ab-vs-ba.svg', OUT)


def vec_unit_vector():
    v = (3, 4)
    u = scale(1 / length(v), v)
    assert close(u, (0.6, 0.8)) and abs(length(u) - 1) < 1e-12
    s = new_svg(470, 360, 'The vector (3, 4) has length 5. Dividing it by 5 gives the unit vector (0.6, 0.8), '
                          'which points the same way but has length exactly 1, so it ends on the circle of radius 1')
    A = Axes(s, 60, 320, 56, (0, 6), (0, 5))
    A.poly([(math.cos(a / 60 * math.pi / 2), math.sin(a / 60 * math.pi / 2)) for a in range(61)],
           GREY, 1.4, close=False, dash='4 3')
    A.label((0.92, 0.38), 'radius 1', 6, 4, GREY, 'start', 10)
    varrow(A, (0, 0), v, TRUE, 2.4)
    varrow(A, (0, 0), u, ACCENT, 3.4)
    A.label(v, 'v = (3, 4), |v| = 5', 8, 4, TRUE, 'start', 12, 'bold')
    A.label(u, 'v / |v| = (0.6, 0.8), length 1', 26, 30, ACCENT, 'start', 12, 'bold')
    s.text(235, 352, 'Same direction, length thrown away. That is all a unit vector is.', 12)
    s.save('vec-unit-vector.svg', OUT)


def vec_add_and_scale():
    u, v = (3, 1), (1, 2)
    assert add(u, v) == (4, 3) and scale(2, v) == (2, 4) and scale(-1, v) == (-1, -2)
    s = new_svg(600, 340, 'Left: adding vectors tip to tail, u = (3, 1) then v = (1, 2) gives u + v = (4, 3). '
                          'Right: scaling v = (1, 2) by 2 gives (2, 4), twice as long; by minus 1 gives (minus 1, '
                          'minus 2), turned round')
    L = Axes(s, 40, 280, 44, (0, 5), (0, 5), ticks=False)
    varrow(L, (0, 0), u, PIX, 2.6)
    varrow(L, u, add(u, v), ORANGE, 2.6)
    varrow(L, (0, 0), add(u, v), TRUE, 2.6)
    L.label((1.5, 0.5), 'u = (3, 1)', 0, 18, PIX, 'middle', 12, 'bold')
    L.label((3.5, 2), 'v = (1, 2)', 8, 4, ORANGE, 'start', 12, 'bold')
    L.label((2, 1.5), 'u + v = (4, 3)', -8, -8, TRUE, 'end', 12, 'bold')
    s.text(L.X(2.5), 26, 'Add: follow u, then v', 13, weight='bold')
    R = Axes(s, 340, 300, 42, (-2, 3), (-2, 4), ticks=False)
    R.s = s
    varrow(R, (0, 0), scale(2, v), ACCENT, 2.4)
    varrow(R, (0, 0), v, PIX, 3.4)
    varrow(R, (0, 0), scale(-1, v), TRUE, 2.4)
    R.label(scale(2, v), '2v = (2, 4)', 8, 4, ACCENT, 'start', 12, 'bold')
    R.label(v, 'v = (1, 2)', 8, 6, PIX, 'start', 12, 'bold')
    R.label(scale(-1, v), '−v = (−1, −2)', 8, 10, TRUE, 'start', 12, 'bold')
    s.text(R.X(0.5), 26, 'Scale: multiply every part', 13, weight='bold')
    s.save('vec-add-and-scale.svg', OUT)


def vec_point_vs_direction_w():
    T = (5, 0)
    p, d = (1, 2), (0, 1)
    moved_p = add(p, scale(1, T))       # w = 1: the translation is added once
    moved_d = add(d, scale(0, T))       # w = 0: the translation is added zero times
    assert moved_p == (6, 2) and moved_d == (0, 1)
    s = new_svg(560, 300, 'Translating by (5, 0). The point (1, 2) with w = 1 moves to (6, 2). The direction '
                          '(0, 1) with w = 0, drawn as an arrow, is unchanged: it still points straight up')
    A = Axes(s, 40, 250, 42, (0, 11), (0, 4))
    A.dot(p, PIX, 6)
    A.dot(moved_p, PIX, 6)
    varrow(A, (1.4, 2), (5.6, 2), GREY, 1.6, '5 4')
    A.label(p, 'point (1, 2, w = 1)', -6, 22, PIX, 'start', 12, 'bold')
    A.label(moved_p, 'moves to (6, 2)', -6, 22, PIX, 'start', 12, 'bold')
    for base in ((8, 1), (10, 1)):
        varrow(A, base, add(base, (0, 1.8)), ORANGE, 3)
    A.label((9, 3), 'direction (0, 1, w = 0)', 0, -12, ORANGE, 'middle', 12, 'bold')
    A.label((8, 1), 'before', 0, 18, ORANGE, 'middle', 11)
    A.label((10, 1), 'after', 0, 18, ORANGE, 'middle', 11)
    s.text(280, 24, 'Translate by (5, 0): w = 1 picks up the move, w = 0 ignores it', 13, weight='bold')
    s.save('vec-point-vs-direction-w.svg', OUT)


# ---------- Vectors 2: the line between two points ----------

def vec_line_t():
    pts = {t: line_point(A0, B0, t) for t in (-0.5, 0, 0.25, 0.5, 1, 1.5)}
    assert pts[0] == A0 and pts[1] == B0 and pts[0.5] == (2.5, 4.0) and pts[0.25] == (1.75, 3.0)
    assert pts[1.5] == (5.5, 8.0) and pts[-0.5] == (-0.5, 0.0)
    s = new_svg(470, 420, 'The line P(t) = A + t(B minus A) through A (1, 2) and B (4, 6). t = 0 is A, t = 0.25 is '
                          '(1.75, 3), t = 0.5 is the midpoint (2.5, 4), t = 1 is B, t = 1.5 is past B at (5.5, 8) and '
                          't = minus 0.5 is behind A at (minus 0.5, 0)')
    A = Axes(s, 60, 380, 40, (-1, 7), (0, 8))
    A.seg(pts[-0.5], A0, GREY, 2, '6 4')
    A.seg(B0, pts[1.5], GREY, 2, '6 4')
    A.seg(A0, B0, TRUE, 3)
    for t, p in pts.items():
        col = INK if t in (0, 1) else (TRUE if 0 < t < 1 else GREY)
        A.dot(p, col, 5)
        name = {0: 'A', 1: 'B'}.get(t, '')
        A.label(p, f't = {t:g}' + (f'  ({name})' if name else f'  ({p[0]:g}, {p[1]:g})'), 10, 4, col, 'start', 12,
                'bold')
    s.text(235, 412, 'Red: 0 ≤ t ≤ 1, the segment. Grey dashes: t < 0 behind A, t > 1 past B.', 11)
    s.save('vec-line-t.svg', OUT)


def vec_journey_not_point():
    ab = sub(B0, A0)
    # is (3, 4) on the line through A and B?  x = 1 + 3t = 3 gives t = 2/3, then y = 2 + 4t = 14/3, not 4
    t = (ab[0] - A0[0]) / ab[0]
    assert abs(A0[1] + 4 * t - 14 / 3) < 1e-12 and A0[1] + 4 * t != 4
    s = new_svg(470, 340, 'B minus A = (3, 4) is a journey, not a place. Drawn from A it reaches B. The point (3, 4) '
                          'itself is off the line from A to B')
    A = Axes(s, 50, 300, 40, (0, 9), (0, 7))
    A.seg((0.25, 1), (5, 7.33), GREY, 1.4, '6 4')
    varrow(A, A0, B0, TRUE, 2.8)
    A.dot(A0, INK)
    A.dot(B0, INK)
    A.label(A0, 'A (1, 2)', 8, 14, weight='bold')
    A.label(B0, 'B (4, 6)', 8, 4, weight='bold')
    A.label((2.5, 4), 'B − A = (3, 4)', -12, -6, TRUE, 'end', 12, 'bold')
    A.dot(ab, PIX, 6)
    A.label(ab, 'the point (3, 4): not on the line', 10, 4, PIX, 'start', 12, 'bold')
    s.text(235, 334, 'Start + journey = destination. The journey alone says how far and which way, not where.', 11)
    s.save('vec-journey-not-point.svg', OUT)


def vec_one_third():
    a, b = (2, 1), (8, 7)
    trip = sub(b, a)
    part = scale(1 / 3, trip)
    p = add(a, part)
    assert trip == (6, 6) and close(part, (2, 2)) and close(p, (4, 3))
    s = new_svg(470, 380, 'One-third of the way from A (2, 1) to B (8, 7). Step 1: the full trip B minus A = (6, 6). '
                          'Step 2: one-third of it is (2, 2). Step 3: add it to A to land on P = (4, 3)')
    A = Axes(s, 50, 340, 36, (0, 10), (0, 8))
    A.seg(a, b, GREY, 1.6, '6 4')
    varrow(A, a, (round(p[0]), round(p[1])), ACCENT, 3.4)
    A.dot(a, INK)
    A.dot(b, INK)
    A.dot((4, 3), TRUE, 6)
    A.label(a, 'A (2, 1)', 8, 14, weight='bold')
    A.label(b, 'B (8, 7)', 8, 4, weight='bold')
    A.label((4, 3), 'P = A + ⅓(B − A) = (4, 3)', 10, 8, TRUE, 'start', 12, 'bold')
    A.label((5, 4), 'full trip (6, 6)', 10, 2, GREY, 'start', 11, 'bold')
    A.label((3, 2), '⅓ of it: (2, 2)', -10, -6, ACCENT, 'end', 12, 'bold')
    s.text(235, 374, 'Find the trip, take the fraction, add to the start.', 12)
    s.save('vec-one-third.svg', OUT)


def vec_t_ranges():
    rows = (((0, 1), 't from 0 to 1: the whole segment'),
            ((0, 0.5), 't from 0 to 0.5: half drawn (a stroke drawing itself)'),
            ((0.2, 0.8), 't from 0.2 to 0.8: trimmed, gaps at both ends'))
    assert line_point(A0, B0, 0.5) == (2.5, 4.0)
    assert close(line_point(A0, B0, 0.2), (1.6, 2.8)) and close(line_point(A0, B0, 0.8), (3.4, 5.2))
    s = new_svg(660, 290, 'The same line from A (1, 2) to B (4, 6) drawn for three ranges of t: 0 to 1 is the whole '
                          'segment, 0 to 0.5 is the first half up to (2.5, 4), and 0.2 to 0.8 trims both ends, '
                          'from (1.6, 2.8) to (3.4, 5.2)')
    for k, ((t0, t1), title) in enumerate(rows):
        A = Axes(s, 25 + k * 215, 220, 30, (0, 5), (1, 7), ticks=False)
        A.seg(A0, B0, '#e5e7eb', 6)
        A.seg(line_point(A0, B0, t0), line_point(A0, B0, t1), TRUE, 3.5)
        A.dot(A0, INK, 4)
        A.dot(B0, INK, 4)
        A.label(A0, 'A', -8, 14, anchor='end', weight='bold')
        A.label(B0, 'B', 8, 4, weight='bold')
        words = title.split(': ')
        s.text(A.X(2.5), 248, words[0], 12, weight='bold')
        s.text(A.X(2.5), 266, words[1], 10)
    s.text(330, 24, 'Same formula, smaller range of t = only part of the line', 13, weight='bold')
    s.save('vec-t-ranges.svg', OUT)


def vec_lerp_colours():
    red, blue = (255, 0, 0), (0, 0, 255)
    c03 = line_point(red, blue, 0.3)
    assert close(c03, (178.5, 0, 76.5))
    s = new_svg(600, 200, 'Lerp between two colours: red (255, 0, 0) at t = 0 to blue (0, 0, 255) at t = 1. At '
                          't = 0.3 the colour is 70 percent red and 30 percent blue, (178.5, 0, 76.5)')
    x0, w, n = 40, 520, 52
    for i in range(n):
        t = i / (n - 1)
        r, g, b = line_point(red, blue, t)
        s.rect(x0 + i * w / n, 50, w / n + 0.6, 60, f'rgb({r:.0f},{g:.0f},{b:.0f})')
    for t in (0, 0.3, 0.5, 1):
        x = x0 + t * (w - w / n) + w / n / 2
        s.line(x, 112, x, 124, INK, 1.5)
        s.text(x, 138, f't = {t:g}', 12, weight='bold')
    s.text(x0 + 0.3 * (w - w / n) + w / n / 2, 160, '(178.5, 0, 76.5)', 11)
    s.text(300, 34, '(1 − t)·red + t·blue, worked out on each of R, G and B', 13, weight='bold')
    s.text(300, 188, 'A colour is a vector of three numbers, so the line formula blends colours too.', 11)
    s.save('vec-lerp-colours.svg', OUT)


def vec_ray_wall():
    o, d = (0, 1), (1, 0.5)
    t = (4 - o[0]) / d[0]
    hit = add(o, scale(t, d))
    assert t == 4 and hit == (4, 3)
    s = new_svg(470, 300, 'A ray P(t) = O + tD from O (0, 1) in direction D (1, 0.5) hits the wall x = 4 when '
                          '0 + t times 1 = 4, so t = 4 and the hit point is (4, 3)')
    A = Axes(s, 50, 260, 50, (0, 7), (0, 4))
    s.rect(A.X(4), A.Y(4), 10, A.Y(0) - A.Y(4), '#e5e7eb', INK, 1.5)
    A.seg(o, add(o, scale(6, d)), GREY, 1.4, '6 4')
    varrow(A, o, add(o, d), ORANGE, 3)
    A.seg(add(o, d), hit, TRUE, 2.6)
    A.dot(o, INK)
    A.dot(hit, TRUE, 6)
    A.label(o, 'O (0, 1)', -6, 18, weight='bold')
    A.label(add(o, d), 'D = (1, 0.5)', -16, -22, ORANGE, 'start', 12, 'bold')
    A.label(hit, 'hit at t = 4: (4, 3)', -10, -12, TRUE, 'end', 12, 'bold')
    A.label((4, 0.4), 'wall x = 4', 14, 0, INK, 'start', 11, 'bold')
    s.text(235, 292, 'Same line formula; the intersection test solves for t.', 12)
    s.save('vec-ray-wall.svg', OUT)


# ---------- Vectors 3: dot and cross products ----------

def vec_dot_signs():
    cases = (((3, 1), (1, 2), 'positive: roughly the same way'),
             ((2, 1), (-1, 2), 'zero: a right angle'),
             ((3, 1), (-2, 1), 'negative: roughly opposite'))
    vals = [dot(a, b) for a, b, _ in cases]
    assert vals == [5, 0, -5]
    s = new_svg(690, 270, 'Three pairs of vectors. (3, 1) and (1, 2): dot product 5, positive, pointing roughly the '
                          'same way. (2, 1) and (minus 1, 2): dot product 0, at a right angle. (3, 1) and '
                          '(minus 2, 1): dot product minus 5, pointing roughly opposite ways')
    for k, ((a, b, title), v) in enumerate(zip(cases, vals)):
        A = Axes(s, 50 + k * 215, 190, 34, (-2, 3), (-1, 3), ticks=False)
        varrow(A, (0, 0), a, PIX, 2.6)
        varrow(A, (0, 0), b, ORANGE, 2.6)
        A.label(a, f'a = {a}'.replace('-', '−'), 0, 22, PIX, 'middle', 11, 'bold')
        A.label(b, f'b = {b}'.replace('-', '−'), 0, -8, ORANGE, 'middle', 11, 'bold')
        s.text(A.X(0.5), 222, f'a · b = {v}'.replace('-', '−'), 13, TRUE, weight='bold')
        s.text(A.X(0.5), 242, title, 11)
    s.save('vec-dot-signs.svg', OUT)


def vec_dot_angle():
    a, b = (3, 4), (2, 1)
    ab = dot(a, b)
    cos = ab / (length(a) * length(b))
    theta = math.degrees(math.acos(cos))
    shadow = ab / length(b)
    foot = scale(ab / dot(b, b), b)
    assert ab == 10 and round(cos, 3) == 0.894 and round(theta, 1) == 26.6 and round(shadow, 2) == 4.47
    assert close(foot, (4, 2))
    s = new_svg(520, 386, 'a = (3, 4) and b = (2, 1). Their dot product is 10. The angle between them is about '
                          '26.6 degrees. The shadow of a on the line of b has length 10 over root 5, about 4.47, '
                          'and its foot is (4, 2)')
    A = Axes(s, 50, 320, 56, (0, 6), (0, 5))
    A.seg((0, 0), (5.6, 2.8), GREY, 1.2, '5 4')
    A.seg(a, foot, GREY, 1.4, '4 3')
    A.seg((0, 0), foot, ACCENT, 6)
    varrow(A, (0, 0), a, PIX, 2.6)
    varrow(A, (0, 0), b, ORANGE, 2.8)
    A.label(a, 'a = (3, 4), |a| = 5', 8, 4, PIX, 'start', 12, 'bold')
    A.label(b, 'b = (2, 1), |b| = √5', 10, 22, ORANGE, 'start', 12, 'bold')
    A.label(foot, "a's shadow on b: 10 / √5 ≈ 4.47", 10, 20, ACCENT, 'start', 12, 'bold')
    s.text(260, 356, 'a · b = 3×2 + 4×1 = 10 = |a| |b| cos θ = shadow length × |b|', 12)
    s.text(260, 374, 'cos θ = 10 / (5 × √5) ≈ 0.894, so the angle θ between a and b ≈ 26.6°', 12)
    s.save('vec-dot-angle.svg', OUT)


def vec_lambert():
    n = (0, 1)
    cases = ((90, 'overhead'), (60, '60° up'), (30, '30° up'), (-20, 'below the surface'))
    vals = []
    for deg, _ in cases:
        L = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
        vals.append(max(0.0, dot(n, L)))
    assert [round(v, 3) for v in vals] == [1.0, 0.866, 0.5, 0.0]
    s = new_svg(680, 280, 'Diffuse (Lambert) lighting, brightness = max(0, N dot L). Light overhead: 1. Light 60 '
                          'degrees up: 0.866. Light 30 degrees up: 0.5. Light below the surface: N dot L is negative, '
                          'so the brightness is 0')
    for k, ((deg, title), v) in enumerate(zip(cases, vals)):
        cx, cy = 90 + k * 168, 170
        s.rect(cx - 70, cy, 140, 14, f'rgb({int(40 + 215 * v)},{int(40 + 200 * v)},{int(30 + 120 * v)})', INK, 1)
        sarrow(s, cx, cy, cx, cy - 70, INK, 2.4)
        s.text(cx + 10, cy - 62, 'N', 13, INK, 'start', 'bold')
        a = math.radians(deg)
        sarrow(s, cx, cy, cx + 70 * math.cos(a), cy - 70 * math.sin(a), ORANGE, 2.4)
        s.text(cx + 82 * math.cos(a), cy - 82 * math.sin(a) + 4, 'L', 13, ORANGE, 'middle', 'bold')
        s.text(cx, 34, title, 12, weight='bold')
        s.text(cx, 212, f'N · L = {dot(n, (math.cos(a), math.sin(a))):.3f}'.replace('-', '−'), 12)
        s.text(cx, 232, f'brightness {v:.3f}'.rstrip('0').rstrip('.'), 12, TRUE, weight='bold')
    s.text(340, 266, 'The surface colour (strip) is the material colour times max(0, N · L).', 11)
    s.save('vec-lambert.svg', OUT)


def vec_reflection():
    n, l = (0, 1), (-0.6, 0.8)
    nl = dot(n, l)
    r = sub(scale(2 * nl, n), l)
    assert abs(nl - 0.8) < 1e-12 and close(r, (0.6, 0.8))
    s = new_svg(470, 330, 'Reflecting the light direction L = (minus 0.6, 0.8) about the normal N = (0, 1). N dot L '
                          '= 0.8, so 2(N dot L)N = (0, 1.6), and R = 2(N dot L)N minus L = (0.6, 0.8): the mirror image '
                          'of L on the other side of N')
    A = Axes(s, 35, 265, 100, (-2, 2), (0, 2), ticks=False)
    s.rect(A.X(-1.3), A.Y(0), A.X(1.3) - A.X(-1.3), 14, '#e5e7eb', INK, 1.5)
    varrow(A, (0, 0), n, INK, 2.6)
    varrow(A, (0, 0), l, ORANGE, 2.8)
    varrow(A, (0, 0), r, TRUE, 2.8)
    A.seg(l, (0, 0.8), GREY, 1.2, '4 3')
    A.seg((0, 0.8), r, GREY, 1.2, '4 3')
    A.seg((0, 1), (0, 1.6), ACCENT, 2.4, '6 3')
    A.dot((0, 0.8), ACCENT, 4)
    A.label(n, 'N = (0, 1)', 10, 6, INK, 'start', 12, 'bold')
    A.label(l, 'L = (−0.6, 0.8)', -6, -8, ORANGE, 'end', 12, 'bold')
    A.label(r, 'R = (0.6, 0.8)', 6, -8, TRUE, 'start', 12, 'bold')
    A.label((0, 1.6), '2(N·L)N = (0, 1.6)', 10, 4, ACCENT, 'start', 11, 'bold')
    A.label((0, 0.8), '(N·L)N', -10, 16, ACCENT, 'end', 11)
    s.text(235, 322, 'R = 2(N·L)N − L: the same angle to N as L, on the other side.', 12)
    s.save('vec-reflection.svg', OUT)


def vec_cross_normal():
    a, b, c = (1, 0, 0), (0, 2, 0), (0, 0, 2)
    e1, e2 = sub(b, a), sub(c, a)
    nrm = cross(e1, e2)
    assert e1 == (-1, 2, 0) and e2 == (-1, 0, 2) and nrm == (4, 2, 2)
    assert dot(nrm, e1) == 0 and dot(nrm, e2) == 0
    assert cross(e2, e1) == (-4, -2, -2)
    unit = scale(1 / length(nrm), nrm)
    assert round(length(nrm), 3) == 4.899 and close(tuple(round(x, 3) for x in unit), (0.816, 0.408, 0.408))
    s = new_svg(470, 360, 'Triangle A (1, 0, 0), B (0, 2, 0), C (0, 0, 2) drawn in 3D. Edge e1 = B minus A = '
                          '(minus 1, 2, 0) and edge e2 = C minus A = (minus 1, 0, 2). Their cross product e1 cross e2 = '
                          '(4, 2, 2) is perpendicular to both edges: it is the triangle\'s normal')
    sc = 70

    def P(p):          # simple oblique projection: x to the lower left, y right, z up
        x, y, z = p
        return 210 + sc * (y - 0.55 * x), 250 - sc * (z - 0.35 * x)
    for q, name in (((1.6, 0, 0), 'x'), ((0, 3, 0), 'y'), ((0, 0, 2.8), 'z')):
        x1, y1 = P((0, 0, 0))
        x2, y2 = P(q)
        sarrow(s, x1, y1, x2, y2, GREY, 1.4)
        s.text(x2 + 8, y2 + 4, name, 12, GREY, 'start', 'bold')
    pts = [P(a), P(b), P(c)]
    s.add('<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) +
          f'" fill="rgba(59,130,246,0.18)" stroke="{INK}" stroke-width="1.8"/>')
    sarrow(s, *P(a), *P(b), PIX, 2.6)
    sarrow(s, *P(a), *P(c), ORANGE, 2.6)
    cen = tuple(sum(v) / 3 for v in zip(a, b, c))
    tip = add(cen, scale(0.55, unit))
    sarrow(s, *P(cen), *P(tip), TRUE, 3)
    for p, name, dx, dy in ((a, 'A (1, 0, 0)', -16, 2), (b, 'B (0, 2, 0)', 8, 16), (c, 'C (0, 0, 2)', 10, -4)):
        x, y = P(p)
        s.circle(x, y, 4, INK)
        s.text(x + dx, y + dy, name, 12, INK, 'end' if dx < 0 else 'start', 'bold')
    xm, ym = P(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0))
    s.text(xm + 6, ym + 18, 'e1 = (−1, 2, 0)', 12, PIX, 'start', 'bold')
    xm, ym = P(((a[0] + c[0]) / 2, 0, (a[2] + c[2]) / 2))
    s.text(xm - 10, ym + 4, 'e2 = (−1, 0, 2)', 12, ORANGE, 'end', 'bold')
    xt, yt = P(tip)
    s.text(xt + 8, yt - 4, 'normal e1 × e2 = (4, 2, 2)', 12, TRUE, 'start', 'bold')
    s.text(235, 346, 'Check: (4, 2, 2)·e1 = −4 + 4 + 0 = 0 and (4, 2, 2)·e2 = −4 + 0 + 4 = 0.', 12)
    s.save('vec-cross-normal.svg', OUT)


# ---------- Curves 1: Bézier curves from straight lines ----------

Q0, Q1, Q2 = (0, 0), (2, 4), (4, 0)


def quad_curve_pts(n=80, t0=0.0, t1=1.0):
    return [quad_bezier(Q0, Q1, Q2, t0 + (t1 - t0) * i / n) for i in range(n + 1)]


def curve_lerp_of_lerps():
    q, r = lerp(Q0, Q1, 0.5), lerp(Q1, Q2, 0.5)
    c = lerp(q, r, 0.5)
    assert q == (1, 2) and r == (3, 2) and c == (2, 2) and quad_bezier(Q0, Q1, Q2, 0.5) == (2, 2)
    s = new_svg(470, 340, 'Lerp of lerps at t = 0.5 for P0 (0, 0), P1 (2, 4), P2 (4, 0). Step 1: Q, halfway along '
                          'P0P1, is (1, 2). Step 2: R, halfway along P1P2, is (3, 2). Step 3: halfway along QR is '
                          '(2, 2), a point on the curve, below P1')
    A = Axes(s, 50, 290, 60, (0, 6), (0, 4))
    A.seg(Q0, Q1, GREY, 1.6, '6 4')
    A.seg(Q1, Q2, GREY, 1.6, '6 4')
    A.poly(quad_curve_pts(), TRUE, 2.6, close=False)
    A.seg(q, r, ACCENT, 2.2)
    for p, name, dx, dy, anchor in ((Q0, 'P0 (0, 0)', 8, 16, 'start'), (Q1, 'P1 (2, 4)', 8, -2, 'start'),
                                    (Q2, 'P2 (4, 0)', -8, 16, 'end')):
        A.dot(p, INK)
        A.label(p, name, dx, dy, anchor=anchor, weight='bold')
    A.dot(q, ORANGE, 5.5)
    A.dot(r, ORANGE, 5.5)
    A.label(q, '1. Q (1, 2)', -10, 0, ORANGE, 'end', 12, 'bold')
    A.label(r, '2. R (3, 2)', 10, 0, ORANGE, 'start', 12, 'bold')
    A.dot(c, TRUE, 6)
    A.label(c, '3. C (2, 2)', 0, 22, TRUE, 'middle', 12, 'bold')
    s.text(235, 330, 'Same line formula three times, all at t = 0.5. Red: the curve.', 12)
    s.save('curve-lerp-of-lerps.svg', OUT)


FROZEN = {0.25: ((0.5, 1), (2.5, 3), (1, 1.5)), 0.5: ((1, 2), (3, 2), (2, 2)), 0.75: ((1.5, 3), (3.5, 1), (3, 1.5))}


def curve_frozen_t():
    for t, (q, r, c) in FROZEN.items():
        assert close(lerp(Q0, Q1, t), q) and close(lerp(Q1, Q2, t), r) and close(lerp(q, r, t), c)
        assert close(quad_bezier(Q0, Q1, Q2, t), c)
    s = new_svg(680, 306, 'Freeze t at one value at a time. t = 0.25: Q (0.5, 1), R (2.5, 3), C (1, 1.5). t = 0.5: '
                          'Q (1, 2), R (3, 2), C (2, 2). t = 0.75: Q (1.5, 3), R (3.5, 1), C (3, 1.5). Each time C is '
                          'one point on the segment QR, t of the way along, and it lies on the curve')
    for k, (t, (q, r, c)) in enumerate(FROZEN.items()):
        A = Axes(s, 30 + k * 220, 235, 45, (0, 4), (0, 4), ticks=False)
        A.seg(Q0, Q1, GREY, 1.4, '5 4')
        A.seg(Q1, Q2, GREY, 1.4, '5 4')
        A.poly(quad_curve_pts(), '#fca5a5', 2, close=False)
        A.poly(quad_curve_pts(t1=t), TRUE, 2.8, close=False)
        A.seg(q, r, ACCENT, 2)
        A.dot(q, ORANGE, 5)
        A.dot(r, ORANGE, 5)
        A.dot(c, TRUE, 6)
        A.label(q, 'Q', -8, -2, ORANGE, 'end', 12, 'bold')
        A.label(r, 'R', 8, -2, ORANGE, 'start', 12, 'bold')
        A.label(c, 'C', 0, 20, TRUE, 'middle', 12, 'bold')
        s.text(A.X(2), 30, f't = {t}', 14, weight='bold')
        s.text(A.X(2), 258, f'Q {q}  R {r}', 11)
        s.text(A.X(2), 276, f'C {c}', 11, TRUE, weight='bold')
    s.text(340, 298, 'Dark red: the curve traced so far, up to this t.', 11)
    s.save('curve-frozen-t.svg', OUT)


def curve_rounded_corner():
    s = new_svg(470, 330, 'The two control-polygon lines P0P1 and P1P2 make a sharp corner like the letter lambda. '
                          'The green lines are the segments QR for t = 0.1, 0.2 and so on to 0.9. The curve touches '
                          'each one at one point and rounds the corner off, leaning toward P1 without reaching it')
    A = Axes(s, 50, 290, 60, (0, 6), (0, 4))
    A.seg(Q0, Q1, INK, 2.4)
    A.seg(Q1, Q2, INK, 2.4)
    for i in range(1, 10):
        t = i / 10
        q, r = lerp(Q0, Q1, t), lerp(Q1, Q2, t)
        c = lerp(q, r, t)
        assert close(c, quad_bezier(Q0, Q1, Q2, t))
        A.seg(q, r, ACCENT, 1.2)
        A.dot(c, TRUE, 3)
    A.poly(quad_curve_pts(), TRUE, 2.8, close=False)
    assert quad_bezier(Q0, Q1, Q2, 0.5)[1] == 2 < Q1[1]
    for p, name, dx, dy, anchor in ((Q0, 'P0', 8, 16, 'start'), (Q1, 'P1: the corner', 10, 0, 'start'),
                                    (Q2, 'P2', -8, 16, 'end')):
        A.dot(p, INK)
        A.label(p, name, dx, dy, anchor=anchor, weight='bold')
    s.text(235, 322, 'Sharp corner (black) → rounded corner (red). Green: the QR lines it touches.', 12)
    s.save('curve-rounded-corner.svg', OUT)


def curve_weights():
    for t in (0, 0.25, 0.5, 0.75, 1):
        w = ((1 - t) ** 2, 2 * (1 - t) * t, t * t)
        assert abs(sum(w) - 1) < 1e-12
    assert (0.25, 0.5, 0.25) == ((1 - 0.5) ** 2, 2 * 0.5 * 0.5, 0.5 ** 2)
    s = new_svg(470, 400, 'The three quadratic Bezier weights plotted against t from 0 to 1. (1 minus t) squared on '
                          'P0 starts at 1 and falls to 0. 2(1 minus t)t on P1 rises to 0.5 at t = 0.5 and falls back. '
                          't squared on P2 rises from 0 to 1. At every t they add up to 1')
    A = Axes(s, 70, 330, 300, (0, 1), (0, 1), ticks=False)
    for i in range(11):
        v = i / 10
        s.text(A.X(v), A.Y(0) + 16, f'{v:g}', 10)
        s.text(A.X(0) - 8, A.Y(v) + 4, f'{v:g}', 10, anchor='end')
    fns = (((lambda t: (1 - t) ** 2), PIX, '(1 − t)² on P0', (0.2, 0.9)),
           ((lambda t: 2 * (1 - t) * t), ORANGE, '2(1 − t)t on P1', (0.5, 0.56)),
           ((lambda t: t * t), ACCENT, 't² on P2', (0.8, 0.9)))
    for f, col, name, at in fns:
        A.poly([(i / 100, f(i / 100)) for i in range(101)], col, 2.6, close=False)
        A.label(at, name, 0, 0, col, 'middle', 12, 'bold')
    A.seg((0.5, 0), (0.5, 0.5), GREY, 1, '3 3')
    A.label((0.5, 0.25), 't = 0.5: ¼ + ½ + ¼ = 1', 6, 40, INK, 'start', 11)
    s.text(220, 366, 't', 13, weight='bold')
    s.text(235, 386, 'P0 leads early, P1 pulls hardest in the middle, P2 takes over at the end.', 11)
    s.save('curve-weights.svg', OUT)


def curve_pascal_triangle():
    rows = [[math.comb(n, k) for k in range(n + 1)] for n in range(5)]
    assert rows[2] == [1, 2, 1] and rows[3] == [1, 3, 3, 1] and rows[4] == [1, 4, 6, 4, 1]
    names = ('', 'linear: a line', 'quadratic', 'cubic', 'quartic')
    s = new_svg(520, 260, "Pascal's triangle, rows 0 to 4: 1; 1 1; 1 2 1; 1 3 3 1; 1 4 6 4 1. Each number is the sum "
                          'of the two above it. Row n gives the weights of a degree n Bezier curve: row 1 a line, '
                          'row 2 the quadratic 1 2 1, row 3 the cubic 1 3 3 1')
    for n, row in enumerate(rows):
        y = 50 + n * 42
        s.text(40, y + 5, f'row {n}', 12, GREY, 'start')
        for k, v in enumerate(row):
            x = 230 + (k - n / 2) * 52
            hl = n in (2, 3)
            s.circle(x, y, 16, '#fef3c7' if hl else '#f3f4f6', ORANGE if hl else GREY)
            s.text(x, y + 5, v, 14, INK, 'middle', 'bold')
        if names[n]:
            s.text(370, y + 5, names[n], 12, ORANGE if n in (2, 3) else INK, 'start', 'bold' if n in (2, 3) else 'normal')
    s.text(260, 248, 'Each number = the two above it added. Row n = the weights of a degree-n Bézier.', 11)
    s.save('curve-pascal-triangle.svg', OUT)


C4 = [(0, 0), (1, 4), (5, 4), (6, 0)]


def curve_cubic_layers():
    lv = de_casteljau_levels(C4, 0.5)
    assert lv[1] == [(0.5, 2), (3, 4), (5.5, 2)]
    assert lv[2] == [(1.75, 3), (4.25, 3)]
    assert lv[3] == [(3, 3)] and close(bezier(C4, 0.5), (3, 3))
    s = new_svg(500, 330, 'A cubic Bezier built in layers at t = 0.5 from P0 (0, 0), P1 (1, 4), P2 (5, 4), P3 (6, 0). '
                          'Layer 1: three lines give Q (0.5, 2), R (3, 4), S (5.5, 2). Layer 2: two lines give '
                          'T (1.75, 3) and U (4.25, 3). Layer 3: one line gives the curve point (3, 3)')
    A = Axes(s, 40, 290, 60, (0, 7), (0, 4))
    A.poly(C4, GREY, 1.6, close=False, dash='6 4')
    pts = [bezier(C4, i / 80) for i in range(81)]
    A.poly(pts, TRUE, 2.6, close=False)
    A.poly(lv[1], ORANGE, 1.8, close=False)
    A.seg(lv[2][0], lv[2][1], ACCENT, 1.8)
    for p, name, dx, dy, anchor in ((C4[0], 'P0', 8, 16, 'start'), (C4[1], 'P1', -8, -6, 'end'),
                                    (C4[2], 'P2', 8, -6, 'start'), (C4[3], 'P3', -8, 16, 'end')):
        A.dot(p, INK)
        A.label(p, name, dx, dy, anchor=anchor, weight='bold')
    for p, name, dx, anchor in zip(lv[1], ('Q', 'R', 'S'), (-10, 0, 10), ('end', 'middle', 'start')):
        A.dot(p, ORANGE, 5)
        A.label(p, f'{name} ({p[0]:g}, {p[1]:g})', {'Q': 10, 'R': 0, 'S': -10}[name], {'Q': 18, 'R': -10, 'S': 18}[name], ORANGE, {'Q': 'start', 'R': 'middle', 'S': 'end'}[name], 11, 'bold')
    for p, name, dx, anchor in zip(lv[2], ('T', 'U'), (-10, 10), ('end', 'start')):
        A.dot(p, ACCENT, 5)
        A.label(p, f'{name} ({p[0]:g}, {p[1]:g})', dx, -8, ACCENT, anchor, 11, 'bold')
    A.dot(lv[3][0], TRUE, 6)
    A.label(lv[3][0], '(3, 3)', 0, 22, TRUE, 'middle', 12, 'bold')
    s.text(250, 322, 'Grey: 3 starting lines. Orange: layer 1 (3 points). Green: layer 2 (2). Red dot: layer 3 (1).', 11)
    s.save('curve-cubic-layers.svg', OUT)


def curve_degree_pattern():
    sets = (([(0, 0), (4, 3)], 'Linear: 2 points, 1 line'),
            ([(0, 0), (2, 4), (4, 0)], 'Quadratic: 3 points, 2 lines'),
            ([(0, 0), (1, 4), (3, -1), (4, 3)], 'Cubic: 4 points, 3 lines'))
    s = new_svg(660, 305, 'Linear Bezier: 2 control points, a straight line, degree 1. Quadratic: 3 control points, '
                          'one bend, degree 2. Cubic: 4 control points, can bend twice like an S, degree 3')
    for k, (ps, title) in enumerate(sets):
        A = Axes(s, 30 + k * 215, 245, 36, (0, 4), (-1, 4), ticks=False)
        A.poly(ps, GREY, 1.4, close=False, dash='5 4')
        A.poly([bezier(ps, i / 80) for i in range(81)], TRUE, 2.6, close=False)
        for p in ps:
            A.dot(p, INK, 4)
        s.text(A.X(2), 272, title, 12, weight='bold')
        s.text(A.X(2), 292, f'degree {len(ps) - 1}', 12, TRUE)
    s.text(330, 24, 'Each extra point adds one layer of blending and one more bend', 13, weight='bold')
    s.save('curve-degree-pattern.svg', OUT)


def curve_t_outside():
    pm = quad_bezier(Q0, Q1, Q2, -0.5)
    pp = quad_bezier(Q0, Q1, Q2, 1.5)
    assert close(pm, (-2, -6)) and close(pp, (6, -6))
    assert close(((1 - -0.5) ** 2, 2 * (1 - -0.5) * -0.5, 0.25), (2.25, -1.5, 0.25))
    s = new_svg(470, 438, 'The quadratic Bezier with P0 (0, 0), P1 (2, 4), P2 (4, 0). For t from 0 to 1 it is the '
                          'red arch. For t below 0 or above 1 (grey dashes) the formula keeps going and swings down, '
                          'reaching (minus 2, minus 6) at t = minus 0.5 and (6, minus 6) at t = 1.5')
    A = Axes(s, 50, 395, 34, (-3, 7), (-7, 4))
    A.poly(quad_curve_pts(40, -0.5, 0), GREY, 2, close=False, dash='6 4')
    A.poly(quad_curve_pts(40, 1, 1.5), GREY, 2, close=False, dash='6 4')
    A.poly(quad_curve_pts(), TRUE, 3, close=False)
    A.poly([Q0, Q1, Q2], '#d1d5db', 1.2, close=False)
    for p, name in ((Q0, 'P0'), (Q1, 'P1'), (Q2, 'P2')):
        A.dot(p, INK, 4)
        A.label(p, name, 8, -4, weight='bold')
    A.dot(pm, GREY, 5)
    A.dot(pp, GREY, 5)
    A.label(pm, 't = −0.5: (−2, −6)', 8, 4, GREY, 'start', 11, 'bold')
    A.label(pp, 't = 1.5: (6, −6)', -8, 4, GREY, 'end', 11, 'bold')
    s.text(235, 428, 'Red: 0 ≤ t ≤ 1, the curve you designed. Outside it, weights go negative.', 11)
    s.save('curve-t-outside.svg', OUT)


# ---------- Curves 5: other curve families ----------

def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def hermite(p0, p1, m0, m1, t):
    h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
    h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
    return tuple(h00 * a + h10 * b + h01 * c + h11 * d for a, b, c, d in zip(p0, m0, p1, m1))


def lagrange(xs, ys, x):
    total = 0.0
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        term = yi
        for j, xj in enumerate(xs):
            if j != i:
                term *= (x - xj) / (xi - xj)
        total += term
    return total


def curve_families():
    P = [(0, 0), (1, 3), (3, 3), (4, 0)]
    # Catmull-Rom through P1..P2 needs neighbours: pad the ends by repeating them
    ext = [P[0]] + P + [P[-1]]
    cr = []
    for i in range(1, len(ext) - 2):
        for k in range(21):
            cr.append(catmull_rom(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], k / 20))
    for p in P:
        assert any(close(p, q, 1e-9) for q in cr)                       # passes through every point
    bz = [bezier(P, i / 80) for i in range(81)]
    assert not any(close(P[1], q, 1e-3) for q in bz)                    # Bezier misses the middle points
    m0, m1 = (3, 6), (3, -6)
    he = [hermite(P[0], P[3], m0, m1, i / 80) for i in range(81)]
    assert close(he[0], P[0]) and close(he[-1], P[3])
    xs, ys = [0, 1, 2, 3, 4, 5, 6], [0, 0, 0, 1, 0, 0, 0]
    lg = [(x / 20, lagrange(xs, ys, x / 20)) for x in range(121)]
    for x, y in zip(xs, ys):
        assert abs(lagrange(xs, ys, x) - y) < 1e-9
    assert min(y for _, y in lg) < -0.2                                 # it wiggles below the flat data
    s = new_svg(680, 520, 'Four curve families. Bezier: pulled toward the control points, touches only the ends. '
                          'Catmull-Rom: passes through every point. Hermite: two end points plus a tangent arrow at '
                          'each end. Lagrange through 7 points that are flat except one bump: it passes through all '
                          'of them but wiggles below zero between them')
    panels = ((30, 60, 'Bézier: pulled, touches only the ends'), (370, 60, 'Catmull-Rom: through every point'),
              (30, 300, 'Hermite: ends + a direction at each end'), (370, 300, 'Lagrange: through all, but wiggles'))
    for k, (x0, y0, title) in enumerate(panels):
        s.text(x0 + 140, y0 - 30, title, 12, weight='bold')
        if k < 3:
            A = Axes(s, x0 + 40, y0 + 160, 48, (0, 4), (0, 3), ticks=False)
            A.poly(P, GREY, 1.2, close=False, dash='5 4') if k < 2 else None
            A.poly(bz if k == 0 else (cr if k == 1 else he), TRUE, 2.6, close=False)
            if k < 2:
                for p in P:
                    A.dot(p, INK, 4)
            else:
                A.dot(P[0], INK, 4)
                A.dot(P[3], INK, 4)
                varrow(A, P[0], add(P[0], scale(1 / 6, m0)), ORANGE, 2.4)
                varrow(A, sub(P[3], scale(1 / 6, m1)), P[3], ORANGE, 2.4)
                A.label(add(P[0], scale(1 / 6, m0)), 'start tangent', 6, 4, ORANGE, 'start', 11, 'bold')
                A.label(sub(P[3], scale(1 / 6, m1)), 'end tangent', 6, -6, ORANGE, 'start', 11, 'bold')
        else:
            A = Axes(s, x0 + 10, y0 + 130, 44, (0, 6), (-1, 2), ticks=False)
            A.seg((0, 0), (6, 0), '#e5e7eb', 1)
            A.poly(lg, TRUE, 2.4, close=False)
            for x, y in zip(xs, ys):
                A.dot((x, y), INK, 4)
    s.text(340, 510, 'Bézier and B-splines approximate (pulled toward points); Catmull-Rom, Hermite ends and Lagrange interpolate (pass through).', 11)
    s.save('curve-families.svg', OUT)


def curve_nurbs_quarter_circle():
    P = [(1, 0), (1, 1), (0, 1)]
    w = (1, math.sqrt(2) / 2, 1)

    def rational(t):
        b = ((1 - t) ** 2, 2 * (1 - t) * t, t * t)
        den = sum(bi * wi for bi, wi in zip(b, w))
        return tuple(sum(bi * wi * p[k] for bi, wi, p in zip(b, w, P)) / den for k in range(2))
    nurbs = [rational(i / 80) for i in range(81)]
    plain = [quad_bezier(*P, i / 80) for i in range(81)]
    err_n = max(abs(length(p) - 1) for p in nurbs)
    err_b = max(abs(length(p) - 1) for p in plain)
    assert err_n < 1e-12 and round(err_b, 3) == 0.061 and length(plain[40]) > 1
    s = new_svg(470, 360, 'A quarter circle of radius 1 from (1, 0) to (0, 1) with corner control point (1, 1). The '
                          'plain quadratic Bezier (orange) bulges outward, up to 0.061 off the circle. Giving the '
                          'corner point a weight of root 2 over 2 (NURBS, red) lands exactly on the circle')
    A = Axes(s, 70, 320, 260, (0, 1), (0, 1), ticks=False)
    A.poly(P, GREY, 1.2, close=False, dash='5 4')
    A.poly([(math.cos(a / 60 * math.pi / 2), math.sin(a / 60 * math.pi / 2)) for a in range(61)], INK, 6, close=False)
    A.poly(plain, ORANGE, 2.4, close=False)
    A.poly(nurbs, TRUE, 2.2, close=False, dash='8 4')
    for p, name in zip(P, ('(1, 0)', '(1, 1), weight √2/2 ≈ 0.707', '(0, 1)')):
        A.dot(p, INK, 4)
        A.label(p, name, 8, -6 if p != (1, 0) else 16, INK, 'start' if p != (1, 1) else 'end', 11, 'bold')
    A.label((0.06, 0.42), 'orange, plain Bézier: bulges out by up to 0.061', 0, 0, ORANGE, 'start', 11, 'bold')
    A.label((0.06, 0.32), 'red dashes, NURBS: exactly on the circle', 0, 0, TRUE, 'start', 11, 'bold')
    s.text(235, 352, 'Thick black: the true circle. A weight on each control point is the extra knob NURBS adds.', 11)
    s.save('curve-nurbs-quarter-circle.svg', OUT)


# ---------- Curves 3: the cubic, its velocity and end conditions ----------

def bezier_deriv(ps, t):
    n = len(ps) - 1
    qs = [scale(n, sub(ps[i + 1], ps[i])) for i in range(n)]
    return bezier(qs, t)


def curve_end_conditions():
    p0, p3, v0, v1 = (1, 2), (7, 3), (3, 6), (-6, 3)
    p1, p2 = add(p0, scale(1 / 3, v0)), sub(p3, scale(1 / 3, v1))
    assert close(p1, (2, 4)) and close(p2, (9, 2))
    P = [p0, p1, p2, p3]
    assert close(bezier_deriv(P, 0), v0) and close(bezier_deriv(P, 1), v1)
    s = new_svg(500, 360, 'A cubic Bezier from P0 (1, 2) to P3 (7, 3) with start velocity (3, 6) and end velocity '
                          '(minus 6, 3). The control points are a third of each velocity from the ends: P1 = P0 + v0 '
                          'over 3 = (2, 4) and P2 = P3 minus v1 over 3 = (9, 2)')
    A = Axes(s, 40, 310, 42, (0, 10), (0, 6))
    A.poly(P, GREY, 1.4, close=False, dash='6 4')
    A.poly([bezier(P, i / 80) for i in range(81)], TRUE, 2.8, close=False)
    varrow(A, p0, add(p0, scale(0.5, v0)), '#fbbf24', 1.6, '4 3')
    varrow(A, p0, p1, ORANGE, 3)
    varrow(A, p2, p3, PIX, 3)
    for p, name, dx, dy, anchor in ((p0, 'P0 (1, 2)', -8, 16, 'end'), (p1, 'P1 (2, 4)', -10, -4, 'end'),
                                    (p2, 'P2 (9, 2)', 8, 16, 'start'), (p3, 'P3 (7, 3)', 4, -10, 'end')):
        A.dot(p, INK)
        A.label(p, name, dx, dy, anchor=anchor, weight='bold')
    A.label(add(p0, scale(0.5, v0)), 'v0 = (3, 6), half drawn', 8, 0, '#b45309', 'start', 11)
    A.label(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), 'v0 / 3 = (1, 2)', 12, 18, ORANGE, 'start', 12, 'bold')
    A.label(((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2), 'v1 / 3 = (−2, 1)', 6, -12, PIX, 'start', 12, 'bold')
    s.text(250, 350, "B'(0) = 3(P1 − P0) = v0 and B'(1) = 3(P3 − P2) = v1, so each arrow is a third of a velocity.", 11)
    s.save('curve-end-conditions.svg', OUT)


def curve_slopes_choice():
    p0, p3, m0, m1 = (0, 5), (6, 1), 2, 3
    s = new_svg(420, 410, 'Two cubic Beziers through (0, 5) with slope 2 and (6, 1) with slope 3. With a = b = 1 the '
                          'control points are (1, 7) and (5, minus 2); with a = b = 2 they are (2, 9) and (4, minus 5). '
                          'Same end points, same end slopes, different curves')
    A = Axes(s, 80, 372, 21, (-1, 8), (-6, 10))
    for a, col, dash in ((1, ORANGE, None), (2, TRUE, None)):
        p1 = add(p0, scale(a, (1, m0)))
        p2 = sub(p3, scale(a, (1, m1)))
        P = [p0, p1, p2, p3]
        d0, d1 = bezier_deriv(P, 0), bezier_deriv(P, 1)
        assert abs(d0[1] / d0[0] - m0) < 1e-12 and abs(d1[1] / d1[0] - m1) < 1e-12
        A.poly(P, col, 1.2, close=False, dash='4 4')
        A.poly([bezier(P, i / 80) for i in range(81)], col, 2.6, close=False)
        for q in (p1, p2):
            A.dot(q, col, 4.5)
            A.label(q, f'({q[0]:g}, {q[1]:g})', 8, 4, col, 'start', 11, 'bold')
    for p, name in ((p0, '(0, 5), slope 2'), (p3, '(6, 1), slope 3')):
        A.dot(p, INK, 5)
        A.label(p, name, -8, -8 if p == p0 else 18, INK, 'end', 11, 'bold')
    s.text(210, 22, 'Orange: a = b = 1.   Red: a = b = 2.', 12, weight='bold')
    s.text(210, 404, 'A slope fixes the direction of P1 and P2 from the ends, not how far: state your choice.', 11)
    s.save('curve-slopes-choice.svg', OUT)


if __name__ == '__main__':
    vec_a_to_b()
    vec_point_vs_vector()
    vec_ab_vs_ba()
    vec_unit_vector()
    vec_add_and_scale()
    vec_point_vs_direction_w()
    vec_line_t()
    vec_journey_not_point()
    vec_one_third()
    vec_t_ranges()
    vec_lerp_colours()
    vec_ray_wall()
    vec_dot_signs()
    vec_dot_angle()
    vec_lambert()
    vec_reflection()
    vec_cross_normal()
    curve_lerp_of_lerps()
    curve_frozen_t()
    curve_rounded_corner()
    curve_weights()
    curve_pascal_triangle()
    curve_cubic_layers()
    curve_degree_pattern()
    curve_t_outside()
    curve_families()
    curve_nurbs_quarter_circle()
    curve_end_conditions()
    curve_slopes_choice()
