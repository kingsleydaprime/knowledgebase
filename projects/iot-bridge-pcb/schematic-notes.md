# IoT Bridge — Schematic Notes

> Running log of decisions, wiring details, and gotchas encountered while drawing the schematic. Update this as you go.

---

## Progress

- [ ] Power Section
- [x] ESP32-C6 — 3V3 supply + decoupling caps (10µF + 100nF)
- [x] ESP32-C6 — EN/CHIP_PU circuit (10kΩ pull-up + 100nF cap)
- [x] ESP32-C6 — BOOT/GPIO9 circuit (10kΩ pull-down + SW_Push button)
- [x] ESP32-C6 — PWR_FLAG on +3V3 and GND nets
- [x] ESP32-C6 — GPIO net labels
- [x] ESP32-C6 — No-connect markers on unused pins
- [x] USB-C Connector
- [ ] SX1262 (LoRa)
- [ ] W5500 (Ethernet)
- [ ] SIM7080G (Cellular)
- [ ] USB-C Connector
- [ ] MicroSD Slot
- [ ] User Interface (Button + LED)
- [ ] SWD Debug Header
- [ ] ERC clean (0 errors)

---

## Section 1 — Power

### What to place in KiCad

**USB-C Connector (USB4105-GF-A)**
- VBUS pin → fuse (500mA polyfuse) → power net labeled `USB_5V`
- D+ and D- → wire to MCU (label them `USB_DP` and `USB_DM`)
- CC1 and CC2 → each gets a **5.1kΩ resistor to GND** (tells the USB host this is a device that wants 5V/900mA)
- SHIELD / GND pins → GND

**LM66100 #1 (PoE 5V side)**
- IN → net labeled `POE_5V` (comes from TPS23730 output)
- OUT → net labeled `+5V` (system rail)
- GND → GND
- CE → GND (CE is active-low — pulling LOW keeps chip always enabled)
- ST → no-connect (status output, not needed)
- Add 100nF decoupling cap from IN to GND and OUT to GND

