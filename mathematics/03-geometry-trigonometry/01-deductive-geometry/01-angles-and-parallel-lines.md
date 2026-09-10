# Angles and Parallel Lines

**[Beginner]** — how measuring *one* angle can tell you seven others exactly, and which single assumption makes that possible.

## Before you start

- You can solve a linear equation — [[01-linear-equations|linear equations]].
- You can substitute a value into an expression — [[02-variables|variables]].

**What you will be able to do after this lesson:**

1. Name every angle pair formed when a transversal crosses two parallel lines, and say which pairs are equal and which are supplementary.
2. *Derive* "vertically opposite angles are equal" rather than memorise it.
3. Carry out a multi-step angle chase, naming the rule that justifies each step.
4. State which fact about parallel lines is **assumed** rather than proved, and say what breaks without it.

**Study route:** read sections 1–4, attempt the prediction in section 5 before reading on, then run the lab and do the practice task.

---

## 1. Why this exists

A roof truss is being built from two parallel beams with a diagonal brace across them. The builder needs all eight angles where the brace meets the beams — to cut the timber, every angle must be exact.

The obvious approach is to measure all eight with a protractor. That fails for three reasons:

- **Error accumulates.** A protractor is good to about half a degree. Eight independent measurements give eight independent errors, and the cuts stop fitting.
- **You cannot measure what does not exist yet.** The truss is a drawing. There is nothing to put a protractor against.
- **Measurement never proves anything.** Reading 65° tells you the angle is *near* 65°. It cannot tell you it is *exactly* 65°, and it cannot tell you the same will hold for the next truss.

Deductive geometry replaces measurement with inference. Measure **one** angle — or choose it, since it is your drawing — and the other seven follow exactly, with no error and no protractor.

That is the whole trade: a small number of assumptions, and everything else derived from them.

## 2. Terminology

| Term | Plain-English definition | Example |
| :--- | :--- | :--- |
| **Angle** | The amount of turn between two rays meeting at a point | A quarter turn is $90°$ |
| **Vertex** | The point where the two rays meet | The corner of the angle |
| **Acute / right / obtuse / reflex** | Less than $90°$ / exactly $90°$ / between $90°$ and $180°$ / more than $180°$ | $30°$ / $90°$ / $120°$ / $200°$ |
| **Complementary** | Two angles adding to $90°$ | $30°$ and $60°$ |
| **Supplementary** | Two angles adding to $180°$ | $115°$ and $65°$ |
| **Linear pair** | Two adjacent angles on a straight line — always supplementary | The two angles either side of a fence post leaning on a wall |
| **Vertically opposite** | The two angles facing each other where two lines cross | The "bow-tie" pair in an X |
| **Transversal** | A line that crosses two or more other lines | The diagonal brace across two beams |
| **Interior / exterior** | Between the two crossed lines / outside them | The brace angles inside the truss / outside it |

Note that **vertically** here has nothing to do with up and down. It comes from *vertex*: the angles share a vertex and face away from each other.

## 3. The two facts everything rests on

Everything in this lesson is built from two statements:

**Fact 1 — angles on a straight line sum to $180°$.**
A straight line is a half turn, and a half turn is $180°$ by definition of the degree.

**Fact 2 — angles at a point sum to $360°$.**
A full turn. Same definition, applied once round instead of halfway.

From those two alone, a result follows that most people memorise instead of deriving.

### Vertically opposite angles are equal

Two straight lines cross at a point. Four angles appear:

```
          b
       \     /
     a  \   /  c
    ------X------
        /   \
       /  d  \
```

$a$ and $b$ sit on a straight line, so by Fact 1:

$$
a + b = 180°
$$

$b$ and $c$ also sit on a straight line, so:

$$
b + c = 180°
$$

Both expressions equal $180°$, so they equal each other:

$$
a + b = b + c
$$

Subtract $b$ from both sides:

$$
a = c
$$

That is the whole proof. It is worth noticing what it did **not** use: nothing about the size of the angles, nothing about how steeply the lines cross, no measurement. The result holds for every pair of crossing lines that ever will be drawn.

> [!NOTE]
> This is the shape of every proof in deductive geometry: take facts you have already accepted, apply them to the figure in front of you, and combine them with ordinary algebra. If you can do [[01-linear-equations|linear equations]], you can already do the algebra half.

## 4. A transversal across two parallel lines

Now add the second beam. Two parallel lines, $L_1$ and $L_2$, both crossed by a transversal. Eight angles appear, four at each crossing:

```
                    /   transversal
          a1       /       a2
   L1 -----------+-------------
          a3     /         a4
                /
          a5   /           a6
   L2 ---------+---------------
          a7  /             a8
             /
```

