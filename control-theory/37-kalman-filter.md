---
id: a17cd60c-b67e-455e-adc3-deb25db5d6fa
---

# The Kalman Filter

The Kalman filter is an observer that chooses its correction gain optimally, by weighing how much it trusts its model against how much it trusts its sensors.

## Before you start
<!-- bite: e0476544-7f4e-490c-8ee5-edcfcc100a2d -->

You should have read [[control-theory/36-observers|36 — Observers]], and know what a variance is ([[machine-learning/00-foundations/03-mathematics/03-probability-and-statistics/index|probability and statistics]]).

After this lesson you will be able to:

1. carry out one predict and update step of a Kalman filter by hand;
2. explain the Kalman gain as a trust ratio, and what $Q$ and $R$ each do;
3. tune a filter from its symptoms, and check it with the innovation;
4. choose between the EKF, the UKF and a particle filter, and design a simple sensor fusion with a bias state.

## What the Kalman filter is
<!-- bite: 1942dbeb-e1e3-43b4-826e-77d9ac098e20 -->

Lesson 36's observer chose $L$ by placing poles, by feel. But real sensors are noisy and real models are imperfect, and the right $L$ depends on *how* noisy and *how* imperfect. The Kalman filter puts both into the model:

$$\mathbf{x}_{k+1} = A\mathbf{x}_k + B\mathbf{u}_k + \mathbf{w}_k, \qquad \mathbf{y}_k = C\mathbf{x}_k + \mathbf{v}_k$$

1. **Process noise $\mathbf{w}$**, with covariance $Q$: "my model isn't perfect".
2. **Measurement noise $\mathbf{v}$**, with covariance $R$: "my sensors aren't perfect".

Both are assumed zero on average, unrelated from one step to the next, and Gaussian. Under those assumptions, **the Kalman filter is the best possible estimator**: no other gives a smaller error variance. That's a theorem, not a tuning claim. It guided Apollo to the moon, and versions of it run in every phone and drone.

## The kid version
<!-- bite: 07272bf9-e631-470b-a78b-b1de29527cc4 -->

Two friends guess a jar's sweet count. One is careful and usually close; the other guesses wildly. You wouldn't just average them; you'd lean towards the careful one. The Kalman filter does exactly this at every step, between two "friends": its model's prediction and the sensor's reading, leaning towards whichever has been more reliable.

**Where the analogy stops working.** The friends' reliability is fixed. The filter's trust in its *own* prediction changes every step: it grows less sure as it predicts without data, and more sure each time a measurement arrives.

## One update by hand
<!-- bite: fb0dafbf-efa2-487f-9fab-90a71baf2c3c -->

Take the car's speed. The filter's estimate is 20 m/s, and it's unsure by a variance of 4 (a standard deviation of 2 m/s). The GPS reads 22 m/s, with variance 1. Predict before reading on: should the new estimate be nearer 20 or 22?

1. **Gain**: $K = \dfrac{4}{4 + 1} = 0.8$.
2. **New estimate**: $20 + 0.8(22 - 20) = 21.6$ m/s.
3. **New variance**: $(1 - 0.8) \times 4 = 0.8$.

Nearer 22, because the GPS is four times more trustworthy than the current estimate. And the new variance, 0.8, is smaller than *either* source's: combining two noisy readings gives you something better than both.

## The discrete algorithm
<!-- bite: 77811324-982e-439b-adef-1aa9f1e709cc -->

The form you'd implement, two steps per sample. **Predict**, by running the model forward:

$$\hat{\mathbf{x}}^-_k = A\hat{\mathbf{x}}_{k-1} + B\mathbf{u}_{k-1}, \qquad P^-_k = AP_{k-1}A^T + Q$$

**Update**, by folding in the measurement:

$$K_k = P^-_kC^T\left(CP^-_kC^T + R\right)^{-1}$$

$$\hat{\mathbf{x}}_k = \hat{\mathbf{x}}^-_k + K_k\left(\mathbf{y}_k - C\hat{\mathbf{x}}^-_k\right), \qquad P_k = (I - K_kC)P^-_k$$

$P$ is the **error covariance**, the filter's own statement of how unsure it is. **Predicting increases it** (the model drifts); **measuring decreases it**. With one state and $C = 1$, the gain is exactly the hand calculation above: $P^-/(P^- + R)$.

## The gain is a trust ratio
<!-- bite: a3489820-aa69-46be-b774-bea9793be385 -->

In words, the gain is

