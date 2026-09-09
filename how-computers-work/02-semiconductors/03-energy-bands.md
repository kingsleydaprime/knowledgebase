# Module 8: Energy Bands and Conduction (One Number Sorts All Matter)

**[Intermediate]** — The shell model of module 6 got the trend right and the boundaries wrong. This module replaces it with the model that actually works, and produces the single number that correctly classifies every material: the band gap.

## Before you start

- You know valence electrons determine bonding, and that silicon shares four bonds — [[how-computers-work/02-semiconductors/01-atoms-and-electrons|module 6]].
- You know silicon's atomic density is $5 \times 10^{22}$/cm³ — [[how-computers-work/02-semiconductors/02-silicon-and-crystal|module 7]].
- You are comfortable with exponentials. $e^{-40}$ being unimaginably small is the key intuition.

**After this lesson you will be able to:**

1. Explain why discrete atomic energy levels become continuous bands in a solid.
2. Classify a material as conductor, semiconductor or insulator from its band gap alone, and say why this succeeds where valence counting failed.
3. Explain what a hole is and why treating it as a positive particle is legitimate rather than a fudge.
4. Explain why silicon's conductivity rises with temperature while a metal's falls, and calculate the effect.

**Study route:** sections 3–5 are the model. Section 6 (holes) is the conceptually hardest idea in Part III — read it twice. Section 7 sets up module 13.

---

## 1. Why this exists (real-world motivation)

Module 6's model said: count valence electrons. Four means semiconductor.

**It gave three wrong answers in its own worked example.** Boron came out "metal" and is a metalloid. Phosphorus came out "insulator". Worst of all, **carbon and silicon both have 4 valence electrons and identical lattices, yet diamond is one of the best insulators known and silicon is a semiconductor.** A model that cannot distinguish diamond from silicon cannot be the real mechanism.

Module 6 gestured at the answer — "bond strength differs, 5.5 eV versus 1.12 eV" — without saying where those numbers come from or what they measure.

**This module supplies the mechanism.** It replaces "how many valence electrons" with a single measured quantity that classifies every material correctly, predicts the temperature behaviour, explains why light can generate current, and gives you the number you need for every calculation in Parts IV onward.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Energy band** | A near-continuous range of energies electrons may occupy in a solid | A floor with millions of rooms |
| **Valence band** | The highest band that is full at absolute zero — electrons bound in bonds | The full ground floor |
| **Conduction band** | The next band up — electrons here are free to move | The empty first floor |
| **Band gap** ($E_g$) | The energy range between them, containing no allowed states | The unclimbable stairwell |
| **Electron-volt (eV)** | Energy an electron gains crossing 1 volt; $1.602 \times 10^{-19}$ J | The natural unit here |
| **Hole** | A vacancy in the valence band, behaving as a mobile positive charge | A bubble in water |
| **Electron-hole pair** | Both carriers created together when a bond breaks | — |
| **Recombination** | An electron falling back into a hole, destroying both | — |
| **Intrinsic carriers** ($n_i$) | Carrier concentration in pure, undoped material | — |
| **Mobility** ($\mu$) | How readily a carrier drifts under a field, cm²/(V·s) | — |
| **$kT$** | Characteristic thermal energy available at temperature $T$ | The size of nature's random kicks |

---

## 3. Why levels become bands

Take one silicon atom. Its electrons sit at sharp, discrete energy levels — module 6's shells.

Now bring a second silicon atom close. **The Pauli exclusion principle forbids two electrons in the same quantum state**, so the two atoms' identical levels cannot stay identical. Each level **splits in two**: one slightly lower, one slightly higher.

Bring in a third atom and each level splits three ways. Bring in $N$ atoms and it splits $N$ ways.

