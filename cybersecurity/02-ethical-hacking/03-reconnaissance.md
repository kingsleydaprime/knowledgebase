# Reconnaissance

The information-gathering phase — building a picture of the target before touching it directly (or before touching it in any way that could be noticed). What gets found here shapes every later phase: you can't scan or exploit what you don't know exists.

## Passive vs active reconnaissance

- **Passive** — gathering information without directly interacting with the target's systems at all: public records, search engines, social media, DNS records, job postings (which often reveal internal tech stack), leaked credential databases. Effectively undetectable to the target, since no traffic touches their infrastructure.
- **Active** — directly interacting with the target's systems to gather information (pinging hosts, resolving DNS, browsing the target's own website) — still typically low-risk and often within normal scope, but detectable in logs, unlike passive recon.

Most engagements start entirely passive and only move to active reconnaissance once broad passive groundwork is done.

## OSINT — Open Source Intelligence

The practice of gathering information from publicly available sources. Common categories:

- **Domain/DNS information** — WHOIS records, DNS records (which can reveal mail servers, subdomains, hosting providers).
- **Organizational information** — company structure, employee names/roles (useful for understanding likely usernames, and for social engineering awareness testing specifically authorized in scope).
- **Technical footprint** — job postings mentioning specific technologies, code repositories, exposed documentation, cached pages showing since-removed content.
- **Breach data** — checking whether an organization's email domains appear in known public breach databases, which can indicate reused/weak credentials in circulation.

```
# illustrative, conceptual examples of passive recon commands — not exploit tooling
whois example.com
dig example.com ANY
nslookup -type=MX example.com
```

## Why reconnaissance quality determines the rest of the engagement

A thorough recon phase can reveal an organization's entire external attack surface — every subdomain, every exposed service, every piece of software in use — often before a single scan is run. Skipping or rushing this phase means later scanning/exploitation is working from an incomplete picture, and it's the phase most likely to reveal an easy, low-effort weakness (an exposed admin panel, a misconfigured cloud storage bucket) that a rushed engagement would miss entirely by jumping straight to scanning.

## Social engineering awareness (as a specifically scoped activity)

Some engagements explicitly include testing human vulnerability to social engineering — phishing simulations, pretexting phone calls — but only when explicitly authorized in scope (see [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]), since it involves interacting with real people who haven't individually consented the way a system owner has. This is a distinct, separately-scoped activity from technical reconnaissance, not a default part of every engagement.

## Gotchas

- Even passive reconnaissance should stay within the agreed scope — gathering information about systems or subsidiaries not covered by the authorization can create legal exposure despite involving no direct interaction with those systems.
- Information gathered in recon can go stale — a subdomain found early in a long engagement may be decommissioned by the time exploitation begins; recon is often revisited throughout an engagement, not treated as a one-time, upfront step.

## Related
- [[02-penetration-testing-methodology|penetration-testing-methodology]]
- [[06-scanning-and-enumeration|scanning-and-enumeration]]
- [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]
