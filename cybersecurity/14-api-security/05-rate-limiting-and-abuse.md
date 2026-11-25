---
id: 82b1420c-4aec-4ae2-8426-308a61da0a3a
---

# Rate Limiting and Abuse

**Rate limiting caps how many requests a caller makes in a time window — but the hardest abuse uses the API exactly as designed, where only the *pattern* reveals the attack.**

## Before you start
<!-- bite: e12f3b33-7f7a-47de-a1ce-65377e58b885 -->

You should have:

- Why machine clients make abuse the normal case → [[cybersecurity/14-api-security/01-what-makes-api-security-different|what makes API security different]].
- Bounding per-request work → [[cybersecurity/14-api-security/04-input-validation-and-injection|input validation]].
- The credential-stuffing threat → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords and reuse]].

After this lesson you will be able to:

1. Name the resource-consumption vectors (volume, expensive ops, large payloads, amplification) and the defences.
2. Explain why a rate limit alone can't stop business-flow abuse, and what does.
3. Choose where to enforce each control — gateway, app, shared store, WAF.

**Study route.** Read the kid version and API4, then API6 carefully — the "valid requests, bad pattern" idea is the one that trips people up. The practice task reviews your own limits.

## What rate limiting and abuse are
<!-- bite: 497cd4da-5138-4310-9847-7d8060f7b6a1 -->

A human uses your app a few times a minute; a script uses it thousands of times a second, all day, from a thousand IPs. So an API faces attacks a web page rarely does — brute-forcing logins, scraping the whole database, exhausting resources, and abusing legitimate features at machine scale. Rate limiting is the throttle, and it handles raw volume well. But some abuse needs *more* than a throttle, because it uses the API precisely as intended — just far more, and for the wrong reason. This lesson covers both: resource consumption (API4), which a throttle does catch, and sensitive-business-flow abuse (API6), which it doesn't.

## The kid version
<!-- bite: 3b3b0a4f-4ec9-4fda-8c3e-d473e1215dec -->

A human uses your app a few times a minute. **A script uses it a few thousand times a second** — and can keep going all day, from a thousand IPs. So an API faces attacks a web page rarely does: brute-forcing logins, scraping the whole database, exhausting your resources, and abusing legitimate features at machine scale.

Rate limiting is the throttle. And some abuse needs *more* than a throttle, because it uses the API precisely as intended — just far more, and for the wrong reason.

## API4: Unrestricted Resource Consumption
<!-- bite: 08be1b14-0eea-452c-b7fc-6b5abbe2c8a6 -->

Every request costs you — CPU, memory, database load, bandwidth, and real money (third-party API calls, SMS, egress, LLM tokens). **An API with no limits lets a caller run up that cost without bound**, which is denial-of-service and, in the cloud, denial-of-*wallet*.

The vectors:
- **Volume** — millions of requests exhausting capacity
- **Expensive operations** — one request that triggers heavy work (a huge export, an unbounded search, a complex GraphQL query)
- **Large payloads** — a giant request body, or a response the caller forces to be enormous (`?limit=10000000`)
- **Amplification** — one API call fanning out into many downstream calls or a costly external one (SMS, email, an LLM call — **"denial of wallet"**)

## API4: the defences
<!-- bite: e7b7e041-a440-44a5-bc27-0c090cabaa2c -->

**Rate limiting** — cap requests per client per time window:
- **Token bucket** is the standard algorithm — a bucket refills at a steady rate, each request spends a token, empty bucket = rejected. Allows bursts while bounding the average → [[backend/06-cross-cutting/index|rate limiting]], and you can [[build-your-own-shit/index|build one]]
- **Per what?** Per API key, per user, per IP — and usually several at once (a per-IP limit stops one attacker; a per-user limit stops a botnet targeting one account)
- **Return `429 Too Many Requests`** with a `Retry-After` header, so legitimate clients back off politely
- **Tiered limits** — different caps per plan, stricter on expensive endpoints (login, search, export) than cheap ones

**Bound the work per request** — pagination with a *maximum* page size (never trust `?limit=`), query timeouts, payload size limits, GraphQL depth/complexity limits → [[cybersecurity/14-api-security/04-input-validation-and-injection|bounding input]].

**Quotas** — longer-window caps (per day/month), especially where each call has real cost.

## API6: Unrestricted Access to Sensitive Business Flows
<!-- bite: 2b102dbd-3030-4cfd-a202-a82ab0d8b784 -->

The subtle one, and why rate limiting alone isn't enough. **Some abuse uses the API *exactly as designed* — the requests are individually valid, but the *pattern* is the attack:**

- **Buying all the concert tickets** with bots to resell — every purchase is legitimate; the scale and intent are the abuse
- **Creating thousands of fake accounts** for a signup bonus
- **Scraping the entire product catalogue** for a competitor
- **Credential stuffing** — each login attempt is a valid request; the pattern (many accounts, breach-list passwords) is the attack → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|credential stuffing]]

