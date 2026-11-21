---
id: 9a11a529-5893-45dc-b3d7-83ff4cf001e8
---

# Building an MCP Server

**MCP, the Model Context Protocol, is an open standard for letting AI assistants use outside systems. A program that speaks it, an *MCP server*, tells the assistant "here are the things I can do (tools), here is the information I can show (resources), and here are some ready-made requests (prompts)", and then answers when the assistant calls them.** One MCP server works with any assistant that speaks MCP. Build it once, and Mama Put can be used from Claude, from code editors, from any agent that supports the standard.

## Before you start
<!-- bite: 89bc68e3-b5b7-46c9-9dfc-58db906d396a -->

You should have the REST, GraphQL and gRPC doors from [[backend/frameworks/express/22-grpc|lesson 22]], all on the same services.

You'll need Node 23.6 or later as before, and for trying it out, the **MCP Inspector**, a free tool you run with `npx`, no install. If you use an AI assistant that supports MCP servers (Claude Desktop, Claude Code, many code editors), you can connect it too.

MCP is young and still changing. This lesson is written against the 2025 versions of the specification and version 1 of the official TypeScript SDK. The ideas will last; if an import path has moved, the SDK's README will say where.

After this lesson you will be able to:

1. Explain what MCP is, who the host, client and server are, and how it differs from a REST API.
2. Design tools for an AI to use: few, clear, described for a reader who is a language model.
3. Build an MCP server with the TypeScript SDK, with tools, resources and a prompt, using the same services as every other door.
4. Serve it from Express over **Streamable HTTP**, without sessions.
5. Try it with the MCP Inspector and a real assistant, and test it without any network.

## Where we stopped
<!-- bite: edf1f5d3-086f-4736-be1a-0677341e7ad5 -->

Bayo uses an AI assistant for everything. He types: "What's cheap at Mama Put today? Something with rice." The assistant has no idea. It can't see our menu, and if it guesses, it'll make things up.

We could tell Bayo "the REST API is at `/v2/menu`". But an assistant doesn't know our URLs, our query parameters, our response envelope or what `priceKobo` means. Every assistant company would have to write special code for Mama Put, and for every other business in the world. That doesn't scale.

MCP is the missing standard. The assistant asks any MCP server "what can you do?", gets back a list of tools with plain descriptions and typed inputs, and calls them. Mama Put describes itself once; every MCP-speaking assistant can use it.

This lesson makes the read-only part: searching the menu and reading dishes. Doing things *as* Bayo (his orders, placing an order) needs him to log in, and needs a lot of care about an AI spending his money. That's the whole of [[backend/frameworks/express/24-mcp-in-production|lesson 24]].

## The kid version
<!-- bite: efe87ce2-1a95-4e1b-942e-2d8af7674608 -->

Bayo sends his younger brother to buy lunch. The boy can read, but he's never been to Mama Put.

