# Floating Point and Error

**[Intermediate]** — Machine epsilon, cancellation, and how to analyse the error in a computation rather than hoping.

> **The format itself is in [[foundations/computer-architecture/02-data-representation|Data Representation]]** — sign/exponent/mantissa, NaN, denormals. **This note is what it means for numerical work**: how error propagates, and how to write algorithms that don't amplify it.

## Machine epsilon

**The gap between 1.0 and the next representable number.**

$$\epsilon_{\text{double}} = 2^{-52} \approx 2.22\times10^{-16}$$
$$\epsilon_{\text{float}} = 2^{-23} \approx 1.19\times10^{-7}$$

**Every stored value has relative error at most $\epsilon/2$:**

$$\text{fl}(x) = x(1 + \delta), \qquad |\delta| \leq \epsilon/2$$

**And every arithmetic operation is correctly rounded** (IEEE 754 guarantees this):

$$\text{fl}(a \oplus b) = (a \oplus b)(1+\delta)$$

> **The mental model that matters: floating point numbers are *relatively* spaced, not absolutely.** Near 1.0 the gap is $10^{-16}$; near $10^{6}$ it's $10^{-10}$; near $10^{-6}$ it's $10^{-22}$.
>
> **So "how many decimal places" is the wrong question.** A `double` has ~16 *significant digits*, wherever it sits on the number line. **Absolute tolerances are almost always a bug** — use relative ones, or a hybrid.

**The tolerance you actually want:**

```python
def close(a, b, rtol=1e-9, atol=1e-12):
    return abs(a - b) <= max(rtol * max(abs(a), abs(b)), atol)
```

**Relative for normal magnitudes, absolute as a floor near zero** — because relative comparison is meaningless when the true answer is 0.

## Catastrophic cancellation

**The single biggest source of accuracy loss**, and it's worth being able to spot on sight.

**Subtracting two nearly-equal numbers destroys significant digits:**

```
  1.2345678901234567
- 1.2345678901234000
  ─────────────────────
  0.0000000000000567     ← 3 significant digits left, from 17
```

**The inputs were accurate to 16 digits. The result is accurate to 3.** No arithmetic error occurred — **the information simply wasn't there.**

**The canonical example — the quadratic formula:**

$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$

**When $b^2 \gg 4ac$, $\sqrt{b^2-4ac} \approx |b|$.** So one of the two roots involves subtracting nearly-equal quantities and loses precision catastrophically.

**The fix — compute the well-conditioned root, then use the product of roots:**

```python
q = -0.5 * (b + copysign(sqrt(b*b - 4*a*c), b))
x1 = q / a
x2 = c / q          # from x1·x2 = c/a — no subtraction
```

**Same mathematics, completely different accuracy.** This is the classic demonstration that **algebraically equivalent expressions are not numerically equivalent.**

**Other cancellations and their fixes:**

| Naive | Better |
|---|---|
| $\sqrt{x+1}-\sqrt{x}$ | $\dfrac{1}{\sqrt{x+1}+\sqrt{x}}$ |
| $1-\cos x$ (small $x$) | $2\sin^2(x/2)$ |
| $e^x - 1$ (small $x$) | **`expm1(x)`** |
| $\log(1+x)$ (small $x$) | **`log1p(x)`** |
| variance via $E[X^2]-E[X]^2$ | **Welford's online algorithm** |

> **`expm1` and `log1p` exist in every standard library for exactly this reason.** If you're computing $e^x - 1$ for small $x$ by hand, you're throwing away most of your precision, and the library function is there to stop you.

**The variance one is worth naming** because it's so common: the textbook formula $\frac{1}{n}\sum x_i^2 - \bar{x}^2$ subtracts two large nearly-equal numbers and **can return a negative variance.** Welford's algorithm updates incrementally and is stable. → [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/02-expectation-and-variance|Expectation and Variance]]

## Summation

**Adding many numbers loses accuracy**, because each addition rounds and the errors accumulate.

**Naive summation of $n$ terms has error growing as $O(n\epsilon)$** — and worse if magnitudes vary, because small terms get swallowed:

```python
sum([1e16, 1.0, -1e16])   # → 0.0 in naive order
                          # → 1.0 if you add the small ones first
```

**Floating-point addition is not associative**, so **the order changes the answer.** → [[foundations/computer-architecture/02-data-representation|Non-associativity]]

**Kahan summation** carries a running compensation term:

```python
total = 0.0; c = 0.0
for x in values:
    y = x - c
    t = total + y
    c = (t - total) - y      # recovers the lost low-order bits
    total = t
```

**Error becomes $O(\epsilon)$ — independent of $n$.** Roughly 4× the arithmetic, and worth it for long sums.

