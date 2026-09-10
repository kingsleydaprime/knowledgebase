# Applications of Integration

**[Intermediate]** — What integrals compute once you stop thinking of them as reversed derivatives: volumes, lengths, averages, and probability.

## Before you start

- You can evaluate definite integrals — [[01-integration-by-parts|integration]].
- You know the Fundamental Theorem — [[01-preview|calculus preview]].

**What you will be able to do after this lesson:**

1. Compute the area between two curves.
2. Compute a volume of revolution by discs and by shells, and choose between them.
3. Compute the average value of a function and say why it is not the average of the endpoints.
4. Explain why probability density integrates to 1.

---

## 1. The pattern behind every application

**All of these follow one recipe**, and recognising it is worth more than memorising the formulas:

1. **Slice** the quantity into pieces so thin that each is approximately something simple — a rectangle, a disc, a straight segment.
2. **Write one slice** in terms of $x$ and a width $dx$.
3. **Integrate** to add up all the slices.

**Every formula below is step 2.** If you can write one slice, the integral writes itself.

## 2. Area between curves

$$A = \int_a^b [f(x) - g(x)]\,dx \qquad\text{where } f \ge g$$

**One slice** is a rectangle of height $f(x)-g(x)$ and width $dx$.

**Find the intersections first** — they are the limits. And **if the curves cross inside the interval**, split the integral at the crossing, because the sign of $f - g$ flips and the areas would cancel.

**Example:** between $y=x^2$ and $y=x$ from 0 to 1. Here $x \ge x^2$ on that interval:

$$\int_0^1 (x - x^2)dx = \left[\frac{x^2}{2}-\frac{x^3}{3}\right]_0^1 = \frac12 - \frac13 = \frac16$$

## 3. Volumes of revolution

Rotate a region about an axis and it sweeps out a solid.

**Disc method** — slices perpendicular to the axis are circles:

$$V = \pi\int_a^b [f(x)]^2\,dx$$

**One slice** is a disc of radius $f(x)$ and thickness $dx$, so volume $\pi r^2\,dx$.

**Example:** $y = x^2$ from 0 to 2, about the $x$-axis:

$$V = \pi\int_0^2 x^4\,dx = \pi\left[\frac{x^5}{5}\right]_0^2 = \frac{32\pi}{5}$$

**Shell method** — slices parallel to the axis are cylindrical shells:

$$V = 2\pi\int_a^b x\,f(x)\,dx$$

**One slice** is a thin cylinder of radius $x$, height $f(x)$, thickness $dx$ — unrolled, it is a rectangle of area $2\pi x \cdot f(x)$.

> [!NOTE]
> **Choose by which one avoids solving for the other variable.**
>
> Rotating about the $x$-axis, discs need $f(x)$ — which you already have. Rotating about the $y$-axis, discs would need $x$ as a function of $y$, which may be awkward or impossible; shells keep everything in $x$.
>
> **Both always give the same answer.** The choice is purely about which integral you can actually evaluate.

## 4. Arc length

