# Vectors

**[Intermediate]** — quantities with direction, and the algebra that works identically in 2, 3 or 300 dimensions.

## Before you start

- You know the dot and cross products geometrically — [[01-lines-and-planes|lines and planes in space]]. This lesson develops the same objects **algebraically**, and does not repeat the geometry.
- You can manipulate algebraic expressions — [[03-algebraic-manipulation|algebraic manipulation]].
- Helpful: [[01-matrices-and-determinants|matrices]], since a vector is a one-column matrix.

**What you will be able to do after this lesson:**

1. Work with vectors in **any** number of dimensions, and say which operations survive the move beyond three and which do not.
2. Project one vector onto another, and split a vector into parallel and perpendicular parts.
3. Prove the **Cauchy–Schwarz inequality**, and derive the triangle inequality from it.
4. Explain **cosine similarity**, and why it is the standard way to compare documents or embeddings.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 4 is where this stops being geometry.

---

## 1. Why this exists

A force of $5$ newtons is not a complete description — you need to know which way it pushes. Same for velocity, displacement, electric field. These are **vectors**: magnitude *and* direction.

That much is school physics, and [[01-lines-and-planes|the geometry course]] handles the arrows. The reason vectors get a second lesson, in an algebra course, is that the arrow picture **runs out**.

A document can be represented by how often each word occurs — a vector with one component per word in the vocabulary, so perhaps $50{,}000$ dimensions. A neural network's embedding of a sentence is a vector of $1{,}536$ numbers. Neither can be drawn, and no intuition about arrows applies. But the *algebra* is unchanged: you can still add them, scale them, take dot products, measure angles, and ask whether two are pointing the same way.

That is the point of this lesson. Everything is defined by **formulas on components**, so nothing depends on being able to picture it.

## 2. Terminology

| Term | Plain-English definition | Note |
| :--- | :--- | :--- |
| **Vector** | An ordered list of numbers, $\mathbf{a} = (a_1, \dots, a_n)$ | A point, a displacement, or a list of measurements |
| **Component** | One entry of the list | $a_i$ |
| **Magnitude** (norm) | $\lVert\mathbf{a}\rVert = \sqrt{a_1^2 + \cdots + a_n^2}$ | Pythagoras, in $n$ dimensions |
| **Unit vector** | A vector of magnitude $1$ | $\hat{\mathbf{a}} = \mathbf{a}/\lVert\mathbf{a}\rVert$ |
| **Zero vector** | All components zero | Has no direction |
| **Linear combination** | $c_1\mathbf{v}_1 + \cdots + c_k\mathbf{v}_k$ | The single most important phrase in linear algebra |
| **Orthogonal** | Perpendicular — dot product zero | Works in any dimension |
| **Projection** | The shadow of one vector along another | The "how much of $\mathbf{a}$ points along $\mathbf{b}$" |

## 3. Operations, and which ones generalise

**Addition and scalar multiplication** are componentwise:

$$
\mathbf{a} + \mathbf{b} = (a_1+b_1, \dots, a_n+b_n), \qquad k\mathbf{a} = (ka_1, \dots, ka_n)
$$

Geometrically, addition is the triangle law — but the formula needs no picture, and works in $50{,}000$ dimensions unchanged.

**The dot product** is the sum of componentwise products:

$$
\mathbf{a}\cdot\mathbf{b} = \sum_{i=1}^{n} a_i b_i
$$

and it connects to geometry through:

$$
\mathbf{a}\cdot\mathbf{b} = \lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert\cos\theta
$$

In two or three dimensions this is a theorem about an angle you can see. In $n$ dimensions it is turned round and used as the **definition** of the angle:

$$
\cos\theta = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}
$$

That is legitimate only because the right-hand side is guaranteed to lie in $[-1, 1]$ — which is exactly what Cauchy–Schwarz says, and is why section 4 proves it before using it.

**The cross product does not generalise.** It is defined only in three dimensions (and, in a modified form, seven). Everything else here works in any number of dimensions; the cross product is the exception, and if a technique depends on it, that technique is stuck in 3-D.

### Projection

The component of $\mathbf{a}$ pointing along $\mathbf{b}$:

$$
\operatorname{proj}_{\mathbf{b}}\mathbf{a} = \left(\frac{\mathbf{a}\cdot\mathbf{b}}{\mathbf{b}\cdot\mathbf{b}}\right)\mathbf{b}
$$