## API6: why a rate limit can't catch it
<!-- bite: 9dd68a13-ccce-40a8-b31b-5419c2dd1164 -->

**A simple rate limit doesn't catch this**, because a distributed attack stays under any per-client limit, and the individual requests are indistinguishable from real use. The defences are behavioural, not just volumetric:

- **Bot detection** — CAPTCHA, device fingerprinting, proof-of-work challenges, behavioural analysis (mouse/timing patterns real users have and scripts don't)
- **Anomaly detection** — flag patterns: one device creating many accounts, purchases faster than humanly possible, a spike in a sensitive flow → [[cybersecurity/07-security-operations/index|detection]]
- **Business-logic limits** — "max 4 tickets per person," "one signup bonus per verified identity/payment method," step-up verification on sensitive flows
- **Friction for the suspicious** — email/SMS verification, waiting periods, holds on new accounts

**The mindset shift: ask not just "is this request valid?" but "does this *pattern of valid requests* make sense for a real user?"** That's the question a rate limit can't answer alone.

## Login and credential endpoints
<!-- bite: 16a75182-446d-4991-98a2-e34b6cb48572 -->

The highest-value target for automated abuse, deserving special treatment:

- **Strict rate limiting** on login, password reset, MFA, and token endpoints
- **Account lockout / exponential backoff** after failed attempts — but beware lockout-as-DoS (an attacker locking out real users); prefer backoff + anomaly detection over hard lockout
- **Check against breach lists** and require strong passwords → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords]]
- **CAPTCHA or step-up** after a few failures
- **Monitor for credential stuffing** — many accounts, one IP; or many IPs, breach-list passwords

## Where to enforce it
<!-- bite: 2f695599-81db-4c23-aa35-9cd4c1dee2e3 -->

- **API gateway / reverse proxy** — the natural place for coarse rate limiting, applied before requests reach your app (Kong, cloud API gateways, nginx, Cloudflare) → [[cybersecurity/14-api-security/06-the-api-security-lifecycle|gateways]]
- **Application layer** — for per-user and business-logic limits the gateway can't see
- **A shared store** (Redis) so limits hold *across* your instances — a per-instance counter is defeated by load balancing → [[databases/index|Redis]]
- **A WAF / bot-management layer** for the behavioural stuff

**Layer them:** gateway for volume, app for business logic, WAF for bots.

## Key insight
<!-- bite: 93ac4347-8c99-43ac-9fb5-45670548f9e9 -->

**Machine clients turn abuse from an edge case into the normal case, so APIs need throttling that web pages rarely do — but rate limiting alone catches only volume, not *pattern*.** The harder class (API6) is abuse that uses the API exactly as designed — bulk-buying, fake accounts, scraping, credential stuffing — where every request is valid and only the pattern reveals the attack. Defending it means asking "does this *sequence* of valid requests make sense for a real user?", which needs behavioural detection and business-logic limits, not just a token bucket.

## Terms used in this lesson
<!-- bite: c7437cbe-0018-40a6-8e11-fffb95edb41e -->

1. **Rate limiting**: Capping requests per client per time window to bound load and raw abuse.
2. **Token bucket**: The standard rate-limit algorithm — a bucket refills at a steady rate, each request spends a token, an empty bucket rejects; allows bursts while bounding the average.
3. **Denial of wallet**: Cloud-era DoS where the attack runs up your *bill* (SMS, email, LLM tokens, egress) rather than exhausting capacity.
4. **Amplification**: One API call fanning out into many downstream or costly external calls.

## Terms used in this lesson: abuse and detection
<!-- bite: b464984c-c19f-45b4-a141-25400185d378 -->

5. **Quota**: A longer-window cap (per day/month), especially where each call has real cost.
6. **Business-flow abuse (API6)**: Abuse that uses the API exactly as designed — bulk-buying, fake accounts, scraping, credential stuffing — where each request is valid and only the pattern is the attack.
7. **Credential stuffing**: Trying breach-list username/password pairs across many accounts; each login is a valid request, the pattern is the attack.
8. **Bot detection / anomaly detection**: Behavioural defences (CAPTCHA, device fingerprinting, pattern analysis) that spot abuse a volumetric limit can't.

## Check your understanding
<!-- bite: 92bd9b07-ec72-49e7-8eba-ebdce17978b9 -->

Try each one before you open the answer.

1. <!-- q: mcq id="2bb821c6" -->
   A single endpoint lets a caller request `?limit=10000000`, returning a massive response. Which resource-consumption vector is this, and what bounds it?

   - [ ] Amplification; add a CAPTCHA
   - [x] A caller-forced large payload; enforce a server-side *maximum* page size and never trust `?limit=`
   - [ ] Credential stuffing; lock the account
   - [ ] SSRF; block internal IPs

   <details><summary>Answer</summary>

   It's a large-payload / expensive-operation vector. The fix is to bound the work per request: pagination with a server-enforced maximum page size, query timeouts, and payload limits. Never let the client dictate how much work or data a request produces.

   </details>

