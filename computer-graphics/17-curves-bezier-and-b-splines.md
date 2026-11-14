# Curves: Bézier and B-splines

**[Intermediate → Advanced]** — Implicit, explicit and parametric curves; affine and barycentric combinations; where the Bézier weights come from; position, velocity, de Casteljau and splitting; B-splines and the Cox–de Boor recursion; Chaikin corner cutting; and drawing a curve with straight lines to a tolerance.

> Part 1 of the course. [[computer-graphics/08-geometry-and-meshes|Note 08]] gives the big picture (NURBS, subdivision surfaces, CAD versus real-time). **This note is the hand-calculation version that SSG 511 Q1(c) is worth 15 marks on.**

## Before you start

You can add vectors and multiply them by numbers, expand $(a + b)^2$ and $(a + b)^3$, and differentiate a polynomial.

**After this note you will be able to:**
1. Choose between implicit, explicit and parametric forms and say why.
2. Find a cubic Bézier's control points from end positions and velocities, and evaluate $B(t)$ and $B'(t)$.
3. Run de Casteljau by hand and read off the control points of each half.
4. Explain local versus global control, and what the B-spline knot vector does.

## The kid version

Stick a pin in a board at the start and another at the end, and add a couple of "magnet" pins in between. A bendy wire runs from the first pin to the last and is pulled towards the magnets without usually touching them. Move a magnet and the wire bends. **That wire is a Bézier curve, and the pins are its control points.**

There's a neat way to find any point on it: join the pins with straight lines, mark the point a fraction $t$ along each line, join those marks, mark $t$ along *those*, and keep going until one point is left. That point is on the curve. **That's de Casteljau's algorithm.**

**Where the analogy stops working.** With a Bézier curve, moving *any* magnet nudges the whole wire, even far away. B-splines fix that: each control point only influences a nearby stretch.

## Terms used in curves

1. **Control point**: This is one of the points $P_0, \dots, P_n$ that shape the curve.
2. **Control polygon**: This is the polyline joining the control points in order.
3. **Degree**: This is the highest power of $t$ in the curve's polynomial. For a Bézier curve it is the number of control points minus 1.
4. **Affine combination**: This is a weighted sum $\alpha_1P_1 + \alpha_2P_2 + \dots$ whose weights add up to 1. It always gives a point, whatever coordinate system you use.
5. **Barycentric combination**: This is an affine combination of a triangle's three corners. The weights are the point's barycentric coordinates.
6. **Bernstein basis functions**: These are the weights $B_i^n(t) = \binom{n}{i}t^i(1-t)^{n-i}$ that a Bézier curve gives its control points.
7. **Convex hull**: This is the smallest convex shape containing all the control points — the shape a rubber band makes when stretched around them.
8. **Knot vector**: This is the list of non-decreasing numbers $t_0 \le t_1 \le \dots$ that marks where a B-spline's polynomial pieces join.
9. **Order**: This is a B-spline's degree plus 1, written $k$.
10. **Local control**: This is the property that moving one control point only changes the nearby part of the curve.

## 1. Three ways to represent a curve

| Type | Form | Circle of radius $r$ | Strength | Weakness |
|---|---|---|---|---|
| **Implicit** | $f(x,y) = 0$ | $x^2 + y^2 - r^2 = 0$ | Easy to test on/inside/outside — check the sign of $f$ | Hard to generate points in order |
| **Explicit** | $y = f(x)$ | $y = \sqrt{r^2 - x^2}$ | Simple | Single-valued: one $y$ per $x$, so no full circle or vertical line |
| **Parametric** | $P(t) = (x(t), y(t))$ | $(r\cos t, r\sin t)$, $t \in [0, 2\pi]$ | General: closed and multi-valued curves; tangents from the derivative; $t$ can be time | Needs a parameter; harder inside/outside test |

In a parametric curve, $x(t)$ and $y(t)$ give the coordinates while $t$ varies over an interval, usually $[0, 1]$. **Adding $z(t)$ gives a 3D curve.** Bézier curves and B-splines are parametric.

## 2. Vectors and affine combinations

