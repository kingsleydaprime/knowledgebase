# Electricity

**[Beginner]** — The foundation everything else stands on: voltage, current, resistance, and the components that shape them. If Ohm's law isn't reflexive yet, this is the note to read twice.

Before you touch a microcontroller or antenna, you need to internalize three things: **voltage**, **current**, and **resistance**. Everything else is built on top of these.

## The Water Analogy (and Why It's Actually Useful)

Think of electricity flowing through a wire like water flowing through a pipe:

| Electricity | Water equivalent |
|---|---|
| **Voltage (V)** | Water pressure |
| **Current (A)** | Flow rate (litres per second) |
| **Resistance (Ω)** | Pipe width / friction |
| **Power (W)** | Work done per second |

- **Voltage** is the *potential difference* — the "push" that wants to move electrons from one place to another. A 9V battery has more push than a 3.3V one.
- **Current** is how many electrons actually flow. Measured in Amperes (A). Your USB port delivers up to 500mA (0.5A). Your phone charger might do 3A.
- **Resistance** is how much a component fights current. A resistor is literally a component designed to resist. Measured in Ohms (Ω).

## Ohm's Law — The One Formula You Must Know

```
V = I × R
```

That's it. Every other formula in basic electronics is derived from this.

- If you know voltage and resistance, you can find current: `I = V / R`
- If you need a specific current through an LED, you calculate the resistor: `R = V / I`

**Practical example:** You have a 5V pin and an LED that needs 20mA (0.02A) to light up. The LED itself drops ~2V, leaving 3V across your resistor. What resistor do you need?

```
R = 3V / 0.02A = 150Ω
```

Use a 150Ω resistor. Miss this step and you burn the LED in about 2 seconds.

## Power

```
P = V × I
```

Power tells you heat. If something dissipates more power than it's rated for, it gets hot and dies. A resistor rated for 0.25W (quarter watt) handling 0.5W will toast itself.

## AC vs DC

- **DC (Direct Current)** — current flows in one direction. Batteries, USB, GPIO pins. Everything in embedded systems is DC.
- **AC (Alternating Current)** — current reverses direction at a frequency (50Hz in Nigeria/EU, 60Hz in the US). Your wall socket is AC. Power supplies convert AC to DC for your devices.

## Voltage Regulators — Making One Voltage from Another

Almost every real circuit needs multiple voltages. Your USB port gives you 5V, but the STM32 or ESP32 needs 3.3V, and a cellular module might need 3.8V. Voltage regulators solve this — they take a higher input voltage and output a stable, lower voltage regardless of how much current the load draws.

There are two main types:

**LDO (Low Dropout Regulator)**
A linear regulator — it literally burns off the excess voltage as heat. Simple, cheap, no switching noise. "Low Dropout" means it can regulate even when the input is only slightly higher than the output (low headroom).

```
IN (5V) ──► [LDO] ──► OUT (3.3V)
                │
               GND
               (heat)
```

The wasted power = (V_in - V_out) × Current. Running 500mA through a 5V→3.3V LDO wastes (5 - 3.3) × 0.5 = **0.85W as heat**. Fine for small currents, inefficient for large ones. Common parts: AMS1117, TLV1117, AP2112.

**Buck Converter (Switching Regulator)**
Rapidly switches a transistor on and off, then uses an inductor and capacitor to smooth the result. Much more efficient (85–95%) because instead of burning the excess as heat, it converts it. Noisier than an LDO due to the switching, and needs more external components (inductor, caps). Used when current is high or battery life matters. Common parts: MP2307, TPS54360, LM2596.

| | LDO | Buck Converter |
|---|---|---|
| Efficiency | Low (wastes heat) | High (85-95%) |
| Noise | Very low (no switching) | Higher (needs filtering) |
| Components needed | Just caps | Inductor + caps + sometimes resistors |
| Best for | Low current, analog supplies | High current, battery-powered |

For the IoT Bridge: we use LDOs (TLV1117-33 and AP2112K-3.8) because the currents are manageable and we want clean, quiet power rails.

## Power OR'ing — Combining Two Power Sources Safely

When a device can be powered from two different sources (e.g., USB-C and PoE), you need a way to combine them so:
- Whichever source is present powers the board
- If both are present, they don't fight each other or push current back into the inactive source
- Swapping sources doesn't glitch the board

The naive solution — just connect both sources together — is dangerous. If USB gives you 5.0V and PoE gives you 5.1V, the higher one will try to push current backwards into the lower one. In the worst case this damages components. Even if nothing breaks, the voltage on the rail becomes unpredictable.

**Ideal Diode Controller**

