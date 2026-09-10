# Bearings

**[Intermediate]** — navigation angles, why they run clockwise from north, and how to turn a journey into a triangle.

## Before you start

- You can use the sine and cosine rules — [[03-sine-and-cosine-rules|sine and cosine rules]].
- You know the ratios and can resolve a length into components — [[01-ratios-and-right-triangles|trigonometric ratios]].

**What you will be able to do after this lesson:**

1. Read and write **three-figure bearings**, and convert between a bearing and a standard mathematical angle.
2. Compute a back bearing, and say why the rule is "add $180°$, then reduce mod $360°$".
3. Resolve a journey leg into northing and easting, and combine several legs into a single resultant.
4. Solve a navigation problem two ways — by components and by the cosine rule — and check one against the other.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 is the useful check.

---

## 1. Why this exists

Mathematics measures angles anticlockwise from the positive $x$-axis. Navigation measures them **clockwise from north**. These are different conventions, and mixing them is the most reliable way to sail into a rock.

The navigational convention is not perverse. A compass points north, so north is the one direction available for free anywhere on Earth. And a clock face turns clockwise, so "turn to $090$" reads naturally as a quarter turn to the right. The convention is built around what an instrument can actually give you.

So this lesson is partly trigonometry and partly **translation**: getting a bearing into a form the sine and cosine rules can consume, and getting the answer back out as a bearing.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Bearing** | Direction measured **clockwise from north**, always written with **three figures** | $007°$, not $7°$ |
| **Three-figure bearing** | The convention of padding to three digits | Removes any ambiguity over a dropped digit in radio traffic |
| **Back bearing** | The bearing of the reverse journey | Differs by exactly $180°$ |
| **Northing / Easting** | The north–south and east–west components of a displacement | The coordinates a bearing resolves into |
| **Resultant** | The single displacement equivalent to several legs | The straight line from start to finish |
| **Compass points** | $N = 000°$, $E = 090°$, $S = 180°$, $W = 270°$ | Increasing clockwise |

```
                 N  000
                  |
      315  NW     |     NE  045
             \    |    /
              \   |   /
   270  W -----+--+--+----- E  090
              /   |   \
             /    |    \
      225  SW     |     SE  135
                  |
                 S  180
```

## 3. Converting to and from mathematical angles

Let $\beta$ be a bearing and $\theta$ the standard mathematical angle (anticlockwise from east). The two conventions differ in **where zero is** and in **which way is positive**, so the conversion flips and shifts:

$$
\theta = 90° - \beta \pmod{360°}, \qquad \beta = 90° - \theta \pmod{360°}
$$

The relation is its own inverse, which is a useful thing to notice — the same line of code converts both ways.

**Resolving a leg into components.** Travel distance $d$ on bearing $\beta$. Because $\beta$ is measured from **north**, the component along north uses cosine and the component along east uses sine — the opposite of the usual arrangement:

$$
\text{northing} = d\cos\beta, \qquad \text{easting} = d\sin\beta
$$

Check it against a known case: on bearing $090°$ (due east), $\cos 90° = 0$ and $\sin 90° = 1$, giving northing $0$ and easting $d$. Correct.

**Recovering a bearing from components:**

$$
\beta = \operatorname{atan2}(\text{easting},\ \text{northing}) \pmod{360°}
$$

Note the argument order — easting first. `atan2(y, x)` normally takes the "vertical" component first, and here the roles are swapped because bearings are measured from north. This ordering is the single most common bug in navigation code.

**Back bearings.** The reverse of bearing $\beta$ is:

$$
\beta_{\text{back}} = (\beta + 180°) \bmod 360°
$$

The reduction matters. The back bearing of $250°$ is $070°$, not $430°$.

## 4. Multi-leg journeys

A journey of several legs is handled by resolving each into components, adding, and converting back:

1. For each leg, compute northing $= d_i\cos\beta_i$ and easting $= d_i\sin\beta_i$.
2. Sum all northings; sum all eastings.
3. Resultant distance $= \sqrt{N^2 + E^2}$.
4. Resultant bearing $= \operatorname{atan2}(E, N) \bmod 360°$.

This works for any number of legs and never needs a diagram. The alternative — drawing the triangle and applying the cosine rule — is faster for **two** legs and gives more insight, but it does not scale and it requires care with which angle sits inside the triangle.

**The angle inside the triangle.** For two legs on bearings $\beta_1$ then $\beta_2$, the interior angle at the turning point is:

$$
180° - \lvert \beta_2 - \beta_1 \rvert
$$

when that difference is under $180°$. This is where errors creep in: the angle *between the legs* is not the difference of the bearings, because the second leg's bearing is measured from a **new** north line, parallel to the first. The two north lines being parallel is what makes the interior angle a co-interior angle from [[01-angles-and-parallel-lines|angles and parallel lines]] — which is why that lesson comes first.

