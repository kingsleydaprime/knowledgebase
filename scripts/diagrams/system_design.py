"""Draw the system-design (architecture/) lesson diagrams as small SVG files.

    python3 scripts/diagrams/system_design.py      # run from the vault root

Boxes-and-arrows pictures (request paths, replication, queues, patterns) are laid
out by Graphviz (`dot`, which must be installed). Timelines and message sequences
(Lamport and vector clocks, 2PC, Raft, sagas, the outbox) are drawn by hand with
the Svg class. Anything with numbers in it (clock values, hash ring placement,
quorum overlaps, gossip rounds, queueing delay) is computed here from the same
rules the lessons teach, and checked against the lesson's numbers before it is
drawn. Output: architecture/images/sd-*.svg.
"""
import hashlib
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, PIX, PIX2, TRUE, ACCENT, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('architecture', 'images')
ORANGE = '#f59e0b'
GREY = '#6b7280'
MUTED = '#4b5563'

# Fill colours for the kinds of box in an architecture picture.
FILL = {'client': '#f3f4f6', 'svc': '#dbeafe', 'db': '#d1fae5', 'cache': '#fef3c7',
        'queue': '#fde68a', 'lb': '#e0e7ff', 'bad': '#fee2e2', 'note': '#ffffff'}


# ---------------------------------------------------------------- helpers

def arch(name, title, body, rankdir='LR', nodesep=0.35, ranksep=0.45, extra=''):
    """A Graphviz picture. In `body`, give nodes a class with K(kind)."""
    src = (f'digraph {{ bgcolor="white"; pad=0.25; rankdir={rankdir}; nodesep={nodesep}; ranksep={ranksep}; '
           f'newrank=true; {extra}\n'
           f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", fillcolor="{FILL["svc"]}", '
           f'color="{INK}", penwidth=1.3, margin="0.15,0.06"];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151", arrowsize=0.8];\n'
           f'{body}\n}}')
    save_dot(src, 'sd-' + name, title, OUT)


def K(kind, **kw):
    """Attribute string for a node of one kind (db nodes are cylinders)."""
    a = {'fillcolor': FILL[kind]}
    if kind == 'db':
        a['shape'] = 'cylinder'
    if kind == 'client':
        a['style'] = 'filled'
        a['shape'] = 'box'
    if kind == 'queue':
        a['shape'] = 'box'
        a['style'] = 'filled'
    a.update(kw)
    return '[' + ', '.join(f'{k}="{v}"' for k, v in a.items()) + ']'


def arrow_defs(s, colors=(INK, PIX, TRUE, ORANGE, ACCENT, GREY, '#b45309')):
    s.add('<defs>' + ''.join(
        f'<marker id="a{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for i, c in enumerate(colors))
        + '</defs>')
    return {c: f'url(#a{i})' for i, c in enumerate(colors)}


def arrow(s, mk, x1, y1, x2, y2, color=INK, width=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
          f'stroke-width="{width}" marker-end="{mk[color]}"{d}/>')


def box(s, x, y, w, h, fill, label, sub=None, stroke=INK, width=1.3, size=13):
    s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" fill="{fill}" '
          f'stroke="{stroke}" stroke-width="{width}"/>')
    if sub:
        s.text(x + w / 2, y + h / 2 - 3, label, size, weight='bold')
        s.text(x + w / 2, y + h / 2 + 13, sub, size - 2.5, color=MUTED)
    else:
        s.text(x + w / 2, y + h / 2 + size * 0.35, label, size, weight='bold')


class Seq:
    """A message-sequence diagram: one vertical lifeline per actor, time runs down.

    msg(a, b, label, t) draws an arrow from actor a to actor b leaving at row t
    (arriving at row t + slope). note(a, t, text) writes beside a lifeline."""

    def __init__(self, actors, rows, title, col=150, row=34, left=20, top=56, right=20, lw=None):
        self.actors = actors
        self.col, self.row, self.left, self.top = col, row, left, top
        w = left + col * len(actors) + right
        h = top + row * rows + 20
        self.s = Svg(w, h, title)
        self.mk = arrow_defs(self.s)
        for i, a in enumerate(actors):
            x = self.x(i)
            self.s.line(x, top - 6, x, h - 14, '#9ca3af', 1.2, dash='4 4')
            box(self.s, x - col / 2 + 10, 10, col - 20, 32, FILL['svc'] if lw is None else lw.get(a, FILL['svc']), a)

    def x(self, i):
        if isinstance(i, str):
            i = self.actors.index(i)
        return self.left + self.col * (i + 0.5)

    def y(self, t):
        return self.top + self.row * t

    def msg(self, a, b, label, t, slope=0.6, color=INK, dash=None, size=11.5, lab_dy=-5):
        x1, x2 = self.x(a), self.x(b)
        y1, y2 = self.y(t), self.y(t + slope)
        sgn = 1 if x2 > x1 else -1
        arrow(self.s, self.mk, x1, y1, x2 - sgn * 3, y2, color, 1.6, dash)
        # label sits above the arrow, near its middle
        self.s.text((x1 + x2) / 2, y1 + lab_dy, label, size, color=color if color != INK else '#111827')

    def self_note(self, a, t, text, color=INK, anchor='start', dx=8, size=11.5, weight='normal'):
        x = self.x(a)
        self.s.text(x + (dx if anchor == 'start' else -dx if anchor == 'end' else 0), self.y(t) + 4, text, size,
                    color=color, anchor=anchor, weight=weight)

    def dot(self, a, t, color=INK, r=4.5):
        self.s.circle(self.x(a), self.y(t), r, color)

    def band(self, t0, t1, text, fill='#f3f4f6'):
        self.s.rect(4, self.y(t0), self.s.w - 8, self.y(t1) - self.y(t0), fill)
        self.s.text(8, self.y(t0) + 13, text, 11, color=MUTED, anchor='start', weight='bold')

    def save(self, name):
        self.s.save('sd-' + name, OUT)


class Timeline:
    """Processes as horizontal lines, time running right; messages are diagonal arrows."""

    def __init__(self, procs, width, title, left=56, top=34, gap=78, height=None):
        self.procs, self.left, self.top, self.gap = procs, left, top, gap
        h = height or top + gap * (len(procs) - 1) + 48
        self.s = Svg(width, h, title)
        self.mk = arrow_defs(self.s)
        for i, p in enumerate(procs):
            y = self.y(p)
            self.s.text(left - 12, y + 5, p, 14, anchor='end', weight='bold')
            arrow(self.s, self.mk, left, y, width - 14, y, GREY, 1.4)

    def y(self, p):
        return self.top + self.gap * self.procs.index(p)

    def event(self, p, x, label, color=INK, above=True, size=12, weight='bold', fill=None):
        y = self.y(p)
        self.s.circle(x, y, 5.5, fill or color)
        self.s.text(x, y - 11 if above else y + 21, label, size, color=color, weight=weight)

    def message(self, p1, x1, p2, x2, label=None, color=PIX):
        y1, y2 = self.y(p1), self.y(p2)
        k = 7 / math.hypot(x2 - x1, y2 - y1)
        arrow(self.s, self.mk, x1, y1, x2 - (x2 - x1) * k, y2 - (y2 - y1) * k, color, 1.6)
        if label:
            self.s.text((x1 + x2) / 2 + 8, (y1 + y2) / 2, label, 11.5, color=color, anchor='start')

    def save(self, name):
        self.s.save('sd-' + name, OUT)


class Plot:
    """Data coordinates to SVG pixels, with axes, ticks and labels (as in machine_learning.py)."""

    def __init__(self, s, x0, y0, w, h, xr, yr):
        self.s, self.x0, self.y0, self.w, self.h, self.xr, self.yr = s, x0, y0, w, h, xr, yr

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def axes(self, xlabel, ylabel, xticks=(), yticks=(), xfmt='{:g}', yfmt='{:g}'):
        s = self.s
        for t in xticks:
            s.line(self.X(t), self.y0, self.X(t), self.y0 + self.h, '#eef2f6', 1)
            s.text(self.X(t), self.y0 + self.h + 16, xfmt.format(t), 11)
        for t in yticks:
            s.line(self.x0, self.Y(t), self.x0 + self.w, self.Y(t), '#eef2f6', 1)
            s.text(self.x0 - 8, self.Y(t) + 4, yfmt.format(t), 11, anchor='end')
        s.line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, INK, 1.2)
        s.line(self.x0, self.y0, self.x0, self.y0 + self.h, INK, 1.2)
        s.text(self.x0 + self.w / 2, self.y0 + self.h + 34, xlabel, 12)
        s.add(f'<text x="{self.x0 - 42:.1f}" y="{self.y0 + self.h / 2:.1f}" font-size="12" fill="{INK}" '
              f'text-anchor="middle" font-family="system-ui, sans-serif" '
              f'transform="rotate(-90 {self.x0 - 42:.1f} {self.y0 + self.h / 2:.1f})">{ylabel}</text>')

    def curve(self, pts, color, width=2.5, dash=None):
        self.s.path('M ' + ' L '.join(f'{self.X(x):.1f} {self.Y(y):.1f}' for x, y in pts), color, width, dash=dash)

    def dot(self, x, y, color, r=4.5):
        self.s.circle(self.X(x), self.Y(y), r, color)


# ======================================================= 01 fundamentals

def leaderboard():
    arch('leaderboard-design.svg',
         'Leaderboard high-level design: a player calls the load balancer, which spreads requests over stateless '
         'API servers; the API servers write every score to the scores database and update an in-memory ranking store',
         f'''
         p [label="player"] {K('client')};
         lb [label="load balancer"] {K('lb')};
         api [label="API servers\\n(stateless: any one\\ncan serve any request)"];
         db [label="scores database\\nscores, best_scores\\n(durable: every score)"] {K('db')};
         rk [label="ranking store (in memory)\\nbest score per player\\n(top 100, my rank)"] {K('cache')};
         p -> lb -> api;
         api -> db [label=" 1. save "];
         api -> rk [label=" 2. update rank "];
         ''')


def fenwick():
    # Scores 0..7 live at Fenwick indexes 1..8. Cell i covers the lowbit(i) indexes ending at i.
    n = 8
    cover = {i: (i - (i & -i) + 1, i) for i in range(1, n + 1)}
    # "counting those at most 5 adds cell 6 (scores 4-5) and cell 4 (scores 0-3)"
    used, i = [], 5 + 1
    while i > 0:
        used.append(i)
        i -= i & -i
    assert used == [6, 4]
    assert cover[6] == (5, 6) and cover[4] == (1, 4)       # indexes 5-6 = scores 4-5; 1-4 = scores 0-3
    cw, left, top = 52, 92, 40
    s = Svg(left + cw * n + 24, 300, 'Fenwick tree for scores 0 to 7: each cell counts players in a power-of-two '
            'range of scores; counting players scoring at most 5 adds cell 6 (scores 4 to 5) and cell 4 (scores 0 to 3)')
    s.text(left - 10, top - 14, 'score', 12, anchor='end', color=MUTED)
    for sc in range(n):
        s.rect(left + sc * cw, top - 30, cw, 22, '#f3f4f6', '#9ca3af')
        s.text(left + sc * cw + cw / 2, top - 14, sc, 13, weight='bold')
    levels = {1: 0, 2: 1, 4: 2, 8: 3}
    for i, (a, b) in cover.items():
        lvl = levels[b - a + 1]
        y = top + 14 + lvl * 44
        x0, x1 = left + (a - 1) * cw + 3, left + b * cw - 3
        hot = i in used
        fill = '#fed7aa' if hot else FILL['svc']
        s.add(f'<rect x="{x0:.1f}" y="{y}" width="{x1 - x0:.1f}" height="30" rx="6" fill="{fill}" '
              f'stroke="{ORANGE if hot else INK}" stroke-width="{2.6 if hot else 1.2}"/>')
        rng = f'{a - 1}' if a == b else f'{a - 1}–{b - 1}'
        s.text((x0 + x1) / 2, y + 20, f'cell {i}: scores {rng}' if b - a >= 1 else f'cell {i}', 11.5,
               weight='bold' if hot else 'normal')
    for lvl, sz in enumerate((1, 2, 4, 8)):
        s.text(left - 10, top + 34 + lvl * 44, f'{sz} score{"s" if sz > 1 else ""}', 11, anchor='end', color=MUTED)
    s.text(left + cw * n / 2, 250, 'players scoring at most 5 = cell 6 + cell 4', 14, color='#b45309', weight='bold')
    s.text(left + cw * n / 2, 272, 'two cells instead of six scores', 12, color=MUTED)
    s.save('sd-fenwick-cells.svg', OUT)


def photo_app_sketch():
    arch('sketch-photo-app.svg',
         'Answer sketch for a photo-sharing app: clients reach a load balancer and stateless API servers; photo bytes '
         'go to object storage served through a CDN; photo metadata goes to a database; a cache holds hot feed reads',
         f'''
         u [label="phone app"] {K('client')};
         cdn [label="CDN\\n(serves photo files)"] {K('lb')};
         lb [label="load balancer"] {K('lb')};
         api [label="API servers\\n(stateless)"];
         obj [label="object storage\\nphoto files"] {K('db')};
         db [label="metadata database\\nphotos, users, follows"] {K('db')};
         c [label="cache\\nhot feeds"] {K('cache')};
         u -> lb -> api;
         u -> cdn [label=" GET image "];
         cdn -> obj [label=" on a miss "];
         api -> obj [label=" upload "];
         api -> db; api -> c;
         {{rank=same; lb; cdn}}
         ''')


def waiting_curve():
    S = 10                                   # ms of work per request
    T = lambda rho: S / (1 - rho)
    table = {0.5: 20, 0.8: 50, 0.9: 100, 0.95: 200, 0.99: 1000}
    for rho, t in table.items():
        assert abs(T(rho) - t) < 1e-6
    s = Svg(520, 340, 'Average time in a server against utilisation for 10 ms of work, from T = S / (1 - rho): '
            '20 ms at 50 percent busy, 50 ms at 80, 100 ms at 90, 200 ms at 95 and 1 second at 99')
    p = Plot(s, 78, 24, 400, 240, (0, 1), (0, 1050))
    p.axes('utilisation (how busy the server is)', 'average time (ms)', xticks=(0, 0.2, 0.4, 0.6, 0.8, 1.0),
           yticks=(0, 200, 400, 600, 800, 1000), xfmt='{:.0%}')
    p.curve([(r / 1000, T(r / 1000)) for r in range(0, 991)], PIX)
    s.rect(p.X(0.5), p.y0, p.X(0.7) - p.X(0.5), p.h, ACCENT, opacity=0.10)
    s.text(p.X(0.6), p.y0 + 16, 'run here', 11, ACCENT, weight='bold')
    s.text(p.X(0.6), p.y0 + 30, 'at peak', 11, ACCENT, weight='bold')
    for rho, t in table.items():
        p.dot(rho, t, ORANGE)
    labels = {0.5: ('20 ms', 0, -12), 0.8: ('50 ms', -6, -12), 0.9: ('100 ms', -10, -6), 0.95: ('200 ms', -10, 0),
              0.99: ('1 s', -10, 4)}
    for rho, (lab, dx, dy) in labels.items():
        s.text(p.X(rho) + dx, p.Y(table[rho]) + dy, lab, 11, weight='bold', anchor='end' if dx else 'middle')
    s.save('sd-waiting-curve.svg', OUT)


def checkout_bottleneck():
    stages = [('load balancer', 50_000), ('app servers (4 x 800)', 4 * 800), ('database writes', 2_000)]
    assert stages[1][1] == 3_200
    cap = min(c for _, c in stages)
    assert cap == 2_000
    body = ['u [label="customers" ' + K('client')[1:] + ';']
    prev = 'u'
    for i, (name, c) in enumerate(stages):
        hot = c == cap
        attrs = K('db' if 'database' in name else ('lb' if 'balancer' in name else 'svc'),
                  **({'color': TRUE, 'penwidth': '3'} if hot else {}))
        body.append(f'n{i} [label="{name}\n{c:,} a second"] {attrs};')
        body.append(f'{prev} -> n{i};')
        prev = f'n{i}'
    body.append(f'note [label="the slowest stage sets the\nwhole path: 2,000 a second", shape=plaintext, '
                f'style="", fontcolor="{TRUE}"]; n2 -> note [style=invis];')
    arch('checkout-bottleneck.svg',
         'The checkout path with each stage\'s capacity: load balancer 50,000 a second, four app servers 3,200 a '
         'second, database writes 2,000 a second; the database is the bottleneck, so the whole path handles 2,000',
         '\n'.join(body))


def scaling_ceiling():
    alpha, beta, s_ = 0.05, 0.001, 0.05
    usl = lambda n: n / (1 + alpha * (n - 1) + beta * n * (n - 1))
    amdahl = lambda n: 1 / (s_ + (1 - s_) / n)
    assert round(amdahl(8), 1) == 5.9
    peak = max(range(1, 121), key=usl)
    assert peak == 31 and round(usl(31)) == 9 and round(usl(60)) == 8 and round(usl(100), 1) == 6.3
    s = Svg(520, 340, 'Speed-up against number of machines: Amdahl\'s law with 5 percent that cannot be split rises '
            'towards 20; the universal scalability law with 5 percent contention and 0.1 percent coherence peaks at '
            'about 9 times near 31 machines and then falls')
    p = Plot(s, 70, 24, 410, 240, (0, 120), (0, 20))
    p.axes('number of machines', 'speed-up (times one machine)', xticks=(0, 20, 40, 60, 80, 100, 120),
           yticks=(0, 5, 10, 15, 20))
    p.curve([(n, n) for n in range(1, 21)], '#9ca3af', 1.4, '5 4')
    s.text(p.X(14) - 4, p.Y(15), 'perfect', 11, GREY, 'end')
    p.curve([(n, amdahl(n)) for n in range(1, 121)], PIX)
    p.curve([(n, usl(n)) for n in range(1, 121)], ORANGE)
    s.line(p.X(0), p.Y(20), p.X(120), p.Y(20), PIX, 1, '3 3')
    s.text(p.X(118), p.Y(17.2) - 8, "Amdahl: never above 20", 12, PIX, 'end', 'bold')
    p.dot(31, usl(31), TRUE)
    s.text(p.X(31), p.Y(usl(31)) - 12, 'peak: 9 times at 31 machines', 11.5, TRUE, 'start', 'bold')
    s.text(p.X(100), p.Y(usl(100)) + 18, 'USL: falls to 6.3 at 100', 12, ORANGE, 'middle', 'bold')
    s.save('sd-scaling-ceiling.svg', OUT)


def bottleneck_sketch():
    stages = [('CDN', 'lb', 80_000), ('load balancer', 'lb', 40_000), ('app servers (6 x 500)', 'svc', 3_000),
              ('cache reads', 'cache', 25_000), ('database writes', 'db', 1_200)]
    cap = min(c for *_, c in stages)
    assert cap == 1_200
    body = [f'u [label="users"] {K("client")};',
            f'cdn [label="CDN\n80,000 a second"] {K("lb")};',
            f'lb [label="load balancer\n40,000 a second"] {K("lb")};',
            f'app [label="app servers (6 x 500)\n3,000 a second"];',
            f'c [label="cache\n25,000 reads a second"] {K("cache")};',
            f'db [label="database\n1,200 writes a second"] {K("db", color=TRUE, penwidth="3")};',
            'u -> cdn [label=" images "]; u -> lb [label=" orders "]; lb -> app; app -> c [label=" reads "];',
            f'app -> db [label=" every order writes ", fontcolor="{TRUE}", color="{TRUE}", penwidth=2];']
    arch('sketch-bottleneck.svg',
         'Answer sketch: users fetch images from a CDN (80,000 a second) and send orders through a load balancer '
         '(40,000) to six app servers (3,000); servers read a cache (25,000) and every order writes to the database '
         '(1,200), which is the bottleneck circled in red', '\n'.join(body))


