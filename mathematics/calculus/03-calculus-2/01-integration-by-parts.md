# Integration and Integration by Parts

**[Intermediate]** — The other half of calculus: reversing differentiation to recover accumulated totals, and the technique for integrating a product.

## Before you start

- You can differentiate fluently, including the product and chain rules — [[01-rules|derivative rules]].
- You know what the Fundamental Theorem claims — [[01-preview|calculus preview]].

**What you will be able to do after this lesson:**

1. Explain integration as antidifferentiation and as accumulated area, and why they are the same.
2. State the Fundamental Theorem and use it to evaluate a definite integral.
3. Apply integration by parts and choose $u$ and $dv$ sensibly.
4. Explain why integration is harder than differentiation.

---

## 1. Two definitions that turn out to agree

**Antiderivative.** $F$ is an antiderivative of $f$ when $F' = f$. Differentiation run backwards.

$$\int 2x\,dx = x^2 + C$$

**The $+C$ is not a formality.** Every constant differentiates to zero, so $x^2$, $x^2+7$ and $x^2-100$ all have derivative $2x$. **Antiderivatives come in families**, and $C$ names the family.

**Definite integral.** $\int_a^b f(x)\,dx$ is the accumulated area under $f$ between $a$ and $b$, defined as the limit of a sum of thin rectangles:

$$\int_a^b f(x)\,dx = \lim_{n\to\infty}\sum_{i=1}^{n} f(x_i)\,\Delta x$$

**These two things have no obvious connection.** One reverses a derivative; the other adds up areas.

## 2. The Fundamental Theorem

**They are the same operation.**

$$\int_a^b f(x)\,dx = F(b) - F(a) \qquad\text{where } F' = f$$

**Why it is believable:** let $A(x)$ be the area accumulated from $a$ up to $x$. Extend $x$ by a sliver $h$; the area grows by approximately $f(x)\cdot h$, a thin rectangle. So

$$\frac{A(x+h) - A(x)}{h} \approx f(x)$$

and taking $h \to 0$ gives $A'(x) = f(x)$. **The area function's derivative is the original function** — so area is antidifferentiation.

**The practical consequence is enormous.** Computing an area no longer requires summing infinitely many rectangles; you find any antiderivative and subtract two values.

$$\int_0^3 x^2\,dx = \left[\frac{x^3}{3}\right]_0^3 = 9 - 0 = 9$$

**And the $C$ cancels** in the subtraction, which is why definite integrals do not carry one.

## 3. The basic antiderivatives

| $f(x)$ | $\int f(x)\,dx$ |
| :--- | :--- |
| $x^n$ ($n \neq -1$) | $\dfrac{x^{n+1}}{n+1} + C$ |
| $\dfrac{1}{x}$ | $\ln|x| + C$ |
| $e^x$ | $e^x + C$ |
| $\cos x$ | $\sin x + C$ |
| $\sin x$ | $-\cos x + C$ |

**Note the exception at $n = -1$.** The power rule would give $\frac{x^0}{0}$, which is undefined — and that gap is exactly where the logarithm lives. **$\ln$ is not an unrelated special case; it is the missing entry in the power rule's table.**

## 4. Why integration is harder than differentiation

**Differentiation is mechanical.** Every elementary function has an elementary derivative, and the rules compose without judgement — you can always just apply them.

**Integration is not.** There is no rule that reverses the product rule or the chain rule in general, so you need *techniques* and *judgement about which to try*.

**Worse, some elementary functions have no elementary antiderivative at all:**

$$\int e^{-x^2}\,dx$$

is not expressible in terms of any combination of polynomials, exponentials, logs and trigonometric functions. **This is a proved impossibility, not a gap in anyone's cleverness** — and that integral is the normal distribution, which is why statistics uses tables and numerical methods rather than a formula.

## 5. Integration by parts

**It is the product rule, reversed.** Start from

$$\frac{d}{dx}(uv) = u'v + uv'$$

Integrate both sides and rearrange:

$$\int u\,dv = uv - \int v\,du$$

**What it does:** trades one integral for another. **It only helps if the new one is easier.**

### Worked example

$$\int x e^x\,dx$$

Choose $u = x$ (so $du = dx$) and $dv = e^x dx$ (so $v = e^x$):

$$= xe^x - \int e^x\,dx = xe^x - e^x + C = e^x(x-1) + C$$

