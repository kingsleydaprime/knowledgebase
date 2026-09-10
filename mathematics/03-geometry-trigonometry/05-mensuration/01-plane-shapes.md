# Mensuration: Plane Shapes

**[Beginner]** — where the area formulas come from, and how Archimedes computed $\pi$ without knowing what $\pi$ was.

## Before you start

- You know the polygon angle sums, and that a regular polygon approaches a circle — [[02-triangles-and-polygons|triangles and polygons]].
- You can use $\tfrac12 ab\sin C$ for a triangle's area — [[03-sine-and-cosine-rules|sine and cosine rules]].
- You know radians — [[02-graphs-and-identities|graphs and identities]].

**What you will be able to do after this lesson:**

1. Derive the area of a parallelogram, triangle and trapezium by rearrangement, rather than recall them.
2. Derive the circle's area and circumference as the **limit of inscribed polygons**, and bracket $\pi$ between two computable bounds.
3. Compute arc length, sector area and segment area, in degrees or radians, and say why radians make them simpler.
4. Break a composite shape into pieces and account for every part.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 2 reproduces Archimedes' calculation.

---

## 1. Why this exists

Area is what you pay for. Land is sold by it, paint and fabric and roofing are bought by it, and a wrong figure costs money in a way a wrong angle usually does not.

But there is a deeper reason these formulas are worth deriving rather than memorising. Area for straight-sided shapes is a matter of **rearrangement** — cut a shape up, reassemble it as a rectangle, and the area cannot have changed. Area for a *curved* shape is not, because no finite rearrangement turns a circle into a rectangle. Getting from one to the other requires a limit, and that limit is the first genuinely infinite argument in elementary mathematics. It is the beginning of integral calculus, two thousand years early.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Perimeter** | The distance all the way round | For a circle it has its own name: circumference |
| **Area** | The amount of surface enclosed | Measured in square units, always |
| **Perpendicular height** | The height measured at right angles to the chosen base | **Not** the slanted side |
| **Arc** | Part of the circumference | Length $r\theta$ in radians |
| **Sector** | Region bounded by two radii and an arc | A pizza slice |
| **Segment** | Region bounded by a chord and an arc | Sector minus triangle |
| **Composite shape** | A shape made by joining or removing simpler ones | Add or subtract the parts |

## 3. Straight-sided shapes, by rearrangement

**Rectangle.** $A = bh$. This is the definition of area — how many unit squares fit — rather than a result.

**Parallelogram.** Cut off the triangle at one end and slide it to the other. The result is a rectangle of the same base and the same perpendicular height:

```
     ____________              ____________
    /|          /             |            |
   / |         /       =>     |            |
  /__|________/               |____________|
     b                              b
```

$$
A = bh
$$

with $h$ the **perpendicular** height, not the slanted side. This is the single most common error in the topic.

**Triangle.** Two copies of a triangle fit together into a parallelogram of the same base and height, so a triangle is half of it:

$$
A = \tfrac12 bh
$$

And when the height is not given but two sides and their included angle are, $h = a\sin C$ gives the form from [[03-sine-and-cosine-rules|the sine rule lesson]]: $A = \tfrac12 ab\sin C$.

**Trapezium.** Two copies fit together into a parallelogram whose base is $a + b$, the sum of the two parallel sides:

$$
A = \tfrac12 (a + b) h
$$

Read it as "the average of the parallel sides, times the height" — which also explains why a trapezium with $a = b$ reduces to the parallelogram formula.

## 4. The circle, by exhaustion

No rearrangement turns a circle into a rectangle. So instead: **approximate it by polygons and let the number of sides grow.**

Inscribe a regular $n$-gon in a circle of radius $r$. Split it into $n$ identical triangles meeting at the centre, each with two sides of length $r$ and an apex angle of $\frac{2\pi}{n}$. By the area formula $\tfrac12 ab\sin C$:

$$
A_n = n \cdot \tfrac12 r^2 \sin\!\frac{2\pi}{n}
$$

Now let $n \to \infty$. Writing $\theta = \frac{2\pi}{n}$, so $n = \frac{2\pi}{\theta}$:

$$
A_n = \frac{2\pi}{\theta}\cdot\tfrac12 r^2\sin\theta = \pi r^2 \cdot \frac{\sin\theta}{\theta}
$$

And $\frac{\sin\theta}{\theta} \to 1$ as $\theta \to 0$ — the fundamental limit of trigonometry, and the reason radians are the right unit. So:

$$
A = \pi r^2
$$

The perimeter argument runs the same way. Each side of the inscribed $n$-gon has length $2r\sin\frac{\pi}{n}$, so the perimeter is $2nr\sin\frac{\pi}{n} \to 2\pi r$.

**Bracketing $\pi$.** The inscribed polygon under-estimates and a **circumscribed** one over-estimates. Taking $r = 1$, so that both the area and the semi-perimeter of the circle equal $\pi$, there are two brackets available:

$$
\underbrace{n\,\tfrac12\sin\!\frac{2\pi}{n}}_{\text{inscribed area}} \;<\; \pi \;<\; \underbrace{n\tan\frac{\pi}{n}}_{\text{circumscribed area}}
$$
$$
\underbrace{n\sin\frac{\pi}{n}}_{\text{inscribed semi-perimeter}} \;<\; \pi \;<\; \underbrace{n\tan\frac{\pi}{n}}_{\text{circumscribed semi-perimeter}}
$$

The upper bounds coincide, because a circumscribed polygon's area is half its perimeter times its apothem, and the apothem *is* $r$. The **perimeter** lower bound is the tighter of the two, and it is the one Archimedes used: running it by hand up to a $96$-sided polygon he obtained $3\tfrac{10}{71} < \pi < 3\tfrac17$, that is $3.140845 < \pi < 3.142857$. Block 2 of the lab reproduces both brackets and shows the difference.

> [!TIP]
> **Predict before running the lab.** The two bounds close in on $\pi$ from either side. If doubling $n$ from $6$ to $12$ roughly quarters the gap, how many doublings would you need to pin $\pi$ down to ten decimal places? Estimate before opening the answers.

## 5. Arcs, sectors and segments

A sector is a fraction of the circle — the fraction being the angle over a full turn.

| Quantity | In degrees | In radians |
| :--- | :--- | :--- |
| Arc length | $\dfrac{\theta}{360}\times 2\pi r$ | $r\theta$ |
| Sector area | $\dfrac{\theta}{360}\times \pi r^2$ | $\tfrac12 r^2\theta$ |

The radian forms have no conversion constants. That is not a coincidence: a radian is *defined* as the angle whose arc equals the radius, so $\text{arc} = r\theta$ is the definition rearranged.

**Segment.** The region between a chord and its arc is what is left when the triangle is removed from the sector:

$$
\text{segment} = \underbrace{\tfrac12 r^2\theta}_{\text{sector}} - \underbrace{\tfrac12 r^2\sin\theta}_{\text{triangle}} = \tfrac12 r^2(\theta - \sin\theta)
$$

The triangle's area uses $\tfrac12 ab\sin C$ with both sides equal to $r$. And notice: the formula is positive exactly because $\theta > \sin\theta$ for $\theta > 0$ — the same inequality that made $\frac{\sin\theta}{\theta} \to 1$ approach from below.

## Worked example — runnable

**Runnable example:** save as `plane_shapes.py` in any empty directory and run `python3 plane_shapes.py`. Standard library only; writes no files.

