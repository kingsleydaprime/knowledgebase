# TLS & Transport Security

**[Intermediate→Advanced]** — how two machines that have never met establish a private, authenticated channel across a network run by strangers. This note is about the *protocol*; the underlying maths lives in [[cybersecurity/05-cryptography/README|cryptography]].

## The kid version first

You want to send a secret to a shop you've never visited, over a postal system where anyone can read and rewrite your letters. Three problems, in strict order of importance:

1. **Is this actually the shop?** If you're talking to an impostor, encryption is worthless — you've encrypted your secret *to the attacker*. **Authentication comes first.**
2. **How do we agree on a shared secret code** when everything we say is public? (This looks impossible. It isn't — that's Diffie-Hellman.)
3. **How do I know my letter wasn't altered** in transit? (Integrity.)

TLS solves all three in one handshake. The order matters: most TLS mistakes in the wild are getting step 1 wrong while doing steps 2 and 3 perfectly — which is exactly what "certificate verification disabled" means, and why it's so much worse than it sounds.

## The three guarantees

| Guarantee | Mechanism | If you skip it |
|---|---|---|
| **Confidentiality** | symmetric encryption (AES-GCM, ChaCha20-Poly1305) | anyone on the path reads everything |
| **Integrity** | AEAD — authenticated encryption | anyone on the path silently *modifies* everything |
| **Authentication** | X.509 certificates + a chain of trust | you have a perfectly secure channel to an attacker |

## The key exchange problem, and why forward secrecy matters

Symmetric encryption is fast but needs a shared key. Getting that key to a stranger over a public channel is the founding problem of modern cryptography.

**The old way (RSA key transport, removed in TLS 1.3):** the client picks a secret, encrypts it with the server's public key, sends it. Works — but has a fatal property: **if the server's private key is ever compromised, every past recorded session can be decrypted.** An adversary can record traffic today and decrypt it years later when they eventually obtain the key. "Harvest now, decrypt later" is a real, funded strategy.

**The modern way (ephemeral Diffie-Hellman, ECDHE):** both sides generate a *throwaway* key pair per connection, exchange public halves, and each derives the same shared secret — which never crosses the wire and cannot be reconstructed from the recorded conversation. The server's long-term key is used only to **sign** the exchange (proving identity), never to encrypt the secret.

This gives **forward secrecy**: compromising the server's private key tomorrow reveals nothing about sessions recorded today, because the ephemeral keys were discarded. TLS 1.3 makes this **mandatory** — it removed every non-forward-secret key exchange. That's the single most important thing TLS 1.3 did.

## Certificates and the chain of trust

A certificate binds a **name** to a **public key**, signed by a **Certificate Authority**. Verification walks a chain:

```
example.com's cert  ──signed by──►  intermediate CA  ──signed by──►  root CA
                                                                      │
                                              already in your OS/browser trust store
```

The root's public key ships with your operating system — that's the anchor, and it's a *trust decision made for you* by your OS vendor. Roots are kept offline; intermediates do the day-to-day signing, so a compromised intermediate can be revoked without invalidating everything.

What the client actually checks, in order — and each is a real-world failure mode:

1. **Signature chain** validates to a trusted root.
2. **Not expired.** The single most common outage cause in this entire note. Automate renewal ([[devops/06-ci-cd/README|certbot / cert-manager]]) or you *will* be paged at 3am about it.
3. **Name matches** — the `Subject Alternative Name` must cover the hostname. (Common Name has been deprecated for this since 2017; browsers ignore it entirely.)
4. **Not revoked.** The weakest link. CRLs are huge and stale; **OCSP** requires an online check that leaks browsing to the CA and fails open (soft-fail) — an attacker who can MITM can also block the OCSP query. **OCSP stapling** improves this by having the *server* fetch and attach a signed freshness proof. Chrome largely abandoned OCSP for CRLSets; the industry's real answer has become **short-lived certificates** — a 90-day (soon 47-day) cert that expires before revocation would have mattered.

