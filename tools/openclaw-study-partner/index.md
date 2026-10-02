# OpenClaw Study Partner

> A local AI that reads this knowledgebase and quizzes you on it, running on your own laptop with Ollama. The lesson behind the choices — sizing, speed, context and permissions — is [[ai-ml/03-ai-engineer/16-local-and-open-models|local and open models]]. Set up 2026-10-02, for sparring — hints, questions, critique — not for handing over answers. See [[learning/06-ai-as-sparring-partner|AI as a sparring partner]].

## What this sets up

- A **separate OpenClaw agent called `study`**. Your existing default agent and its Telegram connection don't change.
- It runs **`qwen3.5:4b`** through Ollama, CPU-only: small enough for this laptop, with tool calling, which OpenClaw needs to read files.
- It can **read files and nothing else** — no shell, no web, no writing.
- Its persona and rules live in [[tools/openclaw-study-partner/SOUL|SOUL.md]] and [[tools/openclaw-study-partner/AGENTS|AGENTS.md]], copied into its workspace.
- It's only reachable from your terminal — it isn't connected to Telegram.

## Why this model

The laptop: 16 GB of RAM (about 7 GB free with your usual apps open), an Intel i7-8650U, and an NVIDIA MX130 with 2 GB of video memory — too little to help much, so models run on the CPU.

| Model | Download | Fits? |
|---|---|---|
| `gemma4:latest` (8B, already pulled) | 9.6 GB | No — more than the free RAM; it will swap and crawl |
| `qwen3.5:latest` (9.7B, already pulled) | 6.6 GB | Barely — slow on CPU |
| **`qwen3.5:4b`** | 3.4 GB | **Yes** — usable speed, tool calling, image input |
| `qwen3.5:2b` | smaller | Faster fallback if 4B feels slow |

**It runs on the CPU only.** Measured on 2026-10-02: Ollama on its own put 10% of the model on the MX130 and ran at **3.91 tokens per second**; on the CPU alone, **5.09** — about 30% faster, because moving work to and from a 2 GB GPU costs more than it saves. The `Modelfile` in this folder builds `study-qwen3.5:4b`, a variant with `num_gpu 0` built in. CPU temperature stayed at 40–55 °C under load, so heat isn't a limit. Its context window is **32K tokens**. OpenClaw's own instructions take about 8,800 tokens before you type anything, and it keeps about 8,400 in reserve for the reply. A 16K window, tried first to save memory, overflowed on the first message. 32K leaves room for OpenClaw, one lesson file and a conversation.

**Thinking is off by default for this agent.** Qwen 3.5 reasons silently before answering unless told not to. Measured on this laptop on 2026-10-02: about 4.6 tokens per second, and the first test — "two sentences", with thinking on — produced 1,087 tokens and took four minutes. Most of that was hidden reasoning. With `thinkingDefault: "off"`, answers start in seconds. The first message after a while also waits about 20 seconds while Ollama loads the model into memory.

**Small models get things wrong more often.** That's acceptable here because the notes are the source of truth — the agent is told to read the file first and name it. Treat it as a quiz partner, not an authority. If it says something the notes don't, check the notes.

## Setup — run these yourself

From the vault root (`~/code/personal/knowledgebase`):

```bash
# 1. Get the model, build the CPU-only variant from ./Modelfile, and check its speed.
#    "eval rate" is tokens per second; expect about 5 on this laptop.
ollama pull qwen3.5:4b
ollama create study-qwen3.5:4b -f tools/openclaw-study-partner/Modelfile
ollama run study-qwen3.5:4b --think=false --verbose "Explain a token bucket in two sentences."

# 2. Back up OpenClaw's config, credentials and sessions before changing anything.
openclaw backup create

# 3. Give the study agent its persona and rules.
mkdir -p ~/.openclaw/workspace-study
cp tools/openclaw-study-partner/SOUL.md tools/openclaw-study-partner/AGENTS.md ~/.openclaw/workspace-study/

# 4. Add the agent. Check first, then apply.
openclaw config patch --file tools/openclaw-study-partner/study-agent.patch.json5 --dry-run
openclaw config patch --file tools/openclaw-study-partner/study-agent.patch.json5

# 5. Restart the gateway and confirm the agent exists.
openclaw daemon restart
openclaw agents list

# 6. Talk to it.
openclaw tui --session agent:study:main
```

On first run OpenClaw may add a few files of its own to the workspace (such as `IDENTITY.md`) and ask you a couple of setup questions. That's its normal bootstrap.

## Using it

Prompts that work well:

- `quiz me on backend/03-structuring-a-backend/01-layers-controllers-services-repositories`
- `check my explanation of the token bucket: <your explanation>`
- `what's in week 2 of SWE 101?`
- `tooling mode — summarise the outbox lesson` (when you genuinely want an answer)

Give it a file path when you can. A small model searching 1,150 notes for "that coupling thing" will struggle; reading one file it's been pointed to works well.

## Safety notes

- **Read access is machine-wide.** The vault is outside the agent's workspace, so `tools.fs.workspaceOnly` stays off (its default), and `read` can open any file your user can. That's fine for a terminal-only agent you're driving yourself. **Don't connect this agent to Telegram or any chat channel** as it is: anyone who could message it could ask it to read files like `~/.ssh` or `~/.openclaw/credentials`.
- **Your existing default agent is more exposed than this one.** It uses `tools.profile: "coding"` — shell access, file writes, web search — and it answers on Telegram. Your `ownerAllowFrom` limits owner commands, but the Telegram group setting (`"*"` with `requireMention`) means it can be added to groups. Worth reviewing; OpenClaw's own guidance for small local models is the `minimal` profile, partly because [small models are more easily misled by prompt injection](https://docs.openclaw.ai/providers/ollama/recipes).
- **Keep OpenClaw updated.** Its file-access boundaries have had [security fixes](https://advisories.gitlab.com/npm/openclaw/CVE-2026-32002/) — `openclaw --version` against the release notes now and then.

## Undo

```bash
openclaw agents delete study
```

Or restore the backup from step 2.

## Files

- [[tools/openclaw-study-partner/SOUL|SOUL.md]] — persona: sparring partner, not answer machine
- [[tools/openclaw-study-partner/AGENTS|AGENTS.md]] — where the notes are, and the rules: read first, cite the file, look up acronyms in `glossary.json`, don't reveal hidden answers
- `Modelfile` — the CPU-only model variant
- `study-agent.patch.json5` — the config change, validated with `--dry-run` against your config on 2026-10-02
