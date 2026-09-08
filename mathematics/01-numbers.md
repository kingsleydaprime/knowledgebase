# 1. NUMBER SYSTEMS

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
