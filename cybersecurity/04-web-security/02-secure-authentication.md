---
id: cf472dee-209a-484a-bdc2-637f5b69159b
---

# Secure Authentication

**Authentication is how an app checks that someone is who they say they are, and secure authentication is doing that check in a way that survives a stolen database, a guessing script and a phished password.**

## Before you start
<!-- bite: 8821ec54-562f-4794-94fe-996ac9c85514 -->

You should have:

- Cracked a hash offline with a wordlist → [[cybersecurity/02-ethical-hacking/10-pdf-and-document-security|PDF and document security]]. This lesson is the defender's side of that attack.
- Python 3, and `hashcat` installed (`sudo dnf install hashcat`), with `rockyou.txt` from that lesson.
- Met sessions and tokens → [[backend/05-auth/01-authentication-flows|authentication flows]].

After this lesson you will be able to:

1. Explain why passwords are stored with a slow, salted hash, and what that does and doesn't protect.
2. Seed a database of dummy accounts, crack it with hashcat, and measure the difference bcrypt makes.
3. Say what actually stops online guessing, credential stuffing and phished passwords.
4. Name the session and JWT mistakes that undo a good login.

**Study route.** Kid version and §1–5, then the worked example. It runs on your laptop; the accounts are fake people you make up.

## What secure authentication is
<!-- bite: 3f85c32b-27d5-4020-8b33-e57ff02465b7 -->

Remember lesson 07 of the ethical-hacking section? One SQL injection on Juice Shop's login, and you were admin. Lesson 01 of this section fixed that bug. But a login can fail in quieter ways: the database leaks and every password is cracked by morning, a script tries a million passwords against your login, or a user types their password into a fake site.

Attackers love the login, because getting past it skips almost every other defence. This lesson goes through the ways it breaks, one at a time. The centrepiece is the one you've already done from the attacker's side: cracking stored passwords. This time you build the database, choose how it's stored, and watch what the attacker gets.

## The kid version
<!-- bite: 0b499ff6-ec70-4df2-96ec-fb0200173197 -->

Imagine a club that keeps a notebook of every member's secret password. If a thief steals the notebook, they can walk in as anyone. So the club gets clever: instead of the password, it writes down what the password looks like after going through a slow, messy kitchen blender. At the door, you say your password, they blend it, and check it matches the notebook.

A thief who steals that notebook only has blended mush. To find a password, they must guess, blend, and compare, again and again. If the blender takes a whole second per guess, guessing a million passwords takes eleven days, for each member.

**Where the analogy stops working.** The slow blender protects good passwords, not bad ones. If your password is "password1", it's one of the first guesses on every thief's list, and they get it on try number three no matter how slow the blender is. Slow hashing buys time; it can't fix a password everybody guesses.

## 1. Never store the password — store a slow hash
<!-- bite: 74c359b6-d7a5-4907-8902-333996276087 -->

When the database leaks, and you should plan as if it will, the password column is the prize. Storing the password itself gives every account away instantly. And people reuse passwords, so you've also given away their email and bank logins.

The fix has three parts, and you need all three:

1. **Hash it.** A hash is a one-way scramble: easy to compute from the password, impossible to reverse. At login you hash what was typed and compare.
2. **Make the hash slow.** Ordinary hashes like MD5 and SHA-256 are built to be *fast*; a graphics card can try billions of them a second. Password hashes, like **bcrypt** and **Argon2**, are built to be slow on purpose, with a cost setting you turn up as computers get faster.
## 1. Never store the password: the salt
<!-- bite: b7631aa7-8f3a-4757-ad9e-ce701bd908b4 -->

The third part deals with users who pick the same password.

3. **Salt it.** A salt is a random value made fresh for each user and mixed in before hashing. Two users with the same password now get different hashes, so the attacker can't crack them both with one guess, or look them up in a precomputed table.

bcrypt and Argon2 do the salting for you and store the salt inside the hash. That's one of many reasons to use the library and never invent your own scheme.

## 2. What a slow hash buys, in numbers
<!-- bite: 0d644571-acdf-4421-acc0-7caa70bfbd62 -->

Here's the difference, with round numbers. Say an attacker's machine tries SHA-256 at 1 billion guesses a second, and bcrypt at cost 12 at 100 guesses a second. The `rockyou.txt` list has about 14.3 million passwords.

