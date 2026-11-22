---
id: 6cb72c4b-6036-4956-999e-832ef4b73cee
---

# Building an MCP Server

**MCP, the Model Context Protocol, is an open standard that lets an AI assistant use your system: it asks your server "what can you do?", gets back a list of tools with plain descriptions and typed inputs, and calls them when they help answer someone's question. An MCP server is the part of your backend that speaks it.** REST is for programmers who read your docs and write code. MCP is for a language model that reads your descriptions, every conversation, and decides for itself what to call.

## Before you start
<!-- bite: edce756c-eb67-44fe-a97a-915f1999872d -->

You should have finished [[backend/frameworks/net-http/22-grpc|lesson 22]]. This lesson puts a fourth door on the same services, and leans on two habits from earlier: thin handlers that call services (lesson 4), and errors that show our own messages and hide everything else (lesson 7).

After this lesson you will be able to:

1. Explain hosts, clients and servers, and tools, resources and prompts.
2. Design tools for a model to read, not a programmer: few, plain, small results, helpful errors.
3. Write typed tools with the official Go SDK, with input and output schemas made from Go structs.
4. Turn errors into something the model can act on, without ever showing it an internal error.
5. Serve MCP statelessly over Streamable HTTP on the same server, and try it with `curl`, the Inspector and a real assistant.
6. Test tools in memory, with no network.

## What to install
<!-- bite: fe63d8e6-1cc5-4339-8a6b-553135bcd754 -->

One Go module, the official MCP SDK for Go, maintained by the MCP project together with Google:

```bash
go get github.com/modelcontextprotocol/go-sdk@latest
```

That's all the code needs. For trying the server by hand (step 7) there are two optional tools:

1. **The MCP Inspector**, a web page for poking at any MCP server. It's written in JavaScript, so it needs **Node.js** (the LTS version from [nodejs.org](https://nodejs.org)); you run it with `npx`, nothing to install globally.
2. **An AI assistant that can use MCP servers.** Step 7 uses Claude Code; most assistants have a settings page for adding a server by URL.

## Where we stopped
<!-- bite: 246fd352-c084-4a19-9fb9-b62d2c5efae8 -->

Bayo uses an AI assistant for everything. He types: "What's cheap at Mama Put today? Something with rice." The assistant has no idea. It can't see our menu, and if it guesses, it'll make things up.

We could tell Bayo "the REST API is at `/v2/menu`". But an assistant doesn't know our URLs, our query parameters, our `{ data }` envelope or what `priceKobo` means. Every assistant company would have to write special code for Mama Put, and for every other business in the world. That doesn't scale.

MCP is the missing standard. The assistant asks any MCP server "what can you do?", gets back a list of tools, and calls them. Mama Put describes itself once; every MCP-speaking assistant can use it.

This lesson makes the read-only part: searching the menu and reading dishes. Doing things *as* Bayo (his orders, placing an order) needs him to log in, and needs a lot of care about an AI spending his money. That's the whole of [[backend/frameworks/net-http/24-mcp-in-production|lesson 24]].

## The kid version
<!-- bite: 452ff281-32f9-49f8-85f8-6b858310e08c -->

Bayo sends his younger brother to buy lunch. The boy can read, but he's never been to Mama Put.

