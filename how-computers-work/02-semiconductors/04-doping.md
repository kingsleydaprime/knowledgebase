# Module 9: Doping (Engineering a Semiconductor)

**[Intermediate]** — You predicted this back in module 6. Adding one atom in five million changes silicon's resistivity by a factor of 700,000 — and, less obviously, suppresses the carriers you don't want just as hard as it multiplies the ones you do.

## Before you start

- You know silicon's band gap is 1.12 eV, that $kT$ = 25.85 meV at 300 K, and that $n_i \approx 10^{10}$/cm³ — [[how-computers-work/02-semiconductors/03-energy-bands|module 8]].
- You understand holes as mobile positive carriers, and that electron mobility exceeds hole mobility by ~2.8× — module 8.
- You know silicon's atomic density is $5 \times 10^{22}$/cm³ and why 9N purity is required — [[how-computers-work/02-semiconductors/02-silicon-and-crystal|module 7]].

**After this lesson you will be able to:**

1. Explain how group V and group III impurities produce N-type and P-type silicon.
2. Explain why dopants ionise almost completely at room temperature while intrinsic carriers remain vanishingly rare.
3. Apply the mass action law $np = n_i^2$ and explain why doping *reduces* minority carriers.
4. Compute resistivity from doping level, and explain why compensation subtracts rather than adds.

**Study route:** section 4 (shallow levels) is the mechanism, section 6 (mass action) is the non-obvious result. Both are needed for module 10.

---

## 1. Why this exists (real-world motivation)

Module 8 left silicon in an awkward position. It has a band gap small enough that a few electrons cross it thermally — about one atom in $10^{13}$ — so it conducts a little. But "a little, depending on temperature" is not control. You cannot build a switch from a material whose conductivity you merely observe.

**You need to set the carrier concentration deliberately, to a value you choose, that stays put.**

The answer was predicted in module 6 by valence counting alone: substitute in atoms with one extra or one missing valence electron. This module works out what that actually buys — and the answer is more dramatic, and stranger, than "it conducts better".

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Intrinsic** | Pure semiconductor, carriers only from thermal generation | — |
| **Extrinsic** | Deliberately doped | — |
| **Dopant** | An impurity added on purpose to control conductivity | Phosphorus, boron |
| **Donor** | Group V atom — donates a spare electron | Phosphorus, arsenic |
| **Acceptor** | Group III atom — accepts an electron, leaving a hole | Boron, gallium |
| **N-type** | Doped with donors; electrons are the majority carrier | — |
| **P-type** | Doped with acceptors; holes are the majority carrier | — |
| **Majority carrier** | The abundant one, set by doping | Electrons in N-type |
| **Minority carrier** | The rare one, suppressed by doping | Holes in N-type |
| **Shallow level** | A dopant energy level very close to a band edge | 45 meV from the edge |
| **Ionised dopant** | One that has given up (or captured) its electron, leaving a fixed charge | — |
| **Compensation** | Donors and acceptors cancelling each other | — |
| **Mass action law** | $n \times p = n_i^2$ always, at equilibrium | — |

---

## 3. The two dopants

### Donors — group V makes N-type

Substitute a **phosphorus** atom (5 valence electrons) into a silicon lattice site. The site demands four bonds. Phosphorus supplies four — **and has one left over.**

```
        Si        Si        Si
         │         │         │
   Si ── Si ────── P ────── Si ── Si
         │         │╲
        Si        Si  ● ← the fifth electron: no bond to join,
                         only loosely held to the P nucleus
```

That fifth electron is not in a covalent bond. It is weakly bound to its parent phosphorus atom by simple electrostatic attraction, and it takes very little energy to free it entirely.

Once freed, it is a conduction electron. The phosphorus atom, having lost an electron, becomes a **fixed positive ion** — and critically, it is *fixed*: it is locked in the lattice and cannot move. **The charge moves; the ion does not.**

Silicon doped with donors is **N-type** (negative majority carriers).

### Acceptors — group III makes P-type

Substitute a **boron** atom (3 valence electrons). The site demands four bonds and boron can only supply three. **One bond position is left vacant.**

