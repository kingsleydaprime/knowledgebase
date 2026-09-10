# Coordinate Geometry

**[Beginner]** — putting numbers on the plane, so that every geometric question becomes an algebraic one.

## Before you start

- You can solve and rearrange linear equations — [[01-linear-equations|linear equations]].
- You know Pythagoras' theorem, and the congruence results — [[02-triangles-and-polygons|triangles and polygons]].
- Helpful: the circle theorems, which section 6 re-proves by algebra — [[01-circle-theorems|circle theorems]].

**What you will be able to do after this lesson:**

1. Compute distance, midpoint and gradient between two points, and say which of Pythagoras' assumptions each one inherits.
2. Move fluently between the forms $y = mx + c$, point-gradient, two-point and $ax + by + c = 0$, and say when each is the right one.
3. Prove the perpendicular-gradient rule $m_1 m_2 = -1$ instead of memorising it, and state the case it excludes.
4. Prove a geometric theorem **by coordinates** — reaching the same result as a synthetic proof, by different means.

**Study route:** read 1–6, attempt the prediction in section 5, then run the lab. Block 5 of the lab is the point of the lesson.

---

## 1. Why this exists

The previous four lessons proved things by argument: draw an auxiliary line, spot a congruence, chain the rules. It works, and it is beautiful, but it has an awkward property — **you have to see the trick**. The angle-sum proof needs someone to think of drawing a parallel through the apex. Nothing in the problem statement suggests it.

Descartes' idea removes the need to be clever. Put an origin and two axes on the plane, and every point becomes a pair of numbers. Then:

- A line becomes an equation.
- "These two lines are perpendicular" becomes an arithmetic condition on two numbers.
- "This point lies on that circle" becomes substituting and checking.

Geometry becomes algebra, and algebra can be done by following rules — or by a machine. Every graphics program, every mapping application, every CAD package works this way. Nothing draws auxiliary lines.

The trade is real, though, and worth naming up front: coordinate proofs are *mechanical* but often *longer*, and they can obscure why a result is true. Both methods are worth having.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Origin** | The point $(0, 0)$ where the axes cross | Its position is a choice, not a fact about the figure |
| **Coordinates** | The pair $(x, y)$ locating a point | $x$ across, $y$ up — always that order |
| **Gradient** (slope) | How much $y$ changes per unit of $x$ | "Rise over run" |
| **Intercept** | Where a line crosses an axis | $c$ in $y = mx + c$ is the $y$-intercept |
| **Collinear** | Lying on one straight line | Three points are collinear when two gradients agree |
| **Locus** | The set of points satisfying a condition | A circle is the locus of points at distance $r$ from a centre |

## 3. Distance, midpoint, gradient

Take two points $A(x_1, y_1)$ and $B(x_2, y_2)$.

**Distance.** Drop a horizontal and a vertical from the two points to form a right triangle with legs $\lvert x_2 - x_1 \rvert$ and $\lvert y_2 - y_1 \rvert$. Pythagoras gives:

$$
AB = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
$$

This is Pythagoras' theorem wearing coordinates, and it inherits everything Pythagoras assumes — including that the axes are **perpendicular** and the scales on them **equal**. On a plot with a stretched $y$-axis this formula does not measure what the picture shows.

**Midpoint.** The average of the coordinates:

$$
M = \left( \frac{x_1 + x_2}{2},\ \frac{y_1 + y_2}{2} \right)
$$

**Gradient.**

$$
m = \frac{y_2 - y_1}{x_2 - x_1} = \frac{\text{rise}}{\text{run}}
$$

with the standing exception that a **vertical** line has $x_2 = x_1$, so the gradient is undefined — not infinite, undefined. Every rule below that mentions gradients has vertical lines as an exception, and forgetting it is the most common source of a wrong answer in this topic.

### Parallel and perpendicular

**Parallel lines have equal gradients.** Same rise per run, so the same $m$.

**Perpendicular gradients multiply to $-1$.** Here is the proof, which is shorter than the rule is long-winded.

A line of gradient $m_1$ has direction vector $(1, m_1)$ — go one across, $m_1$ up. Similarly the other has direction $(1, m_2)$. Two directions are perpendicular exactly when their dot product is zero:

$$
(1)(1) + (m_1)(m_2) = 0 \quad\Longrightarrow\quad 1 + m_1 m_2 = 0 \quad\Longrightarrow\quad m_1 m_2 = -1
$$

$\blacksquare$

The proof also shows the exception cleanly. The direction vector $(1, m)$ can never be vertical, so a vertical and a horizontal line — which *are* perpendicular — cannot be tested by this rule at all. Their gradients are undefined and $0$, and the product is meaningless.

