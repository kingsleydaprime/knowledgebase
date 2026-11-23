"""Draw the DSA data-structure lesson diagrams as small SVG files.

    python3 scripts/diagrams/dsa_structures.py      # run from the vault root

Covers dsa/01-loops-and-what-they-cost.md and dsa/02-data-structures (not graphs).
Every picture is computed by running the operation the lesson teaches (inserting
into a BST, pushing onto a heap, probing a hash table, union with path
compression...) and the lesson's numbers are asserted before drawing, so a
picture can never disagree with the text. Trees are drawn with Graphviz (`dot`).
Output: dsa/images/ds-*.svg.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgkit  # noqa: E402
from svgkit import INK, GRID, PIX, PIX2, TRUE, ACCENT, FONT  # noqa: E402


def _esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Svg(svgkit.Svg):
    """svgkit.Svg with the <title> escaped, so titles may say 1 < 3."""

    def __init__(self, w, h, title):
        super().__init__(w, h, _esc(title))


def save_dot(src, name, title, out):
    svgkit.save_dot(src, name, _esc(title), out)

OUT = os.path.join('dsa', 'images')
ORANGE = '#f59e0b'
SOFT = '#dbeafe'      # normal cell / node fill
NEWF = '#fef3c7'      # fill for the thing that changed in this step
DONE = '#d1fae5'      # finished / result fill
GREY = '#9ca3af'
FADE = '#f3f4f6'


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
          f'stroke-width="{width}" marker-end="{mk[color]}"{d}/>')


def curve_arrow(s, mk, x1, y1, x2, y2, bend, color=INK, width=1.6):
    """Quadratic arrow from (x1,y1) to (x2,y2); bend > 0 bulges upward."""
    cx, cy = (x1 + x2) / 2, min(y1, y2) - bend
    s.add(f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" stroke="{color}" '
          f'stroke-width="{width}" fill="none" marker-end="{mk[color]}"/>')


def cells(s, x, y, values, w=44, h=36, fills=None, strokes=None, idx=None, size=14, idx_label=True):
    """A row of boxes. fills/strokes: dict index -> colour. idx: list of index labels under the cells."""
    fills, strokes = fills or {}, strokes or {}
    for i, v in enumerate(values):
        st = strokes.get(i, INK)
        s.rect(x + i * w, y, w, h, fills.get(i, SOFT), st, 3 if st != INK else 1.2)
        if v is not None and v != '':
            s.text(x + i * w + w / 2, y + h / 2 + 5, v, size, INK if v != '—' else GREY)
    if idx_label:
        labels = idx if idx is not None else list(range(len(values)))
        for i, lab in enumerate(labels):
            s.text(x + i * w + w / 2, y + h + 15, lab, 11, '#6b7280')


def bin_tree_dot(root, kids, title_hint='', hl=(), fade=(), done=(), order=None, labels=None, shape='circle',
                 extra='', edge_labels=None, dashed_edges=(), hl_edges=()):
    """Binary tree in dot. kids: node -> (left, right) with None for missing. Missing children get an invisible
    placeholder so a lone right child is drawn to the right. order: node -> visit number (orange tag)."""
    labels = labels or {}
    lines = [f'digraph {{ bgcolor="white"; pad=0.2; nodesep=0.3; ranksep=0.35; ordering=out; {extra}',
             f'node [fontname="{FONT}", fontsize=14, shape={shape}, style=filled, fillcolor="{SOFT}", '
             f'color="{INK}", penwidth=1.3, width=0.5, fixedsize={"true" if shape == "circle" else "false"}];',
             f'edge [color="{INK}", arrowhead=none, penwidth=1.3];']
    ph = iter(range(10000))

    def nid(n):
        return 'n' + ''.join(c if c.isalnum() else '_' for c in str(n))

    def walk(n):
        lab = labels.get(n, str(n))
        attrs = [f'label="{lab}"']
        if n in hl:
            attrs += [f'color="{ORANGE}"', 'penwidth=3.2', f'fillcolor="{NEWF}"']
        elif n in done:
            attrs += [f'fillcolor="{DONE}"']
        elif n in fade:
            attrs += [f'fillcolor="{FADE}"', f'color="{GREY}"', f'fontcolor="{GREY}"', 'style="filled,dashed"']
        if order and n in order:
            attrs += [f'xlabel=<<font color="{ORANGE}" point-size="13"><b>{order[n]}</b></font>>']
        lines.append(f'{nid(n)} [{", ".join(attrs)}];')
        l, r = kids.get(n, (None, None))
        if l is None and r is None:
            return
        for c in (l, r):
            if c is None:
                p = f'p{next(ph)}'
                lines.append(f'{p} [label="", style=invis];')
                lines.append(f'{nid(n)} -> {p} [style=invis];')
            else:
                walk(c)
                ea = []
                if (n, c) in dashed_edges:
                    ea.append(f'style=dashed, color="{GREY}"')
                if (n, c) in hl_edges:
                    ea.append(f'color="{ORANGE}", penwidth=3')
                if edge_labels and (n, c) in edge_labels:
                    ea.append(f'label=" {edge_labels[(n, c)]}", fontname="{FONT}", fontsize=11')
                lines.append(f'{nid(n)} -> {nid(c)}' + (f' [{", ".join(ea)}]' if ea else '') + ';')

    if order:
        lines.insert(1, 'forcelabels=true;')
    if root is not None:
        walk(root)
    lines.append('}')
    return '\n'.join(lines)


def bin_layout(kids, root, dx=44, dy=58):
    """In-order x position, depth y: a left child is always drawn left of its parent and a right child right."""
    order = inorder(kids, root)
    xi = {n: i for i, n in enumerate(order)}
    pos = {}

    def walk(n, d):
        if n is None:
            return
        pos[n] = (xi[n] * dx, d * dy)
        l, r = kids.get(n, (None, None))
        walk(l, d + 1)
        walk(r, d + 1)

    walk(root, 0)
    return pos


def draw_bin_tree(s, kids, root, ox, oy, hl=(), fade=(), done=(), order=None, hl_edges=(), dashed_edges=(),
                  dx=44, dy=58, r=16, size=13, labels=None):
    """Binary tree drawn with plain SVG. order: node -> visit number, shown as an orange badge."""
    pos = bin_layout(kids, root, dx, dy)
    labels = labels or {}
    for n, (l, rr) in kids.items():
        if n not in pos:
            continue
        for c in (l, rr):
            if c is None or c not in pos:
                continue
            (x1, y1), (x2, y2) = pos[n], pos[c]
            if (n, c) in hl_edges:
                s.line(ox + x1, oy + y1, ox + x2, oy + y2, ORANGE, 3.2)
            elif (n, c) in dashed_edges:
                s.line(ox + x1, oy + y1, ox + x2, oy + y2, GREY, 1.4, '4,3')
            else:
                s.line(ox + x1, oy + y1, ox + x2, oy + y2, INK, 1.4)
    for n, (x, y) in pos.items():
        if n in hl:
            f, st, w, tc = NEWF, ORANGE, 3, INK
        elif n in done:
            f, st, w, tc = DONE, INK, 1.3, INK
        elif n in fade:
            f, st, w, tc = FADE, GREY, 1.3, GREY
        else:
            f, st, w, tc = SOFT, INK, 1.3, INK
        dash = ' stroke-dasharray="4,3"' if n in fade else ''
        s.add(f'<circle cx="{ox + x:.1f}" cy="{oy + y:.1f}" r="{r}" fill="{f}" stroke="{st}" stroke-width="{w}"{dash}/>')
        s.text(ox + x, oy + y + 5, labels.get(n, n), size, tc, 'middle', 'bold')
        if order and n in order:
            bx, by = ox + x + r - 2, oy + y - r + 1
            s.add(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="9" fill="{ORANGE}"/>')
            s.text(bx, by + 4, order[n], 11, '#ffffff', 'middle', 'bold')
    return pos


def tree_extent(kids, root, dx=44, dy=58):
    pos = bin_layout(kids, root, dx, dy)
    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    return max(xs) - min(xs), max(ys)


def bin_tree_svg(kids, root, name, title, out=OUT, pad=30, top=None, extra_h=0, min_w=0, **kw):
    """Save a standalone picture of one binary tree. Returns the Svg so callers can add notes before saving."""
    dx, dy = kw.get('dx', 44), kw.get('dy', 58)
    w, h = tree_extent(kids, root, dx, dy)
    top = top if top is not None else pad
    W = max(w + 2 * pad, min_w)
    s = Svg(W, h + top + pad + extra_h, title)
    draw_bin_tree(s, kids, root, (W - w) / 2, top, **kw)
    s.save(name, out)
    return s


# ---------- BST operations, exactly as the lessons teach them ----------

def bst_insert(kids, root, key):
    if root is None:
        kids[key] = (None, None)
        return key
    cur = root
    while True:
        l, r = kids[cur]
        if key < cur:
            if l is None:
                kids[cur] = (key, r)
                break
            cur = l
        else:
            if r is None:
                kids[cur] = (l, key)
                break
            cur = r
    kids[key] = (None, None)
    return root


def inorder(kids, n):
    if n is None:
        return []
    l, r = kids.get(n, (None, None))
    return inorder(kids, l) + [n] + inorder(kids, r)


def preorder(kids, n):
    if n is None:
        return []
    l, r = kids.get(n, (None, None))
    return [n] + preorder(kids, l) + preorder(kids, r)


def postorder(kids, n):
    if n is None:
        return []
    l, r = kids.get(n, (None, None))
    return postorder(kids, l) + postorder(kids, r) + [n]


def levelorder(kids, n):
    out, q = [], [n]
    while q:
        x = q.pop(0)
        if x is None:
            continue
        out.append(x)
        q += list(kids.get(x, (None, None)))
    return out


def height(kids, n):
    if n is None:
        return -1
    l, r = kids.get(n, (None, None))
    return 1 + max(height(kids, l), height(kids, r))


# ======================================================================
# dsa/01-loops-and-what-they-cost.md
# ======================================================================

def loops_grids():
    n = 6
    square = [(i, j) for i in range(n) for j in range(n)]
    tri = [(i, j) for i in range(n) for j in range(i, n)]
    assert len(square) == 36 and len(tri) == n * (n + 1) // 2 == 21
    c = 26
    s = Svg(470, 250, 'Two 6 by 6 grids of loop steps: the full nested loop fills all 36 cells, the triangular loop '
                      'with j starting at i fills 21 cells on and above the diagonal')
    for k, (pts, name, x0) in enumerate(((square, 'nested: j in range(n)', 40), (tri, 'triangular: j in range(i, n)', 270))):
        y0 = 40
        s.text(x0 + n * c / 2, 22, name, 13, INK, 'middle', 'bold')
        for i in range(n):
            s.text(x0 - 8, y0 + i * c + c / 2 + 4, f'i={i}', 10, '#6b7280', 'end')
            for j in range(n):
                on = (i, j) in pts
                s.rect(x0 + j * c, y0 + i * c, c, c, PIX if on else '#f3f4f6', '#ffffff', 1.5)
        for j in range(n):
            s.text(x0 + j * c + c / 2, y0 + n * c + 14, f'j={j}', 9, '#6b7280')
        s.text(x0 + n * c / 2, y0 + n * c + 36, f'{len(pts)} steps' + (' = 6 × 6' if k == 0 else ' = 6+5+4+3+2+1'),
               13, PIX, 'middle', 'bold')
    s.save('ds-loops-nested-vs-triangular.svg', OUT)


def loops_halving():
    i, vals = 1000, [1000]
    while i > 1:
        i //= 2
        vals.append(i)
    assert vals == [1000, 500, 250, 125, 62, 31, 15, 7, 3, 1]
    passes = len(vals) - 1
    w, top = 520, 30
    s = Svg(w, 40 + 26 * len(vals) + 30, 'Halving loop from 1000: 1000, 500, 250, 125, 62, 31, 15, 7, 3, 1, which '
                                          'is 9 passes, close to log base 2 of 1000, about 10')
    scale = 380 / 1000
    for k, v in enumerate(vals):
        y = top + k * 26
        s.text(60, y + 15, 'start' if k == 0 else f'pass {k}', 11, '#6b7280', 'end')
        s.rect(70, y + 2, max(v * scale, 2), 18, PIX if k else INK)
        s.text(78 + max(v * scale, 2), y + 16, v, 12, INK, 'start', 'bold')
    s.text(w / 2, top + 26 * len(vals) + 18, f'{passes} passes to reach 1 (log₂ 1000 ≈ 10)', 13, ACCENT, 'middle', 'bold')
    s.save('ds-loops-halving.svg', OUT)


# ======================================================================
# dsa/02-data-structures/01-arrays.md
# ======================================================================

def address_of(base, i, size):
    return base + i * size


def arrays_mailboxes():
    base, size = 100, 4
    addrs = [address_of(base, i, size) for i in range(5)]
    assert addrs == [100, 104, 108, 112, 116]
    s = Svg(330, 120, 'Five mailboxes side by side, box 0 to box 4, at addresses 100, 104, 108, 112 and 116')
    s.text(165, 20, 'one unbroken row: each box is 4 bytes', 12, '#6b7280')
    cells(s, 30, 34, ['letter'] * 5, w=54, h=40, size=11, idx=[f'box {i}' for i in range(5)])
    for i, a in enumerate(addrs):
        s.text(30 + i * 54 + 27, 106, a, 12, PIX, 'middle', 'bold')
    s.save('ds-array-mailboxes.svg', OUT)


def arrays_address():
    base, size, vals, i = 1000, 4, [10, 22, 7, 41, 3], 3
    assert address_of(base, i, size) == 1012
    s = Svg(360, 175, 'Array of 4-byte integers 10, 22, 7, 41, 3 starting at address 1000; arr[3] = 41 is found '
                      'directly at 1000 + 3 × 4 = 1012')
    s.text(20, 24, 'index', 11, '#6b7280', 'start')
    for k in range(5):
        s.text(70 + k * 50 + 25, 24, k, 12, '#6b7280')
    cells(s, 70, 32, vals, w=50, h=38, fills={i: NEWF}, strokes={i: ORANGE}, idx_label=False)
    s.text(20, 56, 'value', 11, '#6b7280', 'start')
    s.text(20, 92, 'address', 11, '#6b7280', 'start')
    for k in range(5):
        a = address_of(base, k, size)
        s.text(70 + k * 50 + 25, 92, a, 12, ORANGE if k == i else INK, 'middle', 'bold' if k == i else 'normal')
    s.text(180, 130, 'arr[3]  →  1000 + 3 × 4 = 1012', 15, ORANGE, 'middle', 'bold')
    s.text(180, 156, 'one multiply, one add: no walking past 0, 1, 2', 12, '#6b7280')
    s.save('ds-array-address.svg', OUT)


def flatten_picture(row_major):
    grid = [[1, 2, 3], [4, 5, 6]]
    R, C = 2, 3
    flat = [None] * 6
    for r in range(R):
        for c in range(C):
            flat[r * C + c if row_major else c * R + r] = grid[r][c]
    assert flat == ([1, 2, 3, 4, 5, 6] if row_major else [1, 4, 2, 5, 3, 6])
    group_cols = ['#dbeafe', '#fde68a', '#d1fae5']
    kind = 'row' if row_major else 'col'
    s = Svg(470, 160, ('Row-major' if row_major else 'Column-major') + ' layout: the grid 1 2 3 over 4 5 6 is stored as '
            + ', '.join(map(str, flat)) + (', row 0 then row 1' if row_major else ', column 0, then column 1, then column 2'))
    w = 40
    s.text(20 + 1.5 * w, 22, 'grid', 12, '#6b7280')
    for r in range(R):
        for c in range(C):
            g = r if row_major else c
            s.rect(20 + c * w, 32 + r * w, w, w, group_cols[g], INK, 1.2)
            s.text(20 + c * w + w / 2, 32 + r * w + w / 2 + 5, grid[r][c], 15)
    mk = arrow_defs(s)
    arrow(s, mk, 150, 72, 190, 72)
    s.text(320, 22, 'memory (one long row)', 12, '#6b7280')
    for k, v in enumerate(flat):
        r, c = (k // C, k % C) if row_major else (k % R, k // R)
        g = r if row_major else c
        s.rect(200 + k * w, 52, w, w, group_cols[g], INK, 1.2)
        s.text(200 + k * w + w / 2, 52 + w / 2 + 5, v, 15)
        s.text(200 + k * w + w / 2, 52 + w + 14, k, 10, '#6b7280')
    span = C if row_major else R
    for g in range(len(flat) // span):
        x0 = 200 + g * span * w
        s.path(f'M{x0 + 3},{116} L{x0 + 3},{122} L{x0 + span * w - 3},{122} L{x0 + span * w - 3},{116}', INK, 1.2)
        s.text(x0 + span * w / 2, 140, f'{"Row" if row_major else "Col"} {g}', 12, INK, 'middle', 'bold')
    s.save(f'ds-array-{kind}-major.svg', OUT)


def arrays_insert_shift():
    arr = [10, 22, 7, 41, 3, None]
    moves = []
    for k in range(4, 0, -1):          # shift from the back so nothing is overwritten
        arr[k + 1] = arr[k]
        moves.append(k)
    arr[1] = 99
    assert arr == [10, 99, 22, 7, 41, 3] and len(moves) == 4
    s = Svg(380, 170, 'Inserting 99 at index 1 of 10, 22, 7, 41, 3: the four elements at indexes 1 to 4 each move one '
                      'place right, starting from the back, then 99 goes into the gap')
    mk = arrow_defs(s)
    s.text(20, 20, 'before', 12, '#6b7280', 'start')
    cells(s, 60, 28, [10, 22, 7, 41, 3, ''], w=48, h=34, fills={5: FADE}, idx_label=False)
    for k in moves:
        curve_arrow(s, mk, 60 + k * 48 + 30, 66, 60 + (k + 1) * 48 + 18, 66, -18, ORANGE)
    s.text(20, 120, 'after', 12, '#6b7280', 'start')
    cells(s, 60, 128, arr, w=48, h=34, fills={1: NEWF}, strokes={1: ORANGE}, idx_label=False)
    s.text(60 + 3 * 48, 108, '4 moves (indexes 1 to 4), then write 99', 12, ORANGE, 'middle', 'bold')
    s.save('ds-array-insert-shift.svg', OUT)


def arrays():
    arrays_mailboxes()
    arrays_address()
    flatten_picture(True)
    flatten_picture(False)
    arrays_insert_shift()


# ======================================================================
# dsa/02-data-structures/02-dynamic-arrays.md
# ======================================================================

class GrowableArray:
    """The lesson's dynamic array: doubles when full and counts copies."""

    def __init__(self, capacity=1):
        self.data, self.size, self.capacity, self.copies = [None] * capacity, 0, capacity, 0
        self.log = []          # (append number, copies made by that append)

    def append(self, v, snap=None):
        made = 0
        if self.size == self.capacity:
            bigger = [None] * (self.capacity * 2)
            if snap is not None:
                snap.append(('alloc', list(bigger)))
            for i in range(self.size):
                bigger[i] = self.data[i]
            made = self.size
            if snap is not None:
                snap.append(('copy', list(bigger)))
            self.data, self.capacity = bigger, self.capacity * 2
        self.copies += made
        self.data[self.size] = v
        self.size += 1
        self.log.append(made)
        if snap is not None:
            snap.append(('append', list(self.data)))


