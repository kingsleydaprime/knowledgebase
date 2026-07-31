# Social Engineering

**[reference]** — from the roadmap.sh cyber-security roadmap. Educational/defensive: understanding these so you can recognize and stop them.

## Why it's the #1 vector

The easiest way past a firewall is to convince someone to open the door. **Social engineering** attacks the human, not the technology — and it works because it exploits trust, authority, urgency, fear, and helpfulness, which no patch fixes. The overwhelming majority of real breaches start here (a phished credential), which is why security awareness training and technical controls that assume humans *will* be fooled ([[cybersecurity/04-web-security/02-secure-authentication|MFA]], least privilege) matter more than any single tool.

## Phishing and its variants

**Phishing** — fraudulent messages (usually email) that impersonate a trusted entity to steal credentials, deliver malware, or trigger a payment. The variants are named by channel and target:

| Term | What it is |
|---|---|
| **Phishing** | mass fraudulent email |
| **Spear phishing** | targeted at a specific person, personalized with research |
| **Whaling** | spear phishing aimed at executives ("big fish") |
| **Smishing** | phishing via SMS |
| **Vishing** | phishing via voice call (often impersonating IT/bank support) |
| **Pharming** | redirecting a legitimate URL to a fake site (via [[cybersecurity/06-attacks-and-threats/02-network-attacks|DNS poisoning]]/host-file tampering) |
| **BEC** (business email compromise) | impersonating an executive/vendor to authorize a fraudulent wire transfer — one of the costliest attack types |

The tells: urgency ("act now or your account is locked"), a mismatched sender/URL, unexpected attachments, requests to bypass process. Defenses: email authentication ([[cybersecurity/03-network-security/README|SPF/DKIM/DMARC]]), link/attachment scanning, MFA (a phished password alone isn't enough), and training.

## In-person and physical

- **Pretexting** — inventing a scenario/identity to extract info ("Hi, I'm from IT, I need your password to fix your account").
- **Baiting** — leaving malware-loaded USB drives where a curious victim will plug them in.
- **Tailgating / piggybacking** — following an authorized person through a secure door.
- **Shoulder surfing** — reading credentials/PINs over someone's shoulder.
- **Dumpster diving** — recovering sensitive info from discarded documents/drives.
- **Impersonation** — posing as a delivery driver, contractor, or executive on-site.

## Other manipulation

- **Watering hole** — compromise a website the target group frequents, infecting them when they visit.
- **Quid pro quo** — offering a "service" (fake tech support) in exchange for access/info.
- **Scareware** — fake "your computer is infected!" popups pushing malicious downloads or payment.
- **Typosquatting** — registering misspelled domains (`gooogle.com`) to catch mistyped traffic.

## The defense mindset

You can't patch people, so defense is layered: **training** (recognize the tactics), **process** (verify unusual requests out-of-band — call the "CEO" back on a known number), **technical controls that assume compromise** ([[cybersecurity/07-security-operations/01-defensive-architecture|least privilege and zero-trust]] limit what a phished account can do), and **detection** ([[cybersecurity/07-security-operations/02-logging-siem-and-detection|monitoring]] for the anomalous login/behavior that follows a successful phish). The realistic goal isn't "no one ever gets fooled" — it's "getting fooled doesn't hand over the kingdom."

## Related
- [[cybersecurity/04-web-security/02-secure-authentication|Secure Authentication]] — MFA, the key mitigation for phished credentials
- [[cybersecurity/07-security-operations/README|Security Operations]] — detecting the post-phish activity
- [[cybersecurity/03-attacker-and-hacker-types|Attacker & Hacker Types]] — who runs these campaigns
