# Continuity

**[Intermediate]** — The property that makes substitution legal, stated precisely — and the theorems it unlocks, one of which you already use to debug code.

## Before you start

- You can evaluate limits and know when they fail — [[01-definition|the limit of a function]], [[01-laws|limit laws]].

**What you will be able to do after this lesson:**

1. State the three conditions for continuity at a point.
2. Classify a discontinuity as removable, jump or infinite.
3. State the Intermediate Value Theorem and use it to prove a root exists.
4. Explain why continuity is what justifies evaluating a limit by substitution.

---

## 1. The definition

**$f$ is continuous at $a$ when three things all hold:**

1. $f(a)$ **is defined** — the point exists
2. $\lim_{x\to a} f(x)$ **exists** — the function approaches something
3. $\lim_{x\to a} f(x) = f(a)$ — **and it approaches the value it actually has**

**All three are needed, and each can fail independently.** The third is the interesting one: a function can be defined at a point and approach a *different* value there, as the piecewise example in [[01-definition|the limits lesson]] showed.

**Informally:** you can draw the graph through $a$ without lifting your pen. That intuition is correct and is not a definition — the three conditions are.

> [!NOTE]
> **This is what makes substitution legal.** Every time you evaluate $\lim_{x\to 3}(x^2+1)$ by writing $10$, you are using continuity — condition 3 says the limit *equals* the value, so computing the value answers the limit.
>
> Polynomials are continuous everywhere, which is why substitution never fails for them. The moment a function is not continuous at the point, substitution is not a valid method and you need the techniques from the previous lessons.

## 2. Three ways to be discontinuous

**Removable** — the limit exists but disagrees with the value (or the value is missing). A single point is wrong; redefining it fixes everything.

$$f(x) = \frac{x^2-1}{x-1} \quad\text{at } x=1$$

The limit is 2; the function is undefined. Define $f(1) = 2$ and it becomes continuous — hence *removable*.

**Jump** — both one-sided limits exist but differ. No redefinition can fix it; the function genuinely leaps.

$$f(x) = \frac{|x|}{x} \quad\text{at } x=0$$

**Infinite** — the function grows without bound.

$$f(x) = \frac{1}{x} \quad\text{at } x=0$$

```
   removable            jump              infinite
      ,-o-,           ---,               |
    ,'     ',            |    ,---       |
   '         '           '----'          |____
        ^                    ^                ^
   one point wrong      a genuine step    unbounded
```

## 3. Which functions are continuous

**Continuous everywhere they are defined:**

- polynomials (everywhere, no exceptions)
- $\sin x$, $\cos x$, $e^x$ (everywhere)
- rational functions, except where the denominator is zero
- $\sqrt{x}$ for $x \ge 0$, $\ln x$ for $x > 0$

**And continuity survives combination:** sums, differences, products, quotients (where the denominator is non-zero) and compositions of continuous functions are continuous.

**Practical consequence:** almost every function you write down is continuous almost everywhere, and the exceptions are exactly where you divided by something that can be zero, or took a root or log of something that can be non-positive. **Those are also the places your code throws exceptions**, which is not a coincidence.

## 4. The Intermediate Value Theorem

**If $f$ is continuous on $[a,b]$, then it takes every value between $f(a)$ and $f(b)$ somewhere in that interval.**

Obvious once stated: to get from one height to another without lifting the pen, you must pass through every height between.

**But it is not obvious that it needs continuity** — and it does. $\frac{1}{x}$ goes from $-1$ at $x=-1$ to $+1$ at $x=1$ without ever being 0, because it is not continuous on that interval.

### Using it to prove a root exists

Does $x^3 - x - 1 = 0$ have a solution between 1 and 2?

$$f(1) = 1 - 1 - 1 = -1 \qquad f(2) = 8 - 2 - 1 = 5$$

$f$ is a polynomial, so continuous. It goes from $-1$ to $5$, so it must pass through $0$ somewhere in between. **A root exists in $(1,2)$** — proved without finding it.

