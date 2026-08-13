# Networking Interview — TCP & Transport

From [[foundations/networking/05-udp-and-ports|05-udp-and-ports]], [[foundations/networking/06-tcp-connection-lifecycle|06-tcp-connection-lifecycle]], [[foundations/networking/07-tcp-reliability-and-flow-control|07-tcp-reliability-and-flow-control]], [[foundations/networking/08-congestion-control|08-congestion-control]], [[foundations/networking/09-sockets-and-the-network-api|09-sockets-and-the-network-api]].

---

### Q1. [Beginner] 🔥 Why is the TCP handshake three messages and not two?

**Strong answer covers:** each side must confirm that **both** directions work. SYN proves the client can send. SYN-ACK proves the server received and can send. The final ACK proves the client received the server's message. With only two messages, the server never learns its own packets are arriving.

**Detail worth adding:** the handshake also exchanges **initial sequence numbers** for both directions independently (TCP is full-duplex). The ISN is **randomised** — not for load-balancing but for security: a predictable ISN lets an off-path attacker inject data into an existing connection or complete a handshake while spoofing a source address.

**The cost to name:** one full RTT before any data. Stack TLS on top and you're at 2–3 RTTs. That accumulated tax is the entire motivation for QUIC and for connection reuse.

---

### Q2. [Intermediate] 🔥 What is `TIME_WAIT`, why does it exist, and what do you do when you have 50,000 of them?

**Strong answer covers:** the side that **closes first** waits 2×MSL (60s on Linux) before releasing the socket. Two reasons: (1) if the final ACK is lost, the peer will retransmit its FIN and needs someone present to re-ACK it; (2) a delayed duplicate packet from this connection could otherwise be accepted by a *new* connection reusing the same 4-tuple.

**What to do about 50,000 of them — in the right order:**
1. **Reuse connections** (keep-alive, connection pooling). This is the actual fix — it removes the churn rather than managing it.
2. Make the **server** close first where possible, so the accumulation lands on the side with fewer connections per peer.
3. `net.ipv4.tcp_tw_reuse=1` — safe reuse for *outbound* connections, validated by timestamps.

**The trap to avoid, and say so:** **`tcp_tw_recycle` — never.** It was removed in Linux 4.12 because it broke horribly behind NAT (it assumed per-host timestamp monotonicity, which multiple clients behind one NAT violate). Naming this unprompted signals you've actually operated systems rather than read a blog post.

---

### Q3. [Intermediate] 🔥 You see thousands of sockets in `CLOSE_WAIT`. What's wrong?

**Strong answer covers:** `CLOSE_WAIT` means **the peer sent a FIN and your application hasn't called `close()`**. The kernel is waiting on *you*. This is a file-descriptor leak in your code — almost always an error path that returns without cleaning up the socket. It ends in "too many open files."

**Contrast to draw:** `FIN_WAIT_2` is the mirror image — *you* closed, the **peer** hasn't. That's their bug.

**Detail worth adding:** this is one of the highest-signal things in `ss -tan` output, because it points directly at application code rather than at the network.

---

### Q4. [Intermediate] Explain the difference between flow control and congestion control.

**Strong answer covers:** **flow control protects the receiver** (don't send faster than they can consume) via the receive window advertised in every ACK. **Congestion control protects the network** (don't send faster than the path can carry) via the congestion window, which nobody advertises — the sender infers it from feedback. The sender is limited by `min(rwnd, cwnd)`.

**Why the distinction matters practically:** they fail differently and need different fixes. A zero-window stall means *the receiving application isn't reading fast enough* — a consumer problem. Retransmissions and a shrinking cwnd mean *the path is congested* — a network problem. Conflating them sends you optimising the wrong thing.

---

### Q5. [Intermediate→Advanced] 🔥 What is head-of-line blocking in TCP, and why doesn't HTTP/2 fix it?

**Strong answer covers:** TCP delivers a strictly ordered byte stream, and acknowledgements are **cumulative** — `ack=2000` means "I have everything up to 1999." If a segment is lost, the receiver may hold later segments in its buffer but **cannot deliver them to the application**, because that would break ordering. One lost packet stalls everything behind it.

**Why HTTP/2 doesn't fix it:** HTTP/2 multiplexes many streams over **one TCP connection**. It removes head-of-line blocking at the *application* layer, but the transport underneath still enforces total ordering — so one lost packet stalls *every* stream. HTTP/2 moved the problem down a layer rather than eliminating it. On a lossy network HTTP/2 can therefore be **slower than HTTP/1.1 with six connections**, because those six fail independently.

**The resolution:** QUIC gives each stream its own delivery guarantee, so loss affects only its own stream. This is the single strongest argument for HTTP/3.

**Clarify SACK if it comes up:** SACK tells the *sender* precisely what's missing so it retransmits only the gap. It fixes sender efficiency; it does **not** let the receiver deliver out of order.

---

### Q6. [Intermediate] What causes a mysterious 40ms delay in a request/response protocol?

**Strong answer covers:** the **Nagle's algorithm + delayed ACK** interaction. Nagle (sender) won't send a small segment while an earlier small segment is unacknowledged. Delayed ACK (receiver) waits ~40ms hoping to piggyback the ACK on outgoing data. If your app writes a header, then a body, then waits for a response: Nagle holds the second write, the receiver can't respond to an incomplete request so it holds the ACK, and **both sides wait for a timer**.

