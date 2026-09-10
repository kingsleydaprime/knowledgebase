# Mensuration: Solids

**[Intermediate]** — surface area and volume, and the one principle that delivers the cone and the sphere without calculus.

## Before you start

- You can find the area of plane shapes, including sectors — [[01-plane-shapes|plane shapes]].
- You met the limiting argument that gave $\pi r^2$ — same lesson, section 4.
- You know Pythagoras, for slant heights — [[02-triangles-and-polygons|triangles and polygons]].

**What you will be able to do after this lesson:**

1. State **Cavalieri's principle** and use it to derive the volume of a sphere from a cylinder and a cone.
2. Derive the curved surface area of a cone by unrolling it into a sector.
3. Compute surface area and volume for prisms, cylinders, cones, pyramids and spheres, and choose the right one for a composite solid.
4. Apply the **scaling laws** — length, area and volume scale as $k$, $k^2$, $k^3$ — and explain a physical consequence.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 1 is the derivation that matters.

---

## 1. Why this exists

A cylindrical water tank is to be built. Its **volume** determines what it holds and what you are paid for; its **surface area** determines how much steel it costs and how fast it loses heat. These are different numbers with different units, and they do not scale together — which is the point of section 5 and the reason large animals are not simply scaled-up small ones.

There is also a mathematical reason. Areas of straight-sided plane shapes came from rearrangement. Volumes of straight-sided solids do **not** always: no finite cutting turns a regular tetrahedron into a cube of equal volume. That was Hilbert's third problem, settled by Dehn in 1900 — the year it was posed. So even the pyramid's volume needs a limiting argument, and the sphere certainly does.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Prism** | A solid with the same cross-section all the way along | A cylinder is a prism with a circular cross-section |
| **Cross-section** | The shape you get by slicing | Constant for a prism, shrinking for a cone |
| **Perpendicular height** | Height measured at right angles to the base | Not the slant |
| **Slant height** ($l$) | Distance from apex to base edge along the surface | For a cone, $l = \sqrt{r^2 + h^2}$ |
| **Curved surface area** | The area of the curved part only | Excludes the flat base(s) |
| **Total surface area** | Everything, including bases | Say which you mean |
| **Cavalieri's principle** | Solids with equal cross-sectional areas at every height have equal volume | The workhorse of this lesson |

## 3. Prisms and cylinders

For any solid with a constant cross-section of area $A$ and perpendicular height $h$:

$$
V = Ah
$$

For a cylinder, $A = \pi r^2$, so $V = \pi r^2 h$.

**Curved surface of a cylinder — by unrolling.** Cut the cylinder down its side and flatten it. You get a **rectangle** whose width is the base circumference and whose height is $h$:

$$
\text{curved surface} = 2\pi r h, \qquad \text{total} = 2\pi r h + 2\pi r^2
$$

Unrolling is the key move, and it works because a cylinder is *developable* — it can be flattened without stretching. Section 4 uses it again for the cone. A sphere is **not** developable, which is exactly why every flat map of the Earth distorts something.

## 4. Cavalieri's principle, and the cone and sphere

> **Cavalieri's principle.** If two solids have the same height, and at every level their cross-sections have equal area, then they have equal volume.

The intuition is a stack of coins: shear the stack sideways and it still contains the same amount of metal, because no slice changed size.

### The cone

$$
V = \tfrac13 \pi r^2 h
$$

The $\tfrac13$ can be seen directly: a cube can be dissected into **three** identical square-based pyramids, each with the cube's base and height. So each is a third of the cube — and Cavalieri then extends the result from that special pyramid to every pyramid and cone of the same base area and height, because their cross-sections match level by level.

The cross-section of a cone at height $y$ is a circle of radius $r\left(1 - \frac{y}{h}\right)$, shrinking linearly, so its area falls as the **square** of the remaining height. That is why the answer is $\tfrac13$ rather than $\tfrac12$.

**Curved surface of a cone — by unrolling.** Cut along a slant line and flatten. You get a **sector** of a circle of radius $l$ (the slant height), whose arc is the base circumference $2\pi r$. Using sector area $=\tfrac12 \times \text{arc} \times \text{radius}$:

$$
\text{curved surface} = \tfrac12 (2\pi r)(l) = \pi r l, \qquad \text{total} = \pi r l + \pi r^2
$$

with $l = \sqrt{r^2 + h^2}$ by Pythagoras.

### The sphere — Archimedes' argument

