"""Draw the adversarial-search diagrams (artificial-intelligence/04-adversarial-search) and assert every number.

    python3 scripts/diagrams/ai_games.py      # run from the vault root

Game trees are nested lists with numbers at the leaves; the root is a MAX node and the
levels alternate MAX, MIN, MAX, ... Minimax and alpha-beta (left to right) run on the
SSG 518 class-notes tree (10/03/26), the classic 3 x 3 alpha-beta example, and the quiz
trees, and every backed-up value, pruned leaf and count the lessons quote is asserted.
Also counts tic-tac-toe games by brute force and checks the evaluation-function example.
Output: artificial-intelligence/images/gm-*.svg.
"""
import itertools
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, ACCENT, Svg  # noqa: E402
from artificial_intelligence import OUT, ORANGE  # noqa: E402

GREY = '#9ca3af'
MAXC = '#dbeafe'
MINC = '#fde68a'
INF = float('inf')

NOTES_TREE = [[[10, 9], [14, 18]], [[5, 4], [50, 30]]]
CLASSIC = [[3, 12, 8], [2, 4, 6], [14, 5, 2]]
CLASSIC_ORDERED = [[3, 12, 8], [2, 4, 6], [2, 5, 14]]


def minimax(node, is_max=True):
    if not isinstance(node, list):
        return node
    vals = [minimax(c, not is_max) for c in node]
    return max(vals) if is_max else min(vals)


def backed_up(node, is_max=True, path=(), out=None):
    """Value of every node, keyed by path."""
    out = {} if out is None else out
    if not isinstance(node, list):
        out[path] = node
        return node, out
    vals = [backed_up(c, not is_max, path + (i,), out)[0] for i, c in enumerate(node)]
    out[path] = max(vals) if is_max else min(vals)
    return out[path], out


def alphabeta(node, is_max=True, alpha=-INF, beta=INF, path=(), log=None):
    """Returns value; log collects ('leaf', path, value), ('prune', path) and ('node', path, alpha, beta, value)."""
    log = [] if log is None else log
    if not isinstance(node, list):
        log.append(('leaf', path, node))
        return node, log
    v = -INF if is_max else INF
    for i, child in enumerate(node):
        cv, _ = alphabeta(child, not is_max, alpha, beta, path + (i,), log)
        if is_max:
            v = max(v, cv)
            alpha = max(alpha, v)
        else:
            v = min(v, cv)
            beta = min(beta, v)
        if alpha >= beta:
            for j in range(i + 1, len(node)):
                log.append(('prune', path + (j,)))
            break
    log.append(('node', path, alpha, beta, v))
    return v, log


def leaves_seen(log):
    return [e[2] for e in log if e[0] == 'leaf']


def pruned(log):
    return [e[1] for e in log if e[0] == 'prune']


def count_leaves(node):
    return 1 if not isinstance(node, list) else sum(count_leaves(c) for c in node)


# ---------- tic-tac-toe ----------

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(b):
    for a, c, d in LINES:
        if b[a] != '.' and b[a] == b[c] == b[d]:
            return b[a]
    return None


def count_games(b='.' * 9, player='X'):
    if winner(b) or '.' not in b:
        return 1
    tot = 0
    for i, c in enumerate(b):
        if c == '.':
            tot += count_games(b[:i] + player + b[i + 1:], 'O' if player == 'X' else 'X')
    return tot


def open_lines(b, p):
    other = 'O' if p == 'X' else 'X'
    return sum(1 for line in LINES if all(b[i] != other for i in line))


def ttt_eval(b):
    return open_lines(b, 'X') - open_lines(b, 'O')


def ttt_value(b, player):
    """Exact minimax value for X: +1 win, 0 draw, -1 loss."""
    w = winner(b)
    if w:
        return 1 if w == 'X' else -1
    if '.' not in b:
        return 0
    vals = [ttt_value(b[:i] + player + b[i + 1:], 'O' if player == 'X' else 'X') for i, c in enumerate(b) if c == '.']
    return max(vals) if player == 'X' else min(vals)


# ---------- assertions ----------

