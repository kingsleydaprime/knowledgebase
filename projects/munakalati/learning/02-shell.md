# Shell — Munakalati

**Domain:** the command line, as it showed up in [[projects/munakalati/learning/README|munakalati]] — a `bun`-scripted ops workflow, `curl` against an undocumented API, and the commands used to audit this codebase while writing these notes.
**General version:** [[devops/01-linux/README|devops/01-linux]] — especially [[devops/01-linux/12-bash-scripting|bash scripting]] and [[devops/01-linux/16-sed-and-awk|sed and awk]].

---

## Part 1 — the project's own commands

### `bun` as a script runner

```json
"scripts": {
  "dev": "next dev",
  "build": "next build",
  "migrate": "bun run src/migration.js",
  "backfill-images": "bun run src/backfill-images.js",
  "dedup": "bun run src/dedup.js --dry-run",
  "dedup:apply": "bun run src/dedup.js",
  "fix-slugs": "bun run src/fix-slugs.js --dry-run",
  "fix-slugs:apply": "bun run src/fix-slugs.js"
}
```

**`bun run <file.js>` executes a JS file directly**, the way `node file.js` would — but bun brings three things that matter for one-off ops scripts:

1. **Native ESM.** The scripts use top-level `import` in a `.js` file with no `"type": "module"` and no build step. Node would need the file renamed `.mjs` or the package flagged.
2. **`.env` loaded automatically.** No `dotenv` import, no `--env-file` flag. `process.env.SANITY_API_TOKEN` is just there.
3. **Fast cold start**, which matters when you're iterating on a script you'll run twenty times.

That auto-`.env` loading is convenient and is also the foot-gun noted in [[projects/munakalati/learning/05-migration/05-repair-scripts|migration/05]]: `.env` and `.env.migration` both exist, bun loads `.env`, and **which dataset a destructive script hits is decided by which lines are commented out in a file you're not looking at.** Being explicit is one flag:

```bash
bun --env-file=.env.migration run src/migration.js
```

**The `:apply` suffix convention is the important part of that scripts block** — `bun run dedup` previews, `bun run dedup:apply` destroys. The safe verb is the short one.

### Sanity CLI — the backup that made everything else safe

```bash
sanity dataset export production ./sanity-export.tar.gz    # → 70MB
sanity dataset import ./sanity-export.tar.gz production    # the way back
sanity documents query '*[_type == "post"][0...3]{_id, title}'
```

`sanity.cli.ts` is what lets these run in the project directory with no `--project` flag.

**`dataset export` before the first destructive run is non-negotiable**, and 70MB is a trivial price. The export is an ndjson document dump plus image assets, tarred — which also means it's greppable in an emergency:

```bash
tar -xzf sanity-export.tar.gz -C /tmp/export        # -x extract, -z gunzip, -f file, -C into dir
grep -c '"_type":"post"' /tmp/export/data.ndjson    # count posts in the backup
```

`tar` flags are worth committing to memory as pairs — **`-czf` to create, `-xzf` to extract**, `-t` to list without extracting. `tar -tzf archive.tar.gz | head` is always the right first move on an archive you didn't make, because there's no guarantee it unpacks into a subdirectory rather than all over your cwd.

### `curl` before code

From `src/docs.md`:

```bash
curl 'https://www.wixapis.com/blog/v3/posts?featured=false&categoryIds=a68da372-...' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: <AUTH>'
```

The habit — hit the endpoint by hand, save the response, *then* write the client — is argued for in [[projects/munakalati/learning/05-migration/02-reading-the-wix-api|migration/02]]. The flags that make it practical:

```bash
curl -s URL | jq '.'                    # -s: no progress bar, so the pipe stays clean
curl -i URL                             # include response headers
curl -o out.json URL                    # write to a file
curl -s URL | jq 'keys'                 # top-level keys — fastest way to see a shape
curl -s URL | jq '.posts | length'      # does the count match what the API claims?
```

**`jq 'keys'` is the shell version of the `--debug` flag** built into `backfill-images.js`. Both answer "what is actually in this response", which the documentation didn't.

