# Optimal Control Problem Bank

Every problem from the author's optimal-control problem sheets, in one place. They come from F. L. Lewis, *Optimal Control*: problems 2.1-1 to 2.2-8 (discrete time) and 3.2-2 to 3.2-6 (continuous time). Each one points to the lesson that teaches it, and the final answers sit in a hidden "Check" block so you can mark your attempt without seeing the working.

**How to use this:** attempt each problem on paper first, then open the Check. If you're off, go to the linked lesson. Problems 2.1-3, 2.2-1, 2.2-2 and 2.2-3 were struck through on the sheet, so they weren't set; they're kept here briefly for completeness.

The notation follows Lewis: the Hamiltonian is $H^k = L^k + \lambda_{k+1}^Tf^k$ in discrete time and $H = L + \lambda^Tf$ in continuous time.

---

## Section 2.1: the discrete recipe

### 2.1-1 Optimal control of a bilinear system

Scalar plant $x_{k+1} = x_ku_k + 1$, cost $J = \tfrac12\sum_{k=0}^{1}u_k^2$, $N = 2$, and $x_2 = 0$ required.

- **(a)** Write the state and costate equations with $u_k$ eliminated.
- **(b)** Assume $\lambda_2$ is known. Solve for $\lambda_0$, $\lambda_1$ in terms of $\lambda_2$ and the state, express $x_2$ in terms of $\lambda_2$ and $x_0$, and find a quartic for $\lambda_2$.
- **(c)** With $x_0 = 1$, find the optimal states, costates, controls and cost.

→ [[control-theory/38-optimal-control-1|38 — Optimal Control 1: The Performance Index and the Discrete Recipe]] (worked in full)

<details><summary>Check</summary>

(a) $x_{k+1} = 1 - \lambda_{k+1}x_k^2$, $\lambda_k = -\lambda_{k+1}^2x_k$. (b) $x_1 = 1/(1 - \lambda_2^2x_0^2)$; quartic $x_0^4\lambda_2^4 - 2x_0^2\lambda_2^2 - \lambda_2 + 1 = 0$. (c) Two real roots; the optimum is $\lambda_2 = 0.5249$: $x_1 = 1.3803$, $\lambda_1 = -0.3803$, $\lambda_0 = -0.1446$, $u_0 = 0.3803$, $u_1 = -0.7245$, $J^* = 0.3347$. The other root (1.4902) gives $J = 2.400$.

</details>

### 2.1-2 Bilinear system, vector state

$x_{k+1} = Ax_k + Dx_ku_k + bu_k$, $x_k \in \mathbb{R}^n$, $u_k$ scalar, $J = \tfrac12x_N^TS_Nx_N + \tfrac12\sum(x_k^TQx_k + ru_k^2)$. Show the optimal control is $u_k = -(b + Dx_k)^T\lambda_{k+1}/r$, and find the state and costate equations with $u_k$ eliminated.

→ [[control-theory/38-optimal-control-1|38 — Optimal Control 1: The Performance Index and the Discrete Recipe]] (practice task)

<details><summary>Check</summary>

Stationarity: $ru_k + \lambda_{k+1}^T(Dx_k + b) = 0$. State: $x_{k+1} = Ax_k - (b + Dx_k)(b + Dx_k)^T\lambda_{k+1}/r$. Costate: $\lambda_k = Qx_k + A^T\lambda_{k+1} - (b + Dx_k)^T\lambda_{k+1}\,D^T\lambda_{k+1}/r$. Boundary: $\lambda_N = S_Nx_N$.

</details>

### 2.1-3 Generalised state-space (descriptor) system *(struck through, not set)*

Rederive the recipe for $Ex_{k+1} = f^k(x_k, u_k)$ with $E$ singular. The multiplier attaches to $f^k - Ex_{k+1}$, so the costate equation becomes $E^T\lambda_k = \partial(L^k + \lambda_{k+1}^Tf^k)/\partial x_k$.

---

## Section 2.2: linear plants and quadratic costs

### 2.2-1 The Lyapunov equation as a vector equation *(struck through, not set)*

Stacking the columns of $S$ into a vector $s(S)$ turns $S_k = A^TS_{k+1}A + Q$ into $s(S_k) = (A^T \otimes A^T)s(S_{k+1}) + s(Q)$, using the Kronecker product. → [[control-theory/40-optimal-control-3|23]]

### 2.2-2 Solutions to the algebraic Lyapunov equation *(struck through, not set)*

$A = \begin{bmatrix}\tfrac12 & 1 \\ 0 & -\tfrac12\end{bmatrix}$, $C = [2\ \ 0]$, $Q = C^TC$. Solve $P = A^TPA + Q$ by writing $P = \begin{bmatrix}p_1 & p_2 \\ p_3 & p_4\end{bmatrix}$. → [[control-theory/40-optimal-control-3|40 — Optimal Control 3: The Discrete Riccati Equation]]

