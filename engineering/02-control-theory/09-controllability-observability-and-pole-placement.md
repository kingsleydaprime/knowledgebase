# Controllability, Observability and Pole Placement

**[Advanced]** — Can you steer it? Can you see it? And if both, you can put the poles anywhere you like.

## Controllability

> **A system is controllable if you can drive the state from any initial value to any desired value in finite time, using the available inputs.**

The test:

$$\mathcal{C} = \begin{bmatrix} B & AB & A^2B & \cdots & A^{n-1}B \end{bmatrix}$$

**Controllable iff $\text{rank}(\mathcal{C}) = n$.**

**Why that matrix.** $B$ is where the input pushes directly. $AB$ is where that push has propagated after an instant. $A^2B$ the instant after. The columns span everything the input can eventually reach — the **reachable subspace**. Full rank means it reaches everywhere. (Cayley–Hamilton is why the series stops at $A^{n-1}$: higher powers add nothing new.)

**What uncontrollable means physically:** there's a direction in state space you cannot influence, no matter what you do with the actuators.

- A symmetric two-mass system driven exactly at its centre of symmetry cannot excite the antisymmetric mode
- A satellite with a thruster pointing through the centre of mass cannot produce torque
- **A quadcopter with three rotors** — four degrees of freedom to control, three inputs

**If an uncontrollable mode is unstable, the system cannot be stabilised.** Full stop, by any controller. That's the strongest negative result in the subject, and it's worth checking before designing anything.

**Stabilisable** is the weaker, sufficient condition: all *unstable* modes are controllable. Uncontrollable stable modes are usually acceptable — they decay on their own and you simply can't influence them.

**The rank test is numerically fragile.** $\mathcal{C}$ is often badly conditioned, and "rank 4" versus "rank 3 with a tiny singular value" is a judgement call. **Use the smallest singular value, not the rank** — it tells you *how* controllable, which is what you actually want to know. A system that is technically controllable but nearly not will demand enormous control effort in that direction. Prefer the **PBH test** for reliability: the pair $(A,B)$ is controllable iff $\text{rank}[\,sI - A \quad B\,] = n$ for every eigenvalue $s$ of $A$ — and it tells you *which mode* is the problem.

## Observability

The dual question.

> **A system is observable if you can determine the initial state from measuring the output over a finite interval.**

$$\mathcal{O} = \begin{bmatrix} C \\ CA \\ CA^2 \\ \vdots \\ CA^{n-1} \end{bmatrix}$$

**Observable iff $\text{rank}(\mathcal{O}) = n$.**

$C$ is what you see directly; $CA$ is what you see of the state's motion; and so on. Full rank means nothing is hidden.

**Unobservable means a state can be doing something arbitrary while the output shows nothing.** Measure only position and you may not distinguish two internal configurations; measure only a sum of temperatures and you can't tell which zone is hot.

**Detectable** is the weaker condition: all unstable modes are observable. Which is what actually matters — **an unobservable stable mode decays harmlessly; an unobservable unstable mode grows without any indication at the output** until something breaks.

**That's the formal version of the pole–zero cancellation warning** from [[engineering/02-control-theory/05-stability-and-root-locus|note 05]]. Cancelling an unstable pole with a controller zero makes it unobservable. The transfer function looks perfect. The state diverges.

### Duality

$$(A, B) \text{ controllable} \iff (A^T, B^T) \text{ observable}$$

**Every controllability result has an observability twin.** It's not a coincidence — the observer design in [[engineering/02-control-theory/10-observers-and-kalman|note 10]] is literally the controller design applied to the transposed system, and it means learning one gets you the other free.

| Control | Estimation |
|---|---|
| Controllability | Observability |
| $\mathcal{C} = [B, AB, \ldots]$ | $\mathcal{O} = [C; CA; \ldots]$ |
| State feedback gain $K$ | Observer gain $L$ |
| LQR | Kalman filter |
| Stabilisable | Detectable |

## Minimal realisation

A state-space model is **minimal** iff it's both controllable and observable.

**Non-minimal means the model has states the transfer function can't see** — states that are unreachable from the input, unobservable at the output, or both. Convert to a transfer function and they vanish silently.

```
                  observable    unobservable
 controllable   │  ← this is    │ can drive it,
                │    the TF     │ can't see it
 uncontrollable │ can see it,   │ completely
                │ can't drive   │ invisible
```

