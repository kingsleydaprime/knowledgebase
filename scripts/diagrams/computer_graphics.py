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

INK = '#1f2933'        # text and outlines
GRID = '#cbd2d9'       # grid lines
PIX = '#3b82f6'        # lit pixels
PIX2 = '#93c5fd'       # mirrored / secondary pixels
TRUE = '#dc2626'       # the true (ideal) shape
ACCENT = '#059669'     # constructions, results
BG = '#ffffff'


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.title = title

    def add(self, s):
        self.parts.append(s)

    def line(self, x1, y1, x2, y2, color=INK, width=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{color}" stroke-width="{width}"{d}/>')

    def rect(self, x, y, w, h, fill, stroke='none', width=1, opacity=1):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{width}" fill-opacity="{opacity}"/>')

    def circle(self, x, y, r, fill, stroke='none'):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}"/>')

    def text(self, x, y, s, size=13, color=INK, anchor='middle', weight='normal'):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" '
                 f'font-family="system-ui, sans-serif">{s}</text>')

    def path(self, d, color, width=2, fill='none', dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}"{da}/>')

    def save(self, name):
        os.makedirs(OUT, exist_ok=True)
        body = '\n'.join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" role="img">\n<title>{self.title}</title>\n'
               f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>\n{body}\n</svg>\n')
        with open(os.path.join(OUT, name), 'w') as f:
            f.write(svg)
        print(f'{name}: {len(svg)} bytes')


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
    s.save('bresenham-2-3-to-9-8.svg')


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
    s.save('line-stepping-the-right-axis.svg')


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
    s.save('midpoint-circle-r10.svg')


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
    s.save('cohen-sutherland-region-codes.svg')


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
    s.save('bezier-de-casteljau.svg')


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
    s.save('rotate-about-pivot.svg')


if __name__ == '__main__':
    bresenham_shallow()
    bresenham_steep_vs_wrong_axis()
    midpoint_circle()
    cohen_sutherland_regions()
    bezier_de_casteljau()
    rotate_about_pivot()
