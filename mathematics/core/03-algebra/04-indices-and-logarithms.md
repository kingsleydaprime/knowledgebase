# Indices and Logarithms

## Before you start

- You can manipulate algebraic expressions — [[03-algebraic-manipulation|algebraic manipulation]].

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

## Practice — indices


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

**Next:** [[03-approximation-and-standard-form|Scientific Notation]] — the notation exponents make possible, for numbers too large or small to write out.

---

# Part 2 — Logarithms

## 1. A logarithm is an exponent

**That sentence is the whole topic.** Everything else follows from it.

$$\log_b x = y \quad\text{means exactly}\quad b^y = x$$

The logarithm answers: **"what power do I raise $b$ to, in order to get $x$?"**

$$\log_2 8 = 3 \quad\text{because}\quad 2^3 = 8$$

**Logarithm and exponentiation are inverse operations**, in the same way subtraction inverts addition. Reading $\log_2 8$ as "the exponent that turns 2 into 8" makes most confusion disappear.

| Statement | Equivalent exponent form |
| :--- | :--- |
| $\log_{10} 1000 = 3$ | $10^3 = 1000$ |
| $\log_2 16 = 4$ | $2^4 = 16$ |
| $\log_5 1 = 0$ | $5^0 = 1$ |
| $\log_2 0.5 = -1$ | $2^{-1} = 0.5$ |

**Three bases have names.** $\log_{10}$ is the *common* logarithm, often written $\log$. $\log_2$ is the *binary* logarithm, written $\lg$, and it is the one computing uses. $\log_e$ is the *natural* logarithm, written $\ln$, where $e \approx 2.71828$.

## 2. Why logarithms exist

**They were invented to turn multiplication into addition.**

Before calculators, multiplying two six-digit numbers by hand was slow and error-prone. Napier's observation in 1614 was that if you write both numbers as powers of a common base, multiplying them means *adding their exponents* — and adding is easy.

$$\log(xy) = \log x + \log y$$

Look up two logs in a table, add them, look up the answer backwards. That is what a slide rule does mechanically, and it is how engineering was done for three centuries.

**The calculator made that use obsolete and the mathematics more important**, because logarithms turn out to describe how a great many real quantities behave.

## 3. The laws, and where they come from

**Every logarithm law is an index law read backwards.** Do not memorise them separately.

| Index law | Logarithm law | Why |
| :--- | :--- | :--- |
| $b^m \cdot b^n = b^{m+n}$ | $\log(xy) = \log x + \log y$ | multiplying adds exponents |
| $\dfrac{b^m}{b^n} = b^{m-n}$ | $\log\dfrac{x}{y} = \log x - \log y$ | dividing subtracts them |
| $(b^m)^n = b^{mn}$ | $\log(x^n) = n\log x$ | a power multiplies the exponent |
| $b^0 = 1$ | $\log_b 1 = 0$ | nothing raised to zero |
| $b^1 = b$ | $\log_b b = 1$ | — |

**Derivation of the first law**, so you can reconstruct the rest:

Let $\log_b x = m$ and $\log_b y = n$. By definition $x = b^m$ and $y = b^n$. Then

$$xy = b^m \cdot b^n = b^{m+n}$$

so by definition $\log_b(xy) = m + n = \log_b x + \log_b y$. ∎

**Two things that are not laws**, and are the commonest mistakes:

$$\log(x + y) \neq \log x + \log y \qquad\qquad \frac{\log x}{\log y} \neq \log\frac{x}{y}$$

## 4. Changing the base

Your calculator has $\log_{10}$ and $\ln$. Computing uses $\log_2$. The bridge:

$$\log_b x = \frac{\log_c x}{\log_c b}$$

So $\log_2 1000 = \dfrac{\log_{10} 1000}{\log_{10} 2} = \dfrac{3}{0.30103} \approx 9.97$.

> [!NOTE]
> **This is why complexity analysis never states the base.** Changing base only multiplies by a constant — $\log_2 n$ and $\log_{10} n$ differ by a factor of about 3.32, forever.
>
> Since Big-O discards constant factors, $O(\log_2 n)$ and $O(\log_{10} n)$ are **the same class**. That is why [[foundations/dsa/05-algorithms/01-algorithms|complexity analysis]] writes $O(\log n)$ with no base and means it.

