---
id: 6d276bd7-8c6d-4e63-ba67-32bece9aa91b
---

# PDF and Document Password Security

**This is offline password cracking, learned on a file you locked yourself.** You take a password-protected document you own, pull the password check out of it as a hash, and throw guesses at that hash until one matches — entirely offline, with the file sitting still. It's the same pattern behind cracking a Wi-Fi handshake or a leaked database, in its simplest, most hands-on form.

## Before you start
<!-- bite: b181e318-3b40-4053-94c3-12035a59f63a -->

You should have:

- John the Ripper and/or hashcat installed → [[cybersecurity/02-ethical-hacking/08-common-tools|common tools]].
- A PDF you can lock yourself (any PDF tool, or `qpdf`).

After this lesson you will be able to:

1. Explain the two kinds of PDF password and which one is real encryption.
2. Extract a crackable hash from a document you own and attack it offline.
3. Use a mask attack when you remember part of your own password.
4. Say why the same pattern works on ZIP, Office and disk-encryption files.

**Study route.** Kid version and §1–5, then the worked example — **lock a PDF, then crack it** — then the practice task. Everything here is a file you created.

## The kid version
<!-- bite: 37c9c19a-dbb8-4217-83f4-3bbe93e23c25 -->

Imagine a padlock whose key is a word. You can't see the word, but you *can* take the padlock to a bench and try words on it as fast as your hands move — "password", "letmein", "january2020" — one after another, thousands a second, until one clicks. You never had to be near the door the lock came from; you just needed the lock on your bench.

Cracking a document password is exactly that. You don't attack the file over and over — you extract the "lock" (a small hash that says yes/no to a guess) onto your bench, and a cracking tool tries millions of words against it offline. If the real password is a common word, it clicks in seconds. If it's long and random, your hands never find it.

**Where the analogy stops working.** A real padlock takes the same time per try whether the key is "cat" or a 20-character jumble. A password lock doesn't care about length *per try* either — but the number of possible long-random passwords is so astronomically large that trying them all would outlast the sun. So the lock isn't what's weak; the *human-chosen word* is. That's the whole lesson.

## 1. Two passwords, only one of them real
<!-- bite: 9798d857-d8fa-4eab-a149-6e30eaba492d -->

A PDF can carry two different passwords, and they are **not** equally serious:

1. **User password** (the "open" password) — required to open the document. The content is genuinely **encrypted** with a key derived from this password. No password, no readable content. This is real cryptographic protection.
2. **Owner password** (the "permissions" password) — restricts actions like printing, editing or copying, *without* necessarily stopping the document from opening. It's enforced only by the reader **choosing to honour** restriction flags. A reader (or a tool) that ignores the flags removes the restriction instantly, with nothing to crack.

So the first question about any locked PDF is *which lock is this?* An owner-password restriction is a flag you strip; a user password is encryption you must actually attack. They're completely different problems, and confusing them wastes hours.

## Terms used in this lesson
<!-- bite: b17c8f28-d558-4570-a649-afeaf627bd12 -->

1. **Hash**: This is a scrambled, one-way value derived from the password. The file stores enough of it to check a guess, but you can't reverse it back to the password.
2. **Offline attack**: This is trying guesses against an extracted hash on your own machine, with no contact with the original file or any server per guess — so there's no rate limit and no lockout.
3. **Dictionary attack**: This is trying every word in a wordlist (like `rockyou.txt`) as the password.
4. **Mask attack**: This is trying passwords that match a known *pattern* — e.g. a word then four digits — shrinking the search enormously when you know part of it.
5. **Wordlist**: This is the file of candidate passwords a dictionary attack reads. `rockyou.txt` is the famous leaked one.
6. **Hash mode**: This is the number telling hashcat which hashing scheme it's attacking (PDFs, Wi-Fi and MD5 each have their own).
7. **RC4 / AES-256**: These are encryption algorithms. Old PDFs used weak 40-/128-bit RC4; modern ones use strong AES-256.
8. **Entropy**: This is how unpredictable a password is. High entropy (long, random) is what makes an offline attack hopeless.

## 2. Encryption strength depends on the PDF's age
<!-- bite: 4ef84a70-654a-442d-9ec0-c7c0f9a33ca2 -->