The fraction is a **number** — how many copies of $\mathbf{b}$ you need — and multiplying by $\mathbf{b}$ turns it back into a vector.

This gives the decomposition that everything from least-squares fitting to Gram–Schmidt relies on:

$$
\mathbf{a} = \underbrace{\operatorname{proj}_{\mathbf{b}}\mathbf{a}}_{\text{parallel to } \mathbf{b}} + \underbrace{\left(\mathbf{a} - \operatorname{proj}_{\mathbf{b}}\mathbf{a}\right)}_{\text{orthogonal to } \mathbf{b}}
$$

Every vector splits, uniquely, into a part along $\mathbf{b}$ and a part perpendicular to it. Block 3 of the lab checks the perpendicularity.

## 4. Cauchy–Schwarz, and the triangle inequality

**Claim:** for any two vectors,

$$
\lvert \mathbf{a}\cdot\mathbf{b} \rvert \le \lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert
$$

with equality exactly when one is a scalar multiple of the other.

**Proof.** Consider the vector $\mathbf{a} - t\mathbf{b}$ for a real number $t$. Its squared length cannot be negative:

$$
0 \le \lVert\mathbf{a} - t\mathbf{b}\rVert^2 = (\mathbf{a}-t\mathbf{b})\cdot(\mathbf{a}-t\mathbf{b}) = \lVert\mathbf{a}\rVert^2 - 2t\,(\mathbf{a}\cdot\mathbf{b}) + t^2\lVert\mathbf{b}\rVert^2
$$

Read the right-hand side as a **quadratic in $t$**. It is never negative, so it cannot have two distinct real roots, so its discriminant is at most zero:

$$
4(\mathbf{a}\cdot\mathbf{b})^2 - 4\lVert\mathbf{b}\rVert^2\lVert\mathbf{a}\rVert^2 \le 0
$$

Rearranging and taking square roots gives the result. $\blacksquare$

Equality needs the discriminant to be exactly zero, which means $\lVert\mathbf{a}-t\mathbf{b}\rVert = 0$ for some $t$ — that is, $\mathbf{a} = t\mathbf{b}$.

Notice what the proof used: only that a squared length is non-negative, and the algebra of the dot product. Nothing about dimension, and nothing about pictures.

**The triangle inequality** follows in three lines:

$$
\lVert\mathbf{a}+\mathbf{b}\rVert^2 = \lVert\mathbf{a}\rVert^2 + 2(\mathbf{a}\cdot\mathbf{b}) + \lVert\mathbf{b}\rVert^2 \le \lVert\mathbf{a}\rVert^2 + 2\lVert\mathbf{a}\rVert\lVert\mathbf{b}\rVert + \lVert\mathbf{b}\rVert^2 = \left(\lVert\mathbf{a}\rVert+\lVert\mathbf{b}\rVert\right)^2
$$

so $\lVert\mathbf{a}+\mathbf{b}\rVert \le \lVert\mathbf{a}\rVert + \lVert\mathbf{b}\rVert$: no detour is shorter than going direct.

> [!TIP]
> **Predict before running the lab.** Two documents are represented by word-count vectors. Document A uses every word exactly twice as often as document B — it is simply twice as long, on the same topic. What is the **angle** between their vectors, and what is the **distance** between them? Which of the two is the better measure of "same topic"? Decide before opening the answers.

## 5. Cosine similarity

Comparing two documents by the **distance** between their word-count vectors punishes length: a long article and a short note on the identical topic sit far apart, simply because one has bigger numbers.

Comparing them by the **angle** does not. Scaling a vector does not change its direction, so:

$$
\text{similarity}(\mathbf{a}, \mathbf{b}) = \cos\theta = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}
$$

is $1$ for identical direction, $0$ for orthogonal, and (for non-negative data like word counts) never below $0$.

This is the standard similarity measure for text retrieval, recommendation systems and embedding search — every "find similar documents" feature is this formula, in a few hundred or a few thousand dimensions. It is worth appreciating that it is nothing more than the dot product with the lengths divided out, and that Cauchy–Schwarz is what guarantees it is a valid cosine at all.

## Worked example — runnable

