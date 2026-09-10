# Multiple Integrals

**[Intermediate → Advanced]** — Accumulating over a region rather than an interval, and why changing the order of integration is sometimes the whole solution.

## Before you start

- You can evaluate definite integrals — [[01-integration-by-parts|integration]].
- You understand partial derivatives — [[01-partial-derivatives|partial derivatives]].

**What you will be able to do after this lesson:**

1. Evaluate a double integral as an iterated integral.
2. Set up the limits for a non-rectangular region.
3. Change the order of integration and say when it is necessary.
4. Convert to polar coordinates and explain the Jacobian factor.

---

## 1. From intervals to regions

**A single integral accumulates along a line:** $\int_a^b f(x)\,dx$ adds up strips of width $dx$.

**A double integral accumulates over an area:**

$$\iint_R f(x,y)\,dA$$

**One slice is now a tiny rectangle** of area $dA = dx\,dy$, and $f(x,y)$ is its height — so the whole thing is a volume under a surface, just as the single integral was an area under a curve.

## 2. Iterated integration

**You never evaluate a double integral directly. You do two ordinary integrals, one inside the other.**

$$\iint_R f\,dA = \int_c^d\left[\int_a^b f(x,y)\,dx\right]dy$$

**The inner integral treats $y$ as a constant** — exactly like a partial derivative in reverse. The result is a function of $y$, which the outer integral then handles.

**Worked, over the rectangle $0\le x\le2$, $0\le y\le3$:**

$$\int_0^3\int_0^2 xy\,dx\,dy = \int_0^3\left[\frac{x^2y}{2}\right]_0^2 dy = \int_0^3 2y\,dy = \left[y^2\right]_0^3 = 9$$

**Over a rectangle with fixed limits, the order does not matter** — Fubini's theorem. Over anything else, it can matter a great deal.

## 3. Non-rectangular regions

**When the region is bounded by curves, the inner limits become functions.**

For the region under $y = x^2$, between $x=0$ and $x=2$:

$$\int_0^2\int_0^{x^2} f(x,y)\,dy\,dx$$

**Read it inside out:** for each fixed $x$, $y$ runs from $0$ up to $x^2$; then $x$ runs across $[0,2]$.

**The rule that prevents most errors: the outer limits must be constants.** If your outer integral still has a variable in its limits, the setup is wrong — there would be nothing left to substitute it with.

> [!NOTE]
> **Always sketch the region.** Nearly every mistake in multiple integration is a limits mistake, and limits are geometry — they are far easier to see than to derive algebraically.
>
> Sketch it, decide whether to slice vertically or horizontally, and read the limits off the picture.

## 4. Changing the order

**Sometimes reversing the order turns an impossible integral into an easy one.**

$$\int_0^1\int_x^1 e^{y^2}\,dy\,dx$$

**The inner integral cannot be done** — $\int e^{y^2}dy$ has no elementary antiderivative, as [[01-integration-by-parts|noted earlier]].

**Sketch the region:** $x$ from 0 to 1, and $y$ from $x$ to 1. That is the triangle above the line $y = x$ inside the unit square.

**Describe the same triangle the other way:** $y$ from 0 to 1, and for each $y$, $x$ runs from 0 to $y$:

$$\int_0^1\int_0^y e^{y^2}\,dx\,dy = \int_0^1 e^{y^2}\left[x\right]_0^y dy = \int_0^1 y\,e^{y^2}\,dy$$

**Now it is a substitution.** With $u = y^2$, $du = 2y\,dy$:

$$= \frac12\left[e^{y^2}\right]_0^1 = \frac{e-1}{2}$$

**The integral was always solvable — the first ordering just hid it.** That extra factor of $y$, which appeared from integrating $dx$ over $[0,y]$, is exactly what the substitution needed.

## 5. Polar coordinates

**Circular regions are painful in $x$ and $y$** — the limits involve $\sqrt{1-x^2}$ and similar.

**In polar coordinates** $x = r\cos\theta$, $y = r\sin\theta$, and:

$$dA = r\,dr\,d\theta$$

**That extra $r$ is not optional, and it is not a convention.** A small polar rectangle spanning $dr$ and $d\theta$ is not a rectangle of area $dr\,d\theta$ — it is a curved patch whose arc length grows with radius. **Its area is $r\,dr\,d\theta$**, because the arc subtended by $d\theta$ at radius $r$ has length $r\,d\theta$.

