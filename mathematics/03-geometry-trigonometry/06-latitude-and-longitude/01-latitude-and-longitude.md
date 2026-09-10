# Latitude and Longitude

**[Intermediate]** — measuring distance *on* a sphere, where parallel lines do not exist and the shortest route is not the obvious one.

## Before you start

- You can use bearings and resolve a journey — [[04-bearings|bearings]].
- You know the sine and cosine rules for plane triangles — [[03-sine-and-cosine-rules|sine and cosine rules]].
- You know arc length $= r\theta$ in radians — [[01-plane-shapes|plane shapes]].

**What you will be able to do after this lesson:**

1. Locate a point by latitude and longitude, and compute the radius of its parallel of latitude.
2. Compute distances along a meridian and along a parallel, and say which is a **great circle** and which is not.
3. Compute great-circle distance with the spherical cosine rule and with the **haversine** formula, and explain why the second one exists.
4. Demonstrate that a route along a parallel is **longer** than the great-circle route between the same two points.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Blocks 3 and 4 are the payoff.

---

## 1. Why this exists

Everything in this folder so far has assumed a flat plane. The Earth is not one, and over long distances the difference is not a rounding error — it changes which route is shortest.

The most striking consequence: two cities at the **same latitude** are not most quickly reached by travelling due east or west. That path looks straight on a wall map and feels obviously right, but it is not the shortest one. Flight paths that appear to bow northwards on a flat map are not detours; they are the straight lines, and the map is what is bent.

So the plane geometry has to be rebuilt. There are no parallel lines on a sphere, triangle angles sum to more than $180°$, and "straight line" has to be redefined before anything else can be said.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Latitude** ($\phi$) | Angle north or south of the equator, $0°$ to $90°$ | $\phi = 0$ at the equator, $90°$N at the pole |
| **Longitude** ($\lambda$) | Angle east or west of the prime meridian, $0°$ to $180°$ | Greenwich is $0°$ by convention, not by nature |
| **Meridian** | A half-circle of constant longitude, pole to pole | Always part of a **great** circle |
| **Parallel of latitude** | A circle of constant latitude | A **small** circle, except the equator |
| **Great circle** | A circle whose centre is the Earth's centre | The shortest path between two points lies on one |
| **Small circle** | Any other circle on the sphere | Every parallel except the equator |
| **Nautical mile** | One minute of arc along a great circle | Defined as exactly $1852$ m |

The distinction that carries the lesson: **meridians are great circles, parallels are not.** Travelling due north follows a shortest path; travelling due east generally does not.

## 3. The radius of a parallel

A parallel at latitude $\phi$ is a circle, but not one centred on the Earth's centre. Slicing the sphere at that latitude gives a circle of radius:

$$
r = R\cos\phi
$$

where $R$ is the Earth's radius. The cosine appears because the parallel's radius is the *horizontal* leg of a right triangle whose hypotenuse is $R$ and whose angle at the centre is $\phi$.

```
              N pole
                |
          ______|______   parallel at latitude phi
         /   r  |      \
        /       |       \
       |    R  /|        |
       |     /  |        |
       |   / phi|        |
       |-------+---------|   equator (radius R)
        \      centre   /
         \             /
          \___________/
```

At the equator $\cos 0 = 1$, giving the full radius. At the pole $\cos 90° = 0$: the parallel shrinks to a point.

**Distances:**

| Along | Formula | Great circle? |
| :--- | :--- | :---: |
| A **meridian** (change of latitude) | $R \times \Delta\phi_{\text{rad}}$ | **Yes** |
| A **parallel** (change of longitude) | $R\cos\phi \times \Delta\lambda_{\text{rad}}$ | **No**, unless $\phi = 0$ |

The $\cos\phi$ factor is why longitude lines crowd together towards the poles, and why one degree of longitude is about $111$ km at the equator but only about $56$ km at $60°$N.

**Nautical miles.** One minute of arc along a great circle is one nautical mile. That is why the unit exists: a degree of latitude is $60$ nautical miles anywhere on Earth, so latitude differences can be read directly off a chart as distances. Longitude differences cannot, because of the $\cos\phi$.

## 4. Great-circle distance

