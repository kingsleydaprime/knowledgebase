# Constructions

**[Beginner]** — building exact figures with two tools that cannot measure anything, and proving that what you built is what you claimed.

## Before you start

- You know the congruence criteria, especially SSS — [[02-triangles-and-polygons|triangles and polygons]]. Every proof in this lesson is an SSS argument.
- You can chase angles across parallel lines — [[01-angles-and-parallel-lines|angles and parallel lines]].
- Useful but not required: a physical compass and straightedge. The lesson can be done entirely on paper or entirely in code.

**What you will be able to do after this lesson:**

1. Construct a perpendicular bisector, an angle bisector, and angles of $60°$, $90°$, $45°$ and $30°$, using only compass and straightedge.
2. **Prove** each construction correct, rather than trusting that the picture looks right.
3. State the rules of the game precisely — what a straightedge may and may not do.
4. Explain why trisecting a general angle is impossible, and why that is a theorem rather than a confession of failure.

**Study route:** read 1–3, do at least one construction physically before section 4, then run the lab, then attempt the practice task.

---

## 1. Why this exists

A protractor is marked in whole degrees. A ruler is marked in millimetres. Both were manufactured by someone else, and both are only as accurate as that manufacture.

Compass-and-straightedge construction throws both away. The tools cannot measure. A compass copies a distance without ever naming it; a straightedge draws a line without ever reading it. Yet from them you can produce an angle that is *exactly* $60°$ — not $60.0°$ to the precision of some instrument, but exactly, provably, with error zero.

That is the appeal, and it is why this survived from Euclid to the school syllabus. It is also the earliest example of a question that turned out to be about **algebra**: which numbers can these two tools reach? The answer took until 1837, and it is in section 5.

## 2. The rules of the game

A construction starts from a small set of given points and produces new ones. Only three moves are legal:

| Move | What it does | What it may **not** do |
| :--- | :--- | :--- |
| **Straightedge** | Draw the line through two points that already exist | Measure length; draw a line "roughly parallel"; use its edge markings |
| **Compass** | Draw the circle centred at an existing point, passing through another existing point | Be set to a numeric radius |
| **Intersect** | Create a new point where two drawn lines or circles cross | Create a point by eyeballing a position |

Every new point must arise from that third move. "Mark a point near the middle" is not a construction step.

| Term | Plain-English definition |
| :--- | :--- |
| **Locus** | The set of all points satisfying a condition |
| **Arc** | Part of a circle — in practice, as much of the circle as you bother to draw |
| **Bisect** | Cut exactly in half |
| **Perpendicular bisector** | The line cutting a segment in half at right angles |
| **Rhombus** | A quadrilateral with all four sides equal |
| **Constructible** | Reachable from the starting points by legal moves alone |

One idea does most of the work:

> **The perpendicular bisector of $AB$ is the locus of points equidistant from $A$ and $B$.**

Every construction below is an application of that, sometimes twice.

## 3. The constructions, with proofs

### 3.1 Perpendicular bisector of a segment $AB$

1. Open the compass to any radius $r$ greater than half of $AB$.
2. Draw an arc centred at $A$.
3. Draw an arc of the **same** radius centred at $B$.
4. The arcs meet at two points, $P$ and $Q$. Draw the line $PQ$.

```
              P
             / \
            /   \
       A---+-----+---B        PQ crosses AB at its midpoint, at 90 degrees
            \   /
             \ /
              Q
```

**Why it works.** $AP = r$ and $BP = r$ because both arcs had radius $r$ — so $P$ is equidistant from $A$ and $B$. The same argument gives $AQ = BQ$. So $APBQ$ has all four sides equal: it is a **rhombus**, and the diagonals of a rhombus bisect each other at right angles.

If you would rather not quote that property, argue directly: triangles $APQ$ and $BPQ$ have $AP = BP$, $AQ = BQ$ and share $PQ$, so they are congruent by **SSS**. Hence $\angle APQ = \angle BPQ$. Then triangles $APM$ and $BPM$ (where $M$ is the crossing point) are congruent by **SAS**, giving $AM = BM$ and two equal adjacent angles at $M$ — which, being a linear pair, must each be $90°$. $\blacksquare$

