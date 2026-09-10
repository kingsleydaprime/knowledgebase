# Hyperbolic Functions

**[Advanced]** — a second family built from the same algebra, describing the hanging cable rather than the turning wheel.

## Before you start

- You know the circular functions and the unit-circle definition — [[02-graphs-and-identities|graphs and identities]].
- You are comfortable with $e^x$ and $\ln x$ — [[01-indices-and-logarithms|indices and logarithms]].
- Helpful but not required: derivatives — [[07-derivative-rules/01-rules|derivative rules]].

**What you will be able to do after this lesson:**

1. Define $\cosh$, $\sinh$ and $\tanh$ from exponentials, and state the identity that replaces $\sin^2 + \cos^2 = 1$.
2. Explain what is **hyperbolic** about them — that they parametrise $x^2 - y^2 = 1$ exactly as the circular functions parametrise $x^2 + y^2 = 1$.
3. Convert a circular identity into its hyperbolic counterpart using **Osborn's rule**, and say why the rule has the sign change it does.
4. Derive the inverse $\operatorname{arsinh} x = \ln\!\left(x + \sqrt{x^2+1}\right)$ by solving a quadratic.

**Study route:** read 1–5, attempt the prediction in section 5, then run the lab. Block 4 answers a question that was open for 50 years.

---

## 1. Why this exists

Hang a chain between two posts. What curve does it make?

Galileo said a parabola. He was wrong, and it took until 1691 for Johann Bernoulli, Huygens and Leibniz — working independently on a challenge problem — to establish the real answer. The curve is a **catenary**, from Latin *catena*, a chain:

$$
y = a\cosh\!\left(\frac{x}{a}\right)
$$

and $\cosh$ is not a circular function at all. The distinction is not academic: it is the difference between a stable arch and one that fails, and every suspension bridge and overhead power line is designed around it.

The functions arise the same way in a second setting entirely. Rotation in the plane preserves $x^2 + y^2$ and is described by $\cos$ and $\sin$. The transformation in special relativity — a Lorentz boost — preserves $x^2 - c^2t^2$, and is described by $\cosh$ and $\sinh$. Same algebra, one sign changed.

## 2. The definitions

$$
\cosh x = \frac{e^x + e^{-x}}{2}, \qquad \sinh x = \frac{e^x - e^{-x}}{2}, \qquad \tanh x = \frac{\sinh x}{\cosh x} = \frac{e^x - e^{-x}}{e^x + e^{-x}}
$$

They are simply the **even and odd parts** of $e^x$: any function splits uniquely into a symmetric piece and an antisymmetric piece, and for $e^x$ those pieces are $\cosh$ and $\sinh$. Adding them recovers what you started with:

$$
\cosh x + \sinh x = e^x
$$

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **$\cosh$** | "cosh" — the even part of $e^x$ | Always $\ge 1$; symmetric about the $y$-axis |
| **$\sinh$** | "shine" or "sinch" — the odd part | Odd, strictly increasing, all reals |
| **$\tanh$** | "tanch" — their ratio | S-shaped, asymptotes at $\pm 1$ |
| **Catenary** | The curve of a hanging flexible chain | $y = a\cosh(x/a)$ |
| **Osborn's rule** | The recipe converting circular identities to hyperbolic ones | See section 4 |

## 3. What is hyperbolic about them

Compute $\cosh^2 x - \sinh^2 x$ directly:

$$
\cosh^2 x - \sinh^2 x = \left(\frac{e^x + e^{-x}}{2}\right)^2 - \left(\frac{e^x - e^{-x}}{2}\right)^2
$$

Expanding both squares:

$$
= \frac{e^{2x} + 2 + e^{-2x}}{4} - \frac{e^{2x} - 2 + e^{-2x}}{4} = \frac{4}{4} = 1
$$

So:

$$
\boxed{\cosh^2 x - \sinh^2 x = 1}
$$

Now compare the two families side by side:

| | Circular | Hyperbolic |
| :--- | :--- | :--- |
| Identity | $\cos^2 t + \sin^2 t = 1$ | $\cosh^2 t - \sinh^2 t = 1$ |
| Curve traced by $(\cos t, \sin t)$ or $(\cosh t, \sinh t)$ | Unit **circle** $x^2 + y^2 = 1$ | Unit **hyperbola** $x^2 - y^2 = 1$ (right branch) |
| Range of the parameter | $t \in [0, 2\pi)$ covers it once | $t \in \mathbb{R}$ covers one branch |
| Periodic? | Yes, period $2\pi$ | **No** — never repeats |
| Meaning of the parameter $t$ | Twice the area of the circular sector | Twice the area of the hyperbolic sector |

