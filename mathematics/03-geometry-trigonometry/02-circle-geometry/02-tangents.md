# Tangents to a Circle

**[Intermediate]** — what happens when a chord's two ends slide together until the line only touches, and the three theorems that follow.

## Before you start

- You know the central angle theorem and its corollaries — [[01-circle-theorems|circle theorems]]. The alternate segment proof uses the angle in a semicircle.
- You can use RHS congruence — [[02-triangles-and-polygons|triangles and polygons]].
- You know the perpendicular bisector construction — [[03-constructions|constructions]].

**What you will be able to do after this lesson:**

1. Prove that a tangent is perpendicular to the radius at its point of contact, and that two tangents from an external point are equal.
2. State and prove the **alternate segment theorem**, and recognise the diagram that calls for it.
3. Use the **power of a point** to relate intersecting chords, secants and tangents with one formula.
4. Construct the tangents from an external point, and explain why the construction works.

**Study route:** read 1–5, attempt the prediction in section 5, then run the lab, then the practice task.

---

## 1. Why this exists

A belt runs around two pulleys. To cut it to length you need the straight sections — and each straight section is a **tangent** to both wheels, touching each at exactly one point. There is no chord to work with and no obvious triangle, yet the length is completely determined by the two radii and the distance between the centres.

More generally, tangents are how a circle meets the world outside it: a wheel meeting a road, a rope leaving a capstan, a light ray grazing a lens. The theorems below turn "just touching" into something you can compute with.

Start from a chord. Slide its two endpoints towards each other along the circle. The chord shortens, and at the instant the two points coincide, the line touches at one point only. That limiting line is the tangent, and several chord theorems survive the limit in a modified form — which is a useful way to remember them.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Tangent** | A line meeting the circle at exactly **one** point | From Latin *tangere*, to touch |
| **Point of contact** | The single point where the tangent meets the circle | Also called the point of tangency |
| **Secant** | A line cutting the circle at **two** points | A chord is the part of a secant inside the circle |
| **External point** | A point outside the circle | Exactly two tangents pass through it |
| **Tangent length** | The distance from an external point to its point of contact | Equal for both tangents |
| **Alternate segment** | The segment on the *other* side of a chord from the tangent-chord angle | The source of most confusion in this topic |
| **Power of a point** | For a point $P$ and circle of centre $O$, radius $r$: the quantity $OP^2 - r^2$ | Negative inside, zero on, positive outside |

## 3. The two basic theorems

### 3.1 A tangent is perpendicular to the radius at the point of contact

**Proof by contradiction.** Let the tangent touch at $T$, and suppose $OT$ is **not** perpendicular to it. Drop the perpendicular from $O$ to the line, meeting it at $M$, with $M \neq T$.

The perpendicular is the shortest distance from a point to a line, so:

$$
OM < OT = r
$$

So $M$ lies **inside** the circle. But a line through an interior point cuts the circle at **two** points — contradicting the assumption that the line is a tangent and meets it at one.

Therefore $M = T$, and $OT$ is perpendicular to the tangent. $\blacksquare$

This is the theorem everything else rests on, and the proof is worth noticing: it never constructs anything, it just rules out the alternative.

### 3.2 Two tangents from an external point are equal

Let $P$ be outside the circle, with tangents touching at $T_1$ and $T_2$.

Triangles $OT_1P$ and $OT_2P$ have:

- $OT_1 = OT_2 = r$ — radii,
- $OP$ common,
- right angles at $T_1$ and $T_2$ — by 3.1.

By **RHS**, the triangles are congruent. Hence $PT_1 = PT_2$, and also $\angle T_1PO = \angle T_2PO$. $\blacksquare$

Two consequences worth stating separately:

- **The tangent lengths are equal.** From Pythagoras in either right triangle, $PT = \sqrt{OP^2 - r^2}$ — which is the square root of the power of the point.
- **$OP$ bisects the angle between the tangents**, and also bisects $T_1T_2$ at right angles.

## 4. The alternate segment theorem

