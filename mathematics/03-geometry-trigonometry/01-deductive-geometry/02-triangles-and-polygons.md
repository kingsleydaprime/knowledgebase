# Triangles and Polygons

**[Beginner]** — why every triangle's angles sum to exactly $180°$, and what it takes to prove two shapes are *the same* shape.

## Before you start

- You can chase angles across a transversal — [[01-angles-and-parallel-lines|angles and parallel lines]]. The proof in section 3 depends on the alternate-angle rule, which is why parallels came first.
- You can solve a linear equation — [[01-linear-equations|linear equations]].

**What you will be able to do after this lesson:**

1. Prove the angle sum of a triangle, and extend the proof to any polygon.
2. State the exterior angle theorem and use it to skip a step in an angle chase.
3. Choose the right congruence criterion (SSS, SAS, ASA, AAS, RHS) for a given pair of triangles, and explain why **SSA is not one of them**.
4. Distinguish congruence from similarity, and use similarity to find an unknown length.

**Study route:** read 1–5, attempt the prediction in section 6 before reading past it, then run the lab — its third block is the one worth your attention.

---

## 1. Why this exists

You are given two triangular brackets and asked whether they are interchangeable. Measuring all six quantities of each — three sides and three angles — and comparing them works, but it is six measurements per bracket where the answer might need only three.

Worse, some sets of three measurements are **not enough**, and it is not obvious which. Two triangles can agree on two sides and an angle and still be different triangles. If you pick the wrong three, you will confidently declare two different brackets identical.

This lesson is about which minimal sets of facts pin a triangle down completely, and which leave room for a second, different answer.

## 2. Terminology

| Term | Plain-English definition | Example |
| :--- | :--- | :--- |
| **Vertex** (plural *vertices*) | A corner of a shape | A triangle has three |
| **Interior angle** | The angle inside the shape at a vertex | The $60°$ of an equilateral triangle |
| **Exterior angle** | The angle between one side and the *extension* of the next | Its interior angle's supplement |
| **Scalene / isosceles / equilateral** | All sides different / two sides equal / all three equal | — |
| **Congruent** | Same shape **and** same size — one can be laid exactly on the other | Two copies of the same bracket |
| **Similar** | Same shape, possibly different size — all angles equal, all sides in one ratio | A photo and its enlargement |
| **Included angle** | The angle *between* two named sides | In "SAS", the A sits between the two S's |
| **Convex polygon** | A polygon with no interior angle over $180°$ | A regular hexagon |

The distinction between **congruent** and **similar** carries most of the weight in this lesson. Congruent triangles are interchangeable brackets. Similar triangles are a bracket and a scale drawing of it.

## 3. The angle sum of a triangle

**Claim:** the three interior angles of any triangle sum to $180°$.

The proof needs one construction: through the apex, draw a line **parallel** to the base.

```
        x  \  a  /  y
     -------+-------      <- line through the apex, parallel to the base
             \ /
            / a \
           /     \
          /       \
      ---+---------+---   <- base
         x         y
```

Let the triangle's angles be $a$ at the apex, $x$ at the left base vertex, $y$ at the right.

The two sides of the triangle act as transversals across a pair of parallel lines, so:

- The angle marked $x$ at the apex equals the base angle $x$ — **alternate interior angles**, using the left side as transversal.
- The angle marked $y$ at the apex equals the base angle $y$ — alternate interior angles, using the right side as transversal.

The three angles at the apex sit on a straight line, so by Fact 1 of the previous lesson:

$$
x + a + y = 180°
$$

And those are exactly the triangle's three angles. $\blacksquare$

Notice the dependency: **the angle sum of a triangle is a consequence of the parallel postulate.** Drop that postulate and the result goes with it — on a sphere the sum exceeds $180°$, which is not a rounding error but a different geometry.

### The exterior angle theorem

Extend one side of the triangle. The exterior angle $e$ at that vertex and the interior angle $c$ form a linear pair:

