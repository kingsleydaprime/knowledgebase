# Trigonometric Ratios and Right Triangles

**[Beginner]** — why a ratio of two sides depends only on an angle, and how that one fact lets you measure things you cannot reach.

## Before you start

- You know similar triangles and the AA criterion — [[02-triangles-and-polygons|triangles and polygons]].
- You know Pythagoras' theorem.
- Helpful: the equilateral and perpendicular constructions, which section 4 uses to derive exact values — [[03-constructions|constructions]].

**What you will be able to do after this lesson:**

1. Explain *why* $\sin$, $\cos$ and $\tan$ are well defined — that is, why the ratio does not depend on the size of the triangle.
2. Derive the exact values for $30°$, $45°$ and $60°$ from two constructed triangles, rather than memorising a table.
3. Prove $\sin^2\theta + \cos^2\theta = 1$ and $\tan\theta = \frac{\sin\theta}{\cos\theta}$ from the definitions.
4. Solve angle-of-elevation and depression problems, including the two-observation case where the distance is unknown.

**Study route:** read 1–5, attempt the prediction in section 5, then run the lab. Do the practice task before moving to graphs.

---

## 1. Why this exists

You need the height of a tree. You cannot climb it and you cannot lay a tape up it. You *can* stand somewhere, measure your distance from the base, and measure the angle from horizontal up to the top.

[[02-triangles-and-polygons|Similar triangles]] already told us that a stick and its shadow can give the tree's height, if the sun cooperates. Trigonometry removes the dependency on the sun: it tabulates, once and for all, what the ratio of sides is **for every angle**. Then a single angle measurement plus a single distance gives the height.

The whole subject rests on one observation, which is worth stating before any notation:

> In a right triangle, once you fix one of the non-right angles, **the shape is fixed**. Every triangle with that angle is a scaled copy of every other. So the ratio of any two sides is determined by the angle alone — it does not matter how big the triangle is.

That is the AA similarity criterion, applied to right triangles. Everything below is bookkeeping on top of it.

## 2. Terminology

Fix one non-right angle $\theta$. The three sides then get names **relative to that angle**:

```
                    /|
                   / |
      hypotenuse  /  |  opposite
                 /   |     (opposite theta)
                / θ  |
               /_____|
              adjacent
```

| Term | Plain-English definition | Warning |
| :--- | :--- | :--- |
| **Hypotenuse** | The side opposite the right angle | Always the longest; never changes name |
| **Opposite** | The side facing $\theta$ | **Swaps** if you switch to the other angle |
| **Adjacent** | The side next to $\theta$ that is not the hypotenuse | Also swaps |
| **$\sin\theta$** | opposite / hypotenuse | — |
| **$\cos\theta$** | adjacent / hypotenuse | — |
| **$\tan\theta$** | opposite / adjacent | — |
| **Angle of elevation** | The angle *up* from horizontal to a line of sight | Measured from the horizontal, not the vertical |
| **Angle of depression** | The angle *down* from horizontal | Equal to the elevation seen from the other end — alternate angles |

The mnemonic **SOH-CAH-TOA** encodes the three definitions. It is a memory aid, not a reason; the reason is section 1.

> [!WARNING]
> "Opposite" and "adjacent" are defined **with respect to the angle you chose**. Switch to the other non-right angle and they exchange. This is the single most common source of wrong answers: $\sin$ of one angle equals $\cos$ of the other, and using the wrong one silently gives a plausible number.

## 3. The ratios are functions of the angle

Take a right triangle with $\theta = 30°$ and legs of some size. Double every side. Triple them. The angles are unchanged — scaling preserves angle — so all these triangles are similar, and corresponding side ratios are equal:

$$
\frac{\text{opp}}{\text{hyp}} = \frac{2 \times \text{opp}}{2 \times \text{hyp}} = \frac{3 \times \text{opp}}{3 \times \text{hyp}}
$$

So $\sin 30°$ is a **number**, not a property of a particular triangle. That is what licenses writing $\sin$ as a function. Block 1 of the lab checks this over several scale factors.

## 4. Exact values, derived not memorised

Two triangles are constructible with compass and straightedge, and between them they give every "nice" angle.

### The $45°$ triangle — half a square

Take a unit square and draw a diagonal. The two triangles are isosceles right triangles with legs $1$ and, by Pythagoras, hypotenuse $\sqrt{2}$. The non-right angles are equal and sum to $90°$, so each is $45°$:

