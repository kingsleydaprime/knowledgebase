# Circles and Polygon Filling

**[Intermediate]** — Drawing circles with integers only (eight-way symmetry, the midpoint and Bresenham circle algorithms, ellipses), then colouring the inside of shapes: scan-line fill with edge tables, flood fill, boundary fill, and 4- versus 8-connectivity.

> Part 1 of the course. Builds on the midpoint idea from [[computer-graphics/02-line-drawing-and-antialiasing|note 02]].

## Before you start

You can trace a Bresenham line table ([[computer-graphics/02-line-drawing-and-antialiasing|note 02]]) and you know $x^2 + y^2 = r^2$ is a circle.

**After this note you will be able to:**
1. Use eight-way symmetry to draw a full circle from one octant.
2. Trace the midpoint circle algorithm by hand and derive its update rules.
3. Fill a polygon with the scan-line algorithm, handling vertices correctly.
4. Choose between flood fill and boundary fill, and between 4- and 8-connected.

## The kid version

A circle looks the same if you flip it left-right, up-down, or across a diagonal. So you only need to draw one-eighth of it carefully — a slice like a pizza wedge — and then copy it eight ways. For each step along that slice you ask the same "which square is closer?" question as with lines.

Filling is colouring in. Either you go row by row like a printer, colouring between the points where the row crosses the outline (scan-line), or you drop a tin of paint inside and let it spread until it hits the edge (seed fill).

**Where the analogy stops working.** Paint that spreads diagonally can squeeze through a gap where two outline pixels only touch at a corner. Real paint wouldn't; an 8-connected fill does.

## Terms used in circles and filling

1. **Octant**: This is one eighth of the circle, a 45° slice. The algorithms compute the octant from $(0, r)$ to the point where $x = y$.
2. **Eight-way symmetry**: This is the fact that each point $(x, y)$ on a circle centred at the origin gives seven more by swapping and negating coordinates.
3. **Circle function**: This is $f(x, y) = x^2 + y^2 - r^2$. It is negative inside the circle, zero on it, and positive outside.
4. **Scan line**: This is one horizontal row of pixels, at a fixed $y$.
5. **Edge table**: This is a list of a polygon's edges, each stored with its top $y$, its $x$ at the bottom, and its inverse slope $dx/dy$.
6. **Active edge table**: This is the subset of edges that cross the current scan line.
7. **Seed**: This is the one pixel inside the region from which a flood or boundary fill starts.
8. **4-connected**: This describes moving to the four neighbours up, down, left and right.
9. **8-connected**: This describes moving to those four plus the four diagonal neighbours.

## 1. Why not just use the equation?

Drawing $x^2 + y^2 = r^2$ directly has problems:

- **$y = \pm\sqrt{r^2 - x^2}$ needs a square root per pixel**, and the pixels come out unevenly spaced — big gaps where the circle is steep.
- **The polar form $x = r\cos\theta$, $y = r\sin\theta$ needs trigonometry**, which is slow.

**So, as with lines, use incremental integer algorithms.**

## 2. Eight-way symmetry

**Compute one octant — from $(0, r)$ at the top to the 45° point where $x = y$ — and each computed point gives eight.** For centre $(x_c, y_c)$:

```
(xc + x, yc + y)   (xc - x, yc + y)   (xc + x, yc - y)   (xc - x, yc - y)
(xc + y, yc + x)   (xc - y, yc + x)   (xc + y, yc - x)   (xc - y, yc - x)
```

## 3. The midpoint circle algorithm

**Start at $(0, r)$ and move clockwise.** At each step $x$ increases by 1, and you choose between **E** $= (x_k + 1, y_k)$ and **$\mathrm{SE}$** $= (x_k + 1, y_k - 1)$.

**Evaluate the circle function at the midpoint of the two candidates:**

$$p_k = f\!\left(x_k + 1,\; y_k - \tfrac12\right) = (x_k + 1)^2 + \left(y_k - \tfrac12\right)^2 - r^2$$

- **$p_k < 0$**: the midpoint is inside the circle, so E is closer. Plot $(x_k + 1, y_k)$.
- **$p_k \ge 0$**: $\mathrm{SE}$ is closer. Plot $(x_k + 1, y_k - 1)$.

