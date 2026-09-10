# Lines and Planes in Space

**[Advanced]** — three-dimensional coordinate geometry, where gradient stops working and vectors take over.

## Before you start

- You can use coordinates, the distance formula and the perpendicularity condition — [[03-coordinate-geometry/01-coordinate-geometry|coordinate geometry]].
- You know $\cos$ and $\sin$ for any angle — [[02-graphs-and-identities|graphs and identities]].
- Useful: the dot product appeared in the proof that $m_1m_2 = -1$ — same coordinate geometry lesson, section 3.

**What you will be able to do after this lesson:**

1. Compute and interpret the **dot** and **cross** products, and say what each one measures.
2. Write a line in vector, parametric and symmetric form, and a plane in normal and Cartesian form.
3. Find where a line meets a plane, and handle the parallel and contained-in cases separately.
4. Recognise **skew** lines — a configuration with no analogue in the plane — and compute the distance between them.

**Study route:** read 1–6, attempt the prediction in section 5, then run the lab. Block 5 is the part with no two-dimensional counterpart.

---

## 1. Why this exists

In two dimensions a line is $y = mx + c$, and gradient does all the work. In three dimensions that breaks immediately: a line in space has no single "rise over run", because there are two independent directions to rise in.

Something worse also happens. In the plane, two distinct lines either meet or are parallel — there is no third option. In space there is: two lines can be neither parallel nor intersecting, passing each other at different heights like an overpass and the road beneath it. These are **skew** lines, and no amount of plane geometry prepares you for them.

So the whole apparatus is rebuilt on **vectors**, which handle any number of dimensions without modification. The payoff is immediate in graphics, robotics and physics: every ray-traced image is line-plane intersections, and every collision test is a distance computation of the kind below.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Vector** | A quantity with magnitude and direction, written $(x, y, z)$ | Position or displacement, depending on use |
| **Magnitude** | Its length, $\lvert\mathbf{a}\rvert = \sqrt{x^2+y^2+z^2}$ | Pythagoras, one dimension up |
| **Unit vector** | A vector of length $1$ | Written $\hat{\mathbf{a}} = \mathbf{a}/\lvert\mathbf{a}\rvert$ |
| **Dot product** | $\mathbf{a}\cdot\mathbf{b}$ — a **number** | Measures alignment |
| **Cross product** | $\mathbf{a}\times\mathbf{b}$ — a **vector** | Measures perpendicularity and area |
| **Direction vector** | A vector along a line | Replaces gradient |
| **Normal** | A vector perpendicular to a plane | Defines the plane's orientation |
| **Skew** | Neither parallel nor intersecting | Only possible in three or more dimensions |

## 3. The two products

### Dot product — a number measuring alignment

$$
\mathbf{a}\cdot\mathbf{b} = a_1b_1 + a_2b_2 + a_3b_3 = \lvert\mathbf{a}\rvert\lvert\mathbf{b}\rvert\cos\theta
$$

The second form is what makes it useful: it extracts the **angle** between two vectors from their coordinates. Three consequences:

- $\mathbf{a}\cdot\mathbf{b} = 0 \iff$ the vectors are **perpendicular** (for non-zero vectors). This is the condition used to prove $m_1m_2 = -1$.
- $\mathbf{a}\cdot\mathbf{a} = \lvert\mathbf{a}\rvert^2$.
- The sign tells you whether the angle is acute (positive) or obtuse (negative).

### Cross product — a vector measuring perpendicularity

$$
\mathbf{a}\times\mathbf{b} = (a_2b_3 - a_3b_2,\ a_3b_1 - a_1b_3,\ a_1b_2 - a_2b_1)
$$

Its defining properties:

- It is **perpendicular to both** $\mathbf{a}$ and $\mathbf{b}$ — which is how you manufacture a normal vector.
- Its magnitude is $\lvert\mathbf{a}\rvert\lvert\mathbf{b}\rvert\sin\theta$, the **area of the parallelogram** they span. So $\mathbf{a}\times\mathbf{b} = \mathbf{0}$ exactly when the vectors are parallel.
- Its direction follows the right-hand rule, and it is **anticommutative**: $\mathbf{a}\times\mathbf{b} = -\mathbf{b}\times\mathbf{a}$.

