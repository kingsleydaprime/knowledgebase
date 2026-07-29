# Building the Home Lab — Step by Step

> Turns [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]] from "here's what a lab is" into "here's exactly how to have one running tonight." Everything from here on assumes this lab exists — [[12-practice-exercises|practice-exercises]] is written against it directly.

**Everything below is against machines you own, on a network isolated from your real one. Nothing here ever points at a target you don't control.** That's not a legal disclaimer tacked on — it's what makes the rest of this folder practice instead of a crime, per [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]].

---

## What you're building

```
┌─────────────────────────────────────────┐
│         Host-only virtual network          │  ← isolated, no route to your real LAN
│                                              │
│   Kali Linux (attacker)  ──────────────► Metasploitable2 (target)
│   192.168.56.10                            192.168.56.20
│                                              │
│                                    DVWA (target, web-focused)
│                                    192.168.56.30
└─────────────────────────────────────────┘
```

Three VMs: one attacker, two deliberately-vulnerable targets covering different practice ground — Metasploitable2 for network/service-level exploitation, DVWA for web application testing specifically.

---

## Step 1 — Hypervisor

VirtualBox (free, cross-platform) is the standard choice for this — it's what most Kali/Metasploitable documentation assumes, which matters a lot when you inevitably need to search an error message.

```bash
# Ubuntu/Debian host
sudo apt install virtualbox

# Fedora/RHEL host
sudo dnf install VirtualBox

# macOS/Windows — download the installer directly from virtualbox.org
```

---

## Step 2 — The isolated network, first

Build the network before importing any VM — get this wrong and a "vulnerable by design" VM ends up reachable from your real home network.

1. VirtualBox → **File → Host Network Manager → Create**
2. This creates a host-only adapter, e.g. `vboxnet0`, typically defaulting to `192.168.56.0/24`
3. **Every VM in this lab uses this adapter, and nothing else** — no bridged adapter, no NAT-with-port-forwarding, unless you specifically know why you're changing that for one exercise

Host-only means: the VMs can talk to each other and to your host machine, but **not** to your real router or the wider internet by default. That containment is the entire point.

---

## Step 3 — Kali Linux (attacker)

1. Download the pre-built VirtualBox OVA from kali.org (official downloads page) — this skips a manual OS install entirely
2. VirtualBox → **File → Import Appliance**, point at the `.ova`
3. Before first boot: **Settings → Network → Adapter 1 → Attached to: Host-only Adapter → vboxnet0**
4. Boot it, log in (default creds are on Kali's download page — change them immediately: `passwd`)
5. Confirm networking:
   ```bash
   ip addr show eth0        # should show a 192.168.56.x address
   ping 192.168.56.1        # the host-only adapter's gateway — confirms basic connectivity
   ```

---

## Step 4 — Metasploitable2 (network-level target)

Deliberately ancient, deliberately full of known, unpatched, well-documented vulnerabilities — built specifically to be attacked and thrown away.

1. Download from the official Rapid7/SourceForge Metasploitable2 page
2. Import into VirtualBox same as above
3. **Same host-only adapter, same network**
4. Boot it (default login: `msfadmin` / `msfadmin` — this is intentional, it's a target)
5. Confirm its IP:
   ```bash
   ifconfig eth0        # older tooling on this intentionally old VM — ip addr may not even exist here
   ```
6. From Kali, confirm reachability:
   ```bash
   ping 192.168.56.20        # or whatever IP Metasploitable actually got
   ```

**Never expose this VM to a bridged/real network.** It's running years-old, genuinely exploitable services on purpose.

---

## Step 5 — DVWA (web application target)

Either the pre-built VM image, or install it inside a minimal Linux VM yourself (more setup, more understanding of the moving parts — reasonable either way, same tradeoff [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]] describes for Kali vs. vanilla Linux):

```bash
# Manual install path, inside a fresh minimal Ubuntu/Debian VM on the SAME host-only network
sudo apt install apache2 mysql-server php php-mysqli git
git clone https://github.com/digininja/DVWA.git /var/www/html/dvwa
# configure config/config.inc.php with DB credentials, create the dvwa database in MySQL,
# visit http://<vm-ip>/dvwa/setup.php in a browser to finish setup and set difficulty level
```

Set DVWA's security level to **Low** for your first pass through any given vulnerability class — the point right now is confirming you can execute the technique at all, not fighting the intentionally-hardened "Impossible" level on your first attempt.

---

## Step 6 — Snapshot everything, immediately

Before running a single exercise:

```
VirtualBox → select each VM → Machine → Take Snapshot → "clean-install"
```

This is what makes the lab genuinely disposable — break something, misconfigure a service, corrupt a database testing SQLi: revert to the snapshot in under a minute instead of rebuilding from scratch. Take a fresh snapshot again after any setup step you don't want to repeat (e.g., right after DVWA's initial setup completes).

---

## Verifying the whole lab is actually ready

From Kali:
```bash
nmap -sn 192.168.56.0/24              # host discovery sweep across the whole lab subnet — should list Kali, Metasploitable2, and DVWA's VM
nmap -sV 192.168.56.20                # Metasploitable2 — should show a long list of old, named services with version numbers
curl -I http://192.168.56.30/dvwa/    # DVWA reachable over HTTP
```

If all three come back, the lab is live — move to [[12-practice-exercises|practice-exercises]].

---

## Gotchas specific to lab setup (distinct from the general ones in [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]])

- **Adapter mismatch** — the single most common "nothing can reach anything" cause is one VM accidentally left on NAT while the others are on host-only. Check every VM's network settings individually; VirtualBox doesn't warn you about the mismatch.
- **Metasploitable2 has no DHCP reservation guarantee** — its IP can change between reboots on some host-only DHCP configs. Re-run the discovery `nmap -sn` sweep after any reboot rather than assuming the IP from last time.
- **Host firewall on your actual machine** — some host OS firewalls (particularly on macOS/Windows hosts) can interfere with host-only adapter traffic. If VMs can't reach each other despite correct adapter settings, this is the next thing to check.