```
        Si        Si        Si
         │         │         │
   Si ── Si ────── B ────── Si ── Si
         │         │
        Si        Si   ○ ← a vacant bond position: a hole
```

A neighbouring valence electron can easily hop into that vacancy, completing boron's fourth bond. But now the *neighbour* has a vacancy — the hole has moved. Boron, having gained an electron, becomes a **fixed negative ion**.

Silicon doped with acceptors is **P-type** (positive majority carriers).

> [!NOTE]
> **Doped silicon is still electrically neutral overall.** Every mobile carrier is matched by a fixed ionised dopant of opposite charge. N-type silicon is not negatively charged; it has mobile electrons balanced by immobile positive ions.
>
> This matters enormously in [[how-computers-work/02-semiconductors/05-pn-junctions|module 10]]. When carriers move away from a region, the fixed ions they leave behind are *exposed*, and that uncovered charge creates an electric field. The whole PN junction depends on the ions being immobile.

---

## 4. Shallow levels — why this works at all

Here is the mechanism that makes doping effective, and it is a matter of one number.

**A donor's spare electron does not sit in the valence band.** It occupies a new allowed state *inside the band gap*, just below the conduction band edge. For phosphorus in silicon that state sits about **45 meV** below the edge.

```
    ─────────────────────────  conduction band edge
      ● ● ● ● ●  ← donor level, only 45 meV below         E_g = 1120 meV
                                                          kT  =  25.9 meV
    ░░░░░░░░░░░░░░░░░░░░░░░░░  (1120 meV of forbidden gap)

      ○ ○ ○ ○ ○  ← acceptor level, only 45 meV above
    ─────────────────────────  valence band edge
```

**Now compare the two energies an electron might need:**

| To create a carrier by... | Energy needed | Relative to $kT$ = 25.85 meV |
| :--- | ---: | ---: |
| Lifting a valence electron across the gap | 1120 meV | 43× |
| Ionising a phosphorus donor | 45 meV | 1.7× |

**Thermal energy is 1.7× short of ionising a donor, and 43× short of crossing the gap.** Because the probability falls exponentially, that difference is astronomically large. At room temperature **essentially every dopant atom is ionised** — better than 99% — while intrinsic generation remains at one atom in $10^{13}$.

**This is the whole trick.** You are not making silicon conduct by brute force; you are inserting energy levels so close to a band edge that room temperature alone is enough to activate all of them. The dopant does the work; heat just triggers it.

> [!NOTE]
> **Not every impurity is a useful dopant.** Gold, copper and iron in silicon create **deep levels** — states near the *middle* of the gap. Those do not donate carriers; they act as efficient **recombination centres**, catching electrons and holes and destroying them.
>
> Deep-level contaminants ruin carrier lifetime and are precisely what module 7's purification exists to eliminate. "Shallow good, deep bad" is the rule, and it explains why *which* impurity matters, not just how much.

---

## 5. Predict before reading on

Silicon is doped with $10^{16}$ phosphorus atoms/cm³. Intrinsic $n_i = 10^{10}$/cm³.

**(a)** Roughly how many conduction electrons per cm³? **(b)** What do you think happens to the *hole* concentration — does it stay at $10^{10}$, rise, or fall?

<details><summary>Check your answers</summary>

**(a)** About $10^{16}$/cm³. Essentially every donor is ionised, and $10^{16}$ utterly swamps the $10^{10}$ from thermal generation. **The doping sets the carrier concentration; the intrinsic contribution is a rounding error.**

**(b)** Holes **fall**, and they fall hard — to $10^4$/cm³, a factor of a million *below* the intrinsic value.

Most people guess "stay the same". The reason they fall is section 6, and it is the most surprising result in Part III.
</details>

---

## 6. The mass action law — doping suppresses minority carriers

At thermal equilibrium, for any doping level whatsoever:

$$n \times p = n_i^2$$

where $n$ is the electron concentration and $p$ the hole concentration. **The product is a constant fixed by temperature and band gap — not by doping.**

