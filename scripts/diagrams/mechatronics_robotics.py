"""Draw the robotic-systems diagrams (mechatronics section F) and check every worked number.

    python3 scripts/diagrams/mechatronics_robotics.py      # run from the vault root

The four numerical inverse-kinematics methods (Newton-Raphson, Jacobian transpose, Jacobian
pseudoinverse, damped least squares) are implemented here and run on the course's tutorial and
exam problems; the parallel-manipulator velocities, the Lagrangian equations of motion, the
one-link linearisation, the grasp indices and the potential-field numbers are computed the same
way. Every number the lessons quote is asserted before anything is drawn. No libraries needed.
Output: mechatronics/images/robot-*.svg.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import INK, Svg  # noqa: E402

OUT = os.path.join('mechatronics', 'images')
BLUE = '#2563eb'
ORANGE = '#f59e0b'
GREEN = '#059669'
PURPLE = '#7c3aed'
RED = '#dc2626'
GREY = '#6b7280'
LIGHT = '#e5e7eb'
LINKFILL = '#dbeafe'


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(1.0, abs(b))


# --------------------------------------------------------------------------- small matrix kit
def T(A):
    return [list(r) for r in zip(*A)]


def mul(A, B):
    return [[sum(a * b for a, b in zip(r, c)) for c in zip(*B)] for r in A]


def mv(A, v):
    return [sum(a * b for a, b in zip(r, v)) for r in A]


def inv(A):
    n = len(A)
    M = [list(map(float, r)) + [1.0 if i == j else 0.0 for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-14:
            raise ZeroDivisionError('singular matrix')
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [r[n:] for r in M]


def det2(A):
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


def norm(v):
    return math.sqrt(sum(x * x for x in v))


# --------------------------------------------------------------------------- planar serial arm
def fk(l, q):
    """End-effector (x, y) and all joint points of a planar serial arm."""
    pts, x, y, phi = [(0.0, 0.0)], 0.0, 0.0, 0.0
    for li, qi in zip(l, q):
        phi += qi
        x += li * math.cos(phi)
        y += li * math.sin(phi)
        pts.append((x, y))
    return (x, y), pts


def jac(l, q):
    """2 x n Jacobian: J[0][k] = -sum_{j>=k} l_j sin(phi_j), J[1][k] = +sum_{j>=k} l_j cos(phi_j)."""
    phis, phi = [], 0.0
    for qi in q:
        phi += qi
        phis.append(phi)
    n = len(q)
    return [[-sum(l[j] * math.sin(phis[j]) for j in range(k, n)) for k in range(n)],
            [sum(l[j] * math.cos(phis[j]) for j in range(k, n)) for k in range(n)]]


def step(method, l, q, xd, alpha=0.05, lam=0.1, clip=None):
    (x, y), _ = fk(l, q)
    e = [xd[0] - x, xd[1] - y]
    J = jac(l, q)
    if method == 'NR':
        dq = mv(inv(J), e)
    elif method == 'JT':
        dq = [alpha * v for v in mv(T(J), e)]
    elif method == 'JPI':
        dq = mv(mul(T(J), inv(mul(J, T(J)))), e)
    elif method == 'DLS':
        JJ = mul(J, T(J))
        JJ = [[JJ[i][j] + (lam * lam if i == j else 0) for j in range(2)] for i in range(2)]
        dq = mv(mul(T(J), inv(JJ)), e)
    if clip:
        big = max(abs(v) for v in dq)
        if big > clip:
            dq = [v * clip / big for v in dq]
    return [a + b for a, b in zip(q, dq)], e, dq, J


def solve_ik(method, l, q0, xd, eps, max_it=5000, **kw):
    q, history = list(q0), []
    for it in range(max_it):
        (x, y), _ = fk(l, q)
        err = math.hypot(xd[0] - x, xd[1] - y)
        history.append(err)
        if err < eps:
            return q, it, history
        q, e, dq, J = step(method, l, q, xd, **kw)
        if method in ('NR', 'JPI') and norm(dq) < eps:
            (x, y), _ = fk(l, q)
            history.append(math.hypot(xd[0] - x, xd[1] - y))
            return q, it + 1, history
    return q, max_it, history


def ik_checks():
    out = {}
    # 18: 2-DOF analytical IK, l1 = l2 = 1, target (1, 1)
    l = [1.0, 1.0]
    c2 = (1 + 1 - 1 - 1) / 2
    sols = []
    for s2 in (+1, -1):
        t2 = s2 * math.acos(c2)
        t1 = math.atan2(1, 1) - math.atan2(l[1] * math.sin(t2), l[0] + l[1] * math.cos(t2))
        (x, y), _ = fk(l, [t1, t2])
        assert close(x, 1) and close(y, 1)
        sols.append((math.degrees(t1), math.degrees(t2)))
    assert close(sols[0][0], 0) and close(sols[0][1], 90), sols
    assert close(sols[1][0], 90) and close(sols[1][1], -90), sols
    out['ik2'] = sols
    # 18 practice: l1 = l2 = 1, target (1.2, 0.8)
    c2 = (1.2 ** 2 + 0.8 ** 2 - 2) / 2
    assert close(c2, 0.04)
    for s2, want1 in ((+1, -10.16), (-1, 77.54)):
        t2 = s2 * math.acos(c2)
        t1 = math.atan2(0.8, 1.2) - math.atan2(math.sin(t2), 1 + math.cos(t2))
        assert close(math.degrees(t2), s2 * 87.71, 1e-3) and close(math.degrees(t1), want1, 1e-3)
        (x, y), _ = fk([1, 1], [t1, t2])
        assert close(x, 1.2) and close(y, 0.8)
    # 18 quiz: FK checks
    (x, y), _ = fk([1.0, 0.5], [math.radians(90), math.radians(-90)])
    assert close(x, 0.5) and close(y, 1.0)
    (x, y), _ = fk([1, 1, 1], [math.radians(30)] * 3)
    assert close(x, 1.36603, 1e-5) and close(y, 2.36603, 1e-5)
    # 19: exam Q5 / tutorial Q8: 3-DOF, Jacobian transpose, alpha = 0.05
    l = [1.8, 1.3, 1.0]
    xd = (2.8, 2.0)
    assert close(sum(l), 4.1) and close(math.hypot(*xd), 3.441, 1e-3)
    q1, e0, dq, J0 = step('JT', l, [0, 0, 0], xd, alpha=0.05)
    assert close(e0[0], -1.3) and close(e0[1], 2.0) and close(norm(e0), 2.385, 1e-3)
    assert all(close(a, b) for a, b in zip(J0[1], [4.1, 2.3, 1.0])) and max(map(abs, J0[0])) < 1e-12
    assert all(close(a, b) for a, b in zip(mv(T(J0), e0), [8.2, 4.6, 2.0]))
    assert all(close(a, b) for a, b in zip(q1, [0.41, 0.23, 0.10]))
    (x1, y1), _ = fk(l, q1)
    e1 = math.hypot(xd[0] - x1, xd[1] - y1)
    assert close(x1, 3.4317, 1e-3) and close(y1, 2.1681, 1e-3), (x1, y1)
    assert close(e1, 0.6537, 1e-3), e1
    out['q5'] = dict(x1=x1, y1=y1, e1=e1, red=1 - e1 / norm(e0))
    q2, _, _, _ = step('JT', l, q1, xd, alpha=0.05)
    (x2, y2), _ = fk(l, q2)
    e2 = math.hypot(xd[0] - x2, xd[1] - y2)
    assert e2 < e1, (e1, e2)
    out['q5']['e2'] = e2
    runs = {}
    for m, q0, kw in [('JT', [0, 0, 0], dict(alpha=0.05)), ('JPI', [0.1, 0.1, 0.1], {}),
                      ('DLS', [0, 0, 0], dict(lam=0.1))]:
        qf, its, hist = solve_ik(m, l, q0, xd, 5e-5, **kw)
        (xf, yf), _ = fk(l, qf)
        assert math.hypot(xd[0] - xf, xd[1] - yf) < 5e-5 + 1e-9 or m == 'JPI', (m, its)
        runs[m] = (qf, its, hist)
    out['q5runs'] = runs
    # tutorial Q2: 3-DOF JT, l = (2, 1, 1.5), target (3, 2.5)
    q, e, dq, J = step('JT', [2.0, 1.0, 1.5], [0, 0, 0], (3.0, 2.5), alpha=0.05)
    assert all(close(a, b) for a, b in zip(q, [0.5625, 0.3125, 0.1875])), q
    # tutorial Q1: 2-DOF NR, l = (1.5, 2.0), target (2, 2): singular at q = 0
    l = [1.5, 2.0]
    assert abs(det2(jac(l, [0, 0]))) < 1e-12
    J = jac(l, [0.1, 0.1])
    assert close(det2(J), 0.29950, 1e-3) and close(det2(J), 1.5 * 2.0 * math.sin(0.1))
    q, e, dq, J = step('NR', l, [0.1, 0.1], (2.0, 2.0))
    out['t1'] = dq
    assert close(dq[0], -7.5795, 1e-3) and close(dq[1], 14.092, 1e-3), dq
    # tutorial Q7: 2-DOF NR, l = (2.0, 2.5), target (3, 1.5), perturbed start (0.2, 0.2)
    l = [2.0, 2.5]
    J = jac(l, [0.2, 0.2])
    assert close(det2(J), 2.0 * 2.5 * math.sin(0.2)) and close(det2(J), 0.99335, 1e-3)
    q, e, dq, J = step('NR', l, [0.2, 0.2], (3.0, 1.5))
    out['t7'] = (det2(J), dq)
    assert close(dq[0], -2.8007, 1e-3) and close(dq[1], 5.2409, 1e-3), dq
    runs7 = {}
    for m, kw in [('NR', dict(clip=0.5)), ('DLS', dict(lam=0.1)), ('JT', dict(alpha=0.02))]:
        qf, its, hist = solve_ik(m, l, [0.2, 0.2], (3.0, 1.5), 1e-4, **kw)
        runs7[m] = (qf, its, hist)
    out['t7runs'] = runs7
    # tutorial Q9 reachability
    assert close(sum([1.5, 2.0, 1.5, 1.0]), 6.0) and close(math.hypot(5, 1), 5.0990, 1e-4)
    return out


# --------------------------------------------------------------------------- 20: singularities
def singularity_checks():
    l = [1.0, 1.0, 1.0]
    for t1 in (0.0, 0.7, 2.1):
        J = jac(l, [t1, 0.0, 0.0])
        JJ = mul(J, T(J))
        assert abs(det2(JJ)) < 1e-9
        for k in range(3):     # every column proportional to (-sin t1, cos t1)
            assert abs(J[0][k] * math.cos(t1) + J[1][k] * math.sin(t1)) < 1e-12
    # null-space projector: J (I - J+ J) = 0 at a non-singular pose
    q = [0.3, 0.6, 0.4]
    J = jac(l, q)
    Jp = mul(T(J), inv(mul(J, T(J))))
    P = [[(1.0 if i == j else 0.0) - v for j, v in enumerate(r)] for i, r in enumerate(mul(Jp, J))]
    assert all(abs(v) < 1e-12 for r in mul(J, P) for v in r)
    w = math.sqrt(det2(mul(J, T(J))))
    # tutorial Q4 (topic 2): C = |x_d - x_s|^2 with x_d = (5,4,2), x_s = (4,2,1)
    d = [5 - 4, 4 - 2, 2 - 1]
    assert close(sum(v * v for v in d), 6.0) and [2 * v for v in d] == [2, 4, 2]
    return dict(J=J, Jp=Jp, w=w, q=q)


# --------------------------------------------------------------------------- 21: parallel
BASE = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.866)]


def par_fk(l, q):
    tips = [(b[0] + li * math.cos(qi), b[1] + li * math.sin(qi)) for b, li, qi in zip(BASE, l, q)]
    return tips, (sum(p[0] for p in tips) / 3, sum(p[1] for p in tips) / 3)


def par_jac(l, q):
    return [[-li * math.sin(qi) for li, qi in zip(l, q)], [li * math.cos(qi) for li, qi in zip(l, q)]]


def parallel_checks():
    out = {}
    r = math.radians
    # exam Q4 / tutorial Q2
    l, q = [1.0, 0.9, 1.1], [r(30), r(45), r(60)]
    J = par_jac(l, q)
    want = [[-0.5000, -0.6364, -0.9526], [0.8660, 0.6364, 0.5500]]
    assert all(close(a, b, 1e-3) for ra, rb in zip(J, want) for a, b in zip(ra, rb)), J
    JJ = mul(J, T(J))
    assert close(JJ[0][0], 1.5624, 1e-3) and close(JJ[0][1], -1.3619, 1e-3)
    assert close(JJ[1][1], 1.4575, 1e-3), JJ
    dd = det2(JJ)
    assert close(dd, 0.4225, 2e-3) and close(math.sqrt(dd), 0.650, 2e-3), dd
    v = mv(inv(JJ), [1.5, 2.0])
    qd = mv(T(J), v)
    assert close(v[0], 11.62, 2e-3) and close(v[1], 12.23, 2e-3), v
    assert close(qd[0], 4.783, 2e-3) and close(qd[1], 0.389, 5e-3) and close(qd[2], -4.344, 2e-3), qd
    assert all(close(a, b) for a, b in zip(mv(J, qd), [1.5, 2.0]))
    out['q4'] = dict(J=J, JJ=JJ, det=dd, w=math.sqrt(dd), v=v, qd=qd)
    # tutorial Q1: legs pointed at (2.0, 1.5)
    ang = [math.degrees(math.atan2(1.5 - b[1], 2.0 - b[0])) for b in BASE]
    assert close(ang[0], 36.87, 1e-3) and close(ang[1], 56.31, 1e-3) and close(ang[2], 22.91, 1e-3)
    dist = [math.hypot(2.0 - b[0], 1.5 - b[1]) for b in BASE]
    out['t1'] = (ang, dist)
    # tutorial Q3
    l, q = [1.0, 0.8, 1.1], [r(30), r(45), r(60)]
    tips, c = par_fk(l, q)
    assert close(c[0], 1.161, 1e-3) and close(c[1], 0.962, 1e-3), c
    ang = [math.degrees(math.atan2(2.5 - b[1], 2.0 - b[0])) for b in BASE]
    assert close(ang[0], 51.34, 1e-3) and close(ang[1], 68.20, 1e-3) and close(ang[2], 47.45, 1e-3)
    J = par_jac(l, q)
    JJ = mul(J, T(J))
    assert close(det2(JJ), 0.397, 2e-3) and close(math.sqrt(det2(JJ)), 0.630, 2e-3)
    qd = mv(T(J), mv(inv(JJ), [1.0, 1.5]))
    assert close(qd[0], 3.48, 3e-3) and close(qd[1], 0.29, 1e-2) and close(qd[2], -3.05, 3e-3), qd
    out['t3'] = dict(tips=tips, c=c, ang=ang, det=det2(JJ), qd=qd)
    # type 1 singularity: two legs parallel -> det(JJ^T) = 0 when all legs parallel; check 3 legs
    Js = par_jac([1, 1, 1], [r(40)] * 3)
    assert abs(det2(mul(Js, T(Js)))) < 1e-12
    return out


# --------------------------------------------------------------------------- 22: dynamics
G = 9.81


def lagrangian_checks():
    m1 = m2 = 1.0
    l1 = 1.0
    lc1 = lc2 = 0.5
    I1 = I2 = 0.1

    def energies(q, qd):
        x1, y1 = lc1 * math.cos(q[0]), lc1 * math.sin(q[0])
        vx1, vy1 = -lc1 * math.sin(q[0]) * qd[0], lc1 * math.cos(q[0]) * qd[0]
        a = q[0] + q[1]
        y2 = l1 * math.sin(q[0]) + lc2 * math.sin(a)
        vx2 = -l1 * math.sin(q[0]) * qd[0] - lc2 * math.sin(a) * (qd[0] + qd[1])
        vy2 = l1 * math.cos(q[0]) * qd[0] + lc2 * math.cos(a) * (qd[0] + qd[1])
        K = (0.5 * m1 * (vx1 ** 2 + vy1 ** 2) + 0.5 * I1 * qd[0] ** 2
             + 0.5 * m2 * (vx2 ** 2 + vy2 ** 2) + 0.5 * I2 * (qd[0] + qd[1]) ** 2)
        P = m1 * G * y1 + m2 * G * y2
        return K, P

    def L(q, qd):
        K, P = energies(q, qd)
        return K - P

    def closed(q, qd, qdd):
        c2, s2 = math.cos(q[1]), math.sin(q[1])
        M11, M12, M22 = 1.7 + c2, 0.35 + 0.5 * c2, 0.35
        h = 0.5 * s2
        g1 = 1.5 * G * math.cos(q[0]) + 0.5 * G * math.cos(q[0] + q[1])
        g2 = 0.5 * G * math.cos(q[0] + q[1])
        t1 = M11 * qdd[0] + M12 * qdd[1] - h * (2 * qd[0] * qd[1] + qd[1] ** 2) + g1
        t2 = M12 * qdd[0] + M22 * qdd[1] + h * qd[0] ** 2 + g2
        return [t1, t2]

    hstep = 1e-4
    for q, qd, qdd in [([0.3, 0.7], [0.5, -0.4], [1.2, 0.3]), ([1.1, -0.6], [-0.9, 1.3], [-0.4, 2.0])]:
        # numerical Euler-Lagrange: d/dt(dL/dqd) - dL/dq, by finite differences along the motion
        def dL_dqd(qq, qqd, i):
            a, b = list(qqd), list(qqd)
            a[i] += hstep
            b[i] -= hstep
            return (L(qq, a) - L(qq, b)) / (2 * hstep)
        tau = []
        for i in range(2):
            qa = [x + v * hstep for x, v in zip(q, qd)]
            qb = [x - v * hstep for x, v in zip(q, qd)]
            va = [x + a * hstep for x, a in zip(qd, qdd)]
            vb = [x - a * hstep for x, a in zip(qd, qdd)]
            ddt = (dL_dqd(qa, va, i) - dL_dqd(qb, vb, i)) / (2 * hstep)
            a, b = list(q), list(q)
            a[i] += hstep
            b[i] -= hstep
            dLdq = (L(a, qd) - L(b, qd)) / (2 * hstep)
            tau.append(ddt - dLdq)
        want = closed(q, qd, qdd)
        assert all(abs(x - y) < 2e-4 for x, y in zip(tau, want)), (tau, want)
    K, P = energies([0.0, 0.0], [1.0, 0.0])
    assert close(K, 0.5 * (1.7 + 1.0) * 1.0)          # K = 1/2 M11 qd1^2 at q2 = 0
    print('check Lagrangian 2-DOF equations: ok')
    # tau = J^T F: two-link (1, 1) at q = (0, 90 deg) holding up a 1 kg load at the hand
    J = jac([1.0, 1.0], [0.0, math.pi / 2])
    tau = mv(T(J), [0.0, G * 1.0])
    assert close(tau[0], 9.81) and abs(tau[1]) < 1e-12, tau
    # quiz: stretched arm l = (1, 0.5), q = 0, hand pushes up with 20 N
    tau = mv(T(jac([1.0, 0.5], [0.0, 0.0])), [0.0, 20.0])
    assert close(tau[0], 30.0) and close(tau[1], 10.0), tau
    # one-link arm: tau = (1/3) m a^2 thdd + (1/2) m g a sin(th); linearised about th = 0
    m, a = 2.0, 1.0
    A21 = -3 * G / (2 * a)
    B2 = 3 / (m * a * a)
    assert close(A21, -14.715) and close(B2, 1.5)
    wn = math.sqrt(-A21)
    return dict(A21=A21, B2=B2, wn=wn)


def pendulum(theta0, a=1.0, linear=False, tmax=3.0, dt=1e-3):
    th, w, t, out = theta0, 0.0, 0.0, []
    k = 3 * G / (2 * a)
    while t <= tmax + 1e-12:
        out.append((t, th))
        acc = -k * (th if linear else math.sin(th))
        w += acc * dt
        th += w * dt
        t += dt
    return out


# --------------------------------------------------------------------------- 23: grasping
def grasp_checks():
    out = {}
    F, r, th = [10, 12, 8], [0.05, 0.06, 0.04], [30, 120, 240]
    tau = [f * ri for f, ri in zip(F, r)]
    assert all(close(a, b) for a, b in zip(tau, [0.5, 0.72, 0.32])) and close(sum(tau), 1.54)
    fx = sum(f * math.cos(math.radians(t)) for f, t in zip(F, th))
    fy = sum(f * math.sin(math.radians(t)) for f, t in zip(F, th))
    assert close(fx, -1.3397, 1e-3) and close(fy, 8.4641, 1e-3) and close(math.hypot(fx, fy), 8.5695, 1e-3)
    out['t1'] = dict(tau=tau, fx=fx, fy=fy)
    F, th = [5, 6, 7, 4], [45, 90, 135, 180]
    fx = sum(f * math.cos(math.radians(t)) for f, t in zip(F, th))
    fy = sum(f * math.sin(math.radians(t)) for f, t in zip(F, th))
    assert close(sum(F), 22) and close(fx, -5.4142, 1e-3) and close(fy, 14.4853, 1e-3)
    out['t2'] = dict(fx=fx, fy=fy, mag=math.hypot(fx, fy))
    F, th = [15, 14, 13], [45, 135, 225]
    fx = sum(f * math.cos(math.radians(t)) for f, t in zip(F, th))
    fy = sum(f * math.sin(math.radians(t)) for f, t in zip(F, th))
    assert close(math.hypot(fx, fy), math.sqrt(200), 1e-6)
    out['t3'] = math.hypot(fx, fy)
    P, F = [(0.1, 0.2), (-0.1, 0.3), (0.2, -0.1)], [12, 10, 15]
    Q4 = sum(f * math.hypot(*p) for f, p in zip(F, P))
    assert close(Q4, 9.1997, 1e-3), Q4
    P, F = [(0.1, 0.2), (-0.1, 0.3), (0.3, -0.2), (-0.2, 0.4)], [10, 12, 9, 11]
    Q5 = sum(f * math.hypot(*p) for f, p in zip(F, P))
    assert close(Q5, 14.195, 1e-3), Q5
    out['Q'] = (Q4, Q5)
    # friction worked example: 0.5 kg held by two fingers, mu = 0.4
    W = 0.5 * G
    N = W / (2 * 0.4)
    assert close(N, 6.13125, 1e-4)
    out['N'] = N
    # lesson 23 quiz numbers
    assert close(15 * 0.04, 0.6)
    assert close(10 * math.hypot(0.3, 0.4) + 20 * math.hypot(0.0, 0.2), 9.0)
    assert close(1.0 * G / (2 * 0.5), 9.81)
    return out


# --------------------------------------------------------------------------- 24: potential field
def urep(r, kr, r0):
    return 0.0 if r > r0 else 0.5 * kr * (1 / r - 1 / r0) ** 2


def field_checks():
    out = {}
    d1 = math.hypot(5 - 1, 6 - 2)
    assert close(d1, 5.6569, 1e-4)
    # obstacle centre (3, 4) lies on the straight line from (1, 2) to (5, 6)
    assert abs((6 - 2) * (3 - 1) - (5 - 1) * (4 - 2)) < 1e-12
    U1 = urep(math.hypot(4 - 3, 5 - 4), 10, 1.5)
    assert close(U1, 0.0081781, 1e-3), U1
    U1s = urep(math.hypot(4 - 3, 5 - 4) - 1.0, 10, 1.5)
    assert close(U1s, 15.2693, 1e-3), U1s
    d3 = math.hypot(5, 5)
    U3 = urep(math.hypot(2.0 - 2.5, 2.5 - 3.0), 100, 2.0)
    assert close(d3, 7.0711, 1e-4) and close(U3, 41.789, 1e-3), U3
    # tutorial 6 Q2: 3-link arm l = (1, 1.5, 1) cannot reach (3, 2)
    assert 1.0 + 1.5 + 1.0 < math.hypot(3, 2)
    out.update(d1=d1, U1=U1, U1s=U1s, d3=d3, U3=U3, reach=math.hypot(3, 2))
    # lesson 24 quiz numbers
    assert close(math.hypot(6, 8), 10) and close(urep(1.0, 10, 2.0), 1.25) and urep(2.5, 10, 2.0) == 0
    assert close(math.hypot(3, 2), 3.60555, 1e-5) and close(math.degrees(math.atan2(2, 3)), 33.69, 1e-3)
    return out


def descend(start, goal=(5.0, 6.0), obs=(3.0, 4.0), R=1.0, ka=1.0, kr=1.0, r0=0.5, vmax=1.0,
            dt=0.01, steps=6000):
    """Gradient descent on U_att + U_rep, with the repulsive distance measured from the obstacle's
    surface (so the barrier is infinite at the surface) and speed limited to vmax."""
    x, y = start
    path = [(x, y)]
    for _ in range(steps):
        fx, fy = -ka * (x - goal[0]), -ka * (y - goal[1])
        dx, dy = x - obs[0], y - obs[1]
        r = math.hypot(dx, dy)
        rs = r - R
        if rs <= r0:
            mag = kr * (1 / rs - 1 / r0) / (rs * rs)
            fx += mag * dx / r
            fy += mag * dy / r
        sp = math.hypot(fx, fy)
        if sp < 1e-6:
            break
        k = min(vmax, sp) / sp
        x, y = x + fx * k * dt, y + fy * k * dt
        path.append((x, y))
        if math.hypot(x - goal[0], y - goal[1]) < 0.02:
            break
    return path


# --------------------------------------------------------------------------- 25: performance (T_4)
def fk_abs(l, q):
    """T_4's convention: each q_i is an absolute link angle (x = sum l_i cos q_i)."""
    return (sum(li * math.cos(qi) for li, qi in zip(l, q)), sum(li * math.sin(qi) for li, qi in zip(l, q)))


