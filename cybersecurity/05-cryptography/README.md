# Cryptography

The mathematical foundation underneath most of the rest of `cybersecurity/` — [[02-cia-triad|the CIA triad]], [[03-https-and-tls|TLS]], and [[02-secure-authentication|password storage]] are all specific applications of the ideas in this folder, not separate topics.

## Reading order
1. [[01-what-is-cryptography|what-is-cryptography]] — **[Beginner]** — the four goals (confidentiality, integrity, authentication, non-repudiation), symmetric vs asymmetric, Kerckhoffs's principle, and why encoding/encryption/hashing aren't the same thing
2. [[02-symmetric-encryption|symmetric-encryption]] — **[Intermediate]** — AES, block vs stream ciphers, modes of operation (why ECB is broken, GCM is the modern default), the key-exchange problem it can't solve
3. [[03-hashing-and-integrity|hashing-and-integrity]] — **[Intermediate]** — one-way functions, SHA-256 vs the broken MD5/SHA-1, HMAC, and why password hashing is a deliberately different algorithm family
4. [[04-asymmetric-encryption|asymmetric-encryption]] — **[Advanced]** — RSA, Diffie-Hellman, ECC, and hybrid encryption (how TLS actually uses both branches together)
5. [[05-digital-signatures-and-pki|digital-signatures-and-pki]] — **[Advanced]** — signing/verification, Certificate Authorities, the chain of trust, revocation
6. [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]] — **[Advanced]** — brute force, padding oracles, side channels, weak randomness, and why key management matters more than algorithm choice in practice

## Related
- [[cybersecurity/README|cybersecurity curriculum map]]
- [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|Number Theory]] — the maths under RSA and Diffie–Hellman, with RSA derived in eight lines
- [[foundations/theory-of-computation/08-beyond-p-vs-np|Beyond P vs NP]] — why cryptographic hardness is *conjectured*, and what quantum computing does to it
- [[cybersecurity/04-web-security/README|web-security]] — TLS and secure authentication as applied cryptography
- [[cybersecurity/03-network-security/README|network-security]] — VPNs and encryption in transit as applied cryptography