**Claim:** the angle between a tangent and a chord equals the angle subtended by that chord in the **alternate segment**.

```
                    B
                   / \
                  /   \
                 /     \
                /       \
               C         \
                \         \
        ---------A---------------   tangent at A
                 ^
          angle TAB  =  angle ACB   (C is in the alternate segment)
```

**Proof.** Let the tangent touch at $A$, and let $AB$ be a chord. Draw the diameter $AD$ from $A$.

By 3.1, the tangent is perpendicular to the radius $AO$, so:

$$
\angle DAT = 90°
$$

By the angle in a semicircle (Corollary 1 of the previous lesson), since $AD$ is a diameter:

$$
\angle ABD = 90°
$$

In triangle $ABD$ the angles sum to $180°$, so:

$$
\angle ADB = 180° - 90° - \angle DAB = 90° - \angle DAB
$$

And from the right angle at $A$:

$$
\angle TAB = \angle DAT - \angle DAB = 90° - \angle DAB
$$

The two right-hand sides are identical, so:

$$
\angle TAB = \angle ADB
$$

And $\angle ADB$ is the angle subtended by chord $AB$ at $D$, which lies in the alternate segment. By "angles in the same segment are equal", any other point $C$ in that segment gives the same angle. $\blacksquare$

**Which segment is "alternate"?** The chord divides the circle into two segments. The tangent-chord angle you are measuring opens towards one of them; the alternate segment is the **other** one. If you find yourself getting the supplement of the expected answer, you have used the near segment instead of the far one.

## 5. Power of a point — one formula for three theorems

Let $P$ be any point and let a line through $P$ cut the circle at $A$ and $B$. The product $PA \times PB$ turns out not to depend on which line you chose.

- **$P$ inside** (intersecting chords): for two chords $AB$ and $CD$ through $P$,
  $$PA \times PB = PC \times PD$$
- **$P$ outside** (two secants): with $A$, $B$ on one secant and $C$, $D$ on the other,
  $$PA \times PB = PC \times PD$$
- **$P$ outside, one line a tangent**: the two intersection points merge into the single point $T$, so $PA \times PB$ becomes $PT \times PT$:
  $$PT^2 = PA \times PB$$

All three are the same statement. In each case the common value is $\lvert OP^2 - r^2 \rvert$ — the magnitude of the **power of the point**. That is why the tangent length is $\sqrt{OP^2 - r^2}$: it is the case where the two points coincide.

> [!TIP]
> **Predict before running the lab.** A point $P$ sits $13$ units from the centre of a circle of radius $5$. A secant from $P$ cuts the circle at $A$ and $B$, with $PA = 8$. What is $PB$, and what is the tangent length from $P$? Work both out before opening the answers.

### Constructing the tangents from an external point

You cannot draw a tangent by sliding a ruler until it "looks right". The construction:

1. Draw the segment $OP$ and find its **midpoint** $M$, by perpendicular bisector.
2. Draw the circle centred at $M$ through $O$ — that is, the circle with $OP$ as diameter.
3. It cuts the original circle at two points $T_1$ and $T_2$. Draw $PT_1$ and $PT_2$.

**Why it works.** $T_1$ lies on the circle with diameter $OP$, so by the angle in a semicircle, $\angle OT_1P = 90°$. So $PT_1$ is perpendicular to the radius $OT_1$ at a point on the circle — which by the converse of 3.1 makes it a tangent. $\blacksquare$

## Worked example — runnable

**Runnable example:** save as `tangents.py` in any empty directory and run `python3 tangents.py`. Standard library only; writes no files.

