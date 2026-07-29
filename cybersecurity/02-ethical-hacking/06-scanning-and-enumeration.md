# Scanning & Enumeration

Where [[03-reconnaissance|reconnaissance]] builds a broad picture of the target, scanning and enumeration get specific: which hosts are actually alive, which ports are open, which services are running on them, and what those services will reveal about themselves if asked directly.

## Port scanning — what's actually reachable

A port scan checks which network ports on a target respond, revealing which services are exposed. **Nmap** is the standard tool for this, conceptually:

```
# illustrative — conceptual usage of a standard, well-known scanning tool
nmap -sV 192.168.1.10          # scan common ports, attempt to identify service versions
nmap -p- 192.168.1.10           # scan all 65535 ports, not just the common subset
nmap -sC -sV 192.168.1.10       # run default detection scripts plus version detection
```

A scan's output — open ports, service names, version numbers — is the map used to decide what to investigate further. An open port running an old, known-vulnerable service version is exactly the kind of finding scanning exists to surface.

## Enumeration — going one level deeper than "is this port open"

Enumeration means actively extracting more detail from a discovered service: what OS is running, what usernames exist, what shares are accessible, what the exact software version and configuration is. This is inherently more intrusive than a basic port scan (it involves actually talking to the service, sometimes authenticating or half-authenticating) and correspondingly needs firmer scope justification.

Common categories: enumerating users on a system that allows it, enumerating shared network drives and their permissions, enumerating web application directories/endpoints (see [[07-exploitation-concepts|exploitation-concepts]] for what this feeds into on the web side), enumerating DNS subdomains more aggressively than passive recon allows.

## Vulnerability scanning — automated comparison against known weaknesses

Distinct from a plain port scan: a vulnerability scanner (e.g. Nessus, OpenVAS) checks discovered services against a database of known vulnerabilities (CVEs) and misconfigurations, producing a prioritized list of likely weaknesses. Fast and thorough for known issues, but generates false positives that need manual verification, and — critically — won't find genuinely novel or logic-based vulnerabilities that aren't in any database, which is exactly the gap manual testing (see [[07-exploitation-concepts|exploitation-concepts]]) exists to fill.

## Why noisy scanning matters as a concept

Aggressive scanning (scanning all ports rapidly, hitting a service repeatedly) is far more likely to be detected by the target's monitoring than reconnaissance was — and in a red-team-style engagement specifically testing detection capability (see [[02-penetration-testing-methodology|penetration-testing-methodology]]), the scan's *stealth* can matter as much as its results. Scan timing/aggressiveness is itself a scoped decision, not just a technical default.

## Gotchas

- Scanning too aggressively against a fragile or unexpectedly sensitive system (older industrial control systems are a well-known example) can cause real disruption — a scan is an active action against a live system, not a purely passive read, and scope/rules of engagement (see [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]) should specify acceptable scan intensity for exactly this reason.
- A clean vulnerability scan report doesn't mean a target is actually secure — automated scanning only catches known signatures/patterns, and manual testing is what catches business-logic flaws and novel weaknesses that no scanner's database includes.
- Enumeration results (usernames, share names, software versions) should be handled carefully in later reporting — accurate detail matters for remediation, but a report is a sensitive document in its own right and needs to be protected accordingly (see [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]]).

## Related
- [[03-reconnaissance|reconnaissance]]
- [[07-exploitation-concepts|exploitation-concepts]]
- [[02-penetration-testing-methodology|penetration-testing-methodology]]
