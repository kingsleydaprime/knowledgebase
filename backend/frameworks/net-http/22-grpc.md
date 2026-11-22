---
id: f077ea1c-2879-4ae2-b27f-9ee6077e701c
---

# gRPC

**gRPC is a way for one program to call a function in another program over the network, as if it were a normal function call. You describe the functions and their messages in a `.proto` file; tools generate typed code for both sides; and the messages travel as small binary Protocol Buffers over HTTP/2.** REST is built around resources and URLs, for anyone. gRPC is built around functions and contracts, mostly for your own services talking to each other.

## Before you start
<!-- bite: 761918b7-6489-4ba4-b836-a323a0e5f8fd -->

You should have finished [[backend/frameworks/net-http/21-graphql|lesson 21]]. You've seen code generation twice already, oapi-codegen in lesson 11 and gqlgen in lesson 21, and gRPC is the third: a contract file in, typed Go out.

After this lesson you will be able to:

1. Write a `.proto` file: a service, its RPCs, messages, field numbers, `repeated` and `optional`.
2. Generate Go with `buf`, `protoc-gen-go` and `protoc-gen-go-grpc`, all run as Go tools.
3. Serve the menu over gRPC with grpc-go, beside the HTTP server, on the same services.
4. Turn `apperr` errors into gRPC status codes with an interceptor, with our stable code in the details.
5. Call it from Go with a deadline, stream changes to a caller, and test the whole thing in memory with `bufconn`.
6. Change a `.proto` without breaking callers, and let `buf breaking` check it for you.

## What to install
<!-- bite: ccd661a2-7f8b-4c6a-85c3-f4d129f79555 -->

No compiler to install by hand. The usual Protocol Buffers compiler, `protoc`, is a C++ program you'd download separately; **buf** is a modern replacement written in Go, so it can be a Go tool like oapi-codegen and gqlgen. In the `mama-put` folder:

```bash
go get -tool github.com/bufbuild/buf/cmd/buf@latest
go get -tool google.golang.org/protobuf/cmd/protoc-gen-go@latest
go get -tool google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
go get google.golang.org/grpc@latest
```

1. **buf** reads `.proto` files, checks their style (`buf lint`), checks a change won't break callers (`buf breaking`), and runs the code generators (`buf generate`).
2. **protoc-gen-go** generates the Go types for the messages.
3. **protoc-gen-go-grpc** generates the Go server interface and client for the services.
4. **grpc-go** (`google.golang.org/grpc`) is the gRPC library itself, which the generated code and our server use.

Check it worked: `go tool buf --version` prints a version number.

For calling the server by hand, install **grpcurl**, which is `curl` for gRPC. It's a tool for you, not for the project, so it goes in your own `~/go/bin` rather than in `go.mod`:

```bash
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
```