Take a hemisphere of radius $r$. Alongside it, take a cylinder of radius $r$ and height $r$, with a **cone** of the same radius and height removed from it, apex down.

Slice both at height $y$ above the base:

- **Hemisphere:** the slice is a circle. By Pythagoras its radius is $\sqrt{r^2 - y^2}$, so its area is $\pi(r^2 - y^2)$.
- **Cylinder minus cone:** the cylinder's slice is a circle of radius $r$, area $\pi r^2$. The cone's slice at height $y$ has radius $y$, area $\pi y^2$. The remaining ring has area $\pi r^2 - \pi y^2 = \pi(r^2 - y^2)$.

**Identical, at every height.** So by Cavalieri the two solids have the same volume:

$$
V_{\text{hemisphere}} = \underbrace{\pi r^2 \cdot r}_{\text{cylinder}} - \underbrace{\tfrac13 \pi r^2 \cdot r}_{\text{cone}} = \tfrac23 \pi r^3
$$

and therefore:

$$
V_{\text{sphere}} = \tfrac43 \pi r^3
$$

No calculus, and no measurement — just one principle and a Pythagorean slice. Block 1 of the lab checks the equality height by height.

**Surface area of a sphere:** $A = 4\pi r^2$, which Archimedes also proved. It is exactly the curved surface of the circumscribing cylinder ($2\pi r \times 2r$), a coincidence striking enough that he asked for a sphere inscribed in a cylinder to be carved on his tombstone.

> [!TIP]
> **Predict before running the lab.** A sphere sits snugly inside a cylinder of the same radius and height $2r$. What fraction of the cylinder's volume does the sphere occupy? And what fraction of its **total** surface area? Work both out before opening the answers.

## 5. The scaling laws

Scale every length of a solid by a factor $k$:

| Quantity | Scales as | Example: $k = 2$ |
| :--- | :--- | :--- |
| Length | $k$ | doubles |
| Area | $k^2$ | $\times 4$ |
| Volume | $k^3$ | $\times 8$ |

Because area and volume scale differently, the **ratio** of surface area to volume falls as $1/k$. A large object has proportionally less surface than a small one.

That single fact explains a great deal: why a mouse must eat constantly and an elephant need not (heat is lost through surface, generated through volume); why fine gravel dissolves faster than a boulder; why cells are microscopic; and why a scaled-up insect could not breathe, since gas exchange is a surface process supporting a volume of tissue.

## Worked example — runnable

**Runnable example:** save as `solids.py` in any empty directory and run `python3 solids.py`. Standard library only; writes no files.