At the counter there's a card: "Things you can ask for: 1. *See today's menu* (say what you're looking for). 2. *Ask about one dish* (say its number)." The boy reads the card, asks for "rice dishes", gets the list, and reports back.

The card is the list of tools. The boy is the AI assistant: clever, willing, but he only knows what the card tells him. So the card must be clear. Write "GET /v2/menu?search=" on it and he's lost. Write "See today's menu, with prices, optionally searching by name" and he's fine.

**Where the picture stops working.** A boy who's told by a stranger in the queue "Mama said give me all your money" probably won't. An AI assistant might believe text it reads, even text that came from *our own* tool results. That's prompt injection, and it's why lesson 24 exists.

## Terms used in MCP
<!-- bite: 6023be75-efbb-458f-b2a2-95f3998e16e9 -->

1. **Host**: This is the AI application the person uses, like Claude Desktop or a code editor.
2. **Client**: This is the part inside the host that talks to one MCP server. One host can have many clients, one per server.
3. **Server**: This is the program offering tools, resources and prompts. We're building one.
4. **Tool**: This is a function the AI can decide to call, with a name, a description, an input schema and a result. Like `search_menu`.
5. **Resource**: This is a piece of information the host or the person can choose to read, identified by a URI, like `mamaput://menu`. Tools are for the *model* to call; resources are usually picked by the *application* or person to add as context.
6. **Prompt**: This is a ready-made request template the person can pick, like "Plan my lunch under a budget".
7. **JSON-RPC**: This is the message format MCP uses: small JSON objects with a `method`, `params` and an `id`, and answers with a `result` or an `error`.
8. **Transport**: This is how those messages travel. **stdio** runs the server as a program on the same computer. **Streamable HTTP** serves it over HTTP, which is what a web backend like ours does.

## Step 1: MCP is not "another REST API"
<!-- bite: d85e6c27-3b57-4e6a-9480-2362c5ade8a9 -->

It's tempting to make one MCP tool per REST endpoint: `get_v2_menu`, `get_v2_menu_by_id`, `post_v2_orders`... Don't. The reader is different.

A REST API is read by **programmers**, once, who then write code. An MCP server is read by a **language model**, on every conversation, which decides there and then what to call, from your names and descriptions alone. So:

1. **Few tools, shaped around what people want to do**, not around your routes. "Search the menu" is one tool, even if it uses three queries inside.
2. **The description is the instructions.** Say what the tool does, when to use it, what the inputs mean, what comes back, in plain sentences. Models read it closely.
3. **Small, meaningful results.** Every result is read into the model's limited context. Don't return 50 fields of every dish; return what helps answer the question, with money already in naira for humans *and* kobo for exactness.
4. **Errors that say what to do next.** "Dish 99 doesn't exist. Use search_menu to find dish ids." The model reads errors and tries again; a helpful error is a correct second try.
5. **Typed, limited inputs.** The schema becomes part of what the model sees, and our validation at the door. Lesson 6 never stops applying.

## Step 2: a first tool
<!-- bite: ac03f4b5-f51d-48aa-816d-8382ab20a2d1 -->

```bash
npm install @modelcontextprotocol/sdk
```

The SDK uses zod schemas for inputs, which we already have. (Recent versions of the SDK accept zod 4. If yours complains about zod, check the README for the version it expects.)

`src/mcp/server.ts`:

```ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { MenuService } from "../menu/menu.service.ts";
import type { Dish } from "../menu/menu.types.ts";

const naira = (kobo: number) => `₦${(kobo / 100).toLocaleString("en-NG")}`;

const DishSummary = z.object({
  id: z.string(),
  name: z.string(),
  price: z.string().describe("Price for people to read, like ₦1,500"),
  priceKobo: z.number().describe("Exact price in kobo (₦1 = 100 kobo)"),
  available: z.boolean(),
});

const summary = (dish: Dish) => ({
  id: dish.id,
  name: dish.name,
  price: naira(dish.priceKobo),
  priceKobo: dish.priceKobo,
  available: dish.available && dish.portionsLeft > 0,
});

export function createMcpServer(deps: { menu: MenuService }) {
  const server = new McpServer({ name: "mama-put", version: "1.0.0" });

  server.registerTool(
    "search_menu",
    {
      title: "Search Mama Put's menu",
      description:
        "Lists dishes on Mama Put's menu today, with prices. Use this first whenever someone asks what's " +
        "available, what something costs, or wants a dish by name. 'search' matches part of a dish name " +
        "(for example 'rice'). Leave it out to see the whole menu. Returns at most 20 dishes.",
      inputSchema: {
        search: z.string().trim().min(1).max(50).optional().describe("Part of a dish name, like 'jollof' or 'rice'"),
        onlyAvailable: z.boolean().default(true).describe("If true, leave out dishes that have finished for today"),
      },
      outputSchema: { dishes: z.array(DishSummary) },
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async ({ search, onlyAvailable }) => {
      const page = await deps.menu.list({ limit: 20, search, available: onlyAvailable ? true : undefined });
      const dishes = page.items.map(summary);
      return {
        structuredContent: { dishes },
        content: [{ type: "text", text: JSON.stringify({ dishes }) }],
      };
    },
  );

  return server;
}
```

Piece by piece:

1. **`registerTool(name, definition, handler)`**. The name is what the model calls: short, `snake_case`, a verb. The definition is what the model reads. The handler is our code.
2. **`inputSchema`** is a set of zod fields. The SDK turns it into JSON Schema for the model to read, and **validates every call against it** before our handler runs. A model that sends `search: 42` gets an error and never reaches our code. Each `.describe()` is a hint the model sees for that field.
3. **`outputSchema` and `structuredContent`**: the result as typed data, which clients and models can rely on. `content` carries the same thing as text, for clients that only show text. Send both.
4. **`annotations`**: hints for the host. `readOnlyHint: true` says "this changes nothing", so a host may let the model call it without asking the person each time. `openWorldHint: false` says it only touches our own system. They are hints, not security: a host may ignore them, and our server must be safe whatever the host does.
5. **The handler calls `deps.menu.list`**, the same menu service with lesson 19's cache in front of it. This is the fifth door into the same kitchen.

`available` in the summary combines `available` and `portionsLeft > 0`. The model doesn't need to know our two columns; it needs to know whether Bayo can have it. Shape results around the question.

## Step 3: errors the model can use
<!-- bite: 0adc3a20-7c37-4503-8ec5-5e8dbad31708 -->

Our services throw `AppError`s. For a tool, an error is part of the conversation: the model should *see* it and recover. MCP has a way to say "the tool ran, and this is a failure": `isError: true` in the result.

`src/mcp/results.ts`:

```ts
import { AppError } from "../shared/errors.ts";

export function toolError(text: string) {
  return { isError: true, content: [{ type: "text" as const, text }] };
}

export async function safely<T extends object>(work: () => Promise<T>, hint = "") {
  try {
    return await work();
  } catch (err) {
    if (err instanceof AppError) return toolError(`${err.message}${hint ? ` ${hint}` : ""}`);
    console.error("mcp tool failed", err);
    return toolError("Something went wrong on Mama Put's side. Try again in a moment.");
  }
}
```

The same split as lesson 7: our own errors in plain words; anything unexpected hidden, and logged in full on our side. A model must never see a stack trace or a SQL error: everything it sees may be repeated to the person, or worse, acted on.

The second tool, using it:

```ts
server.registerTool(
  "get_dish",
  {
    title: "Get one dish",
    description:
      "Gets one dish by its id, including whether it's available now. Use search_menu first to find the id.",
    inputSchema: { dishId: z.string().regex(/^\d{1,18}$/).describe("The dish id from search_menu, like '1'") },
    outputSchema: { dish: DishSummary.extend({ photoUrl: z.string().nullable() }) },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  async ({ dishId }) =>
    safely(async () => {
      const dish = await deps.menu.get(dishId);
      const result = { dish: { ...summary(dish), photoUrl: dish.photo ? `${deps.publicUrl}/photos/${dish.photo}` : null } };
      return { structuredContent: result, content: [{ type: "text" as const, text: JSON.stringify(result) }] };
    }, "Use search_menu to find dish ids."),
);
```

Ask for dish 99 and the model reads: "Dish 99 was not found. Use search_menu to find dish ids." It calls `search_menu` next, which is exactly what we want.

## Step 4: a resource and a prompt
<!-- bite: 43afd05c-fd0c-4f61-91ad-8a0be832906f -->

**A resource** is information the person or the app can attach, rather than something the model decides to call. Today's whole menu is a good one: someone can say "use Mama Put's menu" and the host attaches it.

```ts
server.registerResource(
  "todays-menu",
  "mamaput://menu/today",
  {
    title: "Today's menu at Mama Put",
    description: "Every dish on the menu today, with prices and whether it's still available.",
    mimeType: "application/json",
  },
  async (uri) => {
    const page = await deps.menu.list({ limit: 50 });
    return {
      contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify(page.items.map(summary)) }],
    };
  },
);
```

`mamaput://menu/today` is a URI we invent. It names the resource; it isn't a web address anyone fetches. (Resources can also be templates, like `mamaput://dishes/{id}`, which the SDK supports with a `ResourceTemplate`.)

**A prompt** is a ready-made request the person picks from a menu in the host. It saves them writing it, and tells the model how to use our tools well:

```ts
server.registerPrompt(
  "plan_lunch",
  {
    title: "Plan lunch at Mama Put",
    description: "Suggests a lunch from today's menu within a budget.",
    argsSchema: { budgetNaira: z.string().regex(/^\d{1,6}$/).describe("Most you want to spend, in naira, like '3000'") },
  },
  ({ budgetNaira }) => ({
    messages: [
      {
        role: "user",
        content: {
          type: "text",
          text:
            `Use the search_menu tool to see what's available at Mama Put today, then suggest a lunch ` +
            `for one person that costs at most ₦${budgetNaira}. Show the price of each item and the total.`,
        },
      },
    ],
  }),
);
```

Prompt arguments always arrive as strings in MCP, which is why the budget is a `z.string()` with a pattern rather than a number.

## Step 5: serving it over Streamable HTTP
<!-- bite: 4abae9d7-e340-48df-9ac0-a18cded607d5 -->

An MCP server can run as a program on the person's own computer (stdio), or over HTTP. Mama Put is a web backend, so HTTP, on the same Express app, at one URL: `/mcp`.

**Streamable HTTP** is simple at heart: the client POSTs a JSON-RPC message to `/mcp`; the server answers either with a plain JSON response or, when it has several things to send, with a stream of events (the SSE format from lesson 20). The SDK handles all of that.

We'll run it **stateless**: no session kept between requests. Every POST gets a fresh server object and transport, used once and thrown away. Stateless means any of our servers can answer any request, with nothing to share between them, which is exactly how the rest of our API already works.

`src/mcp/mcp.routes.ts`:

```ts
import express from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createMcpServer } from "./server.ts";
import type { AppDeps } from "../app.ts";