> [!TIP]
> **Predict before running the lab.** A ship sails $8$ km on bearing $060°$, then $5$ km on bearing $150°$. Before computing: is the turn to the right or the left, and is the angle between the two legs acute, right, or obtuse? Decide, then check against the lab's block 3.

## 5. Bearings and the triangle rules

Once the interior angle is known, a two-leg problem is an ordinary SAS triangle:

- **Distance from start to finish**: cosine rule on the two leg lengths and the included angle.
- **Bearing of the finish from the start**: sine rule for one of the remaining angles, then add or subtract from the first leg's bearing.

The component method and the triangle method must agree. Block 4 of the lab checks exactly that, and disagreement between them is a far better bug detector than re-reading your own arithmetic.

## Worked example — runnable

**Runnable example:** save as `bearings.py` in any empty directory and run `python3 bearings.py`. Standard library only; writes no files.

```python
"""Bearings: conversion, back bearings, and journeys resolved two ways."""
import math

EPS = 1e-9


def to_math_angle(bearing):
    """Bearing (clockwise from north) -> maths angle (anticlockwise from east)."""
    return (90 - bearing) % 360


def to_bearing(math_angle):
    """The same relation, used the other way round."""
    return (90 - math_angle) % 360


def components(distance, bearing):
    """A leg resolved into (northing, easting). Cosine for north, sine for east."""
    b = math.radians(bearing)
    return (distance * math.cos(b), distance * math.sin(b))


def back_bearing(bearing):
    return (bearing + 180) % 360


def resultant(legs):
    """legs is a list of (distance, bearing). Returns (distance, bearing)."""
    north = sum(components(d, b)[0] for d, b in legs)
    east = sum(components(d, b)[1] for d, b in legs)
    dist = math.hypot(north, east)
    bearing = math.degrees(math.atan2(east, north)) % 360
    return dist, bearing, north, east


def two_leg_by_cosine_rule(d1, b1, d2, b2):
    """The same two-leg problem, solved as an SAS triangle instead."""
    turn = abs(b2 - b1) % 360
    if turn > 180:
        turn = 360 - turn
    interior = 180 - turn                 # co-interior with the parallel north lines
    third = math.sqrt(d1*d1 + d2*d2 - 2*d1*d2*math.cos(math.radians(interior)))
    # angle at the start, between leg 1 and the direct line, by the sine rule
    sin_start = d2 * math.sin(math.radians(interior)) / third
    start_angle = math.degrees(math.asin(max(-1.0, min(1.0, sin_start))))
    direction = 1 if ((b2 - b1) % 360) < 180 else -1
    return third, (b1 + direction * start_angle) % 360, interior


if __name__ == "__main__":
    print("Block 1 - bearing and maths angle are the same relation both ways")
    for bearing in (0, 45, 90, 137, 180, 250, 315, 359):
        m = to_math_angle(bearing)
        print(f"  bearing {bearing:3.0f} -> maths angle {m:3.0f} -> bearing {to_bearing(m):3.0f}")
        assert abs(to_bearing(m) - bearing) < EPS

    print()
    print("Block 2 - components, and the compass points as a sanity check")
    for name, bearing in [("N", 0), ("E", 90), ("S", 180), ("W", 270)]:
        n, e = components(10, bearing)
        print(f"  10 km on {name} ({bearing:03d}): northing {n:+7.3f}  easting {e:+7.3f}")
    n, e = components(10, 90)
    assert abs(n) < EPS and abs(e - 10) < EPS
    n, e = components(10, 180)
    assert abs(n + 10) < EPS and abs(e) < EPS

    print("  back bearings:")
    for b in (70, 250, 0, 180, 359):
        print(f"    {b:03.0f} -> {back_bearing(b):03.0f}")
    assert back_bearing(250) == 70
    assert back_bearing(back_bearing(137)) == 137

    print()
    print("Block 3 - a two-leg journey")
    legs = [(8.0, 60.0), (5.0, 150.0)]
    dist, bearing, north, east = resultant(legs)
    print(f"  leg 1: 8 km on 060, leg 2: 5 km on 150")
    print(f"  total northing {north:+.6f} km, total easting {east:+.6f} km")
    print(f"  resultant: {dist:.6f} km on bearing {bearing:.4f}")

    print()
    print("Block 4 - the same problem as an SAS triangle, as a cross-check")
    tri_dist, tri_bearing, interior = two_leg_by_cosine_rule(8.0, 60.0, 5.0, 150.0)
    print(f"  interior angle between the legs = {interior:.4f} degrees")
    print(f"  cosine rule distance = {tri_dist:.6f} km")
    print(f"  bearing from start   = {tri_bearing:.4f}")
    print(f"  components method    = {dist:.6f} km on {bearing:.4f}")
    assert abs(tri_dist - dist) < 1e-9, (tri_dist, dist)
    assert abs(tri_bearing - bearing) < 1e-9, (tri_bearing, bearing)
    print("  the two methods agree")

    print()
    print("Block 5 - three legs, and a closed journey returns to the start")
    trip = [(12.0, 30.0), (7.0, 120.0), (9.0, 240.0)]
    d3, b3, n3, e3 = resultant(trip)
    print(f"  three legs -> {d3:.6f} km on bearing {b3:.4f}")
    # adding the reverse of the resultant must close the loop exactly
    closed = trip + [(d3, back_bearing(b3))]
    dc, bc, nc, ec = resultant(closed)
    print(f"  adding the return leg ({d3:.4f} km on {back_bearing(b3):.4f}) -> {dc:.9f} km")
    assert dc < 1e-9
    print("  a closed journey has zero resultant, as it must")

    print()
    print("bearings: passed")
```

