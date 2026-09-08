# NAT, Firewalls & Middleboxes

**[Intermediate→Advanced]** — everything sitting between your two endpoints that the layered model says shouldn't exist. Reality: the internet is full of boxes that read and rewrite layers that aren't theirs, and they shape what protocols are even *possible*.

## The kid version first

The postal system was supposed to just move letters. Instead there are offices along the way that **open your envelope, read it, sometimes rewrite the address, sometimes throw it away**, and always refuse to handle any envelope shaped in a way they've not seen before.

Two consequences follow, and they explain a huge amount of modern networking:

1. **Two people behind different offices can't easily start a conversation** — each office only forwards letters that are replies to something sent from inside. (NAT traversal.)
2. **Nobody can invent a new envelope shape**, because the offices drop what they don't recognise. (Ossification.)

## NAT traversal — the hardest common problem

[[foundations/networking/03-ip-addressing-and-subnetting|NAT]] means an inside host has no address the outside can reach. Fine for client-server: you initiate, the mapping is created, replies come back. Fatal for **peer-to-peer** — video calls, games, file sharing — where both parties are behind NATs and neither can be reached first.

**NAT types**, and the reason they matter:

| Type | Mapping behaviour | Traversable? |
|---|---|---|
| **Full cone** | one external port per internal socket, anyone may use it | easy |
| **Restricted cone** | only hosts you've sent to may reply | with help |
| **Port-restricted cone** | only host+port you've sent to | with help |
| **Symmetric** | a *different* external port per destination | **very hard** — the port you learn is not the port your peer will see |

The toolchain that grew around this:

- **STUN** — "what does my address look like from outside?" You ask a public server, it tells you the external IP/port your NAT assigned. Cheap, works for most NAT types.
- **Hole punching** — both peers send packets *at the same time* to each other's discovered external addresses. Each outbound packet creates a mapping in its own NAT, so the incoming packet from the peer now matches an existing entry and is allowed through. Elegant — you're deliberately tricking both NATs into thinking each side initiated. Fails against symmetric NAT, because the external port differs per-destination so the address STUN gave you isn't the one your peer will hit.
- **TURN** — give up and relay everything through a public server. Always works, costs bandwidth and adds latency. This is why WebRTC deployments need TURN infrastructure and why it's the expensive part.
- **ICE** — the orchestrator: gather every candidate address (local, STUN-discovered, TURN-relayed), try them all in parallel, use whichever connects first. This is what WebRTC actually runs.

Roughly 80–90% of connections succeed via STUN + hole punching; the rest fall back to TURN. Budget for it.

**UPnP/NAT-PMP/PCP** let an inside host *ask* the router to open a port. Convenient, widely disabled, and historically a security disaster (any device on the LAN, including malware or a malicious webpage, could open holes).

## Firewalls — and reject vs. drop

A firewall filters by rules on the 4-tuple and connection state. Two categories worth distinguishing:

- **Stateless** packet filters — evaluate each packet alone. Fast, dumb.
- **Stateful** — track connections (`conntrack` on Linux), so "allow replies to connections I initiated" is expressible. This is what nearly everything is.

**The single most useful operational distinction in this note:**

- **REJECT** sends back an ICMP unreachable or a TCP RST → the client fails **immediately** with "connection refused."
- **DROP** silently discards → the client **hangs until timeout**.

So: *"connection refused" instantly = you reached something and it said no. A 30-second hang = something is silently dropping.* That one diagnostic split will save you hours, repeatedly. It's also why cloud security groups (which DROP) produce hangs, while a service that simply isn't running produces instant refusals.

**Stateful firewalls have finite tables.** `conntrack` table exhaustion under load produces mysterious dropped connections with `nf_conntrack: table full` in dmesg — a real and easily-missed production failure. And stateful timeouts are why idle connections silently die (see [[foundations/networking/06-tcp-connection-lifecycle|keepalives]]).

## Proxies and load balancers

| Kind | Operates at | Sees | Can |
|---|---|---|---|
| **L4 (TCP) LB** | transport | 4-tuple only | forward fast, no HTTP awareness, **works with any protocol** |
| **L7 (HTTP) LB** | application | full request | route by path/header, retry, rewrite, terminate TLS |
| **Forward proxy** | on behalf of clients | outbound requests | filter/log/cache egress |
| **Reverse proxy** | on behalf of servers | inbound requests | TLS termination, caching, LB |

Two recurring practical problems:

- **The client IP disappears.** Behind a proxy, your server sees the proxy's address. `X-Forwarded-For` / the `PROXY` protocol restore it — and **`X-Forwarded-For` is client-controllable**, so trusting it blindly lets anyone spoof their IP past your rate limiter or IP allowlist. Only trust the hops you control (count from the right).
- **TLS termination boundaries.** Terminating at the edge means plaintext internally. Fine if the internal network is trusted; [[foundations/networking/12-tls-and-transport-security|mTLS]]/service mesh exists because that assumption keeps turning out to be wrong.

Also worth internalising: L7 proxies **re-parse and re-serialise HTTP**, and when the front-end and back-end disagree about how to parse a request (`Content-Length` vs `Transfer-Encoding`), you get **request smuggling** — one of the highest-severity web vulnerability classes, and a direct consequence of having a middlebox interpret a layer it doesn't own. → [[cybersecurity/04-web-security/README|web security]]

## Ossification — the deep cost

The end-to-end principle said the middle of the network should be dumb. It isn't. Middleboxes parse TCP options, rewrite headers, enforce assumptions about what "normal" traffic looks like — and **drop what they don't recognise**.

The consequence is that **the internet has become resistant to change at exactly the layers it was designed to evolve at**:

- **TCP Fast Open** — standardised 2014, still not reliably deployable; middleboxes strip the option or drop the SYN.
- **ECN** — a strictly better congestion signal ([[foundations/networking/08-congestion-control|note 08]]), delayed ~20 years because some middleboxes dropped packets with those bits set.
- **MPTCP** — multipath TCP, heavily constrained by what middleboxes tolerate.
- **New IP protocol numbers** — effectively impossible to deploy. This is *why* [[foundations/networking/13-quic-and-modern-transport|QUIC]] is built on UDP rather than as a new protocol: UDP is one of the two things guaranteed to pass.

QUIC's response — encrypt the headers so middleboxes physically cannot inspect them — is the strongest available statement about how bad this got. **The protocol hides from the network to preserve its right to change.**

There's a general engineering lesson here that transfers well past networking: **any interface others can observe will be depended upon, and anything depended upon becomes impossible to change.** That's Hyrum's Law operating at internet scale. If you intend to keep evolving something, don't expose its internals — the same reason you version an API and keep implementation details private.

## Key insight

The clean layered model in [[foundations/networking/01-what-a-network-is|note 01]] describes how the internet was designed, not how it runs. In practice a packet crosses NATs that rewrite it, firewalls that judge it, and proxies that reassemble it — each violating layer boundaries for a locally-good reason. Every one of those violations bought something real (address scarcity relief, security, scalability) and cost the same thing: **the ability of the network to evolve.** Modern protocol design is largely the work of routing *around* that accumulated cost.

## Related
- [[foundations/networking/03-ip-addressing-and-subnetting|IP Addressing]] — NAT's origin
- [[foundations/networking/13-quic-and-modern-transport|QUIC]] — the response to ossification
- [[architecture/02-building-blocks/01-load-balancing-and-proxies|Load Balancing & Proxies]] — the architecture view
- [[cybersecurity/03-network-security/01-firewalls|Firewalls]] — the security view
