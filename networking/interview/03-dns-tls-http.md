# Networking Interview — DNS, TLS & HTTP

From [[foundations/networking/10-dns-in-depth|10-dns-in-depth]], [[foundations/networking/11-http-evolution|11-http-evolution]], [[foundations/networking/12-tls-and-transport-security|12-tls-and-transport-security]], [[foundations/networking/13-quic-and-modern-transport|13-quic-and-modern-transport]].

---

### Q1. [Beginner→Intermediate] 🔥 Explain DNS resolution. What's the difference between recursive and iterative?

**Strong answer covers:** stub resolver (your OS) → recursive resolver (ISP, 8.8.8.8, 1.1.1.1) → root → TLD → authoritative, with caching at every layer.

**Recursive** = "go find the answer, I'll wait" — what your machine asks its resolver. **Iterative** = "tell me what you know and I'll follow up" — what the resolver does to each server in the chain. Root and TLD servers answer *only* iteratively, because doing recursion for the whole world would melt them.

**Detail worth adding:** the 13 root server *names* are a limit from fitting in a 512-byte UDP response, not a count of machines — there are 1000+ instances reachable via **anycast**.

---

### Q2. [Intermediate] 🔥 You changed a DNS record and some users still hit the old server. Why, and what should you have done?

**Strong answer covers:** **TTL.** Resolvers cache for the TTL and will not re-ask, no matter what you do. **You cannot revoke a DNS answer** — once it's out, it's out until it expires. Caching also happens at multiple independent layers (browser, OS, resolver), some of which clamp TTLs to their own minimums.

**What you should have done:** lower the TTL to ~60s **a day or two before** the migration — long enough for the *old, long* TTL to expire everywhere first — then migrate, then raise it back. Doing it in the wrong order is exactly this outage.

**Bonus that impresses:** **negative caching** is real too. An `NXDOMAIN` is cached per the SOA minimum, so if someone looked up a record before you created it, they'll keep failing for a while. That's the "works for me, not for my colleague" case right after setup.

---

### Q3. [Intermediate] Why does DNS cause so many outages?

**Strong answer covers:** it's a dependency of everything, cached invisibly, and rarely monitored. Specific mechanisms: it's the **first thing in every request path** so a slow resolver taxes every connection; **DNS-based load balancing is coarse** (cached everywhere, failover takes a full TTL — which is why real LB happens at L4/L7 with DNS just pointing at the balancer); and **it's a third-party single point of failure** — the 2016 Dyn DDoS took down Twitter, GitHub, Netflix and Reddit, none of which were attacked.

**Kubernetes-specific, if relevant:** `ndots:5` in the default `resolv.conf` means `api.example.com` (3 dots) is tried against every search domain first — several failed lookups before the real one. Combined with an older conntrack race, that produced the famous intermittent 5-second DNS timeouts. Fix: `ndots:2`, fully-qualified names with a trailing dot, or NodeLocal DNSCache.

---

### Q4. [Intermediate] 🔥 DNSSEC vs DNS-over-HTTPS — what does each actually give you?

**Strong answer covers:** they're **orthogonal**, and conflating them is the common mistake.
- **DNSSEC** = *authenticity and integrity*. Records are cryptographically signed with a chain of trust from the root, so you can verify the answer is genuine. **It does not encrypt anything** — anyone can still read your queries.
- **DoH/DoT** = *confidentiality*. Your queries are encrypted so the network can't read or tamper with them. **They do not authenticate the answer** — a lying resolver still lies, now privately.

You want both.

**Detail worth adding:** DNSSEC adoption is limited because it's operationally unforgiving — a botched key rollover removes your domain from the internet entirely. And DoH is contentious for a non-technical reason: it centralises resolution onto a few large providers and bypasses network-level filtering that enterprises and parental controls depended on.

---

### Q5. [Intermediate] 🔥 What problems does TLS solve, and in what order of importance?

**Strong answer covers:** three guarantees — **confidentiality** (symmetric encryption), **integrity** (AEAD), and **authentication** (X.509 certs and the chain of trust).

**The ordering is the answer they want:** **authentication comes first**, because if you're talking to an impostor, encryption is worthless — you've encrypted your secret *to the attacker*. Most real TLS failures are authentication failures (expired cert, rogue CA, verification disabled, downgrade) rather than broken ciphers. The maths has held; the trust infrastructure around it is the soft part.

---

### Q6. [Advanced] 🔥 What is forward secrecy and why did TLS 1.3 make it mandatory?

**Strong answer covers:** with old **RSA key transport**, the client encrypted the session secret with the server's public key. If that private key is ever compromised, **every past recorded session can be decrypted** — enabling "harvest now, decrypt later," which is a real and funded strategy.

With **ephemeral Diffie-Hellman (ECDHE)**, both sides generate throwaway key pairs per connection and derive a shared secret that never crosses the wire and can't be reconstructed from a recording. The server's long-term key only **signs** the exchange to prove identity. So compromising it tomorrow reveals nothing about traffic recorded today.

TLS 1.3 removed every non-forward-secret key exchange. That's the most important thing it did.

