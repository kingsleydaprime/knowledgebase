"""Draw the mechatronics modelling diagrams (sections C and D) and check the lessons' algebra.

    python3 scripts/diagrams/mechatronics_models.py      # run from the vault root

Every transfer function in the modelling and analogy lessons is checked here before anything is
drawn: the system's differential equations are Laplace-transformed and solved as a linear system
at several complex values of s, and the answer must equal the lesson's closed-form transfer
function. Block-diagram reductions are checked the same way, by solving the signal equations.
No libraries needed; block diagrams use Graphviz (`dot`).
Output: mechatronics/images/model-*.svg.
"""
import cmath
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, Svg, save_dot  # noqa: E402

OUT = os.path.join('mechatronics', 'images')
BLUE = '#2563eb'
ORANGE = '#f59e0b'
GREY = '#6b7280'
GREEN = '#059669'
MASSFILL = '#dbeafe'
TEST_S = [0.3 + 0.7j, -0.2 + 1.9j, 1.1 - 0.4j, 2.5 + 0.1j]


# --------------------------------------------------------------------------- algebra checks
def solve(A, b):
    """Gaussian elimination with partial pivoting, complex numbers allowed."""
    n = len(A)
    M = [list(map(complex, row)) + [complex(b[i])] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * bb for a, bb in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def agree(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))


def check_tf(name, matrix, rhs, index, closed):
    """matrix(s) and rhs(s) give the Laplace-domain equations; closed(s) is the lesson's TF."""
    for s in TEST_S:
        got = solve(matrix(s), rhs(s))[index]
        want = closed(s)
        assert agree(got, want), (name, s, got, want)
    print(f'check {name}: ok')


def checks():
    M, f, K = 2.0, 3.0, 8.0
    # 09: hanging mass-spring-damper  F = M x'' + f x' + K x
    check_tf('msd X/F', lambda s: [[M * s * s + f * s + K]], lambda s: [1], 0,
             lambda s: 1 / (M * s * s + f * s + K))
    # 09 / 11: cart  M y'' + f(y' - u') + K(y - u) = 0
    check_tf('cart Y/U', lambda s: [[M * s * s + f * s + K]], lambda s: [f * s + K], 0,
             lambda s: (f * s + K) / (M * s * s + f * s + K))
    # 11: damper in series with M and K to ground  f(xi' - xo') = M xo'' + K xo
    check_tf('series damper Xo/Xi', lambda s: [[M * s * s + f * s + K]], lambda s: [f * s], 0,
             lambda s: f * s / (M * s * s + f * s + K))
    # 09: three-mass ceiling system (2025/26 Q6, quiz 2 Q7), force only on M1 -> X1/F1
    M1, M2, M3, K1, K2, K3, f1, f3 = 1.0, 2.0, 1.5, 4.0, 3.0, 5.0, 0.6, 0.9

    def three(s):
        return [[M1 * s * s + f1 * s + K1 + K2, -K2, 0],
                [-K2, M2 * s * s + f3 * s + K2 + K3, -(f3 * s + K3)],
                [0, -(f3 * s + K3), M3 * s * s + f3 * s + K3]]
    # the lesson only writes the equations; check symmetry rules by solving and re-substituting
    for s in TEST_S:
        x = solve(three(s), [1, 0, 0])
        r = [sum(a * xi for a, xi in zip(row, x)) for row in three(s)]
        assert all(agree(ri, ti) for ri, ti in zip(r, [1, 0, 0]))
    # 09 / quiz: quiz 2 Q5, ceiling K1||f1 - M1 (F) - K2 - M2
    check_tf('quiz2 Q5 X1/F',
             lambda s: [[M1 * s * s + f1 * s + K1 + K2, -K2], [-K2, M2 * s * s + K2]],
             lambda s: [1, 0], 0,
             lambda s: (M2 * s * s + K2) /
             ((M1 * s * s + f1 * s + K1 + K2) * (M2 * s * s + K2) - K2 ** 2))
    # 10: J - K - f(to wall), torque on J
    J = 1.5
    check_tf('rot theta1/T', lambda s: [[J * s * s + K, -K], [-K, f * s + K]],
             lambda s: [1, 0], 0,
             lambda s: (f * s + K) / (s * (J * f * s * s + J * K * s + K * f)))
    # 10: two inertias on a shaft (practice Q4)
    J1, J2 = 1.2, 0.7
    check_tf('two-inertia theta1/T', lambda s: [[J1 * s * s + K, -K], [-K, J2 * s * s + K]],
             lambda s: [1, 0], 0,
             lambda s: (J2 * s * s + K) / (s * s * (J1 * J2 * s * s + K * (J1 + J2))))
    # 10: class example 1, three-inertia system; unknowns (theta_m, theta_2, theta_1)
    Jm, Ka, Kb = 0.5, 6.0, 2.5   # Ka = K1 (to J1), Kb = K2 (to J2)

    def tri(s):
        return [[Jm * s * s + Ka + Kb, -Kb, -Ka],
                [-Kb, J2 * s * s + Kb, 0],
                [-Ka, 0, J1 * s * s + Ka]]

    def tri_closed(s):
        num = (J2 * s * s + Kb) * Ka
        den = s * s * (J1 * J2 * Jm * s ** 4
                       + (Kb * Jm * J1 + Ka * Jm * J2 + J2 * J1 * Kb + J2 * J1 * Ka) * s * s
                       + (J2 * Kb * Ka + J1 * Ka * Kb + Jm * Ka * Kb))
        return num / den
    check_tf('three-inertia theta1/T', tri, lambda s: [1, 0, 0], 2, tri_closed)
    # 11: impulse response of M-K: x(t) = sin(wn t)/sqrt(MK), wn = sqrt(K/M)
    Mi, Ki = 2.0, 8.0
    wn = math.sqrt(Ki / Mi)
    assert agree(wn, 2.0) and agree(1 / math.sqrt(Mi * Ki), 0.25)
    # numeric check: integrate M x'' + K x = 0 with x(0)=0, x'(0)=1/M (the impulse's effect)
    x, v, dt = 0.0, 1 / Mi, 1e-4
    for _ in range(int(round(1.0 / dt))):      # semi-implicit Euler to t = 1 s
        v -= Ki / Mi * x * dt
        x += v * dt
    assert abs(x - 0.25 * math.sin(2.0)) < 1e-3, x
    print('check impulse response: ok')
    return wn


# --------------------------------------------------------------------------- drawing helpers
def _frame(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy)
    u = (dx / L, dy / L)
    n = (-u[1], u[0])
    return u, n, L


def _at(p1, u, n, L, t, off=0.0):
    return (p1[0] + u[0] * L * t + n[0] * off, p1[1] + u[1] * L * t + n[1] * off)


def _poly(s, pts, color=INK, width=1.8):
    s.add('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
          + f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')


def _label(s, p1, u, n, L, side, off, label, color=INK):
    """Element label: centred beside a horizontal element, anchored beside a vertical one."""
    if abs(u[0]) < 1e-9:                      # vertical element
        x, y = _at(p1, u, n, L, 0.5, side * off)
        right = n[0] * side > 0
        s.text(x + (-4 if right else 4), y + 5, label, size=13, color=color, weight='bold',
               anchor='start' if right else 'end')
    else:
        x, y = _at(p1, u, n, L, 0.5, side * (off + 4))
        s.text(x, y + 5, label, size=13, color=color, weight='bold')


def spring(s, p1, p2, label=None, side=1, coils=5, amp=7, color=INK):
    u, n, L = _frame(p1, p2)
    pts = [p1, _at(p1, u, n, L, 0.22)]
    m = coils * 2
    for k in range(1, m):
        pts.append(_at(p1, u, n, L, 0.22 + 0.56 * k / m, amp if k % 2 else -amp))
    pts += [_at(p1, u, n, L, 0.78), p2]
    _poly(s, pts, color)
    if label:
        _label(s, p1, u, n, L, side, amp + 10, label, color)


def damper(s, p1, p2, label=None, side=1, w=9, color=INK):
    u, n, L = _frame(p1, p2)
    a, b, c = 0.32, 0.68, 0.52
    _poly(s, [p1, _at(p1, u, n, L, a)], color)
    _poly(s, [_at(p1, u, n, L, b, -w), _at(p1, u, n, L, a, -w), _at(p1, u, n, L, a, w),
              _at(p1, u, n, L, b, w)], color)
    _poly(s, [_at(p1, u, n, L, c, -w + 3), _at(p1, u, n, L, c, w - 3)], color, 2.4)
    _poly(s, [_at(p1, u, n, L, c), p2], color)
    if label:
        _label(s, p1, u, n, L, side, w + 10, label, color)


def mass(s, x, y, w, h, label, fill=MASSFILL):
    s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="{fill}" '
          f'stroke="{INK}" stroke-width="1.6"/>')
    s.text(x + w / 2, y + h / 2 + 5, label, size=14, weight='bold')