```
   1 atom        2 atoms         many atoms          a real crystal
                                                     (N ~ 10^23)

   ─────         ─────           ═════
                 ─────           ═════            ┌─────────────┐
                                 ═════            │▓▓▓▓▓▓▓▓▓▓▓▓▓│  BAND
                                 ═════            └─────────────┘
   ─────         ─────           ═════
                 ─────           ═════            ┌─────────────┐
                                 ═════            │▓▓▓▓▓▓▓▓▓▓▓▓▓│  BAND
                                 ═════            └─────────────┘
   discrete      split in 2      N closely        so many levels, so
   levels                        spaced levels    close, they form a
                                                  continuous BAND
```

In a real crystal $N$ is around $10^{23}$. The levels are so numerous and so finely spaced that they are, for every practical purpose, a **continuous band of allowed energies**.

**But the gaps between the original levels do not disappear.** Bands broaden into the space around each original level; the regions between remain **forbidden** — no allowed states at any energy in there. An electron can sit in a band. It cannot sit in a gap, ever.

Two bands matter:

- The **valence band** — the highest band completely full at absolute zero. These electrons are the ones in covalent bonds.
- The **conduction band** — the next one up, empty at absolute zero. An electron here is detached from any particular bond and free to move through the crystal.

**The band gap $E_g$ is the energy separation between them**, and it is the only number you need.

---

## 4. The band gap classifies everything

```
   CONDUCTOR              SEMICONDUCTOR             INSULATOR
   (metal)                 (silicon)                 (glass)

  ┌──────────┐            ┌──────────┐             ┌──────────┐
  │ conduct. │            │ conduct. │             │ conduct. │
  │▓▓▓▓░░░░░░│ partly     │          │ empty       │          │ empty
  └──────────┘ filled     └──────────┘             └──────────┘
   ▲ overlap                   ▲                        ▲
   │ or partly             1.12 eV gap              9.0 eV gap
   ▼ filled band               ▼                        ▼
  ┌──────────┐            ┌──────────┐             ┌──────────┐
  │▓▓▓▓▓▓▓▓▓▓│ full       │▓▓▓▓▓▓▓▓▓▓│ full        │▓▓▓▓▓▓▓▓▓▓│ full
  │ valence  │            │ valence  │             │ valence  │
  └──────────┘            └──────────┘             └──────────┘

  No gap to cross.        Small gap. Thermal        Huge gap. Nothing
  Carriers always         energy lifts a few        crosses. No carriers,
  available.              electrons across.         ever.
  ALWAYS conducts         SOMETIMES conducts        NEVER conducts
                          -> CONTROLLABLE
```

### Why a full band cannot conduct

This point is subtle and worth stating explicitly, because it is what makes the whole picture work.

**Conduction requires electrons to change their state** — to gain a little energy from the applied field and move to a slightly different momentum. In a **completely full** band, every state is already occupied, so there is nowhere for an electron to move *to*. Pauli forbids it. The band is full of electrons and yet carries no current.

This is why an insulator's packed valence band conducts nothing, and why conduction needs either a partly filled band (a metal) or electrons promoted into an empty one (a semiconductor).

### The numbers

| Material | Band gap (eV) | Gap ÷ $kT$ at 300 K | Behaviour |
| :--- | ---: | ---: | :--- |
| Germanium | 0.66 | 25.5 | semiconductor, leaky |
| **Silicon** | **1.12** | **43.3** | **semiconductor** |
| Gallium arsenide | 1.42 | 54.9 | semiconductor, fast |
| Diamond | 5.47 | 211.6 | insulator |
| Silicon dioxide | 9.0 | 348.1 | excellent insulator |

**Diamond and silicon are now correctly distinguished** — same lattice, same valence count, gaps differing by a factor of five. The model that failed in module 6 succeeds here.

> [!NOTE]
> **Silicon dioxide is on this list for a reason.** SiO₂ is silicon's own native oxide, it grows on a silicon surface simply by heating it in oxygen, and at 9 eV it is a superb insulator.
>
> A semiconductor that manufactures its own perfect insulator is an extraordinary piece of luck, and it is the single biggest reason silicon beat germanium. That oxide becomes the **gate insulator** of every MOSFET in [[how-computers-work/03-transistors/02-mosfet-physics|module 12]] — the "O" in MOS.

---

