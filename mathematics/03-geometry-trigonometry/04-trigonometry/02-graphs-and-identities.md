# Trigonometric Graphs and Identities

**[Intermediate]** — extending three ratios from acute angles to every angle, and the identities that survive the extension.

## Before you start

- You know $\sin$, $\cos$, $\tan$ for acute angles, and $\sin^2 + \cos^2 = 1$ — [[01-ratios-and-right-triangles|trigonometric ratios]].
- You can work with coordinates and the circle equation — [[03-coordinate-geometry/01-coordinate-geometry|coordinate geometry]].

**What you will be able to do after this lesson:**

1. Define $\sin$, $\cos$ and $\tan$ for **any** angle using the unit circle, and show the definition agrees with the right-triangle one where both apply.
2. Determine the sign of each ratio in each quadrant without memorising a mnemonic.
3. Derive the addition formula for $\cos(A - B)$, and obtain the double-angle formulas from it.
4. Solve a trigonometric equation over a stated range and find **all** solutions, not just the one your calculator returns.

**Study route:** read 1–5. Attempt the prediction in section 5 before section 6. Run the lab — its plot block makes periodicity visible.

---

## 1. Why this exists

The right-triangle definitions have a hard ceiling: a right triangle cannot contain an angle of $90°$ or more, so $\sin 120°$ is undefined by them. That is awkward, because obtuse angles occur constantly — in a triangle with an obtuse vertex, in a bearing of $200°$, in a rotation of $450°$.

There is a second, larger reason. Almost everything that **repeats** is described by these functions: alternating current, sound pressure, tides, orbits, a pendulum, the vibration of a string. None of those is a triangle. What they share is *periodicity*, and to describe periodicity you need a definition of $\sin$ that keeps going past $90°$ and repeats forever.

So the definition gets rebuilt on a circle instead of a triangle — in a way that keeps every acute-angle value exactly as it was.

## 2. The unit circle definition

Draw the circle of radius $1$ centred at the origin. Start at $(1, 0)$ and rotate anticlockwise through an angle $\theta$. You land at some point $P$. **Define:**

$$
\cos\theta = x\text{-coordinate of } P, \qquad \sin\theta = y\text{-coordinate of } P, \qquad \tan\theta = \frac{\sin\theta}{\cos\theta}
$$

```
                   y
                   |
             P=(cos θ, sin θ)
                 . |
              .    |
           .       | sin θ
        .  θ       |
     ---+----------+------ x
        O   cos θ
```

**Why this agrees with the old definition.** For acute $\theta$, drop a perpendicular from $P$ to the $x$-axis. You get a right triangle with hypotenuse $1$ (the radius), adjacent $x$, opposite $y$. So:

$$
\cos\theta = \frac{\text{adj}}{\text{hyp}} = \frac{x}{1} = x, \qquad \sin\theta = \frac{\text{opp}}{\text{hyp}} = \frac{y}{1} = y
$$

Identical. The new definition is a genuine **extension**: it adds meaning for angles the old one could not handle, and changes nothing where the old one worked. Block 1 of the lab checks this over many acute angles.

Two facts now come for free:

- **$\sin^2\theta + \cos^2\theta = 1$ for every angle**, because $(x, y)$ is on the unit circle and $x^2 + y^2 = 1$ is the circle's equation. The identity is no longer a consequence of Pythagoras in a triangle; it *is* the circle equation.
- **Everything repeats every $360°$**, because rotating a full turn returns you to the same point.

## 3. Signs by quadrant

The sign of $\sin$ and $\cos$ is just the sign of the coordinate, so no memorisation is needed — only knowing which quadrant you are in.

| Quadrant | Angle range | $x = \cos$ | $y = \sin$ | $\tan = y/x$ | Positive there |
| :--- | :--- | :---: | :---: | :---: | :--- |
| I | $0°$–$90°$ | $+$ | $+$ | $+$ | **A**ll |
| II | $90°$–$180°$ | $-$ | $+$ | $-$ | **S**ine |
| III | $180°$–$270°$ | $-$ | $-$ | $+$ | **T**angent |
| IV | $270°$–$360°$ | $+$ | $-$ | $-$ | **C**osine |