**Only the top-left block appears in the transfer function.** The other three are real dynamics that a classical model is blind to — Kalman's decomposition, and the single clearest argument for state space.

## Pole placement

Given controllability, here's the payoff.

**Full state feedback:**

$$\mathbf{u} = -K\mathbf{x}$$

Substituting into $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$:

$$\dot{\mathbf{x}} = (A - BK)\mathbf{x}$$

**The closed-loop dynamics are the eigenvalues of $A - BK$.**

> **If $(A,B)$ is controllable, you can place the eigenvalues of $A - BK$ anywhere you want.**

That's a remarkable result. Not "improve the response" — **place the poles exactly**, at whatever locations you specify. Controllability is precisely the condition for it.

**Computing $K$:**

- **Ackermann's formula** — closed form, and numerically poor above about 5th order. Fine for hand calculation, fine for teaching
- **`place()` / robust pole assignment** — what you should use. For MIMO, $K$ isn't unique, and the extra freedom is used to make the eigenvalues as insensitive as possible to perturbation
- **By hand:** match coefficients between $\det(sI - A + BK)$ and your desired characteristic polynomial

### Choosing where to put them

**The part that's actually hard.** Placement is mechanical; deciding *where* is the design.

**Start from the specification:** $\zeta$ from the overshoot requirement, $\zeta\omega_n$ from settling time, then place a dominant pair there and the rest 5–10× further left. → [[engineering/02-control-theory/03-time-response|Time Response]]

**Standard patterns** worth knowing:

- **Butterworth** — poles evenly spaced on a semicircle of radius $\omega_0$. Good all-round transient, no dominant mode
- **Bessel** — maximally flat group delay, so minimal overshoot. Good when overshoot is the binding constraint
- **ITAE** — minimises $\int t|e|dt$. Tabulated coefficients, good compromise response

**Three warnings, and they're where beginners come unstuck:**

**Fast poles cost control effort.** Effort scales roughly with how far you move a pole. Demand 10× the natural bandwidth and you'll demand torque the motor doesn't have — and once it saturates, all your careful placement is void.

**Fast poles amplify noise.** High gain on a noisy measurement gives noisy actuation, which wears hardware and can excite unmodelled modes.

**Pole placement says nothing about robustness.** You can place poles beautifully and end up with terrible stability margins — the classical margins simply aren't part of the calculation. **This is the main practical criticism of the method**, and it's why [[engineering/02-control-theory/11-optimal-control-and-lqr|LQR]] is usually preferred: same structure, but the gain comes from an optimisation with known margin guarantees, and you tune weights rather than guessing pole locations.

## Integral action

State feedback alone has the same failing as proportional control: **steady-state error.** $\mathbf{u} = -K\mathbf{x}$ drives the state to zero, which isn't the same as tracking a reference.

The fix is the same as in PID — **add an integrator as an extra state**:

$$\dot{x}_I = r - y$$

Augment the system:

$$\begin{bmatrix}\dot{\mathbf{x}} \\ \dot{x}_I\end{bmatrix} = \begin{bmatrix}A & 0 \\ -C & 0\end{bmatrix}\begin{bmatrix}\mathbf{x} \\ x_I\end{bmatrix} + \begin{bmatrix}B \\ 0\end{bmatrix}\mathbf{u} + \begin{bmatrix}0 \\ 1\end{bmatrix}r$$

then place poles for the augmented $(n+1)$-state system. The result is **state feedback plus integral action** — zero steady-state error, robust to constant disturbances and to plant gain error.

**And it needs anti-windup for exactly the reason PID does.** → [[engineering/02-control-theory/04-pid-control|PID Control]]

## The catch

$\mathbf{u} = -K\mathbf{x}$ requires **the full state**.

You rarely have it. You have $\mathbf{y} = C\mathbf{x}$ — a few sensors, not every state. Position but not velocity. One temperature out of five.

Two options:

**Add sensors.** Sometimes right, often expensive, and some states aren't directly measurable at all.

**Estimate the state from what you can measure.** Which requires observability — and is the entire subject of the next note.

---

## Related
- [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]] — getting the state you don't measure
- [[engineering/02-control-theory/08-state-space|State Space]] — the representation
- [[engineering/02-control-theory/11-optimal-control-and-lqr|Optimal Control and LQR]] — choosing $K$ by optimisation instead
- [[engineering/02-control-theory/README|Control theory map]]
