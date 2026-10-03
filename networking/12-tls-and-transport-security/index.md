# TLS & Transport Security

**[Intermediate → Advanced]** — How two machines that have never met set up a private, authenticated channel across a network run by strangers. This lesson covers the protocol, and then, in section 7, the **maths underneath**, worked by hand with small numbers: Diffie-Hellman, why it can't be run backwards, RSA signatures, how one shared secret becomes many keys, and how AES-GCM encrypts and detects tampering. The lab does the maths by hand, then for real, then runs a real TLS 1.3 handshake on your machine with a certificate authority it creates, and breaks it three ways.

## Before you start

You can already:

- Explain what HTTP sends and why ALPN and handshakes cost round trips → [[networking/11-http-evolution/index|HTTP and its evolution]].
- Do arithmetic with remainders: 17 mod 5 is 2, because 17 = 3 × 5 + 2 → [[mathematics/02-discrete-math/08-number-theory-and-modular-arithmetic|number theory and modular arithmetic]] goes further, and the maths section here builds on it.
- Say what a hash function is: a fixed-size fingerprint of any input → [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing and integrity]].
- Run a TypeScript test file with Node 26 (`node --test`), with `openssl` installed (it usually is).

After this lesson you will be able to:

1. Name TLS's three guarantees and the mechanism behind each, and say why authentication comes first.
2. Work a Diffie-Hellman exchange by hand, and explain why an eavesdropper who sees every message still can't compute the secret.
3. Explain what a certificate is, how its signature is checked up to a trusted root, and the four checks a client makes, recognising each failure's error.
4. Trace the TLS 1.3 handshake, and say what forward secrecy is and why TLS 1.3 made it mandatory.

**Study route:** sections 1–6 are the protocol; section 7 is the maths, and can be read on its own. Stop at the predictions in sections 4 and 7 and try them before reading on. Section 8 is the lab.

## The kid version first

You want to send a secret to a shop you've never visited, through a postal system where anyone can read and rewrite your letters. There are three problems, in strict order of importance:

1. **Is this actually the shop?** If you're talking to an impostor, encryption is worthless: you've encrypted your secret *to the attacker*. **Authentication comes first.**
2. **How do we agree on a secret code** when everything we say is public? This looks impossible. It isn't: that's Diffie-Hellman, and section 7 shows the trick.
3. **How do I know my letter wasn't changed** on the way? That's integrity.

TLS solves all three in one handshake.

**Where the analogy stops working.** In the post you'd recognise the shop's handwriting. On the internet there's nothing to recognise: TLS decides "this is the shop" by checking a certificate signed by an organisation your computer was told to trust in advance. Most TLS mistakes in the wild get step 1 wrong while doing steps 2 and 3 perfectly, which is exactly what "certificate verification disabled" means, and why it's so much worse than it sounds.

## 1. Why this exists

The shop's login form sends a password. Without TLS, anyone on the same Wi-Fi, every router on the way, and the ISP can read it, and can change the page on its way back, say to point the "pay" button somewhere else. Encrypting it isn't enough on its own, because an attacker in the middle can simply pretend to be the shop and have the customer encrypt everything to them. TLS has to prove who the server is, agree a key nobody else can learn, and protect every byte afterwards, in one round trip, millions of times a second. And it has to keep working even if, years from now, the server's private key leaks.

## Terms used in this lesson

1. **TLS (Transport Layer Security)**: The letters stand for those words. It's the protocol that gives a connection confidentiality, integrity and authentication; HTTPS is HTTP inside TLS.
2. **Symmetric encryption**: This is encryption where the same key locks and unlocks, such as AES. It's fast, but both sides need the key.
3. **Public-key cryptography**: This is also called **asymmetric** cryptography. Each party has a private key it keeps and a public key it shares; what one does, only the other can undo or check.
4. **Key exchange**: This is two parties agreeing a shared secret over a public channel, so that an eavesdropper can't learn it.
5. **Certificate**: This is a document binding a name (`shop.example`) to a public key, signed by a certificate authority. The standard format is X.509.
6. **Certificate authority (CA)**: This is an organisation that signs certificates. Clients trust a set of **root** CAs built into the operating system or browser.
7. **Digital signature**: This is a value only the holder of a private key can produce for a given message, and anyone with the public key can check.
8. **Forward secrecy**: This means that stealing a server's long-term private key later doesn't let anyone decrypt connections recorded earlier.
9. **AEAD (authenticated encryption with associated data)**: The letters stand for those words. It's encryption that also produces a tag proving the ciphertext, and some unencrypted data alongside it, weren't changed. AES-GCM is one.
10. **Nonce**: This is a "number used once": a value that must never repeat under the same key.
11. **ALPN (Application-Layer Protocol Negotiation)**: The letters stand for those words. It's the part of the TLS handshake where client and server agree which protocol, such as HTTP/2, runs inside.
12. **SNI (Server Name Indication)**: The letters stand for those words. It's the hostname the client sends at the start of the handshake, so one IP address can serve many sites.

