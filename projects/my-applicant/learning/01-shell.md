# Shell — my-applicant

Commands actually run while building this project, with what each flag does.
Only new-to-this-project things get an entry; repeats of an already-explained
command don't.

---

## Inspecting a directory of directories

```bash
ls -d ~/code/personal/knowledgebase/projects/*/
```

- `-d` lists **the directories themselves**, not their contents. Without it,
  `ls` descends into each match and prints what's inside — almost never what
  you want when you're surveying a tree.
- The trailing `/` in the glob is doing real work: `*/` only matches
  directories, so files in that folder are excluded before `ls` ever sees them.

Pair the two and you get a clean one-per-line listing of subdirectories.

---

## Checking a tool's cache without running it

```bash
ls ~/.cache/ms-playwright
```

Playwright stores downloaded browser binaries **outside** any project, in a
shared cache. That's why `npx playwright install chromium` is a one-time cost
per machine rather than per repo — and why a project can use Playwright
without the browser appearing anywhere in `node_modules`.

The same pattern shows up elsewhere: `~/.npm` (npm's package cache),
`~/.cache/ms-playwright` (browsers), `~/.ollama/models` (local LLM weights).
When something is huge and reusable, tools put it in a user-level cache.

---

## Reading a version out of a package without a JSON parser

```bash
node -p "require('./node_modules/ai/package.json').version"
```

- `node -p` evaluates the expression and **prints the result**. (`node -e`
  evaluates but prints nothing — you'd need your own `console.log`.)
- `require()` on a `.json` file parses it and hands back an object, so this is
  a one-liner substitute for `jq`.

Compare against the registry:

```bash
npm view ai version                 # latest published version
npm view ai peerDependencies        # any field from the registry manifest
```

`npm view <pkg> <field>` reads any field of the published manifest. Checking
`peerDependencies` is how you find out whether a community package supports
the major version you're on — which is exactly the check that decided whether
this project could use the dedicated OpenRouter and Ollama providers or had to
fall back to a generic OpenAI-compatible shim.

---

## The caret trap in `package.json`

Worth internalising, because it silently cost a version here.

Writing `"ai": "^5.0.0"` by hand and then running `npm install` does **not**
give you the latest `ai`. The caret means "compatible with 5.x", so npm
resolved 5.0.228 while the actual latest was 7.0.58 — two majors behind, with
a different API surface.

```bash
npm install ai@latest    # explicitly asks for latest, rewrites the caret
```

Rule of thumb: hand-writing a version range in `package.json` **pins you to
your own guess**. Prefer `npm install <pkg>@latest` and let npm write the
range, especially for a package you haven't used recently.

---

## Multi-file find-and-replace with perl vs sed

Both appear in this project's history.

```bash
sed -i 's/old/new/' file.ts
```

- `-i` edits the file **in place** rather than printing to stdout.
- `s/old/new/` substitutes the first match **per line**; add `g` for all
  matches on a line.

`sed` is line-oriented, which is its limitation. For a pattern spanning
multiple lines:

```bash
perl -0pi -e 's/\)\n    \.default\(\{\}\)/)\n    .prefault({})/g' file.ts
```

- `-0` slurps the **whole file** as one string, so `\n` in the pattern matches.
- `-p` loops over input and prints it; `-i` edits in place; `-e` supplies the
  script inline.

Reach for `perl -0pi` whenever the thing you're matching crosses a newline.

---

## Running a typechecker without emitting files

```bash
npx tsc --noEmit
```

Typechecks and reports errors, writing **no output files**. This is the fast
inner loop — run it after every few edits rather than saving up errors.

`npx tsc` (without the flag) does the real build, writing to `outDir`.

Empty output means success, which is unnerving the first few times. To make
that explicit:

```bash
npx tsc --noEmit && echo "typecheck clean"
```

---

## Probing an API before writing code against it

```bash
node -e "const {z}=require('zod'); const s=z.object({a:z.boolean().default(false)}).prefault({}); console.log(z.object({x:s}).parse({}));"
```

Before committing to `.prefault()` across a whole schema file, this ran it once
to confirm the behaviour. Thirty seconds here beat a rewrite later.

Generalise the habit: when you're about to apply an unfamiliar API in fifteen
places, spend one command proving it does what you think in **one** place
first.

---

## Grepping a package's type definitions for its exports

```bash
grep -o "^export {.*}" node_modules/ollama-ai-provider-v2/dist/index.d.ts
```

- `-o` prints **only the matching part** of the line, not the whole line —
  invaluable when the match is buried in a very long generated line.

This is how the exact export names (`createOllama`, `createOpenRouter`) were
confirmed rather than guessed. A `.d.ts` file is the authoritative answer to
"what does this package actually export", and it's already on disk — faster
and more reliable than searching the web for a package's README.