At the counter there's a card: "Things you can ask for: 1. *See today's menu* (say what you're looking for). 2. *Ask about one dish* (say its number)." The boy reads the card, asks for "rice dishes", gets the list, and reports back.

The card is the list of tools. The boy is the AI assistant: clever, willing, but he only knows what the card tells him. So the card must be clear. Write "GET /v2/menu?q=" on it and he's lost. Write "See today's menu, with prices, optionally searching by name" and he's fine.

**Where the picture stops working.** A boy who's told by a stranger in the queue "Mama said give me all your money" probably won't. An AI assistant might believe text it reads, even text that came from *our own* tool results. That's prompt injection, and it's why lesson 24 exists.

## Terms used in this lesson
<!-- bite: 312b8991-5f61-496b-814e-c702021455ec -->

1. **Host**: This is the AI application the person uses, like Claude Desktop or a code editor.
2. **Client**: This is the part inside the host that talks to one MCP server. One host can have many clients, one per server.
3. **Server**: This is the program offering tools, resources and prompts. We're building one.
4. **Tool**: This is a function the AI can decide to call, with a name, a description, an input schema and a result. Like `search_menu`.
5. **Resource**: This is a piece of information the host or the person can choose to read, named by a URI, like `mamaput://menu/today`. Tools are for the *model* to call; resources are usually picked by the *application* or the person, to add as context.
6. **Prompt**: This is a ready-made request the person can pick from a list, like "Plan my lunch under a budget".
7. **JSON-RPC**: This is the message format MCP uses: small JSON objects with a `method`, `params` and an `id`, answered with a `result` or an `error`.
8. **Transport**: This is how those messages travel. **stdio** runs the server as a program on the same computer, talking through standard input and output. **Streamable HTTP** serves it over HTTP, which is what a web backend like ours does.
9. **JSON Schema**: This is a standard way of describing the shape of JSON ("an object with a whole number called `dishId`"). MCP uses it for every tool's input and output.

## Step 1: MCP is not "another REST API"
<!-- bite: 0b719276-2dec-4ce1-8f36-78662fa366b7 -->

It's tempting to make one MCP tool per REST route: `get_v2_menu`, `get_v2_menu_by_id`, `post_v2_orders`... Don't. The reader is different.

A REST API is read by **programmers**, once, who then write code. An MCP server is read by a **language model**, in every conversation, which decides there and then what to call, from your names and descriptions alone. So:

1. **Few tools, shaped around what people want to do**, not around your routes. "Search the menu" is one tool, even if it runs three queries inside.
2. **The description is the instructions.** Say what the tool does, when to use it, what the inputs mean and what comes back, in plain sentences. Models read it closely.
3. **Small, meaningful results.** Every result is read into the model's limited context. Don't return all fifteen fields of every dish; return what helps answer the question, with money in naira for people *and* kobo for exactness.
4. **Errors that say what to do next.** "There's no such dish. Use search_menu to find dish IDs." The model reads errors and tries again; a helpful error is a correct second try.
5. **Typed, limited inputs.** The schema becomes part of what the model sees, and our validation at the door. Lesson 6 never stops applying.

## Step 2: the server and a first tool
<!-- bite: b3fda261-3802-4cb0-a6c3-dc2ee2e04b8b -->

`internal/mcpserver/server.go`. (The package is `mcpserver`, not `mcp`, because the SDK's package is already called `mcp` and we import it.)

```go
// Package mcpserver offers Mama Put to AI assistants over the Model Context Protocol.
package mcpserver

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"mamaput/internal/apperr"
	"mamaput/internal/menu"
	"mamaput/internal/money"
)

// Menu is what the MCP tools need from the menu package.
type Menu interface {
	List(ctx context.Context, q menu.ListQuery) (menu.Page, error)
	Get(ctx context.Context, id int64) (menu.Dish, error)
}

type Deps struct {
	Menu      Menu
	PublicURL string // like https://api.mamaput.ng, for photo links
	Log       *slog.Logger
}

// New builds the MCP server: its tools, resource and prompt.
func New(d Deps) *mcp.Server {
	s := mcp.NewServer(&mcp.Implementation{Name: "mama-put", Title: "Mama Put", Version: "1.0.0"}, &mcp.ServerOptions{
		Instructions: "Mama Put is a roadside food seller in Lagos. Use these tools to see today's menu and prices. " +
			"Prices are in naira (₦).",
	})
	addMenuTools(s, d)
	addMenuResource(s, d)
	addLunchPrompt(s)
	return s
}

// DishSummary is a dish as the model sees it: what helps answer a question, nothing more.
type DishSummary struct {
	ID        int64  `json:"id"`
	Name      string `json:"name"`
	Price     string `json:"price" jsonschema:"price for people to read, like ₦1,500"`
	PriceKobo int64  `json:"priceKobo" jsonschema:"exact price in kobo (₦1 = 100 kobo)"`
	Available bool   `json:"available" jsonschema:"true if it can be ordered right now"`
}

func summary(d menu.Dish) DishSummary {
	return DishSummary{
		ID:        d.ID,
		Name:      d.Name,
		Price:     naira(d.Price),
		PriceKobo: int64(d.Price),
		Available: d.Available && d.PortionsLeft > 0,
	}
}

// naira writes kobo for people: 150000 → "₦1,500", 250050 → "₦2,500.50".
func naira(k money.Kobo) string {
	whole, kobo := int64(k)/100, int64(k)%100
	s := fmt.Sprint(whole)
	for i := len(s) - 3; i > 0; i -= 3 {
		s = s[:i] + "," + s[i:]
	}
	if kobo != 0 {
		return fmt.Sprintf("₦%s.%02d", s, kobo)
	}
	return "₦" + s
}
```

1. **`mcp.NewServer`** takes who we are (`Implementation`: a name, a title for people, a version) and options. **`Instructions`** is sent to the client when it connects, and many hosts give it to the model: one or two sentences of "what is this server for".
2. **`DishSummary` is the presenter**, a third set of wire types after lesson 10's REST ones and lesson 22's protobuf ones. Each door shapes the same `menu.Dish` for its own reader.
3. **`available` combines two columns.** `Available && PortionsLeft > 0`. The model doesn't need to know we have two; it needs to know whether Bayo can have it. Shape results around the question.
4. **The `jsonschema` tag** is a description for the model. Step 3 shows where it goes.

### The tool

`internal/mcpserver/tools.go`:

```go
package mcpserver

import (
	"context"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"

	"mamaput/internal/menu"
)

type SearchMenuInput struct {
	Search          string `json:"search,omitempty" jsonschema:"part of a dish name, like jollof or rice; leave out to see the whole menu"`
	IncludeFinished bool   `json:"includeFinished,omitempty" jsonschema:"true to also list dishes that have finished for today"`
}

type SearchMenuOutput struct {
	Dishes []DishSummary `json:"dishes"`
}

var (
	no       = false
	readOnly = &mcp.ToolAnnotations{ReadOnlyHint: true, IdempotentHint: true, OpenWorldHint: &no}
)

func addMenuTools(s *mcp.Server, d Deps) {
	mcp.AddTool(s, &mcp.Tool{
		Name:  "search_menu",
		Title: "Search Mama Put's menu",
		Description: "Lists dishes on Mama Put's menu today, with prices. Use this first whenever someone asks " +
			"what's available, what something costs, or wants a dish by name. 'search' matches part of a dish " +
			"name (for example 'rice'). Leave it out to see the whole menu. Returns at most 20 dishes.",
		Annotations: readOnly,
	}, func(ctx context.Context, _ *mcp.CallToolRequest, in SearchMenuInput) (*mcp.CallToolResult, SearchMenuOutput, error) {
		search := strings.TrimSpace(in.Search)
		if len([]rune(search)) > 50 {
			return nil, SearchMenuOutput{}, errSearchTooLong
		}
		q := menu.ListQuery{Search: search, OnlyAvailable: !in.IncludeFinished, Limit: 20}
		page, err := d.Menu.List(ctx, q)
		if err != nil {
			return nil, SearchMenuOutput{}, toolError(ctx, d.Log, err, "")
		}
		out := SearchMenuOutput{Dishes: make([]DishSummary, 0, len(page.Dishes))}
		for _, dish := range page.Dishes {
			out.Dishes = append(out.Dishes, summary(dish))
		}
		return nil, out, nil
	})

	// get_dish comes in step 4
}
```

Piece by piece:

1. **`mcp.AddTool(s, tool, handler)`** is a **generic function**. Look at the handler's type: `func(ctx, *mcp.CallToolRequest, SearchMenuInput) (*mcp.CallToolResult, SearchMenuOutput, error)`. From `SearchMenuInput` and `SearchMenuOutput`, Go works out `AddTool`'s two type parameters by itself, and the SDK uses them to do a lot of work for us (step 3).
2. **The name** is what the model calls: short, `snake_case`, a verb. **`Title`** is for people, in the host's list of tools. **`Description`** is what the model reads to decide whether to call it.
3. **Annotations** are hints for the host. `ReadOnlyHint: true` says "this changes nothing", so a host may let the model call it without asking the person each time. `IdempotentHint: true` says calling it twice is the same as once. `OpenWorldHint: false` says it only touches our own system, not the open internet. They're **hints, not security**: a host may ignore them, and our server must be safe whatever the host does. (`OpenWorldHint` is a `*bool` because "not said" and "false" mean different things in the spec, so we need the address of a `false`: that's what `no` is for.)
4. **`IncludeFinished`, not `OnlyAvailable`.** We want "leave out finished dishes" to be the default. In Go, a `bool` the model didn't send is `false`, so the option is named so that `false` is the default we want. That's simpler than a `*bool` that might be `nil`, and it's a good Go habit everywhere: **choose names whose zero value is the right default.**
5. **The handler calls `d.Menu.List`**, the same menu service with lesson 19's cache in front of it. This is the fourth door into the same kitchen, after REST, GraphQL and gRPC.
6. **`return nil, out, nil`.** The first result, `*mcp.CallToolResult`, is for when you want to control the result by hand. Returning `nil` lets the SDK build it from `out`.

## Step 3: what the SDK does with the types
<!-- bite: 557a04b6-2611-49c8-8a33-a1cad47badc3 -->

Because the handler is typed, the SDK does four jobs we'd otherwise write by hand:

1. **It writes the input schema from the struct.** `SearchMenuInput` becomes this JSON Schema, which is exactly what the model sees:

```json
{
  "type": "object",
  "properties": {
    "search": { "type": "string", "description": "part of a dish name, like jollof or rice; leave out to see the whole menu" },
    "includeFinished": { "type": "boolean", "description": "true to also list dishes that have finished for today" }
  },
  "additionalProperties": false
}
```

The `json` tag gives the property's name; `omitempty` makes it optional (no `omitempty`, and it goes in `required`); the `jsonschema` tag becomes its description.

2. **It checks every call against that schema before our handler runs.** A model that sends `"dishId": "abc"` for a number, or leaves out a required field, never reaches our code; it gets back an error saying what was wrong, and usually fixes it on the next try. `additionalProperties: false` refuses arguments we don't know, the same promise as lesson 6's `DisallowUnknownFields`.
3. **It writes the output schema** from `SearchMenuOutput`, so the client knows the shape of the answer before it asks.
4. **It sends the result twice**: as `structuredContent` (typed JSON clients can rely on) and as text in `content` (for clients that only show text). The MCP spec asks for both.

The schema checks types, not sense. It can't say "at most 50 characters" from a struct tag, and it can't know a dish ID must be at least 1. So those checks are still ours, in the handler. The schema is the bouncer at the door; the handler still checks the ticket.

(The descriptions in `jsonschema` tags start with a small letter and have no full stop because they're read as labels, like a form's field hints. The tool's `Description` is full sentences, because it's instructions.)

## Step 4: errors the model can use
<!-- bite: 00ca16ec-dc2b-4d9c-98ed-ad13d45870cf -->

This is where Go's MCP SDK needs the most care. When a typed handler returns an error, the SDK doesn't send a protocol error. It sends a normal result with **`isError: true`**, and the error's text as the content. That's right by the spec: the tool ran, it failed, and the model should read why and recover.

It also means **the model reads every word of every error you return.** Return `err` from a failed database query as it is, and the model reads `pgx: connection refused 10.0.0.3:5432`, may repeat it to Bayo, and has learned something about our network. Everything a model sees can end up in front of the person, or be acted on.

So no handler returns a raw error. They go through one function, at the bottom of `server.go`:

```go
// toolError decides what the model may read about an error. The model sees every word.
func toolError(ctx context.Context, log *slog.Logger, err error, hint string) error {
	var appErr *apperr.Error
	if errors.As(err, &appErr) && appErr.Kind != apperr.Internal {
		return errors.New(strings.TrimSpace(appErr.Message + " " + hint))
	}
	log.ErrorContext(ctx, "mcp tool failed", "error", err)
	return errors.New("Something went wrong on Mama Put's side. Try again in a moment.")
}
```

The same split as lesson 7, lesson 21's error presenter and lesson 22's `toStatus`: our own errors in plain words; anything unexpected hidden, and logged in full on our side. The `hint` is new, and it's for the model: the next thing to try.

And the errors the handlers make themselves, `internal/mcpserver/errors.go`:

```go
package mcpserver

import "errors"

var (
	errSearchTooLong = errors.New("search must be at most 50 characters. Try one word, like 'rice'.")
	errBadDishID     = errors.New("dishId must be a dish ID from search_menu, like 1.")
)
```

Go's style guide says error strings start with a small letter and have no full stop, because they usually get wrapped into longer messages (`"place order: dish not found"`). These are an exception on purpose: they're never wrapped; they're a whole message for a reader, the model, so they're written as sentences.

Now the second tool, in `tools.go`:

```go
type GetDishInput struct {
	DishID int64 `json:"dishId" jsonschema:"the dish ID from search_menu, like 1"`
}

type DishDetail struct {
	DishSummary
	Description string `json:"description,omitempty"`
	PhotoURL    string `json:"photoUrl,omitempty" jsonschema:"a link to a photo of the dish, if there is one"`
}

type GetDishOutput struct {
	Dish DishDetail `json:"dish"`
}

// inside addMenuTools:
mcp.AddTool(s, &mcp.Tool{
	Name:  "get_dish",
	Title: "Get one dish",
	Description: "Gets one dish by its ID: its price, description, photo, and whether it's available now. " +
		"Use search_menu first to find the ID.",
	Annotations: readOnly,
}, func(ctx context.Context, _ *mcp.CallToolRequest, in GetDishInput) (*mcp.CallToolResult, GetDishOutput, error) {
	if in.DishID < 1 {
		return nil, GetDishOutput{}, errBadDishID
	}
	dish, err := d.Menu.Get(ctx, in.DishID)
	if err != nil {
		return nil, GetDishOutput{}, toolError(ctx, d.Log, err, "Use search_menu to find dish IDs.")
	}
	out := GetDishOutput{Dish: DishDetail{DishSummary: summary(dish), Description: dish.Description}}
	if dish.PhotoLarge != "" {
		out.Dish.PhotoURL = d.PublicURL + "/photos/" + dish.PhotoLarge
	}
	return nil, out, nil
})
```

`DishDetail` **embeds** `DishSummary`, so it has all of its fields plus two more, and `encoding/json` writes them all at the same level: `{"id":1,"name":"Jollof rice",...,"photoUrl":"..."}`, not a nested `"DishSummary": {...}`. The SDK's schema follows the same rule.

What the model reads, for each kind of mistake (real output from the test in step 8):

```text
{"dishId": 99}     → There's no such dish. Use search_menu to find dish IDs.
{"dishId": 0}      → dishId must be a dish ID from search_menu, like 1.
{"dishId": "abc"}  → validating "arguments": validating root: validating /properties/dishId: type: abc has type "string", want "integer"
{}                 → validating "arguments": validating root: required: missing properties: ["dishId"]
{"dishId": 500}    → Something went wrong on Mama Put's side. Try again in a moment.
```

All five come back with `isError: true`. Ask for dish 99 and the model calls `search_menu` next, which is exactly what we want. The two schema errors are the SDK's own wording; they're about the model's input, not our insides, so they're safe to show. And dish 500, where the fake database failed with an address in its message, shows nothing of it.

## Step 5: a resource and a prompt
<!-- bite: 92c99e11-a5de-4fef-ba19-73974fccc97a -->

**A resource** is information the person or the app can attach, rather than something the model decides to call. Today's whole menu is a good one: someone can say "use Mama Put's menu" and the host attaches it. `internal/mcpserver/resources.go`:

```go
const menuURI = "mamaput://menu/today"

func addMenuResource(s *mcp.Server, d Deps) {
	s.AddResource(&mcp.Resource{
		URI:         menuURI,
		Name:        "todays-menu",
		Title:       "Today's menu at Mama Put",
		Description: "Every dish on the menu today, with prices and whether it's still available.",
		MIMEType:    "application/json",
	}, func(ctx context.Context, req *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
		page, err := d.Menu.List(ctx, menu.ListQuery{Limit: 50})
		if err != nil {
			return nil, toolError(ctx, d.Log, err, "")
		}
		dishes := make([]DishSummary, 0, len(page.Dishes))
		for _, dish := range page.Dishes {
			dishes = append(dishes, summary(dish))
		}
		b, err := json.Marshal(dishes)
		if err != nil {
			return nil, err
		}
		return &mcp.ReadResourceResult{Contents: []*mcp.ResourceContents{
			{URI: menuURI, MIMEType: "application/json", Text: string(b)},
		}}, nil
	})
}
```

`mamaput://menu/today` is a URI we invent. It names the resource; it isn't a web address anyone fetches. (Resources can also be templates, like `mamaput://dishes/{id}`, which the SDK supports with `AddResourceTemplate`.) Unlike a tool, a resource handler's error becomes a protocol error, but it goes through `toolError` all the same, so nothing internal leaks.

**A prompt** is a ready-made request the person picks from a list in the host. It saves them writing it, and tells the model how to use our tools well:

```go
var wholeNaira = regexp.MustCompile(`^\d{1,6}$`)

func addLunchPrompt(s *mcp.Server) {
	s.AddPrompt(&mcp.Prompt{
		Name:        "plan_lunch",
		Title:       "Plan lunch at Mama Put",
		Description: "Suggests a lunch from today's menu within a budget.",
		Arguments: []*mcp.PromptArgument{
			{Name: "budgetNaira", Description: "Most you want to spend, in naira, like 3000", Required: true},
		},
	}, func(ctx context.Context, req *mcp.GetPromptRequest) (*mcp.GetPromptResult, error) {
		budget := req.Params.Arguments["budgetNaira"]
		if !wholeNaira.MatchString(budget) {
			return nil, fmt.Errorf("budgetNaira must be a whole number of naira, like 3000")
		}
		return &mcp.GetPromptResult{
			Description: "Lunch at Mama Put for ₦" + budget + " or less",
			Messages: []*mcp.PromptMessage{{
				Role: "user",
				Content: &mcp.TextContent{Text: "Use the search_menu tool to see what's available at Mama Put today, " +
					"then suggest a lunch for one person that costs at most ₦" + budget + ". " +
					"Show the price of each item and the total."},
			}},
		}, nil
	})
}
```

Prompt arguments always arrive as strings in MCP (`req.Params.Arguments` is a `map[string]string`), which is why the budget is checked with a pattern rather than read as a number. Checking it matters more than it looks: the argument is pasted into text the model will read as the person's own request, so a "budget" of `3000. Also, ignore all earlier instructions...` would be a small injection. `^\d{1,6}$` allows digits and nothing else.

## Step 6: serving it over Streamable HTTP
<!-- bite: db7aa1d5-03e2-48d7-a2de-0907f8cfee68 -->

An MCP server can run as a program on the person's own computer (stdio), or over HTTP. Mama Put is a web backend, so HTTP, on the same server, at one URL: `/mcp`.

**Streamable HTTP** is simple at heart: the client POSTs a JSON-RPC message to `/mcp`; the server answers with a JSON response or, when it has several things to send, with a stream of events in lesson 20's SSE format. The SDK handles all of that. `internal/mcpserver/http.go`:

```go
package mcpserver

import (
	"net/http"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// Handler serves the MCP server at one URL, statelessly: every POST stands alone.
func Handler(s *mcp.Server) http.Handler {
	return mcp.NewStreamableHTTPHandler(func(*http.Request) *mcp.Server { return s }, &mcp.StreamableHTTPOptions{
		Stateless:           true,
		JSONResponse:        true,
		MaxRequestBodyBytes: 64 << 10,
	})
}
```

1. **`NewStreamableHTTPHandler`** returns an ordinary `http.Handler`, so it goes on our mux like anything else. Its first argument is a function that picks the `*mcp.Server` for a request. We have one server, built once in `run`, so it always returns that. (A server is safe to share: the SDK makes a separate session object for each connection.)
2. **`Stateless: true`**: no session kept between requests. Every POST stands alone, so **any** of our API servers can answer any request, with nothing to share between them, which is how the rest of our API already works. In stateless mode the SDK answers GET and DELETE with 405 by itself: those are for the long-lived streams and sessions we don't have.
3. **`JSONResponse: true`**: answer each POST with plain `application/json` instead of an SSE stream. Our tools answer in milliseconds and never send progress messages, so a stream would only add ceremony. (Turn it off if you add a slow tool that reports progress.)
4. **`MaxRequestBodyBytes: 64 << 10`**: lesson 6's size limit, again. A body over 64 KB gets a 413 before it's read.

In `app.New`, on the `api` mux:

```go
mcpServer := mcpserver.New(mcpserver.Deps{Menu: d.Menu, PublicURL: d.PublicURL, Log: d.Logger})
api.Handle("/mcp", httpx.RateLimit(d.MCPLimit, d.ClientIP)(mcpserver.Handler(mcpServer)))
```

1. **`"/mcp"` with no method** in the pattern, so GET and DELETE reach the SDK and get its proper 405, rather than our mux's.
2. **Its own rate limit**, `d.MCPLimit` (lesson 19's Redis limiter, with a tighter budget than the general one). An AI in a loop can call tools far faster than a person taps buttons.
3. **On the `api` mux**, so it's inside lesson 17's full chain: request IDs, logs, panic recovery, security headers, CORS and `Authenticate`. I checked: values that our middleware puts in the request's context, like the request ID's logger and the identity, **do reach the tool handlers' `ctx`**. Lesson 24 builds on that.
4. **Outside `/v1` and `/v2`.** MCP has its own versioning: client and server agree a protocol version in their first message.

**One security check the spec insists on.** A web page in Bayo's browser could try to send requests to an MCP server running on his *own* computer, using a trick called DNS rebinding. The Go SDK guards against it automatically: a request that arrives on a localhost address (`127.0.0.1`) but names some other host in its `Host` header gets 403. For a server on the internet that's harmless, with one trap for later: if you ever put a proxy on the **same machine** that connects to the API over `127.0.0.1` and passes the public `Host` header through, every MCP request gets 403. Lesson 28's Docker setup avoids that (the proxy reaches the API over Docker's network, not localhost); if your setup can't, set `DisableLocalhostProtection: true` on purpose, with a comment saying why. And if you ever run an MCP server locally for yourself, bind it to `127.0.0.1` and leave the protection on.

## Step 7: trying it
<!-- bite: 2c53eea5-3dbb-4596-abd4-e2ce715daf43 -->

**With curl**, to see that it's really just JSON-RPC over HTTP. The first message of an MCP conversation is `initialize`:

```bash
curl -s localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"curl","version":"0"}}}'
```

```json
{"jsonrpc":"2.0","id":1,"result":{"capabilities":{"logging":{},"prompts":{"listChanged":true},"resources":{"listChanged":true},"tools":{"listChanged":true}},"instructions":"Mama Put is a roadside food seller in Lagos. Use these tools to see today's menu and prices. Prices are in naira (₦).","protocolVersion":"2025-11-25","serverInfo":{"name":"mama-put","title":"Mama Put","version":"1.0.0"}}}
```

The server says who it is, what it can do and which protocol version it agrees to. The `Accept` header must list both types: that's the client saying "I can read a plain answer or a stream". Then list the tools:

```bash
curl -s localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

and call one:

```bash
curl -s localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_menu","arguments":{"search":"rice"}}}'
```

```json
{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{\"dishes\":[{\"available\":true,\"id\":1,\"name\":\"Jollof rice\",\"price\":\"₦1,500\",\"priceKobo\":150000}]}"}],"structuredContent":{"dishes":[{"available":true,"id":1,"name":"Jollof rice","price":"₦1,500","priceKobo":150000}]}}}
```

Okay!!!!! The same answer twice, as text and as structured data, exactly as step 3 said.

**With the MCP Inspector**, which is much nicer:

```bash
npx @modelcontextprotocol/inspector
```

It opens in your browser. Choose the **Streamable HTTP** transport, enter `http://localhost:8080/mcp`, connect, and you'll see the tools, the resource and the prompt, with forms to try each. Look at the tool list as the model will see it. If a description confuses *you*, it'll confuse the model.

