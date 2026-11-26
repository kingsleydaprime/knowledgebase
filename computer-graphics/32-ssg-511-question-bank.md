# SSG 511 Question Bank

> **[Intermediate]** · Every exam and assignment question from SSG 511 (Computer Graphics, Systems Engineering, first semester 2025/2026) in one place, **left unsolved on purpose.** Each one points to the note that teaches the method. Where a figure or matrix was missing from the source text, that is flagged — the question can't be answered without it.

**How to use this:** attempt closed-book, then check with the runnable code in the linked note (the Bresenham, Liang–Barsky and de Casteljau scripts are independent checks on hand work). **Answers are deliberately not here** — the value is in the attempt.

---

## Exam paper (2 hours — answer question **one** and any other three)

### Question 1

**(a)** Why are line and curve drawing algorithms important in computer graphics? State three reasons why Bresenham's algorithm is preferred over the digital differential analyser (DDA) for practical applications. *(5 marks)* → [[computer-graphics/03-line-drawing-and-antialiasing-1|note 03]] (why line algorithms matter), [[computer-graphics/04-line-drawing-and-antialiasing-2|note 04]] and [[computer-graphics/05-line-drawing-and-antialiasing-3|note 05]] (why Bresenham)

**(b)** With illustration, derive an expression to execute Bresenham's algorithm with slope greater than one. Given two end points $A(1,1)$ and $B(3,11)$, construct a table and produce the plot to rasterise A and B. *(15 marks)* → [[computer-graphics/06-line-drawing-and-antialiasing-4|note 06]]

**(c)** A particle is animated in $\mathbb R^3$ so that it starts at $(0,0,0)$ at $t = 0$ and arrives at $(4,0,2)$ at $t = 1$. The initial velocity is $(6,0,0)$ and the final velocity is $(0,0,3)$. The motion is modelled with a degree-three Bézier curve $B(t)$. → [[computer-graphics/17-curves-3|notes 17]]–[[computer-graphics/18-curves-4|18]]
- (i) Derive the equations for computing the position and velocity of the particle AND give the control points $P_1$ and $P_2$. *(6 marks)*
- (ii) Find the position of the particle at $t = \tfrac12$. *(3 marks)*
- (iii) The "first half" of the curve is $B_1(t) = B(t/2)$. Express $B_1(t)$ as a degree-three Bézier curve by giving its four control points. *(6 marks)*

### Question 2 *(10 marks)*

Refer to Fig. 1 — a square with vertices $B(-1,1)$, $C(1,1)$, $A(-1,-1)$, $D(1,-1)$, divided into four smaller squares by a horizontal and a vertical line through the middle ($D$ is the bottom-right corner). Draw its image after being transformed by each matrix: → [[computer-graphics/14-2d-and-3d-transformations|note 14]]

(a) $\begin{pmatrix}\cos60 & \sin60 & 0\\ -\sin60 & \cos60 & 0\\ 0&0&1\end{pmatrix}$ (b) $\begin{pmatrix}1&0&0\\1&3&0\\0&0&1\end{pmatrix}$ (c) $\begin{pmatrix}1&0&0.5\\0&1&0\\0&0&1\end{pmatrix}$

> **Hint:** decide the vector convention first. Matrix (a)'s layout is the row-vector form of an anticlockwise rotation — and that choice changes what (c) means. See note 14's "Check your understanding" Q1.

### Question 3 *(10 marks)*

The inkjet technology is widely used in industry for marking and coding, and reposes on the emission of charged droplets at high velocity and high frequency. Give a detailed step-by-step account of the numerical modelling of the ink jet breakup process in COMSOL Multiphysics. → [[computer-graphics/33-comsol-ink-jet-breakup|note 33]] *(not in the lecture notes; taken from a published COMSOL paper)*

### Question 4 *(10 marks)*

