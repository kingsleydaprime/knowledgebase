# 6. EXPONENTS

## Before you start

- You can manipulate algebraic expressions — [[05-algebraic-manipulation|algebraic manipulation]].

**What you will be able to do after this lesson:**

1. State and apply the laws of indices.
2. Explain why $a^0 = 1$ and why $a^{-n} = \frac{1}{a^n}$, rather than memorising them.
3. Interpret fractional exponents as roots.
4. Recognise exponential growth and say why it defeats intuition.

**Study route:** read the lesson, then attempt every problem before opening the answers.

---

Now let's introduce powers.

Consider:

$$
2^3
$$

This means:

$$
2\times2\times2
$$

Therefore:

$$
2^3=8
$$

The 2 is called the **base**.

The 3 is the **exponent**.

So:

$$
\underbrace{2}_{\text{base}}^{\underbrace{3}_{\text{exponent}}}
$$

means "multiply 2 by itself 3 times."

---

Some important rules:

### Multiplication

$$
a^m a^n=a^{m+n}
$$

Example:

$$
2^3\times2^4=2^7
$$

### Division

$$
\frac{a^m}{a^n}=a^{m-n}
$$

### Power of a power

$$
(a^m)^n=a^{mn}
$$

These rules become extremely important when we start dealing with:

- binary
- memory sizes
- transistor counts
- signal amplitudes
- scientific notation
- logarithms

---

## Practice — problems

Attempt all of these before opening the answers.

1. Simplify: (a) $x^3 \cdot x^5$  (b) $\frac{y^7}{y^2}$  (c) $(z^2)^4$  (d) $(2ab^2)^3$.
2. Evaluate without a calculator: $2^{-3}$, $16^{1/2}$, $27^{2/3}$, $5^0$, $(\frac{1}{4})^{-2}$.
3. **Derive, do not memorise.** Using only $\frac{a^m}{a^n} = a^{m-n}$, show that $a^0 = 1$ and that $a^{-n} = \frac{1}{a^n}$.
4. **Why fractional exponents are roots.** If $a^{1/2} \cdot a^{1/2} = a^1 = a$, what must $a^{1/2}$ be?
5. **Exponential growth.** A sheet of paper 0.1 mm thick is folded in half 42 times. How thick is it? Compute $0.1 \times 2^{42}$ mm in kilometres before you guess.

<details><summary>Answers — open only after an attempt</summary>

1. (a) $x^8$. (b) $y^5$. (c) $z^8$. (d) $8a^3b^6$.
2. $2^{-3} = \frac{1}{8}$; $16^{1/2} = 4$; $27^{2/3} = (27^{1/3})^2 = 9$; $5^0 = 1$; $(\frac{1}{4})^{-2} = 16$.
3. $\frac{a^n}{a^n} = a^{n-n} = a^0$. But any non-zero quantity divided by itself is 1, so $a^0 = 1$. Similarly $\frac{a^0}{a^n} = a^{-n}$, and the left side is $\frac{1}{a^n}$. <strong>Neither is a convention — both are forced</strong> by requiring the subtraction law to keep working.
4. $a^{1/2}$ is the number that multiplied by itself gives $a$ — the <strong>square root</strong>. The notation is not analogy; it follows from the multiplication law.
5. $2^{42} \approx 4.4 \times 10^{12}$, so the thickness is about $4.4 \times 10^{11}$ mm $= 440{,}000$ km — <strong>past the Moon</strong>, which is about 384,000 km away. Almost nobody guesses within three orders of magnitude, and that failure of intuition is the entire point of the exercise.
</details>

## Before moving on

You are done with this lesson when you can, closed-book:

- [ ] State the laws of indices and apply them to a compound expression.
- [ ] Derive $a^0 = 1$ and $a^{-n} = 1/a^n$ from the division law.
- [ ] Interpret a fractional exponent as a root and justify it.
- [ ] Estimate an exponential quantity and explain why intuition fails.

**Recap:** Exponents are shorthand for repeated multiplication, and their laws follow from that meaning rather than being arbitrary rules. Requiring the division law to hold in every case forces $a^0 = 1$ and $a^{-n} = 1/a^n$, and requiring the multiplication law to hold forces $a^{1/2}$ to be a square root. Exponential growth outruns intuition dramatically, which is why it must be computed rather than estimated.

**Next:** [[07-scientific-notation|Scientific Notation]] — the notation exponents make possible, for numbers too large or small to write out.
