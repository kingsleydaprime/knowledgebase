---
id: 116a68e8-3d41-46f2-b2e9-90048ac18b77
---

# 7. SCIENTIFIC NOTATION

Scientific notation is a short way of writing very big or very small numbers as a number between 1 and 10 times a power of ten, like 5 × 10^10 instead of 50,000,000,000. Engineers and scientists use it all the time, because counting zeros by hand is slow and easy to get wrong.

## Before you start
<!-- bite: f471da88-e4f2-40b1-b2a3-61c26b875588 -->

- You know the laws of indices — [[01-indices-and-logarithms|exponents]].

**What you will be able to do after this lesson:**

1. Write any number in scientific notation and convert back.
2. Multiply and divide in scientific notation without a calculator.
3. Use significant figures correctly and say what they claim.
4. Estimate an order of magnitude and check a result for plausibility.

**Study route:** read the lesson, then attempt every problem before opening the answers.

---

Engineering deals with ridiculously large and ridiculously small numbers.

For example, the number of transistors in a modern processor can be **tens of billions**.

Writing:

```text
50,000,000,000
```

over and over is annoying.

So we write:

$$
5\times10^{10}
$$

That's scientific notation.

The general form is:

$$
\boxed{a\times10^n}
$$

where \(a\) is typically between 1 and 10.

For example:

$$
3000000=3\times10^6
$$

and:

$$
0.000004=4\times10^{-6}
$$

genui{"learning_viz":{"type_id":"SCIENTIFIC_NOTATION"}}

Notice the exponent tells us which direction the decimal point moves.

Positive exponent:

$$
10^6
$$

means a large number.

Negative exponent:

$$
10^{-6}
$$

means a small number.

This becomes particularly useful in electronics.

For example:

$$
1\mu m=10^{-6}m
$$

and:

$$
1nm=10^{-9}m
$$

Modern semiconductor manufacturing deals with dimensions at scales like these.

---

## Practice — problems
<!-- bite: 8179ae88-c46b-4a7f-b47d-64b66fccd0f8 -->

Attempt all of these before opening the answers.

1. Write in scientific notation: 47,000; 0.00082; 6,022,000,000,000,000,000,000,000; 0.000000001.
2. Compute by hand, leaving the answer in scientific notation: (a) $(3 \times 10^8) \times (2 \times 10^{-3})$  (b) $\frac{6 \times 10^{12}}{3 \times 10^{4}}$  (c) $(4 \times 10^5) + (3 \times 10^6)$.
3. **Why (c) is harder than (a) and (b).** Explain what you must do first when adding, and why multiplication needs no such step.
4. **Significant figures.** How many does each have: 0.00450, 1200, $1.200 \times 10^3$? Why is scientific notation unambiguous where plain decimal is not?
5. **Order-of-magnitude estimation.** Roughly how many seconds are in a human lifetime? Estimate to the nearest power of ten before computing, then check.

<details><summary>Answers — open only after an attempt</summary>

1. $4.7 \times 10^4$; $8.2 \times 10^{-4}$; $6.022 \times 10^{23}$; $1 \times 10^{-9}$.
2. (a) $6 \times 10^5$. (b) $2 \times 10^8$. (c) Convert to a common exponent: $0.4 \times 10^6 + 3 \times 10^6 = 3.4 \times 10^6$.
3. Addition requires the same power of ten because you are adding <em>quantities</em>, and the exponent is part of the quantity. Multiplication does not, because the mantissas and the powers multiply independently — $(a \times 10^m)(b \times 10^n) = ab \times 10^{m+n}$.
4. 0.00450 has <strong>three</strong> (leading zeros only place the point; the trailing zero is significant). 1200 is <strong>ambiguous</strong> — two, three or four. $1.200 \times 10^3$ has <strong>four</strong>, unambiguously. That removal of ambiguity is a real reason scientists use the notation, beyond compactness.
5. About 80 years $\times$ 365 days $\times$ 24 hours $\times$ 3600 s $\approx 2.5 \times 10^9$ — a few billion seconds. Most people guess millions. <strong>The useful habit is getting the exponent right</strong>; the leading digits rarely matter for a sanity check.
</details>

## Before moving on
<!-- bite: 58600bfd-a658-4293-a9a4-789e0bc15af2 -->

You are done with this lesson when you can, closed-book:

- [ ] Convert both ways between decimal and scientific notation.
- [ ] Multiply, divide and add in scientific notation by hand.
- [ ] Count significant figures and explain what they claim about precision.
- [ ] Estimate an order of magnitude and use it to sanity-check a result.

**Recap:** Scientific notation writes any number as a mantissa between 1 and 10 times a power of ten, making very large and very small quantities manageable and comparable. Multiplication and division act on mantissa and exponent independently; addition first requires a common exponent. The notation also makes significant figures unambiguous, which plain decimal cannot do. Its most practical use is order-of-magnitude estimation — getting the exponent right is usually enough to catch an error.

**This is the end of the foundations sequence.** Next is [[mathematics/02-discrete-math/index|discrete mathematics]], which is written and is the natural continuation.
