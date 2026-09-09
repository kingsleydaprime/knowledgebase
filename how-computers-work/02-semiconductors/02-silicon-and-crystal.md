# Module 7: Silicon and the Crystal Lattice (From Sand to Wafer)

**[Beginner]** — Module 6 said group IV shares four bonds. This module turns that sketch into a real material: the lattice geometry, the extraordinary purity required, and how a wafer is actually made.

## Before you start

- You know silicon has 4 valence electrons and forms four covalent bonds — [[how-computers-work/02-semiconductors/01-atoms-and-electrons|module 6]].
- You can work with scientific notation and convert between cm³ and m³.

**After this lesson you will be able to:**

1. Describe the diamond cubic lattice and explain why the four-bond arrangement forces that specific geometry.
2. Explain each stage from quartz sand to a polished wafer, and say what problem each stage solves.
3. Calculate silicon's atomic density and the residual impurity concentration at a given purity grade.
4. Explain why silicon must be purified to roughly one part per billion *before* impurities are deliberately added back at one part per million.

**Study route:** section 5 contains the argument the rest of Part III depends on. Sections 3–4 are process description — read for understanding, not memorisation.

---

## 1. Why this exists (real-world motivation)

Module 6 ended with a promising claim: silicon's conductivity is controllable, because it has few enough intrinsic carriers that added impurities can dominate.

**That claim has a hidden requirement.** If control comes from impurities you add deliberately, then impurities you did *not* add are not a minor quality problem — they are noise directly on top of your signal. A stray phosphorus atom is indistinguishable from one you placed on purpose.

So before you can dope silicon, you must first make silicon that has essentially nothing in it. This turns out to be one of the hardest materials-engineering problems ever solved routinely, and it is why a semiconductor fab costs billions rather than millions.

**The material this module produces — a single crystal of silicon, pure to about one atom in a billion — is arguably the most refined bulk substance humans manufacture.**

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Crystal** | A solid whose atoms sit in a regular repeating pattern | Bricks in a wall |
| **Lattice** | The repeating geometric arrangement itself | The bricklaying pattern |
| **Unit cell** | The smallest block that tiles to build the whole crystal | One repeating tile |
| **Diamond cubic** | Silicon's specific lattice, where every atom bonds to four neighbours tetrahedrally | — |
| **Amorphous** | Non-crystalline — atoms with no long-range order | Glass |
| **Polycrystalline** | Many small crystals stuck together at random angles | A dry-stone wall |
| **Monocrystalline** | One single unbroken crystal throughout | A single carved block |
| **Grain boundary** | The mismatched seam where two crystal grains meet | The gap between stones |
| **Czochralski process** | Pulling a single crystal from a melt using a seed | Drawing a candle from wax |
| **Ingot / boule** | The cylindrical single crystal produced | A salami |
| **Wafer** | A thin polished slice of the ingot | One slice of that salami |
| **9N purity** | 99.9999999% — nine nines | 1 unwanted atom per billion |

---

## 3. The diamond cubic lattice

Each silicon atom forms four covalent bonds. **Four bonds around one atom, repelling each other as far apart as possible, point to the corners of a tetrahedron** — at 109.5° to each other. The geometry is forced, not chosen.

```
   One atom and its four neighbours (tetrahedral):

              Si
               │
               │
        Si ────Si──── Si          all bond angles 109.5°
              ╱ ╲
            ╱     ╲
          Si       (fourth neighbour, out of the page)
```

Repeat that arrangement in every direction and you get the **diamond cubic** lattice — literally the same structure as diamond, since carbon is also group IV.

Two numbers worth carrying:

- **Lattice constant:** 5.431 Å ($5.431 \times 10^{-10}$ m) — the unit cell edge length.
- **Atomic density:** about $5.0 \times 10^{28}$ atoms per m³, which is $5.0 \times 10^{22}$ per cm³.

That density is the denominator for every purity and doping calculation in Part III.

**Notice how open the structure is.** Diamond cubic fills only about 34% of space, compared with 74% for the close-packed arrangements metals adopt. The bonds are directional — they point where the tetrahedron says, not wherever packing would be tightest. That openness is what leaves room for dopant atoms to substitute in without wrecking the lattice.

---

## 4. From sand to wafer

### Step 1 — the raw material

Silicon is the **second most abundant element in Earth's crust**, about 28% by mass, after oxygen. It is never found pure; it occurs as silicon dioxide (SiO₂) — quartz sand — and in silicates.

