# Module 6: Atoms and Electrons (Why Some Matter Conducts)

**[Beginner]** — Part III begins. Module 2 said copper's resistivity is $10^{-8}$ Ω·m and glass's is $10^{12}$ — twenty orders of magnitude apart. This module explains where that gap comes from, and why silicon sits in the middle.

## Before you start

- You know that current is charge in motion and that resistance is carriers scattering — [[how-computers-work/01-electricity/02-resistance-and-ohms-law|module 2]].
- You know what the digital abstraction needs from a switch: pull hard to the rails, switch sharply, leak little — [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]].
- Secondary-school chemistry is helpful but not assumed. Everything needed is defined here.

**After this lesson you will be able to:**

1. Describe an atom's structure and say which part participates in electrical conduction and which never does.
2. Work out an element's valence electron count from its atomic number.
3. Explain, in terms of valence electrons, why metals conduct, why insulators don't, and why group IV elements are the interesting case.
4. Predict which periodic-table groups will matter for doping in module 9, before being told.

**Study route:** sections 1–5 build the model. Section 6 is the one that sets up the entire rest of Part III.

---

## 1. Why this exists (real-world motivation)

You need a switch. [[how-computers-work/01-electricity/03-circuit-laws|Module 3]] showed that if you had a component whose resistance could be flipped between roughly zero and roughly infinite by a third terminal, you could build a logic gate out of it and the rest of computing follows.

So: what material can do that?

**Not a metal.** Copper's resistance is fixed by its structure. You can heat it or cool it slightly, but you cannot switch it off. A metal is always conducting.

**Not an insulator.** Glass never conducts, no matter what you do to it short of destroying it.

You need something whose conductivity is *controllable* — normally reluctant to conduct, but persuadable. That is a strange, specific requirement, and the fact that such materials exist at all is the reason electronic computing is possible.

Everything about whether a material conducts comes down to one question: **are there electrons free to move, and how much energy does it take to free one?** To answer that, you have to look at where electrons live.

---

## 2. Terminology

| Term | Plain-English definition | Example / analogy |
| :--- | :--- | :--- |
| **Nucleus** | The atom's dense centre: protons and neutrons | The sun in a solar system |
| **Atomic number** ($Z$) | Number of protons — this defines which element it is | Silicon is always $Z = 14$ |
| **Shell** | A group of electron states at a similar energy | A floor of a building |
| **Subshell** (s, p, d, f) | Divisions within a shell, each holding a fixed number | Rooms on that floor |
| **Valence electrons** | Electrons in the outermost occupied shell | The residents who can leave |
| **Core electrons** | Everything inner — tightly bound, never participate | Residents locked in the basement |
| **Covalent bond** | Two atoms sharing a pair of electrons | A handshake that binds |
| **Free electron** | One that has escaped its atom and can drift through the material | A commuter |
| **Ion** | An atom with unequal protons and electrons, so net charged | — |

---

## 3. The atom, and which part matters

An atom is a nucleus of **protons** (positive) and **neutrons** (neutral), surrounded by **electrons** (negative). A neutral atom has equal numbers of protons and electrons.

**Only the electrons matter for electricity, and only some of them.**

The nucleus is roughly 100,000 times smaller than the atom and enormously heavy — a proton is about 1,836 times an electron's mass. In a solid it is locked rigidly in the crystal and never goes anywhere. **Every electrical phenomenon in this course is electrons moving; the nuclei just sit there providing positive charge and something to bump into.**

> [!NOTE]
> **The solar-system picture is wrong, but useful.** Electrons do not orbit like planets. Quantum mechanics says an electron occupies an *orbital* — a probability cloud describing where it is likely to be found — and it has no definite trajectory at all.
>
> Keep the shell picture for bookkeeping (it gets valence counts right, which is all we need), but do not trust it for mechanism. When it stops working, in [[how-computers-work/02-semiconductors/03-energy-bands|module 8]], we replace it with energy bands rather than patching it.

---

## 4. Shells, and why they fill in that order

Electrons occupy discrete energy levels. **They cannot sit between levels** — this quantisation is the single most important fact in the whole of Part III, and it is what ultimately produces the band gap in module 8.

Levels are organised into shells (numbered $n = 1, 2, 3, \dots$) and subshells within them:

| Subshell | Electrons it holds |
| :--- | :--- |
| s | 2 |
| p | 6 |
| d | 10 |
| f | 14 |

Electrons fill the lowest-energy states first. The order is not simply shell-by-shell — 4s fills before 3d, because energy levels overlap between shells:

```
   1s → 2s → 2p → 3s → 3p → 4s → 3d → 4p → 5s → 4d → 5p → ...
```

