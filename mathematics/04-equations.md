# 4. EQUATIONS

## Before you start

- You can substitute into expressions — [[03-variables|variables]].

**What you will be able to do after this lesson:**

1. Solve linear equations by doing the same thing to both sides.
2. Solve simultaneous linear equations by substitution and by elimination.
3. Change the subject of a formula.
4. Check a solution and explain why checking is not optional.

**Study route:** read the lesson, then attempt every problem before opening the answers.

---

An equation says that two expressions have the same value.

For example:

$$
x+5=12
$$

The question is:

> What must \(x\) be?

We want to isolate \(x\).

Subtract 5 from both sides:

$$
x+5-5=12-5
$$

Therefore:

$$
\boxed{x=7}
$$

This might look ridiculously basic right now.

But equations become incredibly powerful when we use them to describe **physical systems**.

For example, Ohm's law:

$$
V=IR
$$

is an equation.

It tells us a relationship between:

- voltage \(V\)
- current \(I\)
- resistance \(R\)

If:

$$
R=10\Omega
$$

and:

$$
I=2A
$$

then:

$$
V=(2)(10)
$$

$$
\boxed{V=20V}
$$

So mathematics isn't merely something sitting beside engineering.

**Mathematics is how we describe what the engineering system is doing.**

---

## Practice — problems

Attempt all of these before opening the answers.

1. Solve: (a) $3x + 7 = 22$  (b) $5(x-2) = 3x + 4$  (c) $\frac{x}{3} + \frac{x}{4} = 7$.
2. Solve simultaneously, once by substitution and once by elimination: $2x + 3y = 12$ and $x - y = 1$.
3. Make $r$ the subject of $A = \pi r^2$. What must you state about $r$ for the answer to be valid?
4. Make $C$ the subject of $F = \frac{9}{5}C + 32$, then find the temperature at which the two scales read the same.
5. **A trap.** Solve $\frac{x^2 - 4}{x - 2} = 5$. Then check your answer by substitution. What went wrong, and at what step?

<details><summary>Answers — open only after an attempt</summary>

1. (a) $x = 5$. (b) $5x - 10 = 3x + 4 \Rightarrow 2x = 14 \Rightarrow x = 7$. (c) Multiply through by 12: $4x + 3x = 84 \Rightarrow x = 12$.
2. From the second, $x = y + 1$. Substituting: $2(y+1) + 3y = 12 \Rightarrow 5y = 10 \Rightarrow y = 2$, so $x = 3$. By elimination, multiply the second by 3 and add. <strong>Both give $(3, 2)$</strong> — and checking in <em>both</em> original equations is the point.
3. $r = \sqrt{A/\pi}$, and you must state $r \geq 0$ — squaring loses the sign, so the algebra alone admits a negative root that the geometry forbids.
4. $C = \frac{5}{9}(F - 32)$. Setting $F = C$ gives $C = \frac{5}{9}(C-32) \Rightarrow 9C = 5C - 160 \Rightarrow C = -40$. The scales agree at $-40^\circ$.
5. Cancelling gives $x + 2 = 5$, so $x = 3$ — which checks out. But the cancellation <strong>divided by $x - 2$</strong>, which silently assumed $x \neq 2$. Here that is harmless, but the habit is dangerous: dividing by an expression that could be zero is how you lose solutions or invent them. <strong>Always state what you assumed non-zero.</strong>
</details>

## Before moving on

You are done with this lesson when you can, closed-book:

- [ ] Solve a linear equation and justify each step as an operation on both sides.
- [ ] Solve simultaneous equations both ways and check in both originals.
- [ ] Change the subject, stating any domain restriction.
- [ ] Explain why dividing by an expression containing the unknown is risky.

**Recap:** Solving an equation means isolating the unknown by applying the same operation to both sides, which preserves equality. Simultaneous equations are solved by substitution or elimination and should be checked in every original equation, not just one. Changing the subject is the same technique aimed at a different symbol, and often introduces a domain restriction — taking a square root loses a sign, and dividing by an expression assumes it is non-zero.

**Next:** [[05-algebraic-manipulation|Algebraic Manipulation]] — the toolkit that makes those steps possible.
