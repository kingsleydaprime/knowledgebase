# 01 — Shell

Command-line technique that came up while replatforming usghcc.org.

See also: [02-content-modelling.md](02-content-modelling.md) ·
[03-frontend.md](03-frontend.md) · [index.md](index.md)

---

## 1. Heredocs: `<< 'EOF'` vs `<< EOF`

A **heredoc** feeds a block of text to a command's standard input:

```bash
cat > file.txt << 'EOF'
hello
EOF
```

`cat > file.txt` means "write what you read on stdin into file.txt". The
heredoc supplies that stdin. Everything between the opening line and the
closing delimiter becomes the file.

**The quoting is the part that matters.** Compare:

```bash
cat << EOF        # UNQUOTED delimiter
Cost: $100 and `date`
EOF
# → Cost:  and Wed 24 Sep ...   ($100 expanded to nothing, `date` ran)

cat << 'EOF'      # QUOTED delimiter
Cost: $100 and `date`
EOF
# → Cost: $100 and `date`       (literal, exactly as typed)
```

With an unquoted delimiter the shell expands `$variables`, `` `backticks` ``
and history `!` **inside the body** before the command ever sees it. Quoting
the delimiter turns all of that off.

**Practical rule: when writing code or markdown, always quote the delimiter.**
TypeScript is full of `${...}` template literals and Tailwind classes contain
`$`; an unquoted heredoc silently eats them and you get a file that looks right
in your editor buffer but is wrong on disk.

### The trap I actually hit writing this file

Writing this very document with `cat > 01-shell.md << 'EOF'` **failed**, because
the document itself contains a line that is exactly `EOF` at column 0 — the
example above. The shell saw it and closed the heredoc early, leaving the rest
of the file as broken shell commands:

```
(eval):250: parse error
```

**The fix: pick a delimiter that cannot appear in the body.** This file was
written with `<< 'MDDOC'`. Any document *about* heredocs, or containing shell
examples, needs an unusual delimiter for exactly this reason.

The closing delimiter must also be at column 0 — no leading spaces — unless you
use `<<-`, which strips leading **tabs** only (not spaces, which is why `<<-`
is usually more trouble than it is worth).

---

## 2. `python3 -` — when `sed` stops being the right tool

```bash
python3 - << 'PY'
import pathlib
p = pathlib.Path("src/lib/schemas.ts")
s = p.read_text()

old = "export const homePageSchema"
assert old in s, "anchor not found"
s = s.replace(old, "// ...", 1)
p.write_text(s)
PY
```

The `-` means **"read the program from stdin"** rather than from a file. So the
heredoc becomes the script. Nothing is written to disk, nothing needs cleaning
up.

**Why reach for this over `sed`:** `sed` is line-oriented and its regex dialect
is awkward. The moment an edit needs to span multiple lines, or be conditional,
or happen exactly once, `sed` becomes a puzzle. Python is just code.

### The habit that makes it safe: assert before writing

```python
assert old in s, "anchor not found"
s = s.replace(old, new, 1)
```

Two separate ideas, both important:

- **`assert old in s`** — if the text you meant to replace is not there, the
  script *fails loudly*. Without it, `.replace()` on a non-match returns the
  string unchanged and `write_text` happily writes the original back. You get a
  silent no-op and believe the edit worked. This is the most common way
  scripted edits go wrong.
- **the `1` in `.replace(old, new, 1)`** — replace the **first occurrence
  only**. Without it, every occurrence changes.

### Verifying after, not just asserting before

```python
assert s.count("export const homePageSchema") == 1
```

Assert the *end state*, not only the precondition. "There is now exactly one of
these" catches a duplicate that "the anchor existed" would not. On this project
a duplicated `homePageSchema` plus byte-identical duplicated import lines
appeared in two files — exactly the shape an insertion applied twice leaves
behind, and exactly what an end-state assertion would have caught immediately.

---

## 3. Reading a big XML export without a parser

The WordPress export (WXR) was a single 300-item XML file. You rarely need a
real XML parser to answer "what is in here".

**Count occurrences of a marker:**

```bash
grep -c '<wp:post_type><!\[CDATA\[attachment\]\]></wp:post_type>' migration/*.xml
# → 217
```

