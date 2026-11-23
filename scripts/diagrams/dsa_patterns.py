"""Draw the DSA pattern lesson diagrams (dsa/04-patterns) as small SVG files.

    python3 scripts/diagrams/dsa_patterns.py      # run from the vault root

Every picture is computed by running the pattern the lesson teaches on the
lesson's own input, and the lesson's numbers are asserted before drawing, so a
picture can never disagree with the text. Trees and graphs are drawn with
Graphviz (`dot`, which must be installed). Output: dsa/images/pat-*.svg.
"""
import heapq
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, PIX, PIX2, TRUE, ACCENT, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('dsa', 'images')
ORANGE = '#f59e0b'
GREY = '#9ca3af'
LIGHT = '#e5e7eb'
BLUE_BG = '#dbeafe'
GREEN_BG = '#d1fae5'
ORANGE_BG = '#fde68a'
RED_BG = '#fee2e2'
MUTED = '#6b7280'


# ---------- shared drawing helpers ----------

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


def curved_arrow(s, mk, d, color=INK, width=1.6, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    s.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none"{da} marker-end="{mk[color]}"/>')


def cells(s, x, y, vals, cw=44, ch=36, fills=None, strokes=None, size=14, idx=None, idx_size=10, weight='normal',
          colors=None):
    """A row of boxes. fills/strokes/colors: dict index -> colour. idx: list of index labels drawn above."""
    fills, strokes, colors = fills or {}, strokes or {}, colors or {}
    for i, v in enumerate(vals):
        cx = x + i * cw
        st = strokes.get(i)
        s.rect(cx, y, cw, ch, fills.get(i, '#ffffff'), st or INK, 2.6 if st else 1.2)
        s.text(cx + cw / 2, y + ch / 2 + size * 0.36, v, size, colors.get(i, INK), weight=weight)
        if idx is not None:
            s.text(cx + cw / 2, y - 6, idx[i], idx_size, MUTED)


def pointer(s, x, y, label, color, up=True, size=12):
    """A small triangle pointing at a cell edge (up=True: triangle below the cell pointing up)."""
    if up:
        s.add(f'<path d="M{x:.1f},{y:.1f} L{x - 6:.1f},{y + 9:.1f} L{x + 6:.1f},{y + 9:.1f} z" fill="{color}"/>')
        s.text(x, y + 22, label, size, color, weight='bold')
    else:
        s.add(f'<path d="M{x:.1f},{y:.1f} L{x - 6:.1f},{y - 9:.1f} L{x + 6:.1f},{y - 9:.1f} z" fill="{color}"/>')
        s.text(x, y - 13, label, size, color, weight='bold')


def dot_header(extra=''):
    return [f'digraph {{ bgcolor="white"; pad=0.25; nodesep=0.35; ranksep=0.45; {extra}',
            f'node [fontname="{FONT}", fontsize=13, shape=circle, style=filled, fillcolor="{BLUE_BG}", '
            f'color="{INK}", penwidth=1.3, width=0.45, fixedsize=true];',
            f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="{INK}"];']


# ---------- 01 prefix sum ----------

def prefix_sums(nums):
    p = [0]
    for v in nums:
        p.append(p[-1] + v)
    return p


def prefix_revenue():
    rev = [120, 340, 90, 210, 400, 150]
    p = prefix_sums(rev)
    totals = p[1:]                                   # "total through day d"
    assert totals == [120, 460, 550, 760, 1160, 1310]
    lo, hi = 2, 5
    assert totals[hi] - totals[lo - 1] == 850 == sum(rev[lo:hi + 1])

    s = Svg(560, 250, 'Daily revenue for days 0 to 5 with the running total under each day; days 2 to 5 are '
                      'highlighted, and their sum 850 is the total through day 5 (1310) minus the total through day 1 (460)')
    x0, cw = 150, 62
    s.text(x0 - 12, 52, 'day', 12, MUTED, 'end')
    for d in range(6):
        s.text(x0 + d * cw + cw / 2, 52, d, 12, MUTED)
    s.text(x0 - 12, 85, 'revenue', 13, INK, 'end', 'bold')
    cells(s, x0, 62, rev, cw, 36, fills={d: BLUE_BG for d in range(lo, hi + 1)})
    s.text(x0 - 12, 140, 'total through day', 13, INK, 'end', 'bold')
    cells(s, x0, 117, totals, cw, 36, fills={hi: GREEN_BG, lo - 1: ORANGE_BG},
          strokes={hi: ACCENT, lo - 1: ORANGE})
    s.text(x0 + (lo + hi + 1) / 2 * cw, 30, 'days 2 to 5', 12, PIX, weight='bold')
    s.line(x0 + lo * cw + 2, 36, x0 + (hi + 1) * cw - 2, 36, PIX, 2)
    s.text(x0 + hi * cw + cw / 2, 172, 'everything to day 5', 11, ACCENT)
    s.text(x0 + (lo - 1) * cw + cw / 2, 172, 'everything before day 2', 11, ORANGE)
    s.text(280, 210, '1310 − 460 = 850  =  90 + 210 + 400 + 150', 15, INK, weight='bold')
    s.text(280, 234, 'Two lookups and one subtraction, however long the range is.', 12, MUTED)
    s.save('pat-prefix-revenue.svg', OUT)


def prefix_sentinel():
    a = [1, 2, 3, 4, 5, 6]
    p = prefix_sums(a)
    assert p == [0, 1, 3, 6, 10, 15, 21]
    assert p[3] - p[0] == 6
    s = Svg(470, 230, 'Array A = 1 to 6 above its prefix array P = 0, 1, 3, 6, 10, 15, 21; P has one extra slot at the '
                      'front, the sentinel 0, and each P entry is the one before it plus the A value above-left')
    mk = arrow_defs(s)
    x0, cw = 60, 48
    s.text(x0 - 10, 70, 'A', 15, INK, 'end', 'bold')
    cells(s, x0 + cw / 2, 47, a, cw, 36, idx=list(range(6)))
    s.text(x0 - 10, 150, 'P', 15, INK, 'end', 'bold')
    cells(s, x0 - cw / 2, 127, p, cw, 36, idx=list(range(7)), fills={0: ORANGE_BG}, strokes={0: ORANGE})
    for i in range(6):        # P[i+1] = P[i] + A[i]
        arrow(s, mk, x0 + cw / 2 + i * cw + cw / 2, 84, x0 - cw / 2 + (i + 1) * cw + cw / 2, 124, GREY, 1.2)
    s.text(x0 - cw / 2, 186, 'sentinel: the sum of nothing', 12, ORANGE, 'start', 'bold')
    s.text(235, 214, 'P[i+1] = P[i] + A[i].   Sum of A[0..2] = P[3] − P[0] = 6 − 0 = 6', 13, INK)
    s.save('pat-prefix-sentinel.svg', OUT)


def prefix_2d():
    grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    S = [[0] * 3 for _ in range(3)]
    for r in range(3):
        for c in range(3):
            S[r][c] = grid[r][c] + (S[r - 1][c] if r else 0) + (S[r][c - 1] if c else 0) - (S[r - 1][c - 1] if r and c else 0)
    r1, c1, r2, c2 = 1, 1, 2, 2
    parts = [S[r2][c2], S[r1 - 1][c2], S[r2][c1 - 1], S[r1 - 1][c1 - 1]]
    assert parts == [45, 6, 12, 1]
    total = parts[0] - parts[1] - parts[2] + parts[3]
    assert total == 28 == sum(grid[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))

    panels = [('S[2][2] = 45', 'whole', (0, 0, 2, 2), PIX, BLUE_BG, ''),
              ('S[0][2] = 6', 'top strip', (0, 0, 0, 2), TRUE, RED_BG, '−'),
              ('S[2][0] = 12', 'left strip', (0, 0, 2, 0), TRUE, RED_BG, '−'),
              ('S[0][0] = 1', 'corner, taken twice', (0, 0, 0, 0), ACCENT, GREEN_BG, '+'),
              ('= 28', 'the rectangle', (1, 1, 2, 2), ORANGE, ORANGE_BG, '=')]
    s = Svg(640, 200, 'Summing the rectangle (1,1) to (2,2) of the grid 1 to 9 with four lookups: the whole block 45, '
                      'minus the top strip 6, minus the left strip 12, plus the corner 1 that was taken away twice, '
                      'gives 28')
    pw, cs = 128, 30
    for k, (lab, sub, (a, b, c, d), col, bg, op) in enumerate(panels):
        x = 20 + k * pw
        if op and op != '':
            s.text(x - 8, 92, op, 22, INK, weight='bold')
        for r in range(3):
            for cc in range(3):
                inside = a <= r <= c and b <= cc <= d
                s.rect(x + 8 + cc * cs, 40 + r * cs, cs, cs, bg if inside else '#ffffff', INK, 1)
                s.text(x + 8 + cc * cs + cs / 2, 40 + r * cs + 20, grid[r][cc], 12, col if inside else GREY,
                       weight='bold' if inside else 'normal')
        s.rect(x + 8 + b * cs, 40 + a * cs, (d - b + 1) * cs, (c - a + 1) * cs, 'none', col, 2.6)
        s.text(x + 8 + 1.5 * cs, 158, lab, 13, col, weight='bold')
        s.text(x + 8 + 1.5 * cs, 176, sub, 11, MUTED)
    s.text(320, 22, '45 − 6 − 12 + 1 = 28   (check: 5 + 6 + 8 + 9 = 28)', 13, INK, weight='bold')
    s.save('pat-prefix-2d.svg', OUT)


# ---------- 02 two pointers ----------

def two_pointer_trace(nums, target):
    rows, l, r = [], 0, len(nums) - 1
    while l < r:
        t = nums[l] + nums[r]
        if t == target:
            rows.append((l, r, t, 'found'))
            return rows
        move = 'left++' if t < target else 'right--'
        rows.append((l, r, t, move))
        if t < target:
            l += 1
        else:
            r -= 1
    return rows


def two_pointers_steps():
    nums, target = [1, 2, 3, 4, 6], 6
    rows = two_pointer_trace(nums, target)
    assert [(l, r, t, m) for l, r, t, m in rows] == [(0, 4, 7, 'right--'), (0, 3, 5, 'left++'), (1, 3, 6, 'found')]
    s = Svg(560, 330, 'Two pointers on the sorted array 1, 2, 3, 4, 6 with target 6: step 1 sums 1 + 6 = 7, too big, '
                      'so right moves in; step 2 sums 1 + 4 = 5, too small, so left moves up; step 3 sums 2 + 4 = 6 '
                      'and finds indices 1 and 3')
    x0, cw, ch, rh = 80, 44, 34, 100
    notes = {'right--': ('too big: move right in', TRUE), 'left++': ('too small: move left up', PIX),
             'found': ('equals 6: found [1, 3]', ACCENT)}
    for k, (l, r, t, m) in enumerate(rows):
        y = 30 + k * rh
        s.text(20, y + 22, f'step {k + 1}', 12, MUTED, 'start')
        fills = {i: LIGHT for i in range(len(nums)) if i < l or i > r}
        fills[l] = fills[r] = GREEN_BG if m == 'found' else BLUE_BG
        colors = {i: GREY for i in range(len(nums)) if i < l or i > r}
        cells(s, x0, y, nums, cw, ch, fills=fills, colors=colors, idx=list(range(len(nums))) if k == 0 else None)
        pointer(s, x0 + l * cw + cw / 2, y + ch + 3, 'left', PIX)
        pointer(s, x0 + r * cw + cw / 2, y + ch + 3, 'right', TRUE)
        text, col = notes[m]
        s.text(x0 + len(nums) * cw + 24, y + 14, f'{nums[l]} + {nums[r]} = {t}', 14, INK, 'start', 'bold')
        s.text(x0 + len(nums) * cw + 24, y + 34, text, 12, col, 'start', 'bold')
    s.text(280, 320, 'Grey cells are ruled out: no pair that uses them can work.', 12, MUTED)
    s.save('pat-two-pointers-steps.svg', OUT)


# ---------- 03 sliding window ----------

def window_bracket(s, x, y, w, h, color):
    s.rect(x - 3, y - 3, w + 6, h + 6, 'none', color, 2.6)


def sliding_fixed():
    nums, k = [2, 1, 5, 1, 3, 2], 3
    sums = [sum(nums[:k])]
    for i in range(k, len(nums)):
        sums.append(sums[-1] + nums[i] - nums[i - k])
    assert sums == [8, 7, 9, 6] and max(sums) == 9
    best = sums.index(max(sums))
    s = Svg(560, 330, 'A window of size 3 sliding over 2, 1, 5, 1, 3, 2: sums 8, then 8 − 2 + 1 = 7, then 7 − 1 + 3 = 9 '
                      '(the best), then 9 − 5 + 2 = 6; each slide drops one number on the left and adds one on the right')
    x0, cw, ch, rh = 70, 40, 32, 72
    for w, total in enumerate(sums):
        y = 34 + w * rh
        fills = {i: (GREEN_BG if w == best else BLUE_BG) for i in range(w, w + k)}
        if w:
            fills[w - 1] = RED_BG
        cells(s, x0, y, nums, cw, ch, fills=fills, idx=list(range(len(nums))) if w == 0 else None)
        window_bracket(s, x0 + w * cw, y, k * cw, ch, ACCENT if w == best else PIX)
        if w:
            s.text(x0 + (w - 1) * cw + cw / 2, y + ch + 15, 'out', 11, TRUE, weight='bold')
            s.text(x0 + (w + k - 1) * cw + cw / 2, y + ch + 15, 'in', 11, PIX, weight='bold')
            calc = f'{sums[w - 1]} − {nums[w - 1]} + {nums[w + k - 1]} = {total}'
        else:
            calc = f'2 + 1 + 5 = {total}'
        s.text(x0 + len(nums) * cw + 24, y + 22, calc, 14, ACCENT if w == best else INK, 'start', 'bold')
        if w == best:
            s.text(x0 + len(nums) * cw + 150, y + 22, 'best', 13, ACCENT, 'start', 'bold')
    s.text(280, 318, 'Each slide costs one subtraction and one addition, whatever k is.', 12, MUTED)
    s.save('pat-sliding-fixed.svg', OUT)


def sliding_variable():
    nums = [1, 2, 3, 1, 2, 3, 1]
    seen, left, best, rows = set(), 0, 0, []
    for right in range(len(nums)):
        dropped = []
        while nums[right] in seen:
            seen.remove(nums[left])
            dropped.append(left)
            left += 1
        seen.add(nums[right])
        best = max(best, right - left + 1)
        rows.append((left, right, dropped, best))
    assert best == 3
    assert [(l, r) for l, r, _, _ in rows] == [(0, 0), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)]
    rh = 46
    s = Svg(530, 52 + rh * len(rows), 'A variable window over 1, 2, 3, 1, 2, 3, 1 looking for the longest run with no '
                                      'repeats: the right edge grows by one each step; when the new number is already '
                                      'inside, the left edge moves past the old copy; the longest window has length 3')
    x0, cw, ch = 90, 38, 30
    for k, (l, r, dropped, b) in enumerate(rows):
        y = 30 + k * rh
        s.text(20, y + 20, f'right = {r}', 12, MUTED, 'start')
        fills = {i: BLUE_BG for i in range(l, r + 1)}
        for d in dropped:
            fills[d] = RED_BG
        colors = {i: GREY for i in range(len(nums)) if i > r}
        cells(s, x0, y, nums, cw, ch, fills=fills, colors=colors, idx=list(range(len(nums))) if k == 0 else None)
        window_bracket(s, x0 + l * cw, y, (r - l + 1) * cw, ch, PIX)
        note = f'length {r - l + 1}'
        if dropped:
            note += f'  ({nums[r]} again: left to {l})'
        s.text(x0 + len(nums) * cw + 18, y + 20, note, 12, TRUE if dropped else INK, 'start', 'bold' if dropped else 'normal')
    s.text(265, 40 + rh * len(rows), 'Red cells just left the window. Longest window: 3.', 12, MUTED)
    s.save('pat-sliding-variable.svg', OUT)


