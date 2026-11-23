---
id: 7369539c-f497-41e8-b962-4c2f2f2dec15
---

# Building an MCP Server

**The Model Context Protocol (MCP) is a standard way for an AI assistant to find out what a service can do and then use it: it asks the service for its list of tools, reads what each one is for, and calls the ones that help answer the person's question.** An MCP server is a program that offers those tools. Mama Put describes itself once, and every assistant that speaks MCP (Claude, code editors, and others) can look at its menu, without anyone writing special code for Mama Put. In Rust, the official library is **rmcp**.

## Before you start
<!-- bite: dab5e14e-2a5f-4057-b8ad-5b2c88a84e3c -->

You should have:

1. Finished [[backend/frameworks/axum/22-grpc|lesson 22]], so `cargo test` runs 79 tests.
2. An AI app that can connect to an MCP server over HTTP, if you want to try it by hand. Not required: the tests use an MCP client.

After this lesson you will be able to:

1. Explain what MCP is for, and why an MCP server isn't one tool per REST route.
2. Write tools with rmcp's macros, whose names, descriptions and schemas the model reads.
3. Shape results and errors for a language model: small, plain, and saying what to do next.
4. Offer a resource and a prompt as well as tools.
5. Serve MCP over Streamable HTTP, inside the Axum app, safely.
6. Test it with a real MCP client.

## What to install
<!-- bite: d4775636-7795-4f66-9a70-8960578da158 -->

```bash
cargo add rmcp --features server,macros,transport-streamable-http-server
cargo add schemars
cargo add --dev rmcp --features client,transport-streamable-http-client-reqwest
```

1. **`rmcp`** is the official Rust library for MCP. `server` and `macros` give the server side and the `#[tool]` macros; `transport-streamable-http-server` serves it over HTTP, as a Tower service Axum can mount.
2. **`schemars`** writes JSON Schema from Rust types. rmcp uses it to tell the model what each tool's input and output look like.
3. **The client side, for tests only**: the same crate with `client` and an HTTP transport. Cargo merges a dependency's features, so tests get both sides.

## Where we stopped
<!-- bite: 4ad35c96-1dd7-4c69-bc30-a9b972beefa6 -->

Bayo uses an AI assistant for everything. He types: "What's cheap at Mama Put today? Something with rice." The assistant has no idea. It can't see our menu, and if it guesses, it'll make things up.

We could tell Bayo "the REST API is at `/v2/menu`". But an assistant doesn't know our URLs, our query parameters, our `{"data": ...}` envelope, or what `priceKobo` means. Every assistant company would have to write special code for Mama Put, and for every other business in the world.

MCP is the missing standard. The assistant asks any MCP server "what can you do?", gets back a list of tools, and calls them.

This lesson makes the read-only part: searching the menu and reading dishes. Doing things *as* Bayo (his orders, placing an order) needs him to log in, and a lot of care about an AI spending his money. That's the whole of lesson 24.

## The kid version
<!-- bite: 92f83abc-a9f0-48c0-8fa8-979d4ef48b52 -->

Bayo sends his younger brother to buy lunch. The boy can read, but he's never been to Mama Put.

