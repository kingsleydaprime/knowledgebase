# Decimal (Base 10)

**[Beginner]** — The base you already use, examined properly: why ten, why it is not mathematically special, and which fractions it can and cannot write down.

## Before you start

- You can convert between bases — [[01-introduction|number bases]].

**What you will be able to do after this lesson:**

1. Explain why humans use base ten, and why that reason is not a mathematical one.
2. Explain which fractions terminate in a given base, using prime factors.
3. Explain why $0.999\ldots = 1$ exactly.

---

## 1. Why ten

**Because we have ten fingers.** That is the whole reason, and it is worth saying plainly, because it makes the arbitrariness obvious.

Other bases have been used for exactly the same kind of reason:

- **Base 60** (Babylonian) — survives in 60 seconds, 60 minutes, 360 degrees. It has many divisors (2, 3, 4, 5, 6, 10, 12, 15, 20, 30), which makes fractions convenient.
- **Base 20** (Mayan, and traces in French *quatre-vingts*) — fingers and toes.
- **Base 12** — twelve has more divisors than ten, which is why dozens, inches and clock faces persist.

**Base ten is not better. It is habitual.** Twelve would arguably be more useful for hand arithmetic, since it divides evenly by 3 and 4.

## 2. Which fractions terminate

This is the useful mathematical content of the lesson.

**A fraction terminates in base $b$ exactly when its denominator, in lowest terms, has no prime factors other than those of $b$.**

Base ten factors as $2 \times 5$, so:

| Fraction | Denominator factors | Terminates in base 10? |
| :--- | :--- | :--- |
| $\frac{1}{2}$ | 2 | yes — 0.5 |
| $\frac{1}{4}$ | 2×2 | yes — 0.25 |
| $\frac{1}{5}$ | 5 | yes — 0.2 |
| $\frac{1}{8}$ | 2³ | yes — 0.125 |
| $\frac{1}{3}$ | **3** | **no** — 0.333… |
| $\frac{1}{7}$ | **7** | **no** — 0.142857… |

**And the same rule explains floating point.** Base two factors as just $2$, so only denominators that are powers of two terminate. $\frac{1}{10}$ has a factor of 5, so **0.1 cannot be written exactly in binary** — which is why `0.1 + 0.2 != 0.3` in nearly every language.

**That is not imprecision.** Binary floating point is exact; 0.1 simply is not a binary-representable number, in the same way $\frac{1}{3}$ is not a finite decimal.

## 3. Why 0.999… = 1

Not "nearly 1". **Exactly 1.** Three arguments, and the third is the real one:

$$\frac{1}{3} = 0.333\ldots \quad\Rightarrow\quad 3 \times \frac{1}{3} = 0.999\ldots = 1$$

$$x = 0.999\ldots,\quad 10x = 9.999\ldots,\quad 10x - x = 9,\quad x = 1$$

**The rigorous version:** $0.999\ldots$ is defined as the limit of the sequence $0.9, 0.99, 0.999, \ldots$, and that limit is exactly 1. The two numerals denote the same real number.

**This is a fact about notation, not about numbers.** Decimal expansion is not a unique naming scheme — some numbers have two names. Nothing is wrong.

## 4. Practice — independent task

- **(a)** Without dividing, predict which of $\frac{1}{6}$, $\frac{3}{16}$, $\frac{7}{20}$, $\frac{5}{12}$ terminate in decimal. Then check.
- **(b)** Which of them terminate in **binary**? State the rule you used.
- **(c)** In base 12, which of $\frac{1}{2}$, $\frac{1}{3}$, $\frac{1}{4}$, $\frac{1}{5}$ terminate? What does that suggest about base 12 for everyday arithmetic?
- **(d)** Write a function `terminates(numerator, denominator, base)` that answers this without doing any division — reduce the fraction, then check the denominator's prime factors against the base's.
- **(e)** Use it to find every denominator under 30 whose reciprocal terminates in base 10 but not base 2.

**Done when:** your function agrees with actual long division for all denominators up to 50 in bases 2, 10 and 12.

<details><summary>Hint for (d) — open only after an attempt</summary>
Reduce the fraction first using <code>gcd</code>. Then repeatedly divide the denominator by each prime factor of the base, as many times as it goes. If you reach 1, it terminates; if anything is left over, it does not.<br><br>
You do not need to factorise the base properly — dividing out each of its prime factors greedily is enough, and for small bases you can hardcode them.
</details>

## Before moving on

- [ ] Explain why base ten was chosen, and why that is not a mathematical reason.
- [ ] State the terminating-fraction rule and apply it in bases 2, 10 and 12.
- [ ] Explain why 0.1 is not exactly representable in binary.
- [ ] Explain why $0.999\ldots = 1$.

**Recap:** Base ten is a biological accident, not a mathematical one — other cultures used 12, 20 and 60 for equally practical reasons. A fraction terminates in base $b$ exactly when its reduced denominator has no prime factors outside those of $b$, which explains both why $\frac{1}{3}$ never terminates in decimal and why 0.1 is not exactly representable in binary. And $0.999\ldots$ equals 1 exactly, because decimal notation does not name every real number uniquely.

**Next:** [[04-hexadecimal|Hexadecimal]] — the base chosen deliberately, for a reason that is entirely mathematical.

## Related

- [[01-introduction|Number bases]] · [[02-binary|Binary]]
- [[foundations/computer-architecture/02-data-representation|computer-architecture/data representation]] — floating point in detail