The two products are complementary: the dot is largest when the vectors align and zero when perpendicular; the cross is zero when they align and largest when perpendicular. Between them, $(\mathbf{a}\cdot\mathbf{b})^2 + \lvert\mathbf{a}\times\mathbf{b}\rvert^2 = \lvert\mathbf{a}\rvert^2\lvert\mathbf{b}\rvert^2$, which is $\cos^2 + \sin^2 = 1$ in disguise. Block 1 checks it.

## 4. Lines

A line is fixed by a point on it and a direction along it. With position vector $\mathbf{a}$ and direction $\mathbf{d}$:

$$
\mathbf{r} = \mathbf{a} + t\mathbf{d}, \qquad t \in \mathbb{R}
$$

Writing out the components gives the **parametric form**:

$$
x = a_1 + t d_1, \qquad y = a_2 + t d_2, \qquad z = a_3 + t d_3
$$

and eliminating $t$ gives the **symmetric form**:

$$
\frac{x - a_1}{d_1} = \frac{y - a_2}{d_2} = \frac{z - a_3}{d_3}
$$

valid only when no component of $\mathbf{d}$ is zero — the same kind of exception vertical lines caused in two dimensions, and a reason to prefer the parametric form in code.

## 5. Planes

A plane is fixed by a point on it and a **normal** direction. A point $\mathbf{r}$ lies on it exactly when the displacement from $\mathbf{a}$ is perpendicular to the normal:

$$
\mathbf{n}\cdot(\mathbf{r} - \mathbf{a}) = 0
$$

Expanding with $\mathbf{n} = (a, b, c)$ gives the Cartesian form:

$$
ax + by + cz = d
$$

where $d = \mathbf{n}\cdot\mathbf{a}$. **The coefficients are the normal vector** — that is the fact worth carrying away, and it makes most plane problems immediate.

**Distance from a point to a plane** is the direct analogue of the two-dimensional formula:

$$
\text{distance} = \frac{\lvert \mathbf{n}\cdot\mathbf{p} - d \rvert}{\lvert\mathbf{n}\rvert}
$$

**Line meets plane.** Substitute $\mathbf{r} = \mathbf{a} + t\mathbf{d}$ into $\mathbf{n}\cdot\mathbf{r} = d$:

$$
\mathbf{n}\cdot\mathbf{a} + t\,(\mathbf{n}\cdot\mathbf{d}) = d \quad\Longrightarrow\quad t = \frac{d - \mathbf{n}\cdot\mathbf{a}}{\mathbf{n}\cdot\mathbf{d}}
$$

Three cases, decided by the denominator:

| Condition | Meaning |
| :--- | :--- |
| $\mathbf{n}\cdot\mathbf{d} \neq 0$ | Exactly one intersection point |
| $\mathbf{n}\cdot\mathbf{d} = 0$ and $\mathbf{n}\cdot\mathbf{a} \neq d$ | Line **parallel** to the plane, never meets it |
| $\mathbf{n}\cdot\mathbf{d} = 0$ and $\mathbf{n}\cdot\mathbf{a} = d$ | Line lies **inside** the plane — every point is an intersection |

A ray tracer performs this test billions of times, and the degenerate branches are where the bugs live.

> [!TIP]
> **Predict before section 6.** Two lines in space are not parallel. In the plane that would guarantee they meet. Does it here? If not, what extra condition is needed for them to intersect? Decide before opening the answers.

## 6. Skew lines

Two lines $\mathbf{r}_1 = \mathbf{a}_1 + s\mathbf{d}_1$ and $\mathbf{r}_2 = \mathbf{a}_2 + t\mathbf{d}_2$ fall into exactly one of four cases:

| Case | Test |
| :--- | :--- |
| **Parallel** | $\mathbf{d}_1 \times \mathbf{d}_2 = \mathbf{0}$, and the lines are distinct |
| **Identical** | Parallel, and $\mathbf{a}_2$ lies on line 1 |
| **Intersecting** | Not parallel, and $(\mathbf{a}_2 - \mathbf{a}_1)\cdot(\mathbf{d}_1\times\mathbf{d}_2) = 0$ |
| **Skew** | Not parallel, and that triple product is **non-zero** |

