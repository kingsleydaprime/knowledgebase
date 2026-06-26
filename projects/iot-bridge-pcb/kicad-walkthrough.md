# IoT Bridge — KiCad Step-by-Step Walkthrough

> Follow this file alongside KiCad. One screen KiCad, one screen this file.
> When something confuses you, write it in `learning.md`.
> Reference wiring details: `schematic-notes.md`
> Component choices: `component-selection.md`

---

## Keyboard Shortcuts (Keep These Handy)

| Key | Action |
|---|---|
| `A` | Add component symbol |
| `P` | Add power symbol (+3V3, GND, etc.) |
| `W` | Draw wire |
| `L` | Place net label |
| `R` | Rotate selected item |
| `G` | Grab and drag (moves item + keeps wires attached) |
| `M` | Move item (disconnects wires) |
| `E` | Edit properties |
| `C` | Copy |
| `Q` | Place no-connect marker (X) on unused pins |
| `Del` | Delete |
| `Ctrl+S` | Save — do this constantly |
| `Ctrl+Z` | Undo |
| Mouse wheel | Zoom in/out |
| Middle click drag | Pan |

---

## Phase 1 — Project Setup

### Step 1: Create the Project
1. Open KiCad
2. File → **New Project**
3. Name it `iot-bridge`
4. Save it somewhere outside the knowledgebase (e.g. `~/projects/iot-bridge/`)
5. KiCad creates two files: `iot-bridge.kicad_sch` (schematic) and `iot-bridge.kicad_pcb` (PCB layout)

### Step 2: Open the Schematic Editor
1. In the KiCad project window, click the **Schematic Editor** icon (first icon, top row)

### Step 3: Set Up the Title Block
1. File → **Page Settings**
2. Paper Size: **A3**
3. Fill in Title: `IoT Bridge PCB`, Revision: `v0.1`, Date: today
4. Click OK

---

## Phase 2 — Place the ESP32-C6 (The Brain)

> This is the first real component you place. Everything else in the schematic will connect to or from this chip.

### Step 4: Find and Place the ESP32-C6 Symbol

Press `A` to open the symbol chooser. Search `ESP32-C6`.

> If it doesn't appear, you need to add the Espressif KiCad library:
> - Download it from: github.com/espressif/kicad-libraries
> - In KiCad: Preferences → Manage Symbol Libraries → Add the downloaded library
> - Search again

Place the ESP32-C6 symbol somewhere in the **centre** of your schematic — leave plenty of space around it on all sides. Every peripheral we add later will surround this chip.

The symbol will look like a large box with many pins sticking out on all sides. That's normal — the ESP32-C6 has a lot of pins.

---

### Step 5: Wire the Power Pins

The ESP32-C6-WROOM-1 is a **module** (not a bare chip), so it only exposes **one 3V3 pin and one GND pin**. Espressif handled all the internal decoupling and power routing inside the module itself. This makes your job much simpler.

**Press `P` and place:**
- One `+3V3` power symbol
- One `GND` power symbol

**Connect them:**

| Pin | Connect to | Extra components |
|---|---|---|
| 3V3 (pin 2) | `+3V3` | 10µF cap + 100nF cap, both between 3V3 and GND |
| GND (pin 1) | `GND` | Nothing extra needed |

```
+3V3 ──┬── 3V3 pin (pin 2)
       │
      10µF ── GND     ← bulk capacitor
       │
      100nF ── GND    ← decoupling capacitor
```

**How to place the caps:**
1. Press `A`, search `C` for capacitor
2. Place it between the 3V3 wire and a GND symbol
3. Press `E` to edit — set Value to `10uF` for the first, `100nF` for the second

> **Note:** If you were using the bare ESP32-C6 chip instead of the WROOM module, you'd see multiple VDD pins (VDD3P3, VDD3P3_CPU, VDD3P3_RTC, VDDA) each needing individual caps. The WROOM module abstracts all of that — it's already done inside the module.

---

### Step 6: Wire the Enable and Boot Pins

These two pins control how the ESP32-C6 starts up.

**EN (Enable pin):**
- Connect a **10kΩ resistor** between EN and `+3V3` (pull-up — keeps the chip enabled by default)
- Connect a **100nF cap** between EN and GND (filters noise to prevent false resets)
- Optionally: connect a **reset button** between EN and GND (pressing it resets the chip)