A **vector** has magnitude and direction. It can stand for a direction (a velocity) or a point in space; in 2D it has $x$, $y$ components, in 3D $x$, $y$, $z$. It can be scaled and added to or subtracted from another.

**Two points.** Any point on the segment from $P_1$ to $P_2$ is "start at $P_1$ and go a fraction $t$ of the way to $P_2$":

$$P = P_1 + t(P_2 - P_1) = (1-t)P_1 + tP_2,\qquad 0 \le t \le 1$$

The weights $(1 - t)$ and $t$ sum to 1. **A sum $\alpha_1P_1 + \alpha_2P_2 + \dots$ with $\alpha_1 + \alpha_2 + \dots = 1$ is an affine combination.** (The *weights* are $\alpha$; $t$ is the parameter. Write "$\alpha_1 + \alpha_2 = 1$", not "$t_1 + t_2 = 1$".)

**Three points (triangle $P_1P_2P_3$).** Start at $P_1$ and move along the edges $P_2 - P_1$ and $P_3 - P_1$:

$$P = P_1 + \alpha_2(P_2 - P_1) + \alpha_3(P_3 - P_1) = (1 - \alpha_2 - \alpha_3)P_1 + \alpha_2P_2 + \alpha_3P_3$$

Call $P_1$'s weight $\alpha_1 = 1 - \alpha_2 - \alpha_3$. Then $\alpha_1 + \alpha_2 + \alpha_3 = 1$ always. **This is a barycentric combination** — the same coordinates the rasteriser interpolates with in [[computer-graphics/03-rasterisation|note 03]].

## 3. Where the Bézier weights come from

**For any $t$, $(1 - t) + t = 1$.** Square both sides and expand:

$$[(1-t) + t]^2 = (1-t)^2 + 2t(1-t) + t^2 = 1$$

**Use those three terms as weights** — they are never negative on $[0,1]$ and they sum to 1, so the result is an affine combination. That *is* the quadratic Bézier curve:

$$P(t) = (1-t)^2P_0 + 2t(1-t)P_1 + t^2P_2$$

**For $n + 1$ control points, expand $[(1 - t) + t]^n = 1$.** Each term $\binom{n}{i}(1-t)^{n-i}t^i$ is one weight; Pascal's triangle gives the coefficients.

| Degree | Coefficients | Curve |
|---|---|---|
| 1 | 1, 1 | $(1-t)P_0 + tP_1$ |
| 2 | 1, 2, 1 | $(1-t)^2P_0 + 2t(1-t)P_1 + t^2P_2$ |
| 3 | 1, 3, 3, 1 | $(1-t)^3P_0 + 3t(1-t)^2P_1 + 3t^2(1-t)P_2 + t^3P_3$ |

## 4. Bézier curves

**A Bézier curve is the Bernstein-weighted sum of its control points:**

$$P(t) = \sum_{i=0}^{n} P_i\,B_i^n(t),\qquad B_i^n(t) = \binom{n}{i}t^i(1-t)^{n-i} = \frac{n!}{i!\,(n-i)!}\,t^i(1-t)^{n-i},\qquad 0 \le t \le 1$$

(Use one index throughout — summing over $k$ while the terms use $i$ is a common slip.)

- $n$ is the degree, $i$ the index, $t$ the variable, $P_i$ control point $i$.
- **Degree = number of control points − 1.** Two points give a line, three a quadratic, four a cubic.
- **It passes through the first and last control points** (not usually the others), and **lies inside the convex hull** of its control points.
- **Limits:** the degree grows with the number of control points, so long curves get expensive and hard to control; **and moving any one control point changes the whole curve (global control).**

### The cubic in detail

**Position:**

$$B(t) = (1-t)^3P_0 + 3(1-t)^2t\,P_1 + 3(1-t)t^2\,P_2 + t^3P_3$$

**Do every calculation separately on each coordinate** ($x$, $y$, $z$).

**Matrix form.** Expanding $(1-t)^3 = 1 - 3t + 3t^2 - t^3$, $3t(1-t)^2 = 3t - 6t^2 + 3t^3$, $3t^2(1-t) = 3t^2 - 3t^3$ and $t^3$:

