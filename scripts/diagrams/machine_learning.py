"""Draw the machine-learning lesson diagrams as small SVG files.

    python3 scripts/diagrams/machine_learning.py      # run from the vault root

The decision trees are grown here by running ID3 (entropy) and Gini on the same
tables the lessons use, then drawn with Graphviz (`dot`, which must be installed),
so a tree can never disagree with the worked numbers. The charts are computed
from the formulas in the lessons. Output: machine-learning/images/*.svg.
"""
import math
import os
import re
import subprocess
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, PIX, PIX2, TRUE, ACCENT, FONT, Svg, save_dot  # noqa: E402

BG_STROKE = '#ffffff'

OUT = os.path.join('machine-learning', 'images')
ORANGE = '#f59e0b'


# ---------- decision trees, grown with the lessons' own rules ----------

def entropy(rows, target):
    n = len(rows)
    return -sum(c / n * math.log2(c / n) for c in Counter(r[target] for r in rows).values())


def gini(rows, target):
    n = len(rows)
    return 1 - sum((c / n) ** 2 for c in Counter(r[target] for r in rows).values())


def split_score(rows, attr, target, measure):
    n = len(rows)
    return sum(len(part) / n * measure(part, target)
               for v in sorted({r[attr] for r in rows})
               for part in [[r for r in rows if r[attr] == v]])


def grow(rows, attrs, target, method):
    """ID3 picks the highest information gain; Gini picks the smallest Gini Index."""
    counts = Counter(r[target] for r in rows)
    if len(counts) == 1 or not attrs:
        return {'leaf': counts.most_common(1)[0][0], 'counts': counts}
    if method == 'entropy':
        best = max(attrs, key=lambda a: entropy(rows, target) - split_score(rows, a, target, entropy))
    else:
        best = min(attrs, key=lambda a: split_score(rows, a, target, gini))
    rest = [a for a in attrs if a != best]
    kids = {v: grow([r for r in rows if r[best] == v], rest, target, method)
            for v in sorted({r[best] for r in rows})}
    return {'attr': best, 'counts': counts, 'kids': kids}


def shape(t):
    if 'leaf' in t:
        return t['leaf']
    return {t['attr']: {v: shape(k) for v, k in t['kids'].items()}}


def tree_dot(tree, title, order=None, count_fmt=None):
    lines = [f'digraph {{ bgcolor="white"; pad=0.25; nodesep=0.35; ranksep=0.45;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", '
             f'color="{INK}", penwidth=1.3];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="{INK}"];']
    ids = iter(range(1000))

    def walk(t):
        i = next(ids)
        c = count_fmt(t['counts'])
        if 'leaf' in t:
            lines.append(f'n{i} [label="{t["leaf"]}\\n{c}", fillcolor="#d1fae5", fontcolor="#065f46"];')
        else:
            lines.append(f'n{i} [label="{t["attr"]}?\\n{c}", fillcolor="#dbeafe"];')
            values = order.get(t['attr'], sorted(t['kids'])) if order else sorted(t['kids'])
            for v in values:
                j = walk(t['kids'][v])
                lines.append(f'n{i} -> n{j} [label=" {v} "];')
        return i

    walk(tree)
    lines.append('}')
    return '\n'.join(lines)


def play_tennis_tree():
    cols = ['Outlook', 'Temp', 'Humidity', 'Wind', 'Play']
    data = """Sunny Hot High Weak No|Sunny Hot High Strong No|Overcast Hot High Weak Yes|Rain Mild High Weak Yes
Rain Cool Normal Weak Yes|Rain Cool Normal Strong No|Overcast Cool Normal Strong Yes|Sunny Mild High Weak No
Sunny Cool Normal Weak Yes|Rain Mild Normal Weak Yes|Sunny Mild Normal Strong Yes|Overcast Mild High Strong Yes
Overcast Hot Normal Weak Yes|Rain Mild High Strong No"""
    rows = [dict(zip(cols, r.split())) for r in data.replace('\n', '|').split('|')]
    assert len(rows) == 14
    t = grow(rows, cols[:-1], 'Play', 'entropy')
    assert shape(t) == {'Outlook': {'Overcast': 'Yes',
                                    'Rain': {'Wind': {'Strong': 'No', 'Weak': 'Yes'}},
                                    'Sunny': {'Humidity': {'High': 'No', 'Normal': 'Yes'}}}}
    fmt = lambda c: f'[{c.get("Yes", 0)}+, {c.get("No", 0)}−]'
    src = tree_dot(t, 'Play Tennis', order={'Outlook': ['Sunny', 'Overcast', 'Rain']}, count_fmt=fmt)
    save_dot(src, 'play-tennis-tree.svg', out=OUT, title=
             'The Play Tennis decision tree built by ID3: Outlook at the root; Sunny splits on Humidity, '
             'Overcast is always Yes, Rain splits on Wind')


def weekend_tree():
    cols = ['Weather', 'Parent', 'Money', 'Decision']
    data = """Sunny Yes Rich Cinema|Sunny No Rich Tennis|Windy Yes Rich Cinema|Rainy Yes Poor Cinema
Rainy No Rich StayIn|Rainy Yes Poor Cinema|Windy No Poor Cinema|Windy No Rich Shopping
Windy Yes Rich Cinema|Sunny No Rich Tennis"""
    rows = [dict(zip(cols, r.split())) for r in data.replace('\n', '|').split('|')]
    for r in rows:
        r['Decision'] = r['Decision'].replace('StayIn', 'Stay In')
    t = grow(rows, cols[:-1], 'Decision', 'gini')
    assert shape(t) == {'Parent': {'No': {'Weather': {'Rainy': 'Stay In', 'Sunny': 'Tennis',
                                                      'Windy': {'Money': {'Poor': 'Cinema', 'Rich': 'Shopping'}}}},
                                   'Yes': 'Cinema'}}
    fmt = lambda c: f'({sum(c.values())} weekend{"s" if sum(c.values()) > 1 else ""})'
    src = tree_dot(t, 'Weekend', order={'Parent': ['Yes', 'No'], 'Weather': ['Sunny', 'Rainy', 'Windy'],
                                        'Money': ['Rich', 'Poor']}, count_fmt=fmt)
    save_dot(src, 'weekend-gini-tree.svg', out=OUT, title=
             'The Weekend decision tree built with the Gini Index: Parent at the root; Parent Yes gives Cinema; '
             'Parent No splits on Weather, and Windy splits on Money')


def bayes_net(name, title, edges, layout):
    lines = ['digraph { bgcolor="white"; pad=0.25; rankdir=TB; nodesep=0.6; ranksep=0.55;',
             f'node [fontname="{FONT}", fontsize=13, shape=ellipse, style=filled, fillcolor="#dbeafe", '
             f'color="{INK}", penwidth=1.3];',
             f'edge [color="{INK}", penwidth=1.3];']
    lines += [f'{{rank=same; {" ".join(chr(34) + n + chr(34) for n in rank)}}}' for rank in layout]
    lines += [f'"{a}" -> "{b}";' for a, b in edges]
    lines.append('}')
    save_dot('\n'.join(lines), name, title, OUT)


# ---------- charts ----------

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


def overfitting_curves():
    xs = [i / 10 for i in range(0, 101)]
    train = [(x, 0.15 + 0.85 * math.exp(-x / 2.2)) for x in xs]
    val = [(x, 0.22 + 0.85 * math.exp(-x / 1.8) + 0.006 * x * x) for x in xs]   # illustrative shape
    best = min(val, key=lambda p: p[1])
    s = Svg(500, 330, 'Training loss keeps falling while validation loss bottoms out and then rises; '
                      'overfitting starts at the bottom of the validation curve')
    p = Plot(s, 70, 30, 390, 230, (0, 10), (0, 1.1))
    p.axes('training progress (epochs)', 'loss', xticks=(0, 2, 4, 6, 8, 10), yticks=(0, 0.5, 1))
    p.curve(train, PIX)
    p.curve(val, ORANGE)
    s.line(p.X(best[0]), p.Y(0), p.X(best[0]), p.Y(1.05), TRUE, 1.3, '5 4')
    s.text(p.X(best[0]) + 6, p.Y(1.0), 'overfitting starts here', 11, TRUE, 'start', 'bold')
    s.text(p.X(9.6), p.Y(train[-1][1]) + 18, 'training', 12, PIX, 'end', 'bold')
    s.text(p.X(9.6), p.Y(val[-1][1]) - 10, 'validation', 12, ORANGE, 'end', 'bold')
    s.save('overfitting-loss-curves.svg', OUT)


