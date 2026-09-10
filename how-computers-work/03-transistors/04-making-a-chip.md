# Module 14: Making a Chip (How Transistors Are Actually Built)

**[Intermediate]** — Part IV ends with the question the previous three modules kept deferring: a MOSFET is a beautiful idea, but **how do you physically build a billion of them, each a few atoms across, without touching any of them individually?**

## Before you start

- You know what a MOSFET is structurally — gate, oxide, source, drain, body — [[how-computers-work/03-transistors/02-mosfet-physics|module 12]].
- You know how CMOS pairs NMOS and PMOS — [[how-computers-work/03-transistors/03-cmos|module 13]].
- You know how a wafer is grown and why it must be a single crystal — [[how-computers-work/02-semiconductors/02-silicon-and-crystal|module 7]].
- You know doping is done by ion implantation through a mask — [[how-computers-work/02-semiconductors/04-doping|module 9]].

**After this lesson you will be able to:**

1. Describe the photolithography cycle and explain why chips are built in layers.
2. Walk through the construction of a single MOSFET, step by step.
3. Explain how gates become *wires* — the metal interconnect stack.
4. Explain why light of 193 nm can print 20 nm features, and what that costs.
5. Compute die yield and explain why large chips are disproportionately expensive.

**Study route:** section 3 is the core loop — everything else is that loop repeated. Section 5 (interconnect) answers "how are gates made from wires". Section 7 is the economics that shapes the whole industry.

---

## 1. Why this exists (real-world motivation)

Module 13 finished the logical story: two complementary transistors make an inverter, and from there any gate. Module 7 delivered a polished single-crystal wafer.

**Between those two facts is an enormous unanswered question.** A modern processor has tens of billions of transistors, each with features a few nanometres across — smaller than a virus, smaller than the wavelength of visible light. **Nobody places them.** No tool touches an individual transistor. There is no assembly line where transistors are set down one at a time; at a billion per second it would still take decades per chip.

**They are all made at once, by printing.**

The entire semiconductor industry rests on one idea: **you cannot build things that small individually, but you can *photograph* a pattern onto a surface, and a photograph costs the same whether it contains ten shapes or ten billion.**

That single economic fact — patterning is parallel and its cost is independent of complexity — is why transistors became essentially free, and therefore why computing became ubiquitous.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Photolithography** | Printing a pattern using light and a light-sensitive coating |
| **Photoresist** | A polymer whose solubility changes where light hits it |
| **Mask / reticle** | The quartz-and-chrome "negative" carrying one layer's pattern |
| **Stepper / scanner** | The machine that projects the mask onto the wafer, repeatedly |
| **Etching** | Chemically removing material not protected by resist |
| **Deposition** | Adding a thin film of material across the wafer |
| **Ion implantation** | Firing dopant ions into exposed silicon (module 9) |
| **Planarisation (CMP)** | Polishing the surface flat before the next layer |
| **Interconnect** | The metal wiring layers above the transistors |
| **Via** | A vertical connection between two metal layers |
| **Numerical aperture (NA)** | How steeply a lens can gather light — bigger means finer detail |
| **Multi-patterning** | Using several exposures to print finer than one can manage |
| **Die** | One chip on the wafer |
| **Yield** | Fraction of dies that work |
| **Defect density** | Fatal defects per cm² of silicon |

---

## 3. The core loop: pattern, then modify

Everything in chip fabrication is one cycle, repeated. **Learn the cycle and you have learned the process** — a modern chip is this loop run 60 to 75 times.

```
   1. DEPOSIT       lay down a thin film across the whole wafer
        ↓             (oxide, polysilicon, metal, nitride...)
   2. COAT          spin on liquid photoresist, bake it
        ↓
   3. EXPOSE        shine UV through the mask; the pattern
        ↓             lands on the resist, usually shrunk 4x
   4. DEVELOP       wash away the exposed (or unexposed) resist,
        ↓             leaving a stencil of hardened polymer
   5. ETCH/IMPLANT  attack the surface where resist is absent --
        ↓             remove material, or fire dopants in
   6. STRIP         remove the remaining resist
        ↓
   7. PLANARISE     polish the surface flat (CMP)
        ↓
       repeat for the next layer
```

**Two things about step 3 deserve emphasis.**

First, **the whole wafer is patterned in parallel** — every transistor on the die is defined by the same flash of light. A die with a billion transistors takes no longer to expose than one with a thousand.

