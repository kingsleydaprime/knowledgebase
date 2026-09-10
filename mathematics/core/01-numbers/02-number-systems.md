# 1. NUMBER SYSTEMS

## Before you start

- You can do arithmetic with whole numbers and fractions.
- You have met [[core/01-numbers/01-number-bases/01-introduction|number bases]], though it is not required.

**What you will be able to do after this lesson:**

1. Name the number systems in order and say what each one adds.
2. Explain what problem each extension was invented to solve.
3. Decide which system a given quantity needs.
4. Explain why the reals are needed and what irrational means.

**Study route:** read the lesson, then attempt every problem before opening the answers.

---

Before computers can manipulate information, **we need something to represent the information with**.

The most fundamental mathematical objects we use for this are **numbers**.

But interestingly, mathematics doesn't have just one "type" of number.

We have different number systems.

---

## 1.1 Natural Numbers

These are the numbers we use for **counting**.

Depending on convention, you'll see either:

$$
\mathbb{N} = \{1,2,3,4,5,\ldots\}
$$

or

$$
\mathbb{N} = \{0,1,2,3,4,5,\ldots\}
$$

We'll use the second convention:

$$
\boxed{\mathbb{N}=\{0,1,2,3,\ldots\}}
$$

Think:

> **"How many?"**

For example:

- 0 computers
- 1 computer
- 2 computers
- 50 computers
- 1,000 computers

You can't have **2.7 computers** in ordinary counting.

So natural numbers are useful for **discrete quantities**.

And notice something important already.

A computer is fundamentally a **discrete system**.

That connection will become VERY important in Week 2.

---

# 1.2 Integers

Now suppose you want to represent things like:

- temperatures below zero
- money you owe
- movement backward
- a position to the left of zero

Natural numbers aren't enough.

So we introduce negative numbers.

The integers are:

$$
\mathbb{Z}=\{\ldots,-3,-2,-1,0,1,2,3,\ldots\}
$$

For example:

```text
← negative                 positive →
---|---|---|---|---|---|--->
  -3  -2  -1   0   1   2   3
```

So:

$$
-5,\,-2,\,0,\,4,\,17
$$

are all integers.

But:

$$
\frac12
$$

isn't an integer.

Neither is:

$$
3.14159
$$

---

# 1.3 Rational Numbers

Now we encounter fractions.

A **rational number** is any number that can be expressed as:

$$
\boxed{\frac{p}{q}}
$$

where \(p\) and \(q\) are integers and:

$$
q\neq0
$$

Examples:

$$
\frac12
$$

$$
\frac34
$$

$$
-\frac72
$$

$$
5=\frac51
$$

$$
0=\frac01
$$

So integers are actually rational numbers too.

For example:

$$
7=\frac71
$$

This means:

$$
\boxed{\mathbb{Z}\subset\mathbb{Q}}
$$

Read that as:

> "The integers are a subset of the rational numbers."

---

## Something interesting happens with decimals

Consider:

$$
\frac12=0.5
$$

Easy.

Now:

$$
\frac13=0.333333\ldots
$$

The decimal continues forever.

But it is still rational because it can be written as:

$$
\frac13
$$

So a rational number can have either:

- a terminating decimal
- or a repeating decimal

For example:

$$
\frac14=0.25
$$

and

$$
\frac13=0.333333\ldots
$$

---

# 1.4 Real Numbers

Now we encounter numbers that **cannot** be represented as a fraction of two integers.

For example:

$$
\sqrt2
$$

There is no pair of integers \(p,q\) such that:

$$
\sqrt2=\frac pq
$$

Another famous example is:

$$
\pi
$$

These are called **irrational numbers**.

So the real numbers contain both:

### Rational numbers

$$
\frac12,\quad -3,\quad 0.75,\quad 7,\quad \frac{22}{7}
$$

and irrational numbers:

$$
\sqrt2,\quad\pi,\quad e
$$

Therefore:

$$
\boxed{\mathbb{R}=\text{rational numbers + irrational numbers}}
$$

And our hierarchy becomes:

```text
Natural numbers
      ↓
   Integers
      ↓
Rational numbers
      ↓
  Real numbers
```

More formally:

$$
\boxed{\mathbb N\subset\mathbb Z\subset\mathbb Q\subset\mathbb R}
$$

That's an important relationship to remember.

---

# Why do we care about all these categories?

Because later, when we're dealing with computers, we'll repeatedly ask:

> **What kind of value are we representing?**

For example:

A CPU register might contain:

```text
00001101
```

What does that mean?

It could represent:

$$
13
$$

It could represent:

$$
-3
$$

It could be part of a memory address.

It could represent a character.

It could be part of a floating-point number.

The physical bits themselves don't inherently "mean" anything.

**The representation system gives them meaning.**

And that is going to become one of the biggest ideas in our entire course.

---

## Practice — problems

Attempt all of these before opening the answers.

1. **Which system is the smallest that contains each of these?** $-7$, $\frac{22}{7}$, $\sqrt{2}$, $0$, $\pi$, $3.75$, $\sqrt{-1}$.
2. **Closure.** A set is *closed* under an operation if the result is always still in the set. For each of $\mathbb{N}, \mathbb{Z}, \mathbb{Q}, \mathbb{R}$, say whether it is closed under addition, subtraction, multiplication and division. **The gaps in that table are exactly why each new system was invented.**
3. **Prove $\sqrt{2}$ is irrational.** Assume $\sqrt{2} = \frac{a}{b}$ in lowest terms and derive a contradiction.
4. **Why does a computer's `int` type not model $\mathbb{Z}$?** Name two ways it differs.

<details><summary>Answers — open only after an attempt</summary>

1. $-7 \in \mathbb{Z}$; $\frac{22}{7} \in \mathbb{Q}$; $\sqrt{2} \in \mathbb{R}$ (irrational); $0 \in \mathbb{N}$ by most modern conventions, otherwise $\mathbb{Z}$; $\pi \in \mathbb{R}$; $3.75 \in \mathbb{Q}$ (it is $\frac{15}{4}$); $\sqrt{-1} \in \mathbb{C}$.
2. $\mathbb{N}$: closed under $+$ and $\times$ only. $\mathbb{Z}$: adds closure under $-$. $\mathbb{Q}$: adds closure under $\div$ (except by zero). $\mathbb{R}$: adds closure under limits, which is what makes $\sqrt{2}$ and $\pi$ exist. <strong>Each system is the previous one plus whatever was needed to close an operation.</strong>
3. If $\sqrt{2} = \frac{a}{b}$ in lowest terms, then $a^2 = 2b^2$, so $a^2$ is even, so $a$ is even. Write $a = 2k$: then $4k^2 = 2b^2$, so $b^2 = 2k^2$ and $b$ is even too. But then $a$ and $b$ share a factor of 2, contradicting "lowest terms".
4. It is <strong>finite</strong> (a 32-bit int stops at about 2.1 billion and wraps or overflows), and it is <strong>not closed under division</strong> (integer division truncates). See [[foundations/computer-architecture/02-data-representation|data representation]].
</details>

## Before moving on

You are done with this lesson when you can, closed-book:

- [ ] Name the number systems in order and what each adds.
- [ ] State which operations each system is closed under.
- [ ] Prove $\sqrt{2}$ is irrational.
- [ ] Explain why a machine integer is not $\mathbb{Z}$.

**Recap:** Each number system exists because the previous one could not answer a question. Naturals count but cannot express debt, so integers add negatives. Integers cannot divide evenly, so rationals add fractions. Rationals leave gaps on the line — $\sqrt{2}$ is not a ratio of whole numbers — so reals fill them. Each extension is the smallest one that closes an operation the previous system could not.

**Next:** [[01-sets|Sets]] — the language used to state precisely what a number system *is*.
