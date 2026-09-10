# Circle Theorems

**[Beginner]** — one theorem about the centre, and the four results that fall out of it for free.

## Before you start

- You can use the isosceles triangle result and the exterior angle theorem — [[02-triangles-and-polygons|triangles and polygons]].
- You can chase angles and name the rule at each step — [[01-angles-and-parallel-lines|angles and parallel lines]].

**What you will be able to do after this lesson:**

1. Prove the central angle theorem, and derive the angle-in-a-semicircle, same-segment and cyclic-quadrilateral results from it.
2. Recognise which theorem a diagram is asking for, from the position of the marked angles.
3. Prove that a perpendicular from the centre bisects a chord, and use it to find distances.
4. Say what "subtends" means precisely enough to avoid the most common misreading of these theorems.

**Study route:** read 1–4, attempt the prediction in section 4, then run the lab and do the practice task.

---

## 1. Why this exists

A circular window is being fitted into a stone arch. The mason knows two points where the glass meets the frame, and needs the angle the glass makes when viewed from a third point on the rim — but the centre of the circle is behind the stonework and cannot be reached.

Circle theorems answer exactly this class of question: they relate angles at the **rim** to angles at the **centre**, and to each other, so that an inaccessible measurement can be deduced from accessible ones.

There is a second reason these are worth learning properly. Almost every one of them is a consequence of a **single** theorem. Learning five separate facts is a memory problem; learning one fact and four short derivations is not.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Centre** | The point every point of the circle is equidistant from | Usually labelled $O$ |
| **Radius** | A segment from the centre to the circle | All radii of one circle are equal — this drives every proof |
| **Chord** | A segment joining two points on the circle | A diameter is the longest chord |
| **Arc** | Part of the circle itself | Two points cut the circle into a **minor** and a **major** arc |
| **Segment** | The region between a chord and an arc | Not the same as "line segment" |
| **Sector** | The region between two radii and an arc | A pizza slice |
| **Subtend** | To "sit opposite" — the angle a chord opens up at a point | Chord $AB$ subtends $\angle APB$ at $P$ |
| **Cyclic quadrilateral** | A four-sided figure with **all four** vertices on one circle | The condition is easy to lose sight of |
| **Angle at the centre** | The angle a chord subtends at $O$ | $\angle AOB$ |
| **Angle at the circumference** | The angle the same chord subtends at a point on the circle | $\angle APB$ |

**Subtend** deserves care. When a theorem says "the angle subtended by arc $AB$ at $P$", it means the angle $\angle APB$ — the angle you would see if you stood at $P$ and looked at the two ends of the chord. Which *arc* is named matters: the same chord subtends one angle from the major arc and a different one from the minor arc, and mixing them up is the most common error in this topic.

## 3. The one theorem

**Central angle theorem:** the angle a chord subtends at the centre is **twice** the angle it subtends at any point on the major arc.

$$
\angle AOB = 2 \times \angle APB
$$

```
              P
             / \
            /   \
           /     \
          /   O   \          angle AOB = 2 x angle APB
         /   / \   \
        /   /   \   \
       A---+-----+---B
```

**Proof.** Join $P$ to $O$ and extend it to a point $Q$ on the far side of the circle.

$OA$ and $OP$ are both radii, so triangle $OAP$ is **isosceles**, and the base angles are equal. Call each of them $a$:

$$
\angle OAP = \angle OPA = a
$$

Now apply the **exterior angle theorem** to triangle $OAP$ at $O$. The exterior angle $\angle AOQ$ equals the sum of the two opposite interior angles:

$$
\angle AOQ = a + a = 2a
$$

The identical argument on triangle $OBP$, with base angles $b$, gives:

$$
\angle BOQ = 2b
$$

Adding:

$$
\angle AOB = \angle AOQ + \angle BOQ = 2a + 2b = 2(a + b) = 2\,\angle APB \qquad \blacksquare
$$

Everything else in this lesson is a corollary.

### Corollary 1 — angle in a semicircle is $90°$

Let $AB$ be a **diameter**. Then $A$, $O$, $B$ are collinear, so $\angle AOB = 180°$. By the theorem:

$$
\angle APB = \tfrac{1}{2} \times 180° = 90°
$$

Every point on the circle sees a diameter at a right angle. This is often called Thales' theorem, and it is the oldest result here.

### Corollary 2 — angles in the same segment are equal