Second, **the mask is not the same size as the chip.** It carries the pattern at roughly 4× scale, and the projection optics *shrink* it onto the wafer. This is why mask defects are more tolerable than they sound, and why the machine is called a **stepper**: it exposes one die, steps the wafer along, and exposes the next, tiling the wafer with copies.

---

## 4. Building one MOSFET, step by step

Here is a simplified but honest sequence for a single NMOS transistor. Each numbered step is one pass around the loop above.

```
  START: p-type silicon wafer (module 7)

  ┌─────────────────────────────────┐
  │        p-type substrate         │
  └─────────────────────────────────┘

  1. GROW FIELD OXIDE and pattern it, leaving a bare "active area"
     where the transistor will live. Everything else is insulated.

  ┌───┬─────────────────────────┬───┐
  │oxi│     active area         │oxi│
  ├───┴─────────────────────────┴───┤
  │        p-type substrate         │
  └─────────────────────────────────┘

  2. GROW GATE OXIDE -- a very thin, very pure SiO2 layer, thermally
     grown by heating the wafer in oxygen. ~1-2 nm (module 11).
     This is the "O" in MOS, and silicon's native oxide is why
     silicon won over germanium (module 8).

  3. DEPOSIT POLYSILICON and pattern it into the gate stripe.

  ┌───┬─────┬───────┬─────┬───┐
  │oxi│     │ POLY  │     │oxi│   <- the gate
  │   │     ├───────┤     │   │
  │   │░░░░░░░░░░░░░░░░░░░│   │   <- gate oxide
  ├───┴─────────────────────┴───┤
  │        p-type substrate     │
  └─────────────────────────────┘

  4. IMPLANT SOURCE AND DRAIN -- fire n-type dopants (module 9).
     THE GATE ITSELF BLOCKS THE IMPLANT in the middle. This is
     "self-alignment": the channel is defined by the gate, not by
     a separate mask, so no misalignment is possible.

  ┌───┬─────┬───────┬─────┬───┐
  │oxi│ n+  │ POLY  │ n+  │oxi│
  │   │     ├───────┤     │   │
  ├───┴─────────────────────┴───┤
  │        p-type substrate     │
  └─────────────────────────────┘
     source            drain

  5. ANNEAL to repair implant damage and activate the dopants.
  6. DEPOSIT INSULATOR, etch CONTACT HOLES down to source, drain, gate.
  7. DEPOSIT METAL, pattern it into wires.
```

> [!NOTE]
> **Step 4 is the most elegant idea in the whole process.**
>
> The channel must sit exactly between source and drain, with no overlap and no gap. Overlap adds parasitic capacitance; a gap leaves a region the gate cannot control, and the transistor fails.
>
> Aligning two separate masks to a few nanometres is impossible. **So the process does not try.** The gate is patterned first, and then it *physically blocks* the implant from reaching the region beneath it. The channel is defined by the gate's own shadow.
>
> **The self-aligned gate (around 1969) is what made MOS scaling practical.** Rather than demanding better alignment, it made alignment irrelevant — replacing a precision requirement with a geometric guarantee. That pattern of thinking is worth stealing for other engineering problems.

---

## 5. How gates become wires — the interconnect stack

This answers a question the course has quietly dodged: schematics show gates connected by lines, but **what is a wire on a chip?**

Transistors occupy only the bottom surface of the die. **Everything above them is wiring** — 10 to 15 stacked layers of metal, separated by insulator, connected vertically by **vias**.

```
        ┌──────────────────────────────────────┐
        │  M10-M15  thick, wide: POWER + CLOCK │  global
        ├──────────────────────────────────────┤
        │  M5-M9    medium: long-distance      │  intermediate
        ├──────────────────────────────────────┤
        │  M2-M4    thin: block-level wiring   │
        ├──────────────────────────────────────┤
        │  M1       finest: inside standard    │  local
        │           cells, gate to gate        │
        ├──────────────────────────────────────┤
        │  ▄▄  ▄▄  ▄▄  transistors  ▄▄  ▄▄     │  device layer
        └──────────────────────────────────────┘
             ▲ vias connect layer to layer ▲
```

**The layers are deliberately not identical.** Lower layers are thin and narrow for density; upper layers are thick and wide because resistance matters more than density when a wire crosses the whole chip, and because power distribution needs low resistance to avoid the supply droop that would break [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]]'s noise margins.