Three new named pairs matter:

| Pair name | Which angles | Relationship | How to spot it |
| :--- | :--- | :--- | :--- |
| **Corresponding** | $a_1$ and $a_5$ | **Equal** | Same position at each crossing — an **F** shape |
| **Alternate interior** | $a_4$ and $a_5$ | **Equal** | Inside, opposite sides — a **Z** shape |
| **Co-interior** (allied) | $a_3$ and $a_5$ | **Supplementary** | Inside, same side — a **C** shape |

The F, Z and C shapes are a genuinely useful way to find the pair in a cluttered diagram, but they are a *search technique*, not a reason. The reason is below.

### Which of these is assumed?

Here is the part usually skipped. **Corresponding angles being equal is not proved — it is assumed.** It is logically equivalent to Euclid's fifth postulate, the parallel postulate, and two thousand years of attempts to derive it from the other axioms all failed. In the nineteenth century mathematicians discovered why: it cannot be derived, because consistent geometries exist in which it is false.

Once corresponding angles are granted, the other two follow immediately:

- **Alternate interior.** $a_1 = a_5$ (corresponding, assumed). $a_1 = a_4$ (vertically opposite, proved in section 3). Therefore $a_4 = a_5$.
- **Co-interior.** $a_3 + a_1 = 180°$ (linear pair on $L_1$). $a_1 = a_5$ (corresponding). Substituting, $a_3 + a_5 = 180°$.

So of the three rules, one is an assumption and two are consequences. Knowing which is which is the difference between doing geometry and reciting it.

### What fails without parallel lines

If $L_1$ and $L_2$ are **not** parallel, Facts 1 and 2 still hold — they say nothing about parallelism. So linear pairs still sum to $180°$ and vertically opposite angles are still equal, at each crossing separately.

What is lost is every rule connecting the two crossings. Corresponding angles are no longer equal, alternate angles are no longer equal, co-interior angles no longer sum to $180°$. The lab below demonstrates exactly this.

## 5. Worked example — the full angle chase

Take $a_1 = 115°$ and $L_1 \parallel L_2$. Work out all eight, naming the reason at each step.

| Angle | Value | Reason |
| :--- | :--- | :--- |
| $a_1$ | $115°$ | Given |
| $a_2$ | $65°$ | Linear pair with $a_1$ along $L_1$: $180 - 115$ |
| $a_3$ | $65°$ | Linear pair with $a_1$ along the transversal |
| $a_4$ | $115°$ | Vertically opposite $a_1$ |
| $a_5$ | $115°$ | Corresponds to $a_1$ |
| $a_6$ | $65°$ | Corresponds to $a_2$ |
| $a_7$ | $65°$ | Corresponds to $a_3$ |
| $a_8$ | $115°$ | Corresponds to $a_4$ |

> [!TIP]
> **Predict before reading on.** Only two distinct values appear in that table, $115°$ and $65°$. Before continuing — is that a coincidence of the number chosen, or must it happen for every starting angle? Decide, then check your reasoning against the answer at the end of *Check your understanding*.

## Worked example — runnable

**Runnable example:** save as `angle_chase.py` in any empty directory and run `python3 angle_chase.py`. It uses only the standard library and writes no files.

