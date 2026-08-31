# Your Privacy Footprint

**[Beginner]** — what's already public about you, why it's a security problem rather than just a privacy one, and what's worth doing.

## The kid version first

Privacy and security sound like different topics. They're connected by one mechanism: **the things people know about you are the raw material for convincing you they're legitimate.**

Your birthday, your first school, your mother's maiden name, your pet, your employer, your street — those aren't just personal details. **They're the answers to security questions, and the ingredients of a phone call that sounds like it's really from your bank.**

## Where your data already is

Be realistic — some of it is out and won't come back:

- **Breach dumps.** Companies you used got breached. Check yours: [haveibeenpwned.com](https://haveibeenpwned.com). **Most people find several.** Names, emails, phone numbers, sometimes addresses and passwords
- **Data brokers.** Companies that aggregate public records, purchases and app-location data into profiles they sell. **You never agreed to this in any meaningful sense**
- **Social media** — yours, and other people's photos and posts about you
- **Public records** — electoral roll, company filings, property records, court records
- **Your phone's apps.** Location and usage data sold onward through advertising networks

## The security consequence

```
attacker reads your Facebook
   → your dog's name, your school, your birthday
        → answers your bank's security questions
             → resets your account
```

Or the softer version: a call that opens with your full name, address and last four digits of your card. **Those details make people believe the rest**, and that belief is the actual attack → [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing]].

**So the practical fix isn't hiding your life. It's severing the link between public facts and account access.**

## The highest-value habits

**1. Lie on security questions.**
Random strings, stored in your password manager. Your mother's maiden name is discoverable; `vault-orbit-clement-99` is not. **Five minutes per account, and it removes an entire attack path** → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords]].

**2. Use email aliases.**
A different address per service, so a breach at one doesn't link to the others, and you can see who leaked or sold your address. Apple's Hide My Email, Firefox Relay, SimpleLogin, or a catch-all on your own domain. **Also lets you cut off spam at the source** by disabling one alias.

**3. Protect your phone number like a password.**
It's a recovery method for most accounts and the target of SIM swap. **Ask your network for a port-out PIN.** Consider a separate number (Google Voice, a second SIM) for shops and sign-ups.

**4. Audit what's public about you.**
Search your own name, email and phone number. Look at your social profiles while logged out. **You'll usually find something you forgot.**

**5. Lock down old accounts.**
The forum from 2011 has your details and no security team. **Delete accounts you don't use** — [JustDeleteMe](https://justdeleteme.xyz) is a directory of how.

**6. Review app permissions twice a year.**
Both phone platforms show which apps have location, contacts, microphone and camera. **Revoke generously** — you can always re-grant.

## What's worth it, and what isn't

**Worth doing:**
- **A privacy-respecting browser setup.** Firefox or Safari, plus **uBlock Origin**. Ad networks are a genuine malware vector ("malvertising"), so **this is a security measure, not just a privacy one**
- **A search engine that doesn't profile you** — DuckDuckGo, Brave
- **Encrypted messaging for private conversations** — Signal. WhatsApp is also end-to-end encrypted but shares metadata
- **Opting out of the big data brokers.** Tedious. In the EU/UK, GDPR gives you a legal right to erasure that generally works
- **Reviewing privacy settings** on the platforms you actually use

**Mostly not worth it:**
- **Deleting all social media** unless you want to. The cost is usually social, and the benefit is smaller than the six basics
- **Trying to be truly anonymous online.** Enormously hard, and not what your threat model needs → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|threat model]]
- **Paid "remove your data from the internet" services.** Do some of what you could do yourself, incompletely, forever, for a subscription
- **A VPN for privacy from advertisers.** Tracking is by cookies and fingerprinting, not IP → [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks|VPNs, honestly]]

## What not to post

Not paranoia — these specific things get used:

- **Your full date of birth** alongside your full name and place of birth
- **Boarding passes, tickets, documents** — the barcode contains your booking reference and surname
- **Your address**, or photos identifying it. Check for house numbers and street signs in the background
- **Real-time holiday posts.** Post afterwards
- **Photos of children with school uniforms visible**
- **Crypto holdings.** This attracts targeted phishing **and physical risk** → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]]
- **Anything you'd be answering as a security question**

**And an easy one people miss:** those social quizzes — *"your stripper name is your first pet and the street you grew up on"* — are collecting security-question answers, whether by design or by accident.

## Key insight

**Your privacy footprint is your attacker's research budget.** Every public fact makes the next phone call more convincing and the next security question easier to answer. You can't retract what's already out — but you can make it *useless* by ensuring no account access depends on facts a stranger could look up.

## Related
- [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing and scams]] — where this data gets used
- [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords]] — the security-question fix
- [[using-ai/07-privacy-and-what-not-to-share|privacy and AI]] — the same discipline, for chatbots
- [[cybersecurity/02-ethical-hacking/03-reconnaissance|reconnaissance]] — the professional side: how this is gathered deliberately
