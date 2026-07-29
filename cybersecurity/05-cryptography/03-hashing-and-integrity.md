# Hashing & Integrity

A hash function takes input of any size and produces a fixed-size output (a "digest"), deterministically — the same input always produces the same hash — but with **no way to reverse it** back to the original input. This one-way property is what makes hashing useful for integrity checking and, in a specifically hardened form, password storage (see [[02-secure-authentication|secure-authentication]]) — but general-purpose hashing and password hashing solve different problems and use deliberately different kinds of algorithms, covered below.

## The properties a cryptographic hash function needs

- **Deterministic** — the same input always produces the same output.
- **One-way (preimage resistance)** — given a hash output, it's computationally infeasible to find *any* input that produces it.
- **Collision resistant** — computationally infeasible to find two *different* inputs that produce the same hash output.
- **Avalanche effect** — changing even one bit of the input produces a wildly different, unrelated-looking output — this is what makes hashing useful for tamper detection, since even a trivial modification is immediately obvious.

```python
import hashlib
hashlib.sha256(b"hello world").hexdigest()
# 'b94d27b9934d3e08a52e52d7da7dacefe...'

hashlib.sha256(b"hello worle").hexdigest()   # one character changed
# '...completely different output, no resemblance to the above'
```

## SHA-256 vs the broken algorithms you'll still see referenced

**SHA-256** (part of the SHA-2 family) is the current, widely trusted standard for general-purpose hashing. **MD5** and **SHA-1** are both considered cryptographically broken — practical collision attacks exist for both (two different inputs producing the same hash has been demonstrated for real, not just theorized), which means they should not be used anywhere collision resistance matters. They still show up constantly in older systems, non-security contexts (like a quick checksum for detecting accidental corruption, where an attacker deliberately engineering a collision isn't a realistic threat), and legacy documentation — worth recognizing by name specifically so you know to flag them when you see them used for anything security-relevant.

## What hashing is actually used for

- **Integrity verification** — publishing a file's SHA-256 hash alongside a download lets anyone verify the file wasn't corrupted or tampered with in transit, by hashing what they received and comparing.
- **Password storage** — never with a plain general-purpose hash like SHA-256 alone (fast hashing makes offline cracking cheap, see [[08-common-tools|Hashcat/John the Ripper]]) — always with a deliberately slow, memory-hard algorithm (bcrypt, Argon2), covered in depth in [[02-secure-authentication|secure-authentication]]. This is the single most important distinction in this note: **general-purpose hashing is designed to be fast; password hashing is deliberately designed to be slow**, and using the wrong one for the wrong job is a serious, common mistake.
- **Data structures** (outside security entirely) — hash tables/dictionaries use non-cryptographic hash functions for fast lookup, a completely different use case with completely different requirements (speed matters, adversarial collision resistance generally doesn't) — see [[03-hash-maps|hash-maps]] in the DSA notes for that side of hashing.

## HMAC — hashing combined with a secret key

A plain hash proves data hasn't changed, but anyone can compute a hash — it doesn't prove data came from a specific, trusted sender. **HMAC (Hash-based Message Authentication Code)** combines a hash function with a secret key, so only someone who knows the key can produce a valid HMAC for a given message — this gets you both integrity *and* authentication in one primitive (mapping directly onto the goals framework in [[01-what-is-cryptography|what-is-cryptography]]).

```python
import hmac, hashlib
secret_key = b"shared-secret"
message = b"transfer $100 to account X"
signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
# the recipient, holding the same secret_key, recomputes this and compares — 
# a mismatch means either the message changed or it wasn't from someone who knows the key
```

This is exactly the mechanism behind verifying that a JWT (see [[02-secure-authentication|secure-authentication]]) or a webhook payload genuinely came from the expected source and wasn't tampered with in transit.

## Gotchas

- Comparing hashes/HMACs with a plain `==` in some languages can be vulnerable to **timing attacks** — the comparison can return faster on an early mismatch than a late one, leaking information about how many leading bytes were correct. Constant-time comparison functions (`hmac.compare_digest` in Python) exist specifically to close this gap.
- Using MD5 or SHA-1 for anything where an adversary might deliberately engineer a collision (digital signatures, security tokens) is a real, exploitable weakness today, not a theoretical one — SHA-256 or better should be the default for any new security-relevant use.
- Hashing a password directly with SHA-256 (no salt, no deliberate slowness) is a common and serious real-world mistake — see [[02-secure-authentication|secure-authentication]] for the actual correct approach.

## Related
- [[01-what-is-cryptography|what-is-cryptography]]
- [[05-digital-signatures-and-pki|digital-signatures-and-pki]]
- [[02-secure-authentication|secure-authentication]]
