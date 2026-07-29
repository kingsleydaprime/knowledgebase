# Network Segmentation

A flat network — every device able to reach every other device directly — means a single compromised machine can potentially reach anything else on that network. Segmentation splits a network into smaller, isolated zones with controlled traffic between them, so a breach in one zone doesn't automatically become a breach of everything.

## VLANs — the basic building block

A VLAN (Virtual LAN) logically separates devices on the same physical network infrastructure into distinct broadcast domains, as if they were on separate physical networks, without needing separate physical switches for each segment. Traffic between VLANs has to pass through a router or firewall (see [[01-firewalls|firewalls]]), which is exactly where segmentation's actual security value comes from — that's the choke point where rules can be enforced.

```
# illustrative switch config shape (Cisco-style), not exhaustive:
vlan 10
 name Corporate
vlan 20
 name Guest
vlan 30
 name IoT-Devices
interface GigabitEthernet0/1
 switchport access vlan 10
```

## Common segmentation patterns

- **Guest network isolation** — guest Wi-Fi traffic is placed on its own VLAN with no route to internal/corporate systems, so a compromised or malicious guest device can't reach anything sensitive.
- **IoT/device isolation** — smart home and IoT devices (often poorly secured, rarely patched) go on their own segment, so a compromised smart bulb or camera can't be used as a stepping stone to reach a laptop or NAS holding real data.
- **DMZ (Demilitarized Zone)** — a segment for systems that must be reachable from the internet (a public web server, a mail server), isolated from the internal network so that if one of those internet-facing systems is compromised, the attacker still doesn't have direct access to internal systems — they've only reached the DMZ, one more segmentation boundary away from anything sensitive.

```
Internet <-> [Firewall] <-> DMZ (web server, mail server)
                  |
              [Firewall]
                  |
           Internal network (workstations, internal databases)
```

## Zero Trust — segmentation taken to its logical extreme

Traditional network security often assumes "inside the network perimeter = trusted." **Zero Trust** rejects that assumption entirely: no device or user is trusted by default based on network location alone; every request is authenticated and authorized individually, regardless of whether it originates "inside" or "outside" the traditional perimeter. This is a response to a real failure mode of perimeter-only security — once an attacker gets past the perimeter (via phishing, a single compromised credential), a purely perimeter-based model offers little further resistance; Zero Trust assumes breach is possible anywhere and verifies continuously rather than once at the boundary.

## Why segmentation directly limits the damage of a compromise

This is the practical payoff tying back to [[09-post-exploitation-and-reporting|post-exploitation]]'s concept of lateral movement: a well-segmented network turns "one compromised device" into a contained incident, while a flat network turns the same single compromise into potential access to everything. Segmentation doesn't prevent the initial compromise — it limits what that compromise can reach afterward, which is exactly the kind of control that shows up as the difference between a minor incident and a full breach in a post-incident report.

## Gotchas

- Segmentation only helps if the boundaries between segments are actually enforced (firewall rules between VLANs) — a VLAN with an overly permissive "allow all" rule to every other VLAN provides the isolation label without the actual security benefit.
- Segmentation adds real operational complexity (more rules to maintain, more places a legitimate service can be accidentally blocked) — it's a genuine tradeoff against simplicity, not a free win, which is part of why smaller/less mature organizations sometimes skip it despite the security benefit.
- IoT devices are a commonly underestimated segmentation priority — they're frequently the least secure devices on a home or small-office network and the easiest entry point, precisely why isolating them specifically is called out above.

## Related
- [[01-firewalls|firewalls]]
- [[03-vpns-and-encryption-in-transit|vpns-and-encryption-in-transit]]
- [[04-intrusion-detection-and-prevention|intrusion-detection-and-prevention]]
