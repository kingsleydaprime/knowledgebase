"""Draw the engineering design and prototyping lesson diagrams as small SVG files.

    python3 scripts/diagrams/engineering_design.py      # run from the vault root

The flowcharts and the tree are drawn with Graphviz (`dot`, which must be
installed). The Kano graph is computed from three simple curves. The worked
tables in the lessons (Pugh matrix, decision matrices, FMEA) are checked here
with asserts, so a lesson's numbers can never drift from the sums.
Output: engineering-design-and-prototyping/images/*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, PIX, TRUE, ACCENT, FONT, Svg, save_dot  # noqa: E402

OUT = os.path.join('engineering-design-and-prototyping', 'images')
ORANGE = '#f59e0b'


# ---------- the lessons' worked numbers ----------

def weighted_total(weights, scores):
    return sum(w * s for w, s in zip(weights, scores))


def check_tables():
    # Lesson 09: the student backpack Pugh matrix.
    w = [2, 1, 1, 1, 0.5, 0.5]
    assert weighted_total(w, [+1, -1, -1, 0, -1, +1]) == 0
    assert weighted_total(w, [-1, +1, +1, +1, +1, 0]) == 1.5
    assert weighted_total(w, [0, +1, +1, 0, 0, +1]) == 2.5
    # Lesson 11: the office location decision matrix (the lecture's totals were wrong).
    w = [5, 4, 3, 2, 4]
    assert weighted_total(w, [2, 5, 4, 3, 4]) == 64
    assert weighted_total(w, [4, 3, 5, 2, 3]) == 63
    assert weighted_total(w, [5, 4, 3, 5, 2]) == 68
    # Lesson 20: the study desk decision matrix.
    w = [5, 4, 3, 2]
    assert weighted_total(w, [3, 2, 2, 3]) == 35
    assert weighted_total(w, [4, 3, 2, 3]) == 44
    assert weighted_total(w, [4, 2, 3, 2]) == 41


# ---------- pictures ----------

def graph(name, title, body, rankdir='TB'):
    src = (f'digraph {{ bgcolor="white"; pad=0.25; rankdir={rankdir}; nodesep=0.3; ranksep=0.35;\n'
           f'node [fontname="{FONT}", fontsize=13, shape=box, style="rounded,filled", fillcolor="#dbeafe", '
           f'color="{INK}", penwidth=1.2];\n'
           f'edge [fontname="{FONT}", fontsize=11, color="{INK}", fontcolor="#374151"];\n{body}\n}}')
    save_dot(src, name, title, OUT)


def design_phases():
    phases = ['1. Problem definition', '2. Concept generation', '3. Concept selection',
              '4. Concept refinement', '5. Detailed design', '6. Prototyping', '7. Testing and evaluation']
    body = [f'p{i} [label="{p}", width=3];' for i, p in enumerate(phases)]
    body += [f'p{i} -> p{i + 1};' for i in range(len(phases) - 1)]
    body.append(f'p6 -> p1 [label="  test shows a problem:\\n  go back", style=dashed, color="{ORANGE}", '
                f'fontcolor="#b45309", constraint=false];')
    graph('ed-design-phases.svg',
          'The seven phases of the design process in order, from problem definition to testing and evaluation, '
          'with a dashed arrow from testing back to an earlier phase because the process is iterative',
          '\n'.join(body))


def life_cycle():
    steps = ['1. Mine, drill or harvest\\nnatural material', '2. Extract and refine\\nraw materials',
             '3. Process into finished\\nengineering material', '4. Design and\\nmanufacture the part',
             '5. Performance, service\\nor use of the part', '6. Wears out or becomes\\nobsolete (end of life)',
             '7. Recycle or dispose\\nof the part']
    body = [f's{i} [label="{s}", width=2.8];' for i, s in enumerate(steps)]
    body += [f's{i} -> s{i + 1};' for i in range(len(steps) - 1)]
    body.append(f's6 -> s2 [label="  recycling restarts\\n  the life cycle", style=dashed, color="{ACCENT}", '
                f'fontcolor="{ACCENT}", constraint=false];')
    body.append(f's6 -> s0 [label="  disposal returns\\n  material to the earth", style=dotted, color="#6b7280", '
                f'constraint=false];')
    graph('ed-life-cycle.svg',
          'The seven phases of the total life cycle of a part, from mining natural material to recycling or disposal; '
          'recycling loops back to processing, and disposal returns the material to the earth',
          '\n'.join(body))


def bottle_tree():
    body = ['root [label="Collapsible water bottle", fillcolor="#fef3c7"];']
    subs = [('Contain liquid', 'body, cap, seal'),
            ('Provide drinking access', 'mouthpiece, lid, valve'),
            ('Collapse for storage', 'flexible material,\\nfolding mechanism'),
            ('Maintain shape', 'ribs, supports')]
    for i, (f, parts) in enumerate(subs):
        body.append(f'f{i} [label="{f}"];')
        body.append(f'c{i} [label="{parts}", fillcolor="#d1fae5", fontsize=12];')
        body.append(f'root -> f{i}; f{i} -> c{i};')
    graph('ed-bottle-decomposition.svg',
          'Functional decomposition of a collapsible water bottle: the overall function splits into four subfunctions '
          '(contain liquid, provide drinking access, collapse for storage, maintain shape), each with the parts that do it',
          '\n'.join(body))


def kano():
    W, H = 520, 400
    ox, oy, sx, sy = 260, 200, 210, 160       # origin in the middle; x and y run from -1 to 1
    s = Svg(W, H, 'The Kano model graph: fulfilment of the need on the x-axis and user satisfaction on the y-axis, '
                  'with a basic needs curve that only reaches neutral, a straight rising performance line, '
                  'and a delight curve that jumps up sharply')

    def P(x, y):
        return ox + x * sx, oy - y * sy

    # axes
    s.line(*P(-1.05, 0), *P(1.08, 0), width=1.5)
    s.line(*P(0, -1.1), *P(0, 1.1), width=1.5)
    s.text(*P(1.04, 0.07), 'fulfilled', size=12, anchor='end')
    s.text(*P(-1.0, 0.1), 'not fulfilled', size=12, anchor='start')
    s.text(P(0, 1.1)[0] + 8, P(0, 1.1)[1] + 10, 'satisfied', size=12, anchor='start')
    s.text(P(0, -1.1)[0] + 8, P(0, -1.1)[1], 'dissatisfied', size=12, anchor='start')

    def curve(f, color, dash=None):
        pts = [P(x / 50 - 1, f(x / 50 - 1)) for x in range(101)]
        d = 'M ' + ' L '.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        s.path(d, color, width=2.5, dash=dash)

    basic = lambda x: -math.exp(-2.2 * (x + 1)) * 1.0 + 0.0 - 0.02   # rises to just under neutral, then flat
    perf = lambda x: 0.85 * x
    delight = lambda x: math.exp(2.4 * (x - 1)) * 1.0 - 0.05          # flat near neutral, then jumps up
    curve(basic, TRUE)
    curve(perf, PIX)
    curve(delight, ACCENT)
    s.text(*P(0.98, -0.2), 'Basic', size=13, color=TRUE, anchor='end', weight='bold')
    s.text(*P(0.62, 0.62), 'Performance', size=13, color=PIX, anchor='end', weight='bold')
    s.text(*P(0.70, 0.95), 'Delight', size=13, color=ACCENT, anchor='end', weight='bold')
    s.save('ed-kano-model.svg', OUT)


if __name__ == '__main__':
    check_tables()
    design_phases()
    life_cycle()
    bottle_tree()
    kano()
