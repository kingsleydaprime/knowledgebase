# Riemann Sums — Turning an Integral into a Sum

**[Beginner]** — how a continuous integral becomes something a computer can actually add up.

## Before you start

- You know what an integral means as "the area under a curve" — [[03-calculus-2/01-integration-by-parts|integration]].
- You can write a `for` loop.

**After this lesson you will be able to:**

1. Take any definite integral and write down its discrete form, with the step width and the sample points worked out explicitly.
2. Explain the difference between the **left**, **right** and **midpoint** rules, and the **trapezoidal** rule.
3. Say why a computer can never evaluate a true integral, and what it does instead.
4. Watch the error shrink as you use more steps, and say how fast it shrinks for each rule.

**Study route:** read the terms, then work through section 3 with a pen, attempt the prediction, then run the lab.

---

## 1. Why this exists

An integral like $\int_1^{10} x\,dx$ is defined using infinity. It is the limit of adding up infinitely many infinitely thin rectangles. That definition is exact and beautiful, and a computer cannot do it, because a computer cannot do infinity. It has a finite amount of memory and a finite amount of time.

So every piece of software that has ever computed an integral — a battery-range estimate in an electric car, a rocket working out its position from its acceleration, a monitor totalling your blood flow — did something else. It chopped the range into a **finite** number of pieces, worked out the area of each piece using simple shapes, and added them up.

That chopping-up is called **discretising**, and this lesson is about doing it properly. It is the bridge between the calculus you were taught and the code you would actually write.

## Terms used in numerical integration

1. **Continuous**: This means something has a value at *every* point, with no gaps. A real-world quantity like temperature is continuous — between any two instants there is another instant.

2. **Discrete**: This means something has values only at separate, countable points. A computer's view of the world is always discrete, because it stores a finite list of numbers.

3. **Discretising**: This is the act of turning a continuous thing into a discrete one, by choosing a finite set of points to sample and ignoring everything between them.

4. **Interval**: This is the range you are integrating over. In $\int_1^{10} x\,dx$ the interval runs from $1$ to $10$. The number at the bottom is the **lower limit** and the number at the top is the **upper limit**.

5. **Subinterval**: This is one of the equal pieces you chop the interval into. If you chop $1$ to $10$ into nine pieces, each subinterval is one unit wide.

6. **Step width**: This is how wide each subinterval is. It is usually written $\Delta x$, said "delta x", where the $\Delta$ just means "a change in". If you chop an interval from $a$ to $b$ into $n$ equal pieces then $\Delta x = \frac{b-a}{n}$.

7. **Sample point**: This is the single $x$ value inside a subinterval where you actually evaluate the function. You get to choose where it sits, and that choice is what separates the rules below from each other.

8. **Riemann sum**: This is the total you get when you multiply each sample's height by the step width and add all of them up. It is an *approximation* of the integral.

9. **Convergence**: This means that as you use more and more subintervals, the approximation gets closer and closer to the true answer. Every rule here converges; they just do it at different speeds.

10. **Error**: This is the gap between your approximation and the true value. It is the number you actually care about, and the thing every rule is trying to make small cheaply.

## 2. The general discrete form

Take any integral $\int_a^b f(x)\,dx$ and chop the interval into $n$ equal pieces.

The step width is the total distance divided by the number of pieces:

$$
\Delta x = \frac{b - a}{n}
$$

The sample points are then spaced $\Delta x$ apart, starting from $a$:

$$
x_i = a + i\,\Delta x
$$

And the discrete form of the integral is:

$$
\int_a^b f(x)\,dx \;\approx\; \sum_{i=1}^{n} f(x_i)\,\Delta x
$$

Read that right to left: take the height of the function at a sample point, multiply by the width of the step to get the area of one thin rectangle, and add up all $n$ of them.

The only thing separating this from the real integral is that $n$ is a finite number. Let $n$ grow without limit and the approximation becomes exact:

$$
\int_a^b f(x)\,dx = \lim_{n \to \infty}\sum_{i=1}^{n} f(x_i)\,\Delta x
$$

**That limit is the definition of the integral**, and it is the line a computer cannot follow.

## 3. A worked example, all the way through

Take $\int_1^{10} x\,dx$, chopped into $n$ equal pieces.

**Step width.** The interval runs from $1$ to $10$, so its total width is $10 - 1 = 9$:

$$
\Delta x = \frac{10 - 1}{n} = \frac{9}{n}
$$

**Sample points.** Starting at $1$ and stepping by $\frac{9}{n}$ each time:

$$
x_i = 1 + i\,\Delta x = 1 + \frac{9i}{n}
$$

**The sum.** Substituting both into the general form:

$$
\int_1^{10} x\,dx \;\approx\; \sum_{i=1}^{n}\left(1 + \frac{9i}{n}\right)\frac{9}{n}
$$

That is the discrete form, and it is directly translatable into code — the sum is a loop, and the bracket is the function evaluated at the loop index.

**Checking against the exact answer.** This particular integral is easy to do by hand:

$$
\int_1^{10} x\,dx = \left[\frac{x^2}{2}\right]_1^{10} = \frac{100}{2} - \frac{1}{2} = 49.5
$$

Having an exact answer to compare against is why this example is worth using — you can *see* the approximation closing in on $49.5$, which you cannot do for the integrals you would actually need this for.

### The simplest case: a step width of exactly 1

Set $\Delta x = 1$, so there are nine subintervals. Now the three rules are easy to write out in full.

**Left Riemann sum** — take the height at the *start* of each subinterval, so $x = 1, 2, \dots, 9$:

$$
\sum_{x=1}^{9} x \cdot 1 = 1+2+3+4+5+6+7+8+9 = 45
$$

**Right Riemann sum** — take the height at the *end* of each subinterval, so $x = 2, 3, \dots, 10$:

$$
\sum_{x=2}^{10} x \cdot 1 = 2+3+4+5+6+7+8+9+10 = 54
$$

The true answer is $49.5$, sitting exactly between $45$ and $54$. That is not a coincidence, and it is worth understanding why. Because $f(x) = x$ is increasing, the left rule always takes the lowest point of each strip and **underestimates**, while the right rule always takes the highest point and **overestimates**.

**Trapezoidal rule** — instead of a flat rectangle, join the two ends with a slanted line, making a trapezium. Its area uses the *average* of the two heights:

$$
\sum_{x=1}^{9}\frac{x + (x+1)}{2} = \frac{1+2}{2} + \frac{2+3}{2} + \cdots + \frac{9+10}{2} = 49.5
$$

Exactly right, first time, with only nine strips. That happens because $f(x) = x$ is a straight line, and a trapezium's slanted top matches a straight line perfectly. For a curve it would not be exact — but it is still far better than either rectangle rule, because it is the average of an underestimate and an overestimate.

> [!TIP]
> **Predict before running the lab.** The left rule gave $45$ and the right rule gave $54$ on this increasing function. What would the **midpoint** rule give — taking the height at the centre of each strip? And would you expect it to be better or worse than the trapezoidal rule on a curve like $f(x) = x^2$? Decide both before opening the answers.

## 4. Which rule, and how fast each one converges

Each rule differs only in where the sample point sits, and that small choice changes how fast the error dies.

| Rule | Where it samples | Error shrinks like |
| :--- | :--- | :--- |
| Left | the start of each strip | $O(h)$ |
| Right | the end of each strip | $O(h)$ |
| Midpoint | the centre of each strip | $O(h^2)$ |
| Trapezoidal | average of both ends | $O(h^2)$ |

Here $h$ is the step width $\Delta x$. Reading that last column: halving the step width **halves** the error for the left and right rules, but **quarters** it for the midpoint and trapezoidal rules. That difference compounds, and by $n = 1000$ it is enormous. The lab measures it.

The midpoint rule beating the left and right rules is worth a moment's thought. It samples exactly one point per strip, the same as they do, and costs exactly the same to compute — but its errors on the two halves of each strip partly cancel, and that cancellation buys a whole order of accuracy for free.

## Worked example — runnable

**Runnable example:** save as `riemann.py` in any empty directory and run `python3 riemann.py`. Standard library only; writes no files.