# ---------- 04 fast and slow pointers ----------

def fast_slow():
    vals = [1, 3, 5, 7, 9]
    nxt = {1: 3, 3: 5, 5: 7, 7: 9, 9: 5}          # 9 points back to 5
    slow = fast = 1
    rows = [(slow, fast)]
    while True:
        slow, fast = nxt[slow], nxt[nxt[fast]]
        rows.append((slow, fast))
        if slow == fast:
            break
    assert [r[0] for r in rows] == [1, 3, 5, 7] and [r[1] for r in rows] == [1, 5, 9, 7]
    assert rows[-1] == (7, 7) and len(rows) - 1 == 3

    rh = 92
    s = Svg(560, 30 + rh * len(rows), 'The list 1, 3, 5, 7, 9 where 9 points back to 5, drawn four times: slow '
                                      'moves one node per step (1, 3, 5, 7) and fast moves two (1, 5, 9, 7); after '
                                      '3 steps both stand on node 7, so there is a cycle')
    mk = arrow_defs(s)
    x0, gap, r = 140, 84, 18
    for k, (sl, fa) in enumerate(rows):
        y = 50 + k * rh
        s.text(20, y + 5, 'start' if k == 0 else f'step {k}', 13, MUTED, 'start', 'bold')
        for i, v in enumerate(vals):
            cx = x0 + i * gap
            if i < len(vals) - 1:
                arrow(s, mk, cx + r + 2, y, cx + gap - r - 3, y, INK, 1.4)
            hit = v == sl or v == fa
            met = sl == fa == v and k
            s.circle(cx, y, r, GREEN_BG if met else (BLUE_BG if hit else '#ffffff'), INK)
            s.text(cx, y + 5, v, 14, INK, weight='bold')
        curved_arrow(s, mk, f'M{x0 + 4 * gap:.0f},{y + r + 2} C{x0 + 4 * gap - 10:.0f},{y + 52} '
                            f'{x0 + 2 * gap + 10:.0f},{y + 52} {x0 + 2 * gap + 4:.0f},{y + r + 3}', GREY, 1.3)
        xs, xf = x0 + vals.index(sl) * gap, x0 + vals.index(fa) * gap
        if sl == fa:
            s.text(xs, y - r - 8, 'slow + fast meet: cycle!' if k else 'slow + fast', 12, ACCENT, weight='bold')
        else:
            s.text(xs, y - r - 8, 'slow', 12, PIX, weight='bold')
            s.text(xf, y - r - 8, 'fast', 12, ORANGE, weight='bold')
    s.save('pat-fast-slow-cycle.svg', OUT)


