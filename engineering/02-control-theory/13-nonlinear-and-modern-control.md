# Nonlinear and Modern Control

**[Advanced]** — What happens when linearisation isn't enough, the tools for handling it, and where the field is going.

## Why linear methods fail

Everything so far assumed linearity. Real systems aren't, and the failures come in two flavours.

**Nonlinearities you can linearise around** — smooth functions, valid locally. $\sin\theta \approx \theta$ works fine near zero.

**Nonlinearities you can't** — non-smooth, and they don't disappear under a Taylor expansion:

- **Saturation** — every actuator has limits
- **Deadzone** — a valve that doesn't move for the first 5% of command
- **Backlash** — gear play, and it's hysteretic
- **Coulomb friction** — discontinuous at zero velocity, and the reason a position loop can hunt around the setpoint forever
- **Hysteresis** — magnetic, piezo, shape-memory

**And behaviours with no linear analogue at all**, which is the deeper problem:

| Behaviour | What it means |
|---|---|
| **Multiple equilibria** | a pendulum has two; linear systems have one |
| **Limit cycles** | self-sustaining oscillation at a fixed amplitude, independent of initial conditions |
| **Finite escape time** | blowing up in *finite* time, not just exponentially |
| **Chaos** | bounded, deterministic, and unpredictable in practice |
| **Amplitude-dependent response** | small and large inputs produce qualitatively different behaviour |

> **The last one breaks the mental model most.** For a linear system, doubling the input doubles the output — superposition. For a nonlinear one, a system stable for small disturbances can be unstable for large ones. **Stability becomes a local property with a region of attraction, not a global fact.**

## Lyapunov stability

The main analytical tool, and it works without solving anything.

**The idea:** find a scalar "energy-like" function $V(\mathbf{x})$ that is positive everywhere except at the equilibrium and **always decreasing along trajectories**. If one exists, the system converges.

$$V(\mathbf{x}) > 0 \ \text{ for } \mathbf{x} \neq 0, \qquad V(0) = 0, \qquad \dot{V}(\mathbf{x}) < 0$$

$$\implies \text{asymptotically stable}$$

**The intuition is physical.** A ball in a bowl: $V$ is its energy, friction dissipates it, so it must end at the bottom. **Energy is the natural first candidate** for a mechanical system, and often it works directly.

**The two things worth knowing:**

**It requires no solution of the differential equation.** For nonlinear systems, where closed-form solutions rarely exist, that's the whole value.

**It's sufficient, not necessary.** Failing to find a $V$ proves nothing — the system may be perfectly stable and you simply haven't found the right function. **And finding $V$ is an art**, which is the honest limitation of the method. Sum-of-squares programming has automated it for polynomial systems, which helps considerably.

**Region of attraction** — the set of initial conditions from which you converge. A level set of $V$ inside the region where $\dot{V} < 0$ gives a provable estimate, usually conservative. **This is the nonlinear replacement for "it's stable"**: not a yes/no answer, but a set.

**LaSalle's invariance principle** relaxes the requirement to $\dot{V} \leq 0$ plus an argument that the system can't stay where $\dot{V} = 0$. Necessary for most mechanical systems, where damping doesn't act in every direction.

## Describing functions

An engineer's approximation for **predicting limit cycles**, and genuinely useful.

Replace the nonlinearity with an equivalent gain $N(A)$ that **depends on the input amplitude** $A$ — the fundamental-harmonic gain, obtained by assuming a sinusoidal input and keeping only the first Fourier term.

Then apply Nyquist with an amplitude-dependent gain. A limit cycle exists where

$$L(j\omega) = -\frac{1}{N(A)}$$

**Plot $L(j\omega)$ and the $-1/N(A)$ locus on the same diagram; intersections are predicted limit cycles**, and the crossing geometry tells you whether they're stable.

**It's an approximation** — it assumes the plant filters out harmonics well, which requires reasonable lowpass rolloff. But it predicts the amplitude and frequency of oscillation caused by saturation or backlash, which is exactly the practical question when a loop is limit-cycling and you need to know why. → [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist]]

## Practical nonlinear methods

The ones you'd actually reach for, roughly in order of how often.

**Gain scheduling.** Linearise at several operating points, design a linear controller for each, interpolate between them on a measured variable.

**By far the most used nonlinear technique in practice.** Standard in aerospace (scheduled on Mach and altitude), engine control (speed and load), and process control. Simple, effective, and it reuses everything from the linear toolkit.

*Caveats:* stability between design points isn't guaranteed by the point designs, and the scheduling variable must vary **slowly** relative to the dynamics. Schedule too fast and the interpolation itself destabilises the loop.

**Feedback linearisation.** Cancel the nonlinearity with the control input, exactly. For $\dot{x} = f(x) + g(x)u$, choose

