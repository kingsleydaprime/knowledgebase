# Tools & MCP

**Source:** new for the track (folds the tool-calling section from the old agents note), from the [roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer) tools/MCP branch. **Grounded** — MCP is something these projects use in practice, not just reference.

## Function/tool calling — giving a model hands

An LLM only outputs text ([[ai-ml/03-ai-engineer/02-how-llms-work|how LLMs work]]). **Tool calling** lets it *request* that your code run a function — turning "predict text" into "do things." The mechanism:

1. You describe the available tools to the model — each a name, description, and a parameter schema (usually JSON Schema).
2. Instead of a plain answer, the model can emit a **structured request** to call a tool with arguments (it's trained to recognize when a task needs one).
3. **Your application code** executes the function and feeds the result back into the model's context.
4. The model reads the result and continues — answering, or calling another tool.

```
tools available: get_weather(city), convert_temp(value, from, to)

User: "Weather in Lagos, then that temp in Fahrenheit"
Model → calls get_weather("Lagos")          → your code runs it → {"temp_c": 29}
Model → calls convert_temp(29, "C", "F")     → your code runs it → {"temp_f": 84.2}
Model → "It's 29°C (84.2°F) in Lagos."
```

The crucial point: **the model never runs code itself** — it produces a request that *trusted application code* fulfills. What tools exist, whether to actually execute a requested call, and what to return are all your decisions. That control boundary is where [[ai-ml/03-ai-engineer/10-safety-and-production|safety]] (sandboxing, permissioning, confirmation for high-stakes actions) lives. Good tool design: clear names/descriptions (the model picks tools from these), tight schemas, and results scoped small (tool output consumes [[ai-ml/03-ai-engineer/02-how-llms-work|context budget]]).

This loop of call-tool → observe → decide is the backbone of [[ai-ml/03-ai-engineer/08-agents|agents]].

## MCP — the Model Context Protocol

Without a standard, every app hand-codes "here's how *this* model calls *this* API" — an N×M integration mess. **MCP (Model Context Protocol)** is an open standard that decouples the two: a tool/data source is exposed **once** as an MCP server, and any MCP-compatible client can use it. Build a tool once, use it everywhere — the same idea as a universal adapter, applied to LLM tool/context integration.

The pieces:

- **MCP server** — exposes capabilities: **tools** (functions the model can call), **resources** (data/context it can read), and **prompts** (reusable templates). You write a server to wrap a database, an API, a filesystem, a SaaS product.
- **MCP client** — connects to servers and makes their capabilities available to a model.
- **MCP host** — the application the user interacts with (an IDE assistant, a chat app) that runs one or more clients. (This assistant's environment is an MCP host — the connectors it can call are MCP servers.)
- **Transport** — how client and server talk: local (stdio, a subprocess on your machine) or remote (HTTP/SSE, a networked service).

```
Host (e.g. an AI assistant)
  └─ Client ──MCP──► Server: Gmail   (tools: send, search; resources: messages)
  └─ Client ──MCP──► Server: your DB (tools: query; resources: schema)
```

**Why it matters for an AI engineer:** MCP is becoming the standard way to give models capabilities, so "expose my system as an MCP server" is increasingly how you integrate AI with existing software — write the server once and any MCP-aware host (across vendors) can use it, instead of a bespoke integration per product. Worth building a small server to internalize the model; it's a modest amount of code over the tool-calling concepts above.

## Related
- [[ai-ml/03-ai-engineer/08-agents|Agents]] — the tool-calling loop, scaled into autonomous multi-step behavior
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — where tool definitions attach to a request
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — tool sandboxing and permissioning
