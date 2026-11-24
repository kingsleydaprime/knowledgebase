---
id: e9c00e96-ebdb-4bfc-b3c4-b25ac2203213
---

# What a Network Actually Is

A network is a set of computers joined together so they can send messages to each other. Every WhatsApp message, video call and web page you open travels across one, usually the internet. This first lesson introduces the two ideas the whole course is built on.

## The kid version first
<!-- bite: e265ab4e-065b-4e23-93bf-6503dd72e6c4 -->

You want to send a long letter to a friend in another city. Two ways to do it:

- **Reserve a private road** from your house to theirs. Nobody else may drive on it while you're using it. Your letter arrives in perfect order, at a guaranteed speed — but the road sits empty whenever you pause to think, and you had to book it in advance. This is **circuit switching** — the old telephone network.
- **Chop the letter into postcards**, number them, and drop them in the ordinary mail. Each postcard finds its own way. They share the roads with everyone else's mail, so the roads are never idle. But postcards can arrive out of order, late, or not at all — and *you* have to reassemble them. This is **packet switching** — the internet.

The internet chose postcards. Nearly every difficulty in this entire folder — retransmission, ordering, congestion, latency spikes — is the bill for that choice. And nearly every benefit — that a single fiber can carry a billion conversations, that a failed router routes around itself, that you don't book a call before loading a webpage — is what you bought with it.

## Why packet switching won
<!-- bite: 77c1646e-5ffe-4155-bb0b-b8e0c532ba49 -->

Circuit switching wastes capacity on **bursty** traffic. A human conversation is maybe 40% silence; a web session is a 200ms burst followed by 30 seconds of you reading. If you reserve capacity for the peak, you idle through the average.

Packet switching gets **statistical multiplexing**: because many flows are bursty and their bursts don't line up, a link sized well below the sum of everyone's peaks still serves everyone most of the time. This is the same insight as an airline overbooking a flight, or a bank not keeping every depositor's money in the vault. It works because of averaging — and it fails, occasionally and spectacularly, when everyone bursts at once. That failure has a name: **congestion**, and [[networking/08-congestion-control|an entire note]] on how the internet keeps itself from collapsing under it.

The second win is **failure independence**. In a circuit-switched network, a dead switch kills every call through it. In a packet-switched network, each packet is routed independently, so the next one just takes another path. Nobody has to tear down and rebuild a connection — the connection was never a physical thing to begin with. That's the deep idea: **a "connection" on the internet is a shared fiction agreed on by the two endpoints**, not a resource the network holds. See [[networking/06-tcp-connection-lifecycle|the TCP connection lifecycle]] for what that fiction costs to maintain.

## Layering — the idea that made the internet buildable
<!-- bite: 0afc39e4-ff37-456f-bfb3-fb306717943f -->

Here's the real problem: you want any program to talk to any other program, over any physical medium (copper, fiber, radio, satellite), across any number of intermediate networks owned by companies that have never met. Writing that as one piece of software is impossible.

The solution is a **stack of layers**, each one solving exactly one problem and using only the layer below it:

| # | Layer | The one question it answers | Address it uses | Examples |
|---|---|---|---|---|
| 5 | **Application** | What do these bytes *mean*? | URL, name | HTTP, DNS, SSH, SMTP |
| 4 | **Transport** | Which *program* on the host, and is delivery reliable? | Port | TCP, UDP, QUIC |
| 3 | **Network** | How do I reach a host *anywhere in the world*? | IP address | IP, ICMP |
| 2 | **Link** | How do I reach the next machine *on this wire*? | MAC address | Ethernet, Wi-Fi |
| 1 | **Physical** | How do I turn a bit into a signal? | — | copper, fiber, radio |

