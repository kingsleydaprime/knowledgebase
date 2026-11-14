# The Geometry of Linear Programs

**[Intermediate]** — Why the best answer to a linear program is always at a corner of the feasible region, how to solve a two-variable LP with a pencil, and the algebra of corners that the simplex method runs on.

**Source:** `[reference]` — see [[operations-research/index|the domain note]].

## Before you start

You need to be able to write a small LP from words → [[operations-research/02-formulating-linear-programs|note 02]], draw the line $4x_1 + 3x_2 = 240$ by finding where it crosses each axis, and solve two simultaneous equations.

After this lesson you will be able to:

1. Solve any two-variable LP graphically, and explain why checking the corners is enough.
2. Recognise the four outcomes an LP can have: one optimum, many optima, infeasible, unbounded.
3. Convert an LP to standard form with slack variables, and list its basic solutions by hand.

**Study route:** sections 1–3 with a pencil and graph paper. Stop after section 3 and do the workshop graph yourself with the note closed. Then sections 4–5.

## The kid version

Imagine a fenced field with straight fences, and a hill that rises steadily in one direction — no bumps, no dips, just a tilted flat plane. You want to stand as high as possible without leaving the field. Walk uphill and you'll hit a fence. Walk along the fence uphill and you'll hit a corner. **The highest spot in a field with straight fences on a tilted plane is always at a corner.** So you never need to search the middle of the field: just check the corners.

**Where the analogy stops working.** A real field has two dimensions. An LP with 1,000 variables has a "field" in 1,000 dimensions with an astronomically large number of corners, so "check every corner" stops being practical. The simplex method (note 04) is a clever way of walking from corner to corner uphill, visiting only a tiny fraction of them.

## 1. Why this exists

The workshop from note 01 asks you to choose $x_1$ tables and $x_2$ chairs. There are infinitely many feasible plans — 12.5 tables and 30.2 chairs is one. Trying them all is impossible. **Geometry tells you that only a handful of points can ever be optimal**, which turns an infinite search into a finite one. Every LP algorithm is built on that fact.

## Terms used in LP geometry

1. **Half-plane**: This is the set of points on one side of a straight line, including the line. Each $\le$ constraint in two variables is a half-plane.
2. **Convex set**: A set is convex when the straight line between any two of its points stays entirely inside the set. A disc is convex; a crescent moon isn't. The feasible region of an LP is always convex, because it's the overlap of half-planes and overlaps of convex sets are convex.
3. **Corner point**: This is also known as a **vertex** or an **extreme point**. This is a point of the feasible region that isn't on the line between two other feasible points — in two dimensions, where two boundary lines meet.
4. **Binding constraint**: This is also known as an **active** or **tight** constraint. A constraint is binding at a solution when it holds with equality there — the resource is used up exactly.
5. **Iso-profit line**: This is also known as a **contour** of the objective. This is a line along which the objective has the same value, such as all plans earning exactly ₦280,000.
6. **Slack variable**: This is a new, non-negative variable that measures the unused part of a $\le$ constraint. It turns the inequality into an equation.
7. **Standard form**: This is a way of writing an LP with every constraint as an equation and every variable non-negative. The simplex method needs this form.
8. **Basic solution**: This is a solution found by setting some variables to zero and solving the constraint equations for the rest. The ones that are non-negative are exactly the corner points.

## 2. Solving the workshop graphically

The model, from note 01:

$$\max\; 7x_1 + 5x_2 \quad\text{s.t.}\quad 4x_1 + 3x_2 \le 240,\quad 2x_1 + x_2 \le 100,\quad x_1, x_2 \ge 0$$

**Step 1 — draw each constraint as a line.** Find where it crosses each axis.

1. Carpentry, $4x_1 + 3x_2 = 240$: when $x_1 = 0$, $x_2 = 80$. When $x_2 = 0$, $x_1 = 60$.
2. Finishing, $2x_1 + x_2 = 100$: when $x_1 = 0$, $x_2 = 100$. When $x_2 = 0$, $x_1 = 50$.

**Step 2 — shade the side that's allowed.** Test the origin: $0 \le 240$ and $0 \le 100$ are both true, so the allowed side of each line is the side containing $(0, 0)$.

```
 x2 (chairs)                    not to scale
 100 ┼ F                        F–C–B is finishing:  2x1 + x2 = 100
     │  ╲                       D–C–G is carpentry:  4x1 + 3x2 = 240
  80 ┼ D  ╲
     │░░ ─ ╲
  60 ┼░░░░░─╲
     │░░░░░░░╲─
  40 ┼░░░░░░░░ C
     │░░░░░░░░░╲ ─
  20 ┼░░░░░░░░░░╲   ─
     │░░░░░░░░░░░╲     ─
   0 ┼ A──────────B───────G──── x1 (tables)
     0            50      60
```

The shaded region with corners $A=(0,0)$, $B=(50,0)$, $C=(30,40)$ and $D=(0,80)$ is the feasible region. From D to C the carpentry line is the tighter limit; from C to B the finishing line is. F $=(0,100)$ and G $=(60,0)$ are where each line hits an axis *outside* the region.

