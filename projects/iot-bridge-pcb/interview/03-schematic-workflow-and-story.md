# IoT Bridge PCB — Workflow, KiCad & Project Story

From [`../kicad-walkthrough.md`](../kicad-walkthrough.md),
[`../schematic-notes.md`](../schematic-notes.md) and
[`../documentation.md`](../documentation.md) §6–10.

---

### Q1. [Intermediate] 🔥 Walk me through how you actually built this schematic.

**Strong answer covers the phase order and *why* it's that order:**
1. **Project setup** — sheets, title block, libraries.
2. **Place the ESP32-C6 first** — it's the hub, and every other block's pin assignment is decided by
   what the MCU has available.
3. **Power section next** — because every other block needs a rail to connect to, and the rails
   determine which parts are even viable.
4. **Peripherals** — LoRa, Ethernet, cellular, then the USB/SD/button/LED/SWD section.
5. **Final ERC and cleanup.**

**The specific tactic worth naming:** the PoE controller is a 47-pin part, so it was **placed early
and wired last** — get the footprint and the sheet layout settled while the surrounding context is
simple, then do the tedious wiring when everything it connects to already exists.

**The mental model to state:** the schematic isn't drawn left-to-right; it's built **hub outward,
power first**.

---

### Q2. [Intermediate] 🔥 What is ERC and what does it actually catch?

**Strong answer covers:** Electrical Rules Check validates the *schematic's* connectivity — unconnected
pins, outputs driven against each other, inputs with no driver, and power nets with no source. It is
**not** a design review: it can't tell you a resistor is the wrong value, a supply is out of range,
or that you've connected TX to TX. It catches the mechanical mistakes so your attention is free for
the ones that need judgement.

**The habit:** run it continuously, not once at the end. A clean ERC after every section means each
new error belongs to the thing you just drew.

---

### Q3. [Advanced] 🔥 Explain PWR_FLAG. When does a net need one and when doesn't it?

**Strong answer covers:** ERC insists every power net be *driven* by something. Regulator outputs are
declared as power outputs, so a rail fed by an LDO's VOUT already has a driver. But a net that enters
the board from outside — from a USB cable, or from a source you haven't wired yet — has no pin in the
schematic claiming to drive it, so ERC reports "power input not driven." `PWR_FLAG` is the annotation
that says "this is externally sourced, trust me."

**The project's rule, stated precisely:** only on externally-sourced nets — **`USB_VBUS`** (comes from
the cable) and **`POE_5V`** (because the PPS23730 isn't wired yet). Nets fed by an LDO's VOUT pin do
**not** need one.

**Why this is a good answer:** the wrong instinct is to spray `PWR_FLAG` on every rail until ERC goes
quiet, which suppresses exactly the errors that would have told you a rail has no source. Knowing
when *not* to use it is the point.

---

### Q4. [Intermediate] How do you know your pin assignments are actually legal?

**Strong answer covers:** GPIO on an ESP32 is not uniform — some pins are **strapping pins** that
determine boot mode and must be at a known level at reset; some are input-only; some are consumed by
the module's own flash and must never be used; and USB and JTAG functions occupy specific pins. So
assignment is a constraint-satisfaction exercise against the datasheet's pin-function table, not a
"pick a free pin" exercise. The failure mode is a board that behaves perfectly until a peripheral
holds a strapping pin low at power-on and it silently boots into download mode.

---

### Q5. [Intermediate] 🔥 What's the difference between the schematic and the layout, and what's still ahead of you?

**Strong answer covers:** the schematic captures **connectivity** — what connects to what. The layout
is **physics** — where components sit, how wide and how long the traces are, stack-up, impedance
control, thermal relief, and every EMC consequence. A netlist that's perfect in schematic can produce
a board that doesn't work, and almost every hard problem on a multi-radio board (Q9 in
[02-power-and-rf.md](02-power-and-rf.md)) is a layout problem.

**Be honest about status:** the schematic work — power, MCU, LoRa, Ethernet, cellular, and the
USB/SD/button/LED/SWD section — is what's done, along with component selection and the design-decision
record. Layout, DRC, gerber generation, and a fabricated board are outstanding. Saying that plainly is
much stronger than implying a finished product; interviewers respect a precise status.

