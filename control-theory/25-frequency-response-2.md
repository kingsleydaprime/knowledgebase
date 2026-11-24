---
id: 14950c35-cfd5-48d0-aa57-944b7ae6f92d
---

# Frequency Response 2: Loop Shaping, Bandwidth and Margins

Loop shaping designs a controller by bending the loop's Bode plot, and the gain and phase margins read off that plot say how safe the loop is.

## Before you start
<!-- bite: c58cbefb-f9fc-4e3f-b8e6-3eeeffa60ed9 -->

You should have read [[control-theory/24-frequency-response-1|24 — Frequency Response 1: Bode Plots]], and be able to sketch a Bode plot from its building blocks.

After this lesson you will be able to:

1. say what the sensitivity $S$ and complementary sensitivity $T$ are, and why $S + T = 1$ is a hard limit;
2. describe a good loop shape and find the crossover frequency;
3. read gain margin and phase margin off a Bode plot, and convert phase margin to a damping ratio;
4. work out how much phase margin a delay costs, and list the limits on bandwidth.

## What this lesson covers
<!-- bite: f7152c4e-70de-445d-a8ee-88276d1f74ae -->

Lesson 24 drew Bode plots. Now we use them. The big idea: you don't design the closed loop directly. You shape the **open-loop** gain $L(j\omega)$, because it's what you can see and what the controller directly changes. Then you read off two numbers that say how far the loop is from going unstable, and lesson 19's "stability needs a margin" finally gets measured.

## The kid version
<!-- bite: ee9ffd60-e5f5-4de6-8454-08e62f7abdd4 -->

