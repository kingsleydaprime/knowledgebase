# Failure and Yield

**[Intermediate → Advanced]** — Turning a six-component stress tensor into one number and a verdict. The criteria, what each assumes, and why most real failures are fatigue.

## The problem

You have a stress state — six independent components. Material data comes from a **uniaxial** tensile test — one number.

**A failure criterion is a function that reduces the tensor to a scalar comparable with that one number:**

$$f(\boldsymbol\sigma) \geq \sigma_{\text{allowable}} \quad\Longrightarrow\quad \text{failure}$$

Different criteria embody different assumptions about *how* the material fails, and choosing the wrong one gives a confidently wrong answer.

## Ductile vs brittle

The distinction that determines which criterion applies.

| | Ductile | Brittle |
|---|---|---|
| Mechanism | **shear** — dislocation slip | **tensile separation** |
| Warning | large plastic deformation first | none — sudden |
| Fracture plane | 45° to max principal stress | ⊥ to max principal stress |
| Tension vs compression | roughly symmetric | **much stronger in compression** |
| Examples | mild steel, aluminium, copper | cast iron, concrete, glass, ceramics |

**The fracture surface tells you the mechanism.** Twist a piece of chalk (brittle) and it breaks along a 45° helix — following the principal *tension*. Twist mild steel and it fails on a transverse plane — following the maximum *shear*. Same loading, different criterion, visibly different result. → [[engineering/01-continuum-mechanics/05-stress|Stress]]

## Von Mises — for ductile materials

The standard, and the one you'll use most:

$$\sigma_v = \sqrt{\tfrac{1}{2}\left[(\sigma_1-\sigma_2)^2 + (\sigma_2-\sigma_3)^2 + (\sigma_3-\sigma_1)^2\right]}$$

Yield when $\sigma_v \geq \sigma_y$.

Equivalently, in terms of the deviatoric stress:

$$\sigma_v = \sqrt{\tfrac{3}{2}\,s_{ij}s_{ij}}$$

**Why it's built on the deviator:** metals yield by dislocation slip, which is driven by shear. **Hydrostatic pressure produces no shear**, so it produces no yielding — a solid steel ball at the bottom of the ocean is unharmed, while a hollow one implodes (that's buckling, a different failure). → [[engineering/01-continuum-mechanics/04-strain-measures|the deviatoric split]]

The physical interpretation is **distortion energy**: yielding begins when the energy of shape change reaches a critical value, independent of the energy of volume change.

In principal stress space, the von Mises surface is a **cylinder** whose axis is the hydrostatic line $\sigma_1=\sigma_2=\sigma_3$. Move along that axis — pure pressure — and you never reach the surface.

> **Von Mises stress is what FE post-processors plot by default**, and it's usually the right thing to look at for metals. But it is a **scalar with no sign** — it cannot distinguish tension from compression. For a material with different tensile and compressive strengths (concrete, cast iron, most polymers) it is simply the wrong criterion.

## Tresca — maximum shear stress

$$\tau_{max} = \frac{\sigma_1 - \sigma_3}{2} \geq \frac{\sigma_y}{2}$$

Simpler, and **always conservative relative to von Mises** — up to 15% more so in pure shear.

In principal space it's a **hexagonal prism** inscribed inside the von Mises cylinder.

**Used in pressure-vessel codes** (ASME) precisely because it's conservative and easy to hand-check. Experimentally, von Mises fits metal data better; Tresca errs safe. The corners of the hexagon make it awkward numerically, which is why FE plasticity uses von Mises.

## Maximum principal stress (Rankine) — for brittle materials

$$\sigma_1 \geq \sigma_{ut}$$

Failure when the largest principal *tension* reaches the ultimate tensile strength.

Correct for brittle materials, which separate rather than slip. And it captures the asymmetry: concrete is roughly **10× stronger in compression than tension**, which is the entire reason for reinforced concrete — steel carries the tension the concrete cannot.

**Mohr–Coulomb** generalises this for materials whose shear strength depends on normal stress:

$$\tau = c + \sigma_n\tan\phi$$

with $c$ the cohesion and $\phi$ the friction angle. **The standard criterion in soil and rock mechanics**, where confining pressure genuinely does increase strength — which is why deep rock is stronger than surface rock, and why sand holds together under load but not loose.

**Drucker–Prager** is the smooth version, used in FE because it has no corners.

## Choosing

| Material | Criterion |
|---|---|
| Ductile metal (steel, aluminium) | **von Mises** |
| Ductile, conservative / code work | **Tresca** |
| Brittle (cast iron, glass, ceramic) | **max principal stress** |
| Concrete, rock, soil | **Mohr–Coulomb** or Drucker–Prager |
| Composites | **Tsai–Wu / Hashin** — direction-dependent |
| Anything cyclic | **none of these** — see fatigue |

That last row matters more than the rest.

## Fatigue

> **Most real structural failures are fatigue.** A part that survives its static load indefinitely can fail after millions of cycles at a fraction of that load.

Cracks initiate at a stress concentration, grow a little each cycle, and eventually the remaining section fails suddenly. **Static criteria say nothing about this.**

**The S–N curve** plots stress amplitude against cycles to failure:

- **Steel has an endurance limit** — below roughly $0.5\sigma_{ut}$ it survives indefinitely ($>10^7$ cycles)
- **Aluminium does not.** It fails eventually at any stress amplitude, which is why aircraft have finite fatigue lives and mandated inspection intervals

**Mean stress matters.** A tensile mean stress reduces allowable amplitude, captured by the Goodman or Gerber relations. This is why **compressive residual stress improves fatigue life** — and why shot peening, cold-rolling threads, and autofrettage of gun barrels all work.

**The practical levers:**

- **Eliminate stress concentrations.** Fillets, generous radii, no sharp internal corners. This dominates everything else → [[engineering/01-continuum-mechanics/08-linear-elasticity|stress concentration]]
- **Surface finish matters enormously** — cracks initiate at the surface, so a machined finish outperforms an as-cast one substantially
- **Compressive residual stress** via peening
- **Avoid fretting** at joints and press fits

**Miner's rule** sums damage over variable amplitude: $\sum n_i/N_i \geq 1$ predicts failure. It's crude — it ignores load sequence — and it's still what's used.

Historical note worth carrying: the **de Havilland Comet** crashes of 1954 were fatigue cracks starting at square window corners. The fix — rounded windows — is why every aircraft window you've looked through has a radius.

## Fracture mechanics

For a body that already contains a crack, stress-based criteria fail: [[engineering/01-continuum-mechanics/08-linear-elasticity|linear elasticity predicts infinite stress at a crack tip]].

**Replace stress with the stress intensity factor:**

$$K_I = Y\sigma\sqrt{\pi a}$$

where $a$ is crack length and $Y$ a geometry factor. Fracture when $K_I \geq K_{Ic}$, the **fracture toughness** — a measured material property.

**The $\sqrt{a}$ is the important part.** Doubling crack length raises $K$ by only 41% — cracks grow slowly, then accelerate. Combined with **Paris' law** ($da/dN = C\Delta K^m$, with $m \approx 3$ for steel), this is the basis of **damage-tolerant design**: assume a crack exists, predict its growth, and inspect before it reaches critical length. That's how aircraft are certified.

**Toughness and strength trade off.** High-strength steels are generally less tough — they tolerate smaller cracks before fracturing. Choosing the strongest available alloy can *reduce* structural safety, which is genuinely counterintuitive and a real design trap.

**Ductile-to-brittle transition:** many steels become brittle below a transition temperature. The **Liberty ship** fractures of WWII — hulls splitting in cold North Atlantic water — established this, and it's why toughness is specified at service temperature rather than at room temperature.

## Other failure modes

Stress-based criteria miss several important ones entirely:

**Buckling** — instability, not strength. A slender column fails at a stress far below yield, with the material undamaged. **Strength doesn't help; only stiffness and geometry do.** → [[engineering/01-continuum-mechanics/09-beams-and-structures|Beams and Structures]]

**Creep** — slow deformation under sustained load at high temperature (above ~0.4 of the melting point in kelvin). The design limit for turbine blades, boiler tubes, and lead pipes.

**Corrosion and stress-corrosion cracking** — chemistry, not mechanics, and often the actual initiator of a fatigue crack.

**Wear and fretting** — surface degradation at contacts.

**Impact** — high strain rate changes material behaviour; many materials embrittle. A static toughness value can be badly optimistic.

## Safety factors

$$n = \frac{\text{strength}}{\text{applied stress}}$$

Typical values: 1.5–2 for well-characterised static loads; 2–4 where loads are uncertain; **1.5 for aircraft structure** (with extremely well-known loads and rigorous inspection); 3–5 for pressure vessels.

**A safety factor covers ignorance, not physics.** Material variability, load uncertainty, manufacturing tolerance, modelling error, and degradation over life.

Which is why **a large safety factor does not compensate for the wrong criterion.** Applying von Mises to a brittle material with $n=4$ is still wrong — you've scaled a prediction that was never valid.

**Limit-state design** (Eurocode, LRFD) is the modern replacement: separate partial factors on loads and on resistances, calibrated so the *probability* of failure meets a target. More honest than a single lumped number, because it distinguishes "we don't know the load" from "we don't know the material".

## The practical checklist

1. **Ductile or brittle?** Choose von Mises or max principal accordingly
2. **Static or cyclic?** If cyclic, fatigue governs and static criteria are irrelevant
3. **Stress concentrations?** Check fillets and holes; that's where it will fail
4. **Slender in compression?** Check buckling before strength
5. **Hot, or loaded for years?** Check creep
6. **Cracks assumed present?** Fracture mechanics, not stress
7. **Cold service?** Check the ductile–brittle transition
8. **Did the analysis stay inside its assumptions?** If a linear-elastic run predicts stress above yield, the result is invalid — rerun it plastic → [[engineering/01-continuum-mechanics/07-constitutive-models|Constitutive Models]]

That last one is the most commonly ignored, and the most consequential.

---

## Related
- [[engineering/01-continuum-mechanics/05-stress|Stress]] — principal stresses and the deviator
- [[engineering/01-continuum-mechanics/08-linear-elasticity|Linear Elasticity]] — stress concentration and the crack-tip singularity
- [[engineering/01-continuum-mechanics/09-beams-and-structures|Beams and Structures]] — buckling
- [[engineering/01-continuum-mechanics/README|Continuum mechanics map]]
