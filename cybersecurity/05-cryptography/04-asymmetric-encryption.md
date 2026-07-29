# Asymmetric (Public-Key) Encryption

Where [[02-symmetric-encryption|symmetric-encryption]] uses one shared key, asymmetric cryptography uses a mathematically linked **key pair**: a **public key** anyone can have, and a **private key** only the owner ever holds. Data encrypted with the public key can only be decrypted with the matching private key — which solves the exact problem symmetric encryption can't: establishing protected communication between two parties who've never met and share no secret in advance.

## Why this is possible at all — one-way math

Asymmetric cryptography relies on mathematical problems that are easy to compute in one direction and computationally infeasible to reverse without a specific piece of extra information (the private key) — a **trapdoor function**. RSA relies on the difficulty of factoring the product of two large prime numbers; elliptic curve cryptography relies on a different hard problem (the discrete logarithm problem over elliptic curves). Multiplying two large primes together is trivial; recovering the original two primes from just their product is, for large enough primes, computationally impractical with any known method — that asymmetry is the entire security foundation.

## RSA — the classic example

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

ciphertext = public_key.encrypt(
    b"secret message",
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)
# only the matching private_key can decrypt this:
plaintext = private_key.decrypt(ciphertext, padding.OAEP(...))
```

RSA key sizes are much larger than AES key sizes for comparable security (2048-4096 bits vs AES's 128-256) — a direct consequence of the underlying math being a different, more structured kind of hard problem than symmetric ciphers rely on, which is also part of why RSA is significantly slower.

## Elliptic Curve Cryptography (ECC) — smaller keys, same security level

ECC achieves equivalent security to RSA with much shorter keys (a 256-bit ECC key is roughly comparable in strength to a 3072-bit RSA key), because its underlying hard problem scales more favorably. This is why ECC (commonly **ECDSA** for signatures, **ECDH** for key exchange) has become the modern default in places like TLS and cryptocurrency systems — smaller keys mean faster computation and less data to transmit, with no security tradeoff.

## Diffie-Hellman — key exchange without ever transmitting the key

Diffie-Hellman (DH, or its elliptic-curve variant ECDH) lets two parties independently compute the *same* shared secret over a public channel, without ever transmitting that secret directly — each side combines their own private value with the other's public value, and the underlying math guarantees both sides land on the same result, while an eavesdropper who only sees the public values can't feasibly compute it.

```
Alice: private a, public A = g^a mod p  ----->  sends A to Bob
Bob:   private b, public B = g^b mod p  ----->  sends B to Alice

Alice computes: B^a mod p = g^(ba) mod p
Bob computes:   A^b mod p = g^(ab) mod p
-> both arrive at the same shared secret, g^(ab) mod p, without either exposing a or b
```

This is exactly the mechanism underneath the key-exchange step of a [[03-https-and-tls|TLS handshake]] — and using an ephemeral (freshly generated per session) DH exchange specifically is what provides the **forward secrecy** mentioned in that note: even a stolen long-term private key later doesn't let an attacker retroactively decrypt already-captured past sessions, since each session's actual shared secret was unique and never stored anywhere.

## Hybrid encryption — why real systems use both branches together

Asymmetric encryption is orders of magnitude slower than symmetric encryption for bulk data. Real protocols use asymmetric methods only to solve the key-establishment problem, then switch to fast symmetric encryption (see [[02-symmetric-encryption|symmetric-encryption]]) for the actual data:

```
1. Use asymmetric crypto (RSA or, more commonly today, ECDH) to establish a shared secret
2. Derive a symmetric (AES) key from that shared secret
3. Encrypt all the actual bulk data with the fast symmetric cipher
```

This is exactly what happens in TLS (see [[03-https-and-tls|https-and-tls]]'s handshake diagram) — asymmetric cryptography establishes trust and a shared secret; the entire rest of the connection's actual data is symmetrically encrypted.

## Gotchas

- Asymmetric encryption alone, without additional padding schemes (like OAEP, shown above), is vulnerable to specific structural attacks — always use an established library's implementation rather than hand-rolling raw RSA math.
- A private key's security is everything — if it leaks, every message ever encrypted to the matching public key (without forward secrecy) is retroactively exposed, and every signature that key produced becomes forgeable going forward.
- Quantum computers, if built at sufficient scale, threaten RSA and ECC's underlying hard-math assumptions specifically (Shor's algorithm) — this is the motivation behind ongoing "post-quantum cryptography" standardization, worth knowing the term exists even without needing its details yet.

## Related
- [[02-symmetric-encryption|symmetric-encryption]]
- [[05-digital-signatures-and-pki|digital-signatures-and-pki]]
- [[03-https-and-tls|https-and-tls]]
