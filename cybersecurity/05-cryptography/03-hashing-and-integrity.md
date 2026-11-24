---
id: 02abaad4-4366-4a4c-8767-328f191bd438
---

# Hashing and Integrity

**A hash function turns any amount of data into a short, fixed-size fingerprint, so that the same data always gives the same fingerprint and any change, however small, gives a completely different one.**

## Before you start
<!-- bite: 6ff4bae5-f7ee-4c05-8fb0-11e59fb4b0fe -->

You should have:

- Read the map of the four goals → [[cybersecurity/05-cryptography/01-what-is-cryptography|what is cryptography]].
- Python 3 and `sha256sum` (standard on Linux).
- Stored passwords with bcrypt → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]]. This lesson explains why that needed a *different* kind of hash.

After this lesson you will be able to:

1. List the properties a cryptographic hash needs, and see the avalanche effect for yourself.
2. Say which hashes are broken (MD5, SHA-1) and what to use instead.
3. Verify a download with its published SHA-256.
4. Sign and verify a webhook with HMAC, and compare MACs safely.

**Study route.** Kid version and §1–4, then the worked example: a webhook you sign, tamper with, and verify.

## What hashing is
<!-- bite: 74d826c0-e0a1-41f4-8743-9945650580de -->

You've used hashes twice already in this course: bcrypt stored passwords as hashes, and the JWT in lesson 01 carried a hash-based signature. Hashing is the tool for integrity: it answers "is this exactly the data it should be?"

But a plain hash has a gap: anyone can compute one, so it can't tell you *who* made it. This lesson builds up to the fix, HMAC, which puts a secret key into the hash. It's how your payment provider proves a "payment received" message really came from them, and you'll build exactly that.

## The kid version
<!-- bite: e8f25342-952e-4083-9630-47574fb82374 -->

Think of a fingerprint. Every person has one, it's tiny compared to the whole person, and two different people practically never share one. Looking at a fingerprint, you can't rebuild the person. But if someone shows you a fingerprint and a person, you can check in seconds whether they match.

A hash is a fingerprint for data. A whole film gives a 64-character hash. Change one pixel and the fingerprint is totally different.

**Where the analogy stops working.** Anyone can take anyone's fingerprint. So if an attacker swaps the file *and* the fingerprint printed beside it, the check passes. A plain hash proves "this matches that fingerprint", not "this came from the right person". That's what HMAC (§4) and signatures (lesson 05) add.

## 1. What a cryptographic hash must do
<!-- bite: 89b408ce-cd96-4d16-99a5-d7ff5fcb6ceb -->

A hash function for security needs four properties:

1. **Deterministic** — the same input always gives the same hash.
2. **One-way** — given a hash, you can't work back to an input that makes it. The only way is guessing.
3. **Collision-resistant** — nobody can find two *different* inputs with the same hash.
4. **Avalanche effect** — change one bit of input, and about half the output bits change. The new hash looks nothing like the old.

Here's the avalanche effect with real values. One letter changes, `d` to `e`:

```text
sha256("hello world") = b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
sha256("hello worle") = 0fc30e735a0228a31cbbb969988b4f50e02e737f979f091d7d224b765443f5d4
```

No resemblance at all. That's what makes a hash useful for spotting changes: there's no "almost the same" hash that a small edit could hide behind.

## 2. Which hashes to use, and which are broken
<!-- bite: db176e4d-aaa4-4da5-a2bf-5681d9932228 -->

**SHA-256** (from the SHA-2 family) is the standard choice today. **SHA-3** and **BLAKE2/BLAKE3** are good alternatives.

**MD5** and **SHA-1** are broken: researchers have produced real collisions for both, two different files with the same hash. In 2017 Google published two different PDFs with the same SHA-1. So never use them where an attacker could benefit from a collision: signatures, certificates, file verification against a malicious source. You'll still see them in old systems and as quick checksums for accidental corruption, where no attacker is involved. Know their names so you can flag them.