2. <!-- q: mcq id="92e3d940" -->
   Why does a per-client rate limit fail to stop a bot operation buying all the concert tickets?

   - [ ] Rate limits don't apply to purchases
   - [x] The attack is distributed (many accounts/IPs) and each purchase is a legitimate request, so it stays under any per-client limit and looks like real use
   - [ ] Tickets aren't an API resource
   - [ ] The limit only counts failed requests

   <details><summary>Answer</summary>

   Business-flow abuse (API6) uses the API exactly as designed. Spread across many accounts and IPs, each request stays under the limit, and individually every purchase is valid. Volume-based throttling can't tell it from real demand — you need behavioural defences and business-logic limits ("max 4 per person," bot detection, step-up verification).

   </details>

3. <!-- q: gap id="c866e955" answers="token bucket|token-bucket" -->
   The standard rate-limiting algorithm, which refills at a steady rate and lets each request spend one unit — allowing short bursts while bounding the average — is the ___.

   <details><summary>Answer</summary>

   Token bucket. The bucket refills steadily; each request spends a token; an empty bucket rejects (return `429` with `Retry-After`). It permits bursts up to the bucket size while capping the sustained rate.

   </details>

4. <!-- q: mcq id="2a5493db" -->
   The lesson's "mindset shift" for catching business-flow abuse is to ask which question?

   - [ ] "Is this request syntactically valid?"
   - [ ] "Is this caller over the rate limit?"
   - [x] "Does this *pattern of valid requests* make sense for a real user?"
   - [ ] "Is the payload too large?"

   <details><summary>Answer</summary>

   Each individual request is valid, so validity and volume checks pass. The useful question is about the *pattern*: one device creating many accounts, purchases faster than humanly possible, logins against many accounts with breach-list passwords. That's what behavioural and business-logic controls — not a token bucket — are for.

   </details>

5. <!-- q: open id="afcfa2b5" -->
   Where should rate limiting and abuse defences be enforced, and why not just one layer?

   <details><summary>Answer</summary>

   Layer them, because each layer sees different things. The **API gateway / reverse proxy** is the natural place for coarse, volumetric limits applied before requests reach your app (Kong, Cloudflare, nginx). The **application layer** enforces per-user and business-logic limits the gateway can't see ("max 4 tickets," "one bonus per payment method"). A **shared store (Redis)** holds counters *across* instances, since a per-instance counter is defeated by load balancing. And a **WAF / bot-management layer** handles the behavioural detection. Gateway for volume, app for business logic, WAF for bots — no single layer covers all three.

   </details>

## Practice — review your limits
<!-- bite: 443f21e0-9887-4104-898c-54d276821719 -->

Audit an API you own for the two classes.

- List the expensive endpoints (login, search, export, anything calling a paid service) and check each has a rate limit and a bound on work (max page size, timeout, payload cap).
- Check the login/reset/MFA endpoints specifically: strict limits, backoff (prefer over hard lockout to avoid lockout-as-DoS), breach-list checks.
- For one sensitive business flow (signup bonus, purchase, invite), ask "what stops a bot doing this 10,000 times?" and note whether any behavioural or business-logic limit exists.
- **Done when:** you can name one resource-consumption gap and one business-flow gap, with the specific control each needs.

## Before moving on
<!-- bite: 982e2049-ae66-415b-820f-c77c1a331cee -->

You should be able to name the consumption vectors and their defences, explain why a rate limit can't catch business-flow abuse, and place each control at the right layer. The key shift: ask not just "is this request valid?" but "does this *pattern* of valid requests make sense?"

Next: [[cybersecurity/14-api-security/06-the-api-security-lifecycle|the API security lifecycle]] — shadow/zombie APIs, misconfiguration, consuming third-party APIs safely, and testing (why BOLA needs manual testing).

## Related
<!-- bite: 1ddfe864-16dc-4a30-a261-e69c74ed5b69 -->
- [[cybersecurity/14-api-security/04-input-validation-and-injection|input validation]] — bounding per-request work
- [[cybersecurity/14-api-security/06-the-api-security-lifecycle|the API security lifecycle]] — gateways and WAFs
- [[backend/06-cross-cutting/index|cross-cutting concerns]] — rate limiting while building
- [[cybersecurity/07-security-operations/index|security operations]] — anomaly detection

## About this lesson
<!-- bite: fb61228c-8ed2-4fff-a71d-094b84de1402 -->

**Level:** Intermediate. **Covers:** defending against machine clients that hit you thousands of times a second, and abuse that uses your API exactly as designed.

*Source: [reference] — OWASP API4/API6. Aug 2026.*