# ---------- 05 linked list reversal ----------

def reversal_states(vals):
    """Run the lesson's reverse_list loop on a list of node values; record next pointers after each pass."""
    nxt = {v: (vals[i + 1] if i + 1 < len(vals) else None) for i, v in enumerate(vals)}
    states = [(dict(nxt), None, vals[0], None)]
    prev, curr = None, vals[0]
    while curr is not None:
        n = nxt[curr]
        nxt[curr] = prev
        changed = curr
        prev, curr = curr, n
        states.append((dict(nxt), prev, curr, changed))
    return states


def draw_list_row(s, mk, x0, y, vals, nxt, gap, changed=None, fills=None, none_left=(), r=17):
    """Nodes in a row with a None at each end; each next pointer is an arrow to its neighbour.
    A None pointer goes to the left None if the node is in none_left, else to the right None."""
    fills = fills or {}
    pos = {v: x0 + (i + 1) * gap for i, v in enumerate(vals)}
    left_none, right_none = x0, x0 + (len(vals) + 1) * gap
    for xn in (left_none, right_none):
        s.text(xn, y + 4, 'None', 11, MUTED)
    for v in vals:
        s.circle(pos[v], y, r, fills.get(v, '#ffffff'), INK)
        s.text(pos[v], y + 5, v, 13, INK, weight='bold')
    for v in vals:
        target = nxt[v]
        tx = pos[target] if target is not None else (left_none if v in none_left else right_none)
        col = ORANGE if v == changed else INK
        sgn = 1 if tx > pos[v] else -1
        dy = -6 if sgn > 0 else 6
        end_off = (r + 3) if target is not None else 17
        arrow(s, mk, pos[v] + sgn * (r - 2), y + dy, tx - sgn * end_off, y + dy, col, 2.4 if col == ORANGE else 1.4)
    return pos


def reversal_steps():
    vals = [1, 2, 3, 4, 5]
    states = reversal_states(vals)
    assert states[1][1:3] == (1, 2) and states[2][1:3] == (2, 3)
    assert states[-1][1] == 5 and states[-1][2] is None
    final = states[-1][0]
    head, out = 5, []
    while head is not None:
        out.append(head)
        head = final[head]
    assert out == [5, 4, 3, 2, 1]

    rh = 64
    s = Svg(560, 34 + rh * len(states), 'Reversing 1, 2, 3, 4, 5 one pass at a time: each pass turns one pointer '
                                         'round to point back at prev (in orange), then moves prev and curr one node '
                                         'right; after 5 passes every arrow points left and prev, node 5, is the new head')
    mk = arrow_defs(s)
    x0, gap = 105, 66
    for k, (nxt, prev, curr, changed) in enumerate(states):
        y = 36 + k * rh
        s.text(14, y + 5, 'before' if k == 0 else f'pass {k}', 13, MUTED, 'start', 'bold')
        fills = {}
        if prev is not None:
            fills[prev] = BLUE_BG
        if curr is not None:
            fills[curr] = GREEN_BG
        done = set(vals[:k])
        pos = draw_list_row(s, mk, x0, y, vals, nxt, gap, changed, fills, none_left=done)
        if prev is not None:
            s.text(pos[prev], y + 33, 'prev' + (' = new head' if curr is None else ''), 11, PIX, weight='bold')
        if curr is not None:
            s.text(pos[curr], y + 33, 'curr', 11, ACCENT, weight='bold')
    s.save('pat-reversal-steps.svg', OUT)


def reverse_sublist_vals(vals, m, n):
    """The lesson's reverse_sublist on a plain Python list of values, via next pointers and a dummy node."""
    nxt = {('d',): vals[0]}
    for i, v in enumerate(vals):
        nxt[v] = vals[i + 1] if i + 1 < len(vals) else None
    prev = ('d',)
    for _ in range(m - 1):
        prev = nxt[prev]
    curr = nxt[prev]
    for _ in range(n - m):
        x = nxt[curr]
        nxt[curr] = nxt[x]
        nxt[x] = nxt[prev]
        nxt[prev] = x
    out, h = [], nxt[('d',)]
    while h is not None:
        out.append(h)
        h = nxt[h]
    return out


def reversal_sketch_answer():
    vals = [7, 14, 21, 28, 35, 42]
    assert reverse_sublist_vals([1, 2, 3, 4, 5], 2, 4) == [1, 4, 3, 2, 5]
    out = reverse_sublist_vals(vals, 3, 5)
    assert out == [7, 14, 35, 28, 21, 42]
    s = Svg(560, 150, 'The list 7, 14, 21, 28, 35, 42 after reversing positions 3 to 5: 7, 14, 35, 28, 21, 42; the '
                      'reversed piece 35, 28, 21 is shaded, and the two stitched pointers, 14 to 35 and 21 to 42, are orange')
    mk = arrow_defs(s)
    x0, gap, y, r = 18, 84, 62, 20
    for i, v in enumerate(out):
        cx = x0 + i * gap + 30
        mid = 2 <= i <= 4
        s.circle(cx, y, r, ORANGE_BG if mid else '#ffffff', INK)
        s.text(cx, y + 5, v, 14, INK, weight='bold')
        s.text(cx, y - r - 8, f'pos {i + 1}', 10, MUTED)
        if i + 1 < len(out):
            stitch = i in (1, 4)
            arrow(s, mk, cx + r + 2, y, cx + gap - r - 3, y, ORANGE if stitch else INK, 2.6 if stitch else 1.4)
    s.text(x0 + len(out) * gap + 2, y + 5, 'None', 11, MUTED, 'start')
    s.rect(x0 + 2 * gap + 30 - 32, y + 30, 2 * gap + 64, 4, ORANGE)
    s.text(x0 + 3 * gap + 30, y + 54, 'positions 3 to 5, now reversed', 12, INK, weight='bold')
    s.text(280, 136, 'Orange arrows: 14 now points to 35, and 21 (the old start) now points to 42.', 12, MUTED)
    s.save('pat-reversal-sublist-answer.svg', OUT)


# ---------- 06 monotonic stack ----------

def mono_stack_trace(nums):
    result, stack, steps = [-1] * len(nums), [], []
    for i, num in enumerate(nums):
        pops = []
        while stack and nums[stack[-1]] < num:
            j = stack.pop()
            result[j] = num
            pops.append(j)
        stack.append(i)
        steps.append((i, num, pops, list(stack)))
    return result, steps


