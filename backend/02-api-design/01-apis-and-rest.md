# APIs — REST, GraphQL, gRPC, WebSockets

An API style is a set of conventions for how a client and server exchange data — the actual transport is almost always HTTP (or, for real-time cases, a persistent connection), but the four common styles below structure that exchange very differently, and picking the right one is a real architectural decision, not a stylistic preference.

## REST — resource-oriented, the default for most public APIs

Models an API around **resources** (nouns), each with a URL, manipulated via standard HTTP methods (verbs):

```
GET    /posts          -> list posts
GET    /posts/42       -> get one post
POST   /posts          -> create a post
PUT    /posts/42       -> replace a post
PATCH  /posts/42       -> partially update a post
DELETE /posts/42       -> delete a post
```

Simple, cacheable (GET requests map naturally onto HTTP/CDN caching), and widely understood — the default choice for public-facing APIs specifically because of how broadly it's already known. Its main limitation: a client often needs data shaped differently than any single resource endpoint provides, leading to either **over-fetching** (getting a big object when you needed two fields) or **under-fetching** (needing several round-trips to assemble what you actually need — fetch a post, then separately fetch its author, then separately fetch its comments).

## GraphQL — client-specified shape, one request

The client sends a query describing exactly the shape of data it needs, across what would otherwise be several REST resources, and gets back exactly that — no more, no less, in one round trip.

```graphql
query {
  post(id: 42) {
    title
    author { name }
    comments { text, author { name } }
  }
}
```

This directly solves REST's over/under-fetching problem — the client dictates the shape instead of accepting whatever a fixed endpoint returns. The tradeoff: a single flexible endpoint is harder to cache at the HTTP layer (every query can be shaped differently, so there's no single stable URL per resource the way REST naturally provides), and the server needs care to avoid excessively expensive queries a client is technically allowed to construct (deeply nested queries can translate into a large number of underlying database calls if not deliberately optimized against, commonly with request complexity limits or "dataloader"-style batching).

## gRPC — high-performance service-to-service communication

Uses Protocol Buffers (a compact binary format, not JSON) over HTTP/2, with the request/response shape defined in a strict schema (a `.proto` file) that generates strongly-typed client/server code in multiple languages automatically.

```protobuf
service PostService {
  rpc GetPost (GetPostRequest) returns (Post);
}
message GetPostRequest { int32 id = 1; }
message Post { int32 id = 1; string title = 2; }
```

Much faster and more bandwidth-efficient than JSON-over-HTTP (binary encoding, HTTP/2 multiplexing), and the generated, strongly-typed clients eliminate a whole class of "the API changed and nobody told the client" bugs. The tradeoff: not human-readable on the wire (harder to debug by just looking at raw traffic the way you can with REST/JSON), and less naturally suited to a public-facing API consumed directly by arbitrary web browsers — which is exactly why gRPC is the common choice for internal microservice-to-microservice communication specifically, rather than a public API surface.

## WebSockets — persistent, bidirectional, real-time

Unlike REST/GraphQL/gRPC's request-response model (client asks, server answers, connection ends), a WebSocket keeps a single connection open, over which either side can send messages at any time, without the client needing to re-request anything.

```javascript
const socket = new WebSocket("wss://example.com/chat");
socket.onmessage = (event) => console.log("received:", event.data);
socket.send("hello");   // server can also push messages to the client, unprompted
```

The right choice specifically when the server needs to **push** data to the client without the client asking first — chat applications, live notifications, collaborative editing, live dashboards. Using WebSockets for ordinary request-response interactions that don't need this pushed-update property adds real complexity (connection management, reconnection handling, scaling a stateful persistent connection across multiple server instances) for no actual benefit over a simpler REST/GraphQL call.

## Choosing between them

| | Best fit |
|---|---|
| REST | Public APIs, simple CRUD, cacheable resources |
| GraphQL | Complex/nested data needs, many different client shapes (mobile vs web needing different fields) |
| gRPC | Internal service-to-service calls, performance-critical paths |
| WebSockets | Real-time, server-initiated updates |

Real systems frequently mix these — a public-facing REST or GraphQL API at the edge, gRPC between internal microservices, and WebSockets specifically for the subset of features that need live updates — rather than picking exactly one style for an entire system.

## Gotchas

- GraphQL's flexibility is also its biggest operational risk — without query complexity limits, a client (malicious or just careless) can construct a query that's cheap to write but extremely expensive for the server to resolve, effectively becoming a form of denial-of-service.
- REST's convention isn't strictly enforced by the protocol — nothing stops someone from building a "REST" API that doesn't actually follow resource/verb conventions consistently, which is a common, confusing real-world deviation from the textbook description above.
- WebSocket connections are stateful, which complicates horizontal scaling the same way session-based auth does (see [[backend/05-auth/01-authentication-flows|authentication flows]]) — a message meant for a specific connected client needs to reach whichever specific server instance that client is actually connected to, usually requiring a pub/sub layer (Redis, or a message queue) between instances.

## Related
- [[backend/01-foundations/02-http-servers|HTTP servers]]
- [[backend/04-data-and-persistence/01-databases-in-the-backend|databases]]
- [[backend/07-practices/01-backend-best-practices|backend best practices]]