The clean solution uses a pair of **ideal diode controllers** (like the LM66100). A regular diode blocks reverse current but wastes ~0.6V as a forward voltage drop. An ideal diode controller uses a MOSFET instead — which has near-zero voltage drop when conducting — but controls it with a circuit that mimics a diode's one-way behavior.

Two ideal diode controllers in an ORing configuration:

```
Source A (5.0V) ──► [LM66100 #1] ──┐
                                     ├──► Output rail (5V)
Source B (5.1V) ──► [LM66100 #2] ──┘
```

- Source B (5.1V) wins — its LM66100 conducts, feeding the rail
- LM66100 #1 detects that the output (5.1V) is higher than its input (5.0V) and switches off, blocking reverse current into Source A
- If Source B disappears, Source A's LM66100 instantly takes over
- No glitch, no reverse current, no damage

## Ground

Ground (GND) is the reference point — the "zero" that all voltages are measured against. It's not a mystical sink, it's just a common reference. If two circuits don't share a common ground, they can't communicate reliably. This trips up beginners constantly.

## How Does Electricity Move So Fast?

Here's something that breaks most people's mental model: when we say electricity travels "at nearly the speed of light," we do NOT mean electrons are sprinting down the wire. Individual electrons in a copper wire actually crawl at roughly **3 inches per hour** — this is called **drift velocity**. Embarrassingly slow.

So how does flipping a switch on one end of a 100-meter wire turn on a light almost instantly?

**The Newton's Cradle Effect.**

Imagine a pipe stuffed completely full of marbles from end to end — no gaps. If you push one marble in on the left, a marble pops out immediately on the right. The individual marbles barely moved; what traveled was the *wave of pressure* through the chain.

Copper wire works identically. The wire is already packed dense with free electrons — roughly 8.5 × 10²⁸ electrons per cubic meter. The moment you apply a voltage, you're not waiting for electrons to travel from source to load. You're creating an **electromagnetic wave** that propagates through the electric field surrounding the wire. That wave travels at **50% to 90% of the speed of light** depending on the material (this ratio is called the velocity factor).

This is why signal integrity matters in high-speed circuits. At low frequencies, you barely notice. But once you're dealing with GHz-speed signals, the physical length of a wire becomes a significant fraction of the signal's wavelength — and things get complicated fast (reflections, impedance matching, transmission line effects).

## Transistors — The Switch That Changed Everything

Understanding transistors is understanding *why* modern electronics can do what they do. A transistor is a microscopic electronic switch — no moving parts, no mechanical contact, just a tiny voltage controlling whether current can flow through a pathway.

The basic idea: a transistor has three terminals. In a **BJT (Bipolar Junction Transistor)**, they're called Base, Collector, and Emitter. A small current into the Base controls a much larger current from Collector to Emitter — this is *amplification*. In a **MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor)**, the terminals are Gate, Drain, and Source. A voltage on the Gate controls current flow — and crucially, the Gate draws almost no current itself (it's capacitively isolated). This is why MOSFETs dominate digital logic.

**CMOS Logic** (Complementary MOS) is what every modern chip uses. A CMOS gate pairs two MOSFETs: an N-type (conducts when Gate is HIGH) and a P-type (conducts when Gate is LOW). They work in complementary opposition — when one is on, the other is off. The result: almost zero static power consumption, because there's never a direct path from power to ground in steady state. Power is only consumed during the switching transition. This is why battery-powered devices can sleep at microamp levels.

**Speed** comes from size. A transistor switches by charging or discharging its Gate capacitance. Smaller transistor = smaller capacitance = less charge needed = faster switching. Modern chips (like the ones in your phone) use transistors measured in nanometers — Apple's A18 chip uses a 3nm process, meaning transistor features are ~3 nanometers wide. For reference, a strand of DNA is ~2.5nm wide. At these scales, a single chip contains **tens of billions of transistors**, each switching billions of times per second (GHz clock speeds).

So here's the full picture: electricity provides a near-light-speed electromagnetic wave of energy. Billions of transistors act as hyper-fast gates, opening and closing in orchestrated patterns to shape that energy into **1s and 0s** — binary data. The clock signal is what synchronizes them all: a square wave oscillating at the chip's rated frequency, telling every transistor when to sample its inputs and latch its output. At 240 MHz (ESP32), that synchronization pulse fires 240 million times every second.

This is why clock speed isn't the only thing that matters for performance — pipeline depth, instruction-level parallelism, cache architecture, and branch prediction all affect how much actual work gets done per clock cycle. MHz/GHz is just the metronome. The orchestra is everything else.

## Capacitors — Storing and Releasing Energy

A **capacitor** stores electrical energy in an electric field between two conductive plates separated by an insulating layer (called a dielectric). Unlike a battery — which stores energy chemically and releases it slowly — a capacitor stores energy electrically and can release it almost instantaneously. That difference in speed is exactly what makes capacitors so useful in electronics.