**The raw material is free and unlimited.** Everything expensive that follows is purification, not extraction.

### Step 2 — carbothermic reduction → metallurgical grade

Heat quartz with carbon in an arc furnace at around 2000 °C:

$$\mathrm{SiO_2} + 2\mathrm{C} \rightarrow \mathrm{Si} + 2\mathrm{CO}$$

The carbon strips the oxygen away. The result is **metallurgical-grade silicon**, about **98–99% pure**.

That sounds excellent and is hopelessly inadequate. 99% pure means **one atom in a hundred** is something else — roughly $5 \times 10^{26}$ impurity atoms per m³, which is *ten thousand times more* than the dopant concentration you eventually want to control. Useless for electronics; fine for making aluminium alloys and silicones, which is where most of it goes.

### Step 3 — the Siemens process → electronic grade

To go further, convert the silicon into a gas that can be distilled. React it with hydrogen chloride to make trichlorosilane (HSiCl₃), which boils at 32 °C, then **fractionally distil it** — the same physical principle as refining crude oil, exploiting tiny differences in boiling point between the compound you want and its contaminants.

Then reverse the reaction, depositing pure silicon onto heated rods.

The result is **electronic-grade polysilicon**, typically **99.9999999% pure (9N)** or better — around **one impurity atom per billion silicon atoms**.

> [!NOTE]
> **A sense of scale.** One part per billion is one second in 32 years, or one grain of sand in a swimming pool. This purity is achieved in bulk, continuously, at industrial scale, for a commodity price.

### Step 4 — Czochralski growth → single crystal

The polysilicon is pure but **polycrystalline** — many small crystals at random angles, with grain boundaries between them.

**Grain boundaries are fatal for devices.** They scatter carriers unpredictably, trap charge, and provide fast diffusion paths that let dopants wander where they should not. A transistor built across one behaves differently from an identical transistor built beside it, and reproducibility is the whole game in chip manufacturing.

The fix is the **Czochralski process**:

```
              ┌──────┐  ← pull slowly upward (mm/hour) while rotating
              │ seed │
              ├──────┤
             ╱        ╲
            │  growing │  ← atoms join the crystal at the melt surface,
            │  crystal │     each one adopting the seed's orientation
            ╲          ╱
        ═════▓▓▓▓▓▓▓▓▓▓═════
        ║  molten silicon  ║  ← 1414 °C
        ║   (crucible)     ║
        ╚══════════════════╝
```

1. Melt the polysilicon at silicon's melting point, **1414 °C**.
2. Dip in a small **seed crystal** with a known, perfect orientation.
3. Pull upward slowly — millimetres per hour — while rotating.
4. Atoms attach at the liquid–solid boundary and **align with the existing lattice**, because that is the lowest-energy position available.

The seed's orientation propagates through the entire boule. The result is a **monocrystalline ingot**, commonly 300 mm in diameter and up to two metres long — a single unbroken crystal weighing hundreds of kilograms, in which essentially every atom sits where the lattice says it should.

**A bonus:** Czochralski growth purifies further. Most impurities are more soluble in liquid silicon than in solid, so they preferentially stay in the melt rather than joining the crystal — an effect called **segregation**. The crystal comes out cleaner than the material it grew from.

**Dopants are often added right here**, dissolved into the melt in a measured quantity, producing a uniformly doped ingot. This is the "bulk doping" of [[how-computers-work/02-semiconductors/04-doping|module 9]], as opposed to the localised implantation used to pattern individual devices.

### Step 5 — slicing and polishing

The ingot is ground to a precise diameter, then sliced with a diamond wire saw into wafers under a millimetre thick. Slicing leaves surface damage, so wafers are then lapped, etched, and finished by **chemical-mechanical polishing (CMP)**.

The resulting surface is flat to within a few nanometres — because features patterned onto it will themselves be a few nanometres across, and the lithography that prints them has almost no depth of focus.

---

## 5. The argument that justifies all of it

Here is why the purity numbers above are what they are. This is the section to understand.

**Silicon's atomic density is $5.0 \times 10^{22}$ atoms/cm³.**

**Typical doping levels are $10^{15}$ to $10^{18}$ dopant atoms/cm³.** As a fraction of the lattice:

$$\frac{10^{15}}{5.0 \times 10^{22}} = 2 \times 10^{-8} = 0.02 \text{ parts per million}$$

