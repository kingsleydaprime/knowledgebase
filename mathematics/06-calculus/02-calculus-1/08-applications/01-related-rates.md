# Applications of the Derivative

**[Intermediate]** — Using derivatives to answer questions: how fast is *this* changing given *that*, and where is a quantity largest.

## Before you start

- You can apply all the derivative rules, especially the chain rule — [[01-rules|derivative rules]].
- You know the Extreme Value Theorem — [[01-definition|continuity]].

**What you will be able to do after this lesson:**

1. Solve a related-rates problem by differentiating a relationship with respect to time.
2. Find critical points and classify them as maxima, minima or neither.
3. Solve an optimisation problem end to end, including checking the endpoints.
4. Explain what the second derivative tells you that the first does not.

---

## 1. Related rates

**The setup:** two quantities are related by an equation, both change over time, you know one rate and want the other.

**The move: differentiate the relationship with respect to time**, using the chain rule on every variable — because each is itself a function of $t$.

### Worked example

A ladder 5 m long leans against a wall. Its base slides away at 0.5 m/s. **How fast is the top sliding down when the base is 3 m from the wall?**

**Relationship** (Pythagoras): $x^2 + y^2 = 25$.

**Differentiate with respect to $t$** — note the chain rule on both terms:

$$2x\frac{dx}{dt} + 2y\frac{dy}{dt} = 0$$

**Substitute the known instant.** When $x = 3$: $y = \sqrt{25-9} = 4$, and $\frac{dx}{dt} = 0.5$:

$$2(3)(0.5) + 2(4)\frac{dy}{dt} = 0 \quad\Rightarrow\quad \frac{dy}{dt} = -\frac{3}{8} = -0.375 \text{ m/s}$$

**Negative means the top is descending**, as it must be.

> [!NOTE]
> **Substitute the specific values only after differentiating.** Putting $x = 3$ into the relationship first gives $9 + y^2 = 25$, a statement about one frozen instant with no $t$ in it — differentiating that yields $0 = 0$.
>
> **The relationship must hold for all $t$ when you differentiate it.** This is the single commonest error in related rates, and it is worth checking every time.

## 2. Critical points

**At a maximum or minimum of a smooth function, the tangent is horizontal**, so $f'(x) = 0$.

**A critical point is where $f'(x) = 0$ or $f'(x)$ does not exist.** Every interior extremum is a critical point — **but not every critical point is an extremum.**

$$f(x) = x^3 \quad\Rightarrow\quad f'(0) = 0$$

yet $x=0$ is neither a maximum nor a minimum. The curve flattens and continues rising — an **inflection point**.

**So finding critical points is step one, not the answer.**

## 3. Classifying them

**First derivative test** — check the sign of $f'$ either side:

| $f'$ before | $f'$ after | Conclusion |
| :--- | :--- | :--- |
| $+$ | $-$ | local **maximum** |
| $-$ | $+$ | local **minimum** |
| same sign | same sign | neither |

**Second derivative test** — usually faster:

- $f''(a) > 0$ → curve is concave up → **minimum**
- $f''(a) < 0$ → concave down → **maximum**
- $f''(a) = 0$ → **inconclusive**, fall back to the first derivative test

**What the second derivative means:** $f'$ tells you the direction; $f''$ tells you how the direction is *changing*. In motion, $s'$ is velocity and $s''$ is acceleration — and you can be moving forwards while decelerating, which is precisely $f' > 0$ with $f'' < 0$.

## 4. Optimisation

**The procedure:**

1. Write the quantity to be optimised as a function of one variable.
2. Use any constraint to eliminate the other variables.
3. Find critical points.
4. **Check the endpoints of the valid domain too.**
5. Compare all candidates and state the answer with units.

### Worked example

**A farmer has 100 m of fencing and wants the largest rectangular enclosure against a straight river, so only three sides need fencing.**

Let $x$ be the two perpendicular sides and $y$ the side parallel to the river.

**Constraint:** $2x + y = 100$, so $y = 100 - 2x$.

**Objective:** $A = xy = x(100-2x) = 100x - 2x^2$.

**Differentiate and solve:** $A' = 100 - 4x = 0 \Rightarrow x = 25$.

**Classify:** $A'' = -4 < 0$, so it is a maximum.

**Check the domain:** $x$ must lie in $[0, 50]$, and $A(0) = A(50) = 0$. So $x=25$ wins.

