---
id: 5b91c819-d812-4a7b-80a5-c7846f02f036
---

# NAT, Firewalls & Middleboxes

NAT, firewalls and other middleboxes are devices sitting between your computer and the server that look at your data, and sometimes change it or block it. Your home Wi-Fi router is one: it lets every device in the house share a single internet address. They are everywhere, and they explain many strange network problems.

## The kid version first
<!-- bite: 879381e0-5950-4fd7-ac29-0c207b5c1e27 -->

The postal system was supposed to just move letters. Instead there are offices along the way that **open your envelope, read it, sometimes rewrite the address, sometimes throw it away**, and always refuse to handle any envelope shaped in a way they've not seen before.

Two consequences follow, and they explain a huge amount of modern networking:

1. **Two people behind different offices can't easily start a conversation** — each office only forwards letters that are replies to something sent from inside. (NAT traversal.)
2. **Nobody can invent a new envelope shape**, because the offices drop what they don't recognise. (Ossification.)

## NAT traversal — the hardest common problem
<!-- bite: f0d52f04-8285-450a-9be0-0b2993bde26e -->

[[networking/03-ip-addressing-and-subnetting|NAT]] means an inside host has no address the outside can reach. Fine for client-server: you initiate, the mapping is created, replies come back. Fatal for **peer-to-peer** — video calls, games, file sharing — where both parties are behind NATs and neither can be reached first.

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
<!-- bite: 0d76b67c-5ccf-4433-9867-a62106c5366f -->

A firewall filters by rules on the 4-tuple and connection state. Two categories worth distinguishing:

- **Stateless** packet filters — evaluate each packet alone. Fast, dumb.
- **Stateful** — track connections (`conntrack` on Linux), so "allow replies to connections I initiated" is expressible. This is what nearly everything is.

**The single most useful operational distinction in this note:**

- **REJECT** sends back an ICMP unreachable or a TCP RST → the client fails **immediately** with "connection refused."
- **DROP** silently discards → the client **hangs until timeout**.

So: *"connection refused" instantly = you reached something and it said no. A 30-second hang = something is silently dropping.* That one diagnostic split will save you hours, repeatedly. It's also why cloud security groups (which DROP) produce hangs, while a service that simply isn't running produces instant refusals.

**Stateful firewalls have finite tables.** `conntrack` table exhaustion under load produces mysterious dropped connections with `nf_conntrack: table full` in dmesg — a real and easily-missed production failure. And stateful timeouts are why idle connections silently die (see [[networking/06-tcp-connection-lifecycle|keepalives]]).

## Proxies and load balancers
<!-- bite: 6c135a0a-3184-40fc-8b55-67af8fd5b2e6 -->

| Kind | Operates at | Sees | Can |
|---|---|---|---|
| **L4 (TCP) LB** | transport | 4-tuple only | forward fast, no HTTP awareness, **works with any protocol** |
| **L7 (HTTP) LB** | application | full request | route by path/header, retry, rewrite, terminate TLS |
| **Forward proxy** | on behalf of clients | outbound requests | filter/log/cache egress |
| **Reverse proxy** | on behalf of servers | inbound requests | TLS termination, caching, LB |

Two recurring practical problems:

- **The client IP disappears.** Behind a proxy, your server sees the proxy's address. `X-Forwarded-For` / the `PROXY` protocol restore it — and **`X-Forwarded-For` is client-controllable**, so trusting it blindly lets anyone spoof their IP past your rate limiter or IP allowlist. Only trust the hops you control (count from the right).
- **TLS termination boundaries.** Terminating at the edge means plaintext internally. Fine if the internal network is trusted; [[networking/12-tls-and-transport-security/index|mTLS]]/service mesh exists because that assumption keeps turning out to be wrong.

Also worth internalising: L7 proxies **re-parse and re-serialise HTTP**, and when the front-end and back-end disagree about how to parse a request (`Content-Length` vs `Transfer-Encoding`), you get **request smuggling** — one of the highest-severity web vulnerability classes, and a direct consequence of having a middlebox interpret a layer it doesn't own. → [[cybersecurity/04-web-security/index|web security]]

## Ossification — the deep cost
<!-- bite: b01c45fd-e74c-411d-9cf0-dbc88102a32d -->

The end-to-end principle said the middle of the network should be dumb. It isn't. Middleboxes parse TCP options, rewrite headers, enforce assumptions about what "normal" traffic looks like — and **drop what they don't recognise**.

The consequence is that **the internet has become resistant to change at exactly the layers it was designed to evolve at**:

- **TCP Fast Open** — standardised 2014, still not reliably deployable; middleboxes strip the option or drop the SYN.
- **ECN** — a strictly better congestion signal ([[networking/08-congestion-control|note 08]]), delayed ~20 years because some middleboxes dropped packets with those bits set.
- **MPTCP** — multipath TCP, heavily constrained by what middleboxes tolerate.
- **New IP protocol numbers** — effectively impossible to deploy. This is *why* [[networking/13-quic-and-modern-transport|QUIC]] is built on UDP rather than as a new protocol: UDP is one of the two things guaranteed to pass.