---

### Q6. [Advanced] 🔥 Which decision in this project are you least sure about?

**Strong answer covers — pick a real one and reason both ways:**
- **The LDO for 3.3 V.** Simple and quiet, but it burns ~0.85 W at 500 mA. If the real load turns out
  higher, that's a thermal problem on a small board and a buck converter becomes necessary — with
  switching noise arriving next to three radios.
- **A shared 16 MHz SPI bus** across radio, Ethernet and SD. It's clean and pin-efficient, but the SD
  card can hold the bus during internal operations, and that latency lands on a radio that has timing
  expectations. A second SPI peripheral for the SD card is the fix if it bites.
- **Antenna placement and isolation**, which is genuinely unresolved until there's a fabricated board
  to measure. That's the honest answer to "what worries you", and it's not something a schematic can
  settle.

---

### Q7. [Intermediate] 🔥 Why does a hardware project need this much documentation?

**Strong answer covers:** because in hardware, **the cost of being wrong is a respin** — weeks and
real money, not a redeploy. A written decision record (why 868 MHz, why a module, why the cellular
rail is separate, why no external flash) is what stops the same question being re-litigated from
memory three months later, and it's what a reviewer or a manufacturer needs in order to check your
reasoning rather than just your netlist.

**The second reason:** a schematic records *what* you did and never *why*. Six months on, "why is
there a 49.9 Ω resistor on the centre tap?" is answerable from a datasheet reference in your notes and
essentially unanswerable from the schematic alone.

---

### Q8. [Beginner] You'd never used KiCad before. How did you learn it?

**Strong answer covers:** by building the actual board rather than by working through tutorials —
with a written walkthrough capturing the phases, plus a keyboard-shortcut sheet, so the tool stopped
being the bottleneck. The transferable point: for a tool you'll use for one project, learn it against
the real artefact and write down what you had to look up; for a tool you'll use for years, invest in
fluency separately. Naming which situation you were in is the answer.

---

### Q9. [Advanced] What's the riskiest part of this design, and how would you de-risk it before committing to fabrication?

**Strong answer covers, in order:**
1. **RF performance** — LoRa range and multi-radio coexistence can't be verified from a schematic.
   De-risk with dev-kit prototyping: an ESP32-C6 board plus an SX1262 module plus a SIM7080G breakout
   on a bench, proving the firmware and the coexistence story before laying out a single trace.
2. **The PoE front end** — the most complex part, currently unwired, and the section with safety and
   isolation implications. De-risk by prototyping against a reference design and a real 802.3af
   switch.
3. **Power budget under simultaneous worst case** — every radio active at once. That's an arithmetic
   exercise against datasheet peak currents, and it's cheap to do before it's expensive to discover.

**The framing:** buy a dev kit for every risky subsystem and prove the software before you spin a
board. The board is the last step, not the first.

---

### Q10. [Intermediate] 🔥 What did designing hardware teach you that software hadn't?

**Strong answer covers — pick one and go deep:**
- **Irreversibility changes the process.** You can't hotfix a PCB. That's what makes the documented
  decision record, the DNP eSIM footprint, and the "place it now, wire it last" discipline rational
  rather than fussy — the same reasoning as designing around irreversible actions in software, but
  enforced by physics instead of by judgement.
- **The datasheet is the API, and it's non-negotiable.** A 49.9 Ω centre-tap resistor isn't a
  preference; it's a stated requirement, and there's no runtime that will forgive getting it wrong.
- **Constraints propagate physically.** Choosing a cellular modem forced a second regulator, which
  forced a thermal question, which constrained the layout. Software dependencies rarely couple that
  tightly.

---

### Q11. [Beginner] Explain this board to a non-technical interviewer.

**Strong answer covers:** it's a translator box for connected devices. Sensors in a building or a
field speak short-range low-power radio protocols and can't reach the internet on their own; this
board listens to all of the common ones, then forwards the data over whichever internet connection
is available — a network cable, Wi-Fi, or a mobile network if there's nothing else. The engineering
challenge is fitting four radios and three power sources onto one board without them interfering with
each other.
