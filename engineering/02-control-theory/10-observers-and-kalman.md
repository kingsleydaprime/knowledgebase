# Observers and Kalman Filters

**[Advanced]** — Estimating the state you can't measure, why the separation principle makes this tractable, and the filter that took Apollo to the moon.

## The problem

State feedback needs $\mathbf{x}$. You have $\mathbf{y} = C\mathbf{x}$ — fewer measurements than states.

**So build a model that runs alongside the real system and corrects itself using the measurements.**

## The Luenberger observer

The naive version: simulate the plant.

$$\dot{\hat{\mathbf{x}}} = A\hat{\mathbf{x}} + B\mathbf{u}$$

**This doesn't work.** If the initial estimate is wrong, the error never corrects — and if $A$ is unstable, the estimate diverges from reality exponentially. It's open-loop estimation, with all the failings of open-loop control.

**The fix is feedback, applied to the estimator:**

$$\dot{\hat{\mathbf{x}}} = A\hat{\mathbf{x}} + B\mathbf{u} + L\underbrace{(\mathbf{y} - C\hat{\mathbf{x}})}_{\text{innovation}}$$

The **innovation** $\mathbf{y} - C\hat{\mathbf{x}}$ is the difference between what you measured and what your estimate predicted you'd measure. **Nonzero innovation means the estimate is wrong**, and $L$ decides how hard to correct.

```
        u ──┬──────────────→[ PLANT ]────→ y
            │                                │
            └──→[ MODEL ]──→ŷ ──→(−)←───────┤
                    ▲                │       │
                    └──[ L ]←────────┘ innovation
```

## Error dynamics

Define $\mathbf{e} = \mathbf{x} - \hat{\mathbf{x}}$. Subtract the observer equation from the plant equation, and the $B\mathbf{u}$ terms cancel:

$$\dot{\mathbf{e}} = (A - LC)\mathbf{e}$$

**The estimation error has its own dynamics, governed by $A - LC$, and it's independent of the input entirely.**

$$\boxed{\text{Choose } L \text{ so } A - LC \text{ is stable} \implies \hat{\mathbf{x}} \to \mathbf{x}}$$

And by duality with [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|note 09]]: **if $(A,C)$ is observable, you can place the eigenvalues of $A - LC$ anywhere.** Same algorithm, applied to $(A^T, C^T)$.

**How fast?** Rule of thumb: **observer poles 2–5× faster than the controller poles.** The estimate must converge before the controller needs it. Faster than that and you amplify measurement noise — which is precisely the trade-off the Kalman filter formalises.

## The separation principle

**The result that makes this practical.**

Design the controller assuming perfect state knowledge. Design the observer ignoring the controller. Put them together. The closed-loop eigenvalues are:

$$\text{eig}(A - BK) \ \cup \ \text{eig}(A - LC)$$

> **The controller poles and observer poles do not interact.** You can design them separately and the combination behaves exactly as designed.

This is genuinely surprising — feedback loops normally interact strongly — and it's what makes the whole state-space approach usable. Without it you'd have to design a $2n$-dimensional system all at once.

**Two caveats that matter in practice:**

**It holds exactly only for the linear model.** With nonlinearity, model error, or saturation, controller and observer *do* interact, and an aggressive observer with a fast controller can misbehave together in ways neither does alone.

**Separation is about pole locations, not robustness.** An observer-based controller can have much worse stability margins than the state-feedback design it was built from — the famous result is that **LQG has no guaranteed margins at all**, unlike LQR. → [[engineering/02-control-theory/11-optimal-control-and-lqr|LQR]]

## The Kalman filter

The observer above is fine when you choose $L$ by intuition. The Kalman filter chooses it **optimally**, given a statistical description of the noise.

$$\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u} + \mathbf{w}, \qquad \mathbf{y} = C\mathbf{x} + \mathbf{v}$$

- $\mathbf{w}$ — **process noise**, covariance $Q$. "My model isn't perfect"
- $\mathbf{v}$ — **measurement noise**, covariance $R$. "My sensors aren't perfect"

Both assumed zero-mean, white, and Gaussian.

> **The Kalman filter is the minimum-variance estimator for a linear system with Gaussian noise.** No estimator does better. That's a theorem, not a claim about tuning.

### The discrete algorithm

The form you'd actually implement. Two steps per sample:

**Predict** — run the model forward:

$$\hat{\mathbf{x}}^-_k = A_d\hat{\mathbf{x}}_{k-1} + B_d\mathbf{u}_{k-1}$$
$$P^-_k = A_d P_{k-1} A_d^T + Q$$

**Update** — fold in the measurement:

$$K_k = P^-_k C^T\left(C P^-_k C^T + R\right)^{-1}$$
$$\hat{\mathbf{x}}_k = \hat{\mathbf{x}}^-_k + K_k\left(\mathbf{y}_k - C\hat{\mathbf{x}}^-_k\right)$$
$$P_k = (I - K_k C)P^-_k$$

$P$ is the **estimate error covariance** — the filter's own statement of how uncertain it is. **Prediction increases it** (the model drifts); **measurement decreases it** (data informs).

**The Kalman gain is the whole story:**

$$K \approx \frac{\text{uncertainty in my estimate}}{\text{uncertainty in my estimate} + \text{uncertainty in the measurement}}$$

- **$R$ large** (noisy sensor) → small $K$ → **trust the model**, smooth heavily
- **$Q$ large** (poor model) → large $K$ → **trust the measurement**, respond fast