**Single-quote the URL.** A URL containing `&`, unquoted, backgrounds the command at the first ampersand and runs the rest as separate jobs — a genuinely confusing failure the first time it happens.

## Part 2 — commands used to audit this codebase

These were run while writing these notes. Each earned its place by answering a question that reading the code top-to-bottom wouldn't.

### Mapping the codebase by size

```bash
find src -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' \) -exec wc -l {} + | sort -rn | head -30
```

- **`\( … -o … \)`** groups the OR'd name tests. The backslashes escape the parentheses *from the shell*, which would otherwise read them as a subshell. Without the group, `-o` binds loosely and `-type f` applies to only the first branch.
- **`-exec wc -l {} +`** — the `+` (rather than `\;`) batches all matches into **one** `wc` invocation instead of one per file. Much faster, and as a bonus `wc` prints a `total` line.
- **`sort -rn`** — numeric, reversed. `sort -r` alone sorts *lexically*, where `9` beats `1000`.

**Sorting a codebase by line count is the fastest way to find where the complexity is.** It put `about/page.tsx` (590 lines) and `migration.js` (414) at the top immediately, and those turned out to be the two most interesting files in the repo.

### Where the client/server boundary is

```bash
grep -rl '"use client"' src --include='*.tsx' | sort
```

`-r` recursive, **`-l` prints filenames only** (not matching lines), `--include` restricts by glob. Five files — the entire client boundary of the app, answered in one command.

### Finding dead exports

```bash
for q in $(grep -oP 'export const \K\w+Query' src/sanity/lib/queries.ts); do
  n=$(grep -rl "$q" src --include='*.tsx' --include='*.ts' | grep -vc 'queries.ts')
  echo "$n  $q"
done | sort -n
```

This found the two GROQ queries nothing references. The pieces:

- **`grep -oP`** — `-o` prints **only the matched part** rather than the whole line; `-P` enables Perl regex, needed for `\K`.
- **`\K`** — "discard everything matched so far". `export const \K\w+Query` matches the whole phrase but *outputs* only `allPostsQuery`. Without it you'd need a capture group plus `sed` to extract it. **`grep -oP 'prefix\Kpattern'` is the concise idiom for "print the thing after the marker"**, and it comes up constantly.
- **`grep -vc`** — `-v` invert, `-c` count. Together: *count the lines that don't match*, i.e. references outside `queries.ts` itself.

**The general shape — `for x in $(names); do count references to x; done | sort -n`** — finds dead code in any language. Anything with `0` is a candidate.

### Interrogating `.gitignore`

```bash
git check-ignore -v src/migration.js
# .gitignore:51:migration.js    src/migration.js
```

**The most useful git command nobody knows.** It prints the file, line number and text of the rule that excluded a path — turning "why isn't the migration script in the repo?" into a five-second answer. That's the whole finding in [[projects/munakalati/learning/01-git|01 — git]].

Companion, worth running once on any repo you inherit:

```bash
git status --ignored --short | grep '^!!' | grep -v node_modules
```

`!!` is the ignored marker in short format; the second `grep -v` drops the `node_modules` noise.

### Reading a file safely — `sed -n` and redaction

```bash
sed -n 58,90p src/components/home/cms/Testimonials.tsx     # print lines 58–90
```

`-n` suppresses sed's default "print every line"; `58,90p` prints that range. **`sed -n START,ENDp` is the precise way to read a slice of a large file** without `head`/`tail` arithmetic.

```bash
sed 's/=.*/=<redacted>/' .env
```

Replace everything after the first `=` with a placeholder. This is how the env files were inspected for **variable names** without their values ever reaching the terminal. **When you need to look at a secrets file, redact in the same command that reads it** — not afterwards, and never by opening it and trusting yourself to skim past.

### Counting and grouping

```bash
git log --format='%an' | sort | uniq -c | sort -rn
#      43 Kingsley Ihemelandu
#       2 Joseph Awe
```

**`sort | uniq -c | sort -rn` is the universal group-by.** `uniq -c` counts *adjacent* duplicates, which is why the first `sort` is mandatory — omit it and you get a wrong answer rather than an error, the worst kind. The final `sort -rn` orders by count.

