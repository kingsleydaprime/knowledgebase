# Routing — Finding a Path Nobody Knows

**[Intermediate]** — how a packet crosses a dozen networks owned by companies that have no contract with each other, when **no single machine anywhere knows the whole path**.

## The kid version first

You're in a strange city trying to reach the airport, and there are no maps. But at every junction there's a signpost saying only: **"Airport → turn left."** Not how far, not the route after that. Just the next turn.

Follow enough signposts and you get there. No signpost knows the whole way; each only knows *the next step for each possible destination*. That's routing. The signposts are routing tables, and the interesting question isn't how a packet is forwarded — it's **who writes the signposts, and how they agree.**

## Forwarding vs routing — the distinction everything hinges on

Two different jobs, often confused, running at completely different speeds:

- **Forwarding** (the *data plane*) — for this one packet, look up the destination and send it out an interface. Happens billions of times a second, in hardware. Microseconds.
- **Routing** (the *control plane*) — build and maintain the table by talking to other routers. Happens continuously in the background, in software. Seconds to minutes.

This split is why a router can forward at line rate while running complex protocols, and it's the same architectural split you'll recognise in [[devops/05-orchestration/README|Kubernetes]] (controllers reconcile; kube-proxy forwards) and in [[architecture/03-architectural-patterns/04-microservices-patterns|service mesh]] design.

## Reading a routing table

```
$ ip route
default via 192.168.1.1 dev wlan0            # 0.0.0.0/0 — everything else
192.168.1.0/24 dev wlan0 proto kernel scope link src 192.168.1.42
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1
```

Each line is *destination prefix → how to reach it*. `default` is `0.0.0.0/0` — a prefix matching every address, the fallback.

**Longest prefix match** is the selection rule: when several entries match, **the most specific wins**. A packet for `192.168.1.5` matches both `192.168.1.0/24` and `default`; the /24 is longer, so it wins. This single rule is what makes hierarchical addressing work — a provider can advertise one big `/16` while a customer inside it advertises their own `/24`, and traffic still reaches the customer.

It's also the mechanism behind a lot of practical work: a VPN "split tunnel" is just more-specific routes pointing at the tunnel interface; the reason a Docker container can't reach your `10.x` corporate network is often a `172.17.0.0/16` route shadowing something.

## Interior routing — inside one organisation

Within a single administrative domain (an **AS**, Autonomous System), routers cooperate fully and optimise for shortest path. Two families:

- **Distance-vector** (RIP) — each router tells its neighbours "I can reach X at cost N." Simple, but converges slowly and suffers **count-to-infinity**: when a link dies, routers can bounce a stale route between each other, each adding one to the cost, believing the other still has a path. Mitigated with split horizon and poison reverse; fundamentally, *nobody has the full picture, so nobody can tell a real path from an echo of their own*.
- **Link-state** (OSPF, IS-IS) — every router floods a description of *its own links* to everyone, so all routers build an identical map of the whole domain, then each runs **Dijkstra** locally. Converges fast, no count-to-infinity, but every router holds the full topology — which is exactly why this can't work for the whole internet.

That's a genuinely useful trade to have internalised: **distance-vector = local knowledge, slow convergence; link-state = global knowledge, doesn't scale.** It's the same tension as gossip vs. consensus in [[architecture/04-distributed-systems/14-failure-detection-and-membership|failure detection]].

## BGP — how the internet actually holds together

Between organisations, shortest path is the wrong goal. Cost, contracts, and politics dominate: a route through your paid transit provider costs money; a route through a settlement-free peer is free. **BGP** (Border Gateway Protocol) is therefore a **path-vector** protocol built around *policy*, not distance.

- Each AS advertises "I can reach `203.0.113.0/24`, via AS path `[64500, 64501]`." The full AS path travels with the advertisement, which makes loops detectable (see your own AS number → discard) without any global map.
- Route selection considers **local preference** (business policy) *before* AS-path length. The internet routinely takes a longer path because it's cheaper.
- It is built on trust. Historically, **any AS could announce any prefix** and much of the internet would believe it. That's **BGP hijacking** — the mechanism behind Pakistan Telecom taking YouTube offline globally in 2008, and multiple cryptocurrency thefts since. Mitigations (RPKI origin validation) are being deployed, slowly.

The takeaway for an engineer who isn't a network operator: **the internet's core routing is consensus-free, policy-driven, and trust-based.** Your traffic's path is a business decision made by strangers, it changes without warning, and it is not authenticated. That is a load-bearing assumption behind why you encrypt everything ([[foundations/networking/12-tls-and-transport-security|TLS]]) and why latency to a given host can change overnight for no reason you control.

**Anycast** is the useful trick built on BGP: announce the *same* prefix from many locations, and each client's traffic naturally lands on the topologically nearest one. This is how [[foundations/networking/10-dns-in-depth|DNS root servers]] and CDN edges work — one IP address, hundreds of physical sites.

## TTL, ICMP, and how traceroute works

Every IP packet carries a **TTL** (hop limit), decremented by each router. At zero the packet is discarded and the router sends back an ICMP **Time Exceeded**. This exists to stop packets circulating forever during a routing loop.

**Traceroute** weaponises it beautifully: send a packet with TTL=1 (the first router complains, revealing itself), then TTL=2, then TTL=3. Each complaint names one hop.

Reading traceroute output correctly requires knowing its limits, which is where most people misread it:

- **Stars (`* * *`) usually mean "this router doesn't send ICMP,"** not "the packet died here." Routers deprioritise or block ICMP generation. A middle hop full of stars with the final hop responding is *fine*.
- **The path is one-way.** Reply latency includes the return path, which may be completely different. A slow-looking hop may just be a slow route home.
- **Latency at one hop that recovers later is not a problem** — it means that router was slow to *generate ICMP* (a control-plane task it deprioritises), not slow to forward.
- Use **`mtr`** instead where you can: it runs continuously and shows loss *per hop over time*, which distinguishes a genuinely lossy link from ICMP rate-limiting.

## Key insight

No entity on the internet knows the route your packet takes. Routing is an **emergent, continuously renegotiated agreement** between independent parties with conflicting incentives — which is why the path is asymmetric, changes without notice, is optimised for money rather than speed, and is not authenticated. Design as if the network between two points is an untrusted stranger who reroutes you at will, because it is.

## Related
- [[foundations/networking/03-ip-addressing-and-subnetting|IP Addressing & Subnetting]] — the prefixes routers match on
- [[foundations/networking/16-debugging-networks|Debugging Networks]] — traceroute/mtr in practice
- [[foundations/networking/15-network-performance|Network Performance]] — why path length is a latency floor
- [[architecture/04-distributed-systems/14-failure-detection-and-membership|Failure Detection & Membership]] — gossip, the same convergence problem one layer up