```
+3V3
  │
 10kΩ
  │
  ├──── EN pin
  │
 100nF
  │
 GND
```

**GPIO9 / BOOT pin:**
- Connect a **10kΩ resistor** between GPIO9 and GND (pull-down — tells chip to boot from flash normally)
- Optionally: connect a **button** between GPIO9 and `+3V3` (hold during power-on to enter bootloader mode for flashing)

---

### Step 7: Assign SPI Bus Pins

The ESP32-C6 will talk to three devices over SPI (W5500 Ethernet, SX1262 LoRa, MicroSD). They share the same MOSI, MISO, and SCK wires — but each gets its own CS (Chip Select) pin so the ESP32 can talk to one at a time.

Press `L` to place net labels on these GPIO pins:

| GPIO | Net label to place | Goes to |
|---|---|---|
| GPIO2 | `CS_ETH` | W5500 only |
| GPIO6 | `SPI_MOSI` | W5500, SX1262, SD card |
| GPIO7 | `SPI_MISO` | W5500, SX1262, SD card |
| GPIO8 | `SPI_SCK` | W5500, SX1262, SD card |
| GPIO9 | already used for BOOT — skip | — |
| GPIO10 | `CS_LORA` | SX1262 only |
| GPIO11 | `CS_SD` | MicroSD only |

> **Why GPIO9 is not CS_ETH:** GPIO9 is a strapping pin — the ESP32-C6 reads it at boot to choose between flash boot (LOW) and bootloader mode (HIGH). We've wired it with a 10kΩ pull-down for this purpose. CS pins must default HIGH (chip not selected), which conflicts with a pull-down. GPIO2 has no strapping function and no pull resistor, so it's a clean CS line.

> **What is a net label?** Instead of drawing a wire from the ESP32 all the way across the schematic to a peripheral, you place a label on the ESP32 pin and the same label on the peripheral pin. KiCad treats them as connected. Much cleaner than wires everywhere.

---

### Step 8: Assign UART Pins (for Cellular Module)

| GPIO | Net label | Goes to |
|---|---|---|
| GPIO4 | `UART_TX` | SIM7080G RX pin |
| GPIO5 | `UART_RX` | SIM7080G TX pin |

> Note the cross: ESP32 TX → Cellular RX, ESP32 RX → Cellular TX. This is standard UART — one side's transmit goes into the other side's receive.

---

### Step 9: Assign USB Pins

| GPIO | Net label | Goes to |
|---|---|---|
| GPIO13 | `USB_DP` | USB-C connector D+ |
| GPIO12 | `USB_DM` | USB-C connector D- |

---

### Step 10: Assign Remaining GPIO Pins

| GPIO | Net label | Purpose |
|---|---|---|
| GPIO15 | `LORA_RESET` | SX1262 hardware reset |
| GPIO18 | `LORA_BUSY` | SX1262 busy signal |
| GPIO19 | `LORA_DIO1` | SX1262 interrupt |
| GPIO20 | `ETH_RESET` | W5500 hardware reset |
| GPIO21 | `ETH_INT` | W5500 interrupt |
| GPIO22 | `SIM_PWRKEY` | SIM7080G power on/off |
| GPIO3  | `BTN` | User button |
| GPIO0  | `LED` | Status LED |

> **GPIO14 does not exist on the WROOM-1** — the module uses it internally for SPI flash. The symbol skips from GPIO13 to GPIO15.

---

### Step 11: Mark Unused Pins

Any GPIO you're not using right now gets a **no-connect marker** so KiCad's ERC doesn't flag them as errors.

Press `Q` and click each unused pin to place an X on it.

---

### Step 12: Run ERC on the ESP32-C6 Section

Before moving on:
1. Inspect → **Electrical Rules Checker** → Run ERC
2. Fix any errors before continuing

**Common errors here:**

| Error | What it means | Fix |
|---|---|---|
| `Pin unconnected` | A pin has nothing on it | Connect it, or press `Q` to mark no-connect |
| `Power pin not driven` | KiCad doesn't know what's supplying +3V3 yet | Add a `PWR_FLAG` — press `P`, search `PWR_FLAG`, place on the +3V3 net |
| `Wire not connected` | A wire is floating, not touching a pin | Zoom in and check — look for a wire end that missed the pin |