```python
"""Tangent theorems, checked numerically - including the construction.

The construction block uses only circle-circle intersection, so it is a
legal compass-and-straightedge procedure, not a trigonometric shortcut.
"""
import math

EPS = 1e-9
R = 5.0
O = (0.0, 0.0)


def dist(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def angle_at(v, p, q):
    u = (p[0] - v[0], p[1] - v[1])
    w = (q[0] - v[0], q[1] - v[1])
    cos = (u[0] * w[0] + u[1] * w[1]) / (math.hypot(*u) * math.hypot(*w))
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def circle_circle(c1, r1, c2, r2):
    (x1, y1), (x2, y2) = c1, c2
    d = dist(c1, c2)
    if d < EPS or d > r1 + r2 + EPS or d < abs(r1 - r2) - EPS:
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    xm, ym = x1 + a * (x2 - x1) / d, y1 + a * (y2 - y1) / d
    return [(xm + h * (y2 - y1) / d, ym - h * (x2 - x1) / d),
            (xm - h * (y2 - y1) / d, ym + h * (x2 - x1) / d)]


def on_circle(theta_degrees, r=R, centre=O):
    t = math.radians(theta_degrees)
    return (centre[0] + r * math.cos(t), centre[1] + r * math.sin(t))


def tangent_points(P):
    """Construction: intersect the circle with the circle on diameter OP."""
    M = ((O[0] + P[0]) / 2, (O[1] + P[1]) / 2)
    return circle_circle(O, R, M, dist(O, P) / 2)


def line_circle(p, direction, r=R, centre=O):
    """Where the ray from p along `direction` meets the circle: both roots."""
    dx, dy = direction
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    fx, fy = p[0] - centre[0], p[1] - centre[1]
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - r * r
    disc = b * b - 4 * c
    if disc < 0:
        return []
    s = math.sqrt(disc)
    return [(p[0] + t * dx, p[1] + t * dy) for t in ((-b - s) / 2, (-b + s) / 2)]


if __name__ == "__main__":
    P = (13.0, 0.0)                      # external point, 13 from the centre

    print("3.1 and the construction: tangent is perpendicular to the radius")
    T1, T2 = tangent_points(P)
    print(f"  contact points: ({T1[0]:.6f}, {T1[1]:.6f}) and ({T2[0]:.6f}, {T2[1]:.6f})")
    print(f"  angle OT1P = {angle_at(T1, O, P):.6f}   angle OT2P = {angle_at(T2, O, P):.6f}")
    assert abs(angle_at(T1, O, P) - 90) < EPS
    assert abs(angle_at(T2, O, P) - 90) < EPS

    print()
    print("3.2 the two tangent lengths are equal")
    print(f"  PT1 = {dist(P, T1):.6f}   PT2 = {dist(P, T2):.6f}")
    print(f"  sqrt(OP^2 - r^2) = {math.sqrt(dist(O, P)**2 - R*R):.6f}")
    assert abs(dist(P, T1) - dist(P, T2)) < EPS
    assert abs(dist(P, T1) - math.sqrt(dist(O, P) ** 2 - R * R)) < EPS
    print(f"  OP bisects the angle: {angle_at(P, T1, O):.6f} = {angle_at(P, T2, O):.6f}")
    assert abs(angle_at(P, T1, O) - angle_at(P, T2, O)) < EPS

    print()
    print("4. alternate segment theorem")
    A = on_circle(180)                   # point of contact; tangent here is vertical
    B = on_circle(100)                   # the chord AB
    # the tangent at A runs perpendicular to OA, so along (0, 1) from A
    T_dir = (A[0] + 0.0, A[1] + 1.0)
    tangent_chord = angle_at(A, T_dir, B)
    for theta in (250, 300, 350):        # three points in the alternate segment
        C = on_circle(theta)
        print(f"  tangent-chord = {tangent_chord:.6f},  angle ACB at {theta} deg = {angle_at(C, A, B):.6f}")
        assert abs(tangent_chord - angle_at(C, A, B)) < EPS

    print()
    print("5. power of a point: PA x PB is the same for every line through P")
    power = dist(O, P) ** 2 - R * R
    print(f"  power of P = OP^2 - r^2 = {power:.6f}")
    for direction in [(-1.0, 0.0), (-12.0, 5.0), (-8.0, -3.0), (-13.0, 4.0)]:
        hits = line_circle(P, direction)
        if len(hits) < 2:
            continue
        pa, pb = dist(P, hits[0]), dist(P, hits[1])
        print(f"  direction {str(direction):>13} -> PA={pa:8.6f} PB={pb:8.6f} product={pa*pb:.6f}")
        assert abs(pa * pb - power) < 1e-6
    print(f"  tangent length squared = {dist(P, T1)**2:.6f}  (same value)")
    assert abs(dist(P, T1) ** 2 - power) < EPS

    print()
    print("tangents: passed")
```