The triple product $(\mathbf{a}_2 - \mathbf{a}_1)\cdot(\mathbf{d}_1\times\mathbf{d}_2)$ is the volume of the parallelepiped spanned by the three vectors. It is zero exactly when they are **coplanar** — and two non-parallel lines meet precisely when they lie in a common plane.

When the volume is non-zero, the lines are skew, and their shortest distance is that volume divided by the base area:

$$
\text{distance} = \frac{\lvert (\mathbf{a}_2 - \mathbf{a}_1)\cdot(\mathbf{d}_1\times\mathbf{d}_2) \rvert}{\lvert \mathbf{d}_1\times\mathbf{d}_2 \rvert}
$$

## Worked example — runnable

**Runnable example:** save as `lines_planes.py` in any empty directory and run `python3 lines_planes.py`. Standard library only; writes no files.

```python
"""Vectors, lines and planes in three dimensions."""
import math

EPS = 1e-9


def add(a, b):      return tuple(x + y for x, y in zip(a, b))
def sub(a, b):      return tuple(x - y for x, y in zip(a, b))
def scale(a, k):    return tuple(k * x for x in a)
def dot(a, b):      return sum(x * y for x, y in zip(a, b))
def norm(a):        return math.sqrt(dot(a, a))


def cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])


def angle_between(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, dot(a, b) / (norm(a) * norm(b))))))


def line_plane_intersection(point, direction, normal, d):
    """Returns (kind, value). kind is 'point', 'parallel' or 'contained'."""
    denom = dot(normal, direction)
    if abs(denom) > EPS:
        t = (d - dot(normal, point)) / denom
        return "point", add(point, scale(direction, t))
    if abs(dot(normal, point) - d) < EPS:
        return "contained", None
    return "parallel", None


def point_plane_distance(p, normal, d):
    return abs(dot(normal, p) - d) / norm(normal)


def classify_lines(a1, d1, a2, d2):
    """One of: parallel, identical, intersecting, skew."""
    n = cross(d1, d2)
    gap = sub(a2, a1)
    if norm(n) < EPS:                       # directions are parallel
        # is a2 on line 1? then the lines coincide
        return "identical" if norm(cross(gap, d1)) < EPS else "parallel"
    return "intersecting" if abs(dot(gap, n)) < EPS else "skew"


def line_line_distance(a1, d1, a2, d2):
    n = cross(d1, d2)
    gap = sub(a2, a1)
    if norm(n) < EPS:                       # parallel: distance to a point
        return norm(cross(gap, d1)) / norm(d1)
    return abs(dot(gap, n)) / norm(n)


if __name__ == "__main__":
    print("Block 1 - the two products are complementary")
    print("        a            b        a.b    |axb|   angle   check")
    for a, b in [((1, 0, 0), (0, 1, 0)),
                 ((1, 0, 0), (1, 0, 0)),
                 ((1, 2, 3), (4, 5, 6)),
                 ((2, -1, 3), (-1, 4, 2))]:
        d, c = dot(a, b), norm(cross(a, b))
        identity = d * d + c * c
        expected = norm(a) ** 2 * norm(b) ** 2
        print(f"  {str(a):>12} {str(b):>12}  {d:5.1f}  {c:7.4f}  {angle_between(a,b):6.2f}"
              f"   {identity:.6f} = {expected:.6f}")
        assert abs(identity - expected) < 1e-9
    print("  (a.b)^2 + |axb|^2 = |a|^2|b|^2, which is cos^2 + sin^2 = 1 rescaled")

    print()
    print("  the cross product is perpendicular to both inputs:")
    a, b = (1, 2, 3), (4, 5, 6)
    c = cross(a, b)
    print(f"    a x b = {c},  (axb).a = {dot(c, a)},  (axb).b = {dot(c, b)}")
    assert dot(c, a) == 0 and dot(c, b) == 0
    print(f"    and it is anticommutative: b x a = {cross(b, a)}")
    assert cross(b, a) == scale(c, -1)

    print()
    print("Block 2 - a plane's Cartesian coefficients ARE its normal")
    normal, d = (2.0, -3.0, 6.0), 12.0      # 2x - 3y + 6z = 12
    print(f"  plane 2x - 3y + 6z = 12, normal {normal}, |n| = {norm(normal)}")
    for p in [(6.0, 0.0, 0.0), (0.0, 0.0, 2.0), (0.0, 0.0, 0.0), (2.0, 2.0, 2.0)]:
        on = abs(dot(normal, p) - d) < EPS
        print(f"    {str(p):>18}: distance {point_plane_distance(p, normal, d):8.6f}"
              f"   {'on the plane' if on else ''}")
    assert point_plane_distance((6.0, 0.0, 0.0), normal, d) < EPS
    assert abs(point_plane_distance((0.0, 0.0, 0.0), normal, d) - 12/7) < EPS

    print()
    print("Block 3 - line meets plane: all three cases")
    cases = [
        ("crosses it",  (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
        ("parallel",    (0.0, 0.0, 0.0), (3.0, 2.0, 0.0)),   # dot with normal = 0
        ("contained",   (6.0, 0.0, 0.0), (3.0, 2.0, 0.0)),   # starts ON the plane
    ]
    for label, point, direction in cases:
        kind, value = line_plane_intersection(point, direction, normal, d)
        extra = "" if value is None else f" at {tuple(round(v, 6) for v in value)}"
        print(f"  {label:12} -> {kind}{extra}")
        if kind == "point":
            assert abs(dot(normal, value) - d) < EPS
    assert line_plane_intersection((0.,0.,0.), (3.,2.,0.), normal, d)[0] == "parallel"
    assert line_plane_intersection((6.,0.,0.), (3.,2.,0.), normal, d)[0] == "contained"

    print()
    print("Block 4 - the angle between two planes is the angle between their normals")
    n1, n2 = (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)
    print(f"  normals {n1} and {n2}: angle {angle_between(n1, n2):.4f} degrees")
    assert abs(angle_between(n1, n2) - 45) < 1e-9

    print()
    print("Block 5 - the case the plane has no room for: skew lines")
    pairs = [
        ("intersecting", (0.,0.,0.), (1.,0.,0.), (0.,0.,0.), (0.,1.,0.)),
        ("parallel",     (0.,0.,0.), (1.,0.,0.), (0.,1.,0.), (2.,0.,0.)),
        ("identical",    (0.,0.,0.), (1.,0.,0.), (5.,0.,0.), (-3.,0.,0.)),
        ("skew",         (0.,0.,0.), (1.,0.,0.), (0.,0.,1.), (0.,1.,0.)),
    ]
    for expected, a1, d1, a2, d2 in pairs:
        kind = classify_lines(a1, d1, a2, d2)
        dist = line_line_distance(a1, d1, a2, d2)
        print(f"  {expected:13} -> classified {kind:13} distance {dist:.6f}")
        assert kind == expected, (expected, kind)
    # the skew pair above is the x-axis and a line one unit above it along y
    assert abs(line_line_distance((0.,0.,0.), (1.,0.,0.), (0.,0.,1.), (0.,1.,0.)) - 1) < EPS
    print("  the last pair is the x-axis and a line running along y one unit up:")
    print("  never parallel, never meeting - exactly 1 unit apart")

    print()
    print("lines_planes: passed")
```