## 5. Thermal energy — why the gap size matters so much

At any temperature above absolute zero, atoms vibrate and electrons receive random energy kicks. The characteristic size of those kicks is:

$$kT \quad\text{where}\quad k = 8.617 \times 10^{-5} \text{ eV/K}$$

At room temperature (300 K): $kT = 25.85$ **milli**-electron-volts.

**Compare that with silicon's 1.12 eV gap.** The average kick is about **1/43rd** of what is needed. Crossing requires a rare, extreme fluctuation — and the probability of such a fluctuation falls **exponentially**:

$$n_i \propto e^{-E_g / 2kT}$$

That exponential is what produces the colossal spread in the table. A gap five times larger does not make a material five times more insulating; it makes it insulating by a factor of $e^{-170}$ or so. **This is why materials feel like categories rather than a smooth scale** — the underlying quantity varies smoothly, but an exponential turns a smooth input into an apparently discrete output.

### The consequence: temperature dependence

Because carriers must be *thermally created*, heating a semiconductor creates more of them:

| Temperature | $n_i$ (per cm³) | Relative to 300 K |
| ---: | ---: | ---: |
| 250 K | $6.67 \times 10^{7}$ | 0.01× |
| 300 K | $6.68 \times 10^{9}$ | 1× |
| 350 K | $1.86 \times 10^{11}$ | 27.8× |
| 400 K | $2.31 \times 10^{12}$ | 346× |

**A 100 K rise multiplies the carrier count by roughly 350.** This is the opposite of a metal, whose carrier count is fixed and whose resistance rises with temperature — and it is a reliable experimental test of which material you have.

It is also a genuine engineering hazard. A hot chip leaks more, and leaking more makes it hotter, which makes it leak more still — **thermal runaway**. Preventing it is a real constraint on power delivery and cooling design.

> [!NOTE]
> **Now look at how few carriers there are.** At 300 K, $n_i \approx 6.7 \times 10^9$/cm³ against $5 \times 10^{22}$ lattice atoms — about **one atom in $10^{13}$** has given up a carrier.
>
> That extreme scarcity is exactly what makes doping powerful. Adding $10^{15}$ dopants/cm³ — module 7's "one atom in fifty million" — swamps the intrinsic carriers by a factor of about **150,000**. You are not nudging silicon's conductivity; you are completely overwriting it.

---

## 6. Holes — the hardest idea in Part III

When an electron absorbs enough energy to jump the gap, **two things are created, not one.**

There is now a free electron in the conduction band. There is also a **vacancy** in the valence band where it used to be — a broken bond with a missing electron. That vacancy is called a **hole**, and the pair is an **electron-hole pair**.

**The hole moves, and it carries current.** A neighbouring valence electron can hop sideways into the vacancy — a small step within the band, not a jump across the gap. That fills the original hole and creates a new one where the neighbour came from.

```
   Step 1:   Si ── Si ── Si ── Si        ○ = hole (missing electron)
                    ○                     ← an electron from the left
                                            hops right into it

   Step 2:   Si ── Si ── Si ── Si
               ○                          the hole has moved LEFT
                                          while electrons moved RIGHT
```

**Electrons shuffle one way; the vacancy travels the other way.** Rather than track billions of valence electrons each shuffling a tiny distance, physics tracks the vacancy — and the mathematics comes out identical to a single positively charged particle drifting through the crystal.

> [!NOTE]
> **The bubble analogy, and where it breaks.** A bubble in water is not a thing; it is an absence of water. Yet it moves, has a position and velocity, and rises predictably. Describing "the bubble" is far easier than describing every water molecule moving down around it.
>
> A hole is the same kind of object — a genuine, useful description of collective behaviour.
>
> **Where it breaks:** a bubble is a region of *nothing*, whereas a hole sits in a region absolutely packed with electrons. A hole also has an *effective mass* different from an electron's, set by the band structure, which is why the two carriers do not move equally easily. The analogy gets the concept right and the quantitative behaviour wrong.