## 4. The equation of a straight line

Four forms, each convenient for different given information:

| Form | Equation | Use it when |
| :--- | :--- | :--- |
| **Gradient-intercept** | $y = mx + c$ | You know the gradient and where it crosses the $y$-axis |
| **Point-gradient** | $y - y_1 = m(x - x_1)$ | You know one point and the gradient |
| **Two-point** | $\dfrac{y - y_1}{y_2 - y_1} = \dfrac{x - x_1}{x_2 - x_1}$ | You know two points |
| **General** | $ax + by + c = 0$ | You need to handle vertical lines, or want a formula |

The general form is the one to prefer in code. It is the only one of the four that can represent a **vertical** line ($b = 0$), and the distance formula below needs it.

**Distance from a point to a line.** For the line $ax + by + c = 0$ and the point $(x_0, y_0)$:

$$
d = \frac{\lvert a x_0 + b y_0 + c \rvert}{\sqrt{a^2 + b^2}}
$$

The numerator measures how far the point is from satisfying the equation; dividing by $\sqrt{a^2+b^2}$ converts that into an actual distance. This is the perpendicular distance — the shortest one — which is exactly what section 3.1 of [[02-tangents|tangents]] needed.

## 5. The circle

A circle is the locus of points at fixed distance $r$ from a centre $(a, b)$. Writing that with the distance formula and squaring both sides:

$$
(x - a)^2 + (y - b)^2 = r^2
$$

That is the whole definition, turned into an equation with no further work. Expanding gives the general form $x^2 + y^2 + Dx + Ey + F = 0$, and completing the square takes you back.

> [!TIP]
> **Predict before running the lab.** The line $y = 2x + 1$ and the circle $x^2 + y^2 = 5$: how many points do they share? Substitute and look at the discriminant of the resulting quadratic before opening the answers. What would a discriminant of exactly zero mean geometrically?

## 6. Proving a theorem by coordinates

Section 3.1 of [[03-constructions|constructions]] needed this fact: **the diagonals of a rhombus bisect each other at right angles.** It was proved there by congruent triangles. Here it is by algebra.

Place the rhombus conveniently — and choosing the placement *is* the skill in coordinate proofs. Put one vertex at the origin and one side along the $x$-axis:

$$
A(0,0), \quad B(p, q), \quad C(p + s, q), \quad D(s, 0)
$$

For this to be a rhombus all four sides must be equal. $AD = s$ and $AB = \sqrt{p^2 + q^2}$, so the condition is:

$$
p^2 + q^2 = s^2
$$

Now the diagonals are $AC$ and $BD$. Their midpoints:

$$
\text{mid}(AC) = \left(\tfrac{p+s}{2}, \tfrac{q}{2}\right), \qquad \text{mid}(BD) = \left(\tfrac{p+s}{2}, \tfrac{q}{2}\right)
$$

Identical — so the diagonals **bisect each other**, with no conditions at all. That half is true for any parallelogram.

Their gradients:

$$
m_{AC} = \frac{q}{p+s}, \qquad m_{BD} = \frac{q - 0}{p - s} = \frac{q}{p-s}
$$

Multiplying:

$$
m_{AC} \cdot m_{BD} = \frac{q^2}{(p+s)(p-s)} = \frac{q^2}{p^2 - s^2}
$$

And the rhombus condition says $s^2 = p^2 + q^2$, so $p^2 - s^2 = -q^2$:

$$
m_{AC} \cdot m_{BD} = \frac{q^2}{-q^2} = -1
$$

Perpendicular. $\blacksquare$

Notice what happened: **the rhombus condition entered exactly once**, at the last step. That tells you precisely which part of the theorem needs all four sides equal — the perpendicularity — and which part does not — the bisection. The synthetic proof does not make that separation nearly as obvious.

## Worked example — runnable

**Runnable example:** save as `coordinate_geometry.py` in any empty directory and run `python3 coordinate_geometry.py`. Standard library only; writes no files.