Expected output:

```
Block 1 - the two products are complementary
        a            b        a.b    |axb|   angle   check
     (1, 0, 0)    (0, 1, 0)    0.0   1.0000   90.00   1.000000 = 1.000000
     (1, 0, 0)    (1, 0, 0)    1.0   0.0000    0.00   1.000000 = 1.000000
     (1, 2, 3)    (4, 5, 6)   32.0   7.3485   12.93   1078.000000 = 1078.000000
    (2, -1, 3)   (-1, 4, 2)    0.0  17.1464   90.00   294.000000 = 294.000000
  (a.b)^2 + |axb|^2 = |a|^2|b|^2, which is cos^2 + sin^2 = 1 rescaled

  the cross product is perpendicular to both inputs:
    a x b = (-3, 6, -3),  (axb).a = 0,  (axb).b = 0
    and it is anticommutative: b x a = (3, -6, 3)

Block 2 - a plane's Cartesian coefficients ARE its normal
  plane 2x - 3y + 6z = 12, normal (2.0, -3.0, 6.0), |n| = 7.0
       (6.0, 0.0, 0.0): distance 0.000000   on the plane
       (0.0, 0.0, 2.0): distance 0.000000   on the plane
       (0.0, 0.0, 0.0): distance 1.714286   
       (2.0, 2.0, 2.0): distance 0.285714   

Block 3 - line meets plane: all three cases
  crosses it   -> point at (2.4, 2.4, 2.4)
  parallel     -> parallel
  contained    -> contained

Block 4 - the angle between two planes is the angle between their normals
  normals (1.0, 0.0, 0.0) and (1.0, 1.0, 0.0): angle 45.0000 degrees

Block 5 - the case the plane has no room for: skew lines
  intersecting  -> classified intersecting  distance 0.000000
  parallel      -> classified parallel      distance 1.000000
  identical     -> classified identical     distance 0.000000
  skew          -> classified skew          distance 1.000000
  the last pair is the x-axis and a line running along y one unit up:
  never parallel, never meeting - exactly 1 unit apart

lines_planes: passed
```