**LM66100 #2 (USB-C 5V side)**
- IN → `USB_VBUS`
- OUT → `+5V` (same system rail as above — this is the OR'ing)
- GND → GND
- CE → GND (active-low — must be LOW to enable, NOT tied to VOUT)
- ST → no-connect
- Add 100nF decoupling cap from IN to GND and OUT to GND

**TPS23730 (PoE PD Controller)**
- Connects to the RJ45 PoE pairs (pins from the magjack)
- Outputs regulated 5V → label `POE_5V`
- Needs external transformer (add transformer symbol, label primary/secondary)
- Refer to TPS23730 datasheet application circuit — copy it exactly

**TLV1117-33 (3.3V LDO)**
- IN → `+5V`
- OUT → `+3V3` power net
- GND → GND
- Input cap: 10µF electrolytic + 100nF ceramic (IN to GND)
- Output cap: 10µF electrolytic + 100nF ceramic (OUT to GND)

**AP2112K-3.8 (3.8V LDO for cellular)**
- IN → `+5V`
- OUT → `+3V8` power net (only goes to SIM7080G)
- GND → GND
- Input cap: 1µF ceramic (IN to GND)
- Output cap: 1µF ceramic (OUT to GND)

### Power nets (global labels to use consistently)
| Net name | Voltage | Powers |
|---|---|---|
| `USB_5V` | 5V | From USB-C VBUS, before OR'ing |
| `POE_5V` | 5V | From TPS23730 output, before OR'ing |
| `+5V` | 5V | System rail after OR'ing |
| `+3V3` | 3.3V | ESP32, W5500, SX1262, SD card |
| `+3V8` | 3.8V | SIM7080G only |
| `GND` | 0V | Everything |

### Decisions made
- LoRa frequency: **868 MHz** (Nigeria is Region 1 — 868 MHz band)
- USB-C: 5V default only, no PD negotiation chip needed
- CC resistors: 5.1kΩ to GND on both CC1 and CC2

### Gotchas
- **PWR_FLAG rule**: only add it when no component output drives that net. If an LDO VOUT is already on the net, no PWR_FLAG needed — adding one causes "two power outputs" ERC error
- Nets needing PWR_FLAG in this design: `USB_VBUS` (from external cable), `POE_5V` (until PPS23730 is wired), `SIM_VCC` (SIM_VDD pin type is "Output" not "Power output")
- Nets NOT needing PWR_FLAG: `+3V3` (TLV1117 VOUT), `+3V8` (AP2112K VOUT), `+5V` (LM66100 VOUTs), `GND` (power symbol)
- Two LM66100 VOUTs on `+5V` will always give "two power outputs" ERC error — this is intentional OR-ing, exclude it from ERC
- The PPS23730 application circuit is complex — download the datasheet and copy the reference design exactly, don't freehand it
- LM66100 max current is 1.5A — total board current at peak must stay under 1.5A per source or use a higher-rated ORing solution

---

## Section 2 — ESP32-C6 MCU

> Fill in as you work through this section

### What to place
- ESP32-C6-1U-N8 symbol (may need to create custom symbol from datasheet)
- All VDD/VDDIO pins → `+3V3` (100nF decoupling cap per pin, placed right at the pin)
- All GND pins → GND
- EN (enable) pin → 10kΩ pull-up to `+3V3` + 100nF cap to GND
- GPIO0 (boot mode) → 10kΩ pull-down to GND + optional button to `+3V3`

### SPI bus assignments
| Signal | ESP32 GPIO | Device |
|---|---|---|
| MOSI | GPIO6 | W5500, SX1262, SD card (shared) |
| MISO | GPIO7 | W5500, SX1262, SD card (shared) |
| SCK | GPIO8 | W5500, SX1262, SD card (shared) |
| CS_ETH | GPIO2 | W5500 chip select (moved from GPIO9 — see note) |
| CS_LORA | GPIO10 | SX1262 chip select |
| CS_SD | GPIO11 | MicroSD chip select |

> **Note — why not GPIO9 for CS_ETH:** GPIO9 is a strapping pin read at boot (LOW = normal flash boot). We use it for the BOOT button circuit with a 10kΩ pull-down. CS lines must idle HIGH (not selected), which conflicts with a pull-down to GND. GPIO2 has no strapping function and is a clean replacement.

### UART assignment (for SIM7080G)
| Signal | ESP32 GPIO |
|---|---|
| UART_TX | GPIO4 |
| UART_RX | GPIO5 |

### USB
- GPIO13 (USB_DP) → D+ on USB-C connector
- GPIO12 (USB_DM) → D- on USB-C connector

---

## Section 3 — SX1262 (LoRa)

### Key wiring — SPI and control
- NSS (19) → CS_LORA (GPIO10)
- SCK (18) → SPI_SCK (GPIO8)
- MOSI (17) → SPI_MOSI (GPIO6)
- MISO (16) → SPI_MISO (GPIO7)
- RESET (15) → LORA_RESET (GPIO15) — active low
- BUSY (14) → LORA_BUSY (GPIO18)
- DIO1 (13) → LORA_DIO1 (GPIO19) — TX/RX done interrupt
- DIO2 (12) → 100Ω resistor → PE4259 CTRL pin — controls RF switch (TX vs RX path)
- DIO3 (6) → no-connect

### Key wiring — power
- VDD_IN (1) → +3V3, 100nF to GND
- VBAT (10) → +3V3, 100nF + 10µF to GND
- VBAT_IO (11) → +3V3, 100nF to GND
- VR_PA (24) → +3V3, 100nF to GND
- VREG (7) → 100nF cap to GND only (internal regulator output — do not drive)
- DCC_SW (9) → 15µH inductor → +3V3 (DC-DC switch node)
- GND (2) → GND

### Key wiring — crystal
- XTA (3) → 32 MHz crystal pin + 10pF cap to GND
- XTB (4) → 32 MHz crystal pin + 10pF cap to GND
- Crystal case pins → GND
- Use Crystal_GND24 symbol in KiCad

### Key wiring — RF section (copy from SX1262 datasheet section 14.6.2)
- RFO (23) → matching network (L, C per datasheet) → PE4259 RF1 (pin 1)
- RFI_N (22) + RFI_P (21) → their own matching network → PE4259 RF2 (pin 3)
- PE4259 RFC (pin 5) → C8, L5, C9, C10 output matching → Conn_Coaxial pin 1 (ANT_NET)
- PE4259 CTRL (pin 4) → 100Ω resistor → DIO2 (SX1262 pin 12)
- PE4259 CTRL/VDD (pin 6) → +3V3 (no decoupling cap — logic supply only)
- PE4259 GND (pin 2) → GND
- Conn_Coaxial pin 1 (centre/signal) → ANT_NET
- Conn_Coaxial pin 2 (shield) → GND
- Download PE4259 symbol from SnapEDA

### Gotchas
- DIO2 is NOT no-connect — it controls the PE4259 RF switch
- DCC_SW inductor is **15µH** (from datasheet reference design), not 22nH
- Copy the RF matching network component values exactly from datasheet section 14.6.2 — do not guess

---

## Section 4 — W5500 (Ethernet)

### Key wiring
- SCSn → `CS_ETH` (GPIO2)
- SCLK → `SPI_SCK`, MOSI → `SPI_MOSI`, MISO → `SPI_MISO`
- RSTn → `ETH_RESET` (GPIO20) — active low
- INTn → `ETH_INT` (GPIO21) — interrupt
- RSVD → GND (per datasheet)
- EXRES1 → 12.4kΩ resistor → GND (sets internal reference current — value must be exactly 12.4kΩ)
- PMODE0, PMODE1, PMODE2 → all `+3V3` (sets 100Base-T full duplex auto-negotiation)
- VBG, TOCAP, 1V2O → decoupling cap to GND only (internal voltage outputs — never drive them)
- 25 MHz crystal (Crystal_GND24) between XTLIN and XTLOUT, 20pF load caps on each pin, case pins → GND

### RJ45 — use RJ45_Hanrun_HR911105A (MagJack with integrated magnetics)
- W5500 TXOP / TXON → MagJack TX+ / TX-
- W5500 RXIP / RXIN → MagJack RX+ / RX-
- MagJack CT (centre tap) pins → `+3V3` through 49.9Ω resistor (copy from W5500 datasheet)
- MagJack GND / shield → GND
- LED pins → no-connect for prototype

### Gotchas
- EXRES1 must be exactly 12.4kΩ — do not substitute
- VBG/TOCAP/1V2O are outputs — cap to GND only, never connect to a power rail
- Centre tap resistor value comes from the W5500 datasheet application circuit — copy it exactly

---

## Section 5 — SIM7080G (Cellular)

> Fill in as you work through this section

### Key wiring
- UART TX/RX → ESP32 GPIO4/GPIO5
- PWRKEY → GPIO22 — pulse LOW for 1 second to power on/off module
- Power supply → `+3V8` rail (NOT 3.3V)
- SIM card holder → SIM_VCC, SIM_RST, SIM_CLK, SIM_DATA pins on module
- Main antenna → U.FL connector (LTE)
- GNSS antenna → separate U.FL connector

---

## Section 6 — USB-C, MicroSD, Button, LED, SWD

> Fill in as you work through this section

---

## Learning Notes (merged from `learning.md`, split out 2026-07-27)

> The sections below were moved here from the old flat `learning.md` file when learning notes were split into topic-scoped files. Content is verbatim from the original — only heading levels were adjusted to nest under this section.
>
> Original file header, preserved verbatim: "IoT Bridge — Project Learning Notes. This file is for understanding, not presenting. Every time something in this project makes you ask 'wait, why?' — the answer goes here. Written in plain language, tied to real decisions made in this project."

### How Does SPI Work? What Are MOSI, MISO, SCK, and CS?

SPI (Serial Peripheral Interface) is how the ESP32 talks to the W5500, SX1262, and MicroSD card. "Serial" means data is sent one bit at a time over a single wire.

**The four wires:**

**SCK (Serial Clock)** — the master (ESP32) pulses this at a fixed rate (16 MHz on our board). Every pulse = one bit transferred. Both sides watch SCK to stay in sync. Without it, neither side would know when to read a bit.

**MOSI (Master Out Slave In)** — the wire where ESP32 sends data *to* a chip. One direction only: ESP32 → chip.

**MISO (Master In Slave Out)** — the wire where a chip sends data *back* to the ESP32. One direction only: chip → ESP32. MOSI and MISO work simultaneously (full duplex) — while sending a command, the chip is already sending back its response.

**CS (Chip Select)** — each slave chip has its own CS wire. A chip only responds when its CS is pulled LOW. HIGH = ignore everything. This is how three chips share the same MOSI/MISO/SCK wires without interfering with each other:

```
Pull CS_LORA LOW  → SX1262 listens, W5500 and SD card ignore
Pull CS_ETH LOW   → W5500 listens, SX1262 and SD card ignore
Pull CS_SD LOW    → MicroSD listens, SX1262 and W5500 ignore
```

CS is "active LOW" — selected when LOW, ignored when HIGH. This is why you sometimes see it written as `/CS`, `~CS`, or `NSS`.

**Do the chips have names/addresses?** No — they're selected purely by which CS line the ESP32 pulls LOW. No addresses involved. This is different from I2C where every device has a 7-bit address embedded in the message itself.

**Why 16 MHz on our board?** The SX1262 has a maximum SPI clock of 16 MHz. Since all three devices share the same SCK, the slowest device sets the speed for everyone.

### When do you use PWR_FLAG? When a resistor? When a decoupling cap? How do you pick values?

#### PWR_FLAG

PWR_FLAG is **KiCad-only** — it has zero effect on the actual circuit. It tells KiCad's ERC that a net is being powered even when no output pin on the schematic is visibly driving it.

**The rule:**
- Net has a real power output pin (LDO VOUT, regulator output) → **no PWR_FLAG needed**
- Net is powered from outside the schematic (USB cable, external supply, section not yet drawn) → **add PWR_FLAG**
- GND → **no PWR_FLAG needed** (GND power symbol is already a power output type)

One PWR_FLAG per net is enough — place it anywhere on that net.

> If you add a PWR_FLAG to a net that already has a real VOUT pin, KiCad will throw "two power outputs connected" error. Remove the PWR_FLAG in that case.

#### Resistors — when and what value

| Situation | Resistor? | Value | Reason |
|---|---|---|---|
| LED in series | Yes | 330Ω | Limits current so the LED doesn't burn out |
| Signal line that nothing drives at rest | Yes — pull-up or pull-down | 10kΩ | Holds line at a known HIGH or LOW |
| Strapping / BOOT / EN pins | Yes | 10kΩ | Industry default for startup pin biasing |
| USB-C CC pins | Yes | 5.1kΩ | USB-C specification mandates this exact value |
| EXRES1 on W5500 | Yes | 12.4kΩ | W5500 datasheet mandates this exact value |
| IC power pin | No | — | Connect directly to the power rail |
| SPI / UART signal line | Usually no | — | These are actively driven signals |

**How to calculate the value:**
- **Datasheet specifies it** → use that exact value, always
- **Pull-up or pull-down** → default **10kΩ** (not too much current waste, strong enough to hold the line)
- **LED current limiting** → `R = (Vsupply − Vforward) ÷ Idesired`
  - Example: 3.3V supply, LED forward voltage 2.0V, want 10mA → `(3.3 − 2.0) ÷ 0.01 = 130Ω` → round up to **330Ω** for safety

#### Decoupling capacitors — when and what value

Every IC power pin gets a 100nF cap placed right next to it. Every time a chip switches a logic gate, it pulls a brief current spike from its supply. The cap sits right there and supplies that spike instantly, before the supply voltage can dip. Without it, the chip can glitch or crash.

| Situation | Cap? | Value |
|---|---|---|
| Any IC VDD / VCC / VBAT / VDDIO pin | Yes | 100nF ceramic |
| High-current IC (e.g. SIM7080G cellular) | Yes — also add bulk | 100nF + 100µF electrolytic |
| RF chip power pin (SX1262) | Yes | 100nF + 10µF |
| LDO regulator input | Yes | 10µF + 100nF |
| LDO regulator output | Yes | 10µF + 100nF |
| Crystal pin (load caps) | Yes | 10–20pF (from crystal datasheet) |
| Internal regulator output pin (e.g. VREG on SX1262) | Yes — stabilising only | 100nF to GND, nothing else |
| Signal / GPIO pin | No | Caps filter signals — wrong place |
| Passive component (resistor, another cap) | No | — |

**How to know the value:**
- **100nF** → universal default for IC decoupling. Use when the datasheet doesn't specify.
- **10µF** → bulk capacitor, handles slower larger current spikes. Pair with 100nF on power sections.
- **100µF** → high current draws like the cellular module (can spike 2A).
- **1µF** → simple low-power LDOs like the AP2112K.
- **10–20pF** → crystal load caps. Use the value in the crystal's datasheet.

**The datasheet always wins.** 100nF is only the fallback when nothing is specified.

### Why does the MCU need so many capacitors on its power pins?

Every time a microcontroller switches a logic gate (which happens billions of times per second), it pulls a tiny spike of current. At 160 MHz (ESP32-C6's clock speed), that's 160 million spikes per second. Those spikes travel back up the power trace and cause tiny voltage dips on the chip's VDD pin.

If the dip is bad enough, the chip reads its own power supply as a logic LOW — and it crashes or corrupts data. A 100nF ceramic capacitor placed right next to the VDD pin acts as a local charge reservoir: it instantly supplies the current spike before the dip can happen, then slowly recharges between spikes.

**This is why placement matters in PCB layout** — a decoupling cap on the other side of the board doesn't help, because the trace between the cap and the pin is too long (adds inductance, slows response). Place them within 1–2mm of the pin.

The ESP32-C6 has multiple VDD and VDDIO pins — each one needs its own 100nF cap. It looks excessive on the schematic but every single one matters.

### Why two separate LDOs (3.3V and 3.8V)? Why not one supply?

The SIM7080G cellular module requires 3.0–4.2V — it cannot run on 3.3V or 5V. 3.8V is the sweet spot in the middle of its range.

But more importantly, cellular modules are electrically noisy. When the SIM7080G transmits an LTE packet, it pulls a large current spike (can be 2A for a few milliseconds). That spike, if it shared a power rail with the ESP32 or the SX1262, would cause voltage dips that corrupt data or crash those chips.

Giving the SIM7080G its own dedicated LDO (AP2112K-3.8) with its own input and output capacitors isolates it. The 3.3V rail for the ESP32 and RF chips stays clean.

**Rule of thumb:** Noisy components (motors, cellular modules, switching regulators) should never share a power rail with sensitive analog or RF components without isolation.

### Why does the SX1262 need a BUSY pin and a DIO1 pin?

The SX1262 processes commands internally and takes time to do things (change frequency, start transmitting, etc.). The **BUSY pin** is HIGH while it's busy processing. Your firmware must always check that BUSY is LOW before sending a new command — if you send a command while it's busy, it gets ignored.

The **DIO1 pin** is an interrupt output. You configure it to trigger when certain events happen (transmission complete, packet received, timeout). Instead of your firmware constantly asking "are you done yet?", the SX1262 taps you on the shoulder via DIO1 when it's finished. This frees up the CPU to do other things while the radio is working.

**Pattern in the firmware:**
```
1. Check BUSY = LOW
2. Send command to SX1262 over SPI
3. Wait for DIO1 interrupt (radio signals it's done)
4. Read result over SPI
```

### What is a crystal and why do chips need one?

A **quartz crystal** (or just "crystal") is a small physical component — a tiny slice of quartz mineral — that vibrates at a precise, stable frequency when electricity is applied to it. This is called the **piezoelectric effect**: mechanical vibration and electrical oscillation are linked in quartz, so you can electrically "ring" it like a tuning fork.

The frequency it vibrates at is determined by its physical size and cut — a 32 MHz crystal vibrates exactly 32 million times per second, always, regardless of temperature or voltage changes (within limits). This makes it far more accurate than a software timer or an internal RC oscillator.

**Why do chips need this?**

Chips need a clock — a regular electrical pulse that drives every operation. "160 MHz processor" means the chip does 160 million operations per second, timed by 160 million clock pulses. Without a stable clock source, timing drifts, and things go wrong:

- Radio chips drift off their target frequency → other radios can't hear them
- Ethernet chips can't maintain the precise bit rate → connection drops
- Microcontrollers running software timers lose track of real time

**Crystal vs internal oscillator:**

Most chips have a built-in RC oscillator (resistor + capacitor that charges and discharges). It's convenient — no external parts — but it's only accurate to about ±1%. For general computation that's fine, but for radio frequency and Ethernet, ±1% is catastrophic.

A crystal is accurate to ±20–50 ppm (parts per million) — that's 0.002–0.005% — orders of magnitude better.

**What are the load capacitors (the 10pF caps)?**

The crystal doesn't vibrate correctly in isolation — it needs a small capacitive load on each pin to "tune" its oscillation to the exact target frequency. These are called **load capacitors**. The crystal's datasheet specifies the exact capacitance value. Get them wrong and the crystal runs slightly off frequency (usually a few kHz off — bad for radio).

**The KiCad symbol:**

Two variants you'll encounter:
- `Crystal` — basic 2-pin symbol
- `Crystal_GND24` — 4-pin: 2 signal pins + 2 pins for the metal case (tie to GND to shield the crystal from interference)

Use `Crystal_GND24` for RF designs. The case pins go to GND.

```
XTA ──┬── [Crystal] ──┬── XTB
      │   (case→GND)  │
    10pF            10pF
      │               │
     GND             GND
```

### Why does the W5500 need a 25 MHz crystal?

Ethernet (10/100 Mbps) is a synchronous protocol — both devices need to agree on timing precisely. The W5500's PHY (physical layer chip) needs an accurate clock source to generate and receive Ethernet signals at exactly the right frequency.

The 25 MHz crystal provides this reference. The W5500 uses it internally to generate the clocks needed for MII (Media Independent Interface) and line encoding.

Without a crystal (or with a poor quality one), the Ethernet link won't establish or will drop packets randomly.

### What is the DCC_SW pin on the SX1262? And the 22nH inductor?

The SX1262 has an internal voltage regulator — it can either use a simple **LDO** (linear dropout) or a **DC-DC buck converter** (switching regulator) to power its internal core from VBAT.

- **LDO mode**: simpler, no external parts, but wastes energy as heat
- **DC-DC mode**: more efficient (less battery drain), but needs a small external inductor

The **DCC_SW pin** is the switching node of the internal DC-DC converter. When running in DC-DC mode, current pulses in and out of this pin at high frequency — the external inductor smooths these pulses into a stable DC voltage.

The **22nH inductor** connects from DCC_SW back to VBAT. The switching happens so fast (MHz range) that the inductor stores and releases energy faster than a capacitor could, acting as a current buffer.

We use DC-DC mode on this board because the SX1262 is running on 3.3V from a regulator and efficiency matters. The firmware must also be configured to use DC-DC mode on startup via `SetRegulatorMode`.

> **Note:** this section is preserved verbatim from the original learning notes and mentions a 22nH inductor. Section 3 above corrected this during schematic work to **15µH**, taken from the SX1262 datasheet reference design — use 15µH, not 22nH.

### What is VR_PA on the SX1262?

VR_PA is the **power amplifier supply**. The RF transmitter inside the SX1262 has its own dedicated supply pin, separate from the digital logic supply (VBAT). This isolation prevents the transmitter's current spikes during TX from disturbing the digital sections of the chip.

On our board, VR_PA connects to +3V3 with a 100nF decoupling cap. At 3.3V, the SX1262 can transmit at up to +22 dBm — more than enough for our 868 MHz LoRa link.

### What is VREG on the SX1262?

VREG is the **output of the SX1262's internal voltage regulator**. The chip generates a lower internal voltage (around 1.8V) from VBAT and uses it to power its own internal digital logic.

You do not connect VREG to anything external. You only place a 100nF decoupling capacitor from VREG to GND. This stabilises the regulator's output — without it, the chip's internal voltage rails would oscillate and the chip wouldn't function correctly.

### What is the PE4259 RF switch and why does the SX1262 need one?

The SX1262 has two separate RF ports:
- **RFO** — transmit output. The LoRa signal goes OUT through here to the antenna.
- **RFI_N / RFI_P** — receive input (differential pair). Incoming signals come IN from the antenna through here.

The problem: you only have one antenna. You cannot connect it to both ports simultaneously — the transmitter output would flood into the receiver input and the chip would hear itself instead of the air.

The **PE4259** is an RF switch — a tiny chip that acts like a signal traffic controller. It has three RF ports:
- **RF1** — connected to the TX path (from RFO)
- **RF2** — connected to the RX path (from RFI_N/RFI_P)
- **RFC** — connected to the antenna

At any moment, RFC is connected to either RF1 or RF2, never both. The **CTRL pin** decides which:
- CTRL HIGH → RFC connects to RF1 → antenna goes to TX path → transmitting
- CTRL LOW → RFC connects to RF2 → antenna goes to RX path → receiving

**DIO2 on the SX1262 controls CTRL** through a 100Ω resistor. The firmware configures DIO2 to go HIGH before transmitting and LOW before receiving — the SX1262 can do this automatically via the `SetDio2AsRfSwitchCtrl` command.

**Why the 100Ω resistor between DIO2 and CTRL?**
It limits current and protects against any voltage mismatch between the SX1262's DIO pin and the PE4259's CTRL input. Standard practice for any digital signal driving an RF component.

**This is why DIO2 is not no-connect.** Without it, the RF switch never changes state and the radio either can't transmit or can't receive.

### Why is the USB-C CC resistor value specifically 5.1kΩ?

The USB-C specification defines how a device tells the host what power it needs. The **CC (Configuration Channel)** pins are how this negotiation happens.

When a USB-C device (like this board) puts a **5.1kΩ pull-down resistor** on both CC1 and CC2:
- The host (laptop, charger, USB hub) detects these resistors
- It identifies the connected device as a **UFP (Upstream Facing Port)** — i.e., something that wants to receive power
- It delivers **5V at up to 900mA** (USB 3.x default current)

Different resistor values signal different power requests:
- No resistor → not a USB device
- 5.1kΩ → 5V / 900mA (what we use)
- Requires a USB PD controller chip → higher voltages/currents (9V, 12V, 20V)

Since this board only needs USB-C as a backup 5V source and programming port, 5.1kΩ is exactly right — no PD controller IC needed.

### What is a ferrite bead and why does VDDA use one?

A **ferrite bead** is a passive component that acts like a frequency-selective resistor. At DC and low frequencies, it has near-zero resistance (current passes freely). At high frequencies (MHz range), it becomes resistive and blocks the signal.

For the VDDA (analog supply) pin on a microcontroller:

```
+3V3 digital rail ──[ferrite bead]──► VDDA ──[100nF cap]──► GND
```

The digital 3.3V rail carries high-frequency switching noise from the CPU and peripherals. The ferrite bead blocks that noise from reaching the ADC's supply pin. The capacitor on the VDDA side filters out whatever gets through.

Without this, your ADC readings will have a noise floor that looks like random fluctuations on top of your signal — especially noticeable when reading slowly-changing signals like temperature or battery voltage.

### What is a power rail?

A power rail is a named voltage that gets distributed to every component on the board that needs it. Instead of drawing a wire from your voltage regulator to every single chip, you give that voltage a name (`+3V3`, `+5V`, `GND`) and every component just connects to that name.

Think of it like mains electricity in a building — one source at the meter, but every socket in every room is on the same "230V rail." You don't see individual wires from the meter to each socket; they're all tied to the same distribution line behind the walls.

In KiCad, power rails are represented by **power symbols**. Drop a `+3V3` symbol on a pin and KiCad knows that pin is connected to everything else labelled `+3V3`, even if no visible wire connects them on the schematic.

This board has four rails:
- `+5V` — after PoE and USB-C are OR'd together
- `+3V3` — ESP32, W5500, SX1262, SD card
- `+3V8` — SIM7080G only (isolated because cellular modules are noisy)
- `GND` — the return path for all of the above

### ERC Errors Explained — The Full Guide

#### "Input Power pin not driven by any Output Power pins"

KiCad is saying: "I can see components consuming power on this net, but nothing producing it."

**The rule:**
- If **no component output** is producing that voltage on the schematic (e.g. the LDO isn't drawn yet, or the power comes from an external cable) → add a `PWR_FLAG`
- If a **real power output pin** (LDO VOUT, regulator output) is already on that net → **no PWR_FLAG needed**. The VOUT pin already tells KiCad where the power comes from.

**In your design:**

| Net | Source on schematic | PWR_FLAG needed? |
|---|---|---|
| `+3V3` | TLV1117-33 VOUT | No — VOUT drives it |
| `+3V8` | AP2112K VOUT | No — VOUT drives it |
| `+5V` | LM66100 VOUT × 2 | No — VOUT drives it |
| `GND` | GND power symbol | No — power symbol drives it |
| `USB_VBUS` | Nothing (comes from USB cable) | Yes — add PWR_FLAG |
| `POE_5V` | Nothing yet (PPS23730 not wired) | Yes — temporarily |
| `SIM_VCC` | SIM7080G SIM_VDD (Output type) | Yes — add PWR_FLAG (see below) |

**Important:** PWR_FLAGs placed early (before the LDO was placed) must be **removed** once the LDO is added. Keeping them causes the next error.

#### "Pins of type Power output and Power output are connected"

Two pins defined as "Power output" are on the same net. KiCad sees two power sources fighting.

Three situations where this happens:

1. **PWR_FLAG left on a net that now has a real VOUT** → remove the PWR_FLAG
2. **Two LM66100 VOUTs both on +5V** → this is intentional (OR-ing circuit). Right-click → Exclude from ERC
3. **SIM_VDD (Output) + PWR_FLAG** → SIM_VDD is "Output" type (not "Power output"), but they still conflict. Keep the PWR_FLAG, right-click the SIM_VCC error → Exclude from ERC

#### "Pins of type Output and Power output are connected"

A regular "Output" pin and a PWR_FLAG are on the same net. This is the SIM7080G SIM_VDD case — the pin is typed "Output" in the symbol, not "Power output", but PWR_FLAG is "Power output". They conflict.

Fix: keep the PWR_FLAG (so the SIM card VCC gets a power source), then exclude the specific error from ERC.

#### The core rule for PWR_FLAG (final version)

> **PWR_FLAG = "I know power comes here, but the schematic doesn't show a component producing it."**
> 
> If any component's output pin is already on the net → no PWR_FLAG.  
> If the power comes from outside the schematic (USB cable, external supply, unfinished section) → add PWR_FLAG.

### What are strapping pins and why can't we use GPIO9 as CS_ETH?

**Strapping pins** are special GPIO pins that the chip reads at the exact moment of power-on or reset — before any firmware runs — to decide how to start up. The values on these pins during that brief window determine boot mode, so they need to be in a defined, deliberate state at power-on.

On the ESP32-C6, **GPIO9 is a strapping pin**:
- GPIO9 LOW at boot → boot normally from flash (run your program)
- GPIO9 HIGH at boot → enter download/bootloader mode (accept new firmware)

After the chip finishes booting, GPIO9 is released and becomes a regular GPIO. So technically you could use it for other purposes after boot — but there's a catch.

We wired GPIO9 with a 10kΩ pull-**down** resistor to GND (to ensure normal boot by default). CS (Chip Select) pins must idle **HIGH** — HIGH means "chip not selected, ignore the bus." A pull-down forces the pin LOW by default, which would mean the W5500 is permanently selected at power-on. That causes bus conflicts and undefined behaviour before the firmware even starts.

**Fix:** Move CS_ETH to GPIO2, which has no strapping function, no pull resistor, and no conflicts. Clean pin, clean CS line.

**Rule to remember:** Always check the datasheet for strapping pins before assigning GPIOs. Don't use them for signals that need a specific default state (like CS HIGH, or signals with external pull resistors that might conflict).

### Why does GPIO9 (BOOT pin) get a 10kΩ pull-down resistor to GND?

GPIO9 is the BOOT pin on the ESP32-C6. When the chip powers on or resets, it reads this pin before running any code to decide what mode to start in:

- **LOW (GND)** → boot normally, run the program in flash memory
- **HIGH (3.3V)** → enter download/bootloader mode, wait for new firmware

The 10kΩ resistor keeps GPIO9 LOW by default so the chip always boots your program. It's a resistor (not a wire directly to GND) so a button can still pull it HIGH when you need to flash new firmware:

```
+3V3
  │
[Button]  ← hold during power-on to enter flash mode
  │
GPIO9
  │
[10kΩ]    ← default LOW = normal boot
  │
GND
```

You've used this before without realising it — the BOOT button on every ESP32 dev board is exactly this circuit. Our PCB builds it in.

The EN pin uses the same idea but opposite: a 10kΩ pull-UP to +3V3 keeps EN HIGH by default (chip runs). A button to GND pulls EN LOW to reset the chip. That's the RESET button.

### Why do crystals for different chips need different load cap values?

The load capacitors on each side of a crystal "tune" the crystal to its exact target frequency. Each crystal has a specified **load capacitance (CL)** in its datasheet — this is the total capacitance the crystal "sees" across both pins.

Since the two caps are in series from the crystal's perspective:
```
CL = (C1 × C2) / (C1 + C2)    (if C1 = C2, this simplifies to C/2)
```

So if the crystal needs CL = 10pF, you use two 20pF caps (20/2 = 10pF).

In this design:
- **SX1262 crystal (32 MHz)** → 10pF load caps (CL ≈ 5pF, as per SX1262 datasheet)
- **W5500 crystal (25 MHz)** → 20pF load caps (CL ≈ 10pF, as per W5500 datasheet)

For the W5500, a standard 2-pin Crystal symbol is fine — it's not an RF design, so the Crystal_GND24 (grounded case) isn't needed. Crystal_GND24 is for RF chips where the grounded case provides RF shielding.

---

> Original closing note from `learning.md`, preserved verbatim: "Add more as you go... Every time something in KiCad or a datasheet confuses you, write the question and answer here. This file is for you."
