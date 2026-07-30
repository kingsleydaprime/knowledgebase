# Manage Network Security

> RHCSA V10

Part of [[README|RHCSA V10]]. RHEL's firewall stack — where Ubuntu/Debian notes in this vault use `ufw` (see [[devops/01-linux/13-network-fundamentals|Networking Fundamentals]]), RHEL uses **firewalld**. The actual kernel-level packet filter underneath is **`nftables`** — the modern successor to the older `iptables`/`ip6tables` (still convertible via `iptables-translate`) — and `firewalld` is the recommended, higher-level front end to it; you almost never touch `nftables` rules directly.

---

## firewalld vs. ufw — the mental model shift

`ufw` is dead simple: allow/deny by port or service, done. `firewalld` adds a layer of **zones** — named trust levels an interface belongs to, each with its own independent rule set. The idea is a laptop's wifi interface (untrusted network) and a server's internal NIC (trusted network) can have completely different rules without juggling one flat rule list.

```bash
sudo systemctl status firewalld       # confirm it's running — it is, by default, on RHEL
sudo firewall-cmd --state              # quick running/not-running check
```

---

## Zones

Every zone allows return traffic for connections *you* initiated, and all outbound traffic, by default — the table below is specifically what's allowed **inbound**, unsolicited:

| Zone | Default inbound behavior |
|---|---|
| `trusted` | Accept everything |
| `home` / `internal` | Reject unless related to outbound traffic, or matches `ssh`, `mdns`, `ipp-client`, `samba-client`, `dhcpv6-client` |
| `work` | Same idea, narrower list: `ssh`, `ipp-client`, `dhcpv6-client` |
| `public` | **Default zone for newly added interfaces** — narrower still: just `ssh`, `dhcpv6-client` |
| `external` | Just `ssh` — plus masquerades (NAT) outgoing IPv4 traffic forwarded through it, for a router-like box |
| `dmz` | Just `ssh` — publicly reachable, but isolated from the rest of the internal network |
| `block` | Reject **all** incoming (not just unmatched) |
| `drop` | Drop all incoming silently — doesn't even send back an ICMP rejection, unlike `block` |

Which zone a packet actually lands in is decided in this order: **source IP's assigned zone** (if you've explicitly bound an address/range to a zone) → **the zone of the interface it arrived on** → the **default zone** as a last resort. `NetworkManager` can also auto-switch a connection's zone based on which network you've joined — the practical payoff is a laptop that's `home`-zoned on your home Wi-Fi (SSH reachable) and automatically drops to something tighter on a coffee-shop network, without you touching firewalld by hand.

```bash
firewall-cmd --get-default-zone            # which zone new interfaces get by default
firewall-cmd --get-active-zones            # zones currently in use, and which interface is in each
firewall-cmd --zone=public --change-interface=eth0    # move an interface to a specific zone
```

---

## Runtime vs. permanent — the single biggest gotcha

This mirrors the exact trap that shows up in [[07-manage-selinux-security|manage-selinux-security]] with `setsebool -P`. `firewall-cmd` changes are **runtime-only by default** — they vanish on the next `--reload` or reboot unless you also write them to the permanent config.

```bash
sudo firewall-cmd --add-service=http                      # runtime only — works right now, GONE after reload/reboot
sudo firewall-cmd --add-service=http --permanent           # written to config — does NOT apply until reloaded
sudo firewall-cmd --reload                                  # apply permanent changes to the running firewall
```

The safe habit: do **both** together, so runtime state and permanent config never drift apart:
```bash
sudo firewall-cmd --add-service=http --permanent && sudo firewall-cmd --reload
```

---

## Core commands

```
$ firewall-cmd --list-all
public (active)
  target: default
  interfaces: eth0
  services: cockpit dhcpv6-client ssh
  ports: 8080/tcp
```
Reading this: `public` is which zone this is; `services` are allowed by name (self-documenting); `ports` are raw port allows that don't have a named service. This is the single command to run first whenever "is X actually open?" comes up.
```bash
firewall-cmd --list-all                       # full ruleset for the DEFAULT zone
firewall-cmd --zone=public --list-all          # full ruleset for a SPECIFIC zone
firewall-cmd --get-services                    # every named service firewalld knows how to allow by name
firewall-cmd --add-service=ssh --permanent     # allow by service NAME — firewalld maps this to the right port(s) internally
firewall-cmd --add-port=8080/tcp --permanent   # allow by raw port — for anything without a named service definition
firewall-cmd --remove-service=http --permanent # revoke
firewall-cmd --list-services                   # just the allowed services, for the default/current zone
firewall-cmd --list-ports                       # just the allowed raw ports
```

Prefer `--add-service` over `--add-port` whenever a named service exists — it's self-documenting (`--list-all` shows `ssh` instead of an unlabeled `22/tcp`) and some services need more than one port, which the service definition already accounts for.

---

## Rich rules — when zone/service granularity isn't enough

For anything more specific than "allow this service in this zone" — like restricting a port to a single source IP:
```bash
firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.1.50" port port="3306" protocol="tcp" accept' --permanent
firewall-cmd --reload
```
Worth knowing this exists; the exam mostly stays at the service/port level.

---

## SSH hardening — where this connects back

Changing SSH off the default port (covered in [[devops/01-linux/14-basic-ssh-config|Basic SSH Config]]) is a two-system change, not one — this is a real trap:

1. Update `Port` in `/etc/ssh/sshd_config`, restart `sshd`
2. **firewalld** — the new port needs an explicit allow, the old one should be removed:
   ```bash
   firewall-cmd --add-port=2222/tcp --permanent
   firewall-cmd --remove-service=ssh --permanent
   firewall-cmd --reload
   ```
3. **SELinux** — SSH's default policy only expects `sshd_t` to bind port 22. A custom port needs its own label or SELinux blocks `sshd` from even binding it, regardless of what the firewall allows:
   ```bash
   sudo semanage port -a -t ssh_port_t -p tcp 2222
   ```

All three layers — sshd config, firewalld, SELinux — have to agree, or the service either won't start, won't be reachable, or will bind but get silently blocked. This three-layer check is worth running through as a checklist any time "the service should be listening but isn't reachable."