def dyn_headroom():
    a = GrowableArray(4)
    for v in (10, 22, 7):
        a.append(v)
    assert (a.size, a.capacity) == (3, 4)
    s = Svg(340, 100, 'Dynamic array with length 3 and capacity 4: 10, 22, 7 and one empty slot of headroom')
    cells(s, 30, 30, [x if x is not None else '' for x in a.data], w=50, h=38, fills={3: FADE}, idx_label=True)
    s.text(30, 20, 'length = 3, capacity = 4', 13, INK, 'start', 'bold')
    s.text(240, 49, '← headroom', 12, ACCENT, 'start', 'bold')
    s.save('ds-dynarray-headroom.svg', OUT)


def dyn_resize_steps():
    a = GrowableArray(4)
    for v in (10, 22, 7, 41):
        a.append(v)
    assert (a.size, a.capacity) == (4, 4)
    old = list(a.data)
    snap = []
    a.append(99, snap)
    kinds = [k for k, _ in snap]
    assert kinds == ['alloc', 'copy', 'append'] and (a.size, a.capacity) == (5, 8) and a.log[-1] == 4
    rows = [('full: length 4, capacity 4', old, {}, None),
            ('step 1: allocate 8 empty slots', snap[0][1], {}, None),
            ('step 2: copy the 4 old elements (4 copies)', snap[1][1], {i: PIX2 for i in range(4)}, None),
            ('step 3: free the old block', None, {}, None),
            ('step 4: write 99 into slot 4', snap[2][1], {4: NEWF}, 4)]
    w, h, gap = 38, 30, 62
    s = Svg(380, 30 + gap * 4 + 30, 'Resizing a full dynamic array of 10, 22, 7, 41 on append(99): allocate 8 slots, '
                                     'copy the 4 old elements, free the old block, then write 99; length 5, capacity 8')
    y = 14
    for label, data, fills, hl in rows:
        s.text(20, y + 12, label, 12, INK, 'start', 'bold')
        if data is None:
            y += 26
            continue
        f = {i: FADE for i, v in enumerate(data) if v is None}
        f.update(fills)
        cells(s, 20, y + 20, ['' if v is None else v for v in data], w=w, h=h, fills=f,
              strokes={hl: ORANGE} if hl is not None else None, idx_label=False, size=13)
        y += gap
    s.text(360, y + 4, 'length 5, capacity 8: 3 slots of headroom', 12, ACCENT, 'end', 'bold')
    s.h = y + 18
    s.save('ds-dynarray-resize-steps.svg', OUT)


def dyn_copies_chart():
    a = GrowableArray(1)
    for i in range(16):
        a.append(i)
    per = a.log
    assert sum(per) == 15 and [k + 1 for k, c in enumerate(per) if c] == [2, 3, 5, 9]
    assert [c for c in per if c] == [1, 2, 4, 8]
    s = Svg(480, 235, 'Copies made by each of 16 appends starting from capacity 1: append 2 copies 1, append 3 copies 2, '
                      'append 5 copies 4, append 9 copies 8, every other append copies nothing; 15 copies in total')
    x0, y0, bw, sc = 50, 190, 25, 15
    s.line(x0, y0, x0 + 16 * bw + 6, y0, INK, 1.2)
    for k, c in enumerate(per):
        x = x0 + k * bw + 4
        if c:
            s.rect(x, y0 - c * sc, bw - 8, c * sc, ORANGE)
            s.text(x + (bw - 8) / 2, y0 - c * sc - 5, c, 12, INK, 'middle', 'bold')
        else:
            s.rect(x, y0 - 3, bw - 8, 3, GREY)
        s.text(x + (bw - 8) / 2, y0 + 15, k + 1, 10, '#6b7280')
    s.text(x0 + 8 * bw, y0 + 33, 'append number', 11, '#6b7280')
    s.text(x0 - 8, y0 - 8 * sc, 'copies', 11, '#6b7280', 'end')
    s.text(x0 + 10, 28, 'total: 1 + 2 + 4 + 8 = 15 copies', 13, ACCENT, 'start', 'bold')
    s.text(x0 + 10, 46, 'the other 12 appends copy nothing', 12, '#6b7280', 'start')
    s.save('ds-dynarray-copies-per-append.svg', OUT)


def dynamic_arrays():
    dyn_headroom()
    dyn_resize_steps()
    dyn_copies_chart()


# ======================================================================
# dsa/02-data-structures/03-hash-maps.md
# ======================================================================

def chain_insert(buckets, key, bucket):
    buckets[bucket].append(key)


def probe_insert(slots, key, home):
    """Linear probing: try home, home+1, ... wrapping round. Returns (slot, list of slots tried)."""
    n, tried = len(slots), []
    for k in range(n):
        i = (home + k) % n
        tried.append(i)
        if slots[i] is None:
            slots[i] = key
            return i, tried
    raise RuntimeError('table full')


def draw_chains(s, x, y, buckets, title=None, hl=None, rowh=34, nodew=92, mk=None):
    """Bucket array drawn as a column; each bucket's chain runs to the right. hl = (bucket, position)."""
    if title:
        s.text(x, y - 10, title, 13, INK, 'start', 'bold')
    for b, chain in enumerate(buckets):
        yy = y + b * rowh
        s.text(x + 14, yy + rowh / 2 + 4, b, 11, '#6b7280', 'end')
        s.rect(x + 20, yy, 34, rowh, SOFT if chain else FADE, INK, 1.2)
        if not chain:
            s.text(x + 37, yy + rowh / 2 + 4, '—', 12, GREY)
            continue
        s.circle(x + 37, yy + rowh / 2, 3, INK)
        px = x + 37
        for k, lab in enumerate(chain):
            nx = x + 70 + k * (nodew + 22)
            arrow(s, mk, px + (4 if k == 0 else 0), yy + rowh / 2, nx - 2, yy + rowh / 2)
            on = hl == (b, k)
            s.rect(nx, yy + 4, nodew, rowh - 8, NEWF if on else DONE, ORANGE if on else INK, 3 if on else 1.1)
            s.text(nx + nodew / 2, yy + rowh / 2 + 4, lab, 12)
            px = nx + nodew


def hash_coat_check():
    src = f"""digraph {{ bgcolor="white"; pad=0.25; rankdir=LR; nodesep=0.3; ranksep=0.35;
node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
edge [fontname="{FONT}", fontsize=11, color="{INK}"];
k [label="key\\n“Alice”", fillcolor="#fef3c7"];
h [label="attendant\\n(hash function)", fillcolor="#dbeafe"];
b [label="slot 4 (bucket)\\nAlice's coat", fillcolor="#d1fae5"];
k -> h; h -> b [label=" 4"];
}}"""
    save_dot(src, 'ds-hash-coat-check.svg', 'Coat check as a hash map: the key Alice goes to the attendant, who works out '
             'slot 4, where Alice\'s coat is kept', OUT)


def hash_bucket_array():
    h, cap = 2_166_136_261, 8      # the lesson's example hash value
    idx = h % cap
    assert idx == 5
    s = Svg(470, 120, 'The key apple hashes to 2,166,136,261; 2,166,136,261 mod 8 is 5, so the pair apple, 100 is '
                      'stored in slot 5 of an 8-slot bucket array')
    s.text(235, 20, 'hash("apple") = 2,166,136,261   →   2,166,136,261 % 8 = 5', 13, INK, 'middle', 'bold')
    vals = ['' for _ in range(cap)]
    vals[idx] = 'apple: 100'
    w = [44] * cap
    w[idx] = 96
    x = 20
    for i in range(cap):
        on = i == idx
        s.rect(x, 40, w[i], 38, NEWF if on else FADE, ORANGE if on else INK, 3 if on else 1.2)
        s.text(x + w[i] / 2, 64, vals[i] if on else '—', 13 if on else 12, INK if on else GREY)
        s.text(x + w[i] / 2, 94, f'slot {i}', 10, '#6b7280')
        x += w[i]
    s.text(235, 114, 'one hash, one modulo, one jump: no searching', 12, ACCENT, 'middle', 'bold')
    s.save('ds-hash-bucket-array.svg', OUT)


def hash_chaining_example():
    buckets = [[] for _ in range(8)]
    for key, val, b in (('apple', 100, 5), ('grape', 250, 5)):   # both land in bucket 5, as in the lesson
        chain_insert(buckets, f'{key}: {val}', b)
    assert buckets[5] == ['apple: 100', 'grape: 250'] and sum(map(len, buckets)) == 2
    s = Svg(290, 8 * 26 + 30, 'Separate chaining: apple, 100 and grape, 250 both hash to bucket 5, so bucket 5 holds '
                              'a short list, apple then grape; the other buckets are empty')
    mk = arrow_defs(s)
    draw_chains(s, 10, 14, buckets, hl=(5, 1), rowh=26, nodew=90, mk=mk)
    s.save('ds-hash-chaining.svg', OUT)