$$L = \int_a^b \sqrt{1 + [f'(x)]^2}\,dx$$

**Derivation from one slice:** a tiny piece of curve is almost straight, so by Pythagoras

$$ds = \sqrt{dx^2 + dy^2} = \sqrt{1 + \left(\frac{dy}{dx}\right)^2}\,dx$$

**Be warned: these integrals are usually not elementary.** Even the arc length of a parabola needs a substitution and a logarithm, and the arc length of an ellipse has *no* elementary form — that is where elliptic integrals come from, and they are named after exactly this failure.

## 5. Average value

$$f_{\text{avg}} = \frac{1}{b-a}\int_a^b f(x)\,dx$$

**Read it as the discrete average generalised.** For $n$ numbers you add and divide by $n$; for a continuous function you integrate and divide by the width of the interval.

**It is not the average of the endpoints.** For $f(x)=x^2$ on $[0,3]$:

$$f_{\text{avg}} = \frac13\int_0^3 x^2dx = \frac13\cdot 9 = 3$$

whereas the endpoint average would be $\frac{0+9}{2} = 4.5$. **The function spends most of the interval well below its final value**, and the integral accounts for that; the endpoints do not.

## 6. Probability

**For a continuous random variable, probability is area under the density curve:**

$$P(a \le X \le b) = \int_a^b f(x)\,dx \qquad\text{and}\qquad \int_{-\infty}^{\infty} f(x)\,dx = 1$$

**The total must be 1 because something must happen.** That is the entire meaning of the normalisation condition.

**And it explains why $P(X = c) = 0$ for any single value** — the integral over an interval of zero width is zero. A continuous variable has zero probability of any exact value, which sounds paradoxical until you notice that *the same is true of hitting an exact point on a dartboard*.

**This is why the normal distribution needs tables.** Its density is $e^{-x^2/2}$ up to constants, and [[01-integration-by-parts|as noted]], $\int e^{-x^2}dx$ has no elementary antiderivative. **Statistics uses numerical values because the algebra provably cannot be done.**

## 7. Practice — problems

1. Find the area between $y = x^2$ and $y = 2x$.
2. Find the area between $y=\sin x$ and $y=\cos x$ from $0$ to $\frac{\pi}{4}$.
3. Rotate $y=\sqrt{x}$, $0 \le x \le 4$, about the $x$-axis. Find the volume by discs.
4. Rotate the same region about the $y$-axis using **shells**, and explain why discs would be awkward here.
5. Find the average value of $f(x)=\sin x$ on $[0,\pi]$. **Is it more or less than $\frac12$?** Explain.
6. A density is $f(x)=kx$ on $[0,2]$ and zero elsewhere. Find $k$, then $P(0 \le X \le 1)$.
7. **Explain** why $P(X = 1) = 0$ for a continuous variable, and why that is not the same as saying it is impossible.

<details><summary>Answers — open only after an attempt</summary>

1. They meet where $x^2 = 2x$, at $x=0$ and $x=2$. On that interval $2x \ge x^2$: $\int_0^2(2x-x^2)dx = \left[x^2-\frac{x^3}{3}\right]_0^2 = 4-\frac83 = \frac43$.
2. On $[0,\frac\pi4]$, $\cos x \ge \sin x$: $\int_0^{\pi/4}(\cos x-\sin x)dx = [\sin x+\cos x]_0^{\pi/4} = \sqrt2 - 1 \approx 0.414$.
3. $V = \pi\int_0^4 x\,dx = \pi\left[\frac{x^2}{2}\right]_0^4 = 8\pi$.
4. Shells: $V = 2\pi\int_0^4 x\sqrt x\,dx = 2\pi\int_0^4 x^{3/2}dx = 2\pi\cdot\frac{2}{5}\left[x^{5/2}\right]_0^4 = \frac{128\pi}{5}$. Discs would require rewriting as $x = y^2$ and integrating in $y$ with different limits — <strong>possible here but more work, and impossible when the function cannot be inverted</strong>.
5. $\frac{1}{\pi}\int_0^\pi \sin x\,dx = \frac{2}{\pi} \approx 0.637$ — <strong>more</strong> than $\frac12$, because the sine curve bulges above the straight line joining its endpoints for the whole interval.
6. $\int_0^2 kx\,dx = 2k = 1$, so $k=\frac12$. Then $P(0\le X\le1) = \int_0^1\frac{x}{2}dx = \frac14$.
7. The integral over a zero-width interval is zero, so every exact value has probability zero. <strong>Zero probability is not impossibility</strong> for continuous variables — the variable does take <em>some</em> exact value every time. Probability zero means "negligible among a continuum of alternatives", which is why continuous probability is always stated over intervals.
</details>

## Before moving on

- [ ] State the slice-write-integrate recipe and apply it to a new quantity.
- [ ] Compute area between curves, splitting where they cross.
- [ ] Choose between discs and shells and justify the choice.
- [ ] Explain why a probability density must integrate to 1.

**Recap:** Every application of integration follows one recipe — slice the quantity into pieces each of which is approximately simple, write a single slice in terms of $dx$, and integrate. That gives area between curves, volumes by discs or shells, arc length, average value and probability. Choosing between discs and shells is about avoiding an inversion, not about correctness. Probability density integrates to 1 because something must happen, and single values have probability zero without being impossible.

**This is the end of Calculus 2.**

**Next:** [[01-partial-derivatives|Calculus 3]] — the same ideas with more than one input variable.

## Related

- [[01-integration-by-parts|Integration]] · [[02-partial-fractions|Partial fractions]]
- [[ai-ml/01-data-scientist/03-inferential-statistics|ai-ml/inferential statistics]] — where these densities are used
