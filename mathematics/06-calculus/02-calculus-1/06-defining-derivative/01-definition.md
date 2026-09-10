# Defining the Derivative

**[Intermediate]** — The tangent problem, solved. One limit, and everything in differential calculus follows from it.

## Before you start

- You can evaluate limits, especially $\frac{0}{0}$ forms — [[01-definition|the limit of a function]], [[01-laws|limit laws]].
- You know what a gradient is for a straight line.

**What you will be able to do after this lesson:**

1. State the definition of the derivative as a limit and explain each part.
2. Compute a derivative from first principles.
3. Give the three main interpretations of a derivative and say when each is used.
4. Explain what it means for a function to be non-differentiable at a point.

---

## 1. The problem, restated

From [[01-preview|the preview]]: the gradient at a single point is $\frac{0}{0}$, because steepness needs two points and you have one.

**The fix is to use two points and then take a limit.** Pick $x$ and a nearby $x + h$:

$$\text{gradient of the secant} = \frac{f(x+h) - f(x)}{h}$$

That is the average rate of change over an interval of width $h$ — a perfectly ordinary calculation, valid for any $h \neq 0$.

**Then shrink $h$ towards zero.**

```
   f(x+h) |          ,-'|
          |        ,'   |
          |      ,'     | rise = f(x+h) - f(x)
     f(x) |----'--------|
          |    |   run = h
          +----+--------+----
               x      x+h

   as h -> 0, the secant pivots into the tangent
```

## 2. The definition

$$f'(x) = \lim_{h\to 0}\frac{f(x+h) - f(x)}{h}$$

**When this limit exists, $f$ is differentiable at $x$ and the limit is the derivative.**

**Every part earns its place:**

- $f(x+h) - f(x)$ — the change in output
- $h$ — the change in input
- the quotient — average rate of change over that interval
- $\lim_{h\to 0}$ — **what that average approaches** as the interval vanishes

**Note that $h$ never equals zero.** The expression is undefined at $h = 0$, and the limit does not evaluate there — which is exactly the exclusion built into the definition of a limit. **That exclusion is what makes the derivative possible**, and it is why [[01-definition|limits]] had to come first.

## 3. From first principles

**Compute $f'(x)$ for $f(x) = x^2$.**

$$f'(x) = \lim_{h\to 0}\frac{(x+h)^2 - x^2}{h}$$

Expand:
$$= \lim_{h\to 0}\frac{x^2 + 2xh + h^2 - x^2}{h} = \lim_{h\to 0}\frac{2xh + h^2}{h}$$

Factor and cancel — legal because $h \neq 0$:
$$= \lim_{h\to 0}\frac{h(2x + h)}{h} = \lim_{h\to 0}(2x+h) = 2x$$

**So $\frac{d}{dx}x^2 = 2x$.** Every rule in [[01-rules|the next lesson]] is proved this way; they are shortcuts for a limit you could always compute directly.

**The pattern is always the same:** expand, find the common factor of $h$, cancel it, then substitute $h = 0$ into what remains. **If the $h$ does not cancel, the function is not differentiable there.**

## 4. Three readings of the same number

$f'(a)$ means three things at once, and the useful skill is switching between them.

**Geometric — the gradient of the tangent at $x = a$.** Steepness of the curve at that point.

**Physical — the instantaneous rate of change.** If $s(t)$ is position, $s'(t)$ is velocity. If $v(t)$ is velocity, $v'(t)$ is acceleration. **"Instantaneous" is meaningful only because of the limit** — a speedometer reading is not an average over any interval.

**Analytic — the best linear approximation.** Near $a$:

$$f(x) \approx f(a) + f'(a)(x-a)$$

**This third reading is the one that matters computationally.** It says the derivative tells you how the output responds to a small nudge in the input — which is exactly what gradient descent uses to decide which way to step, and why backpropagation is the chain rule ([[ai-ml/index|ai-ml]]).

## 5. When the derivative does not exist

**Differentiability is stronger than continuity.** A differentiable function is automatically continuous; the converse fails.

**A corner.** $f(x) = |x|$ at $x=0$: from the right the difference quotient is $+1$, from the left $-1$. The one-sided limits disagree, so the limit does not exist. **The function is continuous but has no single tangent** — you cannot say which way it points.

**A vertical tangent.** $f(x) = \sqrt[3]{x}$ at $x = 0$: the quotient grows without bound. The tangent exists geometrically but is vertical, so its gradient is not a number.

**A discontinuity.** Any break makes differentiation impossible — the difference quotient does not settle.

