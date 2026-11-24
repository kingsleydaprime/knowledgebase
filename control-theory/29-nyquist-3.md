---
id: 71c2bf7e-d9d5-42d1-807e-642be6436718
---

# Nyquist 3: Uncertainty and Fundamental Limits

Robustness is how far a real plant can differ from its model before the loop misbehaves, and some limits on it can't be beaten by any controller.

## Before you start
<!-- bite: 00b4ea0e-ca97-4585-af24-22b6a276cff2 -->

You should have read [[control-theory/27-nyquist-1|27 — Nyquist 1: The Nyquist Criterion]], and know what $S$, $T$ and $M_s$ are.

After this lesson you will be able to:

1. describe model uncertainty with a frequency weight, and state the robust stability test;
2. explain the waterbed effect and what an unstable pole does to it;
3. recognise a plant that no controller can handle well;
4. run the six practical robustness checks, including the delay margin.

## What robustness is
<!-- bite: c1c62b27-1b88-4844-85ad-b045107e6c2d -->

No model is exact. The car gets heavier with passengers, the drag changes with the wind, the motor warms up. **Robustness** is a loop's ability to keep working, stable and performing, across all the plants it might really be.

That only means something once you say *how* wrong the model might be. Lesson 27 measured the closest approach to −1. This lesson asks how big the model error can get before the curve is pushed onto −1, and what limits exist whatever you do.

## The kid version
<!-- bite: f49600d9-4a30-43fa-8f10-a422b73d559b -->

You've packed a suitcase so tightly you can only close it by pressing down on one corner. Press there and another corner pops up. You can choose *where* the bulge goes, but the stuff inside doesn't shrink. Control has the same kind of law: push the loop's error down at some frequencies, and it must bulge up somewhere else.

**Where the analogy stops working.** A suitcase's bulge is just untidy. A loop's bulge, if it lands where the model is wrong or where noise lives, can make the loop shake or go unstable.

## Describing how wrong the model is
<!-- bite: 36eaa013-47f8-48c3-9cbd-53234901014d -->

The standard way to describe model error is **multiplicative uncertainty**:

$$G_{real}(s) = G(s)\big(1 + \Delta(s)\big), \qquad |\Delta(j\omega)| < W(\omega)$$

$\Delta$ is the unknown error, and the **weight** $W(\omega)$ says how large it might be at each frequency, as a fraction. $W$ is usually small at low frequency and large at high frequency, because you know a plant's steady gain well and its fast dynamics badly.

The loop stays stable for every such plant when

$$|T(j\omega)| < \frac{1}{W(\omega)} \quad \text{at every } \omega$$

In words: **where your model is untrustworthy, the closed-loop gain must be small.** You'd reach the same rule by instinct, and it's the real reason to roll the loop gain off at high frequency: not just for noise, but because that's where the model is wrong.

## The waterbed effect
<!-- bite: 2503e10f-9ef5-41db-9a6b-3dcb8e5c6b9d -->

Now the limits no controller can beat. The first is **Bode's sensitivity integral**: for a loop whose plant is stable and has at least two more poles than zeros,

$$\int_0^\infty \ln|S(j\omega)|\,d\omega = 0$$

In words: **the area under the log-sensitivity curve is fixed at zero.** Where $|S| < 1$ the loop rejects disturbances and $\ln|S|$ is negative; that area must be paid back somewhere with $|S| > 1$, where the loop *amplifies* disturbances.

![The logarithm of the sensitivity of the loop 1 over s times s plus 1 times s plus 2 against frequency: it is negative at low frequency, where disturbances are rejected, crosses zero at 0.41 radians per second, and rises above zero to a peak of 0.45 at 0.73 radians per second before falling back towards zero. The negative and positive areas are equal.](images/ct-waterbed.svg)

You're not removing the difficulty; **you're moving it**. The name "waterbed effect" is exact.