Expected output:

```
Block 1 - bearing and maths angle are the same relation both ways
  bearing   0 -> maths angle  90 -> bearing   0
  bearing  45 -> maths angle  45 -> bearing  45
  bearing  90 -> maths angle   0 -> bearing  90
  bearing 137 -> maths angle 313 -> bearing 137
  bearing 180 -> maths angle 270 -> bearing 180
  bearing 250 -> maths angle 200 -> bearing 250
  bearing 315 -> maths angle 135 -> bearing 315
  bearing 359 -> maths angle  91 -> bearing 359

Block 2 - components, and the compass points as a sanity check
  10 km on N (000): northing +10.000  easting  +0.000
  10 km on E (090): northing  +0.000  easting +10.000
  10 km on S (180): northing -10.000  easting  +0.000
  10 km on W (270): northing  -0.000  easting -10.000
  back bearings:
    070 -> 250
    250 -> 070
    000 -> 180
    180 -> 000
    359 -> 179

Block 3 - a two-leg journey
  leg 1: 8 km on 060, leg 2: 5 km on 150
  total northing -0.330127 km, total easting +9.428203 km
  resultant: 9.433981 km on bearing 92.0054

Block 4 - the same problem as an SAS triangle, as a cross-check
  interior angle between the legs = 90.0000 degrees
  cosine rule distance = 9.433981 km
  bearing from start   = 92.0054
  components method    = 9.433981 km on 92.0054
  the two methods agree

Block 5 - three legs, and a closed journey returns to the start
  three legs -> 4.892700 km on bearing 60.7282
  adding the return leg (4.8927 km on 240.7282) -> 0.000000000 km
  a closed journey has zero resultant, as it must

bearings: passed
```

Block 4 is the habit worth keeping: two independent methods, one answer. If they disagree, one of them is wrong and you find out immediately rather than at sea.

## Common pitfalls and traps

- **Swapping sine and cosine.** Bearings measure from **north**, so northing uses $\cos$ and easting uses $\sin$. Every other trigonometry lesson trains the opposite habit. Check against a compass point — bearing $090°$ must give zero northing.
- **Argument order in `atan2`.** It is `atan2(easting, northing)`, not the usual `atan2(y, x)` with $y$ vertical. Getting this wrong reflects the bearing about $045°$, which looks plausible.
- **Forgetting to reduce mod $360°$.** A back bearing of $430°$ is a bug, not a bearing.
- **Taking the angle between legs as the difference of bearings.** It is $180°$ minus that difference, because the second bearing is measured from a fresh north line. This is a co-interior angle, and the lab's block 4 checks the result against the component method precisely because this step is so easy to get wrong.
- **Dropping the leading zeros.** $070°$ and $700$ are distinguishable on paper; over a radio they are not, which is why the three-figure convention exists.
- **Treating the Earth as flat.** Everything here assumes a plane. Over tens of kilometres that is fine; over hundreds it is not, and the bearing of a long great-circle route **changes continuously along the path**. See the limits section.

## Check your understanding

1. Convert bearings $000°$, $135°$, $270°$ to standard mathematical angles.
2. A walks from $P$ to $Q$ on bearing $115°$. What bearing does the return journey take?
3. A ship sails $10$ km due east, then $10$ km due north. Give the resultant distance and bearing.
4. Two legs are flown on bearings $040°$ and $100°$. What is the interior angle between them at the turning point?
5. Why does the resultant of a closed journey have to be zero, and what does that give you as a check on a multi-leg calculation?

<details><summary>Answers — open only after an attempt</summary>