Trying the whole list against **SHA-256**: 14.3 million ÷ 1 billion ≈ 0.014 seconds. And with no salt, that one pass cracks every user in the database at once.

Trying the whole list against **bcrypt**: 14.3 million ÷ 100 = 143,000 seconds, about 40 hours, *per user*, because every user has their own salt.

So for a password somewhere in the middle of the list, bcrypt turns "instant" into "days per account". For a password at the top of the list, like `password1`, both fall in under a second. That's why §3 exists.

## Terms used in this lesson
<!-- bite: b8fb46be-7e4f-4a4e-8b5e-20478a9b0688 -->

1. **Authentication**: This is checking who someone is. **Authorization** is the different question of what they're allowed to do.
2. **Hash**: This is a one-way scramble of some data into a fixed-length value. You can check a guess against it, but you can't turn it back into the password.
3. **Salt**: This is a random value, different for every user, mixed into the password before hashing and stored next to the hash.
4. **Password hashing function**: This is a hash built to be slow and tunable, like bcrypt or Argon2. Its **cost** (or work factor) sets how slow; for bcrypt, each +1 doubles the work.

## Terms used in this lesson: attacks and factors
<!-- bite: e4a8d546-229f-4610-979e-4af3af6be189 -->

The rest of the terms name the attacks on a login and the defences against them.

5. **Credential stuffing**: This is trying username and password pairs leaked from *other* sites against yours, betting that people reuse passwords.
6. **Rate limiting**: This is capping how many attempts a client may make in a period, so online guessing becomes slow.
7. **MFA (multi-factor authentication)**: The letters stand for those words. It's requiring a second, different kind of proof, like a code from your phone, as well as the password.
8. **TOTP (time-based one-time password)**: The letters stand for those words. It's the 6-digit code an authenticator app shows, computed from a shared secret and the current 30-second window.

## 3. Weak passwords — stop them at the door
<!-- bite: e65fe182-5578-4c98-ae9d-e908ea96373a -->

Slow hashing can't save `password1`. So stop people choosing it.

Current guidance (from NIST, the US standards body) is short, and it surprised people when it came out:

1. **Require length, not puzzles.** At least 8 characters, and allow long ones (64 or more). Forced symbols just produce `Password1!`.
2. **Check new passwords against breached lists.** If it appears in a known leak, refuse it and say why. This one rule removes the passwords at the top of every cracking list.
## 3. Weak passwords: what not to force
<!-- bite: 55999155-e63b-4aa4-896e-ad7936a304dc -->

The last two rules are about what *not* to make users do.

3. **Don't force regular changes.** Forced rotation produces `Summer2026!`, then `Autumn2026!`. Change only when there's a sign of compromise.
4. **Allow paste and password managers.** The best password is one the user never has to remember.

That covers stored passwords. The next three sections cover attacks on a login that's running.

## 4. Online guessing and credential stuffing
<!-- bite: 5ccb12db-b347-4d11-a33d-b14640827586 -->

Not every attacker steals your database. Many just use your login form, sending guess after guess. Two shapes:

1. **Brute force on one account**: many passwords, one username.
2. **Credential stuffing**: one leaked password each, across thousands of usernames. Each account sees only one or two attempts, so per-account lockouts never trigger.

**Rate limiting** is the main defence: cap attempts per IP and per account, and slow down after failures. Be careful with hard lockouts: "lock after 5 failures" lets anyone lock your users out on purpose. Slowing down, adding a challenge, or asking for the second factor works better.

The detection half: log every failed login with username and source IP. A burst of failures across *many* usernames from a few IPs is credential stuffing, and that's exactly the pattern the SIEM from [[cybersecurity/03-network-security/04-intrusion-detection-and-prevention|intrusion detection]] is built to correlate.

## 5. MFA, and the password that was phished
<!-- bite: 4d4c712b-8dbb-4fea-977d-b4eaf103ae95 -->

A user types their correct password into a fake login page. Your hashing, your rate limit, your breach check: none of it helps, because the attacker now has the real password.

**MFA** is the answer. A second factor of a different kind, something you *have* (a phone, a security key) as well as something you *know*, means the password alone is no longer enough.

They aren't equally strong:

1. **SMS codes**: better than nothing, but a phone number can be stolen by a SIM swap.
2. **TOTP apps**: much better, but a convincing fake site can ask for the code too and use it within the 30 seconds.
3. **Passkeys and security keys (WebAuthn)**: the key checks the website's real address before answering, so a fake site gets nothing. These are phishing-resistant, the strongest of the three.

## 6. After login — sessions and tokens
<!-- bite: 4a7b9e89-f68c-42ee-be87-694338c44487 -->

Logging in once creates a **session**: a token, usually in a cookie, that says "this browser already proved who it is". A perfect login is wasted if the session is weak. The rules:

1. **The token is long and random.** Generated by a secure random source, never a counter or a timestamp.
2. **Make a new session ID at login.** If you keep the one the browser had before, an attacker who planted it is now logged in as the user (session fixation).
3. **Logout kills it on the server.** Deleting the cookie isn't enough; a copied token would still work.
4. **The cookie has `HttpOnly`, `Secure` and `SameSite`.** That's [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|lesson 04]].

## 6. After login: JWTs
<!-- bite: f52e2a37-1e56-4639-9cb9-0d5aa92de251 -->

Some apps use a different kind of token, with rules of its own.

**JWTs** carry the user's details inside a signed token instead of a server-side session. Two rules matter most: always verify the signature, with an algorithm *you* choose rather than the one the token claims, and never accept `"alg": "none"`. And since a JWT can't easily be cancelled before it expires, keep its lifetime short. [[backend/05-auth/01-authentication-flows|Authentication flows]] compares the two approaches.

## Worked example — seed a database of dummy accounts
<!-- bite: 33e16a64-3375-495e-9cc8-0127920c6aba -->

This is tier 3 of your owned-target lab: a database of people who don't exist, so cracking it harms nobody. Install the library with `pip install bcrypt`, then save this as `seed_users.py`:

```python
# seed_users.py: a throwaway database of dummy accounts, stored two ways.
import hashlib, sqlite3, bcrypt

USERS = {"ada": "sunshine", "bayo": "password1", "chidi": "iloveyou",
         "dami": "sunshine", "efe": "correct-horse-battery-staple"}

db = sqlite3.connect("dummy.db")
db.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, fast TEXT, slow TEXT)")
for name, password in USERS.items():
    fast = hashlib.sha256(password.encode()).hexdigest()                    # wrong: fast, unsalted
    slow = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()  # right: slow, salted
    db.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (name, fast, slow))
db.commit()
```

Run it with `python3 seed_users.py`, then look at what a thief would steal: `sqlite3 dummy.db "SELECT name, fast FROM users"`.

## Worked example: what the stolen table shows
<!-- bite: 2dec8e02-b95b-4161-a8b6-d469042b94d5 -->

**Predict first:** before you crack anything, what can you already learn from the `fast` column?

Look at `ada` and `dami`. Their `fast` hashes are identical, because they chose the same password and there's no salt. The thief knows two people share a password before guessing at all. Now compare their `slow` hashes: completely different. Each starts with `$2b$12$`, the bcrypt version and the cost of 12, followed by that user's own salt and the hash.

That's §1 made visible. Without salt, equal passwords leak each other. With salt, every user is a separate puzzle.

## Worked example: crack both columns
<!-- bite: ab16bb73-143a-4bcc-a808-066e9878b6b7 -->

Export each column to a file and point hashcat at it. Mode `1400` is SHA-256; mode `3200` is bcrypt.

```bash
sqlite3 dummy.db "SELECT fast FROM users" > fast.txt
sqlite3 dummy.db "SELECT slow FROM users" > slow.txt

hashcat -m 1400 fast.txt /usr/share/wordlists/rockyou.txt
hashcat -m 3200 slow.txt /usr/share/wordlists/rockyou.txt
hashcat -b -m 1400; hashcat -b -m 3200       # benchmark: guesses per second for each
```

Your speeds will differ (a laptop CPU is far slower than a cracking rig), but the gap is what matters. On the SHA-256 file, hashcat finishes the whole list in moments and cracks four of the five accounts. On the bcrypt file, the benchmark is thousands of times slower, and the estimate for the full list runs to hours or days.

## Worked example: what the cracking proves
<!-- bite: 4480f2a6-950e-4ca5-9427-730fd180de79 -->

Look at *which* passwords fell, not just how fast.