def jac_abs(l, q):
    return [[-li * math.sin(qi) for li, qi in zip(l, q)], [li * math.cos(qi) for li, qi in zip(l, q)]]


def performance_checks():
    import random
    out = {}
    r = math.radians
    l1 = [0.5, 0.7, 0.8, 0.6, 0.9, 0.7]
    assert close(sum(l1), 4.2)
    x, y = fk_abs(l1, [r(a) for a in (45, 60, 90, 120, 150, 180)])
    assert close(x, -1.07587, 1e-4) and close(y, 2.72939, 1e-4), (x, y)
    out['q1pose'] = (x, y)
    # workspace with every q_i in [0, 180 deg]: grid Minkowski sum of the links' half-circle arcs
    def minkowski(h):
        R = {(0, 0)}
        for li in l1:
            n = int(math.pi * li / (h / 2)) + 1
            arc = {(round(li * math.cos(math.pi * k / n) / h), round(li * math.sin(math.pi * k / n) / h))
                   for k in range(n + 1)}
            R = {(u + c, v + d) for u, v in R for c, d in arc}
        return R
    a05 = len(minkowski(0.05)) * 0.05 ** 2
    grid = minkowski(0.025)
    a025 = len(grid) * 0.025 ** 2
    est = 2 * a025 - a05                     # remove the grid's edge over-count (error ~ h)
    half_disc = 0.5 * math.pi * 4.2 ** 2
    assert close(half_disc, 27.709, 1e-4) and 25.0 < est < 26.0 < a025 < half_disc, (a05, a025, est)
    # naive Monte Carlo (each joint uniform) badly under-samples the rim
    rnd = random.Random(11)
    pts = [fk_abs(l1, [rnd.uniform(0, math.pi) for _ in l1]) for _ in range(20000)]
    naive = len({(math.floor(px / 0.1), math.floor(py / 0.1)) for px, py in pts}) * 0.01
    assert naive < 20.0, naive
    out.update(area_grid=a025, area_est=est, half_disc=half_disc, naive=naive, grid=grid)
    # Q2: joint performance index = range / link length (deg per m)
    ranges = [180, 150, 160, 170, 180, 180]
    jpi = [a / b for a, b in zip(ranges, l1)]
    want = [360.0, 214.2857, 200.0, 283.3333, 200.0, 257.1429]
    assert all(close(a, b, 1e-4) for a, b in zip(jpi, want)), jpi
    order = sorted(range(6), key=lambda i: -jpi[i])
    assert order[:4] == [0, 3, 5, 1], order
    out['jpi'] = jpi
    # Q3: 4-DOF manipulability, absolute angles
    l3, q3 = [1.0, 1.5, 1.0, 1.2], [r(a) for a in (45, 60, 90, 120)]
    J = jac_abs(l3, q3)
    JJ = mul(J, T(J))
    w = math.sqrt(det2(JJ))
    out['q3'] = dict(J=J, det=det2(JJ), w=w)
    # Q4: error propagation at a chosen pose q = (30, 60, 90, 120, 150) deg, each joint +-0.01 rad
    l4, q4 = [0.8, 1.0, 1.2, 0.6, 1.0], [r(a) for a in (30, 60, 90, 120, 150)]
    J = jac_abs(l4, q4)
    dq = 0.01
    ex = math.sqrt(sum((v * dq) ** 2 for v in J[0]))
    ey = math.sqrt(sum((v * dq) ** 2 for v in J[1]))
    worst_x = sum(abs(v) * dq for v in J[0])
    out['q4'] = dict(J=J, ex=ex, ey=ey, e=math.hypot(ex, ey), worst_x=worst_x,
                     w=math.sqrt(det2(mul(J, T(J)))))
    # Q5: 3-D reach check
    l5 = [0.9, 1.1, 0.8, 1.2, 1.0, 1.0]
    d5 = math.sqrt(1.5 ** 2 + 2.0 ** 2 + 3.0 ** 2)
    assert close(sum(l5), 6.0) and close(d5, 3.90512, 1e-5)
    out['q5'] = dict(R=sum(l5), d=d5, sphere=4 / 3 * math.pi * 6 ** 3, hemi=2 / 3 * math.pi * 6 ** 3)
    # lesson 25 quiz numbers
    assert close(120 / 0.4, 300) and close(math.hypot(0.5 * 0.02, 0.3 * 0.02), 0.0116619, 1e-5)
    assert close(0.5 * math.pi * 2 ** 2, 6.28319, 1e-5)
    return out


