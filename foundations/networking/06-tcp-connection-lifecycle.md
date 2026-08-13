# TCP Connection Lifecycle

**[Intermediate]** — how a "connection" gets created and destroyed when there is no such physical thing. This note is the one that pays off most often in production debugging: `TIME_WAIT` exhaustion, SYN backlog drops, half-open connections, and "why is my connection pool broken" all live here.

## The kid version first

Two people want to have a phone conversation, but there are no phones — only postcards that may get lost.

How do you both become confident you're talking to each other and both ready to listen? You each need to know **that you can send, and that they can hear you.** Postcard 1: "Can you hear me?" Postcard 2: "Yes, and can you hear me?" Postcard 3: "Yes."

Three postcards. That's the three-way handshake, and it's the minimum — with two, one side never learns their own messages are getting through.

A "connection" is now just: **both machines have written down the same numbers in their own memory.** Nothing exists in the network. If both sides forget, the connection is gone; if one forgets and the other doesn't, you get a **half-open connection**, which is the source of an entire genre of bug.

## The three-way handshake

```
Client                                     Server
  │                                          │  (LISTEN)
  │──── SYN,  seq=x ────────────────────────►│
  │                                          │  (SYN_RECEIVED)
  │◄─── SYN-ACK, seq=y, ack=x+1 ─────────────│
  │  (ESTABLISHED)                           │
  │──── ACK,  ack=y+1 ──────────────────────►│
  │                                          │  (ESTABLISHED)
  │──── data ───────────────────────────────►│
```

Two things are being agreed, and it's worth separating them:

1. **Mutual reachability** — each side confirms the other can both send and receive.
2. **Initial sequence numbers (ISN)** — each side picks a starting number for its byte stream. Both directions are numbered independently, because TCP is full-duplex.

**Why the ISN is random rather than 0:** if it were predictable, an off-path attacker could forge packets into an existing connection (**sequence prediction / TCP injection**) or complete a handshake while spoofing someone else's address. RFC 6528 specifies a randomised ISN derived from a hash including a secret. This is a security control hiding inside a mechanism that looks purely functional — a good example of how much of TCP's design is scar tissue.

**Cost:** one full round trip (RTT) before any data moves. On a 100ms path that's 100ms of nothing, and then [[foundations/networking/12-tls-and-transport-security|TLS]] wants 1–2 more. This accumulated handshake tax is the single strongest motivation for [[foundations/networking/13-quic-and-modern-transport|QUIC]] and for connection reuse everywhere.

## The SYN backlog and SYN floods

The server allocates state at step 2, when it has only heard *one* packet from an unverified address. That asymmetry is exploitable.

A **SYN flood** sends thousands of SYNs from spoofed sources and never completes the handshake. The server fills its **SYN backlog** queue with half-open connections waiting for an ACK that will never come, and legitimate clients get dropped. Classic resource-exhaustion DoS.

The elegant defence is **SYN cookies**: instead of storing state, the server encodes the connection state *into the ISN it sends back*, cryptographically. It allocates nothing. If a real ACK comes back, the ACK number contains the cookie, and the server reconstructs the state from it. Statelessness as a defence — a genuinely beautiful idea worth stealing for other protocols. (Linux: `net.ipv4.tcp_syncookies`, on by default.)

Two queues matter operationally, and conflating them causes confusion:
- the **SYN queue** (half-open, `tcp_max_syn_backlog`)
- the **accept queue** (fully established, waiting for your app to call `accept()`, sized by the `listen()` backlog and `somaxconn`)

If your application is slow to `accept()`, the accept queue overflows and the kernel **silently drops** established connections. The symptom is clients seeing hangs or resets under load with no error in your app logs. Check it with `ss -lnt` — the `Recv-Q`/`Send-Q` columns on a listening socket are current and max accept-queue depth. → [[foundations/networking/16-debugging-networks|debugging]]

## Teardown, and the TIME_WAIT question

Closing is *four* messages, because each direction closes independently — TCP allows a **half-close**, where one side is done sending but still receiving (this is what `shutdown(SHUT_WR)` does, and how the old `HTTP/1.0` "connection close signals end of body" worked).

```
  │──── FIN ────────────►│   (I'm done sending)
  │◄─── ACK ─────────────│
  │◄─── FIN ─────────────│   (so am I)
  │──── ACK ────────────►│
  │   TIME_WAIT (2×MSL)  │
```

The side that closes first enters **`TIME_WAIT`** for 2× the maximum segment lifetime — 60 seconds on Linux, not tunable without a rebuild. It exists for two real reasons:

1. **The final ACK might be lost.** If it is, the peer retransmits its FIN and needs someone still present to re-ACK it. Vanish immediately and the peer is stuck in `LAST_ACK`.
2. **Stray old packets.** A delayed duplicate from this connection could otherwise be accepted by a *new* connection reusing the same 4-tuple, corrupting its stream.

**The production consequence:** a busy client (or a proxy) that opens and closes many short connections accumulates tens of thousands of `TIME_WAIT` sockets, exhausting ephemeral ports and failing new connections. The reflexes, in order of correctness:

- **Reuse connections.** HTTP keep-alive, a connection pool, `Connection: keep-alive`. This is the actual fix — it removes the churn instead of managing it.
- **Make the *server* close first** where you can, so `TIME_WAIT` accumulates on the side with fewer connections per peer.
- **`net.ipv4.tcp_tw_reuse=1`** — lets the kernel reuse a `TIME_WAIT` socket for a new *outbound* connection when timestamps prove it's safe. Reasonable.
- **`tcp_tw_recycle`** — **do not.** It was removed in Linux 4.12 because it broke horribly behind NAT (it assumed per-host timestamp monotonicity, which many clients behind one NAT violate). If you find this in an old blog post or a legacy sysctl file, delete it.

## The state machine, and the states you'll actually see

`ss -tan` output states, and what each means when you see it pile up:

| State | Meaning | When a pile-up means trouble |
|---|---|---|
| `LISTEN` | waiting for connections | — |
| `SYN_SENT` | sent SYN, no reply | firewall dropping, or host down (a *reject* gives you a fast RST instead) |
| `SYN_RECV` | half-open | SYN flood, or clients disappearing |
| `ESTABLISHED` | open | leaked connections, missing pool limits |
| `FIN_WAIT_2` | we closed, peer hasn't | **peer app isn't closing its socket** — a real application bug |
| `CLOSE_WAIT` | peer closed, **we** haven't | **your app isn't closing its socket** — the classic file-descriptor leak |
| `TIME_WAIT` | waiting out stray packets | connection churn, see above |

`CLOSE_WAIT` accumulating is the highest-signal one on that list: it is almost always *your* code failing to call `close()` on a socket after the peer hung up, usually because an error path skips the cleanup. It ends in "too many open files."

## RST — the other way connections end

A **RST** is an abrupt abort, not a graceful close. You get one when connecting to a port nobody is listening on (that's how "connection refused" happens — instantly, versus a *timeout* when a firewall silently drops instead of rejecting), when sending to a socket that's already closed, or when a middlebox decides to kill your connection.

That distinction is diagnostically valuable: **"connection refused" means you reached the host and nothing was listening. A hang/timeout means something is dropping silently** — a firewall, a security group, a wrong route, or a black-holed [[foundations/networking/02-the-link-layer|MTU]].

## Keepalives and the idle-connection problem

TCP will happily sit idle forever — it sends nothing, so it never learns the peer died or that a [[foundations/networking/03-ip-addressing-and-subnetting|NAT]] dropped the mapping. Both sides think they're connected; the next write fails, minutes later.

TCP keepalive exists but defaults to **2 hours** of idle before the first probe, which is useless for anything real. Most systems set application-level pings (WebSocket ping frames, database pool validation queries) at 30–60 seconds instead — comfortably under typical NAT and load-balancer idle timeouts. That's the actual reason your ORM's connection pool has a "test on borrow" or "max idle time" setting, and why getting it wrong produces the maddening "first request after a quiet period always fails" bug.

## Key insight

A TCP connection is **soft state held only at the two endpoints** — the network holds nothing and knows nothing. Every awkward part of TCP's lifecycle (`TIME_WAIT`, half-open connections, SYN backlogs, keepalives) is the cost of maintaining a shared illusion across an unreliable medium where either party can vanish without notice and the other can't tell the difference between "dead" and "slow." That last impossibility is the same one at the heart of [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|distributed systems]].

## Related
- [[foundations/networking/07-tcp-reliability-and-flow-control|TCP Reliability & Flow Control]] — what happens between handshake and teardown
- [[foundations/networking/09-sockets-and-the-network-api|Sockets & the Network API]] — these states from the code side
- [[foundations/networking/16-debugging-networks|Debugging Networks]] — `ss`, `netstat`, and reading state tables
- [[cybersecurity/06-attacks-and-threats/README|Attacks & Threats]] — SYN floods and connection-exhaustion DoS
