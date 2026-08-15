# State Estimation and Filtering

**[Advanced]** — Combining unreliable sensors into one usable belief, and why a robot never actually knows where it is.

> **The theory is in [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]]** — the algorithm, the separation principle, tuning $Q$ and $R$, the EKF/UKF/particle variants. **This note is the robotics application**: what you fuse, why odometry drifts, and the practical failures.

## The premise

**A robot never observes its own state. It infers one.**

Every measurement is noisy, delayed, partial, or all three. No sensor reports "you are at $(3.24, 1.07)$ facing 41°". So the robot maintains a **belief** — a best estimate plus an admission of how uncertain it is — and updates it as evidence arrives.

$$\text{belief} = p(\mathbf{x}_t \mid \mathbf{z}_{1:t}, \mathbf{u}_{1:t})$$

The state given every measurement and every command so far. **Filtering is the recursive computation of that distribution**, and the reason it's tractable is the Markov assumption: the current state summarises everything relevant about the past. → [[engineering/02-control-theory/08-state-space|What "state" means]]

**Two steps, forever:**

**Predict** — apply the motion model. *Uncertainty grows*, because the model is wrong.

**Update** — fold in a measurement. *Uncertainty shrinks*, because data informs.

```
 uncertainty
    │    ╱╲    ╱╲    ╱╲       predict: grows
    │   ╱  ╲  ╱  ╲  ╱  ╲      update:  drops
    │  ╱    ╲╱    ╲╱    ╲
    └────────────────────→ t
       ↑     ↑     ↑
    measurements arrive
```

## Odometry and why it drifts

**Odometry** integrates motion to estimate pose — wheel encoders for a ground robot, IMU for a drone, visual features for a camera.

For differential drive:

$$\Delta x = \Delta s\cos\theta, \quad \Delta y = \Delta s\sin\theta, \quad \Delta\theta = \frac{\Delta s_R - \Delta s_L}{L}$$

**It is smooth, high-rate, and locally excellent.** Over a second, wheel odometry is very accurate.

**And it drifts without bound**, because you're integrating error:

- **Wheel slip** — the wheel turned, the robot didn't move. Odometry is *certain* it moved
- **Wrong wheel radius or track width** — a systematic error that accumulates every metre. A 1% radius error is a metre off after 100
- **Uneven floor, carpet, dust**
- **Heading error is the killer.** A small angular error rotates *all subsequent translation*. **1° of heading error becomes 17 cm of position error after 10 metres**, and it never comes back

> **This is the fundamental limit: odometry is a relative measurement being used as an absolute one.** No amount of encoder resolution fixes it. **You need something absolute** — a landmark, a map match, GPS, a fiducial marker — or the estimate degrades forever.

**Which is exactly the complementary structure from [[robotics/02-sensors-and-perception|note 02]]:** odometry is precise short-term and drifts; absolute measurements are noisy and don't. Fusing them is the whole game.

## What robots actually fuse

**Wheel odometry + IMU** — the IMU's gyro gives much better heading than differencing wheel encoders, and it doesn't care about slip. **This one pairing removes most odometry error** on a ground robot, and it's cheap.

**IMU + GPS** — the standard outdoor combination. GPS at 1–10 Hz gives absolute position with no drift; the IMU at 100–1000 Hz fills the gaps and survives dropouts. → [[engineering/02-control-theory/10-observers-and-kalman|Sensor fusion]]

**Odometry + lidar scan matching** — indoor mobile robots. The scan match against a map is the absolute correction.

**Visual-inertial odometry (VIO)** — camera + IMU, and the pairing is unusually good: the camera fixes the IMU's drift, the IMU carries you through motion blur, featureless walls, and fast rotation. **This is what phone AR and most drones use**, and it's why it works handheld.

**Joint encoders + FK** for an arm — usually enough on its own, because a bolted-down arm has no drift. Add vision when the *object* position is uncertain rather than the robot's.

## Bias estimation

**The trick worth knowing**, and it generalises beyond IMUs.

A gyro's bias drifts with temperature. If you subtract a bias measured at startup, you'll be wrong ten minutes later.

**So make the bias part of the state:**

$$\mathbf{x} = [\text{pose},\ \text{velocity},\ \underbrace{\mathbf{b}_{gyro},\ \mathbf{b}_{accel}}_{\text{estimated continuously}}]$$

The filter tracks and removes it as conditions change. **Every serious IMU filter does this**, and it's the difference between an attitude estimate that holds for an hour and one that doesn't.

**The same idea covers** wheel radius, camera-to-IMU extrinsics, and clock offset between sensors. **If a parameter drifts and affects your measurements, consider estimating it** — it costs a state dimension and often removes an entire class of error.