**A "wire" on a chip is a copper trench**, etched into insulator and filled with copper (the damascene process). It has real resistance and real capacitance to its neighbours — which is exactly the RC that [[how-computers-work/01-electricity/04-signals-and-time|module 4]] said sets propagation delay.

> [!NOTE]
> **Wires stopped being free, and this changed processor design.**
>
> As transistors shrank, wires shrank too — but a thinner wire has *higher* resistance and, packed closer to its neighbours, similar capacitance. So while gates got faster with every process generation, **wires got relatively slower.**
>
> In modern chips, crossing the die can take longer than several gate delays. This is a major reason architectures became multicore and locality-obsessed: **it is now cheaper to compute a value again nearby than to fetch it from far away.** The memory hierarchy of [[computer-architecture/08-the-memory-hierarchy|computer-architecture/memory hierarchy]] is partly a response to wire delay.

### Standard cells and place-and-route

Designers do not draw individual transistors. They use a **standard cell library**: pre-designed, pre-verified layouts for NAND, NOR, inverters, flip-flops, all built to a **fixed height** so they tile into rows like text on a page.

```
   ┌────────────────────────────────────────┐
   │ VDD rail ══════════════════════════════│
   │  ┌──────┐ ┌────┐ ┌────────┐ ┌──────┐   │  row of cells,
   │  │ NAND │ │INV │ │  DFF   │ │ NOR  │   │  all the same height
   │  └──────┘ └────┘ └────────┘ └──────┘   │
   │ GND rail ══════════════════════════════│
   └────────────────────────────────────────┘
```

Automated tools then **place** cells and **route** wires between them. This is where [[how-computers-work/04-logic/01-gates-from-transistors|module 15]]'s claim becomes concrete: a synthesis tool prefers NAND because the NAND cell is smaller, so more logic fits per row.

**This is the practical answer to "how are gates made from wires":** the gate is a standard cell of patterned silicon and polysilicon; the wires are copper trenches on the metal layers above; and software decides where each cell sits and which trenches connect them.

---

## 6. Printing smaller than your light

Here is the part that sounds impossible.

Optical resolution is limited by the **Rayleigh criterion**:

$$\text{CD} = k_1 \frac{\lambda}{\text{NA}}$$

where $\lambda$ is wavelength, NA is numerical aperture, and $k_1$ is a process factor (~0.25–0.4, with a hard physical floor at 0.25).

| Light source | $\lambda$ | NA | Half-pitch |
| :--- | ---: | ---: | ---: |
| i-line mercury lamp | 365 nm | 0.60 | 182.5 nm |
| KrF excimer | 248 nm | 0.70 | 106.3 nm |
| ArF excimer | 193 nm | 0.93 | 62.3 nm |
| **ArF immersion** | 193 nm | 1.35 | **42.9 nm** |
| EUV | 13.5 nm | 0.33 | 12.3 nm |
| High-NA EUV | 13.5 nm | 0.55 | 7.4 nm |

**Note the immersion row.** NA above 1.0 is impossible in air. The trick is to fill the gap between lens and wafer with **purified water** ($n = 1.44$), which raises the achievable NA. A production machine printing billion-transistor chips works through a puddle.

### The 193 nm plateau, and multi-patterning

**ArF immersion stalled at ~43 nm, and stayed there from 2007 to about 2019.** EUV was promised for years and repeatedly delayed — 13.5 nm light is absorbed by *everything*, including air and glass, so it needs a vacuum, mirrors instead of lenses, and a source that vaporises tin droplets with a laser 50,000 times a second.

Meanwhile the industry kept shrinking, using **multi-patterning**: print half the lines, then print the other half offset between them.

| Target pitch | Exposures needed |
| ---: | ---: |
| 40 nm | 2 |
| 20 nm | 3 |
| 10 nm | 5 |

**Each extra exposure means another mask, another pass through the scanner, and another chance to misalign.** Cost and cycle time rise steeply — which is exactly why EUV was worth tens of billions to develop.

> [!NOTE]
> **Node names are marketing, not measurements.** A "5 nm" process has no 5 nm feature. Since roughly the 22 nm node, the number is a label indicating "the generation that would have followed, had classical scaling continued". Actual gate lengths at "5 nm" are around 16–20 nm.
>
> Compare processes by transistor density (millions per mm²), not by node name.

---

## 7. Yield — why big chips cost so much

Wafers have defects: a dust particle, a crystal flaw, a mis-etched line. Defects land at random, so **a bigger die is more likely to catch one.**