Let $P$ and $P'$ both lie on the major arc. Both angles $\angle APB$ and $\angle AP'B$ are half of the *same* central angle $\angle AOB$, so:

$$
\angle APB = \angle AP'B
$$

The angle a chord subtends does not depend on **where** on the arc you stand. Move around the major arc and the angle stays fixed.

### Corollary 3 — opposite angles of a cyclic quadrilateral sum to $180°$

Let $ABCD$ be cyclic. Chord $AC$ subtends $\angle ABC$ at $B$ and $\angle ADC$ at $D$, on opposite arcs. The two central angles at $O$ — one for each arc — together make a full turn:

$$
2\,\angle ABC + 2\,\angle ADC = 360°
$$

Dividing by two:

$$
\angle ABC + \angle ADC = 180°
$$

Opposite angles of a cyclic quadrilateral are **supplementary**. The converse also holds and is often the more useful direction: if a quadrilateral's opposite angles sum to $180°$, its four vertices lie on a circle.

## 4. Chords and the centre

**Theorem:** the perpendicular from the centre to a chord **bisects** the chord.

**Proof.** Let $M$ be the foot of the perpendicular from $O$ to chord $AB$. Triangles $OMA$ and $OMB$ have $OA = OB$ (radii), $OM$ common, and right angles at $M$. By **RHS** they are congruent, so $AM = MB$. $\blacksquare$

The converse holds too: the line from the centre to a chord's midpoint is perpendicular to it.

This gives a useful length relation. If the circle has radius $r$, the chord has length $2\ell$, and the perpendicular distance from centre to chord is $d$, then Pythagoras in triangle $OMA$ gives:

$$
r^2 = d^2 + \ell^2
$$

Two consequences follow immediately:

- **Equal chords are equidistant from the centre**, and conversely. Longer chord, smaller $d$.
- The **longest** chord has $d = 0$, so it passes through the centre: it is a diameter, of length $2r$.

> [!TIP]
> **Predict before running the lab.** A chord of length $6$ sits in a circle of radius $5$. Another chord of the same circle is $8$ long. Which is closer to the centre, and by how much? Work it out before opening the answers.

## Worked example — runnable

**Runnable example:** save as `circle_theorems.py` in any empty directory and run `python3 circle_theorems.py`. Standard library only; writes no files.

```python
"""Every circle theorem in this lesson, checked numerically.

Points live on a circle of radius r centred at the origin, named by the
angle in degrees at which they sit. That makes it easy to move a point
around an arc and watch which quantities change and which do not.
"""
import math

EPS = 1e-9
R = 5.0


def on_circle(theta_degrees, r=R):
    t = math.radians(theta_degrees)
    return (r * math.cos(t), r * math.sin(t))


def angle_at(v, p, q):
    """Angle p-v-q in degrees."""
    u = (p[0] - v[0], p[1] - v[1])
    w = (q[0] - v[0], q[1] - v[1])
    cos = (u[0] * w[0] + u[1] * w[1]) / (math.hypot(*u) * math.hypot(*w))
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def dist(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


O = (0.0, 0.0)

if __name__ == "__main__":
    A = on_circle(200)      # chord AB, fixed
    B = on_circle(340)

    print("Central angle theorem: angle at centre = 2 x angle at circumference")
    centre_angle = angle_at(O, A, B)
    print(f"  angle AOB at the centre = {centre_angle:.6f}")
    for theta in (30, 60, 90, 120):          # four positions on the major arc
        P = on_circle(theta)
        at_P = angle_at(P, A, B)
        print(f"    P at {theta:3} deg -> angle APB = {at_P:.6f}   (2x = {2*at_P:.6f})")
        assert abs(2 * at_P - centre_angle) < EPS

    print()
    print("Corollary 2: the angle does not depend on where P sits on the arc")
    values = {round(angle_at(on_circle(t), A, B), 9) for t in (30, 60, 90, 120)}
    print(f"  distinct values across four positions: {len(values)}")
    assert len(values) == 1

    print()
    print("Corollary 1: angle in a semicircle")
    D1, D2 = on_circle(0), on_circle(180)    # a diameter
    for theta in (37, 90, 143, 250):
        P = on_circle(theta)
        a = angle_at(P, D1, D2)
        print(f"  P at {theta:3} deg -> angle in semicircle = {a:.6f}")
        assert abs(a - 90) < EPS

    print()
    print("Corollary 3: cyclic quadrilateral, opposite angles")
    quad = [on_circle(t) for t in (20, 100, 190, 300)]
    W, X, Y, Z = quad
    wx = angle_at(W, Z, X)
    xy = angle_at(X, W, Y)
    yz = angle_at(Y, X, Z)
    zw = angle_at(Z, Y, W)
    print(f"  angles: {wx:.4f}, {xy:.4f}, {yz:.4f}, {zw:.4f}")
    print(f"  opposite pairs sum to {wx + yz:.6f} and {xy + zw:.6f}")
    assert abs((wx + yz) - 180) < EPS
    assert abs((xy + zw) - 180) < EPS

    print()
    print("Chords: perpendicular from the centre bisects, and r^2 = d^2 + l^2")
    for chord_len in (6.0, 8.0, 10.0):
        half = chord_len / 2
        d = math.sqrt(R * R - half * half)   # distance from centre to chord
        print(f"  chord {chord_len:4.1f} -> half {half:3.1f}, distance from centre {d:.6f}")
        assert abs(R * R - (d * d + half * half)) < EPS
    print("  the longest chord has distance 0 from the centre: it is the diameter")

    print()
    print("circle_theorems: passed")
```