$$
e + c = 180°
$$

And from the angle sum, $a + b + c = 180°$. Both equal $180°$, so:

$$
e + c = a + b + c \quad\Longrightarrow\quad e = a + b
$$

**An exterior angle equals the sum of the two opposite interior angles.** This is worth memorising precisely because it *skips* a step: without it you would compute $c$ first, then subtract from $180°$.

### Isosceles triangles

If two sides are equal, the angles opposite them are equal — and conversely. The proof drops a line from the apex to the midpoint of the base, splitting the triangle into two triangles with three pairs of equal sides, and then applies SSS from section 4.

The converse matters as much as the theorem: showing two angles equal is often the easiest route to showing two *sides* equal.

## 4. Congruence — which three facts are enough

Two triangles are congruent when one can be picked up and placed exactly on the other. Six quantities describe a triangle, but three of the right kind suffice:

| Criterion | What you must show | Why it pins the triangle down |
| :--- | :--- | :--- |
| **SSS** | Three pairs of equal sides | Three side lengths admit exactly one triangle shape |
| **SAS** | Two sides and the **included** angle | Fix two sides and the angle between them; the third side has no freedom |
| **ASA** | Two angles and the included side | Two angles fix the third (angle sum), then the side sets the scale |
| **AAS** | Two angles and a **non**-included side | Same as ASA once the third angle is deduced |
| **RHS** | Right angle, hypotenuse, one other side | Pythagoras determines the remaining side, reducing it to SSS |

### Why SSA is not on the list

Suppose you know two sides and an angle that is **not** between them. Place the known angle $A$ at a vertex and lay side $b$ along one arm. Now swing side $a$ down from the far end of $b$ to meet the other arm. If $a$ is short enough, the swinging side crosses that arm in **two different places** — giving two genuinely different triangles from the same three facts.

This is called the **ambiguous case**, and it is not a technicality. Block 3 of the lab constructs both triangles explicitly from the data $A = 30°$, $a = 5$, $b = 8$: same angle, same two sides, two different third sides and two different remaining angles.

RHS escapes the ambiguity because a right angle is the largest angle a triangle may have besides the obtuse one, and the hypotenuse is forced to be the longest side — which rules the second solution out.

## 5. Similarity

Similar triangles have equal angles and proportional sides. Because the angle sum fixes the third angle, **two** equal angles are enough:

- **AA** — two pairs of equal angles.
- **SAS (similarity)** — two pairs of sides in the same ratio, with equal included angles.
- **SSS (similarity)** — all three pairs of sides in the same ratio.

The payoff is measuring the unreachable. A stick of known height casts a known shadow; a tower casts a measurable shadow at the same moment. The sun's rays are effectively parallel, so the two triangles have equal angles, so:

$$
\frac{\text{tower height}}{\text{tower shadow}} = \frac{\text{stick height}}{\text{stick shadow}}
$$

One unknown, one equation. This is how the height of the Great Pyramid was first estimated, and it is the same idea a camera uses to turn image size into distance.

## 6. Polygons

Cut a convex polygon with $n$ sides into triangles by joining one vertex to every other non-adjacent vertex. You always get $n - 2$ triangles, so:

$$
\text{interior angle sum} = (n-2) \times 180°
$$

For the exterior angles, each interior angle $i_k$ has exterior angle $180° - i_k$, so:

$$
\sum_{k=1}^{n} (180° - i_k) = 180n - (n-2)180 = 360°
$$

**The exterior angles of any convex polygon sum to $360°$, whatever $n$ is.** Walking once round the outline turns you through one full revolution — which is the same statement without the algebra.

> [!TIP]
> **Predict before running the lab.** A regular polygon has all angles equal, so each exterior angle is $360°/n$. As $n$ grows, what happens to the interior angle — and what shape is the polygon approaching? Decide before opening the answers.

## Worked example — runnable

**Runnable example:** save as `triangles.py` in any empty directory and run `python3 triangles.py`. Standard library only; writes no files.