```python
"""Coordinate geometry, with a coordinate proof at the end.

Block 5 re-proves, numerically, the rhombus fact that the compass-and-
straightedge lesson proved by congruent triangles.
"""
import math
from fractions import Fraction

EPS = 1e-9


def dist(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def midpoint(p, q):
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


def gradient(p, q):
    """Rise over run, or None for a vertical line."""
    if abs(q[0] - p[0]) < EPS:
        return None
    return (q[1] - p[1]) / (q[0] - p[0])


def line_through(p, q):
    """General form (a, b, c) with ax + by + c = 0. Handles vertical lines."""
    a = q[1] - p[1]
    b = p[0] - q[0]
    c = -(a * p[0] + b * p[1])
    return (a, b, c)


def point_line_distance(pt, line):
    a, b, c = line
    return abs(a * pt[0] + b * pt[1] + c) / math.hypot(a, b)


def line_circle_intersections(m, k, r):
    """Where y = mx + k meets x^2 + y^2 = r^2. Returns the discriminant too."""
    A = 1 + m * m
    B = 2 * m * k
    C = k * k - r * r
    disc = B * B - 4 * A * C
    if disc < -EPS:
        return disc, []
    if abs(disc) < EPS:
        x = -B / (2 * A)
        return disc, [(x, m * x + k)]
    s = math.sqrt(disc)
    return disc, [((-B + s) / (2 * A), m * ((-B + s) / (2 * A)) + k),
                  ((-B - s) / (2 * A), m * ((-B - s) / (2 * A)) + k)]


if __name__ == "__main__":
    A, B = (1.0, 2.0), (7.0, 10.0)

    print("Block 1 - distance, midpoint, gradient")
    print(f"  A={A} B={B}")
    print(f"  distance = {dist(A, B):.6f}   midpoint = {midpoint(A, B)}   gradient = {gradient(A, B)}")
    assert abs(dist(A, B) - 10.0) < EPS          # the 6-8-10 triangle
    assert midpoint(A, B) == (4.0, 6.0)

    print()
    print("Block 2 - perpendicular gradients multiply to -1")
    for m1 in (2.0, -0.5, 3.0, 0.25):
        m2 = -1 / m1
        print(f"  m1={m1:6.3f}  m2={m2:8.4f}  product={m1 * m2:.6f}")
        assert abs(m1 * m2 + 1) < EPS
    vertical = gradient((3.0, 1.0), (3.0, 9.0))
    horizontal = gradient((1.0, 4.0), (8.0, 4.0))
    print(f"  vertical line gradient = {vertical}, horizontal = {horizontal}")
    print("  these two ARE perpendicular, but the rule cannot express it")
    assert vertical is None and horizontal == 0.0

    print()
    print("Block 3 - general form and distance from a point to a line")
    line = line_through((0.0, 0.0), (4.0, 3.0))   # 3x - 4y = 0
    print(f"  line through (0,0) and (4,3): {line[0]}x + {line[1]}y + {line[2]} = 0")
    for pt in [(0.0, 5.0), (4.0, 3.0), (8.0, 6.0), (-3.0, 4.0)]:
        print(f"    distance from {str(pt):>12} = {point_line_distance(pt, line):.6f}")
    assert abs(point_line_distance((4.0, 3.0), line)) < EPS      # on the line
    assert abs(point_line_distance((0.0, 5.0), line) - 4.0) < EPS

    print()
    print("Block 4 - line meets circle: the discriminant decides")
    for m, k, label in [(2.0, 1.0, "y = 2x + 1"),
                        (2.0, 5.0, "y = 2x + 5"),
                        (2.0, 6.0, "y = 2x + 6")]:
        disc, pts = line_circle_intersections(m, k, math.sqrt(5))
        kind = {0: "misses", 1: "tangent", 2: "secant"}[len(pts)]
        print(f"  {label:12} vs x^2+y^2=5 -> discriminant {disc:9.4f}, {len(pts)} point(s), {kind}")
    assert len(line_circle_intersections(2.0, 1.0, math.sqrt(5))[1]) == 2
    assert len(line_circle_intersections(2.0, 5.0, math.sqrt(5))[1]) == 1
    assert len(line_circle_intersections(2.0, 6.0, math.sqrt(5))[1]) == 0

    print()
    print("Block 5 - coordinate proof: diagonals of a rhombus")
    # Exact arithmetic, so 'perpendicular' means exactly -1, not nearly.
    for p, q in [(Fraction(3), Fraction(4)),
                 (Fraction(5), Fraction(12)),
                 (Fraction(8), Fraction(15))]:
        s = Fraction(int(math.isqrt(int(p * p + q * q))))   # side length, a whole number
        assert p * p + q * q == s * s, "need a Pythagorean pair for exact arithmetic"
        Av, Bv, Cv, Dv = (0, 0), (p, q), (p + s, q), (s, 0)
        sides = {abs(s), abs(s)}                            # AD and BC
        m_ac = Fraction(q, p + s)
        m_bd = Fraction(q, p - s)
        mid_ac = (Fraction(p + s, 2), Fraction(q, 2))
        mid_bd = (Fraction(p + s, 2), Fraction(q, 2))
        print(f"  rhombus with p={p}, q={q}, side={s}")
        print(f"    midpoints coincide: {mid_ac == mid_bd}")
        print(f"    gradient product   = {m_ac * m_bd}")
        assert mid_ac == mid_bd
        assert m_ac * m_bd == -1

    print()
    print("coordinate_geometry: passed")
```

