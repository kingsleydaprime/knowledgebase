# Module 26: Memory Technology (Six Transistors Versus One Capacitor)

**[Intermediate]** — Part VII ends by asking why we don't build all memory the way module 25 built registers. The answer is cost per bit — and that single number generates the entire memory hierarchy.

## Before you start

- You know a flip-flop stores a bit in a cross-coupled feedback loop — [[how-computers-work/06-memory/01-latches-and-flip-flops|module 24]].
- You can build a register file from a decoder and multiplexers — [[how-computers-work/06-memory/02-registers-and-counters|module 25]].
- You know decoders must be hierarchical for wide addresses — [[how-computers-work/05-combinational/01-multiplexers-and-decoders|module 20]].
- You remember noise margins and what happens when they shrink — [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]].

**After this lesson you will be able to:**

1. Explain the SRAM cell and why it is fast, large and volatile.
2. Explain the DRAM cell, why it needs refresh, and what refresh costs.
3. Explain how a floating gate makes flash non-volatile, and why it wears out.
4. **Derive** the memory hierarchy from cell cost rather than accepting it as given.

**Study route:** section 3 and 4 are the two competing cell designs. Section 7 is the payoff — the hierarchy falling out of the numbers.

---

## 1. Why this exists (real-world motivation)

Module 25 built a register file. It works, it is fast, and you could in principle build all of a computer's memory the same way.

**Do the arithmetic and see why nobody does.**

A master–slave D flip-flop is roughly 20–24 transistors. For 16 GB of memory — $1.3 \times 10^{11}$ bits — that would be about **$3 \times 10^{12}$ transistors.** A large modern processor has around $10^{11}$. You would need thirty of the largest chips ever manufactured, for the RAM alone, and it would draw kilowatts.

**So memory is not one technology. It is a family**, each member making a different bargain between speed, density, cost and volatility. The bargains are not arbitrary — they follow from what a cell physically has to do.

**And the memory hierarchy you have heard about is not a design choice.** It is the unavoidable consequence of those bargains.

---

## 2. Terminology

| Term | Plain-English definition |
| :--- | :--- |
| **Cell** | The circuit storing one bit |
| **SRAM** | Static RAM — holds its bit as long as power is on |
| **DRAM** | Dynamic RAM — holds charge that leaks, so needs refresh |
| **Refresh** | Periodically reading and rewriting DRAM to restore charge |
| **Volatile** | Loses contents when power is removed |
| **Word line** | The row select line from the decoder |
| **Bit line** | The column line carrying data in and out |
| **Sense amplifier** | Circuit detecting the tiny voltage a DRAM cell produces |
| **Floating gate** | A fully insulated gate that traps charge — the basis of flash |
| **SLC / MLC / TLC / QLC** | 1, 2, 3 or 4 bits stored per flash cell |
| **F²** | Cell area in units of the squared feature size — a process-independent measure |
| **P/E cycle** | One program/erase cycle; flash endurance is counted in these |

---

## 3. SRAM — the flip-flop, slimmed down

An SRAM cell is **module 24's bistable loop**, reduced to its minimum: two cross-coupled inverters (4 transistors) plus two access transistors connecting it to the bit lines.

```
              word line (from the row decoder)
        ────────┬───────────────────┬────────
                │                   │
             ┌──┴──┐             ┌──┴──┐
             │ M5  │             │ M6  │      access transistors
             └──┬──┘             └──┬──┘
                │                   │
       bit_line │   ┌───────────┐   │ bit_line_bar
                ├───┤ inverter  ├───┤
                │   └───────────┘   │
                │   ┌───────────┐   │        the SAME cross-coupled
                ├───┤ inverter  ├───┤        pair as module 24
                │   └───────────┘   │
```

**Six transistors, and the bit is the equilibrium of the loop** — exactly as in module 24. It never needs refreshing, because the inverters actively drive the state; as long as power flows, each side holds the other.

**Consequences:**

- **Fast** (~1 ns) — the cell actively drives the bit line, so the signal is strong.
- **Large** (~140 F² per bit) — six transistors plus the wiring.
- **Volatile** — the state is a maintained equilibrium, not a stored object. Remove power and it does not decay, it simply stops existing.

**This is what caches are made of**, and why cache is measured in megabytes while main memory is measured in gigabytes.

---

## 4. DRAM — one transistor and a bucket of charge

DRAM abandons the feedback loop entirely. **A bit is charge on a capacitor**, with a single transistor as the gate.

