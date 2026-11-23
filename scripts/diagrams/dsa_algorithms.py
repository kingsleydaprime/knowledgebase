"""Draw the DSA algorithms lesson diagrams (dsa/03-algorithms) as small SVG files.

    python3 scripts/diagrams/dsa_algorithms.py      # run from the vault root

Every picture is computed by running the algorithm the lesson teaches on the
lesson's own data, and the lesson's numbers are asserted before anything is
drawn, so a picture can never disagree with the text. Trees use Graphviz
(`dot`, which must be installed). Output: dsa/images/alg-*.svg.
"""
import math
import os
import re
import sys
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, PIX, PIX2, TRUE, ACCENT, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('dsa', 'images')
ORANGE = '#f59e0b'
GREY = '#9ca3af'
LIGHT = '#f3f4f6'
BLUE_BG = '#dbeafe'
GREEN_BG = '#d1fae5'
YELLOW_BG = '#fef3c7'
RED_BG = '#fee2e2'


def esc(v):
    return str(v).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def save(s, name):
    if not getattr(s, 'grouped', False):
        s.title = esc(s.title)
    # one group carries the default text style, so the many small labels can be short <t> tags
    if not getattr(s, 'grouped', False):
        s.parts = [f'<g font-family="system-ui, sans-serif" font-size="12" text-anchor="middle" fill="{INK}">'] + \
            s.parts + ['</g>']
        s.grouped = True
    s.save('alg-' + name, OUT)


def t(s, x, y, v, size=None, color=None, weight=None):
    """A short text tag that inherits the group's default style."""
    v = str(v).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    extra = (f' font-size="{size}"' if size else '') + (f' fill="{color}"' if color else '') + \
        (f' font-weight="{weight}"' if weight else '')
    s.add(f'<text x="{x:.0f}" y="{y:.0f}"{extra}>{v}</text>')


def r(s, x, y, w, h, fill, stroke=None, width=1):
    st = (f' stroke="{stroke}"' + (f' stroke-width="{width}"' if width != 1 else '')) if stroke else ''
    s.add(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{fill}"{st}/>')


def dot(src, name, title):
    save_dot(src, 'alg-' + name, title.replace('&', 'and').replace('<', 'less than').replace('>', 'more than'), OUT)
    # Graphviz writes coordinates with many decimals; one is plenty and keeps the files small
    path = os.path.join(OUT, 'alg-' + name)
    svg = open(path).read()
    svg = re.sub(r'(?<![#\w])(-?\d+\.\d{2,})', lambda m: f'{float(m.group()):.1f}', svg)
    svg = re.sub(r'(?<=\d)\.0(?=[^\d])', '', svg)
    svg = re.sub(r'\n<g id="(node|edge)\d+" class="(node|edge)">', '\n<g>', svg)
    open(path, 'w').write(svg)


# ---------- shared drawing helpers ----------

class Plot:
    """Data coordinates to SVG pixels, with axes, ticks and labels."""

    def __init__(self, s, x0, y0, w, h, xr, yr):
        self.s, self.x0, self.y0, self.w, self.h, self.xr, self.yr = s, x0, y0, w, h, xr, yr

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def axes(self, xlabel, ylabel, xticks=(), yticks=()):
        s = self.s
        for t in xticks:
            s.line(self.X(t), self.y0, self.X(t), self.y0 + self.h, '#eef2f6', 1)
            s.text(self.X(t), self.y0 + self.h + 16, f'{t:g}', 11)
        for t in yticks:
            s.line(self.x0, self.Y(t), self.x0 + self.w, self.Y(t), '#eef2f6', 1)
            s.text(self.x0 - 8, self.Y(t) + 4, f'{t:g}', 11, anchor='end')
        s.line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, INK, 1.2)
        s.line(self.x0, self.y0, self.x0, self.y0 + self.h, INK, 1.2)
        s.text(self.x0 + self.w / 2, self.y0 + self.h + 34, xlabel, 12)
        s.add(f'<text x="{self.x0 - 38:.1f}" y="{self.y0 + self.h / 2:.1f}" font-size="12" fill="{INK}" '
              f'text-anchor="middle" font-family="system-ui, sans-serif" '
              f'transform="rotate(-90 {self.x0 - 38:.1f} {self.y0 + self.h / 2:.1f})">{ylabel}</text>')

    def curve(self, pts, color, width=2.5, dash=None):
        self.s.path('M ' + ' L '.join(f'{self.X(x):.1f} {self.Y(y):.1f}' for x, y in pts), color, width, dash=dash)

    def dot(self, x, y, color, r=4.5):
        self.s.circle(self.X(x), self.Y(y), r, color)


