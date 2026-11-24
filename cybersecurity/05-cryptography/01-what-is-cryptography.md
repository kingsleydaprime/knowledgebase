---
id: 35707b17-03c5-40cf-82ce-3b86e2c8a8a7
---

# What Is Cryptography

**Cryptography is using maths to keep data secret, to detect any change to it, and to prove who sent it, even when an attacker can see everything you send.**

## Before you start
<!-- bite: 01a3f6d0-9ca9-4cee-bc13-e0a2b750b808 -->

You should have:

- A terminal with `base64`, `sha256sum` and `openssl` (all standard on Linux).
- Met the CIA triad → [[cybersecurity/01-fundamentals/02-cia-triad|the CIA triad]].

After this lesson you will be able to:

1. Name the four goals cryptography serves, and say which one a given tool provides.
2. Tell symmetric from asymmetric cryptography, and say why real systems use both.
3. Explain Kerckhoffs's principle, and why a secret algorithm is a warning sign.
4. Tell encoding, encryption and hashing apart on sight, and decode a JWT to prove encoding hides nothing.

**Study route.** Kid version and §1–4, then the worked example in your terminal. It takes ten minutes.

## What cryptography is
<!-- bite: 15f9639b-7a00-4179-8bd6-569e604bde82 -->

You've already leaned on cryptography all through this course without stopping to look at it. The WireGuard tunnel to your VPS, the HTTPS certificate, the bcrypt password hashes, the signature on a JWT: each is cryptography doing one particular job.

This section opens the box. This first lesson is the map: the four jobs cryptography does, the two families of tools, the one rule every good design follows, and the three words people mix up most. The next five lessons take the tools one at a time, and every one has something you run.

## The kid version
<!-- bite: e508bec3-eb98-4e6c-ac6e-955b3775b6ad -->

Imagine passing notes in class with a friend. You want three things. The teacher who grabs the note can't read it, so you write it in a code only you two know. Nobody can change "meet at 3" into "meet at 4" without you noticing, so you add a check mark that only works for the real words. And your friend knows the note really came from you, so you sign it in a way nobody else can copy.

Cryptography is those three tricks, done with maths instead of made-up codes, so that even a very clever teacher with a supercomputer can't break them.

**Where the analogy stops working.** A made-up code is safe only while nobody knows how it works. Real cryptography is the opposite: everyone knows exactly how it works, and it's still safe, because the only secret is a key, a long random number. That's §3, and it's the most important idea in this section.

## 1. The four goals
<!-- bite: 7a9136ea-0d3e-4f3c-aa9f-cd60dec7e083 -->

Every cryptographic tool serves at least one of four goals. When you meet a new tool, ask which one it provides; that question clears up most confusion.

1. **Confidentiality** — only the right people can read it. Tool: **encryption**.
2. **Integrity** — any change is detected. Tools: **hashes** and **MACs** (message authentication codes).
3. **Authentication** — you can tell who sent it, or that a server is who it says. Tools: MACs, **digital signatures**, certificates.
4. **Non-repudiation** — the sender can't later deny sending it. Tool: digital signatures only, because only one person holds the signing key.

Notice what's missing from encryption alone: it hides the message, but it doesn't stop someone changing the scrambled bytes. That's why modern encryption (lesson 02) always comes with an integrity check built in.

## 2. Two families: one key, or a pair
<!-- bite: 3e2dce87-192b-4825-ad1a-642dd8edf51d -->

Cryptography's tools come in two families, and the difference is the key.

**Symmetric** cryptography uses one key for both locking and unlocking. It's very fast, and it's what encrypts almost every byte you send. Its weakness: both sides need the same secret key first, and you can't send that key over the network you're trying to protect.

**Asymmetric** (public-key) cryptography uses a **key pair**: a public key you can give to anyone, and a private key only you hold. What one locks, only the other unlocks. It solves the "how do we agree a key?" problem, but it's far slower.

