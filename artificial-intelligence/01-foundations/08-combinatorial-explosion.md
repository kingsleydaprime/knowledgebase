---
id: a45b70d9-1455-4341-b990-b009c518ffed
---

# Combinatorial Explosion

Combinatorial explosion is the way the number of possibilities in a problem grows so fast, as the problem gets bigger, that checking them all becomes impossible.

## Before you start
<!-- bite: 40a55d35-7da4-434d-a2a3-bf223f21996a -->

Read [[artificial-intelligence/01-foundations/07-types-of-problems-and-techniques|Types of Problems and Techniques]] first. You'll need multiplication and powers ($3^4$ means $3 \times 3 \times 3 \times 3$).

After this lesson you will be able to:

1. name the three central problems of AI;
2. explain combinatorial explosion with the $z^n$ formula, and compare it with constant, linear and quadratic growth;
3. work out the worst-case size of the Mancala (ayo) game tree, and say why the worst case matters;
4. explain how a heuristic cuts the search, and why that's the only way through.

## What combinatorial explosion is
<!-- bite: 52c1d892-f069-401b-a69b-0beafa0f4b11 -->

Imagine a padlock with 3 dials, each with 10 digits. There are $10 \times 10 \times 10 = 1{,}000$ combinations. Add one dial, and there are 10,000. Every extra dial multiplies the work by 10. With 12 dials, there are a trillion combinations, and trying one a second would take over 30,000 years.

That's **combinatorial explosion**: each new variable *multiplies* the number of possibilities instead of adding to it. Your notes define it as an exponential or polynomial increase in complexity depending on the number of input variables and the number of states each input variable can take.

It's the single biggest reason AI is hard, and it's why the rest of this subject spends so much time on clever search.

## The kid version
<!-- bite: c65e948d-57ed-440c-aed1-0ecade9dc82b -->

You're choosing an outfit: 3 shirts, 3 trousers, 3 pairs of shoes. That's $3 \times 3 \times 3 = 27$ outfits. Easy to try them all. Now add 3 caps, 3 watches and 3 bags: 729 outfits. Add a few more things, and you'd spend your whole life trying outfits on. So you don't try them all: you use rules of thumb, like "blue goes with brown", and only try the few that make sense.

**Where the analogy stops working.** With outfits, a wrong choice just looks odd. In a real problem, such as a chess game or a flight schedule, the rule of thumb might rule out the one good answer, so choosing good rules of thumb matters a lot.

## The three problems of AI
<!-- bite: d5a27623-1413-44f7-9822-4507c8204358 -->

Your notes list three central problems AI has to solve:

1. **Knowledge representation**: how to describe what we know about the world so a program can use it.
2. **Knowledge acquisition**: how to get that knowledge into the program in the first place.
3. **Knowledge application**: how to use the knowledge to solve a problem, which nearly always means searching through possibilities.

The third is where combinatorial explosion hits. Applying knowledge means trying combinations, and the combinations explode.

## Counting the explosion: z to the power n
<!-- bite: 9c7f124a-01b5-4ccf-b880-a2b163e0a6cd -->

Your notes draw it with one parameter that can take 3 different values. One parameter: 3 possibilities. Two parameters: each value of the first goes with each value of the second, so $3 \times 3 = 3^2 = 9$. Three parameters: $3^3 = 27$.

In words: if each of $n$ variables can be in any of $z$ states, the total number of combinations is $z$ multiplied by itself $n$ times.

$$\text{combinations} = z^n$$

where $z$ is the number of possible states for each variable and $n$ is the number of input variables. With $z = 3$ and just 10 variables, that's $3^{10} = 59{,}049$. The number of variables sits in the *exponent*, and that's what makes it explode.

## Ways a problem can grow
<!-- bite: df7a3248-0e10-4699-bc71-9eb31195099a -->

Your notes use the $O(\,)$ notation to compare how fast the work grows as the input size $n$ grows:

1. **Constant, $O(1)$**: the work doesn't grow at all, like looking up item number 5 in a list.
2. **Linear, $O(n)$**: double the input, double the work, like reading every name on a list.
3. **Quadratic, $O(n^2)$**: double the input, four times the work, like comparing every pair of names.
4. **Exponential, $O(2^n)$ or $O(z^n)$**: add *one* to the input, and the work multiplies. That's combinatorial explosion.

## Polynomial versus exponential
<!-- bite: 6b2b0584-9319-4dc3-9bd7-f49e6f2fbc08 -->

Put numbers in to see the difference:

| $n$ | $n^2$ (quadratic) | $2^n$ (exponential) |
|---|---|---|
| 10 | 100 | 1,024 |
| 20 | 400 | 1,048,576 |
| 30 | 900 | 1,073,741,824 |
| 40 | 1,600 | 1,099,511,627,776 |

Quadratic growth is slow and steady: going from 10 to 40 multiplies it by 16. Exponential growth is a wall: going from 10 to 40 multiplies it by about a billion. A computer twice as fast lets a quadratic method handle a problem about 41% bigger, but an exponential method only one step bigger. That's the **tyranny of combinatorial explosion**: no amount of faster hardware catches up with it.

## Example: the African game Mancala
<!-- bite: 479783f8-19b3-45c7-ae88-3f6f12de489a -->

The SSG 503 papers ask three times for the worst-case complexity of **Mancala**, the family of games that includes **ayo** (Yoruba), **awari** and **okweese**. In ayo, each player has 6 pits. On your turn you choose one of your pits to sow from, so you have at most 6 choices. The branching factor is $b \le 6$.

If a program looks $m$ moves ahead, the game tree has at most $6 \times 6 \times \dots \times 6 = 6^m$ positions at the bottom:

$$\text{worst-case time} = O(6^m), \qquad \text{space (depth-first)} = O(6m)$$

Put numbers in, for a computer that checks a million positions a second:

1. **10 moves ahead:** $6^{10} = 60{,}466{,}176$ positions, about a minute.
2. **20 moves ahead:** $6^{20} \approx 3.66 \times 10^{15}$ positions, about **116 years**.

Doubling how far ahead you look took the time from a minute to over a century.

## Why consider the worst case
<!-- bite: d13c8ddd-897b-4106-8556-383f9c353d26 -->

The exam also asks why it's necessary to consider the worst case. Because a game program has to move in a fixed time *every* turn. The average position might be easy, with only 2 or 3 sensible pits, but the program has to be ready for the position where all 6 pits are possible on every move. If it only planned for the average, it would run out of time exactly in the hardest positions, which are usually the important ones. The worst case is the guarantee; the average case is only a hope.

## How a heuristic cuts the explosion
<!-- bite: 016e22b3-3089-401d-b976-fea615986af2 -->

Ayo players use a rule of thumb: **avoid leaving runs of contiguous (side-by-side) empty pits**, because they let your opponent capture easily. A program can use the same heuristic to *prune*: never explore moves that create such a position.

Say it rules out 2 of the 6 moves on a typical turn. The effective branching factor drops from 6 to 4. Looking 10 moves ahead, that's $4^{10} = 1{,}048{,}576$ positions instead of 60,466,176, about **58 times fewer**. Every pruned move cuts off a whole subtree below it, so a small cut at each level compounds into a huge saving. That's exactly what heuristics, alpha-beta pruning and good problem formulation do in the rest of this subject.

## When search is the only option
<!-- bite: a735b363-43ad-4f72-b304-75aa4c945491 -->

A 2012/13 question puts it this way: some problems have a closed-form algebraic solution (a formula), some are solved by numerical methods, but problems that demand intelligence usually depend on **search**. Why doesn't search always work, and what's done to make it viable?

Search doesn't always work because of combinatorial explosion: the space is too big to search fully in any reasonable time. To make it viable, we:

1. **Use heuristics** to explore the most promising states first (section 03).
2. **Prune** branches that can't lead anywhere useful (alpha-beta, section 04).
3. **Formulate the problem well**, with abstraction, so the state space is as small as possible (lesson 06).
4. **Accept a good answer instead of the best one**, with local search.

Some problems, called **NP-complete**, seem to have no fast exact method at all. The travelling salesman problem is one. For them, heuristics aren't a shortcut; they're the only practical way to get an answer.

## Terms used in this lesson
<!-- bite: 1722f558-9e0c-4b1d-9ab6-b7f1459b55c0 -->

1. **Combinatorial explosion**: This is the very fast growth in the number of possible combinations as a problem gains more variables or more states per variable.
2. **Tyranny of combinatorial explosion**: This is the fact that faster computers barely help with an exponentially growing problem, because each extra variable multiplies the work.
3. **Knowledge representation, acquisition and application**: These are the three central problems of AI: describing knowledge, getting it into a program, and using it to solve problems.
4. **Exponential growth**: This is growth where adding one to the input multiplies the work, as in $2^n$ or $z^n$.
5. **Polynomial growth**: This is growth like $n$ or $n^2$, where the work rises steadily rather than multiplying.
6. **Worst case**: This is the largest amount of work an algorithm can need for any input of a given size.
7. **NP-complete problem**: This is a problem for which no fast exact algorithm is known, and for which finding one would also solve thousands of other hard problems.

