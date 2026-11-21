---
id: 92a6e212-e6c1-4d84-b40d-c8a93ef96c27
---

# The Simplex Method

**Source:** `[reference]` — see [[operations-research/index|the domain note]]. The code below was run and its output checked.

## Before you start
<!-- bite: 9eb51a81-16db-409e-9d19-6e7fa181351e -->

You need the algebra of corners: standard form, slack variables, and what a basic solution is → [[operations-research/03-the-geometry-of-linear-programs|note 03]]. You need to be able to do row operations on a set of equations (divide a row by a number, subtract a multiple of one row from another) → [[mathematics/04-linear-algebra/index|linear algebra]].

After this lesson you will be able to:

1. Run the simplex method by hand on a small LP in tableau form, explaining each pivot.
2. Read the optimal tableau: the solution, the objective value, and the shadow prices.
3. Recognise unboundedness, degeneracy and the need for a phase-one start.
4. Implement a working tableau simplex and test it.

**Study route:** sections 1–3, then **close the note** and redo the workshop tableau on paper. Then sections 4–6 and the code.

## The kid version
<!-- bite: f32bab18-ab2a-438a-8f7f-daa0d77f457e -->

You're on a big crystal, standing on one of its corners, and you want to reach the highest corner. You can't see the whole crystal — only the edges leaving the corner you're on. So you look at each edge, pick one that goes uphill, and walk along it to the next corner. Repeat. When every edge from where you stand goes downhill, you're at the top. **The simplex method is that walk, done with arithmetic instead of eyes.**

**Where the analogy stops working.** On a real bumpy rock, "no uphill edge" might just be a small peak. On an LP's region it's guaranteed to be the true top, because the region is convex and the objective is flat — there are no small peaks. That guarantee is why the simplex method can stop with certainty.

## 1. Why this exists
<!-- bite: 69b9e700-a615-4982-8a59-c9ccd5705a30 -->

Note 03 showed that the optimum is at a corner, and that there can be $10^{40}$ corners. George Dantzig's insight in 1947 was that you don't need to look at them all: **start at any corner, move to a better neighbour, repeat.** In practice the method visits a small multiple of the number of constraints — for a model with 1,000 constraints, typically a few thousand pivots, not $10^{40}$.

## Terms used in the simplex method
<!-- bite: fa00672d-ad8f-415e-b4a6-8fee94783eae -->

1. **Tableau**: This is a table holding the coefficients of the standard-form equations, plus a row for the objective. It's the simplex method's working surface.
2. **Basis**: This is the set of basic variables at the current corner — one per constraint. Changing the basis by one variable moves you to a neighbouring corner.
3. **Reduced cost**: This is the amount the objective would change per unit if you increased a non-basic variable from zero. In this note's tableau it sits in the objective row; a negative entry means increasing that variable would increase profit.
4. **Entering variable**: This is the non-basic variable chosen to increase from zero — the edge you'll walk along.
5. **Leaving variable**: This is the basic variable that hits zero first as the entering variable increases — the constraint you'll run into, which ends the walk at the next corner.
6. **Minimum ratio test**: This is the rule for choosing the leaving variable: divide each row's right-hand side by its (positive) entry in the entering column, and take the smallest.
7. **Pivot**: This is the row operation that makes the entering variable basic: scale its row so the pivot entry is 1, then subtract multiples of that row so every other entry in the column is 0.
8. **Degenerate**: A corner is degenerate when a basic variable equals zero. A pivot from it can leave you at the same point, which is how the method can stall.

## 2. The tableau
<!-- bite: 6ac185c5-aa5d-40fa-95c1-77153069e9f4 -->

Start from the workshop in standard form (from note 03), and write the objective as an equation too:

$$z - 7x_1 - 5x_2 = 0$$

Writing $-7$ and $-5$ is a convention: in this form, **a negative number in the objective row means "increasing this variable raises profit."**

The starting tableau puts the slacks in the basis. That's corner A: make nothing, every hour idle.

```text
 basis │  x1    x2    s1    s2  │  RHS
 ──────┼────────────────────────┼──────
  s1   │   4     3     1     0  │  240    carpentry
  s2   │   2     1     0     1  │  100    finishing
 ──────┼────────────────────────┼──────
  z    │  -7    -5     0     0  │    0    profit so far
```

Read it as: $s_1 = 240$, $s_2 = 100$, $x_1 = x_2 = 0$, profit 0.

## 3. The method, step by step
<!-- bite: e0a2be11-ad31-4fc1-8bd4-bba3ed840a50 -->

Each iteration has three steps: **choose who enters, choose who leaves, pivot.**

### Iteration 1

