---
id: 4cc6e07c-9c78-4b7a-9626-1ae5a91aca41
---

# The Limit of a Function

A limit is the value a function gets closer and closer to as its input gets closer to some number. What matters is what happens near the number, not at it, and this one idea is what the rest of calculus is built on.

## Before you start
<!-- bite: a3893703-98e4-4fcc-a705-68985066d138 -->

- You know why calculus needs limits — [[01-preview|preview]].
- You can evaluate and simplify algebraic expressions — [[03-algebraic-manipulation|algebraic manipulation]].

**What you will be able to do after this lesson:**

1. State informally what $\lim_{x \to a} f(x) = L$ means.
2. Explain why the limit does not depend on $f(a)$, and give an example where they differ.
3. Evaluate limits by substitution, by factoring, and by rationalising.
4. Identify one-sided limits and say when a two-sided limit fails to exist.

---

## 1. The definition, informally
<!-- bite: 6f0d8bdc-65fd-4b13-a878-137c2759f043 -->

$$\lim_{x \to a} f(x) = L$$

means: **as $x$ gets arbitrarily close to $a$, $f(x)$ gets arbitrarily close to $L$.**

**Note what it does not say.** It says nothing about $f(a)$. The limit is about the *neighbourhood* of $a$, deliberately excluding $a$ itself.

That exclusion is not a technicality — **it is the entire point**. The tangent problem needs the value that $\frac{f(x)-f(a)}{x-a}$ approaches as $x \to a$, and that expression is undefined *at* $x = a$. If limits required the function to be defined at the point, calculus would not exist.

## 2. A function whose limit and value disagree
<!-- bite: 2fd83810-feed-4fe5-b733-ef6caa727e96 -->

$$f(x) = \frac{x^2 - 1}{x - 1}$$

At $x = 1$ this is $\frac{0}{0}$ — **undefined**. The function has a hole there.

But near $x = 1$, factor the numerator:

$$\frac{x^2-1}{x-1} = \frac{(x-1)(x+1)}{x-1} = x + 1 \qquad \text{for } x \neq 1$$

| $x$ | 0.9 | 0.99 | 0.999 | **1** | 1.001 | 1.01 | 1.1 |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| $f(x)$ | 1.9 | 1.99 | 1.999 | **undefined** | 2.001 | 2.01 | 2.1 |

**The limit is 2**, even though $f(1)$ does not exist. The function approaches 2 from both sides; whether it arrives is a separate question.

> [!NOTE]
> **The cancellation is legal precisely because of the exclusion.** Dividing by $x - 1$ requires $x \neq 1$ — and the limit never evaluates at $x = 1$, so the requirement is always satisfied.
>
> This is the standard technique: **an indeterminate $\frac{0}{0}$ usually means a common factor is hiding**. Cancel it and the limit becomes a substitution.

## 3. How to actually evaluate a limit
<!-- bite: bd7c4ef1-f97c-4831-831f-80ffe6b659d7 -->

**Try substitution first.** If $f(a)$ is defined and the function has no jump there, the limit is $f(a)$. Most limits are this easy.

$$\lim_{x\to 3}(x^2 + 2x) = 9 + 6 = 15$$

**If you get $\frac{0}{0}$, that is not the answer — it is a signal.** It means the expression is hiding a removable factor. Three standard moves:

**Factor and cancel:**
$$\lim_{x\to 2}\frac{x^2-4}{x-2} = \lim_{x\to 2}\frac{(x-2)(x+2)}{x-2} = \lim_{x\to 2}(x+2) = 4$$

**Rationalise**, when a square root is involved:
$$\lim_{x\to 0}\frac{\sqrt{x+4}-2}{x} = \lim_{x\to 0}\frac{(\sqrt{x+4}-2)(\sqrt{x+4}+2)}{x(\sqrt{x+4}+2)} = \lim_{x\to 0}\frac{x}{x(\sqrt{x+4}+2)} = \frac{1}{4}$$

**Simplify a compound fraction:**
$$\lim_{x\to 0}\frac{\frac{1}{x+1}-1}{x} = \lim_{x\to 0}\frac{\frac{-x}{x+1}}{x} = \lim_{x\to 0}\frac{-1}{x+1} = -1$$

## 4. One-sided limits, and when the limit fails
<!-- bite: 238b2653-d412-448b-a1c5-03e27a10f236 -->

Approaching from the left and from the right can give different answers:

$$\lim_{x\to a^-} f(x) \quad\text{(from below)} \qquad \lim_{x\to a^+} f(x) \quad\text{(from above)}$$

**The two-sided limit exists only if both one-sided limits exist and are equal.**

