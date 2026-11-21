---
id: 6d276bd7-8c6d-4e63-ba67-32bece9aa91b
---

# PDF & Document Password Security

The most common legitimate reason to actually run this kind of attack is mundane: recovering access to a password-protected file *you own* after forgetting the password — a genuinely frequent, unglamorous real-world scenario, and a good concrete way to learn how password-based encryption is attacked in general, on files that are unambiguously yours.

## How PDF password protection actually works
<!-- bite: 38cc63ff-de2a-407c-9a79-82baa2925e6e -->

A password-protected PDF can have two independent passwords:

- **User password (open password)** — required to open the document at all; the document's content is genuinely encrypted with a key derived from this password.
- **Owner password (permissions password)** — restricts actions (printing, editing, copying text) without necessarily preventing the document from being opened — enforced by the PDF reader honoring restriction flags, which is a much weaker guarantee than actual encryption, since a reader that ignores those flags (or a tool that strips them) bypasses it entirely without needing to crack anything.

Only the user password represents genuine cryptographic protection — this distinction (encryption vs. a permissions flag) is the first thing worth understanding, since attacking one vs. the other are completely different problems.

## Encryption strength varies a lot by PDF version
<!-- bite: e3027e3c-7dc6-4632-913c-5598a68de0f3 -->

Older PDFs used weak 40-bit or 128-bit RC4 encryption, both of which are fast to brute-force with modern hardware. Modern PDFs (PDF 2.0, or Acrobat's AES-256 setting) use strong, standard AES-256 encryption — brute-forcing this is only remotely feasible if the password itself is weak or falls within a crackable dictionary/pattern space; the algorithm itself isn't the weak point at that encryption level, the *human-chosen password* is.

## The general methodology
<!-- bite: 918334df-557a-495a-a828-dd83403dd44c -->

1. **Extract a crackable hash from the file** — a tool reads the PDF's encryption metadata and produces a hash representing the password check, without needing to already know the password (`pdf2john.py file.pdf > hash.txt`, part of the John the Ripper toolkit).
2. **Run a dictionary or mask attack against that hash, offline** — the same fundamental approach as [[11-wifi-security-testing|cracking a captured Wi-Fi handshake]]: try candidate passwords against the hash until one matches, entirely offline, with no interaction with the original file needed per guess.

```text
# illustrative shape of the workflow:
python2 pdf2john.py locked.pdf > hash.txt
john --wordlist=rockyou.txt hash.txt
# or, far faster on a GPU:
hashcat -m 10500 hash.txt rockyou.txt      # mode for PDF 1.7 Level 3 (AES-128)
```

`pdfcrack` is a purpose-built alternative that works directly against the PDF file for older encryption schemes without a separate hash-extraction step.

## The same pattern applies to almost any password-protected file format
<!-- bite: 8f7102e0-cdbc-472d-a0c4-a0866e2bb864 -->

Password-protected ZIP archives (`zip2john`), Office documents (`office2john`), and full-disk encryption containers all follow the identical shape: extract a crackable representation of the password check, then dictionary/mask-attack it offline. Once this pattern clicks for PDFs, it transfers directly — the specific extraction tool changes per format, the cracking approach doesn't.

## Mask attacks — when you know something about the password
<!-- bite: 74ef3a19-caff-4c20-9dad-c0515edc92fb -->

If you have partial memory of your own forgotten password (a phone number, a specific word, a date format you tend to use), a **mask attack** specifies which parts are fixed and which are unknown character ranges, dramatically shrinking the search space versus a blind dictionary attack — often the difference between a crack finishing in seconds versus not finishing in a practical timeframe at all.

```text
# example mask: "Password" followed by 4 unknown digits (a year, say)
hashcat -m 10500 -a 3 hash.txt "Password?d?d?d?d"
```

## Defensive takeaways for your own documents
<!-- bite: 1ba8ae7c-6df4-44b4-8d2d-a5c6b157144f -->

- Use AES-256 encryption specifically (available in Acrobat's "Protect" settings) rather than relying on default/legacy settings that may still offer weaker RC4.
- A long, random passphrase beats a memorable-but-guessable one — the same lesson as [[11-wifi-security-testing|Wi-Fi passphrase strength]], since the underlying attack (offline dictionary/mask cracking) is structurally identical.
- For genuinely sensitive documents, password protection alone shouldn't be the only control — proper access control on wherever the file is stored matters just as much, since a copied file carries its password protection (and its crackability) with it wherever it goes.
- Use a password manager to avoid the "forgot my own password" scenario in the first place — the actual motivation for most people who ever need this technique on their own files.

## Gotchas
<!-- bite: ed1b53d5-17d8-4e7d-9485-d630da146554 -->

- Cracking speed depends heavily on encryption strength and hardware — a weak, older RC4-encrypted PDF can crack in minutes; a modern AES-256 PDF with a genuinely strong password is not practically crackable at all, regardless of how long you run it.
- This technique only applies to files you're authorized to access — running it against someone else's password-protected file is unauthorized access to protected data, not a gray area, exactly as covered in [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]].

## Related
<!-- bite: 0f96a859-ea43-4aac-ad0d-7d29f26a9299 -->
- [[11-wifi-security-testing|wifi-security-testing]]
- [[08-common-tools|common-tools]]
- [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]
