# Sine and Cosine Rules

**[Intermediate]** — solving triangles that have no right angle, and the one case where the data does not determine the answer.

## Before you start

- You know the ratios and can drop a perpendicular to create right triangles — [[01-ratios-and-right-triangles|trigonometric ratios]].
- You know that $\sin(180° - \theta) = \sin\theta$ — [[02-graphs-and-identities|graphs and identities]]. This identity is the entire source of the ambiguous case.
- You met SSA as the criterion that fails — [[02-triangles-and-polygons|triangles and polygons]].

**What you will be able to do after this lesson:**

1. Derive both rules — the sine rule by dropping a perpendicular, the cosine rule by coordinates.
2. Choose the correct rule from which parts of the triangle are known.
3. Detect and resolve the **ambiguous case**, returning both triangles when both exist.
4. Compute a triangle's area from two sides and the included angle, and from three sides.

**Study route:** read 1–5, attempt the prediction in section 5, then run the lab. Block 4 is the one that matters.

---

## 1. Why this exists

SOH-CAH-TOA requires a right angle. Most triangles do not have one.

A surveyor measuring across a river cannot choose the triangle's shape — the landmarks are where they are. Triangulation, the technique that mapped entire countries before satellites, works by measuring one baseline accurately and then measuring only *angles* to distant points, chaining triangle to triangle. None of those triangles is right-angled.

The two rules below extend trigonometry to every triangle. Both are proved by the same trick: **drop a perpendicular to manufacture right triangles**, then eliminate it.

## 2. The sine rule

**Claim:**

$$
\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}
$$

where $a$ is the side **opposite** angle $A$, and so on.

**Proof.** Drop a perpendicular of length $h$ from vertex $C$ to side $AB$.

```
              C
             /|\
            / | \
         b /  |h \ a
          /   |   \
         /____|____\
        A           B
              c
```

In the left right triangle, $h = b\sin A$. In the right one, $h = a\sin B$. The same $h$:

$$
b\sin A = a\sin B \quad\Longrightarrow\quad \frac{a}{\sin A} = \frac{b}{\sin B}
$$

Repeat with a perpendicular from $A$ to get the third ratio. $\blacksquare$

**The common value has a meaning.** All three ratios equal $2R$, where $R$ is the radius of the **circumcircle** — the circle through all three vertices, met in the [[01-circle-theorems|circle theorems]] practice task:

$$
\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R
$$

This follows from the central angle theorem: the chord $a$ subtends angle $A$ at the circumference and $2A$ at the centre, and the chord of a circle subtending $2A$ at the centre has length $2R\sin A$.

**Use it when you know:** two angles and any side (ASA, AAS), or two sides and a non-included angle (SSA — with care).

## 3. The cosine rule

**Claim:**

$$
c^2 = a^2 + b^2 - 2ab\cos C
$$

**Proof by coordinates.** Place the triangle so that $A$ is at the origin and $B$ lies on the positive $x$-axis:

$$
A = (0, 0), \qquad B = (c, 0), \qquad C = (b\cos A,\ b\sin A)
$$

The placement of $C$ is exactly the unit circle definition scaled by $b$. Now compute $a^2 = BC^2$ with the distance formula:

$$
a^2 = (b\cos A - c)^2 + (b\sin A)^2
$$
$$
= b^2\cos^2 A - 2bc\cos A + c^2 + b^2\sin^2 A
$$
$$
= b^2(\cos^2 A + \sin^2 A) - 2bc\cos A + c^2
$$

And $\cos^2 + \sin^2 = 1$, so:

$$
a^2 = b^2 + c^2 - 2bc\cos A \qquad \blacksquare
$$

**Pythagoras is the special case.** Put $A = 90°$. Then $\cos A = 0$ and the correction term vanishes:

$$
a^2 = b^2 + c^2
$$

So the cosine rule is Pythagoras plus a correction $-2bc\cos A$ that measures how far the triangle is from right-angled. Acute angle ⇒ $\cos A > 0$ ⇒ the opposite side is **shorter** than Pythagoras would give. Obtuse ⇒ longer.

**Use it when you know:** three sides (SSS — rearrange for the angle), or two sides and the **included** angle (SAS).

### Rearranged for an angle

$$
\cos C = \frac{a^2 + b^2 - c^2}{2ab}
$$