For two points $(\phi_1, \lambda_1)$ and $(\phi_2, \lambda_2)$, the **spherical cosine rule** gives the angle $c$ subtended at the Earth's centre:

$$
\cos c = \sin\phi_1\sin\phi_2 + \cos\phi_1\cos\phi_2\cos(\Delta\lambda)
$$

and then the distance is $R c$ with $c$ in radians.

This is the spherical analogue of the plane cosine rule from [[03-sine-and-cosine-rules|the sine and cosine rules]] — the sides of a spherical triangle are themselves angles, so products of sines and cosines replace the squares.

**Why a formula with a name of its own.** The cosine rule is exact in mathematics and poor in floating point. For two nearby points $\cos c \approx 1$, and `acos` is ill-conditioned there — its derivative is unbounded, so a rounding error in the seventh decimal place of $\cos c$ becomes a large relative error in $c$. Distances of a few metres come out badly wrong.

The **haversine** formula avoids this by working with half-angles and `atan2`:

$$
a = \sin^2\!\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1\cos\phi_2\sin^2\!\left(\frac{\Delta\lambda}{2}\right)
$$
$$
c = 2\operatorname{atan2}\!\left(\sqrt{a},\ \sqrt{1-a}\right), \qquad d = Rc
$$

Mathematically identical, numerically far better for short distances. Block 4 of the lab measures the difference.

> [!TIP]
> **Predict before running the lab.** Two points both lie at $60°$N, one at $0°$ longitude and one at $180°$. Travelling along the parallel means going halfway round a circle of radius $R\cos 60° = R/2$. What is the alternative, and roughly how much shorter is it? Estimate before opening the answers.

## 5. Why the parallel is not the shortest route

Take the two points from the prediction: $(60°\text{N}, 0°)$ and $(60°\text{N}, 180°)$.

**Along the parallel.** The parallel has radius $R\cos 60° = R/2$, and the journey covers half of it:

$$
d_{\text{parallel}} = \pi \times \frac{R}{2} \approx 1.5708R
$$

**Over the pole.** Both points lie on the *same* great circle — the meridian through $0°$ and $180°$ is a single complete great circle passing over the North Pole. From $60°$N to the pole is $30°$ of arc, and down the other side is another $30°$:

$$
d_{\text{great circle}} = R \times \frac{60\pi}{180} \approx 1.0472R
$$

The polar route is about **one third shorter**. With $R = 6371$ km that is roughly $10{,}008$ km against $6{,}672$ km — a saving of over $3{,}300$ km, which is why polar routes exist.

The general principle: a great circle is the intersection of the sphere with a plane through the **centre**. Any other circle has a smaller radius, so covering the same angular span takes more distance.

## Worked example — runnable

**Runnable example:** save as `lat_long.py` in any empty directory and run `python3 lat_long.py`. Standard library only; writes no files.