export function createMcpRouter(deps: AppDeps) {
  const router = express.Router();

  router.post("/", async (req, res) => {
    const server = createMcpServer({ menu: deps.services.menu, publicUrl: deps.publicUrl });
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });

    res.on("close", () => {
      transport.close();
      server.close();
    });

    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  });

  // Stateless: no server-initiated streams, no sessions to end.
  const notAllowed = (_req: express.Request, res: express.Response) => {
    res.set("Allow", "POST").status(405).json({
      jsonrpc: "2.0",
      error: { code: -32000, message: "Method not allowed." },
      id: null,
    });
  };
  router.get("/", notAllowed);
  router.delete("/", notAllowed);

  return router;
}
```

and in `app.ts`, after `express.json()`:

```ts
app.use("/mcp", mcpLimit, createMcpRouter(deps));
```

1. **`sessionIdGenerator: undefined`** turns sessions off. That's the stateless mode.
2. **`res.on("close")`** cleans up when the response ends. Every open needs a close, as in lesson 20.
3. **`req.body`** is passed in because `express.json()` has already read the body. The transport would otherwise try to read it again.
4. **GET and DELETE answer 405.** In stateful mode, GET opens a stream for the server to send messages at any time, and DELETE ends a session. We have neither.
5. **`mcpLimit`** is a rate limit of its own (lesson 19's Redis store). An AI in a loop can call tools far faster than a person taps buttons.

It's outside `/v1` and `/v2`. MCP has its own versioning: client and server agree a protocol version in their first message.

**One security check the spec insists on.** A web page in Bayo's browser could try to send requests to an MCP server running on his own computer, using a trick called DNS rebinding. Servers must check the `Origin` header on incoming requests and refuse origins they don't expect. Our server lives on the internet, not on Bayo's laptop, and lesson 14's CORS settings already refuse unknown browser origins. But if you ever run an MCP server locally on HTTP, bind it to `127.0.0.1`, and turn on the transport's DNS-rebinding protection (the SDK has options for allowed hosts and origins; see its README).

## Step 6: trying it
<!-- bite: 622574bb-ec20-4361-8373-a48d43f76fd9 -->

**With curl**, to see that it's really just JSON-RPC over HTTP. First message of any MCP conversation is `initialize`:

```bash
curl -s http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