```python
"""Triangle facts, checked numerically from coordinates.

Block 1: angle sum of a triangle, computed from vertices.
Block 2: the exterior angle theorem.
Block 3: the SSA ambiguous case - two different triangles, same three facts.
Block 4: polygon angle sums.
"""
import math

Point = tuple  # (x, y)


def angle_at(vertex, p, q):
    """Interior angle at `vertex` in the triangle vertex-p-q, in degrees."""
    (vx, vy), (px, py), (qx, qy) = vertex, p, q
    u = (px - vx, py - vy)
    w = (qx - vx, qy - vy)
    dot = u[0] * w[0] + u[1] * w[1]
    mag = math.hypot(*u) * math.hypot(*w)
    # clamp guards against a dot/mag of 1.0000000002 from rounding
    return math.degrees(math.acos(max(-1.0, min(1.0, dot / mag))))


def triangle_angles(a, b, c):
    return (angle_at(a, b, c), angle_at(b, a, c), angle_at(c, a, b))


def solve_ssa(angle_A_deg, a, b):
    """Every triangle with angle A, opposite side a, and adjacent side b.

    The sine rule gives sin(B) = b*sin(A)/a. If that value is below 1 there
    are two candidate angles B - one acute, one obtuse - and each is a real
    triangle whenever A + B < 180.
    """
    sin_B = b * math.sin(math.radians(angle_A_deg)) / a
    if sin_B > 1:
        return []                      # side a too short to reach: no triangle
    B_acute = math.degrees(math.asin(sin_B))
    solutions = []
    for B in (B_acute, 180 - B_acute):
        C = 180 - angle_A_deg - B
        if C > 1e-9:                   # a real triangle needs a positive third angle
            c = a * math.sin(math.radians(C)) / math.sin(math.radians(angle_A_deg))
            solutions.append({"B": B, "C": C, "c": c})
    return solutions


if __name__ == "__main__":
    print("Block 1 - angle sum from coordinates")
    for tri in [((0, 0), (4, 0), (1, 3)),
                ((0, 0), (5, 0), (5, 12)),
                ((-2, -1), (3, 0), (0, 4))]:
        angs = triangle_angles(*tri)
        total = sum(angs)
        print(f"  {tri} -> " + ", ".join(f"{a:.2f}" for a in angs) + f"  sum={total:.6f}")
        assert abs(total - 180) < 1e-9, total

    print()
    print("Block 2 - exterior angle theorem")
    tri = ((0, 0), (5, 0), (5, 12))
    A, B, C = triangle_angles(*tri)
    exterior_at_C = 180 - C
    print(f"  interior angles: A={A:.2f} B={B:.2f} C={C:.2f}")
    print(f"  exterior at C = {exterior_at_C:.2f}, A + B = {A + B:.2f}")
    assert abs(exterior_at_C - (A + B)) < 1e-9

    print()
    print("Block 3 - SSA: two triangles from the same three facts")
    solutions = solve_ssa(angle_A_deg=30, a=5, b=8)
    print(f"  given A=30 deg, a=5, b=8  ->  {len(solutions)} distinct triangles")
    for n, s in enumerate(solutions, 1):
        print(f"    triangle {n}: B={s['B']:.4f}  C={s['C']:.4f}  c={s['c']:.4f}")
    assert len(solutions) == 2, "SSA should be ambiguous here"
    assert abs(solutions[0]["c"] - solutions[1]["c"]) > 1, "the two must differ"

    # RHS is not ambiguous: with A = 90 the obtuse branch cannot exist.
    right_angled = solve_ssa(angle_A_deg=90, a=13, b=5)
    print(f"  given A=90 deg, a=13, b=5 ->  {len(right_angled)} triangle (RHS is safe)")
    assert len(right_angled) == 1

    print()
    print("Block 4 - polygon angle sums")
    for n in range(3, 9):
        interior = (n - 2) * 180
        each = interior / n
        print(f"  n={n}: interior sum={interior:5}  each={each:6.2f}  exterior each={360/n:6.2f}")
        assert abs(n * (180 - each) - 360) < 1e-9

    print()
    print("triangles: passed")
```