Consider a cone of height one unit, with apex at $(0,1,0)$ and a base of diameter one unit centred at the origin. Transform it so that the apex is at $(-1,2,-3)$, the base is centred at $(1,4,-3)$, and the base's diameter is two units. What transformations are required, and in what order? Write down the product of the individual transformation matrices. → [[computer-graphics/14-2d-and-3d-transformations|note 14]] §6

### Question 5

**(a)** Give a detailed description of how Cohen–Sutherland can be used to clip a straight-line segment against a rectangle. *(6 marks)* → [[computer-graphics/10-clipping|note 10]] §3

**(b)** Consider the window region A–D of a clipped line with coordinates $A(-3,1)$ and $C(2,6)$. Determine whether the lines $P_1(-6,1)$–$P_2(-4,5)$, $P_3(-4,2)$–$P_4(-1,7)$, $P_5(-2,3)$–$P_6(1,2)$, $P_7(0,7)$–$P_8(3,2)$ and $P_9(4,5)$–$P_{10}(5,2)$ can be clipped or not, and perform the clipping on each as appropriate. *(4 marks)*

> **Hint:** $A$ is the lower-left corner (giving $xw_{min}$, $yw_{min}$) and $C$ the upper-right. Codes and accept/reject tests first; intersections only for lines that pass neither.

### Question 6 *(10 marks)*

Develop a program to implement Bresenham's line drawing algorithm. Ensure it uses only integer arithmetic. The code should handle slopes with $m > 1$ and correctly plot pixels for user-defined start and end points. Justify your results with **three** use cases. → [[computer-graphics/06-line-drawing-and-antialiasing-4|note 06]] (the program and its test cases)

### Exam coverage

| Question | Topic | Note | In the lecture-note PDF? |
|---|---|---|---|
| 1(a) | Why line algorithms matter; Bresenham vs DDA | 13 | Partly (pp. 2–3) |
| 1(b) | Bresenham derivation, $m > 1$; table | 13 | **No** |
| 1(c) | Cubic Bézier: position, velocity, control points, $t = \tfrac12$, first half | 17 | Yes (pp. 104–107) |
| 2 | Transform a square with three matrices | 16 | Yes (ch. 3, pp. 10–16) |
| 3 | Inkjet breakup in COMSOL | 20 | **No** — needs the lecturer's material |
| 4 | Transform a cone in 3D | 16 | Yes (§5.5, p. 27) |
| 5 | Cohen–Sutherland: description and five lines | 15 | **No** |
| 6 | Bresenham program, three use cases | 13 | **No** |

**Strategy:** Q1 is compulsory, and Q2, Q4, Q5 and Q6 are all covered — **Q3 is the one to leave until last or skip.** **Study order:** Bresenham first (Q1b is 15 marks and Q6 reuses it), then Bézier (Q1c), transformations (Q2, Q4), Cohen–Sutherland (Q5).

---

## Assignment Part A — programming tasks

All in the line drawing notes, [[computer-graphics/03-line-drawing-and-antialiasing-1|03]] to [[computer-graphics/07-line-drawing-and-antialiasing-5|07]].

1. Implement DDA. Prompt for start and end coordinates, draw the line, plotting the intermediate pixels.
2. Implement Bresenham with integer arithmetic only, for the first octant ($0 < m < 1$), for user-defined end points.
3. One application that switches between DDA and Bresenham for the same segment, displaying both (different colours or slightly offset) to compare end-point accuracy and smoothness.
4. Extend Bresenham to any slope (positive, negative, vertical, horizontal) in all quadrants, using $|dx|$, $|dy|$ and the right increments.
5. Draw simple 2D shapes (triangle, rectangle, arbitrary polygon) from input vertices by calling the line function in sequence.
6. DDA by hand, compared with the program: $A(20,10)$ to $B(30,18)$.
7. Full-octant integer Bresenham by hand, compared with the program: a "cross" of $(10,10)$–$(50,50)$ ($m = 1$) and $(50,10)$–$(10,50)$ ($m = -1$).
8. A regular hexagon centred at $(100,100)$ with radius 50 — you supply the six vertices.
9. Toggle standard/styled lines: a dashed rectangle with vertices $(50,50)$, $(200,50)$, $(200,150)$, $(50,150)$.