$$B(t) = \begin{pmatrix} 1 & t & t^2 & t^3 \end{pmatrix}\begin{pmatrix} 1 & 0 & 0 & 0 \\ -3 & 3 & 0 & 0 \\ 3 & -6 & 3 & 0 \\ -1 & 3 & -3 & 1 \end{pmatrix}\begin{pmatrix} P_0 \\ P_1 \\ P_2 \\ P_3 \end{pmatrix}$$

(A cubic has four weights, so the column must hold four points.)

**Velocity.** If $t$ is time, the derivative is the velocity:

$$B'(t) = 3\left[(1-t)^2(P_1 - P_0) + 2(1-t)t\,(P_2 - P_1) + t^2(P_3 - P_2)\right]$$

**In general, the derivative of a degree-$n$ Bézier is a degree-$(n-1)$ Bézier whose control points are $n$ times the differences of neighbouring control points:**

$$\frac{d}{dt}B_i^n(t) = n\left(B_{i-1}^{n-1}(t) - B_i^{n-1}(t)\right)\quad\Rightarrow\quad B'(t) = \sum_{i=0}^{n-1} B_i^{n-1}(t)\;n\,(P_{i+1} - P_i)$$

so $Q_0 = n(P_1 - P_0),\; Q_1 = n(P_2 - P_1),\; \dots,\; Q_{n-1} = n(P_n - P_{n-1})$.

**End conditions.** Put $t = 0$ and $t = 1$ into the two formulas:

$$B(0) = P_0,\quad B(1) = P_3,\quad B'(0) = 3(P_1 - P_0),\quad B'(1) = 3(P_3 - P_2)$$

**So given start/end positions and velocities $v_0$, $v_1$, the control points follow directly:**

$$P_1 = P_0 + \frac{v_0}{3},\qquad P_2 = P_3 - \frac{v_1}{3}$$

**Position at $t = \tfrac12$:** every weight is $\tfrac18$ times $1, 3, 3, 1$:

$$B\!\left(\tfrac12\right) = \frac{P_0 + 3P_1 + 3P_2 + P_3}{8}$$

### de Casteljau and splitting

**To find $B(t)$, repeatedly take points a fraction $t$ of the way along each segment:**

$$P_i^{\,r} = (1-t)P_i^{\,r-1} + tP_{i+1}^{\,r-1},\qquad P_i^{\,0} = P_i,\qquad B(t) = P_0^{\,n}$$

It forms a triangle of points; the one at the bottom is $B(t)$. **It is numerically stable and needs only interpolation** — no powers of $t$.

**Splitting.** The part of the curve for $t \in [0, s]$ is itself a cubic Bézier. **Its control points are the left edge of the de Casteljau triangle at $t = s$**: $P_0^0, P_0^1, P_0^2, P_0^3$. The second part uses the right edge, read from the bottom up.

**For $s = \tfrac12$ — the "first half" $B_1(t) = B(t/2)$:**

$$Q_0 = P_0,\quad Q_1 = \frac{P_0 + P_1}{2},\quad Q_2 = \frac{P_0 + 2P_1 + P_2}{4},\quad Q_3 = \frac{P_0 + 3P_1 + 3P_2 + P_3}{8}$$

and the second half has control points $Q_3$, $\frac{P_1 + 2P_2 + P_3}{4}$, $\frac{P_2 + P_3}{2}$, $P_3$. **It is still a cubic because replacing $t$ by $t/2$ in a degree-3 polynomial gives another degree-3 polynomial.**

### Properties

1. **Convexity of the basis:** the weights are never negative and sum to 1.
2. **Convex-hull property:** the curve lies inside the convex hull of its control points. (This is what makes cheap curve clipping possible → [[computer-graphics/15-clipping|note 15]].)
3. **Affine invariance:** transforming the curve equals transforming its control points and redrawing — **which is why you move a Bézier curve by moving four points.**
4. **Linear precision:** control points on a line give that line.
5. **Variation diminishing:** no straight line crosses the curve more often than it crosses the control polygon.
6. **End tangents:** the curve leaves $P_0$ towards $P_1$ and arrives at $P_3$ from $P_2$.

## 5. Worked examples

### (a) Control points from end conditions