**Why it holds:** carriers are constantly generated in pairs and constantly recombining. Generation rate depends only on temperature and band gap. Recombination rate depends on how often an electron *meets* a hole, which is proportional to $n \times p$. At equilibrium the two rates balance, which pins the product.

Add donors and you flood the material with electrons. Those electrons now find holes far more easily, so recombination accelerates and the hole population is driven down until the product returns to $n_i^2$.

**Worked through, for $N_d = 10^{16}$:**

$$n \approx 10^{16} \qquad p = \frac{n_i^2}{n} = \frac{(10^{10})^2}{10^{16}} = \frac{10^{20}}{10^{16}} = 10^{4}\ \text{/cm}^3$$

| | Intrinsic | N-type at $10^{16}$ | Change |
| :--- | ---: | ---: | ---: |
| Electrons | $10^{10}$ | $10^{16}$ | ×$10^{6}$ |
| Holes | $10^{10}$ | $10^{4}$ | ×$10^{-6}$ |

**Doping is not merely additive — it is a trade.** You gain majority carriers by exactly the factor you lose minority carriers.

This symmetry is not a curiosity. **It is what makes a PN junction work.** In module 10 you will place N-type against P-type, and the junction's rectifying behaviour depends entirely on each side having almost none of the other side's carrier type. A material with plenty of both would not rectify at all.

---

## 7. What it buys — the numbers

Conductivity comes from both carrier types:

$$\sigma = q\,(n\,\mu_n + p\,\mu_p) \qquad\qquad \rho = \frac{1}{\sigma}$$

Running that for a range of doping levels:

| Doping (/cm³) | Type | Majority | Minority | Resistivity (Ω·cm) | ppm of lattice |
| ---: | :--- | ---: | ---: | ---: | ---: |
| — | intrinsic | $10^{10}$ | $10^{10}$ | $3.4 \times 10^{5}$ | 0 |
| $10^{14}$ | N | $10^{14}$ | $10^{6}$ | 46.2 | 0.002 |
| $10^{16}$ | N | $10^{16}$ | $10^{4}$ | 0.462 | 0.200 |
| $10^{18}$ | N | $10^{18}$ | $10^{2}$ | 0.005 | 20.0 |
| $10^{16}$ | P | $10^{16}$ | $10^{4}$ | 1.300 | 0.200 |
| $10^{18}$ | P | $10^{18}$ | $10^{2}$ | 0.013 | 20.0 |

**The headline: doping at $10^{16}$/cm³ — 0.2 parts per million — drops resistivity from $3.4 \times 10^5$ to 0.46 Ω·cm, a factor of about 740,000.**

**Note the N/P asymmetry.** At identical doping, P-type silicon has 2.8× the resistivity of N-type — exactly the electron/hole mobility ratio from module 8. Same carrier count, less mobile carriers, more resistance. This is the same fact that makes PMOS transistors wider in module 13, showing up here as a bulk material property.

### Compensation subtracts

If both dopant types are present, they **cancel**. Only the net difference matters:

$$n \approx N_d - N_a \quad (\text{if } N_d > N_a)$$

Add $10^{17}$ donors and $9 \times 10^{16}$ acceptors and you get material behaving as lightly doped N-type at $10^{16}$ — **not** heavily doped anything. The spare electrons simply fill the vacant bonds.

This is genuinely useful: it is how a P-type region is created inside an N-type wafer, by implanting enough acceptors to overwhelm the existing donors. It is also a hazard, since compensated material has more scattering centres than lightly doped material of the same net concentration, and therefore lower mobility than the table above suggests.

### How dopants get in

- **Melt doping** (module 7) — dissolved into the Czochralski melt for a uniform ingot.
- **Diffusion** — dopant gas at 900–1200 °C; atoms diffuse in from the surface. Simple, but spreads sideways as well as down, limiting how small features can be.
- **Ion implantation** — dopant ions accelerated to 10–500 keV and fired into the wafer. Precise dose and depth control, and it works through a patterned mask. It damages the lattice, so an **annealing** step follows to repair the crystal and move dopants onto proper lattice sites. This is the modern method for everything that needs precision.

---

## 8. Worked example — runnable

Save as `doping_lab.py` and run `python3 doping_lab.py`.