```python
"""Distances on a sphere: meridians, parallels, and great circles."""
import math

R_EARTH_KM = 6371.0088          # IUGG mean radius
NAUTICAL_MILE_M = 1852.0


def parallel_radius(lat_deg, R=R_EARTH_KM):
    return R * math.cos(math.radians(lat_deg))


def along_meridian(lat1, lat2, R=R_EARTH_KM):
    """Distance due north or south: always a great-circle arc."""
    return R * abs(math.radians(lat2 - lat1))


def along_parallel(lat, lon1, lon2, R=R_EARTH_KM):
    """Distance due east or west: a SMALL circle unless lat is 0."""
    return parallel_radius(lat, R) * abs(math.radians(lon2 - lon1))


def great_circle_cosine_rule(lat1, lon1, lat2, lon2, R=R_EARTH_KM):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    cos_c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dlon)
    return R * math.acos(max(-1.0, min(1.0, cos_c)))


def great_circle_haversine(lat1, lon1, lat2, lon2, R=R_EARTH_KM):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


if __name__ == "__main__":
    print("Block 1 - the radius of a parallel shrinks as cos(latitude)")
    print("   latitude    radius km    1 deg of longitude, km")
    for lat in (0, 30, 45, 60, 80, 90):
        r = parallel_radius(lat)
        per_degree = r * math.radians(1)
        print(f"     {lat:3} N     {r:9.3f}     {per_degree:8.3f}")
    assert abs(parallel_radius(0) - R_EARTH_KM) < 1e-9
    assert abs(parallel_radius(90)) < 1e-9
    assert abs(parallel_radius(60) - R_EARTH_KM / 2) < 1e-9

    print()
    print("Block 2 - one minute of latitude is one nautical mile, anywhere")
    one_minute_km = R_EARTH_KM * math.radians(1 / 60)
    print(f"  1 minute of arc = {one_minute_km * 1000:.2f} m")
    print(f"  the nautical mile is DEFINED as {NAUTICAL_MILE_M:.0f} m")
    print(f"  difference {abs(one_minute_km * 1000 - NAUTICAL_MILE_M):.2f} m"
          " - the Earth is not a perfect sphere")
    assert abs(one_minute_km * 1000 - NAUTICAL_MILE_M) < 5
    print(f"  1 degree of latitude = {R_EARTH_KM * math.radians(1):.3f} km, everywhere")

    print()
    print("Block 3 - the parallel route is NOT the shortest")
    LAT = 60.0
    par = along_parallel(LAT, 0.0, 180.0)
    gc_cos = great_circle_cosine_rule(LAT, 0.0, LAT, 180.0)
    gc_hav = great_circle_haversine(LAT, 0.0, LAT, 180.0)
    over_pole = along_meridian(LAT, 90.0) * 2        # up to the pole and back down
    print(f"  from (60N, 0) to (60N, 180):")
    print(f"    along the parallel      {par:9.3f} km")
    print(f"    great circle (cosine)   {gc_cos:9.3f} km")
    print(f"    great circle (haversine){gc_hav:9.3f} km")
    print(f"    straight over the pole  {over_pole:9.3f} km")
    print(f"    saving {par - gc_hav:.3f} km, which is {100*(par-gc_hav)/par:.1f}%")
    assert gc_hav < par
    assert abs(gc_hav - over_pole) < 1e-6, "these two points share a polar meridian"

    print()
    print("  and for a real pair of cities:")
    LON, NYC = (51.5074, -0.1278), (40.7128, -74.0060)
    d = great_circle_haversine(LON[0], LON[1], NYC[0], NYC[1])
    print(f"    London to New York: {d:.1f} km  ({d / 1.609344:.1f} miles)")
    assert 5500 < d < 5600

    print()
    print("Block 4 - why haversine exists: the cosine rule at short range")
    print("   separation        cosine rule        haversine     disagreement")
    base_lat, base_lon = 51.5, -0.1
    for metres in (1000000.0, 10000.0, 100.0, 1.0, 0.01):
        # move north by the given distance
        dlat = math.degrees(metres / 1000.0 / R_EARTH_KM)
        c = great_circle_cosine_rule(base_lat, base_lon, base_lat + dlat, base_lon) * 1000
        h = great_circle_haversine(base_lat, base_lon, base_lat + dlat, base_lon) * 1000
        rel = abs(c - h) / metres
        print(f"  {metres:12.2f} m  {c:15.6f} m  {h:14.6f} m   {rel:10.2%}")
    # at a metre the cosine rule has lost most of its significant figures
    dlat = math.degrees(0.001 / R_EARTH_KM)
    c1 = great_circle_cosine_rule(base_lat, base_lon, base_lat + dlat, base_lon) * 1000
    h1 = great_circle_haversine(base_lat, base_lon, base_lat + dlat, base_lon) * 1000
    assert abs(h1 - 1.0) < 1e-6, h1
    assert abs(c1 - 1.0) > 1e-6, "the cosine rule should be visibly wrong here"
    print(f"  at 1 m: haversine {h1:.9f} m, cosine rule {c1:.9f} m")
    print("  haversine is exact to nanometres; the cosine rule is not")

    print()
    print("lat_long: passed")
```

Expected output:

```
Block 1 - the radius of a parallel shrinks as cos(latitude)
   latitude    radius km    1 deg of longitude, km
       0 N      6371.009      111.195
      30 N      5517.455       96.298
      45 N      4504.984       78.627
      60 N      3185.504       55.598
      80 N      1106.314       19.309
      90 N         0.000        0.000

Block 2 - one minute of latitude is one nautical mile, anywhere
  1 minute of arc = 1853.25 m
  the nautical mile is DEFINED as 1852 m
  difference 1.25 m - the Earth is not a perfect sphere
  1 degree of latitude = 111.195 km, everywhere

Block 3 - the parallel route is NOT the shortest
  from (60N, 0) to (60N, 180):
    along the parallel      10007.557 km
    great circle (cosine)    6671.705 km
    great circle (haversine) 6671.705 km
    straight over the pole   6671.705 km
    saving 3335.852 km, which is 33.3%

  and for a real pair of cities:
    London to New York: 5570.2 km  (3461.2 miles)

Block 4 - why haversine exists: the cosine rule at short range
   separation        cosine rule        haversine     disagreement
    1000000.00 m   1000000.000000 m  1000000.000000 m        0.00%
      10000.00 m     10000.000000 m    10000.000000 m        0.00%
        100.00 m        99.999999 m      100.000000 m        0.00%
          1.00 m         1.000207 m        1.000000 m        0.02%
          0.01 m         0.000000 m        0.010000 m      100.00%
  at 1 m: haversine 1.000000000 m, cosine rule 1.000206810 m
  haversine is exact to nanometres; the cosine rule is not

lat_long: passed
```

Block 4 is the practical lesson. Both formulas are correct mathematics. Only one of them survives contact with floating point at short range, and that is why every mapping library ships haversine rather than the cosine rule.

## Common pitfalls and traps

- **Forgetting the $\cos\phi$ on longitude.** A degree of latitude is the same everywhere; a degree of longitude is not. This is the single most common error in position calculations.
- **Assuming due east is the shortest way east.** It is not, except along the equator. Block 3 quantifies the difference.
- **Using the plane distance formula on latitude and longitude.** Treating $(\phi, \lambda)$ as Cartesian coordinates and applying Pythagoras is wrong everywhere except over very short distances near the equator.
- **Using the cosine rule for short distances.** Mathematically fine, numerically unusable. Use haversine.
- **Mixing up sign conventions.** South latitudes and west longitudes are negative in the usual convention. Feeding in positive values for a western longitude puts the point on the wrong side of the planet, and the answer will look plausible.
- **Treating the Earth as a sphere when precision matters.** It is an oblate spheroid, flattened by about $0.3\%$. Every result here carries that error — see the limits section.

## Check your understanding

1. Find the radius of the parallel at latitude $45°$N, taking $R = 6371$ km.
2. How far apart are two points on the same meridian at $20°$N and $50°$N?
3. How far apart are two points at $45°$N, one at $10°$E and one at $40°$E, measured along the parallel?
4. Why is one minute of latitude a fixed distance while one minute of longitude is not?
5. Two points lie on the equator, $90°$ of longitude apart. Is the route along the equator the shortest? Why does your answer differ from the $60°$N case?

<details><summary>Answers — open only after an attempt</summary>

1. $r = 6371\cos 45° = 6371 \times 0.7071 \approx 4505.3$ km.
2. Same meridian, so it is a great-circle arc of $30°$: $d = 6371 \times \frac{30\pi}{180} \approx 3336.7$ km.
3. Radius of the parallel is $6371\cos 45° \approx 4505.3$ km, and $\Delta\lambda = 30°$: $d = 4505.3 \times \frac{30\pi}{180} \approx 2359.4$ km. Note this is **less** than the answer to question 2 for the same angular span — because the parallel is a smaller circle.
4. Because meridians are all great circles of the same radius $R$, so a fixed angle always subtends a fixed arc. Parallels have radius $R\cos\phi$, which shrinks towards the poles, so the same angle of longitude covers less distance the further from the equator you are.
5. **Yes** — the equator is itself a great circle, being the only parallel whose centre is the Earth's centre. That is exactly what fails at $60°$N: that parallel is a small circle, so following it is a detour.

**And the prediction from section 4:** the alternative is to go **over the pole**, since the $0°$ and $180°$ meridians together form one great circle. That route is $60°$ of arc against the parallel's effective $180°$ on a half-size circle: about $1.047R$ against $1.571R$, so roughly a third shorter — about $6{,}672$ km against $10{,}008$ km.
</details>

## Practice — independent task