```python
"""Turning an integral into a sum, and watching the error shrink."""
import math


def left_sum(f, a, b, n):
    h = (b - a) / n
    return sum(f(a + i * h) for i in range(n)) * h


def right_sum(f, a, b, n):
    h = (b - a) / n
    return sum(f(a + (i + 1) * h) for i in range(n)) * h


def midpoint_sum(f, a, b, n):
    h = (b - a) / n
    return sum(f(a + (i + 0.5) * h) for i in range(n)) * h


def trapezoid_sum(f, a, b, n):
    h = (b - a) / n
    total = (f(a) + f(b)) / 2
    total += sum(f(a + i * h) for i in range(1, n))
    return total * h


RULES = [("left", left_sum), ("right", right_sum),
         ("midpoint", midpoint_sum), ("trapezoid", trapezoid_sum)]


if __name__ == "__main__":
    print("Block 1 - the worked example, with a step width of exactly 1")
    f = lambda x: x
    exact = 49.5
    print(f"  integral of x from 1 to 10, exact answer {exact}")
    for name, rule in RULES:
        got = rule(f, 1, 10, 9)
        print(f"    {name:10} with 9 strips: {got:8.4f}   error {got - exact:+8.4f}")
    assert abs(left_sum(f, 1, 10, 9) - 45.0) < 1e-9
    assert abs(right_sum(f, 1, 10, 9) - 54.0) < 1e-9
    assert abs(trapezoid_sum(f, 1, 10, 9) - 49.5) < 1e-9
    assert abs(midpoint_sum(f, 1, 10, 9) - 49.5) < 1e-9
    print("  left underestimates and right overestimates, because x is increasing.")
    print("  Trapezoid and midpoint are EXACT here, because a straight line is")
    print("  matched perfectly by a straight-topped trapezium.")

    print()
    print("Block 2 - on a curve, the rules separate")
    g = lambda x: x * x
    exact_g = (10 ** 3 - 1 ** 3) / 3          # integral of x^2 is x^3/3
    print(f"  integral of x^2 from 1 to 10, exact answer {exact_g:.6f}")
    print("       n        left       right    midpoint   trapezoid")
    for n in (9, 90, 900):
        row = "".join(f"{rule(g, 1, 10, n):12.4f}" for _, rule in RULES)
        print(f"  {n:6}{row}")
    for name, rule in RULES:
        assert abs(rule(g, 1, 10, 100000) - exact_g) < 0.01, name
    print("  every rule converges to the same answer - they differ only in how fast")

    print()
    print("Block 3 - how fast the error shrinks when you halve the step")
    print("       n   left error   ratio    midpoint error   ratio")
    prev_l = prev_m = None
    for n in (10, 20, 40, 80, 160, 320):
        el = abs(left_sum(g, 1, 10, n) - exact_g)
        em = abs(midpoint_sum(g, 1, 10, n) - exact_g)
        rl = "     " if prev_l is None else f"{prev_l/el:5.2f}"
        rm = "     " if prev_m is None else f"{prev_m/em:5.2f}"
        print(f"  {n:6}   {el:10.6f}   {rl}    {em:14.8f}   {rm}")
        prev_l, prev_m = el, em
    # doubling n halves the left error and quarters the midpoint error
    e1 = abs(left_sum(g, 1, 10, 100) - exact_g)
    e2 = abs(left_sum(g, 1, 10, 200) - exact_g)
    assert 1.9 < e1 / e2 < 2.1, "left rule is O(h)"
    m1 = abs(midpoint_sum(g, 1, 10, 100) - exact_g)
    m2 = abs(midpoint_sum(g, 1, 10, 200) - exact_g)
    assert 3.8 < m1 / m2 < 4.2, "midpoint rule is O(h^2)"
    print("  the ratio column IS the convergence rate: about 2 for the left rule,")
    print("  about 4 for the midpoint rule. Same cost per strip, twice the order.")

    print()
    print("Block 4 - an integral with no elementary antiderivative")
    # exp(-x^2) has no antiderivative you can write down, but the area is fine
    h = lambda x: math.exp(-x * x)
    reference = midpoint_sum(h, 0, 2, 2000000)
    print("  integral of e^(-x^2) from 0 to 2 - no formula exists for this one")
    print("       n   midpoint estimate   difference from a very fine grid")
    for n in (4, 16, 64, 256):
        got = midpoint_sum(h, 0, 2, n)
        print(f"  {n:6}   {got:17.10f}   {abs(got - reference):.2e}")
    assert abs(midpoint_sum(h, 0, 2, 256) - reference) < 1e-6
    print("  this is the normal case. Most integrals that matter cannot be done by")
    print("  hand at all, and discretising is not a shortcut - it is the only route.")

    print()
    print("Block 5 - the trade-off every engineer actually makes")
    print("  more strips means more accuracy and more work. That is the whole decision.")
    print("       n   evaluations   midpoint error on x^2")
    for n in (10, 100, 1000, 10000):
        err = abs(midpoint_sum(g, 1, 10, n) - exact_g)
        print(f"  {n:6}   {n:11,}   {err:.10f}")
    print("  a medical monitor sampling too slowly saves battery and may miss an")
    print("  event; sampling too fast drains the battery by lunchtime. Choosing n")
    print("  IS the engineering - the formula was never the hard part.")

    print()
    print("riemann: passed")
```