```python
"""Volumes and surface areas, including Cavalieri's derivation of the sphere."""
import math

EPS = 1e-9


def cylinder_volume(r, h):
    return math.pi * r * r * h


def cone_volume(r, h):
    return math.pi * r * r * h / 3


def sphere_volume(r):
    return 4 * math.pi * r ** 3 / 3


def cone_slant(r, h):
    return math.hypot(r, h)


def cone_curved_area(r, h):
    return math.pi * r * cone_slant(r, h)


def sphere_area(r):
    return 4 * math.pi * r * r


def slice_area_hemisphere(r, y):
    """Cross-section of a hemisphere at height y: a circle of radius sqrt(r^2-y^2)."""
    return math.pi * (r * r - y * y)


def slice_area_cylinder_minus_cone(r, y):
    """Cross-section of (cylinder radius r, height r) with a cone removed."""
    return math.pi * r * r - math.pi * y * y


def volume_by_slicing(area_at_height, lo, hi, n=200000):
    """Riemann midpoint sum of cross-sectional areas - Cavalieri, numerically."""
    dy = (hi - lo) / n
    return sum(area_at_height(lo + (i + 0.5) * dy) for i in range(n)) * dy


if __name__ == "__main__":
    R = 3.0

    print("Block 1 - Cavalieri: hemisphere vs (cylinder minus cone), slice by slice")
    print("      y    hemisphere   cyl - cone    difference")
    for i in range(6):
        y = R * i / 5
        a1 = slice_area_hemisphere(R, y)
        a2 = slice_area_cylinder_minus_cone(R, y)
        print(f"  {y:5.2f}  {a1:11.6f}  {a1:11.6f}  {a1 - a2:.1e}")
        assert abs(a1 - a2) < EPS
    print("  equal at every height, so the two solids have equal volume")

    hemi = cylinder_volume(R, R) - cone_volume(R, R)
    print(f"  cylinder(r={R}, h={R}) - cone(r={R}, h={R}) = {hemi:.6f}")
    print(f"  2/3 pi r^3                                  = {2*math.pi*R**3/3:.6f}")
    print(f"  so the whole sphere is                       {2*hemi:.6f}")
    print(f"  and 4/3 pi r^3 is                            {sphere_volume(R):.6f}")
    assert abs(2 * hemi - sphere_volume(R)) < EPS

    print()
    print("Block 2 - the same volumes by numerical slicing")
    hemi_numeric = volume_by_slicing(lambda y: slice_area_hemisphere(R, y), 0, R)
    print(f"  hemisphere by Riemann sum = {hemi_numeric:.6f}")
    print(f"  closed form               = {sphere_volume(R)/2:.6f}")
    assert abs(hemi_numeric - sphere_volume(R) / 2) < 1e-6
    cone_numeric = volume_by_slicing(
        lambda y: math.pi * (R * (1 - y / 6.0)) ** 2, 0, 6.0)
    print(f"  cone (r={R}, h=6) by Riemann sum = {cone_numeric:.6f}")
    print(f"  1/3 pi r^2 h                     = {cone_volume(R, 6.0):.6f}")
    assert abs(cone_numeric - cone_volume(R, 6.0)) < 1e-6

    print()
    print("Block 3 - unrolling a cone gives a sector")
    H = 4.0
    l = cone_slant(R, H)
    base_circumference = 2 * math.pi * R
    sector_angle = base_circumference / l           # radians: arc = radius * angle
    sector_area = 0.5 * l * l * sector_angle        # 1/2 r^2 theta
    print(f"  r={R}, h={H} -> slant l = {l:.6f}")
    print(f"  unrolled: a sector of radius {l:.4f}, arc {base_circumference:.6f}")
    print(f"  sector angle {sector_angle:.6f} rad ({math.degrees(sector_angle):.4f} deg)")
    print(f"  sector area  {sector_area:.6f}   pi r l = {cone_curved_area(R, H):.6f}")
    assert abs(sector_area - cone_curved_area(R, H)) < EPS
    assert sector_angle < 2 * math.pi, "the sector never closes into a full circle"

    print()
    print("Block 4 - Archimedes' tombstone: sphere inside its snug cylinder")
    cyl_v = cylinder_volume(R, 2 * R)
    cyl_total_area = 2 * math.pi * R * (2 * R) + 2 * math.pi * R * R
    print(f"  sphere volume {sphere_volume(R):.6f},  cylinder volume {cyl_v:.6f}")
    print(f"  ratio = {sphere_volume(R) / cyl_v:.10f}")
    print(f"  sphere area   {sphere_area(R):.6f},  cylinder total area {cyl_total_area:.6f}")
    print(f"  ratio = {sphere_area(R) / cyl_total_area:.10f}")
    assert abs(sphere_volume(R) / cyl_v - 2 / 3) < EPS
    assert abs(sphere_area(R) / cyl_total_area - 2 / 3) < EPS
    print("  both ratios are exactly 2/3 - which is what he wanted on his grave")
    # the curved part of the cylinder alone equals the sphere's whole surface
    assert abs(2 * math.pi * R * (2 * R) - sphere_area(R)) < EPS

    print()
    print("Block 5 - scaling: length k, area k^2, volume k^3")
    print("      k    volume x    area x    area/volume x")
    base_v, base_a = sphere_volume(1.0), sphere_area(1.0)
    for k in (1, 2, 3, 10):
        v, a = sphere_volume(k), sphere_area(k)
        print(f"  {k:5}  {v/base_v:9.1f}  {a/base_a:8.1f}  {(a/v)/(base_a/base_v):13.4f}")
        assert abs(v / base_v - k ** 3) < 1e-6
        assert abs(a / base_a - k ** 2) < 1e-6
    print("  surface-to-volume falls as 1/k: big things have proportionally less skin")

    print()
    print("solids: passed")
```

Expected output:

```
Block 1 - Cavalieri: hemisphere vs (cylinder minus cone), slice by slice
      y    hemisphere   cyl - cone    difference
   0.00    28.274334    28.274334  0.0e+00
   0.60    27.143361    27.143361  3.6e-15
   1.20    23.750440    23.750440  0.0e+00
   1.80    18.095574    18.095574  3.6e-15
   2.40    10.178760    10.178760  1.8e-15
   3.00     0.000000     0.000000  0.0e+00
  equal at every height, so the two solids have equal volume
  cylinder(r=3.0, h=3.0) - cone(r=3.0, h=3.0) = 56.548668
  2/3 pi r^3                                  = 56.548668
  so the whole sphere is                       113.097336
  and 4/3 pi r^3 is                            113.097336

Block 2 - the same volumes by numerical slicing
  hemisphere by Riemann sum = 56.548668
  closed form               = 56.548668
  cone (r=3.0, h=6) by Riemann sum = 56.548668
  1/3 pi r^2 h                     = 56.548668

Block 3 - unrolling a cone gives a sector
  r=3.0, h=4.0 -> slant l = 5.000000
  unrolled: a sector of radius 5.0000, arc 18.849556
  sector angle 3.769911 rad (216.0000 deg)
  sector area  47.123890   pi r l = 47.123890

Block 4 - Archimedes' tombstone: sphere inside its snug cylinder
  sphere volume 113.097336,  cylinder volume 169.646003
  ratio = 0.6666666667
  sphere area   113.097336,  cylinder total area 169.646003
  ratio = 0.6666666667
  both ratios are exactly 2/3 - which is what he wanted on his grave

Block 5 - scaling: length k, area k^2, volume k^3
      k    volume x    area x    area/volume x
      1        1.0       1.0         1.0000
      2        8.0       4.0         0.5000
      3       27.0       9.0         0.3333
     10     1000.0     100.0         0.1000
  surface-to-volume falls as 1/k: big things have proportionally less skin

solids: passed
```

Block 1 is Archimedes' argument, executed. The two solids look nothing alike, yet every slice matches — and that is enough to force equal volumes.

> [!NOTE]
> In block 4 the sphere's volume and surface area print as the same number, $113.097$. That is a coincidence of choosing $r = 3$: $\tfrac43\pi r^3 = 36\pi$ and $4\pi r^2 = 36\pi$ only when $r = 3$. They are still a volume and an area, in different units, and at any other radius the numbers differ.

## Common pitfalls and traps

- **Using slant height where perpendicular height belongs, or the reverse.** Volume of a cone uses $h$; curved surface uses $l$. They are different numbers related by $l = \sqrt{r^2+h^2}$, and swapping them is the classic error.
- **Forgetting which surfaces are included.** "Curved surface area" of a cone excludes the base. A closed cylinder has two circular ends; an open pipe has none. Read the question.
- **Assuming a cone is half a cylinder.** It is a **third**. The cross-section shrinks linearly, so its *area* shrinks quadratically.
- **Applying Cavalieri without checking every height.** The principle requires equal cross-sections at *every* level, not just at a few. Matching at three heights proves nothing.
- **Expecting the sphere to unroll.** It cannot — a sphere has intrinsic curvature and no flat development exists. This is a theorem, not a lack of ingenuity, and it is why world maps must distort area, angle, or both.
- **Scaling area and volume by the same factor.** Doubling the radius of a tank multiplies steel by $4$ and capacity by $8$. Costing a scaled design as though both grow together is a real and expensive mistake.

## Check your understanding

1. A cylinder has radius $7$ cm and height $10$ cm. Find its volume and total surface area. Use $\pi \approx \frac{22}{7}$.
2. A cone has radius $5$ and perpendicular height $12$. Find its slant height, curved surface area and volume.
3. A sphere and a cone have the same radius $r$, and the cone has height $2r$. Which has the greater volume, and by what ratio?
4. A hemisphere of radius $r$ sits on top of a cylinder of the same radius and height $h$. Give the total volume and the total **exterior** surface area.
5. If a model is built at $\frac{1}{10}$ scale, what fraction of the original's surface area and volume does it have?

<details><summary>Answers — open only after an attempt</summary>

1. $V = \pi r^2 h = \frac{22}{7}\times 49 \times 10 = 1540$ cm³. Total surface $= 2\pi r h + 2\pi r^2 = \frac{22}{7}\times 2 \times 7 \times 10 + \frac{22}{7}\times 2 \times 49 = 440 + 308 = 748$ cm².
2. $l = \sqrt{25 + 144} = \sqrt{169} = 13$. Curved surface $= \pi r l = 65\pi \approx 204.2$. Volume $= \tfrac13\pi(25)(12) = 100\pi \approx 314.2$.
3. Sphere $= \tfrac43\pi r^3$; cone $= \tfrac13\pi r^2(2r) = \tfrac23\pi r^3$. The **sphere** is greater, by a factor of exactly $2$.
4. Volume $= \pi r^2 h + \tfrac23\pi r^3$. Exterior surface $=$ cylinder's curved part $2\pi r h$ $+$ hemisphere's curved part $2\pi r^2$ $+$ the cylinder's **base** $\pi r^2$ — the top of the cylinder is covered by the hemisphere and is not exterior. Total $= 2\pi r h + 3\pi r^2$.
5. Surface area $\left(\frac{1}{10}\right)^2 = \frac{1}{100}$; volume $\left(\frac{1}{10}\right)^3 = \frac{1}{1000}$.