Expected output:

```
3.1 and the construction: tangent is perpendicular to the radius
  contact points: (1.923077, -4.615385) and (1.923077, 4.615385)
  angle OT1P = 90.000000   angle OT2P = 90.000000

3.2 the two tangent lengths are equal
  PT1 = 12.000000   PT2 = 12.000000
  sqrt(OP^2 - r^2) = 12.000000
  OP bisects the angle: 22.619865 = 22.619865

4. alternate segment theorem
  tangent-chord = 40.000000,  angle ACB at 250 deg = 40.000000
  tangent-chord = 40.000000,  angle ACB at 300 deg = 40.000000
  tangent-chord = 40.000000,  angle ACB at 350 deg = 40.000000

5. power of a point: PA x PB is the same for every line through P
  power of P = OP^2 - r^2 = 144.000000
  direction   (-1.0, 0.0) -> PA=8.000000 PB=18.000000 product=144.000000
  direction  (-12.0, 5.0) -> PA=12.000000 PB=12.000000 product=144.000000
  direction  (-8.0, -3.0) -> PA=10.131597 PB=14.212961 product=144.000000
  direction  (-13.0, 4.0) -> PA=9.202739 PB=15.647515 product=144.000000
  tangent length squared = 144.000000  (same value)

tangents: passed
```

The last block is the point: four different lines through $P$, one identical product. Look at the second of them — it returns $PA = PB = 12$, because that direction *is* the tangent, and the two intersection points have merged. The tangent case is not a separate theorem; it is the same computation with a repeated root. That invariance is what "power of a point" names.

## Common pitfalls and traps

- **Using the near segment instead of the alternate one.** The alternate segment is on the *far* side of the chord from the angle you are measuring. Using the near one gives the supplement — an answer that looks plausible and is wrong.
- **Assuming a line that touches "at about one point" is a tangent.** Tangency is exact. In a diagram it must be stated or derivable, most often from a marked right angle at the radius.
- **Forgetting the converse of 3.1.** To *prove* a line is a tangent, showing it is perpendicular to a radius at a point on the circle is enough. Many problems want this direction.
- **Applying the tangent length formula to an internal point.** $\sqrt{OP^2 - r^2}$ requires $OP > r$. Inside the circle the power is negative and there are no tangents through the point at all.
- **Mixing up which segments the power formula multiplies.** $PA \times PB$ uses the distances from $P$ to *both* intersection points, not the chord length. For an external point both lie on the same side; for an internal point they lie on opposite sides.
- **Reading the lab as proof.** It confirms the configurations tested. The proofs in sections 3 and 4 are what make the results general.

## Check your understanding

1. A tangent from $P$ touches a circle of radius $7$, and $OP = 25$. Find the tangent length.
2. Two tangents from $P$ meet the circle at $A$ and $B$, and $\angle APB = 48°$. Find $\angle AOB$.
3. A tangent-chord angle is $63°$. What is the angle in the alternate segment? What is the angle in the *other* segment?
4. Chords $AB$ and $CD$ meet inside a circle at $P$, with $PA = 4$, $PB = 9$, $PC = 6$. Find $PD$.
5. Why is the tangent length the *square root* of the power of the point rather than the power itself?

<details><summary>Answers — open only after an attempt</summary>