That last row is the deepest correspondence and the least often mentioned. In *both* cases the parameter is twice the swept sector area — the circular one happens to coincide with arc length, which is why we call it an angle. For the hyperbola there is no angle, but the area interpretation carries over unchanged.

The point $(\cosh t, \sinh t)$ can never reach the left branch, because $\cosh t \ge 1 > 0$ always. Block 2 of the lab traces the branch.

### Graphs and derivatives

| Function | Range | Shape | Derivative |
| :--- | :--- | :--- | :--- |
| $\cosh x$ | $[1, \infty)$ | U-shaped, minimum $1$ at $x=0$ | $\sinh x$ |
| $\sinh x$ | $(-\infty, \infty)$ | Odd, through the origin, increasing | $\cosh x$ |
| $\tanh x$ | $(-1, 1)$ | S-shaped, asymptotic to $\pm1$ | $\operatorname{sech}^2 x$ |

The derivatives are worth noticing: $\frac{d}{dx}\cosh x = \sinh x$ with **no minus sign**, unlike $\frac{d}{dx}\cos x = -\sin x$. This is why $\cosh$ and $\sinh$ solve $y'' = y$ while $\cos$ and $\sin$ solve $y'' = -y$ — a restoring force gives oscillation, a repelling one gives exponential growth.

## 4. Osborn's rule

Every circular identity has a hyperbolic counterpart, obtained mechanically:

> Replace $\cos \to \cosh$ and $\sin \to \sinh$, then **change the sign of any term containing a product of two sines**.

Examples:

| Circular | Hyperbolic |
| :--- | :--- |
| $\cos^2 + \sin^2 = 1$ | $\cosh^2 - \sinh^2 = 1$ |
| $\cos(A+B) = \cos A\cos B - \sin A \sin B$ | $\cosh(A+B) = \cosh A\cosh B + \sinh A\sinh B$ |
| $\sin(A+B) = \sin A\cos B + \cos A \sin B$ | $\sinh(A+B) = \sinh A\cosh B + \cosh A\sinh B$ |
| $\cos 2A = 1 - 2\sin^2 A$ | $\cosh 2A = 1 + 2\sinh^2 A$ |

Note the third row is unchanged — it contains no product of two sines.

**Why the rule works.** From the definitions, $\cosh x = \cos(ix)$ and $\sinh x = -i\sin(ix)$. Substituting into a circular identity produces the hyperbolic one, and each $\sin$ contributes a factor of $i$; a product of two sines contributes $i^2 = -1$, which is precisely the sign change. The rule is a bookkeeping device for that substitution, and it becomes obvious once complex numbers are available — see **complex numbers** *(reserved)*.

### The inverse functions are logarithms

Solve $y = \sinh x$ for $x$. Write $t = e^x$:

$$
y = \frac{t - t^{-1}}{2} \quad\Longrightarrow\quad 2y = t - \frac{1}{t} \quad\Longrightarrow\quad t^2 - 2yt - 1 = 0
$$

A quadratic in $t$. By the formula:

$$
t = \frac{2y \pm \sqrt{4y^2 + 4}}{2} = y \pm \sqrt{y^2 + 1}
$$

Since $t = e^x > 0$ and $\sqrt{y^2+1} > \lvert y\rvert$, the minus root is negative and must be discarded. So $e^x = y + \sqrt{y^2+1}$, giving:

$$
\operatorname{arsinh} y = \ln\!\left(y + \sqrt{y^2 + 1}\right)
$$

Similarly $\operatorname{arcosh} y = \ln\!\left(y + \sqrt{y^2 - 1}\right)$ for $y \ge 1$, and $\operatorname{artanh} y = \tfrac12\ln\frac{1+y}{1-y}$ for $\lvert y \rvert < 1$.

The circular inverses are nothing like this. Hyperbolic functions are built from exponentials, so their inverses are logarithms — the whole family stays inside elementary algebra.

> [!TIP]
> **Predict before running the lab.** A chain and a parabola are hung between the same two posts, sagging by the same amount at the centre. Are they the same curve? If not, where do they differ most — near the posts, near the middle, or somewhere between? Decide before opening the answers.