Expected output:

```
Block 1 - the worked example, with a step width of exactly 1
  integral of x from 1 to 10, exact answer 49.5
    left       with 9 strips:  45.0000   error  -4.5000
    right      with 9 strips:  54.0000   error  +4.5000
    midpoint   with 9 strips:  49.5000   error  +0.0000
    trapezoid  with 9 strips:  49.5000   error  +0.0000
  left underestimates and right overestimates, because x is increasing.
  Trapezoid and midpoint are EXACT here, because a straight line is
  matched perfectly by a straight-topped trapezium.

Block 2 - on a curve, the rules separate
  integral of x^2 from 1 to 10, exact answer 333.000000
       n        left       right    midpoint   trapezoid
       9    285.0000    384.0000    332.2500    334.5000
      90    328.0650    337.9650    332.9925    333.0150
     900    332.5052    333.4952    332.9999    333.0002
  every rule converges to the same answer - they differ only in how fast

Block 3 - how fast the error shrinks when you halve the step
       n   left error   ratio    midpoint error   ratio
      10    43.335000                0.60750000        
      20    21.971250    1.97        0.15187500    4.00
      40    11.061562    1.99        0.03796875    4.00
      80     5.549766    1.99        0.00949219    4.00
     160     2.779629    2.00        0.00237305    4.00
     320     1.391001    2.00        0.00059326    4.00
  the ratio column IS the convergence rate: about 2 for the left rule,
  about 4 for the midpoint rule. Same cost per strip, twice the order.

Block 4 - an integral with no elementary antiderivative
  integral of e^(-x^2) from 0 to 2 - no formula exists for this one
       n   midpoint estimate   difference from a very fine grid
       4        0.8827889485   7.08e-04
      16        0.8821288703   4.75e-05
      64        0.8820843710   2.98e-06
     256        0.8820815771   1.86e-07
  this is the normal case. Most integrals that matter cannot be done by
  hand at all, and discretising is not a shortcut - it is the only route.

Block 5 - the trade-off every engineer actually makes
  more strips means more accuracy and more work. That is the whole decision.
       n   evaluations   midpoint error on x^2
      10            10   0.6075000000
     100           100   0.0060750000
    1000         1,000   0.0000607500
   10000        10,000   0.0000006075
  a medical monitor sampling too slowly saves battery and may miss an
  event; sampling too fast drains the battery by lunchtime. Choosing n
  IS the engineering - the formula was never the hard part.

riemann: passed
```

Block 3 is the one to study. The ratio column is the convergence rate, measured rather than asserted: doubling the number of strips halves the left rule's error and quarters the midpoint rule's, for exactly the same amount of work.

## Common pitfalls and traps

- **Using $n$ where you meant $n+1$.** Chopping an interval into $n$ pieces creates $n+1$ boundary points. The left rule uses the first $n$ of them and the right rule uses the last $n$. Off-by-one here is the most common bug in this whole topic.
- **Assuming more strips is always better.** Beyond a point, rounding error in the additions grows faster than the method error shrinks, and the answer gets *worse*. There is an optimal $n$, and it is not infinity.
- **Forgetting which direction the error runs.** For an increasing function the left rule underestimates and the right overestimates. For a decreasing function it is the other way round. Neither is "the safe one".
- **Reaching for the left or right rule at all.** The midpoint rule costs exactly the same per strip and is an order more accurate. There is almost no reason to use the plain rectangle rules except to explain the idea.
- **Thinking the trapezoidal rule is always better than the midpoint rule.** It is not — they are both $O(h^2)$, and for smooth functions the midpoint rule's error is typically about half the trapezoidal rule's, and in the opposite direction.

## Check your understanding