Expected output:

```
Central angle theorem: angle at centre = 2 x angle at circumference
  angle AOB at the centre = 140.000000
    P at  30 deg -> angle APB = 70.000000   (2x = 140.000000)
    P at  60 deg -> angle APB = 70.000000   (2x = 140.000000)
    P at  90 deg -> angle APB = 70.000000   (2x = 140.000000)
    P at 120 deg -> angle APB = 70.000000   (2x = 140.000000)

Corollary 2: the angle does not depend on where P sits on the arc
  distinct values across four positions: 1

Corollary 1: angle in a semicircle
  P at  37 deg -> angle in semicircle = 90.000000
  P at  90 deg -> angle in semicircle = 90.000000
  P at 143 deg -> angle in semicircle = 90.000000
  P at 250 deg -> angle in semicircle = 90.000000

Corollary 3: cyclic quadrilateral, opposite angles
  angles: 100.0000, 95.0000, 80.0000, 85.0000
  opposite pairs sum to 180.000000 and 180.000000

Chords: perpendicular from the centre bisects, and r^2 = d^2 + l^2
  chord  6.0 -> half 3.0, distance from centre 4.000000
  chord  8.0 -> half 4.0, distance from centre 3.000000
  chord 10.0 -> half 5.0, distance from centre 0.000000
  the longest chord has distance 0 from the centre: it is the diameter

circle_theorems: passed
```

The second block is the corollary made visible: four different positions on the arc, one identical angle, to the last decimal place available.

## Common pitfalls and traps

- **Using the wrong arc.** "Angle at the circumference" means from the **major** arc when the central angle is the minor one. Stand on the minor arc instead and you get $180°$ minus the expected answer. If a diagram gives an angle that seems to be the supplement of the one you want, this is why.
- **Forgetting that all four vertices must be on the circle.** A quadrilateral with three vertices on a circle is not cyclic and its opposite angles need not sum to anything in particular.
- **Assuming a point is the centre.** A point drawn in the middle of a circle is the centre only if the diagram says so, or if two radii to it are marked equal. Every proof here uses $OA = OB$; without that, none of them apply.
- **Assuming a chord through the middle is a diameter.** It is a diameter only if it passes through the centre exactly. "Looks like it goes through the middle" is not a reason.
- **Applying the semicircle result to a chord that is not a diameter.** The $90°$ comes from $\angle AOB = 180°$, which only happens for a diameter.
- **Reading the lab as proof.** It confirms the theorems hold for the configurations tested, at floating-point precision. Section 3 is where the certainty comes from.

## Check your understanding

1. A chord subtends $70°$ at the circumference. What does it subtend at the centre?
2. In a cyclic quadrilateral $ABCD$, $\angle A = 105°$. Find $\angle C$. Can you find $\angle B$?
3. $PQ$ is a diameter and $R$ is on the circle. $\angle RPQ = 34°$. Find $\angle PQR$.
4. A chord of length $8$ lies in a circle of radius $5$. How far is it from the centre?
5. Why does the central angle theorem's proof need $P$ on the **major** arc? What goes wrong otherwise?