Position $(1,2)$ at $t = 0$, $(7,3)$ at $t = 1$; velocity $(3,6)$ at $t = 0$, $(-6,3)$ at $t = 1$.

$$P_1 = P_0 + \frac{v_0}{3} = (1,2) + (1,2) = (2,4),\qquad P_2 = P_3 - \frac{v_1}{3} = (7,3) - (-2,1) = (9,2)$$

### (b) de Casteljau at $t = \tfrac12$ for $P_0(1,2)$, $P_1(3,8)$, $P_2(8,9)$, $P_3(7,3)$

| Level | Points |
|---|---|
| 0 | (1,2), (3,8), (8,9), (7,3) |
| 1 | (2,5), (5.5,8.5), (7.5,6) |
| 2 | (3.75,6.75), (6.5,7.25) |
| 3 | **(5.125, 7)** |

**$B(\tfrac12) = (5.125, 7)$.** First half's control points (first point of each level): $(1,2), (2,5), (3.75,6.75), (5.125,7)$. Second half (last point of each level, bottom up): $(5.125,7), (6.5,7.25), (7.5,6), (7,3)$. End tangents: $B'(0) = 3(P_1 - P_0) = (6,18)$, $B'(1) = 3(P_3 - P_2) = (-3,-18)$.

Check with the formula: $\frac{(1,2) + 3(3,8) + 3(8,9) + (7,3)}{8} = \frac{(41, 56)}{8} = (5.125, 7)$. ✓

### (c) A curve through two points with given slopes

**A slope gives a direction, not a speed.** So $P_1$ must lie on the line through $P_0$ with the first slope, and $P_2$ on the line through $P_3$ with the second slope — **but how far along is your choice.** Write $P_1 = P_0 + a(1, m_0)$ and $P_2 = P_3 - b(1, m_1)$, pick sensible positive $a$, $b$ (say a fraction of the distance between the points), **state the choice**, and substitute into the cubic. A different $a$, $b$ gives a different curve through the same points with the same slopes.

### Runnable check

```python
# bezier.py — run: python3 bezier.py
def lerp(a, b, t):
    return tuple((1 - t) * x + t * y for x, y in zip(a, b))

def de_casteljau(points, t):
    """Return all levels of the de Casteljau triangle; the last level is B(t)."""
    levels = [list(points)]
    while len(levels[-1]) > 1:
        prev = levels[-1]
        levels.append([lerp(prev[i], prev[i + 1], t) for i in range(len(prev) - 1)])
    return levels

levels = de_casteljau([(1, 2), (3, 8), (8, 9), (7, 3)], 0.5)
for level in levels:
    print(level)
first_half = [level[0] for level in levels]
second_half = [level[-1] for level in reversed(levels)]
print("first half:", first_half)
print("second half:", second_half)
```

**Expected:** the four levels in the table above, then `first half: [(1, 2), (2.0, 5.0), (3.75, 6.75), (5.125, 7.0)]` and `second half: [(5.125, 7.0), (6.5, 7.25), (7.5, 6.0), (7, 3)]`.

## 6. B-spline curves

**A B-spline is built from several polynomial pieces joined smoothly.** It is more flexible than a Bézier curve because **the degree does not have to grow with the number of control points.** It is a weighted sum of the control points with B-spline basis functions $N_{i,k}(t)$:

$$C(t) = \sum_{i=0}^{n} P_i\,N_{i,k}(t),\qquad t_{k-1} \le t \le t_{n+1},\qquad n \ge k - 1$$

- There are $n + 1$ control points. **$k$ is the order, and the degree is $k - 1$.**
- **The knot vector** $t_0 \le t_1 \le \dots \le t_{n+k}$ marks where the pieces join.
- **The basis functions come from the Cox–de Boor recursion.** In words: order-1 functions are "1 on their own knot interval, 0 elsewhere", and each higher order blends two neighbouring lower-order functions with linear ramps:

$$N_{i,1}(t) = \begin{cases} 1 & t_i \le t < t_{i+1} \\ 0 & \text{otherwise}\end{cases}$$

$$N_{i,k}(t) = \frac{t - t_i}{t_{i+k-1} - t_i}\,N_{i,k-1}(t) + \frac{t_{i+k} - t}{t_{i+k} - t_{i+1}}\,N_{i+1,k-1}(t)$$