def ground(s, x1, y1, x2, y2, side='up'):
    """A fixed wall/ceiling/floor: a thick line with hatch ticks on `side`."""
    s.line(x1, y1, x2, y2, width=2.4)
    if y1 == y2:                       # horizontal
        d = -1 if side == 'up' else 1
        x = x1
        while x <= x2:
            s.line(x, y1, x - 7, y1 + d * 8, width=1.1)
            x += 10
    else:                              # vertical
        d = 1 if side == 'right' else -1
        y = y1
        while y <= y2:
            s.line(x1, y, x1 + d * 8, y + 7, width=1.1)
            y += 10


def arrow(s, p1, p2, label=None, color=BLUE, width=2.0, lab_dx=0, lab_dy=0, anchor='middle',
          size=13):
    s.line(p1[0], p1[1], p2[0], p2[1], color=color, width=width)
    u, n, L = _frame(p1, p2)
    a = _at(p1, u, n, L, 1 - 9 / L, 4.5)
    b = _at(p1, u, n, L, 1 - 9 / L, -4.5)
    s.add(f'<polygon points="{p2[0]:.1f},{p2[1]:.1f} {a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f}" '
          f'fill="{color}"/>')
    if label:
        s.text(p2[0] + lab_dx, p2[1] + lab_dy, label, size=size, color=color, anchor=anchor,
               weight='bold')


def wheel(s, x, y, r):
    s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{INK}" stroke-width="1.6"/>')


def node_dot(s, x, y):
    s.circle(x, y, 3.2, INK)


def source(s, x, y1, y2, label, kind='force'):
    """A force/torque source in a mechanical network: circle with an arrow, from ground (y2) up to
    the node (y1)."""
    cy = (y1 + y2) / 2
    s.line(x, y1, x, cy - 15)
    s.line(x, cy + 15, x, y2)
    s.add(f'<circle cx="{x}" cy="{cy}" r="15" fill="white" stroke="{INK}" stroke-width="1.6"/>')
    arrow(s, (x, cy + 9), (x, cy - 10), color=INK, width=1.6)
    s.text(x - 22, cy + 5, label, size=13, weight='bold', anchor='end')


def net_mass(s, x, y1, y2, label, color=INK):
    """A mass in a mechanical network: a box between the node and the reference."""
    cy = (y1 + y2) / 2
    s.line(x, y1, x, cy - 16, color=color)
    s.line(x, cy + 16, x, y2, color=color)
    s.add(f'<rect x="{x - 16}" y="{cy - 16}" width="32" height="32" fill="{MASSFILL}" '
          f'stroke="{color}" stroke-width="1.6"/>')
    s.text(x, cy + 5, label, size=12.5, weight='bold')


def reference(s, x1, x2, y):
    s.line(x1, y, x2, y, width=2.2)
    x = x1
    while x <= x2:
        s.line(x, y, x - 7, y + 8, width=1.1)
        x += 10


def curved_torque(s, cx, cy, label, color=BLUE):
    """A curved arrow around a shaft seen side-on (an arc above the shaft)."""
    s.path(f'M {cx - 16} {cy + 4} A 16 22 0 0 1 {cx + 16} {cy + 4}', color, 2)
    s.add(f'<polygon points="{cx + 16},{cy + 10} {cx + 11},{cy} {cx + 21},{cy + 1}" '
          f'fill="{color}"/>')
    s.text(cx, cy - 26, label, size=13, color=color, weight='bold')


# --------------------------------------------------------------------------- 08: element symbols
def elements():
    s = Svg(640, 250, 'The three translational elements: a mass M with force F and displacement x, '
                      'a spring K between ends x1 and x2, and a damper f between ends with '
                      'velocities v1 and v2, each with its force equation underneath')
    mass(s, 50, 60, 110, 70, 'M')
    arrow(s, (160, 95), (205, 95), 'F', lab_dy=-8, color=BLUE)
    arrow(s, (70, 45), (130, 45), 'x', lab_dx=10, lab_dy=5, anchor='start', color=GREY)
    s.text(105, 185, 'F = M dv/dt = M d²x/dt²', size=13)
    s.text(105, 208, 'stores kinetic energy', size=11.5, color=GREY)
    node_dot(s, 260, 95)
    node_dot(s, 380, 95)
    spring(s, (260, 95), (380, 95), 'K', side=-1)
    s.text(260, 125, 'x₁', size=12.5, color=GREY)
    s.text(380, 125, 'x₂', size=12.5, color=GREY)
    s.text(320, 185, 'F = K(x₁ − x₂)', size=13)
    s.text(320, 208, 'stores potential energy', size=11.5, color=GREY)
    node_dot(s, 470, 95)
    node_dot(s, 590, 95)
    damper(s, (470, 95), (590, 95), 'f', side=-1)
    s.text(470, 125, 'v₁', size=12.5, color=GREY)
    s.text(590, 125, 'v₂', size=12.5, color=GREY)
    s.text(530, 185, 'F = f(v₁ − v₂)', size=13)
    s.text(530, 208, 'dissipates energy', size=11.5, color=GREY)
    s.save('model-elements.svg', OUT)


def rot_elements():
    s = Svg(640, 250, 'The three rotational elements: an inertia J turned by torque T, a torsional '
                      'spring K twisted between angles theta1 and theta2, and a rotational damper f '
                      'between angular velocities omega1 and omega2, each with its torque equation')
    s.line(40, 100, 180, 100, width=3)
    s.add(f'<rect x="95" y="50" width="26" height="100" rx="3" fill="{MASSFILL}" stroke="{INK}" '
          f'stroke-width="1.6"/>')
    s.text(108, 172, 'J', size=14, weight='bold')
    curved_torque(s, 60, 100, 'T, θ')
    s.text(110, 205, 'T = J dω/dt = J d²θ/dt²', size=13)
    node_dot(s, 260, 100)
    node_dot(s, 380, 100)
    spring(s, (260, 100), (380, 100), 'K', side=-1)
    s.text(260, 130, 'θ₁', size=12.5, color=GREY)
    s.text(380, 130, 'θ₂', size=12.5, color=GREY)
    s.text(320, 205, 'T = K(θ₁ − θ₂)', size=13)
    s.text(320, 226, 'K in N·m/rad', size=11.5, color=GREY)
    node_dot(s, 470, 100)
    node_dot(s, 590, 100)
    damper(s, (470, 100), (590, 100), 'f', side=-1)
    s.text(470, 130, 'ω₁', size=12.5, color=GREY)
    s.text(590, 130, 'ω₂', size=12.5, color=GREY)
    s.text(530, 205, 'T = f(ω₁ − ω₂)', size=13)
    s.save('model-rot-elements.svg', OUT)


# --------------------------------------------------------------------------- 09: one mass
def msd_system():
    s = Svg(320, 330, 'A mass M hanging from a fixed ceiling by a spring K and a damper f side by '
                      'side, with a force F(t) pulling the mass down and its displacement x(t) '
                      'measured downward')
    ground(s, 60, 30, 240, 30, 'up')
    spring(s, (110, 30), (110, 160), 'K', side=1)
    damper(s, (190, 30), (190, 160), 'f', side=-1)
    mass(s, 80, 160, 140, 70, 'M')
    arrow(s, (150, 230), (150, 292), 'F(t)', lab_dy=22)
    arrow(s, (250, 170), (250, 225), 'x(t)', color=GREY, lab_dx=8, lab_dy=-20, anchor='start')
    s.save('model-msd-system.svg', OUT)


def msd_fbd():
    s = Svg(420, 300, 'Free-body diagram of the mass: the applied force F(t) acts downward, and '
                      'three forces resist it upward: the spring force Kx, the damper force f dx/dt '
                      'and the inertia force M d²x/dt²')
    mass(s, 140, 120, 140, 70, 'M')
    for x, lab in [(165, 'Kx'), (210, 'f dx/dt'), (255, 'M d²x/dt²')]:
        arrow(s, (x, 120), (x, 62), color=ORANGE)
    s.text(150, 48, 'Kx', size=13, color=ORANGE, weight='bold')
    s.text(210, 30, 'f dx/dt', size=13, color=ORANGE, weight='bold')
    s.text(285, 48, 'M d²x/dt²', size=13, color=ORANGE, weight='bold')
    arrow(s, (210, 190), (210, 255), 'F(t)', lab_dy=22)
    arrow(s, (320, 130), (320, 180), 'x', color=GREY, lab_dx=8, anchor='start')
    s.save('model-msd-fbd.svg', OUT)


def msd_network():
    s = Svg(440, 260, 'Mechanical network of the mass-spring-damper: one node x at the top and the '
                      'fixed reference at the bottom, with the force source F, the mass M, the '
                      'damper f and the spring K all connected between them in parallel')
    top, bot = 50, 210
    s.line(70, top, 390, top, width=2)
    s.text(60, top + 5, 'x', size=14, weight='bold', anchor='end')
    reference(s, 60, 400, bot)
    source(s, 90, top, bot, 'F')
    net_mass(s, 180, top, bot, 'M')
    damper(s, (270, top), (270, bot), 'f', side=-1)
    spring(s, (360, top), (360, bot), 'K', side=-1)
    for x in (90, 180, 270, 360):
        node_dot(s, x, top)
    s.save('model-msd-network.svg', OUT)


