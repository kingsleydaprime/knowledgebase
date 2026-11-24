"""Draw the control theory lesson diagrams as small SVG files, and check the lessons' numbers.

    python3 scripts/diagrams/control_theory.py      # run from the vault root

Every worked example and quiz answer in control-theory/ that comes from a sum is checked here with
an assert before anything is drawn: the cruise-control numbers, step-response formulas, Routh
tables, Bode and Nyquist points, state-space matrices, the optimal-control sequences, phase
portraits, limit cycles and Lyapunov functions. Plots are simulated with a plain RK4 integrator,
so no libraries are needed. Block diagrams use Graphviz (`dot`, which must be installed).
Output: control-theory/images/*.svg.
"""
import cmath
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, GRID, ACCENT, TRUE, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('control-theory', 'images')
BLUE = '#2563eb'
ORANGE = '#f59e0b'
GREY = '#9ca3af'
PURPLE = '#7c3aed'


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


# ---------- numerics ----------

def rk4(f, x0, t0, t1, n):
    """Integrate dx/dt = f(t, x) (x a list) from t0 to t1 in n steps. Returns ts, xs."""
    h = (t1 - t0) / n
    t, x = t0, list(x0)
    ts, xs = [t], [list(x)]
    for _ in range(n):
        k1 = f(t, x)
        k2 = f(t + h / 2, [a + h / 2 * b for a, b in zip(x, k1)])
        k3 = f(t + h / 2, [a + h / 2 * b for a, b in zip(x, k2)])
        k4 = f(t + h, [a + h * b for a, b in zip(x, k3)])
        x = [a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(x, k1, k2, k3, k4)]
        t += h
        ts.append(t)
        xs.append(list(x))
    return ts, xs


def rk4_box(f, x0, h, nmax, box):
    """RK4 on dx/dt = f(x) with step h, stopping when x leaves box = (x0, x1, y0, y1)."""
    x = list(x0)
    out = [list(x)]
    for _ in range(nmax):
        k1 = f(x)
        k2 = f([a + h / 2 * b for a, b in zip(x, k1)])
        k3 = f([a + h / 2 * b for a, b in zip(x, k2)])
        k4 = f([a + h * b for a, b in zip(x, k3)])
        x = [a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(x, k1, k2, k3, k4)]
        out.append(list(x))
        if not (box[0] <= x[0] <= box[1] and box[2] <= x[1] <= box[3]):
            break
    return out


def eig2(a, b, c, d):
    """Eigenvalues of [[a, b], [c, d]]."""
    tr, det = a + d, a * d - b * c
    disc = cmath.sqrt(tr * tr - 4 * det)
    return (tr + disc) / 2, (tr - disc) / 2


# ---------- plotting ----------

class Plot:
    """A data-space plot on an Svg. Margins leave room for tick labels."""

    def __init__(self, w, h, xr, yr, title, ml=56, mr=18, mt=18, mb=44):
        self.s = Svg(w, h, title)
        self.x0, self.x1 = xr
        self.y0, self.y1 = yr
        self.ml, self.mr, self.mt, self.mb = ml, mr, mt, mb
        self.w, self.h = w, h

    def X(self, x):
        return self.ml + (x - self.x0) / (self.x1 - self.x0) * (self.w - self.ml - self.mr)

    def Y(self, y):
        return self.h - self.mb - (y - self.y0) / (self.y1 - self.y0) * (self.h - self.mt - self.mb)

    def axes(self, xticks=(), yticks=(), xlabel='', ylabel='', grid=True, cross=False, fmt=None, xfmt=None,
             xticklabels=True):
        s = self
        f = fmt or (lambda v: f'{v:g}')
        fx = xfmt or f
        for v in xticks:
            if grid:
                s.s.line(s.X(v), s.Y(s.y0), s.X(v), s.Y(s.y1), GRID, 1)
            if xticklabels:
                s.s.text(s.X(v), s.Y(s.y0) + 16, fx(v), 11)
        for v in yticks:
            if grid:
                s.s.line(s.X(s.x0), s.Y(v), s.X(s.x1), s.Y(v), GRID, 1)
            s.s.text(s.X(s.x0) - 6, s.Y(v) + 4, f(v), 11, anchor='end')
        if cross:
            s.s.line(s.X(s.x0), s.Y(0), s.X(s.x1), s.Y(0), INK, 1.3)
            s.s.line(s.X(0), s.Y(s.y0), s.X(0), s.Y(s.y1), INK, 1.3)
        else:
            s.s.line(s.X(s.x0), s.Y(s.y0), s.X(s.x1), s.Y(s.y0), INK, 1.3)
            s.s.line(s.X(s.x0), s.Y(s.y0), s.X(s.x0), s.Y(s.y1), INK, 1.3)
        if xlabel:
            s.s.text((s.X(s.x0) + s.X(s.x1)) / 2, s.h - 8, xlabel, 12)
        if ylabel:
            yc = (s.Y(s.y0) + s.Y(s.y1)) / 2
            s.s.add(f'<text x="14" y="{yc:.1f}" font-size="12" fill="{INK}" text-anchor="middle" '
                    f'transform="rotate(-90 14 {yc:.1f})" font-family="system-ui, sans-serif">{ylabel}</text>')

    def curve(self, xs, ys, color=BLUE, width=2.2, dash=None, clip=True, maxpts=300):
        xs, ys = list(xs), list(ys)
        pts = []
        segs = []
        last = None
        n = len(xs)
        for i, (x, y) in enumerate(zip(xs, ys)):
            ok = (not clip) or (self.y0 - 1e-9 <= y <= self.y1 + 1e-9 and self.x0 - 1e-9 <= x <= self.x1 + 1e-9)
            if ok:
                X, Y = self.X(x), self.Y(y)
                if last is not None and pts and i < n - 1 and math.hypot(X - last[0], Y - last[1]) < 1.5:
                    continue
                last = (X, Y)
                pts.append(f'{X:.1f},{Y:.1f}')
            elif pts:
                segs.append(pts)
                pts = []
                last = None
        if pts:
            segs.append(pts)
        for p in segs:
            if len(p) > 1:
                self.s.path('M' + ' L'.join(p), color, width, dash=dash)

    def hline(self, y, color=GREY, dash='5,4', width=1.3):
        self.s.line(self.X(self.x0), self.Y(y), self.X(self.x1), self.Y(y), color, width, dash)

    def vline(self, x, color=GREY, dash='5,4', width=1.3):
        self.s.line(self.X(x), self.Y(self.y0), self.X(x), self.Y(self.y1), color, width, dash)

    def dot(self, x, y, color=INK, r=4):
        self.s.circle(self.X(x), self.Y(y), r, color)

    def cross(self, x, y, color=TRUE, r=6, width=2.2):
        X, Y = self.X(x), self.Y(y)
        self.s.line(X - r, Y - r, X + r, Y + r, color, width)
        self.s.line(X - r, Y + r, X + r, Y - r, color, width)

    def ring(self, x, y, color=BLUE, r=6):
        self.s.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="white" '
                   f'stroke="{color}" stroke-width="2.2"/>')

    def label(self, x, y, text, color=INK, size=12, anchor='start', dx=0, dy=0, weight='normal'):
        self.s.text(self.X(x) + dx, self.Y(y) + dy, text, size, color, anchor, weight)

    def arrow(self, x, y, dx, dy, color=INK, size=7):
        """A small arrowhead at (x, y) pointing along data direction (dx, dy)."""
        px, py = self.X(x + dx) - self.X(x), self.Y(y + dy) - self.Y(y)
        n = math.hypot(px, py) or 1
        ux, uy = px / n, py / n
        X, Y = self.X(x), self.Y(y)
        a = (X - size * ux + size * 0.5 * uy, Y - size * uy - size * 0.5 * ux)
        b = (X - size * ux - size * 0.5 * uy, Y - size * uy + size * 0.5 * ux)
        self.s.add(f'<path d="M{X:.1f},{Y:.1f} L{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f} Z" fill="{color}"/>')

    def legend(self, items, x, y, size=12):
        """items: list of (text, color, dash). x, y in pixels (top-left)."""
        for i, (t, c, d) in enumerate(items):
            yy = y + i * 18
            self.s.line(x, yy - 4, x + 24, yy - 4, c, 2.4, d)
            self.s.text(x + 30, yy, t, size, anchor='start')

    def save(self, name):
        self.s.save(name, OUT)


class Blocks:
    """Hand-placed block diagrams: boxes, summing junctions and arrowed wires, in pixels."""

    def __init__(self, w, h, title):
        self.s = Svg(w, h, title)

    def box(self, x, y, w, h, label, fill='#dbeafe', size=13):
        self.s.add(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w}" height="{h}" rx="7" '
                   f'fill="{fill}" stroke="{INK}" stroke-width="1.3"/>')
        lines = label.split('\n')
        for i, t in enumerate(lines):
            self.s.text(x, y + 4.5 + (i - (len(lines) - 1) / 2) * 15, t, size)

    def sum(self, x, y, r=13, signs=None):
        """signs: dict side -> sign text, sides 'w', 's', 'n'."""
        self.s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fef3c7" stroke="{INK}" stroke-width="1.3"/>')
        self.s.text(x, y + 5, 'Σ', 14)
        for side, t in (signs or {}).items():
            dx, dy = {'w': (-r - 6, -6), 's': (-11, r + 12), 'n': (-11, -r - 2)}[side]
            self.s.text(x + dx, y + dy, t, 15, anchor='middle', weight='bold')

    def wire(self, pts, arrow=True, color=INK, label=None, at=0, dx=0, dy=-7, anchor='middle'):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        self.s.path(d, color, 1.5)
        if arrow:
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            n = math.hypot(x2 - x1, y2 - y1) or 1
            ux, uy = (x2 - x1) / n, (y2 - y1) / n
            a = (x2 - 9 * ux + 4.5 * uy, y2 - 9 * uy - 4.5 * ux)
            b = (x2 - 9 * ux - 4.5 * uy, y2 - 9 * uy + 4.5 * ux)
            self.s.add(f'<path d="M{x2:.1f},{y2:.1f} L{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f} Z" '
                       f'fill="{color}"/>')
        if label:
            (x1, y1), (x2, y2) = pts[at], pts[at + 1]
            self.s.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, label, 12, '#374151', anchor)

    def text(self, x, y, t, size=13, anchor='middle', color=INK):
        self.s.text(x, y, t, size, color, anchor)

    def dot(self, x, y):
        self.s.circle(x, y, 3, INK)

    def save(self, name):
        self.s.save(name, OUT)


def block(src, name, title):
    head = (f'digraph {{ bgcolor="white"; pad=0.25; rankdir=LR; nodesep=0.35; ranksep=0.45; splines=ortho;\n'
            f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", fillcolor="#dbeafe", '
            f'color="{INK}", penwidth=1.2];\n'
            f'edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="#374151", arrowsize=0.8];\n')
    save_dot(head + src + '\n}', name, title, OUT)


SUM = 'shape=circle, label="Σ", width=0.4, fixedsize=true, fillcolor="#fef3c7"'
PT = 'shape=point, width=0.01'
TXT = 'shape=plaintext, style="", fillcolor="none"'


# ---------- lessons 01-02: the feedback loop ----------

CAR_M, CAR_B = 1000.0, 50.0        # kg, N per m/s
KP, REF, HILL = 500.0, 20.0, 300.0


def cruise_steady(kp, ref, b, d, u_ff=0.0):
    """Steady speed with push u_ff + kp (ref - v) - d = b v."""
    return (u_ff + kp * ref - d) / (kp + b)


def check_01():
    assert cruise_steady(0, 0, CAR_B, 0, 1000) == 20
    assert close(cruise_steady(KP, REF, CAR_B, 0), 18.1818)
    assert cruise_steady(0, 0, CAR_B, HILL, 1000) == 14
    assert close(cruise_steady(KP, REF, CAR_B, HILL), 17.6364)
    assert close(cruise_steady(KP, REF, CAR_B, 0) - cruise_steady(KP, REF, CAR_B, HILL), 0.5455)
    assert close((KP + CAR_B) / CAR_B, 11)
    assert close(1000 / 75, 13.333) and close(cruise_steady(KP, REF, 75, 0), 17.391)
    assert close(100 / 101, 0.990, 1e-3) and close(200 / 201, 0.995, 1e-3)
    assert 4 * CAR_M / CAR_B == 80 and close(4 * CAR_M / (KP + CAR_B), 7.27)
    assert 200 / 40 == 5                                    # quiz 4


def fig_01():
    b = Blocks(590, 90, 'Open-loop control: reference, controller, plant, output, with no return path')
    b.text(40, 50, 'reference')
    b.wire([(78, 45), (150, 45)])
    b.box(205, 45, 110, 40, 'Controller')
    b.wire([(260, 45), (350, 45)], label='command u')
    b.box(405, 45, 110, 40, 'Plant')
    b.wire([(460, 45), (520, 45)])
    b.text(528, 50, 'output', anchor='start')
    b.save('ct-open-loop.svg')

    b = Blocks(700, 200, 'Closed-loop control with reference, error, controller, actuator, plant, disturbance '
               'and sensor')
    y = 80
    b.text(42, y + 5, 'reference r')
    b.wire([(84, y), (117, y)])
    b.sum(130, y, signs={'w': '+', 's': '−'})
    b.wire([(143, y), (205, y)], label='error e')
    b.box(255, y, 100, 40, 'Controller')
    b.wire([(305, y), (360, y)], label='u')
    b.box(410, y, 100, 40, 'Actuator')
    b.wire([(460, y), (505, y)])
    b.box(555, y, 100, 40, 'Plant')
    b.text(555, 22, 'disturbance d')
    b.wire([(555, 30), (555, y - 20)])
    b.wire([(605, y), (660, y)])
    b.text(666, y + 5, 'output y', anchor='start')
    b.s.w = 740
    b.dot(632, y)
    b.wire([(632, y), (632, 160), (390, 160)])
    b.box(340, 160, 100, 36, 'Sensor')
    b.wire([(290, 160), (130, 160), (130, y + 13)], label='measured y')
    b.save('ct-closed-loop.svg')

    # hill response
    def sim(kp, uff):
        def f(t, x):
            d = HILL if t >= 30 else 0.0
            u = uff + kp * (REF - x[0])
            return [(u - d - CAR_B * x[0]) / CAR_M]
        v0 = cruise_steady(kp, REF, CAR_B, 0, uff)
        return rk4(f, [v0], 0, 150, 1500)
    p = Plot(560, 280, (0, 150), (12, 21), 'Cruise control on a hill')
    p.axes(range(0, 151, 30), range(12, 22, 2), 'time (s)', 'speed (m/s)')
    ts, xs = sim(0, 1000)
    assert close(xs[-1][0], 14, 2e-3)
    p.curve(ts, [x[0] for x in xs], ORANGE)
    ts, xs = sim(KP, 0)
    assert close(xs[-1][0], 17.636, 1e-3)
    p.curve(ts, [x[0] for x in xs], BLUE)
    p.vline(30)
    p.label(31, 12.5, 'hill starts', GREY, 11)
    p.label(150, 14.4, 'open loop: 20 → 14', ORANGE, 12, 'end')
    p.label(150, 18.2, 'closed loop: 18.18 → 17.64', BLUE, 12, 'end')
    p.save('ct-cruise-hill.svg')
    b = Blocks(660, 210, 'Feedforward and feedback together, their commands added before the plant')
    y = 120
    b.text(42, y + 5, 'reference r')
    b.dot(100, y)
    b.wire([(84, y), (167, y)])
    b.sum(180, y, signs={'w': '+', 's': '−'})
    b.wire([(193, y), (240, y)])
    b.box(300, y, 120, 44, 'Feedback\ncontroller')
    b.wire([(360, y), (427, y)])
    b.sum(440, y, signs={'w': '+', 'n': '+'})
    b.wire([(100, y), (100, 40), (250, 40)])
    b.box(300, 40, 100, 36, 'Feedforward', fill='#d1fae5')
    b.wire([(350, 40), (440, 40), (440, y - 13)])
    b.wire([(453, y), (490, y)])
    b.box(535, y, 90, 40, 'Plant')
    b.wire([(580, y), (630, y)])
    b.text(636, y + 5, 'y', anchor='start')
    b.dot(600, y)
    b.wire([(600, y), (600, 185), (180, 185), (180, y + 13)])
    b.save('ct-feedforward.svg')


# ---------- lessons 03-04: modelling ----------

def check_03():
    # car transfer function 1/(1000 s + 50) = 0.02/(20 s + 1)
    assert close(1 / CAR_B, 0.02) and CAR_M / CAR_B == 20 and -CAR_B / CAR_M == -0.05
    # RHP zero: y = 1 - e^-t - 2 t e^-t, min at t = 0.5
    y = lambda t: 1 - math.exp(-t) - 2 * t * math.exp(-t)
    assert close(y(0.5), -0.2131, 1e-3)
    assert all(y(0.5) <= y(t / 100) for t in range(0, 1000))
    # quiz: 3/(s+4)
    assert 3 / 4 == 0.75


def check_04():
    # cruise loop: T = 500/(1000 s + 550)
    assert close(500 / 550, 0.90909) and close(500 / 550 * 20, 18.1818) and -550 / 1000 == -0.55
    assert close(0.55 / 0.05, 11)
    assert 2.5 * 20 ** 2 == 1000 and 5 * 20 == 100 and 5 * 10 == 50
    # quiz: 2/(s+2) with gain 5 -> 10/(s+12)
    assert close(10 / 12, 0.8333)


def resp_rhp(t):
    return 1 - math.exp(-t) - 2 * t * math.exp(-t)


def fig_03():
    p = Plot(520, 360, (-3.2, 2.2), (-3, 3), 'The s-plane: where each pole sits and what it does', ml=20, mb=20)
    s = p.s
    s.rect(p.X(-3.2), p.Y(3), p.X(0) - p.X(-3.2), p.Y(-3) - p.Y(3), '#d1fae5', opacity=0.55)
    s.rect(p.X(0), p.Y(3), p.X(2.2) - p.X(0), p.Y(-3) - p.Y(3), '#fee2e2', opacity=0.55)
    p.axes(cross=True, grid=False)
    p.label(-3.1, 2.65, 'left half: stable', ACCENT, 12, weight='bold')
    p.label(2.1, 2.65, 'right half: unstable', TRUE, 12, 'end', weight='bold')
    p.label(2.15, 0.15, 'Re', INK, 12, 'end')
    p.label(0.08, 2.75, 'Im', INK, 12)
    for (x, y) in [(-2, 0), (-1, 2), (-1, -2), (0, 2), (0, -2), (0, 0), (1, 0)]:
        p.cross(x, y)
    p.label(-2, -0.45, '−2: decays', INK, 12, 'middle')
    p.label(-1, 2.45, '−1 ± 2j: wobble dies away', INK, 12, 'middle')
    p.label(0.15, 1.95, '± 2j: wobbles forever', INK, 12)
    p.label(0.15, -0.45, '0: integrator', INK, 12)
    p.label(1, 0.35, '+1: grows', TRUE, 12, 'middle')
    p.save('ct-pole-map.svg')

    p = Plot(520, 260, (0, 8), (-0.4, 1.2), 'Step response with a right-half-plane zero')
    p.axes(range(0, 9), [-0.4, 0, 0.4, 0.8, 1.2], 'time (s)', 'output', fmt=lambda v: f'{v:g}')
    ts = [i / 50 for i in range(401)]
    p.hline(0, INK, None, 1)
    p.hline(1)
    p.curve(ts, [resp_rhp(t) for t in ts], BLUE)
    p.dot(0.5, resp_rhp(0.5), TRUE)
    p.label(0.7, -0.3, 'dips to −0.21 at t = 0.5 s', TRUE, 12)
    p.save('ct-rhp-zero.svg')


