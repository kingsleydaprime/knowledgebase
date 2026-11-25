"""Draw the mechatronics Karnaugh-map diagrams (section E) and check the lesson's minimisations.

    python3 scripts/diagrams/mechatronics_logic.py      # run from the vault root

A small Quine-McCluskey solver finds every prime implicant and every minimum-cost cover of each
exam function. The lesson's minimal expressions are asserted to be (a) exactly the solver's
minimum covers and (b) equal to the function on every input that is not a don't-care, before any
map is drawn. No libraries needed. Output: mechatronics/images/logic-*.svg.
"""
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, Svg  # noqa: E402

OUT = os.path.join('mechatronics', 'images')
VARS = 'ABCD'
GRAY = [0, 1, 3, 2]
COLORS = ['#2563eb', '#f59e0b', '#059669', '#7c3aed', '#dc2626']
F1 = ([0, 1, 4, 5, 6, 7, 8, 10, 11, 12, 14], [2, 3, 9, 13, 15])   # 2024/25 and 2025/26
F2 = ([1, 3, 4, 6, 8, 9, 11, 13, 15], [0, 2, 14])                  # 2020/21, 2023/24, practice Q5
F3 = ([0, 1, 2, 5, 7, 8, 10, 13, 15], [])                          # practice Q3


# --------------------------------------------------------------------------- Quine-McCluskey
def primes(ones, dcs):
    terms = {(m, 0) for m in set(ones) | set(dcs)}       # (value, mask of eliminated bits)
    found = set()
    while terms:
        nxt, used = set(), set()
        for a, b in combinations(sorted(terms), 2):
            if a[1] == b[1]:
                d = a[0] ^ b[0]
                if d and not d & (d - 1):
                    nxt.add((a[0] & ~d, a[1] | d))
                    used |= {a, b}
        found |= terms - used
        terms = nxt
    return found


def covers(p, m):
    return (m & ~p[1]) == p[0]


def literals(p):
    return 4 - bin(p[1]).count('1')


def text(p):
    out = []
    for i in range(4):
        bit = 1 << (3 - i)
        if not p[1] & bit:
            out.append(VARS[i] if p[0] & bit else VARS[i] + "'")
    return ''.join(out) or '1'


def parse(term):
    """"AB'D" -> implicant (value, mask)."""
    if term == '1':
        return (0, 15)
    val, mask, i = 0, 15, 0
    while i < len(term):
        v = VARS.index(term[i])
        neg = i + 1 < len(term) and term[i + 1] == "'"
        bit = 1 << (3 - v)
        mask &= ~bit
        if not neg:
            val |= bit
        i += 2 if neg else 1
    return (val, mask)


def minimum_covers(ones, dcs):
    P = sorted(primes(ones, dcs))
    for k in range(1, len(P) + 1):
        sols = [c for c in combinations(P, k) if all(any(covers(p, m) for p in c) for m in ones)]
        if sols:
            best = min(sum(literals(p) for p in c) for c in sols)
            return P, [c for c in sols if sum(literals(p) for p in c) == best]
    return P, []


def check(name, fn, exprs):
    ones, dcs = fn
    P, sols = minimum_covers(ones, dcs)
    want = {frozenset(text(p) for p in c) for c in sols}
    got = {frozenset(e.split(' + ')) for e in exprs}
    assert got == want, (name, got, want)
    for e in exprs:
        imps = [parse(t) for t in e.split(' + ')]
        for m in range(16):
            if m in dcs:
                continue
            assert any(covers(p, m) for p in imps) == (m in ones), (name, e, m)
    print(f'check {name}: ok ({len(P)} primes, {len(sols)} minimal)')
    return P


# --------------------------------------------------------------------------- drawing
CELL, X0, Y0 = 58, 120, 80


def cell_xy(m):
    ab, cd = m >> 2, m & 3
    return X0 + GRAY.index(cd) * CELL, Y0 + GRAY.index(ab) * CELL


def segments(pos):
    pos = sorted(set(pos))
    if len(pos) == 4:
        return [(0, 3)]
    if pos == [0, 3]:
        return [(0, 0), (3, 3)]
    return [(pos[0], pos[-1])]