Expected output:

```
Block 1 - distance, midpoint, gradient
  A=(1.0, 2.0) B=(7.0, 10.0)
  distance = 10.000000   midpoint = (4.0, 6.0)   gradient = 1.3333333333333333

Block 2 - perpendicular gradients multiply to -1
  m1= 2.000  m2= -0.5000  product=-1.000000
  m1=-0.500  m2=  2.0000  product=-1.000000
  m1= 3.000  m2= -0.3333  product=-1.000000
  m1= 0.250  m2= -4.0000  product=-1.000000
  vertical line gradient = None, horizontal = 0.0
  these two ARE perpendicular, but the rule cannot express it

Block 3 - general form and distance from a point to a line
  line through (0,0) and (4,3): 3.0x + -4.0y + -0.0 = 0
    distance from   (0.0, 5.0) = 4.000000
    distance from   (4.0, 3.0) = 0.000000
    distance from   (8.0, 6.0) = 0.000000
    distance from  (-3.0, 4.0) = 5.000000

Block 4 - line meets circle: the discriminant decides
  y = 2x + 1   vs x^2+y^2=5 -> discriminant   96.0000, 2 point(s), secant
  y = 2x + 5   vs x^2+y^2=5 -> discriminant    0.0000, 1 point(s), tangent
  y = 2x + 6   vs x^2+y^2=5 -> discriminant  -44.0000, 0 point(s), misses

Block 5 - coordinate proof: diagonals of a rhombus
  rhombus with p=3, q=4, side=5
    midpoints coincide: True
    gradient product   = -1
  rhombus with p=5, q=12, side=13
    midpoints coincide: True
    gradient product   = -1
  rhombus with p=8, q=15, side=17
    midpoints coincide: True
    gradient product   = -1

coordinate_geometry: passed
```

Block 5 uses `Fraction`, not floating point, deliberately. The claim being checked is that the gradient product is **exactly** $-1$, and with floats the best you could report is $-0.9999999999999998$. Exact arithmetic makes it a proof for those cases rather than strong evidence.

## Common pitfalls and traps

- **Forgetting vertical lines.** Gradient undefined, $y = mx + c$ unusable, perpendicular rule inapplicable. Any function taking a gradient needs a decision about this case; the lab returns `None` and forces the caller to handle it.
- **Subtracting in inconsistent order.** $\frac{y_2 - y_1}{x_2 - x_1}$ and $\frac{y_1 - y_2}{x_1 - x_2}$ agree. $\frac{y_2 - y_1}{x_1 - x_2}$ is the negative of both, and it is an easy slip.
- **Using the distance formula on unequal axis scales.** The formula assumes perpendicular axes with equal units. On a chart with a compressed axis, the visual distance and the computed distance are different things.
- **Choosing an awkward placement in a coordinate proof.** Putting a vertex at the origin and a side along an axis eliminates variables and shortens the algebra enormously. A general placement with four arbitrary vertices is valid but usually unmanageable — and this choice is where most coordinate proofs are won or lost.
- **Over-specifying the placement.** Placing the rhombus as $A(0,0), B(3,4), C(8,4), D(5,0)$ proves the theorem for *that* rhombus only. The proof needs symbols with one stated condition, not a worked instance.
- **Comparing floats with `==`.** Everywhere except block 5, the lab compares against a tolerance. Block 5 can use `==` only because `Fraction` is exact.

## Check your understanding

1. Find the distance and midpoint between $(-2, 3)$ and $(4, -5)$.
2. A line passes through $(2, 1)$ with gradient $-3$. Give its equation in general form.
3. Is the triangle with vertices $(0,0)$, $(4,2)$, $(1,5)$ right-angled? Justify with gradients.
4. Find the perpendicular distance from $(7, 2)$ to the line $3x + 4y - 10 = 0$.
5. A circle has equation $x^2 + y^2 - 6x + 4y - 12 = 0$. Find its centre and radius.

<details><summary>Answers — open only after an attempt</summary>

