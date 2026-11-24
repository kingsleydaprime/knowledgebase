---
id: 7d90765f-3cea-4825-875f-c751a10130b9
---

# Security Design Principles

**Security design principles are a small set of rules of thumb, like "have more than one lock" and "give each person only the keys they need", that stay true whatever the technology and that you reason from when you meet a problem you've never seen.**

## Before you start
<!-- bite: 6f5ad7b7-c504-4e7b-844e-eff65ac37782 -->

You should have:

- Met risk, the CIA triad and attacker types → lessons [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|01]], [[cybersecurity/01-fundamentals/02-cia-triad|02]] and [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|03]].

After this lesson you will be able to:

1. State the core principles: defence in depth, least privilege, fail securely, minimise the attack surface, zero trust, separation of duties, keep it simple, no security through obscurity, and complete mediation.
2. Spot which principle a design mistake breaks.
3. Use the principles as questions to review any design, including your own.

**Study route.** Kid version and §1–5, then the worked example: a review of five Mama Put design decisions.

## What security principles are
<!-- bite: 77950d13-8628-423a-a58b-c4b8d359eafd -->

The rest of this course is mostly *techniques*: how to hash a password, block an injection, set up a firewall. Techniques change every few years. Underneath them sits a small set of **principles**, ways of thinking that were true in 1975, when Jerome Saltzer and Michael Schroeder wrote most of them down, and are still true now.

Learn the principles and you can reason your way to a good answer for a situation no checklist covers. That's the difference between someone who memorised a list of rules and someone who understands security. You'll meet every one of these again, in every section of the course.

## The kid version
<!-- bite: febb8f6e-b8b3-42a6-b502-1df358364ac3 -->

Think about how a sensible family protects their home. They don't rely on one lock: there's a gate, a door lock and a dog (more than one layer). The babysitter gets a key to the front door, not to the safe (only the keys you need). If the electric gate breaks, it stays shut instead of swinging open (break safely). They don't leave spare keys under every flowerpot (fewer ways in). And they don't count on burglars "not knowing" where the safe is.

Each of those habits is a security principle. Nobody needs a rulebook for every possible burglar; the habits cover them all.

**Where the analogy stops working.** A home has a few doors you can see. A software system has thousands of "doors" (every input, port, account and library), many of which nobody remembers adding. So the principle about having fewer ways in matters far more in software than it does for a house.

## 1. Defence in depth, and least privilege
<!-- bite: 09d0511e-7a94-400a-8cc1-cd2cbabd7b3c -->

These two come first, because between them they make sure one failure is both *contained* and *limited*.

**Defence in depth: never rely on one control; layer them, so one failure isn't a breach.** Every control eventually fails: a patch is missed, a setting drifts, a new bug appears. With layers, a firewall *and* safe code *and* limited access *and* monitoring, the others still stand when one falls. Whenever you hear "the firewall will catch it", that's relying on one layer.

**Least privilege: give every person, program and key the minimum access it needs, and nothing more.** A stolen account or a hacked program can do exactly what it was allowed to do. If the kitchen screen's account can only read today's orders, stealing it gets the attacker today's orders, not the whole database. Over-permissioning is how a small break-in becomes a total one.

## 2. Fail securely, and minimise the attack surface
<!-- bite: 90770458-d63b-449e-a31a-e72f2248d698 -->

**Fail securely: when something breaks, it should break closed (deny), not open (allow).** An error in a permission check must refuse access, never grant it:

```python
try:
    authorized = check_permission(user, order)
except Exception:
    authorized = False        # fail CLOSED: an error denies access, never grants it
```

The same idea gives **default deny**: allow only what's explicitly listed, block everything else. An allowlist beats a blocklist, because you can list what's safe far more reliably than everything that's dangerous.

**Minimise the attack surface: every feature, port, account and library is something that can be attacked.** The most secure part is the one that isn't there. Turn off what you don't use, remove old code and test accounts, and don't collect data you don't need: data you never stored can't leak.