def cart_system():
    s = Svg(440, 250, 'A cart moving with displacement u(t). Inside it, a spring K and damper f in '
                      'parallel join the cart’s left wall to a mass M on small wheels, whose '
                      'displacement is y(t)')
    s.line(40, 70, 40, 200, width=2.4)
    s.line(40, 200, 400, 200, width=2.4)
    s.line(400, 200, 400, 150, width=2.4)
    wheel(s, 95, 214, 14)
    wheel(s, 345, 214, 14)
    s.line(20, 229, 420, 229, width=1.4, color=GREY)
    mass(s, 230, 100, 100, 85, 'M')
    wheel(s, 252, 191, 7)
    wheel(s, 308, 191, 7)
    spring(s, (40, 122), (230, 122), 'K', side=-1)
    damper(s, (40, 165), (230, 165), 'f', side=-1)
    arrow(s, (60, 45), (140, 45), 'u(t)', lab_dx=10, lab_dy=5, anchor='start')
    arrow(s, (245, 82), (315, 82), 'y(t)', color=GREY, lab_dx=10, lab_dy=5, anchor='start')
    s.save('model-cart-system.svg', OUT)


# --------------------------------------------------------------------------- 09: three masses
def three_mass_system():
    s = Svg(320, 500, 'Three masses hanging in a chain from a ceiling: spring K1 and damper f1 in '
                      'parallel hold M1, which carries force F1 and moves x1; spring K2 joins M1 to '
                      'M2, which carries force F2 and moves x2; spring K3 and damper f3 in parallel '
                      'join M2 to M3, which moves x3. All displacements are downward')
    ground(s, 60, 30, 240, 30, 'up')
    spring(s, (110, 30), (110, 115), 'K₁', side=1)
    damper(s, (190, 30), (190, 115), 'f₁', side=-1)
    mass(s, 80, 115, 140, 55, 'M₁')
    spring(s, (150, 170), (150, 265), 'K₂', side=1)
    mass(s, 80, 265, 140, 55, 'M₂')
    spring(s, (110, 320), (110, 415), 'K₃', side=1)
    damper(s, (190, 320), (190, 415), 'f₃', side=-1)
    mass(s, 80, 415, 140, 55, 'M₃')
    for y, fx, xl in [(115, 'F₁', 'x₁'), (265, 'F₂', 'x₂'), (415, None, 'x₃')]:
        arrow(s, (45, y + 5), (45, y + 50), xl, color=GREY, lab_dx=-6, lab_dy=-18, anchor='end')
        if fx:
            arrow(s, (245, y + 5), (245, y + 50), fx, lab_dx=8, lab_dy=-18, anchor='start')
    s.save('model-three-mass-system.svg', OUT)


def three_mass_network():
    s = Svg(690, 270, 'Mechanical network of the three-mass system: node x1 carries the force '
                      'source F1, mass M1, damper f1 and spring K1 to the reference; spring K2 joins '
                      'node x1 to node x2; node x2 carries the source F2 and mass M2; spring K3 and '
                      'damper f3 in parallel join node x2 to node x3; node x3 carries mass M3')
    top, bot = 80, 230
    reference(s, 30, 670, bot)
    s.line(50, top, 290, top, width=2)
    s.line(370, top, 480, top, width=2)
    s.line(580, top, 650, top, width=2)
    s.text(170, top - 14, 'x₁', size=14, weight='bold')
    s.text(425, top - 14, 'x₂', size=14, weight='bold')
    s.text(625, top - 14, 'x₃', size=14, weight='bold')
    source(s, 70, top, bot, 'F₁')
    net_mass(s, 135, top, bot, 'M₁')
    damper(s, (205, top), (205, bot), 'f₁', side=-1)
    spring(s, (270, top), (270, bot), 'K₁', side=-1)
    spring(s, (290, top), (370, top), 'K₂', side=1)
    source(s, 400, top, bot, 'F₂')
    net_mass(s, 455, top, bot, 'M₂')
    spring(s, (480, top), (580, top), 'K₃', side=1)
    s.line(480, top, 480, 40)
    s.line(580, top, 580, 40)
    damper(s, (480, 40), (580, 40), 'f₃', side=-1)
    net_mass(s, 625, top, bot, 'M₃')
    for x in (70, 135, 205, 270, 290, 370, 400, 455, 480, 580, 625):
        node_dot(s, x, top)
    s.save('model-three-mass-network.svg', OUT)


def quiz2_q5_network():
    s = Svg(520, 260, 'Mechanical network for two hanging masses: node x1 carries the force source F, '
                      'mass M1, damper f1 and spring K1 to the reference; spring K2 joins node x1 to '
                      'node x2; node x2 carries mass M2 to the reference')
    top, bot = 60, 220
    reference(s, 30, 500, bot)
    s.line(50, top, 300, top, width=2)
    s.line(390, top, 470, top, width=2)
    s.text(175, top - 14, 'x₁', size=14, weight='bold')
    s.text(430, top - 14, 'x₂', size=14, weight='bold')
    source(s, 75, top, bot, 'F')
    net_mass(s, 140, top, bot, 'M₁')
    damper(s, (210, top), (210, bot), 'f₁', side=-1)
    spring(s, (280, top), (280, bot), 'K₁', side=-1)
    spring(s, (300, top), (390, top), 'K₂', side=1)
    net_mass(s, 445, top, bot, 'M₂')
    for x in (75, 140, 210, 280, 300, 390, 445):
        node_dot(s, x, top)
    s.save('model-quiz-two-mass-network.svg', OUT)


def quiz2_q5_system():
    s = Svg(320, 350, 'Two masses hanging from a ceiling: spring K1 and damper f1 in parallel hold '
                      'M1, which carries a downward force F(t) and moves x1; spring K2 joins M1 to '
                      'M2 below, which moves x2')
    ground(s, 60, 30, 240, 30, 'up')
    spring(s, (110, 30), (110, 125), 'K₁', side=1)
    damper(s, (190, 30), (190, 125), 'f₁', side=-1)
    mass(s, 80, 125, 140, 60, 'M₁')
    spring(s, (150, 185), (150, 270), 'K₂', side=1)
    mass(s, 80, 270, 140, 60, 'M₂')
    arrow(s, (45, 130), (45, 180), 'x₁', color=GREY, lab_dx=-6, lab_dy=-18, anchor='end')
    arrow(s, (45, 275), (45, 325), 'x₂', color=GREY, lab_dx=-6, lab_dy=-18, anchor='end')
    arrow(s, (245, 130), (245, 180), 'F(t)', lab_dx=8, lab_dy=-18, anchor='start')
    s.save('model-quiz-two-mass-system.svg', OUT)


# --------------------------------------------------------------------------- 10: rotational
def disc(s, x, label, sub, top=55, h=100):
    s.add(f'<rect x="{x}" y="{top}" width="24" height="{h}" rx="3" fill="{MASSFILL}" '
          f'stroke="{INK}" stroke-width="1.6"/>')
    s.text(x + 12, top + h + 22, label, size=14, weight='bold')
    if sub:
        s.text(x + 12, top + h + 42, sub, size=12.5, color=GREY)


def rot_jkf_system():
    s = Svg(460, 230, 'Rotational system: a torque T(t) turns an inertia J through angle theta1; a '
                      'flexible shaft of torsional stiffness K joins J to a point at angle theta2, '
                      'where a rotational damper f connects it to a fixed wall')
    cy = 105
    s.line(30, cy, 100, cy, width=3)
    curved_torque(s, 55, cy, 'T(t)')
    disc(s, 100, 'J', 'θ₁', top=cy - 50)
    s.line(124, cy, 150, cy, width=3)
    spring(s, (150, cy), (290, cy), 'K (shaft)', side=-1, amp=9)
    node_dot(s, 290, cy)
    s.text(290, cy + 32, 'θ₂', size=12.5, color=GREY)
    damper(s, (290, cy), (410, cy), 'f', side=-1)
    ground(s, 410, cy - 50, 410, cy + 50, 'right')
    s.save('model-rot-jkf-system.svg', OUT)


def rot_jkf_network():
    s = Svg(440, 260, 'Rotational mechanical network: node theta1 carries the torque source T and the '
                      'inertia J to the reference; the shaft stiffness K joins node theta1 to node '
                      'theta2; node theta2 carries the damper f to the reference')
    top, bot = 60, 220
    reference(s, 30, 420, bot)
    s.line(50, top, 200, top, width=2)
    s.line(300, top, 390, top, width=2)
    s.text(125, top - 14, 'θ₁', size=14, weight='bold')
    s.text(345, top - 14, 'θ₂', size=14, weight='bold')
    source(s, 80, top, bot, 'T')
    net_mass(s, 170, top, bot, 'J')
    spring(s, (200, top), (300, top), 'K', side=1)
    damper(s, (360, top), (360, bot), 'f', side=-1)
    for x in (80, 170, 200, 300, 360):
        node_dot(s, x, top)
    s.save('model-rot-jkf-network.svg', OUT)