1. `sunshine`, `password1` and `iloveyou` are near the top of `rockyou.txt`. They fall against **both** files, bcrypt included, in seconds, because hashcat tries them almost first. Slow hashing can't save a password everyone guesses. That's why §3 says to block breached passwords at sign-up.
2. `correct-horse-battery-staple` falls against **neither**. It's long, and it isn't in the list.
3. The gap between the two files is what protects everyone in between: a password ranked in the millions on the list is found in moments in the SHA-256 file, and takes days per account in the bcrypt file.

That's the honest picture. Slow, salted hashing protects the middle. Breach checks remove the top. Length protects the rest.

## Common pitfalls and traps
<!-- bite: df0ba464-1069-49d3-a8a1-903ba4b7a702 -->

1. **Fast hashes for passwords.** MD5, SHA-1 and SHA-256 alone are cracking-friendly by design. Use bcrypt or Argon2, through a library.
2. **Rolling your own.** "SHA-256 a thousand times with a secret" is a scheme nobody has reviewed. Authentication is the place to use the well-tested library or identity provider.
3. **Hard lockouts.** "5 failures and the account is locked" hands attackers a way to lock out every user. Slow down and challenge instead.
4. **Telling attackers which half was wrong.** "No such user" versus "wrong password" lets them list your users. Say "username or password is incorrect" for both.
5. **Logout that only deletes the cookie.** The session must be ended on the server.
6. **Trusting a JWT before checking its signature**, or letting the token choose its own algorithm.

## Check your understanding
<!-- bite: 5e5356ef-df48-4e1b-b62e-38cec46398c3 -->

Try each one before you open the answer.

1. <!-- q: mcq id="6b57bfc4" -->
   A leaked users table stores unsalted SHA-256 password hashes. Two rows have exactly the same hash. What does that tell an attacker before they guess anything?

   - [ ] Nothing, because hashes can't be compared.
   - [x] Those two users have the same password, so cracking one cracks both.
   - [ ] One of the rows is a duplicate account.
   - [ ] The hashes have been salted.

   <details><summary>Answer</summary>

   With no salt, the same password always gives the same hash, so equal hashes mean equal passwords. A per-user salt makes every hash different even for the same password, so each one has to be attacked on its own.

   </details>

2. <!-- q: exact id="f8f2d4fa" answer="40" tolerance="1" -->
   An attacker can test 200 bcrypt guesses per second against one stolen hash. Their wordlist has 28.8 million passwords. To the nearest hour, how many hours does it take to try the whole list against that one hash?

   <details><summary>Answer</summary>

   40 hours. 28,800,000 ÷ 200 = 144,000 seconds, and 144,000 ÷ 3,600 = 40 hours. Because every user has their own salt, the attacker pays that again for every account.

   </details>

3. <!-- q: mcq id="1e143dda" -->
   A site stores passwords with bcrypt at cost 12. A user's password is `password1`. The database leaks. How safe is this user's password?

   - [ ] Safe, because bcrypt is slow.
   - [ ] Safe for about 40 hours.
   - [x] Not safe: `password1` is near the top of every wordlist, so it's tried almost first and falls in seconds even with bcrypt.
   - [ ] Safe, because the salt hides it.

   <details><summary>Answer</summary>

   Slow hashing makes each guess expensive, but `password1` needs only a handful of guesses. Slow hashing protects passwords in the middle of the list; the fix for the top of the list is refusing breached passwords at sign-up.

   </details>

4. <!-- q: mcq id="3b631f3e" -->
   Your login logs show 20,000 failed logins in an hour, across 19,000 different usernames, from about 30 IP addresses. No single account had more than 2 attempts. What is this, and which defence fits?

   - [ ] Brute force on one account; lock accounts after 3 failures.
   - [x] Credential stuffing; rate limit per IP, check for breached passwords, and offer MFA.
   - [ ] A broken mobile app; ignore it.
   - [ ] SQL injection; use parameterised queries.

   <details><summary>Answer</summary>

   Many usernames with one or two tries each is credential stuffing with passwords leaked from other sites. Per-account lockouts never trigger at 2 attempts. Rate limiting by source, refusing breached passwords and MFA are what help, and the pattern is easy to alert on once failed logins are logged.

   </details>