QUIC's response — encrypt the headers so middleboxes physically cannot inspect them — is the strongest available statement about how bad this got. **The protocol hides from the network to preserve its right to change.**

There's a general engineering lesson here that transfers well past networking: **any interface others can observe will be depended upon, and anything depended upon becomes impossible to change.** That's Hyrum's Law operating at internet scale. If you intend to keep evolving something, don't expose its internals — the same reason you version an API and keep implementation details private.

## Key insight
<!-- bite: b54033c8-9b6c-47b9-bc42-d49d0b054b15 -->

The clean layered model in [[networking/01-what-a-network-is|note 01]] describes how the internet was designed, not how it runs. In practice a packet crosses NATs that rewrite it, firewalls that judge it, and proxies that reassemble it — each violating layer boundaries for a locally-good reason. Every one of those violations bought something real (address scarcity relief, security, scalability) and cost the same thing: **the ability of the network to evolve.** Modern protocol design is largely the work of routing *around* that accumulated cost.

## Check your understanding
<!-- bite: 0e4b2dcd-671e-4a02-897b-edff4f589f9b -->

Try each one before you open the answer.

1. <!-- q: mcq id="fe34d592" -->
   Two peers behind NATs try a video call. STUN and hole punching fail, because one side is behind a symmetric NAT. What does ICE fall back to?

   - [ ] It gives up
   - [x] TURN: relaying all the traffic through a public server
   - [ ] UPnP on both routers
   - [ ] Sending the media over DNS

   <details><summary>Answer</summary>

   TURN. It always works, but costs bandwidth and adds latency, which is why WebRTC needs TURN servers. Symmetric NAT gives a different external port per destination, so the address STUN discovered isn't the one the peer will hit.

   </details>

2. <!-- q: exact id="07ee2a11" answer="45" -->
   A WebRTC app expects about 85% of connections to succeed with STUN and hole punching. On a day with 300 calls, about how many will need a TURN relay?

   <details><summary>Answer</summary>

   45. The other 15% fall back to TURN: 300 × 0.15 = 45. Size and pay for TURN capacity for that share.

   </details>

3. <!-- q: mcq id="90f75550" -->
   Connecting to a server hangs for 30 seconds and then times out. Another server's closed port fails instantly with "connection refused". What does the hang suggest?

   - [ ] The service is running but slow
   - [x] Something on the path is silently dropping packets, such as a firewall rule or a cloud security group
   - [ ] DNS is broken
   - [ ] The server sent a RST

   <details><summary>Answer</summary>

   A silent DROP. REJECT, or a host with nothing listening, answers at once, so you get an instant refusal. A drop sends nothing back, so the client waits until it times out.

   </details>

4. <!-- q: open id="534f99dc" -->
   Your rate limiter reads the client's IP from the `X-Forwarded-For` header. Why is that dangerous, and how should it be done?

   <details><summary>Answer</summary>

   Anyone can send their own `X-Forwarded-For` header, so a client can claim any IP and dodge the rate limit or an IP allowlist. Only trust the entries added by proxies you control: count from the right-hand end by the number of trusted hops, or use the `PROXY` protocol from your load balancer.

   </details>

5. <!-- q: mcq id="018cc3a4" -->
   You need to route `/api/*` to one backend and `/static/*` to another. Which kind of load balancer can do this?

   - [ ] An L4 (TCP) load balancer
   - [x] An L7 (HTTP) load balancer
   - [ ] Either
   - [ ] Neither; you need DNS

   <details><summary>Answer</summary>

   An L7 load balancer, because it reads the HTTP request and can see the path. An L4 load balancer only sees IP addresses and ports.

   </details>

6. <!-- q: open id="876a85e6" -->
   Under heavy load, a Linux server starts dropping new connections, and `dmesg` shows `nf_conntrack: table full`. What happened?

   <details><summary>Answer</summary>

   The stateful firewall tracks every connection in a table of fixed size, and the table filled up, so new connections couldn't be tracked and were dropped. Raise the table size, shorten timeouts for finished connections, or exclude high-volume traffic from tracking.

   </details>

## Related
<!-- bite: 8d55651e-d5a9-4461-a6f8-ee4f19115b5b -->
- [[networking/03-ip-addressing-and-subnetting|IP Addressing]] — NAT's origin
- [[networking/13-quic-and-modern-transport|QUIC]] — the response to ossification
- [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|Load Balancing & Proxies]] — the architecture view
- [[cybersecurity/03-network-security/01-firewalls|Firewalls]] — the security view

## About this lesson
<!-- bite: 7812a006-05ec-428b-9bcc-2421b36a7f95 -->

**Level:** Intermediate→Advanced. **Covers:** everything sitting between your two endpoints that the layered model says shouldn't exist. Reality: the internet is full of boxes that read and rewrite layers that aren't theirs, and they shape what protocols are even *possible*.
