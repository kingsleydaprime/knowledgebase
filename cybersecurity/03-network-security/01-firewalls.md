# Firewalls

A firewall decides which network traffic is allowed through and which is blocked, based on a set of rules — the single most fundamental network security control, and usually the first line of defense between a network (or a single host) and everything else.

## Packet filtering vs stateful inspection

- **Packet filtering (stateless)** — evaluates each packet in isolation against rules (source/destination IP, port, protocol). Fast and simple, but has no memory of a connection's history, which makes some legitimate patterns awkward to allow safely (e.g. permitting return traffic for outbound connections without also blanket-allowing all inbound traffic on that port).
- **Stateful inspection** — tracks the state of active connections, so a rule can say "allow inbound traffic that's part of a connection *we* initiated outbound" without needing a separate, permanently-open inbound rule. This is what nearly all modern firewalls (including host-based ones like `iptables`/`nftables` and cloud security groups) actually do by default.

## A concrete example: `iptables` (Linux)

```bash
# default policy: drop everything not explicitly allowed
iptables -P INPUT DROP

# allow traffic on established/related connections (stateful — the reply to something we or a client initiated)
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# allow SSH in from a specific trusted subnet only, not the whole internet
iptables -A INPUT -p tcp -s 10.0.0.0/24 --dport 22 -j ACCEPT

# allow inbound HTTPS from anywhere (a public web server)
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

The `-P INPUT DROP` default-deny stance is the important part conceptually — a secure firewall configuration blocks everything by default and explicitly allows only what's needed, rather than allowing everything and trying to block specific known-bad traffic (a losing game, since you can't enumerate every bad thing in advance).

## Network firewalls vs host-based firewalls

- **Network firewall** — a dedicated device or appliance sitting at a network boundary (between a LAN and the internet, or between network segments — see [[02-network-segmentation|network-segmentation]]), protecting everything behind it at once.
- **Host-based firewall** (`iptables`/`nftables` on Linux, Windows Defender Firewall) — runs on an individual machine, protecting that machine specifically, and still valuable even behind a network firewall as a second layer (defense in depth) — if one host on a network gets compromised, host-based firewalls on other machines limit how far the compromise can spread laterally.

## Next-Generation Firewalls (NGFW) and application-layer awareness

Traditional firewalls decide based on IP/port/protocol — a NGFW can also inspect traffic content at the application layer (recognizing that traffic on port 443 is actually a specific web application doing a specific thing, not just "some HTTPS traffic"), and often integrates intrusion prevention (see [[04-intrusion-detection-and-prevention|intrusion-detection-and-prevention]]) directly. This matters because plenty of malicious traffic today deliberately uses standard, normally-allowed ports (443, 80) to blend in — a port/protocol-only firewall has no way to distinguish it from legitimate traffic on the same port.

## Web Application Firewalls (WAF) — a specialized, higher-layer case

A WAF sits in front of a web application specifically and filters based on HTTP-level patterns — blocking requests that look like SQL injection or XSS attempts (see [[07-exploitation-concepts|exploitation-concepts]]) before they reach the application at all. Valuable as a mitigating control, but explicitly a mitigation layered on top of secure coding (see [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]) — not a substitute for fixing the underlying vulnerability, since WAF rules can be bypassed with a sufficiently crafted payload.

## Gotchas

- A firewall with an overly permissive rule (e.g. allowing a broad port range "just to get something working" and forgetting to tighten it later) provides much less protection than it appears to — rule review/audit is an ongoing task, not a one-time setup step.
- A firewall only controls traffic that passes through it — traffic between two hosts on the same, unsegmented network segment (see [[02-network-segmentation|network-segmentation]]) doesn't necessarily transit the firewall at all, which is exactly why segmentation and host-based firewalls both still matter even with a strong network firewall in place.
- Default-allow configurations ("block known bad") are a common early-career mistake — default-deny plus explicit allow rules is the more defensible posture, covered above.

## Related
- [[02-network-segmentation|network-segmentation]]
- [[04-intrusion-detection-and-prevention|intrusion-detection-and-prevention]]
- [[cybersecurity/04-web-security/README|web-security]]
