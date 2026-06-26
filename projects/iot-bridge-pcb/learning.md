# IoT Bridge — Project Learning Notes

> This file is for understanding, not presenting. Every time something in this project makes you ask "wait, why?" — the answer goes here. Written in plain language, tied to real decisions made in this project.

---

## Tools & Software We're Using — And Why

### KiCad
Free, open-source PCB design software. Industry-used alongside paid tools like Altium Designer and Eagle. Has two main editors:
- **Schematic Editor** — draw the logical connections (what connects to what)
- **PCB Editor** — physically place components and route copper traces

We're using KiCad because the brief specifically recommends it, it's free, and it's powerful enough for professional work. Altium is the industry gold standard but costs thousands of dollars per year.

### Espressif KiCad Libraries
Espressif (makers of the ESP32) publishes official KiCad symbol and footprint libraries for all their chips. Downloaded from their GitHub and added to KiCad. Without this, there's no ESP32-C6-WROOM-1 symbol available in KiCad's default library — you'd have to draw one from scratch.

**How to add it:** Preferences → Manage Symbol Libraries → add the downloaded `.kicad_sym` file.

### KiCad Symbol Libraries Used So Far
| Library | What's in it |
|---|---|
| `Device` | Generic passives — R (resistor), C (capacitor), L (inductor) |
| `Switch` | SW_Push — momentary tactile button |
| `power` | Power symbols — +3V3, GND, +5V, PWR_FLAG |
| `espressif` | ESP32-C6-WROOM-1 and other Espressif modules |
| `Connector` | USB-C, RJ45, pin headers |

### ESP-IDF (Planned — Firmware)
Espressif IoT Development Framework. This is the official C/C++ framework for writing firmware for ESP32 chips. Think of it like the Arduino IDE but professional-grade — more control, more features, more complex. Includes:
- FreeRTOS (real-time operating system for running multiple tasks)
- WiFi and Bluetooth stack
- SPI, UART, I2C, GPIO drivers
- OTA update support

### RadioLib (Planned — Firmware)
An open-source library for controlling RF (radio) chips like the SX1262 over SPI. Handles all the low-level SPI commands and register writes so your firmware can call simple functions like `lora.transmit("hello")` instead of manually writing SX1262 opcodes. Supports both raw LoRa and full LoRaWAN.

### FreeRTOS (Planned — Firmware)
A real-time operating system built into ESP-IDF. Lets you run multiple "tasks" concurrently — like reading a LoRa packet in one task while simultaneously checking for an MQTT message in another. Without an RTOS, you'd have to handle all of that manually in one loop, which gets very messy very fast.

---

## How Does SPI Work? What Are MOSI, MISO, SCK, and CS?

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

---

## What is Zigbee and Thread? What are they used for?

Both are **low-power mesh networking protocols** for smart devices. They both run on the **IEEE 802.15.4 radio standard** at 2.4GHz — the same physical radio, different software on top.

**Mesh** means devices relay messages through each other. A door sensor too far from the hub sends its packet through a light bulb, which passes it through a plug socket, which reaches the hub. The network heals itself if one device drops out.

**Zigbee (2004)**
The established smart home standard. Used in: Philips Hue, IKEA Tradfri, Samsung SmartThings, most smart plugs, sensors, and bulbs you can buy today. Requires a central **coordinator** (hub/bridge) to manage the network. Not IP-based — devices don't have internet addresses, they use Zigbee-specific IDs. Huge installed base.

**Thread (2014)**
Designed to fix Zigbee's weaknesses. The key difference: Thread is **IP-based** — every device gets a real IPv6 address, so it can be addressed directly like any internet device. No single point of failure — any device can act as the border router. Backed by Apple, Google, Amazon, Samsung. Powers the **Matter** protocol — the new universal smart home standard that all major ecosystems (HomeKit, Google Home, Alexa) have agreed to support.

**Why both on this bridge?**
Zigbee covers the massive existing market of smart home devices. Thread/Matter covers everything being built now and going forward. The ESP32-C6's single 802.15.4 radio handles both — firmware chooses which protocol is active at runtime.

---

## What's the difference between WiFi 4 and WiFi 6?

The numbers (4, 5, 6) are marketing names for 802.11 generations:
- WiFi 4 = 802.11n (2009)
- WiFi 5 = 802.11ac (2013)
- WiFi 6 = 802.11ax (2019)

