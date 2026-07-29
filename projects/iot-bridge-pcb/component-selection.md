# IoT Bridge PCB — Component Selection Document

> **Status:** Draft  
> **Phase:** Component Research & Selection  
> This document justifies every major IC choice before schematic work begins. Lock this down before touching KiCad.

---

## Table of Contents

1. [Main MCU](#1-main-mcu)
2. [LoRa Transceiver](#2-lora-transceiver)
3. [Cellular Module](#3-cellular-module)
4. [Ethernet Controller](#4-ethernet-controller)
5. [PoE Controller](#5-poe-controller)
6. [Power Auto-Switching](#6-power-auto-switching)
7. [Power Regulation](#7-power-regulation)
8. [Storage](#8-storage)
9. [Passives & Connectors](#9-passives--connectors)
10. [Block Diagram](#10-block-diagram)
11. [Open Questions](#11-open-questions)

---

## 1. Main MCU

### Selected: ESP32-C6 (variant: ESP32-C6-1U-N8)

| Spec | Value |
|---|---|
| Core | Single RISC-V @ 160 MHz |
| SRAM | 512 KB (+ 16 KB RTC SRAM) |
| ROM | 320 KB |
| Flash | 8 MB (built-in, N8 variant) |
| Wi-Fi | 802.11 b/g/n/ax (Wi-Fi 6, 2.4 GHz) |
| Bluetooth | BT 5.0 LE |
| 802.15.4 radio | Zigbee 3.0 + Thread 1.3 (same radio, time-shared) |
| GPIO | 23 configurable pins |
| Interfaces | SPI, I2C, UART, I2S, USB Serial/JTAG |
| Operating temp | -40°C to +85°C |
| Package | QFN-40 or as module |

**Why this chip:**  
The ESP32-C6 collapses four radios (Wi-Fi 6, BT5, Zigbee, Thread) into a single $3–5 chip with 8MB flash on-die. No external flash chip needed for the MCU itself. The `-1U` suffix means it exposes a U.FL/IPEX antenna connector instead of a PCB trace antenna — important here because the board will be inside an enclosure. The `N8` suffix confirms 8MB flash built in.

**What it does NOT have (and how we handle it):**
- No built-in Ethernet MAC → handled by W5500 over SPI
- No LoRa radio → handled by SX1262 over SPI
- No cellular → handled by SIM7080G over UART
- No 5G/LTE → out of scope per requirements

**Zigbee + Thread note:** Both protocols share the 802.15.4 radio. They cannot run simultaneously — firmware selects one mode at boot. For this bridge that's fine; the bridge will be pre-configured for whichever mesh protocol the deployment uses.

---

## 2. LoRa Transceiver

### Selected: Semtech SX1262

| Spec | Value |
|---|---|
| Frequency range | 150 – 960 MHz (covers 433, 868, 915 MHz bands) |
| TX power | Up to +22 dBm |
| RX sensitivity | Down to –148 dBm |
| RX current | 4.2 mA |
| Sleep current | < 1.5 µA |
| Interface | SPI + 3× DIO pins |
| Modulation | LoRa (CSS), FSK, GFSK |
| Package | QFN-24 |

**Why SX1262 over SX1276:**  
The SX1262 is the current-generation chip (SX1276 is the older one on the Heltec V2). The SX1262 delivers better sensitivity (–148 vs –137 dBm), lower current consumption, and a cleaner SPI command interface. The Heltec WiFi LoRa 32 V3 (the reference board in the brief) already uses the SX1262 — studying its schematic gives us a validated reference for wiring it to an ESP32.

**Dual-role operation (hub + end-node):**  
Both modes are software-defined using the same chip:
- **Hub mode:** SX1262 listens on a configured frequency/SF, receives packets from sensor nodes, ESP32 processes and forwards upstream via WiFi/Ethernet/cellular
- **LoRaWAN end-node mode:** ESP32 runs a LoRaWAN stack (e.g., RadioLib or LMIC), SX1262 transmits join requests and data frames to a LoRaWAN network server

**Required external components:**
- 32 MHz crystal (Crystal_GND24 symbol in KiCad — 4-pin with grounded case) with 10pF load caps
- PE4259 RF switch to route the single antenna between TX (RFO) and RX (RFI_N/RFI_P) paths — see Section 2A
- RF matching network (copy values from SX1262 datasheet section 14.6.2 exactly)
- U.FL coax connector (Conn_Coaxial in KiCad) for the antenna cable

---

## 2A. LoRa RF Switch

### Selected: Skyworks PE4259

| Spec | Value |
|---|---|
| Type | SPDT RF switch |
| Frequency | DC – 3 GHz |
| Insertion loss | ~0.4 dB |
| Isolation | ~30 dB |
| Control | Single logic pin (CTRL) |
| Supply (CTRL/VDD) | 1.8 – 3.6V |
| Package | SOT-26 (6-pin) |

**Why it's needed:**  
The SX1262 has separate TX (RFO) and RX (RFI_N / RFI_P) ports, but only one antenna is used. The PE4259 routes the shared antenna to the TX path when transmitting and the RX path when receiving. Without this switch, you would need two antennas or leave TX/RX permanently connected to the antenna (which degrades performance and risks damage).

**How it is controlled:**  
SX1262 DIO2 drives the CTRL pin via a 100Ω series resistor. The SX1262 automatically sets DIO2 HIGH during TX and LOW during RX. No firmware control needed — the chip handles it.

| CTRL pin state | PE4259 routing |
|---|---|
| HIGH (TX) | RFC → RF1 (to SX1262 RFO) |
| LOW (RX) | RFC → RF2 (to SX1262 RFI_N/RFI_P) |

**Pin connections:**
- CTRL (pin 4) → DIO2 via 100Ω resistor
- CTRL/VDD (pin 6) → +3V3 (logic supply — no decoupling cap needed)
- RFC (pin 5) → output matching network → U.FL connector
- RF1 (pin 1) → SX1262 RFO matching network
- RF2 (pin 3) → SX1262 RFI_N/RFI_P matching network
- GND (pin 2) → GND

**Symbol source:** Download from SnapEDA (not in KiCad standard library).

---

## 3. Cellular Module

### Selected: SIMCom SIM7080G

| Spec | Value |
|---|---|
| Standard | LTE Cat-M1 + NB-IoT + EGPRS (2G fallback) |
| Bands | Global multi-band |
| Data (LTE-M) | 588 kbps DL / 1119 kbps UL |
| Data (NB-IoT) | 589 kbps DL / 1800 kbps UL |
| GNSS | Built-in (GPS, GLONASS, BeiDou) — bonus |
| Interface | UART (AT commands) |
| SIM | Physical nano-SIM slot |
| eSIM | No onboard eSIM (see note) |
| Supply voltage | 3.0 – 4.2 V |
| Package | LCC (surface mount) |

**Why SIM7080G over SIM800L:**  
The brief says "GSM/GPRS" but this is likely loose terminology — the real requirement is cellular connectivity. The SIM800L is 2G only (GPRS), and 2G networks are being shut down globally (many African and European operators have already decommissioned 2G). Designing a bridge around a dead technology is a liability. The SIM7080G gives you:
- LTE Cat-M1 and NB-IoT (the correct cellular standards for IoT in 2025+)
- 2G/EGPRS fallback for areas without LTE-M coverage
- Built-in GNSS for location tracking (free feature, very useful for an IoT bridge)
- Lower power consumption than LTE modules like SIM7600

**Why not SIM7600 / Quectel EC21:**  
Those are LTE Cat 1 modules — appropriate for higher data throughput (video, large files). An IoT bridge sending MQTT payloads doesn't need that. Cat-M1/NB-IoT is the right tier: lower power, lower cost, optimized for exactly this use case.

**eSIM note:**  
The brief requests an eSIM footprint. The SIM7080G doesn't have one, so the design should include:
1. Physical nano-SIM card holder (primary)
2. An eSIM footprint (unpopulated pads for a future discrete eSIM chip like the KIGEN OS from ARM, or a Truphone/Eseye module) — label it DNP (Do Not Populate) on the BOM

**Power supply note:**  
The SIM7080G requires 3.0–4.2V — it cannot be powered directly from a 3.3V rail or 5V rail. A dedicated LDO or small buck converter (e.g., 3.8V) is needed for the cellular module. This is standard for all SIM modules.

---

## 4. Ethernet Controller

### Selected: WIZnet W5500

| Spec | Value |
|---|---|
| Type | Hardwired TCP/IP + MAC + PHY |
| Interface to MCU | SPI (up to 80 MHz) |
| Speed | 10/100 Mbps |
| Supply | 3.3V |
| Protocols | TCP, UDP, IPv4, ICMP, ARP, IGMP, PPPoE |
| Sockets | 8 independent hardware sockets |
| Package | QFN-48 or LQFP-48 |

**Why W5500:**  
The ESP32-C6 has no Ethernet MAC. The W5500 offloads the entire TCP/IP stack to dedicated hardware — the ESP32 just writes data to it over SPI and the W5500 handles framing, checksums, and transmission. This is far more efficient than a software TCP/IP stack running on the MCU. The W5500 is massively documented, has native support in ESP-IDF and Arduino core v3.x, and is proven in thousands of production IoT designs.

**Required external components:**
- Magjack (RJ45 with integrated magnetics and PoE pairs) — e.g., **HanRun HR911105A** or similar
- 25 MHz crystal for W5500's PHY
- Decoupling caps per datasheet

---

## 5. PoE Controller

### Selected: Texas Instruments PPS23730A0RMTT

> **Updated during schematic phase:** The originally specified TPS23730 was not found in the KiCad standard library. The PPS23730A0RMTT was found instead — it is in the same TI PoE PD controller family and has compatible functionality with an integrated DC-DC controller. It has 47 pins.

| Spec | Value |
|---|---|
| Standard | IEEE 802.3af/at compatible |
| DC-DC controller | Integrated |
| Pins | 47 (complex — place now, wire last in schematic) |
| Package | VQFN / similar |

**Why PPS23730A0RMTT:**  
It is a full PoE PD (Powered Device) controller + DC-DC controller in one chip. It handles the IEEE 802.3bt handshake with the PSE (the PoE switch/injector), draws power from the Ethernet cable, and steps it down to usable DC. Found in the KiCad standard library — avoids needing a custom symbol.

**What it outputs:**  
Drives an external transformer for isolation. Secondary side outputs regulated DC, targeted at 5V to feed into the power OR'ing circuit (net label: `POE_5V`).

**Schematic approach:**  
Place the symbol early, leave all pins unconnected, wire it last using the PPS23730 datasheet application circuit. It is the most complex section of the schematic.

**Original alternative noted:**  
TPS2375 (8-pin, 802.3af only, ~15.4W) + separate DC-DC is simpler but has less power headroom.

---

## 6. Power Auto-Switching

### Selected: Texas Instruments LM66100 × 2 (ORing configuration)

| Spec | Value |
|---|---|
| Input voltage range | 1.5 – 5.5 V |
| Max current | 1.5 A per device |
| Ron | 79 mΩ |
| Quiescent current | Low IQ |
| Package | SOT-23-5 |

**How the power tree works:**

```
PoE Input (48V, from RJ45)
    │
    ▼
TPS23730 (PoE PD Controller + DC-DC)
    │
    ▼
5V regulated (PoE path)
    │
    ├──► LM66100 #1 ──┐
                       ├──► 5V system rail ──► LDO to 3.3V
USB-C Input (5V)       │
    │                  │
    └──► LM66100 #2 ──┘
```

Two LM66100 ideal diodes in an ORing (highest-wins) configuration:
- When PoE is present and USB-C is not: PoE supplies the 5V rail, LM66100 #2 blocks reverse flow into the USB-C port
- When USB-C is present and PoE is not: USB-C supplies the 5V rail, LM66100 #1 blocks reverse flow into the PoE circuit
- When both are present: PoE takes priority (its output is regulated to exactly 5V; USB-C is also 5V — the one with marginally higher voltage wins and the other is blocked automatically)

**USB-C power delivery note:**  
For basic 5V/900mA operation (USB-C default), no PD negotiation chip is needed. If we want to negotiate higher power (9V, 12V, 20V profiles), a USB PD controller like FUSB302 would be needed. For this design, 5V default is fine — USB-C is only a fallback/programming port.

**USB-C port also serves programming/debug:**  
The ESP32-C6 has a built-in USB Serial/JTAG controller. The USB-C connector routes D+ and D- directly to the ESP32-C6's USB pins for flashing and debug — no external USB-to-UART chip (like CP2102) required.

---

## 7. Power Regulation

### 5V → 3.3V: Texas Instruments TLV1117-33 LDO

| Spec | Value |
|---|---|
| Type | LDO linear regulator |
| Output | 3.3V fixed |
| Max current | 800 mA |
| Dropout | ~1.1V at full load |
| Package | SOT-223 |

Supplies: ESP32-C6, SX1262, W5500, SD card, LEDs, button pull-ups.

### 5V → 3.8V: Separate LDO for SIM7080G

The SIM7080G requires 3.0–4.2V. A dedicated **AP2112K-3.8** or **MIC5219** LDO set to 3.8V isolates the noisy cellular module from the main 3.3V rail. This is standard practice — GSM/LTE modules draw large current spikes during transmission and can corrupt the 3.3V rail if not isolated.

---

## 8. Storage

### External Flash: Winbond W25Q64JV (if needed)

The ESP32-C6-1U-N8 already has 8MB flash on-die. This is sufficient for:
- Dual OTA partitions (~3.5MB each)
- NVS (non-volatile storage for config)
- SPIFFS/LittleFS filesystem

No additional flash chip is required. If more storage is needed in a future revision, add a W25Q128 (16MB, SPI) — footprint can be included as DNP.

### MicroSD Card Slot

Standard **push-push MicroSD slot** (e.g., Molex 1040310811 or Amphenol 101-00660-68). Connects to ESP32-C6 over SPI (shares the SPI bus with W5500 and SX1262, using separate CS lines).

**SD card notes:**
- Operates at 3.3V (SD cards are 3.3V native in SPI mode)
- 10kΩ pull-ups on MOSI, CLK, CS lines recommended
- Used for data logging and config files per the brief

---

## 9. Passives & Connectors

| Component | Part | Notes |
|---|---|---|
| RJ45 with magnetics | HanRun HR911105A or Amphenol RJE7318800310 | Integrated Bob Smith termination and PoE pairs |
| USB-C receptacle | USB4105-GF-A (GCT) or XKB U262-161N-4BVC11 | Mid-mount or top-mount, 16-pin |
| SIM card holder | Amphenol 101-00064-68 (nano-SIM, push-pull) | Standard nano-SIM, 6-pin |
| MicroSD slot | Molex 1040310811 (push-push) | SPI mode |
| Tactile button | C&K PTS636 or TE FSM4JSMATR | SMD, 4-pin, 6mm |
| Status LED | Lite-On LTST-C191TBKT (blue) or RGB: Kingbright APFA3010LSEEZGKQBKC | Driven via GPIO through 330Ω resistor |
| U.FL connectors | Hirose U.FL-R-SMT-1(80) | One each for: ESP32-C6 antenna, SX1262, cellular |

---

## 10. Block Diagram

```
                        ┌───────────────────────────────────────────────────┐
                        │                  ESP32-C6-1U-N8                   │
                        │                                                   │
                        │  Wi-Fi 6  │  BT5 LE  │  Zigbee/Thread (802.15.4) │
                        │                                                   │
   SX1262 ◄──── SPI ───►│  SPI bus                                          │
   W5500  ◄──── SPI ───►│  (shared, separate CS lines)                      │
   MicroSD◄──── SPI ───►│                                                   │
                        │  UART ────────────────────────────► SIM7080G      │
                        │                                                   │
                        │  USB D+/D─ ─────────────────────── USB-C port     │
                        └───────────────────────────────────────────────────┘
                                │                        │
                           3.3V rail                3.8V rail
                                │                        │
                         TLV1117-33               AP2112K-3.8
                                │                        │
                            ┌───┴────────────────────────┘
                            │           5V system rail
                            │
               ┌────────────┴────────────┐
               │                         │
          LM66100 #1                LM66100 #2
               │                         │
       PPS23730A0RMTT (PoE)       USB-C 5V input
               │
       RJ45 + Magnetics
       (PoE 48V from switch)


Antennas (all via U.FL):
  ESP32-C6 ─────── 2.4GHz antenna  (Wi-Fi / BT / Zigbee / Thread)
  SX1262   ─────── Sub-GHz antenna (LoRa 868/915 MHz)
  SIM7080G ─────── LTE antenna
  SIM7080G ─────── GNSS antenna    (separate port on module)
```

---

## 11. Open Questions

- [ ] **Antenna placement:** All four antennas need to be separated on the PCB edge with ground plane cutouts beneath them. Need to decide board size and antenna layout before starting layout.
- [ ] **SPI bus contention:** W5500, SX1262, and MicroSD share SPI. SX1262 is the limiting device at 16 MHz — run the whole bus at 16 MHz.
- [ ] **eSIM footprint:** Identify a specific eSIM module footprint to include as DNP pads. Candidates: Truphone TP-000-0001, Sierra Wireless WP7702.
- [x] **USB-C CC resistors:** ✅ Resolved — 5.1kΩ to GND on both CC1 and CC2. No PD controller needed for 5V/900mA default.
- [x] **Regulatory bands:** ✅ Resolved — **868 MHz** confirmed. Nigeria is ITU Region 1, same band as Europe.
- [x] **ESP32-C6 SPI peripheral count:** ✅ Resolved — shared SPI bus with separate CS lines (CS_ETH on GPIO2, CS_LORA on GPIO10, CS_SD on GPIO11). Bus runs at 16 MHz to satisfy SX1262 limit.

---

## Summary BOM (Major ICs)

| # | Component | Part Number | Function |
|---|---|---|---|
| 1 | MCU | ESP32-C6-1U-N8 | Main processor, Wi-Fi 6, BT5, Zigbee, Thread |
| 2 | LoRa transceiver | Semtech SX1262 | LoRa hub + LoRaWAN end-node |
| 3 | Cellular module | SIMCom SIM7080G | LTE Cat-M1 / NB-IoT / 2G fallback + GNSS |
| 4 | Ethernet controller | WIZnet W5500 | 10/100 Ethernet over SPI |
| 5 | PoE PD controller | TI PPS23730A0RMTT | PoE powered device + integrated DC-DC |
| 6 | Ideal diode × 2 | TI LM66100 | PoE + USB-C power ORing |
| 7 | 3.3V LDO | TLV1117-33 | Main 3.3V rail |
| 8 | 3.8V LDO | AP2112K-3.8 | Isolated cellular supply |
| 9 | LoRa RF switch | Skyworks PE4259 | TX/RX antenna switching for SX1262 |
| 10 | MicroSD slot | Molex 1040310811 | Local storage |
| 11 | USB-C receptacle | USB4105-GF-A | Power + programming |
| 12 | RJ45 w/ magnetics | HanRun HR911105A | Ethernet (MagJack — integrated magnetics) |
| 13 | nano-SIM holder | Amphenol 101-00064-68 | Physical SIM |

---

## Learning Notes (merged from `learning.md`, split out 2026-07-27)

> The sections below were moved here from the old flat `learning.md` file when learning notes were split into topic-scoped files. Content is verbatim from the original — only heading levels were adjusted to nest under this section.

### What is Zigbee and Thread? What are they used for?

Both are **low-power mesh networking protocols** for smart devices. They both run on the **IEEE 802.15.4 radio standard** at 2.4GHz — the same physical radio, different software on top.

**Mesh** means devices relay messages through each other. A door sensor too far from the hub sends its packet through a light bulb, which passes it through a plug socket, which reaches the hub. The network heals itself if one device drops out.

**Zigbee (2004)**
The established smart home standard. Used in: Philips Hue, IKEA Tradfri, Samsung SmartThings, most smart plugs, sensors, and bulbs you can buy today. Requires a central **coordinator** (hub/bridge) to manage the network. Not IP-based — devices don't have internet addresses, they use Zigbee-specific IDs. Huge installed base.

**Thread (2014)**
Designed to fix Zigbee's weaknesses. The key difference: Thread is **IP-based** — every device gets a real IPv6 address, so it can be addressed directly like any internet device. No single point of failure — any device can act as the border router. Backed by Apple, Google, Amazon, Samsung. Powers the **Matter** protocol — the new universal smart home standard that all major ecosystems (HomeKit, Google Home, Alexa) have agreed to support.

**Why both on this bridge?**
Zigbee covers the massive existing market of smart home devices. Thread/Matter covers everything being built now and going forward. The ESP32-C6's single 802.15.4 radio handles both — firmware chooses which protocol is active at runtime.

### What's the difference between WiFi 4 and WiFi 6?

The numbers (4, 5, 6) are marketing names for 802.11 generations:
- WiFi 4 = 802.11n (2009)
- WiFi 5 = 802.11ac (2013)
- WiFi 6 = 802.11ax (2019)

For IoT, the headline speed difference doesn't matter. What matters:

**OFDMA** — WiFi 6 can talk to multiple devices simultaneously on the same channel. WiFi 4 can only serve one device at a time. In a house with 50 smart devices, WiFi 6 routers handle the traffic far more efficiently.

**TWT (Target Wake Time)** — the killer IoT feature. WiFi 6 devices can negotiate a schedule with the router: "I'll wake up every 10 minutes, send my data packet, then sleep again." Between those windows, the WiFi radio is completely off. This dramatically reduces power consumption for battery-powered devices. WiFi 4 has no equivalent — devices have to stay awake listening for the router constantly.

**Dense environments** — WiFi 6 uses BSS Coloring to reduce interference in apartment buildings or offices where many networks overlap. WiFi 4 degrades badly in the same conditions.

For this bridge: the ESP32-C6's WiFi 6 support means it works better in environments with many devices, and any WiFi 6 devices connecting to it can use TWT for battery savings.

### REYAX RYLR998 — The LoRa Module I Used Before

The RYLR998 is a ready-made LoRa module made by REYAX Technology. The important thing to know: **it is built around the Semtech SX1262 chip** — the same chip we're using bare on this PCB. You've already worked with the heart of our LoRa design.

#### RYLR998 Specs
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

#### How You Used It vs How We Use SX1262 Now

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

#### Common AT Commands on the RYLR998
```
AT               → ping the module (responds OK)
AT+BAND=868000000 → set frequency to 868 MHz
AT+ADDRESS=1     → set device address
AT+NETWORKID=6   → set network ID (both sides must match)
AT+SEND=0,5,HELLO → send "HELLO" (5 bytes) to address 0
AT+PARAMETER=9,7,1,12 → set SF9, BW125, CR4/5, preamble 12
```

#### Why We're Not Using the RYLR998 on This PCB

The RYLR998 is great for prototyping but not ideal for a custom PCB:
1. **Size** — it's a module with its own PCB, which sits on top of yours. The bare SX1262 is a tiny QFN chip that integrates directly.
2. **Cost at volume** — a RYLR998 module costs ~$8-15. A bare SX1262 chip is ~$3.
3. **Control** — with the bare chip, we configure every LoRa parameter directly and can integrate LoRaWAN stacks (RadioLib) with more flexibility.
4. **PCB integration** — the bare chip sits flat on the board. A module adds height and requires its own mounting footprint.

If you were prototyping this project on a breadboard, you'd use the RYLR998. Since we're designing a custom PCB, we use the SX1262 directly.

### What alternative components could we have used?

If the ESP32-C6 wasn't an option (unavailable, wrong package, etc.) here's what we'd have needed:

#### For WiFi + Bluetooth
| Alternative | Notes |
|---|---|
| ESP32-S3 | Dual core, more GPIO, no Zigbee/Thread — would need separate 802.15.4 chip |
| ESP32-C3 | Cheaper, smaller, no Zigbee/Thread |
| CYW43439 | Used in Raspberry Pi Pico W, WiFi 4 + BT 5 only |
| nRF7002 | Nordic's WiFi 6 companion chip (needs a host MCU alongside it) |

#### For Zigbee / Thread (802.15.4)
| Alternative | Notes |
|---|---|
| Nordic nRF52840 | ARM Cortex-M4, excellent BLE + 802.15.4, very popular for Thread/Matter |
| TI CC2652R | TI's dedicated Zigbee/Thread/BLE chip, used in many commercial hubs |
| Silicon Labs EFR32MG | Used in Samsung SmartThings, very capable but expensive |
| nRF52833 | Smaller/cheaper nRF52840, same radio capabilities |

With any of these, you'd need the MCU (ESP32-S3) connected to the 802.15.4 chip over SPI or UART — two chips instead of one.

#### For LoRa
| Alternative | Notes |
|---|---|
| SX1276 | Previous generation Semtech chip, lower sensitivity than SX1262, still widely used |
| SX1278 | Same as SX1276 family, 433MHz focused |
| RFM95W | A module (not bare chip) using the SX1276 inside — easier to prototype with |
| LR1110 | Semtech's newer multi-standard chip (LoRa + WiFi geolocation + GNSS) — overkill |

We chose SX1262 because it's the current generation with better sensitivity and lower power.

#### For Cellular
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

#### For Ethernet
| Alternative | Notes |
|---|---|
| ENC28J60 | Older, SPI-based, no hardwired TCP/IP stack — MCU does more work |
| LAN8720A | Ethernet PHY only (no MAC/TCP) — needs MCU with built-in Ethernet MAC |
| W6100 | WIZnet's newer chip, adds IPv6 support over the W5500 |

We chose W5500 because it has the full TCP/IP stack in hardware, is massively documented, and works directly with ESP32 over SPI.

#### For PoE
| Alternative | Notes |
|---|---|
| TPS2375 | Simpler 8-pin 802.3af only (15.4W max) — less power headroom but easier to design with |
| PD70101 | Microchip's PoE PD controller, common in enterprise equipment |
| AG9800 | Integrated PoE PD + DC-DC, similar to TPS23730 |

We chose TPS23730 for 802.3bt support (51W headroom) and the integrated DC-DC controller.

### Why the ESP32-C6 and not another ESP32 variant?

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

### Why LoRa at 868 MHz and not 915 MHz or 433 MHz?

Radio frequencies for unlicensed (no licence required) use are regulated by region:

- **Region 1 (Europe, Middle East, Africa)** → 868 MHz ISM band
- **Region 2 (Americas)** → 915 MHz ISM band
- **Region 3 (Asia-Pacific)** → 433 MHz or 923 MHz depending on country

Nigeria falls under **ITU Region 1**, so 868 MHz is the correct band. Using 915 MHz in Nigeria would still work electrically, but it would be operating outside the licensed band — a regulatory problem if the product is ever certified.

The SX1262 covers 150–960 MHz so it can do either, but the antenna design and RF matching network on the PCB needs to be tuned for one specific frequency.

### What is PoE and why does it need a special IC?

**PoE (Power over Ethernet)** sends DC power over the unused wire pairs (or spare pairs) in an Ethernet cable — so you only need one cable to a device instead of separate power and network cables.

The problem: PoE uses 48V (much higher than the 3.3V–5V our board needs), and not all Ethernet cables/switches support PoE. The IEEE 802.3 standard defines a handshake protocol so PoE devices don't accidentally fry non-PoE equipment.

The **TPS23730** is a **PD (Powered Device) controller** — it:
1. Performs the IEEE 802.3 handshake with the PoE switch to negotiate power
2. Converts the 48V from the cable down to a usable voltage (we target 5V) via an internal DC-DC controller
3. Protects the circuit if the voltage/current exceeds safe limits

Without this IC, you'd have to design all of that yourself. This is why you don't just wire the Ethernet cable directly to your board.

### What does "DNP" mean on a BOM?

**DNP = Do Not Populate.** It means the footprint (pad pattern) is on the PCB, but the component is not soldered during this revision. The pads are there for a future version.

We used this for the eSIM footprint — the SIM7080G doesn't have an eSIM, so we included unpopulated pads where a discrete eSIM chip could be soldered in a future revision. Manufacturing the board with empty pads costs nothing extra and saves redesigning the PCB later.

### What is a Polyfuse?

A polyfuse (resettable fuse / PPTC) is a protection component placed on the USB-C VBUS line. It limits current to a set value (500mA on our board) and protects the circuit from overcurrent faults.

**Regular fuse vs polyfuse:**
- Regular fuse: blows permanently when overcurrent occurs — you replace it
- Polyfuse: trips when overcurrent occurs (resistance jumps to near-infinite), then **resets itself** once the fault is removed and it cools down

**How it works:** The polymer material inside is normally conductive. Too much current → heats up → polymer expands → resistance skyrockets → current drops to near zero → fault is cleared → cools down → resets.

**Why we use it on USB-C VBUS:** If something on the board short-circuits and tries to pull 2A through the USB port, the 500mA polyfuse trips and prevents damage to the USB source. Without it, you could fry the host computer's USB port or the board itself.

In KiCad: press `A`, search `Polyfuse` or `Fuse_Resettable`. Set value to `500mA`.

### What is the LM66100?

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
