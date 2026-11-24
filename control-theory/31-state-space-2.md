---
id: 2831bc93-97f7-4240-af2a-f85224686dcd
---

# State Space 2: Solution, Eigenvalues and Conversions

The state equation has a closed-form solution built on the matrix exponential, and the eigenvalues of $A$ turn out to be exactly the poles of the transfer function.

## Before you start
<!-- bite: 2d26ce12-7745-459e-804b-eab58f5bd417 -->

You should have read [[control-theory/30-state-space-1|30 — State Space 1: States and the State Equation]], and be able to find the eigenvalues of a 2×2 matrix ([[mathematics/04-linear-algebra/index|linear algebra]]).

After this lesson you will be able to:

1. write the solution of $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$, and say what the matrix exponential does;
2. find a system's poles as the eigenvalues of $A$, and test stability with them;
3. convert a state-space model to a transfer function, and know why the reverse isn't unique;
4. discretise a model and state the discrete-time stability test.

## What this lesson covers
<!-- bite: 98bcdf5e-0931-45d7-8e07-3a1f267c79e2 -->

Lesson 30 wrote the suspension as matrices. Now we solve those equations, and find the bridge back to everything in lessons 03 to 29: the eigenvalues of $A$ are the poles. Once that's clear, every classical idea (stability, damping, dominant poles) carries straight over to matrices.

## The kid version
<!-- bite: 88178609-96df-4764-b8dd-2aec8430fad3 -->

Imagine a ball rolling on a shaped floor. Wherever you put it, the floor's slopes say exactly which way it moves next. The matrix $A$ is the floor. Some directions are special: put the ball on one of those lines and it rolls straight along it, speeding up or slowing down at a fixed rate. Those special directions are eigenvectors, and their rates are eigenvalues.

**Where the analogy stops working.** A real ball has momentum and friction you can feel. Here everything is in the matrix, including the "momentum", which is just one more state, and the special rates can be complex numbers, which means spinning rather than rolling.

## The solution
<!-- bite: e3ae1611-cd80-4862-b7df-c232145dadc7 -->

The state at any time is the sum of two parts:

$$\mathbf{x}(t) = \underbrace{e^{At}\mathbf{x}(0)}_{\text{natural response}} + \underbrace{\int_0^t e^{A(t-\tau)}B\mathbf{u}(\tau)\,d\tau}_{\text{forced response}}$$

In words: what the starting state does by itself, plus the effect of every input push since, each one carried forward to now.

The **matrix exponential** $e^{At}$ is called the **state transition matrix**: multiply the state now by it, and you get the state $t$ seconds later (with no input). It's defined by the same series as $e^x$:

$$e^{At} = I + At + \frac{A^2t^2}{2!} + \cdots$$

But **don't compute it that way**; the series behaves badly. Software uses eigenvalues or a "scaling and squaring" method. It's a famously delicate problem: a classic paper on it is titled *"Nineteen Dubious Ways to Compute the Exponential of a Matrix"*.

## Eigenvalues are the poles
<!-- bite: 78a8f812-0326-480c-ac8c-9620bb98033d -->

Here is the bridge to classical control:

$$\boxed{\text{eigenvalues of } A = \text{poles of the transfer function}}$$

Why: the eigenvalues solve $\det(sI - A) = 0$, and that determinant *is* the characteristic polynomial. So stability becomes a linear-algebra statement: **stable exactly when every eigenvalue of $A$ has a negative real part.**

Check it on the suspension. With $A = \begin{bmatrix}0 & 1 \\ -64 & -8\end{bmatrix}$:

$$\det(sI - A) = s(s + 8) + 64 = s^2 + 8s + 64 = 0 \quad\Rightarrow\quad s = -4 \pm 6.93j$$

Compare with lesson 13: $\omega_n = \sqrt{64} = 8$, $\zeta = 8/16 = 0.5$, and poles at $-\zeta\omega_n \pm j\omega_d = -4 \pm 6.93j$. The same numbers, found with matrices.

## Eigenvectors and modes
<!-- bite: d530489e-86e6-4074-9c35-42fbd42276f8 -->

