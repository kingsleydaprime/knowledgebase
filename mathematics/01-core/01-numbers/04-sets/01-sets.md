# 2. SETS

## Before you start

- You know what a number system is — [[01-number-systems|numbers]].

**What you will be able to do after this lesson:**

1. Use set notation for membership, subset, union, intersection and complement.
2. Draw and read a Venn diagram for up to three sets.
3. Apply the inclusion-exclusion principle to a counting problem.
4. Explain why sets underpin databases, type systems and search.

**Study route:** read the lesson, then attempt every problem before opening the answers.

---

Now let's introduce another fundamental mathematical idea.

A **set** is simply a collection of distinct objects.

For example:

$$
A=\{1,2,3,4,5\}
$$

We say:

> 3 belongs to set \(A\).

Written:

$$
3\in A
$$

But:

$$
7\notin A
$$

A set can contain numbers:

$$
A=\{1,2,3\}
$$

letters:

$$
B=\{a,b,c\}
$$

or even objects:

$$
C=\{\text{CPU},\text{RAM},\text{SSD}\}
$$

---

## Why are sets important to computing?

Because computers constantly deal with **collections of things**.

For example:

```text
Set of valid states
Set of memory addresses
Set of instructions
Set of possible inputs
Set of characters
Set of numbers
```

Later, when we talk about **Boolean logic**, we'll essentially be working with systems containing a very small set of possible states:

$$
\{0,1\}
$$

That's where our earlier transistor discussion starts connecting back to mathematics.

---

## Practice — problems

Attempt all of these before opening the answers.

1. Given $A = \{1,2,3,4,5\}$, $B = \{4,5,6,7\}$, $U = \{1,\ldots,10\}$, find $A \cup B$, $A \cap B$, $A \setminus B$, $A'$, and $(A \cap B)'$.
2. **Inclusion–exclusion.** In a class of 40, 25 study Physics, 20 study Chemistry and 8 study both. How many study neither? Draw the Venn diagram first.
3. **Three sets.** Of 100 people, 60 like tea, 50 like coffee, 40 like juice; 30 like tea and coffee, 20 tea and juice, 15 coffee and juice, and 10 like all three. How many like none?
4. **Why is $|A \cup B| = |A| + |B| - |A \cap B|$ rather than $|A| + |B|$?** Answer in one sentence about double counting.
5. **Where do you already use this?** Name the set operation each of these performs: SQL `UNION`, SQL `INNER JOIN`, Python's `&` on sets, a search query `cats -dogs`.

<details><summary>Answers — open only after an attempt</summary>

1. $A \cup B = \{1,2,3,4,5,6,7\}$; $A \cap B = \{4,5\}$; $A \setminus B = \{1,2,3\}$; $A' = \{6,7,8,9,10\}$; $(A \cap B)' = \{1,2,3,6,7,8,9,10\}$.
2. $|P \cup C| = 25 + 20 - 8 = 37$, so $40 - 37 = \mathbf{3}$ study neither.
3. $|T \cup C \cup J| = 60+50+40-30-20-15+10 = 95$, so $\mathbf{5}$ like none. Note the pattern: add singles, subtract pairs, add back the triple — each region must be counted exactly once.
4. Because elements in both sets are counted once in $|A|$ and again in $|B|$, so the overlap must be subtracted once to leave every element counted exactly once.
5. `UNION` is $\cup$; `INNER JOIN` is $\cap$ on the join key; Python's `&` is $\cap$; `cats -dogs` is set difference $\setminus$.
</details>

## Before moving on

You are done with this lesson when you can, closed-book:

- [ ] Use union, intersection, difference and complement correctly.
- [ ] Draw a three-set Venn diagram and label every region.
- [ ] Apply inclusion–exclusion and explain why the alternating signs appear.
- [ ] Name a computing operation that is each set operation.

**Recap:** A set is an unordered collection with no duplicates, and set notation is the language for saying precisely which things belong. Union, intersection, difference and complement combine sets; Venn diagrams show the regions. Inclusion–exclusion corrects for double counting by adding singles, subtracting pairs and adding back triples, so every element is counted exactly once. Databases, type systems and search queries are all set operations wearing different syntax.

**Next:** [[02-variables|Variables]] — what happens when you stop naming specific numbers and start naming unknown ones.
