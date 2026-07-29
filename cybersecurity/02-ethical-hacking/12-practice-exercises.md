# Ethical Hacking — Practice Exercises

> Goal-only tasks, no walkthroughs — same format as the [[../../devops/01-linux/15-rhcsa/15-practice-exercises|RHCSA practice exercises]]. You're told the objective, not the commands; a real engagement doesn't hand you the payload either. Run every one of these against the lab built in [[05-home-lab-setup|home-lab-setup]] — **never against anything you don't own or don't have explicit written authorization to test**, per [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]].

## How to use this

- Snapshot the relevant target VM before each exercise. Several of these are meant to leave the target in a broken/compromised state — that's the point, and you revert after, not before.
- Try to complete each task using the concepts in [[07-exploitation-concepts|exploitation-concepts]] and the tools in [[08-common-tools|common-tools]] *before* looking up a specific walkthrough for that exact CVE — the goal is transferable skill, not memorizing one target's specific solution.
- Write a one-paragraph note after each exercise: what you found, how, and what the fix would be. This is the actual habit that separates "ran a tool" from "did a pentest" — see [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]].
- Time yourself loosely once you've done a category once cold. Not to simulate exam pressure like the RHCSA drills — this is about noticing which categories are still slow for you, which tells you where to spend more repetition.

---

## Reconnaissance & Scanning

1. Against Metasploitable2, determine every open TCP port and identify the service + version running on each, without yet trying to exploit anything.
   **Verify:** you have a written list of port → service → version for at least 10 open ports.

2. From that service list, identify which specific service(s) are running a version with a **publicly documented, named vulnerability** (not just "old" — an actual CVE or well-known exploit name).
   **Verify:** you can name the vulnerability and cite where you confirmed it (searchsploit, a CVE database, exploit-db).

3. Enumerate every share exposed by Metasploitable2's file-sharing service and determine which, if any, are accessible without authentication.
   **Verify:** a list of share names with their access level (readable/writable/none), gathered without guessing — actually enumerated.

---

## Exploitation — Network Services

4. Gain a remote shell on Metasploitable2 using one of the vulnerabilities identified in exercise 2, via a purpose-built exploitation framework rather than hand-writing an exploit.
   **Verify:** a working shell with `whoami` returning a result, and you can state which specific CVE/vulnerability you used.

5. Once you have a shell, determine what privilege level you landed at, and — if it isn't already root — escalate.
   **Verify:** `id` shows `uid=0(root)`.

6. Gain a shell using an *entirely different* vulnerable service than the one from exercise 4 (Metasploitable2 has several) — don't reuse the same technique twice.
   **Verify:** a second, independent shell via a different named vulnerability.

---

## Password & Credential Testing

7. Metasploitable2 has at least one service accepting weak/default credentials over the network directly (not a hash to crack — a live login attempt). Find it and demonstrate a successful login using a wordlist-based attack, not a guessed password.
   **Verify:** a successful authenticated session, plus the specific username/password pair the attack found.

8. Extract a password hash from a compromised target (from exercise 4 or 6) and crack it offline.
   **Verify:** a plaintext password recovered, plus which hash format you identified it as before choosing a cracking mode.

---

## Web Application Testing (DVWA)

9. At DVWA's **Low** security setting, find and demonstrate a SQL injection that extracts data the application was never meant to return (e.g., every username and password hash in the database), first by hand in the browser/Burp before reaching for an automated tool.
   **Verify:** actual extracted data, plus the specific injected input that caused it.

10. Confirm the same injection using an automated tool, and use it to enumerate the full database schema (table names, column names) — not just the one table from exercise 9.
    **Verify:** a full list of tables and columns the tool extracted.

11. Find a reflected or stored XSS vulnerability in DVWA and demonstrate impact beyond a plain `alert()` popup (e.g., something that would exfiltrate a cookie/session token in a real scenario — you don't need a live receiving server, describing the mechanism precisely counts).
    **Verify:** a working payload plus a one-sentence explanation of what it would actually let an attacker do.

12. Find a broken access control issue in DVWA — access another simulated user's data or action by manipulating a request, without ever being given that access directly.
    **Verify:** you can show the exact parameter/ID you changed and the unauthorized data/action it exposed.

13. Repeat exercises 9 and 11 at DVWA's **Medium** setting. Note specifically *what* changed in the application's defenses and how you adapted the technique — not just that it eventually worked.
    **Verify:** a short written comparison of the Low vs. Medium bypass.

---

## Wireless (requires the external adapter from [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]])

14. Against a WiFi network you own and control, capture a WPA2 4-way handshake and crack the pre-shared key offline using a wordlist you know contains it (i.e., prove the pipeline works before testing against an unknown/strong password).
    **Verify:** the recovered key matches the network's actual configured password.

15. Determine whether that same network has WPS enabled, and if so, what that means for its practical security regardless of WPA2 password strength.
    **Verify:** a clear yes/no on WPS status plus a one-sentence explanation of the risk if enabled.

---

## Reporting

16. Take exercises 4–13 (whichever you completed) and write them up as a short-form finding report: what was found, how it was found, actual demonstrated impact, and a concrete remediation for each — structured the way [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]] describes, not just a command transcript.
    **Verify:** someone who wasn't in the room could read the report and understand exactly what's broken and how to fix it, without needing you to explain it verbally.

---

## Hosted platforms — once the lab exercises feel routine

[[08-common-tools|common-tools]] already points at **HackTheBox** and **TryHackMe** for legally-sanctioned targets beyond your own lab. The natural next step after this file: pick one beginner-track machine/room per category above (a "starting point" HTB box, a TryHackMe web-focused room) and repeat the same exercises against a target you didn't build yourself — that's the real test of whether the skill transferred or whether you'd just memorized Metasploitable2 and DVWA specifically.