**Eigenvectors are the mode shapes**: the direction in state space along which each mode acts. In a model of a building, an eigenvalue gives a vibration's frequency and damping; its eigenvector shows what the building looks like while doing it (top floor swaying one way, middle floors the other). → [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/index|Linear Algebra]]

Change coordinates so that $A$ becomes diagonal, with the eigenvalues on the diagonal, and the modes separate completely into $n$ independent first-order systems. This **modal form** is the clearest way to see what a system is doing.

## Converting to a transfer function
<!-- bite: 8a76f5f5-2d6e-442d-a531-0a1125bfb53a -->

From state space to transfer function is one formula, and it always gives the same answer:

$$G(s) = C(sI - A)^{-1}B + D$$

For the suspension, $(sI - A)^{-1}$ has $s^2 + 8s + 64$ underneath, and multiplying by $C$ and $B$ picks out one entry:

$$G(s) = \frac{0.004}{s^2 + 8s + 64}$$

Its DC gain is $0.004/64 = 1/16000$ m per newton: one over the spring stiffness, as it should be.

## Converting back: many answers
<!-- bite: 9531086f-dd78-4a6a-ae07-a8935c78fb00 -->

From transfer function to state space there are **infinitely many** correct answers, called **realisations**. Three standard ones:

1. **Controllable canonical form**: the denominator's coefficients sit in the bottom row of $A$. It's always controllable, which makes pole placement easy (lesson 35).
2. **Observable canonical form**: its mirror image. Always observable.
3. **Modal form**: $A$ diagonal. Best numerically and clearest physically.

Remember this one: **the conversion can lose information.** If the transfer function has a pole–zero cancellation, the smallest realisation has fewer states than the real system, and the cancelled mode still exists in the hardware. The transfer function genuinely can't see it. That's the sharpest argument for state space: the hidden mode is real, and it can grow while the output looks perfect.

## Discrete time
<!-- bite: 1371ecbf-a7b0-4aa8-a9a8-d114fbdb63fb -->

A computer updates its controller every $T$ seconds, so it needs a model that steps from sample to sample:

$$\mathbf{x}[k+1] = A_d\mathbf{x}[k] + B_d\mathbf{u}[k]$$

If the input is held constant between samples (a **zero-order hold**), the exact conversion is

$$A_d = e^{AT}, \qquad B_d = A^{-1}(A_d - I)B \quad \text{(when } A \text{ is invertible)}$$

The car makes it concrete. Its one-state model is $\dot{v} = -0.05v + 0.001u$. With $T = 0.1$ s: $A_d = e^{-0.005} = 0.99501$ and $B_d = (0.99501 - 1)/(-0.05) \times 0.001 = 9.98 \times 10^{-5}$.

## Discrete-time stability
<!-- bite: 2bf586bb-707e-4459-a15b-7927a758531f -->

**Stability moves from the left half plane to the unit disc**: a discrete system is stable when every eigenvalue of $A_d$ has size less than 1, $|\lambda_i| < 1$.

The reason is the mapping $z = e^{sT}$. A continuous pole with negative real part maps to a $z$ inside the unit circle; the imaginary axis maps onto the circle itself. The car's pole at $-0.05$ maps to $e^{-0.005} = 0.995$, just inside. → [[control-theory/44-digital-control-1|44 — Digital Control 1: Sampling and the z-Transform]]

## Practical notes
<!-- bite: 54445f06-999c-4e05-9f54-ee723177c0bd -->

1. **Scale your states.** A model mixing metres and microradians gives a badly conditioned $A$, and every later calculation suffers.
2. **Check the eigenvalues first.** `eig(A)` tells you stability, natural frequencies and time constants at once.
3. **Check the rank of $B$ and $C$.** If they're rank-deficient, an actuator or sensor is redundant, often a modelling mistake.
4. **Watch stiffness.** Eigenvalues many orders of magnitude apart make simulation slow. A mode 1000 times faster than your loop is just a constant to the controller; remove it.
5. **Balanced truncation** is the principled way to shrink a model: it ranks states by how much they matter between input and output, and drops the rest.