def three_inertia_system():
    s = Svg(560, 275, 'Three-inertia rotational system: a motor of inertia Jm, driven by torque T(t) '
                      'and turning through theta_m, is joined on the left by torsional spring K2 to '
                      'inertia J2 (angle theta2) and on the right by torsional spring K1 to inertia J1 '
                      '(angle theta1)')
    cy = 145
    disc(s, 60, 'J₂', 'θ₂', top=cy - 45, h=90)
    spring(s, (84, cy), (240, cy), 'K₂', side=-1, amp=9)
    disc(s, 240, 'Jₘ', 'θₘ', top=cy - 60, h=120)
    curved_torque(s, 252, cy - 78, '')
    s.text(252, 22, 'T(t)', size=13, color=BLUE, weight='bold')
    spring(s, (264, cy), (430, cy), 'K₁', side=-1, amp=9)
    disc(s, 430, 'J₁', 'θ₁', top=cy - 45, h=90)
    s.save('model-three-inertia.svg', OUT)


# --------------------------------------------------------------------------- 11: impulse response
def impulse_plot(wn):
    s = Svg(460, 260, 'Impulse response of a mass M = 2 kg on a spring K = 8 N/m: a sine wave '
                      'x(t) = 0.25 sin(2t) metres, starting at zero, peaking at 0.25 m and repeating '
                      'every pi seconds for ever because there is no damper')
    ox, oy, w, hh = 55, 130, 380, 90
    s.line(ox, oy, ox + w, oy, color=INK)
    s.line(ox, 25, ox, 235, color=INK)
    tmax = 7.0
    pts = []
    for k in range(301):
        t = tmax * k / 300
        x = 0.25 * math.sin(wn * t)
        pts.append((ox + w * t / tmax, oy - hh * x / 0.25))
    _poly(s, pts, BLUE, 2.2)
    s.line(ox - 4, oy - hh, ox + w, oy - hh, color='#e5e7eb', width=1)
    s.line(ox - 4, oy + hh, ox + w, oy + hh, color='#e5e7eb', width=1)
    s.text(ox - 8, oy - hh + 4, '0.25', size=11, anchor='end')
    s.text(ox - 8, oy + hh + 4, '−0.25', size=11, anchor='end')
    s.text(ox - 8, oy + 4, '0', size=11, anchor='end')
    for k in (1, 2):
        x = ox + w * (k * math.pi) / tmax
        s.line(x, oy - 4, x, oy + 4, color=INK)
        s.line(x, oy - hh, x, oy + hh, color='#e5e7eb', width=1)
        s.text(x + 4, oy - hh + 16, 'π s' if k == 1 else '2π s', size=11, anchor='start')
    s.text(ox + w, oy - 8, 't', size=12, anchor='end')
    s.text(ox + 8, 20, 'x(t), m', size=12, anchor='start')
    s.save('model-impulse-response.svg', OUT)


# --------------------------------------------------------------------------- 16: block diagrams
BW, BH, SR = 54, 34, 11      # block width/height, summing-junction radius


def bblock(s, x, y, label):
    s.add(f'<rect x="{x - BW / 2}" y="{y - BH / 2}" width="{BW}" height="{BH}" rx="2" '
          f'fill="{MASSFILL}" stroke="{INK}" stroke-width="1.5"/>')
    s.text(x, y + 5, label, size=14, weight='bold')


def bsum(s, x, y):
    s.add(f'<circle cx="{x}" cy="{y}" r="{SR}" fill="white" stroke="{INK}" stroke-width="1.5"/>')


def wire(s, pts, head=True):
    _poly(s, pts, INK, 1.5)
    if head:
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        u, n, L = _frame((x1, y1), (x2, y2))
        a = (x2 - u[0] * 9 + n[0] * 4, y2 - u[1] * 9 + n[1] * 4)
        b = (x2 - u[0] * 9 - n[0] * 4, y2 - u[1] * 9 - n[1] * 4)
        s.add(f'<polygon points="{x2},{y2} {a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f}" '
              f'fill="{INK}"/>')


def sign(s, x, y, t):
    s.text(x, y, t, size=15, weight='bold')


def ends(s, y, xr, xc, rx_to, cx_from):
    s.text(xr, y + 5, 'R(s)', size=14, anchor='middle')
    wire(s, [(xr + 22, y), (rx_to, y)])
    wire(s, [(cx_from, y), (xc - 24, y)])
    s.text(xc, y + 5, 'C(s)', size=14, anchor='middle')


def bd_checks():
    import random
    rnd = random.Random(7)

    def c():
        return complex(rnd.uniform(-2, 2), rnd.uniform(-2, 2))
    for _ in range(5):
        G1, G2, G3, G4, H1, H2, H3 = (c() for _ in range(7))
        # Quiz 1 fig 1&2: unknowns E, Z, C
        E, Z, Cc = solve([[1, H2, 0], [0, 1, -H1], [-G1 * (G2 - G3), 0, 1]], [1, -G4, 0])
        want = G1 * (G2 - G3) * (1 + G4 * H2) / (1 + G1 * H1 * H2 * (G2 - G3))
        assert agree(Cc, want), ('fig12', Cc, want)
        # Quiz 1 fig 3: unknowns e1, e2, e3, P, C
        G = G2 + G4
        x = solve([[1, 0, 0, 0, 1], [-G1, 1, 0, H2, 0], [0, -1, 1, 0, H3],
                   [0, 0, -G, 1, 0], [0, 0, 0, -G3, 1]], [1, 0, 0, 0, 0])
        want = G1 * G3 * G / (1 + G * (H2 + G1 * G3 + G3 * H3))
        assert agree(x[4], want), ('fig3', x[4], want)
        # Quiz 1 fig 4 (as transcribed): unknowns e1, e2, q, w, C
        x = solve([[1, 0, H1, 0, 0], [-G1, 1, H1, H2, 0], [0, -G2, 1, 0, 0],
                   [0, 0, -G3, 1, 0], [0, 0, G3, 0, 1]], [1, 0, 0, 0, G4])
        D = 1 + G1 * G2 * H1 + G2 * H1 + G2 * G3 * H2
        want = (G4 * D - G1 * G2 * G3) / D
        assert agree(x[4], want), ('fig4', x[4], want)
        # rules: single loop and two-loop quiz diagrams
        e, Cc = solve([[1, H1], [-G1 * G2, 1]], [1, 0])
        assert agree(Cc, G1 * G2 / (1 + G1 * G2 * H1))
        e1, e2, Cc = solve([[1, 0, 1], [-G1, 1, H1], [0, -G2, 1]], [1, 0, 0])
        assert agree(Cc, G1 * G2 / (1 + G2 * H1 + G1 * G2))
    assert agree(4 / (1 + 4 * 0.5), 4 / 3) and agree(6 / (1 + 3 + 6), 0.6)
    print('check block diagrams: ok')


