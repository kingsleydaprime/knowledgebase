# Control Theory

Making a system behave the way you want despite an imperfect model, unpredictable disturbances, and components that drift. The mathematics behind every thermostat, motor drive, autopilot, robot joint, and — if you look at it right — every autoscaler and congestion-control algorithm.

**~21,000 words across 13 notes.** Built August 2026. `[reference]` — see [[engineering/README|the domain note]] on what that means here.

> **The one idea:** measure the output, compare it to what you wanted, and act on the difference. That single loop buys you disturbance rejection, insensitivity to model error, and the ability to stabilise systems that fall over on their own. It also buys you the possibility of instability, amplified noise, and a hard trade between speed and robustness — which is why control is a design discipline and not a recipe.

## Reading order

**Notes 02–07 are classical control** and build strictly in order. **08–11 are state space**, and need linear algebra. **12–13 are implementation and what lies beyond.**

**Orientation**

1. [[engineering/02-control-theory/01-what-control-theory-is|What Control Theory Is]] — **[Beginner → Intermediate]** — open vs closed loop, the $r/y/e/u/d$ vocabulary, what feedback buys and what it costs, and why the field looks like two subjects

**Classical control**

2. [[engineering/02-control-theory/02-modelling-and-transfer-functions|Modelling and Transfer Functions]] — **[Intermediate]** — physics to ODE to $G(s)$, why Laplace is worth it, what poles and zeros mean, and **why right-half-plane zeros cap your bandwidth permanently**
3. [[engineering/02-control-theory/03-time-response|Time Response]] — **[Intermediate]** — $\zeta$ and $\omega_n$, the step-response specifications, dominant poles, system type and steady-state error, and why delay wrecks everything
4. [[engineering/02-control-theory/04-pid-control|PID Control]] — **[Intermediate]** — **the note that matters most.** What each term does, tuning methods that work, and the four implementation details that separate working code from a controller that fights you
5. [[engineering/02-control-theory/05-stability-and-root-locus|Stability and Root Locus]] — **[Intermediate]** — Routh–Hurwitz without factoring polynomials, where the closed-loop poles go as gain rises, lead/lag compensation, and **why cancelling an unstable pole is the most dangerous move in classical design**
6. [[engineering/02-control-theory/06-frequency-response|Frequency Response]] — **[Intermediate]** — Bode plots, loop shaping, what bandwidth costs, and the hard limits on how fast you're allowed to be
7. [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist and Robustness]] — **[Advanced]** — the criterion that handles unstable and delayed plants, **why gain and phase margins can both look fine on a fragile design**, and the waterbed effect made precise

**State space**

8. [[engineering/02-control-theory/08-state-space|State Space]] — **[Advanced]** — $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$, what "state" means, eigenvalues *are* the poles, and why MIMO stops being painful
9. [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Controllability, Observability and Pole Placement]] — **[Advanced]** — can you steer it, can you see it, and the result that if both, you can put the poles anywhere
10. [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]] — **[Advanced]** — estimating the state you can't measure, the separation principle, sensor fusion, and tuning $Q$ and $R$ honestly
11. [[engineering/02-control-theory/11-optimal-control-and-lqr|Optimal Control and LQR]] — **[Advanced]** — designing by minimising a cost instead of guessing pole locations, LQR's guaranteed margins, **why LQG loses them**, and MPC

**Implementation and beyond**

12. [[engineering/02-control-theory/12-digital-control|Digital Control]] — **[Intermediate → Advanced]** — sampling, the $z$-transform, discretising properly, fixed-point implementation, and **the failure modes that only appear on hardware**
13. [[engineering/02-control-theory/13-nonlinear-and-modern-control|Nonlinear and Modern Control]] — **[Advanced]** — Lyapunov, limit cycles, gain scheduling, sliding mode, and an honest read on where RL fits

## The things worth carrying

If the algebra fades, these keep paying:

1. **Stable means every closed-loop pole is in the left half plane.** Everything else in classical control is machinery for arranging that with margin → [[engineering/02-control-theory/05-stability-and-root-locus|05]]
2. **Each integrator kills the steady-state error to one higher order of input.** That's the whole reason the I term exists → [[engineering/02-control-theory/03-time-response|03]]
3. **Every real PID needs anti-windup, a filtered derivative, and derivative-on-measurement.** A textbook PID misbehaves the first time it saturates, and it will saturate → [[engineering/02-control-theory/04-pid-control|04]]
4. **$\zeta \approx PM°/100$.** The bridge between frequency-domain design and time-domain specifications → [[engineering/02-control-theory/06-frequency-response|06]]
5. **Good margins don't guarantee robustness; $M_s < 2$ does.** GM and PM measure two directions, and uncertainty comes from all of them → [[engineering/02-control-theory/07-nyquist-and-robustness|07]]
6. **RHP zeros and delays cap your bandwidth. Unstable poles set a floor.** If those constraints collide, no controller exists — change the plant → [[engineering/02-control-theory/07-nyquist-and-robustness|07]]
7. **Cancelling an unstable pole makes it unobservable, not gone.** The output looks perfect while the state diverges → [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|09]]
8. **A zero-order hold costs you $T/2$ of delay.** The commonest reason a controller that simulated beautifully oscillates on hardware → [[engineering/02-control-theory/12-digital-control|12]]
9. **Jitter is worse than latency.** Constant delay you design around; varying delay changes your effective gains every sample → [[engineering/02-control-theory/12-digital-control|12]]
10. **A good model beats a clever controller.** Most control failures are modelling failures → [[engineering/02-control-theory/13-nonlinear-and-modern-control|13]]

## Where this connects

**Software people meet control theory more often than they realise.** Three real instances, all with the classical pathologies:

- **TCP congestion control** — a distributed feedback loop where the plant is the network → [[foundations/networking/08-congestion-control|Congestion Control]]
- **Autoscaling** — sensor delay (metrics lag), actuator delay (instances take minutes to boot), and a noisy plant. It oscillates for exactly the reasons note 03 explains
- **Rate limiting and backpressure** — a controller with a saturating actuator, and it needs anti-windup for the same reason a PID does

**Within engineering:**

- [[robotics/README|Robotics]] — cascaded position/velocity/current loops, Kalman-based localisation, and where most of notes 08–11 get used
- [[engineering/01-continuum-mechanics/README|Continuum Mechanics]] — the plants you're controlling, and where structural resonances come from
- [[hardware/README|Hardware & Embedded]] — op-amps as the cleanest example of feedback buying accuracy the components don't have, and where note 12 gets implemented

## Prerequisites and gaps

**You need** complex numbers, differential equations, Laplace transforms (introduced in note 02), and linear algebra — eigenvalues and eigenvectors especially — for the state-space half. [[ai-ml/00-foundations/03-mathematics/README|The vault's maths notes]] cover the linear algebra; the differential equations and transform theory are a genuine gap.

**Within the track:** no worked design examples end to end, no Bode/root-locus plots beyond ASCII sketches, no MIMO worked example, nothing on system identification in depth, and no treatment of $\mathcal{H}_\infty$ synthesis beyond naming it.

## The honest note

**This is a map, not a lab.** Control theory is learned by tuning a real loop and watching it oscillate — the intuition for "that's too much integral" comes from having done it, not from reading the table.

The cheapest way to close that gap: **simulate one.** A hundred lines of Python — a second-order plant, a discrete PID, a step input, a plot — and every claim in notes 03 and 04 becomes something you can check. Add saturation and watch windup happen. Add noise and watch the derivative term ruin everything. It takes an afternoon and it's worth more than the rest of the track.

**A physical build is better still**: a motor, an encoder, and a microcontroller. Everything in note 12 stops being abstract the moment you sample too slowly and the thing screams. → [[build-your-own-shit/README|build-your-own-shit]]

## Related
- [[engineering/README|Engineering]] — the umbrella
- [[engineering/01-continuum-mechanics/README|Continuum Mechanics]] — the other engineering track
- [[robotics/README|Robotics]] — where this gets applied
- [[hardware/README|Hardware & Embedded]] — where this gets implemented