**Answer:** $25 \times 50$ m, area **1250 m²**.

**Note the shape of the answer** — the side parallel to the river is twice each perpendicular side. That relationship holds for any amount of fencing, which is a more useful result than the number.

> [!NOTE]
> **Step 4 is the one people skip.** The Extreme Value Theorem guarantees a maximum exists on a closed interval, but it does not promise it is at a critical point — it can sit at an endpoint.
>
> A function decreasing throughout $[0,10]$ has its maximum at $x = 0$, where $f' \neq 0$. **Checking endpoints is not optional.**

## 5. Practice — problems

1. A spherical balloon is inflated at 100 cm³/s. How fast is the radius growing when $r = 5$ cm? *(Volume $V = \frac{4}{3}\pi r^3$.)*
2. A 10 m ladder slides down a wall; the base moves out at 1 m/s. How fast does the top fall when the base is 6 m out?
3. Find and classify the critical points of $f(x) = x^3 - 3x^2 + 1$.
4. Find the maximum and minimum of $f(x) = x^3 - 3x$ on $[-2, 3]$. **Include the endpoints.**
5. A box with a square base and no lid must hold 32 000 cm³. Find the dimensions minimising the material used.
6. **Explain the error:** a student solving problem 2 substitutes $x = 6$ into $x^2 + y^2 = 100$ *before* differentiating, gets $y = 8$, and then differentiates to obtain $0 = 0$. What went wrong, in one sentence?

<details><summary>Answers — open only after an attempt</summary>

1. $\frac{dV}{dt} = 4\pi r^2\frac{dr}{dt}$, so $100 = 4\pi(25)\frac{dr}{dt}$, giving $\frac{dr}{dt} = \frac{1}{\pi} \approx 0.318$ cm/s.
2. $2x\frac{dx}{dt} + 2y\frac{dy}{dt} = 0$. At $x=6$, $y=8$: $12(1) + 16\frac{dy}{dt} = 0$, so $\frac{dy}{dt} = -0.75$ m/s.
3. $f' = 3x^2-6x = 3x(x-2)$, so critical points at $x=0$ and $x=2$. $f'' = 6x - 6$: at $x=0$, $f''=-6<0$ → <strong>local maximum</strong> $(0,1)$; at $x=2$, $f''=6>0$ → <strong>local minimum</strong> $(2,-3)$.
4. $f' = 3x^2-3 = 0$ at $x = \pm1$. Candidates: $f(-2)=-2$, $f(-1)=2$, $f(1)=-2$, $f(3)=18$. <strong>Maximum 18 at $x=3$ (an endpoint), minimum $-2$ at both $x=-2$ and $x=1$.</strong> The maximum is at an endpoint, not a critical point — which is exactly why step 4 exists.
5. Base $x$, height $h$, volume $x^2h = 32000$ so $h = \frac{32000}{x^2}$. Material $= x^2 + 4xh = x^2 + \frac{128000}{x}$. Differentiating: $2x - \frac{128000}{x^2} = 0 \Rightarrow x^3 = 64000 \Rightarrow x = 40$ cm, $h = 20$ cm.
6. Substituting first turns a relationship that holds <em>for all time</em> into a statement about <em>one frozen instant</em>, which contains no variables left to change — so differentiating it says nothing. <strong>Differentiate first, substitute after.</strong>
</details>

## Before moving on

- [ ] Solve a related-rates problem, differentiating before substituting.
- [ ] Find critical points and classify them with both tests.
- [ ] Solve an optimisation problem including the endpoint check.
- [ ] Explain what the second derivative adds to the first.

**Recap:** Related rates differentiate a relationship with respect to time, applying the chain rule to every variable — and the specific values must be substituted only after differentiating, or the relationship collapses to a statement about one instant. Extrema occur at critical points where $f'=0$ or is undefined, but not every critical point is an extremum; the first and second derivative tests classify them. Optimisation means expressing the target as a function of one variable, finding critical points, and comparing them against the endpoints, which the Extreme Value Theorem guarantees are candidates too.

**This is the end of Calculus 1.**

**Next:** [[01-integration-by-parts|Calculus 2]] — the other half of the subject, where you reverse differentiation to compute accumulated totals.

## Related

- [[01-rules|Derivative rules]] · [[01-definition|Continuity]]
- [[foundations/ai-ml/index|ai-ml]] — optimisation is what training a model *is*
