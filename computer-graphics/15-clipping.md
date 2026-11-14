# Clipping

**[Intermediate]** — Removing everything outside the viewing window before it is drawn: point clipping, the three classes of line, Cohen–Sutherland, midpoint subdivision, Cyrus–Beck and Liang–Barsky, and extending them to a 3D frustum and to Bézier curves.

> Part 1 of the course. The 3D, clip-space version of this lives in [[computer-graphics/02-the-transform-pipeline|note 02]] ("Clip space and NDC") — this note is where the algorithms behind it are worked by hand.

## Before you start

You can find where two lines cross, use a slope $m$, and take a dot product.

**After this note you will be able to:**
1. Compute 4-bit region codes and apply Cohen–Sutherland's accept/reject/clip loop by hand.
2. Clip the same line with Liang–Barsky and get the same answer.
3. Explain Cyrus–Beck and why Liang–Barsky is its rectangular special case.
4. Describe how to clip against a 3D frustum and how to clip a Bézier curve.

## The kid version

You're looking at a big drawing through a small window cut in a piece of card. Only what shows through the hole matters, so before you bother tracing anything, you throw away the parts outside the hole. Some lines are completely inside (keep them), some are completely off to one side (bin them without a thought), and only the ones that poke through the edge of the hole need scissors.

**Where the analogy stops working.** A line can pass *near* a corner of the window without going through it. By eye you'd spot that instantly; the algorithm may have to cut it once or twice before it can prove nothing is left.

## Terms used in clipping

1. **Clipping**: This is the removal of objects, lines or parts of lines that lie outside the viewing window, before the view is drawn. It saves work and guarantees only the visible part is drawn.
2. **Clipping window**: This is also known as the **window**. This is the rectangle with edges $xw_{min}$, $xw_{max}$, $yw_{min}$, $yw_{max}$ that the picture is clipped to.
3. **Region code**: This is also known as an **outcode**. This is the 4-bit code that says which side(s) of the window a point is beyond.
4. **Trivial accept**: This is keeping a whole line without calculation, because both its end points are inside.
5. **Trivial reject**: This is discarding a whole line without calculation, because both end points are beyond the same edge.
6. **Parametric line**: This is a line written as $P(t) = P_0 + t(P_1 - P_0)$, so $t = 0$ is the start, $t = 1$ is the end, and values between are points on the segment.
7. **Outward normal**: This is a vector perpendicular to a window edge, pointing out of the window.
8. **Entering / leaving**: These describe whether a line, travelling from $P_0$ to $P_1$, is crossing a window edge from outside to inside (entering) or inside to outside (leaving).

## 1. Point clipping

**A point is kept only if it is inside the window in both directions.** If either condition fails, it is removed.

$$xw_{min} \le x \le xw_{max} \qquad\text{and}\qquad yw_{min} \le y \le yw_{max}$$

Other kinds of clipping exist too: line, polygon, curve and text clipping.

## 2. The three classes of line

1. **Visible** — both end points inside the window. Drawn as is.
2. **Non-visible** — the whole line is outside. Rejected. *Sufficient* condition: both end points are beyond the same side ($x_1, x_2 > x_{max}$; or both $< x_{min}$; or both $> y_{max}$; or both $< y_{min}$).
3. **Partially visible** (the clipping case) — neither of the above. This is where an algorithm is needed.

The algorithms covered: **Cohen–Sutherland**, **midpoint subdivision**, **Cyrus–Beck** and **Liang–Barsky**.

## 3. Cohen–Sutherland

### Step 1: region codes

**The window and the lines extending its edges split the plane into 9 regions.** Each gets a 4-bit code, in the order **Top, Bottom, Right, Left** (TBRL). A bit is 1 when the point is beyond that edge:

1. **Top** is 1 if $y > yw_{max}$.
2. **Bottom** is 1 if $y < yw_{min}$.
3. **Right** is 1 if $x > xw_{max}$.
4. **Left** is 1 if $x < xw_{min}$.

```
 1001 | 1000 | 1010
------+------+------
 0001 | 0000 | 0010     ← 0000 is the window itself
------+------+------
 0101 | 0100 | 0110
```

### Step 2: the loop