The unit of capacitance is the **Farad (F)**, but a full Farad is enormous. In practice you'll work with:
- **µF (microfarad)** — 10⁻⁶ F. Bulk capacitors: 10µF, 100µF.
- **nF (nanofarad)** — 10⁻⁹ F. Mid-range filtering: 10nF, 100nF.
- **pF (picofarad)** — 10⁻¹² F. High-frequency filtering, crystal load caps: 12pF, 22pF.

Capacitors have two key behaviors that matter in circuits:

1. **They block DC but pass AC.** Once a capacitor is fully charged to a DC voltage, no more current flows. But for an alternating or changing signal, the capacitor continuously charges and discharges, so current flows. This is the basis of filtering.

2. **They resist sudden voltage changes.** A capacitor can't change its voltage instantaneously — it has to charge or discharge first. This makes them excellent at smoothing out voltage spikes and dips.

## Decoupling Capacitors — The Most Important Caps You'll Place

You will see these on *every single* professional PCB, right next to every IC's power pins. Understanding them separates someone who copies schematics from someone who understands them.

**The problem they solve:**

A microcontroller switches millions of logic gates every clock cycle. Each switching event pulls a sudden spike of current from the power supply. Think of a chip running at 240 MHz — it's drawing 240 million tiny current pulses per second. That's not a smooth, steady current draw. It's a continuous series of rapid spikes.

Those spikes travel back down the power supply trace toward your voltage regulator. The trace has resistance and inductance — so as the current spikes, the voltage on the power pin *dips* momentarily. These dips are called **supply noise** or **power rail ripple**. If the dip is bad enough, the chip reads its own VDD pin as a logic LOW — and it crashes, resets, or produces corrupt data.

**The solution:**

Place a capacitor physically right next to the chip's power pin, connected between VDD and GND. When the chip pulls a current spike, the capacitor discharges *locally* to supply that spike — before the noise has a chance to propagate back down the trace. The power supply then recharges the capacitor slowly between spikes. The chip never sees the dip.

```
Power supply (far away)
       │
       │  (long trace — has resistance and inductance)
       │
       ├──── 100nF cap ──── GND    ← local charge reservoir
       │
       ▼
   Chip VDD pin
```

This is a **decoupling capacitor** (also called a bypass capacitor). It decouples the chip's power pin from the noise on the supply line.

**What values to use and why:**

| Cap value | What it handles | One per... |
|---|---|---|
| **100nF ceramic** | High-frequency switching noise (MHz range) | Every VDD/VDDA/VDDIO pin on the IC |
| **10µF ceramic or electrolytic** | Lower-frequency ripple, bulk charge reservoir | Each power rail entering the board |
| **1µF ceramic** | Mid-frequency filtering, analog supply pins (VDDA) | VDDA pins on STM32 / ADC power pins |

The 100nF (0.1µF) ceramic cap is the universal decoupling cap. You'll see it everywhere. It's not magic — it's physics. The ceramic dielectric has very low inductance, which means it can respond to fast transients. Electrolytic caps are cheaper and come in larger values but are too slow for high-frequency decoupling.

**The golden rule of placement:**

A decoupling cap on the other side of the board is almost useless. The whole point is to minimize the length of the path between the cap and the chip's pin — every millimeter of trace adds inductance that slows the cap's response. In PCB layout, place decoupling caps within **1–2mm of the IC pin they serve**, on the same side of the board.

**Analog supplies (VDDA) need extra attention:**

Analog circuits (ADCs, DACs) are sensitive to noise in the µV range. For VDDA pins, you often add a **ferrite bead** in series between the main 3.3V rail and the VDDA pin, with the decoupling caps on the VDDA side. The ferrite bead acts like a frequency-selective resistor — it passes DC cleanly but chokes high-frequency noise from the digital side before it can reach the analog circuits.

```
+3V3 ──── ferrite bead ──── VDDA ──── 1µF + 100nF caps to GND
```

**In the schematic:**

When a tutorial places capacitors directly on an STM32's VDD or VDDA pins — one end to the power net, other end to GND — that's exactly this. It can look cluttered but every single one serves a purpose. Skip them and your chip will work fine on a bench with a clean lab supply and fail mysteriously in the field.

---

## Related
- [[hardware/02-digital-and-analog|Digital vs Analog]] — turning these voltages into numbers
- [[hardware/03-embedded-systems|Embedded Systems]] — what runs on the power you've just designed
- [[hardware/10-kicad-basics|KiCad Basics]] — decoupling and power rails as drawn on a real board
- [[projects/iot-bridge-pcb/component-selection|IoT Bridge — component selection]] — these tradeoffs argued under real constraints