**Silicon, $Z = 14$**, fills as: 1s² 2s² 2p⁶ 3s² 3p²

```
        Shell 1: ●●                        2 electrons  (full)
        Shell 2: ●●●●●●●●                  8 electrons  (full)
        Shell 3: ●●●● ○○○○                 4 electrons  ← VALENCE
                 └──┴─ four empty slots

        Si:  14 protons, 14 electrons, 4 valence electrons
```

Count the electrons in the outermost shell that has any ($n = 3$): 3s² gives 2, 3p² gives 2, total **4 valence electrons**.

### Only valence electrons matter

**Core electrons are irrelevant to electricity.** They are close to the nucleus, tightly bound, and freeing one takes vastly more energy than is available at room temperature or from any voltage you would apply.

**Valence electrons are the outermost, most weakly held, and the only ones that participate** in chemical bonding or electrical conduction. From here on, "how many valence electrons" is the only question we ask about an element.

---

## 5. The three cases

**Atoms are most stable with a full outer shell** — eight valence electrons for the elements that concern us (the octet rule). Every element's behaviour is a strategy for reaching that state, and the strategy determines whether it conducts.

### Metals — 1 to 3 valence electrons

Sodium has 1, magnesium 2, aluminium 3. Far from eight, and the cheapest route to a full outer shell is to **give the outer electrons away entirely**, exposing the full shell beneath.

In a solid, every atom does this at once. The donated electrons are not owned by anyone; they form a **sea of free electrons** drifting through a lattice of positive ions.

```
   METAL — the electron sea

     ⊕   ⊕   ⊕   ⊕      ⊕ = positive ion core (nucleus + core electrons)
       e⁻  e⁻   e⁻      e⁻ = free electrons, belonging to no single atom
     ⊕   ⊕   ⊕   ⊕
      e⁻   e⁻  e⁻       Apply a field → the sea drifts → current
     ⊕   ⊕   ⊕   ⊕
```

**Metals conduct because free carriers are already present**, in enormous numbers — recall the $8.5 \times 10^{28}$ per m³ used for copper in module 1. No energy is needed to create a carrier; they simply exist. This is also why a metal's conductivity **falls** as it heats: the carrier count is already fixed, so extra heat only adds lattice vibration and more scattering.

### Insulators — 7 to 8 valence electrons

Elements near a full shell either grab an extra electron or share tightly. Either way, **every electron ends up locked in a bond**, with no free carriers and an enormous energy cost to break one loose.

```
   INSULATOR — every electron committed

     ⊕═══⊕═══⊕═══⊕       ═══ = electrons locked in bonds
     ║   ║   ║   ║
     ⊕═══⊕═══⊕═══⊕       Apply a field → nothing moves → no current
```

### Group IV — exactly half full

Now the interesting case. **Carbon, silicon and germanium have exactly 4 valence electrons** — precisely half of eight.

They have no cheap strategy. Giving away four electrons costs too much; grabbing four costs too much. So they do the only remaining thing: **share**. Each atom forms four covalent bonds with four neighbours, and each shared pair counts towards both atoms' octets. Every atom reaches eight, and every electron is committed to a bond.

```
   SILICON — every atom shares with four neighbours

          Si          Each line is a shared electron pair.
           │          Every atom "sees" 8 valence electrons.
     Si ── Si ── Si   Every electron is in a bond.
           │
          Si          At absolute zero: a perfect insulator.
```

**At absolute zero, pure silicon is an insulator** — no free carriers at all, exactly like glass.

**But the bonds are weak.** Breaking one takes 1.12 electron-volts in silicon, compared with about 9 eV for the bonds in silicon dioxide (glass). That difference is everything. At room temperature, thermal energy is enough to shake a small number of electrons out of their bonds — not many, but not zero either.

**So silicon conducts slightly.** Not like a metal, not like glass. Its conductivity depends on temperature, on light, and — critically — on what impurities you deliberately add. **It is controllable**, and that is exactly the property the switch required.

> [!NOTE]
> **Notice what just happened.** We asked for a material whose conductivity could be manipulated, and the answer fell out of one number: how many valence electrons the element has. Four — exactly half a shell — is the sweet spot, because it forces a bonding arrangement that is complete but weakly held.
>
> This is why the semiconductor industry is built on column IV of the periodic table, and it is not a coincidence or a historical accident.

---

## 6. Predict before reading on

You will shortly want to add impurities to silicon to control its conductivity — either to add a spare electron, or to create a missing one.

**Looking at valence electron counts alone: which periodic-table groups would you choose, and why?**

<details><summary>Check your answer</summary>