def workspace_figure(grid, h=0.025):
    s = Svg(470, 290, 'Workspace of the 6-link arm with links 0.5, 0.7, 0.8, 0.6, 0.9 and 0.7 m and every '
                      'joint between 0 and 180 degrees: it fills almost all of the upper half of a disc '
                      'of radius 4.2 m, with thin gaps along the x-axis')
    P = frame(s, 235, 245, 50, (-4.5, 4.5), (0, 4.5), grid=1.0)
    rows = {}
    for u, v in grid:
        rows.setdefault(v, []).append(u)
    for v, us in rows.items():
        us.sort()
        start = prev = us[0]
        for u in us[1:] + [None]:
            if u is not None and u == prev + 1:
                prev = u
                continue
            x0, y0 = P((start - 0.5) * h, (v + 0.5) * h)
            x1, _ = P((prev + 0.5) * h, 0)
            s.add(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{h * 50 + 0.3:.1f}" '
                  f'fill="{BLUE}" fill-opacity="0.45"/>')
            if u is not None:
                start = prev = u
    s.path(' '.join(('M' if i == 0 else 'L') + f' {P(4.2 * math.cos(math.radians(t)), 4.2 * math.sin(math.radians(t)))[0]:.1f} '
                    f'{P(4.2 * math.cos(math.radians(t)), 4.2 * math.sin(math.radians(t)))[1]:.1f}'
                    for i, t in enumerate(range(0, 181, 3))), ORANGE, 2, dash='5 4')
    s.text(235, 30, 'dashed: R_max = 4.2 m (the half-disc bound)', size=12, color=ORANGE, weight='bold')
    s.save('robot-workspace.svg', OUT)