The **Poisson yield model**:

$$Y = e^{-A D}$$

where $A$ is die area and $D$ is defect density. With $D = 0.1/\text{cm}^2$ on a 300 mm wafer at \$15,000:

| Die area | Gross dies | Yield | Good dies | \$/good die |
| ---: | ---: | ---: | ---: | ---: |
| 0.5 cm² | 1319 | 95.1% | 1255 | \$11.96 |
| 1.0 cm² | 640 | 90.5% | 579 | \$25.90 |
| 2.0 cm² | 306 | 81.9% | 251 | \$59.87 |
| 4.0 cm² | 143 | 67.0% | 96 | \$156.49 |
| 6.0 cm² | 90 | 54.9% | 49 | \$303.69 |
| 8.0 cm² | 64 | 44.9% | 29 | \$521.61 |

**Doubling die area from 4 to 8 cm² multiplies cost per working die by 3.3×** — because you get fewer dies *and* a smaller fraction of them work. **Cost grows faster than area**, which is the single most important economic fact in chip design.

### Why chiplets exist

One 8 cm² die costs \$522. Eight 1 cm² dies cost \$207 total — **2.5× cheaper in silicon for the same area.**

This is why AMD, Intel and Apple build large processors from **chiplets**: several small, high-yielding dies packaged together rather than one huge die. The cost is packaging complexity and inter-die communication, and the win is yield.

It is also why defective dies are not thrown away: a chip with one bad core is sold as a lower-core-count part — **binning**, which is why product lines have so many variants.

---

## 8. Predict before reading on

A mask set for a 3 nm process costs about \$30 million, paid once per design regardless of volume.

**What does that imply about who can afford a custom chip, and what the alternative is?**

<details><summary>Check your answer</summary>

Amortised over volume, \$30 M is \$30 per chip at a million units, and 3 cents at a billion. **Only very high-volume products can justify a leading-edge custom chip** — which is why the list of companies designing 3 nm silicon is short.

**The alternatives:**

1. **Use an older node.** A 180 nm mask set is ~\$250,000. Most chips in the world — microcontrollers, power management, automotive — are not on leading-edge nodes and never will be.
2. **Use an FPGA.** [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] showed an FPGA is an array of LUTs configured by stored bits. **You pay a large area and speed penalty to avoid the mask cost entirely** — someone else already paid it, and you buy their chip and reconfigure it.

That tradeoff is now fully explained: FPGAs exist because **masks are a fixed cost and reconfigurability moves the function from structure into data.** Both halves of that sentence came from different modules, and they meet here.
</details>

---

## 9. Worked example — runnable

Save as `fab_lab.py` and run `python3 fab_lab.py`.