The answer (possibly in SSE format, `event: message` then `data: {...}`) names the server and what it supports. Then list the tools:

```bash
curl -s http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

and call one:

```bash
curl -s http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_menu","arguments":{"search":"rice"}}}'
```

The `Accept` header must list both types: that's the client saying "I can read a plain answer or a stream".

**With the MCP Inspector**, which is much nicer:

```bash
npx @modelcontextprotocol/inspector
```

It opens in your browser. Choose the **Streamable HTTP** transport, enter `http://localhost:3000/mcp`, connect, and you'll see the tools, resources and prompt, with forms to try each. Look at the tool list as the model will see it. If a description confuses *you*, it'll confuse the model.

**With a real assistant.** For example, in Claude Code:

```bash
claude mcp add --transport http mama-put http://localhost:3000/mcp
```

Then ask: "What rice dishes does Mama Put have today, and what's cheapest?" Watch it call `search_menu` with `search: "rice"`, read the prices, and answer. Other assistants have a settings page for adding an MCP server by URL; the address is the same.

(For an assistant running on someone else's computer to reach your laptop, you'd need a tunnel, like Paystack's webhooks in lesson 17.)

## Step 7: testing without a network
<!-- bite: 6494f700-f686-434c-949d-532321cea3de -->

The SDK comes with a client, and an **in-memory transport** that connects a client and a server directly, no HTTP at all. That makes fast tests:

```ts
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";

async function connect(menu: MenuService) {
  const server = createMcpServer({ menu, publicUrl: "https://test.example" });
  const client = new Client({ name: "test", version: "0" });
  const [clientSide, serverSide] = InMemoryTransport.createLinkedPair();
  await Promise.all([server.connect(serverSide), client.connect(clientSide)]);
  return client;
}

it("search_menu finds rice dishes and gives prices in naira and kobo", async () => {
  const client = await connect(fakeMenuWith([{ id: "1", name: "Jollof rice", priceKobo: 150000 }]));
  const result = await client.callTool({ name: "search_menu", arguments: { search: "rice" } });
  assert.deepEqual(result.structuredContent, {
    dishes: [{ id: "1", name: "Jollof rice", price: "₦1,500", priceKobo: 150000, available: true }],
  });
});

it("get_dish for a missing dish is an error the model can act on", async () => {
  const client = await connect(fakeMenuWith([]));
  const result = await client.callTool({ name: "get_dish", arguments: { dishId: "99" } });
  assert.equal(result.isError, true);
  assert.match(JSON.stringify(result.content), /search_menu/);
});
```

Also test: the tool list (names, and that every tool has a description and annotations, so nobody adds a tool carelessly); a bad input (`dishId: "abc"`) is refused before the handler; and one HTTP test with supertest that POSTs `tools/list` to `/mcp` with the right `Accept` header, to check the Express wiring.

And a different kind of test, by hand: give a real model the tool list and ten questions a customer might ask. Does it pick the right tool with the right arguments? If not, the description needs work. This is how you test the "reader is a model" part, and it's worth doing whenever you change a description.

## The TypeScript in this lesson
<!-- bite: 352da552-900b-462f-b3b9-7be9733fca51 -->

1. **`import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js"`**: The SDK is split into many entry points, so you import from a path inside the package. The `.js` ending is part of the package's own path, even though we're writing TypeScript.
2. **`inputSchema: { search: z.string()..., onlyAvailable: z.boolean()... }`**: A plain object of zod schemas (sometimes called a "raw shape"), not a `z.object(...)`. The SDK builds the object schema itself, and gives the handler its argument already typed: `{ search?: string; onlyAvailable: boolean }`.
3. **`.describe("...")`**: Attaches a description to a schema. It ends up in the JSON Schema the model reads.
4. **`.default(true)`**: If the model leaves the field out, it becomes `true`, so the handler's type says `boolean`, not `boolean | undefined`.
5. **`DishSummary.extend({ photoUrl: ... })`**: Makes a new zod object with all of `DishSummary`'s fields plus more. No copying.
6. **`type: "text" as const`**: The SDK's result type wants exactly the word `"text"`, not any string. `as const` keeps it exact. (Inside `registerTool`'s handler the SDK works this out itself; in a helper function like `toolError`, it needs the hint.)
7. **`safely<T extends object>(work: () => Promise<T>, hint = "")`**: A generic helper: `T` is whatever the work returns, and `extends object` says it must be an object. `hint = ""` is a default parameter.
8. **`(kobo / 100).toLocaleString("en-NG")`**: Formats a number the Nigerian way, with commas: `1500` becomes `"1,500"`.
9. **`const [clientSide, serverSide] = InMemoryTransport.createLinkedPair()`**: The function returns two transports in an array; array destructuring names both in one line.
10. **`Promise.all([server.connect(...), client.connect(...)])`**: Both sides must connect at the same time, since each waits for the other. Starting both and waiting for both is how you do that.

