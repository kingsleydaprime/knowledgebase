---
id: 2a1098f6-28b1-4d8e-a462-485573deebc3
---

# gRPC

**gRPC is a way for one program to call a function in another program over the network as if it were a local function. You describe the functions and their messages in a `.proto` file, both sides are built from that file, and the messages travel as small binary Protocol Buffers over HTTP/2.** REST and GraphQL are built for clients far away that you don't control. gRPC is built for services you *do* control, talking to each other quickly and strictly, many times a second.

## Before you start
<!-- bite: fcfaa2d0-229d-4635-9cf0-47a57d4c7434 -->

You should have the REST and GraphQL APIs from [[backend/frameworks/express/21-graphql|lesson 21]], both built on the same services.

After this lesson you will be able to:

1. Explain what gRPC gives services that JSON over HTTP doesn't, and why browsers rarely use it.
2. Write a `.proto` file: a package, a service, messages, field numbers.
3. Serve it from Node with `@grpc/grpc-js`, next to Express, using the same services.
4. Turn our `AppError`s into gRPC status codes, and use deadlines.
5. Call it from a Node client and from `grpcurl`, and stream messages from server to client.
6. Change a `.proto` file safely, using the same rules as lesson 10.

## What to install
<!-- bite: aaddbd07-e420-4dfe-8d96-3ae9f5232b2a -->

1. **Two npm packages**, in the `api` folder:

   ```bash
   npm install @grpc/grpc-js @grpc/proto-loader
   ```

   `@grpc/grpc-js` is gRPC itself for Node (server and client). `@grpc/proto-loader` reads `.proto` files when the program starts.

2. **`grpcurl`**, a command-line tool for calling gRPC services, like `curl` for REST. It's in most package managers (`brew install grpcurl`, `dnf install grpcurl`), or download it from its GitHub releases page. You only need it for trying calls by hand.

3. **Not needed: `protoc`**, the Protocol Buffers compiler. Many gRPC tutorials start by installing it to generate code from `.proto` files. We don't generate code: `proto-loader` reads the `.proto` file at start-up instead (step 7 explains the trade-off). The `.proto` file in step 2 is just a text file you create, `proto/mamaput/menu/v1/menu.proto`.

