# State Space

**[Advanced]** — The modern representation. Why matrices instead of transfer functions, what "state" really means, and how the two views connect.

## The representation

Instead of one $n$th-order differential equation, write $n$ first-order ones and stack them:

$$\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$$
$$\mathbf{y} = C\mathbf{x} + D\mathbf{u}$$

| Symbol | Name | Size | Meaning |
|---|---|---|---|
| $\mathbf{x}$ | **state** | $n \times 1$ | everything you need to know about *now* |
| $\mathbf{u}$ | input | $m \times 1$ | what you command |
| $\mathbf{y}$ | output | $p \times 1$ | what you measure |
| $A$ | system / dynamics matrix | $n \times n$ | how the state evolves on its own |
| $B$ | input matrix | $n \times m$ | how inputs push the state |
| $C$ | output matrix | $p \times n$ | what the sensors see |
| $D$ | feedthrough | $p \times m$ | direct input→output; usually **0** |

$D = 0$ for almost every physical system, because a real plant can't respond instantaneously.

## What "state" means

The definition worth internalising:

> **The state is the minimum set of variables such that, knowing $\mathbf{x}(t_0)$ and $\mathbf{u}(t)$ for $t \geq t_0$, you can determine all future behaviour.**

**The state is a complete summary of the past.** Nothing about the history before $t_0$ matters beyond what's in $\mathbf{x}(t_0)$ — which is the same Markov property that shows up in [[ai-ml/03-ai-engineer/README|reinforcement learning]] and in queueing theory, and for the same reason.

**Choosing states** — usually the energy-storing elements, because energy can't change instantaneously:

- **Mechanical** — positions and velocities (potential and kinetic energy)
- **Electrical** — capacitor voltages, inductor currents
- **Thermal** — temperatures
- **Chemical** — concentrations

**The number of states equals the system order**, which equals the number of independent energy stores.

### Example: mass–spring–damper

$$m\ddot{x} + c\dot{x} + kx = F$$

Pick $x_1 = x$ (position), $x_2 = \dot{x}$ (velocity):

$$\begin{bmatrix}\dot{x}_1 \\ \dot{x}_2\end{bmatrix} = \begin{bmatrix}0 & 1 \\ -k/m & -c/m\end{bmatrix}\begin{bmatrix}x_1 \\ x_2\end{bmatrix} + \begin{bmatrix}0 \\ 1/m\end{bmatrix}F$$

$$y = \begin{bmatrix}1 & 0\end{bmatrix}\mathbf{x}$$

The first row says $\dot{x}_1 = x_2$ — position's derivative is velocity, definitionally. **The second row is the physics.** That pattern (trivial rows plus one real row) is what a state-space model of a mechanical system looks like.

**State representations are not unique.** Any invertible $T$ gives $\mathbf{z} = T\mathbf{x}$ with

$$\bar{A} = TAT^{-1}, \quad \bar{B} = TB, \quad \bar{C} = CT^{-1}$$

Different coordinates, same system. **Eigenvalues are invariant under this transformation** — which is why they, and not the matrix entries, are the physically meaningful thing.

## Why bother

Transfer functions work fine for SISO systems. The case for state space:

**MIMO is natural.** $B$ is just wider and $C$ taller. Transfer functions become matrices of transfer functions and the algebra gets painful fast. → [[engineering/02-control-theory/01-what-control-theory-is|SISO and MIMO]]

**Internal behaviour is visible.** A transfer function only describes input→output. State space shows you states that are internally unstable but invisible at the output — exactly the pole–zero cancellation trap from [[engineering/02-control-theory/05-stability-and-root-locus|note 05]], now expressible.

**It handles time-varying and nonlinear systems.** $A(t)$ is no harder to write than $A$. Nonlinear systems generalise to $\dot{\mathbf{x}} = f(\mathbf{x},\mathbf{u})$, and much of the theory carries over.

**Initial conditions are explicit.** Transfer functions assume they're zero.

**Numerically better.** Matrix computations on $(A,B,C,D)$ are far better conditioned than root-finding on high-order polynomials. For $n > 10$, transfer-function methods are numerically unreliable and state-space methods are routine.

**It's what the algorithms want.** LQR, Kalman filtering, MPC, and every modern synthesis method are stated in state space.

## The solution

$$\mathbf{x}(t) = \underbrace{e^{At}\mathbf{x}(0)}_{\text{natural response}} + \underbrace{\int_0^t e^{A(t-\tau)}B\mathbf{u}(\tau)\,d\tau}_{\text{forced response}}$$

The **matrix exponential** $e^{At}$ is the **state transition matrix** — it propagates the state forward:

$$e^{At} = I + At + \frac{A^2t^2}{2!} + \cdots$$

