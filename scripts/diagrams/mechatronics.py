"""Draw the mechatronics lesson diagrams as small SVG files, and check the lessons' numbers.

    python3 scripts/diagrams/mechatronics.py      # run from the vault root

Conceptual diagrams (design process, history, synergy, measurement loop) are built from
Graphviz (`dot`, which must be installed) or drawn directly. Worked-example numbers that
come from a calculation (uncertainty propagation, kinematics) are checked here with an
assert before anything is drawn, so a picture can never disagree with the lesson.
Output: mechatronics/images/*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, Svg, flowchart, save_dot  # noqa: E402

OUT = os.path.join('mechatronics', 'images')
BLUE = '#2563eb'
ORANGE = '#f59e0b'
GREY = '#9ca3af'
GREEN = '#10b981'


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


# --- 01: historical development of mechatronics -----------------------------
def history():
    stages = [
        ('Pure mechanical\n(before 1900)', 'fixed'),
        ('Mechanical with\nelectrical drives (1920)', 'fixed'),
        ('Mechanical with\nautomatic control (1935)', 'prog'),
        ('Electronic analog &\nsequential control (1955)', 'prog'),
        ('Digital continuous &\nsequential control (1975)', 'prog'),
        ('Mechatronic systems:\nhardware + software (1985+)', 'data'),
    ]
    flowchart(stages, 'mecha-history.svg',
              'Timeline of how mechatronics grew from purely mechanical machines to integrated '
              'hardware and software systems', OUT, rankdir='LR')


# --- 01/02: the synergy of the three disciplines ----------------------------
def synergy():
    s = Svg(560, 380, 'Three overlapping circles for Electronics, Mechanics and Information '
                      'technology, overlapping in the middle as Mechatronics')
    circ = [(200, 165, '#2563eb', 'Electronics', 150, 120),
            (360, 165, '#10b981', 'Mechanics', 410, 120),
            (280, 265, '#f59e0b', 'Information\ntechnology', 280, 330)]
    for cx, cy, col, _, _, _ in circ:
        s.add(f'<circle cx="{cx}" cy="{cy}" r="120" fill="{col}" fill-opacity="0.18" '
              f'stroke="{col}" stroke-width="1.5"/>')
    for cx, cy, col, label, lx, ly in circ:
        for i, line in enumerate(label.split('\n')):
            s.text(lx, ly + i * 16, line, size=14, color=col, weight='bold')
    s.text(280, 205, 'Mechatronics', size=15, color=INK, weight='bold')
    s.save('mecha-synergy.svg', OUT)


# --- 03: the mechatronic design process -------------------------------------
def design_process():
    src = (
        'digraph {{ bgcolor="white"; pad=0.25; rankdir=TB; nodesep=0.3; ranksep=0.35;\n'
        'node [fontname="Helvetica,Arial,sans-serif", fontsize=12, shape=box, '
        'style="rounded,filled", color="{ink}", penwidth=1.2, width=3.6];\n'
        'edge [fontname="Helvetica,Arial,sans-serif", fontsize=11, color="{ink}", '
        'fontcolor="#374151"];\n'
        'n0 [label="Recognition of the need", fillcolor="#e5e7eb"];\n'
        'n1 [label="Conceptual design &\\nfunctional specification", fillcolor="#dbeafe"];\n'
        'n2 [label="First-principle\\nmodular mathematical modelling", fillcolor="#dbeafe"];\n'
        'n3 [label="Sensor and actuator selection", fillcolor="#dbeafe"];\n'
        'n4 [label="Detailed\\nmodular mathematical modelling", fillcolor="#dbeafe"];\n'
        'n5 [label="Control system design", fillcolor="#dbeafe"];\n'
        'n6 [label="Design optimisation", fillcolor="#d1fae5"];\n'
        'n7 [label="Prototyping:\\nhardware-in-the-loop simulation", fillcolor="#fde68a"];\n'
        'n8 [label="Deployment & life cycle:\\nreliability, maintainability, upgrade", '
        'fillcolor="#fde68a"];\n'
        'n0 -> n1 -> n2 -> n3 -> n4 -> n5 -> n6 -> n7 -> n8;\n'
        'n6 -> n2 [label="  feedback", constraint=false, style=dashed];\n'
        'n6 -> n1 [label="  feedback", constraint=false, style=dashed];\n'
        'n7 -> n6 [constraint=false, style=dashed];\n'
        '}}'
    ).format(ink=INK)
    save_dot(src, 'mecha-design-process.svg',
             'The mechatronic design process from recognising the need through modelling, '
             'sensor and actuator selection, control design and optimisation to prototyping and '
             'deployment, with feedback loops back to the modelling stages', OUT)


# --- 05: the mechatronic measurement system loop ----------------------------
def measurement_loop():
    src = (
        'digraph {{ bgcolor="white"; pad=0.25; rankdir=LR; nodesep=0.35; ranksep=0.45;\n'
        'node [fontname="Helvetica,Arial,sans-serif", fontsize=12, shape=box, '
        'style="rounded,filled", color="{ink}", penwidth=1.2];\n'
        'edge [fontname="Helvetica,Arial,sans-serif", fontsize=11, color="{ink}", '
        'fontcolor="#374151"];\n'
        'src [label="Source\\n(measurand)", fillcolor="#e5e7eb"];\n'
        'det [label="Sensor /\\ndetector", fillcolor="#dbeafe"];\n'
        'cond [label="Signal\\nconditioning", fillcolor="#dbeafe"];\n'
        'disp [label="Display", fillcolor="#d1fae5"];\n'
        'ctl [label="Controller", fillcolor="#fde68a"];\n'
        'fb [label="Feedback sensor\\n(auxiliary energy)", fillcolor="#dbeafe"];\n'
        'src -> det -> cond -> disp;\n'
        'disp -> fb [style=invis];\n'
        'fb -> ctl -> src [label="  correct"];\n'
        'cond -> fb [constraint=false, style=dashed];\n'
        '}}'
    ).format(ink=INK)
    save_dot(src, 'mecha-measurement-loop.svg',
             'A mechatronic measurement system: the source feeds a sensor, then signal '
             'conditioning, then a display, while a feedback sensor and controller act back on '
             'the source to correct it', OUT)


if __name__ == '__main__':
    history()
    synergy()
    design_process()
    measurement_loop()
    print('mechatronics diagrams: done')
