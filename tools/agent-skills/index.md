# Agent Skills

Reusable instruction files that configure how a coding agent behaves — standing
preferences, project workflows, review checklists — kept in version control
rather than re-explained every session.

## What's here

1. [[tools/agent-skills/01-skill-files-and-frontmatter|01 — Skill Files and Their Frontmatter]] — the file format, the YAML frontmatter contract, the unquoted-colon bug that stops a skill loading, and how to validate a whole skills directory at once

## Known gaps

- Skill *composition* — several skills applying at once, and how to keep them from contradicting each other
- Testing a skill actually fires when intended, rather than assuming it does

## Related
- [[tools/index|Tools]]
- [[using-ai/index|Using AI]] — the non-builder course on working with these models