**Group V (5 valence electrons) — phosphorus, arsenic, antimony.** Substitute one into the silicon lattice. Four of its electrons form the four bonds the site requires; **the fifth has no bond to join** and is only loosely held to its parent atom. It is easily freed, giving a spare negative carrier.

**Group III (3 valence electrons) — boron, aluminium, gallium.** Substitute one in and it can only form three of the four required bonds. **One bond position is left vacant** — a "hole" that a neighbouring electron can hop into, moving the vacancy along.

Group V donates electrons; group III accepts them. They are called **donors** and **acceptors**, they produce **N-type** and **P-type** silicon, and putting the two kinds next to each other builds every device in this course.

You have just derived the basis of doping from valence counting alone. [[how-computers-work/02-semiconductors/04-doping|Module 9]] works out the details.
</details>

---

## 7. Worked example — runnable

This computes electron configurations from atomic number and classifies elements by valence count.

Save as `atoms_lab.py` and run `python3 atoms_lab.py`. Standard library only.

```python
# Subshells in the order they fill (the Aufbau order), with their capacities.
FILL_ORDER = [
    ("1s", 1, 2), ("2s", 2, 2), ("2p", 2, 6), ("3s", 3, 2), ("3p", 3, 6),
    ("4s", 4, 2), ("3d", 3, 10), ("4p", 4, 6), ("5s", 5, 2), ("4d", 4, 10),
    ("5p", 5, 6),
]

def configuration(z):
    """Fill subshells in energy order. Returns [(label, principal_n, count)]."""
    remaining, config = z, []
    for label, n, capacity in FILL_ORDER:
        if remaining <= 0:
            break
        placed = min(remaining, capacity)
        config.append((label, n, placed))
        remaining -= placed
    if remaining > 0:
        raise ValueError(f"Z={z} is beyond this table")
    return config

def valence_electrons(z):
    """Electrons in the highest occupied principal shell."""
    config = configuration(z)
    outermost = max(n for _, n, count in config if count > 0)
    return sum(count for _, n, count in config if n == outermost)

def classify(valence):
    """Rough electrical class from valence count alone."""
    if valence <= 3:
        return "metal (donates electrons -> free carriers exist already)"
    if valence == 4:
        return "SEMICONDUCTOR (shares four bonds -> controllable)"
    return "insulator/non-metal (holds electrons tightly)"

if __name__ == "__main__":
    elements = [
        ("B  boron",       5), ("C  carbon",    6), ("Al aluminium", 13),
        ("Si silicon",    14), ("P  phosphorus", 15), ("S  sulfur",   16),
        ("Ga gallium",    31), ("Ge germanium", 32), ("As arsenic",  33),
    ]
    for name, z in elements:
        v = valence_electrons(z)
        print(f"{name:15s} Z={z:2d}  valence={v}  {classify(v)}")

    # The three groups that build every device in this course
    assert valence_electrons(14) == 4    # Si  — the lattice
    assert valence_electrons(32) == 4    # Ge  — the other group IV
    assert valence_electrons(15) == 5    # P   — donor, makes N-type
    assert valence_electrons(33) == 5    # As  — donor
    assert valence_electrons(5)  == 3    # B   — acceptor, makes P-type
    assert valence_electrons(31) == 3    # Ga  — acceptor

    print()
    print("silicon configuration:", " ".join(
        f"{label}{count}" for label, _, count in configuration(14) if count))
    print("phosphorus has one more:", " ".join(
        f"{label}{count}" for label, _, count in configuration(15) if count))
    print("boron has one fewer bond to offer:", " ".join(
        f"{label}{count}" for label, _, count in configuration(5) if count))

    print("atoms_lab: passed")
```

Expected output:

```
B  boron        Z= 5  valence=3  metal (donates electrons -> free carriers exist already)
C  carbon       Z= 6  valence=4  SEMICONDUCTOR (shares four bonds -> controllable)
Al aluminium    Z=13  valence=3  metal (donates electrons -> free carriers exist already)
Si silicon      Z=14  valence=4  SEMICONDUCTOR (shares four bonds -> controllable)
P  phosphorus   Z=15  valence=5  insulator/non-metal (holds electrons tightly)
S  sulfur       Z=16  valence=6  insulator/non-metal (holds electrons tightly)
Ga gallium      Z=31  valence=3  metal (donates electrons -> free carriers exist already)
Ge germanium    Z=32  valence=4  SEMICONDUCTOR (shares four bonds -> controllable)
As arsenic      Z=33  valence=5  insulator/non-metal (holds electrons tightly)

silicon configuration: 1s2 2s2 2p6 3s2 3p2
phosphorus has one more: 1s2 2s2 2p6 3s2 3p3
boron has one fewer bond to offer: 1s2 2s2 2p1
atoms_lab: passed
```