**You control silicon's electrical behaviour by changing roughly one atom in fifty million.** That is the whole trick, and it is only possible because pure silicon has so few intrinsic carriers to begin with — its intrinsic carrier concentration at room temperature is about $10^{10}$ per cm³, so adding $10^{15}$ dopants multiplies the carrier count by a hundred thousand.

**Now the requirement follows immediately.** If deliberate doping sits at $10^{15}$/cm³, residual contamination must be far below that, or you have no idea what you built.

At 9N purity, residual impurities are:

$$5.0 \times 10^{22} \times 10^{-9} = 5.0 \times 10^{13} \text{ atoms/cm}^3$$

Compare with the lightest doping of $10^{15}$/cm³: **the deliberate dopants outnumber the accidental ones by only about 20 to 1.** That is a workable but genuinely tight margin, which is exactly why lightly doped material demands 10N or 11N purity, while heavily doped regions can tolerate less.

> [!NOTE]
> **This is the reason for the entire purification chain.** You do not purify silicon because purity is inherently good. You purify it to establish a **known, empty baseline**, so that the impurities you add on purpose are the only ones that matter.
>
> It is the same principle as taring a balance before weighing. Control requires a known zero — and in silicon, "zero" costs a Siemens process and a Czochralski puller.

---

## 6. Predict before reading on

A 300 mm wafer is 775 μm thick. Silicon's atomic density is $5.0 \times 10^{22}$/cm³.

**Roughly how many silicon atoms are in one wafer, and how many residual impurity atoms at 9N purity?**

<details><summary>Check your answer</summary>

Radius 15 cm, thickness 0.0775 cm.

$$V = \pi r^2 h = \pi \times 225 \times 0.0775 \approx 54.8 \text{ cm}^3$$

$$N_{Si} = 54.8 \times 5.0 \times 10^{22} \approx 2.7 \times 10^{24} \text{ atoms}$$

At 9N purity, impurities are $10^{-9}$ of that:

$$N_{imp} \approx 2.7 \times 10^{15} \text{ atoms}$$

**Nearly three thousand trillion unwanted atoms in a single wafer** — and this is considered extraordinarily pure material. The number feels alarming until you compare it with the ~$10^{18}$ dopant atoms deliberately placed in the same wafer. Fractions, not absolute counts, are what matter.
</details>

---

## 7. Worked example — runnable

Save as `silicon_lab.py` and run `python3 silicon_lab.py`.

```python
import math

SI_ATOMIC_DENSITY = 5.0e22       # atoms per cm^3
SI_INTRINSIC_CARRIERS = 1.0e10   # carriers per cm^3 at 300 K

def purity_to_impurity_density(nines):
    """Residual impurity atoms per cm^3 at a given N-nines purity grade."""
    return SI_ATOMIC_DENSITY * 10 ** (-nines)

def wafer_volume_cm3(diameter_mm, thickness_um):
    radius_cm = diameter_mm / 10 / 2
    thickness_cm = thickness_um / 10_000
    return math.pi * radius_cm ** 2 * thickness_cm

def doping_fraction(doping_per_cm3):
    """Dopant atoms as a fraction of lattice atoms, and as parts per million."""
    fraction = doping_per_cm3 / SI_ATOMIC_DENSITY
    return fraction, fraction * 1e6

if __name__ == "__main__":
    print("Residual impurities by purity grade:")
    for nines, label in [(2, "metallurgical (99%)"),
                         (9, "electronic 9N"),
                         (11, "electronic 11N")]:
        d = purity_to_impurity_density(nines)
        print(f"  {label:22s} {d:.2e} impurity atoms/cm^3")

    print()
    print("Doping levels as a fraction of the lattice:")
    for doping in (1e15, 1e17, 1e19):
        frac, ppm = doping_fraction(doping)
        print(f"  {doping:.0e}/cm^3 -> {frac:.2e} of atoms ({ppm:.3f} ppm)")

    # The margin that justifies the whole purification chain
    residual_9n = purity_to_impurity_density(9)
    light_doping = 1e15
    margin = light_doping / residual_9n
    print()
    print(f"9N residual = {residual_9n:.1e}/cm^3, light doping = {light_doping:.0e}/cm^3")
    print(f"  deliberate dopants outnumber accidental ones {margin:.0f}:1")
    assert 15 < margin < 25, "margin should be tight but workable"

    # Why doping works at all: it swamps the intrinsic carriers
    print(f"  and light doping exceeds intrinsic carriers by"
          f" {light_doping/SI_INTRINSIC_CARRIERS:.0e}x")

    # One 300 mm wafer
    v = wafer_volume_cm3(300, 775)
    atoms = v * SI_ATOMIC_DENSITY
    print()
    print(f"300 mm wafer: {v:.1f} cm^3, {atoms:.2e} silicon atoms")
    print(f"  impurities at 9N: {atoms*1e-9:.2e} atoms")
    print(f"  dopants at 1e17/cm^3: {v*1e17:.2e} atoms")
    assert v * 1e17 > atoms * 1e-9, "dopants must dominate residual impurities"

    print("silicon_lab: passed")
```