1. $\theta = 90 - \beta \bmod 360$: $000° \to 90°$; $135° \to -45° \equiv 315°$; $270° \to -180° \equiv 180°$.
2. $115 + 180 = 295°$.
3. Northing $10$, easting $10$. Distance $= \sqrt{200} \approx 14.142$ km. Bearing $= \operatorname{atan2}(10, 10) = 45°$, so $045°$.
4. The difference is $60°$, so the interior angle is $180 - 60 = 120°$.
5. Because the resultant is the straight-line displacement from start to finish, and for a closed journey those are the same point — displacement zero. It is a complete check on a multi-leg calculation: append the reverse of your computed resultant and confirm the total collapses to zero, as block 5 does.

**And the prediction from section 4:** $150° > 060°$, so the turn is to the **right** (clockwise). The bearings differ by $90°$, so the interior angle between the legs is $180 - 90 = 90°$ — a **right** angle. The lab confirms it, and the resultant is then just $\sqrt{8^2 + 5^2} = \sqrt{89} \approx 9.434$ km.
</details>

## Practice — independent task

Implement `navigate(legs)` and a companion `intercept(start_a, bearing_a, start_b, bearing_b)`.

**Part A — `navigate(legs)`.** Take a list of `(distance, bearing)` and return the resultant, plus a running position after each leg.

1. Return the position history so a caller can plot the track.
2. Assert your resultant equals the last position in the history.
3. Verify with the closed-journey check: appending the reverse resultant must give zero to within `1e-9`.

**Part B — `intercept(...)`.** Two vessels start from known positions on known constant bearings. Find where their tracks cross, or report that they do not.

1. Convert each track to a line and intersect them — reuse the general-form line intersection from [[03-coordinate-geometry/01-coordinate-geometry|coordinate geometry]].
2. **Parallel tracks** must be reported, not divided by zero.
3. Crossing *behind* a vessel is not an interception: check that the crossing point lies **ahead** on both tracks, and say in a comment how you tested "ahead".
4. Return the distance each vessel travels to the crossing point, and hence — given speeds — whether they arrive at the same time.

**Edge cases:** identical starting points; tracks that cross at exactly the start; bearings differing by exactly $180°$ (head-on, same line); a bearing of $000°$, which puts a zero in one component.

**Done when:** Part A's closed-journey check passes for at least five random journeys, Part B correctly rejects a crossing that lies behind either vessel, and you can state what your intersection test does when the two tracks are the same line.

## Tradeoffs, limits and extensions

**The flat-Earth assumption.** Every formula here treats the surface as a plane. Over short distances the error is negligible; over long ones it is not. Worse, on a sphere the shortest path — the great circle — does **not** keep a constant bearing. A route flown on a fixed bearing is a *rhumb line*, which spirals towards the pole and is measurably longer. This is why long-haul flight paths look curved on a flat map, and it is handled in [[01-latitude-and-longitude|latitude and longitude]].

**True north, magnetic north, grid north.** A compass points to magnetic north, which differs from true north by the local *magnetic declination* — currently over $10°$ in parts of the world, and drifting year by year. Charts are drawn to true or grid north. A bearing is meaningless without knowing which north it refers to, and the mathematics here cannot tell you.

**Components scale, triangles do not.** For two legs the cosine rule is quicker by hand. For ten legs, components win outright, and they extend to three dimensions without modification. Prefer components in code; keep the triangle method for checking.

## Before moving on

You are done with this lesson when you can:

- Convert freely between bearings and mathematical angles, and say why the relation is its own inverse.
- Resolve a leg into northing and easting without hesitating over which gets $\cos$.
- Solve a two-leg problem by components *and* by the cosine rule, and get the same answer.
- Explain why the interior angle at a turning point is not the difference of the bearings.

**Recap for later lookup:** bearings run clockwise from north, always three figures; $\theta = 90° - \beta \pmod{360°}$ both ways; northing $= d\cos\beta$, easting $= d\sin\beta$; bearing $= \operatorname{atan2}(E, N) \bmod 360°$; back bearing $= (\beta + 180°) \bmod 360°$; interior angle between successive legs $= 180° - \lvert\Delta\beta\rvert$; a closed journey has zero resultant.

**Next:** [[05-hyperbolic-functions|Hyperbolic Functions]] — a second family of functions built from the same algebra, describing the hanging cable rather than the rotating wheel.

## Related

- [[03-sine-and-cosine-rules|Sine and Cosine Rules]] — the triangle method used as a cross-check
- [[01-angles-and-parallel-lines|Angles and Parallel Lines]] — the co-interior angle at the turning point
- [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — the line intersection the practice task needs
- [[01-latitude-and-longitude|Latitude and Longitude]] — what to do when the Earth's curvature matters
