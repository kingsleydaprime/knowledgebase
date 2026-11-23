---
id: 10976c3b-d5bd-4470-b090-1eba2153e598
---

# gRPC

**gRPC is a way for one program to call a function in another program over the network, as if it were a function in its own code.** Both sides agree on a contract first, written in a `.proto` file: which calls exist, and exactly what goes in and comes out of each. From that file, code is generated for both sides, and messages travel in a small binary format, over HTTP/2. It's made for services talking to services: strict, fast, and with timeouts and streaming built in. In Rust, the library is **tonic**.

## Before you start
<!-- bite: a19e27dc-db1f-4203-8939-f8434ee72ea1 -->

You should have:

1. Finished [[backend/frameworks/axum/21-graphql|lesson 21]], so `cargo test` runs 75 tests.

After this lesson you will be able to:

1. Say what gRPC gives services that REST and JSON don't, and where it doesn't fit.
2. Write a `.proto` contract that can change safely later.
3. Generate Rust from it in `build.rs`, with nothing extra installed.
4. Serve a gRPC service beside the HTTP server, with health, reflection and logging.
5. Turn our errors into gRPC status codes that any language can read.
6. Stream changes to a caller, and know what does and doesn't end a stream.
7. Call it, and test it with a real client on a real port.

## What to install
<!-- bite: ffae0dbe-aee0-474a-a302-db998f2addc7 -->

```bash
cargo add tonic tonic-prost prost tonic-health tonic-reflection tonic-types
cargo add --build tonic-prost-build protox prost
cargo add tokio-stream --features sync,net
```

1. **`tonic`** is the gRPC library for Rust: servers, clients, and the HTTP/2 underneath. It's built on hyper and Tower, like Axum, so the same layers work on it.
2. **`prost`** turns protobuf messages into Rust structs and back; **`tonic-prost`** connects the two.
3. **`tonic-health`** and **`tonic-reflection`** are two standard services every gRPC server should have (step 4). **`tonic-types`** has gRPC's standard error details (step 5).
4. **`--build`** adds a crate to `[build-dependencies]`: crates used only by `build.rs`, the program Cargo runs before compiling ours (step 3). **`tonic-prost-build`** writes the Rust code. **`protox`** is a protobuf compiler written in Rust. The usual compiler, `protoc`, is a separate program you'd have to install on every computer and in CI; protox is just a crate.
5. **`net`** on tokio-stream gives `TcpListenerStream`, for serving on a listener we've already opened.

## Where we stopped
<!-- bite: b41bbf3b-93d1-4cef-9eb5-aba8b0073d3b -->

Mama Put API has REST for everyone and GraphQL for the phone app. Part 6 is coming: a separate **notifications service** that texts Ada "your jollof is ready". To write that message, it needs the dish's name, many times a day. And a stock screen in the kitchen wants to know the moment any dish is running low.

They could call `GET /v2/menu/1` like any client. But:

1. JSON is text: field names repeated in every message, numbers written out as digits, parsed on both sides.
2. Nothing makes the two services agree on the shape. Rename a field in the API and the notifications service breaks at runtime, in production, at 12:40.
3. Lesson 17's Paystack client needed a timeout we had to remember to add. Every service call needs one.

Services talking to services want a strict contract, small messages and built-in deadlines. That's gRPC.

## The kid version
<!-- bite: fd3f9c50-62d3-4187-9c46-98c2c037fc20 -->

Two kitchens share one building. The cook in kitchen A sometimes needs a dish's price from kitchen B.

The REST way: write a note in full sentences, "Dear kitchen B, kindly tell me the name and price of dish number one", walk it over, and wait for a note back in full sentences.

The gRPC way: both kitchens agreed on a printed form long ago. Box 1 is the dish number, box 3 is the price. You tick boxes and slide the form through a hatch in the wall. Kitchen B fills in boxes and slides it back. Fast, small, and nobody can misread it, because the boxes are numbered.

**Where the picture stops working.** In a real kitchen, if you add a box to the form, the old forms are thrown away. With services, old and new forms are in use at the same time for a while, because you can't update every service at the same instant. So the rules for changing the form (step 8) matter a lot.

## Terms used in this lesson
<!-- bite: 8cc7b0ee-945a-40d9-bdca-2184a0408681 -->

1. **RPC**: This means remote procedure call. It's calling a function that runs in another program, usually on another machine.
2. **Protocol Buffers**: This is also called **protobuf**. It's Google's format for messages: a typed schema, and a small binary encoding.
3. **`.proto` file**: This is the file where the services and messages are described. It's the contract.
4. **Message**: This is a typed record, like `Dish`, with numbered fields.
5. **Field number**: This is the number each field has in the `.proto` (`name = 2`). On the wire only the numbers are sent, never the names.
6. **Stub** (or **client**): This is the generated code a caller uses: a Rust type whose methods make the remote calls.
7. **Deadline**: This is how long the caller will wait, sent with the call, so the server knows it too.
8. **Status code**: This is gRPC's version of an HTTP status: `OK`, `NOT_FOUND`, `INVALID_ARGUMENT`, `UNAVAILABLE` and so on.
9. **Streaming**: This is one call carrying many messages instead of one: from the server, from the client, or both.
10. **Build script**: This is `build.rs`, a small Rust program Cargo compiles and runs before compiling your crate. It can generate code for the crate to include.