def mono_stack_steps():
    nums = [2, 1, 2, 4, 3]
    result, steps = mono_stack_trace(nums)
    assert result == [4, 2, 4, -1, -1]
    assert [st for _, _, _, st in steps] == [[0], [0, 1], [0, 2], [3], [3, 4]]
    cw, bh, bw = 108, 30, 70
    s = Svg(570, 330, 'The stack after each step of next greater element on 2, 1, 2, 4, 3: step 0 pushes index 0; '
                      'step 1 pushes 1; step 2 pops index 1 (answer 2) and pushes 2; step 3 pops 2 and 0 (answer 4 '
                      'for both) and pushes 3; step 4 pushes 4; the result is 4, 2, 4, -1, -1')
    base = 238
    for k, (i, num, pops, stack) in enumerate(steps):
        x = 20 + k * cw
        s.text(x + bw / 2 + 6, 24, f'i = {i}, num = {num}', 12, INK, weight='bold')
        for n, j in enumerate(pops):
            s.text(x + bw / 2 + 6, 46 + n * 17, f'pop {j}: result[{j}] = {num}', 11, TRUE, weight='bold')
        if not pops:
            s.text(x + bw / 2 + 6, 46, 'no pops', 11, MUTED)
        for h, j in enumerate(stack):
            y = base - (h + 1) * bh
            new = j == i
            s.rect(x + 6, y, bw, bh, GREEN_BG if new else BLUE_BG, INK, 1.2)
            s.text(x + 6 + bw / 2, y + 20, f'[{j}] = {nums[j]}', 12, INK, weight='bold' if new else 'normal')
        s.line(x, base, x + bw + 12, base, INK, 2)
        s.line(x + 6, base, x + 6, base - 3.6 * bh, GREY, 1)
        s.line(x + 6 + bw, base, x + 6 + bw, base - 3.6 * bh, GREY, 1)
    s.text(20, 262, 'Each stack lists index = value, bottom to top; values never rise going up. Green = just pushed.', 11, MUTED, 'start')
    s.text(20, 300, 'result', 13, INK, 'start', 'bold')
    cells(s, 80, 280, [str(v) for v in result], 44, 30, fills={j: GREEN_BG for j in range(5) if result[j] != -1},
          idx=None)
    s.text(310, 300, 'still on the stack at the end: -1', 11, MUTED, 'start')
    s.save('pat-mono-stack-steps.svg', OUT)


# ---------- 07 top-k elements ----------

def heap_tree(s, cx, y, arr, width, fills=None, strokes=None, r=15, lh=44):
    """Draw a heap array as a binary tree: index i has children 2i+1 and 2i+2."""
    fills, strokes = fills or {}, strokes or {}
    pos = {}
    for i in range(len(arr)):
        lvl = (i + 1).bit_length() - 1
        first = 2 ** lvl - 1
        slots = 2 ** lvl
        pos[i] = (cx - width / 2 + (i - first + 0.5) * width / slots, y + lvl * lh)
    for i in range(1, len(arr)):
        (x1, y1), (x2, y2) = pos[(i - 1) // 2], pos[i]
        s.line(x1, y1 + r, x2, y2 - r, INK, 1.2)
    for i, v in enumerate(arr):
        x, yy = pos[i]
        st = strokes.get(i)
        s.add(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r}" fill="{fills.get(i, BLUE_BG)}" '
              f'stroke="{st or INK}" stroke-width="{2.6 if st else 1.2}"/>')
        s.text(x, yy + 5, v, 13, INK, weight='bold')
    return pos


def topk_trace(nums, k):
    heap, steps = [], []
    for num in nums:
        heapq.heappush(heap, num)
        after_push = list(heap)
        popped = heapq.heappop(heap) if len(heap) > k else None
        steps.append((num, after_push, popped, list(heap)))
    return steps


