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


# --- 05: the instrumentation chain -----------------------------------------
def instrumentation_chain():
    stages = [
        ('Measurand\n(displacement, force,\ntemperature, pressure…)', 'fixed'),
        ('Sensor /\ntransducer', 'prog'),
        ('Signal\nprocessing', 'prog'),
        ('Input / output\nstructure', 'prog'),
        ('Application', 'data'),
    ]
    flowchart(stages, 'mecha-instrumentation-chain.svg',
              'The instrumentation chain: a measurand is picked up by a sensor or transducer, '
              'passed through signal processing and an input/output structure, and used by the '
              'application', OUT, rankdir='LR')


# --- 06: accuracy versus precision -----------------------------------------
def accuracy_precision():
    s = Svg(560, 210, 'Four dartboard targets showing low and high accuracy against low and high '
                      'precision: scattered-and-off-centre, scattered-around-centre, '
                      'tight-but-off-centre, and tight-and-on-centre')
    panels = [
        ('Low accuracy\nLow precision', [(-22, 18), (14, 30), (28, -6), (-8, 40), (36, 14)]),
        ('High accuracy\nLow precision', [(-26, 8), (22, -18), (6, 26), (-14, -22), (18, 16)]),
        ('Low accuracy\nHigh precision', [(24, 22), (30, 16), (20, 28), (27, 24), (22, 18)]),
        ('High accuracy\nHigh precision', [(-4, 3), (3, -5), (-6, -2), (2, 5), (0, 0)]),
    ]
    for i, (label, dots) in enumerate(panels):
        cx = 70 + i * 140
        cy = 90
        for r, col in [(46, '#e5e7eb'), (31, '#d1fae5'), (16, '#fde68a')]:
            s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" '
                  f'stroke-width="7"/>')
        s.add(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{INK}"/>')
        for dx, dy in dots:
            s.add(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="3.4" fill="{BLUE}" '
                  f'stroke="white" stroke-width="0.8"/>')
        for j, line in enumerate(label.split('\n')):
            s.text(cx, 172 + j * 15, line, size=11.5, color=INK, weight='bold')
    s.save('mecha-accuracy-precision.svg', OUT)


# --- 06: sensitivity and linearity -----------------------------------------
def sensitivity_linearity():
    s = Svg(440, 300, 'A graph of sensor output against input: a straight ideal line whose slope '
                      'is the sensitivity, and a curved real response whose gap from the line is '
                      'the non-linearity')
    ox, oy, w, h = 60, 250, 340, 210
    s.line(ox, oy, ox + w, oy, color=INK, width=1.5)
    s.line(ox, oy, ox, oy - h, color=INK, width=1.5)
    s.text(ox + w / 2, 285, 'Input (measured quantity)', size=12, color=INK)
    s.add(f'<text x="18" y="{oy - h / 2}" font-size="12" fill="{INK}" '
          f'transform="rotate(-90 18 {oy - h / 2})" text-anchor="middle">Output signal</text>')
    # ideal straight line, slope = sensitivity
    x0, y0 = ox, oy
    x1, y1 = ox + w, oy - h * 0.86
    s.line(x0, y0, x1, y1, color=BLUE, width=2.2)
    s.text(x1 - 10, y1 - 8, 'ideal (slope = sensitivity)', size=11, color=BLUE, anchor='end')
    # real curved response
    pts = []
    for k in range(41):
        t = k / 40
        x = ox + t * w
        ideal = t * 0.86
        real = ideal + 0.12 * math.sin(t * math.pi)  # bows above then meets
        y = oy - h * real
        pts.append(f'{x:.1f},{y:.1f}')
    s.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ORANGE}" '
          f'stroke-width="2.2"/>')
    s.text(ox + w * 0.5, oy - h * 0.70, 'real response', size=11, color=ORANGE, anchor='start')
    s.text(ox + w * 0.62, oy - h * 0.38, '(gap between them = non-linearity)', size=10.5, color=GREY,
           anchor='start')
    s.save('mecha-sensitivity-linearity.svg', OUT)