And remember the distinction from the web-security section: **general-purpose hashes are built to be fast; password hashes are built to be slow.** SHA-256 is right for fingerprinting a file and wrong for storing a password. bcrypt and Argon2 are right for passwords and pointless for files.

## 3. Verifying a download
<!-- bite: 53a54e93-bce5-475e-95d7-895ced74f404 -->

The everyday use: software sites publish the SHA-256 of each download. You hash what you received and compare. If even one byte changed, through a bad network or a tampered mirror, the hashes won't match.

```bash
sha256sum kali-linux.iso                       # prints the hash; compare it with the website's
echo "<published-hash>  kali-linux.iso" | sha256sum -c     # prints: kali-linux.iso: OK
```

Remember the analogy's limit, though. If an attacker controls the website, they change the file *and* the published hash, and your check passes. That's why serious projects also *sign* the hash list with a private key (lesson 05). The hash proves the file matches the list; the signature proves who wrote the list.

## Terms used in this lesson
<!-- bite: 45d64bbf-f23f-4734-b236-8c02887dc3dd -->

1. **Hash function**: This is a function that turns any input into a fixed-size output, the **hash** or **digest**, in a way that can't be reversed.
2. **Collision**: This is two different inputs that give the same hash. A secure hash makes finding one practically impossible.
3. **Avalanche effect**: This is a tiny change in the input completely changing the hash.
4. **SHA-256**: This is the standard 256-bit hash from the SHA-2 family. Its output is 64 hex characters.

## Terms used in this lesson: keys and checks
<!-- bite: 8b7108dc-ebcf-473f-a27f-eea60cbf4010 -->

The rest of the terms are about adding a key to a hash and checking the result safely.

5. **MAC (message authentication code)**: The letters stand for those words. It's a short value computed from a message and a secret key, proving the message wasn't changed and came from someone with the key.
6. **HMAC (hash-based MAC)**: The letters stand for those words. It's the standard way to build a MAC from a hash function like SHA-256.
7. **Webhook**: This is a request one service sends to another when something happens, like a payment provider telling your app "order 42 was paid".
8. **Constant-time comparison**: This is comparing two values in a way that takes the same time whether they differ in the first byte or the last, so timing leaks nothing.

## 4. HMAC — a hash only the key holder can make
<!-- bite: 46c7a7b5-fd81-46ea-82c7-a22ebbebe2c4 -->

A plain hash can't prove who made it, because anyone can compute one. **HMAC** fixes that by mixing a secret key into the hash. Only someone who holds the key can produce the right HMAC for a message. So a matching HMAC proves two things at once: the message wasn't changed (integrity), and it came from someone with the key (authentication).

This is exactly how payment providers and GitHub protect webhooks. When you set up the webhook, you and the provider share a secret. Every webhook they send carries an HMAC of the body in a header. Your server computes the HMAC of the body it received, with the same secret, and compares. Match: genuine. No match: forged or altered, reject it.

One detail matters. Compare with a **constant-time** function, never `==`. A plain `==` stops at the first differing byte, so it answers slightly faster for a bad guess than for an almost-right one, and an attacker who measures those times can work out the correct value byte by byte. Python's `hmac.compare_digest` always takes the same time.

## Worked example — verify a webhook with HMAC
<!-- bite: 952a522a-95e9-4f6b-a272-3088570a86a8 -->

Your Mama Put API gets a webhook from the payment provider saying order 42 was paid. Save this as `webhook.py`:

```python
# webhook.py: check that a webhook really came from the payment provider.
import hmac, hashlib

SECRET = b"webhook-secret"          # shared once with the provider, kept out of git

def sign(body: bytes) -> str:
    """What the provider does: HMAC-SHA256 of the raw body, sent in a header."""
    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()

def verify(body: bytes, signature: str) -> bool:
    """What your server does: recompute and compare in constant time."""
    return hmac.compare_digest(sign(body), signature)

body = b'{"order":42,"status":"paid"}'
header = sign(body)
print("signature:", header)
print("genuine: ", verify(body, header))
print("tampered:", verify(b'{"order":42,"status":"refunded"}', header))
print("forged:  ", verify(body, hmac.new(b"guessed-secret", body, hashlib.sha256).hexdigest()))
```