<details><summary>Check</summary>

$A$'s eigenvalues are $\pm\tfrac12$, so the equation has exactly one solution, and it is symmetric: $p_1 = 16/3$, $p_2 = p_3 = 32/15$, $p_4 = 64/15$. (This assumes Lewis's equation 2.2-26 is the discrete form $P = A^TPA + Q$.)

</details>

### 2.2-3 Joseph-stabilised Riccati equation *(struck through, not set)*

Show the Joseph form $S_k = (A - BK_k)^TS_{k+1}(A - BK_k) + K_k^TRK_k + Q$, with the optimal $K_k$, equals the standard Riccati update. Expand and substitute $K_k = (B^TS_{k+1}B + R)^{-1}B^TS_{k+1}A$. → [[control-theory/40-optimal-control-3|23]]

### 2.2-4 Control of a scalar system

$x_{k+1} = 2x_k + u_k$.

- **(a)** Find the homogeneous solution $x_k$ for $k = 0$ to 5 if $x_0 = 3$.
- **(b)** Find the minimum-energy control that drives $x_0 = 3$ to $x_5 = 0$, and check the trajectory.
- **(c)** Find the optimal feedback gains $K_k$ minimising $J_0 = 5x_5^2 + \tfrac12\sum_{k=0}^{4}(x_k^2 + u_k^2)$, the resulting trajectory, and the costs to go $J_k^*$.

→ (a, b) [[control-theory/39-optimal-control-2|39 — Optimal Control 2: Minimum-Energy Control and Deadbeat]], (c) [[control-theory/40-optimal-control-3|40 — Optimal Control 3: The Discrete Riccati Equation]] (both worked in full)

<details><summary>Check</summary>

(a) 3, 6, 12, 24, 48, 96. (b) $u_k = -0.2815 \times 2^{4-k}$: $-4.504, -2.252, -1.126, -0.563, -0.282$; $x$: 3, 1.496, 0.739, 0.352, 0.141, 0; $J = 13.51$. (c) $K$: 1.618, 1.619, 1.622, 1.645, 1.818; $S$: 4.236, 4.237, 4.244, 4.290, 4.636, 10; $x$: 3, 1.146, 0.437, 0.165, 0.059, 0.011; $J^*_k = \tfrac12S_kx_k^2$: 19.06, 2.78, 0.405, 0.059, 0.008, 0.0006.

</details>

### 2.2-5 Comparison of different discrete controllers

$x_{k+1} = \begin{bmatrix}-\tfrac12 & \tfrac12 \\ 3 & -1\end{bmatrix}x_k + \begin{bmatrix}2 & 1 \\ 2 & 0\end{bmatrix}u_k$, $x_0 = \begin{bmatrix}8 \\ 4\end{bmatrix}$.

- **(a)** Find the open-loop $u_0$, $u_1$ driving $x_2 = 0$ while minimising $J_a = \tfrac12\sum_{k=0}^{1}u_k^T\begin{bmatrix}2 & 0 \\ 0 & 1\end{bmatrix}u_k$. Check by simulation.
- **(b)** Find constant feedback to input one, $u_k^1 = -Kx_k$ (input two zero), giving deadbeat control. Find the trajectory.
- **(c)** With $J_c = 10x_2^Tx_2 + J_a$, use the discrete LQ algorithm to find $u_0$, $u_1$ and the optimal cost.
- **(d)** Compare the trajectories. **(e)** With $x_0 = [1\ \ 2]^T$, how must each controller change?

→ (a) [[control-theory/39-optimal-control-2|22]], (b) [[control-theory/39-optimal-control-2|22]], (c) [[control-theory/40-optimal-control-3|23]]

<details><summary>Check</summary>

(a) $u_0 = [2.927,\ 6.195]^T$, $u_1 = [-2.146,\ -3.610]^T$, $x_1 = [10.05,\ 25.85]^T$, $x_2 = 0$, $J_a = 38.88$. (b) $K = [-1.5625,\ 0.8125]$, so $A - b_1K = \begin{bmatrix}2.625 & -1.125 \\ 6.125 & -2.625\end{bmatrix}$ (trace 0, determinant 0); $u_0^1 = 9.25$, $x_1 = [16.5,\ 38.5]^T$, $x_2 = 0$. (c) $S_2 = 20I$; $u_0 = [2.916,\ 6.152]^T$, $u_1 = [-2.096,\ -3.554]^T$, $x_2 = [0.178,\ -0.073]^T$, $J_c = 38.50$: a soft end penalty is slightly cheaper than (a)'s hard constraint. (e) (a)'s open-loop controls must be recomputed, since they depend on $x_0$; (b)'s and (c)'s feedback gains are unchanged, only the controls they produce change.