# --------------------------------------------------------------------------- drawing helpers
def frame(s, ox, oy, sc, xr, yr, grid=1.0, labels=True):
    """Light grid and axes for a world-coordinate drawing. Returns a world->screen mapper."""
    def P(x, y):
        return ox + x * sc, oy - y * sc
    x0, x1 = xr
    y0, y1 = yr
    g = x0
    while g <= x1 + 1e-9:
        a, b = P(g, y0), P(g, y1)
        s.line(a[0], a[1], b[0], b[1], color=LIGHT, width=1)
        if labels:
            s.text(a[0], a[1] + 15, f'{g:g}', size=10, color=GREY)
        g += grid
    g = y0
    while g <= y1 + 1e-9:
        a, b = P(x0, g), P(x1, g)
        s.line(a[0], a[1], b[0], b[1], color=LIGHT, width=1)
        if labels:
            s.text(a[0] - 6, a[1] + 4, f'{g:g}', size=10, color=GREY, anchor='end')
        g += grid
    return P


def draw_arm(s, P, pts, color=BLUE, width=6, opacity=1.0, joints=True):
    xy = [P(*p) for p in pts]
    s.add('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in xy) + f'" fill="none" '
          f'stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" '
          f'stroke-opacity="{opacity}"/>')
    if joints:
        for x, y in xy[:-1]:
            s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="white" stroke="{INK}" '
                  f'stroke-width="1.5" stroke-opacity="{opacity}"/>')
        x, y = xy[-1]
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{INK}" fill-opacity="{opacity}"/>')