At the counter there's a card: "Things you can ask for: 1. *See today's menu* (say what you're looking for). 2. *Ask about one dish* (say its number)." The boy reads the card, asks for "rice dishes", gets the list, and reports back.

The card is the list of tools. The boy is the AI assistant: clever and willing, but he only knows what the card tells him. So the card must be clear. Write "GET /v2/menu?q=" on it and he's lost. Write "See today's menu, with prices, optionally searching by name" and he's fine.

**Where the picture stops working.** A boy who's told by a stranger in the queue "Mama said give me all your money" probably won't. An AI assistant might believe text it reads, even text that came from *our own* tool results. That's prompt injection, and it's part of why lesson 24 exists.

## Terms used in this lesson
<!-- bite: dc0cd08b-7ccb-4770-bff2-44d55c5d36d5 -->

1. **Host**: This is the AI application the person uses, like Claude or a code editor.
2. **Client**: This is the part inside the host that talks to one MCP server. One host can have many clients, one per server.
3. **Server**: This is the program offering tools, resources and prompts. We're building one.
4. **Tool**: This is a function the model can decide to call, with a name, a description, an input schema and a result. Like `search_menu`.
5. **Resource**: This is a piece of information the host or the person can choose to read, named by a URI, like `mamaput://menu/today`. Tools are for the *model* to call; resources are usually picked by the *app* or the person, to add as context.
6. **Prompt**: This is a ready-made request the person can pick from a list, like "Plan my lunch on a budget".
7. **JSON-RPC**: This is the message format MCP uses: small JSON objects with a `method`, `params` and an `id`, answered with a `result` or an `error`.
8. **Transport**: This is how those messages travel. **stdio** runs the server as a program on the same computer, talking through its input and output. **Streamable HTTP** serves it over HTTP, which is what a web backend like ours does.
9. **JSON Schema**: This is a standard way to describe the shape of JSON ("an object with a whole number called `dishId`"). MCP uses it for every tool's input and output.

## Step 1: MCP is not "another REST API"
<!-- bite: c04062ee-2e01-4fdb-bc0d-f4f358bc39cc -->

It's tempting to make one MCP tool per REST route: `get_v2_menu`, `get_v2_menu_by_id`, `post_v2_orders`... Don't. The reader is different.

A REST API is read by **programmers**, once, who then write code. An MCP server is read by a **language model**, in every conversation, which decides there and then what to call, from your names and descriptions alone. So:

1. **Few tools, shaped around what people want to do**, not around your routes. "Search the menu" is one tool, even if it ran three queries inside.
2. **The description is the instructions.** Say what the tool does, when to use it, what the inputs mean and what comes back, in plain sentences. Models read it closely.
3. **Small, meaningful results.** Every result goes into the model's limited memory for the conversation. Don't return all nine fields of every dish; return what helps answer the question, with money as people write it *and* in kobo for exact sums.
4. **Errors that say what to do next.** "There's no dish 999. Use search_menu to find dish ids." The model reads errors and tries again; a helpful error is a correct second try.
5. **Typed, limited inputs.** The schema is part of what the model sees, and our checks at the door. Lesson 6 never stops applying.

## Step 2: the server
<!-- bite: 83b66fdb-16ba-43fc-abbf-fdcd7f12b449 -->

`src/mcp/mod.rs` starts:

```rust
//! Mama Put for AI assistants, over the Model Context Protocol: a few tools shaped around what people
//! ask, a resource and a prompt, at `/mcp`. Read-only for now; acting as a customer is lesson 24.

mod tools;

use std::sync::Arc;

use rmcp::{
    ErrorData, RoleServer, ServerHandler,
    handler::server::router::{prompt::PromptRouter, tool::ToolRouter},
    model::{
        Implementation, ListResourcesResult, PaginatedRequestParams, ReadResourceRequestParams, ReadResourceResponse,
        ReadResourceResult, Resource, ResourceContents, ServerCapabilities, ServerConfig,
    },
    prompt_handler,
    service::RequestContext,
    tool_handler,
    transport::streamable_http_server::{StreamableHttpServerConfig, StreamableHttpService, session::local::LocalSessionManager},
};

pub use tools::{DishDetail, DishSummary, SearchMenu, SearchMenuOutput};

use crate::menu::{DishFilter, MenuService};

/// The MCP server: what an AI assistant can find out about Mama Put.
#[derive(Clone)]
pub struct MamaPut {
    menu: MenuService,
    tool_router: ToolRouter<Self>,
    prompt_router: PromptRouter<Self>,
}

impl MamaPut {
    pub fn new(menu: MenuService) -> Self {
        MamaPut { menu, tool_router: Self::tool_router(), prompt_router: Self::prompt_router() }
    }
}
```

`MamaPut` holds the `MenuService` (the same one REST, GraphQL and gRPC use, with lesson 19's cache) and two routers that the macros in step 3 fill in. It's `Clone`, because the HTTP server makes one for every request.

It becomes an MCP server by implementing rmcp's `ServerHandler` trait:

```rust
#[tool_handler(router = self.tool_router)]
#[prompt_handler(router = self.prompt_router)]
impl ServerHandler for MamaPut {
    fn get_info(&self) -> ServerConfig {
        ServerConfig::new(ServerCapabilities::builder().enable_tools().enable_prompts().enable_resources().build())
            .with_server_info(Implementation::from_build_env())
            // Sent when an assistant connects; many give it to the model.
            .with_instructions(
                "Mama Put is a food seller in Lagos. Use these tools to see today's menu and prices. \
                 Prices are in naira (₦). You can't place orders through this server yet.",
            )
    }
```

1. **`#[tool_handler]` and `#[prompt_handler]`** write the trait's `list_tools`, `call_tool`, `list_prompts` and `get_prompt` for us, from the routers.
2. **`get_info`** is what the server says about itself when an assistant connects: which features it has (tools, prompts, resources), its name and version (`from_build_env` reads them from `Cargo.toml`), and **instructions**: one or two sentences that many hosts give the model, saying what this server is for. Saying "you can't place orders yet" there stops the model promising Bayo something it can't do.

## Step 3: the tools
<!-- bite: bea3982f-60e3-4126-b9a5-a08153e22faf -->

`src/mcp/tools.rs`, the inputs and outputs first:

```rust
//! The tools, and the prompt. Written for a language model: few, plain, and shaped around questions.

use rmcp::{
    Json,
    handler::server::wrapper::Parameters,
    model::{PromptMessage, Role},
    prompt, prompt_router, tool, tool_router,
};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

use super::MamaPut;
use crate::{
    http::ApiError,
    menu::{Dish, DishFilter, MenuError},
};

/// A dish on Mama Put's menu.
// What helps answer a question, nothing more. Doc comments go into the schema the model reads; this one doesn't.
#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "camelCase")]
pub struct DishSummary {
    pub id: i64,
    pub name: String,
    /// The price for people, like "₦1,500.00".
    pub price: String,
    /// The same price in kobo (₦1 is 100), for exact sums.
    pub price_kobo: i64,
    /// Whether it can be ordered now: on the menu, and not finished.
    pub available: bool,
    pub special: bool,
}

impl From<Dish> for DishSummary {
    fn from(d: Dish) -> Self {
        DishSummary {
            id: d.id,
            name: d.name,
            price: format!("₦{}", d.price.naira_text()),
            price_kobo: d.price.0,
            available: d.available && d.portions_left > 0,
            special: d.special,
        }
    }
}

#[derive(Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct SearchMenu {
    /// Part of a dish's name, like "jollof" or "rice". Leave out to see the whole menu.
    #[serde(default)]
    pub search: Option<String>,
    /// True to also list dishes that have finished for today.
    #[serde(default)]
    pub include_finished: bool,
}

#[derive(Serialize, JsonSchema)]
pub struct SearchMenuOutput {
    pub dishes: Vec<DishSummary>,
    /// True if more dishes matched than are listed here: search with a word to narrow it down.
    pub more: bool,
}

#[derive(Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct GetDish {
    /// The dish's id, from search_menu.
    pub dish_id: i64,
}

#[derive(Serialize, JsonSchema)]
#[serde(rename_all = "camelCase")]
pub struct DishDetail {
    #[serde(flatten)]
    pub dish: DishSummary,
    /// Plates left today.
    pub portions_left: i32,
    /// A link to its photo, if it has one.
    pub photo_url: Option<String>,
}

#[derive(Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct PlanLunch {
    /// How much the person wants to spend, in naira, like 3000.
    pub budget_naira: i64,
}
```

1. **`DishSummary` is the presenter**: a fourth shape for the same `Dish`, after REST's, GraphQL's and protobuf's. Each door shapes the dish for its own reader.
2. **`available` combines two columns**: on the menu, *and* plates left. The model doesn't need to know we have two; it needs to know whether Bayo can have it. Shape results around the question.
3. **Money twice**: `"₦1,500.00"` for the model to repeat to people, and `150000` in kobo for adding up a lunch exactly.
4. **`#[derive(JsonSchema)]`** turns each type into JSON Schema, and every **doc comment becomes a description** in it, which the model reads. Lesson 21 taught the same thing about GraphQL: `///` is for the reader of the API, `//` is for us.
5. **`#[serde(default)]` and `Option`** make an input optional; a plain field is required. `include_finished: bool` defaults to `false`, so "leave out finished dishes" is what happens when the model says nothing. Name options so their default is the safe, common case.
6. **`#[serde(deny_unknown_fields)]`** becomes `"additionalProperties": false` in the schema, and refuses anything extra, like lesson 6's REST bodies.

The tools themselves:

```rust
#[tool_router(vis = "pub(super)")]
impl MamaPut {
    /// See Mama Put's menu for today, with prices: the whole menu, or dishes whose name contains a word.
    /// Use this first, to answer questions like "what's cheap?" or "do they have rice?", and to find a
    /// dish's id. Dishes that have finished for today are left out unless asked for.
    #[tool(annotations(title = "Search the menu", read_only_hint = true, idempotent_hint = true, open_world_hint = false))]
    async fn search_menu(&self, Parameters(input): Parameters<SearchMenu>) -> Result<Json<SearchMenuOutput>, String> {
        if input.search.as_ref().is_some_and(|s| s.chars().count() > 50) {
            return Err("The search is too long. Use one or two words from a dish's name, like \"rice\".".into());
        }
        let filter = DishFilter {
            available: if input.include_finished { None } else { Some(true) },
            special: None,
            min_price: None,
            max_price: None,
            name_contains: input.search.filter(|s| !s.trim().is_empty()),
            sort: Vec::new(),
            limit: 20,
            offset: 0,
        };
        let (dishes, total) = self.menu.list(&filter).await.map_err(|e| tool_error(e, ""))?;
        let dishes = dishes
            .into_iter()
            .filter(|d| input.include_finished || d.portions_left > 0)
            .map(DishSummary::from)
            .collect();
        Ok(Json(SearchMenuOutput { dishes, more: total > filter.limit }))
    }

    /// Everything about one dish: its price, whether it can be ordered now, and how many plates are left.
    #[tool(annotations(title = "Look at one dish", read_only_hint = true, idempotent_hint = true, open_world_hint = false))]
    async fn get_dish(&self, Parameters(input): Parameters<GetDish>) -> Result<Json<DishDetail>, String> {
        if input.dish_id < 1 {
            return Err("A dish id is a whole number from 1. Use search_menu to find dish ids.".into());
        }
        let dish = self.menu.get(input.dish_id).await.map_err(|e| tool_error(e, "Use search_menu to find dish ids."))?;
        let (portions_left, photo_url) = (dish.portions_left, dish.photo.as_ref().map(|name| format!("/uploads/{name}")));
        Ok(Json(DishDetail { dish: dish.into(), portions_left, photo_url }))
    }
}
```

1. **`#[tool_router]` on an `impl`** collects every `#[tool]` method into the router `MamaPut::new` builds. `vis = "pub(super)"` lets `mod.rs` call `Self::tool_router()`, since the macro's function is otherwise private to this file.
2. **The method's name is the tool's name**: `search_menu`, a verb, `snake_case`. **Its doc comment is the description**: full sentences, because it's instructions. It says when to use the tool ("use this first"), not just what it does.
3. **Annotations** are hints for the host. `read_only_hint` says "this changes nothing", so a host may let the model call it without asking Bayo each time. `idempotent_hint` says calling it twice is the same as once. `open_world_hint = false` says it only touches our own system, not the wider internet. `title` is for people, in the host's list of tools.
4. **`Parameters(input): Parameters<SearchMenu>`** is like Axum's `Json`: rmcp reads the call's arguments into our type. The pattern takes the value straight out of the wrapper.
5. **`Json<SearchMenuOutput>`** sends the answer twice, as the MCP spec asks: as typed JSON (`structuredContent`), which clients can rely on, and as text, for hosts that only show text. Returning `Json<T>` also gives the tool an **output schema**, so the client knows the shape before it asks.
6. **The checks the schema can't make are ours.** The schema says `search` is text, but not "at most 50 characters", and it says `dishId` is a number, but not "at least 1". So the handler still checks.
7. **`more`, not a total.** My first version returned `total`, and a live call showed `"dishes": [], "total": 1`: the total counted a dish that had finished for today, which the list left out. A model would have reported a dish that isn't there. `more` only says whether there are more than the 20 listed.

Here is what the model sees for `search_menu`, from the server's `tools/list` (trimmed):

```json
{
  "name": "search_menu",
  "description": "See Mama Put's menu for today, with prices: the whole menu, or dishes whose name contains a word.\nUse this first, to answer questions like \"what's cheap?\" or \"do they have rice?\", and to find a\ndish's id. Dishes that have finished for today are left out unless asked for.",
  "inputSchema": {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "additionalProperties": false,
    "type": "object",
    "properties": {
      "search": {
        "description": "Part of a dish's name, like \"jollof\" or \"rice\". Leave out to see the whole menu.",
        "type": ["string", "null"],
        "default": null
      },
      "includeFinished": {
        "description": "True to also list dishes that have finished for today.",
        "type": "boolean",
        "default": false
      }
    }
  }
}
```

Every word there came from our Rust: the method name, its doc comment, the struct's fields and theirs. (The line breaks in the description are where the doc comment wrapped. Models don't mind them.)

## Step 4: errors the model can use
<!-- bite: ccba6a53-8937-41af-a076-531c1475166e -->

A tool that returns `Err(String)` doesn't fail the call. rmcp sends a normal result with **`isError: true`**, and the string as its text. That's right by the MCP spec: the tool ran, it failed, and the model should read why and try again.

It also means **the model reads every word of every error.** Return a database error as it is, and the model reads something like `pool timed out while waiting for an open connection`, may repeat it to Bayo, and has learned something about our system. Everything a model sees can end up in front of a person, or be used by someone trying to break in.

So every error goes through one function, in `tools.rs`:

```rust
/// What the model may read about an error, and what to try next. The model reads every word, and may
/// repeat it to the person, so our own errors are in plain words and anything unexpected says nothing.
pub(super) fn tool_error(err: MenuError, hint: &str) -> String {
    let err: ApiError = err.into();
    if err.code == "internal" {
        return "Something went wrong on Mama Put's side. Try again in a moment.".into();
    }
    // Our details are written to be joined into other text ("there's no dish 9"); here they're a
    // whole message, so they start with a capital and end with a full stop.
    let mut sentence: String = err.detail.chars().take(1).flat_map(char::to_uppercase).chain(err.detail.chars().skip(1)).collect();
    if !sentence.ends_with(['.', '!', '?']) {
        sentence.push('.');
    }
    format!("{sentence} {hint}").trim_end().to_owned()
}
```

The same split as lesson 7's problem details, lesson 21's `gql` and lesson 22's `status`: our own errors in plain words; anything unexpected hidden, and logged in full on our side by `ApiError::internal`. Two things are new:

1. **A hint**, for the model: the next thing to try. "Use search_menu to find dish ids."
2. **A whole sentence.** Our errors' details are written to be joined into longer text ("there's no dish 999"). Here, they're a whole message for a reader, so the first letter becomes a capital and a full stop is added. The test caught this: my first version gave the model "there's no dish 999 Use search_menu to find dish ids."

Over the wire, a call for dish 999:

```json
{"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"There's no dish 999. Use search_menu to find dish ids."}],"isError":true}}
```

And arguments of the wrong type never reach our code. rmcp reads them into `GetDish` first, and if that fails, the model gets serde's explanation:

```json
{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"failed to deserialize parameters: invalid type: string \"jollof\", expected i64"}],"isError":true}}
```

That's clear enough for a model to fix on its next try. (Go's MCP library checks arguments against the JSON Schema before the handler; rmcp relies on the Rust type, which comes to the same thing, with serde's wording.)

`ErrorData`, rmcp's other error type, is a *protocol* error: "you asked for something that doesn't exist", like an unknown resource. Use it for mistakes in how the client talks to us, and `Err(String)` for a tool that ran and failed.

## Step 5: a resource and a prompt
<!-- bite: 9151b65b-7fa3-42a4-8f8b-1c6b39a42c76 -->

**A resource** is something to read, not to call. Hosts show resources to the person, who can attach one to the conversation: "use Mama Put's menu as context". Ours is today's menu as a short Markdown list. Back in `mod.rs`, two more `ServerHandler` methods:

```rust
    async fn list_resources(
        &self,
        _request: Option<PaginatedRequestParams>,
        _context: RequestContext<RoleServer>,
    ) -> Result<ListResourcesResult, ErrorData> {
        let today = Resource::new(MENU_TODAY, "menu-today")
            .with_title("Today's menu")
            .with_description("Every dish Mama Put has today, with prices.")
            .with_mime_type("text/markdown");
        Ok(ListResourcesResult::with_all_items(vec![today]))
    }

    async fn read_resource(
        &self,
        request: ReadResourceRequestParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<ReadResourceResponse, ErrorData> {
        if request.uri != MENU_TODAY {
            return Err(ErrorData::resource_not_found(format!("there's no resource {}", request.uri), None));
        }
        let filter = DishFilter {
            available: Some(true),
            special: None,
            min_price: None,
            max_price: None,
            name_contains: None,
            sort: Vec::new(),
            limit: 100,
            offset: 0,
        };
        let (dishes, _) = self.menu.list(&filter).await.map_err(|e| ErrorData::internal_error(tools::tool_error(e, ""), None))?;
        let mut text = String::from("# Mama Put: today's menu\n\n");
        for dish in dishes.iter().filter(|d| d.portions_left > 0) {
            text.push_str(&format!("- {} (dish {}): ₦{}\n", dish.name, dish.id, dish.price.naira_text()));
        }
        Ok(ReadResourceResult::new(vec![ResourceContents::text(text, MENU_TODAY).with_mime_type("text/markdown")]).into())
    }
}
```

`list_resources` says what exists; `read_resource` reads one by its URI. `mamaput://` is our own URI scheme, a name rather than an address. An unknown URI is an `ErrorData`, because asking for it was a mistake in the request.

**A prompt** is a ready-made request the person can choose, often from a menu in the host, with blanks to fill in:

```rust
#[prompt_router(vis = "pub(super)")]
impl MamaPut {
    /// Plan a lunch from today's menu within a budget.
    #[prompt(name = "plan_lunch")]
    async fn plan_lunch(&self, Parameters(input): Parameters<PlanLunch>) -> Vec<PromptMessage> {
        let text = format!(
            "I have ₦{} for lunch from Mama Put. Use search_menu to see what's available today, \
             and suggest a meal that fits the budget. Show each dish's price and the total.",
            input.budget_naira
        );
        vec![PromptMessage::new_text(Role::User, text)]
    }
}
```

The person picks "plan_lunch", types 3000, and the host puts "I have ₦3000 for lunch from Mama Put. Use search_menu..." into the conversation as if they'd typed it. The prompt tells the model which tool to use, so the answer is built from the real menu.

## Step 6: serving it over Streamable HTTP
<!-- bite: e5509bdf-27b1-4644-9c01-260b30d6bbcf -->

The end of `mod.rs`:

```rust
pub type McpService = StreamableHttpService<MamaPut, LocalSessionManager>;

/// The MCP server as a Tower service, for `nest_service("/mcp", ...)`.
/// `allowed_hosts`: the names this server answers to. Anything else is refused, which stops a web page
/// from using DNS tricks to reach a server on someone's own computer.
pub fn service(menu: MenuService, allowed_hosts: Vec<String>) -> McpService {
    let server = MamaPut::new(menu);
    let config = StreamableHttpServerConfig::default()
        .with_legacy_session_mode(false) // every request stands alone: any copy of the app can answer it
        .with_json_response(true) // a plain JSON answer when the tool has nothing to stream
        .with_max_request_body_bytes(64 * 1024)
        .with_allowed_hosts(allowed_hosts);
    StreamableHttpService::new(move || Ok(server.clone()), Arc::new(LocalSessionManager::default()), config)
}
```

1. **`StreamableHttpService` is a Tower service**, so Axum mounts it like any other: `nest_service("/mcp", state.mcp.clone())` in `src/lib.rs`, outside `/v1` and `/v2` like GraphQL, with our request IDs, logging, security headers and timeout around it.
2. **No sessions** (`with_legacy_session_mode(false)`): every request stands alone, so any copy of the app can answer any request, and nothing has to remember a conversation between requests. The newest MCP version has removed sessions altogether.
3. **`with_json_response(true)`**: when a tool just returns an answer, it comes back as plain JSON, not as a stream of events. Easier to read, and to test with `curl`.
4. **64 KB at most per request.** No tool call needs more. rmcp checks this itself, since it reads the body without Axum's extractors.
5. **`with_allowed_hosts`**: the server refuses a request whose `Host` header isn't one of ours. This protects a server running on someone's own computer from a trick called **DNS rebinding**, where a web page makes the browser think `evil.example` is `127.0.0.1`, and then talks to the local server as if it were the page's own. rmcp allows only `localhost` names by default, which would also refuse our real domain, so `main` adds the host from `PUBLIC_URL`:

```rust
    // The names the MCP server answers to: this machine, and wherever the public finds us.
    let public_url: reqwest::Url = env("PUBLIC_URL")?.parse()?;
    let mut mcp_hosts = vec!["localhost".to_string(), "127.0.0.1".to_string()];
    mcp_hosts.extend(public_url.host_str().map(str::to_owned));
    let mcp = mcp::service(menu.clone(), mcp_hosts);
```

and `AppState` gains `mcp: mcp::McpService`. With the wrong host:

```bash
curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/mcp -H 'Host: evil.example' \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/list"}'
```

```text
403
```

## Step 7: trying it
<!-- bite: 6e47607c-3df7-4170-83d3-431eaa7386ee -->

**With curl**, to see the protocol itself. Each request is one JSON-RPC message; the `Accept` header says we can take plain JSON or a stream:

```bash
curl -s localhost:8080/mcp -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' -H 'MCP-Protocol-Version: 2025-06-18' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_menu","arguments":{"search":"beans"}}}'
```

```json
{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{\"dishes\":[{\"id\":2,\"name\":\"Beans and plantain\",\"price\":\"₦1,200.00\",\"priceKobo\":120000,\"available\":true,\"special\":false}],\"more\":false}"}],"structuredContent":{"dishes":[{"id":2,"name":"Beans and plantain","price":"₦1,200.00","priceKobo":120000,"available":true,"special":false}],"more":false},"isError":false}}
```

The same answer twice: as text in `content`, and as typed JSON in `structuredContent`.

**With an AI app**: add an MCP server with the URL `http://localhost:8080/mcp` in its settings (each app has its own place for this), and ask "what rice dishes does Mama Put have today?". Watch it call `search_menu` with `{"search": "rice"}`, and answer from the result. Then ask about a dish that doesn't exist, and watch it read the error and call `search_menu` next, as the hint said.

## Step 8: testing
<!-- bite: 81c30c6b-56ac-4cb9-aff7-bef29bab5147 -->

`tests/mcp.rs` tests the server exactly as an assistant uses it: rmcp's own **client**, over HTTP, to the whole app on a free port.

```rust
/// Runs the whole app on a free port, and connects an MCP client to its `/mcp`.
async fn assistant(app: &TestApp) -> RunningService<RoleClient, ()> {
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let url = format!("http://{}/mcp", listener.local_addr().unwrap());
    let router = app.router.clone();
    tokio::spawn(async move { axum::serve(listener, router).await.unwrap() });
    ().serve(StreamableHttpClientTransport::from_uri(url)).await.unwrap()
}

/// Calls a tool. Returns its structured answer, or the error text the model would read.
async fn call(client: &RunningService<RoleClient, ()>, tool: &str, arguments: Value) -> Result<Value, String> {
    let arguments = arguments.as_object().unwrap().clone();
    let result = client.call_tool(CallToolRequestParams::new(tool.to_owned()).with_arguments(arguments)).await.unwrap();
    if result.is_error == Some(true) {
        let ContentBlock::Text(text) = &result.content[0] else { panic!("an error is text") };
        return Err(text.text.clone());
    }
    Ok(result.structured_content.unwrap())
}
```

`().serve(transport)` starts a client. `()` is the "do nothing special" client handler: rmcp implements its `ClientHandler` trait for the empty tuple, so a test needs no client code of its own. `call` returns the structured answer, or the exact error text the model would read. Four tests:

1. `an_assistant_finds_the_tools_and_their_descriptions`: exactly two tools; `search_menu`'s description and annotation, and its `search` field's description in the schema.
2. `searching_and_reading_a_dish`: "rice" finds jollof but not the fried rice that's finished, unless `includeFinished`; `get_dish` gives the plates left.
3. `errors_tell_the_model_what_to_do_next`, below.
4. `a_resource_and_a_prompt`: today's menu as Markdown, and `plan_lunch` with a budget.

```rust
#[sqlx::test]
async fn errors_tell_the_model_what_to_do_next(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let client = assistant(&app).await;

    let missing = call(&client, "get_dish", json!({"dishId": 999})).await.unwrap_err();
    assert_eq!(missing, "There's no dish 999. Use search_menu to find dish ids.");
    let long = call(&client, "search_menu", json!({"search": "x".repeat(51)})).await.unwrap_err();
    assert!(long.starts_with("The search is too long"), "{long}");

    // A wrong type never reaches our code: the arguments can't be read into `GetDish`, and the model
    // is told why, in serde's words.
    let wrong = call(&client, "get_dish", json!({"dishId": "jollof"})).await.unwrap_err();
    assert!(wrong.contains("invalid type: string \"jollof\", expected i64"), "{wrong}");
    client.cancel().await.unwrap();
}
```

The error test pins the *words*, because for this reader the words are the interface.

```bash
cargo test
```

83 tests, all passing.

## The Rust in this lesson
<!-- bite: c2bf2e69-6f66-4bb8-8219-4a750ad000fb -->

1. **Attribute macros on `impl` blocks**, `#[tool_router]`, `#[prompt_router]`, and on trait impls, `#[tool_handler]`: Macros that read your methods and write more code from them: a router, and the trait methods that use it.
2. **Macro arguments**, `#[tool(annotations(read_only_hint = true))]`, `#[tool_router(vis = "pub(super)")]`: Settings passed to a macro, read when compiling.
3. **`pub(super)`**: Visible to the parent module, and no further.
4. **`#[derive(JsonSchema)]`** and doc comments: schemars writes a JSON Schema from a type, with every `///` as a description.
5. **`#[serde(flatten)]`**: A struct's fields written as if they belonged to the outer struct: `DishDetail` is a `DishSummary`'s fields plus two more, in one flat object.
6. **Patterns in parameters**, `Parameters(input): Parameters<SearchMenu>`: Takes the value out of its wrapper as the function is called.
7. **`Result<Json<T>, String>` as a tool's return type**: rmcp turns `Ok` into a result with structured content, and `Err` into a result with `isError: true`.
8. **`impl Trait for ()`**: A trait implemented for the empty tuple, as a ready-made "nothing special" value, like rmcp's client handler.
9. **Iterator adapters on characters**: `chars().take(1).flat_map(char::to_uppercase).chain(...)` capitalises the first letter correctly even when uppercasing it makes more than one character.
10. **`ends_with(['.', '!', '?'])`**: `ends_with` takes a list of characters, and is true if the text ends with any of them.

## Your project so far
<!-- bite: 866fc444-9a55-47c8-bbf7-10b73cef1e16 -->

```text
mama-put/
├── Cargo.toml                    ← rmcp (server, macros, Streamable HTTP server), schemars;
│                                   [dev-dependencies] rmcp (client, Streamable HTTP client)
├── src/
│   ├── main.rs                   ← the MCP service, with the hosts it answers to
│   ├── lib.rs                    ← /mcp, outside the versions; AppState.mcp
│   └── mcp/                      ← NEW
│       ├── mod.rs                ← MamaPut: ServerHandler (info, instructions, the menu resource); service()
│       └── tools.rs              ← search_menu, get_dish, plan_lunch; DishSummary; tool_error
└── tests/
    └── mcp.rs                    ← NEW: 4 tests with rmcp's client, over HTTP
```

## Common mistakes
<!-- bite: 860fa7c4-5534-45d3-abb6-53fd28bd2bf6 -->

1. **One tool per REST route.** The model drowns in choices. A few tools, shaped around what people ask.
2. **Descriptions written for programmers**, or not written at all. The model decides from the description. Say what it's for and when to use it.
3. **Notes for yourself in doc comments.** They go into the schema the model reads. Use `//`.
4. **Big results.** Every field costs the model's attention. Send what answers the question.
5. **Raw errors.** The model reads them and may repeat them. Go through one function, with a hint.
6. **Numbers that disagree with the list**, like a total that counts what the list leaves out. The model will report it.
7. **`ErrorData` for a tool that ran and failed.** The model can't read a protocol error as advice. Use `Err(String)`.
8. **Leaving the allowed hosts at their defaults in production**, or turning the check off. Add your real host names.
9. **Saying nothing about what the server can't do.** The model will promise it anyway. Put it in the instructions.

## Check your understanding
<!-- bite: d1c119c5-865d-482b-8c1b-691558f5abbf -->

1. Why shouldn't an MCP server have one tool per REST route?
2. Where does the model's description of `search_menu` come from, in our code?
3. A tool fails because there's no such dish. What does the model receive, and why is a hint worth adding?
4. Why does `tool_error` capitalise the first letter and add a full stop?
5. What happens when the model sends `"dishId": "jollof"`?
6. What's the difference between a tool, a resource and a prompt, and who usually picks each?
7. What does `with_allowed_hosts` protect against, and why does `main` add the host from `PUBLIC_URL`?
8. Why did `search_menu` stop returning a `total`?

<details>
<summary>Answers, after your attempt</summary>

1. Because the reader is a language model choosing tools from names and descriptions in every conversation. Many route-shaped tools confuse it; a few tools shaped around what people want to do are easier to choose correctly.
2. From the method's doc comment. The tool's name is the method's name, and the input schema's descriptions are the doc comments on `SearchMenu`'s fields.
3. A normal result with `isError: true` and the text "There's no dish 999. Use search_menu to find dish ids." The model reads errors and tries again, and the hint tells it the right next step.
4. Our errors' details are written to be joined into longer text. Here the model reads them as a whole message, so they should be a proper sentence; without the full stop, the hint ran straight on: "there's no dish 999 Use search_menu".
5. rmcp can't read the arguments into `GetDish`, so our code never runs. The model gets `isError: true` with serde's explanation: "invalid type: string "jollof", expected i64".
6. A tool is a function the model calls; a resource is information the person or app attaches, by URI; a prompt is a ready-made request the person picks. Model, app or person, and person.
7. DNS rebinding: a web page making the browser treat another name as `127.0.0.1` and talking to a local server. Requests whose `Host` isn't ours are refused. The default allows only local names, which would refuse our real domain, so `main` adds it.
8. Because it counted dishes the list left out (finished for today), and showed `"dishes": []` with `"total": 1`. A model would report a dish that isn't there. `more` only says whether there are more matches than listed.

</details>

## Practice
<!-- bite: bf847577-f31e-4240-9c4f-29c3479da992 -->

1. Add a `specials` tool: today's specials, with a description saying when to use it rather than `search_menu`. Is it worth a separate tool? Write down why or why not.
2. Add `maxPriceNaira` to `search_menu`, with a description and a check that it's positive.
3. Make `plan_lunch` refuse a budget under ₦500 with a helpful message.
4. Ask an AI app three questions about the menu, and read which tools it called and with what arguments. Rewrite one description that it misunderstood, and ask again.
5. Write a test that a request with `Host: evil.example` gets 403.

**Done when** `tools/list` shows two tools with descriptions written for a model; `search_menu` finds dishes by a word and leaves out finished ones; a missing dish tells the model what to do next; the menu resource and `plan_lunch` prompt work; a foreign `Host` gets 403; and `cargo test` runs 83 tests and passes.

## Before moving on
<!-- bite: 9ad567c4-60d3-431b-b9b3-e90e14c76954 -->

Mama Put now has a fourth door, for AI assistants: a few clear tools, results shaped for a model, errors that teach it what to do next, all on the same `MenuService` as the other three.

But everything here is public and read-only. Bayo wants to say "order me the jollof" and have it done, as him, with his money. That needs the assistant to act as Bayo, with his permission and only what he's allowed, and it needs care that a model reading text from anywhere can't be talked into spending his money. That's MCP in production, the next lesson.

## Related
<!-- bite: 13b20785-27de-44bf-a93c-738bba1a39e7 -->

- [[backend/frameworks/axum/24-mcp-in-production-1|Next: MCP in Production 1: Logging In]]
- [[backend/frameworks/net-http/23-mcp-server|The same lesson in net/http]] — the official Go SDK, and its schema checks
- [[backend/frameworks/axum/21-graphql|GraphQL]] — the same lesson about doc comments being public
- [[backend/frameworks/axum/07-errors|Errors]] — the one place errors become words for a reader

## About this lesson
<!-- bite: 8ea00b2f-c363-41d2-a4d5-06f65b6bada9 -->

**Level:** Advanced. Lesson 23 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), rmcp 3.11 and schemars 1.2. Covers what MCP is for and why tools aren't REST routes, a `ServerHandler` with instructions, tools written with `#[tool_router]` and `#[tool]` whose names, doc comments and `JsonSchema` types are what the model reads, annotations, results shaped for a model, errors as `isError` results with hints and whole sentences, what happens to arguments of the wrong type, a resource and a prompt, Streamable HTTP without sessions inside the Axum app with a body limit and allowed hosts against DNS rebinding, trying it with curl and an AI app, and testing with rmcp's own client over HTTP.
