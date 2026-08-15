# Optimal Control and LQR

**[Advanced]** — Designing a controller by minimising a cost instead of guessing pole locations. The one method that scales to MIMO without pain.

## The shift in thinking

Pole placement asks: *where do I want the poles?* On a 12-state quadcopter that's twelve numbers to guess, with no principled way to choose them.

Optimal control asks a better question: **what do I actually care about, and what will I pay for it?**

$$J = \int_0^\infty \left(\mathbf{x}^T Q \mathbf{x} + \mathbf{u}^T R \mathbf{u}\right)dt$$

- $\mathbf{x}^T Q\mathbf{x}$ — **penalty on state error.** "Being off target is bad"
- $\mathbf{u}^T R\mathbf{u}$ — **penalty on control effort.** "Actuation costs fuel, wear, and heat"

Minimise $J$ subject to $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$, and the answer is the controller.

**$Q$ and $R$ are the design knobs, and they're physically meaningful in a way pole locations aren't.** "Position error matters ten times more than velocity error, and I have limited torque" is a statement an engineer can make with confidence. "Put the poles at $-3 \pm 4j$" usually isn't.

## The LQR solution

**Linear plant, Quadratic cost, Regulator.** The result is remarkably clean:

$$\boxed{\mathbf{u} = -K\mathbf{x}, \qquad K = R^{-1}B^T P}$$

where $P$ solves the **algebraic Riccati equation**:

$$A^TP + PA - PBR^{-1}B^TP + Q = 0$$

**The optimal controller is linear state feedback.** Not something exotic — the same structure as pole placement, with $K$ computed rather than chosen. Which is why LQR is usually the better way to *do* pole placement: you tune $Q$ and $R$, and the poles land somewhere sensible on their own.

**In code it's one line** — `K = lqr(A, B, Q, R)`. The Riccati solver is standard and reliable. **You don't solve it by hand**; the effort goes entirely into choosing the weights.

## Choosing Q and R

The actual design work.

**Start diagonal.** $Q = \text{diag}(q_1, \ldots, q_n)$, $R = \text{diag}(r_1, \ldots, r_m)$. Cross terms are rarely necessary.

**Bryson's rule** — the standard starting point, and it handles the units problem:

$$q_i = \frac{1}{(\text{max acceptable } x_i)^2}, \qquad r_j = \frac{1}{(\text{max acceptable } u_j)^2}$$

**This normalises everything.** Each term contributes about 1 when that variable is at its acceptable limit, so states measured in radians and states measured in metres become comparable. Without it, a badly scaled $Q$ silently ignores whichever state has small numerical values.

**Then tune the ratio.** Only $Q/R$ matters — scaling both by the same factor changes nothing:

- **$Q$ up relative to $R$** → tighter regulation, faster, more control effort, more noise amplification
- **$R$ up relative to $Q$** → gentler, slower, less effort, more robust

**The workflow that works:** Bryson's rule → simulate → is the actuator saturating? Raise $R$. Too slow? Raise $Q$. Iterate. **Always check the control signal**, not just the state response — an LQR design that looks perfect and demands 3× the available torque is not a design.

**Two things people miss:**

**LQR guarantees stability whenever $(A,B)$ is stabilisable and $(A, Q^{1/2})$ is detectable.** You get a stable closed loop by construction, for any positive weights. That's a strong property — you cannot accidentally design an unstable LQR.

**Optimal means optimal for that cost function.** If the response is bad, the cost function is wrong, not the solver. LQR is a machine for turning a statement of priorities into a controller; garbage priorities give a garbage controller, faithfully.

## Why it beats pole placement

| | Pole placement | LQR |
|---|---|---|
| Tuning knobs | $n$ pole locations | $Q$, $R$ — physically meaningful |
| MIMO | $K$ not unique, awkward | natural, one solution |
| Control effort | not considered | **explicitly penalised** |
| Stability | you must ensure it | **guaranteed** |
| Margins | none guaranteed | **GM ∞, PM ≥ 60°** |
| Systematic | no | yes |

**That margin row is the striking result.** LQR state feedback has an **infinite upward gain margin, a gain margin of 0.5 downward, and at least 60° of phase margin** — for every LQR design, automatically. → [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist and Robustness]]

Which is exactly what pole placement fails to provide.

## LQG and the loss of margins

Combine LQR with a [[engineering/02-control-theory/10-observers-and-kalman|Kalman filter]] and you get **LQG** — Linear Quadratic Gaussian. Optimal control with optimal estimation, and it's the classic modern-control package.

The separation principle applies: design the LQR gain and the Kalman gain independently, combine.