**Holes are not a bookkeeping fiction.** They have measurable mass and mobility, respond to magnetic fields with the sign of a positive charge (measurable via the Hall effect), and P-type silicon genuinely conducts by hole transport. Treating them as real particles is legitimate physics, not a shortcut.

The reverse process — a conduction electron falling back into a hole, annihilating both and releasing the energy — is **recombination**. At equilibrium, generation and recombination balance exactly, which is what fixes $n_i$ at a stable value for a given temperature.

---

## 7. Mobility — and why PMOS transistors are fat

Electrons and holes both carry current, but **not equally well**. Mobility measures how fast a carrier drifts per unit of applied field:

| Carrier in silicon | Mobility, cm²/(V·s) |
| :--- | ---: |
| Electron | 1350 |
| Hole | 480 |

**Electrons are about 2.8× more mobile than holes.** An electron in the conduction band moves through a mostly empty band; a hole moves by the laborious relay of valence electrons shuffling sideways through a nearly full one. Its greater effective mass follows from the band structure.

**This asymmetry has a direct, visible consequence in every chip ever made.**

In [[how-computers-work/03-transistors/03-cmos|module 13]] you will build gates from complementary pairs: NMOS transistors that conduct via **electrons**, and PMOS transistors that conduct via **holes**. For a gate to switch symmetrically — pulling up as strongly as it pulls down — the two must have equal drive strength.

Since holes are 2.8× less mobile, **PMOS transistors are made roughly 2 to 3 times physically wider than their NMOS partners.** Look at a die photo of a standard cell library and you can see it: the P-type row is visibly taller than the N-type row.

**That layout asymmetry, on every chip in the world, is a direct consequence of a hole being a relay of valence electrons rather than a free particle.** This is the course's method working exactly as intended — a fact about band structure surfacing as a visible feature of silicon layout, six modules later.

---

## 8. Predict before reading on

Germanium's gap is 0.66 eV, silicon's is 1.12 eV. Both were used for early transistors.

**Roughly how many times more intrinsic carriers does germanium have at room temperature, and what practical problem does that cause?**

<details><summary>Check your answer</summary>

The ratio is dominated by the exponential:

$$\frac{n_i(\mathrm{Ge})}{n_i(\mathrm{Si})} \approx \exp\!\left(\frac{E_g(\mathrm{Si}) - E_g(\mathrm{Ge})}{2kT}\right) = \exp\!\left(\frac{1.12 - 0.66}{2 \times 0.02585}\right) = e^{8.90} \approx 7300$$

**Germanium has roughly three to four orders of magnitude more intrinsic carriers** (the measured ratio is around $10^3$; effective-mass differences moderate the pure exponential estimate).

**The practical problem is leakage.** Those thermal carriers conduct whether you want them to or not, so a germanium device never fully turns off — and the leakage worsens rapidly with temperature. Early germanium transistors failed above about 70 °C, while silicon works past 150 °C.

Combined with SiO₂ being a superb native oxide and germanium's oxide being water-soluble, this is why the industry switched to silicon despite germanium's higher carrier mobility.
</details>

---

## 9. Worked example — runnable

Save as `bands_lab.py` and run `python3 bands_lab.py`. Standard library only.

