# Cybersecurity — live runs still to do

The pentesting lessons are written against targets the learner owns, but the commands and
exploits in them have **not been run yet** while writing (same policy as the framework lessons:
write first, run later, on an isolated setup). This file lists what to actually execute and
confirm before any lesson is marked fully verified. Every item assumes the owned-target model:
your own app, a real open-source app you cloned onto **your own VPS**, a PDF you locked, and a
database of dummy accounts you seeded. Nothing belonging to anyone else.

## The three target tiers (decided 2026-11-24)

The worked examples are written against **tier 1** so they're reproducible; practice tasks extend to tiers 2 and 3.

1. **Tier 1 — OWASP Juice Shop, local Docker.** Runnable now, no VPS. The teaching target for every worked example. `docker run -d -p 3000:3000 bkimminich/juice-shop`.
2. **Tier 2 — a real production-grade OSS app on your own VPS.** Added when you rent the box.
3. **Tier 3 — your own app, a PDF you locked, a database of dummy accounts.** For app-sec, document and password cracking.

## Lab the runs need

- [ ] Docker on the laptop, Juice Shop pulled and running (tier 1). Confirm it loads on `localhost:3000`.
- [ ] A VPS you control (any provider), with a snapshot taken before testing so you can roll back (tier 2).
- [ ] One real open-source web app deployed to the VPS (the real engagement target). Record which one.
- [ ] Your own small app deployed, for the app-sec track (tier 3).
- [ ] A locked PDF you created, for the document-cracking lesson (tier 3).
- [ ] A throwaway database seeded with dummy accounts and known passwords, for the hashing lesson (tier 3).
- [ ] Kali (or a vanilla Linux box with the tools) to run the attacks from.

## Per-lesson checks

### 02-ethical-hacking
- [ ] 01 rules-of-engagement — no commands; confirm the authorization decision chart matches the lab.
- [ ] 03 reconnaissance — run the passive + active recon commands against your own deployed target.
- [ ] 06 scanning-and-enumeration — run the real `nmap`/enumeration commands against the VPS target; confirm the outputs in the lesson.
- [ ] 07 exploitation — reproduce each vulnerability class on the owned target; capture the proof.
- [ ] 08 common-tools — run the Burp intercept→Repeater workflow against Juice Shop (basket IDOR).
- [ ] 09 post-exploitation-and-reporting — produce the actual report from a real finding.
- [ ] 10 pdf-and-document-security — lock a PDF, then crack it; confirm timings.
- [ ] 11 wifi-security-testing — only against your own access point.
- [ ] 12/13 practice-exercises — work them end to end on the lab.

### 03-network-security
- [ ] 01 firewalls — UFW default deny on the VPS (SSH rule first), `nft list ruleset` matches the lesson's shape, rescan shows 5432 `filtered`, a `UFW BLOCK ... DPT=5432` line appears in `/var/log/ufw.log`. Confirm the Docker `-p` bypass of UFW for real (publish a port, rescan).
- [ ] 02 network-segmentation — run the `seg-lab` Compose file; confirm the four tests (only app → db succeeds; `getent` from web fails; db → internet gives "Network is unreachable"; nmap 5432 closed). Confirm image tags `nginx:1.27` / `postgres:16` still pull.
- [ ] 03 vpns-and-encryption-in-transit — WireGuard laptop ↔ VPS, SSH over `10.8.0.1`, then move SSH behind `wg0`; public scan shows TCP 22 `filtered` and UDP 51820 `open|filtered`; `journalctl -u ssh` logins come from `10.8.0.2`. Check the unit name (`ssh` vs `sshd`) on the VPS's distro.
- [ ] 04 intrusion-detection-and-prevention — Suricata on `lo` with `-k none -S local.rules`; confirm both rules fire (scan `sid:1000002`, login SQLi `sid:1000001`) and paste the real `fast.log` lines into the lesson. Confirm HTTP is detected on port 3000, the `threshold` syntax, and that `admin@juice-sh.op'--` slips past rule 1.

### 05-cryptography
- [ ] 01 what-is-cryptography — the base64/sha256sum/openssl commands and the JWT decode were checked while writing; just rerun to confirm.
- [ ] 02 symmetric-encryption — `pip install cryptography`, run `aes_lab.py`: three identical ECB blocks, three different GCM blocks, `InvalidTag` on the flipped bit. Replace the illustrative hex in the lesson with a real run.
- [ ] 03 hashing-and-integrity — run `webhook.py`; the signature in the lesson (b20e72f1…) was computed, so it should match exactly: genuine True, tampered False, forged False.
- [ ] 04 asymmetric-encryption — run `hybrid.py` (same shared secret: True; Bayo reads b'meet at 3'). Stretch: check a `wg pubkey` matches the Python-derived X25519 public key.
- [ ] 05 digital-signatures-and-pki — run `sign.py` (64-byte signature, VALID then INVALID). The openssl CA commands and their output were run while writing (OpenSSL on Fedora).
- [ ] 06 cryptographic-attacks — `weak_token.py` was run once while writing (recovered in 223 tries). Install gitleaks and run `gitleaks detect --source .` on a real repo; confirm the subcommand name for the installed version.

