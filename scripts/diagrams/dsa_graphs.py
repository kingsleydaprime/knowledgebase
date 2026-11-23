"""Draw the DSA graph lesson diagrams (dsa/02-data-structures/09-graphs) as small SVG files.

    python3 scripts/diagrams/dsa_graphs.py      # run from the vault root

Every picture is computed by running the algorithm the lesson teaches on the
lesson's own graph (DFS, BFS, Kahn, Dijkstra, Bellman-Ford, Floyd-Warshall, A*,
Kruskal, Prim), and the lesson's numbers are asserted before drawing. Graphs are
laid out with Graphviz `neato` and pinned positions, so one graph looks the same
in every step picture of a lesson. Output: dsa/images/graph-*.svg.
"""
import heapq
import os
import re
import subprocess
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, PIX, PIX2, TRUE, ACCENT, FONT, Svg  # noqa: E402

OUT = os.path.join('dsa', 'images')
ORANGE = '#f59e0b'
PURPLE = '#7c3aed'
GREY = '#9ca3af'
NODE_FILL = '#dbeafe'
DONE_FILL = '#d1fae5'
FRONT_FILL = '#fef3c7'
COMP_FILLS = ['#dbeafe', '#d1fae5', '#fde68a', '#fbcfe8', '#e9d5ff', '#fed7aa', '#e5e7eb']
INF = float('inf')


# ---------- drawing helpers ----------

def save_graph(src, name, title, engine='neato'):
    """Like svgkit.save_dot, but lets us pick the engine (neato honours pinned pos= positions)."""
    r = subprocess.run([engine, '-Tsvg'], input=src, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f'{engine} failed on {name}: {r.stderr}')
    svg = r.stdout
    svg = re.sub(r'<\?xml.*?\?>\s*', '', svg)
    svg = re.sub(r'<!DOCTYPE.*?>\s*', '', svg, flags=re.S)
    svg = re.sub(r'<!--.*?-->\s*', '', svg, flags=re.S)
    svg = svg.replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', '')
    svg = re.sub(r'<title>[^<]*</title>\s*', '', svg)
    # Shrink: drop Graphviz's per-node/edge groups, hoist the font, round coordinates to one decimal.
    svg = re.sub(r'<g id="(?:node|edge)\d+" class="(?:node|edge)">\s*', '', svg)
    head, body = svg.split('<g id="graph0"', 1)
    body = body.replace('</g>\n', '').replace('</g>', '')
    body = body.replace('</svg>', '</g>\n</svg>')
    svg = head + '<g id="graph0" font-family="' + FONT + '"' + body
    svg = svg.replace(f' font-family="{FONT}"', '').replace('<g id="graph0"', f'<g id="graph0" font-family="{FONT}"', 1)
    svg = re.sub(r'(\d+\.\d)\d+', r'\1', svg)
    svg = re.sub(r'<g id="graph0" font-family="[^"]*" font-family', '<g id="graph0" font-family', svg)
    svg = svg.replace('<svg ', '<svg role="img" ', 1)
    title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    svg = re.sub(r'(<svg[^>]*>)', lambda m: m.group(1) + '\n<title>' + title + '</title>', svg, count=1)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(svg)
    print(f'{name}: {len(svg)} bytes')


def q(s):
    return str(s).replace('\\', '\\\\').replace('"', '\\"')


class G:
    """A graph picture with pinned positions (inches). Nodes and edges carry Graphviz attributes."""

    def __init__(self, directed=False, size=None):
        self.directed = directed
        self.splines = 'true'
        self.lines = []
        self.size = size

    def node(self, n, x, y, label=None, **a):
        attrs = {'pos': f'{x},{y}!', 'label': n if label is None else label}
        attrs.update(a)
        self.lines.append(f'"{q(n)}" [' + ', '.join(f'{k}="{q(v)}"' for k, v in attrs.items()) + '];')

    def text(self, key, x, y, label, size=13, **a):
        a.setdefault('fontcolor', INK)
        self.node('_t_' + key, x, y, label=label, shape='plaintext', style='', fontsize=size, width=0.1, height=0.1, fixedsize='false', **a)

    def edge(self, u, v, label=None, directed=None, **a):
        d = self.directed if directed is None else directed
        html = ''
        if label is not None:
            fc = a.pop('fontcolor', '#374151')
            lab = str(label).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html = (f', label=<<table border="0" cellborder="0" cellpadding="1" cellspacing="0" bgcolor="white">'
                    f'<tr><td><font color="{fc}">{lab}</font></td></tr></table>>')
        if not d:
            a.setdefault('dir', 'none')
        parts = [f'{k}="{q(v2)}"' for k, v2 in a.items()] + ([html[2:]] if html else [])
        self.lines.append(f'"{q(u)}" -> "{q(v)}" [' + ', '.join(parts) + '];')

    def src(self):
        return '\n'.join([
            f'digraph {{ bgcolor="white"; pad=0.2; splines={self.splines}; outputorder=edgesfirst; overlap=true;',
            f'node [fontname="{FONT}", fontsize=14, shape=circle, style=filled, fillcolor="{NODE_FILL}", '
            f'color="{INK}", penwidth=1.3, width=0.42, height=0.42, fixedsize=true];',
            f'edge [fontname="{FONT}", fontsize=12, color="{INK}", fontcolor="#374151", penwidth=1.3, arrowsize=0.8];',
            *self.lines, '}'])

    def save(self, name, title):
        save_graph(self.src(), name, title)


def draw_graph(pos, edges, directed=False, weights=None, node_style=None, edge_style=None, labels=None,
               dx=0.0, dy=0.0, g=None, xlabels=None):
    """Add one graph to G g (or a new one). pos: {v: (x, y)}; edges: [(u, v)]; weights: {(u, v): w}."""
    g = g or G(directed)
    node_style = node_style or {}
    edge_style = edge_style or {}
    for v, (x, y) in pos.items():
        a = dict(node_style.get(v, {}))
        if xlabels and v in xlabels:
            a['xlabel'] = xlabels[v]
        g.node(v, x + dx, y + dy, label=(labels or {}).get(v, v.split('#')[0]), **a)
    for e in edges:
        u, v = e
        w = (weights or {}).get(e)
        g.edge(u, v, label=w, directed=directed, **edge_style.get(e, {}))
    return g


def contact_check():
    pass


# ---------- lesson 1: what a graph is ----------

def degrees(edges, verts):
    deg = {v: 0 for v in verts}
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1          # a self-loop adds two ends at the same vertex
    return deg


def lesson1():
    # Block 1 of the lab, and Block 3's multigraph.
    pos = {'A': (0, 1.2), 'B': (1.4, 1.2), 'C': (0.7, 0), 'D': (2.1, 0)}
    edges = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D')]
    deg = degrees(edges, pos)
    assert deg == {'A': 2, 'B': 2, 'C': 3, 'D': 1} and sum(deg.values()) == 2 * len(edges)
    mpos = {'P': (3.6, 1.2), 'Q': (3.6, 0), 'R': (5.0, 0)}
    medges = [('P', 'Q'), ('P', 'Q'), ('Q', 'R'), ('R', 'R')]
    mdeg = degrees(medges, mpos)
    assert mdeg == {'P': 2, 'Q': 3, 'R': 3}
    g = G()
    g.lines.append('forcelabels=true;')
    for v, (x, y) in {**pos, **mpos}.items():
        d = {**deg, **mdeg}[v]
        g.node(v, x, y, xlabel=f'deg {d}', fontcolor=INK)
    for u, v in edges:
        g.edge(u, v)
    g.edge('P', 'Q', color=TRUE, penwidth=2)
    g.edge('P', 'Q', color=TRUE, penwidth=2)
    g.edge('Q', 'R')
    g.edge('R', 'R', color=TRUE, penwidth=2)
    g.text('t1', 1.05, -0.75, 'Simple graph: 4 edges,\ndegrees add to 8 = 2 x 4', 12)
    g.text('t2', 4.3, -0.75, 'Multigraph: parallel P-Q edges and\na self-loop at R (counts 2 to its degree)', 12)
    g.save('graph-terms-degrees.svg',
           'Left, a simple graph with edges A-B, A-C, B-C, C-D and degrees A 2, B 2, C 3, D 1. Right, a multigraph '
           'with two parallel P-Q edges, edge Q-R and a self-loop at R, degrees P 2, Q 3, R 3.')

    # The four dimensions, one small panel each.
    tri = {'A': (0, 1), 'B': (1.2, 1), 'C': (0.6, 0)}
    g = G()
    # 1. undirected
    for v, (x, y) in tri.items():
        g.node(v + '1', x, y, label=v)
    for u, v in [('A', 'B'), ('B', 'C'), ('C', 'A')]:
        g.edge(u + '1', v + '1')
    g.text('c1', 0.6, -0.6, 'Undirected: every edge\ngoes both ways', 12)
    # 2. directed, Block 4 of the lab
    dedges = [('A', 'B'), ('B', 'C'), ('C', 'A'), ('A', 'C')]
    indeg = {v: sum(1 for a, b in dedges if b == v) for v in tri}
    outdeg = {v: sum(1 for a, b in dedges if a == v) for v in tri}
    assert indeg == {'A': 1, 'B': 1, 'C': 2} and outdeg == {'A': 2, 'B': 1, 'C': 1}
    for v, (x, y) in tri.items():
        g.node(v + '2', x + 2.4, y, label=v)
    for u, v in dedges:
        g.edge(u + '2', v + '2', directed=True)
    g.text('c2', 3.0, -0.6, 'Directed: A to B exists,\nB to A does not', 12)
    # 3. weighted
    wt = {('A', 'B'): 4, ('B', 'C'): 1, ('C', 'A'): 2}
    for v, (x, y) in tri.items():
        g.node(v + '3', x, y - 2.2, label=v)
    for (u, v), w in wt.items():
        g.edge(u + '3', v + '3', label=w)
    g.text('c3', 0.6, -2.8, 'Weighted: A to B direct costs 4,\nA to C to B costs only 3', 12)
    # 4. disconnected
    for v, (x, y) in {'A': (0, 1), 'B': (1.2, 1), 'C': (0.6, 0), 'D': (1.6, 0.1)}.items():
        g.node(v + '4', x + 2.4, y - 2.2, label=v)
    g.edge('A4', 'B4')
    g.edge('A4', 'C4')
    g.text('c4', 3.0, -2.8, 'Disconnected: nothing\nreaches D', 12)
    g.save('graph-four-dimensions.svg',
           'Four small graphs: an undirected triangle; a directed graph with A to B, B to C, C to A and A to C; a '
           'weighted triangle where A to B costs 4 but A to C to B costs 3; and a disconnected graph where D has no edges.')

    # Sketch answer: P-Q, P-R, Q-R, R-S, S-S, plus isolated T.
    spos = {'P': (0, 1.2), 'Q': (1.4, 1.2), 'R': (0.7, 0), 'S': (2.1, 0), 'T': (2.6, 1.2)}
    sedges = [('P', 'Q'), ('P', 'R'), ('Q', 'R'), ('R', 'S'), ('S', 'S')]
    sdeg = degrees(sedges, spos)
    assert sdeg == {'P': 2, 'Q': 2, 'R': 3, 'S': 3, 'T': 0} and sum(sdeg.values()) == 10
    g = G()
    g.lines.append('forcelabels=true;')
    for v, (x, y) in spos.items():
        g.node(v, x, y, xlabel=f'deg {sdeg[v]}')
    for u, v in sedges:
        g.edge(u, v)
    g.text('t', 1.3, -0.65, 'Degrees add to 10 = 2 x 5 edges', 12)
    g.save('graph-sketch-degrees.svg',
           'Answer graph: triangle P-Q-R, edge R-S, a self-loop at S and a lone vertex T; degrees P 2, Q 2, R 3, '
           'S 3, T 0, adding to 10.')


# ---------- shared algorithms ----------

def adjacency(verts, edges, directed=False):
    adj = {v: [] for v in verts}
    for u, v in edges:
        adj[u].append(v)
        if not directed and u != v:
            adj[v].append(u)
    return adj


def components(verts, edges):
    adj = adjacency(verts, edges)
    seen, comps = set(), []
    for s in verts:
        if s in seen:
            continue
        seen.add(s)
        stack, grp = [s], []
        while stack:
            u = stack.pop()
            grp.append(u)
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        comps.append(sorted(grp))
    return comps


def reach(adj, s):
    seen, stack = {s}, [s]
    while stack:
        for w in adj[stack.pop()]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return seen


def sccs(verts, edges):
    adj = adjacency(verts, edges, directed=True)
    r = {v: reach(adj, v) for v in verts}
    out, done = [], set()
    for v in verts:
        if v not in done:
            grp = sorted(w for w in verts if w in r[v] and v in r[w])
            done |= set(grp)
            out.append(grp)
    return out


def condense(verts, edges):
    groups = sccs(verts, edges)
    cid = {v: i for i, g in enumerate(groups) for v in g}
    cedges = sorted({(cid[u], cid[v]) for u, v in edges if cid[u] != cid[v]})
    return groups, cedges


# ---------- lesson 2: paths, cycles and connectivity ----------

def classify_route(edges, seq):
    und = {frozenset(e) for e in edges}
    steps = [frozenset((a, b)) for a, b in zip(seq, seq[1:])]
    if any(s not in und for s in steps):
        return 'not a walk'
    closed = seq[0] == seq[-1]
    rep_e = len(set(steps)) < len(steps)
    inner = seq[:-1] if closed else seq
    rep_v = len(set(inner)) < len(inner)
    if not rep_v and not rep_e:
        return 'cycle' if closed else 'path'
    if not rep_e:
        return 'circuit' if closed else 'trail'
    return 'walk'


