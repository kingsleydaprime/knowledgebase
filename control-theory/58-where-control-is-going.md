---
id: 12727cd0-5759-4ccd-8971-0e2053dba0c4
---

# Where Control Is Going

Modern control is moving towards optimising on every step, learning from data and provable safety, while PID still runs most loops.

## Before you start
<!-- bite: d51865b5-fb71-4532-a499-85ffd6d5bd58 -->

You should have read [[control-theory/43-lqg-and-mpc|43 — LQG and MPC]] and [[control-theory/57-nonlinear-design-2|57 — Nonlinear Design 2: Feedback Linearisation, Sliding Mode and Adaptive Control]].

After this lesson you will be able to:

1. place reinforcement learning against classical control, with the strengths of each;
2. describe learning-based control and control barrier functions;
3. name the main trends: MPC, networked and multi-agent control, data-driven control;
4. say what to take away from the whole subject.

## What this lesson covers
<!-- bite: 2bd08de8-c1c9-4de7-8670-c9a314a8576a -->

You've now covered the core of control: classical loops, state space, optimal control, digital implementation and nonlinear systems. This short last lesson is an honest map of the frontier, so you know where each new idea sits relative to what you've learned, and what's hype.

## The kid version
<!-- bite: 7601e50d-b8a7-4bf3-b0db-7ffd33297d24 -->

Two ways to learn to ride a bike: read the physics and work out exactly how to balance, or just keep trying and falling until your body figures it out. Engineers used to do only the first. Now computers can do the second, millions of falls in a simulator. The best riders use both: the physics for what's certain, practice for what isn't.

**Where the analogy stops working.** A child's falls are cheap. A real aircraft can't fall a million times, which is why learning alone isn't enough for anything dangerous.

## Model predictive control everywhere
<!-- bite: d588b5de-f80c-4d86-8b1e-e28a8d7ad455 -->

MPC (lesson 43) is the dominant modern method, for good reason: constraints, many inputs, preview. Fast solvers now make **nonlinear MPC** feasible in real time for many systems, from car driver-assistance to rocket landing. If one modern method is worth getting good at, it's this.

## Reinforcement learning
<!-- bite: 56387027-ef1e-44d4-86f7-9676a102216e -->

**Reinforcement learning** (RL) is optimal control without a model: learn the policy (the controller) from interaction, by trial and reward. It's impressive on problems with no usable model, or dynamics too complex to write down, like legged robots and game playing.

The honest comparison:

1. **RL** needs enormous amounts of data, gives no stability guarantee, and transfers poorly from simulation to hardware.
2. **Classical and modern control** need a model, and give provable guarantees.

They're complementary, and the interesting work is in the overlap: RL for the high-level decisions with a classical inner loop keeping things safe, or learned models feeding an MPC. Nobody flies an airliner on a pure neural network policy, and nobody hand-designs a controller for a task with no model. → [[machine-learning/index|Machine learning]]

## Learning the model, not the controller
<!-- bite: 2e2757ba-10b5-49ec-98f2-f1f7e6c1abd2 -->

**Learning-based control** learns the *model*, then uses the classical design methods on it: Gaussian-process MPC, iterative learning control for repeated tasks, system identification with neural networks. It's often the practical middle ground, because **it keeps the guarantees where they matter** and uses learning where models are hard.

## Safety around controllers you don't trust
<!-- bite: 60c04b4c-78d8-45a0-8aa0-6d46099b559e -->

A **control barrier function** (CBF) is a Lyapunov-like function for *safety* rather than stability: it gives a provable condition on the input that keeps the state inside a safe set. Its big practical value is that it works with *any* nominal controller, learned or not: a CBF filter sits after the controller and changes its command only when the command would leave the safe set. It's how you put a hard safety envelope around a policy you don't fully trust.

## Networks, swarms and data
<!-- bite: 822c005b-5f54-4882-95da-63e6d8977fd3 -->

1. **Networked and multi-agent control**: consensus, formations, distributed optimisation. Drone swarms, power grids, traffic. The "plant" is a graph, and stability depends on how it's connected. → [[architecture/04-distributed-systems/index|Distributed systems]]
2. **Data-driven control**: behavioural systems theory and Willems' fundamental lemma. **Design a controller directly from measured input and output data, with guarantees, without ever identifying a model.** An active and genuinely new area.