```python
import math

K_BOLTZMANN_EV = 8.617333e-5      # eV per kelvin
ROOM_TEMPERATURE = 300.0          # kelvin

# Band gaps in eV at 300 K
BAND_GAPS = {
    "germanium":       0.66,
    "silicon":         1.12,
    "gallium arsenide":1.42,
    "diamond":         5.47,
    "silicon dioxide": 9.0,
}

# Effective density of states at 300 K, per cm^3
N_C_SILICON = 2.8e19
N_V_SILICON = 1.04e19

def thermal_energy_ev(temperature_k):
    """kT, the characteristic thermal energy available to a carrier."""
    return K_BOLTZMANN_EV * temperature_k

def gap_in_kt(band_gap_ev, temperature_k):
    """How many multiples of kT an electron must find to cross the gap."""
    return band_gap_ev / thermal_energy_ev(temperature_k)

def intrinsic_carriers(temperature_k, band_gap_ev=1.12):
    """Simplified intrinsic carrier concentration for silicon, per cm^3."""
    kt = thermal_energy_ev(temperature_k)
    scale = math.sqrt(N_C_SILICON * N_V_SILICON) * (temperature_k / 300.0) ** 1.5
    return scale * math.exp(-band_gap_ev / (2 * kt))

def classify(band_gap_ev):
    if band_gap_ev < 0.1:  return "conductor"
    if band_gap_ev < 3.0:  return "SEMICONDUCTOR"
    return "insulator"

if __name__ == "__main__":
    kt = thermal_energy_ev(ROOM_TEMPERATURE)
    print(f"thermal energy at {ROOM_TEMPERATURE:.0f} K: kT = {kt*1000:.2f} meV")
    print()
    print(f"{'material':18s} {'gap (eV)':>9s} {'gap/kT':>8s}   class")
    for name, gap in BAND_GAPS.items():
        print(f"{name:18s} {gap:9.2f} {gap_in_kt(gap, ROOM_TEMPERATURE):8.1f}   {classify(gap)}")

    print()
    print("silicon intrinsic carriers vs temperature:")
    base = intrinsic_carriers(300.0)
    for t in (250.0, 300.0, 350.0, 400.0):
        n = intrinsic_carriers(t)
        print(f"  {t:5.0f} K  n_i = {n:.2e} /cm^3   ({n/base:9.3g}x room temperature)")

    # How much of the lattice is ionised at room temperature?
    frac = base / 5.0e22
    print()
    print(f"at 300 K only {frac:.1e} of silicon atoms have donated a carrier")
    print(f"  = 1 atom in {1/frac:.1e}")

    # Mobility: why NMOS is stronger than PMOS
    MU_ELECTRON, MU_HOLE = 1350.0, 480.0   # cm^2 / (V.s) in silicon
    print()
    print(f"electron mobility {MU_ELECTRON:.0f} vs hole mobility {MU_HOLE:.0f} cm^2/V.s")
    print(f"  electrons are {MU_ELECTRON/MU_HOLE:.2f}x more mobile")
    print(f"  -> PMOS must be ~{MU_ELECTRON/MU_HOLE:.1f}x wider than NMOS for equal drive")

    assert classify(1.12) == "SEMICONDUCTOR"
    assert classify(9.0) == "insulator"
    assert gap_in_kt(1.12, 300) > 40
    assert intrinsic_carriers(400) > 100 * intrinsic_carriers(300)
    print()
    print("bands_lab: passed")
```

Expected output:

```
thermal energy at 300 K: kT = 25.85 meV

material            gap (eV)   gap/kT   class
germanium               0.66     25.5   SEMICONDUCTOR
silicon                 1.12     43.3   SEMICONDUCTOR
gallium arsenide        1.42     54.9   SEMICONDUCTOR
diamond                 5.47    211.6   insulator
silicon dioxide         9.00    348.1   insulator

silicon intrinsic carriers vs temperature:
    250 K  n_i = 6.67e+07 /cm^3   (  0.00999x room temperature)
    300 K  n_i = 6.68e+09 /cm^3   (        1x room temperature)
    350 K  n_i = 1.86e+11 /cm^3   (     27.8x room temperature)
    400 K  n_i = 2.31e+12 /cm^3   (      346x room temperature)

at 300 K only 1.3e-13 of silicon atoms have donated a carrier
  = 1 atom in 7.5e+12

electron mobility 1350 vs hole mobility 480 cm^2/V.s
  electrons are 2.81x more mobile
  -> PMOS must be ~2.8x wider than NMOS for equal drive

bands_lab: passed
```

> [!NOTE]
> **This model is deliberately simplified.** It computes $n_i \approx 6.7 \times 10^9$/cm³ at 300 K; the accepted measured value is about $1.0 \times 10^{10}$/cm³. The ~1.5× discrepancy comes from treating the effective densities of states as temperature-independent apart from the $T^{1.5}$ factor, and from ignoring the slight narrowing of the band gap as temperature rises.
>
> The model gets the **scaling** right, which is what it is for. Use measured values, not this function, for any real design.