Note what the proof does **not** need: the value of $r$. Any radius over half of $AB$ gives the same line. The construction is exact for every legal choice.

### 3.2 Bisecting an angle

Given an angle at vertex $V$:

1. Draw an arc centred at $V$ crossing both arms, at $X$ and $Y$.
2. Draw equal arcs centred at $X$ and at $Y$, meeting at $Z$.
3. Draw $VZ$.

**Why it works.** $VX = VY$ (same arc), $XZ = YZ$ (equal arcs), and $VZ$ is shared. Triangles $VXZ$ and $VYZ$ are congruent by **SSS**, so $\angle XVZ = \angle YVZ$. $\blacksquare$

### 3.3 An angle of exactly $60°$

1. Draw a segment $AB$.
2. Draw the arc centred at $A$ through $B$.
3. Draw the arc centred at $B$ through $A$.
4. They meet at $C$. Draw $AC$ and $BC$.

**Why it works.** $AB = AC$ (first arc) and $AB = BC$ (second arc), so all three sides are equal. The triangle is **equilateral**, and by the isosceles result applied twice all three angles are equal. They sum to $180°$, so each is $60°$. $\blacksquare$

This is the construction that makes the rest possible: bisect it for $30°$, bisect again for $15°$.

### 3.4 $90°$, then $45°$

A right angle is the perpendicular bisector construction of 3.1, applied to any segment. Bisect the result for $45°$, and bisect again for $22.5°$.

So from the two base constructions you get, exactly:

$$
60°,\ 30°,\ 15°,\ 7.5°,\ \dots \qquad 90°,\ 45°,\ 22.5°,\ \dots
$$

and every sum and difference of them — $75° = 60° + 15°$, $105° = 60° + 45°$, and so on.

## 4. Worked example — runnable

The lab performs each construction with coordinates, using only circle and line intersections, then checks the property the construction is *supposed* to guarantee. It is a check on the reasoning, not a substitute for the proofs above.

**Runnable example:** save as `constructions.py` in any empty directory and run `python3 constructions.py`. Standard library only; writes no files.

