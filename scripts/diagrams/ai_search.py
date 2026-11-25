"""Draw the uninformed-search diagrams (artificial-intelligence/02-uninformed-search) and assert every trace.

    python3 scripts/diagrams/ai_search.py      # run from the vault root

Each search method the lessons teach is implemented here and run on the lessons' own
examples: the Lagos-to-Abuja map from artificial_intelligence.py, the two small trees
from the SSG 518 class notes, and the notes' uniform-cost graph (A, B, C, D, G).
Conventions used everywhere (and stated in the lessons): children are generated in
alphabetical order; BFS tests for the goal when a node is generated; UCS tests when a
node is taken off the frontier. Output: artificial-intelligence/images/se-*.svg.
"""
import heapq
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, ACCENT, Svg  # noqa: E402
from artificial_intelligence import ROADS, OUT, ORANGE, NODE_FILL, START_FILL, GOAL_FILL, route_map, cost  # noqa: E402

GREY = '#9ca3af'
LIGHT = '#f3f4f6'


def graph_from(edges):
    g = {}
    for (a, b), d in edges.items():
        g.setdefault(a, {})[b] = d
        g.setdefault(b, {})[a] = d
    return {k: dict(sorted(v.items())) for k, v in g.items()}


MAP = graph_from(ROADS)
# The uniform-cost graph from the class notes (24/11/25).
UCS_G = graph_from({('A', 'B'): 2, ('A', 'C'): 5, ('B', 'C'): 1, ('B', 'D'): 1, ('C', 'D'): 3, ('D', 'G'): 2})
# The class-notes trees: a 7-node tree (BFS and DFS pages) and a 15-node tree (IDS page).
TREE7 = {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': ['F', 'G']}
TREE15 = {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': ['F', 'G'], 'D': ['H', 'I'], 'E': ['J', 'K'],
          'F': ['L', 'M'], 'G': ['N', 'O']}


# ---------- the algorithms ----------

def bfs(g, start, goal):
    """Graph-search BFS with the goal test on generation. Returns path and a trace of (expanded, frontier)."""
    if start == goal:
        return [start], []
    frontier, parent, trace = deque([start]), {start: None}, []
    while frontier:
        node = frontier.popleft()
        for child in g[node]:
            if child not in parent:
                parent[child] = node
                if child == goal:
                    trace.append((node, list(frontier) + [child]))
                    return walk(parent, child), trace
                frontier.append(child)
        trace.append((node, list(frontier)))
    return None, trace


def dfs(g, start, goal):
    """Recursive DFS that never revisits a city. Returns path and visit order."""
    order, seen = [], set()

    def go(node, path):
        order.append(node)
        seen.add(node)
        if node == goal:
            return path
        for child in g[node]:
            if child not in seen:
                r = go(child, path + [child])
                if r:
                    return r
        return None
    return go(start, [start]), order


def dls(g, start, goal, limit):
    """Depth-limited DFS that skips cities already on the current path. Returns (path or 'cutoff' or 'failure', order)."""
    order = []

    def go(path, depth):
        node = path[-1]
        order.append(node)
        if node == goal:
            return path
        if depth == limit:
            return 'cutoff'
        cut = False
        for child in g.get(node, []):
            if child in path:
                continue
            r = go(path + [child], depth + 1)
            if r == 'cutoff':
                cut = True
            elif r:
                return r
        return 'cutoff' if cut else 'failure'
    return go([start], 0), order


def ids(g, start, goal, max_limit=20):
    rounds = []
    for limit in range(max_limit + 1):
        r, order = dls(g, start, goal, limit)
        rounds.append((limit, order, r))
        if r not in ('cutoff', 'failure'):
            return r, rounds
        if r == 'failure':
            return None, rounds
    return None, rounds


def ucs(g, start, goal):
    """Uniform-cost search with goal test on expansion. Returns path, cost and a trace of (popped, g, frontier)."""
    best, parent, done, trace = {start: 0}, {start: None}, set(), []
    heap = [(0, start)]
    while heap:
        c, node = heapq.heappop(heap)
        if node in done or c > best[node]:
            continue
        done.add(node)
        if node == goal:
            trace.append((node, c, []))
            return walk(parent, node), c, trace
        for child, d in g[node].items():
            nc = c + d
            if child not in done and nc < best.get(child, float('inf')):
                best[child], parent[child] = nc, node
                heapq.heappush(heap, (nc, child))
        front = sorted((best[n], n) for n in best if n not in done)
        trace.append((node, c, front))
    return None, None, trace


def bidirectional(g, start, goal):
    """Alternate one BFS layer from each end until the two reached sets meet."""
    fpar, bpar = {start: None}, {goal: None}
    flayer, blayer = [start], [goal]
    layers = []
    forward = True
    while flayer and blayer:
        par, other, layer = (fpar, bpar, flayer) if forward else (bpar, fpar, blayer)
        new = []
        for node in layer:
            for child in g[node]:
                if child not in par:
                    par[child] = node
                    new.append(child)
                    if child in other:
                        layers.append(('forward' if forward else 'backward', new))
                        left = walk(fpar, child)
                        right = walk(bpar, child)[::-1][1:]
                        return left + right, child, layers, set(fpar), set(bpar)
        layers.append(('forward' if forward else 'backward', new))
        if forward:
            flayer = new
        else:
            blayer = new
        forward = not forward
    return None, None, layers, set(fpar), set(bpar)


def walk(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def tree_bfs_order(tree, root):
    out, q = [], deque([root])
    while q:
        n = q.popleft()
        out.append(n)
        q.extend(tree.get(n, []))
    return out


def tree_dfs_order(tree, root):
    out = [root]
    for c in tree.get(root, []):
        out += tree_dfs_order(tree, c)
    return out


def tree_dls_order(tree, root, limit, depth=0):
    out = [root]
    if depth < limit:
        for c in tree.get(root, []):
            out += tree_dls_order(tree, c, limit, depth + 1)
    return out


def tree_ids_rounds(tree, root, goal):
    rounds = []
    for limit in range(10):
        order = tree_dls_order(tree, root, limit)
        if goal in order:
            rounds.append((limit, order[:order.index(goal) + 1]))
            return rounds
        rounds.append((limit, order))


def nodes_bfs(b, d):
    return sum(b ** i for i in range(1, d + 1))


def nodes_ids(b, d):
    return sum((d - i + 1) * b ** i for i in range(1, d + 1))


# ---------- assertions: every number the lessons quote ----------

def check():
    # Lesson 01-02: search tree sizes and the cost formulas.
    assert nodes_bfs(10, 6) == 1_111_110
    assert nodes_bfs(2, 2) == 6 and nodes_bfs(2, 3) == 14
    # Lesson 03 BFS.
    p, trace = bfs(MAP, 'Lagos', 'Abuja')
    assert p == ['Lagos', 'Benin', 'Lokoja', 'Abuja'] and cost(p) == 830
    assert [t[0] for t in trace] == ['Lagos', 'Benin', 'Ibadan', 'Akure', 'Lokoja']
    assert trace[0][1] == ['Benin', 'Ibadan']
    assert trace[1][1] == ['Ibadan', 'Akure', 'Lokoja']
    assert trace[2][1] == ['Akure', 'Lokoja', 'Ilorin']
    assert trace[3][1] == ['Lokoja', 'Ilorin']
    assert trace[4][1] == ['Ilorin', 'Abuja']
    assert tree_bfs_order(TREE7, 'A') == list('ABCDEFG')
    # Lesson 04 DFS.
    p, order = dfs(MAP, 'Lagos', 'Abuja')
    assert p == ['Lagos', 'Benin', 'Akure', 'Ibadan', 'Ilorin', 'Abuja'] and cost(p) == 1385
    assert order == ['Lagos', 'Benin', 'Akure', 'Ibadan', 'Ilorin', 'Abuja']
    assert tree_dfs_order(TREE7, 'A') == list('ABDECFG')
    # Lesson 05 DLS.
    r, order = dls(MAP, 'Lagos', 'Abuja', 2)
    assert r == 'cutoff'
    assert order == ['Lagos', 'Benin', 'Akure', 'Lokoja', 'Ibadan', 'Akure', 'Ilorin']
    r, order = dls(MAP, 'Lagos', 'Abuja', 3)
    assert r == ['Lagos', 'Benin', 'Lokoja', 'Abuja']
    assert order == ['Lagos', 'Benin', 'Akure', 'Ibadan', 'Lokoja', 'Lokoja', 'Abuja']
    assert tree_dls_order(TREE15, 'A', 2) == list('ABDECFG')
    # Lesson 05: the map's diameter (most roads between any two cities by their fewest-road route) is 3.
    def hops(a):
        dist, q = {a: 0}, deque([a])
        while q:
            n = q.popleft()
            for c in MAP[n]:
                if c not in dist:
                    dist[c] = dist[n] + 1
                    q.append(c)
        return dist
    assert max(max(hops(c).values()) for c in MAP) == 3
    # Lesson 06 IDS.
    r, rounds = ids(MAP, 'Lagos', 'Abuja')
    assert r == ['Lagos', 'Benin', 'Lokoja', 'Abuja'] and [x[0] for x in rounds] == [0, 1, 2, 3]
    assert [len(x[1]) for x in rounds] == [1, 3, 7, 7] and sum(len(x[1]) for x in rounds) == 18
    tr = tree_ids_rounds(TREE15, 'A', 'M')
    assert [''.join(o) for _, o in tr] == ['A', 'ABC', 'ABDECFG', 'ABDHIEJKCFLM']
    assert nodes_ids(10, 5) == 123_450 and nodes_bfs(10, 5) == 111_110
    # Lesson 07 UCS.
    p, c, trace = ucs(UCS_G, 'A', 'G')
    assert p == ['A', 'B', 'D', 'G'] and c == 5
    assert [(t[0], t[1]) for t in trace] == [('A', 0), ('B', 2), ('C', 3), ('D', 3), ('G', 5)]
    assert trace[0][2] == [(2, 'B'), (5, 'C')]
    assert trace[1][2] == [(3, 'C'), (3, 'D')]
    assert trace[3][2] == [(5, 'G')]
    p, c, trace = ucs(MAP, 'Lagos', 'Abuja')
    assert p == ['Lagos', 'Ibadan', 'Akure', 'Lokoja', 'Abuja'] and c == 790
    assert [(t[0], t[1]) for t in trace] == [('Lagos', 0), ('Ibadan', 130), ('Ilorin', 290), ('Benin', 330),
                                              ('Akure', 340), ('Lokoja', 590), ('Abuja', 790)]
    assert (810, 'Abuja') in trace[2][2]
    assert (630, 'Lokoja') in trace[3][2] and (590, 'Lokoja') in trace[4][2]
    # Lesson 08 bidirectional.
    p, meet, layers, fset, bset = bidirectional(MAP, 'Lagos', 'Abuja')
    assert meet == 'Lokoja' and p == ['Lagos', 'Benin', 'Lokoja', 'Abuja']
    assert layers == [('forward', ['Benin', 'Ibadan']), ('backward', ['Ilorin', 'Lokoja']), ('forward', ['Akure', 'Lokoja'])]
    assert 2 * nodes_bfs(10, 3) == 2220
    assert 2 * nodes_bfs(10, 2) == 220 and nodes_bfs(10, 4) == 11_110      # lesson 09 quiz
    assert nodes_ids(10, 3) == 1230 and nodes_bfs(10, 3) == 1110            # lesson 06 quiz, lesson 02 quiz
    # Quiz graphs in the UCS lessons.
    assert ucs(graph_from({('S', 'A'): 1, ('S', 'B'): 4, ('A', 'B'): 2, ('A', 'G'): 6, ('B', 'G'): 1}), 'S', 'G')[1] == 4
    assert ucs(graph_from({('S', 'A'): 2, ('S', 'B'): 5, ('A', 'C'): 4, ('B', 'C'): 1, ('C', 'G'): 6, ('A', 'G'): 11}), 'S', 'G')[1] == 12
    # Lesson 10's results table.
    assert cost(dfs(MAP, 'Lagos', 'Abuja')[0]) == 1385 and ucs(MAP, 'Lagos', 'Abuja')[1] == 790


# ---------- drawing ----------

def tree_layout(tree, root):
    """x by leaf order, y by depth."""
    pos, leaves = {}, [0]

    def place(n, depth):
        kids = tree.get(n, [])
        if not kids:
            pos[n] = (leaves[0], depth)
            leaves[0] += 1
        else:
            for k in kids:
                place(k, depth + 1)
            pos[n] = (sum(pos[k][0] for k in kids) / len(kids), depth)
    place(root, 0)
    return pos, leaves[0]


def draw_tree(tree, root, name, title, numbers=None, highlight=None, grey=None, limits=None, labels=None,
              xgap=70, ygap=80):
    pos, nleaves = tree_layout(tree, root)
    depth = max(d for _, d in pos.values())
    left = 60 if limits else 40
    w = left + (nleaves - 1) * xgap + 140 if limits else left * 2 + (nleaves - 1) * xgap
    h = 60 + depth * ygap + 50
    s = Svg(w, h, title)
    xy = {n: (left + x * xgap, 40 + d * ygap) for n, (x, d) in pos.items()}
    for p, kids in tree.items():
        for k in kids:
            if k in xy:
                s.line(*xy[p], *xy[k], color=GREY if grey and k in grey else INK, width=1.5)
    for lim, text in (limits or []):
        y = 40 + lim * ygap + ygap / 2
        s.line(left - 30, y, w - 110, y, color=ORANGE, width=2, dash='6 4')
        s.text(w - 104, y + 5, text, size=12, color='#b45309', anchor='start')
    for n, (x, y) in xy.items():
        fill = LIGHT if grey and n in grey else GOAL_FILL if highlight and n in highlight else NODE_FILL
        s.circle(x, y, 19, fill, stroke=GREY if grey and n in grey else INK)
        s.text(x, y + 5, (labels or {}).get(n, n), size=14, weight='bold', color=GREY if grey and n in grey else INK)
        if numbers and n in numbers:
            s.circle(x + 18, y - 17, 10, ORANGE)
            s.text(x + 18, y - 13, numbers[n], size=11, color='#ffffff', weight='bold')
    s.save(name, OUT)


def search_tree_from_map(depth):
    """The search tree from Lagos with no repeated-state check, to show the same city appearing many times."""
    tree, labels, ids_ = {}, {}, [0]

    def grow(city, d):
        nid = f'n{ids_[0]}'
        ids_[0] += 1
        labels[nid] = city[:3]
        if d < depth:
            tree[nid] = [grow(c, d + 1) for c in MAP[city]]
        return nid
    root = grow('Lagos', 0)
    return tree, labels, root


def draw_ucs_graph(name, title, highlight=None):
    from artificial_intelligence import save_neato, FONT
    pos = {'A': (0.5, 3.0), 'B': (0.0, 1.8), 'C': (1.6, 1.8), 'D': (0.8, 0.8), 'G': (1.6, -0.3)}
    hl = {frozenset(e) for e in zip(highlight or [], (highlight or [])[1:])}
    lines = ['graph { bgcolor="white"; pad=0.3; splines=line;',
             f'node [fontname="{FONT}", fontsize=14, shape=circle, style=filled, color="{INK}", penwidth=1.2, width=0.45, fixedsize=true];',
             f'edge [fontname="{FONT}", fontsize=13, color="{INK}", fontcolor="#374151", penwidth=1.4];']
    for n, (x, y) in pos.items():
        fill = START_FILL if n == 'A' else GOAL_FILL if n == 'G' else NODE_FILL
        lines.append(f'"{n}" [pos="{x * 90:.0f},{y * 90:.0f}!", fillcolor="{fill}"];')
    seen = set()
    for a, nb in UCS_G.items():
        for b, d in nb.items():
            if frozenset((a, b)) in seen:
                continue
            seen.add(frozenset((a, b)))
            st = f', color="{ORANGE}", penwidth=3.5' if frozenset((a, b)) in hl else ''
            lines.append(f'"{a}" -- "{b}" [label="  {d}  "{st}];')
    lines.append('}')
    save_neato('\n'.join(lines), name, title)


def draw_bidirectional(name, title, fset, bset, meet):
    from artificial_intelligence import save_neato, FONT, POS
    lines = ['graph { bgcolor="white"; pad=0.3; splines=line;',
             f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", color="{INK}", penwidth=1.2, margin="0.12,0.06"];',
             f'edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="#374151", penwidth=1.4];']
    for city, (x, y) in POS.items():
        if city == meet:
            fill, pw = '#fdba74', 3
        elif city in fset:
            fill, pw = START_FILL, 1.2
        elif city in bset:
            fill, pw = GOAL_FILL, 1.2
        else:
            fill, pw = '#ffffff', 1.2
        lines.append(f'"{city}" [pos="{x * 72:.0f},{y * 72:.0f}!", fillcolor="{fill}", penwidth={pw}];')
    for (a, b), d in ROADS.items():
        lines.append(f'"{a}" -- "{b}" [label=" {d}"];')
    lines.append('}')
    save_neato('\n'.join(lines), name, title)


def complexity_bars():
    """Nodes BFS would hold at b = 10, by depth: shows the exponential wall."""
    s = Svg(640, 300, 'Bar chart of nodes generated by breadth-first search with branching factor 10: 10 at depth 1, '
                      '100 at depth 2, 1,000 at depth 3, 10,000 at depth 4, 100,000 at depth 5, 1,000,000 at depth 6, on a log scale')
    import math
    base_y, top = 250, 40
    for d in range(1, 7):
        n = 10 ** d
        hgt = (math.log10(n) / 6) * (base_y - top)
        x = 60 + (d - 1) * 95
        s.rect(x, base_y - hgt, 60, hgt, NODE_FILL, stroke=INK)
        s.text(x + 30, base_y - hgt - 8, f'{n:,}', size=12)
        s.text(x + 30, base_y + 20, f'depth {d}', size=12)
    s.line(40, base_y, 620, base_y)
    s.text(320, 285, 'nodes at each depth when b = 10 (each bar is 10 times the one before)', size=12, color='#374151')
    s.save('se-growth.svg', OUT)


if __name__ == '__main__':
    check()
    bfs_n = {n: str(i) for i, n in enumerate(tree_bfs_order(TREE7, 'A'))}
    dfs_n = {n: str(i) for i, n in enumerate(tree_dfs_order(TREE7, 'A'))}
    draw_tree(TREE7, 'A', 'se-tree-bfs-order.svg',
              'A tree with root A, children B and C, and grandchildren D, E under B and F, G under C; breadth-first visits them '
              'in the order A 0, B 1, C 2, D 3, E 4, F 5, G 6, level by level', numbers=bfs_n)
    draw_tree(TREE7, 'A', 'se-tree-dfs-order.svg',
              'The same tree visited depth-first: A 0, B 1, D 2, E 3, C 4, F 5, G 6, going all the way down one branch before the next',
              numbers=dfs_n)
    tree, labels, root = search_tree_from_map(2)
    draw_tree(tree, root, 'se-search-tree.svg',
              'The search tree two levels deep from Lagos: Lagos has children Benin and Ibadan; Benin has children Akure, Lagos and '
              'Lokoja; Ibadan has children Akure, Ilorin and Lagos, so Lagos and Akure each appear more than once',
              labels=labels, xgap=74)
    dls_grey = set('HIJKLMNO')
    draw_tree(TREE15, 'A', 'se-dls-tree.svg',
              'A 15-node tree, A at the top, B and C, then D to G, then H to O; a depth limit of 2 is drawn under D to G, '
              'and H to O below it are greyed out because depth-limited search never visits them',
              grey=dls_grey, limits=[(2, 'limit = 2')], xgap=52)
    draw_tree(TREE15, 'A', 'se-ids-tree.svg',
              'The 15-node tree from the class notes with iterative-deepening limits 0, 1, 2 and 3 drawn as dashed lines '
              'between the levels; the goal M is on the bottom level, so it is found only when the limit reaches 3',
              highlight={'M'}, limits=[(0, 'limit 0'), (1, 'limit 1'), (2, 'limit 2')], xgap=52)
    draw_ucs_graph('se-ucs-graph.svg',
                   'The uniform-cost example from the class notes: A to B costs 2, A to C 5, B to C 1, B to D 1, C to D 3, D to G 2',)
    draw_ucs_graph('se-ucs-graph-path.svg',
                   'The same graph with the cheapest path A to B to D to G, cost 5, highlighted in orange',
                   highlight=['A', 'B', 'D', 'G'])
    route_map('se-bfs-route.svg',
              'The route breadth-first search returns, Lagos to Benin to Lokoja to Abuja, 830 km over 3 roads, highlighted in orange',
              highlight=['Lagos', 'Benin', 'Lokoja', 'Abuja'])
    route_map('se-dfs-route.svg',
              'The route depth-first search returns, Lagos to Benin to Akure to Ibadan to Ilorin to Abuja, 1,385 km over 5 roads, '
              'highlighted in orange', highlight=['Lagos', 'Benin', 'Akure', 'Ibadan', 'Ilorin', 'Abuja'])
    p, meet, layers, fset, bset = bidirectional(MAP, 'Lagos', 'Abuja')
    draw_bidirectional('se-bidirectional.svg',
                       'Bidirectional search on the map: the forward search from Lagos has reached Benin, Ibadan and Akure (green), '
                       'the backward search from Abuja has reached Ilorin and Lokoja (yellow), and they meet at Lokoja (orange)',
                       fset, bset, meet)
    complexity_bars()