## 5. Where logarithms actually show up

- **Complexity.** Binary search is $O(\log n)$ because each step halves the problem, and $\log_2 n$ is precisely "how many times can you halve $n$ before reaching 1".
- **Tree height.** A balanced binary tree over $n$ nodes has height $\log_2 n$ — the same fact from the other direction.
- **Information.** A quantity with $n$ equally likely outcomes needs $\log_2 n$ bits to identify one. Eight outcomes need 3 bits. This is the foundation of [[foundations/information-theory/index|information theory]].
- **Decibels, pH, Richter.** All logarithmic scales, because human perception and physical ranges are multiplicative rather than additive. A Richter 7 is not slightly worse than a 6 — it is about 32 times the energy.
- **Log plots.** Plotting on a log axis turns exponential growth into a straight line, which is why it is the standard way to see whether growth *is* exponential.

## 6. Practice — problems

1. Evaluate without a calculator: $\log_2 32$, $\log_3 81$, $\log_{10} 0.001$, $\log_5 1$, $\log_7 7$.
2. Write as a single logarithm: (a) $\log 6 + \log 4$  (b) $\log 30 - \log 5$  (c) $2\log 3 + \log 2$.
3. Solve for $x$: (a) $\log_2 x = 5$  (b) $\log_x 81 = 4$  (c) $2^x = 40$ (leave the answer as a logarithm, then estimate it).
4. **Derive** the quotient law $\log\frac{x}{y} = \log x - \log y$ from the index laws, as done in section 3.
5. **Why is $\log_b$ undefined for $x \le 0$?** Answer in terms of what $b^y$ can produce for a positive base $b$.
6. A binary search over 1,000,000 items takes at most how many comparisons? Compute $\log_2 10^6$ using the change-of-base rule.

<details><summary>Answers — open only after an attempt</summary>

1. $\log_2 32 = 5$; $\log_3 81 = 4$; $\log_{10} 0.001 = -3$; $\log_5 1 = 0$; $\log_7 7 = 1$.
2. (a) $\log 24$  (b) $\log 6$  (c) $\log(3^2 \cdot 2) = \log 18$.
3. (a) $x = 2^5 = 32$. (b) $x^4 = 81$ so $x = 3$. (c) $x = \log_2 40 = \frac{\log 40}{\log 2} \approx \frac{1.602}{0.301} \approx 5.32$ — check: $2^5 = 32$ and $2^6 = 64$, so a value just above 5 is right.
4. Let $\log_b x = m$, $\log_b y = n$, so $x = b^m$, $y = b^n$. Then $\frac{x}{y} = \frac{b^m}{b^n} = b^{m-n}$, so $\log_b\frac{x}{y} = m - n$. ∎
5. For a positive base $b$, $b^y$ is <strong>always positive</strong>, whatever real $y$ you choose — it approaches zero as $y \to -\infty$ but never reaches or crosses it. So no exponent produces zero or a negative number, and the logarithm of such a value does not exist among the reals.
6. $\log_2 10^6 = \frac{6}{0.30103} \approx 19.9$, so <strong>at most 20 comparisons</strong>. A million items, twenty questions — which is the entire argument for keeping data sorted.
</details>

## Before moving on — logarithms

- [ ] State what a logarithm is in one sentence, without using the word "logarithm".
- [ ] Derive the product law from the index laws.
- [ ] Convert between $\log_2$, $\log_{10}$ and $\ln$ using change of base.
- [ ] Explain why complexity analysis omits the base.
- [ ] Explain why $\log_b x$ is undefined for $x \le 0$.

**Recap:** A logarithm is an exponent — $\log_b x$ is the power that turns $b$ into $x$ — which makes it the inverse of exponentiation. Every logarithm law is an index law read backwards, so they are derived rather than memorised. Changing base multiplies by a constant, which is why Big-O writes $\log n$ with no base. Logarithms describe anything that grows or shrinks multiplicatively, which is why they appear in complexity, tree height, information content and every perceptual scale.

