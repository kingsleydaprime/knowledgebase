# Quadric Surfaces

**[Advanced]** — what second-degree equations describe in space, and the curved surface you can build entirely from straight beams.

## Before you start

- You can work with planes, normals and the dot product — [[01-lines-and-planes|lines and planes in space]].
- You know the circle and its equation, and completing the square — [[03-coordinate-geometry/01-coordinate-geometry|coordinate geometry]].
- Helpful: Cavalieri's slicing argument — [[02-solids|solids]]. The method of traces is the same idea used to *identify* rather than measure.

**What you will be able to do after this lesson:**

1. Identify any quadric surface from its equation by the **signs** of its squared terms.
2. Use the **method of traces** — cutting with coordinate planes — to determine a surface's shape without plotting it.
3. Explain what a **ruled surface** is, and verify that a hyperboloid of one sheet contains two distinct families of straight lines.
4. Recognise a **saddle**, and say why it is neither a maximum nor a minimum.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 3 verifies the fact that sounds impossible.

---

## 1. Why this exists

In the plane, second-degree equations give the conic sections: circles, ellipses, parabolas, hyperbolas. In space they give the **quadric surfaces**, and each one is in industrial use:

- A **paraboloid** focuses every incoming parallel ray to a single point. Every satellite dish, radio telescope and car headlight reflector is one.
- A **hyperboloid of one sheet** is the shape of a power-station cooling tower — chosen because, remarkably, it can be built from **straight** steel members despite being curved in every direction.
- A **hyperbolic paraboloid** is the saddle, and saddle points dominate the landscape that gradient descent has to navigate in high dimensions.

There is also a classification worth having for its own sake. There are infinitely many second-degree equations in three variables, but up to rotation and translation only a handful of distinct shapes, and the signs of three coefficients tell you which one you have.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Quadric surface** | The solution set of a second-degree equation in $x, y, z$ | The 3D analogue of a conic section |
| **Trace** | The curve where the surface meets a plane | Usually $x = k$, $y = k$ or $z = k$ |
| **Sheet** | A connected piece of the surface | A hyperboloid has one or two |
| **Ruled surface** | A surface through every point of which a straight line lies entirely in the surface | A cylinder and a cone are the easy cases |
| **Doubly ruled** | Two distinct lines through every point | Only the plane, the hyperboloid of one sheet, and the hyperbolic paraboloid |
| **Saddle point** | A point that is a minimum in one direction and a maximum in another | Neither a peak nor a pit |

## 3. The classification

Every quadric can be rotated and translated into one of these standard forms. **The signs decide the shape:**

| Standard form | Signs | Surface |
| :--- | :---: | :--- |
| $\dfrac{x^2}{a^2} + \dfrac{y^2}{b^2} + \dfrac{z^2}{c^2} = 1$ | $+\,+\,+$ | **Ellipsoid** (a sphere if $a=b=c$) |
| $\dfrac{x^2}{a^2} + \dfrac{y^2}{b^2} - \dfrac{z^2}{c^2} = 1$ | $+\,+\,-$ | **Hyperboloid of one sheet** |
| $\dfrac{x^2}{a^2} - \dfrac{y^2}{b^2} - \dfrac{z^2}{c^2} = 1$ | $+\,-\,-$ | **Hyperboloid of two sheets** |
| $\dfrac{x^2}{a^2} + \dfrac{y^2}{b^2} - \dfrac{z^2}{c^2} = 0$ | $+\,+\,-$, $=0$ | **Cone** — the boundary case between the two hyperboloids |
| $z = \dfrac{x^2}{a^2} + \dfrac{y^2}{b^2}$ | both $+$ | **Elliptic paraboloid** — the dish |
| $z = \dfrac{x^2}{a^2} - \dfrac{y^2}{b^2}$ | mixed | **Hyperbolic paraboloid** — the saddle |

The **number of minus signs** on the left of $=1$ tells you the whole story: none gives a closed surface, one gives a connected surface with a waist, two gives a surface in two separate pieces.

### The method of traces

To identify a surface without plotting it, cut it with planes and see what curves appear.

Take $x^2 + y^2 - z^2 = 1$:

- **$z = k$:** substituting gives $x^2 + y^2 = 1 + k^2$ — a **circle** of radius $\sqrt{1+k^2}$, for *every* $k$. So horizontal slices are circles, smallest at $z=0$ where the radius is $1$, widening in both directions. That is the cooling-tower waist.
- **$y = 0$:** $x^2 - z^2 = 1$ — a **hyperbola** opening left and right.
- **$x = 0$:** $y^2 - z^2 = 1$ — another hyperbola.

Circles horizontally, hyperbolas vertically, one connected piece: a hyperboloid of one sheet. Block 1 of the lab does this mechanically.

Compare with $x^2 - y^2 - z^2 = 1$. Now the $z=k$ trace is $x^2 = 1 + y^2 + k^2$, which forces $\lvert x\rvert \ge 1$ — **no points at all** for $\lvert x \rvert < 1$. The surface is empty in a slab through the middle, so it comes in two separate sheets.

## 4. Ruled surfaces

A surface is **ruled** if through every point there is a straight line lying entirely within it. Cones and cylinders are obviously ruled. The surprise is this:

> The hyperboloid of one sheet — curved in every direction, with no flat piece anywhere — is **doubly ruled**. Two distinct straight lines pass through each of its points, and both lie wholly in the surface.

This is why cooling towers, and Shukhov's lattice towers, are built from straight members: the formwork and the steel are straight, and the curved surface emerges from how they are arranged. It is far cheaper than fabricating curved beams.

**The two families, explicitly.** For $x^2 + y^2 - z^2 = 1$, take the point $(\cos\theta, \sin\theta, 0)$ on the waist circle and the two directions:

$$
\mathbf{d}^{\pm} = (\mp\sin\theta,\ \pm\cos\theta,\ 1)
$$

Every point on either line satisfies the equation. Take the $+$ family and substitute $x = \cos\theta - t\sin\theta$, $y = \sin\theta + t\cos\theta$, $z = t$:

$$
x^2 + y^2 = \cos^2\theta - 2t\sin\theta\cos\theta + t^2\sin^2\theta + \sin^2\theta + 2t\sin\theta\cos\theta + t^2\cos^2\theta
$$

The cross terms cancel, and $\sin^2 + \cos^2 = 1$ twice:

$$
x^2 + y^2 = 1 + t^2 = 1 + z^2 \quad\Longrightarrow\quad x^2 + y^2 - z^2 = 1 \qquad \blacksquare
$$

for **every** $t$ and every $\theta$. The $-$ family works identically. Block 3 of the lab checks both.

The hyperbolic paraboloid is doubly ruled too, and more obviously: rotating $z = x^2 - y^2$ by $45°$ turns it into $z = xy$, in which fixing $x = a$ leaves $z = ay$ — a straight line — and likewise for $y = b$.

> [!TIP]
> **Predict before section 5.** On the surface $z = x^2 - y^2$, walk away from the origin along the $x$-axis. Does $z$ rise or fall? Now walk along the $y$-axis. What does that make the origin — a maximum, a minimum, or neither? Decide before opening the answers.

## 5. The saddle, and why it matters

The origin of $z = x^2 - y^2$ is a **saddle point**. Along the $x$-axis ($y=0$) the surface is $z = x^2$, a valley with a minimum at the origin. Along the $y$-axis ($x=0$) it is $z = -y^2$, a ridge with a maximum there.

So the origin is simultaneously the lowest point of one cross-section and the highest of another. It is a stationary point — the surface is momentarily flat there in every direction — but it is neither a maximum nor a minimum.

This is not a curiosity. In high-dimensional optimisation, a stationary point is a true minimum only if it curves upwards in **every** one of the many directions. With $n$ independent directions and no reason for the curvature signs to agree, saddle points vastly outnumber genuine minima as $n$ grows. That is the central obstacle in training large models, and it is developed properly in [[06-calculus/04-calculus-3/03-optimization|multivariable optimisation]].

## Worked example — runnable

**Runnable example:** save as `quadrics.py` in any empty directory and run `python3 quadrics.py`. Standard library only; writes no files.