1. $PT = \sqrt{25^2 - 7^2} = \sqrt{625 - 49} = \sqrt{576} = 24$.
2. $OAPB$ has right angles at $A$ and $B$ (tangent ⟂ radius). Angles of a quadrilateral sum to $360°$, so $\angle AOB = 360 - 90 - 90 - 48 = 132°$.
3. The angle in the alternate segment is $63°$. The angle in the other segment is $180 - 63 = 117°$, since the two are angles of a cyclic quadrilateral on opposite sides of the chord.
4. $PA \times PB = PC \times PD$, so $4 \times 9 = 6 \times PD$, giving $PD = 36/6 = 6$.
5. Because the power is the *product* $PA \times PB$, and for a tangent the two intersection points coincide, so the product becomes $PT \times PT = PT^2$. Taking the square root recovers the single length.

**And the prediction from section 5:** the power of $P$ is $13^2 - 5^2 = 169 - 25 = 144$. So $PA \times PB = 144$, giving $PB = 144/8 = 18$. The tangent length is $\sqrt{144} = 12$.
</details>

## Practice — independent task

Implement `belt_length(c1, r1, c2, r2)` returning the total length of a belt wrapped around two pulleys — the problem from section 1.

For an **open** belt (both pulleys turning the same way), the belt consists of two straight external tangent sections plus an arc on each pulley.

1. Compute the length of an external tangent between two circles. Derive it rather than looking it up: the answer is $\sqrt{d^2 - (r_1 - r_2)^2}$ where $d$ is the centre distance. Explain in a comment where the $(r_1 - r_2)$ comes from — hint: translate one circle's radius onto the other.
2. Compute the wrap angle on each pulley, and hence each arc length.
3. Sum: two straight sections plus two arcs.
4. **Check it against a case you can verify independently:** when $r_1 = r_2 = r$, the belt is two straight sections of length $d$ plus two half-circumferences, so the total must be exactly $2d + 2\pi r$. Assert this.
5. Handle the degenerate cases: one circle inside the other (no external tangent exists), and $d = 0$.

**Done when:** your equal-radius case matches $2d + 2\pi r$ to within `1e-9`, your wrap angles sum to $2\pi$ across the two pulleys, and you can explain why they must.

## Tradeoffs, limits and extensions

**Power of a point generalises further than shown.** It extends to the *radical axis* — the locus of points with equal power with respect to two circles — which is the basis for how circle-circle intersection is computed in practice, including in the lab's own `circle_circle` function.

**The limit argument is intuition, not proof.** Describing a tangent as "a chord whose endpoints have merged" is a good way to remember which theorems survive, but every theorem above was proved directly, without limits. The limiting picture becomes rigorous only once derivatives are available — a tangent line is exactly what a [[06-defining-derivative/01-definition|derivative]] computes, and the circle case is the first example of that idea.

**Numerical caution.** The lab's power-of-a-point assertion uses a looser tolerance (`1e-6`) than the rest. Solving the quadratic for line-circle intersection loses precision when the two roots are close — a near-tangential secant. This is catastrophic cancellation, and a production implementation would use the numerically stable quadratic formula instead.

## Before moving on

You are done with this lesson when you can:

- Prove the tangent-radius perpendicularity by contradiction, without notes.
- State the alternate segment theorem and identify the correct segment in an unfamiliar diagram.
- Use the power of a point to handle chord, secant and tangent problems with one relation.
- Construct the tangents from an external point and say why the construction works.

**Recap for later lookup:** tangent ⟂ radius at the point of contact; two tangents from an external point are equal, with length $\sqrt{OP^2 - r^2}$, and the line to the centre bisects the angle between them; tangent-chord angle = angle in the alternate segment; $PA \times PB$ is constant for every line through $P$, equal to $\lvert OP^2 - r^2 \rvert$.

**Next:** [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — the same circles and lines, handled by algebra on coordinates rather than by theorem.

## Related

- [[01-circle-theorems|Circle Theorems]] — the angle in a semicircle, used twice here
- [[03-constructions|Constructions]] — the perpendicular bisector the tangent construction needs
- [[01-ratios-and-right-triangles|Trigonometric Ratios]] — the wrap angles in the practice task