```python
"""Areas by rearrangement, the circle by exhaustion, and sectors."""
import math

EPS = 1e-9


def triangle_area_base_height(b, h):
    return 0.5 * b * h


def triangle_area_two_sides(a, b, included_deg):
    return 0.5 * a * b * math.sin(math.radians(included_deg))


def trapezium_area(a, b, h):
    return 0.5 * (a + b) * h


def inscribed_polygon_area(n, r=1.0):
    """n triangles, each with apex angle 2pi/n and two sides r."""
    return n * 0.5 * r * r * math.sin(2 * math.pi / n)


def circumscribed_polygon_area(n, r=1.0):
    return n * r * r * math.tan(math.pi / n)


def inscribed_polygon_perimeter(n, r=1.0):
    return 2 * n * r * math.sin(math.pi / n)


def sector_area(r, theta_rad):
    return 0.5 * r * r * theta_rad


def segment_area(r, theta_rad):
    return 0.5 * r * r * (theta_rad - math.sin(theta_rad))


if __name__ == "__main__":
    print("Block 1 - the straight-sided formulas agree with each other")
    # A triangle with sides 5 and 8 at 30 degrees has height 8*sin30 = 4 on base 5
    by_sides = triangle_area_two_sides(5, 8, 30)
    by_base = triangle_area_base_height(5, 8 * math.sin(math.radians(30)))
    print(f"  triangle: 1/2 ab sinC = {by_sides:.6f}, 1/2 bh = {by_base:.6f}")
    assert abs(by_sides - by_base) < EPS
    # a trapezium with equal parallel sides IS a parallelogram
    print(f"  trapezium with a = b = 7, h = 3: {trapezium_area(7, 7, 3):.6f}")
    print(f"  parallelogram  b = 7, h = 3:     {7 * 3:.6f}")
    assert abs(trapezium_area(7, 7, 3) - 21) < EPS

    print()
    print("Block 2 - Archimedes: bracketing pi with polygons (r = 1)")
    print("      n   area bound    semi-perimeter   upper bound       gap")
    n = 6
    for _ in range(9):
        lo_area = inscribed_polygon_area(n)
        lo_perim = inscribed_polygon_perimeter(n) / 2
        hi = circumscribed_polygon_area(n)     # equals the semi-perimeter bound
        print(f"  {n:5}  {lo_area:.10f}   {lo_perim:.10f}  {hi:.10f}  {hi - lo_perim:.3e}")
        assert lo_area < math.pi < hi, n
        assert lo_perim < math.pi < hi, n
        assert lo_perim > lo_area, "the perimeter bound is the tighter one"
        n *= 2

    lo96 = inscribed_polygon_perimeter(96) / 2
    hi96 = circumscribed_polygon_area(96)
    print(f"  Archimedes stopped at n = 96: {lo96:.6f} < pi < {hi96:.6f}")
    print(f"    his published bounds, 223/71 and 22/7: "
          f"{223/71:.6f} < pi < {22/7:.6f}")
    assert 223 / 71 < lo96 < math.pi < hi96 < 22 / 7
    print("    his bounds bracket the polygon bounds, as rounding by hand requires")
    print(f"  the inscribed AREA at n = 96 is only {inscribed_polygon_area(96):.6f}"
          " - a weaker bound")

    print()
    print("  the gap shrinks by a factor of about 4 per doubling:")
    prev = None
    for n in (6, 12, 24, 48, 96, 192):
        gap = circumscribed_polygon_area(n) - inscribed_polygon_perimeter(n) / 2
        ratio = "" if prev is None else f"  ratio {prev / gap:.4f}"
        print(f"    n={n:4}: gap {gap:.3e}{ratio}")
        prev = gap

    print()
    print("Block 3 - perimeter converges to 2 pi r as well")
    for n in (6, 60, 600, 6000):
        p = inscribed_polygon_perimeter(n)
        print(f"  n={n:5}: perimeter {p:.10f}   2*pi = {2*math.pi:.10f}")
        assert p < 2 * math.pi
    assert abs(inscribed_polygon_perimeter(100000) - 2 * math.pi) < 1e-8

    print()
    print("Block 4 - sectors and segments")
    R = 10.0
    for deg in (30, 90, 180, 360):
        th = math.radians(deg)
        print(f"  {deg:3} deg: arc {R*th:8.4f}  sector {sector_area(R, th):9.4f}"
              f"  segment {segment_area(R, th):9.4f}")
    # a full turn must give the whole circle
    assert abs(sector_area(R, 2 * math.pi) - math.pi * R * R) < EPS
    assert abs(R * 2 * math.pi - 2 * math.pi * R) < EPS
    # a semicircular segment is exactly half the circle
    assert abs(segment_area(R, math.pi) - 0.5 * math.pi * R * R) < EPS
    print("  a 360 degree sector is the whole circle; a 180 degree segment is half of it")

    print()
    print("Block 5 - a composite shape, accounted for piece by piece")
    # A running track: a rectangle with a semicircle on each end.
    # IAAF dimensions: 84.39 m straights, kerb radius 36.50 m.
    STRAIGHT, KERB_RADIUS = 84.39, 36.50
    infield = STRAIGHT * (2 * KERB_RADIUS) + math.pi * KERB_RADIUS ** 2
    kerb_length = 2 * STRAIGHT + 2 * math.pi * KERB_RADIUS
    print(f"  rectangle {STRAIGHT} x {2*KERB_RADIUS}: "
          f"area {STRAIGHT * 2 * KERB_RADIUS:.4f} m^2")
    print(f"  two semicircular ends (radius {KERB_RADIUS}) = one circle: "
          f"area {math.pi * KERB_RADIUS ** 2:.4f} m^2")
    print(f"  total enclosed area {infield:.4f} m^2")
    print(f"  length along the kerb itself: {kerb_length:.4f} m - NOT 400")

    # The race distance is measured along a line 30 cm outside the kerb,
    # because that is where a runner's centre of mass actually travels.
    RUN_RADIUS = KERB_RADIUS + 0.30
    running_line = 2 * STRAIGHT + 2 * math.pi * RUN_RADIUS
    print(f"  measured 0.30 m out (radius {RUN_RADIUS}): {running_line:.4f} m")
    assert abs(running_line - 400) < 0.01, running_line
    print("  the 30 cm offset is worth 1.88 m - the whole discrepancy")
    assert abs((running_line - kerb_length) - 2 * math.pi * 0.30) < EPS

    print()
    print("plane_shapes: passed")
```