1. Compute codes $r_1$, $r_2$ for the end points.
2. **If $r_1 \mathbin{\text{OR}} r_2 = 0000$** — both inside — **accept** the whole line. Stop.
3. **Else if $r_1 \mathbin{\text{AND}} r_2 \ne 0000$** — both beyond the same edge — **reject** the whole line. Stop.
4. **Otherwise** (AND is 0000 but the line was not accepted) part of the line **may** be inside, so clip:
   1. Pick an end point that is outside (code not 0000).
   2. Find where the line crosses the edge named by a 1 bit in that code.
   3. **Replace that end point with the intersection and recompute its code.**
   4. Go back to step 2.

> **"AND = 0000" means the line *may* be inside, not that it is.** A line can pass near a corner without entering; it gets clipped once or twice and then rejected when the new end point's code still shows it outside.

### Intersection formulas

With slope $m = \frac{y_1 - y_0}{x_1 - x_0}$, taking an outside end point:

| Edge | Fixed | The other coordinate |
|---|---|---|
| Top | $y = y_{max}$ | $x = x_1 + (y_{max} - y_1)/m$ |
| Bottom | $y = y_{min}$ | $x = x_1 + (y_{min} - y_1)/m$ |
| Right | $x = x_{max}$ | $y = y_1 + m(x_{max} - x_1)$ |
| Left | $x = x_{min}$ | $y = y_1 + m(x_{min} - x_1)$ |

### Worked — window $x \in [2, 8]$, $y \in [2, 6]$

| Line | Start code | End code | Test | Result |
|---|---|---|---|---|
| (3,3) to (6,5) | 0000 | 0000 | Both 0000 | **Accept as is** |
| (0,0) to (1,5) | 0101 | 0001 | AND = 0001 | **Reject** |
| (0,4) to (6,8) | 0001 | 1000 | AND = 0000 | **Clip** |

**Clipping $(0,4)$ to $(6,8)$**, $m = 4/6 = 2/3$:

| Step | What happens | Result |
|---|---|---|
| 1 | Start (0,4) is Left. Cut at $x = 2$: $y = 4 + \tfrac23(2 - 0) = 5.33$ | New start (2, 5.33), code 0000 |
| 2 | End (6,8) is Top. Cut at $y = 6$: $x = 6 + (6 - 8)/\tfrac23 = 3$ | New end (3, 6), code 0000 |
| 3 | Both codes 0000 | **Accept: (2, 5.33) to (3, 6)** |

### Worked — window $(4,4)$ to $(10,8)$

| Line | End points | Codes | OR | AND | Result |
|---|---|---|---|---|---|
| 1 | (5,5), (7,7) | 0000, 0000 | 0000 | 0000 | Visible |
| 2 | (7,9), (11,4) | 1000, 0010 | 1010 | 0000 | Clipping case |
| 3 | (1,5), (4,1) | 0001, 0100 | 0101 | 0000 | Clipping case → rejected |

**Line 2:** $m = (4 - 9)/(11 - 7) = -5/4$. Top: $x = 7 + (8 - 9)/(-5/4) = 7.8$, giving $(7.8, 8)$. Right: $y = 4 + (10 - 11)(-5/4) = 5.25$, giving $(10, 5.25)$. **Clipped line: $(7.8, 8)$ to $(10, 5.25)$.** Starting from the other end point gives the same $y = 5.25$.

**Line 3 is the subtle one.** The conclusion "invisible" is right, **but the AND test does not reject it at once (AND = 0000).** The algorithm clips against Left: $m = -4/3$, $y = 5 + (4 - 1)(-4/3) = 1$, giving $(4, 1)$ with code 0100. **Now both end points have the Bottom bit set, so AND ≠ 0000 and it is rejected.** In an exam, show that step.

### Worked — several clips, window $x \in [2,12]$, $y \in [2,8]$

| Line | Codes | Steps | Result |
|---|---|---|---|
| (−1,5) to (15,11) | 0001, 1010 | Clip Left at $x = 2$ → (2, 6.125), 0000. Other end still 1010: clip Top at $y = 8$ → (7, 8), 0000 | (2, 6.125) to (7, 8) |
| (0,10) to (14,−2) | 1001, 0110 | Clip Top → (2.33, 8). Clip Bottom for the other end → (9.33, 2) | (2.33, 8) to (9.33, 2) |
| (−3,9) to (1,12) | 1001, 1001 | AND = 1001 | Rejected immediately |