### What the model gets wrong, and why that is instructive

Look at the last two output lines and at boron's classification. **The model is wrong in three places, and each error teaches something:**

- **Boron is called a "metal".** It is actually a metalloid, and carbon at valence 4 is a semiconductor only in its diamond form (graphite conducts). Valence count alone is too crude a classifier — it gets the *trend* right and the boundaries wrong. Module 8 replaces it with the band gap, a number that classifies correctly.
- **Phosphorus and arsenic are called "insulators".** As pure elements that is roughly right, but they are used here as *dopants inside silicon*, where what matters is the one spare electron, not their bulk behaviour.
- **The classifier has no notion of context.** Phosphorus is not being used as a bulk material here; it is being used as a single substituted atom inside a silicon lattice, where only its spare fifth electron matters. A function that classifies elements in isolation cannot express that.

**A model that is wrong in known, bounded ways is still useful.** Valence counting correctly identifies group IV as special and correctly predicts groups III and V as the dopants — which is precisely what Part III needs it for. Knowing where a model fails is what lets you trust it where it holds.

---

## 8. Common pitfalls and traps

1. **Thinking electrons orbit like planets.** They occupy probability clouds with no trajectory. The shell picture is a bookkeeping device, and it will be replaced in module 8.
2. **Counting all electrons instead of valence electrons.** Silicon has 14 electrons and 4 valence electrons. Only the 4 ever matter.
3. **Assuming more electrons means better conduction.** Gold has 79 electrons and copper 29; copper is the better conductor. **Availability, not quantity**, is what counts.
4. **Believing pure silicon is a good conductor.** It is a poor one — closer to an insulator than a metal. Its usefulness is that its conductivity can be *changed*, not that it is high.
5. **Forgetting that shells do not fill in strict numeric order.** 4s fills before 3d. This is why the transition metals exist and why the naive $2n^2$ rule mispredicts them.

---

## 9. Check your understanding

1. **Germanium ($Z = 32$) was used for the first transistors before silicon took over. From its position in the periodic table, why would it work at all?**
   <details><summary>Answer</summary>
   Germanium is directly below silicon in group IV, so it also has <strong>4 valence electrons</strong> and forms the same four-covalent-bond lattice. The same physics applies.<br>
   Silicon displaced it because germanium's bonds are weaker (0.66 eV versus 1.12 eV), so it generates far more thermal carriers and leaks badly as it warms — and, decisively, because silicon's native oxide SiO₂ is an excellent, easily grown insulator. Germanium's oxide is water-soluble. The <em>oxide</em>, not the semiconductor, is what made silicon win.
   </details>

2. **Why does a metal's resistance rise with temperature while a semiconductor's falls?**
   <details><summary>Answer</summary>
   In a metal the carrier count is fixed — the electron sea already exists. Heating only increases lattice vibration and therefore scattering, so resistance <strong>rises</strong>.<br>
   In a semiconductor, heating <em>creates</em> carriers by shaking electrons out of bonds. That effect overwhelms the extra scattering, so resistance <strong>falls</strong>. This opposite sign is a reliable experimental test of which kind of material you have.
   </details>

3. **Diamond and silicon are both group IV with identical four-bond lattices. Why is diamond an excellent insulator?**
   <details><summary>Answer</summary>
   Same structure, very different bond strength. Carbon atoms are much smaller, so bonds are shorter and far stronger — about <strong>5.5 eV</strong> to break, against silicon's 1.12 eV. Room-temperature thermal energy is nowhere near enough, so essentially no carriers are generated.<br>
   The structure sets the <em>type</em> of behaviour; the bond energy sets <em>where on the scale</em> it lands. Module 8 makes this precise as the band gap.
   </details>

4. **Why can't you make a switchable device out of copper by adding impurities?**
   <details><summary>Answer</summary>
   Copper already has roughly $10^{29}$ free carriers per cubic metre. Doping might add or remove $10^{23}$ — a change of about one part in a million, which is undetectable. There is no "off" state to switch to.<br>
   Silicon's intrinsic carrier concentration is about $10^{16}$ per m³, so adding $10^{22}$ dopant atoms changes the carrier count by a <strong>factor of a million</strong>. Silicon is controllable precisely <em>because</em> it starts with so few carriers. Its poverty is the feature.
   </details>

---

## 10. Practice — independent task

**Task, part 1 — fix the classifier.** As shown above, `classify()` calls boron a metal and arsenic an insulator. Both are misleading in the context that matters here.