## 5. The catenary, and why it is not a parabola

A chain of uniform weight per unit **length** hangs as $y = a\cosh(x/a)$. A cable carrying a uniform weight per unit **horizontal distance** — a suspension bridge deck, where the roadway is far heavier than the cable — hangs as a **parabola**.

So both curves are physically real; they answer different loading questions. Galileo's error was assuming the chain case behaves like the deck case.

The two curves are genuinely different, though they look alike. Expanding $\cosh$ as a series:

$$
a\cosh\frac{x}{a} = a\left(1 + \frac{x^2}{2a^2} + \frac{x^4}{24a^4} + \cdots\right) = a + \frac{x^2}{2a} + \frac{x^4}{24a^3} + \cdots
$$

The first two terms **are** a parabola. The catenary is a parabola plus an $x^4$ correction, so for a shallow sag — where $x/a$ is small — the two are nearly indistinguishable, and Galileo's guess was a good approximation for exactly that reason. As the sag deepens, the $x^4$ term takes over.

Block 4 of the lab measures the gap.

## Worked example — runnable

**Runnable example:** save as `hyperbolic.py` in any empty directory and run `python3 hyperbolic.py`. Standard library only; writes no files.

```python
"""Hyperbolic functions: definitions, the hyperbola, Osborn's rule, catenary."""
import math

EPS = 1e-12


def cosh(x):
    return (math.exp(x) + math.exp(-x)) / 2


def sinh(x):
    return (math.exp(x) - math.exp(-x)) / 2


def tanh(x):
    return sinh(x) / cosh(x)


def arsinh(y):
    """Derived by solving t^2 - 2yt - 1 = 0 for t = e^x."""
    return math.log(y + math.sqrt(y * y + 1))


def catenary(x, a):
    """A chain of uniform weight per unit length, lowest point at the origin."""
    return a * cosh(x / a) - a


def matched_parabola(x, half_span, sag):
    """The parabola through the same endpoints with the same central sag."""
    return sag * (x / half_span) ** 2


if __name__ == "__main__":
    print("Block 1 - the definitions match the library, and cosh + sinh = e^x")
    for x in (-2.5, -1.0, 0.0, 0.5, 3.0):
        assert abs(cosh(x) - math.cosh(x)) < EPS
        assert abs(sinh(x) - math.sinh(x)) < EPS
        assert abs((cosh(x) + sinh(x)) - math.exp(x)) < EPS
    print("  cosh and sinh are the even and odd parts of e^x, for every x tried")
    print(f"  cosh(0) = {cosh(0):.6f} (the minimum), sinh(0) = {sinh(0):.6f}")

    print()
    print("Block 2 - (cosh t, sinh t) traces the unit hyperbola x^2 - y^2 = 1")
    print("      t        cosh t      sinh t    cosh^2 - sinh^2")
    for t in (-2.0, -1.0, 0.0, 1.0, 2.0, 5.0):
        c, s = cosh(t), sinh(t)
        print(f"  {t:6.1f}   {c:10.6f}  {s:10.6f}   {c*c - s*s:.10f}")
        assert abs(c * c - s * s - 1) < 1e-9
    print("  cosh is never below 1, so only the right branch is ever reached")
    assert min(cosh(t) for t in (-5, -1, 0, 1, 5)) >= 1.0

    print()
    print("Block 3 - Osborn's rule, checked against the real identities")
    for A, B in [(0.5, 1.3), (-1.0, 2.0), (2.5, -0.75)]:
        # cos(A+B) = cosAcosB - sinAsinB  ->  sign flips (product of two sines)
        assert abs(cosh(A + B) - (cosh(A) * cosh(B) + sinh(A) * sinh(B))) < 1e-9
        # sin(A+B) = sinAcosB + cosAsinB  ->  unchanged (no sin*sin term)
        assert abs(sinh(A + B) - (sinh(A) * cosh(B) + cosh(A) * sinh(B))) < 1e-9
        # cos2A = 1 - 2sin^2 A  ->  cosh2A = 1 + 2sinh^2 A
        assert abs(cosh(2 * A) - (1 + 2 * sinh(A) ** 2)) < 1e-9
    print("  cosh(A+B), sinh(A+B) and cosh(2A) confirm the sign rule")

    print("  the inverse is a logarithm, not another transcendental:")
    for y in (-3.0, 0.0, 1.0, 7.5):
        x = arsinh(y)
        print(f"    arsinh({y:5.1f}) = ln(y + sqrt(y^2+1)) = {x:10.6f}   sinh(x) = {sinh(x):.6f}")
        assert abs(sinh(x) - y) < 1e-9

    print()
    print("Block 4 - catenary versus parabola, same posts and same sag")
    A_PARAM, HALF_SPAN = 1.0, 2.0
    SAG = catenary(HALF_SPAN, A_PARAM)
    print(f"  posts at x = +/-{HALF_SPAN}, both curves sag by {SAG:.6f} at the centre")
    print("       x     catenary    parabola   difference")
    worst_x, worst = 0.0, 0.0
    for i in range(0, 21):
        x = HALF_SPAN * i / 20
        cat, par = catenary(x, A_PARAM), matched_parabola(x, HALF_SPAN, SAG)
        if abs(cat - par) > worst:
            worst_x, worst = x, abs(cat - par)
        if i % 5 == 0:
            print(f"  {x:6.2f}  {cat:10.6f}  {par:10.6f}  {cat - par:+10.6f}")
    print(f"  they agree at both ends and at the centre, by construction")
    print(f"  largest gap {worst:.6f} at x = {worst_x:.2f} - between centre and post")
    assert abs(catenary(0, A_PARAM)) < EPS
    assert abs(catenary(HALF_SPAN, A_PARAM) - SAG) < EPS
    assert worst > 0.01, "the two curves are genuinely different"
    assert 0.0 < worst_x < HALF_SPAN

    print()
    print("  a shallower sag makes the parabola a better approximation:")
    for a in (1.0, 4.0, 16.0, 64.0):
        sag = catenary(HALF_SPAN, a)
        gap = max(abs(catenary(HALF_SPAN * i / 20, a)
                      - matched_parabola(HALF_SPAN * i / 20, HALF_SPAN, sag))
                  for i in range(21))
        print(f"    a = {a:5.1f}: sag {sag:9.6f}, largest gap {gap:.8f}")

    print()
    print("Block 5 - tanh saturates, which is why it was used as an activation")
    for x in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0):
        print(f"  tanh({x:5.1f}) = {tanh(x):.10f}")
        assert -1 < tanh(x) < 1
    print("  it never reaches 1, but by x = 10 it is within 1e-8 of it")
    assert abs(tanh(10.0) - 1) < 1e-8

    print()
    print("hyperbolic: passed")
```

