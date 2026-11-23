"""Draw the engineering economics lesson diagrams as small SVG files, and check the lessons' numbers.

    python3 scripts/diagrams/engineering_economics.py      # run from the vault root

Every worked example and quiz answer in engineering-economics/ that comes from a sum is
checked here with an assert before anything is drawn, so a lesson's numbers can never
drift from the arithmetic. The graphs are computed from the same functions. The capital
budgeting flowchart is drawn with Graphviz (`dot`, which must be installed).
Output: engineering-economics/images/*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, GRID, PIX, TRUE, ACCENT, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('engineering-economics', 'images')
ORANGE = '#f59e0b'
GREY = '#6b7280'


# ---------- the interest factors (lessons 06 and 07) ----------

def pf(i, n): return (1 + i) ** -n
def fp(i, n): return (1 + i) ** n
def pa(i, n): return ((1 + i) ** n - 1) / (i * (1 + i) ** n)
def ap(i, n): return 1 / pa(i, n)
def fa(i, n): return ((1 + i) ** n - 1) / i
def af(i, n): return 1 / fa(i, n)
def ag(i, n): return 1 / i - n / ((1 + i) ** n - 1)
def pg(i, n): return ((1 + i) ** n - 1 - n * i) / (i * i * (1 + i) ** n)


def close(a, b, tol):
    return abs(a - b) <= tol


def npv(rate, flows):
    """flows[0] is at time 0."""
    return sum(cf * pf(rate, t) for t, cf in enumerate(flows))


def irr(flows, lo=0.0, hi=1.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(mid, flows) > 0:
            lo = mid
        else:
            hi = mid
    return mid


# ---------- depreciation (lessons 16 to 18) ----------

def straight_line(fc, sv, n):
    return [(fc - sv) / n] * n


def double_declining(fc, sv, n):
    k, bv, out = 2 / n, fc, []
    for _ in range(n):
        d = min(k * bv, bv - sv)          # never below salvage value
        bv -= d
        out.append(d)
    return out


def syd(fc, sv, n):
    total = n * (n + 1) / 2
    return [(fc - sv) * (n - t) / total for t in range(n)]


def book_values(fc, charges):
    bvs, bv = [fc], fc
    for d in charges:
        bv -= d
        bvs.append(bv)
    return bvs


# ---------- risk (lessons 23 and 24) ----------

def mean_sd(values, probs):
    m = sum(p * x for p, x in zip(probs, values))
    return m, math.sqrt(sum(p * (x - m) ** 2 for p, x in zip(probs, values)))


PRICING = {'Raise price': [25, 15, -10], 'No change': [15, 20, -5], 'Lower price': [15, 0, 5]}
PLANT = {'Big': [40, 20, -15], 'Medium': [25, 18, 0], 'Small': [12, 10, 6]}


def max_regret(table):
    best = [max(row[j] for row in table.values()) for j in range(3)]
    return {k: max(b - x for b, x in zip(best, row)) for k, row in table.items()}


# ---------- production (lesson 32) ----------

def tp(L): return 10 * L * L - L ** 3
def mp_cont(L): return 20 * L - 3 * L * L
def ap_cont(L): return 10 * L - L * L


# ---------- the lessons' worked numbers ----------

def check_lessons():
    # 02, 03: cost equation and cost sheets.
    assert 10 + 5 * 20 == 110 and 25 + 8 * 40 == 345
    assert 4500 / 300 == 15 and 2430 - 2400 == 30 and 1008 - 1000 == 8
    assert (7000 + 2800, 9800 + 2600, 12400 + 1000, 13400 + 900, 20000 - 14300) == (9800, 12400, 13400, 14300, 5700)
    assert (12000 + 5000, 17000 + 3500, 20500 + 2000, 22500 + 1500, 30000 - 24000) == (17000, 20500, 22500, 24000, 6000)
    # 04: the loans.
    assert (500 + 0.08 * 1000, 500 + 0.08 * 500) == (580, 540)
    assert (1000 + 0.1 * 2000, 1000 + 0.1 * 1000) == (1200, 1100)
    # 05: simple and compound interest, equivalence.
    assert 200000 * 0.05 * 4 == 40000 and close(150000 * 0.06 * 3, 27000, 1e-6)
    assert close(500000 * fp(.08, 5), 734664.04, 0.01) and close(100 * fp(.09, 2), 118.81, 1e-9)
    assert close(1e6 * fp(.1, 5), 1610510, 1e-6) and close(200000 * fp(.12, 3), 280985.60, 0.01)
    assert close(50000 * fp(.1, 2) - 50000 - 50000 * .1 * 2, 500, 1e-6)
    assert close(800000 * pf(.1, 2), 661157.02, 0.01)
    assert close(1000 * pa(.1, 5), 3791, 0.5) and close(2000 * pa(.1, 3), 4973.70, 0.01)
    # 06: the six factors and the lecture's examples.
    assert close(pf(.1, 3), 0.7513, 5e-5) and close(fp(.08, 5), 1.4693, 5e-5) and close(pa(.1, 4), 3.1699, 5e-5)
    assert close(ap(.1, 5), 0.2638, 5e-5) and close(fa(.1, 4), 4.641, 5e-4) and close(af(.1, 5), 0.1638, 5e-5)
    assert close(ap(.1, 5) - af(.1, 5), 0.1, 1e-12)                       # A/P = A/F + i
    assert close(1e6 * ap(.1, 5), 263797.48, 0.01)
    assert close(300000 * pf(.12, 4), 190655.42, 0.01) and close(2e6 * ap(.12, 5), 554819.46, 0.01)
    assert close(50000 * fa(.08, 6), 366796.45, 0.01)
    # 07: gradient series.
    assert close(ag(.1, 5), 1.8101, 5e-5) and close(pg(.1, 5), 6.8618, 5e-5)
    assert close(50000 + 10000 * ag(.1, 5), 68101.26, 0.01)
    rising = [0] + [50000 + 10000 * t for t in range(5)]
    assert close(npv(.1, rising), 50000 * pa(.1, 5) + 10000 * pg(.1, 5), 1e-6)
    assert close(npv(.1, rising), 258157.35, 0.01)
    assert close(ag(.08, 4), 1.4040, 5e-5) and close(20000 + 5000 * ag(.08, 4), 27019.80, 0.01)
    assert close(pg(.08, 4), 4.6501, 5e-5) and close(npv(.08, [0, 0, 5000, 10000, 15000]), 23250.46, 0.01)
    # 08: nominal and effective, continuous, capitalized cost.
    assert close((1 + .0525 / 365) ** 365 - 1, 0.0539, 5e-5) and close(1.01 ** 12 - 1, 0.1268, 5e-5)
    assert close(1.015 ** 12 - 1, 0.195618, 1e-6) and close(1.02 ** 4 - 1, 0.0824322, 1e-7)
    assert close(math.exp(.1) - 1, 0.1052, 5e-5) and close(10000 * math.exp(.4), 14918.25, 0.01)
    assert 75 / 0.06 == 1250 and close(200000 / .08, 2.5e6, 1e-6)
    assert close(10000 + 10000 / (1.1 ** 5 - 1), 26379.75, 0.01)
    assert close(50000 + 50000 / (1.1 ** 10 - 1), 81372.70, 0.01)
    # 09: inflation and the Fisher equation.
    assert (132 - 120) / 120 == 0.1 and (275 - 250) / 250 == 0.1
    assert close(1.12 / 1.04 - 1, 0.0769, 5e-5) and close(1.15 / 1.10 - 1, 0.0455, 5e-5)
    assert close(1.15 / 1.09 - 1, 0.0550459, 1e-7) and close(1.08 * 1.05 - 1, 0.134, 1e-12)
    assert close(2000 * 1.166 ** -2, 1471, 0.5) and close(1.25 / 1.20 - 1, 0.0417, 5e-5)
    assert 100000 / 1.25 == 80000 and 60000 / 1.2 == 50000
    # 10: bracket creep and FIFO.
    assert close(950000 * 1.1, 1045000, 1e-6) and close(2e6 * 1.15, 2.3e6, 1e-6)
    assert (100 * 10 + 50 * 12, 150 * 20 - 1600, 150 * 14, 3000 - 2100) == (1600, 1400, 2100, 900)
    assert (200 * 50 + 100 * 60, 30000 - 16000, 300 * 60, 30000 - 18000) == (16000, 14000, 18000, 12000)
    # 11: present worth.
    assert close(-3e6 + 1.2e6 * 3.1699, 803880, 1e-6) and close(-4.2e6 + 1.7e6 * 3.1699, 1188830, 1e-6)
    assert close(pa(.09, 10), 6.418, 5e-4) and close(pf(.09, 10), 0.4224, 5e-5)
    assert close(50000 + 2000 * 6.418 - 10000 * 0.4224, 58612, 1e-6) and close(58612 / 6.418, 9132.44, 0.01)
    assert close(npv(.12, [-2e6] + [6e5] * 4 + [8e5]), 276351.09, 0.01)
    assert close(-(1e6 + 150000 * pa(.1, 4)), -1475480, 1) and close(-(1.3e6 + 80000 * pa(.1, 4)), -1553589, 1)
    assert close(50000 / 4.1667, 12000, 1)
    # 12: annual worth and future worth.
    assert close(-3e6 * 0.3155 + 1.2e6, 253500, 1e-6) and close(-4.2e6 * 0.3155 + 1.7e6, 374900, 1e-6)
    pw_tb = -40000 + 10000 * pa(.15, 10) + 5000 * pf(.15, 10)
    assert close(pw_tb, 11424, 1) and close(11424 * 0.1993, 2277, 0.5)
    assert close(10000 * ap(.1, 3) + 2000, 6021, 0.5) and close(16000 * ap(.1, 6) + 1500, 5174, 0.5)
    assert close((5000 * 0.4021 - 1200 * 0.3021 + 500) / 0.11, 19527, 1)
    assert close(npv(.12, [-2e6] + [6e5] * 4 + [8e5]) * ap(.12, 5), 76662.48, 0.01)
    assert close(af(.12, 5), 0.1574, 5e-5) and close(2908 / 0.15, 19386.67, 0.01)
    assert close(1188830 * 1.4641, 1740566, 0.5)
    # 13: rate of return.
    slide = [-500, 300, 300, 200]
    assert [round(c * pf(.1, t)) for t, c in enumerate(slide)][1:] == [273, 248, 150]
    assert [round(c * pf(.2, t)) for t, c in enumerate(slide)][1:] == [250, 208, 116]
    assert [round(c * pf(.3, t)) for t, c in enumerate(slide)][1:] == [231, 178, 91]
    assert round(irr(slide), 2) == 0.30
    a, b = -1000 + 400 * 2.53129, -1000 + 400 * 2.48685
    assert close(a, 12.5, 0.05) and close(b, -5.3, 0.05) and close(9 + a / (a - b), 9.70, 0.01)
    assert close(irr([-1000, 400, 400, 400]), 0.0970, 5e-5)
    assert close(1300 / 1.1 - 1000, 182, 0.5) and close(2500 / 1.1 - 2000, 273, 0.5) and irr([-1000, 1200]) - 0.2 < 1e-9
    assert close(12 + 2 * 28.06 / (28.06 + 24.01), 13.08, 0.005)
    assert close(npv(.12, [-2000, 1200, 1200]), 28.06, 0.01) and close(npv(.14, [-2000, 1200, 1200]), -24.01, 0.01)
    assert close(400 * pa(.2, 3), 843, 0.5) and close(400 * pa(.25, 3), 781, 0.5)
    # 14: benefit-cost ratio and payback.
    assert 18 / 12 == 1.5 and 49 - (40 + 12) == -3 and 15 / 10 == 1.5 and close(20 / 14, 1.43, 5e-3) and 5 / 4 == 1.25
    assert 9 / 12 == 0.75 and (39 - 30) / (26 - 20) == 1.5 and 300000 / 60000 == 5 and 12 / 80 == 0.15
    cum5 = -200000 + 50000 * pa(.1, 5)
    cum6 = -200000 + 50000 * pa(.1, 6)
    assert close(cum5, -10461, 0.5) and close(cum6, 17763, 0.5)
    # 15 to 17: depreciation.
    assert straight_line(5e6, 5e5, 5)[0] == 900000 and straight_line(12e6, 2e6, 5)[0] == 2e6
    assert book_values(12e6, straight_line(12e6, 2e6, 5)) == [12e6, 10e6, 8e6, 6e6, 4e6, 2e6]
    assert straight_line(2e6, 2e5, 5)[0] == 360000 and 9000 - 3 * 880 == 6360
    ddb = double_declining(8.5e6, 5e5, 5)
    assert [round(d, 2) for d in ddb] == [3400000, 2040000, 1224000, 734400, 440640]
    assert round(book_values(8.5e6, ddb)[-1], 2) == 660960
    gen = double_declining(6e6, 6e5, 4)
    assert gen == [3e6, 1.5e6, 750000, 150000] and book_values(6e6, gen)[-1] == 6e5
    assert syd(6e6, 6e5, 4) == [2160000, 1620000, 1080000, 540000] and sum(syd(6e6, 6e5, 4)) == 5.4e6
    assert double_declining(10e6, 0, 5)[:3] == [4e6, 2.4e6, 1.44e6] and close(book_values(10e6, [4e6, 2.4e6, 1.44e6])[-1], 2.16e6, 1e-6)
    assert double_declining(4e6, 8e5, 4) == [2e6, 1e6, 2e5, 0]
    assert straight_line(9e6, 1e6, 8)[0] == 1e6
    assert syd(1.6e6, 1e5, 5)[0] == 500000 and syd(1.6e6, 1e5, 5)[2] == 300000
    assert (15e6 - 3e6) / 120000 == 100 and 15e6 - 100 * (20000 + 30000 + 25000) == 7.5e6
    assert (8e6 - 5e5) / 150000 == 50 and 9000 - (900 + 1620 + 1296) == 5184
    assert close(1e6 * af(.1, 5), 163797.48, 0.01)
    # 18: depreciation, tax and cash flow.
    assert 200 * 0.7 + 50 * 0.3 == 155 and (200 - 50) * 0.7 == 105
    assert 350 * 0.7 + 100 * 0.3 == 275 and close((350 - 100) * 0.7, 175, 1e-9)
    assert close(75000 * pa(.1, 4), 237740, 1)
    assert close(npv(.1, [0] + [0.3 * d for d in syd(1e6, 0, 4)]), 249040, 1)
    assert close(60000 * pa(.12, 3), 144110, 1) and close(npv(.12, [0] + [0.3 * d for d in syd(6e5, 0, 3)]), 149542, 1)
    # 19 to 21: cost estimation.
    assert 1 * 7 / 5 == 1.4 and 80 * 10 / 4 == 200
    assert close(500 * 16 ** 0.6, 2639, 0.5) and close(120 * 2 ** 0.6, 182, 0.5) and close(2 ** 0.6, 1.5157, 5e-5)
    assert close(300 * 20 ** 0.7, 2442.54, 0.01) and close(40 * 3 ** 0.6, 77.327, 0.001)
    assert 80 * 210 / 150 == 112 and 50 * 270 / 180 == 75 and 120 + 40 + 30 + 10 == 200
    b = math.log(0.8) / math.log(2)
    assert [round(100 * x ** b, 1) for x in (1, 2, 4, 8)] == [100, 80, 64, 51.2] and close(100 * 10 ** b, 47.7, 0.05)
    assert close(200 * 0.9 ** 2, 162, 1e-9) and close(200 * 0.9 ** 3, 145.8, 1e-9)
    # 23, 24: measuring risk and decision rules.
    assert mean_sd([100, 1000], [.4, .6]) == (640, math.sqrt(194400)) and close(math.sqrt(194400), 441, 0.5)
    assert mean_sd([-10, 10], [.5, .5]) == (0, 10) and mean_sd([200, 600], [.25, .75])[0] == 500
    assert close(mean_sd([200, 600], [.25, .75])[1], 173.205, 0.001) and close(.3 * 200 + .7 * 50, 95, 1e-9)
    assert (30000 / 100000, round(40000 / 150000, 3), 50000 / 200000, 36000 / 120000) == (0.3, 0.267, 0.25, 0.3)
    probs = [.35, .5, .15]
    got = {k: tuple(round(x, 2) for x in mean_sd(v, probs)) for k, v in PRICING.items()}
    assert got == {'Raise price': (14.75, 11.34), 'No change': (14.5, 8.5), 'Lower price': (6.0, 6.82)}
    eq = [1 / 3] * 3
    assert [round(mean_sd(v, eq)[0], 2) for v in PRICING.values()] == [10, 10, 6.67]
    assert round(mean_sd(PRICING['No change'], eq)[1], 2) == 10.80 and round(mean_sd(PRICING['Raise price'], eq)[1], 2) == 14.72
    assert max_regret(PRICING) == {'Raise price': 15, 'No change': 10, 'Lower price': 20}
    assert [min(v) for v in PRICING.values()] == [-10, -5, 0] and [max(v) for v in PRICING.values()] == [25, 20, 15]
    hurwicz = lambda v, a: a * max(v) + (1 - a) * min(v)
    assert [round(hurwicz(v, .6), 2) for v in PRICING.values()] == [11, 10, 9]
    assert max_regret(PLANT) == {'Big': 21, 'Medium': 15, 'Small': 28}
    assert [round(hurwicz(v, .6), 2) for v in PLANT.values()] == [18, 15, 9.6]
    assert [round(mean_sd(v, [.3, .5, .2])[0], 2) for v in PLANT.values()] == [19, 16.5, 9.8]
    # 25: sensitivity analysis.
    assert [round(-100 + a * pa(.1, 5), 2) for a in (24, 30, 36)] == [-9.02, 13.72, 36.47]
    assert close(100 / pa(.1, 5), 26.38, 0.005)
    assert close(-50 + 15 * pa(.12, 5), 4.0716, 1e-4) and close(50 / pa(.12, 5), 13.870, 1e-3)
    assert close((15 - 13.87) / 15 * 100, 7.53, 0.01)
    # 26 to 28: break-even.
    assert 40000 / 20 == 2000 and 40000 / 0.4 == 100000 and 50000 / 20 == 2500
    assert 75000 / 30 == 2500 and 30 / 80 == 0.375 and 75000 / 0.375 == 200000 and 105000 / 30 == 3500
    assert 12 + 35 + 5 * 8 + 2 == 89 and 120000 + (160000 - 2 * 10000) + 80000 == 340000
    assert 340000 / 40 == 8500 and 380000 / 40 * 129 == 1225500 and close(400000 / 60000, 6.67, 0.005)
    assert (1000 - 15000) / (0.5 - 1.5) == 14000 and 30000 / 2.5 == 12000 and 6e6 / (150 - 90) == 100000
    m = 5 * (7 - 2.94) + (15 - 4.5)
    assert close(m, 30.8, 1e-9) and math.ceil(36000 / m) == 1169
    assert 5845 * 7 + 1169 * 15 == 58450 and close(36000 / (m / 50), 58442, 0.5)
    w = 5 * (8 - 3.8) + 6 * (14 - 4.2)
    assert close(w, 79.8, 1e-9) and close(43890 / w, 550, 1e-9)
    assert 2750 * 8 + 3300 * 14 == 68200 and 74400 - 68200 == 6200 and round(6200 / 74400 * 100, 1) == 8.3
    assert 2 * 6 + 3 + 3 * 6 == 33 and 132000 / 33 == 4000 and 8000 * 22 + 4000 * 15 + 12000 * 19 == 464000
    assert 3 * 4 + 8 == 20 and 24000 / 20 * 3 * 10 + 1200 * 20 == 60000 and 20 / 50 == 0.4
    assert close(10000 / (21000 / 58000), 27619, 0.5)
    # 30 to 33: elasticity, production, equilibrium.
    assert close(0.30 / 0.20, 1.5, 1e-9) and close(0.15 / 0.10, 1.5, 1e-9) and close(0.2 / 0.5, 0.4, 1e-9)
    assert [12 - 8, 8 - 5, 5 - 3, 3 - 2] == [4, 3, 2, 1] and (12 - 15) / (3 - 2) == -3
    table = [(L, tp(L), tp(L) - tp(L - 1), tp(L) / L) for L in range(1, 9)]
    assert [r[1] for r in table] == [9, 32, 63, 96, 125, 144, 147, 128]
    assert [r[2] for r in table] == [9, 23, 31, 33, 29, 19, 3, -19]
    assert [r[3] for r in table] == [9, 16, 21, 24, 25, 24, 21, 16]
    assert 62 - 40 == 22 and 62 / 4 == 15.5
    assert (100 - 20) / 5 == 16 and 100 - 2 * 16 == 68 == 20 + 3 * 16 and (100 - 40, 20 + 60) == (60, 80)
    assert (120 - 20) / 5 == 20 and 120 - 60 == 60 and (20 + 50) - (120 - 75) == 25


# ---------- a small plotting helper ----------

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
        zero_y = self.P(self.x0, 0)[1] if self.y0 <= 0 <= self.y1 else self.top + self.h
        s.line(self.left, zero_y, self.left + self.w, zero_y, width=1.5)
        s.line(self.left, self.top, self.left, self.top + self.h, width=1.5)
        s.text(self.left + self.w / 2, self.top + self.h + 36, xlabel, size=12)
        s.add(f'<text x="{self.left - 52:.1f}" y="{self.top + self.h / 2:.1f}" font-size="12" fill="{INK}" '
              f'text-anchor="middle" font-family="system-ui, sans-serif" '
              f'transform="rotate(-90 {self.left - 52:.1f} {self.top + self.h / 2:.1f})">{ylabel}</text>')

    def curve(self, pts, color, width=2.5, dash=None):
        d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in (self.P(*p) for p in pts))
        self.s.path(d, color, width=width, dash=dash)

    def dot(self, x, y, color, r=4.5):
        self.s.circle(*self.P(x, y), r, color, '#ffffff')


def naira(v):
    return f'{v:,.0f}'


# ---------- pictures ----------

def cash_flow(name, title, flows, unit_h):
    """flows: list of (year, amount, label). Upward arrows are benefits, downward are costs."""
    years = max(y for y, _, _ in flows)
    W, H = 170 + years * 130, 300
    s = Svg(W, H, title)
    base, left, step = 150, 60, 130
    s.line(left - 20, base, left + years * step + 40, base, width=2)
    for y in range(years + 1):
        x = left + y * step
        s.line(x, base - 5, x, base + 5, width=2)
        s.text(x, base + 22 if not any(f[0] == y and f[1] < 0 for f in flows) else base - 10, y, size=12,
               color='#374151')
    s.text(left + years * step + 70, base + 5, 'year', size=12, color='#374151', anchor='end')
    offsets = {}
    for y, amt, label in flows:
        k = offsets.get((y, amt > 0), 0)
        offsets[(y, amt > 0)] = k + 1
        x = left + y * step + k * 26
        h = abs(amt) * unit_h
        color = ACCENT if amt > 0 else TRUE
        if amt > 0:
            s.line(x, base, x, base - h, color=color, width=3)
            s.path(f'M {x - 7:.1f} {base - h + 10:.1f} L {x:.1f} {base - h:.1f} L {x + 7:.1f} {base - h + 10:.1f}', color, 3)
            s.text(x, base - h - 8, label, size=12, color=color, weight='bold')
        else:
            s.line(x, base, x, base + h, color=color, width=3)
            s.path(f'M {x - 7:.1f} {base + h - 10:.1f} L {x:.1f} {base + h:.1f} L {x + 7:.1f} {base + h - 10:.1f}', color, 3)
            s.text(x, base + h + 18, label, size=12, color=color, weight='bold')
    s.text(W - 12, 20, 'up = benefit (in)', size=11, color=ACCENT, anchor='end')
    s.text(W - 12, 36, 'down = cost (out)', size=11, color=TRUE, anchor='end')
    s.save(name, OUT)


def irr_curve():
    flows = [-500, 300, 300, 200]
    s = Svg(560, 360, 'Present worth of a 500 naira investment returning 300, 300 and 200 plotted against the interest '
                      'rate from 0 to 40 percent: the curve falls from 300 at 0 percent and crosses zero at about 30 '
                      'percent, the internal rate of return, with the 15 percent target rate marked to its left')
    p = Plot(s, 90, 30, 430, 260, 0, 40, -100, 300)
    p.axes(range(0, 41, 10), range(-100, 301, 100), 'interest rate (%)', 'present worth (₦)',
           xfmt=lambda v: f'{v}%')
    p.curve([(r / 2, npv(r / 200, flows)) for r in range(0, 81)], PIX)
    r = irr(flows) * 100
    p.dot(r, 0, TRUE, 6)
    x, y = p.P(r, 0)
    s.text(x + 8, y - 12, f'IRR ≈ {r:.0f}%', size=13, color=TRUE, anchor='start', weight='bold')
    x15, _ = p.P(15, 0)
    s.line(x15, p.top, x15, p.top + p.h, color=ORANGE, width=2, dash='6 4')
    s.text(x15 + 6, p.top + 14, 'target 15%', size=12, color='#b45309', anchor='start')
    s.text(*p.P(3, 250), 'PW > 0: accept', size=12, color=ACCENT, anchor='start')
    s.text(*p.P(31, -60), 'PW < 0', size=12, color=TRUE, anchor='start')
    s.save('ee-irr-pw-curve.svg', OUT)


def book_value_methods():
    fc, sv, n = 6e6, 6e5, 4
    lines = [('Straight line', book_values(fc, straight_line(fc, sv, n)), PIX, None),
             ('Sum-of-the-years digits', book_values(fc, syd(fc, sv, n)), ACCENT, None),
             ('Double declining balance', book_values(fc, double_declining(fc, sv, n)), TRUE, None)]
    s = Svg(690, 380, 'Book value of a 6 million naira generator over 4 years under straight line, sum-of-the-years '
                      'digits and double declining balance: all three start at 6 million and end at the 600,000 '
                      'salvage value, but double declining balance falls fastest, then sum-of-the-years digits, '
                      'while straight line falls in a straight line')
    p = Plot(s, 100, 30, 330, 270, 0, 4, 0, 6)
    p.axes(range(0, 5), range(0, 7), 'year', 'book value (₦ million)')
    for _, bvs, color, dash in lines:
        p.curve([(t, b / 1e6) for t, b in enumerate(bvs)], color, dash=dash)
        for t, b in enumerate(bvs):
            p.dot(t, b / 1e6, color, 4)
    xs, ys = p.P(4, 0.6)
    s.line(p.left, ys, p.left + p.w, ys, color=GREY, width=1.2, dash='5 4')
    s.text(p.left + 8, ys - 6, 'salvage value ₦600,000', size=11, color=GREY, anchor='start')
    for k, (label, _, color, _) in enumerate(lines):
        y = 70 + k * 26
        s.line(445, y - 4, 470, y - 4, color=color, width=3)
        s.text(476, y, label, size=12, color=color, anchor='start', weight='bold')
    s.save('ee-book-value-methods.svg', OUT)


def spider():
    base = dict(C=100, A=30, n=5, i=.10)

    def pw(C, A, n, i):
        return -C + A * pa(i, n)

    variables = [('annual benefit', 'A', ACCENT), ('first cost', 'C', TRUE), ('interest rate (MARR)', 'i', PIX)]
    s = Svg(600, 400, 'Spider diagram for a 100 million naira project returning 30 million a year for 5 years at 10 '
                      'percent: present worth against percentage change from minus 20 to plus 20 percent, with a steep '
                      'rising line for annual benefit that crosses zero near minus 12 percent, a falling line for first '
                      'cost that crosses zero near plus 14 percent, and a gentle falling line for the interest rate '
                      'that stays positive')
    p = Plot(s, 90, 30, 330, 290, -20, 20, -20, 40)
    p.axes(range(-20, 21, 10), range(-20, 41, 10), 'change in the estimate (%)', 'present worth (₦ million)',
           xfmt=lambda v: f'{v:+d}%' if v else '0')
    for k, (label, key, color) in enumerate(variables):
        pts = []
        for pct in range(-20, 21, 2):
            d = dict(base)
            d[key] = base[key] * (1 + pct / 100)
            pts.append((pct, pw(**d)))
        p.curve(pts, color)
        y = 70 + k * 26
        s.line(435, y - 4, 460, y - 4, color=color, width=3)
        s.text(466, y, label, size=12, color=color, anchor='start', weight='bold')
    p.dot(0, pw(**base), INK, 5)
    x, y = p.P(0, pw(**base))
    s.text(x + 8, y - 8, f'base PW {pw(**base):.2f}', size=11, anchor='start')
    s.save('ee-spider-diagram.svg', OUT)


def break_even_chart():
    fc, vc, price, budget = 340000, 89, 129, 10000
    bep = fc / (price - vc)
    s = Svg(620, 400, 'Break-even chart for the lecture 9 exercise: units from 0 to 12,000 on the horizontal axis and '
                      'naira on the vertical axis, a flat fixed cost line at 340,000, a total cost line rising from '
                      '340,000 at 89 naira per unit, and a revenue line rising from zero at 129 naira per unit, crossing '
                      'total cost at the break-even point of 8,500 units; budgeted sales of 10,000 units are marked, '
                      'with the gap from 8,500 to 10,000 shaded as the margin of safety')
    p = Plot(s, 100, 30, 380, 290, 0, 12000, 0, 1600000)
    p.axes(range(0, 12001, 2000), range(0, 1600001, 400000), 'units sold', 'naira',
           xfmt=naira, yfmt=lambda v: f'{v / 1000:,.0f}k')
    x1, y1 = p.P(bep, 0)
    x2, y2 = p.P(budget, 0)
    s.rect(x1, p.top, x2 - x1, p.h, ORANGE, opacity=0.18)
    s.text((x1 + x2) / 2, p.top + 14, 'margin', size=11, color='#b45309')
    s.text((x1 + x2) / 2, p.top + 28, 'of safety', size=11, color='#b45309')
    p.curve([(0, fc), (12000, fc)], GREY, dash='6 4')
    p.curve([(0, fc), (12000, fc + vc * 12000)], TRUE)
    p.curve([(0, 0), (12000, price * 12000)], ACCENT)
    p.dot(bep, price * bep, INK, 6)
    x, y = p.P(bep, price * bep)
    s.text(x - 10, y - 12, 'break-even: 8,500 units', size=12, anchor='end', weight='bold')
    s.line(x2, p.top + 34, x2, p.top + p.h, color=ORANGE, width=1.5, dash='4 3')
    s.text(x2 + 4, p.top + p.h - 8, 'budget 10,000', size=11, color='#b45309', anchor='start')
    for k, (label, color) in enumerate([('total revenue', ACCENT), ('total cost', TRUE), ('fixed cost', GREY)]):
        y = 70 + k * 24
        s.line(495, y - 4, 520, y - 4, color=color, width=3)
        s.text(526, y, label, size=12, color=color, anchor='start', weight='bold')
    s.save('ee-break-even-chart.svg', OUT)


def demand_curve():
    pts = [(6, 5), (9, 4), (12, 3), (15, 2), (18, 1)]
    s = Svg(520, 360, 'Market demand curve from the lecture\'s schedule: price in naira on the vertical axis from 0 to 6 '
                      'and quantity in kilograms on the horizontal axis from 0 to 20, with points at 6 kg for 5 naira, '
                      '9 kg for 4 naira, 12 kg for 3 naira, 15 kg for 2 naira and 18 kg for 1 naira, joined by a '
                      'straight line sloping down to the right')
    p = Plot(s, 90, 30, 380, 260, 0, 20, 0, 6)
    p.axes(range(0, 21, 5), range(0, 7), 'quantity demanded (kg per week)', 'price (₦ per kg)')
    p.curve(pts, PIX)
    for q, pr in pts:
        p.dot(q, pr, PIX)
        x, y = p.P(q, pr)
        s.text(x + 8, y - 8, f'({q}, ₦{pr})', size=11, anchor='start')
    s.text(*p.P(17, 1.6), 'D', size=14, color=PIX, weight='bold')
    s.save('ee-demand-curve.svg', OUT)


def isoquant():
    pts = [(1, 12), (2, 8), (3, 5), (4, 3), (5, 2)]
    s = Svg(520, 380, 'Isoquant for 20 units of output with input X on the horizontal axis and input Y on the vertical '
                      'axis: points A (1, 12), B (2, 8), C (3, 5), D (4, 3) and E (5, 2) joined by a curve that slopes '
                      'down and is convex to the origin, with the drops in Y of 4, 3, 2 and 1 marked between '
                      'neighbouring points')
    p = Plot(s, 90, 30, 360, 280, 0, 6, 0, 14)
    p.axes(range(0, 7), range(0, 15, 2), 'units of input X', 'units of input Y')
    p.curve(pts, PIX)
    for k, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
        p.curve([(x0, y0), (x0, y1), (x1, y1)], ORANGE, width=1.5, dash='4 3')
        x, y = p.P(x0, (y0 + y1) / 2)
        s.text(x - 6, y + 4, f'−{y0 - y1}', size=11, color='#b45309', anchor='end')
    for label, (x, y) in zip('ABCDE', pts):
        p.dot(x, y, PIX)
        px, py = p.P(x, y)
        s.text(px + 9, py - 7, label, size=13, weight='bold', anchor='start')
    s.text(*p.P(5.0, 4.4), 'Q = 20', size=12, color=PIX, weight='bold')
    s.save('ee-isoquant.svg', OUT)


def variable_proportions():
    s = Svg(560, 560, 'Total, average and marginal product against units of the variable input for TP equals 10 L '
                      'squared minus L cubed: the top panel shows total product rising steeply, flattening and peaking '
                      'near L equals 6.7 before falling; the bottom panel shows marginal product rising then falling '
                      'through zero at L equals 6.7, and average product peaking at L equals 5 where marginal product '
                      'crosses it; dashed lines at L equals 5 and L equals 6.7 divide stages 1, 2 and 3')
    top = Plot(s, 90, 40, 400, 190, 0, 8.5, 0, 160)
    top.axes(range(0, 9), range(0, 161, 40), '', 'total product')
    top.curve([(L / 20, tp(L / 20)) for L in range(0, 171)], PIX)
    bot = Plot(s, 90, 300, 400, 190, 0, 8.5, -50, 40)
    bot.axes(range(0, 9), range(-40, 41, 20), 'units of the variable input (L)', 'product per unit')
    bot.curve([(L / 20, mp_cont(L / 20)) for L in range(0, 171)], TRUE)
    bot.curve([(L / 20, ap_cont(L / 20)) for L in range(1, 171)], ACCENT)
    assert close(mp_cont(5), ap_cont(5), 1e-9) and close(mp_cont(20 / 3), 0, 1e-9)
    for L in (5, 20 / 3):
        for pl in (top, bot):
            x, _ = pl.P(L, 0)
            s.line(x, pl.top, x, pl.top + pl.h, color=ORANGE, width=1.5, dash='5 4')
    for label, a, b in (('stage 1', 0, 5), ('stage 2', 5, 20 / 3), ('stage 3', 20 / 3, 8.5)):
        x = (top.P(a, 0)[0] + top.P(b, 0)[0]) / 2
        s.text(x, 30, label, size=12, color='#b45309', weight='bold')
    s.text(*top.P(4, 120), 'TP', size=13, color=PIX, weight='bold')
    s.text(*bot.P(2.4, 33), 'MP', size=13, color=TRUE, weight='bold')
    s.text(*bot.P(7.6, 19), 'AP', size=13, color=ACCENT, weight='bold')
    s.save('ee-variable-proportions.svg', OUT)


def supply_demand():
    s = Svg(560, 400, 'Demand and supply curves for Qd equals 100 minus 2P and Qs equals 20 plus 3P, with quantity on '
                      'the horizontal axis and price on the vertical axis: the downward demand line and upward supply '
                      'line cross at the equilibrium of quantity 68 and price 16; a dashed line at price 20 shows '
                      'quantity demanded 60 and quantity supplied 80, a surplus of 20')
    p = Plot(s, 90, 30, 400, 300, 0, 120, 0, 40)
    p.axes(range(0, 121, 20), range(0, 41, 10), 'quantity', 'price')
    p.curve([(100 - 2 * pr, pr) for pr in (0, 40)], PIX)
    p.curve([(20 + 3 * pr, pr) for pr in (0, 33)], ACCENT)
    s.text(*p.P(24, 36), 'D', size=14, color=PIX, weight='bold')
    s.text(*p.P(112, 31), 'S', size=14, color=ACCENT, weight='bold')
    p.curve([(0, 16), (68, 16), (68, 0)], GREY, width=1.2, dash='4 3')
    p.dot(68, 16, INK, 6)
    x, y = p.P(68, 16)
    s.text(x + 10, y + 18, 'equilibrium (68, 16)', size=12, anchor='start', weight='bold')
    p.curve([(0, 20), (80, 20)], ORANGE, width=1.5, dash='6 4')
    p.dot(60, 20, PIX, 4)
    p.dot(80, 20, ACCENT, 4)
    xa, ya = p.P(60, 20)
    xb, _ = p.P(80, 20)
    s.line(xa, ya - 12, xb, ya - 12, color='#b45309', width=1.5)
    s.text((xa + xb) / 2, ya - 18, 'surplus 20', size=12, color='#b45309', weight='bold')
    s.text(p.left + 6, ya - 6, 'P = 20', size=11, color='#b45309', anchor='start')
    s.save('ee-supply-demand.svg', OUT)


def capital_budgeting_phases():
    phases = ['1. Planning', '2. Analysis', '3. Selection', '4. Financing', '5. Implementation', '6. Review']
    body = [f'p{i} [label="{ph}", width=2.4];' for i, ph in enumerate(phases)]
    body += [f'p{i} -> p{i + 1};' for i in range(len(phases) - 1)]
    body.append(f'p5 -> p0 [label="  what is learned\\n  feeds the next round", style=dashed, color="{ORANGE}", '
                f'fontcolor="#b45309", constraint=false];')
    src = (f'digraph {{ bgcolor="white"; pad=0.25; rankdir=TB; nodesep=0.3; ranksep=0.3;\n'
           f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", fillcolor="#dbeafe", '
           f'color="{INK}", penwidth=1.2];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];\n' + '\n'.join(body) + '\n}')
    save_dot(src, 'ee-capital-budgeting-phases.svg',
             'The six phases of capital budgeting in order: planning, analysis, selection, financing, implementation '
             'and review, with a dashed arrow from review back to planning because what is learned feeds the next round',
             OUT)


if __name__ == '__main__':
    check_lessons()
    cash_flow('ee-cash-flow-loan.svg',
              'Cash flow diagram of a 1,000 naira loan at 8 percent from the borrower\'s side: an upward arrow of 1,000 '
              'at year 0, a downward arrow of 580 at year 1 and a downward arrow of 540 at year 2',
              [(0, 1000, '+1,000'), (1, -580, '−580'), (2, -540, '−540')], 0.1)
    cash_flow('ee-cash-flow-machine.svg',
              'Cash flow diagram of a 50,000 naira machine: a downward arrow of 50,000 at year 0, upward arrows of '
              '20,000 at years 1, 2 and 3, and a separate upward arrow of 5,000 salvage at year 3',
              [(0, -50000, '−50,000'), (1, 20000, '+20,000'), (2, 20000, '+20,000'), (3, 20000, '+20,000'),
               (3, 5000, '+5,000')], 0.0024)
    irr_curve()
    book_value_methods()
    spider()
    break_even_chart()
    demand_curve()
    isoquant()
    variable_proportions()
    supply_demand()
    capital_budgeting_phases()
