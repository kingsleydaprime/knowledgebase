# SSG 511 Formula Sheet

> **Lookup reference** for Part 1 (notes 12–18). Every key formula on one page, for revision and for checking hand work. **Matrices use column vectors** ($p' = Mp$); for row vectors ($P' = PT$, as in the SSG 511 assignment) transpose each one. The explanation of each formula lives in the linked note — this page is for after you have understood it.

## Display → [[computer-graphics/12-graphics-systems-and-display-hardware|note 12]]

$$\text{frame buffer bytes} = \frac{W \times H \times \text{bpp}}{8},\qquad \text{pixel rate} = W \times H \times \text{refresh rate},\qquad \text{ms per refresh} = \frac{1000}{\text{Hz}}$$

$N$ bits per pixel → $2^N$ colours.

## Lines → [[computer-graphics/13-line-drawing-and-antialiasing|note 13]]

**Slope and DDA**

$$m = \frac{dy}{dx},\qquad dx = x_2 - x_1,\qquad dy = y_2 - y_1$$

$$\text{steps} = \max(|dx|, |dy|),\qquad x_{inc} = \frac{dx}{\text{steps}},\qquad y_{inc} = \frac{dy}{\text{steps}},\qquad x_{i+1} = x_i + x_{inc},\quad y_{i+1} = y_i + y_{inc}$$

**Bresenham, $0 < m < 1$ (step in $x$)**

$$p_0 = 2dy - dx,\qquad p_{k+1} = \begin{cases} p_k + 2dy & p_k < 0\;\;(y \text{ stays})\\ p_k + 2dy - 2dx & p_k \ge 0\;\;(y + 1)\end{cases}$$

**Bresenham, $m > 1$ (step in $y$)**

$$p_0 = 2dx - dy,\qquad p_{k+1} = \begin{cases} p_k + 2dx & p_k < 0\;\;(x \text{ stays})\\ p_k + 2dx - 2dy & p_k \ge 0\;\;(x + 1)\end{cases}$$

**Midpoint line:** $d_0 = 2dy - dx$; $d \mathrel{+}= 2dy$ (lower) or $2(dy - dx)$ (upper).

## Circles → [[computer-graphics/14-circles-and-polygon-filling|note 14]]

$$x^2 + y^2 = r^2,\qquad f(x, y) = x^2 + y^2 - r^2$$

**Midpoint circle**

$$p_0 = 1 - r,\qquad p_{k+1} = \begin{cases} p_k + 2x_{k+1} + 1 & p_k < 0 \;\;(\text{E})\\ p_k + 2x_{k+1} + 1 - 2y_{k+1} & p_k \ge 0\;\;(\text{SE})\end{cases}$$

**Bresenham circle**

$$d_0 = 3 - 2r,\qquad d_{k+1} = \begin{cases} d_k + 4x_k + 6 & d_k < 0\\ d_k + 4(x_k - y_k) + 10 & d_k \ge 0\end{cases}$$

**Eight-way symmetry:** $(\pm x, \pm y)$ and $(\pm y, \pm x)$ about the centre.

