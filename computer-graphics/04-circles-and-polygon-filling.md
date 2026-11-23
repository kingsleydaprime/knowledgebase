---
id: b638438e-35cc-4fa8-b880-be87378ae2df
---

# Circles and Polygon Filling

Circles and filled shapes both have to be drawn on the pixel grid with whole numbers.

## Before you start
<!-- bite: 40f55116-6732-497e-ade9-a693e2726f24 -->

You can trace a Bresenham line table ([[computer-graphics/03-line-drawing-and-antialiasing|note 03]]) and you know $x^2 + y^2 = r^2$ is a circle.

**After this note you will be able to:**
1. Use eight-way symmetry to draw a full circle from one octant.
2. Trace the midpoint circle algorithm by hand and derive its update rules.
3. Fill a polygon with the scan-line algorithm, handling vertices correctly.
4. Choose between flood fill and boundary fill, and between 4- and 8-connected.

## What circle drawing and polygon filling are
<!-- bite: cb3f1606-77aa-47e1-8c83-06b1c017270d -->

This lesson covers two jobs: drawing a circle on the pixel grid using only whole numbers, and filling the inside of a shape with colour. Every round button in an app and every coloured shape in a drawing program needs both.

Next: the kid version, then the words you need.

## The kid version
<!-- bite: 45490b6f-2a46-46c6-9e12-d8ee4eb741c2 -->

A circle looks the same if you flip it left-right, up-down, or across a diagonal. So you only need to draw one-eighth of it carefully — a slice like a pizza wedge — and then copy it eight ways. For each step along that slice you ask the same "which square is closer?" question as with lines.

Filling is colouring in. Either you go row by row like a printer, colouring between the points where the row crosses the outline (scan-line), or you drop a tin of paint inside and let it spread until it hits the edge (seed fill).

**Where the analogy stops working.** Paint that spreads diagonally can squeeze through a gap where two outline pixels only touch at a corner. Real paint wouldn't; an 8-connected fill does.

## Terms used in circles
<!-- bite: a965ad43-07e9-4c3d-85f6-687e477fce2a -->

1. **Octant**: This is one eighth of the circle, a 45° slice. The algorithms compute the octant from $(0, r)$ to the point where $x = y$.
2. **Eight-way symmetry**: This is the fact that each point $(x, y)$ on a circle centred at the origin gives seven more by swapping and negating coordinates.
3. **Circle function**: This is $f(x, y) = x^2 + y^2 - r^2$. It is negative inside the circle, zero on it, and positive outside.
## Terms used in filling
<!-- bite: 09f5fba2-1ed0-43e8-ad24-4fc5e1a5e38c -->

4. **Scan line**: This is one horizontal row of pixels, at a fixed $y$.
5. **Edge table**: This is a list of a polygon's edges, each stored with its top $y$, its $x$ at the bottom, and its inverse slope $dx/dy$.
6. **Active edge table**: This is the subset of edges that cross the current scan line.
7. **Seed**: This is the one pixel inside the region from which a flood or boundary fill starts.
8. **4-connected**: This describes moving to the four neighbours up, down, left and right.
9. **8-connected**: This describes moving to those four plus the four diagonal neighbours.

## 1. Why not just use the equation?
<!-- bite: 17d4c522-7ac1-4545-a0fc-87bc9c8d59f1 -->

Drawing $x^2 + y^2 = r^2$ directly has problems:

- **$y = \pm\sqrt{r^2 - x^2}$ needs a square root per pixel**, and the pixels come out unevenly spaced — big gaps where the circle is steep.
- **The polar form $x = r\cos\theta$, $y = r\sin\theta$ needs trigonometry**, which is slow.

**So, as with lines, use incremental integer algorithms.**

## 2. Eight-way symmetry
<!-- bite: 763c881d-fee0-472d-bcfa-8978343c0684 -->

**Compute one octant — from $(0, r)$ at the top to the 45° point where $x = y$ — and each computed point gives eight.** For centre $(x_c, y_c)$:

```text
(xc + x, yc + y)   (xc - x, yc + y)   (xc + x, yc - y)   (xc - x, yc - y)
(xc + y, yc + x)   (xc - y, yc + x)   (xc + y, yc - x)   (xc - y, yc - x)
```

## 3. The midpoint circle algorithm
<!-- bite: 18a3ab80-e8e6-4aca-8c95-226e3fceb6b5 -->

**Start at $(0, r)$ and move clockwise.** At each step $x$ increases by 1, and you choose between **E** $= (x_k + 1, y_k)$ and **$\mathrm{SE}$** $= (x_k + 1, y_k - 1)$.

**Evaluate the circle function at the midpoint of the two candidates:**

$$p_k = f\!\left(x_k + 1,\; y_k - \tfrac12\right) = (x_k + 1)^2 + \left(y_k - \tfrac12\right)^2 - r^2$$

- **$p_k < 0$**: the midpoint is inside the circle, so E is closer. Plot $(x_k + 1, y_k)$.
- **$p_k \ge 0$**: $\mathrm{SE}$ is closer. Plot $(x_k + 1, y_k - 1)$.

## Midpoint circle: the start value and updates
<!-- bite: c34a71b1-18d1-4bf2-8a98-65e3e1e05dad -->

**Start value:** $p_0 = f(1, r - \tfrac12) = \tfrac54 - r$. **For integer $r$, use $p_0 = 1 - r$** (the $\tfrac14$ never changes a sign decision, since everything else is an integer).

**Updates** ($x_{k+1}$, $y_{k+1}$ are the *new* coordinates):

$$p_{k+1} = \begin{cases} p_k + 2x_{k+1} + 1 & \text{E chosen} \\ p_k + 2x_{k+1} + 1 - 2y_{k+1} & \text{SE chosen}\end{cases}$$

**Where they come from:** subtract $f$ at the old midpoint from $f$ at the new one. For E the change is $(x_k + 2)^2 - (x_k + 1)^2 = 2x_k + 3 = 2x_{k+1} + 1$. For $\mathrm{SE}$ there is an extra $(y_k - \tfrac32)^2 - (y_k - \tfrac12)^2 = -2y_k + 2 = -2y_{k+1}$.

## Midpoint circle: the steps
<!-- bite: f8dd0342-956c-4515-90af-ff24bf5dda9a -->
1. Input $r$ and centre $(x_c, y_c)$.
2. Set $x = 0$, $y = r$, $p = 1 - r$. Plot the eight symmetric points.
3. While $x < y$: $x \mathrel{+}= 1$. If $p < 0$, $p \mathrel{+}= 2x + 1$; otherwise $y \mathrel{-}= 1$ and $p \mathrel{+}= 2(x - y) + 1$. Plot the eight points.

## Midpoint circle worked: r = 10, centre at the origin
<!-- bite: dc84d96d-8cb0-4286-b7c5-1bbaf6045c04 -->

$p_0 = 1 - 10 = -9$.

| k | $p_k$ | Choice | Next $(x, y)$ | $p_{k+1}$ |
|---|---|---|---|---|
| start | | | (0, 10) | |
| 0 | −9 | E | (1, 10) | −9 + 2(1) + 1 = −6 |
| 1 | −6 | E | (2, 10) | −6 + 2(2) + 1 = −1 |
| 2 | −1 | E | (3, 10) | −1 + 2(3) + 1 = 6 |
| 3 | 6 | $\mathrm{SE}$ | (4, 9) | 6 + 2(4) + 1 − 2(9) = −3 |
| 4 | −3 | E | (5, 9) | −3 + 2(5) + 1 = 8 |
| 5 | 8 | $\mathrm{SE}$ | (6, 8) | 8 + 2(6) + 1 − 2(8) = 5 |
| 6 | 5 | $\mathrm{SE}$ | (7, 7) | 5 + 2(7) + 1 − 2(7) = 6 |

**Stop at $(7, 7)$ because $x = y$.** Octant pixels: $(0,10), (1,10), (2,10), (3,10), (4,9), (5,9), (6,8), (7,7)$. Mirror them for the full circle.