## 2. The three guarantees

| Guarantee | Mechanism | If you skip it |
|---|---|---|
| **Confidentiality** | symmetric encryption (AES-GCM, ChaCha20-Poly1305) | anyone on the path reads everything |
| **Integrity** | AEAD: authenticated encryption | anyone on the path silently *changes* everything |
| **Authentication** | X.509 certificates and a chain of trust | you have a perfectly secure channel to an attacker |

## 3. The key-exchange problem, and forward secrecy

Symmetric encryption is fast but needs a shared key. Getting that key to a stranger over a public channel is the founding problem of modern cryptography.

**The old way, RSA key transport (removed in TLS 1.3):** the client picks a secret, encrypts it with the server's public key, and sends it. It works, but has a fatal property: **if the server's private key is ever stolen, every past recorded session can be decrypted.** An adversary can record traffic today and decrypt it years later. "Harvest now, decrypt later" is a real, funded strategy.

**The modern way, ephemeral Diffie-Hellman (ECDHE):** both sides make a *throwaway* key pair for each connection, exchange the public halves, and each computes the same shared secret, which never crosses the wire and can't be reconstructed from the recording (section 7 shows why). The server's long-term key is used only to **sign** the exchange, proving its identity, and never to encrypt the secret.

That gives **forward secrecy**: stealing the server's private key tomorrow reveals nothing about sessions recorded today, because the throwaway keys are gone. In the lab, two connections to the same server with the same certificate derive different session keys. TLS 1.3 made this **mandatory** by removing every key exchange without it, which is the single most important thing TLS 1.3 did.

## 4. Certificates and the chain of trust

A certificate binds a **name** to a **public key**, signed by a **certificate authority**. Checking it walks a chain:

```
shop.example's cert  ──signed by──►  intermediate CA  ──signed by──►  root CA
                                                                        │
                                              already in your OS or browser's trust store
```

The root's public key ships with your operating system. That's the anchor, and it's a *trust decision made for you* by your OS vendor. Roots are kept offline; intermediates do the day-to-day signing, so a compromised intermediate can be revoked without invalidating everything.

What the client checks, and each is a real-world failure:

1. **The signature chain** leads to a trusted root.
2. **Not expired.** The most common outage cause in this whole lesson. Automate renewal ([[devops/06-ci-cd/index|certbot or cert-manager]]) or you *will* be paged at 3 a.m. about it.
3. **The name matches.** The certificate's Subject Alternative Name list must cover the hostname. (Using the Common Name for this has been deprecated since 2017; browsers ignore it.)
4. **Not revoked.** The weakest link. Revocation lists are huge and stale; **OCSP** needs an online check that leaks your browsing to the CA and fails open, so an attacker in the middle can just block it. **OCSP stapling** has the *server* fetch and attach a signed freshness proof. Browsers have largely moved on, and the industry's real answer is **short-lived certificates**: one that expires in weeks matters less if it can't be revoked.

**Predict before reading on.** The lab makes its own CA and a certificate for `shop.test`, then connects three ways: asking for `evil.test`, not trusting the lab's CA, and using a certificate whose dates ended in 2020. What happens in each case?

<details>
<summary>After your prediction</summary>

Each fails, and each with its own error: `ERR_TLS_CERT_ALTNAME_INVALID` for the wrong name, `UNABLE_TO_VERIFY_LEAF_SIGNATURE` when the CA isn't trusted (the client can't check the signature on the server's certificate), and `CERT_HAS_EXPIRED` for the old one. With the right name, the trusted CA and a current certificate, the handshake succeeds. The lab also checks the signature directly: the certificate verifies against the CA's public key.

</details>

**Certificate Transparency** is the systemic fix for wrongly issued certificates: every certificate must be logged in public append-only logs, so domain owners can spot a CA issuing for their domain. **CAA records** in [[networking/10-dns-in-depth/index|DNS]] say which CAs may issue for you at all. Both are cheap and worth setting.

## 5. The handshake, and what TLS 1.3 changed

**TLS 1.2 took two round trips before application data. TLS 1.3 takes one.** The client guesses which key-exchange group the server will pick and sends its key share in the *first* message, so the server can reply with everything needed:

```
TLS 1.2:  ClientHello → ServerHello, Certificate → KeyExchange → Finished → DATA      (2 round trips)
TLS 1.3:  ClientHello + KeyShare → ServerHello + Certificate + CertificateVerify + Finished → DATA   (1 round trip)
```

`CertificateVerify` is the server signing a hash of the whole handshake so far with its certificate's private key. That signature is what ties the throwaway key exchange to the server's identity: an attacker in the middle could run their own key exchange, but couldn't produce that signature. TLS 1.3 also:

- **Deleted the dangerous options.** RSA key transport, static Diffie-Hellman, RC4, 3DES, MD5 and SHA-1, CBC-mode ciphers, compression (which enabled CRIME) and renegotiation are all gone. The cipher-suite list went from hundreds to five. **This is the real lesson of TLS 1.3: most TLS vulnerabilities of the previous decade (BEAST, CRIME, POODLE, FREAK, Logjam, Sweet32) came from *optional legacy support and downgrade negotiation*, not from broken modern crypto.** Removing choices was the security fix.
- **Encrypts more of the handshake**, including the certificate.
- **Offers 0-RTT resumption**: on a resumed connection, application data can go in the very first packet. It's free speed with a real catch: **0-RTT data can be replayed** by an attacker who captured it, so only idempotent requests belong there. A `POST /transfer` in 0-RTT is a real vulnerability.

**SNI** lets one IP address host many TLS sites by sending the hostname in the `ClientHello`. It's necessary, but sent in the clear, so it reveals which site you're visiting even though the traffic is encrypted; **Encrypted Client Hello** fixes that and is rolling out now. **ALPN** negotiates HTTP/1.1, HTTP/2 or HTTP/3 in the same handshake, with no extra round trip. In the lab's handshake: TLS 1.3, the cipher suite `TLS_AES_256_GCM_SHA384`, ALPN choosing `h2`, and a key exchange called `X25519MLKEM768` (section 7 explains that name).

## 6. Mutual TLS, and what TLS doesn't give you

**Mutual TLS** has the *client* present a certificate too, so both sides are authenticated cryptographically rather than by a bearer token. It's the backbone of [[architecture/03-architectural-patterns/04-microservices-patterns|service mesh]] identity and zero-trust networking: services prove who they are with a key they hold, rather than a secret they could leak.

What TLS explicitly doesn't protect:

- **Traffic metadata.** Sizes, timing and destination IP addresses are all visible, and encrypted traffic still leaks a lot to analysis.
- **Anything after termination.** TLS ended at your load balancer means plain text behind it, which is fine if that network is trusted, and exactly what mutual TLS and service meshes exist to stop assuming.
- **The endpoints.** A compromised server serves malware over a perfect TLS connection. **The padlock means "encrypted to the site you named", never "this site is trustworthy"**: the most widely misunderstood point in web security, and why phishing sites all have valid certificates now.

## 7. The maths underneath

Everything in this section is checked by the lab with the same numbers. It builds on [[mathematics/02-discrete-math/08-number-theory-and-modular-arithmetic|modular arithmetic]] and [[cybersecurity/05-cryptography/04-asymmetric-encryption|asymmetric encryption]], which have more of the number theory.

### Arithmetic on a clock

"$a \bmod n$" is the remainder when $a$ is divided by $n$: arithmetic on a clock with $n$ hours, where counting past $n - 1$ wraps round to 0. The useful fact is that you can reduce at every step and get the same answer: $(a \times b) \bmod n = ((a \bmod n) \times (b \bmod n)) \bmod n$. That's what keeps the numbers small, however big the exponents get.

### Diffie-Hellman, by hand

In words: both sides agree a public prime $p$ and a public number $g$. Each picks a secret, and sends $g$ raised to its secret, mod $p$. Each then raises the number it *received* to its *own* secret. Because raising to $a$ then $b$ is the same as raising to $b$ then $a$, both arrive at $g^{ab} \bmod p$, a number neither ever sent.

$$A = g^a \bmod p, \qquad B = g^b \bmod p, \qquad B^a \bmod p = g^{ab} \bmod p = A^b \bmod p$$

With $p = 23$ and $g = 5$, Alice picks $a = 6$ and Bob picks $b = 15$:

1. Alice sends $A = 5^6 \bmod 23 = 15{,}625 \bmod 23 = 8$.
2. Bob sends $B = 5^{15} \bmod 23 = 19$.
3. Alice computes $19^6 \bmod 23 = 2$. Bob computes $8^{15} \bmod 23 = 2$. **The shared secret is 2**, and it never crossed the wire.

An eavesdropper saw 23, 5, 8 and 19.

**Predict before reading on.** How would the eavesdropper find the secret, and why does that stop working with real numbers?

<details>
<summary>After your prediction</summary>

They'd need $a$ or $b$: the exponent that turns 5 into 8 mod 23. That's the **discrete logarithm**, and for a group this small they just try every exponent: 5¹, 5², 5³… until one gives 8. With real sizes, that becomes hopeless, as the next part shows.

</details>

### Easy forwards, hard backwards

Raising a number to a huge power mod $p$ is fast with **square-and-multiply**: walk the exponent's binary digits, squaring at each step and multiplying when the digit is 1. The work grows with the number of *digits* of the exponent, not its size. The lab computes $3^{54{,}321} \bmod 65{,}537$ in **23** multiplications, while finding the exponent from the answer, by trying each one in turn, takes **54,321** steps: one per possible exponent.