$$K \approx \frac{\text{uncertainty in my estimate}}{\text{uncertainty in my estimate} + \text{uncertainty in the measurement}}$$

1. **$R$ large** (noisy sensor): small $K$, so **trust the model** and smooth heavily.
2. **$Q$ large** (poor model): large $K$, so **trust the measurement** and respond fast.

That's the whole intuition: a weighted average of two noisy sources, weighted by reliability. It's the same as inverse-variance weighting in statistics, or a Bayesian posterior combining a prior with a likelihood, which is exactly what it is.

## The filter on the car
<!-- bite: 6967c1ae-7964-493b-b447-a7acb97d934d -->

Here the car speeds up steadily, the GPS speed is noisy (standard deviation 1 m/s), and the filter knows the engine force. Watch the estimate stay close to the truth while the readings scatter: its typical error after the first 5 seconds is 0.12 m/s, against 1 m/s for the raw readings.

![A simulated car accelerating from 10 to about 14.6 metres per second over 30 seconds. The GPS speed readings scatter by about 1 metre per second either side of the true speed, and up to 2; after the first 5 seconds the Kalman estimate stays within 0.22 metres per second of the truth.](images/ct-kalman-car.svg)

## Tuning it
<!-- bite: f5075243-3ea9-4795-92b8-68c4d2d67ecf -->

$Q$ and $R$ are the knobs, and in practice they're tuned rather than derived.

1. **$R$ you can measure.** Hold the sensor still and compute the variance of its readings: ten minutes' work.
2. **$Q$ is a fudge factor.** It soaks up all your unmodelled dynamics. Larger $Q$ means "trust the model less": more responsive, noisier.
3. **Only the ratio $Q/R$ matters** for the settled gain, which halves the problem.

The symptoms: an estimate that **lags the truth and is too smooth** needs more $Q$ (or less $R$); one that's **noisy and jumpy** needs less $Q$ (or more $R$).

## Checking it with the innovation
<!-- bite: babc21e9-9eb4-4d8a-9547-983010e65424 -->

For a correctly tuned filter, the innovation sequence $\mathbf{y}_k - C\hat{\mathbf{x}}^-_k$ should be **zero on average, uncorrelated from step to step**, with covariance $CP^-C^T + R$. If it's biased, correlated or the wrong size, your model or tuning is wrong. It's a free self-check, and most implementations never look at it.

For a system that doesn't change over time, $P$ and $K$ settle to constants. You can compute the settled gain offline (by solving a Riccati equation, lesson 40) and run a fixed-gain filter: much cheaper, and standard on small processors. The changing gain only matters at start-up.

## Nonlinear versions
<!-- bite: a839d395-6c8f-4eb6-8c72-b198c416e1a7 -->

Real systems aren't linear. The standard extensions:

1. **Extended Kalman filter (EKF)**: linearise about the current estimate at every step, using Jacobians. By far the most used: GPS and inertial units, robot localisation, flight controllers. But it can **diverge** if the linearisation is poor or the starting estimate is far off, and it has no optimality guarantee.
2. **Unscented Kalman filter (UKF)**: push a few carefully chosen **sigma points** through the true nonlinear function and rebuild the mean and covariance from them. No Jacobians, more accurate, a bit more computing. **If your EKF diverges, try the UKF before more tuning.**
3. **Particle filter**: represent the belief with many weighted samples. Handles any nonlinearity and beliefs with several peaks ("I might be in one of four identical corridors"), at a high computing cost. → [[robotics/index|Robotics]]

## Sensor fusion
<!-- bite: 4c5ef4de-bbec-4c2d-8943-c4df2b6fe050 -->

The most common real use. A gyroscope, integrated, gives your angle accurately over milliseconds but **drifts** over minutes. A magnetometer or GPS gives an absolute reference that's **noisy but doesn't drift**. The Kalman filter combines them: fast information from the gyro, slow correction from the absolute sensor, with the hand-over chosen by the noise levels.

Standard pairs: inertial sensors with GPS (aircraft, cars, drones); gyro with accelerometer (tilt, since gravity gives an absolute "down"); wheel counting with lidar (robots).

Remember this one: **estimate a bias as an extra state.** A gyro's bias drifts slowly; add it to the state vector and the filter estimates and removes it continuously. Almost every real inertial filter does this, and it's the difference between an attitude that drifts and one that doesn't. The same trick estimates a motor's load torque, called a **disturbance observer**.

## Practical notes
<!-- bite: 3b7776b9-a74b-45ed-af31-9ce904fb6951 -->

