# 05 — The MCP server: how Paddie talks to the app

*MyPaddie, Day 2 onwards (written up 2026-10-08). Files: `src/app/api/mcp/route.ts`,
`src/shared/mcp/{kit,auth}.ts`, every `src/features/*/*.tools.ts`.*
See also: [[02-rules-engine-design]] · [[06-scheduling-and-push]] · [[08-data-modelling-choices]] ·
general course: [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|Tools and MCP]] (the protocol itself —
hosts, clients, servers, discovery; this file is how MyPaddie *uses* it)

## The shape

The AI app (Claude) is the **host**. MyPaddie is a **remote MCP server**: one
Next.js route, `/api/mcp`, speaking MCP over HTTP. Every tool the AI can call is
registered there. The AI never touches the database. It asks, our code runs, and
the result goes back as JSON.

```
Claude  ──HTTP + Bearer token──▶  /api/mcp  ──▶  tool callback  ──▶  feature repo  ──▶  Postgres (RLS)
                                    │                                  │
                                 auth, rate limit,                  same functions the
                                 per-user context                   phone app calls
```

The tools are thin. A tool parses arguments with zod, calls the **same repo
function the app's buttons call** (`createTask`, `startTask`, `payBill`…), and
wraps the result. So the AI and the app can't disagree about the rules: there is
only one implementation ([[02-rules-engine-design]]).

## The route, piece by piece

```ts
const handler = createMcpHandler((server) => {
  const tools = catalogue(server);
  tools.area("Today", () => registerTodayTools(server));
  tools.area("Tasks and habits", () => registerTaskTools(server));
  // … one line per feature
}, { serverInfo: { name: "mypaddie", version: "1.0.0" }, instructions: "MyPaddie is the user's private life coach. Call get_today first…" });
```

- **`createMcpHandler`** (package `mcp-handler`) turns an MCP server definition
  into a Next.js route handler. Exported as `GET`, `POST` and `DELETE` because
  the streamable-HTTP transport uses all three.