```
              word line
        ─────────┬──────────
                 │
              ┌──┴──┐
              │  M1 │        one access transistor
              └──┬──┘
                 │
      bit line ──┤
                 │
                ═╪═           capacitor: ~25 fF
                 │            charged = 1, empty = 0
                GND
```

**One transistor and one capacitor — about 6 F², more than twenty times denser than SRAM.** That density is the whole reason DRAM exists.

**The price is that capacitors leak.** Charge drains through the transistor's off-state leakage and through the dielectric — the subthreshold leakage of [[how-computers-work/03-transistors/02-mosfet-physics|module 12]], now working directly against you. Within tens of milliseconds a stored 1 becomes indistinguishable from a 0.

### Refresh

Every row must be read and rewritten before its charge decays — typically every 64 ms.

| Rows | Window | Row cycle | Bandwidth lost |
| ---: | ---: | ---: | ---: |
| 8192 | 64 ms | 50 ns | 0.64% |
| 16384 | 64 ms | 45 ns | 1.15% |
| 32768 | 32 ms | 45 ns | **4.61%** |

**Refresh is a real tax, and it grows.** More capacity means more rows; and because leakage rises with temperature ([[how-computers-work/02-semiconductors/03-energy-bands|module 8]]), hot DRAM needs a *shorter* window — which is why the third row costs 4.6%. Servers under thermal load genuinely lose measurable memory bandwidth to refresh.

> [!NOTE]
> **Reading DRAM is destructive**, which surprises people. The tiny stored charge is shared onto the much larger bit line capacitance, producing a swing of only ~100 mV — far too small for the logic levels of module 5. A **sense amplifier** amplifies it back to a full rail.
>
> But the act of reading has drained the cell. **So every read is followed by a write-back**, and this is why DRAM has a row cycle time longer than its access time, and why the "row buffer" exists: once a row is opened and sensed, reading more columns from it is cheap. That asymmetry is why sequential memory access is so much faster than random access — and it is the hardware reason [[foundations/dsa/04-data-structures/01-arrays|arrays outperform linked lists]] far more than their Big-O suggests.

---

## 5. Flash — trapping charge behind an insulator

SRAM and DRAM both lose everything when power goes. **Non-volatility needs charge that cannot escape even with no power applied.**

Flash adds a **second gate inside the transistor, completely surrounded by insulator**:

```
              control gate
        ┌───────────────────────┐
        │███████████████████████│
        ├───────────────────────┤   insulator
        │▓▓▓ FLOATING GATE ▓▓▓▓▓│   <- charge trapped HERE
        ├───────────────────────┤   insulator (tunnel oxide)
      ──┴───────────────────────┴──
        n+                      n+
              p-substrate
```

Charge is forced onto the floating gate by **quantum tunnelling** — the same effect that limited gate oxide thinning in [[how-computers-work/03-transistors/01-what-a-transistor-is|module 11]], used deliberately here.

Once there, **it has nowhere to go.** The floating gate is surrounded by SiO₂ with its 9 eV band gap ([[how-computers-work/02-semiconductors/03-energy-bands|module 8]]), so the charge stays for years without power. Its presence shifts the transistor's threshold voltage, and reading the cell means testing which threshold it now has.

**That is what "non-volatile" physically means:** not a different kind of memory, but electrons parked behind an insulator too tall to climb.

### The ROM family, and how it got writable

Flash is the end of a lineage, and the names are worth knowing because you will meet all of them:

| Type | Written | Erased | Where you meet it |
| :--- | :--- | :--- | :--- |
| **ROM** | At manufacture, by the mask itself | Never | High-volume fixed firmware |
| **PROM** | Once, by blowing fuses | Never | One-time configuration |
| **EPROM** | Electrically | **Ultraviolet light**, ~20 minutes | Older firmware; the chip has a quartz window |
| **EEPROM** | Electrically | **Electrically**, byte by byte | Small configuration stores, the [[build-your-own-shit/17-your-own-cpu/04-breadboard\|PRIME-1 control ROM]] |
| **Flash** | Electrically | Electrically, **in large blocks** | SSDs, phones, everything |

**The progression is one of steadily cheaper erasure.** Mask ROM cannot be changed at all. PROM's fuses are physically destroyed. EPROM needed UV photons energetic enough to knock trapped electrons off the floating gate — which is why those chips had a quartz window, and why a sticker over it was mandatory.