---

## Phase 3 — Power Section

> Now that the ESP32-C6 is placed and its power needs are visible, draw the circuit that actually supplies those voltages.

### Step 13: Place the USB-C Connector

Press `A`, search `USB_C_Receptacle`.

**Wire each pin:**

| USB-C Pin | Connect to | Notes |
|---|---|---|
| VBUS | One end of a polyfuse | 500mA polyfuse, other end to net `USB_VBUS` |
| D+ | Net label `USB_DP` | Connects to ESP32 GPIO12 you labelled earlier |
| D- | Net label `USB_DM` | Connects to ESP32 GPIO13 |
| CC1 | 5.1kΩ resistor → GND | Tells USB host "give me 5V/900mA" |
| CC2 | 5.1kΩ resistor → GND | Both CC pins need this |
| GND / Shield | GND | |

---

### Step 14: Place LM66100 #1 and #2 (Power OR'ing)

These two chips combine the USB-C and PoE 5V sources safely. Place both.

The KiCad symbol is **LM66100DCK**. Its actual pin names are:

**LM66100 #1 — USB-C path:**
| Pin | Name | Connect to | Notes |
|---|---|---|---|
| 1 | VIN | `USB_VBUS` | |
| 6 | VOUT | `+5V` power symbol | |
| 2 | GND | GND | |
| 3 | CE | GND | Active-low — pull LOW to always enable |
| 5 | ST | no-connect (`Q`) | Status output, unused |

**LM66100 #2 — PoE path:**
| Pin | Name | Connect to | Notes |
|---|---|---|---|
| 1 | VIN | `POE_5V` | comes from PoE controller |
| 6 | VOUT | `+5V` | same net — this is the OR'ing |
| 2 | GND | GND | |
| 3 | CE | GND | Active-low — must be LOW to enable |
| 5 | ST | no-connect (`Q`) | |

Add 100nF decoupling cap on VIN to GND and VOUT to GND on both chips.

---

### Step 15: Place the PoE Controller (PPS23730A0RMTT)

> The KiCad symbol found is **PPS23730A0RMTT** — a TI PoE PD controller with integrated DC-DC, same family as the TPS23730. It has 47 pins. **Do not wire this now.** Place it, leave all pins unconnected, and come back after everything else is done.

To place: Press `A`, search `PPS23730`, place it with lots of space around it.

When you return to it:
- Open the PPS23730 datasheet application circuit and copy it exactly
- PoE input pairs come from the RJ45 magjack
- DC-DC output → net label `POE_5V`
- Refer to datasheet for all external components (transformer, MOSFETs, resistors)

---

### Step 16: Place the Voltage Regulators

**TLV1117-33 (3.3V LDO):**
| Pin | Connect to |
|---|---|
| VI | `+5V` |
| VO | `+3V3` power symbol |
| GND | GND |

Caps: 10µF + 100nF on input, 10µF + 100nF on output.

**AP2112K-3.8 (3.8V for cellular):**

> KiCad only has **AP2112K-3.3** in its library. Place that symbol, then press `E` and change the Value field to `AP2112K-3.8`. The pinout is identical — the difference is only the output voltage, which is set internally by the chip you order.

| Pin | Connect to |
|---|---|
| VIN | `+5V` |
| VOUT | Net label `+3V8` |
| GND | GND |
| EN | `+5V` (tie high to always enable) |

Caps: 1µF ceramic on VIN to GND, 1µF ceramic on VOUT to GND.

---

## Phase 4 — Peripherals

> Draw these sections one at a time. Each one follows the same pattern: place the IC → connect power pins with decoupling caps → connect signal pins using the net labels you placed on the ESP32 earlier.

---

### 4A — SX1262 (LoRa Transceiver)

Press `A`, search `SX1262IMLTRT`, place it with space around it.

**Power pins — using actual pin names from the symbol:**

| Pin | Name | Connect to | Notes |
|---|---|---|---|
| 10 | VBAT | `+3V3` | 100nF + 10µF to GND |
| 11 | VBAT_IO | `+3V3` | 100nF to GND |
| 1 | VDD_IN | `+3V3` | 100nF to GND |
| 24 | VR_PA | `+3V3` | 100nF to GND |
| 7 | VREG | 100nF cap to GND only | Internal regulator output — do NOT drive it, just decouple |
| 9 | DCC_SW | 15µH inductor → `+3V3` | DC-DC switch node — value from datasheet reference design |
| 2 | GND | GND | — |

