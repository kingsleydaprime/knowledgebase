---
id: 40241352-3e32-457c-8918-6d64949fce58
---

# Cryptographic Attacks and Best Practices

**Cryptographic attacks almost never break the maths; they break everything around it: weak keys, predictable randomness, leaky error messages, reused nonces and secrets left lying in code.**

## Before you start
<!-- bite: 63b7c0d7-f08f-4601-83d1-738dbb61d198 -->

You should have:

- Worked through AES-GCM, hashing, key exchange and signatures → lessons [[cybersecurity/05-cryptography/02-symmetric-encryption|02]] to [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|05]].
- Python 3. The worked example uses only the standard library.

After this lesson you will be able to:

1. Say why brute-forcing a real key is hopeless, and when brute force works anyway.
2. Explain padding oracles, timing attacks and nonce reuse: attacks on how crypto is *used*.
3. Recover a password-reset token that was made with the wrong random generator, and fix it.
4. Manage keys properly: generate, store, rotate and, when one leaks, respond.

**Study route.** Kid version and §1–5, then the worked example, then the checklist. The checklist is the part to keep.

## What cryptographic attacks are
<!-- bite: 694eceaa-9cdb-4c7e-97ea-b35a97c45220 -->

Every lesson in this section ended with a version of "use it this way, not that way". This lesson is why. AES, SHA-256, X25519 and Ed25519 have survived decades of the world's best attacks. Real breaches involving cryptography nearly always come through a side door: a key guessed from a password, a random number that wasn't random, an error message that said too much, a key committed to GitHub.

You'll see each side door, then go through one yourself: a reset token made with Python's ordinary `random` module, recovered in a few hundred guesses. It closes the section with the list every review of crypto code should start from.

## The kid version
<!-- bite: 7b501885-6c69-4253-9745-039b84724a5a -->

Picture a bank vault with a door so thick no drill can get through. Robbers don't drill. They read the combination off a sticky note on the manager's desk. They notice the manager always picks his birthday. They listen to the clicks of the dial. They wait for the cleaner who props the door open.

The vault door is the maths. Everything else is how the vault is used, and that's where the robberies happen.

**Where the analogy stops working.** A real vault has one door. Software has thousands of small places to make one of these mistakes, often in code written years apart by different people, and one mistake is enough. That's why the answer is mostly "use a library that already avoids them", not "be careful".

## 1. Brute force — hopeless against keys, easy against people
<!-- bite: a9ceff91-970f-43e3-a417-90ae98941cdf -->

Brute force means trying every possible key. Against a real key, it's hopeless. A 128-bit AES key has 2¹²⁸ possibilities, about 3.4 × 10³⁸. Even at a trillion guesses per second, trying them all takes about 10¹⁹ years, nearly a billion times the age of the universe.

But brute force works the moment the *real* number of possibilities is small. A key made from the password `sunshine` doesn't have 2¹²⁸ possibilities; it has "every password in a leaked list". That's why your PDF from the ethical-hacking section fell in seconds despite AES-256, and why bcrypt and breach checks exist.

So the question is never "how long is the key?" but **"how many guesses would it really take?"** Human-chosen secrets, short codes and predictable random numbers all shrink that number, and the worked example shows the last one.

## 2. Attacks on how crypto is used
<!-- bite: 14a5410a-a9a6-4245-adab-efe0898c725b -->

These attacks leave the algorithm alone and go after the way it's used.

1. **Padding oracles.** A server decrypts CBC data and answers "bad padding" differently from "bad data", in its message or its timing. By sending thousands of altered ciphertexts and watching those answers, an attacker decrypts the data without the key. Real attacks on TLS and web frameworks came from exactly this. The fix: use AEAD like GCM, which rejects any altered ciphertext before looking at padding.
2. **Nonce reuse.** From lesson 02: the same key and nonce twice in GCM leaks how the two messages differ and lets tags be forged. Sony's PlayStation 3 signing key was extracted in 2010 because the same supposedly random value was used for every ECDSA signature.
3. **Downgrade attacks.** An attacker in the middle persuades both sides to use an old, weak protocol version. Turning old versions off, as you did with TLS 1.0 and 1.1, is the fix.

## 3. Side channels — leaks from the outside
<!-- bite: 91b3e5d4-4fd9-4cea-a3f2-d767e562731f -->

A **side channel** is information a computation gives away by *how* it runs, not what it outputs: how long it takes, how much power it draws, even the sound or radio noise it makes.

The one that matters most in everyday code is **timing**. You met it in lesson 03: comparing a MAC with `==` stops at the first wrong byte, so a guess with a correct first byte takes a tiny bit longer. Measure enough times and the right value comes out byte by byte. Crypto libraries are written to run in **constant time** for anything secret, and your code should use their comparison functions (`hmac.compare_digest`).