## Unstable poles make it worse
<!-- bite: e719a30e-97a9-47aa-b59b-b6b4cc0d2a5e -->

If the plant has unstable poles $p_i$, the integral is no longer zero:

$$\int_0^\infty \ln|S(j\omega)|\,d\omega = \pi\sum \text{Re}(p_i)$$

The fixed area is now *positive*: an unstable plant forces the loop to amplify disturbances more than it rejects them, overall. **Unstable plants are fundamentally harder, and no cleverness in the controller changes that.**

## The impossible plant
<!-- bite: 0e0a9bbb-9805-486f-a658-6110738e4277 -->

Lesson 25 listed the bandwidth caps: $\omega_c \lesssim z/2$ for a right-half-plane zero at $z$, and $\omega_c \lesssim 1/T$ for a delay $T$. They're not tuning advice; exceed them and the loop is unstable whatever the controller.

Now put the caps together. A plant with an unstable pole at $p$ needs $\omega_c \gtrsim 2p$. If it also has a right-half-plane zero at $z$, it needs $\omega_c \lesssim z/2$. When $z < 4p$ or so, those can't both hold: **no controller stabilises it with reasonable margins.**

Remember this one: if you meet a plant like that, the answer isn't a better controller. It's to change the plant, move the sensor or add an actuator. That's why some aircraft shapes are never flown and some chemical processes are redesigned rather than better controlled. Spotting it early saves months.

## Robust control, by name
<!-- bite: 9a46f799-c7b3-4259-825c-e2a5e31a2ad3 -->

A whole field is built on taking these limits seriously. Named here so the words are familiar:

1. **H-infinity control** ($\mathcal{H}_\infty$): design the controller to minimise the *worst-case* gain from disturbance to error over all frequencies. **Mixed sensitivity** design shapes $S$, $T$ and the control effort at once, using weights you choose: one where you want disturbances rejected, one where you don't trust the model.
2. **μ-synthesis**: handles several separately uncertain parameters, and is less pessimistic than lumping them into one block.

A useful feature: the synthesis either returns a controller or says the specification is impossible, which tells you the *specification* is the problem, not your tuning. The cost is that these controllers have high order, so they're harder to implement and maintain. They're standard in aircraft and hard-disk drives, and rare in process plants, where a well-tuned PI with good margins is easier to look after.

## Practical robustness checks
<!-- bite: 81ed95c5-13e6-4e6d-83e5-c0b94d15ca5a -->

What to actually check, in order:

1. **$M_s < 2$**, the sensitivity peak. The single most informative number.
2. **PM ≥ 45° and GM ≥ 6 dB.** Necessary, not enough on their own.
3. **Delay margin**: $PM/\omega_c$, with PM in radians. How much extra delay before instability. Worth computing for anything networked or software-timed, since delay is what most often changes unexpectedly.
4. **Gain change**: does it survive the plant gain doubling or halving? Real plants drift with temperature, load and wear.
5. **Simulate the extremes** of every uncertain parameter, not just the nominal model.
6. **Check the actuator effort.** A robust design that saturates is not robust.

## The checks on our loop
<!-- bite: 5044f833-355a-428f-b78d-84af6a6a59a7 -->