```python
"""Quadric surfaces: classification by traces, ruling lines, and the saddle."""
import math

EPS = 1e-9


def trace_kind(coefficients, fixed_axis, k):
    """What curve appears when a quadric Ax^2 + By^2 + Cz^2 = D is cut by a plane.

    Substituting the fixed coordinate leaves a 2-variable quadratic; the signs
    of the two remaining coefficients and of the constant decide the curve.
    """
    A, B, C, D = coefficients
    coeffs = {"x": A, "y": B, "z": C}
    fixed = coeffs.pop(fixed_axis)
    (p, q) = list(coeffs.values())
    rhs = D - fixed * k * k

    if abs(p) < EPS or abs(q) < EPS:      # a squared term is missing
        return "parabola or lines"
    if p * q < 0:                          # opposite signs: a hyperbola
        return "hyperbola" if abs(rhs) > EPS else "two crossing lines"
    # same sign: multiply through by -1 if needed so both are positive
    if p < 0:
        p, q, rhs = -p, -q, -rhs
    if rhs > EPS:
        return "ellipse" if abs(p - q) > EPS else "circle"
    return "single point" if abs(rhs) < EPS else "empty"


def on_hyperboloid(x, y, z):
    return x * x + y * y - z * z


def ruling_point(theta, t, family):
    """A point on one of the two straight lines through (cos t, sin t, 0)."""
    s = 1 if family == "+" else -1
    return (math.cos(theta) - s * t * math.sin(theta),
            math.sin(theta) + s * t * math.cos(theta),
            t)


def saddle(x, y):
    return x * x - y * y


if __name__ == "__main__":
    print("Block 1 - identifying surfaces by their traces")
    surfaces = [
        ("x^2 + y^2 + z^2 = 1   (ellipsoid)",            (1, 1, 1, 1)),
        ("x^2 + y^2 - z^2 = 1   (one sheet)",            (1, 1, -1, 1)),
        ("x^2 - y^2 - z^2 = 1   (two sheets)",           (1, -1, -1, 1)),
        ("x^2 + y^2 - z^2 = 0   (cone)",                 (1, 1, -1, 0)),
    ]
    for label, coeffs in surfaces:
        print(f"  {label}")
        for axis in ("z", "y"):
            kinds = [f"{axis}={k}: {trace_kind(coeffs, axis, k):20}" for k in (0, 1, 2)]
            print("      " + "".join(kinds))

    print()
    print("  the two-sheet case is empty in a slab, which is what splits it:")
    for k in (0.0, 0.5, 0.99, 1.0, 2.0):
        # x^2 = 1 + y^2 + z^2 has no solution with |x| < 1
        print(f"    plane x={k:4}: {trace_kind((1, -1, -1, 1), 'x', k)}")
    assert trace_kind((1, -1, -1, 1), "x", 0.0) == "empty"
    assert trace_kind((1, -1, -1, 1), "x", 2.0) == "circle"
    assert trace_kind((1, 1, -1, 1), "z", 0.0) == "circle"
    assert trace_kind((1, 1, -1, 1), "y", 0.0) == "hyperbola"

    print()
    print("Block 2 - the waist of the one-sheet hyperboloid")
    print("      z    radius of the circular trace")
    for z in (0.0, 1.0, 2.0, 5.0):
        print(f"  {z:5.1f}    {math.sqrt(1 + z*z):.6f}")
    print("  narrowest at z = 0 and widening both ways: the cooling-tower profile")

    print()
    print("Block 3 - the doubly ruled hyperboloid: straight lines on a curved surface")
    worst = 0.0
    for theta_deg in (0, 37, 90, 214, 300):
        theta = math.radians(theta_deg)
        for family in ("+", "-"):
            for t in (-50.0, -3.0, 0.0, 1.5, 50.0):
                x, y, z = ruling_point(theta, t, family)
                worst = max(worst, abs(on_hyperboloid(x, y, z) - 1))
        p0 = ruling_point(theta, 0.0, "+")
        p1 = ruling_point(theta, 1.0, "+")
        p2 = ruling_point(theta, 2.0, "+")
        # collinear? the three points must be equally spaced along one direction
        d1 = tuple(b - a for a, b in zip(p0, p1))
        d2 = tuple(c - b for b, c in zip(p1, p2))
        assert all(abs(u - v) < EPS for u, v in zip(d1, d2)), "not a straight line"
        print(f"  theta={theta_deg:4} deg: both families stay on the surface,"
              f" direction {tuple(round(v, 4) for v in d1)}")
    print(f"  largest deviation from x^2+y^2-z^2 = 1 over all points tested: {worst:.2e}")
    assert worst < 1e-12

    print()
    print("  the two lines through one point are genuinely different:")
    th = math.radians(37)
    dplus = tuple(b - a for a, b in zip(ruling_point(th, 0, "+"), ruling_point(th, 1, "+")))
    dminus = tuple(b - a for a, b in zip(ruling_point(th, 0, "-"), ruling_point(th, 1, "-")))
    print(f"    family +: {tuple(round(v,6) for v in dplus)}")
    print(f"    family -: {tuple(round(v,6) for v in dminus)}")
    assert any(abs(a - b) > EPS for a, b in zip(dplus, dminus))

    print()
    print("Block 4 - the saddle z = x^2 - y^2 at the origin")
    print("     step   along x-axis   along y-axis   diagonal x=y")
    for step in (0.0, 0.5, 1.0, 2.0):
        print(f"  {step:7.1f}   {saddle(step, 0):12.4f}   {saddle(0, step):12.4f}"
              f"   {saddle(step, step):12.4f}")
    assert saddle(1, 0) > saddle(0, 0), "a minimum along x"
    assert saddle(0, 1) < saddle(0, 0), "a maximum along y"
    assert abs(saddle(1, 1) - saddle(0, 0)) < EPS, "flat along the diagonal"
    print("  minimum along x, maximum along y, and exactly level along x = y")
    print("  so the origin is stationary but is neither a max nor a min")

    print()
    print("Block 5 - why a paraboloid is used for dishes: parallel rays meet at the focus")
    FOCUS = 2.0                       # y = x^2 / (4f) has its focus at (0, f)
    for x0 in (0.5, 1.0, 3.0, 7.0):
        y0 = x0 * x0 / (4 * FOCUS)
        slope = x0 / (2 * FOCUS)                       # dy/dx
        n = (-slope, 1.0)                              # normal to the curve
        n_len = math.hypot(*n)
        n = (n[0] / n_len, n[1] / n_len)
        d = (0.0, -1.0)                                # incoming ray, straight down
        dot = d[0] * n[0] + d[1] * n[1]
        r = (d[0] - 2 * dot * n[0], d[1] - 2 * dot * n[1])   # reflected direction
        # where does the reflected ray cross x = 0?
        t = -x0 / r[0]
        y_at_axis = y0 + t * r[1]
        print(f"  ray at x={x0:4.1f} reflects to cross the axis at y = {y_at_axis:.9f}")
        assert abs(y_at_axis - FOCUS) < 1e-9
    print(f"  every one of them passes through the focus at y = {FOCUS}")

    print()
    print("quadrics: passed")
```