For syntax colours, install a Protocol Buffers extension in your editor (in VS Code, "vscode-proto3" or Buf's extension).

## Where we stopped
<!-- bite: 265a2250-699d-49de-b896-23dcc943f0d2 -->

In [[backend/frameworks/express/25-splitting-out-a-microservice|lesson 25]], sending emails and texts moves out of the main API into its own **notifications service**. To write "Your jollof rice (x2) is ready!", it needs the dish's name. It will ask the main API, for every message, all day.

Could it use the REST API? It could. But look at what it would be signing up for:

1. **No contract it can check.** It would read `res.body.data.name` and hope. If someone renames a field, it finds out in production.
2. **Text where numbers would do.** JSON sends `"priceKobo":150000` as 18 characters, field name and all, every time.
3. **Our public API's concerns.** Versions for old phones, rate limits for strangers, CORS, presenters for customers. None of that is for an internal service.

What services want from each other is different: a strict, shared contract, small fast messages, and built-in deadlines. That's what gRPC is for.

## The kid version
<!-- bite: 5aa0977f-7165-47b6-8790-c4d92f44dfb5 -->

When Mama sends her son to the market, she doesn't say "buy some stuff". She writes a list on a form they both know: "Line 1: tomatoes, how many. Line 2: pepper, how many." She fills in numbers; he reads numbers. No long sentences, no confusion about what "some" means.

And she adds: "Be back in 30 minutes. If the tomato seller isn't there, don't wait all day."

The form is the `.proto` file. The numbers on the lines are field numbers. The 30 minutes is a deadline.

**Where the picture stops working.** If Mama adds a new line to the form, her son's old copy of the form doesn't have it. With gRPC, that's fine *by design*: old readers skip lines they don't know. But she must never reuse an old line number for something new, or he'll buy pepper when she meant onions.

## Terms used in gRPC
<!-- bite: d2df53e5-b4bf-493a-8e41-02d034173c82 -->

1. **Protocol Buffers (protobuf)**: This is a way of turning structured messages into compact binary, and back, using a schema both sides share.
2. **`.proto` file**: This is the schema: the messages and the services, written in protobuf's own language.
3. **Message**: This is a structure with numbered, typed fields, like `Dish { string id = 1; string name = 2; }`.
4. **Field number**: This is the number after each field. On the wire, the field is identified by its number, not its name.
5. **Service** and **RPC**: A service is a group of functions; each function is an RPC (remote procedure call), with one request message and one response message.
6. **Unary** and **streaming**: A unary RPC is one request, one response. A streaming RPC sends many messages one way, or both ways.
7. **Status code**: This is gRPC's version of an HTTP status, like `NOT_FOUND` or `INVALID_ARGUMENT`.
8. **Deadline**: This is the time by which the caller needs an answer. After it, the call is cancelled on both sides.
9. **Metadata**: This is gRPC's version of headers: key-value pairs sent with a call.

## Step 1: what gRPC gives you
<!-- bite: ec003778-3d07-42d6-b8c7-4777df7aebee -->

| | REST + JSON | gRPC |
|---|---|---|
| Contract | Optional (OpenAPI, written beside the code) | Required: the `.proto` file is the API |
| Message size | Text, field names repeated | Binary, field numbers, much smaller |
| Speed | Parse JSON on each side | Fast binary encoding, one HTTP/2 connection reused for many calls at once |
| Timeouts | You remember to add them | Deadlines are part of every call, and travel to the next service |
| Streaming | SSE (one way), WebSockets | Built in, both directions |
| Generated clients | Optional | In almost every language from the same `.proto` |
| Browsers | Natively | Not directly; needs a proxy or gRPC-Web |
| Reading it by hand | `curl` and your eyes | Needs tools; the bytes aren't readable |

Those last two rows are why gRPC is mostly *between services*: browsers can't speak plain gRPC, and you can't debug it by looking at it. For internal calls, nobody needs to read it by hand, and every other row is a win.

## Step 2: the `.proto` file
<!-- bite: 8d1607fc-f77f-450f-9497-dab9c214e9cf -->

`proto/mamaput/menu/v1/menu.proto`:

```proto
syntax = "proto3";

package mamaput.menu.v1;

// Read-only menu access for Mama Put's own services.
service MenuService {
  // One dish by id. NOT_FOUND if there's no such dish.
  rpc GetDish(GetDishRequest) returns (Dish);

  // Many dishes at once. Unknown ids are left out of the response.
  rpc BatchGetDishes(BatchGetDishesRequest) returns (BatchGetDishesResponse);

  // Streams a message each time a dish's portions change, until the caller hangs up.
  rpc WatchPortions(WatchPortionsRequest) returns (stream PortionsChanged);
}

message GetDishRequest {
  string id = 1;
}

message BatchGetDishesRequest {
  repeated string ids = 1;
}

message BatchGetDishesResponse {
  repeated Dish dishes = 1;
}

message Dish {
  string id = 1;
  string name = 2;
  int64 price_kobo = 3;
  bool available = 4;
  int32 portions_left = 5;
  optional string photo_url = 6;
}

message WatchPortionsRequest {
  repeated string dish_ids = 1;    // empty means every dish
}

message PortionsChanged {
  string dish_id = 1;
  int32 portions_left = 2;
}
```

Reading it:

1. **`package mamaput.menu.v1`**: the full name of everything in the file. The `v1` is the version, in the name itself. A breaking change means a new package, `v2`, served side by side, like lesson 10's `/v1` and `/v2`.
2. **Every RPC has its own request and response message**, even when the request is just an id. `GetDishRequest` can gain fields later; a bare `string` can't.
3. **`repeated`** means a list.
4. **`int64` for money.** Kobo can grow past what `int32` holds (about ₦21 million), and money must never overflow.
5. **`optional`** means "may be absent, and you can tell". Without it, a missing `string` reads as `""`, and you can't tell "no photo" from "photo with an empty name".
6. **Field names are `snake_case`** in protobuf, by convention. The loader turns them into `camelCase` for JavaScript.
7. **Comments are documentation.** The `.proto` file is the contract other teams read, so it says what each call does and what errors it gives.

Where does the file live? In this repository for now, in its own `proto/` folder. When there are several services, teams often move `.proto` files to a shared repository, so every service builds from the same copy.

## Step 3: the server
<!-- bite: 46cec7cd-056d-4e76-aa30-92c2bb6aca77 -->

You installed `@grpc/grpc-js` and `@grpc/proto-loader` in "What to install". First, a file that loads the `.proto`.

`src/grpc/load.ts`:

```ts
import * as protoLoader from "@grpc/proto-loader";
import * as grpc from "@grpc/grpc-js";

const PROTO_ROOT = new URL("../../proto/", import.meta.url).pathname;

export const menuDefinition = protoLoader.loadSync("mamaput/menu/v1/menu.proto", {
  includeDirs: [PROTO_ROOT],
  keepCase: false,   // price_kobo → priceKobo
  longs: String,     // int64 → string in JavaScript (see "The TypeScript in this lesson")
  enums: String,
  defaults: true,    // missing fields get their default values
  oneofs: true,
});

export const menuPackage = grpc.loadPackageDefinition(menuDefinition) as unknown as {
  mamaput: { menu: { v1: { MenuService: grpc.ServiceClientConstructor } } };
};
```

The message types, written once by hand to match the `.proto` (step 7 talks about generating them instead), `src/grpc/menu.types.ts`:

```ts
export type GetDishRequest = { id: string };
export type BatchGetDishesRequest = { ids: string[] };
export type DishMessage = {
  id: string;
  name: string;
  priceKobo: string;          // int64 arrives and leaves as text
  available: boolean;
  portionsLeft: number;
  photoUrl?: string;
};
export type WatchPortionsRequest = { dishIds: string[] };
export type PortionsChanged = { dishId: string; portionsLeft: number };
```

Now the handlers, `src/grpc/menu.server.ts`:

```ts
import * as grpc from "@grpc/grpc-js";
import { menuPackage } from "./load.ts";
import { toGrpcError } from "./errors.ts";
import type { MenuService } from "../menu/menu.service.ts";
import type { Dish } from "../menu/menu.types.ts";
import type { GetDishRequest, BatchGetDishesRequest, DishMessage } from "./menu.types.ts";

const toMessage = (dish: Dish): DishMessage => ({
  id: dish.id,
  name: dish.name,
  priceKobo: String(dish.priceKobo),
  available: dish.available,
  portionsLeft: dish.portionsLeft,
  ...(dish.photo ? { photoUrl: `/photos/${dish.photo}` } : {}),
});

export function createMenuGrpcHandlers(menu: MenuService) {
  return {
    async GetDish(
      call: grpc.ServerUnaryCall<GetDishRequest, DishMessage>,
      callback: grpc.sendUnaryData<DishMessage>,
    ) {
      try {
        if (!/^\d{1,18}$/.test(call.request.id)) {
          return callback({ code: grpc.status.INVALID_ARGUMENT, details: "id must be a number" });
        }
        callback(null, toMessage(await menu.get(call.request.id)));
      } catch (err) {
        callback(toGrpcError(err));
      }
    },

    async BatchGetDishes(
      call: grpc.ServerUnaryCall<BatchGetDishesRequest, { dishes: DishMessage[] }>,
      callback: grpc.sendUnaryData<{ dishes: DishMessage[] }>,
    ) {
      try {
        const ids = call.request.ids;
        if (ids.length > 100) {
          return callback({ code: grpc.status.INVALID_ARGUMENT, details: "at most 100 ids per call" });
        }
        const dishes = await menu.getMany(ids);
        callback(null, { dishes: dishes.map(toMessage) });
      } catch (err) {
        callback(toGrpcError(err));
      }
    },
  };
}

export function startGrpcServer(handlers: grpc.UntypedServiceImplementation, address: string) {
  const server = new grpc.Server();
  server.addService(menuPackage.mamaput.menu.v1.MenuService.service, handlers);
  return new Promise<grpc.Server>((resolve, reject) => {
    server.bindAsync(address, grpc.ServerCredentials.createInsecure(), (err) =>
      err ? reject(err) : resolve(server),
    );
  });
}
```

The same lesson again: the handlers are **thin**. `menu.get(id)` is the menu service from lesson 4, with lesson 19's cache in front of it. REST, GraphQL and gRPC are three doors into one kitchen.

Input still gets validated at the door (lesson 6). The `.proto` guarantees `id` is a string; it doesn't guarantee it's a sensible one. And lists get limits, like every list in every API.

Each handler sends exactly one answer through `callback`: `callback(null, response)` for success, `callback(error)` for failure. A handler that forgets to call it leaves the caller waiting until its deadline.

In `server.ts`, start it next to Express:

```ts
const grpcServer = await startGrpcServer(createMenuGrpcHandlers(menuService), "127.0.0.1:50051");
console.log("gRPC listening on 50051");
```

Two ports now: 3000 for the outside world (REST, GraphQL, webhooks), 50051 for our own services. **50051 is never exposed to the internet.** In lesson 28, Docker only lets other containers reach it. `createInsecure()` means no encryption; that's acceptable for this lesson on one laptop, and lesson 26 adds authentication between services.

## Step 4: errors as status codes
<!-- bite: 03d82a58-6883-4778-89c2-bc5cdf5ee9b9 -->

gRPC has its own small set of status codes. Our `AppError` kinds map onto them, `src/grpc/errors.ts`:

```ts
import * as grpc from "@grpc/grpc-js";
import { AppError, type ErrorKind } from "../shared/errors.ts";

const STATUS: Record<ErrorKind, grpc.status> = {
  invalid: grpc.status.INVALID_ARGUMENT,
  unauthenticated: grpc.status.UNAUTHENTICATED,
  forbidden: grpc.status.PERMISSION_DENIED,
  not_found: grpc.status.NOT_FOUND,
  conflict: grpc.status.ABORTED,
  rule_broken: grpc.status.FAILED_PRECONDITION,
  upstream: grpc.status.UNAVAILABLE,
};

export function toGrpcError(err: unknown): Partial<grpc.StatusObject> {
  if (err instanceof AppError) {
    const metadata = new grpc.Metadata();
    metadata.set("error-code", err.code);       // our stable code, like "dish-not-found"
    return { code: STATUS[err.kind], details: err.message, metadata };
  }
  console.error(err);
  return { code: grpc.status.INTERNAL, details: "internal error" };
}
```

The same `Record<ErrorKind, ...>` trick as lesson 7's HTTP statuses: add a new kind and this file won't compile until it has a gRPC code too. Our own `code` travels in metadata, so a caller can tell `dish-not-found` from any other `NOT_FOUND`. And unexpected errors are hidden, as always; the details stay in our logs.

`UNAVAILABLE` has a special meaning: "try again, this is temporary". Lesson 26's retries only retry that one. Use it only for things that really are temporary.

## Step 5: calling it
<!-- bite: 39f96f61-91e1-468b-9c73-8d594278d776 -->

**From the command line.** `grpcurl` needs to know the messages. Give it the `.proto`:

```bash
grpcurl -plaintext \
  -import-path proto -proto mamaput/menu/v1/menu.proto \
  -d '{"id": "1"}' \
  127.0.0.1:50051 mamaput.menu.v1.MenuService/GetDish
```

```json
{
  "id": "1",
  "name": "Jollof rice",
  "priceKobo": "150000",
  "available": true,
  "portionsLeft": 12
}
```

Try `"id": "999"` and see `Code: NotFound`, and `"id": "abc"` for `InvalidArgument`.

(You can also add **server reflection** with `@grpc/reflection`, so tools can ask the server for its own schema and you can drop the `-proto` flags. Handy in development; leave it off in production for the same reason as GraphQL introspection.)

**From Node.** This is what the notifications service will do in lesson 25. `src/grpc/menu.client.ts`:

```ts
import * as grpc from "@grpc/grpc-js";
import { menuPackage } from "./load.ts";
import type { DishMessage } from "./menu.types.ts";

export function createMenuClient(address: string) {
  const client = new menuPackage.mamaput.menu.v1.MenuService(address, grpc.credentials.createInsecure());

  return {
    getDish(id: string, timeoutMs = 500): Promise<DishMessage> {
      return new Promise((resolve, reject) => {
        client.GetDish({ id }, { deadline: Date.now() + timeoutMs }, (err: grpc.ServiceError | null, dish: DishMessage) =>
          err ? reject(err) : resolve(dish),
        );
      });
    },
    close: () => client.close(),
  };
}
```

**Every call has a deadline.** `{ deadline: Date.now() + 500 }`: if there's no answer in half a second, the call fails with `DEADLINE_EXCEEDED`. gRPC also tells the *server* the deadline, so a server can give up on work nobody is waiting for. A call without a deadline can wait forever, and lesson 26 is about why that's the start of most outages.

One client object is made once and reused. It keeps a single HTTP/2 connection open and sends many calls over it at the same time. Making a new client per call would throw that away.

## Step 6: streaming
<!-- bite: d1cc5d6e-778b-41ff-a072-86c6e8cd5956 -->

`WatchPortions` returns `stream PortionsChanged`: one request, then many messages, until someone hangs up. It's lesson 20's SSE idea, for services.

```ts
WatchPortions(call: grpc.ServerWritableStream<WatchPortionsRequest, PortionsChanged>) {
  const wanted = new Set(call.request.dishIds);
  const unsubscribe = menuEvents.subscribe((change) => {
    if (wanted.size === 0 || wanted.has(change.dishId)) call.write(change);
  });
  call.on("cancelled", unsubscribe);
},
```

The shape is the same as the kitchen stream: subscribe, write each event, clean up when the caller goes. `call.write` sends one message; `"cancelled"` fires when the client hangs up or its deadline passes. (`menuEvents` is published by the orders service each time portions change, through Redis like lesson 20's kitchen events. That's the practice.)

gRPC can stream in both directions too (`stream` on the request *and* the response), for things like a chat or a live game. We won't need it.

## Step 7: changing a `.proto` safely
<!-- bite: 70e3b959-3e80-420c-99f7-5e082ec8a0b6 -->

Every service that talks to this one was built from the same `.proto`. When you change it, old and new versions run side by side for a while, because you can't redeploy every service at the same instant. Protobuf is designed for that, as long as you follow its rules, which are [[backend/frameworks/express/10-versioning|lesson 10]]'s rules, made precise:

**Safe:**

1. **Add a new field with a new number.** Old readers skip numbers they don't know. Old writers don't send it, so new readers get its default.
2. **Add a new RPC.** Old clients just don't call it.
3. **Rename a field.** The wire only has numbers, so the bytes don't change. (Your *code* changes, so do it carefully; JSON tools that use names will notice.)

**Breaking:**

1. **Changing a field's number**, or **reusing an old number** for something new. Old services read the new data as the old field. That's the onions-for-pepper mistake, and it corrupts data silently.
2. **Changing a field's type** (`int32` to `string`).
3. **Removing a field** without reserving its number.
4. **Changing what a field means** (kobo to naira, the most dangerous, again).

When you remove a field, reserve it, so nobody reuses it by accident:

```proto
message Dish {
  reserved 6;
  reserved "photo_url";
  // ...
}
```

The compiler then refuses any new field numbered 6 or named `photo_url`.

For a breaking change, make `mamaput.menu.v2`, serve both, move callers over, and retire `v1`, exactly like lesson 10. Tools like `buf breaking` can check a change against the last version automatically; lesson 29's pipeline is a good place for that.

**Generating types instead of writing them.** We wrote `menu.types.ts` by hand. It's small, but it can drift from the `.proto`. Code generators (`ts-proto`, `protobuf-es`) produce the types for you. One thing to check with Node running TypeScript directly: the generated code must be "erasable" TypeScript (our `erasableSyntaxOnly` setting). Some generators produce TypeScript `enum`s, which aren't, so pick options that turn enums into plain string unions, or generate JavaScript with `.d.ts` files.

## Step 8: testing
<!-- bite: 5271bc88-9da3-441f-b74c-2f457044a2c2 -->

1. **Handlers are functions.** Call `createMenuGrpcHandlers(fakeMenuService).GetDish(...)` with a fake `call` (`{ request: { id: "1" } }`) and a callback that records what it got. No network.
2. **The real thing on a free port.** Start the server on `127.0.0.1:0` (port 0 picks a free one; `bindAsync` gives you the real port), make a client, and check: a dish comes back with `priceKobo` as a string; an unknown id gives `NOT_FOUND` with `error-code: dish-not-found` in the metadata; 101 ids give `INVALID_ARGUMENT`.
3. **Deadlines.** Give the fake menu service a 1-second delay and the client a 100 ms deadline. The call must fail with `DEADLINE_EXCEEDED` in about 100 ms, not 1 second.
4. **The contract.** A test that loads the `.proto` and checks `menu.types.ts` agrees with it (field names and types) stops the hand-written types from drifting.

## The TypeScript in this lesson
<!-- bite: 527d834a-e63d-4807-a016-6eeeb40dfdd0 -->

1. **`import * as grpc from "@grpc/grpc-js"`**: Imports everything the package exports as one object, `grpc`, so you write `grpc.Server`, `grpc.status.NOT_FOUND`.
2. **`as unknown as { mamaput: ... }`**: `loadPackageDefinition` returns a very general type, because it can't know what's in your `.proto` until it runs. Casting to `unknown` first, then to the shape we know is there, is how you tell TypeScript "trust me" for something only known at runtime. Keep such casts in one place, like here.
3. **`priceKobo: string`**: JavaScript numbers are exact only up to about 9 quadrillion (2^53). An `int64` can be bigger. `longs: String` makes the loader give int64 values as text so nothing is ever silently rounded. We turn it back into a number where we know it's small enough.
4. **`grpc.ServerUnaryCall<GetDishRequest, DishMessage>`**: A generic type for "a unary call whose request is this and response is that". `call.request` is then typed.
5. **`grpc.sendUnaryData<DishMessage>`**: The type of the callback: it takes an error or `null`, and a response.
6. **`return callback(...)`**: Calling the callback and returning in one line, so nothing after it runs. The function's return value is ignored by gRPC.
7. **`...(dish.photo ? { photoUrl: ... } : {})`**: Adds `photoUrl` only when there is a photo. Spreading an empty object adds nothing. That's how you leave an `optional` field truly absent rather than `undefined`.
8. **`Record<ErrorKind, grpc.status>`**: The same complete-map trick as lesson 7, with gRPC's codes as the values.
9. **`Partial<grpc.StatusObject>`**: `Partial<T>` makes every field of `T` optional. gRPC accepts an error object with just the fields you have.
10. **`new Promise<grpc.Server>((resolve, reject) => {...})`**: Wraps a callback-style function (`bindAsync`) in a promise, so callers can `await` it. You'll see this pattern whenever an older-style library uses callbacks.
11. **`(err: grpc.ServiceError | null, dish: DishMessage) => ...`**: The client callback's types, written out because the client's type is general.

## Your project so far
<!-- bite: 86fee7d7-422d-4fe9-a855-4e9d6be710ea -->

```text
mama-put-api/
├── package.json                  ← NEW: @grpc/grpc-js, @grpc/proto-loader
├── proto/
│   └── mamaput/menu/v1/
│       └── menu.proto            ← NEW: MenuService: GetDish, BatchGetDishes, WatchPortions
└── src/
    ├── server.ts                 ← starts Express on 3000 AND gRPC on 127.0.0.1:50051
    ├── grpc/
    │   ├── load.ts               ← NEW: loads the .proto (camelCase, int64 as text, defaults)
    │   ├── menu.types.ts         ← NEW: the message types, by hand, checked by a test
    │   ├── menu.server.ts        ← NEW: thin handlers over the menu service; startGrpcServer
    │   ├── menu.client.ts        ← NEW: one reusable client, every call with a deadline
    │   ├── errors.ts             ← NEW: AppError kinds → gRPC status codes, our code in metadata
    │   └── menu.grpc.test.ts     ← NEW: handlers, a real server on port 0, deadlines, the contract
    ├── menu/
    │   └── menu.service.ts       ← NEW: getMany(ids), through the cache
    └── graphql/ · kitchen/ · jobs/ · payments/ · orders/ · auth/ · shared/ · webhooks/ · admin/ · docs/ · db/
```

## Common mistakes
<!-- bite: ae44c3e2-5943-40c2-9260-978fa20764c6 -->

1. **Exposing the gRPC port to the internet.** It's for our services. Keep it on an internal network, and add authentication (lesson 26).
2. **Calls without deadlines.** One slow service then freezes every service that calls it.
3. **Reusing or renumbering fields.** Old and new services silently read each other's data wrong. `reserved` the old numbers.
4. **int64 as JavaScript numbers.** Big values get rounded without any error. Use `longs: String`.
5. **A new client for every call.** It throws away the shared connection. Make one, reuse it.
6. **Fat handlers.** Rules inside gRPC handlers drift from REST and GraphQL. Call the service.
7. **Returning `INTERNAL` with the real error text.** It leaks internals to other teams' logs. Log it; send a plain message.
8. **`UNAVAILABLE` for errors that won't go away.** Callers will retry them over and over. Only for temporary failures.
9. **Using gRPC for browsers.** They can't speak it without a proxy. REST or GraphQL for the outside world.

## Check your understanding
<!-- bite: 4ecbe72b-33c6-4d07-ac97-02bbb5557f3c -->

1. Why is gRPC a good fit between our services but not for the phone app?
2. A new field `string description = 7;` is added to `Dish`. An old notifications service, built before the change, receives a `Dish`. What happens?
3. Someone removes `photo_url = 6`, and a month later adds `string spice_level = 6;`. What goes wrong?
4. Why does the client set a deadline on every call?
5. Why is `priceKobo` a string in JavaScript?
6. The menu service throws `notFound("Dish", "9")`. What does the gRPC caller see?

<details>
<summary>Answers, after your attempt</summary>

1. Between services, we control both sides, so a strict shared contract, small binary messages, deadlines and generated clients are all wins, and nobody needs to read the bytes. Phones and browsers can't speak plain gRPC without a proxy, and for the outside world REST's simplicity and HTTP caching matter more.
2. Nothing bad. The old service doesn't know field 7, so it skips it. Everything else reads normally.
3. Old services still think field 6 is `photo_url`. They'll read the spice level as a photo address, with no error at all. Reserving 6 when it was removed would have made the compiler refuse the new field.
4. Without one, a slow or stuck server makes the caller wait forever, and everything waiting on the caller waits too. A deadline turns "stuck" into a fast, clear `DEADLINE_EXCEEDED` the caller can handle.
5. `int64` can hold numbers bigger than JavaScript numbers can represent exactly. Loading it as text means nothing is rounded silently; we convert to a number where we know the value is small.
6. Status `NOT_FOUND`, details "Dish 9 was not found.", and `error-code: dish-not-found` in the response metadata.

</details>

## Practice
<!-- bite: b625a44a-f6b4-4ec4-8a66-4f857b4381a6 -->

1. Publish `menuEvents` when portions change (after placing an order, and on staff edits) through Redis, and finish `WatchPortions`. Watch it with `grpcurl -d '{}' ... MenuService/WatchPortions` while you place orders.
2. Add `@grpc/reflection` in development only, and call `GetDish` with `grpcurl` without `-proto`.
3. Write the contract test from step 8.
4. Add a `ListAvailableDishes` RPC with a `page_size` and `page_token`, the gRPC style of cursor pagination, reusing lesson 9's cursor code.
5. Pretend to remove `photo_url`: replace it with `reserved`, then try adding a new field numbered 6 and read the error.

**Done when** `grpcurl` gets a dish, `NOT_FOUND` for an unknown one and `INVALID_ARGUMENT` for a bad id; the Node client fails fast on a short deadline; `WatchPortions` prints a message each time you place an order; and the gRPC port can't be reached from another machine on your network.

## Before moving on
<!-- bite: e988d601-0a0f-4b96-9bd6-4e34e33fa18d -->

Mama Put API now has three ways in: REST for everyone, GraphQL for the phone app, gRPC for our own services. All three are thin doors over the same services.

There's one more kind of client knocking, and it's very new. Customers are starting to ask AI assistants things like "order me two plates of jollof from Mama Put for lunch". For an assistant to do that, it needs to discover what Mama Put can do (read the menu, check an order, place one) and call it safely. There's now a standard for exactly that: the Model Context Protocol. Next lesson, Mama Put becomes an MCP server.

## Related
<!-- bite: 015a0d37-de75-4451-aec7-f4492e676b29 -->

- [[backend/frameworks/express/23-mcp-server|Next: Building an MCP Server]]
- [[backend/frameworks/express/26-calling-services-safely|Calling Other Services Safely]] — deadlines, retries, circuit breakers and authentication for these calls
- [[backend/frameworks/express/10-versioning|Versioning]] — the same "add, don't change" rules
- [[backend/02-api-design/index|API Design]] — REST, GraphQL and gRPC side by side

## About this lesson
<!-- bite: 1b057a9f-7aef-45aa-8587-0c891522bb8d -->

**Level:** Intermediate → Advanced. Lesson 22 of [[backend/frameworks/express/index|Express]]. Covers what gRPC gives services over JSON and HTTP and why browsers rarely use it, writing a `.proto` file with a versioned package, a service, request and response messages, `repeated`, `optional`, `int64` money and field numbers, serving it from Node with `@grpc/grpc-js` and `@grpc/proto-loader` beside Express on an internal port, thin handlers with validation and list limits, mapping `AppError` kinds to gRPC status codes with our code in metadata, calling with `grpcurl` and a reusable Node client, deadlines on every call, server streaming, safe and breaking `.proto` changes with `reserved`, generated types and erasable TypeScript, and testing handlers, a real server, deadlines and the contract.
