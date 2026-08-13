# IoT Bridge PCB — Power & RF

From [`../component-selection.md`](../component-selection.md) §5–7 and
[`../schematic-notes.md`](../schematic-notes.md) §1, 3, 4.

The power tree is where hardware interviews get serious, and it's where this design has the most
defensible decisions.

---

### Q1. [Intermediate] 🔥 The board has three power inputs. How do they coexist without fighting?

**Strong answer covers:** two **TI LM66100 ideal-diode controllers in an ORing configuration**. Each
is effectively a controlled MOSFET that conducts when its input is the higher voltage and blocks
reverse current when it isn't — so whichever source is present (or highest) feeds the rail, and the
others are isolated. Plugging in USB while PoE is live is safe, and removing one source doesn't
interrupt the rail.

**Why not literal diodes:** a Schottky drops ~0.3–0.4 V and burns it as heat at every amp — a real
loss on a 5 V rail. The LM66100's **79 mΩ** on-resistance drops millivolts instead, which at 1 A is
under 0.1 V versus 0.4 V. Low quiescent current matters too, since this thing may idle for months.

**Follow-up:** *"Why two, not three?"* — one per source that needs isolating from the others; the
topology is per-input, and the count follows from how many can be present simultaneously.

---

### Q2. [Intermediate] 🔥 How does Power-over-Ethernet work here?

**Strong answer covers:** the **TI PPS23730A0RMTT** is an 802.3af/at-compatible PD (powered device)
front end with an **integrated DC-DC controller**. The sequence: the PSE (switch) detects a valid PD
by looking for a signature resistance, then classifies it to learn the power class, then applies
48 V; the PD's front end handles that negotiation, provides the required isolation, and the DC-DC
steps 48 V down to the board's 5 V rail.

**Practical notes worth giving:** it's a 47-pin part — the schematic-notes approach was to **place it
early and wire it last**, because it's the most complex symbol on the sheet and everything else is
easier to reason about first. And PoE brings safety-isolation and creepage requirements that most of
the board doesn't have, so it constrains layout, not just schematic.

---

### Q3. [Intermediate] Why USB-C at 5 V with just CC resistors, and no USB-PD controller?

**Strong answer covers:** two **5.1 kΩ pull-downs on CC1 and CC2** are all a device needs to advertise
itself as a sink and get the default 5 V at up to ~900 mA (or more, depending on the source's
advertised current). A PD controller is only needed to *negotiate* higher voltages, and this board
doesn't want any — everything downstream is derived from 5 V.

**The detail that catches people:** you need a resistor on **each** CC line, not one, because the
cable orientation determines which CC is connected. A single resistor gives a port that works one way
round and not the other — a genuinely common first-board bug.

---

### Q4. [Advanced] 🔥🔥 Why does the cellular modem get its own 3.8 V LDO instead of running off the 3.3 V rail?

**This is the best power question in the project.**

**Strong answer covers two independent reasons:**
1. **Voltage.** The SIM7080G's supply range is **3.0–4.2 V**, and it wants headroom above 3.3 V — a
   3.3 V rail sitting at the bottom of its range gives no margin for droop.
2. **The real reason — current transients.** A cellular modem draws large, fast bursts during
   transmit (bursty by the nature of the radio protocol). If it shares a rail with the MCU and the
   sensitive digital/RF parts, each burst pulls the rail down; the MCU browns out, or the LoRa
   receiver's noise floor rises, and the symptom is "the board resets when the modem connects" or
   "range is fine until cellular is enabled." Giving it its own regulator means the spike is
   absorbed locally and the 3.3 V rail never sees it.

**The generalisable principle:** separate the noisy, bursty load from the quiet, sensitive one at the
**regulator**, not just with a bit more capacitance. Rail separation is a design decision; decoupling
is damage control.

**Follow-up to have ready:** *"How do you size the bulk capacitance for the modem?"* — from the
datasheet's peak burst current and duration, plus the allowable droop. That's a real calculation, and
saying so is better than a number you can't defend.

---

### Q5. [Intermediate] Why an LDO for 3.3 V rather than a switching regulator?

**Strong answer covers:** the **TLV1117-33** is simple, quiet, and needs almost no external parts —
no inductor, no switching node, and critically **no switching noise** near three radios. Its cost is
efficiency: an LDO burns (Vin − Vout) × I as heat, so 5 V → 3.3 V at 500 mA dissipates about 0.85 W,
which is a thermal question on a small board (hence SOT-223 with copper pour for heatsinking). The
~1.1 V dropout at full load also sets a floor on the input rail.

**When you'd switch:** if the 3.3 V load grew, or if the input were higher (a raw PoE rail rather
than a pre-regulated 5 V), a buck converter becomes necessary and you pay for it with layout
discipline — keep the switching loop tiny and away from the RF sections.