def fig_04():
    b = Blocks(560, 170, 'A negative feedback loop with forward path G and feedback path H')
    y = 60
    b.text(40, y + 5, 'R')
    b.wire([(52, y), (117, y)])
    b.sum(130, y, signs={'w': '+', 's': '−'})
    b.wire([(143, y), (230, y)], label='error')
    b.box(280, y, 100, 40, 'G(s)')
    b.wire([(330, y), (450, y)])
    b.text(462, y + 5, 'Y', anchor='start')
    b.dot(400, y)
    b.wire([(400, y), (400, 130), (330, 130)])
    b.box(280, 130, 100, 36, 'H(s)', fill='#e5e7eb')
    b.wire([(230, 130), (130, 130), (130, y + 13)])
    b.text(540, 25, 'T = G / (1 + GH)', 15, 'end', ACCENT)
    b.save('ct-feedback-rule.svg')

    p = Plot(520, 300, (0, 32), (0, 2500), 'Linearising drag 2.5 v squared at 20 m/s')
    p.axes(range(0, 33, 4), range(0, 2501, 500), 'speed v (m/s)', 'drag force (N)')
    vs = [i / 10 for i in range(321)]
    p.curve(vs, [2.5 * v * v for v in vs], BLUE)
    p.curve(vs, [1000 + 100 * (v - 20) for v in vs], ORANGE, dash='6,4')
    p.dot(20, 1000, TRUE)
    p.label(19.5, 1180, '(20, 1000)', TRUE, 12, 'end')
    p.label(23.5, 2250, 'drag 2.5v²', BLUE, 12, 'end')
    p.label(31.5, 700, 'tangent: slope 100 N per m/s', ORANGE, 12, 'end')
    p.save('ct-linearise-drag.svg')


# ---------- lessons 05-06: time response ----------

