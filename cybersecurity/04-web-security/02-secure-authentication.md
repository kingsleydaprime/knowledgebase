# Secure Authentication

Authentication is verifying that someone is who they claim to be — almost always the first thing an attacker targets, since bypassing it skips the need for almost any other vulnerability entirely (see the broken-authentication category in [[07-exploitation-concepts|exploitation-concepts]]). This note is the defensive counterpart: how to actually implement it well.

## Never store passwords in plaintext, and never use a plain fast hash either

Storing a password directly means a single database breach exposes every user's real password. Storing a plain, fast hash (MD5, SHA-256 alone) is barely better — these algorithms are *designed* to be fast, which means an attacker with the hash database can try billions of guesses per second (see [[08-common-tools|hashcat/John the Ripper]] for exactly this kind of cracking in action).

The fix is a **slow, purpose-built password hashing algorithm**: bcrypt, scrypt, or Argon2 (the current recommended default). These are deliberately, tunably slow and memory-hard, so that even with the full hash database, testing each password guess is expensive enough to make large-scale cracking impractical.

```python
# conceptual example using a purpose-built password hashing library
import bcrypt

password = b"user_password_here"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())   # salt is generated and stored alongside the hash automatically

bcrypt.checkpw(password, hashed)   # True if it matches, without ever needing to store or compare plaintext
```

## Salting — why two identical passwords shouldn't produce identical hashes

A **salt** is random data mixed into the password before hashing, unique per user, stored alongside the hash. Without it, two users with the same password get the exact same hash — visible to anyone with database access — and precomputed "rainbow table" lookups become effective against the whole database at once. With per-user salting, each password has to be attacked individually, even if two users happen to share a password. Modern libraries like bcrypt handle salting automatically, which is part of why using an established library instead of hand-rolling hashing matters.

## Multi-Factor Authentication (MFA)

Authentication based on a password alone relies entirely on "something you know" — MFA adds a second, independent factor: "something you have" (a phone generating a time-based code, a hardware key) or "something you are" (biometrics). The security value comes specifically from independence — a leaked/guessed password alone is no longer sufficient, since the attacker also needs the second factor, which typically requires a completely different compromise (physical device access, for instance).

```
TOTP (Time-based One-Time Password) — the standard behind most "authenticator app" codes:
shared_secret + current_time_window -> a 6-digit code, regenerated every 30 seconds,
independently computable by both the server and the user's authenticator app without any network round-trip.
```

## Session management — staying authenticated after login

Once authenticated, a **session token** (commonly stored in a cookie) represents "this request comes from an already-authenticated user," so the user doesn't have to re-authenticate on every single request. Getting this right matters as much as the login step itself:

- Session tokens need to be long, random, and unguessable (predictable session IDs are a direct account-takeover vector).
- Cookies holding session tokens should be marked `HttpOnly` (inaccessible to JavaScript, mitigating token theft via XSS — see [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]) and `Secure` (only ever sent over HTTPS, see [[03-https-and-tls|https-and-tls]]).
- Sessions should expire, and critically, should be invalidated server-side on logout — a session token that still works after "logout" because only the client-side cookie was cleared is a common, subtle bug.

## JWTs — a common but frequently misused alternative

JSON Web Tokens are a popular way to represent authentication state without server-side session storage — the token itself carries the claims (user ID, roles), cryptographically signed so tampering is detectable. Common pitfalls: accepting a token with `"alg": "none"` (some libraries historically trusted this, allowing an attacker to submit an unsigned, self-asserted token), and simply not validating the signature at all on the server side before trusting the token's contents. A JWT's claims should never be trusted unless the signature has been verified against the expected algorithm and key.

## Gotchas

- Rolling your own authentication/hashing scheme instead of using a well-vetted library or identity provider is one of the most common sources of serious vulnerabilities in this area — this is a place where "don't reinvent it yourself" is genuinely the professional default, not laziness.
- Password complexity *requirements* (forcing special characters, frequent forced rotation) are increasingly considered less effective than simply requiring length and checking against known-breached password lists — current guidance (NIST) has moved away from the older complexity-rule-heavy approach.
- Rate limiting login attempts is what actually stops online brute-force guessing (as opposed to the offline cracking covered in [[08-common-tools|common-tools]]) — an authentication endpoint with no attempt limiting is directly exploitable regardless of how strong the hashing is.

## Related
- [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]
- [[03-https-and-tls|https-and-tls]]
- [[07-exploitation-concepts|exploitation-concepts]]
- [[03-hashing-and-integrity|hashing-and-integrity]] — general-purpose hashing vs. the deliberately slow password hashing covered above
- [[06-cryptographic-attacks-and-best-practices|cryptographic-attacks-and-best-practices]] — CSPRNGs, key management, why "don't roll your own crypto" applies here too
