# Firewalls and Hardening

**[Intermediate]** — closing a server's front door. The minimum you owe any machine with a public IP.

## The kid version first

Every listening service is a door. A firewall decides which doors face the street.

The default on a fresh cloud VM is usually **no firewall at all** — everything a service binds to `0.0.0.0` is reachable from the entire internet, and automated scanners find a new public IP within minutes, not days. Not hypothetically: put an unfirewalled box online and watch `/var/log/auth.log` fill with SSH attempts from a dozen countries by the next morning.

## First, know what's actually exposed

Before adding rules, find out what's listening:

```bash
sudo ss -tulpn          # every listening TCP/UDP socket, with the process
```

Read the address column carefully — it's the whole point:

- `127.0.0.1:5432` — localhost only. **Not** reachable from outside. Fine.
- `0.0.0.0:5432` — every interface. Reachable by anyone who can route to you.

**Binding a service to localhost is a stronger control than any firewall rule**, because it can't be undone by a mistyped rule later. If Postgres only ever serves an app on the same box, bind it to `127.0.0.1` and the firewall becomes a second line of defence rather than the only one. This is the single highest-value hardening step on this page.

## ufw — the Ubuntu/Debian path

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH          # DO THIS BEFORE ENABLING
sudo ufw allow 80,443/tcp
sudo ufw enable
sudo ufw status verbose
```

> **Allow SSH before you enable the firewall.** Enabling a default-deny policy over an SSH session without an SSH rule locks you out of the machine instantly. On a VPS with console access you can recover; on one without, you rebuild. This mistake is made constantly, including by people who know better, because the enable command feels like the last step rather than the dangerous one.

Restrict by source where you can — administrative ports have no business being globally reachable:

```bash
sudo ufw allow from 203.0.113.7 to any port 22 proto tcp
```

## firewalld — the RHEL/Fedora path

Same job, different model: hosts are grouped into **zones**, and interfaces are assigned to a zone.

```bash
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --add-service=https --permanent
sudo firewall-cmd --reload
```

**The `--permanent` gotcha** is the thing to internalise: without it, a rule applies immediately and vanishes on reload/reboot. With it, the rule is written to disk but *doesn't apply until you reload*. So a rule added with `--permanent` and no `--reload` appears to do nothing, and one added without `--permanent` appears to work and then silently disappears next week.

The safe habit is to add it both ways — once live to test, once permanent to persist — or add permanent then reload and re-verify.

Underneath both tools is **nftables** (which replaced iptables). You rarely touch it directly, but that's what `nft list ruleset` shows you when a rule isn't behaving as the front-end suggests.

## SSH hardening

The one service that's almost always exposed, and therefore the one worth spending effort on. In `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no        # keys only — the big one
```

```bash
sudo sshd -t                     # VALIDATE THE CONFIG FIRST
sudo systemctl reload sshd
```

Keep your current session open and open a *second* one to test before closing the first. `sshd -t` catches syntax errors, but not "I disabled password auth and my key isn't installed."

Disabling password authentication ends credential-stuffing against your box outright — it's worth more than any rate-limiting or port-moving. Moving SSH to a non-standard port reduces log noise but is not security; scanners check all ports. **fail2ban** is a reasonable addition for noise reduction, unnecessary once passwords are off. See [[devops/01-linux/14-basic-ssh-config|basic ssh config]].

## SELinux and AppArmor

A firewall controls *who can reach a process*. These control *what a process can do once running* — so a compromised web server can't read `/etc/shadow` even as root.

| | Ubuntu/Debian | RHEL/Fedora |
|---|---|---|
| System | **AppArmor** (path-based) | **SELinux** (label-based) |
| Status | `sudo aa-status` | `getenforce` |
| Logs | `journalctl -k \| grep apparmor` | `sudo ausearch -m avc -ts recent` |

When a service mysteriously can't read a file it clearly has Unix permissions for, this is usually why — and the standard advice on the internet is "disable SELinux," which trades a solved problem for an unsolved one. Read the denial (`ausearch -m avc`) and fix the label instead; the denial message usually names the exact fix.

## The baseline

For any internet-facing machine:

1. Keys-only SSH, root login off
2. Default-deny inbound, allow only what's needed (**SSH rule first**)
3. Databases and internal services bound to `127.0.0.1`
4. Automatic security updates enabled
5. AppArmor/SELinux left on
6. A non-root user with sudo for daily work

That takes ten minutes and removes essentially all opportunistic attacks. Everything beyond it is diminishing returns until you have something genuinely worth targeting.

## Key insight

Check `ss -tulpn` before you write a single rule — most exposure is a service bound to `0.0.0.0` that had no business being there, and binding it to localhost fixes the problem more durably than any firewall rule. Then: allow SSH *before* enabling default-deny.

## Related
- [[devops/01-linux/14-basic-ssh-config|Basic SSH Config]] — keys, config files, the session you shouldn't close
- [[devops/01-linux/15-rhcsa/12-manage-network-security|RHCSA: Manage Network Security]] — firewalld zones and rich rules in depth
- [[devops/01-linux/15-rhcsa/07-manage-selinux-security|RHCSA: SELinux]] — contexts, booleans, and diagnosing denials properly
- [[cybersecurity/README|Cybersecurity]] — the attacker's view of everything above
- [[devops/04-vps/vps-setup|VPS Setup]] — where this gets applied to a real deployed box