## Worked example: reading the output
<!-- bite: e78008f3-9dc5-4cd6-bf1e-50b78b8dd395 -->

**Predict first:** which of the three checks pass? Then run `python3 webhook.py`:

```text
signature: b20e72f1fbbab7a4a5654ddc6cf7902cd651670109d95df93adf9e36673af8d5
genuine:   True
tampered:  False
forged:    False
```

The genuine webhook passes. Changing `paid` to `refunded` fails, because the HMAC of the new body is completely different (the avalanche effect again). And an attacker who doesn't know the secret can't make a valid signature, even for the real body. That's integrity and authentication from one line of maths.

Two real-world rules come with it. Verify against the **raw bytes** of the body, before any JSON parsing, because re-serialising can change spacing and break the match. And reject old webhooks: providers include a timestamp in the signed data so a captured webhook can't be replayed next week.

## Common pitfalls and traps
<!-- bite: 38f9ae1c-0358-495d-bbf2-f8f248690fc5 -->

1. **MD5 or SHA-1 for anything security-related.** Both have real collisions. Use SHA-256 or better.
2. **A fast hash for passwords.** SHA-256 is for fingerprints. Passwords need bcrypt or Argon2.
3. **A plain hash where you need authenticity.** Anyone can compute SHA-256, so a hash alone can't prove who sent something. Use HMAC or a signature.
4. **Comparing MACs with `==`.** Use `hmac.compare_digest` (or your language's constant-time compare).
5. **Verifying parsed JSON instead of the raw body.** Sign and verify the exact bytes that travelled.
6. **Trusting a hash from the same place as the file.** If one attacker controls both, the check proves nothing. Signed hash lists fix this.

## Check your understanding
<!-- bite: cd0b54f2-d5ad-40ff-b055-7a593b11544a -->

Try each one before you open the answer.

1. <!-- q: mcq id="7c6fe406" -->
   `sha256("invoice 100")` and `sha256("invoice 101")` are computed. How similar will the two hashes look?

   - [ ] They'll share most characters, differing only near the end.
   - [ ] They'll differ by exactly one character.
   - [x] They'll look completely unrelated, because one small change alters about half the output bits.
   - [ ] They'll be identical, because the inputs are nearly the same.

   <details><summary>Answer</summary>

   The avalanche effect: any change, even one digit, gives an output with no visible relationship to the first. That's why a hash can't be "nearly right" for an edited file.

   </details>

2. <!-- q: mcq id="f78323d7" -->
   A team wants to check that firmware files haven't been tampered with by an attacker. Which hash should they choose?

   - [ ] MD5, because it's fastest.
   - [ ] SHA-1, because it's widely supported.
   - [x] SHA-256, because MD5 and SHA-1 have practical collisions an attacker could use.
   - [ ] bcrypt, because it's the most secure hash.

   <details><summary>Answer</summary>

   An attacker could exploit a collision in MD5 or SHA-1 to make a malicious file match a trusted hash. SHA-256 has no known practical collisions. bcrypt is a deliberately slow password hash, the wrong tool for fingerprinting files.

   </details>

3. <!-- q: exact id="edb603d6" answer="64" -->
   A SHA-256 hash is 256 bits long. Written in hexadecimal, where each character stands for 4 bits, how many characters long is it?

   <details><summary>Answer</summary>

   64. 256 ÷ 4 = 64 hex characters.

   </details>

4. <!-- q: mcq id="a4725848" -->
   A webhook arrives with the header `X-Signature: sha256=…`. Your server checks it by computing plain `sha256(body)`, with no key, and comparing. Why is this worthless as protection?

   - [ ] SHA-256 is too slow for webhooks.
   - [x] Anyone can compute SHA-256 of any body, so an attacker can send a forged body with a matching hash.
   - [ ] The header can't hold a SHA-256 value.
   - [ ] Plain hashes can't be compared.

   <details><summary>Answer</summary>

   A plain hash needs no secret, so the attacker computes it for their forged body and sends both. Only an HMAC, made with a secret the attacker doesn't have, proves who sent the message.

   </details>

5. <!-- q: gap id="86d2a78b" answers="compare_digest|hmac.compare_digest" -->
   In Python, to compare a received HMAC with the expected one without leaking timing information, use `hmac.___`.

   <details><summary>Answer</summary>

   `hmac.compare_digest`. It takes the same time whatever the inputs, so an attacker can't learn how many leading bytes they got right.

   </details>

6. <!-- q: open id="6aefee5d" -->
   A project's website lists a SHA-256 next to each download. An attacker takes over the website. Explain why checking the hash no longer protects users, and what would.

   <details><summary>Answer</summary>

   The attacker can replace the file *and* change the listed hash to match it, so the check passes for the malicious file. A hash proves a file matches a list, not who made the list. The fix is a signature: the project signs the hash list with a private key kept off the website, and users verify it with the project's public key, which the attacker can't forge (lesson 05).

   </details>

## Practice — protect a webhook endpoint
<!-- bite: f952f296-e431-45e2-b3c6-86de78fff35b -->

**Task.** Add HMAC verification to a real endpoint in your own app (or a tiny Flask/Express app made for this).

1. Read the **raw** request body before any parsing.
2. Compute HMAC-SHA256 with a secret from an environment variable, and compare with the header in constant time.
3. Reject with `401` if the header is missing or wrong, and log the rejection.
4. Write tests for: a genuine webhook, a changed body, a wrong secret, and a missing header.

## Practice: when your endpoint is done
<!-- bite: 6e1c7491-ec6d-411f-b0ab-90ed3fb8c344 -->

Here is how you know the task is finished, plus a stretch step.

**Done when:** all four tests pass, and the secret is read from the environment, not written in the code. Record it in `cybersecurity/LIVE-RUNS-TODO.md`.

**Stretch.** Add replay protection: include a timestamp in the signed data, and reject webhooks older than five minutes. Then read your payment provider's (or GitHub's) webhook docs and compare their scheme with yours.