**The fixes, best first:** write the whole message in **one `write()`/`writev()`** so it never arises; or set **`TCP_NODELAY`**, which nearly every RPC library and database driver does by default.

**The generalisable lesson worth stating:** two locally-sensible optimisations can compose into a pathology neither causes alone. The same class of bug shows up in message queues and event loops.

---

### Q7. [Advanced] 🔥 Why does TCP use AIMD specifically? Why not additive decrease, or multiplicative increase?

**Strong answer covers:** Chiu & Jain (1989) proved that among linear control rules, **only additive-increase/multiplicative-decrease converges to a fair and efficient allocation** from arbitrary starting points. Additive decrease doesn't converge to fairness — flows keep their relative advantage. Multiplicative increase is unstable — it overshoots and oscillates. The sawtooth shape isn't a heuristic; it's forced by the maths.

**Context that lands well:** it's a distributed resource-allocation algorithm with **no coordinator and no communication between participants**, allocating a resource none of them can directly measure. It works because the rule's shape converges and because nearly everyone voluntarily runs it — which is precisely why writing a UDP application without congestion control is defection, not just risk.

**If pushed on modern algorithms:** CUBIC (Linux default) grows as a cubic function of time since last loss, making it RTT-fair and fast to recover on long fat links. BBR abandons loss as the signal entirely — it estimates bottleneck bandwidth and minimum RTT and paces to the BDP, so it doesn't need to fill queues to learn anything. That matters on wireless (where loss ≠ congestion) and against bufferbloat.

---

### Q8. [Intermediate] Why do short HTTP responses not use the available bandwidth?

**Strong answer covers:** **slow start.** A new connection begins at ~10 segments and doubles per RTT. A small response finishes before TCP has discovered how fast the path could go — it never leaves slow start. So for typical web traffic the bottleneck is **the number of round trips, not bandwidth**.

**The conclusion to draw:** this is why connection reuse matters so much (a warm connection has already grown its window), why the first ~14 KB of a response is special in web-performance advice, and why upgrading a link often changes nothing measurable.

---

### Q9. [Intermediate] 🔥 When would you choose UDP over TCP?

**Strong answer covers:** when TCP's guarantees are *harmful*, not merely unnecessary:
- **Real-time media** — a late packet is worse than a lost one; retransmission would stall the stream.
- **Independent multiplexed streams** — TCP's ordering creates head-of-line blocking across unrelated messages.
- **Single small request/response** — DNS; a handshake would triple the cost.
- **You need custom semantics** — partial reliability, custom congestion control, connection migration. TCP is in the kernel and can't be reshaped.

**The responsibility to name — this is what interviewers are listening for:** choosing UDP means **you have taken on congestion control yourself.** A UDP app that blasts at a fixed rate starves every TCP flow sharing the path and can drive congestion collapse. QUIC and WebRTC both implement full congestion control in userspace because they had to.

---

### Q10. [Intermediate→Advanced] 🔥 Walk me from `select()` to `epoll` — why did each exist?

**Strong answer covers:** the driver is **C10K**: blocking I/O costs one thread per connection (~1 MB stack plus scheduling), but most connections are idle, so you're paying for concurrency you don't use. The alternative is non-blocking sockets plus asking the kernel which are ready.

- `select()` — pass a bitmap of all fds each call; kernel scans all of them. **O(n) per call**, capped at 1024.
- `poll()` — array instead of bitmap, no cap, still O(n).
- **`epoll`/`kqueue`** — register fds **once**; the kernel maintains the set and returns only the ready ones. **O(ready)**, scales to millions.
- **`io_uring`** — shared submission/completion rings; submit *operations*, not just readiness. Fewer syscalls, and genuinely async (works for file I/O too).

**The pattern to articulate:** each step stops re-telling the kernel what you care about on every call.

**The trade to mention:** an event loop handles huge connection counts cheaply, but **any blocking work stalls every connection** — hence "never block the event loop" in Node, and why Redis is blazing until you run `KEYS *`. And note that threads came back via green/virtual threads (goroutines, Java's Loom): the *programming model* (blocking, readable) and the *execution model* (multiplexed onto few OS threads) never actually had to match.

---

### Q11. [Intermediate] 🔥 Your protocol works locally but corrupts messages in production. Why?

**Strong answer covers:** **TCP is a byte stream, not a message stream.** `write("HELLO")` then `write("WORLD")` may arrive as one read of `"HELLOWORLD"`, or as `"HEL"` + `"LOWORLD"`. You must frame messages yourself — a length prefix or a delimiter.

**Why it only shows up in production:** loopback rarely splits or coalesces the way a real network does, so the bug is invisible locally. This is the single most common "worked on my machine" network bug.

**Related lies from the same API worth mentioning:** a successful `write()` means "copied to the kernel buffer," not "delivered" — only an application-level ack proves processing. A short `read()` is normal, not an error. And a peer whose machine loses power sends no FIN or RST, so your socket stays `ESTABLISHED` until you try to write — which is why heartbeats exist.