<details><summary>Answers — open only after an attempt</summary>

1. $140°$ — the angle at the centre is twice the angle at the circumference.
2. $\angle C = 180 - 105 = 75°$, since opposite angles of a cyclic quadrilateral are supplementary. $\angle B$ **cannot** be found: the constraint links opposite pairs only, and $\angle B$ can take any value with $\angle D$ adjusting to keep $\angle B + \angle D = 180°$.
3. $\angle PRQ = 90°$ (angle in a semicircle). The angles of triangle $PQR$ sum to $180°$, so $\angle PQR = 180 - 90 - 34 = 56°$.
4. Half the chord is $4$, so $d = \sqrt{5^2 - 4^2} = \sqrt{9} = 3$.
5. The proof extends $PO$ to $Q$ and adds $\angle AOQ + \angle BOQ$. That addition is only valid when $OQ$ lies **between** $OA$ and $OB$, which is what $P$ being on the major arc guarantees. With $P$ on the minor arc the two angles must be *subtracted* instead, and the result becomes the reflex angle at the centre — still twice $\angle APB$, but the reflex one.

**And the prediction from section 4:** for the chord of length $6$, $d = \sqrt{25 - 9} = 4$. For the chord of length $8$, $d = \sqrt{25 - 16} = 3$. The **longer** chord is closer to the centre, by $1$ unit. Longer chords always sit nearer the centre, and the diameter sits on it.
</details>

## Practice — independent task

Implement `circumcircle(a, b, c)`: given three points, return the centre and radius of the unique circle through all three — or `None` if they are collinear.

1. Find the centre as the intersection of two **perpendicular bisectors**, reusing the reasoning from [[03-constructions|constructions]]: the centre is equidistant from all three points, so it lies on the perpendicular bisector of every side.
2. Detect the collinear case and return `None` rather than dividing by a near-zero determinant. Say in a comment what tolerance you chose and why.
3. Assert that the returned centre really is equidistant from all three inputs.
4. Then use it to **test whether a quadrilateral is cyclic**: build the circumcircle of three vertices and check whether the fourth lies on it.
5. Verify your cyclic test against the theorem: for at least three cyclic quadrilaterals, confirm opposite angles sum to $180°$; for at least two non-cyclic ones, confirm they do not.

**Edge cases:** three collinear points; two coincident points; a quadrilateral whose fourth vertex is close to the circle but not on it — decide what "on the circle" means numerically and defend the choice.

**Done when:** your cyclic test and the opposite-angle test agree on every quadrilateral you try, and you can explain why they must agree — that is, why the converse of Corollary 3 is what licenses using either one.

## Tradeoffs, limits and extensions

**These are theorems about a plane.** On a sphere the "circle" through three points and the angle relations both change, and none of the results above survive unmodified.

**The converse is often the useful direction.** Corollary 3 says cyclic implies supplementary. The converse — supplementary implies cyclic — is what lets you *prove* four points lie on a circle, which is how these theorems are usually deployed in a harder problem. Do not assume a converse holds without checking; here it does, but the perpendicular-from-centre converse and the equal-chords converse each need their own argument.

**Where this reappears.** The inscribed angle theorem is the geometric core of the [[03-coordinate-geometry/01-coordinate-geometry|circle equation]], and the circumcircle of the practice task is the basis of Delaunay triangulation — the standard way to turn scattered points into a mesh in graphics and terrain modelling.

## Before moving on

You are done with this lesson when you can:

- Prove the central angle theorem from the isosceles and exterior-angle results, without notes.
- Derive all three corollaries from it rather than recalling them separately.
- Use $r^2 = d^2 + \ell^2$ to move between chord length and distance from the centre.

**Recap for later lookup:** angle at centre $= 2\times$ angle at circumference; angle in a semicircle $= 90°$; angles in the same segment are equal; opposite angles of a cyclic quadrilateral sum to $180°$; the perpendicular from the centre bisects a chord, with $r^2 = d^2 + \ell^2$.

**Next:** [[02-tangents|Tangents to a Circle]] — what happens when a chord's two ends slide together until the line touches at a single point.

## Related

- [[02-triangles-and-polygons|Triangles and Polygons]] — the isosceles and exterior-angle results every proof here uses
- [[03-constructions|Constructions]] — the perpendicular bisector needed for the practice task
- [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — the same circle handled by equation instead of theorem
