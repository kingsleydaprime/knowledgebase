---
id: fdabb3e5-7036-46b7-b807-43e915975248
---

# Your Devices and Networks

**Device security is mostly two settings — encryption, so a thief can't read your data, and automatic updates, so known holes get fixed.**

## Before you start
<!-- bite: 25646f38-2618-4419-ad87-1a65e4bdfd47 -->

You should have:

- Met device theft and malware in your threat model → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|your actual threat model]].
- Nothing technical; your phone and laptop to hand.

After this lesson you will be able to:

1. Explain why automatic updates and full-disk encryption do most of device security.
2. Turn both on, and lock your phone properly.
3. Set up home Wi-Fi safely, and judge public Wi-Fi honestly.
4. Give a straight answer on whether you need a VPN.

**Study route.** Kid version and §1–2, then the practice task: turn on updates and encryption and check them.

## What device security is
<!-- bite: dd15f4d6-f59b-46d8-b245-9c19c408fe67 -->

This covers things three and six on the list. It sounds like it should need special software, but it mostly comes down to two settings you already own. **Encryption** scrambles what's stored so a stolen laptop is a lost object, not a data breach. **Automatic updates** close the known holes that almost all real-world malware relies on.

Both are free, built in, and one-time. Almost everything *sold* as "security software" — extra antivirus, a consumer VPN "for safety" — is competing for your attention with these two steps that outperform it. This lesson turns the two settings on, sets up your Wi-Fi, and gives the honest version of the VPN question.

## The kid version
<!-- bite: 5935bc16-97a2-4845-9a60-4171f1c5290a -->

Imagine your diary. Two things keep it safe: writing it in a code only you can read, so a thief who grabs it sees gibberish, and fixing the broken lock on your drawer whenever the locksmith warns you about it. The code is encryption; fixing the lock is updates. You don't need a guard dog, an alarm company, or the gadgets in the shop window — those two habits do most of the job.

**Where the analogy stops working.** A diary's lock stays however you left it. Software "locks" are found broken all the time — researchers and attackers discover new holes constantly, and the fix only protects you once you install it. So "fix the lock when warned" isn't a one-off; it's *automatic* updates, running quietly forever, because almost all malware that reaches ordinary people walks through a hole that was patched months ago but never installed.

## 1. Updates — the highest-value click
<!-- bite: 403811cb-d421-4f4c-8d4b-48694fb958a5 -->

**Turn on automatic updates for your operating system, browser and phone. Today.** Almost all malware that reaches ordinary people exploits a hole **patched months or years ago** — attackers don't need new vulnerabilities, they need people who haven't installed the fix.

1. **Phone:** update immediately when offered — mobile updates are usually security-critical.
2. **Browser:** the most exposed software you run. Restart it when it asks; that's when the fix lands.
3. **Router:** the forgotten one. Check for firmware updates once a year, and replace it when the maker stops supporting it.
4. **Anything old and unsupported** — a phone past its update window, Windows past end-of-life — is permanently vulnerable. That's an upgrade decision, not a settings one.

## 2. Encryption and locking
<!-- bite: 5645e61d-6d81-4732-9e95-929ee25a9f77 -->

**Full-disk encryption means a stolen device is a hardware loss, not a data breach.**

1. **Windows** — BitLocker. **Check it's actually on** (Settings → Privacy & security → Device encryption); Home editions historically shipped without it.
2. **macOS** — FileVault (System Settings → Privacy & Security). On by default on modern Macs.
3. **iPhone** — on by default once you set a passcode. **Android** — on by default on modern devices.
4. **Save the recovery key somewhere that isn't the encrypted device** — your password manager, or printed with your documents.

**Locking:** a PIN of 6+ digits (biometrics for convenience, the PIN is the real secret); a short auto-lock; Find My on so you can wipe remotely; and **hide notification contents on the lock screen** — codes previewing on a locked phone undo your 2FA. One legal note: in several places courts treat compelling a fingerprint differently from a passcode, and your phone's power-button-hold forces passcode-only mode if that ever matters to you.

## 3. Software you install
<!-- bite: 018231bb-2207-446e-a53f-f1795a0383ff -->

**Most compromise arrives as something the user installed.**

1. **Install from official sources** — the OS app store or the vendor's real website.
2. **Be suspicious of search ads.** Attackers buy ads for common software names; the top result is sometimes a trojanised installer. Scroll to the real result.
3. **Say no to "download this to view the document"** — always.
4. **Browser extensions are full programs** with access to everything you browse. Install few, from known publishers, and review them yearly — extensions get sold and turn malicious.
5. **Antivirus:** the one built into your OS (Windows Defender) is genuinely good now. Third-party suites are mostly upsell, and some have *been* the security problem. Don't buy one.

For phone apps: stick to official stores and **review permissions** — a torch app wanting contacts and location is telling you what it's for.

## 4. Wi-Fi, and an honest answer on VPNs
<!-- bite: 59d5fc3e-6a9e-4c06-b204-6dc71bde2387 -->