Implement `initial_bearing(lat1, lon1, lat2, lon2)` and `destination(lat, lon, bearing, distance)`.

1. **`initial_bearing`** returns the compass bearing to set off on for the great-circle route:
   $$\theta = \operatorname{atan2}\big(\sin\Delta\lambda\cos\phi_2,\ \cos\phi_1\sin\phi_2 - \sin\phi_1\cos\phi_2\cos\Delta\lambda\big)$$
   Normalise to $[0°, 360°)$ using the conventions from [[04-bearings|bearings]].
2. **`destination`** returns the point reached by travelling a given distance from a start point on a given initial bearing, along a great circle.
3. **Round-trip test:** from any start, take a bearing and distance, find the destination, then confirm the great-circle distance back to the start matches the distance you travelled, to within `1e-9` km.
4. **Demonstrate that the bearing changes along the route.** Take London to Tokyo, compute the initial bearing, then step along the great circle in twenty hops using `destination`, recomputing the bearing to Tokyo at each. Print the sequence. Explain in a comment why a constant-bearing route (a *rhumb line*) is a different and longer path.
5. Compute the rhumb-line distance for the same pair and report the penalty as a percentage.

**Edge cases:** the two points are identical (bearing is undefined — say what you return and why); the points are exactly antipodal (infinitely many great circles connect them); a start or end exactly at a pole, where longitude is meaningless.

**Done when:** your round-trip test passes for at least ten random pairs, your step-4 output shows the bearing genuinely changing, and you can state the rhumb-line penalty for London–Tokyo with a number you computed.

## Tradeoffs, limits and extensions

**The Earth is not a sphere.** It is an oblate spheroid, with an equatorial radius about $21$ km larger than the polar one — a flattening of roughly $1/298$. Spherical formulas therefore carry errors up to about $0.5\%$, which is metres over a kilometre and tens of kilometres over an intercontinental route. Where that matters, **Vincenty's formulae** or Karney's improved algorithm solve the problem on an ellipsoid, at considerably greater cost and complexity. The choice is a genuine engineering trade: haversine is a dozen lines and good to half a percent; Vincenty is iterative, occasionally fails to converge for near-antipodal points, and is good to millimetres.

**Spherical geometry is not a variant of plane geometry.** It is a different geometry. Triangle angles sum to more than $180°$, the excess being proportional to area; there are no similar triangles that are not congruent, since angles determine size; and no parallel lines exist at all. This is exactly the non-Euclidean case flagged at the end of [[01-angles-and-parallel-lines|angles and parallel lines]] — the parallel postulate fails, and everything downstream of it changes.

**Map projections must distort.** A sphere is not developable, as noted in [[02-solids|solids]], so no flat map can preserve area, angle and distance together. Mercator preserves angles — which makes a constant compass bearing a straight line, invaluable for navigation — at the cost of wildly exaggerating polar areas. That trade-off is a theorem, not a design flaw.

## Before moving on

You are done with this lesson when you can:

- Compute the radius of any parallel and say why it involves $\cos\phi$.
- Distinguish great from small circles, and predict which routes are shortest.
- Use both great-circle formulas and say when each is appropriate.
- Explain why polar flight routes exist, with numbers.

**Recap for later lookup:** parallel radius $R\cos\phi$; distance along a meridian $R\,\Delta\phi$; along a parallel $R\cos\phi\,\Delta\lambda$ — angles in radians; meridians and the equator are great circles, other parallels are not; spherical cosine rule $\cos c = \sin\phi_1\sin\phi_2 + \cos\phi_1\cos\phi_2\cos\Delta\lambda$; use **haversine** in code; $1$ minute of great-circle arc $= 1$ nautical mile $= 1852$ m.

**Next:** [[01-lines-and-planes|Lines and Planes in Space]] — leaving the surface entirely for full three-dimensional coordinate geometry.

## Related

- [[04-bearings|Bearings]] — the flat-Earth version, and its limits
- [[03-sine-and-cosine-rules|Sine and Cosine Rules]] — the plane originals of the spherical formulas
- [[02-solids|Solids]] — why a sphere cannot be flattened
- [[01-angles-and-parallel-lines|Angles and Parallel Lines]] — the parallel postulate that fails here