**Certificate Transparency** is the systemic fix for misissuance: every cert must be logged to public append-only logs, so a domain owner can detect a CA issuing certs for their domain. **CAA records** ([[foundations/networking/10-dns-in-depth|DNS]]) let you declare which CAs may issue for you at all. Both are cheap and worth setting.

## The handshake, and what TLS 1.3 changed

**TLS 1.2:** two round trips before application data. **TLS 1.3: one.** The client guesses which key-exchange group the server will pick and sends its key share in the *first* message, so the server can reply with everything needed.

```
TLS 1.2:  ClientHello → ServerHello/Cert → KeyExchange → Finished → DATA   (2 RTT)
TLS 1.3:  ClientHello+KeyShare → ServerHello+Cert+Finished → DATA          (1 RTT)
```

On a 100ms path stacked on top of a TCP handshake, that saved round trip is a visible improvement. TLS 1.3 also:

- **Deleted the dangerous options.** RSA key transport, static DH, RC4, 3DES, MD5/SHA-1, CBC-mode ciphers, compression (which enabled CRIME), and renegotiation are all gone. The cipher suite list went from hundreds to five. **This is the real lesson of TLS 1.3: most TLS vulnerabilities of the previous decade (BEAST, CRIME, POODLE, FREAK, Logjam, Sweet32) were caused by *optional legacy support and downgrade negotiation*, not by broken modern crypto.** Removing choices was the security fix.
- **Encrypts more of the handshake**, including the certificate.
- **0-RTT resumption** — send application data in the very first packet on a resumed connection. Free speed, with a genuine catch: 0-RTT data is **replayable** by an attacker who captured it. Only use it for idempotent requests. Sending a `POST /transfer` in 0-RTT is a real vulnerability, which is why servers should restrict 0-RTT to safe methods.

**SNI** (Server Name Indication) lets one IP host many TLS sites by sending the hostname in the ClientHello — necessary, but it's sent in the clear, so it leaks which site you're visiting even though the traffic is encrypted. **ECH** (Encrypted Client Hello) fixes this and is rolling out now. **ALPN** is the same-handshake mechanism that negotiates HTTP/1.1 vs h2 vs h3 without an extra round trip.

## mTLS, and what TLS does *not* give you

**Mutual TLS** has the *client* also present a certificate, so both sides are authenticated cryptographically rather than by a bearer token. This is the backbone of [[architecture/03-architectural-patterns/04-microservices-patterns|service mesh]] identity and zero-trust networking: services prove who they are with a key they hold, rather than a secret they could leak.

Things TLS explicitly does not protect:

- **Traffic metadata.** Sizes, timing, and destination IPs are all visible. Encrypted traffic still leaks a lot to analysis.
- **Anything after termination.** TLS terminated at your load balancer means plaintext behind it — which is fine if that network is trusted, and is exactly what mTLS/service mesh exists to stop assuming.
- **The endpoints.** A compromised server serves malware over a perfect TLS connection. **The padlock means "encrypted to the site you named," never "this site is trustworthy"** — the most widely misunderstood point in web security, and the reason phishing sites all have valid certificates now.

## Key insight

TLS's hardest problem was never encryption — it's **authentication**, and TLS doesn't actually solve it so much as *delegate* it to a global network of certificate authorities that you implicitly trust because your OS vendor does. Every serious TLS incident of the last fifteen years has been an authentication or negotiation failure (a rogue CA, a stripped connection, a downgrade to weak legacy crypto, an expired cert), not a broken cipher. The maths has held. The trust infrastructure around it is the soft part.

## Related
- [[cybersecurity/05-cryptography/README|Cryptography]] — the primitives underneath
- [[foundations/networking/13-quic-and-modern-transport|QUIC]] — TLS 1.3 fused into the transport itself
- [[foundations/networking/11-http-evolution|HTTP Evolution]] — ALPN, and why h2 requires TLS in practice
- [[cybersecurity/03-network-security/03-vpns-and-encryption-in-transit|Encryption in Transit]] — the operator's view