## Step 1: what gRPC gives you
<!-- bite: 8eeabc16-e463-4bb8-8bcf-8970f1de8b48 -->

| | REST and JSON | gRPC |
|---|---|---|
| Contract | Optional (OpenAPI, which we wrote in lesson 11) | Required: the `.proto` file is the API |
| Message size | Text, field names repeated | Binary, field numbers, much smaller |
| Speed | Parse JSON on each side | Fast binary encoding, one HTTP/2 connection carrying many calls at once |
| Timeouts | You remember to add them | A deadline goes with every call |
| Streaming | SSE (one way), WebSockets | Built in, both directions |
| Generated clients | Optional | In almost every language, from the same `.proto` |
| Browsers | Natively | Not directly; needs a proxy or gRPC-Web |
| Reading it by hand | `curl` and your eyes | Needs tools; the bytes aren't readable |

Those last two rows are why gRPC is mostly *between services*: browsers can't speak plain gRPC, and you can't debug it by looking at it. For internal calls, nobody needs to read it by hand, and every other row is a win.

And in Rust, the contract row is even stronger than it sounds. The generated code is Rust types and a Rust trait, so a server that forgets a call, or returns the wrong message, doesn't **compile**.

## Step 2: the `.proto` file
<!-- bite: a25fd832-4fd7-4fee-9e04-1b11df799e8d -->

`proto/mamaput/menu/v1/menu.proto`:

```proto
syntax = "proto3";

package mamaput.menu.v1;

// Read-only menu access for Mama Put's own services.
service MenuService {
  // One dish by id. NOT_FOUND if there's no such dish.
  rpc GetDish(GetDishRequest) returns (GetDishResponse);
  // Many dishes at once, at most 100 ids. Unknown ids are left out of the response.
  rpc BatchGetDishes(BatchGetDishesRequest) returns (BatchGetDishesResponse);
  // A message each time a dish's portions change, until the caller hangs up.
  rpc WatchPortions(WatchPortionsRequest) returns (stream WatchPortionsResponse);
}

message GetDishRequest {
  int64 id = 1;
}

message GetDishResponse {
  Dish dish = 1;
}

message BatchGetDishesRequest {
  repeated int64 ids = 1;
}

message BatchGetDishesResponse {
  repeated Dish dishes = 1;
}

message Dish {
  int64 id = 1;
  string name = 2;
  int64 price_kobo = 3;
  bool available = 4;
  int32 portions_left = 5;
  optional string thumbnail_url = 6;
}

message WatchPortionsRequest {
  repeated int64 dish_ids = 1; // empty means every dish
}

message WatchPortionsResponse {
  int64 dish_id = 1;
  int32 portions_left = 2;
}
```

Reading it:

1. **`package mamaput.menu.v1`**: the full name of everything in the file. The `v1` is the version, in the name itself. A breaking change means a new package, `v2`, served side by side, like lesson 10's `/v1` and `/v2`.
2. **Every RPC has its own request and its own response message**, even when the request is one id and the response is one dish. `GetDishRequest` can gain fields later, and so can `GetDishResponse`. A bare `Dish` as the response would make that impossible without breaking callers.
3. **`repeated`** means a list.
4. **`int64` for money and ids.** Kobo can grow past what `int32` holds (about ₦21 million), and money must never overflow. In Rust it's just `i64`.
5. **`optional`** means "may be absent, and you can tell". Without it, a missing `string` reads as `""`, and you can't tell "no thumbnail" from "a thumbnail with an empty name". In Rust, an `optional string` becomes an `Option<String>`.
6. **`stream`** on the response of `WatchPortions` makes it a server stream: one request, then a message each time something changes.
7. **Field names are `snake_case`** by protobuf convention, which suits Rust exactly: `price_kobo` stays `price_kobo`.
8. **Comments are documentation.** The `.proto` file is the contract other teams read, so it says what each call does and what errors it gives.

The file lives in its own `proto/` folder, beside `src/`. It isn't Rust; it's the contract. When there are several services in several repositories, teams often move `.proto` files to a shared one, so every service builds from the same copy.

## Step 3: generating Rust, in `build.rs`
<!-- bite: 4080c9a9-bc11-4e62-a578-5dd4878694ad -->

`build.rs`, at the root of the project, beside `Cargo.toml`:

```rust
//! Runs before the crate compiles: turns the `.proto` contract into Rust.
//! protox is a protobuf compiler written in Rust, so nothing needs installing.

use std::{env, path::PathBuf};

use prost::Message;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto = "proto/mamaput/menu/v1/menu.proto";
    println!("cargo:rerun-if-changed={proto}");

    // Read and check the .proto (and anything it imports), as protoc would.
    let descriptors = protox::compile([proto], ["proto"])?;
    // Keep the compiled description too: gRPC reflection serves it to tools like grpcurl.
    let out = PathBuf::from(env::var("OUT_DIR")?);
    std::fs::write(out.join("menu_descriptor.bin"), descriptors.encode_to_vec())?;
    // Messages as Rust structs, the service as a trait to implement, and a client.
    tonic_prost_build::configure().compile_fds(descriptors)?;
    Ok(())
}
```