## Before moving on
<!-- bite: 413670d0-b012-4c4c-bf1a-6583bf05d7a8 -->

You can now list the properties of a cryptographic hash and see the avalanche effect, choose SHA-256 over MD5 and SHA-1, verify a download, and sign and verify a webhook with HMAC, comparing in constant time.

**Recap for later lookup:** hash = deterministic, one-way, collision-resistant, avalanche. SHA-256 (or SHA-3, BLAKE2/3); never MD5 or SHA-1 for security. Fast hashes for fingerprints, slow ones for passwords. `sha256sum -c` to verify. A plain hash proves matching, not authorship. HMAC = hash + secret key = integrity + authentication. Verify raw bytes; `hmac.compare_digest`; reject replays.

Next: [[cybersecurity/05-cryptography/04-asymmetric-encryption|asymmetric encryption]]. HMAC and AES both need a shared secret. The next lesson is how two strangers get one.

## Related
<!-- bite: dd4f0de0-0f7b-480a-b0e8-4bc03dbfb055 -->

- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]] — why passwords need slow hashes instead.
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|Digital signatures and PKI]] — proving authorship without a shared secret.
- [[dsa/02-data-structures/03-hash-maps|Hash maps]] — non-cryptographic hashing, for fast lookups instead of security.

## About this lesson
<!-- bite: 4eab9eb5-57e0-465a-a5ef-e4e1085fceca -->

**Level:** Intermediate. **Covers:** the four properties of a cryptographic hash, the avalanche effect with real SHA-256 values, broken hashes (MD5, SHA-1), fast versus password hashes, verifying downloads, HMAC, constant-time comparison, and a webhook-verification lab. **Where it sits:** lesson 3 of the [[cybersecurity/05-cryptography/index|Cryptography]] section. **Sources:** the original vault note, rebuilt with a runnable lab; the hashes and the HMAC in the sample output were computed for this lesson. `[reference]` — the lab hasn't been run end to end yet; tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