## Midpoint circle worked: r = 13
<!-- bite: 757e3702-653c-4917-9aac-edf7ee1c59d1 -->

$p_0 = -12$.

| x | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| y | 13 | 13 | 13 | 13 | 12 | 12 | 12 | 11 | 10 | 9 |
| p | −12 | −9 | −4 | 3 | −12 | −1 | 12 | 5 | 2 | 3 |

The octant ends at $(9, 9)$ on the diagonal.

## Midpoint circle: runnable check
<!-- bite: 54d410f1-ab79-4555-b744-62b3cf643eec -->

```python
# midpoint_circle.py — run: python3 midpoint_circle.py
def midpoint_circle_octant(r):
    x, y, p = 0, r, 1 - r
    pts = [(x, y)]
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        pts.append((x, y))
    return pts

def eight_way(xc, yc, pts):
    out = set()
    for x, y in pts:
        out |= {(xc+x, yc+y), (xc-x, yc+y), (xc+x, yc-y), (xc-x, yc-y),
                (xc+y, yc+x), (xc-y, yc+x), (xc+y, yc-x), (xc-y, yc-x)}
    return out

print(midpoint_circle_octant(10))
print(len(eight_way(0, 0, midpoint_circle_octant(10))))
```

**Expected:** `[(0, 10), (1, 10), (2, 10), (3, 10), (4, 9), (5, 9), (6, 8), (7, 7)]`, then `56` — the full-circle pixel count. That is less than $8 \times 8 = 64$ because points on the axes and on the diagonal map onto each other, and the set merges the duplicates.

## 4. Bresenham's circle algorithm
<!-- bite: 916488de-ca52-463b-b7c8-b9448234feb8 -->

**Same structure, but the decision compares the squared distances of the two candidates from the circle:**

$$d = \left[(x+1)^2 + y^2 - r^2\right] + \left[(x+1)^2 + (y-1)^2 - r^2\right]$$

When $d < 0$, E is closer. Simplifying, with $(x, y)$ the pixel just plotted (before moving):

- **Start:** $d_0 = 3 - 2r$.
- **$d < 0$:** next pixel $(x + 1, y)$, and $d \mathrel{+}= 4x + 6$.
- **$d \ge 0$:** next pixel $(x + 1, y - 1)$, and $d \mathrel{+}= 4(x - y) + 10$.

For $r = 10$ it gives the same octant as the midpoint algorithm — and it does so for $r = 5, 10, 13, 17, 40$ (re-run). **Both use only integer additions.**

## 5. Ellipses
<!-- bite: b669d4c4-4538-47a3-9e89-ab9d09aaf8de -->

**The midpoint idea also works for ellipses**, but an ellipse has only **four-way symmetry**. Compute one quadrant, **split into two regions at the point where the curve's slope passes −1**: in region 1 (slope shallower than −1) step $x$; in region 2 step $y$ — the same "step the long axis" rule as lines.

## 6. Polygon filling
<!-- bite: cf784cbf-df4d-47dd-9800-9e2780ef5699 -->

**Filling a polygon means colouring every pixel inside it.** Two families:

- **Scan-line fill** works from the edges, one horizontal line at a time.
- **Seed fill** (flood fill and boundary fill) starts from one inside pixel and spreads outwards.

## Scan-line algorithm
<!-- bite: c523f024-1ba8-4a2e-8677-68209c3c2ea9 -->

For each scan line $y$ from the polygon's lowest to highest point:

1. Find where the scan line crosses the polygon's edges.
2. Sort the crossings by $x$.
3. **Pair them up — 1st with 2nd, 3rd with 4th — and fill between each pair.** This is the **odd–even rule**: inside between crossings 1 and 2, outside between 2 and 3, inside between 3 and 4.

## Scan-line algorithm: details that matter
<!-- bite: b4f28f6b-1a50-4e4e-8d3c-d017ab6edcab -->