(You'll also meet the 7-layer **OSI** model, which splits the application layer into three. Nobody implements OSI; it survives as vocabulary — "that's a layer 7 load balancer" means "it reads HTTP." The 5-layer model above is what the internet actually is. The ops-facing view of the same map is in [[devops/02-networking-and-web/01-networking-and-protocols|devops networking & protocols]].)

The contract between layers is deliberately narrow: **the layer below promises to move a chunk of bytes to a destination, and promises nothing else.** IP does not promise the packet arrives. Ethernet does not know what an IP address is. HTTP does not know whether it's running over TCP or QUIC.

### Encapsulation — layering made physical

Each layer wraps the layer above in its own header, like nesting envelopes:

```text
[ Ethernet header | IP header | TCP header | HTTP request | Ethernet trailer ]
 \_______________/ \_________/ \__________/ \____________/
   next hop MAC     dest IP     dest port     the actual thing you wanted
```

Sending is wrapping; receiving is unwrapping. Every router along the path opens **only the IP envelope**, looks at the destination, and passes it on — it never reads the TCP or HTTP inside. That is why the internet scales: the machines in the middle do the least possible work, and all the complexity lives at the edges.

That principle has a name — the **end-to-end argument** (Saltzer, Reed & Clark, 1984): *a function should be implemented at the endpoints unless the network can implement it more efficiently and correctly.* Reliability is the classic case. The network *could* make every hop reliable, but the endpoints would still need their own check (a router could corrupt data after verifying it), so hop-by-hop reliability is redundant work. Hence: IP is unreliable on purpose, and TCP fixes it at the edges.

You will see this argument violated constantly by NATs, firewalls, and other **middleboxes** — and you'll see [[networking/14-nat-firewalls-and-middleboxes|what that costs us]] in the note on ossification.

## What actually happens when you load a webpage
<!-- bite: fd8fd801-ff3e-4c26-951f-44148d01535d -->

The whole course, compressed. You type `example.com`:

1. **Name → address.** Your machine asks a DNS resolver for the IP. That itself is a network round trip, often several. → [[networking/10-dns-in-depth/index|DNS in depth]]
2. **Is it local or remote?** Your host compares the destination IP against its own subnet mask. Local → send directly. Remote → send to the default gateway. → [[networking/03-ip-addressing-and-subnetting|addressing & subnetting]]
3. **Find the next machine's hardware address.** ARP asks "who has 192.168.1.1?" and caches the answer. → [[networking/02-the-link-layer|the link layer]]
4. **Hop across the internet.** Each router does a longest-prefix-match lookup and forwards. Nobody knows the whole path; each knows only the next step. → [[networking/04-routing|routing]]
5. **Establish a connection.** A three-way handshake creates the shared fiction. → [[networking/06-tcp-connection-lifecycle|TCP connections]]
6. **Agree on secrecy.** A TLS handshake negotiates keys and verifies the server's certificate. → [[networking/12-tls-and-transport-security/index|TLS]]
7. **Ask for the thing.** `GET / HTTP/1.1`. → [[networking/11-http-evolution/index|HTTP]]
8. **Receive it, slowly at first.** The sender starts cautious and speeds up, probing for how much the path can take. → [[networking/08-congestion-control|congestion control]]

Notice that **six network round trips can happen before a single byte of your HTML moves**. That's why [[networking/15-network-performance|latency, not bandwidth, is what makes the web feel slow]] — and why [[networking/13-quic-and-modern-transport|QUIC]] exists.

## Key insight
<!-- bite: 23f80d81-244b-48a8-86c4-1318c12e41e8 -->

The internet is not a network. It is an **agreement to interoperate**: a minimal, unreliable, best-effort delivery service (IP) that any physical network can implement and any application can build on. Its power comes from what it *refuses* to promise. Everything you want that IP doesn't give you — reliability, ordering, security, identity — is built on top, at the edges, by the two machines that actually care.

## Check your understanding
<!-- bite: 289b9092-8f84-4b9e-8741-959fe9d0fa64 -->

Try each one before you open the answer.

1. <!-- q: mcq id="03c1e953" -->
   Which describes how the internet moves data?

   - [ ] Circuit switching: a path is reserved for the whole conversation
   - [x] Packet switching: data is chopped into packets that each find their own way over shared links
   - [ ] Every router keeps a permanent connection open to every other router
   - [ ] Data is broadcast to every machine on the internet

   <details><summary>Answer</summary>

   Packet switching. Packets share the links with everyone else's traffic, so links are never idle, but packets can arrive late, out of order or not at all, and the endpoints have to cope.

   </details>

2. <!-- q: gap id="a341ba1b" answers="transport;network" -->
   In the five-layer model, the ___ layer picks which program on the host gets the data, using a port. The ___ layer gets a packet to a host anywhere in the world, using an IP address.

   <details><summary>Answer</summary>

   Transport (TCP, UDP, QUIC), then network (IP). Below them are link (MAC addresses, the next machine on this wire) and physical; above them is application (HTTP, DNS).

   </details>

3. <!-- q: mcq id="d087be8d" -->
   A router on the path receives a packet carrying an HTTP request. Which header does it read to decide where to send it?

   - [ ] The HTTP request
   - [ ] The TCP header
   - [x] The IP header
   - [ ] All of them

   <details><summary>Answer</summary>

   Only the IP header. Routers open just the IP envelope and pass the rest on unread. Keeping the middle simple and putting the complexity at the edges is what lets the internet scale.

   </details>

4. <!-- q: open id="fdaa1f69" -->
   A link is sized well below the total of every user's peak traffic, yet everyone gets good service most of the time. What idea makes that work, and when does it fail?

   <details><summary>Answer</summary>

   Statistical multiplexing. Traffic is bursty and different users' bursts rarely line up, so averaging lets a smaller link serve everyone, like an airline overbooking a flight. It fails when many users burst at once, which is congestion.

   </details>

5. <!-- q: open id="ad391580" -->
   IP doesn't promise that packets arrive. Using the end-to-end argument, explain why that is a deliberate choice rather than a flaw.

   <details><summary>Answer</summary>

   A function should live at the endpoints unless the network can do it better and correctly. Even if every hop were reliable, a router could still corrupt data after checking it, so the endpoints would need their own check anyway. Hop-by-hop reliability would be wasted work, so IP stays simple and TCP adds reliability at the edges.

   </details>

6. <!-- q: exact id="4dfde5a8" answer="6" -->
   You open an HTTPS page for the first time. The DNS lookup takes 2 round trips, the TCP handshake 1, a TLS 1.2 handshake 2, and the HTTP request and its response 1. How many round trips pass before the first byte of HTML arrives?

   <details><summary>Answer</summary>

   6: DNS 2 + TCP 1 + TLS 2 + HTTP 1. This is why latency, not bandwidth, makes the web feel slow, and why TLS 1.3 and QUIC cut round trips.

   </details>

## Related
<!-- bite: 9bea2753-f516-4822-9128-e18faa43dd1b -->
- [[networking/index|Networking course map]]
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes Distributed Systems Hard]] — the consequences of unreliable networks, one layer up
- [[devops/02-networking-and-web/01-networking-and-protocols|Networking & Protocols (devops)]] — the same territory from the operator's chair

## About this lesson
<!-- bite: 4e564337-c6d9-4658-885d-6d0c9af66e06 -->

**Level:** Beginner. **Covers:** the foundation note. Everything else in this folder is a detail of what's introduced here: **packet switching** and **layering**. If you only ever read one note in this course, read this one twice.