**EEPROM made erasure electrical**, using the same tunnelling as programming but reversed. That is genuinely convenient and genuinely expensive: byte-level erase needs extra transistors per cell.

**Flash is EEPROM with the erase granularity coarsened deliberately.** Erasing in large blocks rather than bytes removes most of that per-cell circuitry, which is what makes flash dense enough to be cheap. **The entire complexity of SSD firmware — wear levelling, garbage collection, the flash translation layer — exists to hide that one compromise** from software that expects to write single bytes.

### Multi-level cells, and why flash wears out

| Technology | Bits/cell | Write cycles |
| :--- | ---: | ---: |
| NAND SLC | 1 | 100,000 |
| NAND TLC | 3 | 3,000 |

**Storing 3 bits per cell means distinguishing 8 charge levels instead of 2.** The voltage window is divided eight ways, so each level has far less margin.

**This is [[how-computers-work/01-electricity/05-the-digital-abstraction|module 5]]'s bargain being traded away for density** — precisely the "more voltage bands means less noise margin" tradeoff from that module's check-your-understanding, now a shipping product.

**And flash wears out.** Every program/erase cycle forces electrons through the tunnel oxide, and each passage damages it slightly. Eventually the oxide traps charge permanently and the cell can no longer be reliably erased. TLC's smaller margins mean less damage is needed to push a level out of its band — hence ~30× fewer cycles than SLC.

This is why SSDs perform **wear levelling**, spreading writes across cells, and why they report remaining endurance. It is also why a drive can fail from *writing* rather than from age.

---

## 6. Predict before reading on

SRAM is ~23× larger per bit than DRAM, and DRAM is ~1000× slower to access.

**Given that, why is any SRAM used at all — and why is any DRAM?**

<details><summary>Check your answer</summary>

**Because neither dominates on both axes, so the right answer is to use both.**

If SRAM were merely more expensive, you would buy less of it. If DRAM were merely slower, you would wait. But the gap is enormous in *both* directions: SRAM is 23× the area, DRAM is ~60× the latency.

**So the machine uses a small amount of the fast one and a large amount of the cheap one**, and tries hard to keep the data it needs in the fast one. That "tries hard" is **caching**, and it works only because real programs exhibit locality — they reuse recent data and access neighbouring addresses.

**The memory hierarchy is not a design someone chose.** It is what you are forced into when no single technology is both fast and cheap. If someone invented a memory that was as fast as SRAM and as dense as DRAM, the hierarchy would collapse to one level and a large part of [[foundations/computer-architecture/08-the-memory-hierarchy|computer architecture]] would become unnecessary.
</details>

---

## 7. The hierarchy, derived

Put the numbers together and the familiar pyramid emerges — not as a diagram to memorise, but as a consequence:

| Level | Capacity | Latency | CPU cycles |
| :--- | ---: | ---: | ---: |
| Registers | 256 B | 0.05 ns | <1 |
| L1 cache | 32 KB | 1 ns | 3 |
| L2 cache | 512 KB | 4 ns | 13 |
| L3 cache | 32 MB | 20 ns | 67 |
| DRAM | 16 GB | 80 ns | **267** |
| NAND SSD | 1 TB | 50 µs | **166,667** |

**A DRAM access costs about 270 CPU cycles.** In that time a modern superscalar core could have retired several hundred instructions. An SSD access costs over 160,000 cycles — the CPU may as well run an entirely different thread.

**Every number in that table traces back to a cell design:**

- Registers are flip-flops — biggest cell, fastest, so there are dozens.
- Caches are SRAM — 140 F², so megabytes.
- Main memory is DRAM — 6 F² but needs sensing and refresh, so gigabytes and 60 ns.
- Storage is flash — 1.33 F²/bit at TLC, non-volatile, but erase-block granularity makes it microseconds.

**The pyramid is the cell costs, sorted.**

---

## 8. Worked example — runnable

Save as `memory_lab.py` and run `python3 memory_lab.py`.

