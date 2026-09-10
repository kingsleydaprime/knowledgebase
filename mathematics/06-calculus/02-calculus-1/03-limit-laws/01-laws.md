# Limit Laws

**[Intermediate]** — The rules that make limits computable, why each is believable, and the one case they all refuse to cover.

## Before you start

- You can evaluate simple limits by substitution and factoring — [[01-definition|the limit of a function]].

**What you will be able to do after this lesson:**

1. State the limit laws for sums, products, quotients and powers.
2. Explain why every law carries the condition "provided both limits exist".
3. Recognise the indeterminate forms and say what they signal.
4. Use the Squeeze Theorem on a limit the ordinary laws cannot touch.

---

## 1. The laws

If $\lim_{x\to a} f(x) = L$ and $\lim_{x\to a} g(x) = M$ — **and both exist** — then:

| Law | Statement |
| :--- | :--- |
| Sum | $\lim (f + g) = L + M$ |
| Difference | $\lim (f - g) = L - M$ |
| Constant multiple | $\lim (cf) = cL$ |
| Product | $\lim (fg) = LM$ |
| Quotient | $\lim \dfrac{f}{g} = \dfrac{L}{M}$, **provided $M \neq 0$** |
| Power | $\lim [f(x)]^n = L^n$ |
| Root | $\lim \sqrt[n]{f(x)} = \sqrt[n]{L}$ |

**Read them as one sentence:** *limits pass straight through ordinary arithmetic.* If you can compute the pieces, you can combine them exactly as you would combine numbers.

**Why that is believable:** if $f(x)$ is settling towards $L$ and $g(x)$ towards $M$, then $f(x) + g(x)$ has nowhere to settle except $L + M$. The formal proof uses the $\varepsilon$–$\delta$ definition from [[01-epsilon-delta|the precise definition]]; the intuition is exactly this.

## 2. The condition that matters

**Every law says "provided both limits exist".** That is not decoration.

$$\lim_{x\to 0}\left(\frac{1}{x} - \frac{1}{x}\right)$$

The expression is identically $0$ for every $x \neq 0$, so the limit is $0$. But the *difference law* does not apply, because neither $\lim \frac{1}{x}$ exists. Applying it anyway gives $\infty - \infty$, which is meaningless.

**When a law's precondition fails, the law says nothing** — not that the limit fails to exist, but that this particular tool cannot decide. You need a different approach.

## 3. Polynomials and rational functions

The laws combine to give a very useful shortcut.

**For any polynomial $P$:** $\lim_{x\to a} P(x) = P(a)$. Substitution always works.

**For a rational function $\frac{P(x)}{Q(x)}$:** $\lim_{x\to a} \frac{P(x)}{Q(x)} = \frac{P(a)}{Q(a)}$, **provided $Q(a) \neq 0$**.

**That proviso is where all the interesting cases live.** If $Q(a) = 0$:

- and $P(a) \neq 0$ → the limit is unbounded (a vertical asymptote)
- and $P(a) = 0$ → **indeterminate $\frac{0}{0}$** → factor and cancel

## 4. The indeterminate forms

$$\frac{0}{0} \qquad \frac{\infty}{\infty} \qquad 0 \cdot \infty \qquad \infty - \infty \qquad 1^\infty \qquad 0^0 \qquad \infty^0$$

**"Indeterminate" does not mean "no answer". It means "not yet determined".**

Each of these can come out to anything depending on the specific functions:

$$\lim_{x\to 0}\frac{x}{x} = 1 \qquad \lim_{x\to 0}\frac{x^2}{x} = 0 \qquad \lim_{x\to 0}\frac{x}{x^2} = \text{unbounded}$$

**All three are $\frac{0}{0}$, and all three answers differ.** So the form alone tells you nothing except *do more work* — the two quantities are racing to zero and you have to find out which wins.

**Compare with $\frac{5}{0}$**, which is *not* indeterminate. It is definitely unbounded; there is nothing more to determine.

## 5. The Squeeze Theorem

Some limits resist every algebraic move. The classic:

$$\lim_{x\to 0} x^2 \sin\frac{1}{x}$$

$\sin\frac{1}{x}$ oscillates infinitely fast near 0 and has no limit, so the product law is unusable.