def kmap(name, title, ones, dcs, groups=(), show_numbers=True, values=True, caption=None):
    s = Svg(440, 400 if caption else 370, title)
    s.text(X0 - 30, Y0 - 32, 'AB \\ CD', size=13, weight='bold')
    for i, g in enumerate(GRAY):
        s.text(X0 + i * CELL + CELL / 2, Y0 - 12, f'{g:02b}', size=13, weight='bold')
        s.text(X0 - 22, Y0 + i * CELL + CELL / 2 + 5, f'{g:02b}', size=13, weight='bold')
    for r in range(4):
        for c in range(4):
            s.rect(X0 + c * CELL, Y0 + r * CELL, CELL, CELL, fill='white', stroke=INK, width=1.2)
    for m in range(16):
        x, y = cell_xy(m)
        if show_numbers:
            s.text(x + CELL - 6, y + 14, str(m), size=10, color='#6b7280', anchor='end')
        if values:
            v = '1' if m in ones else ('X' if m in dcs else '0')
            col = INK if v == '1' else ('#6b7280' if v == 'X' else '#c4c9d0')
            s.text(x + CELL / 2, y + CELL / 2 + 8, v, size=19, color=col,
                   weight='bold' if v == '1' else 'normal')
    for gi, (label, p) in enumerate(groups):
        col = COLORS[gi % len(COLORS)]
        cells = [m for m in range(16) if covers(p, m)]
        rows = [GRAY.index(m >> 2) for m in cells]
        cols = [GRAY.index(m & 3) for m in cells]
        inset = 5 + 4 * gi
        for r0, r1 in segments(rows):
            for c0, c1 in segments(cols):
                x = X0 + c0 * CELL + inset
                y = Y0 + r0 * CELL + inset
                w = (c1 - c0 + 1) * CELL - 2 * inset
                h = (r1 - r0 + 1) * CELL - 2 * inset
                s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{col}" '
                      f'fill-opacity="0.08" stroke="{col}" stroke-width="2.4"/>')
        s.text(X0 + 4 * CELL + 16, Y0 + 14 + gi * 22, label, size=14, color=col, weight='bold',
               anchor='start')
    if caption:
        s.text(X0 + 2 * CELL, Y0 + 4 * CELL + 34, caption, size=14, weight='bold')
    s.save(name, OUT)


def main():
    f1_min = ['1']
    f1_nodc = ["AD' + A'B + A'C' + AB'C"]
    f2_min = ["AD + B'D + B'C' + A'D'", "AD + A'B' + B'C' + A'D'"]
    f2_nodc = ["B'D + AD + A'BD' + AB'C'"]
    f3_min = ["BD + B'D' + A'B'C'", "BD + B'D' + A'C'D"]
    check('F1 with don’t-cares', F1, f1_min)
    check('F1 without don’t-cares', (F1[0], []), f1_nodc)
    check('F2 with don’t-cares', F2, f2_min)
    check('F2 without don’t-cares', (F2[0], []), f2_nodc)
    check('F3', F3, f3_min)

    kmap('logic-kmap-layout.svg', 'An empty four-variable Karnaugh map: rows labelled by A and B '
         'and columns by C and D, each in Gray-code order 00, 01, 11, 10, with each cell showing '
         'its minterm number',
         [], [], values=False)
    kmap('logic-f2-cells.svg', 'Karnaugh map of F = sum of minterms 1, 3, 4, 6, 8, 9, 11, 13, 15 '
         'with don’t-cares 0, 2 and 14: ones in those nine cells, X in the three don’t-care '
         'cells, zeros elsewhere', *F2)
    kmap('logic-f2-groups.svg', 'The same map grouped: AD is the 2-by-2 block of rows 11 and 10, '
         'columns 01 and 11; B’D is rows 00 and 10, columns 01 and 11; B’C’ is rows 00 '
         'and 10, columns 00 and 01; A’D’ is rows 00 and 01, columns 00 and 10, wrapping '
         'round the sides', *F2,
         groups=[(t, parse(t)) for t in f2_min[0].split(' + ')],
         caption="F = AD + B'D + B'C' + A'D'")
    kmap('logic-f2-alt.svg', 'An equally small alternative grouping: A’B’ (the whole top '
         'row) replaces B’D, giving AD + A’B’ + B’C’ + A’D’', *F2,
         groups=[(t, parse(t)) for t in f2_min[1].split(' + ')],
         caption="F = AD + A'B' + B'C' + A'D'")
    kmap('logic-f1-groups.svg', 'Karnaugh map of the robotic-arm function: every one of the 16 cells '
         'is either a 1 or a don’t-care X, so one group covers the whole map and F = 1', *F1,
         groups=[('1', parse('1'))], caption='F = 1')
    kmap('logic-f1-nodc.svg', "The robotic-arm function if the don't-cares had to be 0: four "
         'groups are needed, read as A and not-D, not-A and B, not-A and not-C, and A with '
         'not-B and C', F1[0], [],
         groups=[(t, parse(t)) for t in f1_nodc[0].split(' + ')],
         caption="F = AD' + A'B + A'C' + AB'C")
    kmap('logic-f3-groups.svg', 'Karnaugh map of F = sum of minterms 0, 1, 2, 5, 7, 8, 10, 13, 15 '
         'grouped as the centre block where B and D are both 1, the four corners where B and D are '
         'both 0, and the pair of minterms 0 and 1',
         *F3, groups=[(t, parse(t)) for t in f3_min[0].split(' + ')],
         caption="F = BD + B'D' + A'B'C'")
    print('mechatronics logic diagrams: done')


if __name__ == '__main__':
    main()
