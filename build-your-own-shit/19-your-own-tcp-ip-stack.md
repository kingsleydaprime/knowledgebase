# Build Your Own TCP/IP Stack

> **[Advanced]** · A userspace network stack that real tools talk to. **`ping` answers, `curl` fetches a page, and the server from guide 01 runs on top of your own TCP.**

## What you're building

**A working TCP/IP stack in userspace**, attached to a virtual network interface, speaking enough Ethernet, ARP, IPv4, ICMP, UDP and TCP that unmodified programs on your machine cannot tell the difference. By the end, `curl http://10.0.0.4:8080/` returns a page that travelled through code you wrote, at every layer below the application.

**And what you're deliberately not:** IPv6, fragmentation and reassembly, selective acknowledgement, path MTU discovery, or performance. **This is the guide that closes the hole under every other network project in this folder.** [[build-your-own-shit/01-http-server|Guide 01]] starts at `accept()` and treats everything below the socket as given. This one builds what it was standing on.

## What you need first

- **The layer model, and what each layer actually adds** → [[networking/01-what-a-network-is|what a network is]]
- **Ethernet frames and MAC addresses** → [[networking/02-the-link-layer|the link layer]]
- **IP addressing and how a packet is routed** → [[networking/03-ip-addressing-and-subnetting|IP addressing]] · [[networking/04-routing|routing]]
- **The TCP connection lifecycle** — the state machine is the hard part of this project, so read it before you start → [[networking/06-tcp-connection-lifecycle|connection lifecycle]] · [[networking/07-tcp-reliability-and-flow-control|reliability and flow control]]
- **A language with byte-level control** and comfort with bitfields and byte order → [[languages/04-c/index|C]]
- Helpful: [[networking/16-debugging-networks|debugging networks]], because **Wireshark is the debugger for this entire project**

**C is the canonical choice** — the headers are byte layouts and C lets you say so. **Go and Rust are both excellent** here and save you a category of memory bug. **Python works** and teaches the same lessons via `struct.unpack`; it will be slow and it will not matter.

**You need `CAP_NET_ADMIN`** to create the interface, so this runs under `sudo` or with the capability granted to the binary.

## The build order

**1. Get a virtual network interface.**
Open `/dev/net/tun` and `ioctl(TUNSETIFF)` it into existence. **TAP gives you Ethernet frames, TUN gives you bare IP packets.** Start with **TAP** — the extra layer is where ARP lives, and ARP is worth building.

```bash
# on the host side, once your program has created tap0
sudo ip addr add 10.0.0.1/24 dev tap0
sudo ip link set tap0 up
```
Your stack owns `10.0.0.4` on that subnet; the kernel owns `10.0.0.1`.
*Works when:* a `read()` on the file descriptor returns bytes when you `ping 10.0.0.4`, even though nothing answers yet.

**2. Parse Ethernet frames.**
Destination MAC, source MAC, ethertype, payload. Two ethertypes matter: `0x0806` (ARP) and `0x0800` (IPv4).
*Works when:* you can print the ethertype of every inbound frame and they are all ARP at this point — because **nothing can send you IP until it knows your MAC address.**

**3. ARP, and become visible.**
Answer "who has 10.0.0.4, tell 10.0.0.1" with your own made-up MAC address. Keep a small translation table of the replies you receive.
*Works when:* `ip neigh show dev tap0` on the host lists `10.0.0.4` with your MAC. **You now exist on the network**, and IPv4 packets start arriving.

**4. Parse IPv4, and validate the checksum.**
Version and header length, total length, TTL, protocol, source and destination. The header checksum is a **one's complement sum of the header as 16-bit words, with the carries folded back in, then inverted.**

```c
uint16_t checksum(void *data, int len) {
    uint32_t sum = 0;
    uint16_t *p = data;
    for (; len > 1; len -= 2) sum += *p++;
    if (len == 1) sum += *(uint8_t *)p;
    while (sum >> 16) sum = (sum & 0xFFFF) + (sum >> 16);  /* fold carries */
    return ~sum;
}
```
*Works when:* the checksum over a received header, **including its own checksum field**, comes out to zero. That property is the whole trick, and it is the fastest way to know your byte order is right.

**5. ICMP echo — answer a ping.**
Swap source and destination, change type 8 to type 0, recompute both checksums, send it back.
*Works when:* **`ping 10.0.0.4` prints replies.** This is the first real moment in the project: a program you did not write, using the kernel's stack, is having a conversation with yours.

**6. UDP, because it is TCP without the hard part.**
Ports, length, and a checksum computed over a **pseudo-header** — source IP, destination IP, a zero byte, the protocol number and the UDP length — prepended to the datagram but never transmitted.
*Works when:* `nc -u 10.0.0.4 7` gets back whatever you type, via an echo service you wrote in twenty lines.

**7. The TCP handshake.**
Now the real work. Implement `LISTEN` → `SYN_RECEIVED` → `ESTABLISHED`: on a SYN, pick a **random initial sequence number**, reply SYN-ACK with `ack = their_seq + 1`, and move on when their ACK arrives.
*Works when:* `nc 10.0.0.4 8080` connects and stays connected, and `tcpdump -i tap0` shows the three packets in order. **Get this working before touching anything else** — every later bug is easier to find from a connection that establishes cleanly.

**8. Data transfer.**
A receive buffer, a send buffer, sequence and acknowledgement numbers that advance by bytes, and a window you advertise. Accept in-order segments, acknowledge them, and buffer out-of-order ones instead of dropping them.
*Works when:* you echo back everything typed into `nc`, including a paste large enough to arrive as several segments.