Our loop $L = 1/(s(s+1)(s+2))$ has $M_s = 1.57$, PM = 53.4° and GM = 6. Its delay margin is $0.932 \text{ rad}/0.446 \text{ rad/s} = 2.09$ s: a sensor that suddenly lags by two seconds would make it oscillate. Doubling the gain to 2 keeps it stable (lesson 19's limit is 6).

Remember this one: **a controller tuned perfectly for the nominal plant and marginal everywhere else is a bad design.** Detune on purpose. The best real-world controller is usually noticeably slower than the fastest stable one, and that gap is the price of it still working next year.

## Common pitfalls
<!-- bite: 53245ec1-d1bd-459a-a5cc-d250eeb43842 -->

1. **Saying "robust" without saying to what.** Robustness is always relative to a stated uncertainty.
2. **Trying to tune past a fundamental limit.** A delay or right-half-plane zero caps the bandwidth for every controller.
3. **Pushing $|S|$ down everywhere.** The waterbed makes it rise somewhere else; choose where.
4. **Skipping the delay margin on software loops.** Timing is what changes most in practice.

## Check your understanding
<!-- bite: b8b75ba1-0803-419b-86bb-50738afe6481 -->

Try each one before you open the answer.

1. <!-- q: mcq id="5f0a2e48" -->
   A model is accurate to 5% below 10 rad/s but could be 200% wrong above 100 rad/s. Where must the closed-loop gain $|T|$ be small?

   - [ ] Below 10 rad/s
   - [x] Above 100 rad/s
   - [ ] Everywhere equally
   - [ ] Only at the crossover frequency

   <details><summary>Answer</summary>

   Above 100 rad/s. The test $|T| < 1/W$ demands a small closed-loop gain where the uncertainty weight is large.

   </details>

2. <!-- q: exact id="d8e2b6c1" answer="1.5" -->
   A loop has a phase margin of 0.6 rad at a crossover of 0.4 rad/s. What is its delay margin, in seconds?

   <details><summary>Answer</summary>

   $0.6/0.4 = 1.5$ s.

   </details>

3. <!-- q: mcq id="2c9f7d30" -->
   A plant has an unstable pole at $p = 2$ and a right-half-plane zero at $z = 3$. What should the engineer conclude?

   - [ ] A lead compensator will fix it
   - [ ] Increase the gain until it is stable
   - [x] No controller can handle it well; change the plant, sensor or actuator
   - [ ] Use a PI controller with a long integral time

   <details><summary>Answer</summary>

   The pole needs $\omega_c \gtrsim 4$ but the zero allows only $\omega_c \lesssim 1.5$. With $z < 4p$ no controller gives reasonable margins.

   </details>

4. <!-- q: gap id="9a1e5c72" answers="zero|0;positive" -->
   For a stable plant with at least two more poles than zeros, the integral of $\ln|S|$ over all frequencies is ___. With unstable poles it is ___.

   <details><summary>Answer</summary>

   Zero; positive ($\pi$ times the sum of the unstable poles' real parts).

   </details>

5. <!-- q: open id="b4d71e09" -->
   Explain the waterbed effect in your own words, and why it means a designer must choose *where* the loop performs badly.

   <details><summary>Answer</summary>

   The area under $\ln|S|$ is fixed, so making $|S|$ small (good disturbance rejection) over some frequencies forces it above 1 (disturbances amplified) over others. The designer can't remove the bad region, only move it, so they should put it where there are few disturbances and the model is trusted.

   </details>

## Before moving on
<!-- bite: 37cc972b-57d1-4f68-8f18-f05b36b762ae -->

You can describe uncertainty, explain the waterbed, spot an impossible plant and run the practical checks. That finishes classical control. **Next:** [[control-theory/30-state-space-1|30 — State Space 1: States and the State Equation]], the modern way of writing a model, which handles many inputs and outputs at once.

## Related
<!-- bite: a3c394d7-2c17-4d1b-9629-1bcd7b6d5beb -->

- [[control-theory/43-lqg-and-mpc|43 — LQG and MPC]]: an optimal design whose margins vanish.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 11b20519-2951-407d-8db8-473297fd91b1 -->

**Level:** Advanced. **Covers:** multiplicative uncertainty and the robust stability test, Bode's sensitivity integral, the impossible plant, H-infinity and μ-synthesis by name, and the practical robustness checks.

**Where it sits:** lesson 29 of 58, part 3 of 3 on Nyquist analysis, and the last lesson of classical control.

**Source:** `[reference]`, assembled from standard control texts. The waterbed plot and the margins come from `scripts/diagrams/control_theory.py`.