So real systems use both. The slow asymmetric part runs once at the start, to agree a key safely; the fast symmetric part carries all the data. Your WireGuard tunnel does exactly this, and so does every HTTPS connection. Lesson 04 shows it step by step.

## 3. Kerckhoffs's principle — only the key is secret
<!-- bite: 8b539754-4c77-4868-acbd-8489bf32f081 -->

In the 1880s, Auguste Kerckhoffs wrote down the rule modern cryptography still follows: **a system should stay secure even if everything about it except the key is public.**

So the algorithms are published. AES, the cipher protecting your disk and your HTTPS traffic, was chosen in an open competition, and the world's cryptographers have spent over twenty years trying to break it. They haven't. That public attack-testing is exactly why you can trust it.

A secret algorithm has the opposite problem. Nobody outside has tested it, and its "security" vanishes the day someone reverse-engineers it, which they always eventually do. So when a product boasts about its "proprietary encryption", treat it as a warning sign, not a feature. This is also the root of the rule you'll meet in lesson 06: **don't invent your own crypto.**

## Terms used in this lesson
<!-- bite: 2376da96-ed09-4996-9c06-5a0e754b8728 -->

1. **Plaintext and ciphertext**: Plaintext is the readable data; ciphertext is the scrambled version encryption produces.
2. **Key**: This is the secret value that controls the scrambling. With the right key you can reverse encryption; without it you can't.
3. **Cipher**: This is also known as an **encryption algorithm**. It's the published method that turns plaintext and a key into ciphertext, like AES.
4. **Symmetric and asymmetric**: Symmetric means one shared key does both jobs. Asymmetric means a key pair: a public key to share and a private key to keep.

## Terms used in this lesson: the three that get mixed up
<!-- bite: d7fa5660-f4f1-4025-b677-9c1ceb8c0aa8 -->

The rest of the terms are the three words §4 is about, plus the token you'll decode.

5. **Encoding**: This is changing how data is written so it fits somewhere, like Base64 for putting bytes into text. There's no key, so anyone can reverse it.
6. **Encryption**: This is scrambling data with a key so only someone with the right key can reverse it.
7. **Hashing**: This is turning data into a short fixed-size fingerprint that can't be reversed at all, with no key.
8. **JWT (JSON Web Token)**: The letters stand for those words. It's a login token made of three Base64 parts: a header, the data, and a signature.

## 4. Encoding, encryption, hashing — not the same thing
<!-- bite: e0c7fec0-eade-47a9-974d-01883bf53108 -->

These three get confused constantly, and the confusion causes real breaches. The quickest test is two questions: **is there a key, and can it be reversed?**

1. **Encoding**: no key, reversible by anyone. It's for compatibility, never for security. "I Base64'd the password" means "I stored the password".
2. **Encryption**: a key, reversible only with that key. For data you need back later.
3. **Hashing**: no key, not reversible by anyone. For checking data, like a password or a download, without keeping the original.

Remember this one: **encoding hides nothing.** The worked example proves it with a real token.

## Worked example — encode, encrypt, hash
<!-- bite: 48e6d820-bf04-46e7-b7e7-30db4c513767 -->

Run these in your terminal. **Predict first:** which of the three outputs can you turn back into `password1` without knowing any secret?

```bash
echo -n 'password1' | base64                 # encoding
echo -n 'password1' | sha256sum              # hashing
echo -n 'password1' | openssl enc -aes-256-cbc -pbkdf2 -a -pass pass:lab-key   # encryption
```

The first prints `cGFzc3dvcmQx`. Now reverse it, with no secret at all:

```bash
echo 'cGFzc3dvcmQx' | base64 -d              # prints: password1
```

The hash can't be reversed by anyone; the only attack is guessing, as you did with hashcat. The encrypted output reverses only with the key: add `-d` and `-pass pass:lab-key` to the same `openssl` command to get `password1` back, or try a wrong key and watch it fail.

