# Stability and Root Locus

**[Intermediate]** — What stability actually means, how to test for it without factoring polynomials, and how to see where the closed-loop poles go as you turn the gain up.

## What stability means

**BIBO stability** — bounded input, bounded output. A bounded input can never produce an unbounded output.

For a linear time-invariant system, that's equivalent to a statement about poles, and it's the criterion the whole field uses:

$$\boxed{\text{Stable} \iff \text{all closed-loop poles lie strictly in the left half plane}}$$

Three cases:

| Poles | Behaviour |
|---|---|
| All in LHP (Re < 0) | **stable** — response decays |
| Any in RHP (Re > 0) | **unstable** — response grows without bound |
| Simple poles on the axis, none in RHP | **marginally stable** — sustained oscillation |

**Marginal stability is not "just barely stable" — treat it as unstable.** Repeated poles on the axis actually diverge, and any real system has enough model error that a pole nominally *on* the axis is somewhere unknown near it.

**The poles that matter are the closed-loop poles** — roots of $1 + L(s) = 0$, not the poles of the plant. An unstable plant can be stabilised by feedback (that's the point), and a stable plant can be destabilised by it.

## Routh–Hurwitz

You can test stability **without finding the roots**. For a polynomial of degree 5 or more there's no closed form, so this matters.

$$a_n s^n + a_{n-1}s^{n-1} + \cdots + a_1 s + a_0 = 0$$

**Necessary condition first, and it's free:** all coefficients must be present and have the same sign. A missing term or a sign change means unstable — stop there. (It isn't sufficient: all-positive coefficients can still hide RHP roots for $n \geq 3$.)

**The Routh array.** For $s^3 + a_2 s^2 + a_1 s + a_0$:

```
s³ │  1     a₁
s² │  a₂    a₀
s¹ │  b₁    0        b₁ = (a₂a₁ − a₀)/a₂
s⁰ │  a₀
```

Each row is built from the two above it by a determinant-like cross multiplication.

> **The number of sign changes in the first column equals the number of RHP roots.** No sign changes, no RHP roots, stable.

For the cubic that means: stable iff all coefficients positive **and** $a_2 a_1 > a_0$.

**What makes it genuinely useful is symbolic gain.** Leave $K$ in the characteristic equation and the Routh conditions give you the **exact gain range for stability** in one calculation:

$$s^3 + 3s^2 + 2s + K = 0 \quad\Rightarrow\quad 6 > K > 0$$

At $K = 6$ the $s^1$ row vanishes — the poles are on the imaginary axis, and that gain is the **ultimate gain** $K_u$ from [[engineering/02-control-theory/04-pid-control|Ziegler–Nichols tuning]]. The auxiliary polynomial from the row above gives the oscillation frequency, hence $T_u$. Routh–Hurwitz computes the Z-N test parameters analytically instead of by experiment.

## Root locus

**The question:** as you increase the controller gain $K$, where do the closed-loop poles move?

Closed-loop poles are the roots of

$$1 + K G(s)H(s) = 0 \quad\Longleftrightarrow\quad KG(s)H(s) = -1$$

which splits into two conditions:

$$\text{Magnitude: } |KGH| = 1 \qquad\qquad \text{Angle: } \angle GH = 180° \pm 360°k$$

**The angle condition alone determines the shape of the locus** — every point on it satisfies $\angle GH = 180°$. The magnitude condition just tells you which gain puts a pole at a given point on it. That separation is what makes the graphical construction possible.

### The construction rules

Enough to sketch a locus by hand, which is still the fastest way to understand a design:

**1. Start and end.** Branches start at the **open-loop poles** ($K = 0$) and end at the **open-loop zeros** ($K \to \infty$). There are $n$ branches for $n$ poles; $n - m$ of them go to infinity.

**2. Real-axis segments.** A point on the real axis is on the locus if the number of real poles and zeros **to its right** is odd.

**3. Asymptotes.** The $n-m$ branches heading to infinity do so along asymptotes at angles

$$\theta = \frac{180°(2k+1)}{n-m}$$

meeting the real axis at the **centroid**

$$\sigma_a = \frac{\sum \text{poles} - \sum \text{zeros}}{n - m}$$

**4. Breakaway points** — where branches leave the real axis, found by solving $dK/ds = 0$.

