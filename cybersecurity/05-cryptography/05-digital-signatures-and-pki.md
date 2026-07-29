# Digital Signatures & PKI

A digital signature proves two things at once: the message hasn't been altered (integrity), and it genuinely came from whoever holds a specific private key (authentication) — and unlike [[03-hashing-and-integrity|HMAC]], it does this **without a shared secret**, using the public/private key pairs from [[04-asymmetric-encryption|asymmetric-encryption]]. That extra property — anyone can verify the signature using only the *public* key, with no shared secret required — is also what provides non-repudiation: only the private key holder could have produced it, so they can't credibly deny having signed it.

## How signing and verification actually work

```
Signing (done with the private key):
  1. Hash the message (see hashing-and-integrity)
  2. Encrypt that hash with the sender's private key -> this encrypted hash is the "signature"

Verification (done with the public key, by anyone):
  1. Decrypt the signature using the sender's public key -> recovers the original hash
  2. Independently hash the received message
  3. Compare the two hashes -> match means: authentic, and unmodified
```

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
message = b"transfer approved"

signature = private_key.sign(
    message,
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256()
)

# anyone with the public key can verify, without ever needing the private key:
public_key = private_key.public_key()
public_key.verify(signature, message, padding.PSS(...), hashes.SHA256())   # raises an exception if invalid
```

ECDSA (elliptic-curve-based signing, see [[04-asymmetric-encryption|asymmetric-encryption]]) achieves the same guarantee with much smaller signatures and faster computation, and is the more common choice in modern systems.

## The remaining problem: whose public key is it, really?

A signature proves a message came from whoever holds a specific private key — but how do you know that public key actually belongs to the person or organization you think it does, and not an attacker who generated their own key pair and claims to be them? This is exactly the problem **PKI (Public Key Infrastructure)** exists to solve.

## Certificate Authorities and the chain of trust

A **Certificate Authority (CA)** is a trusted third party that verifies an entity's identity and then issues a **certificate** — a data structure binding a public key to that verified identity, digitally signed by the CA itself. Your browser/OS ships with a built-in list of trusted **root CAs**; when a website presents a certificate, your browser checks that it's validly signed by a trusted root (often through one or more **intermediate CAs**, forming a chain), rather than needing to somehow personally verify every website's identity itself.

```
Root CA (trusted, built into your OS/browser)
   |
   | signs
   v
Intermediate CA
   |
   | signs
   v
example.com's certificate (public key + identity, signed by the intermediate)
```

This is the exact mechanism briefly introduced in [[03-https-and-tls|https-and-tls]] — this note is that same chain of trust, one level deeper.

## Certificate revocation — what happens when a private key is compromised

If a certificate's private key leaks, the certificate needs to be invalidated before its official expiration date — otherwise an attacker holding the leaked key can impersonate the certificate's owner until it naturally expires. Two mechanisms:

- **CRL (Certificate Revocation List)** — a published list of revoked certificate serial numbers that a client can check against.
- **OCSP (Online Certificate Status Protocol)** — a real-time query to the CA asking "is this specific certificate still valid?" instead of downloading an entire list.

Both add overhead and both have historically had gaps (a client that fails to check, or "fails open" when the check itself is unreachable) — an active area of ongoing improvement in the field rather than a fully solved problem.

## Self-signed certificates and code signing — PKI outside the public-web case

- **Self-signed certificates** — an entity signs its own certificate instead of using a CA; fine for internal/testing purposes where you control both ends and can manually trust the specific certificate, but meaningless as a public trust signal (anyone can self-sign a certificate claiming to be anyone), which is exactly why browsers warn loudly about them for public sites.
- **Code signing certificates** — the same chain-of-trust model applied to software instead of websites: a signed executable/package proves it came from a specific, verified publisher and hasn't been tampered with since signing — the mechanism behind your OS warning (or not warning) about "unidentified developer" software.

## Gotchas

- A signature proves *authenticity and integrity of the message*, not that the message's content is correct or true — someone can validly sign a message containing false information; the signature only proves who said it and that it wasn't altered afterward.
- PKI's entire trust model rests on root CAs behaving correctly and staying uncompromised — a CA that's compromised or issues a fraudulent certificate undermines the trust of everything built on top of it, which is why CA compromises are treated as severe, wide-reaching incidents when they occur.
- Confusing "self-signed" with "insecure" is a common oversimplification — a self-signed certificate can use perfectly strong cryptography; the actual gap is the *trust/verification* problem, not the math.

## Related
- [[04-asymmetric-encryption|asymmetric-encryption]]
- [[03-hashing-and-integrity|hashing-and-integrity]]
- [[03-https-and-tls|https-and-tls]]