```python
"""Compass-and-straightedge constructions, verified by coordinates.

Only two primitives are used, matching the two legal tools:
  circle_circle - where two compass arcs meet
  line_line     - where two straightedge lines meet
Every new point comes from one of them. Nothing is measured into existence.
"""
import math

EPS = 1e-9


def dist(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def circle_circle(c1, r1, c2, r2):
    """Intersection points of two circles: 0, 1 or 2 of them."""
    (x1, y1), (x2, y2) = c1, c2
    d = dist(c1, c2)
    if d < EPS or d > r1 + r2 + EPS or d < abs(r1 - r2) - EPS:
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h_sq = r1 * r1 - a * a
    if h_sq < 0:
        h_sq = 0.0                      # tangent circles, flattened by rounding
    h = math.sqrt(h_sq)
    xm = x1 + a * (x2 - x1) / d
    ym = y1 + a * (y2 - y1) / d
    if h < EPS:
        return [(xm, ym)]
    return [(xm + h * (y2 - y1) / d, ym - h * (x2 - x1) / d),
            (xm - h * (y2 - y1) / d, ym + h * (x2 - x1) / d)]


def line_line(p1, p2, p3, p4):
    """Intersection of line p1p2 with line p3p4, or None if parallel."""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < EPS:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def angle_at(v, p, q):
    """Angle p-v-q in degrees."""
    u = (p[0] - v[0], p[1] - v[1])
    w = (q[0] - v[0], q[1] - v[1])
    cos = (u[0] * w[0] + u[1] * w[1]) / (math.hypot(*u) * math.hypot(*w))
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def perpendicular_bisector(a, b):
    """Section 3.1. Returns the two arc-intersection points P and Q."""
    r = dist(a, b)                      # any radius over half of AB
    pts = circle_circle(a, r, b, r)
    assert len(pts) == 2, "arcs must cross twice"
    return pts


def equilateral_apex(a, b):
    """Section 3.3. Returns the apex C of an equilateral triangle on AB."""
    return circle_circle(a, dist(a, b), b, dist(a, b))[0]


def bisect_angle(v, p, q):
    """Section 3.2. Returns a point Z with VZ bisecting angle PVQ."""
    r = min(dist(v, p), dist(v, q)) / 2
    x = (v[0] + r * (p[0] - v[0]) / dist(v, p), v[1] + r * (p[1] - v[1]) / dist(v, p))
    y = (v[0] + r * (q[0] - v[0]) / dist(v, q), v[1] + r * (q[1] - v[1]) / dist(v, q))
    s = dist(x, y)
    candidates = circle_circle(x, s, y, s)
    full = angle_at(v, p, q)
    for z in candidates:
        # When PVQ is exactly 60 degrees, triangle VXY is equilateral and one
        # candidate lands back on V itself. That point names no direction.
        if dist(z, v) < EPS:
            continue
        # Keep the point inside the angle, not the one on the opposite ray.
        if angle_at(v, p, z) <= full + EPS and angle_at(v, q, z) <= full + EPS:
            return z
    raise ValueError("no bisector point found")


if __name__ == "__main__":
    A, B = (0.0, 0.0), (6.0, 0.0)

    print("3.1 perpendicular bisector of AB")
    P, Q = perpendicular_bisector(A, B)
    M = line_line(P, Q, A, B)
    print(f"  P is {dist(P, A):.6f} from A and {dist(P, B):.6f} from B")
    print(f"  PQ meets AB at {M[0]:.6f}, {M[1]:.6f}  (midpoint is 3.0, 0.0)")
    print(f"  angle between PQ and AB = {angle_at(M, P, B):.6f} degrees")
    assert abs(dist(P, A) - dist(P, B)) < EPS
    assert abs(M[0] - 3.0) < EPS and abs(M[1]) < EPS
    assert abs(angle_at(M, P, B) - 90) < EPS

    print()
    print("3.3 equilateral triangle gives 60 degrees")
    C = equilateral_apex(A, B)
    print(f"  apex C = ({C[0]:.6f}, {C[1]:.6f})")
    print(f"  sides: AB={dist(A, B):.6f} AC={dist(A, C):.6f} BC={dist(B, C):.6f}")
    print(f"  angle at A = {angle_at(A, B, C):.6f} degrees")
    assert abs(angle_at(A, B, C) - 60) < EPS

    print()
    print("3.2 bisection, applied repeatedly")
    Z60 = bisect_angle(A, B, C)                 # halve the 60
    print(f"  bisecting 60 -> {angle_at(A, B, Z60):.6f} and {angle_at(A, Z60, C):.6f}")
    assert abs(angle_at(A, B, Z60) - 30) < EPS
    assert abs(angle_at(A, B, Z60) - angle_at(A, Z60, C)) < EPS

    Z30 = bisect_angle(A, B, Z60)               # halve the 30
    print(f"  bisecting 30 -> {angle_at(A, B, Z30):.6f}")
    assert abs(angle_at(A, B, Z30) - 15) < EPS

    print()
    print("3.4 right angle, then 45")
    right = angle_at(M, P, B)
    Z45 = bisect_angle(M, P, B)
    print(f"  right angle  = {right:.6f}")
    print(f"  bisected     = {angle_at(M, P, Z45):.6f}")
    assert abs(angle_at(M, P, Z45) - 45) < EPS

    print()
    print("the radius in 3.1 does not matter")
    for scale in (0.55, 1.0, 2.0, 7.5):
        r = dist(A, B) * scale
        pts = circle_circle(A, r, B, r)
        m = line_line(pts[0], pts[1], A, B)
        print(f"  r = {r:5.2f} -> crossing at x = {m[0]:.6f}")
        assert abs(m[0] - 3.0) < EPS

    print()
    print("constructions: passed")
```

Expected output:

```
3.1 perpendicular bisector of AB
  P is 6.000000 from A and 6.000000 from B
  PQ meets AB at 3.000000, 0.000000  (midpoint is 3.0, 0.0)
  angle between PQ and AB = 90.000000 degrees

3.3 equilateral triangle gives 60 degrees
  apex C = (3.000000, -5.196152)
  sides: AB=6.000000 AC=6.000000 BC=6.000000
  angle at A = 60.000000 degrees

3.2 bisection, applied repeatedly
  bisecting 60 -> 30.000000 and 30.000000
  bisecting 30 -> 15.000000

3.4 right angle, then 45
  right angle  = 90.000000
  bisected     = 45.000000

the radius in 3.1 does not matter
  r =  3.30 -> crossing at x = 3.000000
  r =  6.00 -> crossing at x = 3.000000
  r = 12.00 -> crossing at x = 3.000000
  r = 45.00 -> crossing at x = 3.000000

constructions: passed
```

