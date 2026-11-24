# Cryptography

**Cryptography is using maths to keep data secret, detect any change to it, and prove who sent it, even when an attacker sees everything you send.**

By this point in the course you've used cryptography everywhere without stopping to look at it: the WireGuard tunnel, the HTTPS certificate, bcrypt, the HMAC on a webhook, the signature on a JWT. This section opens each one up. Every lesson has something to run on your laptop, and the numbers in the worked examples are small enough to check by hand.

## What you'll be able to do

By the end of this section you will be able to:

- tell encoding, encryption and hashing apart, and match any tool to the goal it serves;
- encrypt with AES-GCM, and show why ECB leaks and why a nonce must never repeat;
- verify downloads with SHA-256 and webhooks with HMAC;
- run RSA and Diffie–Hellman by hand, then build hybrid encryption with X25519 and AES-GCM;
- sign and verify with Ed25519, and run your own small certificate authority with openssl;
- find the real-world crypto mistakes (weak keys, predictable randomness, leaked secrets) and fix them.

## Reading order

1. [[cybersecurity/05-cryptography/01-what-is-cryptography|01 — What Is Cryptography]] — **[Beginner]** — the four goals, the two families, Kerckhoffs's principle, and encoding versus encryption versus hashing (decode a real JWT).
2. [[cybersecurity/05-cryptography/02-symmetric-encryption|02 — Symmetric Encryption]] — **[Intermediate]** — AES, modes, why ECB leaks, AES-GCM and its tamper check, nonces and keys from passwords.
3. [[cybersecurity/05-cryptography/03-hashing-and-integrity|03 — Hashing and Integrity]] — **[Intermediate]** — hash properties, broken hashes, verifying downloads, and HMAC on a webhook.
4. [[cybersecurity/05-cryptography/04-asymmetric-encryption|04 — Asymmetric Encryption]] — **[Advanced]** — trapdoors, RSA and Diffie–Hellman by hand, elliptic curves, forward secrecy and hybrid encryption.
5. [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|05 — Digital Signatures and PKI]] — **[Advanced]** — signing and verifying, certificates and the chain of trust, and a CA of your own.
6. [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|06 — Cryptographic Attacks and Best Practices]] — **[Advanced]** — brute force, padding oracles, side channels, bad randomness, key management, and the checklist.

## Related

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[mathematics/02-discrete-math/08-number-theory-and-modular-arithmetic|Number theory]] — the maths under RSA and Diffie–Hellman.
- [[theory-of-computation/08-beyond-p-vs-np|Beyond P vs NP]] — why cryptographic hardness is assumed rather than proven, and what quantum computing changes.
- [[cybersecurity/04-web-security/index|Web security]] and [[cybersecurity/03-network-security/index|network security]] — this section's tools, applied.

## About this section

**How it's built:** one map lesson, four tool lessons (symmetric, hashing, asymmetric, signatures) and one lesson on how the tools are misused, each with a Python or openssl lab and small worked numbers that are checked in code. The labs tie back to what the earlier sections built: WireGuard's X25519 keys, the VPS's certificate chain, bcrypt, webhooks. Rebuilt to the [[COURSE-STANDARD|course standard]]: all six lessons converted. Live runs are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