Expected output:

```
Block 1 - identifying surfaces by their traces
  x^2 + y^2 + z^2 = 1   (ellipsoid)
      z=0: circle              z=1: single point        z=2: empty               
      y=0: circle              y=1: single point        y=2: empty               
  x^2 + y^2 - z^2 = 1   (one sheet)
      z=0: circle              z=1: circle              z=2: circle              
      y=0: hyperbola           y=1: two crossing lines  y=2: hyperbola           
  x^2 - y^2 - z^2 = 1   (two sheets)
      z=0: hyperbola           z=1: hyperbola           z=2: hyperbola           
      y=0: hyperbola           y=1: hyperbola           y=2: hyperbola           
  x^2 + y^2 - z^2 = 0   (cone)
      z=0: single point        z=1: circle              z=2: circle              
      y=0: two crossing lines  y=1: hyperbola           y=2: hyperbola           

  the two-sheet case is empty in a slab, which is what splits it:
    plane x= 0.0: empty
    plane x= 0.5: empty
    plane x=0.99: empty
    plane x= 1.0: single point
    plane x= 2.0: circle

Block 2 - the waist of the one-sheet hyperboloid
      z    radius of the circular trace
    0.0    1.000000
    1.0    1.414214
    2.0    2.236068
    5.0    5.099020
  narrowest at z = 0 and widening both ways: the cooling-tower profile

Block 3 - the doubly ruled hyperboloid: straight lines on a curved surface
  theta=   0 deg: both families stay on the surface, direction (0.0, 1.0, 1.0)
  theta=  37 deg: both families stay on the surface, direction (-0.6018, 0.7986, 1.0)
  theta=  90 deg: both families stay on the surface, direction (-1.0, 0.0, 1.0)
  theta= 214 deg: both families stay on the surface, direction (0.5592, -0.829, 1.0)
  theta= 300 deg: both families stay on the surface, direction (0.866, 0.5, 1.0)
  largest deviation from x^2+y^2-z^2 = 1 over all points tested: 9.09e-13

  the two lines through one point are genuinely different:
    family +: (-0.601815, 0.798636, 1)
    family -: (0.601815, -0.798636, 1)

Block 4 - the saddle z = x^2 - y^2 at the origin
     step   along x-axis   along y-axis   diagonal x=y
      0.0         0.0000         0.0000         0.0000
      0.5         0.2500        -0.2500         0.0000
      1.0         1.0000        -1.0000         0.0000
      2.0         4.0000        -4.0000         0.0000
  minimum along x, maximum along y, and exactly level along x = y
  so the origin is stationary but is neither a max nor a min

Block 5 - why a paraboloid is used for dishes: parallel rays meet at the focus
  ray at x= 0.5 reflects to cross the axis at y = 2.000000000
  ray at x= 1.0 reflects to cross the axis at y = 2.000000000
  ray at x= 3.0 reflects to cross the axis at y = 2.000000000
  ray at x= 7.0 reflects to cross the axis at y = 2.000000000
  every one of them passes through the focus at y = 2.0

quadrics: passed
```