Expected output:

```
Block 1 - the straight-sided formulas agree with each other
  triangle: 1/2 ab sinC = 10.000000, 1/2 bh = 10.000000
  trapezium with a = b = 7, h = 3: 21.000000
  parallelogram  b = 7, h = 3:     21.000000

Block 2 - Archimedes: bracketing pi with polygons (r = 1)
      n   area bound    semi-perimeter   upper bound       gap
      6  2.5980762114   3.0000000000  3.4641016151  4.641e-01
     12  3.0000000000   3.1058285412  3.2153903092  1.096e-01
     24  3.1058285412   3.1326286133  3.1596599421  2.703e-02
     48  3.1326286133   3.1393502030  3.1460862151  6.736e-03
     96  3.1393502030   3.1410319509  3.1427145996  1.683e-03
    192  3.1410319509   3.1414524723  3.1418730500  4.206e-04
    384  3.1414524723   3.1415576079  3.1416627471  1.051e-04
    768  3.1415576079   3.1415838921  3.1416101766  2.628e-05
   1536  3.1415838921   3.1415904632  3.1415970343  6.571e-06
  Archimedes stopped at n = 96: 3.141032 < pi < 3.142715
    his published bounds, 223/71 and 22/7: 3.140845 < pi < 3.142857
    his bounds bracket the polygon bounds, as rounding by hand requires
  the inscribed AREA at n = 96 is only 3.139350 - a weaker bound

  the gap shrinks by a factor of about 4 per doubling:
    n=   6: gap 4.641e-01
    n=  12: gap 1.096e-01  ratio 4.2360
    n=  24: gap 2.703e-02  ratio 4.0531
    n=  48: gap 6.736e-03  ratio 4.0130
    n=  96: gap 1.683e-03  ratio 4.0032
    n= 192: gap 4.206e-04  ratio 4.0008

Block 3 - perimeter converges to 2 pi r as well
  n=    6: perimeter 6.0000000000   2*pi = 6.2831853072
  n=   60: perimeter 6.2803147492   2*pi = 6.2831853072
  n=  600: perimeter 6.2831565977   2*pi = 6.2831853072
  n= 6000: perimeter 6.2831850201   2*pi = 6.2831853072

Block 4 - sectors and segments
   30 deg: arc   5.2360  sector   26.1799  segment    1.1799
   90 deg: arc  15.7080  sector   78.5398  segment   28.5398
  180 deg: arc  31.4159  sector  157.0796  segment  157.0796
  360 deg: arc  62.8319  sector  314.1593  segment  314.1593
  a 360 degree sector is the whole circle; a 180 degree segment is half of it

Block 5 - a composite shape, accounted for piece by piece
  rectangle 84.39 x 73.0: area 6160.4700 m^2
  two semicircular ends (radius 36.5) = one circle: area 4185.3868 m^2
  total enclosed area 10345.8568 m^2
  length along the kerb itself: 398.1163 m - NOT 400
  measured 0.30 m out (radius 36.8): 400.0012 m
  the 30 cm offset is worth 1.88 m - the whole discrepancy

plane_shapes: passed
```