Block 5 is the part with no two-dimensional analogue. In the plane, "not parallel" forces intersection. In space it does not, and the triple product is what distinguishes the two outcomes.

## Common pitfalls and traps

- **Assuming non-parallel lines must meet.** True in the plane, false in space. This is the most important structural difference in the lesson.
- **Writing $\mathbf{a}\times\mathbf{b} = \mathbf{b}\times\mathbf{a}$.** The cross product is anticommutative — swapping the arguments reverses the result. The dot product *is* commutative, and mixing up which is which is easy.
- **Confusing the two products' types.** The dot product returns a **number**; the cross product returns a **vector**. An expression like $\mathbf{a}\cdot\mathbf{b}\times\mathbf{c}$ only parses one way for that reason.
- **Using the symmetric form of a line when a direction component is zero.** It divides by zero. Use the parametric form.
- **Forgetting to normalise before using the distance formula.** The $\lvert\mathbf{n}\rvert$ in the denominator is not optional; without it the answer scales with however you happened to write the plane's equation.
- **Ignoring the degenerate branches of line-plane intersection.** "Parallel" and "contained" both give $\mathbf{n}\cdot\mathbf{d} = 0$ and must be told apart by a second test. Code that only handles the generic case fails silently on exactly the inputs that matter.

## Check your understanding

1. Find $\mathbf{a}\cdot\mathbf{b}$ and $\mathbf{a}\times\mathbf{b}$ for $\mathbf{a} = (2, -1, 3)$, $\mathbf{b} = (1, 4, -2)$.
2. Find the angle between $(1,1,0)$ and $(1,0,1)$.
3. Find the equation of the plane through $(1,2,3)$ with normal $(4,-1,2)$.
4. Find the distance from $(1,1,1)$ to the plane $2x + y - 2z = 6$.
5. Are the lines $\mathbf{r} = (1,0,0) + s(1,1,0)$ and $\mathbf{r} = (0,1,1) + t(1,-1,0)$ skew? Show your test.

<details><summary>Answers — open only after an attempt</summary>

1. $\mathbf{a}\cdot\mathbf{b} = 2 - 4 - 6 = -8$ — negative, so the angle is obtuse. $\mathbf{a}\times\mathbf{b} = ((-1)(-2) - (3)(4),\ (3)(1) - (2)(-2),\ (2)(4) - (-1)(1)) = (2 - 12,\ 3 + 4,\ 8 + 1) = (-10, 7, 9)$.
2. $\cos\theta = \frac{1}{\sqrt2 \cdot \sqrt2} = \tfrac12$, so $\theta = 60°$.
3. $4(x-1) - 1(y-2) + 2(z-3) = 0$, so $4x - y + 2z = 4 - 2 + 6 = 8$.
4. $\frac{\lvert 2 + 1 - 2 - 6\rvert}{\sqrt{4+1+4}} = \frac{5}{3}$.
5. $\mathbf{d}_1\times\mathbf{d}_2 = (1,1,0)\times(1,-1,0) = (0, 0, -2)$, non-zero, so they are not parallel. The gap is $(0,1,1)-(1,0,0) = (-1,1,1)$, and $(-1,1,1)\cdot(0,0,-2) = -2 \neq 0$. Non-zero triple product, so the lines are **skew**, at distance $\frac{2}{2} = 1$.