Expected output:

```
Block 1 - angle sum from coordinates
  ((0, 0), (4, 0), (1, 3)) -> 71.57, 45.00, 63.43  sum=180.000000
  ((0, 0), (5, 0), (5, 12)) -> 67.38, 90.00, 22.62  sum=180.000000
  ((-2, -1), (3, 0), (0, 4)) -> 56.89, 64.44, 58.67  sum=180.000000

Block 2 - exterior angle theorem
  interior angles: A=67.38 B=90.00 C=22.62
  exterior at C = 157.38, A + B = 157.38

Block 3 - SSA: two triangles from the same three facts
  given A=30 deg, a=5, b=8  ->  2 distinct triangles
    triangle 1: B=53.1301  C=96.8699  c=9.9282
    triangle 2: B=126.8699  C=23.1301  c=3.9282
  given A=90 deg, a=13, b=5 ->  1 triangle (RHS is safe)

Block 4 - polygon angle sums
  n=3: interior sum=  180  each= 60.00  exterior each=120.00
  n=4: interior sum=  360  each= 90.00  exterior each= 90.00
  n=5: interior sum=  540  each=108.00  exterior each= 72.00
  n=6: interior sum=  720  each=120.00  exterior each= 60.00
  n=7: interior sum=  900  each=128.57  exterior each= 51.43
  n=8: interior sum= 1080  each=135.00  exterior each= 45.00

triangles: passed
```

Block 3 is the one to study. Both triangles satisfy $A = 30°$, $a = 5$, $b = 8$ exactly. They are not the same triangle. That is why SSA is absent from the congruence list.

## Common pitfalls and traps

- **Using SSA as though it were a congruence rule.** It is the single most common false proof in school geometry. If the angle you know is not between the two sides you know, you may have two triangles.
- **Assuming the included angle.** "SAS" requires the angle *between* the two sides. Two sides and some other angle is SSA in disguise.
- **Confusing congruent with similar.** Similar triangles have equal angles; that says nothing about size. Writing $AB = PQ$ when you have only proved similarity is a real error, not a slip of notation.
- **Applying $(n-2)\times180°$ to a non-convex polygon without care.** The formula still holds for simple polygons, but the triangulation argument as stated assumes every diagonal from the chosen vertex stays inside — which fails for a re-entrant vertex. Choose a vertex from which it does.
- **Believing the angle sum is a fact about triangles.** It is a fact about triangles *in a flat plane*. It is the parallel postulate wearing a different hat.
- **Trusting a numerically checked angle sum to prove the theorem.** The lab confirms the arithmetic is consistent for the cases tried. The proof in section 3 is what establishes it for all triangles.

## Check your understanding

1. A triangle has angles $(2x)°$, $(3x)°$ and $(4x)°$. Find them.
2. An exterior angle of a triangle is $110°$, and one opposite interior angle is $45°$. Find all three interior angles.
3. Two triangles have $AB = PQ$, $BC = QR$ and $\angle A = \angle P$. Are they necessarily congruent?
4. A regular polygon has an interior angle of $156°$. How many sides has it?
5. Why does RHS avoid the ambiguity that sinks SSA, even though it also names two sides and a non-included angle?

<details><summary>Answers — open only after an attempt</summary>