---

### Q7. [Intermediate→Advanced] What else did TLS 1.3 change, and what's the general lesson?

**Strong answer covers:** one round trip instead of two (the client speculatively sends its key share in the ClientHello); the handshake including the certificate is now encrypted; **0-RTT resumption**; and a huge amount of **deletion** — RSA key transport, static DH, RC4, 3DES, MD5/SHA-1, CBC-mode ciphers, compression, and renegotiation are all gone. Cipher suites went from hundreds to five.

**The lesson, which is the real answer:** BEAST, CRIME, POODLE, FREAK, Logjam, Sweet32 — nearly every TLS vulnerability of the previous decade came from **optional legacy support and downgrade negotiation**, not from broken modern crypto. **Removing choices was the security fix.** That generalises well beyond TLS.

**The 0-RTT caveat to raise unprompted:** 0-RTT data is **replayable** by an attacker who captured it. Restrict it to idempotent requests — a `POST /transfer` in 0-RTT is a genuine vulnerability.

---

### Q8. [Intermediate] What does the padlock in the browser actually mean?

**Strong answer covers:** it means "the connection is encrypted and authenticated **to the domain you named**." It says nothing about whether that site is trustworthy. Phishing sites all have valid certificates — they're free.

**Also worth naming — what TLS does *not* protect:** traffic metadata (sizes, timing, destination IPs are all visible); anything after termination (TLS ending at your load balancer means plaintext behind it — which is what mTLS/service mesh exists to fix); and the endpoints themselves.

---

### Q9. [Intermediate] 🔥 What did HTTP/2 fix, and what couldn't it fix?

**Strong answer covers:** **fixed** — application-layer head-of-line blocking, via binary framing and true multiplexing of many streams over one connection; plus HPACK header compression (huge on cookie-heavy sites); plus it made the HTTP/1.1-era workarounds obsolete.

**Couldn't fix** — transport-layer head-of-line blocking, because it multiplexes over a single TCP connection and TCP enforces total ordering. One lost packet stalls every stream.

**The detail that shows depth:** name the obsolete workarounds and say they're now *harmful* — **domain sharding** (defeats multiplexing, multiplies DNS/TCP/TLS setup), **concatenation and spriting** (wreck caching granularity), **inlining** (defeats caching entirely), and browsers' 6-connections-per-origin. Auditing an old codebase for these is real, cheap performance work.

**Also worth knowing:** server push was **removed from Chrome in 2022** — it mostly pushed things clients already had cached. `103 Early Hints` is the surviving idea. A good example of a feature that's obviously right in theory and measurably wrong in deployment.

---

### Q10. [Advanced] 🔥 Why is QUIC built on UDP rather than as a new protocol, and what does it give you?

**Strong answer covers the four wins:**
1. **Real stream multiplexing** — per-stream delivery guarantees, so loss blocks only its own stream. The thing HTTP/2 couldn't have.
2. **Handshake collapse** — transport and crypto handshakes fused: 1 RTT new, 0 RTT resumed (vs 2 for TCP+TLS).
3. **Connection migration** — connections are identified by a **connection ID**, not the 4-tuple, so switching Wi-Fi → mobile doesn't kill the connection. Impossible to retrofit into TCP.
4. **Escaping ossification** — the real answer.

**On "why UDP":** because you **cannot deploy a new IP protocol number** on today's internet — middleboxes drop what they don't recognise. TCP Fast Open was standardised in 2014 and still isn't reliably usable for exactly this reason. UDP is one of the two things guaranteed to pass everywhere. And building in **userspace** means QUIC ships in a browser release rather than waiting a decade for kernel and middlebox deployment.

**The point that lands hardest:** QUIC **encrypts nearly the entire packet including most of the header** — not only for privacy, but so middleboxes physically *cannot* parse it and therefore cannot ossify it. The protocol hides from the network to preserve its own ability to evolve. That's Hyrum's Law at internet scale, and the generalisation — *an interface others can observe becomes impossible to change* — is worth stating.

**The honest costs, if asked:** higher CPU (userspace + per-packet crypto, less hardware offload), some networks throttle UDP so you need a TCP fallback, and it's opaque to your existing tcpdump/IDS tooling (debug with qlog instead).

---

### Q11. [Intermediate] Which HTTP methods can be safely retried automatically, and why does it matter?

**Strong answer covers:** **safe** (no side effects): `GET`, `HEAD`. **Idempotent** (repeating is harmless): `GET`, `HEAD`, `PUT`, `DELETE`. **Neither:** `POST`, `PATCH`.

**Why it matters:** it determines what clients, proxies, and load balancers may retry on their own. A retried `POST` after a timeout can double-charge a customer — the network failed *after* the server processed it, and the client can't tell the difference. That's why payment APIs require **idempotency keys**: the client supplies a unique key so the server can recognise and deduplicate the retry.

**Connect it upward:** this is the same "did it fail before or after the effect?" ambiguity as in distributed systems — you can't distinguish a lost request from a lost response, so exactly-once delivery is impossible and you build idempotent receivers instead.