Expected output:

```
Block 1 - the definitions match the library, and cosh + sinh = e^x
  cosh and sinh are the even and odd parts of e^x, for every x tried
  cosh(0) = 1.000000 (the minimum), sinh(0) = 0.000000

Block 2 - (cosh t, sinh t) traces the unit hyperbola x^2 - y^2 = 1
      t        cosh t      sinh t    cosh^2 - sinh^2
    -2.0     3.762196   -3.626860   1.0000000000
    -1.0     1.543081   -1.175201   1.0000000000
     0.0     1.000000    0.000000   1.0000000000
     1.0     1.543081    1.175201   1.0000000000
     2.0     3.762196    3.626860   1.0000000000
     5.0    74.209949   74.203211   1.0000000000
  cosh is never below 1, so only the right branch is ever reached

Block 3 - Osborn's rule, checked against the real identities
  cosh(A+B), sinh(A+B) and cosh(2A) confirm the sign rule
  the inverse is a logarithm, not another transcendental:
    arsinh( -3.0) = ln(y + sqrt(y^2+1)) =  -1.818446   sinh(x) = -3.000000
    arsinh(  0.0) = ln(y + sqrt(y^2+1)) =   0.000000   sinh(x) = 0.000000
    arsinh(  1.0) = ln(y + sqrt(y^2+1)) =   0.881374   sinh(x) = 1.000000
    arsinh(  7.5) = ln(y + sqrt(y^2+1)) =   2.712465   sinh(x) = 7.500000

Block 4 - catenary versus parabola, same posts and same sag
  posts at x = +/-2.0, both curves sag by 2.762196 at the centre
       x     catenary    parabola   difference
    0.00    0.000000    0.000000   +0.000000
    0.50    0.127626    0.172637   -0.045011
    1.00    0.543081    0.690549   -0.147468
    1.50    1.352410    1.553735   -0.201325
    2.00    2.762196    2.762196   +0.000000
  they agree at both ends and at the centre, by construction
  largest gap 0.202577 at x = 1.40 - between centre and post

  a shallower sag makes the parabola a better approximation:
    a =   1.0: sag  2.762196, largest gap 0.20257742
    a =   4.0: sag  0.510504, largest gap 0.00263562
    a =  16.0: sag  0.125163, largest gap 0.00004071
    a =  64.0: sag  0.031253, largest gap 0.00000064

Block 5 - tanh saturates, which is why it was used as an activation
  tanh(  0.0) = 0.0000000000
  tanh(  0.5) = 0.4621171573
  tanh(  1.0) = 0.7615941560
  tanh(  2.0) = 0.9640275801
  tanh(  5.0) = 0.9999092043
  tanh( 10.0) = 0.9999999959
  it never reaches 1, but by x = 10 it is within 1e-8 of it

hyperbolic: passed
```