Think of the loop as a guard who listens for trouble and shoves back. You want the guard very alert to slow, real trouble (a hill, a drift) and deaf to fast chatter (sensor noise, wobbles the model doesn't know about). Loop shaping is tuning the guard's hearing: loud at low pitches, quiet at high ones.

**Where the analogy stops working.** A guard can, in principle, be alert to everything. A loop can't: there's a law saying that wherever it rejects disturbances, it passes noise, and the trade has to happen somewhere.

## Sensitivity and its partner
<!-- bite: 8c51230a-314c-4245-a88d-84d8b4a9abdb -->

Two closed-loop transfer functions matter, both built from $L$ (lesson 08):

$$T = \frac{L}{1+L} \qquad\qquad S = \frac{1}{1+L} \qquad\qquad S + T = 1$$

1. **Complementary sensitivity $T$**: how the reference reaches the output. You want it near 1 where you want tracking.
2. **Sensitivity $S$**: how a disturbance reaches the output. You want it near 0 where disturbances live.

Where $|L| \gg 1$: $T \approx 1$ and $S \approx 0$, so good tracking and good disturbance rejection. Where $|L| \ll 1$: $T \approx 0$ and $S \approx 1$, so no tracking, but sensor noise is ignored.

And $S + T = 1$ is the trap you can't escape: **you cannot make both small at the same frequency.** Rejecting disturbances at a frequency means following sensor noise at that frequency too.

## The shape to aim for
<!-- bite: 46fb3066-4dd0-422d-8fbd-d77005ca55ab -->

So the rule is: **high gain at low frequency, low gain at high frequency.** High where references and disturbances live, low where noise and unmodelled dynamics live.

The **crossover frequency** $\omega_c$, where $|L| = 1$ (0 dB), is the single most important number in a design:

1. **It sets the speed.** The closed-loop bandwidth is roughly $\omega_c$, and rise time is about $1.8/\omega_c$.
2. **The slope through crossover should be about −20 dB per decade.** Steeper means more phase lag at crossover, so less margin.
3. **Phase margin is measured there**, and it decides the damping.

## Bandwidth
<!-- bite: fd7d4d47-2ee8-46c8-b305-dc5810130cb7 -->

The **bandwidth** $\omega_b$ is where the closed-loop gain has dropped by 3 dB. The loop follows references slower than that and ignores faster ones. Higher bandwidth means a faster response:

$$t_r \approx \frac{1.8}{\omega_b}, \qquad \omega_b \approx \omega_c$$

And higher bandwidth costs you:

1. **More noise gets through**: you're following frequencies where the signal is mostly noise.
2. **More actuator effort**, so the actuator saturates sooner.
3. **Less robustness**, because high frequencies are exactly where your model is worst.

## The hard limits on bandwidth
<!-- bite: 6961aa41-c11d-4021-84d9-53e6bdd5a837 -->

Some limits can't be tuned away:

| Limit | Rough cap on $\omega_c$ |
| --- | --- |
| Right-half-plane zero at $z$ | $\omega_c < z/2$ |
| Time delay $T$ | $\omega_c < 1/T$ |
| Unstable pole at $p$ | $\omega_c > 2p$, a *lower* bound |
| Actuator | can't demand what it can't deliver |
| Sensor noise | can't act on what you can't measure |

Note the third row: an unstable plant forces the loop to be fast, while a right-half-plane zero or a delay forces it to be slow. **A plant with an unstable pole and a right-half-plane zero close together may be impossible to control at all.** That's a law, not a design failure, and worth checking before a month of tuning.

## Gain and phase margin
<!-- bite: 036c1640-1275-4714-b463-6a024816c516 -->

Two numbers say how far the loop is from instability. The danger point is a loop gain of exactly $-1$: size 1 and phase −180°, where a signal comes back around the loop the same size and flipped, so it feeds itself.

1. **Gain margin (GM)**: how many times you can multiply the loop gain before instability. Read it where the phase is −180°: it's how far below 0 dB the magnitude is there.
2. **Phase margin (PM)**: how much extra phase lag the loop can take before instability. Read it at crossover, where $|L| = 1$: it's how far above −180° the phase is there.

Targets: **PM of at least 45°, GM of at least 6 dB** (a factor of 2). Below about 30° of phase margin a loop is oscillatory and fragile.

## Margins on our loop
<!-- bite: 69f4a2df-f8a6-43f6-a3fa-cd02180c62dc -->

Back to $L = K/(s(s+1)(s+2))$ with $K = 1$, whose Bode plot you saw in lesson 24.

![The Bode plot of 1 over s times s plus 1 times s plus 2 with its margins marked: at crossover, 0.446 radians per second, the phase is minus 126.6 degrees, so the phase margin is 53.4 degrees; at 1.414 radians per second, where the phase is minus 180 degrees, the magnitude is minus 15.6 decibels, which is the gain margin.](images/ct-margins.svg)

1. **Gain margin.** The phase is −180° at 1.414 rad/s, where $|L| = 1/6$, or −15.6 dB. So GM = 6, matching lesson 19: the loop goes unstable at $K = 6$.
2. **Phase margin.** $|L| = 1$ at $\omega_c = 0.446$ rad/s, where the phase is $-90° - \tan^{-1}0.446 - \tan^{-1}0.223 = -126.6°$. So PM = 53.4°.

## From phase margin to damping
<!-- bite: 02bcf2e0-dd19-49c3-aa62-485b7597632e -->

Here's the rule of thumb that bridges the frequency plot and the step response:

$$\zeta \approx \frac{PM}{100}$$

with PM in degrees. So our 53° of phase margin means $\zeta \approx 0.53$: about 14% overshoot (lesson 13's table). And the classic 70° gives $\zeta \approx 0.7$. This is why an engineer can tune on a Bode plot while thinking about overshoot.

Now add a delay of 0.5 s to the loop, from a slow sensor. It doesn't change $|L|$, so crossover stays at 0.446 rad/s, but it adds $-\omega T = -0.446 \times 0.5 = -0.223$ rad, which is −12.8°. Phase margin drops to 40.6°, and the overshoot rises to about 25%. That's delay "taking away the thing keeping you stable", in numbers.

## Why work here at all
<!-- bite: 23fe4bad-54c1-49ed-890e-d749634faa75 -->

Root locus exists, so why the frequency domain? Five reasons:

1. **You can measure it.** A frequency sweep gives the plot with no model. You can't measure a root locus.
2. **Delays are exact.** $e^{-j\omega T}$ is just a phase shift. Root locus needs an approximation.
3. **Uncertainty is natural here.** "My model is good up to 100 rad/s and I don't trust it above that" is a frequency statement, and robust control is built on it.
4. **Margins mean something.** "45° of phase margin" is a defensible robustness claim. "Poles at $-2 \pm 3j$" says nothing about how much the plant can change.
5. **It composes.** In series, Bode plots add, so you can see at a glance what a compensator does.

## Common pitfalls
<!-- bite: e4cb19bf-a4d3-4aaa-ba70-0931c1ada76f -->

1. **Reading phase margin at the wrong frequency.** It's at crossover ($|L| = 1$), not where the phase is −180°.
2. **Trusting PM alone.** A loop can have good PM and GM and still be fragile, as lesson 27 shows.
3. **Pushing bandwidth past the hard limits.** No tuning beats a delay or a right-half-plane zero.
4. **Forgetting delay costs more at higher crossover.** The lag is $\omega_c T$, so a faster loop loses more margin to the same delay.

## Check your understanding
<!-- bite: 5b7b8cdd-b58c-4135-ba71-ddd1a1360a84 -->

Try each one before you open the answer.

1. <!-- q: mcq id="8d3f0b16" -->
   At a frequency where $|L| \gg 1$, what is true?

   - [x] $S \approx 0$ and $T \approx 1$: good tracking and disturbance rejection
   - [ ] $S \approx 1$ and $T \approx 0$: noise is rejected
   - [ ] $S$ and $T$ are both near 0
   - [ ] $S$ and $T$ are both near 1

   <details><summary>Answer</summary>

   With large $L$, $T = L/(1+L) \approx 1$ and $S = 1/(1+L) \approx 0$. They always add to 1.

   </details>

2. <!-- q: exact id="2a6e9c47" answer="40" accept="40°" -->
   At crossover a loop's phase is −140°. What is its phase margin, in degrees?

   <details><summary>Answer</summary>

   $180 - 140 = 40°$.

   </details>

3. <!-- q: exact id="7b0d5e31" answer="12" tolerance="0.1" -->
   Where a loop's phase is −180°, its magnitude is 0.25. What is the gain margin in dB?

   <details><summary>Answer</summary>

   GM = 1/0.25 = 4, which is $20\log_{10}4 = 12.0$ dB.

   </details>

4. <!-- q: exact id="e4c18a92" answer="28.65" sigfigs="2" -->
   A loop crosses over at $\omega_c = 2$ rad/s. A delay of 0.25 s is added. How many degrees of phase margin are lost?

   <details><summary>Answer</summary>

   $\omega_c T = 0.5$ rad $= 0.5 \times 180/\pi = 28.6°$.

   </details>

5. <!-- q: open id="f15a3c08" -->
   Why can't a controller reject a disturbance and ignore sensor noise at the same frequency?

   <details><summary>Answer</summary>

   Because $S + T = 1$ at every frequency. Rejecting disturbances needs $S$ small, which forces $T$ near 1, and $T$ is also how sensor noise reaches the output. So at any one frequency you get one or the other.

   </details>

## Before moving on
<!-- bite: 29ffea94-d9fc-4120-a718-9c0a38d28c5d -->

You can shape a loop, read both margins, turn PM into a damping ratio, and cost a delay. **Next:** [[control-theory/26-frequency-response-3|26 — Frequency Response 3: Reading Bode Plots and Design by Gain Adjustment]], which reads Bode plots backwards and sets the margins by choosing the gain.

## Related
<!-- bite: b8abe4ae-9196-4c43-a5a4-8f83c3709c11 -->

- [[control-theory/14-time-response-2|14 — Time Response 2: Dominant Poles, Delay and Step Tests]]: delay in the time domain.
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: 0cdd06a9-5592-4b69-835b-ddd188a270b7 -->

**Level:** Intermediate. **Covers:** sensitivity and complementary sensitivity, loop shaping and crossover, bandwidth and its hard limits, gain and phase margin, the phase-margin rule for damping, and what delay costs.

**Where it sits:** lesson 25 of 58, part 2 of 3 on frequency response.

**Source:** `[reference]`, assembled from standard control texts. Margins computed by `scripts/diagrams/control_theory.py`.