(A term with a zero denominator is taken as 0.)

- **The maximum order is the number of control points** ("the number of vertices defining the B-spline polygon"). **With that order and suitable knots, the B-spline is a Bézier curve.**
- **Local control:** $N_{i,k}$ is non-zero only on $[t_i, t_{i+k})$, so moving $P_i$ changes only that stretch.
- The basis functions are never negative and sum to 1, so **the curve stays inside the convex hull** of its control points.
- **With distinct knots the curve has continuity $C^{k-2}$.** A cubic B-spline ($k = 4$) is smooth up to the second derivative — why it is the default in modelling tools.

| | Bézier | B-spline |
|---|---|---|
| Degree | Number of control points − 1 | Chosen separately (order $k$) |
| Control | **Global** — one point moves the whole curve | **Local** — one point moves part of it |
| Extra ingredient | None | A knot vector |
| Relationship | | A Bézier is a B-spline with order = number of control points |

## 7. Chaikin's corner-cutting algorithm

> Class notes only have the heading "curve drawing algorithm: George Chaikin's algorithm"; this is the standard method — **check it against the lecturer's version.**

**Start with a polygon $P_0, \dots, P_n$. For each edge $P_iP_{i+1}$, make two new points a quarter and three-quarters of the way along:**

$$Q_i = \tfrac34P_i + \tfrac14P_{i+1},\qquad R_i = \tfrac14P_i + \tfrac34P_{i+1}$$

Replace the polygon with $Q_0, R_0, Q_1, R_1, \dots$ and repeat. **Each round cuts the corners off, and the polygon converges to a smooth quadratic B-spline.**

**Worked — the closed square $(0,0), (4,0), (4,4), (0,4)$:** after one round the 4 points become 8: $(1,0), (3,0), (4,1), (4,3), (3,4), (1,4), (0,3), (0,1)$. After the next round there are 16.

## 8. Drawing a curve with straight lines

### Distance from a point to a segment

**Assumptions:** 2D Euclidean space; segment from $A$ to $B$; point $P$; $A \ne B$ (if $A = B$, the distance is $|P - A|$).

1. Let $\vec{AB} = B - A$ and $\vec{AP} = P - A$.
2. **Project $P$ onto the line through $A$ and $B$:** $t = \frac{\vec{AP}\cdot\vec{AB}}{\vec{AB}\cdot\vec{AB}}$. $t = 0$ is $A$, $t = 1$ is $B$.
3. **A segment stops at its ends, so clamp $t$ to $[0, 1]$.**
4. The closest point is $C = A + t\,\vec{AB}$; the distance is $|P - C|$.

$$t = \frac{(P - A)\cdot(B - A)}{(B - A)\cdot(B - A)},\qquad C = A + \operatorname{clamp}(t, 0, 1)\,(B - A),\qquad d = \lVert P - C\rVert$$

Three cases: nearest to $A$ ($t \le 0$), nearest to $B$ ($t \ge 1$), or the perpendicular foot in between.

**Worked — segment $A(1,1)$ to $B(9,5)$**, $\vec{AB} = (8,4)$, $|\vec{AB}|^2 = 80$:

| P | t | Clamped | Closest point | Distance |
|---|---|---|---|---|
| (3,7) | 0.5 | 0.5 | (5,3) | $\sqrt{20} = 4.472$ |
| (12,2) | 1.15 | 1 | B (9,5) | $\sqrt{18} = 4.243$ |
| (0,0) | −0.15 | 0 | A (1,1) | $\sqrt2 = 1.414$ |

**Rows 2 and 3 are why the clamp matters:** without it you measure to the infinite line, which is wrong for a segment. (Also: $A = (0,0)$, $B = (4,0)$ gives 1 for $(1,1)$, 5 for $(-3,4)$, and 5 for $(7,4)$.)

### Flattening a quadratic Bézier to tolerance $\sigma$

**Split the curve until each piece is nearly straight, then draw each piece as a line.** The quadratic's furthest point from its chord $P_1P_3$ is at $t = \tfrac12$, where the tangent is parallel to the chord. That point is $M = (P_1 + 2P_2 + P_3)/4$.

