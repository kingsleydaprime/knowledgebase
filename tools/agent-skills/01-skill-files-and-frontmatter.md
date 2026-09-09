# Skill Files and Their Frontmatter

An **agent skill** is a folder containing a `SKILL.md`: a markdown file with a
YAML frontmatter block on top and instructions below it. The agent reads the
frontmatter of every installed skill up front, and loads a skill's *body* only
when its description looks relevant to what you're doing.

```
~/.agents/skills/<skill-name>/SKILL.md      # canonical copy
~/.claude/skills/<skill-name> -> ../../.agents/skills/<skill-name>
```

Keeping one canonical directory and symlinking it into each client's
skills folder means the same skill serves several tools without duplication.
See [[devops/01-linux/09-symbolic-links|symbolic links]] — `ln -sfn` is the
spelling that makes re-pointing idempotent.

## The frontmatter is a contract, not decoration

```yaml
---
name: dev-workflow
description: 'What this skill covers and exactly when to load it.'
---
```

- **`name`** — must match the directory name.
- **`description`** — the only thing the agent sees before deciding whether to
  load the skill. It is a *routing* string, not a summary: say what the skill
  covers **and the situations that should trigger it**. A description that
  describes the content but not the trigger produces a skill that never loads.

Everything below the closing `---` is ordinary markdown, loaded in full once
the skill is selected.

## The failure mode: an unquoted colon

A skill silently not loading, with `Invalid YAML frontmatter` in the logs, is
almost always this:

```yaml
description: Standing preferences for coding sessions. Triggers: new projects, commits
#                                                      ^^^^^^^^^
```

**In YAML, `: ` (colon followed by whitespace) inside an unquoted scalar starts
a nested mapping.** The parser reads `Triggers:` as a key, finds it somewhere a
key cannot legally appear, and reports:

```
mapping values are not allowed here
```

An error phrased in terms of YAML's grammar, which is why it doesn't obviously
mean "your sentence contains a colon".

**Fix: quote the value.**

```yaml
description: 'Standing preferences for coding sessions. Triggers: new projects, commits'
```

Descriptions are exactly the field that attracts this, because a good one is
prose — and prose contains colons, `#`, quotes and dashes.

Characters that force quoting in YAML: `: ` anywhere, a trailing `:`, and a
leading `#`, `&`, `*`, `!`, `|`, `>`, `%`, `@`, `` ` ``, `{`, `[`.

**Just quote every prose value and stop thinking about it.** Single quotes are
the simpler choice — the only escape is `''` for a literal apostrophe, with no
backslash rules. If the text contains both apostrophes and double quotes, let a
serialiser do it rather than hand-escaping:

```python
yaml.dump(value, default_style="'", width=10**9, allow_unicode=True)
```

(`width` prevents PyYAML wrapping a long description across lines;
`allow_unicode` keeps em-dashes as characters instead of escapes.)

## Validate the whole set, not the file named in the error

The error names one skill, but the useful question is which of them parse. A
sweep takes seconds and the diagnosis comes from the *contrast* between the
passing and failing files:

```bash
cd ~/.agents/skills && python3 - << 'PY'
import os, re, yaml
for d in sorted(os.listdir('.')):
    f = os.path.join(d, 'SKILL.md')
    if not os.path.exists(f): continue
    m = re.match(r'---\n(.*?)\n---\n', open(f, encoding='utf-8-sig').read(), re.S)
    if not m: print(f"{d:32s} NO FRONTMATTER"); continue
    try:
        print(f"{d:32s} OK   {list(yaml.safe_load(m.group(1)).keys())}")
    except Exception as e:
        print(f"{d:32s} FAIL {str(e).splitlines()[0]}")
PY
```

Worth running after hand-editing any skill, and cheap enough to keep as a
pre-commit check on a skills repo.

If everything *looks* right and still fails, check the bytes rather than the
characters — a UTF-8 BOM or CRLF line endings from another editor break strict
parsers invisibly:

```bash
file ~/.agents/skills/*/SKILL.md     # reports "with BOM" / "with CRLF line terminators"
```

`open(path, encoding='utf-8-sig')` decodes and strips a BOM if present.

## Writing a description that actually routes

The body can be excellent and never run if the description doesn't match how
you talk. Two habits help:

- **Include trigger phrases in your own words** — the things you actually type
  when the skill should fire, not a formal topic label.
- **Say when *not* to use it** if a sibling skill overlaps, so the agent picks
  between them instead of loading both.

## Related
- [[devops/01-linux/09-symbolic-links|Symbolic links]] — how skills get shared across clients
- [[tools/index|Tools]]