def hash_probing_example():
    slots = [None] * 8
    a, _ = probe_insert(slots, 'apple: 100', 5)
    g, tried = probe_insert(slots, 'grape: 250', 5)
    assert (a, g, tried) == (5, 6, [5, 6])
    s = Svg(560, 130, 'Open addressing: apple, 100 sits in slot 5; grape, 250 also hashes to 5, finds it full, and '
                      'is probed to the next slot, 6')
    mk = arrow_defs(s)
    w = [46] * 8
    w[5] = w[6] = 92
    xs = [20]
    for i in range(8):
        xs.append(xs[-1] + w[i])
    for i in range(8):
        on = i == 6
        s.rect(xs[i], 50, w[i], 36, NEWF if on else (SOFT if slots[i] else FADE), ORANGE if on else INK, 3 if on else 1.2)
        s.text(xs[i] + w[i] / 2, 73, slots[i] or '—', 12, INK if slots[i] else GREY)
        s.text(xs[i] + w[i] / 2, 102, f'slot {i}', 10, '#6b7280')
    s.text(xs[5] + w[5] / 2, 20, 'grape hashes to 5: taken', 12, TRUE, 'middle')
    curve_arrow(s, mk, xs[5] + w[5] / 2 + 20, 48, xs[6] + w[6] / 2, 48, 22, ORANGE)
    s.text(xs[6] + w[6] / 2 + 30, 30, 'probe 6: free', 12, ORANGE, 'start', 'bold')
    s.save('ds-hash-open-addressing.svg', OUT)


def probe_steps_picture(keys, n, name, title, show_note=True):
    slots, rows = [None] * n, []
    for k in keys:
        slot, tried = probe_insert(slots, k, k % n)
        rows.append((k, slot, tried, list(slots)))
    w, rh = 40, 52
    s = Svg(150 + n * w, 30 + rh * len(rows), title)
    s.text(150 + n * w / 2 - 5, 16, ' '.join(f'{i}' for i in range(0)), 10)
    for i in range(n):
        s.text(140 + i * w + w / 2, 18, f'slot {i}', 10, '#6b7280')
    for r, (k, slot, tried, state) in enumerate(rows):
        y = 26 + r * rh
        s.text(12, y + 17, f'insert {k}', 12, INK, 'start', 'bold')
        s.text(12, y + 33, f'{k} % {n} = {k % n}', 11, '#6b7280', 'start')
        for i in range(n):
            on = i == slot
            bad = i in tried and not on
            s.rect(140 + i * w, y, w, 34, NEWF if on else (SOFT if state[i] is not None else FADE),
                   ORANGE if on else (TRUE if bad else INK), 3 if on or bad else 1.1)
            s.text(140 + i * w + w / 2, y + 22, '—' if state[i] is None else state[i], 13,
                   GREY if state[i] is None else INK, 'middle', 'bold' if on else 'normal')
        if len(tried) > 1:
            s.text(140 + n * w + 6, y + 22, f'{len(tried)} tries', 11, TRUE, 'start')
    s.w += 50
    s.save(name, OUT)
    return rows


def hash_probe_steps():
    rows = probe_steps_picture([18, 26, 7, 34, 15], 8, 'ds-hash-probing-steps.svg',
                               'Linear probing in an 8-slot table with hash k mod 8: 18 goes to slot 2; 26 hashes to 2, '
                               'finds it taken and lands in 3; 7 goes to 7; 34 hashes to 2 and probes 2, 3, then lands in '
                               '4; 15 hashes to 7, finds it taken and wraps round to slot 0')
    assert [(k, sl) for k, sl, _, _ in rows] == [(18, 2), (26, 3), (7, 7), (34, 4), (15, 0)]
    assert rows[3][2] == [2, 3, 4] and rows[4][2] == [7, 0]


def hash_rehash():
    def build(keys, cap):
        b = [[] for _ in range(cap)]
        for k in keys:
            chain_insert(b, str(k), k % cap)
        return b
    keys = [3, 7, 11]
    small, big = build(keys, 4), build(keys, 8)
    assert len(keys) / 4 == 0.75 > 0.7
    assert small[3] == ['3', '7', '11'] and big[3] == ['3', '11'] and big[7] == ['7']
    s = Svg(530, 295, 'Rehashing: keys 3, 7 and 11 all sit in bucket 3 of a 4-bucket table, load factor 0.75. After '
                      'doubling to 8 buckets and recomputing k mod 8, 3 and 11 share bucket 3 and 7 moves to bucket 7')
    mk = arrow_defs(s)
    draw_chains(s, 10, 40, small, title='4 buckets, k % 4 (load 0.75 > 0.7)', rowh=30, nodew=40, mk=mk)
    draw_chains(s, 290, 40, big, title='8 buckets, k % 8 (load 0.38)', rowh=30, nodew=40, mk=mk, hl=(7, 0))
    s.text(150, 200, 'every key is rehashed,', 12, '#6b7280')
    s.text(150, 216, 'because the bucket', 12, '#6b7280')
    s.text(150, 232, 'depends on the capacity', 12, '#6b7280')
    s.save('ds-hash-rehash.svg', OUT)


def hash_sketch_answer():
    keys, cap = [14, 21, 8, 26, 33, 4], 6
    b = [[] for _ in range(cap)]
    for k in keys:
        chain_insert(b, str(k), k % cap)
    assert b == [[], [], ['14', '8', '26'], ['21', '33'], ['4'], []]
    s = Svg(260, cap * 32 + 24, 'Answer: a 6-bucket chained table with k mod 6. Bucket 2 holds 14, 8, 26; bucket 3 '
                                'holds 21, 33; bucket 4 holds 4; buckets 0, 1 and 5 are empty')
    mk = arrow_defs(s)
    draw_chains(s, 10, 12, b, rowh=32, nodew=44, mk=mk)
    s.save('ds-hash-sketch-answer.svg', OUT)


def hash_maps():
    hash_coat_check()
    hash_bucket_array()
    hash_chaining_example()
    hash_probing_example()
    hash_probe_steps()
    hash_rehash()
    hash_sketch_answer()


# ======================================================================
# dsa/02-data-structures/04-linked-lists.md
# ======================================================================

class LNode:
    def __init__(self, value, nxt=None):
        self.value, self.next, self.prev = value, nxt, None


NODE_W, VAL_W, NODE_H, GAP = 66, 42, 34, 40


def draw_nodes(s, mk, x0, y, nodes, tags=None, hl=(), fade=(), hl_ptr=(), doubly=False):
    """Draw LNode objects left to right at fixed slots, with each `next` arrow drawn from the real pointer.
    A None pointer is drawn as a slash in the pointer cell. tags: node -> label above it."""
    tags = tags or {}
    pos = {id(n): x0 + i * (NODE_W + GAP) for i, n in enumerate(nodes)}
    for n in nodes:
        x = pos[id(n)]
        on, gone = n in hl, n in fade
        stroke = ORANGE if on else (GREY if gone else INK)
        fill = NEWF if on else (FADE if gone else SOFT)
        if doubly:
            s.rect(x - 18, y, 18, NODE_H, fill, stroke, 3 if on else 1.2)
            if n.prev is None:
                s.line(x - 18, y + NODE_H, x, y, stroke, 1.2)
        s.rect(x, y, VAL_W, NODE_H, fill, stroke, 3 if on else 1.2)
        s.rect(x + VAL_W, y, NODE_W - VAL_W, NODE_H, fill, stroke, 3 if on else 1.2)
        s.text(x + VAL_W / 2, y + NODE_H / 2 + 5, n.value, 14, GREY if gone else INK)
        if n in tags:
            s.text(x + VAL_W / 2, y - 8, tags[n], 12, ORANGE if on else PIX, 'middle', 'bold')
        px, py = x + VAL_W + (NODE_W - VAL_W) / 2, y + NODE_H / 2
        if n.next is None:
            s.line(x + VAL_W, y + NODE_H, x + NODE_W, y, stroke, 1.2)
            continue
        s.circle(px, py, 3, stroke)
        col = ORANGE if n in hl_ptr else (GREY if gone else INK)
        tx = pos[id(n.next)]
        if tx > x and tx - x == NODE_W + GAP:
            ay = py - 7 if doubly else py
            arrow(s, mk, px + 3, ay, tx - (20 if doubly else 2), ay, col, 2.4 if n in hl_ptr else 1.6)
        elif tx > x:
            s.add(f'<path d="M{px:.1f},{y + NODE_H:.1f} C{px + 20:.1f},{y + NODE_H + 40:.1f} '
                  f'{tx + VAL_W / 2 - 20:.1f},{y + NODE_H + 40:.1f} {tx + VAL_W / 2:.1f},{y + NODE_H + 2:.1f}" '
                  f'stroke="{col}" stroke-width="{2.4 if n in hl_ptr else 1.6}" fill="none" marker-end="{mk[col]}"/>')
        else:
            s.add(f'<path d="M{px:.1f},{y + NODE_H:.1f} C{px:.1f},{y + NODE_H + 32:.1f} '
                  f'{tx + 14:.1f},{y + NODE_H + 32:.1f} {tx + 14:.1f},{y + NODE_H + 2:.1f}" '
                  f'stroke="{col}" stroke-width="{2.4 if n in hl_ptr else 1.6}" fill="none" marker-end="{mk[col]}"/>')
        if doubly and n.next is not None and n.next.prev is n:
            nx = pos[id(n.next)]
            s.circle(nx - 9, py + 8, 3, col)
            arrow(s, mk, nx - 12, py + 8, x + NODE_W + 2, py + 8, col)
    return pos