def series_parallel(name, title, chain, pair, pair_label, total_label=None):
    """Draw a chain of components in series, where `pair` (a list of replicas) sits in parallel at the end."""
    series = 1.0
    for _, a in chain:
        series *= a
    par = 1 - math.prod(1 - a for a in pair)
    total = series * par
    pc = lambda a: f'{a * 100:.2f}'.rstrip('0').rstrip('.') + '%'
    s = Svg(90 + 132 * len(chain) + 200, 250, title)
    mk = arrow_defs(s)
    x, y = 20, 92
    box(s, x, y, 70, 44, FILL['client'], 'user')
    x += 70
    for lab, a in chain:
        arrow(s, mk, x, y + 22, x + 26, y + 22)
        x += 28
        box(s, x, y, 104, 44, FILL['svc'], lab, pc(a))
        x += 104
    # the parallel pair
    arrow(s, mk, x, y + 22, x + 34, y - 18)
    arrow(s, mk, x, y + 22, x + 34, y + 62)
    for k, a in enumerate(pair):
        yy = y - 44 + k * 88
        box(s, x + 36, yy, 120, 44, FILL['db'], f'{pair_label} {k + 1}', f'{a:.0%} each')
    s.rect(x + 28, y - 52, 136, 148, 'none', ORANGE, 2)
    s.text(x + 96, y + 108, f'either one is enough: {par:.2%}', 11.5, '#b45309', weight='bold')
    s.text(20, 24, f'in a chain, availabilities multiply: {" x ".join(pc(a) for _, a in chain)} = {pc(series)}',
           13, anchor='start', weight='bold')
    s.text(20, 44, f'a pair fails only if both fail: 1 - {(1 - pair[0]):.2f} x {(1 - pair[1]):.2f} = {par:.2%}',
           13, anchor='start', weight='bold', color='#b45309')
    s.text(20, 236, total_label or f'whole path: {series:.2%} x {par:.2%} = {total:.2%}', 13, anchor='start',
           weight='bold', color=PIX)
    s.save('sd-' + name, OUT)
    return series, par, total


def availability_pictures():
    se, pa, tot = series_parallel(
        'availability-series-parallel.svg',
        'Availability in series and in parallel: a 99.9 percent service that calls three other 99.9 percent services '
        'is about 99.6 percent available; two 99 percent database replicas in parallel give 99.99 percent',
        [('web', 0.999), ('orders', 0.999), ('payments', 0.999), ('stock', 0.999)], [0.99, 0.99], 'database')
    assert round(se, 3) == 0.996 and round(pa, 4) == 0.9999
    se, pa, tot = series_parallel(
        'sketch-availability.svg',
        'Answer sketch: a load balancer at 99.99 percent and an API at 99.9 percent in a chain, then two cache '
        'replicas at 95 percent each in parallel; the chain is 99.89 percent, the pair 99.75 percent, the whole path '
        'about 99.64 percent',
        [('load balancer', 0.9999), ('API', 0.999)], [0.95, 0.95], 'replica')
    assert round(pa, 4) == 0.9975 and round(tot, 4) == 0.9964


def cap_partition():
    s = Svg(640, 300, 'A network partition between node A and node B: a client writes x = 2 to node A, which cannot '
            'reach node B; another client reads x from node B. A CP system answers with an error; an AP system '
            'answers with the old value x = 1')
    mk = arrow_defs(s)
    for k, (head, reply, col) in enumerate([('CP: refuse rather than be wrong', 'error: can\'t reach A', TRUE),
                                            ('AP: answer, maybe out of date', 'x = 1 (old value)', ORANGE)]):
        ox = 10 + k * 320
        s.text(ox + 150, 24, head, 14, col, weight='bold')
        box(s, ox + 20, 110, 100, 50, FILL['db'], 'node A', 'x = 2 (new)')
        box(s, ox + 190, 110, 100, 50, FILL['db'], 'node B', 'x = 1')
        # the broken link
        s.line(ox + 120, 135, ox + 190, 135, GREY, 1.6, '5 4')
        s.line(ox + 147, 123, ox + 163, 147, TRUE, 3)
        s.line(ox + 163, 123, ox + 147, 147, TRUE, 3)
        s.text(ox + 155, 112, 'partition', 11, TRUE)
        box(s, ox + 20, 220, 100, 36, FILL['client'], 'client 1')
        box(s, ox + 190, 220, 100, 36, FILL['client'], 'client 2')
        arrow(s, mk, ox + 70, 220, ox + 70, 163)
        s.text(ox + 76, 198, 'write x = 2', 11.5, anchor='start')
        arrow(s, mk, ox + 225, 220, ox + 225, 163)
        s.text(ox + 220, 198, 'read x', 11.5, anchor='end')
        arrow(s, mk, ox + 255, 163, ox + 255, 220, col)
        s.text(ox + 240, 280, reply, 12, col, weight='bold')
        s.text(ox + 150, 60, 'A and B cannot talk to each other', 11, MUTED)
    s.line(320, 40, 320, 290, '#e5e7eb', 1.5)
    s.save('sd-cap-partition.svg', OUT)


# ======================================================= 02 building blocks

def health_checks():
    """HAProxy-style fall 3 / rise 2, on the lesson's eight check results."""
    results = ['fail', 'fail', 'pass', 'fail', 'fail', 'fail', 'pass', 'pass']
    fall, rise = 3, 2
    up, bad, good, states = True, 0, 0, []
    for r in results:
        if r == 'fail':
            bad, good = bad + 1, 0
            if up and bad >= fall:
                up = False
        else:
            good, bad = good + 1, 0
            if not up and good >= rise:
                up = True
        states.append((up, bad if r == 'fail' else good))
    down_at = next(i for i, (u, _) in enumerate(states) if not u) + 1
    back_at = next(i for i, (u, _) in enumerate(states) if u and i >= down_at) + 1
    assert (down_at, back_at) == (6, 8)
    cw, left = 66, 110
    sv = Svg(left + cw * 8 + 20, 210, 'Health checks with fall 3 and rise 2 on the results fail, fail, pass, fail, '
             'fail, fail, pass, pass: the pass at check 3 resets the count; the server is marked down after check 6 '
             'and back in the pool after check 8')
    sv.text(left - 10, 40, 'check', 12, MUTED, 'end')
    sv.text(left - 10, 82, 'result', 12, MUTED, 'end')
    sv.text(left - 10, 124, 'in a row', 12, MUTED, 'end')
    sv.text(left - 10, 166, 'server', 12, MUTED, 'end')
    for i, (r, (u, run)) in enumerate(zip(results, states)):
        x = left + i * cw
        sv.text(x + cw / 2, 40, i + 1, 13, weight='bold')
        ok = r == 'pass'
        sv.rect(x + 6, 62, cw - 12, 30, '#d1fae5' if ok else '#fee2e2', ACCENT if ok else TRUE)
        sv.text(x + cw / 2, 82, r, 12.5, '#065f46' if ok else '#991b1b', weight='bold')
        sv.text(x + cw / 2, 124, f'{run} {"pass" if ok else "fail"}', 12, MUTED)
        sv.rect(x + 1, 148, cw - 2, 28, PIX if u else '#9ca3af')
        sv.text(x + cw / 2, 167, 'in pool' if u else 'down', 12, '#ffffff', weight='bold')
        if i + 1 in (down_at, back_at):
            sv.add(f'<rect x="{x + 2}" y="54" width="{cw - 4}" height="128" rx="6" fill="none" stroke="{ORANGE}" '
                   f'stroke-width="2.6"/>')
    sv.text(left + (down_at - 0.5) * cw, 200, '3rd fail in a row: out', 11.5, '#b45309', weight='bold')
    sv.text(left + (back_at - 0.5) * cw - 20, 200, '2nd pass: back', 11.5, '#b45309', weight='bold')
    sv.save('sd-health-checks.svg', OUT)


def ring_pos(name):
    """Where a name lands on the ring, in degrees clockwise from the top (from its MD5 hash)."""
    return int.from_bytes(hashlib.md5(name.encode()).digest()[:4], 'big') / 2 ** 32 * 360


def ring_owner(key_deg, nodes):
    """The first node clockwise from the key."""
    after = sorted((d, n) for n, d in nodes.items() if d >= key_deg)
    return after[0][1] if after else min((d, n) for n, d in nodes.items())[1]


NODE_COL = {'A': '#3b82f6', 'B': '#059669', 'C': '#a855f7', 'D': '#db2777', 'E': ORANGE, 'F': '#0891b2'}


def draw_ring(s, cx, cy, r, nodes, keys, moved=(), head=''):
    pt = lambda deg, rr: (cx + rr * math.sin(math.radians(deg)), cy - rr * math.cos(math.radians(deg)))
    order = sorted(nodes, key=nodes.get)
    for i, n in enumerate(order):            # each node owns the arc from the node before it, clockwise
        a0, a1 = nodes[order[i - 1]], nodes[n]
        if a1 <= a0:
            a1 += 360
        (x0, y0), (x1, y1) = pt(a0, r), pt(a1, r)
        s.add(f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 {1 if a1 - a0 > 180 else 0} 1 {x1:.1f} {y1:.1f}" '
              f'fill="none" stroke="{NODE_COL[n]}" stroke-width="5" stroke-opacity="0.35"/>')
    s.text(cx, cy - r - 30, head, 13.5, weight='bold')
    for k, d in keys.items():
        o = ring_owner(d, nodes)
        x, y = pt(d, r)
        mv = k in moved
        s.add(f'<rect x="{x - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" fill="{NODE_COL[o]}" '
              f'stroke="{ORANGE if mv else "#ffffff"}" stroke-width="{3 if mv else 1}"/>')
        lx, ly = pt(d, r - 22)
        s.text(lx, ly + 4, k, 10.5, NODE_COL[o])
    for n, d in nodes.items():
        x, y = pt(d, r)
        s.circle(x, y, 11, NODE_COL[n], '#ffffff')
        s.text(x, y + 4.5, n, 12.5, '#ffffff', weight='bold')


def spread_keys(pool, nodes, n, gap=17, node_gap=9):
    """Pick n names from `pool` whose ring positions are at least `gap` degrees apart (so labels don't collide)."""
    taken, out = [ring_pos(x) for x in nodes], []
    kd = []
    for k in pool:
        d = ring_pos(k)
        if all(min(abs(d - t), 360 - abs(d - t)) >= gap for t in kd) and \
                all(min(abs(d - t), 360 - abs(d - t)) >= node_gap for t in taken):
            kd.append(d)
            out.append(k)
        if len(out) == n:
            return out
    raise ValueError('not enough spread keys')


def ring_before_after(name, title, before, added, keys):
    nodes0 = {n: ring_pos(n) for n in before}
    nodes1 = dict(nodes0, **{added: ring_pos(added)})
    kd = {k: ring_pos(k) for k in keys}
    own0 = {k: ring_owner(d, nodes0) for k, d in kd.items()}
    own1 = {k: ring_owner(d, nodes1) for k, d in kd.items()}
    moved = [k for k in keys if own0[k] != own1[k]]
    assert moved and all(own1[k] == added for k in moved)      # only keys moving to the new node move
    s = Svg(660, 360, title)
    draw_ring(s, 165, 190, 120, nodes0, kd, head=f'{len(before)} nodes')
    draw_ring(s, 495, 190, 120, nodes1, kd, moved, head=f'after adding {added}')
    s.text(330, 352, f'only {", ".join(moved)} moved (orange outline), all of them to {added}; every other key stayed',
           12, '#b45309', weight='bold')
    s.save('sd-' + name, OUT)
    return nodes1, own0, own1, moved


def lb_pictures():
    keys = spread_keys([f'p{i}' for i in range(1, 200)], 'ABCDE', 12)
    ring_before_after('hash-ring-add-node.svg',
                      'Consistent hashing: twelve product keys (p1, p2 ...) on a ring with nodes A to D, each key owned by the first '
                      'node clockwise; after adding node E only the keys just before E move, all of them to E',
                      ['A', 'B', 'C', 'D'], 'E', keys)
    # mod-N: share of keys that move when 4 nodes become 5 = 16 of every 20 hash values
    assert sum(h % 4 != h % 5 for h in range(20)) == 16


def shop_front_door():
    apps = '; '.join(f'a{i} [label="app server {i}"]' for i in range(1, 5))
    arch('shop-front-door.svg',
         'The shop behind its load balancer: browsers fetch images and scripts from a CDN, and send page requests to a '
         'layer 7 load balancer that picks one of four app servers by least outstanding requests; the servers keep '
         'baskets in Redis and read products through a four-node cache placed by consistent hashing, in front of the '
         'database',
         f'''
         b [label="browser"] {K('client')};
         cdn [label="CDN\\nimages, scripts\\n(versioned names)"] {K('lb')};
         lb [label="layer 7 load balancer\\nTLS, least outstanding\\nGET /health every 2 s"] {K('lb')};
         {apps};
         r [label="Redis\\nbaskets"] {K('cache')};
         pc [label="product cache\\n4 Redis nodes,\\nconsistent hashing"] {K('cache')};
         db [label="database"] {K('db')};
         b -> cdn [label=" static files "];
         b -> lb [label=" pages "];
         lb -> a1; lb -> a2; lb -> a3; lb -> a4;
         a1 -> r; a2 -> r; a3 -> r; a4 -> r;
         a1 -> pc; a2 -> pc; a3 -> pc; a4 -> pc;
         pc -> db [label=" on a miss ", style=dashed, minlen=2];
         ''', nodesep=0.2, ranksep=0.6, extra='ordering=out;')


def lb_sketch():
    arch('sketch-lb-path.svg',
         'Answer sketch: clients reach a layer 4 load balancer that spreads connections over two layer 7 load '
         'balancers; they send /api requests to the API pool of three servers and /images requests to the image '
         'pool of two servers; sessions live in a shared session store',
         f'''
         c [label="clients"] {K('client')};
         l4 [label="layer 4 load balancer\\n(spreads connections)"] {K('lb')};
                  l7a [label="layer 7 balancer 1"] {K('lb')}; l7b [label="layer 7 balancer 2"] {K('lb')};
         api [label="API pool\\napi 1, api 2, api 3"];
         img [label="image pool\\nimage 1, image 2"];
         ss [label="shared\\nsession store"] {K('cache')};
         c -> l4; l4 -> l7a; l4 -> l7b;
         l7a -> api [label=" /api/* "]; l7b -> api [label=" /api/* "];
         l7a -> img [label=" /images/* "]; l7b -> img [label=" /images/* "];
         api -> ss;
         ''', nodesep=0.25, ranksep=0.6)


def cache_layers():
    arch('cache-layers.svg',
         'Where caches live, from the user to the database: browser cache, CDN, reverse proxy, the app server\'s '
         'in-process cache, a shared cache such as Redis, and the database\'s own buffer cache; each layer answers '
         'what it can and passes misses on',
         f'''
         b [label="browser cache\\nCache-Control: max-age"] {K('client')};
         cdn [label="CDN (edge)\\nstatic files, pages"] {K('lb')};
         rp [label="reverse proxy\\nwhole responses"] {K('lb')};
         app [label="app server\\nin-process cache\\n(one copy per server)"];
         rc [label="shared cache\\nRedis / Memcached\\n(one copy for all)"] {K('cache')};
         db [label="database\\nbuffer cache"] {K('db')};
         b -> cdn -> rp -> app -> rc -> db [label="  miss "];
         ''', rankdir='TB', nodesep=0.2, ranksep=0.25)


def cache_aside(name, title, key, old, new_, actors=('app', 'cache', 'database')):
    q = Seq(list(actors), 12.4, title, col=170, row=31,
            lw={'cache': FILL['cache'], 'database': FILL['db']})
    a, c, d = actors
    q.band(0.1, 4.75, 'read, cache miss')
    q.msg(a, c, f'GET {key}', 0.6)
    q.msg(c, a, 'miss', 1.4, color=TRUE)
    q.msg(a, d, f'SELECT {key}', 2.2)
    q.msg(d, a, f'{old}', 3.0)
    q.msg(a, c, f'SET {key} = {old}, TTL', 3.8, color=ACCENT)
    q.band(4.95, 7.35, 'read, cache hit', '#ecfdf5')
    q.msg(a, c, f'GET {key}', 5.6)
    q.msg(c, a, f'{old} (database not asked)', 6.4, color=ACCENT)
    q.band(7.55, 12.2, 'write', '#eff6ff')
    q.msg(a, d, f'UPDATE {key} = {new_}', 8.2)
    q.msg(d, a, 'ok', 9.0)
    q.msg(a, c, f'DELETE {key}', 9.8, color=ORANGE)
    q.self_note(a, 11.4, 'next read misses and loads ' + str(new_), MUTED, size=11.5)
    q.save(name)


def stale_race():
    """The lesson's three steps: reader misses and reads 10, writer saves 12 and deletes, reader caches 10."""
    db, cache = {'p42': 10}, {}
    seen = db['p42']                 # 1. reader misses and reads 10, then stalls
    db['p42'] = 12                   # 2. writer saves 12 ...
    cache.pop('p42', None)           #    ... and deletes the (missing) entry
    cache['p42'] = seen              # 3. reader's late answer is cached
    assert cache['p42'] == 10 and db['p42'] == 12
    q = Seq(['reader', 'writer', 'cache', 'database'], 9.6,
            'The stale-value race: the reader misses and reads price 10, then stalls; the writer saves 12 and deletes '
            'the cache entry, which is not there yet; the reader then writes 10 into the cache, where it stays until '
            'the TTL runs out', col=150, row=33,
            lw={'reader': FILL['client'], 'writer': FILL['client'], 'cache': FILL['cache'], 'database': FILL['db']})
    q.msg('reader', 'cache', 'GET p42: miss', 0.5)
    q.msg('reader', 'database', 'SELECT p42', 1.4)
    q.msg('database', 'reader', '10', 2.2, slope=0.4)
    q.s.rect(q.x('reader') - 6, q.y(2.7), 12, q.y(6.6) - q.y(2.7), ORANGE, opacity=0.35)
    q.self_note('reader', 4.5, 'stalls', '#b45309', anchor='end', weight='bold')
    q.msg('writer', 'database', 'UPDATE p42 = 12', 3.2)
    q.msg('writer', 'cache', 'DELETE p42 (nothing there)', 4.6)
    q.msg('reader', 'cache', 'SET p42 = 10', 6.9, color=TRUE)
    q.self_note('cache', 8.4, 'cache: 10', TRUE, anchor='middle', dx=0, weight='bold')
    q.self_note('database', 8.4, 'database: 12', ACCENT, anchor='middle', dx=0, weight='bold')
    q.self_note('reader', 9.3, 'stale until the TTL runs out', TRUE, weight='bold')
    q.save('cache-stale-race.svg')


def leader_followers():
    arch('leader-followers.svg',
         'Leader-follower replication: the app sends every write to the leader, which copies changes to two '
         'read-only followers; reads go to the followers, which may lag slightly behind; right after writing, a '
         'user\'s reads go to the leader',
         f'''
         app [label="app servers"];
         L [label="leader\\n(takes all writes)"] {K('db', penwidth='2.2')};
         F1 [label="follower 1\\n(read-only)"] {K('db')};
         F2 [label="follower 2\\n(read-only)"] {K('db')};
         app -> L [label=" writes ", color="{TRUE}", fontcolor="{TRUE}", penwidth=2];
         app -> L [label=" read-your-own-writes ", style=dashed];
         L -> F1 [label=" copy changes\\n (may lag) ", color="{PIX}", fontcolor="{PIX}"];
         L -> F2 [color="{PIX}"];
         app -> F1 [label=" reads ", color="{ACCENT}", fontcolor="{ACCENT}"];
         app -> F2 [label=" reads ", color="{ACCENT}", fontcolor="{ACCENT}"];
         {{rank=same; F1; F2}}
         ''', rankdir='TB', nodesep=0.6, ranksep=0.5)