## What to take away
<!-- bite: 6a3f8f3c-d421-48b1-b2ac-e4651693cf9b -->

1. **Classical control isn't obsolete.** Most working loops are PID, and much of the value in this subject is in lessons 03 to 29.
2. **Reach for nonlinear methods when linear ones demonstrably fail**: when the operating range is too wide for one linearisation, a hard nonlinearity dominates, or the performance asked for is beyond a linear design. Not because they're more sophisticated.
3. **Gain scheduling handles most real nonlinearity**, so try it first.
4. **Constraints are the usual reason to leave PID**, and they point to MPC rather than to nonlinear theory.
5. **A good model is worth more than a clever controller.** Across every method in this subject, failures are far more often modelling failures than design failures.

## Common pitfalls
<!-- bite: 5e0f1b42-2f60-4084-a414-48c92fd361d1 -->

1. **Treating RL as a replacement for control theory.** It lacks the guarantees safety-critical systems need.
2. **Adopting a fashionable method for a problem PID solves.** Simple loops deserve simple controllers.
3. **Skipping the model because "the network will learn it".** It learns what the data shows, and nothing outside it.
4. **Forgetting constraints.** They decide more designs than any optimality criterion.

## Check your understanding
<!-- bite: 1be183a6-3048-47c6-8c73-e1c85ca120c1 -->

Try each one before you open the answer.

1. <!-- q: mcq id="2f9c7d04" -->
   What is the main advantage classical and modern control keep over pure reinforcement learning?

   - [ ] They need less computing power to train
   - [x] They come with provable guarantees such as stability margins
   - [ ] They work without any model
   - [ ] They handle more inputs

   <details><summary>Answer</summary>

   Provable guarantees. RL can find good policies without a model, but it offers no stability guarantee and needs huge amounts of data.

   </details>

2. <!-- q: mcq id="a6e04b31" -->
   What does a control barrier function do?

   - [ ] It replaces the controller entirely
   - [ ] It speeds up an MPC solver
   - [x] It provably keeps the state in a safe set by adjusting any controller's command only when needed
   - [ ] It estimates unmeasured states

   <details><summary>Answer</summary>

   It's a safety filter: it works with any nominal controller and changes its command only when the command would leave the safe set.

   </details>

3. <!-- q: gap id="d8b15e72" answers="model;controller|policy" -->
   Learning-based control usually learns the ___ and then designs the ___ with classical methods, keeping the guarantees.

   <details><summary>Answer</summary>

   The model; the controller.

   </details>

4. <!-- q: mcq id="5c3a9f16" -->
   A loop keeps saturating its actuator and must respect a temperature limit. Which direction does this lesson point you?

   - [ ] Reinforcement learning
   - [ ] Sliding mode
   - [x] Model predictive control
   - [ ] Higher PID gains

   <details><summary>Answer</summary>

   Constraints that bind point to MPC.

   </details>

5. <!-- q: open id="e17b6c80" -->
   "A good model is worth more than a clever controller." Explain with an example from this subject.

   <details><summary>Answer</summary>

   Any of several: feedback linearisation leaves every model error in the response (lesson 57); MPC is only as good as its predictions (lesson 43); a well-tuned PID on a plant you understand beats an LQR on a plant you don't (lesson 18). In each case the controller faithfully acts on the model, so a wrong model gives a wrong controller, however sophisticated.

   </details>

## Before moving on
<!-- bite: 4e4b8121-b3ef-4ade-a923-5362401177ae -->

That's the subject. To turn it into skill, build something: the [[control-theory/projects|projects]] start with tuning a PID on a simulated plant and end with balancing a real pendulum. And the [[control-theory/optimal-control-problem-bank|problem bank]] has every problem from the optimal-control sheets.

## Related
<!-- bite: 0caeef97-8af8-4c7b-b794-545112cee981 -->

- [[control-theory/index|Control theory map]]
- [[robotics/index|Robotics]]: where most of this gets applied.

## About this lesson
<!-- bite: 664d120f-22ec-47c2-98f2-a18225a9ad35 -->

**Level:** Advanced. **Covers:** MPC, reinforcement learning against classical control, learning-based control, control barrier functions, networked and data-driven control, and the subject's main takeaways.

**Where it sits:** lesson 58 of 58, the last lesson of the subject.

**Source:** `[reference]`, assembled from standard control texts.