```python
"""Photolithography limits, yield, and why big chips cost so much."""
import math

def rayleigh_resolution(wavelength_nm, numerical_aperture, k1=0.30):
    """Smallest half-pitch printable: CD = k1 * lambda / NA."""
    return k1 * wavelength_nm / numerical_aperture

def patterning_passes(target_nm, single_exposure_nm):
    """Multi-patterning: how many exposures to reach a pitch below the limit."""
    if target_nm >= single_exposure_nm:
        return 1
    return math.ceil(single_exposure_nm / target_nm)

def yield_poisson(die_area_cm2, defect_density_per_cm2):
    """Poisson yield model: probability a die contains zero fatal defects."""
    return math.exp(-die_area_cm2 * defect_density_per_cm2)

def gross_dies_per_wafer(wafer_diameter_mm, die_area_cm2):
    """Dies that fit on a wafer, allowing for wasted edge area."""
    r = wafer_diameter_mm / 20.0                      # radius in cm
    return math.floor(math.pi * r**2 / die_area_cm2
                      - math.pi * 2 * r / math.sqrt(2 * die_area_cm2))

def cost_per_good_die(wafer_cost, wafer_diameter_mm, die_area_cm2, defect_density):
    gross = gross_dies_per_wafer(wafer_diameter_mm, die_area_cm2)
    good = gross * yield_poisson(die_area_cm2, defect_density)
    return (wafer_cost / good) if good >= 1 else float("inf"), gross, good

if __name__ == "__main__":
    print("PHOTOLITHOGRAPHY -- printing features smaller than the light used")
    print(f"  {'light source':28s} {'lambda':>8s} {'NA':>6s} {'half-pitch':>12s}")
    for name, lam, na in [("i-line mercury lamp", 365, 0.60),
                          ("KrF excimer (deep UV)", 248, 0.70),
                          ("ArF excimer", 193, 0.93),
                          ("ArF immersion (water)", 193, 1.35),
                          ("EUV", 13.5, 0.33),
                          ("High-NA EUV", 13.5, 0.55)]:
        print(f"  {name:28s} {lam:6.1f}nm {na:6.2f} {rayleigh_resolution(lam, na):10.1f} nm")
    print()

    print("The trick that kept Moore's law alive: MULTI-PATTERNING")
    single = rayleigh_resolution(193, 1.35)
    print(f"  193nm immersion prints a {single:.1f} nm half-pitch in one exposure")
    for target in (40, 20, 10):
        n = patterning_passes(target, single)
        print(f"  a {target:2d} nm pitch needs {n} exposure(s)"
              f" -> {n}x the masks, {n}x the time, {n}x the alignment error budget")
    print()

    print("YIELD -- why big chips are disproportionately expensive")
    print("  (Poisson model: Y = exp(-area x defect_density))")
    D = 0.10                                   # defects per cm^2, a good mature process
    print(f"  defect density = {D} per cm^2, 300 mm wafer, $15,000 per wafer")
    print(f"  {'die area':>9s} {'gross':>7s} {'yield':>7s} {'good':>7s} {'$/good die':>11s}")
    for area in (0.5, 1.0, 2.0, 4.0, 6.0, 8.0):
        cost, gross, good = cost_per_good_die(15000, 300, area, D)
        print(f"  {area:7.1f}cm2 {gross:7d} {100*yield_poisson(area, D):6.1f}%"
              f" {good:7.0f} {cost:10.2f}")
    print()

    big, small = 8.0, 1.0
    c_big, _, _ = cost_per_good_die(15000, 300, big, D)
    c_small, _, _ = cost_per_good_die(15000, 300, small, D)
    print(f"  one {big:.0f} cm2 die costs ${c_big:.0f};"
          f" {big/small:.0f} dies of {small:.0f} cm2 cost ${c_small*big/small:.0f}")
    print(f"  -> splitting a big chip into chiplets is"
          f" {c_big/(c_small*big/small):.1f}x cheaper in silicon")
    print()

    print("MASK LAYERS -- each one is a separate print-and-etch cycle")
    for node, layers, mask_cost in [("180 nm", 22, 250_000),
                                    ("28 nm", 40, 2_000_000),
                                    ("7 nm", 60, 15_000_000),
                                    ("3 nm", 75, 30_000_000)]:
        print(f"  {node:7s} ~{layers:2d} mask layers, mask set ~${mask_cost:,}")
    print("  a mask set is paid ONCE per design -- which is why low-volume")
    print("  custom chips are uneconomic and FPGAs exist (module 20)")

    assert rayleigh_resolution(193, 1.35) < rayleigh_resolution(193, 0.93)
    assert yield_poisson(8.0, 0.1) < yield_poisson(1.0, 0.1)
    assert gross_dies_per_wafer(300, 1.0) > gross_dies_per_wafer(300, 4.0)
    print()
    print("fab_lab: passed")
```

Expected output:

```
PHOTOLITHOGRAPHY -- printing features smaller than the light used
  light source                   lambda     NA   half-pitch
  i-line mercury lamp           365.0nm   0.60      182.5 nm
  KrF excimer (deep UV)         248.0nm   0.70      106.3 nm
  ArF excimer                   193.0nm   0.93       62.3 nm
  ArF immersion (water)         193.0nm   1.35       42.9 nm
  EUV                            13.5nm   0.33       12.3 nm
  High-NA EUV                    13.5nm   0.55        7.4 nm

The trick that kept Moore's law alive: MULTI-PATTERNING
  193nm immersion prints a 42.9 nm half-pitch in one exposure
  a 40 nm pitch needs 2 exposure(s) -> 2x the masks, 2x the time, 2x the alignment error budget
  a 20 nm pitch needs 3 exposure(s) -> 3x the masks, 3x the time, 3x the alignment error budget
  a 10 nm pitch needs 5 exposure(s) -> 5x the masks, 5x the time, 5x the alignment error budget

YIELD -- why big chips are disproportionately expensive
  (Poisson model: Y = exp(-area x defect_density))
  defect density = 0.1 per cm^2, 300 mm wafer, $15,000 per wafer
   die area   gross   yield    good  $/good die
      0.5cm2    1319   95.1%    1255      11.96
      1.0cm2     640   90.5%     579      25.90
      2.0cm2     306   81.9%     251      59.87
      4.0cm2     143   67.0%      96     156.49
      6.0cm2      90   54.9%      49     303.69
      8.0cm2      64   44.9%      29     521.61

  one 8 cm2 die costs $522; 8 dies of 1 cm2 cost $207
  -> splitting a big chip into chiplets is 2.5x cheaper in silicon

MASK LAYERS -- each one is a separate print-and-etch cycle
  180 nm  ~22 mask layers, mask set ~$250,000
  28 nm   ~40 mask layers, mask set ~$2,000,000
  7 nm    ~60 mask layers, mask set ~$15,000,000
  3 nm    ~75 mask layers, mask set ~$30,000,000
  a mask set is paid ONCE per design -- which is why low-volume
  custom chips are uneconomic and FPGAs exist (module 20)

fab_lab: passed
```