5. <!-- q: mcq id="907b6c60" -->
   A user types their password, and the 6-digit code from their authenticator app, into a perfect copy of your login page on a fake domain. Which second factor would have stopped the attacker logging in as them?

   - [ ] An SMS code.
   - [ ] A longer TOTP code.
   - [x] A passkey or security key (WebAuthn), because it checks the real website address before answering.
   - [ ] None; MFA can't help once the password is phished.

   <details><summary>Answer</summary>

   A fake site can ask for an SMS or TOTP code and replay it within seconds. A passkey or security key signs a challenge tied to the real site's address, so on the fake domain it gives nothing usable. That's what "phishing-resistant" means.

   </details>

6. <!-- q: open id="8801cb9d" -->
   An app's logout button deletes the session cookie in the browser, and nothing else. Explain the problem, and what logout should do.

   <details><summary>Answer</summary>

   The session is still valid on the server. Anyone who copied the token earlier, from a shared computer, a log, or an XSS bug, can keep using it after the user "logged out". Logout must end the session on the server (delete or invalidate it) so the token stops working everywhere, and then clear the cookie.

   </details>

## Practice — harden a login
<!-- bite: bb58fdf2-fdc3-41c7-9885-6da63cbf93df -->

**Task.** Take the login of your own app (the flagship from SWE 101, or any small app you wrote), and check it against this lesson.

1. How are passwords stored? If it's not bcrypt or Argon2 through a library, change it, and plan how existing users move over (re-hash at their next login).
2. Add a breached-password check at sign-up, using a breached-password list or the Have I Been Pwned range API.
3. Add rate limiting to the login route, and log every failed login with username and IP.
4. Check that logout ends the session on the server, and that login issues a fresh session ID.

## Practice: when your login is done
<!-- bite: a13f66e2-968e-4860-83ef-982d84273b15 -->

Here is how you know the task is finished, plus a stretch step.

**Done when:** a test signs up with `password1` and is refused, a test sends 20 bad logins and gets slowed or blocked, a test shows a token stops working after logout, and the worked example's crack results are in your notes. Record the run in `cybersecurity/LIVE-RUNS-TODO.md`.

**Stretch.** Add TOTP as a second factor with a library such as `pyotp` or `otplib`, then try logging in with a code from the previous 30-second window. Does your library accept it? Most allow one window either side for clock drift; find where that's set.

## Before moving on
<!-- bite: e42678a8-7996-4324-b525-4ae9920219a9 -->

You can now explain why passwords are stored as slow, salted hashes, seed and crack a dummy database to see what that buys, stop weak passwords at sign-up, defend against online guessing and credential stuffing, choose between MFA types, and spot the session and JWT mistakes that undo a good login.

**Recap for later lookup:** bcrypt or Argon2 through a library, never a fast hash. Salt stops equal passwords looking equal. Slow hashing protects the middle of the list; breach checks remove the top; length protects the rest. Rate limit and log failures; avoid hard lockouts; one error message for both halves. Passkeys resist phishing; SMS and TOTP don't. New session ID at login; end sessions on the server; verify JWT signatures with your chosen algorithm.

Next: [[cybersecurity/04-web-security/03-https-and-tls|HTTPS and TLS]]. Everything in this lesson assumed the password reached your server unread. HTTPS is what makes that true.

## Related
<!-- bite: 226c684f-c2f0-4b05-8e04-b06f2a3ec572 -->

- [[cybersecurity/02-ethical-hacking/10-pdf-and-document-security|PDF and document security]] — the same offline cracking, from the attacker's side.
- [[backend/05-auth/01-authentication-flows|Authentication flows]] — sessions, JWTs, OAuth and SSO, compared.
- [[cybersecurity/05-cryptography/03-hashing-and-integrity|Hashing and integrity]] — fast hashes, what they're for, and why passwords need a different kind.

## About this lesson
<!-- bite: 6c21b070-503d-4a38-948d-5419b74ce67f -->

**Level:** Intermediate. **Covers:** slow salted password hashing (bcrypt, Argon2) and what it does and doesn't protect, breached-password checks and current password guidance, online guessing, credential stuffing and rate limiting, MFA strengths from SMS to passkeys, session and JWT rules, and a lab that seeds a dummy-account database and cracks it with hashcat both ways. **Where it sits:** lesson 2 of the [[cybersecurity/04-web-security/index|Web Security]] section; the defender's side of the password-cracking labs in ethical hacking. **Sources:** the original vault note, rebuilt around the tier-3 dummy-account lab. `[reference]` — commands not yet run live; tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