```python
"""Why one bit costs different amounts in different technologies --
and why that single fact produces the memory hierarchy."""

# Cell area in F^2, where F is the process feature size.
# Using F^2 rather than transistor counts because DRAM's capacitor and
# NAND's 3D stacking make raw transistor counts misleading.
TECHNOLOGIES = {
    #                    cell area   bits/    latency    volatile  writes
    #                      (F^2)     cell       (ns)
    "flip-flop":         (   300.0,   1,        0.05,     True,    float("inf")),
    "SRAM (6T)":         (   140.0,   1,        1.0,      True,    float("inf")),
    "DRAM (1T1C)":       (     6.0,   1,       60.0,      True,    float("inf")),
    "NAND flash (SLC)":  (     4.0,   1,    50_000.0,     False,   100_000),
    "NAND flash (TLC)":  (     4.0,   3,   100_000.0,     False,     3_000),
}

def area_per_bit(name):
    area, bits, *_ = TECHNOLOGIES[name]
    return area / bits

def relative_density(name, baseline="SRAM (6T)"):
    return area_per_bit(baseline) / area_per_bit(name)

def dram_refresh_overhead(rows, refresh_period_ms, row_cycle_ns):
    """DRAM capacitors leak. Every row must be re-read and rewritten
    within the retention window, and that steals bandwidth."""
    refresh_time_ns = rows * row_cycle_ns
    window_ns = refresh_period_ms * 1e6
    return refresh_time_ns / window_ns

def hierarchy_level(name, capacity_bytes, latency_ns, cycle_ns=0.3):
    """How many CPU cycles does a miss to this level cost?"""
    return capacity_bytes, latency_ns, latency_ns / cycle_ns

def human_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}"
        n /= 1024

if __name__ == "__main__":
    print("COST OF ONE BIT, by technology")
    print(f"  {'technology':20s} {'F^2/bit':>9s} {'density':>9s} {'latency':>12s}"
          f" {'volatile':>9s}")
    for name in TECHNOLOGIES:
        area, bits, lat, vol, _ = TECHNOLOGIES[name]
        lat_str = f"{lat:.2f} ns" if lat < 1000 else f"{lat/1000:.0f} us"
        print(f"  {name:20s} {area_per_bit(name):9.2f}"
              f" {relative_density(name):8.1f}x {lat_str:>12s}"
              f" {'yes' if vol else 'no':>9s}")
    print()
    print("  a flip-flop is ~50x larger per bit than DRAM, and ~2x larger than SRAM.")
    print("  THIS is why registers are counted in dozens, caches in megabytes,")
    print("  and main memory in gigabytes. Nobody chose that spread -- it falls")
    print("  out of cell cost.")
    print()

    print("WHY DRAM IS SO SMALL: 1 transistor + 1 capacitor")
    print("  SRAM holds its bit in a feedback loop (module 24) -- it needs")
    print("  6 transistors and constant power, but it never forgets.")
    print("  DRAM holds its bit as CHARGE ON A CAPACITOR -- 1 transistor,")
    print("  but the charge leaks away in milliseconds.")
    print()

    print("THE PRICE OF DRAM: refresh")
    for rows, period_ms, cycle_ns in [(8192, 64, 50), (16384, 64, 45), (32768, 32, 45)]:
        ov = dram_refresh_overhead(rows, period_ms, cycle_ns)
        print(f"  {rows:6d} rows, {period_ms} ms window, {cycle_ns} ns/row"
              f"  -> {100*ov:.2f}% of bandwidth lost to refresh")
    print("  the memory is unavailable during refresh -- a real, if small, tax")
    print("  that grows as capacity grows and retention windows shrink with heat")
    print()

    print("NON-VOLATILE: the floating gate")
    print("  flash adds a SECOND, fully insulated gate inside the transistor.")
    print("  charge tunnelled onto it has nowhere to go -- it stays for years")
    print("  with no power. That is what 'non-volatile' physically means.")
    print()
    print(f"  {'technology':20s} {'bits/cell':>10s} {'write cycles':>14s}")
    for name in ("NAND flash (SLC)", "NAND flash (TLC)"):
        _, bits, _, _, cycles = TECHNOLOGIES[name]
        print(f"  {name:20s} {bits:10d} {cycles:14,}")
    print("  storing 3 bits/cell means distinguishing 8 charge levels instead")
    print("  of 2 -- denser and cheaper, but far less margin, so it wears out")
    print("  ~30x sooner. This is the digital abstraction (module 5) being")
    print("  traded away for density.")
    print()

    print("THE HIERARCHY THAT FALLS OUT OF ALL THIS")
    print(f"  {'level':14s} {'capacity':>10s} {'latency':>11s} {'CPU cycles':>12s}")
    levels = [
        ("registers",     256,           0.05),
        ("L1 cache",      32 * 1024,     1.0),
        ("L2 cache",      512 * 1024,    4.0),
        ("L3 cache",      32 * 1024**2,  20.0),
        ("DRAM",          16 * 1024**3,  80.0),
        ("NAND SSD",      1024**4,       50_000.0),
    ]
    for name, cap, lat in levels:
        _, _, cycles = hierarchy_level(name, cap, lat)
        lat_str = f"{lat:.2f} ns" if lat < 1000 else f"{lat/1000:.0f} us"
        print(f"  {name:14s} {human_bytes(cap):>10s} {lat_str:>11s} {cycles:11,.0f}")
    print()
    print("  a DRAM access costs ~270 cycles. In that time the CPU could have")
    print("  executed hundreds of instructions. Caches exist to avoid paying it.")

    assert relative_density("DRAM (1T1C)") > relative_density("SRAM (6T)")
    assert area_per_bit("NAND flash (TLC)") < area_per_bit("NAND flash (SLC)")
    assert TECHNOLOGIES["SRAM (6T)"][2] < TECHNOLOGIES["DRAM (1T1C)"][2]
    assert 0 < dram_refresh_overhead(8192, 64, 50) < 0.05
    print()
    print("memory_lab: passed")
```

