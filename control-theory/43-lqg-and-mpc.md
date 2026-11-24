---
id: e10703ee-2de1-4556-9c1d-287b346c5259
---

# LQG and MPC

LQG joins LQR with a Kalman filter, and model predictive control re-solves a short optimal-control problem at every step so it can respect hard limits.

## Before you start
<!-- bite: 41161cc2-5db6-49dc-b773-b58cab4b0157 -->

You should have read [[control-theory/42-lqr|42 — LQR]] and [[control-theory/37-kalman-filter|37 — The Kalman Filter]].

After this lesson you will be able to:

1. say what LQG is and why its margins aren't guaranteed;
2. name the main LQR variants and when each is used;
3. explain receding-horizon control and why constraints are MPC's whole point;
4. decide between PID, LQR and MPC for a given problem.

## What this lesson covers
<!-- bite: 8e7ff2d9-9d34-457c-8064-6d480f029aac -->

LQR needs the full state, and lesson 36 showed how to estimate it. Put the best controller and the best estimator together and you'd expect the best of both. You get something subtler, and the story of finding that out launched a whole field. Then we meet the modern workhorse, model predictive control, which does what LQR can't: respect the actuator's limits on purpose.

## The kid version
<!-- bite: 5a058d00-a517-429f-bb57-780e8896a203 -->

Planning a long walk by phone map: you plan the next kilometre, take *one* step, look up, and plan again from where you actually are. You never follow the old plan blindly, and you always plan around the river you know you can't cross. That's MPC: plan ahead a little, act a little, re-plan.

**Where the analogy stops working.** Re-planning a walk takes you a moment. MPC must solve an optimisation problem every sample, maybe hundreds of times a second, and if the computer can't finish in time, the plan is late.

## LQG and the loss of margins
<!-- bite: 44e65512-e784-44b5-af27-5bddeb691663 -->

Combine LQR with a Kalman filter and you get **LQG**, linear quadratic Gaussian: optimal control with optimal estimation, the classic modern-control package. The separation principle (lesson 36) lets you design the two gains independently.

But here's the shock. **LQG has no guaranteed stability margins.** In 1978 John Doyle published a paper titled *"Guaranteed Margins for LQG Regulators"*. Its abstract is three words: **"There are none."**

LQR's beautiful margins (lesson 42) **do not survive adding the observer.** An LQG design can be arbitrarily fragile. That result started robust control as a field (lesson 29).

## What to do about LQG
<!-- bite: 8a09edf0-8be5-4158-a1d1-ab56a4d9d289 -->

1. **Loop transfer recovery (LTR).** Deliberately detune the Kalman filter (inflate its $Q$) so the loop gain approaches LQR's and the margins come back. It works, at the cost of a noisier estimate: a real trade, not a free fix.
2. **Or just check.** Compute the actual margins and $M_s$ of the combined design.

Remember this one: **never assume LQG is robust because LQR is.** It's the single most important practical lesson of the pair.

## LQR variants
<!-- bite: f377c4a7-75e6-47b5-9664-ddc10dc8856e -->

1. **LQR with integral action.** Add $\dot{x}_I = r - y$ as an extra state and run LQR on the bigger system: zero steady-state error, and the integrator gets its own weight (lesson 35).
2. **Finite-horizon LQR.** Cost over $[0, T]$ instead of forever. $P$ varies in time and solves a differential Riccati equation backwards from the end, exactly lesson 40's sweep in continuous time. Used when the task genuinely ends, like tracking a trajectory.
3. **LQR tracking.** To follow a reference instead of regulating to zero, add a feedforward term so the steady state is right.
4. **Discrete LQR.** The same thing for $\mathbf{x}_{k+1} = A_d\mathbf{x}_k + B_d\mathbf{u}_k$, and what you actually run on a computer (lessons 40 and 44).

## Model predictive control
<!-- bite: b91bccce-de59-4490-9554-2f9756069200 -->

The most important practical development in modern control. At every sample:

1. Measure (or estimate) the current state.
2. Solve a finite-horizon optimal-control problem over the next $N$ steps, **including the limits**.
3. Apply only the **first** input.
4. Next sample, start again from the new measurement.

That's **receding-horizon** control. The problem solved each time is

$$\min_{\mathbf{u}_0 \ldots \mathbf{u}_{N-1}} \sum_{k=0}^{N-1}\left(\mathbf{x}_k^TQ\mathbf{x}_k + \mathbf{u}_k^TR\mathbf{u}_k\right) + \mathbf{x}_N^TP_f\mathbf{x}_N$$

subject to the dynamics **and the constraints**:

$$\mathbf{u}_{min} \le \mathbf{u}_k \le \mathbf{u}_{max}, \qquad \mathbf{x}_{min} \le \mathbf{x}_k \le \mathbf{x}_{max}$$

## Constraints are the whole point
<!-- bite: 9daabf90-98cd-44e7-b4a5-5b846683c28b -->

No other method handles hard limits on states and inputs properly. LQR pretends the actuator is unlimited, then you saturate and hope; lesson 18's car overshot to 27.8 m/s for exactly that reason. MPC knows the engine stops at 3000 N and plans around it from the start.

What MPC buys:

1. **Hard limits respected by construction**, on states as well as inputs.
2. **Many coupled inputs and outputs**, handled naturally.
3. **Preview**: if you know the future reference (a planned path, a forecast load), MPC uses it.
4. **Nonlinear plants**, if you can afford nonlinear optimisation.

## What MPC costs
<!-- bite: 2b89a618-81b1-4691-bd16-8bc36c7ace83 -->

1. **An optimisation every sample.** With a linear model and quadratic cost it's a quadratic program (QP): fast and reliable. Nonlinear makes it slow and possibly unreliable.
2. **A good model is mandatory.** MPC is only as good as its predictions.
3. **More knobs**: horizon length, terminal cost $P_f$, terminal constraints, sample rate.
4. **Stability isn't automatic**, unlike LQR. It's guaranteed by the right terminal cost and terminal set, and getting those right is real work.

Where it's used: born in refineries in the 1980s (slow processes, costly limit violations, plenty of computing time). Fast QP solvers moved it to millisecond-rate embedded control: rocket landing guidance, car driver-assistance, data-centre cooling and grid battery dispatch.

The unifying idea: **LQR is MPC with an infinite horizon and no constraints. MPC is LQR that re-plans and respects limits.**

## Practical guidance
<!-- bite: 5ddd61c8-6bc4-47bf-8283-4672f148d3ea -->

1. **Start with LQR.** Bryson's rule, tune the ratio, simulate. It's fast to try and usually works.
2. **Check the control signal.** Every time.
3. **Check the margins**, especially with an observer in the loop.
4. **Reach for MPC when constraints bind.** If the design keeps saturating, or you have state limits you must respect, that's the signal, not "MPC is more advanced".
5. **Don't skip the model.** Both methods are model-based and fail quietly when the model is wrong. A well-tuned PID on a plant you understand beats an LQR on a plant you don't (lesson 18).

## Common pitfalls
<!-- bite: ce87e77e-a097-4fd5-8253-3d1991ca6a25 -->

1. **Assuming LQG inherits LQR's margins.** It doesn't; check.
2. **Using MPC without a terminal cost.** A short horizon with no terminal cost can be unstable.
3. **Choosing MPC for prestige.** If nothing saturates and there are no state limits, LQR or PID is simpler.
4. **Forgetting computation time.** The QP must finish within one sample.

## Check your understanding
<!-- bite: 86245f6a-264a-41c4-a966-373a6cc24701 -->

Try each one before you open the answer.

1. <!-- q: mcq id="2d7f9b30" -->
   What are LQG's guaranteed stability margins?

   - [ ] The same as LQR's: infinite gain margin, at least 60° phase margin
   - [ ] At least 6 dB and 45°
   - [x] None: it can be arbitrarily fragile
   - [ ] Twice LQR's

   <details><summary>Answer</summary>

   None. Doyle's 1978 paper showed that adding the Kalman filter removes LQR's guarantees.

   </details>

2. <!-- q: mcq id="a5c81e46" -->
   In receding-horizon control, how much of each solved plan is applied?

   - [ ] All $N$ inputs, then re-plan
   - [ ] Half of them
   - [x] Only the first input; then re-plan from the new measurement
   - [ ] None; it only predicts

   <details><summary>Answer</summary>

   Only the first, so every action is based on the latest measurement.

   </details>

3. <!-- q: gap id="e0b74c19" answers="infinite;constraints|limits" -->
   LQR is MPC with an ___ horizon and no ___.

   <details><summary>Answer</summary>

   Infinite; constraints (limits).

   </details>

4. <!-- q: mcq id="6f3a2d85" -->
   A tank level loop must never let the level exceed 2 m, and the inflow valve often hits fully open. Which controller fits best?

   - [ ] PID with a higher gain
   - [ ] LQR
   - [x] MPC
   - [ ] Pole placement

   <details><summary>Answer</summary>

   MPC: it handles both the input limit and the hard state limit by construction.

   </details>

5. <!-- q: open id="38e1c0b7" -->
   What is loop transfer recovery, and what does it cost?

   <details><summary>Answer</summary>

   It detunes the Kalman filter, raising its process-noise weight, so the LQG loop gain approaches the LQR loop gain and the LQR margins return. The cost is a noisier state estimate, because the filter now trusts measurements more.

   </details>

## Before moving on
<!-- bite: 8b46a873-19fd-485b-b97e-6178fb344a1b -->

You can explain why LQG needs checking and when MPC earns its cost. **Next:** [[control-theory/44-digital-control-1|44 — Digital Control 1: Sampling and the z-Transform]], which turns any of these designs into code running on a real processor.

## Related
<!-- bite: 4fa8ba9e-6885-4720-af54-f1a133b34374 -->

- [[control-theory/29-nyquist-3|29 — Nyquist 3: Uncertainty and Fundamental Limits]]: robust control, which LQG's failure launched.
- [[control-theory/projects|Projects]]: MPC on a constrained system.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 0490ea1a-bab7-4a5b-81c9-8365997bfccb -->

**Level:** Advanced. **Covers:** LQG and its missing margins, loop transfer recovery, LQR variants, model predictive control, its costs, and practical guidance on choosing a controller.

**Where it sits:** lesson 43 of 58, the second of two on modern optimal controllers.

**Source:** `[reference]`, assembled from standard control texts.