**5. Imaginary-axis crossings** — where the system goes unstable. Found with Routh–Hurwitz, and this gives you $K_u$.

**6. Symmetry.** The locus is symmetric about the real axis, because complex poles come in conjugate pairs.

### Reading a locus

```
       Im
        │      ╱  ← branches heading right:
        │     ╱      unstable above some K
    ────┼────●───────
        │   ╱ ╲
   ×────┼──╱───╲──×────  Re
        │ ╱     ╲
        │╱       ╲
        │         ╲
```

**The typical story of a second-order system with an added pole:** at low gain the poles are real and sluggish. Raise the gain and they meet, break away, and become a complex pair — the response gets faster and starts overshooting. Raise it further and they head toward the imaginary axis — more overshoot, less damping. Cross it, and the system oscillates and diverges.

**That single picture explains the entire $K_p$ row of the PID tuning table.** Higher gain: faster, more overshoot, less stable. The locus is *why*.

### Designing with it

The practical use is **placing dominant poles where you want them**:

1. Translate the specification into a target pole location — $\zeta$ from the overshoot requirement (an angle from the origin), $\zeta\omega_n$ from the settling time (a vertical line) → [[engineering/02-control-theory/03-time-response|Time Response]]
2. Sketch the locus and see whether it passes through the target region
3. **If it does**, read off the gain from the magnitude condition. Done — a proportional controller suffices
4. **If it doesn't**, you must reshape the locus by adding poles and zeros — that is, by designing a dynamic compensator

**Adding a zero pulls the locus left** (more stable, faster). **Adding a pole pushes it right** (less stable, slower). That's the entire design intuition, and it explains the two classical compensators:

**Lead compensator** — zero closer to the origin than its pole:

$$C(s) = K\frac{s + z}{s + p}, \quad |z| < |p|$$

Pulls the locus left. **Improves transient response** — faster, better damped. It's essentially a filtered PD, and adds phase lead.

**Lag compensator** — pole closer to the origin:

$$C(s) = K\frac{s + z}{s + p}, \quad |z| > |p|$$

A pole–zero pair near the origin, close together. Barely moves the dominant poles, but **raises the low-frequency gain**, which reduces steady-state error. Essentially an approximate PI, and it adds phase lag you must keep away from the crossover frequency.

**Lead–lag** does both — the classical answer when you need transient performance *and* steady-state accuracy, and the structural analogue of a full PID.

## Pole–zero cancellation — a warning

The locus makes an attractive-looking move available: put a controller zero exactly on a bad plant pole to cancel it.

**Don't rely on it.**

**It never cancels exactly.** Your model of the pole is approximate, so a tiny pole–zero pair survives at whatever the real location is.

**If the cancelled pole is unstable, the system is still unstable.** The RHP pole is still there; you've merely made it **unobservable** from the output, so the state grows without bound while the output looks fine — until something saturates or breaks. This is the single most dangerous mistake in classical design, and it's the practical meaning of the observability conditions in [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|note 09]].

**Cancelling a stable, well-damped, well-known pole is acceptable** and is exactly what lag compensator design does deliberately. Cancelling anything near the imaginary axis or in the RHP is not.

## Stability isn't binary

The important shift in thinking, and the bridge to the next two notes.

Knowing a system is stable tells you almost nothing useful. A pole at $-0.001$ is stable, and it takes an hour to settle. A design that goes unstable if the plant gain rises 5% is stable *and useless*.

**What you need is a margin** — how much can the plant change before stability is lost?

Root locus answers this partially (you can see how close the locus is to the axis), but the systematic answer is in the frequency domain: **gain margin and phase margin**. That's [[engineering/02-control-theory/07-nyquist-and-robustness|note 07]], and it's what practising engineers actually design against.

---

## Related
- [[engineering/02-control-theory/02-modelling-and-transfer-functions|Modelling and Transfer Functions]] — the characteristic equation
- [[engineering/02-control-theory/06-frequency-response|Frequency Response]] — the other view of the same problem
- [[engineering/02-control-theory/07-nyquist-and-robustness|Nyquist and Robustness]] — stability with margin
- [[engineering/02-control-theory/09-controllability-observability-and-pole-placement|Pole Placement]] — placing poles directly instead of via gain
- [[engineering/02-control-theory/README|Control theory map]]