One pipeline, endless uses: who wrote this, which error is most common in a log, which file changes most often:

```bash
git log --format= --name-only | sort | uniq -c | sort -rn | head
```

```bash
git log --format='%s' | grep -cE '^(feat|fix|chore|docs|refactor|test)(\(.+\))?:'
```

`-c` counts matching lines, `-E` extended regex. 28 of 45 — the commit-convention drift, measured rather than asserted.

### Creating a tree in one command

```bash
mkdir -p projects/munakalati/learning/{03-sanity,04-frontend,05-migration} \
         projects/munakalati/interview \
         frontend/frameworks/sanity
```

- **`-p`** creates intermediate directories and **doesn't error if the target exists** — which is what makes it safe to re-run.
- **`{a,b,c}` is brace expansion**, performed by the shell before `mkdir` ever runs: the line above expands to six paths. No spaces after the commas, and it works with any command — `cp file{,.bak}` expands to `cp file file.bak`, the classic one-token backup.

## Part 3 — heredocs, and scripting the edits

Every file in these notes was written with a heredoc:

```
cat > 01-git.md << 'XEOF'
# Git — Munakalati
...content with `backticks`, $variables and ! marks, all literal...
XEOF
```

**Quoting the delimiter is the whole trick.** Quoted (`<< 'XEOF'`), the shell passes the body through untouched. Unquoted (`<< XEOF`) it expands `$variables`, executes `` `backticks` `` and interprets `\`. For writing markdown or code — both *stuffed* with `$` and backticks — the quoted form is nearly always what you want, and forgetting the quotes corrupts the file silently instead of erroring.

### The mistake actually made writing this file

The first attempt at this note used `<< 'EOF'` as its delimiter, and the example above originally used `EOF` too. **The shell terminates a heredoc at the first line that is exactly the delimiter** — it has no idea the line is inside a fenced code block in some markdown. So the body ended early at the example's `EOF`, the file was written half-finished, and every remaining line of prose was handed to zsh as commands. It died on `*full*` — zsh trying to glob a word from a sentence.

Two lessons, both cheap:

- **Use a delimiter that cannot appear in the body.** This file is written with `MDDOC`; the example inside it uses `XEOF`. Nested-heredoc collisions are otherwise invisible until they fire.
- **Check the tail of what you wrote** (`tail -5 file`) when a heredoc-heavy command errors — the truncation point tells you exactly which line closed it.

### Python heredocs for edits with logic

```
python3 - << 'PY'
import pathlib
p = pathlib.Path("02-data-fetching-and-caching.md")
s = p.read_text()
old = "the homepage makes **seven separate requests to Sanity**"
new = "the homepage makes **eleven separate requests to Sanity**"
assert old in s, "anchor not found"          # ← fail loudly rather than write nothing
s = s.replace(old, new)
p.write_text(s)
print("patched")
PY
```

Three things this has over `sed -i`:

- **`python3 -` reads the program from stdin** — that's what the bare `-` means. No temp file.
- **Multi-line, punctuation-heavy matching with no escaping.** The same replacement in `sed` would need every `*`, `/` and `.` escaped.
- **`assert old in s` before writing.** Without it, a match that silently fails rewrites the file unchanged and reports success — and you discover it three steps later. **Assert the precondition, then write.** This is the single most valuable habit in scripted editing, and it's one line.

Reach for `sed -i 's/x/y/g'` for a simple literal swap; reach for a Python heredoc the moment there's a condition, a multi-line match, or something worth asserting first.

## Related
- [[devops/01-linux/12-bash-scripting|bash scripting]] — including the ops-script flag conventions from this project
- [[devops/01-linux/16-sed-and-awk|sed and awk]] · [[projects/arete/learning/devops/05-grep-in-depth|grep in depth]] · [[projects/arete/learning/devops/06-find-in-depth|find in depth]]
- [[projects/munakalati/learning/01-git|01 — git]] · [[projects/munakalati/learning/05-migration/05-repair-scripts|migration/05 — repair scripts]]