## 3. Zero trust, and separation of duties
<!-- bite: c2a03db4-a6b3-42d1-9c2d-622cca96cbae -->

**Zero trust: don't trust anything because of where it is; check every request, every time.** Old networks trusted everything "inside". But attackers get inside (one phished laptop is enough), and with cloud services and remote work there's no clear "inside" anyway. So every request proves who it's from and that it's allowed, wherever it comes from.

**Separation of duties: no single person or program should be able to do something critical alone.** Two people to approve a large refund; the person who writes code isn't the one who approves it going live; the person asking for access isn't the one granting it. It limits both fraud and the damage from one stolen account, because one corrupted party can't finish the job alone.

## 4. Keep it simple, and no security through obscurity
<!-- bite: b679f476-2f76-4750-9e87-20b286a09028 -->

**Keep it simple.** Complexity is where bugs and misconfigurations hide. A simple design you fully understand is safer than a clever one you don't, which is why security-critical code is written to be easy to review, not impressive.

**No security through obscurity: don't rely on attackers not knowing how your system works.** Assume they have your code and your design; they often do. Security must hold even when everything except the secrets is public. That's [[cybersecurity/05-cryptography/01-what-is-cryptography|Kerckhoffs's principle]], applied to everything. A hidden admin page at `/secret-admin-xyz` isn't protection; a login with a strong password and two-factor is. Obscurity can be a thin extra layer, never the foundation.

## 5. Complete mediation — check every time
<!-- bite: 94e98ec2-4eba-4cb5-a951-9720f90ab102 -->

**Check permission on every access, not just the first.** Don't check once and remember "they're allowed" for ever, because permissions change and a remembered "yes" outlives the reason it was given. A staff member who was fired an hour ago must not still be able to change prices because their session said "admin" this morning.

This is also why every API request has to check that the thing being asked for belongs to the person asking. Forgetting that, so that changing `/orders/41` to `/orders/42` shows someone else's order, is one of the most common serious bugs on the web ([[cybersecurity/14-api-security/03-authorization-and-bola|BOLA]]).

## Terms used in this lesson
<!-- bite: 29d53bd8-df37-4dba-be68-d6111a035420 -->

1. **Defence in depth**: This is using several layers of protection, so one failing isn't a breach.
2. **Least privilege**: This is giving every person, program and key only the access it needs.
3. **Fail securely**: This is also called **fail-safe defaults**. It means breaking into a "deny" state, and allowing only what's explicitly permitted.
4. **Attack surface**: This is everything an attacker could try: every input, port, account, feature and library.
5. **Zero trust**: This is checking every request on its own merits, never trusting it because of where it came from.

## Terms used in this lesson: the rest of the principles
<!-- bite: 56f5b42f-36e2-4f11-a416-df58ebb2fcab -->

The rest of the terms finish the set.

6. **Separation of duties**: This is requiring more than one person or program to complete a critical action.
7. **Security through obscurity**: This is relying on attackers not knowing how a system works. It's a weakness, not a defence.
8. **Complete mediation**: This is checking permission on every single access, not just the first.
9. **Allowlist and blocklist**: An allowlist names what's permitted and blocks the rest; a blocklist names what's forbidden and allows the rest.

## Worked example — review five Mama Put decisions
<!-- bite: 13f07b65-07fa-4f7e-84e4-0016e81df89a -->

A developer has made these five choices in Mama Put's app. For each, name the principle it breaks and suggest a fix. **Predict first**, then check.

1. The kitchen screen logs in with the same admin account the owner uses.
2. When the permission check throws an error, the code lets the request through "so the kitchen isn't blocked".
3. A `/debug` page that shows server settings and recent orders was left on in production.
4. The Paystack secret key is in the mobile app's code, "because nobody will look".
5. Any staff member can issue a refund of any size on their own.

## Worked example: the answers
<!-- bite: 23bccb4d-a30a-4992-9668-c37c9efcd510 -->

1. **Least privilege.** The kitchen needs to read today's orders and mark them cooked. Give it its own account that can do only that.
2. **Fail securely.** An error must deny, not allow. Show the kitchen a clear error and fix the bug; never open the door because the lock is broken.
3. **Minimise the attack surface.** A debug page is a door nobody needs in production. Remove it, or make it reachable only from the server itself.
4. **No security through obscurity.** Anyone can unpack a mobile app and find the key; tools do it automatically. Secret keys stay on the server, and the app talks to the server.
5. **Separation of duties.** Large refunds should need a second person's approval, so one compromised or dishonest account can't drain the takings.

Notice that none of the fixes needs an expensive product. Most security failures are design decisions, and the principles are how you catch them before they ship.

## How to use these principles
<!-- bite: 393808a8-3c13-4053-8410-b8cd903f4fbc -->

Turn them into questions, and ask them of every design, including your own:

1. Am I relying on one control? → defence in depth.
2. Does this have more access than it needs? → least privilege.
3. What happens when this fails? → fail securely.
4. Do I need this feature, port or data at all? → minimise the attack surface.
5. Am I trusting this because of where it came from? → zero trust.
6. Can one person or one stolen account do this alone? → separation of duties.
7. Am I hoping they won't figure it out? → no security through obscurity.
8. Is this checked every time, or only once? → complete mediation.

When a specific rule isn't obvious, work it out from these.

## Common pitfalls and traps
<!-- bite: 5224e063-e8f7-49b3-bd41-350fb1a39a40 -->

1. **"The firewall protects us."** That's one layer. What happens when it's bypassed?
2. **Giving admin "for now".** Temporary broad access becomes permanent. Start minimal and add what's needed.
3. **Fail-open error handling.** `except: return True` in a security check is a backdoor waiting to be found.
4. **Hidden URLs and secret keys in client code.** If it ships to the user's device, assume the attacker has it.
5. **Treating the principles as a checklist to tick once.** They're questions to ask of every change.

## Check your understanding
<!-- bite: 420a3198-fb3d-4b2a-9175-d3100e25517a -->

Try each one before you open the answer.

1. <!-- q: mcq id="2ecc2663" -->
   A reporting tool only needs to read sales figures, but it connects to the database with an account that can also delete tables. Which principle does this break?

   - [ ] Defence in depth
   - [x] Least privilege
   - [ ] Separation of duties
   - [ ] Complete mediation

   <details><summary>Answer</summary>

   Least privilege. If the reporting tool is compromised, the attacker can do everything its account can, including deleting tables. A read-only account would cap the damage.

   </details>

2. <!-- q: mcq id="c74c5e30" -->
   A login service crashes. While it's down, the app treats every request as logged in, "so users aren't locked out". Which principle does this break?

   - [ ] Minimise the attack surface
   - [ ] Zero trust
   - [x] Fail securely
   - [ ] Keep it simple

   <details><summary>Answer</summary>

   Fail securely. A broken security check must deny access. Here the failure opens the door to everyone, and an attacker who can crash the login service gets in.

   </details>

3. <!-- q: gap id="b27a0f0e" answers="allowlist|allow list|allow-list" -->
   An upload form accepts only `.jpg`, `.png` and `.pdf` files and rejects everything else. Naming exactly what's permitted, and blocking the rest, is called an ___.

   <details><summary>Answer</summary>

   An allowlist. It follows fail-safe defaults: anything not explicitly permitted is denied. A blocklist of "bad" extensions would miss the ones nobody thought of.

   </details>

4. <!-- q: mcq id="8a9bf070" -->
   A company protects its admin panel only by putting it at an unusual address, `/panel-8f3k2`, with no login. Which principle does this break?

   - [ ] Separation of duties
   - [x] No security through obscurity
   - [ ] Least privilege
   - [ ] Defence in depth only

   <details><summary>Answer</summary>

   It relies on attackers not knowing the address. Addresses leak through browser history, logs and scanners that guess paths. The panel needs real authentication; an unusual address can only ever be a thin extra layer.

   </details>

5. <!-- q: mcq id="22d698b4" -->
   An employee is fired at 10:00. At 11:00 they're still using their open session to change prices, because the app checked their admin role only when they logged in that morning. Which principle does this break?

   - [ ] Minimise the attack surface
   - [ ] Fail securely
   - [x] Complete mediation
   - [ ] Keep it simple

   <details><summary>Answer</summary>

   Complete mediation: permission must be checked on every access, not remembered from the first. Checking the role on each request, and ending sessions when access is removed, would have stopped them.

   </details>

6. <!-- q: open id="5ebcbdd9" -->
   A colleague says: "We use HTTPS and a firewall, so we don't need to validate input or limit database permissions." Use defence in depth to explain why that's wrong.

   <details><summary>Answer</summary>

   HTTPS protects data on the road, and a firewall controls what reaches the server, but both deliberately let web requests through, including malicious ones. An injection attack arrives over HTTPS on the allowed port. Defence in depth means having other layers for when (not if) one is bypassed: input validation and parameterised queries stop the injection, least-privilege database accounts limit what a successful one can do, and monitoring notices it.

   </details>

## Practice — review a design of your own
<!-- bite: a04948ef-8bdf-4aad-a4f9-1f5863cd4dde -->

**Task.** Take an app you've built (or Mama Put's API from the framework subjects) and review it with the eight questions from "How to use these principles".

1. For each question, write one specific place in your app it applies to.
2. Mark each one "fine" or "needs work", with a reason.
3. Fix the most serious "needs work" item.

## Practice: when your review is done
<!-- bite: c83c78c2-2b7f-4f6a-bc1e-ba26e0b5bac6 -->

Here is how you know the task is finished.

**Done when:** all eight questions have a specific answer about your app, and at least one fix is made, with a note of which principle it applies.

## Before moving on
<!-- bite: 7051a246-5add-4f50-83b8-baf6dca42e7a -->

You can now state the core security principles, spot which one a design mistake breaks, and use them as review questions for any design.

**Recap for later lookup:** defence in depth (layers); least privilege (minimum access); fail securely (break closed, default deny, allowlists); minimise the attack surface (remove what you don't need); zero trust (check every request, wherever it's from); separation of duties (no one acts alone on critical things); keep it simple; no security through obscurity (assume they know the design); complete mediation (check every time). Least privilege and defence in depth come up most.

Next: [[cybersecurity/01-fundamentals/05-threat-modeling|threat modelling]], the method for deciding which principles to apply where.

## Related
<!-- bite: 2ba3da10-8017-4cae-bc08-c066f14782a0 -->

- [[cybersecurity/07-security-operations/01-defensive-architecture|Defensive architecture]] — these principles in day-to-day operation.
- [[cybersecurity/03-network-security/index|Network security]] — default deny, layers and zones, built on a real server.
- [[cybersecurity/09-cloud-security/02-identity-is-the-perimeter|Identity is the perimeter]] — least privilege and zero trust in the cloud.

## About this lesson
<!-- bite: 67f5d0bb-abae-4081-b0e9-cf2cae7784d7 -->

**Level:** Beginner→Intermediate. **Covers:** defence in depth, least privilege, fail securely and default deny, minimising the attack surface, zero trust, separation of duties, simplicity, no security through obscurity, and complete mediation, with a review of five Mama Put design decisions and the principles as eight review questions. **Where it sits:** lesson 4 of the [[cybersecurity/01-fundamentals/index|Fundamentals]] section. **Sources:** Saltzer and Schroeder, "The Protection of Information in Computer Systems" (1975), and modern practice; rebuilt from the original vault note around the Mama Put running example.