> [!NOTE]
> **Continuous everywhere, differentiable nowhere.** Weierstrass constructed such a function in 1872, and it caused genuine alarm — mathematicians had assumed continuity implied differentiability except at isolated points.
>
> These functions are not curiosities: **Brownian motion and fractal coastlines behave this way**, continuous but so jagged that no zoom level reveals a straight line. It is why "smooth" is an assumption to state rather than expect.

## 6. Practice — problems

1. From first principles, find $f'(x)$ for: (a) $f(x) = 3x + 2$  (b) $f(x) = x^2 - 4x$  (c) $f(x) = \frac{1}{x}$.
2. Use the definition to find $f'(2)$ for $f(x) = x^3$. Then guess the general rule for $x^n$ and check it against your answer for $x^2$.
3. A ball's height is $s(t) = 20t - 5t^2$ metres. Find $s'(t)$ from first principles, then the velocity at $t=1$ and $t=3$. **What does the sign tell you?**
4. Explain why $f(x) = |x - 3|$ is not differentiable at $x = 3$, using one-sided difference quotients.
5. **Show that differentiability implies continuity.** *Hint: if $f'(a)$ exists, consider $\lim_{h\to0}[f(a+h) - f(a)]$ written as $\frac{f(a+h)-f(a)}{h}\cdot h$.*
6. Use the linear approximation $f(x) \approx f(a) + f'(a)(x-a)$ to estimate $\sqrt{4.1}$, taking $f(x)=\sqrt{x}$ and $a=4$. Compare with a calculator.

<details><summary>Answers — open only after an attempt</summary>

1. (a) $\frac{3(x+h)+2-3x-2}{h} = 3$, so $f' = 3$ — a straight line has constant gradient. (b) $\frac{(x+h)^2-4(x+h)-x^2+4x}{h} = 2x + h - 4 \to 2x-4$. (c) $\frac{\frac{1}{x+h}-\frac{1}{x}}{h} = \frac{-1}{x(x+h)} \to -\frac{1}{x^2}$.
2. $\frac{(2+h)^3-8}{h} = \frac{12h+6h^2+h^3}{h} = 12+6h+h^2 \to 12$. Guess: $\frac{d}{dx}x^n = nx^{n-1}$ — at $n=3, x=2$ that is $3\cdot4 = 12$ ✓, and at $n=2$ it gives $2x$ ✓.
3. $\frac{20(t+h)-5(t+h)^2-20t+5t^2}{h} = 20 - 10t - 5h \to 20-10t$. At $t=1$: $+10$ m/s (rising). At $t=3$: $-10$ m/s — <strong>the negative sign means falling</strong>. The ball turns around at $t=2$, where the velocity is zero.
4. From the right, $\frac{|3+h-3|}{h} = \frac{h}{h} = 1$. From the left ($h<0$), $\frac{-h}{h} = -1$. The one-sided limits are $1$ and $-1$, so the limit does not exist — a corner has no single tangent direction.
5. $\lim_{h\to0}[f(a+h)-f(a)] = \lim_{h\to0}\left(\frac{f(a+h)-f(a)}{h}\cdot h\right) = f'(a)\cdot 0 = 0$. So $\lim_{h\to0}f(a+h) = f(a)$, which is exactly continuity at $a$. ∎
6. $f'(x) = \frac{1}{2\sqrt x}$, so $f'(4) = 0.25$. Then $\sqrt{4.1} \approx 2 + 0.25(0.1) = 2.025$. The true value is $2.0248...$ — <strong>accurate to four figures from one multiplication</strong>, which is the whole appeal of linear approximation.
</details>

## Before moving on

- [ ] State the derivative as a limit and explain why $h$ is never zero.
- [ ] Differentiate from first principles, cancelling the $h$.
- [ ] Give the geometric, physical and analytic readings of $f'(a)$.
- [ ] Explain why $|x|$ is continuous but not differentiable at 0.

**Recap:** The derivative is the limit of the difference quotient as the interval shrinks to zero — the average rate of change refined into an instantaneous one. It is simultaneously the gradient of the tangent, the instantaneous rate of change, and the coefficient of the best linear approximation, and switching between those readings is most of the skill. Differentiability implies continuity but not conversely: corners, vertical tangents and breaks all defeat it.

**Next:** [[01-rules|Derivative Rules]] — the shortcuts, each proved from this definition.

## Related

- [[01-preview|Calculus preview]] · [[01-definition|Continuity]]
- [[ai-ml/index|ai-ml]] — where the linear-approximation reading does the work