The second half of block 4 is the quantitative version of Galileo's mistake. As the sag gets shallower the gap collapses fast — which is why the wrong answer survived for so long.

## Common pitfalls and traps

- **Expecting periodicity.** These functions never repeat. $\cosh$ grows without bound and $\tanh$ approaches its asymptotes. Nothing here has a period.
- **Getting the identity's sign wrong.** It is $\cosh^2 - \sinh^2 = 1$, with a **minus**. Writing $+$ gives a false statement that is easy to miss.
- **Forgetting the domain of $\operatorname{arcosh}$.** $\cosh x \ge 1$, so $\operatorname{arcosh} y$ is undefined for $y < 1$. And $\cosh$ is even, so its inverse needs a branch choice — conventionally the non-negative one.
- **Assuming the derivative has a minus sign.** $\frac{d}{dx}\cosh x = +\sinh x$. The absence of the minus is the entire difference between oscillation and growth.
- **Calling a hanging chain a parabola.** The correct answer depends on how the weight is distributed: uniform per unit *length* gives a catenary; uniform per unit *horizontal distance* gives a parabola.
- **Computing $\cosh$ for large arguments naively.** `math.exp(800)` overflows, but $\cosh(800)$ is a perfectly meaningful (enormous) number. The lab stays in a safe range; production code needs the scaled form.

## Check your understanding

1. Show $\cosh x + \sinh x = e^x$ and $\cosh x - \sinh x = e^{-x}$ directly from the definitions.
2. Use Osborn's rule to write the hyperbolic version of $\sin 2A = 2\sin A\cos A$.
3. Evaluate $\cosh(\ln 3)$ exactly.
4. Why can the point $(\cosh t, \sinh t)$ never reach the left branch of $x^2 - y^2 = 1$?
5. What is $\lim_{x\to\infty}\tanh x$, and what does that mean for $\tanh$ as a neural-network activation function?

<details><summary>Answers — open only after an attempt</summary>

1. $\cosh x + \sinh x = \frac{e^x + e^{-x}}{2} + \frac{e^x - e^{-x}}{2} = \frac{2e^x}{2} = e^x$. Subtracting instead cancels the $e^x$ terms and leaves $\frac{2e^{-x}}{2} = e^{-x}$.
2. There is no product of two sines, so nothing changes: $\sinh 2A = 2\sinh A\cosh A$.
3. $\cosh(\ln 3) = \frac{e^{\ln 3} + e^{-\ln 3}}{2} = \frac{3 + \frac13}{2} = \frac{10/3}{2} = \frac{5}{3}$.
4. Because $\cosh t = \frac{e^t + e^{-t}}{2}$ is a sum of two positive numbers, and by AM–GM it is at least $\sqrt{e^t \cdot e^{-t}} = 1$. The $x$-coordinate is therefore always $\ge 1$, so the point stays on the right branch.
5. $\tanh x \to 1$. As an activation function this means the output **saturates**: for large inputs the derivative $\operatorname{sech}^2 x$ becomes vanishingly small, so gradients almost stop flowing. This is the vanishing-gradient problem, and it is the main reason ReLU displaced $\tanh$ in deep networks.

**And the prediction from section 4:** they are **not** the same curve. Both pass through the two posts and both have the same central sag, so they agree at exactly three points — and differ everywhere else. The largest gap falls **between** the centre and the posts, which the lab locates at $x = 1.40$ out of a half-span of $2$.
</details>