def shard_table(name, title, keys, n, per, label_key='id', note=None):
    """Two rows of shards: by range (consecutive blocks of `per`) and by hash (key mod n)."""
    rng = {i: [k for k in keys if (k - keys[0]) // per == i] for i in range(n)}
    hsh = {i: [k for k in keys if k % n == i] for i in range(n)}
    assert sorted(sum(rng.values(), [])) == sorted(keys) == sorted(sum(hsh.values(), []))
    cw = 140
    sv = Svg(130 + cw * n + 10, 252, title)
    for row, (lab, sub, parts) in enumerate([('by range', 'neighbours together', rng),
                                             ('by hash', f'{label_key} mod {n}', hsh)]):
        y = 44 + row * 92
        sv.text(118, y + 26, lab, 14, anchor='end', weight='bold')
        sv.text(118, y + 44, sub, 11, MUTED, 'end')
        for i in range(n):
            x = 130 + i * cw
            box(sv, x, y, cw - 12, 62, FILL['db'], f'shard {i}', ', '.join(map(str, parts[i])), size=14)
    sv.text(130 + cw * n / 2, 22, note or f'{label_key}s {keys[0]} to {keys[-1]} on {n} shards', 13, weight='bold')
    sv.text(130 + cw * n / 2, 222, 'range keeps neighbours together: good for range queries, risks a hot shard',
            11.5, MUTED)
    sv.text(130 + cw * n / 2, 240, 'hash scatters neighbours evenly: no hot range, but a range query asks every shard',
            11.5, MUTED)
    sv.save('sd-' + name, OUT)
    return rng, hsh


def queue_lifecycle():
    arch('queue-message-life.svg',
         'The life of one message in a queue with a 30 second visibility timeout and a limit of three deliveries: '
         'published, visible, then received and hidden; an ack deletes it; no ack within 30 seconds makes it '
         'visible again; after the third failed delivery it goes to the dead-letter queue',
         f'''
         pub [label="producer publishes\\n\\"order 7\\""] {K('client')};
         vis [label="visible\\n(waiting in the queue)"] {K('queue')};
         hid [label="hidden for 30 s\\n(a consumer has it)"];
         del [label="deleted\\n(done)"] {K('db')};
         dlq [label="dead-letter queue\\n(a person looks at it)"] {K('bad')};
         pub -> vis;
         vis -> hid [label=" receive\\n delivery 1, 2, 3 "];
         hid -> del [label=" ack ", color="{ACCENT}", fontcolor="{ACCENT}", penwidth=2];
         hid -> vis [label=" no ack in 30 s\\n (crash, too slow) ", color="{TRUE}", fontcolor="{TRUE}", constraint=false];
         hid -> dlq [label=" 3rd delivery failed ", color="{TRUE}", fontcolor="{TRUE}"];
         ''', rankdir='TB', nodesep=0.7, ranksep=0.45)


def level_load(spike, T, after, mu, horizon):
    """Second by second: arrivals join the queue, then consumers take up to mu."""
    depth, xs = 0, [(0, 0)]
    for t in range(1, horizon + 1):
        depth += spike if t <= T else after
        depth -= min(depth, mu)
        xs.append((t, depth))
    return xs


def load_levelling():
    two = level_load(300, 10, 20, 100, 45)
    four = level_load(300, 10, 20, 200, 45)
    peak2, peak4 = max(d for _, d in two), max(d for _, d in four)
    clear2 = next(t for t, d in two if t > 10 and d == 0)
    clear4 = next(t for t, d in four if t > 10 and d == 0)
    assert (peak2, clear2, peak4, clear4) == (2000, 35, 1000, 16)
    sv = Svg(520, 330, 'Queue depth second by second: 300 orders a second for 10 seconds, then 20. With two workers '
             '(100 a second) the queue peaks at 2,000 at 10 seconds and is empty at 35 seconds; with four workers it '
             'peaks at 1,000 and is empty at 16 seconds')
    p = Plot(sv, 78, 24, 400, 230, (0, 45), (0, 2200))
    p.axes('seconds', 'messages waiting', xticks=(0, 5, 10, 15, 20, 25, 30, 35, 40, 45),
           yticks=(0, 500, 1000, 1500, 2000))
    sv.rect(p.X(0), p.y0, p.X(10) - p.X(0), p.h, ORANGE, opacity=0.12)
    sv.text(p.X(5), p.y0 + 14, 'spike: 300/s', 11, '#b45309', weight='bold')
    p.curve(two, PIX)
    p.curve(four, ACCENT)
    p.dot(10, peak2, PIX)
    p.dot(10, peak4, ACCENT)
    sv.text(p.X(10) + 8, p.Y(peak2) + 4, 'peak 2,000', 11.5, PIX, 'start', 'bold')
    sv.text(p.X(10) + 8, p.Y(peak4) - 6, 'peak 1,000', 11.5, ACCENT, 'start', 'bold')
    sv.text(p.X(clear2), p.Y(0) - 10, 'empty at 35 s', 11.5, PIX, 'middle', 'bold')
    sv.text(p.X(clear4) + 2, p.Y(0) - 10, 'empty at 16 s', 11.5, ACCENT, 'start', 'bold')
    sv.text(p.X(44), p.Y(1700), '2 workers (100/s)', 12, PIX, 'end', 'bold')
    sv.text(p.X(44), p.Y(1500), '4 workers (200/s)', 12, ACCENT, 'end', 'bold')
    sv.save('sd-load-levelling.svg', OUT)


def queue_topic_log():
    sv = Svg(530, 488, 'Three shapes of delivery. A queue gives each message to one of the competing workers. A topic '
             'copies each message into every subscription queue. A log keeps messages in order at numbered offsets, '
             'and each consumer group reads from its own offset')
    mk = arrow_defs(sv)

    def msgs(x, y, labels, fill=FILL['queue'], w=34):
        for i, m in enumerate(labels):
            sv.rect(x + i * (w + 3), y, w, 26, fill, INK, 1)
            sv.text(x + i * (w + 3) + w / 2, y + 17.5, m, 11.5, weight='bold')
        return x + len(labels) * (w + 3)

    # 1. queue
    sv.text(14, 26, '1. Queue: each message goes to ONE worker', 14, anchor='start', weight='bold')
    box(sv, 14, 50, 84, 34, FILL['client'], 'producer', size=12)
    arrow(sv, mk, 98, 67, 128, 67)
    end = msgs(132, 54, ['m3', 'm2', 'm1'])
    for k, (lab, got) in enumerate([('worker 1', 'got m1, m3'), ('worker 2', 'got m2')]):
        y = 38 + k * 46
        arrow(sv, mk, end + 4, 67, 300, y + 17)
        box(sv, 302, y, 96, 34, FILL['svc'], lab, size=12)
        sv.text(410, y + 22, got, 11.5, MUTED, 'start')
    # 2. topic
    y0 = 160
    sv.text(14, y0, '2. Topic: every subscription gets a COPY', 14, anchor='start', weight='bold')
    box(sv, 14, y0 + 44, 84, 34, FILL['client'], 'producer', size=12)
    arrow(sv, mk, 98, y0 + 61, 128, y0 + 61)
    box(sv, 130, y0 + 40, 104, 42, FILL['lb'], 'topic', 'orders', size=12)
    for k, sub in enumerate(['invoices', 'analytics', 'warehouse']):
        y = y0 + 16 + k * 40
        arrow(sv, mk, 234, y0 + 61, 280, y + 13)
        e = msgs(284, y, ['m2', 'm1'], w=30)
        sv.text(e + 8, y + 18, f'{sub} queue', 12, INK, 'start')
    # 3. log
    y0 = 320
    sv.text(14, y0, '3. Log: messages are KEPT; each group has its own offset', 14, anchor='start', weight='bold')
    box(sv, 14, y0 + 44, 84, 34, FILL['client'], 'producer', size=12)
    arrow(sv, mk, 98, y0 + 61, 128, y0 + 61)
    for i in range(7):
        x = 132 + i * 50
        sv.rect(x, y0 + 46, 47, 30, FILL['queue'] if i < 6 else '#ffffff', INK, 1)
        sv.text(x + 23.5, y0 + 66, f'm{i}' if i < 6 else '…', 11.5, weight='bold')
        sv.text(x + 23.5, y0 + 40, i if i < 6 else '', 10.5, GREY)
    sv.text(132, y0 + 34, 'offset', 10.5, GREY, 'end')
    for lab, off, col, dy in [('analytics group', 2, PIX, 110), ('shipping group', 5, ACCENT, 110)]:
        x = 132 + off * 50 + 23.5
        arrow(sv, mk, x, y0 + dy, x, y0 + 80, col)
        sv.text(x, y0 + dy + 16, f'{lab}: next is {off}', 11.5, col, weight='bold')
    sv.text(270, y0 + 152, 'reading does not delete; a new group can replay from offset 0', 11.5, MUTED)
    sv.save('sd-queue-topic-log.svg', OUT)


def order_pipeline(name, title, src, topic, subs):
    body = [f'co [label="{src[0]}\\n{src[1]}"];',
            f'ob [label="outbox table\\n(same transaction)"] {K("db")};',
            f'rl [label="relay"];',
            f't [label="{topic} topic"] {K("lb")};',
            'co -> ob [label=" commit "]; ob -> rl; rl -> t [label=" publish "];']
    for i, (sub, kind, cons) in enumerate(subs):
        body.append(f's{i} [label="{sub}\\n{kind}"] {K("queue")};')
        body.append(f'c{i} [label="{cons}"];')
        body.append(f't -> s{i}; s{i} -> c{i};')
    arch(name, title, '\n'.join(body), rankdir='TB', nodesep=0.25, ranksep=0.35)


def call_shapes(name, title, rest_rounds, gql_query, rest_bytes, gql_bytes, rtt):
    """REST on the left (requests grouped into round trips), GraphQL on the right (one POST)."""
    n_req = sum(len(r) for r in rest_rounds)
    rows = sum(len(r) + 1 for r in rest_rounds)
    sv = Svg(660, 92 + rows * 30 + 70, title)
    mk = arrow_defs(sv)
    for ox, head, server in [(0, 'REST', 'REST API'), (340, 'GraphQL', 'GraphQL server')]:
        sv.text(ox + 165, 22, head, 15, weight='bold')
        box(sv, ox + 20, 34, 100, 30, FILL['client'], 'app', size=12)
        box(sv, ox + 190, 34, 130, 30, FILL['svc'], server, size=12)
        sv.line(ox + 70, 64, ox + 70, sv.h - 56, '#9ca3af', 1.2, '4 4')
        sv.line(ox + 255, 64, ox + 255, sv.h - 56, '#9ca3af', 1.2, '4 4')
    y = 88
    for k, rnd in enumerate(rest_rounds):
        top = y - 16
        for req in rnd:
            arrow(sv, mk, 70, y, 252, y + 8, PIX)
            sv.text(160, y - 4, req, 11, PIX)
            y += 30
        arrow(sv, mk, 255, y - 14, 73, y - 6, ACCENT)
        sv.text(160, y - 16, 'answers' if len(rnd) > 1 else 'answer', 11, ACCENT)
        sv.rect(8, top, 316, y - top, ORANGE, opacity=0.08)
        sv.text(14, top + 12, f'round trip {k + 1}', 10.5, '#b45309', 'start', weight='bold')
        y += 22
    arrow(sv, mk, 410, 88, 592, 96, PIX)
    sv.text(500, 84, 'POST /graphql', 11, PIX)
    for i, line in enumerate(gql_query):
        sv.text(500, 112 + i * 15, line, 10.5, MUTED)
    yy = 112 + len(gql_query) * 15 + 6
    arrow(sv, mk, 595, yy, 413, yy + 8, ACCENT)
    sv.text(500, yy - 4, 'exactly those fields', 11, ACCENT)
    sv.rect(348, 72, 316, yy + 18 - 72, ORANGE, opacity=0.08)
    sv.text(354, 84, 'round trip 1', 10.5, '#b45309', 'start', weight='bold')
    nr = len(rest_rounds)
    sv.text(165, sv.h - 30, f'{n_req} requests, {nr} round trips = {nr * rtt} ms', 12.5, weight='bold')
    sv.text(165, sv.h - 12, f'{rest_bytes} bytes sent' if isinstance(rest_bytes, int) else rest_bytes, 12, MUTED)
    sv.text(505, sv.h - 30, f'1 request, 1 round trip = {rtt} ms', 12.5, weight='bold')
    sv.text(505, sv.h - 12, f'{gql_bytes} bytes sent' if isinstance(gql_bytes, int) else gql_bytes, 12, MUTED)
    sv.save('sd-' + name, OUT)


def varint(n):
    out = []
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return out


def varint_picture():
    assert varint(150) == [0x96, 0x01] and varint(8996) == [0xA4, 0x46]
    sv = Svg(560, 250, 'Encoding 150 as a protobuf varint: 150 is 10010110 in binary; split into 7-bit groups from '
             'the lowest, 0010110 and 0000001; the first byte gets a top bit of 1 because more follows, giving 96 in '
             'hex, and the last byte gets 0, giving 01; with the tag 08 the field id = 150 is 08 96 01')
    bits = f'{150:014b}'
    lo, hi = bits[7:], bits[:7]
    sv.text(20, 30, '150 in binary, split into groups of 7 bits from the right:', 13, anchor='start', weight='bold')
    cw = 22
    for g, (grp, col, x0) in enumerate([(hi, ORANGE, 70), (lo, PIX, 270)]):
        for i, b in enumerate(grp):
            sv.rect(x0 + i * cw, 46, cw - 2, 28, '#f3f4f6', col, 1.5)
            sv.text(x0 + i * cw + cw / 2 - 1, 66, b, 14, weight='bold')
    sv.text(70 + 3.5 * cw, 92, 'high group = 1', 11.5, '#b45309')
    sv.text(270 + 3.5 * cw, 92, 'low group = 22', 11.5, PIX)
    sv.text(20, 130, 'send the low group first; top bit 1 means "another byte follows":', 13, anchor='start', weight='bold')
    for k, (grp, more, col, x0) in enumerate([(lo, 1, PIX, 70), (hi, 0, ORANGE, 300)]):
        sv.rect(x0, 146, cw - 2, 28, '#fed7aa' if more else '#e5e7eb', INK, 1.5)
        sv.text(x0 + cw / 2 - 1, 166, more, 14, weight='bold')
        for i, b in enumerate(grp):
            sv.rect(x0 + (i + 1) * cw, 146, cw - 2, 28, '#f3f4f6', col, 1.5)
            sv.text(x0 + (i + 1) * cw + cw / 2 - 1, 166, b, 14, weight='bold')
        val = int(f'{more}{grp}', 2)
        sv.text(x0 + 4 * cw, 196, f'byte {k + 1} = {val:02x} (hex)', 12.5, weight='bold')
    sv.text(280, 236, 'tag 08 (field 1, varint), then 96 01:   id = 150  ->  08 96 01', 13.5, ACCENT, weight='bold')
    sv.save('sd-varint-150.svg', OUT)


def chain_timing():
    calls = [(f'service {i}', 20) for i in range(1, 6)]
    seq_t = sum(t for _, t in calls)
    par_t = max(t for _, t in calls)
    avail = 0.999 ** len(calls)
    assert seq_t == 100 and par_t == 20 and round(avail * 100, 2) == 99.50
    sv = Svg(560, 330, 'Five 20 ms calls: one after another they take 100 ms; sent together, if they do not depend on '
             'each other, they take 20 ms, the slowest one. Either way all five must be up, so five services at 99.9 '
             'percent give 99.5 percent')
    x0, sc = 110, 4
    for row, (head, par) in enumerate([('one after another', False), ('all at once', True)]):
        y0 = 40 + row * 130
        sv.text(20, y0 - 12, head, 13.5, anchor='start', weight='bold')
        t = 0
        for i, (nm, d) in enumerate(calls):
            start = 0 if par else t
            y = y0 + i * 19
            sv.rect(x0 + start * sc, y, d * sc - 2, 16, FILL['svc'], PIX)
            sv.text(x0 - 8, y + 12, nm, 11, MUTED, 'end')
            t += d
        total = par_t if par else seq_t
        sv.line(x0 + total * sc, y0 - 4, x0 + total * sc, y0 + 96, TRUE, 1.6, '4 3')
        sv.text(x0 + total * sc + 6, y0 + 52, f'{total} ms', 13, TRUE, 'start', 'bold')
    for ms in range(0, 101, 20):
        sv.text(x0 + ms * sc, 284, f'{ms} ms', 10, GREY)
    sv.text(x0 + 50 * sc, 316, f'either way: 99.9% ^ 5 = {avail:.2%} available', 12, MUTED)
    sv.save('sd-sync-chain-timing.svg', OUT)


def push_styles():
    sv = Svg(660, 300, 'Four ways to push updates: polling asks every few seconds and mostly gets nothing; long '
             'polling holds each request open until there is news; server-sent events keep one response open and '
             'the server writes events into it; a WebSocket is one two-way channel where either side can send')
    mk = arrow_defs(sv)
    cols = [('polling', 'poll'), ('long polling', 'long'), ('server-sent events', 'sse'), ('WebSocket', 'ws')]
    news = [150, 230]                       # times when the server has news
    for k, (head, kind) in enumerate(cols):
        ox = 8 + k * 163
        sv.text(ox + 78, 20, head, 13, weight='bold')
        sv.text(ox + 30, 40, 'client', 11, MUTED)
        sv.text(ox + 126, 40, 'server', 11, MUTED)
        cx, srv = ox + 30, ox + 126
        sv.line(cx, 46, cx, 290, '#9ca3af', 1.2, '4 4')
        sv.line(srv, 46, srv, 290, '#9ca3af', 1.2, '4 4')
        for t in news:
            sv.circle(srv, t, 4.5, ORANGE)
        if kind == 'poll':
            for t in (60, 120, 180, 240):
                arrow(sv, mk, cx, t, srv - 3, t + 6, PIX)
                got = any(t - 60 < n <= t for n in news)
                arrow(sv, mk, srv, t + 10, cx + 3, t + 16, ACCENT if got else GREY, dash=None if got else '3 3')
                sv.text(cx + 48, t + 30, 'news' if got else 'nothing', 10, ACCENT if got else GREY)
        elif kind == 'long':
            t0 = 60
            for n in news:
                arrow(sv, mk, cx, t0, srv - 3, t0 + 6, PIX)
                sv.line(srv + 3, t0 + 6, srv + 3, n, PIX, 3)
                arrow(sv, mk, srv, n, cx + 3, n + 8, ACCENT)
                sv.text(cx + 48, n + 22, 'news', 10, ACCENT)
                t0 = n + 14
            sv.text(srv + 8, 110, 'held', 10, PIX, 'start')
        elif kind == 'sse':
            arrow(sv, mk, cx, 60, srv - 3, 66, PIX)
            sv.text(cx + 48, 58, 'GET (stays open)', 10, PIX)
            for n in news:
                arrow(sv, mk, srv, n, cx + 3, n + 8, ACCENT)
                sv.text(cx + 48, n - 4, 'event', 10, ACCENT)
        else:
            arrow(sv, mk, cx, 60, srv - 3, 66, PIX)
            sv.text(cx + 48, 58, 'upgrade', 10, PIX)
            arrow(sv, mk, srv, 76, cx + 3, 82, PIX)
            for n in news:
                arrow(sv, mk, srv, n, cx + 3, n + 8, ACCENT)
            arrow(sv, mk, cx, 190, srv - 3, 196, ORANGE)
            sv.text(cx + 48, 188, 'client sends', 10, '#b45309')
    sv.save('sd-push-styles.svg', OUT)


# ======================================================= 03 architectural patterns

def find_cycle(edges):
    """Depth-first search for a cycle in a dependency graph; returns it as a list of nodes, or None."""
    graph = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
    state, stack = {}, []

    def dfs(u):
        state[u] = 1
        stack.append(u)
        for v in graph.get(u, []):
            if state.get(v) == 1:
                return stack[stack.index(v):] + [v]
            if not state.get(v):
                c = dfs(v)
                if c:
                    return c
        state[u] = 2
        stack.pop()
        return None

    for u in list(graph):
        if not state.get(u):
            c = dfs(u)
            if c:
                return c
    return None


def module_graph(name, title, edges, internal=()):
    cyc = find_cycle(edges)
    cyc_edges = set(zip(cyc, cyc[1:])) if cyc else set()
    body = []
    nodes = sorted({x for e in edges for x in e})
    for n in nodes:
        if '/internal/' in n:
            body.append(f'"{n}" {K("bad", style="rounded,filled,dashed")};')
        else:
            body.append(f'"{n}";')
    for a, b in edges:
        if (a, b) in cyc_edges:
            body.append(f'"{a}" -> "{b}" [color="{TRUE}", penwidth=2.4];')
        elif '/internal/' in b:
            body.append(f'"{a}" -> "{b}" [color="{ORANGE}", penwidth=2.4, style=dashed, label=" reaches inside ", '
                        f'fontcolor="#b45309"];')
        else:
            body.append(f'"{a}" -> "{b}";')
    arch(name, title, '\n'.join(body), rankdir='LR', nodesep=0.4, ranksep=0.5)
    return cyc


def architecture_shapes():
    sv = Svg(660, 330, 'Three ways to build the shop. A monolith: one deployment where every part can call every '
             'other part, with one database. A modular monolith: still one deployment and one database, but modules '
             'call each other only through public interfaces. Microservices: separate deployments, each with its own '
             'database, calling each other over the network')
    mk = arrow_defs(sv)
    mods = ['orders', 'billing', 'catalogue', 'search']
    for k, (head, sub) in enumerate([('monolith', 'one deployment'), ('modular monolith', 'one deployment'),
                                     ('microservices', 'four deployments')]):
        ox = 10 + k * 218
        sv.text(ox + 100, 22, head, 14, weight='bold')
        sv.text(ox + 100, 40, sub, 11, MUTED)
        pos = [(ox + 14, 64), (ox + 108, 64), (ox + 14, 134), (ox + 108, 134)]
        if k < 2:
            sv.add(f'<rect x="{ox + 4}" y="52" width="196" height="138" rx="10" fill="{FILL["client"]}" '
                   f'stroke="{INK}" stroke-width="1.4"/>')
            box(sv, ox + 52, 240, 100, 44, FILL['db'], 'one database', size=12)
            arrow(sv, mk, ox + 102, 190, ox + 102, 238)
        if k == 0:                                                  # everything calls everything
            pts = [(ox + 53, 86), (ox + 147, 86), (ox + 53, 156), (ox + 147, 156)]
            for a in range(4):
                for b in range(a + 1, 4):
                    sv.line(*pts[a], *pts[b], GREY, 1.2)
            for i, (x, y) in enumerate(pts):
                sv.rect(x - 34, y - 11, 68, 20, FILL['client'])
                sv.text(x, y + 4, mods[i], 12, MUTED)
            sv.text(ox + 102, 210, 'anything calls anything', 10.5, MUTED)
        elif k == 1:
            for i, (x, y) in enumerate(pos):
                box(sv, x, y, 78, 44, FILL['svc'], mods[i], size=12)
                sv.rect(x + 60, y + 30, 14, 10, ACCENT)          # the public interface
            arrow(sv, mk, ox + 92, 86, ox + 108, 86, ACCENT)
            arrow(sv, mk, ox + 53, 108, ox + 53, 132, ACCENT)
            arrow(sv, mk, ox + 186, 150, ox + 160, 108, ACCENT)
            sv.text(ox + 102, 210, 'calls only via', 10.5, ACCENT)
            sv.text(ox + 102, 223, 'public interfaces (green)', 10.5, ACCENT)
        else:
            pos = [(ox + 10, 58), (ox + 112, 58), (ox + 10, 156), (ox + 112, 156)]
            for i, (x, y) in enumerate(pos):
                sv.add(f'<rect x="{x - 4}" y="{y - 4}" width="86" height="80" rx="8" fill="none" stroke="#9ca3af" '
                       f'stroke-dasharray="4 3"/>')
                box(sv, x, y, 78, 32, FILL['svc'], mods[i], size=12)
                sv.add(f'<ellipse cx="{x + 39}" cy="{y + 54}" rx="24" ry="9" fill="{FILL["db"]}" stroke="{INK}"/>')
                sv.text(x + 39, y + 58, 'own db', 9.5, MUTED)
            arrow(sv, mk, ox + 88, 74, ox + 110, 74, TRUE, dash='4 3')
            arrow(sv, mk, ox + 70, 132, ox + 70, 154, TRUE, dash='4 3')
            sv.text(ox + 100, 258, 'network calls (red): slower,', 10.5, TRUE)
            sv.text(ox + 100, 271, 'and each one can fail', 10.5, TRUE)
    sv.text(330, 318, 'from left to right: more independence for teams, more network to pay for', 12, MUTED)
    sv.save('sd-architecture-shapes.svg', OUT)


def serverless_breakeven():
    per_m, gbs, secs, gb, server = 0.20, 0.0000166667, 0.2, 0.5, 30
    cost = lambda r: r / 1e6 * per_m + r * secs * gb * gbs
    assert round(cost(1e6), 2) == 1.87 and round(cost(50e6), 2) == 93.33
    be = server / cost(1)
    assert round(be / 1e6) == 16
    sv = Svg(520, 330, 'Monthly cost against invoices a month: serverless grows in a straight line from zero, about '
             '1.87 dollars per million; a server costs a flat 30 dollars; they cross at about 16 million a month')
    p = Plot(sv, 74, 24, 410, 236, (0, 50), (0, 100))
    p.axes('invoices a month (millions)', 'cost a month ($)', xticks=(0, 10, 20, 30, 40, 50),
           yticks=(0, 20, 40, 60, 80, 100))
    p.curve([(m, cost(m * 1e6)) for m in (0, 50)], ORANGE)
    p.curve([(0, server), (50, server)], PIX)
    p.dot(be / 1e6, server, TRUE)
    sv.text(p.X(be / 1e6), p.Y(server) - 14, 'break-even: about 16 million', 11.5, TRUE, weight='bold')
    sv.text(p.X(49), p.Y(cost(49e6)) - 10, 'serverless', 12, '#b45309', 'end', 'bold')
    sv.text(p.X(49), p.Y(server) + 18, 'one $30 server', 12, PIX, 'end', 'bold')
    sv.text(p.X(5), p.Y(8), 'serverless cheaper', 11, ACCENT, 'start')
    sv.text(p.X(28), p.Y(13), 'server cheaper', 11, ACCENT, 'start')
    sv.save('sd-serverless-breakeven.svg', OUT)


def strangler_fig():
    arch('strangler-fig.svg',
         'The strangler fig: clients call a gateway; /search is routed to the new search service, which builds its '
         'own index from catalogue events; every other path still goes to the monolith',
         f'''
         c [label="clients"] {K('client')};
         g [label="gateway\\n(routes by path)"] {K('lb')};
         m [label="monolith\\n(orders, billing, catalogue ...)"];
         sr [label="new search service"] {K('svc', color=ORANGE, penwidth='2.6')};
         idx [label="search index"] {K('db')};
         c -> g;
         g -> m [label=" everything else "];
         g -> sr [label=" /search ", color="{ORANGE}", fontcolor="#b45309", penwidth=2];
         m -> sr [label=" catalogue events ", style=dashed];
         sr -> idx;
         {{rank=same; m; sr}}
         ''', rankdir='TB')


def circuit_breaker(name, title, fails, wait):
    arch(name, title, f'''
         closed [label="CLOSED\\ncalls go through\\n(count failures in a row)", fillcolor="#d1fae5"];
         open [label="OPEN\\nfail at once, no call\\n(wait {wait})", fillcolor="#fee2e2"];
         half [label="HALF-OPEN\\nlet one trial call through", fillcolor="#fef3c7"];
         closed -> closed [label=" success: count = 0 "];
         closed -> open [label=" {fails} failures in a row ", color="{TRUE}", fontcolor="{TRUE}", penwidth=2];
         open -> half [label=" {wait} passed "];
         half -> closed [label=" trial succeeds ", color="{ACCENT}", fontcolor="{ACCENT}", penwidth=2];
         half -> open [label=" trial fails ", color="{TRUE}", fontcolor="{TRUE}"];
         ''', rankdir='TB', nodesep=0.8, ranksep=0.55)


def bulkheads():
    rates = {'search': 20, 'profile': 30}
    healthy = {'search': 0.2, 'profile': 0.1}
    need_h = {k: rates[k] * healthy[k] for k in rates}
    assert round(sum(need_h.values())) == 7
    slow_need = rates['search'] * 5
    assert slow_need == 100
    sv = Svg(620, 300, 'Workers when search slows to 5 seconds. Shared pool of 50: search needs 100 workers by '
             'Little\'s law, so it takes all 50 and profile gets none. Bulkheads of 20 for search and 30 for '
             'profile: search fills its 20, and profile still has its 30, of which it needs only 3')
    cell, cols = 22, 10

    def grid(ox, oy, n, filled, col, label):
        for i in range(n):
            x, y = ox + (i % cols) * cell, oy + (i // cols) * cell
            sv.rect(x, y, cell - 3, cell - 3, col if i < filled else '#f3f4f6', '#9ca3af', 0.8)
        sv.text(ox + cols * cell / 2, oy - 8, label, 12, weight='bold')

    sv.text(130, 22, 'one shared pool of 50', 14, weight='bold')
    grid(20, 62, 50, 50, TRUE, 'search takes all 50')
    sv.text(130, 200, 'needs 20 x 5 s = 100 workers', 11.5, TRUE)
    sv.text(130, 218, 'profile: no worker left', 11.5, TRUE, weight='bold')
    sv.text(460, 22, 'bulkheads: 20 + 30', 14, weight='bold')
    grid(350, 62, 20, 20, TRUE, 'search: its own 20, all busy')
    grid(350, 152, 30, round(need_h['profile']), ACCENT, 'profile: its own 30')
    sv.text(460, 254, 'profile needs 30 x 0.1 s = 3 workers', 11.5, ACCENT)
    sv.text(460, 272, 'and still has them', 11.5, ACCENT, weight='bold')
    sv.line(310, 40, 310, 285, '#e5e7eb', 1.5)
    sv.save('sd-bulkheads.svg', OUT)


def saga_picture(name, title, steps, fail_at, comp):
    """Forward steps left to right; the failing step gets a red cross; compensations run backwards, in reverse."""
    done = steps[:fail_at]
    undo = [comp[st] for st in reversed(done)]
    sv = Svg(130 * len(steps) + 30, 250, title)
    mk = arrow_defs(sv)
    for i, st in enumerate(steps):
        x = 20 + i * 130
        if i < fail_at:
            box(sv, x, 60, 100, 46, '#d1fae5', st, 'done')
        elif i == fail_at:
            box(sv, x, 60, 100, 46, '#fee2e2', st, 'FAILS', stroke=TRUE, width=2.4)
        else:
            box(sv, x, 60, 100, 46, '#f3f4f6', st, 'never runs', stroke='#9ca3af')
        if i:
            col = ACCENT if i <= fail_at else '#9ca3af'
            arrow(sv, mk, x - 30, 83, x - 2, 83, col if col != '#9ca3af' else GREY)
    sv.text(20, 34, 'forward: one local transaction per service', 13, ACCENT, 'start', 'bold')
    for k, st in enumerate(reversed(done)):
        i = steps.index(st)
        x = 20 + i * 130
        sv.add(f'<path d="M {x + 150} 112 C {x + 140} 170, {x + 70} 170, {x + 54} 112" fill="none" stroke="{ORANGE}" '
               f'stroke-width="2" stroke-dasharray="5 4" marker-end="{mk[ORANGE]}"/>')
        sv.text(x + 50, 186, f'{k + 1}. {comp[st]}', 12, '#b45309', weight='bold')
    sv.text(20, 232, 'backward: compensations, newest first: ' + ', then '.join(undo), 13, '#b45309', 'start', 'bold')
    sv.save('sd-' + name, OUT)
    return undo


def cqrs_picture():
    arch('cqrs.svg',
         'CQRS: commands go to the write model and its store; the write side publishes events; the events update '
         'read models shaped for each screen; queries read from the read models, which may lag slightly',
         f'''
         cmd [label="commands\\n(place order)"] {K('client')};
         q [label="queries\\n(order history screen)"] {K('client')};
         w [label="write model"];
         ws [label="write store\\n(normalised)"] {K('db')};
         ev [label="events"] {K('queue')};
         r1 [label="read model\\nhistory by customer"] {K('db')};
         r2 [label="read model\\nsales by day"] {K('db')};
         cmd -> w -> ws;
         ws -> ev [label=" publish "];
         ev -> r1 [label=" update "]; ev -> r2;
         q -> r1 [label=" read "];
         {{rank=same; cmd; q}}
         ''', rankdir='TB', nodesep=0.5, ranksep=0.4)


def event_sourcing():
    events = [('Opened', 0), ('Deposited', 100), ('Withdrew', -30), ('Deposited', 50), ('Withdrew', -20)]
    bal, states = 0, []
    for _, amt in events:
        bal += amt
        states.append(bal)
    assert states[-1] == 100
    sv = Svg(560, 210, 'Event sourcing: the stored events are Opened, Deposited 100, Withdrew 30, Deposited 50 and '
             'Withdrew 20; replaying them in order gives balances 0, 100, 70, 120 and 100, so the current balance '
             'is 100')
    mk = arrow_defs(sv)
    sv.text(20, 26, 'stored: the events (append-only, never changed)', 13, anchor='start', weight='bold')
    for i, (ev, amt) in enumerate(events):
        x = 20 + i * 106
        lab = f'{ev} {abs(amt)}' if amt else ev
        box(sv, x, 40, 98, 36, FILL['queue'], lab, size=11.5)
        arrow(sv, mk, x + 49, 80, x + 49, 116, PIX)
        sv.text(x + 49, 140, f'balance {states[i]}', 12, PIX, weight='bold')
    sv.text(20, 180, 'derived: replay the events in order to get any state, past or present', 13, anchor='start',
            weight='bold')
    sv.text(20, 200, f'current balance = {states[-1]}', 13, ACCENT, 'start', 'bold')
    sv.save('sd-event-sourcing.svg', OUT)


def discovery():
    cl = f'fontname="{FONT}"; fontsize=13; color="#9ca3af"; style="rounded,dashed";'
    arch('service-discovery.svg',
         'Two kinds of service discovery. Client-side: the orders service asks the registry where payments is, gets '
         'the healthy instances back, and calls one itself. Server-side: the orders service calls one load-balancer '
         'name, and the load balancer picks a healthy instance. Health checks keep both lists current',
         f'''
         subgraph cluster_c {{ label="client-side"; {cl}
           o1 [label="orders"];
           reg [label="service registry\\n(Consul, etcd)"] {K('cache')};
           p1 [label="payments #1"]; p2 [label="payments #2"];
           o1 -> reg [label=" 1. where is payments? "];
           reg -> o1 [label=" 2. #1, #2 "];
           o1 -> p2 [label=" 3. call #2 ", color="{PIX}", fontcolor="{PIX}", penwidth=2];
           reg -> p1 [style=dashed, dir=back, label=" health ", color="{GREY}", fontcolor="{GREY}"];
           {{rank=same; p1; p2}}
         }}
         subgraph cluster_s {{ label="server-side"; {cl}
           o2 [label="orders"];
           lb [label="load balancer\\n(\\"payments\\")"] {K('lb')};
           q1 [label="payments #1"]; q2 [label="payments #2"];
           o2 -> lb [label=" call payments "];
           lb -> q1; lb -> q2 [color="{PIX}", penwidth=2];
         }}
         ''', rankdir='TB', nodesep=0.4, ranksep=0.45)


def gateway_bff():
    arch('gateway-bff.svg',
         'Backends for frontends: the web app calls a web BFF and the mobile app calls a mobile BFF; each BFF '
         'handles login checks and rate limits and combines calls to the orders, catalogue and customers services '
         'into the shape its own screens need',
         f'''
         web [label="web app"] {K('client')}; mob [label="mobile app"] {K('client')};
         wb [label="web BFF\\n(richer pages)"] {K('lb')};
         mb [label="mobile BFF\\n(lean payloads)"] {K('lb')};
         o [label="orders"]; c [label="catalogue"]; u [label="customers"];
         web -> wb; mob -> mb;
         wb -> o; wb -> c; wb -> u;
         mb -> o; mb -> c;
         ''', rankdir='TB', nodesep=0.4, ranksep=0.5)


def sidecar():
    cl = f'fontname="{FONT}"; fontsize=12; color="{INK}"; style="rounded";'
    arch('sidecar.svg',
         'Sidecars: each pod runs the service next to a proxy sidecar; the orders service talks only to its own '
         'sidecar, and the sidecars talk to each other with mutual TLS, retries and metrics, so the service code '
         'does none of that',
         f'''
         subgraph cluster_a {{ label="pod: orders"; {cl}
           a [label="orders service\\n(business logic only)"];
           sa [label="sidecar proxy"] {K('cache')}; }}
         subgraph cluster_b {{ label="pod: payments"; {cl}
           sb [label="sidecar proxy"] {K('cache')};
           b [label="payments service\\n(business logic only)"]; }}
         a -> sa [label=" plain call "];
         sa -> sb [label=" mTLS, retries,\\n metrics ", color="{PIX}", fontcolor="{PIX}", penwidth=2];
         sb -> b [label=" plain call "];
         ''', rankdir='TB', nodesep=0.3, ranksep=0.35)


def dual_write():
    sv = Svg(660, 300, 'The two failures of a dual write. Save, then publish: the order insert commits, the service '
             'crashes, and the publish never happens, so the order is lost to everyone else. Publish, then save: '
             'OrderPlaced is sent, then the insert fails, so everyone hears about a phantom order that does not exist')
    mk = arrow_defs(sv)
    for k, (head, first, second, verdict, why) in enumerate([
            ('save, then publish', ('database', 'INSERT order', True), ('broker', 'publish OrderPlaced', None),
             'LOST', 'the order exists, nobody is told'),
            ('publish, then save', ('broker', 'publish OrderPlaced', True), ('database', 'INSERT order', False),
             'PHANTOM', 'everyone hears of an order that doesn\'t exist')]):
        ox = 10 + k * 330
        sv.text(ox + 155, 22, head, 14, weight='bold')
        lanes = {'service': ox + 45, 'database': ox + 160, 'broker': ox + 270}
        for nm, x in lanes.items():
            box(sv, x - 44, 34, 88, 28, FILL['db'] if nm == 'database' else FILL['queue'] if nm == 'broker'
                else FILL['svc'], nm, size=12)
            sv.line(x, 62, x, 236, '#9ca3af', 1.2, '4 4')
        for t, (dest, lab, ok) in [(96, first), (166, second)]:
            x2 = lanes[dest]
            if ok is None:
                arrow(sv, mk, lanes['service'], t, x2 - 3, t + 8, GREY, dash='4 4')
                sv.text((lanes['service'] + x2) / 2, t - 5, lab + ': never happens', 11, GREY)
            else:
                col = ACCENT if ok else TRUE
                arrow(sv, mk, lanes['service'], t, x2 - 3, t + 8, col)
                sv.text((lanes['service'] + x2) / 2, t - 5, lab + (' ✓' if ok else ' ✗ fails'), 11, col,
                        weight='bold')
        if k == 0:
            sv.text(lanes['service'] + 8, 134, '✗ crash', 13, TRUE, 'start', 'bold')
        sv.text(ox + 155, 262, verdict, 15, TRUE, weight='bold')
        sv.text(ox + 155, 282, why, 11.5, MUTED)
    sv.line(335, 20, 335, 290, '#e5e7eb', 1.5)
    sv.save('sd-dual-write.svg', OUT)


def outbox_flow():
    q = Seq(['service', 'database', 'relay', 'broker'], 9.4,
            'The transactional outbox: the service inserts the order and an outbox row in one transaction and '
            'commits; separately, the relay selects unpublished outbox rows, publishes each to the broker, then '
            'marks it published', col=150, row=33,
            lw={'database': FILL['db'], 'broker': FILL['queue'], 'relay': FILL['svc']})
    q.band(0.0, 3.4, 'one transaction: both rows or neither', '#ecfdf5')
    q.msg('service', 'database', 'INSERT order', 1.0)
    q.msg('service', 'database', 'INSERT outbox row', 1.8)
    q.msg('service', 'database', 'COMMIT', 2.6, color=ACCENT)
    q.band(3.6, 9.3, 'later, again and again: the relay', '#eff6ff')
    q.msg('relay', 'database', 'SELECT unpublished rows', 4.6)
    q.msg('database', 'relay', 'row: OrderPlaced o5', 5.5)
    q.msg('relay', 'broker', 'publish OrderPlaced', 6.4, color=PIX)
    q.msg('relay', 'database', 'UPDATE published_at = now()', 7.5)
    q.self_note('service', 8.7, 'the request never talks to the broker', MUTED)
    q.save('outbox-flow.svg')


def relay_duplicate(name, title, event, order_id):
    """Publish, crash before marking, restart, publish again; the idempotent consumer applies it once."""
    seen, applied, results = set(), [], []
    for delivery in (event, event):            # the broker receives it twice
        if delivery in seen:
            results.append('duplicate')
        else:
            seen.add(delivery)
            applied.append(order_id)
            results.append('applied')
    assert results == ['applied', 'duplicate'] and applied == [order_id]
    q = Seq(['relay', 'database', 'broker', 'consumer'], 9.8, title, col=150, row=33,
            lw={'database': FILL['db'], 'broker': FILL['queue']})
    q.msg('relay', 'broker', f'publish {event}', 0.6, color=PIX)
    q.msg('broker', 'consumer', f'{event}', 1.4)
    q.self_note('consumer', 2.4, 'applied', ACCENT, anchor='end', weight='bold')
    q.self_note('relay', 2.9, '✗ crash before marking it sent', TRUE, weight='bold')
    q.self_note('relay', 3.7, 'restart: row still unpublished', MUTED)
    q.msg('relay', 'database', 'SELECT unpublished rows', 5.0)
    q.msg('relay', 'broker', f'publish {event} again', 6.0, color=PIX)
    q.msg('broker', 'consumer', f'{event}', 6.8)
    q.self_note('consumer', 7.8, 'duplicate: skipped', '#b45309', anchor='end', weight='bold')
    q.msg('relay', 'database', 'UPDATE published_at', 8.6)
    q.save(name)


# ======================================================= 04 distributed systems

def no_reply_cases():
    sv = Svg(660, 290, 'Four reasons a request gets no reply: the request was lost on the way; the work was done but '
             'the reply was lost; the server is still working, just slowly; the server crashed. From the client\'s '
             'side all four look the same: silence until the timeout')
    mk = arrow_defs(sv)
    cases = [('request lost', 'lost'), ('reply lost', 'reply'), ('slow, still working', 'slow'),
             ('server crashed', 'crash')]
    for k, (head, kind) in enumerate(cases):
        ox = 8 + k * 163
        cx, sx = ox + 30, ox + 124
        sv.text(ox + 77, 20, head, 12.5, weight='bold')
        sv.text(cx, 40, 'client', 11, MUTED)
        sv.text(sx, 40, 'server', 11, MUTED)
        sv.line(cx, 46, cx, 236, '#9ca3af', 1.2, '4 4')
        sv.line(sx, 46, sx, 236 if kind != 'crash' else 110, '#9ca3af', 1.2, '4 4')
        if kind == 'lost':
            arrow(sv, mk, cx, 70, cx + 52, 84, PIX)
            sv.text(cx + 60, 92, '✗', 16, TRUE, weight='bold')
        else:
            arrow(sv, mk, cx, 70, sx - 3, 96, PIX)
        if kind == 'reply':
            sv.rect(sx - 5, 100, 10, 30, ACCENT)
            sv.text(sx - 9, 120, 'work done', 10, ACCENT, 'end')
            arrow(sv, mk, sx, 134, sx - 52, 148, PIX)
            sv.text(sx - 60, 158, '✗', 16, TRUE, weight='bold')
        if kind == 'slow':
            sv.rect(sx - 5, 100, 10, 136, ORANGE, opacity=0.7)
            sv.text(sx - 9, 170, 'still busy', 10, '#b45309', 'end')
        if kind == 'crash':
            sv.text(sx, 128, '✗', 20, TRUE, weight='bold')
            sv.text(sx, 146, 'crashed', 10, TRUE)
        sv.rect(cx - 6, 72, 12, 128, '#e5e7eb')
        sv.line(cx - 12, 200, cx + 12, 200, TRUE, 2)
        sv.text(cx + 16, 204, 'timeout', 10.5, TRUE, 'start', 'bold')
    sv.text(330, 266, 'the client sees the same thing every time: nothing, then its timeout', 13, weight='bold')
    sv.text(330, 284, 'so it cannot know whether the work happened', 12, MUTED)
    sv.save('sd-no-reply-cases.svg', OUT)


def two_generals():
    msgs = ['attack at dawn', 'got it (ack)', 'got your ack', 'got your ack of my ack']
    q = Seq(['General A', 'General B'], len(msgs) + 1.7,
            'Two Generals: A sends attack at dawn, B acks, A acks the ack, B acks that, and so on; each message '
            'needs a confirmation, so whoever sent the last message can never be sure it arrived',
            col=230, row=44, lw={'General A': FILL['svc'], 'General B': '#fee2e2'})
    for i, m in enumerate(msgs):
        a, b = ('General A', 'General B') if i % 2 == 0 else ('General B', 'General A')
        last = i == len(msgs) - 1
        q.msg(a, b, m + ('  - did it arrive?' if last else ''), 0.6 + i, slope=0.55,
              color=ORANGE if last else INK, dash='5 4' if last else None)
    q.self_note('General A', len(msgs) + 1.0, 'the last message is always unconfirmed', '#b45309', anchor='start',
                dx=40, weight='bold')
    q.save('two-generals.svg')


def quorum_partition():
    n = 5
    majority = n // 2 + 1
    left, right = 3, 2
    assert left >= majority > right
    sv = Svg(590, 260, 'A partition splits five nodes into three and two. A majority is 3 of 5. In a CP system the '
             'side with 3 can still reach a majority and keeps accepting writes; the side with 2 cannot, so it '
             'refuses writes. In an AP system both sides keep answering and must reconcile later')
    for i in range(n):
        side = 0 if i < left else 1
        x = 70 + (i if side == 0 else i - left) * 80 + side * 300
        y = 110 if i % 2 == 0 else 150
        sv.circle(x, y, 24, '#d1fae5' if side == 0 else '#fee2e2', INK)
        sv.text(x, y + 5, f'n{i + 1}', 13, weight='bold')
    sv.line(320, 50, 320, 200, TRUE, 2.5, '7 5')
    sv.text(320, 40, 'partition', 12, TRUE, weight='bold')
    sv.text(150, 40, f'{left} nodes: a majority ({majority} of {n})', 13, ACCENT, weight='bold')
    sv.text(450, 40, f'{right} nodes: no majority', 13, TRUE, weight='bold')
    sv.text(150, 212, 'CP: keeps accepting writes', 12, ACCENT)
    sv.text(450, 212, 'CP: refuses writes (stays correct)', 12, TRUE)
    sv.text(450, 232, 'AP: answers anyway, may be stale', 12, '#b45309')
    sv.text(150, 232, 'AP: answers too', 12, '#b45309')
    sv.save('sd-quorum-partition.svg', OUT)


def run_clocks(procs, events):
    """events: (proc, kind, name, msg, x) with kind local/send/recv. Returns Lamport and vector values by name."""
    lam = {p: 0 for p in procs}
    vec = {p: [0] * len(procs) for p in procs}
    sent, L, V = {}, {}, {}
    for proc, kind, name, msg, _x in events:
        i = procs.index(proc)
        if kind == 'recv':
            ml, mv = sent[msg]
            lam[proc] = max(lam[proc], ml) + 1
            vec[proc] = [max(a, b) for a, b in zip(vec[proc], mv)]
            vec[proc][i] += 1
        else:
            lam[proc] += 1
            vec[proc][i] += 1
        if kind == 'send':
            sent[msg] = (lam[proc], list(vec[proc]))
        L[name], V[name] = lam[proc], list(vec[proc])
    return L, V


def draw_clocks(name, title, procs, events, values, width, fmt, gap=80, below=()):
    t = Timeline(procs, width, title, gap=gap)
    pos = {nm: (proc, x) for proc, _k, nm, _m, x in events}
    sends = {m: nm for proc, k, nm, m, x in events if k == 'send'}
    for proc, kind, nm, msg, x in events:
        if kind == 'recv':
            sp, sx = pos[sends[msg]]
            t.message(sp, sx, proc, x, msg)
    for proc, kind, nm, msg, x in events:
        t.event(proc, x, fmt(nm, values[nm]), above=nm not in below,
                color=PIX if kind == 'send' else ACCENT if kind == 'recv' else INK)
    t.save(name)


def vec_str(v):
    return '[' + ','.join(map(str, v)) + ']'


def concurrent(a, b):
    return any(x > y for x, y in zip(a, b)) and any(y > x for x, y in zip(a, b))


def lamport_trace():
    procs = ['P1', 'P2', 'P3']
    ev = [('P1', 'local', 'a', None, 90), ('P1', 'send', 'b', 'm', 170),
          ('P2', 'local', 'c', None, 120), ('P2', 'recv', 'd', 'm', 260), ('P2', 'send', 'e', 'n', 340),
          ('P3', 'local', 'f', None, 90), ('P3', 'local', 'g', None, 170), ('P3', 'recv', 'h', 'n', 450)]
    L, V = run_clocks(procs, ev)
    assert L == {'a': 1, 'b': 2, 'c': 1, 'd': 3, 'e': 4, 'f': 1, 'g': 2, 'h': 5}
    assert concurrent(V['g'], V['d'])             # g:2 and d:3 are concurrent although 2 < 3
    draw_clocks('lamport-trace.svg', 'Lamport clocks on three processes: P1 has a:1 and b:2, and b sends m to P2; '
                'P2 has c:1, then receives m at d:3 (max of 1 and 2, plus 1), then sends n at e:4; P3 has f:1 and g:2, '
                'then receives n at h:5 (max of 2 and 4, plus 1)', procs, ev, L, 520,
                lambda nm, v: f'{nm}:{v}', below={'d', 'h'})


def vector_siblings():
    # A and B each write once with no contact: concurrent. The client reads both and writes the merge through A.
    a1, b1 = [1, 0, 0], [0, 1, 0]
    assert concurrent(a1, b1)
    merged = [max(x, y) for x, y in zip(a1, b1)]
    assert merged == [1, 1, 0]
    a2 = list(merged)
    a2[0] += 1                                    # A's next write descends the merge
    assert a2 == [2, 1, 0] and all(x >= y for x, y in zip(a2, merged)) and a2 != merged
    t = Timeline(['A', 'B', 'client'], 600, 'Vector clocks catching a conflict: node A writes cat with [1,0,0] and '
                 'node B writes dog with [0,1,0]; neither dominates, so they are concurrent and the store keeps both '
                 'as siblings; the client reads both, resolves cat-dog and writes it with the merged clock [1,1,0]; '
                 'A\'s later write [2,1,0] descends from it, so there is no conflict', gap=88, left=70, height=284)
    t.event('A', 100, 'cat [1,0,0]', PIX)
    t.event('B', 130, 'dog [0,1,0]', PIX)
    t.message('A', 100, 'client', 270)
    t.message('B', 130, 'client', 270)
    t.event('client', 270, 'reads both: siblings', TRUE, above=False)
    t.event('client', 340, '', ACCENT)
    t.s.text(350, t.y('client') + 21, 'writes cat-dog [1,1,0]', 12, ACCENT, 'start', 'bold')
    t.message('client', 340, 'A', 420)
    t.event('A', 420, 'stored [1,1,0]', ACCENT)
    t.event('A', 520, '[2,1,0]', INK)
    t.s.text(520, t.y('A') + 22, 'later write: no conflict', 11, MUTED)
    t.s.text(300, t.y('client') + 58, '[1,0,0] vs [0,1,0]: neither dominates, so the writes are concurrent', 12,
             TRUE, weight='bold')
    t.save('vector-siblings.svg')


def clock_skew():
    skew = 50                                     # A's clock runs 50 ms ahead of B's
    a_real, b_real = 50, 110                      # real times of the two writes; B writes later
    a_ts, b_ts = a_real + skew, b_real - skew     # = 100 and 60, the lesson's stamps (B's clock = real - 50)
    assert (a_ts, b_ts) == (100, 60) and b_real > a_real and max((a_ts, 'cat'), (b_ts, 'dog'))[1] == 'cat'
    t = Timeline(['A', 'B'], 560, 'Clock skew breaks last-write-wins: node A\'s clock is 50 ms ahead of B\'s; A '
                 'writes cat stamped 100, then B writes dog later in real time but stamped 60; last-write-wins keeps '
                 'the higher stamp, cat, so B\'s newer write is lost', gap=80, height=230)
    X = lambda ms: 90 + ms * 3
    t.event('A', X(a_real), 'x = "cat", stamp 100', PIX)
    t.event('B', X(b_real), 'x = "dog", stamp 60', ORANGE, above=False)
    t.s.text(X(a_real), t.y('A') + 24, "A's clock: 50 ms fast", 11, MUTED)
    t.s.text(X(b_real), t.y('B') - 14, 'later in real time', 11, '#b45309', weight='bold')
    t.s.text(280, 200, 'last write wins keeps stamp 100: "cat" wins, the newer "dog" is lost', 12.5, TRUE,
             weight='bold')
    t.s.text(530, t.y('B') + 34, 'real time', 11, GREY, 'end')
    t.save('clock-skew-lww.svg')


def vector_sketch():
    procs = ['P1', 'P2', 'P3']
    ev = [('P1', 'local', 'a', None, 90), ('P1', 'send', 'b', 'm1', 170),
          ('P2', 'local', 'c', None, 110), ('P2', 'recv', 'd', 'm1', 250), ('P2', 'send', 'e', 'm2', 330),
          ('P3', 'local', 'f', None, 150), ('P3', 'recv', 'g', 'm2', 420), ('P1', 'local', 'h', None, 300)]
    L, V = run_clocks(procs, ev)
    assert V['d'] == [2, 2, 0] and V['g'] == [2, 3, 2] and V['h'] == [3, 0, 0]
    assert concurrent(V['h'], V['e']) and concurrent(V['f'], V['b'])
    draw_clocks('sketch-vector-clocks.svg', 'Answer sketch: P1 has a [1,0,0], b [2,0,0] sending m1, and h [3,0,0]; '
                'P2 has c [0,1,0], receives m1 at d [2,2,0], and sends m2 at e [2,3,0]; P3 has f [0,0,1] and '
                'receives m2 at g [2,3,2]; h and e are concurrent', procs, ev, V, 540,
                lambda nm, v: f'{nm} {vec_str(v)}', below={'d', 'g'})
    return V


def read_your_writes():
    """A user writes to the leader; the copy to the follower takes a while; a read from the follower in between is
    stale. Times are in ms; the follower applies the change when the copy arrives."""
    write_at, copy_arrives, read1, read2 = 20, 140, 70, 180
    follower_value = lambda t: 'new bio' if t >= copy_arrives else 'old bio'
    assert follower_value(read1) == 'old bio' and follower_value(read2) == 'new bio'
    X = lambda ms: 100 + ms * 2.6
    t = Timeline(['you', 'leader', 'follower'], 660, 'Read-your-writes broken by replication lag: you save a new bio '
                 'on the leader; the copy to the follower is still on its way when your next read goes to the '
                 'follower, so you see the old bio; a read after the copy arrives sees the new one', gap=82,
                 height=270, left=80)
    t.event('you', X(write_at), 'save "new bio"', PIX)
    t.message('you', X(write_at), 'leader', X(write_at + 20))
    t.event('leader', X(write_at + 20), 'saved', ACCENT, above=False)
    t.message('leader', X(write_at + 20), 'follower', X(copy_arrives), 'copy (lagging)', GREY)
    t.event('follower', X(copy_arrives), 'now new', ACCENT, above=False)
    for r, col in ((read1, TRUE), (read2, ACCENT)):
        t.s.add(f'<line x1="{X(r)}" y1="{t.y("you")}" x2="{X(r)}" y2="{t.y("follower") - 7}" stroke="{col}" '
                f'stroke-width="1.6" stroke-dasharray="4 3" marker-end="{t.mk[col]}"/>')
        t.event('you', X(r), f'read: "{follower_value(r)}"', col)
    t.s.text(X(read1) - 6, t.y('leader') + 30, 'too early', 11, TRUE, 'end', 'bold')
    t.s.text(320, 258, 'read-your-writes fix: send your reads to the leader for a moment after you write', 12,
             MUTED)
    t.save('read-your-writes.svg')


def sync_async():
    sv = Svg(660, 300, 'Synchronous and asynchronous replication. Synchronous: the leader waits for the follower to '
             'confirm the copy before telling the client done, so the write survives a leader crash but takes '
             'longer. Asynchronous: the leader tells the client done at once and copies in the background; if it '
             'crashes before the copy, the confirmed write is lost')
    mk = arrow_defs(sv)
    for k, head in enumerate(['synchronous', 'asynchronous']):
        ox = 10 + k * 330
        lanes = {'client': ox + 45, 'leader': ox + 160, 'follower': ox + 270}
        sv.text(ox + 155, 22, head, 14, weight='bold')
        for nm, x in lanes.items():
            box(sv, x - 42, 34, 84, 28, FILL['client'] if nm == 'client' else FILL['db'], nm, size=12)
            sv.line(x, 62, x, 250, '#9ca3af', 1.2, '4 4')
        c, l, f = lanes['client'], lanes['leader'], lanes['follower']
        arrow(sv, mk, c, 84, l - 3, 96, PIX)
        sv.text((c + l) / 2, 80, 'write', 11, PIX)
        if k == 0:
            arrow(sv, mk, l, 106, f - 3, 118, INK)
            sv.text((l + f) / 2, 102, 'copy', 11)
            arrow(sv, mk, f, 128, l + 3, 140, INK)
            sv.text((l + f) / 2, 126, 'got it', 11)
            arrow(sv, mk, l, 152, c + 3, 164, ACCENT)
            sv.text((c + l) / 2, 150, 'done', 11.5, ACCENT, weight='bold')
            sv.text(ox + 155, 272, 'safe: two copies before "done"', 12, ACCENT, weight='bold')
            sv.text(ox + 155, 290, 'but slower, and stalls if the follower is down', 11.5, MUTED)
        else:
            arrow(sv, mk, l, 106, c + 3, 118, ACCENT)
            sv.text((c + l) / 2, 104, 'done', 11.5, ACCENT, weight='bold')
            sv.text(l + 8, 150, '✗ crash', 13, TRUE, 'start', 'bold')
            arrow(sv, mk, l, 176, f - 3, 188, GREY, dash='4 4')
            sv.text((l + f) / 2, 172, 'copy never sent', 11, GREY)
            sv.text(ox + 155, 272, 'fast: "done" at once', 12, ACCENT, weight='bold')
            sv.text(ox + 155, 290, 'but the confirmed write is lost', 11.5, TRUE, weight='bold')
    sv.line(335, 20, 335, 295, '#e5e7eb', 1.5)
    sv.save('sd-sync-async-replication.svg', OUT)


def multi_leader():
    arch('multi-leader.svg',
         'Multi-leader replication: users in Lagos write to the Lagos leader and users in London write to the London '
         'leader; each leader copies its changes to the other; if both change the same field at once, the copies '
         'meet as a conflict that must be resolved',
         f'''
         u1 [label="users in Lagos"] {K('client')};
         u2 [label="users in London"] {K('client')};
         l1 [label="Lagos leader\\nname = \\"Ada\\""] {K('db')};
         l2 [label="London leader\\nname = \\"Adaeze\\""] {K('db')};
         u1 -> l1 [label=" write nearby "]; u2 -> l2 [label=" write nearby "];
         l1 -> l2 [label=" copy changes ", dir=both, color="{PIX}", fontcolor="{PIX}"];
         c [label="same field changed in both:\\na conflict to resolve", shape=plaintext, style="", fontcolor="{TRUE}"];
         l1 -> c [style=invis]; l2 -> c [style=invis];
         {{rank=same; l1; l2}}
         ''', rankdir='TB', nodesep=1.0, ranksep=0.5)


def quorum_overlap(name, title, n, write, reads, w, r):
    assert len(write) == w and all(len(x) == r for x in reads)
    from itertools import combinations
    # every possible read set meets the write set, in at least w + r - n replicas
    assert w + r > n and min(len(set(c) & set(write)) for c in combinations(range(1, n + 1), r)) == w + r - n
    for rs in reads:
        assert set(rs) & set(write)
    rows = [('write', write)] + [(f'read {i + 1}', rs) for i, rs in enumerate(reads)]
    sv = Svg(150 + 64 * n + 140, 58 + 62 * len(rows) + 30, title)
    sv.text(20, 28, f'N = {n} copies, W = {w}, R = {r}: W + R = {w + r} > {n}', 14, anchor='start', weight='bold')
    for k, (lab, members) in enumerate(rows):
        y = 70 + k * 62
        sv.text(110, y + 5, lab, 13, PIX if k == 0 else '#b45309', 'end', 'bold')
        for i in range(1, n + 1):
            x = 150 + (i - 1) * 64
            has_write = i in write
            if k == 0:
                sv.circle(x, y, 20, PIX if has_write else '#f3f4f6', INK)
                sv.text(x, y + 5, f'r{i}', 12.5, '#ffffff' if has_write else INK, weight='bold')
            else:
                inside = i in members
                both = inside and has_write
                sv.circle(x, y, 20, '#dbeafe' if has_write else '#f3f4f6', INK)
                if inside:
                    sv.add(f'<circle cx="{x}" cy="{y}" r="25" fill="none" stroke="{ORANGE}" stroke-width="3"/>')
                sv.text(x, y + 5, f'r{i}', 12.5, weight='bold' if both else 'normal')
        if k:
            shared = sorted(set(members) & set(write))
            sv.text(150 + 64 * n - 10, y + 5, 'shares ' + ', '.join(f'r{i}' for i in shared), 12, ACCENT, 'start',
                    'bold')
    sv.text(20, sv.h - 14, 'blue = has the new write; orange ring = asked by the read. Every read meets a blue copy.',
            12, MUTED, 'start')
    sv.save('sd-' + name, OUT)


def g_counter():
    nodes = ['A', 'B', 'C']
    r1, r2 = {'A': 3, 'B': 1, 'C': 0}, {'A': 1, 'B': 4, 'C': 2}
    merge = lambda x, y: {k: max(x[k], y[k]) for k in nodes}
    m = merge(r1, r2)
    assert m == merge(r2, r1) == merge(m, r2) == {'A': 3, 'B': 4, 'C': 2} and sum(m.values()) == 9
    sv = Svg(560, 290, 'A G-Counter merge: replica 1 holds A 3, B 1, C 0 (total 4) and replica 2 holds A 1, B 4, C 2 '
             '(total 7); merging takes the larger number for each node, giving A 3, B 4, C 2 with total 9, the same '
             'whichever order they merge in and however often')
    mk = arrow_defs(sv)
    cw = 52

    def row(x, y, vals, head, hl=None):
        sv.text(x + cw * 1.5, y - 10, head, 13, weight='bold')
        for i, k in enumerate(nodes):
            hot = hl and hl[k]
            sv.rect(x + i * cw, y, cw - 4, 44, '#fed7aa' if hot else FILL['svc'], ORANGE if hot else INK,
                    2.4 if hot else 1)
            sv.text(x + i * cw + cw / 2 - 2, y + 17, k, 11, MUTED)
            sv.text(x + i * cw + cw / 2 - 2, y + 37, vals[k], 15, weight='bold')
        sv.text(x + cw * 3 + 8, y + 30, f'= {sum(vals.values())}', 14, PIX, 'start', 'bold')

    row(30, 50, r1, 'replica 1')
    row(320, 50, r2, 'replica 2')
    arrow(sv, mk, 110, 104, 230, 160, GREY)
    arrow(sv, mk, 400, 104, 330, 160, GREY)
    hl = {k: True for k in nodes}
    row(180, 180, m, 'merged: the larger number for each node', hl)
    sv.text(280, 256, 'max is order-free and repeat-safe: merge 1 with 2, 2 with 1,', 12, MUTED)
    sv.text(280, 274, 'or the same message twice, and the total is always 9', 12, MUTED)
    sv.save('sd-g-counter-merge.svg', OUT)


def majority_overlap():
    from itertools import combinations
    n = 5
    q = n // 2 + 1
    assert all(set(a) & set(b) for a in combinations(range(n), q) for b in combinations(range(n), q))
    q1, q2 = {0, 1, 2}, {2, 3, 4}
    sv = Svg(520, 230, 'Two majorities of a five-node cluster: quorum 1 is nodes 1, 2 and 3, quorum 2 is nodes 3, 4 '
             'and 5; any two sets of 3 out of 5 must share at least one node, here node 3, which remembers the '
             'earlier decision')
    xs = [70 + i * 95 for i in range(n)]
    sv.add(f'<rect x="{xs[0] - 34}" y="62" width="{xs[2] - xs[0] + 68}" height="76" rx="36" fill="{PIX}" '
           f'fill-opacity="0.12" stroke="{PIX}" stroke-width="2"/>')
    sv.add(f'<rect x="{xs[2] - 30}" y="70" width="{xs[4] - xs[2] + 60}" height="60" rx="30" fill="{ORANGE}" '
           f'fill-opacity="0.12" stroke="{ORANGE}" stroke-width="2"/>')
    for i, x in enumerate(xs):
        both = i in q1 and i in q2
        sv.circle(x, 100, 22, '#d1fae5' if both else '#ffffff', INK)
        sv.text(x, 105, f'n{i + 1}', 13, weight='bold')
    sv.text(xs[1], 50, 'quorum 1: n1, n2, n3', 13, PIX, weight='bold')
    sv.text(xs[3] + 10, 160, 'quorum 2: n3, n4, n5', 13, '#b45309', weight='bold')
    sv.text(260, 196, f'a quorum is {q} of {n}; any two quorums share a node (here n3)', 13, ACCENT, weight='bold')
    sv.text(260, 216, 'so a new quorum always contains someone who saw the last decision', 12, MUTED)
    sv.save('sd-majority-overlap.svg', OUT)


def paxos_round(name, title, n, reports, own):
    """reports: acceptor -> (accepted_n, value) or None. The proposer must re-propose the value with the highest
    accepted proposal number, or its own value if none was reported."""
    accepted = [r for r in reports.values() if r]
    chosen = max(accepted)[1] if accepted else own
    acc = list(reports)
    q = Seq(['proposer'] + acc, 11.2, title, col=138, row=33,
            lw={a: FILL['db'] for a in acc})
    q.band(0.1, 4.9, f'phase 1: prepare({n}) / promise', '#eff6ff')
    for i, a in enumerate(acc):
        q.msg('proposer', a, f'prepare({n}) to each acceptor' if i == 0 else '', 1.0 + i * 0.6, slope=0.3,
              size=10.5, lab_dy=-4)
    for i, a in enumerate(acc):
        r = reports[a]
        lab = f'promise, had ({r[0]}, {r[1]})' if r else 'promise, nothing'
        q.msg(a, 'proposer', lab, 3.0 + i * 0.65, slope=0.3, size=10.5, color='#b45309' if r else INK)
    q.self_note('proposer', 5.4, f'must propose "{chosen}"' + (
        f' (highest number: {max(accepted)[0]})' if accepted else ' (its own value)'), '#b45309', weight='bold',
        size=12)
    q.band(5.9, 11.0, f'phase 2: accept({n}, "{chosen}") / accepted', '#ecfdf5')
    for i, a in enumerate(acc):
        q.msg('proposer', a, f'accept({n}, "{chosen}") to each acceptor' if i == 0 else '', 6.8 + i * 0.6,
              slope=0.3, size=10.5, lab_dy=-4)
    for i, a in enumerate(acc):
        q.msg(a, 'proposer', f'accepted ({a})', 8.8 + i * 0.6, slope=0.3, size=10.5, color=ACCENT)
    q.self_note('proposer', 10.7, f'a majority accepted: "{chosen}" is chosen', ACCENT, weight='bold', size=12)
    q.save(name)
    return chosen


def raft_roles():
    arch('raft-roles.svg',
         'Raft roles: a follower that hears no leader before its election timeout becomes a candidate; a candidate '
         'that wins votes from a majority becomes leader; a candidate whose vote splits starts a new election; a '
         'candidate or leader that sees a higher term goes back to follower',
         f'''
         F [label="FOLLOWER\\ncopies the leader", fillcolor="#e5e7eb"];
         C [label="CANDIDATE\\nterm + 1, votes for itself,\\nasks everyone for votes", fillcolor="#fef3c7"];
         L [label="LEADER\\ntakes all writes,\\nsends heartbeats", fillcolor="#d1fae5"];
         F -> C [label=" no heartbeat before\\n election timeout "];
         C -> L [label=" votes from a majority ", color="{ACCENT}", fontcolor="{ACCENT}", penwidth=2];
         C -> C [label=" split vote:\\n new election "];
         C -> F [label=" sees a leader or a higher term ", color="{GREY}", fontcolor="{GREY}"];
         L -> F [label=" sees a higher term ", color="{TRUE}", fontcolor="{TRUE}"];
         ''', rankdir='TB', nodesep=0.8, ranksep=0.6)


def raft_election():
    timeouts = {'N1': 260, 'N2': 170, 'N3': 290, 'N4': 220, 'N5': 240}       # ms, picked from 150-300
    cand = min(timeouts, key=timeouts.get)
    others = [n for n in timeouts if n != cand]
    votes = 1 + len(others)                                                  # everyone grants: same term, logs equal
    assert cand == 'N2' and votes >= len(timeouts) // 2 + 1
    q = Seq(list(timeouts), 9.6, 'A Raft election in a five-node cluster: N2 has the shortest random timeout, '
            '170 ms, so it times out first, moves to term 2, votes for itself and sends RequestVote to the other four; '
            'they grant their votes; with a majority N2 becomes leader and sends heartbeats, which reset everyone '
            'else\'s timers', col=112, row=33, lw={cand: '#fef3c7'})
    for n, t in timeouts.items():
        q.self_note(n, 0.3, f'timeout {t} ms', ORANGE if n == cand else MUTED, anchor='middle', dx=0, size=10.5,
                    weight='bold' if n == cand else 'normal')
    q.self_note(cand, 1.3, 'times out first: term 2', '#b45309', anchor='middle', dx=0, size=11, weight='bold')
    for i, n in enumerate(others):
        q.msg(cand, n, 'RequestVote(term 2)' if i == 0 else '', 2.2 + i * 0.35, slope=0.3, size=10)
    for i, n in enumerate(others):
        q.msg(n, cand, 'vote granted' if i == 0 else '', 4.2 + i * 0.35, slope=0.3, size=10, color=ACCENT)
    q.self_note(cand, 6.2, f'{votes} of 5 votes: LEADER', ACCENT, anchor='middle', dx=0, size=11.5, weight='bold')
    for i, n in enumerate(others):
        q.msg(cand, n, 'heartbeat (empty AppendEntries)' if i == 0 else '', 7.0 + i * 0.35, slope=0.3, size=10,
              color=PIX)
    q.self_note('N3', 9.2, 'heartbeats reset the other timers, so nobody else runs', MUTED, anchor='middle', dx=0,
                size=11)
    q.save('raft-election.svg')


def raft_repair(leader, follower):
    """The leader walks prevLogIndex back until the follower has a matching (index, term), then overwrites."""
    tries = []
    nxt = len(leader) + 1
    while True:
        prev = nxt - 1
        ok = prev == 0 or (prev <= len(follower) and follower[prev - 1] == leader[prev - 1])
        tries.append((prev, leader[prev - 1] if prev else 0, ok))
        if ok:
            break
        nxt -= 1
    new = follower[:prev] + leader[prev:]
    assert new == leader
    return tries, prev, new


def draw_raft_repair(name, title, leader, follower):
    tries, match, new = raft_repair(leader, follower)
    n = max(len(leader), len(follower))
    cw, left = 46, 120
    sv = Svg(max(left + cw * n + 30, 500), 150 + 24 * len(tries) + 100, title)
    sv.text(left - 12, 30, 'index', 11, MUTED, 'end')
    for i in range(n):
        sv.text(left + i * cw + cw / 2, 30, i + 1, 12, MUTED)

    def logrow(y, lab, log, hl_from=None, col=FILL['svc']):
        sv.text(left - 12, y + 22, lab, 13, anchor='end', weight='bold')
        for i, t in enumerate(log):
            hot = hl_from is not None and i >= hl_from
            sv.rect(left + i * cw + 2, y, cw - 4, 34, '#fed7aa' if hot else col, ORANGE if hot else INK,
                    2.4 if hot else 1)
            sv.text(left + i * cw + cw / 2, y + 22, f't{t}', 13, weight='bold')

    logrow(42, 'leader', leader, col='#d1fae5')
    logrow(86, 'follower', follower)
    sv.text(left, 146, 'AppendEntries checks (prevLogIndex, prevLogTerm), walking back:', 12, anchor='start',
            weight='bold')
    for k, (prev, term, ok) in enumerate(tries):
        y = 168 + k * 24
        have = follower[prev - 1] if 0 < prev <= len(follower) else None
        why = 'match: accept' if ok else (f'follower has t{have} there: reject' if have else
                                         'follower has no entry there: reject')
        sv.text(left, y, f'{k + 1}. prev = ({prev}, t{term})  ->  {why}', 12, ACCENT if ok else TRUE, 'start')
    y = 168 + len(tries) * 24 + 12
    logrow(y, 'follower after', new, hl_from=match)
    sv.text(left, y + 56, f'entries after index {match} are replaced with the leader\'s (orange)', 12, '#b45309',
            'start', 'bold')
    sv.save('sd-' + name, OUT)
    return tries


def zk_election():
    members = [('worker-A', 1), ('worker-B', 2), ('worker-C', 3)]
    leader = min(members, key=lambda m: m[1])[0]
    assert leader == 'worker-A'
    after = [m for m in members if m[0] != leader]
    assert min(after, key=lambda m: m[1])[0] == 'worker-B'
    arch('zk-election.svg',
         'ZooKeeper leader election: workers A, B and C create ephemeral sequential nodes n_0001, n_0002 and n_0003 '
         'under /election; the lowest, n_0001 (worker A), is the leader; B watches n_0001 and C watches n_0002; if '
         'A dies its node vanishes and B, the next lowest, is told and becomes leader',
         f'''
         root [label="/election", fillcolor="#e5e7eb"];
         a [label="n_0001\\nworker-A\\nLEADER (lowest)", fillcolor="#d1fae5", penwidth=2.2];
         b [label="n_0002\\nworker-B"]; c [label="n_0003\\nworker-C"];
         root -> a; root -> b; root -> c;
         b -> a [label=" watches ", style=dashed, color="{ORANGE}", fontcolor="#b45309", constraint=false];
         c -> b [label=" watches ", style=dashed, color="{ORANGE}", fontcolor="#b45309", constraint=false];
         note [label="if worker-A dies, n_0001 vanishes;\\nB is notified and becomes leader", shape=plaintext,
               style="", fontcolor="{MUTED}"];
         a -> note [style=invis];
         ''', rankdir='TB', nodesep=0.7, ranksep=0.5)


def fencing(name, title, grants, writes, pause_worker):
    """grants: [(worker, token)] in order. writes: [(worker, token)] in arrival order at storage.
    Storage rejects any token lower than the highest it has accepted."""
    highest, results = 0, []
    for w, tok in writes:
        ok = tok >= highest
        if ok:
            highest = tok
        results.append((w, tok, ok))
    actors = ['lock service'] + [w for w, _ in grants] + ['storage']
    q = Seq(actors, 3.4 + 1.9 * len(writes) + len(grants), title, col=124, row=31,
            lw={'lock service': FILL['cache'], 'storage': FILL['db']})
    t = 0.7
    gi = {w: i for i, (w, _) in enumerate(grants)}
    for i, (w, tok) in enumerate(grants):
        q.msg('lock service', w, f'lock, token {tok}', t, slope=0.4, size=10.5)
        t += 0.9
        if w == pause_worker:
            q.s.rect(q.x(w) - 6, q.y(t), 12, q.y(t + 2.4) - q.y(t), ORANGE, opacity=0.4)
            q.self_note(w, t + 1.2, 'GC pause', '#b45309', anchor='start', dx=10, size=11, weight='bold')
            q.self_note('lock service', t + 1.9, 'lease runs out', MUTED, anchor='start', size=10.5)
            t += 2.6
    for w, tok, ok in results:
        q.msg(w, 'storage', f'write, token {tok}', t, slope=0.4, size=10.5, color=ACCENT if ok else TRUE)
        q.self_note('storage', t + 1.0, 'accepted' if ok else f'rejected: {tok} < newest seen', ACCENT if ok else TRUE,
                    anchor='end', size=11, weight='bold')
        t += 1.9
    q.save(name)
    return results


def two_pc(name, title, votes, crash=False):
    decision = 'commit' if all(v == 'yes' for v in votes.values()) else 'abort'
    parts = list(votes)
    q = Seq(['coordinator'] + parts, 10.6, title, col=150, row=31, lw={pp: FILL['db'] for pp in parts})
    q.band(0.1, 4.7, 'phase 1: prepare (vote)', '#eff6ff')
    for i, pp in enumerate(parts):
        q.msg('coordinator', pp, 'prepare: can you commit?' if i == 0 else '', 1.0 + i * 0.6, slope=0.3, size=10.5)
    for i, pp in enumerate(parts):
        v = votes[pp]
        q.msg(pp, 'coordinator', f'{v}' + (' (locked, promised)' if v == 'yes' else ''), 2.8 + i * 0.6, slope=0.3,
              size=10.5, color=ACCENT if v == 'yes' else TRUE)
    if crash:
        q.self_note('coordinator', 5.4, '✗ coordinator crashes before deciding', TRUE, weight='bold', size=12)
        for pp in parts:
            q.s.rect(q.x(pp) - 6, q.y(6.0), 12, q.y(10.2) - q.y(6.0), ORANGE, opacity=0.35)
        q.self_note(parts[-1], 8.0, 'stuck: locks held,', '#b45309', anchor='end', dx=12, weight='bold', size=11.5)
        q.self_note(parts[-1], 8.6, 'cannot decide alone', '#b45309', anchor='end', dx=12, weight='bold', size=11.5)
        q.save(name)
        return None
    q.self_note('coordinator', 5.35, f'writes decision durably: {decision.upper()}', ACCENT if decision == 'commit'
                else TRUE, weight='bold', size=12)
    q.band(5.9, 10.4, f'phase 2: {decision}', '#ecfdf5' if decision == 'commit' else '#fef2f2')
    for i, pp in enumerate(parts):
        q.msg('coordinator', pp, f'{decision}' if i == 0 else '', 6.8 + i * 0.6, slope=0.3, size=10.5,
              color=ACCENT if decision == 'commit' else TRUE)
    for i, pp in enumerate(parts):
        q.msg(pp, 'coordinator', 'done' if i == 0 else '', 8.6 + i * 0.6, slope=0.3, size=10.5)
    q.save(name)
    return decision


def spanner_shards():
    cl = f'fontname="{FONT}"; fontsize=12; color="#9ca3af"; style="rounded,dashed";'
    groups = []
    for g, keys in [('shard 1 (keys A to M)', 'a'), ('shard 2 (keys N to Z)', 'b')]:
        groups.append(f'subgraph cluster_{keys} {{ label="{g}: a Paxos group"; {cl} '
                      f'{keys}1 [label="leader"] {K("db", penwidth="2")}; {keys}2 [label="replica"] {K("db")}; '
                      f'{keys}3 [label="replica"] {K("db")}; {keys}1 -> {keys}2 [color="{PIX}", arrowsize=0.6]; '
                      f'{keys}1 -> {keys}3 [color="{PIX}", arrowsize=0.6]; }}')
    arch('spanner-shards.svg',
         'Spanner\'s structure: each shard is a Paxos group of a leader and replicas; a transaction that touches '
         'two shards runs two-phase commit between the shard leaders, so every participant is a replicated group '
         'rather than one machine that can crash and block',
         f'''
         tx [label="transaction\\n(touches A and P)"] {K('client')};
         {groups[0]}
         {groups[1]}
         tx -> a1 [label=" 2PC "]; tx -> b1 [label=" 2PC "];
         ''', rankdir='TB', nodesep=0.35, ranksep=0.5)


def commit_wait():
    eps = 4                       # TrueTime uncertainty in ms
    start = 100                   # true time when the commit begins
    s_ts = start + eps            # commit timestamp = TT.now().latest
    done = s_ts + eps             # TT.now().earliest = t - eps passes s just after true time s + eps
    assert s_ts == 104 and done == 108 and done - start == 2 * eps
    sv = Svg(580, 240, 'Spanner commit wait with a TrueTime uncertainty of 4 ms: at true time 100 TrueTime says '
             'between 96 and 104, so the commit gets timestamp 104; Spanner then waits until the earliest possible '
             'time is past 104, just after true time 108, twice the uncertainty, before releasing locks')
    X = lambda t: 40 + (t - 92) * 22
    mk = arrow_defs(sv)
    arrow(sv, mk, X(92), 150, X(113), 150, GREY)
    for t in range(92, 113, 2):
        sv.line(X(t), 146, X(t), 154, GREY, 1)
        sv.text(X(t), 172, t, 10.5, GREY)
    sv.text(X(112.5), 192, 'true time (ms)', 11, GREY, 'end')
    for t, lab, col in [(start, 'commit starts', PIX), (done, 'locks released', ACCENT)]:
        sv.line(X(t), 40, X(t), 150, col, 1.6, '4 3')
        sv.text(X(t), 34, lab, 12, col, weight='bold')
    for t, y, col, anc in [(start, 80, PIX, 'end'), (done, 115, ACCENT, 'end')]:
        sv.rect(X(t - eps), y, X(t + eps) - X(t - eps), 18, col, col, 1, 0.2)
        sv.text(X(t + eps) + 6 if anc == 'start' else X(t - eps) - 6, y + 13, f'TrueTime: {t - eps} to {t + eps}', 11,
                col, anc)
    sv.line(X(s_ts), 60, X(s_ts), 150, TRUE, 2.2)
    sv.text(X(s_ts) + 4, 66, f'timestamp s = {s_ts}', 11.5, TRUE, 'start', 'bold')
    sv.rect(X(start), 200, X(done) - X(start), 14, ORANGE, opacity=0.5)
    sv.text((X(start) + X(done)) / 2, 230, f'commit wait: {done - start} ms (2 x the uncertainty)', 12, '#b45309',
            weight='bold')
    sv.save('sd-commit-wait.svg', OUT)


def calvin():
    arch('calvin.svg',
         'Calvin: clients send transactions to a sequencer, which uses a consensus log to fix one global order, T1 '
         'then T2 then T3; every replica executes that same order with deterministic logic, so all replicas reach the '
         'same state with no commit protocol',
         f'''
         c [label="clients"] {K('client')};
         seq [label="sequencer\\n(consensus log)"] {K('lb')};
         log [label="agreed order: T1, T2, T3"] {K('queue')};
         r1 [label="replica 1\\nruns T1, T2, T3"]; r2 [label="replica 2\\nruns T1, T2, T3"];
         r3 [label="replica 3\\nruns T1, T2, T3"];
         s [label="same state everywhere,\\nno 2PC", shape=plaintext, style="", fontcolor="{ACCENT}"];
         c -> seq [label=" transactions "]; seq -> log; log -> r1; log -> r2; log -> r3;
         r2 -> s [style=invis];
         ''', rankdir='TB', nodesep=0.35, ranksep=0.4)


def apply_cmd(state, cmd):
    op, var, val = cmd
    st = dict(state)
    st[var] = {'set': lambda o: val, 'add': lambda o: o + val, 'sub': lambda o: o - val,
               'mul': lambda o: o * val}[op](st.get(var, 0))
    return st


def cmd_text(c):
    op, var, val = c
    return {'set': f'set {var} = {val}', 'add': f'add {val} to {var}', 'sub': f'take {val} from {var}',
            'mul': f'multiply {var} by {val}'}[op]


def rsm_picture(name, title, log, replicas):
    """replicas: [(name, how many log entries applied)]. Each replica's state is computed by applying the log."""
    states = [{}]
    for c in log:
        states.append(apply_cmd(states[-1], c))
    cw = 150 if len(log) < 4 else 128
    sv = Svg(max(130 + cw * len(log) + 20, 600), 96 + 56 * len(replicas) + 40, title)
    mk = arrow_defs(sv)
    sv.text(118, 46, 'the log', 13, anchor='end', weight='bold')
    for i, c in enumerate(log):
        box(sv, 130 + i * cw, 26, cw - 10, 34, FILL['queue'], f'{i + 1}. {cmd_text(c)}', size=11.5)
    fmt = lambda st: ', '.join(f'{k} = {v}' for k, v in sorted(st.items())) or 'empty'
    for r, (nm, applied) in enumerate(replicas):
        y = 96 + r * 56
        sv.text(118, y + 22, nm, 13, anchor='end', weight='bold')
        for i in range(len(log)):
            done = i < applied
            col = '#d1fae5' if done else '#f3f4f6'
            sv.rect(130 + i * cw, y, cw - 10, 34, col, INK if done else '#9ca3af', 1)
            sv.text(130 + i * cw + (cw - 10) / 2, y + 22, fmt(states[i + 1]) if done else 'not yet', 11.5,
                    INK if done else GREY)
        if applied < len(log):
            sv.text(130 + applied * cw + (cw - 10) / 2, y + 50, 'behind, catching up', 10.5, '#b45309')
    sv.text(130, sv.h - 14, 'same start + same commands in the same order = same state on every replica', 12,
            ACCENT, 'start', 'bold')
    sv.save('sd-' + name, OUT)
    return states[-1]


def arc_shares(points):
    """points: {label: degrees}; label's first character is the physical node. Share of the ring each node owns."""
    order = sorted(points, key=points.get)
    share = {}
    for i, lab in enumerate(order):
        a0, a1 = points[order[i - 1]], points[lab]
        share[lab[0]] = share.get(lab[0], 0) + ((a1 - a0) % 360) / 360
    return share


def vnode_rings():
    phys = ['A', 'B', 'C', 'D']
    one = {n: ring_pos(n) for n in phys}
    many = {f'{n}{i}': ring_pos(f'{n}#{i}') for n in phys for i in range(64)}
    s1, s8 = arc_shares(one), arc_shares(many)
    assert abs(sum(s1.values()) - 1) < 1e-9 and abs(sum(s8.values()) - 1) < 1e-9
    assert max(s8.values()) < 0.27 < max(s1.values())   # virtual nodes even out the shares
    sv = Svg(660, 380, 'Virtual nodes: with one point per node on the ring, nodes A to D own very uneven arcs; with '
             '64 points per node, each node owns many small arcs and every share comes out between 22 and 27 '
             'percent, close to a quarter')
    for k, (pts, head, sh) in enumerate([(one, 'one point per node', s1), (many, '64 points per node', s8)]):
        cx, cy, r = 165 + k * 330, 175, 115
        pt = lambda deg, rr: (cx + rr * math.sin(math.radians(deg)), cy - rr * math.cos(math.radians(deg)))
        order = sorted(pts, key=pts.get)
        arcs = []                                  # (start, end, node), merging neighbours with the same owner
        for i, lab in enumerate(order):
            a0, a1 = pts[order[i - 1]], pts[lab]
            if a1 <= a0:
                a1 += 360
            if arcs and arcs[-1][2] == lab[0] and abs(arcs[-1][1] % 360 - a0) < 1e-9:
                arcs[-1] = (arcs[-1][0], arcs[-1][0] + (a1 - arcs[-1][0]) % 360 or 360, lab[0])
            else:
                arcs.append((a0, a1, lab[0]))
        for a0, a1, nd in arcs:
            (x0, y0), (x1, y1) = pt(a0, r), pt(a1, r)
            sv.add(f'<path d="M{x0:.0f} {y0:.0f}A{r} {r} 0 {1 if a1 - a0 > 180 else 0} 1 {x1:.0f} {y1:.0f}" '
                   f'fill="none" stroke="{NODE_COL[nd]}" stroke-width="12" stroke-opacity=".55"/>')
        for lab, d in pts.items():
            if k == 0:
                x, y = pt(d, r)
                sv.circle(x, y, 9, NODE_COL[lab[0]], '#ffffff')
                lx, ly = pt(d, r + 22)
                sv.text(lx, ly + 5, lab, 13, NODE_COL[lab[0]], weight='bold')
        sv.text(cx, 30, head, 14, weight='bold')
        for i, n in enumerate(phys):
            sv.text(cx - 105 + i * 70, 330, f'{n}: {sh[n]:.0%}', 13, NODE_COL[n], weight='bold')
        sv.text(cx, 356, f'biggest share {max(sh.values()):.0%} (fair is 25%)', 12, MUTED)
    sv.save('sd-virtual-nodes.svg', OUT)


def shards_on_nodes():
    nodes, shards, rf = 3, 3, 3
    placement = {sh: [(sh + i) % nodes for i in range(rf)] for sh in range(shards)}   # first = leader
    leaders = [placement[sh][0] for sh in range(shards)]
    assert sorted(leaders) == list(range(nodes))          # one leader per node spreads the write load
    sv = Svg(560, 250, 'Partitioning plus replication: three shards, each copied to all three nodes; each shard\'s '
             'copies form a small Raft group, and each node leads a different shard, so writes are spread across '
             'the nodes and any one node can fail')
    for n in range(nodes):
        x = 30 + n * 175
        sv.add(f'<rect x="{x}" y="40" width="160" height="180" rx="10" fill="{FILL["client"]}" stroke="{INK}"/>')
        sv.text(x + 80, 30, f'node {n + 1}', 13, weight='bold')
        for sh in range(shards):
            lead = placement[sh][0] == n
            y = 56 + sh * 54
            col = ['#dbeafe', '#d1fae5', '#fde68a'][sh]
            sv.rect(x + 14, y, 132, 40, col, ORANGE if lead else INK, 2.6 if lead else 1)
            sv.text(x + 80, y + 18, f'shard {sh + 1}', 12.5, weight='bold')
            sv.text(x + 80, y + 33, 'leader' if lead else 'follower', 11, '#b45309' if lead else MUTED,
                    weight='bold' if lead else 'normal')
    sv.text(280, 242, 'each shard = a 3-copy Raft group; orange = that shard\'s leader', 12, MUTED)
    sv.save('sd-shards-on-nodes.svg', OUT)


def gossip_rounds():
    n, rng = 16, random.Random(7)
    informed, rounds = {0}, [{0}]
    while len(informed) < n:
        new = set(informed)
        for node in sorted(informed):
            new.add(rng.choice([x for x in range(n) if x != node]))      # tell one random peer
        informed = new
        rounds.append(set(informed))
    counts = [len(r) for r in rounds]
    assert counts[0] == 1 and counts[-1] == n and all(a <= b for a, b in zip(counts, counts[1:]))
    cell = 26
    sv = Svg(130 + cell * n + 70, 50 + 34 * len(rounds) + 30,
             f'Gossip in a 16-node cluster where each node that knows the news tells one random peer each round: '
             f'the number who know goes {", ".join(map(str, counts))}, so everyone knows after {len(rounds) - 1} '
             f'rounds, close to log2 of 16 = 4 plus a few rounds of bad luck at the end')
    sv.text(118, 30, 'round', 12, MUTED, 'end')
    for i in range(n):
        sv.text(130 + i * cell + cell / 2, 30, i + 1, 10, GREY)
    for r, inf in enumerate(rounds):
        y = 50 + r * 34
        sv.text(118, y + 16, r, 13, anchor='end', weight='bold')
        prev = rounds[r - 1] if r else set()
        for i in range(n):
            new = i in inf and i not in prev
            sv.circle(130 + i * cell + cell / 2, y + 12, 9, ORANGE if new else PIX if i in inf else '#f3f4f6',
                      INK if i in inf else '#9ca3af')
        sv.text(130 + n * cell + 10, y + 17, f'{len(inf)} know', 12, PIX, 'start', 'bold')
    sv.text(130, sv.h - 10, 'orange = heard it this round; it roughly doubles, then the last few take longer', 11.5,
            MUTED, 'start')
    sv.save('sd-gossip-rounds.svg', OUT)
    return counts


def swim_indirect():
    q = Seq(['A', 'B', 'C', 'D'], 9.4, 'SWIM indirect ping: A pings B and gets no reply because the A to B link is '
            'flaky; instead of declaring B dead, A asks C and D to ping B; B answers them, they pass the acks back to '
            'A, and A keeps B as alive', col=130, row=33, lw={'B': '#fee2e2'})
    q.msg('A', 'B', 'ping', 0.6, slope=0.3, color=TRUE, dash='5 4')
    q.self_note('A', 1.4, 'no reply (A to B link flaky)', TRUE, size=11)
    q.msg('A', 'C', 'ping-req: check B', 2.3, slope=0.3)
    q.msg('A', 'D', 'ping-req: check B', 3.0, slope=0.3)
    q.msg('C', 'B', 'ping', 4.0, slope=0.3)
    q.msg('D', 'B', 'ping', 4.6, slope=0.3)
    q.msg('B', 'C', 'ack', 5.4, slope=0.3, color=ACCENT)
    q.msg('B', 'D', 'ack', 6.0, slope=0.3, color=ACCENT)
    q.msg('C', 'A', 'B is alive', 6.9, slope=0.3, color=ACCENT)
    q.msg('D', 'A', 'B is alive', 7.6, slope=0.3, color=ACCENT)
    q.self_note('A', 8.8, 'B stays in the cluster: a false alarm avoided', ACCENT, weight='bold', size=11.5)
    q.save('swim-indirect-ping.svg')


def merkle_compare():
    h = lambda x: hashlib.sha256(x.encode()).hexdigest()[:6]
    r1 = {'k1': 'red', 'k2': 'blue', 'k3': 'green', 'k4': 'gold'}
    r2 = dict(r1, k3='grey')                      # one key differs
    def tree(d):
        leaves = [h(f'{k}={d[k]}') for k in sorted(d)]
        mid = [h(leaves[0] + leaves[1]), h(leaves[2] + leaves[3])]
        return leaves, mid, h(mid[0] + mid[1])
    l1, m1, t1 = tree(r1)
    l2, m2, t2 = tree(r2)
    assert t1 != t2 and m1[0] == m2[0] and m1[1] != m2[1] and [a != b for a, b in zip(l1, l2)] == [0, 0, 1, 0]
    cl = f'fontname="{FONT}"; fontsize=13; color="#9ca3af"; style="rounded,dashed";'
    body = []
    for tag, (lv, md, top), data in [('a', tree(r1), r1), ('b', tree(r2), r2)]:
        other = tree(r2 if tag == 'a' else r1)
        diff = lambda x, y: f', color="{TRUE}", penwidth=2.6' if x != y else ''
        body.append(f'subgraph cluster_{tag} {{ label="replica {1 if tag == "a" else 2}"; {cl}')
        body.append(f'{tag}r [label="root\\n{top}"{diff(top, other[2])}];')
        for i in range(2):
            body.append(f'{tag}m{i} [label="{["k1, k2", "k3, k4"][i]}\\n{md[i]}"{diff(md[i], other[1][i])}];'
                        f'{tag}r -> {tag}m{i};')
        for i, k in enumerate(sorted(data)):
            body.append(f'{tag}l{i} [label="{k} = {data[k]}\\n{lv[i]}", fillcolor="#d1fae5"'
                        f'{diff(lv[i], other[0][i])}]; {tag}m{i // 2} -> {tag}l{i};')
        body.append('}')
    arch('merkle-compare.svg',
         'Comparing two replicas with Merkle trees: each leaf hashes one key, each parent hashes its children; the '
         'roots differ, so the replicas compare the next level down; the k1, k2 branch matches and is skipped; the '
         'k3, k4 branch differs, and below it only k3 differs (green on replica 1, grey on replica 2), so only k3 is '
         'sent', '\n'.join(body), rankdir='TB', nodesep=0.15, ranksep=0.35)


def doubling_tree(name, title, n):
    """Idealised gossip: in round r, node i (already informed) tells node i + 2^(r-1)."""
    informed, edges, r = {1}, [], 0
    while len(informed) < n:
        r += 1
        step = 2 ** (r - 1)
        for i in sorted(informed):
            if i + step <= n:
                edges.append((i, i + step, r))
        informed |= {i + step for i in informed if i + step <= n}
    assert r == math.ceil(math.log2(n)) and len(informed) == n
    cols = {1: PIX, 2: ACCENT, 3: ORANGE, 4: TRUE}
    body = [f'n{i} [label="node {i}"];' for i in range(1, n + 1)]
    body.append('n1 [fillcolor="#fde68a"];')
    for a, b, rr in edges:
        body.append(f'n{a} -> n{b} [label=" round {rr} ", color="{cols[rr]}", fontcolor="{cols[rr]}", penwidth=2];')
    arch(name, title, '\n'.join(body), rankdir='TB', nodesep=0.25, ranksep=0.45)
    return r


def jepsen_loop():
    arch('jepsen-loop.svg',
         'How Jepsen tests a database: many clients run concurrent operations against the real cluster while a '
         'nemesis injects partitions, crashes, pauses and clock skew; every operation and result is recorded in a '
         'history; a checker such as Knossos or Elle asks whether any single-machine order explains the history, '
         'and either passes it or prints the exact counterexample',
         f'''
         w [label="clients\\n(concurrent workload)"] {K('client')};
         n [label="nemesis\\npartitions, crashes,\\npauses, clock skew"] {K('bad')};
         db [label="the real cluster"] {K('db')};
         h [label="history\\nevery call and result,\\nwith times"] {K('queue')};
         c [label="checker (Knossos, Elle)\\nis there a valid single-machine order?"];
         ok [label="pass"] {K('db')};
         bad [label="violation:\\nexact counterexample"] {K('bad')};
         w -> db [label=" operations "]; n -> db [label=" faults ", color="{TRUE}", fontcolor="{TRUE}"];
         db -> h [label=" record "]; h -> c; c -> ok [label=" yes "]; c -> bad [label=" no "];
         {{rank=same; w; n}}
         ''', rankdir='TB', nodesep=0.5, ranksep=0.4)


def deterministic_sim():
    arch('deterministic-sim.svg',
         'Deterministic simulation: a seed drives a random number generator inside a simulator that controls the '
         'network, the clock and the disk; the whole system runs single-threaded inside it; the same seed replays '
         'exactly the same run, so a failing seed reproduces its bug every time, and sweeping many seeds explores '
         'many bad days',
         f'''
         seed [label="seed 4071"] {K('queue')};
         subgraph cluster_sim {{ label="simulator (single-threaded)"; fontname="{FONT}"; fontsize=12;
           color="#9ca3af"; style="rounded,dashed";
           rng [label="random number\\ngenerator"] {K('cache')};
           net [label="simulated network\\ndelays, drops, reorders"]; clk [label="simulated clock"];
           dsk [label="simulated disk\\nfaults"];
           sys [label="the system's nodes"] {K('db')};
           rng -> net; rng -> clk; rng -> dsk; net -> sys; clk -> sys; dsk -> sys;
         }}
         out [label="same seed = same run:\\na bug found once replays every time", shape=plaintext, style="",
              fontcolor="{ACCENT}"];
         seed -> rng; sys -> out [style=invis];
         ''', rankdir='TB', nodesep=0.3, ranksep=0.4)


# ======================================================= 05 case studies

def base62(n):
    digits = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    out = ''
    while True:
        n, r = divmod(n, 62)
        out = digits[r] + out
        if not n:
            return out


def url_shortener():
    code = base62(125)
    assert code == '21'                     # 125 = 2 x 62 + 1
    arch('url-shortener.svg',
         'URL shortener: to create, the app server takes the next number from an ID generator, turns it into a '
         'short base-62 code (125 becomes 21) and stores code to long URL in a key-value store; to redirect, a '
         'GET for the code goes through the load balancer to an app server that checks the cache first and the '
         'store on a miss, then answers 301 with the long URL',
         f'''
         u [label="users"] {K('client')};
         lb [label="load balancer"] {K('lb')};
         app [label="app servers\\n(stateless)"];
         id [label="ID generator\\n(counter ranges)"] {K('cache')};
         c [label="cache\\nhot codes"] {K('cache')};
         kv [label="key-value store\\ncode -> long URL"] {K('db')};
         u -> lb [label=" POST long URL\\n GET /21 "]; lb -> app;
         app -> id [label=" create: next id 125\\n -> code 21 "];
         app -> c [label=" redirect: 1. cache "];
         app -> kv [label=" 2. on a miss; create: save "];
         ''', rankdir='TB', nodesep=0.5, ranksep=0.5)


def fanout():
    cl = f'fontname="{FONT}"; fontsize=13; color="#9ca3af"; style="rounded,dashed";'
    arch('feed-fanout.svg',
         'Fan-out on write against fan-out on read. On write: when Ada posts, the post is pushed into each '
         'follower\'s precomputed timeline, so reading is one lookup but a celebrity\'s post means millions of '
         'writes. On read: the post is stored once, and a follower\'s timeline is assembled at read time from '
         'everyone they follow, so writes are cheap and reads are slow',
         f'''
         subgraph cluster_w {{ label="fan-out on write (push)"; {cl}
           p1 [label="Ada posts"] {K('client')};
           t1 [label="Ben\\'s timeline"] {K('cache')}; t2 [label="Cy\\'s timeline"] {K('cache')};
           t3 [label="Dee\\'s timeline"] {K('cache')};
           p1 -> t1; p1 -> t2; p1 -> t3;
           r1 [label="Ben reads:\\none lookup"] {K('client')}; t1 -> r1;
         }}
         subgraph cluster_r {{ label="fan-out on read (pull)"; {cl}
           p2 [label="Ada posts"] {K('client')};
           s2 [label="posts store\\n(stored once)"] {K('db')};
           p2 -> s2;
           r2 [label="Ben reads: gather posts\\nfrom all he follows"] {K('client')};
           s2 -> r2 [label=" merge at\\n read time ", dir=back];
         }}
         ''', rankdir='TB', nodesep=0.3, ranksep=0.4)


def token_bucket():
    cap, rate = 3, 1.0                              # 3 tokens, refill 1 a second
    reqs = [0.0, 0.2, 0.4, 0.6, 0.8, 2.0, 2.1, 2.2, 4.5]
    tokens, last, res, levels = cap, 0.0, [], []
    for t in reqs:
        tokens = min(cap, tokens + (t - last) * rate)
        last = t
        ok = tokens >= 1
        if ok:
            tokens -= 1
        res.append(ok)
        levels.append(tokens)
    assert res == [True, True, True, False, False, True, True, False, True]
    sv = Svg(580, 230, 'A token bucket holding 3 tokens and refilling 1 a second: of five requests in the first '
             'second, three are allowed and two rejected; by 2 seconds two tokens have come back, so two of the '
             'three requests at 2.0, 2.1 and 2.2 seconds are allowed and the third is rejected; at 4.5 seconds the '
             'bucket has refilled and the request is allowed')
    X = lambda t: 40 + t * 100
    mk = arrow_defs(sv)
    arrow(sv, mk, X(0) - 10, 150, X(5), 150, GREY)
    for t in range(6):
        sv.line(X(t), 145, X(t), 155, GREY)
        sv.text(X(t), 172, f'{t} s', 11, GREY)
    seen = {}
    for t, ok, lv in zip(reqs, res, levels):
        k = round(t)
        dy = seen.get(k, 0)
        seen[k] = dy + 1
        col = ACCENT if ok else TRUE
        sv.line(X(t), 150, X(t), 110, col, 2)
        sv.circle(X(t), 104, 6, col)
        sv.text(X(t), 92, '✓' if ok else '✗', 13, col, weight='bold')
    sv.text(20, 30, 'bucket: 3 tokens, +1 token a second; each request spends one', 13, anchor='start', weight='bold')
    sv.text(20, 50, 'green = allowed, red = rejected (bucket below 1 token)', 12, MUTED, 'start')
    sv.text(X(0.4), 200, '5 at once: 3 pass', 11.5, MUTED)
    sv.text(X(2.1), 200, '2 tokens back: 2 of 3 pass', 11.5, MUTED)
    sv.text(X(4.5), 200, 'full again', 11.5, MUTED)
    sv.save('sd-token-bucket.svg', OUT)
    return res


def chat_system():
    arch('chat-system.svg',
         'A chat system: Ada and Ben each hold a WebSocket to a chat server; Ada\'s message is saved with an id to '
         'the message store, the presence service says which server holds Ben\'s connection, and the message goes '
         'through a queue to that server, which pushes it to Ben; if Ben is offline it waits for him',
         f'''
         a [label="Ada\\'s phone"] {K('client')}; b [label="Ben\\'s phone"] {K('client')};
         s1 [label="chat server 1"]; s2 [label="chat server 2"];
         pr [label="presence\\nwho is on which server"] {K('cache')};
         q [label="message queue"] {K('queue')};
         st [label="message store\\n(id per message, dedup)"] {K('db')};
         a -> s1 [label=" WebSocket ", dir=both]; b -> s2 [label=" WebSocket ", dir=both];
         s1 -> st [label=" save "]; s1 -> pr [label=" where is Ben? "]; s1 -> q; q -> s2 [label=" deliver "];
         {{rank=same; s1; s2}}
         ''', rankdir='TB', nodesep=0.6, ranksep=0.5)


def pastebin_sketch():
    arch('sketch-pastebin.svg',
         'Answer sketch for a paste-sharing service: users go through a load balancer to stateless app servers; '
         'creating a paste takes an id from an ID generator, stores the text in object storage and the details in '
         'a metadata database; reading goes through a CDN and a cache for popular pastes before the stores',
         f'''
         u [label="users"] {K('client')};
         cdn [label="CDN\\n(popular pastes)"] {K('lb')};
         lb [label="load balancer"] {K('lb')};
         app [label="app servers\\n(stateless)"];
         id [label="ID generator\\n-> short code"] {K('cache')};
         c [label="cache"] {K('cache')};
         obj [label="object storage\\npaste text"] {K('db')};
         db [label="metadata database\\ncode, owner, expiry"] {K('db')};
         u -> cdn [label=" read "]; cdn -> lb [label=" miss "]; u -> lb [label=" create "]; lb -> app;
         app -> id; app -> c; app -> obj; app -> db;
         ''', rankdir='TB', nodesep=0.4, ranksep=0.45)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    leaderboard()
    fenwick()
    photo_app_sketch()
    waiting_curve()
    checkout_bottleneck()
    scaling_ceiling()
    bottleneck_sketch()
    availability_pictures()
    cap_partition()
    health_checks()
    lb_pictures()
    shop_front_door()
    lb_sketch()
    cache_layers()
    cache_aside('cache-aside.svg', 'Cache-aside in three parts: on a read miss the app asks the cache, reads price 10 '
                'from the database and stores it with a TTL; the next read is a hit; on a write the app updates the '
                'database to 12 and then deletes the cached entry', 'p42', 10, 12)
    cache_aside('sketch-cache-aside.svg', 'Answer sketch: user 1 reads product 9 and misses, so the app reads 25 from '
                'the database and caches it; user 2 hits the cache; staff change the price to 30, so the app updates '
                'the database and deletes the cache entry', 'p9', 25, 30)
    stale_race()
    leader_followers()
    shard_table('shard-range-vs-hash.svg', 'User ids 1 to 12 on 3 shards. By range: shard 0 holds 1 to 4, shard 1 '
                'holds 5 to 8, shard 2 holds 9 to 12. By hash (id mod 3): shard 0 holds 3, 6, 9, 12; shard 1 holds '
                '1, 4, 7, 10; shard 2 holds 2, 5, 8, 11', list(range(1, 13)), 3, 4, 'user id')
    r, h = shard_table('sketch-shards.svg', 'Answer sketch: order ids 101 to 112 on 4 shards. By range: 101 to 103, '
                       '104 to 106, 107 to 109, 110 to 112. By hash (id mod 4): shard 0 holds 104, 108, 112; shard 1 '
                       'holds 101, 105, 109; shard 2 holds 102, 106, 110; shard 3 holds 103, 107, 111',
                       list(range(101, 113)), 4, 3, 'order id')
    assert h[0] == [104, 108, 112] and r[3] == [110, 111, 112]
    queue_lifecycle()
    call_shapes('rest-vs-graphql.svg', 'The order page over REST and over GraphQL. REST: round trip 1 is GET '
                '/orders/o1; round trip 2 sends GET /customers/c1 and GET /products/p1, p2 and p3 together; five '
                'requests, two round trips, 300 ms on a 150 ms connection, 912 bytes. GraphQL: one POST naming the '
                'fields, one round trip, 150 ms, 203 bytes',
                [['GET /orders/o1'], ['GET /customers/c1', 'GET /products/p1', 'GET /products/p2', 'GET /products/p3']],
                ['{ order(id: "o1") {', 'id totalPence', 'customer { name }', 'items { quantity', 'product { name } } } }'],
                912, 203, 150)
    call_shapes('sketch-rest-graphql.svg', 'Answer sketch for the profile page. REST: round trip 1 is GET /users/u7; '
                'round trip 2 sends GET /teams/t2, GET /posts/p41 and GET /posts/p42 together; four requests, two round '
                'trips, 200 ms on a 100 ms connection. GraphQL: one POST, one round trip, 100 ms',
                [['GET /users/u7'], ['GET /teams/t2', 'GET /posts/p41', 'GET /posts/p42']],
                ['{ user(id: "u7") {', 'name', 'team { name }', 'posts(last: 2)', '{ title } } }'],
                'every field of each resource', 'only the fields asked for', 100)
    varint_picture()
    chain_timing()
    push_styles()
    cyc = module_graph('module-cycle.svg', 'The shop\'s module dependencies: orders uses catalog, billing and '
                       'catalog/internal/prices, which breaks the no-reaching-inside rule; orders uses billing, billing '
                       'uses customers and customers uses orders, which is a cycle',
                       [('orders', 'catalog'), ('orders', 'catalog/internal/prices'), ('orders', 'billing'),
                        ('billing', 'customers'), ('customers', 'orders')])
    assert cyc == ['orders', 'billing', 'customers', 'orders']
    cyc = module_graph('sketch-module-cycle.svg', 'Answer sketch: payments uses inventory and notifications; inventory '
                       'uses shipping; shipping uses notifications; notifications uses inventory, which closes the '
                       'cycle inventory, shipping, notifications, inventory',
                       [('payments', 'inventory'), ('payments', 'notifications'), ('inventory', 'shipping'),
                        ('shipping', 'notifications'), ('notifications', 'inventory')])
    assert cyc == ['inventory', 'shipping', 'notifications', 'inventory']
    architecture_shapes()
    serverless_breakeven()
    strangler_fig()
    circuit_breaker('circuit-breaker.svg', 'The circuit breaker\'s three states: closed passes calls through and '
                    'counts failures; after enough failures in a row it opens and fails every call at once; after a '
                    'cool-down it goes half-open and lets one trial call through; success closes it, failure opens it '
                    'again', 'enough', 'a cool-down')
    circuit_breaker('sketch-circuit-breaker.svg', 'Answer sketch: closed until 5 failures in a row, then open; after '
                    '30 seconds half-open with one trial call; a successful trial closes the breaker, a failed one '
                    'opens it again for another 30 seconds', '5', '30 s')
    bulkheads()
    undo = saga_picture('saga-compensation.svg', 'A saga for an order: Order and Payment succeed, Inventory fails, '
                        'Shipping never runs; the compensations then run backwards: refund the payment, then cancel '
                        'the order', ['Order', 'Payment', 'Inventory', 'Shipping'], 2,
                        {'Order': 'cancel order', 'Payment': 'refund payment'})
    assert undo == ['refund payment', 'cancel order']
    cqrs_picture()
    event_sourcing()
    discovery()
    gateway_bff()
    sidecar()
    dual_write()
    outbox_flow()
    relay_duplicate('outbox-relay-duplicate.svg', 'The relay crashes after publishing OrderPlaced for order o5 but '
                    'before marking it sent; on restart it publishes the same event again; the consumer applies the '
                    'first copy and skips the second as a duplicate, because it has seen the event id',
                    'OrderPlaced evt-o5', 'o5')
    no_reply_cases()
    two_generals()
    quorum_partition()
    lamport_trace()
    vector_siblings()
    clock_skew()
    vector_sketch()
    read_your_writes()
    sync_async()
    g_counter()
    majority_overlap()
    raft_roles()
    zk_election()
    spanner_shards()
    commit_wait()
    calvin()
    ring_before_after('ring-add-d.svg', 'Consistent hashing on a ring with nodes A, B and C: each key belongs to the '
                      'first node clockwise; when node D joins, only the keys in the arc just before D change owner, '
                      'and they all move to D', ['A', 'B', 'C'], 'D',
                      spread_keys([f'user{i}' for i in range(1, 300)], 'ABCD', 10))
    # the sketch question quotes rounded positions; check the rounded ring gives the same owners
    sk = spread_keys([f'k{i}' for i in range(1, 300)], 'ABCD', 10)
    rounded = {k: round(ring_pos(k)) for k in sk}
    assert rounded == {'k1': 256, 'k2': 137, 'k4': 283, 'k6': 109, 'k7': 3, 'k10': 318, 'k12': 35, 'k13': 234,
                       'k17': 165, 'k18': 336}
    nb = {n: round(ring_pos(n)) for n in 'ABCD'}
    assert nb == {'A': 180, 'B': 221, 'C': 19, 'D': 346}
    for k in sk:
        for ns in ('BCD', 'ABCD'):
            assert ring_owner(rounded[k], {n: nb[n] for n in ns}) == ring_owner(ring_pos(k), {n: ring_pos(n) for n in ns})
    ring_before_after('sketch-ring.svg', 'Answer sketch: nodes B, C and D on the ring with ten keys k1 to k10 owned '
                      'by the first node clockwise; adding node A moves only the keys between C and A, all to A',
                      ['B', 'C', 'D'], 'A', spread_keys([f'k{i}' for i in range(1, 300)], 'ABCD', 10))
    vnode_rings()
    gossip_rounds()
    swim_indirect()
    merkle_compare()
    jepsen_loop()
    deterministic_sim()
    url_shortener()
    fanout()
    token_bucket()
    chat_system()
    pastebin_sketch()
    assert doubling_tree('sketch-gossip.svg', 'Answer sketch: node 1 knows the news; in round 1 it tells node 2; in '
                         'round 2 nodes 1 and 2 tell 3 and 4; in round 3 nodes 1 to 4 tell 5 to 8; all 8 nodes know '
                         'after 3 rounds, which is log2 of 8', 8) == 3
    shards_on_nodes()
    assert rsm_picture('replicated-state-machine.svg', 'A replicated state machine: the log is set balance = 100, add '
                       '50 to balance, take 30 from balance; replicas 1 and 2 apply all three and both reach balance '
                       '120; replica 3 has applied two so far and shows 150, and will reach 120 when it applies the '
                       'third', [('set', 'balance', 100), ('add', 'balance', 50), ('sub', 'balance', 30)],
                       [('replica 1', 3), ('replica 2', 3), ('replica 3', 2)]) == {'balance': 120}
    assert rsm_picture('sketch-rsm.svg', 'Answer sketch: the log is set x = 1, add 4 to x, set y = 3, multiply x by '
                       '3; after each entry both replicas hold x = 1, then x = 5, then x = 5 and y = 3, then x = 15 '
                       'and y = 3', [('set', 'x', 1), ('add', 'x', 4), ('set', 'y', 3), ('mul', 'x', 3)],
                       [('replica 1', 4), ('replica 2', 4)]) == {'x': 15, 'y': 3}
    assert two_pc('two-phase-commit.svg', 'Two-phase commit: the coordinator asks node 1 (debit A) and node 2 (credit '
                  'B) to prepare; both lock the data and vote yes; the coordinator writes COMMIT durably and tells both '
                  'to commit; both reply done', {'node 1 (debit A)': 'yes', 'node 2 (credit B)': 'yes'}) == 'commit'
    two_pc('two-pc-blocking.svg', 'Two-phase commit blocking: both participants vote yes and hold their locks, then '
           'the coordinator crashes before announcing a decision; the participants are stuck, unable to commit or '
           'abort on their own until it recovers', {'node 1 (debit A)': 'yes', 'node 2 (credit B)': 'yes'}, crash=True)
    assert two_pc('sketch-2pc.svg', 'Answer sketch: the coordinator sends prepare to stock, payments and shipping; '
                  'stock and payments vote yes, shipping votes no; the coordinator writes ABORT and tells all three '
                  'to abort; they reply done', {'stock': 'yes', 'payments': 'yes', 'shipping': 'no'}) == 'abort'
    r = fencing('fencing-tokens.svg', 'Fencing tokens: worker A gets the lock with token 33, then pauses; the lease '
                'runs out and worker B gets the lock with token 34 and writes, which storage accepts; A wakes and '
                'writes with token 33, which storage rejects because it has already seen 34',
                [('worker A', 33), ('worker B', 34)], [('worker B', 34), ('worker A', 33)], 'worker A')
    assert [ok for *_, ok in r] == [True, False]
    r = fencing('sketch-fencing.svg', 'Answer sketch: worker A gets token 7 and pauses; the lease runs out; worker B '
                'gets token 8 and worker C token 9; B writes with 8, accepted; A wakes and writes with 7, rejected; '
                'C writes with 9, accepted', [('worker A', 7), ('worker B', 8), ('worker C', 9)],
                [('worker B', 8), ('worker A', 7), ('worker C', 9)], 'worker A')
    assert [ok for *_, ok in r] == [True, False, True]
    raft_election()
    t = draw_raft_repair('raft-log-repair.svg', 'Raft log repair: the leader\'s log has terms 1, 1, 2, 3, 3, 3 and the '
                         'follower\'s has 1, 1, 2, 2, 2; the leader tries prevLogIndex 6, 5 and 4, which the follower '
                         'rejects, then 3 with term 2, which matches; the follower keeps entries 1 to 3 and takes '
                         'the leader\'s entries 4 to 6', [1, 1, 2, 3, 3, 3], [1, 1, 2, 2, 2])
    assert [p for p, _, _ in t] == [6, 5, 4, 3]
    t = draw_raft_repair('sketch-raft-repair.svg', 'Answer sketch: leader log 1, 2, 2, 4, 4; follower log 1, 2, 3, 3, '
                         '3, 3; the leader tries prevLogIndex 5, 4 and 3, which are rejected, then 2 with term 2, '
                         'which matches; the follower ends with 1, 2, 2, 4, 4, dropping its extra sixth entry',
                         [1, 2, 2, 4, 4], [1, 2, 3, 3, 3, 3])
    assert [p for p, _, _ in t] == [5, 4, 3, 2]
    assert paxos_round('paxos-round.svg', 'One round of single-decree Paxos with proposal number 5: the proposer '
                       'sends prepare(5) to three acceptors; A1 and A3 promise with nothing accepted, A2 promises and '
                       'reports it already accepted value x under proposal 3; so the proposer must send accept(5, x), '
                       'not its own value, and when a majority accepts, x is chosen', 5,
                       {'A1': None, 'A2': (3, 'x'), 'A3': None}, 'y') == 'x'
    assert paxos_round('sketch-paxos.svg', 'Answer sketch: the proposer sends prepare(8); A1 promises with nothing, '
                       'A2 reports (4, red) and A3 reports (6, blue); the highest accepted number is 6, so the '
                       'proposer sends accept(8, blue) and blue is chosen when a majority accepts', 8,
                       {'A1': None, 'A2': (4, 'red'), 'A3': (6, 'blue')}, 'green') == 'blue'
    multi_leader()
    quorum_overlap('quorum-overlap.svg', 'Quorum overlap with N = 3, W = 2, R = 2: the write reaches r1 and r2; the '
                   'three possible read sets r1 r2, r1 r3 and r2 r3 each include at least one of r1 or r2, so every '
                   'read sees the new write', 3, [1, 2], [[1, 2], [1, 3], [2, 3]], 2, 2)
    quorum_overlap('sketch-quorum.svg', 'Answer sketch with N = 5, W = 3, R = 3: the write reaches r1, r2 and r3; a '
                   'read that tries to avoid them can take r4 and r5 but must still take one of r1 to r3, so it '
                   'shares at least one copy (3 + 3 - 5 = 1)', 5, [1, 2, 3], [[3, 4, 5], [1, 4, 5]], 3, 3)
    relay_duplicate('sketch-relay-duplicate.svg', 'Answer sketch: the relay publishes PaymentCaptured evt-p9, the '
                    'consumer applies it, the relay crashes before marking it sent, restarts, finds the row still '
                    'unpublished and publishes it again; the consumer skips the second copy as a duplicate; then the '
                    'relay marks the row published', 'PaymentCaptured evt-p9', 'p9')
    load_levelling()
    queue_topic_log()
    order_pipeline('order-pipeline.svg', 'The shop\'s order pipeline: checkout saves the order, payment, stock and an '
                   'outbox row in one transaction; a relay publishes to the orders topic; its three subscriptions are '
                   'an invoices queue, an analytics queue and a warehouse log partitioned by order id, each with its '
                   'own idempotent consumers', ('checkout', 'order + payment + stock'), 'orders',
                   [('invoices', 'queue, 2 workers', 'invoice workers\\n(unique order id)'),
                    ('analytics', 'queue', 'analytics\\n(upsert by message id)'),
                    ('warehouse', 'log, keyed by order id', 'warehouse\\n(idempotency key)')])
    order_pipeline('sketch-fanout.svg', 'Answer sketch: the payments service saves the payment and an outbox row '
                   'in one transaction; a relay publishes to the payment-received topic; three subscriptions get a '
                   'copy each: an email queue with two workers, a ledger queue with one worker, and a fraud log '
                   'partitioned by account id', ('payments', 'payment + outbox row'), 'payment-received',
                   [('email', 'queue', '2 email workers'),
                    ('ledger', 'queue', '1 ledger worker'),
                    ('fraud', 'log, keyed by account id', 'fraud checker')])
