# AI Automation

**New domain, scaffold only — nothing written yet.** Workflow automation, with n8n as the primary tool, connecting APIs and AI models into runnable pipelines rather than one-off scripts. Distinct from [[ai-ml/README|ai-ml/]], which is about how models themselves work — this folder is about *orchestrating* them (and everything else) into workflows.

## Planned reading order

1. `what-is-workflow-automation` — **[Beginner]** — the problem this category solves: triggers, actions, and why "automation platform" beats a pile of cron scripts past a certain complexity
2. `n8n-core-concepts` — **[Beginner]** — nodes, triggers, workflows, executions, credentials
3. `connecting-apis-and-webhooks` — **[Intermediate]** — REST/webhook nodes, authentication, handling pagination and rate limits inside a workflow
4. `ai-agent-workflows-in-n8n` — **[Intermediate → Advanced]** — wiring an LLM into a workflow as a node (classification, extraction, agent-style tool calling), and where that overlaps with [[ai-ml/01-fundamentals/06-agents|agents]]
5. `error-handling-and-retries` — **[Intermediate]** — making a workflow actually production-safe: retry logic, dead-letter handling, alerting on failure
6. `self-hosting-n8n` — **[Intermediate]** — Docker-based self-hosting vs n8n cloud, and the tradeoffs

Other automation tools (Zapier, Make, Temporal) would slot in as separate notes/comparisons if they come up later — n8n is the starting point because it's self-hostable and node-based rather than a black box.

## Related
- [[ai-ml/README|ai-ml curriculum map]] — the models this domain orchestrates
- [[devops/02-docker/README|docker]] — self-hosting n8n runs through this