**Step 3 — find corner C** by solving the two lines together. From finishing, $x_2 = 100 - 2x_1$. Substitute into carpentry: $4x_1 + 3(100 - 2x_1) = 240$, so $-2x_1 = -60$ and $x_1 = 30$, $x_2 = 40$.

**Pause and predict:** which corner earns the most?

**Step 4 — evaluate the objective at each corner.**

| Corner | Plan | Profit $7x_1 + 5x_2$ (₦ thousands) |
|---|---|---|
| A | (0, 0) | 0 |
| B | (50, 0) — all tables | 350 |
| **C** | **(30, 40)** | **410** |
| D | (0, 80) — all chairs | 400 |

**The optimum is C: 30 tables and 40 chairs.** All-tables (B) loses because tables are hungry for *finishing* time — 50 tables use all 100 finishing hours while leaving 40 carpentry hours idle. Swapping some tables for chairs uses the idle carpentry. **The best plan uses both scarce resources fully**, and in the picture that means the corner where both lines meet.

### The iso-profit view

Draw the line $7x_1 + 5x_2 = k$ for some value $k$. Increasing $k$ slides the line parallel to itself, away from the origin. The optimum is the last point of the feasible region the line touches before leaving it.

The slope of the profit line is $-7/5 = -1.4$. Carpentry has slope $-4/3 \approx -1.33$ and finishing has slope $-2$. The profit line's slope lies *between* them, which is exactly why the last point touched is the corner where they meet. **This slope comparison is the geometric heart of sensitivity analysis**: if table profit rose until the profit line was steeper than finishing, the optimum would jump to B → [[operations-research/05-duality-and-sensitivity|note 05]].

## 3. Why the answer is always at a corner

**The fundamental theorem of linear programming states that if an LP has an optimal solution, then at least one optimal solution is at a corner point of the feasible region.**

The argument, in words. Take any feasible point that isn't a corner. Because it's not a corner, it lies on a line segment between two other feasible points. Along that segment the objective is linear, so it either rises in one direction or is constant. Move in the direction that doesn't make things worse until you hit a new constraint. You've reached a point with at least one more binding constraint and no worse objective. Repeat; after finitely many moves there's nowhere left to slide, and you're at a corner.

Two consequences matter:

1. **You only need to check corners.** In two variables, there are a handful. That's the graphical method.
2. **Corners are where constraints are binding.** In $n$ variables, a corner is where $n$ independent constraints hold with equality. That gives an algebraic way to find corners without drawing anything — section 5.

## 4. The four possible outcomes

Every LP ends in exactly one of these.

1. **A unique optimum.** The workshop. One corner beats all others.
2. **Multiple optima.** If the profit line is *parallel* to a binding constraint, a whole edge is optimal. Change the profits to ₦8,000 per table and ₦4,000 per chair: the profit line $8x_1 + 4x_2$ has slope $-2$, the same as finishing. Corners B and C both earn 400, and so does every point on the edge between them. The solver returns one of them; it doesn't tell you there were others unless you ask.
3. **Infeasible.** The constraints have no point in common. Add "make at least 70 tables": no point satisfies $x_1 \ge 70$ and $2x_1 + x_2 \le 100$ together. The shaded region is empty.
4. **Unbounded.** The region extends forever in an improving direction. Delete both resource constraints and profit is infinite. In a real model this is always a missing constraint.

A fifth situation is worth knowing about though it isn't an outcome: **degeneracy**, where more constraints than necessary pass through one corner. In two variables, three lines through one point. It's harmless geometrically but can make the simplex method stall → [[operations-research/04-the-simplex-method|note 04]].

## 5. The algebra of corners

Drawing stops working at three variables. The algebraic version works in any number.

### Standard form

Add a **slack variable** to each $\le$ constraint to soak up the unused amount. For the workshop, $s_1$ is idle carpentry hours and $s_2$ is idle finishing hours:

$$\begin{aligned}
4x_1 + 3x_2 + s_1 \phantom{+ s_2} &= 240\\
2x_1 + x_2 \phantom{+ s_1} + s_2 &= 100\\
x_1, x_2, s_1, s_2 &\ge 0
\end{aligned}$$

A $\ge$ constraint gets a **surplus** variable *subtracted* instead: $x_1 + x_2 \ge 10$ becomes $x_1 + x_2 - e = 10$ with $e \ge 0$.

### Basic solutions

There are now 4 variables and 2 equations. Pick any 2 variables to be **basic** — the ones you solve for — and set the other 2 (the **non-basic** ones) to zero. Each choice gives one basic solution.

With $n$ variables and $m$ equations there are at most $\binom{n}{m}$ choices. Here, $\binom{4}{2} = 6$:

| Basic variables | Set to zero | Solution $(x_1, x_2, s_1, s_2)$ | Feasible? | Corner |
|---|---|---|---|---|
| $s_1, s_2$ | $x_1, x_2$ | (0, 0, 240, 100) | yes | A |
| $x_1, s_1$ | $x_2, s_2$ | (50, 0, 40, 0) | yes | B |
| $x_1, s_2$ | $x_2, s_1$ | (60, 0, 0, −20) | **no** — finishing over by 20 | (60, 0) |
| $x_2, s_1$ | $x_1, s_2$ | (0, 100, −60, 0) | **no** — carpentry over by 60 | (0, 100) |
| $x_2, s_2$ | $x_1, s_1$ | (0, 80, 0, 20) | yes | D |
| $x_1, x_2$ | $s_1, s_2$ | (30, 40, 0, 0) | yes | C |

**The feasible basic solutions are exactly the four corners.** The two infeasible ones are where a constraint line crosses an axis *outside* the region. And notice that at each corner, the zero slacks name the binding constraints: at C both slacks are zero, so both resources are used up.

This table is the whole idea behind the simplex method. **A corner is a choice of which variables are basic.** Moving to a neighbouring corner means swapping one basic variable for one non-basic one.

### Why brute force fails

With 50 constraints and 100 variables (plus 50 slacks), the count is $\binom{150}{50} \approx 2 \times 10^{40}$. Even a computer checking a billion a second would need far longer than the age of the universe. So we need a method that only visits corners that improve the objective.

## Common pitfalls and traps

1. **Shading the wrong side.** Always test a point — the origin, if it isn't on the line — against the inequality.
2. **Missing a corner.** List every pair of boundary lines that meet on the region's edge, including the axes.
3. **Thinking "integer corner".** Corners are where lines meet, and that is usually at fractions. The workshop's integer corner is luck. If you need whole numbers, see note 07.
4. **Confusing "optimal edge" with "solver failure".** Multiple optima are a feature of the data, and useful: you can choose among equally good plans on other grounds.

## Check your understanding

1. Using the graph, what's the optimum if chair profit rises to ₦6,000 (table stays at ₦7,000)?
2. Why must the feasible region of an LP be convex? What would go wrong with the corner argument if it weren't?
3. In the basic-solutions table, what does it mean physically that $s_2 = -20$ at (60, 0)?
4. A three-variable LP has 4 constraints (all $\le$). How many variables does standard form have, and at most how many basic solutions are there?

<details>
<summary>After your attempt — answers</summary>

1. Profit line slope is $-7/6 \approx -1.17$, now flatter than carpentry's $-1.33$. The last corner touched becomes D. Check: A = 0, B = 350, C = 210 + 240 = 450, D = 480. Optimum D = (0, 80), all chairs, ₦480,000.
2. Each constraint is a half-plane, which is convex, and the overlap of convex sets is convex. If the region weren't convex, it could have a dent, and sliding along a segment towards a better point could leave the region; a local best corner might not be the global best.
3. Making 60 tables needs 120 finishing hours, and you only have 100. The slack would have to be −20 hours, i.e. you'd be 20 hours over. Negative slack means a broken constraint.
4. 3 original variables + 4 slacks = 7 variables and 4 equations. At most $\binom{7}{4} = 35$ basic solutions, of which some are infeasible.

</details>

## Practice — independent task

**Graph and solve:** $\max\; 3x + 2y$ subject to $x + y \le 8$, $x + 3y \le 12$, $x \le 7$, $x, y \ge 0$.

1. Draw the region on graph paper and label every corner with its coordinates.
2. Evaluate the objective at each corner and name the optimum and its binding constraints.
3. Change the objective to $\max\; 2x + 2y$ and explain what happens.

**Done when:** you have the optimum with its binding constraints, and you can explain part 3 using the word "parallel". Confirm part 2 with `linprog` from note 02 — only after doing it by hand.

<details>
<summary>Answer — after your attempt</summary>

Corners: (0, 0), (7, 0), (7, 1), (6, 2), (0, 4). Objective values: 0, 21, 23, 22, 8. Optimum $(7, 1)$, value 23, with $x + y \le 8$ and $x \le 7$ binding. With $2x + 2y$, the objective is parallel to $x + y \le 8$: the whole edge from (7, 1) to (6, 2) earns 16. Multiple optima.

</details>

## Before moving on

You're ready for the simplex method when you can, with the note closed, draw the workshop region, find all four corners, and explain why "all tables" loses — and when you can list the six basic solutions and say which are corners.

**Recap:**

1. The feasible region of an LP is convex, with straight edges.
2. If there's an optimum, one is at a corner. So only corners need checking.
3. Four outcomes: unique, multiple, infeasible, unbounded.
4. Algebraically, a corner is a feasible basic solution: choose which variables are basic, set the rest to zero, solve.

**Next:** [[operations-research/04-the-simplex-method|The Simplex Method]] — walking from corner to corner, uphill, in any number of dimensions.

## Related

- [[operations-research/02-formulating-linear-programs|Formulating Linear Programs]] — where the model came from
- [[operations-research/04-the-simplex-method|The Simplex Method]] — the next note
- [[mathematics/04-linear-algebra/index|Linear algebra]] — the equation-solving underneath basic solutions
- [[operations-research/index|Operations research map]]
