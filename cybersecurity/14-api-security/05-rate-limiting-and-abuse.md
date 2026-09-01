# Rate Limiting and Abuse

**[Intermediate]** — defending against machine clients that hit you thousands of times a second, and abuse that uses your API exactly as designed.

## The kid version first

A human uses your app a few times a minute. **A script uses it a few thousand times a second** — and can keep going all day, from a thousand IPs. So an API faces attacks a web page rarely does: brute-forcing logins, scraping the whole database, exhausting your resources, and abusing legitimate features at machine scale.

Rate limiting is the throttle. And some abuse needs *more* than a throttle, because it uses the API precisely as intended — just far more, and for the wrong reason.

## API4: Unrestricted Resource Consumption

Every request costs you — CPU, memory, database load, bandwidth, and real money (third-party API calls, SMS, egress, LLM tokens). **An API with no limits lets a caller run up that cost without bound**, which is denial-of-service and, in the cloud, denial-of-*wallet*.

The vectors:
- **Volume** — millions of requests exhausting capacity
- **Expensive operations** — one request that triggers heavy work (a huge export, an unbounded search, a complex GraphQL query)
- **Large payloads** — a giant request body, or a response the caller forces to be enormous (`?limit=10000000`)
- **Amplification** — one API call fanning out into many downstream calls or a costly external one (SMS, email, an LLM call — **"denial of wallet"**)

**The defences:**

**Rate limiting** — cap requests per client per time window:
- **Token bucket** is the standard algorithm — a bucket refills at a steady rate, each request spends a token, empty bucket = rejected. Allows bursts while bounding the average → [[backend/06-cross-cutting/README|rate limiting]], and you can [[build-your-own-shit/README|build one]]
- **Per what?** Per API key, per user, per IP — and usually several at once (a per-IP limit stops one attacker; a per-user limit stops a botnet targeting one account)
- **Return `429 Too Many Requests`** with a `Retry-After` header, so legitimate clients back off politely
- **Tiered limits** — different caps per plan, stricter on expensive endpoints (login, search, export) than cheap ones

**Bound the work per request** — pagination with a *maximum* page size (never trust `?limit=`), query timeouts, payload size limits, GraphQL depth/complexity limits → [[cybersecurity/14-api-security/04-input-validation-and-injection|bounding input]].

**Quotas** — longer-window caps (per day/month), especially where each call has real cost.

## API6: Unrestricted Access to Sensitive Business Flows

The subtle one, and why rate limiting alone isn't enough. **Some abuse uses the API *exactly as designed* — the requests are individually valid, but the *pattern* is the attack:**

- **Buying all the concert tickets** with bots to resell — every purchase is legitimate; the scale and intent are the abuse
- **Creating thousands of fake accounts** for a signup bonus
- **Scraping the entire product catalogue** for a competitor
- **Credential stuffing** — each login attempt is a valid request; the pattern (many accounts, breach-list passwords) is the attack → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|credential stuffing]]

**A simple rate limit doesn't catch this**, because a distributed attack stays under any per-client limit, and the individual requests are indistinguishable from real use. The defences are behavioural, not just volumetric:

- **Bot detection** — CAPTCHA, device fingerprinting, proof-of-work challenges, behavioural analysis (mouse/timing patterns real users have and scripts don't)
- **Anomaly detection** — flag patterns: one device creating many accounts, purchases faster than humanly possible, a spike in a sensitive flow → [[cybersecurity/07-security-operations/README|detection]]
- **Business-logic limits** — "max 4 tickets per person," "one signup bonus per verified identity/payment method," step-up verification on sensitive flows
- **Friction for the suspicious** — email/SMS verification, waiting periods, holds on new accounts

**The mindset shift: ask not just "is this request valid?" but "does this *pattern of valid requests* make sense for a real user?"** That's the question a rate limit can't answer alone.

## Login and credential endpoints

The highest-value target for automated abuse, deserving special treatment:

- **Strict rate limiting** on login, password reset, MFA, and token endpoints
- **Account lockout / exponential backoff** after failed attempts — but beware lockout-as-DoS (an attacker locking out real users); prefer backoff + anomaly detection over hard lockout
- **Check against breach lists** and require strong passwords → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords]]
- **CAPTCHA or step-up** after a few failures
- **Monitor for credential stuffing** — many accounts, one IP; or many IPs, breach-list passwords

## Where to enforce it

- **API gateway / reverse proxy** — the natural place for coarse rate limiting, applied before requests reach your app (Kong, cloud API gateways, nginx, Cloudflare) → [[cybersecurity/14-api-security/06-the-api-security-lifecycle|gateways]]
- **Application layer** — for per-user and business-logic limits the gateway can't see
- **A shared store** (Redis) so limits hold *across* your instances — a per-instance counter is defeated by load balancing → [[databases/README|Redis]]
- **A WAF / bot-management layer** for the behavioural stuff

**Layer them:** gateway for volume, app for business logic, WAF for bots.

## Key insight

**Machine clients turn abuse from an edge case into the normal case, so APIs need throttling that web pages rarely do — but rate limiting alone catches only volume, not *pattern*.** The harder class (API6) is abuse that uses the API exactly as designed — bulk-buying, fake accounts, scraping, credential stuffing — where every request is valid and only the pattern reveals the attack. Defending it means asking "does this *sequence* of valid requests make sense for a real user?", which needs behavioural detection and business-logic limits, not just a token bucket.

## Related
- [[cybersecurity/14-api-security/04-input-validation-and-injection|input validation]] — bounding per-request work
- [[cybersecurity/14-api-security/06-the-api-security-lifecycle|the API security lifecycle]] — gateways and WAFs
- [[backend/06-cross-cutting/README|cross-cutting concerns]] — rate limiting while building
- [[cybersecurity/07-security-operations/README|security operations]] — anomaly detection

*Source: [reference] — OWASP API4/API6. Aug 2026.*