def topk_heap_steps():
    nums, k = [3, 2, 1, 5, 6, 4], 2
    steps = topk_trace(nums, k)
    assert [p for _, _, p, _ in steps] == [None, None, 1, 2, 3, 4]
    assert steps[-1][3][0] == 5 and sorted(steps[-1][3]) == [5, 6]
    s = Svg(570, 380, 'A min-heap of size 2 finding the 2nd largest of 3, 2, 1, 5, 6, 4: each panel shows the heap '
                      'right after a push; once it holds 3 values the smallest, at the root, is popped (red): 1, then 2, '
                      'then 3, then 4; the heap ends as 5 and 6, and its root 5 is the answer')
    pw, ph = 190, 170
    for n, (num, pushed, popped, after) in enumerate(steps):
        x, y = (n % 3) * pw, (n // 3) * ph
        cx = x + pw / 2
        s.text(cx, y + 24, f'push {num}', 14, INK, weight='bold')
        new_i = pushed.index(num)
        fills = {0: RED_BG} if popped is not None else {}
        strokes = {new_i: ORANGE}
        heap_tree(s, cx, y + 50, pushed, 130, fills, strokes)
        if popped is not None:
            s.text(cx, y + 136, f'size 3 > 2: pop {popped}', 12, TRUE, weight='bold')
        else:
            s.text(cx, y + 136, 'size ≤ 2: keep', 12, MUTED)
        s.text(cx, y + 154, 'heap now ' + str(after).replace(' ', ''), 12, INK)
        if n % 3:
            s.line(x, y + 12, x, y + ph - 8, LIGHT, 1)
    s.line(10, ph, 560, ph, LIGHT, 1)
    s.text(285, 366, 'Orange ring = the value just pushed. Red root = the smallest, thrown out. Final root 5 = 2nd largest.',
           11, MUTED)
    s.save('pat-topk-heap-steps.svg', OUT)


def topk_sketch_answer():
    nums, k = [9, 4, 7, 1, 8, 2], 3
    steps = topk_trace(nums, k)
    push8 = [st for st in steps if st[0] == 8][0]
    assert push8[1] == [4, 8, 7, 9] and push8[2] == 4
    assert steps[-1][3] == [7, 8, 9]
    s = Svg(480, 210, 'Min-heap of size 3 over 9, 4, 7, 1, 8, 2: right after pushing 8 the heap is 4 at the root with '
                      'children 8 and 7, and 9 under 8, so 4 is popped; at the end the heap is 7 at the root with '
                      'children 8 and 9, and 7 is the 3rd largest')
    s.text(120, 26, 'just after push 8', 14, INK, weight='bold')
    heap_tree(s, 120, 56, push8[1], 170, {0: RED_BG}, {1: ORANGE})
    s.text(120, 172, 'array [4, 8, 7, 9]: root 4 gets popped', 12, TRUE)
    s.text(360, 26, 'at the end', 14, INK, weight='bold')
    heap_tree(s, 360, 56, steps[-1][3], 170, {0: GREEN_BG})
    s.text(360, 172, 'array [7, 8, 9]: root 7 = 3rd largest', 12, ACCENT)
    s.line(240, 14, 240, 190, LIGHT, 1)
    s.save('pat-topk-sketch-answer.svg', OUT)


# ---------- 08 overlapping intervals ----------

def merge_intervals(intervals):
    intervals = sorted(intervals, key=lambda pair: pair[0])
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def interval_timeline(intervals, lo, hi, name, title, note):
    ivs = sorted(intervals, key=lambda p: p[0])
    merged = merge_intervals(ivs)
    rh = 30
    ytop = 30
    ya = ytop + len(ivs) * rh + 6
    h = ya + 112
    s = Svg(560, h, title)
    x0, x1 = 70, 540
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    for v in range(lo, hi + 1, 2):
        s.line(X(v), ytop - 14, X(v), ya, '#f1f5f9', 1)
    s.text(x0 - 10, ytop + 4, 'sorted', 12, MUTED, 'end')
    for i, (a, b) in enumerate(ivs):
        y = ytop + i * rh
        grp = next(k for k, (ma, mb) in enumerate(merged) if ma <= a and b <= mb)
        col = (PIX, ORANGE, ACCENT, TRUE)[grp % 4]
        s.rect(X(a), y - 8, X(b) - X(a), 16, col, 'none', 1, 0.85)
        s.text(X(b) + 6, y + 5, f'[{a}, {b}]', 11, INK, 'start')
    s.line(x0, ya, x1, ya, INK, 1.2)
    for v in range(lo, hi + 1):
        big = v % 2 == 0
        s.line(X(v), ya, X(v), ya + (6 if big else 3), INK, 1)
        if big:
            s.text(X(v), ya + 19, v, 10, MUTED)
    ym = ya + 46
    s.text(x0 - 10, ym + 4, 'merged', 12, INK, 'end', 'bold')
    for k, (a, b) in enumerate(merged):
        col = (PIX, ORANGE, ACCENT, TRUE)[k % 4]
        s.rect(X(a), ym - 10, X(b) - X(a), 20, col, INK, 1.2)
        s.text((X(a) + X(b)) / 2, ym + 28, f'[{a}, {b}]', 12, col, weight='bold')
    s.text(280, h - 10, note, 11, MUTED)
    s.save(name, OUT)
    return merged


def intervals_merge():
    ivs = [[1, 3], [2, 6], [8, 10], [15, 18]]
    m = interval_timeline(ivs, 0, 19, 'pat-intervals-merge.svg',
                          'The intervals 1 to 3, 2 to 6, 8 to 10 and 15 to 18 on a timeline; 1 to 3 and 2 to 6 overlap '
                          'and merge into 1 to 6, while 8 to 10 and 15 to 18 stay on their own',
                          'Bars of one colour overlap and become one merged bar.')
    assert m == [[1, 6], [8, 10], [15, 18]]


def intervals_sketch_answer():
    ivs = [[3, 7], [1, 2], [6, 9], [12, 14], [13, 16], [10, 11]]
    m = interval_timeline(ivs, 0, 17, 'pat-intervals-sketch-answer.svg',
                          'The intervals 1 to 2, 3 to 7, 6 to 9, 10 to 11, 12 to 14 and 13 to 16 sorted on a timeline; '
                          'they merge into 1 to 2, 3 to 9, 10 to 11 and 12 to 16',
                          '2 and 3 do not touch, nor do 9 and 10 or 11 and 12, so those stay apart.')
    assert m == [[1, 2], [3, 9], [10, 11], [12, 16]]


# ---------- 09 modified binary search ----------

def rotated_trace(nums, target):
    rows, left, right = [], 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            rows.append((left, mid, right, None, 'found'))
            return rows
        if nums[left] <= nums[mid]:
            half = (left, mid)
            go = 'left' if nums[left] <= target < nums[mid] else 'right'
        else:
            half = (mid, right)
            go = 'right' if nums[mid] < target <= nums[right] else 'left'
        rows.append((left, mid, right, half, go))
        if go == 'left':
            right = mid - 1
        else:
            left = mid + 1
    return rows


def rotated_search():
    nums, target = [4, 5, 6, 7, 0, 1, 2], 0
    rows = rotated_trace(nums, target)
    assert [(l, m, r) for l, m, r, _, _ in rows] == [(0, 3, 6), (4, 5, 6), (4, 4, 4)]
    assert rows[-1][4] == 'found' and rows[-1][1] == 4
    s = Svg(570, 340, 'Searching for 0 in the rotated array 4, 5, 6, 7, 0, 1, 2: round 1 has mid 7 and the sorted half '
                      '4 to 7 cannot hold 0, so go right; round 2 has mid 1 and the sorted half 0 to 1 can hold 0, so '
                      'go left; round 3 has mid 0, found at index 4')
    x0, cw, ch, rh = 80, 44, 34, 100
    notes = [('sorted half 4..7 can\'t hold 0', 'go right: left = 4'),
             ('sorted half 0..1 can hold 0', 'go left: right = 4'),
             ('nums[4] = 0', 'found at index 4')]
    for k, (l, m, r, half, go) in enumerate(rows):
        y = 34 + k * rh
        s.text(16, y + 22, f'round {k + 1}', 12, MUTED, 'start')
        fills = {i: LIGHT for i in range(len(nums)) if i < l or i > r}
        colors = {i: GREY for i in range(len(nums)) if i < l or i > r}
        if half:
            for i in range(half[0], half[1] + 1):
                fills[i] = GREEN_BG
        strokes = {m: ORANGE}
        if go == 'found':
            fills[m] = GREEN_BG
            strokes = {m: ACCENT}
        cells(s, x0, y, nums, cw, ch, fills=fills, colors=colors, strokes=strokes,
              idx=list(range(len(nums))) if k == 0 else None)
        labels = {}
        for name, i in (('left', l), ('mid', m), ('right', r)):
            labels.setdefault(i, []).append(name)
        for i, names in labels.items():
            col = ORANGE if 'mid' in names else (PIX if names == ['left'] else TRUE if names == ['right'] else INK)
            pointer(s, x0 + i * cw + cw / 2, y + ch + 3, ' + '.join(names), col, size=11)
        a, b = notes[k]
        s.text(x0 + len(nums) * cw + 16, y + 14, a, 12, INK, 'start')
        s.text(x0 + len(nums) * cw + 16, y + 32, b, 12, ACCENT if go == 'found' else PIX, 'start', 'bold')
    s.text(285, 330, 'Green = the half that is in normal sorted order. Grey = ruled out.', 11, MUTED)
    s.save('pat-rotated-search.svg', OUT)


# ---------- 10 binary tree traversal ----------

def orders(tree, root):
    """tree: node -> (left, right). Returns preorder, inorder, postorder lists."""
    pre, ino, post = [], [], []

    def go(n):
        if n is None:
            return
        left, right = tree.get(n, (None, None))
        pre.append(n)
        go(left)
        ino.append(n)
        go(right)
        post.append(n)
    go(root)
    return pre, ino, post


def bt_dot_body(tree, root, prefix='', xlabels=None, fills=None, strokes=None, edge_labels=None):
    """Graphviz lines for a binary tree, keeping left/right sides with invisible placeholders."""
    xlabels, fills, strokes, edge_labels = xlabels or {}, fills or {}, strokes or {}, edge_labels or {}
    lines, stack, inv = [], [root], 0
    while stack:
        n = stack.pop()
        if n in xlabels:
            attrs = [f'label=<<b>{n}</b><br/><font point-size="10" color="#b45309">#{xlabels[n]}</font>>', 'width=0.6']
        else:
            attrs = [f'label="{n}"']
        if n in fills:
            attrs.append(f'fillcolor="{fills[n]}"')
        if n in strokes:
            attrs.append(f'color="{strokes[n]}", penwidth=2.6')
        lines.append(f'"{prefix}{n}" [{", ".join(attrs)}];')
        left, right = tree.get(n, (None, None))
        if left is None and right is None:
            continue
        for c in (left, right):
            if c is None:
                inv += 1
                lines.append(f'"{prefix}inv{n}_{inv}" [style=invis, label=""]; '
                             f'"{prefix}{n}" -> "{prefix}inv{n}_{inv}" [style=invis];')
            else:
                lab = f' [label=" {edge_labels[(n, c)]} "]' if (n, c) in edge_labels else ''
                lines.append(f'"{prefix}{n}" -> "{prefix}{c}"{lab};')
        stack.extend(c for c in (right, left) if c is not None)
    return lines


def traversal_orders():
    tree = {1: (2, 3), 2: (4, 5)}
    pre, ino, post = orders(tree, 1)
    assert pre == [1, 2, 4, 5, 3] and ino == [4, 2, 5, 1, 3] and post == [4, 5, 2, 3, 1]
    lines = dot_header('forcelabels=true; newrank=true; ranksep=0.4; nodesep=0.3;')
    for k, (name, order) in enumerate((('preorder: node, left, right', pre), ('inorder: left, node, right', ino),
                                       ('postorder: left, right, node', post))):
        lines.append(f'subgraph cluster{k} {{ label=<<b>{name}</b><br/>{", ".join(map(str, order))}>; '
                     f'labelloc=b; fontname="{FONT}"; fontsize=13; color="{LIGHT}"; margin=14;')
        lines += bt_dot_body(tree, 1, prefix=f't{k}_', xlabels={v: i + 1 for i, v in enumerate(order)})
        lines.append('}')
    lines.append('}')
    save_dot('\n'.join(lines), 'pat-tree-orders.svg',
             'The tree 1 with children 2 and 3, and 2 with children 4 and 5, drawn three times; the orange number '
             'by each node is when it is visited: preorder 1, 2, 4, 5, 3; inorder 4, 2, 5, 1, 3; postorder 4, 5, 2, 3, 1',
             OUT)


def traversal_sketch_answer():
    tree = {7: (3, 11), 3: (1, 5), 11: (None, 13)}
    pre, ino, post = orders(tree, 7)
    assert post == [1, 5, 3, 13, 11, 7]
    lines = dot_header('forcelabels=true;')
    lines += bt_dot_body(tree, 7, xlabels={v: i + 1 for i, v in enumerate(post)})
    lines.append('}')
    save_dot('\n'.join(lines), 'pat-tree-sketch-answer.svg',
             'The tree with root 7: 7 has left child 3 and right child 11; 3 has children 1 and 5; 11 has a right child '
             '13. Orange numbers give the postorder: 1, 5, 3, 13, 11, 7', OUT)


# ---------- 11 DFS pattern ----------

def find_order(num_courses, prerequisites):
    """The lesson's DFS topological sort; also returns the finish order (postorder)."""
    graph = {i: [] for i in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    visited, visiting, order = set(), set(), []

    def dfs(node):
        if node in visiting:
            return False
        if node in visited:
            return True
        visiting.add(node)
        for nb in graph[node]:
            if not dfs(nb):
                return False
        visiting.remove(node)
        visited.add(node)
        order.append(node)
        return True

    for c in range(num_courses):
        if c not in visited and not dfs(c):
            return [], []
    return order[::-1], order


def topo_picture(n, prereqs, name, title, caption):
    result, finish = find_order(n, prereqs)
    lines = dot_header('rankdir=LR; ranksep=0.6; nodesep=0.35;')
    lines[1] = lines[1].replace('width=0.45', 'width=0.62')
    for v in range(n):
        lines.append(f'{v} [label=<<b>{v}</b><br/><font point-size="10" color="#b45309">done #{finish.index(v) + 1}</font>>];')
    for course, prereq in prereqs:
        lines.append(f'{prereq} -> {course};')
    lines.append(f'label=<{caption}<br/><b>order: {", ".join(map(str, result))}</b>>; labelloc=b; '
                 f'fontname="{FONT}"; fontsize=13;')
    lines.append('}')
    save_dot('\n'.join(lines), name, title, OUT)
    return result, finish


def dfs_topo():
    result, finish = topo_picture(
        4, [[1, 0], [2, 0], [3, 1], [3, 2]], 'pat-dfs-topo.svg',
        'Course graph with arrows 0 to 1, 0 to 2, 1 to 3 and 2 to 3; DFS from 0 finishes 3 first, then 1, then 2, '
        'then 0, and reading the finish order backwards gives the course order 0, 2, 1, 3',
        'finish order 3, 1, 2, 0, read backwards')
    assert finish == [3, 1, 2, 0] and result == [0, 2, 1, 3]


def dfs_sketch_answer():
    result, finish = topo_picture(
        5, [[1, 0], [2, 0], [3, 1], [4, 3], [4, 2]], 'pat-dfs-sketch-answer.svg',
        'Course graph with arrows 0 to 1, 0 to 2, 1 to 3, 3 to 4 and 2 to 4; DFS from 0 finishes 4, 3, 1, 2, 0 in '
        'that order, so the course order is 0, 2, 1, 3, 4',
        'finish order 4, 3, 1, 2, 0, read backwards')
    assert finish == [4, 3, 1, 2, 0] and result == [0, 2, 1, 3, 4]


# ---------- 12 BFS pattern ----------

LEVEL_FILLS = [BLUE_BG, GREEN_BG, ORANGE_BG, '#ede9fe', RED_BG]


def level_order(tree, root):
    from collections import deque
    result, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft()
            level.append(n)
            for c in tree.get(n, (None, None)):
                if c is not None:
                    q.append(c)
        result.append(level)
    return result


def bfs_levels():
    tree = {3: (9, 20), 20: (15, 7)}
    levels = level_order(tree, 3)
    assert levels == [[3], [9, 20], [15, 7]]
    fills = {v: LEVEL_FILLS[d] for d, lvl in enumerate(levels) for v in lvl}
    lines = dot_header('ranksep=0.4;')
    lines += bt_dot_body(tree, 3, fills=fills)
    for d, lvl in enumerate(levels):
        lines.append(f'L{d} [shape=box, style="rounded,filled", fixedsize=false, width=1.6, fillcolor="{LEVEL_FILLS[d]}", '
                     f'color="{LEVEL_FILLS[d]}", fontsize=12, label="level {d}: {", ".join(map(str, lvl))}"];')
        lines.append(f'{{rank=same; L{d}; "{lvl[0]}";}}')
        if d:
            lines.append(f'L{d - 1} -> L{d} [style=invis];')
    lines.append('}')
    save_dot('\n'.join(lines), 'pat-bfs-levels.svg',
             'The tree 3 with children 9 and 20, and 20 with children 15 and 7, coloured by level: level 0 is 3, '
             'level 1 is 9 and 20, level 2 is 15 and 7, which is exactly what level-order BFS returns', OUT)


def rot(grid):
    """The lesson's multi-source BFS; returns minutes and the minute each cell rotted (0 = rotten at start)."""
    from collections import deque
    g = [row[:] for row in grid]
    rows, cols = len(g), len(g[0])
    q, fresh, when = deque(), 0, {}
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == 2:
                q.append((r, c))
                when[(r, c)] = 0
            elif g[r][c] == 1:
                fresh += 1
    minutes = 0
    while q and fresh:
        minutes += 1
        for _ in range(len(q)):
            r, c = q.popleft()
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:
                    g[nr][nc] = 2
                    fresh -= 1
                    when[(nr, nc)] = minutes
                    q.append((nr, nc))
    return (minutes if fresh == 0 else -1), when


ROT, FRESH, EMPTY = '#b45309', '#fde68a', '#f3f4f6'


def orange_grid(s, x, y, grid, when, upto, cs=34, show_minutes=False):
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            px, py = x + c * cs, y + r * cs
            if v == 0:
                s.rect(px, py, cs, cs, EMPTY, GREY, 1)
                continue
            rotten = (r, c) in when and when[(r, c)] <= upto
            new = rotten and when[(r, c)] == upto and upto > 0
            s.rect(px, py, cs, cs, '#ffffff', GREY, 1)
            s.circle(px + cs / 2, py + cs / 2, cs * 0.36, ROT if rotten else FRESH, INK)
            if show_minutes and (r, c) in when:
                s.text(px + cs / 2, py + cs / 2 + 5, when[(r, c)], 13, '#ffffff', weight='bold')
            if new:
                s.rect(px + 1.5, py + 1.5, cs - 3, cs - 3, 'none', ORANGE, 2.6)


def bfs_rotting():
    grid = [[2, 1, 1], [1, 1, 0], [0, 1, 1]]
    minutes, when = rot(grid)
    assert minutes == 4
    s = Svg(570, 190, 'Rotting oranges on the grid 2 1 1 / 1 1 0 / 0 1 1, one panel per minute: minute 1 rots the two '
                      'neighbours of the corner, and the rot spreads one step per minute until the last orange, '
                      'bottom right, rots at minute 4')
    pw = 112
    for m in range(minutes + 1):
        x = 14 + m * pw
        s.text(x + 51, 24, 'start' if m == 0 else f'minute {m}', 13, INK, weight='bold')
        orange_grid(s, x, 36, grid, when, m)
        left = sum(1 for r, row in enumerate(grid) for c, v in enumerate(row) if v and when[(r, c)] > m)
        s.text(x + 51, 160, f'{left} fresh left', 11, MUTED)
    s.text(285, 182, 'Brown = rotten, yellow = fresh, grey = empty. Orange ring = rotted this minute.', 11, MUTED)
    s.save('pat-bfs-rotting.svg', OUT)


def bfs_sketch_answer():
    grid = [[1, 1, 0, 2], [1, 0, 1, 1], [2, 1, 1, 0]]
    minutes, when = rot(grid)
    assert minutes == 3
    assert [when[k] for k in ((1, 0), (2, 1), (1, 3), (0, 0), (1, 2), (2, 2), (0, 1))] == [1, 1, 1, 2, 2, 2, 3]
    s = Svg(300, 190, 'The grid 1 1 0 2 / 1 0 1 1 / 2 1 1 0 with the minute each orange rots written on it: both '
                      'rotten oranges start at 0; three oranges rot at minute 1, three more at minute 2, and the '
                      'top one in column 1 last, at minute 3, so the answer is 3 minutes')
    orange_grid(s, 60, 20, grid, when, 99, cs=44, show_minutes=True)
    s.text(150, 176, 'number = minute that orange rots; answer: 3', 12, INK, weight='bold')
    s.save('pat-bfs-sketch-answer.svg', OUT)


# ---------- 13 matrix traversal ----------

DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]       # right, left, down, up, as in the lesson
PAINT = {0: '#f3f4f6', 1: '#bfdbfe', 2: '#86efac'}


def flood_fill_order(image, sr, sc, new):
    img = [row[:] for row in image]
    old, rows, cols, order = img[sr][sc], len(img), len(img[0]), []

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols) or img[r][c] != old:
            return
        img[r][c] = new
        order.append((r, c))
        for dr, dc in DIRS:
            dfs(r + dr, c + dc)
    dfs(sr, sc)
    return img, order