def chain(values):
    nodes = [LNode(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next, b.prev = b, a
    return nodes


def ll_treasure_hunt():
    cards = [('Clue 1', 'at Base Camp', 'next: Oak Tree'), ('Clue 2', 'under Oak Tree', 'next: Cave'),
             ('Clue 3', 'inside Cave', 'Treasure!')]
    s = Svg(520, 110, 'Treasure hunt as a linked list: Clue 1 at Base Camp points to the Oak Tree, Clue 2 under the Oak '
                      'Tree points to the Cave, and Clue 3 inside the Cave holds the treasure')
    mk = arrow_defs(s)
    for i, (a, b, c) in enumerate(cards):
        x = 20 + i * 170
        s.rect(x, 20, 140, 72, DONE if i == 2 else SOFT, INK, 1.2)
        s.text(x + 70, 42, a, 14, INK, 'middle', 'bold')
        s.text(x + 70, 62, b, 12)
        s.text(x + 70, 81, c, 12, ORANGE if i == 2 else PIX, 'middle', 'bold')
        if i < 2:
            arrow(s, mk, x + 142, 56, x + 168, 56)
    s.save('ds-ll-treasure-hunt.svg', OUT)


def ll_variants():
    s = Svg(560, 400, 'Four kinds of linked list holding 10, 20, 30: singly linked (next pointers only, last is None), '
                      'doubly linked (next and prev pointers), circular singly linked (30 points back to 10), and '
                      'circular doubly linked (both directions loop)')
    mk = arrow_defs(s)
    rows = [('1. singly linked', False, False), ('2. doubly linked', True, False),
            ('3. circular singly linked', False, True), ('4. circular doubly linked', True, True)]
    for r, (name, dbl, circ) in enumerate(rows):
        y = 40 + r * 92
        nodes = chain([10, 20, 30])
        if circ:
            nodes[-1].next = nodes[0]
            nodes[0].prev = nodes[-1]
        if not dbl:
            for n in nodes:
                n.prev = 'x'      # hide the prev cell
        s.text(20, y - 14, name, 13, INK, 'start', 'bold')
        x0 = 90 if dbl else 70
        if circ:
            # draw the wrap-around as a loop above the row instead of a curve under it
            last = nodes[-1]
            last.next, keep = None, last.next
            draw_nodes(s, mk, x0, y, nodes, doubly=dbl)
            px = x0 + 2 * (NODE_W + GAP) + VAL_W + (NODE_W - VAL_W) / 2
            s.rect(px - 12, y + 1, 24, NODE_H - 2, SOFT)     # cover the None slash
            s.circle(px, y + NODE_H / 2, 3, INK)
            s.add(f'<path d="M{px:.1f},{y + NODE_H / 2:.1f} L{px + 40:.1f},{y + NODE_H / 2:.1f} '
                  f'L{px + 40:.1f},{y + NODE_H + 18:.1f} L{x0 - 34:.1f},{y + NODE_H + 18:.1f} '
                  f'L{x0 - 34:.1f},{y + NODE_H / 2:.1f} L{x0 - (20 if dbl else 2):.1f},{y + NODE_H / 2:.1f}" '
                  f'stroke="{ACCENT}" stroke-width="1.6" fill="none" marker-end="{mk[ACCENT]}"/>')
            if dbl:
                s.add(f'<path d="M{x0 - 9:.1f},{y + NODE_H - 4:.1f} L{x0 - 26:.1f},{y + NODE_H - 4:.1f} '
                      f'L{x0 - 26:.1f},{y + NODE_H + 10:.1f} L{px + 32:.1f},{y + NODE_H + 10:.1f} '
                      f'L{px + 32:.1f},{y + NODE_H - 4:.1f} L{px + 16:.1f},{y + NODE_H - 4:.1f}" '
                      f'stroke="{ACCENT}" stroke-width="1.6" fill="none" marker-end="{mk[ACCENT]}"/>')
            last.next = keep
        else:
            draw_nodes(s, mk, x0, y, nodes, doubly=dbl)
    s.text(540, 390, 'slash = None (nothing there)', 11, '#6b7280', 'end')
    s.save('ds-ll-variants.svg', OUT)


def ll_memory():
    s = Svg(540, 190, 'Array versus linked list in memory: the array\'s four elements sit side by side and one fetch '
                      'brings them in; the linked list\'s nodes sit at scattered addresses 100, 8500 and 410, and each '
                      'hop is a cache miss')
    mk = arrow_defs(s)
    s.text(20, 24, 'array: side by side, one fetch', 13, INK, 'start', 'bold')
    cells(s, 20, 34, ['node 0', 'node 1', 'node 2', 'node 3'], w=64, h=32, size=12, idx_label=False,
          fills={i: DONE for i in range(4)})
    s.rect(18, 32, 260, 36, 'none', ACCENT, 2)
    s.text(290, 55, 'one 64-byte cache line', 12, ACCENT, 'start', 'bold')
    s.text(20, 104, 'linked list: scattered on the heap', 13, INK, 'start', 'bold')
    addrs = [(100, 20), (8500, 360), (410, 190)]
    for k, (a, x) in enumerate(addrs):
        s.rect(x, 116, 70, 30, SOFT, INK, 1.2)
        s.text(x + 35, 136, f'node {k}', 12)
        s.text(x + 35, 162, f'address {a}', 11, '#6b7280')
        s.text(x + 35, 178, 'cache miss', 11, TRUE, 'middle', 'bold')
    curve_arrow(s, mk, 20 + 70, 120, 360, 118, 26)
    curve_arrow(s, mk, 360 + 35, 146, 190 + 70, 140, -10)
    s.save('ds-ll-memory.svg', OUT)


def ll_insert_steps():
    a, b = LNode('20'), LNode('30')
    head = LNode('10', a)
    a.next = b
    x = LNode('25')
    frames = []
    order = [head, a, x, b]
    frames.append(('before: 25 is a new node, not linked yet', (), ()))
    snap = [(n, n.next) for n in order]
    states = [list(snap)]
    x.next = b                       # step 1, the safe order
    states.append([(n, n.next) for n in order])
    frames.append(('step 1: X.next = B (25 now points to 30)', (x,), (x,)))
    a.next = x                       # step 2
    states.append([(n, n.next) for n in order])
    frames.append(('step 2: A.next = X (20 now points to 25)', (x,), (a,)))
    vals, cur = [], head
    while cur:
        vals.append(cur.value)
        cur = cur.next
    assert vals == ['10', '20', '25', '30']
    s = Svg(470, 3 * 110 + 10, 'Inserting 25 between 20 (A) and 30 (B): before, 25 points nowhere; step 1 sets X.next = B '
                               'so 25 points to 30; step 2 sets A.next = X so 20 points to 25, giving 10, 20, 25, 30')
    mk = arrow_defs(s)
    for k, ((label, hl, hp), state) in enumerate(zip(frames, states)):
        for n, nx in state:
            n.next = nx
        y = 40 + k * 110
        s.text(20, y - 22, label, 13, INK, 'start', 'bold')
        draw_nodes(s, mk, 30, y + 6, order, tags={a: 'A', x: 'X', b: 'B'}, hl=hl, hl_ptr=hp)
    s.save('ds-ll-insert-steps.svg', OUT)


def ll_delete_steps():
    nodes = chain([10, 20, 30])
    for n in nodes:
        n.prev = None
    before = [(n, n.next) for n in nodes]
    prev, x = nodes[0], nodes[1]
    prev.next = x.next               # the one pointer change
    vals, cur = [], nodes[0]
    while cur:
        vals.append(cur.value)
        cur = cur.next
    assert vals == [10, 30]
    after = [(n, n.next) for n in nodes]
    s = Svg(400, 230, 'Deleting 20 from 10, 20, 30: one pointer change, prev.next = X.next, makes 10 point straight to '
                      '30; nothing points to 20 any more, so it is skipped')
    mk = arrow_defs(s)
    for k, (label, state) in enumerate((('before', before), ('after prev.next = X.next', after))):
        for n, nx in state:
            n.next = nx
        y = 40 + k * 110
        s.text(20, y - 22, label, 13, INK, 'start', 'bold')
        draw_nodes(s, mk, 30, y + 6, nodes, tags={prev: 'prev', x: 'X'},
                   fade=(x,) if k else (), hl_ptr=(prev,) if k else ())
    s.save('ds-ll-delete-steps.svg', OUT)


def ll_reverse_answer():
    nodes = chain([5, 8, 2])
    for n in nodes:
        n.prev = None
    prev, cur = None, nodes[0]
    states = []
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
        states.append(([(n, n.next) for n in nodes], prev, cur))
    out, c = [], prev
    while c:
        out.append(c.value)
        c = c.next
    assert out == [2, 8, 5] and len(states) == 3
    s = Svg(400, 3 * 120 + 10, 'Answer: reversing 5, 8, 2 in place. After pass 1, 5 points to None, prev is 5 and cur is '
                               '8. After pass 2, 8 points to 5, prev is 8 and cur is 2. After pass 3, 2 points to 8, prev '
                               'is 2 (the new head) and cur is None')
    mk = arrow_defs(s)
    for k, (state, pv, cu) in enumerate(states):
        for n, nx in state:
            n.next = nx
        y = 40 + k * 120
        tags = {}
        if pv is not None:
            tags[pv] = 'prev'
        if cu is not None:
            tags[cu] = 'cur'
        s.text(20, y - 22, f'after pass {k + 1}' + ('   (cur = None, so stop)' if cu is None else ''), 13, INK,
               'start', 'bold')
        draw_nodes(s, mk, 30, y + 6, nodes, tags=tags, hl=(nodes[k],), hl_ptr=(nodes[k],))
    s.save('ds-ll-reverse-answer.svg', OUT)


def linked_lists():
    ll_treasure_hunt()
    ll_variants()
    ll_memory()
    ll_insert_steps()
    ll_delete_steps()
    ll_reverse_answer()


# ======================================================================
# dsa/02-data-structures/05-stacks-and-queues.md
# ======================================================================

class CircularQueue:
    """The lesson's fixed-capacity queue with modulo wraparound."""

    def __init__(self, capacity):
        self.capacity, self.queue, self.head, self.tail, self.size = capacity, [None] * capacity, 0, 0, 0

    def enqueue(self, val):
        if self.size == self.capacity:
            return False
        self.queue[self.tail] = val
        self.tail = (self.tail + 1) % self.capacity
        self.size += 1
        return True

    def dequeue(self):
        if self.size == 0:
            return None
        val = self.queue[self.head]
        self.queue[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return val


def sq_metaphor():
    s = Svg(520, 190, 'A stack of plates with plate 3 on top, where push and pop both happen; and a queue holding 3, 2, '
                      '1, where new items enqueue at the tail on the left and dequeue from the head on the right')
    mk = arrow_defs(s)
    s.text(90, 22, 'STACK (LIFO)', 13, INK, 'middle', 'bold')
    for k in range(3):
        y = 140 - k * 34
        on = k == 2
        s.rect(40, y, 100, 28, NEWF if on else SOFT, ORANGE if on else INK, 2.5 if on else 1.2)
        s.text(90, y + 19, f'plate {k + 1}', 13)
    s.text(146, 90, '← top: push', 12, ORANGE, 'start', 'bold')
    s.text(162, 106, 'and pop here', 12, ORANGE, 'start', 'bold')
    s.text(380, 22, 'QUEUE (FIFO)', 13, INK, 'middle', 'bold')
    cells(s, 320, 80, [3, 2, 1], w=40, h=34, idx_label=False, fills={2: DONE})
    arrow(s, mk, 262, 97, 316, 97, PIX, 2)
    s.text(262, 72, 'enqueue', 12, PIX, 'start', 'bold')
    arrow(s, mk, 442, 97, 496, 97, ACCENT, 2)
    s.text(500, 72, 'dequeue', 12, ACCENT, 'end', 'bold')
    s.text(340, 134, 'tail', 12, '#6b7280')
    s.text(420, 134, 'head', 12, '#6b7280')
    s.text(380, 160, '1 arrived first, so it leaves first', 11, '#6b7280')
    s.save('ds-sq-metaphor.svg', OUT)


def sq_stack_states():
    ops = [('push', 10), ('push', 20), ('push', 30), ('pop', None), ('push', 40)]
    st, frames = [], []
    for op, v in ops:
        if op == 'push':
            st.append(v)
            frames.append((f'push {v}', list(st), None))
        else:
            out = st.pop()
            frames.append(('pop', list(st), out))
    assert [f[2] for f in frames] == [None, None, None, 30, None] and frames[-1][1] == [10, 20, 40]
    cw, ch = 86, 30
    s = Svg(20 + cw * len(frames), 200, 'A stack after each operation: push 10, push 20, push 30, then pop returns 30, '
                                        'then push 40 leaves 10, 20, 40 from bottom to top')
    for k, (label, items, out) in enumerate(frames):
        x = 20 + k * cw
        s.text(x + 34, 20, label, 12, INK, 'middle', 'bold')
        base = 170
        s.line(x + 4, base + 2, x + 64, base + 2, INK, 2)
        for j, v in enumerate(items):
            top = j == len(items) - 1
            new = top and out is None
            s.rect(x + 8, base - (j + 1) * ch, 52, ch - 3, NEWF if new else SOFT, ORANGE if new else INK,
                   2.5 if new else 1.1)
            s.text(x + 34, base - (j + 1) * ch + 18, v, 13)
        if out is not None:
            y = base - (len(items) + 1) * ch
            s.rect(x + 8, y, 52, ch - 3, FADE, GREY, 1.1)
            s.text(x + 34, y + 18, out, 13, GREY)
            s.text(x + 34, y - 8, f'→ returns {out}', 11, ACCENT, 'middle', 'bold')
        s.text(x + 34, base + 20, 'bottom', 10, '#9ca3af')
    s.save('ds-sq-stack-states.svg', OUT)


def sq_queue_states():
    from collections import deque
    ops = [('enqueue', 10), ('enqueue', 20), ('enqueue', 30), ('dequeue', None), ('enqueue', 40)]
    q, frames = deque(), []
    for op, v in ops:
        if op == 'enqueue':
            q.append(v)
            frames.append((f'enqueue {v}', list(q), None))
        else:
            frames.append(('dequeue', None, q.popleft()))
            frames[-1] = ('dequeue', list(q), frames[-1][2])
    assert frames[3][2] == 10 and frames[-1][1] == [20, 30, 40]
    s = Svg(400, 30 + 46 * len(frames) + 10, 'A queue after each operation: enqueue 10, 20, 30, then dequeue returns 10 '
                                              'from the front, then enqueue 40 leaves 20, 30, 40 from front to back')
    s.text(170, 18, 'front', 11, '#6b7280', 'start')
    for k, (label, items, out) in enumerate(frames):
        y = 28 + k * 46
        s.text(20, y + 22, label, 12, INK, 'start', 'bold')
        x = 170
        if out is not None:
            s.rect(x - 52, y, 44, 32, FADE, GREY, 1.1)
            s.text(x - 30, y + 21, out, 13, GREY)
            s.text(x - 56, y + 21, '←', 13, ACCENT, 'end', 'bold')
        for j, v in enumerate(items):
            new = j == len(items) - 1 and out is None
            s.rect(x + j * 44, y, 44, 32, NEWF if new else SOFT, ORANGE if new else INK, 2.5 if new else 1.1)
            s.text(x + j * 44 + 22, y + 21, v, 13)
    s.text(118 - 4, 28 + 3 * 46 - 6, 'returns 10', 11, ACCENT, 'start', 'bold')
    s.save('ds-sq-queue-states.svg', OUT)


def sq_circular():
    q = CircularQueue(5)
    script = [('enq', 1), ('enq', 2), ('enq', 3), ('enq', 4), ('deq', None), ('deq', None), ('enq', 5), ('enq', 6),
              ('enq', 7)]
    frames = []
    for op, v in script:
        if op == 'enq':
            ok = q.enqueue(v)
            assert ok
            frames.append((f'enqueue {v}', list(q.queue), q.head, q.tail, (q.tail - 1) % 5))
        else:
            out = q.dequeue()
            frames.append((f'dequeue → {out}', list(q.queue), q.head, q.tail, None))
    # keep the interesting frames: after 4 enqueues, after 2 dequeues, then each wrapping enqueue
    keep = [frames[3], frames[5], frames[6], frames[7], frames[8]]
    keep[0] = ('enqueue 1, 2, 3, 4',) + keep[0][1:]
    keep[1] = ('dequeue twice (→ 1, 2)',) + keep[1][1:4] + (None,)
    assert q.queue == [6, 7, 3, 4, 5] and q.head == 2 and q.tail == 2 and q.size == 5
    w, rh = 46, 66
    s = Svg(470, 20 + rh * len(keep) + 10, 'Circular buffer with 5 slots: after enqueue 1, 2, 3, 4 and two dequeues, '
                                            'head is at slot 2; 5 goes in slot 4, then tail wraps to slot 0 so 6 and 7 '
                                            'reuse slots 0 and 1; the buffer ends full with 3, 4, 5, 6, 7 in order')
    for k, (label, arr, h, tl, new) in enumerate(keep):
        y = 30 + k * rh
        s.text(20, y + 20, label, 12, INK, 'start', 'bold')
        x0 = 200
        for i, v in enumerate(arr):
            on = i == new
            s.rect(x0 + i * w, y, w, 30, NEWF if on else (SOFT if v is not None else FADE), ORANGE if on else INK,
                   2.5 if on else 1.1)
            s.text(x0 + i * w + w / 2, y + 20, '—' if v is None else v, 13, GREY if v is None else INK)
            if k == 0:
                s.text(x0 + i * w + w / 2, y - 8, i, 10, '#6b7280')
        if h == tl:
            s.text(x0 + h * w + w / 2, y + 46, 'H T', 11, PIX, 'middle', 'bold')
        else:
            s.text(x0 + h * w + w / 2, y + 46, 'H', 11, ACCENT, 'middle', 'bold')
            s.text(x0 + tl * w + w / 2, y + 46, 'T', 11, PIX, 'middle', 'bold')
    s.text(20, 20 + rh * len(keep) + 2, 'H = head (next to leave), T = tail (next free slot)', 11, '#6b7280', 'start')
    s.h += 6
    s.save('ds-sq-circular-buffer.svg', OUT)


def stacks_queues():
    sq_metaphor()
    sq_stack_states()
    sq_queue_states()
    sq_circular()


# ======================================================================
# dsa/02-data-structures/06-trees/01-trees.md
# ======================================================================

def tree_layout(children, root, dx=64, dy=70):
    """Leaves get consecutive x slots, parents sit centred over their children. Returns node -> (x, y), depth."""
    pos, depth, nxt = {}, {}, [0]

    def walk(n, d):
        depth[n] = d
        kids = children.get(n, [])
        if not kids:
            x = nxt[0]
            nxt[0] += 1
        else:
            xs = [walk(c, d + 1) for c in kids]
            x = (xs[0] + xs[-1]) / 2
        pos[n] = x
        return x

    walk(root, 0)
    return {n: (pos[n] * dx, depth[n] * dy) for n in pos}, depth


def gen_height(children, n):
    kids = children.get(n, [])
    return 0 if not kids else 1 + max(gen_height(children, c) for c in kids)


def draw_svg_tree(s, children, root, ox, oy, fills=None, strokes=None, notes=None, r=17, dx=64, dy=70):
    pos, depth = tree_layout(children, root, dx, dy)
    fills, strokes, notes = fills or {}, strokes or {}, notes or {}
    for n, kids in children.items():
        for c in kids:
            (x1, y1), (x2, y2) = pos[n], pos[c]
            s.line(ox + x1, oy + y1, ox + x2, oy + y2, INK, 1.4)
    for n, (x, y) in pos.items():
        st = strokes.get(n, INK)
        sw = 3 if st != INK else 1.3
        if n in notes:      # a box with the name on top and the note underneath
            s.add(f'<rect x="{ox + x - 26:.1f}" y="{oy + y - 20:.1f}" width="52" height="40" rx="8" '
                  f'fill="{fills.get(n, SOFT)}" stroke="{st}" stroke-width="{sw}"/>')
            s.text(ox + x, oy + y - 3, n, 14, INK, 'middle', 'bold')
            s.text(ox + x, oy + y + 13, notes[n], 11, '#b45309', 'middle', 'bold')
            continue
        s.add(f'<circle cx="{ox + x:.1f}" cy="{oy + y:.1f}" r="{r}" fill="{fills.get(n, SOFT)}" stroke="{st}" '
              f'stroke-width="{sw}"/>')
        s.text(ox + x, oy + y + 5, n, 14, INK, 'middle', 'bold')
    return pos, depth


ABCDEF = {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': ['F']}


def trees_parts():
    pos, depth = tree_layout(ABCDEF, 'A')
    leaves = [n for n in pos if not ABCDEF.get(n)]
    assert sorted(leaves) == ['D', 'E', 'F'] and sum(map(len, ABCDEF.values())) == len(pos) - 1
    s = Svg(420, 250, 'A tree with root A; A has children B and C; B has children D and E; C has child F. D, E and F '
                      'are leaves. B with D and E is a subtree')
    s.rect(40, 70, 160, 140, '#fef3c7', 'none', 0, 0.6)
    s.text(46, 204, 'subtree rooted at B', 11, '#92400e', 'start')
    fills = {n: DONE for n in leaves}
    fills['A'] = '#fde68a'
    p, _ = draw_svg_tree(s, ABCDEF, 'A', 90, 40, fills=fills)
    s.text(90 + p['A'][0] + 26, 45, '← root (no parent)', 12, INK, 'start')
    s.text(90 + p['F'][0] + 26, 40 + p['F'][1] + 5, '← leaves (no children)', 12, ACCENT, 'start', 'bold')
    s.text(90 + p['C'][0] + 26, 40 + p['C'][1] + 5, '← internal node', 12, PIX, 'start')
    s.save('ds-tree-parts.svg', OUT)


def depth_height_picture(children, root, name, title, w=420):
    pos, depth = tree_layout(children, root)
    hts = {n: gen_height(children, n) for n in pos}
    levels = max(depth.values()) + 1
    s = Svg(w, 70 * levels + 44, title)
    for L in range(levels):
        y = 56 + L * 70
        s.rect(10, y - 24, w - 20, 48, '#f9fafb' if L % 2 else '#eef2ff', 'none')
        s.text(18, y + 4, f'level {L}', 11, '#6b7280', 'start')
    notes = {n: f'd{depth[n]} h{hts[n]}' for n in pos}
    s.text(w / 2, 18, 'd = depth (edges down from the root)   h = height (edges down to its deepest leaf)', 11,
           '#6b7280')
    xs = [x for x, _ in pos.values()]
    ox = (w - (max(xs) - min(xs))) / 2 + 20
    draw_svg_tree(s, children, root, ox, 56, notes=notes, r=15)
    return depth, hts, s


def trees_depth_height():
    depth, hts, s = depth_height_picture(
        ABCDEF, 'A', 'ds-tree-depth-height.svg',
        'Depth and height on the tree A to F. Depths: A 0, B and C 1, D, E and F 2. Heights: D, E and F 0, B and C 1, '
        'A 2, so the height of the tree is 2')
    assert depth == {'A': 0, 'B': 1, 'D': 2, 'E': 2, 'C': 1, 'F': 2}
    assert hts['A'] == 2 and hts['B'] == 1 and hts['D'] == 0 and hts['C'] == 1
    s.save('ds-tree-depth-height.svg', OUT)


def trees_sketch_answer():
    kids = {'M': ['N', 'O', 'W'], 'N': ['X'], 'W': ['Y', 'Z'], 'Z': ['K']}
    depth, hts, s = depth_height_picture(
        kids, 'M', 'ds-tree-sketch-answer.svg',
        'Answer: root M with children N, O and W; N has child X; W has children Y and Z; Z has child K. Depths: M 0; '
        'N, O, W 1; X, Y, Z 2; K 3. Heights: K, X, O, Y 0; N and Z 1; W 2; M 3', w=440)
    assert depth['K'] == 3 and hts == {'M': 3, 'N': 1, 'X': 0, 'O': 0, 'W': 2, 'Y': 0, 'Z': 1, 'K': 0}
    s.save('ds-tree-sketch-answer.svg', OUT)


def trees():
    trees_parts()
    trees_depth_height()
    trees_sketch_answer()


# ======================================================================
# dsa/02-data-structures/06-trees/02-binary-trees.md
# ======================================================================

def bt_is_full(k, n):
    if n is None:
        return True
    l, r = k.get(n, (None, None))
    return (l is None) == (r is None) and bt_is_full(k, l) and bt_is_full(k, r)


def bt_count(k, n):
    if n is None:
        return 0
    l, r = k.get(n, (None, None))
    return 1 + bt_count(k, l) + bt_count(k, r)


def bt_is_perfect(k, n):
    return bt_count(k, n) == 2 ** (height(k, n) + 1) - 1


def bt_is_complete(k, root):
    q, gap = [root], False
    while q:
        x = q.pop(0)
        if x is None:
            gap = True
        else:
            if gap:
                return False
            q += list(k.get(x, (None, None)))
    return True


def bt_is_balanced(k, n):
    if n is None:
        return True
    l, r = k.get(n, (None, None))
    return abs(height(k, l) - height(k, r)) <= 1 and bt_is_balanced(k, l) and bt_is_balanced(k, r)


def bt_is_degenerate(k, n):
    if n is None:
        return True
    l, r = k.get(n, (None, None))
    return not (l is not None and r is not None) and bt_is_degenerate(k, l) and bt_is_degenerate(k, r)


SHAPES = {
    'full': ({1: (2, 3), 2: (4, 5)}, 'Full binary tree: 1 has children 2 and 3, 2 has children 4 and 5; every node has '
                                     '0 or 2 children'),
    'complete': ({1: (2, 3), 2: (4, 5), 3: (6, None)}, 'Complete binary tree: levels 1 and 2 are full and the last '
                                                       'level holds 4, 5, 6 filled from the left'),
    'perfect': ({1: (2, 3), 2: (4, 5), 3: (6, 7)}, 'Perfect binary tree of height 2: 7 nodes, every internal node '
                                                   'has 2 children and all leaves 4, 5, 6, 7 are at depth 2'),
    'balanced': ({1: (2, 3), 2: (4, None)}, 'Balanced binary tree: 1 has children 2 and 3, 2 has a left child 4; '
                                            'subtree heights differ by at most 1 everywhere'),
    'degenerate': ({1: (None, 2), 2: (None, 3), 3: (None, 4)}, 'Degenerate binary tree: 1, 2, 3, 4 in a straight line '
                                                               'of right children, like a linked list'),
}


def binary_shapes():
    expect = {  # full, complete, perfect, balanced, degenerate
        'full': (True, True, False, True, False), 'complete': (False, True, False, True, False),
        'perfect': (True, True, True, True, False), 'balanced': (False, True, False, True, False),
        'degenerate': (False, False, False, False, True)}
    for name, (k, title) in SHAPES.items():
        got = (bt_is_full(k, 1), bt_is_complete(k, 1), bt_is_perfect(k, 1), bt_is_balanced(k, 1),
               bt_is_degenerate(k, 1))
        assert got == expect[name], (name, got)
        bin_tree_svg(k, 1, f'ds-bt-{name}.svg', title, dx=46)


def heap_positions(n, dx=48, dy=62):
    """Node i of a complete tree: level-by-level positions so the last level is evenly spaced."""
    import math
    levels = int(math.log2(n)) + 1 if n else 0
    width = 2 ** (levels - 1) * dx
    pos = {}
    for i in range(n):
        d = int(math.log2(i + 1))
        k = i + 1 - 2 ** d
        span = width / 2 ** d
        pos[i] = (span * (k + 0.5), d * dy)
    return pos, width, levels


def tree_and_array(s, vals, ox, oy, ax, ay, hl=(), hl2=(), cellw=40, dx=48, dy=62, show_idx=True, arrows=()):
    """A complete binary tree (from array order) drawn above its array. hl: indexes outlined orange.
    hl2: indexes shaded light orange. arrows: (i, j) pairs drawn as orange swap/link arrows on the tree."""
    pos, width, levels = heap_positions(len(vals), dx, dy)
    for i in range(1, len(vals)):
        (x1, y1), (x2, y2) = pos[(i - 1) // 2], pos[i]
        s.line(ox + x1, oy + y1, ox + x2, oy + y2, INK, 1.3)
    for i, v in enumerate(vals):
        x, y = pos[i]
        on, sh = i in hl, i in hl2
        s.add(f'<circle cx="{ox + x:.1f}" cy="{oy + y:.1f}" r="17" fill="{NEWF if (on or sh) else SOFT}" '
              f'stroke="{ORANGE if on else INK}" stroke-width="{3 if on else 1.3}"/>')
        s.text(ox + x, oy + y + 5, v, 13, INK, 'middle', 'bold')
        if show_idx:
            s.text(ox + x + 20, oy + y - 12, i, 10, PIX, 'start', 'bold')
    for i, v in enumerate(vals):
        on, sh = i in hl, i in hl2
        s.rect(ax + i * cellw, ay, cellw, 32, NEWF if (on or sh) else SOFT, ORANGE if on else INK, 3 if on else 1.1)
        s.text(ax + i * cellw + cellw / 2, ay + 21, v, 13, INK, 'middle', 'bold')
        s.text(ax + i * cellw + cellw / 2, ay + 46, i, 10, PIX, 'middle', 'bold')
    return pos


def bt_array_storage():
    vals = list('ABCDEF')
    assert vals[2 * 1 + 1] == 'D' and vals[(4 - 1) // 2] == 'B' and vals[2 * 2 + 1] == 'F'
    s = Svg(470, 250, 'Complete binary tree A to F numbered level by level, A at index 0 to F at index 5, stored as the '
                      'array A, B, C, D, E, F. The left child of B (index 1) is at 2 × 1 + 1 = 3, which is D; the parent '
                      'of E (index 4) is at (4 − 1) // 2 = 1, which is B')
    tree_and_array(s, vals, 14, 34, 240, 60, hl=(1, 3), cellw=36, dx=56)
    s.text(240, 30, 'array, index under each cell', 11, '#6b7280', 'start')
    s.text(240, 140, 'left child of B (1): 2·1 + 1 = 3 → D', 12, ORANGE, 'start', 'bold')
    s.text(240, 162, 'right child of B (1): 2·1 + 2 = 4 → E', 12, INK, 'start')
    s.text(240, 184, 'parent of E (4): (4 − 1) // 2 = 1 → B', 12, INK, 'start')
    s.text(240, 206, 'parent of F (5): (5 − 1) // 2 = 2 → C', 12, INK, 'start')
    s.text(20, 236, 'blue numbers = array index', 11, PIX, 'start')
    s.save('ds-bt-array-storage.svg', OUT)


def bt_sketch_answer():
    vals = [7, 3, 9, 1, 5, 8, 2, 6]
    assert vals[2 * 3 + 1] == 6 and (7 - 1) // 2 == 3
    s = Svg(430, 315, 'Answer: the array 7, 3, 9, 1, 5, 8, 2, 6 as a complete binary tree. 7 is the root; 3 and 9 are '
                      'its children; 1 and 5 are children of 3; 8 and 2 are children of 9; 6 is the left child of 1')
    tree_and_array(s, vals, 20, 30, 50, 254, hl=(7,), cellw=40)
    s.save('ds-bt-sketch-answer.svg', OUT)


def binary_trees():
    binary_shapes()
    bt_array_storage()
    bt_sketch_answer()


# ======================================================================
# dsa/02-data-structures/06-trees/03-binary-search-trees.md
# ======================================================================

def build_bst(keys):
    kids, root = {}, None
    for k in keys:
        root = bst_insert(kids, root, k)
    return kids, root


def bst_path(kids, root, key):
    path, cur = [], root
    while cur is not None:
        path.append(cur)
        if key == cur:
            break
        cur = kids[cur][0] if key < cur else kids[cur][1]
    return path


def bst_delete(kids, root, key):
    """Delete as the lesson teaches: leaf -> remove; one child -> child takes its place; two children -> copy the
    in-order successor (smallest in the right subtree) into the node, then delete the successor."""
    kids = {n: tuple(c) for n, c in kids.items()}

    def rec(n, key):
        if n is None:
            return None
        l, r = kids[n]
        if key < n:
            kids[n] = (rec(l, key), r)
            return n
        if key > n:
            kids[n] = (l, rec(r, key))
            return n
        if l is None or r is None:
            del kids[n]
            return l if l is not None else r
        succ = r
        while kids[succ][0] is not None:
            succ = kids[succ][0]
        new_r = rec(r, succ)
        del kids[n]
        kids[succ] = (l, new_r)
        return succ

    root = rec(root, key)
    return {n: c for n, c in kids.items()}, root


def path_edges(path):
    return set(zip(path, path[1:]))


LESSON_BST = [8, 3, 10, 1, 6, 14, 4, 7, 13]


def bst_valid():
    kids, root = build_bst(LESSON_BST)
    assert kids[8] == (3, 10) and kids[3] == (1, 6) and kids[10] == (None, 14) and kids[6] == (4, 7)
    assert kids[14] == (13, None) and inorder(kids, root) == sorted(LESSON_BST)
    left = inorder(kids, 3)
    assert left == [1, 3, 4, 6, 7]
    s = Svg(440, 250, 'A valid binary search tree: 8 at the root; 3 left with children 1 and 6, and 6 has 4 and 7; 10 '
                      'right with right child 14, which has left child 13. Everything left of 8 is smaller, everything '
                      'right is larger')
    s.rect(14, 64, 210, 160, '#dbeafe', 'none', 0, 0.35)
    s.rect(270, 64, 150, 160, '#d1fae5', 'none', 0, 0.45)
    s.text(20, 216, 'left of 8: 1, 3, 4, 6, 7 (all < 8)', 11, PIX, 'start', 'bold')
    s.text(414, 216, 'right of 8: 10, 13, 14 (all > 8)', 11, ACCENT, 'end', 'bold')
    draw_bin_tree(s, kids, root, 40, 36, dx=44, dy=52)
    s.save('ds-bst-valid.svg', OUT)


def bst_build_steps():
    keys = LESSON_BST
    cols, pw, ph = 3, 200, 200
    rows = (len(keys) + cols - 1) // cols
    s = Svg(cols * pw + 10, rows * ph + 10, 'The binary search tree built one insert at a time from 8, 3, 10, 1, 6, 14, '
            '4, 7, 13. Each panel shows the tree after one insert, with the new key and the path it took outlined '
            'in orange')
    kids, root = {}, None
    for i, k in enumerate(keys):
        root = bst_insert(kids, root, k)
        path = bst_path(kids, root, k)
        assert path[-1] == k
        px, py = 10 + (i % cols) * pw, 10 + (i // cols) * ph
        s.rect(px, py, pw - 10, ph - 10, '#f9fafb', '#e5e7eb', 1)
        turns = ' → '.join(str(n) for n in path[:-1]) if len(path) > 1 else 'empty tree: root'
        s.text(px + 8, py + 18, f'{i + 1}. insert {k}', 12, INK, 'start', 'bold')
        s.text(px + 8, py + 33, turns if len(path) == 1 else f'via {turns}', 10, '#6b7280', 'start')
        dx, dy = 22, 38
        w, _ = tree_extent(kids, root, dx, dy)
        pos = bin_layout(kids, root, dx, dy)
        minx = min(x for x, _ in pos.values())
        draw_bin_tree(s, kids, root, px + (pw - 10 - w) / 2 - minx, py + 56, hl=(k,), hl_edges=path_edges(path),
                      dx=dx, dy=dy, r=12, size=11)
    assert kids == build_bst(keys)[0]
    s.save('ds-bst-build-steps.svg', OUT)


def bst_search_path():
    kids, root = build_bst(LESSON_BST)
    path = bst_path(kids, root, 7)
    assert path == [8, 3, 6, 7]
    s = Svg(460, 250, 'Searching the tree for 7: 7 is less than 8 so go left to 3; 7 is more than 3 so go right to 6; 7 is more than 6 so go right to '
                      '7, found after 4 nodes. The right side of 8 is never looked at')
    draw_bin_tree(s, kids, root, 70, 36, hl=(7,), done=(8, 3, 6), fade=(10, 14, 13, 1, 4),
                  hl_edges=path_edges(path), dx=44, dy=52)
    notes = [(8, '7 < 8: go left', 1), (3, '7 > 3: go right', -1), (6, '7 > 6: go right', 1), (7, 'found', 1)]
    pos = bin_layout(kids, root, 44, 52)
    for n, txt, side in notes:
        x, y = pos[n]
        s.text(70 + x + 22 * side, 36 + y + (5 if side < 0 else -14), txt, 11, ORANGE,
               'start' if side > 0 else 'end', 'bold')
    s.save('ds-bst-search-path.svg', OUT)


def rotate_right(kids, n):
    """Right rotation at n: its left child p becomes the subtree root, p's right subtree moves under n."""
    kids = dict(kids)
    p = kids[n][0]
    pl, pr = kids[p]
    kids[n] = (pr, kids[n][1])
    kids[p] = (pl, n)
    return kids, p


def bst_rotation():
    kids = {5: (3, 'D'), 3: ('A', 'C'), 'A': (None, None), 'C': (None, None), 'D': (None, None)}
    order = {'A': 0, 3: 1, 'C': 2, 5: 3, 'D': 4}

    def io(k, n):   # in-order with mixed labels, using the order above
        return inorder_any(k, n)
    before = inorder_any(kids, 5)
    after_k, new_root = rotate_right(kids, 5)
    assert new_root == 3 and after_k[3] == ('A', 5) and after_k[5] == ('C', 'D')
    assert inorder_any(after_k, 3) == before == ['A', 3, 'C', 5, 'D']
    s = Svg(470, 200, 'Right rotation on node 5: before, 5 has left child 3 (with subtrees A and C) and right subtree '
                      'D. After, 3 is on top with A on its left and 5 on its right; C moves across to become 5\'s left '
                      'subtree. The in-order order A, 3, C, 5, D does not change')
    mk = arrow_defs(s)
    sub = ('A', 'C', 'D')
    lab = {}
    draw_any(s, kids, 5, 40, 40, order, hl=(5, 3), fade=sub)
    arrow(s, mk, 215, 100, 255, 100, INK, 2)
    s.text(235, 88, 'rotate', 11, '#6b7280')
    draw_any(s, after_k, 3, 280, 40, order, hl=(5, 3), fade=sub, hl_edge=(5, 'C'))
    s.text(235, 186, 'A, C, D are whole subtrees; in-order stays A, 3, C, 5, D', 11, '#6b7280')
    s.save('ds-bst-rotation.svg', OUT)


def inorder_any(kids, n):
    if n is None:
        return []
    l, r = kids.get(n, (None, None))
    return inorder_any(kids, l) + [n] + inorder_any(kids, r)


def draw_any(s, kids, root, ox, oy, xorder, hl=(), fade=(), hl_edge=None, dx=36, dy=52):
    """Small tree whose x positions come from a fixed in-order rank (so mixed labels work)."""
    pos = {}

    def walk(n, d):
        if n is None:
            return
        pos[n] = (xorder[n] * dx, d * dy)
        l, r = kids.get(n, (None, None))
        walk(l, d + 1)
        walk(r, d + 1)
    walk(root, 0)
    minx = min(x for x, _ in pos.values())
    for n, (l, r) in kids.items():
        for c in (l, r):
            if c is None or n not in pos:
                continue
            (x1, y1), (x2, y2) = pos[n], pos[c]
            on = hl_edge == (n, c)
            s.line(ox + x1 - minx, oy + y1, ox + x2 - minx, oy + y2, ORANGE if on else INK, 3 if on else 1.4)
    for n, (x, y) in pos.items():
        x -= minx
        if n in fade:
            s.add(f'<polygon points="{ox + x:.1f},{oy + y - 16:.1f} {ox + x - 17:.1f},{oy + y + 14:.1f} '
                  f'{ox + x + 17:.1f},{oy + y + 14:.1f}" fill="{FADE}" stroke="{GREY}" stroke-width="1.3"/>')
            s.text(ox + x, oy + y + 9, n, 12, '#4b5563', 'middle', 'bold')
        else:
            on = n in hl
            s.add(f'<circle cx="{ox + x:.1f}" cy="{oy + y:.1f}" r="16" fill="{NEWF if on else SOFT}" '
                  f'stroke="{ORANGE if on else INK}" stroke-width="{2.5 if on else 1.3}"/>')
            s.text(ox + x, oy + y + 5, n, 13, INK, 'middle', 'bold')


def bst_delete_cases():
    kids, root = build_bst(LESSON_BST)
    cases = [(13, 'leaf: just remove it'), (14, 'one child: 13 moves up into its place'),
             (3, 'two children: copy in the successor 4, then remove 4 from below')]
    s = Svg(620, 3 * 215 + 10, 'The three delete cases on the tree 8, 3, 10, 1, 6, 14, 4, 7, 13. Deleting the leaf 13 '
                               'just removes it. Deleting 14, which has one child, moves 13 up. Deleting 3, which has two '
                               'children, copies in its in-order successor 4 and removes 4 from under 6')
    mk = arrow_defs(s)
    for i, (key, label) in enumerate(cases):
        y = 10 + i * 215
        s.text(16, y + 18, f'delete {key}: {label}', 13, INK, 'start', 'bold')
        after, new_root = bst_delete(kids, root, key)
        assert inorder(after, new_root) == [k for k in sorted(LESSON_BST) if k != key]
        hl_after = ()
        if key == 14:
            assert after[10] == (None, 13)
            hl_after = (13,)
        if key == 3:
            assert after[8] == (4, 10) and after[4] == (1, 6) and after[6] == (None, 7)
            hl_after = (4,)
        draw_bin_tree(s, kids, root, 30, y + 50, hl=(key,), dx=30, dy=44, r=14, size=12)
        arrow(s, mk, 300, y + 110, 330, y + 110, INK, 2)
        draw_bin_tree(s, after, new_root, 350, y + 50, hl=hl_after, dx=30, dy=44, r=14, size=12)
    s.save('ds-bst-delete-cases.svg', OUT)


def bst_sketch_answer():
    keys = [41, 20, 65, 11, 29, 50, 91, 32, 72]
    kids, root = build_bst(keys)
    assert kids[41] == (20, 65) and kids[20] == (11, 29) and kids[29] == (None, 32) and kids[65] == (50, 91)
    assert kids[91] == (72, None) and height(kids, root) == 3
    bin_tree_svg(kids, root, 'ds-bst-sketch-answer.svg',
                 'Answer: 41 at the root; 20 left with children 11 and 29, and 32 is the right child of 29; 65 right '
                 'with children 50 and 91, and 72 is the left child of 91', dx=44, dy=56)


def bsts():
    bst_valid()
    bst_build_steps()
    bst_search_path()
    bst_rotation()
    bst_delete_cases()
    bst_sketch_answer()


# ======================================================================
# dsa/02-data-structures/06-trees/04-traversal/01-depth-first-traversals.md
# ======================================================================

REF_TREE = {1: (2, 3), 2: (4, 5)}


def dfs_reference_tree():
    s = Svg(330, 190, 'The reference tree: root 1 with left child 2 and right child 3; 2 has left child 4 and right '
                      'child 5')
    pos = draw_bin_tree(s, REF_TREE, 1, 40, 34, dx=46, dy=58)
    for d, name in enumerate(('root, level 0', 'level 1', 'level 2')):
        s.text(320, 34 + d * 58 + 5, name, 11, '#6b7280', 'end')
    s.save('ds-dfs-reference-tree.svg', OUT)


def dfs_three_orders():
    orders = [('pre-order: node, left, right', preorder(REF_TREE, 1)),
              ('in-order: left, node, right', inorder(REF_TREE, 1)),
              ('post-order: left, right, node', postorder(REF_TREE, 1))]
    assert [o for _, o in orders] == [[1, 2, 4, 5, 3], [4, 2, 5, 1, 3], [4, 5, 2, 3, 1]]
    pw = 210
    s = Svg(pw * 3 + 10, 230, 'The reference tree three times, with orange badges giving the visit order. Pre-order '
                              'visits 1, 2, 4, 5, 3. In-order visits 4, 2, 5, 1, 3. Post-order visits 4, 5, 2, 3, 1')
    for i, (name, seq) in enumerate(orders):
        x0 = 10 + i * pw
        s.rect(x0, 8, pw - 10, 214, '#f9fafb', '#e5e7eb', 1)
        s.text(x0 + (pw - 10) / 2, 28, name, 12, INK, 'middle', 'bold')
        draw_bin_tree(s, REF_TREE, 1, x0 + 22, 64, order={n: k + 1 for k, n in enumerate(seq)}, dx=40, dy=52)
        s.text(x0 + (pw - 10) / 2, 208, ', '.join(map(str, seq)), 13, ORANGE, 'middle', 'bold')
    s.save('ds-dfs-three-orders.svg', OUT)


def dfs_preorder_stack():
    stack, frames, visited = [1], [], []
    frames.append(('start', list(stack), None))
    while stack:
        n = stack.pop()
        visited.append(n)
        l, r = REF_TREE.get(n, (None, None))
        if r:
            stack.append(r)
        if l:
            stack.append(l)
        frames.append((f'pop {n}, visit it', list(stack), n))
    assert visited == preorder(REF_TREE, 1)
    assert [f[1] for f in frames] == [[1], [3, 2], [3, 5, 4], [3, 5], [3], [], ]
    cw, ch = 84, 30
    s = Svg(20 + cw * len(frames), 205, 'Iterative pre-order on the reference tree, stack shown bottom to top after '
                                        'each step: start [1]; pop 1, push 3 then 2, giving [3, 2]; pop 2, push 5 then '
                                        '4, giving [3, 5, 4]; pop 4 gives [3, 5]; pop 5 gives [3]; pop 3 leaves it '
                                        'empty. Visit order 1, 2, 4, 5, 3')
    for k, (label, items, out) in enumerate(frames):
        x = 20 + k * cw
        s.text(x + 34, 20, label.split(',')[0], 12, INK, 'middle', 'bold')
        if out is not None:
            s.text(x + 34, 36, 'visit ' + str(out), 11, ORANGE, 'middle', 'bold')
        base = 160
        s.line(x + 4, base + 2, x + 64, base + 2, INK, 2)
        prev = frames[k - 1][1] if k else []
        for j, v in enumerate(items):
            new = k > 0 and v not in prev
            s.rect(x + 8, base - (j + 1) * ch, 52, ch - 3, NEWF if new else SOFT, ORANGE if new else INK,
                   2.5 if new else 1.1)
            s.text(x + 34, base - (j + 1) * ch + 18, v, 13)
        if not items:
            s.text(x + 34, base - 12, 'empty', 11, GREY)
    s.text(20, 192, 'orange = just pushed; the top of each stack is popped next', 11, '#6b7280', 'start')
    s.save('ds-dfs-preorder-stack.svg', OUT)


def dfs_sketch_answer():
    kids = {'P': ('Q', 'R'), 'Q': (None, 'S'), 'R': ('T', 'U'), 'T': ('V', None)}
    seq = inorder(kids, 'P')
    assert seq == ['Q', 'S', 'P', 'V', 'T', 'R', 'U']
    s = bin_tree_svg(kids, 'P', 'ds-dfs-sketch-answer.svg',
                     'Answer: root P with left child Q and right child R; Q has right child S; R has children T and U; T '
                     'has left child V. In-order badges: Q 1, S 2, P 3, V 4, T 5, R 6, U 7',
                     order={n: k + 1 for k, n in enumerate(seq)}, dx=46, dy=58)


def dfs():
    dfs_reference_tree()
    dfs_three_orders()
    dfs_preorder_stack()
    dfs_sketch_answer()


# ======================================================================
# dsa/02-data-structures/06-trees/04-traversal/02-level-order-traversal.md
# ======================================================================

def bfs_queue_states(kids, root):
    from collections import deque
    q, frames = deque([root]), [('start', [root], None)]
    while q:
        n = q.popleft()
        for c in kids.get(n, (None, None)):
            if c is not None:
                q.append(c)
        frames.append((f'pop {n}', list(q), n))
    return frames


def bfs_level_order_picture():
    frames = bfs_queue_states(REF_TREE, 1)
    seq = [f[2] for f in frames if f[2] is not None]
    assert seq == levelorder(REF_TREE, 1) == [1, 2, 3, 4, 5]
    assert [f[1] for f in frames] == [[1], [2, 3], [3, 4, 5], [4, 5], [5], []]
    s = Svg(520, 250, 'Level-order on the reference tree. The badges give the visit order 1, 2, 3, 4, 5, level by level. '
                      'The queue, front on the left: start [1]; pop 1, add 2 and 3; pop 2, add 4 and 5, giving [3, 4, 5]; '
                      'pop 3 gives [4, 5]; pop 4 gives [5]; pop 5 leaves it empty')
    draw_bin_tree(s, REF_TREE, 1, 26, 40, order={n: k + 1 for k, n in enumerate(seq)}, dx=40, dy=58)
    s.text(106, 210, 'badge = visit order', 12, ORANGE, 'middle', 'bold')
    s.text(250, 22, 'queue after each step (front on the left)', 12, INK, 'start', 'bold')
    for k, (label, items, out) in enumerate(frames):
        y = 36 + k * 34
        s.text(306, y + 19, label, 12, ORANGE if out else INK, 'end', 'bold')
        prev = frames[k - 1][1] if k else []
        for j, v in enumerate(items):
            new = k > 0 and v not in prev
            s.rect(318 + j * 36, y, 36, 28, NEWF if new else SOFT, ORANGE if new else INK, 2.5 if new else 1.1)
            s.text(318 + j * 36 + 18, y + 19, v, 13)
        if not items:
            s.text(318, y + 19, 'empty: done', 11, GREY, 'start')
    s.save('ds-bfs-queue-states.svg', OUT)


def bfs_sketch_answer():
    kids = {10: (6, 15), 6: (3, 8), 15: (None, 20), 8: (7, None), 20: (18, 25)}
    seq = levelorder(kids, 10)
    assert seq == [10, 6, 15, 3, 8, 20, 7, 18, 25]
    bin_tree_svg(kids, 10, 'ds-bfs-sketch-answer.svg',
                 'Answer: root 10 with children 6 and 15; 6 has children 3 and 8; 15 has right child 20; 8 has left '
                 'child 7; 20 has children 18 and 25. Level-order badges: 10 is 1, 6 is 2, 15 is 3, 3 is 4, 8 is 5, '
                 '20 is 6, 7 is 7, 18 is 8, 25 is 9', order={n: k + 1 for k, n in enumerate(seq)}, dx=44, dy=58)


def level_order():
    bfs_level_order_picture()
    bfs_sketch_answer()


# ======================================================================
# dsa/02-data-structures/07-heaps.md
# ======================================================================

def is_min_heap(a):
    return all(a[(i - 1) // 2] <= a[i] for i in range(1, len(a)))


def heap_push_frames(a, v):
    """Min-heap push as the lesson teaches: append, then swap up while smaller than the parent."""
    a = list(a) + [v]
    i = len(a) - 1
    frames = [(f'append {v} at index {i}', list(a), (i,), ())]
    while i > 0 and a[i] < a[(i - 1) // 2]:
        p = (i - 1) // 2
        a[i], a[p] = a[p], a[i]
        frames.append((f'{v} < {a[i]}: swap with its parent (index {i} ↔ {p})', list(a), (p,), (i,)))
        i = p
    return a, frames


def sift_down(a, i, frames=None, who=None):
    n = len(a)
    while True:
        l, r, m = 2 * i + 1, 2 * i + 2, i
        if l < n and a[l] < a[m]:
            m = l
        if r < n and a[r] < a[m]:
            m = r
        if m == i:
            return a
        a[i], a[m] = a[m], a[i]
        if frames is not None:
            frames.append((f'{a[m]} > {a[i]}: swap with smaller child (index {i} ↔ {m})', list(a), (m,), (i,)))
        i = m


def heap_pop_frames(a):
    a = list(a)
    top = a[0]
    last = a.pop()
    a[0] = last
    frames = [(f'take {top}; move last item {last} to the root', list(a), (0,), ())]
    sift_down(a, 0, frames)
    return top, a, frames


def heap_frames_picture(frames, name, title, cellw=36):
    n = max(len(f[1]) for f in frames)
    pos, width, levels = heap_positions(n, 40, 50)
    fh = levels * 50 + 50
    W = 30 + width + 30 + n * cellw + 20
    s = Svg(W, 10 + fh * len(frames), title)
    for k, (label, arr, hl, hl2) in enumerate(frames):
        y = 10 + k * fh
        s.rect(6, y, W - 12, fh - 8, '#f9fafb', '#e5e7eb', 1)
        s.text(16, y + 20, f'{k + 1}. {label}', 12, INK, 'start', 'bold')
        tree_and_array(s, arr, 26, y + 46, 30 + width + 20, y + 46 + (levels - 1) * 25 - 16, hl=hl, hl2=hl2,
                       cellw=cellw, dx=40, dy=50)
    s.save(name, OUT)


def heap_triage():
    src = f"""digraph {{ bgcolor="white"; pad=0.25; nodesep=0.5; ranksep=0.4;
node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2];
d [label="ER triage desk", fillcolor="#e5e7eb"];
a [label="critical heart patient\\npriority 1: treat NEXT", fillcolor="#fef3c7", color="{ORANGE}", penwidth=2.5];
b [label="broken arm patient\\npriority 3: wait", fillcolor="#dbeafe"];
d -> a; d -> b;
}}"""
    save_dot(src, 'ds-heap-triage.svg', 'ER triage desk: the critical heart patient with priority 1 is treated next; '
             'the broken arm patient with priority 3 waits, whatever order they arrived in', OUT)


def heap_array():
    a = [1, 3, 5, 8, 9, 7]
    assert is_min_heap(a)
    s = Svg(470, 220, 'Min-heap 1, 3, 5, 8, 9, 7 as a tree and as an array. 1 at index 0 is the root; 3 and 5 at '
                      'indexes 1 and 2 are level 1; 8, 9 and 7 at indexes 3 to 5 are level 2. Parent of index i is '
                      '(i − 1) // 2, children are 2i + 1 and 2i + 2')
    tree_and_array(s, a, 20, 40, 230, 60, cellw=36, dx=46)
    groups = [(0, 1, 'root'), (1, 3, 'level 1'), (3, 6, 'level 2')]
    for lo, hi, lab in groups:
        x0, x1 = 230 + lo * 36, 230 + hi * 36
        s.path(f'M{x0 + 3},{116} L{x0 + 3},{122} L{x1 - 3},{122} L{x1 - 3},{116}', INK, 1.2)
        s.text((x0 + x1) / 2, 138, lab, 11, INK, 'middle', 'bold')
    s.text(230, 170, 'index 1 (3): children at 3 and 4 → 8, 9', 12, INK, 'start')
    s.text(230, 190, 'index 5 (7): parent at (5 − 1) // 2 = 2 → 5', 12, INK, 'start')
    s.save('ds-heap-array.svg', OUT)


def heap_push_steps():
    start = [2, 4, 3, 7, 9, 8]
    assert is_min_heap(start)
    end, frames = heap_push_frames(start, 1)
    assert end == [1, 4, 2, 7, 9, 8, 3] and is_min_heap(end) and len(frames) == 3
    heap_frames_picture(frames, 'ds-heap-push-steps.svg',
                        'Pushing 1 onto the min-heap 2, 4, 3, 7, 9, 8. 1 is appended at index 6 under 3; 1 < 3 so they '
                        'swap; 1 < 2 so they swap again, and 1 is the root. The array ends as 1, 4, 2, 7, 9, 8, 3')


def heap_pop_steps():
    start = [1, 3, 2, 6, 4, 5, 9, 8]
    assert is_min_heap(start)
    top, end, frames = heap_pop_frames(start)
    assert top == 1 and end == [2, 3, 5, 6, 4, 8, 9] and is_min_heap(end) and len(frames) == 3
    heap_frames_picture(frames, 'ds-heap-pop-steps.svg',
                        'Popping the min-heap 1, 3, 2, 6, 4, 5, 9, 8. 1 is taken and the last item 8 moves to the root; '
                        '8 swaps with its smaller child 2; then with its smaller child 5. The array ends as 2, 3, 5, 6, '
                        '4, 8, 9')


def heap_heapify_steps():
    a = [9, 2, 7, 4, 1]
    frames = [('start: [9, 2, 7, 4, 1] is not a heap', list(a), (), ())]
    for i in range(len(a) // 2 - 1, -1, -1):
        frames.append((f'sift down index {i} (value {a[i]})', list(a), (i,), ()))
        sift_down(a, i, frames)
    assert a == [1, 2, 7, 4, 9] and is_min_heap(a)
    labels = [f[0] for f in frames]
    assert len(frames) == 6, labels
    # keep: start, each sift-down's swaps (the "sift down index" frames only announce the next step)
    keep = [frames[0]] + [f for f in frames[1:] if 'swap' in f[0]]
    keep = [(lab, arr, hl, h2) for lab, arr, hl, h2 in keep]
    keep[-1] = (keep[-1][0] + '; done', ) + keep[-1][1:]
    heap_frames_picture(keep, 'ds-heap-heapify-steps.svg',
                        'Heapify on 9, 2, 7, 4, 1, working backwards from index 1. Index 1 (2) swaps with its smaller '
                        'child 1. Index 0 (9) swaps with its smaller child 1, then with its smaller child 2. The result '
                        'is the min-heap 1, 2, 7, 4, 9')


def heap_sketch_answer():
    a = []
    for v in (8, 3, 6, 1, 5):
        a, _ = heap_push_frames(a, v)
    assert a == [1, 3, 6, 8, 5] and is_min_heap(a)
    s = Svg(420, 200, 'Answer: after pushing 8, 3, 6, 1, 5 the min-heap array is 1, 3, 6, 8, 5. As a tree, 1 is the '
                      'root, 3 and 6 are its children, and 8 and 5 are the children of 3')
    tree_and_array(s, a, 20, 40, 210, 70, cellw=38, dx=46)
    s.save('ds-heap-sketch-answer.svg', OUT)


def heaps():
    heap_triage()
    heap_array()
    heap_push_steps()
    heap_pop_steps()
    heap_heapify_steps()
    heap_sketch_answer()


# ======================================================================
# dsa/02-data-structures/08-tries.md
# ======================================================================

class TrieNode:
    def __init__(self):
        self.children, self.is_end = {}, False


class Trie:
    """The lesson's trie."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        cur, made = self.root, []
        for k, ch in enumerate(word):
            if ch not in cur.children:
                cur.children[ch] = TrieNode()
                made.append(word[:k + 1])
            cur = cur.children[ch]
        cur.is_end = True
        return made

    def walk(self, text):
        cur = self.root
        for ch in text:
            if ch not in cur.children:
                return None
            cur = cur.children[ch]
        return cur

    def prefixes(self):
        """Every node as its prefix string ('' is the root), with its children's prefixes in letter order."""
        out = {}

        def rec(node, pre):
            out[pre] = ([pre + c for c in sorted(node.children)], node.is_end)
            for c in sorted(node.children):
                rec(node.children[c], pre + c)
        rec(self.root, '')
        return out


def draw_trie(s, trie, ox, oy, new=(), path=(), dx=40, dy=48, r=14):
    info = trie.prefixes()
    children = {p: kids for p, (kids, _) in info.items()}
    pos, depth = tree_layout(children, '', dx, dy)
    for p, kids in children.items():
        for c in kids:
            (x1, y1), (x2, y2) = pos[p], pos[c]
            on = c in path
            s.line(ox + x1, oy + y1, ox + x2, oy + y2, ORANGE if on else INK, 3 if on else 1.3)
    for p, (x, y) in pos.items():
        end = info[p][1]
        if p == '':
            s.rect(ox + x - 22, oy + y - 12, 44, 24, '#e5e7eb', INK, 1.2)
            s.text(ox + x, oy + y + 4, 'root', 11, INK, 'middle', 'bold')
            continue
        on = p in new
        fill = NEWF if on else (DONE if end else SOFT)
        st = ORANGE if on else (ACCENT if end else INK)
        s.add(f'<circle cx="{ox + x:.1f}" cy="{oy + y:.1f}" r="{r}" fill="{fill}" stroke="{st}" '
              f'stroke-width="{3 if on or end else 1.3}"/>')
        if end:
            s.add(f'<circle cx="{ox + x:.1f}" cy="{oy + y:.1f}" r="{r - 4}" fill="none" stroke="{ACCENT}" '
                  f'stroke-width="1"/>')
        s.text(ox + x, oy + y + 5, p[-1], 13, INK, 'middle', 'bold')
    return pos


def trie_extent(trie, dx=40, dy=48):
    info = trie.prefixes()
    pos, depth = tree_layout({p: k for p, (k, _) in info.items()}, '', dx, dy)
    return max(x for x, _ in pos.values()), max(y for _, y in pos.values())


LESSON_WORDS = ['app', 'apple', 'apt', 'cat']


def trie_autocomplete():
    words = ['apple', 'application']
    assert all(w.startswith('app') for w in words)
    src = f"""digraph {{ bgcolor="white"; pad=0.25; rankdir=LR; nodesep=0.25; ranksep=0.35;
node [fontname="{FONT}", fontsize=13, shape=circle, style=filled, fillcolor="{SOFT}", color="{INK}", width=0.42,
      fixedsize=true];
edge [color="{INK}", arrowhead=none, penwidth=1.3];
q [label="types\\n\\"app\\"", shape=box, style="rounded,filled", fillcolor="#e5e7eb", fixedsize=false];
r [label="root", shape=box, style="rounded,filled", fillcolor="#e5e7eb", fixedsize=false];
a [label="a", color="{ORANGE}", penwidth=2.5, fillcolor="{NEWF}"];
p1 [label="p", color="{ORANGE}", penwidth=2.5, fillcolor="{NEWF}"];
p2 [label="p", color="{ORANGE}", penwidth=2.5, fillcolor="{NEWF}"];
w1 [label="apple", shape=box, style="rounded,filled", fillcolor="{DONE}", fixedsize=false];
w2 [label="application", shape=box, style="rounded,filled", fillcolor="{DONE}", fixedsize=false];
q -> r [arrowhead=normal, style=dashed];
r -> a [color="{ORANGE}", penwidth=3]; a -> p1 [color="{ORANGE}", penwidth=3]; p1 -> p2 [color="{ORANGE}", penwidth=3];
p2 -> w1 [style=dashed, label=" l, e", fontname="{FONT}", fontsize=11];
p2 -> w2 [style=dashed, label=" l, i, c, ...", fontname="{FONT}", fontsize=11];
}}"""
    src = src.replace('\\"app\\"', "'app'")
    save_dot(src, 'ds-trie-autocomplete.svg', 'Autocomplete with a trie: typing app walks root, a, p, p; every word '
             'below that node, such as apple and application, starts with app', OUT)


def trie_anatomy():
    tr = Trie()
    for w in LESSON_WORDS:
        tr.insert(w)
    info = tr.prefixes()
    assert len(info) == 10 and [p for p, (_, e) in info.items() if e] == ['app', 'apple', 'apt', 'cat']
    assert tr.walk('ap') is not None and not tr.walk('ap').is_end
    w, h = trie_extent(tr, 78, 48)
    s = Svg(w + 180, h + 64, 'A trie holding app, apple, apt and cat. From the root, a then p is shared by app, apple '
                             'and apt. The nodes where app, apple, apt and cat end are marked green with a double ring')
    pos = draw_trie(s, tr, 90, 24, dx=78)
    for wd in LESSON_WORDS:
        x, y = pos[wd]
        if info[wd][0]:          # a word that continues (app -> apple): label on the left
            s.text(90 + x - 20, 24 + y + 4, f'"{wd}" ends', 11, ACCENT, 'end', 'bold')
        else:
            s.text(90 + x, 24 + y + 30, f'"{wd}"', 11, ACCENT, 'middle', 'bold')
    s.text(w + 170, h + 56, 'green double ring = is_end', 11, ACCENT, 'end')
    s.save('ds-trie-anatomy.svg', OUT)


def trie_build_steps():
    tr = Trie()
    made_all = []
    pw, ph = 230, 300
    s = Svg(pw * 4 + 10, ph, 'The trie built word by word. Insert app creates a, p, p. Insert apple adds l and e under '
                             'app. Insert apt adds only t under ap, because a and p already exist. Insert cat adds a new '
                             'branch c, a, t. New nodes are outlined orange; green double rings mark word ends')
    for i, wd in enumerate(LESSON_WORDS):
        made = tr.insert(wd)
        made_all.append(made)
        x0 = 10 + i * pw
        s.rect(x0, 8, pw - 10, ph - 16, '#f9fafb', '#e5e7eb', 1)
        s.text(x0 + 10, 28, f'{i + 1}. insert "{wd}"', 12, INK, 'start', 'bold')
        s.text(x0 + 10, 44, f'new nodes: {len(made)}', 11, ORANGE, 'start', 'bold')
        w, _ = trie_extent(tr, 34, 42)
        draw_trie(s, tr, x0 + (pw - 10 - w) / 2, 70, new=made, path=[wd[:k + 1] for k in range(len(wd))], dx=34, dy=42,
                  r=13)
    assert [len(m) for m in made_all] == [3, 2, 1, 3]
    s.save('ds-trie-build-steps.svg', OUT)


def trie_sketch_answer():
    tr = Trie()
    for wd in ['bat', 'bad', 'ban', 'be', 'bee']:
        tr.insert(wd)
    info = tr.prefixes()
    assert len(info) == 8 and sorted(p for p, (_, e) in info.items() if e) == ['bad', 'ban', 'bat', 'be', 'bee']
    w, h = trie_extent(tr)
    s = Svg(w + 120, h + 50, 'Answer: a trie for bat, bad, ban, be, bee. Root, then b. Under b: a and e. Under ba: d, '
                             'n, t, all word ends. be is a word end, and e under it (bee) is a word end too. 8 nodes '
                             'counting the root')
    draw_trie(s, tr, 60, 24)
    s.save('ds-trie-sketch-answer.svg', OUT)


def tries():
    trie_autocomplete()
    trie_anatomy()
    trie_build_steps()
    trie_sketch_answer()


# ======================================================================
# dsa/02-data-structures/10-union-find.md
# ======================================================================

class UnionFind:
    """The lesson lab's union-find: full path compression and union by rank, each switchable."""

    def __init__(self, n, compress=True, by_rank=True):
        self.parent, self.rank = list(range(n)), [0] * n
        self.compress, self.by_rank = compress, by_rank

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        if self.compress:
            while self.parent[x] != root:
                self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.by_rank:
            if self.rank[ra] < self.rank[rb]:
                ra, rb = rb, ra
            self.parent[rb] = ra
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
        else:
            self.parent[rb] = ra
        return True


def plain_union(parent, x, y):
    """Worked-problem rule: no optimisations, parent[root of y] = root of x."""
    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v
    rx, ry = root(x), root(y)
    if rx != ry:
        parent[ry] = rx
    return rx != ry


def draw_forest(s, mk, parent, ox, oy, names=None, hl=(), moved=(), dx=46, dy=56, r=16, size=13, gap=26):
    """Draw a parent array as a forest. Arrows point from each element up to its parent; roots have a thick ring.
    hl: nodes outlined orange; moved: nodes whose parent pointer just changed (orange arrow)."""
    names = names or {}
    n = len(parent)
    children = {i: [] for i in range(n)}
    for i in range(n):
        if parent[i] != i:
            children[parent[i]].append(i)
    roots = [i for i in range(n) if parent[i] == i]
    x = ox
    pos = {}
    for rt in roots:
        p, _ = tree_layout({k: v for k, v in children.items() if v}, rt, dx, dy)
        minx = min(px for px, _ in p.values())
        maxx = max(px for px, _ in p.values())
        for k, (px, py) in p.items():
            pos[k] = (x + px - minx, oy + py)
        x += maxx - minx + dx + gap - dx / 2
    for i in range(n):
        if parent[i] != i:
            (x1, y1), (x2, y2) = pos[i], pos[parent[i]]
            d = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            ux, uy = (x2 - x1) / d, (y2 - y1) / d
            col = ORANGE if i in moved else INK
            arrow(s, mk, x1 + ux * r, y1 + uy * r, x2 - ux * (r + 2), y2 - uy * (r + 2), col, 2.6 if i in moved else 1.5)
    for i, (px, py) in pos.items():
        on = i in hl
        root = parent[i] == i
        s.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{NEWF if on else (DONE if root else SOFT)}" '
              f'stroke="{ORANGE if on else INK}" stroke-width="{3 if on else (2.2 if root else 1.3)}"/>')
        s.text(px, py + 5, names.get(i, i), size, INK, 'middle', 'bold')
    return pos, x


def uf_friends():
    names = {0: 'Alice', 1: 'Bob', 2: 'Charlie', 3: 'David'}
    uf = UnionFind(4)
    frames = [('start: 4 separate people', list(uf.parent), ())]
    uf.union(0, 1)
    frames.append(('union(Alice, Bob)', list(uf.parent), (1,)))
    uf.union(1, 2)
    frames.append(('union(Bob, Charlie)', list(uf.parent), (2,)))
    assert uf.parent == [0, 0, 0, 3] and uf.find(0) == uf.find(2) and uf.find(3) != uf.find(0)
    s = Svg(470, 3 * 135 + 40, 'Friend groups as a union-find forest. At the start Alice, Bob, Charlie and David each '
                               'stand alone. After union(Alice, Bob), Bob points to Alice. After union(Bob, Charlie), '
                               'Charlie also points to Alice, so Alice, Bob and Charlie share the root Alice; David is '
                               'still alone')
    mk = arrow_defs(s)
    for k, (label, par, moved) in enumerate(frames):
        y = 14 + k * 135
        s.text(16, y + 14, label, 13, INK, 'start', 'bold')
        draw_forest(s, mk, par, 50, y + 46, names={i: n[0] for i, n in names.items()}, moved=moved, dx=60, gap=60)
    s.text(454, 3 * 135 + 26, 'A = Alice, B = Bob, C = Charlie, D = David; arrows point to the parent; green = root',
           10, '#6b7280', 'end')
    s.save('ds-uf-friends.svg', OUT)


def uf_optimisations():
    naive = UnionFind(5, compress=False, by_rank=False)
    both = UnionFind(5)
    for i in range(4):
        naive.union(i + 1, i)      # the lab's degenerate order
        both.union(i + 1, i)
    assert naive.parent == [1, 2, 3, 4, 4]
    assert both.parent == [1, 1, 1, 1, 1]
    s = Svg(470, 345, 'The same unions, union(1, 0), union(2, 1), union(3, 2), union(4, 3), done two ways. With no '
                      'optimisations the forest is a chain 0, 1, 2, 3 up to root 4, so find(0) takes 4 steps. With union '
                      'by rank and path compression every element points straight at root 1, so any find takes 1 step')
    mk = arrow_defs(s)
    s.text(20, 22, 'no optimisations: a chain', 13, INK, 'start', 'bold')
    s.text(20, 40, 'find(0) walks 4 pointers', 12, TRUE, 'start')
    draw_forest(s, mk, naive.parent, 90, 70, dy=58)
    s.text(250, 22, 'rank + path compression', 13, INK, 'start', 'bold')
    s.text(250, 40, 'every find is 1 step', 12, ACCENT, 'start')
    draw_forest(s, mk, both.parent, 270, 110, dx=44)
    s.text(235, 335, 'same unions: union(1,0), union(2,1), union(3,2), union(4,3)', 11, '#6b7280')
    s.save('ds-uf-optimisations.svg', OUT)


def uf_path_compression():
    parent = [1, 3, 3, 4, 5, 5]
    before = list(parent)
    uf = UnionFind(6)
    uf.parent = list(parent)
    root = uf.find(0)
    after = uf.parent
    assert root == 5 and after == [5, 5, 3, 5, 5, 5]
    changed = tuple(i for i in range(6) if before[i] != after[i])
    assert changed == (0, 1, 3)
    s = Svg(470, 290, 'Path compression during find(0). Before, 0 points to 1, 1 to 3, 3 to 4 and 4 to root 5, and 2 '
                      'hangs under 3; find(0) walks 4 pointers. After, 0, 1 and 3 point straight at 5. 2 was not on the '
                      'path, so it still points to 3')
    mk = arrow_defs(s)
    s.text(20, 22, 'before find(0)', 13, INK, 'start', 'bold')
    draw_forest(s, mk, before, 60, 54, hl=(0,), dx=44, dy=52)
    s.text(250, 22, 'after find(0)', 13, INK, 'start', 'bold')
    draw_forest(s, mk, after, 290, 54, moved=changed, dx=44, dy=60)
    s.text(250, 250, 'orange arrows: pointers rewritten', 11, ORANGE, 'start', 'bold')
    s.text(250, 266, 'to point straight at the root 5', 11, ORANGE, 'start', 'bold')
    s.save('ds-uf-path-compression.svg', OUT)


def uf_union_steps():
    uf = UnionFind(6)
    ops = [(0, 1), (2, 3), (4, 5), (1, 3), (5, 3)]
    frames = [('start: 6 groups', list(uf.parent), (), ())]
    for a, b in ops:
        before = list(uf.parent)
        uf.union(a, b)
        moved = tuple(i for i in range(6) if before[i] != uf.parent[i])
        frames.append((f'union({a}, {b})', list(uf.parent), moved, ()))
    assert uf.parent == [0, 0, 0, 0, 0, 4]
    assert frames[4][1] == [0, 0, 0, 2, 4, 4] and frames[5][2] == (3, 4)
    def levels(par):
        def d(i):
            return 0 if par[i] == i else 1 + d(par[i])
        return max(d(i) for i in range(len(par))) + 1
    heights = [max(66, 46 + (levels(f[1]) - 1) * 40 + 10) for f in frames]
    W = 500
    s = Svg(W, 10 + sum(heights) + 6 * len(frames), 'Union-find with union by rank and path compression on elements 0 to 5. union(0, 1): 1 '
                            'points to 0. union(2, 3): 3 points to 2. union(4, 5): 5 points to 4. union(1, 3): root 2 '
                            'joins root 0. union(5, 3): find(3) compresses so 3 points straight at 0, and root 4 joins '
                            'root 0, leaving one group with root 0 and 5 under 4')
    mk = arrow_defs(s)
    notes = {4: ('roots 0 and 2 have equal rank,', 'so 2 goes under 0'),
             5: ('find(3) compresses 3 onto 0,', 'then 4 (lower rank) goes under 0')}
    y = 10
    for k, (label, par, moved, _) in enumerate(frames):
        s.rect(6, y, W - 12, heights[k], '#f9fafb', '#e5e7eb', 1)
        s.text(16, y + 22, label, 12, INK, 'start', 'bold')
        if k in notes:
            s.text(16, y + 42, notes[k][0], 10, ORANGE, 'start', 'bold')
            s.text(16, y + 56, notes[k][1], 10, ORANGE, 'start', 'bold')
        draw_forest(s, mk, par, 250, y + 26, moved=moved, dx=38, dy=40, r=13, size=12, gap=24)
        y += heights[k] + 6
    s.save('ds-uf-union-steps.svg', OUT)


def uf_sketch_answer():
    parent = list(range(7))
    for x, y in [(3, 4), (5, 6), (3, 5), (0, 1), (6, 1)]:
        plain_union(parent, x, y)
    assert parent == [3, 0, 2, 3, 3, 3, 5]
    s = Svg(330, 220, 'Answer: parent array 3, 0, 2, 3, 3, 3, 5. Root 3 has children 0, 4 and 5; 1 hangs under 0; 6 '
                      'hangs under 5; 2 is alone as its own root')
    mk = arrow_defs(s)
    draw_forest(s, mk, parent, 40, 40, dx=50, dy=64)
    s.text(16, 206, 'parent = [3, 0, 2, 3, 3, 3, 5]', 12, INK, 'start', 'bold')
    s.save('ds-uf-sketch-answer.svg', OUT)


def union_find():
    uf_friends()
    uf_optimisations()
    uf_path_compression()
    uf_union_steps()
    uf_sketch_answer()


LESSONS = [union_find, tries, heaps, level_order, dfs, bsts, binary_trees, trees, stacks_queues, linked_lists, hash_maps, dynamic_arrays, loops_grids, loops_halving, arrays]

if __name__ == '__main__':
    for fn in LESSONS:
        fn()