1. Write down $\Delta x$ and $x_i$ for $\int_0^4 f(x)\,dx$ split into $8$ pieces.
2. For an increasing function, which is bigger — the left sum or the right sum?
3. You halve the step width using the trapezoidal rule. What happens to the error?
4. Why is the trapezoidal rule exact for $\int_1^{10} x\,dx$?
5. Why can a computer never compute a true integral?

<details><summary>Answers — open only after an attempt</summary>

1. $\Delta x = \frac{4-0}{8} = 0.5$, and $x_i = 0 + 0.5i$, so the sample points are $0, 0.5, 1.0, \dots, 4.0$.
2. The **right** sum. For an increasing function the height at the end of each strip is greater than the height at the start, so every rectangle is taller.
3. It drops to about **a quarter** of what it was. The trapezoidal rule is $O(h^2)$, so halving $h$ divides the error by $2^2 = 4$.
4. Because $f(x) = x$ is a straight line, and the slanted top of a trapezium is also a straight line. The shape matches the function exactly, so there is no gap to be wrong about.
5. Because the true integral is defined as a **limit** as the number of strips goes to infinity, and a computer has finite memory and finite time. It can only ever add up a finite number of pieces, so it always computes an approximation — the skill is in knowing how close it is.

**And the prediction from section 3:** the midpoint rule gives **exactly $49.5$** as well. On a straight line the centre height of each strip is precisely the average of the two end heights, so the rectangle has exactly the same area as the trapezium. On a curve like $x^2$ the two separate, and the midpoint rule is typically about **twice as accurate** as the trapezoidal rule, with its error in the opposite direction — which is exactly the cancellation Simpson's rule exploits.
</details>

## Practice — independent task

Write `integrate(f, a, b, tolerance)` that chooses $n$ for itself, instead of being told.

1. Start with some small $n$. Compute the estimate, then double $n$ and compute it again.
2. Use the difference between the two as an estimate of the error. Keep doubling until that difference falls below `tolerance`, then return the finer answer and the $n$ you needed.
3. **Test it on functions whose answers you know:** $\int_1^{10}x\,dx = 49.5$, $\int_0^\pi \sin x\,dx = 2$, and $\int_0^1 e^x dx = e - 1$. Assert each result is genuinely within the tolerance you asked for.
4. Report the $n$ required for each, at tolerances of $10^{-3}$, $10^{-6}$ and $10^{-9}$. Compare the midpoint rule against the left rule and state how many times more evaluations the left rule needs for the same accuracy.
5. **Then find where it breaks.** Try $\int_0^1 \sqrt{x}\,dx$, whose derivative is infinite at $0$, and $\int_0^1 \sin(1/x)\,dx$, which oscillates infinitely fast near $0$. Report what your function does on each and explain why doubling $n$ stops helping in the way the theory promised.

**Edge cases:** $a = b$ (the answer is zero — does your loop terminate?); $a > b$ (the sign should flip); a tolerance so small that rounding error stops you ever reaching it — detect this and give up gracefully rather than looping forever.

**Done when:** all three known integrals come back within tolerance, your table of required $n$ shows the midpoint rule needing far fewer evaluations, and you can explain both step-5 failures rather than just reporting them.

## Before moving on

You are done with this lesson when you can take any definite integral, write down its discrete form with $\Delta x$ and $x_i$ worked out, and say how fast each rule's error shrinks.

**Recap for later lookup:** $\Delta x = \frac{b-a}{n}$ and $x_i = a + i\Delta x$; the discrete form is $\sum f(x_i)\Delta x$, and the true integral is its limit as $n \to \infty$; the **left** rule samples the start of each strip and the **right** rule the end, both $O(h)$; the **midpoint** rule samples the centre and the **trapezoidal** rule averages the two ends, both $O(h^2)$; for an increasing function left underestimates and right overestimates; more strips is not always better, because rounding error eventually wins.

**Next:** [[02-quadrature-rules|Quadrature Rules]] — Simpson's rule and Gaussian quadrature, which get far more accuracy out of the same number of function evaluations.

## Related

- [[03-calculus-2/01-integration-by-parts|Integration]] — where the limit definition comes from
- [[02-quadrature-rules|Quadrature Rules]] — the better rules built on this idea
- [[01-why-numerical-methods|Why Numerical Methods]] — the general case of "computers cannot do infinity"
- [[digital-signal-processing/02-sampling-and-aliasing|Sampling and Aliasing]] — the same trade-off for signals, where sampling too slowly does not merely lose detail but invents a wrong answer