---

## 10. Common pitfalls and traps

1. **Thinking transistors are placed individually.** Nothing is placed. Everything on a layer is printed simultaneously by one exposure.
2. **Reading node names as measurements.** "5 nm" names a generation, not a feature. Compare density instead.
3. **Assuming smaller is always better.** Leading-edge nodes cost more per wafer, need multi-patterning or EUV, and leak more. Most chips are deliberately built on older nodes.
4. **Forgetting wires.** Over half a modern die's layers are interconnect, and wire delay often dominates gate delay.
5. **Ignoring yield when sizing a chip.** Cost grows faster than area, and the effect is exponential, not linear.
6. **Thinking the mask is chip-sized.** It carries the pattern at ~4× and is optically shrunk.

---

## 11. Check your understanding

1. **Why is the self-aligned gate such an important invention?**
   <details><summary>Answer</summary>
   The channel must lie exactly between source and drain. Achieving that with two independently aligned masks would demand nanometre alignment accuracy — impossible at scale, and any error would either add parasitic capacitance (overlap) or leave an uncontrolled region (gap).<br>
   Self-alignment sidesteps the problem: the gate is patterned first, then <em>blocks the implant itself</em>, so the channel is defined by the gate's own shadow. <strong>A precision requirement was replaced by a geometric guarantee</strong> — and the alignment error becomes structurally impossible rather than merely small.
   </details>

2. **A design team doubles a chip's die area to add features. What happens to cost per working chip, and why is it worse than 2×?**
   <details><summary>Answer</summary>
   Two effects compound. <strong>Fewer dies per wafer</strong> — roughly half, plus worse edge waste. <strong>Lower yield</strong> — $Y = e^{-AD}$ falls exponentially with area.<br>
   From the table, 4 cm² to 8 cm² takes cost from \$156 to \$522, a <strong>3.3× increase for 2× the area</strong>. This is the core economic argument for chiplets, and why architects fight hard for area efficiency in a way that seems disproportionate until you see this curve.
   </details>

3. **Why did the industry spend two decades and tens of billions on EUV instead of continuing with multi-patterning?**
   <details><summary>Answer</summary>
   Multi-patterning works but scales badly. Each additional exposure means another mask (millions of dollars), another scanner pass (throughput falls proportionally), and another alignment step whose error adds to the budget. At 10 nm pitch you need about five exposures — five times the cost and time for one layer.<br>
   EUV's 13.5 nm wavelength restores single-exposure patterning at those pitches. <strong>The economics eventually favoured rebuilding the entire optical stack</strong> — vacuum, mirrors, tin-plasma sources — over continuing to multiply exposures.
   </details>

4. **How does this module change your reading of "a wire" in a circuit diagram?**
   <details><summary>Answer</summary>
   A schematic line is an idealisation: zero resistance, zero delay, zero capacitance. A real on-chip wire is a <strong>copper trench in an insulator</strong>, on one of 10–15 metal layers, with genuine R and C.<br>
   That RC is precisely module 4's propagation delay, and it now dominates gate delay for long routes. So a schematic tells you the <em>logic</em> but not the <em>timing</em> — which is why place-and-route happens before timing can be signed off, and why moving a block physically further away can break a design that was logically correct.
   </details>

---

## 12. Practice — independent task

**Task:** You are advising on the packaging strategy for a 256-core processor. Each core plus its cache occupies 0.35 cm². Defect density is 0.08/cm², wafers are 300 mm and cost \$18,000.