1. **Start unsure.** A bad starting estimate with a small $P_0$ recovers slowly and can diverge an EKF. When unsure, set $P_0$ large, so early measurements count heavily.
2. **Keep $P$ healthy.** Rounding can make $P$ lose symmetry. Use the **Joseph form** update, or a square-root filter, on anything long-running or embedded.
3. **Reject outliers.** One bad reading (a GPS reflection, a corrupted packet) can wreck the estimate. If the innovation is more than about 3 standard deviations from expected, discard it. Most field failures are outliers, not tuning.
4. **Missing readings are easy.** If a sensor doesn't report, skip the update and keep predicting.
5. **Different rates are fine.** Predict at every 1 kHz gyro sample; update whenever the 10 Hz GPS arrives.

## Common pitfalls
<!-- bite: f2093849-3d00-4bad-897d-d9f0faa7af65 -->

1. **Setting $Q = 0$.** The filter then trusts its model completely, and stops listening to sensors.
2. **Tuning on setpoint behaviour only.** Check the innovation.
3. **Starting overconfident.** A small $P_0$ with a wrong estimate takes ages to recover.
4. **Using an EKF far from its linearisation.** Start close, or use a UKF.

## Check your understanding
<!-- bite: 570e1da9-85ca-4c44-8152-1c6ef7df1a67 -->

Try each one before you open the answer.

1. <!-- q: exact id="a1c9e520" answer="0.75" accept="3/4" -->
   A temperature estimate has variance 3. A thermometer reading has variance 1. What is the Kalman gain?

   <details><summary>Answer</summary>

   $K = 3/(3 + 1) = 0.75$.

   </details>

2. <!-- q: exact id="6e2b8d47" answer="51.5" tolerance="0.01" -->
   Same filter: the estimate is 50 °C (variance 3) and the thermometer reads 52 °C (variance 1). What is the new estimate?

   <details><summary>Answer</summary>

   $50 + 0.75 \times (52 - 50) = 51.5$ °C.

   </details>

3. <!-- q: exact id="f3d07a91" answer="0.75" accept="3/4" -->
   Same numbers: prior variance 3, gain 0.75. What is the variance after the update?

   <details><summary>Answer</summary>

   $(1 - 0.75) \times 3 = 0.75$, smaller than either the prior (3) or the sensor (1).

   </details>

4. <!-- q: mcq id="2b7f4e08" -->
   A filter's estimate is smooth but lags behind every real change. What should you change?

   - [x] Increase $Q$ (or decrease $R$)
   - [ ] Decrease $Q$ (or increase $R$)
   - [ ] Set $P_0$ to zero
   - [ ] Remove the predict step

   <details><summary>Answer</summary>

   Lag means the filter trusts its model too much. More $Q$ (or less $R$) raises the gain so it follows measurements faster.

   </details>

5. <!-- q: open id="d95c1a36" -->
   Why do almost all real gyro-based attitude filters include the gyro bias as an extra state?

   <details><summary>Answer</summary>

   A gyro's bias drifts slowly, and integrating a biased rate makes the angle drift without limit. With the bias as a state, the absolute sensor's corrections let the filter estimate the bias and subtract it continuously, so the angle stops drifting.

   </details>

## Before moving on
<!-- bite: 5c1a44ea-b602-4160-8634-6871356c9b7e -->

You can run a Kalman update by hand, tune $Q$ and $R$, check the innovation and pick a nonlinear variant. That finishes estimation. **Next:** [[control-theory/38-optimal-control-1|38 — Optimal Control 1: The Performance Index and the Discrete Recipe]], which chooses the *controller* by optimisation, the mirror image of what the Kalman filter does for the estimate.

## Related
<!-- bite: 096187e3-b657-4b8c-bb60-b501ca7ff811 -->

- [[control-theory/projects|Projects]]: a Kalman filter on real phone data.
- [[robotics/11-state-estimation-and-filtering|Robotics: State Estimation and Filtering]]
- [[control-theory/index|Control theory map]]

## About this lesson
<!-- bite: d839c079-e428-40f4-9a85-604bb3ab467b -->

**Level:** Advanced. **Covers:** the Kalman filter model, a hand update, the predict and update steps, the gain as a trust ratio, tuning $Q$ and $R$, the innovation check, EKF, UKF and particle filters, sensor fusion with a bias state, and practical notes.

**Where it sits:** lesson 37 of 58, part 2 of 2 on estimation.

**Source:** `[reference]`, assembled from standard control texts. The simulated filter comes from `scripts/diagrams/control_theory.py`, using a fixed random seed so the picture is reproducible.