The sign of the numerator alone classifies the angle — positive means acute, zero right, negative obtuse. That is the classification test from the [[02-triangles-and-polygons|triangles]] practice task, and it needs no inverse cosine at all.

## 4. Which rule, and area

| You know | Use | Notes |
| :--- | :--- | :--- |
| SSS | **Cosine** rule, rearranged | Start with the angle opposite the longest side |
| SAS | **Cosine** rule | Gives the third side directly |
| ASA / AAS | **Sine** rule | Find the third angle first by the angle sum |
| SSA | **Sine** rule | **Ambiguous** — may give two triangles, one, or none |

**Area from two sides and the included angle.** The perpendicular from the sine-rule proof has height $h = b\sin A$, and area is half base times height:

$$
\text{Area} = \tfrac12 bc\sin A
$$

**Area from three sides — Heron's formula.** With $s = \frac{a+b+c}{2}$ the semi-perimeter:

$$
\text{Area} = \sqrt{s(s-a)(s-b)(s-c)}
$$

Heron's formula follows from the previous one by substituting $\sin A = \sqrt{1 - \cos^2 A}$ and the cosine rule, then simplifying — long, but nothing beyond algebra.

> [!TIP]
> **Predict before section 5.** You are given $A = 30°$, $a = 5$, $b = 8$. The sine rule gives $\sin B = \frac{b\sin A}{a} = 0.8$, so $B = 53.13°$. Is that the answer? What else satisfies $\sin B = 0.8$, and does it produce a valid triangle? Decide before opening the answers.

## 5. The ambiguous case, resolved

Given SSA — angle $A$, opposite side $a$, adjacent side $b$ — the sine rule gives:

$$
\sin B = \frac{b\sin A}{a}
$$

Because $\sin(180° - B) = \sin B$, **two** angles satisfy this whenever $\sin B < 1$. Both may be legitimate. The full case analysis:

| Condition | Triangles | Why |
| :--- | :---: | :--- |
| $\sin B > 1$ | **0** | Side $a$ is too short to reach the far arm |
| $\sin B = 1$ | **1** | Exactly one right-angled triangle; $a$ is the perpendicular distance |
| $\sin B < 1$ and $a \ge b$ | **1** | The obtuse branch gives $A + B \ge 180°$, so it is rejected |
| $\sin B < 1$ and $a < b$ | **2** | Both branches give a valid third angle — genuinely ambiguous |

The deciding comparison is $a$ against $b$: the side **opposite** the known angle against the side **adjacent** to it. When the opposite side is the shorter one, the swinging arm crosses twice.

This is not a defect of the sine rule. It is the data being genuinely insufficient, which is exactly why SSA is absent from the congruence criteria.

## Worked example — runnable

**Runnable example:** save as `triangle_rules.py` in any empty directory and run `python3 triangle_rules.py`. Standard library only; writes no files.