- **(a)** Compute the die area for a single monolithic 256-core chip. Compute gross dies per wafer, yield, good dies, and cost per good die.
- **(b)** Now split it into chiplets of 32 cores each. Compute area, yield and cost per chiplet, then the silicon cost of the eight chiplets needed for one product.
- **(c)** Packaging eight chiplets costs \$90 more than packaging one monolithic die. Which option is cheaper overall, and by how much?
- **(d)** At what defect density do the two options break even? Solve numerically by sweeping $D$.
- **(e)** Monolithic dies communicate on-die; chiplets need inter-die links that cost power and latency. State two workloads where that penalty would change your recommendation.
- **(f)** Add `chiplet_vs_monolithic(cores, area_per_core, chiplet_cores, defect_density, wafer_cost, packaging_delta)` to `fab_lab.py`, returning both costs and the winner. Verify your answers to (a)–(c).
- **(g)** With binning, a monolithic die with up to 16 dead cores can be sold as a 240-core part. Estimate how much that improves effective monolithic yield, and whether it changes your answer.

**Done when:** your function reproduces your hand calculations, you have a break-even defect density, and you can state one condition under which monolithic wins despite worse yield.

<details><summary>Hint for (d), only if stuck</summary>
As $D \to 0$ yield approaches 100% for both, so the monolithic option wins — it avoids the \$90 packaging premium and wastes no area on inter-die interfaces.<br>
As $D$ grows, the exponential punishes large dies far harder. Sweep $D$ from 0.01 to 0.2 in small steps and find the crossing. <strong>This is genuinely why chiplets appeared when they did</strong> — not because the idea was new, but because die sizes grew until the yield curve made it unavoidable.
</details>

---

## 13. Tradeoffs and limits

- **This is a simplified flow.** A real process has 60–75 mask layers, with wells, multiple threshold implants, strain engineering, silicide, and many steps omitted here.
- **The Poisson yield model is optimistic.** Real defects cluster rather than distributing uniformly, so refined models (Murphy, negative binomial) are used commercially. The qualitative conclusion — cost grows faster than area — holds under all of them.
- **Planar transistors are shown; modern ones are 3D.** FinFETs and gate-all-around nanosheets wrap the gate around the channel. The lithography and layering story is unchanged; the device cross-section is not.
- **Packaging is now a first-class design problem.** Advanced packaging — 2.5D interposers, 3D stacking, hybrid bonding — is where much current innovation sits, precisely because of the yield economics above.

---

## Before moving on

**This is the end of Part IV.** You are ready for Part V when you can, closed-book:

- [ ] Describe the seven-step photolithography loop and explain why chips are built in layers.
- [ ] Walk through building a MOSFET and explain self-alignment.
- [ ] Describe the metal interconnect stack and say what a chip "wire" physically is.
- [ ] Explain how 193 nm light prints 20 nm features, and what multi-patterning costs.
- [ ] Compute yield from die area and defect density, and explain the chiplet argument.

**Recap:** Chips are printed, not assembled — one exposure patterns an entire layer regardless of how many transistors it contains, which is why transistors became effectively free. The process is one loop (deposit, coat, expose, develop, etch or implant, strip, planarise) repeated 60–75 times. The self-aligned gate defines the channel by blocking its own implant, removing an impossible alignment requirement. Above the transistors sit 10–15 metal layers of copper trenches — the wires of every schematic. Resolution follows $k_1\lambda/\text{NA}$, and multi-patterning or EUV is needed below ~43 nm. Yield falls exponentially with die area, making cost grow faster than size and motivating chiplets.

**Next:** [[how-computers-work/04-logic/01-gates-from-transistors|Module 15 — Gates from Transistors]] begins Part V. You now know both how a CMOS gate works *and* how it is physically manufactured and wired — so when module 15 says NAND cells are smaller and tile into rows, you know exactly what that means on silicon.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/02-semiconductors/02-silicon-and-crystal|Module 7]] — where the wafer came from
- [[how-computers-work/02-semiconductors/04-doping|Module 9]] — ion implantation through a mask
- [[how-computers-work/03-transistors/03-cmos|Module 13]] — the device being built here
- [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] — FPGAs, and why mask cost makes them worth it
- [[computer-architecture/08-the-memory-hierarchy|computer-architecture/memory hierarchy]] — partly a response to wire delay