Expected output:

```
Residual impurities by purity grade:
  metallurgical (99%)    5.00e+20 impurity atoms/cm^3
  electronic 9N          5.00e+13 impurity atoms/cm^3
  electronic 11N         5.00e+11 impurity atoms/cm^3

Doping levels as a fraction of the lattice:
  1e+15/cm^3 -> 2.00e-08 of atoms (0.020 ppm)
  1e+17/cm^3 -> 2.00e-06 of atoms (2.000 ppm)
  1e+19/cm^3 -> 2.00e-04 of atoms (200.000 ppm)

9N residual = 5.0e+13/cm^3, light doping = 1e+15/cm^3
  deliberate dopants outnumber accidental ones 20:1
  and light doping exceeds intrinsic carriers by 1e+05x

300 mm wafer: 54.8 cm^3, 2.74e+24 silicon atoms
  impurities at 9N: 2.74e+15 atoms
  dopants at 1e17/cm^3: 5.48e+18 atoms
silicon_lab: passed
```

---

## 8. Common pitfalls and traps

1. **Thinking "pure silicon" means chemically pure only.** It must also be **structurally** pure — a single crystal. Chemically perfect polysilicon is still useless for transistors.
2. **Assuming higher purity is always better.** It costs enormously and 11N is unnecessary for heavily doped regions. Purity is specified per application, not maximised.
3. **Confusing the two doping routes.** Melt doping produces uniform bulk material; ion implantation patterns individual device regions on a finished wafer. Both appear in module 9.
4. **Underestimating grain boundaries.** They do not merely degrade performance slightly; they destroy the device-to-device reproducibility that mass manufacturing depends on.
5. **Reading absolute impurity counts as alarming.** $10^{15}$ stray atoms per wafer sounds catastrophic until compared with $10^{24}$ lattice atoms. Always work in fractions.

---

## 9. Check your understanding

1. **Why is amorphous silicon used in cheap solar panels but never for CPUs?**
   <details><summary>Answer</summary>
   Amorphous silicon has no long-range order, so it is full of dangling bonds and trap states. Carrier mobility is orders of magnitude lower and behaviour varies from point to point.<br>
   A solar panel only needs to absorb photons and collect <em>some</em> current over a large area — it tolerates poor mobility and does not need two devices to match. A CPU needs billions of transistors with nearly identical switching characteristics, which demands a perfect single crystal. Different requirements, different material, and amorphous silicon is far cheaper.
   </details>

2. **Czochralski growth leaves impurities preferentially in the melt. What does that imply about the two ends of an ingot?**
   <details><summary>Answer</summary>
   The <strong>tail</strong> end — grown last, from a melt progressively enriched in rejected impurities — is dirtier than the <strong>seed</strong> end. Resistivity therefore varies along the boule's length.<br>
   Manufacturers measure this, grade wafers by position, and discard the extreme ends. It is also the basis of <strong>zone refining</strong>, which sweeps a molten band repeatedly along a rod to drive impurities to one end, then cuts it off.
   </details>

3. **Silicon's lattice fills only 34% of space. Why is that useful rather than wasteful?**
   <details><summary>Answer</summary>
   The open, directional structure leaves room for dopant atoms to <strong>substitute into lattice sites without severely straining the crystal</strong>. A close-packed metal has no such room, so impurity atoms distort it heavily.<br>
   It also allows dopants to be driven in by diffusion and implantation and then settle onto proper lattice sites during annealing — which is the whole basis of how devices are patterned.
   </details>