**Check by differentiating:** $\frac{d}{dx}[e^x(x-1)] = e^x(x-1) + e^x = xe^x$ ✓

**Always check.** Differentiation is easy, so verifying an integral costs almost nothing.

### Choosing $u$ — the LIATE guide

Pick $u$ as the first type that appears, in this order:

**L**ogarithmic · **I**nverse trig · **A**lgebraic · **T**rigonometric · **E**xponential

**The reasoning:** you want $u$ to get *simpler* when differentiated, and $dv$ to be something you can integrate. Logs simplify dramatically ($\ln x \to \frac{1}{x}$); exponentials never simplify, so they make better $dv$.

**The trick case:** $\int \ln x\,dx$ has no obvious product. Take $u = \ln x$ and $dv = dx$:

$$= x\ln x - \int x\cdot\frac{1}{x}dx = x\ln x - x + C$$

## 6. Practice — problems

1. Evaluate: (a) $\int (3x^2 - 4x + 1)dx$  (b) $\int \frac{1}{x^2}dx$  (c) $\int (e^x + \sin x)dx$.
2. Definite integrals: (a) $\int_1^2 x^3 dx$  (b) $\int_0^{\pi} \sin x\,dx$  (c) $\int_1^e \frac{1}{x}dx$.
3. Integration by parts: (a) $\int x\cos x\,dx$  (b) $\int x^2 e^x dx$ *(twice)*  (c) $\int \ln x\,dx$.
4. **Why does $\int \frac{1}{x}dx$ give $\ln|x|$ and not $\frac{x^0}{0}$?** What does the absolute value protect against?
5. Evaluate $\int_0^2 (x^2+1)dx$ and sketch the region whose area you computed.
6. **Explain** why $\int_a^b f(x)dx$ can be negative, and what that means physically if $f$ is a velocity.

<details><summary>Answers — open only after an attempt</summary>

1. (a) $x^3 - 2x^2 + x + C$. (b) $\int x^{-2}dx = -x^{-1} + C = -\frac1x + C$. (c) $e^x - \cos x + C$.
2. (a) $\left[\frac{x^4}{4}\right]_1^2 = 4 - 0.25 = 3.75$. (b) $[-\cos x]_0^\pi = 1-(-1) = 2$. (c) $[\ln x]_1^e = 1 - 0 = 1$.
3. (a) $u=x, dv=\cos x\,dx$: $x\sin x + \cos x + C$. (b) Apply parts twice: $e^x(x^2 - 2x + 2) + C$. (c) $x\ln x - x + C$.
4. The power rule adds one to the exponent, and $-1 + 1 = 0$, giving $\frac{x^0}{0}$ — division by zero. <strong>The logarithm fills exactly that hole.</strong> The absolute value covers $x < 0$, where $\ln x$ is undefined but $\frac{1}{x}$ is perfectly well defined, so the antiderivative must exist there too.
5. $\left[\frac{x^3}{3} + x\right]_0^2 = \frac83 + 2 = \frac{14}{3} \approx 4.67$ — the region under a parabola shifted up by 1, between $x=0$ and $x=2$.
6. Because area below the axis counts as negative. If $f$ is velocity, $\int f\,dt$ is <strong>displacement</strong>, not distance — travelling backwards subtracts. To get total distance you integrate $|f|$, which is why the two questions have different answers.
</details>

## Before moving on

- [ ] Explain integration both as antidifferentiation and as accumulated area.
- [ ] State the Fundamental Theorem and say why the $+C$ cancels in a definite integral.
- [ ] Apply integration by parts and choose $u$ using LIATE.
- [ ] Explain why integration is harder than differentiation, with an example that has no elementary antiderivative.

**Recap:** Integration is both the reverse of differentiation and the accumulation of area, and the Fundamental Theorem says those are the same operation — which is why an area can be found by subtracting two values of an antiderivative rather than summing infinitely many rectangles. Unlike differentiation, integration is not mechanical: it needs techniques and judgement, and some elementary functions provably have no elementary antiderivative. Integration by parts reverses the product rule, trading one integral for another that you hope is easier.

**Next:** [[02-partial-fractions|Partial Fractions]] — a technique for integrating rational functions by splitting them apart.

## Related

- [[01-rules|Derivative rules]] · [[01-preview|Calculus preview]]