Block 3 is the claim that sounds false. Points generated along a perfectly straight line — equal steps, constant direction — satisfy the hyperboloid's equation to within $10^{-12}$, for both families and every angle tried.

## Common pitfalls and traps

- **Reading the surface off the equation without normalising first.** A quadric with cross terms like $xy$ is one of the standard forms *rotated*. Classify only after removing them — $z = xy$ looks unlike anything in the table but is a hyperbolic paraboloid.
- **Confusing the cone with the hyperboloids.** All three have signs $+\,+\,-$. What separates them is the right-hand side: $=1$ gives one sheet, $=0$ gives the cone, and $=-1$ (equivalently $+\,-\,-$ with $=1$) gives two sheets.
- **Assuming a curved surface cannot contain straight lines.** It can, and the practical consequences are large. "Curved" and "ruled" are independent properties.
- **Calling a saddle point a minimum because the gradient vanishes.** A vanishing gradient means *stationary*, not *minimal*. The second derivatives decide, and they must agree in sign across all directions.
- **Assuming every trace is non-empty.** For a two-sheet hyperboloid, whole families of planes miss the surface entirely — and that is the defining feature, not a failure of the method.
- **Forgetting that a dish must be a paraboloid, not a sphere.** A spherical mirror does not focus parallel rays to a point; it suffers spherical aberration. Only the parabola has the exact focusing property that block 5 verifies.

## Check your understanding

1. Identify $4x^2 + 9y^2 + z^2 = 36$.
2. Identify $z = x^2 + 4y^2$, and describe its $z = k$ traces for $k > 0$, $k = 0$ and $k < 0$.
3. Identify $x^2 - y^2 + z^2 = 1$. Careful — the minus is on the middle term.
4. Which quadric surfaces are doubly ruled?
5. Why is $z = x^2 - y^2$ level along the whole line $x = y$, and what does that say about the origin?

<details><summary>Answers — open only after an attempt</summary>

1. Divide by $36$: $\frac{x^2}{9} + \frac{y^2}{4} + \frac{z^2}{36} = 1$. All signs positive — an **ellipsoid**, with semi-axes $3$, $2$ and $6$.
2. Both squared terms positive — an **elliptic paraboloid**. For $k > 0$ the trace is the ellipse $x^2 + 4y^2 = k$; for $k = 0$ it is the single point at the origin; for $k < 0$ it is **empty**, since the surface never goes below $z = 0$.
3. Signs are $+\,-\,+$ with right-hand side $1$: one minus, so a **hyperboloid of one sheet** — but around the $y$-axis rather than the $z$-axis. Which variable carries the minus tells you the axis.
4. The **plane** (trivially), the **hyperboloid of one sheet**, and the **hyperbolic paraboloid**. Cones and cylinders are ruled but only singly.
5. Setting $y = x$ gives $z = x^2 - x^2 = 0$ for every $x$, so the surface contains that entire horizontal line — one of its ruling lines. It means the origin is not isolated in its flatness: there are directions in which the surface neither rises nor falls at all, which is a further reason the origin cannot be classified as a maximum or a minimum.

