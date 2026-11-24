"""Draw the systems simulation lesson diagrams as small SVG files, and check the lessons' numbers.

    python3 scripts/diagrams/systems_simulation.py      # run from the vault root

Every worked example and quiz answer in systems-simulation/ that comes from a sum is checked
here with an assert before anything is drawn: the hand simulations, the queueing formulas,
the random number generators and their periods, the test statistics, the inverse transforms
and the Monte Carlo estimates. The flowcharts are drawn with Graphviz (`dot`, which must be
installed). Output: systems-simulation/images/*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, GRID, PIX, TRUE, ACCENT, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('systems-simulation', 'images')
ORANGE = '#f59e0b'
GREY = '#9ca3af'


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ---------- queues (lessons 09 to 15, 24, 37, 38) ----------

def hand_sim(arrivals, services):
    """Single server, FIFO. Returns rows of (arrival, start, service, departure, delay, time in system)."""
    rows, free_at = [], None
    for a, s in zip(arrivals, services):
        start = a if free_at is None else max(a, free_at)
        dep = start + s
        rows.append((a, start, s, dep, start - a, dep - a))
        free_at = dep
    return rows


def mm1(lam, mu):
    rho = lam / mu
    return dict(rho=rho, L=rho / (1 - rho), Lq=rho ** 2 / (1 - rho), W=1 / (mu - lam), Wq=rho / (mu - lam), P0=1 - rho)


def mmc(lam, mu, c):
    a, rho = lam / mu, lam / (c * mu)
    tail = a ** c / math.factorial(c) / (1 - rho)
    p0 = 1 / (sum(a ** n / math.factorial(n) for n in range(c)) + tail)
    pw = tail * p0
    lq = pw * rho / (1 - rho)
    return dict(a=a, rho=rho, P0=p0, Pw=pw, Lq=lq, Wq=lq / lam, W=lq / lam + 1 / mu, L=lq + a)


def pk_wq(lam, mean_s, var_s):
    rho = lam * mean_s
    return lam * (var_s + mean_s ** 2) / (2 * (1 - rho))


# ---------- random numbers (lessons 16 to 22) ----------

def lcg(x0, a, c, m, n):
    xs, x = [], x0
    for _ in range(n):
        x = (a * x + c) % m
        xs.append(x)
    return xs


def period(x0, a, c, m):
    seen, x, i = {}, x0, 0
    while x not in seen:
        seen[x] = i
        x = (a * x + c) % m
        i += 1
    return i - seen[x]


def ks(nums):
    r, n = sorted(nums), len(nums)
    dplus = max((i + 1) / n - x for i, x in enumerate(r))
    dminus = max(x - i / n for i, x in enumerate(r))
    return dplus, dminus


def chi_square(observed):
    e = sum(observed) / len(observed)
    return sum((o - e) ** 2 / e for o in observed)


def autocorr_M(n, i, m):
    M = 0
    while i + (M + 2) * m <= n:
        M += 1
    return M


def expo(mean, r):
    return -mean * math.log(1 - r)


def check_lessons():
    # 09: the hand-run bank (arrivals 0, 3, 4, service 5) and the quiz (0, 2, 3, service 4)
    assert [row[3] for row in hand_sim([0, 3, 4], [5, 5, 5])] == [5, 10, 15]
    assert hand_sim([0, 2, 3], [4, 4, 4])[2][3] == 12
    # 12: the two-customer example and quiz
    two = hand_sim([1, 2], [3, 4])
    assert [r[4] for r in two] == [0, 2] and [r[5] for r in two] == [3, 6] and close(7 / 8, 0.875)
    # 13: the four-customer table and the quiz data
    four = hand_sim([2, 5, 6, 10], [4, 3, 5, 2])
    assert [r[1] for r in four] == [2, 6, 9, 14] and [r[3] for r in four] == [6, 9, 14, 16]
    assert sum(r[4] for r in four) / 4 == 2 and sum(r[5] for r in four) / 4 == 5.5
    assert sum(r[2] for r in four) / 16 == 0.875
    quiz = hand_sim([1, 3, 4, 10], [3, 4, 2, 2])
    assert quiz[2][1] == 8 and sum(r[4] for r in quiz) / 4 == 1.25 and sum(r[5] for r in quiz) / 4 == 4
    assert quiz[-1][3] == 12 and close(sum(r[2] for r in quiz) / 12, 11 / 12)
    # 14: Little's law, the pharmacy, the quiz queue
    assert close(12 * 0.25, 3)
    ph = mm1(1 / 6, 1 / 3)
    assert close(ph['rho'], 0.5) and close(ph['Lq'], 0.5) and close(ph['Wq'], 3)
    q = mm1(4, 6)
    assert close(q['L'], 2) and close(q['Wq'] * 60, 20) and close(q['Lq'] / 4, q['Wq'])
    assert close(mm1(1, 1 / 0.5)['L'], 1) and close(mm1(0.8, 1)['L'], 4) and close(mm1(0.9, 1)['L'], 9)
    # 15: M/M/c example (corrected) and quiz, plus the c = 1 check
    ex = mmc(2, 1.5, 2)
    assert close(ex['P0'], 0.2) and close(ex['Pw'], 0.533333, 1e-5) and close(ex['Lq'], 1.066667, 1e-5)
    assert close(ex['Wq'], 0.533333, 1e-5)
    qz = mmc(3, 2, 2)
    assert close(qz['P0'], 1 / 7) and close(qz['Pw'], 9 / 14) and close(qz['Lq'], 27 / 14)
    one, ref = mmc(0.6, 1, 1), mm1(0.6, 1)
    assert close(one['P0'], ref['P0']) and close(one['Lq'], ref['Lq']) and close(one['Pw'], 0.6)
    # 17: the linear congruential sequences
    assert lcg(37, 17, 29, 100, 6) == [58, 15, 84, 57, 98, 95]
    assert lcg(27, 17, 43, 100, 3) == [2, 77, 52]
    assert lcg(7, 5, 3, 16, 2) == [6, 1] and lcg(12, 13, 32, 100, 1) == [88]
    # 18: periods
    assert [period(s, 13, 0, 64) for s in (1, 2, 3, 4)] == [16, 8, 16, 4]
    assert period(7, 5, 3, 16) == 16 and period(1, 5, 0, 32) == 32 // 4
    # 19: Kolmogorov-Smirnov
    dp, dm = ks([0.44, 0.81, 0.14, 0.05, 0.93])
    assert close(dp, 0.26) and close(dm, 0.21)
    dp, dm = ks([0.39, 0.08, 0.82, 0.31])
    assert close(dp, 0.36) and close(dm, 0.08)
    # 20: chi-square and autocorrelation M
    assert close(chi_square([8, 12, 10, 7, 13]), 2.6) and close(chi_square([12, 7, 9, 11, 14, 7]), 4.0)
    assert autocorr_M(30, 3, 5) == 4 and autocorr_M(40, 2, 6) == 5
    # 21: inverse transform
    assert close(expo(2, 0.6), 1.832581, 1e-6) and close(expo(4, 0.25), 1.150728, 1e-6)
    assert close(expo(3, 0.5), 2.079442, 1e-6)
    # 22: Monte Carlo and the news vendor
    xs = [0 + 2 * r for r in (0.5, 0.25, 0.75)]
    assert close(2 * sum(x * x for x in xs) / 3, 7 / 3)
    assert 60 * 50 + 10 * 5 - 70 * 30 == 950 and 60 * 50 - 60 * 30 == 1200
    # 24 and 37/38: expected utilisations and the Pollaczek-Khinchine checks
    assert close(13.5 / 15, 0.9) and close(12 / 16, 0.75)
    assert close(pk_wq(0.2, 4, 1), 8.5) and close(0.2 * pk_wq(0.2, 4, 1), 1.7)
    assert close(pk_wq(0.1, 6, 4), 5) and close(6 / 10, 0.6)
    assert close((0.75 + 1.5 + 3) / 3 / 2, 0.875) and close((2 + 4 + 6) / 3 / 5, 0.8)
    # 05, 26, 34: small sums
    assert 12 - 7 == 5 and close(2000 * 0.001, 2)
    assert close(2.262 * 1.5 / math.sqrt(10), 1.073, 1e-3) and close(2.131 * 2 / 4, 1.0655)
    print('all lesson numbers check out')


# ---------- drawing helpers ----------

class Plot:
    """Data axes inside an Svg: x from x0 to x1 maps to the box [left, left + w], y to [top + h, top]."""

    def __init__(self, s, left, top, w, h, x0, x1, y0, y1):
        self.s, self.left, self.top, self.w, self.h = s, left, top, w, h
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1

    def P(self, x, y):
        return (self.left + (x - self.x0) / (self.x1 - self.x0) * self.w,
                self.top + self.h - (y - self.y0) / (self.y1 - self.y0) * self.h)

    def axes(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str):
        s = self.s
        for x in xticks:
            px, _ = self.P(x, self.y0)
            s.line(px, self.top, px, self.top + self.h, color=GRID, width=0.8)
            s.text(px, self.top + self.h + 16, xfmt(x), size=11, color='#374151')
        for y in yticks:
            _, py = self.P(self.x0, y)
            s.line(self.left, py, self.left + self.w, py, color=GRID, width=0.8)
            s.text(self.left - 6, py + 4, yfmt(y), size=11, color='#374151', anchor='end')
        s.line(self.left, self.top + self.h, self.left + self.w, self.top + self.h, width=1.5)
        s.line(self.left, self.top, self.left, self.top + self.h, width=1.5)
        s.text(self.left + self.w / 2, self.top + self.h + 36, xlabel, size=12)
        s.add(f'<text x="{self.left - 46:.1f}" y="{self.top + self.h / 2:.1f}" font-size="12" fill="{INK}" '
              f'text-anchor="middle" font-family="system-ui, sans-serif" '
              f'transform="rotate(-90 {self.left - 46:.1f} {self.top + self.h / 2:.1f})">{ylabel}</text>')

    def curve(self, pts, color, width=2.5, dash=None):
        d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in (self.P(*p) for p in pts))
        self.s.path(d, color, width=width, dash=dash)

    def dot(self, x, y, color, r=4.5):
        self.s.circle(*self.P(x, y), r, color, '#ffffff')


def dot_graph(body, name, title, rankdir='TB', extra=''):
    src = (f'digraph {{ bgcolor="white"; pad=0.25; rankdir={rankdir}; nodesep=0.35; ranksep=0.35; {extra}\n'
           f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", fillcolor="#dbeafe", '
           f'color="{INK}", penwidth=1.2];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];\n' + '\n'.join(body) + '\n}')
    save_dot(src, name, title, OUT)


# ---------- the diagrams ----------

def ways_to_study():
    body = ['sys [label="System", fillcolor="#e5e7eb"];',
            'act [label="Experiment with\\nthe actual system", fillcolor="#e5e7eb"];',
            'mod [label="Experiment with\\na model of the system"];',
            'phy [label="Physical model", fillcolor="#e5e7eb"];',
            'mat [label="Mathematical model"];',
            'ana [label="Analytical solution", fillcolor="#e5e7eb"];',
            'sim [label="Simulation", fillcolor="#d1fae5", penwidth=2];',
            'sys -> act; sys -> mod; mod -> phy; mod -> mat; mat -> ana; mat -> sim;']
    dot_graph(body, 'ss-ways-to-study.svg',
              'A tree of the ways to study a system: the system splits into experimenting with the actual system or '
              'with a model; the model splits into a physical model or a mathematical model; the mathematical model '
              'splits into an analytical solution or a simulation')


def simulation_study():
    steps = ['1. Problem formulation', '2. Objectives and overall design', '3. Model conceptualisation',
             '4. Data collection', '5. Model translation', '6. Verified?', '7. Validated?',
             '8. Experimental design', '9. Production runs and analysis', '10. More runs?',
             '11. Documentation and reporting', '12. Implementation']
    phase = [0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3]
    fills = ['#e5e7eb', '#dbeafe', '#d1fae5', '#fef3c7']
    names = ['Planning', 'Building the model', 'Running it', 'Reporting']
    body = []
    for p in range(4):
        body.append(f'subgraph cluster_{p} {{ label="{names[p]}"; fontname="{FONT}"; fontsize=12; '
                    f'style="rounded,dashed"; color="{GREY}";')
        for i, st in enumerate(steps):
            if phase[i] == p:
                shape = ', shape=diamond, style="filled", width=1.6' if st.endswith('?') else ''
                body.append(f's{i} [label="{st}", fillcolor="{fills[p]}"{shape}];')
        body.append('}')
    body += ['s0 -> s1; s1 -> s2; s2 -> s3; s3 -> s4; s4 -> s5;',
             's5 -> s6 [label=" yes"];',
             's5 -> s4 [label=" no", style=dashed, color="#b45309", fontcolor="#b45309", constraint=false];',
             's6 -> s7 [label=" yes"];',
             's6 -> s2 [label=" no: rethink the model\\n and its data", style=dashed, color="#b45309", '
             'fontcolor="#b45309", constraint=false];',
             's7 -> s8; s8 -> s9;',
             's9 -> s8 [label=" yes", style=dashed, color="#b45309", fontcolor="#b45309", constraint=false];',
             's9 -> s10 [label=" no"]; s10 -> s11;']
    dot_graph(body, 'ss-simulation-study.svg',
              'A flowchart of the twelve steps of a simulation study in four phases: planning (problem formulation, '
              'objectives), building (conceptualisation, data collection, translation, verification, validation), '
              'running (experimental design, production runs, more runs) and reporting (documentation, '
              'implementation), with loops back from verification to translation, from validation to '
              'conceptualisation and data collection, and from more runs to production runs')


def queue_configurations():
    s = Svg(760, 250, 'Three queue configurations side by side: one line of customers feeding one server; one line '
                      'feeding three servers; and three separate lines each feeding its own server')
    titles = ['Single queue, single server', 'Single queue, multiple servers', 'Multiple queues, multiple servers']

    def people(x, y, n):
        for k in range(n):
            s.circle(x - k * 18, y, 6, PIX)

    def server(x, y):
        s.rect(x - 14, y - 12, 28, 24, '#d1fae5', stroke=INK, width=1.2)

    for col, t in enumerate(titles):
        x0 = 20 + col * 250
        s.text(x0 + 110, 30, t, size=12, weight='bold')
        if col == 0:
            people(x0 + 120, 125, 5)
            s.line(x0 + 130, 125, x0 + 168, 125)
            server(x0 + 185, 125)
        elif col == 1:
            people(x0 + 100, 125, 5)
            for k, y in enumerate((75, 125, 175)):
                s.line(x0 + 110, 125, x0 + 168, y)
                server(x0 + 185, y)
        else:
            for y in (75, 125, 175):
                people(x0 + 120, y, 3)
                s.line(x0 + 130, y, x0 + 168, y)
                server(x0 + 185, y)
    s.circle(40, 225, 6, PIX)
    s.text(52, 229, 'customer', size=11, anchor='start')
    s.rect(126, 215, 22, 20, '#d1fae5', stroke=INK, width=1.2)
    s.text(156, 229, 'server', size=11, anchor='start')
    s.save('ss-queue-configurations.svg', OUT)


def timeline(rows, name, title, tmax):
    n = len(rows)
    s = Svg(620, 70 + 42 * n + 50, title)
    p = Plot(s, 110, 30, 470, 42 * n, 0, tmax, 0, n)
    for t in range(0, tmax + 1, 2):
        x, _ = p.P(t, 0)
        s.line(x, p.top, x, p.top + p.h, color=GRID, width=0.8)
        s.text(x, p.top + p.h + 16, str(t), size=11, color='#374151')
    s.line(p.left, p.top + p.h, p.left + p.w, p.top + p.h, width=1.5)
    s.text(p.left + p.w / 2, p.top + p.h + 36, 'time (minutes)', size=12)
    for i, (a, start, svc, dep, wait, _) in enumerate(rows):
        yc = p.top + 42 * i + 21
        s.text(p.left - 10, yc + 4, f'customer {i + 1}', size=12, anchor='end')
        xa, _ = p.P(a, 0)
        xs, _ = p.P(start, 0)
        xd, _ = p.P(dep, 0)
        if wait:
            s.rect(xa, yc - 9, xs - xa, 18, GREY, opacity=0.6)
        s.rect(xs, yc - 9, xd - xs, 18, PIX)
        s.text((xs + xd) / 2, yc + 4, f'{start}–{dep}', size=11, color='#ffffff', weight='bold')
        s.circle(xa, yc, 3.5, INK)
    yl = p.top + p.h + 52
    s.rect(110, yl - 10, 22, 12, GREY, opacity=0.6)
    s.text(138, yl, 'waiting', size=11, anchor='start')
    s.rect(210, yl - 10, 22, 12, PIX)
    s.text(238, yl, 'in service', size=11, anchor='start')
    s.circle(330, yl - 4, 3.5, INK)
    s.text(340, yl, 'arrival', size=11, anchor='start')
    s.save(name, OUT)


def mm1_curve():
    s = Svg(560, 380, 'A curve of the average number in an M/M/1 system against utilisation: L is 1 at rho 0.5, 4 at '
                      'rho 0.8 and 9 at rho 0.9, rising steeply towards infinity as rho approaches 1')
    p = Plot(s, 90, 30, 420, 280, 0, 1, 0, 20)
    p.axes([0, 0.2, 0.4, 0.6, 0.8, 1.0], range(0, 21, 5), 'utilisation ρ', 'average number in system L',
           xfmt=lambda v: f'{v:.1f}')
    pts = [(r / 1000, (r / 1000) / (1 - r / 1000)) for r in range(0, 953, 4)]
    p.curve(pts, PIX)
    for r in (0.5, 0.8, 0.9):
        L = r / (1 - r)
        p.dot(r, L, TRUE)
        x, y = p.P(r, L)
        s.text(x - 8, y - 8, f'ρ = {r}: L = {L:.0f}', size=11, anchor='end', weight='bold')
    x, _ = p.P(1, 0)
    s.line(x, p.top, x, p.top + p.h, color=TRUE, width=1.2, dash='5 4')
    s.save('ss-mm1-curve.svg', OUT)


def ks_test():
    nums = sorted([0.44, 0.81, 0.14, 0.05, 0.93])
    dp, _ = ks(nums)
    s = Svg(540, 400, 'The empirical cdf of the five numbers 0.05, 0.14, 0.44, 0.81 and 0.93 drawn as a staircase '
                      'against the straight uniform cdf; the largest gap, D plus of 0.26, sits just after 0.14, where '
                      'the staircase is at 0.4 and the line at 0.14')
    p = Plot(s, 80, 30, 400, 300, 0, 1, 0, 1)
    p.axes([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0], 'value', 'cumulative fraction',
           xfmt=lambda v: f'{v:.1f}', yfmt=lambda v: f'{v:.1f}')
    p.curve([(0, 0), (1, 1)], GREY, dash='6 4')
    pts, y = [(0, 0)], 0
    for i, x in enumerate(nums):
        pts += [(x, y), (x, (i + 1) / 5)]
        y = (i + 1) / 5
    pts.append((1, 1))
    p.curve(pts, PIX)
    x1, y1 = p.P(0.14, 0.14)
    x2, y2 = p.P(0.14, 0.4)
    s.line(x1, y1, x2, y2, color=TRUE, width=3)
    s.text(x2 + 8, (y1 + y2) / 2 + 4, f'D⁺ = {dp:.2f}', size=12, color=TRUE, anchor='start', weight='bold')
    s.text(*p.P(0.66, 0.4), 'uniform cdf F(x) = x', size=11, color='#6b7280')
    s.text(*p.P(0.3, 0.75), 'empirical cdf', size=11, color=PIX, weight='bold')
    s.save('ss-ks-test.svg', OUT)


def inverse_transform():
    mean, r = 2, 0.6
    x = expo(mean, r)
    s = Svg(540, 380, 'The exponential cdf with mean 2 rising from 0 towards 1; a horizontal line from R equal to 0.6 '
                      'on the vertical axis meets the curve and drops to X equal to 1.83 on the horizontal axis')
    p = Plot(s, 80, 30, 400, 280, 0, 8, 0, 1)
    p.axes(range(0, 9), [0, 0.2, 0.4, 0.6, 0.8, 1.0], 'x (minutes)', 'F(x)', yfmt=lambda v: f'{v:.1f}')
    p.curve([(t / 20, 1 - math.exp(-(t / 20) / mean)) for t in range(0, 161)], PIX)
    p.curve([(0, r), (x, r)], TRUE, width=2, dash='5 3')
    p.curve([(x, r), (x, 0)], TRUE, width=2, dash='5 3')
    p.dot(x, r, TRUE)
    s.text(*p.P(0.15, r + 0.04), 'R = 0.6', size=12, color=TRUE, anchor='start', weight='bold')
    xx, yy = p.P(x, 0)
    s.text(xx + 6, yy - 8, f'X = {x:.2f}', size=12, color=TRUE, anchor='start', weight='bold')
    s.save('ss-inverse-transform.svg', OUT)


def monte_carlo_area():
    rs = [0.12, 0.27, 0.35, 0.48, 0.55, 0.63, 0.71, 0.80, 0.88, 0.95]
    xs = [1 + 3 * r for r in rs]
    est = 3 * sum(math.sqrt(x) for x in xs) / len(xs)
    assert close(2 / 3 * (8 - 1), 14 / 3)
    s = Svg(540, 380, 'The curve square root of x from 1 to 4, with the true area of 4.67 shaded and ten sample '
                      'points marked on the curve at random x values; their average height times the width of 3 '
                      'gives the Monte Carlo estimate')
    p = Plot(s, 80, 30, 400, 280, 0, 4.5, 0, 2.5)
    p.axes([0, 1, 2, 3, 4], [0, 0.5, 1.0, 1.5, 2.0, 2.5], 'x', '√x', yfmt=lambda v: f'{v:.1f}')
    pts = [(1 + t / 40 * 3, math.sqrt(1 + t / 40 * 3)) for t in range(0, 41)]
    poly = [p.P(1, 0)] + [p.P(*q) for q in pts] + [p.P(4, 0)]
    s.add('<path d="M ' + ' L '.join(f'{a:.1f} {b:.1f}' for a, b in poly) + f' Z" fill="{ACCENT}" '
          'fill-opacity="0.15" stroke="none"/>')
    p.curve([(t / 20, math.sqrt(t / 20)) for t in range(0, 91)], PIX)
    for x in xs:
        p.curve([(x, 0), (x, math.sqrt(x))], ORANGE, width=1.2, dash='3 3')
        p.dot(x, math.sqrt(x), ORANGE, 3.5)
    s.text(*p.P(2.5, 0.6), f'true area 14/3 = {14 / 3:.2f}', size=12, color=ACCENT, weight='bold')
    s.text(*p.P(2.5, 0.35), f'these 10 points estimate {est:.2f}', size=11, color='#b45309')
    s.save('ss-monte-carlo-area.svg', OUT)


def histogram_shapes():
    s = Svg(760, 260, 'Three histogram shapes side by side: an exponential shape, tall on the left with a long tail '
                      'to the right; a normal shape, a symmetric hump; and a uniform shape, roughly flat across its '
                      'range')
    shapes = [('exponential', [math.exp(-k / 2.2) for k in range(10)]),
              ('normal', [math.exp(-((k - 4.5) ** 2) / 4) for k in range(10)]),
              ('uniform', [0.62, 0.58, 0.65, 0.6, 0.57, 0.63, 0.61, 0.59, 0.64, 0.6])]
    for col, (name, hs) in enumerate(shapes):
        x0 = 30 + col * 245
        s.text(x0 + 100, 30, name, size=13, weight='bold')
        for k, h in enumerate(hs):
            bh = 160 * h / max(hs) * (0.62 if name == 'uniform' else 1)
            s.rect(x0 + k * 20, 210 - bh, 18, bh, PIX)
        s.line(x0 - 4, 210, x0 + 204, 210)
    s.save('ss-histogram-shapes.svg', OUT)


def credibility():
    s = Svg(560, 380, 'Two curves against the amount of validation effort: the utility of the model rises quickly at '
                      'first and then levels off, while the cost rises slowly at first and then faster and faster; the '
                      'best point is where the gap between utility and cost is largest')
    p = Plot(s, 80, 30, 420, 280, 0, 10, 0, 10)
    p.axes([], [], 'validation effort (credibility bought)', 'value or cost')

    def u(t): return 8 * (1 - math.exp(-t / 2.5))

    def c(t): return 0.08 * t * t

    p.curve([(t / 10, u(t / 10)) for t in range(0, 101)], ACCENT)
    p.curve([(t / 10, c(t / 10)) for t in range(0, 101)], TRUE)
    best = max((t / 100 for t in range(0, 1001)), key=lambda t: u(t) - c(t))
    x, y1 = p.P(best, u(best))
    _, y2 = p.P(best, c(best))
    s.line(x, y1, x, y2, color=ORANGE, width=3)
    s.text(x + 8, (y1 + y2) / 2, 'biggest gap:', size=11, color='#b45309', anchor='start', weight='bold')
    s.text(x + 8, (y1 + y2) / 2 + 15, 'stop here', size=11, color='#b45309', anchor='start', weight='bold')
    s.text(*p.P(8.6, 7.4), 'utility', size=12, color=ACCENT, weight='bold')
    s.text(*p.P(8.9, 5.6), 'cost', size=12, color=TRUE, weight='bold')
    s.save('ss-credibility.svg', OUT)


def activity_diagram():
    s = Svg(620, 230, 'An activity diagram of a single-server queue: a zigzag arrival line feeds a queue drawn as a '
                      'circle, which feeds a service activity drawn as a rectangle, which leads to a zigzag departure '
                      'line; a small circle for the server resource is joined to the service rectangle by dashed seize '
                      'and release arrows')

    def zigzag(x, y):
        d = f'M {x} {y} ' + ' '.join(f'L {x + 8 * k} {y + (8 if k % 2 else -8)}' for k in range(1, 7))
        s.path(d, INK, width=2)

    zigzag(30, 140)
    s.text(55, 120, 'arrive', size=11)
    s.line(80, 140, 150, 140, width=1.8)
    s.circle(185, 140, 32, '#fef3c7', INK)
    s.text(185, 145, 'queue', size=12)
    s.line(217, 140, 290, 140, width=1.8)
    s.rect(290, 112, 130, 56, '#dbeafe', stroke=INK, width=1.4)
    s.text(355, 145, 'service', size=12)
    s.line(420, 140, 490, 140, width=1.8)
    zigzag(490, 140)
    s.text(515, 120, 'leave', size=11)
    s.circle(355, 45, 14, '#d1fae5', INK)
    s.text(380, 49, 'server', size=11, anchor='start')
    s.line(340, 58, 320, 112, dash='5 4', width=1.4)
    s.text(300, 85, 'seize', size=11, anchor='end')
    s.line(370, 58, 390, 112, dash='5 4', width=1.4)
    s.text(410, 85, 'release', size=11, anchor='start')
    s.save('ss-activity-diagram.svg', OUT)


def gpss_drill():
    blocks = ['GENERATE 15,4.5', 'QUEUE DRILLQUE', 'SEIZE DRILL', 'DEPART DRILLQUE', 'ADVANCE 13.5,3',
              'RELEASE DRILL', 'TERMINATE 1']
    body = [f'b{i} [label="{b}", width=2.4];' for i, b in enumerate(blocks)]
    body += [f'b{i} -> b{i + 1};' for i in range(len(blocks) - 1)]
    dot_graph(body, 'ss-gpss-drill.svg',
              'A block diagram of the drill model: GENERATE 15,4.5 flows to QUEUE, SEIZE the drill, DEPART, ADVANCE 13.5,3, RELEASE the drill and TERMINATE 1')


def gpss_telephone():
    body = ['g [label="GENERATE 1.667,1"];',
            'gate [label="Again: GATE SNF Sets\\n(a line free?)", shape=diamond, style="filled", fillcolor="#fef3c7"];',
            'en [label="ENTER Sets"]; adv [label="ADVANCE 3,1  (talk)"]; lv [label="LEAVE Sets"];',
            'tab [label="TABULATE Transit"]; term [label="TERMINATE 1"];',
            'occ [label="Occupied: ADVANCE 5,1\\n(wait to redial)", fillcolor="#fde68a"];',
            'tr [label="TRANSFER ,Again", fillcolor="#fde68a"];',
            'g -> gate; gate -> en [label=" yes"]; en -> adv; adv -> lv; lv -> tab; tab -> term;',
            'gate -> occ [label=" no, both busy"]; occ -> tr;',
            f'tr -> gate [style=dashed, color="#b45309", constraint=false];']
    dot_graph(body, 'ss-gpss-telephone.svg',
              'A block diagram of the telephone model: GENERATE flows to a GATE that checks whether the two-line '
              'storage is full; if a line is free the call goes through ENTER, ADVANCE 3,1, LEAVE, TABULATE and '
              'TERMINATE; if both are busy it goes to ADVANCE 5,1 for the redial wait and TRANSFERs back to the GATE')


def production_control():
    body = ['subgraph cluster_p { label="Production side"; fontname="%s"; fontsize=12; style="rounded,dashed"; color="%s";' % (FONT, GREY),
            'prod [label="Produce a batch of 5\\n(10–20 min per unit,\\nbreakdowns and repairs)"];',
            'full [label="Stock at 500?", shape=diamond, style="filled", fillcolor="#fef3c7"];',
            'block [label="Production blocked\\nuntil stock falls to 150", fillcolor="#e5e7eb"];',
            'prod -> full; full -> block [label=" yes"]; }',
            'wh [label="Warehouse stock", fillcolor="#d1fae5", width=2];',
            'subgraph cluster_c { label="Customer side"; fontname="%s"; fontsize=12; style="rounded,dashed"; color="%s";' % (FONT, GREY),
            'cust [label="Customer arrives\\n(every 3–7 h, wants 50–100)"];',
            'enough [label="Stock covers\\nthe demand?", shape=diamond, style="filled", fillcolor="#fef3c7"];',
            'ship [label="Serve in full", fillcolor="#d1fae5"];',
            'lost [label="Serve part and lose the rest,\\nor lose the whole order", fillcolor="#fee2e2"];',
            'cust -> enough; enough -> ship [label=" yes"]; enough -> lost [label=" no"]; }',
            'full -> prod [label=" no", constraint=false];',
            'block -> prod [label=" stock ≤ 150", style=dashed, color="#b45309", fontcolor="#b45309", constraint=false];',
            'prod -> wh [label=" adds stock", constraint=false]; wh -> enough [label=" checked", style=dashed];']
    dot_graph(body, 'ss-production-control.svg',
              'A flowchart of the production control logic: production adds batches to the warehouse until stock '
              'reaches 500, when production is blocked until stock falls to 150; a customer arrival checks whether '
              'stock covers the demand and is either served in full or partly served or lost')


def vv_chain():
    body = ['real [label="Real system", fillcolor="#e5e7eb", width=2.6];',
            'conc [label="Conceptual model\\n(assumptions, structure)", width=2.6];',
            'comp [label="Computerised model\\n(the program)", fillcolor="#d1fae5", width=2.6];',
            'real -> conc [label="  observe and abstract"]; conc -> comp [label="  program it"];',
            f'v [shape=plaintext, style="", label="verification:\\nbuilt right?", fontcolor="{PIX}"];',
            f'w [shape=plaintext, style="", label="validation:\\nthe right model?", fontcolor="{ACCENT}"];',
            '{ rank=same; conc; v; } { rank=same; real; w; }',
            f'v -> conc [dir=none, style=dashed, color="{PIX}"]; v -> comp [style=dashed, color="{PIX}"];',
            f'w -> real [dir=none, style=dashed, color="{ACCENT}"]; w -> comp [style=dashed, color="{ACCENT}", constraint=false];']
    dot_graph(body, 'ss-vv-chain.svg',
              'A chain from the real system to the conceptual model to the computerised model; verification checks '
              'the step from the conceptual model to the computerised model, and validation checks the computerised '
              'model against the real system')


def calibration_loop():
    body = ['run [label="Run the model"];', 'cmp [label="Compare its output\\nwith the real system"];',
            'ok [label="Gap within\\ntolerance?", shape=diamond, style="filled", fillcolor="#fef3c7"];',
            'stop [label="Stop: test on held-back data,\\nrecord the bounds of validity", fillcolor="#d1fae5"];',
            'find [label="Find the discrepancy"];', 'adj [label="Adjust an assumption\\nor a parameter"];',
            'run -> cmp; cmp -> ok; ok -> stop [label=" yes"]; ok -> find [label=" no"]; find -> adj;',
            f'adj -> run [style=dashed, color="#b45309", constraint=false];']
    dot_graph(body, 'ss-calibration-loop.svg',
              'A loop: run the model, compare its output with the real system, and if the gap is within tolerance '
              'stop; otherwise find the discrepancy, adjust an assumption or parameter, and run again')


def arena_bank():
    body = ['c [label="CREATE\\nCustomers arrive\\nEXPO(5) min", shape=box, fillcolor="#fef3c7"];',
            'p [label="PROCESS\\nTeller serves\\nseize, delay NORM(4,1), release", fillcolor="#dbeafe"];',
            'd [label="DISPOSE\\nCustomers leave", fillcolor="#fee2e2"];', 'c -> p; p -> d;']
    dot_graph(body, 'ss-arena-bank.svg',
              'An Arena flowchart for the bank: a CREATE module named Customers arrive, with EXPO(5), connected to a '
              'PROCESS module named Teller serves, with seize, delay NORM(4,1) and release, connected to a DISPOSE '
              'module named Customers leave', rankdir='LR')


def arena_airport():
    body = ['c [label="CREATE\\nPassengers arrive\\nEXPO(2) min", fillcolor="#fef3c7"];',
            'p [label="PROCESS\\nID check\\nTRIA(0.75, 1.5, 3)", fillcolor="#dbeafe"];',
            'd [label="DECIDE\\n2-way by chance", shape=diamond, style="filled", fillcolor="#fde68a"];',
            'ok [label="DISPOSE\\nCleared", fillcolor="#d1fae5"];',
            'no [label="DISPOSE\\nDenied", fillcolor="#fee2e2"];',
            'c -> p; p -> d; d -> ok [label=" 93%"]; d -> no [label=" 7%"];']
    dot_graph(body, 'ss-arena-airport.svg',
              'An Arena flowchart for airport security: CREATE with EXPO(2) feeds a PROCESS ID check with TRIA(0.75, '
              '1.5, 3), which feeds a DECIDE that sends 93 percent to a DISPOSE for cleared passengers and 7 percent '
              'to a DISPOSE for denied passengers', rankdir='LR')


if __name__ == '__main__':
    check_lessons()
    ways_to_study()
    simulation_study()
    queue_configurations()
    timeline(hand_sim([2, 5, 6, 10], [4, 3, 5, 2]), 'ss-hand-simulation.svg',
             'A timeline of the four-customer hand simulation from minute 0 to 16: customer 1 is served from 2 to 6 '
             'with no wait; customer 2 waits from 5 to 6 and is served 6 to 9; customer 3 waits 6 to 9 and is served '
             '9 to 14; customer 4 waits 10 to 14 and is served 14 to 16', 16)
    timeline(hand_sim([1, 3, 4, 10], [3, 4, 2, 2]), 'ss-hand-simulation-quiz.svg',
             'A timeline of the quiz run from minute 0 to 12: customer 1 is served 1 to 4; customer 2 waits 3 to 4 '
             'and is served 4 to 8; customer 3 waits 4 to 8 and is served 8 to 10; customer 4 is served 10 to 12 '
             'with no wait', 12)
    mm1_curve()
    ks_test()
    inverse_transform()
    monte_carlo_area()
    histogram_shapes()
    credibility()
    activity_diagram()
    gpss_drill()
    gpss_telephone()
    production_control()
    vv_chain()
    calibration_loop()
    arena_bank()
    arena_airport()