```python
"""Sine and cosine rules, with the full ambiguous-case analysis."""
import math

EPS = 1e-9


def dist(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def sides_and_angles(A_pt, B_pt, C_pt):
    """Return (a, b, c, A, B, C) in degrees, from three vertices."""
    a, b, c = dist(B_pt, C_pt), dist(A_pt, C_pt), dist(A_pt, B_pt)
    A = math.degrees(math.acos(max(-1, min(1, (b*b + c*c - a*a) / (2*b*c)))))
    B = math.degrees(math.acos(max(-1, min(1, (a*a + c*c - b*b) / (2*a*c)))))
    C = math.degrees(math.acos(max(-1, min(1, (a*a + b*b - c*c) / (2*a*b)))))
    return a, b, c, A, B, C


def circumradius(a, b, c):
    """From the extended sine rule: R = abc / (4 * area)."""
    s = (a + b + c) / 2
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    return a * b * c / (4 * area)


def solve_ssa(A_deg, a, b):
    """All triangles with angle A, opposite side a, adjacent side b."""
    sin_B = b * math.sin(math.radians(A_deg)) / a
    if sin_B > 1 + EPS:
        return []
    sin_B = min(1.0, sin_B)
    B1 = math.degrees(math.asin(sin_B))
    out = []
    for B in ({B1} if abs(sin_B - 1) < EPS else {B1, 180 - B1}):
        C = 180 - A_deg - B
        if C > EPS:
            c = a * math.sin(math.radians(C)) / math.sin(math.radians(A_deg))
            out.append({"B": B, "C": C, "c": c})
    return sorted(out, key=lambda s: s["B"])


if __name__ == "__main__":
    print("Block 1 - both rules agree with coordinates")
    for tri in [((0, 0), (7, 0), (2, 5)),
                ((0, 0), (6, 0), (6, 8)),
                ((-3, 1), (4, -2), (1, 6))]:
        a, b, c, A, B, C = sides_and_angles(*tri)
        # sine rule: all three ratios equal
        ratios = [a / math.sin(math.radians(A)),
                  b / math.sin(math.radians(B)),
                  c / math.sin(math.radians(C))]
        # cosine rule: reconstruct side c from a, b and C
        c_from_cos = math.sqrt(a*a + b*b - 2*a*b*math.cos(math.radians(C)))
        print(f"  sides {a:.4f} {b:.4f} {c:.4f}  angles {A:.2f} {B:.2f} {C:.2f}")
        print(f"    sine-rule ratios: {ratios[0]:.6f} {ratios[1]:.6f} {ratios[2]:.6f}")
        print(f"    cosine rule gives c = {c_from_cos:.6f}  (measured {c:.6f})")
        assert max(ratios) - min(ratios) < 1e-9
        assert abs(c_from_cos - c) < 1e-9

    print()
    print("Block 2 - the common ratio is the circumcircle diameter")
    a, b, c, A, B, C = sides_and_angles((0, 0), (7, 0), (2, 5))
    R = circumradius(a, b, c)
    print(f"  a/sin A = {a / math.sin(math.radians(A)):.6f}")
    print(f"  2R      = {2 * R:.6f}")
    assert abs(a / math.sin(math.radians(A)) - 2 * R) < 1e-9

    print()
    print("Block 3 - area two ways, and Pythagoras as a special case")
    for tri in [((0, 0), (7, 0), (2, 5)), ((0, 0), (6, 0), (6, 8))]:
        a, b, c, A, B, C = sides_and_angles(*tri)
        by_sine = 0.5 * a * b * math.sin(math.radians(C))
        s = (a + b + c) / 2
        by_heron = math.sqrt(s * (s - a) * (s - b) * (s - c))
        print(f"  1/2 ab sin C = {by_sine:.6f},  Heron = {by_heron:.6f}")
        assert abs(by_sine - by_heron) < 1e-9
    # the right-angled triangle: the cosine correction term vanishes
    a, b, c, A, B, C = sides_and_angles((0, 0), (6, 0), (6, 8))
    print(f"  right-angled triangle: largest angle = {max(A, B, C):.6f}")
    print(f"    6^2 + 8^2 = {6**2 + 8**2}, 10^2 = {10**2}")
    assert abs(max(A, B, C) - 90) < 1e-9

    print()
    print("Block 4 - the ambiguous case, all four outcomes")
    cases = [
        ("A=30, a=5,  b=8   (a < b, sin B < 1)", 30, 5, 8),
        ("A=30, a=4,  b=8   (a is exactly half b)", 30, 4, 8),
        ("A=30, a=3,  b=8   (a too short to reach)", 30, 3, 8),
        ("A=30, a=10, b=8   (a >= b)", 30, 10, 8),
    ]
    for label, A_deg, a_len, b_len in cases:
        sols = solve_ssa(A_deg, a_len, b_len)
        print(f"  {label:40} -> {len(sols)} triangle(s)")
        for s in sols:
            print(f"      B={s['B']:9.4f}  C={s['C']:9.4f}  c={s['c']:9.4f}")
        # every returned triangle must satisfy the sine rule it came from
        for s in sols:
            assert abs(a_len / math.sin(math.radians(A_deg))
                       - b_len / math.sin(math.radians(s["B"]))) < 1e-9
    assert len(solve_ssa(30, 5, 8)) == 2      # ambiguous
    assert len(solve_ssa(30, 4, 8)) == 1      # right-angled, sin B = 1
    assert len(solve_ssa(30, 3, 8)) == 0      # impossible
    assert len(solve_ssa(30, 10, 8)) == 1     # a >= b, obtuse branch rejected

    print()
    print("triangle_rules: passed")
```

Expected output:

```
Block 1 - both rules agree with coordinates
  sides 7.0711 5.3852 7.0000  angles 68.20 45.00 66.80
    sine-rule ratios: 7.615773 7.615773 7.615773
    cosine rule gives c = 7.000000  (measured 7.000000)
  sides 8.0000 10.0000 6.0000  angles 53.13 90.00 36.87
    sine-rule ratios: 10.000000 10.000000 10.000000
    cosine rule gives c = 6.000000  (measured 6.000000)
  sides 8.5440 6.4031 7.6158  angles 74.54 46.25 59.22
    sine-rule ratios: 8.864811 8.864811 8.864811
    cosine rule gives c = 7.615773  (measured 7.615773)

Block 2 - the common ratio is the circumcircle diameter
  a/sin A = 7.615773
  2R      = 7.615773

Block 3 - area two ways, and Pythagoras as a special case
  1/2 ab sin C = 17.500000,  Heron = 17.500000
  1/2 ab sin C = 24.000000,  Heron = 24.000000
  right-angled triangle: largest angle = 90.000000
    6^2 + 8^2 = 100, 10^2 = 100

Block 4 - the ambiguous case, all four outcomes
  A=30, a=5,  b=8   (a < b, sin B < 1)     -> 2 triangle(s)
      B=  53.1301  C=  96.8699  c=   9.9282
      B= 126.8699  C=  23.1301  c=   3.9282
  A=30, a=4,  b=8   (a is exactly half b)  -> 1 triangle(s)
      B=  90.0000  C=  60.0000  c=   6.9282
  A=30, a=3,  b=8   (a too short to reach) -> 0 triangle(s)
  A=30, a=10, b=8   (a >= b)               -> 1 triangle(s)
      B=  23.5782  C= 126.4218  c=  16.0934

triangle_rules: passed
```

Block 4 walks the whole table in section 5. Note the third case returns an empty list rather than raising or returning a nonsense triangle — "no triangle exists" is a correct answer, and a solver that hides it is worse than one that says so.

## Common pitfalls and traps

- **Taking the calculator's $\sin^{-1}$ as the only answer.** This is the ambiguous case, and it is the single biggest source of lost marks in this topic. Always ask whether $180° - B$ also works.
- **Using the sine rule when the cosine rule is needed.** With SAS, the sine rule has two unknowns in one equation and cannot start. Check what you know before choosing.
- **Mislabelling.** $a$ is the side **opposite** $A$. Getting this wrong produces a plausible number from a wrong equation.
- **Finding the largest angle with the sine rule.** Because $\sin$ cannot distinguish an angle from its supplement, resolve the **largest** angle with the *cosine* rule — $\cos$ is negative for obtuse angles, so it is unambiguous — then use the sine rule for the rest.
- **Heron's formula on near-degenerate triangles.** When a triangle is very thin, $s - a$ is a small difference of large numbers and loses precision catastrophically. A numerically stable variant exists and should be used in production code.
- **Forgetting to check $A + B < 180°$.** A candidate angle from the sine rule is only a triangle if a positive third angle remains.

## Check your understanding

1. In triangle $ABC$, $A = 40°$, $B = 75°$ and $a = 12$. Find $b$.
2. In triangle $PQR$, $p = 7$, $q = 9$ and $R = 52°$. Find $r$.
3. A triangle has sides $5$, $7$, $10$. Find its largest angle, and say why you chose the rule you did.
4. Given $A = 40°$, $a = 6$, $b = 8$: how many triangles exist? Justify from the table in section 5.
5. Find the area of a triangle with sides $13$, $14$, $15$.

<details><summary>Answers — open only after an attempt</summary>

1. Sine rule: $\frac{b}{\sin 75°} = \frac{12}{\sin 40°}$, so $b = \frac{12\sin 75°}{\sin 40°} \approx \frac{12 \times 0.9659}{0.6428} \approx 18.03$.
2. Cosine rule (SAS): $r^2 = 7^2 + 9^2 - 2(7)(9)\cos 52° = 49 + 81 - 126(0.6157) \approx 130 - 77.57 = 52.43$, so $r \approx 7.24$.
3. The largest angle is opposite the longest side, $10$. Use the **cosine** rule: $\cos\theta = \frac{5^2 + 7^2 - 10^2}{2(5)(7)} = \frac{25 + 49 - 100}{70} = \frac{-26}{70} \approx -0.3714$, so $\theta \approx 111.8°$. The cosine rule is chosen because the negative cosine identifies the obtuse angle unambiguously — the sine rule could not distinguish $111.8°$ from $68.2°$.
4. $\sin B = \frac{8\sin 40°}{6} \approx \frac{5.142}{6} \approx 0.857 < 1$, and $a = 6 < b = 8$. So the fourth row applies: **two** triangles, with $B \approx 59.0°$ or $B \approx 121.0°$.
5. $s = \frac{13+14+15}{2} = 21$. Area $= \sqrt{21 \times 8 \times 7 \times 6} = \sqrt{7056} = 84$.