The rest, power and electromagnetic leaks, matter mostly for hardware: smart cards, phones, chips in cars. They're why secure chips exist. In application code, your job is simpler: don't write your own crypto, and you won't write your own side channel.

## 4. Randomness — the foundation everything stands on
<!-- bite: 25d9ce03-a7e4-46f1-8d4c-9c38ecbd3ef3 -->

Keys, nonces, salts, session IDs and reset tokens all need numbers an attacker can't predict. Most languages have two random generators, and only one is fit for this:

1. **A general-purpose generator**, like Python's `random` or JavaScript's `Math.random()`. It's built for games and simulations. Its output follows from a small starting value, the **seed**, so anyone who learns or guesses the seed can reproduce every number.
2. **A cryptographically secure generator (CSPRNG)**, like Python's `secrets`, Node's `crypto.randomBytes`, or the OS's `/dev/urandom`. It draws on unpredictable events collected by the operating system, and its output can't be predicted even from earlier output.

The classic bug is seeding the general one with the time. The time is easy to guess to within an hour, and an hour is only 3,600 seeds. That's the worked example.

## Terms used in this lesson
<!-- bite: 6924f126-e68d-40af-ac06-a500e8f2b012 -->

1. **Brute force**: This is trying every possible key or password until one works.
2. **Key space**: This is the number of possible keys. The real key space of a human-chosen password is far smaller than its length suggests.
3. **Padding oracle**: This is a system that reveals, by its errors or timing, whether decrypted data had valid padding, letting an attacker decrypt without the key.
4. **Side channel**: This is information leaked by how a computation runs, such as its timing or power use, rather than its output.

## Terms used in this lesson: randomness and keys
<!-- bite: 4557e672-dac6-43bf-a772-e6dcff8e2a57 -->

The rest of the terms are about random numbers and looking after keys.

5. **Seed**: This is the starting value a general-purpose random generator grows all its numbers from. Same seed, same numbers.
6. **CSPRNG (cryptographically secure pseudo-random number generator)**: The letters stand for those words. It's a random generator whose output can't be predicted, safe for keys and tokens.
7. **Secrets manager**: This is a service that stores keys and passwords, hands them to programs that need them, and logs who used them. Cloud providers and tools like Vault offer one.
8. **Key rotation**: This is replacing a key with a new one on a schedule, or straight away after a leak, so an old key's damage is limited.

## 5. Key management — the part that actually fails
<!-- bite: 9d599d1a-3702-4f83-b4ca-f93de73e1d12 -->

A perfect algorithm with a leaked key protects nothing. Keys have a life, and each stage has a rule:

1. **Generate** from a CSPRNG, never by hand and never from a password without a slow key-derivation function.
2. **Store** in a secrets manager or hardware module, never in source code, never in a committed config file, and not next to the data it protects.
3. **Rotate** on a schedule, so any one key protects a limited amount of data and time.
4. **Revoke and replace** the moment a key may have leaked.
5. **Destroy** retired keys, so old backups can't bring them back.

## 5. Key management: the key in git
<!-- bite: 70ff16ae-61f1-4a0b-877b-5ccb0ebf8b32 -->

One kind of leak happens far more than all the others.

The most common leak by far is a key committed to a git repository. Deleting it in a new commit doesn't help: it's still in the history, and bots scan GitHub for keys within minutes of a push. **A leaked key must be rotated, not just deleted.** Revoke it at the provider, issue a new one, then clean the history if you want to. Scanners like `gitleaks` find keys in a repository's history before attackers do.

## Worked example — recover a token made with `random`
<!-- bite: 8ba6d207-a960-4833-ac50-c2aaaa9cf47c -->

A password-reset feature makes its token with `random`, seeded with the current second. Save this as `weak_token.py`:

```python
# weak_token.py: a reset token made the wrong way, recovered by guessing the seed.
import random, secrets, time

def weak_token(seed: int) -> str:
    random.seed(seed)                        # seeded with a timestamp: the bug
    return "%032x" % random.getrandbits(128)

# Somewhere in the last hour, the server made a reset token for the victim.
issued_at = int(time.time()) - secrets.randbelow(3600)
victim_token = weak_token(issued_at)         # emailed to the victim; the attacker never sees it

# The attacker can't see the token, but can test guesses against the reset page.
# Here, "testing" is comparing; on a real site each guess is one request.
now = int(time.time())
for tries, guess in enumerate(range(now, now - 3601, -1), start=1):
    if weak_token(guess) == victim_token:
        print(f"recovered in {tries} tries: {weak_token(guess)}")
        break

print("the right way:", secrets.token_urlsafe(32))
```