Expected output:

```
COST OF ONE BIT, by technology
  technology             F^2/bit   density      latency  volatile
  flip-flop               300.00      0.5x      0.05 ns       yes
  SRAM (6T)               140.00      1.0x      1.00 ns       yes
  DRAM (1T1C)               6.00     23.3x     60.00 ns       yes
  NAND flash (SLC)          4.00     35.0x        50 us        no
  NAND flash (TLC)          1.33    105.0x       100 us        no

  a flip-flop is ~50x larger per bit than DRAM, and ~2x larger than SRAM.
  THIS is why registers are counted in dozens, caches in megabytes,
  and main memory in gigabytes. Nobody chose that spread -- it falls
  out of cell cost.

WHY DRAM IS SO SMALL: 1 transistor + 1 capacitor
  SRAM holds its bit in a feedback loop (module 24) -- it needs
  6 transistors and constant power, but it never forgets.
  DRAM holds its bit as CHARGE ON A CAPACITOR -- 1 transistor,
  but the charge leaks away in milliseconds.

THE PRICE OF DRAM: refresh
    8192 rows, 64 ms window, 50 ns/row  -> 0.64% of bandwidth lost to refresh
   16384 rows, 64 ms window, 45 ns/row  -> 1.15% of bandwidth lost to refresh
   32768 rows, 32 ms window, 45 ns/row  -> 4.61% of bandwidth lost to refresh
  the memory is unavailable during refresh -- a real, if small, tax
  that grows as capacity grows and retention windows shrink with heat

NON-VOLATILE: the floating gate
  flash adds a SECOND, fully insulated gate inside the transistor.
  charge tunnelled onto it has nowhere to go -- it stays for years
  with no power. That is what 'non-volatile' physically means.

  technology            bits/cell   write cycles
  NAND flash (SLC)              1        100,000
  NAND flash (TLC)              3          3,000
  storing 3 bits/cell means distinguishing 8 charge levels instead
  of 2 -- denser and cheaper, but far less margin, so it wears out
  ~30x sooner. This is the digital abstraction (module 5) being
  traded away for density.

THE HIERARCHY THAT FALLS OUT OF ALL THIS
  level            capacity     latency   CPU cycles
  registers           256 B     0.05 ns           0
  L1 cache            32 KB     1.00 ns           3
  L2 cache           512 KB     4.00 ns          13
  L3 cache            32 MB    20.00 ns          67
  DRAM                16 GB    80.00 ns         267
  NAND SSD             1 TB       50 us     166,667

  a DRAM access costs ~270 cycles. In that time the CPU could have
  executed hundreds of instructions. Caches exist to avoid paying it.

memory_lab: passed
```

---

## 9. Addressing a large array