`grep -c` counts *matching lines*, not matches. If two markers sit on one line
you get 1. Fine for one-per-line XML, wrong for minified files — know which you
have.

Note `\[` — in a bracket-heavy CDATA marker, `[` is a regex metacharacter and
must be escaped.

**Extract every URL of a given shape, deduplicated:**

```bash
grep -oE 'https://[^<"]*\.(jpg|jpeg|png|webp)' migration/*.xml | sort -u | wc -l
# → 131
```

- `-o` prints **only the matched part**, not the whole line. This is what turns
  grep from a search tool into an extraction tool.
- `-E` selects extended regex, so `(a|b)` and `+` work without backslashes.
- `[^<"]*` — "any run of characters that is not `<` or `"`". Defining a match
  by what *ends* it is usually more robust than describing what it contains.
- `sort -u` — sort and drop duplicates. `uniq` alone will not do this: `uniq`
  only collapses *adjacent* duplicates, so it is nearly always wrong without a
  preceding `sort`.

**Collapsing WordPress's resized variants.** WordPress stores
`image-1024x683.jpg`, `image-300x200.jpg` and `image.jpg` as separate URLs. To
get back to originals:

```python
re.sub(r'-\d+x\d+(?=\.[a-z]+$)', '', url)
```

`(?=...)` is a **lookahead** — it asserts the extension follows without
consuming it, so the extension survives the substitution.

---

## 4. Diagnosing a download that "works" but returns nothing

Symptom: `curl` exited 0, files were created, everything looked fine — but each
file was ~220 bytes.

```bash
file test.jpeg
# → HTML document, ASCII text
```

**`file` reads magic bytes, not the extension.** A `.jpeg` that is actually
HTML is instantly visible. Make this the first check whenever a downloaded file
is the wrong size.

Then read the headers:

```bash
curl -sSI --max-time 20 "https://usghcc.org/wp-content/uploads/2024/09/image00059.jpeg"
```

- `-I` — **HEAD** request: headers only, no body.
- `-s` — silent (no progress meter); `-S` — but still show errors. `-sS`
  together is the combination you almost always want in a script: quiet when it
  works, loud when it does not.

The response:

```
HTTP/2 202
content-type: text/html
sg-captcha: challenge
```

Three things, each decisive:

- **202 Accepted, not 200 OK.** 202 means "received, not acted on yet". No
  static file server returns 202 for an image.
- **`content-type: text/html`** for a `.jpeg` — the server is not sending the
  image.
- **`sg-captcha: challenge`** — SiteGround's anti-bot. The body was an HTML
  `<meta http-equiv="refresh">` pointing at a captcha URL.

**Why `-w` is worth knowing:**

```bash
curl ... -w 'http=%{http_code} type=%{content_type} size=%{size_download}\n'
```

`-w` prints a format string after the transfer, surfacing the status code
*without* a second request — otherwise curl succeeds silently on a 404 or a 202
and you never see it.

**The lesson:** curl exiting 0 means "the HTTP conversation completed", not
"you got what you asked for". A challenge page is a successful HTTP
transaction. Faking a browser `User-Agent` and `Referer` did not help either,
because the challenge requires executing JavaScript — no amount of header
spoofing substitutes for a JS engine. At that point stop scraping and use the
credentialed path (SFTP, or the host's file manager).

---

## 5. Small things worth keeping

**Loop over a file of URLs:**

```bash
while read -r u; do
  curl -sSL --max-time 30 -o "$(basename "$u")" "$u"
done < urls.txt
```

`read -r` disables backslash escaping — without `-r`, a backslash in the input
is eaten. Use `-r` every time.

`-L` follows redirects. `--max-time` bounds the whole operation, so one
unresponsive host cannot hang the loop forever.

**Quote every expansion.** `"$u"`, `"$(basename "$u")"` — an unquoted variable
undergoes word-splitting and globbing, so a filename with a space becomes two
arguments. WordPress uploads are full of spaces and parentheses.

---

## Outstanding — promote to the general vault

General technique, not usghcc-specific; should also land in `devops/01-linux/`:

- [ ] Heredoc quoting, delimiter collisions, and `python3 -` as an editing tool
- [ ] `grep -oE` as an extraction tool; `sort -u` vs `uniq`
- [ ] Diagnosing HTTP with `curl -I` / `-w`, and `file` for magic-byte checks