- **`instructions`** is sent to the host when it connects: standing orders for
  the model (call `get_today` first, the voice, "check your tools before saying
  you can't"). **Gotcha:** it's read at connect time. Change it, and the user may
  need to reconnect the app before the model sees the new rule.
- **`catalogue(server)`** wraps `server.registerTool` so every tool is recorded,
  with the area it was registered under, *as it's added*. `what_can_paddie_do`
  lists that record. There's no hand-maintained list to drift out of date. This
  is a small, useful pattern: monkey-patch the registrar once and get a
  self-documenting server.

### Auth: every call is a real user

```ts
const authed = withMcpAuth(asUser, verifyToken, { required: true, resourceMetadataPath: "/.well-known/oauth-protected-resource/api/mcp" });
```

- The host signs the user in with OAuth and then sends a **Bearer token** on every
  request. `verifyToken` checks it with Supabase `auth.getClaims` (signature and
  expiry) and rejects anonymous users. Anonymous sign-ins carry
  `role=authenticated` too ([[01-supabase-schema-and-rls]]).
- No token or a bad one → `401` plus a pointer to the OAuth metadata, which is how
  the host knows to start the login flow.
- `dbFrom(ctx)` makes a Supabase client **with the user's own token**, so every
  query in every tool is RLS-scoped. A bug in a tool can't read someone else's
  rows: the database refuses it.

### Per-user context without threading it everywhere

`withUser(db, …)` runs the whole request inside an `AsyncLocalStorage` holder with
the user's profile (time zone, currency, voice, plan). Deep code calls
`currentConfig().timeZone` instead of every function taking a `tz` argument.
*Lesson learned the hard way (see the comment in `user-context.ts`):*
`enterWith` inside an awaited helper doesn't carry back to the caller, so the
holder is entered at the top and filled in later.

### Rate limit before work

`rate_hit` (a Postgres function) counts calls per user, 300 per 10 minutes. A
runaway agent loop gets a JSON-RPC error (`-32000`) with HTTP 429 and
`Retry-After`, before any tool runs.

## The result shape: `ok()` and `toolError()`

```ts
ok(data)        → { content: [{ type: "text", text: JSON.stringify(data) }], structuredContent: data }
toolError(msg)  → { content: [{ type: "text", text: msg }], isError: true }
```

- **Both** `structuredContent` and text: some hosts read JSON, some only show
  text.
- **Two kinds of failure** (the course calls these the two MCP errors):
  - A protocol error: the request was malformed, or you're unauthorised.
  - A tool error (`isError: true`): the call happened, it failed, and the model
    should read why and react ("no single course matches 'Algo' — check
    list_courses").
- **Every reply carries context:** `withMode(db, now, data)` adds the coaching
  `mode` to every result, and during quiet hours a `lateNight` block too. The
  model sets its tone from it without a separate call.

## Tool design: lessons from real bugs

The general course says "the description is the interface". MyPaddie shows
what that means in practice.

### 1. A result the model must say out loud has to be impossible to miss

**Bug:** creating a routine saved the routine, then each step as a task. A step
could be *refused* (the day was full), but the repo still returned
`result: "created"`, with the refusals buried in a list. The model said "done!",
the routine had no steps, and the user found out days later.

**Fix:**
- Make the write **all or nothing**: the first refused step undoes the whole
  routine.
- Return `{ result: "refused", step, reason, saved: false }`.
- Tell the model what to do with it, in the tool's description: *"NOTHING was
  saved — tell them which step and why, and offer a fix."*

Same idea elsewhere:
- `update_routine` returns `notAdded` ("never report them as added").
- `start_task` returns `busy` with what's running ("nothing changed; ask whether
  to pause or finish it").

**Rule:** if the happy path and the failure path look alike in JSON, the model
will report the happy path.

### 2. Never make the model guess an ID

**Bug:** `update_task` needed a `task_id`, but no tool listed recurring tasks
with their IDs. The model could *see* the user's Sunday task in a schedule and
had no safe way to point at it. To its credit it refused to invent an ID, but
the user was stuck.

**Fix:**
- A `list_habits` tool that returns each recurring task's `series_id`.
- `update_task` accepts `habit: <series_id>` as an alternative to `task_id`.
- The repo finds that habit's next row, creating it early if the day hasn't
  arrived yet ([[08-data-modelling-choices]]).

**Rule:** for every "change X" tool, there has to be a "find X" tool that returns
the identifier it needs, and its description should say *"never guess ids"*.

### 3. Names are part of the contract

`list_habits` returns every **recurring task**: weekly meetings, classes, workout
days. "Habit" is the internal word. The user read "habit" as "not my meetings",
and the model could have too. The fix was the **description and title**
("Every recurring task — anything with a repeat rule, not only habits…"), not the
tool name. Renaming a tool breaks any host that has already discovered it.

### 4. Explicit tools for actions, fields for settings

- **Actions** you do *at a moment* get their own tools: `start_task`,
  `pause_task`, `complete_task`, `start_event`, `complete_event`. One flag-driven
  `start_task(pause: true)` was split in two because the model (and the human
  reading the transcript) should see the verb.
- **Properties** of a thing are fields on the existing add and update tools:
  `priority`, `self_care`, `checklist`. A `set_priority` tool would be one more
  thing to discover for no gain.

### 5. Descriptions carry policy, not just syntax

Real lines from MyPaddie's tool descriptions, each a rule the model must follow:

- `priority`: *"Default normal — leave it unless they say it matters more or
  less. Never ask them to rate tasks."* This keeps the field from inflating.
- `self_care`: *"Set it when the user says what something is; don't guess."*
- `tick_step`: *"If `allDone` comes back true, ask whether the task itself is
  done — don't complete it for them."*
- `complete_task`: *"mention [how long it took] only when it's well off the
  plan."*

The model only learns about a rule if it's in the description. The repo enforces
what it *can*, the description covers judgement calls, and you need both.

### 6. Plan limits and errors as data

When a feature isn't in the user's plan, the tool returns a message that says
exactly that. The server instructions say *"tell them exactly that"*, so the
model doesn't paraphrase it into "something went wrong".

## Testing it

Tools are thin, so most testing happens one layer down: pure functions with
`bun test`, SQL with pgTAP ([[03-testing]]). What's left to check by hand is the
**contract**: does the description lead the model to call the tool correctly?
The routine bug only showed up in real use. That's the argument for result shapes
that are hard to misread, not for more unit tests.
