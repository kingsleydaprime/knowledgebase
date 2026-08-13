# The Link Layer — Getting to the Next Machine

**[Beginner]** — the layer under IP. Its entire job: move a frame **one hop**, across one physical medium, to a directly-attached neighbour. It has no concept of "the internet."

## The kid version first

Imagine a big office building. To send a memo to someone in another building, you write their full postal address on it — but you don't carry it there yourself. You hand it to the mailroom **on your floor**. The mailroom only knows about desks on this floor and the loading dock downstairs.

- The **postal address** is the IP address — it identifies the final destination anywhere in the world, and it doesn't change as the memo travels.
- The **"hand it to the desk by the door"** step is the link layer — it only knows the people it can physically reach, and it's re-done at every single hop.

So a packet has **two destination addresses at once**, and this trips up nearly everyone learning networking: the IP address of where it's ultimately going (constant end-to-end) and the MAC address of the next machine on this wire (rewritten at every hop).

## Frames, and why MTU matters

The link layer's unit is a **frame**: a header, a payload (which is the entire IP packet), and a trailer holding a checksum. An Ethernet frame carries at most **1500 bytes** of payload by default — that limit is the **MTU** (Maximum Transmission Unit).

MTU sounds like trivia. It is one of the top causes of "the connection hangs on large responses but small requests work fine":

- If an IP packet is bigger than the next link's MTU, something must **fragment** it or drop it. IPv4 routers could fragment; IPv6 routers refuse to, and send back an ICMP "Packet Too Big."
- Hosts discover the smallest MTU on the path (**Path MTU Discovery**) by setting the *don't fragment* bit and listening for those ICMP messages.
- **If a firewall blocks ICMP** — a depressingly common "hardening" decision — those messages never arrive. The sender keeps sending packets that are too big, and they keep getting silently dropped. Small packets (the handshake, a `GET`) fit and work fine; the first big response vanishes. The connection just... stalls. This is the **PMTU black hole**, and it's why "block all ICMP" is bad advice.

Tunnels (VPN, VXLAN, [[devops/05-orchestration/README|Kubernetes overlay networks]]) add their own headers, shrinking the usable MTU below 1500 — which is why MTU bugs show up so often in container networking specifically.

**Jumbo frames** (MTU ~9000) exist in data centres to cut per-packet overhead, but only work if *every* device on the path agrees.

## MAC addresses

A **MAC address** is 48 bits, burned into the network interface at manufacture (`a4:83:e7:2b:11:9f`). The first half identifies the vendor. Properties worth internalising:

- **Flat, not hierarchical.** Unlike IP, you cannot look at a MAC and infer where it is. There is no routing on MAC addresses across the internet — it wouldn't scale, because every switch would need an entry for every device on Earth. Hierarchy is exactly what makes [[foundations/networking/03-ip-addressing-and-subnetting|IP addressing]] scalable.
- **Locally meaningful only.** A MAC address is only useful within one broadcast domain.
- **Randomised now, for privacy.** Modern phones/laptops rotate their Wi-Fi MAC per network, because a stable MAC is a perfect tracking identifier for anyone listening.

## ARP — the join between layers 3 and 2

Your host has an IP packet for `192.168.1.1` and needs the MAC to put in the frame. It doesn't know it. So it **shouts**:

```
ARP request  (broadcast to ff:ff:ff:ff:ff:ff): "Who has 192.168.1.1? Tell 192.168.1.42"
ARP reply    (unicast back):                   "192.168.1.1 is at a4:83:e7:2b:11:9f"
```

The answer goes in the **ARP cache** (`ip neigh` on Linux) for a few minutes.

ARP has no authentication whatsoever. Anyone on the segment can answer *any* request, or send unsolicited replies. That's **ARP spoofing** — the classic LAN man-in-the-middle, and the reason [[cybersecurity/03-network-security/02-network-segmentation|network segmentation]] and [[cybersecurity/03-network-security/03-vpns-and-encryption-in-transit|encryption in transit]] are not optional even "inside the perimeter." Your traffic being encrypted is what makes ARP spoofing an annoyance rather than a catastrophe.

IPv6 replaces ARP with **NDP** (Neighbor Discovery), which uses multicast rather than broadcast and can be secured — though usually isn't.

## Hubs, switches, and broadcast domains

Three generations of "the box in the middle," and the difference explains most LAN behaviour:

- A **hub** (extinct) repeats every bit to every port. Everyone hears everything; two simultaneous senders collide. This is one **collision domain**.
- A **switch** learns which MAC lives behind which port (by watching source addresses on incoming frames) and forwards a frame only to the right port. Each port is its own collision domain, so there are effectively no collisions on modern full-duplex switched Ethernet. **CSMA/CD** — the classic collision-detection algorithm in every textbook — is essentially dead history on wired networks. It still matters conceptually on Wi-Fi, which uses CSMA/**CA** (collision *avoidance*), because radios can't listen while transmitting.
- A **router** connects different networks and operates on IP. It is where one **broadcast domain** ends.

**Broadcast domain** is the concept that matters: the set of machines that receive each other's broadcasts (like ARP). A switch forwards broadcasts everywhere; a router does not. Too many machines in one broadcast domain means broadcast traffic drowns everyone — which is *the* reason to split networks up.

**VLANs** let one physical switch host several logical broadcast domains by tagging frames with a VLAN ID (802.1Q). This is how a single switch serves separate "production" and "guest" networks, and it's the physical mechanism behind a lot of [[cybersecurity/03-network-security/02-network-segmentation|segmentation]] policy.

## Wi-Fi, briefly, because it breaks assumptions

Wired Ethernet is nearly lossless — a dropped packet almost always means congestion. Wi-Fi is not:

- Loss comes from **interference and distance**, not congestion. This wrecks the core assumption of classic [[foundations/networking/08-congestion-control|congestion control]] ("loss means slow down"), which is part of why loss-based algorithms behave badly on wireless and why **BBR** measures the path instead of waiting for loss.
- It's **half-duplex and shared** — the access point and every client contend for the same air. Your "1 Gbps Wi-Fi" is shared with everyone in range.
- It retransmits at layer 2, which turns loss into **latency variance** (jitter) instead of loss. Good for TCP throughput, bad for real-time audio.

## Key insight

The link layer is where the **abstraction is deliberately broken and re-made at every hop**. The IP header stays intact end-to-end; the Ethernet frame around it is destroyed and rebuilt by every router on the path. Understanding that a packet has a permanent final address *and* a temporary next-hop address is the single mental shift that makes routing, ARP, NAT, and traceroute all make sense at once.

## Related
- [[foundations/networking/03-ip-addressing-and-subnetting|IP Addressing & Subnetting]] — the hierarchical addressing MAC can't do
- [[foundations/networking/04-routing|Routing]] — how the next hop is chosen
- [[foundations/networking/16-debugging-networks|Debugging Networks]] — `ip neigh`, `arping`, and diagnosing MTU black holes
- [[cybersecurity/03-network-security/02-network-segmentation|Network Segmentation]] — VLANs and broadcast domains as a security boundary
