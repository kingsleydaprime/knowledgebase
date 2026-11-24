"""Draw the planning and scheduling lesson diagrams as small SVG files, and check the lessons' numbers.

    python3 scripts/diagrams/planning_scheduling.py      # run from the vault root

Every worked example and quiz answer in planning-and-scheduling/ that comes from a sum is checked
here with an assert before anything is drawn: the CPM passes (box and arrow diagrams), precedence
relationships, PERT probabilities, crashing tables, resource profiles, priority rules (RAF, SAF,
CAF) and Brooks' algorithm. The sums live in ps_calc.py. Networks are drawn with Graphviz (`dot`,
which must be installed). Output: planning-and-scheduling/images/*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, GRID, PIX, ACCENT, FONT, Svg, save_dot  # noqa: E402
from ps_calc import (close, cpm, paths, critical, aoa, te, var, phi, slope, crash_table,  # noqa: E402
                     caf_table, brooks)

OUT = os.path.join('planning-and-scheduling', 'images')
ORANGE = '#f59e0b'
GREY = '#9ca3af'

FENCE = {'A': (3, []), 'B': (2, ['A']), 'C': (1, ['A']), 'D': (3, ['B']), 'E': (1, ['C']),
         'F': (1, ['D', 'E']), 'G': (2, ['F']), 'H': (1, ['G'])}
FENCE_NAMES = {'A': 'Dig holes', 'B': 'Buy wood', 'C': 'Buy gate', 'D': 'Erect fence', 'E': 'Buy paint',
               'F': 'Erect gate', 'G': 'Paint fence', 'H': 'Paint gate'}
FENCE_WORKERS = {'A': 3, 'B': 2, 'C': 2, 'D': 1, 'E': 2, 'F': 2, 'G': 2, 'H': 1}
CRANEBURG = {(1, 2): 0, (1, 3): 11, (1, 4): 6, (2, 4): 5, (3, 5): 7, (3, 6): 5, (4, 6): 9, (4, 7): 10,
             (4, 8): 12, (5, 6): 2, (6, 8): 8, (6, 9): 12, (7, 8): 4, (8, 9): 8}
SOFTWARE = {'A': (3, []), 'B': (5, []), 'C': (7, []), 'D': (8, ['A']), 'E': (5, ['B']), 'F': (5, ['C']),
            'G': (4, ['E']), 'H': (5, ['F']), 'I': (6, ['D']), 'J': (4, ['G', 'H'])}
PERT_AJ = {'A': (1, 2, 3, []), 'B': (1, 1, 1, ['A']), 'C': (2, 6, 10, ['A']), 'D': (1, 4, 7, ['A']),
           'E': (2, 2, 2, ['B']), 'F': (4, 5, 6, ['C']), 'G': (1, 3, 5, ['D']), 'H': (2, 8, 14, ['C', 'G']),
           'I': (4, 6, 8, ['E']), 'J': (3, 3, 3, ['F', 'I', 'H'])}
SW_CRASH_ACTS = {'A': (5, []), 'B': (3, ['A']), 'C': (2, ['A']), 'D': (2, ['B', 'C']), 'E': (1, ['C']),
                 'F': (4, ['D']), 'G': (4, ['E'])}
SW_CRASH = {'A': (4, 100, 200), 'B': (2, 300, 350), 'C': (1, 200, 325), 'D': (1, 250, 300),
            'E': (1, 400, 400), 'F': (2, 500, 900), 'G': (2, 150, 350)}
TASKS_1920 = {'A': (4, 6, 7, [4, 5]), 'B': (3, 4, 7, [6, 3]), 'C': (2, 3, 4, [4, 5]), 'D': (1, 2, 4, [5, 4]),
              'E': (1, 3, 4, [3, 5]), 'F': (8, 10, 14, [6, 6]), 'G': (3, 3, 3, [5, 4]), 'H': (1, 2, 4, [5, 4])}
PRE_1920 = {'A': [], 'B': [], 'C': ['A'], 'D': ['B'], 'E': ['B'], 'F': [], 'G': ['E', 'F'], 'H': ['C', 'D']}
SMOOTH = {'C': 5, 'E': 6}          # lesson 27: new start days for Buy gate and Buy paint
BROOKS_SMALL = {'A': (2, [], [3]), 'B': (3, [], [2]), 'C': (2, [], [2]), 'D': (1, ['A'], [2])}


def times(r, a):
    v = r[a]
    return v['ES'], v['EF'], v['LS'], v['LF'], v['TF']


def profile(acts, starts, need, T):
    """Workers on site in each day [d, d+1)."""
    return [sum(need[a] for a in acts if starts[a] <= d < starts[a] + acts[a][0]) for d in range(T)]


def precedence_2021():
    """Lesson 12: the forward pass under the 2020/21 relationships. Returns {act: (start, finish)}."""
    d = {'A': 3, 'B': 1, 'C': 2, 'D': 4, 'E': 1, 'F': 1, 'G': 4, 'H': 3}
    s = {'A': 0}
    s['B'] = s['A'] + d['A'] + 2                                  # FS(A,B) = 2
    s['C'] = s['A'] + 4                                           # SS(A,C) = 4
    s['D'] = s['B'] + 2                                           # SS(B,D) = 2
    s['E'] = (s['C'] + 3) - d['E']                                # SF(C,E) = 3
    s['F'] = (s['C'] + d['C'] + 5) - d['F']                       # FF(C,F) = 5
    s['G'] = max(s['D'] + 1, s['E'] + d['E'])                     # SS(D,G) = 1, and E plain
    s['H'] = max((s['F'] + 8) - d['H'], s['G'] + d['G'])          # SF(F,H) = 8, and G plain
    return {a: (s[a], s[a] + d[a]) for a in d}


# ---------- the checks ----------

def check_lessons():
    # 13, 14: the fence
    r, T = cpm(FENCE)
    assert T == 12 and critical(r) == ['A', 'B', 'D', 'F', 'G', 'H']
    assert [r[a]['EF'] for a in 'ABCDEFGH'] == [3, 5, 4, 8, 5, 9, 11, 12]
    assert times(r, 'C') == (3, 4, 6, 7, 3) and times(r, 'E') == (4, 5, 7, 8, 3)
    assert r['C']['FF'] == 0 and r['E']['FF'] == 3
    assert dict(paths(FENCE))['A-C-E-F-G-H'] == 9
    # 13 quiz: P..T; 14 quiz: A..G
    q = {'P': (4, []), 'Q': (1, ['P']), 'R': (5, ['P']), 'S': (3, ['Q']), 'T': (2, ['R', 'S'])}
    r, T = cpm(q)
    assert T == 11 and r['S']['ES'] == 5
    q = {'A': (2, []), 'B': (4, []), 'C': (3, ['A']), 'D': (6, ['A', 'B']), 'E': (2, ['C']),
         'F': (3, ['D', 'E']), 'G': (1, ['F'])}
    r, T = cpm(q)
    assert T == 14 and r['A']['TF'] == 2 and critical(r) == ['B', 'D', 'F', 'G']
    assert sorted(dict(paths(q)).values()) == [11, 12, 14]
    # 12: precedence relationships, and its quiz
    assert cpm({'A': (3, []), 'B': (1, ['A']), 'C': (2, ['A']), 'D': (4, ['B']), 'E': (1, ['C']),
                'F': (1, ['C']), 'G': (4, ['D', 'E']), 'H': (3, ['G', 'F'])})[1] == 15
    p = precedence_2021()
    assert p == {'A': (0, 3), 'B': (5, 6), 'C': (4, 6), 'D': (7, 11), 'E': (6, 7), 'F': (10, 11),
                 'G': (8, 12), 'H': (15, 18)}
    b = (0 + 2, 0 + 2 + 3)                    # SS(A,B) = 2, B 3 days
    c_fin = 4 + 3                             # FF(A,C) = 3
    dd = (b[1] + 1, b[1] + 1 + 3)             # FS(B,D) = 1
    assert c_fin == 7 and max(c_fin, dd[1]) == 9 and (0 + 5) - 2 == 3
    assert cpm({'A': (4, []), 'B': (3, ['A']), 'C': (2, ['A']), 'D': (3, ['B'])})[1] == 10
    # 15: Craneburg, and the quiz network
    early, late, acts, T = aoa(CRANEBURG)
    assert T == 36 and early == {1: 0, 2: 0, 3: 11, 4: 6, 5: 18, 6: 20, 7: 16, 8: 28, 9: 36}
    assert late == {1: 0, 2: 6, 3: 11, 4: 11, 5: 18, 6: 20, 7: 24, 8: 28, 9: 36}
    assert [k for k, v in acts.items() if v['TF'] == 0] == [(1, 3), (3, 5), (5, 6), (6, 8), (8, 9)]
    assert acts[(3, 6)]['TF'] == 4 and acts[(4, 8)]['TF'] == 10
    e2, l2, a2, T2 = aoa({(1, 2): 4, (1, 3): 6, (2, 3): 0, (2, 4): 5, (3, 4): 2, (4, 5): 3})
    assert T2 == 12 and l2[3] == 7 and a2[(1, 3)]['TF'] == 1
    # 16: software network, and the quiz
    r, T = cpm(SOFTWARE)
    assert T == 21 and critical(r) == ['C', 'F', 'H', 'J']
    assert [r[a]['TF'] for a in 'ABCDEFGHIJ'] == [4, 3, 0, 4, 3, 0, 3, 0, 4, 0]
    q = {'K': (4, []), 'L': (6, []), 'M': (5, ['K']), 'N': (3, ['L']), 'O': (7, ['M', 'N']), 'P': (2, ['N'])}
    r, T = cpm(q)
    assert T == 16 and r['P']['TF'] == 5
    # 17 to 20: PERT
    assert close(te(2, 3, 7), 3.5) and close(var(2, 7), (5 / 6) ** 2)
    assert te(2, 5, 14) == 6 and var(2, 14) == 4 and te(4, 5, 9) == 5.5 and te(3, 4, 11) == 5
    acts = {k: (te(a, m, b), p) for k, (a, m, b, p) in PERT_AJ.items()}
    r, T = cpm(acts)
    assert close(T, 20) and critical(r) == ['A', 'D', 'G', 'H', 'J']
    vp = sum(var(PERT_AJ[k][0], PERT_AJ[k][2]) for k in critical(r))
    sd = math.sqrt(vp)
    assert close(vp, 5.5556, 1e-3) and close(sd, 2.357, 1e-3)
    assert close(phi((21 - 20) / sd), 0.66, 0.01) and close(phi((24 - 20) / sd), 0.955, 1e-3)
    assert close(phi(1), 0.8413, 1e-4) and close(1 - phi(1), 0.1587, 1e-4) and math.sqrt(9 + 16) == 5
    assert close(20 + 1.64 * sd, 23.9, 0.05)
    elib = {'A-C-F-I-K': (20, 5.222), 'A-D-F-I-K': (22, 6.111), 'B-E-G-H-J-K': (23, 4.0), 'B-E-G-I-K': (21, 4.333)}
    probs = [phi((25 - m) / math.sqrt(v)) for m, v in elib.values()]
    assert close(math.prod(probs), 0.716, 2e-3)
    assert close(phi(1.5) * phi(2), 0.912, 1e-3) and close(40 + 1.64 * 3, 44.92)
    cp = {'A': (80, 100, 150), 'B': (40, 50, 75), 'C': (200, 200, 200), 'D': (50, 60, 60), 'E': (30, 40, 60)}
    m = sum(te(*v) for v in cp.values())
    vv = sum(var(v[0], v[2]) for v in cp.values())
    assert close(m, 457.5) and close(vv, 197.92, 0.01)
    assert close(phi((500 - m) / math.sqrt(vv)) - phi((450 - m) / math.sqrt(vv)), 0.70, 0.01)
    assert te(10, 16, 28) == 17 and var(10, 28) == 9 and close(2 * phi(1) - 1, 0.6826, 1e-4)
    t = 1.7                                    # any t: the parameter version
    a, mm, b = t * t - t, t, t * t + t
    assert close(te(a, mm, b), (t * t + 2 * t) / 3) and close((b - a) / 6, t / 3)
    assert close((t * t + 2 * t - te(a, mm, b)) / ((b - a) / 6), 2 * (t + 2))
    assert close(te(t, 2 * t, 5 * t), 7 * t / 3) and close((5 * t - t) / 6, 2 * t / 3)
    # 22 to 24: crashing
    assert slope(6, 4, 800, 1400) == 300 and slope(3, 1, 30000, 70000) == 20000
    ad = {'A': (4, []), 'B': (8, ['A']), 'C': (5, ['A']), 'D': (5, ['C'])}
    rows = crash_table(ad, {'A': (2, 4000, 14000), 'B': (5, 1000, 11000), 'C': (4, 4000, 18000),
                            'D': (3, 2000, 13000)}, 3500)
    assert rows[0] == (14, 11000, 60000, '') and min(r[2] for r in rows) == 60000 and rows[1][2] == 61500
    ad = {'A': (3, []), 'B': (7, ['A']), 'C': (4, ['A']), 'D': (5, ['C'])}
    cr = {'A': (1, 4000, 14000), 'B': (3, 1000, 11000), 'C': (2, 4000, 18000), 'D': (2, 2000, 13000)}
    assert [round(slope(ad[k][0], *cr[k])) for k in 'ABCD'] == [5000, 2500, 7000, 3667]
    rows = crash_table(ad, cr, 4500)
    assert rows[0][2] == 65000 and round(rows[1][2]) == 64167
    best = min(rows, key=lambda r: r[2])
    assert best[0] == 10 and round(best[2]) == 63333
    xyz = crash_table({'X': (5, []), 'Y': (4, ['X']), 'Z': (6, ['X'])},
                      {'X': (3, 1000, 1600), 'Y': (3, 500, 700), 'Z': (4, 900, 1700)}, 350)
    assert xyz[0][2] == 6250 and min(xyz, key=lambda r: r[2])[:3] == (9, 3000, 6150)
    rows = crash_table(SW_CRASH_ACTS, SW_CRASH, 100)
    assert [(d, round(dc), round(tc)) for d, dc, tc, _ in rows] == [
        (14, 1900, 3300), (13, 1950, 3250), (12, 2000, 3200), (11, 2100, 3200), (10, 2400, 3400), (9, 2700, 3600)]
    assert sum(c[2] for c in SW_CRASH.values()) == 2825 and 1800 + 50 * 12 == 2400
    # 25, 27: resource profiles
    r, T = cpm(FENCE)
    early = {a: r[a]['ES'] for a in FENCE}
    prof = profile(FENCE, early, FENCE_WORKERS, T)
    assert prof == [3, 3, 3, 4, 4, 1, 1, 1, 2, 2, 2, 1] and max(prof) == 4 and sum(prof) == 27
    smooth = dict(early, **SMOOTH)
    assert all(smooth[a] <= r[a]['LS'] for a in SMOOTH) and smooth['E'] >= smooth['C'] + FENCE['C'][0]
    prof2 = profile(FENCE, smooth, FENCE_WORKERS, T)
    assert prof2 == [3, 3, 3, 2, 2, 3, 3, 1, 2, 2, 2, 1] and max(prof2) == 3 and sum(prof2) == 27
    assert 5 * 8 + 4 * 6 + 6 * 4 == 88 and 4 * 6 + 3 * 4 + 5 * 6 + 6 * 8 == 114
    # 28, 29: priority rules
    assert 4 * 3 == 12 and 3 / 4 == 0.75 and 0.5 * 4 + 0.5 * 12 == 8 and close(0.3 * 4 + 0.7 * 12, 9.6)
    assert close((1 / 4) * (2 / 4 + 3 / 6), 0.25) and close(4 + (4 / 3) / 4, 4.3333, 1e-4)
    assert 0.5 * 5 + 0.5 * 15 == 10 and close((1 / 5) * (4 / 8 + 5 / 10), 0.2) and close(6 + 0.6 / 6, 6.1)
    c = caf_table(TASKS_1920, [8, 10], 0.6)
    want = {'A': (0.171, 36.2, 46.8, 40.5, 48.1), 'B': (0.242, 51.2, 54.3, 52.5, 62.3),
            'C': (0.333, 70.5, 38.6, 57.7, 68.6), 'D': (0.473, 100.0, 60.5, 84.2, 100.0),
            'E': (0.309, 65.3, 51.9, 60.0, 71.2), 'F': (0.131, 27.6, 71.0, 45.0, 53.4),
            'G': (0.342, 72.2, 14.5, 49.1, 58.4), 'H': (0.473, 100.0, 60.5, 84.2, 100.0)}
    for k, (raf, sraf, ssaf, caf, scaf) in want.items():
        v = c[k]
        assert close(v['RAF'], raf, 6e-4) and close(v['sRAF'], sraf, 0.06) and close(v['sSAF'], ssaf, 0.06)
        assert close(v['CAF'], caf, 0.06) and close(v['sCAF'], scaf, 0.06), k
    assert ''.join(sorted(c, key=lambda k: -c[k]['sCAF'])) == 'DHECBGFA'
    q = caf_table({'P': (2, 3, 10, [2, 3]), 'Q': (4, 4, 4, [4, 1])}, [4, 6], 0.5)
    assert close(q['P']['sRAF'], 85.7143, 1e-3) and close(q['P']['sSAF'], 100) and close(q['P']['CAF'], 92.857, 1e-3)
    assert close(q['Q']['sCAF'], 80.769, 1e-3)
    # 30, 31: Brooks
    s = brooks(BROOKS_SMALL, [4], {'A': 4, 'B': 3, 'C': 2, 'D': 1})
    assert s == {'A': (0, 2), 'B': (2, 5), 'C': (2, 4), 'D': (4, 5)}
    assert cpm({k: (v[0], v[1]) for k, v in BROOKS_SMALL.items()})[1] == 3
    s = brooks({'P': (3, [], [4]), 'Q': (2, [], [3]), 'R': (3, [], [1])}, [5], {'P': 3, 'Q': 2, 'R': 1})
    assert max(f for _, f in s.values()) == 5
    bt = {k: (c[k]['t'], PRE_1920[k], TASKS_1920[k][3]) for k in TASKS_1920}
    s = brooks(bt, [8, 10], {k: c[k]['sCAF'] for k in c})
    want = {'B': (0, 4.33), 'D': (4.33, 6.50), 'E': (4.33, 7.17), 'A': (6.50, 12.33), 'C': (12.33, 15.33),
            'H': (15.33, 17.50), 'F': (17.50, 27.83), 'G': (27.83, 30.83)}
    for k, (st, fi) in want.items():
        assert close(s[k][0], st, 0.01) and close(s[k][1], fi, 0.01), k
    assert close(cpm({k: (c[k]['t'], PRE_1920[k]) for k in c})[1], 13.33, 0.01)
    # 32, 35: scoring and earned value
    sc = {'Estate': (0.8, 10, 5), 'Hospital': (0.6, 12, 6), 'School': (0.9, 6, 3), 'Factory': (0.5, 15, 8)}
    score = {k: (p + 2 * pay) / cost for k, (p, pay, cost) in sc.items()}
    assert [round(score[k], 2) for k in ('Estate', 'Hospital', 'School', 'Factory')] == [4.16, 4.1, 4.3, 3.81]
    assert close((0.7 + 18) / 4, 4.675)
    assert 48 - 60 == -12 and 48 - 54 == -6 and close(48 / 60, 0.8) and close(48 / 54, 0.889, 1e-3)
    assert 90 - 80 == 10 and 90 - 100 == -10 and close(90 / 100, 0.9)
    print('all lesson numbers check out')


# ---------- drawing helpers ----------

class Plot:
    """Data axes inside an Svg: x from x0 to x1 maps to [left, left + w], y to [top + h, top]."""

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
        if ylabel:
            s.add(f'<text x="{self.left - 40:.1f}" y="{self.top + self.h / 2:.1f}" font-size="12" fill="{INK}" '
                  f'text-anchor="middle" font-family="system-ui, sans-serif" '
                  f'transform="rotate(-90 {self.left - 40:.1f} {self.top + self.h / 2:.1f})">{ylabel}</text>')

    def curve(self, pts, color, width=2.5, dash=None):
        d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in (self.P(*p) for p in pts))
        self.s.path(d, color, width=width, dash=dash)


def dot_graph(body, name, title, rankdir='LR', extra=''):
    src = (f'digraph {{ bgcolor="white"; pad=0.25; rankdir={rankdir}; nodesep=0.35; ranksep=0.45; {extra}\n'
           f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", fillcolor="#dbeafe", '
           f'color="{INK}", penwidth=1.2];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];\n' + '\n'.join(body) + '\n}')
    save_dot(src, name, title, OUT)


def aon(acts, name, title, labels=None, crit=()):
    """Activity-on-node network with Start and End nodes. labels: {act: node label}."""
    body = ['S [label="Start", fillcolor="#e5e7eb"];', 'E_ [label="End", fillcolor="#e5e7eb"];']
    succ = {a: [b for b, (_, p) in acts.items() if a in p] for a in acts}
    for a, (d, pre) in acts.items():
        lab = labels[a] if labels else f'{a}  {d:g}'
        fill = '#fde68a' if a in crit else '#dbeafe'
        pen = f', color="{ORANGE}", penwidth=2.2' if a in crit else ''
        body.append(f'{a} [label="{lab}", fillcolor="{fill}"{pen}];')
        if not pre:
            body.append(f'S -> {a};')
        for p in pre:
            col = f' [color="{ORANGE}", penwidth=2.2]' if a in crit and p in crit else ''
            body.append(f'{p} -> {a}{col};')
        if not succ[a]:
            body.append(f'{a} -> E_;')
    dot_graph(body, name, title)


def aoa_graph(arrows, name, title, names=None, dummies=(), crit=(), event_labels=None):
    """arrows: {(i, j): label}. dummies: event pairs drawn dashed. crit: event pairs drawn orange."""
    body = ['node [shape=circle, style="filled", fillcolor="#ffffff", width=0.45, fixedsize=false];']
    events = sorted({e for ij in arrows for e in ij})
    for e in events:
        lab = event_labels[e] if event_labels else str(e)
        body.append(f'n{e} [label="{lab}"];')
    for (i, j), lab in arrows.items():
        attrs = [f'label=" {lab} "']
        if (i, j) in dummies:
            attrs.append('style=dashed')
        if (i, j) in crit:
            attrs.append(f'color="{ORANGE}", penwidth=2.4')
        body.append(f'n{i} -> n{j} [{", ".join(attrs)}];')
    dot_graph(body, name, title)


def bars(rows, name, title, tmax, step=1, crit=(), floats=None, marker=None, unit='days', w=620):
    """rows: [(label, start, finish)]. floats: {label: float end}. marker: (x, text)."""
    n = len(rows)
    s = Svg(w, 70 + 34 * n + 40, title)
    p = Plot(s, 130, 24, w - 170, 34 * n, 0, tmax, 0, n)
    t = 0
    while t <= tmax + 1e-9:
        x, _ = p.P(t, 0)
        s.line(x, p.top, x, p.top + p.h, color=GRID, width=0.8)
        s.text(x, p.top + p.h + 16, f'{t:g}', size=11, color='#374151')
        t += step
    s.line(p.left, p.top + p.h, p.left + p.w, p.top + p.h, width=1.5)
    s.text(p.left + p.w / 2, p.top + p.h + 36, f'time ({unit})', size=12)
    for i, (lab, st, fi) in enumerate(rows):
        yc = p.top + 34 * i + 17
        s.text(p.left - 10, yc + 4, lab, size=12, anchor='end')
        x0, _ = p.P(st, 0)
        x1, _ = p.P(fi, 0)
        key = lab.split()[0]
        s.rect(x0, yc - 9, x1 - x0, 18, ORANGE if key in crit else PIX)
        if floats and key in floats:
            xf, _ = p.P(floats[key], 0)
            s.line(x1, yc, xf, yc, color=INK, width=1.5)
            s.line(xf, yc - 5, xf, yc + 5, color=INK, width=1.5)
    if marker:
        xm, _ = p.P(marker[0], 0)
        s.line(xm, p.top - 6, xm, p.top + p.h, color=TRUE_RED, width=1.8, dash='5,4')
        s.text(xm + 4, p.top - 8, marker[1], size=11, color=TRUE_RED, anchor='start')
    s.save(name, OUT)


TRUE_RED = '#dc2626'


def histogram(ax_profiles, name, title, ymax=5):
    """ax_profiles: [(caption, profile, highlight_days)]. One histogram per caption, stacked."""
    k = len(ax_profiles)
    s = Svg(620, 40 + k * 190, title)
    for i, (cap, prof, hi) in enumerate(ax_profiles):
        top = 34 + i * 190
        p = Plot(s, 70, top, 510, 120, 0, len(prof), 0, ymax)
        p.axes(range(0, len(prof) + 1, 1), range(0, ymax + 1), 'day', 'workers')
        s.text(p.left + p.w / 2, top - 12, cap, size=13, weight='bold')
        for d, v in enumerate(prof):
            x0, y0 = p.P(d, v)
            x1, _ = p.P(d + 1, 0)
            s.rect(x0 + 1, y0, x1 - x0 - 2, p.top + p.h - y0, ORANGE if d in hi else PIX, opacity=0.9)
    s.save(name, OUT)


# ---------- the diagrams ----------

def level_of_activity():
    s = Svg(700, 330, 'Level of activity of the five process groups across the project')
    p = Plot(s, 70, 30, 430, 230, 0, 10, 0, 1.0)
    p.axes([], [], 'time (project life)', 'level of activity')
    groups = [('Initiating', 0.9, 0.6, 0.35, '#6b7280'), ('Planning', 2.6, 1.3, 0.55, PIX),
              ('Executing', 5.6, 1.6, 0.95, ACCENT), ('Monitoring and', 5.4, 2.4, 0.5, ORANGE),
              ('Closing', 9.2, 0.6, 0.35, '#7c3aed')]
    for i, (lab, mu, sd, hgt, col) in enumerate(groups):
        pts = [(x / 20, hgt * math.exp(-((x / 20 - mu) / sd) ** 2 / 2)) for x in range(0, 201)]
        p.curve(pts, col, width=2.6)
        y = 60 + 34 * i
        s.line(520, y - 4, 548, y - 4, color=col, width=3)
        s.text(556, y, lab, size=12, color=col, anchor='start', weight='bold')
        if lab == 'Monitoring and':
            s.text(556, y + 15, 'Controlling', size=12, color=col, anchor='start', weight='bold')
    s.save('ps-level-of-activity.svg', OUT)


def wbs_fence():
    body = ['P [label="Fence and gate project", fillcolor="#e5e7eb"];',
            'F1 [label="Fence"]; G1 [label="Gate"]; P1 [label="Painting"];', 'P -> F1; P -> G1; P -> P1;']
    groups = {'F1': 'ABD', 'G1': 'CF', 'P1': 'EGH'}
    for g, acts in groups.items():
        for a in acts:
            body.append(f'{a} [label="{a} {FENCE_NAMES[a]}", fillcolor="#d1fae5"];')
            body.append(f'{g} -> {a};')
    dot_graph(body, 'ps-wbs-fence.svg',
              'A work breakdown structure tree: the Fence and gate project at the top splits into Fence, Gate and '
              'Painting; Fence holds A Dig holes, B Buy wood and D Erect fence; Gate holds C Buy gate and F Erect '
              'gate; Painting holds E Buy paint, G Paint fence and H Paint gate', rankdir='TB')


def fence_networks():
    labels = {a: f'{a} {FENCE_NAMES[a]}\\n{d} day{"s" if d != 1 else ""}' for a, (d, _) in FENCE.items()}
    aon(FENCE, 'ps-aon-fence.svg', 'The fence and gate as an activity-on-node diagram', labels=labels)
    arrows = {(1, 2): 'A 3', (2, 3): 'B 2', (2, 4): 'C 1', (3, 5): 'D 3', (4, 5): 'E 1', (5, 6): 'F 1',
              (6, 7): 'G 2', (7, 8): 'H 1'}
    aoa_graph(arrows, 'ps-aoa-fence.svg', 'The fence and gate as an activity-on-arrow diagram')
    q = {'K': (2, []), 'L': (4, ['K']), 'M': (3, ['K']), 'N': (1, ['L']), 'O': (2, ['M', 'N'])}
    aon(q, 'ps-aon-quiz.svg', 'The quiz project K to O as an activity-on-node diagram')
    r, T = cpm(FENCE)
    fwd = {a: f'{a} {FENCE_NAMES[a]} ({d})\\nES {r[a]["ES"]}  EF {r[a]["EF"]}' for a, (d, _) in FENCE.items()}
    aon(FENCE, 'ps-fence-forward.svg', 'The fence network after the forward pass', labels=fwd)
    full = {a: f'{a} {FENCE_NAMES[a]} ({d})\\nES {r[a]["ES"]}  EF {r[a]["EF"]}\\nLS {r[a]["LS"]}  LF {r[a]["LF"]}'
               f'\\nfloat {r[a]["TF"]}' for a, (d, _) in FENCE.items()}
    aon(FENCE, 'ps-fence-cpm.svg', 'The fence network with all four times, float and the critical path',
        labels=full, crit=critical(r))


def dummies():
    body = ['node [shape=circle, style="filled", fillcolor="#ffffff"];',
            'subgraph cluster_w { label="Wrong: both are 2-3"; fontname="' + FONT + '"; color="#dc2626";',
            'w2 [label="2"]; w3 [label="3"];',
            'w2 -> w3 [label=" B "]; w2 -> w3 [label=" C "]; }',
            'subgraph cluster_r { label="Right: B is 2-4, C is 2-3"; fontname="' + FONT + '"; color="#059669";',
            'r2 [label="2"]; r3 [label="3"]; r4 [label="4"];',
            'r2 -> r4 [label=" B "]; r2 -> r3 [label=" C "]; r3 -> r4 [label=" dummy ", style=dashed]; }']
    dot_graph(body, 'ps-dummy-unique.svg', 'Two ways to draw B and C, wrong and right, with a dummy')
    aoa_graph({(1, 2): 'P', (1, 3): 'Q', (2, 3): 'dummy', (2, 4): 'R', (3, 5): 'S'}, 'ps-dummy-logic.svg',
              'P, Q, R and S with a dummy from event 2 to event 3', dummies={(2, 3)})
    aoa_graph({(1, 2): 'Y', (1, 3): 'X', (2, 3): 'dummy', (2, 4): 'Z', (3, 5): 'W'}, 'ps-dummy-quiz.svg',
              'X, Y, Z and W with a dummy from event 2 to event 3', dummies={(2, 3)})


def precedence_types():
    s = Svg(620, 330, 'The four precedence relationships drawn as pairs of bars')
    cases = [('Finish to start (FS)', (0, 3), (3, 6), 3, 3), ('Start to start (SS)', (0, 3), (0, 3), 0, 0),
             ('Finish to finish (FF)', (0, 3), (1, 3), 3, 3), ('Start to finish (SF)', (2, 5), (0, 2), 2, 2)]
    for i, (lab, a, b, xa, xb) in enumerate(cases):
        col, row = i % 2, i // 2
        left, top = 30 + col * 300, 30 + row * 150
        s.text(left + 130, top, lab, size=13, weight='bold')
        sc = 40
        s.rect(left + 20 + a[0] * sc, top + 20, (a[1] - a[0]) * sc, 22, PIX)
        s.text(left + 20 + a[0] * sc + (a[1] - a[0]) * sc / 2, top + 36, 'A', size=12, color='#ffffff', weight='bold')
        s.rect(left + 20 + b[0] * sc, top + 70, (b[1] - b[0]) * sc, 22, ACCENT)
        s.text(left + 20 + b[0] * sc + (b[1] - b[0]) * sc / 2, top + 86, 'B', size=12, color='#ffffff', weight='bold')
        s.line(left + 20 + xa * sc, top + 42, left + 20 + xb * sc, top + 70, color=ORANGE, width=2.4)
        s.circle(left + 20 + xb * sc, top + 70, 4, ORANGE)
    s.save('ps-precedence-types.svg', OUT)


def precedence_example():
    p = precedence_2021()
    rows = [(a, *p[a]) for a in 'ABCDEFGH']
    bars(rows, 'ps-precedence-example.svg', 'The 2020/21 schedule with precedence relationships', 18,
         step=2, crit='ACFH')


def craneburg():
    early, late, acts, T = aoa(CRANEBURG)
    labels = {e: f'{e}\\n{early[e]} | {late[e]}' for e in early}
    arrows = {ij: f'{d}' for ij, d in CRANEBURG.items()}
    crit = {ij for ij, v in acts.items() if v['TF'] == 0}
    aoa_graph(arrows, 'ps-aoa-craneburg.svg', 'The Craneburg arrow network with event times',
              dummies={(1, 2)}, crit=crit, event_labels=labels)


def software_network():
    r, T = cpm(SOFTWARE)
    aon(SOFTWARE, 'ps-software-network.svg', 'The 2024/25 software project as an AON diagram', crit=critical(r))


def beta_curve():
    a, m, b = 2, 3, 7
    s = Svg(620, 300, 'A skewed beta curve for erecting the fence with a = 2, m = 3, b = 7')
    p = Plot(s, 60, 30, 520, 200, 1, 8, 0, 1.05)
    p.axes(range(1, 9), [], 'time (days)', '')
    # a PERT-beta shape with mode m on [a, b]
    al = 1 + 4 * (m - a) / (b - a)
    be = 1 + 4 * (b - m) / (b - a)
    xs = [a + (b - a) * i / 200 for i in range(201)]
    ys = [((x - a) / (b - a)) ** (al - 1) * ((b - x) / (b - a)) ** (be - 1) for x in xs]
    top = max(ys)
    p.curve([(x, y / top) for x, y in zip(xs, ys)], PIX, width=2.8)
    for x, lab, col, h, anc in ((a, 'a = 2', INK, 1.0, 'middle'), (m, 'm = 3', INK, 1.0, 'end'),
                                (b, 'b = 7', INK, 1.0, 'middle'), (te(a, m, b), 't_e = 3.5', ORANGE, 0.45, 'start')):
        px, py0 = p.P(x, 0)
        _, py1 = p.P(x, h)
        s.line(px, py0, px, py1, color=col, width=1.4, dash='4,4')
        s.text(px + (6 if anc == 'start' else 0), py1 - 6, lab, size=12, color=col, weight='bold', anchor=anc)
    s.save('ps-beta.svg', OUT)


def normal_21():
    mu, sd = 20, math.sqrt(sum(var(PERT_AJ[k][0], PERT_AJ[k][2]) for k in 'ADGHJ'))
    s = Svg(620, 300, 'A normal curve for the project time with the area below 21 days shaded')
    p = Plot(s, 60, 30, 520, 200, 12, 28, 0, 0.19)
    p.axes(range(12, 29, 2), [], 'project time (days)', '')
    f = lambda x: math.exp(-((x - mu) / sd) ** 2 / 2) / (sd * math.sqrt(2 * math.pi))  # noqa: E731
    xs = [12 + 16 * i / 300 for i in range(301)]
    shade = [(x, f(x)) for x in xs if x <= 21]
    pts = [p.P(x, y) for x, y in shade]
    d = f'M {p.P(12, 0)[0]:.1f} {p.P(12, 0)[1]:.1f} ' + ' '.join(f'L {x:.1f} {y:.1f}' for x, y in pts)
    d += f' L {p.P(21, 0)[0]:.1f} {p.P(21, 0)[1]:.1f} Z'
    s.path(d, 'none', fill='#bfdbfe')
    p.curve([(x, f(x)) for x in xs], PIX, width=2.6)
    for x, lab in ((20, 'T_e = 20'), (21, 'T = 21')):
        px, py0 = p.P(x, 0)
        _, py1 = p.P(x, f(x))
        s.line(px, py0, px, py1, color=ORANGE if x == 21 else INK, width=1.5, dash='4,4')
        s.text(px + (30 if x == 21 else -30), py1 - 6, lab, size=12, weight='bold')
    s.text(p.P(17.5, 0.06)[0], p.P(17.5, 0.06)[1], f'P = {phi(1 / sd):.2f}', size=14, color=INK, weight='bold')
    s.save('ps-normal-21.svg', OUT)


def time_cost_u():
    s = Svg(620, 320, 'Direct, indirect and total cost against project duration')
    p = Plot(s, 70, 30, 500, 220, 0, 10, 0, 10)
    p.axes([], [], 'project duration (crash on the left, normal on the right)', 'cost')
    xs = [1 + 8 * i / 100 for i in range(101)]
    direct = [(x, 1.0 + 6.0 * math.exp(-(x - 1) / 2.2)) for x in xs]
    indirect = [(x, 0.45 * x) for x in xs]
    total = [(x, d + i) for (x, d), (_, i) in zip(direct, indirect)]
    p.curve(direct, PIX)
    p.curve(indirect, ACCENT)
    p.curve(total, ORANGE, width=3)
    best = min(total, key=lambda t: t[1])
    bx, by = p.P(*best)
    s.circle(bx, by, 5, ORANGE, '#ffffff')
    s.text(bx, by - 12, 'optimum (lowest total)', size=12, weight='bold')
    for pts, lab, col in ((direct, 'direct', PIX), (indirect, 'indirect', ACCENT), (total, 'total', ORANGE)):
        x, y = p.P(*pts[-1])
        s.text(x + 6, y + 4, lab, size=12, color=col, anchor='start', weight='bold')
    s.save('ps-time-cost-u.svg', OUT)


def crash_software():
    rows = crash_table(SW_CRASH_ACTS, SW_CRASH, 100)
    s = Svg(620, 330, 'Total, direct and indirect cost against duration for the software project')
    p = Plot(s, 80, 30, 470, 230, 9, 14, 0, 4000)
    p.axes(range(9, 15), range(0, 4001, 1000), 'duration (days)', "cost (N'000)")
    dur = [r[0] for r in rows]
    for vals, lab, col in (([r[1] for r in rows], 'direct', PIX), ([100 * d for d in dur], 'indirect', ACCENT),
                           ([r[2] for r in rows], 'total', ORANGE)):
        p.curve(list(zip(dur, vals)), col)
        for d, v in zip(dur, vals):
            x, y = p.P(d, v)
            s.circle(x, y, 3.5, col, '#ffffff')
        x, y = p.P(dur[0], vals[0])
        s.text(x + 8, y + 4, lab, size=12, color=col, anchor='start', weight='bold')
    x, y = p.P(11.5, 3200)
    s.text(x, y - 14, 'minimum 3,200 at 11 and 12 days', size=12, weight='bold')
    s.save('ps-crash-software.svg', OUT)


def fence_profiles():
    r, T = cpm(FENCE)
    early = {a: r[a]['ES'] for a in FENCE}
    prof = profile(FENCE, early, FENCE_WORKERS, T)
    histogram([('Fence at earliest start', prof, [3, 4])], 'ps-fence-loading.svg',
              'Resource loading histogram for the fence at earliest start')
    prof2 = profile(FENCE, dict(early, **SMOOTH), FENCE_WORKERS, T)
    histogram([('Before smoothing: peak 4', prof, [3, 4]), ('After smoothing: peak 3, still 12 days', prof2, [5, 6])],
              'ps-fence-smoothed.svg', 'Fence resource histograms before and after smoothing')


def brooks_charts():
    s = brooks(BROOKS_SMALL, [4], {'A': 4, 'B': 3, 'C': 2, 'D': 1})
    rows = [(f'{a} ({BROOKS_SMALL[a][2][0]} workers)', *s[a]) for a in 'ABCD']
    bars(rows, 'ps-brooks-small.svg', 'The four-activity Brooks example with a limit of 4 workers', 5,
         marker=(3, 'unconstrained finish'))
    c = caf_table(TASKS_1920, [8, 10], 0.6)
    bt = {k: (c[k]['t'], PRE_1920[k], TASKS_1920[k][3]) for k in TASKS_1920}
    s = brooks(bt, [8, 10], {k: c[k]['sCAF'] for k in c})
    rows = [(k, *s[k]) for k in sorted(s, key=lambda k: s[k][0])]
    bars(rows, 'ps-brooks-2019.svg', 'The resource-constrained 2019/20 schedule', 32, step=4,
         marker=(13.33, 'unconstrained 13.33'), unit='weeks')


def gantt_charts():
    r, T = cpm(FENCE)
    rows = [(f'{a} {FENCE_NAMES[a]}', r[a]['ES'], r[a]['EF']) for a in 'ABCDEFGH']
    bars(rows, 'ps-gantt-fence.svg', 'A bar chart of the fence with float lines', 12, crit=critical(r),
         floats={a: r[a]['LF'] for a in FENCE if r[a]['TF'] > 0})
    q = {'K': (2, []), 'L': (4, ['K']), 'M': (3, ['K']), 'N': (1, ['L']), 'O': (2, ['M', 'N'])}
    r, T = cpm(q)
    assert T == 9 and r['M']['TF'] == 2 and r['M']['LF'] == 7
    bars([(a, r[a]['ES'], r[a]['EF']) for a in q], 'ps-gantt-quiz.svg', 'A bar chart of the quiz project K to O',
         9, crit=critical(r), floats={a: r[a]['LF'] for a in q if r[a]['TF'] > 0})


def line_of_balance():
    s = Svg(620, 320, 'A line-of-balance chart for a 10-house estate')
    p = Plot(s, 70, 30, 480, 220, 0, 24, 0, 10)
    p.axes(range(0, 25, 4), range(0, 11, 2), 'time (weeks)', 'houses completed')
    trades = [('foundations', 0, 1.0, PIX), ('walls', 3, 0.8, ACCENT), ('roofing', 8, 0.9, ORANGE)]
    for lab, start, rate, col in trades:
        end = start + 10 / rate
        p.curve([(start, 0), (end, 10)], col, width=3)
        x, y = p.P(end, 10)
        s.text(x - 4, y - 8, lab, size=12, color=col, weight='bold', anchor='end' if lab != 'roofing' else 'start')
    s.save('ps-line-of-balance.svg', OUT)


def time_location():
    s = Svg(620, 320, 'A time-location chart for a 10 kilometre road')
    p = Plot(s, 70, 30, 480, 220, 0, 10, 0, 20)
    p.axes(range(0, 11, 2), range(0, 21, 4), 'position along the road (km)', 'time (weeks)')
    crews = [('clearing', 0, 0.8, PIX), ('earthworks', 3, 1.2, ACCENT), ('surfacing', 8, 1.0, ORANGE)]
    for lab, start, wpk, col in crews:
        p.curve([(0, start), (10, start + 10 * wpk)], col, width=3)
        x, y = p.P(10, start + 10 * wpk)
        s.text(x - 6, y - 6, lab, size=12, color=col, weight='bold', anchor='end')
    s.save('ps-time-location.svg', OUT)


if __name__ == '__main__':
    check_lessons()
    level_of_activity()
    wbs_fence()
    fence_networks()
    dummies()
    precedence_types()
    precedence_example()
    craneburg()
    software_network()
    beta_curve()
    normal_21()
    time_cost_u()
    crash_software()
    fence_profiles()
    brooks_charts()
    gantt_charts()
    line_of_balance()
    time_location()
