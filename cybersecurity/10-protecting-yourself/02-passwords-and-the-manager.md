# Passwords, and the Manager

**[Beginner]** — the single highest-value hour in this folder.

## The kid version first

The problem was never that your password is weak. **The problem is that you used it twice.**

Companies get breached constantly. When one you used gets breached, your email and password end up in a file that gets passed around. Software then tries that pair on hundreds of other sites, automatically, for free. **Every account where you reused it opens.** Nobody had to hack you — you were on a list.

The fix is one thing: **a different password everywhere.** Which is impossible to remember, which is why password managers exist.

## Why reuse is the whole problem

```
2019: a shop you forgot about gets breached
      your email + password end up in a public dump
        │
2026: software tries that pair against
      Gmail · your bank · Instagram · Amazon · your work login
        │
      every site where you reused it → opened
```

**This is called credential stuffing, and it's the most common account compromise there is.** It requires no skill, costs nothing, and runs continuously.

**Check your own exposure right now:** [haveibeenpwned.com](https://haveibeenpwned.com) — enter your email. It's run by a well-known security researcher, it's free, and it doesn't store what you type. **Most people find several breaches.** That's normal, and it tells you which passwords to change first.

## Use a password manager

It generates a unique random password per site, stores them encrypted behind one master password, and fills them in. You remember **one** password.

**Which one — any of these is fine:**

| | |
|---|---|
| **Bitwarden** | Free tier is genuinely complete, open-source, works everywhere. **The default recommendation** |
| **1Password** | Paid, best polish and family sharing |
| **Proton Pass** | Good if you already use Proton |
| **Built into your browser/OS** | Chrome, Apple Passwords, Firefox. **Much better than reuse.** Weaker across ecosystems, and tied to that browser |

**The built-in one is a real option.** The best password manager is the one you'll actually use, and "I'll set up Bitwarden eventually" protects nobody.

## The master password

This one you memorise, so make it a **passphrase** — four or five random, unrelated words:

```
correct-horse-battery-staple-mango
```

**Long beats complicated.** `Tr0ub4dor&3` is shorter, harder to remember, and easier to crack than the line above. Length is what makes a password expensive to guess.

**Rules for this one password:**
- Used **nowhere else**, ever
- Not derived from anything about you — no birthdays, names, or your dog
- **Write it down and keep it somewhere physically safe** if that's what it takes. A note in your home safe is a fine trade against forgetting it. Your realistic adversary is software on the internet, not a burglar reading your filing cabinet
- **Set up account recovery when you set up the manager**, not later. Bitwarden and 1Password have emergency-access and recovery-kit features. **Losing the master password can mean losing everything in it**

## "Isn't that all my eggs in one basket?"

The most common objection, and it deserves a straight answer.

**Yes. And it's still much better**, because:

- The alternative isn't many baskets — it's **one weak basket copied a hundred times.** Reuse is a shared basket with a bad lock
- The vault is encrypted on your device before it's uploaded, so the provider can't read it. **Even a full breach of the provider doesn't expose your passwords** unless your master password is weak. LastPass's 2022 breach is the case study: the vaults were stolen, and the accounts that suffered were those with weak master passwords and old settings
- **The basket is guarded by one strong password plus 2FA** → [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|03]]

## Getting there without a miserable weekend

**Don't try to change 200 passwords at once.** You'll stop after nine.

1. **Install it. Set a strong master password. Turn on 2FA for the manager itself.**
2. **Fix these five today:** your primary email, your bank, your phone-network account, your work login, and whichever service holds your card details. **Email first — it's the master key.**
3. **Let it fill in the rest as you go.** Each time you log into something over the next months, let the manager save it and change the password if it was reused.
4. **Run its breach/reuse report** — every good manager has one. It'll show you a depressing list. Work down it slowly.

**Also do:** turn on breach alerts, and **delete accounts you don't use.** An account you forgot about is an account you won't notice being breached.

## Security questions are passwords too

*"Mother's maiden name"*, *"first school"* — these are **often discoverable** on social media or public records, and they bypass your strong password entirely.

**Lie.** Put a random string in your password manager as the answer:

```
First school?  →  vault-orbit-clement-99
```

Nothing requires the answer to be true. This is one of the highest-value five-minute habits in the folder → [[cybersecurity/10-protecting-yourself/07-your-privacy-footprint|your privacy footprint]].

## Key insight

**Password strength is a much smaller problem than password reuse.** A "weak" unique password on a site that salts and hashes properly is safer than a strong one you used in four places — because the attack that actually reaches you isn't guessing, it's a list from someone else's breach being replayed against you.

## Related
- [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|two-factor and passkeys]] — the layer that survives a stolen password
- [[cybersecurity/10-protecting-yourself/08-when-it-goes-wrong|when it goes wrong]]
- [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]] — the builder's side: how sites *should* store these
- [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|password attacks]] — the professional treatment