```
        the patch at large r is WIDER
        than the patch at small r
        for the same dθ

           ,--.___
         ,'   |   `--.
        /  dr |         <- arc length = r dθ
       |______|_____
        small r   large r
```

**Forgetting the $r$ is the single most common error in polar integration**, and it produces answers that are wrong by a factor that varies with the region.

**Example — area of a circle of radius $a$:**

$$\int_0^{2\pi}\int_0^a r\,dr\,d\theta = \int_0^{2\pi}\frac{a^2}{2}d\theta = \pi a^2 \checkmark$$

**And the Gaussian integral**, which cannot be done in one dimension, becomes possible in two:

$$\left(\int_{-\infty}^{\infty}e^{-x^2}dx\right)^2 = \iint e^{-(x^2+y^2)}dA = \int_0^{2\pi}\int_0^\infty e^{-r^2}r\,dr\,d\theta = \pi$$

so the original integral is $\sqrt\pi$. **The $r$ from the Jacobian is precisely what makes the substitution work** — this is the classic demonstration that the factor is real.

## 6. Practice — problems

1. Evaluate $\int_0^2\int_0^1 (x+y)\,dy\,dx$.
2. Evaluate $\int_0^1\int_0^{x} xy\,dy\,dx$. Sketch the region first.
3. Set up (do not evaluate) the double integral for the area between $y=x$ and $y=x^2$, both orders.
4. Reverse the order: $\int_0^1\int_{y}^{1}\sin(x^2)\,dx\,dy$, then evaluate.
5. Use polar coordinates to find $\iint_R (x^2+y^2)\,dA$ over the disc $x^2+y^2 \le 4$.
6. **Explain** why $dA = r\,dr\,d\theta$ rather than $dr\,d\theta$, in one sentence about arc length.

<details><summary>Answers — open only after an attempt</summary>

1. Inner: $\int_0^1(x+y)dy = x + \frac12$. Outer: $\int_0^2(x+\frac12)dx = 2 + 1 = 3$.
2. Inner: $\int_0^x xy\,dy = \frac{x^3}{2}$. Outer: $\int_0^1\frac{x^3}{2}dx = \frac18$. The region is the triangle below $y=x$ over $[0,1]$.
3. The curves meet at $x=0$ and $x=1$, with $x \ge x^2$ between. <strong>$dy\,dx$:</strong> $\int_0^1\int_{x^2}^{x}dy\,dx$. <strong>$dx\,dy$:</strong> $\int_0^1\int_{y}^{\sqrt y}dx\,dy$ — note the limits swap roles because the same region is now sliced horizontally.
4. The region is $0\le y\le1$, $y\le x\le1$ — the triangle above $y=x$. Reversed: $\int_0^1\int_0^x \sin(x^2)dy\,dx = \int_0^1 x\sin(x^2)dx = \left[-\frac{\cos(x^2)}{2}\right]_0^1 = \frac{1-\cos 1}{2}$.
5. $x^2+y^2 = r^2$, so $\int_0^{2\pi}\int_0^2 r^2\cdot r\,dr\,d\theta = \int_0^{2\pi}\left[\frac{r^4}{4}\right]_0^2 d\theta = 4\cdot2\pi = 8\pi$.
6. Because the patch swept by a fixed angle $d\theta$ has arc length $r\,d\theta$, which grows with radius — so a patch far from the origin covers more area than one near it, and the $r$ accounts for that stretching.
</details>

## Before moving on

- [ ] Evaluate a double integral as two nested ordinary integrals.
- [ ] Set up limits for a non-rectangular region, keeping the outer limits constant.
- [ ] Reverse the order of integration and explain when it helps.
- [ ] Explain the $r$ in $dA = r\,dr\,d\theta$ geometrically.

**Recap:** A double integral accumulates over a region, and is evaluated as two nested single integrals with the inner one treating the outer variable as constant. Over a rectangle the order is free; over a curved region the inner limits become functions and the outer limits must remain constants. Reversing the order can turn an impossible inner integral into a routine substitution. Polar coordinates simplify circular regions, and the Jacobian factor $r$ is required because a patch's area grows with its distance from the origin.

**Next:** [[03-optimization|Optimisation]] — finding extrema of a function of several variables, with and without constraints.

## Related

- [[01-partial-derivatives|Partial derivatives]] · [[01-integration-by-parts|Integration]]