def arrow_defs(s, colors=(INK, PIX, TRUE, ORANGE, ACCENT, GREY)):
    s.add('<defs>' + ''.join(
        f'<marker id="a{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for i, c in enumerate(colors))
        + '</defs>')
    return {c: f'url(#a{i})' for i, c in enumerate(colors)}


def arrow(s, mk, x1, y1, x2, y2, color=INK, width=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
          f'stroke-width="{width}"{d} marker-end="{mk[color]}"/>')


def cells(s, x, y, vals, cw=34, ch=30, fill=None, outline=None, index=True, size=13, idx_from=0, dim=()):
    """Draw one row of array cells. fill/outline: dict index -> colour. dim: indexes drawn greyed out."""
    fill, outline = fill or {}, outline or {}
    for i, v in enumerate(vals):
        f = fill.get(i, LIGHT if i in dim else '#ffffff')
        r(s, x + i * cw, y, cw, ch, f, INK)
        t(s, x + i * cw + cw / 2, y + ch / 2 + size * 0.36, v, size if size != 12 else None, GREY if i in dim else None)
        if index:
            t(s, x + i * cw + cw / 2, y - 6, i + idx_from, 10, '#6b7280')
    for i, c in outline.items():
        r(s, x + i * cw + 1.5, y + 1.5, cw - 3, ch - 3, 'none', c, 3)


def table(s, x, y, rows, cw, ch, header_rows=1, header_cols=1, fill=None, size=12, colw=None):
    """Draw a grid of strings. fill: dict (r, c) -> colour."""
    fill = fill or {}
    colw = colw or [cw] * len(rows[0])
    for r, row in enumerate(rows):
        xx = x
        for c, v in enumerate(row):
            head = r < header_rows or c < header_cols
            f = fill.get((r, c), LIGHT if head else '#ffffff')
            s.rect(xx, y + r * ch, colw[c], ch, f, '#9ca3af', 1)
            s.text(xx + colw[c] / 2, y + r * ch + ch / 2 + size * 0.36, v, size, INK, weight='bold' if head else 'normal')
            xx += colw[c]


def dot_header(extra=''):
    return [f'digraph {{ bgcolor="white"; pad=0.2; nodesep=0.25; ranksep=0.4; {extra}',
            f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", '
            f'fillcolor="{BLUE_BG}", penwidth=1.2, height=0.3];',
            f'edge [fontname="{FONT}", fontsize=11, color="{INK}", arrowsize=0.6];']


# =====================================================================
# 01-complexity-analysis/01 growth and asymptotic notation
# =====================================================================

def growth_curves():
    fs = [('O(1)', lambda n: 1, GREY), ('O(log n)', lambda n: math.log2(n), ACCENT),
          ('O(n)', lambda n: n, PIX), ('O(n log n)', lambda n: n * math.log2(n), '#7c3aed'),
          ('O(n²)', lambda n: n * n, ORANGE), ('O(2ⁿ)', lambda n: 2 ** n, TRUE)]
    ymax, nmax = 100, 20
    s = Svg(520, 360, 'Growth curves on one chart for n from 1 to 20: O(1) stays flat, O(log n) barely rises, O(n) '
                      'is a straight line, O(n log n) bends up, O(n squared) passes 100 at n = 10 and O(2 to the n) '
                      'passes 100 at n = 7')
    p = Plot(s, 70, 20, 340, 270, (0, nmax), (0, ymax))
    p.axes('input size n', 'steps', xticks=(0, 5, 10, 15, 20), yticks=(0, 25, 50, 75, 100))
    for name, f, col in fs:
        pts = []
        n = 1.0
        while n <= nmax:
            y = f(n)
            if y > ymax:
                # clip exactly where the curve leaves the chart
                lo, hi = n - 0.25, n
                for _ in range(40):
                    mid = (lo + hi) / 2
                    lo, hi = (mid, hi) if f(mid) <= ymax else (lo, mid)
                pts.append((lo, ymax))
                break
            pts.append((n, y))
            n += 0.25
        p.curve(pts, col, 2.6)
        ex, ey = pts[-1]
        if ey >= ymax:
            s.text(p.X(ex), p.Y(ymax) - 6, name, 12, col, 'middle', 'bold')
        else:
            s.text(p.X(ex) + 6, p.Y(ey) + (12 if name == 'O(1)' else 0), name, 12, col, 'start', 'bold')
    # the lesson's point: quadratic and exponential leave the chart early
    assert 2 ** 6 <= 100 < 2 ** 7 and 9 * 9 <= 100 < 11 * 11
    s.text(260, 352, 'The faster a curve bends up, the sooner it leaves the chart. Steps are counts, not seconds.', 11)
    save(s, 'growth-curves.svg')


def bounds_sandwich():
    T = lambda n: 0.5 * n * n + 4 * n + 8      # the measured work
    lo = lambda n: 0.5 * n * n                  # c1 * f(n), f(n) = n^2
    hi = lambda n: 1.0 * n * n                  # c2 * f(n)
    n0 = next(n for n in range(1, 50) if all(lo(m) <= T(m) <= hi(m) for m in range(n, 200)))
    assert n0 == 10
    s = Svg(520, 340, 'Big-O, Big-Omega and Big-Theta as a sandwich: the work T(n) stays below n squared (the upper '
                      'bound, O) and above half of n squared (the lower bound, Omega) from n = 10 on, so T(n) is '
                      'Theta of n squared')
    p = Plot(s, 70, 20, 330, 250, (0, 20), (0, 400))
    p.axes('input size n', 'work', xticks=(0, 5, 10, 15, 20), yticks=(0, 100, 200, 300, 400))
    xs = [i / 4 for i in range(0, 81)]
    band = [(x, hi(x)) for x in xs if x >= n0] + [(x, lo(x)) for x in reversed(xs) if x >= n0]
    s.add('<path d="M ' + ' L '.join(f'{p.X(x):.1f} {p.Y(y):.1f}' for x, y in band) + ' Z" fill="#ecfdf5"/>')
    p.curve([(x, hi(x)) for x in xs], TRUE, 2.4)
    p.curve([(x, lo(x)) for x in xs], PIX, 2.4)
    p.curve([(x, T(x)) for x in xs if T(x) <= 400], INK, 2.8)
    s.line(p.X(n0), p.Y(0), p.X(n0), p.Y(400), GREY, 1.2, '5 4')
    s.text(p.X(n0) + 4, p.Y(380), 'n₀ = 10', 11, '#4b5563', 'start')
    s.text(p.X(20) + 6, p.Y(hi(20)) + 4, 'n²', 12, TRUE, 'start', 'bold')
    s.text(p.X(20) + 6, p.Y(hi(20)) + 18, 'upper: O', 11, TRUE, 'start')
    s.text(p.X(20) + 6, p.Y(T(19.5)) + 4, 'T(n)', 12, INK, 'start', 'bold')
    s.text(p.X(20) + 6, p.Y(lo(20)) + 4, '½n²', 12, PIX, 'start', 'bold')
    s.text(p.X(20) + 6, p.Y(lo(20)) + 18, 'lower: Ω', 11, PIX, 'start')
    s.text(260, 330, 'Past n₀, T(n) stays inside the green band: below O, above Ω. Both hold, so T(n) is Θ(n²).', 11)
    save(s, 'bounds-sandwich.svg')


def lesson_growth():
    growth_curves()
    bounds_sandwich()


# =====================================================================
# 01-complexity-analysis/02 amortised analysis
# =====================================================================

def append_costs(n):
    """Actual cost of each append to a doubling array that starts at capacity 1 (1 write + copies on a resize)."""
    size, cap, out = 0, 1, []
    for _ in range(n):
        c = 1
        if size == cap:
            c += size
            cap *= 2
        size += 1
        out.append(c)
    return out


def amortised_bars():
    n = 33
    cost = append_costs(n)
    assert cost[:5] == [1, 2, 3, 1, 5]                   # the lesson's potential table
    full = append_costs(1000)
    assert sum(full) == 2023 and sum(append_costs(100000)) == 231071
    s = Svg(540, 330, 'Bar chart of the actual cost of appends 1 to 33 on a doubling array: most cost 1, but appends '
                      '2, 3, 5, 9, 17 and 33 cost 2, 3, 5, 9, 17 and 33 because they copy everything; the running '
                      'average stays under the flat amortised line at 3')
    p = Plot(s, 60, 20, 440, 240, (0.3, n + 0.7), (0, 34))
    p.axes('append number', 'writes for this append', xticks=(1, 5, 9, 17, 25, 33), yticks=(0, 5, 10, 20, 30))
    bw = p.w / n * 0.7
    for i, c in enumerate(cost, 1):
        col = ORANGE if c > 1 else PIX2
        s.rect(p.X(i) - bw / 2, p.Y(c), bw, p.Y(0) - p.Y(c), col, INK if c > 1 else 'none', 0.6)
        if c > 1:
            s.text(p.X(i), p.Y(c) - 4, c, 10, '#92400e', weight='bold')
    avg = [(i, sum(cost[:i]) / i) for i in range(1, n + 1)]
    assert all(a < 3 for _, a in avg)
    p.curve(avg, ACCENT, 2.2)
    s.line(p.X(0.3), p.Y(3), p.X(n + 0.7), p.Y(3), TRUE, 1.6, '6 4')
    s.line(p.X(2), p.Y(31), p.X(4), p.Y(31), TRUE, 1.6, '6 4')
    s.text(p.X(4.5), p.Y(31) + 4, 'amortised cost: 3 per append', 11, TRUE, 'start', 'bold')
    s.line(p.X(2), p.Y(28), p.X(4), p.Y(28), ACCENT, 2.2)
    s.text(p.X(4.5), p.Y(28) + 4, 'running average of the real costs (always under 3)', 11, ACCENT, 'start', 'bold')
    s.text(270, 318, 'Orange bars are resizes. Each one is twice as far from the last, so the average stays flat.', 11)
    save(s, 'amortised-append-costs.svg')


def bank_balance():
    n = 64
    cost = append_costs(1000)

    def bank(fee, m):
        b, out = 0, [(0, 0)]
        for i in range(m):
            b += fee - cost[i]
            out.append((i + 1, b))
        return out

    full2, full3 = bank(2, 1000), bank(3, 1000)
    assert full3[-1][1] == 977 and min(b for _, b in full3) == 0
    assert full2[-1][1] == -23 and min(b for _, b in full2) == -510
    b2, b3 = bank(2, n), bank(3, n)
    s = Svg(540, 320, 'The credit balance over 64 appends: charging 3 per append the bank drops at each resize but '
                      'never goes below zero; charging 2 it goes below zero at the early resizes and dips deeper at '
                      'each one, down to minus 30 at append 33')
    lo = min(b for _, b in b2)
    hi = max(b for _, b in b3)
    p = Plot(s, 65, 20, 440, 240, (0, n), (lo - 2, hi + 4))
    p.axes('append number', 'credit in the bank', xticks=(0, 8, 16, 32, 48, 64), yticks=(-30, -15, 0, 15, 30, 45, 60))
    s.rect(p.X(0), p.Y(0), p.w, p.Y(lo - 2) - p.Y(0), RED_BG, opacity=0.6)
    s.line(p.X(0), p.Y(0), p.X(n), p.Y(0), INK, 1.2)
    p.curve(b3, ACCENT, 2.4)
    p.curve(b2, TRUE, 2.4)
    s.text(p.X(40), p.Y(b3[40][1]) - 12, 'charge 3: never below 0', 12, ACCENT, 'middle', 'bold')
    s.text(p.X(46), p.Y(b2[46][1]) + 22, 'charge 2: in debt', 12, TRUE, 'middle', 'bold')
    s.text(p.X(2), p.Y(lo) + 4, 'negative = invalid proof', 10, TRUE, 'start')
    s.text(270, 310, 'Each resize spends the bank. With a fee of 3 the savings exactly cover every copy.', 11)
    save(s, 'amortised-bank-balance.svg')


def lesson_amortised():
    amortised_bars()
    bank_balance()


# =====================================================================
# 02-recursion/01 recursion fundamentals
# =====================================================================

def photos_tree():
    tree = ('photos/', [('cat.jpg', None), ('dog.jpg', None),
                        ('2023/', [('jan.jpg', None), ('feb.jpg', None)]),
                        ('2024/', [('trips/', [('rome.jpg', None)])])])

    def files(t):
        name, kids = t
        return 1 if kids is None else sum(files(k) for k in kids)

    assert files(tree) == 5
    lines = dot_header('ranksep=0.35;')
    ids = iter(range(100))

    def walk(t):
        i = next(ids)
        name, kids = t
        if kids is None:
            lines.append(f'n{i} [label="{name}", shape=note, fillcolor="#ffffff"];')
        else:
            lines.append(f'n{i} [label="{name}\\nfiles = {files(t)}", fillcolor="{YELLOW_BG}"];')
            for k in kids:
                lines.append(f'n{i} -> n{walk(k)};')
        return i

    walk(tree)
    lines.append('}')
    dot('\n'.join(lines), 'photos-folder-tree.svg',
        'The photos folder as a tree: photos holds cat.jpg, dog.jpg and the folders 2023 (2 files) and 2024; '
        '2024 holds trips (1 file); every folder is labelled with its own file count, and photos totals 5')


def call_stack_picture():
    vals = [3, 1, 4]
    frames = []
    for k in range(len(vals) + 1):
        rest = vals[k:]
        frames.append((rest, sum(rest)))
    assert [f[1] for f in frames] == [8, 5, 4, 0]
    s = Svg(560, 290, 'The call stack for list_sum of [3, 1, 4]: four frames pile up while winding down, each waiting '
                      'on the next; the base case returns 0, then answers travel back up: 4, then 5, then 8')
    mk = arrow_defs(s)
    s.text(140, 22, 'winding: calls pile up', 13, PIX, weight='bold')
    s.text(430, 22, 'unwinding: answers go back', 13, ACCENT, weight='bold')
    for k, (rest, total) in enumerate(frames):
        y = 40 + k * 58
        x = 30 + k * 22
        lab = f'list_sum({rest})'.replace(' ', '')
        pend = f'{rest[0]} + ?' if rest else '0  (base case)'
        fill = GREEN_BG if not rest else BLUE_BG
        s.rect(x, y, 230, 40, fill, INK, 1.2)
        s.text(x + 10, y + 17, lab, 13, INK, 'start', 'bold')
        s.text(x + 10, y + 33, f'frame {k + 1}:  {pend}', 11, '#374151', 'start')
        if k < len(frames) - 1:
            arrow(s, mk, x + 40, y + 40, x + 62, y + 58, PIX)
        ret = f'returns {total}' if not rest else f'returns {rest[0]} + {total - rest[0]} = {total}'
        s.text(330, y + 25, ret, 13, ACCENT, 'start', 'bold')
        s.line(x + 232, y + 20, 322, y + 20, GREY, 1, '3 3')
        if k > 0:
            arrow(s, mk, 470, y + 8, 470, y - 22, ACCENT)
    s.text(280, 282, 'No addition happens until the base case answers. Then each frame finishes and is released.', 11)
    save(s, 'call-stack-list-sum.svg')


def call_tree(root, kids, label, name, title, memo=False, hl_repeats=True):
    """Graphviz call tree. kids(n) -> list of child args (empty for a base case).
    Repeated calls get an orange outline; with memo=True a repeat is a cached leaf (dashed)."""
    lines = dot_header('nodesep=0.15; ranksep=0.35;')
    ids = iter(range(10000))
    seen, count = set(), {}

    def walk(n):
        i = next(ids)
        count[n] = count.get(n, 0) + 1
        repeat = n in seen
        seen.add(n)
        ks = kids(n)
        if memo and repeat and ks:
            lines.append(f'n{i} [label="{label(n)}\\ncached", style="rounded,dashed", fillcolor="#ffffff", '
                         f'color="{ACCENT}", fontcolor="{ACCENT}"];')
            return i
        fill = GREEN_BG if not ks else BLUE_BG
        extra = f', color="{ORANGE}", penwidth=2.6' if (hl_repeats and repeat and ks) else ''
        lines.append(f'n{i} [label="{label(n)}", fillcolor="{fill}"{extra}];')
        for k in ks:
            lines.append(f'n{i} -> n{walk(k)};')
        return i

    walk(root)
    lines.append('}')
    dot('\n'.join(lines), name, title)
    return count


def fib_trees():
    fk = lambda n: [] if n < 2 else [n - 1, n - 2]
    c = call_tree(5, fk, lambda n: f'fib({n})', 'fib5-call-tree.svg',
                  'The call tree of naive fib(5): 15 calls; fib(3) is computed twice, fib(2) three times and fib(1) '
                  'five times; repeated work is outlined in orange')
    assert sum(c.values()) == 15 and c[3] == 2 and c[2] == 3 and c[1] == 5
    c = call_tree(5, fk, lambda n: f'fib({n})', 'fib5-memo-tree.svg',
                  'The call tree of memoised fib(5): 9 calls; the second fib(3) and the second fib(2) are answered '
                  'from the cache, so the tree becomes a chain', memo=True)
    assert sum(c.values()) == 2 * 5 - 1


def ways_sketch_tree():
    wk = lambda n: [] if n < 3 else [n - 1, n - 3]
    c = call_tree(6, wk, lambda n: f'ways({n})', 'ways6-call-tree.svg',
                  'The call tree of ways(6) where ways(n) = ways(n-1) + ways(n-3) and n below 3 is a base case: '
                  '11 calls; ways(3) is computed twice (the repeat outlined in orange) and ways(2) three times')
    assert sum(c.values()) == 11 and c[3] == 2 and c[2] == 3 and c[0] == 2 and c[1] == 1


def lesson_recursion_fundamentals():
    photos_tree()
    call_stack_picture()
    fib_trees()
    ways_sketch_tree()


# =====================================================================
# 02-recursion/02 recursion trees and recurrences
# =====================================================================

def level_work(a, b, f, n):
    """Simulate T(n) = a*T(n/b) + f(n) as the lesson's lab does; return the work at each level."""
    by = {}

    def rec(size, level):
        by[level] = by.get(level, 0) + f(size)
        if size <= 1:
            return
        for _ in range(a):
            rec(size / b, level + 1)

    rec(n, 0)
    return [by[k] for k in sorted(by)]


def fmt_num(x):
    return f'{x:g}' if x < 10000 else f'{x:,.0f}'


def recursion_tree_svg(a, b, f, n, name, title, node_text=None, sum_text=None, leaf_w=30, caption=''):
    """Draw every call of T(n) = a*T(n/b) + f(n) as a node holding its own work, with each level's total on the right."""
    node_text = node_text or (lambda size: fmt_num(f(size)))
    levels = []

    def build(size, depth):
        node = {'size': size, 'kids': []}
        while len(levels) <= depth:
            levels.append([])
        levels[depth].append(node)
        if size > 1:
            node['kids'] = [build(size / b, depth + 1) for _ in range(a)]
        return node

    root = build(n, 0)
    leaves = levels[-1]
    gap_y = 56
    tree_w = len(leaves) * leaf_w
    W = 40 + tree_w + 190
    H = 50 + len(levels) * gap_y + (24 if caption else 0)
    s = Svg(W, H, title)
    for i, leaf in enumerate(leaves):
        leaf['x'] = 30 + i * leaf_w + leaf_w / 2

    def place(nd):
        if nd['kids']:
            for k in nd['kids']:
                place(k)
            nd['x'] = sum(k['x'] for k in nd['kids']) / len(nd['kids'])

    place(root)
    for d, row in enumerate(levels):
        y = 36 + d * gap_y
        for nd in row:
            for k in nd['kids']:
                s.line(nd['x'], y + 11, k['x'], y + gap_y - 11, GREY, 1.1)
    for d, row in enumerate(levels):
        y = 36 + d * gap_y
        bw = min(46, leaf_w - 4) if d == len(levels) - 1 else 46
        for nd in row:
            r(s, nd['x'] - bw / 2, y - 11, bw, 22, BLUE_BG if nd['kids'] else GREEN_BG, INK)
            t(s, nd['x'], y + 4, node_text(nd['size']), 11)
        total = sum(f(nd['size']) for nd in row)
        txt = sum_text(d, len(row), row[0]['size'], total) if sum_text else f'{len(row)} × {fmt_num(f(row[0]["size"]))} = {fmt_num(total)}'
        s.text(W - 180, y + 4, f'level {d}:', 11, '#6b7280', 'start')
        s.text(W - 128, y + 4, txt, 12, ACCENT, 'start', 'bold')
    if caption:
        s.text(W / 2, H - 12, caption, 11)
    save(s, name)
    return [sum(f(nd['size']) for nd in row) for row in levels]


def level_panels(cases, name, title, caption):
    """One small horizontal bar chart per recurrence: work at each level, top level at the top."""
    pw, ph = 190, 210
    s = Svg(20 + pw * len(cases), ph + 70, title)
    for c, (label, verdict, works, col) in enumerate(cases):
        x0 = 20 + c * pw
        s.text(x0 + pw / 2 - 10, 22, label, 13, INK, weight='bold')
        s.text(x0 + pw / 2 - 10, 40, verdict, 12, col, weight='bold')
        mx = max(works)
        bh = min(24, (ph - 30) / len(works) - 4)
        for k, w in enumerate(works):
            y = 56 + k * (bh + 4)
            L = max(2, (pw - 80) * w / mx)
            s.text(x0 + 16, y + bh / 2 + 4, f'{k}', 10, '#6b7280', 'end')
            s.rect(x0 + 22, y, L, bh, col, opacity=0.85)
            s.text(x0 + 26 + L, y + bh / 2 + 4, fmt_num(w), 10, INK, 'start')
        s.text(x0 + pw / 2 - 10, 56 + len(works) * (bh + 4) + 14, f'total {fmt_num(sum(works))}', 11, INK, weight='bold')
    s.text(10 + pw * len(cases) / 2, ph + 60, caption, 11)
    save(s, name)


def lesson_recursion_trees():
    lv = recursion_tree_svg(2, 2, lambda x: x, 16, 'recursion-tree-2t-n2-plus-n.svg',
                            'The recursion tree of T(n) = 2T(n/2) + n for n = 16: each node holds its own work, '
                            '16, then two 8s, four 4s, eight 2s and sixteen 1s; every level adds up to 16, and there '
                            'are 5 levels, so the total is 16 × 5 = 80', leaf_w=30,
                            caption='Sum across each level, not down each branch: every level does n = 16 work.')
    assert lv == [16] * 5 and lv == level_work(2, 2, lambda x: x, 16)
    n = 64
    leaves = level_work(2, 2, lambda x: 1, n)
    equal = level_work(2, 2, lambda x: x, n)
    root = level_work(2, 2, lambda x: x * x, n)
    assert sum(equal) == 448 and sum(leaves) == 127 and sum(root) == 8128
    assert root == [4096, 2048, 1024, 512, 256, 128, 64] and leaves == [1, 2, 4, 8, 16, 32, 64]
    level_panels([('2T(n/2) + 1', 'leaves win: O(n)', leaves, PIX),
                  ('2T(n/2) + n', 'all equal: O(n log n)', equal, ACCENT),
                  ('2T(n/2) + n²', 'root wins: O(n²)', root, ORANGE)],
                 'recursion-three-cases.svg',
                 'Work per level for three recurrences at n = 64, top level first: 2T(n/2) + 1 doubles each level '
                 '(1 to 64, total 127, the leaves win); 2T(n/2) + n is 64 on every level (total 448); '
                 '2T(n/2) + n squared halves each level (4096 down to 64, total 8128, the root wins)',
                 'Each bar is one level, root at the top. Where the big bars sit tells you the answer.')
    karat = level_work(3, 2, lambda x: x, n)
    assert karat == [64, 96, 144, 216, 324, 486, 729] and round(sum(karat)) == 2059
    # sketch answer: T(n) = 3T(n/3) + n with n = 9
    lv = recursion_tree_svg(3, 3, lambda x: x, 9, 'recursion-tree-3t-n3-sketch.svg',
                            'The recursion tree of T(n) = 3T(n/3) + n for n = 9: the root does 9, its three '
                            'children do 3 each, and the nine leaves do 1 each; every level adds up to 9, there are '
                            '3 levels, total 27', leaf_w=34)
    assert lv == [9, 9, 9]


# =====================================================================
# 02-recursion/03 the master theorem
# =====================================================================

def master_cases():
    c1 = level_work(4, 2, lambda x: x, 64)
    c2 = level_work(1, 2, lambda x: 1, 64)
    c3 = level_work(1, 3, lambda x: x, 81)
    assert round(sum(level_work(4, 2, lambda x: x, 128))) == 32640      # the lab's measured work
    assert round(sum(level_work(1, 3, lambda x: x, 128))) == 192
    assert c1 == [64, 128, 256, 512, 1024, 2048, 4096] and c2 == [1] * 7 and c3 == [81, 27, 9, 3, 1]
    level_panels([('4T(n/2) + n', 'Case 1: leaves win', c1, PIX),
                  ('T(n/2) + 1', 'Case 2: all equal', c2, ACCENT),
                  ('T(n/3) + n', 'Case 3: root wins', c3, ORANGE)],
                 'master-three-cases.svg',
                 'Work per level for one recurrence from each Master Theorem case, root first: 4T(n/2) + n at n = 64 '
                 'doubles every level from 64 to 4096 (Case 1, the leaves win, n squared); T(n/2) + 1 is 1 on every '
                 'level (Case 2, log n); T(n/3) + n at n = 81 shrinks 81, 27, 9, 3, 1 (Case 3, the root wins, n)',
                 'Case 1: n^(log_b a) beats f(n). Case 2: they tie. Case 3: f(n) beats n^(log_b a).')


def master_flowchart():
    L = dot_header('ranksep=0.32; nodesep=0.3;')
    L += [f'q1 [label="Does the input shrink by a FACTOR?\\nT(n) = a·T(n/b) + f(n)", fillcolor="{YELLOW_BG}"];',
          f'tree [label="No (e.g. T(n-1)):\\ntheorem does not apply,\\ndraw the recursion tree", fillcolor="{RED_BG}"];',
          'crit [label="Work out the leaf work n^(log_b a)"];',
          f'q2 [label="Compare f(n) with n^(log_b a)", fillcolor="{YELLOW_BG}"];',
          f'c1 [label="Case 1\\nf smaller by a power of n\\nΘ(n^(log_b a))", fillcolor="{GREEN_BG}"];',
          f'c2 [label="Case 2\\nequal (times log^k n)\\nΘ(n^(log_b a) · log^(k+1) n)", fillcolor="{GREEN_BG}"];',
          f'c3 [label="Case 3\\nf bigger by a power of n\\ncheck regularity, Θ(f(n))", fillcolor="{GREEN_BG}"];',
          f'gap [label="Only a log factor apart\\nand not Case 2: the gap,\\ndraw the tree", fillcolor="{RED_BG}"];',
          'q1 -> tree [label=" no "]; q1 -> crit [label=" yes "]; crit -> q2;',
          'q2 -> c1; q2 -> c2; c1 -> c3 [style=invis]; c2 -> gap [style=invis];',
          'q2 -> c3 [constraint=false]; q2 -> gap [constraint=false];', '{rank=same; tree; crit}', '}']
    dot('\n'.join(L), 'master-decision.svg',
        'The Master Theorem decision procedure: first check the input shrinks by a factor (if not, draw the tree); '
        'work out n to the log_b a; compare f(n) with it to pick Case 1, Case 2 or Case 3, or the gap where you '
        'draw the tree')


def lesson_master():
    master_cases()
    master_flowchart()


# =====================================================================
# 03-searching/01 linear and binary search
# =====================================================================

def binary_search_steps(xs, target):
    """The lesson's binary_search, recording (lo, hi, mid, what happened) at each step."""
    lo, hi, steps = 0, len(xs) - 1, []
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if xs[mid] == target:
            steps.append((lo, hi, mid, f'{xs[mid]} = {target}: found at index {mid}'))
            return steps, mid
        if xs[mid] < target:
            steps.append((lo, hi, mid, f'{xs[mid]} < {target}: low = {mid + 1}'))
            lo = mid + 1
        else:
            steps.append((lo, hi, mid, f'{xs[mid]} > {target}: high = {mid - 1}'))
            hi = mid - 1
    steps.append((lo, hi, None, f'low = {lo} > high = {hi}: not found, return -1'))
    return steps, -1


def draw_search_steps(xs, steps, name, title, head):
    cw, ch, row = 40, 30, 78
    W = max(60 + cw * len(xs) + 20, 470)
    s = Svg(W, 40 + row * len(steps), title)
    s.text(W / 2, 20, head, 13, INK, weight='bold')
    for k, (lo, hi, mid, msg) in enumerate(steps):
        y = 44 + k * row
        s.text(14, y + 20, f'{k + 1}', 14, '#6b7280', 'start', 'bold')
        live = set(range(lo, hi + 1))
        fill = {i: BLUE_BG for i in live}
        if mid is not None:
            fill[mid] = GREEN_BG if 'found' in msg and 'not' not in msg else YELLOW_BG
        cells(s, 40, y, xs, cw, ch, fill=fill, outline={mid: ORANGE} if mid is not None else {},
              dim=[i for i in range(len(xs)) if i not in live], index=(k == 0))
        marks = {}
        for lab, i in (('low', lo), ('mid', mid), ('high', hi)):
            if i is not None and 0 <= i < len(xs):
                marks.setdefault(i, []).append(lab)
        for i, labs in marks.items():
            col = ORANGE if 'mid' in labs else PIX
            s.text(40 + i * cw + cw / 2, y + ch + 13, '/'.join(labs), 10, col, weight='bold')
        s.text(40 + cw * len(xs) + 10 if W > 60 + cw * len(xs) + 200 else 40, y + ch + 28, msg, 11, INK, 'start')
    save(s, name)


def lesson_binary_search():
    xs = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    steps, found = binary_search_steps(xs, 23)
    assert found == 5 and [m for _, _, m, _ in steps] == [4, 7, 5]
    draw_search_steps(xs, steps, 'binary-search-steps.svg',
                      'Binary search for 23 in [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]: step 1 checks index 4 (16, '
                      'too small, low = 5); step 2 checks index 7 (56, too big, high = 6); step 3 checks index 5 and '
                      'finds 23; greyed cells are already ruled out', 'Searching for 23: the blue cells are still in play')
    # the lesson's worked problem 1, asserted so the text and the method agree
    w = [3, 8, 15, 21, 27, 34, 40, 52, 61, 75, 88]
    assert [m for _, _, m, _ in binary_search_steps(w, 61)[0]] == [5, 8]
    assert [m for _, _, m, _ in binary_search_steps(w, 10)[0]][:4] == [5, 2, 0, 1]
    # sketch answer: a search that fails
    xs = [4, 9, 13, 20, 26, 31, 37, 45, 50]
    steps, found = binary_search_steps(xs, 40)
    assert found == -1 and [m for _, _, m, _ in steps] == [4, 6, 7, None]
    draw_search_steps(xs, steps, 'binary-search-sketch.svg',
                      'Binary search for 40 in [4, 9, 13, 20, 26, 31, 37, 45, 50]: mid 4 holds 26 (low = 5), mid 6 '
                      'holds 37 (low = 7), mid 7 holds 45 (high = 6), then low 7 is past high 6, so 40 is not there',
                      'Searching for 40: the blue cells are still in play')


# =====================================================================
# 03-searching/02 binary search on the answer
# =====================================================================

def koko_search():
    piles, h = [3, 6, 7, 11], 8
    hours = lambda sp: sum(-(-p // sp) for p in piles)
    works = lambda sp: hours(sp) <= h
    speeds = list(range(1, max(piles) + 1))
    assert [hours(x) for x in speeds[:6]] == [27, 15, 10, 8, 8, 6]
    lo, hi, steps = 1, max(piles), []
    while lo < hi:                                   # the lesson's smallest_true template
        mid = lo + (hi - lo) // 2
        ok = works(mid)
        steps.append((lo, hi, mid, ok))
        hi, lo = (mid, lo) if ok else (hi, mid + 1)
    assert lo == 4 and len(steps) == 4     # the lab prints checks + 1 = 5
    cw, ch = 38, 28
    W = 70 + cw * len(speeds) + 20
    s = Svg(W, 120 + 56 * len(steps) + 40, 'Binary search on Koko\'s eating speed for piles [3, 6, 7, 11] in 8 hours: '
            'the yes/no answers for speeds 1 to 11 read F F F T T T T T T T T; the search checks speeds 6, 3, 5 '
            'and 4 and closes in on 4, the first speed that works')
    x0 = 70
    s.text(x0 - 8, 52, 'speed', 11, '#6b7280', 'end')
    s.text(x0 - 8, 76, 'hours', 11, '#6b7280', 'end')
    s.text(x0 - 8, 98, 'works?', 11, '#6b7280', 'end')
    for i, sp in enumerate(speeds):
        ok = works(sp)
        r(s, x0 + i * cw, 34, cw, ch, LIGHT, INK)
        t(s, x0 + i * cw + cw / 2, 53, sp, 13, None, 'bold')
        t(s, x0 + i * cw + cw / 2, 77, hours(sp))
        r(s, x0 + i * cw + 3, 84, cw - 6, 20, GREEN_BG if ok else RED_BG, ACCENT if ok else TRUE)
        t(s, x0 + i * cw + cw / 2, 98, 'T' if ok else 'F', None, ACCENT if ok else TRUE, 'bold')
    s.text(W / 2, 20, 'One flip from F to T: binary search finds where it happens', 13, INK, weight='bold')
    for k, (lo_, hi_, mid, ok) in enumerate(steps):
        y = 130 + k * 56
        s.text(16, y + 18, f'{k + 1}', 14, '#6b7280', 'start', 'bold')
        s.rect(x0, y, cw * len(speeds), 26, LIGHT, GREY, 1)
        for i, sp in enumerate(speeds):
            if lo_ <= sp <= hi_:
                r(s, x0 + i * cw, y, cw, 26, BLUE_BG, INK)
                t(s, x0 + i * cw + cw / 2, y + 18, sp)
        s.rect(x0 + (mid - 1) * cw + 1.5, y + 1.5, cw - 3, 23, 'none', ORANGE, 3)
        verdict = f'speed {mid}: {hours(mid)} h, works, so hi = {mid}' if ok else \
            f'speed {mid}: {hours(mid)} h, too slow, so lo = {mid + 1}'
        s.text(x0, y + 42, f'lo = {lo_}, hi = {hi_}, check mid = {mid}.  ' + verdict, 11, INK, 'start')
    y = 130 + len(steps) * 56
    s.text(x0, y + 10, f'lo = hi = {lo}: the smallest speed that works is {lo}', 12, ACCENT, 'start', 'bold')
    save(s, 'koko-answer-search.svg')
    return steps


def lesson_answer_search():
    steps = koko_search()
    assert [m for _, _, m, _ in steps] == [6, 3, 5, 4]


# =====================================================================
# 03-searching/03 state-space search
# =====================================================================

GOAL8 = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def successors8(state):
    """The lesson's successor function: slide a tile into the blank (up, down, left, right)."""
    i = state.index(0)
    r, c = divmod(i, 3)
    out = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            j = nr * 3 + nc
            lst = list(state)
            lst[i], lst[j] = lst[j], lst[i]
            out.append(tuple(lst))
    return out


def board(s, x, y, st, cell=15, stroke=INK, width=1.2, dash=None):
    r(s, x, y, cell * 3, cell * 3, '#ffffff', stroke, width)
    b = st.index(0)
    r(s, x + (b % 3) * cell, y + (b // 3) * cell, cell, cell, '#d1d5db')
    s.path(f'M{x + cell} {y} v{cell * 3} M{x + 2 * cell} {y} v{cell * 3} M{x} {y + cell} h{cell * 3} '
           f'M{x} {y + 2 * cell} h{cell * 3}', GREY, 0.8)
    if dash or stroke != INK:
        s.add(f'<rect x="{x - 2}" y="{y - 2}" width="{cell * 3 + 4}" height="{cell * 3 + 4}" fill="none" '
              f'stroke="{stroke}" stroke-width="{width}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')
    for rr in range(3):
        row = st[rr * 3:rr * 3 + 3]
        for c, v in enumerate(row):
            if v:
                t(s, x + c * cell + cell / 2, y + rr * cell + cell * 0.72, v, 11)


def puzzle_tree():
    start = (1, 2, 3, 0, 4, 6, 7, 5, 8)
    # graph-search BFS, level by level, remembering each state's parent
    parent, levels = {start: None}, [[start]]
    while GOAL8 not in parent:
        nxt = []
        for st in levels[-1]:
            for t in successors8(st):
                if t not in parent:
                    parent[t] = st
                    nxt.append(t)
        levels.append(nxt)
    assert len(levels) - 1 == 3                       # the lesson: medium board is 3 moves away
    path, st = [], GOAL8
    while st:
        path.append(st)
        st = parent[st]
    path = path[::-1]
    shown = levels[:3] + [[GOAL8]]
    cell, bw, gap = 17, 51, 18
    widest = max(len(r) for r in shown)
    W = max(40 + widest * (bw + gap), 520)
    s = Svg(W, 60 + 4 * 100 + 10, 'Part of the 8-puzzle state space for the medium board 1 2 3 / blank 4 6 / 7 5 8: one '
            'board at depth 0, its 3 neighbours at depth 1, their new neighbours at depth 2, and the goal at depth 3; '
            'the three-move solution path is outlined in orange')
    s.text(W / 2, 20, 'Each row is generated from the row above. No list of boards exists beforehand.', 12, INK,
           weight='bold')
    pos = {}
    for d, row in enumerate(shown):
        y = 40 + d * 100
        total = len(row) * (bw + gap) - gap
        x0 = (W - total) / 2
        for k, st in enumerate(row):
            pos[st] = (x0 + k * (bw + gap), y)
    for st, (x, y) in pos.items():
        par = parent[st]
        if par in pos:
            px, py = pos[par]
            on = st in path and par in path
            s.line(px + bw / 2, py + bw, x + bw / 2, y, ORANGE if on else GREY, 2.4 if on else 1)
    for d, row in enumerate(shown):
        for st in row:
            x, y = pos[st]
            board(s, x, y, st, cell, ORANGE if st in path else INK, 2.6 if st in path else 1.2)
        s.text(10, pos[row[0]][1] + 26, f'depth {d}', 10, '#6b7280', 'start')
    s.text(pos[GOAL8][0] + bw + 10, pos[GOAL8][1] + 26, f'goal (one of {len(levels[3])} boards at depth 3)', 11,
           ACCENT, 'start', 'bold')
    save(s, 'eight-puzzle-states.svg')


def frontier_orders():
    kids = {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': ['F', 'G']}

    def run(kind):
        frontier, explored, order = ['A'], set(), []
        while frontier:
            cur = frontier.pop() if kind == 'stack' else frontier.pop(0)
            if cur in explored:
                continue
            explored.add(cur)
            order.append(cur)
            frontier.extend(k for k in kids.get(cur, []) if k not in explored)
        return order

    bfs, dfs = run('queue'), run('stack')
    assert bfs == list('ABCDEFG') and dfs == list('ACGFBED')
    L = dot_header('nodesep=0.2; ranksep=0.35;')
    for tag, order, col, lab in (('q', bfs, PIX, 'queue (first in, first out): BFS'),
                                 ('s', dfs, ORANGE, 'stack (last in, first out): DFS')):
        L.append(f'subgraph cluster_{tag} {{ label="{lab}"; fontname="{FONT}"; fontsize=12; color="#d1d5db"; '
                 f'style=rounded;')
        for n in 'ABCDEFG':
            L.append(f'{tag}{n} [label="{n}\\n#{order.index(n) + 1}", shape=circle, width=0.5, fixedsize=true, '
                     f'fillcolor="{BLUE_BG if tag == "q" else YELLOW_BG}", color="{col}"];')
        for a, ks in kids.items():
            for k in ks:
                L.append(f'{tag}{a} -> {tag}{k};')
        L.append('}')
    L.append('}')
    dot('\n'.join(L), 'frontier-orders.svg',
        'The same tree searched with two frontiers. With a queue the order is A, B, C, D, E, F, G (level by level). '
        'With a stack it is A, C, G, F, B, E, D (deep first). The number under each letter is when it was expanded')


def lesson_state_space():
    frontier_orders()
    puzzle_tree()


# =====================================================================
# 04 divide and conquer (and 05-sorting/03 merge sort)
# =====================================================================

def merge_count(left, right):
    """The lesson's merge: take the smaller head; taking from the right adds len(left) - i inversions."""
    out, i, j, inv = [], 0, 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
            inv += len(left) - i
    out.extend(left[i:]); out.extend(right[j:])
    return out, inv


def split_merge_svg(arr, name, title, head, count_inv=False, cw=30, g=14, caption=''):
    """Merge sort drawn as an hourglass: split rows going down, merge rows coming back up."""
    rows = {}                                       # (phase, depth) -> list of (lo, hi, values, inv)

    def go(lo, hi, d):
        rows.setdefault(('split', d), []).append((lo, hi, arr[lo:hi], None))
        if hi - lo <= 1:
            return arr[lo:hi], 0
        mid = lo + (hi - lo) // 2
        lv, li = go(lo, mid, d + 1)
        rv, ri = go(mid, hi, d + 1)
        merged, ic = merge_count(lv, rv)
        rows.setdefault(('merge', d), []).append((lo, hi, merged, ic))
        return merged, li + ri + ic

    out, total = go(0, len(arr), 0)
    depth = max(d for ph, d in rows if ph == 'split')
    order = [('split', d) for d in range(depth + 1)] + [('merge', d) for d in range(depth - 1, -1, -1)]
    rh, ch = 50, 26
    x0 = 20
    W = x0 * 2 + len(arr) * (cw + g) - g + (60 if count_inv else 0)
    if W < 440:
        x0 += (440 - W) / 2
        W = 440
    H = 40 + len(order) * rh + (20 if caption else 0)
    s = Svg(W, H, title)
    s.text(W / 2, 20, head, 13, INK, weight='bold')
    centre = lambda lo, hi: x0 + ((lo + hi - 1) / 2) * (cw + g) + cw / 2
    ypos = {key: 36 + k * rh for k, key in enumerate(order)}
    # connectors
    for key, nodes in rows.items():
        ph, d = key
        for lo, hi, vals, inv in nodes:
            if hi - lo <= 1:
                continue
            mid = lo + (hi - lo) // 2
            for a, b in ((lo, mid), (mid, hi)):
                if ph == 'split':
                    y1, y2 = ypos[key] + ch, ypos[('split', d + 1)]
                else:
                    src = ('merge', d + 1) if b - a > 1 else ('split', depth if ('merge', d + 1) not in ypos else d + 1)
                    if b - a <= 1:
                        src = ('split', d + 1)
                    y1, y2 = ypos[src] + ch, ypos[key]
                s.line(centre(lo, hi), y1 if ph == 'split' else y2, centre(a, b), y2 if ph == 'split' else y1,
                       PIX if ph == 'split' else ACCENT, 1.1)
    for key, nodes in rows.items():
        ph, d = key
        y = ypos[key]
        for lo, hi, vals, inv in nodes:
            n = hi - lo
            x = centre(lo, hi) - n * cw / 2
            fill = BLUE_BG if ph == 'split' else GREEN_BG
            if ph == 'split' and n == 1:
                fill = YELLOW_BG
            r(s, x, y, n * cw, ch, fill, INK)
            if n > 1:
                s.path(' '.join(f'M{x + k * cw:.0f} {y:.0f}v{ch}' for k in range(1, n)), GREY, 0.8)
            for k, v in enumerate(vals):
                t(s, x + k * cw + cw / 2, y + 17, v)
            if count_inv and inv is not None:
                s.text(x + n * cw + 6, y + 17, f'+{inv}', 12, TRUE if inv else '#6b7280', 'start', 'bold')
    if caption:
        s.text(W / 2, H - 10, caption, 11)
    save(s, name)
    return out, total, rows


def lesson_divide_and_conquer():
    arr = [6, 3, 8, 2, 7, 1]
    brute = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
    out, total, rows = split_merge_svg(arr, 'inversions-split-merge.svg',
                                       'Counting inversions in [6, 3, 8, 2, 7, 1] by divide and conquer: split down to '
                                       'single elements, then merge back up; each merge adds the pairs it finds out of '
                                       'order across its two halves, and the counts add up to 10',
                                       'Red numbers: inversions found by that merge',
                                       count_inv=True,
                                       caption=f'Total: {brute} inversions, the same as checking every pair.')
    assert out == sorted(arr) and total == brute == 10
    # sketch answer
    arr = [4, 1, 3, 2]
    out, total, _ = split_merge_svg(arr, 'inversions-sketch.svg',
                                    'Counting inversions in [4, 1, 3, 2]: split into [4, 1] and [3, 2]; merging 4 and 1 '
                                    'finds 1, merging 3 and 2 finds 1, and merging [1, 4] with [2, 3] finds 2, for a '
                                    'total of 4', 'Split down, merge back up, add the inversions', count_inv=True)
    assert total == 4


# =====================================================================
# 05-sorting/01 the lower bound: comparison decision trees
# =====================================================================

class Probe:
    """An item that remembers its name; comparing two Probes asks the oracle and logs the question."""
    log, truth = None, None

    def __init__(self, name):
        self.name = name

    def __lt__(self, other):
        ans = Probe.truth[self.name] < Probe.truth[other.name]
        Probe.log.append((self.name, other.name, ans, '<'))
        return ans

    def __le__(self, other):
        ans = Probe.truth[self.name] <= Probe.truth[other.name]
        Probe.log.append((self.name, other.name, ans, '<'))
        return ans

    def __gt__(self, other):
        ans = Probe.truth[self.name] > Probe.truth[other.name]
        Probe.log.append((other.name, self.name, ans, '<'))
        return ans


def insertion_sort(xs):
    xs = list(xs)
    for i in range(1, len(xs)):
        j = i
        while j > 0 and xs[j - 1] > xs[j]:
            xs[j - 1], xs[j] = xs[j], xs[j - 1]
            j -= 1
    return xs


def merge_sort(xs):
    if len(xs) <= 1:
        return list(xs)
    mid = len(xs) // 2
    left, right = merge_sort(xs[:mid]), merge_sort(xs[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]


def decision_tree(sort, names, name, title):
    """Run `sort` on every ordering of `names` and merge the comparison logs into one tree."""
    from itertools import permutations
    tree = {}
    for perm in permutations(range(len(names))):
        Probe.truth = dict(zip(names, perm))
        Probe.log = []
        out = sort([Probe(n) for n in names])
        assert [Probe.truth[p.name] for p in out] == sorted(perm)
        node = tree
        for a, b, ans, _ in Probe.log:
            node.setdefault('q', (a, b))
            assert node['q'] == (a, b)
            node = node.setdefault(ans, {})
        node['leaf'] = ' < '.join(p.name for p in out)
    L = dot_header('nodesep=0.18; ranksep=0.38;')
    ids = iter(range(1000))
    leaves, height = [], [0]

    def walk(nd, d):
        i = next(ids)
        if 'leaf' in nd:
            leaves.append(nd['leaf'])
            height[0] = max(height[0], d)
            L.append(f'n{i} [label="{nd["leaf"]}", fillcolor="{GREEN_BG}"];')
            return i
        a, b = nd['q']
        L.append(f'n{i} [label="{a} < {b}?", fillcolor="{BLUE_BG}", shape=ellipse];')
        for ans in (True, False):
            if ans in nd:
                L.append(f'n{i} -> n{walk(nd[ans], d + 1)} [label=" {"yes" if ans else "no"} "];')
        return i

    walk(tree, 0)
    L.append('}')
    dot('\n'.join(L), name, title)
    return leaves, height[0]


def lesson_lower_bound():
    leaves, h = decision_tree(insertion_sort, 'abc', 'decision-tree-insertion3.svg',
                              'The decision tree of insertion sort on three items a, b, c: each oval is one comparison, '
                              'each green leaf is one of the 6 possible orderings, and the longest path from the top '
                              'to a leaf is 3 comparisons')
    assert len(leaves) == 6 and len(set(leaves)) == 6 and h == 3 == math.ceil(math.log2(6))
    leaves, h = decision_tree(merge_sort, 'xyz', 'decision-tree-merge3.svg',
                              'The decision tree of merge sort on three items x, y, z: it first compares y with z, '
                              'then merges x into the sorted pair; 6 leaves, one per ordering, and at most 3 '
                              'comparisons on any path')
    assert len(leaves) == 6 and h == 3


# =====================================================================
# 05-sorting/02 elementary sorts, pass by pass
# =====================================================================

def selection_passes(xs):
    xs, out = list(xs), []
    for i in range(len(xs) - 1):
        m = min(range(i, len(xs)), key=lambda k: xs[k])
        xs[i], xs[m] = xs[m], xs[i]
        out.append((list(xs), set(range(i + 1)), {i, m} if m != i else {i}))
    return out


def bubble_passes(xs):
    xs, out, n = list(xs), [], len(xs)
    for i in range(n):
        swapped = False
        moved = set()
        for j in range(n - 1 - i):
            if xs[j] > xs[j + 1]:
                xs[j], xs[j + 1] = xs[j + 1], xs[j]
                swapped = True
                moved |= {j, j + 1}
        out.append((list(xs), set(range(n - 1 - i, n)), moved))
        if not swapped:
            break
    return out


def insertion_passes(xs):
    xs, out = list(xs), []
    for i in range(1, len(xs)):
        j = i
        while j > 0 and xs[j - 1] > xs[j]:
            xs[j - 1], xs[j] = xs[j], xs[j - 1]
            j -= 1
        out.append((list(xs), set(range(i + 1)), {j}))
    return out


def passes_panel(s, x0, y0, start, passes, label, note, cw=28, ch=26, rh=36):
    s.text(x0 + cw * len(start) / 2, y0, label, 13, INK, weight='bold')
    s.text(x0 + cw * len(start) / 2, y0 + 16, note, 10, '#4b5563')
    cells(s, x0, y0 + 28, start, cw, ch, index=False)
    s.text(x0 - 6, y0 + 28 + 17, 'start', 9, '#6b7280', 'end')
    for k, (arr, done, moved) in enumerate(passes):
        y = y0 + 28 + (k + 1) * rh
        cells(s, x0, y, arr, cw, ch, fill={i: GREEN_BG for i in done},
              outline={i: ORANGE for i in moved}, index=False)
        s.text(x0 - 6, y + 17, f'{k + 1}', 10, '#6b7280', 'end')


def elementary_sorts_picture():
    start = [5, 2, 4, 6, 1, 3]
    sel, bub, ins = selection_passes(start), bubble_passes(start), insertion_passes(start)
    for ps in (sel, bub, ins):
        assert ps[-1][0] == sorted(start)
    assert [p[0] for p in sel][:2] == [[1, 2, 4, 6, 5, 3], [1, 2, 4, 6, 5, 3]]
    assert bub[0][0] == [2, 4, 5, 1, 3, 6]
    assert ins[2][0] == [2, 4, 5, 6, 1, 3]
    rows = max(len(sel), len(bub), len(ins))
    s = Svg(640, 80 + (rows + 1) * 36 + 30, 'Selection, bubble and insertion sort on [5, 2, 4, 6, 1, 3], one row per '
            'pass. Selection grows a sorted prefix by swapping in the minimum; bubble grows a sorted suffix as the '
            'largest value bubbles right; insertion keeps the front sorted among itself and slides each new element '
            'into place. Green cells are the sorted part, orange outlines are what moved')
    passes_panel(s, 40, 24, start, sel, 'Selection', 'green = final, smallest first')
    passes_panel(s, 250, 24, start, bub, 'Bubble', 'green = final, largest last')
    passes_panel(s, 460, 24, start, ins, 'Insertion', 'green = sorted among itself')
    s.text(320, 80 + (rows + 1) * 36 + 14, 'Orange outline: the elements that moved in that pass.', 11)
    save(s, 'elementary-sorts-passes.svg')


def elementary_sketch():
    start = [4, 9, 2, 7, 1]
    sel = selection_passes(start)
    assert [p[0] for p in sel] == [[1, 9, 2, 7, 4], [1, 2, 9, 7, 4], [1, 2, 4, 7, 9], [1, 2, 4, 7, 9]]
    s = Svg(260, 80 + (len(sel) + 1) * 36, 'Selection sort on [4, 9, 2, 7, 1], one row per pass: [1, 9, 2, 7, 4], '
            '[1, 2, 9, 7, 4], [1, 2, 4, 7, 9], and a last pass that swaps nothing; the sorted prefix (green) grows by '
            'one each pass')
    passes_panel(s, 60, 24, start, sel, 'Selection sort', 'green = final, orange = swapped')
    save(s, 'selection-sketch.svg')


def lesson_elementary():
    elementary_sorts_picture()
    elementary_sketch()


# =====================================================================
# 05-sorting/03 merge sort
# =====================================================================

def merge_trace(left, right):
    i = j = 0
    out, steps = [], []
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            steps.append((i, j, 'L', f'{left[i]} ≤ {right[j]}: take {left[i]} from the left'))
            out.append(left[i]); i += 1
        else:
            steps.append((i, j, 'R', f'{left[i]} > {right[j]}: take {right[j]} from the right'))
            out.append(right[j]); j += 1
    rest = left[i:] + right[j:]
    steps.append((i, j, 'rest', f'one side is empty: copy {rest} without comparing'))
    return out + rest, steps


def merge_step_picture():
    left, right = [27, 38, 43], [3, 9, 10, 82]
    out, steps = merge_trace(left, right)
    assert out == [3, 9, 10, 27, 38, 43, 82] and sum(1 for st in steps if st[2] != 'rest') == 6
    cw, ch, rh = 28, 24, 52
    s = Svg(600, 52 + rh * len(steps), 'Merging the sorted lists [27, 38, 43] and [3, 9, 10, 82]: one pointer '
            'per list, always take the smaller head; 3, 9 and 10 come from the right, then 27, 38, 43 from the left, '
            'and 82 is copied at the end; 6 comparisons build [3, 9, 10, 27, 38, 43, 82]')
    t(s, 300, 20, 'One merge: compare the two heads, take the smaller, move that pointer', 13, None, 'bold')
    done = []
    for k, (i, j, side, msg) in enumerate(steps):
        y = 52 + k * rh
        fl = {a: LIGHT for a in range(i)}
        fr = {b: LIGHT for b in range(j)}
        ol, orr = {}, {}
        if side == 'L':
            ol[i] = ORANGE
        elif side == 'R':
            orr[j] = ORANGE
        cells(s, 20, y, left, cw, ch, fill=fl, outline=ol, index=False, dim=range(i))
        cells(s, 120, y, right, cw, ch, fill=fr, outline=orr, index=False, dim=range(j))
        if side == 'L':
            done.append(left[i])
        elif side == 'R':
            done.append(right[j])
        else:
            done += left[i:] + right[j:]
        cells(s, 262, y, done, cw, ch, fill={a: GREEN_BG for a in range(len(done))}, index=False)
        s.add(f'<text x="20" y="{y + ch + 15}" font-size="10" fill="#374151" text-anchor="start">{msg}</text>')
    for x, lab in ((62, 'left'), (176, 'right'), (290, 'output')):
        t(s, x, 44, lab, 11, '#6b7280', 'bold')
    save(s, 'merge-step.svg')


def lesson_merge_sort():
    arr = [38, 27, 43, 3, 9, 82, 10]
    out, _, rows = split_merge_svg(arr, 'merge-sort-split-merge.svg',
                                   'Merge sort on [38, 27, 43, 3, 9, 82, 10]: split by position into [38, 27, 43] and '
                                   '[3, 9, 82, 10], down to single elements (yellow), then merged back up: [27, 43], '
                                   '[3, 9], [10, 82], [27, 38, 43], [3, 9, 10, 82] and finally [3, 9, 10, 27, 38, 43, 82]',
                                   'Split by position going down, merge in order coming up')
    assert out == sorted(arr)
    assert [v for _, _, v, _ in rows[('split', 1)]] == [[38, 27, 43], [3, 9, 82, 10]]
    assert [v for _, _, v, _ in rows[('merge', 1)]] == [[27, 38, 43], [3, 9, 10, 82]]
    merge_step_picture()
    arr = [9, 4, 7, 1, 6, 2]
    out, _, rows = split_merge_svg(arr, 'merge-sort-sketch.svg',
                                   'Merge sort on [9, 4, 7, 1, 6, 2]: split into [9, 4, 7] and [1, 6, 2], then [9] and '
                                   '[4, 7], [1] and [6, 2], down to single elements; merging back up gives [4, 7], '
                                   '[2, 6], [4, 7, 9], [1, 2, 6] and finally [1, 2, 4, 6, 7, 9]',
                                   'Split going down, merge coming up')
    assert [v for _, _, v, _ in rows[('merge', 1)]] == [[4, 7, 9], [1, 2, 6]]


# =====================================================================
# 05-sorting/04 quicksort
# =====================================================================

def lomuto_trace(a):
    """The lesson's Lomuto partition on the whole array, recording the state after each step."""
    a = list(a)
    lo, hi = 0, len(a) - 1
    pivot, i = a[hi], lo - 1
    rows = [(list(a), i, None, f'start: pivot = {pivot} (last element), i = {i}')]
    for j in range(lo, hi):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
            msg = f'j = {j}: {a[i]} ≤ {pivot}, so i = {i} and swap a[{i}] with a[{j}]'
        else:
            msg = f'j = {j}: {a[j]} > {pivot}, leave it'
        rows.append((list(a), i, j, msg))
    a[i + 1], a[hi] = a[hi], a[i + 1]
    rows.append((list(a), i, 'final', f'swap the pivot into a[{i + 1}]: it is now in its final place'))
    return a, i + 1, rows


def lomuto_picture():
    arr = [3, 8, 2, 5, 1, 4]
    out, p, rows = lomuto_trace(arr)
    assert out == [3, 2, 1, 4, 8, 5] and p == 3
    w = [7, 2, 9, 4, 1, 6, 5]                               # the lesson's worked problem 1
    assert lomuto_trace(w)[:2] == ([2, 4, 1, 5, 9, 6, 7], 3)
    cw, ch, rh = 34, 26, 50
    n = len(arr)
    s = Svg(420, 50 + rh * len(rows), 'Lomuto partition of [3, 8, 2, 5, 1, 4] with pivot 4: j scans left to right; 3, '
            '2 and 1 are at most 4 and are swapped into the green region at the front, 8 and 5 stay in the red '
            'region; finally the pivot swaps into index 3, giving [3, 2, 1, 4, 8, 5]')
    t(s, 210, 20, 'green: ≤ pivot,  red: > pivot,  yellow: the pivot', 12, None, 'bold')
    for k, (a, i, j, msg) in enumerate(rows):
        y = 40 + k * rh
        fill = {}
        if j == 'final':
            fill = {x: GREEN_BG for x in range(i + 1)}
            fill[i + 1] = YELLOW_BG
            fill.update({x: RED_BG for x in range(i + 2, n)})
            out_l = {i + 1: ORANGE}
        else:
            fill = {x: GREEN_BG for x in range(i + 1)}
            if j is not None:
                fill.update({x: RED_BG for x in range(i + 1, j + 1)})
            fill[n - 1] = YELLOW_BG
            out_l = {j: ORANGE} if j is not None else {}
        cells(s, 30, y, a, cw, ch, fill=fill, outline=out_l, index=(k == 0))
        s.add(f'<text x="30" y="{y + ch + 14}" font-size="11" fill="#374151" text-anchor="start">{msg}</text>')
    save(s, 'lomuto-partition.svg')


def quicksort_tree(arr, tag, L, col):
    """Lomuto quicksort; draw each call as a node showing left part | pivot | right part."""
    ids = iter(range(1000))
    depth = [0]

    def qs(a, d):
        i = next(ids)
        depth[0] = max(depth[0], d)
        if len(a) <= 1:
            L.append(f'{tag}{i} [label="{a}" , fillcolor="{GREEN_BG}"];' if a else
                     f'{tag}{i} [label="[ ]", fillcolor="#ffffff", color="{GREY}", fontcolor="{GREY}"];')
            return i, list(a)
        out, p, _ = lomuto_trace(a)
        left, right = out[:p], out[p + 1:]
        lab = f'{left} <FONT COLOR="#b45309"><B>{out[p]}</B></FONT> {right}'.replace('[]', '[ ]')
        L.append(f'{tag}{i} [label=<{lab}>, fillcolor="{BLUE_BG}", color="{col}"];')
        li, ls = qs(left, d + 1)
        ri, rs = qs(right, d + 1)
        L.append(f'{tag}{i} -> {tag}{li}; {tag}{i} -> {tag}{ri};')
        return i, ls + [out[p]] + rs

    _, res = qs(arr, 0)
    assert res == sorted(arr)
    return depth[0]


def quicksort_depth_picture():
    mixed, srt = [2, 7, 1, 5, 3, 8, 6, 4], list(range(1, 9))
    L = dot_header('nodesep=0.15; ranksep=0.28;')
    L.append(f'subgraph cluster_a {{ label="mixed input: 3 levels deep"; fontname="{FONT}"; fontsize=12; '
             f'color="#d1d5db"; style=rounded;')
    da = quicksort_tree(mixed, 'a', L, ACCENT)
    L.append('}')
    L.append(f'subgraph cluster_b {{ label="sorted input: 7 levels deep"; fontname="{FONT}"; fontsize=12; '
             f'color="#d1d5db"; style=rounded;')
    db = quicksort_tree(srt, 'b', L, TRUE)
    L += ['}', '}']
    assert (da, db) == (3, 7)
    dot('\n'.join(L), 'quicksort-depth.svg',
        'Quicksort calls with a last-element pivot. Each box shows the left part, the pivot, and the right part. On the '
        'mixed array [2, 7, 1, 5, 3, 8, 6, 4] the pivot 4 lands in the middle and the tree is 3 levels deep. On the '
        'sorted array 1 to 8 every pivot is the maximum, one side is always empty, and the tree is a chain 7 levels deep')


def quicksort_sketch():
    L = dot_header('nodesep=0.15; ranksep=0.3;')
    d = quicksort_tree([5, 1, 6, 3, 7, 2, 4], 'q', L, INK)
    L.append('}')
    assert d == 3
    dot('\n'.join(L), 'quicksort-sketch.svg',
        'Quicksort with Lomuto partition on [5, 1, 6, 3, 7, 2, 4]: pivot 4 splits it into [1, 3, 2] and [7, 6, 5]; '
        'pivot 2 splits [1, 3, 2] into [1] and [3]; pivot 5 splits [7, 6, 5] into nothing and [6, 7], and pivot 7 '
        'splits [6, 7] into [6] and nothing')


def lesson_quicksort():
    lomuto_picture()
    quicksort_depth_picture()
    quicksort_sketch()


# =====================================================================
# 05-sorting/05 non-comparison sorts
# =====================================================================

KEY_COLOURS = ['#dbeafe', '#fef3c7', '#d1fae5', '#fee2e2', '#ede9fe', '#fce7f3', '#e0f2fe', '#f3f4f6',
               '#ecfccb', '#ffedd5']


def counting_sort_steps(xs, k):
    count = [0] * (k + 1)
    for v in xs:
        count[v] += 1
    counts = list(count)
    for i in range(1, k + 1):
        count[i] += count[i - 1]
    prefix = list(count)
    out = [None] * len(xs)
    for i in reversed(range(len(xs))):
        count[xs[i]] -= 1
        out[count[xs[i]]] = xs[i]
    return counts, prefix, out


def counting_sort_picture():
    xs, k = [2, 5, 3, 0, 2, 3, 0, 3], 5
    counts, prefix, out = counting_sort_steps(xs, k)
    assert counts == [2, 0, 2, 3, 0, 1] and prefix == [2, 2, 4, 7, 7, 8] and out == sorted(xs)
    assert counting_sort_steps([3, 1, 4, 1, 0, 3, 2, 3], 4)[:2] == ([1, 2, 1, 3, 1], [1, 3, 4, 7, 8])
    cw, ch = 36, 28
    s = Svg(470, 330, 'Counting sort on [2, 5, 3, 0, 2, 3, 0, 3] with keys 0 to 5: the counts are [2, 0, 2, 3, 0, 1]; '
            'the prefix sums [2, 2, 4, 7, 7, 8] say where each key\'s run ends; walking the input backwards places '
            'every element, giving [0, 0, 2, 2, 3, 3, 3, 5]')
    col = lambda v: KEY_COLOURS[v]
    x0 = 150
    rows = [('1. input', xs, {i: col(v) for i, v in enumerate(xs)}, 'index'),
            ('2. count of each key', counts, {}, 'key'),
            ('3. prefix sums: run ends', prefix, {}, 'key'),
            ('4. output', out, {i: col(v) for i, v in enumerate(out)}, 'index')]
    for k_, (lab, vals, fill, idx) in enumerate(rows):
        y = 40 + k_ * 72
        s.add(f'<text x="{x0 - 12}" y="{y + 18}" font-size="12" font-weight="bold" text-anchor="end">{lab}</text>')
        if idx == 'key':
            fill = {i: col(i) for i in range(len(vals))}
        cells(s, x0, y, vals, cw, ch, fill=fill)
        s.add(f'<text x="{x0 - 12}" y="{y - 6}" font-size="10" fill="#6b7280" text-anchor="end">{idx}</text>')
    t(s, 235, 322, 'Same colour = same key. The prefix sum for key 3 is 7, so the 3s fill positions 4, 5 and 6.', 11)
    save(s, 'counting-sort.svg')


def radix_passes(xs, digits=3):
    rows = [list(xs)]
    for d in range(digits):
        cur = rows[-1]
        rows.append(sorted(cur, key=lambda v: (v // 10 ** d) % 10))      # Python's sort is stable
    return rows


def radix_picture():
    xs = [170, 45, 75, 90, 802, 24, 2, 66]
    rows = radix_passes(xs)
    assert [f'{v:03d}' for v in rows[1]] == '170 090 802 002 024 045 075 066'.split()
    assert [f'{v:03d}' for v in rows[2]] == '802 002 024 045 066 170 075 090'.split()
    assert rows[3] == sorted(xs)
    assert radix_passes([329, 457, 657, 839, 436, 720, 355])[1] == [720, 355, 436, 457, 657, 329, 839]
    cw, ch, rh = 46, 26, 66
    x0 = 100
    s = Svg(x0 + cw * 8 + 20, 40 + rh * 4, 'LSD radix sort on [170, 45, 75, 90, 802, 24, 2, 66], one stable pass per '
            'digit: by the 1s digit, then the 10s, then the 100s; lines follow each number from row to row, and the '
            'digit being sorted on is shown in orange')
    labels = ['input', 'by 1s', 'by 10s', 'by 100s']
    for k, row in enumerate(rows):
        y = 30 + k * rh
        if k:
            prev = rows[k - 1]
            for i, v in enumerate(row):
                j = prev.index(v)
                s.line(x0 + j * cw + cw / 2, y - rh + ch, x0 + i * cw + cw / 2, y, GREY, 1)
    for k, row in enumerate(rows):
        y = 30 + k * rh
        s.add(f'<text x="{x0 - 12}" y="{y + 17}" font-size="12" font-weight="bold" text-anchor="end">{labels[k]}</text>')
        for i, v in enumerate(row):
            r(s, x0 + i * cw + 2, y, cw - 4, ch, '#ffffff', INK)
            digs = f'{v:03d}'
            hot = 3 - k if k else None
            parts = ''.join(f'<tspan fill="{ORANGE}" font-weight="bold">{c}</tspan>' if hot is not None and p == hot
                            else c for p, c in enumerate(digs))
            s.add(f'<text x="{x0 + i * cw + cw / 2:.0f}" y="{y + 18}" font-size="13">{parts}</text>')
    save(s, 'radix-passes.svg')


def lesson_non_comparison():
    counting_sort_picture()
    radix_picture()


# =====================================================================
# 06-greedy-algorithms/01 when greedy works
# =====================================================================

def greedy_coins(coins, amount):
    out = []
    for c in sorted(coins, reverse=True):
        while amount >= c:
            out.append(c)
            amount -= c
    return out


def dp_coins(coins, amount):
    """Fewest coins by dynamic programming, with the coins used."""
    best = [0] + [None] * amount
    used = [None] * (amount + 1)
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] is not None and (best[a] is None or best[a - c] + 1 < best[a]):
                best[a], used[a] = best[a - c] + 1, c
    out, a = [], amount
    while a and used[a]:
        out.append(used[a])
        a -= used[a]
    return best, sorted(out, reverse=True)


def trail_picture():
    paths = {'+150 m branch': [150], '+200 m branch': [200, -300]}
    greedy = max(paths, key=lambda p: paths[p][0])
    best = max(paths, key=lambda p: sum(paths[p]))
    assert greedy == '+200 m branch' and best == '+150 m branch'
    assert sum(paths[greedy]) == -100 and sum(paths[best]) == 150
    L = dot_header('rankdir=LR; nodesep=0.3; ranksep=0.5;')
    L += [f'S [label="Start", fillcolor="{LIGHT}"];',
          f'A [label="+150 m\\ntotal +150 m", fillcolor="{GREEN_BG}", color="{ACCENT}", penwidth=2.4];',
          f'B [label="+200 m", fillcolor="{YELLOW_BG}", color="{ORANGE}", penwidth=2.4];',
          f'C [label="−300 m\\ntotal −100 m", fillcolor="{RED_BG}", color="{ORANGE}", penwidth=2.4];',
          f'S -> A [label=" best overall ", color="{ACCENT}", fontcolor="{ACCENT}", penwidth=2];',
          f'S -> B [label=" greedy: steeper now ", color="{ORANGE}", fontcolor="#b45309", penwidth=2];',
          f'B -> C [color="{ORANGE}", penwidth=2];', '}']
    dot('\n'.join(L), 'greedy-trail.svg',
        'A trail junction: the greedy hiker takes the steeper +200 m branch, which then drops 300 m for a total of '
        'minus 100 m; the other branch gains only +150 m now but +150 m overall, which is the best choice')


def coin_trap_picture():
    coins, amount = [1, 3, 4], 6
    g = greedy_coins(coins, amount)
    best, opt = dp_coins(coins, amount)
    assert g == [4, 1, 1] and opt == [3, 3] and best[amount] == 2
    s = Svg(440, 190, 'Making 6 from coins 1, 3 and 4: greedy grabs the biggest coin first and ends with 4 + 1 + 1, '
            'three coins; the best answer is 3 + 3, two coins')
    colours = {1: '#e5e7eb', 3: '#bfdbfe', 4: '#fde68a'}

    def row(y, label, cs, col):
        s.add(f'<text x="20" y="{y + 5}" font-size="13" font-weight="bold" fill="{col}" text-anchor="start">{label}</text>')
        x = 200
        for c in cs:
            rad = 16 + 4 * c
            s.circle(x + rad, y, rad, colours[c], INK)
            t(s, x + rad, y + 6, c, 16, None, 'bold')
            x += 2 * rad + 10
        t(s, x + 24, y + 5, f'{len(cs)} coins', 13, col, 'bold')

    row(55, 'greedy (biggest first)', g, TRUE)
    row(140, 'best (found by DP)', opt, ACCENT)
    save(s, 'coin-trap.svg')


def canoe_picture():
    weights, k = [60, 20, 75, 45, 30, 85], 100
    w = sorted(weights)
    left, right, steps = 0, len(w) - 1, []
    while left <= right:
        if left < right and w[left] + w[right] <= k:
            steps.append((left, right, [w[right], w[left]], f'{w[right]} + {w[left]} = {w[right] + w[left]} ≤ {k}: share'))
            left += 1
        else:
            why = f'{w[right]} + {w[left]} = {w[right] + w[left]} > {k}: {w[right]} goes alone' if left < right \
                else f'only {w[right]} is left: alone'
            steps.append((left, right, [w[right]], why))
        right -= 1
    assert len(steps) == 4 and [b for *_, b, _ in steps] == [[85], [75, 20], [60, 30], [45]]
    cw, ch, rh = 40, 28, 62
    s = Svg(560, 40 + rh * len(steps) + 10, 'Canoe pairing for weights 20, 30, 45, 60, 75, 85 with a 100 kg limit: '
            '85 cannot share with 20 so goes alone; 75 shares with 20; 60 shares with 30; 45 goes alone; 4 canoes')
    t(s, 280, 20, 'Sorted weights. Pair the heaviest (right) with the lightest (left) if they fit.', 12, None, 'bold')
    for n_, (lo, hi, boat, msg) in enumerate(steps):
        y = 36 + n_ * rh
        seated = set()
        for (a, b, bt, _) in steps[:n_]:
            seated.add(b)
            if len(bt) == 2:
                seated.add(a)
        out = {hi: ORANGE}
        if len(boat) == 2:
            out[lo] = ORANGE
        cells(s, 20, y, w, cw, ch, outline=out, dim=seated, index=False)
        marks = [(lo, 'left/right')] if lo == hi else [(lo, 'left'), (hi, 'right')]
        for i, lab in marks:
            t(s, 20 + i * cw + cw / 2, y + ch + 13, lab, 10, PIX, 'bold')
        bx = 290
        s.path(f'M{bx} {y + 6} h{40 * len(boat) + 30} l-14 {ch - 6} h-{40 * len(boat) + 2} z', '#92400e', 1.5,
               '#fde68a')
        for q, wt in enumerate(boat):
            t(s, bx + 26 + q * 40, y + 22, wt, 12, None, 'bold')
        s.add(f'<text x="{bx}" y="{y + ch + 18}" font-size="10" fill="#374151" text-anchor="start">canoe {n_ + 1}: {msg}</text>')
    save(s, 'canoe-pairing.svg')


def lesson_when_greedy():
    trail_picture()
    coin_trap_picture()
    canoe_picture()


# =====================================================================
# 06-greedy-algorithms/02 selection and scheduling
# =====================================================================

def earliest_end(meetings):
    chosen, last = [], -math.inf
    for st, en in sorted(meetings, key=lambda m: m[1]):
        if st >= last:
            chosen.append((st, en))
            last = en
    return chosen


def any_order_greedy(meetings, key):
    """Take meetings in `key` order, keeping each one that does not overlap anything already kept."""
    chosen = []
    for m in sorted(meetings, key=key):
        if all(m[0] >= c[1] or m[1] <= c[0] for c in chosen):
            chosen.append(m)
    return chosen


def timeline(s, x0, y0, w, tmax, meetings, chosen, label, bar_h=14, gap=6, ticks=True):
    X = lambda v: x0 + v / tmax * w
    if label:
        s.add(f'<text x="{x0}" y="{y0 - 6}" font-size="12" font-weight="bold" text-anchor="start">{label}</text>')
    for k, (a, b) in enumerate(meetings):
        y = y0 + k * (bar_h + gap)
        on = (a, b) in chosen
        r(s, X(a), y, X(b) - X(a), bar_h, GREEN_BG if on else LIGHT, ACCENT if on else GREY, 2 if on else 1)
        t(s, (X(a) + X(b)) / 2, y + bar_h - 3, f'{a}–{b}', 10, INK if on else '#6b7280')
    if ticks:
        yb = y0 + len(meetings) * (bar_h + gap)
        s.line(X(0), yb, X(tmax), yb, GREY, 1)
        for v in range(0, tmax + 1):
            t(s, X(v), yb + 12, v, 9, '#6b7280')


def scheduling_picture():
    ms = [(1, 3), (2, 5), (4, 7), (6, 8), (0, 10)]
    end = earliest_end(ms)
    start = any_order_greedy(ms, lambda m: m[0])
    short = any_order_greedy(ms, lambda m: (m[1] - m[0], m[0]))
    assert end == [(1, 3), (4, 7)] and start == [(0, 10)] and sorted(short) == [(1, 3), (6, 8)]
    panel_h = len(ms) * 20 + 40
    s = Svg(520, 20 + 3 * panel_h, 'The meetings 1–3, 2–5, 4–7, 6–8 and 0–10 on a timeline, three times. Earliest end '
            'first keeps 1–3 and 4–7 (2 meetings). Earliest start first keeps only 0–10 (1 meeting). Shortest first '
            'keeps 1–3 and 6–8 (2 meetings, a tie that hides the flaw)')
    for k, (lab, ch_) in enumerate([('Earliest END first: 2 meetings (correct rule)', end),
                                    ('Earliest START first: 1 meeting', start),
                                    ('SHORTEST first: 2 meetings here, but wrong in general', short)]):
        timeline(s, 30, 30 + k * panel_h, 460, 10, ms, ch_, lab)
    save(s, 'interval-sort-keys.svg')


def rooms_picture():
    ms = [(1, 3), (2, 5), (4, 7), (6, 8), (0, 10)]
    events = sorted([(a, 1) for a, b in ms] + [(b, -1) for a, b in ms])
    cur, peak, steps = 0, 0, []
    for tm, d in events:
        cur += d
        peak = max(peak, cur)
        steps.append((tm, cur))
    assert peak == 3
    s = Svg(520, 300, 'The same five meetings on a timeline with the number running at each moment underneath: the count '
            'rises at each start and falls at each end, and its peak is 3 (for example from 2 to 3 and from 4 to 5), '
            'so 3 rooms are needed')
    timeline(s, 30, 30, 460, 10, ms, ms, 'Every meeting must be held', ticks=False)
    p = Plot(s, 30, 150, 460, 100, (0, 10), (0, 3.5))
    for v in range(0, 4):
        s.line(p.X(0), p.Y(v), p.X(10), p.Y(v), '#eef2f6', 1)
        t(s, p.X(0) - 8, p.Y(v) + 4, v, 10, '#6b7280')
    pts, prev = [], 0
    for tm, c in steps:
        pts += [(tm, prev), (tm, c)]
        prev = c
    p.curve(pts, PIX, 2.4)
    for tm, c in steps:
        if c == peak:
            p.dot(tm, c, TRUE, 4)
    s.line(p.X(0), p.Y(0), p.X(10), p.Y(0), INK, 1.2)
    for v in range(11):
        t(s, p.X(v), p.Y(0) + 14, v, 9, '#6b7280')
    s.add(f'<text x="30" y="{p.Y(3.5) - 8:.0f}" font-size="12" font-weight="bold" text-anchor="start">Meetings running '
          f'at each moment: +1 at a start, −1 at an end</text>')
    t(s, 260, 292, f'The highest point is {peak}, so {peak} rooms are needed.', 12, TRUE, 'bold')
    save(s, 'rooms-sweep.svg')


def scheduling_sketch():
    ms = [(0, 3), (2, 4), (3, 6), (5, 7), (1, 8), (6, 9), (8, 10)]
    end = earliest_end(ms)
    assert end == [(0, 3), (3, 6), (6, 9)]
    s = Svg(520, 30 + len(ms) * 20 + 40, 'The meetings 0–3, 2–4, 3–6, 5–7, 1–8, 6–9 and 8–10 on a timeline; earliest '
            'end first keeps 0–3, 3–6 and 6–9, three meetings')
    timeline(s, 30, 30, 460, 10, ms, end, 'Earliest end first keeps 3 meetings (green)')
    save(s, 'interval-sketch.svg')


def lesson_scheduling():
    scheduling_picture()
    rooms_picture()
    scheduling_sketch()


# =====================================================================
# 07-dynamic-programming/01 what makes a problem DP
# =====================================================================

def simple_paths(edges, a, b):
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    out = []

    def go(path):
        if path[-1] == b:
            out.append(path)
            return
        for nxt in sorted(adj[path[-1]]):
            if nxt not in path:
                go(path + [nxt])

    go([a])
    return out


def substructure_picture():
    edges = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('C', 'D')]
    shortest = min(simple_paths(edges, 'A', 'D'), key=len)
    long_ab = max(simple_paths(edges, 'A', 'B'), key=len)
    long_bd = max(simple_paths(edges, 'B', 'D'), key=len)
    long_ad = max(len(p_) for p_ in simple_paths(edges, 'A', 'D')) - 1
    assert shortest == ['A', 'B', 'D'] and long_ab == ['A', 'C', 'D', 'B'] and long_bd == ['B', 'A', 'C', 'D']
    assert long_ad == 3
    pos = {'A': (0, 0), 'B': (1, 0), 'C': (0, 1), 'D': (1, 1)}
    s = Svg(600, 240, 'The graph with edges A–B, A–C, B–C, B–D and C–D drawn three times. Left: the shortest path from A '
            'to D is A, B, D. Middle: the longest simple path from A to B is A, C, D, B. Right: the longest simple path '
            'from B to D is B, A, C, D. The two longest paths both need C and D, so they cannot be joined')
    mk = arrow_defs(s)
    panels = [('shortest A→D = 2', shortest, ACCENT), ('longest A→B = 3', long_ab, ORANGE),
              ('longest B→D = 3', long_bd, PIX)]
    for k, (lab, path, col) in enumerate(panels):
        ox, oy, sc = 50 + k * 195, 50, 110
        P = lambda n: (ox + pos[n][0] * sc, oy + pos[n][1] * sc)
        for u, v in edges:
            (x1, y1), (x2, y2) = P(u), P(v)
            s.line(x1, y1, x2, y2, '#d1d5db', 2)
        for u, v in zip(path, path[1:]):
            (x1, y1), (x2, y2) = P(u), P(v)
            d = math.hypot(x2 - x1, y2 - y1)
            f = 17 / d
            arrow(s, mk, x1 + (x2 - x1) * f, y1 + (y2 - y1) * f, x2 - (x2 - x1) * f, y2 - (y2 - y1) * f, col, 3)
        for n in pos:
            x, y = P(n)
            on = n in path
            s.circle(x, y, 15, '#ffffff' if not on else LIGHT, col if on else GREY)
            t(s, x, y + 5, n, 14, INK, 'bold')
        t(s, ox + sc / 2, oy + sc + 42, lab, 13, col, 'bold')
        t(s, ox + sc / 2, oy + sc + 60, ' → '.join(path), 12, '#374151')
    t(s, 300, 22, 'All edges have weight 1', 12, '#6b7280')
    save(s, 'substructure-paths.svg')
    # the plain graph, for where the lesson first introduces it
    g = Svg(220, 170, 'A graph of four vertices: A and B on top, C and D below, with edges A–B, A–C, B–C, B–D and C–D, '
            'each of weight 1')
    P = lambda n: (55 + pos[n][0] * 110, 35 + pos[n][1] * 100)
    for u, v in edges:
        (x1, y1), (x2, y2) = P(u), P(v)
        g.line(x1, y1, x2, y2, INK, 2)
    for n in pos:
        x, y = P(n)
        g.circle(x, y, 15, BLUE_BG, INK)
        t(g, x, y + 5, n, 14, INK, 'bold')
    save(g, 'substructure-graph.svg')


def lesson_what_is_dp():
    substructure_picture()


# =====================================================================
# 07-dynamic-programming/02 memoisation and tabulation
# =====================================================================

def stairs_table(n):
    ways = [0] * (n + 1)
    ways[0] = ways[1] = 1
    for i in range(2, n + 1):
        ways[i] = ways[i - 1] + ways[i - 2]
    return ways


def stairs_picture():
    ways = stairs_table(8)
    assert ways == [1, 1, 2, 3, 5, 8, 13, 21, 34] and stairs_table(10)[10] == 89
    cw, ch = 46, 34
    s = Svg(470, 176, 'The climbing-stairs table ways[0..8] = 1, 1, 2, 3, 5, 8, 13, 21, 34, filled left to right; '
            'cell 6 reads only the two cells just before it: ways[6] = ways[5] + ways[4] = 8 + 5 = 13')
    mk = arrow_defs(s)
    x0, y0 = 28, 86
    fill = {i: GREEN_BG for i in range(6)}
    fill[6] = YELLOW_BG
    cells(s, x0, y0, ways, cw, ch, fill=fill, outline={6: ORANGE}, dim=[7, 8], size=14)
    for j, col in ((5, PIX), (4, ACCENT)):
        x1, x2 = x0 + j * cw + cw / 2, x0 + 6 * cw + cw / 2 - 6
        h = 26 if j == 5 else 46
        s.path(f'M{x1:.0f} {y0 - 16} C{x1:.0f} {y0 - 16 - h} {x2:.0f} {y0 - 16 - h} {x2:.0f} {y0 - 17}', col, 2.2)
        s.add(f'<path d="M{x2 - 5:.0f} {y0 - 23} L{x2:.0f} {y0 - 16} L{x2 + 5:.0f} {y0 - 23}" fill="none" stroke="{col}" stroke-width="2.2"/>')
    t(s, x0 + 6 * cw + cw / 2, 20, 'ways[6] = ways[5] + ways[4] = 8 + 5 = 13', 13, INK, 'bold')
    t(s, 235, 146, 'Green cells are final. Cell 6 reads only cells to its left, so left-to-right is the fill order.', 11)
    t(s, 235, 164, 'Grey cells are not filled yet.', 11, '#6b7280')
    save(s, 'stairs-table.svg')


def grid_paths(rows, cols):
    table = [[1] * cols for _ in range(rows)]
    for i in range(1, rows):
        for j in range(1, cols):
            table[i][j] = table[i - 1][j] + table[i][j - 1]
    return table


def grid_table_svg(rows, cols, name, title, focus=None, note=''):
    tb = grid_paths(rows, cols)
    cw = 44
    s = Svg(cols * cw + 60, rows * cw + 70, title)
    mk = arrow_defs(s)
    x0, y0 = 40, 34
    for j in range(cols):
        t(s, x0 + j * cw + cw / 2, y0 - 8, f'col {j}', 10, '#6b7280')
    for i in range(rows):
        s.add(f'<text x="{x0 - 8}" y="{y0 + i * cw + cw / 2 + 4:.0f}" font-size="10" fill="#6b7280" text-anchor="end">row {i}</text>')
        for j in range(cols):
            f = LIGHT if (i == 0 or j == 0) else '#ffffff'
            if focus and (i, j) == focus:
                f = YELLOW_BG
            r(s, x0 + j * cw, y0 + i * cw, cw, cw, f, INK)
            t(s, x0 + j * cw + cw / 2, y0 + i * cw + cw / 2 + 5, tb[i][j], 14, None, 'bold' if (i, j) == (rows - 1, cols - 1) else None)
    if focus:
        i, j = focus
        cx, cy = x0 + j * cw + cw / 2, y0 + i * cw + cw / 2
        arrow(s, mk, cx, cy - cw + 12, cx, cy - 12, PIX, 2.2)
        arrow(s, mk, cx - cw + 12, cy, cx - 13, cy, ACCENT, 2.2)
        r(s, x0 + j * cw + 1.5, y0 + i * cw + 1.5, cw - 3, cw - 3, 'none', ORANGE, 3)
    if note:
        t(s, (cols * cw + 60) / 2, y0 + rows * cw + 24, note, 11)
    save(s, name)
    return tb


def lesson_tabulation():
    stairs_picture()
    tb = grid_table_svg(4, 5, 'grid-paths-table.svg',
                        'The unique-paths table for a 4 by 5 grid: the top row and left column are all 1; every other '
                        'cell is the cell above plus the cell to the left, for example row 2, col 3 is 4 + 6 = 10; '
                        'the bottom-right corner is 35', focus=(2, 3),
                        note='Each cell = the cell above + the cell to the left.')
    assert tb[2][3] == 10 and tb[3][4] == 35 and grid_paths(3, 3)[2][2] == 6
    assert grid_paths(18, 18)[17][17] == 2333606220
    tb = grid_table_svg(3, 4, 'grid-paths-sketch.svg',
                        'The unique-paths table for a 3 by 4 grid: the top row and left column are 1; the middle row '
                        'is 1, 2, 3, 4; the bottom row is 1, 3, 6, 10, so there are 10 paths')
    assert tb == [[1, 1, 1, 1], [1, 2, 3, 4], [1, 3, 6, 10]]


# =====================================================================
# 07-dynamic-programming/03 classic one-dimensional
# =====================================================================

def house_robber_picture():
    nums = [2, 7, 9, 3, 1]
    best = [nums[0], max(nums[0], nums[1])]
    for i in range(2, len(nums)):
        best.append(max(best[i - 1], best[i - 2] + nums[i]))
    assert best == [2, 7, 11, 11, 12]
    robbed, i = [], len(nums) - 1                      # walk back: equal to predecessor means skip
    while i >= 0:
        if i == 0 or (i == 1 and best[1] == nums[1] and nums[1] > nums[0]) or (i >= 2 and best[i] != best[i - 1]):
            robbed.append(i)
            i -= 2
        else:
            i -= 1
    robbed.reverse()
    assert robbed == [0, 2, 4] and sum(nums[k] for k in robbed) == 12
    cw = 64
    s = Svg(400, 250, 'House robber on [2, 7, 9, 3, 1]: the best-so-far row is 2, 7, 11, 11, 12; walking back from '
            'the end, a cell bigger than the one before it means that house was robbed, giving houses 0, 2 and 4 '
            'for 2 + 9 + 1 = 12')
    x0 = 40
    for k, v in enumerate(nums):
        x = x0 + k * cw
        on = k in robbed
        col = ACCENT if on else GREY
        s.path(f'M{x + 8} {78} L{x + cw / 2} {50} L{x + cw - 8} {78} Z', col, 1.4, GREEN_BG if on else LIGHT)
        r(s, x + 12, 78, cw - 24, 34, GREEN_BG if on else LIGHT, col, 1.4)
        t(s, x + cw / 2, 101, v, 14, None, 'bold')
        t(s, x + cw / 2, 40, f'house {k}', 10, '#6b7280')
    s.add(f'<text x="{x0 - 6}" y="{160}" font-size="11" fill="#6b7280" text-anchor="end">best</text>')
    cells(s, x0, 140, best, cw, 30, fill={k: GREEN_BG for k in robbed}, index=False, size=13)
    t(s, 200, 200, 'best[3] = best[2] = 11: house 3 was skipped.', 12, '#374151')
    t(s, 200, 222, 'Robbed (green): houses 0, 2, 4 → 2 + 9 + 1 = 12', 13, ACCENT, 'bold')
    save(s, 'house-robber.svg')


def coin_table_svg(coins, amount, name, title, head):
    best, used = [0] + [None] * amount, [None] * (amount + 1)
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and best[a - c] is not None and (best[a] is None or best[a - c] + 1 < best[a]):
                best[a], used[a] = best[a - c] + 1, c
    path, a = [amount], amount
    while a:
        a -= used[a]
        path.append(a)
    cw = 40 if amount <= 8 else 34
    W = 60 + cw * (amount + 1) + 20
    s = Svg(max(W, 420), 200, title)
    mk = arrow_defs(s)
    x0, y0 = 60, 92
    t(s, max(W, 420) / 2, 20, head, 13, None, 'bold')
    s.add(f'<text x="{x0 - 8}" y="{y0 - 6}" font-size="10" fill="#6b7280" text-anchor="end">a</text>')
    s.add(f'<text x="{x0 - 8}" y="{y0 + 20}" font-size="11" fill="#6b7280" text-anchor="end">best</text>')
    s.add(f'<text x="{x0 - 8}" y="{y0 + 50}" font-size="10" fill="#6b7280" text-anchor="end">last coin</text>')
    cells(s, x0, y0, [b if b is not None else '∞' for b in best], cw, 28,
          fill={a_: YELLOW_BG for a_ in path}, outline={amount: ORANGE})
    for a_ in range(1, amount + 1):
        t(s, x0 + a_ * cw + cw / 2, y0 + 50, used[a_] if used[a_] else '–', 11, '#374151')
    for a1, a2 in zip(path, path[1:]):
        x1, x2 = x0 + a1 * cw + cw / 2, x0 + a2 * cw + cw / 2
        h = 18 + 4 * (a1 - a2)
        s.path(f'M{x1:.0f} {y0 - 14} C{x1:.0f} {y0 - 14 - h} {x2:.0f} {y0 - 14 - h} {x2:.0f} {y0 - 15}', ORANGE, 2)
        s.add(f'<path d="M{x2 - 5:.0f} {y0 - 21} L{x2:.0f} {y0 - 14} L{x2 + 5:.0f} {y0 - 21}" fill="none" stroke="{ORANGE}" stroke-width="2"/>')
        t(s, (x1 + x2) / 2, y0 - 18 - h * 0.75, f'−{a1 - a2}', 11, '#b45309', 'bold')
    coins_used = [a1 - a2 for a1, a2 in zip(path, path[1:])]
    t(s, max(W, 420) / 2, 186, f'Walk back from {amount}: coins ' + ' + '.join(map(str, coins_used)) +
      f' = {amount}, {best[amount]} coins', 12, ACCENT, 'bold')
    save(s, name)
    return best, coins_used


def lis_picture():
    nums = [10, 9, 2, 5, 3, 7, 101, 18]
    lis, prev = [1] * len(nums), [None] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i] and lis[j] + 1 > lis[i]:
                lis[i], prev[i] = lis[j] + 1, j
    assert lis == [1, 1, 1, 2, 2, 3, 4, 4]
    end = lis.index(max(lis))
    seq, k = [], end
    while k is not None:
        seq.append(k)
        k = prev[k]
    seq.reverse()
    assert [nums[k] for k in seq] == [2, 5, 7, 101]
    cw = 52
    s = Svg(40 + cw * 8 + 30, 200, 'Longest increasing subsequence of [10, 9, 2, 5, 3, 7, 101, 18]: lis values '
            '1, 1, 1, 2, 2, 3, 4, 4; following each cell back to the earlier cell it extended picks out 2, 5, 7, 101, '
            'length 4')
    mk = arrow_defs(s)
    x0, y0 = 60, 92
    s.add(f'<text x="{x0 - 8}" y="{y0 + 19}" font-size="11" fill="#6b7280" text-anchor="end">value</text>')
    s.add(f'<text x="{x0 - 8}" y="{y0 + 55}" font-size="11" fill="#6b7280" text-anchor="end">lis[i]</text>')
    cells(s, x0, y0, nums, cw, 28, fill={k: GREEN_BG for k in seq}, outline={k: ACCENT for k in seq})
    cells(s, x0, y0 + 36, lis, cw, 28, index=False, fill={k: GREEN_BG for k in seq})
    for a, b in zip(seq, seq[1:]):
        x1, x2 = x0 + a * cw + cw / 2, x0 + b * cw + cw / 2
        h = 14 + 8 * (b - a)
        s.path(f'M{x1:.0f} {y0 - 14} C{x1:.0f} {y0 - 14 - h} {x2:.0f} {y0 - 14 - h} {x2:.0f} {y0 - 15}', ACCENT, 2)
        s.add(f'<path d="M{x2 - 5:.0f} {y0 - 21} L{x2:.0f} {y0 - 14} L{x2 + 5:.0f} {y0 - 21}" fill="none" stroke="{ACCENT}" stroke-width="2"/>')
    t(s, (40 + cw * 8 + 30) / 2, 182, 'Each arrow: this element extends the subsequence ending at the earlier one. '
      'Answer 4: 2, 5, 7, 101', 11, '#374151')
    save(s, 'lis-chain.svg')


def lesson_dp_1d():
    house_robber_picture()
    best, used = coin_table_svg([1, 3, 4], 6, 'coin-change-table.svg',
                                'Coin change with coins 1, 3 and 4 for amounts 0 to 6: best is 0, 1, 2, 1, 1, 2, 2; '
                                'the last coin row says 6 came from a 3 and 3 came from a 3, so the answer is 3 + 3, '
                                'two coins', 'Fewest coins for each amount, coins {1, 3, 4}')
    assert best == [0, 1, 2, 1, 1, 2, 2] and sorted(used) == [3, 3]
    best, used = coin_table_svg([1, 6, 10], 12, 'coin-change-sketch.svg',
                                'Coin change with coins 1, 6 and 10 for amounts 0 to 12: best is 0, 1, 2, 3, 4, 5, 1, 2, '
                                '3, 4, 1, 2, 2; walking back from 12 by the last coin used gives 6 + 6, two coins',
                                'Fewest coins for each amount, coins {1, 6, 10}')
    assert best == [0, 1, 2, 3, 4, 5, 1, 2, 3, 4, 1, 2, 2] and used == [6, 6]
    assert greedy_coins([1, 6, 10], 12) == [10, 1, 1]
    lis_picture()


# =====================================================================
# 07-dynamic-programming/04 classic two-dimensional
# =====================================================================

def dp_grid_svg(rows, cols, T, path, name, title, head, corner='', note='', cw=36, mark=None):
    """A DP table with header row/column; `path` cells shaded yellow with orange outline, `mark` cells green."""
    mark = mark or set()
    n, m = len(T), len(T[0])
    x0, y0 = 70, 50
    W = x0 + (m + 0) * cw + 30
    H = y0 + (n + 1) * 30 + (36 if note else 14)
    s = Svg(max(W, 360), H, title)
    t(s, max(W, 360) / 2, 20, head, 13, None, 'bold')
    t(s, x0 - 22, y0 + 20, corner, 10, '#6b7280')
    for j, c in enumerate(cols):
        r(s, x0 + j * cw, y0, cw, 30, LIGHT, GREY)
        t(s, x0 + j * cw + cw / 2, y0 + 20, c, 12, None, 'bold')
    for i, rl in enumerate(rows):
        y = y0 + 30 + i * 30
        r(s, x0 - 44, y, 44, 30, LIGHT, GREY)
        t(s, x0 - 22, y + 20, rl, 12, None, 'bold')
        for j in range(m):
            f = GREEN_BG if (i, j) in mark else (YELLOW_BG if (i, j) in path else '#ffffff')
            r(s, x0 + j * cw, y, cw, 30, f, GREY)
            t(s, x0 + j * cw + cw / 2, y + 20, T[i][j], 12, None, 'bold' if (i, j) in path else None)
    for (i, j) in path:
        r(s, x0 + j * cw + 1.5, y0 + 30 + i * 30 + 1.5, cw - 3, 27, 'none', ORANGE, 2.5)
    if note:
        t(s, max(W, 360) / 2, H - 12, note, 11)
    save(s, name)


def lcs(a, b):
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            L[i][j] = L[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(L[i - 1][j], L[i][j - 1])
    out, i, j, path, diag = [], n, m, [(n, m)], set()
    while i > 0 and j > 0:                      # the lesson's reconstruction, >= tie-break
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1]); diag.add((i, j)); i -= 1; j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
        path.append((i, j))
    return L, ''.join(reversed(out)), path, diag


def lcs_picture(a, b, name, title, head, note):
    L, word, path, diag = lcs(a, b)
    dp_grid_svg(['–'] + list(a), ['–'] + list(b), L, set(path), name, title, head, note=note, mark=diag)
    return L, word, diag


def knapsack_picture():
    wts, vals, cap = [1, 3, 4, 5], [1, 4, 5, 7], 7
    K = [[0] * (cap + 1)]
    for i in range(len(wts)):
        prev = K[-1]
        K.append([max(prev[w], prev[w - wts[i]] + vals[i]) if w >= wts[i] else prev[w] for w in range(cap + 1)])
    assert K[-1] == [0, 1, 1, 4, 5, 7, 8, 9]
    path, taken, w = [], [], cap
    for i in range(len(wts), 0, -1):
        path.append((i, w))
        if K[i][w] != K[i - 1][w]:
            taken.append(i - 1)
            w -= wts[i - 1]
    path.append((0, w))
    assert sorted(taken) == [1, 2]
    rows = ['none'] + [f'+it{i}' for i in range(len(wts))]
    dp_grid_svg(rows, [f'w={w_}' for w_ in range(cap + 1)], K, set(path), 'knapsack-table.svg',
                'The 0/1 knapsack table for weights 1, 3, 4, 5, values 1, 4, 5, 7 and capacity 7: the bottom-right '
                'cell is 9; walking back up, the value changes when item 2 is added (take it, capacity 7 to 3) and '
                'when item 1 is added (take it, capacity 3 to 0), so items 1 and 2 are taken',
                'Weights [1, 3, 4, 5], values [1, 4, 5, 7], capacity 7', cw=42,
                note='Walk up from 9: a change from the row above means "taken". Items 1 and 2, value 4 + 5.')


def edit_distance_picture():
    a, b = 'kitten', 'sitting'
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = D[i - 1][j - 1] if a[i - 1] == b[j - 1] else 1 + min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])
    assert D[n][m] == 3 and D[6] == [6, 6, 5, 4, 3, 3, 2, 3]
    i, j, path, ops = n, m, [(n, m)], []
    while i > 0 or j > 0:
        if i and j and a[i - 1] == b[j - 1] and D[i][j] == D[i - 1][j - 1]:
            i, j = i - 1, j - 1
        elif i and j and D[i][j] == D[i - 1][j - 1] + 1:
            ops.append(f"replace '{a[i - 1]}' with '{b[j - 1]}'"); i, j = i - 1, j - 1
        elif i and D[i][j] == D[i - 1][j] + 1:
            ops.append(f"delete '{a[i - 1]}'"); i -= 1
        else:
            ops.append(f"insert '{b[j - 1]}'"); j -= 1
        path.append((i, j))
    ops.reverse()
    assert ops == ["replace 'k' with 's'", "replace 'e' with 'i'", "insert 'g'"]
    dp_grid_svg(['–'] + list(a), ['–'] + list(b), D, set(path), 'edit-distance-table.svg',
                'The edit distance table from kitten to sitting: the bottom-right cell is 3; the shaded path walks '
                'back through a replacement of k with s, free matches, a replacement of e with i, and an insert of g',
                'Edit distance: kitten → sitting', note='Diagonal = match or replace, left = insert, up = delete.')


def lesson_dp_2d():
    L, word, _ = lcs_picture('ABCBDAB', 'BDCABA', 'lcs-table.svg',
                             'The LCS table for ABCBDAB (rows) and BDCABA (columns): the bottom-right cell is 4; the '
                             'shaded traceback path goes back to the top-left, and its green diagonal steps are the '
                             'matched letters B, C, B, A',
                             'LCS of ABCBDAB and BDCABA', 'Yellow: the walk back. Green: a diagonal match. LCS = BCBA')
    assert L[7][6] == 4 and word == 'BCBA'
    assert L[1] == [0, 0, 0, 0, 1, 1, 1]
    knapsack_picture()
    edit_distance_picture()
    L, word, _ = lcs_picture('CABD', 'ABCD', 'lcs-sketch.svg',
                             'The LCS table for CABD (rows) and ABCD (columns): the bottom-right cell is 3; walking '
                             'back takes diagonal steps on D, B and A, so the LCS is ABD',
                             'LCS of CABD and ABCD', 'Yellow: the walk back. Green: a diagonal match. LCS = ABD')
    assert L[4][4] == 3 and word == 'ABD'


# =====================================================================
# 08 number theory basics
# =====================================================================

def alarms_picture():
    a, b = 12, 18
    lcm = a * b // math.gcd(a, b)
    assert lcm == 36
    s = Svg(540, 150, 'Two alarms on a timeline from 0 to 60 minutes: alarm A rings at 0, 12, 24, 36, 48, 60 and alarm '
            'B at 0, 18, 36, 54; the first time after 0 that both ring together is 36, the least common multiple')
    x0, w = 135, 380
    X = lambda v: x0 + v / 60 * w
    s.line(X(lcm), 108, X(lcm), 124, TRUE, 1.5, '4 3')
    t(s, X(lcm), 140, 'both ring at 36 = LCM(12, 18)', 12, TRUE, 'bold')
    for k, (lab, step, col) in enumerate((('Alarm A (12 min)', a, PIX), ('Alarm B (18 min)', b, ORANGE))):
        y = 50 + k * 50
        s.add(f'<text x="{x0 - 10}" y="{y + 4}" font-size="12" font-weight="bold" text-anchor="end">{lab}</text>')
        s.line(X(0), y, X(60), y, GREY, 1.2)
        for v in range(0, 61, step):
            s.circle(X(v), y, 7 if v == lcm else 5, TRUE if v == lcm else col)
            t(s, X(v), y - 11, v, 10, '#374151')
    save(s, 'lcm-alarms.svg')


def sieve_picture():
    n = 50
    spf = [0] * (n + 1)                        # which prime crossed each number out first (the lesson's sieve)
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    i = 2
    while i * i <= n:
        if is_p[i]:
            for k in range(i * i, n + 1, i):
                if is_p[k]:
                    spf[k] = i
                is_p[k] = False
        i += 1
    primes = [x for x in range(n + 1) if is_p[x]]
    assert len(primes) == 15 and primes[-1] == 47
    cols = {2: '#dbeafe', 3: '#fef3c7', 5: '#fce7f3', 7: '#ede9fe'}
    cw = 44
    s = Svg(40 + 10 * cw, 70 + 5 * cw + 40, 'The sieve of Eratosthenes on 1 to 50: multiples of 2, 3, 5 and 7 are '
            'crossed out, each coloured by the prime that crossed it out first; the 15 numbers left (2, 3, 5, 7, 11, '
            '13, 17, 19, 23, 29, 31, 37, 41, 43, 47) are the primes, in green')
    t(s, 20 + 5 * cw, 22, 'Cross out multiples of 2, 3, 5, 7 (7 × 7 = 49 ≤ 50, so stop there)', 12, None, 'bold')
    for v in range(1, n + 1):
        rr, cc = divmod(v - 1, 10)
        x, y = 20 + cc * cw, 40 + rr * cw
        f = GREEN_BG if is_p[v] else cols.get(spf[v], LIGHT)
        r(s, x, y, cw, cw, f, '#9ca3af')
        t(s, x + cw / 2, y + cw / 2 + 5, v, 14, ACCENT if is_p[v] else '#6b7280', 'bold' if is_p[v] else None)
    y = 40 + 5 * cw + 26
    x = 20
    for p_, c in cols.items():
        r(s, x, y - 12, 16, 16, c, '#9ca3af')
        s.add(f'<text x="{x + 22}" y="{y + 1}" font-size="11" text-anchor="start">crossed by {p_}</text>')
        x += 100
    r(s, x, y - 12, 16, 16, GREEN_BG, '#9ca3af')
    s.add(f'<text x="{x + 22}" y="{y + 1}" font-size="11" text-anchor="start">prime</text>')
    save(s, 'sieve-50.svg')


def euclid_picture(a=48, b=18):
    steps = []
    while b:
        steps.append((a, b, a // b, a % b))
        a, b = b, a % b
    assert [(x, y) for x, y, _, _ in steps] == [(48, 18), (18, 12), (12, 6)] and a == 6
    sc = 8
    s = Svg(560, 44 + 56 * len(steps) + 20, 'Euclid\'s algorithm for gcd(48, 18) drawn as bars: 48 holds two 18s with '
            '12 left over; 18 holds one 12 with 6 left over; 12 holds two 6s with nothing left over, so the gcd is 6')
    t(s, 280, 22, 'gcd(a, b) = gcd(b, a mod b): keep the leftover piece', 13, None, 'bold')
    for k, (x, y, q, rem) in enumerate(steps):
        yy = 44 + k * 56
        xx = 20
        for _ in range(q):
            r(s, xx, yy, y * sc, 24, BLUE_BG, INK)
            t(s, xx + y * sc / 2, yy + 17, y, 12)
            xx += y * sc
        if rem:
            r(s, xx, yy, rem * sc, 24, YELLOW_BG, ORANGE, 2)
            t(s, xx + rem * sc / 2, yy + 17, rem, 12, None, 'bold')
        s.add(f'<text x="{20 + x * sc + 14}" y="{yy + 17}" font-size="12" text-anchor="start">'
              f'{x} = {q} × {y} + {rem}</text>')
    t(s, 280, 44 + 56 * len(steps) + 4, f'The remainder hits 0, so the last divisor, {a}, is the gcd. '
      f'lcm = 48 × 18 / 6 = 144', 12, ACCENT, 'bold')
    save(s, 'euclid-48-18.svg')


def lesson_number_theory():
    alarms_picture()
    sieve_picture()
    euclid_picture()


# =====================================================================
# 09 leader algorithm
# =====================================================================

VOTES = list('ABAACABAA')


def votes_picture():
    n, a = len(VOTES), VOTES.count('A')
    assert a == 6 and a > n // 2
    cw = 44
    s = Svg(460, 130, 'Nine votes A, B, A, A, C, A, B, A, A: A appears 6 times out of 9, more than half (4.5), so A is '
            'the leader')
    fill = {i: GREEN_BG for i, v in enumerate(VOTES) if v == 'A'}
    cells(s, 32, 40, VOTES, cw, 34, fill=fill, size=15)
    t(s, 230, 100, 'A appears 6 times out of 9. Half of 9 is 4.5, and 6 > 4.5,', 12)
    t(s, 230, 118, 'so A is the leader (the majority element).', 12, ACCENT, 'bold')
    save(s, 'leader-votes.svg')


def boyer_moore_picture():
    cand, count, rows = None, 0, []
    for v in VOTES:
        if count == 0:
            cand, count, why = v, 1, 'adopt'
        elif v == cand:
            count, why = count + 1, '+1'
        else:
            count, why = count - 1, '−1'
        rows.append((v, cand, count, why))
    assert [c for _, _, c, _ in rows] == [1, 0, 1, 2, 1, 2, 1, 2, 3] and rows[-1][1] == 'A'
    cw = 46
    x0 = 100
    s = Svg(x0 + cw * 9 + 20, 250, 'Boyer-Moore voting on A, B, A, A, C, A, B, A, A: the count goes 1, 0, 1, 2, 1, 2, 1, '
            '2, 3; every different vote cancels one A, the count never stays at zero, and A survives as the candidate '
            'with count 3; a second pass confirms A appears 6 times out of 9')
    lab = lambda y, text: s.add(f'<text x="{x0 - 10}" y="{y}" font-size="12" font-weight="bold" text-anchor="end">{text}</text>')
    lab(52, 'vote')
    cells(s, x0, 30, VOTES, cw, 30, fill={i: GREEN_BG if v == 'A' else RED_BG for i, v in enumerate(VOTES)}, size=14)
    lab(84, 'what happens')
    base = 180
    lab(base - 40, 'count')
    for i, (v, c, cnt, why) in enumerate(rows):
        x = x0 + i * cw
        t(s, x + cw / 2, 84, why, 11, '#374151')
        h = cnt * 22
        r(s, x + 8, base - h, cw - 16, h, PIX2, PIX) if h else None
        t(s, x + cw / 2, base - h - 5, cnt, 12, None, 'bold')
    s.line(x0, base, x0 + cw * 9, base, INK, 1.2)
    lab(base + 20, 'candidate')
    for i, (v, c, cnt, why) in enumerate(rows):
        t(s, x0 + i * cw + cw / 2, base + 20, c, 13, ACCENT if c == 'A' else INK, 'bold')
    t(s, (x0 + cw * 9 + 20) / 2, 236, 'Candidate A survives with count 3. Then count it for real: 6 of 9 > 4.5, '
      'so A is the leader.', 11)
    save(s, 'boyer-moore-votes.svg')


def lesson_leader():
    votes_picture()
    boyer_moore_picture()


# =====================================================================
# 10 max slice algorithms
# =====================================================================

PNL = [-2, 3, 4, -1, 5, -8, 4, 1]


def best_slice(xs):
    best, lo, hi = -math.inf, 0, 0
    for p_ in range(len(xs)):
        for q in range(p_, len(xs)):
            if sum(xs[p_:q + 1]) > best:
                best, lo, hi = sum(xs[p_:q + 1]), p_, q
    return best, lo, hi


def pnl_picture():
    best, lo, hi = best_slice(PNL)
    assert (best, lo + 1, hi + 1) == (11, 2, 5)            # days are numbered from 1
    s = Svg(500, 260, 'Daily profit and loss for days 1 to 8: -2, +3, +4, -1, +5, -8, +4, +1 drawn as bars; the best '
            'window is days 2 to 5, shaded green, with sum 3 + 4 - 1 + 5 = 11')
    p = Plot(s, 60, 20, 400, 180, (0.4, 8.6), (-9, 7))
    s.rect(p.X(lo + 1 - 0.45), p.Y(7), p.X(hi + 1 + 0.45) - p.X(lo + 1 - 0.45), p.Y(-9) - p.Y(7), '#ecfdf5')
    s.line(p.X(0.4), p.Y(0), p.X(8.6), p.Y(0), INK, 1.2)
    for d, v in enumerate(PNL, 1):
        col = ACCENT if lo + 1 <= d <= hi + 1 else (TRUE if v < 0 else PIX2)
        y1, y2 = sorted((p.Y(0), p.Y(v)))
        r(s, p.X(d) - 16, y1, 32, y2 - y1, col)
        t(s, p.X(d), (p.Y(v) - 6) if v > 0 else (p.Y(v) + 15), f'{v:+d}', 11, None, 'bold')
        t(s, p.X(d), 222, f'day {d}', 10, '#6b7280')
    t(s, 250, 248, 'Best window: days 2 to 5, sum 3 + 4 − 1 + 5 = 11', 13, ACCENT, 'bold')
    save(s, 'max-slice-pnl.svg')


def kadane_picture():
    end, far, ends, fars = 0, 0, [], []
    for v in PNL:
        end = max(0, end + v)
        far = max(far, end)
        ends.append(end)
        fars.append(far)
    assert ends == [0, 3, 7, 6, 11, 3, 7, 8] and fars == [0, 3, 7, 7, 11, 11, 11, 11]
    s = Svg(500, 280, 'Kadane\'s algorithm on -2, 3, 4, -1, 5, -8, 4, 1: max_ending_here (blue) goes 0, 3, 7, 6, 11, 3, '
            '7, 8, dropping to 0 when the run turns negative; max_so_far (green) only ever rises and ends at 11')
    p = Plot(s, 60, 30, 400, 180, (0.5, 8.5), (0, 12))
    p.axes('', 'running sum', xticks=(), yticks=(0, 3, 6, 9, 12))
    for d, v in enumerate(PNL, 1):
        t(s, p.X(d), 228, f'{v:+d}', 12, TRUE if v < 0 else INK, 'bold')
    s.add(f'<text x="{p.X(0.5) - 6:.0f}" y="228" font-size="10" fill="#6b7280" text-anchor="end">value</text>')
    p.curve([(d, e) for d, e in enumerate(fars, 1)], ACCENT, 3)
    p.curve([(d, e) for d, e in enumerate(ends, 1)], PIX, 2.4, dash='6 4')
    for d, (e, f) in enumerate(zip(ends, fars), 1):
        p.dot(d, f, ACCENT, 4.5)
        p.dot(d, e, PIX, 4)
        t(s, p.X(d) + 10, p.Y(e) + 14, e, 10, PIX, 'bold')
    t(s, 250, 256, 'Dashed blue: best sum ending here (reset to 0 when it goes negative).', 11, PIX)
    t(s, 250, 272, 'Solid green: best sum seen so far. It finishes at 11.', 11, ACCENT)
    save(s, 'kadane-trace.svg')


def lesson_max_slice():
    pnl_picture()
    kadane_picture()


# =====================================================================
# 11 bit manipulation
# =====================================================================

def bit_row(s, x0, y, value, label, cw=34, hl=None, hl_col=ORANGE, nbits=8, weights=False, note=''):
    hl = hl or set()
    label = label.replace('&', '&amp;')
    s.add(f'<text x="{x0 - 10}" y="{y + 20}" font-size="12" font-weight="bold" text-anchor="end">{label}</text>')
    for k in range(nbits):
        bit = nbits - 1 - k
        on = (value >> bit) & 1
        r(s, x0 + k * cw, y, cw, 30, BLUE_BG if on else '#ffffff', INK)
        t(s, x0 + k * cw + cw / 2, y + 20, on, 14, INK if on else GREY, 'bold' if on else None)
        if bit in hl:
            r(s, x0 + k * cw + 1.5, y + 1.5, cw - 3, 27, 'none', hl_col, 3)
        if weights:
            t(s, x0 + k * cw + cw / 2, y - 18, f'bit {bit}', 9, '#6b7280')
            t(s, x0 + k * cw + cw / 2, y - 6, 2 ** bit, 10, '#374151')
    if note:
        s.add(f'<text x="{x0 + nbits * cw + 12}" y="{y + 20}" font-size="12" text-anchor="start">{note}</text>')


def bits_53_picture():
    v = 53
    assert format(v, '08b') == '00110101'
    s = Svg(470, 140, 'The number 53 as eight bits 0 0 1 1 0 1 0 1: bit 7 on the left is the most significant, bit 0 on '
            'the right the least; the bits that are on have weights 32, 16, 4 and 1, which add up to 53')
    bit_row(s, 70, 50, v, '53', weights=True)
    t(s, 70 + 4 * 34, 104, '32 + 16 + 4 + 1 = 53', 13, ACCENT, 'bold')
    t(s, 70 + 17, 124, '← bit 7: most significant', 10, '#6b7280')
    t(s, 70 + 8 * 34 - 40, 124, 'bit 0: least →', 10, '#6b7280')
    save(s, 'bits-53.svg')


def idioms_picture():
    x = 0b01010010
    ops = [('set bit 2:  x | (1 << 2)', 1 << 2, x | (1 << 2), 2, 'OR'),
           ('clear bit 4:  x & ~(1 << 4)', ~(1 << 4) & 0xFF, x & ~(1 << 4), 4, 'AND'),
           ('toggle bit 1:  x ^ (1 << 1)', 1 << 1, x ^ (1 << 1), 1, 'XOR')]
    assert ops[0][2] == 0b01010110 and ops[1][2] == 0b01000010 and ops[2][2] == 0b01010000
    s = Svg(470, 40 + 3 * 140, 'Three bit idioms on x = 01010010 (82): OR with the mask 00000100 sets bit 2, giving '
            '01010110; AND with the mask 11101111 clears bit 4, giving 01000010; XOR with the mask 00000010 flips bit 1, '
            'giving 01010000')
    for k, (title, mask, res, bit, op) in enumerate(ops):
        y = 30 + k * 140
        s.add(f'<text x="20" y="{y + 4}" font-size="13" font-weight="bold" text-anchor="start">{esc(title)}</text>')
        bit_row(s, 110, y + 14, x, 'x', hl={bit})
        bit_row(s, 110, y + 48, mask, f'{op} mask', hl={bit})
        bit_row(s, 110, y + 82, res, '=', hl={bit}, hl_col=ACCENT,
                note=f'{res} (was 82)')
    save(s, 'bit-idioms.svg')


def kernighan_picture():
    x, rows = 0b10110, []
    while x:
        rows.append((x, x - 1, x & (x - 1)))
        x &= x - 1
    assert len(rows) == 3 and bin(0b10110).count('1') == 3
    s = Svg(470, 56 + 3 * 132, 'Kernighan\'s loop on 22 = 00010110: each x & (x - 1) clears the lowest set bit, going '
            '00010110, 00010100, 00010000, 0; three set bits, three iterations')
    for k, (a, b, c) in enumerate(rows):
        y = 30 + k * 132
        low = (a & -a).bit_length() - 1
        s.add(f'<text x="20" y="{y + 2}" font-size="12" font-weight="bold" text-anchor="start">iteration {k + 1}: '
              f'clear bit {low}</text>')
        bit_row(s, 110, y + 10, a, 'x', hl={low})
        bit_row(s, 110, y + 44, b, 'x − 1', hl=set(range(low + 1)), hl_col=PIX)
        bit_row(s, 110, y + 78, c, 'x & (x−1)', hl={low}, hl_col=ACCENT, note=f'= {c}')
    t(s, 235, 56 + 3 * 132 - 10, '3 set bits, 3 iterations: the loop runs once per 1, not once per bit.', 12, ACCENT, 'bold')
    save(s, 'kernighan.svg')


def lesson_bits():
    bits_53_picture()
    idioms_picture()
    kernighan_picture()


# =====================================================================
# 12 math and geometry
# =====================================================================

def grid_cells(s, x0, y0, M, cw=40, fill=None, outline=None):
    fill, outline = fill or {}, outline or {}
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            r(s, x0 + j * cw, y0 + i * cw, cw, cw, fill.get((i, j), '#ffffff'), INK)
            t(s, x0 + j * cw + cw / 2, y0 + i * cw + cw / 2 + 5, v, 15)
    for (i, j), c in outline.items():
        r(s, x0 + j * cw + 1.5, y0 + i * cw + 1.5, cw - 3, cw - 3, 'none', c, 3)


def rotate_picture():
    M = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    T = [list(r_) for r_ in zip(*M)]
    R = [row[::-1] for row in T]
    assert R == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    s = Svg(540, 210, 'Rotating a 3 by 3 matrix 90 degrees clockwise in place: the original 1 2 3 / 4 5 6 / 7 8 9 is '
            'transposed across its main diagonal to 1 4 7 / 2 5 8 / 3 6 9, then each row is reversed to give '
            '7 4 1 / 8 5 2 / 9 6 3')
    mk = arrow_defs(s)
    diag = {(k, k): YELLOW_BG for k in range(3)}
    colfill = {(i, 0): GREEN_BG for i in range(3)}
    for k, (lab, mat, fill) in enumerate((('original', M, {**diag, **{(2, j): BLUE_BG for j in range(3)}}),
                                          ('1. transpose', T, {**diag, **{(i, 2): BLUE_BG for i in range(3)}}),
                                          ('2. reverse each row', R, {(i, 0): BLUE_BG for i in range(3)}))):
        x0 = 20 + k * 190
        t(s, x0 + 60, 30, lab, 13, None, 'bold')
        grid_cells(s, x0, 44, mat, fill=fill)
        if k < 2:
            arrow(s, mk, x0 + 128, 104, x0 + 182, 104, INK, 2)
    t(s, 270, 190, 'Yellow: the diagonal stays put. Blue: the old bottom row 7 8 9 ends up as the first column.', 11)
    save(s, 'matrix-rotate.svg')


def spiral(M):
    out, path = [], []
    top, bottom, left, right = 0, len(M) - 1, 0, len(M[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            path.append((top, c))
        top += 1
        for rr in range(top, bottom + 1):
            path.append((rr, right))
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                path.append((bottom, c))
            bottom -= 1
        if left <= right:
            for rr in range(bottom, top - 1, -1):
                path.append((rr, left))
            left += 1
    return [M[i][j] for i, j in path], path


def spiral_svg(M, name, title):
    order, path = spiral(M)
    cw = 52
    rows, cols = len(M), len(M[0])
    s = Svg(cols * cw + 40, rows * cw + 70, title)
    mk = arrow_defs(s)
    x0, y0 = 20, 20
    grid_cells(s, x0, y0, M, cw, fill={path[0]: GREEN_BG, path[-1]: YELLOW_BG})
    C = lambda p_: (x0 + p_[1] * cw + cw / 2, y0 + p_[0] * cw + cw / 2)
    for a, b in zip(path, path[1:]):
        (x1, y1), (x2, y2) = C(a), C(b)
        dx, dy = (x2 - x1) * 0.28, (y2 - y1) * 0.28
        arrow(s, mk, x1 + dx, y1 + dy - 0, x2 - dx, y2 - dy, ORANGE, 2.4)
    t(s, (cols * cw + 40) / 2, rows * cw + 46, ', '.join(map(str, order)), 12, None, 'bold')
    save(s, name)
    return order


def orientation_picture():
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    cases = [((0, 0), (1, 0), (0, 1), 'left turn: counter-clockwise', ACCENT),
             ((0, 0), (1, 0), (0, -1), 'right turn: clockwise', TRUE),
             ((0, 0), (1, 0), (2, 0), 'straight on: collinear', PIX)]
    assert [cross(o, a, b) for o, a, b, _, _ in cases] == [1, -1, 0]
    s = Svg(570, 230, 'The sign of the cross product of OA and OB for O = (0, 0) and A = (1, 0): with B = (0, 1) it is +1, '
            'a left (counter-clockwise) turn; with B = (0, -1) it is -1, a right (clockwise) turn; with B = (2, 0) it '
            'is 0, the three points are in a line')
    mk = arrow_defs(s)
    for k, (o, a, b, lab, col) in enumerate(cases):
        cx, cy, sc = 40 + k * 190, 112, 70
        P = lambda q: (cx + q[0] * sc, cy - q[1] * sc)
        s.line(cx - 30, cy, cx + 140, cy, '#eef2f6', 1)
        (ox, oy), (ax, ay), (bx, by) = P(o), P(a), P(b)
        arrow(s, mk, ox, oy, ax - 4, ay, INK, 2.4)
        arrow(s, mk, ox, oy, bx - (4 if b[1] == 0 else 0), by + (4 if b[1] > 0 else -4 if b[1] < 0 else 0), col, 2.4)
        for (px, py), nm in (((ox, oy), 'O'), ((ax, ay), 'A'), ((bx, by), 'B')):
            s.circle(px, py, 4, INK)
            t(s, px + (12 if nm == 'B' and b[1] else 0) - (10 if nm == 'O' else 0), py + (18 if nm == 'O' else -8), nm, 12, None, 'bold')
        c_ = cross(o, a, b)
        t(s, cx + 50, 200, f'cross = {c_:+d}' if c_ else 'cross = 0', 13, col, 'bold')
        t(s, cx + 50, 218, lab, 11, col)
    t(s, 285, 22, 'cross(O, A, B) = (A − O) × (B − O): the sign says which way B turns from OA', 12, None, 'bold')
    save(s, 'cross-orientation.svg')


def lesson_geometry():
    rotate_picture()
    order = spiral_svg([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 'spiral-3x3.svg',
                       'Spiral order of the 3 by 3 matrix 1 to 9: right along the top 1, 2, 3, down 6, 9, left 8, 7, '
                       'up 4, then right to 5; the order is 1, 2, 3, 6, 9, 8, 7, 4, 5')
    assert order == [1, 2, 3, 6, 9, 8, 7, 4, 5]
    assert spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])[0] == [1, 2, 3, 6, 9, 12, 11, 10, 7, 4, 5, 8]
    order = spiral_svg([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], 'spiral-sketch.svg',
                       'Spiral order of the 3 by 4 matrix 1 to 12: right 1, 2, 3, 4, down 8, 12, left 11, 10, 9, up 5, '
                       'then right 6, 7; the order is 1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7')
    assert order == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
    orientation_picture()


if __name__ == '__main__':
    lesson_growth()
    lesson_amortised()
    lesson_recursion_fundamentals()
    lesson_recursion_trees()
    lesson_master()
    lesson_binary_search()
    lesson_answer_search()
    lesson_state_space()
    lesson_divide_and_conquer()
    lesson_lower_bound()
    lesson_elementary()
    lesson_merge_sort()
    lesson_quicksort()
    lesson_non_comparison()
    lesson_when_greedy()
    lesson_scheduling()
    lesson_what_is_dp()
    lesson_tabulation()
    lesson_dp_1d()
    lesson_dp_2d()
    lesson_number_theory()
    lesson_leader()
    lesson_max_slice()
    lesson_bits()
    lesson_geometry()