Reading the last column upwards from quadrant IV gives **CAST**. Useful, but the table's middle columns are the reason, and they are just "which way is the point from the origin".

### Radians

Degrees are arbitrary — $360$ was chosen by Babylonian astronomers, not by mathematics. The natural unit measures an angle by the **arc length it cuts on the unit circle**:

$$
\theta \text{ in radians} = \frac{\text{arc length}}{\text{radius}}
$$

A full turn is a circumference of $2\pi$, so:

$$
360° = 2\pi \text{ rad}, \qquad 180° = \pi, \qquad 90° = \frac{\pi}{2}, \qquad 1 \text{ rad} = \frac{180°}{\pi} \approx 57.2958°
$$

Radians are not merely another scale. Arc length becomes $r\theta$ and sector area $\tfrac12 r^2\theta$ with no conversion constant, and — the reason they take over completely later — the derivative of $\sin$ is $\cos$ **only** in radians. In degrees an extra factor of $\pi/180$ appears and never leaves.

## 4. The graphs

| Function | Period | Range | Notable feature |
| :--- | :--- | :--- | :--- |
| $y = \sin\theta$ | $360°$ ($2\pi$) | $[-1, 1]$ | Zero at $0°$, rising |
| $y = \cos\theta$ | $360°$ ($2\pi$) | $[-1, 1]$ | The sine curve shifted left by $90°$ |
| $y = \tan\theta$ | $180°$ ($\pi$) | all reals | Vertical asymptotes where $\cos\theta = 0$ |

$\tan$ has half the period of the other two because $\tan\theta = \frac{y}{x}$, and rotating by $180°$ negates **both** $x$ and $y$, leaving the ratio unchanged.

The lab prints the sine curve as text, which makes the period and range visible without a plotting library.

### Transformations

For $y = a\sin\!\big(b(\theta - c)\big) + d$:

| Parameter | Effect | Value |
| :--- | :--- | :--- |
| $a$ | **Amplitude** — vertical stretch | Range becomes $[d - \lvert a\rvert,\ d + \lvert a\rvert]$ |
| $b$ | Horizontal compression | Period becomes $\dfrac{360°}{\lvert b\rvert}$ |
| $c$ | **Phase shift** — horizontal translation | Right by $c$ |
| $d$ | Vertical translation | Centre line moves to $y = d$ |

The most common error is reading the phase shift off $\sin(2\theta - 60°)$ as $60°$. Factorise first: $\sin\big(2(\theta - 30°)\big)$, so the shift is $30°$.

## 5. The identities, derived

### From symmetry of the circle

Reflecting the point $P$ gives three relations directly:

$$
\sin(-\theta) = -\sin\theta, \qquad \cos(-\theta) = \cos\theta
$$
$$
\sin(180° - \theta) = \sin\theta, \qquad \cos(180° - \theta) = -\cos\theta
$$

The first pair says $\cos$ is symmetric about the $y$-axis and $\sin$ is antisymmetric. The second pair matters enormously in practice: it is **why a calculator's $\sin^{-1}$ gives you only half the answers**, and it is the source of the ambiguous case in [[03-sine-and-cosine-rules|the sine rule]].

### The addition formula, derived

Take two points on the unit circle, $P$ at angle $A$ and $Q$ at angle $B$:

$$
P = (\cos A, \sin A), \qquad Q = (\cos B, \sin B)
$$

Compute $PQ^2$ **two ways**.

*By coordinates,* using the distance formula:

$$
PQ^2 = (\cos A - \cos B)^2 + (\sin A - \sin B)^2
$$
$$
= \cos^2 A - 2\cos A\cos B + \cos^2 B + \sin^2 A - 2\sin A \sin B + \sin^2 B
$$

Group the squares and use $\sin^2 + \cos^2 = 1$ twice:

$$
PQ^2 = 2 - 2(\cos A \cos B + \sin A \sin B)
$$

*By the cosine rule* in triangle $OPQ$, where $OP = OQ = 1$ and the angle between them is $A - B$:

$$
PQ^2 = 1^2 + 1^2 - 2(1)(1)\cos(A - B) = 2 - 2\cos(A-B)
$$

Setting the two expressions equal and cancelling:

$$
\boxed{\cos(A - B) = \cos A \cos B + \sin A \sin B}
$$

Every other addition formula follows by substitution. Replace $B$ with $-B$ and use the symmetry relations:

$$
\cos(A + B) = \cos A \cos B - \sin A \sin B
$$

Put $A = B$ into that:

$$
\cos 2A = \cos^2 A - \sin^2 A = 2\cos^2 A - 1 = 1 - 2\sin^2 A
$$

And the sine versions come from $\sin\theta = \cos(90° - \theta)$:

$$
\sin(A + B) = \sin A \cos B + \cos A \sin B, \qquad \sin 2A = 2 \sin A \cos A
$$

> [!TIP]
> **Predict before section 6.** Solve $\sin\theta = 0.5$ for $0° \le \theta < 360°$. A calculator gives one answer. How many are there in that range, and how would you find the others from the symmetry relations above? Decide before opening the answers.

## 6. Solving trigonometric equations

A calculator's inverse functions return a **single** value from a restricted range — $\sin^{-1}$ from $[-90°, 90°]$, $\cos^{-1}$ from $[0°, 180°]$, $\tan^{-1}$ from $(-90°, 90°)$. They have to, because the functions are not one-to-one and an inverse must return one value.

So the procedure is always:

1. Get the **principal value** from the calculator.
2. Use the symmetry relations to find the **second** solution in one revolution:
   - For $\sin$: the other is $180° - \theta_1$.
   - For $\cos$: the other is $360° - \theta_1$.
   - For $\tan$: the other is $\theta_1 + 180°$.
3. Add multiples of the period ($360°$ for $\sin$, $\cos$; $180°$ for $\tan$) until you leave the required range.
4. Discard anything outside the range.

**Worked example.** Solve $2\sin\theta = 1$ for $0° \le \theta < 360°$.

$\sin\theta = 0.5$. The principal value is $\theta_1 = 30°$. The second is $180° - 30° = 150°$. Adding $360°$ to either leaves the range. So the solutions are $\{30°, 150°\}$.

## Worked example — runnable

**Runnable example:** save as `trig_graphs.py` in any empty directory and run `python3 trig_graphs.py`. Standard library only; writes no files.