How hard the user password is to crack depends on the encryption the PDF uses:

- **Old PDFs** used **40-bit or 128-bit RC4** — weak enough that modern hardware brute-forces them quickly, sometimes regardless of password.
- **Modern PDFs** (PDF 2.0, or Acrobat's AES-256 setting) use **AES-256**, which is not brute-forceable by attacking the algorithm at all. The *only* way in is guessing the password itself.

So against a modern PDF, the algorithm is a brick wall and the password is the whole game. A weak password behind AES-256 still falls to a dictionary attack; a strong one behind AES-256 is effectively uncrackable. This is exactly why the defensive advice (§5) is "AES-256 **and** a strong passphrase" — you need both.

## 3. The general methodology
<!-- bite: 8fe0cf68-87ab-42c3-9d9c-f8c61fc013d0 -->

Every offline document crack is two steps:

1. **Extract a crackable hash from the file.** A helper reads the file's encryption metadata and writes out a hash representing the password check — no need to know the password yet. For PDFs that's `pdf2john`:
   ```bash
   pdf2john locked.pdf > hash.txt
   ```
2. **Attack that hash offline** with a dictionary or mask attack, using John or (far faster on a GPU) hashcat:
   ```bash
   john --wordlist=rockyou.txt hash.txt
   # or, GPU-accelerated:
   hashcat -m 10500 hash.txt rockyou.txt      # -m 10500: a PDF hash mode
   ```

`pdfcrack` is a purpose-built alternative that works straight against older-encryption PDFs with no separate extraction step. The pattern — extract, then attack offline — is the thing to remember; the exact tool varies.

## 4. Mask attacks — when you remember part of it
<!-- bite: 3fcf8683-f27c-42e7-a79c-f2cdf54124c9 -->

The most common *real* reason to do this is recovering your **own** forgotten password — and you usually remember *something* about it. A **mask attack** uses that. If you know it was a word you like followed by a year, you don't try the whole dictionary blindly; you fix the known part and only vary the unknown:

```bash
hashcat -m 10500 -a 3 hash.txt "Password?d?d?d?d"    # "Password" + 4 unknown digits
```

Each `?d` is one unknown digit. Four of them is only 10,000 possibilities — done in a blink — versus a blind search that might never finish. Knowing a little about the password is often the entire difference between cracking it and not. That's why, on a real engagement, OSINT about a target (a pet's name, a birth year) feeds straight into mask attacks.

## 5. Defending your own documents
<!-- bite: 792acb3d-f232-48e5-8db3-f991f3beadd7 -->

Everything above tells you how to defend, because you now know what the attack needs:

1. **Use AES-256**, not a tool's legacy default that might still be RC4. Check the "protect"/"encrypt" settings.
2. **Use a long, random passphrase.** The attack only beats guessable passwords; high entropy defeats it. Same lesson as [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi passphrase strength]] — identical underlying attack.
3. **Don't rely on the password alone** for truly sensitive files. A copied file carries its crackability wherever it goes, so access control on *where it's stored* matters as much.
4. **Use a password manager** — which, conveniently, also means you never need this technique on your own files in the first place.

## Worked example — lock a PDF, then crack it
<!-- bite: 75eaec4c-0d79-4807-8077-f2acce037b36 -->

The whole pattern, on a file you make right now. This is tier-3 of your owned-target lab — a file that's unambiguously yours.

```bash
# 1. Make a PDF and lock it with a deliberately weak password you choose.
#    (qpdf; or use any PDF app's "protect with password".)
qpdf --encrypt hunter2 hunter2 256 -- original.pdf locked.pdf
#    user-pw  owner-pw  AES-256      input        output

# 2. Confirm it's locked: opening it should demand a password.

# 3. Extract the hash.
pdf2john locked.pdf > hash.txt

# 4. Crack it with a wordlist that contains your password (rockyou has 'hunter2').
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
john --show hash.txt        # prints: locked.pdf:hunter2
```

