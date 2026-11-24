---
id: b3530cdd-df33-4654-b98d-f2ab0b68673e
---

# Routing — Finding a Path Nobody Knows

Routing is how a message finds its way across the internet from your device to a server far away, one step at a time. No single machine knows the whole path. Each router along the way only knows which direction to send the message next, like signposts on a road.

## The kid version first
<!-- bite: 8406412b-62c8-4558-9997-4240aa089c1a -->

You're in a strange city trying to reach the airport, and there are no maps. But at every junction there's a signpost saying only: **"Airport → turn left."** Not how far, not the route after that. Just the next turn.

Follow enough signposts and you get there. No signpost knows the whole way; each only knows *the next step for each possible destination*. That's routing. The signposts are routing tables, and the interesting question isn't how a packet is forwarded — it's **who writes the signposts, and how they agree.**

## Forwarding vs routing — the distinction everything hinges on
<!-- bite: b983e57d-e716-4fe1-a580-e96ed5948382 -->

Two different jobs, often confused, running at completely different speeds:

- **Forwarding** (the *data plane*) — for this one packet, look up the destination and send it out an interface. Happens billions of times a second, in hardware. Microseconds.
- **Routing** (the *control plane*) — build and maintain the table by talking to other routers. Happens continuously in the background, in software. Seconds to minutes.

This split is why a router can forward at line rate while running complex protocols, and it's the same architectural split you'll recognise in [[devops/10-orchestration/index|Kubernetes]] (controllers reconcile; kube-proxy forwards) and in [[architecture/03-architectural-patterns/04-microservices-patterns|service mesh]] design.

## Reading a routing table
<!-- bite: dbcb2768-8bc4-4439-ab6c-a1be466097e2 -->

```text
$ ip route
default via 192.168.1.1 dev wlan0            # 0.0.0.0/0 — everything else
192.168.1.0/24 dev wlan0 proto kernel scope link src 192.168.1.42
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1
```

Each line is *destination prefix → how to reach it*. `default` is `0.0.0.0/0` — a prefix matching every address, the fallback.

**Longest prefix match** is the selection rule: when several entries match, **the most specific wins**. A packet for `192.168.1.5` matches both `192.168.1.0/24` and `default`; the /24 is longer, so it wins. This single rule is what makes hierarchical addressing work — a provider can advertise one big `/16` while a customer inside it advertises their own `/24`, and traffic still reaches the customer.

It's also the mechanism behind a lot of practical work: a VPN "split tunnel" is just more-specific routes pointing at the tunnel interface; the reason a Docker container can't reach your `10.x` corporate network is often a `172.17.0.0/16` route shadowing something.

## Interior routing — inside one organisation
<!-- bite: b190d524-a781-405b-ba2f-e6987197180b -->

Within a single administrative domain (an **AS**, Autonomous System), routers cooperate fully and optimise for shortest path. Two families:

- **Distance-vector** (RIP) — each router tells its neighbours "I can reach X at cost N." Simple, but converges slowly and suffers **count-to-infinity**: when a link dies, routers can bounce a stale route between each other, each adding one to the cost, believing the other still has a path. Mitigated with split horizon and poison reverse; fundamentally, *nobody has the full picture, so nobody can tell a real path from an echo of their own*.
- **Link-state** (OSPF, IS-IS) — every router floods a description of *its own links* to everyone, so all routers build an identical map of the whole domain, then each runs **Dijkstra** locally. Converges fast, no count-to-infinity, but every router holds the full topology — which is exactly why this can't work for the whole internet.

That's a genuinely useful trade to have internalised: **distance-vector = local knowledge, slow convergence; link-state = global knowledge, doesn't scale.** It's the same tension as gossip vs. consensus in [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure detection]].

## BGP — how the internet actually holds together
<!-- bite: 746023e3-6e61-4972-b490-58bbca01ebbd -->

Between organisations, shortest path is the wrong goal. Cost, contracts, and politics dominate: a route through your paid transit provider costs money; a route through a settlement-free peer is free. **BGP** (Border Gateway Protocol) is therefore a **path-vector** protocol built around *policy*, not distance.

- Each AS advertises "I can reach `203.0.113.0/24`, via AS path `[64500, 64501]`." The full AS path travels with the advertisement, which makes loops detectable (see your own AS number → discard) without any global map.
- Route selection considers **local preference** (business policy) *before* AS-path length. The internet routinely takes a longer path because it's cheaper.
- It is built on trust. Historically, **any AS could announce any prefix** and much of the internet would believe it. That's **BGP hijacking** — the mechanism behind Pakistan Telecom taking YouTube offline globally in 2008, and multiple cryptocurrency thefts since. Mitigations (RPKI origin validation) are being deployed, slowly.

The takeaway for an engineer who isn't a network operator: **the internet's core routing is consensus-free, policy-driven, and trust-based.** Your traffic's path is a business decision made by strangers, it changes without warning, and it is not authenticated. That is a load-bearing assumption behind why you encrypt everything ([[networking/12-tls-and-transport-security/index|TLS]]) and why latency to a given host can change overnight for no reason you control.

**Anycast** is the useful trick built on BGP: announce the *same* prefix from many locations, and each client's traffic naturally lands on the topologically nearest one. This is how [[networking/10-dns-in-depth/index|DNS root servers]] and CDN edges work — one IP address, hundreds of physical sites.

