# n8n Core Concepts

> **[Beginner]** · Nodes, connections, executions, credentials — and the data model that causes most beginner confusion.

## The pieces

**Node** — one step. A trigger, an app integration, a transformation, a condition, or a code block.
**Connection** — an edge. Data flows along it from one node's output to the next node's input.
**Workflow** — the graph.
**Execution** — one run, with its input data, its output at every node, and its status. **Kept and inspectable**, which is the main operational advantage over a script.
**Credential** — a stored, encrypted secret, referenced by nodes rather than embedded in them.

## The data model — the part everyone gets wrong

**This is the single biggest source of confusion, and understanding it removes most beginner friction.**

**n8n passes an *array of items* between nodes, not a single object.** Every node receives a list and emits a list:

```js
[
  { json: { id: 1, name: "Ada" },  binary: {} },
  { json: { id: 2, name: "Alan" }, binary: {} }
]
```

**The consequence: most nodes run once per item, automatically.** Fetch 50 rows, connect an email node, and it sends 50 emails — no loop node required. **The iteration is implicit**, which is elegant once you know and baffling before.

**The three things that follow:**

**Item count changes the shape of everything downstream.** A node that returns 0 items stops that branch silently. A node returning 100 makes everything after it run 100 times.

**Some nodes aggregate rather than iterate** — they take *all* items and emit one (or vice versa). Knowing which is which is most of the learning curve.

**Item linking matters for merges.** When branches rejoin, n8n needs to know which item corresponds to which — the "paired item" concept, and the source of the confusing errors when it can't work it out.

## Expressions

Referencing data from earlier nodes:

```js
{{ $json.email }}                        // this item, from the previous node
{{ $node["HTTP Request"].json.id }}      // a specific earlier node
{{ $json.items[0].price * 1.2 }}         // real JavaScript
{{ $now.toISO() }}                       // built-in helpers (Luxon for dates)
{{ $itemIndex }}                         // position in the batch
```

**Expressions are JavaScript**, so anything valid in an expression position works. When they get long, that's the signal to use a Code node instead — a five-line expression in a UI field is unreviewable and undiffable.

## The node types worth knowing

| Node | Does |
|---|---|
| **Webhook** | Trigger on an inbound HTTP request; gives you a URL |
| **Schedule** | Cron-style trigger |
| **HTTP Request** | **The universal escape hatch** — any REST API, with auth |
| **Code** | Arbitrary JavaScript or Python over the items |
| **IF / Switch** | Branch on a condition |
| **Merge** | Rejoin branches (append, merge by key, wait for both) |
| **Set / Edit Fields** | Reshape the JSON |
| **Split In Batches** | Chunk items — **for rate limits** → [[ai-automation/03-connecting-apis-and-webhooks\|note 03]] |
| **App nodes** | Slack, Sheets, Postgres, Gmail, ~400 more |

**The HTTP Request node is the one to learn properly.** App nodes are conveniences over it; when an app node lacks the endpoint you need — which happens constantly — you drop to HTTP Request and it always works.

## Credentials

Stored encrypted, referenced by name, **never inline in a node's parameters.**

n8n handles the OAuth dance for supported services, which is a large part of the value — implementing OAuth2 refresh correctly against six providers is a genuine project → [[backend/05-auth/README|auth]].

**Two things that matter operationally:**
- Credentials are encrypted with a key from `N8N_ENCRYPTION_KEY`. **Lose that key and every stored credential is unrecoverable** — back it up separately from the database → [[devops/09-secret-management/README|secret management]]
- Anyone who can edit a workflow can *use* a credential — they can't read the secret back, but they can make it call anything. **Editor access is effectively credential access**

## Executions, and how you debug

Every run is recorded: input and output **at every node**, timing, and status.

**The debugging loop:**
1. Open a failed execution
2. Click the node that failed — see exactly what it received and what it returned
3. **Pin** that data, so re-running uses the same input without re-hitting the upstream API
4. Fix, re-run from that node

**Pinning is the feature that makes iteration bearable.** Without it, testing step 8 means re-running steps 1–7 and burning API quota each time.

**The operational catch:** execution data is stored in the database, including every payload. On a busy self-hosted instance this grows fast, and pruning is a setting you must configure — and payloads may contain personal data, which is a retention question, not just a disk one → [[ai-automation/06-self-hosting-n8n|note 06]].

## Where the visual model stops helping

**Worth saying plainly, because this folder is not a sales pitch:**

- **Diffing and code review are poor.** A workflow is JSON; a meaningful diff of a node graph is hard, and reviewing one in a pull request is unpleasant → [[git/README|git]]
- **Testing is weak.** There's no real unit-test story; you test by running it
- **Complex logic becomes unreadable faster than code does.** Thirty nodes with nested branches is worse than the equivalent 200 lines
- **Version control needs deliberate setup** — export to files, or use the paid Git integration

**The rule of thumb: when a workflow needs more than a handful of Code nodes, it wanted to be a service.** The platform's advantage is integration and operations, not logic — so keep the logic thin and let the graph do the wiring.

## Related
- [[ai-automation/03-connecting-apis-and-webhooks|connecting APIs and webhooks]]
- [[ai-automation/01-what-workflow-automation-is|what workflow automation is]]
- [[devops/09-secret-management/README|secret management]] — the credential-store argument

*Source: [reference] — from the n8n documentation, Aug 2026.*
