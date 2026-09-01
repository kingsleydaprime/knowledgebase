# IP Addressing & Subnetting

**[Beginner→Intermediate]** — how a machine anywhere on Earth gets a name a router can act on. Subnetting is the one piece of arithmetic in this course you should be able to do on a whiteboard cold, because it comes up in every cloud VPC design and every firewall rule you will ever write.

## The kid version first

MAC addresses are like **fingerprints** — unique, but useless for finding someone. If I hand you a fingerprint and say "deliver this letter," you'd have to check every person on Earth.

IP addresses are like **postal addresses** — deliberately hierarchical. `Nigeria → Lagos → Yaba → 12 Herbert Macaulay`. A postal worker in Ghana doesn't need to know your street; they only need to know "anything for Nigeria goes on that plane." Each step narrows it down, and **each router only has to know the next narrowing**.

That's the whole trick. Hierarchy means a router can hold a rule for *millions of addresses in one line*. Without it, the internet's routing tables would need billions of entries instead of ~1 million, and the internet would not exist.

## The anatomy of an IPv4 address

32 bits, written as four bytes: `192.168.1.42`. Every address is split into two parts:

```
192.168.1.42 / 24
└──────┬───┘ └┬┘
   network    host      /24 = "the first 24 bits are the network"

192 . 168 . 1 . 42
11000000.10101000.00000001.00101010
└─────────network──────────┘└─host─┘
```

The `/24` is the **prefix length** (CIDR notation), equivalent to the **subnet mask** `255.255.255.0`. It answers exactly one question, and it's the question every host asks about every packet it sends:

> **Is this destination on my own network, or do I hand it to the gateway?**

The host ANDs its own address with the mask, ANDs the destination with the mask, and compares. Same → put it on the wire directly (ARP for it). Different → send it to the **default gateway** and let a router deal with it.

## Subnetting arithmetic you should know cold

The prefix length determines size. Two facts generate everything:

- **Host bits** = `32 − prefix`. **Addresses** = `2^host bits`. **Usable hosts** = that minus 2 (the all-zeros *network address* and the all-ones *broadcast address* are reserved).

| CIDR | Mask | Addresses | Usable | Typical use |
|---|---|---|---|---|
| `/8` | 255.0.0.0 | 16,777,216 | 16.7M | a whole legacy Class A |
| `/16` | 255.255.0.0 | 65,536 | 65,534 | a cloud VPC |
| `/24` | 255.255.255.0 | 256 | 254 | one subnet / office LAN |
| `/28` | 255.255.255.240 | 16 | 14 | a small server pool |
| `/30` | 255.255.255.252 | 4 | 2 | a point-to-point router link |
| `/32` | 255.255.255.255 | 1 | 1 | one exact host (firewall rules) |

**The two mental shortcuts:**

1. **Smaller prefix = bigger network.** `/16` is bigger than `/24`. It feels backwards until you see it as "fewer bits pinned down, more freedom in the rest."
2. **The block size in the last octet is `256 − mask octet`.** For `/28`, the mask is `.240`, so blocks are 16 wide: `.0–.15`, `.16–.31`, `.32–.47`… So `192.168.1.37/28` sits in the `.32–.47` block: network `.32`, broadcast `.47`, usable `.33–.46`. That's the whole calculation, and you can do it in your head.

Worked example — split `10.0.0.0/22` into `/24`s: `/22` is 4× `/24`, so you get `10.0.0.0/24`, `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`. This is exactly what you do when carving a VPC into public/private/database subnets across availability zones.

**CIDR replaced "classes."** You'll still see Class A/B/C in older material — a rigid scheme where the first bits fixed the split at /8, /16, or /24. It wasted enormous space (an organisation needing 300 addresses had to take a /16 of 65k). CIDR (1993) made the boundary arbitrary and bought IPv4 an extra two decades. Classes are dead; the vocabulary lingers.

## Special ranges worth memorising