### 06-attacks-and-threats
- [ ] 01 social-engineering — run the two `dig +short TXT` commands against a real domain; confirm the SPF/DMARC output shape. The email headers are illustrative (made-up domain).
- [ ] 02 network-attacks — run the ARP-spoofing Docker lab (`arp-lab` compose + `spoof.py`): confirm the victim's `ip neigh` shows the attacker's MAC for 10.9.0.2 after the attack, the sniff captures the victim's ICMP, and the duplicate-MAC detection finds it. Then the two defence steps (no-forward = DoS; static ARP entry holds). Check scapy installs in the slim image and NET_ADMIN/NET_RAW caps work.
- [ ] 03 web-application-attacks — no commands of its own (uses Juice Shop from 02-ethical-hacking). Re-verify the OWASP Top 10 2025 ordering against owasp.org when the final (non-RC) list is published; A06–A08 were reconstructed, not confirmed.
- 04 password-malware-and-exploits — `detect.py` was run while writing (output matches the lesson). The practice-task extended detector (time window, failure-then-success) is still [ ] to build and run.

### 04-web-security
- 01 and 04 have runnable labs checked by `python3 labs/run.py input-validation-and-output-encoding security-headers-and-same-origin-policy` — not live runs, already verified.
- [ ] 02 secure-authentication — run `seed_users.py` (needs `pip install bcrypt`), confirm `ada`/`dami` share a SHA-256 hash and bcrypt hashes start `$2b$12$`; crack both files with hashcat (`-m 1400`, `-m 3200`) and record which accounts fall and the `-b` benchmark speeds on the laptop CPU. Confirm `correct-horse-battery-staple` is not in rockyou.
- [ ] 03 https-and-tls — needs a domain pointed at the VPS. `certbot --nginx --redirect`, `renew --dry-run`, `ssl_protocols` + HSTS, then the checks: 301 redirect, HSTS header, `-tls1_1` refused, nmap `ssl-enum-ciphers` grade A, crt.sh lists only your certs. Save the before/after nmap output.

### 07-security-operations
- [ ] 01 defensive-architecture — run `ss -tulpn | grep LISTEN` and `sudo lynis audit system` on the lab box; record the hardening index, disable an unused service (and/or bind a port to localhost, enable the firewall), and re-run both; confirm the port list shortened and the index rose. Save the before/after numbers.
- [ ] 02 logging-siem-and-detection — the `journalctl`/`grep`/`awk` SSH-spray detection: spray your own lab box, confirm the one-liner and the Sigma logic would fire, and that it stays quiet on an hour of baselined normal traffic. Build the second detection (sudo failures, or 404s→200 on an admin path) end to end.
- [ ] 03 threat-intelligence-and-hunting — run the ATT&CK-mapped hunt `awk` query against the lab `auth.log`; confirm it returns the spraying source IP and nothing on clean traffic. Verify the technique IDs (T1595, T1190, T1110.003, T1557.002) on attack.mitre.org.
- [ ] 04 incident-response — rehearse the SSH-compromise runbook's identification→containment commands on your own lab box (capture `ss`/`ps`/`last` first, then `pkill`/`usermod -L`/`iptables DROP`); confirm the eradication hunt (`crontab -l`, `authorized_keys`, `grep <ip>`) finds a planted persistence artefact.
- [ ] 05 forensics-and-malware-analysis — create the EICAR `sample.txt` (`printf`), confirm `sha256sum` = `275a021b…fd0f` (computed while writing), `file` reports ASCII text, and `strings` shows the one line; if a scanner is installed, confirm it flags the file. Build and run `triage.sh`, then verify `sha256sum -c MANIFEST.sha256` reports OK for every collected file.

### 08-governance-risk-and-compliance
Most of this section produces **documents, not runs** (risk register, career plan, policy set) — build those in your notes. The one live run is the dependency scan:
- 04 third-party-and-supply-chain-risk — on a real Python or Node project: `pip list --format=freeze > sbom.txt` (or `npm ls --all`), then `pip install pip-audit && pip-audit` (or `npm audit`). Record the count of direct vs transitive deps, every known vulnerability + its fix version, and time an "are we affected by X?" `grep` of the SBOM. Bonus: wire the scanner into CI. Confirm `pip-audit`'s current subcommand/flags for the installed version.
- 01 risk-and-frameworks — build a scored, ranked risk register for an owned app (asset/threat/vuln, likelihood×impact 1–5, treatment, owner, revisit trigger on each "accept"). Document, not a run.
- 03 governance-and-the-human-layer — write a four-level policy set (policy→standard→procedure→guideline) for one control, pick the auditable standard, and compute one metric (e.g. phishing click rate, % MFA, patch latency). Document, not a run.

_(Add lessons here as the rebuild reaches them.)_

## Done
_(Move items here once run and confirmed, with the date.)_
