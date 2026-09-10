# 5. ALGEBRAIC MANIPULATION

## Before you start

- You can solve linear equations — [[01-linear-equations|equations]].

**What you will be able to do after this lesson:**

1. Expand brackets and collect like terms reliably.
2. Factorise common forms, including the difference of two squares.
3. Simplify algebraic fractions and say what you assumed non-zero.
4. Recognise when an expression can be simplified before it is evaluated.

**Study route:** read the lesson, then attempt every problem before opening the answers.

---

This is where we start learning to **transform mathematical expressions without changing their meaning**.

Suppose:

$$
2x+4=10
$$

Subtract 4:

$$
2x=6
$$

Divide by 2:

$$
x=3
$$

Simple.

But eventually you'll encounter things like:

$$
V=IR
$$

and need to solve for \(I\).

Divide both sides by \(R\):

$$
\boxed{I=\frac VR}
$$

Or solve for \(R\):

$$
\boxed{R=\frac VI}
$$

Same equation.

Different arrangement.

This ability is called **algebraic manipulation**.

And you're going to use it constantly in engineering.

---

## Practice — problems

Attempt all of these before opening the answers.

1. Expand and simplify: (a) $(x+3)(x-5)$  (b) $(2a-b)^2$  (c) $(x+y)(x-y)$.
2. Factorise: (a) $x^2 - 9$  (b) $x^2 + 7x + 12$  (c) $6ab + 9a^2$  (d) $x^2 - 6x + 9$.
3. Simplify $\frac{x^2 - 16}{x^2 + 8x + 16}$, stating any restriction.
4. **Why factorising matters computationally.** Evaluate $x^2 - y^2$ and $(x+y)(x-y)$ for $x = 1000001$, $y = 1000000$. Which form would you rather compute by hand, and why?
5. Simplify $\frac{1}{x} - \frac{1}{x+1}$ into a single fraction.

<details><summary>Answers — open only after an attempt</summary>

1. (a) $x^2 - 2x - 15$. (b) $4a^2 - 4ab + b^2$. (c) $x^2 - y^2$ — <strong>the difference of two squares</strong>, worth recognising instantly.
2. (a) $(x-3)(x+3)$. (b) $(x+3)(x+4)$. (c) $3a(2b + 3a)$. (d) $(x-3)^2$.
3. $\frac{(x-4)(x+4)}{(x+4)^2} = \frac{x-4}{x+4}$, valid for $x \neq -4$ — the original was undefined there and the simplified form is not, so the restriction must be carried.
4. $x^2 - y^2$ needs two large multiplications and a subtraction of near-equal numbers. $(x+y)(x-y) = 2000001 \times 1 = 2000001$ is <strong>immediate</strong>. Subtracting near-equal large numbers also causes <em>catastrophic cancellation</em> in floating point, so the factored form is more accurate as well as faster.
5. $\frac{(x+1) - x}{x(x+1)} = \frac{1}{x(x+1)}$, for $x \neq 0, -1$.
</details>

## Before moving on

You are done with this lesson when you can, closed-book:

- [ ] Expand brackets and collect like terms without error.
- [ ] Recognise and factorise the difference of two squares on sight.
- [ ] Simplify an algebraic fraction and state its restriction.
- [ ] Explain why an algebraically identical form can be computationally better.

**Recap:** Algebraic manipulation rewrites an expression into an equivalent form that is easier to work with. Expanding removes brackets; factorising reintroduces them, and recognising standard patterns — the difference of two squares, perfect squares, common factors — is most of the skill. Simplifying a fraction can change its domain, so restrictions must be carried. Two algebraically identical expressions can differ enormously in how easy and how accurate they are to compute.

**Next:** [[01-indices-and-logarithms|Exponents]] — the notation that makes repeated multiplication manageable.