## Worked example: what the attack shows
<!-- bite: 15a832a0-ab1a-48aa-8708-6cae0549d922 -->

**Predict first:** the token is 128 bits, 32 hex characters, the same size as an AES key. How many guesses will the attacker need at most? Then run `python3 weak_token.py`. A run while writing this lesson printed:

```text
recovered in 223 tries: 0b9bda88c280860336d19ba7c9e9835b
the right way: -wsGxDnafqcu05RiLFwGcvkFsrKsPGHkFDyf9Z48LxQ
```

Your number of tries will differ, but it can never be more than 3,601. The token *looked* like 128 random bits, but every bit came from the seed, and the seed was one of 3,601 seconds. That's §1's lesson again: the real key space was 3,601, not 2¹²⁸. A few thousand requests to a reset page take minutes, and then the attacker owns the account.

The fix is one line: `secrets.token_urlsafe(32)`, which comes from the operating system's CSPRNG and has no seed to guess. Rate limiting the reset endpoint and making tokens expire quickly are good extra layers, but they don't fix the token.

## A checklist for crypto in code
<!-- bite: 083a0b46-1e4c-476c-b1e9-c4965e7f3079 -->

Use this whenever you write or review code that touches cryptography.

1. **Use a maintained library's high-level interface.** Never implement an algorithm, a mode or padding yourself.
2. **Encrypt with AEAD**: AES-GCM or ChaCha20-Poly1305, with a fresh random nonce every time.
3. **Hash with SHA-256 or better** for fingerprints; **bcrypt or Argon2** for passwords. Never MD5 or SHA-1 for security.
4. **Authenticate messages** with HMAC or signatures, and compare in constant time.
5. **Make every key, token, salt and nonce with a CSPRNG** (`secrets`, `crypto.randomBytes`).
6. **Use current sizes and versions**: AES-128 or 256, RSA 2048+, or elliptic curves; TLS 1.2 and 1.3 only.
7. **Keep keys out of code and git**; use a secrets manager; scan for leaks; rotate when in doubt.

## Common pitfalls and traps
<!-- bite: bd6ab03f-b511-4635-ad37-a680b0959701 -->

1. **`random` or `Math.random()` for anything secret.** Use the CSPRNG.
2. **"The key is 256 bits, so it's safe."** Not if it came from a password, a timestamp or a short code. Ask how many guesses it would really take.
3. **Distinguishable error messages on decryption.** "Bad padding" versus "bad data" is a padding oracle. AEAD avoids the question.
4. **Deleting a leaked key instead of rotating it.** It's still in git history and possibly already copied. Revoke and replace.
5. **Writing your own crypto "just this once".** That's where side channels, nonce reuse and padding bugs come from.

## Check your understanding
<!-- bite: a04b70b1-41e6-4972-9506-4adab384a6b7 -->

Try each one before you open the answer.

1. <!-- q: mcq id="21fa1884" -->
   A file is encrypted with AES-256. The key was derived, with one fast hash, from the password `sunshine1`. Which attack is realistic?

   - [ ] None, because AES-256 has 2²⁵⁶ possible keys.
   - [x] A dictionary attack on the password: the real number of keys is "passwords in a leaked list", not 2²⁵⁶.
   - [ ] Breaking AES-256 mathematically.
   - [ ] A padding oracle, because AES uses padding.

   <details><summary>Answer</summary>

   The key can only be one of the keys made from likely passwords, and `sunshine1` is in every list. Brute force works against the real key space, which the password shrank to a few million. A slow key-derivation function and a strong passphrase would fix it.

   </details>

2. <!-- q: exact id="90703274" answer="86400" accept="86,400" -->
   A server makes session tokens with a general-purpose random generator seeded with the current time in whole seconds. An attacker knows a token was created on a particular day. At most, how many seeds must they try?

   <details><summary>Answer</summary>

   86,400: one per second in a day (24 × 60 × 60). However long the token looks, its real key space is just the number of possible seeds.

   </details>

3. <!-- q: mcq id="3a3637e1" -->
   A server decrypting CBC data returns "500: padding error" for some altered ciphertexts and "400: invalid data" for others. Why is that dangerous?

   - [ ] It slows the server down.
   - [x] It's a padding oracle: by sending many altered ciphertexts and reading which error comes back, an attacker can decrypt data without the key.
   - [ ] It reveals the key length.
   - [ ] It isn't dangerous; errors should be specific.

   <details><summary>Answer</summary>

   Different responses for bad padding let an attacker learn about the plaintext one byte at a time. The fix is AEAD (like GCM), which rejects any altered ciphertext with one identical error before padding is ever examined.

   </details>

