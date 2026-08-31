# Backups and Your Data

**[Beginner]** — the only defence against the failures you can't prevent.

## The kid version first

Some things you can't stop: a drive dies, a phone goes in a river, a laptop is stolen, ransomware encrypts everything you own.

**Backups are the answer to all four**, and they're the security measure people are most confident they have and most often don't — because an untested backup is a belief, not a backup.

## Why this is a security topic, not just a safety one

**Ransomware makes backups the primary defence.** Malware encrypts your files and demands payment. Paying funds the industry, is often unnecessary, and frequently doesn't work — victims routinely pay and get nothing usable.

**A tested, offline backup makes ransomware an inconvenience instead of a catastrophe.** Wipe, restore, move on.

Modern ransomware also **steals data before encrypting** and threatens to publish it, which backups don't solve — but that's an argument for encryption and prevention, not against backups.

## 3-2-1

The rule that's survived decades:

```
3 copies of anything you care about
2 different kinds of storage
1 copy off-site
```

Concretely: the file on your laptop, a copy on an external drive at home, and a copy in cloud storage. **The off-site copy is what survives fire, flood and theft** — a backup drive next to the laptop is one burglary away from useless.

## Sync is not backup

**The most common and expensive misunderstanding here.**

Dropbox, iCloud, Google Drive and OneDrive **synchronise** — they make everywhere match. So:

```
you delete a file          → it deletes everywhere
ransomware encrypts a file → the encrypted version syncs everywhere
you corrupt a file         → the corruption syncs everywhere
```

**Sync propagates mistakes at the speed of your internet connection.**

They do offer version history and a recycle bin — 30 days is typical, and it has saved many people. **Know your provider's window**, and know it's a partial mitigation, not a backup.

**A real backup is versioned** — it keeps yesterday's file even after today's changed — **and it isn't continuously writable by your everyday machine.**

## What to actually use

| | Good for |
|---|---|
| **Time Machine** (macOS) / **File History** (Windows) | Automatic, versioned, local. **Turn one on today** — it's free and already installed |
| **Backblaze / iDrive** | Unlimited-ish cloud backup, versioned, off-site. Set and forget |
| **An external drive, unplugged between backups** | **The offline copy ransomware can't reach.** Cheap and effective |
| **Restic / Borg / Duplicati** | Free, encrypted, scriptable, to any storage. If you're technical, this |
| **Photos** | The thing people grieve. Ensure they're in **two** places, not just your phone |

**Encrypt any backup you keep off-site or in the cloud.** Most tools do this; turn it on and store the key in your password manager.

## The test nobody does

> **An untested backup is not a backup. It's a hope.**

Backups fail silently, constantly — a job stopped months ago, a drive died, a folder was never included, the encryption key is lost.

**Twice a year, do this. It takes ten minutes:**

1. Pick a file you'd hate to lose
2. **Restore it from your backup** to a different location
3. Open it and check it's intact and current

**Once a year, try something bigger** — restore a whole folder, or check you *could* rebuild a machine. Discovering your backup is broken should happen on a Tuesday afternoon, not the day the laptop dies.

## What to back up

**Irreplaceable:** photos and video · documents · code not pushed anywhere · anything creative · records, contracts, tax files · your password manager's recovery kit and 2FA backup codes → [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|03]].

**Not worth it:** applications, the OS, films you can re-download. **Backing up less makes it more likely you'll do it.**

**Don't forget your phone** — usually the device with the most irreplaceable content and the highest chance of being dropped, stolen or soaked. Both platforms back up automatically; **check yours is actually running**, because a full iCloud or Google account silently stops.

## Getting your data out

- **Google Takeout**, **Apple's Data and Privacy**, **Facebook's Download Your Information** — export what a platform holds
- Do this **before** you need it. **Account lockouts and bans happen with no appeal**, and people lose two decades of photos that way

## Key insight

**Every other measure in this folder reduces the chance of something bad; backups reduce the cost when it happens anyway** — which makes them the only one that works against threats nobody has thought of yet. The two failure modes are equally common: not having one, and having one that has silently not run since last year. **The ten-minute restore test is what separates them.**

## Related
- [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks|devices]] — encryption and updates
- [[cybersecurity/10-protecting-yourself/08-when-it-goes-wrong|when it goes wrong]]
- [[cybersecurity/07-security-operations/04-incident-response|incident response]] — the organisational version
- [[devops/README|devops]] — the same 3-2-1 logic, applied to production