**Crystal (pins 3 and 4):**

The SX1262 needs a **32 MHz crystal** for its clock reference. A crystal is a quartz component that vibrates at a precise frequency to give the chip an accurate timing source — essential for radio communication. See `learning.md` for a full explanation.

| Pin | Connect to |
|---|---|
| XTA (3) | One end of 32 MHz crystal + 10pF cap to GND |
| XTB (4) | Other end of 32 MHz crystal + 10pF cap to GND |

Press `A`, search `Crystal_GND24` — this is the 4-pin version with case ground pins. Place it between XTA and XTB. Connect the two case pins (pins 2 and 4 on the symbol) to GND. Add a 10pF cap from each signal pin to GND.

**SPI and control pins:**

| Pin | Name | Net label | Notes |
|---|---|---|---|
| 19 | NSS | `CS_LORA` | Chip select — active low |
| 18 | SCK | `SPI_SCK` | Shared SPI clock |
| 17 | MOSI | `SPI_MOSI` | Data to SX1262 |
| 16 | MISO | `SPI_MISO` | Data from SX1262 |
| 15 | RESET | `LORA_RESET` | Active low reset from ESP32 |
| 14 | BUSY | `LORA_BUSY` | ESP32 waits for this to go LOW before sending commands |
| 13 | DIO1 | `LORA_DIO1` | Interrupt — fires when TX/RX is done |
| 12 | DIO2 | 100Ω resistor → PE4259 CTRL pin | Controls RF switch — HIGH=TX, LOW=RX |
| 6 | DIO3 | no-connect (`Q`) | — |

**RF section — PE4259 RF Switch + matching network:**

The SX1262 has separate TX (RFO) and RX (RFI_N/RFI_P) ports but only one antenna. The **PE4259 RF switch** routes the antenna to TX when transmitting and RX when receiving. DIO2 controls which path is active.

> Download the PE4259 symbol from SnapEDA before starting this section.

**Step 1 — Place the PE4259 RF switch**

| PE4259 pin | Connect to | Notes |
|---|---|---|
| CTRL (pin 4) | DIO2 (pin 12 on SX1262) via 100Ω resistor | Insert resistor in series on the wire |
| CTRL/VDD (pin 6) | `+3V3` power symbol | Logic supply — no decoupling cap needed here |
| RFC (pin 5) | Antenna matching network → U.FL connector | Common antenna port |
| RF1 (pin 1) | RFO matching network output | TX path |
| RF2 (pin 3) | RFI_N/RFI_P matching network output | RX path |
| GND (pin 2) | GND | |

**Step 2 — Copy the matching networks from the datasheet**

Open SX1262 datasheet section **14.6.2** and copy the RF circuit exactly:
- RFO (23) → inductor/capacitor network → PE4259 RF1
- RFI_N (22) + RFI_P (21) → their own network → PE4259 RF2
- PE4259 RFC → output matching (C8, L5, C9, C10 in datasheet) → U.FL connector

**Step 3 — Place the U.FL connector**

Press `A`, search `Connector_Coaxial` — this is the U.FL coax socket that the antenna cable plugs into.

| Conn_Coaxial pin | Connect to |
|---|---|
| Pin 1 (centre/signal) | ANT_NET (from PE4259 RFC matching network) |
| Pin 2 (shield/outer) | GND |

> Do not guess component values. Every inductor and capacitor value in the RF matching network comes from the datasheet. Getting these wrong means the radio won't work at 868 MHz.

> Reference: Heltec WiFi LoRa 32 V3 schematic is a working SX1262 + PE4259 reference design.

---

### 4B — W5500 (Ethernet Controller)

Press `A`, search `W5500`, place it.

**Power pins (W5500 has multiple VDD pins — each needs its own 100nF cap):**

| Pin | Connect to | Decoupling |
|---|---|---|
| VDD_IO | `+3V3` | 100nF to GND |
| VDD_CORE | `+3V3` | 100nF to GND |
| AVDD | `+3V3` | 100nF to GND |
| GND (all) | GND | Add 10µF bulk cap once on the main +3V3 wire |