Block 2 is the lesson in miniature. The bounds are computable, they provably straddle $\pi$, and they converge — which is what makes this a *derivation* of the circle's area rather than a measurement of it.

## Common pitfalls and traps

- **Using a slanted side as the height.** In a parallelogram, trapezium or triangle, $h$ is the **perpendicular** distance between the parallel sides. The slanted side is longer and gives a wrong, too-large answer.
- **Mixing degrees and radians in sector formulas.** $\tfrac12 r^2\theta$ requires radians. With degrees you need the $\frac{\theta}{360}$ version. Substituting $90$ into the radian formula gives an answer about $57$ times too big.
- **Confusing sector and segment.** The sector includes the triangle; the segment does not. Segment $=$ sector $-$ triangle.
- **Forgetting that area units are squared.** Doubling every length multiplies area by $4$, not $2$ — a scaling fact worth internalising, because it also explains why the polygon gap shrinks by $4$ per doubling.
- **Adding curved and straight perimeters carelessly in composite shapes.** When two shapes are joined, the shared edge is *inside* the composite and must not be counted in the perimeter — though it still counts fully in the area.
- **Treating $\pi r^2$ as a definition.** It is a theorem, and the limit argument is what proves it. The lab's block 2 is that argument made computational.

## Check your understanding

1. A parallelogram has base $12$ cm and slant side $8$ cm, with the slant at $30°$ to the base. Find its area.
2. A trapezium has parallel sides $9$ and $15$, and height $6$. Find its area.
3. A sector of a circle of radius $6$ has angle $\frac{\pi}{3}$. Find its arc length, sector area and segment area.
4. Why does the inscribed polygon **under**-estimate and the circumscribed one **over**-estimate?
5. A circular pond of radius $5$ m is surrounded by a path $1$ m wide. Find the path's area.

<details><summary>Answers — open only after an attempt</summary>

1. The perpendicular height is $8\sin 30° = 4$ cm, **not** $8$. Area $= 12 \times 4 = 48$ cm².
2. $A = \tfrac12(9 + 15)\times 6 = \tfrac12 \times 24 \times 6 = 72$.
3. Arc $= r\theta = 6 \times \frac{\pi}{3} = 2\pi \approx 6.283$. Sector $= \tfrac12(36)\frac{\pi}{3} = 6\pi \approx 18.850$. Segment $= \tfrac12(36)\left(\frac{\pi}{3} - \sin\frac{\pi}{3}\right) = 18\left(1.0472 - 0.8660\right) \approx 3.261$.
4. The inscribed polygon lies entirely **inside** the circle — its sides are chords, which cut off segments the polygon misses. The circumscribed polygon lies entirely **outside**, its sides being tangents, so it includes area the circle does not. Hence one is a strict lower bound and the other a strict upper bound.
5. The path is an annulus: outer radius $6$, inner radius $5$. Area $= \pi(6^2 - 5^2) = \pi(36 - 25) = 11\pi \approx 34.56$ m².