## Assignment Part B — transformations, clipping and curves

**B-1.** Draw the figure's image under each of (i), (ii), (iii) individually, not cumulatively. The square is $A(-1,1)$, $B(1,1)$, $C(1,-1)$, $D(-1,-1)$; (i) is a 30° rotation, (ii) is $\begin{pmatrix}1&0&0\\1&2&0\\0&0&1\end{pmatrix}$. ⚠️ *(iii)'s matrix was not in the source text.* → note 14 (part (i) is worked there)

**B-2.** Fig. 1 shows a complicated 2D transformation applied to a unit square. Describe it in terms of simpler transformations, give a homogeneous matrix for each, and use them to find the image $A'$ of point $A$. ⚠️ *Figure not in the source text.* → note 14

**B-3.** A triangle with vertices $(0,0)$, $(1,0)$, $(0,1)$ as homogeneous column vectors $a = [0,0,1]^T$, $b = [1,0,1]^T$, $c = [0,1,1]^T$, in an orthonormal basis (first unit vector right, second up). → note 14
- a. A matrix that translates the triangle 5 units to the left.
- b. A matrix that rotates it 90° anticlockwise.
- c. A matrix that translates it 5 units left **and** rotates it 90° anticlockwise about its own origin (point $a$ in its original coordinates).
- d. Under an affine $T$ the triangle maps to $a' = [4,2,1]$, $b' = [2,4,1]$, $c' = [4,4,1]$. Find $T$.

**B-4.** Homogeneous coordinates in 3D (Fig. 2). → note 14 §5
- (i) How do you convert $(x, y, z)$ to homogeneous coordinates, and back?
- (ii) What types of transformation does each of the four blocks ($a_{11}$…$a_{33}$, $b_1$…$b_3$, $c_1$…$c_3$, $d$) provide?
- (iii) What transformation does each matrix in Fig. 4 produce? ⚠️ *Matrices not in the source text.*

**B-5.** Square $ABCD$ and rectangle A′B′C′D′. ⚠️ *Figure not in the source text.* → note 14
1. A matrix, or product of matrices, that transforms $ABCD$ into A′B′C′D′.
2. What happens if the same transformation is applied to A′B′C′D′?

**B-6.** A homographic transformation of a 3D point as a 4 × 4 matrix product. → note 14
- (a) For each given matrix, identify the basic transformation(s) (translation, scaling, rotation, projection), naming any rotation axis and the order. ⚠️ *Matrices not in the source text.*
- (b) The cone — same as exam Q4. No need to multiply the matrices out.

**B-7.** Clipping. ⚠️ *The three example lines were in a figure not in the source text.* → [[computer-graphics/10-clipping|note 10]]
1. Describe an algorithm for clipping a line against a rectangle, and show it works on the three examples.
2. Describe Cohen–Sutherland in detail.
3. Extend the algorithm from (1) to clip a line against a 3D viewing frustum.
4. Describe how to clip a Bézier curve against a screen rectangle.
5. Apply Cohen–Sutherland to $P_1(40,15)$–$P_2(75,45)$ and $P_3(70,20)$–$P_4(100,10)$ against the window $A(50,10)$, $B(80,10)$, $C(80,40)$, $D(50,40)$.

**B-8.** The derivative of a Bézier curve: $B(t) = \sum_{i=0}^n P_iB_{n,i}(t)$, $B_{n,i}(t) = \frac{n!}{i!(n-i)!}t^i(1-t)^{n-i}$, $\frac{d}{dt}B_{n,i}(t) = n(B_{n-1,i-1}(t) - B_{n-1,i}(t))$, so $B'(t) = \sum_{i=0}^{n-1}B_{n-1,i}(t)\,n(P_{i+1} - P_i)$ — a degree-$(n-1)$ Bézier with control points $Q_i = n(P_{i+1} - P_i)$. *(Signs and ranges in the pasted original were garbled; this is the standard form — check against the slides.)* A particle starts at $(1,0,1)$ at $t = 0$ and arrives at $(5,2,4)$ at $t = 1$, with initial velocity $(6,0,0)$ and final velocity $(0,0,3)$, on a cubic Bézier. → [[computer-graphics/17-curves-3|note 17]]
- (a) Give $P_0, P_1, P_2, P_3$.
- (b) Find the position at $t = \tfrac12$ (the source read "t = 12").
- (c) Express the first half $B_1(t) = B(t/2)$ as a cubic Bézier by its four control points.