**That's the entire intuition**, and it's a weighted average of two noisy sources of information, weighted by their reliability. The same logic as inverse-variance weighting in statistics, or a Bayesian posterior combining prior and likelihood — which is exactly what it is. → [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability and Statistics]]

### Tuning it

**$Q$ and $R$ are the knobs**, and in practice they're tuned rather than derived.

**$R$ you can usually measure.** Hold the sensor still and compute the variance of its output. That's a real number you can obtain in ten minutes.

**$Q$ is a fudge factor.** It nominally represents process noise, but in practice it absorbs all your unmodelled dynamics. Larger $Q$ means "I trust my model less", which makes the filter more responsive and noisier.

**Only the ratio $Q/R$ matters** for the steady-state gain — which halves the tuning problem.

**Symptoms:**
- Estimate lags the truth, too smooth → **increase $Q$** (or decrease $R$)
- Estimate is noisy and jumpy → **decrease $Q$** (or increase $R$)

**Check the innovation.** For a correctly tuned filter, the innovation sequence should be **zero-mean white noise** with covariance $CP^-C^T + R$. If it's correlated, or biased, or its magnitude doesn't match, your model or your tuning is wrong. **This is the diagnostic worth building in** — it's a self-check the filter gives you free, and most implementations never look at it.

**Steady state.** For a time-invariant system, $P$ and $K$ converge. You can precompute the steady-state gain (solve the algebraic Riccati equation offline) and run a fixed-gain filter — much cheaper, and standard on embedded hardware. The transient benefit of the time-varying gain only matters at startup.

## Nonlinear variants

Real systems aren't linear, and the standard extensions:

**Extended Kalman Filter (EKF)** — linearise about the current estimate at every step, using Jacobians of $f$ and $h$.

**Overwhelmingly the most used**, and the one in most GPS/INS units, robot localisation stacks, and flight controllers. But: it requires Jacobians (analytical or numerical), it can **diverge** if the linearisation is poor or the initial estimate is far off, and it has **no optimality guarantee** at all. A diverged EKF is a common and frustrating failure — and the usual cause is an initial estimate outside the region where linearisation holds.

**Unscented Kalman Filter (UKF)** — propagate a deliberately chosen set of **sigma points** through the true nonlinear function and reconstruct the mean and covariance.

**No Jacobians needed**, accurate to higher order, and more robust to strong nonlinearity. Costs a bit more computation. **If your EKF is diverging, try the UKF before adding more tuning.**

**Particle filter** — represent the distribution with weighted samples. Handles arbitrary nonlinearity *and* non-Gaussian, multi-modal distributions. Expensive, and suffers from particle depletion in high dimensions, but it's the only option when the posterior is genuinely multi-modal — which is why it's used for robot kidnapping/global localisation, where "I might be in one of four identical corridors" is a real belief state. → [[robotics/README|Robotics]]

## Sensor fusion

The most common real use, and the one worth understanding concretely.

**An IMU integrates to give attitude, and drifts.** Accurate over milliseconds, useless over minutes. **A magnetometer or GPS gives an absolute reference that is noisy but doesn't drift.**

The Kalman filter combines them optimally: **high-frequency information from the gyro, low-frequency correction from the absolute sensor.** It's a complementary filter with the crossover chosen by the noise statistics rather than by hand.

Standard combinations:
- **IMU + GPS** — position and attitude for aircraft, cars, drones
- **Gyro + accelerometer** — attitude; the accelerometer gives absolute tilt from gravity, the gyro gives fast rotation
- **Wheel odometry + lidar** — robot localisation
- **Estimating a disturbance as an extra state** — a "disturbance observer", used to cancel load torque in motor drives

> **Estimating a bias as a state** is the trick worth remembering. Gyro bias drifts slowly; add it to the state vector and the filter estimates and removes it continuously. Almost every real IMU filter does this, and it's the difference between an attitude estimate that drifts and one that doesn't.

## Practical notes

**Initialise well.** A bad initial estimate with an overconfident $P_0$ can take a long time to recover, and can diverge an EKF entirely. When unsure, **set $P_0$ large** — that tells the filter to trust early measurements heavily.

**Watch numerical conditioning.** The covariance update can lose symmetry and positive-definiteness through rounding. Use the **Joseph form** update, or a square-root/UD-factorised filter, on anything long-running or embedded.

**Reject outliers.** A single bad measurement (GPS multipath, a dropped packet) can corrupt the estimate badly. Gate on the normalised innovation — if it's more than ~3σ from expected, discard the measurement. **Most field failures of a Kalman filter are outliers, not tuning.**

**Handle missing measurements properly.** If a sensor doesn't report this cycle, just skip the update step and keep predicting. The filter handles it naturally, and this is a real advantage over a fixed complementary filter.

**Different rates are fine.** IMU at 1 kHz, GPS at 10 Hz — predict every IMU sample, update whenever GPS arrives. One of the filter's most useful practical properties.

---

## Related
- [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Controllability and Observability]] — the condition for any of this
- [[engineering/02-control-theory/11-optimal-control-and-lqr|Optimal Control and LQR]] — the dual problem, and LQG
- [[engineering/02-control-theory/12-digital-control|Digital Control]] — implementing the discrete filter
- [[robotics/README|Robotics]] — where sensor fusion lives
- [[engineering/02-control-theory/README|Control theory map]]