**And the prediction from section 4:** $B = 53.13°$ is *an* answer, not *the* answer. Since $\sin(180° - B) = \sin B$, $B = 126.87°$ also satisfies $\sin B = 0.8$. With $A = 30°$ that leaves $C = 23.13° > 0$, so it is a valid triangle. Here $a = 5 < b = 8$, so the table predicts two — and the lab confirms it.
</details>

## Practice — independent task

Implement `solve_triangle(**known)` accepting any three of $a, b, c, A, B, C$ and returning **every** consistent triangle.

1. Dispatch on which three are known: SSS and SAS to the cosine rule; ASA and AAS to the sine rule; SSA to your ambiguous-case handler.
2. Return a **list**, so SSA can return zero, one or two triangles and every other case returns exactly one. A uniform return type avoids a caller forgetting the ambiguous case.
3. Reject inconsistent input: angles summing to more than $180°$; sides violating the triangle inequality; AAA (shape without scale — infinitely many similar triangles).
4. For every triangle returned, assert **both** rules hold and the angles sum to $180°$.
5. Cross-check against coordinates: reconstruct the vertices from your solution, recompute all six quantities from the coordinates, and confirm they match the input to within `1e-9`.

**Edge cases:** the exact-right-angle SSA case where $\sin B = 1$ — make sure you return one triangle, not two identical ones; a nearly degenerate triangle with angles like $179.9°$, $0.05°$, $0.05°$ — report what precision you actually get; AAA input.

**Done when:** all five SSA rows from section 5's table return the predicted count, your coordinate cross-check passes for at least ten triangles, and you can state what your function does with AAA and why that is the right behaviour.

## Tradeoffs, limits and extensions

**Numerical stability is a real concern here.** `acos` is ill-conditioned near $\pm 1$: its derivative is unbounded, so a tiny error in the cosine becomes a large error in the angle for angles near $0°$ or $180°$. For thin triangles, an implementation based on `atan2` is considerably more accurate. The lab clamps to $[-1, 1]$ before calling `acos`, which prevents a domain error from rounding, but clamping hides the underlying loss of precision rather than fixing it.

**Heron's formula has a stable variant.** Sorting $a \ge b \ge c$ and computing
$\frac14\sqrt{(a+(b+c))(c-(a-b))(c+(a-b))(a+(b-c))}$
avoids the cancellation that the textbook form suffers on thin triangles. Kahan's analysis of this is the standard reference.

**Beyond the plane.** On a sphere both rules have analogues — the spherical sine and cosine rules — with the sides measured as angles rather than lengths. The spherical cosine rule is what [[01-latitude-and-longitude|latitude and longitude]] uses to compute great-circle distances.

## Before moving on

You are done with this lesson when you can:

- Derive the sine rule by dropping one perpendicular, and the cosine rule from coordinates.
- Pick the right rule from the known parts without hesitating.
- Work through the ambiguous case and say how many triangles exist before computing them.
- Explain why the largest angle should be found with the cosine rule.

**Recap for later lookup:** $\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R$; $c^2 = a^2 + b^2 - 2ab\cos C$, with Pythagoras the case $C = 90°$; $\cos C = \frac{a^2+b^2-c^2}{2ab}$; area $= \tfrac12 ab\sin C = \sqrt{s(s-a)(s-b)(s-c)}$. SSA is ambiguous exactly when $\sin B < 1$ and the side opposite the known angle is shorter than the adjacent one.

**Next:** [[04-bearings|Bearings]] — these rules applied to navigation, where the angles are measured from north and the triangles are journeys.

## Related

- [[02-triangles-and-polygons|Triangles and Polygons]] — where SSA was first rejected as a congruence criterion
- [[02-graphs-and-identities|Graphs and Identities]] — the supplement identity that causes the ambiguity
- [[01-circle-theorems|Circle Theorems]] — the circumcircle the common ratio measures
- [[01-latitude-and-longitude|Latitude and Longitude]] — the spherical versions of both rules