**And the prediction from section 4:** the gap falls by a factor of about $4$ per doubling, so each doubling wins roughly $\log_{10} 4 \approx 0.6$ of a decimal place. Going from the $n = 6$ gap of about $0.9$ to $10^{-10}$ needs a reduction of about $10^{10}$, so roughly $\log_4(10^{10}) \approx 17$ doublings — an $n$ of around $800{,}000$. The lab's ratio column shows the factor of $4$ directly. This is why nobody computes $\pi$ this way any more.
</details>

## Practice — independent task

Implement `polygon_area(vertices)` using the **shoelace formula**, and use it to check everything above.

$$
A = \tfrac12\left\lvert \sum_{i=0}^{n-1}\left(x_i y_{i+1} - x_{i+1} y_i\right) \right\rvert
$$

1. Implement it for any simple polygon given as a list of vertices, with indices wrapping at the end.
2. Verify against the formulas in this lesson: build a rectangle, a triangle, a parallelogram and a trapezium from coordinates and check the shoelace area matches each closed form to within `1e-9`.
3. **Drop the absolute value** and report the sign. Determine experimentally what the sign tells you, and state it in a comment.
4. Use it to reproduce block 2: generate the vertices of a regular $n$-gon on the unit circle and confirm the shoelace area matches $\tfrac12 n\sin\frac{2\pi}{n}$.
5. Test a **non-convex** polygon — an L-shape or a star — and confirm it still works. Then test a **self-intersecting** one (a figure-eight) and report what you get. Explain why that result is what it is.

**Edge cases:** fewer than three vertices; three collinear vertices; a polygon listed clockwise versus anticlockwise; a repeated vertex.

**Done when:** all four closed forms are reproduced, you can state what the sign means and why the figure-eight behaves as it does, and your $n$-gon check matches to `1e-9` for at least five values of $n$.

## Tradeoffs, limits and extensions

**This is integral calculus in disguise.** "Approximate by simple pieces, refine, take a limit" is exactly the Riemann integral. The circle was done here with triangles because they are the pieces available without calculus; a formal treatment uses rectangles and reaches the same answer. Anyone who has followed section 4 has already met the central idea of [[06-calculus/03-calculus-2/03-applications|integration]].

**The limit is the hard part, historically.** Greek mathematicians would not write "$n \to \infty$" — the method of exhaustion instead proves that the area *cannot* be greater and *cannot* be less, so it must be equal. That is rigorous, and it avoids committing to what infinity means. Making the limit itself respectable took until the nineteenth century, in [[05-precise-definition/01-epsilon-delta|the epsilon-delta definition]].

**Precision in practice.** For land measurement the shoelace formula on surveyed coordinates is what is actually used, and its accuracy is set by the coordinates, not the formula. On a large enough parcel the Earth's curvature matters and a plane formula is simply wrong — see [[01-latitude-and-longitude|latitude and longitude]].

## Before moving on

You are done with this lesson when you can:

- Derive the parallelogram, triangle and trapezium areas by rearrangement.
- Derive $\pi r^2$ as a polygon limit and explain why $\frac{\sin\theta}{\theta}\to1$ is the step that does the work.
- Compute arcs, sectors and segments in either angle unit.
- Explain why the inscribed and circumscribed polygons bracket the answer.

**Recap for later lookup:** rectangle $bh$; parallelogram $bh$ with **perpendicular** $h$; triangle $\tfrac12 bh = \tfrac12 ab\sin C$; trapezium $\tfrac12(a+b)h$; circle $\pi r^2$ and $2\pi r$; arc $r\theta$; sector $\tfrac12 r^2\theta$; segment $\tfrac12 r^2(\theta - \sin\theta)$ — the last three in **radians**.

**Next:** [[02-solids|Mensuration: Solids]] — the same limiting idea applied one dimension up, where it delivers the cone and the sphere.

## Related

- [[02-triangles-and-polygons|Triangles and Polygons]] — where the polygon-to-circle prediction was made
- [[03-sine-and-cosine-rules|Sine and Cosine Rules]] — the $\tfrac12 ab\sin C$ the derivation depends on
- [[01-circle-theorems|Circle Theorems]] — chords and segments, by argument rather than area