> [!NOTE]
> **This is bisection, and you have used it.** Halve the interval, check which side changes sign, repeat. It is exactly [[dsa/06-patterns/09-modified-binary-search|binary search]] over a continuous domain, and it is how numerical root-finders work — see [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]].
>
> It is also `git bisect`: the "function" is *does the build pass*, the interval is your commit history, and you are finding where it changed sign.

## 5. The Extreme Value Theorem

**A continuous function on a closed interval $[a,b]$ attains a maximum and a minimum on it.**

**Both conditions are necessary.** On the *open* interval $(0,1)$, $f(x) = x$ gets arbitrarily close to 1 but never reaches it — no maximum. And a discontinuous function can jump over its own supremum.

**This is what guarantees optimisation problems have answers**, and it is why [[01-related-rates|the applications lesson]] can talk about finding a maximum at all.

## 6. Practice — problems

1. For $f(x) = \begin{cases}x^2 & x<1\\ 3 & x=1\\ 2x & x>1\end{cases}$, check all three conditions at $x=1$. Is it continuous? What kind of discontinuity, and can it be removed?
2. Where is $f(x) = \frac{x+1}{x^2-4}$ discontinuous? Classify each.
3. Find $k$ making $f(x) = \begin{cases}x^2+k & x\le 2\\ 3x & x>2\end{cases}$ continuous at $x=2$.
4. Use the IVT to show $\cos x = x$ has a solution in $[0,1]$. (Use $\cos 0 = 1$, $\cos 1 \approx 0.54$.)
5. **Explain** why the IVT needs a *closed* interval and continuity, giving a counterexample for dropping each.
6. **Connect it to code.** You are bisecting 1024 commits to find one that broke a test. How many builds must you run? Which theorem are you relying on, and what assumption about the bug does it encode?

<details><summary>Answers — open only after an attempt</summary>

1. $f(1) = 3$ is defined ✓. Left limit $= 1$, right limit $= 2$ — <strong>they disagree, so the limit does not exist</strong> ✗. It is a <strong>jump</strong> discontinuity and cannot be removed: no choice of $f(1)$ fixes a genuine step.
2. Discontinuous at $x = 2$ and $x = -2$, where the denominator vanishes. Both are <strong>infinite</strong> discontinuities, since the numerator is non-zero there.
3. Continuity needs $\lim_{x\to2^-} = \lim_{x\to2^+}$: $4 + k = 6$, so $k = 2$.
4. Let $g(x) = \cos x - x$. Then $g(0) = 1 > 0$ and $g(1) \approx -0.46 < 0$. $g$ is continuous, so it crosses zero in $(0,1)$ — that crossing is the solution.
5. <strong>Open interval:</strong> $f(x)=x$ on $(0,1)$ never attains 1 (this breaks the Extreme Value Theorem). <strong>Discontinuity:</strong> $\frac{1}{x}$ on $[-1,1]$ runs from $-1$ to $1$ without ever equalling 0, so it skips an intermediate value.
6. $\log_2 1024 = \mathbf{10}$ builds. You are relying on the <strong>Intermediate Value Theorem</strong> — and the assumption it encodes is that the test result changed <em>exactly once</em>, monotonically. If the bug was introduced and fixed and reintroduced, the "function" is not monotone and bisection can land on the wrong commit. That is why `git bisect` misleads on flaky tests.
</details>

## Before moving on

- [ ] State the three conditions for continuity and give a function failing each.
- [ ] Classify removable, jump and infinite discontinuities.
- [ ] Explain why continuity is what makes substitution valid.
- [ ] Use the IVT to prove a root exists without finding it.

**Recap:** $f$ is continuous at $a$ when $f(a)$ exists, the limit exists, and the two are equal — and that third condition is what makes evaluating a limit by substitution legitimate. Discontinuities are removable (one point wrong), jump (one-sided limits disagree) or infinite. Continuity guarantees the Intermediate Value Theorem, which proves roots exist without locating them and underpins bisection, and the Extreme Value Theorem, which guarantees optimisation problems on closed intervals have answers.

**Next:** [[01-epsilon-delta|The Precise Definition of a Limit]] — making "arbitrarily close" mean something exact.

## Related

- [[01-laws|Limit laws]] · [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]]