**B-9.** A cubic Bézier with $P_0 = (0,0)$, $P_1 = (2,0)$, $P_2 = (0,2)$, $P_3 = (4,4)$ (the source labelled the last two $P_3$, $P_4$). → [[computer-graphics/18-curves-4|note 18]]
- (a) Sketch and label the control points and the control polygon.
- (b) Use de Casteljau to compute $B(\tfrac12)$.
- (c) Sketch the curve approximately, to scale, showing the initial and final points and slopes.

**B-10.** A particle in $\mathbb R^2$ on a cubic Bézier: at $t = 0$ it is at $(0,0)$ with velocity $(6,0)$; at $t = 1$ at $(0,4)$ with velocity $(-12,0)$. → [[computer-graphics/17-curves-3|notes 17]]–[[computer-graphics/18-curves-4|18]]
- a. The control points $P_0$…$P_3$.
- b. Draw them and the control polygon.
- c. Calculate $B(\tfrac12)$, showing the work on the same graph.
- d. Sketch the curve for $0 \le t \le 1$ with the start and end slopes shown.
- e. The second half ($\tfrac12 \le t \le 1$) is also a cubic Bézier. Its control points?

**B-11.**
- (a) Define computer graphics and explain its applications. → [[computer-graphics/01-introduction-to-computer-graphics|note 01]]
- (b) List the major differences between DDA and Bresenham. For $A(2,2)$ and $B(9,2)$, write code that runs Bresenham, develop the table, and show the plot. If the $x$ and $y$ axes in A and B were switched, derive an expression (with a diagram) for Bresenham connecting the new points A′ and B′, plot A′B′ and compare with $AB$. → notes 03–06

## Supplementary questions

1. Define antialiasing. → note 08
2. Translate triangle $A(0,0)$, $B(5,0)$, $C(5,5)$ by 2 units in $x$ and 3 in $y$. → note 14
3. What is the computational complexity of basic DDA? Of Bresenham? What makes Bresenham more efficient? → note 05 (complexity)
4. **(a)** Describe in detail an algorithm that returns the minimum distance from a point to a line segment in 2D. Include all assumptions and calculations. → [[computer-graphics/18-curves-4|note 18]]
5. **(b)** A quadratic Bézier $P(t) = (1-t)^2P_1 + 2t(1-t)P_2 + t^2P_3$, $0 \le t \le 1$. Describe an algorithm that draws it with straight lines only, to within tolerance $\sigma$. You may use (a) and assume a line-drawing routine. → [[computer-graphics/18-curves-4|note 18]]
6. **(c)** Find a Bézier curve through $(0,5)$ with slope 2 and through $(6,1)$ with slope 3. Sketch it. → [[computer-graphics/17-curves-3|note 17]], worked (c)

## Still to confirm with the lecturer

- Rows 2–5 of the "five areas of improvement in GUI operations" list ([[computer-graphics/01-introduction-to-computer-graphics|note 01]]) — written from slide titles only.
- Whether there are COMSOL slides for Q3.
- The lecturer's version of Chaikin's algorithm ([[computer-graphics/19-curves-5|note 19]], §7).
- The figures and matrices flagged ⚠️ above.

## Related
- [[computer-graphics/34-ssg-511-formula-sheet|Formula sheet]] — everything you need to memorise, on one page
- [[computer-graphics/30-practice-exercises|Part 2 practice exercises]] — the modern-pipeline exercises
- [[computer-graphics/index|Computer graphics map]]