4. **If metallurgical silicon is 99% pure, why can't you simply dope it more heavily to swamp the contaminants?**
   <details><summary>Answer</summary>
   Two independent reasons. First, 99% pure means $5 \times 10^{20}$ impurities/cm³, so swamping them would need doping above $10^{21}$/cm³ — beyond silicon's solid solubility limit, at which dopants precipitate out instead of dissolving.<br>
   Second and more fundamentally, the contaminants are a <strong>random mixture</strong>: some donors, some acceptors, many deep-level traps that kill carrier lifetime outright. You cannot swamp a mixture whose composition you do not know and which varies from batch to batch. Doping controls a <em>known</em> baseline; it cannot rescue an unknown one.
   </details>

---

## 10. Practice — independent task

**Task:** A fab is evaluating whether it can use cheaper 8N silicon (99.999999%) instead of 10N for a new product.

- **(a)** Compute the residual impurity density for 8N and 10N silicon in atoms/cm³.
- **(b)** The product needs a lightly doped region at $5 \times 10^{15}$/cm³. Compute the ratio of deliberate dopants to residual impurities for both grades.
- **(c)** Assume a design rule that dopants must outnumber residual impurities by at least 100:1 for predictable behaviour. Which grades pass?
- **(d)** The same product also has heavily doped contact regions at $10^{20}$/cm³. Does 8N pass the 100:1 rule *there*?
- **(e)** Based on (c) and (d), write a two-sentence recommendation. Consider whether one wafer must serve both region types.
- **(f)** Extend `silicon_lab.py` with a `passes_design_rule(doping, nines, ratio=100)` function returning a boolean, and reproduce your answers to (c) and (d) as assertions.

**Done when:** your function agrees with your hand calculations, and your recommendation explicitly addresses the fact that both region types are patterned onto the *same* wafer.

<details><summary>Hint for (e), only if stuck</summary>
The lightly doped region and the heavily doped contacts are not separate wafers — they are different regions of the same die. The wafer's purity grade must therefore satisfy the <em>most demanding</em> region on it. Which region is that, and why is it the lightly doped one rather than the heavily doped one?
</details>

---

## 11. Tradeoffs and limits

- **Czochralski silicon contains dissolved oxygen** from the quartz crucible, typically $10^{17}$–$10^{18}$/cm³. Usually harmless and sometimes beneficial — oxygen precipitates can getter metallic contaminants — but unacceptable for some devices, which use **float-zone** silicon grown without a crucible at higher cost.
- **Bigger wafers are better economically, up to a point.** Going from 200 mm to 300 mm roughly doubled the die per wafer for similar processing cost per wafer. The move to 450 mm was planned and abandoned: crystal growth, handling and equipment costs rose faster than the yield gains.
- **This module covers bulk material only.** Modern devices are built in thin surface layers, often epitaxial films grown on the wafer, and increasingly in three-dimensional structures. The wafer is the substrate, not the device.
- **Nothing here explains why silicon conducts as it does.** Bond strength was quoted in module 6 without justification. The next module supplies the real mechanism.

---

## Before moving on

- [ ] Describe the diamond cubic lattice and say why four bonds force tetrahedral geometry.
- [ ] Name each stage from sand to wafer and the problem it solves.
- [ ] Compute residual impurity density from a purity grade and silicon's atomic density.
- [ ] Explain why purification must reach ~1 ppb before doping at ~1 ppm makes sense.
- [ ] Explain why polycrystalline silicon is unusable for CPUs even at perfect chemical purity.

**Recap:** Silicon's four bonds force a tetrahedral, diamond cubic lattice with $5 \times 10^{22}$ atoms/cm³. Sand is reduced to 99% metallurgical silicon, distilled as trichlorosilane to 9N+ electronic grade, grown into a single crystal by the Czochralski process, then sliced and polished. The extreme purity exists to establish a known-empty baseline, so that deliberate dopants at $10^{15}$–$10^{18}$/cm³ — one atom in fifty million — are the only electrically significant impurities present.

**Next:** [[how-computers-work/02-semiconductors/03-energy-bands|Module 8 — Energy Bands and Conduction]] replaces the valence-counting model with the one that actually explains conduction, and produces the single number — the band gap — that correctly sorts every material into conductor, insulator or semiconductor.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/02-semiconductors/04-doping|Module 9 — Doping]] — where the prepared baseline gets used
- [[how-computers-work/02-semiconductors/01-atoms-and-electrons|Module 6 — Atoms and Electrons]]