```python
"""Angle chase across a transversal, with every theorem checked.

                    /   transversal
          a1       /       a2
   L1 -----------+-------------
          a3     /         a4
                /
          a5   /           a6
   L2 ---------+---------------
          a7  /             a8
             /
"""


def crossing(angle_at_upper_left):
    """The four angles where one line meets the transversal.

    Only Fact 1 (straight line = 180) and the vertical-angle result are
    used here, so this is valid whether or not any lines are parallel.
    """
    x = angle_at_upper_left
    return {
        "upper_left": x,
        "upper_right": 180 - x,   # linear pair with upper_left
        "lower_left": 180 - x,    # linear pair with upper_left
        "lower_right": x,         # vertically opposite upper_left
    }


def figure(a1, a5=None):
    """Label all eight angles.

    a1 fixes the first crossing. If a5 is None the lines are parallel, so
    a5 = a1 by the corresponding-angles assumption. Passing an explicit a5
    models two lines that are NOT parallel.
    """
    top = crossing(a1)
    bottom = crossing(a1 if a5 is None else a5)
    return {
        "a1": top["upper_left"],    "a2": top["upper_right"],
        "a3": top["lower_left"],    "a4": top["lower_right"],
        "a5": bottom["upper_left"], "a6": bottom["upper_right"],
        "a7": bottom["lower_left"], "a8": bottom["lower_right"],
    }


LINEAR_PAIRS = [("a1", "a2"), ("a3", "a4"), ("a1", "a3"), ("a2", "a4"),
                ("a5", "a6"), ("a7", "a8"), ("a5", "a7"), ("a6", "a8")]
VERTICAL_PAIRS = [("a1", "a4"), ("a2", "a3"), ("a5", "a8"), ("a6", "a7")]
CORRESPONDING = [("a1", "a5"), ("a2", "a6"), ("a3", "a7"), ("a4", "a8")]
ALTERNATE_INTERIOR = [("a3", "a6"), ("a4", "a5")]
CO_INTERIOR = [("a3", "a5"), ("a4", "a6")]


def holds(f, pairs, rule):
    """Report whether a rule holds for every pair it claims to cover."""
    return all(rule(f[p], f[q]) for p, q in pairs)


equal = lambda p, q: p == q
supplementary = lambda p, q: p + q == 180


def report(title, f):
    print(title)
    print("  " + "  ".join(f"{k}={v}" for k, v in f.items()))
    print(f"  linear pairs supplementary : {holds(f, LINEAR_PAIRS, supplementary)}")
    print(f"  vertically opposite equal  : {holds(f, VERTICAL_PAIRS, equal)}")
    print(f"  corresponding equal        : {holds(f, CORRESPONDING, equal)}")
    print(f"  alternate interior equal   : {holds(f, ALTERNATE_INTERIOR, equal)}")
    print(f"  co-interior supplementary  : {holds(f, CO_INTERIOR, supplementary)}")


if __name__ == "__main__":
    parallel = figure(115)
    report("Parallel lines, a1 = 115 degrees:", parallel)

    # The two facts that never mention parallelism must survive.
    assert holds(parallel, LINEAR_PAIRS, supplementary)
    assert holds(parallel, VERTICAL_PAIRS, equal)
    # With parallel lines, only two distinct values can appear.
    assert set(parallel.values()) == {115, 65}, parallel

    print()
    skew = figure(115, a5=100)          # second line tilted by 15 degrees
    report("NOT parallel, a1 = 115 and a5 = 100:", skew)

    # Same two facts still hold - they are about one crossing at a time.
    assert holds(skew, LINEAR_PAIRS, supplementary)
    assert holds(skew, VERTICAL_PAIRS, equal)
    # Everything that linked the two crossings is now false.
    assert not holds(skew, CORRESPONDING, equal)
    assert not holds(skew, ALTERNATE_INTERIOR, equal)
    assert not holds(skew, CO_INTERIOR, supplementary)

    print()
    print("angle_chase: passed")
```

Expected output:

```
Parallel lines, a1 = 115 degrees:
  a1=115  a2=65  a3=65  a4=115  a5=115  a6=65  a7=65  a8=115
  linear pairs supplementary : True
  vertically opposite equal  : True
  corresponding equal        : True
  alternate interior equal   : True
  co-interior supplementary  : True

NOT parallel, a1 = 115 and a5 = 100:
  a1=115  a2=65  a3=65  a4=115  a5=100  a6=80  a7=80  a8=100
  linear pairs supplementary : True
  vertically opposite equal  : True
  corresponding equal        : False
  alternate interior equal   : False
  co-interior supplementary  : False

angle_chase: passed
```

The second block is the point of the lab. The rules that survive are exactly the ones whose derivation never mentioned parallel lines.

## Common pitfalls and traps

- **Reading parallelism off the picture.** Two lines drawn *nearly* parallel look parallel. Corresponding angles are equal only when the lines are *stated* to be parallel — usually by arrow marks in the diagram or a line of text. If nothing says so, you may not use those three rules.
- **Confusing alternate with co-interior.** Both pairs are interior. Alternate are on *opposite* sides of the transversal and are **equal**; co-interior are on the *same* side and are **supplementary**. Getting these backwards turns a $65°$ into a $115°$, and the error survives to the end of the chase.
- **Assuming "looks equal" means equal.** Diagrams in textbooks are not to scale, and diagrams in exams are deliberately not to scale. The only equalities you may use are ones a rule gives you.
- **Losing the reason.** Writing $a_5 = 115°$ with no justification earns nothing in an exam and, more importantly, means you cannot check your own work. Each line should name its rule.
- **Applying a rule across a figure that has two different transversals.** Corresponding angles correspond *with respect to a particular transversal*. In a diagram with several crossing lines, say which transversal you are using.

## Check your understanding