> **But LQG has no guaranteed stability margins.** Doyle's 1978 paper — titled, memorably, *"Guaranteed Margins for LQG Regulators"*, whose abstract is one sentence: **"There are none."**

The beautiful LQR margins **do not survive the introduction of the observer.** An LQG design can be arbitrarily fragile, and it was a genuine shock at the time — it's the result that launched robust control as a field.

**What to do about it:**

**LTR (Loop Transfer Recovery)** — deliberately detune the Kalman filter (inflate $Q$) so the loop gain approaches the LQR loop gain and the margins come back. It works, at the cost of a noisier estimate. A real trade, not a free fix.

**Or just check.** Compute the actual margins and $M_s$ of the combined design. **Never assume LQG is robust because LQR is** — this is the single most important practical takeaway of the note.

## Variants

**LQR with integral action** — augment with $\dot{x}_I = r - y$ and run LQR on the augmented system. Zero steady-state error, and you get to weight the integrator alongside everything else. → [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Integral action]]

**Finite horizon LQR** — cost over $[0, T]$ instead of $[0,\infty)$. $P$ becomes time-varying and solves a differential Riccati equation backwards from a terminal cost. Used for trajectory tracking, where the task genuinely ends.

**LQR tracking** — for following a reference rather than regulating to zero, add a feedforward term so the steady state is right.

**Discrete LQR** — the same thing for $\mathbf{x}[k+1] = A_d\mathbf{x}[k] + B_d\mathbf{u}[k]$, and what you actually implement. → [[engineering/02-control-theory/12-digital-control|Digital Control]]

## Model Predictive Control

**The most important practical development in modern control**, and where a lot of this leads.

At each time step: solve a finite-horizon optimal control problem over the next $N$ steps, apply only the first input, then **re-solve at the next step with fresh measurements**. That's *receding horizon* control.

$$\min_{\mathbf{u}_0 \ldots \mathbf{u}_{N-1}} \sum_{k=0}^{N-1}\left(\mathbf{x}_k^TQ\mathbf{x}_k + \mathbf{u}_k^TR\mathbf{u}_k\right) + \mathbf{x}_N^TP_f\mathbf{x}_N$$

subject to the dynamics **and constraints**:

$$\mathbf{u}_{min} \leq \mathbf{u}_k \leq \mathbf{u}_{max}, \qquad \mathbf{x}_{min} \leq \mathbf{x}_k \leq \mathbf{x}_{max}$$

**Constraints are the entire point.** No other method handles hard limits on states and inputs properly. LQR pretends the actuator is unlimited and then you saturate and hope; MPC knows the limit and plans around it.

**What it buys:**
- **Hard constraints respected by construction** — including on *states*, not just inputs
- **MIMO with coupling, handled naturally**
- **Preview** — if you know the future reference (a planned trajectory, a forecast load), MPC uses it
- **Nonlinear plants**, if you can afford nonlinear optimisation

**What it costs:**
- **You solve an optimisation problem every sample.** A QP if everything is linear, which is fast and reliable; nonconvex and slow if not
- **A good model is mandatory** — MPC is only as good as its predictions
- **Tuning has more knobs**: horizon length, terminal cost, terminal constraint, sample rate
- **Stability isn't automatic**, unlike LQR. It's guaranteed via terminal cost and terminal set conditions, and getting those right is real work

**Where it's used:** born in refineries and chemical plants in the 1980s (slow processes, expensive constraint violations, plenty of computing time). Now everywhere — **Tesla's autopilot, SpaceX's landing guidance, data-centre thermal management, and grid-scale battery dispatch are all MPC.** Fast QP solvers and cheap compute moved it from "slow processes only" to millisecond-rate embedded control.

> **The unifying idea:** LQR is MPC with an infinite horizon and no constraints. MPC is LQR that re-plans and respects limits. If you understand LQR, MPC is a short step.

## Practical guidance

**Start with LQR.** Bryson's rule, tune the ratio, simulate. It's fast to try and it usually works.

**Check the control signal.** Every time.

**Check the margins**, especially with an observer in the loop.

**Reach for MPC when constraints bind.** If your design keeps saturating, or you have state limits you must respect, that's the signal — not "MPC is more advanced".

**Don't skip the model.** Both methods are model-based, and both fail quietly when the model is wrong. A well-tuned PID on a plant you understand beats an LQR on a plant you don't. → [[engineering/02-control-theory/04-pid-control|PID Control]]

---

## Related
- [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Pole Placement]] — the alternative way to choose $K$
- [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]] — the estimation half of LQG
- [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist and Robustness]] — why margins matter here
- [[engineering/02-control-theory/README|Control theory map]]