---

### Q6. [Advanced] 🔥🔥 The SX1262 has separate TX and RX ports and there's one antenna. How is that resolved?

**Strong answer covers:** a **Skyworks PE4259 SPDT RF switch**. The SX1262 transmits from **RFO** and
receives on **RFI_N/RFI_P**; the switch's common port (RFC) goes to the antenna and routes to one
side or the other based on a single logic pin:

| CTRL | Routing |
|---|---|
| HIGH (TX) | RFC → RF1 → SX1262 RFO |
| LOW (RX) | RFC → RF2 → SX1262 RFI_N/RFI_P |

**The detail that makes this a strong answer:** **DIO2 on the SX1262 drives CTRL automatically** —
the radio switches the antenna itself, in hardware, synchronised with its own transmit timing. That
removes the entire class of firmware bug where the switch is in the wrong position during a
transition, which at +22 dBm means transmitting into your own receiver input.

**The specs that matter:** ~0.4 dB insertion loss (a direct, permanent subtraction from your link
budget in both directions) and ~30 dB isolation (how well the idle path is protected from the active
one).

---

### Q7. [Intermediate] 🔥 Why the HR911105A MagJack rather than a plain RJ45?

**Strong answer covers:** it has the **magnetics integrated** — the isolation transformers and
common-mode chokes that Ethernet requires are inside the connector, so there's no separate
transformer to place, route differential pairs to and from, or get wrong. On a first board that
removes a genuinely error-prone section.

**The datasheet detail worth citing:** the **centre tap goes to +3V3 through a 49.9 Ω resistor**, per
the W5500 reference design. Knowing that specific requirement — rather than "connect the magnetics" —
is what shows you read the datasheet rather than copied a picture.

**The trade:** a MagJack costs more than connector-plus-discrete-magnetics at volume, and constrains
your connector choice.

---

### Q8. [Advanced] What's the difference between 802.15.4, Zigbee and Thread, and why can only one run at a time?

**Strong answer covers:** **802.15.4** is the PHY and MAC — the radio layer. **Zigbee** and **Thread**
are different network/application stacks running *on top of* that same radio; Zigbee has its own
mesh and application profiles, Thread is IPv6-based (6LoWPAN) and routable. Because they share one
physical radio, the ESP32-C6 **time-shares** it — the stacks can't both own the radio simultaneously,
so the choice is firmware-selectable per deployment.

**Why this matters to the hardware:** none of it changes the board. It's the strongest argument for
choosing this MCU — one radio, two ecosystems, decided in software after manufacture.

---

### Q9. [Advanced] 🔥 Three radios plus Ethernet on one small board. What are you worried about?

**Strong answer covers, ranked:**
1. **Antenna isolation and coexistence.** Wi-Fi/802.15.4 at 2.4 GHz, LoRa at 868 MHz, cellular
   multi-band — physically separated antennas, and the transmit power of one arriving at another's
   input is the concern. The cellular PA is the loudest thing on the board.
2. **Power transients coupling into RF** — addressed by rail separation (Q4), and the reason it's a
   power decision and not just a capacitor choice.
3. **Ground plane integrity.** RF returns follow the path of least impedance directly under the
   trace; a split or slotted plane under an RF line is a radiating antenna you didn't design.
4. **Switching noise from any DC-DC** landing in a receiver's band — an argument for the LDO on the
   sensitive rail.
5. **Layout of the 50 Ω traces** — controlled impedance, keep-outs under antennas, and the matching
   network placed right at the pin.

**The honest framing to end on:** most of these are **layout** problems, and the schematic is where
you make them solvable — by separating the rails, placing the RF sections apart, and using a module
with pre-tuned matching for the hardest radio.

---

### Q10. [Intermediate] The microSD, button and LED look trivial. Anything to get right?

**Strong answer covers:** the microSD needs pull-ups on its lines and shares the SPI bus (so its own
CS, and card-detect if the socket has it); it can also draw meaningful current during writes, which
belongs in the power budget. The button needs a pull-up/pull-down so it isn't floating, plus
debouncing — hardware RC or firmware. The LED needs a current-limiting resistor sized for the desired
brightness and the GPIO's current limit. And on ESP32 parts, **strapping pins** determine boot mode,
so anything connected to one must not hold it at the wrong level at reset — the classic "board won't
boot with the SD card inserted" bug.

---

### Q11. [Beginner] Why is there an SWD/JTAG header on a board with USB?

**Strong answer covers:** the ESP32-C6 has USB Serial/JTAG built in, which covers flashing and basic
debug — but a dedicated header is what you want when USB itself is the thing that's broken, when the
board is powered from PoE in a deployed enclosure, or when you need to attach a debugger without
enumerating a USB device. It costs a footprint and nothing else, and leaving it off is the sort of
economy you regret exactly once.