def value_grid(s, x, y, grid, cs, fills, labels=None, strokes=None, small=None):
    labels, strokes, small = labels or {}, strokes or {}, small or {}
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            s.rect(x + c * cs, y + r * cs, cs, cs, fills(r, c, v), GREY, 1)
            s.text(x + c * cs + cs / 2, y + r * cs + cs / 2 + 5, labels.get((r, c), v), 14, INK, weight='bold')
            if (r, c) in small:
                s.text(x + c * cs + cs - 4, y + r * cs + 12, small[(r, c)], 10, '#b45309', 'end', 'bold')
    for (r, c), col in strokes.items():
        s.rect(x + c * cs + 1.5, y + r * cs + 1.5, cs - 3, cs - 3, 'none', col, 2.6)


def matrix_flood():
    image = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
    out, order = flood_fill_order(image, 1, 1, 2)
    assert out == [[2, 2, 2], [2, 2, 0], [2, 0, 1]]
    assert len(order) == 6 and order[0] == (1, 1)
    s = Svg(460, 230, 'Flood fill from row 1, col 1 with colour 2 on the image 1 1 1 / 1 1 0 / 1 0 1: the six 1s joined '
                      'to the start turn into 2 (small numbers give the order DFS paints them), while the 1 in the '
                      'bottom-right corner is cut off by 0s and stays 1')
    cs = 52
    s.text(100, 26, 'before', 14, INK, weight='bold')
    value_grid(s, 22, 40, image, cs, lambda r, c, v: PAINT[v], strokes={(1, 1): ORANGE})
    s.text(100, 216, 'start: row 1, col 1', 12, ORANGE, weight='bold')
    s.text(360, 26, 'after', 14, INK, weight='bold')
    value_grid(s, 282, 40, out, cs, lambda r, c, v: PAINT[v],
               small={rc: f'#{i + 1}' for i, rc in enumerate(order)})
    s.text(360, 216, 'small number = paint order', 12, '#b45309')
    s.text(230, 120, '→', 30, INK, weight='bold')
    s.save('pat-matrix-flood.svg', OUT)