**Start value:** $p_0 = f(1, r - \tfrac12) = \tfrac54 - r$. **For integer $r$, use $p_0 = 1 - r$** (the $\tfrac14$ never changes a sign decision, since everything else is an integer).

**Updates** ($x_{k+1}$, $y_{k+1}$ are the *new* coordinates):

$$p_{k+1} = \begin{cases} p_k + 2x_{k+1} + 1 & \text{E chosen} \\ p_k + 2x_{k+1} + 1 - 2y_{k+1} & \text{SE chosen}\end{cases}$$

**Where they come from:** subtract $f$ at the old midpoint from $f$ at the new one. For E the change is $(x_k + 2)^2 - (x_k + 1)^2 = 2x_k + 3 = 2x_{k+1} + 1$. For $\mathrm{SE}$ there is an extra $(y_k - \tfrac32)^2 - (y_k - \tfrac12)^2 = -2y_k + 2 = -2y_{k+1}$.

**Steps:**
1. Input $r$ and centre $(x_c, y_c)$.
2. Set $x = 0$, $y = r$, $p = 1 - r$. Plot the eight symmetric points.
3. While $x < y$: $x \mathrel{+}= 1$. If $p < 0$, $p \mathrel{+}= 2x + 1$; otherwise $y \mathrel{-}= 1$ and $p \mathrel{+}= 2(x - y) + 1$. Plot the eight points.

### Worked — $r = 10$, centre at the origin

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

### Worked — $r = 13$

$p_0 = -12$.

| x | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| y | 13 | 13 | 13 | 13 | 12 | 12 | 12 | 11 | 10 | 9 |
| p | −12 | −9 | −4 | 3 | −12 | −1 | 12 | 5 | 2 | 3 |

The octant ends at $(9, 9)$ on the diagonal.

### Runnable check

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

**Same structure, but the decision compares the squared distances of the two candidates from the circle:**

$$d = \left[(x+1)^2 + y^2 - r^2\right] + \left[(x+1)^2 + (y-1)^2 - r^2\right]$$

When $d < 0$, E is closer. Simplifying, with $(x, y)$ the pixel just plotted (before moving):

- **Start:** $d_0 = 3 - 2r$.
- **$d < 0$:** next pixel $(x + 1, y)$, and $d \mathrel{+}= 4x + 6$.
- **$d \ge 0$:** next pixel $(x + 1, y - 1)$, and $d \mathrel{+}= 4(x - y) + 10$.

For $r = 10$ it gives the same octant as the midpoint algorithm — and it does so for $r = 5, 10, 13, 17, 40$ (re-run). **Both use only integer additions.**

## 5. Ellipses

**The midpoint idea also works for ellipses**, but an ellipse has only **four-way symmetry**. Compute one quadrant, **split into two regions at the point where the curve's slope passes −1**: in region 1 (slope shallower than −1) step $x$; in region 2 step $y$ — the same "step the long axis" rule as lines.

## 6. Polygon filling

**Filling a polygon means colouring every pixel inside it.** Two families:

- **Scan-line fill** works from the edges, one horizontal line at a time.
- **Seed fill** (flood fill and boundary fill) starts from one inside pixel and spreads outwards.

### Scan-line algorithm

For each scan line $y$ from the polygon's lowest to highest point:

1. Find where the scan line crosses the polygon's edges.
2. Sort the crossings by $x$.
3. **Pair them up — 1st with 2nd, 3rd with 4th — and fill between each pair.** This is the **odd–even rule**: inside between crossings 1 and 2, outside between 2 and 3, inside between 3 and 4.

**Details that matter:**

1. **Horizontal edges are ignored.** The edges next to them cover those pixels.
2. **Shared vertices.** A vertex shared by two edges would be counted twice. If the two edges lie on *opposite* sides of the scan line (the outline passes through), count it once. If both lie on the *same* side (a peak or valley), count it twice or not at all. **The common trick: include an edge's lower end, exclude its upper end** — this handles both cases automatically.
3. **Coherence for speed.** Keep an **edge table** with each edge's top $y$, its $x$ at the bottom, and its inverse slope $dx/dy$. On the next scan line, an edge's crossing moves by exactly its inverse slope, **so you add it instead of recomputing.** The edges crossing the current line form the **active edge table**.