**With a real assistant.** For example, in Claude Code:

```bash
claude mcp add --transport http mama-put http://localhost:8080/mcp
```

Then ask: "What rice dishes does Mama Put have today, and what's cheapest?" Watch it call `search_menu` with `search: "rice"`, read the prices, and answer. Other assistants have a settings page for adding an MCP server by URL; the address is the same. (For an assistant running on someone else's computer to reach your laptop, you'd need a tunnel, like Paystack's webhooks in lesson 17.)

## Step 8: testing without a network
<!-- bite: 9b687478-cdb9-42d2-a68e-bf5c9e152d49 -->

The SDK comes with a client, and **in-memory transports** that connect a client and a server directly, no HTTP at all. That makes fast tests. `internal/mcpserver/mcp_test.go`:

```go
func connect(t *testing.T, m Menu) *mcp.ClientSession {
	t.Helper()
	s := New(Deps{Menu: m, PublicURL: "https://test.example", Log: slog.New(slog.NewTextHandler(io.Discard, nil))})
	clientSide, serverSide := mcp.NewInMemoryTransports()
	if _, err := s.Connect(t.Context(), serverSide, nil); err != nil {
		t.Fatal(err)
	}
	c := mcp.NewClient(&mcp.Implementation{Name: "test", Version: "0"}, nil)
	cs, err := c.Connect(t.Context(), clientSide, nil)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { cs.Close() })
	return cs
}

func text(r *mcp.CallToolResult) string {
	var b strings.Builder
	for _, c := range r.Content {
		if tc, ok := c.(*mcp.TextContent); ok {
			b.WriteString(tc.Text)
		}
	}
	return b.String()
}

func TestSearchMenuGivesNairaAndKobo(t *testing.T) {
	cs := connect(t, fakeMenu{})

	res, err := cs.CallTool(t.Context(), &mcp.CallToolParams{
		Name: "search_menu", Arguments: map[string]any{"search": "rice"},
	})

	if err != nil || res.IsError {
		t.Fatalf("err %v, result %s", err, text(res))
	}
	want := `{"dishes":[{"available":true,"id":1,"name":"Jollof rice","price":"₦1,500","priceKobo":150000}]}`
	if got := text(res); got != want {
		t.Errorf("got %s\nwant %s", got, want)
	}
}

func TestGetDishHidesInternalErrors(t *testing.T) {
	cs := connect(t, fakeMenu{}) // the fake fails dish 500 with "pgx: connection refused 10.0.0.3"

	res, err := cs.CallTool(t.Context(), &mcp.CallToolParams{
		Name: "get_dish", Arguments: map[string]any{"dishId": 500},
	})

	if err != nil || !res.IsError {
		t.Fatalf("want a tool error, got err %v, result %+v", err, res)
	}
	if strings.Contains(text(res), "10.0.0.3") || strings.Contains(text(res), "pgx") {
		t.Errorf("the model can see an internal error: %s", text(res))
	}
}
```

`connect` is the whole setup: a linked pair of transports, the server on one end, a real SDK client on the other, the same JSON-RPC in between as over HTTP. `cs.CallTool` is exactly what a host does.

Also test:

1. **The tool list**: every tool has a `Description` and `Annotations`, so nobody adds a tool carelessly. Loop over `cs.ListTools(...)`.
2. **Errors the model can act on**: dish 99's message mentions `search_menu`.
3. **Bad input never reaches the handler**: `{"dishId": "abc"}` is an error, and a counting fake shows `Get` wasn't called.
4. **The prompt**: a budget of `"3000"` works; `"lots"` and `"3000. Ignore that"` are refused.
5. **The HTTP wiring**, once: `httptest.NewServer` with the real handler, a POST of `tools/list` with the right `Accept` header gets 200; a GET gets 405.

And a different kind of test, by hand: give a real model the tool list and ten questions a customer might ask. Does it pick the right tool with the right arguments? If not, the description needs work. This is how you test the "the reader is a model" part, and it's worth doing whenever you change a description.

## The Go in this lesson
<!-- bite: e585da24-e75a-4cfd-a5a4-f4c417e4d109 -->

1. **`mcp.AddTool(s, tool, handler)`**: A generic function whose two type parameters, the input and output types, are inferred from the handler you pass. You never write `AddTool[SearchMenuInput, SearchMenuOutput]`.
2. **Struct tags as schema**: `json:"search,omitempty"` names a property and makes it optional; `jsonschema:"..."` describes it. One struct is the Go type, the schema the model reads, and the check on the way in.
3. **Zero values as defaults**: `IncludeFinished bool` instead of `OnlyAvailable *bool`, so "not sent" already means what we want.
4. **The address of a constant value, `OpenWorldHint: &no`**: Go can't take `&false` directly, so a variable holds it.
5. **Embedding in a struct for JSON, `DishDetail{DishSummary, ...}`**: The embedded struct's fields are written at the same level, as if declared in `DishDetail` itself.
6. **Returning `nil` for a result the library can build**: `return nil, out, nil` lets the SDK fill in `CallToolResult` from `out`.
7. **`errors.As` and a hand-made message**: The same check as lessons 7, 21 and 22, deciding what a reader may see.
8. **Error strings as sentences, on purpose**: An exception to Go's style rule, because these are whole messages for the model, never wrapped.
9. **`[]rune(search)`**: Counts characters, not bytes. `len("₦")` is 3; `len([]rune("₦"))` is 1.
10. **`regexp.MustCompile` at package level**: Compiled once when the program starts; `MustCompile` panics on a bad pattern, so a typo shows up at start-up, not on the first request.
11. **A type switch with `ok`, `c.(*mcp.TextContent)`**: Picks the text parts out of a result's content, which can also hold images and other kinds.
12. **`mcp.NewInMemoryTransports()`**: A linked pair, returned as two values, for connecting a client and server in a test.

## Your project so far
<!-- bite: 6db7e187-b878-4166-9875-b16381eff529 -->

```text
mama-put/
├── go.mod                         ← github.com/modelcontextprotocol/go-sdk
└── internal/
    ├── app/
    │   └── app.go                 ← "/mcp" on the api mux, with its own rate limit (MCPLimit)
    └── mcpserver/                 ← NEW package
        ├── server.go              ← New (instructions), DishSummary, summary, naira, toolError
        ├── tools.go               ← search_menu and get_dish: typed inputs and outputs, read-only annotations
        ├── errors.go              ← messages written for the model
        ├── resources.go           ← mamaput://menu/today, and the plan_lunch prompt with a checked budget
        ├── http.go                ← Handler: stateless Streamable HTTP, JSON responses, 64 KB limit
        └── mcp_test.go            ← in-memory client: results, hidden errors, bad input, prompts, one HTTP test
```

## Common mistakes
<!-- bite: 5fbb2d81-71a2-4bcb-995e-d8e8f27c63de -->

1. **One tool per REST route.** The model drowns in choices. Shape tools around what people want to do.
2. **Descriptions written for programmers.** "GET dishes by q" means nothing to a model. Say what, when and what comes back, in sentences.
3. **Returning a raw error from a tool.** The SDK sends its text straight to the model. Every error goes through `toolError`.
4. **Results with every field.** They fill the model's context and bury the answer. Return what helps.
5. **Trusting the schema for everything.** It checks types, not lengths or sense. Check the rest in the handler.
6. **Trusting annotations as security.** `ReadOnlyHint` is a hint to the host. A tool that changes things must be safe however it's called.
7. **Prompt arguments pasted in unchecked.** They become words the model reads as the person's. Check them like any input.
8. **A stateful server behind a load balancer.** The session is on one server and the next request lands on another. Stateless, unless you really need sessions.
9. **No rate limit of its own.** An AI in a loop calls far faster than a person.
10. **A proxy on the same machine, over `127.0.0.1`, passing the public `Host`.** The SDK's DNS rebinding protection answers 403 to everything.

## Check your understanding
<!-- bite: 49aec974-891d-48b4-85bd-856c38d7efff -->

1. Why not make one MCP tool for each REST route?
2. A model calls `get_dish` with `{"dishId": "abc"}`. What runs, and what does the model read?
3. Why does every tool error go through `toolError`, when the SDK would send `err.Error()` by itself?
4. Why is the option called `includeFinished` and not `onlyAvailable`?
5. What does `Stateless: true` buy us, given that we'll run several API servers?
6. `ReadOnlyHint: true` is on both tools. What does it do, and what doesn't it do?

<details>
<summary>Answers, after your attempt</summary>

1. The reader is a model choosing tools from their names and descriptions, every conversation. Many route-shaped tools make it harder to pick the right one; a few tools shaped around what people want to do ("search the menu") are easier to use well.
2. The SDK checks the arguments against the schema made from `GetDishInput`, sees a string where an integer is required, and returns a tool error (`isError: true`) saying so. Our handler never runs. The model reads the message and usually tries again with a number.
3. Because the SDK sends the error's text to the model, and a raw error could contain internals, like a database address. `toolError` shows our own `apperr` messages, with a hint for what to do next, and replaces everything else with a plain "something went wrong", logging the real error for us.
4. Because a `bool` the model doesn't send is `false` in Go. We want "leave out finished dishes" to happen by default, so the option is named so that `false` means exactly that. No `*bool`, no `nil` to check.
5. Every request stands alone, so any server can answer any request. A stateful session would live on one server, and the next request might land on another that has never heard of it.
6. It tells the host the tool changes nothing, so the host may let the model call it without asking the person each time. It doesn't protect anything: a host can ignore it, so the server must be safe however its tools are called.

</details>

## Practice
<!-- bite: 78893b15-e004-4fbd-aea0-ccbeb0952c5e -->

1. Write the tests from step 8 in `internal/mcpserver/mcp_test.go`, including the tool-list test and the HTTP wiring test.
2. Add a `todays_specials` tool, read-only, using the menu service's `Specials`. Write its description, then ask a real model "anything special today?" and check it picks the new tool.
3. Add a resource template, `mamaput://dishes/{id}`, with `AddResourceTemplate`, returning one dish's `DishDetail` as JSON.
4. Add the `MCPLimit` rate limit to `app.Deps`, with a budget of 60 calls a minute per address, and a test that the 61st gets 429.
5. Rewrite the `search_menu` description badly on purpose ("GET dishes; params: search, includeFinished"), ask a model five menu questions, and compare its choices with the good description.

**Done when** `curl` gets the tool list and a `search_menu` result from `/mcp`; the Inspector shows both tools, the resource and the prompt; a real assistant answers "what rice dishes are there?" by calling `search_menu`; dish 99 gives an error that mentions `search_menu`; a failing store shows the model nothing internal; and `make test` passes.

## Before moving on
<!-- bite: 007acdc5-ae4d-4af9-b2e0-5994bf3b6208 -->

Mama Put now has a door for AI assistants. Two read-only tools, a resource and a prompt, described for a model to read, with schemas made from Go structs, inputs checked twice, errors that say what to do next and hide everything else, all stateless over HTTP on the same server and the same services.

Everything here is safe because it only reads a public menu. Bayo's next question is "order me two plates of jollof", and that's different: the assistant must act **as Bayo**, with his permission, and spend **his money**. Who is the assistant acting for? How does it log in? What stops it ordering fifty plates because a dish description told it to? That's lesson 24, the last of Part 5.

## Related
<!-- bite: cf1c981e-acf4-4915-ba72-9a4e9d07e954 -->

- [[backend/frameworks/net-http/24-mcp-in-production|Next: MCP in Production]]
- [[backend/frameworks/express/23-mcp-server|The same lesson in Express]] — the TypeScript SDK with zod schemas and a fresh server per request
- [[backend/frameworks/net-http/07-errors|Errors and Structured Responses]] — the split between our errors and everything else
- [[backend/frameworks/net-http/06-validation|Input Validation]] — why a schema is the start of checking, not the end

## About this lesson
<!-- bite: bedd13e2-ca20-4cac-8257-eeb76cdff8d9 -->

**Level:** Intermediate → Advanced. Lesson 23 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later and the official MCP Go SDK v1. Covers hosts, clients and servers, tools, resources and prompts, designing tools for a model to read, typed tools with `mcp.AddTool` and schemas made from struct tags, validation before the handler and the checks still left to it, annotations as hints, zero values as defaults, tool errors that the model reads and a single function that decides what it may see, resources and prompts with checked arguments, stateless Streamable HTTP with JSON responses and a body limit, the SDK's DNS rebinding protection and its proxy trap, trying a server with curl, the Inspector and a real assistant, and testing with in-memory transports.