**And the prediction from section 5:** no, non-parallel lines need **not** meet in space. They intersect only if they are additionally **coplanar**, which is exactly what the vanishing triple product $(\mathbf{a}_2-\mathbf{a}_1)\cdot(\mathbf{d}_1\times\mathbf{d}_2) = 0$ tests. Otherwise they are skew.
</details>

## Practice — independent task

Implement `ray_triangle_intersection(origin, direction, v0, v1, v2)` — the single most-executed geometric routine in computer graphics.

1. Build the triangle's plane from its vertices: the normal is $(\mathbf{v}_1 - \mathbf{v}_0)\times(\mathbf{v}_2-\mathbf{v}_0)$.
2. Intersect the ray with that plane using section 5, handling the parallel and contained cases.
3. Test whether the intersection point lies **inside** the triangle. Use barycentric coordinates: express $\mathbf{p} - \mathbf{v}_0$ in terms of the two edge vectors and require both coefficients to be non-negative with their sum at most $1$.
4. A **ray** is not a line — reject intersections behind the origin ($t < 0$).
5. Verify against known cases: a ray straight down onto a triangle in the $z=0$ plane; a ray that misses; a ray parallel to the plane; a ray pointing away. Then check that a point you generate *inside* the triangle by construction is always reported as a hit.

**Edge cases:** a degenerate triangle with zero area; a hit exactly on an edge or at a vertex — decide whether that counts and justify the choice (in a renderer, two adjacent triangles sharing an edge must not both miss, or you get visible cracks); a ray origin lying on the triangle's plane.

**Done when:** your five verification cases pass, at least fifty randomly generated interior points are all reported as hits, and you can state your edge-case policy and why a renderer needs it.

## Tradeoffs, limits and extensions

**The cross product is unusual.** It exists as defined only in three dimensions (and, in a different form, seven). The general-dimension replacement is the **wedge product** of exterior algebra, and the "vector" the cross product returns is really a bivector that happens to be representable as a vector in 3D. This is why the cross product behaves oddly under reflection — it is a *pseudovector*, and its direction depends on a handedness convention rather than on the geometry.

**Floating point and near-degeneracy.** Classifying two lines as parallel means testing $\lvert\mathbf{d}_1\times\mathbf{d}_2\rvert$ against a tolerance. Nearly-parallel lines are genuinely hard: the computed intersection point flies off to infinity, and no tolerance choice is right for all scales. Robust geometric predicates are a research area for this reason, and the lab's fixed `EPS` would not survive production use on coordinates spanning many orders of magnitude.

**Where this goes.** Systems of plane equations are systems of linear equations, and asking whether three planes meet in a point, a line, or not at all is asking about the rank of a matrix — which is **systems of linear equations** *(reserved)* and **vector spaces** *(reserved)*. The dot product generalises to the inner product, and the whole apparatus becomes dimension-independent.

## Before moving on

You are done with this lesson when you can:

- Compute both products and say what each measures.
- Write a line and a plane in every form given here, and convert between them.
- Intersect a line with a plane, handling all three cases.
- Classify a pair of lines and compute the distance between skew ones.

**Recap for later lookup:** $\mathbf{a}\cdot\mathbf{b} = \lvert\mathbf{a}\rvert\lvert\mathbf{b}\rvert\cos\theta$, zero iff perpendicular; $\lvert\mathbf{a}\times\mathbf{b}\rvert = \lvert\mathbf{a}\rvert\lvert\mathbf{b}\rvert\sin\theta$, zero iff parallel, direction perpendicular to both; line $\mathbf{r} = \mathbf{a} + t\mathbf{d}$; plane $\mathbf{n}\cdot\mathbf{r} = d$, coefficients are the normal; point-plane distance $\frac{\lvert\mathbf{n}\cdot\mathbf{p} - d\rvert}{\lvert\mathbf{n}\rvert}$; lines are skew iff not parallel and $(\mathbf{a}_2-\mathbf{a}_1)\cdot(\mathbf{d}_1\times\mathbf{d}_2)\neq 0$.

**Next:** [[02-quadric-surfaces|Quadric Surfaces]] — what second-degree equations describe in space, and a surface curved everywhere that is nonetheless built from straight lines.

## Related

- [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — the two-dimensional version, and where the dot product first appeared
- **Vectors** *(reserved)* — the same objects, developed as algebra
- **Systems of Linear Equations** *(reserved)* — intersecting several planes at once