1. Distance $= \sqrt{6^2 + (-8)^2} = \sqrt{100} = 10$. Midpoint $= (1, -1)$.
2. $y - 1 = -3(x - 2)$, so $y = -3x + 7$, so $3x + y - 7 = 0$.
3. Gradients: $(0,0)$ to $(4,2)$ is $\tfrac12$; $(0,0)$ to $(1,5)$ is $5$; $(4,2)$ to $(1,5)$ is $\tfrac{5-2}{1-4} = -1$. Now $\tfrac12 \times 5 = 2.5$, $\tfrac12 \times -1 = -\tfrac12$, $5 \times -1 = -5$. No pair multiplies to $-1$, so it is **not** right-angled.
4. $d = \dfrac{\lvert 3(7) + 4(2) - 10 \rvert}{\sqrt{9 + 16}} = \dfrac{\lvert 21 + 8 - 10 \rvert}{5} = \dfrac{19}{5} = 3.8$.
5. Complete the square: $(x-3)^2 - 9 + (y+2)^2 - 4 - 12 = 0$, so $(x-3)^2 + (y+2)^2 = 25$. Centre $(3, -2)$, radius $5$.

**And the prediction from section 5:** substituting $y = 2x+1$ into $x^2+y^2=5$ gives $5x^2 + 4x - 4 = 0$, discriminant $16 + 80 = 96 > 0$, so **two** intersection points. A discriminant of exactly zero would mean the two points have merged: the line is a **tangent** — the same repeated-root situation seen in the power-of-a-point lab.
</details>

## Practice — independent task

Prove the **midpoint theorem** by coordinates, then verify it: *the segment joining the midpoints of two sides of a triangle is parallel to the third side and half its length.*

1. Choose a placement that minimises variables. Justify your choice in a comment — how many variables did a general placement need, and how many did yours?
2. Prove it symbolically on paper: show the gradients are equal and the length ratio is exactly $\tfrac12$.
3. Implement `midpoint_segment(a, b, c)` returning the two midpoints, and assert both properties numerically for at least five triangles, including one with a vertical side.
4. Use `Fraction` so that "parallel" means gradients are *exactly* equal, and handle the vertical-side case explicitly rather than letting it raise.
5. Then answer: does your proof use the fact that the three points form a triangle at all? What happens if they are collinear?

**Done when:** your symbolic proof and your numerical check agree, the vertical case passes without special-casing the mathematics (only the representation), and you can answer step 5 with a reason rather than a guess.

## Tradeoffs, limits and extensions

**Coordinate proofs versus synthetic proofs.** Coordinate proofs are mechanical: choose axes, write the algebra, grind. They always terminate, which synthetic proofs do not guarantee. But they can hide the reason — section 6's algebra proves the rhombus fact without ever suggesting *why* equal sides should force perpendicular diagonals, whereas the congruent-triangle proof makes it visible. Prefer coordinates when you need certainty or a computer; prefer synthetic when you need insight.

**The origin is a choice.** Nothing in a triangle knows where your origin is. A good coordinate proof exploits that by placing the figure to zero out as many coordinates as possible. A poor one carries six arbitrary variables through pages of algebra to reach the same result.

**Where this goes next.** Adding a third coordinate gives [[01-lines-and-planes|lines and planes in space]], where gradient stops working and direction vectors take over. Adding calculus turns "gradient of a line" into "gradient of a curve at a point", which is the [[06-defining-derivative/01-definition|derivative]].

## Before moving on

You are done with this lesson when you can:

- Derive the distance formula from Pythagoras rather than recall it.
- Prove $m_1 m_2 = -1$ from direction vectors, and state the case it excludes.
- Convert between all four line forms, and say why the general form is the one to use in code.
- Complete a coordinate proof, choosing the placement yourself.

**Recap for later lookup:** $AB = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$; midpoint is the average of coordinates; $m = \frac{\Delta y}{\Delta x}$, undefined for vertical; parallel means equal $m$, perpendicular means $m_1m_2 = -1$; line forms $y = mx+c$, $y - y_1 = m(x-x_1)$, $ax+by+c=0$; distance from point to line $= \frac{|ax_0+by_0+c|}{\sqrt{a^2+b^2}}$; circle $(x-a)^2 + (y-b)^2 = r^2$.

**Next:** [[01-ratios-and-right-triangles|Trigonometric Ratios]] — coordinates give you lengths and gradients; trigonometry connects those to *angles*.

## Related

- [[03-constructions|Constructions]] — the rhombus theorem proved the other way
- [[01-circle-theorems|Circle Theorems]] — the same circles, by argument instead of equation
- [[01-lines-and-planes|Lines and Planes in Space]] — the three-dimensional continuation
- [[04-linear-algebra/02-vectors/01-vectors|Vectors]] — the dot product used in the perpendicularity proof