# --- 15: where the uncertainty in C_q comes from ---------------------------
def uncertainty_contributions():
    # C_q = W / (t * rho * A * sqrt(2gh)),  A = pi d^2 / 4
    W, dW = 200.0, 0.23
    t, dt = 500.0, 2.0
    rho = 1000.0
    d, dd = 1.25, 0.11
    g, dg = 9.81, 0.11
    h, dh = 3.66, 0.003
    A = math.pi * d ** 2 / 4
    Cq = W / (t * rho * A * math.sqrt(2 * g * h))
    assert close(A, 1.22718, 1e-4), A
    assert close(Cq, 3.8464e-5, 1e-3), Cq
    # relative-uncertainty terms (exponent * relative uncertainty)
    terms = {
        'd (orifice dia., power 2)': 2 * dd / d,
        'g (power ½)': 0.5 * dg / g,
        't (time, power 1)': 1 * dt / t,
        'W (weight, power 1)': 1 * dW / W,
        'h (head, power ½)': 0.5 * dh / h,
    }
    total = math.sqrt(sum(v ** 2 for v in terms.values()))
    assert close(total, 0.17614, 1e-3), total
    assert close(terms['d (orifice dia., power 2)'], 0.176, 1e-2)
    order = sorted(terms.items(), key=lambda kv: -kv[1])
    s = Svg(560, 250, f'Horizontal bar chart of each variable’s contribution to the '
                      f'uncertainty in the discharge coefficient C_q: the orifice diameter '
                      f'dominates at about 17.6 percent while the rest are under 1 percent, and '
                      f'the combined uncertainty is {total * 100:.1f} percent')
    x0, y0 = 220, 40
    maxv = max(v for _, v in order)
    barw = 250
    for i, (name, v) in enumerate(order):
        y = y0 + i * 34
        bw = barw * v / maxv
        s.add(f'<rect x="{x0}" y="{y}" width="{bw:.1f}" height="20" rx="3" fill="{BLUE}"/>')
        s.text(x0 - 8, y + 15, name, size=11.5, color=INK, anchor='end')
        s.text(x0 + bw + 6, y + 15, f'{v * 100:.2f}%', size=11, color=INK, anchor='start')
    s.text(x0 + barw / 2, 240, f'Combined (root-sum-square): {total * 100:.2f}%', size=12.5,
           color=INK, weight='bold')
    s.save('mecha-uncertainty-contributions.svg', OUT)


# --- 15: worked-example and quiz numbers (asserts only, no picture) ---------
def rss(*terms):
    return math.sqrt(sum(x * x for x in terms))


def uncertainty_checks():
    # omega = sqrt(F / (m r)), exam: m = 200 +- 0.01 g, r = 25 +- 0.01 mm, F = 500 +- 0.1 %
    w = math.sqrt(500 / (0.200 * 0.025))
    rel = rss(0.5 * 0.001, 0.5 * 0.01 / 200, 0.5 * 0.01 / 25)
    assert close(w, 316.228, 1e-5), w
    assert close(rel, 5.3909e-4, 1e-3), rel
    assert close(w * rel, 0.17048, 1e-3), w * rel
    worst = 0.5 * 0.001 + 0.5 * 0.01 / 200 + 0.5 * 0.01 / 25
    assert close(worst, 7.25e-4, 1e-6), worst
    # practice Q6: m = 150 +- 0.01 g, r = 20 +- 0.01 mm, F = 350 +- 0.1 %
    w2 = math.sqrt(350 / (0.150 * 0.020))
    rel2 = rss(0.5 * 0.001, 0.5 * 0.01 / 150, 0.5 * 0.01 / 20)
    assert close(w2, 341.565, 1e-5), w2
    assert close(rel2, 5.6001e-4, 1e-3), rel2
    assert close(w2 * rel2, 0.19128, 1e-3), w2 * rel2
    # RLC impedance, assumed 50 Hz: R = 2 kOhm, L = 0.8 H, C = 5 uF, each +- 5 %
    om = 2 * math.pi * 50
    R, XL, XC = 2000.0, om * 0.8, 1 / (om * 5e-6)
    D = XL - XC
    Z = math.hypot(R, D)
    dZ = rss(R / Z * 0.05 * R, D / Z * 0.05 * XL, D / Z * 0.05 * XC)
    assert close(XL, 251.327, 1e-4) and close(XC, 636.620, 1e-4), (XL, XC)
    assert close(Z, 2036.77, 1e-4), Z
    assert close(dZ, 98.41, 1e-3), dZ
    print('uncertainty checks: ok')


if __name__ == '__main__':
    history()
    synergy()
    design_process()
    measurement_loop()
    instrumentation_chain()
    accuracy_precision()
    sensitivity_linearity()
    uncertainty_contributions()
    uncertainty_checks()
    print('mechatronics diagrams: done')