$$
\sin 45° = \frac{1}{\sqrt2}, \qquad \cos 45° = \frac{1}{\sqrt2}, \qquad \tan 45° = 1
$$

### The $30°$–$60°$ triangle — half an equilateral triangle

Take the equilateral triangle of side $2$ constructed in [[03-constructions|constructions]], and drop a perpendicular from the apex. It bisects the base (SSS congruence), giving a right triangle with hypotenuse $2$, short leg $1$, and by Pythagoras the third side $\sqrt{4-1} = \sqrt3$.

The bisected apex angle is $30°$; the base angle is still $60°$:

$$
\sin 30° = \frac{1}{2}, \quad \cos 30° = \frac{\sqrt3}{2}, \quad \tan 30° = \frac{1}{\sqrt3}
$$
$$
\sin 60° = \frac{\sqrt3}{2}, \quad \cos 60° = \frac{1}{2}, \quad \tan 60° = \sqrt3
$$

Notice $\sin 30° = \cos 60°$ and $\sin 60° = \cos 30°$. That is not a coincidence — it is the opposite/adjacent swap of section 2, and in general:

$$
\sin\theta = \cos(90° - \theta)
$$

which is where the "co" in cosine comes from: the sine of the **co**mplementary angle.

### Two identities that come free

Let the hypotenuse be $h$, opposite $o$, adjacent $a$. Pythagoras says $o^2 + a^2 = h^2$. Divide through by $h^2$:

$$
\left(\frac{o}{h}\right)^2 + \left(\frac{a}{h}\right)^2 = 1 \quad\Longrightarrow\quad \sin^2\theta + \cos^2\theta = 1
$$

And directly from the definitions:

$$
\frac{\sin\theta}{\cos\theta} = \frac{o/h}{a/h} = \frac{o}{a} = \tan\theta
$$

Both are Pythagoras and division, nothing more. $\sin^2\theta$ means $(\sin\theta)^2$, a notation that exists only to avoid writing brackets everywhere.

## 5. Elevation, depression, and the unknown-distance case

**One observation.** Standing $d$ from the base, measuring elevation $\theta$ to the top, with eye height $e$:

$$
\text{height} = d\tan\theta + e
$$

Forgetting $e$ is the standard error. The triangle sits on your eye, not on the ground.

**Two observations.** Now suppose you cannot measure $d$ — the base is inside a fenced compound. Take the elevation $\alpha$ from where you stand, walk **directly away** a measured distance $k$, and take a second elevation $\beta$ (necessarily smaller). Then with $h$ the height above eye level:

$$
h = d\tan\alpha \qquad\text{and}\qquad h = (d + k)\tan\beta
$$

Two equations, two unknowns. Eliminating $d$:

$$
h = \frac{k \tan\alpha \tan\beta}{\tan\alpha - \tan\beta}
$$

This is the workhorse of practical surveying, and it needs no access to the base at all.

> [!TIP]
> **Predict before running the lab.** In that last formula, what happens as $\alpha$ and $\beta$ get closer together? What does that mean physically — and what does it tell you about how far apart your two observation points should be? Decide before opening the answers.

## Worked example — runnable

**Runnable example:** save as `trig_ratios.py` in any empty directory and run `python3 trig_ratios.py`. Standard library only; writes no files.