</details>

### 2.2-6 Linear performance index

$x_{k+1} = Ax_k + Bu_k$, $J = S_Nx_N + \sum(Qx_k + Ru_k)$, scalar. Write the state and costate equations and stationarity. What is the problem?

→ [[control-theory/38-optimal-control-1|38 — Optimal Control 1: The Performance Index and the Discrete Recipe]] (quiz question 5)

<details><summary>Check</summary>

Costate $\lambda_k = Q + A^T\lambda_{k+1}$, $\lambda_N = S_N$; stationarity $R + B^T\lambda_{k+1} = 0$, which has no $u_k$ in it. Without bounds on $u$ there's no minimum; with bounds the solution is bang-bang (Lewis section 5.2).

</details>

### 2.2-7 Cubic performance index

$x_{k+1} = ax_k + bu_k$, $J = \tfrac13s_Nx_N^3 + \tfrac13\sum(qx_k^3 + ru_k^3)$.

- **(a)** State and costate equations and stationarity. **(b)** When can you solve for $u_k$? Eliminate it. **(c)** Solve the open-loop problem with $x_N$ fixed, $s_N = 0$, $q = 0$.

→ [[control-theory/38-optimal-control-1|38 — Optimal Control 1: The Performance Index and the Discrete Recipe]]

<details><summary>Check</summary>

(a) $\lambda_k = qx_k^2 + a\lambda_{k+1}$; $ru_k^2 + b\lambda_{k+1} = 0$. (b) Only when $-b\lambda_{k+1}/r \ge 0$: then $u_k = \pm\sqrt{-b\lambda_{k+1}/r}$, and $x_{k+1} = ax_k \pm b\sqrt{-b\lambda_{k+1}/r}$. (c) $\lambda_{k+1} = a^{N-k-1}\lambda_N$, so $u_k = \pm\sqrt{-ba^{N-k-1}\lambda_N/r}$, and $\lambda_N$ is chosen so that $x_N = a^Nx_0 + \sum a^{N-1-k}bu_k$ hits the target.

</details>

### 2.2-8 Weighting the state-input product

- **(a)** Redo 2.2-4c with $J = 5x_5^2 + \tfrac12\sum_{k=0}^{4}(x_k^2 + u_k^2 + 2x_ku_k)$.
- **(b)** Redo 2.2-5c with $2x_k^Tu_k$ added to $J_a$.

→ [[control-theory/40-optimal-control-3|40 — Optimal Control 3: The Discrete Riccati Equation]]

<details><summary>Check</summary>

(a) With a cross weight $N$, $K_k = (B^TS_{k+1}B + R)^{-1}(B^TS_{k+1}A + N^T)$ and $S_k = A^TS_{k+1}A + Q - (A^TS_{k+1}B + N)K_k$. Here $K_k = (2S_{k+1} + 1)/(S_{k+1} + 1)$: $K_0 \ldots K_4$ = 1.196, 1.244, 1.323, 1.476, 1.909, with $S_0 \ldots S_4$ = 0.196, 0.244, 0.323, 0.476, 0.909. Notice $x^2 + u^2 + 2xu = (x + u)^2$: the running cost is zero when $u = -x$, so $S$ falls towards 0 far from the end. (b) The same cross-weight formulas with $N = I$ and the matrices of 2.2-5.

</details>

---

## Section 3.2: continuous time

### 3.2-2 Determining optimal control by approximation

$\dot{x} = -x^3 + u$, $x(0) = \tfrac12$, $J = \tfrac12x^2(2) + \tfrac12\int_0^2(x^2 + u^2)\,dt$.

- **(a)** State and costate equations, stationarity and boundary conditions; eliminate $u$.
- **(b)** Show that if $x$ stays small, $\lambda \approx x - x^3$.
- **(c)** Find $x(t)$ for this costate. **(d)** Find the approximate optimal control.

→ [[control-theory/41-optimal-control-4|41 — Optimal Control 4: Continuous Time and the Euler–Lagrange Equations]]

<details><summary>Check</summary>

(a) $u = -\lambda$; $\dot{x} = -x^3 - \lambda$; $-\dot\lambda = x - 3x^2\lambda$; $x(0) = \tfrac12$, $\lambda(2) = x(2)$. (b) Try $\lambda = x + ax^3$ and match powers of $x$ in $\dot\lambda = \lambda'(x)\dot{x}$: the $x^3$ terms give $-(1 + 4a) = 3$, so $a = -1$. The end condition $\lambda(2) = x(2)$ holds to first order when $x$ is small. (c) $\dot{x} = -x^3 - x + x^3 = -x$, so $x(t) = \tfrac12e^{-t}$. (d) $u = -(x - x^3) = -\tfrac12e^{-t} + \tfrac18e^{-3t}$.