```python
"""The unit circle definition, its identities, and solving equations."""
import math

EPS = 1e-12


def unit_circle_point(theta_deg):
    t = math.radians(theta_deg)
    return (math.cos(t), math.sin(t))


def quadrant(theta_deg):
    return int((theta_deg % 360) // 90) + 1


def solve_sin(value, lo=0.0, hi=360.0):
    """Every theta in [lo, hi) with sin(theta) = value."""
    if abs(value) > 1:
        return []
    principal = math.degrees(math.asin(value))
    out = []
    for base in (principal, 180 - principal):
        k = math.ceil((lo - base) / 360)
        theta = base + 360 * k
        while theta < hi:
            out.append(theta)
            theta += 360
    return sorted(set(round(t, 9) for t in out))


def ascii_plot(f, lo, hi, steps=72, height=9):
    """A text plot of f over [lo, hi], for looking at period and range."""
    rows = []
    values = [f(lo + (hi - lo) * i / steps) for i in range(steps + 1)]
    for r in range(height, -height - 1, -1):
        level = r / height
        row = "".join("*" if abs(v - level) < (1 / height) else
                      ("-" if abs(level) < EPS else " ") for v in values)
        rows.append(f"{level:+5.2f} |{row}")
    return "\n".join(rows)


if __name__ == "__main__":
    print("Block 1 - the unit circle agrees with the right-triangle ratios")
    for theta in (5, 17, 30, 45, 60, 73, 89):
        x, y = unit_circle_point(theta)
        # right-triangle ratios in the triangle with hypotenuse 1
        assert abs(math.sin(math.radians(theta)) - y) < EPS
        assert abs(math.cos(math.radians(theta)) - x) < EPS
        assert abs(x * x + y * y - 1) < EPS
    print("  for every acute angle tried, cos = x, sin = y, and x^2 + y^2 = 1")

    print()
    print("Block 2 - signs by quadrant")
    print("  angle  quadrant     cos       sin       tan")
    for theta in (45, 135, 225, 315):
        x, y = unit_circle_point(theta)
        print(f"  {theta:5}      {quadrant(theta)}     {x:+.4f}   {y:+.4f}   {y/x:+.4f}")
    assert unit_circle_point(135)[0] < 0 < unit_circle_point(135)[1]   # II: sin only
    assert unit_circle_point(225)[0] < 0 and unit_circle_point(225)[1] < 0
    assert unit_circle_point(315)[0] > 0 > unit_circle_point(315)[1]   # IV: cos only

    print()
    print("Block 3 - periodicity")
    for theta in (0, 37, 128, 264):
        assert abs(math.sin(math.radians(theta)) - math.sin(math.radians(theta + 360))) < EPS
        assert abs(math.cos(math.radians(theta)) - math.cos(math.radians(theta + 360))) < EPS
        assert abs(math.tan(math.radians(theta)) - math.tan(math.radians(theta + 180))) < 1e-9
    print("  sin and cos repeat every 360 degrees; tan repeats every 180")

    print()
    print("Block 4 - identities, checked against their derivations")
    for A, B in [(30, 45), (17, 128), (200, 95), (-40, 310)]:
        ra, rb = math.radians(A), math.radians(B)
        lhs = math.cos(math.radians(A - B))
        rhs = math.cos(ra) * math.cos(rb) + math.sin(ra) * math.sin(rb)
        assert abs(lhs - rhs) < EPS, (A, B)
        lhs2 = math.sin(math.radians(A + B))
        rhs2 = math.sin(ra) * math.cos(rb) + math.cos(ra) * math.sin(rb)
        assert abs(lhs2 - rhs2) < EPS
        assert abs(math.cos(2 * ra) - (1 - 2 * math.sin(ra) ** 2)) < EPS
        assert abs(math.sin(2 * ra) - 2 * math.sin(ra) * math.cos(ra)) < EPS
    print("  cos(A-B), sin(A+B), cos(2A) and sin(2A) hold for every pair tried")
    for theta in (0, 30, 90, 137, 250):
        r = math.radians(theta)
        assert abs(math.sin(math.radians(180 - theta)) - math.sin(r)) < EPS
        assert abs(math.cos(math.radians(180 - theta)) + math.cos(r)) < EPS
    print("  sin(180-x) = sin(x) and cos(180-x) = -cos(x): confirmed")

    print()
    print("Block 5 - solving 2 sin(theta) = 1 on [0, 360)")
    solutions = solve_sin(0.5)
    print(f"  calculator principal value: {math.degrees(math.asin(0.5)):.4f}")
    print(f"  all solutions found:        {solutions}")
    assert solutions == [30.0, 150.0]
    for t in solutions:
        assert abs(2 * math.sin(math.radians(t)) - 1) < 1e-9
    print(f"  sin(theta) = -0.5 on [0,360): {solve_sin(-0.5)}")
    print(f"  sin(theta) = 1    on [0,360): {solve_sin(1.0)}")
    print(f"  sin(theta) = 2    on [0,360): {solve_sin(2.0)}  (impossible)")
    assert solve_sin(2.0) == []

    print()
    print("Block 6 - y = sin(theta) over two full periods")
    print(ascii_plot(lambda d: math.sin(math.radians(d)), 0, 720))
    print("        0" + " " * 34 + "360" + " " * 33 + "720")

    print()
    print("trig_graphs: passed")
```

Expected output:

```
Block 1 - the unit circle agrees with the right-triangle ratios
  for every acute angle tried, cos = x, sin = y, and x^2 + y^2 = 1

Block 2 - signs by quadrant
  angle  quadrant     cos       sin       tan
     45      1     +0.7071   +0.7071   +1.0000
    135      2     -0.7071   +0.7071   -1.0000
    225      3     -0.7071   -0.7071   +1.0000
    315      4     +0.7071   -0.7071   -1.0000

Block 3 - periodicity
  sin and cos repeat every 360 degrees; tan repeats every 180

Block 4 - identities, checked against their derivations
  cos(A-B), sin(A+B), cos(2A) and sin(2A) hold for every pair tried
  sin(180-x) = sin(x) and cos(180-x) = -cos(x): confirmed

Block 5 - solving 2 sin(theta) = 1 on [0, 360)
  calculator principal value: 30.0000
  all solutions found:        [30.0, 150.0]
  sin(theta) = -0.5 on [0,360): [210.0, 330.0]
  sin(theta) = 1    on [0,360): [90.0]
  sin(theta) = 2    on [0,360): []  (impossible)

Block 6 - y = sin(theta) over two full periods
+1.00 |       *****                               *****                         
+0.89 |      *** ***                             *** ***                        
+0.78 |     **     **                           **     **                       
+0.67 |    **       **                         **       **                      
+0.56 |   **         **                       **         **                     
+0.44 |  **           **                     **           **                    
+0.33 |  *             *                     *             *                    
+0.22 | *               *                   *               *                   
+0.11 | *               **                  *               **                  
+0.00 |*-----------------*-----------------*-----------------*-----------------*
-0.11 |                   *               **                  *               **
-0.22 |                   *               *                   *               * 
-0.33 |                    *             *                     *             *  
-0.44 |                    **           **                     **           **  
-0.56 |                     **         **                       **         **   
-0.67 |                      **       **                         **       **    
-0.78 |                       **     **                           **     **     
-0.89 |                        *** ***                             *** ***      
-1.00 |                         *****                               *****       
        0                                  360                                 720

trig_graphs: passed
```

Block 6 shows the period directly: the curve between $0°$ and $360°$ is repeated exactly between $360°$ and $720°$, and never leaves $[-1, 1]$.

## Common pitfalls and traps

- **Trusting the calculator's single answer.** $\sin^{-1}(0.5)$ returns $30°$ and says nothing about $150°$. Nearly every "lost mark" in this topic is a missing second solution.
- **Reading the phase shift without factorising.** In $\sin(b\theta - c)$ the shift is $c/b$, not $c$.
- **Mixing degrees and radians.** `math.sin` is radians. A mixed calculation gives no error, just a wrong number.
- **Assuming $\tan$ has period $360°$.** It is $180°$, so $\tan$ equations have twice as many solutions in a given range as you might expect.
- **Evaluating $\tan 90°$.** Undefined — $\cos 90° = 0$. Floating point returns a huge finite number instead of raising, so a check on $\cos$ is safer than trusting the result.
- **Treating the identities as separate facts.** There is essentially one — $\cos(A-B)$ — and the rest are substitutions. Learning six independent formulas is a memory problem you do not need to have.

## Check your understanding

1. Without a calculator, give $\sin 150°$, $\cos 240°$ and $\tan 315°$ exactly.
2. Solve $\cos\theta = -\tfrac{1}{2}$ for $0° \le \theta < 360°$.
3. State the amplitude, period, phase shift and centre line of $y = 3\sin(2\theta - 60°) + 1$.
4. Use the addition formula to find $\cos 75°$ exactly.
5. Why does $\tan$ have period $180°$ when $\sin$ and $\cos$ have period $360°$?

<details><summary>Answers — open only after an attempt</summary>

1. $\sin 150° = \sin(180° - 30°) = \sin 30° = \tfrac12$. $\cos 240° = \cos(180° + 60°) = -\cos 60° = -\tfrac12$. $\tan 315° = \tan(360° - 45°) = -\tan 45° = -1$.
2. Principal value $\cos^{-1}(-0.5) = 120°$. The second solution is $360° - 120° = 240°$. So $\{120°, 240°\}$.
3. Factorise: $3\sin\big(2(\theta - 30°)\big) + 1$. Amplitude $3$; period $360°/2 = 180°$; phase shift $30°$ right; centre line $y = 1$, so the range is $[-2, 4]$.
4. $\cos 75° = \cos(45° + 30°) = \cos 45°\cos 30° - \sin 45°\sin 30° = \frac{1}{\sqrt2}\cdot\frac{\sqrt3}{2} - \frac{1}{\sqrt2}\cdot\frac12 = \frac{\sqrt3 - 1}{2\sqrt2} \approx 0.2588$.
5. Because $\tan\theta = y/x$, and rotating by $180°$ maps $(x, y)$ to $(-x, -y)$. Both signs flip, so the ratio is unchanged — the function returns to its value after only half a revolution.