**What this proves.** You chose AES-256 — the strong algorithm — and it *still* fell, in seconds, because the password (`hunter2`) is in `rockyou.txt`. That's the lesson made physical: strong encryption plus a weak password equals no protection. Now redo step 1 with a long random passphrase (`qpdf --encrypt "$(openssl rand -base64 18)" ... `) that you *don't* put in any wordlist, and watch the same crack run forever. Same algorithm, opposite outcome — the password was the whole thing.

**Predict first:** before step 4, guess roughly how long the weak-password crack takes. Then time it. (Seconds, because `hunter2` is early in `rockyou.txt`.)

## 6. The pattern transfers to almost any locked file
<!-- bite: 3695c55e-11b8-45b9-8059-fb627a50954e -->

Once "extract a hash, attack it offline" clicks for PDFs, it transfers directly to other formats — only the extraction helper changes:

- **ZIP archives** → `zip2john archive.zip > hash.txt`
- **Office documents** → `office2john report.docx > hash.txt`
- **Disk-encryption containers** and many more, each with its own `*2john` helper.

Then the *same* `john`/`hashcat` dictionary or mask attack runs against the hash. The cracking approach never changes; learn it once here and you have it for everything. This is why §3 stressed the *pattern* over the tool.

## Common pitfalls and traps
<!-- bite: ebee3ed6-5021-463b-8f51-992fec6dac22 -->

1. **Confusing the owner password with the user password.** The owner (permissions) one is a flag you strip in seconds, not encryption to crack. Check which you're facing first.
2. **Expecting AES-256 with a strong password to crack.** It won't, ever. If it's modern encryption and a long random password, stop — the answer is "not practically crackable," and that's a finding in itself (good protection).
3. **Blind dictionary attack when you know the pattern.** A mask attack using what you remember is often thousands of times faster.
4. **Wrong hash mode.** hashcat needs the right `-m` for the PDF version; the wrong mode fails silently or errors. `pdf2john`'s output or hashcat's examples tell you which.
5. **Doing this to a file that isn't yours.** Cracking someone else's protected file is unauthorized access to protected data — not a grey area. Everything here is a file you created.

## Check your understanding
<!-- bite: 1c0efe08-d26e-4c1e-8d10-29da9e13fdb6 -->

Try each one before you open the answer.

1. <!-- q: mcq id="cd530b9b" -->
   A PDF won't let you print or copy text, but opens instantly with no password prompt. What kind of protection is this, and how hard is it to remove?

   - [ ] A user password — you must crack the encryption.
   - [x] An owner (permissions) password — a flag a reader chooses to honour, removable instantly with a tool, nothing to crack.
   - [ ] AES-256 encryption — not removable at all.
   - [ ] A mask-protected password — removable only with the right pattern.

   <details><summary>Answer</summary>

   It opens with no prompt, so the content isn't encrypted — the restriction is an owner/permissions flag enforced only by cooperating readers. A tool that ignores the flag strips it immediately. A user password, by contrast, encrypts the content and must actually be attacked.

   </details>

2. <!-- q: gap id="7a82896d" answers="offline" -->
   Because you attack an extracted hash on your own machine with no contact with the original file per guess, there's no rate limit and no lockout. This kind of attack is called an ___ attack.

   <details><summary>Answer</summary>

   Offline. Extracting the hash removes the per-guess interaction with the file, so you can try millions of candidates as fast as your hardware allows — which is exactly why passphrase strength (entropy), not the algorithm, is what protects you.

   </details>

3. <!-- q: mcq id="d54c6d44" -->
   You lock a PDF with AES-256 and the password `hunter2`, then crack it in seconds. What does this demonstrate?

   - [ ] AES-256 is a weak algorithm.
   - [ ] qpdf doesn't really encrypt.
   - [x] Strong encryption with a weak, guessable password gives no real protection — the human-chosen password is the weak point.
   - [ ] Cracking only works on files you own.

   <details><summary>Answer</summary>

   AES-256 is strong — the algorithm wasn't broken. The password `hunter2` is in `rockyou.txt`, so a dictionary attack finds it immediately. Strong encryption plus a weak password equals no protection; you need both a strong algorithm and a high-entropy password.

   </details>