</details>

### 3.2-3 Automobile suspension durability test

$m\ddot{y} + ky = u$, state $x = [y\ \ \dot{y}]^T$. Move from rest to $y(T) = h$, $\dot{y}(T) = 0$, minimising $\tfrac12\int_0^Tu^2\,dt$. Use $m = k = 1$, $T = 2$, $h = -3$ from part d.

→ [[control-theory/30-state-space-1|15]] (part a) and [[control-theory/41-optimal-control-4|41 — Optimal Control 4: Continuous Time and the Euler–Lagrange Equations]] (practice task)

<details><summary>Check</summary>

(a) $\dot{x}_1 = x_2$, $\dot{x}_2 = -(k/m)x_1 + u/m$. (b) $u = -\lambda_2/m$; $\dot\lambda_1 = (k/m)\lambda_2$, $\dot\lambda_2 = -\lambda_1$. (d) $\lambda(0) = [0.146,\ 3.439]^T$. (e) $u^*(t) = -3.439\cos t + 0.146\sin t$; $J^* = 4.60$. (f) Simulating gives $x(2) = [-3,\ 0]^T$.

</details>

### 3.2-4 Charging an inductor

A source $u$ drives a 1 Ω resistor and a 1 H inductor in series (figure P3.2-1). (a) State equation. (b) Charge from $x(0) = 0$ to $x(1) = 2$ A minimising $\int_0^1u^2\,dt$: the optimal control. (c) The optimal trajectory.

→ [[control-theory/41-optimal-control-4|41 — Optimal Control 4: Continuous Time and the Euler–Lagrange Equations]] (worked in full)

<details><summary>Check</summary>

(a) $\dot{x} = -x + u$. (b) $u^*(t) = (2/\sinh 1)e^{t} = 1.702e^{t}$, $J^* = 9.25$. (c) $x^*(t) = 1.702\sinh t$.

</details>

### 3.2-5 Bilinear system, continuous time

$\dot{x} = Ax + Dxu + bu$, $J = \tfrac12x^T(T)S(T)x(T) + \tfrac12\int_0^T(x^TQx + ru^2)\,dt$. Show the optimal control is a state-costate inner product, and eliminate $u$.

→ [[control-theory/41-optimal-control-4|41 — Optimal Control 4: Continuous Time and the Euler–Lagrange Equations]]

<details><summary>Check</summary>

$u = -(Dx + b)^T\lambda/r$. $\dot{x} = Ax - (Dx + b)(Dx + b)^T\lambda/r$; $-\dot\lambda = Qx + A^T\lambda - (Dx + b)^T\lambda\,D^T\lambda/r$; $\lambda(T) = S(T)x(T)$. Cubic in $(x, \lambda)$, so it needs a numerical solver.

</details>

### 3.2-6 Numerical solution of a bilinear system

$\dot{x}_1 = x_1x_2 + u$, $\dot{x}_2 = x_1^2 + x_2^2$, $J = \tfrac12s_1x_1^2(T) + \tfrac12s_2x_2^2(T) + \tfrac12\int_0^T(q_1x_1^2 + q_2x_2^2 + ru^2)\,dt$, $T$ fixed. Derive the Euler equations and boundary conditions. (The sheet asks for Fortran subroutines for Lewis's `tpoint`; today, write the right-hand side and boundary function for `scipy.integrate.solve_bvp`.)

→ [[control-theory/41-optimal-control-4|41 — Optimal Control 4: Continuous Time and the Euler–Lagrange Equations]]

<details><summary>Check</summary>

$u = -\lambda_1/r$. $-\dot\lambda_1 = q_1x_1 + \lambda_1x_2 + 2\lambda_2x_1$; $-\dot\lambda_2 = q_2x_2 + \lambda_1x_1 + 2\lambda_2x_2$. Boundary: $x(0)$ given, $\lambda_1(T) = s_1x_1(T)$, $\lambda_2(T) = s_2x_2(T)$. For `solve_bvp`, the state vector is $[x_1, x_2, \lambda_1, \lambda_2]$, with two conditions at $t = 0$ and two at $t = T$.

</details>

---

## Related

- [[control-theory/index|Control theory map]]
- [[control-theory/42-lqr|42 — LQR]]: the infinite-horizon continuous controller these problems lead to.

## About this bank

**Source:** the author's scanned problem sheets (Lewis, *Optimal Control*, pages 102 to 104 and 168 to 169). Every numerical Check is computed in `scripts/diagrams/control_theory.py` (`check_21` to `check_24` and `check_bank`).