[[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] warned that flat decoding does not scale — a 32-bit address would need $2^{32}$ AND gates. Memory arrays solve this by decoding in **two dimensions**.

```
                    column decoder
                  ┌──┬──┬──┬──┬──┐
        row       │  │  │  │  │  │
      decoder  ───┼──┼──┼──┼──┼──┤  <- word line (one row selected)
                  │  │  │  │  │  │
               ───┼──┼──┼──┼──┼──┤
                  │  │  │  │  │  │
                  └──┴──┴──┴──┴──┘
                   bit lines (columns)
                          │
                  ┌───────▼────────┐
                  │ sense amplifiers│
                  └────────────────┘
```

Split a 20-bit address into 10 row bits and 10 column bits: **two decoders of 1024 outputs each, instead of one with a million.** $2 \times 2^{10}$ gates rather than $2^{20}$.

**This is why DRAM has separate row and column address strobes (RAS/CAS)** and why the row buffer matters: opening a row is the expensive step, and once open, other columns in it are cheap. Sequential access reuses the open row; random access reopens constantly.

That is the mechanism behind **spatial locality** paying off, and the reason a cache line is fetched as a contiguous block rather than a single word.

---

## 10. Common pitfalls and traps

1. **Thinking "static" means non-volatile.** SRAM is static because it needs no refresh, but it is entirely volatile.
2. **Assuming DRAM reads are non-destructive.** Every read drains the cell and must be followed by a write-back.
3. **Treating flash as RAM.** Flash erases in large blocks, not bytes, and wears out. This drives the whole design of SSD firmware.
4. **Believing more bits per cell is free.** TLC is denser and ~30× less durable, with slower writes and more error correction.
5. **Ignoring temperature.** DRAM retention falls as it heats, so refresh rates rise and effective bandwidth drops.
6. **Thinking the hierarchy was designed.** It is forced by cell economics, and it would vanish if one technology were both fast and dense.

---

## 11. Check your understanding

1. **Why does SRAM need no refresh while DRAM does?**
   <details><summary>Answer</summary>
   SRAM's cross-coupled inverters <strong>actively drive</strong> the stored state — each side continuously holds the other, powered by the supply. Any leakage is immediately replaced.<br>
   DRAM stores <strong>passive charge</strong> on an isolated capacitor with nothing replenishing it. Leakage through the access transistor and the dielectric drains it within milliseconds, so it must be periodically read and rewritten. <strong>Active maintenance versus passive storage</strong> is the whole difference, and it is also why SRAM is 23× larger.
   </details>

2. **An SSD is rated for 3,000 P/E cycles. Why can it still be warrantied for years of heavy use?**
   <details><summary>Answer</summary>
   Because of <strong>wear levelling</strong>. The controller spreads writes across all blocks rather than repeatedly hitting the same ones, so endurance is the <em>drive's</em> total write capacity, not one block's.<br>
   A 1 TB drive at 3,000 cycles per cell can absorb roughly 3 PB of writes. At 50 GB/day that is over 160 years. The controller also over-provisions spare blocks, retires failing ones, and uses strong error correction. <strong>The weak cell is compensated for at the system level</strong> — the same move as module 5's noise margins, one layer up.
   </details>

3. **Why is sequential memory access so much faster than random access, beyond just caching?**
   <details><summary>Answer</summary>
   DRAM is addressed by row and column. Reading requires <strong>opening a row</strong> — activating the word line and letting sense amplifiers resolve the tiny charge — which is the slow part. Once open, other columns in that row are read quickly from the row buffer.<br>
   Sequential access mostly hits the already-open row; random access forces a close-and-reopen almost every time, paying the full latency repeatedly. <strong>This is a property of the array structure, independent of caching</strong>, and it is why the performance gap between arrays and pointer-chasing structures is far larger than complexity analysis predicts.
   </details>

4. **What would happen to computer architecture if someone invented memory as fast as SRAM and as dense as DRAM?**
   <details><summary>Answer</summary>
   <strong>The memory hierarchy would collapse.</strong> Caches exist solely to bridge a gap that would no longer exist — so cache design, replacement policies, prefetching, cache-aware algorithms and most of the locality optimisations in software would become pointless.<br>
   Processors would simplify considerably: no cache coherence protocols, far less speculation to hide memory latency, and a much shorter memory pipeline. This is exactly why persistent-memory and MRAM/ReRAM research attracts so much attention — <strong>the hierarchy is a workaround, not a goal</strong>, and a large part of what makes computers complicated is the effort spent hiding it.
   </details>

---

## 12. Practice — independent task

**Task:** Design the memory system for a small embedded processor and justify every choice numerically.

- **(a)** The processor runs at 200 MHz (5 ns cycle) and needs 64 KB of working memory. Using the module's latency figures, compute how many cycles a DRAM access would stall the CPU versus an SRAM access.
- **(b)** Using the F²/bit figures, compute the relative die area of 64 KB of SRAM versus 64 KB of DRAM. Which would you put on-chip?
- **(c)** The design also needs 4 MB of program storage, retained without power. Which technology, and why is neither SRAM nor DRAM viable?
- **(d)** Program storage is written once at manufacture but read constantly. Does SLC or TLC flash make more sense? Justify using both endurance and cost.
- **(e)** Model a cache: with 64 KB of on-chip SRAM as a cache in front of 16 MB of external DRAM, and a 95% hit rate, compute the *average* access latency in cycles. Compare with DRAM-only.
- **(f)** At what hit rate does the cache stop being worth its area? Assume the SRAM costs 23× the area per bit and you could have spent it on more DRAM.
- **(g)** Write `average_latency(hit_rate, fast_ns, slow_ns)` and sweep the hit rate from 50% to 99.9%. Plot or tabulate the result. Why is the curve so steep at the top end?

**Done when:** you have a justified technology choice for each of the three memories, an average-latency figure for your cache, and can explain why the last few percent of hit rate matter disproportionately.

<details><summary>Hint for (g), only if stuck</summary>
$t_{avg} = h \cdot t_{fast} + (1-h) \cdot t_{slow}$. With $t_{fast} = 1$ ns and $t_{slow} = 80$ ns, going from 95% to 99% takes you from 4.95 ns to 1.79 ns — <strong>nearly 3× faster from a 4-point improvement</strong>.<br>
The reason: at high hit rates the average is dominated by the <em>miss</em> term, and halving the miss rate halves that dominant term. This is why architects fight so hard for the last percent of hit rate, and why a small cache-unfriendly change in software can wreck performance out of all proportion to its size.
</details>

---

## 13. Tradeoffs and limits

- **Cell areas are approximate and process-dependent.** F² normalises across nodes but real cells vary with design rules, port counts and vendor. Use these for reasoning about ratios, not for datasheet numbers.
- **Modern NAND is 3D.** Cells are stacked in over 200 layers, so effective area per bit is far below the planar figures here. The floating-gate principle (or charge-trap variants) is unchanged.
- **Emerging technologies aim at the gap.** MRAM, ReRAM, phase-change and ferroelectric memories all target "fast, dense and non-volatile". None has yet displaced DRAM at scale.
- **This module ignores error correction entirely.** Server DRAM uses ECC, and flash relies on strong LDPC codes — without which TLC would be unusable. That is [[foundations/information-theory/06-error-correcting-codes|information-theory/error-correcting codes]].

---

## Before moving on

**This is the end of Part VII, and of the physics half of this course.** You are ready for the bridge when you can, closed-book:

- [ ] Draw an SRAM cell and explain why it is fast, large and volatile.
- [ ] Draw a DRAM cell, explain refresh, and explain why reads are destructive.
- [ ] Explain how a floating gate stores charge without power, and why flash wears out.
- [ ] Explain two-dimensional addressing and why sequential access beats random.
- [ ] **Derive** the memory hierarchy from cell costs rather than reciting it.

**Recap:** SRAM is module 24's bistable loop in six transistors — fast, self-sustaining, large and volatile. DRAM stores passive charge on a capacitor in ~6 F², 23× denser, but it leaks, so it needs refresh costing 0.6–4.6% of bandwidth, and its reads are destructive. Flash traps charge on a fully insulated floating gate, giving non-volatility at the cost of block erase and finite endurance, with multi-level cells trading noise margin for density. No technology is both fast and dense, and the memory hierarchy is the forced consequence.

**Next:** [[how-computers-work/07-the-bridge|Module 26 — The Bridge]]. You have now built every component of a computer from electric charge upward: switches, gates, arithmetic, and memory. The bridge is where you assemble them into a processor and connect to the existing courses that carry the story up to software.

---

## Related

- [[how-computers-work/index|How Computers Work — course index]]
- [[how-computers-work/06-memory/01-latches-and-flip-flops|Module 24]] — the bistable loop inside every SRAM cell
- [[how-computers-work/05-combinational/01-multiplexers-and-decoders|Module 20]] — the decoders addressing the array
- [[foundations/computer-architecture/08-the-memory-hierarchy|computer-architecture/memory hierarchy]] — where this hierarchy is exploited
- [[foundations/computer-architecture/09-caches-in-depth|computer-architecture/caches in depth]] — the machinery built on top of these tradeoffs
- [[foundations/dsa/04-data-structures/01-arrays|dsa/arrays]] — why locality beats complexity analysis