def check():
    # Lesson 01: tic-tac-toe size, chess estimate.
    assert math.factorial(9) == 362_880
    assert count_games() == 255_168
    assert round(100 * math.log10(35)) == 154
    assert ttt_value('.' * 9, 'X') == 0
    # Lesson 02: the notes' tree.
    v, vals = backed_up(NOTES_TREE)
    assert v == 10
    assert [vals[(0, 0)], vals[(0, 1)], vals[(1, 0)], vals[(1, 1)]] == [10, 18, 5, 50]
    assert [vals[(0,)], vals[(1,)]] == [10, 5]
    # Lesson 02 quiz tree: 2-ply.
    assert minimax([[4, 7], [2, 9], [6, 5]]) == 5
    # Lesson 03: evaluation function example and the depth-2 quiz.
    b = 'O...X....'
    assert open_lines(b, 'X') == 5 and open_lines(b, 'O') == 4 and ttt_eval(b) == 1
    assert open_lines('X...O....', 'X') == 4 and open_lines('X...O....', 'O') == 5
    b2 = '....X....'
    assert open_lines(b2, 'X') == 8 and open_lines(b2, 'O') == 4 and ttt_eval(b2) == 4
    b3 = 'X.......O'
    assert ttt_eval(b3) == 0
    assert minimax([[[3, 1], [8, 2]], [[7, 6], [0, 4]]]) == 4
    # Lesson 04: alpha-beta on the notes' tree.
    v, log = alphabeta(NOTES_TREE)
    assert v == 10
    assert leaves_seen(log) == [10, 9, 14, 5, 4]
    assert pruned(log) == [(0, 1, 1), (1, 1)]
    # Lesson 05: the classic example, natural and best ordering.
    v, log = alphabeta(CLASSIC)
    assert v == 3 and leaves_seen(log) == [3, 12, 8, 2, 14, 5, 2]
    assert pruned(log) == [(1, 1), (1, 2)]
    v, log = alphabeta(CLASSIC_ORDERED)
    assert v == 3 and leaves_seen(log) == [3, 12, 8, 2, 2] and len(leaves_seen(log)) == 5
    assert minimax(CLASSIC) == minimax(CLASSIC_ORDERED) == 3
    # Quiz trees for the alpha-beta lessons.
    qa = [[6, 8], [3, 9]]
    v, log = alphabeta(qa)
    assert v == 6 and pruned(log) == [(1, 1)]
    qb = [[5, 2, 7], [1, 8, 3], [6, 4, 9]]
    v, log = alphabeta(qb)
    assert v == 4 and leaves_seen(log) == [5, 2, 7, 1, 6, 4, 9] and len(leaves_seen(log)) == 7
    assert minimax([[[3, 7], [8, 1]], [[2, 6], [4, 5]]]) == 7          # minimax-1 quiz
    # Complexity numbers.
    assert 35 ** 4 == 1_500_625 and 35 ** 8 == 2_251_875_390_625


# ---------- drawing ----------

def layout(tree):
    pos, leaves = {}, [0]

    def place(node, path, depth):
        if not isinstance(node, list):
            pos[path] = (leaves[0], depth)
            leaves[0] += 1
            return
        for i, c in enumerate(node):
            place(c, path + (i,), depth + 1)
        xs = [pos[path + (i,)][0] for i in range(len(node))]
        pos[path] = (sum(xs) / len(xs), depth)
    place(tree, (), 0)
    return pos, leaves[0]


def node_at(tree, path):
    for i in path:
        tree = tree[i]
    return tree


def draw_game_tree(tree, name, title, values=None, pruned_paths=(), show_leaves=True, ab=None, xgap=64, ygap=86):
    pos, nleaves = layout(tree)
    depth = max(d for _, d in pos.values())
    w = 120 + (nleaves - 1) * xgap + 90
    h = 50 + depth * ygap + 60
    s = Svg(w, h, title)
    xy = {p: (90 + x * xgap, 40 + d * ygap) for p, (x, d) in pos.items()}

    def is_pruned(p):
        return any(p[:len(q)] == q for q in pruned_paths)
    for p in xy:
        if p:
            par = p[:-1]
            s.line(*xy[par], *xy[p], color=GREY if is_pruned(p) else INK, width=1.5, dash='5 4' if is_pruned(p) else None)
    # level labels
    for d in range(depth):
        s.text(30, 40 + d * ygap + 5, 'MAX' if d % 2 == 0 else 'MIN', size=12, weight='bold',
               color='#1d4ed8' if d % 2 == 0 else '#b45309')
    for p, (x, y) in xy.items():
        node = node_at(tree, p)
        grey = is_pruned(p)
        if isinstance(node, list):
            is_max = len(p) % 2 == 0
            r = 20
            pts = (f'{x},{y - r} {x - r},{y + r * 0.8} {x + r},{y + r * 0.8}' if is_max
                   else f'{x - r},{y - r * 0.8} {x + r},{y - r * 0.8} {x},{y + r}')
            fill = '#f3f4f6' if grey else (MAXC if is_max else MINC)
            s.add(f'<polygon points="{pts}" fill="{fill}" stroke="{GREY if grey else INK}" stroke-width="1.2"/>')
            if values and p in values and not grey:
                s.text(x, y + (7 if is_max else 2), values[p], size=13, weight='bold')
            if ab and p in ab:
                s.text(x + 24, y - 14, ab[p], size=11, color='#374151', anchor='start')
        else:
            fill = '#f3f4f6' if grey else '#ffffff'
            s.rect(x - 16, y - 14, 32, 28, fill, stroke=GREY if grey else INK, width=1.2)
            if show_leaves:
                s.text(x, y + 5, node, size=13, color=GREY if grey else INK, weight='bold')
    s.save(name, OUT)