## Worked example: a JWT is encoded, not encrypted
<!-- bite: 652a0343-8d18-46da-b45a-9776a6045252 -->

Here's a JWT of the kind lesson 02 of the web-security section talked about. The dots separate its three parts:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZGEiLCJyb2xlIjoibWVtYmVyIn0.GdMFl6-8ukUQI1rg7ekLOBhHhrTRDefAbagY0MIUg-0
```

Decode the middle part, which is the data:

```bash
echo 'eyJzdWIiOiJhZGEiLCJyb2xlIjoibWVtYmVyIn0' | base64 -d     # prints: {"sub":"ada","role":"member"}
```

Anyone holding the token can read who it's for and their role. A JWT's data is **encoded, not encrypted**. What protects it is the third part, the signature (an HMAC, lesson 03): you can *read* the data, but you can't *change* `member` to `admin` without the signature failing. So never put a secret inside a JWT's data, and always check its signature.

## Common pitfalls and traps
<!-- bite: df3dc74d-52c3-4736-86b0-226dee764894 -->

1. **"It's Base64'd, so it's safe."** Base64 is encoding. Anyone reverses it in one command.
2. **Thinking encryption gives integrity.** Encryption alone hides data; it doesn't stop tampering. Use a mode with a built-in check (lesson 02).
3. **Trusting secret algorithms.** "Proprietary encryption" has had no public testing. Use published, standard algorithms.
4. **Hashing what you need back.** If you'll need the data again (a card number to charge later), hashing is the wrong tool; it can't be reversed. Encrypt it.
5. **Blaming the maths.** Almost every real crypto failure is a leaked key, a bad random number, or a misused library, not a broken algorithm. That's lesson 06.

## Check your understanding
<!-- bite: 366607bd-3de9-444a-af1c-a34405f6a148 -->

Try each one before you open the answer.

1. <!-- q: mcq id="dc5a71d4" -->
   An app stores users' passwords as `cGFzc3dvcmQx`, the Base64 of `password1`. The developer says they're "encrypted". What is actually true?

   - [ ] They're encrypted, because they can't be read directly.
   - [x] They're only encoded: anyone can decode them with no key, so the passwords are effectively stored in plain text.
   - [ ] They're hashed, so they can't be reversed.
   - [ ] They're safe as long as the database is private.

   <details><summary>Answer</summary>

   Base64 is encoding: no key, reversible by anyone with `base64 -d`. Passwords should be hashed with a slow password hash like bcrypt, which can't be reversed at all.

   </details>

2. <!-- q: mcq id="f9e89e17" -->
   A software download page lists the SHA-256 fingerprint of the file. Which goal does checking that fingerprint serve?

   - [ ] Confidentiality
   - [x] Integrity
   - [ ] Non-repudiation
   - [ ] Availability

   <details><summary>Answer</summary>

   Integrity: if the file you downloaded hashes to the same value, it hasn't been changed. It doesn't hide the file, and a plain hash doesn't prove who published it; a signature would do that.

   </details>

3. <!-- q: gap id="f328e74f" answers="key" -->
   Kerckhoffs's principle says a cryptographic system should stay secure even if everything about it is public except the ___.

   <details><summary>Answer</summary>

   The key. Algorithms like AES are published and tested in the open; the only secret is the key.

   </details>

4. <!-- q: mcq id="0af4dfae" -->
   A JWT's middle part decodes to `{"sub":"bayo","role":"member"}`. An attacker edits it to say `"role":"admin"`, re-encodes it, and sends the token. Why does a correctly built server reject it?

   - [ ] The data is encrypted, so the edit makes it unreadable.
   - [ ] Base64 can't encode the word "admin".
   - [x] The signature was made over the original data, so it no longer matches the edited data.
   - [ ] Servers ignore the role field.

   <details><summary>Answer</summary>

   The data is only encoded, so the attacker can read and edit it easily. What stops them is the signature: it was computed over the original header and data with a key they don't have, so a changed payload fails verification. That's integrity and authentication, not confidentiality.

   </details>

5. <!-- q: mcq id="8b35c2b3" -->
   Which goal can a digital signature give that a shared-key MAC can't?

   - [ ] Confidentiality
   - [ ] Integrity
   - [x] Non-repudiation
   - [ ] Availability

   <details><summary>Answer</summary>

   Non-repudiation. With a MAC, both sides hold the same key, so either could have made it, and the sender can deny it. A signature can only be made with a private key one person holds.

   </details>

6. <!-- q: open id="854777a5" -->
   A vendor advertises its product as "protected by our own secret, proprietary encryption algorithm". Explain, using Kerckhoffs's principle, why that should make you less confident, not more.

   <details><summary>Answer</summary>

   A good system is secure even when the algorithm is public, so secrecy of the algorithm adds nothing real. A secret algorithm hasn't been attacked by the world's cryptographers the way AES has, so its weaknesses are unknown, and once someone reverse-engineers it (which tends to happen) any security that depended on the secret is gone. Published, publicly tested algorithms are the ones to trust.

   </details>

## Practice — find the crypto in your own setup
<!-- bite: c7189a91-c168-409d-a26c-babd355d9e50 -->

**Task.** List every piece of cryptography you already use, and name the goal each one serves.

1. Start with your own lab: the WireGuard tunnel, the HTTPS certificate on your VPS, bcrypt password storage, a JWT if your app uses them. If you haven't built those yet, use your phone and laptop: messaging app, disk encryption, Wi-Fi, banking app.
2. For each one, write: what it protects, which of the four goals it serves, and whether it's symmetric, asymmetric, hashing or a mix.
3. Find one place something is *encoded* and might be mistaken for encryption (a JWT, a Base64 value in a config file, a cookie). Decode it.

## Practice: when your list is done
<!-- bite: 6f950f33-6694-4632-bc9e-14b3d884b7c6 -->

Here is how you know the task is finished.

**Done when:** you have at least six entries, each with a goal and a family, and one decoded value with a sentence on whether it should have been encrypted instead.

## Before moving on
<!-- bite: e757065e-94cb-4071-9ee8-216220d6cb40 -->

You can now name the four goals of cryptography and match tools to them, tell symmetric from asymmetric and say why systems use both, explain Kerckhoffs's principle, and tell encoding, encryption and hashing apart, including decoding a JWT.

**Recap for later lookup:** confidentiality (encryption), integrity (hashes, MACs), authentication (MACs, signatures, certificates), non-repudiation (signatures only). Symmetric = one key, fast; asymmetric = key pair, slow; real systems use both. Only the key is secret. Key? Reversible? Encoding: no, yes. Encryption: yes, with the key. Hashing: no, never.

Next: [[cybersecurity/05-cryptography/02-symmetric-encryption|symmetric encryption]], the fast family that carries almost every encrypted byte you send.

## Related
<!-- bite: bfa94b9f-18c0-4255-bad3-f5b31bddce76 -->

- [[cybersecurity/01-fundamentals/02-cia-triad|The CIA triad]] — where confidentiality and integrity come from.
- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]] — hashing and JWTs, applied.
- [[mathematics/02-discrete-math/08-number-theory-and-modular-arithmetic|Number theory]] — the maths underneath the asymmetric family.

## About this lesson
<!-- bite: 0e248d1e-f109-456f-aee6-2988b494ef88 -->

**Level:** Beginner. **Covers:** the four goals (confidentiality, integrity, authentication, non-repudiation), symmetric versus asymmetric and why systems use both, Kerckhoffs's principle, and encoding versus encryption versus hashing, with a terminal lab that decodes a real JWT. **Where it sits:** lesson 1 of the [[cybersecurity/05-cryptography/index|Cryptography]] section, the map for the five lessons after it. **Sources:** the original vault note, rebuilt with a hands-on terminal lab; the JWT and its decoded payload were computed for this lesson. `[reference]` — commands not yet run live; tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
