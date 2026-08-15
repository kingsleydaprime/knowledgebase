# Localisation and SLAM

**[Advanced]** — Knowing where you are in a map, and building the map while you do.

## Three related problems

The distinction matters because they have very different difficulty:

| Problem | Given | Find |
|---|---|---|
| **Localisation** | a map | where am I? |
| **Mapping** | known poses | what does the world look like? |
| **SLAM** | neither | **both, simultaneously** |

**SLAM is hard because it's circular.** You need the map to know where you are; you need to know where you are to build the map. **Errors feed back into themselves**, and a small pose error corrupts the map, which corrupts the next pose estimate.

That it works at all is the field's genuine achievement, and the resolution is that **the geometry is over-constrained** — observing the same landmark from many poses gives more equations than unknowns, so the errors can be squeezed out globally even though each individual estimate is bad.

## Localisation with a known map

The easier problem, and often all you need — a warehouse robot maps once and localises forever.

**Position tracking** — you know roughly where you are, track it. Local, easy, and a Gaussian belief works fine.

**Global localisation** — you have *no idea* where you are. **The belief is multi-modal**: you could be in any of several places that look identical, and a Gaussian cannot represent that. This is why particle filters exist.

**The kidnapped robot problem** — you were localised, then got picked up and moved. **Harder than global localisation**, because the filter is *confident* and wrong, and a well-converged filter actively resists evidence that contradicts it. Detecting it requires monitoring whether measurements stop matching expectations.

### Monte Carlo Localisation

The standard solution, and what ROS's `amcl` implements.

**Represent the belief as a cloud of weighted particles**, each a hypothesis about the pose:

```
1. PREDICT   move every particle by the motion model + noise
2. WEIGHT    score each by how well the sensor reading matches
             what you'd see from there, given the map
3. RESAMPLE  draw a new set, proportional to weight
```

```
  scattered (lost)          converged (localised)
  ┌──────────────┐          ┌──────────────┐
  │ · ·  ·   ·   │          │              │
  │  ·  ·  ·  ·  │   ───→   │      ▓       │
  │ ·   ·  ·   · │          │              │
  └──────────────┘          └──────────────┘
```

**Why it's the right tool:** particles represent *any* distribution, including several distinct hypotheses. As evidence accumulates, wrong hypotheses get low weights and die out.

**What bites:**

- **Particle depletion.** Resampling repeatedly can eliminate the correct hypothesis by bad luck, especially with too few particles. **Once it's gone it never comes back** — resampling only ever removes diversity
- **Too few particles** in a large map means you may never have one near the truth
- **Adaptive particle counts** (KLD-sampling — the "A" in AMCL) use many when uncertain, few when converged. **This is what makes it practical**
- **Add random particles** to allow recovery from kidnapping
- **The motion model needs realistic noise.** Too little and particles collapse prematurely; too much and it never converges

## Map representations

**Occupancy grid** — the plane divided into cells, each holding $P(\text{occupied})$.

*Simple, handles uncertainty naturally, and directly usable by a planner.* **The standard for 2D indoor robots**, and stored as log-odds so updates are additions rather than multiplications.

Memory scales with **area × resolution²**, so it doesn't extend well to large 3D spaces.

**Octree / OctoMap** — hierarchical 3D occupancy, subdividing only where there's detail. **Dramatically more efficient than a 3D grid** and the standard for 3D occupancy.

**Feature/landmark map** — a list of distinctive points with positions. Compact, and it's what visual SLAM builds. Doesn't tell you where the *free space* is, which a planner needs.

**Point cloud** — raw accumulated returns. Detailed, large, and needs processing before a planner can use it.

**Topological map** — a graph of places and connections, no metric detail. Very compact, robust, and enough for "navigate to the kitchen". Often layered *on top* of a metric map.

**Semantic map** — objects and their meanings ("this is a door, that's a chair"). Where the field is heading, and what makes "bring me the mug from the kitchen" possible. → [[ai-ml/02-ml-engineer/06-computer-vision/README|Computer Vision]]

## SLAM approaches

### Filter-based

**EKF-SLAM** — one big state vector holding the robot pose *and* every landmark, with a full covariance matrix.

**Elegant** — it correctly captures that landmark estimates are correlated, which is the key structural insight of SLAM.

**And it doesn't scale.** The covariance is $O(n^2)$ in landmarks and the update is $O(n^2)$. Beyond a few hundred landmarks it's impractical. **Historically important, rarely used now.**

**FastSLAM** — a particle filter over robot *trajectories*, each particle carrying its own set of small independent EKFs for landmarks. Exploits the Rao–Blackwellisation insight that **given the trajectory, landmarks become independent.** Scales much better, and `gmapping` is the well-known implementation.

### Graph-based

**What the field uses now.**

Represent the problem as a graph: **nodes are poses (and landmarks), edges are measured constraints between them.** Then find the configuration of nodes that best satisfies all constraints:

$$\min_{\mathbf{x}}\sum_{ij}\|f(\mathbf{x}_i, \mathbf{x}_j) - \mathbf{z}_{ij}\|^2_{\Sigma_{ij}}$$

**A big sparse nonlinear least-squares problem**, solved with Gauss–Newton or Levenberg–Marquardt.

**Why it wins:**

- **The information matrix is sparse** — each pose only constrains its neighbours — and sparse solvers exploit that ruthlessly
- **It re-optimises the whole trajectory**, so a correction propagates backwards and fixes the past. A filter cannot do this; once it's committed to an estimate, it's committed
- **Re-linearisation** at each iteration avoids the EKF's accumulated linearisation error
- Mature libraries: **g2o, GTSAM, Ceres**

**The two-part structure** you'll see everywhere:

**Front end** — process sensor data into constraints. Feature extraction, scan matching, data association. *Where the domain-specific work is.*

**Back end** — optimise the graph. *Generic*, and reusable across sensors.

## Loop closure

**The single most important operation in SLAM.**

Drift accumulates without bound as you drive. Then you return somewhere you've been, **recognise it**, and add a constraint linking the current pose to that old one.

```
  without loop closure        with loop closure
   ┌────────╮                  ┌────────┐
   │        │                  │        │
   │        ╰─ drifted         │        │  corrected
   ╰──────╴  ✗ doesn't meet    ╰────────┘  ✓ closed
```

**That one constraint redistributes the accumulated error across the entire trajectory.** The map snaps into consistency, and the effect is dramatic — it's the moment a wobbly map becomes a usable one.

**How places are recognised:**

- **Bag of visual words** (DBoW2) — quantise image features into a vocabulary and compare. Fast, and the standard for visual SLAM
- **Scan context / descriptors** for lidar
- **Learned place recognition** (NetVLAD and descendants) — more robust to lighting and viewpoint change
- **Geometric verification always** — after a candidate match, check the geometry actually agrees

> **A false loop closure is catastrophic.** It tells the optimiser that two genuinely different places are the same, and the map folds in on itself irrecoverably. **Verify aggressively; a missed loop closure costs you accuracy, a false one destroys the map.** Robust cost functions (Huber, switchable constraints) limit the damage from a bad one.

**Perceptual aliasing** is the underlying danger — identical-looking corridors, repeated office layouts, featureless warehouses. It's why loop closure in a building full of identical doors is genuinely hard.

## The main systems

Worth recognising by name:

**2D lidar:** `gmapping` (FastSLAM, mature), `Cartographer` (Google, graph-based, 2D and 3D, excellent loop closure), `slam_toolbox` — **the current ROS 2 default**, graph-based, supports lifelong mapping and map serialisation.

**3D lidar:** LOAM and its descendants (LeGO-LOAM, LIO-SAM). LIO-SAM tightly couples an IMU and is the strong current baseline.

**Visual:** **ORB-SLAM3** — the reference feature-based system, handling monocular/stereo/RGB-D with IMU. `RTAB-Map` for RGB-D with appearance-based loop closure. **VINS-Fusion** for visual-inertial on drones.

**The practical pattern:** lidar for reliability and metric accuracy, vision for cheapness and rich loop closure, and **the two together beat either alone**.

## Practical notes

**Localisation is much easier than SLAM. Do it if you can.** Map once, carefully, offline, with good sensors. Then localise against that map forever. **Most production robots work this way** — a warehouse doesn't need to re-map every shift.

**Your map is a snapshot.** Furniture moves, pallets appear, doors close. **A static map plus a dynamic obstacle layer** is the standard architecture: localise against the static map, avoid obstacles using live sensor data.

**Dynamic objects corrupt maps.** People walking through while you map get baked in as walls. Filter moving objects out, or map when it's quiet.

**Glass and mirrors defeat lidar.** The beam passes through or reflects away, so the map has holes where windows are. A known, unsolved-in-general problem — most deployments add physical markers or no-go zones.

**Featureless environments defeat scan matching.** A long empty corridor gives no constraint along its length — you know how far you are from the walls and nothing about your position down the hall. **The uncertainty is anisotropic**, and a filter that reports a single scalar "confidence" hides this.

**Save and reuse maps.** Rebuilding on every boot is wasteful and gives you a different map each time, which makes waypoints meaningless.

**Evaluate honestly.** Absolute Trajectory Error (ATE) against ground truth for global consistency; Relative Pose Error (RPE) for local drift. **Ground truth needs motion capture or a survey** — "the map looks right" is not evaluation. → [[research/06-analyzing-and-interpreting-results|Analysing Results]]

---

## Related
- [[robotics/11-state-estimation-and-filtering|State Estimation and Filtering]] — the estimation machinery
- [[robotics/10-motion-planning|Motion Planning]] — what consumes the map
- [[robotics/02-sensors-and-perception|Sensors and Perception]] — lidar, cameras, and their failure modes
- [[robotics/README|Robotics map]]