**Home network:** change the router's admin password (the default is on the internet); use WPA3 or WPA2, never WEP or open; turn off WPS; and put visitors and cheap smart devices on a **guest network**, away from your laptops.

**Public Wi-Fi — the honest version.** "Never bank on public Wi-Fi" is largely out of date: nearly all traffic is HTTPS-encrypted now, so the café sees *which sites* you visit, not what you do on them. The real risks are a fake hotspot named like the real one, and — the important one — a **certificate warning**: if your browser says the connection isn't private, **stop**; that warning is the actual defence, and clicking through it is the mistake. Your phone's hotspot is better than public Wi-Fi anyway.

## 4. An honest answer on VPNs
<!-- bite: d249275a-3203-40fb-9260-ba11eb851ca3 -->

**VPNs** are the most oversold product in consumer security. What a VPN *does*: moves who can see your traffic's destination from your network to the VPN company — that's the whole function. It does **not** stop phishing, stop malware, protect you when a company you use is breached, or make you anonymous (you log into your accounts). It's genuinely useful for hiding browsing from your ISP, using an untrusted network, getting around geographic restrictions, and **circumventing censorship**. And you're *moving* trust, not removing it — a free VPN is often funded by selling exactly what the ISP could see. **For most people, a VPN is not one of the six things.**

## Terms used in this lesson
<!-- bite: 74603353-c83e-4e98-b39a-df7563b84a47 -->

1. **Full-disk encryption**: This scrambles everything stored on a device so that without the passcode it's unreadable — turning a stolen device into a hardware loss, not a data breach.
2. **Automatic updates**: This is the setting that installs software security fixes as they're released, closing the known holes almost all malware relies on.
3. **Recovery key**: This is the backup code that can unlock your encrypted disk — stored somewhere *other* than that disk.
4. **Patch**: This is a software fix for a known security hole; "unpatched" means the fix exists but you haven't installed it.

## Terms used in this lesson: networks
<!-- bite: 30f087b2-1c0d-4cd9-86a4-f08b2a289169 -->

5. **WPA3 / WPA2**: These are the secure Wi-Fi encryption standards; WEP and open networks are not secure.
6. **Guest network**: This is a separate Wi-Fi network for visitors and cheap smart devices, keeping them away from your main computers.
7. **HTTPS**: This is the encryption already protecting nearly all web traffic, which is why public Wi-Fi is far less risky than it used to be.
8. **VPN (virtual private network)**: This moves who can see your traffic's destination from your network to a VPN provider — useful for a few specific things, but not a general safety tool.

## Check your understanding
<!-- bite: d80608cb-d9ec-435f-8637-bcb88a46ee79 -->

Try each one before you open the answer.

1. <!-- q: mcq id="63b3be8e" -->
   Why is turning on automatic updates described as the highest-value click in device security?

   - [ ] Updates make your device faster.
   - [x] Almost all malware that reaches ordinary people exploits a hole that was already patched months or years ago — updates close it, so the attack has nothing to use.
   - [ ] Updates add new features.
   - [ ] Updates replace the need for a password.

   <details><summary>Answer</summary>

   Attackers overwhelmingly rely on *known*, already-fixed vulnerabilities, betting that people haven't installed the patch. Automatic updates remove that bet. It's one setting that neutralises most malware aimed at ordinary people — which is why it outranks any security product you could buy.

   </details>

2. <!-- q: mcq id="83851b04" -->
   Your laptop is stolen. What does full-disk encryption change about the consequences?

   - [ ] It lets you track the thief.
   - [x] Without your passcode the stored data is unreadable, so the theft is a hardware loss, not a data breach.
   - [ ] It prevents the laptop from being stolen.
   - [ ] It automatically deletes your files.

   <details><summary>Answer</summary>

   Encryption scrambles everything on the disk; without the passcode it's gibberish. So a thief gets a device to resell, not your documents, photos, saved logins and emails. That turns the worst part of device theft — the data — into a non-event. Just store the recovery key somewhere other than the encrypted device.

   </details>

3. <!-- q: mcq id="90c237ea" -->
   You're on café Wi-Fi and your browser warns "this connection is not private" with a certificate error. What should you do?

   - [ ] Click through — certificate warnings are usually glitches.
   - [x] Stop. That warning is the actual defence against someone intercepting the connection, and clicking through it is the mistake.
   - [ ] Switch to a different browser and try again.
   - [ ] Turn off Wi-Fi encryption.

   <details><summary>Answer</summary>

   Since nearly all traffic is HTTPS-encrypted, public Wi-Fi is far less risky than the old advice assumed — the café sees which sites, not what you do. The one thing that *does* matter is a certificate warning, which can indicate someone intercepting the connection. That warning is the protection working; heeding it (stopping) is the right move. Your phone's hotspot avoids the question entirely.

   </details>