```python
"""Trigonometric ratios: why they are well defined, and what they measure."""
import math

EPS = 1e-12


def ratios(opposite, adjacent):
    """sin, cos, tan for the angle whose opposite and adjacent are given."""
    hyp = math.hypot(opposite, adjacent)
    return (opposite / hyp, adjacent / hyp, opposite / adjacent)


def height_one_observation(distance, elevation_deg, eye_height=0.0):
    return distance * math.tan(math.radians(elevation_deg)) + eye_height


def height_two_observations(step_back, alpha_deg, beta_deg, eye_height=0.0):
    """Height when the distance to the base cannot be measured."""
    ta = math.tan(math.radians(alpha_deg))
    tb = math.tan(math.radians(beta_deg))
    if abs(ta - tb) < 1e-12:
        raise ValueError("the two elevations are indistinguishable")
    return step_back * ta * tb / (ta - tb) + eye_height


if __name__ == "__main__":
    print("Block 1 - the ratio depends on the angle, not the size")
    base_opp, base_adj = 3.0, 4.0            # the 3-4-5 triangle
    for scale in (1, 2, 7, 100, 0.01):
        s, c, t = ratios(base_opp * scale, base_adj * scale)
        print(f"  scale {scale:>6}: sin={s:.10f} cos={c:.10f} tan={t:.10f}")
        assert abs(s - 0.6) < EPS and abs(c - 0.8) < EPS and abs(t - 0.75) < EPS

    print()
    print("Block 2 - exact values, derived from the two constructed triangles")
    print("  from half a unit square (legs 1, 1, hypotenuse sqrt2):")
    s45, c45, t45 = ratios(1.0, 1.0)
    print(f"    sin45={s45:.10f}  1/sqrt2={1/math.sqrt(2):.10f}")
    print(f"    tan45={t45:.10f}")
    assert abs(s45 - 1 / math.sqrt(2)) < EPS and abs(t45 - 1.0) < EPS

    print("  from half an equilateral triangle of side 2 (legs 1, sqrt3):")
    s30, c30, t30 = ratios(1.0, math.sqrt(3))     # angle 30: opposite 1
    s60, c60, t60 = ratios(math.sqrt(3), 1.0)     # angle 60: opposite sqrt3
    print(f"    sin30={s30:.10f} (= 1/2)      cos30={c30:.10f} (= sqrt3/2)")
    print(f"    sin60={s60:.10f} (= sqrt3/2)  cos60={c60:.10f} (= 1/2)")
    assert abs(s30 - 0.5) < EPS
    assert abs(c30 - math.sqrt(3) / 2) < EPS
    assert abs(s60 - math.sqrt(3) / 2) < EPS
    assert abs(c60 - 0.5) < EPS
    # the complementary relation
    assert abs(s30 - c60) < EPS and abs(s60 - c30) < EPS
    print("    sin(theta) = cos(90 - theta): confirmed for 30 and 60")

    print()
    print("Block 3 - the two identities")
    for angle in (0, 17, 30, 45, 60, 73, 89):
        r = math.radians(angle)
        pyth = math.sin(r) ** 2 + math.cos(r) ** 2
        assert abs(pyth - 1) < EPS
        if angle != 90:
            assert abs(math.tan(r) - math.sin(r) / math.cos(r)) < EPS
    print("  sin^2 + cos^2 = 1 and tan = sin/cos hold for every angle tried")

    print()
    print("Block 4 - measuring a tree you cannot climb")
    # A tree whose true height we fix, so the recovered value can be checked.
    TRUE_HEIGHT, EYE, DISTANCE = 18.0, 1.6, 25.0
    elevation = math.degrees(math.atan((TRUE_HEIGHT - EYE) / DISTANCE))
    print(f"  true height {TRUE_HEIGHT} m, eye {EYE} m, standing {DISTANCE} m away")
    print(f"  -> elevation would read {elevation:.4f} degrees")
    recovered = height_one_observation(DISTANCE, elevation, EYE)
    print(f"  recovered height = {recovered:.6f} m")
    assert abs(recovered - TRUE_HEIGHT) < 1e-9

    forgot_eye = height_one_observation(DISTANCE, elevation)
    print(f"  forgetting eye height gives {forgot_eye:.6f} m - short by exactly {EYE} m")
    assert abs((TRUE_HEIGHT - forgot_eye) - EYE) < 1e-9

    print()
    print("Block 5 - when the distance to the base cannot be measured")
    STEP = 15.0
    alpha = math.degrees(math.atan((TRUE_HEIGHT - EYE) / DISTANCE))
    beta = math.degrees(math.atan((TRUE_HEIGHT - EYE) / (DISTANCE + STEP)))
    print(f"  elevations {alpha:.4f} and {beta:.4f} degrees, {STEP} m apart")
    two_obs = height_two_observations(STEP, alpha, beta, EYE)
    print(f"  recovered height = {two_obs:.6f} m  (base never measured)")
    assert abs(two_obs - TRUE_HEIGHT) < 1e-9

    print("  sensitivity: how a 0.1 degree error in beta moves the answer")
    for err in (0.0, 0.1, -0.1):
        h = height_two_observations(STEP, alpha, beta + err, EYE)
        print(f"    beta error {err:+.1f} deg -> height {h:8.4f} m  ({h - TRUE_HEIGHT:+.4f})")

    print()
    print("trig_ratios: passed")
```

Expected output:

```
Block 1 - the ratio depends on the angle, not the size
  scale      1: sin=0.6000000000 cos=0.8000000000 tan=0.7500000000
  scale      2: sin=0.6000000000 cos=0.8000000000 tan=0.7500000000
  scale      7: sin=0.6000000000 cos=0.8000000000 tan=0.7500000000
  scale    100: sin=0.6000000000 cos=0.8000000000 tan=0.7500000000
  scale   0.01: sin=0.6000000000 cos=0.8000000000 tan=0.7500000000

Block 2 - exact values, derived from the two constructed triangles
  from half a unit square (legs 1, 1, hypotenuse sqrt2):
    sin45=0.7071067812  1/sqrt2=0.7071067812
    tan45=1.0000000000
  from half an equilateral triangle of side 2 (legs 1, sqrt3):
    sin30=0.5000000000 (= 1/2)      cos30=0.8660254038 (= sqrt3/2)
    sin60=0.8660254038 (= sqrt3/2)  cos60=0.5000000000 (= 1/2)
    sin(theta) = cos(90 - theta): confirmed for 30 and 60

Block 3 - the two identities
  sin^2 + cos^2 = 1 and tan = sin/cos hold for every angle tried

Block 4 - measuring a tree you cannot climb
  true height 18.0 m, eye 1.6 m, standing 25.0 m away
  -> elevation would read 33.2649 degrees
  recovered height = 18.000000 m
  forgetting eye height gives 16.400000 m - short by exactly 1.6 m

Block 5 - when the distance to the base cannot be measured
  elevations 33.2649 and 22.2936 degrees, 15.0 m apart
  recovered height = 18.000000 m  (base never measured)
  sensitivity: how a 0.1 degree error in beta moves the answer
    beta error +0.0 deg -> height  18.0000 m  (+0.0000)
    beta error +0.1 deg -> height  18.2194 m  (+0.2194)
    beta error -0.1 deg -> height  17.7845 m  (-0.2155)

trig_ratios: passed
```

The last three lines are worth more than the rest. A tenth of a degree — finer than most hand-held instruments resolve — shifts the answer by about $0.22$ m on an $18$ m tree, roughly $1.2\%$. The formula is exact; the measurement is not, and the arithmetic **amplifies** the error. Move the two observation points closer together and this gets rapidly worse, which is what the prediction in section 5 was about.

## Common pitfalls and traps

- **Swapping opposite and adjacent.** They are named relative to the chosen angle. Redraw and relabel for the angle you are actually using, every time.
- **Degrees versus radians.** Python's `math.sin` takes **radians**. `math.sin(30)` is the sine of $30$ radians, which is $-0.988$ — a perfectly plausible-looking wrong number. Every angle in the lab passes through `math.radians` first.
- **Forgetting eye height.** The lab quantifies this: the answer is short by exactly the eye height, every time.
- **Assuming the ground is level.** $d\tan\theta$ measures height above the *observer's eye level*, not above the base of the tree, if the two are at different elevations.
- **Using $\tan 90°$.** It is undefined — the adjacent side has length zero. In floating point `math.tan(math.radians(90))` returns about $1.6\times10^{16}$ rather than raising, which is a silent trap.
- **Treating an exact formula as an exact answer.** Block 5's sensitivity check is the honest part of the lesson. The mathematics carries no error; the protractor does.

## Check your understanding

1. In a right triangle, the side opposite $\theta$ is $7$ and the hypotenuse is $25$. Find $\sin\theta$, $\cos\theta$ and $\tan\theta$ exactly.
2. Without a calculator, find $\tan 60° \times \tan 30°$. Explain the result.
3. A ladder $6$ m long leans against a wall at $70°$ to the ground. How far up the wall does it reach, and how far is its foot from the wall?
4. From the top of a cliff $80$ m high, the angle of depression to a boat is $25°$. How far is the boat from the base of the cliff?
5. Why is $\sin\theta$ never greater than $1$?

<details><summary>Answers — open only after an attempt</summary>

1. The adjacent side is $\sqrt{25^2 - 7^2} = \sqrt{625 - 49} = \sqrt{576} = 24$. So $\sin\theta = \frac{7}{25}$, $\cos\theta = \frac{24}{25}$, $\tan\theta = \frac{7}{24}$.
2. $\sqrt3 \times \frac{1}{\sqrt3} = 1$. It happens because $30°$ and $60°$ are complementary: $\tan(90° - \theta) = \frac{1}{\tan\theta}$, since the opposite and adjacent swap.
3. Height up the wall $= 6\sin 70° \approx 5.638$ m. Distance of the foot $= 6\cos 70° \approx 2.052$ m.
4. The angle of depression from the cliff equals the angle of elevation from the boat — alternate angles between two horizontals. So $\tan 25° = \frac{80}{d}$, giving $d = \frac{80}{\tan 25°} \approx 171.6$ m.
5. Because $\sin\theta = \frac{\text{opposite}}{\text{hypotenuse}}$, and the hypotenuse is the longest side of a right triangle. A fraction whose denominator is at least as large as its numerator cannot exceed $1$, with equality only in the degenerate case where the triangle collapses.