Cargo finds `build.rs` by itself, compiles it, and runs it before compiling the crate, every time `menu.proto` changes (that's what the `rerun-if-changed` line asks for).

1. **`protox::compile`** reads the `.proto`, checks it (a typo in a type name is an error here, with a line number), and returns a `FileDescriptorSet`: the whole contract, as data.
2. **We save that set** as `menu_descriptor.bin`, for reflection (step 4).
3. **`tonic_prost_build`** writes Rust from it into `OUT_DIR`, a folder Cargo gives every build script for generated files. It's in `target/`, never in `src/`: generated code isn't something to edit or commit.

The crate includes the generated code, in `src/grpc/mod.rs`:

```rust
/// The messages, the service trait and a client, generated from `proto/` by `build.rs`.
pub mod pb {
    tonic::include_proto!("mamaput.menu.v1");

    /// The compiled `.proto`, for reflection: tools like grpcurl ask the server what it offers.
    pub const FILE_DESCRIPTOR_SET: &[u8] = tonic::include_file_descriptor_set!("menu_descriptor");
}
```

`include_proto!` pastes in the generated file. Inside `pb` there are now:

1. **A struct per message**: `pb::Dish { id, name, price_kobo, available, portions_left, thumbnail_url }`, with `#[derive(prost::Message)]` doing the binary encoding.
2. **A trait per service**, `pb::menu_service_server::MenuService`, with one async method per RPC. Our server implements it.
3. **A client per service**, `pb::menu_service_client::MenuServiceClient`, with the same methods, which make the calls.

## Step 4: the server
<!-- bite: 2621460f-ca3c-4da6-b6fe-b653322a6ec5 -->

The trait's name, `MenuService`, is also the name of our own menu service, so the generated one is imported as `MenuGrpc`. `src/grpc/menu.rs`:

```rust
use std::{collections::HashSet, pin::Pin};

use axum::http::StatusCode;
use tokio_stream::{Stream, StreamExt, wrappers::BroadcastStream};
use tonic::{Request, Response, Status};

use super::{
    errors::status,
    pb::{
        BatchGetDishesRequest, BatchGetDishesResponse, GetDishRequest, GetDishResponse, WatchPortionsRequest, WatchPortionsResponse,
        menu_service_server::MenuService as MenuGrpc,
    },
};
use crate::{
    http::ApiError,
    kitchen::{Hub, KitchenEvent},
    menu::{Dish, MenuService},
};

/// The `MenuService` from `menu.proto`, answered by the same `MenuService` as REST and GraphQL.
#[derive(Clone)]
pub struct MenuApi {
    pub menu: MenuService,
    pub hub: Hub,
}

impl From<Dish> for super::pb::Dish {
    fn from(d: Dish) -> Self {
        super::pb::Dish {
            id: d.id,
            name: d.name,
            price_kobo: d.price.0,
            available: d.available,
            portions_left: d.portions_left,
            thumbnail_url: d.thumb.map(|name| format!("/uploads/{name}")),
        }
    }
}

type PortionsStream = Pin<Box<dyn Stream<Item = Result<WatchPortionsResponse, Status>> + Send>>;

#[tonic::async_trait]
impl MenuGrpc for MenuApi {
    async fn get_dish(&self, request: Request<GetDishRequest>) -> Result<Response<GetDishResponse>, Status> {
        let dish = self.menu.get(request.into_inner().id).await.map_err(status)?;
        Ok(Response::new(GetDishResponse { dish: Some(dish.into()) }))
    }

    async fn batch_get_dishes(&self, request: Request<BatchGetDishesRequest>) -> Result<Response<BatchGetDishesResponse>, Status> {
        let ids = request.into_inner().ids;
        if ids.len() > 100 {
            return Err(status(ApiError::new(StatusCode::BAD_REQUEST, "too-many-ids", "Too many ids", "Ask for at most 100 dishes at once.")));
        }
        let dishes = self.menu.many(&ids).await.map_err(status)?;
        Ok(Response::new(BatchGetDishesResponse { dishes: dishes.into_iter().map(Into::into).collect() }))
    }

    type WatchPortionsStream = PortionsStream;

    /// Every change to the dishes asked about, from this moment, until the caller hangs up.
    /// Subscribe first, then call `BatchGetDishes` for the starting numbers: nothing falls between.
    async fn watch_portions(&self, request: Request<WatchPortionsRequest>) -> Result<Response<PortionsStream>, Status> {
        let wanted: HashSet<i64> = request.into_inner().dish_ids.into_iter().collect();
        let changes = BroadcastStream::new(self.hub.subscribe())
            .map_while(move |got| match got {
                Ok(KitchenEvent::Portions { dish_id, portions_left }) if wanted.is_empty() || wanted.contains(&dish_id) => {
                    Some(Some(Ok(WatchPortionsResponse { dish_id, portions_left })))
                }
                // Missed changes: end with UNAVAILABLE, "call again", and the caller starts afresh.
                Ok(KitchenEvent::Resync) | Err(_) => Some(Some(Err(status(ApiError::new(
                    StatusCode::SERVICE_UNAVAILABLE,
                    "missed-updates",
                    "Missed updates",
                    "Some changes were missed. Call again, and read the dishes afresh.",
                ))))),
                Ok(_) => Some(None), // another dish, or not about stock
            })
            .filter_map(|change| change);
        Ok(Response::new(Box::pin(changes)))
    }
}
```

1. **`MenuApi` holds our `MenuService`**, the same one REST and GraphQL use, and lesson 20's hub. gRPC is a third door into the same house: `get_dish` is cached by lesson 19, and its "not found" is the same error.
2. **`#[tonic::async_trait]`**: the generated trait uses async-trait, so our `impl` must too.
3. **`Request<T>` and `Response<T>`** wrap the messages with their metadata (gRPC's headers). `into_inner()` takes the message out.
4. **`Option<Dish>` in the response.** In proto3, a message field is always optional underneath, so prost makes `dish` an `Option`. We always send `Some`.
5. **`From<Dish> for pb::Dish`** turns our domain type into the contract's type, the way lesson 10's `DishV2::from` did for JSON. The domain type knows nothing of protobuf.
6. **`BatchGetDishes` refuses more than 100 ids.** The contract says so, and it stops one call from asking for the whole table.

### Serving it

The rest of `src/grpc/mod.rs`:

```rust
/// Serves gRPC on `listener` until `shutdown` finishes, then lets running calls end.
/// `reflection`: whether tools may ask what the server offers (yes while developing).
pub async fn serve(
    listener: TcpListener,
    menu: MenuApi,
    reflection: bool,
    shutdown: impl Future<Output = ()>,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // The standard health service: load balancers and Docker ask it "are you serving?" (lesson 38).
    let (health, health_service) = tonic_health::server::health_reporter();
    health.set_serving::<MenuServiceServer<MenuApi>>().await;

    let reflection = match reflection {
        true => Some(
            tonic_reflection::server::Builder::configure()
                .register_encoded_file_descriptor_set(pb::FILE_DESCRIPTOR_SET)
                .register_encoded_file_descriptor_set(tonic_health::pb::FILE_DESCRIPTOR_SET)
                .build_v1()?,
        ),
        false => None,
    };

    Server::builder()
        // No call runs longer than 10 seconds, whatever deadline the caller sent; a shorter one wins.
        .timeout(Duration::from_secs(10))
        // The same Tower layers as the HTTP side: one log line per call.
        .layer(TraceLayer::new_for_grpc().on_response(DefaultOnResponse::new().level(Level::INFO)))
        .add_service(health_service)
        .add_service(MenuServiceServer::new(menu))
        .add_optional_service(reflection)
        .serve_with_incoming_shutdown(TcpListenerStream::new(listener), shutdown)
        .await?;
    Ok(())
}
```

1. **Health.** `grpc.health.v1.Health` is a standard service every gRPC server should offer: "is `mamaput.menu.v1.MenuService` serving?". Load balancers, Kubernetes and lesson 38's Docker health checks ask it.
2. **Reflection**, while developing: tools like `grpcurl` can ask the server what services and messages it offers, using the descriptor set `build.rs` saved. Off in production, like GraphQL's introspection.
3. **`.timeout(10s)`** and **`TraceLayer::new_for_grpc()`** are Tower layers, as on the HTTP side: the same 10 seconds, and one log line per call. tonic is built on Tower, so the layers you know work here too.
4. **`serve_with_incoming_shutdown`** serves on a listener we opened ourselves, until `shutdown` finishes, then lets calls in progress end. Opening the listener ourselves is what lets tests use port 0 (step 9).

And in `main`, beside the HTTP server:

```rust
    // gRPC, for our own services, on a port of its own. 127.0.0.1: only programs on this machine.
    let grpc_addr = std::env::var("GRPC_ADDR").unwrap_or_else(|_| "127.0.0.1:50051".into());
    let grpc_listener = TcpListener::bind(&grpc_addr).await?;
    info!(addr = %grpc_listener.local_addr()?, "gRPC listening");
    let menu_api = grpc::MenuApi { menu: state.menu.clone(), hub: state.kitchen.hub.clone() };
    tokio::spawn(async move {
        if let Err(e) = grpc::serve(grpc_listener, menu_api, introspection, shutdown_signal()).await {
            tracing::error!(cause = %e, "gRPC server stopped");
        }
    });
```

Two ports now: 8080 for the outside world (REST, GraphQL, webhooks), 50051 for our own services. **50051 is never exposed to the internet**: `127.0.0.1` means only programs on this machine can connect, and in lesson 38, Docker only lets other containers reach it. There's no login on it yet, because only our own services can reach it; lesson 33 adds service-to-service authentication, so that "on our network" isn't the only protection.

## Step 5: errors as status codes
<!-- bite: d02a20f4-6754-47b5-896a-cd78d72747b9 -->

gRPC has its own small set of status codes. Our `ApiError`s map onto them. `src/grpc/errors.rs`:

```rust
use std::collections::HashMap;

use axum::http::StatusCode;
use tonic::{Code, Status};
use tonic_types::{ErrorDetails, StatusExt};

use crate::http::ApiError;

/// Any of our errors as a gRPC status: the nearest code, our calm `detail` as the message, and our stable
/// `code` in a standard `ErrorInfo` detail, which a client in any language can read. Internal errors were
/// already logged by `ApiError::internal`, and say nothing more.
pub fn status(err: impl Into<ApiError>) -> Status {
    let err: ApiError = err.into();
    let code = match err.status {
        StatusCode::BAD_REQUEST | StatusCode::UNPROCESSABLE_ENTITY => Code::InvalidArgument,
        StatusCode::UNAUTHORIZED => Code::Unauthenticated,
        StatusCode::FORBIDDEN => Code::PermissionDenied,
        StatusCode::NOT_FOUND => Code::NotFound,
        StatusCode::CONFLICT => Code::FailedPrecondition,
        StatusCode::REQUEST_TIMEOUT => Code::DeadlineExceeded,
        StatusCode::TOO_MANY_REQUESTS => Code::ResourceExhausted,
        // Only for things that really are temporary: callers may retry these (lesson 33).
        StatusCode::BAD_GATEWAY | StatusCode::SERVICE_UNAVAILABLE => Code::Unavailable,
        _ => Code::Internal,
    };
    let info = ErrorDetails::with_error_info(err.code, "mamaput.example", HashMap::new());
    Status::with_error_details(code, err.detail, info)
}
```

1. **Every error goes through `ApiError` first**, with lesson 7's `From` impls, so the menu's `NotFound` is `dish-not-found` here, in REST and in GraphQL. One set of words, three doors.
2. **The nearest gRPC code** comes from the HTTP status. 404 is `NOT_FOUND`, 409 is `FAILED_PRECONDITION` ("the system isn't in a state for this"), and anything unexpected is `INTERNAL`, with the details only in our log.
3. **Our stable code goes in an `ErrorInfo` detail**: a standard protobuf message from Google for exactly this, which any gRPC client in any language can read. A caller can tell `dish-not-found` from `order-not-found` without parsing English. `domain` says whose codes these are.
4. **`UNAVAILABLE` has a special meaning**: "try again, this is temporary". Lesson 33's retries will retry only that one. Use it only for things that really are temporary, never for "you sent something wrong".

## Step 6: calling it
<!-- bite: ef139b3d-1866-442e-aad1-1d322f808de4 -->

**From Rust**, the way the notifications service will. `examples/menu_client.rs`:

```rust
//! Calls the menu over gRPC, the way another of our services will.
//!
//! cargo run --example menu_client -- 1

use std::time::Duration;

use mama_put::grpc::pb::{GetDishRequest, menu_service_client::MenuServiceClient};
use tonic::Request;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let id: i64 = std::env::args().nth(1).unwrap_or_else(|| "1".into()).parse()?;
    let mut menu = MenuServiceClient::connect("http://127.0.0.1:50051").await?;

    let mut request = Request::new(GetDishRequest { id });
    request.set_timeout(Duration::from_millis(500)); // sent with the call: the server knows it too
    match menu.get_dish(request).await {
        Ok(answer) => println!("{:#?}", answer.into_inner().dish),
        Err(status) => println!("{:?}: {}", status.code(), status.message()),
    }
    Ok(())
}
```

```bash
cargo run --example menu_client -- 1
cargo run --example menu_client -- 999
```

```text
Some(
    Dish {
        id: 1,
        name: "Jollof rice",
        price_kobo: 150000,
        available: true,
        portions_left: 0,
        thumbnail_url: None,
    },
)
NotFound: there's no dish 999
```

and the server's log has one line per call, with gRPC's code for the answer (`5` is `NOT_FOUND`):

```text
INFO tower_http::trace::on_response: finished processing request latency=91 ms status=5
```

`MenuServiceClient::connect` opens one HTTP/2 connection, and every call on it shares that connection, many at once. Make one client and clone it (it's cheap), the way lesson 17 made one `reqwest::Client`.

**The deadline.** `set_timeout(500 ms)` sends a `grpc-timeout` header with the call. The server reads it and gives up at whichever is sooner: the caller's deadline, or its own 10 seconds. When it gives up, it drops the handler's future, and with it the database query that was waiting: in Rust, cancelling is dropping, as it was in lesson 19. The caller never hangs. It gets `CANCELLED` with the message "Timeout expired": that's tonic's choice, where the gRPC docs would lead you to expect `DEADLINE_EXCEEDED`, so a caller deciding what to retry should look for both.

**From the command line**, with `grpcurl` installed, reflection lets it find everything by itself:

```bash
grpcurl -plaintext 127.0.0.1:50051 list
grpcurl -plaintext -d '{"id": 1}' 127.0.0.1:50051 mamaput.menu.v1.MenuService/GetDish
```

## Step 7: streaming
<!-- bite: c8845bd2-bf79-414e-9001-48ac2a52f4dd -->

`WatchPortions` sends a message each time a dish's plates change. Where do the changes come from? Lesson 20's hub, with one new event. In `src/kitchen/events.rs`:

```rust
    /// A dish's plates changed: an order took some, or the kitchen restocked.
    #[serde(rename = "dish.portions")]
    Portions { dish_id: i64, portions_left: i32 },
```

announced like the others, inside the transaction that made it true: in `place_taking_portions`, whose guarded `UPDATE` now says `RETURNING price_kobo, portions_left`, and in the menu store's `change` when it sets `portions_left`, which now runs in a transaction. Every server hears it through Postgres's `NOTIFY`, and every server's hub passes it on. The kitchen's SSE stream skips it (the screen shows orders, not stock), which is why `live_events` now uses `Some(None)` for "not for this screen" and `.filter_map` to drop those.

`watch_portions`, from step 4, turns the hub into the call's stream:

1. **`map_while` and `filter_map`**, as in lesson 20: changes to watched dishes become messages; other events are skipped; a lagging or resyncing stream sends one last `UNAVAILABLE`, "missed-updates", and ends. An `Err` in a tonic stream is sent as the call's final status.
2. **`type WatchPortionsStream`** is the stream's type, chosen by us. `Pin<Box<dyn Stream<...> + Send>>` is "some boxed stream", which saves writing the real type of `map_while(...).filter_map(...)` out in full.
3. **No snapshot.** The caller subscribes first, then calls `BatchGetDishes` for the starting numbers, so nothing falls between. The `.proto` comment says so.

**What ends a stream?** Here I was wrong at first, and the test showed it. I gave the call a 2-second deadline and expected the stream to end after 2 seconds. It didn't: it ran until the test gave up. In tonic, the deadline and the server's 10 seconds cover a call **until its answer starts**. A unary call's answer is one message, so that's the whole call. A stream's answer starts at once, and then runs for as long as it runs. (Go's gRPC library ends streams at the deadline too; tonic doesn't.)

So a stream ends when:

1. **The caller hangs up.** Dropping the stream closes it; the server's stream is dropped, and the receiver with it, so the hub forgets that watcher. The test checks exactly this.
2. **The server ends it**: "missed-updates" here, or lesson 38's shutdown.
3. **You give it a time limit yourself**, if you want one: `tokio_stream::StreamExt::timeout` on the server's stream, or the caller dropping it after a while. A watcher that reconnects every few minutes also gets a fresh start, like lesson 20's screens.

## Step 8: changing a `.proto` safely
<!-- bite: f4a1b330-1455-4284-9ed2-aa0daab1745c -->

Only field **numbers** travel on the wire, never names. That makes some changes safe and others disastrous:

| Change | Safe? | Why |
|---|---|---|
| Add a field with a new number | Yes | Old readers skip numbers they don't know; new readers see the default for a field that's missing |
| Add an RPC | Yes | Old clients never call it |
| Rename a field, keep its number | Yes on the wire | Bytes don't change; only code that uses the name must be updated |
| Remove a field | Only with `reserved` | Write `reserved 6; reserved "thumbnail_url";` so the number and name can never be used again |
| Change a field's type or number | **No** | Old and new programs read the same bytes as different things |
| Reuse an old field number | **Never** | An old client's `price_kobo` becomes a new server's `portions_left` |

Anything breaking means a new package, `mamaput.menu.v2`, served beside `v1` until every caller has moved, like lesson 10's versions.

A tool can check this for you: `buf breaking` compares your `.proto` with the last released one and refuses breaking changes. Lesson 39 runs it in CI.

## Step 9: testing
<!-- bite: 67489241-0941-47ff-b932-828dfcfbb3a3 -->

`tests/grpc.rs` tests the service the way another service uses it: a real tonic client, over a real connection, to a real server on a free port.

```rust
/// Starts the gRPC server for `app` on a free port, and connects a client to it.
async fn client(app: &TestApp) -> (MenuServiceClient<Channel>, String) {
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = format!("http://{}", listener.local_addr().unwrap());
    let api = MenuApi { menu: app.menu(), hub: app.kitchen.hub.clone() };
    tokio::spawn(grpc::serve(listener, api, true, std::future::pending()));
    (MenuServiceClient::connect(address.clone()).await.unwrap(), address)
}
```

`std::future::pending()` is a future that never finishes: in a test, the server never needs to shut down, because it ends when the test does. The four tests:

1. `a_dish_by_id_and_a_clear_not_found`: a dish comes back; 999 is `NOT_FOUND`, with our message, and `dish-not-found` in its `ErrorInfo`.
2. `many_dishes_in_one_call_but_not_too_many`: unknown ids left out; 101 ids is `INVALID_ARGUMENT`.
3. `a_watcher_hears_each_change_until_it_hangs_up`, below.
4. `the_health_service_says_serving`, with tonic-health's own client.

The stream test:

```rust
#[sqlx::test]
async fn a_watcher_hears_each_change_until_it_hangs_up(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let ada = app.user("ada@example.com", "customer").await;
    let (jollof, beans) = (app.dish("Jollof rice", 1500, 40).await, app.dish("Beans", 1200, 40).await);
    let (mut menu, _) = client(&app).await;

    let mut changes = menu.watch_portions(WatchPortionsRequest { dish_ids: vec![jollof] }).await.unwrap().into_inner();
    app.order(&ada, beans).await; // not watched
    app.order(&ada, jollof).await;
    app.patch(&format!("/v1/menu/{jollof}")).header("x-staff-key", STAFF_KEY).json(json!({"portionsLeft": 50})).send().await;

    let wait = Duration::from_secs(5);
    let first = tokio::time::timeout(wait, changes.next()).await.expect("within 5 s").unwrap().unwrap();
    assert_eq!((first.dish_id, first.portions_left), (jollof, 39), "an order took one");
    let second = tokio::time::timeout(wait, changes.next()).await.expect("within 5 s").unwrap().unwrap();
    assert_eq!((second.dish_id, second.portions_left), (jollof, 50), "the kitchen restocked");

    // Hanging up ends it: the server's stream is dropped, and with it its place in the hub.
    assert_eq!(app.kitchen.hub.screens(), 1);
    drop(changes);
    for _ in 0..50 {
        if app.kitchen.hub.screens() == 0 {
            return;
        }
        tokio::time::sleep(Duration::from_millis(20)).await;
    }
    panic!("the server still listens for a caller that hung up");
}
```

An order for beans (not watched), an order for jollof, and a restock through v1's REST door; the watcher hears exactly the two jollof changes, each through a `NOTIFY` in its own transaction. Then it hangs up, and the hub's count of listeners drops to zero. The 5-second `timeout` on each read means a missing message fails the test instead of hanging it. (Writing it, I first used an async closure for those reads, and the stream never delivered. Plain `timeout` calls worked. I didn't find out why, which is a good reason to keep test code plain.)

```bash
cargo test
```

79 tests, all passing.

## The Rust in this lesson
<!-- bite: 2a119291-c7b5-4656-8398-6d8d789bdfd3 -->

1. **`build.rs`** and **`[build-dependencies]`**: A program Cargo runs before compiling the crate, with its own dependencies. `println!("cargo:rerun-if-changed=...")` tells Cargo when to run it again.
2. **`OUT_DIR`** and **`include!`-style macros**: Generated code goes in a folder Cargo chooses; `tonic::include_proto!` and `include_file_descriptor_set!` paste it in at compile time.
3. **Generated traits**: tonic writes `pb::menu_service_server::MenuService`, and the compiler makes sure our server implements every call, with the right types.
4. **`use ... as ...`**: Renaming an import (`MenuService as MenuGrpc`) when two things share a name.
5. **Associated types in a trait impl**, `type WatchPortionsStream = PortionsStream;`: The trait leaves the stream's type for us to choose.
6. **`Pin<Box<dyn Stream<Item = ...> + Send>>`**: Some stream, on the heap, pinned in place: the usual way to return a stream whose real type is long or unnameable.
7. **`HashSet` and `move` closures**: `wanted` is moved into the stream's closure, so the stream owns it for as long as it runs.
8. **`Option<Option<T>>`**: Two levels of "maybe": outside, "carry on or stop"; inside, "send something or not".
9. **`impl Future<Output = ()>` as a parameter**: Any future at all, here the signal to shut down: `shutdown_signal()` in `main`, `std::future::pending()` in tests.
10. **`.add_optional_service(Option<S>)`**: Adds a service only if it's `Some`, which keeps the builder one chain.
11. **`examples/` with arguments**: `cargo run --example menu_client -- 1` passes `1` to the example; `std::env::args()` reads it.

## Your project so far
<!-- bite: f907e49f-c769-4704-b027-afc9e00ddba4 -->

```text
mama-put/
├── Cargo.toml                    ← tonic, tonic-prost, prost, tonic-health, tonic-reflection, tonic-types;
│                                   [build-dependencies] tonic-prost-build, protox, prost; tokio-stream "net"
├── build.rs                      ← NEW: compiles proto/ with protox; saves the descriptor set
├── proto/
│   └── mamaput/menu/v1/menu.proto ← NEW: the contract: GetDish, BatchGetDishes, WatchPortions (a stream)
├── examples/
│   └── menu_client.rs            ← NEW: calls GetDish with a deadline
├── src/
│   ├── main.rs                   ← gRPC on GRPC_ADDR (127.0.0.1:50051), beside HTTP, shutting down with it
│   ├── grpc/                     ← NEW
│   │   ├── mod.rs                ← pb (generated), serve: health, reflection, timeout, trace
│   │   ├── menu.rs               ← MenuApi: the three calls, on the same MenuService
│   │   └── errors.rs             ← status: nearest code, our message, ErrorInfo with our code
│   ├── kitchen/
│   │   ├── events.rs             ← KitchenEvent::Portions
│   │   └── stream.rs             ← the kitchen screen skips Portions
│   ├── orders/store.rs           ← taking plates announces Portions in its transaction
│   └── menu/store.rs             ← a restock announces Portions; change runs in a transaction
└── tests/
    └── grpc.rs                   ← NEW: 4 tests with a real client on a real port
```

## Common mistakes
<!-- bite: 86c551f2-7113-4920-8632-249acd4f01d2 -->

1. **A bare message as a response**, `returns (Dish)`. It can never gain a field beside the dish. Give every call its own response message.
2. **Changing or reusing field numbers.** Old and new programs read the same bytes differently. Add new numbers; `reserved` the old ones.
3. **`int32` for money.** It overflows at about ₦21 million in kobo. Use `int64`.
4. **Our raw error text in a status.** It can leak internal details. Go through `ApiError`, and put the stable code in `ErrorInfo`.
5. **`UNAVAILABLE` for a bad request.** Callers will retry it for ever. Use it only for things that really are temporary.
6. **Exposing the gRPC port to the internet.** It has no login yet. Bind to `127.0.0.1` or a private network.
7. **Expecting a deadline to end a stream.** In tonic it only covers the call until the answer starts. End streams by hanging up, or with a limit of your own.
8. **A new client for every call.** It throws away the HTTP/2 connection. Make one and clone it.
9. **Generated code in `src/`.** It drifts from the `.proto`. Generate it in `build.rs`, into `OUT_DIR`.

## Check your understanding
<!-- bite: c0cac5c6-2688-4425-a18e-5c74e11cf332 -->

1. What does gRPC give two of our own services that REST and JSON don't, and why isn't it used for the phone app?
2. Why does every call in `menu.proto` have its own request and response message?
3. What does `build.rs` do, and why protox instead of `protoc`?
4. A caller asks for dish 999. What does it get back, and how can a program in another language tell which error it is?
5. A caller sets a 500 ms deadline on `GetDish`, and the database is slow. What happens on each side?
6. Why doesn't a 2-second deadline end a `WatchPortions` stream, and what does end one?
7. Which of these is safe to release while old clients are still running: adding a field 7, renaming `name` to `title`, changing `portions_left` to `int64`, reusing number 6 for something new?

<details>
<summary>Answers, after your attempt</summary>

1. A required contract that generates matching code on both sides (in Rust, checked by the compiler), small binary messages over one HTTP/2 connection, a deadline with every call, and streaming built in. Browsers can't speak plain gRPC and nobody can read it by eye, so it's for services, not the phone app.
2. So each can gain fields later without breaking callers. A bare `Dish` as a response could never gain a field beside the dish.
3. It compiles the `.proto` into Rust before the crate is compiled, saving the generated code in `OUT_DIR`, and saves the descriptor set for reflection. protox is a crate, so nobody has to install `protoc` on their computer or in CI.
4. `NOT_FOUND`, with the message "there's no dish 999", and an `ErrorInfo` detail whose `reason` is `dish-not-found`. `ErrorInfo` is a standard message any gRPC library can decode.
5. The deadline travels with the call as `grpc-timeout`. The server gives up at the sooner of 500 ms and its own 10 seconds, dropping the handler's future and the query in it. The caller gets an error, not a hang: `CANCELLED` with "Timeout expired", which is how tonic reports it.
6. Because in tonic the deadline only covers the call until its answer starts, and a stream's answer starts at once. A stream ends when the caller hangs up (dropping it), when the server ends it, or at a time limit you add yourself.
7. Adding field 7: safe. Renaming `name` to `title` while keeping number 2: safe on the wire, though code using the name changes. Changing `portions_left` to `int64`: not safe, the bytes mean something different. Reusing 6: never.

</details>

## Practice
<!-- bite: 55fb8c98-e886-4149-94ea-e090815a0c77 -->

1. Add `optional string description = 7;` to `Dish` (lesson 9's dishes have one), fill it in `From<Dish>`, and check an old client still works.
2. Add a server-side limit of 30 minutes to `WatchPortions` with `tokio_stream::StreamExt::timeout`, ending with `UNAVAILABLE` so the caller reconnects.
3. Write a test that a `GetDish` with a 10 ms deadline, against a store that sleeps for 100 ms, gets `CANCELLED` with "Timeout expired" in well under 100 ms. (Hint: lesson 21's counting store, with a sleep.)
4. Add a row to a test that every `ApiError` status our code uses maps to a gRPC code other than `INTERNAL`, except 500.
5. Install `grpcurl` and call all three methods by hand, using reflection.

**Done when** `cargo run --example menu_client -- 1` prints a dish and `999` prints `NotFound`; the server logs one line per call; a watcher hears an order and a restock, and the hub forgets it when it hangs up; the health service says `SERVING`; and `cargo test` runs 79 tests and passes.

## Before moving on
<!-- bite: 6cd94de6-0672-48b0-a01b-258d5d7f63dc -->

Mama Put now speaks three ways: REST for the world, GraphQL for its app, and gRPC for its own services, all through the same services, with the same rules and the same error codes, and the contract for the third checked by the compiler on both sides.

There's one more kind of client to meet before Part 6: not a person, and not one of our programs, but an AI assistant acting for a person. Ada asks her assistant "order me jollof from Mama Put", and it needs to know what Mama Put can do, and how to ask. That's an MCP server.

## Related
<!-- bite: 728e1ec3-f63f-456d-bb83-622289c9afea -->

- [[backend/frameworks/axum/23-mcp-server|Next: Building an MCP Server]]
- [[backend/frameworks/net-http/22-grpc|The same lesson in net/http]] — grpc-go, buf, and interceptors
- [[backend/frameworks/axum/20-real-time|Real-time Updates]] — the hub `WatchPortions` reads from
- [[backend/frameworks/axum/10-versioning|Versioning]] — the same idea as `mamaput.menu.v2`

## About this lesson
<!-- bite: 6aaa547b-20cf-4ed6-87a5-15a6296dcebe -->

**Level:** Advanced. Lesson 22 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), tonic 0.14, prost 0.14 and protox 0.10. Covers what gRPC gives services and where it doesn't fit, a `.proto` contract with its own messages per call, `int64` money and `optional`, generating Rust in `build.rs` with protox and tonic-prost-build, implementing the generated trait on the same `MenuService`, health, reflection, timeout and trace layers, a second port on `127.0.0.1`, errors as status codes with `ErrorInfo`, a Rust client with a deadline, a server stream from the hub with the `Portions` event announced in its transactions, what does and doesn't end a stream in tonic, changing a `.proto` safely, and testing with a real client on a real port.