## Common pitfalls
<!-- bite: fdf9569d-956f-4f0d-8597-9bf09b612009 -->

1. **Computing $e^{At}$ from the series.** Use a proper routine.
2. **Using the left-half-plane test on a discrete model.** Discrete stability is $|\lambda| < 1$.
3. **Assuming the realisation is unique.** Any similar $A$ is just as correct.
4. **Trusting a transfer function to show every mode.** A cancelled mode is invisible there but real.

## Check your understanding
<!-- bite: 8dc81c9e-04a2-44bf-a60e-ab1ca7f2aae4 -->

Try each one before you open the answer.

1. <!-- q: mcq id="d0a7e4b2" -->
   $A = \begin{bmatrix}0 & 1 \\ -6 & -5\end{bmatrix}$. What are its eigenvalues?

   - [x] $-2$ and $-3$
   - [ ] $2$ and $3$
   - [ ] $-1$ and $-6$
   - [ ] $-2.5 \pm 1.9j$

   <details><summary>Answer</summary>

   $\det(sI - A) = s^2 + 5s + 6 = (s+2)(s+3)$, so $-2$ and $-3$. Stable.

   </details>

2. <!-- q: mcq id="7f3e1c08" -->
   A model has $A = \begin{bmatrix}0 & 1 \\ 4 & 0\end{bmatrix}$. Is it stable?

   - [ ] Yes, both eigenvalues are negative
   - [x] No, one eigenvalue is $+2$
   - [ ] Marginally, the eigenvalues are $\pm 2j$
   - [ ] It can't be decided without $B$

   <details><summary>Answer</summary>

   $\det(sI - A) = s^2 - 4$, so $s = \pm 2$. The $+2$ is unstable: an inverted-pendulum-like system.

   </details>

3. <!-- q: exact id="2e5c8b71" answer="0.5" accept="1/2" -->
   A model has $A = -2$, $B = 1$, $C = 1$, $D = 0$. What is the DC gain of $G(s) = C(sI - A)^{-1}B$?

   <details><summary>Answer</summary>

   $G(s) = 1/(s + 2)$, so $G(0) = 0.5$.

   </details>

4. <!-- q: exact id="c9b6f2e3" answer="0.9048" sigfigs="3" -->
   A continuous model $\dot{x} = -x$ is sampled every $T = 0.1$ s. What is $A_d$?

   <details><summary>Answer</summary>

   $A_d = e^{-0.1} = 0.905$.

   </details>

5. <!-- q: mcq id="5d1a9e46" -->
   A discrete system has eigenvalues $0.5$ and $-1.2$. Is it stable?

   - [ ] Yes, one eigenvalue is negative
   - [x] No, $|-1.2| > 1$
   - [ ] Yes, both are real
   - [ ] Marginally

   <details><summary>Answer</summary>

   Discrete stability needs every $|\lambda| < 1$. $|-1.2| = 1.2$, so it is unstable.

   </details>

## Before moving on
<!-- bite: 0f7eaabd-0a7d-4788-98e0-63c909b7ddc8 -->

You can solve the state equation, find poles as eigenvalues, convert to and from transfer functions, and discretise. **Next:** [[control-theory/32-state-space-3|32 — State Space 3: From Transfer Function to State Space]], which goes the other way: from a transfer function to a state-space model.

## Related
<!-- bite: c3c2557f-3029-408e-8299-14a95fcb9308 -->

- [[control-theory/03-modelling-1|03 — Modelling 1: From Physics to Transfer Functions]]: poles from the other side.
- [[control-theory/52-lyapunov-stability-1|52 — Lyapunov Stability 1: What Stable Means]]: eigenvalue stability tests, made rigorous.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: c1b8386e-2a02-4273-8953-376d1e2e47ea -->

**Level:** Advanced. **Covers:** the solution of the state equation, the matrix exponential, eigenvalues as poles, modal form, converting to and from transfer functions, and discretisation and discrete stability.

**Where it sits:** lesson 31 of 58, part 2 of 4 on state space.

**Source:** `[reference]`, assembled from standard control texts. Numbers checked in `scripts/diagrams/control_theory.py`.