(If `grpcurl` isn't found afterwards, add `$(go env GOPATH)/bin` to your `PATH`.) For syntax colours in your editor, install a Protocol Buffers extension; for VS Code, the "Buf" extension also shows lint problems as you type.

## Where we stopped
<!-- bite: 6456161c-cef5-4924-aedc-3e92d8397409 -->

Mama Put API has REST for everyone and GraphQL for the phone app. Part 6 is coming: a separate **notifications service** that texts Ada "your jollof is ready". To write that message, it needs the dish's name, many times a day. It could call `GET /v2/menu/1` like any client. But:

1. JSON is text: field names repeated in every message, numbers written out as digits, parsed on both sides.
2. Nothing makes the two services agree on the shape. Rename a field in the API and the notifications service breaks at runtime, in production, at 12:40.
3. Lesson 17's Paystack client needed a timeout we had to remember to add. Every service call needs one.

Services talking to services want a strict contract, small messages and built-in deadlines. That's gRPC. It was made at Google for exactly this, and much of the world's gRPC code is Go.

## The kid version
<!-- bite: 618b9b9b-7a18-4b9a-8afe-12c24e865566 -->

Two kitchens share one building. The cook in kitchen A sometimes needs a dish's price from kitchen B.

The REST way: write a note in full sentences, "Dear kitchen B, kindly tell me the name and price of dish number one", walk it over, wait for a note back in full sentences.

The gRPC way: both kitchens agreed on a printed form long ago. Box 1 is the dish number, box 3 is the price. You tick boxes and slide the form through a hatch in the wall. Kitchen B fills boxes and slides it back. Fast, small, and nobody can misread it, because the form is the same on both sides.

**Where the picture stops working.** In a real kitchen, if you add a box to the form, the old forms are just thrown away. With services, old and new forms are in use at the same time for a while, because you can't update every service at the same instant. So there are rules for changing the form (step 8).

## Terms used in this lesson
<!-- bite: 9d10400d-09a1-424b-a365-d9c04213e302 -->

1. **RPC**: This means remote procedure call. It's calling a function that runs in another program, usually on another machine.
2. **Protocol Buffers**: This is also called **protobuf**. It's Google's format for messages: a typed schema, and a small binary encoding.
3. **`.proto` file**: This is the file where the services and messages are described. It's the contract.
4. **Message**: This is a typed record, like `Dish`, with numbered fields.
5. **Field number**: This is the number each field has in the `.proto` (`name = 2`). On the wire only the numbers are sent, never the names.
6. **Stub**: This is the generated client code: a Go type whose methods make the remote calls.
7. **Interceptor**: This is gRPC's middleware. It wraps every call on the server (or client), to log, recover panics or turn errors into statuses.
8. **Deadline**: This is the moment a call must be finished by. It's sent with the call, so the server knows it too.
9. **Status code**: This is gRPC's version of an HTTP status: `OK`, `NOT_FOUND`, `INVALID_ARGUMENT`, `UNAVAILABLE` and so on.
10. **Streaming**: This is when one call carries many messages instead of one: from the server, from the client, or both.

## Step 1: what gRPC gives you
<!-- bite: b635a046-a06e-4073-af6f-829e863cc89d -->

| | REST + JSON | gRPC |
|---|---|---|
| Contract | Optional (OpenAPI, which we wrote in lesson 11) | Required: the `.proto` file is the API |
| Message size | Text, field names repeated | Binary, field numbers, much smaller |
| Speed | Parse JSON on each side | Fast binary encoding, one HTTP/2 connection carrying many calls at once |
| Timeouts | You remember to add them | Deadlines are part of every call, and travel to the next service |
| Streaming | SSE (one way), WebSockets | Built in, both directions |
| Generated clients | Optional | In almost every language from the same `.proto` |
| Browsers | Natively | Not directly; needs a proxy or gRPC-Web |
| Reading it by hand | `curl` and your eyes | Needs tools; the bytes aren't readable |

Those last two rows are why gRPC is mostly *between services*: browsers can't speak plain gRPC, and you can't debug it by looking at it. For internal calls, nobody needs to read it by hand, and every other row is a win.

In Go, the deadline row is even better than it sounds. A gRPC deadline arrives on the server as the **`context.Context`** of the call, the same kind of context we've passed to every database query since lesson 8. So when a caller gives up, our Postgres query is cancelled too, with no extra code.

## Step 2: the `.proto` file
<!-- bite: 0de501f4-c70d-4e4e-a514-75192c0212b3 -->

`proto/mamaput/menu/v1/menu.proto`:

```proto
syntax = "proto3";

package mamaput.menu.v1;

option go_package = "mamaput/internal/gen/mamaput/menu/v1;menuv1";

// Read-only menu access for Mama Put's own services.
service MenuService {
  // One dish by ID. NOT_FOUND if there's no such dish.
  rpc GetDish(GetDishRequest) returns (GetDishResponse);

  // Many dishes at once, at most 100 IDs. Unknown IDs are left out of the response.
  rpc BatchGetDishes(BatchGetDishesRequest) returns (BatchGetDishesResponse);

  // Sends a message each time a dish's portions change, until the caller hangs up.
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
2. **`option go_package`**: where the generated Go goes, and what its package is called. Before the `;` is the import path (`mamaput/internal/gen/mamaput/menu/v1`); after it is the package name, `menuv1`. Every Go project with protobuf uses names like `menuv1`, so `v1` and `v2` can be imported side by side.
3. **Every RPC has its own request and its own response message**, even when the request is one ID and the response is one dish. `GetDishRequest` can gain fields later, and so can `GetDishResponse` (a "this dish is new" flag, say). A bare `Dish` as the response couldn't. `buf lint` insists on this, and on the names: `GetDish` takes `GetDishRequest` and returns `GetDishResponse`.
4. **`repeated`** means a list.
5. **`int64` for money and IDs.** Kobo can grow past what `int32` holds (about ₦21 million), and money must never overflow. In Go, `int64` is just `int64`. (In JavaScript it isn't, which is why the Express lesson sends prices as strings. One less problem here.)
6. **`optional`** means "may be absent, and you can tell". Without it, a missing `string` reads as `""`, and you can't tell "no photo" from "a photo with an empty name". In Go, an `optional string` becomes a `*string`: `nil` means absent.
7. **Field names are `snake_case`** by protobuf convention. The Go generator turns `price_kobo` into `PriceKobo`.
8. **Comments are documentation.** The `.proto` file is the contract other teams read, so it says what each call does and what errors it gives.

Where does the file live? In this repository for now, in its own `proto/` folder, outside `internal/`. It isn't Go; it's the contract. When there are several services in several repositories, teams often move `.proto` files to a shared one, so every service builds from the same copy.

## Step 3: generating Go
<!-- bite: d264e70b-11e5-4863-968a-d806df490ae1 -->

Two small config files at the root of the module. `buf.yaml` says where the `.proto` files are and which rules to check:

```yaml
version: v2
modules:
  - path: proto
lint:
  use:
    - STANDARD
breaking:
  use:
    - FILE
```

`buf.gen.yaml` says which generators to run:

```yaml
version: v2
plugins:
  - local: ["go", "tool", "protoc-gen-go"]
    out: internal/gen
    opt: paths=source_relative
  - local: ["go", "tool", "protoc-gen-go-grpc"]
    out: internal/gen
    opt: paths=source_relative
```

`local: ["go", "tool", "protoc-gen-go"]` is the useful trick: buf runs the generator through `go tool`, at the version in `go.mod`, so nobody needs it installed anywhere else. `paths=source_relative` means `proto/mamaput/menu/v1/menu.proto` becomes `internal/gen/mamaput/menu/v1/...`, the same folders under a different root.

Then:

```bash
go tool buf lint
go tool buf generate
```

`lint` prints nothing when the file follows the rules. `generate` writes two files:

1. **`internal/gen/mamaput/menu/v1/menu.pb.go`**: a Go struct for every message (`menuv1.Dish`, `menuv1.GetDishRequest`, ...), with the code to encode and decode them, and a getter for every field: `GetName()`, `GetPriceKobo()`.
2. **`internal/gen/mamaput/menu/v1/menu_grpc.pb.go`**: the service in Go. A `MenuServiceServer` interface for us to implement, a `MenuServiceClient` for callers, `RegisterMenuServiceServer` and `NewMenuServiceClient`.

The server interface it wrote:

```go
type MenuServiceServer interface {
	GetDish(context.Context, *GetDishRequest) (*GetDishResponse, error)
	BatchGetDishes(context.Context, *BatchGetDishesRequest) (*BatchGetDishesResponse, error)
	WatchPortions(*WatchPortionsRequest, grpc.ServerStreamingServer[WatchPortionsResponse]) error
	mustEmbedUnimplementedMenuServiceServer()
}
```

Ordinary Go: a context first, a request pointer in, a response pointer and an `error` out. Like gqlgen's files, these are never edited by hand.

buf has to run from the module root, where `buf.yaml` is, so instead of a `//go:generate` line, the `Makefile`'s `generate` target gets one more command:

```makefile
generate:
	go generate ./...
	go tool buf generate
```

`make generate` now regenerates OpenAPI types, GraphQL and gRPC together.

**Use the getters.** `req.GetId()` instead of `req.Id`. Getters work on a `nil` message (they return the zero value), so `res.GetDish().GetName()` can never panic, even when `Dish` is missing. Reaching through fields would.

## Step 4: the server
<!-- bite: 666e1df5-9560-451e-b81a-3748763415bb -->

`internal/grpcapi/menu.go`:

```go
// Package grpcapi serves Mama Put's gRPC API, for our own services.
package grpcapi

import (
	"context"

	"mamaput/internal/apperr"
	menuv1 "mamaput/internal/gen/mamaput/menu/v1"
	"mamaput/internal/menu"
)

// Menu is what the gRPC menu service needs from the menu package.
type Menu interface {
	Get(ctx context.Context, id int64) (menu.Dish, error)
	Many(ctx context.Context, ids []int64) ([]menu.Dish, error)
}

// Portions is a feed of portion changes (lesson 20's hub idea, for dishes).
type Portions interface {
	Subscribe() (<-chan menu.PortionsChanged, func())
}

type MenuServer struct {
	menuv1.UnimplementedMenuServiceServer
	menu     Menu
	portions Portions
}

func NewMenuServer(m Menu, p Portions) *MenuServer {
	return &MenuServer{menu: m, portions: p}
}

var (
	errBadID   = apperr.New(apperr.Invalid, "bad-id", "IDs are positive whole numbers.")
	errTooMany = apperr.New(apperr.Invalid, "too-many-ids", "Ask for at most 100 dishes per call.")
)

func (s *MenuServer) GetDish(ctx context.Context, req *menuv1.GetDishRequest) (*menuv1.GetDishResponse, error) {
	if req.GetId() < 1 {
		return nil, errBadID
	}
	d, err := s.menu.Get(ctx, req.GetId())
	if err != nil {
		return nil, err
	}
	return &menuv1.GetDishResponse{Dish: toProto(d)}, nil
}

func (s *MenuServer) BatchGetDishes(ctx context.Context, req *menuv1.BatchGetDishesRequest) (*menuv1.BatchGetDishesResponse, error) {
	ids := req.GetIds()
	if len(ids) > 100 {
		return nil, errTooMany
	}
	for _, id := range ids {
		if id < 1 {
			return nil, errBadID
		}
	}
	dishes, err := s.menu.Many(ctx, ids)
	if err != nil {
		return nil, err
	}
	out := &menuv1.BatchGetDishesResponse{Dishes: make([]*menuv1.Dish, 0, len(dishes))}
	for _, d := range dishes {
		out.Dishes = append(out.Dishes, toProto(d))
	}
	return out, nil
}

func toProto(d menu.Dish) *menuv1.Dish {
	out := &menuv1.Dish{
		Id:           d.ID,
		Name:         d.Name,
		PriceKobo:    int64(d.Price),
		Available:    d.Available,
		PortionsLeft: int32(d.PortionsLeft),
	}
	if d.PhotoThumb != "" {
		url := "/photos/" + d.PhotoThumb
		out.ThumbnailUrl = &url
	}
	return out
}
```

The same lesson again: the handlers are **thin**. `s.menu.Get` is the menu service from lesson 4, with lesson 19's cache in front of it, and `Many` is the one lesson 21 added for the dataloader. REST, GraphQL and gRPC are three doors into one kitchen.

Things to notice:

1. **`menuv1.UnimplementedMenuServiceServer` is embedded.** The generated interface has a hidden method, `mustEmbedUnimplementedMenuServiceServer`, so you *must* embed this. It gives every RPC a default that answers `UNIMPLEMENTED`. The point is the future: when someone adds a `ListSpecials` RPC to the `.proto` and regenerates, our server still compiles, and callers of the new RPC get a clear `UNIMPLEMENTED` until we write it. Embed it **by value**, as here, not as a pointer (a `nil` pointer would panic when one of its methods is called; the generated code checks for this when you register).
2. **`toProto` is the presenter.** Like lesson 10's wire types, the message is its own type, separate from `menu.Dish`. The domain type can change without changing the contract.
3. **Input is still checked at the door** (lesson 6). The `.proto` guarantees `id` is an `int64`; it doesn't guarantee it's a sensible one. A missing `id` arrives as `0`, since proto3 fields without `optional` can't be absent, so `< 1` catches both "zero" and "not sent". And lists get limits, like every list in every API.
4. **Handlers return our own errors.** `errBadID` is an `*apperr.Error`, and `s.menu.Get` returns `menu.ErrDishNotFound` as always. Turning those into gRPC statuses is one interceptor's job, in step 5, so it can't be forgotten in one handler.

### The server itself

`internal/grpcapi/server.go`:

```go
package grpcapi

import (
	"log/slog"

	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthpb "google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"

	menuv1 "mamaput/internal/gen/mamaput/menu/v1"
)

type Options struct {
	Production bool
}

// NewServer builds the gRPC server with every service on it. The caller starts it.
func NewServer(log *slog.Logger, m *MenuServer, opt Options) *grpc.Server {
	srv := grpc.NewServer(
		grpc.ChainUnaryInterceptor(Log(log), Errors(log), Recover(log)),
		grpc.ChainStreamInterceptor(StreamErrors(log)),
		grpc.MaxRecvMsgSize(1<<20),
	)
	menuv1.RegisterMenuServiceServer(srv, m)

	healthpb.RegisterHealthServer(srv, health.NewServer())
	if !opt.Production {
		reflection.Register(srv)
	}
	return srv
}
```

1. **`ChainUnaryInterceptor(Log, Errors, Recover)`** is lesson 3's middleware chain, for gRPC. The first is the outermost: `Log` sees the final status, after `Errors` has converted it; `Recover` is closest to the handler, so it catches its panics. Unary calls (one request, one response) and streaming calls have separate chains.
2. **`MaxRecvMsgSize(1<<20)`**: the most a single incoming message may be, 1 MB. (4 MB is grpc-go's default; our requests are a few bytes.) Lesson 6's size limit, again.
3. **The health service** is gRPC's standard "are you alive?" RPC. Lesson 28's Docker health checks and load balancers know how to ask it.
4. **Reflection** lets tools ask the server for its own `.proto`, so `grpcurl` works without being given the file. Handy in development; off in production for the same reason as GraphQL introspection.

### Running it beside the HTTP server

In `cmd/api/main.go`'s `run`, after the services are built:

```go
lis, err := net.Listen("tcp", getenv("GRPC_ADDR")) // "127.0.0.1:50051" in development
if err != nil {
	return fmt.Errorf("grpc listen: %w", err)
}
grpcSrv := grpcapi.NewServer(logger, grpcapi.NewMenuServer(menuService, portions),
	grpcapi.Options{Production: production})
go func() {
	if err := grpcSrv.Serve(lis); err != nil {
		logger.Error("grpc server stopped", "error", err)
	}
}()
defer grpcSrv.GracefulStop()
logger.Info("grpc listening", "addr", lis.Addr().String())
```

Two ports now: 8080 for the outside world (REST, GraphQL, webhooks), 50051 for our own services. **50051 is never exposed to the internet**: `127.0.0.1` means only programs on this machine can connect, and in lesson 28, Docker only lets other containers reach it. There's no TLS and no login on it yet. That's acceptable for this lesson on one laptop; lesson 26 adds authentication between services, before anything else calls it.

`GracefulStop` stops taking new calls and waits for running ones to finish, the gRPC version of `http.Server.Shutdown`. Lesson 28 puts both shutdowns together properly, with a time limit, because `GracefulStop` waits for streams too, and a `WatchPortions` stream never finishes by itself.

`portions` is a feed built exactly like lesson 20's `Hub` and `Events`, on a Redis channel called `portions`, with the orders service publishing after every order and every restock. You've written that code once already, so it's in the practice.

## Step 5: errors as status codes
<!-- bite: e4f4df38-1864-4320-856f-e3453037820c -->

gRPC has its own small set of status codes. Our `apperr` kinds map onto them. `internal/grpcapi/errors.go`:

```go
package grpcapi

import (
	"context"
	"errors"
	"log/slog"
	"runtime/debug"

	"google.golang.org/genproto/googleapis/rpc/errdetails"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"mamaput/internal/apperr"
)

// codeFor is lesson 7's statusFor, for gRPC.
var codeFor = map[apperr.Kind]codes.Code{
	apperr.Invalid:         codes.InvalidArgument,
	apperr.Unauthenticated: codes.Unauthenticated,
	apperr.Forbidden:       codes.PermissionDenied,
	apperr.NotFound:        codes.NotFound,
	apperr.Conflict:        codes.Aborted,
	apperr.RuleBroken:      codes.FailedPrecondition,
	apperr.Upstream:        codes.Unavailable,
	apperr.TooLarge:        codes.ResourceExhausted,
}

// toStatus turns any error into a gRPC status a caller may see.
func toStatus(ctx context.Context, log *slog.Logger, err error) error {
	if err == nil {
		return nil
	}
	if _, ok := status.FromError(err); ok {
		return err // already a status, e.g. from Recover
	}
	switch {
	case errors.Is(err, context.Canceled):
		return status.Error(codes.Canceled, "the caller cancelled")
	case errors.Is(err, context.DeadlineExceeded):
		return status.Error(codes.DeadlineExceeded, "the caller's deadline passed")
	}

	var appErr *apperr.Error
	if errors.As(err, &appErr) {
		if code, ok := codeFor[appErr.Kind]; ok {
			st := status.New(code, appErr.Message)
			withInfo, derr := st.WithDetails(&errdetails.ErrorInfo{Domain: "mamaput", Reason: appErr.Code})
			if derr == nil {
				return withInfo.Err()
			}
			return st.Err()
		}
	}
	log.ErrorContext(ctx, "grpc call failed", "error", err)
	return status.Error(codes.Internal, "internal error")
}

// Errors is a unary interceptor: handlers return our errors, callers get statuses.
func Errors(log *slog.Logger) grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
		resp, err := handler(ctx, req)
		return resp, toStatus(ctx, log, err)
	}
}

// StreamErrors does the same for streaming calls.
func StreamErrors(log *slog.Logger) grpc.StreamServerInterceptor {
	return func(srv any, ss grpc.ServerStream, info *grpc.StreamServerInfo, handler grpc.StreamHandler) error {
		return toStatus(ss.Context(), log, handler(srv, ss))
	}
}

// Recover turns a panic in a handler into INTERNAL, instead of killing the server.
func Recover(log *slog.Logger) grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (resp any, err error) {
		defer func() {
			if p := recover(); p != nil {
				log.ErrorContext(ctx, "grpc handler panicked", "method", info.FullMethod, "panic", p, "stack", string(debug.Stack()))
				err = status.Error(codes.Internal, "internal error")
			}
		}()
		return handler(ctx, req)
	}
}

// Log records each call, like lesson 3's LogRequests.
func Log(log *slog.Logger) grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req any, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
		resp, err := handler(ctx, req)
		log.InfoContext(ctx, "grpc", "method", info.FullMethod, "code", status.Code(err).String())
		return resp, err
	}
}
```

How it fits together:

1. **An interceptor is a function wrapped around the handler.** It gets the context, the request, `info` (which RPC this is: `info.FullMethod` is `/mamaput.menu.v1.MenuService/GetDish`) and `handler`, the next step. It calls `handler`, and can look at or change what comes back. Exactly lesson 3's `func(http.Handler) http.Handler`, with a different shape.
2. **One of ours** becomes the matching code, with our message. Our stable code (`dish-not-found`) goes into an **`ErrorInfo` detail**: a standard protobuf message from Google for exactly this, which any gRPC client in any language can read. A caller can tell `dish-not-found` from any other `NOT_FOUND`.
3. **A cancelled or timed-out call** gets `CANCELED` or `DEADLINE_EXCEEDED`, not `INTERNAL`. When a caller gives up, the context cancels our database query, the query returns `context.Canceled`, and that's not a bug on our side. `errors.Is` finds it even when pgx has wrapped it.
4. **Anything else is hidden**: `INTERNAL` with "internal error", and the real error in our log. In the test, a fake store fails with `pgx: connection refused 10.0.0.3`; the caller never sees the address.
5. **`Recover` uses a named result, `(resp any, err error)`.** A deferred function can change a named result after a panic, which is how a panic turns into a returned `INTERNAL`. Without this interceptor, a panic in a gRPC handler **crashes the whole program**, HTTP server and all: grpc-go doesn't recover panics for you, unlike `net/http`, which at least catches them per connection.

The `codeFor` map has the same weakness as lesson 13's policy map: a new `apperr.Kind` with no entry here falls through to `INTERNAL`. Safe, but silent. Add a test that loops over every kind and checks it has a code, like lesson 13's `TestEveryActionHasARule`.

`UNAVAILABLE` has a special meaning: "try again, this is temporary". Lesson 26's retries will retry only that one. Use it only for things that really are temporary (Paystack down, the database restarting), never for "you sent something wrong".

## Step 6: calling it
<!-- bite: 25bf728d-e65a-4047-9e15-6a446d79f605 -->

**From the command line.** Start the API, and with reflection on, grpcurl can find everything by itself:

```bash
grpcurl -plaintext 127.0.0.1:50051 list
```

```text
grpc.health.v1.Health
grpc.reflection.v1.ServerReflection
grpc.reflection.v1alpha.ServerReflection
mamaput.menu.v1.MenuService
```

```bash
grpcurl -plaintext -d '{"id": 1}' 127.0.0.1:50051 mamaput.menu.v1.MenuService/GetDish
```

```json
{
  "dish": {
    "id": "1",
    "name": "Jollof rice",
    "priceKobo": "150000",
    "available": true,
    "portionsLeft": 12
  }
}
```

grpcurl shows the binary answer as JSON, using protobuf's standard JSON rules: names in `camelCase`, and `int64` written as a string (`"150000"`), because JavaScript can't hold every `int64` exactly. On the wire it's a few bytes of binary, and in Go it's an `int64`.

Try `{"id": 999}` and see `Code: NotFound` with `"reason": "dish-not-found"` in the details, and `{"id": 0}` for `InvalidArgument`. Okay!!!!! The menu speaks gRPC.

**From Go.** This is what the notifications service will do in lesson 25, and what the test does:

```go
conn, err := grpc.NewClient("127.0.0.1:50051",
	grpc.WithTransportCredentials(insecure.NewCredentials()))
if err != nil {
	return err
}
defer conn.Close()
menuClient := menuv1.NewMenuServiceClient(conn)

// every call, a deadline
ctx, cancel := context.WithTimeout(ctx, 500*time.Millisecond)
defer cancel()
res, err := menuClient.GetDish(ctx, &menuv1.GetDishRequest{Id: 1})
switch status.Code(err) {
case codes.OK:
	fmt.Println(res.GetDish().GetName()) // Jollof rice
case codes.NotFound:
	// the dish was deleted; write the message without its name
default:
	return fmt.Errorf("get dish: %w", err)
}
```

1. **`grpc.NewClient`** makes a client connection. It doesn't connect yet; it connects on the first call, and reconnects by itself if the connection drops. (Older code uses `grpc.Dial`, which is deprecated.) **Make it once and share it**: one connection carries many calls at the same time over HTTP/2. A new connection per call throws that away.
2. **`insecure.NewCredentials()`** means no TLS. Fine on one machine; lesson 26 changes it.
3. **The deadline is the context.** `context.WithTimeout(ctx, 500*time.Millisecond)`: if there's no answer in half a second, the call fails with `DEADLINE_EXCEEDED`. gRPC sends the deadline to the server, where it becomes the deadline of the handler's `ctx`, which our services pass to Postgres. Nobody keeps working on an answer nobody's waiting for. And if the notifications service was itself handling something with a deadline, passing its `ctx` along means the menu call can never outlive it. Deadlines **travel**, which is the key idea of lesson 26.
4. **`status.Code(err)`** reads the code from any error: `OK` for `nil`, `UNKNOWN` for an error that isn't a status. The `ErrorInfo` reason is in `status.Convert(err).Details()`.
5. **`defer cancel()`** is required. A context with a timeout holds a timer until it's cancelled; forgetting `cancel` leaks it, and `go vet` warns you.

## Step 7: streaming
<!-- bite: 5003a304-f2d0-4e8e-991b-3b81bbb0fc5d -->

`WatchPortions` returns `stream WatchPortionsResponse`: one request, then many messages, until someone hangs up. It's lesson 20's SSE idea, for services:

```go
func (s *MenuServer) WatchPortions(req *menuv1.WatchPortionsRequest, stream menuv1.MenuService_WatchPortionsServer) error {
	wanted := map[int64]bool{}
	for _, id := range req.GetDishIds() {
		wanted[id] = true
	}
	changes, unsubscribe := s.portions.Subscribe()
	defer unsubscribe()

	for {
		select {
		case <-stream.Context().Done():
			return nil // the caller hung up, or its deadline passed
		case c, ok := <-changes:
			if !ok {
				return apperr.New(apperr.Upstream, "too-slow", "You fell behind; call WatchPortions again.")
			}
			if len(wanted) > 0 && !wanted[c.DishID] {
				continue
			}
			err := stream.Send(&menuv1.WatchPortionsResponse{DishId: c.DishID, PortionsLeft: int32(c.Left)})
			if err != nil {
				return err
			}
		}
	}
}
```

Compare it with lesson 20's kitchen stream: subscribe, then `select` on "the caller went away" and "an event arrived", `defer unsubscribe()` so nothing leaks, and a feed that drops listeners who fall too far behind. The differences are small:

1. **`stream.Send`** writes one message and flushes it. No SSE format, no `ResponseController`: gRPC frames each message itself.
2. **No heartbeat.** HTTP/2 has its own keepalive pings; grpc-go's `keepalive` server options control them, and lesson 28 sets them for the proxy.
3. **A dropped listener gets `UNAVAILABLE`**, through `StreamErrors`, which tells a well-written caller "call again". Lesson 20's screen reconnected by itself; here the caller's code does it, in a loop with a short wait.

On the client, a stream is a loop over `Recv`:

```go
stream, err := menuClient.WatchPortions(ctx, &menuv1.WatchPortionsRequest{DishIds: []int64{1}})
if err != nil {
	return err
}
for {
	msg, err := stream.Recv()
	if err != nil {
		return err // io.EOF when the server ends the stream cleanly
	}
	fmt.Println(msg.GetDishId(), msg.GetPortionsLeft())
}
```

No timeout on this `ctx`: a watch is meant to stay open. Cancelling the context is how the caller hangs up.

gRPC can stream in both directions too (`stream` on the request *and* the response), for things like a chat or a live game. We won't need it.

## Step 8: changing a `.proto` safely
<!-- bite: ad164f40-85a0-482c-b1c6-8ef62846f42c -->

Every service that talks to this one was built from the same `.proto`. When you change it, old and new versions run side by side for a while, because you can't redeploy every service at the same instant. Protobuf is designed for that, as long as you follow its rules, which are [[backend/frameworks/net-http/10-versioning|lesson 10]]'s rules, made precise:

**Safe:**

1. **Add a new field with a new number.** Old readers skip numbers they don't know. Old writers don't send it, so new readers get its zero value.
2. **Add a new RPC.** Old clients just don't call it, and old servers answer `UNIMPLEMENTED` (thanks to the embedded struct from step 4).
3. **Rename a field.** The wire only has numbers, so the bytes don't change. (Your Go code changes, because `PriceKobo` becomes a different name; and anything using the JSON form, like grpcurl, sees the new name.)

**Breaking:**

1. **Changing a field's number**, or **reusing an old number** for something new. Old services read the new data as the old field. It's the worst kind of bug: no error, just wrong data.
2. **Changing a field's type** (`int32` to `string`).
3. **Removing a field** without reserving its number.
4. **Changing what a field means** (kobo to naira, the most dangerous, again).

When you remove a field, reserve it, so nobody reuses it by accident:

```proto
message Dish {
  reserved 6;
  reserved "thumbnail_url";
  // ...
}
```

The compiler then refuses any new field numbered 6 or named `thumbnail_url`.

You don't have to remember all this: **`buf breaking`** compares the `.proto` files with an earlier version and lists every breaking change. I tried it by changing `price_kobo = 3` to `price_kobo = 7`:

```bash
go tool buf breaking --against '.git#branch=main'
```

```text
proto/mamaput/menu/v1/menu.proto:35:1:Previously present field "3" with name "price_kobo" on message "Dish" was deleted.
```

`--against '.git#branch=main'` means "compare with the `proto` files as they are on `main`". A non-empty answer exits with an error, so in lesson 29's pipeline it fails the build. For a change that really must break, make `mamaput.menu.v2` in `proto/mamaput/menu/v2/`, serve both, move callers over, and retire `v1`, exactly like lesson 10.

## Step 9: testing
<!-- bite: 0f523a1b-8f13-41cc-9875-69c8853ce128 -->

gRPC tests don't need a real port. **`bufconn`** (from grpc-go's `test/bufconn` package) is a network listener that lives entirely in memory: the server listens on it, the client dials it, and everything between them is real gRPC, interceptors and all. `internal/grpcapi/menu_test.go`:

```go
func client(t *testing.T, m Menu, p Portions) menuv1.MenuServiceClient {
	t.Helper()
	lis := bufconn.Listen(1 << 20)
	srv := NewServer(slog.New(slog.NewTextHandler(io.Discard, nil)), NewMenuServer(m, p), Options{})
	go srv.Serve(lis)
	t.Cleanup(srv.Stop)

	conn, err := grpc.NewClient("passthrough:///bufnet",
		grpc.WithContextDialer(func(ctx context.Context, _ string) (net.Conn, error) { return lis.DialContext(ctx) }),
		grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { conn.Close() })
	return menuv1.NewMenuServiceClient(conn)
}

func reason(err error) string {
	for _, d := range status.Convert(err).Details() {
		if info, ok := d.(*errdetails.ErrorInfo); ok {
			return info.Reason
		}
	}
	return ""
}

func TestGetDishNotFound(t *testing.T) {
	c := client(t, fakeMenu{}, &fakeFeed{})

	_, err := c.GetDish(t.Context(), &menuv1.GetDishRequest{Id: 99})

	if status.Code(err) != codes.NotFound || reason(err) != "dish-not-found" {
		t.Fatalf("got %v (reason %q), want NOT_FOUND dish-not-found", err, reason(err))
	}
}

func TestDeadlineReachesTheServer(t *testing.T) {
	c := client(t, fakeMenu{delay: time.Second}, &fakeFeed{})
	ctx, cancel := context.WithTimeout(t.Context(), 100*time.Millisecond)
	defer cancel()

	start := time.Now()
	_, err := c.GetDish(ctx, &menuv1.GetDishRequest{Id: 1})

	if status.Code(err) != codes.DeadlineExceeded {
		t.Fatalf("got %v, want DEADLINE_EXCEEDED", err)
	}
	if took := time.Since(start); took > 300*time.Millisecond {
		t.Fatalf("took %v; the deadline didn't work", took)
	}
}
```

`passthrough:///bufnet` is a made-up address; `passthrough` tells grpc-go not to look the name up, and `WithContextDialer` hands it our in-memory connection instead. The fake menu's slow `Get` waits on `ctx.Done()`, like a real query does, so the deadline test proves the whole chain: the client's timeout travels to the server, the server's context ends, and the "query" stops.

What to test:

1. A dish comes back, with `ThumbnailUrl` `nil` when there's no photo.
2. An unknown ID gives `NOT_FOUND` with reason `dish-not-found`; ID 0 gives `INVALID_ARGUMENT`; 101 IDs give `too-many-ids`.
3. A fake store failing with an address inside gives `INTERNAL` with "internal error", and nothing more.
4. A handler that panics gives `INTERNAL`, and the server keeps answering the next call.
5. The deadline test above: about 100 milliseconds, not 1 second.
6. `WatchPortions` for dish 1 receives dish 1's change and not dish 2's.
7. Every `apperr.Kind` has an entry in `codeFor`.

All of these ran under `-race` while I wrote this lesson, in about a second.

## The Go in this lesson
<!-- bite: 6fadbbbb-3ba0-4424-97a8-475db56916ca -->

1. **`go get -tool` for three tools**, and buf's `local: ["go", "tool", "protoc-gen-go"]`: Generators run at the versions in `go.mod`, with nothing installed globally.
2. **`option go_package = "path;name"`**: The import path and package name of the generated code. Names like `menuv1` let versions sit side by side.
3. **Generated getters, `req.GetId()`**: Safe on `nil` messages, returning the zero value. Prefer them to reading fields.
4. **`optional string` becomes `*string`**: `nil` means "not sent".
5. **Embedding `menuv1.UnimplementedMenuServiceServer` by value**: Gives every RPC a default answer, so adding RPCs to the `.proto` never breaks the build.
6. **Interceptors**: `grpc.UnaryServerInterceptor` is `func(ctx, req any, info, handler) (any, error)`. `grpc.ChainUnaryInterceptor` runs them outermost first.
7. **`status.New(code, msg).WithDetails(&errdetails.ErrorInfo{...})`**: A status with a typed detail attached. `status.Code(err)` and `status.Convert(err).Details()` read them back.
8. **A named result changed by `defer`**: `func(...) (resp any, err error)`, with `err = ...` inside a deferred `recover`. The only way to turn a panic into a return value.
9. **`grpc.NewClient`**, once, shared: It connects lazily and carries many calls on one HTTP/2 connection.
10. **`context.WithTimeout` as the deadline**: The same context as everywhere else, sent to the server with the call.
11. **Generics in generated code, `grpc.ServerStreamingServer[WatchPortionsResponse]`**: A stream whose `Send` only takes that message type.
12. **`d.(*errdetails.ErrorInfo)`**: A type assertion with `ok`, picking one kind of detail out of a list of `any`.
13. **`bufconn.Listen`** and **`grpc.WithContextDialer`**: A real gRPC server and client, connected in memory, for tests.
14. **`defer grpcSrv.GracefulStop()`**: Stop taking calls and finish the running ones when `run` returns.

## Your project so far
<!-- bite: 9facec87-ba51-4130-a9b5-96f698869c8f -->

```text
mama-put/
├── go.mod                         ← tools: buf, protoc-gen-go, protoc-gen-go-grpc; google.golang.org/grpc
├── buf.yaml                       ← NEW: where the protos are; lint STANDARD; breaking FILE
├── buf.gen.yaml                   ← NEW: the two Go generators, run through go tool
├── Makefile                       ← generate runs buf generate too; lint runs buf lint
├── proto/
│   └── mamaput/menu/v1/
│       └── menu.proto             ← NEW: MenuService: GetDish, BatchGetDishes, WatchPortions
├── cmd/
│   └── api/main.go                ← listens on GRPC_ADDR (127.0.0.1:50051), Serve in a goroutine, GracefulStop
└── internal/
    ├── gen/mamaput/menu/v1/       ← GENERATED: menu.pb.go, menu_grpc.pb.go — never edit
    ├── grpcapi/                   ← NEW package
    │   ├── menu.go                ← MenuServer: thin calls into the menu service; toProto; WatchPortions
    │   ├── errors.go              ← codeFor, toStatus with ErrorInfo, Errors, StreamErrors, Recover, Log
    │   ├── server.go              ← NewServer: interceptor chains, size limit, health, reflection outside production
    │   └── menu_test.go           ← bufconn: dishes, NOT_FOUND reasons, hidden errors, panics, deadlines, streams
    └── menu/
        └── portions.go            ← NEW: PortionsChanged, and the Redis feed (practice)
```

## Common mistakes
<!-- bite: d76dbcce-69ee-4ec7-aac9-546cb7e1f49c -->

1. **Business rules in gRPC handlers.** The three APIs drift apart. Handlers call services.
2. **No deadline on a call.** It can wait forever, holding a goroutine and a connection. Every call gets `context.WithTimeout`, or a context that already has a deadline.
3. **A new client connection per call.** One `grpc.NewClient`, made at start-up and shared.
4. **Changing or reusing a field number.** Silent data corruption. Add new numbers; `reserved` old ones; run `buf breaking`.
5. **Returning a bare message type from an RPC.** It can never grow. Every RPC gets its own request and response, as `buf lint` insists.
6. **No `Recover` interceptor.** A panic in a gRPC handler takes the whole program down.
7. **Sending internal errors to callers.** `INTERNAL` with a plain message; the details go to the log.
8. **`UNAVAILABLE` for a bad request.** Callers will retry it forever. Only temporary problems are `UNAVAILABLE`.
9. **Reading fields instead of using getters.** `res.Dish.Name` panics when `Dish` is `nil`; `res.GetDish().GetName()` doesn't.
10. **The gRPC port open to the internet.** It's for our own services; bind to `127.0.0.1` or a private network, and add authentication (lesson 26).
11. **Editing generated code.** The next `buf generate` throws it away.

## Check your understanding
<!-- bite: 2f861154-0454-4e5e-9011-4ad702d2caad -->

1. Why does `GetDish` return a `GetDishResponse` with a `Dish` inside, instead of a `Dish`?
2. What happens on the wire if someone changes `price_kobo = 3` to `price_kobo = 7` and only the API is redeployed? How would you have been warned?
3. The notifications service calls `GetDish` with a 500 ms deadline, and the menu's database query is slow today. Follow what happens on both sides.
4. Why does `toStatus` check for `context.Canceled` before anything else, instead of letting it become `INTERNAL`?
5. Why must `MenuServer` embed `UnimplementedMenuServiceServer`, and what does it buy you next month?
6. What does `bufconn` give a test that calling `MenuServer.GetDish` directly wouldn't?

<details>
<summary>Answers, after your attempt</summary>

1. So the response can grow. Next month `GetDishResponse` can gain a field without touching `Dish` or breaking anyone. A bare `Dish` as the response would make that impossible without a new RPC. `buf lint`'s STANDARD rules insist on it.
2. The new API sends the price under number 7. The old notifications service doesn't know 7, so it skips it, and reads field 3 as missing: every price is 0, with no error anywhere. `buf breaking` would have reported "Previously present field 3 ... was deleted" and failed the build.
3. The client sends the deadline with the call. On the server, the handler's `ctx` has the same deadline; the menu service passes it to pgx. After 500 ms the client stops waiting and gets `DEADLINE_EXCEEDED`; at the same moment the server's context ends, pgx cancels the query, and the handler returns `context.DeadlineExceeded`, which `toStatus` turns into `DEADLINE_EXCEEDED` rather than an `INTERNAL` error in the logs.
4. Because a caller giving up isn't a bug on our side. Reporting it as `INTERNAL` would fill the logs with false alarms and make lesson 27's error rate lie. `errors.Is` finds it even when the database driver has wrapped it.
5. The generated interface has a hidden method only the embedded struct provides, so it won't compile without it. Next month, when someone adds an RPC to the `.proto` and regenerates, the server still compiles, and the new RPC answers `UNIMPLEMENTED` until it's written.
6. Real gRPC between a real client and server: the interceptors run (so errors become statuses and panics are recovered), messages are encoded and decoded, and deadlines travel. A direct call would test the handler alone, with our raw `apperr` coming straight back.

</details>

## Practice
<!-- bite: d3cddd12-a2a5-44fc-b55c-c7e8bfa3263a -->

1. Write the tests from step 9, including the panic test (the server still answers after it) and the `codeFor` completeness test.
2. Build the portions feed: `menu.PortionsFeed` with `Publish` and `Listen` on a Redis channel called `portions`, like lesson 20's `Events`, and a hub like lesson 20's `Hub`. Publish from the orders service after every order, and from the menu service when staff change portions. Check with `grpcurl -plaintext -d '{"dishIds":[1]}' 127.0.0.1:50051 mamaput.menu.v1.MenuService/WatchPortions` while you place orders with `curl`.
3. Add a stream interceptor that recovers panics, the streaming twin of `Recover`.
4. Add `ListSpecials(ListSpecialsRequest) returns (ListSpecialsResponse)` to the `.proto`. Run `buf lint` and `buf breaking` (adding an RPC isn't breaking), regenerate, and watch the server still compile before you've written the method.
5. Add `make proto-check` that runs `go tool buf lint` and `go tool buf breaking --against '.git#branch=main'`, ready for lesson 29's pipeline.

**Done when** `grpcurl` lists `mamaput.menu.v1.MenuService` and `GetDish` returns a dish; unknown and bad IDs give `NOT_FOUND` and `INVALID_ARGUMENT` with their reasons; a 100 ms deadline on a slow call fails in about 100 ms; a watch receives changes as orders are placed; changing a field number makes `make proto-check` fail; and `make test` passes with `-race`.

## Before moving on
<!-- bite: 367e6a67-7454-48fc-ae63-c5683ec38ccc -->

Mama Put API now has three doors: REST for everyone, GraphQL for the phone app, and gRPC for our own services, all on the same services underneath. The `.proto` is a contract that tools check for you, every call carries a deadline that travels as a Go context, and a slow database is cancelled the moment nobody's waiting.

All three doors are made for programs written by people who know what they're asking for. The next kind of client is different: an **AI assistant**. Ada asks her assistant "order me two plates of jollof from Mama Put", and the assistant needs to find the menu, understand it, and place the order, without a human writing the code for each step. For that there's a protocol made for AI: MCP. That's the next lesson.

## Related
<!-- bite: abb8235b-1ad1-4a97-83a7-dd769212805f -->

- [[backend/frameworks/net-http/23-mcp-server|Next: Building an MCP Server]]
- [[backend/frameworks/express/22-grpc|The same lesson in Express]] — `@grpc/grpc-js` with proto-loader at runtime, and `int64` as strings
- [[backend/frameworks/net-http/10-versioning|Versioning]] — the same rules, which protobuf makes precise
- [[backend/frameworks/net-http/03-middleware|Middleware]] — what interceptors are, in HTTP
- [[backend/02-api-design/index|API Design]] — REST, GraphQL and gRPC side by side

## About this lesson
<!-- bite: 42bbb59f-482c-4c31-96cf-faac39a6b61c -->

**Level:** Advanced. Lesson 22 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, grpc-go 1.64 or later and protoc-gen-go-grpc 1.5 or later (for the generic stream types) and buf v2 configs. Covers what gRPC is for and why it suits service-to-service calls, the `.proto` language (services, messages, field numbers, `repeated`, `optional`, `go_package`), generating Go with buf and both protoc plugins as Go tools, `buf lint`'s request and response rules, a thin server on the existing services with the embedded `Unimplemented` struct, interceptor chains for logging, errors and panic recovery, mapping `apperr` kinds to status codes with `ErrorInfo` details, cancelled and timed-out calls, health checks and reflection, a shared client with `grpc.NewClient`, deadlines as contexts that reach the database, server streaming with the same subscribe-and-select shape as SSE, safe and breaking `.proto` changes with `reserved` and `buf breaking`, and testing in memory with `bufconn`.
