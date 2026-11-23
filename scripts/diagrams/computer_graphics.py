"""Draw the computer-graphics lesson diagrams as small SVG files.

    python3 scripts/diagrams/computer_graphics.py      # run from the vault root

Every picture is computed from the same algorithm the lesson teaches (Bresenham,
midpoint circle, Cohen-Sutherland codes, de Casteljau, rotation about a pivot),
so the diagram can't disagree with the worked example. No libraries needed.
Output: computer-graphics/images/*.svg. Each SVG has its own light background,
so it reads the same in light and dark mode.
"""
import math
import os

OUT = os.path.join('computer-graphics', 'images')

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, GRID, PIX, PIX2, TRUE, ACCENT, BG, Svg, flowchart  # noqa: E402


class PixelGrid:
    """A grid with the origin at the bottom-left, as in the lessons."""

    def __init__(self, svg, cols, rows, cell, left=40, top=20):
        self.s, self.cols, self.rows, self.c = svg, cols, rows, cell
        self.left, self.top = left, top

    def px(self, x):            # centre of column x
        return self.left + (x + 0.5) * self.c

    def py(self, y):            # centre of row y (y grows upward)
        return self.top + (self.rows - y - 0.5) * self.c

    def draw(self, label_every=1):
        s, c = self.s, self.c
        for i in range(self.cols + 1):
            s.line(self.left + i * c, self.top, self.left + i * c, self.top + self.rows * c, GRID, 1)
        for j in range(self.rows + 1):
            s.line(self.left, self.top + j * c, self.left + self.cols * c, self.top + j * c, GRID, 1)
        for x in range(0, self.cols, label_every):
            s.text(self.px(x), self.top + self.rows * c + 16, str(x), 11)
        for y in range(0, self.rows, label_every):
            s.text(self.left - 10, self.py(y) + 4, str(y), 11, anchor='end')

    def pixel(self, x, y, fill=PIX):
        pad = 1.5
        self.s.rect(self.left + x * self.c + pad, self.top + (self.rows - 1 - y) * self.c + pad,
                    self.c - 2 * pad, self.c - 2 * pad, fill)

    def true_line(self, x0, y0, x1, y1, color=TRUE):
        self.s.line(self.px(x0), self.py(y0), self.px(x1), self.py(y1), color, 2)


# ---------- the algorithms, exactly as the lessons state them ----------