**Worked — triangle $(2,2)$, $(10,2)$, $(6,8)$, scan line $y = 3$:**
- Left edge: $dx/dy = (6 - 2)/(8 - 2) = 0.667$, so it crosses at $x = 2 + 0.667 = 2.67$.
- Right edge: $dx/dy = (6 - 10)/(8 - 2) = -0.667$, so $x = 10 - 0.667 = 9.33$.
- **Fill pixels $x = 3$ to $9$.** (The bottom edge $y = 2$ is horizontal, so it is ignored.)

### Flood fill

**Replace every connected pixel of the old (interior) colour with the new colour, starting from a seed.** It stops wherever the colour is not the old colour. **Use it when the region has no single-colour boundary** — recolouring an area of an image.

```
flood_fill(x, y, old, new):      # needs old != new, or it never ends
    if getpixel(x, y) != old: return
    setpixel(x, y, new)
    flood_fill(x + 1, y, old, new)
    flood_fill(x - 1, y, old, new)
    flood_fill(x, y + 1, old, new)
    flood_fill(x, y - 1, old, new)
```

### Boundary fill

**Start from a seed inside and fill until you reach the boundary colour.** The boundary must be a single colour.

```
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

### 4-connected versus 8-connected

**This is which neighbours the fill spreads to** — what "4-connected polygons, 8-connected polygons" in class notes means.

**The key difference is leaking.** A boundary drawn as a diagonal line has pixels that touch only at corners:

```
 . . . # .        A 4-connected fill cannot step diagonally,
 . . # . .        so it stays on its side of this line.
 . # . . .        An 8-connected fill steps through the
 # . . . .        corner gaps and leaks out.
```

- **A 4-connected fill is safe with an 8-connected boundary.**
- **An 8-connected fill needs a 4-connected boundary** (no diagonal gaps). It is useful for thin shapes a 4-connected fill would miss.

> **The recursive versions overflow the stack on large regions** — a 1000 × 1000 region is a million nested calls. In practice use an explicit stack or queue, or fill whole horizontal runs at once (a **span fill**).

## Common pitfalls

1. **Stopping the octant at the wrong place.** Stop when $x \ge y$; going further duplicates the next octant.
2. **Using $p_0 = 5/4 - r$ with integers.** Use $1 - r$.
3. **Counting every shared vertex twice** in scan-line fill — peaks then break the odd–even pairing.
4. **Flood fill with old == new** never terminates.
5. **Recursive fill on a big region** — stack overflow.

## Check your understanding

1. In the $r = 10$ table, why is $(7, 7)$ the last pixel computed?
2. A scan line passes exactly through a vertex where the outline goes *up then down* (a peak). How should that crossing be counted, and what goes wrong if you count it once?
3. You fill inside a circle drawn with an 8-connected outline using an 8-connected flood fill. What might happen?

<details><summary>Answers (after your attempt)</summary>

1. The octant ends where $x = y$ (the 45° point); symmetry supplies the rest.
2. Twice (or zero times). Counting once leaves an odd number of crossings, so the pairing shifts and the span outside the shape gets filled.
3. It can leak through the corner gaps of the diagonal parts of the outline and fill the outside.

</details>

## Practice — independent task

Write `scanline_fill(vertices)` returning the set of filled pixels, using an edge table and the lower-end-included rule. **Done when** the triangle $(2,2)$, $(10,2)$, $(6,8)$ fills $x = 3$ to $9$ on $y = 3$, and a concave "W" shape fills correctly through its valleys.

## Before moving on

**Next:** [[computer-graphics/04-clipping|Clipping]] — throwing away what is outside the window before you spend time drawing it.

## Related
- [[computer-graphics/02-line-drawing-and-antialiasing|Line Drawing]]
- [[computer-graphics/10-rasterisation|Rasterisation]] — the modern triangle-coverage approach (edge functions) that replaced scan-line fill in hardware
- [[computer-graphics/index|Computer graphics map]]