**Choose the entering variable.** Look at the objective row. $x_1$ has $-7$ and $x_2$ has $-5$. Both would raise profit; take the most negative, $x_1$ (Dantzig's rule — ₦7,000 per table beats ₦5,000 per chair *per unit*, though not necessarily per hour).

**Choose the leaving variable with the ratio test.** As $x_1$ rises from 0, how far can it go before a basic variable hits zero?

1. Carpentry row: $240 / 4 = 60$. At 60 tables, carpentry runs out.
2. Finishing row: $100 / 2 = 50$. At 50 tables, finishing runs out.

The smallest is 50, so **$s_2$ leaves**. Finishing is the constraint we hit first. (Taking 60 would give $s_2 = -20$ — the infeasible point (60, 0) from note 03.)

**Pivot on the 2** (row $s_2$, column $x_1$):

1. Divide the $s_2$ row by 2 → it becomes the $x_1$ row: `1  0.5  0  0.5 | 50`.
2. Carpentry row minus 4 × new $x_1$ row: `0  1  1  -2 | 40`.
3. Objective row plus 7 × new $x_1$ row: `0  -1.5  0  3.5 | 350`.

```text
 basis │  x1    x2    s1    s2  │  RHS
 ──────┼────────────────────────┼──────
  s1   │   0     1     1    -2  │   40
  x1   │   1   0.5     0   0.5  │   50
 ──────┼────────────────────────┼──────
  z    │   0  -1.5     0   3.5  │  350
```

**What changed:** we're at corner B, 50 tables, profit 350, with 40 carpentry hours idle ($s_1 = 40$). **What stayed true:** every right-hand side is non-negative, so we're still feasible. **Why the next step follows:** $x_2$ still has a negative reduced cost, $-1.5$, so making chairs would still raise profit.

**Pause and predict:** which variable leaves next?

### Iteration 2

**Entering:** $x_2$, the only negative entry ($-1.5$).

**Ratio test** on the $x_2$ column:

1. $s_1$ row: $40 / 1 = 40$.
2. $x_1$ row: $50 / 0.5 = 100$.

Smallest is 40, so **$s_1$ leaves** — carpentry becomes binding.

**Pivot on the 1** (row $s_1$, column $x_2$):

1. The $s_1$ row is already scaled; it becomes the $x_2$ row: `0  1  1  -2 | 40`.
2. $x_1$ row minus 0.5 × $x_2$ row: `1  0  -0.5  1.5 | 30`.
3. Objective row plus 1.5 × $x_2$ row: `0  0  1.5  0.5 | 410`.

```text
 basis │  x1    x2    s1    s2  │  RHS
 ──────┼────────────────────────┼──────
  x2   │   0     1     1    -2  │   40
  x1   │   1     0  -0.5   1.5  │   30
 ──────┼────────────────────────┼──────
  z    │   0     0   1.5   0.5  │  410
```

**No negative entries in the objective row. Stop: this is optimal.** 30 tables, 40 chairs, ₦410,000 — corner C, as the graph said. The walk was A → B → C, and corner D was never visited.

### Why stopping is safe

The objective row now says

$$z = 410 - 1.5\,s_1 - 0.5\,s_2$$

Since $s_1, s_2 \ge 0$, the only way to change $z$ is to make one of them positive, and that can only *lower* profit. No neighbouring corner is better, and because the region is convex, a corner with no better neighbour is the global optimum.

### Reading the final tableau

Three things fall out of the final tableau for free:

1. **The solution** is in the right-hand column against each basic variable.
2. **The objective value** is the bottom-right number.
3. **The shadow prices** are the objective-row entries under the slack columns: 1.5 for carpentry, 0.5 for finishing. That equation $z = 410 - 1.5s_1 - 0.5s_2$ says forcing one carpentry hour to stay idle costs ₦1,500. Equivalently, one *extra* carpentry hour would earn ₦1,500. These match the solver in note 02, and they're the subject of [[operations-research/05-duality-and-sensitivity|note 05]].

## 4. When things go differently
<!-- bite: c4103dfd-f3f8-4cfd-9382-ca446c5dcc46 -->

### Unbounded

If the entering column has **no positive entries**, the ratio test has nothing to divide. Increasing the entering variable never makes any basic variable hit zero, so you can increase it forever: the LP is unbounded. Stop and report it.

### Degeneracy and cycling

If the ratio test ties, the pivot leaves some basic variable at zero — a **degenerate** corner. The next pivot may then have a ratio of $0$, so you change basis without moving and without improving. In rare, specially constructed cases, the method can loop through the same bases forever. This is called **cycling**.

**Bland's rule** prevents cycling: always choose the *lowest-numbered* eligible entering variable, and break ratio ties by the lowest-numbered leaving variable. It's slower in practice but guaranteed to terminate. Real solvers use small random perturbations instead.

### No obvious starting corner

The tableau starts easily when every constraint is $\le$ with a non-negative right-hand side: the slacks form a ready-made basis at the origin. With $\ge$ or $=$ constraints, the origin isn't feasible and there's no obvious basis. Two standard fixes:

1. **Two-phase method.** Add an **artificial variable** to each awkward constraint, and first solve a different LP: *minimise the sum of the artificials*. If that minimum is 0, you've found a feasible corner, and phase two continues from there with the real objective. If it's above 0, the original LP is **infeasible** — so phase one doubles as the infeasibility test.
2. **Big-M method.** Put the artificials into the real objective with a huge penalty $M$, so the method drives them out on its own. Simpler to explain but numerically fragile, because $M$ has to be "big enough" and big numbers lose precision.

## 5. How fast is it?
<!-- bite: b03d0973-b211-4b2a-8be0-46c4d1b03b9a -->

**In practice, very fast.** The number of pivots is typically between $m$ and $3m$ for $m$ constraints, and modern solvers handle LPs with millions of variables.

**In theory, it can be exponential.** In 1972, Klee and Minty built a cube-shaped LP in $n$ dimensions where Dantzig's rule visits all $2^n$ corners. No pivot rule is known to be polynomial in the worst case. This gap between worst case and typical case is one of the famous puzzles of algorithms; *smoothed analysis* (Spielman and Teng, 2001) explains it by showing that tiny random perturbations of any input make the expected work polynomial.

**Interior-point methods** (Karmarkar, 1984) cut through the inside of the region instead of walking its edges, and are polynomial in the worst case. Modern solvers like HiGHS and Gurobi ship both and often race them. Simplex still wins when you need to *re-solve* after a small change, because it can restart from the old corner — which is exactly what integer programming does thousands of times (note 07).

Real solvers also don't store the full tableau. The **revised simplex method** keeps only the basis matrix in factored form, which is far faster and more stable on large sparse models.

## Worked example — a tableau simplex in Python
<!-- bite: b2503019-487c-4572-b354-1211fb839834 -->

**Runnable**, standard library only, Python 3.10+. It solves $\max\; c \cdot x$ subject to $Ax \le b$, $x \ge 0$, with $b \ge 0$ (so the slacks give a starting corner). It deliberately omits phase one, Bland's rule and numerical safeguards.

```python
# simplex.py — a teaching tableau simplex for max c.x s.t. Ax <= b, x >= 0, b >= 0
def simplex(c, A, b, verbose=True):
    m, n = len(A), len(c)
    # tableau rows: [A | I | b]; last row is the objective row [-c | 0 | 0]
    T = [list(map(float, A[i])) + [1.0 if j == i else 0.0 for j in range(m)] + [float(b[i])]
         for i in range(m)]
    T.append([-float(v) for v in c] + [0.0] * m + [0.0])
    basis = [n + i for i in range(m)]          # slacks start in the basis
    step = 0
    while True:
        z = T[-1]
        col = min(range(n + m), key=lambda j: z[j])   # most negative reduced cost
        if z[col] >= -1e-9:
            break                                  # nothing improves: optimal
        ratios = [(T[i][-1] / T[i][col], i) for i in range(m) if T[i][col] > 1e-9]
        if not ratios:
            raise ValueError("unbounded")
        _, row = min(ratios)                       # minimum ratio test
        step += 1
        if verbose:
            print(f"pivot {step}: column {col} enters, row {row} (basic var {basis[row]}) leaves")
        p = T[row][col]
        T[row] = [v / p for v in T[row]]
        for i in range(m + 1):
            if i != row and abs(T[i][col]) > 1e-12:
                f = T[i][col]
                T[i] = [a - f * r for a, r in zip(T[i], T[row])]
        basis[row] = col
    x = [0.0] * (n + m)
    for i, j in enumerate(basis):
        x[j] = T[i][-1]
    return x[:n], T[-1][-1], T[-1][n:n + m]

if __name__ == "__main__":
    x, z, duals = simplex([7, 5], [[4, 3], [2, 1]], [240, 100])
    print("x =", x, "z =", z, "shadow prices =", duals)
```

```bash
python3 simplex.py
```

Expected output — note the pivots match the hand trace (column 0 is $x_1$; variables 2 and 3 are $s_1$ and $s_2$):

```text
pivot 1: column 0 enters, row 1 (basic var 3) leaves
pivot 2: column 1 enters, row 0 (basic var 2) leaves
x = [30.0, 40.0] z = 410.0 shadow prices = [1.5, 0.5]
```

**What the code is doing:** `col` is the entering choice, `ratios` is the ratio test, and the two list comprehensions after it are the pivot. The `1e-9` tolerances exist because floating-point arithmetic doesn't give exact zeros; a real solver manages these tolerances far more carefully.

## Common pitfalls and traps
<!-- bite: c717b9fa-d4b6-40de-ba10-26a885df4180 -->

1. **Ratio test on non-positive entries.** Only rows with a *positive* entry in the entering column take part. A zero or negative entry means that basic variable doesn't fall as the entering one rises.
2. **Sign convention confusion.** This note writes the objective row as $z - c^\top x = 0$, so "negative means improve". Some textbooks use the opposite. Pick one and say which.
3. **Forgetting to update the objective row.** It gets pivoted like every other row. If it isn't, the stopping test is reading stale numbers.
4. **Assuming "most negative" is best.** Dantzig's rule picks the best rate *per unit*, not the biggest gain. Other rules (steepest edge) often need fewer pivots, and that's what real solvers use.

## Check your understanding
<!-- bite: 357a8eea-0618-4532-b502-682a549667fb -->

1. In iteration 1, what would the tableau represent if you had (wrongly) chosen $s_1$ to leave?
2. Why does a column with no positive entries mean unbounded, not infeasible?
3. In the final tableau, the $x_1$ row has $-0.5$ under $s_1$. What does that mean in workshop terms?
4. Why does phase one tell you whether an LP is infeasible?

<details>
<summary>After your attempt — answers</summary>

1. Corner (60, 0) with $s_2 = -20$ — finishing over-used by 20 hours. Infeasible. The ratio test exists to stop exactly this.
2. Increasing the entering variable never drives any basic variable to zero, so feasibility is never lost and profit keeps rising. You already have a feasible corner, so the region isn't empty.
3. Read the row as $x_1 = 30 + 0.5\,s_1 - 1.5\,s_2$. If you force one carpentry hour to sit idle ($s_1 = 1$), tables go *up* by 0.5 — because chairs, which use more carpentry per unit of profit, are cut back more. In the same way, an extra carpentry hour means 0.5 fewer tables (and one more chair).
4. Phase one minimises the total of the artificial variables, which measure how far from feasible you are. A minimum of 0 means some point satisfies every original constraint. A minimum above 0 means no point does.

</details>

## Practice — independent task
<!-- bite: 08e257d0-51fe-4589-ae24-7e82f02984a6 -->

1. **Predict, then run.** Use `simplex` on the paint problem from [[operations-research/02-formulating-linear-programs|note 02]]: `simplex([5, 4], [[6, 4], [1, 2], [-1, 1], [0, 1]], [24, 6, 1, 2])`. Before running, predict how many pivots it takes. Confirm the answer is $(3, 1.5)$ with profit 21.
2. **Modify.** Add a check: if `step` exceeds 1,000, raise `RuntimeError("possible cycling")`.
3. **Apply.** Implement Bland's rule as an option: `simplex(..., rule="bland")` chooses the lowest-index variable with a negative reduced cost, and breaks ratio ties by the lowest basis index.
4. **Test.** Write three tests: the workshop (410), an unbounded LP such as $\max\; x_1$ subject to $x_1 - x_2 \le 1$ (expect `ValueError`), and a degenerate LP where the ratio test ties: $\max\; x_1 + x_2$ subject to $x_1 \le 1$, $x_2 \le 1$, $x_1 + x_2 \le 2$.

**Done when:** all three tests pass under both rules, and you can explain why the degenerate test's ratio test ties.

## Before moving on
<!-- bite: 2ced867f-7956-4845-a9dc-15e501844aee -->

You're ready when you can run two simplex iterations on paper with the note closed, explaining "who enters, who leaves, and why" at each one, and read the shadow prices off the final tableau.

**Recap:**

1. Start at a corner (slacks basic). Enter the variable with a negative reduced cost. Leave by the minimum ratio. Pivot. Repeat until no reduced cost is negative.
2. Optimal is certain because the region is convex: no better neighbour means no better point.
3. Unbounded = no positive entry in the entering column. Degenerate = ties, possible stalling, fixed by Bland's rule.
4. Phase one finds a starting corner or proves infeasibility.
5. Exponential in the worst case, fast in practice; interior-point methods are the polynomial alternative.

**Next:** [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]] — those shadow prices, what they really mean, and how far you can trust them.

## Related
<!-- bite: 9d9cace6-adf4-4353-8b91-d1c4a6ca18fe -->

- [[operations-research/03-the-geometry-of-linear-programs|The Geometry of Linear Programs]] — the corners being walked
- [[operations-research/05-duality-and-sensitivity|Duality and Sensitivity]] — the next note
- [[theory-of-computation/07-complexity-classes|Complexity classes]] — where "polynomial in the worst case" is made precise
- [[operations-research/index|Operations research map]]

## About this lesson
<!-- bite: e69b1d26-c5db-49fc-82f8-0440e2c5777c -->

**Level:** Intermediate. **Covers:** The algorithm that made linear programming practical: walk from corner to neighbouring corner, always uphill, and stop when no neighbour is better. Traced by hand on the workshop, then implemented in sixty lines of Python.