**And the prediction from section 5:** as $\alpha \to \beta$, the denominator $\tan\alpha - \tan\beta \to 0$ and the computed height blows up. Physically, two nearly-equal elevations carry almost no information about the distance — you have barely moved relative to the object. So the two observation points must be **far enough apart** that the elevation difference is comfortably larger than your measurement error. Block 5's sensitivity numbers show what "comfortably" has to mean.
</details>

## Practice — independent task

Implement `tower_height(observations, eye_height)` where `observations` is a list of `(distance_walked, elevation_degrees)` pairs taken by walking directly away from an object in a straight line, with the first entry at distance $0$.

1. With **two** observations, use the formula from section 5.
2. With **more than two**, do better than picking two: each pair $(k_i, \alpha_i)$ gives $\frac{h}{\tan\alpha_i} - k_i = d$, which is linear in $h$. Fit $h$ by least squares over all observations, and return both the estimate and a measure of spread.
3. Assert that with **noise-free** synthetic data your estimate recovers the true height to within `1e-9`, for at least three different true heights.
4. Then add Gaussian noise of $0.1°$ to the elevations, using a **fixed seed**, and report how the error behaves as the number of observations grows from 2 to 20.
5. Answer in a comment: does the error shrink like $1/n$, like $1/\sqrt{n}$, or not at all? Say which you observed.

**Edge cases:** two identical elevations (raise, do not divide by zero); an elevation of $0°$ or $90°$; observations taken while walking *towards* the object, so the step is negative.

**Done when:** the noise-free assertions pass, your noisy experiment is reproducible from its seed, and your answer to step 5 is based on numbers you produced rather than on what you expected.

## Tradeoffs, limits and extensions

**These definitions only cover $0° < \theta < 90°$.** A right triangle cannot contain an obtuse angle, so nothing above says what $\sin 120°$ means. Extending the definitions to every angle — including negative and reflex — requires the **unit circle**, which is the first section of [[02-graphs-and-identities|graphs and identities]]. The extension is designed so that all the identities here survive unchanged.

**Right triangles are a special case.** For a triangle with no right angle, none of SOH-CAH-TOA applies. The general tools are the sine and cosine rules in [[03-sine-and-cosine-rules|sine and cosine rules]], and both are derived by dropping a perpendicular to *create* right triangles — so this lesson remains the foundation.

**Accuracy in practice.** Surveying instruments quote angular accuracy in *seconds* of arc for this reason. The trigonometry is exact; the answer is only as good as the angle, and as block 5 shows, the amplification factor depends on the geometry you chose.

## Before moving on

You are done with this lesson when you can:

- Explain why $\sin 30°$ is a number rather than a fact about one triangle.
- Reconstruct the exact values for $30°$, $45°$, $60°$ by drawing the two triangles, without a table.
- Derive $\sin^2 + \cos^2 = 1$ from Pythagoras in one line.
- Solve a two-observation elevation problem and say how sensitive the answer is to angle error.

**Recap for later lookup:** $\sin = \frac{\text{opp}}{\text{hyp}}$, $\cos = \frac{\text{adj}}{\text{hyp}}$, $\tan = \frac{\text{opp}}{\text{adj}}$; $\sin^2\theta + \cos^2\theta = 1$; $\tan\theta = \frac{\sin\theta}{\cos\theta}$; $\sin\theta = \cos(90° - \theta)$; exact values from half a square ($45°$) and half an equilateral triangle ($30°$, $60°$); two-observation height $= \frac{k\tan\alpha\tan\beta}{\tan\alpha - \tan\beta}$.

**Next:** [[02-graphs-and-identities|Graphs and Identities]] — extending these three ratios from acute angles to every angle, using the unit circle.

## Related

- [[02-triangles-and-polygons|Triangles and Polygons]] — the similarity result the whole subject rests on
- [[03-constructions|Constructions]] — where the two exact-value triangles come from
- [[03-sine-and-cosine-rules|Sine and Cosine Rules]] — triangles without a right angle
- [[04-bearings|Bearings]] — these ratios applied to navigation