**The first line shows why it is a loop:** after the Left clip the line is still not accepted, because the other end point is beyond both Top and Right and needs its own clip. **Recompute the code after every clip, and keep going until accept or reject.** Testing bits in a different order gives the same final line.

## 4. Midpoint subdivision

**Do Cohen–Sutherland's accept/reject tests, but find the intersection by repeated halving instead of the slope formula.** It needs only additions and division by 2 (a shift), which is why it suits hardware.

1. Compute codes. OR = 0000 → accept. AND ≠ 0000 → reject.
2. Otherwise find the midpoint $M = \left(\frac{x_1 + x_2}{2}, \frac{y_1 + y_2}{2}\right)$ and treat $P_1M$ and $MP_2$ as separate lines. Repeat on each.
3. Stop splitting a piece when it is shorter than about a pixel — it is then a point, accepted or rejected by its own code.
4. The visible pieces join into the clipped line; the outermost accepted end points are the clipped end points.

On Line 2 above it converges to about $(7.80, 8.00)$ and $(10, 5.25)$ — matching the slope method.

## 5. Cyrus–Beck

**A parametric method that works for any convex window, not just rectangles.** (Spelled *Cyrus–Beck*, not "Cyrus Back".)

Write the line as $P(t) = P_0 + tD$, with $D = P_1 - P_0$ and $t \in [0, 1]$. **For each window edge $i$, take an outward normal $N_i$ and any point $P_{E_i}$ on that edge** — any point on the edge, *not* an intersection with your line. The sign of $N_i \cdot (P - P_{E_i})$ tells you where $P$ is: **$> 0$ outside, $< 0$ inside, $= 0$ on the edge.**

**The crossing is where that dot product is zero.** Solving for $t$:

$$t_i = \frac{N_i \cdot (P_{E_i} - P_0)}{N_i \cdot D} \;=\; \frac{-N_i\cdot(P_0 - P_{E_i})}{N_i \cdot D}$$

**Then classify each edge:**
- **$N_i \cdot D < 0$**: entering. Keep the **largest** such $t$ as $t_E$ (start at 0).
- **$N_i \cdot D > 0$**: leaving. Keep the **smallest** such $t$ as $t_L$ (start at 1).
- **$N_i \cdot D = 0$**: parallel to that edge. Reject if the line lies outside it.
- **If $t_E > t_L$, reject.** Otherwise the visible part runs from $P(t_E)$ to $P(t_L)$.

> **Stopping after finding $t$ is the usual incomplete answer.** The classification into entering/leaving and the $t_E > t_L$ test are the algorithm.

## 6. Liang–Barsky

**Liang–Barsky is a parametric method for rectangular windows: turn each window edge into a limit on $t$, and the visible part is the range of $t$ that satisfies all four.**

Let $dx = x_1 - x_0$, $dy = y_1 - y_0$, so $P(t) = (x_0 + t\,dx,\; y_0 + t\,dy)$. A point is inside when

$$xw_{min} \le x_0 + t\,dx \le xw_{max}\qquad\text{and}\qquad yw_{min} \le y_0 + t\,dy \le yw_{max}$$

**Each of the four inequalities rearranges into $t\,p_k \le q_k$.** For the left edge, $x_0 + t\,dx \ge xw_{min}$ becomes $-t\,dx \le x_0 - xw_{min}$:

| k | Edge | $p_k$ | $q_k$ |
|---|---|---|---|
| 1 | Left | $-dx$ | $x_0 - xw_{min}$ |
| 2 | Right | $dx$ | $xw_{max} - x_0$ |
| 3 | Bottom | $-dy$ | $y_0 - yw_{min}$ |
| 4 | Top | $dy$ | $yw_{max} - y_0$ |

**What $p_k$ tells you:**
- **$p_k = 0$**: parallel to that edge. If $q_k < 0$ it is outside — reject. Otherwise no limit.
- **$p_k < 0$**: entering. The limit is $t \ge q_k/p_k$ (the inequality flips when dividing by a negative).
- **$p_k > 0$**: leaving. The limit is $t \le q_k/p_k$.

