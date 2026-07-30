# Arete Backend — Auth, Properly

Split out from the original single-file `backend-learning.md`. Covers bcrypt vs SHA-256 hashing
and the two-token JWT scheme.

---

## Part 5 — Auth, Properly

### Passwords: bcrypt. Reset tokens: SHA-256. Different jobs.

```ts
// Passwords — bcrypt, deliberately SLOW (that's the security):
const hash = await bcrypt.hash(password, 10);
const ok = await bcrypt.compare(password, user.passwordHash);
```

Slow hashing means a stolen database resists brute force. But Arete uses **SHA-256** for password-reset tokens — why the "weaker" hash?

Because of the lookup problem: to find *which user* a reset token belongs to, you must search by the token's hash. bcrypt produces a different hash every time (random salt), so you can't `WHERE token_hash = ?` — you'd have to bcrypt-compare against every row. SHA-256 is deterministic → indexable lookup. And the input isn't a weak human password; it's a 256-bit random token, so slow hashing adds nothing.

**Lesson: security decisions follow from the data's properties, not from "use the strongest thing everywhere."**

### JWT: two tokens

- **Access token** (15 min): sent on every request; short life limits damage if stolen.
- **Refresh token** (30 days): only ever sent to `/auth/refresh` to mint new access tokens.

Server-side, the guard verifies the signature — no DB hit per request. That's the JWT trade: stateless speed, at the cost of not being able to revoke an access token before it expires (hence the short TTL).

---

