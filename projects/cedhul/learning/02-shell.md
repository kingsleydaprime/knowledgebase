# 02 — Shell commands used on CEDHUL

See also: [01-security-incident.md](01-security-incident.md) · [03-deploy.md](03-deploy.md)

## Auditing untrusted files without running them

```bash
head -c 600 file.php          # first 600 *bytes* — safe peek at a huge or minified file
unzip -l index.zip            # list an archive's contents without extracting
unzip -qo index.zip -d DIR    # -q quiet, -o overwrite, -d extract into DIR (a scratch dir, never the project)
```

`head -c` beats `head -n` for minified/obfuscated files, where one "line" can be megabytes.

## Finding injected code

```bash
grep -lniE 'eval\(|base64_decode|gzinflate|atob\(|fromCharCode' *.html *.php js/*
```
- `-l` print only filenames, `-n` line numbers, `-i` case-insensitive, `-E` extended regex (so `|` means OR).
- `\(` escapes the parenthesis, so `eval\(` matches the call rather than starting a regex group.

```bash
grep -hoE 'https?://[a-zA-Z0-9.-]+' *.html | sort | uniq -c | sort -rn
```
Extract every external domain and count it. `-o` prints only the match, and `-h` drops the
filename. `sort | uniq -c | sort -rn` is the classic "frequency table" pipeline. You *must* sort
before `uniq`, because `uniq` only collapses *adjacent* duplicates.

## Diffing against a known-good backup

```bash
for f in backup/*.html; do b=$(basename "$f"); cmp -s "$f" "$b" && echo same $b || echo DIFF $b; done
diff -rq . cedsite            # -r recursive, -q only say *which* files differ
```
`cmp -s` is silent and just sets an exit code, so `&& ... || ...` branches on it.

## Finding files that don't belong in a folder

```bash
find assets -type f ! -name '*.js' ! -name '*.css' ! -name '*.png' ...
```
`!` negates the next test. It's a quick way to spot a `.php` hiding in an images folder.

```bash
find assets -size +20M -exec ls -lh {} \;
```
Find big files. This matters because GitHub rejects any single file over 100 MB.