**9. Teardown.**
FIN, ACK, FIN, ACK, and the `TIME_WAIT` state that keeps the connection tuple reserved afterwards.
*Works when:* `nc` exits cleanly at both ends and `tcpdump` shows no stray RST. **Then read your own `TIME_WAIT` code and you will finally understand why a restarted server says "address already in use".**

**10. Retransmission — where TCP earns its reputation.**
Keep unacknowledged segments in a queue with a timer. When the timer fires, resend. Estimate the timeout from measured round-trip times rather than fixing it:

```
SRTT   = (1 - 1/8) * SRTT   + (1/8) * measured_rtt
RTTVAR = (1 - 1/4) * RTTVAR + (1/4) * |SRTT - measured_rtt|
RTO    = SRTT + 4 * RTTVAR        (and never below 1 second)
```
*Works when:* your connection still transfers a file correctly under `sudo tc qdisc add dev tap0 root netem loss 10%`. **Deliberately breaking the network is the only way to test this**, and it is the most satisfying test in the guide.

**11. Flow control, then congestion control.**
Flow control is the receive window you already advertise — shrink it when your buffer fills and the sender must stop. Congestion control is separate and inferred: **slow start** doubles the congestion window each round trip, **congestion avoidance** adds one segment per round trip after the threshold, and three duplicate acknowledgements trigger a fast retransmit.
*Works when:* under `netem` with loss, a graph of your congestion window over time shows the sawtooth → [[networking/08-congestion-control|congestion control]].

**12. A socket API, and then guide 01 on top of it.**
Wrap the stack in `listen`/`accept`/`read`/`write`/`close` with the signatures you already know. Then port the HTTP server from [[build-your-own-shit/01-http-server|guide 01]] onto it by changing only the import.
*Works when:* **`curl http://10.0.0.4:8080/` prints your page.** Every byte of that transaction below the request line went through code you wrote.

## Per-language toolkit

| | What the standard library gives you | What you write |
|---|---|---|
| **C** | `ioctl`, `read`/`write`, `ntohs`/`htons` | everything else — the canonical choice |
| **Go** | `syscall`, `encoding/binary`, goroutines per connection | headers, state machine; the concurrency is nearly free |
| **Rust** | `libc`, `byteorder`; `smoltcp` as a reference to read | the same, with the compiler enforcing your buffer bounds |
| **Python** | `fcntl.ioctl`, `struct`, `os.read` | the same; ~10× less code and ~100× slower |

**Do not use a raw socket instead of TUN/TAP.** The kernel's stack will see the same packets and answer them first — you will get RSTs from a stack that is not yours, and spend an evening finding out why.

## The parts that will bite you

**Byte order, everywhere.** Network order is big-endian and your machine almost certainly is not. Every multi-byte field needs `ntohs`/`ntohl` on the way in and `htons`/`htonl` on the way out. **The symptom is a port number of 20480 instead of 80** — that is `htons(80)` read the wrong way round.

**The pseudo-header.** TCP and UDP checksums cover fields from the IP header that are not part of the segment. Forget it and everything looks fine in your own hex dumps while the kernel silently discards every packet you send.

**Sequence numbers wrap.** They are 32-bit and modular, so `if (a > b)` is wrong. Compare with signed subtraction — `(int32_t)(a - b) < 0` — which stays correct across the wrap.

**The state machine is larger than the diagram suggests.** Eleven states, and the transitions that bite are the simultaneous ones: a FIN arriving while you have unsent data, a RST at any moment, a SYN for a connection already in `TIME_WAIT`.

**Nagle's algorithm meets delayed acknowledgement.** Your sender waits for a full segment; their receiver waits before acknowledging. Neither is broken and together they add 40 ms to every small exchange. **Implement both, watch the latency appear, then implement `TCP_NODELAY`** — you will never again wonder what that flag is for.

**Zero-window deadlock.** You advertise a window of zero, the sender stops, your buffer drains, and your window update is lost. Without a persist timer, the connection is dead forever. This is a real specified problem with a real specified fix.

## How to know it works

1. **`ping` gets replies** — layers 2, 3 and ICMP are correct
2. **`tcpdump -i tap0 -X` is your debugger**, and Wireshark's *Analyse → Expert Information* tells you exactly which field is malformed. **Use it from step 2, not from step 8**
3. **`nc` connects, exchanges data, and disconnects cleanly** — no RSTs anywhere in the capture
4. **A file transfers byte-identically under 10% simulated loss** (`tc netem`) — this is the test that proves retransmission
5. **`curl` fetches a page** from guide 01's server running on your socket API
6. **The congestion window plotted over time shows the sawtooth**

## Where to stop

**Stop when `curl` works under packet loss.** You have then implemented the parts that carry the ideas.

**Not worth it here:** IPv6 (a second address family, the same TCP), fragmentation (largely deprecated in practice), selective acknowledgement and window scaling (real and important, but they are refinements of a mechanism you already built), and anything about throughput. **A stack that moves 2 MB/s taught you exactly as much as one that moves 2 GB/s.**

**You will have learned:** why a connection has states rather than just being open, what an acknowledgement actually acknowledges, why the 40 ms delay exists, what "reliable" costs, and why the socket API looks the way it does. **Afterwards [[networking/index|the whole networking course]] reads as documentation for something you have built**, and [[networking/13-quic-and-modern-transport|QUIC's]] design decisions read as a list of the things that annoyed you.

## Related

- [[networking/index|networking/]] — the reference course for every layer here
- [[build-your-own-shit/01-http-server|Your Own HTTP Server]] — the layer above, and the final test of this one
- [[networking/12-tls-and-transport-security|TLS]] — the next layer up, if you want to keep climbing
- [[build-your-own-shit/05-your-own-os|Your Own OS]] — where a stack like this would live in kernel space
- [[build-your-own-shit/index|Build Your Own Shit index]]

*Source: [reference] — build guide, Sep 2026.*