**And the prediction from section 4:** the cylinder has volume $\pi r^2(2r) = 2\pi r^3$, and the sphere $\tfrac43\pi r^3$ — a ratio of exactly $\tfrac23$. The cylinder's total surface is $2\pi r(2r) + 2\pi r^2 = 6\pi r^2$, and the sphere's is $4\pi r^2$ — again exactly $\tfrac23$. Both ratios being the same number is Archimedes' result, and block 4 confirms both.
</details>

## Practice — independent task

Implement `volume_of_revolution(radius_at_height, lo, hi, n)`: the volume of the solid formed by rotating a curve about an axis, computed by slicing.

1. Use the disc method: a slice at height $y$ is a circle of radius `radius_at_height(y)`, so its area is $\pi r(y)^2$. Sum over slices.
2. Reproduce every solid in this lesson: cylinder (constant radius), cone (linear), sphere (`sqrt(r^2 - y^2)`), and check each against its closed form to within `1e-6`.
3. Compare **midpoint**, **trapezoidal** and **left-endpoint** sums at the same `n`. Report which converges fastest, and by how much — with numbers you produced.
4. Now do something with no elementary closed form: rotate $y = e^{-x^2}$ about the $x$-axis for $x \in [-3, 3]$. Report your value and estimate its error by comparing $n$ and $2n$.
5. Investigate the sphere near its poles. The radius function has **infinite slope** at $y = \pm r$, so the discs are a poor fit there. Measure how the error behaves as $n$ grows — does it improve like $1/n$, $1/n^2$, or something worse? State what you observed.

**Edge cases:** `lo == hi`; a radius function returning zero throughout; a negative radius (decide whether to raise or square it away, and justify).

**Done when:** all four closed forms are reproduced, your step-3 comparison is backed by measured numbers, and your answer to step 5 identifies the convergence rate you actually observed rather than the one you expected.

## Tradeoffs, limits and extensions

**Cavalieri is integration without the notation.** "Equal cross-sections at every height means equal volume" is the statement that $\int A(y)\,dy$ depends only on $A$. The lab's `volume_by_slicing` is a Riemann sum, and [[06-calculus/03-calculus-2/03-applications|applications of integration]] formalises it. The advantage of Cavalieri's form is that it gives the sphere exactly, with no limit taken.

**Some solids genuinely need calculus.** A torus, an ellipsoid, or the solid of revolution in step 4 above have no elementary dissection argument. The slicing method handles all of them uniformly, which is why it eventually replaced the geometric arguments entirely.

**Numerical accuracy has a shape.** A midpoint Riemann sum converges as $O(1/n^2)$ for a smooth integrand, but the sphere's radius function has unbounded derivative at the poles, so the observed rate there is worse. Step 5 asks you to measure this rather than assume it — the gap between the theoretical rate and the observed one is exactly where numerical analysis lives.

## Before moving on

You are done with this lesson when you can:

- State Cavalieri's principle and use it to derive the sphere's volume from a cylinder and a cone.
- Derive the cone's curved surface area by unrolling it into a sector.
- Choose correctly between perpendicular height and slant height.
- Apply the $k$, $k^2$, $k^3$ scaling laws and give a physical consequence.

**Recap for later lookup:** prism/cylinder $V = Ah$; cylinder curved surface $2\pi r h$; cone $V = \tfrac13\pi r^2 h$, curved surface $\pi r l$ with $l = \sqrt{r^2+h^2}$; sphere $V = \tfrac43\pi r^3$, surface $4\pi r^2$; sphere : circumscribing cylinder $= 2 : 3$ in both volume and surface area; lengths scale as $k$, areas $k^2$, volumes $k^3$.

**Next:** [[01-latitude-and-longitude|Latitude and Longitude]] — the sphere again, but now measuring *on* its surface, where none of the plane formulas apply.

## Related

- [[01-plane-shapes|Plane Shapes]] — the sector area the cone derivation needs
- [[02-triangles-and-polygons|Triangles and Polygons]] — Pythagoras for slant heights
- [[06-calculus/03-calculus-2/03-applications|Applications of Integration]] — where slicing becomes an integral
