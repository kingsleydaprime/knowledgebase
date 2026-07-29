# What is Cryptography

Cryptography is the mathematical foundation almost every other security control in this vault ultimately rests on — [[02-cia-triad|the CIA triad]]'s confidentiality and integrity, [[03-https-and-tls|TLS]], [[02-secure-authentication|password hashing]], all of it is cryptography applied to a specific problem. This folder is that foundation on its own terms.

## The four goals cryptography actually provides

- **Confidentiality** — only authorized parties can read the data (encryption).
- **Integrity** — any tampering with the data is detectable (hashing, MACs).
- **Authentication** — you can verify who actually sent something, or that a server is who it claims to be (digital signatures, certificates).
- **Non-repudiation** — the sender can't credibly deny having sent something, since only they could have produced a valid signature for it (digital signatures specifically — plain encryption/hashing don't provide this on their own).

Every technique in this folder maps to at least one of these four goals — a useful check when you're not sure why a given technique exists: ask which of the four it's actually providing.

## The two major branches

- **[[02-symmetric-encryption|Symmetric cryptography]]** — the same key encrypts and decrypts. Fast, but requires both parties to already share a secret key somehow.
- **[[04-asymmetric-encryption|Asymmetric (public-key) cryptography]]** — a mathematically linked key *pair*, where one key encrypts and only the other can decrypt. Slower, but solves the problem symmetric encryption can't: how do two parties who've never met establish a shared secret over an insecure channel in the first place?

In practice, real systems combine both — asymmetric cryptography to safely establish a shared secret, then symmetric encryption (much faster) for the actual bulk data, exactly as covered in [[04-asymmetric-encryption|asymmetric-encryption]]'s hybrid encryption section and already seen in [[03-https-and-tls|https-and-tls]]'s handshake.

## Kerckhoffs's principle — why "keep the algorithm secret" is not how this works

A cryptographic system should be secure even if everything about it *except the key* is public knowledge — the algorithm itself (AES, RSA) is published, peer-reviewed, and implemented in open-source libraries; only the key is secret. This is deliberate: an algorithm's security should never depend on attackers not knowing how it works, since that assumption fails the moment the algorithm leaks (or is reverse-engineered) — and a secret, unreviewed algorithm has had far less expert scrutiny than a public one that's survived years of attempted attacks by the entire cryptographic research community. This is the direct reason "don't roll your own crypto" (expanded in [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]]) is a near-universal piece of advice in this field.

## Encoding, encryption, and hashing — three things people conflate

- **Encoding** (Base64, URL encoding) — reformats data for compatibility, with **no secret key at all** — trivially reversible by anyone, and provides zero security. Common mistake: treating Base64 as if it were encryption.
- **Encryption** — transforms data using a secret key such that only someone with the right key can reverse it back to the original. Two-way by design.
- **Hashing** — transforms data into a fixed-size output with **no key and no way back**, one-way by design (see [[03-hashing-and-integrity|hashing-and-integrity]]). Used for integrity checks and password storage, never for anything that needs to be recovered later.

Confusing these three is a genuinely common beginner mistake — "I'll just Base64 it for security" is one of the most frequent, and most wrong, statements in this field.

## Gotchas

- Cryptography protects data *given that the implementation and key management are also correct* — a mathematically sound algorithm with a leaked key, a predictable random number generator, or a flawed implementation provides no real protection at all. Most real-world "crypto failures" are implementation/key-management failures, not the underlying math being broken.
- "Encrypted" alone doesn't specify *which* goal is being met — always ask which of the four goals above a specific control is actually providing, since encryption alone (confidentiality) says nothing about integrity or authentication unless paired with a MAC or signature.

## Related
- [[02-symmetric-encryption|symmetric-encryption]]
- [[04-asymmetric-encryption|asymmetric-encryption]]
- [[02-cia-triad|cia-triad]]