1. Two lines cross. One of the four angles is $37°$. What are the other three, and which rule gives each?
2. A transversal crosses two parallel lines. One co-interior pair is $(3x)°$ and $(x + 20)°$. Find $x$.
3. In an angle chase you deduce that a co-interior pair are **equal**. What does that tell you about the transversal?
4. Someone claims "alternate angles are always equal". Correct the statement.
5. The lab's `crossing()` function is used for both the parallel and the non-parallel figure without change. Why is that legitimate?

<details><summary>Answers — open only after an attempt</summary>

1. The vertically opposite angle is $37°$. The other two are $180 - 37 = 143°$ each, by linear pair; they are also vertically opposite each other, which is a useful consistency check.
2. Co-interior angles are supplementary, so $3x + x + 20 = 180$, giving $4x = 160$ and $x = 40$. The angles are $120°$ and $60°$ — supplementary, as required.
3. Co-interior angles sum to $180°$, and if they are also equal each must be $90°$. So the transversal is **perpendicular** to both lines.
4. Alternate angles are equal **only when the two lines cut by the transversal are parallel**. Without that condition the statement is false, as the lab's second figure shows.
5. Because `crossing()` uses only Fact 1 and the vertical-angle result, neither of which mentions a second line. Those results are local to a single crossing, so they hold regardless of what the other line is doing.

**And the prediction from section 5:** it is not a coincidence. Every angle in the figure is either $a_1$ or its supplement, because each rule either preserves the value or replaces it by $180 - a_1$. So exactly two distinct values appear — unless $a_1 = 90°$, when the two coincide and all eight angles are $90°$.
</details>

## Practice — independent task

A transversal crosses two parallel lines $L_1$ and $L_2$. A **second** transversal also crosses both, and the two transversals meet at a point $M$ below $L_2$, forming a triangle with $L_2$.

Given that the first transversal makes an angle of $70°$ with $L_1$ (measured as $a_1$, upper left), and the second makes $50°$ with $L_1$ in the corresponding position:

1. Find the three angles of the triangle formed by $L_2$ and the two transversals.
2. Justify each with a named rule — no step may rest on "from the diagram".
3. Extend the lab: write `triangle_from_transversals(t1, t2)` returning the three angles, and assert that they sum to $180°$.
4. Then assert something stronger: that the angle at $M$ equals the **difference** of the two transversal angles. Explain why that must be so.

**Done when:** your three angles sum to $180°$, your assertion in step 4 passes for at least four different pairs of input angles, and you can state which rule each of your three answers came from without looking back at this lesson.

If you want to check your reasoning against the general result first, note that step 4 is the exterior angle theorem in disguise — it is proved in [[02-triangles-and-polygons|triangles and polygons]].

## Tradeoffs, limits and extensions

**The parallel postulate is a choice, not a truth.** Everything above lives in Euclidean geometry — the geometry of a flat plane. Replace the parallel postulate with a different assumption and you get a different, equally consistent geometry:

- On a **sphere**, "lines" are great circles, and any two of them meet. There are no parallel lines at all, and the angles of a triangle sum to *more* than $180°$. This is not a curiosity: it is the geometry navigation actually uses, and it is why [[01-latitude-and-longitude|latitude and longitude]] calculations do not look like the ones here.
- On a **saddle-shaped** surface, many lines through a point never meet a given line, and triangle angles sum to less than $180°$.

Neither is wrong. They answer a different question about a different surface. Euclidean geometry is the right model for a roof truss and the wrong model for a flight path.

**Where the flat model still fails in practice.** Real beams are not lines and real joints have width. Deduction gives the exact angle for an idealised figure; the carpenter still needs a tolerance. Knowing that the mathematics is exact and the timber is not is part of using it well.

## Before moving on

You are done with this lesson when you can:

- Derive the vertical-angle result from Fact 1 without looking it up.
- Complete an eight-angle chase, naming a rule on every line.
- Say which of the three parallel-line rules is an assumption, and what happens to each rule when the lines are not parallel.

**Recap for later lookup:** angles on a line sum to $180°$; angles at a point sum to $360°$; vertically opposite angles are equal (derived). Across a transversal cutting **parallel** lines: corresponding equal (assumed), alternate interior equal, co-interior supplementary.

**Next:** [[02-triangles-and-polygons|Triangles and Polygons]] — the angle sum of a triangle is proved by drawing one extra parallel line, which is why parallels came first.

## Related

- [[01-linear-equations|Linear Equations]] — the algebra every angle chase reduces to
- [[01-circle-theorems|Circle Theorems]] — the same deductive method applied to circles
- [[01-ratios-and-right-triangles|Trigonometric Ratios]] — what to do when you need side *lengths*, not just angles
- [[COURSE-STANDARD|Course standard]] — the teaching shape this lesson follows