def base_mark(s, P, x=0.0, y=0.0):
    bx, by = P(x, y)
    s.add(f'<polygon points="{bx - 11},{by + 12} {bx + 11},{by + 12} {bx},{by}" fill="{LIGHT}" '
          f'stroke="{INK}" stroke-width="1.3"/>')


def target(s, P, x, y, label=None, color=RED):
    tx, ty = P(x, y)
    s.add(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="7" fill="none" stroke="{color}" stroke-width="2"/>')
    s.line(tx - 10, ty, tx + 10, ty, color=color, width=1.5)
    s.line(tx, ty - 10, tx, ty + 10, color=color, width=1.5)
    if label:
        s.text(tx + 12, ty - 10, label, size=12, color=color, weight='bold', anchor='start')


def polyline(s, pts, color, width=2.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s.add('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" '
          f'stroke="{color}" stroke-width="{width}"{d}/>')


# --------------------------------------------------------------------------- diagrams
def serial_vs_parallel():
    s = Svg(620, 270, 'Left: a serial manipulator, one chain of links and joints from a base to the '
                      'end-effector. Right: a parallel manipulator, three legs from three base anchors '
                      'meeting at one moving platform')
    P = frame(s, 70, 225, 70, (0, 3), (0, 3), labels=False)
    _, pts = fk([1.4, 1.1, 0.7], [math.radians(50), math.radians(-35), math.radians(-40)])
    base_mark(s, P)
    draw_arm(s, P, pts)
    s.text(175, 255, 'Serial: one chain', size=13, weight='bold')
    ox = 360
    Pp = frame(s, ox, 225, 70, (0, 3), (0, 3), labels=False)
    anchors = [(0.2, 0.0), (2.8, 0.0), (1.5, 0.3)]
    plat = [(1.15, 2.0), (1.85, 2.0), (1.5, 2.45)]
    for a, p in zip(anchors, plat):
        base_mark(s, Pp, *a)
        draw_arm(s, Pp, [a, p], color=BLUE, width=5)
    xy = [Pp(*p) for p in plat]
    s.add('<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in xy) + f'" fill="{ORANGE}" '
          f'fill-opacity="0.35" stroke="{INK}" stroke-width="1.5"/>')
    s.text(ox + 105, 255, 'Parallel: legs share a platform', size=13, weight='bold')
    s.save('robot-serial-vs-parallel.svg', OUT)


def two_link_ik(sols):
    s = Svg(420, 360, 'A two-link arm with both links 1 m long reaching the target (1, 1) in two '
                      'ways: elbow-down with theta1 = 0 and theta2 = 90 degrees, and elbow-up with '
                      'theta1 = 90 and theta2 = -90 degrees')
    P = frame(s, 90, 300, 120, (-0.5, 2.0), (-0.5, 2.0), grid=0.5)
    base_mark(s, P)
    for (t1, t2), col, lab, off in [(sols[0], BLUE, 'elbow-down: θ₁ = 0°, θ₂ = 90°', 0),
                                    (sols[1], ORANGE, 'elbow-up: θ₁ = 90°, θ₂ = −90°', 18)]:
        _, pts = fk([1, 1], [math.radians(t1), math.radians(t2)])
        draw_arm(s, P, pts, color=col)
        s.text(95, 28 + off, lab, size=12.5, color=col, weight='bold', anchor='start')
    target(s, P, 1, 1, '(1, 1)')
    s.save('robot-two-link-ik.svg', OUT)


def jt_iterations(q5):
    l, xd = [1.8, 1.3, 1.0], (2.8, 2.0)
    s = Svg(460, 330, 'Jacobian-transpose solution of the 3-link arm (1.8, 1.3, 1.0 m) reaching '
                      '(2.8, 2.0): the start pose lies straight along the x-axis, the pose after one '
                      'iteration has joint angles 0.41, 0.23 and 0.10 rad and ends near (3.43, 2.17), '
                      'and the converged pose reaches the target')
    P = frame(s, 50, 290, 90, (0, 4.5), (-0.5, 3.0), grid=0.5)
    base_mark(s, P)
    qf = q5['q5runs']['JT'][0]
    for q, col, lab, op in [([0, 0, 0], GREY, 'start  q = (0, 0, 0)', 0.8),
                            ([0.41, 0.23, 0.10], ORANGE, 'after iteration 1', 1.0),
                            (qf, BLUE, 'converged', 1.0)]:
        _, pts = fk(l, q)
        draw_arm(s, P, pts, color=col, opacity=op, width=5)
    target(s, P, *xd, '(2.8, 2.0)')
    for i, (lab, col) in enumerate([('start  q = (0, 0, 0)', GREY), ('after iteration 1', ORANGE),
                                    ('converged', BLUE)]):
        s.text(335, 240 + 16 * i, lab, size=12.5, color=col, weight='bold', anchor='start')
    s.save('robot-jt-iterations.svg', OUT)


def convergence(runs, name, title, colors):
    s = Svg(520, 300, title)
    ox, oy, w, h = 70, 250, 400, 210
    s.line(ox, oy, ox + w, oy, color=INK)
    s.line(ox, oy, ox, oy - h, color=INK)
    lo, hi = -6, 1
    itmax = 60
    for k in range(lo, hi + 1):
        y = oy - h * (k - lo) / (hi - lo)
        s.line(ox, y, ox + w, y, color=LIGHT, width=1)
        s.text(ox - 6, y + 4, f'1e{k}', size=10, color=GREY, anchor='end')
    for it in range(0, itmax + 1, 10):
        x = ox + w * it / itmax
        s.text(x, oy + 16, str(it), size=10, color=GREY)
    s.text(ox + w / 2, oy + 36, 'iteration', size=12)
    s.text(ox + 4, oy - h - 8, 'position error ‖e‖ (log scale)', size=12, anchor='start')
    for i, (m, (qf, its, hist)) in enumerate(runs.items()):
        pts = []
        for it, e in enumerate(hist[:itmax + 1]):
            v = max(lo, min(hi, math.log10(max(e, 1e-12))))
            pts.append((ox + w * it / itmax, oy - h * (v - lo) / (hi - lo)))
        polyline(s, pts, colors[m], 2.2)
        label = f'{m}: {its} iterations' if its < 5000 else f'{m}: not converged'
        s.text(ox + w - 4, oy - 14 - 18 * (len(runs) - 1 - i), label, size=12, color=colors[m],
               weight='bold', anchor='end')
    s.save(name, OUT)


def manipulability_plot():
    s = Svg(480, 270, 'Manipulability w = |sin theta2| of a two-link arm with unit links, plotted '
                      'for theta2 from -180 to 180 degrees: it is zero at 0 and plus or minus 180 '
                      'degrees, the singular poses, and largest at plus or minus 90 degrees')
    ox, oy, w, h = 60, 220, 380, 170
    s.line(ox, oy, ox + w, oy, color=INK)
    s.line(ox + w / 2, oy, ox + w / 2, oy - h - 10, color=LIGHT)
    s.line(ox, oy, ox, oy - h - 10, color=INK)
    pts = [(ox + w * (t + 180) / 360, oy - h * abs(math.sin(math.radians(t)))) for t in range(-180, 181, 2)]
    polyline(s, pts, BLUE, 2.4)
    for t in (-180, -90, 0, 90, 180):
        x = ox + w * (t + 180) / 360
        s.text(x, oy + 16, f'{t}°', size=11, color=GREY)
    for t in (-180, 0, 180):
        x = ox + w * (t + 180) / 360
        s.circle(x, oy, 5, RED)
    s.text(ox - 6, oy - h + 4, '1', size=11, color=GREY, anchor='end')
    s.text(ox - 6, oy + 4, '0', size=11, color=GREY, anchor='end')
    s.text(ox + w / 2, oy + 38, 'elbow angle θ₂', size=12)
    s.text(ox + 6, oy - h - 16, 'manipulability w', size=12, anchor='start')
    s.text(ox + w / 2 + 8, oy - 12, 'singular', size=11, color=RED, anchor='start')
    s.save('robot-manipulability.svg', OUT)


def singular_poses():
    s = Svg(560, 230, 'A three-link planar arm in a normal pose (left) and in the arm singularity '
                      '(right), where theta2 = theta3 = 0 and all links lie on one line, so the hand '
                      'cannot move along that line')
    P = frame(s, 50, 190, 50, (0, 4), (0, 3), labels=False)
    _, pts = fk([1, 1, 1], [0.3, 0.6, 0.4])
    base_mark(s, P)
    draw_arm(s, P, pts)
    s.text(150, 220, 'normal: can move any way', size=12.5, weight='bold')
    P2 = frame(s, 320, 190, 50, (0, 4), (0, 3), labels=False)
    _, pts = fk([1, 1, 1], [0.5, 0.0, 0.0])
    base_mark(s, P2)
    draw_arm(s, P2, pts, color=RED)
    tip = P2(*pts[-1])
    u = (math.cos(0.5), -math.sin(0.5))
    s.line(tip[0], tip[1], tip[0] + 30 * u[0], tip[1] + 30 * u[1], color=GREY, width=1.5, dash='4 3')
    s.text(420, 220, 'stretched: θ₂ = θ₃ = 0', size=12.5, weight='bold', color=RED)
    s.save('robot-singular-poses.svg', OUT)


def parallel_figure(q4):
    s = Svg(460, 380, 'Three-legged planar parallel manipulator: base anchors B1 at (0, 0), B2 at '
                      '(1, 0) and B3 at (0.5, 0.866); legs of length 1.0, 0.9 and 1.1 m at angles 30, '
                      '45 and 60 degrees, each measured from its own anchor, with the leg tips and '
                      'their centroid marked')
    P = frame(s, 80, 320, 140, (-0.25, 2.25), (-0.25, 1.9), grid=0.5)
    l, q = [1.0, 0.9, 1.1], [math.radians(30), math.radians(45), math.radians(60)]
    tips, c = par_fk(l, q)
    bxy = [P(*b) for b in BASE]
    s.add('<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in bxy) + f'" fill="{LIGHT}" '
          f'fill-opacity="0.6" stroke="{GREY}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    for i, (b, t, col) in enumerate(zip(BASE, tips, [BLUE, GREEN, PURPLE])):
        base_mark(s, P, *b)
        draw_arm(s, P, [b, t], color=col, width=5)
        bx, by = P(*b)
        s.text(bx - 14, by + 26, f'B{i + 1}', size=12, weight='bold')
        tx, ty = P(*t)
        s.text(tx + 8, ty - 6, f'leg {i + 1}: {["30°", "45°", "60°"][i]}', size=11.5, color=col,
               weight='bold', anchor='start')
    cx, cy = P(*c)
    s.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{ORANGE}" stroke="{INK}"/>')
    s.text(cx + 8, cy + 16, 'centroid of tips', size=11.5, color=ORANGE, weight='bold', anchor='start')
    s.save('robot-parallel-legs.svg', OUT)


def pendulum_plot():
    s = Svg(520, 290, 'Swinging one-link arm (a = 1 m) released from rest: the nonlinear model '
                      'and the linearised model agree closely when released from 10 degrees, but '
                      'drift apart in period when released from 60 degrees')
    ox, oy, w, h = 60, 145, 420, 105
    s.line(ox, oy, ox + w, oy, color=INK)
    s.line(ox, oy - h, ox, oy + h, color=INK)
    for deg, colN, colL, sc in [(10, BLUE, '#93c5fd', 1.0), (60, ORANGE, '#fcd34d', 1.0)]:
        th0 = math.radians(deg)
        nl = pendulum(th0)
        li = pendulum(th0, linear=True)
        polyline(s, [(ox + w * t / 3.0, oy - h * th / math.radians(60)) for t, th in li[::10]], colL,
                 2.0, dash='5 4')
        polyline(s, [(ox + w * t / 3.0, oy - h * th / math.radians(60)) for t, th in nl[::10]], colN, 2.2)
    s.text(ox + w, oy + h + 22, 'time, s (0 to 3)', size=11.5, anchor='end')
    s.text(ox + 6, oy - h - 10, 'angle θ (±60° full scale)', size=11.5, anchor='start')
    s.text(ox + 10, 278, 'solid = nonlinear  ·  dashed = linearised  ·  blue 10°, orange 60°', size=12,
           anchor='start')
    s.save('robot-linearisation.svg', OUT)


def grasp_figure():
    s = Svg(460, 380, 'Three fingers acting on an object around the hand centre O: contact points at '
                      '30, 120 and 240 degrees and 5, 6 and 4 centimetres from O, each finger pushing '
                      'at right angles to its radius with 10, 12 and 8 newtons, so each turns the '
                      'object the same way about O')
    cx, cy, sc = 230, 195, 1900
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{0.065 * sc:.1f}" fill="#dbeafe" fill-opacity="0.45" '
          f'stroke="{GREY}" stroke-width="1" stroke-dasharray="4 4"/>')
    s.circle(cx, cy, 4, INK)
    s.text(cx - 10, cy + 18, 'O', size=13, weight='bold')
    for F, r, a, col in [(10, 0.05, 30, BLUE), (12, 0.06, 120, GREEN), (8, 0.04, 240, PURPLE)]:
        ar = math.radians(a)
        px, py = cx + r * sc * math.cos(ar), cy - r * sc * math.sin(ar)
        s.line(cx, cy, px, py, color=GREY, width=1.2, dash='3 3')
        tx, ty = -math.sin(ar), -math.cos(ar)        # anticlockwise tangent on screen
        L = 3.2 * F
        ex, ey = px - tx * L, py - ty * L
        s.line(ex, ey, px, py, color=col, width=2.8)
        s.add(f'<polygon points="{px:.1f},{py:.1f} {px - 10 * tx + 5 * ty:.1f},{py - 10 * ty - 5 * tx:.1f} '
              f'{px - 10 * tx - 5 * ty:.1f},{py - 10 * ty + 5 * tx:.1f}" fill="{col}"/>')
        s.circle(px, py, 4.5, col)
        lx, ly = cx + (r * sc + 62) * math.cos(ar), cy - (r * sc + 62) * math.sin(ar)
        s.text(lx, ly, f'{F} N', size=12.5, color=col, weight='bold')
        s.text(lx, ly + 15, f'r = {r * 100:g} cm, {a}°', size=11, color=col)
    s.text(230, 368, 'each force at right angles to its radius: τ = r × F', size=12.5, weight='bold')
    s.save('robot-grasp-three-fingers.svg', OUT)


def field_figure():
    s = Svg(470, 470, 'Potential-field path planning from (1, 2) to (5, 6) around a circular obstacle '
                      'of radius 1 m at (3, 4). The straight line passes through the obstacle centre; '
                      'gradient descent started exactly on that line stalls in front of the obstacle, '
                      'while a start just off the line slides round it and reaches the target')
    P = frame(s, 55, 415, 62, (0, 6.5), (0, 6.5), grid=1.0)
    ox, oy = P(3, 4)
    s.add(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{1.5 * 62:.1f}" fill="{ORANGE}" fill-opacity="0.08" '
          f'stroke="{ORANGE}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    s.add(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="{62:.1f}" fill="{GREY}" fill-opacity="0.35" '
          f'stroke="{INK}" stroke-width="1.5"/>')
    a, b = P(1, 2), P(5, 6)
    s.line(a[0], a[1], b[0], b[1], color=GREY, width=1.2, dash='3 4')
    stall = descend((1.0, 2.0))
    good = descend((1.0, 1.85))
    polyline(s, [P(*p) for p in stall], RED, 2.4)
    polyline(s, [P(*p) for p in good], BLUE, 2.4)
    sx, sy = P(*stall[-1])
    s.add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="{RED}"/>')
    target(s, P, 5, 6, 'target (5, 6)', color=GREEN)
    s.circle(*P(1, 2), 5, INK)
    s.text(P(1, 2)[0] + 10, P(1, 2)[1] + 16, 'start (1, 2)', size=12, anchor='start', weight='bold')
    s.text(ox, oy + 5, 'obstacle', size=12, weight='bold')
    s.text(70, 30, 'red: starts on the line, stalls (local minimum)', size=12, color=RED,
           weight='bold', anchor='start')
    s.text(70, 48, 'blue: starts 0.15 m off the line, goes round', size=12, color=BLUE,
           weight='bold', anchor='start')
    s.text(70, 66, 'dashed ring: 1.5 m from the centre, where repulsion starts', size=12, color=ORANGE,
           weight='bold', anchor='start')
    s.save('robot-potential-field.svg', OUT)
    return stall, good


def main():
    q5 = ik_checks()
    print('check IK worked numbers: ok', {m: its for m, (_, its, _) in q5['q5runs'].items()},
          {m: its for m, (_, its, _) in q5['t7runs'].items()}, 'NR t1', [round(v, 3) for v in q5['t1']],
          't7', round(q5['t7'][0], 4), [round(v, 3) for v in q5['t7'][1]])
    sg = singularity_checks()
    print('check singularities: ok, w =', round(sg['w'], 4))
    par = parallel_checks()
    print('check parallel manipulator: ok', [round(v, 3) for v in par['q4']['qd']],
          't3', [round(v, 3) for v in par['t3']['qd']], 'dist', [round(d, 3) for d in par['t1'][1]])
    dyn = lagrangian_checks()
    print('check one-link linearisation: ok', dyn)
    gr = grasp_checks()
    print('check grasping: ok', {k: v for k, v in gr.items() if k != 't1'})
    fd = field_checks()
    print('check potential field: ok', {k: round(v, 4) for k, v in fd.items()})
    serial_vs_parallel()
    two_link_ik(q5['ik2'])
    jt_iterations(q5)
    convergence(q5['q5runs'], 'robot-convergence-3dof.svg',
                'Position error against iteration for the 3-link exam problem: damped least squares '
                'and the pseudoinverse converge in a handful of iterations, while the Jacobian '
                'transpose with alpha = 0.05 creeps down slowly',
                {'JT': ORANGE, 'JPI': PURPLE, 'DLS': GREEN})
    convergence(q5['t7runs'], 'robot-convergence-2dof.svg',
                'Position error against iteration for the 2-link tutorial problem: Newton-Raphson '
                'converges fastest once close, damped least squares is close behind, and the '
                'Jacobian transpose is slowest',
                {'NR': BLUE, 'DLS': GREEN, 'JT': ORANGE})
    manipulability_plot()
    singular_poses()
    parallel_figure(par['q4'])
    pendulum_plot()
    grasp_figure()
    stall, good = field_figure()
    gx, gy = good[-1]
    assert math.hypot(gx - 5, gy - 6) < 0.05, good[-1]
    assert min(math.hypot(x - 3, y - 4) for x, y in good) > 1.0
    assert math.hypot(stall[-1][0] - 5, stall[-1][1] - 6) > 2.0, stall[-1]
    assert close(stall[-1][0], 2.02, 0.01) and close(stall[-1][1], 3.02, 0.01), stall[-1]
    print('check potential-field paths: ok, stall at', [round(v, 3) for v in stall[-1]],
          'min clearance', round(min(math.hypot(x - 3, y - 4) for x, y in good), 3))
    pf = performance_checks()
    print('check performance (T_4): ok', 'pose', [round(v, 4) for v in pf['q1pose']], 'areas', round(pf['area_grid'], 2), round(pf['area_est'], 2), round(pf['naive'], 2),
          'jpi', [round(v, 1) for v in pf['jpi']], 'q3', round(pf['q3']['det'], 4), round(pf['q3']['w'], 4),
          'q4', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in pf['q4'].items() if k != 'J'},
          'q4J', [[round(v, 4) for v in row] for row in pf['q4']['J']], 'q5', {k: round(v, 2) for k, v in pf['q5'].items()})
    workspace_figure(pf['grid'])
    print('mechatronics robotics diagrams: done')


if __name__ == '__main__':
    main()