## TTL, ICMP, and how traceroute works
<!-- bite: b6ff1a61-08cc-4190-bb8f-8a53b045ac33 -->

Every IP packet carries a **TTL** (hop limit), decremented by each router. At zero the packet is discarded and the router sends back an ICMP **Time Exceeded**. This exists to stop packets circulating forever during a routing loop.

**Traceroute** weaponises it beautifully: send a packet with TTL=1 (the first router complains, revealing itself), then TTL=2, then TTL=3. Each complaint names one hop.

Reading traceroute output correctly requires knowing its limits, which is where most people misread it:

- **Stars (`* * *`) usually mean "this router doesn't send ICMP,"** not "the packet died here." Routers deprioritise or block ICMP generation. A middle hop full of stars with the final hop responding is *fine*.
- **The path is one-way.** Reply latency includes the return path, which may be completely different. A slow-looking hop may just be a slow route home.
- **Latency at one hop that recovers later is not a problem** — it means that router was slow to *generate ICMP* (a control-plane task it deprioritises), not slow to forward.
- Use **`mtr`** instead where you can: it runs continuously and shows loss *per hop over time*, which distinguishes a genuinely lossy link from ICMP rate-limiting.

## Key insight
<!-- bite: 031f9c28-f8e6-4197-9624-cbcdb671e730 -->

No entity on the internet knows the route your packet takes. Routing is an **emergent, continuously renegotiated agreement** between independent parties with conflicting incentives — which is why the path is asymmetric, changes without notice, is optimised for money rather than speed, and is not authenticated. Design as if the network between two points is an untrusted stranger who reroutes you at will, because it is.

## Check your understanding
<!-- bite: 704f12e3-dd07-4059-a5d2-4f46be6044d5 -->

Try each one before you open the answer.

1. <!-- q: exact id="34517d03" answer="10.1.4.0/22" -->
   A routing table has these entries:

   | Destination | Next hop |
   |---|---|
   | `0.0.0.0/0` | 192.168.1.1 |
   | `10.0.0.0/8` | 10.255.0.1 |
   | `10.1.0.0/16` | 10.1.0.1 |
   | `10.1.4.0/22` | 10.1.4.1 |

   Which entry does a packet for `10.1.5.20` use?

   <details><summary>Answer</summary>

   `10.1.4.0/22`. It matches `/0`, `/8`, `/16` and `/22`, and longest prefix match picks the most specific. A `/22` from `10.1.4.0` covers `10.1.4.0` to `10.1.7.255`, so `10.1.5.20` is inside it.

   </details>

2. <!-- q: gap id="a8db38cf" answers="forwarding;routing" -->
   ___ is looking up one packet's destination and sending it out of an interface, billions of times a second in hardware. ___ is building and maintaining the table by talking to other routers, in software.

   <details><summary>Answer</summary>

   Forwarding (the data plane), then routing (the control plane).

   </details>

3. <!-- q: mcq id="a5d1e9c7" -->
   Which interior routing approach gives every router a full map of the domain, on which each runs Dijkstra?

   - [ ] Distance-vector, as in RIP
   - [x] Link-state, as in OSPF or IS-IS
   - [ ] Path-vector, as in BGP
   - [ ] Anycast

   <details><summary>Answer</summary>

   Link-state. Every router floods a description of its own links, so all of them build the same map. It converges fast and avoids count-to-infinity, but because every router holds the whole topology, it can't scale to the whole internet.

   </details>

4. <!-- q: open id="75561d16" -->
   Why does traffic between two networks on the internet often take a longer path than the shortest one available?

   <details><summary>Answer</summary>

   BGP chooses routes by policy before path length. Local preference, which encodes business deals, is checked first: a route through a free peer beats a shorter one through a paid transit provider. The internet is routed to save money, not hops.

   </details>

5. <!-- q: mcq id="dff67e35" -->
   A traceroute shows `* * *` at hops 4 to 6, and then hops 7 to 10 answer normally with sensible times. What does it mean?

   - [ ] Packets are being lost at hops 4 to 6
   - [x] Those routers don't send ICMP replies, and traffic passes through them fine
   - [ ] The route is broken
   - [ ] The destination is down

   <details><summary>Answer</summary>

   Those routers just don't answer traceroute. If later hops respond, packets went through them. Use `mtr` to see loss per hop over time.

   </details>

6. <!-- q: open id="3a9bf59a" -->
   How does anycast let one DNS root server IP address be served from hundreds of places?

   <details><summary>Answer</summary>

   The same prefix is announced over BGP from many locations. Each client's traffic follows its routers to the nearest announcement in routing terms, so it lands on a nearby site without knowing others exist. CDN edges work the same way.

   </details>

## Related
<!-- bite: 30fb21c4-1de0-4127-bde8-81326615d843 -->
- [[networking/03-ip-addressing-and-subnetting|IP Addressing & Subnetting]] — the prefixes routers match on
- [[networking/16-debugging-networks|Debugging Networks]] — traceroute/mtr in practice
- [[networking/15-network-performance|Network Performance]] — why path length is a latency floor
- [[architecture/04-distributed-systems/14-failure-detection-and-membership|Failure Detection & Membership]] — gossip, the same convergence problem one layer up

## About this lesson
<!-- bite: c64e5f68-358d-4a9b-b007-b98d6b65b945 -->

**Level:** Intermediate. **Covers:** how a packet crosses a dozen networks owned by companies that have no contract with each other, when **no single machine anywhere knows the whole path**.