```python
Q = 1.602176634e-19        # electron charge, coulombs
N_I = 1.0e10               # silicon intrinsic carriers per cm^3 at 300 K
MU_N, MU_P = 1350.0, 480.0 # electron / hole mobility, cm^2/(V.s)
SI_ATOMS = 5.0e22          # silicon atoms per cm^3

def carriers(n_donors, n_acceptors):
    """Majority and minority carrier concentrations by charge neutrality
    plus the mass action law n*p = n_i^2. Returns (n_electrons, n_holes)."""
    net = n_donors - n_acceptors
    if net > 0:                                   # N-type
        n = (net + (net**2 + 4*N_I**2) ** 0.5) / 2
        return n, N_I**2 / n
    if net < 0:                                   # P-type
        p = (-net + (net**2 + 4*N_I**2) ** 0.5) / 2
        return N_I**2 / p, p
    return N_I, N_I                               # exactly compensated

def conductivity(n, p):
    """Siemens per cm."""
    return Q * (n * MU_N + p * MU_P)

def resistivity(n, p):
    return 1.0 / conductivity(n, p)

if __name__ == "__main__":
    n, p = carriers(0, 0)
    rho_intrinsic = resistivity(n, p)
    print(f"intrinsic silicon:  n = {n:.1e}, p = {p:.1e} /cm^3")
    print(f"  resistivity = {rho_intrinsic:.2e} ohm.cm")
    print()

    print(f"{'doping (/cm^3)':>16s} {'type':>6s} {'majority':>10s} {'minority':>10s}"
          f" {'ohm.cm':>10s} {'ppm':>8s}")
    for nd, na, label in [(1e14, 0, "N"), (1e16, 0, "N"), (1e18, 0, "N"),
                          (0, 1e16, "P"), (0, 1e18, "P")]:
        n, p = carriers(nd, na)
        rho = resistivity(n, p)
        dose = max(nd, na)
        maj, mino = (n, p) if label == "N" else (p, n)
        print(f"{dose:16.0e} {label:>6s} {maj:10.2e} {mino:10.2e}"
              f" {rho:10.3f} {dose/SI_ATOMS*1e6:8.3f}")

    # The headline: how much does a fraction of a ppm buy?
    n, p = carriers(1e16, 0)
    print()
    print(f"doping at 1e16/cm^3 is {1e16/SI_ATOMS*1e6:.3f} ppm of the lattice")
    print(f"  resistivity falls from {rho_intrinsic:.2e} to {resistivity(n,p):.3f} ohm.cm")
    print(f"  a factor of {rho_intrinsic/resistivity(n,p):.3e}")

    # Doping suppresses minority carriers as hard as it boosts majority ones
    print()
    print(f"  majority electrons rose from {N_I:.0e} to {n:.0e}  (x{n/N_I:.0e})")
    print(f"  minority holes FELL from {N_I:.0e} to {p:.0e}  (x{p/N_I:.0e})")

    # Compensation: adding the opposite dopant cancels, it does not add
    n, p = carriers(1e17, 9e16)
    print()
    print(f"compensation: 1e17 donors + 9e16 acceptors -> net 1e16")
    print(f"  n = {n:.2e}/cm^3, behaves like lightly doped N-type")

    assert carriers(1e16, 0)[0] > carriers(1e14, 0)[0]
    assert abs(carriers(1e16, 0)[0] * carriers(1e16, 0)[1] - N_I**2) / N_I**2 < 1e-6
    assert carriers(0, 1e16)[1] > carriers(0, 1e16)[0]
    print()
    print("doping_lab: passed")
```

Expected output:

```
intrinsic silicon:  n = 1.0e+10, p = 1.0e+10 /cm^3
  resistivity = 3.41e+05 ohm.cm

  doping (/cm^3)   type   majority   minority     ohm.cm      ppm
           1e+14      N   1.00e+14   1.00e+06     46.233    0.002
           1e+16      N   1.00e+16   1.00e+04      0.462    0.200
           1e+18      N   1.00e+18   1.00e+02      0.005   20.000
           1e+16      P   1.00e+16   1.00e+04      1.300    0.200
           1e+18      P   1.00e+18   1.00e+02      0.013   20.000

doping at 1e16/cm^3 is 0.200 ppm of the lattice
  resistivity falls from 3.41e+05 to 0.462 ohm.cm
  a factor of 7.377e+05

  majority electrons rose from 1e+10 to 1e+16  (x1e+06)
  minority holes FELL from 1e+10 to 1e+04  (x1e-06)

compensation: 1e17 donors + 9e16 acceptors -> net 1e16
  n = 1.00e+16/cm^3, behaves like lightly doped N-type

doping_lab: passed
```

---

## 9. Common pitfalls and traps

1. **Thinking N-type silicon is negatively charged.** It is neutral. Mobile electrons are exactly balanced by fixed positive donor ions.
2. **Forgetting that ionised dopants are immobile.** The carriers move; the ions stay. Module 10 depends entirely on this.
3. **Assuming minority carriers stay at $n_i$.** They fall by the same factor the majority carriers rise. This is the most commonly missed result in the module.
4. **Adding donor and acceptor concentrations.** They compensate — subtract. $10^{17}$ donors plus $10^{17}$ acceptors gives intrinsic-like material, not double doping.
5. **Believing any impurity dopes silicon.** Only shallow-level impurities from groups III and V. Deep-level metals destroy carrier lifetime instead.
6. **Doping without limit.** Above roughly $10^{20}$–$10^{21}$/cm³ you exceed solid solubility; dopants precipitate instead of dissolving, and the material becomes **degenerate**, behaving more like a metal than a semiconductor.

---

## 10. Check your understanding

1. **Why does doping at only 0.2 ppm change resistivity by a factor of 700,000, when 0.2 ppm of an impurity in copper would be undetectable?**
   <details><summary>Answer</summary>
   Because the comparison is against the <em>existing</em> carrier count, not against the atom count. Copper already has ~$10^{22}$ carriers/cm³, so adding $10^{16}$ is a change of one part in a million — invisible.<br>
   Intrinsic silicon has only $10^{10}$ carriers/cm³, so adding $10^{16}$ multiplies the carrier population by a <strong>million</strong>. Silicon's extreme scarcity of intrinsic carriers is exactly what makes it controllable. Its poverty is the feature.
   </details>

2. **A sample is doped with $2 \times 10^{16}$ donors and $2 \times 10^{16}$ acceptors. What are $n$ and $p$? Is it identical to undoped silicon?**
   <details><summary>Answer</summary>
   The dopants exactly compensate, so net doping is zero and $n = p = n_i = 10^{10}$/cm³. The <em>carrier concentrations</em> match intrinsic silicon.<br>
   But it is <strong>not</strong> identical material. It contains $4 \times 10^{16}$ ionised impurity atoms per cm³, all of which scatter carriers. Mobility is substantially lower than true intrinsic silicon, so its resistivity is <em>higher</em> despite identical carrier counts. Carrier concentration and mobility are independent, and compensation degrades the second.
   </details>

3. **Why must the ionised dopant ions be immobile for a PN junction to work?**
   <details><summary>Answer</summary>
   At a junction, mobile carriers diffuse across and recombine, leaving a region depleted of carriers. What remains is the <strong>fixed ionised dopants</strong> — positive donors on the N side, negative acceptors on the P side. That uncovered, immobile charge creates the built-in electric field that opposes further diffusion and produces the junction's rectifying behaviour.<br>
   If the ions could move, they would follow the field, neutralise the charge separation, and no built-in field could be sustained. There would be no junction. Module 10 builds this properly.
   </details>

4. **Why is a heavily doped region ($10^{19}$/cm³) used where a wire contacts silicon?**
   <details><summary>Answer</summary>
   Two reasons. Its very low resistivity (~0.005 Ω·cm) minimises series resistance. More importantly, a metal-to-lightly-doped-semiconductor contact tends to form a <strong>Schottky barrier</strong> — a rectifying junction where you wanted a plain wire.<br>
   Heavy doping makes the barrier so thin that carriers tunnel straight through, producing an <strong>ohmic contact</strong> that conducts equally in both directions. Every transistor's source and drain contacts rely on this.
   </details>