**Scan-line fill:** next crossing $x_{k+1} = x_k + \dfrac{dx}{dy}$ (the edge's inverse slope).

## Clipping → [[computer-graphics/15-clipping|note 15]]

**Region code (TBRL):** T if $y > y_{max}$, B if $y < y_{min}$, R if $x > x_{max}$, L if $x < x_{min}$. OR = 0000 → accept; AND ≠ 0000 → reject.

**Cohen–Sutherland intersections**

$$\text{Top: } y = y_{max},\; x = x_1 + \frac{y_{max} - y_1}{m}\qquad \text{Bottom: } y = y_{min},\; x = x_1 + \frac{y_{min} - y_1}{m}$$

$$\text{Right: } x = x_{max},\; y = y_1 + m(x_{max} - x_1)\qquad \text{Left: } x = x_{min},\; y = y_1 + m(x_{min} - x_1)$$

**Liang–Barsky**

$$x = x_0 + t\,dx,\qquad y = y_0 + t\,dy,\qquad 0 \le t \le 1$$

$$p_1 = -dx,\; q_1 = x_0 - x_{min}\qquad p_2 = dx,\; q_2 = x_{max} - x_0\qquad p_3 = -dy,\; q_3 = y_0 - y_{min}\qquad p_4 = dy,\; q_4 = y_{max} - y_0$$

$$t_E = \max\!\left(0,\; \frac{q_k}{p_k}\text{ for } p_k < 0\right),\qquad t_L = \min\!\left(1,\; \frac{q_k}{p_k}\text{ for } p_k > 0\right)$$

Visible if $t_E \le t_L$. If $p_k = 0$ and $q_k < 0$, reject.

**Cyrus–Beck** (outward normal $N_i$, any edge point $P_{E_i}$, $P(t) = P_0 + tD$)

$$t_i = \frac{N_i \cdot (P_{E_i} - P_0)}{N_i \cdot D}$$

$N_i\cdot D < 0$ entering (keep the largest as $t_E$); $N_i \cdot D > 0$ leaving (keep the smallest as $t_L$).

**3D:** 6-bit codes; in clip space, inside means $-w \le x, y, z \le w$.

## 2D transformations → [[computer-graphics/16-2d-and-3d-transformations|note 16]]

$$T(t_x, t_y) = \begin{pmatrix} 1 & 0 & t_x \\ 0 & 1 & t_y \\ 0 & 0 & 1\end{pmatrix},\qquad S(s_x, s_y) = \begin{pmatrix} s_x & 0 & 0 \\ 0 & s_y & 0 \\ 0 & 0 & 1\end{pmatrix},\qquad R(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1\end{pmatrix}$$

$$\text{Shear}_x(k) = \begin{pmatrix} 1 & k & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1\end{pmatrix},\qquad \text{Shear}_y(k) = \begin{pmatrix} 1 & 0 & 0 \\ k & 1 & 0 \\ 0 & 0 & 1\end{pmatrix},\qquad \text{Reflect}_x = \operatorname{diag}(1, -1, 1)$$

**About a point:** $M = T(p_x, p_y)\,R(\theta)\,T(-p_x, -p_y)$.

**Row-vector rotation:**

$$R(\theta)^T = \begin{pmatrix} \cos\theta & \sin\theta & 0 \\ -\sin\theta & \cos\theta & 0 \\ 0 & 0 & 1\end{pmatrix}$$

$\cos 30° = 0.866$, $\sin 30° = 0.5$, $\cos 60° = 0.5$, $\sin 60° = 0.866$.

## 3D transformations → note 16

$$T = \begin{pmatrix} 1&0&0&t_x \\ 0&1&0&t_y \\ 0&0&1&t_z \\ 0&0&0&1\end{pmatrix},\qquad S = \begin{pmatrix} s_x&0&0&0 \\ 0&s_y&0&0 \\ 0&0&s_z&0 \\ 0&0&0&1\end{pmatrix}$$

$$R_x = \begin{pmatrix} 1&0&0&0 \\ 0&c&-s&0 \\ 0&s&c&0 \\ 0&0&0&1\end{pmatrix},\quad R_y = \begin{pmatrix} c&0&s&0 \\ 0&1&0&0 \\ -s&0&c&0 \\ 0&0&0&1\end{pmatrix},\quad R_z = \begin{pmatrix} c&-s&0&0 \\ s&c&0&0 \\ 0&0&1&0 \\ 0&0&0&1\end{pmatrix}$$

with $c = \cos\theta$, $s = \sin\theta$.

**Homogeneous:** $(x, y, z) \to (x, y, z, 1)$; $(X, Y, Z, W) \to \left(\frac XW, \frac YW, \frac ZW\right)$; $W = 0$ is a direction.

**Blocks:** top-left 3 × 3 linear; right column translation; bottom row perspective; corner $d$ uniform scale.

## Vectors and Bézier curves → [[computer-graphics/17-curves-bezier-and-b-splines|note 17]]

**Affine and barycentric combinations**

$$P = P_1 + t(P_2 - P_1) = (1-t)P_1 + tP_2,\qquad P = \alpha_1P_1 + \alpha_2P_2 + \alpha_3P_3,\quad \alpha_1 = 1 - \alpha_2 - \alpha_3$$

**Bernstein form**

$$B(t) = \sum_{i=0}^{n} P_i\,B_{n,i}(t),\qquad B_{n,i}(t) = \binom{n}{i}t^i(1-t)^{n-i},\qquad \sum_{i=0}^n B_{n,i}(t) = 1$$

**Quadratic and cubic**

$$P(t) = (1-t)^2P_0 + 2t(1-t)P_1 + t^2P_2$$

$$B(t) = (1-t)^3P_0 + 3t(1-t)^2P_1 + 3t^2(1-t)P_2 + t^3P_3$$

**Cubic in matrix form**

$$B(t) = \begin{pmatrix} 1 & t & t^2 & t^3\end{pmatrix}\begin{pmatrix} 1&0&0&0 \\ -3&3&0&0 \\ 3&-6&3&0 \\ -1&3&-3&1\end{pmatrix}\begin{pmatrix} P_0 \\ P_1 \\ P_2 \\ P_3\end{pmatrix}$$

**Derivative and end conditions**

$$B'(t) = \sum_{i=0}^{n-1} B_{n-1,i}(t)\;n(P_{i+1} - P_i)$$

$$B'(t) = 3\left[(1-t)^2(P_1 - P_0) + 2(1-t)t(P_2 - P_1) + t^2(P_3 - P_2)\right]$$

$$B'(0) = 3(P_1 - P_0),\qquad B'(1) = 3(P_3 - P_2),\qquad P_1 = P_0 + \frac{v_0}{3},\qquad P_2 = P_3 - \frac{v_1}{3}$$

$$B\!\left(\tfrac12\right) = \frac{P_0 + 3P_1 + 3P_2 + P_3}{8}$$

**de Casteljau**

$$P_i^{\,r}(t) = (1-t)P_i^{\,r-1} + tP_{i+1}^{\,r-1},\qquad P_i^{\,0} = P_i,\qquad B(t) = P_0^{\,n}(t)$$

Split at $t = s$: the left edge $P_0^0, P_0^1, P_0^2, P_0^3$ is the first part; the right edge (bottom up) the second. **First half at $s = \tfrac12$:**

$$Q_0 = P_0,\quad Q_1 = \frac{P_0 + P_1}{2},\quad Q_2 = \frac{P_0 + 2P_1 + P_2}{4},\quad Q_3 = \frac{P_0 + 3P_1 + 3P_2 + P_3}{8}$$

**Chaikin corner cutting** (each edge $P_iP_{i+1}$)

$$Q_i = \tfrac34P_i + \tfrac14P_{i+1},\qquad R_i = \tfrac14P_i + \tfrac34P_{i+1}$$

## B-splines (Cox–de Boor) → note 17

$$N_{i,1}(t) = \begin{cases} 1 & t_i \le t < t_{i+1}\\ 0 & \text{otherwise}\end{cases}$$

$$N_{i,k}(t) = \frac{t - t_i}{t_{i+k-1} - t_i}N_{i,k-1}(t) + \frac{t_{i+k} - t}{t_{i+k} - t_{i+1}}N_{i+1,k-1}(t)$$

$$C(t) = \sum_{i=0}^n P_i\,N_{i,k}(t),\qquad t_{k-1} \le t \le t_{n+1},\qquad t_0 \le t_1 \le \dots \le t_{n+k}$$

Order $k$, degree $k - 1$, continuity $C^{k-2}$ with distinct knots.

## Geometry helpers → note 17

**Point to segment $AB$**

$$t = \frac{(P - A)\cdot(B - A)}{|B - A|^2},\qquad t^* = \min(1, \max(0, t)),\qquad d = \left|P - \bigl(A + t^*(B - A)\bigr)\right|$$

**Flatness of a quadratic Bézier** (max distance from the chord; halving divides it by 4)

$$\delta = \frac{|P_1 - 2P_2 + P_3|}{4}$$

**Regular $n$-gon**, centre $(x_c, y_c)$, radius $r$

$$(x_k, y_k) = \left(x_c + r\cos\frac{360°\,k}{n},\; y_c + r\sin\frac{360°\,k}{n}\right),\qquad k = 0, \dots, n-1$$

## Visible surfaces → [[computer-graphics/18-visible-surface-detection|note 18]]

$$z = \frac{-Ax - By - D}{C},\qquad z(x+1, y) = z - \frac AC,\qquad z(x, y-1) = z + \frac BC$$

**Back face** (view direction $V$ into the scene): $V \cdot N > 0$; looking down $-z$, $N_z < 0$.

**Depth-buffer memory:** $W \times H \times$ bytes per depth (1080p at 4 bytes ≈ 8.3 MB).

## Related
- [[computer-graphics/19-ssg-511-question-bank|Question bank]]
- [[computer-graphics/index|Computer graphics map]]