**Steps:**
1. Compute $p_k$, $q_k$ for the four edges.
2. Any $p_k = 0$ with $q_k < 0$ → reject.
3. $t_E = \max(0,\; q_k/p_k \text{ for every } p_k < 0)$.
4. $t_L = \min(1,\; q_k/p_k \text{ for every } p_k > 0)$.
5. **$t_E > t_L$ → reject.** Otherwise the clipped line is $P(t_E)$ to $P(t_L)$. (Equal means it only touches the window at one point, such as a corner.)

### Worked — window $x \in [2,8]$, $y \in [2,6]$, line $(0,4)$ to $(6,8)$

$dx = 6$, $dy = 4$.

| k | Edge | $p_k$ | $q_k$ | $q_k/p_k$ | Type | $t_E$ / $t_L$ after |
|---|---|---|---|---|---|---|
| 1 | Left | −6 | −2 | 1/3 | Entering | $t_E = 1/3$ |
| 2 | Right | 6 | 8 | 4/3 | Leaving | $t_L = 1$ |
| 3 | Bottom | −4 | 2 | −1/2 | Entering | $t_E = 1/3$ |
| 4 | Top | 4 | 2 | 1/2 | Leaving | $t_L = 1/2$ |

$t_E = 1/3 < t_L = 1/2$: accept. $P(1/3) = (2, 5.33)$, $P(1/2) = (3, 6)$ — **the Cohen–Sutherland answer.**

**Two rejections (same window):**
- $(0,0)$ to $(1,5)$: Left gives $p = -1$, $q = -2$, $r = 2$, so $t_E = 2$. Right gives $t_L = \min(1, 8) = 1$. $2 > 1$ → reject.
- $(3,1)$ to $(7,1)$: $dy = 0$, so Bottom has $p = 0$, $q = 1 - 2 = -1 < 0$. Parallel and outside → reject.

**Worked — the several-clips line again:** $(-1,5)$ to $(15,11)$, window $[2,12] \times [2,8]$, $dx = 16$, $dy = 6$. Ratios: Left $3/16$ (entering), Right $13/16$ (leaving), Bottom $-1/2$ (entering), Top $1/2$ (leaving). $t_E = 3/16$, $t_L = 1/2$ → $(2, 6.125)$ to $(7, 8)$. **Same as Cohen–Sutherland, with no repeated recomputation.**

### Why it is faster, and how it relates to Cyrus–Beck

**Cohen–Sutherland may intersect, recompute a code and repeat several times for one line. Liang–Barsky does four divisions, keeps two numbers, and computes the end points once.**

**Liang–Barsky *is* Cyrus–Beck for an axis-aligned rectangle.** The outward normals are $(-1,0)$, $(1,0)$, $(0,-1)$, $(0,1)$, so the dot products collapse into $p_k$ and $q_k$: for the left edge, $N\cdot D = (-1,0)\cdot(dx,dy) = -dx = p_1$.

| | Cohen–Sutherland | Liang–Barsky | Cyrus–Beck |
|---|---|---|---|
| Window | Rectangle | Rectangle | Any convex shape |
| Main tool | 4-bit region codes | $p_k$, $q_k$, then $t_E$, $t_L$ | Dot products with edge normals, then $t_E$, $t_L$ |
| Intersections | Possibly several per line | Two, once, at the end | Two, once, at the end |
| Best when | Most lines are clearly in or out | Many lines need clipping | The window isn't a rectangle |

> **Exam tip:** use the method the question names (SSG 511 Q5 names Cohen–Sutherland). **Liang–Barsky is the ideal way to check your answer**, because it is an independent calculation of the same clipped line.

## 7. Clipping against a 3D view frustum

**The view frustum is a truncated pyramid with six planes: left, right, bottom, top, near, far.** Extend Cohen–Sutherland to 3D:

1. Use a **6-bit region code**, one bit per plane, set when the point is outside that plane.
2. Accept if both codes are 000000; reject if their AND is not 000000.
3. Otherwise pick an outside end point and a plane named by one of its 1 bits, and intersect. With $P(t) = P_0 + t(P_1 - P_0)$ and a plane such as $x = xw$: $t = (xw - x_0)/(x_1 - x_0)$, then $y$ and $z$ follow from the same $t$.
4. Replace the end point, recompute its code, repeat.

**It is much simpler after the perspective transformation.** In the canonical view volume the planes become $x = \pm1$, $y = \pm1$, $z = \pm1$; in homogeneous clip coordinates the test is $-w \le x, y, z \le w$ — exactly what GPUs do → [[computer-graphics/02-the-transform-pipeline|note 02]]. **Cyrus–Beck with six planes also works, because the frustum is convex.**