The final block is the one that matters most: four different compass openings, one identical answer. The construction does not depend on a choice the person makes, which is exactly what "exact" means here.

## 5. What cannot be constructed

Three problems came down from antiquity and resisted every attempt for two thousand years:

- **Trisecting a general angle** — divide any given angle into three equal parts.
- **Doubling the cube** — construct a cube with twice the volume of a given one.
- **Squaring the circle** — construct a square with the same area as a given circle.

All three are **impossible**, and this is a proved theorem, not an admission that nobody has been clever enough yet.

The argument, in outline: start with the two given points, and call the distance between them $1$. Every legal move — intersecting lines and circles — solves at worst a **quadratic** equation in the coordinates you already have. So each new point lives in a field extension of degree $1$ or $2$ over the previous one, and after $n$ steps the degree of any constructible number over the rationals is a power of $2$.

- Doubling the cube needs $\sqrt[3]{2}$, whose minimal polynomial $x^3 - 2$ has degree $3$. And $3$ is not a power of $2$.
- Trisecting $60°$ needs $\cos 20°$, a root of the irreducible cubic $8x^3 - 6x - 1$. Degree $3$ again.
- Squaring the circle needs $\sqrt{\pi}$, and $\pi$ is **transcendental** — not the root of *any* polynomial with rational coefficients (Lindemann, 1882). Its degree is not finite at all.

Wantzel settled the first two in 1837. Note the precision of the claim, though:

> [!WARNING]
> "A general angle cannot be trisected" does not mean "no angle can be trisected". A $90°$ angle trisects perfectly well — $30°$ is constructible, as the lab shows. The impossibility is that **no single procedure works for every angle**. Producing a trisection of one convenient angle refutes nothing.

This is worth sitting with, because it is the first place where a geometry question was answered by algebra, and the answer was *no*. The tools are not weak because of bad technique. Their reach is a mathematical fact.

## Common pitfalls and traps

- **Changing the compass radius mid-construction.** In 3.1 the two arcs must have the *same* radius; that equality is the entire proof. Slipping the compass turns the rhombus into a kite, and the crossing is no longer the midpoint.
- **Choosing a radius that is too small.** If $r < \tfrac{1}{2}AB$ the arcs never meet and there is nothing to draw. The lab's `circle_circle` returns `[]` in that case rather than a wrong answer.
- **Marking a point by eye.** "Where it looks like the middle" is not a legal move, and no proof will support the result.
- **Believing a construction because the drawing looks right.** A drawing at $59.4°$ looks exactly like one at $60°$. Only the proof separates them.
- **Rubbing out the arcs.** In an examination the construction arcs *are* the evidence. A clean final figure with no arcs shows nothing about how the point was found.
- **Reading the lab as a proof.** It confirms the constructions behave as claimed at the precision of floating point, for the cases tried. Section 3 is where the certainty comes from.

## Check your understanding

1. Why must the radius in the perpendicular bisector construction exceed half of $AB$?
2. Which congruence criterion justifies the angle bisector construction, and what are the three pairs of equal parts?
3. Construct $105°$ using only the constructions in this lesson. Which are combined?
4. A classmate says they have trisected an angle with compass and straightedge. What is the one question that settles it?
5. In the lab, `perpendicular_bisector` uses `r = dist(a, b)` — the full length of $AB$, not half. Why is that a safe choice, and what would `r = dist(a, b) / 2` produce?

<details><summary>Answers — open only after an attempt</summary>