**SPI and control pins:**

| Pin | Net label |
|---|---|
| SCSn | `CS_ETH` |
| SCLK | `SPI_SCK` |
| MOSI | `SPI_MOSI` |
| MISO | `SPI_MISO` |
| RSTn | `ETH_RESET` |
| INTn | `ETH_INT` |

**Other pins:**

| Pin | Connect to | Notes |
|---|---|---|
| RSVD | GND | Datasheet says tie to GND |
| EXRES1 | 12.4kΩ resistor → GND | Sets internal reference current — value must be 12.4kΩ |
| PMODE0, PMODE1, PMODE2 | All tie to `+3V3` | Sets 100Base-T full duplex auto-negotiation |

**25 MHz Crystal:**

| Pin | Connect to |
|---|---|
| XTLIN | One end of crystal + 20pF cap to GND |
| XTLOUT | Other end of crystal + 20pF cap to GND |

Press `A`, search `Crystal_GND24` — place between XI/CLKIN and XO, connect the two case pins to GND, add 20pF load caps on each signal pin to GND.

**Ethernet magnetics (RJ45):**

The W5500 does not connect directly to the RJ45 — it goes through a magnetic transformer (built into most magjack connectors):

```
W5500 TPOUT+ / TPOUT-  →  Magnetics TX pair  →  RJ45 TX+/TX-
W5500 TPIN+  / TPIN-   →  Magnetics RX pair  →  RJ45 RX+/RX-
```

Press `A`, search `RJ45_Hanrun_HR911105A` — this is a **MagJack** (RJ45 with integrated magnetics). No separate transformer needed.

| Connection | Detail |
|---|---|
| W5500 TXOP / TXON | MagJack TX+ / TX- |
| W5500 RXIP / RXIN | MagJack RX+ / RX- |
| MagJack CT (centre tap) pins | `+3V3` through a **49.9Ω resistor** — copy exact value from W5500 datasheet |
| MagJack GND / shield | GND |
| LED pins | no-connect (`Q`) for prototype |

> Open the W5500 datasheet application circuit and copy the RJ45 connections exactly — especially the centre tap resistor values. Do not guess.

---

### 4C — SIM7080G (Cellular Module)

Press `A`, search `SIM7080G` (from the SnapEDA library you downloaded), place it.

**Power pins:**

| Pin | Connect to | Decoupling |
|---|---|---|
| VBAT (all VBAT pins) | `+3V8` | 100µF electrolytic + 100nF ceramic to GND |
| GND (all) | GND | — |

> The SIM7080G has multiple VBAT pins — connect all of them. Cellular modules draw sudden current spikes during transmission; the 100µF bulk cap handles that.

**UART (communication with ESP32):**

| SIM7080G pin | Net label | Notes |
|---|---|---|
| TXD | `UART_RX` | Module transmits → ESP32 receives |
| RXD | `UART_TX` | Module receives ← ESP32 transmits |
| PWRKEY | `SIM_PWRKEY` | Pulse LOW for 500ms to power on the module |

**SIM7080G SPI pins — mark as no-connect:**

The SnapEDA symbol for SIM7080G includes SPI pins (SPI_CLK, SPI_CS, SPI_MISO, SPI_MOSI). We are using UART, not SPI, for this module. Press `Q` and mark all four SPI pins with no-connect markers.

**SIM card holder:**

Press `A`, search `SIM_Card` — place a SIM card holder symbol. The actual KiCad symbol (SIM_Card) has these pin names:

| Pin | Name | Connect to | Notes |
|---|---|---|---|
| 1 | VCC | Net label `SIM_VCC` | Connects to SIM7080G SIM_VCC pin |
| 2 | RST | Net label `SIM_RST` | Connects to SIM7080G SIM_RST pin |
| 3 | CLK | Net label `SIM_CLK` | Connects to SIM7080G SIM_CLK pin |
| 5 | GND | GND | |
| 6 | VPP | no-connect (`Q`) | Old programming pin — not used by modern LTE SIMs |
| 7 | I/O | Net label `SIM_DATA` | Connects to SIM7080G SIM_DATA pin |

> Pin 4 is absent from the symbol — it is RFU (reserved) per the ISO 7816 SIM standard.