## 8. Clipping a Bézier curve against a rectangle

**Use the convex-hull property** (the curve always lies inside the hull of its control points) **and de Casteljau splitting** → [[computer-graphics/17-curves-bezier-and-b-splines|note 17]]:

1. If the control points' bounding box is entirely inside the window, draw the whole curve.
2. If it is entirely outside, discard the curve.
3. Otherwise split at $t = \tfrac12$ and repeat on each half.
4. When a piece is flat enough (or about a pixel long), treat it as a straight line and clip it with Cohen–Sutherland.

## Runnable check

```python
# liang_barsky.py — run: python3 liang_barsky.py
def liang_barsky(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    dx, dy = x1 - x0, y1 - y0
    tE, tL = 0.0, 1.0
    for p, q in [(-dx, x0 - xmin), (dx, xmax - x0), (-dy, y0 - ymin), (dy, ymax - y0)]:
        if p == 0:
            if q < 0:
                return None          # parallel and outside
        elif p < 0:
            tE = max(tE, q / p)      # entering
        else:
            tL = min(tL, q / p)      # leaving
    if tE > tL:
        return None
    return (x0 + tE * dx, y0 + tE * dy), (x0 + tL * dx, y0 + tL * dy)

print(liang_barsky(0, 4, 6, 8, 2, 2, 8, 6))     # ((2.0, 5.33...), (3.0, 6.0))
print(liang_barsky(7, 9, 11, 4, 4, 4, 10, 8))   # ((7.8, 8.0), (10.0, 5.25))
print(liang_barsky(1, 5, 4, 1, 4, 4, 10, 8))    # None
```

## Common pitfalls

1. **Treating AND = 0000 as "visible".** It is "maybe".
2. **Forgetting to recompute the code** after each clip.
3. **Taking $P_E$ as the intersection point** in Cyrus–Beck. It is any point on the edge.
4. **A stray $t$ in the Cyrus–Beck denominator.** It is $N_i \cdot D$, nothing else.
5. **Flipping the inequality the wrong way** in Liang–Barsky: dividing by negative $p_k$ flips $\le$ to $\ge$, which is why entering edges give lower bounds.
6. **Garbled point-clipping conditions.** Both $xw_{min} \le x \le xw_{max}$ *and* $yw_{min} \le y \le yw_{max}$ must hold.

## Check your understanding

1. Give the region codes for $(1, 9)$ and $(13, 1)$ against the window $[2,12] \times [2,8]$. Can the line be trivially rejected?
2. Why does Liang–Barsky start $t_E$ at 0 and $t_L$ at 1?
3. Why can Cyrus–Beck not clip against an L-shaped window?

<details><summary>Answers (after your attempt)</summary>

1. $(1, 9)$ is Top and Left: 1001. $(13, 1)$ is Bottom and Right: 0110. AND = 0000, so no — it needs clipping (and here it does cross the window).
2. The segment itself only exists for $t \in [0, 1]$; the edges can only shrink that range.
3. The method relies on each edge's inside being a half-plane and the window being their intersection — true only for convex shapes. An L-shape can make a line enter, leave and enter again.

</details>

## Practice — independent tasks

1. **Exam Q5b** — window from $A(-3,1)$ to $C(2,6)$; five lines. Codes first, accept/reject tests, intersections only for lines that pass neither. Then check every one with the Liang–Barsky code above. → [[computer-graphics/19-ssg-511-question-bank|question bank]]
2. **Assignment B-7.5** — $P_1(40,15)$–$P_2(75,45)$ and $P_3(70,20)$–$P_4(100,10)$ against window $(50,10)$–$(80,40)$.
3. **Write `cohen_sutherland(...)`** and show it agrees with `liang_barsky` on 1,000 random lines. **Done when** every line matches to within $10^{-9}$.

## Before moving on

**Next:** [[computer-graphics/16-2d-and-3d-transformations|2D and 3D Transformations]].

## Related
- [[computer-graphics/02-the-transform-pipeline|The Transform Pipeline]] — clipping in homogeneous clip space
- [[computer-graphics/17-curves-bezier-and-b-splines|Curves]] — the de Casteljau split used above
- [[computer-graphics/index|Computer graphics map]]