**The Squeeze Theorem:** if $g(x) \le f(x) \le h(x)$ near $a$, and $\lim g = \lim h = L$, then $\lim f = L$ too.

**Trap the function between two you can handle.** Since $-1 \le \sin\frac{1}{x} \le 1$ always:

$$-x^2 \le x^2\sin\frac{1}{x} \le x^2$$

Both outer functions go to 0, so the middle one is squeezed to **0**.

**You never needed to understand the oscillation** — only to bound it. That is the technique: when a factor is uncontrollable but *bounded*, multiply it by something going to zero and the whole thing is forced to zero.

## 6. Practice — problems

1. Evaluate using the laws, naming which you use: $\lim_{x\to 2}\frac{x^3 - 2x}{x + 4}$.
2. Evaluate: (a) $\lim_{x\to 1}\frac{x^2-1}{x^2-3x+2}$  (b) $\lim_{x\to 4}\frac{\sqrt{x}-2}{x-4}$.
3. Give three functions all of the form $\frac{0}{0}$ at $x = 0$ whose limits are $0$, $7$ and unbounded respectively.
4. Use the Squeeze Theorem on $\lim_{x\to 0} x\cos\frac{1}{x}$.
5. **Explain the error:** "$\lim_{x\to 0}\left(\frac{1}{x^2} - \frac{1}{x^2}\right) = \infty - \infty = 0$." The answer is 0 — so what exactly is wrong with the reasoning?
6. Evaluate $\lim_{x\to\infty}\frac{3x^2 + 5x}{2x^2 - 1}$ by dividing numerator and denominator by $x^2$. Why does that trick work?

<details><summary>Answers — open only after an attempt</summary>

1. Quotient law (denominator $\to 6 \neq 0$), then sum and power laws on top: $\frac{8-4}{6} = \frac{2}{3}$.
2. (a) $\frac{(x-1)(x+1)}{(x-1)(x-2)} \to \frac{x+1}{x-2} \to \frac{2}{-1} = -2$. (b) Rationalise: $\frac{1}{\sqrt{x}+2} \to \frac{1}{4}$.
3. $\frac{x^2}{x} \to 0$; $\frac{7x}{x} \to 7$; $\frac{x}{x^2} \to$ unbounded. All are $\frac{0}{0}$; <strong>the form does not determine the answer</strong>.
4. $-|x| \le x\cos\frac{1}{x} \le |x|$, and both bounds $\to 0$, so the limit is $\mathbf{0}$.
5. The <em>answer</em> is right and the <em>reasoning</em> is invalid. The difference law requires both limits to exist, and $\lim \frac{1}{x^2}$ does not — so the law cannot be applied, and "$\infty - \infty$" is not an arithmetic step. The correct argument is that the expression <em>simplifies to 0 for every $x \neq 0$</em> before any limit is taken. <strong>Getting the right answer by an invalid route is still wrong</strong>, and here it is luck: $\frac{1}{x} - \frac{1}{x^2}$ has the same form and is unbounded.
6. Dividing by $x^2$ gives $\frac{3 + 5/x}{2 - 1/x^2}$. As $x\to\infty$ the $\frac{1}{x}$ terms vanish, leaving $\frac{3}{2}$. It works because dividing top and bottom by the same non-zero quantity does not change the value, and it converts the unbounded terms into ones that visibly go to zero.
</details>

## Before moving on

- [ ] State the limit laws and the condition attached to every one of them.
- [ ] Explain why an indeterminate form is a signal rather than an answer.
- [ ] Show that $\frac{0}{0}$ can produce any value.
- [ ] Apply the Squeeze Theorem to a bounded-times-vanishing product.

**Recap:** Limits distribute over sums, differences, products, quotients, powers and roots — provided the component limits exist, and provided a denominator's limit is non-zero. For polynomials that makes substitution always valid. When substitution gives an indeterminate form, that is a signal that two quantities are competing and more work is needed, not that the limit fails. When algebra cannot reach a limit, the Squeeze Theorem can, by trapping an uncontrollable but bounded factor between two limits you can evaluate.

**Next:** [[01-definition|Continuity]] — the property that makes substitution work, stated precisely.

## Related

- [[01-definition|The limit of a function]] · [[01-epsilon-delta|The precise definition]]
