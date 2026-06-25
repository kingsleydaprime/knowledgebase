# IoT Bridge PCB — Design Report

**Project Title:** Universal IoT Bridge PCB Design  
**Author:** Kingsley Ihemelandu  
**Organisation:** [Company Name]  
**Date:** June 2026  
**Revision:** v0.1 — Schematic Phase  
**Status:** In Progress

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
7. [Deliverables](#7-deliverables)
8. [References](#8-references)

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
| Power over Ethernet | TI TPS23730 (IEEE 802.3bt) |
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
                    │          ESP32-C6-WROOM-1 (Main MCU)            │
                    │                                                  │
                    │   Wi-Fi 6 | BT 5 LE | Zigbee 3.0 | Thread 1.3  │
                    │                                                  │
   SX1262 ◄─ SPI ──►│  SPI Bus                                         │
   W5500  ◄─ SPI ──►│  (shared MOSI/MISO/SCK, individual CS lines)    │
   MicroSD◄─ SPI ──►│                                                  │
                    │  UART ─────────────────────────────► SIM7080G   │
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
             TPS23730 (PoE)                USB-C VBUS (5V)
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
| PoE Controller | TI TPS23730 | 802.3bt compliant (51W); integrated DC-DC controller |
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
| TPS23730 Datasheet | Texas Instruments | PoE application circuit, transformer selection |
| W5500 Datasheet | WIZnet | SPI interface, crystal requirements, RJ45 wiring |
| SIM7080G Hardware Guide | SIMCom | Power supply requirements, antenna connections, AT command interface |
| Heltec WiFi LoRa 32 V3 Schematic | Heltec | Reference for ESP32 + SX1262 integration |
| AN4488 Application Note | STMicroelectronics | General hardware design best practices (used as reference) |

---

## 6. Schematic Progress

| Section | Status | Notes |
|---|---|---|
| ESP32-C6 MCU | In Progress | 3V3 + decoupling caps ✓, EN circuit ✓, BOOT circuit ✓, PWR_FLAG ✓, GPIO net labels in progress |
| Power (USB-C, PoE, LDOs, OR'ing) | Not started | |
| SX1262 LoRa Transceiver | Not started | |
| W5500 Ethernet Controller | Not started | |
| SIM7080G Cellular Module | Not started | |
| MicroSD Slot | Not started | |
| User Interface (Button + LED) | Not started | |
| SWD Debug Header | Not started | |
| ERC (0 errors) | Not started | |

---

## 7. Deliverables

- [ ] Component Selection Document *(see `component-selection.md`)*
- [ ] Block Diagram *(complete — Section 2.1)*
- [ ] Complete Schematic (KiCad `.kicad_sch`)
- [ ] Complete PCB Layout (KiCad `.kicad_pcb`)
- [ ] Bill of Materials (exported from KiCad)
- [ ] Gerber Files (manufacturing-ready)

---

## 8. References

- Espressif Systems. *ESP32-C6 Series Datasheet.* espressif.com
- Espressif Systems. *ESP32-C6-WROOM-1 Datasheet.* espressif.com
- Semtech Corporation. *SX1261/2 Datasheet Rev. 1.2.* semtech.com
- SIMCom Wireless Solutions. *SIM7080G Hardware Design.* simcom.com
- WIZnet Co. Ltd. *W5500 Datasheet V1.1.0.* wiznet.io
- Texas Instruments. *TPS23730 Datasheet.* ti.com
- Texas Instruments. *LM66100 Datasheet.* ti.com
- Heltec Automation. *WiFi LoRa 32 V3 Schematic.* heltec.org
- STMicroelectronics. *AN4488 — Getting Started with STM32 Hardware Development.* st.com