$$u = \frac{1}{g(x)}\left(-f(x) + v\right)$$

leaving $\dot{x} = v$, a linear system you then control conventionally.

**The robot arm version is `computed torque control`** and it works well because rigid-body dynamics are known precisely from the model.

*Caveats:* it requires an **exact** model — you're cancelling terms, and cancellation error goes straight into the response. It can demand large control effort. And it may cancel useful natural damping, which is wasteful. **Also watch the internal dynamics** — feedback linearisation can leave unobservable "zero dynamics" that must be stable, the nonlinear analogue of the RHP-zero problem.

**Sliding mode control.** Define a surface $s(\mathbf{x}) = 0$ on which the dynamics behave as you want, then switch the control aggressively to drive the state onto it and keep it there.

$$u = -k\,\text{sign}(s)$$

**Extremely robust** to model error and matched disturbances — provably so, which is rare in nonlinear control.

*The problem is **chattering***: infinite-frequency switching that wears actuators and excites unmodelled high-frequency modes. The standard fix is a **boundary layer** — replace `sign` with a saturation function over a thin band — trading exact convergence for practical smoothness. Common in power electronics, where switching is what the hardware does anyway.

**Backstepping.** A recursive design for systems in cascaded (strict-feedback) form: stabilise the innermost subsystem, then treat its state as a virtual control for the next, building a Lyapunov function as you go. Systematic and gives a stability proof, but it produces complicated control laws and is sensitive to model structure.

**Adaptive control.** Estimate unknown plant parameters online and update the controller.

- **MRAC** — drive the plant to behave like a chosen reference model
- **Self-tuning regulators** — identify, then redesign, continuously

*Caveats worth taking seriously:* adaptive control needs **persistent excitation** to keep the estimates honest, it can drift badly without it, and stability proofs are delicate. **Adaptive systems have caused real accidents** — the X-15 crash in 1967 involved an adaptive controller — and the field's reputation for fragility is earned. Use it where parameters genuinely change a lot and you cannot schedule.

## Where the field is going

Honest orientation on the modern landscape.

**Model Predictive Control** is the dominant modern method, for good reason — constraints, MIMO, preview. Nonlinear MPC is now feasible in real time for many systems. → [[engineering/02-control-theory/11-optimal-control-and-lqr|Optimal Control and LQR]]

**Reinforcement learning** is optimal control without a model — learn the policy from interaction. Impressive on problems where no model exists or the dynamics are too complex to write down.

> **The honest comparison:** RL needs enormous amounts of data, offers no stability guarantee, and transfers poorly from simulation to hardware. Classical control needs a model and gives you provable guarantees. **They're complementary, and the interesting work is in the overlap** — RL for high-level policy with a classical inner loop enforcing safety, or learned dynamics models feeding an MPC. Nobody flies an aircraft on a pure neural policy, and nobody hand-designs a controller for a task with no model. → [[ai-ml/README|AI/ML]]

**Learning-based control** — learn the *model*, then use classical synthesis. Often the practical middle ground: Gaussian-process MPC, iterative learning control for repetitive tasks, and system identification with neural networks. **It keeps the guarantees where they matter** and uses learning where models are hard.

**Safe learning and control barrier functions** — a genuinely useful development. A CBF gives a provable constraint on the control input that keeps the state in a safe set, and it composes with *any* nominal controller, learned or not. It's how you put a hard safety envelope around a policy you don't fully trust.

**Networked and multi-agent control** — consensus, formation control, distributed optimisation. Drone swarms, power grids, traffic. The plant is a graph and stability depends on its connectivity. → [[architecture/04-distributed-systems/README|Distributed Systems]]

**Data-driven control** — behavioural systems theory and Willems' fundamental lemma: **design a controller directly from measured input–output data, with guarantees, without ever identifying a model.** An active and genuinely novel area.

## What to take away

**Classical control is not obsolete.** Most working loops are PID, and most of the value in this track is in notes 03–07.

**Reach for nonlinear methods when linear ones demonstrably fail** — when the operating range is too wide for one linearisation, when a hard nonlinearity dominates, or when the required performance exceeds what a linear design achieves. Not because they're more sophisticated.

**Gain scheduling handles most real nonlinearity** and should be the first thing you try.

**Constraints are the usual reason to leave PID**, and that points at MPC rather than at nonlinear theory.

**A good model is worth more than a clever controller.** That's true across every method in this track — the failures are far more often modelling failures than design failures.

---

## Related
- [[engineering/02-control-theory/11-optimal-control-and-lqr|Optimal Control and LQR]] — MPC, the modern default
- [[engineering/02-control-theory/02-modelling-and-transfer-functions|Modelling]] — linearisation and its limits
- [[robotics/README|Robotics]] — where most of this gets applied
- [[engineering/02-control-theory/README|Control theory map]]