---

## 11. Practice — independent task

**Task:** You are specifying doping for the regions of a simple device.

- **(a)** A resistor region must have resistivity 1.0 Ω·cm using N-type silicon. What donor concentration is needed? Solve it by rearranging $\rho = 1/(q n \mu_n)$, then check with `carriers()` and `resistivity()`.
- **(b)** Repeat for P-type at the same 1.0 Ω·cm target. Explain the difference in required concentration.
- **(c)** For your answer to (a), compute the minority hole concentration and confirm $np = n_i^2$ holds.
- **(d)** The wafer starts as P-type at $10^{15}$/cm³. To create your region from (a), how many donors must be implanted, remembering they must first compensate the existing acceptors?
- **(e)** A contact region needs resistivity below 0.01 Ω·cm. What N-type doping achieves this, and what fraction of the lattice is that in ppm? Is it below the ~$10^{21}$/cm³ solubility limit?
- **(f)** Add a `doping_for_resistivity(target_rho, dopant_type)` function that inverts the calculation, and verify it reproduces your answers to (a), (b) and (e).

**Done when:** your inversion function agrees with your hand calculations to within a few percent, and you can explain why P-type needs ~2.8× more doping than N-type for the same resistivity.

<details><summary>Hint for (d), only if stuck</summary>
Compensation subtracts. To reach a <em>net</em> donor concentration of $N_{net}$ in material that already has $10^{15}$ acceptors, you must implant $N_d = N_{net} + 10^{15}$. Given typical answers to (a) are around $10^{16}$, the correction is about 10% — small but not negligible, and exactly the kind of thing that shifts a real process recipe.
</details>

---

## 12. Tradeoffs and limits

- **Mobility falls as doping rises.** Ionised dopants are themselves scattering centres, so heavily doped silicon has substantially lower mobility than the constant values used here. Real calculations use empirical mobility-versus-doping curves; this module's fixed $\mu$ overstates conductivity at high doping.
- **Complete ionisation is an approximation.** Excellent at room temperature; it fails at cryogenic temperatures, where dopants "freeze out" and carriers vanish. This is why some circuits behave oddly when cooled aggressively.
- **The mass action law requires equilibrium.** Under illumination, forward bias or any active drive, $np \neq n_i^2$ — and departures from it are exactly what makes devices *do* things. It is the baseline you measure deviations from, not a universal truth.
- **Doping alone still isn't a switch.** You now have material with a conductivity you chose at manufacturing time. You still cannot change it *while the circuit runs*. That requires a junction.

---

## Before moving on

- [ ] Explain how group V and group III atoms produce N-type and P-type silicon.
- [ ] Explain why 45 meV shallow levels ionise fully at room temperature while a 1120 meV gap does not.
- [ ] Apply $np = n_i^2$ and explain why doping suppresses minority carriers.
- [ ] Compute resistivity from doping, and explain the N/P asymmetry from mobility.
- [ ] Explain why compensation subtracts, and why compensated material still has degraded mobility.
- [ ] Explain why ionised dopants being immobile is essential for module 10.

**Recap:** Group V donors contribute a spare electron at a shallow level 45 meV below the conduction band; group III acceptors leave a vacant bond 45 meV above the valence band. Because these levels are close to the band edges relative to $kT$, dopants ionise essentially completely at room temperature while intrinsic generation stays negligible. Doping at 0.2 ppm changes resistivity by a factor of ~740,000, and by the mass action law it suppresses minority carriers by exactly the factor it multiplies majority ones. Ionised dopants are fixed in the lattice; only the carriers move.

**Next:** [[how-computers-work/02-semiconductors/05-pn-junctions|Module 10 — PN Junctions and Diodes]] puts N-type and P-type in contact. The result is the first device that behaves *asymmetrically* — and the last thing you need before building a transistor.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/02-semiconductors/01-atoms-and-electrons|Module 6]] — where groups III and V were predicted from valence counting
- [[how-computers-work/03-transistors/02-mosfet-physics|Module 12 — MOSFET Physics]] — where doped regions become source and drain