1. $2x + 3x + 4x = 180$, so $9x = 180$ and $x = 20$. The angles are $40°$, $60°$, $80°$.
2. By the exterior angle theorem, $110 = 45 + b$, so the other opposite interior angle is $65°$. The third angle is the one adjacent to the exterior angle: $180 - 110 = 70°$. Check: $45 + 65 + 70 = 180$. ✓
3. **No.** $\angle A$ is not included between $AB$ and $BC$ — the included angle would be $\angle B$. This is SSA, and it may admit two triangles.
4. Each exterior angle is $180 - 156 = 24°$. Exterior angles sum to $360°$, so $n = 360/24 = 15$ sides.
5. Because the right angle is opposite the hypotenuse, which must be the longest side. The obtuse branch of the sine-rule solution would require a second angle above $90°$, giving a triangle with two angles of at least $90°$ — impossible. The lab's `solve_ssa(90, 13, 5)` returns exactly one triangle for this reason.

**And the prediction from section 6:** each exterior angle is $360°/n$, which tends to $0$ as $n$ grows, so each interior angle tends to $180°$. The polygon is approaching a **circle** — and this is the idea behind computing a circle's area as the limit of inscribed polygons.
</details>

## Practice — independent task

Implement `classify_triangle(a, b, c)` taking three side lengths and returning a dictionary describing the triangle.

Requirements:

1. Reject impossible triangles using the **triangle inequality**: each side must be shorter than the sum of the other two. Return `None` for those.
2. Classify by sides: `"equilateral"`, `"isosceles"` or `"scalene"`.
3. Classify by angles: `"right"`, `"acute"` or `"obtuse"`, using the sign of $a^2 + b^2 - c^2$ for the longest side $c$ — do **not** call `math.acos` for this part.
4. Include the three angles in degrees, computed with the cosine rule.
5. Assert that your angles sum to $180°$ for every valid input.

**Edge cases your tests must cover:** $(3,4,5)$ right scalene; $(1,1,1)$ equilateral; $(5,5,8)$ isosceles obtuse; $(1,2,3)$ degenerate — rejected, since $1 + 2 = 3$ exactly; $(1,2,10)$ impossible.

**Done when:** all five cases give the classification you predicted *before* running, your angle sums pass, and you can explain why $(1,2,3)$ must be rejected rather than treated as a very thin triangle.

## Tradeoffs, limits and extensions

**Congruence criteria are about certainty, not convenience.** SSS needs three measurements of the fussiest kind — lengths of sides you may not be able to reach. ASA needs two angles, which are often easier to obtain at a distance. Choosing the criterion is usually driven by what you can actually measure.

**Floating point makes exact equality unusable.** The lab compares against a tolerance (`< 1e-9`) rather than testing `== 180`. Accumulated rounding in `acos` and `hypot` means the sum comes out as something like $179.99999999999997$. Choosing the tolerance is a real decision: too tight and correct triangles fail; too loose and genuinely different shapes pass as congruent.

**Beyond the plane.** On a sphere, the excess of a triangle's angle sum over $180°$ is proportional to its *area* — a result with no Euclidean analogue at all. [[01-latitude-and-longitude|Latitude and longitude]] works in that setting.

## Before moving on

You are done with this lesson when you can:

- Prove the angle sum of a triangle, naming the construction and the rule at each step.
- Pick the correct congruence criterion for a given pair of triangles, and reject SSA with a concrete counterexample.
- Derive $(n-2)\times180°$ rather than recall it.

**Recap for later lookup:** triangle angle sum $180°$; exterior angle = sum of the two opposite interiors; congruence by SSS, SAS, ASA, AAS, RHS — **not** SSA; similarity by AA; polygon interior sum $(n-2)\times180°$, exterior sum $360°$ always.

**Next:** [[03-constructions|Constructions]] — building exact figures with only a compass and straightedge, and proving that what you built is what you claimed.

## Related

- [[01-angles-and-parallel-lines|Angles and Parallel Lines]] — the alternate-angle rule the angle-sum proof depends on
- [[03-sine-and-cosine-rules|Sine and Cosine Rules]] — the sine rule is what makes the ambiguous case computable
- [[01-plane-shapes|Mensuration: Plane Shapes]] — from angles to areas
- [[02-discrete-math/03-proof-techniques|Proof Techniques]] — the general shapes of argument used informally here