**And the prediction from section 4:** along the $x$-axis, $z = x^2$ **rises** — the origin is a minimum in that direction. Along the $y$-axis, $z = -y^2$ **falls** — a maximum there. So the origin is **neither**: it is a saddle point.
</details>

## Practice — independent task

Implement `classify_quadric(A, B, C, D)` for surfaces of the form $Ax^2 + By^2 + Cz^2 = D$, returning the surface name — then extend it.

1. Handle every row of section 3's table, plus the degenerate cases: a single point, the empty set, a plane pair, and a cylinder (one coefficient zero).
2. Normalise before classifying: divide through so $D \in \{1, 0, -1\}$, and note that multiplying the whole equation by $-1$ leaves the same surface. Your classifier must give the same answer for $x^2+y^2-z^2=1$ and $-x^2-y^2+z^2=-1$.
3. Verify each classification with the **method of traces**: for each surface, sample traces in all three directions and check the curve types match what the name predicts.
4. For each surface your classifier calls doubly ruled, **produce the lines**: return a function mapping a surface point to two direction vectors, and assert that points along both directions satisfy the equation to within `1e-12` over a wide range of the parameter.
5. Extend to $z = Ax^2 + By^2$ and classify the two paraboloids, including the degenerate $A = 0$ case.

**Edge cases:** all coefficients zero; $D = 0$ with all coefficients the same sign (a single point); one coefficient zero (a cylinder — say which axis); coefficients differing by less than your tolerance, where "circle" and "ellipse" become indistinguishable numerically.

**Done when:** every surface in section 3 is classified correctly under both sign conventions, your trace check agrees with your classifier on all of them, and your ruling lines stay on the surface to `1e-12` for $\lvert t\rvert$ up to at least $1000$.

## Tradeoffs, limits and extensions

**Classification by signs needs the cross terms gone.** A general quadric $Ax^2 + By^2 + Cz^2 + Dxy + Exz + Fyz + \ldots = 0$ must first be rotated into alignment. The rotation that does it is found by **diagonalising** the symmetric matrix of coefficients, and the resulting signs are its **eigenvalues**. So this classification is really a theorem about eigenvalues in disguise — see **eigenvalues** *(reserved)*.

**The same statement classifies stationary points.** For a function of several variables, the second-derivative matrix — the Hessian — is symmetric, and the signs of its eigenvalues say whether a stationary point is a minimum (all positive), a maximum (all negative) or a saddle (mixed). The quadric surfaces in this lesson are exactly the shapes a function looks like near a stationary point, which is why the saddle appears in both settings.

**Ruled does not mean developable.** A hyperboloid of one sheet is ruled but *cannot* be flattened without stretching — unlike a cylinder or cone, which are both. So the straight beams make it cheap to *build*, but the cladding between them still cannot be cut from flat sheet without distortion. This is the same developability question raised in [[02-solids|solids]] and [[01-latitude-and-longitude|latitude and longitude]].

## Before moving on

You are done with this lesson when you can:

- Name any quadric from the signs of its coefficients and the right-hand side.
- Identify a surface by taking traces, and interpret an empty trace.
- Explain what doubly ruled means and why cooling towers exploit it.
- Recognise a saddle and say why a vanishing gradient does not make it a minimum.

**Recap for later lookup:** with $=1$, no minus signs gives an **ellipsoid**, one gives a **hyperboloid of one sheet**, two gives a **hyperboloid of two sheets**; the same signs with $=0$ give a **cone**. $z = x^2 + y^2$ is an **elliptic paraboloid** (a dish, which focuses parallel rays exactly); $z = x^2 - y^2$ is a **hyperbolic paraboloid** (a saddle). The plane, the one-sheet hyperboloid and the hyperbolic paraboloid are the only **doubly ruled** surfaces.

**Where next:** this is the last lesson in geometry and trigonometry. The natural continuations are **eigenvalues** *(reserved)*, which explain the classification, and [[06-calculus/04-calculus-3/03-optimization|multivariable optimisation]], where saddle points become the central difficulty.

## Related

- [[01-lines-and-planes|Lines and Planes in Space]] — the vector machinery the ruling lines are written in
- [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — the conic sections these surfaces generalise
- [[02-solids|Solids]] — the slicing idea the method of traces borrows
- **Eigenvalues** *(reserved)* — where the classification is properly explained