def block_diagrams():
    bd_checks()
    # series
    d = Svg(360, 80, 'Two blocks G1 and G2 in series between R and C')
    y = 40
    ends(d, y, 30, 330, 95, 249)
    bblock(d, 122, y, 'G₁')
    wire(d, [(149, y), (195, y)])
    bblock(d, 222, y, 'G₂')
    d.save('model-bd-series.svg', OUT)
    # parallel
    d = Svg(380, 150, 'Two blocks G1 and G2 in parallel: the input splits, passes through each, '
                      'and the outputs are added at a summing junction')
    y = 75
    d.text(30, y + 5, 'R(s)', size=14)
    _poly(d, [(52, y), (100, y)])
    node_dot(d, 100, y)
    wire(d, [(100, y), (100, 35), (150, 35)])
    wire(d, [(100, y), (100, 115), (150, 115)])
    bblock(d, 177, 35, 'G₁')
    bblock(d, 177, 115, 'G₂')
    wire(d, [(204, 35), (260, 35), (260, y - SR)])
    wire(d, [(204, 115), (260, 115), (260, y + SR)])
    bsum(d, 260, y)
    sign(d, 272, 58, '+')
    sign(d, 273, 103, '±')
    wire(d, [(271, y), (322, y)])
    d.text(345, y + 5, 'C(s)', size=14)
    d.save('model-bd-parallel.svg', OUT)
    # one negative feedback loop
    d = Svg(360, 140, 'A negative feedback loop: R enters a summing junction, passes through G to '
                      'the output C, and C is fed back through H and subtracted at the junction')
    y = 50
    ends(d, y, 30, 335, 100 - SR, 260)
    bsum(d, 100, y)
    sign(d, 84, 42, '+')
    wire(d, [(100 + SR, y), (160, y)])
    bblock(d, 187, y, 'G')
    _poly(d, [(214, y), (260, y)])
    node_dot(d, 260, y)
    wire(d, [(260, y), (260, 110), (214, 110)])
    bblock(d, 187, 110, 'H')
    wire(d, [(160, 110), (100, 110), (100, y + SR)])
    sign(d, 112, 80, '−')
    d.save('model-bd-feedback.svg', OUT)
    # quiz: single loop around G1 G2
    d = Svg(430, 140, 'A single loop: R enters a summing junction, passes through G1 then G2 to give '
                      'C, and C is fed back through H and subtracted')
    y = 50
    ends(d, y, 30, 400, 100 - SR, 340)
    bsum(d, 100, y)
    sign(d, 84, 42, '+')
    wire(d, [(100 + SR, y), (160, y)])
    bblock(d, 187, y, 'G₁')
    wire(d, [(214, y), (240, y)])
    bblock(d, 267, y, 'G₂')
    _poly(d, [(294, y), (340, y)])
    node_dot(d, 340, y)
    wire(d, [(340, y), (340, 110), (254, 110)])
    bblock(d, 227, 110, 'H')
    wire(d, [(200, 110), (100, 110), (100, y + SR)])
    sign(d, 112, 80, '−')
    d.save('model-bd-q-single.svg', OUT)
    # quiz: inner loop H1 around G2, outer unity loop
    d = Svg(470, 180, 'Two loops: R minus C passes through G1; then H1 times C is subtracted and the '
                      'result passes through G2 to give C')
    y = 50
    ends(d, y, 30, 440, 100 - SR, 380)
    bsum(d, 100, y)
    sign(d, 84, 42, '+')
    wire(d, [(100 + SR, y), (143, y)])
    bblock(d, 170, y, 'G₁')
    wire(d, [(197, y), (240 - SR, y)])
    bsum(d, 240, y)
    sign(d, 224, 42, '+')
    wire(d, [(240 + SR, y), (283, y)])
    bblock(d, 310, y, 'G₂')
    _poly(d, [(337, y), (380, y)])
    node_dot(d, 380, y)
    node_dot(d, 380, 105)
    wire(d, [(380, 105), (337, 105)])
    bblock(d, 310, 105, 'H₁')
    wire(d, [(283, 105), (240, 105), (240, y + SR)])
    sign(d, 252, 80, '−')
    wire(d, [(380, y), (380, 150), (100, 150), (100, y + SR)])
    sign(d, 112, 80, '−')
    d.save('model-bd-q-two-loop.svg', OUT)
    # Quiz 1 figures 1 and 2
    d = Svg(530, 280, 'Quiz 1 figures 1 and 2: R enters a summing junction, passes through G1, then '
                      'splits into G2 (added) and G3 (subtracted) to give C. C is fed back through H1 '
                      'to a second junction, where G4 times R is subtracted; that result passes through '
                      'H2 and is subtracted at the first junction')
    y = 80
    d.text(28, y + 5, 'R(s)', size=14)
    _poly(d, [(50, y), (70, y)])
    node_dot(d, 70, y)
    wire(d, [(70, y), (120 - SR, y)])
    bsum(d, 120, y)
    sign(d, 104, 72, '+')
    wire(d, [(120 + SR, y), (163, y)])
    bblock(d, 190, y, 'G₁')
    _poly(d, [(217, y), (240, y)])
    node_dot(d, 240, y)
    wire(d, [(240, y), (240, y - 40), (275, y - 40)])
    wire(d, [(240, y), (240, y + 40), (275, y + 40)])
    bblock(d, 302, y - 40, 'G₃')
    bblock(d, 302, y + 40, 'G₂')
    wire(d, [(329, y - 40), (380, y - 40), (380, y - SR)])
    wire(d, [(329, y + 40), (380, y + 40), (380, y + SR)])
    bsum(d, 380, y)
    sign(d, 393, y - 18, '−')
    sign(d, 393, y + 28, '+')
    _poly(d, [(380 + SR, y), (440, y)])
    wire(d, [(440, y), (478, y)])
    node_dot(d, 440, y)
    d.text(500, y + 5, 'C(s)', size=14)
    wire(d, [(440, y), (440, y + 110), (427, y + 110)])
    bblock(d, 400, y + 110, 'H₁')
    wire(d, [(373, y + 110), (300 + SR, y + 110)])
    bsum(d, 300, y + 110)
    sign(d, 322, y + 102, '+')
    wire(d, [(70, y), (70, y + 170), (203, y + 170)])
    bblock(d, 230, y + 170, 'G₄')
    wire(d, [(257, y + 170), (300, y + 170), (300, y + 110 + SR)])
    sign(d, 312, y + 140, '−')
    wire(d, [(300 - SR, y + 110), (227, y + 110)])
    bblock(d, 200, y + 110, 'H₂')
    wire(d, [(173, y + 110), (120, y + 110), (120, y + SR)])
    sign(d, 132, y + 30, '−')
    d.save('model-bd-quiz1-fig12.svg', OUT)
    # Quiz 1 figure 3
    d = Svg(640, 300, 'Quiz 1 figure 3: R minus C (unity feedback) passes through G1; H2 times the '
                      'signal after the parallel pair is subtracted, then H3 times C is subtracted; the '
                      'result passes through G2 and G4 in parallel, then G3, to give C')
    y = 120
    ends(d, y, 28, 610, 90 - SR, 565)
    bsum(d, 90, y)
    sign(d, 74, y - 8, '+')
    wire(d, [(90 + SR, y), (128, y)])
    bblock(d, 155, y, 'G₁')
    wire(d, [(182, y), (220 - SR, y)])
    bsum(d, 220, y)
    sign(d, 204, y - 8, '+')
    wire(d, [(220 + SR, y), (275 - SR, y)])
    bsum(d, 275, y)
    sign(d, 259, y - 8, '+')
    _poly(d, [(275 + SR, y), (315, y)])
    node_dot(d, 315, y)
    wire(d, [(315, y), (315, y - 40), (338, y - 40)])
    wire(d, [(315, y), (315, y + 40), (338, y + 40)])
    bblock(d, 365, y - 40, 'G₂')
    bblock(d, 365, y + 40, 'G₄')
    wire(d, [(392, y - 40), (420, y - 40), (420, y - SR)])
    wire(d, [(392, y + 40), (420, y + 40), (420, y + SR)])
    bsum(d, 420, y)
    sign(d, 432, y - 18, '+')
    sign(d, 432, y + 28, '+')
    _poly(d, [(420 + SR, y), (455, y)])
    node_dot(d, 455, y)
    wire(d, [(455, y), (483, y)])
    bblock(d, 510, y, 'G₃')
    _poly(d, [(537, y), (565, y)])
    node_dot(d, 565, y)
    wire(d, [(455, y), (455, y + 100), (367, y + 100)])
    bblock(d, 340, y + 100, 'H₂')
    wire(d, [(313, y + 100), (220, y + 100), (220, y + SR)])
    sign(d, 232, y + 30, '−')
    wire(d, [(565, y), (565, y - 90), (447, y - 90)])
    bblock(d, 420, y - 90, 'H₃')
    wire(d, [(393, y - 90), (275, y - 90), (275, y - SR)])
    sign(d, 287, y - 20, '−')
    wire(d, [(565, y), (565, y + 150), (90, y + 150), (90, y + SR)])
    sign(d, 102, y + 30, '−')
    d.save('model-bd-quiz1-fig3.svg', OUT)
    # Quiz 1 figure 4, as transcribed
    d = Svg(600, 300, 'Quiz 1 figure 4 as transcribed: R passes two summing junctions, G1, G2 and G3; '
                      'H1 times the signal between G2 and G3 is subtracted at both junctions; H2 times '
                      'the output of G3 is subtracted at the second junction; finally the output of G3 '
                      'is subtracted from G4 times R to give C')
    y = 110
    d.text(28, y + 5, 'R(s)', size=14)
    _poly(d, [(50, y), (65, y)])
    node_dot(d, 65, y)
    wire(d, [(65, y), (110 - SR, y)])
    bsum(d, 110, y)
    sign(d, 94, y - 8, '+')
    wire(d, [(110 + SR, y), (148, y)])
    bblock(d, 175, y, 'G₁')
    wire(d, [(202, y), (240 - SR, y)])
    bsum(d, 240, y)
    sign(d, 224, y - 8, '+')
    wire(d, [(240 + SR, y), (278, y)])
    bblock(d, 305, y, 'G₂')
    _poly(d, [(332, y), (355, y)])
    node_dot(d, 355, y)
    wire(d, [(355, y), (383, y)])
    bblock(d, 410, y, 'G₃')
    _poly(d, [(437, y), (460, y)])
    node_dot(d, 460, y)
    wire(d, [(460, y), (510 - SR, y)])
    bsum(d, 510, y)
    sign(d, 494, y - 8, '−')
    wire(d, [(510 + SR, y), (548, y)])
    d.text(572, y + 5, 'C(s)', size=14)
    wire(d, [(355, y), (355, y - 80), (317, y - 80)])
    bblock(d, 290, y - 80, 'H₁')
    _poly(d, [(263, y - 80), (110, y - 80)])
    node_dot(d, 240, y - 80)
    wire(d, [(110, y - 80), (110, y - SR)])
    wire(d, [(240, y - 80), (240, y - SR)])
    sign(d, 122, y - 22, '−')
    sign(d, 252, y - 22, '−')
    wire(d, [(460, y), (460, y + 90), (377, y + 90)])
    bblock(d, 350, y + 90, 'H₂')
    wire(d, [(323, y + 90), (240, y + 90), (240, y + SR)])
    sign(d, 252, y + 32, '−')
    wire(d, [(65, y), (65, y + 160), (273, y + 160)])
    bblock(d, 300, y + 160, 'G₄')
    wire(d, [(327, y + 160), (510, y + 160), (510, y + SR)])
    sign(d, 522, y + 32, '+')
    d.save('model-bd-quiz1-fig4.svg', OUT)