def gradient_descent_steps():
    L = lambda w: (w - 3) ** 2

    def run(w, lr, n):
        out = [w]
        for _ in range(n):
            w = w - lr * 2 * (w - 3)
            out.append(w)
        return out

    good, bad = run(0, 0.25, 5), run(0, 0.95, 5)
    assert good[:3] == [0, 1.5, 2.25]
    s = Svg(560, 300, 'Gradient descent on L = (w - 3) squared from w = 0: learning rate 0.25 walks steadily '
                      'down to the minimum; learning rate 0.95 overshoots and bounces from side to side')
    for k, (ws, lr, col) in enumerate(((good, 0.25, PIX), (bad, 0.95, ORANGE))):
        p = Plot(s, 55 + k * 270, 35, 210, 190, (-0.5, 6.5), (0, 10))
        p.axes('w', 'loss', xticks=(0, 3, 6), yticks=(0, 5, 10))
        lo, hi = 3 - math.sqrt(10), 3 + math.sqrt(10)          # keep the parabola inside the plot
        p.curve([(lo + (hi - lo) * i / 120, L(lo + (hi - lo) * i / 120)) for i in range(121)], INK, 1.5)
        pts = [(w, L(w)) for w in ws]
        p.curve(pts, col, 1.5, dash='4 3')
        for w, y in pts:
            p.dot(w, y, col)
        s.text(p.x0 + p.w / 2, 20, f'learning rate {lr}', 13, col, weight='bold')
    s.text(280, 292, 'Each dot is one step. Left: steady progress to w = 3. Right: steps too big, so it bounces.', 11)
    s.save('gradient-descent-steps.svg', OUT)


def sigmoid_curve():
    sig = lambda z: 1 / (1 + math.exp(-z))
    assert abs(sig(0.8) - 0.690) < 1e-3
    s = Svg(480, 300, 'The sigmoid squeezes any score z into a probability between 0 and 1; '
                      'z = 0 gives 0.5, the decision boundary, and z = 0.8 gives 0.69, class 1')
    p = Plot(s, 70, 25, 370, 210, (-6, 6), (0, 1))
    p.axes('score z', 'σ(z), probability of class 1', xticks=(-6, -4, -2, 0, 2, 4, 6), yticks=(0, 0.5, 1))
    s.line(p.X(-6), p.Y(0.5), p.X(6), p.Y(0.5), TRUE, 1.2, '5 4')
    s.text(p.X(-5.8), p.Y(0.5) - 6, 'threshold 0.5', 11, TRUE, 'start')
    p.curve([(z / 10, sig(z / 10)) for z in range(-60, 61)], PIX)
    p.dot(0.8, sig(0.8), ACCENT, 5.5)
    s.text(p.X(0.8) + 10, p.Y(sig(0.8)) + 16, 'z = 0.8 → 0.69: class 1', 11, ACCENT, 'start', 'bold')
    s.text(p.X(-3), p.Y(0.2), 'class 0', 12, INK, 'middle', 'bold')
    s.text(p.X(3), p.Y(0.85), 'class 1', 12, INK, 'middle', 'bold')
    s.save('sigmoid.svg', OUT)