For IoT, the headline speed difference doesn't matter. What matters:

**OFDMA** — WiFi 6 can talk to multiple devices simultaneously on the same channel. WiFi 4 can only serve one device at a time. In a house with 50 smart devices, WiFi 6 routers handle the traffic far more efficiently.

**TWT (Target Wake Time)** — the killer IoT feature. WiFi 6 devices can negotiate a schedule with the router: "I'll wake up every 10 minutes, send my data packet, then sleep again." Between those windows, the WiFi radio is completely off. This dramatically reduces power consumption for battery-powered devices. WiFi 4 has no equivalent — devices have to stay awake listening for the router constantly.

**Dense environments** — WiFi 6 uses BSS Coloring to reduce interference in apartment buildings or offices where many networks overlap. WiFi 4 degrades badly in the same conditions.

For this bridge: the ESP32-C6's WiFi 6 support means it works better in environments with many devices, and any WiFi 6 devices connecting to it can use TWT for battery savings.

---

## REYAX RYLR998 — The LoRa Module I Used Before

The RYLR998 is a ready-made LoRa module made by REYAX Technology. The important thing to know: **it is built around the Semtech SX1262 chip** — the same chip we're using bare on this PCB. You've already worked with the heart of our LoRa design.

### RYLR998 Specs
| Spec | Value |
|---|---|
| Core chip | Semtech SX1262 |
| Interface | UART (AT commands) |
| Frequency | 868 MHz or 915 MHz versions |
| TX Power | Up to +22 dBm |
| Sensitivity | Down to -148 dBm |
| Supply voltage | 2.8V – 5.5V |
| Range | Up to 15 km (line of sight) |
| Modes | Point-to-point + LoRaWAN |

### How You Used It vs How We Use SX1262 Now

**RYLR998 (what you used before):**
- Plug into breadboard, connect to MCU via UART (TX/RX pins)
- Send plain text AT commands: `AT+SEND=0,5,HELLO` to transmit, read incoming data from UART
- The module handles everything internally — RF matching, protocol, register config
- No RF knowledge needed