Scale that up. The X25519 key exchange works in a group of about $2^{252}$ elements. Forwards, a 255-bit exponent takes **508** multiplications (the lab counts them). Backwards, trying exponents would take about $2^{252}$ steps; even the cleverest known attack on this kind of group needs about $2^{126}$, the square root, which is still far beyond every computer on Earth running until the Sun burns out. That gap, a few hundred steps one way and an impossible number the other, is the whole security of the key exchange.

(Ordinary numbers mod a prime do have shortcuts faster than trying every exponent, which is why classic Diffie-Hellman needs primes of 2,048 bits or more. Elliptic curves have no known shortcut beyond the square root, so 256-bit keys suffice.)

### Elliptic curves, the idea

X25519 does the same exchange on an **elliptic curve**: the points $(x, y)$ satisfying $y^2 = x^3 + 486662x^2 + x$, with all arithmetic mod the prime $2^{255} - 19$, hence the name. There's a way to "add" two points to get a third, and "multiplying" a point $P$ by a secret number $k$ means adding it to itself $k$ times, done fast with double-and-add, the same trick as square-and-multiply. The exchange is then: Alice sends $aP$, Bob sends $bP$, and each computes $a(bP) = b(aP)$. The public keys are 32 bytes, against 256 for 2,048-bit classic Diffie-Hellman, for the same security. In the lab, two real X25519 key pairs, made with `node:crypto`, compute the same 32-byte secret, and the 32-byte public keys are all that would cross the wire.

### What `X25519MLKEM768` means: getting ready for quantum computers

A large enough quantum computer, running Shor's algorithm, would solve discrete logarithms, on curves too, and break this exchange, along with RSA. Such a computer doesn't exist yet, but traffic recorded now could be decrypted when one does. So modern TLS libraries run a **hybrid** exchange: X25519 *and* ML-KEM-768, a "key encapsulation mechanism" based on lattice problems that quantum computers aren't known to solve, standardised as FIPS 203 in 2024. The two secrets are combined, so the connection stays safe as long as *either* holds. It's the default in OpenSSL 3.5, which is why the lab's handshake reports `X25519MLKEM768`.

### Signatures, by hand: RSA

The certificate and `CertificateVerify` rest on signatures. RSA is the easiest to work by hand.

In words: choose two primes and multiply them to get $n$. Choose a public exponent $e$, and compute a private exponent $d$ so that raising to $e$ and then to $d$ (or the other way round) brings any number back to itself, mod $n$. Signing raises the message's hash to the *private* $d$; checking raises the signature to the *public* $e$, and compares it with the hash.

$$s = h^d \bmod n, \qquad s^e \bmod n = h$$

With $p = 61$ and $q = 53$: $n = 3{,}233$, and $\varphi(n) = 60 \times 52 = 3{,}120$ counts the numbers below $n$ that share no factor with it. Choose $e = 17$. Then $d$ is the inverse of 17 mod 3,120, found with the extended Euclidean algorithm: $d = 2{,}753$, because $17 \times 2{,}753 = 46{,}801 = 15 \times 3{,}120 + 1$.

1. Sign the hash $h = 65$: $s = 65^{2753} \bmod 3233 = 588$.
2. Anyone with $(n, e)$ checks: $588^{17} \bmod 3233 = 65$. It matches. For any other hash, say 66, it doesn't.

Why it works: Euler's theorem says $h^{\varphi(n)} \equiv 1 \pmod n$, and $ed = 1 + 15\varphi(n)$, so $h^{ed} = h \times (h^{\varphi(n)})^{15} \equiv h$. Forging a signature means finding $d$, which means knowing $\varphi(n)$, which means factoring $n$. That's easy for 3,233 and infeasible for the 2,048-bit $n$ of a real RSA key. Real certificates sign a SHA-256 hash of their contents, with RSA or, like the lab's certificate, with ECDSA on the curve P-256, the elliptic-curve equivalent.

### One secret, many keys: HKDF

The shared secret isn't used directly. TLS 1.3 feeds it through **HKDF**. In words: HKDF first condenses the secret into a uniformly random key (*extract*), then stretches that into as many independent keys as needed, each tied to a label and to a hash of the handshake so far (*expand*). So the client-to-server key, the server-to-client key and the handshake keys are all different, and tampering with any handshake message changes them all. In the lab, the labels `c ap traffic` and `s ap traffic`, the ones TLS 1.3 uses, give two different keys from one secret.

### Encrypting and detecting tampering: AES-GCM

Each record is sealed with AES-256-GCM, which does two things at once:

1. **Encryption, in counter mode.** AES turns a key and a counter into a block of random-looking bytes, the *keystream*. The plaintext is combined with the keystream by XOR (a bitwise "differs?"). Decrypting does the same XOR again.
2. **A 16-byte tag.** Computed over the ciphertext and the *associated data* (the record's header, sent in the clear but protected) using multiplication in a 128-bit finite field (GHASH). The receiver recomputes it and **rejects the record if it doesn't match**, before using any of it.

In the lab, flipping a single bit of the ciphertext makes decryption fail with "unable to authenticate data", and so does using the other direction's key. The one rule that must never break: **a nonce must never repeat under the same key.** If it does, the two records share a keystream, so XORing their ciphertexts cancels it out and leaves the XOR of the two plaintexts, and the tag's key can be recovered too. TLS 1.3 builds each record's nonce from a per-direction value XORed with the record's sequence number, so it never repeats.

## 8. The lab: the maths by hand, then a real handshake

`tlsmath.ts` has square-and-multiply, a brute-force discrete logarithm, the modular inverse, and wrappers for X25519, HKDF and AES-256-GCM from `node:crypto`. `tls.test.ts` checks every number in section 7, then uses the `openssl` command to create a certificate authority and certificates for `shop.test` (one current, one expired in 2020) in a temporary folder, runs a real TLS server on 127.0.0.1, and connects to it: once correctly, twice to compare session keys, and three times to fail.

```ts
// tlsmath.ts — the maths under TLS, small enough to follow by hand, then the real thing with node:crypto.
// The toy numbers are for understanding only: never use hand-written crypto, or numbers this small, for real.
import { createCipheriv, createDecipheriv, diffieHellman, generateKeyPairSync, hkdfSync, type KeyObject } from "node:crypto";

/**
 * base^exp mod m by square-and-multiply: walk the exponent's bits, squaring each time and multiplying when the bit
 * is 1. Reducing mod m after every step keeps the numbers small. Returns the result and the multiplications used,
 * which grow with the number of bits in exp, not with exp itself.
 */
export function modPow(base: bigint, exp: bigint, m: bigint): { value: bigint; multiplications: number } {
  let result = 1n;
  let b = base % m;
  let e = exp;
  let multiplications = 0;
  while (e > 0n) {
    if (e & 1n) {
      result = (result * b) % m;
      multiplications++;
    }
    b = (b * b) % m;
    multiplications++;
    e >>= 1n;
  }
  return { value: result, multiplications };
}

/** The other direction: find x with g^x ≡ target (mod p) by trying x = 1, 2, 3, … The only general way for a small group. */
export function discreteLog(g: bigint, target: bigint, p: bigint): { x: bigint; steps: number } {
  let value = 1n;
  for (let x = 1n, steps = 1; x < p; x++, steps++) {
    value = (value * g) % p;
    if (value === target) return { x, steps };
  }
  throw new RangeError("no solution");
}

/** The inverse of a mod m, by the extended Euclidean algorithm: the d with a·d ≡ 1 (mod m). */
export function modInverse(a: bigint, m: bigint): bigint {
  let [oldR, r] = [a, m];
  let [oldS, s] = [1n, 0n];
  while (r !== 0n) {
    const q = oldR / r;
    [oldR, r] = [r, oldR - q * r];
    [oldS, s] = [s, oldS - q * s];
  }
  if (oldR !== 1n) throw new RangeError("no inverse: a and m share a factor");
  return ((oldS % m) + m) % m;
}

/** A real X25519 key pair: the private key stays here; only the 32-byte public key is ever sent. */
export function keyPair(): { privateKey: KeyObject; publicKey: KeyObject } {
  return generateKeyPairSync("x25519");
}

/** Both sides compute this from their own private key and the other's public key, and get the same 32 bytes. */
export function sharedSecret(mine: KeyObject, theirs: KeyObject): Buffer {
  return diffieHellman({ privateKey: mine, publicKey: theirs });
}

/**
 * HKDF turns one shared secret into as many independent keys as needed, each tied to a label: "client to server"
 * and "server to client" get different keys from the same secret, as TLS 1.3's key schedule does.
 */
export function deriveKey(secret: Buffer, label: string, transcriptHash: Buffer): Buffer {
  return Buffer.from(hkdfSync("sha256", secret, transcriptHash, label, 32));
}

/**
 * AES-256-GCM: encrypts and also computes a 16-byte tag over the ciphertext and the "additional data" (sent in the
 * clear but protected, like a record's header). A nonce must never repeat under the same key.
 */
export function seal(key: Buffer, nonce: Buffer, plaintext: string, additionalData: Buffer) {
  const cipher = createCipheriv("aes-256-gcm", key, nonce);
  cipher.setAAD(additionalData);
  const ciphertext = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  return { ciphertext, tag: cipher.getAuthTag() };
}

/** Decrypts, and throws unless the tag proves nothing was changed: ciphertext, additional data or tag. */
export function open(key: Buffer, nonce: Buffer, ciphertext: Buffer, tag: Buffer, additionalData: Buffer): string {
  const decipher = createDecipheriv("aes-256-gcm", key, nonce);
  decipher.setAAD(additionalData);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString("utf8");
}
```

```ts
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { X509Certificate } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import tls from "node:tls";
import { deriveKey, discreteLog, keyPair, modInverse, modPow, open, seal, sharedSecret } from "./tlsmath.ts";

test("Diffie-Hellman by hand: p = 23, g = 5, secrets 6 and 15", () => {
  const [p, g, a, b] = [23n, 5n, 6n, 15n];
  const A = modPow(g, a, p).value; // Alice sends A
  const B = modPow(g, b, p).value; // Bob sends B
  assert.deepEqual([A, B], [8n, 19n]);
  assert.equal(modPow(B, a, p).value, 2n); // Alice: B^a = g^(ba)
  assert.equal(modPow(A, b, p).value, 2n); // Bob:   A^b = g^(ab): the same secret, never sent
});

test("easy forwards, hard backwards: the discrete logarithm", () => {
  const forwards = modPow(3n, 54_321n, 65_537n);
  assert.deepEqual(forwards, { value: 21_002n, multiplications: 23 }); // about two per bit of the exponent
  assert.deepEqual(discreteLog(3n, 21_002n, 65_537n), { x: 54_321n, steps: 54_321 }); // one per possible exponent
  // X25519's group has about 2^252 elements: forwards is still a few hundred multiplications...
  assert.equal(modPow(5n, 2n ** 255n - 21n, 2n ** 255n - 19n).multiplications, 508);
  // ...and backwards, by trying exponents, would take about 2^252 steps. Better algorithms exist, but not good enough.
});

test("an RSA signature by hand: n = 61 × 53, e = 17", () => {
  const [p, q, e] = [61n, 53n, 17n];
  const n = p * q;
  const d = modInverse(e, (p - 1n) * (q - 1n)); // the private exponent: e × d ≡ 1 (mod φ(n))
  assert.deepEqual([n, d], [3233n, 2753n]);
  const digest = 65n; // in reality, a hash of the certificate's contents
  const signature = modPow(digest, d, n).value; // only the private key can make this
  assert.equal(signature, 588n);
  assert.equal(modPow(signature, e, n).value, 65n); // anyone with the public key (n, e) can check it
  assert.notEqual(modPow(signature, e, n).value, 66n); // and it doesn't fit any other digest
});

test("the real thing: X25519, then HKDF, then AES-256-GCM", () => {
  const [client, server] = [keyPair(), keyPair()];
  const clientSecret = sharedSecret(client.privateKey, server.publicKey);
  assert.deepEqual(clientSecret, sharedSecret(server.privateKey, client.publicKey)); // the same 32 bytes on both sides
  assert.equal(clientSecret.length, 32);
  assert.equal(client.publicKey.export({ type: "spki", format: "der" }).length, 44); // 12 bytes of label + the 32-byte key

  const transcript = Buffer.from("hash of every handshake message so far");
  const clientToServer = deriveKey(clientSecret, "c ap traffic", transcript);
  const serverToClient = deriveKey(clientSecret, "s ap traffic", transcript);
  assert.notDeepEqual(clientToServer, serverToClient); // one secret, independent keys per direction

  const nonce = Buffer.alloc(12, 1);
  const header = Buffer.from([23, 3, 3, 0, 40]); // a TLS record header: sent in the clear, but covered by the tag
  const { ciphertext, tag } = seal(clientToServer, nonce, "GET / HTTP/1.1", header);
  assert.equal(open(clientToServer, nonce, ciphertext, tag, header), "GET / HTTP/1.1");
  const tampered = Buffer.from(ciphertext);
  tampered[0] ^= 1; // flip one bit on the way
  assert.throws(() => open(clientToServer, nonce, tampered, tag, header), /unable to authenticate/);
  assert.throws(() => open(serverToClient, nonce, ciphertext, tag, header), /unable to authenticate/); // the wrong key
});

// A small certificate authority, made with the openssl command-line tool in a temporary folder.
let dir = "";
const file = (name: string) => readFileSync(join(dir, name));

before(() => {
  dir = mkdtempSync(join(tmpdir(), "tls-lab-"));
  const openssl = (...args: string[]) => execFileSync("openssl", args, { cwd: dir, stdio: "pipe" });
  const ec = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256", "-nodes"];
  openssl("req", "-x509", ...ec, "-keyout", "ca.key", "-out", "ca.crt", "-subj", "/CN=Lab Root CA", "-days", "1");
  openssl("req", ...ec, "-keyout", "shop.key", "-out", "shop.csr", "-subj", "/CN=shop.test");
  writeFileSync(join(dir, "san.cnf"), "subjectAltName=DNS:shop.test\n"); // the names the certificate is valid for
  const sign = ["x509", "-req", "-in", "shop.csr", "-CA", "ca.crt", "-CAkey", "ca.key", "-extfile", "san.cnf"];
  openssl(...sign, "-out", "shop.crt", "-days", "1");
  openssl(...sign, "-out", "expired.crt", "-not_before", "20200101000000Z", "-not_after", "20200102000000Z");
});

after(() => rmSync(dir, { recursive: true, force: true }));

/** Starts a TLS server with this certificate, connects once, and reports what the client saw. */
async function handshake(cert: string, client: tls.ConnectionOptions) {
  const server = tls.createServer({ key: file("shop.key"), cert: file(cert), ALPNProtocols: ["h2", "http/1.1"] }, (s) => s.end());
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    return await new Promise<Record<string, unknown>>((resolve) => {
      const socket = tls.connect({ port: (server.address() as { port: number }).port, host: "127.0.0.1", ...client }, () => {
        resolve({
          version: socket.getProtocol(),
          cipher: socket.getCipher().name,
          alpn: socket.alpnProtocol,
          group: socket.getEphemeralKeyInfo() && (socket.getEphemeralKeyInfo() as { name: string }).name,
          sessionKeys: socket.exportKeyingMaterial(16, "lab").toString("hex"),
        });
        socket.end();
      });
      socket.on("error", (err: NodeJS.ErrnoException) => resolve({ error: err.code }));
    });
  } finally {
    server.close();
  }
}

test("the certificate's signature checks out against the CA's public key, and names shop.test", () => {
  const shop = new X509Certificate(file("shop.crt"));
  const ca = new X509Certificate(file("ca.crt"));
  assert.equal(shop.verify(ca.publicKey), true);
  assert.equal(shop.checkHost("shop.test"), "shop.test");
  assert.equal(shop.checkHost("evil.test"), undefined);
});

test("a real TLS 1.3 handshake: one cipher suite, ALPN, a hybrid post-quantum key exchange", async () => {
  const result = await handshake("shop.crt", { servername: "shop.test", ca: file("ca.crt"), ALPNProtocols: ["h2", "http/1.1"] });
  assert.equal(result.version, "TLSv1.3");
  assert.equal(result.cipher, "TLS_AES_256_GCM_SHA384");
  assert.equal(result.alpn, "h2"); // HTTP/2 chosen inside the handshake, no extra round trip
  assert.equal(result.group, "X25519MLKEM768"); // X25519 combined with ML-KEM: the default in OpenSSL 3.5
});

test("every connection gets fresh keys, even with the same certificate", async () => {
  const options = { servername: "shop.test", ca: file("ca.crt") };
  const [first, second] = [await handshake("shop.crt", options), await handshake("shop.crt", options)];
  assert.notEqual(first.sessionKeys, second.sessionKeys); // ephemeral key exchange: forward secrecy
});

test("the three checks a client makes, each failing on its own", async () => {
  const trusted = { ca: file("ca.crt") };
  assert.equal((await handshake("shop.crt", { ...trusted, servername: "evil.test" })).error, "ERR_TLS_CERT_ALTNAME_INVALID"); // wrong name
  assert.equal((await handshake("shop.crt", { servername: "shop.test" })).error, "UNABLE_TO_VERIFY_LEAF_SIGNATURE"); // CA not trusted
  assert.equal((await handshake("expired.crt", { ...trusted, servername: "shop.test" })).error, "CERT_HAS_EXPIRED"); // out of date
});
```

**Lab:** the code is in [`networking/12-tls-and-transport-security/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/12-tls-and-transport-security/labs/typescript). From the vault root, `python3 labs/run.py tls-and-transport-security/typescript` runs the tests and checks this page still shows the same code. It needs `openssl` 3.4 or later on your `PATH` (for `-not_after`). Expect eight passing tests in under a second. The toy numbers are for understanding: never write your own crypto for real use.

## Common pitfalls

1. **Turning off certificate verification** (`rejectUnauthorized: false`, `curl -k`, `verify=False`). You keep the encryption and lose the authentication, which was the point.
2. **Letting certificates expire.** Automate renewal and monitor expiry dates.
3. **Certificates without the right Subject Alternative Names.** The Common Name isn't checked any more.
4. **Allowing TLS 1.0 and 1.1, or legacy ciphers**, "for compatibility". Downgrade attacks live there.
5. **Sending non-idempotent requests as 0-RTT data.** They can be replayed.
6. **Reusing a nonce with AES-GCM** in your own code. Use a library that handles nonces, or one designed to tolerate reuse.
7. **Reading the padlock as "safe".** It means "encrypted to this name", nothing more.

## Check your understanding

1. Why does TLS put authentication before encryption?
2. In Diffie-Hellman with $p = 23$, $g = 5$, Alice's secret is 4 and Bob's is 3. Work out what each sends and the shared secret.
3. An attacker records all of a TLS 1.3 session, then steals the server's private key a year later. Why can't they decrypt the recording?
4. What does the server's `CertificateVerify` signature prove, and what attack would be possible without it?
5. Why must an AES-GCM nonce never repeat under the same key?
6. A client says `UNABLE_TO_VERIFY_LEAF_SIGNATURE`. What's wrong, and what are two possible fixes?

<details>
<summary>Answers — after your attempt</summary>

1. Encryption to an impostor protects nothing: the attacker decrypts it. Only once the server has proved it holds the private key for a certificate naming the site does the encrypted channel mean anything.
2. Alice sends $5^4 \bmod 23 = 625 \bmod 23 = 4$. Bob sends $5^3 \bmod 23 = 125 \bmod 23 = 10$. Alice computes $10^4 \bmod 23 = 10{,}000 \bmod 23 = 18$; Bob computes $4^3 \bmod 23 = 64 \bmod 23 = 18$. The shared secret is **18**.
3. The session key came from an ephemeral key exchange whose private values were thrown away after the handshake. The server's long-term key only *signed* the exchange; it was never used to encrypt or derive the session key, so stealing it reveals nothing about past sessions.
4. That the server holds the private key matching its certificate, and that it took part in *this* handshake, since it signs a hash of the messages so far. Without it, an attacker in the middle could run their own key exchange with the client while forwarding a real certificate they can't use.
5. A repeated nonce gives the same keystream, so XORing the two ciphertexts removes the keystream and leaves the XOR of the two plaintexts, often enough to recover both. It also exposes the key used for the tag, letting an attacker forge records.
6. The client can't check the signature on the server's certificate, usually because the issuing CA isn't in its trust store, or because the server didn't send the intermediate certificate. Fix the server to send its full chain, or, for a private CA, add that CA to the client's trusted roots (the lab passes `ca`).

</details>

## Practice — independent task

**Inspect a real handshake and certificate.**

1. Run `openssl s_client -connect example.com:443 -servername example.com -alpn h2 </dev/null` and find: the protocol version, the cipher suite, the key-exchange group (`Negotiated TLS1.3 group` or `Server Temp Key`), the ALPN result and the certificate chain.
2. Save the server certificate with `-showcerts`, and run `openssl x509 -noout -text` on it: find the Subject Alternative Names, the validity dates, the signature algorithm and the public key type.
3. By hand, on paper, do Diffie-Hellman with $p = 23$, $g = 5$ and secrets of your choice, then check your answer by changing the lab's first test.

**A smaller step first:** in the lab, change the RSA exponent from $e = 17$ to $e = 7$. Predict whether $d$ exists (does 7 share a factor with 3,120?), then compute $d$ and check a signature.

**Done when:** you have the handshake details and certificate fields written down with one sentence each on what they mean, a hand-worked Diffie-Hellman exchange that the lab confirms, and an answer to whether example.com's handshake was post-quantum.

## Before moving on

You can name TLS's guarantees and their mechanisms, work Diffie-Hellman and an RSA signature by hand, explain why the reverse direction is infeasible, check a certificate chain and name each failure, trace the TLS 1.3 handshake, and explain forward secrecy.

**Recap.** TLS authenticates the server with a certificate chained to a trusted root (name, dates, signature, revocation), agrees a key with an ephemeral elliptic-curve Diffie-Hellman exchange (now often hybrid with ML-KEM against future quantum computers), proves the server took part by signing the handshake, derives separate keys with HKDF, and seals every record with AES-GCM, which rejects any change. The maths works because some operations are cheap forwards and infeasible backwards: 508 multiplications to compute, about $2^{126}$ steps to undo. TLS 1.3 does it in one round trip, makes forward secrecy mandatory, and removed the legacy options that caused a decade of attacks. The padlock means "encrypted to this name", never "trustworthy".

**Next.** You now have the whole of week 7's story: DNS finds the address, TCP and TLS set up a private, authenticated channel, and HTTP carries the request. Write *what happens when I type google.com?* from memory, then week 8 follows the request into the server: [[backend/01-foundations/03-the-request-lifecycle|the request lifecycle]].

## Related

- [[cybersecurity/05-cryptography/index|Cryptography]]: the primitives underneath, in more depth
- [[mathematics/02-discrete-math/08-number-theory-and-modular-arithmetic|Number theory and modular arithmetic]]: the maths of section 7, including RSA in full
- [[networking/13-quic-and-modern-transport|QUIC]]: TLS 1.3 fused into the transport itself
- [[networking/11-http-evolution/index|HTTP and its evolution]]: ALPN, and why browsers need TLS for HTTP/2
- [[cybersecurity/03-network-security/03-vpns-and-encryption-in-transit|Encryption in transit]]: the operator's view