For $f(x) = \frac{|x|}{x}$: approaching 0 from the right gives $+1$; from the left, $-1$. They disagree, so $\lim_{x\to 0}\frac{|x|}{x}$ **does not exist** — even though both one-sided limits do.

**Three ways a limit fails to exist:**

1. **A jump** — the one-sided limits disagree, as above.
2. **Unbounded growth** — $\lim_{x\to 0}\frac{1}{x^2}$ grows without bound. Writing $= \infty$ describes *how* it fails; it is not a value.
3. **Oscillation** — $\lim_{x\to 0}\sin\frac{1}{x}$ oscillates infinitely fast and settles on nothing.

## 5. Practice — problems
<!-- bite: 9738f1f5-d091-4485-8734-5f9acf689e82 -->

1. Evaluate by substitution: (a) $\lim_{x\to 2}(3x^2-x+1)$  (b) $\lim_{x\to 0}\frac{x+3}{x-2}$.
2. Evaluate by factoring: (a) $\lim_{x\to 3}\frac{x^2-9}{x-3}$  (b) $\lim_{x\to -1}\frac{x^2+3x+2}{x+1}$.
3. Evaluate by rationalising: $\lim_{x\to 0}\frac{\sqrt{9+x}-3}{x}$.
4. For $f(x) = \begin{cases} x+1 & x < 2 \\ 5 & x = 2 \\ x^2-1 & x>2\end{cases}$, find $\lim_{x\to 2^-}f(x)$, $\lim_{x\to 2^+}f(x)$, $\lim_{x\to 2}f(x)$ and $f(2)$.
5. **Explain in one sentence** why $\lim_{x\to a}f(x)$ can exist when $f(a)$ does not, and why calculus needs that to be true.
6. Evaluate $\lim_{h\to 0}\frac{(3+h)^2 - 9}{h}$. **You have just computed a derivative** — of what function, at what point?

<details><summary>Answers — open only after an attempt</summary>

1. (a) $12 - 2 + 1 = 11$. (b) $\frac{3}{-2} = -\frac{3}{2}$.
2. (a) $\frac{(x-3)(x+3)}{x-3} \to x+3 \to 6$. (b) $\frac{(x+1)(x+2)}{x+1} \to x+2 \to 1$.
3. Multiply by $\frac{\sqrt{9+x}+3}{\sqrt{9+x}+3}$: numerator becomes $x$, giving $\frac{1}{\sqrt{9+x}+3} \to \frac{1}{6}$.
4. Left limit $= 3$; right limit $= 3$; so the two-sided limit **is 3**. But $f(2) = 5$. <strong>The limit and the value disagree</strong> — the function is defined at 2, just not at the value it approaches. This is a removable discontinuity.
5. The limit describes the behaviour of $f$ <em>near</em> $a$, deliberately excluding $a$ itself — and calculus needs that because the difference quotient $\frac{f(x)-f(a)}{x-a}$ is always undefined at $x = a$, so a definition requiring the value there would define nothing.
6. $\frac{9 + 6h + h^2 - 9}{h} = \frac{6h + h^2}{h} = 6 + h \to \mathbf{6}$. That is the derivative of $f(x) = x^2$ at $x = 3$ — and $2x$ at $x=3$ is indeed 6.
</details>

## Before moving on
<!-- bite: bf67a291-ef07-498e-9821-e32b887a8c22 -->

- [ ] State informally what a limit is.
- [ ] Explain why the limit ignores the value at the point, and why that matters.
- [ ] Evaluate a $\frac{0}{0}$ limit by factoring and by rationalising.
- [ ] Say when a two-sided limit fails to exist, and name three ways it can.

**Recap:** $\lim_{x\to a} f(x) = L$ means $f(x)$ gets arbitrarily close to $L$ as $x$ gets arbitrarily close to $a$ — with $x = a$ deliberately excluded. That exclusion is what lets calculus define a derivative, since the difference quotient is undefined at the point itself. Substitution works when the function is well behaved; $\frac{0}{0}$ signals a hidden common factor to cancel or rationalise. A two-sided limit exists only when both one-sided limits agree.

**Next:** [[01-laws|Limit Laws]] — the rules that let you evaluate limits without a table of values every time.

## Related
<!-- bite: 1b24c432-5be4-46ec-8c97-3b3444c41fe9 -->

- [[01-preview|Calculus preview]] · [[01-epsilon-delta|The precise definition]]

## About this lesson
<!-- bite: a7cabb61-438a-455a-95e8-0d58bef39235 -->

**Level:** Intermediate. **Covers:** What "approaches" means precisely enough to build on, and why the value *at* a point is irrelevant to the limit *near* it.
