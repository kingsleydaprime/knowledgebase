# IoT Bridge PCB — Design Report

![IT Consortium Logo](itc-logo.png)

**Project Title:** Universal IoT Bridge PCB Design  
**Author:** Kingsley Ihemelandu  
**Organisation:** IT Consortium  
**Department:** Research Department  
**Date:** June 2026  
**Revision:** v0.1 — Schematic Phase  
**Status:** Schematic substantially complete — PCB layout and PoE controller wiring outstanding

---

## Abstract

This report documents the design of a universal IoT Bridge printed circuit board (PCB) intended to serve as a central communication hub for IoT edge device deployments. The bridge is designed to support simultaneous operation across multiple wireless protocols — including Wi-Fi 6, Bluetooth 5 Low Energy, Zigbee 3.0, Thread 1.3, LoRa, and cellular (LTE Cat-M1 / NB-IoT) — while providing wired Ethernet connectivity with Power over Ethernet (PoE) support.

The design is exploratory in nature, with the objective of validating component compatibility, feature integration, and PCB layout strategies before a production version is finalised. This document covers the component selection rationale, system architecture, design decisions made during the schematic phase, and the tools used throughout the design process. Elements of this design may be adapted, refined, or omitted in a subsequent production revision.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Component Selection](#3-component-selection)
4. [Design Decisions](#4-design-decisions)
5. [Tools & Software](#5-tools--software)
6. [Schematic Progress](#6-schematic-progress)
7. [Work Completed](#7-work-completed)
8. [Outstanding Work](#8-outstanding-work)
9. [KiCad Familiarisation](#9-kicad-familiarisation)
10. [Deliverables](#10-deliverables)
11. [Project Repository](#11-project-repository)
12. [References](#12-references)

---

## 1. Project Overview

### 1.1 Background

IoT deployments increasingly require a single gateway device capable of communicating with heterogeneous edge nodes — sensors, actuators, and smart devices that speak different wireless protocols. A device that can bridge LoRa sensor nodes, Zigbee smart home devices, BLE peripherals, and Thread/Matter devices simultaneously — while maintaining cloud connectivity over Ethernet or cellular — represents significant value in both commercial and industrial IoT applications.

### 1.2 Objectives

- Design a PCB that integrates the major IoT wireless protocols into a single device
- Support dual power inputs (PoE and USB-C) with automatic failover
- Provide both local storage (MicroSD) and over-the-air (OTA) firmware update capability
- Ensure the design is modular and maintainable, with clear documentation to guide a potential production revision

### 1.3 Scope

This design is a feature exploration prototype. It is not intended for immediate mass production. The scope covers schematic design, component selection, PCB layout, and generation of manufacturing files (Gerbers, BOM).

### 1.4 Key Features

| Feature | Implementation |
|---|---|
| Wi-Fi 6 (802.11ax) | ESP32-C6-WROOM-1 (built-in) |
| Bluetooth 5 LE | ESP32-C6-WROOM-1 (built-in) |
| Zigbee 3.0 | ESP32-C6-WROOM-1 (built-in, 802.15.4 radio) |
| Thread 1.3 / Matter | ESP32-C6-WROOM-1 (built-in, shared 802.15.4 radio) |
| LoRa (hub + LoRaWAN end-node) | Semtech SX1262 |
| Cellular (LTE Cat-M1 / NB-IoT) | SIMCom SIM7080G |
| GNSS / GPS | SIM7080G (built-in) |
| Wired Ethernet (10/100) | WIZnet W5500 |
| Power over Ethernet | TI PPS23730A0RMTT |
| USB-C (power + programming) | Native ESP32-C6 USB Serial/JTAG |
| Flash Storage | 8MB on-module (ESP32-C6-WROOM-1-N8) |
| Removable Storage | MicroSD card slot (SPI) |
| Status Indicator | RGB LED |
| User Input | Tactile push button |

---

## 2. System Architecture

### 2.1 Block Diagram

```
                    ┌──────────────────────────────────────────────────┐
                    │          ESP32-C6-WROOM-1 (Main MCU)             │
                    │                                                  │
                    │   Wi-Fi 6 | BT 5 LE | Zigbee 3.0 | Thread 1.3    │
                    │                                                  │
   SX1262 ◄─ SPI ──►│  SPI Bus                                         │
   W5500  ◄─ SPI ──►│  (shared MOSI/MISO/SCK, individual CS lines)     │
   MicroSD◄─ SPI ──►│                                                  │
                    │  UART ─────────────────────────────► SIM7080G    │
                    │  USB D+/D- ────────────────────────► USB-C Port  │
                    └──────────────────────────────────────────────────┘
                              │                    │
                          +3V3 rail            +3V8 rail
                              │                    │
                       TLV1117-33           AP2112K-3.8
                              └──────┬─────────────┘
                                     │
                               +5V system rail
                                     │
                      ┌──────────────┴──────────────┐
                      │                             │
                 LM66100 #1                    LM66100 #2
                      │                             │
             PPS23730A0RMTT (PoE)          USB-C VBUS (5V)
                      │
             RJ45 + Magnetics
             (PoE 48V input)

Antennas (all via U.FL connectors on enclosure exterior):
  ESP32-C6  ── 2.4 GHz   (Wi-Fi / BT / Zigbee / Thread)
  SX1262    ── 868 MHz    (LoRa — Region 1)
  SIM7080G  ── LTE        (Cellular)
  SIM7080G  ── GNSS       (GPS/GLONASS — separate port)
```

### 2.2 Power Architecture

The board supports two independent power inputs that are automatically OR'd together using ideal diode controllers:

- **PoE input:** 48V from Ethernet cable → TPS23730 PD controller → 5V regulated
- **USB-C input:** 5V from USB connector

Both 5V sources feed into a pair of LM66100 ideal diode controllers. The higher of the two voltages supplies the system rail automatically, with no manual switching required and no risk of reverse current damage.

From the 5V system rail, two voltage regulators produce the required supply voltages:
- **3.3V (TLV1117-33):** Powers the ESP32-C6, W5500, SX1262, and MicroSD
- **3.8V (AP2112K-3.8):** Powers the SIM7080G exclusively (isolated to prevent cellular noise from affecting other components)

---

## 3. Component Selection

### 3.1 Rationale Summary

| Component | Selected Part | Key Justification |
|---|---|---|
| MCU | ESP32-C6-WROOM-1-N8 | Only ESP32 variant with 802.15.4 (Zigbee + Thread) + Wi-Fi 6 + BT5 in one chip |
| LoRa Transceiver | Semtech SX1262 | Current-generation chip; −148 dBm sensitivity; same chip inside RYLR998 module |
| Cellular | SIMCom SIM7080G | LTE Cat-M1 + NB-IoT + GNSS; correct IoT tier; 2G fallback |
| Ethernet Controller | WIZnet W5500 | Hardwired TCP/IP stack; SPI interface; well-supported in ESP-IDF |
| PoE Controller | TI PPS23730A0RMTT | PoE PD controller with integrated DC-DC; same TPS23730 family; 47-pin; found in KiCad library |
| LoRa RF Switch | Skyworks PE4259 | SPDT RF switch routing single antenna between SX1262 TX and RX paths; controlled by DIO2 |
| Power OR'ing | TI LM66100 ×2 | Ideal diode OR'ing; near-zero voltage drop |
| 3.3V Regulator | TLV1117-33 | Low-noise LDO; sufficient for all 3.3V loads |
| 3.8V Regulator | AP2112K-3.8 | Dedicated isolated supply for cellular module |

> Full component research, alternative options considered, and detailed justifications are documented in `component-selection.md`.

---

## 4. Design Decisions

| Decision | Choice Made | Rationale |
|---|---|---|
| MCU module vs bare chip | WROOM-1 module | Integrated antenna matching, decoupling, and FCC certification simplify design |
| LoRa frequency band | 868 MHz | Nigeria is ITU Region 1 — same band as Europe |
| Zigbee vs Thread | Firmware-selectable | Both share the 802.15.4 radio; one active at a time based on deployment |
| USB-C power mode | 5V default (900mA) | 5.1kΩ CC resistors only; no USB PD controller needed for this use case |
| External flash | None added | ESP32-C6-WROOM-1-N8 has 8MB on-module — sufficient for dual OTA + filesystem |
| eSIM | DNP footprint | SIM7080G has no eSIM; pads reserved for future revision |
| SPI bus speed | 16 MHz max | SX1262 is the limiting device at 16 MHz; W5500 and SD card configured to match |
| Cellular supply | Separate 3.8V LDO | Isolates high current-spike cellular transmissions from sensitive 3.3V rail |
| LoRa antenna switching | PE4259 RF switch | SX1262 has separate TX (RFO) and RX (RFI_N/RFI_P) ports; PE4259 routes single antenna between them. DIO2 controls it automatically |
| W5500 RJ45 | HR911105A MagJack | Integrated magnetics — no separate transformer needed. Centre tap to +3V3 via 49.9Ω resistor per datasheet |
| PWR_FLAG usage | Only on externally-sourced nets | Nets with LDO VOUT pins do not need PWR_FLAG. Only USB_VBUS (from cable) and POE_5V (PPS23730 not yet wired) require it |

---

## 5. Tools & Software

### 5.1 PCB Design

**KiCad 8.x** — Open-source PCB design suite used for schematic capture and PCB layout.
- *Schematic Editor (Eeschema):* Draws the logical connections between all components
- *PCB Editor (Pcbnew):* Physical placement and copper routing
- *Footprint Editor:* Creating/editing component pad patterns
- *Gerber Viewer:* Verifying manufacturing files before submission

**Espressif KiCad Libraries** — Official symbol and footprint library from Espressif for all ESP32 components. Downloaded from the Espressif GitHub repository and added to KiCad's symbol library manager.

**Component Libraries Used in KiCad:**
- `Device` — standard passive components (resistors, capacitors)
- `Connector` — USB-C, RJ45, headers
- `Switch` — tactile push buttons (SW_Push)
- `espressif` — ESP32-C6-WROOM-1 symbol and footprint
- `power` — power symbols (+3V3, GND, +5V, PWR_FLAG)

### 5.2 Planned Firmware Tools

| Tool | Purpose |
|---|---|
| **ESP-IDF** | Espressif's official C/C++ development framework for ESP32. Provides FreeRTOS, WiFi/BT stack, GPIO drivers, SPI/UART/I2C APIs |
| **FreeRTOS** | Real-time operating system built into ESP-IDF. Manages concurrent tasks (reading LoRa while serving MQTT while checking Ethernet) |
| **RadioLib** | Arduino/ESP-IDF library for controlling the SX1262 LoRa transceiver over SPI. Supports both raw LoRa and LoRaWAN |
| **LwIP** | Lightweight TCP/IP stack used within ESP-IDF for network communication |
| **ESP-MQTT** | MQTT client library built into ESP-IDF for publishing sensor data to a broker |

### 5.3 Reference Materials Used

| Document | Source | Used For |
|---|---|---|
| ESP32-C6 Datasheet | Espressif (espressif.com) | Pin definitions, power requirements, GPIO capabilities |
| ESP32-C6-WROOM-1 Datasheet | Espressif | Module pinout, antenna design, footprint dimensions |
| SX1262 Datasheet | Semtech | SPI wiring, RF matching network, LoRa parameters |
| PPS23730A0RMTT Datasheet | Texas Instruments | PoE PD + DC-DC application circuit, transformer selection |
| PE4259 Datasheet | Skyworks Solutions | RF switch wiring, CTRL/VDD supply, truth table |
| HR911105A Datasheet | Hanrun / Bothhand | MagJack RJ45 pinout, centre tap wiring, integrated magnetics |
| W5500 Datasheet | WIZnet | SPI interface, crystal requirements, RJ45 wiring |
| SIM7080G Hardware Guide | SIMCom | Power supply requirements, antenna connections, AT command interface |
| Heltec WiFi LoRa 32 V3 Schematic | Heltec | Reference for ESP32 + SX1262 integration |
| AN4488 Application Note | STMicroelectronics | General hardware design best practices (used as reference) |

---

## 6. Schematic Progress

| Section | Status | Notes |
|---|---|---|
| ESP32-C6 MCU | Complete | 3V3 + decoupling caps ✓, EN circuit ✓, BOOT circuit ✓, all GPIO net labels placed ✓, unused pins no-connect ✓ |
| Power — USB-C Connector | Complete | VBUS → polyfuse → USB_VBUS ✓, CC1/CC2 → 5.1kΩ → GND ✓, D+/D- labeled ✓ |
| Power — OR'ing (LM66100 × 2) | Complete | LM66100 #1 (USB path) ✓, LM66100 #2 (PoE path) ✓, both VOUT → +5V ✓, CE → GND ✓ |
| Power — TLV1117-33 (3.3V LDO) | Complete | VIN → +5V, VOUT → +3V3, decoupling caps ✓ |
| Power — AP2112K-3.8 (3.8V LDO) | Complete | VIN → +5V, VOUT → +3V8, EN → +5V, decoupling caps ✓ |
| Power — PPS23730A0RMTT (PoE) | Placed, not wired | All pins no-connect. Wire last using datasheet application circuit. |
| SX1262 LoRa Transceiver | Complete | SPI/control pins ✓, power pins ✓, crystal (32 MHz, 10pF caps) ✓, PE4259 RF switch wired ✓, Conn_Coaxial (U.FL) ✓, RF matching network pending (copy from datasheet 14.6.2) |
| W5500 Ethernet Controller | In Progress | SPI/control ✓, PMODE → +3V3 ✓, EXRES1 → 12.4kΩ ✓, VBG/TOCAP/1V2O caps ✓, crystal (25 MHz, 20pF caps) ✓, RJ45 HR911105A wiring in progress |
| SIM7080G Cellular Module | In Progress | VBAT → +3V8 ✓, UART wired ✓, PWRKEY ✓, SIM card connected ✓, antenna U.FL connectors placed ✓, unused pins no-connect in progress |
| MicroSD Slot | Complete | SPI mode pin mapping applied, pull-up resistors on signal lines ✓ |
| User Interface (Button + LED) | Complete | SW_Push with pull-up + debounce cap ✓, LED with 330Ω resistor ✓ |
| Debug Header (UART 4-pin) | Complete | Conn_01x04 with +3V3, UART_TX, UART_RX, GND ✓ |
| ERC | In Progress | 2 remaining errors: USB_VBUS needs PWR_FLAG, LM66100 OR-ing conflict to exclude |

---

## 7. Work Completed

The following schematic sections were fully designed during this internship:

### Schematic Design
- **ESP32-C6 MCU** — power pins, decoupling capacitors, EN/reset circuit (10kΩ pull-up + 100nF), BOOT circuit (10kΩ pull-down + button), all GPIO net labels assigned, unused pins marked no-connect
- **USB-C Connector** — VBUS through 500mA polyfuse, CC1/CC2 pull-down resistors (5.1kΩ) for 5V/900mA negotiation, D+/D- routed to ESP32
- **Power OR-ing (LM66100 × 2)** — ideal diode OR-ing of USB-C and PoE 5V sources onto shared +5V system rail; CE pins tied to GND (active-low enable)
- **3.3V LDO (TLV1117-33)** — input and output decoupling caps; supplies ESP32-C6, W5500, SX1262, MicroSD
- **3.8V LDO (AP2112K-3.8)** — isolated cellular supply; EN tied to +5V; supplies SIM7080G exclusively
- **SX1262 LoRa Transceiver** — all SPI/control pins wired, power pins with decoupling, 32 MHz crystal with 10pF load caps, PE4259 RF switch for TX/RX antenna routing (DIO2 → 100Ω → CTRL), RF matching network (values from datasheet section 14.6.2), U.FL coaxial connector for LoRa antenna
- **W5500 Ethernet Controller** — SPI bus and control pins, PMODE pins for auto-negotiation, EXRES1 (12.4kΩ), internal voltage output decoupling (VBG/TOCAP/1V2O), 25 MHz crystal with 20pF load caps, HR911105A MagJack with differential pair connections and centre-tap resistors
- **SIM7080G Cellular Module** — VBAT to dedicated +3V8 rail with bulk capacitors, UART to ESP32, PWRKEY, SIM card holder (VCC, RST, CLK, DATA, GND), two U.FL connectors (LTE antenna, GNSS antenna), unused pins no-connect
- **MicroSD Slot** — SPI mode pin mapping, 10kΩ pull-ups on signal lines, VDD decoupling
- **User Button** — pull-up resistor with debounce capacitor
- **Status LED** — 330Ω current-limiting resistor, anode to GPIO, cathode to GND
- **Debug Header** — 4-pin UART header (3V3, TX, RX, GND)
- **PPS23730A0RMTT PoE Controller** — symbol placed on schematic, all pins temporarily no-connect (see Outstanding Work)

### Component Selection & Research
- Evaluated and justified all major IC choices (documented in component-selection.md)
- Identified correct LoRa frequency band for Nigeria (868 MHz — ITU Region 1)
- Selected HR911105A MagJack to eliminate need for separate Ethernet transformer
- Identified PPS23730A0RMTT as available KiCad substitute for TPS23730

### Design Documentation
- Maintained schematic-notes.md with all wiring decisions and pin-level connections
- Maintained learning.md with explanations of every concept encountered
- Maintained component-selection.md with full justification for every major part

---

## 8. Outstanding Work

The following items remain incomplete at the end of the internship period:

### Phase 1 — Complete the Schematic
| Item | Reason incomplete | Estimated effort |
|---|---|---|
| **PPS23730A0RMTT PoE controller wiring** | 47-pin device requiring external transformer, MOSFET, feedback network, and compensation components. Requires datasheet application circuit to be copied exactly — significantly more complex than any other section. Left last intentionally. | 3–5 hours with datasheet open |
| **SX1262 RF matching network values** | Component values (inductors and capacitors between SX1262 and PE4259) must be copied from SX1262 datasheet section 14.6.2. | 1 hour |
| **ERC clean to 0 errors** | Currently 2 remaining: USB_VBUS needs PWR_FLAG; LM66100 OR-ing "two power outputs" to be excluded. | 15 minutes |

### Phase 2 — PCB Layout
This is a full separate phase of work that follows schematic completion. It involves transitioning from the logical schematic into a physical board design.

| Item | Notes |
|---|---|
| **Assign footprints** | Each schematic symbol needs a matching PCB footprint (physical pad size and spacing). Every component must be linked to a footprint before layout can begin. |
| **Component placement** | Physically arrange all components on the board. Key considerations: RF components (SX1262, antennas) need separation from digital logic; SIM7080G needs isolation from the 3.3V rail; decoupling caps must be within 1–2mm of their IC's power pin. |
| **Copper routing** | Draw actual copper traces connecting all components as defined in the schematic. High-speed signals (SPI, Ethernet differential pairs) need controlled impedance and length matching. |
| **Ground plane pour** | Fill unused copper area with a GND pour for noise reduction and improved RF performance. |
| **DRC (Design Rule Check)** | Verify no trace clearance violations, missing connections, or manufacturing rule failures. |
| **Generate BOM** | Bill of Materials — exported from KiCad. Lists every component with reference designator, value, part number, and quantity for procurement. |
| **Generate Gerber files** | Manufacturing output files (one per copper layer, silkscreen, solder mask, drill file) sent to PCB fabrication house (e.g. JLCPCB, PCBWay). |

---

## 9. KiCad Familiarisation

Prior to starting the IoT Bridge PCB project, time was spent learning KiCad from scratch through tutorial projects and video resources.

### Learning Resources Used

| Resource | Topic | Link |
|---|---|---|
| [KiCad 9 Hardware Design Tutorial (TI MSPM0) (1/2 Schematic) - Phil's Lab] | KiCad basics — schematic capture | [YouTube link](https://youtu.be/O-zNn5k5Bn4?si=FqlrjHwdi5oZtbnR) |
| [KiCad 9 Hardware Design Tutorial (TI MSPM0) (2/2 PCB) - Phil's Lab] | PCB layout and routing | [YouTube link](https://youtu.be/igQWdVGZGpI?si=u5auZLYhjf0JMwDA) |
<!--| [Add video title here] | [Topic] | [YouTube link] |-->

<!--**Note to Kingsley:** Fill in the specific YouTube videos you watched during your KiCad learning phase above.-->

### Concepts Learned During Familiarisation
- Schematic capture: placing symbols, drawing wires, net labels, power symbols
- Component libraries: adding external libraries (Espressif, SnapEDA downloads)
- ERC (Electrical Rules Checker): reading and resolving errors
- Footprint assignment: linking schematic symbols to PCB pad patterns
- PCB editor basics: component placement, trace routing
- KiCad project file structure: `.kicad_sch`, `.kicad_pcb`, `.kicad_pro`

---

## 10. Deliverables

- [x] Component Selection Document *(see `component-selection.md`)*
- [x] Block Diagram *(complete — Section 2.1)*
- [x] Schematic — substantially complete *(PoE controller wiring and RF matching network values outstanding — see Section 8)*
- [ ] PCB Layout — not started *(requires schematic completion first — see Section 8, Phase 2)*
- [ ] Bill of Materials — not started *(exported from KiCad after layout)*
- [ ] Gerber Files — not started *(generated after layout and DRC pass)*

---

## 11. Project Repository

All design documentation, notes, and learning resources for this project are maintained in the following GitHub repository:

**GitHub:** https://github.com/kingsleydaprime/knowledgebase/tree/main/projects/iot-bridge-pcb

The repository includes:
- `documentation.md` — this design report
- `component-selection.md` — full component research and justification
- `schematic-notes.md` — pin-level wiring decisions and gotchas
- `learning.md` — concepts learned throughout the project

---

## 12. References

- Espressif Systems. *ESP32-C6 Series Datasheet.* espressif.com
- Espressif Systems. *ESP32-C6-WROOM-1 Datasheet.* espressif.com
- Semtech Corporation. *SX1261/2 Datasheet Rev. 1.2.* semtech.com
- SIMCom Wireless Solutions. *SIM7080G Hardware Design.* simcom.com
- WIZnet Co. Ltd. *W5500 Datasheet V1.1.0.* wiznet.io
- Texas Instruments. *PPS23730A0RMTT Datasheet.* ti.com
- Skyworks Solutions. *PE4259 Datasheet.* skyworksinc.com
- Texas Instruments. *LM66100 Datasheet.* ti.com
- Heltec Automation. *WiFi LoRa 32 V3 Schematic.* heltec.org
- STMicroelectronics. *AN4488 — Getting Started with STM32 Hardware Development.* st.com