**Runnable example:** save as `vectors.py` in any empty directory and run `python3 vectors.py`. Standard library only; writes no files.

```python
"""Vector algebra that does not depend on being able to draw the vectors."""
import math

EPS = 1e-9


def add(a, b):     return tuple(x + y for x, y in zip(a, b))
def sub(a, b):     return tuple(x - y for x, y in zip(a, b))
def scale(a, k):   return tuple(k * x for x in a)
def dot(a, b):     return sum(x * y for x, y in zip(a, b))
def norm(a):       return math.sqrt(dot(a, a))


def unit(a):
    n = norm(a)
    if n < EPS:
        raise ValueError("the zero vector has no direction")
    return scale(a, 1 / n)


def angle_between(a, b):
    c = dot(a, b) / (norm(a) * norm(b))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def project(a, b):
    """The part of a that points along b."""
    return scale(b, dot(a, b) / dot(b, b))


def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))


def gram_schmidt(vectors):
    """Turn a list of vectors into an orthogonal set spanning the same space."""
    out = []
    for v in vectors:
        w = v
        for u in out:                       # subtract off every direction already taken
            w = sub(w, project(w, u))
        if norm(w) > 1e-8:                  # discard anything already spanned
            out.append(w)
    return out


if __name__ == "__main__":
    print("Block 1 - the same formulas in 2, 3 and 10 dimensions")
    for v in [(3.0, 4.0), (1.0, 2.0, 2.0), tuple(float(i) for i in range(1, 11))]:
        print(f"  dim {len(v):2}: norm = {norm(v):9.6f},  unit norm = {norm(unit(v)):.9f}")
        assert abs(norm(unit(v)) - 1) < EPS
    assert abs(norm((3.0, 4.0)) - 5.0) < EPS         # the 3-4-5 triangle
    try:
        unit((0.0, 0.0, 0.0))
    except ValueError as e:
        print(f"  the zero vector: {e}")

    print()
    print("Block 2 - Cauchy-Schwarz and the triangle inequality")
    print("            a.b      |a||b|    slack      |a+b|   |a|+|b|")
    pairs = [((3.0, 4.0), (4.0, 3.0)),
             ((1.0, 0.0), (0.0, 1.0)),
             ((2.0, 1.0), (4.0, 2.0)),                # parallel: equality case
             ((1.0, 2.0, 3.0), (-2.0, 0.0, 5.0))]
    for a, b in pairs:
        cs_lhs, cs_rhs = abs(dot(a, b)), norm(a) * norm(b)
        tri_lhs, tri_rhs = norm(add(a, b)), norm(a) + norm(b)
        print(f"  {cs_lhs:9.4f}  {cs_rhs:9.4f}  {cs_rhs - cs_lhs:8.4f}"
              f"  {tri_lhs:9.4f}  {tri_rhs:9.4f}")
        assert cs_lhs <= cs_rhs + EPS
        assert tri_lhs <= tri_rhs + EPS
    # the parallel pair should hit equality in BOTH inequalities
    a, b = (2.0, 1.0), (4.0, 2.0)
    assert abs(abs(dot(a, b)) - norm(a) * norm(b)) < EPS
    assert abs(norm(add(a, b)) - (norm(a) + norm(b))) < EPS
    print("  row 3 is the equality case: b = 2a, so the vectors are parallel")

    print()
    print("Block 3 - every vector splits into parallel and perpendicular parts")
    a, b = (4.0, 3.0), (1.0, 0.0)
    par = project(a, b)
    perp = sub(a, par)
    print(f"  a = {a}, b = {b}")
    print(f"    parallel part      {par}")
    print(f"    perpendicular part {perp}")
    print(f"    they sum back to   {add(par, perp)}")
    print(f"    perp . b = {dot(perp, b):.9f}  (must be zero)")
    assert abs(dot(perp, b)) < EPS
    assert all(abs(x - y) < EPS for x, y in zip(add(par, perp), a))
    # Pythagoras holds for the two parts
    assert abs(norm(a) ** 2 - (norm(par) ** 2 + norm(perp) ** 2)) < EPS
    print(f"    |a|^2 = |par|^2 + |perp|^2: {norm(a)**2:.6f}"
          f" = {norm(par)**2:.6f} + {norm(perp)**2:.6f}")

    print()
    print("Block 4 - comparing documents, where no picture is available")
    VOCAB = ["cache", "memory", "latency", "recipe", "flour", "oven"]
    docs = {
        "systems note ": (4, 6, 5, 0, 0, 0),
        "same, longer ": (8, 12, 10, 0, 0, 0),      # exactly twice as long
        "systems essay": (2, 9, 7, 0, 1, 0),
        "baking post  ": (0, 1, 0, 5, 7, 6),
    }
    names = list(docs)
    print(f"  vocabulary: {VOCAB}")
    print("                     " + "".join(f"{n[:9]:>11}" for n in names))
    for n1 in names:
        row = "".join(f"{cosine_similarity(docs[n1], docs[n2]):11.4f}" for n2 in names)
        print(f"  {n1}      {row}")
    # a document and a scaled copy of it are at angle zero
    assert abs(cosine_similarity(docs["systems note "], docs["same, longer "]) - 1) < EPS
    print("  'systems note' and 'same, longer' have similarity exactly 1.0:")
    print("    identical direction, because one is a scalar multiple of the other")
    d = norm(sub(docs["systems note "], docs["same, longer "]))
    print(f"    yet the DISTANCE between them is {d:.4f} - which is why angle wins")
    assert d > 5
    assert cosine_similarity(docs["systems note "], docs["baking post  "]) < 0.1
    print("  and the baking post is nearly orthogonal to all three systems notes")

    print()
    print("Block 5 - Gram-Schmidt: building an orthogonal set by repeated projection")
    basis = [(1.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0)]
    ortho = gram_schmidt(basis)
    for i, v in enumerate(ortho):
        print(f"  v{i+1} = {tuple(round(x, 6) for x in v)}")
    for i in range(len(ortho)):
        for j in range(i + 1, len(ortho)):
            assert abs(dot(ortho[i], ortho[j])) < 1e-9, (i, j)
    print("  every pair is orthogonal, to within 1e-9")

    dependent = [(1.0, 1.0, 0.0), (2.0, 2.0, 0.0), (0.0, 0.0, 3.0)]
    result = gram_schmidt(dependent)
    print(f"  given a dependent set of 3, Gram-Schmidt returns {len(result)} vectors")
    print("    the second was already spanned by the first, so it contributed nothing")
    assert len(result) == 2

    print()
    print("vectors: passed")
```