```
draw_bezier(P1, P2, P3, sigma):
    M = (P1 + 2*P2 + P3) / 4
    if distance(M, segment P1P3) <= sigma:     # the point-to-segment routine above
        draw_line(P1, P3)                      # flat enough
    else:                                      # de Casteljau split at t = 1/2
        A = (P1 + P2) / 2
        B = (P2 + P3) / 2
        draw_bezier(P1, A, M, sigma)           # first half
        draw_bezier(M, B, P3, sigma)           # second half
```

**The flatness (maximum distance from the chord) is**

$$\delta = \frac{|P_1 - 2P_2 + P_3|}{4}$$

and **each split in half divides it by 4**, so the recursion always stops. (Equivalently, it is half the distance of $P_2$ from the chord's line — another common flatness test.)

**Worked:** $P_1(0,0)$, $P_2(4,8)$, $P_3(8,0)$. $P_1 - 2P_2 + P_3 = (0,-16)$, so $\delta = 16/4 = 4$ (indeed $P(\tfrac12) = (4,4)$ and the chord midpoint is $(4,0)$). For $\sigma = 0.25$: $4 \to 1 \to 0.25$, **two levels of splitting, giving 4 straight segments.**

## Common pitfalls

1. **Mixing $P_0$–$P_3$ with $P_1$–$P_4$ labels** mid-question. Pick one.
2. **Forgetting the factor 3** in $B'(0) = 3(P_1 - P_0)$, so $P_1 = P_0 + v_0$ instead of $P_0 + v_0/3$.
3. **Reading the second half from the wrong edge** of the de Casteljau triangle.
4. **Not clamping $t$** in the point-to-segment distance.
5. **Treating a slope as a velocity** — a slope fixes direction only.
6. **Reversed binomial index** — the standard form is $\binom{n}{r}(1-t)^{n-r}t^r$ so the highest power of $(1 - t)$ sits on the first point.

## Check your understanding

1. A cubic Bézier has $P_0 = P_1$. What is $B'(0)$, and what does that mean physically?
2. Why does moving one control point of a cubic B-spline with many points leave most of the curve unchanged?
3. How many line segments does flattening need for a quadratic with $\delta = 8$ at $\sigma = 0.5$?

<details><summary>Answers (after your attempt)</summary>

1. Zero: the particle starts at rest (the curve still leaves towards $P_2$).
2. Each basis function is non-zero only over $k$ knot intervals, so each control point's weight is zero elsewhere.
3. $8 \to 2 \to 0.5$: two levels, 4 segments.

</details>

## Practice — independent tasks

From SSG 511 — full wording in the [[computer-graphics/19-ssg-511-question-bank|question bank]]:

1. **Exam Q1(c)** — particle from $(0,0,0)$ to $(4,0,2)$, velocities $(6,0,0)$ and $(0,0,3)$: equations, $P_1$, $P_2$, $B(\tfrac12)$, and the first half's control points.
2. **B-9** — $P_0(0,0)$, $P_1(2,0)$, $P_2(0,2)$, $P_3(4,4)$: sketch, de Casteljau $B(\tfrac12)$, sketch the curve with end slopes.
3. **B-10** — the 2D particle with velocities $(6,0)$ and $(-12,0)$, including the second half's control points.
4. **Supplementary 4–6** — point-to-segment distance, flattening, and the curve through $(0,5)$ slope 2 and $(6,1)$ slope 3.

**Done when** each $B(\tfrac12)$ agrees between the formula and de Casteljau, and the `bezier.py` script reproduces your halves.

## Before moving on

**Next:** [[computer-graphics/18-visible-surface-detection|Visible Surface Detection]].

## Related
- [[computer-graphics/08-geometry-and-meshes|Geometry and Meshes]] — NURBS, subdivision surfaces, the CAD divide
- [[computer-graphics/09-animation-and-simulation|Animation]] — curves as motion paths
- [[mathematics/07-applied-and-computational/01-numerical-methods/06-interpolation-and-approximation|Interpolation and splines]]
- [[computer-graphics/index|Computer graphics map]]