---

## 10. Common pitfalls and traps

1. **Thinking the band gap is a physical space electrons travel through.** It is a range of *energies* with no allowed states. An electron does not cross it gradually — it is either in one band or the other.
2. **Believing a full band conducts because it is full of electrons.** A full band carries no current at all: with every state occupied, no electron can change state. Emptiness is what enables conduction.
3. **Treating holes as a mathematical convenience.** They have measurable mass, mobility and Hall-effect sign. They are as real as any quasiparticle in physics.
4. **Forgetting carriers are created in pairs.** Thermal generation always makes one electron *and* one hole. Only doping can create one without the other, which is the subject of module 9.
5. **Assuming a bigger gap is proportionally more insulating.** The relationship is exponential. Doubling the gap does not double the resistance; it changes it by many orders of magnitude.
6. **Applying $n_i$ to doped silicon.** $n_i$ is the *intrinsic* concentration. In doped material the carrier count is set almost entirely by the dopants — that is the whole point.

---

## 11. Check your understanding

1. **Why does shining light on silicon make it conduct better, while shining light on copper does essentially nothing?**
   <details><summary>Answer</summary>
   A photon with energy above 1.12 eV — visible light comfortably exceeds it — can be absorbed by a valence electron and lift it across the gap, creating an electron-hole pair. More carriers means more conduction. This is <strong>photoconductivity</strong>, and it is the operating principle of photodiodes, image sensors and solar cells.<br>
   Copper has no gap and already has ~$10^{29}$ free carriers/cm³. Adding a few more via light is an utterly negligible fractional change.
   </details>

2. **Silicon at 400 K has 346× more intrinsic carriers than at 300 K. Why doesn't a CPU stop working when it warms up?**
   <details><summary>Answer</summary>
   Because a CPU's silicon is <strong>doped</strong>, typically to $10^{15}$–$10^{18}$/cm³. Even at 400 K, $n_i \approx 2.3 \times 10^{12}$/cm³ remains far below the doping level, so the dopants still dominate the carrier count and the device behaves as designed.<br>
   The intrinsic carriers do show up as <strong>leakage current</strong>, which rises steeply with temperature and contributes to static power — one reason chips throttle when hot. Push far enough and $n_i$ approaches the doping level, the junctions stop working, and the device fails outright. For silicon that is around 150–200 °C.
   </details>

3. **A material has a 2.3 eV band gap. Predict its behaviour, and its likely colour.**
   <details><summary>Answer</summary>
   A wide-gap semiconductor — $2.3/0.02585 \approx 89\,kT$, so very few thermal carriers and near-insulating at room temperature, but usable as a semiconductor at higher temperatures or under illumination.<br>
   On colour: 2.3 eV corresponds to a wavelength of about 540 nm (green). The material absorbs photons <em>above</em> 2.3 eV — green, blue, violet — and transmits those below, so it appears <strong>orange or red</strong>. This is why band gap and colour are linked, and why wide-gap semiconductors like GaN (3.4 eV) are transparent to visible light and used for blue and UV LEDs.
   </details>

4. **Why do holes have lower mobility than electrons, and why does that matter for circuit layout?**
   <details><summary>Answer</summary>
   A conduction-band electron moves through a nearly empty band with few constraints. A hole moves via valence electrons shuffling sideways through a nearly <em>full</em> band — a relay process with a larger effective mass set by the valence band's curvature.<br>
   For layout: PMOS transistors conduct via holes and are therefore ~2.8× weaker than same-size NMOS. To make a gate switch symmetrically, PMOS devices are drawn 2–3× wider. This is why standard cell layouts have a visibly taller P row, and why PMOS-heavy gates like NOR are slower than NAND — a fact that shapes real logic design in [[how-computers-work/04-logic/01-gates-from-transistors|module 15]].
   </details>

---

## 12. Practice — independent task

