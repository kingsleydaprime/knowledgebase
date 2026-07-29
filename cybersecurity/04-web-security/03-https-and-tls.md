# HTTPS & TLS

HTTPS is plain HTTP running over TLS (Transport Layer Security) — the protocol that encrypts a connection, verifies the identity of the server you're talking to, and detects tampering in transit. Without it, every request and response between a browser and a server travels in plaintext, readable and modifiable by anyone positioned on the network path between them.

## What TLS actually provides — the three properties, mapped to the CIA triad

- **Confidentiality** — the connection's contents are encrypted; an eavesdropper on the network sees only ciphertext, not the actual request/response data.
- **Integrity** — any tampering with the data in transit is detectable, so a man-in-the-middle can't silently modify a response (injecting malicious content into an otherwise legitimate page, for instance).
- **Authentication** — the server proves its identity via a certificate, so you can be reasonably confident you're actually talking to the real `example.com` and not an attacker impersonating it.

Directly mapping onto [[02-cia-triad|cia-triad]]'s vocabulary is a useful way to remember what TLS is protecting and, just as importantly, what it *isn't* (it says nothing about whether the server itself is trustworthy or secure once you're legitimately connected to it).

## The handshake, at a conceptual level

```
Client                                          Server
  |-- "Hello, here's what I support" ---------->|
  |<-- "Here's my certificate + chosen cipher" --|
  |-- (verify certificate against trusted CAs) --|
  |-- key exchange (establish a shared secret) ->|
  |<====== encrypted application data ==========>|
```

The client and server perform a key exchange to agree on a shared secret without ever transmitting that secret directly (modern TLS uses Diffie-Hellman-based key exchange, providing **forward secrecy** — even if a server's long-term private key is later compromised, past captured traffic still can't be decrypted, since each session's actual encryption key was unique and never stored).

## Certificates and the chain of trust

A certificate binds a public key to a domain name, signed by a **Certificate Authority (CA)** that your browser/OS already trusts. When you connect to a site, your browser checks that the certificate is validly signed by a trusted CA (or a chain leading to one), hasn't expired, and matches the domain you're actually visiting — this is what stops an attacker from simply presenting their own certificate for a domain they don't own. **Let's Encrypt** made free, automated certificate issuance the norm, which is a large part of why HTTPS became the default across the web rather than a paid, effort-intensive option.

```bash
# checking a site's certificate details from the command line
openssl s_client -connect example.com:443 -servername example.com < /dev/null 2>/dev/null | openssl x509 -noout -dates -issuer -subject
```

## HSTS — forcing HTTPS, and closing the downgrade gap

Without HSTS, a user typing `example.com` (no scheme) or clicking an old `http://` link connects over plain HTTP first, then gets redirected to HTTPS — a brief window an attacker positioned on the network (a malicious Wi-Fi hotspot, for instance) can exploit to intercept that first plaintext request. `Strict-Transport-Security` tells the browser to *only ever* connect over HTTPS for that domain going forward, skipping the vulnerable plaintext-first step entirely on every subsequent visit.

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

## Certificate/TLS misconfigurations worth knowing

- **Expired or self-signed certificates** — trigger browser warnings, and training users to click through those warnings routinely is itself a security risk (it erodes the signal for when a warning is genuinely important).
- **Weak/outdated cipher suites or TLS versions** (TLS 1.0/1.1, or older ciphers) — should be disabled server-side; modern configurations should support TLS 1.2 and 1.3 only.
- **Mixed content** — an HTTPS page loading some resources (scripts, images) over plain HTTP undermines the page's own security guarantees, since those specific resources are still interceptable/modifiable in transit.

## Gotchas

- TLS protects data **in transit** only — it says nothing about how securely data is stored once it reaches the server (see [[02-secure-authentication|secure-authentication]] for that side) or whether the application itself has vulnerabilities (see [[07-exploitation-concepts|exploitation-concepts]]).
- A valid certificate proves the server controls the domain — it does not prove the server is trustworthy, unhackable, or free of vulnerabilities; "the padlock icon" is frequently over-trusted as a general safety signal by end users for exactly this reason.
- Certificate expiration is a surprisingly common, entirely preventable outage cause — automated renewal (Let's Encrypt's standard workflow) largely eliminates this as a risk, and its absence is a real operational gap.

## Related
- [[02-cia-triad|cia-triad]]
- [[02-secure-authentication|secure-authentication]]
- [[04-security-headers-and-same-origin-policy|security-headers-and-same-origin-policy]]
- [[04-asymmetric-encryption|asymmetric-encryption]] — the Diffie-Hellman key exchange underneath the handshake above
- [[05-digital-signatures-and-pki|digital-signatures-and-pki]] — the certificate chain of trust, one level deeper