def islands(grid):
    rows, cols, seen, comps = len(grid), len(grid[0]), set(), []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r, c) not in seen:
                comp, st = [], [(r, c)]
                seen.add((r, c))
                while st:
                    a, b = st.pop()
                    comp.append((a, b))
                    for dr, dc in DIRS:
                        na, nb = a + dr, b + dc
                        if 0 <= na < rows and 0 <= nb < cols and grid[na][nb] == '1' and (na, nb) not in seen:
                            seen.add((na, nb))
                            st.append((na, nb))
                comps.append(((r, c), comp))
    return comps


def matrix_islands():
    grid = [list('11000'), list('11000'), list('00100'), list('00011')]
    comps = islands(grid)
    assert len(comps) == 3 and max(len(c) for _, c in comps) == 4
    cols = [BLUE_BG, ORANGE_BG, GREEN_BG]
    owner = {cell: k for k, (_, comp) in enumerate(comps) for cell in comp}
    s = Svg(420, 260, 'The lab grid with three islands, each in its own colour: a 2 by 2 block top left (area 4), a '
                      'single cell in the middle, and two cells bottom right; the outlined cell in each is where the '
                      'scan started a new DFS and added 1 to the count')
    cs = 44
    value_grid(s, 40, 30, grid, cs, lambda r, c, v: cols[owner[(r, c)]] if v == '1' else '#ffffff',
               strokes={start: ORANGE for start, _ in comps},
               small={start: f'#{k + 1}' for k, (start, _) in enumerate(comps)})
    for k, (start, comp) in enumerate(comps):
        s.text(300, 60 + k * 40, f'island {k + 1}: {len(comp)} cell' + ('s' if len(comp) > 1 else ''), 13, INK,
               'start', 'bold')
        s.rect(276, 46 + k * 40, 18, 18, cols[k], GREY, 1)
    s.text(210, 232, 'Orange outline = a cell where the scan starts a new DFS (count + 1).', 11, MUTED)
    s.save('pat-matrix-islands.svg', OUT)


# ---------- 14 backtracking ----------

def box_tree_dot(nodes, edges, title, name, extra=''):
    """nodes: list of (id, label, fill, stroke or None). edges: (a, b, label)."""
    lines = [f'digraph {{ bgcolor="white"; pad=0.25; nodesep=0.18; ranksep=0.4; {extra}',
             f'node [fontname="{FONT}", fontsize=12, shape=box, style="rounded,filled", color="{INK}", '
             f'penwidth=1.2, margin="0.08,0.04"];',
             f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];']
    for i, lab, fill, stroke in nodes:
        st = f', color="{stroke}", penwidth=2.4' if stroke else ''
        lines.append(f'n{i} [label=<{lab}>, fillcolor="{fill}"{st}];')
    for a, b, lab in edges:
        lines.append(f'n{a} -> n{b} [label=" {lab} "];' if lab else f'n{a} -> n{b};')
    lines.append('}')
    save_dot('\n'.join(lines), name, title, OUT)


def fmt(path):
    return '[' + ', '.join(map(str, path)) + ']'


def permutation_tree():
    nums = [1, 2, 3]
    nodes, edges, result, ids = [], [], [], iter(range(100))

    def backtrack(path, remaining, parent, choice):
        me = next(ids)
        if parent is not None:
            edges.append((parent, me, f'choose {choice}'))
        if not remaining:
            result.append(path[:])
            nodes.append((me, f'<b>{fmt(path)}</b><br/><font point-size="10" color="#065f46">record #{len(result)}</font>',
                          GREEN_BG, None))
            return
        nodes.append((me, fmt(path) if path else '[ ]', BLUE_BG, None))
        for i in range(len(remaining)):
            path.append(remaining[i])
            backtrack(path, remaining[:i] + remaining[i + 1:], me, remaining[i])
            path.pop()
    backtrack([], nums, None, None)
    assert result == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    assert len(nodes) == 16
    box_tree_dot(nodes, edges, 'The decision tree for permutations of 1, 2, 3: from the empty path, choose 1, 2 or 3; '
                 'each child chooses from what is left; the six leaves, recorded in order, are 1 2 3, 1 3 2, 2 1 3, '
                 '2 3 1, 3 1 2 and 3 2 1', 'pat-backtrack-permutations.svg')


def subsets_tree(nums, name, title):
    nodes, edges, result, ids = [], [], [], iter(range(100))

    def backtrack(start, path, parent, choice):
        me = next(ids)
        result.append(path[:])
        if parent is not None:
            edges.append((parent, me, f'add {choice}'))
        nodes.append((me, f'<b>{fmt(path) if path else "[ ]"}</b><br/><font point-size="10" color="#065f46">'
                          f'record #{len(result)}</font>', GREEN_BG, None))
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path, me, nums[i])
            path.pop()
    backtrack(0, [], None, None)
    box_tree_dot(nodes, edges, title, name)
    return result


def backtrack_sketch_answer():
    res = subsets_tree([7, 8, 9], 'pat-backtrack-subsets-answer.svg',
                       'The subsets recursion tree for 7, 8, 9: the empty set at the root; its children add 7, 8 or 9; '
                       'below 7 come 7 8 (then 7 8 9) and 7 9; below 8 comes 8 9; every node is recorded, in the order '
                       'empty, 7, 7 8, 7 8 9, 7 9, 8, 8 9, 9')
    assert res == [[], [7], [7, 8], [7, 8, 9], [7, 9], [8], [8, 9], [9]]


# ---------- 15 dynamic programming ----------