## Your project so far
<!-- bite: db49beaf-f936-4667-9db0-d112f5b9b5ec -->

```text
mama-put-api/
├── package.json                  ← NEW: @modelcontextprotocol/sdk
└── src/
    ├── app.ts                    ← /mcp mounted after express.json, with its own rate limit
    ├── mcp/
    │   ├── server.ts             ← NEW: createMcpServer: search_menu, get_dish, todays-menu, plan_lunch
    │   ├── results.ts            ← NEW: toolError, safely (AppError → isError, everything else hidden)
    │   ├── mcp.routes.ts         ← NEW: stateless Streamable HTTP on POST /mcp; GET/DELETE → 405
    │   └── mcp.test.ts           ← NEW: in-memory client tests, tool list checks, one HTTP test
    ├── shared/
    │   └── rate-limits.ts        ← NEW: mcpLimit
    └── grpc/ · graphql/ · kitchen/ · jobs/ · payments/ · orders/ · menu/ · auth/ · webhooks/ · admin/ · docs/ · db/
```

## Common mistakes
<!-- bite: 2f13afcd-1dfc-4405-9a88-c1820a5aa5fd -->

1. **One tool per endpoint.** The model drowns in choices. Shape tools around what people want to do.
2. **Descriptions for programmers.** "GET menu with filters." The model needs to know *when* to use it and what the inputs mean.
3. **Huge results.** Every byte goes into the model's context. Return what answers the question.
4. **Throwing raw errors.** Stack traces and SQL text reach the model, and maybe the person. Return `isError` with plain words and a next step.
5. **Business rules in tool handlers.** Then MCP disagrees with REST. Call the services.
6. **Trusting annotations as security.** `readOnlyHint` is a hint to the host. The server must be safe whatever the host does.
7. **No rate limit.** An AI in a loop calls tools very fast.
8. **Stateful sessions you don't need.** They tie a client to one server. Stateless is simpler and scales like the rest of the API.
9. **Testing only the code, never the descriptions.** Ask a real model real questions and see which tools it picks.