**The constraint is observability.** You can only estimate what the measurements actually reveal. Accelerometer bias and gravity are indistinguishable when stationary — you need motion to separate them, which is why VIO systems require an initialisation manoeuvre. → [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Observability]]

## Choosing a filter

| | When |
|---|---|
| **Complementary filter** | attitude from IMU, one axis, embedded, no covariance needed. **5 lines** |
| **Kalman filter** | linear model, Gaussian noise. Rare in robotics — the models are nonlinear |
| **EKF** | **the default.** Nonlinear via Jacobians. Robot localisation, IMU+GPS, VIO |
| **UKF** | strong nonlinearity, or you don't want to derive Jacobians. Better attitude estimation |
| **Particle filter** | **multi-modal beliefs** — global localisation, the kidnapped robot problem |
| **Factor graph / smoothing** | offline or near-real-time, optimising over a window. What modern SLAM uses |

**Notes on the choices:**

**The EKF dominates**, and its main failure is divergence when linearisation is poor or the initial estimate is far off. **A diverged EKF is a common and frustrating field failure** — the covariance shrinks confidently while the estimate is wrong, and it never recovers.

**Particle filters are the answer when the belief is genuinely multi-modal.** "I'm in one of four identical corridors" is a real belief state that a Gaussian cannot represent, and forcing a Gaussian onto it gives you a mean in the middle of a wall. AMCL — the standard ROS localisation package — is a particle filter for exactly this reason. → [[robotics/12-localisation-and-slam|Localisation and SLAM]]

**Factor graphs are where the field has moved for SLAM.** Instead of one recursive estimate, keep a window of past states and optimise them jointly. **Re-linearising the past is what makes them more accurate than an EKF**, and GTSAM/g2o/Ceres make it practical.

## Timing

**The robotics-specific problem that catches people**, and it's not in the textbook filter.

**Measurements arrive late and out of order.** A camera frame timestamped $t$ arrives at $t + 80\,\text{ms}$, after IMU samples from $t+10$ through $t+80$ have already been processed.

Applying it as if it were current is wrong — you're correcting the present with evidence about the past.

**The fixes, in increasing order of effort:**

- **Timestamp at capture**, not at arrival. Non-negotiable, and it requires hardware support or a driver that does it properly
- **Buffer and reprocess** — keep recent states and inputs, roll back to the measurement's timestamp, apply it, re-propagate forward
- **Stochastic cloning** — keep an explicit past state in the filter for delayed measurements to attach to
- **Or accept the error** if the delay is small relative to your dynamics. Often fine, but decide deliberately rather than by accident

**Clock synchronisation between machines** is its own problem, and a real one on a multi-computer robot. Two nodes disagreeing by 50 ms produce a fusion result that's confidently wrong. → [[architecture/04-distributed-systems/03-time-and-ordering|Time and Ordering]]

## Practical notes

**Initialise honestly.** A confident wrong initial estimate is worse than an uncertain one — set $P_0$ large when you don't know, and the filter will trust early measurements appropriately.

**Gate outliers.** A single bad GPS fix (multipath), a mis-associated feature, a dropped packet. **Reject measurements whose normalised innovation exceeds ~3σ.** Most field failures of a filter are outliers, not tuning.

**Monitor the innovation.** For a correctly tuned filter it should be zero-mean white noise with the covariance the filter predicts. **If it's biased or too large, your model or your noise parameters are wrong** — and this is a self-check the filter gives you for free that almost nobody looks at.

**Watch for covariance collapse.** If $P$ shrinks too far the filter stops listening to measurements and diverges silently. Enforce a floor on the covariance, or add process noise.

**Tune $R$ from data, tune $Q$ by hand.** Measure sensor variance directly — it takes ten minutes. $Q$ is a fudge factor absorbing your unmodelled dynamics, and only the ratio $Q/R$ matters.

**Missing measurements are fine.** Skip the update, keep predicting. **This is a genuine advantage of a filter over a fixed complementary filter**, and it's why estimator-based designs suit robots where sensors drop out.

**Log the covariance, not just the estimate.** When something goes wrong, the uncertainty history tells you whether the filter knew it was lost.

---

## Related
- [[engineering/02-control-theory/10-observers-and-kalman|Observers and Kalman Filters]] — the theory this applies
- [[robotics/02-sensors-and-perception|Sensors and Perception]] — what's being fused
- [[robotics/12-localisation-and-slam|Localisation and SLAM]] — the largest application
- [[robotics/README|Robotics map]]