Expected output:

```
Block 1 - the same formulas in 2, 3 and 10 dimensions
  dim  2: norm =  5.000000,  unit norm = 1.000000000
  dim  3: norm =  3.000000,  unit norm = 1.000000000
  dim 10: norm = 19.621417,  unit norm = 1.000000000
  the zero vector: the zero vector has no direction

Block 2 - Cauchy-Schwarz and the triangle inequality
            a.b      |a||b|    slack      |a+b|   |a|+|b|
    24.0000    25.0000    1.0000     9.8995    10.0000
     0.0000     1.0000    1.0000     1.4142     2.0000
    10.0000    10.0000    0.0000     6.7082     6.7082
    13.0000    20.1494    7.1494     8.3066     9.1268
  row 3 is the equality case: b = 2a, so the vectors are parallel

Block 3 - every vector splits into parallel and perpendicular parts
  a = (4.0, 3.0), b = (1.0, 0.0)
    parallel part      (4.0, 0.0)
    perpendicular part (0.0, 3.0)
    they sum back to   (4.0, 3.0)
    perp . b = 0.000000000  (must be zero)
    |a|^2 = |par|^2 + |perp|^2: 25.000000 = 16.000000 + 9.000000

Block 4 - comparing documents, where no picture is available
  vocabulary: ['cache', 'memory', 'latency', 'recipe', 'flour', 'oven']
                       systems n  same, lon  systems e  baking po
  systems note            1.0000     1.0000     0.9514     0.0649
  same, longer            1.0000     1.0000     0.9514     0.0649
  systems essay           0.9514     0.9514     1.0000     0.1307
  baking post             0.0649     0.0649     0.1307     1.0000
  'systems note' and 'same, longer' have similarity exactly 1.0:
    identical direction, because one is a scalar multiple of the other
    yet the DISTANCE between them is 8.7750 - which is why angle wins
  and the baking post is nearly orthogonal to all three systems notes

Block 5 - Gram-Schmidt: building an orthogonal set by repeated projection
  v1 = (1.0, 1.0, 0.0)
  v2 = (0.5, -0.5, 1.0)
  v3 = (-0.666667, 0.666667, 0.666667)
  every pair is orthogonal, to within 1e-9
  given a dependent set of 3, Gram-Schmidt returns 2 vectors
    the second was already spanned by the first, so it contributed nothing

vectors: passed
```