def fib_call_tree():
    nodes, edges, calls, ids = [], [], {}, iter(range(100))

    def fib(n, parent):
        me = next(ids)
        calls[n] = calls.get(n, 0) + 1
        nodes.append((me, n))
        if parent is not None:
            edges.append((parent, me))
        if n <= 1:
            return n
        return fib(n - 1, me) + fib(n - 2, me)
    assert fib(5, None) == 5
    assert calls == {5: 1, 4: 1, 3: 2, 2: 3, 1: 5, 0: 3} and len(nodes) == 15
    seen, out = set(), []
    for i, n in nodes:
        repeat = n in seen and n >= 2
        seen.add(n)
        fill = RED_BG if repeat else (LIGHT if n <= 1 else BLUE_BG)
        out.append((i, f'fib({n})', fill, TRUE if repeat else None))
    box_tree_dot(out, [(a, b, '') for a, b in edges],
                 'The call tree of naive fib(5): 15 calls; fib(3) is worked out twice and fib(2) three times; the red '
                 'boxes are repeats that memoization would answer from the cache instead', 'pat-dp-fib-tree.svg',
                 'nodesep=0.12; ranksep=0.3;')


def coin_change_table():
    coins, amount = [1, 2, 5], 11
    dp, pick = [0] + [float('inf')] * amount, [None] * (amount + 1)
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and 1 + dp[a - c] < dp[a]:
                dp[a], pick[a] = 1 + dp[a - c], c
    assert dp[amount] == 3
    chain, a = [], amount
    while a:
        chain.append(a)
        a -= pick[a]
    chain.append(0)
    assert chain == [11, 10, 5, 0]
    s = Svg(600, 210, 'The coin change table for coins 1, 2 and 5 up to amount 11: fewest coins are 0, 1, 1, 2, 2, 1, 2, '
                      '2, 3, 3, 2, 3; dp[11] = 3, traced back as 11 minus 1 is 10, 10 minus 5 is 5, 5 minus 5 is 0')
    mk = arrow_defs(s)
    x0, cw = 40, 44
    s.text(x0 - 8, 78, 'dp', 14, INK, 'end', 'bold')
    cells(s, x0, 55, [int(v) for v in dp], cw, 36, idx=[f'a={a}' if a == 0 else a for a in range(amount + 1)],
          fills={a: (GREEN_BG if a == amount else ORANGE_BG) for a in chain}, strokes={amount: ACCENT})
    for a in chain[:-1]:
        b = a - pick[a]
        xa, xb = x0 + a * cw + cw / 2, x0 + b * cw + cw / 2
        curved_arrow(s, mk, f'M{xa:.1f},{91 + 2} Q{(xa + xb) / 2:.1f},{150} {xb:.1f},{93}', ORANGE, 1.8)
        s.text((xa + xb) / 2, 138, f'− {pick[a]}', 12, '#b45309', weight='bold')
    s.text(300, 176, 'dp[a] = 1 + min(dp[a − c]) over coins c ≤ a.  Fewest coins for 11: 1 + 5 + 5 = 3 coins.', 13, INK)
    s.text(300, 198, 'Orange arrows follow the coin that gave each best answer back to 0.', 11, MUTED)
    s.save('pat-dp-coin-change.svg', OUT)


def lcs_table():
    a, b = 'abcde', 'ace'
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            dp[i][j] = 1 + dp[i + 1][j + 1] if a[i] == b[j] else max(dp[i + 1][j], dp[i][j + 1])
    assert dp[0][0] == 3
    cs = 42
    s = Svg(420, 316, 'The LCS table for abcde and ace, filled from the bottom-right corner: each cell holds the LCS of '
                      'the two suffixes starting there; green cells are letter matches (a, c, e) that take the diagonal '
                      'plus 1; the top-left cell holds the answer, 3')
    mk = arrow_defs(s)
    x0, y0 = 90, 50
    for j, ch in enumerate(b + '·'):
        s.text(x0 + j * cs + cs / 2, y0 - 10, ch if ch != '·' else 'end', 13 if ch != '·' else 10, INK if ch != '·' else MUTED,
               weight='bold')
    for i, ch in enumerate(a + '·'):
        s.text(x0 - 12, y0 + i * cs + cs / 2 + 5, ch if ch != '·' else 'end', 13 if ch != '·' else 10,
               INK if ch != '·' else MUTED, 'end', 'bold')
    for i in range(len(a) + 1):
        for j in range(len(b) + 1):
            match = i < len(a) and j < len(b) and a[i] == b[j]
            fill = GREEN_BG if match else ('#f9fafb' if i == len(a) or j == len(b) else '#ffffff')
            s.rect(x0 + j * cs, y0 + i * cs, cs, cs, fill, GREY, 1)
            s.text(x0 + j * cs + cs / 2, y0 + i * cs + cs / 2 + 5, dp[i][j], 14,
                   INK if i < len(a) and j < len(b) else GREY, weight='bold' if match else 'normal')
            if match:
                arrow(s, mk, x0 + j * cs + cs - 13, y0 + i * cs + cs - 13, x0 + j * cs + cs + 12, y0 + i * cs + cs + 12,
                      ACCENT, 1.8)
    s.rect(x0 + 1.5, y0 + 1.5, cs - 3, cs - 3, 'none', ORANGE, 2.6)
    s.text(x0 + 4 * cs + 24, y0 + 20, 'answer: 3', 13, '#b45309', 'start', 'bold')
    s.text(x0 + 4 * cs + 24, y0 + 40, '("ace")', 12, MUTED, 'start')
    s.text(x0 + 4 * cs + 24, y0 + 90, 'green = letters match:', 11, ACCENT, 'start', 'bold')
    s.text(x0 + 4 * cs + 24, y0 + 106, '1 + the cell down-right', 11, MUTED, 'start')
    s.text(x0 + 4 * cs + 24, y0 + 130, 'otherwise: the bigger of', 11, MUTED, 'start')
    s.text(x0 + 4 * cs + 24, y0 + 146, 'below and right', 11, MUTED, 'start')
    s.save('pat-dp-lcs-table.svg', OUT)


def unique_paths_answer():
    R, C = 3, 4
    dp = [[1] * C for _ in range(R)]
    for r in range(1, R):
        for c in range(1, C):
            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
    assert dp == [[1, 1, 1, 1], [1, 2, 3, 4], [1, 3, 6, 10]]
    cs = 56
    s = Svg(330, 245, 'The Unique Paths table for a 3 by 4 grid: the top row and left column are all 1; each other cell '
                      'is the cell above plus the cell to its left, giving 1 2 3 4 in row 1 and 1 3 6 10 in row 2; the '
                      'bottom-right cell, 10, is the answer')
    x0, y0 = 50, 30
    for r in range(R):
        for c in range(C):
            base = r == 0 or c == 0
            s.rect(x0 + c * cs, y0 + r * cs, cs, cs, LIGHT if base else BLUE_BG, GREY, 1)
            s.text(x0 + c * cs + cs / 2, y0 + r * cs + cs / 2 + 6, dp[r][c], 16, INK, weight='bold')
    s.rect(x0 + 3 * cs + 1.5, y0 + 2 * cs + 1.5, cs - 3, cs - 3, 'none', ORANGE, 2.8)
    s.rect(x0 + 2 * cs + 1.5, y0 + 2 * cs + 1.5, cs - 3, cs - 3, 'none', PIX, 2)
    s.rect(x0 + 3 * cs + 1.5, y0 + 1 * cs + 1.5, cs - 3, cs - 3, 'none', PIX, 2)
    s.text(165, 226, 'grey = base case 1;  10 = 4 (above) + 6 (left)', 12, INK)
    s.save('pat-dp-unique-paths-answer.svg', OUT)


def main():
    prefix_revenue()
    prefix_sentinel()
    prefix_2d()
    two_pointers_steps()
    sliding_fixed()
    sliding_variable()
    fast_slow()
    reversal_steps()
    reversal_sketch_answer()
    mono_stack_steps()
    topk_heap_steps()
    topk_sketch_answer()
    intervals_merge()
    intervals_sketch_answer()
    rotated_search()
    traversal_orders()
    traversal_sketch_answer()
    dfs_topo()
    dfs_sketch_answer()
    bfs_levels()
    bfs_rotting()
    bfs_sketch_answer()
    matrix_flood()
    matrix_islands()
    permutation_tree()
    backtrack_sketch_answer()
    fib_call_tree()
    coin_change_table()
    lcs_table()
    unique_paths_answer()


if __name__ == '__main__':
    main()