def polymul(a, b):
    out = [0.0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def tf_step(num, den, t1, n=2000, u=lambda t: 1.0, delay=0.0):
    """Step response of num/den (highest power first), by controllable canonical form + RK4."""
    a0 = den[0]
    den = [d / a0 for d in den]
    num = [c / a0 for c in num]
    order = len(den) - 1
    num = [0.0] * (order + 1 - len(num)) + num          # pad to order+1
    d0 = num[0]                                         # direct feed (proper case)
    b = [num[i] - d0 * den[i] for i in range(1, order + 1)]   # strictly proper part, highest first
    a = den[1:]

    def f(t, x):
        uu = u(t - delay) if t >= delay else 0.0
        dx = x[1:] + [uu - sum(a[order - 1 - i] * x[i] for i in range(order))]
        return dx
    ts, xs = rk4(f, [0.0] * order, 0, t1, n)
    ys = []
    for t, x in zip(ts, xs):
        uu = u(t - delay) if t >= delay else 0.0
        ys.append(sum(b[order - 1 - i] * x[i] for i in range(order)) + d0 * uu)
    return ts, ys


def second(zeta, wn):
    return [wn * wn], [1, 2 * zeta * wn, wn * wn]


def settle_time(ts, ys, final, band=0.02):
    last = 0.0
    for t, y in zip(ts, ys):
        if abs(y - final) > band * abs(final):
            last = t
    return last


def check_05():
    for k, v in [(1, 0.632), (2, 0.865), (3, 0.950), (4, 0.982)]:
        assert close(1 - math.exp(-k), v, 1e-3)
    assert close(20 * (1 - math.exp(-1)), 12.64, 1e-3) and close(20 * (1 - math.exp(-4)), 19.63, 1e-3)
    m, k, c = 250, 16000, 2000
    wn, z = math.sqrt(k / m), c / (2 * math.sqrt(k * m))
    assert wn == 8 and z == 0.5
    mp = lambda z: math.exp(-math.pi * z / math.sqrt(1 - z * z))
    assert close(mp(0.5), 0.1630, 1e-3)
    wd = wn * math.sqrt(1 - z * z)
    assert close(wd, 6.928, 1e-3) and close(math.pi / wd, 0.4534, 1e-3)
    assert 4 / (z * wn) == 1 and close(1.8 / wn, 0.225)
    for zz, pct in [(0.3, 37), (0.5, 16), (0.7, 4.6), (0.8, 1.5)]:
        assert abs(mp(zz) * 100 - pct) < 0.5, (zz, mp(zz))
    ts, ys = tf_step(*second(0.5, 8), 3, 3000)
    pk = max(ys)
    tpk = ts[ys.index(pk)]
    assert close(pk, 1.163, 1e-3) and abs(tpk - 0.4534) < 0.002
    t7 = settle_time(*tf_step(*second(0.7, 1), 20, 8000), 1, 0.05)
    t1 = settle_time(*tf_step(*second(1.0, 1), 20, 8000), 1, 0.05)
    assert abs(t7 - 2.9) < 0.05 and abs(t1 - 4.74) < 0.05  # zeta 0.7 is within 5% well before zeta 1
    assert close(1 - math.exp(-3), 0.9502, 1e-4)           # quiz
    assert close(mp(0.4), 0.2538, 1e-3) and 4 / (0.4 * 5) == 2


def check_06():
    kp = 500 / 50
    assert kp == 10 and close(20 / (1 + kp), 1.818)
    assert close(20 / (1 + 5000 / 50), 0.198)
    assert 1 / (1 + 4) == 0.2 and 1 / (8 / 2) == 0.25       # quiz
    # step test: K=2, theta=3, tau=10; steepest tangent at theta with slope K/tau, meets K at theta+tau
    assert 3 + 2 / (2 / 10) == 13 and close(3 / 10, 0.3)


def fig_05():
    p = Plot(540, 280, (0, 120), (0, 22), 'First-order step response of the car')
    p.axes(range(0, 121, 20), range(0, 23, 4), 'time (s)', 'speed (m/s)')
    ts = [i / 4 for i in range(481)]
    p.hline(20)
    p.curve(ts, [20 * (1 - math.exp(-t / 20)) for t in ts], BLUE)
    for k, lab in [(1, '63%'), (2, '86%'), (3, '95%'), (4, '98%')]:
        v = 20 * (1 - math.exp(-k))
        p.dot(20 * k, v, ORANGE)
        p.label(20 * k + 1.5, v - 1.6, f'{lab} at {20 * k} s', ORANGE, 11)
    p.save('ct-first-order.svg')

    p = Plot(560, 320, (0, 12), (0, 1.8), 'Second-order step responses for five damping ratios')
    p.axes(range(0, 13, 2), [0, 0.5, 1, 1.5], 'time × ωn', 'output')
    p.hline(1)
    cols = {0.2: TRUE, 0.5: ORANGE, 0.7: BLUE, 1.0: ACCENT, 2.0: PURPLE}
    for z, c in cols.items():
        ts, ys = tf_step(*second(z, 1), 12, 2400)
        p.curve(ts, ys, c, 2)
    p.legend([(f'ζ = {z:g}', c, None) for z, c in cols.items()], 450, 30)
    p.save('ct-second-order-zetas.svg')

    # pole geometry
    wn, z = 3.0, 0.5
    sig, wd = z * wn, wn * math.sqrt(1 - z * z)
    p = Plot(460, 330, (-3.6, 1.0), (-0.6, 3.4), 'Reading a pole: natural frequency, damping and decay', ml=20, mb=20)
    p.axes(cross=True, grid=False)
    p.s.line(p.X(0), p.Y(0), p.X(-sig), p.Y(wd), BLUE, 2)
    p.s.line(p.X(-sig), p.Y(wd), p.X(-sig), p.Y(0), GREY, 1.4, '5,4')
    p.s.line(p.X(-sig), p.Y(wd), p.X(0), p.Y(wd), GREY, 1.4, '5,4')
    p.cross(-sig, wd)
    # angle arc from negative real axis
    r = 0.7
    th = math.acos(z)
    pts = [(-r * math.cos(a * th / 20), r * math.sin(a * th / 20)) for a in range(21)]
    p.curve([q[0] for q in pts], [q[1] for q in pts], ORANGE, 1.6)
    p.label(-0.95, 0.35, 'θ', ORANGE, 14)
    p.label(-sig / 2 - 0.15, wd / 2 + 0.15, 'ωn', BLUE, 14, 'end')
    p.label(-sig / 2, -0.35, 'ζωn', INK, 13, 'middle')
    p.label(0.08, wd / 2, 'ωd', INK, 13)
    p.label(-sig, wd + 0.25, 'pole', TRUE, 12, 'middle')
    p.label(-3.5, 3.1, 'cos θ = ζ', ORANGE, 13)
    p.label(0.9, 0.12, 'Re', INK, 12, 'end')
    p.save('ct-pole-geometry.svg')

    ts, ys = tf_step(*second(0.5, 8), 2, 2000)
    p = Plot(540, 280, (0, 2), (0, 1.3), 'The suspension step response with its specifications')
    p.axes([0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2], [0, 0.25, 0.5, 0.75, 1, 1.25], 'time (s)', 'output')
    p.s.rect(p.X(0), p.Y(1.02), p.X(2) - p.X(0), p.Y(0.98) - p.Y(1.02), '#d1fae5', opacity=0.9)
    p.hline(1)
    p.curve(ts, ys, BLUE)
    pk = max(ys)
    tp = ts[ys.index(pk)]
    p.dot(tp, pk, TRUE)
    p.label(tp + 0.04, pk + 0.03, f'peak {pk:.3f} at {tp:.2f} s', TRUE, 12)
    p.vline(1.0, ACCENT)
    p.label(1.02, 0.2, 'within 2% from ≈ 1 s', ACCENT, 12)
    p.save('ct-suspension-step.svg')


def fig_06():
    base_n, base_d = [1], [1, 1, 1]
    p = Plot(560, 300, (0, 14), (0, 1.3), 'Dominant poles: a far pole barely matters, a near one does')
    p.axes(range(0, 15, 2), [0, 0.25, 0.5, 0.75, 1, 1.25], 'time (s)', 'output')
    p.hline(1)
    ts, ys = tf_step(base_n, base_d, 14, 2800)
    p.curve(ts, ys, BLUE, 2.4)
    ts, ys5 = tf_step([5], polymul(base_d, [1, 5]), 14, 2800)
    p.curve(ts, ys5, ORANGE, 2, '6,4')
    ts, ys1 = tf_step([1], polymul(base_d, [1, 1]), 14, 2800)
    p.curve(ts, ys1, TRUE, 2)
    assert abs(max(ys) - max(ys5)) < 0.005 and max(abs(a - b) for a, b in zip(ys, ys5)) < 0.11
    assert max(ys1) < max(ys) - 0.05
    p.legend([('pair alone: −0.5 ± 0.87j', BLUE, None), ('plus a pole at −5', ORANGE, '6,4'),
              ('plus a pole at −1', TRUE, None)], 330, 210)
    p.save('ct-dominant-poles.svg')

    p = Plot(540, 260, (0, 15), (0, 22), 'Proportional cruise control settles short of the reference')
    p.axes(range(0, 16, 3), range(0, 23, 4), 'time (s)', 'speed (m/s)')
    ts = [i / 20 for i in range(301)]
    p.hline(20, ORANGE)
    p.label(14.8, 20.6, 'reference 20', ORANGE, 12, 'end')
    p.curve(ts, [200 / 11 * (1 - math.exp(-0.55 * t)) for t in ts], BLUE)
    p.label(14.8, 16.2, 'settles at 18.18: error 1.82', BLUE, 12, 'end')
    p.save('ct-car-offset.svg')

    K, th, tau = 2, 3, 10
    p = Plot(540, 280, (0, 50), (0, 2.4), 'Reading dead time, time constant and gain from a step test')
    p.axes(range(0, 51, 5), [0, 0.5, 1, 1.5, 2], 'time (s)', 'output')
    ts = [i / 10 for i in range(501)]
    p.curve(ts, [0 if t < th else K * (1 - math.exp(-(t - th) / tau)) for t in ts], BLUE)
    p.hline(K)
    tt = [th + i / 10 for i in range(0, 101)]
    p.curve(tt, [K / tau * (t - th) for t in tt], ORANGE, 1.8, '6,4')
    p.vline(th, GREY)
    p.vline(th + tau, GREY)
    p.label(th + 0.5, 2.25, 'θ = 3', INK, 12)
    p.label(th + tau + 0.5, 2.25, '13 s: θ + τ', INK, 12)
    p.label(49, 1.75, 'final change 2 = K × step', BLUE, 12, 'end')
    p.label(th + tau / 2 + 1, 0.55, 'steepest tangent', ORANGE, 12)
    p.save('ct-step-test.svg')


# ---------- lessons 07-08: PID ----------

def pid_car(kp, ki, kd=0.0, aw=True, r=20.0, t_end=40.0, dt=0.1, umax=3000.0, beta=1.0, alpha=0.8):
    """The same discrete PID and Euler car as lesson 08's pid_car.py. Returns ts, vs, peak."""
    integ, prev, dfilt, v = 0.0, None, 0.0, 0.0
    ts, vs, peak = [], [], 0.0
    for k in range(int(round(t_end / dt)) + 1):
        ts.append(k * dt)
        vs.append(v)
        e = r - v
        p = kp * (beta * r - v)
        integ += ki * e * dt
        dy = 0.0 if prev is None else (v - prev) / dt
        dfilt = alpha * dfilt + (1 - alpha) * dy
        prev = v
        u = p + integ - kd * dfilt
        us = min(max(u, 0.0), umax)
        if aw and u != us:
            integ -= ki * e * dt
        v += dt * (us - CAR_B * v) / CAR_M
        peak = max(peak, v)
    return ts, vs, peak


def check_07():
    ts, vs, pk = pid_car(500, 100, aw=True)
    assert f'{pk:.2f}' == '20.23'
    assert [f'{vs[i]:.2f}' for i in range(0, 401, 50)] == \
        ['0.00', '13.30', '19.52', '20.23', '20.11', '20.03', '20.00', '20.00', '20.00']
    ts, vs, pk = pid_car(500, 100, aw=False)
    assert f'{pk:.2f}' == '27.81'
    assert [f'{vs[i]:.2f}' for i in range(0, 401, 50)] == \
        ['0.00', '13.30', '23.65', '26.88', '22.42', '20.45', '20.02', '19.98', '19.99']
    assert 100 / 4 == 25                                           # quiz: PB


def check_08():
    K, th, tau = 2, 3, 10
    assert 1.2 * tau / (K * th) == 2 and 2 * th == 6 and 0.5 * th == 1.5
    assert close(2 / 6, 0.333) and 2 * 1.5 == 3
    assert close(tau / (K * (6 + th)), 0.5556)
    # quizzes
    assert close(1.2 * 10 / (1.5 * 2), 4) and close(0.9 * 10 / (1.5 * 2), 3)
    assert 10 / 2 == 5 and close(0.6 * 8, 4.8) and 10 / 8 == 1.25
    assert 10 / (4 * (4 + 1)) == 0.5
    # practice hint: P-only error below 0.5 needs Kp > 1950
    assert close(20 / (1 + 1950 / 50), 0.5)


def fig_07():
    p = Plot(540, 270, (0, 40), (0, 22), 'Cruise control: proportional alone against proportional plus integral')
    p.axes(range(0, 41, 5), range(0, 23, 4), 'time (s)', 'speed (m/s)')
    p.hline(20, GREY)
    ts, vs, _ = pid_car(500, 0)
    assert close(vs[-1], 18.18, 1e-3)
    p.curve(ts, vs, ORANGE)
    ts, vs, _ = pid_car(500, 100)
    p.curve(ts, vs, BLUE)
    p.label(39, 16.6, 'P only: settles at 18.18', ORANGE, 12, 'end')
    p.label(39, 20.6, 'P + I: reaches 20', BLUE, 12, 'end')
    p.save('ct-car-p-vs-pi.svg')

    p = Plot(540, 290, (0, 40), (0, 30), 'Integral windup: the same PI controller with and without anti-windup')
    p.axes(range(0, 41, 5), range(0, 31, 5), 'time (s)', 'speed (m/s)')
    p.hline(20, GREY)
    ts, vs, pk = pid_car(500, 100, aw=False)
    p.curve(ts, vs, TRUE)
    i = vs.index(max(vs))
    p.dot(ts[i], vs[i], TRUE)
    p.label(ts[i] + 0.8, vs[i] + 0.6, f'no anti-windup: peak {pk:.2f}', TRUE, 12)
    ts, vs, pk = pid_car(500, 100, aw=True)
    p.curve(ts, vs, BLUE)
    p.label(39, 17.5, f'with anti-windup: peak {pk:.2f}', BLUE, 12, 'end')
    p.s.rect(p.X(0), p.Y(30), p.X(5.3) - p.X(0), p.Y(0) - p.Y(30), ORANGE, opacity=0.12)
    p.label(0.4, 27.5, 'engine at 3000 N', ORANGE, 11)
    p.save('ct-windup.svg')


def fig_08():
    b = Blocks(760, 210, 'Cascade control: an outer loop setting the setpoint of a faster inner loop')
    y = 70
    b.text(30, y + 5, 'r')
    b.wire([(40, y), (77, y)])
    b.sum(90, y, signs={'w': '+', 's': '−'})
    b.wire([(103, y), (140, y)])
    b.box(195, y, 110, 44, 'Outer\ncontroller')
    b.wire([(250, y), (317, y)], label='setpoint', dx=-8, dy=-10)
    b.sum(330, y, signs={'w': '+', 's': '−'})
    b.wire([(343, y), (380, y)])
    b.box(435, y, 110, 44, 'Inner\ncontroller')
    b.wire([(490, y), (525, y)])
    b.box(575, y, 100, 40, 'Actuator')
    b.wire([(625, y), (655, y)])
    b.box(695, y, 80, 40, 'Plant')
    b.wire([(735, y), (755, y)], arrow=False)
    b.dot(640, y)
    b.wire([(640, y), (640, 130), (330, 130), (330, y + 13)], label='fast inner measurement', at=1, dy=-7)
    b.dot(750, y)
    b.wire([(750, y), (750, 185), (90, 185), (90, y + 13)], label='slow output measurement', at=1, dy=-7)
    b.save('ct-cascade.svg')


# ---------- lessons 09-10: stability and root locus ----------

def roots(coeffs):
    """All roots of a polynomial (highest power first), by Durand-Kerner."""
    c = [complex(x) / coeffs[0] for x in coeffs]
    n = len(c) - 1
    z = [complex(0.4, 0.9) ** k for k in range(n)]
    for _ in range(500):
        new = []
        for i in range(n):
            num = sum(c[j] * z[i] ** (n - j) for j in range(n + 1))
            den = 1
            for k in range(n):
                if k != i:
                    den *= (z[i] - z[k])
            new.append(z[i] - num / den)
        if max(abs(a - b) for a, b in zip(new, z)) < 1e-13:
            z = new
            break
        z = new
    return z


def routh(coeffs):
    """First column of the Routh array (no zero-row handling)."""
    r1, r2 = list(coeffs[0::2]), list(coeffs[1::2])
    r2 += [0] * (len(r1) - len(r2))
    col = [r1[0], r2[0]]
    while len(r2) > 1 or (r2 and r2[0] != 0 and len(col) < len(coeffs)):
        nxt = [(r2[0] * r1[i + 1] - r1[0] * r2[i + 1]) / r2[0] for i in range(len(r1) - 1)]
        if not nxt:
            break
        r1, r2 = r2, nxt + [0] * (len(r2) - len(nxt))
        col.append(r2[0])
        if len(col) == len(coeffs):
            break
    return col


def sign_changes(col):
    return sum(1 for a, b in zip(col, col[1:]) if a * b < 0)


def check_09():
    for K, ok in [(1, True), (5.9, True), (6.1, False)]:
        rs = roots([1, 3, 2, K])
        assert (max(r.real for r in rs) < 0) == ok
    rs = roots([1, 3, 2, 6])
    assert any(abs(r.imag - math.sqrt(2)) < 1e-6 and abs(r.real) < 1e-6 for r in rs)
    assert close(2 * math.pi / math.sqrt(2), 4.443)
    assert sign_changes([1, 4, -2, 5]) == 2                       # quiz
    assert 4 * 5 == 20 and close(math.sqrt(5), 2.236)
    rs = roots([1, 4, 5, 20])
    assert any(abs(r.imag - math.sqrt(5)) < 1e-6 for r in rs)
    assert max(r.real for r in roots([1, 2, -1, 6])) > 0          # quiz 1: the sign-change option


def check_10():
    s = (-6 + math.sqrt(36 - 24)) / 6
    assert close(s, -0.4226) and close(-(s ** 3 + 3 * s ** 2 + 2 * s), 0.3849)
    assert (0 - 1 - 2) / 3 == -1
    assert close((0 - 2 - 5) / 3, -2.3333)


def fig_10():
    p = Plot(520, 440, (-3.5, 1.0), (-2.6, 2.6), 'Root locus of K over s(s+1)(s+2)', ml=24, mb=24)
    p.axes(cross=True, grid=False)
    for v in (-3, -2, -1):
        p.label(v, -0.28, f'{v}', INK, 11, 'middle')
    for v in (-2, -1, 1, 2):
        p.label(0.1, v - 0.05, f'{v}j', INK, 11)
    # asymptotes from centroid -1 at +-60 degrees
    for ang in (60, -60):
        a = math.radians(ang)
        p.curve([-1, -1 + 2.9 * math.cos(a)], [0, 2.9 * math.sin(a)], GREY, 1.3, '5,4')
    branches = [[], [], []]
    prev = [0j, -1 + 0j, -2 + 0j]
    Ks = [0.0005 * 1.03 ** i for i in range(420)]
    for K in Ks:
        rs = roots([1, 3, 2, K])
        # match to previous by nearest
        out = []
        avail = list(rs)
        for q in prev:
            j = min(range(len(avail)), key=lambda i: abs(avail[i] - q))
            out.append(avail.pop(j))
        prev = out
        for b, r in zip(branches, out):
            b.append(r)
    for b in branches:
        p.curve([r.real for r in b], [r.imag for r in b], BLUE, 2.4)
    for x in (0, -1, -2):
        p.cross(x, 0)
    p.dot(-0.4226, 0, ORANGE, 5)
    p.label(-0.55, 0.3, 'breakaway −0.423 (K = 0.385)', ORANGE, 11, 'end')
    for y in (math.sqrt(2), -math.sqrt(2)):
        p.dot(0, y, TRUE, 5)
    p.label(-0.12, 1.55, '±1.414j at K = 6', TRUE, 12, 'end')
    p.dot(-1, 0, GREY, 3)
    p.label(-1.05, -0.5, 'centroid −1', GREY, 11, 'end')
    p.label(-3.4, 2.3, 'poles × at 0, −1, −2', TRUE, 12)
    p.save('ct-root-locus.svg')


# ---------- lessons 11-12: frequency response ----------

def db(x):
    return 20 * math.log10(x)


def phase_deg(z, prev=None):
    """Angle in degrees, unwrapped towards prev."""
    a = math.degrees(cmath.phase(z))
    if prev is not None:
        while a - prev > 180:
            a -= 360
        while a - prev < -180:
            a += 360
    return a


def L_loop(w, K=1.0):
    s = 1j * w
    return K / (s * (s + 1) * (s + 2))


def bisect(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = (a + b) / 2
        if (f(m) > 0) == (fa > 0):
            a, fa = m, f(m)
        else:
            b = m
    return (a + b) / 2


def loop_margins():
    wc = bisect(lambda w: abs(L_loop(w)) - 1, 0.1, 1.0)
    pm = 180 + (-90 - math.degrees(math.atan(wc)) - math.degrees(math.atan(wc / 2)))
    w180 = bisect(lambda w: -90 - math.degrees(math.atan(w)) - math.degrees(math.atan(w / 2)) + 180, 0.5, 5)
    gm = 1 / abs(L_loop(w180))
    return wc, pm, w180, gm


def check_11():
    assert close(abs(20j * 0.6283 + 1), 12.6, 2e-3)
    assert close(-math.degrees(math.atan(20 * 0.6283)), -85.45, 1e-3)
    for g, d in [(0.01, -40), (0.1, -20), (0.5, -6), (2, 6), (10, 20), (100, 40)]:
        assert abs(db(g) - d) < 0.05
    mr = lambda z: 1 / (2 * z * math.sqrt(1 - z * z))
    assert close(db(mr(0.1)), 14.02, 1e-3) and close(db(mr(0.3)), 4.85, 2e-3) and close(db(mr(0.5)), 1.25, 1e-2)
    assert close(mr(0.5), 1.1547) and close(8 * math.sqrt(0.5), 5.657)
    assert close(mr(0.3), 1.7471) and close(db(20), 26.02)
    assert close(db(abs(L_loop(1))), db(0.5 / (math.sqrt(2) * math.sqrt(1.25))), 1e-6)


def check_12():
    wc, pm, w180, gm = loop_margins()
    assert close(wc, 0.4457, 1e-3) and close(pm, 53.4, 2e-3)
    assert close(w180, math.sqrt(2), 1e-6) and close(gm, 6, 1e-6) and close(db(gm), 15.56, 1e-3)
    lost = math.degrees(wc * 0.5)
    assert close(lost, 12.77, 2e-3) and close(pm - lost, 40.6, 2e-3)
    mp = lambda z: math.exp(-math.pi * z / math.sqrt(1 - z * z))
    assert close(mp(0.534), 0.139, 2e-2) and close(mp(0.406), 0.245, 2e-2)
    assert 180 - 140 == 40 and close(db(4), 12.04) and close(math.degrees(0.5), 28.65)


def bode(name, title, curves, wr, magr, phr, magt, pht, marks=None, H=480, legend=None):
    """A Bode plot: magnitude panel above phase panel, sharing a log frequency axis.
    curves: list of (fn(w) -> complex, color, dash). marks(top, bot) draws extras in data units
    (x is log10 of frequency)."""
    a, b = math.log10(wr[0]), math.log10(wr[1])
    top = Plot(560, H, (a, b), magr, title, mt=16, mb=H // 2 + 6)
    bot = Plot(560, H, (a, b), phr, title, mt=H // 2 + 20, mb=44)
    bot.s = top.s
    dec = range(int(math.floor(a)), int(math.ceil(b)) + 1)
    fx = lambda v: f'{10 ** v:g}'
    top.axes(dec, magt, '', '', xticklabels=False)
    bot.axes(dec, pht, 'frequency ω (rad/s), log scale', '', xfmt=fx)
    for pl, lab in ((top, 'magnitude (dB)'), (bot, 'phase (deg)')):
        yc = (pl.Y(pl.y0) + pl.Y(pl.y1)) / 2
        pl.s.add(f'<text x="14" y="{yc:.1f}" font-size="12" fill="{INK}" text-anchor="middle" '
                 f'transform="rotate(-90 14 {yc:.1f})" font-family="system-ui, sans-serif">{lab}</text>')
    ws = [10 ** (a + (b - a) * i / 400) for i in range(401)]
    for fn, c, d in curves:
        top.curve([math.log10(w) for w in ws], [db(abs(fn(w))) for w in ws], c, 2.2, d)
        ph, prev = [], None
        for w in ws:
            prev = phase_deg(fn(w), prev)
            ph.append(prev)
        bot.curve([math.log10(w) for w in ws], ph, c, 2.2, d)
    if marks:
        marks(top, bot)
    if legend:
        top.legend(legend, 380, 34)
    top.save(name)


def fig_11():
    lw = math.log10
    pole = lambda w: 1 / (1 + 1j * w)

    def m(t, b_):
        t.curve([-2, 0, 2], [0, 0, -40], GREY, 1.6, '6,4')
        b_.curve([-2, -1, 1, 2], [0, 0, -90, -90], GREY, 1.6, '6,4')
        t.dot(0, db(abs(pole(1))), TRUE)
        t.label(0.08, -1, '−3 dB at the corner', TRUE, 12)
        t.label(1.05, -16, '−20 dB per decade', INK, 12)
        b_.dot(0, -45, TRUE)
        b_.label(0.1, -40, '−45° at the corner', TRUE, 12)
    bode('ct-bode-pole.svg', 'Bode plot of a single pole with corner at 1 rad/s', [(pole, BLUE, None)],
         (0.01, 100), (-42, 5), (-95, 5), range(-40, 1, 10), range(-90, 1, 45), m)

    def m2(t, b_):
        b_.hline(-180, TRUE, '5,4')
        b_.dot(lw(math.sqrt(2)), -180, TRUE)
        b_.label(lw(math.sqrt(2)) + 0.06, -170, '−180° at 1.414 rad/s', TRUE, 12)
        t.hline(0, GREY, '5,4')
        t.label(-1.9, 22, 'slope −20', INK, 11)
        t.label(-0.05, -32, 'then −40', INK, 11)
        t.label(0.32, -66, 'then −60 dB/decade', INK, 11)
    bode('ct-bode-loop.svg', 'Bode plot of 1 over s(s+1)(s+2)', [(L_loop, BLUE, None)],
         (0.01, 10), (-80, 40), (-280, -80), range(-80, 41, 20), [-270, -180, -90], m2)

    p = Plot(560, 300, (-1, 1), (-30, 16), 'Second-order resonance for four damping ratios')
    p.axes([-1, 0, 1], range(-30, 16, 10), 'frequency ω/ωn, log scale', 'magnitude (dB)', xfmt=lambda v: f'{10 ** v:g}')
    ws = [10 ** (-1 + 2 * i / 600) for i in range(601)]
    cols = {0.1: TRUE, 0.3: ORANGE, 0.5: BLUE, 0.707: ACCENT}
    for z, c in cols.items():
        p.curve([math.log10(w) for w in ws], [db(abs(1 / (1 - w * w + 2j * z * w))) for w in ws], c, 2.2)
    p.hline(0, GREY, '5,4')
    p.legend([(f'ζ = {z:g}', c, None) for z, c in cols.items()], 440, 30)
    p.save('ct-resonance.svg')


def fig_12():
    wc, pm, w180, gm = loop_margins()
    lw = math.log10

    def m(t, b_):
        t.hline(0, GREY, '5,4')
        b_.hline(-180, GREY, '5,4')
        t.vline(lw(wc), ORANGE, '4,3')
        b_.vline(lw(wc), ORANGE, '4,3')
        t.vline(lw(w180), TRUE, '4,3')
        b_.vline(lw(w180), TRUE, '4,3')
        t.dot(lw(wc), 0, ORANGE)
        ph = 180 - pm
        b_.s.line(b_.X(lw(wc)), b_.Y(-ph), b_.X(lw(wc)), b_.Y(-180), ORANGE, 3)
        b_.label(lw(wc) - 0.05, -150, f'PM {pm:.1f}°', ORANGE, 12, 'end')
        t.s.line(t.X(lw(w180)), t.Y(0), t.X(lw(w180)), t.Y(-db(gm)), TRUE, 3)
        t.label(lw(w180) + 0.05, -8, f'GM {db(gm):.1f} dB', TRUE, 12)
        t.label(lw(wc) - 0.05, -14, f'ωc = {wc:.3f}', ORANGE, 12, 'end')
        b_.label(lw(w180) + 0.05, -200, 'phase −180° at 1.414', TRUE, 12)
    bode('ct-margins.svg', 'Gain and phase margin of 1 over s(s+1)(s+2)', [(L_loop, BLUE, None)],
         (0.05, 10), (-60, 30), (-270, -90), range(-60, 31, 20), [-270, -180, -90], m)


# ---------- lessons 13-14: Nyquist and robustness ----------

def closest_to_minus1(K=1.0):
    ws = [10 ** (-2 + 4 * i / 20000) for i in range(20001)]
    best = min(ws, key=lambda w: abs(L_loop(w, K) + 1))
    return best, abs(L_loop(best, K) + 1)


def check_13():
    w, d = closest_to_minus1()
    assert close(d, 0.638, 2e-3), d
    assert close(1 / d, 1.568, 3e-3)
    assert close(L_loop(math.sqrt(2)).real, -1 / 6, 1e-6)
    ms = 2
    assert ms / (ms - 1) == 2 and close(math.degrees(2 * math.asin(1 / (2 * ms))), 28.96)
    assert 1 / 0.25 == 4 and 1 / 0.4 == 2.5


def check_14():
    wc, pm, _, _ = loop_margins()
    assert close(math.radians(pm), 0.932, 2e-3) and close(math.radians(pm) / wc, 2.09, 3e-3)
    # waterbed: integral of ln|S| from 0 to inf is 0 (stable plant, pole excess 3)
    S = lambda w: 1 / abs(1 + L_loop(w))
    total, n, top = 0.0, 400000, 400.0
    h = top / n
    for i in range(n):
        w = (i + 0.5) * h
        total += math.log(S(w)) * h
    assert abs(total) < 0.01, total
    ws = [i / 1000 for i in range(1, 5000)]
    peak = max(ws, key=lambda w: math.log(S(w)))
    assert close(math.log(S(peak)), 0.450, 1e-2) and abs(peak - 0.73) < 0.01
    zero = bisect(lambda w: math.log(S(w)), 0.1, 0.9)
    assert abs(zero - 0.408) < 0.002
    assert close(0.6 / 0.4, 1.5)


def fig_13():
    p = Plot(520, 460, (-2.2, 0.8), (-2.4, 0.6), 'Nyquist plot of 1 over s(s+1)(s+2)', ml=24, mb=24)
    p.axes(cross=True, grid=False)
    th = [2 * math.pi * i / 200 for i in range(201)]
    p.curve([math.cos(t) for t in th], [math.sin(t) for t in th], GREY, 1.3, '5,4')
    ws = [10 ** (-1.2 + 3.2 * i / 800) for i in range(801)]
    pts = [L_loop(w) for w in ws]
    p.curve([z.real for z in pts], [z.imag for z in pts], BLUE, 2.4)
    p.curve([z.real for z in pts], [-z.imag for z in pts], BLUE, 1.4, '6,4')
    # arrow along increasing frequency near w = 0.6
    z1, z2 = L_loop(0.6), L_loop(0.62)
    p.arrow(z1.real, z1.imag, z2.real - z1.real, z2.imag - z1.imag, BLUE, 10)
    p.cross(-1, 0, TRUE, 7)
    p.label(-1.02, 0.15, '−1', TRUE, 13, 'middle')
    p.dot(-1 / 6, 0, ORANGE)
    p.label(-0.2, 0.32, '−1/6: GM = 6', ORANGE, 12, 'end')
    w, d = closest_to_minus1()
    z = L_loop(w)
    p.s.line(p.X(-1), p.Y(0), p.X(z.real), p.Y(z.imag), ACCENT, 2)
    p.dot(z.real, z.imag, ACCENT)
    p.label(z.real - 0.08, z.imag - 0.18, f'closest: {d:.2f}', ACCENT, 12, 'end')
    wc, pm, _, _ = loop_margins()
    zc = L_loop(wc)
    p.dot(zc.real, zc.imag, PURPLE)
    p.label(zc.real + 0.07, zc.imag - 0.05, f'unit circle: PM {pm:.1f}°', PURPLE, 12)
    p.label(-2.1, -2.25, 'solid: ω > 0; dashed: ω < 0', INK, 11)
    p.save('ct-nyquist.svg')


def fig_14():
    S = lambda w: 1 / abs(1 + L_loop(w))
    p = Plot(560, 280, (0, 4), (-3, 0.8), 'The waterbed: log sensitivity of 1 over s(s+1)(s+2)')
    p.axes(range(0, 5), [-3, -2, -1, 0, 0.5], 'frequency ω (rad/s), linear scale', 'ln |S|')
    ws = [0.02 + i * (3.98 / 600) for i in range(601)]
    ys = [math.log(S(w)) for w in ws]
    neg = [(w, y) for w, y in zip(ws, ys) if y <= 0 and w < 0.6]
    pos = [(w, y) for w, y in zip(ws, ys) if y >= 0]
    for pts, col in ((neg, ACCENT), (pos, TRUE)):
        d = f'M{p.X(pts[0][0]):.1f},{p.Y(0):.1f} ' + ' '.join(f'L{p.X(w):.1f},{p.Y(max(y, -3)):.1f}' for w, y in pts) \
            + f' L{p.X(pts[-1][0]):.1f},{p.Y(0):.1f} Z'
        p.s.add(f'<path d="{d}" fill="{col}" fill-opacity="0.18" stroke="none"/>')
    p.hline(0, INK, None, 1)
    p.curve(ws, ys, BLUE)
    p.label(0.15, -2.3, 'disturbances rejected', ACCENT, 12)
    p.label(1.3, 0.55, 'disturbances amplified', TRUE, 12)
    p.label(3.9, -1.0, 'equal areas', INK, 12, 'end')
    p.save('ct-waterbed.svg')


# ---------- lessons 15-16: state space ----------

SUSP_A = (0.0, 1.0, -64.0, -8.0)


def susp_free(x0=-0.05, t1=2.0, n=4000):
    a, b, c, d = SUSP_A
    return rk4(lambda t, x: [a * x[0] + b * x[1], c * x[0] + d * x[1]], [x0, 0.0], 0, t1, n)


def check_15():
    m, c, k = 250, 2000, 16000
    assert -k / m == -64 and -c / m == -8 and 1 / m == 0.004
    ts, xs = susp_free()
    # first upward zero crossing of position: speed there
    for (t0, p0), (t1, p1) in zip(zip(ts, xs), zip(ts[1:], xs[1:])):
        if p0[0] < 0 <= p1[0]:
            v = p0[1]
            break
    assert abs(v - 0.120) < 0.002, v
    assert close(max(x[1] for x in xs), 0.2185, 2e-3) and close(max(x[0] for x in xs), 0.00815, 2e-2)
    assert abs(xs[-1][0]) < 1e-4


def check_16():
    l1, l2 = eig2(*SUSP_A)
    assert close(l1.real, -4) and close(abs(l1.imag), 6.928, 1e-3)
    assert close(0.004 / 64, 1 / 16000)
    ad = math.exp(-0.05 * 0.1)
    assert close(ad, 0.99501, 1e-5) and close((ad - 1) / -0.05 * 0.001, 9.975e-5, 1e-3)
    assert sorted(x.real for x in eig2(0, 1, -6, -5)) == [-3, -2]
    assert sorted(x.real for x in eig2(0, 1, 4, 0)) == [-2, 2]
    assert close(math.exp(-0.1), 0.9048, 1e-4)


def fig_15():
    ts, xs = susp_free()
    p = Plot(500, 340, (-0.06, 0.03), (-0.08, 0.26), 'The suspension state spiralling into rest', ml=60)
    p.axes([-0.06, -0.04, -0.02, 0, 0.02], [-0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.25], 'position x1 (m)', 'speed x2 (m/s)',
           fmt=lambda v: f'{v:g}')
    p.hline(0, INK, None, 1)
    p.vline(0, INK, None, 1)
    p.curve([x[0] for x in xs], [x[1] for x in xs], BLUE, 2.4)
    for i in (60, 260, 520):
        x0, x1 = xs[i], xs[i + 5]
        p.arrow(x0[0], x0[1], x1[0] - x0[0], x1[1] - x0[1], BLUE, 10)
    p.dot(-0.05, 0, ORANGE, 5)
    p.label(-0.05, -0.025, 'start: 5 cm down, at rest', ORANGE, 12, 'middle')
    p.dot(0, 0, INK, 4)
    p.label(0.002, -0.03, 'rest', INK, 12)
    p.save('ct-suspension-state.svg')


# ---------- lessons 17-18: controllability, observability, pole placement ----------

def mat2_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def det2(m):
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def check_17():
    A = [[0, 1], [-64, -8]]
    B = [[0], [0.004]]
    AB = mat2_mul(A, B)
    Cm = [[B[0][0], AB[0][0]], [B[1][0], AB[1][0]]]
    assert close(AB[1][0], -0.032) and close(det2(Cm), -0.000016)
    Acar = [[0, 1], [0, -0.05]]
    CA = mat2_mul([[0, 1]], Acar)
    assert CA == [[0, -0.05]] and det2([[0, 1], CA[0]]) == 0
    # quiz 1: A = diag(-1, 2), B = [1, 0]
    assert det2([[1, -1], [0, 0]]) == 0
    # quiz 2: observability of [[0,1],[-2,-3]] with C=[1 0]
    assert mat2_mul([[1, 0]], [[0, 1], [-2, -3]]) == [[0, 1]]


def placed_free(K, x0=-0.05, t1=2.0, n=4000):
    k1, k2 = K
    return rk4(lambda t, x: [x[1], (-64 - 0.004 * k1) * x[0] + (-8 - 0.004 * k2) * x[1]], [x0, 0.0], 0, t1, n)


def check_18():
    k2 = (16 - 8) / 0.004
    k1 = (128 - 64) / 0.004
    assert close(k1, 16000) and close(k2, 2000)
    l1, _ = eig2(0, 1, -64 - 0.004 * k1, -8 - 0.004 * k2)
    assert close(l1.real, -8) and close(abs(l1.imag), 8)
    assert 16000 * 0.05 == 800
    ts, xs = placed_free((16000, 2000))
    assert close(max(x[0] for x in xs), 0.05 * math.exp(-math.pi), 2e-2)          # 2.2 mm
    assert settle_time(ts, [x[0] for x in xs], 0, 0) < 9                          # sanity
    st = max(t for t, x in zip(ts, xs) if abs(x[0]) > 0.001)                      # within 1 mm
    assert 0.35 < st < 0.6, st
    ts2, xs2 = susp_free()
    st2 = max(t for t, x in zip(ts2, xs2) if abs(x[0]) > 0.001)
    assert 0.8 < st2 < 1.2, st2
    assert 2 - 7 == -5 and 2 - 6 == -4 and 3 + 7 == 10 and 2 + 10 == 12


def fig_18():
    p = Plot(540, 280, (0, 1.6), (-0.055, 0.015), 'Suspension released from 5 cm: passive against placed poles', ml=64)
    p.axes([0, 0.4, 0.8, 1.2, 1.6], [-0.05, -0.04, -0.03, -0.02, -0.01, 0, 0.01], 'time (s)', 'position (m)')
    p.hline(0, INK, None, 1)
    ts, xs = susp_free(t1=1.6, n=3200)
    p.curve(ts, [x[0] for x in xs], ORANGE)
    ts, xs = placed_free((16000, 2000), t1=1.6, n=3200)
    p.curve(ts, [x[0] for x in xs], BLUE)
    p.legend([('passive: poles −4 ± 6.93j', ORANGE, None), ('placed: poles −8 ± 8j', BLUE, None)], 290, 170)
    p.label(0.5, 0.0115, 'overshoot 8 mm', ORANGE, 11)
    p.label(0.23, 0.005, '2 mm', BLUE, 11)
    p.save('ct-pole-placement.svg')


# ---------- lessons 19-20: observers and the Kalman filter ----------

OBS_L = (40.0, 768.0)


def observer_run(t1=0.6, n=2400):
    """True suspension from -5 cm, observer from 0, measuring position only. States: x1, x2, xh1, xh2."""
    l1, l2 = OBS_L

    def f(t, s):
        x1, x2, h1, h2 = s
        y = x1
        inn = y - h1
        return [x2, -64 * x1 - 8 * x2, h2 + l1 * inn, -64 * h1 - 8 * h2 + l2 * inn]
    return rk4(f, [-0.05, 0.0, 0.0, 0.0], 0, t1, n)


def kalman_car(seed=7, dt=0.5, t_end=30.0, sigma_v=1.0, sigma_w=0.05):
    import random
    rng = random.Random(seed)
    a = math.exp(-CAR_B / CAR_M * dt)
    b = (1 - a) / CAR_B
    u = 800.0
    Q, R = sigma_w ** 2, sigma_v ** 2
    v, vh, P = 10.0, 12.0, 4.0
    ts, true, meas, est, gains = [], [], [], [], []
    for k in range(int(t_end / dt) + 1):
        y = v + rng.gauss(0, sigma_v)
        # update
        K = P / (P + R)
        vh = vh + K * (y - vh)
        P = (1 - K) * P
        ts.append(k * dt)
        true.append(v)
        meas.append(y)
        est.append(vh)
        gains.append(K)
        # predict
        vh = a * vh + b * u
        P = a * P * a + Q
        v = a * v + b * u + rng.gauss(0, sigma_w)
    return ts, true, meas, est, gains


def check_19():
    l1, l2 = OBS_L
    assert 8 + l1 == 48 and 64 + 8 * l1 + l2 == 1152
    p1, _ = eig2(-l1, 1, -64 - l2, -8)
    assert close(p1.real, -24) and close(abs(p1.imag), 24)
    ts, xs = observer_run()
    late = [abs(s[1] - s[3]) for t, s in zip(ts, xs) if t >= 0.22]
    assert max(late) < 0.01, max(late)
    assert close(min(s[3] for s in xs), -0.472, 2e-3)
    assert -1 - 6 == -7 and 2 + 30 == 32 and 4 + 60 + 204 == 268


def check_20():
    assert 4 / 5 == 0.8 and close(20 + 0.8 * 2, 21.6) and close(0.2 * 4, 0.8)
    assert 3 / 4 == 0.75 and 50 + 0.75 * 2 == 51.5 and 0.25 * 3 == 0.75
    ts, true, meas, est, _ = kalman_car()
    err = max(abs(e - t) for tt, e, t in zip(ts, est, true) if tt >= 5)
    scatter = max(abs(m - t) for m, t in zip(meas, true))
    assert close(err, 0.220, 1e-2) and close(scatter, 2.01, 1e-2)
    assert close(true[0], 10) and close(true[-1], 14.6, 1e-2)
    late = [(e - t) ** 2 for tt, e, t in zip(ts, est, true) if tt >= 5]
    assert close(math.sqrt(sum(late) / len(late)), 0.117, 2e-2)


def fig_19():
    b = Blocks(620, 220, 'An observer: a model corrected by the innovation through the gain L')
    b.text(30, 45, 'u')
    b.wire([(40, 40), (250, 40)])
    b.dot(80, 40)
    b.box(310, 40, 120, 40, 'Plant')
    b.wire([(370, 40), (560, 40)])
    b.text(575, 45, 'y', anchor='start')
    b.wire([(80, 40), (80, 140), (250, 140)])
    b.box(310, 140, 120, 44, 'Model\n(A, B, C)', fill='#d1fae5')
    b.wire([(370, 140), (447, 140)], label='predicted y', dx=2, dy=17)
    b.dot(460, 40)
    b.wire([(460, 40), (460, 127)])
    b.sum(460, 140, signs={'n': '+', 'w': '−'})
    b.wire([(473, 140), (520, 140), (520, 200), (420, 200)], label='innovation', at=1, dx=8, dy=4, anchor='start')
    b.box(390, 200, 60, 30, 'L', fill='#fef3c7')
    b.wire([(360, 200), (330, 200), (330, 162)])
    b.text(240, 205, 'estimate x̂ inside the model', 12, 'middle', '#374151')
    b.save('ct-observer.svg')

    ts, xs = observer_run()
    p = Plot(540, 280, (0, 0.6), (-0.5, 0.3), 'An observer catching up with the true speed')
    p.axes([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [-0.4, -0.2, 0, 0.2], 'time (s)', 'speed (m/s)')
    p.hline(0, INK, None, 1)
    p.curve(ts, [s[1] for s in xs], BLUE, 2.6)
    p.curve(ts, [s[3] for s in xs], ORANGE, 2.2, '6,4')
    p.legend([('true speed', BLUE, None), ('observer estimate (starts at 0)', ORANGE, '6,4')], 300, 220)
    p.save('ct-observer-catchup.svg')


def fig_20():
    ts, true, meas, est, _ = kalman_car()
    p = Plot(560, 300, (0, 30), (7, 18), 'A Kalman filter estimating the car speed from noisy GPS')
    p.axes(range(0, 31, 5), range(8, 19, 2), 'time (s)', 'speed (m/s)')
    for t, m in zip(ts, meas):
        p.dot(t, m, GREY, 2.6)
    p.curve(ts, true, BLUE, 2.4)
    p.curve(ts, est, ORANGE, 2.2, '6,4')
    p.legend([('true speed', BLUE, None), ('Kalman estimate', ORANGE, '6,4')], 70, 40)
    p.s.circle(77, 75, 3, GREY)
    p.s.text(100, 79, 'GPS readings', 12, anchor='start')
    p.save('ct-kalman-car.svg')


# ---------- lessons 21-24: optimal control (Lewis problem sheets) ----------

def bilinear_211(x0=1.0):
    """Problem 2.1-1: both real roots of x0^4 l^4 - 2 x0^2 l^2 - l + 1 = 0 and their solutions."""
    f = lambda l: x0 ** 4 * l ** 4 - 2 * x0 ** 2 * l ** 2 - l + 1
    out = []
    for a, b in [(0.4, 0.6), (1.4, 1.6)]:
        l2 = bisect(f, a, b)
        x1 = 1 / (1 - l2 ** 2 * x0 ** 2)
        l1 = -l2 ** 2 * x1
        u0, u1 = -l1 * x0, -l2 * x1
        out.append((l2, x1, l1, u0, u1, 0.5 * (u0 ** 2 + u1 ** 2), x1 * u1 + 1))
    return out


def check_21():
    sols = bilinear_211()
    want = [(0.5249, 1.3803, -0.3803, 0.3803, -0.7245, 0.3347), (1.4902, -0.8192, 1.8192, -1.8192, 1.2207, 2.3998)]
    for s, w in zip(sols, want):
        assert all(abs(a - b) < 6e-5 for a, b in zip(s[:6], w)), (s, w)
        assert abs(s[6]) < 1e-9 and close(s[1], s[3] + 1)
    J = lambda u: 0.5 * (u * u + 1 / (u + 1) ** 2)
    best = min((J(i / 100000 - 0.99), i / 100000 - 0.99) for i in range(300000))
    assert close(best[1], 0.3803, 1e-3) and close(best[0], 0.3347, 1e-3)
    assert 3 * 2 * 1 == 6


def fig_21():
    J = lambda u: 0.5 * (u * u + 1 / (u + 1) ** 2)
    p = Plot(540, 300, (-3, 2), (0, 4), 'Cost of problem 2.1-1 against the first input')
    p.axes(range(-3, 3), range(0, 5), 'first input u0', 'cost J')
    for lo, hi in ((-3, -1.05), (-0.95, 2)):
        us = [lo + (hi - lo) * i / 400 for i in range(401)]
        p.curve(us, [J(u) for u in us], BLUE)
    p.vline(-1, GREY)
    p.label(-0.95, 3.75, 'u0 = −1: cost blows up', INK, 11)
    p.dot(0.3803, J(0.3803), ACCENT, 5)
    p.label(0.3, 0.75, 'optimum: u0 = 0.380, J = 0.335', ACCENT, 12, 'middle')
    p.dot(-1.8192, J(-1.8192), ORANGE, 5)
    p.label(-1.85, 1.8, 'other candidate: J = 2.40', ORANGE, 12, 'middle')
    p.save('ct-oc-bilinear-cost.svg')


def mmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def madd(a, b, s=1.0):
    return [[a[i][j] + s * b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def mT(a):
    return [list(r) for r in zip(*a)]


def minv2(a):
    d = det2(a)
    return [[a[1][1] / d, -a[0][1] / d], [-a[1][0] / d, a[0][0] / d]]


def min_energy_scalar(a=2.0, x0=3.0, N=5):
    G = sum((a * a) ** (N - 1 - i) for i in range(N))
    lamN = a ** N * x0 / G
    u = [-lamN * a ** (N - 1 - k) for k in range(N)]
    x = [x0]
    for k in range(N):
        x.append(a * x[-1] + u[k])
    return G, lamN, u, x


def riccati_scalar(a, b, q, r, SN, N):
    S = [0.0] * (N + 1)
    K = [0.0] * N
    S[N] = SN
    for k in range(N - 1, -1, -1):
        K[k] = b * S[k + 1] * a / (b * S[k + 1] * b + r)
        S[k] = a * (S[k + 1] - S[k + 1] * b * b * S[k + 1] / (b * S[k + 1] * b + r)) * a + q
    return S, K


P225_A = [[-0.5, 0.5], [3.0, -1.0]]
P225_B = [[2.0, 1.0], [2.0, 0.0]]
P225_R = [[2.0, 0.0], [0.0, 1.0]]
P225_X0 = [[8.0], [4.0]]


def p225a(x0=P225_X0):
    A, B, Ri = P225_A, P225_B, minv2(P225_R)
    BRB = mmul(mmul(B, Ri), mT(B))
    G = madd(mmul(mmul(A, BRB), mT(A)), BRB)
    lam2 = mmul(minv2(G), mmul(mmul(A, A), x0))
    u1 = [[-v] for v in mmul(mmul(Ri, mT(B)), lam2)[0]] if False else madd([[0], [0]], mmul(mmul(Ri, mT(B)), lam2), -1)
    lam1 = mmul(mT(A), lam2)
    u0 = madd([[0], [0]], mmul(mmul(Ri, mT(B)), lam1), -1)
    x1 = madd(mmul(A, x0), mmul(B, u0))
    x2 = madd(mmul(A, x1), mmul(B, u1))
    J = 0.5 * (mmul(mmul(mT(u0), P225_R), u0)[0][0] + mmul(mmul(mT(u1), P225_R), u1)[0][0])
    return u0, u1, x1, x2, J


def p225b():
    k2 = 3.25 / 4
    k1 = -0.75 - k2
    b = [[2.0], [2.0]]
    Ac = madd(P225_A, mmul(b, [[k1, k2]]), -1)
    return (k1, k2), Ac


def p225c(x0=P225_X0):
    A, B, R = P225_A, P225_B, P225_R
    S = [[20.0, 0.0], [0.0, 20.0]]
    Ks = []
    for _ in range(2):
        K = mmul(minv2(madd(mmul(mmul(mT(B), S), B), R)), mmul(mmul(mT(B), S), A))
        S = mmul(mT(A), mmul(S, madd(A, mmul(B, K), -1)))
        Ks.insert(0, K)
    u0 = madd([[0], [0]], mmul(Ks[0], x0), -1)
    x1 = madd(mmul(A, x0), mmul(B, u0))
    u1 = madd([[0], [0]], mmul(Ks[1], x1), -1)
    x2 = madd(mmul(A, x1), mmul(B, u1))
    J = 0.5 * mmul(mmul(mT(x0), S), x0)[0][0]
    return Ks, u0, u1, x1, x2, J


def p222():
    """Discrete Lyapunov equation P = A^T P A + C^T C, A = [[1/2,1],[0,-1/2]], C = [2 0], by fixed-point iteration."""
    A = [[0.5, 1.0], [0.0, -0.5]]
    Q = [[4.0, 0.0], [0.0, 0.0]]
    P = [[0.0, 0.0], [0.0, 0.0]]
    for _ in range(400):
        P = madd(mmul(mmul(mT(A), P), A), Q)
    return P


def p228a():
    # x_{k+1}=2x+u, J=5x5^2 + 1/2 sum (x^2+u^2+2xu): S_N=10, Q=1, R=1, cross N=1
    S = 10.0
    out = []
    for _ in range(5):
        K = (2 * S + 1) / (S + 1)
        S = 4 * S + 1 - (2 * S + 1) ** 2 / (S + 1)
        out.insert(0, (K, S))
    return out


def check_22():
    G, lam5, u, x = min_energy_scalar()
    assert G == 341 and close(lam5, 0.28152) and abs(x[-1]) < 1e-12
    assert [round(v, 3) for v in u] == [-4.504, -2.252, -1.126, -0.563, -0.282]
    assert [round(v, 3) for v in x[:5]] == [3, 1.496, 0.739, 0.352, 0.141]
    assert close(0.5 * sum(v * v for v in u), 13.513) and close(0.5 * 96 ** 2 / 341, 13.513)
    assert [3 * 2 ** k for k in range(6)] == [3, 6, 12, 24, 48, 96]
    assert 0.5 * 36 == 18
    G3, l3, u3, x3 = min_energy_scalar(x0=4.0, N=3)
    assert G3 == 21 and close(u3[0], -6.0952) and abs(x3[-1]) < 1e-12 and close(x3[1], 1.905, 1e-3)
    assert 5 * 8 == 40


def check_23():
    S, K = riccati_scalar(2, 1, 1, 1, 10, 5)
    assert [round(v, 3) for v in S] == [4.236, 4.237, 4.244, 4.29, 4.636, 10]
    assert [round(v, 3) for v in K] == [1.618, 1.619, 1.622, 1.645, 1.818]
    x = [3.0]
    for k in range(5):
        x.append((2 - K[k]) * x[-1])
    u = [-K[k] * x[k] for k in range(5)]
    assert [round(v, 3) for v in x] == [3, 1.146, 0.437, 0.165, 0.059, 0.011]
    assert [round(v, 3) for v in u] == [-4.854, -1.854, -0.709, -0.272, -0.107]
    direct = 5 * x[5] ** 2 + 0.5 * sum(x[k] ** 2 + u[k] ** 2 for k in range(5))
    assert close(direct, 0.5 * S[0] * 9) and close(direct, 19.063, 1e-4)
    assert close(2 + math.sqrt(5), 4.236, 1e-4) and close((1 + math.sqrt(5)) / 2, 1.618, 1e-4)
    assert close(2 / 3, 0.6667, 1e-3) and close(2 - 4 / 3 + 1, 1.6667, 1e-3)


def rl_c(target=2.0):
    return target / math.sinh(1)


def susp_test():
    """Problem 3.2-3 with m = k = 1, T = 2, h = -3: u = -(a cos t + b sin t). Returns a, b, x(T), J."""
    def run(a, b, n=20000):
        f = lambda t, x: [x[1], -x[0] - (a * math.cos(t) + b * math.sin(t))]
        ts, xs = rk4(f, [0.0, 0.0], 0, 2.0, n)
        return xs[-1]
    xa, xb = run(1, 0), run(0, 1)
    d = xa[0] * xb[1] - xb[0] * xa[1]
    a = (-3 * xb[1]) / d
    b = (xa[1] * 3) / d
    xT = run(a, b)
    n = 20000
    J = sum(0.5 * (a * math.cos((i + 0.5) * 2 / n) + b * math.sin((i + 0.5) * 2 / n)) ** 2 * 2 / n for i in range(n))
    return a, b, xT, J


def check_24():
    c = rl_c()
    assert close(c, 1.7018, 1e-4) and close(c * c * (math.e ** 2 - 1) / 2, 9.2521, 1e-4)
    assert close(c * math.e, 4.626, 1e-3)
    uc = 2 / (1 - math.exp(-1))
    assert close(uc, 3.164, 1e-3) and close(uc * uc, 10.011, 1e-3)
    ts, xs = rk4(lambda t, x: [-x[0] + c * math.exp(t)], [0.0], 0, 1, 2000)
    assert close(xs[-1][0], 2.0, 1e-6)
    a, b, xT, J = susp_test()
    assert close(a, 3.4387, 1e-3) and close(b, -0.1456, 1e-2) and close(xT[0], -3, 1e-6) and abs(xT[1]) < 1e-6
    assert close(J, 4.599, 1e-3)
    assert close(1 / math.sinh(1), 0.8509, 1e-3)


def check_bank():
    u0, u1, x1, x2, J = p225a()
    assert abs(x2[0][0]) < 1e-9 and abs(x2[1][0]) < 1e-9
    (k1, k2), Ac = p225b()
    assert close(k1, -1.5625) and close(k2, 0.8125)
    assert abs(Ac[0][0] + Ac[1][1]) < 1e-12 and abs(det2(Ac)) < 1e-12
    Ks, cu0, cu1, cx1, cx2, cJ = p225c()
    assert cJ > 0
    P = p222()
    A = [[0.5, 1.0], [0.0, -0.5]]
    R = madd(madd(mmul(mmul(mT(A), P), A), [[4.0, 0.0], [0.0, 0.0]]), P, -1)
    assert max(abs(v) for row in R for v in row) < 1e-9


def fig_22():
    G, lam5, u, x = min_energy_scalar()
    p = Plot(540, 300, (0, 5), (-2, 20), 'Driving x(k+1) = 2x(k) + u(k) from 3 to zero')
    p.axes(range(0, 6), range(0, 21, 5), 'step k', 'state x(k)')
    p.hline(0, INK, None, 1)
    ks = list(range(6))
    free = [3 * 2 ** k for k in ks]
    p.curve(ks, free, GREY, 2, '6,4')
    for k in range(5):
        p.dot(k, free[k], GREY, 4)
    p.label(4.1, 18.5, 'no input: 3, 6, 12, 24, 48, 96', GREY, 12, 'end')
    p.curve(ks, x, BLUE)
    for k in ks:
        p.dot(k, x[k], BLUE, 4)
    dead = [3, 0, 0, 0, 0, 0]
    p.curve(ks, dead, TRUE, 2)
    for k in ks:
        p.dot(k, dead[k], TRUE, 3)
    p.label(1.1, 5.5, 'minimum energy: J = 13.5', BLUE, 12)
    p.label(0.15, -1.2, 'deadbeat: J = 18', TRUE, 12)
    p.save('ct-oc-min-energy.svg')


def fig_23():
    S, K = riccati_scalar(2, 1, 1, 1, 10, 5)
    x = [3.0]
    for k in range(5):
        x.append((2 - K[k]) * x[-1])
    p = Plot(540, 300, (0, 5), (0, 11), 'Riccati sweep and the controlled state')
    p.axes(range(0, 6), range(0, 12, 2), 'step k', 'value')
    ks = list(range(6))
    p.curve(ks, S, ORANGE)
    for k in ks:
        p.dot(k, S[k], ORANGE, 4)
    p.curve(ks, x, BLUE)
    for k in ks:
        p.dot(k, x[k], BLUE, 4)
    p.label(4.9, 9.4, 'S(k): runs backwards from 10', ORANGE, 12, 'end')
    p.label(0.15, 5.2, 'S settles at 4.236', ORANGE, 12)
    p.label(0.5, 2.6, 'x(k): 3, 1.15, 0.44, 0.17 ...', BLUE, 12)
    p.save('ct-oc-riccati.svg')


def fig_24():
    c = rl_c()
    uc = 2 / (1 - math.exp(-1))
    ts = [i / 200 for i in range(201)]
    p = Plot(540, 300, (0, 1), (0, 5), 'Charging an inductor with minimum energy')
    p.axes([0, 0.2, 0.4, 0.6, 0.8, 1], range(0, 6), 'time (s)', 'volts / amps')
    p.curve(ts, [c * math.exp(t) for t in ts], ORANGE)
    p.curve(ts, [c * math.sinh(t) for t in ts], BLUE)
    p.curve(ts, [uc for t in ts], GREY, 1.8, '6,4')
    p.curve(ts, [uc * (1 - math.exp(-t)) for t in ts], GREY, 1.4, '2,3')
    p.legend([('optimal voltage 1.702 e^t (J = 9.25)', ORANGE, None), ('current 1.702 sinh t', BLUE, None),
              ('constant 3.16 V (J = 10.01)', GREY, '6,4')], 70, 34)
    p.save('ct-oc-rl.svg')


# ---------- lessons 25-26: LQR ----------

def lqr_scalar(a, b, q, r):
    """Positive root of 2aP - P^2 b^2 / r + q = 0, and K = bP/r."""
    c = b * b / r
    P = (2 * a + math.sqrt(4 * a * a + 4 * c * q)) / (2 * c)
    return P, b * P / r


def check_25():
    P, K = lqr_scalar(-0.05, 0.001, 1.0, 1e-6)
    assert close(P, 0.9512, 1e-3) and close(K, 951.2, 1e-3) and close(-0.05 - 0.001 * K, -1.0012, 1e-3)
    assert close(1 / 50 ** 2, 0.0004)
    P2, K2 = lqr_scalar(0, 1, 2, 1)
    assert close(K2, math.sqrt(2))
    P3, K3 = lqr_scalar(1, 1, 4, 1)
    assert close(P3, 1 + math.sqrt(5)) and close(1 - K3, -2.236, 1e-3)


# ---------- lessons 27-28: digital control ----------

def check_27():
    assert close(0.446 * 0.25, 0.1115, 2e-3) and close(math.degrees(0.4457 * 0.25), 6.38, 2e-3)
    assert close(math.degrees(0.4457 * 1.0), 25.5, 3e-3)
    assert 1000 - 990 == 10 and 500 - 460 == 40
    assert close(math.degrees(2 * 0.1 / 2), 5.7296, 1e-4)
    assert close(math.exp(-0.005), 0.995, 1e-3) and close(math.exp(-0.2), 0.8187, 1e-4)
    ts, vs, _ = pid_car(500, 100)
    t10 = next(t for t, v in zip(ts, vs) if v >= 2)
    t90 = next(t for t, v in zip(ts, vs) if v >= 18)
    assert 6.5 < t90 - t10 < 7.5


def check_28():
    s, T = -30, 0.1
    assert close(1 + s * T, -2) and close(1 / (1 - s * T), 0.25) and close((1 + s * T / 2) / (1 - s * T / 2), -0.2)
    assert close(math.exp(-3), 0.0498, 1e-3)
    assert 500 + 100 * 0.1 / 2 == 505 and -500 + 100 * 0.1 / 2 == -495
    s = -15
    assert close(1 + s * T, -0.5) and close((1 + s * T / 2) / (1 - s * T / 2), 0.1429, 1e-3)
    assert 200 + 40 * 0.1 / 2 == 202 and 200 - 40 * 0.1 / 2 == 198
    # Tustin PI difference equation matches C(s) at low frequency: check DC behaviour as integrator
    u, e_prev = 0.0, 0.0
    for k in range(10):
        e = 1.0
        u = u + 505 * e - 495 * e_prev
        e_prev = e
    assert close(u, 500 + 100 * 0.1 * 9.5)          # Kp*e + Ki * integral (trapezoid)


def fig_27():
    b = Blocks(700, 190, 'A digital loop: sampler, computer, hold, plant')
    y = 70
    b.text(30, y + 5, 'r')
    b.wire([(40, y), (77, y)])
    b.sum(90, y, signs={'w': '+', 's': '−'})
    b.wire([(103, y), (140, y)])
    b.box(200, y, 110, 44, 'Controller\n(code)', fill='#e5e7eb')
    b.wire([(255, y), (300, y)])
    b.box(345, y, 80, 40, 'ZOH / DAC')
    b.wire([(385, y), (470, y)])
    # staircase sketch
    xs0, ys0 = 400, y - 28
    d = f'M{xs0},{ys0 + 14}'
    lv = [14, 6, 10, 2, 8]
    for i, l in enumerate(lv):
        d += f' L{xs0 + 12 * i},{ys0 + l} L{xs0 + 12 * (i + 1)},{ys0 + l}'
    b.s.path(d, ORANGE, 1.6)
    b.box(520, y, 90, 40, 'Plant')
    b.wire([(565, y), (660, y)])
    b.text(668, y + 5, 'y', anchor='start')
    b.dot(620, y)
    b.wire([(620, y), (620, 150), (390, 150)])
    b.box(345, 150, 90, 36, 'ADC', fill='#d1fae5')
    b.wire([(300, 150), (90, 150), (90, y + 13)], label='samples every T')
    b.save('ct-digital-loop.svg')

    p = Plot(560, 260, (0, 0.1), (-1.3, 1.3), 'A 990 Hz wave sampled at 1000 Hz looks like 10 Hz')
    p.axes([0, 0.02, 0.04, 0.06, 0.08, 0.1], [-1, 0, 1], 'time (s)', 'signal')
    ts = [i / 60000 for i in range(6001)]
    p.curve(ts, [math.sin(2 * math.pi * 990 * t) for t in ts], GREY, 0.6, maxpts=10000)
    ks = [k / 1000 for k in range(101)]
    samples = [math.sin(2 * math.pi * 990 * t) for t in ks]
    for t, v in zip(ks, samples):
        assert abs(v + math.sin(2 * math.pi * 10 * t)) < 1e-9       # the samples are exactly a 10 Hz wave
        p.dot(t, v, BLUE, 3)
    p.curve(ks, samples, BLUE, 2)
    p.save('ct-aliasing.svg')

    s = Svg(640, 300, 'The s-plane left half maps to the inside of the unit circle in the z-plane')
    left = Plot(640, 300, (-2.2, 1.0), (-1.5, 1.5), '', ml=20, mr=340, mb=30)
    right = Plot(640, 300, (-1.5, 1.5), (-1.5, 1.5), '', ml=340, mr=20, mb=30)
    left.s = right.s = s
    s.rect(left.X(-2.2), left.Y(1.5), left.X(0) - left.X(-2.2), left.Y(-1.5) - left.Y(1.5), '#d1fae5', opacity=0.6)
    s.add(f'<circle cx="{right.X(0):.1f}" cy="{right.Y(0):.1f}" r="{right.X(1) - right.X(0):.1f}" '
          f'fill="#d1fae5" fill-opacity="0.6" stroke="{BLUE}" stroke-width="2"/>')
    left.axes(cross=True, grid=False)
    right.axes(cross=True, grid=False)
    left.s.line(left.X(0), left.Y(-1.5), left.X(0), left.Y(1.5), BLUE, 2)
    left.label(-2.1, 1.25, 's-plane', INK, 13, weight='bold')
    right.label(-1.4, 1.25, 'z-plane: z = e^(sT)', INK, 13, weight='bold')
    left.label(-1.9, -1.25, 'stable: left half', ACCENT, 12)
    right.label(-1.4, -1.3, 'stable: inside |z| = 1', ACCENT, 12)
    left.dot(0, 0, TRUE)
    left.label(0.06, 0.12, 's = 0', TRUE, 11)
    right.dot(1, 0, TRUE)
    right.label(1.03, 0.12, 'z = 1', TRUE, 11)
    left.cross(-0.05 * 10, 0, ORANGE, 5)
    left.label(-0.5, -0.3, 'car pole (scaled)', ORANGE, 11, 'middle')
    right.cross(math.exp(-0.005), 0, ORANGE, 5)
    right.label(0.6, -0.3, '0.995', ORANGE, 11)
    s.save('ct-s-to-z.svg', OUT)


# ---------- lessons 30-34: phase plane and limit cycles ----------

def traj(f, x0, t1, n=4000):
    return rk4(lambda t, x: f(x), x0, 0, t1, n)


def field_arrows(p, f, xs, ys, color=GREY, scale=0.18, norm=True):
    for x in xs:
        for y in ys:
            v = f([x, y])
            m = math.hypot(*v) or 1
            dx, dy = (v[0] / m * scale, v[1] / m * scale) if norm else (v[0] * scale, v[1] * scale)
            # convert so arrows have equal pixel length: scale in each axis by its range
            sx = (p.x1 - p.x0) / (p.w - p.ml - p.mr)
            sy = (p.y1 - p.y0) / (p.h - p.mt - p.mb)
            pv = (v[0] / sx, v[1] / sy)
            pm = math.hypot(*pv) or 1
            L = 11
            ddx, ddy = pv[0] / pm * L * sx, pv[1] / pm * L * sy
            p.s.line(p.X(x - ddx), p.Y(y - ddy), p.X(x + ddx), p.Y(y + ddy), color, 1.1)
            p.arrow(x + ddx, y + ddy, ddx, ddy, color, 5)


def pend(g=10.0, d=0.0):
    return lambda x: [x[1], -d * x[1] - g * math.sin(x[0])]


def check_30():
    assert [2 * 1 ** 2, 1] == [2, 1] and (1 + 2, 1 + 1) == (3, 2)
    ts, xs = traj(pend(1.0), [math.pi / 2, 0.0], 8, 4000)
    assert close(max(abs(x[1]) for x in xs), math.sqrt(2), 1e-3)
    ts, xs = traj(pend(1.0, 0.5), [math.pi / 2, 0.0], 30, 6000)
    assert math.hypot(*xs[-1]) < 0.01
    assert (3 * 1 * 2, 1 + 2) == (6, 3) and close((1 - 2) / (3 * 1 * -2), 1 / 6)


def fig_30():
    f = pend(10.0)
    p = Plot(600, 380, (-2 * math.pi, 2 * math.pi), (-9, 9), 'Vector field of the frictionless pendulum')
    p.axes([-2 * math.pi, -math.pi, 0, math.pi, 2 * math.pi], [-8, -4, 0, 4, 8], 'angle x1 (rad)', 'speed x2 (rad/s)',
           xfmt=lambda v: {0: '0'}.get(round(v / math.pi), f'{round(v / math.pi)}π'.replace('1π', 'π')))
    xs = [-2 * math.pi + i * (4 * math.pi / 16) for i in range(17)]
    ys = [-8 + 2 * j for j in range(9)]
    field_arrows(p, f, xs, ys)
    for a in (0.8, 1.8, 2.8):
        for c in (0, 2 * math.pi, -2 * math.pi):
            ts, tr = traj(f, [c + a, 0.0], 7, 6000)
            p.curve([x[0] for x in tr], [x[1] for x in tr], BLUE, 1.8)
    for start in ([-2 * math.pi, 7.5], [2 * math.pi, -7.5]):
        ts, tr = traj(f, start, 3, 3000)
        p.curve([x[0] for x in tr], [x[1] for x in tr], ORANGE, 1.8)
    for c in (-2 * math.pi, 0, 2 * math.pi):
        p.dot(c, 0, ACCENT, 4)
    for c in (-math.pi, math.pi):
        p.dot(c, 0, TRUE, 4)
    p.save('ct-pp-vector-field.svg')

    f1 = pend(1.0)
    p = Plot(560, 360, (-math.pi, math.pi), (-2, 2), 'Isoclines of the frictionless pendulum')
    p.axes([-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi], [-2, -1, 0, 1, 2], 'angle x1 (rad)', 'speed x2 (rad/s)',
           xfmt=lambda v: {-4: '−π', -2: '−π/2', 0: '0', 2: 'π/2', 4: 'π'}[round(v / (math.pi / 4))])
    xs1 = [-math.pi + i * 2 * math.pi / 200 for i in range(201)]
    for c in (-2, -1, -0.5, 0.5, 1, 2):
        ys1 = [-math.sin(x) / c for x in xs1]
        p.curve(xs1, ys1, GREY, 1.1, '4,3')
        for k in range(1, 12):
            x = -math.pi + k * 2 * math.pi / 12
            y = -math.sin(x) / c
            if abs(y) > 1.95:
                continue
            sx = (p.x1 - p.x0) / (p.w - p.ml - p.mr)
            sy = (p.y1 - p.y0) / (p.h - p.mt - p.mb)
            pv = (1 / sx, c / sy)
            pm = math.hypot(*pv)
            L = 6
            dx, dy = pv[0] / pm * L * sx, pv[1] / pm * L * sy
            p.s.line(p.X(x - dx), p.Y(y - dy), p.X(x + dx), p.Y(y + dy), INK, 1.6)
    ts, tr = traj(f1, [math.pi / 2, 0.0], 7.5, 3000)
    p.curve([x[0] for x in tr], [x[1] for x in tr], BLUE, 2.4)
    p.dot(math.pi / 2, 0, ORANGE, 5)
    p.label(math.pi / 2 + 0.08, 0.12, 'start (π/2, 0)', ORANGE, 12)
    p.save('ct-pp-isoclines.svg')

    f2 = pend(1.0, 0.5)
    ts, tr = traj(f2, [math.pi / 2, 0.0], 30, 6000)
    p = Plot(520, 340, (-1.2, 1.8), (-1.2, 0.8), 'The pendulum with friction spirals into rest')
    p.axes([-1, -0.5, 0, 0.5, 1, 1.5], [-1, -0.5, 0, 0.5], 'angle x1 (rad)', 'speed x2 (rad/s)')
    p.hline(0, INK, None, 1)
    p.vline(0, INK, None, 1)
    p.curve([x[0] for x in tr], [x[1] for x in tr], BLUE, 2.2)
    for i in (150, 700, 1400):
        a, b = tr[i], tr[i + 4]
        p.arrow(a[0], a[1], b[0] - a[0], b[1] - a[1], BLUE, 9)
    p.dot(math.pi / 2, 0, ORANGE, 5)
    p.label(math.pi / 2, 0.12, 'start (π/2, 0)', ORANGE, 12, 'middle')
    p.save('ct-pp-friction.svg')


def mini_portrait(svg, ox, oy, size, A, title, starts, t1=6.0, R=1.0, reverse=False):
    p = Plot(int(size), int(size), (-R, R), (-R, R), '', ml=6, mr=6, mt=24, mb=6)
    p.s = svg
    p.X = (lambda X0: (lambda x: X0(x) + ox))(p.X)
    p.Y = (lambda Y0: (lambda y: Y0(y) + oy))(p.Y)
    svg.rect(ox + 6, oy + 24, size - 12, size - 30, 'none', GRID, 1)
    svg.line(p.X(-R), p.Y(0), p.X(R), p.Y(0), GRID, 1)
    svg.line(p.X(0), p.Y(-R), p.X(0), p.Y(R), GRID, 1)
    a, b, c, d = A
    sg = 1
    f = lambda t, x: [sg * (a * x[0] + b * x[1]), sg * (c * x[0] + d * x[1])]
    for s0 in starts:
        ts, xs = rk4(f, s0, 0, t1, 600)
        cut = []
        for x in xs:
            if abs(x[0]) > R * 1.05 or abs(x[1]) > R * 1.05:
                if cut:
                    break
                continue
            cut.append(x)
        if len(cut) < 3:
            continue
        if reverse:
            cut = cut[::-1]
        p.curve([x[0] for x in cut], [x[1] for x in cut], BLUE, 1.4, maxpts=120)
        i = len(cut) // 3
        q0, q1 = cut[i], cut[min(i + 3, len(cut) - 1)]
        if math.hypot(q1[0] - q0[0], q1[1] - q0[1]) > 1e-4:
            p.arrow(q0[0], q0[1], q1[0] - q0[0], q1[1] - q0[1], BLUE, 6)
    svg.circle(p.X(0), p.Y(0), 3, TRUE)
    svg.text(ox + size / 2, oy + 17, title, 13, INK, 'middle', 'bold')


def ring(n, r=1.0):
    return [[r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)] for k in range(n)]


def edge_points(n, R=1.0):
    pts = []
    for k in range(n):
        u = -R + 2 * R * (k + 0.5) / n
        pts += [[u, R], [u, -R], [R, u], [-R, u]]
    return pts


def check_31():
    assert sorted(z.real for z in eig2(1, 2, 3, 0)) == [-2, 3]
    l = eig2(-1, 2, -2, -1)
    assert close(l[0].real, -1) and close(abs(l[0].imag), 2)
    l = eig2(0, 1, -4, 0)
    assert abs(l[0].real) < 1e-12 and close(abs(l[0].imag), 2)


def fig_31():
    S = 200
    svg = Svg(3 * S, 2 * S, 'The six types of equilibrium of a linear two-state system')
    mini_portrait(svg, 0, 0, S, (-1, 0, 0, -3), 'stable node', edge_points(4), 8)
    mini_portrait(svg, S, 0, S, (-1, 0, 0, -3), 'unstable node', edge_points(4), 8, reverse=True)
    mini_portrait(svg, 2 * S, 0, S, (1, 0, 0, -1), 'saddle', edge_points(4) + [[0.01, 0.0], [-0.01, 0.0], [0, 1.0], [0, -1.0]], 8)
    mini_portrait(svg, 0, S, S, (-0.3, -1, 1, -0.3), 'stable focus', [[0.95, 0.0], [-0.95, 0.0]], 20)
    mini_portrait(svg, S, S, S, (0.2, -1, 1, 0.2), 'unstable focus', [[0.02, 0.0]], 25)
    mini_portrait(svg, 2 * S, S, S, (0, 1, -1, 0), 'centre', [[r, 0.0] for r in (0.25, 0.5, 0.75, 0.95)], 6.4)
    svg.save('ct-pp-six-types.svg', OUT)


TD_H = lambda x: 17.76 * x - 103.79 * x ** 2 + 229.62 * x ** 3 - 226.31 * x ** 4 + 83.72 * x ** 5
TD_HP = lambda x: 17.76 - 207.58 * x + 688.86 * x ** 2 - 905.24 * x ** 3 + 418.6 * x ** 4


def td_f(x):
    return [0.5 * (-TD_H(x[0]) + x[1]), 0.2 * (-x[0] - 1.5 * x[1] + 1.2)]


def td_equilibria():
    g = lambda x: TD_H(x) - (1.2 - x) / 1.5
    out = []
    xs = [i / 1000 for i in range(-200, 1600)]
    for a, b in zip(xs, xs[1:]):
        if g(a) * g(b) < 0:
            r = bisect(g, a, b)
            out.append((r, (1.2 - r) / 1.5))
    return out


def check_32():
    eq = td_equilibria()
    assert [(round(a, 3), round(b, 3)) for a, b in eq] == [(0.063, 0.758), (0.285, 0.61), (0.884, 0.21)]
    types = []
    for (x1, x2) in eq:
        a11 = -0.5 * TD_HP(x1)
        l1, l2 = eig2(a11, 0.5, -0.2, -0.3)
        types.append((round(a11, 2), sorted([round(l1.real, 2), round(l2.real, 2)])))
    assert types == [(-3.62, [-3.59, -0.33]), (1.82, [-0.25, 1.77]), (-1.44, [-1.34, -0.4])], types
    l = eig2(0, 1, -10, -0.5)
    assert close(l[0].real, -0.25) and close(abs(l[0].imag), 3.152, 1e-3)
    l = eig2(0, 1, 10, -0.5)
    assert sorted(round(z.real, 2) for z in l) == [-3.42, 2.92]
    assert sorted(z.real for z in eig2(0, 1, 1, 0)) == [-1, 1]
    l = eig2(0, 1, -2, 0)
    assert abs(l[0].real) < 1e-12 and close(abs(l[0].imag), math.sqrt(2))


def fig_32():
    p = Plot(520, 460, (-0.4, 1.6), (-0.4, 1.6), 'Phase portrait of the tunnel-diode circuit')
    p.axes([-0.4, 0, 0.4, 0.8, 1.2, 1.6], [-0.4, 0, 0.4, 0.8, 1.2, 1.6], 'voltage x1', 'current x2')
    starts = []
    for k in range(9):
        u = -0.4 + 2.0 * k / 8
        starts += [[u, 1.6], [u, -0.4], [-0.4, u], [1.6, u]]
    for s0 in starts:
        ts, xs = rk4(lambda t, x: td_f(x), s0, 0, 60, 3000)
        cut = [x for x in xs if -0.42 <= x[0] <= 1.62 and -0.42 <= x[1] <= 1.62]
        p.curve([x[0] for x in cut], [x[1] for x in cut], BLUE, 1.3, maxpts=150)
        if len(cut) > 20:
            q0, q1 = cut[8], cut[12]
            p.arrow(q0[0], q0[1], q1[0] - q0[0], q1[1] - q0[1], BLUE, 6)
    # separatrix: integrate backwards from near Q2 along the stable eigenvector
    eq = td_equilibria()
    x1, x2 = eq[1]
    a11 = -0.5 * TD_HP(x1)
    lam = min(z.real for z in eig2(a11, 0.5, -0.2, -0.3))
    v = (0.5, lam - a11)                      # eigenvector of [[a11, .5], [-.2, -.3]] for lam
    n = math.hypot(*v)
    for sg in (1, -1):
        s0 = [x1 + sg * 1e-3 * v[0] / n, x2 + sg * 1e-3 * v[1] / n]
        cut = rk4_box(lambda x: [-c for c in td_f(x)], s0, 0.01, 8000, (-0.42, 1.62, -0.42, 1.62))
        p.curve([x[0] for x in cut], [x[1] for x in cut], ORANGE, 2.6)
    xs_h = [i / 500 for i in range(-200, 800)]
    for (a, b), name, col in zip(eq, ('Q1', 'Q2', 'Q3'), (ACCENT, TRUE, ACCENT)):
        p.dot(a, b, col, 6)
        p.label(a + 0.04, b + 0.05, name, col, 13, weight='bold')
    p.label(1.55, 1.45, 'orange: separatrix', ORANGE, 12, 'end')
    p.save('ct-pp-tunnel-diode.svg')


def polar_sys(g):
    def f(x):
        r = math.hypot(x[0], x[1]) or 1e-12
        k = g(r) / r
        return [k * x[0] + x[1], k * x[1] - x[0]]
    return f


def lc_panel(svg, ox, title, g, starts, t1):
    S = 220
    R = 1.8
    p = Plot(S, S + 10, (-R, R), (-R, R), '', ml=8, mr=8, mt=28, mb=8)
    p.s = svg
    p.X = (lambda X0: (lambda x: X0(x) + ox))(p.X)
    svg.rect(ox + 8, 28, S - 16, S - 26, 'none', GRID, 1)
    th = [2 * math.pi * i / 120 for i in range(121)]
    p.curve([math.cos(t) for t in th], [math.sin(t) for t in th], ORANGE, 2.6)
    f = polar_sys(g)
    for s0 in starts:
        xs = rk4_box(f, s0, 0.01, int(t1 / 0.01), (-R * 1.02, R * 1.02, -R * 1.02, R * 1.02))
        p.curve([x[0] for x in xs], [x[1] for x in xs], BLUE, 1.3, maxpts=200)
        q0, q1 = xs[min(60, len(xs) - 2)], xs[min(63, len(xs) - 1)]
        p.arrow(q0[0], q0[1], q1[0] - q0[0], q1[1] - q0[1], BLUE, 6)
    svg.circle(p.X(0), p.Y(0), 3, INK)
    svg.text(ox + S / 2, 20, title, 13, INK, 'middle', 'bold')


def check_33():
    f = polar_sys(lambda r: -r * (r * r - 1))
    assert all(close(a, b) for a, b in zip(f([0.6, 0.3]), [0.3 - 0.6 * (0.45 - 1), -0.6 - 0.3 * (0.45 - 1)]))
    for r, s in ((0.5, 1), (1.5, -1), (2.5, 1)):
        assert (r * (r - 1) * (r - 2) > 0) == (s > 0)
    assert close(2 * math.pi / 3, 2.0944, 1e-4)
    xs = rk4_box(f, [0.2, 0.0], 0.01, 3000, (-5, 5, -5, 5))
    assert close(math.hypot(*xs[-1]), 1.0, 1e-4)
    xs = rk4_box(f, [1.7, 0.0], 0.01, 3000, (-5, 5, -5, 5))
    assert close(math.hypot(*xs[-1]), 1.0, 1e-4)


def fig_33():
    svg = Svg(660, 240, 'Stable, unstable and semi-stable limit cycles on the unit circle')
    lc_panel(svg, 0, 'stable', lambda r: -r * (r * r - 1), [[0.15, 0], [-0.15, 0], [1.75, 0], [-1.75, 0]], 12)
    lc_panel(svg, 220, 'unstable', lambda r: r * (r * r - 1),
             [[0.9, 0], [-0.9, 0], [1.08, 0], [-1.08, 0]], 12)
    lc_panel(svg, 440, 'semi-stable', lambda r: -r * (r * r - 1) ** 2,
             [[0.85, 0], [-0.85, 0], [1.75, 0], [-1.75, 0]], 40)
    svg.save('ct-lc-three-types.svg', OUT)


def pb_f(x):
    r2 = x[0] ** 2 + x[1] ** 2
    return [x[0] + x[1] - x[0] * r2, -2 * x[0] + x[1] - x[1] * r2]


def check_34():
    l = eig2(1, 1, -2, 1)
    assert close(l[0].real, 1) and close(abs(l[0].imag), math.sqrt(2))
    for c in (1.5, 2.0, 3.0):
        worst = max(2 * x * pb_f([x, y])[0] + 2 * y * pb_f([x, y])[1]
                    for th in [i * 2 * math.pi / 720 for i in range(720)]
                    for x, y in [(math.sqrt(c) * math.cos(th), math.sqrt(c) * math.sin(th))])
        assert worst <= 3 * c - 2 * c * c + 1e-9 and worst <= 1e-9
    assert eig2(2, 5, -1, -2)[0].real == 0 and 2 - 1 == 1


def fig_34():
    p = Plot(460, 440, (-1.6, 1.6), (-1.6, 1.6), 'A Poincare-Bendixson trapping region', ml=40, mb=36)
    p.axes([-1.5, -1, -0.5, 0, 0.5, 1, 1.5], [-1.5, -1, -0.5, 0, 0.5, 1, 1.5], 'x1', 'x2')
    th = [2 * math.pi * i / 200 for i in range(201)]
    R = math.sqrt(1.5)
    p.curve([R * math.cos(t) for t in th], [R * math.sin(t) for t in th], ORANGE, 2, '7,5')
    for s0, col in (([0.05, 0.0], BLUE), ([R * 0.999, 0.0], PURPLE), ([-R * 0.7, R * 0.7], PURPLE)):
        xs = rk4_box(pb_f, s0, 0.005, 6000, (-2, 2, -2, 2))
        p.curve([x[0] for x in xs], [x[1] for x in xs], col, 1.6, maxpts=600)
        q0, q1 = xs[300], xs[306]
        p.arrow(q0[0], q0[1], q1[0] - q0[0], q1[1] - q0[1], col, 8)
    xs = rk4_box(pb_f, [0.05, 0.0], 0.005, 20000, (-2, 2, -2, 2))
    tail = xs[-3000:]
    p.curve([x[0] for x in tail], [x[1] for x in tail], INK, 2.6, maxpts=600)
    p.dot(0, 0, TRUE, 4)
    p.label(0.05, -0.15, 'unstable focus', TRUE, 11)
    p.label(0.75, 1.42, 'x1² + x2² = 1.5', ORANGE, 12)
    p.save('ct-lc-poincare-bendixson.svg')


# ---------- lessons 35-38: Lyapunov stability ----------

def attract_f(x):
    r = math.hypot(*x) or 1e-12
    th = math.atan2(x[1], x[0])
    rd, td = r * (1 - r), math.sin(th / 2) ** 2
    return [rd * math.cos(th) - r * math.sin(th) * td, rd * math.sin(th) + r * math.cos(th) * td]


def check_35():
    xs = rk4_box(attract_f, [1.0, 0.02], 0.01, 60000, (-3, 3, -3, 3))
    far = max(math.hypot(x[0] - 1, x[1]) for x in xs)
    assert close(far, 2.0, 1e-3)
    assert math.hypot(xs[-1][0] - 1, xs[-1][1]) < 0.05


def fig_35():
    p = Plot(440, 360, (-1.5, 1.5), (-1.2, 1.2), 'Stable in the sense of Lyapunov', ml=20, mb=20)
    p.axes(cross=True, grid=False)
    th = [2 * math.pi * i / 200 for i in range(201)]
    for r, c, lab in ((1.0, ORANGE, 'ε'), (0.35, ACCENT, 'δ')):
        p.curve([r * math.cos(t) for t in th], [r * math.sin(t) for t in th], c, 2, '6,4')
        p.label(r * 0.72 + 0.03, r * 0.72 + 0.03, lab, c, 15, weight='bold')
    f = lambda x: [-0.25 * x[0] - 2 * x[1], 2 * x[0] - 0.25 * x[1]]
    xs = rk4_box(f, [0.3, 0.1], 0.005, 4000, (-2, 2, -2, 2))
    p.curve([x[0] for x in xs], [x[1] for x in xs], BLUE, 1.8, maxpts=600)
    p.dot(0.3, 0.1, BLUE, 4)
    p.dot(0, 0, TRUE, 4)
    p.label(-1.45, -1.05, 'start inside δ, stay inside ε', INK, 12)
    p.save('ct-lyap-eps-delta.svg')

    p = Plot(440, 420, (-1.6, 1.6), (-1.6, 1.6), 'Attracting but not stable', ml=40, mb=36)
    p.axes([-1.5, -1, -0.5, 0, 0.5, 1, 1.5], [-1.5, -1, -0.5, 0, 0.5, 1, 1.5], 'x1', 'x2')
    p.curve([math.cos(t) for t in th], [math.sin(t) for t in th], GRID, 1.5)
    for s0 in ([0.2, 0.3], [-0.3, -0.2], [1.5, 1.2], [-1.4, 0.6], [0.4, -1.5]):
        xs = rk4_box(attract_f, s0, 0.01, 40000, (-2, 2, -2, 2))
        p.curve([x[0] for x in xs], [x[1] for x in xs], BLUE, 1.3, maxpts=500)
    xs = rk4_box(attract_f, [1.0, 0.02], 0.01, 60000, (-3, 3, -3, 3))
    p.curve([x[0] for x in xs], [x[1] for x in xs], ORANGE, 2.6, maxpts=800)
    p.dot(1, 0, TRUE, 5)
    p.label(1.05, -0.18, '(1, 0)', TRUE, 12)
    p.label(-1.55, 1.42, 'orange: start at angle 0.02', ORANGE, 12)
    p.save('ct-lyap-attractive-unstable.svg')


def level_set_plot(name, title, f, Vfun, levels, starts, R=2.0, t1=20):
    p = Plot(440, 420, (-R, R), (-R, R), title, ml=40, mb=36)
    tk = [-R, -R / 2, 0, R / 2, R]
    p.axes(tk, tk, 'x1', 'x2')
    for c in levels:
        # trace level set by radial search for V = c in each direction
        pts = []
        for i in range(181):
            th = 2 * math.pi * i / 180
            lo, hi = 0.0, 3 * R
            for _ in range(50):
                m = (lo + hi) / 2
                if Vfun([m * math.cos(th), m * math.sin(th)]) < c:
                    lo = m
                else:
                    hi = m
            pts.append((lo * math.cos(th), lo * math.sin(th)))
        p.curve([q[0] for q in pts], [q[1] for q in pts], ORANGE, 1.3, '5,4')
    for s0 in starts:
        xs = rk4_box(f, s0, 0.005, int(t1 / 0.005), (-R * 1.5, R * 1.5, -R * 1.5, R * 1.5))
        p.curve([x[0] for x in xs], [x[1] for x in xs], BLUE, 1.8)
        q0, q1 = xs[40], xs[46]
        p.arrow(q0[0], q0[1], q1[0] - q0[0], q1[1] - q0[1], BLUE, 8)
    p.dot(0, 0, TRUE, 4)
    p.save(name)


def check_36():
    f = lambda x: [-x[0] + x[1], -x[0] - x[1]]
    x = [1.0, 1.0]
    assert 2 * x[0] * f(x)[0] + 2 * x[1] * f(x)[1] == -4
    import random
    rng = random.Random(3)
    for _ in range(200):
        x = [rng.uniform(-2, 2), rng.uniform(-2, 2)]
        g = lambda x: [x[1], -x[0] - x[1] ** 3]
        assert close(2 * x[0] * g(x)[0] + 2 * x[1] * g(x)[1], -2 * x[1] ** 4, 1e-9)
        pe = lambda x: [x[1], -10 * math.sin(x[0])]
        M, R_, gg = 1.0, 0.1, 1.0      # g/R = 10
        dV = M * gg * R_ * math.sin(x[0]) * pe(x)[0] + M * R_ ** 2 * x[1] * pe(x)[1]
        assert abs(dV) < 1e-12


def check_37():
    import random
    rng = random.Random(5)
    for _ in range(300):
        x = [rng.uniform(-2, 2) for _ in range(3)]
        f = [-x[0] + 4 * x[1], -x[0] - x[1] ** 3]
        assert close(2 * x[0] * f[0] + 8 * x[1] * f[1], -2 * x[0] ** 2 - 8 * x[1] ** 4, 1e-9)
        s, r, b = 2.0, 0.5, 3.0
        g = [s * (x[1] - x[0]), r * x[0] - x[1] - x[0] * x[2], x[0] * x[1] - b * x[2]]
        lhs = 2 * x[0] / s * g[0] + 2 * x[1] * g[1] + 2 * x[2] * g[2]
        k = (1 + r) / 2
        rhs = -2 * ((x[0] - k * x[1]) ** 2 + (1 - k * k) * x[1] ** 2 + b * x[2] ** 2)
        assert close(lhs, rhs, 1e-9)
        h = [x[1], -x[1] - math.sin(x[0])]
        lhs = (x[0] + x[1] + 2 * math.sin(x[0])) * h[0] + (x[1] + x[0] + x[1]) * h[1]
        assert close(lhs, -(x[1] ** 2 + x[0] * math.sin(x[0])), 1e-9)
        y = x[0]
        assert 2 * y * (-y + y ** 3) <= 0 or abs(y) >= 1
    assert 4 - 2 * 2 == 0


def check_38():
    p1, p2, p3 = 1.25, 0.25, 0.25
    assert -4 * p2 == -1 and close(p1 - 3 * p2 - 2 * p3, 0) and close(2 * p2 - 6 * p3, -1)
    assert close(p1 * p3 - p2 * p2, 0.25)
    lam = (p1 + p3 + math.sqrt((p1 - p3) ** 2 + 4 * p2 * p2)) / 2
    assert close(lam, 1.309, 1e-3) and close(1 / (2 * lam), 0.382, 1e-3)
    assert close(1 / 6, 0.16667, 1e-4) and close(1 / 0.75, 1.3333, 1e-4) and 2 / 4 == 0.5


def check_39():
    assert close(4 / (6 * math.pi), 0.2122, 1e-3) and close(8 / (6 * math.pi), 0.42441, 1e-4)
    assert close(4 / (math.pi * (4 / (6 * math.pi))), 6) and close(4 / math.pi, 1.2732, 1e-4)
    r = 0.5
    assert close(2 / math.pi * (math.asin(r) + r * math.sqrt(1 - r * r)), 0.609, 1e-3)


def check_40():
    assert (3 + 3, 3 * 3) == (6, 9) and (4 + 4, 4 * 4) == (8, 16)


def fig_36():
    level_set_plot('ct-lyap-level-sets.svg', 'Level curves of V and a trajectory crossing them',
                   lambda x: [-x[0] + x[1], -x[0] - x[1]], lambda x: x[0] ** 2 + x[1] ** 2,
                   [0.25, 1, 2.25, 3.24], [[1.7, 0.4]], R=2.0, t1=10)


def fig_37():
    level_set_plot('ct-lyap-global.svg', 'Global stability: V = x1 squared + 4 x2 squared',
                   lambda x: [-x[0] + 4 * x[1], -x[0] - x[1] ** 3], lambda x: x[0] ** 2 + 4 * x[1] ** 2,
                   [0.5, 2, 4.5, 8], [[2.8, 1.0], [-2.8, -1.0], [-2.5, 1.4], [2.0, -1.4]], R=3.0, t1=30)


# ---------- block diagrams and signal flow graphs: a numeric checker ----------

def solve_lin(A, b):
    """Gaussian elimination for complex matrices."""
    n = len(A)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def diagram_tf(signals, eqs, inputs, out, s):
    """signals: names; eqs: {sig: [(gain_fn, src), ...]} meaning sig = sum gain(s) * src, where src may be
    a signal or an input name; inputs: {name: value}. Returns the value of `out`."""
    idx = {n: i for i, n in enumerate(signals)}
    n = len(signals)
    A = [[0j] * n for _ in range(n)]
    b = [0j] * n
    for sig, terms in eqs.items():
        i = idx[sig]
        A[i][i] += 1
        for g, src in terms:
            if src in idx:
                A[i][idx[src]] -= g(s)
            else:
                b[i] += g(s) * inputs[src]
    x = solve_lin(A, b)
    return x[idx[out]]


TEST_S = (0.7 + 0.4j, 1.9 - 0.8j, 0.3 + 2.1j)


def same_tf(f1, f2):
    return all(abs(f1(s) - f2(s)) < 1e-9 * max(1, abs(f2(s))) for s in TEST_S)


# ---------- modelling and block diagram lessons (Benha chapters 3 and 6) ----------

def check_models():
    for s in TEST_S:
        D = (1 + s) * (s + 1 + 1 / s) - s * s
        assert abs(s / D - s * s / (2 * s * s + 2 * s + 1)) < 1e-12
        a, b = s * s + s + 2, s + 1
        assert abs(a / (a * a - b * b) - a / ((s * s + 1) * (s * s + 2 * s + 3))) < 1e-12
    # loaded RC ladder, R = C = 1: mesh equations
    for s in TEST_S:
        Z = 1 / s
        A = [[1 + Z, -Z], [-Z, 1 + 2 * Z]]
        i1, i2 = solve_lin(A, [1, 0])
        assert abs(i2 * Z - 1 / (s * s + 3 * s + 1)) < 1e-12
    assert close(math.exp(-math.pi * 0.25 / math.sqrt(1 - 0.0625)), 0.444, 1e-2)
    assert 400 * 600 / 1000 == 240 and 300 * 600 / 900 == 200
    assert close(0.5 + 8 * (25 / 100) ** 2, 1) and close(4 * (25 / 100) ** 2, 0.25)
    Kb, Kt = 100 / 50, 2 * 100 / 100
    assert Kb == Kt == 2 and close((0.25 + Kt * Kb / 2) / 1, 2.25) and close(Kt / (2 * 1), 1)
    assert close(9 * (20 / 60) ** 2, 1) and 120 / 40 == 3 and 100e3 / 25e3 == 4 and close(1 / (25e3 * 4e-6), 10)


def check_blocks():
    G1, G2, G3 = (lambda s: 2 / (s + 1)), (lambda s: 3 / (s + 2)), (lambda s: 1 / s)
    H1, H2 = (lambda s: 0.5), (lambda s: s + 4)
    eqs = {'e1': [(lambda s: 1, 'R'), (lambda s: -H1(s), 'y2')], 'y1': [(G1, 'e1')],
           'e2': [(lambda s: 1, 'y1'), (lambda s: -H2(s), 'C')], 'y2': [(G2, 'e2')], 'C': [(G3, 'y2')]}
    f = lambda s: diagram_tf(['e1', 'y1', 'e2', 'y2', 'C'], eqs, {'R': 1}, 'C', s)
    assert same_tf(f, lambda s: G1(s) * G2(s) * G3(s) / (1 + G2(s) * G3(s) * H2(s) + G1(s) * G2(s) * H1(s)))
    for T in (1.0, 3.0):
        eqs = {'e': [(lambda s: 1, 'R'), (lambda s: -51 / 40, 'C')], 'x': [(lambda s: 1, 'e'), (lambda s: -3 / 40, 'd')],
               'a': [(lambda s: 1, 'x'), (lambda s: -3 / 20, 'b')], 'b': [(lambda s: 60 / (s + 8), 'a')],
               'd': [(lambda s, T=T: 2 / (s + T), 'b')], 'C': [(lambda s: 1 / s, 'd')]}
        f = lambda s: diagram_tf(['e', 'x', 'a', 'b', 'd', 'C'], eqs, {'R': 1}, 'C', s)
        assert same_tf(f, lambda s, T=T: 120 / (s ** 3 + (17 + T) * s ** 2 + (17 * T + 9) * s + 153))
    for K in (10.0, 20.0):
        eqs = {'e': [(lambda s: 1, 'R'), (lambda s: -(s + 1), 'Y')], 'u': [(lambda s, K=K: K / (s + 3), 'e')],
               'v': [(lambda s: 1, 'u'), (lambda s: 1, 'D')], 'Y': [(lambda s: 2 / s, 'v')]}
        fr = lambda s: diagram_tf(['e', 'u', 'v', 'Y'], eqs, {'R': 1, 'D': 0}, 'Y', s)
        fd = lambda s: diagram_tf(['e', 'u', 'v', 'Y'], eqs, {'R': 0, 'D': 1}, 'Y', s)
        den = lambda s, K=K: s * (s + 3) + 2 * K * (s + 1)
        assert same_tf(fr, lambda s, K=K: 2 * K / den(s)) and same_tf(fd, lambda s: 2 * (s + 3) / den(s))
        assert close(6 / (2 * K), 3 / K)
    assert close(20 / (2 + 20 * 0.4 + 0) * 1, 2) and 2 + 20 * 0.4 == 10
    assert close(1 / 11, 0.090909, 1e-5)


def fig_blocks():
    b = Blocks(700, 170, 'Series blocks multiply; parallel blocks add')
    y = 45
    b.text(20, y + 5, 'R')
    b.wire([(30, y), (60, y)])
    for i, g in enumerate(('G1', 'G2', 'G3')):
        x = 95 + i * 100
        b.box(x, y, 66, 34, g)
        b.wire([(x + 33, y), (x + 67, y)])
    b.text(372, y + 5, 'C   =   G1 G2 G3', 14, 'start', ACCENT)
    y0 = 115
    b.text(20, y0 + 5, 'R')
    b.wire([(30, y0), (70, y0)])
    b.dot(70, y0)
    for i, (g, yy) in enumerate((('G1', y0 - 34), ('G2', y0), ('G3', y0 + 34))):
        b.wire([(70, y0), (70, yy), (110, yy)], arrow=True)
        b.box(140, yy, 56, 26, g)
        b.wire([(168, yy), (240, yy), (240, y0 + (yy - y0) * 0.45)])
    b.sum(240, y0, signs={})
    b.wire([(253, y0), (300, y0)])
    b.text(310, y0 + 5, 'C   =   G1 + G2 + G3', 14, 'start', ACCENT)
    b.save('ct-bd-series-parallel.svg')

    # the four moves: before -> after, in a 2 x 2 grid of panels
    b = Blocks(760, 330, 'Moving summing points and take-off points past a block')

    def panel(ox, oy, title, kind):
        b.text(ox + 180, oy + 14, title, 13, 'middle', INK)
        y = oy + 55
        # before (left) and after (right), each about 160 wide
        for side in (0, 1):
            x0 = ox + side * 195
            b.wire([(x0, y), (x0 + 22, y)])
            if kind in ('sum-fwd', 'sum-back'):
                before_sum = (kind == 'sum-fwd') == (side == 0)
                if before_sum:
                    b.sum(x0 + 35, y, signs={'w': '+', 's': '+'})
                    b.wire([(x0 + 48, y), (x0 + 75, y)])
                    b.box(x0 + 100, y, 46, 30, 'G')
                    b.wire([(x0 + 123, y), (x0 + 165, y)])
                    lab = 'X' if kind == 'sum-fwd' else 'X / G'
                    b.wire([(x0 + 35, y + 50), (x0 + 35, y + 13)])
                    b.text(x0 + 35, y + 64, lab if side == 1 else 'X', 12)
                else:
                    b.box(x0 + 45, y, 46, 30, 'G')
                    b.wire([(x0 + 68, y), (x0 + 112, y)])
                    b.sum(x0 + 125, y, signs={'w': '+', 's': '+'})
                    b.wire([(x0 + 138, y), (x0 + 165, y)])
                    lab = 'G X' if kind == 'sum-fwd' else 'X'
                    b.wire([(x0 + 125, y + 50), (x0 + 125, y + 13)])
                    b.text(x0 + 125, y + 64, lab, 12)
            else:
                before_take = (kind == 'take-fwd') == (side == 0)
                if before_take:
                    b.dot(x0 + 32, y)
                    b.box(x0 + 85, y, 46, 30, 'G')
                    b.wire([(x0 + 22, y), (x0 + 62, y)])
                    b.wire([(x0 + 108, y), (x0 + 165, y)])
                    b.wire([(x0 + 32, y), (x0 + 32, y + 48)])
                    b.text(x0 + 32, y + 62, 'R' if side == 0 else 'branch × G', 12)
                else:
                    b.box(x0 + 55, y, 46, 30, 'G')
                    b.wire([(x0 + 78, y), (x0 + 165, y)])
                    b.dot(x0 + 128, y)
                    b.wire([(x0 + 128, y), (x0 + 128, y + 48)])
                    b.text(x0 + 128, y + 62, 'GR' if side == 0 else 'branch ÷ G', 12)
            if side == 0:
                b.text(ox + 182, y + 5, '≡', 18)
    panel(0, 0, 'Summing point moved forward: multiply X by G', 'sum-fwd')
    panel(380, 0, 'Summing point moved backward: divide X by G', 'sum-back')
    panel(0, 165, 'Take-off point moved forward: divide branch by G', 'take-fwd')
    panel(380, 165, 'Take-off point moved backward: multiply branch by G', 'take-back')
    b.save('ct-bd-moves.svg')

    b = Blocks(760, 220, 'Nested loops: 3/20 inside 3/40 inside 51/40')
    y = 60
    b.text(18, y + 5, 'R')
    b.wire([(28, y), (55, y)])
    b.sum(68, y, signs={'w': '+', 's': '−'})
    b.wire([(81, y), (105, y)])
    b.sum(118, y, signs={'w': '+', 's': '−'})
    b.wire([(131, y), (155, y)])
    b.sum(168, y, signs={'w': '+', 's': '−'})
    b.wire([(181, y), (210, y)])
    b.box(235, y, 50, 32, '12')
    b.wire([(260, y), (290, y)])
    b.box(330, y, 80, 36, '5/(s+8)')
    b.wire([(370, y), (420, y)])
    b.box(460, y, 80, 36, '2/(s+T)')
    b.wire([(500, y), (550, y)])
    b.box(580, y, 60, 32, '1/s')
    b.wire([(610, y), (700, y)])
    b.text(710, y + 5, 'C', anchor='start')
    b.dot(395, y)
    b.wire([(395, y), (395, 105), (310, 105)])
    b.box(280, 105, 60, 26, '3/20')
    b.wire([(250, 105), (168, 105), (168, y + 13)])
    b.dot(525, y)
    b.wire([(525, y), (525, 145), (360, 145)])
    b.box(330, 145, 60, 26, '3/40')
    b.wire([(300, 145), (118, 145), (118, y + 13)])
    b.dot(660, y)
    b.wire([(660, y), (660, 190), (400, 190)])
    b.box(370, 190, 60, 26, '51/40')
    b.wire([(340, 190), (68, 190), (68, y + 13)])
    b.save('ct-bd-nested.svg')

    def overlap(b, oy, moved):
        y = oy + 40
        b.text(18, y + 5, 'R')
        b.wire([(28, y), (55, y)])
        b.sum(68, y, signs={'w': '+', 's': '−'})
        b.wire([(81, y), (110, y)])
        b.box(140, y, 56, 30, 'G1')
        b.wire([(168, y), (205, y)])
        b.sum(218, y, signs={'w': '+', 's': '−'})
        b.wire([(231, y), (265, y)])
        b.box(295, y, 56, 30, 'G2')
        b.wire([(323, y), (385, y)])
        b.box(415, y, 56, 30, 'G3')
        b.wire([(443, y), (540, y)])
        b.text(548, y + 5, 'C', anchor='start')
        b.dot(500, y)
        b.wire([(500, y), (500, y + 45), (335, y + 45)])
        b.box(305, y + 45, 56, 26, 'H2')
        b.wire([(277, y + 45), (218, y + 45), (218, y + 13)])
        tx = 520 if moved else 355
        b.dot(tx, y)
        b.wire([(tx, y), (tx, y + 85), (210, y + 85)])
        b.box(170, y + 85, 72 if moved else 56, 26, 'H1 / G3' if moved else 'H1')
        b.wire([(134 if moved else 142, y + 85), (68, y + 85), (68, y + 13)])
    b = Blocks(600, 300, 'Overlapping loops, before and after moving the H1 take-off point')
    overlap(b, 0, False)
    b.text(590, 20, 'before', 12, 'end', GREY)
    overlap(b, 150, True)
    b.text(590, 170, 'after: H1 take-off moved past G3', 12, 'end', GREY)
    b.save('ct-bd-overlap.svg')

    b = Blocks(600, 150, 'A loop with a disturbance input')
    y = 55
    b.text(18, y + 5, 'R')
    b.wire([(28, y), (75, y)])
    b.sum(88, y, signs={'w': '+', 's': '−'})
    b.wire([(101, y), (145, y)])
    b.box(190, y, 80, 36, 'K/(s+3)')
    b.wire([(230, y), (297, y)])
    b.sum(310, y, signs={'w': '+', 'n': '+'})
    b.text(310, 14, 'D')
    b.wire([(310, 20), (310, y - 13)])
    b.wire([(323, y), (365, y)])
    b.box(400, y, 60, 32, '2/s')
    b.wire([(430, y), (520, y)])
    b.text(528, y + 5, 'Y', anchor='start')
    b.dot(480, y)
    b.wire([(480, y), (480, 120), (330, 120)])
    b.box(290, 120, 70, 28, 's + 1')
    b.wire([(255, 120), (88, 120), (88, y + 13)])
    b.save('ct-bd-disturbance.svg')

    b = Blocks(780, 190, 'Block diagram of a geared DC motor')
    y = 60
    b.text(18, y + 5, 'Ea')
    b.wire([(34, y), (62, y)])
    b.sum(75, y, signs={'w': '+', 's': '−'})
    b.wire([(88, y), (118, y)])
    b.box(150, y, 60, 32, '1/Ra')
    b.wire([(180, y), (220, y)], label='Ia')
    b.box(250, y, 56, 32, 'Kt')
    b.wire([(278, y), (318, y)], label='Tm')
    b.box(365, y, 90, 36, '1/(Js + B)')
    b.wire([(410, y), (470, y)], label='ω')
    b.box(500, y, 56, 32, '1/s')
    b.wire([(528, y), (575, y)], label='θm')
    b.box(615, y, 76, 34, 'N1/N2')
    b.wire([(653, y), (720, y)])
    b.text(728, y + 5, 'θL', anchor='start')
    b.dot(440, y)
    b.wire([(440, y), (440, 140), (300, 140)])
    b.box(270, 140, 56, 30, 'Kb')
    b.wire([(242, 140), (75, 140), (75, y + 13)], label='back emf')
    b.save('ct-dc-motor.svg')


def sfg(name, title, nodes, edges, rank=None):
    """nodes: list of names in left-to-right order; edges: (src, dst, label, back)."""
    lines = [f'digraph {{ bgcolor="white"; pad=0.25; rankdir=LR; nodesep=0.5; ranksep=0.75;',
             f'node [shape=circle, width=0.13, height=0.13, fixedsize=true, style=filled, fillcolor="{INK}", label="", '
             f'fontname="{FONT}", fontsize=13];',
             f'edge [fontname="{FONT}", fontsize=13, color="{INK}", fontcolor="{INK}", arrowsize=0.7];']
    for n in nodes:
        lines.append(f'"{n}" [xlabel="{n}"];')
    for i in range(len(nodes) - 1):
        pass
    for src, dst, lab, back in edges:
        attrs = f'label=" {lab} "'
        if back:
            attrs += ', constraint=false, color="#b45309", fontcolor="#b45309"'
        if src == dst:
            attrs += ', dir=forward'
        lines.append(f'"{src}" -> "{dst}" [{attrs}];')
    if rank:
        lines.append(rank)
    lines.append('}')
    save_dot('\n'.join(lines), name, title, OUT)


def check_sfg():
    A = [[1 - 7, -2, -5], [6, 1 - 4, -8], [-3, 9, 1 - 6]]
    x = solve_lin(A, [1, 0, 0])
    assert close((2 * x[0] + x[1] + 3 * x[2]).real, -121 / 285)
    G = [lambda s: 1 / (s + 1), lambda s: 2 / (s + 3), lambda s: s / (s + 2), lambda s: 3, lambda s: 1 / s,
         lambda s: (s + 1) / (s + 4)]
    H1, H2 = (lambda s: 0.7), (lambda s: s + 0.5)
    eqs = {'x1': [(lambda s: 1, 'R')], 'x2': [(G[0], 'x1'), (lambda s: -H1(s), 'x3')], 'x3': [(G[1], 'x2')],
           'x4': [(G[3], 'x1'), (lambda s: -H2(s), 'x5')], 'x5': [(G[4], 'x4')], 'C': [(G[2], 'x3'), (G[5], 'x5')]}
    f = lambda s: diagram_tf(['x1', 'x2', 'x3', 'x4', 'x5', 'C'], eqs, {'R': 1}, 'C', s)
    L1, L2 = (lambda s: -G[1](s) * H1(s)), (lambda s: -G[4](s) * H2(s))
    P1, P2 = (lambda s: G[0](s) * G[1](s) * G[2](s)), (lambda s: G[3](s) * G[4](s) * G[5](s))
    assert same_tf(f, lambda s: (P1(s) * (1 - L2(s)) + P2(s) * (1 - L1(s))) / (1 - L1(s) - L2(s) + L1(s) * L2(s)))
    assert 1 - (-2 - 3) == 6 and 1 - (-2 - 3) + 6 == 12 and close(10 / 6, 1.6667, 1e-4)
    assert (4 * 4 + 6 * 2) / 8 == 3.5 and close(4 / 2 + 6 / 4, 3.5)


def fig_sfg():
    sfg('ct-sfg-equations.svg', 'Signal flow graph of three simultaneous equations',
        ['R', 'x1', 'x2', 'x3', 'C'],
        [('R', 'x1', '1', False), ('x1', 'x2', '−6', False), ('x2', 'x3', '−9', False), ('x3', 'C', '3', False),
         ('x1', 'x3', '3', False), ('x1', 'C', '2', False), ('x2', 'C', '1', False),
         ('x2', 'x1', '2', True), ('x3', 'x1', '5', True), ('x3', 'x2', '8', True),
         ('x1', 'x1', '7', False), ('x2', 'x2', '4', False), ('x3', 'x3', '6', False)])
    sfg('ct-sfg-overlap.svg', 'Signal flow graph of the overlapping-loop system',
        ['R', 'e1', 'y1', 'e2', 'y2', 'C'],
        [('R', 'e1', '1', False), ('e1', 'y1', 'G1', False), ('y1', 'e2', '1', False), ('e2', 'y2', 'G2', False),
         ('y2', 'C', 'G3', False), ('y2', 'e1', '−H1', True), ('C', 'e2', '−H2', True)])
    sfg('ct-sfg-parallel.svg', 'Signal flow graph with two parallel routes, each with its own loop',
        ['R', 'x1', 'x2', 'x3', 'x4', 'x5', 'C'],
        [('R', 'x1', '1', False), ('x1', 'x2', 'G1', False), ('x2', 'x3', 'G2', False), ('x3', 'C', 'G3', False),
         ('x1', 'x4', 'G4', False), ('x4', 'x5', 'G5', False), ('x5', 'C', 'G6', False),
         ('x3', 'x2', '−H1', True), ('x5', 'x4', '−H2', True)],
        rank='{rank=same; x2; x4} {rank=same; x3; x5}')


def check_sse_routh_rl():
    # SSE 1
    assert 120 * 2 / 12 == 20 and close(5 / 21, 0.238, 1e-3) and close(10 / 5, 2) and 20 * 4 == 80
    assert close(5 * 672 / 336, 10)
    # SSE 2: non-unity
    G = lambda s: 100 / (s * (s + 10))
    H = lambda s: 1 / (s + 5)
    Ge = G(1e-9) / (1 + G(1e-9) * H(1e-9) - G(1e-9))
    assert close(Ge, -1.25, 1e-6) and close(1 / (1 + Ge), -4, 1e-6)
    assert max(z.real for z in roots([1, 15, 50, 100])) < 0
    assert close(1 - 10 / 21, 11 / 21) and close(-1 / (2 + 50), -0.019231, 1e-4) and -1 / 1000 == -0.001
    # Routh 2
    r = roots([1, 2, 3, 6, 5, 3])
    assert sum(1 for z in r if z.real > 0) == 2
    r = roots([1, 7, 6, 42, 8, 56])
    assert sum(1 for z in r if abs(z.real) < 1e-6) == 4 and any(close(z.real, -7, 1e-6) for z in r)
    assert sum(1 for z in roots([1, 1, 2, 2, 3]) if z.real > 0) == 2
    assert max(z.real for z in roots([1, 17 - 0.1, 17 * -0.1 + 9, 153])) > 0
    assert max(z.real for z in roots([1, 17.01, 17 * 0.01 + 9, 153])) < 0
    assert 6 * 11 == 66 and close(math.sqrt(11), 3.3166, 1e-4)
    # RL 2
    s = complex(-3, 4)
    assert close(math.degrees(cmath.phase((s + 1) / (s * (s + 2)))), -114.34, 1e-4)
    p = complex(-1, math.sqrt(2))
    assert close(180 + math.degrees(cmath.phase(p + 2)) - 90, 144.74, 1e-4)
    assert 5 * 8 == 40
    # design: lead
    z = -math.log(0.3) / math.sqrt(math.pi ** 2 + math.log(0.3) ** 2)
    assert close(z, 0.358, 2e-3)
    sA = complex(-1.006, 2.627)
    assert close(abs(sA * (sA + 4) * (sA + 6)), 63.2, 3e-3)
    sd = complex(-2.014, 5.255)
    ang = sum(-math.degrees(cmath.phase(sd + q)) for q in (0, 4, 6))
    assert close(ang, -233.08, 1e-4) and close(-180 - ang, 53.08, 1e-3)
    pc = -sd.real + sd.imag / math.tan(math.radians(math.degrees(cmath.phase(sd + 5)) - (-180 - ang)))
    assert close(pc, 42.97, 1e-3)
    K = abs(sd * (sd + 4) * (sd + 6) * (sd + pc) / (sd + 5))
    assert close(K, 1425, 2e-3)
    poly = polymul(polymul([1, 0], [1, 4]), polymul([1, 6], [1, pc]))
    poly[-2] += K
    poly[-1] += 5 * K
    cl = roots(poly)
    assert any(abs(r - sd) < 0.02 for r in cl)
    others = sorted(r.real for r in cl if abs(r.imag) < 1e-6)
    assert close(others[0], -43.8, 1e-3) and close(others[1], -5.13, 2e-3)
    # lag
    s = complex(-0.3307, 0.5864)
    assert close(abs(s * (s + 1) * (s + 2)), 1.06, 1e-3) and close(5 / 0.53, 9.43, 1e-3)
    assert close(math.degrees(cmath.phase((s + 0.053) / (s + 0.0056))), -3.66, 1e-2)
    assert -180 + 210 == 30 and 20 / 2 == 10


def check_bode_nyq():
    ph = lambda w: -90 - math.degrees(math.atan(w)) - math.degrees(math.atan(w / 2))
    w45 = bisect(lambda w: ph(w) + 135, 0.05, 1.0)
    K45 = w45 * math.sqrt(w45 ** 2 + 1) * math.sqrt(w45 ** 2 + 4)
    assert close(w45, 0.562, 1e-3) and close(K45, 1.34, 3e-3) and close(db(6 / K45), 13.0, 3e-3)
    w60 = bisect(lambda w: ph(w) + 120, 0.05, 1.0)
    assert close(w60, 0.36, 1e-2) and close(w60 * math.sqrt(w60 ** 2 + 1) * math.sqrt(w60 ** 2 + 4), 0.78, 1e-2)
    z = -math.log(0.2) / math.sqrt(math.pi ** 2 + math.log(0.2) ** 2)
    wn = 4 / (z * 2)
    bw = wn * math.sqrt((1 - 2 * z * z) + math.sqrt(4 * z ** 4 - 4 * z * z + 2))
    assert close(z, 0.456, 2e-3) and close(wn, 4.39, 2e-3) and close(bw, 5.79, 2e-3)
    assert close(1 / (2 * z * math.sqrt(1 - z * z)), 1.23, 3e-3) and close(wn * math.sqrt(1 - 2 * z * z), 3.35, 2e-3)
    assert close(db(9), 19.1, 2e-3) and close(10 ** (25 / 20), 17.78, 1e-3) and close(1 / math.sqrt(3), 0.577, 1e-3)
    assert close(1 / (2 * 0.5 * math.sqrt(0.75)), 1.1547, 1e-4)
    G = lambda w: 10 / (1j * w + 1) ** 3
    assert close(G(math.sqrt(3)).real, -1.25) and close(G(1 / math.sqrt(3)).imag, -6.495, 1e-3)
    assert sum(1 for r in roots([1, 3, 3, 11]) if r.real > 0) == 2
    assert close(L_loop(1e-5).real, -0.75, 1e-4) and close(5 / -8, -0.625)


def fig_nyq_sketch():
    G = lambda w: 10 / (1j * w + 1) ** 3
    p = Plot(520, 440, (-3, 11), (-7.5, 7.5), 'Polar and Nyquist plot of 10 over (s+1) cubed', ml=24, mb=24)
    p.axes(cross=True, grid=False)
    ws = [10 ** (-3 + 5 * i / 1500) for i in range(1501)]
    pts = [G(w) for w in ws]
    p.curve([z.real for z in pts], [z.imag for z in pts], BLUE, 2.4)
    p.curve([z.real for z in pts], [-z.imag for z in pts], BLUE, 1.4, '6,4')
    p.cross(-1, 0, TRUE, 6)
    p.label(-1, 0.6, '−1', TRUE, 13, 'middle')
    p.dot(-1.25, 0, ORANGE)
    p.label(-1.2, -1.2, '−1.25 at ω = 1.73', ORANGE, 12)
    p.dot(0, -6.495, ORANGE)
    p.label(0.3, -6.6, '−6.50j at ω = 0.577', ORANGE, 12)
    p.dot(10, 0, INK)
    p.label(10, 0.6, '10 at ω = 0', INK, 12, 'middle')
    z1, z2 = G(1.2), G(1.25)
    p.arrow(z1.real, z1.imag, z2.real - z1.real, z2.imag - z1.imag, BLUE, 9)
    p.save('ct-nyq-sketch-type0.svg')

    p = Plot(520, 460, (-1.6, 1.6), (-2.2, 2.2), 'Nyquist plot of 1 over s(s+1)(s+2) with its closing arc', ml=24, mb=24)
    p.axes(cross=True, grid=False)
    ws = [10 ** (-0.75 + 2.5 * i / 1000) for i in range(1001)]
    pts = [L_loop(w) for w in ws]
    p.curve([z.real for z in pts], [z.imag for z in pts], BLUE, 2.4)
    p.curve([z.real for z in pts], [-z.imag for z in pts], BLUE, 1.4, '6,4')
    p.curve([-0.75, -0.75], [-2.2, 2.2], GREY, 1.2, '3,3')
    p.label(-0.78, 2.0, 'asymptote −0.75', GREY, 11, 'end')
    # schematic large arc (drawn at radius 2.05, clockwise from the omega=0- branch top to the omega=0+ branch bottom)
    th = [math.pi / 2 - math.pi * i / 100 for i in range(101)]
    p.curve([-0.75 + 2.0 * math.cos(t) * 1.15 + 0.75 if False else 2.05 * math.cos(t) * 0.7 for t in th],
            [2.05 * math.sin(t) for t in th], PURPLE, 1.6, '8,5', clip=False)
    p.label(1.25, 0.15, 'infinite arc (shrunk)', PURPLE, 11, 'end')
    p.cross(-1, 0, TRUE, 6)
    p.label(-1, 0.18, '−1', TRUE, 13, 'middle')
    p.dot(-1 / 6, 0, ORANGE)
    p.label(-0.2, -0.25, '−1/6', ORANGE, 12, 'end')
    p.save('ct-nyq-sketch-type1.svg')


def check_ss34():
    for s in TEST_S:
        x = solve_lin([[s, -1, 0], [0, s, -1], [24, 26, s + 9]], [0, 0, 1])
        assert abs(2 * x[0] + 7 * x[1] + x[2] - (s * s + 7 * s + 2) / (s ** 3 + 9 * s ** 2 + 26 * s + 24)) < 1e-12
        assert abs(24 * x[0] - 24 / (s ** 3 + 9 * s ** 2 + 26 * s + 24)) < 1e-12
    ts, xs = rk4(lambda t, x: [x[1], -2 * x[0] - 3 * x[1] + 1], [1.0, 0.0], 0, 3, 3000)
    for t, x in zip(ts[::300], xs[::300]):
        assert abs(x[0] - (0.5 + math.exp(-t) - 0.5 * math.exp(-2 * t))) < 1e-9
        assert abs(x[1] - (-math.exp(-t) + math.exp(-2 * t))) < 1e-9
    P = [[1, 1], [-1, -2]]
    D = mmul(minv2(P), mmul([[0, 1], [-2, -3]], P))
    assert all(abs(D[i][j] - [[-1, 0], [0, -2]][i][j]) < 1e-12 for i in range(2) for j in range(2))


def fig_46():
    svg = Svg(660, 240, 'Saturation, dead zone and backlash')

    def panel(ox, title):
        p = Plot(220, 240, (-2, 2), (-2, 2), '', ml=14, mr=14, mt=30, mb=14)
        p.s = svg
        p.X = (lambda X0: (lambda x: X0(x) + ox))(p.X)
        svg.line(p.X(-2), p.Y(0), p.X(2), p.Y(0), GRID, 1)
        svg.line(p.X(0), p.Y(-2), p.X(0), p.Y(2), GRID, 1)
        svg.text(ox + 110, 20, title, 13, INK, 'middle', 'bold')
        p.label(1.95, -0.25, 'input', GREY, 10, 'end')
        p.label(0.08, 1.8, 'output', GREY, 10)
        return p
    xs = [-2 + 4 * i / 200 for i in range(201)]
    p = panel(0, 'saturation')
    p.curve(xs, [max(-1.2, min(1.2, x)) for x in xs], BLUE, 2.4)
    p = panel(220, 'dead zone')
    p.curve(xs, [0 if abs(x) < 0.6 else (x - 0.6 if x > 0 else x + 0.6) for x in xs], BLUE, 2.4)
    p = panel(440, 'backlash')
    b = 0.5
    p.curve([-1.5 + b, 1.5 + b], [-1.5, 1.5], BLUE, 2.4)        # rising: y = x - b
    p.curve([-1.5 - b, 1.5 - b], [-1.5, 1.5], ORANGE, 2.4)      # falling: y = x + b
    p.curve([1.5 - b, 1.5 + b], [1.5, 1.5], GREY, 1.6, '4,3')
    p.curve([-1.5 - b, -1.5 + b], [-1.5, -1.5], GREY, 1.6, '4,3')
    p.arrow(0.5 + b, 0.5, 0.1, 0.1, BLUE, 8)
    p.arrow(-0.5 - b, -0.5, -0.1, -0.1, ORANGE, 8)
    p.label(1.0, -0.6, 'going up', BLUE, 10)
    p.label(-1.0, 0.6, 'going down', ORANGE, 10, 'end')
    svg.save('ct-hard-nonlinearities.svg', OUT)


# ---------- main ----------

if __name__ == '__main__':
    g = dict(globals())
    for k in sorted(g):
        if k.startswith('check_'):
            g[k]()
    print('all lesson numbers check out')
    only = sys.argv[1:]
    for k in sorted(g):
        if k.startswith('fig_') and (not only or k in only):
            g[k]()
