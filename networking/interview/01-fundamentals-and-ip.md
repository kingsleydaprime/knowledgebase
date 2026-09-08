# Networking Interview — Fundamentals & IP

From [[foundations/networking/01-what-a-network-is|01-what-a-network-is]], [[foundations/networking/02-the-link-layer|02-the-link-layer]], [[foundations/networking/03-ip-addressing-and-subnetting|03-ip-addressing-and-subnetting]], [[foundations/networking/04-routing|04-routing]].

---

### Q1. [Beginner] 🔥 Walk me through what happens when you type a URL and press enter.

**Strong answer covers:** DNS resolution (stub → recursive resolver → root → TLD → authoritative, with caching at each layer) → the host decides local vs remote by ANDing the destination with its subnet mask → ARP for the next-hop MAC → the packet is forwarded hop-by-hop by longest-prefix match, each router rewriting the Ethernet frame but never touching the IP header → TCP three-way handshake → TLS handshake → HTTP request → response, subject to slow start.

**What separates a strong answer:** *counting the round trips*. DNS + TCP + TLS + request ≈ 4 RTTs before the first byte of HTML, and slow start caps the first response near 14 KB. Saying "and that's why latency rather than bandwidth dominates page load, and why CDNs exist" turns a recitation into an engineering answer.

**The trap:** don't stop at "the browser renders it." The interviewer is probing for depth — pick one layer and go deep when they ask you to.

---

### Q2. [Beginner] Why does a packet need both an IP address and a MAC address?

