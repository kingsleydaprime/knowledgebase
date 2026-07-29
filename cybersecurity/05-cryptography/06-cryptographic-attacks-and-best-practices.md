# Cryptographic Attacks & Best Practices

Almost every real-world "cryptography failure" isn't the underlying math being broken — AES and RSA, used correctly, remain unbroken by direct attack. It's an implementation mistake, a weak key, a protocol misuse, or a side channel. This note is the practical, defensive summary tying the rest of this folder together.

## Brute force — the baseline every algorithm is measured against

Trying every possible key until one works. Modern algorithms with adequate key lengths (AES-256, RSA-2048+, see [[02-symmetric-encryption|symmetric-encryption]] and [[04-asymmetric-encryption|asymmetric-encryption]]) make brute force computationally infeasible with any current or foreseeable hardware — the key space is simply too large. Brute force becomes practical again the moment the *effective* key space is smaller than it looks — a weak, human-chosen password (see [[02-secure-authentication|secure-authentication]] and [[08-common-tools|Hashcat/John the Ripper]]) is the most common real-world example, since the actual search space is "plausible passwords," not "every possible key."

## Padding oracle attacks — a protocol-level mistake, not a cipher weakness

If a system decrypts CBC-mode ciphertext (see [[02-symmetric-encryption|symmetric-encryption]]) and reveals — even indirectly, through a different error message or a timing difference — whether the padding was valid, an attacker can exploit that leak to decrypt data byte by byte without ever knowing the key, through repeated, carefully crafted queries. This is a genuinely famous, real-world category of vulnerability (several major TLS-related incidents trace back to exactly this pattern) — the fix is ensuring padding validation errors are indistinguishable from other decryption errors, or better, using an authenticated mode like GCM that doesn't have this failure mode at all.

## Side-channel attacks — extracting secrets without breaking the math

Some attacks don't touch the cryptographic algorithm's logic at all — they measure something incidental about its *physical execution*: how long an operation takes (timing attacks, mentioned in [[03-hashing-and-integrity|hashing-and-integrity]] for hash comparison specifically), how much power a chip draws, or even sound/electromagnetic emissions during a cryptographic operation. These can leak key material even when the algorithm itself is mathematically sound, because the attack targets the implementation's physical behavior rather than the math — which is why cryptographic libraries specifically implement constant-time operations for anything handling secret data, deliberately sacrificing a little performance to close this gap.

## Weak random number generation — undermining everything downstream

Keys, IVs, nonces, and salts all depend on genuinely unpredictable randomness. A **cryptographically secure pseudorandom number generator (CSPRNG)** is required — a predictable or low-entropy source (a poorly seeded standard `random()` function, or a known historical case of an embedded system seeding its RNG from too little available entropy at boot) can make keys guessable despite a mathematically perfect algorithm sitting on top of them. This is a structural way "the crypto is broken" actually means "the randomness feeding the crypto was broken."

```python
import secrets          # Python's CSPRNG-backed module, correct for security purposes
import random           # NOT cryptographically secure — fine for games/simulations, wrong for keys

secure_token = secrets.token_bytes(32)     # correct
insecure_token = random.getrandbits(256)   # wrong — predictable given enough observed output
```

## Why "don't roll your own crypto" is near-universal advice

Implementing cryptographic primitives correctly requires avoiding an enormous number of subtle mistakes (timing side-channels, incorrect padding, IV reuse, insufficient randomness) that even experienced engineers get wrong — established libraries (implementing algorithms per Kerckhoffs's principle from [[01-what-is-cryptography|what-is-cryptography]]) have had years of expert scrutiny, security audits, and real-world attack attempts already thrown at them. This applies at two levels: don't invent your own novel algorithm, and — just as important, and far more commonly relevant — don't reimplement a standard algorithm's protocol logic (padding, mode handling, key derivation) yourself when a maintained library already does it correctly.

## Key management — the unglamorous part that matters most

- **Generation** — always via a CSPRNG, never a predictable or hand-chosen source.
- **Storage** — secrets should live in a dedicated secrets manager or hardware security module (HSM), never hardcoded in source code or committed to version control.
- **Rotation** — periodically replacing keys limits how much data a single compromised key can expose.
- **Destruction** — securely deleting keys that are no longer needed, so old, retired keys can't later resurface as a liability.

A perfectly implemented algorithm with a hardcoded, never-rotated key checked into a public repository provides essentially no real security — key management failures are consistently among the most common root causes behind real breaches involving cryptography.

## A practical checklist

- Use established libraries, never hand-rolled algorithm implementations.
- Use authenticated encryption (AES-GCM) over unauthenticated modes where possible.
- Use a CSPRNG for anything security-relevant — never a general-purpose random function.
- Use current, unbroken algorithms (AES, SHA-256+, RSA-2048+/ECC) — actively avoid MD5, SHA-1, DES, and ECB mode for security-relevant purposes.
- Treat key management (generation, storage, rotation) as at least as important as algorithm choice.

## Related
- [[01-what-is-cryptography|what-is-cryptography]]
- [[02-symmetric-encryption|symmetric-encryption]]
- [[02-secure-authentication|secure-authentication]]