**Task:** You are assessing three semiconductors for a sensor that must operate from −40 °C to +200 °C (233 K to 473 K).

| Material | Band gap (eV) |
| :--- | ---: |
| Germanium | 0.66 |
| Silicon | 1.12 |
| Silicon carbide (4H-SiC) | 3.26 |

- **(a)** Compute $kT$ at both temperature extremes in meV.
- **(b)** For each material, compute the ratio $E_g / kT$ at both extremes.
- **(c)** Using `intrinsic_carriers()` adapted for each gap, compute $n_i$ at 233 K and 473 K. State the ratio between them for each material.
- **(d)** The device is doped at $10^{16}$/cm³ and stops working correctly once $n_i$ reaches 1% of the doping level. Which materials survive to 473 K?
- **(e)** Silicon carbide is far more expensive and harder to fabricate than silicon. Given your answer to (d), when is it worth it? Name a real application.
- **(f)** Add a `max_operating_temperature(band_gap, doping)` function that searches for the temperature at which $n_i$ first reaches 1% of the doping level. Report it for all three materials.

**Done when:** you have a temperature limit for each material, and can explain in one sentence why band gap and maximum operating temperature are directly linked.

<details><summary>Hint for (c), only if stuck</summary>
Pass <code>band_gap_ev</code> through to <code>intrinsic_carriers()</code> — it is already a parameter. The $N_C$ and $N_V$ constants are silicon's and are not strictly right for the others, but they only shift the prefactor; the exponential dominates by many orders of magnitude, so the comparison remains valid. Say so in your answer rather than silently ignoring it.
</details>

---

## 13. Tradeoffs and limits of this model

- **Band theory assumes a perfect periodic crystal.** Defects, surfaces and grain boundaries create states *inside* the gap, which trap carriers and degrade devices. This is precisely why module 7 went to such lengths for a single crystal.
- **The simple picture ignores direct versus indirect gaps.** Silicon's gap is *indirect*, meaning an electron crossing it must also change momentum, which requires a lattice vibration. This makes silicon a poor light emitter — which is why LEDs and laser diodes use direct-gap materials like GaAs, and why silicon photonics is hard.
- **Effective mass is a simplification** of real band curvature, which varies with direction in the crystal.
- **Nothing here yet explains a switch.** A band gap explains why silicon *can* conduct a little. It does not explain how to *control* it. That is module 9.

---

## Before moving on

- [ ] Explain why $N$ atoms turn discrete levels into bands, and why gaps survive.
- [ ] Classify materials by band gap, and explain why this beats valence counting.
- [ ] Explain why a completely full band carries no current.
- [ ] Explain what a hole is, why it behaves as a positive carrier, and where the bubble analogy fails.
- [ ] Explain why semiconductor resistance falls with temperature and metal resistance rises.
- [ ] Explain why PMOS transistors are drawn wider than NMOS.

**Recap:** In a solid, atomic energy levels split into near-continuous bands separated by forbidden gaps. The band gap classifies every material: none means conductor, small means semiconductor, large means insulator. Thermal energy $kT$ is 25.85 meV at room temperature against silicon's 1.12 eV gap, so carriers are exponentially rare — about one atom in $10^{13}$ — which makes doping overwhelmingly effective. Crossing the gap creates an electron-hole pair; holes behave as real positive carriers with 2.8× lower mobility, which is why PMOS transistors are drawn wider.

**Next:** [[how-computers-work/02-semiconductors/04-doping|Module 9 — Doping]] takes the scarcity established here and exploits it. You predicted groups III and V back in module 6; now you find out exactly how much control a few parts per million buys.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/03-transistors/02-mosfet-physics|Module 12 — MOSFET Physics]] — where SiO₂'s 9 eV gap becomes the gate insulator
- [[how-computers-work/03-transistors/03-cmos|Module 13 — CMOS]] — where the mobility asymmetry sets transistor sizing
- [[foundations/information-theory/index|information-theory/]] — $kT$ reappears there as the thermodynamic cost of erasing a bit