**Don't compute it that way.** The series converges slowly and badly for stiff systems. Use the eigendecomposition when $A$ is diagonalisable, or a scaling-and-squaring Padé method (what `expm` does) otherwise. It's a genuinely delicate numerical problem — the classic paper on it is titled *"Nineteen Dubious Ways to Compute the Exponential of a Matrix"*.

## Eigenvalues are the poles

**The connection to everything in notes 02–07:**

$$\boxed{\text{eigenvalues of } A = \text{poles of the transfer function}}$$

Because $\det(sI - A) = 0$ *is* the characteristic equation.

So stability is a linear-algebra statement:

$$\text{Stable} \iff \text{all eigenvalues of } A \text{ have negative real part}$$

Everything from the classical notes transfers directly. Complex eigenvalue pairs are oscillatory modes; the rightmost eigenvalue dominates; $\zeta$ and $\omega_n$ are read off the same way. → [[engineering/02-control-theory/03-time-response|Time Response]]

**Eigenvectors are the mode shapes** — the direction in state space along which that mode acts. In a building model, an eigenvalue tells you the frequency and damping of a vibration mode; the eigenvector tells you what the building looks like while doing it. → [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]]

**Modal form:** transform to $\bar{A} = \Lambda$ (diagonal, eigenvalues on the diagonal) and the modes fully decouple — $n$ independent first-order systems. That's the cleanest way to see what a system is doing.

## Converting between representations

**State space → transfer function:**

$$G(s) = C(sI - A)^{-1}B + D$$

Unique, and always exists.

**Transfer function → state space:** not unique — infinitely many realisations. Standard ones:

**Controllable canonical form** — the coefficients of the denominator appear directly in the bottom row of $A$. **Always controllable**, which makes pole placement trivial. → [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|note 09]]

**Observable canonical form** — the dual. Always observable.

**Modal form** — $A$ diagonal. Best numerical conditioning and the clearest physical reading.

> **The conversion can lose information.** If the transfer function has a pole–zero cancellation, the minimal realisation has fewer states than the original system — and the cancelled mode still exists in the real hardware. **The transfer function genuinely cannot see it**, which is the sharpest argument for state space: the hidden mode is a real thing that can grow without bound while the output looks perfect. → [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Controllability and Observability]]

## MIMO

Where state space pays for itself.

$$\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}, \qquad \mathbf{y} = C\mathbf{x}$$

**Nothing about the notation changes.** $B$ has a column per actuator, $C$ a row per sensor. All the analysis — stability, controllability, LQR — applies unmodified.

**Coupling** is what makes MIMO hard in classical terms: input 1 affects outputs 1 and 2, so you can't tune two SISO loops independently. Classical approaches to this are painful (relative gain array, decoupling networks, sequential loop closing). **State-space methods simply don't have the problem** — a full state-feedback gain $K$ is a matrix, and it handles all the coupling at once.

A quadcopter is the standard example: 12 states, 4 inputs, and the couplings (roll affects lateral position, thrust affects everything) are the entire difficulty. Cascaded PID does work in practice, but the design is much cleaner in state space.

## Discrete time

For implementation, the same structure with a difference equation:

$$\mathbf{x}[k+1] = A_d\mathbf{x}[k] + B_d\mathbf{u}[k]$$

Exact discretisation with a zero-order hold:

$$A_d = e^{AT}, \qquad B_d = \left(\int_0^T e^{A\tau}d\tau\right)B = A^{-1}(A_d - I)B \ \text{ if } A \text{ invertible}$$

**Stability moves from the left half plane to the unit disc:** $|\lambda_i| < 1$. The mapping is $z = e^{sT}$, which sends the imaginary axis to the unit circle. → [[engineering/02-control-theory/12-digital-control|Digital Control]]

## Practical notes

**Scale your states.** A model mixing metres and microradians has a badly conditioned $A$, and every subsequent computation suffers. Non-dimensionalise or scale to comparable magnitudes.

**Sanity-check by eigenvalue.** `eig(A)` immediately tells you stability, natural frequencies, and time constants. It's the first thing to run on any model.

**Check the rank of $B$ and $C$.** Rank-deficient means an actuator or sensor is redundant — often a modelling error.

**Watch stiffness.** Eigenvalues separated by many orders of magnitude make simulation slow and discretisation delicate. Consider model reduction: if a mode is 1000× faster than your bandwidth, it's a constant as far as the controller is concerned.

**Balanced truncation** is the principled way to reduce order — it ranks states by how much they contribute to input–output behaviour (Hankel singular values) and discards the ones that don't. Far better than deleting states by intuition.

---

## Related
- [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Controllability, Observability, Pole Placement]] — what you can do with this
- [[engineering/02-control-theory/02-modelling-and-transfer-functions|Modelling and Transfer Functions]] — the classical representation
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — eigenvalues and eigenvectors
- [[engineering/02-control-theory/README|Control theory map]]
