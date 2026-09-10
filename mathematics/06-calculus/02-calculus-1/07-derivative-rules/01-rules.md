# Derivative Rules

**[Intermediate]** — The shortcuts, each derived rather than asserted — and the chain rule, which is the one that actually matters.

## Before you start

- You can differentiate from first principles — [[01-definition|defining the derivative]].
- You know the index laws — [[01-indices-and-logarithms|indices and logarithms]].

**What you will be able to do after this lesson:**

1. Apply the power, sum, product, quotient and chain rules correctly.
2. Derive the power and product rules from the definition.
3. Recognise which rule a composite expression needs, and in what order.
4. Explain why the chain rule is the foundation of backpropagation.

---

## 1. The rules

| Rule | Statement |
| :--- | :--- |
| **Constant** | $\dfrac{d}{dx}c = 0$ |
| **Power** | $\dfrac{d}{dx}x^n = nx^{n-1}$ |
| **Constant multiple** | $\dfrac{d}{dx}[cf] = cf'$ |
| **Sum** | $\dfrac{d}{dx}[f+g] = f' + g'$ |
| **Product** | $\dfrac{d}{dx}[fg] = f'g + fg'$ |
| **Quotient** | $\dfrac{d}{dx}\dfrac{f}{g} = \dfrac{f'g - fg'}{g^2}$ |
| **Chain** | $\dfrac{d}{dx}f(g(x)) = f'(g(x))\cdot g'(x)$ |

**And the standard functions:**

$$\frac{d}{dx}\sin x = \cos x \qquad \frac{d}{dx}\cos x = -\sin x \qquad \frac{d}{dx}e^x = e^x \qquad \frac{d}{dx}\ln x = \frac{1}{x}$$

**$e^x$ is its own derivative**, and that is the *definition* of $e$ — the unique base whose exponential grows at exactly its own value. It is why $e$ appears everywhere growth is proportional to size.

## 2. Two derivations

**The rules are not arbitrary.** Deriving two of them shows where they come from and makes the rest believable.

### The power rule for $n = 3$

$$\frac{d}{dx}x^3 = \lim_{h\to0}\frac{(x+h)^3 - x^3}{h} = \lim_{h\to0}\frac{3x^2h + 3xh^2 + h^3}{h}$$
$$= \lim_{h\to0}(3x^2 + 3xh + h^2) = 3x^2$$

**The general case is the same argument with the binomial theorem.** Expanding $(x+h)^n$ gives $x^n + nx^{n-1}h + (\text{terms with } h^2 \text{ or higher})$. The $x^n$ cancels, dividing by $h$ leaves $nx^{n-1} + O(h)$, and the rest vanishes.

### The product rule

**Why it is not $f'g'$:** consider area. If a rectangle has width $f$ and height $g$, growing both slightly increases the area by *two strips* — one from the width change, one from the height — plus a tiny corner.

```
        g'  ┌───┬─┐   <- corner: f' x g', negligible
            │   │ │
         g  │ fg│ │   <- strip: f x g'
            ├───┼─┤
            └───┴─┘
              f   f'     <- strip: f' x g
```

$$\Delta(fg) \approx f'g\,\Delta x + fg'\,\Delta x + \underbrace{f'g'(\Delta x)^2}_{\text{vanishes}}$$

Divide by $\Delta x$ and take the limit: the corner term still has a $\Delta x$ in it and disappears, leaving $f'g + fg'$. **The two strips are the two terms.**

## 3. The chain rule — the important one

$$\frac{d}{dx}f(g(x)) = f'(g(x))\cdot g'(x)$$

**In Leibniz notation it looks like fractions cancelling**, which is the best way to remember it:

$$\frac{dy}{dx} = \frac{dy}{du}\cdot\frac{du}{dx}$$

**Read it as rates multiplying.** If $y$ changes 3× as fast as $u$, and $u$ changes 5× as fast as $x$, then $y$ changes 15× as fast as $x$.

**Worked:** differentiate $(3x^2 + 1)^5$.

Outer function: $u^5$, whose derivative is $5u^4$. Inner: $3x^2+1$, whose derivative is $6x$.

$$\frac{d}{dx}(3x^2+1)^5 = 5(3x^2+1)^4 \cdot 6x = 30x(3x^2+1)^4$$

**The commonest mistake is forgetting the inner derivative** — writing $5(3x^2+1)^4$ and stopping. **The chain rule is exactly that missing factor.**

