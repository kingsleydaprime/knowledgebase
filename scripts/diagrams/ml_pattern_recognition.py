"""Draw the pattern-recognition and parametric/non-parametric diagrams (machine-learning/03-classical-ml lessons 21-24).

    python3 scripts/diagrams/ml_pattern_recognition.py      # run from the vault root

Every number the lessons quote is computed here and asserted before drawing: the
nearest-mean mango classifier, the parametric (Gaussian) and non-parametric (Parzen
window) density estimates that disagree on a new point, and the kappa, MAE and RMSE
worked examples. Output: machine-learning/images/pr-*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, ACCENT, PIX, TRUE, Svg, flowchart, save_dot, FONT  # noqa: E402

OUT = os.path.join('machine-learning', 'images')
ORANGE = '#f59e0b'

# Lesson 22: nearest-mean classifier on mangoes (sweetness, firmness), both scored 1-10.
RIPE = [(8, 3), (9, 2), (7, 4)]
UNRIPE = [(3, 8), (2, 9), (4, 7)]
NEW_MANGO = (6, 5)

# Lesson 23: one feature; class A has two clumps, class B one tight clump.
A = [1, 2, 2, 9, 10]
B = [5, 5, 6, 6, 7]
X_NEW = 7.5
H = 1.0   # Parzen half-width: count points within +/- 1


def mean(v):
    return sum(v) / len(v)


def var(v):
    m = mean(v)
    return sum((x - m) ** 2 for x in v) / len(v)   # population variance, as in the lesson


def gauss(x, m, v):
    return math.exp(-(x - m) ** 2 / (2 * v)) / math.sqrt(2 * math.pi * v)


def parzen(x, data, h=H):
    k = sum(1 for d in data if abs(d - x) <= h)
    return k, k / (len(data) * 2 * h)


def centroid(pts):
    return tuple(sum(p[i] for p in pts) / len(pts) for i in range(2))


def dist(p, q):
    return math.dist(p, q)


def kappa(tp, fn, fp, tn):
    n = tp + fn + fp + tn
    po = (tp + tn) / n
    pe = ((tp + fn) * (tp + fp) + (fp + tn) * (fn + tn)) / n ** 2
    return po, pe, (po - pe) / (1 - pe)


def check():
    # Lesson 22.
    cr, cu = centroid(RIPE), centroid(UNRIPE)
    assert cr == (8, 3) and cu == (3, 8)
    assert round(dist(NEW_MANGO, cr), 2) == 2.83 and round(dist(NEW_MANGO, cu), 2) == 4.24
    # quiz: new mango (5, 6) is nearer unripe
    assert round(dist((5, 6), cr), 2) == 4.24 and round(dist((5, 6), cu), 2) == 2.83
    # Lesson 23: parametric fit.
    assert mean(A) == 4.8 and round(var(A), 2) == 14.96
    assert mean(B) == 5.8 and round(var(B), 2) == 0.56
    ga, gb = gauss(X_NEW, mean(A), var(A)), gauss(X_NEW, mean(B), var(B))
    assert round(ga, 3) == 0.081 and round(gb, 3) == 0.040 and ga > gb          # Gaussian says A
    ka, pa = parzen(X_NEW, A)
    kb, pb = parzen(X_NEW, B)
    assert (ka, kb) == (0, 1) and pa == 0 and pb == 0.1                         # Parzen says B
    nearest_a = min(abs(a - X_NEW) for a in A)
    nearest_b = min(abs(b - X_NEW) for b in B)
    assert nearest_a == 1.5 and nearest_b == 0.5
    # KNN with k = 3 on the pooled data: the 3 nearest are 7 (B), 6 (B), 6 (B) or 9 (A)?
    pooled = sorted([(abs(x - X_NEW), x, 'A') for x in A] + [(abs(x - X_NEW), x, 'B') for x in B])
    top3 = pooled[:3]
    assert [t[2] for t in top3] == ['B', 'B', 'B'] or [t[1] for t in top3] == [7, 6, 6]
    assert sorted(t[1] for t in top3) == [6, 6, 7]
    # Parameter counts: the Gaussian keeps 2 numbers per class; Parzen keeps every point.
    assert len(A) == 5
    # quiz: Gaussian for [2, 4, 6] -> mean 4, variance 8/3
    assert mean([2, 4, 6]) == 4 and round(var([2, 4, 6]), 3) == 2.667
    # quiz: Parzen at 4 with h = 1 for data [3, 4, 4, 8, 9, 10] -> 3 points, 3/12 = 0.25
    assert parzen(4, [3, 4, 4, 8, 9, 10]) == (3, 0.25)
    # Lesson 24: kappa, MAE, RMSE.
    po, pe, k = kappa(40, 10, 20, 30)
    assert (po, pe, round(k, 2)) == (0.7, 0.5, 0.4)
    po, pe, k = kappa(45, 5, 5, 45)
    assert (po, pe, round(k, 2)) == (0.9, 0.5, 0.8)
    errs = [0.1, 0.4, 0.2, 0.3]
    mae = sum(errs) / 4
    rmse = math.sqrt(sum(e * e for e in errs) / 4)
    assert round(mae, 2) == 0.25 and round(rmse, 4) == 0.2739
    # quiz: errors 0.2, 0.2, 0.6, 0.0 -> MAE 0.25, RMSE sqrt(0.44/4)=0.3317
    e2 = [0.2, 0.2, 0.6, 0.0]
    assert round(sum(e2) / 4, 2) == 0.25 and round(math.sqrt(sum(e * e for e in e2) / 4), 4) == 0.3317
    # The paper's table (Kumar and Sahoo 2012): MLP kappa on training data vs 10-fold CV.
    assert round(0.9144 - 0.045, 4) == 0.8694


def mango_plot():
    s = Svg(460, 400, 'A scatter plot of mangoes by sweetness (across) and firmness (up): ripe mangoes at (8, 3), (9, 2) and (7, 4) '
                      'with mean (8, 3); unripe at (3, 8), (2, 9) and (4, 7) with mean (3, 8); the new mango at (6, 5) is 2.83 from '
                      'the ripe mean and 4.24 from the unripe mean, so it is classed ripe')
    x0, y0, u = 60, 350, 32
    s.line(x0, y0, x0 + 10 * u, y0)
    s.line(x0, y0, x0, y0 - 10 * u)
    for i in range(0, 11, 2):
        s.text(x0 + i * u, y0 + 18, i, size=11)
        s.text(x0 - 14, y0 - i * u + 4, i, size=11)
    s.text(x0 + 5 * u, y0 + 40, 'sweetness', size=12)
    s.text(x0 + 4, y0 - 10 * u - 12, 'firmness', size=12, anchor='start')
    P = lambda p: (x0 + p[0] * u, y0 - p[1] * u)  # noqa: E731
    for p in RIPE:
        s.circle(*P(p), 6, ACCENT)
    for p in UNRIPE:
        s.circle(*P(p), 6, PIX)
    for c, col, lab in ((centroid(RIPE), ACCENT, 'ripe mean'), (centroid(UNRIPE), PIX, 'unripe mean')):
        x, y = P(c)
        s.rect(x - 7, y - 7, 14, 14, '#ffffff', stroke=col, width=2.5)
        s.text(x + 12, y - 10, lab, size=12, color=col, anchor='start')
    nx, ny = P(NEW_MANGO)
    for c, d in ((centroid(RIPE), 2.83), (centroid(UNRIPE), 4.24)):
        cx, cy = P(c)
        s.line(nx, ny, cx, cy, color=ORANGE, width=1.5, dash='5 4')
        s.text((nx + cx) / 2 + 6, (ny + cy) / 2 - 6, d, size=12, color='#b45309', anchor='start')
    s.circle(nx, ny, 7, ORANGE)
    s.text(nx - 10, ny + 22, 'new (6, 5)', size=12, color='#b45309')
    s.save('pr-mango-nearest-mean.svg', OUT)


def density_plot():
    w, h = 620, 330
    s = Svg(w, h, 'One feature from 0 to 11. Class A points at 1, 2, 2, 9 and 10 sit in two clumps; class B points at 5, 5, 6, 6 and 7 '
                  'sit in one. The Gaussian fitted to A is a wide hump centred on 4.8, covering the empty middle; the Gaussian fitted '
                  'to B is a narrow peak at 5.8. At the new point 7.5 the wide A curve is higher, but the only nearby data point, 7, is B')
    x0, y0, u, vs = 40, 250, 50, 900
    s.line(x0, y0, x0 + 11 * u, y0)
    for i in range(12):
        s.text(x0 + i * u, y0 + 18, i, size=11)

    def curve(m, v, col):
        pts = []
        for k in range(0, 221):
            x = k * 0.05
            pts.append((x0 + x * u, y0 - min(gauss(x, m, v), 0.6) * vs * 0.3))
        s.path('M ' + ' L '.join(f'{a:.1f} {b:.1f}' for a, b in pts), col, width=2.5)
    curve(mean(A), var(A), TRUE)
    curve(mean(B), var(B), PIX)
    seen = {}
    for x in A:
        seen[x] = seen.get(x, 0) + 1
        s.circle(x0 + x * u, y0 - 8 - (seen[x] - 1) * 14, 6, TRUE)
    seen = {}
    for x in B:
        seen[x] = seen.get(x, 0) + 1
        s.circle(x0 + x * u, y0 + 32 + (seen[x] - 1) * 14, 6, PIX)
    nx = x0 + X_NEW * u
    s.line(nx, 30, nx, y0, color=ORANGE, width=2, dash='5 4')
    s.text(nx + 6, 40, 'new point 7.5', size=12, color='#b45309', anchor='start')
    s.text(x0 + 0.2 * u, 70, 'Gaussian fitted to A (wide)', size=12, color=TRUE, anchor='start')
    s.text(x0 + 6.3 * u, 22, 'Gaussian fitted to B (narrow)', size=12, color=PIX, anchor='start')
    s.text(x0 + 0.2 * u, h - 14, 'A points above the axis, B points below', size=11, color='#374151', anchor='start')
    s.save('pr-parametric-vs-parzen.svg', OUT)


def steps_flow():
    flowchart([
        ('Data collection', 'data'),
        ('Feature choice', 'prog'),
        ('Model choice', 'prog'),
        ('Training the classifier', 'prog'),
        ('Evaluating the classifier', 'fixed'),
    ], 'pr-steps.svg', 'The steps in pattern recognition: data collection, feature choice, model choice, training the classifier, '
       'then evaluating the classifier, after which the process terminates', OUT, rankdir='LR')


def classifier_tree():
    src = f'''digraph {{ bgcolor="white"; pad=0.25; rankdir=TB; nodesep=0.25; ranksep=0.4;
node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.1, fillcolor="#e5e7eb"];
edge [color="{INK}"];
C [label="Classification", fillcolor="#fde68a"];
S [label="Supervised"]; U [label="Unsupervised\\n(clustering)"];
P [label="Probabilistic based"]; G [label="Geometric based"];
D [label="Density based"];
PA [label="Parametric\\nBayesian, multivariate Gaussian,\\nMLC, naive Bayes, decision tree,\\nSVM, minimal distance", fillcolor="#dbeafe"];
NP [label="Non-parametric\\nKNN, kernel density (Parzen),\\nlogistic regression, MLP,\\nneural network", fillcolor="#d1fae5"];
UL [label="ART 1/2/3, fuzzy ART,\\nISODATA, fuzzy C-means,\\nK-means, genetic algorithm"];
C -> S; C -> U; S -> P; S -> G; P -> D; D -> PA; D -> NP; U -> UL;
}}'''
    save_dot(src, 'pr-classifier-tree.svg',
             'The course tree of classifiers: classification splits into supervised and unsupervised; supervised splits into '
             'probabilistic and geometric; probabilistic is density based, which splits into parametric (Bayesian, multivariate '
             'Gaussian, MLC, naive Bayes, decision tree, SVM, minimal distance) and non-parametric (KNN, kernel density or Parzen, '
             'logistic regression, MLP, neural network); unsupervised lists ART, ISODATA, fuzzy C-means, K-means and genetic algorithms', OUT)


def supervised_process():
    src = f'''digraph {{ bgcolor="white"; pad=0.25; rankdir=TB; nodesep=0.35; ranksep=0.3;
node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", penwidth=1.1, fillcolor="#dbeafe", width=2.4];
edge [fontname="{FONT}", fontsize=11, color="{INK}"];
p [label="Problem", fillcolor="#fde68a"]; di [label="Data identification"]; dp [label="Data preprocessing"];
ts [label="Training set"]; cs [label="Classifier selection"]; tr [label="Training"];
ev [label="Evaluation on test data"]; ok [label="Good enough?", shape=diamond, width=1.6, fillcolor="#e5e7eb"];
tu [label="Parameter tuning", fillcolor="#e5e7eb"]; cl [label="Classifier", fillcolor="#d1fae5"];
opt [label="Test options:\\nuse training set\\nsupplied test set\\ncross-validation\\npercentage split", shape=note, fillcolor="#ffffff"];
p -> di -> dp -> ts -> cs -> tr -> ev -> ok; ok -> cl [label=" yes"]; ok -> tu [label=" no"]; tu -> tr;
ev -> opt [style=dashed, arrowhead=none];
{{rank=same; ev; opt}}
}}'''
    save_dot(src, 'pr-supervised-process.svg',
             'The process of supervised classification: problem, data identification, data preprocessing, training set, classifier '
             'selection, training, evaluation on test data using one of four test options, then if good enough the classifier, '
             'otherwise parameter tuning and back to training', OUT)


if __name__ == '__main__':
    check()
    mango_plot()
    density_plot()
    steps_flow()
    classifier_tree()
    supervised_process()