def draw_board(name, title, board, notes=None):
    s = Svg(260, 230, title)
    x0, y0, c = 40, 20, 60
    for i in range(1, 3):
        s.line(x0 + i * c, y0, x0 + i * c, y0 + 3 * c, width=3)
        s.line(x0, y0 + i * c, x0 + 3 * c, y0 + i * c, width=3)
    for i, ch in enumerate(board):
        r, k = divmod(i, 3)
        if ch != '.':
            s.text(x0 + k * c + c / 2, y0 + r * c + c / 2 + 14, ch, size=40, weight='bold',
                   color='#1d4ed8' if ch == 'X' else '#b45309')
    if notes:
        s.text(130, 222, notes, size=12, color='#374151')
    s.save(name, OUT)


if __name__ == '__main__':
    check()
    _, vals = backed_up(NOTES_TREE)
    draw_game_tree(NOTES_TREE, 'gm-notes-tree.svg',
                   'The game tree from the class notes: a MAX root, two MIN nodes, four MAX nodes, and leaves 10, 9, 14, 18, 5, 4, 50, 30 '
                   'from left to right, with the inner values still blank')
    draw_game_tree(NOTES_TREE, 'gm-notes-minimax.svg',
                   'The same tree with minimax values backed up: the MAX nodes take 10, 18, 5 and 50, the MIN nodes take 10 and 5, '
                   'and the root takes 10', values=vals)
    v, log = alphabeta(NOTES_TREE)
    abvals = {e[1]: e[4] for e in log if e[0] == 'node'}
    draw_game_tree(NOTES_TREE, 'gm-notes-alphabeta.svg',
                   'Alpha-beta on the class-notes tree: the leaf 18 and the whole right-hand MAX node with leaves 50 and 30 are '
                   'pruned and greyed out; the root value is still 10', values=abvals, pruned_paths=pruned(log))
    draw_game_tree(CLASSIC, 'gm-classic.svg',
                   'A two-level game tree: a MAX root with three MIN children, whose leaves are 3, 12, 8; 2, 4, 6; and 14, 5, 2',
                   xgap=56)
    v, log = alphabeta(CLASSIC)
    abvals = {e[1]: e[4] for e in log if e[0] == 'node'}
    draw_game_tree(CLASSIC, 'gm-classic-alphabeta.svg',
                   'Alpha-beta on that tree: the MIN nodes take 3, 2 and 2, the root takes 3, and the leaves 4 and 6 under the '
                   'middle MIN node are pruned', values=abvals, pruned_paths=pruned(log), xgap=56)
    v, log = alphabeta(CLASSIC_ORDERED)
    abvals = {e[1]: e[4] for e in log if e[0] == 'node'}
    draw_game_tree(CLASSIC_ORDERED, 'gm-classic-ordered.svg',
                   'The same tree with the third MIN node\'s leaves reordered to 2, 5, 14: now 4, 6, 5 and 14 are all pruned, '
                   'and only five leaves are examined', values=abvals, pruned_paths=pruned(log), xgap=56)
    draw_board('gm-ttt-eval.svg', 'A tic-tac-toe board with O in the top-left corner and X in the centre; X has 5 open lines, '
               'O has 4, so the evaluation is 5 minus 4, which is 1', 'O...X....', 'X: 5 open lines, O: 4, Eval = 1')