## Common pitfalls and traps
<!-- bite: 39395135-5bf2-4d5b-984c-38b2cf5d829d -->

- **Thinking a faster computer solves the problem.** Against $2^n$, doubling speed buys you one more step of $n$.
- **Mixing up $n^2$ and $2^n$.** In $n^2$ the input is the base; in $2^n$ it's the exponent. The second is the explosion.
- **Treating the worst case as unlikely, so unimportant.** A program that must answer in fixed time has to be ready for it.

## Check your understanding
<!-- bite: 9b8d14da-a1f3-47ee-87c0-f8b2ac803e1a -->

Try each one before you open the answer.

1. <!-- q: exact id="2154df98" answer="81" -->
   A problem has 4 variables, and each can be in any of 3 states. How many combinations are there?

   <details><summary>Answer</summary>

   $3^4 = 81$, using $z^n$ with $z = 3$ and $n = 4$.

   </details>

2. <!-- q: exact id="b49f749f" answer="1296" accept="1,296" -->
   A Mancala program has at most 6 choices each move and looks 4 moves ahead. How many positions are at the bottom of its game tree in the worst case?

   <details><summary>Answer</summary>

   $6^4 = 1{,}296$.

   </details>

3. <!-- q: mcq id="87605d8f" -->
   Which growth is the combinatorial explosion?

   - [ ] $O(1)$
   - [ ] $O(n)$
   - [ ] $O(n^2)$
   - [x] $O(2^n)$

   <details><summary>Answer</summary>

   $O(2^n)$: adding one to the input doubles the work. The others are constant, linear and quadratic, which grow far more slowly.

   </details>

4. <!-- q: gap id="6239a191" answers="representation;acquisition;application" -->
   The three problems of AI are knowledge ___, knowledge ___ and knowledge ___.

   <details><summary>Answer</summary>

   Representation, acquisition and application.

   </details>

5. <!-- q: open id="6162114f" -->
   A Mancala heuristic says "avoid states with contiguous empty holes". Explain how it reduces the search space.

   <details><summary>Answer</summary>

   Moves that leave runs of empty pits give the opponent easy captures, so the program treats them as bad and doesn't explore them. Every move it skips removes the whole subtree under it. If the heuristic cuts the typical number of moves from 6 to 4, the tree 10 moves deep shrinks from $6^{10} \approx 60$ million positions to $4^{10} \approx 1$ million, about 58 times fewer.

   </details>

## Before moving on
<!-- bite: 8d97c611-d5d3-4100-9ebf-275b3fc3fcf6 -->

You're done when you can name the three problems of AI, explain combinatorial explosion with $z^n$ and a table, work out the Mancala worst case, and explain why heuristics are the way through.

Recap: combinatorial explosion means each extra variable multiplies the possibilities: $z^n$ combinations. Exponential growth outruns any computer, which is its tyranny. Ayo has at most 6 moves a turn, so looking $m$ moves ahead costs $O(6^m)$: a minute for 10 moves, over a century for 20. The worst case matters because the program must answer in fixed time. Heuristics and pruning cut the branching factor and are what make search workable.

That's the end of section 01. Section 02 starts the search methods themselves, with [[artificial-intelligence/02-uninformed-search/01-what-search-is|What Search Is]].

## Related
<!-- bite: 3578bb4e-3fd1-4ebb-b3f3-bad77c17c739 -->

- [[artificial-intelligence/02-uninformed-search/02-measuring-a-search-method|Measuring a Search Method]]: the exponential wall in search trees.
- [[theory-of-computation/07-complexity-classes|Complexity Classes]]: P, NP and NP-completeness properly.

## About this lesson
<!-- bite: 8bba1f6d-6eb5-45db-87c4-9725f1672bc5 -->

**Level:** introductory, with powers. Lesson 8 of section 01 (foundations). It covers the three problems of AI, combinatorial explosion and $z^n$, growth rates, Mancala's worst-case complexity and its heuristic, and why search needs heuristics.

**Source:** University of Lagos SSG 503 class notes, first note (problems of AI, combinatorial explosion, the $z^n$ diagram and the $O(\,)$ notation), and the SSG 503 past papers (2012/13, 2014/15, 2016/17: Mancala, combinatorial explosion and the tyranny question). Every number is computed and asserted by `scripts/diagrams/ai_gaps.py`.