| Range | Meaning |
|---|---|
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | **Private** (RFC 1918) — not routable on the internet; what every home LAN and cloud VPC uses |
| `127.0.0.0/8` | **Loopback** — never leaves the host |
| `169.254.0.0/16` | **Link-local** — self-assigned when DHCP fails. Seeing a `169.254.x.x` address means *"DHCP didn't answer"* — an instant diagnosis |
| `169.254.169.254` | the **cloud metadata service** on AWS/GCP/Azure. Memorise this one: it's the endpoint behind most [[cybersecurity/04-web-security/README\|SSRF]] escalations, because it hands out instance credentials to anything that asks |
| `224.0.0.0/4` | **Multicast** — one-to-many |

## NAT — the reason IPv4 survived

There are 4.3 billion IPv4 addresses and far more devices. **NAT** (Network Address Translation) is why that hasn't ended the world: your router rewrites the source address of outgoing packets to its own single public IP, records the mapping in a table, and reverses it on the way back.

```
laptop  192.168.1.42:51000  ──►  router rewrites to  203.0.113.7:62000  ──►  server
                            ◄──  reverses using its table              ◄──
```

Because many hosts share one public IP, the port number is doing the disambiguation — hence the precise name **NAPT** / "port-address translation."

The consequences are enormous and mostly bad:

- **Inbound connections don't work.** There's no table entry until the inside host sends first. This breaks peer-to-peer, and is why VoIP/games/WebRTC need [[foundations/networking/14-nat-firewalls-and-middleboxes|STUN/TURN/ICE]].
- **It breaks the end-to-end principle** from [[foundations/networking/01-what-a-network-is|note 01]]. A middlebox now rewrites headers, so the network is no longer transparent — with knock-on effects on protocol evolution.
- **It is not a firewall,** though it accidentally behaves like one. Don't rely on it as a security control.
- **Connections die silently** when the NAT table entry times out (often 5 minutes of idle for TCP). This is the actual cause of "my long-lived WebSocket / database connection drops after a few minutes idle" — and why TCP keepalives and application-level pings exist.

## IPv6, in the space it deserves

128 bits — `2001:0db8:85a3::8a2e:0370:7334`. That's 3.4×10³⁸ addresses, enough to never think about scarcity again. Rules for reading them: leading zeros in a group may be dropped, and **one** run of all-zero groups collapses to `::`.

What actually changes in practice:

- **No NAT.** Every device gets a globally routable address. End-to-end connectivity comes back. (Firewalls now do the filtering that NAT accidentally did.)
- **`/64` is the standard subnet**, always. Not because you need 18 quintillion hosts on a LAN, but because SLAAC (address autoconfiguration) requires it. A site typically gets a `/48` or `/56` and carves `/64`s from it. Subnetting stops being arithmetic and starts being bookkeeping.
- **No broadcast** — multicast and NDP replace ARP.
- **Routers don't fragment**, so [[foundations/networking/02-the-link-layer|Path MTU Discovery]] is mandatory, which makes blocking ICMPv6 genuinely fatal rather than merely harmful.
- **Dual-stack and Happy Eyeballs** — hosts usually run both, and try IPv6 and IPv4 connections in parallel, taking whichever answers first, so a broken IPv6 path doesn't hang the user.

## Key insight

An IP address is not a name for a *machine* — it's a name for a **location in the routing hierarchy**, which is why it changes when the machine moves and why a laptop has a different address on Wi-Fi than on Ethernet. Identity (who you are) and location (where you are) are conflated in IP, and almost every hard problem in mobility, multi-homing, and NAT traversal traces back to that one conflation.

## Related
- [[foundations/networking/04-routing|Routing]] — what routers do with these prefixes
- [[foundations/networking/14-nat-firewalls-and-middleboxes|NAT, Firewalls & Middleboxes]] — NAT traversal in full
- [[devops/03-cloud/README|Cloud]] — VPC/subnet design is this arithmetic applied
- [[foundations/networking/16-debugging-networks|Debugging Networks]] — `ip addr`, `ip route`, reading a routing table