# --------------------------------------------------------------------------- 12-13: circuits
def resistor(s, p1, p2, label=None, side=1, color=INK):
    spring(s, p1, p2, label, side=side, coils=3, amp=6, color=color)


def inductor(s, p1, p2, label=None, side=1, bumps=4, color=INK):
    u, n, L = _frame(p1, p2)
    a, b = 0.25, 0.75
    pts = [p1, _at(p1, u, n, L, a)]
    for k in range(bumps):
        t0 = a + (b - a) * k / bumps
        for j in range(1, 13):
            ang = math.pi * j / 12
            t = t0 + (b - a) / bumps * (1 - math.cos(ang)) / 2
            pts.append(_at(p1, u, n, L, t, side * 8 * math.sin(ang)))
    pts += [_at(p1, u, n, L, b), p2]
    _poly(s, pts, color)
    if label:
        _label(s, p1, u, n, L, side, 18, label, color)


def capacitor(s, p1, p2, label=None, side=1, color=INK):
    u, n, L = _frame(p1, p2)
    _poly(s, [p1, _at(p1, u, n, L, 0.46)], color)
    _poly(s, [_at(p1, u, n, L, 0.54), p2], color)
    for t in (0.46, 0.54):
        _poly(s, [_at(p1, u, n, L, t, -12), _at(p1, u, n, L, t, 12)], color, 2.4)
    if label:
        _label(s, p1, u, n, L, side, 18, label, color)


def vsource(s, x, y1, y2, label):
    """Voltage source on a vertical wire, + at the top."""
    cy = (y1 + y2) / 2
    s.line(x, y1, x, cy - 16)
    s.line(x, cy + 16, x, y2)
    s.add(f'<circle cx="{x}" cy="{cy}" r="16" fill="white" stroke="{INK}" stroke-width="1.6"/>')
    s.text(x, cy - 3, '+', size=14, weight='bold')
    s.text(x, cy + 12, '−', size=14, weight='bold')
    s.text(x - 24, cy + 5, label, size=13, weight='bold', anchor='end')


def isource(s, x, y1, y2, label):
    source(s, x, y1, y2, label)


def loop_arrow(s, cx, cy, label, color=BLUE):
    """A clockwise mesh-current arrow."""
    s.path(f'M {cx - 14} {cy + 12} A 18 18 0 1 1 {cx + 14} {cy + 12}', color, 1.6)
    s.add(f'<polygon points="{cx + 14},{cy + 12} {cx + 7},{cy + 6} {cx + 17},{cy + 3}" '
          f'fill="{color}"/>')
    s.text(cx, cy + 34, label, size=12.5, color=color, weight='bold')


def series_rlc(labels, name, title, out_label=None):
    """labels: source, L, R, C, current."""
    e, l_, r_, c_, i_ = labels
    s = Svg(470, 250, title)
    x0, x1, y0, y1 = 80, 400, 50, 200
    vsource(s, x0, y0, y1, e)
    inductor(s, (x0, y0), (230, y0), l_, side=-1)
    resistor(s, (230, y0), (x1, y0), r_, side=-1)
    capacitor(s, (x1, y0), (x1, y1), c_, side=-1)
    s.line(x1, y1, x0, y1, width=1.8)
    loop_arrow(s, 240, 115, i_)
    if out_label:
        s.text(x1 + 40, 160, out_label, size=12.5, color=GREY, anchor='start')
    s.save(name, OUT)


def parallel_rlc(labels, name, title):
    """labels: source, C, R, L, node voltage."""
    i_, c_, r_, l_, e = labels
    s = Svg(500, 250, title)
    top, bot = 55, 205
    s.line(80, top, 440, top, width=1.8)
    s.text(260, top - 14, e, size=13, color=BLUE, weight='bold')
    reference(s, 60, 460, bot)
    isource(s, 80, top, bot, i_)
    capacitor(s, (200, top), (200, bot), c_, side=-1)
    resistor(s, (320, top), (320, bot), r_, side=-1)
    inductor(s, (440, top), (440, bot), l_, side=-1)
    for x in (80, 200, 320, 440):
        node_dot(s, x, top)
    s.save(name, OUT)


def rot_tv():
    s = Svg(560, 260, 'Torque-voltage analogue of the J-K-f system: two meshes. The left mesh, with '
                      'current omega1, holds the voltage source e = T and the inductor L = J; the '
                      'middle branch shared by both meshes is the capacitor C = 1/K; the right mesh, '
                      'with current omega2, holds the resistor R = f')
    x0, xm, x1, y0, y1 = 80, 290, 480, 50, 210
    vsource(s, x0, y0, y1, 'e = T')
    inductor(s, (x0, y0), (xm, y0), 'L = J', side=-1)
    capacitor(s, (xm, y0), (xm, y1), 'C = 1/K', side=1)
    s.line(xm, y0, x1, y0, width=1.8)
    resistor(s, (x1, y0), (x1, y1), 'R = f', side=-1)
    s.line(x1, y1, x0, y1, width=1.8)
    node_dot(s, xm, y0)
    node_dot(s, xm, y1)
    loop_arrow(s, 185, 120, 'i₁ = ω₁')
    loop_arrow(s, 385, 120, 'i₂ = ω₂')
    s.save('model-rot-tv.svg', OUT)


def rot_ti():
    s = Svg(520, 250, 'Torque-current analogue of the J-K-f system: node e1 (= omega1) holds the '
                      'current source i = T and the capacitor C = J to ground; the inductor L = 1/K '
                      'joins node e1 to node e2 (= omega2); node e2 holds the resistor R = 1/f to '
                      'ground')
    top, bot = 60, 210
    reference(s, 40, 480, bot)
    s.line(80, top, 210, top, width=1.8)
    s.line(330, top, 420, top, width=1.8)
    s.text(145, top - 14, 'e₁ = ω₁', size=13, color=BLUE, weight='bold')
    s.text(375, top - 14, 'e₂ = ω₂', size=13, color=BLUE, weight='bold')
    isource(s, 80, top, bot, 'i = T')
    capacitor(s, (190, top), (190, bot), 'C = J', side=-1)
    inductor(s, (210, top), (330, top), 'L = 1/K', side=1)
    resistor(s, (400, top), (400, bot), 'R = 1/f', side=-1)
    for x in (80, 190, 210, 330, 400):
        node_dot(s, x, top)
    s.save('model-rot-ti.svg', OUT)


def train_system():
    s = Svg(600, 220, 'Two-train-car system on frictionless wheels: a fixed wall on the left is '
                      'joined by spring K2 and damper f2 in parallel to car M2 (displacement y2, '
                      'velocity v2); M2 is joined by spring K1 and damper f1 in parallel to car M1 '
                      '(displacement y1, velocity v1); a force F pulls M1 to the right')
    ground(s, 40, 50, 40, 170, 'left')
    y_sp, y_dm = 85, 140
    mass(s, 200, 60, 110, 100, 'M₂')
    mass(s, 400, 60, 110, 100, 'M₁')
    spring(s, (40, y_sp), (200, y_sp), 'K₂', side=-1)
    damper(s, (40, y_dm), (200, y_dm), 'f₂', side=-1)
    spring(s, (310, y_sp), (400, y_sp), 'K₁', side=-1)
    damper(s, (310, y_dm), (400, y_dm), 'f₁', side=-1)
    for x in (225, 285, 425, 485):
        wheel(s, x, 170, 10)
    s.line(30, 181, 580, 181, color=GREY)
    arrow(s, (510, 110), (575, 110), 'F', lab_dy=-10)
    arrow(s, (215, 35), (275, 35), 'y₂, v₂', color=GREY, lab_dx=8, lab_dy=5, anchor='start')
    arrow(s, (415, 35), (475, 35), 'y₁, v₁', color=GREY, lab_dx=8, lab_dy=5, anchor='start')
    s.save('model-train-system.svg', OUT)


