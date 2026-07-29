# Symmetric Encryption

The same key both encrypts and decrypts — fast, mathematically simple to reason about, and the workhorse for actually encrypting bulk data everywhere from disk encryption to the data channel in a TLS connection (see [[03-https-and-tls|https-and-tls]]). Its one hard limitation is right there in the definition: both parties need the *same* key before any of this works, which is a problem symmetric encryption alone can't solve (see [[04-asymmetric-encryption|asymmetric-encryption]] for the actual fix).

## AES — the standard today

**AES (Advanced Encryption Standard)** is the near-universal default symmetric cipher, standardized after an open public competition (again, Kerckhoffs's principle from [[01-what-is-cryptography|what-is-cryptography]] in action — the winning design was made public and has been scrutinized by the entire field for over two decades). AES operates on fixed-size blocks of data (128 bits) using a key of 128, 192, or 256 bits — AES-256 being the common choice when key length itself needs to sound reassuring, though AES-128 is also considered secure for the foreseeable future given current computing power.

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

key = os.urandom(32)          # 256-bit key
iv = os.urandom(16)           # initialization vector — see modes below

cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
encryptor = cipher.encryptor()
ciphertext = encryptor.update(b"secret data") + encryptor.finalize()
```

## Block ciphers vs stream ciphers

- **Block cipher** (AES) — encrypts fixed-size chunks of data at a time; data not evenly divisible into blocks needs padding.
- **Stream cipher** (ChaCha20, a modern, widely used alternative) — encrypts data one bit/byte at a time, well-suited to streaming data where you don't want to wait for a full block, and often faster in software without dedicated hardware acceleration.

## Modes of operation — why the same key + algorithm still needs a "mode"

A block cipher alone only defines how to encrypt *one* block — a **mode of operation** defines how to handle a full message made of many blocks, and getting this wrong quietly destroys the security guarantee even with a strong cipher underneath.

- **ECB (Electronic Codebook)** — encrypts each block independently with no relationship between blocks. **Insecure for almost any real use** — identical plaintext blocks produce identical ciphertext blocks, which can leak patterns in the original data (the classic demonstration: ECB-encrypting an image still visibly shows the image's outline in the ciphertext, since large uniform color blocks stay uniform).
- **CBC (Cipher Block Chaining)** — each block is XORed with the previous block's ciphertext before encrypting, so identical plaintext blocks produce different ciphertext. Needs a random, unique **IV (initialization vector)** per message; requires padding and is vulnerable to specific padding-oracle attacks if error handling leaks information (see [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]]).
- **GCM (Galois/Counter Mode)** — the modern default recommendation: encrypts *and* provides integrity verification (an authentication tag) in one operation, so tampering with the ciphertext is detected automatically rather than needing a separate integrity check bolted on. This combination — encryption plus built-in integrity — is why GCM (or similar "authenticated encryption" modes) is preferred over CBC in new designs.

```
ECB (bad):        [Block1]->[Enc]->[Cipher1]    [Block2]->[Enc]->[Cipher2]   (independent, patterns leak)
CBC:               [Block1] XOR IV -> [Enc] -> [Cipher1] -> XOR -> [Block2] -> [Enc] -> [Cipher2]  (chained)
GCM:               like CBC's chaining idea, but also produces an authentication tag verifying integrity
```

## The key exchange problem — symmetric encryption's actual limitation

Both parties need to already possess the same secret key before any of the above works. For two people who've never met, sharing a key over the same network you're trying to protect is a chicken-and-egg problem — send the key in plaintext and anyone listening gets it too. This is precisely the gap [[04-asymmetric-encryption|asymmetric cryptography]] fills, and precisely why real protocols (TLS included) use asymmetric methods only briefly, at the start, specifically to establish a symmetric key safely — covered as hybrid encryption in that note.

## Gotchas

- **Never use ECB mode** for anything beyond a single, standalone block — this is a specific, well-known, and still-surprisingly-common real-world misconfiguration.
- **Never reuse an IV** with the same key in CBC or GCM — IV reuse breaks the security guarantee of the mode, in GCM's case catastrophically (it can fully expose the authentication key, compromising integrity protection for every message that reused it).
- Key management (generating, storing, rotating, and destroying keys securely) is usually the actual weak point in a real system, not the algorithm — see [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]].

## Related
- [[01-what-is-cryptography|what-is-cryptography]]
- [[04-asymmetric-encryption|asymmetric-encryption]]
- [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]]