1. Two circles of radius $r$ centred at $A$ and $B$ meet only when $2r > AB$. If $r$ is smaller, the circles are separate and no intersection points exist to draw a line through.
2. **SSS**, on triangles $VXZ$ and $VYZ$: $VX = VY$ (same arc from $V$), $XZ = YZ$ (equal arcs from $X$ and $Y$), and $VZ$ is common to both.
3. $105° = 60° + 45°$. Construct $60°$ by the equilateral triangle, construct $90°$ by perpendicular bisector, bisect it to $45°$, and add the two by placing them adjacent. Alternatively $105° = 90° + 15°$, bisecting $60°$ twice.
4. **"Does your method work for *every* angle, or only for the one you drew?"** Trisecting $90°$ or $135°$ is easy and proves nothing. The impossibility is about a general procedure.
5. It is safe because $r = AB$ certainly exceeds $\tfrac{1}{2}AB$, so the arcs cross. With $r = \tfrac{1}{2}AB$ the circles would be exactly tangent at the midpoint — a single intersection point, not two — so there would be no second point to draw the line through, and the `assert len(pts) == 2` would fail.
</details>

## Practice — independent task

Extend the lab with two constructions it does not contain.

**Task A — copy an angle.** Implement `copy_angle(v, p, q, new_vertex, direction_point)`: given an angle $PVQ$ and a new vertex with one arm already drawn towards `direction_point`, construct the second arm so that the new angle equals the original.

The classical method: draw an arc centred at $V$ crossing both arms at $X$ and $Y$; draw an arc of the same radius centred at the new vertex, crossing the given arm at $X'$; then draw an arc centred at $X'$ with radius $XY$; where the two new arcs meet is a point on the second arm.

1. Use only `circle_circle` and `line_line`. No trigonometry, no rotation matrices — those are not compass moves.
2. Assert the new angle equals the old to within `1e-9`, for at least five different starting angles including one obtuse.
3. Prove, on paper, why it works. Name the congruence criterion.

**Task B — a perpendicular from a point to a line.** Implement `foot_of_perpendicular(point, line_a, line_b)` using constructions only, and assert that the segment from the point to the foot makes a $90°$ angle with the line, and that the foot is the **closest** point on the line — check it against several other points on the line.

**Edge cases:** in Task B, handle the point already lying on the line. Say what your function does then, and why that is the right choice rather than an error.

**Done when:** both functions use only the two intersection primitives, all assertions pass, your proof for Task A names its congruence criterion, and you can say what geometric fact Task B's "closest point" check is actually testing.

## Tradeoffs, limits and extensions

**Different tools reach different numbers.** Add a marked ruler (a *neusis* construction) and angle trisection becomes possible — the Greeks knew this and considered it a lesser kind of solution. Origami folds reach the cube root too, so paper folding is strictly more powerful than compass and straightedge. The impossibility results are about a *specific* toolset, not about what is knowable.

**Exactness versus practicality.** A construction is exact in principle and approximate in graphite. A $0.3$ mm pencil line over a $50$ mm segment is a relative error near $0.6\%$ — larger than a decent protractor. Constructions are not chosen for accuracy on paper; they are chosen because the *reasoning* is exact and does not depend on a manufactured scale.

**Where this reappears.** The constructible numbers are the first natural example of a Galois-theoretic argument, and the same field-degree reasoning shows which regular polygons are constructible: exactly those whose side count is a power of $2$ times distinct Fermat primes. So the $17$-gon is constructible — Gauss, aged $19$ — and the $7$-gon is not. That thread continues in **abstract algebra** *(reserved)*.

## Before moving on

You are done with this lesson when you can:

- Carry out all four base constructions and state the proof of each without notes.
- Explain why the choice of radius does not affect the result.
- State the impossibility of general angle trisection precisely enough that "but I trisected $90°$" is obviously not a counterexample.

**Recap for later lookup:** perpendicular bisector = equal arcs from both ends, justified by SSS on a rhombus. Angle bisector = equal arcs from both arms, justified by SSS. $60°$ = equilateral triangle. $90°$ = perpendicular bisector. Halve any of them by bisection. Trisecting a general angle, doubling the cube and squaring the circle are impossible, because constructible numbers have degree a power of $2$ over $\mathbb{Q}$.

**Next:** [[01-circle-theorems|Circle Theorems]] — the same deductive method, applied to the one curve compass-and-straightedge geometry is built on.

## Related

- [[02-triangles-and-polygons|Triangles and Polygons]] — the congruence criteria every proof here rests on
- [[01-angles-and-parallel-lines|Angles and Parallel Lines]] — where the deductive method started
- [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — the same figures handled by algebra instead of arcs
- **Abstract Algebra** *(reserved)* — where the impossibility proofs actually live