def train_network():
    s = Svg(560, 260, 'Mechanical network of the two-train-car system: node y2 carries M2, damper f2 '
                      'and spring K2 to the reference; spring K1 and damper f1 in parallel join node '
                      'y2 to node y1; node y1 carries M1 and the force source F')
    top, bot = 80, 230
    reference(s, 30, 540, bot)
    s.line(50, top, 240, top, width=2)
    s.line(350, top, 500, top, width=2)
    s.text(145, top - 46, 'y₂', size=14, weight='bold')
    s.text(425, top - 46, 'y₁', size=14, weight='bold')
    net_mass(s, 70, top, bot, 'M₂')
    damper(s, (145, top), (145, bot), 'f₂', side=-1)
    spring(s, (225, top), (225, bot), 'K₂', side=-1)
    spring(s, (240, top), (350, top), 'K₁', side=1)
    s.line(240, top, 240, 40)
    s.line(350, top, 350, 40)
    damper(s, (240, 40), (350, 40), 'f₁', side=-1)
    net_mass(s, 400, top, bot, 'M₁')
    source(s, 480, top, bot, 'F')
    for x in (70, 145, 225, 240, 350, 400, 480):
        node_dot(s, x, top)
    s.save('model-train-network.svg', OUT)


def train_fv():
    s = Svg(620, 270, 'Force-voltage analogue of the two-train-car system: two meshes. The left '
                      'mesh, current i1 = v1, holds the voltage source e = F and inductor L1 = M1; '
                      'the middle branch shared by both meshes holds R1 = f1 and C1 = 1/K1 in series; '
                      'the right mesh, current i2 = v2, holds inductor L2 = M2, then R2 = f2 and '
                      'C2 = 1/K2 in series')
    x0, xm, x1, y0, y1, ymid = 80, 300, 540, 50, 230, 140
    vsource(s, x0, y0, y1, 'e = F')
    inductor(s, (x0, y0), (xm, y0), 'L₁ = M₁', side=-1)
    resistor(s, (xm, y0), (xm, ymid), 'R₁ = f₁', side=1)
    capacitor(s, (xm, ymid), (xm, y1), 'C₁ = 1/K₁', side=1)
    inductor(s, (xm, y0), (x1, y0), 'L₂ = M₂', side=-1)
    resistor(s, (x1, y0), (x1, ymid), 'R₂ = f₂', side=-1)
    capacitor(s, (x1, ymid), (x1, y1), 'C₂ = 1/K₂', side=-1)
    s.line(x1, y1, x0, y1, width=1.8)
    node_dot(s, xm, y0)
    node_dot(s, xm, y1)
    loop_arrow(s, 190, 125, 'i₁ = v₁')
    loop_arrow(s, 420, 125, 'i₂ = v₂')
    s.save('model-train-fv.svg', OUT)


def train_fi():
    s = Svg(620, 270, 'Force-current analogue of the two-train-car system: node e1 (= v1) holds the '
                      'current source i = F and capacitor C1 = M1 to ground; R1 = 1/f1 and '
                      'L1 = 1/K1 in parallel join node e1 to node e2 (= v2); node e2 holds C2 = M2, '
                      'R2 = 1/f2 and L2 = 1/K2 to ground')
    top, bot = 90, 240
    reference(s, 40, 590, bot)
    s.line(70, top, 230, top, width=1.8)
    s.line(350, top, 560, top, width=1.8)
    s.text(150, top - 50, 'e₁ = v₁', size=13, color=BLUE, weight='bold')
    s.text(470, top - 50, 'e₂ = v₂', size=13, color=BLUE, weight='bold')
    isource(s, 80, top, bot, 'i = F')
    capacitor(s, (190, top), (190, bot), 'C₁ = M₁', side=-1)
    inductor(s, (230, top), (350, top), 'L₁ = 1/K₁', side=1)
    s.line(230, top, 230, 45)
    s.line(350, top, 350, 45)
    resistor(s, (230, 45), (350, 45), 'R₁ = 1/f₁', side=-1)
    capacitor(s, (390, top), (390, bot), 'C₂ = M₂', side=-1)
    resistor(s, (470, top), (470, bot), 'R₂ = 1/f₂', side=-1)
    inductor(s, (550, top), (550, bot), 'L₂ = 1/K₂', side=-1)
    for x in (80, 190, 230, 350, 390, 470, 550):
        node_dot(s, x, top)
    s.save('model-train-fi.svg', OUT)


def quiz_two_mass_fi():
    s = Svg(560, 250, 'Force-current analogue of two hanging masses: node e1 holds the current '
                      'source i = F, C1 = M1, R1 = 1/f1 and L1 = 1/K1 to ground; L2 = 1/K2 joins node '
                      'e1 to node e2; node e2 holds C2 = M2 to ground')
    top, bot = 70, 220
    reference(s, 40, 530, bot)
    s.line(80, top, 360, top, width=1.8)
    s.line(450, top, 490, top, width=1.8)
    s.text(220, top - 16, 'e₁ = v₁', size=13, color=BLUE, weight='bold')
    s.text(470, top - 16, 'e₂ = v₂', size=13, color=BLUE, weight='bold')
    isource(s, 80, top, bot, 'i = F')
    capacitor(s, (165, top), (165, bot), 'C₁ = M₁', side=-1)
    resistor(s, (250, top), (250, bot), 'R₁ = 1/f₁', side=-1)
    inductor(s, (340, top), (340, bot), 'L₁ = 1/K₁', side=-1)
    inductor(s, (360, top), (450, top), 'L₂ = 1/K₂', side=1)
    capacitor(s, (480, top), (480, bot), 'C₂ = M₂', side=-1)
    for x in (80, 165, 250, 340, 360, 450, 480):
        node_dot(s, x, top)
    s.save('model-quiz-two-mass-fi.svg', OUT)


def train_checks():
    M1, M2, f1, f2, K1, K2 = 1.2, 0.8, 0.5, 0.3, 6.0, 4.0
    for s_ in TEST_S:
        A1 = M1 * s_ * s_ + f1 * s_ + K1
        B = f1 * s_ + K1
        A2 = M2 * s_ * s_ + (f1 + f2) * s_ + K1 + K2
        y1, y2 = solve([[A1, -B], [-B, A2]], [1, 0])
        D = A1 * A2 - B * B
        assert agree(y1, A2 / D) and agree(y2, B / D)
        # force-voltage: mesh impedances in s with i = s*y, e = F  (L s + R + 1/(C s))
        Z1 = M1 * s_ + f1 + K1 / s_
        Zs = f1 + K1 / s_
        Z2 = M2 * s_ + f2 + K2 / s_ + Zs
        i1, i2 = solve([[Z1, -Zs], [-Zs, Z2]], [1, 0])
        assert agree(i1, s_ * y1) and agree(i2, s_ * y2)
        # force-current: node admittances C s + 1/R + 1/(L s) with e = s*y, i = F
        Y1 = M1 * s_ + f1 + K1 / s_
        Ys = f1 + K1 / s_
        Y2 = M2 * s_ + f2 + K2 / s_ + Ys
        e1, e2 = solve([[Y1, -Ys], [-Ys, Y2]], [1, 0])
        assert agree(e1, s_ * y1) and agree(e2, s_ * y2)
    # lesson 10's X2/F for two hanging masses
    Ma, Mb, fa, Ka, Kb = 1.0, 2.0, 0.6, 4.0, 3.0
    for s_ in TEST_S:
        A = Ma * s_ * s_ + fa * s_ + Ka + Kb
        Bq = Mb * s_ * s_ + Kb
        x1, x2 = solve([[A, -Kb], [-Kb, Bq]], [1, 0])
        assert agree(x2, Kb / (A * Bq - Kb * Kb))
    # quiz: M1 = M2 = K1 = K2 = 1, no dampers -> denominator s^4 + 3 s^2 + 1
    for s_ in TEST_S:
        A1, B, A2 = s_ * s_ + 1, 1, s_ * s_ + 2
        assert agree(A1 * A2 - B * B, s_ ** 4 + 3 * s_ ** 2 + 1)
    w_lo = math.sqrt((3 - math.sqrt(5)) / 2)
    w_hi = math.sqrt((3 + math.sqrt(5)) / 2)
    assert agree(w_lo, 0.618034, 1e-6) and agree(w_hi, 1.618034, 1e-6), (w_lo, w_hi)
    print('check two-train car and analogies: ok')


# --------------------------------------------------------------------------- 12: seeing the analogies
RED = '#dc2626'
PURPLE = '#7c3aed'
# The two analogy tables of lesson 12, as data: mechanical element -> (force-voltage, force-current).
ANALOGY = {
    'F': ('e = F', 'i = F'),
    'M': ('L = M', 'C = M'),
    'f': ('R = f', 'R = 1/f'),
    'K': ('C = 1/K', 'L = 1/K'),
}
ROW_COLOR = {'F': RED, 'M': BLUE, 'f': ORANGE, 'K': GREEN}