> [!NOTE]
> **This rule is why neural networks can be trained.**
>
> A network is a deep composition: $f_n(f_{n-1}(\cdots f_1(x)))$. To adjust a weight in an early layer you need the derivative of the final loss with respect to that weight — and the chain rule says that is the product of the local derivatives along the path.
>
> **Backpropagation is the chain rule applied systematically**, computing those products from the output backwards and reusing shared sub-products. It is not a separate algorithm — it is bookkeeping over this one rule. See [[ai-ml/index|ai-ml]] and [[build-your-own-shit/10-your-own-neural-network|build your own neural network]].

## 4. Choosing the rule

**Work from the outside in.** Ask what operation is applied *last*:

| Expression | Outermost operation | Rule |
| :--- | :--- | :--- |
| $x^3 + \sin x$ | addition | sum |
| $x^3\sin x$ | multiplication | product |
| $\dfrac{x^3}{\sin x}$ | division | quotient |
| $\sin(x^3)$ | composition | chain |
| $\sin^3 x$ | composition (cube of sine) | chain |

**$\sin(x^3)$ and $\sin^3 x$ are different functions** and need the chain rule applied in opposite orders. Confusing them is one of the most common errors in the topic.

## 5. Practice — problems

1. Differentiate: (a) $5x^4 - 3x^2 + 7$  (b) $\sqrt{x}$  (c) $\dfrac{1}{x^3}$. *(Write (b) and (c) as powers first.)*
2. Product rule: (a) $x^2\sin x$  (b) $xe^x$.
3. Quotient rule: (a) $\dfrac{x}{x+1}$  (b) $\dfrac{\sin x}{x}$.
4. Chain rule: (a) $(2x+1)^7$  (b) $\sin(x^2)$  (c) $e^{3x}$  (d) $\ln(x^2+1)$.
5. **Combined:** differentiate $x^2 e^{3x}$ and $\sqrt{\sin x}$, naming each rule as you use it.
6. **Derive the quotient rule from the product rule.** *Hint: write $\frac{f}{g}$ as $f \cdot g^{-1}$ and use the chain rule on $g^{-1}$.*

<details><summary>Answers — open only after an attempt</summary>

1. (a) $20x^3 - 6x$. (b) $x^{1/2} \Rightarrow \frac{1}{2}x^{-1/2} = \frac{1}{2\sqrt x}$. (c) $x^{-3} \Rightarrow -3x^{-4} = -\frac{3}{x^4}$.
2. (a) $2x\sin x + x^2\cos x$. (b) $e^x + xe^x = e^x(1+x)$.
3. (a) $\frac{1\cdot(x+1) - x\cdot1}{(x+1)^2} = \frac{1}{(x+1)^2}$. (b) $\frac{x\cos x - \sin x}{x^2}$.
4. (a) $14(2x+1)^6$. (b) $2x\cos(x^2)$. (c) $3e^{3x}$. (d) $\frac{2x}{x^2+1}$.
5. $x^2e^{3x}$: product rule, with the chain rule on $e^{3x}$ → $2xe^{3x} + 3x^2e^{3x} = xe^{3x}(2+3x)$.<br>
$\sqrt{\sin x} = (\sin x)^{1/2}$: chain rule → $\frac{1}{2}(\sin x)^{-1/2}\cos x = \frac{\cos x}{2\sqrt{\sin x}}$.
6. $\frac{d}{dx}(f g^{-1}) = f'g^{-1} + f\cdot(-g^{-2}g') = \frac{f'}{g} - \frac{fg'}{g^2} = \frac{f'g - fg'}{g^2}$. ∎ <strong>The quotient rule is not a separate rule</strong> — it is the product and chain rules combined, which is worth knowing if you ever forget it.
</details>

## Before moving on

- [ ] State all seven rules from memory.
- [ ] Derive the power rule for a specific $n$ and explain the product rule geometrically.
- [ ] Identify the outermost operation and choose the right rule.
- [ ] Apply the chain rule without dropping the inner derivative.

**Recap:** The derivative rules are shortcuts for limits you could always compute directly, and each is provable from the definition — the power rule from the binomial expansion, the product rule from the two strips of a growing rectangle, the quotient rule from the product and chain rules together. Choosing a rule means identifying the operation applied last. The chain rule multiplies rates along a composition, and applying it systematically across a deep composition is exactly what backpropagation does.

**Next:** [[01-related-rates|Applications]] — using derivatives to solve problems rather than to differentiate expressions.

## Related

- [[01-definition|Defining the derivative]]
- [[build-your-own-shit/10-your-own-neural-network|Build your own neural network]] — the chain rule, applied