**And the prediction from section 5:** there are **two** solutions in $[0°, 360°)$. The calculator gives $30°$; the identity $\sin(180° - \theta) = \sin\theta$ gives the second, $150°$. Any others would come from adding $360°$, which leaves the range.
</details>

## Practice — independent task

Implement `solve_trig(func, value, lo, hi)` handling all three functions, returning every solution in $[lo, hi)$.

1. Support `"sin"`, `"cos"` and `"tan"`, using the correct second-solution rule and the correct period for each.
2. Return `[]` when no solution exists — $\lvert\text{value}\rvert > 1$ for $\sin$ and $\cos$; note that `tan` has a solution for **every** real value, and say why in a comment.
3. Handle the boundary cases where the two solutions coincide: $\sin\theta = 1$, $\sin\theta = -1$, $\cos\theta = 1$, $\cos\theta = -1$. Your function must return **one** solution per period there, not a duplicated pair.
4. Verify every returned solution by substituting it back, to within `1e-9`.
5. Verify **completeness** independently: scan the range in small steps looking for sign changes of $f(\theta) - \text{value}$, and check that the number of sign changes matches the number of solutions you returned. Explain in a comment why a sign-change scan can miss a solution, and which of the cases in step 3 it would miss.

**Edge cases:** ranges not starting at $0$; negative ranges such as $[-180°, 180°)$; a range shorter than one period; $\tan$ near its asymptotes.

**Done when:** substitution and the independent scan agree for at least ten different equations, your step-3 cases return single solutions, and you can explain the one situation where the scan is guaranteed to disagree with the correct answer.

## Tradeoffs, limits and extensions

**Degrees survive only by convention.** Navigation, surveying and school syllabuses use degrees; essentially all mathematics beyond this point uses radians, because the calculus is only clean there. Expect to convert at the boundary and to keep track of which side you are on.

**The unit circle is a definition, not a derivation.** Nothing forces $\sin 120°$ to equal $\sin 60°$ — that is a *choice* about how to extend the function. It is the right choice because it is the unique extension that keeps the addition formulas working, which in turn is what makes the functions useful for describing rotation and waves.

**Where this goes.** These functions reappear as the solutions of the differential equation $y'' = -y$, which is why anything with a restoring force proportional to displacement oscillates sinusoidally — a pendulum, a spring, an LC circuit. That thread is in **ordinary differential equations** *(reserved)*, and decomposing an arbitrary periodic signal into sines is **Fourier analysis** *(reserved)*.

## Before moving on

You are done with this lesson when you can:

- State the unit circle definition and show it agrees with the right-triangle one for acute angles.
- Determine any quadrant's signs from the coordinates rather than a mnemonic.
- Derive $\cos(A-B)$ by computing one distance two ways, and get the double-angle formulas from it.
- Solve a trigonometric equation and find every solution in the range.

**Recap for later lookup:** $\cos\theta = x$, $\sin\theta = y$ on the unit circle; $\sin^2 + \cos^2 = 1$ is the circle equation; period $360°$ for $\sin$/$\cos$, $180°$ for $\tan$; $\sin(180° - \theta) = \sin\theta$, $\cos(360° - \theta) = \cos\theta$; $\cos(A-B) = \cos A\cos B + \sin A \sin B$, with all other addition and double-angle formulas following by substitution; $180° = \pi$ radians.

**Next:** [[03-sine-and-cosine-rules|Sine and Cosine Rules]] — solving triangles that have no right angle, where the $\sin(180° - \theta) = \sin\theta$ identity causes the ambiguous case.

## Related

- [[01-ratios-and-right-triangles|Trigonometric Ratios]] — the definition this one extends
- [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — the circle equation and distance formula used in the derivation
- **Complex Numbers** *(reserved)* — where the addition formulas turn out to be multiplication