def analogy_checks():
    """The dictionary must agree with the series and parallel RLC equations term for term:
    force-voltage  L q'' + R q' + q/C = e   vs   M x'' + f x' + K x = F  ->  L=M, R=f, 1/C=K
    force-current  C p'' + p'/R + p/L = i   vs   same                    ->  C=M, 1/R=f, 1/L=K"""
    M, f, K = 2.0, 3.0, 5.0
    L_fv, R_fv, C_fv = M, f, 1 / K
    C_fi, R_fi, L_fi = M, 1 / f, 1 / K
    assert (L_fv, R_fv, 1 / C_fv) == (M, f, K) and (C_fi, 1 / R_fi, 1 / L_fi) == (M, f, K)
    assert ANALOGY['M'] == ('L = M', 'C = M') and ANALOGY['K'] == ('C = 1/K', 'L = 1/K')


def analogy_dictionary():
    s = Svg(600, 520, 'The analogy dictionary: each mechanical element beside its partner in each analogy. '
                      'Force F becomes a voltage source e = F (force-voltage) or a current source i = F (force-current); '
                      'mass M becomes an inductor L = M or a capacitor C = M; damper f becomes a resistor R = f or '
                      'R = 1/f; spring K becomes a capacitor C = 1/K or an inductor L = 1/K')
    cols = [(130, 'Mechanical'), (330, 'Force–voltage'), (500, 'Force–current')]
    for x, h in cols:
        s.text(x, 30, h, size=14, weight='bold')
    rows = ['F', 'M', 'f', 'K']
    names = {'F': 'Force', 'M': 'Mass', 'f': 'Damper', 'K': 'Spring'}
    for r, key in enumerate(rows):
        y1, y2 = 55 + r * 115, 145 + r * 115
        col = ROW_COLOR[key]
        s.add(f'<rect x="10" y="{y1 - 8}" width="580" height="{y2 - y1 + 16}" rx="8" fill="{col}" fill-opacity="0.07"/>')
        s.text(20, (y1 + y2) / 2 + 5, names[key], size=13, color=col, weight='bold', anchor='start')
        fv, fi = ANALOGY[key]
        x = 150
        if key == 'F':
            source(s, x, y1, y2, 'F')
            vsource(s, 350, y1, y2, fv)
            isource(s, 520, y1, y2, fi)
        elif key == 'M':
            net_mass(s, x, y1, y2, 'M', color=col)
            inductor(s, (350, y1), (350, y2), fv, side=-1, color=col)
            capacitor(s, (520, y1), (520, y2), fi, side=-1, color=col)
        elif key == 'f':
            damper(s, (x, y1), (x, y2), 'f', side=-1, color=col)
            resistor(s, (350, y1), (350, y2), fv, side=-1, color=col)
            resistor(s, (520, y1), (520, y2), fi, side=-1, color=col)
        else:
            spring(s, (x, y1), (x, y2), 'K', side=-1, color=col)
            capacitor(s, (350, y1), (350, y2), fv, side=-1, color=col)
            inductor(s, (520, y1), (520, y2), fi, side=-1, color=col)
    s.save('model-analogy-dictionary.svg', OUT)


def msd_conversion():
    s = Svg(700, 600, 'Converting the mass-spring-damper in four stages, with each element in its own colour. '
                      'Top left, the system: mass M hanging from spring K and damper f, pulled by F. Top right, its '
                      'mechanical network: one node x with F, M, f and K in parallel to the reference. Bottom left, the '
                      'force-current circuit has the same shape: current source F with C = M, R = 1/f and L = 1/K in '
                      'parallel. Bottom right, the force-voltage circuit is its dual: voltage source F with L = M, R = f '
                      'and C = 1/K in series around one loop')
    # panel 1: system
    s.text(160, 26, '1. The system', size=14, weight='bold')
    ground(s, 70, 50, 250, 50, 'up')
    spring(s, (115, 50), (115, 150), 'K', side=1, color=GREEN)
    damper(s, (205, 50), (205, 150), 'f', side=-1, color=ORANGE)
    s.add(f'<rect x="90" y="150" width="140" height="56" rx="3" fill="{MASSFILL}" stroke="{BLUE}" stroke-width="2"/>')
    s.text(160, 184, 'M', size=14, weight='bold', color=BLUE)
    arrow(s, (160, 206), (160, 256), 'F(t)', color=RED, lab_dy=20)
    # panel 2: network
    s.text(520, 26, '2. Its mechanical network', size=14, weight='bold')
    top, bot = 70, 230
    s.line(400, top, 650, top, width=2)
    s.text(392, top + 5, 'x', size=14, weight='bold', anchor='end')
    reference(s, 390, 660, bot)
    source(s, 425, top, bot, '')
    s.text(403, (top + bot) / 2 + 5, 'F', size=13, weight='bold', color=RED, anchor='end')
    net_mass(s, 500, top, bot, 'M', color=BLUE)
    damper(s, (575, top), (575, bot), 'f', side=-1, color=ORANGE)
    spring(s, (640, top), (640, bot), 'K', side=-1, color=GREEN)
    for x in (425, 500, 575, 640):
        node_dot(s, x, top)
    s.line(345, 285, 345, 580, color='#d1d5db', width=1)
    s.line(20, 285, 680, 285, color='#d1d5db', width=1)
    # panel 3: force-current, same shape
    s.text(160, 312, '3. Force–current: same shape', size=14, weight='bold')
    top, bot = 360, 520
    s.line(55, top, 270, top, width=1.8)
    s.text(170, top - 12, 'node voltage e = v', size=12, color=GREY, weight='bold')
    reference(s, 40, 290, bot)
    isource(s, 55, top, bot, '')
    s.text(33, (top + bot) / 2 + 5, 'i = F', size=12, weight='bold', color=RED, anchor='end')
    capacitor(s, (120, top), (120, bot), 'C = M', side=-1, color=BLUE)
    resistor(s, (195, top), (195, bot), 'R = 1/f', side=-1, color=ORANGE)
    inductor(s, (270, top), (270, bot), 'L = 1/K', side=-1, color=GREEN)
    for x in (55, 120, 195, 270):
        node_dot(s, x, top)
    s.text(170, 560, 'parallel stays parallel', size=12, color=GREY)
    # panel 4: force-voltage, the dual
    s.text(520, 312, '4. Force–voltage: the dual', size=14, weight='bold')
    x0, x1, y0, y1 = 420, 610, 370, 520
    vsource(s, x0, y0, y1, '')
    s.text(x0 - 22, (y0 + y1) / 2 + 22, 'e = F', size=12, weight='bold', color=RED, anchor='end')
    inductor(s, (x0, y0), (515, y0), 'L = M', side=-1, color=BLUE)
    resistor(s, (515, y0), (x1, y0), 'R = f', side=-1, color=ORANGE)
    capacitor(s, (x1, y0), (x1, y1), 'C = 1/K', side=-1, color=GREEN)
    s.line(x1, y1, x0, y1, width=1.8)
    loop_arrow(s, 515, 430, 'i = v')
    s.text(520, 560, 'parallel becomes series', size=12, color=GREY)
    s.save('model-msd-conversion.svg', OUT)


def circuits():
    train_checks()
    series_rlc(('e', 'L', 'R', 'C', 'i'), 'model-rlc-series.svg',
               'A series RLC circuit: a voltage source e drives current i around one loop through '
               'an inductor L, a resistor R and a capacitor C; the output e0 is the capacitor '
               'voltage', out_label='e₀')
    parallel_rlc(('i', 'C', 'R', 'L', 'node voltage e'), 'model-rlc-parallel.svg',
                 'A parallel RLC circuit: a current source i feeds one node with voltage e; a '
                 'capacitor C, a resistor R and an inductor L each connect that node to ground')
    series_rlc(('e = F', 'L = M', 'R = f', 'C = 1/K', 'i = v'), 'model-msd-fv.svg',
               'Force-voltage analogue of the mass-spring-damper: a voltage source e = F drives '
               'loop current i = v through L = M, R = f and C = 1/K in series')
    parallel_rlc(('i = F', 'C = M', 'R = 1/f', 'L = 1/K', 'e = v'), 'model-msd-fi.svg',
                 'Force-current analogue of the mass-spring-damper: a current source i = F feeds a '
                 'node with voltage e = v, which connects to ground through C = M, R = 1/f and '
                 'L = 1/K in parallel')
    rot_tv()
    rot_ti()
    train_system()
    train_network()
    train_fv()
    train_fi()
    quiz_two_mass_fi()
    analogy_checks()
    analogy_dictionary()
    msd_conversion()

if __name__ == '__main__':
    wn = checks()
    elements()
    rot_elements()
    msd_system()
    msd_fbd()
    msd_network()
    cart_system()
    three_mass_system()
    three_mass_network()
    quiz2_q5_system()
    quiz2_q5_network()
    rot_jkf_system()
    rot_jkf_network()
    three_inertia_system()
    impulse_plot(wn)
    block_diagrams()
    circuits()
    print('mechatronics model diagrams: done')