def bresenham(x0, y0, x1, y1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx, sy = (1 if x1 >= x0 else -1), (1 if y1 >= y0 else -1)
    x, y, pts = x0, y0, [(x0, y0)]
    if dx >= dy:
        p = 2 * dy - dx
        for _ in range(dx):
            x += sx
            if p < 0:
                p += 2 * dy
            else:
                y += sy
                p += 2 * dy - 2 * dx
            pts.append((x, y))
    else:
        p = 2 * dx - dy
        for _ in range(dy):
            y += sy
            if p < 0:
                p += 2 * dx
            else:
                x += sx
                p += 2 * dx - 2 * dy
            pts.append((x, y))
    return pts


def midpoint_circle_octant(r):
    x, y, p = 0, r, 1 - r
    pts = [(x, y)]
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        pts.append((x, y))
    return [(a, b) for a, b in pts if a <= b]


def eight_way(pts):
    out = set()
    for x, y in pts:
        for a, b in ((x, y), (y, x), (-x, y), (-y, x), (x, -y), (y, -x), (-x, -y), (-y, -x)):
            out.add((a, b))
    return out


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def de_casteljau_levels(ps, t):
    levels = [ps]
    while len(levels[-1]) > 1:
        prev = levels[-1]
        levels.append([lerp(prev[i], prev[i + 1], t) for i in range(len(prev) - 1)])
    return levels


# ---------- the diagrams ----------

def bresenham_shallow():
    pts = bresenham(2, 3, 9, 8)
    assert pts == [(2, 3), (3, 4), (4, 4), (5, 5), (6, 6), (7, 7), (8, 7), (9, 8)]
    s = Svg(470, 380, 'Bresenham line from (2,3) to (9,8): eight lit pixels hug the true red line')
    g = PixelGrid(s, 12, 11, 30, left=45, top=15)
    g.draw()
    for x, y in pts:
        g.pixel(x, y)
    g.true_line(2, 3, 9, 8)
    s.text(g.px(2) - 22, g.py(3) + 4, 'start', 11, TRUE, 'end')
    s.text(g.px(9) + 4, g.py(8) - 18, 'end', 11, TRUE)
    s.text(235, 372, 'Blue: pixels Bresenham lights. Red: the true line. No pixel is more than ½ away.', 11)
    s.save('bresenham-2-3-to-9-8.svg', OUT)


def bresenham_steep_vs_wrong_axis():
    good = bresenham(0, 0, 2, 6)
    wrong = [(x, round(3 * x)) for x in range(3)]          # stepping the short axis
    s = Svg(470, 300, 'Line (0,0) to (2,6): stepping x leaves gaps; stepping y gives a solid line')
    for k, (pts, title) in enumerate(((wrong, 'Stepping x: 3 pixels, gaps'),
                                      (good, 'Stepping y: 7 pixels, solid'))):
        g = PixelGrid(s, 4, 7, 30, left=50 + k * 230, top=20)
        g.draw()
        for x, y in pts:
            g.pixel(x, y, PIX if k else '#f59e0b')
        g.true_line(0, 0, 2, 6)
        s.text(g.left + 60, 270, title, 12, weight='bold')
    s.save('line-stepping-the-right-axis.svg', OUT)


def midpoint_circle():
    r = 10
    octant = midpoint_circle_octant(r)
    assert octant == [(0, 10), (1, 10), (2, 10), (3, 10), (4, 9), (5, 9), (6, 8), (7, 7)]
    allpts = eight_way(octant)
    n = 2 * r + 3
    s = Svg(560, 560, 'Midpoint circle, radius 10: one computed octant (dark) mirrored eight ways (light)')
    g = PixelGrid(s, n, n, 22, left=45, top=15)
    off = r + 1                                         # shift so the centre is at (11, 11)
    g.draw(label_every=n + 1)
    s.parts = [x for x in s.parts if not x.startswith('<text')]   # coordinates aren't the point here
    for x, y in allpts:
        g.pixel(x + off, y + off, PIX2)
    for x, y in octant:
        g.pixel(x + off, y + off, PIX)
    cx, cy = g.px(off), g.py(off)
    rr = r * g.c
    s.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="none" stroke="{TRUE}" stroke-width="1.5"/>')
    s.line(cx, cy, g.px(off), g.py(off + r), INK, 1, '4 3')
    s.line(cx, cy, g.px(off + 7), g.py(off + 7), INK, 1, '4 3')
    s.circle(cx, cy, 3, INK)
    s.text(cx - 6, cy + 18, 'centre', 11, anchor='end')
    s.text(280, 546, 'Dark: the octant from (0,10) to (7,7) the algorithm computes. Light: its 7 mirror images.', 11)
    s.save('midpoint-circle-r10.svg', OUT)


def cohen_sutherland_regions():
    s = Svg(470, 360, 'Cohen-Sutherland: the window and its 8 neighbours, each with a 4-bit TBRL region code')
    x0, y0, w, h = 150, 110, 170, 130                  # window in screen space
    s.rect(x0, y0, w, h, '#dbeafe', ACCENT, 2)
    for x in (x0, x0 + w):
        s.line(x, 20, x, 330, INK, 1, '6 4')
    for y in (y0, y0 + h):
        s.line(30, y, 440, y, INK, 1, '6 4')
    cols = [(30 + x0) / 2, x0 + w / 2, (x0 + w + 440) / 2]
    rows = [(20 + y0) / 2, y0 + h / 2, (y0 + h + 330) / 2]
    codes = [['1001', '1000', '1010'], ['0001', '0000', '0010'], ['0101', '0100', '0110']]
    for r in range(3):
        for c in range(3):
            s.text(cols[c], rows[r] + 6, codes[r][c], 18, ACCENT if (r, c) == (1, 1) else INK, weight='bold')
    s.text(x0 + w / 2, y0 + h / 2 + 26, 'window', 12, ACCENT)
    s.text(235, 352, 'Bits in order Top, Bottom, Right, Left. 1 = beyond that edge.', 12)
    s.save('cohen-sutherland-region-codes.svg', OUT)


def bezier_de_casteljau():
    P = [(1, 2), (3, 8), (8, 9), (7, 3)]
    levels = de_casteljau_levels(P, 0.5)
    assert levels[-1][0] == (5.125, 7.0)
    s = Svg(470, 430, 'Cubic Bezier P0(1,2) P1(3,8) P2(8,9) P3(7,3) with de Casteljau at t = 1/2, giving B(1/2) = (5.125, 7)')
    sc, ox, oy = 40, 25, 392                        # 1 unit = 40 px, origin bottom-left
    X = lambda p: ox + p[0] * sc
    Y = lambda p: oy - p[1] * sc
    for i in range(0, 11):
        s.line(X((i, 0)), Y((0, 0)), X((i, 0)), Y((0, 9.3)), '#eef2f6', 1)
    for j in range(0, 10):
        s.line(X((0, 0)), Y((0, j)), X((10.5, 0)), Y((0, j)), '#eef2f6', 1)
    # control polygon
    s.path('M ' + ' L '.join(f'{X(p):.1f} {Y(p):.1f}' for p in P), INK, 1.2, dash='5 4')
    # de Casteljau construction lines
    colors = [None, '#f59e0b', ACCENT]
    for k in (1, 2):
        lv = levels[k]
        s.path('M ' + ' L '.join(f'{X(p):.1f} {Y(p):.1f}' for p in lv), colors[k], 1.5)
        for p in lv:
            s.circle(X(p), Y(p), 3.5, colors[k])
    # the curve itself
    pts = []
    for i in range(101):
        t = i / 100
        u = 1 - t
        b = [u ** 3, 3 * u * u * t, 3 * u * t * t, t ** 3]
        pts.append((sum(b[j] * P[j][0] for j in range(4)), sum(b[j] * P[j][1] for j in range(4))))
    s.path('M ' + ' L '.join(f'{X(p):.1f} {Y(p):.1f}' for p in pts), TRUE, 2.5)
    for i, p in enumerate(P):
        s.circle(X(p), Y(p), 5, INK)
        dx, dy = {0: (-14, 4), 1: (-14, -8), 2: (-16, -2), 3: (14, 12)}[i]
        s.text(X(p) + dx, Y(p) + dy, f'P{i}', 13, anchor='middle', weight='bold')
    b = levels[-1][0]
    s.circle(X(b), Y(b), 6, TRUE)
    s.text(X(b), Y(b) + 26, 'B(½)', 13, TRUE, 'middle', 'bold')
    s.text(235, 420, 'Dashed: control polygon. Orange, then green: de Casteljau at t = ½, giving B(½) = (5.125, 7).', 11)
    s.save('bezier-de-casteljau.svg', OUT)


def rotate_about_pivot():
    tri = [(3, 2), (5, 2), (3, 5)]
    pivot, th = (3, 2), math.radians(60)

    def rot(p):
        x, y = p[0] - pivot[0], p[1] - pivot[1]
        return (pivot[0] + x * math.cos(th) - y * math.sin(th), pivot[1] + x * math.sin(th) + y * math.cos(th))

    new = [rot(p) for p in tri]
    assert abs(new[1][0] - 4) < 1e-9 and abs(new[1][1] - (2 + math.sqrt(3))) < 1e-9
    s = Svg(470, 340, 'Triangle (3,2) (5,2) (3,5) rotated 60 degrees anticlockwise about the pivot (3,2)')
    sc, ox, oy = 55, 30, 320
    X = lambda p: ox + p[0] * sc
    Y = lambda p: oy - p[1] * sc
    for i in range(8):
        s.line(X((i, 0)), Y((0, 0)), X((i, 0)), Y((0, 5.5)), '#eef2f6', 1)
        s.text(X((i, 0)), oy + 14, str(i), 10)
    for j in range(6):
        s.line(X((0, 0)), Y((0, j)), X((7.5, 0)), Y((0, j)), '#eef2f6', 1)
        s.text(ox - 8, Y((0, j)) + 4, str(j), 10, anchor='end')
    poly = lambda ps: 'M ' + ' L '.join(f'{X(p):.1f} {Y(p):.1f}' for p in ps) + ' Z'
    s.path(poly(tri), INK, 2, fill='#e5e7eb')
    s.path(poly(new), PIX, 2.5, fill='#dbeafe')
    # the arc swept by (5,2)
    r = 2 * sc
    s.add(f'<path d="M {X((5, 2)):.1f} {Y((5, 2)):.1f} A {r} {r} 0 0 0 {X(new[1]):.1f} {Y(new[1]):.1f}" '
          f'stroke="{ACCENT}" stroke-width="1.5" fill="none" stroke-dasharray="4 3"/>')
    s.circle(X(pivot), Y(pivot), 5, TRUE)
    s.text(X(pivot), Y(pivot) + 20, 'pivot (3,2) stays put', 11, TRUE)
    s.text(X(new[1]) + 8, Y(new[1]) - 6, '(5,2) → (4, 3.73)', 11, PIX, 'start')
    s.text(235, 22, 'Grey: before. Blue: after a 60° anticlockwise rotation about the pivot.', 11)
    s.save('rotate-about-pivot.svg', OUT)


def square_rotated_30():
    sq = {'A': (-1, 1), 'B': (1, 1), 'C': (1, -1), 'D': (-1, -1)}
    c, sn = math.cos(math.radians(30)), math.sin(math.radians(30))
    rot = {k: (x * c - y * sn, x * sn + y * c) for k, (x, y) in sq.items()}
    assert abs(rot['B'][0] - 0.366) < 1e-3 and abs(rot['B'][1] - 1.366) < 1e-3
    s = Svg(560, 420, 'Square A(-1,1) B(1,1) C(1,-1) D(-1,-1) and its image after a 30 degree anticlockwise rotation about the origin')
    sc, ox, oy = 110, 280, 200
    X = lambda p: ox + p[0] * sc
    Y = lambda p: oy - p[1] * sc
    for v in (-1.5, -1, -0.5, 0.5, 1, 1.5):
        s.line(X((v, 0)), 20, X((v, 0)), 380, '#eef2f6', 1)
        s.line(100, Y((0, v)), 460, Y((0, v)), '#eef2f6', 1)
    s.line(100, oy, 460, oy, INK, 1)
    s.line(ox, 20, ox, 380, INK, 1)
    order = 'ABCD'
    poly = lambda d: 'M ' + ' L '.join(f'{X(d[k]):.1f} {Y(d[k]):.1f}' for k in order) + ' Z'
    s.path(poly(sq), INK, 2, fill='#e5e7eb')
    s.path(poly(rot), PIX, 2.5, fill='#dbeafe')
    for k in order:
        s.circle(X(rot[k]), Y(rot[k]), 4, PIX)
        x, y = rot[k]
        s.text(X(rot[k]) + (16 if x >= 0 else -16), Y(rot[k]) + (-8 if y >= 0 else 18),
               f"{k}' ({x:.2f}, {y:.2f})", 11, PIX, 'start' if x >= 0 else 'end', 'bold')
    s.text(280, 408, "Grey: the square. Blue: after rotating 30° anticlockwise. Labels keep the question's letters.", 11)
    s.save('square-rotated-30.svg', OUT)


def bezier_b9():
    P = [(0, 0), (2, 0), (0, 2), (4, 4)]
    b = de_casteljau_levels(P, 0.5)[-1][0]
    assert b == (1.25, 1.25)
    s = Svg(420, 420, 'Cubic Bezier P0(0,0) P1(2,0) P2(0,2) P3(4,4): it leaves P0 heading right, arrives at P3 from P2, and passes through B(1/2) = (1.25, 1.25)')
    sc, ox, oy = 80, 50, 370
    X = lambda p: ox + p[0] * sc
    Y = lambda p: oy - p[1] * sc
    for i in range(5):
        s.line(X((i, 0)), Y((0, 0)), X((i, 0)), Y((0, 4.3)), '#eef2f6', 1)
        s.line(X((0, 0)), Y((0, i)), X((4.3, 0)), Y((0, i)), '#eef2f6', 1)
        if i:
            s.text(X((i, 0)), oy + 16, str(i), 11)
            s.text(ox - 10, Y((0, i)) + 4, str(i), 11, anchor='end')
    s.path('M ' + ' L '.join(f'{X(p):.1f} {Y(p):.1f}' for p in P), INK, 1.2, dash='5 4')
    pts = []
    for i in range(101):
        t = i / 100
        u = 1 - t
        w = [u ** 3, 3 * u * u * t, 3 * u * t * t, t ** 3]
        pts.append((sum(w[j] * P[j][0] for j in range(4)), sum(w[j] * P[j][1] for j in range(4))))
    s.path('M ' + ' L '.join(f'{X(p):.1f} {Y(p):.1f}' for p in pts), TRUE, 2.5)
    labels = {0: (-18, 18), 1: (14, -10), 2: (-20, -8), 3: (-16, -8)}
    for i, p in enumerate(P):
        s.circle(X(p), Y(p), 5, INK)
        dx, dy = labels[i]
        s.text(X(p) + dx, Y(p) + dy, f'P{i}', 13, weight='bold')
    s.circle(X(b), Y(b), 6, TRUE)
    s.text(X(b) + 12, Y(b) + 18, 'B(½) = (1.25, 1.25)', 12, TRUE, 'start', 'bold')
    s.text(210, 410, 'Dashed: control polygon. Red: the curve, inside the hull of P0 to P3.', 11)
    s.save('bezier-b9.svg', OUT)


# ---------- more diagrams: one per idea the notes describe in words ----------

ORANGE = '#f59e0b'


class Axes:
    """Equal-scale data axes for geometry pictures (origin bottom-left)."""

    def __init__(self, s, x0, y0, sc, xr, yr, ticks=True):
        self.s, self.x0, self.y0, self.sc, self.xr, self.yr = s, x0, y0, sc, xr, yr
        for i in range(xr[0], xr[1] + 1):
            s.line(self.X(i), self.Y(yr[0]), self.X(i), self.Y(yr[1]), '#eef2f6', 1)
            if ticks:
                s.text(self.X(i), self.Y(yr[0]) + 15, str(i), 10)
        for j in range(yr[0], yr[1] + 1):
            s.line(self.X(xr[0]), self.Y(j), self.X(xr[1]), self.Y(j), '#eef2f6', 1)
            if ticks:
                s.text(self.X(xr[0]) - 7, self.Y(j) + 4, str(j), 10, anchor='end')

    def X(self, x):
        return self.x0 + (x - self.xr[0]) * self.sc

    def Y(self, y):
        return self.y0 - (y - self.yr[0]) * self.sc

    def seg(self, a, b, color=INK, width=2, dash=None):
        self.s.line(self.X(a[0]), self.Y(a[1]), self.X(b[0]), self.Y(b[1]), color, width, dash)

    def poly(self, pts, color, width=2, fill='none', close=True, dash=None):
        d = 'M ' + ' L '.join(f'{self.X(x):.1f} {self.Y(y):.1f}' for x, y in pts) + (' Z' if close else '')
        self.s.path(d, color, width, fill=fill, dash=dash)

    def dot(self, p, color, r=4.5):
        self.s.circle(self.X(p[0]), self.Y(p[1]), r, color)

    def label(self, p, text, dx=8, dy=-8, color=INK, anchor='start', size=11, weight='normal'):
        self.s.text(self.X(p[0]) + dx, self.Y(p[1]) + dy, text, size, color, anchor, weight)


def arrow_defs(s):
    s.add(f'<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
          f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')


def arrow(s, x1, y1, x2, y2, color=INK, width=1.6):
    s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
          f'stroke-width="{width}" marker-end="url(#arr)"/>')


def bresenham_two_distances():
    # x_k = 0, y_k = 0; the true line crosses column x_k + 1 at height 0.35
    s = Svg(470, 330, 'At column x_k + 1 the true line sits at height y between the lower pixel y_k and the upper '
                      'pixel y_k + 1; d_lower is the gap down to y_k and d_upper the gap up to y_k + 1')
    arrow_defs(s)
    c, ox, oy = 110, 90, 215
    X = lambda x: ox + x * c
    Y = lambda y: oy - y * c
    for x in (0, 1):
        for y in (0, 1):
            s.rect(X(x) - 18, Y(y) - 18, 36, 36, PIX if (x, y) == (0, 0) else '#ffffff', INK, 1.4)
    yt = 0.35
    s.line(X(-0.3), Y(-0.3 * 0.35), X(1.6), Y(1.6 * 0.35), TRUE, 2.2)
    s.circle(X(1), Y(yt), 5, TRUE)
    s.line(X(1) + 30, Y(0), X(1) + 30, Y(yt), INK, 1, None)
    for (a, b, lab) in ((0, yt, 'd_lower = y − y_k'), (yt, 1, 'd_upper = (y_k + 1) − y')):
        arrow(s, X(1) + 30, Y((a + b) / 2), X(1) + 30, Y(b) + 3)
        arrow(s, X(1) + 30, Y((a + b) / 2), X(1) + 30, Y(a) - 3)
        s.text(X(1) + 42, Y((a + b) / 2) + 4, lab, 12, INK, 'start')
    s.text(X(0), oy + 66, 'x_k', 13, weight='bold')
    s.text(X(1), oy + 66, 'x_k + 1', 13, weight='bold')
    s.text(ox - 40, Y(0) + 4, 'y_k', 13, anchor='end', weight='bold')
    s.text(ox - 40, Y(1) + 4, 'y_k + 1', 13, anchor='end', weight='bold')
    s.text(X(1) - 26, Y(yt) + 4, 'y', 13, TRUE, 'end', 'bold')
    s.text(X(0), Y(0) - 26, 'plotted', 11, PIX, weight='bold')
    s.text(X(1), Y(1) - 26, 'upper?', 11)
    s.text(X(1), Y(0) + 34, 'lower?', 11)
    s.text(235, 318, 'Pick the candidate the true line is nearer to: lower when d_lower < d_upper.', 11)
    s.save('bresenham-two-distances.svg', OUT)


def dda_example():
    # A(0,1) to B(5,5): x_inc = 1, y_inc = 0.8, y = 1, 1.8, 2.6, 3.4, 4.2, 5
    ys = [1 + 0.8 * i for i in range(6)]
    pts = [(i, math.floor(y + 0.5)) for i, y in enumerate(ys)]
    assert pts == [(0, 1), (1, 2), (2, 3), (3, 3), (4, 4), (5, 5)]
    s = Svg(400, 300, 'DDA from (0,1) to (5,5): the exact y values 1, 1.8, 2.6, 3.4, 4.2, 5 are rounded to pick each pixel')
    g = PixelGrid(s, 7, 7, 34, left=40, top=15)
    g.draw()
    for x, y in pts:
        g.pixel(x, y)
    g.true_line(0, 1, 5, 5)
    for i, y in enumerate(ys):
        s.circle(g.px(i), g.top + (g.rows - y - 0.5) * g.c, 3.5, TRUE)
        s.text(g.px(i) + 9, g.top + (g.rows - y - 0.5) * g.c + 15, f'{y:g}', 10, TRUE, 'start', 'bold')
    s.text(200, 292, 'Red dots: exact y each step. Blue: the rounded pixel DDA lights.', 11)
    s.save('dda-0-1-to-5-5.svg', OUT)


def antialiasing_compare():
    x1, y1 = 13, 5                      # line from (0,0) to (13,5), drawn 1 pixel wide
    cols, rows = 15, 7
    pts = set(bresenham(0, 0, x1, y1))
    L = math.hypot(x1, y1)

    def coverage(px, py):
        n, hit = 6, 0
        for i in range(n):
            for j in range(n):
                x, y = px - 0.5 + (i + 0.5) / n, py - 0.5 + (j + 0.5) / n
                t = max(0, min(1, (x * x1 + y * y1) / (L * L)))
                if math.hypot(x - t * x1, y - t * y1) <= 0.5:
                    hit += 1
        return hit / (n * n)

    s = Svg(560, 215, 'The same line drawn twice: on the left each pixel is fully on or off, giving jagged steps; '
                      'on the right each pixel is shaded by how much of it the line covers, so the edge looks smooth')
    for k, title in enumerate(('Aliased: on or off', 'Antialiased: shaded by coverage')):
        g = PixelGrid(s, cols, rows, 16, left=20 + k * 280, top=40)
        g.draw(label_every=99)
        s.parts = [x for x in s.parts if not x.endswith('>0</text>')]
        for x in range(cols):
            for y in range(rows):
                if k == 0:
                    if (x, y) in pts:
                        g.pixel(x, y, INK)
                else:
                    cv = coverage(x, y)
                    if cv > 0.02:
                        g.pixel(x, y, INK if cv > 0.98 else f'rgba(31,41,51,{cv:.2f})')
        s.text(g.left + cols * 8, 28, title, 13, weight='bold')
    s.text(280, 180, 'Area sampling (as in Wu’s algorithm): a pixel the line covers 30% gets 30% intensity.', 11)
    s.text(280, 200, 'The steps are still there, but the eye blends them into a smooth, slightly softer line.', 11)
    s.save('antialiasing-compare.svg', OUT)


def raster_vs_random_scan():
    s = Svg(560, 300, 'Raster scan sweeps every row of the screen top to bottom with horizontal retraces; '
                      'random scan moves the beam only along the lines of the picture')
    arrow_defs(s)
    for k, title in enumerate(('Raster scan: every row, every frame', 'Random scan: only the picture’s lines')):
        x0, y0, w, h = 30 + k * 270, 40, 230, 200
        s.rect(x0, y0, w, h, '#f8fafc', INK, 1.3)
        s.text(x0 + w / 2, 28, title, 12, weight='bold')
        tri = [(x0 + 50, y0 + 160), (x0 + 180, y0 + 160), (x0 + 115, y0 + 40)]
        if k == 0:
            for i in range(9):
                yy = y0 + 18 + i * 21
                arrow(s, x0 + 12, yy, x0 + w - 12, yy, PIX, 1.4)
                if i < 8:
                    s.line(x0 + w - 12, yy, x0 + 12, yy + 21, '#9ca3af', 1, '3 3')
            s.path('M ' + ' L '.join(f'{x} {y}' for x, y in tri) + ' Z', TRUE, 2.5)
            s.text(x0 + w / 2, y0 + h + 22, 'blue: beam sweeps; grey dashed: retrace (beam off)', 10)
        else:
            for a, b in zip(tri, tri[1:] + tri[:1]):
                arrow(s, a[0], a[1], b[0], b[1], TRUE, 2.5)
            s.text(x0 + w / 2, y0 + h + 22, 'beam traces each line in turn, from the display file', 10)
    s.save('raster-vs-random-scan.svg', OUT)


def double_buffering():
    s = Svg(520, 230, 'Double buffering: the program draws the next frame into the hidden back buffer while the '
                      'display shows the front buffer; at vertical retrace the two are swapped')
    arrow_defs(s)
    boxes = [(30, 'Program', 'draws frame n + 1', '#e5e7eb'), (190, 'Back buffer', 'hidden, being drawn', '#fef3c7'),
             (190, 'Front buffer', 'shown on screen', '#dbeafe'), (370, 'Display', 'reads front buffer', '#e5e7eb')]
    pos = {}
    for i, (x, name, sub, fill) in enumerate(boxes):
        y = 40 if name != 'Front buffer' else 130
        if name in ('Program', 'Display'):
            y = 85
        s.rect(x, y, 130, 56, fill, INK, 1.3)
        s.text(x + 65, y + 24, name, 13, weight='bold')
        s.text(x + 65, y + 42, sub, 10)
        pos[name] = (x, y)
    arrow(s, 160, 105, 188, 75)
    arrow(s, 320, 160, 368, 125)
    arrow(s, 300, 98, 300, 128)
    arrow(s, 210, 128, 210, 98)
    s.text(255, 117, 'swap at V-sync', 10, ACCENT, 'middle', 'bold')
    s.text(260, 218, 'The screen never shows a half-drawn frame, so there is no tearing.', 11)
    s.save('double-buffering.svg', OUT)


def scanline_triangle():
    tri = [(2, 2), (10, 2), (6, 8)]
    xl = 2 + (3 - 2) * (6 - 2) / (8 - 2)
    xr = 10 + (3 - 2) * (6 - 10) / (8 - 2)
    assert round(xl, 2) == 2.67 and round(xr, 2) == 9.33
    s = Svg(470, 362, 'Scan-line fill of the triangle (2,2), (10,2), (6,8): scan line y = 3 crosses the edges at '
                      'x = 2.67 and x = 9.33, so pixels 3 to 9 on that row are filled')
    g = PixelGrid(s, 12, 10, 30, left=45, top=15)
    g.draw()
    for x in range(3, 10):
        g.pixel(x, 3)
    X = lambda x: g.left + (x + 0.5) * g.c
    Y = lambda y: g.top + (g.rows - y - 0.5) * g.c
    s.path('M ' + ' L '.join(f'{X(x):.1f} {Y(y):.1f}' for x, y in tri) + ' Z', TRUE, 2.2)
    s.line(g.left, Y(3), g.left + g.cols * g.c, Y(3), ORANGE, 1.6, '6 4')
    for xx in (xl, xr):
        s.circle(X(xx), Y(3), 5, ORANGE)
    s.text(X(xl) - 8, Y(3) - 10, '2.67', 11, ORANGE, 'end', 'bold')
    s.text(X(xr) + 8, Y(3) - 10, '9.33', 11, ORANGE, 'start', 'bold')
    s.text(235, 354, 'Orange: scan line y = 3 and its two crossings. Blue: the span filled between them.', 11)
    s.save('scanline-triangle.svg', OUT)


def connected_fill():
    s = Svg(560, 260, '4-connected neighbours are up, down, left and right; 8-connected adds the diagonals, '
                      'which lets an 8-connected fill leak through a boundary that only touches at corners')
    titles = ('4-connected', '8-connected', 'Why 8-connected fills leak')
    for k in range(3):
        n = 3 if k < 2 else 6
        c = 34 if k < 2 else 26
        g = PixelGrid(s, n, n, c, left=30 + k * 180, top=50)
        g.draw(label_every=99)
        s.parts = [x for x in s.parts if not x.endswith('>0</text>')]
        s.text(g.left + n * c / 2, 36, titles[k], 12, weight='bold')
        if k < 2:
            g.pixel(1, 1, INK)
            nb = [(1, 0), (1, 2), (0, 1), (2, 1)] + ([(0, 0), (2, 2), (0, 2), (2, 0)] if k else [])
            for x, y in nb:
                g.pixel(x, y, PIX)
        else:
            wall = [(i, i) for i in range(6)]
            for x, y in wall:
                g.pixel(x, y, INK)
            for x in range(6):
                for y in range(6):
                    if y < x:
                        g.pixel(x, y, PIX2)
            g.pixel(1, 2, TRUE)
            g.pixel(2, 3, TRUE)
            s.text(g.left + 3 * c, g.top + 6 * c + 22, 'red: leaked through the corners', 10)
    s.text(280, 250, 'Dark: the seed or the boundary. A 4-connected fill cannot squeeze between corner-touching pixels.', 10)
    s.save('fill-4-vs-8-connected.svg', OUT)


def clip_worked_example():
    P0, P1 = (0, 4), (6, 8)
    a, b = (2, 16 / 3), (3, 6)
    s = Svg(430, 360, 'Clipping the line (0,4) to (6,8) against the window [2,8] x [2,6]: the part inside runs from '
                      '(2, 5.33) to (3, 6); the rest is cut away')
    A = Axes(s, 45, 320, 34, (0, 10), (0, 9))
    A.poly([(2, 2), (8, 2), (8, 6), (2, 6)], ACCENT, 2, fill='#ecfdf5')
    A.seg(P0, P1, '#9ca3af', 2, '6 4')
    A.seg(a, b, TRUE, 3.5)
    for p, t, code in ((P0, '(0, 4)', '0001'), (P1, '(6, 8)', '1000')):
        A.dot(p, '#9ca3af')
        A.label(p, f'{t}  code {code}', 8 if p == P1 else 4, -8 if p == P1 else 20, '#4b5563')
    for p, t in ((a, '(2, 5.33)'), (b, '(3, 6)')):
        A.dot(p, TRUE)
    A.label(a, '(2, 5.33)', 8, 18, TRUE, weight='bold')
    A.label(b, '(3, 6)', 8, 16, TRUE, weight='bold')
    A.label((5, 3.5), 'window', 0, 0, ACCENT, 'middle', 12, 'bold')
    s.text(215, 352, 'Grey dashed: the whole line. Red: the part that is kept.', 11)
    s.save('clip-worked-example.svg', OUT)


def basic_transforms():
    house = [(0, 0), (2, 0), (2, 1.5), (1, 2.5), (0, 1.5)]
    T = {
        'Translate by (2, 1)': lambda x, y: (x + 2, y + 1),
        'Scale by (1.5, 0.5)': lambda x, y: (1.5 * x, 0.5 * y),
        'Rotate 45° about origin': lambda x, y: (x * math.cos(math.pi / 4) - y * math.sin(math.pi / 4),
                                                 x * math.sin(math.pi / 4) + y * math.cos(math.pi / 4)),
        'Shear in x by 0.5': lambda x, y: (x + 0.5 * y, y),
        'Reflect in the y-axis': lambda x, y: (-x, y),
    }
    s = Svg(620, 470, 'Five basic transforms of a small house shape: translate, scale, rotate, shear and reflect; '
                      'grey is the original, blue is the result')
    for k, (name, f) in enumerate(T.items()):
        cx, cy = 20 + (k % 3) * 200, 220 + (k // 3) * 225
        A = Axes(s, cx + 10, cy, 30, (-3, 3), (-1, 4), ticks=False)
        A.seg((-3, 0), (3, 0), '#9ca3af', 1)
        A.seg((0, -1), (0, 4), '#9ca3af', 1)
        A.poly(house, INK, 1.6, fill='#e5e7eb')
        A.poly([f(x, y) for x, y in house], PIX, 2.2, fill='rgba(59,130,246,0.25)')
        s.text(cx + 100, cy - 165, name, 12, weight='bold')
    s.save('basic-transforms.svg', OUT)


def bspline_basis(i, k, t, knots):
    if k == 1:
        return 1.0 if knots[i] <= t < knots[i + 1] or (t == knots[-1] and knots[i] < t <= knots[i + 1]) else 0.0
    a = knots[i + k - 1] - knots[i]
    b = knots[i + k] - knots[i + 1]
    left = (t - knots[i]) / a * bspline_basis(i, k - 1, t, knots) if a else 0
    right = (knots[i + k] - t) / b * bspline_basis(i + 1, k - 1, t, knots) if b else 0
    return left + right


def bspline_curve(P, k=4, n=200):
    m = len(P)
    knots = [0] * k + list(range(1, m - k + 1)) + [m - k + 1] * k
    tmax = knots[-1]
    out = []
    for i in range(n + 1):
        t = tmax * i / n
        w = [bspline_basis(j, k, t, knots) for j in range(m)]
        out.append((sum(w[j] * P[j][0] for j in range(m)), sum(w[j] * P[j][1] for j in range(m))))
    return out


def bezier_curve(P, n=200):
    deg = len(P) - 1
    out = []
    for i in range(n + 1):
        t = i / n
        w = [math.comb(deg, j) * t ** j * (1 - t) ** (deg - j) for j in range(deg + 1)]
        out.append((sum(w[j] * P[j][0] for j in range(deg + 1)), sum(w[j] * P[j][1] for j in range(deg + 1))))
    return out


def local_vs_global_control():
    P = [(0, 0), (1, 2), (2.5, 2.5), (4, 0.5), (5.5, 2.5), (7, 3), (8, 0.5)]
    Q = list(P)
    Q[5] = (7, 5)                                   # move one control point up
    bz, bz2 = bezier_curve(P), bezier_curve(Q)
    bs, bs2 = bspline_curve(P), bspline_curve(Q)
    # local control: the first part of the B-spline does not move at all
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) < 1e-9 for a, b in zip(bs[:90], bs2[:90]))
    assert any(abs(a[1] - b[1]) > 1e-3 for a, b in zip(bz[10:40], bz2[10:40]))
    s = Svg(600, 300, 'Moving one control point (P5) changes the whole Bezier curve but only the nearby part of the '
                      'cubic B-spline; grey is before the move, coloured is after')
    for k, (title, a, b) in enumerate((('Bézier: the whole curve moves', bz, bz2),
                                       ('Cubic B-spline: only the end moves', bs, bs2))):
        A = Axes(s, 25 + k * 300, 250, 32, (0, 8), (0, 5), ticks=False)
        A.poly(Q, '#9ca3af', 1, close=False, dash='4 3')
        A.poly(a, '#9ca3af', 2, close=False)
        A.poly(b, TRUE if k == 0 else PIX, 2.5, close=False)
        for i, p in enumerate(Q):
            A.dot(p, ORANGE if i == 5 else INK, 4)
        A.seg(P[5], Q[5], ORANGE, 1.5, '3 3')
        A.label(Q[5], 'P5 moved up', -10, 4, ORANGE, 'end', 10, 'bold')
        s.text(A.X(4), 30, title, 12, weight='bold')
    s.text(300, 290, 'Grey: the curve before P5 moved. The B-spline’s first half doesn’t change at all: local control.', 10)
    s.save('bezier-vs-bspline-local-control.svg', OUT)