## Practice — independent task

Implement `hang_chain(span, sag)`: given the horizontal distance between two posts at equal height, and the required central sag, find the catenary parameter $a$ and the chain's **arc length**.

1. The relation is $\text{sag} = a\left(\cosh\frac{\text{span}}{2a} - 1\right)$. This **cannot be solved for $a$ in closed form** — it is transcendental. Solve it numerically by bisection or Newton's method, and say in a comment how you chose your bracket.
2. The arc length of $y = a\cosh(x/a)$ from $-w$ to $w$ is $2a\sinh(w/a)$. Derive this — the integrand $\sqrt{1 + (y')^2}$ simplifies beautifully because of the main identity. Show the simplification in a comment.
3. Assert the chain is always **longer** than the straight-line distance between the posts, and longer than the span.
4. Check a limiting case you can verify independently: as the sag tends to zero, arc length must tend to the span. Confirm numerically for a sequence of shrinking sags, and report the rate at which the excess shrinks.
5. Compare against the parabola: for the same span and sag, compute the parabolic arc length numerically and report the relative difference for sag/span ratios of $0.01$, $0.1$ and $0.5$.

**Edge cases:** zero sag (degenerate — decide whether to raise or return the span); sag larger than the span; a solver bracket that fails to contain the root.

**Done when:** your solved $a$ reproduces the requested sag to within `1e-9`, your limiting check in step 4 behaves as you predicted before running it, and your step-5 table shows the catenary and parabola converging as the sag shrinks.

## Tradeoffs, limits and extensions

**Numerical care with large arguments.** $\cosh x$ and $\sinh x$ overflow around $x \approx 710$ in double precision, even though the mathematical values are finite. Worse, $\sinh x$ for *small* $x$ computed as $\frac{e^x - e^{-x}}{2}$ suffers catastrophic cancellation — two nearly equal numbers subtracted. Python's `math.sinh` uses a series expansion near zero for this reason; the lab's hand-written `sinh` does not, and would lose precision for $x$ near $10^{-8}$.

**Where these turn up.** Beyond the catenary: the shape of a soap film between two rings (a catenoid, the minimal surface of revolution); the Lorentz transformation, where "rapidity" is the hyperbolic angle and velocities add by $\tanh$ addition rather than plain addition; the logistic function of statistics and machine learning, which is $\tanh$ rescaled; and the solutions of $y'' = y$, which is the ODE describing anything with a *repelling* rather than restoring force.

**The arch connection.** An inverted catenary is the shape in which a free-standing arch carries pure compression with no bending anywhere — Gaudí used hanging-chain models upside down to design them, and the Gateway Arch in St. Louis is a weighted catenary for the same reason.

## Before moving on

You are done with this lesson when you can:

- Write the three definitions from memory and show $\cosh + \sinh = e^x$.
- Prove $\cosh^2 - \sinh^2 = 1$ by expanding, and say which curve that parametrises.
- Apply Osborn's rule and explain where its sign change comes from.
- Derive $\operatorname{arsinh}$ by solving a quadratic in $e^x$.

**Recap for later lookup:** $\cosh x = \frac{e^x + e^{-x}}{2}$, $\sinh x = \frac{e^x - e^{-x}}{2}$, $\tanh = \frac{\sinh}{\cosh}$; $\cosh^2 - \sinh^2 = 1$, parametrising the right branch of $x^2 - y^2 = 1$; not periodic; $\frac{d}{dx}\cosh = \sinh$ and $\frac{d}{dx}\sinh = \cosh$, no minus signs; Osborn's rule flips the sign of any $\sinh\!\cdot\!\sinh$ product; $\operatorname{arsinh} y = \ln(y + \sqrt{y^2+1})$; a hanging chain is $y = a\cosh(x/a)$, not a parabola.

**Next:** [[01-plane-shapes|Mensuration: Plane Shapes]] — from angles and curves to the areas they enclose.

## Related

- [[02-graphs-and-identities|Graphs and Identities]] — the circular family this one mirrors
- [[01-indices-and-logarithms|Indices and Logarithms]] — the exponentials these are built from
- **Complex Numbers** *(reserved)* — where Osborn's rule stops being a trick
- **Ordinary Differential Equations** *(reserved)* — $y'' = y$ versus $y'' = -y$