4. <!-- q: gap id="96aa68d9" answers="guest" -->
   To keep cheap, often-insecure smart-home devices and visitors away from your laptops and phones, you should put them on a separate ___ network on your router.

   <details><summary>Answer</summary>

   A guest network. It isolates visitors and badly-secured smart gadgets from your main devices, so a compromise of a cheap smart plug can't reach your laptop. Combined with changing the router's default admin password and using WPA2/WPA3, it's most of home-network security.

   </details>

5. <!-- q: mcq id="eeedfa9c" -->
   Which of these does a consumer VPN actually do?

   - [ ] Stop phishing and malware.
   - [x] Move who can see your traffic's destination from your network/ISP to the VPN company — and nothing more than that.
   - [ ] Make you anonymous online.
   - [ ] Protect you when a company you use is breached.

   <details><summary>Answer</summary>

   A VPN only changes *who* can see where your traffic is going — it shifts that visibility from your ISP to the VPN provider (so you're moving trust, not removing it). It does not stop phishing or malware, doesn't help when a site you use is breached, and doesn't make you anonymous because you log into your accounts. It's useful for hiding browsing from your ISP, untrusted networks, geo-restrictions and censorship — but it's not a general safety tool and not one of the six things.

   </details>

6. <!-- q: open id="082331bf" -->
   A friend is about to pay for a well-advertised antivirus suite and a VPN subscription "to be secure". Using this lesson, explain what they'd get better value doing instead.

   <details><summary>Answer</summary>

   Both products are largely competing with free, built-in steps that do more. For malware: the antivirus built into their OS (Windows Defender) is genuinely good now, and third-party suites are mostly upsell — some have even been the security problem themselves. What actually stops most malware is turning on automatic updates (closing the already-patched holes malware relies on) and not installing dodgy software (official sources, wary of search ads, no "download to view this document"). For the VPN: it only moves who sees their traffic's destination from the ISP to the VPN company — it doesn't stop phishing, malware, or breaches, and doesn't make them anonymous; it's useful only for specific cases like untrusted networks or censorship. So the better-value move is free: turn on automatic updates and full-disk encryption, use a password manager and 2FA, and keep a tested backup — the six things. They'd be far more secure than the person who bought the suite and the VPN but skipped those.

   </details>

## Practice — turn on the two settings
<!-- bite: 371ade3b-a37a-4ee6-9ade-09bbc57cbdac -->

**Task.** Do the two that matter, and check them.

1. Turn on automatic updates for your OS, browser and phone — and update now if anything's pending.
2. Confirm full-disk encryption is actually on (BitLocker/FileVault/device encryption), and save the recovery key into your password manager.
3. Set your phone to a 6+ digit PIN, a short auto-lock, and hidden lock-screen notification contents.
4. On your router: change the admin password, confirm WPA2/WPA3, and set up a guest network.

## Practice: when it's done
<!-- bite: 4ab6b305-50e0-451b-839e-c97bba5f8d84 -->

Here's how you know the task is finished.

**Done when:** updates install automatically, your disk is confirmed encrypted with the recovery key stored safely elsewhere, your phone locks with a strong PIN and hides notification previews, and your router uses WPA2/WPA3 with a changed admin password. The test: if your laptop were stolen tonight, it'd be a hardware loss — and if a known exploit dropped tomorrow, your device would already have the fix.

## Before moving on
<!-- bite: e87be8a4-f47f-4296-9e1b-d3fe0904957a -->

You can now explain why updates and encryption do most of device security, turn both on, lock your phone, set up home Wi-Fi, and give a straight answer on VPNs.

**Recap for later lookup:** two settings do most of it — automatic updates (close known holes almost all malware uses) and full-disk encryption (theft becomes a hardware loss; save the recovery key elsewhere). Lock with a 6+ digit PIN, hide lock-screen previews. Install from official sources, beware search ads, built-in antivirus is enough. Home Wi-Fi: change admin password, WPA2/WPA3, guest network. Public Wi-Fi is mostly fine (HTTPS) except fake hotspots and certificate warnings — heed the warning. A VPN only moves who sees your traffic; it's not a general safety tool.

Next: [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|backups and your data]] — the one defence against the failures you can't prevent.

## Related
<!-- bite: c9de4c99-4548-4d8b-a50d-82dab8f2ca99 -->

- [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|Backups]] — what saves you when a device is lost or ransomed.
- [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|Phishing]] — how malware usually arrives.
- [[cybersecurity/03-network-security/index|Network security]] — the professional treatment.

## About this lesson
<!-- bite: 340e4cfb-2b96-4f45-ade0-12104f19aae4 -->

**Level:** Beginner (no code). **Covers:** why automatic updates and full-disk encryption do most of device security, phone locking, installing software safely, built-in antivirus, home Wi-Fi (admin password, WPA2/WPA3, guest network), the honest version of public Wi-Fi and certificate warnings, and a straight answer on VPNs, with a turn-on-the-settings task. **Where it sits:** lesson 5 of the [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]] section. **Sources:** the original vault note, rebuilt to the [[COURSE-STANDARD|course standard]] with quizzes and a personal task; written for the non-technical reader.
