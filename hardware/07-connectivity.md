# Connectivity

**[Intermediate]** — Getting a device onto a network for real: Ethernet vs WiFi vs cellular, and Power over Ethernet.

## Three Ways to Get a Device Online

**Ethernet**
A physical RJ45 cable plugs directly into the device. Data travels as electrical signals over copper wire — 8 wires inside arranged in 4 twisted pairs. Most reliable, fastest, lowest latency, zero interference. The device can't move (tethered by the cable) but the connection is rock solid. Used everywhere that reliability matters: servers, network switches, desktop PCs, industrial equipment.

**WiFi**
Same end goal as Ethernet but over radio waves. Device talks to a nearby router wirelessly. Convenient — no cables, device can move around. But subject to interference (walls, microwave ovens, neighbouring networks), distance limits, and many devices competing for the same radio channel. Everything WiFi can do, Ethernet does better. WiFi's only real advantage is the absence of a physical cable.

**Cellular**
Uses the mobile phone tower network (2G/3G/4G LTE/5G). Needs a SIM card and a monthly data subscription. Works anywhere there's cell coverage — remote fields, moving vehicles, rooftops with no local network. No local infrastructure needed at all. Slower and more expensive per MB than Ethernet or WiFi. The right choice when: the device is mobile, deployed in a remote location, or needs a failover if the primary connection goes down.

**Choosing between them:**

| | Ethernet | WiFi | Cellular |
|---|---|---|---|
| Infrastructure needed | Cable to the device | WiFi router nearby | Cell tower (already exists) |
| Device can move? | No | Within router range | Yes, anywhere |
| Reliability | Highest | Medium | Medium |
| Speed | Highest | High | Lower |
| Cost | Cable installation | Router hardware | Monthly SIM subscription |
| Best for | Fixed, reliability-critical | Convenience, indoor | Remote, mobile, failover |

## PoE — Power over Ethernet

PoE is not a separate connectivity type — it's an extension of regular Ethernet. The idea: send both **data AND electrical power** through the single Ethernet cable that's already there. One cable does two jobs.

A standard Ethernet cable has 8 wires in 4 twisted pairs. For 100 Mbps Ethernet, only 2 pairs carry data. PoE puts **48V DC** on the other 2 pairs:

```
Ethernet cable (same RJ45 plug, same cable):

  Pair 1 ──► TX data
  Pair 2 ──► RX data
  Pair 3 ──► +48V power
  Pair 4 ──► power return (GND)
```

**Why 48V?** Higher voltage = lower current for the same power (P = V × I). Lower current means less heat lost in the cable and less voltage drop over long runs. The device then steps 48V down to whatever it needs (3.3V, 5V, 12V).

**The two sides of every PoE system:**

- **PSE (Power Sourcing Equipment)** — puts power onto the cable. Usually a PoE-capable network switch or a standalone PoE injector that sits between your router and the cable.
- **PD (Powered Device)** — receives power from the cable and steps it down. The IoT Bridge is a PD. The TPS23730 on the board is the PD controller IC.

**The handshake:** PoE doesn't just blast power down every cable. When a device plugs in, the PSE first detects whether it supports PoE (via a resistance test). Only after a successful handshake does it switch the power on — so plugging a non-PoE device into a PoE switch is completely safe.

**PoE power standards:**

| Standard | Max power | Typical use |
|---|---|---|
| 802.3af (PoE) | 15.4W | IP phones, basic cameras |
| 802.3at (PoE+) | 30W | PTZ cameras, access points |
| 802.3bt (PoE++) | 60–100W | Laptops, LED systems, complex IoT hubs |

**Real world uses:** IP cameras mounted on ceilings (one cable, no power outlet needed), VoIP desk phones, WiFi access points, IoT sensors in warehouses. Anywhere running two cables (data + power) to a device would be awkward.

**Why the IoT Bridge uses PoE:** The bridge is likely installed in a ceiling, wall, or equipment cabinet. With PoE, an installer runs a single Ethernet cable and the bridge gets both internet and power. No separate power adapter, no separate power cable, no nearby wall socket needed.

---

## Related
- [[hardware/06-radio-frequency|Radio Frequency]] — the wireless options in depth
- [[hardware/08-iot-architecture|IoT Architecture]] — the system these devices join
- [[foundations/networking/README|Networking]] — everything above the physical layer
- [[devops/08-networking-and-web/README|DevOps networking]] — the server side of the same link