def chaikin_rounds():
    def step(poly):
        out = []
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            out += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]),
                    (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        return out
    sq = [(0, 0), (4, 0), (4, 4), (0, 4)]
    r1 = step(sq)
    assert r1 == [(1, 0), (3, 0), (4, 1), (4, 3), (3, 4), (1, 4), (0, 3), (0, 1)]
    rounds = [sq, r1, step(r1), step(step(r1))]
    s = Svg(600, 200, 'Chaikin corner cutting on the square (0,0) to (4,4): 4 points become 8, then 16, then 32, '
                      'and the shape rounds off towards a smooth curve')
    for k, poly in enumerate(rounds):
        A = Axes(s, 25 + k * 145, 160, 28, (0, 4), (0, 4), ticks=False)
        if k:
            A.poly(rounds[k - 1], '#9ca3af', 1, dash='3 3')
        A.poly(poly, PIX, 2.2)
        for p in poly:
            A.dot(p, PIX, 2.8)
        s.text(A.X(2), 25, f'round {k}: {len(poly)} points', 11, weight='bold')
    s.text(300, 192, 'Each round replaces every edge with points ¼ and ¾ of the way along it.', 11)
    s.save('chaikin-rounds.svg', OUT)


def point_segment_distance():
    A_, B_ = (1, 1), (9, 5)
    cases = [((3, 7), (5, 3)), ((12, 2), (9, 5)), ((0, 0), (1, 1))]
    for p, c in cases:
        ab = (B_[0] - A_[0], B_[1] - A_[1])
        t = ((p[0] - A_[0]) * ab[0] + (p[1] - A_[1]) * ab[1]) / (ab[0] ** 2 + ab[1] ** 2)
        t = max(0, min(1, t))
        assert (A_[0] + t * ab[0], A_[1] + t * ab[1]) == c
    s = Svg(500, 330, 'Distance from a point to the segment A(1,1) to B(9,5): (3,7) is nearest to the middle point '
                      '(5,3); (12,2) is beyond B so its nearest point is B; (0,0) is before A so its nearest point is A')
    A = Axes(s, 40, 290, 30, (-1, 13), (-1, 8))
    A.seg((-1, 0), (13, 6), '#d1d5db', 1, '5 4')
    A.seg(A_, B_, INK, 3)
    A.label(A_, 'A', -10, 16, weight='bold', anchor='end', size=13)
    A.label(B_, 'B', 6, -8, weight='bold', size=13)
    names = ('middle: t = 0.5', 'clamped to B (t = 1.15 → 1)', 'clamped to A (t = −0.15 → 0)')
    for (p, c), name, col in zip(cases, names, (PIX, TRUE, ORANGE)):
        A.seg(p, c, col, 1.8, '4 3')
        A.dot(p, col, 5)
        A.dot(c, col, 3.5)
        dx, dy, anc = {(3, 7): (8, -6, 'start'), (12, 2): (0, 22, 'end'), (0, 0): (10, 4, 'start')}[p]
        A.label(p, f'{p} {name}', dx, dy, col, anc, 10, 'bold')
    s.text(250, 322, 'Grey dashed: the infinite line. Without the clamp you’d measure to it, which is wrong for a segment.', 10)
    s.save('point-segment-distance.svg', OUT)


def zbuffer_picture():
    s = Svg(560, 270, 'Depth buffer: a red square at depth 0.3 and a blue square at depth 0.7 overlap; with larger z '
                      'meaning nearer, every pixel in the overlap keeps blue, whichever square is drawn first')
    cols, rows = 10, 7
    red = {(x, y) for x in range(1, 6) for y in range(1, 6)}
    blue = {(x, y) for x in range(4, 9) for y in range(0, 4)}
    for k, (title, order) in enumerate((('Draw red, then blue', ('r', 'b')), ('Draw blue, then red', ('b', 'r')))):
        g = PixelGrid(s, cols, rows, 22, left=30 + k * 280, top=40)
        g.draw(label_every=99)
        s.parts = [x for x in s.parts if not x.endswith('>0</text>')]
        depth, colour = {}, {}
        for name in order:
            cells, z, col = (red, 0.3, TRUE) if name == 'r' else (blue, 0.7, PIX)
            for c in cells:
                if z > depth.get(c, 0):
                    depth[c], colour[c] = z, col
        for (x, y), col in colour.items():
            g.pixel(x, y, col)
        s.text(g.left + cols * 11, 30, title, 12, weight='bold')
    s.text(280, 232, 'Red z = 0.3, blue z = 0.7 (larger = nearer). The overlap is blue in both: order doesn’t matter.', 11)
    s.text(280, 252, 'Each pixel keeps the nearest depth seen so far, compared one pixel at a time.', 11)
    s.save('zbuffer-two-squares.svg', OUT)


def backface_picture():
    s = Svg(440, 400, 'Top view of a cube with outward normals; the viewer looks along V into the scene; faces with '
                      'V dot N greater than 0 face away and are culled')
    arrow_defs(s)
    cx, cy, h = 220, 175, 70
    V = (0, -1)                                       # viewer below, looking up the page (into the scene)
    faces = [('front', (cx - h, cy + h), (cx + h, cy + h), (0, 1)), ('back', (cx - h, cy - h), (cx + h, cy - h), (0, -1)),
             ('left', (cx - h, cy - h), (cx - h, cy + h), (-1, 0)), ('right', (cx + h, cy - h), (cx + h, cy + h), (1, 0))]
    for name, a, b, n in faces:
        vn = V[0] * n[0] + V[1] * n[1]
        culled = vn > 0
        col = '#9ca3af' if culled else PIX
        s.line(a[0], a[1], b[0], b[1], col, 4, '6 5' if culled else None)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        arrow(s, mx, my, mx + n[0] * 45, my + n[1] * 45, col, 1.8)
        lbl = {'front': 'V·N = −1 < 0: drawn', 'back': 'V·N = 1 > 0: culled', 'left': 'V·N = 0: edge-on',
               'right': 'V·N = 0: edge-on'}[name]
        tx, ty = mx + n[0] * 60, my + n[1] * 60 + (4 if n[1] == 0 else (14 if n[1] > 0 else -6))
        s.text(tx, ty, lbl, 11, col, 'middle' if n[0] == 0 else ('start' if n[0] > 0 else 'end'), 'bold')
    arrow(s, cx, 392, cx, 352, INK, 2)
    s.text(cx + 8, 384, 'viewer, looking along V', 11, INK, 'start', 'bold')
    s.text(220, 18, 'Top view of a cube. Arrows are outward normals N.', 11)
    s.save('backface-culling.svg', OUT)


def bresenham_two_distances_steep():
    s = Svg(470, 340, 'For a steep line, at row y_k + 1 the true line sits at x between the left pixel x_k and the '
                      'right pixel x_k + 1; d_left is the gap back to x_k and d_right the gap on to x_k + 1')
    arrow_defs(s)
    c, ox, oy = 150, 110, 250
    X = lambda x: ox + x * c
    Y = lambda y: oy - y * c
    for x, y in ((0, 0), (0, 1), (1, 1)):
        s.rect(X(x) - 18, Y(y) - 18, 36, 36, PIX if (x, y) == (0, 0) else '#ffffff', INK, 1.4)
    xt = 0.4
    s.line(X(-0.06), Y(-0.15), X(0.44), Y(1.1), TRUE, 2.2)
    s.circle(X(xt), Y(1), 5, TRUE)
    yy = Y(1) - 34
    s.line(X(0), yy, X(1), yy, INK, 1)
    for (a, b, lab) in ((0, xt, 'd_left = x − x_k'), (xt, 1, 'd_right = (x_k + 1) − x')):
        arrow(s, X((a + b) / 2), yy, X(a) + 3, yy)
        arrow(s, X((a + b) / 2), yy, X(b) - 3, yy)
        s.text(X(xt) - 6 if a == 0 else X(xt) + 6, yy - 12, lab, 12, INK, 'end' if a == 0 else 'start')
    s.text(X(0), oy + 42, 'x_k', 13, weight='bold')
    s.text(X(1), oy + 42, 'x_k + 1', 13, weight='bold')
    s.text(ox - 40, Y(0) + 4, 'y_k', 13, anchor='end', weight='bold')
    s.text(ox - 40, Y(1) + 4, 'y_k + 1', 13, anchor='end', weight='bold')
    s.text(X(xt) + 10, Y(1) + 26, 'x', 13, TRUE, 'start', 'bold')
    s.text(X(0) + 26, Y(0) + 4, 'plotted', 11, PIX, 'start', 'bold')
    s.text(X(0) - 26, Y(1) + 34, 'left?', 11)
    s.text(X(1), Y(1) + 34, 'right?', 11)
    s.text(235, 332, 'Steep line: step y by 1, and choose left (x stays) or right (x + 1) by which is nearer.', 11)
    s.save('bresenham-two-distances-steep.svg', OUT)


if __name__ == '__main__':
    bresenham_shallow()
    bresenham_steep_vs_wrong_axis()
    midpoint_circle()
    cohen_sutherland_regions()
    bezier_de_casteljau()
    rotate_about_pivot()
    square_rotated_30()
    bezier_b9()
    bresenham_two_distances()
    bresenham_two_distances_steep()
    dda_example()
    antialiasing_compare()
    raster_vs_random_scan()
    double_buffering()
    scanline_triangle()
    connected_fill()
    clip_worked_example()
    basic_transforms()
    local_vs_global_control()
    chaikin_rounds()
    point_segment_distance()
    zbuffer_picture()
    backface_picture()
    flowchart([('scene data', 'data'), ('Vertex processing\ntransform to clip space', 'prog'),
               ('Clipping and culling\ndiscard what is invisible', 'fixed'),
               ('Rasterisation\ntriangles → fragments', 'fixed'),
               ('Fragment shading\ncolour per fragment', 'prog'),
               ('Output merging\ndepth test, blending', 'fixed'), ('framebuffer', 'data')],
              'realtime-pipeline.svg', 'The real-time rendering pipeline from scene data through vertex processing, '
              'clipping and culling, rasterisation, fragment shading and output merging to the framebuffer', OUT)
    flowchart([('MODEL space\nthe object\u2019s own coordinates', 'data'), ('WORLD space\nthe whole scene', 'data'),
               ('VIEW space\ncamera at the origin', 'data'), ('CLIP space', 'data'),
               ('NDC\nthe cube [−1, 1]³', 'data'), ('SCREEN\npixels', 'data')],
              'transform-chain.svg', 'The transform chain: model space to world space by M, world to view by V, view '
              'to clip by P, clip to NDC by dividing by w, and NDC to screen pixels by the viewport transform', OUT,
              notes=['model matrix M', 'view matrix V', 'projection matrix P', 'divide by w', 'viewport'])
    flowchart([('vertex buffer', 'data'), ('VERTEX SHADER\nprogrammable: transform each vertex', 'prog'),
               ('tessellation\noptional, programmable', 'prog'), ('GEOMETRY SHADER\noptional; usually avoid it', 'prog'),
               ('clip / cull / rasterise\nfixed function', 'fixed'),
               ('FRAGMENT SHADER\nprogrammable: colour each fragment', 'prog'),
               ('depth / stencil / blend\nfixed function (mostly)', 'fixed'), ('framebuffer', 'data')],
              'gpu-pipeline-stages.svg', 'GPU pipeline stages: vertex buffer, vertex shader, optional tessellation and '
              'geometry shader, fixed-function clip cull and rasterise, fragment shader, fixed-function depth stencil '
              'and blend, framebuffer. Blue stages are programmable, grey are fixed function', OUT)