- **(a)** Write a second function `dopant_role(z)` that returns `"donor (N-type)"` for group V elements, `"acceptor (P-type)"` for group III, `"lattice"` for group IV, and `"not used"` otherwise — deciding purely from the valence count.
- **(b)** Print both `classify()` and `dopant_role()` for every element in the list. Explain in one sentence why two different answers for the same element are not a contradiction.

**Task, part 2 — find where the shell model genuinely breaks.**

- **(c)** Predict what `valence_electrons(29)` returns for copper, using the `FILL_ORDER` table as written. Then look up copper's actual electron configuration.
- **(d)** The function's answer and reality disagree. Explain what the real configuration is and why nature prefers it. What does this tell you about the reliability of strict Aufbau filling?
- **(e)** Add an `ANOMALIES` dictionary mapping atomic numbers to known real configurations, and have `valence_electrons()` consult it before falling back to the table. Add copper ($Z=29$), chromium ($Z=24$), silver ($Z=47$) and gold ($Z=79$). Note that `FILL_ORDER` will need extending for gold.

**Task, part 3 — extend the model.**

- **(f)** Add indium ($Z = 49$) and antimony ($Z = 51$) to the element list. Predict their valence counts before running, then check. Which is a donor and which an acceptor?
- **(g)** Gallium arsenide (GaAs) is a real semiconductor made from group III gallium and group V arsenic. Given Ga has 3 valence electrons and As has 5, explain how a 50/50 compound still gives every atom four bonds. Why might this be useful?

**Done when:** `dopant_role()` correctly labels all nine elements, your anomalies table makes copper return 1 valence electron, and you can say in one sentence why III–V compounds average out to group IV behaviour.

<details><summary>Hint for (d), only if stuck</summary>
Strict filling predicts copper ends 4s² 3d⁹. The real configuration is <strong>3d¹⁰ 4s¹</strong> — an electron is promoted out of 4s to complete the d subshell, because a filled d shell is more stable than the small energy cost of the promotion. The 4s and 3d levels are so close in energy that subshell-completion effects can outweigh the nominal ordering.<br><br>
This is why copper has <em>one</em> valence electron, which is exactly what makes it such a good conductor — and why the naive table gets it wrong.
</details>

---

## 11. Tradeoffs and limits of this model

- **Shell counting is a bookkeeping model, not physics.** It predicts valence correctly for main-group elements and fails for transition metals, where partly filled d subshells make the picture ambiguous. Copper is the classic case: naive filling predicts 2 valence electrons, but the real configuration is 3d¹⁰4s¹, giving 1.
- **The octet rule has plenty of exceptions.** Hydrogen and helium want 2, not 8; boron is stable with 6; phosphorus and sulfur can exceed 8. It is a useful heuristic for group IV, which is all we need.
- **"Metal, insulator, semiconductor" is a spectrum, not three boxes.** Metalloids sit at the boundary, and the same element can behave differently in different crystal forms — carbon as diamond versus graphite is the clearest example.
- **Nothing here explains *why* energy levels are quantised.** That requires quantum mechanics and is well outside this course. We take quantisation as given and build on it.

---

## Before moving on

- [ ] Say which part of an atom participates in conduction and which never does.
- [ ] Compute valence electrons for any main-group element from its atomic number.
- [ ] Explain the three cases — metal, insulator, group IV — in terms of the strategy for filling the outer shell.
- [ ] Explain why pure silicon at absolute zero is an insulator, and what changes at room temperature.
- [ ] Predict groups III and V as the dopants, from valence counting alone.

**Recap:** Only valence electrons matter electrically. Metals have 1–3 and shed them into a free electron sea, so they always conduct. Elements near a full shell lock every electron into a bond and never conduct. Group IV has exactly 4, forcing a four-covalent-bond lattice that is complete but weakly held — an insulator at absolute zero, slightly conducting at room temperature, and controllable by impurities. Silicon's poverty of intrinsic carriers is exactly what makes it switchable.

**Next:** [[how-computers-work/02-semiconductors/02-silicon-and-crystal|Module 7 — Silicon and the Crystal Lattice]] takes the bonding arrangement sketched here and turns it into a real material: how the lattice is structured, how silicon is purified to the extraordinary standards required, and how a wafer is made.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/02-semiconductors/03-energy-bands|Module 8 — Energy Bands]] — replaces valence counting with a number that classifies correctly
- [[how-computers-work/02-semiconductors/04-doping|Module 9 — Doping]] — where groups III and V do their work
- [[how-computers-work/01-electricity/02-resistance-and-ohms-law|Module 2]] — the resistivity gap this module explains