## Check your understanding
<!-- bite: 19178b3b-1145-4d53-981a-b05c7634abd8 -->

1. What's the difference between a tool and a resource, and who decides to use each?
2. Why not make one MCP tool for every REST route?
3. A model calls `search_menu` with `{ "search": 42 }`. What happens, and where?
4. Why does `get_dish`'s "not found" error mention `search_menu`?
5. What does "stateless" mean for our MCP endpoint, and why choose it?
6. `search_menu` has `readOnlyHint: true`. Does that stop it from changing anything?

<details>
<summary>Answers, after your attempt</summary>

1. A tool is a function the *model* decides to call during a conversation. A resource is information, named by a URI, that the *person or the application* chooses to attach as context. Tools act or look things up; resources are read.
2. Because the reader is a language model choosing on the spot from names and descriptions. Dozens of route-shaped tools make it guess between near-duplicates. A few tools shaped around what people want are easier to choose correctly, and each can use several services inside.
3. The SDK validates the arguments against the tool's input schema before our handler runs, finds that `search` should be a string, and returns an error to the client. Our code never sees it.
4. Because the model reads tool errors and decides what to do next. Telling it how to recover (find the id with `search_menu`) makes its next call likely to be right.
5. Every POST to `/mcp` gets a brand-new server and transport, used once and thrown away; nothing is remembered between requests. So any of our servers can answer any request with nothing shared, just like the REST API.
6. No. It's a hint that tells the host it *may* let the model call the tool without asking each time. What makes the tool safe is our code: it only calls read-only service methods.

