# What a Network Actually Is

**[Beginner]** — the foundation note. Everything else in this folder is a detail of what's introduced here: **packet switching** and **layering**. If you only ever read one note in this course, read this one twice.

## The kid version first

You want to send a long letter to a friend in another city. Two ways to do it:

- **Reserve a private road** from your house to theirs. Nobody else may drive on it while you're using it. Your letter arrives in perfect order, at a guaranteed speed — but the road sits empty whenever you pause to think, and you had to book it in advance. This is **circuit switching** — the old telephone network.
- **Chop the letter into postcards**, number them, and drop them in the ordinary mail. Each postcard finds its own way. They share the roads with everyone else's mail, so the roads are never idle. But postcards can arrive out of order, late, or not at all — and *you* have to reassemble them. This is **packet switching** — the internet.

The internet chose postcards. Nearly every difficulty in this entire folder — retransmission, ordering, congestion, latency spikes — is the bill for that choice. And nearly every benefit — that a single fiber can carry a billion conversations, that a failed router routes around itself, that you don't book a call before loading a webpage — is what you bought with it.

## Why packet switching won

Circuit switching wastes capacity on **bursty** traffic. A human conversation is maybe 40% silence; a web session is a 200ms burst followed by 30 seconds of you reading. If you reserve capacity for the peak, you idle through the average.

Packet switching gets **statistical multiplexing**: because many flows are bursty and their bursts don't line up, a link sized well below the sum of everyone's peaks still serves everyone most of the time. This is the same insight as an airline overbooking a flight, or a bank not keeping every depositor's money in the vault. It works because of averaging — and it fails, occasionally and spectacularly, when everyone bursts at once. That failure has a name: **congestion**, and [[foundations/networking/08-congestion-control|an entire note]] on how the internet keeps itself from collapsing under it.

The second win is **failure independence**. In a circuit-switched network, a dead switch kills every call through it. In a packet-switched network, each packet is routed independently, so the next one just takes another path. Nobody has to tear down and rebuild a connection — the connection was never a physical thing to begin with. That's the deep idea: **a "connection" on the internet is a shared fiction agreed on by the two endpoints**, not a resource the network holds. See [[foundations/networking/06-tcp-connection-lifecycle|the TCP connection lifecycle]] for what that fiction costs to maintain.

## Layering — the idea that made the internet buildable

Here's the real problem: you want any program to talk to any other program, over any physical medium (copper, fiber, radio, satellite), across any number of intermediate networks owned by companies that have never met. Writing that as one piece of software is impossible.

The solution is a **stack of layers**, each one solving exactly one problem and using only the layer below it:

| # | Layer | The one question it answers | Address it uses | Examples |
|---|---|---|---|---|
| 5 | **Application** | What do these bytes *mean*? | URL, name | HTTP, DNS, SSH, SMTP |
| 4 | **Transport** | Which *program* on the host, and is delivery reliable? | Port | TCP, UDP, QUIC |
| 3 | **Network** | How do I reach a host *anywhere in the world*? | IP address | IP, ICMP |
| 2 | **Link** | How do I reach the next machine *on this wire*? | MAC address | Ethernet, Wi-Fi |
| 1 | **Physical** | How do I turn a bit into a signal? | — | copper, fiber, radio |

(You'll also meet the 7-layer **OSI** model, which splits the application layer into three. Nobody implements OSI; it survives as vocabulary — "that's a layer 7 load balancer" means "it reads HTTP." The 5-layer model above is what the internet actually is. The ops-facing view of the same map is in [[devops/08-networking-and-web/01-networking-and-protocols|devops networking & protocols]].)

The contract between layers is deliberately narrow: **the layer below promises to move a chunk of bytes to a destination, and promises nothing else.** IP does not promise the packet arrives. Ethernet does not know what an IP address is. HTTP does not know whether it's running over TCP or QUIC.

### Encapsulation — layering made physical

Each layer wraps the layer above in its own header, like nesting envelopes:

```
[ Ethernet header | IP header | TCP header | HTTP request | Ethernet trailer ]
 \_______________/ \_________/ \__________/ \____________/
   next hop MAC     dest IP     dest port     the actual thing you wanted
```

Sending is wrapping; receiving is unwrapping. Every router along the path opens **only the IP envelope**, looks at the destination, and passes it on — it never reads the TCP or HTTP inside. That is why the internet scales: the machines in the middle do the least possible work, and all the complexity lives at the edges.

That principle has a name — the **end-to-end argument** (Saltzer, Reed & Clark, 1984): *a function should be implemented at the endpoints unless the network can implement it more efficiently and correctly.* Reliability is the classic case. The network *could* make every hop reliable, but the endpoints would still need their own check (a router could corrupt data after verifying it), so hop-by-hop reliability is redundant work. Hence: IP is unreliable on purpose, and TCP fixes it at the edges.

You will see this argument violated constantly by NATs, firewalls, and other **middleboxes** — and you'll see [[foundations/networking/14-nat-firewalls-and-middleboxes|what that costs us]] in the note on ossification.

## What actually happens when you load a webpage

The whole course, compressed. You type `example.com`:

1. **Name → address.** Your machine asks a DNS resolver for the IP. That itself is a network round trip, often several. → [[foundations/networking/10-dns-in-depth|DNS in depth]]
2. **Is it local or remote?** Your host compares the destination IP against its own subnet mask. Local → send directly. Remote → send to the default gateway. → [[foundations/networking/03-ip-addressing-and-subnetting|addressing & subnetting]]
3. **Find the next machine's hardware address.** ARP asks "who has 192.168.1.1?" and caches the answer. → [[foundations/networking/02-the-link-layer|the link layer]]
4. **Hop across the internet.** Each router does a longest-prefix-match lookup and forwards. Nobody knows the whole path; each knows only the next step. → [[foundations/networking/04-routing|routing]]
5. **Establish a connection.** A three-way handshake creates the shared fiction. → [[foundations/networking/06-tcp-connection-lifecycle|TCP connections]]
6. **Agree on secrecy.** A TLS handshake negotiates keys and verifies the server's certificate. → [[foundations/networking/12-tls-and-transport-security|TLS]]
7. **Ask for the thing.** `GET / HTTP/1.1`. → [[foundations/networking/11-http-evolution|HTTP]]
8. **Receive it, slowly at first.** The sender starts cautious and speeds up, probing for how much the path can take. → [[foundations/networking/08-congestion-control|congestion control]]

Notice that **six network round trips can happen before a single byte of your HTML moves**. That's why [[foundations/networking/15-network-performance|latency, not bandwidth, is what makes the web feel slow]] — and why [[foundations/networking/13-quic-and-modern-transport|QUIC]] exists.

## Key insight

The internet is not a network. It is an **agreement to interoperate**: a minimal, unreliable, best-effort delivery service (IP) that any physical network can implement and any application can build on. Its power comes from what it *refuses* to promise. Everything you want that IP doesn't give you — reliability, ordering, security, identity — is built on top, at the edges, by the two machines that actually care.

## Related
- [[foundations/networking/README|Networking course map]]
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|What Makes Distributed Systems Hard]] — the consequences of unreliable networks, one layer up
- [[devops/08-networking-and-web/01-networking-and-protocols|Networking & Protocols (devops)]] — the same territory from the operator's chair