Add a 100nF cap from `SIM_VCC` net to GND (filtering for the SIM card supply).

**Antennas:**

| Pin | Connect to |
|---|---|
| ANT_LTE (or ANT_MAIN) | U.FL connector — label `CELL_ANT` |
| ANT_GNSS | U.FL connector — label `GNSS_ANT` |

Place two `Connector_Coaxial` (U.FL) symbols for the two antennas.

---

### 4D — MicroSD Card Slot

Press `A`, search `Micro_SD_Card` — place the MicroSD slot symbol.

The symbol uses SD native mode pin names, but we are using SPI mode. Here is the mapping:

| Pin | Name | Connect to | Notes |
|---|---|---|---|
| 1 | DAT2 | no-connect (`Q`) | Not used in SPI mode |
| 2 | DAT3/CD | Net label `CS_SD` | This is the chip select in SPI mode |
| 3 | CMD | Net label `SPI_MOSI` | CMD = MOSI in SPI mode |
| 4 | VDD | `+3V3` power symbol | 100nF + 10µF cap to GND |
| 5 | CLK | Net label `SPI_SCK` | Clock |
| 6 | VSS | GND | |
| 7 | DAT0 | Net label `SPI_MISO` | DAT0 = MISO in SPI mode |
| 8 | DAT1 | no-connect (`Q`) | Not used in SPI mode |
| SHIELD | GND | GND | Metal shield of the connector |

Add **10kΩ pull-up resistors** from `+3V3` to each of the four active signal lines (CS_SD, SPI_MOSI, SPI_MISO, SPI_SCK). These keep the lines stable when no card is inserted.

---

### 4E — User Button

Press `A`, search `SW_Push` — place a tactile button symbol.

```
+3V3
  │
 10kΩ
  │
  ├──── net label BTN (goes to ESP32 GPIO3)
  │
[SW_Push]
  │
 GND
```

Also add a **100nF cap** from BTN to GND — this filters mechanical bounce from the button press.

---

### 4F — Status LED

Press `A`, search `LED` — place an LED symbol.

```
net label LED (GPIO0) → [330Ω resistor] → [LED anode]
                                              [LED cathode] → GND
```

- Press `A`, search `R` — place the 330Ω resistor between the `LED` net label and the LED anode
- Connect the LED cathode to a GND symbol
- Press `E` on resistor → set Value to `330`
- Press `E` on LED → set Value to `LED_GREEN` (or whatever colour you want)

> The 330Ω resistor limits current through the LED to a safe ~10mA at 3.3V. Without it the LED would burn out instantly.

---

### 4G — Debug Header (UART)

> The ESP32-C6 uses its USB pins (GPIO12/13) for both programming and JTAG debugging — so no external JTAG header is needed. Instead, place a simple 4-pin UART header for serial monitoring.

Press `A`, search `Conn_01x04` — place a 4-pin connector.

| Header pin | Connect to |
|---|---|
| Pin 1 | `+3V3` |
| Pin 2 | `UART_TX` |
| Pin 3 | `UART_RX` |
| Pin 4 | GND |

This lets you plug in a USB-to-Serial adapter (like CP2102 or CH340) for serial monitor output without needing USB.

---

## Phase 5 — Final ERC and Cleanup

Run when ALL sections are drawn:

1. Inspect → **Electrical Rules Checker** → Run ERC → fix all errors
2. Tools → **Annotate Schematic** → auto-assigns reference designators (R1, C1, U1...)
3. Check every passive has a value set (press `E` on each one)
4. Save → `Ctrl+S`

---

## The Mental Model for This Schematic

```
         [ESP32-C6]  ← start here, everything connects to this
              │
    ┌─────────┼─────────┬──────────┬──────────┐
    │         │         │          │          │
[SX1262]  [W5500]  [SIM7080G] [MicroSD]  [Button/LED]
(LoRa)  (Ethernet) (Cellular)  (Storage)   (UI)
    │
[Power Section]  ← supplies +3V3 and +5V to everything above
    │
[USB-C] + [PoE]  ← two ways in, OR'd together
```

You placed the ESP32-C6 first. Now everything else in the schematic is either:
- **Something the ESP32 talks to** (peripherals — LoRa, Ethernet, Cellular, SD)
- **Something that powers the ESP32** (power section — USB-C, PoE, LDOs)
