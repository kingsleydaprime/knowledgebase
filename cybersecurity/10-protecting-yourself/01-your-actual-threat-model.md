# Your Actual Threat Model

**[Beginner]** — assumes nothing technical. Who is realistically after you, who isn't, and why that changes what's worth doing.

## The kid version first

Security advice usually arrives as an enormous list, all of it urgent, none of it ranked. So people either do nothing, or exhaust themselves on the wrong things.

**A threat model is just three questions:** *what do I have that's worth taking, who would plausibly take it, and what would it cost me?* Answer those and the enormous list shrinks to about six things.

## You are almost certainly not being targeted

This is the most freeing thing in this folder. **Nearly all harm that reaches ordinary people is opportunistic, not targeted.** Nobody chose you. A system chose everybody, and you were in the list.

**What that actually looks like:**

- **Credential stuffing.** A company you used got breached years ago. Your email and password are in a file with two hundred million others. Software tries that pair against every major site, automatically. **If you reused that password anywhere, that account is already open.**
- **Phishing at scale.** Ten million identical messages. It doesn't need to fool you specifically; it needs to fool 0.1% of ten million.
- **SIM swap.** Someone convinces your mobile network to move your number to their SIM, then resets every account that texts you a code.
- **Device theft.** A stolen laptop or phone. **The threat is usually the data, not the hardware.**
- **Investment and romance fraud.** Months of grooming, a fake platform showing fake gains. Often run from trafficked-labour compounds — organised crime, not a lone scammer.

**Notice what's not on that list:** sophisticated hackers breaking your encryption, government surveillance of you personally, someone cracking a strong password. Those are the ones people worry about, and they're the least likely.

## But "not targeted" isn't universal

Some people **are** targeted, and the advice changes. Be honest about whether you're one:

| If you are | The added risk |
|---|---|
| **A journalist or activist** | State-level actors, device seizure, targeted malware |
| **A business owner or finance staff** | **Business email compromise** — the invoice that isn't real |
| **Someone with visible crypto holdings** | Targeted phishing, and physical risk. **Don't publicise holdings** |
| **A public figure** | Impersonation, doxxing, coordinated harassment |
| **Leaving an abusive relationship** | **The most dangerous case in this folder** — the adversary knows your birthday, your pet's name, your recovery answers, and may have had physical access to your devices. Standard advice can actively backfire |

**That last row deserves saying plainly.** If someone who knows you intimately may have access to your accounts or devices, changing a password can alert them and escalate things. Domestic-violence support organisations have specialists for exactly this, and the right move is to talk to them **before** changing anything. Technical advice from a general guide is not adequate there.

## What's actually worth protecting

Rank yours. Most people's list looks like this:

1. **Your primary email.** **This is the master key** — password resets for everything else land there. Someone with your email has, given twenty minutes, everything else. Protect it more than your bank.
2. **Your phone number.** The second master key, because so many services use it for recovery. This is what makes SIM swap so effective.
3. **Money** — banking, payment apps, anything holding crypto.
4. **Identity documents** — enough to open accounts in your name.
5. **Private material** — photos, messages, health records. Low financial value, high personal cost.
6. **Work access** — where your mistake becomes your employer's incident.

**If you protect your email and your phone number well and do nothing else, you have done most of the available good.**

## The six things, ranked

The whole folder in one list, in the order of how much harm they prevent per hour spent:

| # | Do this | Why it's here | Note |
|---|---|---|---|
| 1 | **A password manager, and stop reusing** | Kills credential stuffing entirely | [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager\|02]] |
| 2 | **Real 2FA on email and banking** | Kills stolen-password attacks | [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys\|03]] |
| 3 | **Turn on automatic updates** | Kills most malware. **Costs one click** | [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks\|05]] |
| 4 | **Learn the phishing tells** | The most common way people actually lose money | [[cybersecurity/10-protecting-yourself/04-phishing-and-scams\|04]] |
| 5 | **A backup you have tested** | The only defence against ransomware and loss | [[cybersecurity/10-protecting-yourself/06-backups-and-your-data\|06]] |
| 6 | **Lock your phone, encrypt your laptop** | Turns theft into a hardware loss, not a data loss | [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks\|05]] |

**That's a weekend, once, and then almost nothing ongoing.**

## What isn't worth your time

Being honest about this matters, because bad advice crowds out good:

- **Changing passwords every 90 days.** Actively counterproductive — it produces `Summer2024!` → `Autumn2024!`. Even NIST now recommends against forced rotation. **Change a password when there's a reason to.**
- **A consumer VPN "for security".** Oversold. It moves who can see your traffic; it doesn't stop phishing, malware or breaches → [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks|05]].
- **Antivirus beyond what's built in.** Windows Defender is good now. Third-party suites are mostly upsell.
- **Covering your webcam.** Harmless, and far down the list.
- **Worrying about encryption being broken.** It won't be. **The attacker goes around it, through you** → [[cybersecurity/05-cryptography/README|cryptography]].

## Key insight

**Security is not a state you reach; it's a small number of habits that make you a worse target than the person next to you.** Almost all real-world harm is automated and opportunistic — so the goal isn't being unbreakable, it's being expensive enough that the automation moves on. Six things, one weekend, and you've done that.

## Related
- [[cybersecurity/10-protecting-yourself/README|the track]]
- [[cybersecurity/06-attacks-and-threats/README|attacks and threats]] — the same material, for people defending organisations
- [[cybersecurity/01-fundamentals/02-cia-triad|the CIA triad]] — the professional framing of "what's worth protecting"