1. **Horizontal edges are ignored.** The edges next to them cover those pixels.
2. **Shared vertices.** A vertex shared by two edges would be counted twice. If the two edges lie on *opposite* sides of the scan line (the outline passes through), count it once. If both lie on the *same* side (a peak or valley), count it twice or not at all. **The common trick: include an edge's lower end, exclude its upper end** — this handles both cases automatically.
3. **Coherence for speed.** Keep an **edge table** with each edge's top $y$, its $x$ at the bottom, and its inverse slope $dx/dy$. On the next scan line, an edge's crossing moves by exactly its inverse slope, **so you add it instead of recomputing.** The edges crossing the current line form the **active edge table**.

## Scan-line worked: a triangle
<!-- bite: 83a7b8e9-052a-4fa4-a4aa-0486479c191d -->

**Worked — triangle $(2,2)$, $(10,2)$, $(6,8)$, scan line $y = 3$:**
- Left edge: $dx/dy = (6 - 2)/(8 - 2) = 0.667$, so it crosses at $x = 2 + 0.667 = 2.67$.
- Right edge: $dx/dy = (6 - 10)/(8 - 2) = -0.667$, so $x = 10 - 0.667 = 9.33$.
- **Fill pixels $x = 3$ to $9$.** (The bottom edge $y = 2$ is horizontal, so it is ignored.)

## Flood fill
<!-- bite: da2c0f45-8f6e-49ef-86b0-a789f27f037b -->

**Replace every connected pixel of the old (interior) colour with the new colour, starting from a seed.** It stops wherever the colour is not the old colour. **Use it when the region has no single-colour boundary** — recolouring an area of an image.

```text
flood_fill(x, y, old, new):      # needs old != new, or it never ends
    if getpixel(x, y) != old: return
    setpixel(x, y, new)
    flood_fill(x + 1, y, old, new)
    flood_fill(x - 1, y, old, new)
    flood_fill(x, y + 1, old, new)
    flood_fill(x, y - 1, old, new)
```

## Boundary fill
<!-- bite: 29b77fbd-6352-4496-84ee-3b99bb8a7ce0 -->

**Start from a seed inside and fill until you reach the boundary colour.** The boundary must be a single colour.

```text
boundary_fill(x, y, fill, boundary):
    c = getpixel(x, y)
    if c != boundary and c != fill:
        setpixel(x, y, fill)
        boundary_fill(x + 1, y, fill, boundary)
        boundary_fill(x - 1, y, fill, boundary)
        boundary_fill(x, y + 1, fill, boundary)
        boundary_fill(x, y - 1, fill, boundary)
```

| | Flood fill | Boundary fill |
|---|---|---|
| Stops when | Colour is no longer the old interior colour | Colour is the boundary colour |
| Needs | A region of one interior colour | An outline of one boundary colour |
| Typical use | Recolouring part of an image | Filling a drawn shape |

## 4-connected versus 8-connected
<!-- bite: af51ec93-1028-42b2-91af-631094e1263f -->

**This is which neighbours the fill spreads to** — what "4-connected polygons, 8-connected polygons" in class notes means.

**The key difference is leaking.** A boundary drawn as a diagonal line has pixels that touch only at corners:

```text
 . . . # .        A 4-connected fill cannot step diagonally,
 . . # . .        so it stays on its side of this line.
 . # . . .        An 8-connected fill steps through the
 # . . . .        corner gaps and leaks out.
```

- **A 4-connected fill is safe with an 8-connected boundary.**
- **An 8-connected fill needs a 4-connected boundary** (no diagonal gaps). It is useful for thin shapes a 4-connected fill would miss.

> **The recursive versions overflow the stack on large regions** — a 1000 × 1000 region is a million nested calls. In practice use an explicit stack or queue, or fill whole horizontal runs at once (a **span fill**).

## Common pitfalls
<!-- bite: cbf74ffc-90f8-4935-9f47-3fdd9d2775a5 -->

1. **Stopping the octant at the wrong place.** Stop when $x \ge y$; going further duplicates the next octant.
2. **Using $p_0 = 5/4 - r$ with integers.** Use $1 - r$.
3. **Counting every shared vertex twice** in scan-line fill — peaks then break the odd–even pairing.
4. **Flood fill with old == new** never terminates.
5. **Recursive fill on a big region** — stack overflow.