**SX1262 bare chip (what we're doing on the PCB):**
- Soldered directly onto the PCB, connected to ESP32 over SPI (4 wires + CS + RESET + BUSY + DIO1)
- Firmware talks to it via SPI register writes and command opcodes
- We design the RF matching network and antenna connection ourselves
- Full control, smaller footprint, lower cost at volume

### Common AT Commands on the RYLR998
```
AT               → ping the module (responds OK)
AT+BAND=868000000 → set frequency to 868 MHz
AT+ADDRESS=1     → set device address
AT+NETWORKID=6   → set network ID (both sides must match)
AT+SEND=0,5,HELLO → send "HELLO" (5 bytes) to address 0
AT+PARAMETER=9,7,1,12 → set SF9, BW125, CR4/5, preamble 12
```

### Why We're Not Using the RYLR998 on This PCB

The RYLR998 is great for prototyping but not ideal for a custom PCB:
1. **Size** — it's a module with its own PCB, which sits on top of yours. The bare SX1262 is a tiny QFN chip that integrates directly.
2. **Cost at volume** — a RYLR998 module costs ~$8-15. A bare SX1262 chip is ~$3.
3. **Control** — with the bare chip, we configure every LoRa parameter directly and can integrate LoRaWAN stacks (RadioLib) with more flexibility.
4. **PCB integration** — the bare chip sits flat on the board. A module adds height and requires its own mounting footprint.

If you were prototyping this project on a breadboard, you'd use the RYLR998. Since we're designing a custom PCB, we use the SX1262 directly.

---

## What alternative components could we have used?

If the ESP32-C6 wasn't an option (unavailable, wrong package, etc.) here's what we'd have needed:

### For WiFi + Bluetooth
| Alternative | Notes |
|---|---|
| ESP32-S3 | Dual core, more GPIO, no Zigbee/Thread — would need separate 802.15.4 chip |
| ESP32-C3 | Cheaper, smaller, no Zigbee/Thread |
| CYW43439 | Used in Raspberry Pi Pico W, WiFi 4 + BT 5 only |
| nRF7002 | Nordic's WiFi 6 companion chip (needs a host MCU alongside it) |

### For Zigbee / Thread (802.15.4)
| Alternative | Notes |
|---|---|
| Nordic nRF52840 | ARM Cortex-M4, excellent BLE + 802.15.4, very popular for Thread/Matter |
| TI CC2652R | TI's dedicated Zigbee/Thread/BLE chip, used in many commercial hubs |
| Silicon Labs EFR32MG | Used in Samsung SmartThings, very capable but expensive |
| nRF52833 | Smaller/cheaper nRF52840, same radio capabilities |

With any of these, you'd need the MCU (ESP32-S3) connected to the 802.15.4 chip over SPI or UART — two chips instead of one.

### For LoRa
| Alternative | Notes |
|---|---|
| SX1276 | Previous generation Semtech chip, lower sensitivity than SX1262, still widely used |
| SX1278 | Same as SX1276 family, 433MHz focused |
| RFM95W | A module (not bare chip) using the SX1276 inside — easier to prototype with |
| LR1110 | Semtech's newer multi-standard chip (LoRa + WiFi geolocation + GNSS) — overkill |

We chose SX1262 because it's the current generation with better sensitivity and lower power.

### For Cellular
| Part | Standard | Notes |
|---|---|---|
| SIM800L | 2G GPRS only | Cheapest but 2G is dying globally — avoid for new designs |
| A7670E | LTE Cat-1 | SIMCom's LTE module, higher throughput than Cat-M |
| SIM7600E | LTE Cat-4 | Fast but overkill for IoT data rates, higher power |
| Quectel BG95 | LTE Cat-M + NB-IoT + GNSS | Direct alternative to SIM7080G, very popular |
| Quectel EC21 | LTE Cat-1 | Good for higher data rate IoT applications |
| u-blox SARA-R4 | LTE Cat-M + NB-IoT | Premium, used in industrial/medical IoT |
| nRF9160 | LTE Cat-M + NB-IoT | Nordic's SiP (has ARM Cortex-M33 MCU built in — could replace both MCU and cellular module) |

We chose SIM7080G for: correct IoT tier (Cat-M/NB-IoT), built-in GNSS, 2G fallback, and good availability.

### For Ethernet
| Alternative | Notes |
|---|---|
| ENC28J60 | Older, SPI-based, no hardwired TCP/IP stack — MCU does more work |
| LAN8720A | Ethernet PHY only (no MAC/TCP) — needs MCU with built-in Ethernet MAC |
| W6100 | WIZnet's newer chip, adds IPv6 support over the W5500 |

We chose W5500 because it has the full TCP/IP stack in hardware, is massively documented, and works directly with ESP32 over SPI.

### For PoE
| Alternative | Notes |
|---|---|
| TPS2375 | Simpler 8-pin 802.3af only (15.4W max) — less power headroom but easier to design with |
| PD70101 | Microchip's PoE PD controller, common in enterprise equipment |
| AG9800 | Integrated PoE PD + DC-DC, similar to TPS23730 |

We chose TPS23730 for 802.3bt support (51W headroom) and the integrated DC-DC controller.

---

## Why the ESP32-C6 and not another ESP32 variant?

The deciding factor is the **802.15.4 radio** — the C6 is the only chip in the entire ESP32 family that has one built in. Both Zigbee and Thread run on 802.15.4. Every other ESP32 variant (original, S2, S3, C3) has no 802.15.4 radio at all.

Without the C6, meeting the brief's Zigbee + Thread requirement would mean adding a completely separate chip (like a Nordic nRF52840 or TI CC2652) just for that radio — more components, more wiring, more PCB space, more cost.

The C6 also adds Wi-Fi 6 (802.11ax) which no other ESP32 had before it. But that's a bonus — the 802.15.4 radio is the real reason.

**Quick comparison of ESP32 variants:**
| Chip | Wi-Fi | BT | Zigbee/Thread |
|---|---|---|---|
| ESP32 (original) | 4 | Classic + LE | No |
| ESP32-S3 | 4 | BT 5 LE | No |
| ESP32-C3 | 4 | BT 5 LE | No |
| **ESP32-C6** | **6** | **BT 5 LE** | **Yes** |

If this project didn't need Zigbee or Thread, the ESP32-S3 would've been a better choice — it's dual-core, has more GPIO, and handles heavier computation. The C6 is single-core. But for an IoT bridge that needs to speak every major protocol, C6 is the only logical single-chip option.

---

## When do you use PWR_FLAG? When a resistor? When a decoupling cap? How do you pick values?

### PWR_FLAG

PWR_FLAG is **KiCad-only** — it has zero effect on the actual circuit. It tells KiCad's ERC that a net is being powered even when no output pin on the schematic is visibly driving it.

**The rule:**
- Net has a real power output pin (LDO VOUT, regulator output) → **no PWR_FLAG needed**
- Net is powered from outside the schematic (USB cable, external supply, section not yet drawn) → **add PWR_FLAG**
- GND → **no PWR_FLAG needed** (GND power symbol is already a power output type)

One PWR_FLAG per net is enough — place it anywhere on that net.

> If you add a PWR_FLAG to a net that already has a real VOUT pin, KiCad will throw "two power outputs connected" error. Remove the PWR_FLAG in that case.

---

### Resistors — when and what value

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

---

### Decoupling capacitors — when and what value

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

---

## Why does the MCU need so many capacitors on its power pins?

Every time a microcontroller switches a logic gate (which happens billions of times per second), it pulls a tiny spike of current. At 160 MHz (ESP32-C6's clock speed), that's 160 million spikes per second. Those spikes travel back up the power trace and cause tiny voltage dips on the chip's VDD pin.

If the dip is bad enough, the chip reads its own power supply as a logic LOW — and it crashes or corrupts data. A 100nF ceramic capacitor placed right next to the VDD pin acts as a local charge reservoir: it instantly supplies the current spike before the dip can happen, then slowly recharges between spikes.

**This is why placement matters in PCB layout** — a decoupling cap on the other side of the board doesn't help, because the trace between the cap and the pin is too long (adds inductance, slows response). Place them within 1–2mm of the pin.

The ESP32-C6 has multiple VDD and VDDIO pins — each one needs its own 100nF cap. It looks excessive on the schematic but every single one matters.

---

## Why two separate LDOs (3.3V and 3.8V)? Why not one supply?

The SIM7080G cellular module requires 3.0–4.2V — it cannot run on 3.3V or 5V. 3.8V is the sweet spot in the middle of its range.

But more importantly, cellular modules are electrically noisy. When the SIM7080G transmits an LTE packet, it pulls a large current spike (can be 2A for a few milliseconds). That spike, if it shared a power rail with the ESP32 or the SX1262, would cause voltage dips that corrupt data or crash those chips.

Giving the SIM7080G its own dedicated LDO (AP2112K-3.8) with its own input and output capacitors isolates it. The 3.3V rail for the ESP32 and RF chips stays clean.

**Rule of thumb:** Noisy components (motors, cellular modules, switching regulators) should never share a power rail with sensitive analog or RF components without isolation.

---

## Why LoRa at 868 MHz and not 915 MHz or 433 MHz?

Radio frequencies for unlicensed (no licence required) use are regulated by region:

- **Region 1 (Europe, Middle East, Africa)** → 868 MHz ISM band
- **Region 2 (Americas)** → 915 MHz ISM band
- **Region 3 (Asia-Pacific)** → 433 MHz or 923 MHz depending on country

Nigeria falls under **ITU Region 1**, so 868 MHz is the correct band. Using 915 MHz in Nigeria would still work electrically, but it would be operating outside the licensed band — a regulatory problem if the product is ever certified.

The SX1262 covers 150–960 MHz so it can do either, but the antenna design and RF matching network on the PCB needs to be tuned for one specific frequency.

---

## What is PoE and why does it need a special IC?

**PoE (Power over Ethernet)** sends DC power over the unused wire pairs (or spare pairs) in an Ethernet cable — so you only need one cable to a device instead of separate power and network cables.

The problem: PoE uses 48V (much higher than the 3.3V–5V our board needs), and not all Ethernet cables/switches support PoE. The IEEE 802.3 standard defines a handshake protocol so PoE devices don't accidentally fry non-PoE equipment.

The **TPS23730** is a **PD (Powered Device) controller** — it:
1. Performs the IEEE 802.3 handshake with the PoE switch to negotiate power
2. Converts the 48V from the cable down to a usable voltage (we target 5V) via an internal DC-DC controller
3. Protects the circuit if the voltage/current exceeds safe limits

Without this IC, you'd have to design all of that yourself. This is why you don't just wire the Ethernet cable directly to your board.

---

## Why does the SX1262 need a BUSY pin and a DIO1 pin?

The SX1262 processes commands internally and takes time to do things (change frequency, start transmitting, etc.). The **BUSY pin** is HIGH while it's busy processing. Your firmware must always check that BUSY is LOW before sending a new command — if you send a command while it's busy, it gets ignored.

The **DIO1 pin** is an interrupt output. You configure it to trigger when certain events happen (transmission complete, packet received, timeout). Instead of your firmware constantly asking "are you done yet?", the SX1262 taps you on the shoulder via DIO1 when it's finished. This frees up the CPU to do other things while the radio is working.

**Pattern in the firmware:**
```
1. Check BUSY = LOW
2. Send command to SX1262 over SPI
3. Wait for DIO1 interrupt (radio signals it's done)
4. Read result over SPI
```

---

## What is a crystal and why do chips need one?

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

---

## Why does the W5500 need a 25 MHz crystal?

Ethernet (10/100 Mbps) is a synchronous protocol — both devices need to agree on timing precisely. The W5500's PHY (physical layer chip) needs an accurate clock source to generate and receive Ethernet signals at exactly the right frequency.

The 25 MHz crystal provides this reference. The W5500 uses it internally to generate the clocks needed for MII (Media Independent Interface) and line encoding.

Without a crystal (or with a poor quality one), the Ethernet link won't establish or will drop packets randomly.

---

## What is the DCC_SW pin on the SX1262? And the 22nH inductor?

The SX1262 has an internal voltage regulator — it can either use a simple **LDO** (linear dropout) or a **DC-DC buck converter** (switching regulator) to power its internal core from VBAT.

- **LDO mode**: simpler, no external parts, but wastes energy as heat
- **DC-DC mode**: more efficient (less battery drain), but needs a small external inductor

The **DCC_SW pin** is the switching node of the internal DC-DC converter. When running in DC-DC mode, current pulses in and out of this pin at high frequency — the external inductor smooths these pulses into a stable DC voltage.

The **22nH inductor** connects from DCC_SW back to VBAT. The switching happens so fast (MHz range) that the inductor stores and releases energy faster than a capacitor could, acting as a current buffer.

We use DC-DC mode on this board because the SX1262 is running on 3.3V from a regulator and efficiency matters. The firmware must also be configured to use DC-DC mode on startup via `SetRegulatorMode`.

---

## What is VR_PA on the SX1262?

VR_PA is the **power amplifier supply**. The RF transmitter inside the SX1262 has its own dedicated supply pin, separate from the digital logic supply (VBAT). This isolation prevents the transmitter's current spikes during TX from disturbing the digital sections of the chip.

On our board, VR_PA connects to +3V3 with a 100nF decoupling cap. At 3.3V, the SX1262 can transmit at up to +22 dBm — more than enough for our 868 MHz LoRa link.

---

## What is VREG on the SX1262?

VREG is the **output of the SX1262's internal voltage regulator**. The chip generates a lower internal voltage (around 1.8V) from VBAT and uses it to power its own internal digital logic.

You do not connect VREG to anything external. You only place a 100nF decoupling capacitor from VREG to GND. This stabilises the regulator's output — without it, the chip's internal voltage rails would oscillate and the chip wouldn't function correctly.

---

## What is the PE4259 RF switch and why does the SX1262 need one?

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

---

## What is the SWD header and why does every MCU design include one?

**SWD (Serial Wire Debug)** is ARM's debugging interface. It uses just two signal wires (SWDIO and SWDCLK) plus power and ground — so a 4-pin header on your PCB lets you:

1. **Flash firmware** — load your compiled code directly onto the chip without a USB bootloader
2. **Debug in real time** — set breakpoints, step through code line by line, inspect variable values, all while the code is running on the actual hardware

You connect an **ST-Link** (for STM32) or **J-Link** programmer to this header. On the ESP32-C6, USB Serial/JTAG is built in so you can use the USB-C port directly, but a dedicated SWD/JTAG header is still good practice for production boards.

If you don't include an SWD header and your USB bootloader breaks or your firmware bricks the chip, you have no way to recover it.

---

## Why is the USB-C CC resistor value specifically 5.1kΩ?

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

---

## What does "DNP" mean on a BOM?

**DNP = Do Not Populate.** It means the footprint (pad pattern) is on the PCB, but the component is not soldered during this revision. The pads are there for a future version.

We used this for the eSIM footprint — the SIM7080G doesn't have an eSIM, so we included unpopulated pads where a discrete eSIM chip could be soldered in a future revision. Manufacturing the board with empty pads costs nothing extra and saves redesigning the PCB later.

---

## What is a ferrite bead and why does VDDA use one?

A **ferrite bead** is a passive component that acts like a frequency-selective resistor. At DC and low frequencies, it has near-zero resistance (current passes freely). At high frequencies (MHz range), it becomes resistive and blocks the signal.

For the VDDA (analog supply) pin on a microcontroller:

```
+3V3 digital rail ──[ferrite bead]──► VDDA ──[100nF cap]──► GND
```

The digital 3.3V rail carries high-frequency switching noise from the CPU and peripherals. The ferrite bead blocks that noise from reaching the ADC's supply pin. The capacitor on the VDDA side filters out whatever gets through.

Without this, your ADC readings will have a noise floor that looks like random fluctuations on top of your signal — especially noticeable when reading slowly-changing signals like temperature or battery voltage.

---

## What is a power rail?

A power rail is a named voltage that gets distributed to every component on the board that needs it. Instead of drawing a wire from your voltage regulator to every single chip, you give that voltage a name (`+3V3`, `+5V`, `GND`) and every component just connects to that name.

Think of it like mains electricity in a building — one source at the meter, but every socket in every room is on the same "230V rail." You don't see individual wires from the meter to each socket; they're all tied to the same distribution line behind the walls.

In KiCad, power rails are represented by **power symbols**. Drop a `+3V3` symbol on a pin and KiCad knows that pin is connected to everything else labelled `+3V3`, even if no visible wire connects them on the schematic.

This board has four rails:
- `+5V` — after PoE and USB-C are OR'd together
- `+3V3` — ESP32, W5500, SX1262, SD card
- `+3V8` — SIM7080G only (isolated because cellular modules are noisy)
- `GND` — the return path for all of the above

---

## What is a Polyfuse?

A polyfuse (resettable fuse / PPTC) is a protection component placed on the USB-C VBUS line. It limits current to a set value (500mA on our board) and protects the circuit from overcurrent faults.

**Regular fuse vs polyfuse:**
- Regular fuse: blows permanently when overcurrent occurs — you replace it
- Polyfuse: trips when overcurrent occurs (resistance jumps to near-infinite), then **resets itself** once the fault is removed and it cools down

**How it works:** The polymer material inside is normally conductive. Too much current → heats up → polymer expands → resistance skyrockets → current drops to near zero → fault is cleared → cools down → resets.

**Why we use it on USB-C VBUS:** If something on the board short-circuits and tries to pull 2A through the USB port, the 500mA polyfuse trips and prevents damage to the USB source. Without it, you could fry the host computer's USB port or the board itself.

In KiCad: press `A`, search `Polyfuse` or `Fuse_Resettable`. Set value to `500mA`.

---

## What is the LM66100?

The LM66100 is TI's ideal diode controller — the chip that lets us safely combine two power sources (USB-C 5V and PoE 5V) onto the same rail without them fighting each other or pushing reverse current back into each other.

We use two of them in an OR'ing configuration:
- LM66100 #1: USB-C 5V → +5V rail
- LM66100 #2: PoE 5V → +5V rail

Whichever source has a slightly higher voltage automatically wins and supplies the rail. The other one's LM66100 detects the output is higher than its input and shuts off, blocking reverse current.

**Pins (SOT-23-5 package):**
| Pin | Name | Connect to |
|---|---|---|
| IN | Input | Power source (USB_VBUS or POE_5V) |
| OUT | Output | +5V system rail |
| GND | Ground | GND |
| CE | Chip Enable | Short to OUT (enables auto reverse-blocking) |

**In KiCad:** Not in the default library — download from SnapEDA (search LM66100, download KiCad symbol + footprint). Add via Preferences → Manage Symbol Libraries.

---

## ERC Errors Explained — The Full Guide

### "Input Power pin not driven by any Output Power pins"

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

---

### "Pins of type Power output and Power output are connected"

Two pins defined as "Power output" are on the same net. KiCad sees two power sources fighting.

Three situations where this happens:

1. **PWR_FLAG left on a net that now has a real VOUT** → remove the PWR_FLAG
2. **Two LM66100 VOUTs both on +5V** → this is intentional (OR-ing circuit). Right-click → Exclude from ERC
3. **SIM_VDD (Output) + PWR_FLAG** → SIM_VDD is "Output" type (not "Power output"), but they still conflict. Keep the PWR_FLAG, right-click the SIM_VCC error → Exclude from ERC

---

### "Pins of type Output and Power output are connected"

A regular "Output" pin and a PWR_FLAG are on the same net. This is the SIM7080G SIM_VDD case — the pin is typed "Output" in the symbol, not "Power output", but PWR_FLAG is "Power output". They conflict.

Fix: keep the PWR_FLAG (so the SIM card VCC gets a power source), then exclude the specific error from ERC.

---

### The core rule for PWR_FLAG (final version)

> **PWR_FLAG = "I know power comes here, but the schematic doesn't show a component producing it."**
> 
> If any component's output pin is already on the net → no PWR_FLAG.  
> If the power comes from outside the schematic (USB cable, external supply, unfinished section) → add PWR_FLAG.

---

## What are strapping pins and why can't we use GPIO9 as CS_ETH?

**Strapping pins** are special GPIO pins that the chip reads at the exact moment of power-on or reset — before any firmware runs — to decide how to start up. The values on these pins during that brief window determine boot mode, so they need to be in a defined, deliberate state at power-on.

On the ESP32-C6, **GPIO9 is a strapping pin**:
- GPIO9 LOW at boot → boot normally from flash (run your program)
- GPIO9 HIGH at boot → enter download/bootloader mode (accept new firmware)

After the chip finishes booting, GPIO9 is released and becomes a regular GPIO. So technically you could use it for other purposes after boot — but there's a catch.

We wired GPIO9 with a 10kΩ pull-**down** resistor to GND (to ensure normal boot by default). CS (Chip Select) pins must idle **HIGH** — HIGH means "chip not selected, ignore the bus." A pull-down forces the pin LOW by default, which would mean the W5500 is permanently selected at power-on. That causes bus conflicts and undefined behaviour before the firmware even starts.

**Fix:** Move CS_ETH to GPIO2, which has no strapping function, no pull resistor, and no conflicts. Clean pin, clean CS line.

**Rule to remember:** Always check the datasheet for strapping pins before assigning GPIOs. Don't use them for signals that need a specific default state (like CS HIGH, or signals with external pull resistors that might conflict).

---

## Why does GPIO9 (BOOT pin) get a 10kΩ pull-down resistor to GND?

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

---

## Which side of an LED is the anode and which is the cathode?

In the KiCad LED symbol:

```
Anode (+) ──▶|── Cathode (−)
```

- **Anode** — the flat end of the triangle. The (+) side. Current flows IN here.
- **Cathode** — the bar/vertical line at the tip of the triangle. The (−) side. Current flows OUT here, to GND.

On a real physical LED:
- Anode → **longer leg**
- Cathode → **shorter leg** (also has a flat edge on the plastic lens)

In your schematic:
```
LED net (GPIO0) → 330Ω resistor → Anode → LED → Cathode → GND
```

Current flows from the GPIO, through the resistor (which limits how much), into the anode, out the cathode, to ground.

---

## What are the two pins on a Conn_Coaxial (U.FL connector)?

A `Conn_Coaxial` in KiCad represents a U.FL coaxial socket — the tiny RF connector that an antenna cable plugs into. It has two pins:

- **Pin 1** — the centre conductor (signal). This is where the RF signal travels. Connect to your antenna net (e.g. `LORA_ANT`, `ANT_NET`).
- **Pin 2** — the outer shield (ground). The metal shell around the connector. Connect to GND.

This matches how coax cable works physically: the inner wire carries the signal, the outer braid is ground.

---

## Why do crystals for different chips need different load cap values?

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

## Add more as you go...

> Every time something in KiCad or a datasheet confuses you, write the question and answer here. This file is for you.
