# Network Security

Protecting data as it moves between systems, and limiting how far a compromise can spread once something goes wrong. Where [[cybersecurity/02-ethical-hacking/README|ethical-hacking]] is framed offensively (how these boundaries get tested/bypassed), this folder is framed defensively (how to build the boundaries in the first place) — the same concepts, viewed from the other side.

## Reading order
1. [[01-firewalls|firewalls]] — **[Beginner]** — packet filtering vs stateful inspection, default-deny, network vs host-based vs WAF
2. [[02-network-segmentation|network-segmentation]] — **[Intermediate]** — VLANs, DMZs, Zero Trust, why a flat network turns one compromise into a full breach
3. [[03-vpns-and-encryption-in-transit|vpns-and-encryption-in-transit]] — **[Intermediate]** — VPN protocols (IPsec/OpenVPN/WireGuard), and what encryption in transit does and doesn't protect
4. [[04-intrusion-detection-and-prevention|intrusion-detection-and-prevention]] — **[Advanced]** — IDS vs IPS, signature vs anomaly detection, SIEM correlation

## Related
- [[cybersecurity/README|cybersecurity curriculum map]]
- [[cybersecurity/04-web-security/README|web-security]] — the application-layer counterpart to this folder's network-layer focus