## Check your understanding
<!-- bite: 43261169-5806-40b0-906a-3892993bd3d6 -->

Try each one before you open the answer.

1. <!-- q: exact id="7e76b8f8" answer="-9" accept="−9" -->
   For the midpoint circle algorithm with r = 10, what is the starting decision parameter p₀ = 1 − r?

   <details><summary>Answer</summary>

   −9. Use 1 − r instead of 5/4 − r with integers: the ¼ never changes a sign decision.

   </details>

2. <!-- q: mcq id="73729909" -->
   In the r = 10 table, why is (7, 7) the last pixel computed?

   - [x] The octant ends where x = y, and symmetry supplies the rest
   - [ ] The decision parameter became positive
   - [ ] r = 10 only has 8 pixels in total

   <details><summary>Answer</summary>

   The octant ends where x = y (the 45° point); symmetry supplies the rest.

   </details>

3. <!-- q: exact id="52edb57e" answer="8" accept="eight" -->
   How many points on the circle do you get from each point computed in one octant?

   <details><summary>Answer</summary>

   8, by eight-way symmetry: swapping and negating the coordinates. An ellipse only has four-way symmetry.

   </details>

4. <!-- q: gap id="000cc726" answers="3;9" -->
   Fill in the gaps. Triangle (2,2), (10,2), (6,8), scan line y = 3. The edges cross at x = 2.67 and x = 9.33, so the scan-line fill colours pixels x = ___ to x = ___.

   <details><summary>Answer</summary>

   3 to 9. The bottom edge y = 2 is horizontal, so it is ignored.

   </details>

5. <!-- q: mcq id="9c5a65a5" -->
   You fill inside a circle drawn with an 8-connected outline using an 8-connected flood fill. What might happen?

   - [ ] Nothing, it fills perfectly
   - [x] It leaks through the corner gaps of the diagonal parts and fills the outside
   - [ ] It fills only the outline

   <details><summary>Answer</summary>

   It can leak through the corner gaps of the diagonal parts of the outline and fill the outside. A 4-connected fill is safe with an 8-connected boundary.

   </details>

6. <!-- q: open id="b6ce134d" -->
   A scan line passes exactly through a vertex where the outline goes up then down (a peak). How should that crossing be counted, and what goes wrong if you count it once?

   <details><summary>Answer</summary>

   Twice (or zero times). Counting once leaves an odd number of crossings, so the pairing shifts and the span outside the shape gets filled.

   </details>

## Practice — independent task
<!-- bite: 1d617cf2-adce-4aff-a84a-295ac5166cac -->

Write `scanline_fill(vertices)` returning the set of filled pixels, using an edge table and the lower-end-included rule. **Done when** the triangle $(2,2)$, $(10,2)$, $(6,8)$ fills $x = 3$ to $9$ on $y = 3$, and a concave "W" shape fills correctly through its valleys.

## Before moving on
<!-- bite: c79c215c-e51f-4ac3-921e-e328507d890d -->

**Next:** [[computer-graphics/05-clipping|Clipping]] — throwing away what is outside the window before you spend time drawing it.

## Related
<!-- bite: 55074018-c13e-4a52-9a75-776b0c6d48ff -->
- [[computer-graphics/03-line-drawing-and-antialiasing|Line Drawing]]
- [[computer-graphics/11-rasterisation|Rasterisation]] — the modern triangle-coverage approach (edge functions) that replaced scan-line fill in hardware
- [[computer-graphics/index|Computer graphics map]]

## About this lesson
<!-- bite: 8d913885-f60c-4db7-a21c-ba9f06c0f775 -->

**Level:** Intermediate. **Covers:** Drawing circles with integers only (eight-way symmetry, the midpoint and Bresenham circle algorithms, ellipses), then colouring the inside of shapes: scan-line fill with edge tables, flood fill, boundary fill, and 4- versus 8-connectivity.

Part 1 of the course. Builds on the midpoint idea from [[computer-graphics/03-line-drawing-and-antialiasing|note 03]].