Block 4 is the point of the lesson. Nothing there can be drawn — it is a six-dimensional space of word counts — yet every operation is the same one used on arrows, and the answer is exactly right: the note and its doubled copy are at angle zero, and the baking post is nearly orthogonal to all of them.

## Common pitfalls and traps

- **Trying to use the cross product in more than three dimensions.** It does not exist there. If a method needs it, that method is confined to 3-D.
- **Confusing $\mathbf{a}\cdot\mathbf{b}$ (a number) with $\operatorname{proj}_{\mathbf{b}}\mathbf{a}$ (a vector).** The projection is the dot product *scaled by $\mathbf{b}$ again*; forgetting the final multiplication is the most common slip.
- **Normalising the zero vector.** It has no direction and $\mathbf{0}/0$ is undefined. Any function taking a "direction" needs a decision about this input; the lab raises.
- **Using distance where angle is wanted.** For anything where magnitude reflects length or intensity rather than content — documents, ratings, spectra — cosine similarity is usually the right measure. The lab quantifies the difference.
- **Assuming $\cos\theta$ can be computed before you know it is in range.** In floating point, $\frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\lVert\mathbf{b}\rVert}$ can come out as $1.0000000000000002$ and crash `acos`. Cauchy–Schwarz says it *should* be in range; rounding says clamp anyway.
- **Expecting Gram–Schmidt to return as many vectors as it was given.** If the input is linearly dependent, it returns fewer — and that is the useful behaviour, not a bug.

## Check your understanding

1. Find $\lVert(2, -3, 6)\rVert$ and the unit vector in that direction.
2. Find the angle between $(1, 0, 1)$ and $(0, 1, 1)$.
3. Project $(3, 4)$ onto $(1, 1)$. What is the perpendicular part?
4. Two vectors have $\mathbf{a}\cdot\mathbf{b} = 12$, $\lVert\mathbf{a}\rVert = 3$, $\lVert\mathbf{b}\rVert = 4$. What can you conclude?
5. Why does cosine similarity give $1$ for a document and a doubled copy of it, while Euclidean distance does not give $0$?

<details><summary>Answers — open only after an attempt</summary>

1. $\lVert\mathbf{a}\rVert = \sqrt{4+9+36} = \sqrt{49} = 7$. The unit vector is $\left(\tfrac27, -\tfrac37, \tfrac67\right)$.
2. $\cos\theta = \frac{0 + 0 + 1}{\sqrt2\cdot\sqrt2} = \tfrac12$, so $\theta = 60°$.
3. $\operatorname{proj} = \frac{3+4}{2}(1,1) = (3.5, 3.5)$. The perpendicular part is $(3,4) - (3.5,3.5) = (-0.5, 0.5)$, and indeed $(-0.5)(1) + (0.5)(1) = 0$. ✓
4. Cauchy–Schwarz gives $\lvert\mathbf{a}\cdot\mathbf{b}\rvert \le 3\times4 = 12$, and here it is **exactly** $12$. That is the equality case, so the two vectors are **parallel** — $\mathbf{b}$ is a positive scalar multiple of $\mathbf{a}$ (positive, since the dot product is positive). The angle is $0°$.
5. Because scaling a vector changes its magnitude but not its direction. Cosine similarity divides both magnitudes out, so it sees only direction and returns $1$. Euclidean distance measures the gap between the endpoints, which grows with the scaling.

**And the prediction from section 4:** the angle is $0°$ — the vectors are parallel, so cosine similarity is exactly $1$. The distance, however, is $\lVert\mathbf{a}\rVert$ itself (since $\mathbf{b} - \mathbf{a} = \mathbf{a}$ when $\mathbf{b} = 2\mathbf{a}$), which is large. **Angle** is the better measure of "same topic", because it ignores the length difference that carries no topical information.
</details>

## Practice — independent task

Implement `least_squares_fit(points)`: given $(x, y)$ data, find the straight line minimising the total squared vertical error — using **projection**, not the memorised formulas.

