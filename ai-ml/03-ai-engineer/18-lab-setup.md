# Lab Setup

**[Beginner]** — the environment the exercises in [[ai-ml/03-ai-engineer/19-practice-exercises|note 19]] assume. Thirty minutes, one API key, about $2 of spend for the whole exercise set.

Notes 1–17 are the map. This is where the reps start. The same pattern as [[cybersecurity/02-ethical-hacking/05-home-lab-setup|the ethical-hacking home lab]] and the [[devops/01-linux/15-rhcsa/15-practice-exercises|RHCSA practice set]]: stand the lab up once, then work through the exercises against it.

## What you need

| | |
|---|---|
| **Node 20+** and a package manager | `node --version` |
| **One API key** | A [Vercel AI Gateway](https://vercel.com/docs/ai-gateway) key reaches every provider through one key and `provider/model` strings — the least setup. A direct OpenAI or Anthropic key works too |
| **A spending limit** | Set it in the provider dashboard *before* your first call. Non-negotiable — see below |
| **Roughly $2** | The whole set, if you use small models. An accidental loop can spend more |

Python works equally well for all of this (`openai`, `anthropic`, or `litellm`); the solutions are TypeScript because that's what [[ai-ml/03-ai-engineer/04-calling-models|04-calling-models]] uses. Translate freely — the exercises are about the concepts, not the SDK.

## Setup

```bash
mkdir ai-lab && cd ai-lab
npm init -y
npm pkg set type=module
npm install ai zod
npm install -D tsx typescript @types/node
```

Put your key in `.env` and **add `.env` to `.gitignore` before you write anything into it**:

```bash
echo ".env" >> .gitignore
echo "AI_GATEWAY_API_KEY=your_key_here" >> .env      # or OPENAI_API_KEY / ANTHROPIC_API_KEY
```

Run files with `node --env-file=.env $(npm root)/.bin/tsx script.ts`, or add a script to `package.json`. A leaked key in a public repo gets found by scrapers in minutes and spent — this is the single most common beginner incident in applied AI, and it is entirely preventable at this step.

## The first call

```ts
// hello.ts
import { generateText } from "ai";

const { text, usage } = await generateText({
  model: "anthropic/claude-haiku-4.5",
  prompt: "In one sentence: what is a token?",
});

console.log(text);
console.log(usage);            // always look at this
```

If that prints, the lab works.

**Print `usage` on every call while you're learning.** Input tokens, output tokens, and therefore cost. Developing the reflex of seeing the token count next to the output is what makes [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|cost & latency]] concrete rather than theoretical.

## Picking a model

Don't take model IDs from a note — including this one. They're released and retired constantly, and a stale ID is a confusing 404. Get the current list:

```bash
curl -s https://ai-gateway.vercel.sh/v1/models | jq -r '.data[].id'
```

For the exercises: use a **small, cheap model** (a Haiku/mini/Flash tier) by default, and switch to a frontier model only where an exercise says the small one should fail. Watching a task fail on a small model and succeed on a large one is worth more than reading about capability tiers.

## Verify the API before you write against it

The AI SDK changes across versions — parameters get renamed, functions get superseded. Anything you remember, or read in a note written months ago, may be wrong.

The docs ship inside the package and always match what you installed:

```bash
ls node_modules/ai/docs/           # version-matched documentation
grep -rn "inputSchema" node_modules/ai/docs/ | head
cat node_modules/ai/package.json | grep '"version"'
npm view ai version                # compare against latest
```

This is a habit, not a one-off. The notes in this track deliberately mark SDK code as *illustrative* for exactly this reason — the concepts are stable, the function signatures are not.

## Guardrails before you start

Three things that turn a cheap lab into an expensive one:

- **No spending cap.** Set it in the dashboard now.
- **An agent loop with no stop condition.** Every loop in these exercises gets a step limit ([[ai-ml/03-ai-engineer/08-agents|agents]]). A runaway ReAct loop calling a frontier model is how people wake up to a three-figure bill.
- **A retry that retries on the wrong thing.** Retrying a 400 (your bad request) just spends money failing ([[ai-ml/03-ai-engineer/13-reliability-and-plumbing|reliability]]).

Add a `data/` folder for exercise inputs and a `results/` folder for eval output. Commit the lab — you'll want to diff prompt changes against eval scores later, and that only works if the prompts are in version control.

## Key insight

An applied-AI lab is three things: a key with a cap on it, a small model you're not afraid to waste, and the token count printed next to every output. Everything else in the exercises builds on that.

## Related
- [[ai-ml/03-ai-engineer/19-practice-exercises|Practice Exercises]] — start here once this runs
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — what you just did, in depth
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|Cost, Caching & Latency]] — why `usage` is printed on every call above
- [[cybersecurity/02-ethical-hacking/05-home-lab-setup|Ethical hacking home lab]] — the same lab-then-exercises pattern in another domain