**Pairwise summation** — recursively split and add halves — gives $O(\epsilon\log n)$ for essentially free. **NumPy's `sum` does this**, which is why it's more accurate than a Python loop.

> **A practical consequence for ML:** parallel reductions sum in a non-deterministic order, so **the same training run gives slightly different results.** That's not a bug and it can't be fixed without giving up the parallelism — it's why bit-exact reproducibility across GPU counts is generally not offered. → [[foundations/gpu-and-parallel-computing/README|GPU and Parallel Computing]]

## Error propagation

**How error travels through a computation.**

**Through a function**, by Taylor:

$$\delta y \approx f'(x)\,\delta x \qquad\Longrightarrow\qquad \frac{\delta y}{y} \approx \underbrace{\frac{x f'(x)}{f(x)}}_{\text{condition number}}\cdot\frac{\delta x}{x}$$

**That coefficient is the condition number of $f$ at $x$**, and it tells you the amplification factor.

**Examples worth knowing:**

| Operation | Condition | Note |
|---|---|---|
| Multiplication, division | $\kappa = 1$ | **always well-conditioned** |
| Addition of same-sign | $\kappa = 1$ | fine |
| **Subtraction of near-equals** | **$\kappa \to \infty$** | **cancellation** |
| $\sqrt{x}$ | $1/2$ | **error-reducing** |
| $e^x$ | $|x|$ | bad for large $x$ |
| $\log x$ | $1/|\log x|$ | bad near $x=1$ |

> **Multiplication and division never lose relative precision. Subtraction can lose all of it.** That single asymmetry explains most of the reformulations in this note — **the goal is almost always to rewrite a subtraction away.**

## Forward and backward error

**The framing that makes numerical analysis tractable.**

**Forward error** — how far is my answer from the true answer? *What you want to know.*

**Backward error** — for what perturbed *input* would my answer be exactly right? *What you can actually compute.*

$$\text{forward error} \lesssim \text{condition number} \times \text{backward error}$$

> **An algorithm is *backward stable* if it gives the exact answer to a nearby problem.** That's the realistic goal — and it's what LAPACK routines guarantee.
>
> **The insight this buys you:** if your input data is measured to 3 digits anyway, an algorithm with backward error at machine precision is **already better than your data deserves.** Chasing more accuracy is wasted effort — the uncertainty is in the measurement, not the arithmetic.

**Gaussian elimination with partial pivoting is backward stable in practice**; without pivoting it isn't. **That's the entire justification for pivoting.** → [[foundations/numerical-methods/04-linear-systems|Linear Systems]]

## Special values in practice

**NaN propagates**, which is a feature: one NaN anywhere poisons everything downstream, so you find out.

**`NaN != NaN`** — the standard test:

```python
if x != x:  # x is NaN
```

**Where NaN comes from:** $0/0$, $\infty-\infty$, $\sqrt{-1}$, $\log(-1)$, $0\times\infty$.

**Debugging NaN:** enable floating-point exceptions (`feenableexcept` in C, `np.seterr(all='raise')` in NumPy) so you **trap at the point of creation** rather than discovering it a thousand operations later. **This is the single most useful NaN-debugging technique** and almost nobody uses it.

**Infinity is often more useful than an error** — it propagates sensibly, and $1/\infty = 0$ does the right thing.

**Denormals** near zero can be **10–100× slower** on some hardware. Audio and signal-processing code flushes them to zero for this reason.

## Practical notes

**Use `double` by default.** `float` has ~7 digits, which sounds fine and isn't once errors accumulate. **Use `float` deliberately** — for memory bandwidth, or for ML where the noise floor is high anyway.

**Never test floats for equality.** Use a hybrid tolerance.

**Never accumulate in the input's precision.** Sum `float` data into a `double` accumulator — free, and it removes most of the error.

**Prefer `expm1`, `log1p`, `hypot`, `fma`.** They exist because the naive versions lose precision.

**Scale your problem.** A system mixing $10^{-9}$ and $10^{12}$ is badly conditioned by construction. **Non-dimensionalise** — the same advice as [[engineering/02-control-theory/08-state-space|state-space scaling]].

**Test with `-ffast-math` off.** It permits reassociation and assumes no NaN/Inf, so **it can silently break carefully-written numerical code.** If your results change when you enable it, one of the two versions is wrong.

**Check convergence empirically.** Halve the step, confirm the error falls as the theory says. **It's the cheapest correctness test available in this whole domain.**

---

## Related
- [[foundations/computer-architecture/02-data-representation|Data Representation]] — the IEEE 754 format itself
- [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — where conditioning bites hardest
- [[foundations/numerical-methods/01-why-numerical-methods|Why Numerical Methods]] — conditioning vs stability
- [[foundations/numerical-methods/README|Numerical methods map]]