def kmeans(points, k, iters=50):
    cs = points[:k]                                       # deterministic start
    for _ in range(iters):
        groups = [[] for _ in cs]
        for p in points:
            groups[min(range(len(cs)), key=lambda i: (p[0] - cs[i][0]) ** 2 + (p[1] - cs[i][1]) ** 2)].append(p)
        cs = [(sum(x for x, _ in g) / len(g), sum(y for _, y in g) / len(g)) if g else c for g, c in zip(groups, cs)]
    return sum(min((p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 for c in cs) for p in points)


def elbow_plot():
    import random
    rnd = random.Random(7)
    centres = [(2, 2), (8, 3), (5, 8)]
    pts = [(cx + rnd.gauss(0, 0.8), cy + rnd.gauss(0, 0.8)) for cx, cy in centres for _ in range(30)]
    rnd.shuffle(pts)
    best = []
    for k in range(1, 9):                                  # best of a few starts, like n_init
        tries = [kmeans(pts[i:] + pts[:i], k) for i in range(0, 50, 5)]
        best.append((k, min(tries)))
    drops = [best[i][1] - best[i + 1][1] for i in range(len(best) - 1)]
    assert drops[1] > 3 * drops[2]                         # the elbow really is at k = 3
    s = Svg(480, 300, 'Elbow plot: WCSS falls steeply from k = 1 to k = 3, then flattens; '
                      'the elbow at k = 3 matches the three groups in the data')
    top = math.ceil(best[0][1] / 200) * 200
    p = Plot(s, 80, 25, 360, 210, (1, 8), (0, top))
    p.axes('number of clusters k', 'WCSS (inertia_)', xticks=range(1, 9), yticks=(0, top // 2, top))
    p.curve(best, PIX)
    for k, w in best:
        p.dot(k, w, PIX)
    p.dot(3, best[2][1], TRUE, 7)
    s.text(p.X(3) + 12, p.Y(best[2][1]) - 12, 'elbow: k = 3', 12, TRUE, 'start', 'bold')
    s.save('elbow-plot.svg', OUT)


def knn_picture():
    a = [(1.0, 1.2), (1.6, 2.4), (2.4, 1.4), (1.2, 3.0), (2.8, 2.6), (0.8, 2.0)]
    b = [(4.6, 3.8), (5.2, 2.6), (4.0, 4.6), (5.6, 4.2), (3.6, 3.2), (4.4, 2.2)]
    q = (3.3, 2.6)
    labelled = [(p, 'A') for p in a] + [(p, 'B') for p in b]
    near = sorted(labelled, key=lambda t: math.dist(t[0], q))[:3]
    votes = Counter(c for _, c in near)
    assert votes['B'] == 2 and votes['A'] == 1
    r = math.dist(near[-1][0], q)
    s = Svg(440, 330, 'KNN with K = 3: the new point is grey; its three nearest neighbours are circled, '
                      'two blue B and one orange A, so the majority vote predicts B')
    p = Plot(s, 50, 20, 360, 260, (0, 6.2), (0, 5.2))
    s.add(f'<circle cx="{p.X(q[0]):.1f}" cy="{p.Y(q[1]):.1f}" r="{r / 6.2 * 360:.1f}" fill="#f8fafc" '
          f'stroke="{INK}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    for (x, y), c in labelled:
        p.dot(x, y, ORANGE if c == 'A' else PIX, 6)
    for (x, y), _ in near:
        s.line(p.X(q[0]), p.Y(q[1]), p.X(x), p.Y(y), INK, 1, '3 3')
        s.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="10" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    p.dot(q[0], q[1], '#6b7280', 7)
    s.text(p.X(q[0]) + 4, p.Y(q[1]) + 24, 'new point', 11, INK, 'middle', 'bold')
    s.text(p.X(1.4), p.Y(4.6), 'class A', 13, ORANGE, 'middle', 'bold')
    s.text(p.X(5.2), p.Y(1.2), 'class B', 13, PIX, 'middle', 'bold')
    s.text(220, 316, 'K = 3: the 3 nearest are 2 B and 1 A, so the vote says B.', 12)
    s.save('knn-k3-vote.svg', OUT)


def commute_tree():
    """A small new dataset for a sketch question: the learner grows this tree by hand."""
    cols = ['Distance', 'Raining', 'Transport']
    data = ['Near No Walk'] * 3 + ['Near Yes Bus'] + ['Far No Bus'] * 2 + ['Far Yes Bus'] * 2
    rows = [dict(zip(cols, r.split())) for r in data]
    t = grow(rows, cols[:-1], 'Transport', 'entropy')
    assert shape(t) == {'Distance': {'Far': 'Bus', 'Near': {'Raining': {'No': 'Walk', 'Yes': 'Bus'}}}}
    ig = lambda a: entropy(rows, 'Transport') - split_score(rows, a, 'Transport', entropy)
    assert abs(ig('Distance') - 0.549) < 1e-3 and abs(ig('Raining') - 0.348) < 1e-3
    fmt = lambda c: f'[{c.get("Walk", 0)} Walk, {c.get("Bus", 0)} Bus]'
    src = tree_dot(t, 'Commute', order={'Distance': ['Near', 'Far'], 'Raining': ['No', 'Yes']}, count_fmt=fmt)
    save_dot(src, 'commute-tree.svg', out=OUT, title=
             'Decision tree grown by ID3 on the commute data: Distance at the root; Far is always Bus; '
             'Near splits on Raining, where No gives Walk and Yes gives Bus')


def elbow_from_numbers():
    wcss = [(1, 500), (2, 240), (3, 90), (4, 75), (5, 65), (6, 60)]
    s = Svg(480, 300, 'Elbow plot of the given WCSS values 500, 240, 90, 75, 65, 60 for k = 1 to 6; '
                      'the curve bends sharply at k = 3, the elbow')
    p = Plot(s, 80, 25, 360, 210, (1, 6), (0, 500))
    p.axes('number of clusters k', 'WCSS', xticks=range(1, 7), yticks=(0, 250, 500))
    p.curve(wcss, PIX)
    for k, w in wcss:
        p.dot(k, w, PIX)
    p.dot(3, 90, TRUE, 7)
    s.text(p.X(3) + 12, p.Y(90) - 12, 'elbow: k = 3', 12, TRUE, 'start', 'bold')
    s.save('elbow-from-numbers.svg', OUT)


# ---------- more diagrams: one per idea the notes describe in words ----------

def arrow_defs(s, colors=(INK, PIX, TRUE, ORANGE, ACCENT)):
    s.add('<defs>' + ''.join(
        f'<marker id="a{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for i, c in enumerate(colors))
        + '</defs>')
    return {c: f'url(#a{i})' for i, c in enumerate(colors)}


def vec(s, p, a, b, color, mk, width=2.4):
    s.add(f'<line x1="{p.X(a[0]):.1f}" y1="{p.Y(a[1]):.1f}" x2="{p.X(b[0]):.1f}" y2="{p.Y(b[1]):.1f}" '
          f'stroke="{color}" stroke-width="{width}" marker-end="{mk[color]}"/>')


def derivative_tangents():
    f = lambda x: x * x
    s = Svg(470, 330, 'The parabola f(x) = x squared with tangent lines: slope 0 at x = 0 (the minimum), '
                      'slope 2 at x = 1 and slope 6 at x = 3')
    p = Plot(s, 60, 20, 380, 250, (-3.5, 4), (0, 12))
    p.axes('x', 'f(x) = x²', xticks=(-3, -2, -1, 0, 1, 2, 3, 4), yticks=(0, 4, 8, 12))
    p.curve([(x / 20, f(x / 20)) for x in range(-70, 71)], INK)
    for x0, col in ((0, ACCENT), (1, ORANGE), (3, TRUE)):
        m = 2 * x0
        xs = (x0 - 0.9, x0 + 0.9) if x0 != 3 else (x0 - 0.75, x0 + 0.3)
        p.curve([(x, f(x0) + m * (x - x0)) for x in xs], col, 2.2)
        p.dot(x0, f(x0), col, 5)
        dx, dy, anc = {0: (-12, -10, 'end'), 1: (10, 14, 'start'), 3: (10, 4, 'start')}[x0]
        s.text(p.X(x0) + dx, p.Y(f(x0)) + dy, f"f'({x0}) = {m}", 12, col, anc, 'bold')
    s.text(250, 322, 'The steeper the tangent, the bigger the derivative. At the minimum it is flat: 0.', 11)
    s.save('derivative-tangents.svg', OUT)


def normal_distribution():
    pdf = lambda x: math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
    s = Svg(470, 300, 'The normal (bell) curve: outcomes cluster around the mean; about 68 percent fall within one '
                      'standard deviation of it')
    p = Plot(s, 55, 20, 390, 220, (-4, 4), (0, 0.45))
    p.axes('value (in standard deviations from the mean)', 'how likely', xticks=(-3, -2, -1, 0, 1, 2, 3), yticks=())
    band = [(x / 50, pdf(x / 50)) for x in range(-50, 51)]
    d = 'M ' + f'{p.X(-1):.1f} {p.Y(0):.1f} ' + ' '.join(f'L {p.X(x):.1f} {p.Y(y):.1f}' for x, y in band) + f' L {p.X(1):.1f} {p.Y(0):.1f} Z'
    s.add(f'<path d="{d}" fill="#dbeafe" stroke="none"/>')
    p.curve([(x / 25, pdf(x / 25)) for x in range(-100, 101)], PIX, 2.5)
    s.line(p.X(0), p.Y(0.2), p.X(0), p.Y(pdf(0)), TRUE, 1.5, '5 4')
    s.text(p.X(0), p.Y(pdf(0)) - 6, 'mean', 12, TRUE, weight='bold')
    s.text(p.X(0), p.Y(0.12), '≈ 68%', 13, PIX, weight='bold')
    s.text(p.X(0), p.Y(0.08), 'within ±1 sd', 10, PIX)
    s.save('normal-distribution.svg', OUT)


def sklearn_style_tree():
    lines = ['digraph { bgcolor="white"; pad=0.25; nodesep=0.3; ranksep=0.4;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.3, fillcolor="#dbeafe"];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}"];',
             'a [label="age < 30?"]; b [label="income < 40k?"]; c [label="owns home?"];',
             'd [label="…", fillcolor="#d1fae5"]; e [label="…", fillcolor="#d1fae5"]; f [label="…", fillcolor="#d1fae5"]; g [label="…", fillcolor="#d1fae5"];',
             'a -> b [label=" yes "]; a -> c [label=" no "]; b -> d [label=" yes "]; b -> e [label=" no "]; c -> f [label=" yes "]; c -> g [label=" no "];',
             '}']
    save_dot('\n'.join(lines), 'yes-no-tree.svg', 'A decision tree of yes or no questions: age under 30 leads to an '
             'income question, otherwise a home-ownership question, each splitting further', OUT)


def vectors_picture():
    a, b = (1, 2), (3, 1)
    s = Svg(440, 330, 'Vectors as arrows from the origin: a = [1, 2] and b = [3, 1]; adding them tip to tail gives '
                      'a + b = [4, 3]')
    mk = arrow_defs(s)
    p = Plot(s, 50, 20, 360, 260, (0, 5), (0, 3.6))
    p.axes('x', 'y', xticks=range(6), yticks=range(4))
    vec(s, p, (0, 0), a, PIX, mk)
    vec(s, p, (0, 0), b, ORANGE, mk)
    vec(s, p, a, (4, 3), ORANGE, mk, 1.4)
    vec(s, p, (0, 0), (4, 3), ACCENT, mk)
    s.text(p.X(0.4), p.Y(1.3), 'a = [1, 2]', 12, PIX, 'end', 'bold')
    s.text(p.X(2.2), p.Y(0.45), 'b = [3, 1]', 12, ORANGE, 'start', 'bold')
    s.text(p.X(4.05), p.Y(3.05), 'a + b = [4, 3]', 12, ACCENT, 'start', 'bold')
    s.text(220, 322, 'Each vector is a point and an arrow. Adding is element-wise: walk a, then walk b.', 11)
    s.save('vectors-addition.svg', OUT)


def dot_product_cases():
    cases = [('aligned', (2, 1), (2, 1.6)), ('perpendicular', (2, 1), (-1, 2)), ('opposite', (2, 1), (-2, -1.2))]
    s = Svg(570, 240, 'Three pairs of vectors: pointing the same way gives a large positive dot product, at right '
                      'angles gives zero, and pointing opposite ways gives a negative dot product')
    mk = arrow_defs(s)
    for k, (name, a, b) in enumerate(cases):
        d = a[0] * b[0] + a[1] * b[1]
        p = Plot(s, 25 + k * 185, 30, 160, 160, (-2.5, 2.5), (-2.5, 2.5))
        s.line(p.X(-2.5), p.Y(0), p.X(2.5), p.Y(0), '#d1d5db', 1)
        s.line(p.X(0), p.Y(-2.5), p.X(0), p.Y(2.5), '#d1d5db', 1)
        vec(s, p, (0, 0), a, PIX, mk)
        vec(s, p, (0, 0), b, ORANGE, mk)
        s.text(p.X(0), 22, name, 13, weight='bold')
        s.text(p.X(0), 215, f'a · b = {d:g}', 13, ACCENT if d > 0 else (INK if d == 0 else TRUE), weight='bold')
    s.save('dot-product-cases.svg', OUT)


def matrix_transform():
    W = ((1, 0), (0, -1))
    x = (2, 3)
    wx = (W[0][0] * x[0] + W[0][1] * x[1], W[1][0] * x[0] + W[1][1] * x[1])
    assert wx == (2, -3)
    s = Svg(400, 330, 'The matrix W = [[1, 0], [0, -1]] maps the vector x = [2, 3] to W x = [2, -3]: it flips the '
                      'y component, a reflection in the x-axis')
    mk = arrow_defs(s)
    p = Plot(s, 50, 20, 300, 270, (-1, 4), (-3.5, 3.5))
    p.axes('', '', xticks=range(-1, 5), yticks=range(-3, 4))
    s.line(p.X(-1), p.Y(0), p.X(4), p.Y(0), INK, 1.2)
    vec(s, p, (0, 0), x, PIX, mk)
    vec(s, p, (0, 0), wx, ORANGE, mk)
    s.line(p.X(2), p.Y(3), p.X(2), p.Y(-3), '#9ca3af', 1, '4 4')
    s.text(p.X(2.1), p.Y(3), 'x = [2, 3]', 12, PIX, 'start', 'bold')
    s.text(p.X(2.1), p.Y(-3) + 4, 'W x = [2, −3]', 12, ORANGE, 'start', 'bold')
    s.text(200, 322, 'W = [[1, 0], [0, −1]] keeps x and flips the sign of y.', 11)
    s.save('matrix-as-transform.svg', OUT)


def euclid_vs_manhattan():
    P, Q = (1, 2), (4, 6)
    assert math.dist(P, Q) == 5 and abs(Q[0] - P[0]) + abs(Q[1] - P[1]) == 7
    s = Svg(400, 330, 'From (1, 2) to (4, 6): the straight Euclidean distance is 5; the Manhattan distance along '
                      'the grid, 3 across plus 4 up, is 7')
    p = Plot(s, 50, 20, 300, 260, (0, 5), (0, 7))
    p.axes('x', 'y', xticks=range(6), yticks=range(8))
    p.curve([P, (4, 2), Q], ORANGE, 3)
    p.curve([P, Q], PIX, 3)
    p.dot(*P, INK, 5)
    p.dot(*Q, INK, 5)
    s.text(p.X(1) - 8, p.Y(2) + 4, 'p (1, 2)', 12, INK, 'end', 'bold')
    s.text(p.X(4) + 8, p.Y(6) + 4, 'q (4, 6)', 12, INK, 'start', 'bold')
    s.text(p.X(2.2), p.Y(4.4), 'Euclidean = 5', 12, PIX, 'end', 'bold')
    s.text(p.X(4.1), p.Y(3.6), 'Manhattan', 12, ORANGE, 'start', 'bold')
    s.text(p.X(4.1), p.Y(3.15), '= 3 + 4 = 7', 12, ORANGE, 'start', 'bold')
    s.save('euclidean-vs-manhattan.svg', OUT)


def split_bar():
    s = Svg(520, 150, 'A dataset split into 70 percent training, 15 percent validation and 15 percent test')
    parts = [('training 70%', 0.70, PIX, 'learn the parameters'), ('val 15%', 0.15, ORANGE, 'tune'),
             ('test 15%', 0.15, ACCENT, 'score once')]
    x = 20
    for name, f, col, sub in parts:
        w = 480 * f
        s.rect(x, 40, w, 46, col, BG_STROKE, 2)
        s.text(x + w / 2, 68, name, 13, '#ffffff', weight='bold')
        s.text(x + w / 2, 108, sub, 11)
        x += w
    s.text(260, 28, 'Shuffle, then split. Never tune on the test set.', 12, weight='bold')
    s.save('train-val-test-split.svg', OUT)


def fit_curves():
    import random
    rnd = random.Random(3)
    truth = lambda x: math.sin(1.3 * x) + 0.3 * x
    xs = [0.3 + 0.62 * i for i in range(10)]
    data = [(x, truth(x) + rnd.gauss(0, 0.25)) for x in xs]

    def lsq_poly(points, deg):
        n = deg + 1
        A = [[sum(x ** (i + j) for x, _ in points) for j in range(n)] for i in range(n)]
        bvec = [sum(y * x ** i for x, y in points) for i in range(n)]
        for c in range(n):                               # Gaussian elimination with partial pivoting
            piv = max(range(c, n), key=lambda r: abs(A[r][c]))
            A[c], A[piv], bvec[c], bvec[piv] = A[piv], A[c], bvec[piv], bvec[c]
            for r in range(c + 1, n):
                f = A[r][c] / A[c][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
                bvec[r] -= f * bvec[c]
        coef = [0] * n
        for r in range(n - 1, -1, -1):
            coef[r] = (bvec[r] - sum(A[r][k] * coef[k] for k in range(r + 1, n))) / A[r][r]
        return lambda x: sum(c * x ** i for i, c in enumerate(coef))

    def lagrange(points):
        return lambda x: sum(y * math.prod((x - xj) / (xi - xj) for j, (xj, _) in enumerate(points) if j != i)
                             for i, (xi, y) in enumerate(points))

    fits = [('Under-fitting (high bias)', lsq_poly(data, 1)), ('Good fit', lsq_poly(data, 3)),
            ('Over-fitting (high variance)', lagrange(data))]
    s = Svg(600, 240, 'The same ten noisy points fitted three ways: a straight line misses the pattern '
                      '(under-fitting), a gentle curve follows it, and a curve through every point chases the noise '
                      '(over-fitting)')
    for k, (name, f) in enumerate(fits):
        p = Plot(s, 25 + k * 195, 35, 170, 160, (0, 6.2), (-1.8, 3.6))
        s.rect(p.x0, p.y0, p.w, p.h, '#f8fafc', '#e5e7eb', 1)
        pts = [(x / 40, max(-1.8, min(3.6, f(x / 40)))) for x in range(8, 245)]
        p.curve(pts, [ORANGE, ACCENT, TRUE][k], 2.4)
        for x, y in data:
            p.dot(x, y, PIX, 3.8)
        s.text(p.x0 + p.w / 2, 25, name, 12, weight='bold')
    s.text(300, 228, 'Blue dots: training data. The over-fit curve hits every point but would predict new points badly.', 11)
    s.save('under-good-over-fit.svg', OUT)


def least_squares():
    pts = [(1, 1.5), (2, 2.1), (3, 3.6), (4, 3.4), (5, 5.2), (6, 5.4)]
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    w1 = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
    w0 = my - w1 * mx
    s = Svg(440, 320, f'Linear regression by least squares: the line y = {w0:.2f} + {w1:.2f}x makes the sum of the '
                      f'squared vertical gaps (residuals) as small as possible')
    p = Plot(s, 60, 20, 350, 240, (0, 7), (0, 6.5))
    p.axes('x', 'y', xticks=range(8), yticks=range(7))
    p.curve([(0.3, w0 + w1 * 0.3), (6.7, w0 + w1 * 6.7)], TRUE, 2.4)
    for x, y in pts:
        s.line(p.X(x), p.Y(y), p.X(x), p.Y(w0 + w1 * x), ORANGE, 2.6)
        p.dot(x, y, PIX, 5)
    s.text(p.X(0.4), p.Y(6), f'ŷ = {w0:.2f} + {w1:.2f}x', 13, TRUE, 'start', 'bold')
    s.text(220, 312, 'Orange: residuals. Least squares picks the line that minimises the sum of their squares.', 11)
    s.save('least-squares-line.svg', OUT)


def kmeans_clusters():
    import random
    rnd = random.Random(7)
    centres = [(2, 2), (8, 3), (5, 8)]
    pts = [(cx + rnd.gauss(0, 0.8), cy + rnd.gauss(0, 0.8)) for cx, cy in centres for _ in range(30)]
    cs = [(1, 1), (9, 1), (5, 9)]
    for _ in range(20):
        groups = [[] for _ in cs]
        for q in pts:
            groups[min(range(3), key=lambda i: math.dist(q, cs[i]))].append(q)
        cs = [(sum(x for x, _ in g) / len(g), sum(y for _, y in g) / len(g)) for g in groups]
    s = Svg(420, 400, 'K-Means with k = 3 groups 90 unlabelled points into three clusters; each cross is a '
                      'centroid, the mean of its cluster')
    p = Plot(s, 50, 20, 340, 320, (-0.5, 10.5), (-0.5, 10.5))
    p.axes('feature 1', 'feature 2', xticks=(0, 2, 4, 6, 8, 10), yticks=(0, 2, 4, 6, 8, 10))
    cols = [PIX, ORANGE, ACCENT]
    for g, col in zip(groups, cols):
        for x, y in g:
            p.dot(x, y, col, 3.6)
    for (x, y), col in zip(cs, cols):
        X, Y = p.X(x), p.Y(y)
        s.line(X - 8, Y - 8, X + 8, Y + 8, INK, 3)
        s.line(X - 8, Y + 8, X + 8, Y - 8, INK, 3)
    s.text(210, 392, 'Colours: the cluster each point is assigned to. Crosses: the centroids.', 11)
    s.save('kmeans-clusters.svg', OUT)


def pca_directions():
    import random
    rnd = random.Random(11)
    pts = []
    for _ in range(70):
        t, e = rnd.gauss(0, 1.6), rnd.gauss(0, 0.45)
        pts.append((5 + t * 0.866 - e * 0.5, 4 + t * 0.5 + e * 0.866))
    n = len(pts)
    mx, my = sum(x for x, _ in pts) / n, sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts) / n
    syy = sum((y - my) ** 2 for _, y in pts) / n
    sxy = sum((x - mx) * (y - my) for x, y in pts) / n
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    l1 = tr / 2 + math.sqrt(tr * tr / 4 - det)
    l2 = tr - l1
    v1 = (sxy, l1 - sxx)
    nv = math.hypot(*v1)
    v1 = (v1[0] / nv, v1[1] / nv)
    v2 = (-v1[1], v1[0])
    s = Svg(420, 360, 'PCA on a cloud of points: the first principal component points along the direction of '
                      'greatest spread, and the second is at right angles to it with much less spread')
    mk = arrow_defs(s)
    p = Plot(s, 50, 20, 340, 280, (0, 10), (0, 8.2))
    p.axes('feature 1', 'feature 2', xticks=range(0, 11, 2), yticks=range(0, 9, 2))
    for x, y in pts:
        p.dot(x, y, '#93c5fd', 3.4)
    a1, a2 = 2 * math.sqrt(l1), 2 * math.sqrt(l2)
    vec(s, p, (mx, my), (mx + a1 * v1[0], my + a1 * v1[1]), TRUE, mk, 3)
    vec(s, p, (mx, my), (mx + a2 * v2[0], my + a2 * v2[1]), ORANGE, mk, 3)
    s.text(p.X(mx + a1 * v1[0]) + 6, p.Y(my + a1 * v1[1]) - 6, 'PC 1', 12, TRUE, 'start', 'bold')
    s.text(p.X(mx + a2 * v2[0]) - 10, p.Y(my + a2 * v2[1]) - 14, 'PC 2', 12, ORANGE, 'end', 'bold')
    share = l1 / (l1 + l2)
    s.text(210, 352, f'PC 1 keeps {share:.0%} of the variation. Keeping only PC 1 turns 2 features into 1.', 11)
    s.save('pca-directions.svg', OUT)


def entropy_vs_gini():
    H = lambda q: 0 if q in (0, 1) else -(q * math.log2(q) + (1 - q) * math.log2(1 - q))
    Gi = lambda q: 1 - q * q - (1 - q) ** 2
    s = Svg(460, 300, 'Impurity of a two-class node against the share of class 1: entropy peaks at 1 and Gini at '
                      '0.5, both when the classes are 50/50, and both are 0 for a pure node')
    p = Plot(s, 60, 20, 360, 220, (0, 1), (0, 1.05))
    p.axes('share of class 1 in the node', 'impurity', xticks=(0, 0.25, 0.5, 0.75, 1), yticks=(0, 0.5, 1))
    p.curve([(i / 200, H(i / 200)) for i in range(201)], PIX, 2.6)
    p.curve([(i / 200, Gi(i / 200)) for i in range(201)], ORANGE, 2.6)
    s.text(p.X(0.5), p.Y(1) - 6, 'entropy (max 1)', 12, PIX, weight='bold')
    s.text(p.X(0.5), p.Y(0.5) - 8, 'Gini (max 0.5)', 12, ORANGE, weight='bold')
    p.dot(0.75, H(0.75), PIX)
    s.text(p.X(0.75) + 8, p.Y(H(0.75)) - 6, '3 Yes : 1 No → 0.811', 11, PIX, 'start')
    s.text(230, 292, 'Pure nodes (share 0 or 1) score 0 on both. Both rank splits almost the same way.', 11)
    s.save('entropy-vs-gini.svg', OUT)


def ai_nesting():
    s = Svg(460, 300, 'Nested boxes: Artificial Intelligence contains Machine Learning, which contains Deep Learning')
    boxes = [(15, 15, 430, 270, '#f3f4f6', 'Artificial Intelligence', 'the broad goal: machines doing tasks that seem to need intelligence'),
             (55, 75, 350, 195, '#dbeafe', 'Machine Learning', 'learn patterns from data instead of hand-coded rules'),
             (100, 140, 260, 115, '#d1fae5', 'Deep Learning', 'learn patterns with layered neural networks')]
    for x, y, w, h, fill, name, sub in boxes:
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{INK}" stroke-width="1.4"/>')
        s.text(x + w / 2, y + 24, name, 14, weight='bold')
        s.text(x + w / 2, y + 42, sub, 10.5)
    s.save('ai-ml-dl-nesting.svg', OUT)


def graph_svg(name, title, body, rankdir='LR'):
    src = (f'digraph {{ bgcolor="white"; pad=0.25; rankdir={rankdir}; nodesep=0.5; ranksep=0.45;\n'
           f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", fillcolor="#dbeafe", '
           f'color="{INK}", penwidth=1.3];\nedge [fontname="{FONT}", fontsize=12, color="{INK}"];\n{body}\n}}')
    save_dot(src, name, title, OUT)


# ---------- trees drawn step by step, as the lessons build them ----------

def staged_tree_dot(tree, expanded, new, order, count_fmt):
    """Draw `tree` as it stands mid-build. `expanded` holds the paths (tuples of branch values from the root) of the
    nodes already split; any other internal node is drawn as a dashed '?' waiting to be split. `new` is the path of
    the node split in this step, outlined in orange."""
    lines = [f'digraph {{ bgcolor="white"; pad=0.25; nodesep=0.35; ranksep=0.45;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.3];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="{INK}"];']
    ids = iter(range(1000))

    def walk(t, path):
        i = next(ids)
        c = count_fmt(t['counts'])
        if 'leaf' in t:
            lines.append(f'n{i} [label="{t["leaf"]}\\n{c}", fillcolor="#d1fae5", fontcolor="#065f46"];')
        elif path not in expanded:
            lines.append(f'n{i} [label="?\\n{c}", fillcolor="#f3f4f6", style="rounded,filled,dashed", '
                         f'color="#6b7280", fontcolor="#4b5563"];')
        else:
            hl = f', color="{ORANGE}", penwidth=3' if path == new else ''
            lines.append(f'n{i} [label="{t["attr"]}?\\n{c}", fillcolor="#dbeafe"{hl}];')
            for v in order.get(t['attr'], sorted(t['kids'])):
                j = walk(t['kids'][v], path + (v,))
                lines.append(f'n{i} -> n{j} [label=" {v} "];')
        return i

    walk(tree, ())
    lines.append('}')
    return '\n'.join(lines)


def staged_trees():
    cols = ['Outlook', 'Temp', 'Humidity', 'Wind', 'Play']
    data = """Sunny Hot High Weak No|Sunny Hot High Strong No|Overcast Hot High Weak Yes|Rain Mild High Weak Yes
Rain Cool Normal Weak Yes|Rain Cool Normal Strong No|Overcast Cool Normal Strong Yes|Sunny Mild High Weak No
Sunny Cool Normal Weak Yes|Rain Mild Normal Weak Yes|Sunny Mild Normal Strong Yes|Overcast Mild High Strong Yes
Overcast Hot Normal Weak Yes|Rain Mild High Strong No"""
    rows = [dict(zip(cols, r.split())) for r in data.replace('\n', '|').split('|')]
    t = grow(rows, cols[:-1], 'Play', 'entropy')
    fmt = lambda c: f'[{c.get("Yes", 0)}+, {c.get("No", 0)}−]'
    order = {'Outlook': ['Sunny', 'Overcast', 'Rain']}
    steps = [('play-tennis-step1-root.svg', {()}, (),
              'Play Tennis tree after step 1: Outlook is the root; Overcast is already a Yes leaf; Sunny and Rain are '
              'still question marks waiting to be split'),
             ('play-tennis-step2-sunny.svg', {(), ('Sunny',)}, ('Sunny',),
              'Play Tennis tree after step 2: the Sunny branch now splits on Humidity into a No leaf and a Yes leaf; '
              'Rain is still a question mark'),
             ('play-tennis-step3-rain.svg', {(), ('Sunny',), ('Rain',)}, ('Rain',),
              'Play Tennis tree after step 3: the Rain branch now splits on Wind into a No leaf and a Yes leaf, so '
              'every branch ends in a leaf')]
    for name, exp, new, title in steps:
        save_dot(staged_tree_dot(t, exp, new, order, fmt), name, title, OUT)

    cols = ['Weather', 'Parent', 'Money', 'Decision']
    data = """Sunny Yes Rich Cinema|Sunny No Rich Tennis|Windy Yes Rich Cinema|Rainy Yes Poor Cinema
Rainy No Rich StayIn|Rainy Yes Poor Cinema|Windy No Poor Cinema|Windy No Rich Shopping
Windy Yes Rich Cinema|Sunny No Rich Tennis"""
    rows = [dict(zip(cols, r.split())) for r in data.replace('\n', '|').split('|')]
    for r in rows:
        r['Decision'] = r['Decision'].replace('StayIn', 'Stay In')
    t = grow(rows, cols[:-1], 'Decision', 'gini')
    fmt = lambda c: f'({sum(c.values())} weekend{"s" if sum(c.values()) > 1 else ""})'
    order = {'Parent': ['Yes', 'No'], 'Weather': ['Sunny', 'Rainy', 'Windy'], 'Money': ['Rich', 'Poor']}
    steps = [('weekend-step1-root.svg', {()}, (),
              'Weekend tree after step 1: Parent is the root; Parent Yes is already a Cinema leaf; Parent No is a '
              'question mark waiting to be split'),
             ('weekend-step2-weather.svg', {(), ('No',)}, ('No',),
              'Weekend tree after step 2: Parent No splits on Weather into Tennis for Sunny and Stay In for Rainy; '
              'Windy is still a question mark'),
             ('weekend-step3-money.svg', {(), ('No',), ('No', 'Windy')}, ('No', 'Windy'),
              'Weekend tree after step 3: the Windy branch splits on Money into Shopping for Rich and Cinema for '
              'Poor, so every branch ends in a leaf')]
    for name, exp, new, title in steps:
        save_dot(staged_tree_dot(t, exp, new, order, fmt), name, title, OUT)


def loan_tree():
    """A fresh tree for prediction questions, so they don't depend on remembering the lesson's tree."""
    cols = ['Credit', 'Income', 'Employed', 'Loan']
    data = ('Good High Yes Approve|Good High No Approve|Good Low Yes Approve|Good Low No Reject|Good Low No Reject|'
            'Bad High Yes Reject|Bad High No Reject|Bad Low Yes Reject|Good High Yes Approve|Bad Low No Reject')
    rows = [dict(zip(cols, r.split())) for r in data.split('|')]
    t = grow(rows, cols[:-1], 'Loan', 'entropy')
    assert shape(t) == {'Credit': {'Bad': 'Reject', 'Good': {'Income': {'High': 'Approve', 'Low': {
        'Employed': {'No': 'Reject', 'Yes': 'Approve'}}}}}}
    fmt = lambda c: f'[{c.get("Approve", 0)} approve, {c.get("Reject", 0)} reject]'
    src = tree_dot(t, 'Loan', order={'Credit': ['Good', 'Bad'], 'Income': ['High', 'Low'], 'Employed': ['Yes', 'No']},
                   count_fmt=fmt)
    save_dot(src, 'loan-tree.svg', out=OUT, title='Loan decision tree: Credit at the root; Bad credit gives Reject; '
             'Good credit asks Income, where High gives Approve and Low asks Employed, where Yes gives Approve '
             'and No gives Reject')


# ---------- more lessons: classical ML, evaluation, deep learning ----------

def tree_parts():
    src = ('digraph { bgcolor="white"; pad=0.25; nodesep=0.4; ranksep=0.5;\n'
           f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.3];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#6b7280"];\n'
           'r [label="Outlook?\\nROOT NODE", fillcolor="#dbeafe"]; i [label="Humidity?\\nINTERNAL NODE", fillcolor="#dbeafe"];\n'
           'l1 [label="Yes\\nLEAF NODE", fillcolor="#d1fae5"]; l2 [label="No\\nLEAF", fillcolor="#d1fae5"]; l3 [label="Yes\\nLEAF", fillcolor="#d1fae5"];\n'
           'r -> i [label=" branch: Sunny "]; r -> l1 [label=" branch: Overcast "]; i -> l2 [label=" High "]; i -> l3 [label=" Normal "];\n}')
    save_dot(src, 'tree-parts.svg', 'Parts of a decision tree: the root node at the top asks the first question, '
             'branches carry each answer, internal nodes ask further questions, and leaf nodes give the prediction', OUT)


def knn_regression():
    pts = [(40, 70), (55, 90), (62, 100), (70, 120), (78, 140), (90, 150), (105, 175), (120, 190)]
    q = 70.5
    near = sorted(pts, key=lambda p: abs(p[0] - q))[:3]
    pred = sum(y for _, y in near) / 3
    assert sorted(y for _, y in near) == [100, 120, 140] and pred == 120
    s = Svg(470, 310, 'KNN regression with K = 3: the three houses nearest in size sold for 100, 120 and 140 thousand, '
                      'so the prediction for the new house is their average, 120 thousand')
    p = Plot(s, 70, 20, 370, 220, (30, 130), (50, 200))
    p.axes('house size (m²)', 'price (thousands)', xticks=(40, 60, 80, 100, 120), yticks=(50, 100, 150, 200))
    for x, y in pts:
        p.dot(x, y, PIX if (x, y) in near else '#93c5fd', 6 if (x, y) in near else 4.5)
    for x, y in near:
        s.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="10" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    s.line(p.X(q), p.Y(50), p.X(q), p.Y(195), '#9ca3af', 1.2, '4 4')
    s.line(p.X(50), p.Y(pred), p.X(92), p.Y(pred), ORANGE, 2, '6 4')
    p.dot(q, pred, ORANGE, 7)
    s.text(p.X(q) + 12, p.Y(pred) + 18, 'prediction = (100 + 120 + 140) / 3 = 120', 11, ORANGE, 'start', 'bold')
    s.text(p.X(q), p.Y(195) - 4, 'new house', 11, INK, 'middle', 'bold')
    s.save('knn-regression.svg', OUT)


def lvq_update_picture():
    w, x, a = (2, 2), (4, 3), 0.1
    closer = (w[0] + a * (x[0] - w[0]), w[1] + a * (x[1] - w[1]))
    away = (w[0] - a * (x[0] - w[0]), w[1] - a * (x[1] - w[1]))
    assert (round(closer[0], 6), round(closer[1], 6)) == (2.2, 2.1) and (round(away[0], 6), round(away[1], 6)) == (1.8, 1.9)
    s = Svg(470, 300, 'LVQ update with alpha 0.1: prototype w = (2, 2) and training point x = (4, 3); same class moves w '
                      'a tenth of the way towards x, to (2.2, 2.1); different class moves it away, to (1.8, 1.9)')
    mk = arrow_defs(s)
    p = Plot(s, 60, 20, 380, 220, (1.6, 2.75), (1.8, 2.3))
    p.axes('', '', xticks=(1.8, 2, 2.2, 2.4, 2.6), yticks=(1.9, 2, 2.1, 2.2))
    end = (2.75, 2 + 0.75 * 0.5)                       # the direction from w towards x = (4, 3), cut at the plot edge
    s.line(p.X(1.6), p.Y(2 - 0.4 * 0.5), p.X(end[0]), p.Y(end[1]), '#d1d5db', 1.2, '5 4')
    s.text(p.X(2.72), p.Y(2.3) + 14, 'towards x (4, 3) →', 11, PIX, 'end', 'bold')
    vec(s, p, w, closer, ACCENT, mk, 2.6)
    vec(s, p, w, away, TRUE, mk, 2.6)
    p.dot(*w, INK, 6)
    s.text(p.X(2) - 10, p.Y(2) - 8, 'w (2, 2)', 12, INK, 'end', 'bold')
    s.text(p.X(2.2) + 10, p.Y(2.1) + 4, 'same class → (2.2, 2.1)', 11, ACCENT, 'start', 'bold')
    s.text(p.X(1.8) + 10, p.Y(1.9) + 4, 'different class → (1.8, 1.9)', 11, TRUE, 'start', 'bold')
    s.save('lvq-update.svg', OUT)


def kernel_lift():
    a = [-1.2, -0.6, 0, 0.5, 1.1]
    b = [-3, -2.4, -2, 2.1, 2.6, 3.1]
    s = Svg(580, 290, 'The kernel trick idea: on a line, class A sits between two groups of class B, so no single cut '
                      'separates them; mapping each x to (x, x squared) lifts B high, and a straight line now separates them')
    p1 = Plot(s, 30, 120, 230, 40, (-3.5, 3.5), (-1, 1))
    s.line(p1.X(-3.5), p1.Y(0), p1.X(3.5), p1.Y(0), INK, 1.2)
    for x in a:
        p1.dot(x, 0, ORANGE, 6)
    for x in b:
        p1.dot(x, 0, PIX, 6)
    s.text(145, 40, '1-D: no single cut works', 12, weight='bold')
    s.text(145, 200, 'orange A in the middle, blue B on both sides', 10)
    p2 = Plot(s, 320, 30, 230, 200, (-3.5, 3.5), (0, 10))
    p2.axes('x', 'x²', xticks=(-3, 0, 3), yticks=(0, 5, 10))
    p2.curve([(x / 10, (x / 10) ** 2) for x in range(-32, 33)], '#d1d5db', 1)
    for x in a:
        p2.dot(x, x * x, ORANGE, 6)
    for x in b:
        p2.dot(x, x * x, PIX, 6)
    s.line(p2.X(-3.5), p2.Y(2.6), p2.X(3.5), p2.Y(2.6), ACCENT, 2.2, '6 4')
    s.text(p2.X(3.4), p2.Y(2.6) - 6, 'a straight line separates them', 10, ACCENT, 'end', 'bold')
    s.text(435, 22, 'Lifted to (x, x²)', 12, weight='bold')
    s.save('kernel-lift.svg', OUT)


def svm_margin():
    A = [(2, 3), (3, 2), (1, 2), (2, 1), (1, 1), (0.5, 3)]
    B = [(4, 3), (3, 4), (5, 4), (4, 5), (5, 5.5), (6, 3.5)]
    assert min(x + y for x, y in B) == 7 and max(x + y for x, y in A) == 5
    sv = [p for p in A + B if p[0] + p[1] in (5, 7)]
    s = Svg(440, 360, 'A support vector machine: the boundary x + y = 6 sits in the middle of the widest gap between the '
                      'classes; the dashed margin lines touch the support vectors, the only points that fix the boundary')
    p = Plot(s, 50, 20, 340, 280, (0, 7), (0, 6.5))
    p.axes('feature 1', 'feature 2', xticks=range(8), yticks=range(7))
    for c, col in ((5, '#9ca3af'), (7, '#9ca3af'), (6, TRUE)):
        p.curve([(max(0, c - 6.5), min(6.5, c)), (min(7, c), max(0, c - 7))], col, 2.4 if c == 6 else 1.4,
                dash=None if c == 6 else '6 4')
    for q in A:
        p.dot(*q, ORANGE, 6)
    for q in B:
        p.dot(*q, PIX, 6)
    for q in sv:
        s.add(f'<circle cx="{p.X(q[0]):.1f}" cy="{p.Y(q[1]):.1f}" r="11" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    s.text(p.X(4.6), p.Y(1.0), 'boundary x + y = 6', 11, TRUE, 'start', 'bold')
    s.text(220, 352, 'Circled: support vectors. Move any other point and the boundary stays where it is.', 11)
    s.save('svm-margin.svg', OUT)


def confusion_matrix_picture():
    TN, FP, FN, TP = 50, 10, 5, 100
    s = Svg(430, 300, 'Confusion matrix for 165 predictions: 50 true negatives, 10 false positives, 5 false negatives '
                      'and 100 true positives; the diagonal holds the correct predictions')
    cells = [((0, 0), TN, 'TN', ACCENT), ((1, 0), FP, 'FP', TRUE), ((0, 1), FN, 'FN', TRUE), ((1, 1), TP, 'TP', ACCENT)]
    x0, y0, c = 150, 60, 110
    for (cx, cy), v, name, col in cells:
        s.rect(x0 + cx * c, y0 + cy * c, c, c, col, '#ffffff', 3, opacity=0.22 + 0.6 * v / 100)
        s.text(x0 + cx * c + c / 2, y0 + cy * c + c / 2 - 2, str(v), 26, INK, weight='bold')
        s.text(x0 + cx * c + c / 2, y0 + cy * c + c / 2 + 22, name, 13, INK, weight='bold')
    s.text(x0 + c / 2, y0 - 10, 'Predicted No', 12, weight='bold')
    s.text(x0 + 1.5 * c, y0 - 10, 'Predicted Yes', 12, weight='bold')
    s.text(x0 - 12, y0 + c / 2 + 4, 'Actual No', 12, anchor='end', weight='bold')
    s.text(x0 - 12, y0 + 1.5 * c + 4, 'Actual Yes', 12, anchor='end', weight='bold')
    s.text(215, 292, 'Green diagonal: correct. Red: the two kinds of mistake (FP = Type I, FN = Type II).', 11)
    s.save('confusion-matrix.svg', OUT)


def roc_curve():
    import random
    rnd = random.Random(5)
    pos = [rnd.gauss(1.2, 1) for _ in range(200)]
    neg = [rnd.gauss(0, 1) for _ in range(200)]
    scores = sorted([(sc, 1) for sc in pos] + [(sc, 0) for sc in neg], reverse=True)
    tp = fp = 0
    pts = [(0, 0)]
    for sc, y in scores:
        if y:
            tp += 1
        else:
            fp += 1
        pts.append((fp / 200, tp / 200))
    auc = sum((x2 - x1) * (y1 + y2) / 2 for (x1, y1), (x2, y2) in zip(pts, pts[1:]))
    s = Svg(420, 380, f'ROC curve: true positive rate against false positive rate as the threshold moves; the area '
                      f'under it, AUC = {auc:.2f}, beats the 0.5 of random guessing shown by the diagonal')
    p = Plot(s, 70, 20, 310, 290, (0, 1), (0, 1))
    p.axes('false positive rate (FPR)', 'true positive rate (TPR)', xticks=(0, 0.5, 1), yticks=(0, 0.5, 1))
    d = 'M ' + f'{p.X(0):.1f} {p.Y(0):.1f} ' + ' '.join(f'L {p.X(x):.1f} {p.Y(y):.1f}' for x, y in pts) + f' L {p.X(1):.1f} {p.Y(0):.1f} Z'
    s.add(f'<path d="{d}" fill="#dbeafe" stroke="none"/>')
    p.curve(pts, PIX, 2.6)
    p.curve([(0, 0), (1, 1)], '#9ca3af', 1.4, dash='6 4')
    s.text(p.X(0.62), p.Y(0.3), f'AUC = {auc:.2f}', 16, PIX, weight='bold')
    s.text(p.X(0.72), p.Y(0.62), 'random: AUC = 0.5', 11, '#6b7280', 'start')
    s.text(p.X(0.02), p.Y(1) - 6, 'perfect model: top-left corner', 10, INK, 'start')
    s.save('roc-curve.svg', OUT)


def mlp_layers():
    layers = [3, 4, 4, 2]
    names = ['input', 'hidden 1', 'hidden 2', 'output']
    s = Svg(500, 300, 'A multi-layer perceptron: 3 inputs, two hidden layers of 4 neurons and 2 outputs; every neuron '
                      'connects to every neuron in the next layer')
    xs = [70 + i * 120 for i in range(4)]
    pos = [[(xs[i], 150 + (j - (n - 1) / 2) * 52) for j in range(n)] for i, n in enumerate(layers)]
    for i in range(3):
        for a in pos[i]:
            for b in pos[i + 1]:
                s.line(a[0], a[1], b[0], b[1], '#cbd2d9', 1)
    cols = [ORANGE, PIX, PIX, ACCENT]
    for i, layer in enumerate(pos):
        for x, y in layer:
            s.add(f'<circle cx="{x}" cy="{y:.1f}" r="15" fill="#ffffff" stroke="{cols[i]}" stroke-width="2.4"/>')
        s.text(xs[i], 270, names[i], 12, cols[i], weight='bold')
    s.text(250, 26, 'Each line is one weight. Each circle: weighted sum + bias, then an activation.', 11)
    s.save('mlp-layers.svg', OUT)


def activation_functions():
    fns = [('ReLU = max(0, z)', lambda z: max(0.0, z), (-0.5, 4.2)), ('sigmoid', lambda z: 1 / (1 + math.exp(-z)), (-0.1, 1.1)),
           ('tanh', math.tanh, (-1.1, 1.1))]
    s = Svg(600, 230, 'Three activation functions: ReLU is zero for negatives and linear for positives; sigmoid squeezes '
                      'any input into 0 to 1; tanh squeezes it into minus 1 to 1')
    for k, (name, f, yr) in enumerate(fns):
        p = Plot(s, 45 + k * 195, 35, 150, 140, (-4, 4), yr)
        s.line(p.X(-4), p.Y(0), p.X(4), p.Y(0), '#cbd2d9', 1)
        s.line(p.X(0), p.Y(yr[0]), p.X(0), p.Y(yr[1]), '#cbd2d9', 1)
        p.curve([(z / 10, max(yr[0], min(yr[1], f(z / 10)))) for z in range(-40, 41)], [ACCENT, PIX, ORANGE][k], 2.6)
        s.text(p.x0 + p.w / 2, 24, name, 12, weight='bold')
        for t in (yr[0] if yr[0] < 0 else 0, ):
            pass
    s.text(300, 210, 'ReLU: the default in hidden layers. Sigmoid: a probability out. Tanh: centred on 0.', 11)
    s.save('activation-functions.svg', OUT)


def convolution_picture():
    img = [[1, 2, 0, 1, 3], [3, 1, 2, 0, 1], [0, 1, 2, 2, 0], [2, 0, 1, 3, 1], [1, 2, 0, 1, 2]]
    k = [[1, 0, -1], [1, 0, -1], [1, 0, -1]]
    out = [[sum(img[i + a][j + b] * k[a][b] for a in range(3) for b in range(3)) for j in range(3)] for i in range(3)]
    assert out[0][0] == 0                                   # the lesson's worked patch gives 0
    s = Svg(600, 260, 'Convolution: the 3 by 3 filter slides over the 5 by 5 image; at the top-left position it '
                      'multiplies the patch by the filter and sums, giving 0, the first value of the 3 by 3 output')
    def grid(x0, y0, M, c, hl=None, colors=None):
        for i, row in enumerate(M):
            for j, v in enumerate(row):
                fill = '#ffffff'
                if hl and i < 3 and j < 3:
                    fill = '#dbeafe'
                if colors:
                    fill = colors(i, j)
                s.rect(x0 + j * c, y0 + i * c, c, c, fill, INK, 1)
                s.text(x0 + j * c + c / 2, y0 + i * c + c / 2 + 5, str(v), 14)
    grid(20, 50, img, 34, hl=True)
    s.rect(20, 50, 102, 102, 'none', PIX, 3)
    s.text(105, 36, 'image (5 × 5)', 12, weight='bold')
    s.text(205, 136, '∗', 30, weight='bold')
    grid(235, 84, k, 34, colors=lambda i, j: '#fef3c7')
    s.text(286, 70, 'filter (3 × 3)', 12, weight='bold')
    s.text(365, 136, '=', 26, weight='bold')
    grid(400, 84, out, 34, colors=lambda i, j: '#d1fae5' if (i, j) == (0, 0) else '#ffffff')
    s.text(451, 70, 'output (3 × 3)', 12, weight='bold')
    s.text(300, 230, 'Blue patch · filter: (1 + 3 + 0) − (0 + 2 + 2) = 0. Slide one step and repeat for each output cell.', 11)
    s.save('convolution.svg', OUT)


def rnn_unrolled():
    body = ['node [shape=circle, fixedsize=true, width=0.55];']
    for t in range(1, 5):
        body.append(f'x{t} [label="x{t}", fillcolor="#fef3c7"]; h{t} [label="h{t}"]; x{t} -> h{t};')
    body.append('h1 -> h2 -> h3 -> h4 [label="  W  "]; {rank=same; h1; h2; h3; h4}')
    src = ('digraph { bgcolor="white"; pad=0.25; rankdir=BT; nodesep=0.7; ranksep=0.45;\n'
           f'node [fontname="{FONT}", fontsize=13, style=filled, fillcolor="#dbeafe", color="{INK}", penwidth=1.3];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}"];\n' + '\n'.join(body) + '\n}')
    save_dot(src, 'rnn-unrolled.svg', 'An RNN unrolled over four steps: each input x feeds the hidden state h at its step, '
             'and each hidden state passes forward to the next through the same weights W', OUT)


def attention_weights():
    toks = ['The', 'cat', 'sat', 'because', 'it', 'was', 'tired']
    w = [0.04, 0.62, 0.08, 0.05, 0.10, 0.04, 0.07]           # illustrative weights for the query "it"
    assert abs(sum(w) - 1) < 1e-9
    s = Svg(560, 250, 'Self-attention, illustrated: when processing the word "it", the model spreads 100 percent of its '
                      'attention over the sentence, putting most of it, 62 percent, on "cat"')
    x0, gap = 40, 72
    qx, qy = x0 + 4 * gap, 200
    for i, (t, a) in enumerate(zip(toks, w)):
        x = x0 + i * gap
        s.add(f'<path d="M {qx} {qy - 14} Q {(qx + x) / 2} {qy - 110} {x} 74" fill="none" stroke="{PIX}" '
              f'stroke-width="{1 + 14 * a:.1f}" stroke-opacity="{0.25 + 0.75 * a / max(w):.2f}"/>')
        s.rect(x - 30, 40, 60, 30, '#dbeafe' if t != 'it' else '#fef3c7', INK, 1)
        s.text(x, 60, t, 13, weight='bold')
        s.text(x, 34, f'{a:.0%}', 11, PIX, weight='bold')
    s.rect(qx - 30, qy - 14, 60, 28, '#fef3c7', INK, 1.4)
    s.text(qx, qy + 5, 'it', 13, weight='bold')
    s.text(280, 240, 'Weights are illustrative. Thicker line = more attention. The weights always sum to 100%.', 11)
    s.save('attention-weights.svg', OUT)


def backprop_chain():
    src = ('digraph { bgcolor="white"; pad=0.25; rankdir=LR; nodesep=0.5; ranksep=0.6;\n'
           f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", fillcolor="#dbeafe", color="{INK}", penwidth=1.3];\n'
           f'edge [fontname="{FONT}", fontsize=11];\n'
           'W [label="parameter W", fillcolor="#fef3c7"]; L1 [label="layer 1"]; L2 [label="layer 2"]; L3 [label="layer 3"]; loss [label="loss", fillcolor="#fee2e2"];\n'
           f'W -> L1 -> L2 -> L3 -> loss [color="{INK}", label=" forward "];\n'
           f'loss -> L3 [color="{TRUE}", fontcolor="{TRUE}", label=" ∂loss/∂L3 ", constraint=false];\n'
           f'L3 -> L2 [color="{TRUE}", fontcolor="{TRUE}", label=" ∂L3/∂L2 ", constraint=false];\n'
           f'L2 -> L1 [color="{TRUE}", fontcolor="{TRUE}", label=" ∂L2/∂L1 ", constraint=false];\n'
           f'L1 -> W [color="{TRUE}", fontcolor="{TRUE}", label=" ∂L1/∂W ", constraint=false];\n}}')
    save_dot(src, 'backprop-chain.svg', 'Backpropagation: values flow forward from W through layers 1 to 3 to the loss; '
             'derivatives flow backward, and the gradient of the loss with respect to W is the product of the local '
             'derivatives along the way', OUT)


def bayes_frequency_tree():
    total, spam = 1000, 200
    spam_phrase, ham_phrase = 60, 20                      # 30% of spam; total with phrase 80 = 8% of all
    assert spam_phrase / (spam_phrase + ham_phrase) == 0.75
    src = ('digraph { bgcolor="white"; pad=0.25; nodesep=0.3; ranksep=0.45;\n'
           f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", fillcolor="#f3f4f6", color="{INK}", penwidth=1.2];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}"];\n'
           'all [label="1000 emails"]; s [label="200 spam (20%)", fillcolor="#fee2e2"]; h [label="800 not spam", fillcolor="#d1fae5"];\n'
           'sp [label="60 contain\\n\\"free money\\"", fillcolor="#fef3c7", penwidth=2.4]; sn [label="140 don\'t"];\n'
           'hp [label="20 contain\\n\\"free money\\"", fillcolor="#fef3c7", penwidth=2.4]; hn [label="780 don\'t"];\n'
           'all -> s; all -> h; s -> sp [label=" 30% "]; s -> sn; h -> hp [label=" 2.5% "]; h -> hn;\n}')
    save_dot(src, 'bayes-spam-frequencies.svg', 'The spam example as counts out of 1000 emails: 200 are spam and 60 of '
             'those contain free money; 20 of the 800 others also contain it; so of the 80 emails with the phrase, '
             '60 are spam, which is 75 percent', OUT)


def mlops_loop():
    stages = ['collect data', 'validate data', 'engineer features', 'train', 'evaluate', 'validate model', 'deploy', 'monitor']
    body = [f'n{i} [label="{st}"];' for i, st in enumerate(stages)]
    body += [f'n{i} -> n{i + 1};' for i in range(len(stages) - 1)]
    body.append(f'n7 -> n0 [label="  drift detected:\\n  retrain", color="{TRUE}", fontcolor="{TRUE}", penwidth=1.8];')
    src = ('digraph { bgcolor="white"; pad=0.3; layout=circo; mindist=0.9;\n'
           f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", fillcolor="#dbeafe", color="{INK}", penwidth=1.2];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}"];\n' + '\n'.join(body) + '\n}')
    save_dot(src, 'mlops-loop.svg', 'The ML lifecycle as a loop: collect data, validate it, engineer features, train, '
             'evaluate, validate the model, deploy and monitor; when monitoring detects drift, it goes back round to retrain', OUT)


if __name__ == '__main__':
    play_tennis_tree()
    weekend_tree()
    bayes_net('sprinkler-network.svg',
              'Bayesian network: Cloudy points to Sprinkler and Rain, and both Sprinkler and Rain point to WetGrass',
              [('Cloudy', 'Sprinkler'), ('Cloudy', 'Rain'), ('Sprinkler', 'WetGrass'), ('Rain', 'WetGrass')],
              [['Cloudy'], ['Sprinkler', 'Rain'], ['WetGrass']])
    bayes_net('burglary-alarm-network.svg',
              'Bayesian network: Burglary and Earthquake both point to Alarm, and Alarm points to John Calls and Mary Calls',
              [('Burglary', 'Alarm'), ('Earthquake', 'Alarm'), ('Alarm', 'John Calls'), ('Alarm', 'Mary Calls')],
              [['Burglary', 'Earthquake'], ['Alarm'], ['John Calls', 'Mary Calls']])
    overfitting_curves()
    gradient_descent_steps()
    sigmoid_curve()
    elbow_plot()
    knn_picture()
    commute_tree()
    elbow_from_numbers()
    bayes_net('slippery-network.svg',
              'Bayesian network: Rain and Sprinkler both point to WetGrass, and WetGrass points to Slippery',
              [('Rain', 'WetGrass'), ('Sprinkler', 'WetGrass'), ('WetGrass', 'Slippery')],
              [['Rain', 'Sprinkler'], ['WetGrass'], ['Slippery']])
    derivative_tangents()
    normal_distribution()
    sklearn_style_tree()
    vectors_picture()
    dot_product_cases()
    matrix_transform()
    euclid_vs_manhattan()
    split_bar()
    fit_curves()
    least_squares()
    kmeans_clusters()
    pca_directions()
    entropy_vs_gini()
    ai_nesting()
    graph_svg('gan-loop.svg', 'A GAN: random noise goes into the Generator, which makes a fake image; the Discriminator '
              'sees fake and real images and decides real or fake',
              'noise [label="random noise", fillcolor="#f3f4f6"]; G [label="Generator"]; fake [label="fake image", fillcolor="#fef3c7"];'
              'real [label="real image", fillcolor="#d1fae5"]; D [label="Discriminator"]; out [label="real or fake?", fillcolor="#f3f4f6"];'
              'noise -> G -> fake -> D; real -> D; D -> out; {rank=same; fake; real}')
    graph_svg('rl-loop.svg', 'The reinforcement learning loop: the agent sends an action to the environment, and the '
              'environment sends back a new state and a reward',
              'A [label="Agent"]; E [label="Environment", fillcolor="#d1fae5"];'
              'A -> E [label="  action  "]; E -> A [label="  state, reward  "];')
    graph_svg('autoencoder.svg', 'An autoencoder: the input goes through the encoder to a small latent vector, then '
              'the decoder rebuilds it; the loss is the difference between input and reconstruction',
              'in [label="input", fillcolor="#f3f4f6"]; enc [label="encoder"]; z [label="latent\n(small)", fillcolor="#fef3c7", width=0.8];'
              'dec [label="decoder"]; out [label="reconstruction", fillcolor="#f3f4f6"]; in -> enc -> z -> dec -> out;')
    staged_trees()
    loan_tree()
    tree_parts()
    knn_regression()
    lvq_update_picture()
    kernel_lift()
    svm_margin()
    confusion_matrix_picture()
    roc_curve()
    mlp_layers()
    activation_functions()
    convolution_picture()
    rnn_unrolled()
    attention_weights()
    backprop_chain()
    bayes_frequency_tree()
    mlops_loop()