4. <!-- q: mcq id="84b7caf7" -->
   You forgot your own PDF's password but remember it was `Lagos` followed by four digits (a year). Which approach cracks it fastest?

   - [ ] A full dictionary attack with rockyou.txt.
   - [x] A mask attack: fix `Lagos` and vary four unknown digits (`Lagos?d?d?d?d`).
   - [ ] Brute-forcing every possible 9-character string.
   - [ ] Stripping the owner password.

   <details><summary>Answer</summary>

   A mask attack uses what you remember: `Lagos?d?d?d?d` is only 10,000 possibilities (the four digits), cracked instantly. A full dictionary might not contain `Lagos2019`, and brute-forcing all 9-character strings is astronomically slower. Knowing part of the password collapses the search space.

   </details>

5. <!-- q: open id="9ae417d7" -->
   Explain why `zip2john`, `office2john` and `pdf2john` all exist as separate tools, yet you only ever learn *one* cracking step. What does that tell you to focus on?

   <details><summary>Answer</summary>

   Each file format stores its password check differently, so each needs its own extractor to pull out a crackable hash — hence a separate `*2john` helper per format. But once the hash is extracted, it's just a hash, and the *same* dictionary/mask attack with John or hashcat runs against all of them. So the transferable skill is the offline-cracking step (and choosing good wordlists/masks), not any one extractor. Learn the pattern — extract, then attack offline — and every new format is just a different extraction command.

   </details>

## Practice — lock and crack your own files
<!-- bite: 8eed9f4c-8331-4461-b924-897d60ad428e -->

**Task.** Prove the pattern on files you own, and prove the defence.

1. **Weak:** lock a PDF with AES-256 and a password from `rockyou.txt`. Extract the hash, crack it, and time how long it took.
2. **Strong:** lock the same PDF with a long random passphrase you don't put in any wordlist. Run the same attack and confirm it doesn't finish.
3. **Transfer:** lock a ZIP or a `.docx` with a weak password, extract its hash with the right `*2john`, and crack it — proving the pattern moves across formats.

**Done when:** you've cracked a weak-password file, failed to crack a strong-password one (on purpose), and repeated the crack on a second file format. Write one line on why step 2 failed. Log it in `cybersecurity/LIVE-RUNS-TODO.md`.

**Stretch.** Create a file whose password matches a pattern you define (a word + 2 digits), then crack it with a **mask** attack and compare the time to a full dictionary run.

## Before moving on
<!-- bite: 8eed9f4c-8331-4461-b924-897d60ad4290 -->

You can now attack a locked document you own: tell the two password types apart, extract a hash, crack it offline with a dictionary or a mask, and you've proven on your own files that the password — not the algorithm — is what protects a modern document. You know the pattern transfers to ZIP, Office and more.

**Recap for later lookup:** user password = encryption (attack it); owner password = flag (strip it). Extract a hash (`pdf2john`/`zip2john`/`office2john`), attack offline (`john`/`hashcat`). Dictionary for unknown, mask when you remember a pattern. Defence: AES-256 **and** a long random passphrase.

Next: [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi security testing]] — the same offline-cracking pattern, against your own wireless network.

## Related
<!-- bite: 8eed9f4c-8331-4461-b924-897d60ad4291 -->

- [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi security testing]] — offline cracking of a captured handshake, same pattern.
- [[cybersecurity/02-ethical-hacking/08-common-tools|Common tools]] — John, hashcat and wordlists.
- [[cybersecurity/05-cryptography/03-hashing-and-integrity|Hashing and integrity]] — why hashes are one-way, and what makes one slow to crack.

## About this lesson
<!-- bite: d978d8c9-43e8-41e2-8c5b-55074f51a2ed -->

**Level:** Intermediate. **Covers:** user versus owner PDF passwords, encryption strength by PDF version, extracting a hash and attacking it offline with dictionary and mask attacks, the pattern transferring to ZIP/Office/disk files, and defending your own documents. **Where it sits:** lesson 10 of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section — an owned-file offline-cracking lab (tier 3 of the lab). **Sources:** the original vault note, made hands-on with a lock-then-crack worked example on a file you create. `[reference]` — not drawn from a personal paid engagement. Commands are tracked in `cybersecurity/LIVE-RUNS-TODO.md` for a verified run.
