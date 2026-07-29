# Intrusion Detection & Prevention (IDS/IPS)

Firewalls (see [[01-firewalls|firewalls]]) decide what traffic is allowed through based on relatively simple rules. An IDS/IPS goes further: it inspects traffic (or system activity) for signs that something malicious is actually happening, even traffic that a firewall would have permitted.

## IDS vs IPS — detect vs. actively block

- **IDS (Intrusion Detection System)** — monitors and alerts; it doesn't block traffic itself, it flags something for a human (or another system) to act on.
- **IPS (Intrusion Prevention System)** — sits inline with traffic and can actively block/drop what it flags as malicious, in real time, without waiting for a human response.

The tradeoff: an IPS can stop an attack in progress automatically, but a false positive means it can also block legitimate traffic — IDS-only deployments are sometimes chosen specifically to avoid that operational risk while a detection ruleset is still being tuned.

## Signature-based vs anomaly-based detection

- **Signature-based** — matches traffic/activity against a database of known-malicious patterns (a specific exploit's network signature, a known malware hash). Fast and low false-positive, but structurally blind to anything genuinely new that doesn't match an existing signature.
- **Anomaly-based** — establishes a baseline of "normal" behavior for a network/system, then flags significant deviations from it. Can catch novel attacks with no existing signature, at the cost of more false positives, since "unusual" isn't always "malicious."

Most real deployments combine both — signatures for known threats (cheap, reliable), anomaly detection as a safety net for anything new.

## A concrete example: Snort

Snort is a widely used, signature-based network IDS/IPS. A rule looks like this:

```
alert tcp any any -> $HOME_NET 22 (msg:"Possible SSH brute force"; \
  flow:to_server; threshold: type threshold, track by_src, count 5, seconds 60; \
  sid:1000001; rev:1;)
```

Read as: alert if more than 5 SSH connection attempts arrive at a protected host from the same source within 60 seconds — a simple pattern for detecting a brute-force attempt, expressed as a rule Snort evaluates against live traffic.

## Host-based vs network-based (HIDS vs NIDS)

- **NIDS (Network-based)** — monitors traffic on the network itself (Snort, Suricata), seeing everything crossing a given network segment.
- **HIDS (Host-based)** — runs on an individual system, monitoring file integrity, system logs, and process behavior on that specific machine (e.g. OSSEC) — catches things a network-level view can't, like a local privilege escalation with no unusual network traffic at all.

## SIEM — correlating alerts across many sources

A SIEM (Security Information and Event Management system) aggregates logs and alerts from firewalls, IDS/IPS, endpoints, and applications into one place, correlating events across sources to catch patterns no single source would reveal alone (a failed login on one system followed by a successful login from an unusual location minutes later, for instance). This is the tool category most directly responsible for whether a real intrusion gets noticed in minutes vs. months — and precisely the detection capability a red-team engagement (see [[02-penetration-testing-methodology|penetration-testing-methodology]]) is often specifically testing.

## Gotchas

- An IDS/IPS is only as good as its ruleset/baseline — an unmaintained signature database misses new threats entirely, and an anomaly baseline built on already-compromised "normal" traffic will fail to flag the compromise it was supposed to catch.
- Alert fatigue is a real, common failure mode — a system that generates too many false-positive alerts trains its human operators to start ignoring alerts generally, which is how a genuine detection can get missed in the noise.
- Encrypted traffic (see [[03-vpns-and-encryption-in-transit|vpns-and-encryption-in-transit]]) is largely opaque to a network-based IDS inspecting packet contents — this is part of why host-based detection and endpoint visibility remain important even as more traffic becomes encrypted by default.

## Related
- [[01-firewalls|firewalls]]
- [[02-network-segmentation|network-segmentation]]
- [[02-penetration-testing-methodology|penetration-testing-methodology]]