4. <!-- q: gap id="8683c8b7" answers="secrets" -->
   In Python, the standard-library module to use for security tokens, instead of `random`, is ___.

   <details><summary>Answer</summary>

   `secrets`, for example `secrets.token_urlsafe(32)`. It draws from the operating system's CSPRNG, so there's no seed to guess.

   </details>

5. <!-- q: mcq id="176d47cb" -->
   A developer pushes a commit containing a live payment API key, notices ten minutes later, and pushes a second commit deleting it. What should happen next?

   - [ ] Nothing; the key is gone.
   - [ ] Make the repository private.
   - [x] Revoke the key at the provider and issue a new one, because it's still in git history and may already have been copied.
   - [ ] Rename the variable that held it.

   <details><summary>Answer</summary>

   The old commit still contains the key, and bots scan public repositories within minutes. Deleting it doesn't un-leak it. Rotate it: revoke the old key, issue a new one, store it in a secrets manager, and then clean the history if you like.

   </details>

6. <!-- q: open id="774772fc" -->
   AES, SHA-256 and Ed25519 are considered unbroken, yet breaches involving cryptography are common. Explain where those breaches actually come from, with two examples.

   <details><summary>Answer</summary>

   They come from how the cryptography is used, not the maths. Examples: keys derived from weak passwords (brute force over the real key space); predictable randomness, like tokens from a time-seeded `random`; nonce reuse in GCM or ECDSA (the PlayStation 3 key); padding oracles from distinguishable errors; timing leaks from `==` comparisons; and keys committed to git or stored next to the data. The fix is using well-reviewed libraries' high-level interfaces and managing keys properly.

   </details>

## Practice — audit a codebase for crypto mistakes
<!-- bite: b086c832-f253-463a-add4-cdf770398c95 -->

**Task.** Review one of your own projects with the checklist.

1. Search it: `grep -rnE 'Math\.random|random\.(random|randint|choice|getrandbits)|md5|sha1|ECB|==.*(signature|hmac|token)' src/` and judge each hit.
2. Run a secret scanner over the whole history: `gitleaks detect --source .` (install from its releases page). For anything real it finds, rotate the key.
3. Fix the worst finding, with a test.
4. Write a short note: each checklist item, and whether your project passes.

## Practice: when your audit is done
<!-- bite: c8a56f26-4298-43ec-9880-54c53ddeaa3b -->

Here is how you know the task is finished, plus a stretch step.

**Done when:** every grep hit is fixed or explained, gitleaks reports nothing live, and your note covers all seven checklist items. Record it in `cybersecurity/LIVE-RUNS-TODO.md`.

**Stretch.** Change `weak_token.py` so the seed is the time in *milliseconds*. How many seeds are in an hour now? Run it and time it. Is that a fix? (No; explain why, and what is.)

## Before moving on
<!-- bite: 876e8832-2d15-4f03-ad80-0b628c878138 -->

You can now explain why brute force fails against keys but works against people, describe padding oracles, nonce reuse, downgrades and timing side channels, break and fix a time-seeded token, and manage keys through their whole life.

**Recap for later lookup:** ask "how many guesses, really?", not "how long is the key?". AEAD avoids padding oracles. Never reuse a nonce. Constant-time comparisons. CSPRNG (`secrets`) for every key, token, salt and nonce; never `random`. Keys: generate, store in a secrets manager, rotate, revoke, destroy. A leaked key is rotated, not deleted. Use the seven-point checklist.

**The section, in one line:** lesson 01 mapped the goals, 02 to 05 gave you the tools (AES-GCM, hashes and HMAC, key exchange, signatures and certificates), and 06 showed that the tools rarely fail; the way they're used does.

Next: [[cybersecurity/06-attacks-and-threats/index|attacks and threats]], the wider world of how systems actually get breached.

## Related
<!-- bite: f2498bbf-052e-434c-9d68-cfaff648464b -->

- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]] — the password side of "how many guesses, really?".
- [[cybersecurity/02-ethical-hacking/10-pdf-and-document-security|PDF and document security]] — AES-256 defeated by a weak password, from the attacker's seat.
- [[cybersecurity/07-security-operations/index|Security operations]] — detecting leaked keys and responding to them.

## About this lesson
<!-- bite: bae44dca-2fa0-4277-9665-49b8c5e72f57 -->

**Level:** Advanced. **Covers:** brute force and real key spaces, padding oracles, nonce reuse, downgrade attacks, timing and other side channels, general versus cryptographically secure random generators, key management through its life, leaked keys in git, a seven-point checklist, and a lab that recovers a time-seeded reset token. **Where it sits:** lesson 6 of the [[cybersecurity/05-cryptography/index|Cryptography]] section, the practical close of the section. **Sources:** the original vault note, rebuilt with a runnable lab; the lab was run once while writing and its output is shown. Other commands are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