</details>

## Practice
<!-- bite: 892ece7b-0551-4de9-9a66-dc31facb2025 -->

1. Add a `ResourceTemplate` resource, `mamaput://dishes/{id}`, returning one dish.
2. Add a `menu_categories` tool if your menu has categories, or a `cheapest_dishes` tool, and decide honestly whether it's worth being a separate tool or belongs as an option on `search_menu`.
3. Write a check that runs in the tests: every registered tool has a title, a description of at least 40 characters, an `outputSchema`, and annotations.
4. Connect the MCP Inspector and a real assistant. Ask five different menu questions; write down which tools it called. Improve one description based on what you saw.
5. Write the tests from step 7, plus the supertest one for `/mcp`.

**Done when** the Inspector lists two tools, one resource and one prompt; an assistant answers "what's the cheapest rice dish at Mama Put?" correctly from real data; a bad dish id comes back as a tool error that leads the model to `search_menu`; the in-memory tests pass with no server running; and `GET /mcp` answers 405.

## Before moving on
<!-- bite: b0fae365-cdac-4646-a27f-1e9c0efe9165 -->

Mama Put is now readable by any AI assistant that speaks MCP. Bayo can ask "what's cheap today?" and get a true answer from our menu, through the same services as every other door.

But Bayo doesn't just want to *read*. He wants "order me two plates of jollof". That means the assistant must act **as Bayo**: logged in as him, with only his permissions. And it means an AI is about to spend someone's money. What if it misunderstood? What if a dish description it read contained hidden instructions? What if it calls `place_order` fifty times in a loop? Each of those has a real answer, and they're the next lesson: MCP in production.

## Related
<!-- bite: 3e77ecb7-c553-4c6a-a9cc-5ae549aa508d -->

- [[backend/frameworks/express/24-mcp-in-production|Next: MCP in Production]]
- [[backend/frameworks/express/06-validation|Input Validation]] — input schemas are validation at the door, again
- [[backend/frameworks/express/07-errors|Errors and Structured Responses]] — the same split between our errors and hidden ones
- [[ai-engineering/index|AI Engineering]] — how the assistants on the other side use tools

## About this lesson
<!-- bite: 5c040b8a-56a4-4b8f-a9a3-8cda82746eb7 -->

**Level:** Intermediate → Advanced. Lesson 23 of [[backend/frameworks/express/index|Express]]. Covers what MCP is and the host, client and server roles, tools, resources and prompts, why MCP tools are designed for a language model rather than a programmer, building a server with the TypeScript SDK's `McpServer`, `registerTool` with zod input and output schemas, descriptions, structured content and annotations, tool errors with `isError` that tell the model what to do next, a resource and a prompt, serving it statelessly over Streamable HTTP from Express with a fresh server and transport per request, rate limits, origin checks and DNS rebinding, trying it with curl, the MCP Inspector and a real assistant, and testing with the SDK's client and in-memory transport.