**Strong answer covers:** they answer different questions. The **IP address is the final destination** and stays constant end-to-end. The **MAC address is the next machine on this physical segment** and is rewritten at every single hop. IP is hierarchical (so routers can hold one entry for millions of addresses); MAC is flat (so it can't be routed globally — every switch would need an entry for every device on Earth).

**Detail worth adding:** this is exactly why ARP exists — it's the join between layer 3 and layer 2, translating "I know the IP of my next hop" into "I know the hardware address to put in the frame."

---

### Q3. [Beginner→Intermediate] 🔥 What is `192.168.1.0/24`? How many usable hosts, and what's the broadcast address?

**Strong answer covers:** `/24` means the first 24 bits are the network portion, leaving 8 host bits → 256 addresses, **254 usable** (subtract the network address `.0` and the broadcast `.255`). Broadcast is `192.168.1.255`. Equivalent mask `255.255.255.0`.

**Be ready to do a harder one live.** `10.0.5.37/28`: mask is `.240`, block size `256−240 = 16`, so blocks are `.0–.15`, `.16–.31`, `.32–.47`. `.37` is in the `.32` block → network `.32`, broadcast `.47`, usable `.33–.46`, 14 hosts. **Practice this until it's reflexive** — it's the one piece of arithmetic they'll actually make you do, and hesitating reads badly.

**Detail worth adding:** smaller prefix = bigger network (`/16` > `/24`), which sounds backwards until you frame it as "fewer bits pinned down."

---

### Q4. [Intermediate] 🔥 What is NAT, and what does it break?

**Strong answer covers:** a router rewrites the source IP (and port) of outbound packets to its own public address, keeping a translation table to reverse it on the way back. It exists because IPv4 has 4.3 billion addresses and we have far more devices.

**What it breaks:** inbound connections (no table entry exists until the inside host sends first) — which is why peer-to-peer needs STUN/hole-punching/TURN. It breaks the end-to-end principle, since a middlebox now rewrites headers. And **NAT table entries time out**, which is the actual root cause of "my WebSocket/DB connection dies after a few minutes idle" — the fix is application-level keepalives under the timeout.

**The point to make firmly:** NAT is **not a firewall**, even though it accidentally blocks inbound traffic. Don't rely on it as a security control.

---

### Q5. [Intermediate] What's the difference between a switch and a router?

**Strong answer covers:** a **switch** operates at layer 2, forwards frames by MAC address, learns which MAC is behind which port by watching source addresses, and forwards broadcasts everywhere — everything on it is one **broadcast domain**. A **router** operates at layer 3, forwards by IP prefix using longest-prefix match, connects different networks, and **does not forward broadcasts** — it's where a broadcast domain ends.

**Detail worth adding:** VLANs let one physical switch host multiple logical broadcast domains via 802.1Q tags, which is the mechanism underneath most network segmentation policy.

---

### Q6. [Intermediate] 🔥 Explain longest prefix match.

**Strong answer covers:** when multiple routing table entries match a destination, **the most specific (longest) prefix wins**. A packet for `192.168.1.5` matches both `192.168.1.0/24` and `0.0.0.0/0` (default); the /24 wins.

**Why it matters:** it's what makes hierarchical addressing work — a provider can advertise an aggregated `/16` while a customer inside it advertises their own `/24`, and traffic still reaches the customer. Practically, it's also why a VPN split-tunnel works (more-specific routes point at the tunnel) and why a Docker bridge on `172.17.0.0/16` can shadow a corporate network.

---

### Q7. [Advanced] How does the internet's routing actually work between organisations, and why isn't it shortest-path?

**Strong answer covers:** **BGP**, a path-vector protocol between Autonomous Systems. Each AS advertises reachable prefixes with the full AS path, which makes loop detection possible without any global topology map. Selection is driven by **policy (local preference) before path length**, because the choice is commercial — traffic over a settlement-free peer is free, transit costs money. So the internet routinely takes a longer path because it's cheaper.

**Detail that shows real understanding:** BGP is **trust-based**. Historically any AS could announce any prefix and much of the internet would believe it — that's BGP hijacking (Pakistan Telecom vs YouTube, 2008; several crypto thefts since). RPKI origin validation is the partial fix, still rolling out. The engineering conclusion: **your traffic's path is a business decision made by strangers, changes without warning, and is not authenticated — which is a load-bearing argument for encrypting everything.**

**Bonus:** anycast — announcing the same prefix from many locations so clients reach the nearest — is how DNS roots and CDNs work.

---

### Q8. [Intermediate] 🔥 A `traceroute` shows `* * *` at hop 7 but hop 12 responds fine. Is hop 7 broken?

**Strong answer covers:** **No.** Stars mean that router didn't send an ICMP Time Exceeded — usually because it deprioritises or blocks ICMP generation, which is a control-plane task routers deliberately rate-limit. If later hops respond, packets are traversing hop 7 fine.

**Detail worth adding:** the same logic applies to a latency *spike* at one hop that disappears at later hops — that's slow ICMP generation, not slow forwarding. Only latency that persists to the destination is real. And traceroute only shows the forward path; the return path may be completely different, which is why the RTT figures can mislead. Use `mtr` for real diagnosis — continuous, with per-hop loss over time.

---

### Q9. [Intermediate] What's MTU, and how does it cause a bug where small requests work but large responses hang?

**Strong answer covers:** MTU is the largest payload a link will carry — 1500 bytes on standard Ethernet. Path MTU Discovery finds the smallest MTU on the path by setting the "don't fragment" bit and relying on routers to return **ICMP "Packet Too Big"**.

**The bug:** if a firewall blocks ICMP, those messages never arrive. The sender keeps transmitting oversized packets that are silently dropped. Small packets (handshake, a `GET`) fit and work; the first large response vanishes and the connection stalls. That's a **PMTU black hole** — and it's the concrete reason "block all ICMP" is bad advice.

**Where you'll actually meet it:** tunnels. VPNs, VXLAN, and Kubernetes overlay networks add headers that shrink the usable MTU below 1500, which is why this bites container networking disproportionately. Confirm with `ping -M do -s 1472 <host>`, shrinking until it passes.

---

### Q10. [Beginner] What does an address in `169.254.x.x` tell you?

**Strong answer covers:** it's a **link-local** self-assigned address, which means **DHCP didn't answer**. It's an instant diagnosis, not a configuration.

**The one to memorise:** `169.254.169.254` is the **cloud metadata service** on AWS/GCP/Azure — it hands out instance credentials to anything that asks. It's the endpoint behind most SSRF privilege escalations, which is why IMDSv2 (requiring a session token) exists and why you should enforce it.
