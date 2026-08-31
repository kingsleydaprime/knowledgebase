# Your Devices and Networks

**[Beginner]** — the settings that matter, and an honest answer about VPNs.

## The kid version first

Two questions cover almost everything:

1. **If someone picks up this device, can they read what's on it?**
2. **If a piece of software has a known hole, has mine been fixed?**

Encryption answers the first. Updates answer the second. **Together they're most of device security**, and both are one-time settings.

## Updates — the highest-value click in this folder

**Turn on automatic updates for your operating system, browser and phone. Today.**

Almost all malware that reaches ordinary people exploits a hole that was **patched months or years ago**. Attackers don't need new vulnerabilities; they need people who haven't installed the fix.

- **Phone:** update immediately when offered — mobile updates are usually security-critical
- **Browser:** the most exposed software you run. Restart it when it asks; that's when the fix lands
- **Router:** the forgotten one. Check for firmware updates once a year, and **replace it when the manufacturer stops supporting it**
- **Anything old and unsupported** — a phone past its update window, Windows past end-of-life — is permanently vulnerable. **That's an upgrade decision, not a settings one**

## Encryption — so theft is only a hardware loss

**Full-disk encryption means a stolen device is a lost object, not a data breach.**

| | How |
|---|---|
| **Windows** | BitLocker. **Check it's actually on** — Settings → Privacy & security → Device encryption. Home editions historically shipped without it |
| **macOS** | FileVault. System Settings → Privacy & Security. On by default on modern Macs |
| **iPhone** | On by default when you set a passcode |
| **Android** | On by default on modern devices |
| **External drives** | BitLocker To Go, or VeraCrypt cross-platform |

**Save the recovery key somewhere that isn't the encrypted device.** Password manager, or printed with your documents.

## Locking

- **A PIN of 6+ digits**, not 4. Biometrics for convenience, but the PIN is the real secret
- **Short auto-lock** — a minute or two
- **Find My / Find My Device** on, so you can wipe remotely
- **Hide notification contents on the lock screen.** Codes and messages previewing on a locked phone undo your 2FA

**One legal note worth knowing:** in several jurisdictions, courts have treated compelling a fingerprint differently from compelling a passcode. **If that matters to you, know that your phone's power-button-hold or restart forces passcode-only mode.**

## Software you install

**Most compromise arrives as something the user installed.**

- **Install from official sources** — the OS app store, or the vendor's real website
- **Be suspicious of search ads.** Attackers buy ads for common software names, and the top result is sometimes a trojanised installer. **Scroll to the real result**
- **Say no to "download this to view the document"** — always
- **Browser extensions are full programs** with access to everything you browse. Install few, from known publishers, and **review them yearly** — extensions get sold and turn malicious after the fact
- **Uninstall what you don't use**

**Antivirus:** the one built into your OS is genuinely good now. Windows Defender is fine. Third-party suites are mostly upsell, and some have been the security problem themselves. **Don't buy one.**

**Phone apps:** stick to the official stores. **Review permissions** — a torch app wanting contacts and location is telling you what it's for. Both platforms let you grant location "only while using".

## Wi-Fi, and what's actually risky

**Your home network:**
- **Change the router's admin password.** The default is printed in the manual and on the internet
- **WPA3, or WPA2 if that's all it offers.** Never WEP or open
- **Turn off WPS** — the button-pairing feature has a known flaw
- **Guest network for visitors and smart devices.** Cheap smart-home gear is often badly secured and this keeps it away from your laptops → [[hardware/README|IoT]]

**Public Wi-Fi — the honest version.** The classic advice ("never bank on public Wi-Fi") is largely out of date. **Nearly all traffic is HTTPS-encrypted now**, so the café can see *which sites* you visit, not what you do on them. The realistic risks:

- **A fake hotspot** named like the real one
- **Certificate warnings.** If your browser warns you the connection isn't private, **stop.** That warning is the actual defence, and clicking through it is the mistake
- **Shoulder surfing**, which is more likely than anything technical

**Your phone's hotspot is better than public Wi-Fi**, and simpler than any of the above.

## VPNs — an honest answer

VPNs are the most oversold product in consumer security. **YouTube sponsorships have convinced people they're a general safety tool. They aren't.**

**What a VPN actually does:** moves *who can see your traffic's destination* from your network/ISP to the VPN company. That's the whole function.

**What it does NOT do:**
- ❌ Stop phishing
- ❌ Stop malware
- ❌ Protect you if a company you use is breached
- ❌ Make you anonymous — you log into your accounts, and they know you
- ❌ Meaningfully add encryption to HTTPS traffic, which is already encrypted

**When it's genuinely useful:**
- ✅ Hiding browsing from your ISP or network operator
- ✅ Using an untrusted network where you're worried about the operator
- ✅ Getting around geographic restrictions
- ✅ **Circumventing censorship** — a real and serious use, though a targeted user needs more careful tooling than a commercial VPN

**And note you're moving trust, not removing it.** The VPN provider can see everything the ISP could. Free VPNs are often funded by selling exactly that. **If you're going to use one, pay for a provider with an audited no-logs policy.**

**For most people, most of the time: a VPN is not one of the six things** → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|threat model]].

## Key insight

**Two settings — automatic updates and full-disk encryption — do more for your device security than every product you could buy.** Both are free, both are one-time, and both are already built into what you own. Almost everything sold as "security software" is competing for attention with steps that outperform it.

## Related
- [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|backups]] — what saves you when a device is lost or ransomed
- [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing]] — how malware usually arrives
- [[cybersecurity/03-network-security/README|network security]] — the professional treatment
- [[devops/01-linux/README|Linux]] — if you want the technical version of hardening