1. Set it up as a vector problem. With $\mathbf{x}$ the vector of $x$-values, $\mathbf{y}$ the vector of $y$-values, and $\mathbf{1}$ the all-ones vector, you are looking for the combination $m\mathbf{x} + c\mathbf{1}$ closest to $\mathbf{y}$.
2. Use Gram–Schmidt to build an orthogonal basis for the span of $\{\mathbf{1}, \mathbf{x}\}$, then project $\mathbf{y}$ onto it. Recover $m$ and $c$ from the projection.
3. Assert that the **residual** $\mathbf{y} - (m\mathbf{x} + c\mathbf{1})$ is orthogonal to both $\mathbf{x}$ and $\mathbf{1}$. This is the defining property of a least-squares fit — the error has no component left in the space you were fitting from.
4. Check against the standard formulas $m = \frac{n\sum xy - \sum x\sum y}{n\sum x^2 - (\sum x)^2}$ and $c = \bar{y} - m\bar{x}$, to within `1e-9`.
5. Verify on data that lies **exactly** on a line: the residual must be the zero vector.

**Edge cases:** all $x$ values identical (a vertical line — no function fits; say what you return); fewer than two points; two points exactly (the fit is exact).

**Done when:** your orthogonality assertion in step 3 passes for at least five datasets, your answer matches the closed-form formulas, and you can explain in a sentence why "minimise the squared error" and "make the residual orthogonal" are the same condition.

## Tradeoffs, limits and extensions

**The norm is a choice.** $\lVert\cdot\rVert_2$ (Pythagoras) is one option among many. The **$L^1$ norm** $\sum\lvert a_i\rvert$ measures city-block distance and produces sparse solutions, which is why LASSO regression uses it. The **$L^\infty$ norm** takes the largest component. Each defines a different geometry, and different "closest points". The one used here is standard because it is the only one coming from a dot product — which is what makes projection and orthogonality available at all.

**High dimensions are strange.** In $1{,}000$ dimensions, randomly chosen vectors are almost always nearly orthogonal, and almost all of a ball's volume sits near its surface. Intuition trained on arrows in 3-D is actively misleading, which is another reason to trust the algebra over the picture. This is the "curse of dimensionality" that affects nearest-neighbour search.

**Dot products dominate the cost of modern computing.** A matrix multiplication is a grid of dot products, and a transformer's attention mechanism is dot products between query and key vectors. Essentially all GPU hardware exists to do the operation in section 3 as fast as possible.

## Before moving on

You are done with this lesson when you can:

- Compute norms, angles and projections in any dimension without reaching for a picture.
- Prove Cauchy–Schwarz from the non-negativity of $\lVert\mathbf{a}-t\mathbf{b}\rVert^2$.
- Split a vector into parallel and perpendicular parts and verify the split.
- Say why cosine similarity, not distance, compares documents.

**Recap for later lookup:** $\lVert\mathbf{a}\rVert = \sqrt{\mathbf{a}\cdot\mathbf{a}}$; $\mathbf{a}\cdot\mathbf{b} = \sum a_ib_i = \lVert\mathbf{a}\rVert\lVert\mathbf{b}\rVert\cos\theta$; $\operatorname{proj}_{\mathbf{b}}\mathbf{a} = \frac{\mathbf{a}\cdot\mathbf{b}}{\mathbf{b}\cdot\mathbf{b}}\mathbf{b}$; Cauchy–Schwarz $\lvert\mathbf{a}\cdot\mathbf{b}\rvert \le \lVert\mathbf{a}\rVert\lVert\mathbf{b}\rVert$ with equality iff parallel; triangle inequality follows; cosine similarity is the dot product with both lengths divided out; the cross product exists only in 3-D.

**Next:** [[03-systems-of-linear-equations/01-gaussian-elimination|Systems of Linear Equations]] — solving $A\mathbf{x} = \mathbf{b}$ the way software actually does it.

## Related

- [[01-lines-and-planes|Lines and Planes in Space]] — the same objects, geometrically
- [[01-matrices-and-determinants|Matrices and Determinants]] — what acts on these
- [[04-vector-spaces/01-vector-spaces|Vector Spaces]] — the abstraction that lets polynomials and functions be vectors too
