# KiCad Basics & Schematic Fundamentals

> Covers KiCad terminology, the schematic workflow, and the standard circuits you'll see on every microcontroller schematic (power pins, decoupling caps, crystal oscillators, USB power).

---

## Table of Contents

1. [The Two Worlds of KiCad](#1-the-two-worlds-of-kicad)
2. [Symbol vs Footprint](#2-symbol-vs-footprint)
3. [The KiCad Workflow](#3-the-kicad-workflow)
4. [Key Terms Glossary](#4-key-terms-glossary)
5. [PCB Layers](#5-pcb-layers)
6. [STM32 Power Pins Explained](#6-stm32-power-pins-explained)
7. [Decoupling Capacitors](#7-decoupling-capacitors)
8. [Powering from USB](#8-powering-from-usb)
9. [Crystal Oscillators](#9-crystal-oscillators)
10. [How It All Looks in a Schematic](#10-how-it-all-looks-in-a-schematic)

---

## 1. The Two Worlds of KiCad

KiCad has two completely separate editors that work together:

```
Schematic Editor  →  "What connects to what" (logic)
PCB Editor        →  "Where things physically sit on the board" (layout)
```

You always start in the **Schematic Editor** and finish in the **PCB Editor**. The schematic is the blueprint; the PCB is the physical reality. You cannot skip straight to the PCB — the schematic defines all the connections.

---

## 2. Symbol vs Footprint

Every component has **two representations** and this is the concept that confuses everyone at the start:

| | Symbol | Footprint |
|---|---|---|
| **What it is** | A diagram of the component in the schematic | The physical copper pads on the PCB |
| **Lives in** | Schematic Editor | PCB Editor |
| **Example (resistor)** | A rectangle with two lines | Two copper pads 1.6mm apart |
| **Example (STM32)** | A box with 100 labeled pins | An LQFP-100 pad ring you solder to |

When you place a component, you're attaching a **symbol** AND a **footprint** to the same part. The symbol is what you see while drawing wire connections. The footprint is what gets placed on the physical board.

Think of it this way: a symbol is like a circuit diagram icon. A footprint is like the actual component sitting on a workbench.

---

## 3. The KiCad Workflow

```
1. New Project
       ↓
2. Schematic Editor
   — place component symbols
   — draw wires between pins
   — add power symbols (+3V3, GND, etc.)
       ↓
3. Assign footprints
   — link each symbol to its physical PCB pad pattern
       ↓
4. Run ERC (Electrical Rules Check)
   — catches wiring mistakes before moving on
       ↓
5. Update PCB from Schematic
   — pushes your connections to the PCB editor
       ↓
6. PCB Editor
   — arrange components on the board
   — draw copper traces between pads
       ↓
7. Run DRC (Design Rules Check)
   — catches layout mistakes (traces too close, pads too small, etc.)
       ↓
8. Export Gerbers
   — files sent to the factory (JLCPCB, PCBWay) to manufacture
```

---

## 4. Key Terms Glossary

| Term | What it means |
|---|---|
| **Net** | Any signal connection. "The SPI MOSI net" = every pin connected to that signal |
| **Netlist** | The complete list of all nets — what connects to what. KiCad generates this from the schematic |
| **Ratsnest** | Thin lines in the PCB editor showing connections not yet routed. Your job is to replace every ratsnest with a copper trace |
| **Trace** | A copper wire on the PCB |
| **Via** | A drilled hole that connects a trace on one layer to a trace on another layer |
| **Silkscreen** | White text/labels printed on top of the board (component names, polarity marks) |
| **Courtyard** | An invisible boundary around each component that prevents overlapping during placement |
| **ERC** | Electrical Rules Check — runs on the schematic. Catches unconnected pins, power errors |
| **DRC** | Design Rules Check — runs on the PCB. Catches traces too close, pads too small |
| **Gerber** | Standard file format sent to PCB manufacturers |
| **BOM** | Bill of Materials — the list of every component to buy |
| **Power symbol** | A special symbol (`+3V3`, `GND`) that connects nets without drawing a wire across the whole schematic |
| **PWR_FLAG** | A KiCad symbol that tells the ERC "yes, this power net is intentionally driven" — prevents false ERC errors |

---

## 5. PCB Layers

PCBs have layers. The ones you'll see most:

| Layer | What it is |
|---|---|
| `F.Cu` | Front copper — traces on the top of the board |
| `B.Cu` | Back copper — traces on the bottom |
| `F.Silkscreen` | Labels/text printed on the front |
| `F.Courtyard` | Component boundary on the front |
| `Edge.Cuts` | The outline of your board — where the factory cuts it |
| `In1.Cu`, `In2.Cu` | Internal copper layers (only on 4-layer+ boards) |

A standard 2-layer board uses `F.Cu` and `B.Cu`. Vias connect between them.

---

## 6. STM32 Power Pins Explained

### Always Start With the Datasheet and Reference Materials

Before wiring any microcontroller — STM32 or otherwise — the first thing you should do is download two documents from the manufacturer's website:

1. **The Datasheet** — the full technical specification of the chip. Pin definitions, electrical characteristics, absolute maximum ratings, timing diagrams. If you exceed any value in the "Absolute Maximum Ratings" table, you risk permanently damaging the chip.

2. **The Application Note** — ST publishes application notes specifically for hardware design. The most important one for STM32 is **AN4488** ("Getting started with STM32 hardware development"). It tells you exactly how to wire power pins, what decoupling capacitor values to use, how to handle the clock circuit, and common mistakes to avoid. It is essentially the official "how to design a PCB with this chip" guide.

3. **Reference Design / Evaluation Board Schematic** — ST publishes the full schematic of their own evaluation boards (Nucleo, Discovery). These are designed by ST's own engineers and are the most reliable reference you can get. When in doubt, copy exactly what they did.

**Where to find them:**
- Datasheet and application notes: [st.com](https://www.st.com) → search your chip → Documentation tab
- Nucleo board schematics: [st.com/en/evaluation-tools](https://www.st.com/en/evaluation-tools) → find your family → Resources tab

> This principle applies to every chip, not just STM32. Espressif publishes hardware design guides for the ESP32. Semtech publishes reference designs for the SX1262. WIZnet publishes reference schematics for the W5500. Always check what the manufacturer recommends before deciding how to wire something — they know their chip better than anyone.

---

When you open an STM32 symbol in KiCad you'll see a bunch of power-related pins that look confusing at first. Here's what every one of them means:

### VDD — Main Digital Power

**VDD** (Voltage Drain Digital) is the main power supply for the STM32's digital core and logic. It's typically **3.3V**.

Most STM32s have **multiple VDD pins** — they're all internally connected inside the chip, but Espressif and ST expect you to connect *every single one* of them externally. If you leave one floating, the chip behaves unpredictably. You'll see VDD1, VDD2, VDD3... — connect them all to your 3.3V rail.

### VDDA — Analog Power

**VDDA** (Voltage Drain Digital Analog) powers the analog subsystems: ADC, DAC, voltage reference, comparators.

Even though VDDA is also 3.3V, it's kept **separate from VDD** to isolate analog circuits from digital noise. In practice you connect it to the same 3.3V rail but through a small ferrite bead or LC filter, and give it its own set of decoupling capacitors.

### VDDIO / VDD_FT — I/O Port Power

**VDDIO** powers the GPIO banks. On some STM32 families (like the STM32H7), different GPIO banks can run at different voltages (1.8V or 3.3V). On simpler ones like the STM32F1/F4, it's just 3.3V like everything else.

### VSS / VSSA — Ground

**VSS** is digital ground. **VSSA** is analog ground. Like the supply pins, connect every VSS pin to GND. On good PCB layouts, VSSA connects to the analog ground plane and VSS to the digital ground plane, but they must be connected at a single point (star ground). For a beginner board, connecting them all to the same GND net is fine.

### VBAT — Backup Battery

**VBAT** powers the RTC (real-time clock) and backup registers when the main supply is off. You can connect a coin cell here (CR2032) to keep the clock running when the board is unpowered. If you don't need RTC backup, connect VBAT directly to 3.3V with a 100nF decoupling cap.

### VCAP — Internal Regulator Cap (STM32F4/F7 only)

Some STM32s have an internal voltage regulator that steps 3.3V down to ~1.2V for the CPU core. The **VCAP** pins are where this internal regulator's output capacitor connects. You must place a 2.2µF ceramic cap from VCAP to GND — the datasheet is very specific about this. Don't miss it or the chip won't start.

### NRST — Reset Pin

Active-low reset. Driving it LOW resets the chip. In schematics you connect a 100nF cap from NRST to GND (prevents false resets from noise) and optionally a reset button.

### BOOT0 — Boot Mode Selection

Controls what the STM32 does at power-up:
- **BOOT0 = LOW (GND):** Boot from Flash — runs your program. This is normal operation.
- **BOOT0 = HIGH (3.3V):** Boot from system memory (bootloader) — used for flashing via UART without a programmer.

In schematics you'll see a 10kΩ pull-down resistor on BOOT0 to GND (so it defaults to Flash boot), plus a jumper or button to pull it HIGH when you need to flash.

---

## 7. Decoupling Capacitors

This is what was happening when the tutorial was placing capacitors next to the VDD, VDDA pins. It's one of the most important concepts in hardware design.

### What They Do

Microcontrollers switch millions of logic gates per second. Each switching event draws a tiny spike of current. If you don't provide a local current reservoir right next to the chip, these spikes travel back through the power supply trace — creating voltage fluctuations (noise) that corrupt signals and cause the chip to malfunction.

A **decoupling capacitor** (also called a bypass capacitor) sits between VDD and GND right next to the chip. It acts as a tiny local battery: it charges up from the power rail, then discharges instantly to supply the current spike — before the noise can travel back down the trace.

### Values to Use

| Capacitor | Value | Purpose |
|---|---|---|
| Ceramic decoupling cap | **100nF (0.1µF)** | Filters high-frequency switching noise. One per VDD/VDDA pin |
| Bulk capacitor | **4.7µF or 10µF** | Handles lower-frequency ripple, one per power rail |
| VCAP cap (STM32F4) | **2.2µF ceramic** | Required by ST for the internal regulator — specific value, don't substitute |

### Placement Rule

In the schematic, these caps go between the VDD pin and GND. In the PCB layout, they must be placed **as close as physically possible** to the IC's power pin — ideally within 1-2mm. A decoupling cap on the other side of the board is almost useless.

### How It Looks in the Schematic

In the video, when he was connecting capacitors to VDD and VDDA pins, he was:
1. Placing a capacitor symbol (C) near the STM32
2. Connecting one end to the `+3V3` power symbol
3. Connecting the other end to `GND`
4. Doing this for *each* VDD/VDDA pin with its own cap

It can look messy on the schematic but it's mandatory. Professionals often put all the decoupling caps in a dedicated section of the schematic labelled "Power Decoupling."

---

## 8. Powering from USB

USB provides **5V** on its VBUS pin. The STM32 needs **3.3V**. So you need a voltage regulator between them.

### The Standard Circuit

```
USB VBUS (5V)
      │
      ├── 100nF cap to GND    (input decoupling)
      │
      ▼
  AMS1117-3.3                 (3.3V LDO voltage regulator)
      │
      ├── 10µF + 100nF cap to GND    (output decoupling)
      │
      ▼
   +3V3 rail ──────────────── STM32 VDD, VDDA, VDDIO
```

**AMS1117-3.3** is the most common LDO (Low Dropout Regulator) used in STM32 hobby/dev boards. It's a 3-pin package: IN, GND, OUT. 800mA max output. Cheap and widely available.

When the tutorial said "he is using USB" — he meant the 5V from the USB connector is going into a 3.3V regulator, and the 3.3V output is being fed to the STM32's power pins.

### USB Data Lines (if using USB for communication)

If the STM32 also uses USB for data (CDC, HID, etc.):
- **D−** and **D+** connect to the STM32's USB data pins (usually labeled `USB_DM` and `USB_DP`)
- A **1.5kΩ pull-up** on D+ signals to the host that this is a Full-Speed USB device
- Some STM32s (like the STM32F103) handle this pull-up internally; others need an external resistor

---

## 9. Crystal Oscillators

### Why a Crystal?

The STM32 has an internal RC oscillator, but it drifts with temperature — it's inaccurate. For USB (which needs tight timing), UART at high baud rates, or any real-time clock, you need an external crystal for precision frequency reference.

### HSE — High Speed External Crystal

Used to clock the main CPU. Typically **8 MHz** or **25 MHz**. Connects between **OSC_IN** and **OSC_OUT** pins on the STM32. Two load capacitors (typically **12–22 pF**, check your crystal's datasheet for exact value) go from each crystal pin to GND.

```
OSC_IN ──┬── crystal ──┬── OSC_OUT
         │             │
        C1            C2          (load capacitors, e.g. 12pF each)
         │             │
        GND           GND
```

The crystal itself is a small silver can (or SMD package) that oscillates mechanically at a precise frequency. The load capacitors tune the oscillation.

### LSE — Low Speed External Crystal

A **32.768 kHz** crystal for the RTC (real-time clock). Connects to **OSC32_IN** and **OSC32_OUT**. Same two-cap circuit, just a different (smaller) crystal. The specific frequency 32.768 kHz = 2^15 Hz — it divides down cleanly to 1 Hz for timekeeping.

### What the Tutorial Was Showing

When he was connecting the crystal oscillator:
1. He placed a crystal symbol between OSC_IN and OSC_OUT
2. He placed two small capacitors (C) from each crystal pin to GND
3. The crystal + two caps is a complete, self-contained circuit — nothing else needed except good PCB placement (keep the crystal and its caps close to the STM32, away from noisy signals)

### No Crystal? Use the HSI

If your design doesn't need precise timing (no USB, no high baud rate UART, no RTC), you can skip the external crystal entirely and use the STM32's internal HSI (High Speed Internal) oscillator. It's less accurate but works fine for basic GPIO toggling, sensor reading, etc.

---

## 10. How It All Looks in a Schematic

A minimal STM32 schematic has these sections:

```
┌─────────────────────────────────────────────────────┐
│  POWER SECTION                                      │
│  USB 5V → AMS1117-3.3 → +3V3 net                   │
│  Decoupling caps on input and output of LDO         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  STM32 IC                                           │
│  All VDD pins → +3V3 (each with 100nF cap to GND)  │
│  All VSS pins → GND                                 │
│  VDDA → +3V3 (with 1µF + 10nF filtered caps)       │
│  VBAT → +3V3 (with 100nF cap)                      │
│  VCAP → 2.2µF cap to GND (F4/F7 only)              │
│  NRST → 100nF cap to GND + reset button            │
│  BOOT0 → 10kΩ to GND + jumper to +3V3              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  CLOCK SECTION                                      │
│  8MHz crystal between OSC_IN / OSC_OUT              │
│  12pF load caps to GND on each crystal pin          │
│  (optional) 32.768kHz crystal on OSC32_IN/OUT       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  USB CONNECTOR (if used)                            │
│  VBUS → power input                                 │
│  D+ / D− → STM32 USB pins                          │
│  1.5kΩ pull-up on D+                               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  DEBUG / PROGRAMMING                                │
│  SWD header: SWDIO, SWDCLK, GND, +3V3              │
│  (4-pin or 10-pin SWD connector)                   │
└─────────────────────────────────────────────────────┘
```

Every STM32 schematic you ever see will have all of these sections — just the peripheral section changes based on what the board actually does. Get these five sections right and the chip will start.
