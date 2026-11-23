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
from svgkit import INK, PIX, PIX2, TRUE, ACCENT, Svg  # noqa: E402

OUT = os.path.join('machine-learning', 'images')
ORANGE = '#f59e0b'
FONT = 'Helvetica,Arial,sans-serif'


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


def save_dot(src, name, title):
    svg = subprocess.run(['dot', '-Tsvg'], input=src, capture_output=True, text=True, check=True).stdout
    svg = re.sub(r'<\?xml.*?\?>\s*', '', svg)
    svg = re.sub(r'<!DOCTYPE.*?>\s*', '', svg, flags=re.S)
    svg = re.sub(r'<!--.*?-->\s*', '', svg, flags=re.S)
    svg = svg.replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', '')
    svg = re.sub(r'<title>[^<]*</title>\s*', '', svg)            # node ids, not useful
    svg = svg.replace('<svg ', '<svg role="img" ', 1)
    svg = re.sub(r'(<svg[^>]*>)', r'\1\n<title>' + title + '</title>', svg, count=1)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(svg)
    print(f'{name}: {len(svg)} bytes')


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
    save_dot(src, 'play-tennis-tree.svg',
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
    save_dot(src, 'weekend-gini-tree.svg',
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
    save_dot('\n'.join(lines), name, title)


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
    save_dot(src, 'commute-tree.svg',
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