def lesson2():
    bow = [('A', 'B'), ('B', 'C'), ('C', 'A'), ('C', 'D'), ('D', 'E'), ('E', 'C')]
    pos = {'A': (0, 1), 'B': (0, 0), 'C': (0.9, 0.5), 'D': (1.8, 1), 'E': (1.8, 0)}
    panels = [(['A', 'B', 'C', 'D', 'E'], 'path', 'Path A-B-C-D-E: no vertex twice'),
              (['A', 'B', 'C', 'A'], 'cycle', 'Cycle A-B-C-A: back to the start,\nno vertex twice'),
              (['A', 'B', 'C', 'D', 'E', 'C'], 'trail', 'Trail A-B-C-D-E-C: C twice,\nbut no edge twice'),
              (['A', 'B', 'A', 'B'], 'walk', 'Walk A-B-A-B: the edge A-B\nis used three times')]
    g = G()
    for k, (seq, kind, cap) in enumerate(panels):
        assert classify_route(bow, seq) == kind, (seq, kind)
        dx, dy = (k % 2) * 3.0, -(k // 2) * 2.3
        for v, (x, y) in pos.items():
            g.node(f'{v}{k}', x + dx, y + dy, label=v,
                   **({'fillcolor': '#fde68a'} if v == seq[0] else {}))
        steps = {}
        for i, (a, b) in enumerate(zip(seq, seq[1:]), 1):
            steps.setdefault(frozenset((a, b)), []).append(str(i))
        for u, v in bow:
            st = steps.get(frozenset((u, v)))
            if st:
                g.edge(f'{u}{k}', f'{v}{k}', label=','.join(st), color=ORANGE, penwidth=3, fontcolor='#b45309')
            else:
                g.edge(f'{u}{k}', f'{v}{k}', color=GREY)
        g.text(f'c{k}', 0.9 + dx, -0.65 + dy, cap, 12)
    g.save('graph-routes-bowtie.svg',
           'Four copies of the bowtie graph (triangles A-B-C and C-D-E sharing C), each with one route in orange and '
           'its steps numbered: the path A-B-C-D-E, the cycle A-B-C-A, the trail A-B-C-D-E-C and the walk A-B-A-B.')

    # Block 2: components partition the vertices.
    verts = ['A', 'B', 'C', 'D', 'E', 'F']
    edges = [('A', 'B'), ('B', 'C'), ('D', 'E'), ('F', 'F')]
    comps = components(verts, edges)
    assert comps == [['A', 'B', 'C'], ['D', 'E'], ['F']]
    cpos = {'A': (0, 1), 'B': (0.9, 1), 'C': (0.45, 0.1), 'D': (2.0, 1), 'E': (2.0, 0.1), 'F': (3.1, 0.55)}
    g = G()
    for i, c in enumerate(comps):
        for v in c:
            g.node(v, *cpos[v], fillcolor=COMP_FILLS[i])
    for u, v in edges:
        g.edge(u, v)
    g.text('c0', 0.45, -0.5, 'component 1', 12)
    g.text('c1', 2.0, -0.5, 'component 2', 12)
    g.text('c2', 3.1, -0.5, 'component 3', 12)
    g.save('graph-components-partition.svg',
           'The graph with edges A-B, B-C, D-E and a self-loop at F, coloured by connected component: A, B, C in '
           'blue, D, E in green and F alone in yellow.')

    # Block 5: SCCs and the condensation.
    mverts = ['a', 'b', 'c', 'd', 'e', 'f']
    medges = [('a', 'b'), ('b', 'c'), ('c', 'a'), ('c', 'd'), ('d', 'e'), ('e', 'd'), ('e', 'f')]
    groups, cedges = condense(mverts, medges)
    assert groups == [['a', 'b', 'c'], ['d', 'e'], ['f']] and cedges == [(0, 1), (1, 2)]
    mpos = {'a': (0, 1), 'b': (0, 0), 'c': (0.8, 0.5), 'd': (1.8, 0.5), 'e': (2.8, 0.5), 'f': (3.8, 0.5)}
    g = G(directed=True)
    cid = {v: i for i, gr in enumerate(groups) for v in gr}
    for v, (x, y) in mpos.items():
        g.node(v, x, y, fillcolor=COMP_FILLS[cid[v]])
    for u, v in medges:
        g.edge(u, v)
    g.text('t1', 1.9, -0.55, 'Original: colour = strongly connected component', 12)
    cpos2 = {0: (0.4, -1.6), 1: (2.3, -1.6), 2: (3.8, -1.6)}
    for i, gr in enumerate(groups):
        g.node(f'S{i}', *cpos2[i], label='{' + ', '.join(gr) + '}', shape='box', style='rounded,filled',
               fillcolor=COMP_FILLS[i], width=1.0 if len(gr) > 1 else 0.6, height=0.4)
    for a, b in cedges:
        g.edge(f'S{a}', f'S{b}')
    g.text('t2', 1.9, -2.2, 'Condensed: each SCC becomes one vertex, and the result is a DAG', 12)
    g.save('graph-scc-condensation.svg',
           'Top, the directed graph a to b to c to a, c to d, d and e pointing at each other, e to f, coloured by '
           'strongly connected component: a b c, d e, and f. Bottom, its condensation: {a, b, c} to {d, e} to {f}, '
           'a DAG.')

    # Sketch answer: P<->Q, Q->R, R->S->T->R, W->S.
    sverts = ['P', 'Q', 'R', 'S', 'T', 'W']
    sedges = [('P', 'Q'), ('Q', 'P'), ('Q', 'R'), ('R', 'S'), ('S', 'T'), ('T', 'R'), ('W', 'S')]
    groups, cedges = condense(sverts, sedges)
    assert groups == [['P', 'Q'], ['R', 'S', 'T'], ['W']] and cedges == [(0, 1), (2, 1)]
    spos = {'P': (0, 0.5), 'Q': (1.0, 0.5), 'R': (2.0, 0.5), 'S': (3.0, 1.0), 'T': (3.0, 0), 'W': (4.1, 1.0)}
    g = G(directed=True)
    cid = {v: i for i, gr in enumerate(groups) for v in gr}
    for v, (x, y) in spos.items():
        g.node(v, x, y, fillcolor=COMP_FILLS[cid[v]])
    for u, v in sedges:
        g.edge(u, v)
    cpos2 = {0: (0.5, -1.2), 1: (2.4, -1.2), 2: (4.1, -1.2)}
    for i, gr in enumerate(groups):
        g.node(f'S{i}', *cpos2[i], label='{' + ', '.join(gr) + '}', shape='box', style='rounded,filled',
               fillcolor=COMP_FILLS[i], width=1.0 if len(gr) > 1 else 0.6, height=0.4)
    for a, b in cedges:
        g.edge(f'S{a}', f'S{b}')
    g.text('t2', 2.2, -1.8, 'Condensation: {P, Q} to {R, S, T}, and {W} to {R, S, T}', 12)
    g.save('graph-sketch-scc.svg',
           'Answer: the graph coloured by strongly connected component, {P, Q} in blue, {R, S, T} in green and {W} '
           'in yellow; below it the condensation, where {P, Q} and {W} both point to {R, S, T}.')


# ---------- lesson 3: subgraphs, trees and forests ----------

def bfs_tree(verts, edges, start):
    """BFS with neighbours in alphabetical order; returns the tree edges in the order they were added."""
    adj = {v: sorted(n) for v, n in adjacency(verts, edges).items()}
    seen, qu, tree = {start}, deque([start]), []
    while qu:
        u = qu.popleft()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                tree.append((u, w))
                qu.append(w)
    return tree


def is_tree(verts, edges):
    return len(edges) == len(verts) - 1 and len(components(verts, edges)) == 1


def lesson3():
    verts = ['A', 'B', 'C', 'D', 'E']
    edges = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
    pos = {'A': (0, 1), 'B': (0, 0), 'C': (0.9, 0.5), 'D': (1.8, 0.5), 'E': (2.7, 0.5)}
    keep = {'A', 'B', 'C'}
    induced = [e for e in edges if set(e) <= keep]
    assert induced == [('A', 'B'), ('A', 'C'), ('B', 'C')]
    spanning = [e for e in edges if e != ('A', 'C')]
    g = G()
    panels = [('G: all 5 vertices, 5 edges', set(verts), edges),
              ('Induced on {A, B, C}: pick vertices,\nevery edge between them comes along', keep, induced),
              ('Spanning: keep every vertex,\ndrop edges (A-C dropped)', set(verts), spanning)]
    for k, (cap, vs, es) in enumerate(panels):
        dy = -k * 2.1
        for v, (x, y) in pos.items():
            if v in vs:
                g.node(f'{v}{k}', x, y + dy, label=v)
            else:
                g.node(f'{v}{k}', x, y + dy, label=v, style='dashed', color=GREY, fontcolor=GREY)
        for u, v in edges:
            if (u, v) in es:
                g.edge(f'{u}{k}', f'{v}{k}', penwidth=2.2)
            else:
                g.edge(f'{u}{k}', f'{v}{k}', color=GREY, style='dashed')
        g.text(f'c{k}', 1.35, -0.55 + dy, cap, 12)
    g.save('graph-subgraphs.svg',
           'Three rows: the graph G with edges A-B, A-C, B-C, C-D, D-E; the subgraph induced on A, B, C, which keeps '
           'all three edges among them and greys out D and E; and a spanning subgraph that keeps every vertex but '
           'drops the edge A-C.')

    # G's spanning trees: G has one cycle (A-B-C), so drop any one of its 3 edges.
    trees = []
    for drop in [('B', 'C'), ('A', 'C'), ('A', 'B')]:
        es = [e for e in edges if e != drop]
        assert is_tree(verts, es)
        trees.append((drop, es))
    es_set = lambda es: {frozenset(e) for e in es}
    assert es_set(bfs_tree(verts, edges, 'A')) == es_set(trees[0][1])     # BFS from A drops B-C
    assert es_set(bfs_tree(verts, edges, 'B')) == es_set(trees[1][1])     # BFS from B drops A-C
    assert es_set(bfs_tree(verts, edges, 'C')) == es_set(trees[2][1])     # BFS from C drops A-B
    g = G()
    for k, (drop, es) in enumerate(trees):
        dy = -k * 2.15
        for v, (x, y) in pos.items():
            g.node(f'{v}{k}', x, y + dy, label=v)
        for u, v in edges:
            if (u, v) in es:
                g.edge(f'{u}{k}', f'{v}{k}', color=ACCENT, penwidth=3)
            else:
                g.edge(f'{u}{k}', f'{v}{k}', color=TRUE, style='dashed', penwidth=1.5)
        extra = '\n(the one BFS from A gives)' if k == 0 else ''
        g.text(f'c{k}', 1.35, -0.5 + dy, f'Drop {drop[0]}-{drop[1]}: 4 edges, a tree{extra}', 12)
    g.save('graph-spanning-trees.svg',
           'The three spanning trees of G, one per row, in green. Each one drops a different edge of the triangle '
           'A-B-C (dashed red: B-C, then A-C, then A-B) and keeps C-D and D-E, so every tree has 5 vertices and 4 '
           'edges.')

    # Sketch answer: two triangles sharing R, BFS from P with alphabetical neighbours.
    sverts = ['P', 'Q', 'R', 'S', 'T']
    sedges = [('P', 'Q'), ('Q', 'R'), ('P', 'R'), ('R', 'S'), ('S', 'T'), ('R', 'T')]
    st = bfs_tree(sverts, sedges, 'P')
    assert st == [('P', 'Q'), ('P', 'R'), ('R', 'S'), ('R', 'T')] and is_tree(sverts, st)
    spos = {'P': (0, 1), 'Q': (0, 0), 'R': (0.9, 0.5), 'S': (1.8, 1), 'T': (1.8, 0)}
    g = G()
    for v, (x, y) in spos.items():
        g.node(v, x, y, **({'fillcolor': '#fde68a'} if v == 'P' else {}))
    for u, v in sedges:
        if (u, v) in st or (v, u) in st:
            g.edge(u, v, color=ACCENT, penwidth=3)
        else:
            g.edge(u, v, color=TRUE, style='dashed')
    g.text('c', 0.9, -0.6, 'Tree edges (green): P-Q, P-R, R-S, R-T\nLeft out (dashed red): Q-R and S-T', 12)
    g.save('graph-sketch-spanning-tree.svg',
           'Answer: the BFS spanning tree from P in green, with edges P-Q, P-R, R-S and R-T; the edges Q-R and S-T '
           'are left out, shown dashed red.')


# ---------- lesson 4: representations ----------

def matrix_svg(sv, x0, y0, rows, cols, M, cell=30, title=None):
    """Draw a 0/1 grid with row and column headers; 1-cells shaded."""
    if title:
        sv.text(x0 + cell * (len(cols) + 1) / 2, y0 - 10, title, 13, weight='bold')
    for j, c in enumerate(cols):
        sv.text(x0 + cell * (j + 1.5), y0 + cell * 0.65, c, 12, weight='bold')
    for i, r in enumerate(rows):
        y = y0 + cell * (i + 1)
        sv.text(x0 + cell * 0.5, y + cell * 0.65, r, 12, weight='bold')
        for j in range(len(cols)):
            x = x0 + cell * (j + 1)
            v = M[i][j]
            sv.rect(x, y, cell, cell, PIX2 if v else '#ffffff', stroke='#9ca3af')
            sv.text(x + cell / 2, y + cell * 0.65, v, 13, color=INK if v else '#9ca3af')


def adjlist_svg(sv, x0, y0, verts, adj, cell=30, title=None):
    if title:
        sv.text(x0 + 70, y0 - 10, title, 13, weight='bold')
    for i, v in enumerate(verts):
        y = y0 + i * (cell + 10)
        sv.rect(x0, y, cell, cell, '#fde68a', stroke=INK)
        sv.text(x0 + cell / 2, y + cell * 0.65, v, 13, weight='bold')
        x = x0 + cell
        for w in adj[v]:
            sv.line(x, y + cell / 2, x + 14, y + cell / 2, INK, 1.3)
            sv.path(f'M{x + 14:.1f},{y + cell / 2 - 4:.1f} L{x + 20:.1f},{y + cell / 2:.1f} '
                    f'L{x + 14:.1f},{y + cell / 2 + 4:.1f} Z', INK, 1, fill=INK)
            x += 20
            sv.rect(x, y, cell, cell, NODE_FILL, stroke=INK)
            sv.text(x + cell / 2, y + cell * 0.65, w, 13)
            x += cell


def adj_matrix(verts, edges, directed):
    idx = {v: i for i, v in enumerate(verts)}
    M = [[0] * len(verts) for _ in verts]
    for u, v in edges:
        M[idx[u]][idx[v]] = 1
        if not directed:
            M[idx[v]][idx[u]] = 1
    return M


def list_vs_matrix(verts, edges, directed, name, title, caption):
    adj = {v: sorted(n) for v, n in adjacency(verts, edges, directed).items()}
    M = adj_matrix(verts, edges, directed)
    n = len(verts)
    maxlen = max(len(a) for a in adj.values())
    lw = 30 + maxlen * 50 + 30
    sv = Svg(lw + 30 * (n + 1) + 40, 50 + n * 40 + 40, title)
    adjlist_svg(sv, 20, 40, verts, adj, title='Adjacency list')
    matrix_svg(sv, lw + 20, 30, verts, verts, M, title='Adjacency matrix')
    sv.text(sv.w / 2, sv.h - 12, caption, 12, color='#374151')
    sv.save(name, OUT)
    return adj, M


def lesson4():
    verts = ['A', 'B', 'C', 'D']
    edges = [('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('C', 'D')]
    pos = {'A': (0, 1.2), 'B': (1.2, 1.2), 'C': (0, 0), 'D': (1.2, 0)}
    g = G()
    for v, (x, y) in pos.items():
        g.node(v, x, y)
    for u, v in edges:
        g.edge(u, v)
    g.save('graph-rep-example.svg',
           'The example graph: A and B on top, C and D below, with edges A-B, A-C, B-C, B-D and C-D.')

    M = adj_matrix(verts, edges, False)
    assert M == [[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]]
    assert all(M[i][j] == M[j][i] for i in range(4) for j in range(4))
    sv = Svg(200, 185, 'Adjacency matrix of the example graph: row A is 0 1 1 0, row B is 1 0 1 1, row C is 1 1 0 1, '
                       'row D is 0 1 1 0; the shaded 1s are mirror images across the diagonal.')
    matrix_svg(sv, 20, 20, verts, verts, M, cell=32)
    sv.save('graph-rep-adj-matrix.svg', OUT)

    names = [u + v for u, v in edges]
    I = [[1 if v in e else 0 for e in edges] for v in verts]
    assert I == [[1, 1, 0, 0, 0], [1, 0, 1, 1, 0], [0, 1, 1, 0, 1], [0, 0, 0, 1, 1]]
    assert all(sum(I[i][j] for i in range(4)) == 2 for j in range(5))
    sv = Svg(245, 190, 'Incidence matrix of the example graph: rows A to D, columns for the edges AB, AC, BC, BD, '
                       'CD; each column has exactly two shaded 1s, one for each endpoint.')
    matrix_svg(sv, 20, 20, verts, names, I, cell=34)
    sv.save('graph-rep-incidence.svg', OUT)

    adj, _ = list_vs_matrix(verts, edges, False, 'graph-rep-list-vs-matrix.svg',
                            'The same graph stored two ways. Left, the adjacency list: A to B, C; B to A, C, D; C to '
                            'A, B, D; D to B, C, which is 10 entries. Right, the 4 by 4 adjacency matrix, 16 cells of '
                            'which 10 are 1.',
                            'List: 10 entries (2 per edge).  Matrix: 16 cells, whatever the edge count.')
    assert sum(len(a) for a in adj.values()) == 2 * len(edges)

    # Sketch answer: a directed graph.
    sverts = ['P', 'Q', 'R', 'S']
    sedges = [('P', 'Q'), ('P', 'R'), ('Q', 'R'), ('R', 'P'), ('R', 'S')]
    adj, M = list_vs_matrix(sverts, sedges, True, 'graph-sketch-list-matrix.svg',
                            'Answer: adjacency list P to Q, R; Q to R; R to P, S; S has no out-edges. Adjacency '
                            'matrix rows P 0 1 1 0, Q 0 0 1 0, R 1 0 0 1, S 0 0 0 0, which is not symmetric.',
                            'Directed: 5 edges, 5 list entries, five 1s.')
    assert M == [[0, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1], [0, 0, 0, 0]]


# ---------- traversal helpers ----------

def dfs_run(adj, start, seen=None):
    """Recursive DFS, neighbours in list order. Returns pre-order, post-order, parent and the call stack at each
    arrival (one snapshot per visited vertex)."""
    seen = set() if seen is None else seen
    pre, post, parent, stacks, path = [], [], {start: None}, [], []

    def visit(v):
        seen.add(v)
        path.append(v)
        pre.append(v)
        stacks.append(list(path))
        for w in adj[v]:
            if w not in seen:
                parent[w] = v
                visit(w)
        post.append(v)
        path.pop()

    visit(start)
    return pre, post, parent, stacks


def tree_edges_of(parent):
    return {frozenset((v, p)) for v, p in parent.items() if p is not None}


def num_label(g, key, x, y, text, off, color='#b45309'):
    ox, oy = off
    g.text(key, x + ox, y + oy, text, 12, fontcolor=color)


def traversal_frames(pos, edges, frames, name, title, cols=3, directed=False, w=2.6, h=2.5, cap_dy=-0.55,
                     off=None):
    """frames: list of dicts with keys visited (ordered list), new (vertex), tree (set of frozenset edges),
    hot (set of vertices to outline, e.g. the call stack or the queue), caption."""
    g = G(directed)
    for k, fr in enumerate(frames):
        dx, dy = (k % cols) * w, -(k // cols) * h
        num = fr.get('nums') or {v: i + 1 for i, v in enumerate(fr['visited'])}
        for v, (x, y) in pos.items():
            a = {}
            if v in fr['visited']:
                a['fillcolor'] = DONE_FILL
            if v in num:
                num_label(g, f'n{v}#{k}', x + dx, y + dy, str(num[v]), (off or {}).get(v, (-0.36, 0.22)))
            if v in fr.get('hot', ()):
                a['fillcolor'] = FRONT_FILL
            if v == fr.get('new'):
                a.update(color=ORANGE, penwidth=3)
            g.node(f'{v}#{k}', x + dx, y + dy, label=v, **a)
        for u, v in edges:
            if frozenset((u, v)) in fr['tree']:
                g.edge(f'{u}#{k}', f'{v}#{k}', color=PIX, penwidth=3)
            else:
                g.edge(f'{u}#{k}', f'{v}#{k}', color=GREY)
        g.text(f'cap{k}', dx + fr.get('cx', 0.6), dy + cap_dy, fr['caption'], 12)
    g.save(name, title)


# ---------- lesson 5.1: depth-first search ----------

def lesson_dfs():
    # The cave from the motivation: A -> B, A -> C, B -> D, B -> E. DFS goes deep down B first.
    cave = {'A': ['B', 'C'], 'B': ['D', 'E'], 'C': [], 'D': [], 'E': []}
    pre, post, parent, _ = dfs_run(cave, 'A')
    assert pre == ['A', 'B', 'D', 'E', 'C']
    labels = {'A': 'Entrance A', 'B': 'Tunnel B', 'C': 'Tunnel C', 'D': 'Dead end D', 'E': 'Exit E'}
    cpos = {'A': (1.2, 2), 'B': (0.4, 1), 'C': (2.2, 1), 'D': (-0.4, 0), 'E': (1.2, 0)}
    g = G(directed=True)
    for v, (x, y) in cpos.items():
        g.node(v, x, y, label=f'{labels[v]}\n({pre.index(v) + 1})', shape='box', style='rounded,filled',
               width=1.2, height=0.55)
    for u in cave:
        for v in cave[u]:
            g.edge(u, v)
    g.text('cap', 0.9, -0.7, 'Numbers: the order DFS enters each place.\nIt finishes D and E before it ever tries C.', 12)
    g.save('graph-dfs-cave.svg',
           'The cave as a graph: Entrance A leads to Tunnel B and Tunnel C; Tunnel B leads to Dead end D and Exit E. '
           'DFS enters them in the order A 1, B 2, D 3, E 4, C 5.')

    # The lab's graph G.
    verts = ['A', 'B', 'C', 'D', 'E']
    edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E')]
    adj = {v: sorted(n) for v, n in adjacency(verts, edges).items()}
    pre, post, parent, stacks = dfs_run(adj, 'A')
    assert pre == ['A', 'B', 'D', 'C', 'E'] and post == ['C', 'E', 'D', 'B', 'A']
    pos = {'A': (0.8, 2.1), 'B': (0, 1.2), 'C': (1.6, 1.2), 'D': (0.8, 0.4), 'E': (1.9, 0.1)}
    off = {'A': (0, 0.36), 'B': (-0.38, 0), 'C': (0.38, 0), 'D': (-0.38, -0.1), 'E': (0, -0.36)}
    frames = []
    tree = set()
    for k, v in enumerate(pre):
        if parent[v]:
            tree.add(frozenset((v, parent[v])))
        frames.append({'visited': pre[:k + 1], 'new': v, 'tree': set(tree), 'hot': set(stacks[k]),
                       'caption': f'Visit {v}. Call stack: {" ".join(stacks[k])}', 'cx': 0.95})
    frames.append({'visited': pre, 'tree': set(tree), 'caption': 'Done. Blue = DFS tree;\nA-C was never used',
                   'cx': 0.95})
    traversal_frames(pos, edges, frames, 'graph-dfs-steps.svg',
                     'Recursive DFS from A on the lab graph, one frame per visit: A, then B, then D, then C (call '
                     'stack A B D C), then E after backing up to D. The tree edges A-B, B-D, D-C and D-E are blue; '
                     'the edge A-C is never used.', w=2.9, h=3.6, off=off, cap_dy=-0.7)

    # Pre and post order on one picture.
    g = G()
    te = tree_edges_of(parent)
    poff = {'A': (0, 0.4), 'B': (-0.75, 0), 'C': (0.75, 0), 'D': (-0.75, -0.1), 'E': (0, -0.4)}
    for v, (x, y) in pos.items():
        g.node(v, x, y, fillcolor=DONE_FILL)
        num_label(g, 'n' + v, x, y, f'pre {pre.index(v) + 1}, post {post.index(v) + 1}', poff[v])
    for u, v in edges:
        if frozenset((u, v)) in te:
            g.edge(u, v, color=PIX, penwidth=3)
        else:
            g.edge(u, v, color=GREY, style='dashed')
    g.save('graph-dfs-pre-post.svg',
           'The lab graph with each vertex labelled by its pre-order and post-order number: A pre 1 post 5, B pre 2 '
           'post 4, D pre 3 post 3, C pre 4 post 1, E pre 5 post 2. The DFS tree edges are blue.')

    # Sketch answer.
    sverts = ['P', 'Q', 'R', 'S', 'T', 'U']
    sedges = [('P', 'Q'), ('P', 'R'), ('Q', 'S'), ('R', 'S'), ('R', 'T'), ('S', 'U')]
    sadj = {v: sorted(n) for v, n in adjacency(sverts, sedges).items()}
    assert sadj == {'P': ['Q', 'R'], 'Q': ['P', 'S'], 'R': ['P', 'S', 'T'], 'S': ['Q', 'R', 'U'],
                    'T': ['R'], 'U': ['S']}
    pre, post, parent, _ = dfs_run(sadj, 'P')
    assert pre == ['P', 'Q', 'S', 'R', 'T', 'U']
    te = tree_edges_of(parent)
    assert te == {frozenset(e) for e in [('P', 'Q'), ('Q', 'S'), ('S', 'R'), ('R', 'T'), ('S', 'U')]}
    spos = {'P': (0, 1.2), 'Q': (0, 0), 'R': (1.2, 1.2), 'S': (1.2, 0), 'T': (2.4, 1.2), 'U': (2.4, 0)}
    g = G()
    for v, (x, y) in spos.items():
        g.node(v, x, y, fillcolor=DONE_FILL)
        num_label(g, 'n' + v, x, y, str(pre.index(v) + 1), (-0.25, 0.3) if y > 0.5 else (-0.25, -0.3))
    for u, v in sedges:
        if frozenset((u, v)) in te:
            g.edge(u, v, color=PIX, penwidth=3)
        else:
            g.edge(u, v, color=GREY, style='dashed')
    g.text('cap', 1.2, -0.8, 'Visit order P, Q, S, R, T, U. Blue = DFS tree;\nP-R (dashed) is not a tree edge', 12)
    g.save('graph-sketch-dfs.svg',
           'Answer: DFS from P visits P 1, Q 2, S 3, R 4, T 5, U 6. The tree edges P-Q, Q-S, S-R, R-T and S-U are '
           'blue; the edge P-R is dashed because R was already visited by the time P looked at it.')


# ---------- lesson 5.2: breadth-first search ----------

def bfs_run(adj, start):
    """BFS marking on enqueue. Returns dequeue order, dist, parent and one snapshot per dequeue."""
    dist, parent, qu = {start: 0}, {start: None}, deque([start])
    order, snaps = [], []
    while qu:
        v = qu.popleft()
        order.append(v)
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                parent[w] = v
                qu.append(w)
        snaps.append((v, list(qu), dict(parent)))
    return order, dist, parent, snaps


def layered(pos, edges, dist, parent, name, title, caption, directed=False):
    g = G(directed)
    te = tree_edges_of(parent)
    levels = sorted(set(dist.values()))
    xs = [x for x, _ in pos.values()]
    for L in levels:
        y = [pos[v][1] for v in dist if dist[v] == L][0]
        g.text(f'L{L}', min(xs) - 0.9, y, f'level {L}', 12, fontcolor='#6b7280')
    for v, (x, y) in pos.items():
        g.node(v, x, y, fillcolor=COMP_FILLS[dist[v] % len(COMP_FILLS)])
    for u, v in edges:
        if frozenset((u, v)) in te:
            g.edge(u, v, color=PIX, penwidth=3)
        else:
            g.edge(u, v, color=GREY, style='dashed')
    g.text('cap', (min(xs) + max(xs)) / 2, min(y for _, y in pos.values()) - 0.65, caption, 12)
    g.save(name, title)


def lesson_bfs():
    # The pond metaphor: Start -> A, B; A -> C, D; B -> E.
    pond = {'Start': ['A', 'B'], 'A': ['C', 'D'], 'B': ['E'], 'C': [], 'D': [], 'E': []}
    order, dist, parent, _ = bfs_run(pond, 'Start')
    assert order == ['Start', 'A', 'B', 'C', 'D', 'E'] and dist['E'] == 2
    ppos = {'Start': (1.2, 2), 'A': (0.6, 1), 'B': (1.8, 1), 'C': (0, 0), 'D': (1.2, 0), 'E': (2.4, 0)}
    g = G()
    for L in range(3):
        g.text(f'L{L}', -1.0, 2 - L, f'level {L}', 12, fontcolor='#6b7280')
    for v, (x, y) in ppos.items():
        g.node(v, x, y, fillcolor=COMP_FILLS[dist[v]], width=0.62 if v == 'Start' else 0.42)
    for u in pond:
        for v in pond[u]:
            g.edge(u, v, color=PIX, penwidth=2.5)
    g.text('cap', 1.2, -0.65, 'BFS order: Start, A, B, C, D, E.\nEvery level-1 node comes before any level-2 node.', 12)
    g.save('graph-bfs-pond.svg',
           'Ripples as levels: Start at level 0; A and B at level 1; C and D (from A) and E (from B) at level 2. BFS '
           'visits Start, A, B, C, D, E, one level at a time.')

    verts = ['A', 'B', 'C', 'D', 'E', 'F']
    edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('D', 'E'), ('C', 'F'), ('F', 'E')]
    adj = {v: sorted(n) for v, n in adjacency(verts, edges).items()}
    order, dist, parent, snaps = bfs_run(adj, 'A')
    assert dist == {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 3, 'F': 2}
    assert order == ['A', 'B', 'C', 'D', 'F', 'E']
    pos = {'A': (1, 3), 'B': (0.4, 2), 'C': (1.6, 2), 'D': (0.4, 1), 'F': (1.6, 1), 'E': (1, 0)}
    off = {'A': (0.4, 0.1), 'B': (-0.4, 0), 'C': (0.4, 0), 'D': (-0.4, 0), 'F': (0.4, 0), 'E': (0.4, -0.1)}
    frames = []
    for k, (v, qu, par) in enumerate(snaps):
        done = order[:k + 1]
        nums = {w: f'd={dist[w]}' for w in par}
        frames.append({'visited': done, 'nums': nums, 'new': v, 'hot': set(qu), 'tree': tree_edges_of(par),
                       'caption': f'Take {v}. Queue: {" ".join(qu) if qu else "(empty)"}', 'cx': 1.0})
    traversal_frames(pos, edges, frames, 'graph-bfs-steps.svg',
                     'BFS from A on the lab graph, one frame per vertex taken from the queue: A (queue B C), B (queue '
                     'C D), C (queue D F), D (queue F E), F (queue E), E (queue empty). Each vertex shows its '
                     'distance, A 0, B and C 1, D and F 2, E 3, and the BFS tree edges are blue.',
                     w=2.8, h=4.3, off={k: (o[0] * 1.3, o[1]) for k, o in off.items()}, cap_dy=-0.7)

    layered(pos, edges, dist, parent, 'graph-bfs-layers.svg',
            'The lab graph drawn in BFS levels from A: level 0 A, level 1 B and C, level 2 D and F, level 3 E. Blue '
            'tree edges A-B, A-C, B-D, C-F, D-E; the dashed edges C-D and F-E join vertices already found.',
            'Blue: the BFS tree. Dashed: edges that\nfound nothing new. A to E takes 3 edges.')

    # Multi-source BFS on the 4 x 5 grid (Block 3).
    R, C = 4, 5
    gverts = [(r, c) for r in range(R) for c in range(C)]
    gedges = [((r, c), (r + 1, c)) for r in range(R - 1) for c in range(C)] + \
             [((r, c), (r, c + 1)) for r in range(R) for c in range(C - 1)]
    gadj = adjacency(gverts, gedges)

    def msbfs(srcs):
        d, qq = {s0: 0 for s0 in srcs}, deque(srcs)
        while qq:
            v = qq.popleft()
            for w in gadj[v]:
                if w not in d:
                    d[w] = d[v] + 1
                    qq.append(w)
        return d
    single, multi = msbfs([(0, 0)]), msbfs([(0, 0), (3, 4)])
    assert single[(3, 4)] == 7 and multi[(3, 4)] == 0 and [multi[(0, c)] for c in range(C)] == [0, 1, 2, 3, 3]
    shades = ['#1e40af', '#2563eb', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f8fafc']
    cell = 34
    sv = Svg(2 * C * cell + 90, R * cell + 80,
             'Two 4 by 5 grids of BFS distances. Left, from the top-left corner alone: 0 in the corner rising to 7 '
             'in the opposite corner. Right, from both corners at once: each cell holds the distance to the nearer '
             'corner, at most 3.')
    for k, (d, cap) in enumerate([(single, 'From (0,0) alone'), (multi, 'From either corner')]):
        x0 = 20 + k * (C * cell + 50)
        sv.text(x0 + C * cell / 2, 24, cap, 13, weight='bold')
        for r in range(R):
            for c in range(C):
                v = d[(r, c)]
                sv.rect(x0 + c * cell, 36 + r * cell, cell, cell, shades[v], stroke='#ffffff', width=2)
                sv.text(x0 + c * cell + cell / 2, 36 + r * cell + cell * 0.65, v, 13,
                        color='#ffffff' if v <= 2 else INK, weight='bold' if v == 0 else 'normal')
    sv.text(sv.w / 2, sv.h - 14, 'Darker = closer. Both 0s go in the queue first; one pass fills the grid.', 12,
            color='#374151')
    sv.save('graph-bfs-multisource.svg', OUT)

    # Sketch answer.
    sverts = ['S', 'A', 'B', 'C', 'D', 'E', 'F']
    sedges = [('S', 'A'), ('S', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('C', 'E'), ('D', 'E'), ('E', 'F')]
    sadj = {v: sorted(n) for v, n in adjacency(sverts, sedges).items()}
    order, dist, parent, _ = bfs_run(sadj, 'S')
    assert dist == {'S': 0, 'A': 1, 'B': 1, 'C': 2, 'D': 2, 'E': 3, 'F': 4}
    assert tree_edges_of(parent) == {frozenset(e) for e in
                                     [('S', 'A'), ('S', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'E'), ('E', 'F')]}
    spos = {'S': (1, 4), 'A': (0.4, 3), 'B': (1.6, 3), 'C': (0.4, 2), 'D': (1.6, 2), 'E': (1, 1), 'F': (1, 0)}
    layered(spos, sedges, dist, parent, 'graph-sketch-bfs.svg',
            'Answer: BFS levels from S: level 0 S, level 1 A and B, level 2 C and D, level 3 E, level 4 F. Blue tree '
            'edges S-A, S-B, A-C, B-D, C-E, E-F; dashed B-C and D-E.',
            'Blue: BFS tree. Dashed: B-C and D-E.')


# ---------- lesson 5.3: traversal trees and edge classification ----------

KIND_STYLE = {'tree': dict(color=PIX, penwidth=3),
              'back': dict(color=TRUE, penwidth=2.2, style='dashed'),
              'forward': dict(color=ACCENT, penwidth=2.2, style='dashed'),
              'cross': dict(color=PURPLE, penwidth=2.2, style='dotted')}
KIND_FONT = {'tree': '#1d4ed8', 'back': TRUE, 'forward': '#047857', 'cross': PURPLE}


def dfs_classify(graph, roots=None):
    colour = {v: 0 for v in graph}
    d, f, kinds, clock = {}, {}, {}, [0]

    def visit(u):
        clock[0] += 1
        d[u] = clock[0]
        colour[u] = 1
        for v in graph[u]:
            if colour[v] == 0:
                kinds[(u, v)] = 'tree'
                visit(v)
            elif colour[v] == 1:
                kinds[(u, v)] = 'back'
            else:
                kinds[(u, v)] = 'forward' if d[u] < d[v] else 'cross'
        colour[u] = 2
        clock[0] += 1
        f[u] = clock[0]

    for r in roots or graph:
        if colour[r] == 0:
            visit(r)
    return d, f, kinds


def classified_picture(graph, pos, name, title, caption, roots=None, dfnums=True, label_kinds=True, off=None,
                       cap_xy=None):
    d, f, kinds = dfs_classify(graph, roots)
    g = G(directed=True)
    for v, (x, y) in pos.items():
        g.node(v, x, y, fillcolor=DONE_FILL)
        if dfnums:
            num_label(g, 'n' + v, x, y, f'{d[v]}/{f[v]}', (off or {}).get(v, (0, 0.38)), color=INK)
    for (u, v), k in kinds.items():
        g.edge(u, v, label=k if label_kinds and k != 'tree' else None, fontcolor=KIND_FONT[k], **KIND_STYLE[k])
    cx, cy = cap_xy or ((min(x for x, _ in pos.values()) + max(x for x, _ in pos.values())) / 2,
                        min(y for _, y in pos.values()) - 0.75)
    g.text('cap', cx, cy, caption, 12)
    g.save(name, title)
    return d, f, kinds


def lesson_edges():
    # The motivating DAG: A -> B -> D, A -> C -> D. No cycle, but C sees D already visited.
    dag = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': []}
    pos = {'A': (0, 1), 'B': (1.3, 1), 'D': (2.6, 1), 'C': (1.3, 0)}
    d, f, kinds = classified_picture(
        dag, pos, 'graph-edges-naive-trap.svg',
        'The graph A to B to D and A to C to D, with each vertex marked by its DFS discovery and finish times: A 1/8, '
        'B 2/5, D 3/4, C 6/7. The edge C to D is a dotted purple cross edge: D was already visited, but finished, so '
        'there is no cycle.',
        'C to D reaches a vertex already visited, but D is finished\n(black), not on the current path. No cycle.',
        off={'C': (0, -0.38)})
    assert kinds[('C', 'D')] == 'cross' and 'back' not in kinds.values()

    graph = {'u': ['v', 'x'], 'v': ['y'], 'w': ['y', 'z'], 'x': ['v'], 'y': ['x'], 'z': ['z']}
    pos = {'u': (0, 1.2), 'v': (1.4, 1.2), 'y': (2.8, 1.2), 'x': (1.4, 0), 'w': (4.2, 0), 'z': (4.2, -1.2)}
    g = G(directed=True)
    for v, (x, y) in pos.items():
        g.node(v, x, y)
    for u in graph:
        for v in graph[u]:
            g.edge(u, v)
    g.save('graph-edges-example.svg',
           'The running example: u to v, u to x, v to y, y to x, x to v, w to y, w to z, and a self-loop on z.')

    d, f, kinds = classified_picture(
        graph, pos, 'graph-edges-classified.svg',
        'The running example with every edge coloured by kind and each vertex marked discovery/finish: u 1/8, v 2/7, '
        'y 3/6, x 4/5, w 9/12, z 10/11. Tree edges u-v, v-y, y-x, w-z are solid blue; back edges x to v and the '
        'self-loop z are dashed red; forward edge u to x is dashed green; cross edge w to y is dotted purple.',
        'Blue solid = tree, red dashed = back,\ngreen dashed = forward, purple dotted = cross',
        off={'x': (0, -0.38), 'w': (0.5, 0.1), 'z': (-0.5, 0)}, cap_xy=(2.0, -1.4))
    assert (d['u'], f['u'], d['v'], f['v'], d['y'], f['y'], d['x'], f['x']) == (1, 8, 2, 7, 3, 6, 4, 5)
    assert (d['w'], f['w'], d['z'], f['z']) == (9, 12, 10, 11)
    assert kinds == {('u', 'v'): 'tree', ('v', 'y'): 'tree', ('y', 'x'): 'tree', ('x', 'v'): 'back',
                     ('u', 'x'): 'forward', ('w', 'y'): 'cross', ('w', 'z'): 'tree', ('z', 'z'): 'back'}

    # The parenthesis timeline.
    order = sorted(d, key=d.get)
    depth = {'u': 0, 'v': 1, 'y': 2, 'x': 3, 'w': 0, 'z': 1}
    step, x0 = 46, 40
    sv = Svg(x0 * 2 + step * 11, 250,
             'Timeline of the DFS clock from 1 to 12. Each vertex is a bar from its discovery to its finish time: u '
             '1 to 8, v 2 to 7, y 3 to 6, x 4 to 5 nested inside each other, then w 9 to 12 and z 10 to 11 nested '
             'in a separate second tree.')
    for t in range(1, 13):
        X = x0 + (t - 1) * step
        sv.line(X, 30, X, 200, '#e5e7eb', 1)
        sv.text(X, 22, t, 12, color='#6b7280')
    for v in order:
        y = 42 + depth[v] * 34
        X1, X2 = x0 + (d[v] - 1) * step, x0 + (f[v] - 1) * step
        fill = PIX2 if v in 'uvyx' else '#fde68a'
        sv.rect(X1 - 12, y, X2 - X1 + 24, 24, fill, stroke=INK)
        sv.text((X1 + X2) / 2, y + 17, v, 13, weight='bold')
    sv.text(x0 + 3.5 * step, 225, 'first DFS tree (root u)', 12, color='#374151')
    sv.text(x0 + 9.5 * step, 225, 'second DFS tree (root w)', 12, color='#374151')
    sv.text(sv.w / 2, 244, 'Bars nest or sit apart; they never partly overlap.', 12, color='#374151')
    sv.save('graph-edges-timeline.svg', OUT)

    # Sketch answer: fresh digraph.
    sg = {'a': ['b', 'd'], 'b': ['c'], 'c': ['a', 'd'], 'd': [], 'e': ['d', 'e']}
    spos = {'a': (0, 1.2), 'b': (1.4, 1.2), 'c': (1.4, 0), 'd': (2.8, 0), 'e': (4.2, 0)}
    d, f, kinds = classified_picture(
        sg, spos, 'graph-sketch-edge-kinds.svg',
        'Answer: DFS from a gives a 1/8, b 2/7, c 3/6, d 4/5, then e 9/10. Tree edges a-b, b-c, c-d in solid blue; '
        'back edges c to a and the self-loop on e in dashed red; forward edge a to d in dashed green; cross edge e '
        'to d in dotted purple.',
        'tree: a-b, b-c, c-d   back: c-a, e-e\nforward: a-d   cross: e-d',
        off={'c': (0, -0.38), 'd': (0, -0.38), 'e': (0, 0.38)})
    assert kinds == {('a', 'b'): 'tree', ('b', 'c'): 'tree', ('c', 'a'): 'back', ('c', 'd'): 'tree',
                     ('a', 'd'): 'forward', ('e', 'd'): 'cross', ('e', 'e'): 'back'}


# ---------- lesson 6.0: connected components ----------

class UF:
    def __init__(self, items):
        self.p = {x: x for x in items}
        self.count = len(self.p)

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.p[rb] = ra
        self.count -= 1
        return True

    def groups(self):
        out = {}
        for x in self.p:
            out.setdefault(self.find(x), []).append(x)
        return sorted(sorted(g) for g in out.values())


def component_colours(groups, order):
    """Stable colours: a group takes the colour of its first member in `order`."""
    col = {}
    for i, grp in enumerate(sorted(groups, key=lambda g: min(order.index(v) for v in g))):
        for v in grp:
            col[v] = COMP_FILLS[i % len(COMP_FILLS)]
    return col


def stable_colours(groups, order):
    """A group takes the colour of its earliest member, so colours do not jump between step pictures."""
    return {v: COMP_FILLS[min(order.index(w) for w in grp) % len(COMP_FILLS)] for grp in groups for v in grp}


def uf_frames(verts, pos, edge_seq, name, title, cols=2, w=4.6, h=3.0, box=True, cap_dy=-0.5, cx=None):
    uf = UF(verts)
    g = G()
    frames = [(None, None, list(edge_seq[:0]))]
    for i, e in enumerate(edge_seq):
        frames.append((e, uf.union(*e), list(edge_seq[:i + 1])))
    uf = UF(verts)
    for k, (e, merged, done) in enumerate(frames):
        if e:
            uf.union(*e)
        dx, dy = (k % cols) * w, -(k // cols) * h
        col = stable_colours(uf.groups(), verts)
        for v, (x, y) in pos.items():
            extra = dict(shape='box', style='filled', width=0.95, height=0.36, fontsize=12) if box else {}
            g.node(f'{v}#{k}', x + dx, y + dy, label=v, fillcolor=col[v], **extra)
        seen = set()
        for j, (a, b) in enumerate(done):
            key = frozenset((a, b))
            last = j == len(done) - 1
            if last and not merged:
                g.edge(f'{a}#{k}', f'{b}#{k}', color=TRUE, penwidth=2.5, style='dashed')
            elif key in seen:
                continue
            else:
                g.edge(f'{a}#{k}', f'{b}#{k}', **(dict(color=ORANGE, penwidth=3.5) if last else {}))
            seen.add(key)
        if e is None:
            cap = f'Start: {len(verts)} components'
        else:
            cap = f'{e[0]}-{e[1]}: ' + ('merged' if merged else 'redundant') + f', {uf.count} components'
        g.text(f'cap{k}', dx + (cx if cx is not None else 1.0), dy + cap_dy, cap, 12)
    g.save(name, title)
    return uf


def lesson_components():
    teams = ['platform', 'payments', 'fraud', 'design', 'brand', 'legal', 'research']
    meetings = [('platform', 'payments'), ('payments', 'fraud'), ('design', 'brand')]
    comps = components(teams, meetings)
    assert sorted(comps) == [['brand', 'design'], ['fraud', 'payments', 'platform'], ['legal'], ['research']]
    pos = {'platform': (0, 1.6), 'payments': (1.4, 1.6), 'fraud': (2.8, 1.6), 'design': (0, 0.8),
           'brand': (1.4, 0.8), 'legal': (0, 0), 'research': (1.4, 0)}
    col = stable_colours(comps, teams)
    g = G()
    for v, (x, y) in pos.items():
        g.node(v, x, y, fillcolor=col[v], shape='box', style='rounded,filled', width=0.95, height=0.36, fontsize=12)
    for a, b in meetings:
        g.edge(a, b, penwidth=2)
    g.text('cap', 1.4, -0.55, '4 components: one colour each.\nlegal and research are components of one.', 12)
    g.save('graph-cc-teams.svg',
           'Seven teams as vertices and three meetings as edges: platform-payments-fraud in blue, design-brand in '
           'pink, legal alone in orange and research alone in grey, making 4 components.')

    seq = meetings + [('payments', 'platform')]
    uf = uf_frames(teams, pos, seq, 'graph-cc-union-steps.svg',
                   'Union-find on the teams, one frame per edge: start with 7 components; platform-payments merges '
                   '(6); payments-fraud merges (5); design-brand merges (4); payments-platform is redundant, shown '
                   'dashed red, and the count stays 4.', cols=2, w=4.0, h=2.6, cx=1.4)
    assert uf.count == 4

    # Weak vs strong on a->b, b->c, c->a, c->d, d->e, e->d.
    dverts = ['a', 'b', 'c', 'd', 'e']
    dedges = [('a', 'b'), ('b', 'c'), ('c', 'a'), ('c', 'd'), ('d', 'e'), ('e', 'd')]
    weak = components(dverts, dedges)
    strong = sccs(dverts, dedges)
    assert len(weak) == 1 and strong == [['a', 'b', 'c'], ['d', 'e']]
    dpos = {'a': (0, 1), 'b': (0, 0), 'c': (0.9, 0.5), 'd': (1.9, 0.5), 'e': (2.9, 0.5)}
    g = G(directed=True)
    for k, (groups, cap) in enumerate([(weak, 'Weak (ignore arrows): 1 component'),
                                       (strong, 'Strong (follow arrows): 2 SCCs')]):
        dy = -k * 2.0
        cid = {v: i for i, gr in enumerate(groups) for v in gr}
        for v, (x, y) in dpos.items():
            g.node(f'{v}{k}', x, y + dy, label=v, fillcolor=COMP_FILLS[cid[v]])
        for a, b in dedges:
            g.edge(f'{a}{k}', f'{b}{k}')
        g.text(f'c{k}', 1.45, dy - 0.55, cap, 12)
    g.save('graph-cc-weak-strong.svg',
           'The directed graph a to b to c to a, c to d, d and e pointing at each other, drawn twice. Top, weakly '
           'connected: all five vertices one colour. Bottom, strongly connected components: a, b, c in blue and d, e '
           'in green, because d and e cannot get back to c.')

    # Sketch answer.
    sverts = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    sseq = [('A', 'B'), ('C', 'D'), ('B', 'C'), ('E', 'F'), ('A', 'D')]
    uf = UF(sverts)
    merged = [uf.union(*e) for e in sseq]
    assert merged == [True, True, True, True, False] and uf.count == 4
    assert uf.groups() == [['A', 'B', 'C', 'D'], ['E', 'F'], ['G'], ['H']]
    spos = {'A': (0, 1), 'B': (1, 1), 'C': (1, 0), 'D': (0, 0), 'E': (2.1, 1), 'F': (2.1, 0), 'G': (3.1, 1),
            'H': (3.1, 0)}
    col = component_colours(uf.groups(), sverts)
    g = G()
    for v, (x, y) in spos.items():
        g.node(v, x, y, fillcolor=col[v])
    for a, b in sseq[:-1]:
        g.edge(a, b, penwidth=2)
    g.edge('A', 'D', color=TRUE, style='dashed', penwidth=2.5)
    g.text('cap', 1.55, -0.6, '8 - 4 merges = 4 components.\nA-D (dashed red) was redundant: it closes a cycle.', 12)
    g.save('graph-sketch-components.svg',
           'Answer: four components, {A, B, C, D} in blue, {E, F} in green, G alone and H alone. The edge A-D is '
           'dashed red because A and D were already connected through B and C.')


# ---------- lesson 6.1: topological sort ----------

def kahn_steps(adj):
    """Kahn's algorithm with a FIFO queue seeded in sorted order. Returns order and a snapshot per step:
    (taken, queue after, remaining in-degrees, unlocked)."""
    indeg = {v: 0 for v in adj}
    for u in adj:
        for v in adj[u]:
            indeg[v] += 1
    qu = deque(sorted(v for v in adj if indeg[v] == 0))
    snaps = [(None, list(qu), dict(indeg), [])]
    order = []
    while qu:
        v = qu.popleft()
        order.append(v)
        unlocked = []
        for w in adj[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                qu.append(w)
                unlocked.append(w)
        snaps.append((v, list(qu), dict(indeg), unlocked))
    return order, snaps


def all_topo_orders(adj):
    from itertools import permutations
    out = []
    for p in permutations(sorted(adj)):
        ix = {v: i for i, v in enumerate(p)}
        if all(ix[u] < ix[v] for u in adj for v in adj[u]):
            out.append(list(p))
    return out


def order_line(adj, order, name, title, caption, box=None):
    """Lay the vertices out in `order` on one row (dot, invisible chain) and draw every edge; all point right."""
    box = box or {}
    attrs = ', '.join(f'{k}="{q(v)}"' for k, v in box.items())
    lines = ['digraph { bgcolor="white"; pad=0.2; rankdir=LR; nodesep=0.25; ranksep=0.35;',
             f'node [fontname="{FONT}", fontsize=14, shape=circle, style=filled, fillcolor="{DONE_FILL}", '
             f'color="{INK}", penwidth=1.3, width=0.42, height=0.42, fixedsize=true];',
             f'edge [color="{INK}", penwidth=1.3, arrowsize=0.8];']
    for v in order:
        lines.append(f'"{q(v)}" [{attrs}];' if attrs else f'"{q(v)}";')
    for a, b in zip(order, order[1:]):
        lines.append(f'"{q(a)}" -> "{q(b)}" [style=invis, weight=100];')
    for u in adj:
        for v in adj[u]:
            adjacent = order.index(v) - order.index(u) == 1
            lines.append(f'"{q(u)}" -> "{q(v)}"' + ('' if adjacent else ' [constraint=false]') + ';')
    lines.append(f'labelloc=b; label="{q(caption)}"; fontname="{FONT}"; fontsize=12; fontcolor="{INK}";')
    lines.append('}')
    save_graph('\n'.join(lines), name, title, engine='dot')


def kahn_frames(adj, pos, name, title, box, cols=2, w=4.0, h=2.8, cx=1.5, cap_dy=-0.75, off=None):
    off = off or {}
    order, snaps = kahn_steps(adj)
    g = G(directed=True)
    for k, (taken, qu, indeg, unlocked) in enumerate(snaps):
        dx, dy = (k % cols) * w, -(k // cols) * h
        placed = order[:k]
        for v, (x, y) in pos.items():
            a = dict(box)
            if v in placed:
                a['fillcolor'] = DONE_FILL
            elif v in qu:
                a['fillcolor'] = FRONT_FILL
            if v == taken:
                a.update(color=ORANGE, penwidth=3)
            g.node(f'{v}#{k}', x + dx, y + dy, label=v, **a)
            if v not in placed:
                num_label(g, f'n{v}#{k}', x + dx, y + dy, f'in {indeg[v]}', off.get(v, (0, 0.33)))
        for u in adj:
            for v in adj[u]:
                g.edge(f'{u}#{k}', f'{v}#{k}', **(dict(color=GREY, style='dashed') if u in placed else {}))
        if taken is None:
            cap = f'Start. Queue: {" ".join(qu)}'
        else:
            cap = f'Step {k}: take {taken}. Queue: {" ".join(qu) if qu else "(empty)"}'
        g.text(f'cap{k}', dx + cx, dy + cap_dy, cap, 12)
    g.save(name, title)
    return order, snaps


def lesson_topo():
    dress = {'Underwear': ['Pants'], 'Socks': ['Pants'], 'Pants': ['Shoes'], 'Shoes': []}
    orders = all_topo_orders(dress)
    assert orders == [['Socks', 'Underwear', 'Pants', 'Shoes'], ['Underwear', 'Socks', 'Pants', 'Shoes']]
    box = dict(shape='box', style='rounded,filled', width=1.1, height=0.4, fontsize=13)
    g = G(directed=True)
    for v, (x, y) in {'Underwear': (0, 1), 'Socks': (0, 0), 'Pants': (1.7, 0.5), 'Shoes': (3.4, 0.5)}.items():
        g.node(v, x, y, **box)
    for u in dress:
        for v in dress[u]:
            g.edge(u, v)
    g.text('cap', 1.7, -0.55, 'Underwear and Socks both point to Pants, so either can go first.', 12)
    g.save('graph-topo-dressing.svg',
           'Getting dressed as a DAG: Underwear to Pants, Socks to Pants, and Pants to Shoes.')

    courses = {'intro': ['data-structures', 'discrete-math'], 'data-structures': ['algorithms'],
               'discrete-math': ['algorithms'], 'algorithms': ['compilers'], 'compilers': []}
    pos = {'intro': (0, 1), 'data-structures': (1.5, 1.6), 'discrete-math': (1.5, 0.4), 'algorithms': (3.0, 1),
           'compilers': (3.0, -0.1)}
    box = dict(shape='box', style='filled', width=1.3, height=0.34, fontsize=11)
    order, snaps = kahn_frames(courses, pos, 'graph-topo-kahn-steps.svg',
                               "Kahn's algorithm on the course graph, one frame per step, each vertex showing its "
                               "remaining in-degree: start with only intro at 0; take intro, unlocking "
                               "data-structures and discrete-math; take data-structures; take discrete-math, "
                               "unlocking algorithms; take algorithms, unlocking compilers; take compilers.",
                               box, off={v: ((0.95, 0) if v == 'compilers' else (0, 0.3)) for v in pos}, w=4.6, h=2.9, cx=1.5,
                               cap_dy=-0.65)
    assert order == ['intro', 'data-structures', 'discrete-math', 'algorithms', 'compilers']
    assert snaps[0][2] == {'algorithms': 2, 'compilers': 1, 'data-structures': 1, 'discrete-math': 1, 'intro': 0}
    assert [sn[3] for sn in snaps[1:]] == [['data-structures', 'discrete-math'], [], ['algorithms'],
                                          ['compilers'], []]

    order_line(courses, order, 'graph-topo-order-line.svg',
               "The course graph laid out in Kahn's order, intro, data-structures, discrete-math, algorithms, "
               "compilers, with every prerequisite arrow pointing to the right.",
               "Kahn's order in a row: every arrow points to the right.",
               box=dict(shape='box', style='rounded,filled', width=1.45, height=0.36, fontsize=11))

    # Sketch answer.
    sadj = {'D': ['A'], 'C': ['A', 'B'], 'A': ['E'], 'B': ['E'], 'E': ['F'], 'F': []}
    order, snaps = kahn_steps(sadj)
    assert order == ['C', 'D', 'B', 'A', 'E', 'F']
    order_line(sadj, order, 'graph-sketch-topo.svg',
           "Answer: the vertices in Kahn's order C, D, B, A, E, F on one row, with the edges C to A, C to B, D to A, "
           "A to E, B to E and E to F all pointing to the right.",
               'Kahn order: C, D, B, A, E, F. Every arrow points right.')


# ---------- lesson 6.2: Dijkstra ----------

def wadj(edges, directed=False):
    adj = {}
    for u, v, w in edges:
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, [])
        if not directed:
            adj[v].append((u, w))
    return adj


def dijkstra_rounds(adj, src):
    """Lazy-deletion Dijkstra. One snapshot per settled vertex: (settled vertex, settled list, dist, parent)."""
    dist, parent, done, pq, rounds = {src: 0}, {src: None}, [], [(0, src)], []
    while pq:
        d, v = heapq.heappop(pq)
        if v in done:
            continue
        done.append(v)
        for w, wt in adj[v]:
            if w in done:
                continue
            if w not in dist or d + wt < dist[w]:
                dist[w] = d + wt
                parent[w] = v
                heapq.heappush(pq, (d + wt, w))
        rounds.append((v, list(done), dict(dist), dict(parent)))
    return dist, parent, rounds


def fmt_d(x):
    return '∞' if x is None or x == INF else str(x)


def weighted_frames(pos, edges, frames, name, title, cols=2, w=5.0, h=3.0, cap_dy=-0.65, cx=2.1, off=None,
                    directed=False):
    """frames: dicts with settled (list), new, dist (dict), tree (set of frozenset), caption, relaxed (set)."""
    g = G(directed)
    for k, fr in enumerate(frames):
        dx, dy = (k % cols) * w, -(k // cols) * h
        for v, (x, y) in pos.items():
            a = {}
            if v in fr['settled']:
                a['fillcolor'] = DONE_FILL
            elif fr['dist'].get(v, INF) != INF:
                a['fillcolor'] = FRONT_FILL
            if v == fr.get('new'):
                a.update(color=ORANGE, penwidth=3)
            g.node(f'{v}#{k}', x + dx, y + dy, label=v, **a)
            num_label(g, f'n{v}#{k}', x + dx, y + dy, fmt_d(fr['dist'].get(v)), (off or {}).get(v, (0, 0.36)),
                      color='#b45309' if v not in fr['settled'] else '#047857')
        for u, v, wt in edges:
            st = dict(color=PIX, penwidth=3) if frozenset((u, v)) in fr['tree'] else dict(color=GREY)
            g.edge(f'{u}#{k}', f'{v}#{k}', label=wt, **st)
        g.text(f'cap{k}', dx + cx, dy + cap_dy, fr['caption'], 12)
    g.save(name, title)


def dist_table(verts, rows, name, title, row_head='Settle', note=None):
    """rows: list of (row label, {v: value}, highlight vertex or None, settled set)."""
    cw, ch, lw = 44, 28, 96
    width = max(lw + cw * len(verts) + 30, int(len(note or '') * 6.3) + 30)
    sv = Svg(width, 40 + ch * (len(rows) + 1) + (26 if note else 6), title)
    x0, y0 = (width - (lw + cw * len(verts))) / 2, 15
    sv.text(x0 + lw / 2, y0 + 19, row_head, 12, weight='bold')
    for j, v in enumerate(verts):
        sv.text(x0 + lw + cw * j + cw / 2, y0 + 19, v, 13, weight='bold')
    for i, (lab, vals, hi, settled) in enumerate(rows):
        y = y0 + ch * (i + 1)
        sv.text(x0 + 6, y + 19, lab, 12, anchor='start')
        for j, v in enumerate(verts):
            x = x0 + lw + cw * j
            fill = '#ffffff'
            if v in settled:
                fill = DONE_FILL
            if v == hi:
                fill = '#fde68a'
            sv.rect(x, y, cw, ch, fill, stroke='#d1d5db')
            val = vals.get(v)
            sv.text(x + cw / 2, y + 19, fmt_d(val), 13, color=INK if val not in (None, INF) else '#9ca3af',
                    weight='bold' if v == hi else 'normal')
    if note:
        sv.text(sv.w / 2, sv.h - 10, note, 12, color='#374151')
    sv.save(name, OUT)


def lesson_dijkstra():
    # GPS motivation.
    gps = [('A', 'B', 90), ('A', 'C', 15), ('C', 'B', 15)]
    dist, parent, _ = dijkstra_rounds(wadj(gps, directed=True), 'A')
    assert dist['B'] == 30 and parent['B'] == 'C'
    g = G(directed=True)
    box = dict(shape='box', style='rounded,filled', width=1.1, height=0.4, fontsize=12)
    g.node('A', 0, 1, label='City A', **box)
    g.node('B', 3.6, 1, label='City B', **box)
    g.node('C', 1.8, 0, label='Village C', **box)
    g.edge('A', 'B', label='highway, 90 min', color=GREY)
    g.edge('A', 'C', label='local road, 15 min', color=ACCENT, penwidth=3)
    g.edge('C', 'B', label='local road, 15 min', color=ACCENT, penwidth=3)
    g.text('cap', 1.8, -0.6, 'BFS takes the 1-hop highway (90 min).\nDijkstra adds up minutes: through C is 30 min.', 12)
    g.save('graph-dijkstra-gps.svg',
           'City A to City B: a direct highway costing 90 minutes, or two local roads through Village C costing 15 '
           'minutes each. The green route through C totals 30 minutes and is the one Dijkstra picks.')

    edges = [('A', 'B', 4), ('A', 'C', 2), ('B', 'C', 1), ('B', 'D', 5), ('C', 'D', 8), ('C', 'E', 10),
             ('D', 'E', 2), ('D', 'F', 6), ('E', 'F', 3)]
    adj = wadj(edges)
    dist, parent, rounds = dijkstra_rounds(adj, 'A')
    assert dist == {'A': 0, 'B': 3, 'C': 2, 'D': 8, 'E': 10, 'F': 13}
    assert [r[0] for r in rounds] == ['A', 'C', 'B', 'D', 'E', 'F']
    pos = {'A': (0, 1), 'B': (1.5, 2), 'C': (1.5, 0), 'D': (3.0, 2), 'E': (3.0, 0), 'F': (4.5, 1)}
    off = {'A': (-0.45, 0), 'B': (0, 0.36), 'C': (0, -0.36), 'D': (0, 0.36), 'E': (0, -0.36), 'F': (0.45, 0)}
    frames = []
    for v, done, dd, par in rounds:
        frames.append({'settled': done, 'new': v, 'dist': dd, 'tree': tree_edges_of(par),
                       'caption': f'Round {len(done)}: settle {v} at {dd[v]}'})
    weighted_frames(pos, edges, frames, 'graph-dijkstra-steps.svg',
                    'Dijkstra from A on the lab graph, one frame per settled vertex, with each vertex showing its '
                    'current best distance: settle A at 0, C at 2, B at 3 (via C, not the direct 4), D at 8, E at 10 '
                    'and F at 13. Blue edges are the current shortest-path tree.', off=off, w=6.0, h=3.3)

    verts = ['A', 'B', 'C', 'D', 'E', 'F']
    rows = [('start', {'A': 0}, None, set())]
    for v, done, dd, par in rounds:
        rows.append((f'{len(done)}. settle {v}', dd, v, set(done)))
    dist_table(verts, rows, 'graph-dijkstra-table.svg',
               'Dijkstra distance table from A, one row per round. After settling A: B 4, C 2. After C: B improves '
               'to 3, D 10, E 12. After B: D improves to 8. After D: E improves to 10, F 14. After E: F improves to '
               '13. Final: A 0, B 3, C 2, D 8, E 10, F 13.',
               note='Yellow: settled this round. Green: settled earlier, never changes again.')
    assert rows[1][1] == {'A': 0, 'B': 4, 'C': 2} and rows[2][1]['B'] == 3 and rows[3][1]['D'] == 8

    # Negative edge: Dijkstra settles B at 0 too early.
    neg = [('A', 'B', 0), ('A', 'C', 1), ('C', 'B', -10)]
    d, _, rr = dijkstra_rounds(wadj(neg, directed=True), 'A')
    assert d['B'] == 0 and [r[0] for r in rr] == ['A', 'B', 'C']
    g = G(directed=True)
    for v, (x, y) in {'A': (0, 1), 'B': (2.2, 1), 'C': (1.1, 0)}.items():
        g.node(v, x, y, fillcolor=DONE_FILL)
    g.edge('A', 'B', label=0, color=PIX, penwidth=3)
    g.edge('A', 'C', label=1)
    g.edge('C', 'B', label=-10, color=TRUE, penwidth=2.5, fontcolor=TRUE)
    num_label(g, 'nB', 2.2, 1, 'settled at 0 (wrong)', (0, 0.36), color=TRUE)
    num_label(g, 'nA', 0, 1, '0', (0, 0.36), color='#047857')
    num_label(g, 'nC', 1.1, 0, '1', (0, -0.36), color='#047857')
    g.text('cap', 1.1, -0.85, 'True cost of A to C to B: 1 + (-10) = -9.\nB was already settled, so Dijkstra never looks again.',
           12)
    g.save('graph-dijkstra-negative.svg',
           'A directed graph with A to B weight 0, A to C weight 1 and C to B weight -10. Dijkstra settles B at 0 '
           'first, but the route A to C to B costs -9, so its answer is wrong.')

    # Sketch answer.
    sedges = [('S', 'A', 7), ('S', 'B', 2), ('B', 'A', 3), ('A', 'C', 1), ('B', 'D', 8), ('C', 'D', 2),
              ('C', 'E', 6), ('D', 'E', 1)]
    d, par, rr = dijkstra_rounds(wadj(sedges), 'S')
    assert d == {'S': 0, 'B': 2, 'A': 5, 'C': 6, 'D': 8, 'E': 9}
    assert [r[0] for r in rr] == ['S', 'B', 'A', 'C', 'D', 'E']
    spos = {'S': (0, 1), 'A': (1.5, 2), 'B': (1.5, 0), 'C': (3.0, 2), 'D': (3.0, 0), 'E': (4.5, 1)}
    soff = {'S': (-0.45, 0), 'A': (0, 0.36), 'B': (0, -0.36), 'C': (0, 0.36), 'D': (0, -0.36), 'E': (0.45, 0)}
    weighted_frames(spos, sedges, [{'settled': list(d), 'dist': d, 'tree': tree_edges_of(par),
                                    'caption': 'Settle order: S, B, A, C, D, E'}],
                    'graph-sketch-dijkstra.svg',
                    'Answer: shortest distances from S are B 2, A 5, C 6, D 8, E 9. The shortest-path tree in blue is '
                    'S-B, B-A, A-C, C-D, D-E.', cols=1, off=soff, cx=2.25)


# ---------- lesson 6.3: Bellman-Ford ----------

def bf_trace(verts, edge_order, src, rounds=None):
    """Bellman-Ford over an explicit edge order. Returns per-round distance snapshots and per-relaxation steps."""
    dist = {v: INF for v in verts}
    parent = {v: None for v in verts}
    dist[src] = 0
    snaps, steps = [dict(dist)], []
    for r in range(rounds or len(verts) - 1):
        changed = False
        for u, v, w in edge_order:
            improved = dist[u] != INF and dist[u] + w < dist[v]
            if improved:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
            steps.append((r + 1, (u, v, w), improved, dict(dist), dict(parent)))
        snaps.append(dict(dist))
        if not changed:
            break
    neg = any(dist[u] != INF and dist[u] + w < dist[v] for u, v, w in edge_order)
    return snaps, steps, dist, parent, neg


def lesson_bellman():
    trap = [('S', 'A', 1), ('S', 'B', 5), ('A', 'C', 2), ('B', 'C', -4)]
    verts = ['S', 'A', 'B', 'C']
    pos = {'S': (0, 1), 'A': (1.5, 1), 'C': (3.0, 1), 'B': (1.5, 0)}
    off = {'S': (-0.45, 0), 'A': (0, 0.36), 'C': (0.45, 0), 'B': (0, -0.36)}
    # Dijkstra's (wrong) answer and the real one.
    d_dij, _, _ = dijkstra_rounds(wadj(trap, directed=True), 'S')
    snaps, steps, dist, parent, neg = bf_trace(verts, trap, 'S')
    assert dist == {'S': 0, 'A': 1, 'B': 5, 'C': 1} and not neg and len(snaps) == 3   # round 2 changes nothing
    g = G(directed=True)
    for v, (x, y) in pos.items():
        g.node(v, x, y)
    for u, v, w in trap:
        g.edge(u, v, label=w, **(dict(color=TRUE, penwidth=2.5, fontcolor=TRUE) if w < 0 else {}))
    g.text('cap', 1.5, -0.6, 'S to A to C costs 3. S to B to C costs 5 + (-4) = 1.', 12)
    g.save('graph-bf-trap.svg',
           'The trap graph: S to A weight 1, A to C weight 2, S to B weight 5, and B to C weight -4 in red. The '
           'route through B reaches C for 1, cheaper than 3 through A.')

    frames = []
    for r, (u, v, w), improved, dd, par in steps:
        what = f'{v} = {dd[v]}' if improved else 'no change'
        frames.append({'settled': [], 'new': v if improved else None, 'dist': dd,
                       'tree': {frozenset((a, b)) for b, a in par.items() if a},
                       'caption': f'Round {r}: relax {u}→{v} ({w}): {what}'})
    assert [f['caption'] for f in frames[:4]] == ['Round 1: relax S→A (1): A = 1', 'Round 1: relax S→B (5): B = 5',
                                                 'Round 1: relax A→C (2): C = 3', 'Round 1: relax B→C (-4): C = 1']
    # Only show round 1 in detail; round 2 changes nothing.
    frames = frames[:4]
    weighted_frames(pos, trap, frames, 'graph-bf-round1.svg',
                    'Bellman-Ford round 1 on the trap graph, one frame per edge relaxed in order: S to A sets A to 1; '
                    'S to B sets B to 5; A to C sets C to 3; B to C lowers C to 1. Nothing is ever finalised, so C '
                    'can still drop. Round 2 changes nothing and the algorithm stops.', off=off, w=4.3, h=2.6,
                    cx=1.5, cap_dy=-0.75, directed=True)

    # The chain in reverse edge order: one vertex per round.
    chain = ['v0', 'v1', 'v2', 'v3', 'v4']
    rev = [(f'v{i}', f'v{i + 1}', 1) for i in range(3, -1, -1)]
    snaps, _, dist, _, _ = bf_trace(chain, rev, 'v0')
    assert [sum(1 for v in sn.values() if v != INF) for sn in snaps] == [1, 2, 3, 4, 5]
    rows = [('start', snaps[0], None, set())]
    for r in range(1, 5):
        newv = f'v{r}'
        rows.append((f'round {r}', snaps[r], newv, {f'v{i}' for i in range(r)}))
    dist_table(chain, rows, 'graph-bf-chain.svg',
               'Bellman-Ford on the chain v0 to v1 to v2 to v3 to v4 with the edges relaxed in reverse order: after '
               'round 1 only v1 is known (1), after round 2 v2 (2), after round 3 v3 (3), after round 4 v4 (4).',
               row_head='After', note='Edges relaxed last-first: each round reaches just one more vertex.')

    # The negative cycle.
    negc = trap + [('C', 'B', -1)]
    snaps, steps, dist, parent, neg = bf_trace(verts, negc, 'S')
    assert neg and dist == {'S': 0, 'A': 1, 'B': -10, 'C': -9}
    g = G(directed=True)
    for v, (x, y) in pos.items():
        g.node(v, x, y, **({'fillcolor': '#fecaca'} if v in 'BC' else {}))
        num_label(g, 'n' + v, x, y, str(dist[v]), off[v], color=TRUE if v in 'BC' else '#047857')
    for u, v, w in negc:
        hot = (u, v) in {('B', 'C'), ('C', 'B')}
        g.edge(u, v, label=w, **(dict(color=TRUE, penwidth=2.5, fontcolor=TRUE) if hot else {}))
    g.text('cap', 1.5, -0.8, 'B to C to B costs -4 + (-1) = -5. Each lap lowers B and C again,\n'
                             'so after V-1 = 3 rounds they are just "how far it got": B -10, C -9.', 12)
    g.save('graph-bf-negative-cycle.svg',
           'The trap graph plus C to B weight -1. The red cycle B to C to B costs -5, so the distances to B and C '
           'keep falling; after 3 rounds they stand at B -10 and C -9, and the extra pass still finds an edge to '
           'relax.')

    # Sketch answer: round table for a fresh graph and edge order.
    sv = ['S', 'A', 'B', 'C', 'D']
    order = [('C', 'D', 2), ('B', 'C', -3), ('A', 'B', 4), ('S', 'A', 1), ('S', 'B', 6), ('A', 'C', 5)]
    snaps, _, dist, _, neg = bf_trace(sv, order, 'S')
    assert not neg and len(snaps) == 5
    assert snaps[1] == {'S': 0, 'A': 1, 'B': 6, 'C': 6, 'D': INF}
    assert snaps[2] == {'S': 0, 'A': 1, 'B': 5, 'C': 3, 'D': 8}
    assert snaps[3] == {'S': 0, 'A': 1, 'B': 5, 'C': 2, 'D': 5}
    assert snaps[4] == {'S': 0, 'A': 1, 'B': 5, 'C': 2, 'D': 4}
    rows = [('start', snaps[0], None, set())]
    for r in range(1, 5):
        rows.append((f'round {r}', snaps[r], None, {v for v in sv if snaps[r][v] != snaps[r - 1][v]}))
    dist_table(sv, rows, 'graph-sketch-bf.svg',
               'Answer table, distances after each round: round 1 A 1, B 6, C 6, D infinity; round 2 B 5, C 3, D 8; '
               'round 3 C 2, D 5; round 4 D 4. Green cells changed in that round.',
               row_head='After', note='Green: changed in this round. Final: A 1, B 5, C 2, D 4.')


# ---------- lesson 6.4: Floyd-Warshall ----------

def floyd_rounds(verts, edges):
    d = {u: {v: (0 if u == v else INF) for v in verts} for u in verts}
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    snaps = [({u: dict(r) for u, r in d.items()}, None, set())]
    for k in verts:
        changed = set()
        for i in verts:
            for j in verts:
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
                    changed.add((i, j))
        snaps.append(({u: dict(r) for u, r in d.items()}, k, changed))
    return snaps


def dmatrix(sv, x0, y0, verts, d, title, changed=(), k=None, cell=34):
    sv.text(x0 + cell * (len(verts) + 1) / 2, y0 - 8, title, 13, weight='bold')
    for j, v in enumerate(verts):
        sv.text(x0 + cell * (j + 1.5), y0 + cell * 0.65, v, 12, weight='bold',
                color=ORANGE if v == k else INK)
    for i, u in enumerate(verts):
        y = y0 + cell * (i + 1)
        sv.text(x0 + cell * 0.5, y + cell * 0.65, u, 12, weight='bold', color=ORANGE if u == k else INK)
        for j, v in enumerate(verts):
            x = x0 + cell * (j + 1)
            fill = '#ffffff'
            if k is not None and (u == k or v == k):
                fill = '#f3f4f6'
            if (u, v) in changed:
                fill = '#fde68a'
            sv.rect(x, y, cell, cell, fill, stroke='#d1d5db')
            val = d[u][v]
            sv.text(x + cell / 2, y + cell * 0.65, fmt_d(val), 13, color='#9ca3af' if val == INF else INK,
                    weight='bold' if (u, v) in changed else 'normal')


def lesson_floyd():
    verts = ['A', 'B', 'C', 'D']
    edges = [('A', 'B', 3), ('A', 'D', 7), ('B', 'A', 8), ('B', 'C', 2), ('C', 'A', 5), ('C', 'D', 1), ('D', 'A', 2)]
    snaps = floyd_rounds(verts, edges)
    init, final = snaps[0][0], snaps[-1][0]
    rows = lambda d: [[d[u][v] for v in verts] for u in verts]
    assert rows(init) == [[0, 3, INF, 7], [8, 0, 2, INF], [5, INF, 0, 1], [2, INF, INF, 0]]
    assert rows(snaps[1][0]) == [[0, 3, INF, 7], [8, 0, 2, 15], [5, 8, 0, 1], [2, 5, INF, 0]]
    assert rows(final) == [[0, 3, 5, 6], [5, 0, 2, 3], [3, 6, 0, 1], [2, 5, 7, 0]]

    pos = {'A': (0, 1.6), 'B': (1.8, 1.6), 'C': (1.8, 0), 'D': (0, 0)}
    g = G(directed=True)
    g.splines = 'curved'
    for v, (x, y) in pos.items():
        g.node(v, x, y)
    for u, v, w in edges:
        g.edge(u, v, label=w)
    g.save('graph-fw-graph.svg',
           'The four-vertex directed graph from the lab: A to B 3, A to D 7, B to A 8, B to C 2, C to A 5, C to D 1 '
           'and D to A 2.')

    sv = Svg(205, 200, 'Initial distance matrix, no intermediates allowed: row A is 0, 3, infinity, 7; row B is 8, '
                       '0, 2, infinity; row C is 5, infinity, 0, 1; row D is 2, infinity, infinity, 0.')
    dmatrix(sv, 15, 25, verts, init, 'Initial: direct edges only')
    sv.save('graph-fw-initial.svg', OUT)

    allchanged = {(u, v) for u in verts for v in verts if final[u][v] != init[u][v]}
    sv = Svg(205, 220, 'Final distance matrix: row A is 0, 3, 5, 6; row B is 5, 0, 2, 3; row C is 3, 6, 0, 1; row '
                       'D is 2, 5, 7, 0. The yellow cells are the ones that differ from the direct edges.')
    dmatrix(sv, 15, 25, verts, final, 'Final', changed=allchanged)
    sv.text(102, 210, 'Yellow: found via intermediates', 12, color='#374151')
    sv.save('graph-fw-final.svg', OUT)

    cell = 30
    mw = cell * 5 + 20
    sv = Svg(2 * mw + 30, 2 * (cell * 5 + 40) + 30,
             'The distance matrix after each round of k. After k = A: B to D becomes 15, C to B 8, D to B 5. After '
             'k = B: A to C becomes 5, D to C 7. After k = C: A to D becomes 6, B to A 7, B to D 3, D to... After '
             'k = D: B to A becomes 5 and C to A 3. Yellow cells changed in that round; the grey row and column '
             'belong to k.')
    for n, (d, k, ch) in enumerate(snaps[1:]):
        x0 = 15 + (n % 2) * (mw + 15)
        y0 = 25 + (n // 2) * (cell * 5 + 40)
        dmatrix(sv, x0, y0, verts, d, f'After k = {k}', changed=ch, k=k, cell=cell)
    sv.text(sv.w / 2, sv.h - 10, 'Yellow: improved this round. Grey: the row and column of k.', 12, color='#374151')
    # Build an exact title from the computed changes.
    parts = []
    for d, k, ch in snaps[1:]:
        items = ', '.join(f'{i} to {j} {d[i][j]}' for i, j in sorted(ch))
        parts.append(f'after k = {k}: {items}')
    sv.title = ('The distance matrix after each round of k; yellow cells changed in that round: ' + '; '.join(parts)
                + '.')
    sv.save('graph-fw-rounds.svg', OUT)

    # Sketch answer.
    sv3 = ['P', 'Q', 'R']
    sedges = [('P', 'Q', 4), ('Q', 'R', 1), ('R', 'P', 2), ('P', 'R', 9)]
    ss = floyd_rounds(sv3, sedges)
    si, sf = ss[0][0], ss[-1][0]
    assert [[sf[u][v] for v in sv3] for u in sv3] == [[0, 4, 5], [3, 0, 1], [2, 6, 0]]
    ch = {(u, v) for u in sv3 for v in sv3 if sf[u][v] != si[u][v]}
    svg = Svg(330, 200, 'Answer: initial matrix rows P 0, 4, 9; Q infinity, 0, 1; R 2, infinity, 0. Final matrix rows '
                        'P 0, 4, 5; Q 3, 0, 1; R 2, 6, 0, with P to R, Q to P and R to Q improved.')
    dmatrix(svg, 15, 25, sv3, si, 'Initial', cell=34)
    dmatrix(svg, 175, 25, sv3, sf, 'Final', changed=ch, cell=34)
    svg.text(165, 190, 'Yellow: improved by going through another vertex', 12, color='#374151')
    svg.save('graph-sketch-fw.svg', OUT)


# ---------- lesson 6.5: A* ----------

ASTAR_MAIN = [
    "S.........#.........",
    ".........##.........",
    "........##..........",
    ".......##...........",
    "......##............",
    ".....##.............",
    "....##..............",
    "...##...............",
    "..##................",
    ".##.................",
    ".......#############",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "....................",
    "..................G.",
]
ASTAR_TRAP = [
    ".#.......#...",
    ".#.#....##...",
    "#.##........#",
    "...##......##",
    "S......##..#G",
    "........#..#.",
    ".....#.....#.",
    ".#...#.......",
    "....#..#.##..",
]


def astar_grid(rows, h, tie='none', weight=1.0):
    """The lab's search(), copied exactly (same heap keys), so the expansion counts match the lesson."""
    R, C = len(rows), len(rows[0])
    find = lambda ch: next((r, c) for r in range(R) for c in range(C) if rows[r][c] == ch)
    start, goal = find('S'), find('G')

    def nbrs(pos):
        r, c = pos
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and rows[nr][nc] != '#':
                yield (nr, nc)

    g, parent, closed, counter = {start: 0}, {start: None}, set(), 0
    pq = [(weight * h(start, goal), 0, counter, start)]
    while pq:
        _, _, _, cur = heapq.heappop(pq)
        if cur in closed:
            continue
        closed.add(cur)
        if cur == goal:
            path, n = [], cur
            while n is not None:
                path.append(n)
                n = parent[n]
            return {'cost': g[cur], 'expanded': len(closed), 'path': path[::-1], 'closed': closed,
                    'open': set(g) - closed}
        for nb in nbrs(cur):
            ng = g[cur] + 1
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                parent[nb] = cur
                hv = weight * h(nb, goal)
                counter += 1
                second = -ng if tie == 'high-g' else (hv if tie == 'low-h' else 0)
                heapq.heappush(pq, (ng + hv, second, counter, nb))


def grid_panels(rows, results, captions, name, title, cell=11, note=None):
    R, C = len(rows), len(rows[0])
    pw = C * cell
    gap = 22
    sv = Svg(len(results) * pw + (len(results) - 1) * gap + 30, R * cell + 78 + (18 if note else 0), title)
    for k, (res, cap) in enumerate(zip(results, captions)):
        x0, y0 = 15 + k * (pw + gap), 40
        for i, line in enumerate(cap.split('\n')):
            sv.text(x0 + pw / 2, 16 + i * 15, line, 12, weight='bold' if i == 0 else 'normal')
        pset = set(res['path'])

        def colour(r, c):
            ch, p = rows[r][c], (r, c)
            if ch == '#':
                return '#374151'
            if ch in 'SG':
                return TRUE
            if p in pset:
                return ORANGE
            if p in res['closed']:
                return PIX2
            if p in res['open']:
                return '#fde68a'
            return None
        # Run-length rectangles per row keep the file small.
        for r in range(R):
            c = 0
            while c < C:
                f = colour(r, c)
                e = c
                while e + 1 < C and colour(r, e + 1) == f:
                    e += 1
                if f:
                    sv.add(f'<rect x="{x0 + c * cell}" y="{y0 + r * cell}" width="{(e - c + 1) * cell}" '
                           f'height="{cell}" fill="{f}"/>')
                c = e + 1
        grid = ''.join(f'M{x0 + c * cell},{y0}v{R * cell}' for c in range(1, C)) + \
            ''.join(f'M{x0},{y0 + r * cell}h{pw}' for r in range(1, R))
        sv.add(f'<path d="{grid}" stroke="#ffffff" stroke-width="0.6" fill="none"/>')
        sv.rect(x0, y0, pw, R * cell, 'none', stroke='#9ca3af', width=1)
    ly = 40 + R * cell + 18
    items = [(PIX2, 'expanded'), ('#fde68a', 'frontier'), (ORANGE, 'path'), ('#374151', 'wall'), (TRUE, 'S, G')]
    x = 15
    for fill, lab in items:
        sv.rect(x, ly - 10, 11, 11, fill, stroke='#9ca3af', width=0.5)
        sv.text(x + 16, ly, lab, 12, anchor='start')
        x += 22 + len(lab) * 6.6
    if note:
        sv.text(sv.w / 2, ly + 20, note, 12, color='#374151')
    sv.save(name, OUT)


def lesson_astar():
    manh = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
    zero = lambda a, b: 0
    d = astar_grid(ASTAR_MAIN, zero)
    m = astar_grid(ASTAR_MAIN, manh)
    t = astar_grid(ASTAR_MAIN, manh, tie='low-h')
    assert (d['cost'], d['expanded']) == (37, 360)
    assert (m['cost'], m['expanded']) == (37, 233)
    assert (t['cost'], t['expanded']) == (37, 38)
    grid_panels(ASTAR_MAIN, [d, m, t],
                ['h = 0 (Dijkstra)\n360 expanded', 'Manhattan h\n233 expanded', 'Manhattan + tie-break\n38 expanded'],
                'graph-astar-expanded.svg',
                'Three copies of the lab\'s 20 by 20 map, each with an optimal path of cost 37 from S at the top left '
                'to G at the bottom right. Dijkstra (h = 0) expands 360 cells, nearly the whole map; A* with '
                'Manhattan distance expands 233; Manhattan with smaller-h tie-breaking expands only 38, hugging '
                'the path.',
                note='Same path cost, 37, every time. Only the amount of searching changes.')

    w1 = astar_grid(ASTAR_TRAP, manh, weight=1.0)
    w2 = astar_grid(ASTAR_TRAP, manh, weight=2.0)
    assert (w1['cost'], w1['expanded']) == (18, 67) and (w2['cost'], w2['expanded']) == (20, 46)
    grid_panels(ASTAR_TRAP, [w1, w2], ['w = 1 (plain A*)\ncost 18, 67 expanded', 'w = 2 (weighted A*)\ncost 20, 46 expanded'],
                'graph-astar-weighted.svg',
                'The lab\'s cluttered trap map searched twice. Plain A* with weight 1 expands 67 cells and finds the '
                'optimal path of cost 18. Weighted A* with weight 2 expands only 46 cells but returns a path of cost '
                '20, two steps longer.', cell=16,
                note='Doubling h searches less but returns a longer path.')


# ---------- lesson 6.6: minimum spanning tree ----------

def kruskal_order(edges):
    """Edges sorted by (weight, u, v), as in the lab. Returns [(edge, taken)] up to the last taken edge."""
    verts = sorted({x for u, v, _ in edges for x in (u, v)})
    uf, out, taken = UF(verts), [], 0
    for e in sorted(edges, key=lambda e: (e[2], e[0], e[1])):
        ok = uf.union(e[0], e[1])
        out.append((e, ok))
        taken += ok
        if taken == len(verts) - 1:
            break
    return out


def prim_order(edges, start):
    """Lazy Prim with a heap of (w, u, v); ties go to the alphabetically smaller edge."""
    adj = {}
    for u, v, w in edges:
        adj.setdefault(u, []).append((v, w))
        adj.setdefault(v, []).append((u, w))
    seen, pq, chosen = {start}, [], []
    for v, w in adj[start]:
        heapq.heappush(pq, (w, start, v))
    while pq:
        w, u, v = heapq.heappop(pq)
        if v in seen:
            continue
        seen.add(v)
        chosen.append((u, v, w))
        for x, wx in adj[v]:
            if x not in seen:
                heapq.heappush(pq, (wx, v, x))
    return chosen


def mst_picture(pos, edges, picks, rejected, name, title, caption, start=None):
    """picks: [(u, v, w)] in the order chosen; rejected: [(u, v, w)] edges skipped because they close a cycle."""
    g = G()
    num = {frozenset((u, v)): i + 1 for i, (u, v, _) in enumerate(picks)}
    rej = {frozenset((u, v)) for u, v, _ in rejected}
    for v, (x, y) in pos.items():
        g.node(v, x, y, **({'fillcolor': '#fde68a'} if v == start else {}))
    for u, v, w in edges:
        k = frozenset((u, v))
        if k in num:
            g.edge(u, v, label=f'{w}  #{num[k]}', color=ACCENT, penwidth=3.5, fontcolor='#047857')
        elif k in rej:
            g.edge(u, v, label=f'{w} ✗', color=TRUE, style='dashed', fontcolor=TRUE)
        else:
            g.edge(u, v, label=w, color=GREY)
    xs = [x for x, _ in pos.values()]
    g.text('cap', (min(xs) + max(xs)) / 2, min(y for _, y in pos.values()) - 0.7, caption, 12)
    g.save(name, title)


def lesson_mst():
    # The cable motivation.
    cab = [('A', 'B', 10), ('B', 'C', 15), ('B', 'D', 5), ('A', 'D', 12), ('C', 'D', 8)]
    ko = kruskal_order(cab)
    picks = [e for e, ok in ko if ok]
    assert picks == [('B', 'D', 5), ('C', 'D', 8), ('A', 'B', 10)] and sum(w for *_, w in picks) == 23
    g = G()
    box = dict(shape='box', style='rounded,filled', width=0.9, height=0.4, fontsize=12)
    cpos = {'A': (0, 1), 'B': (1.5, 2), 'C': (3.0, 1), 'D': (1.5, 0)}
    for v, (x, y) in cpos.items():
        g.node(v, x, y, label=f'City {v}', **box)
    chosen = {frozenset(e[:2]) for e in picks}
    for u, v, w in cab:
        g.edge(u, v, label=f'${w}M', **(dict(color=ACCENT, penwidth=3.5) if frozenset((u, v)) in chosen
                                         else dict(color=GREY, style='dashed')))
    g.text('cap', 1.5, -0.65, 'Green: the cheapest layout that still links every city, $5M + $8M + $10M = $23M.', 12)
    g.save('graph-mst-cables.svg',
           'Four cities with possible cables: A-B $10M, B-C $15M, B-D $5M, A-D $12M, C-D $8M. The minimum spanning '
           'tree in green uses B-D, C-D and A-B for $23M; the dashed A-D and B-C cables are not needed.')

    E = [('A', 'B', 4), ('A', 'C', 8), ('B', 'C', 11), ('B', 'D', 8), ('C', 'E', 7), ('D', 'E', 2), ('D', 'F', 4),
         ('E', 'F', 14), ('D', 'G', 9), ('F', 'G', 10)]
    pos = {'A': (0, 1), 'B': (1.6, 2), 'C': (1.6, 0), 'D': (3.2, 2), 'E': (3.2, 0), 'F': (4.8, 1), 'G': (4.8, 3.0)}
    ko = kruskal_order(E)
    picks = [e for e, ok in ko if ok]
    rejected = [e for e, ok in ko if not ok]
    assert [(u, v, w) for u, v, w in picks] == [('D', 'E', 2), ('A', 'B', 4), ('D', 'F', 4), ('C', 'E', 7),
                                                 ('A', 'C', 8), ('D', 'G', 9)]
    assert rejected == [('B', 'D', 8)] and sum(w for *_, w in picks) == 34
    mst_picture(pos, E, picks, rejected, 'graph-mst-kruskal.svg',
                "Kruskal's algorithm on the lab graph. Edges taken in order: D-E 2 (#1), A-B 4 (#2), D-F 4 (#3), "
                "C-E 7 (#4), A-C 8 (#5), D-G 9 (#6), total 34. B-D 8 is skipped (red cross) because B and D are "
                "already connected.",
                'Kruskal: cheapest edge first, skip any that closes a loop. Total 34.')

    pp = prim_order(E, 'A')
    assert pp == [('A', 'B', 4), ('A', 'C', 8), ('C', 'E', 7), ('E', 'D', 2), ('D', 'F', 4), ('D', 'G', 9)]
    assert {frozenset(e[:2]) for e in pp} == {frozenset(e[:2]) for e in picks}
    mst_picture(pos, E, pp, [], 'graph-mst-prim.svg',
                "Prim's algorithm from A on the lab graph. Edges added in order: A-B 4 (#1), A-C 8 (#2), C-E 7 (#3), "
                "E-D 2 (#4), D-F 4 (#5), D-G 9 (#6). Same six edges as Kruskal, total 34, found in a different order.",
                "Prim from A: always the cheapest edge leaving the tree. Same tree, total 34.", start='A')

    # Sketch answer.
    sE = [('P', 'Q', 3), ('P', 'R', 1), ('Q', 'R', 7), ('Q', 'S', 5), ('R', 'S', 4), ('R', 'T', 6), ('S', 'T', 2)]
    ko = kruskal_order(sE)
    picks = [e for e, ok in ko if ok]
    assert picks == [('P', 'R', 1), ('S', 'T', 2), ('P', 'Q', 3), ('R', 'S', 4)]
    assert sum(w for *_, w in picks) == 10 and all(ok for _, ok in ko)
    spos = {'P': (0, 1.5), 'Q': (2.0, 1.5), 'R': (0, 0), 'S': (2.0, 0), 'T': (1.0, -1.2)}
    mst_picture(spos, sE, picks, [], 'graph-sketch-mst.svg',
                "Answer: Kruskal takes P-R 1 (#1), S-T 2 (#2), P-Q 3 (#3) and R-S 4 (#4), total 10. The edges Q-S 5, "
                "R-T 6 and Q-R 7 are left out in grey.",
                'MST total 10. Q-S, R-T and Q-R would each close a loop.')


if __name__ == '__main__':
    lesson1()
    lesson2()
    lesson3()
    lesson4()
    lesson_dfs()
    lesson_bfs()
    lesson_edges()
    lesson_components()
    lesson_topo()
    lesson_dijkstra()
    lesson_bellman()
    lesson_floyd()
    lesson_astar()
    lesson_mst()
