---
id: dc8da687-8717-4b08-a339-22b3a272bcf1
---

# Splitting Out a Microservice 1: Should You, and Where the Line Goes

**A microservice is a small program that does one job for the system, owns its own data, and talks to the other programs only through messages and APIs, never by reaching into their code or their database.**

## Before you start
<!-- bite: afb648a4-af24-4304-ace2-f0fa332e0ac6 -->

You should have finished [[backend/frameworks/axum/28-mcp-in-production-5|MCP in Production 5]], the end of the REST, GraphQL, gRPC and MCP lessons. This topic leans on lesson 17 (`settle` and its transaction), lesson 18 (jobs added inside a transaction, and jobs safe to run twice) and lesson 22 (the gRPC contract).

This topic is big, so it comes in four parts:

1. **Should you, and where the line goes**: when a second service is worth it, a Cargo workspace, a boundary the compiler enforces, and a database of its own.
2. **Events and the outbox**: what the API says happened, and how "it happened" and "tell everyone" are committed together.
3. **Streams and readers**: NATS JetStream keeps the events; durable readers handle each one, retry what can work later, and drop what never will.
4. **The notifications service**: the second program itself, the gRPC call it makes to the API, and the whole thing running.

The code across the four parts is one change to the project. It builds and runs at the end of part 4; until then, read each part's code as a piece of that whole.

After this part you will be able to:

1. Decide honestly whether something should be its own service, and pick a good first candidate.
2. Turn the project into a Cargo workspace with several crates, without moving the code you already have.
3. Make the boundary between two services something the compiler checks, and test it.
4. Give a service its own database, with a user that can't reach anyone else's.

## What to install
<!-- bite: f7565962-ec16-4e64-a059-f5146c6f7fc3 -->

**NATS**, the message server, in Docker:

```bash
docker run -d --name mamaput-nats -p 4222:4222 -p 8222:8222 nats:2-alpine -js -m 8222
```

1. **`-js`** switches on **JetStream**, NATS's storage. Without it, NATS passes messages on and forgets them; with it, messages are kept in streams until every reader has handled them.
2. **`-m 8222`** opens a small monitoring page at `http://localhost:8222`, handy for seeing streams and readers.

Lesson 38 moves it into Docker Compose with everything else. The Rust client, **async-nats**, is added to each crate that needs it in parts 2 and 4.

## Where we stopped
<!-- bite: 9f7d61d6-47d9-4368-ae97-622fbef27bcb -->

Look at everything the API does to talk to customers:

1. Receipt emails (lesson 18), from the worker, through an email provider with its own key.
2. Reminders about unpaid orders (lesson 18).
3. Soon: a text when the order is ready, through an SMS provider, with another key.

And look at what happened last Tuesday (pretend). The SMS provider was slow for an hour. The worker's receipts queue filled up with retries, the worker spent its time waiting on it, and lesson 17's webhooks to Okada Riders, in the same worker, went out late. One provider's bad hour reached our delivery partner.

Also, Mama has hired someone to look after customer messages: the wording, which messages to send when. Every small change to a message means deploying the *whole* API, payments and all.

Those are the two real reasons to split something out: **one part's failures shouldn't reach the rest**, and **one part should change on its own schedule**. Notifications has both.

## The kid version
<!-- bite: 6d033cfc-4f66-4fc3-aa14-297c3bbe2d2a -->

When Mama Put was small, Mama took orders, cooked, collected money and shouted "Bayo, your food is ready!", all herself.

Now it's busy. She hires a boy just for calling names and sending texts. He has his own corner, his own phone, his own notebook. Mama doesn't tell him how to send a text; she just writes "order 42 is ready" on a slate by the door. Anyone whose job involves ready orders reads the slate. The boy reads it, looks up who ordered 42, and texts them.

If the boy's phone runs out of credit, Mama keeps cooking. The orders don't stop. The texts are late, and that's all.

The slate is the **event stream**. The boy is the notifications service. "Mama doesn't care who reads the slate" is the point.

**Where the picture stops working.** A slate gets wiped. Our stream keeps every message until each reader has said "done", so when the boy comes back from his break, everything written while he was away is still there, in order.

## Terms used in this part
<!-- bite: 522acea3-03e6-4870-82bb-8da68141bba4 -->

1. **Monolith**: This is one program that does everything. Not an insult: most good systems start as one, and many stay one.
2. **Service boundary**: This is the line around what a service owns: its job, its code, its data.
3. **Workspace**: This is Cargo's way to keep several crates in one repository, built together, with one `Cargo.lock` and one `target` folder.
4. **Monorepo**: This is one repository holding several services.

## Step 1: should you, really?
<!-- bite: e58b8c2b-a910-4210-895b-48104324b37b -->

Microservices are fashionable, and many teams regret them. Be honest about the costs before paying them:

| You get | You pay |
|---|---|
| A failure in one service stays there | Every call between services can fail, be slow, or arrive twice |
| Each service deploys on its own | Changes that span services need careful ordering (versions, both shapes for a while) |
| Each service keeps its own secrets and data | Data is in several places; a "join" across services means network calls |
| Teams can own their service | Debugging means following one request through several programs (lesson 36) |
| Scale only the busy part | More to run, watch, secure and pay for |

The usual good advice is **"monolith first"**: build one well-structured program, with modules that only talk through small traits (lessons 4 and 5), and split only when a real reason appears. Our modules already declare what they need from each other as traits, so much of the cutting is done.

Mama Put, honestly, could stay one program for years. We're splitting notifications to learn how, and because it's the classic **good first candidate**:

1. It has clear edges: "something happened; tell the customer".
2. It doesn't need to answer anyone in a hurry. A receipt a minute late is fine.
3. It talks to unreliable outside providers, whose failures we want kept away from orders and payments.
4. Nothing else waits for it. Nobody's request fails because a text wasn't sent.

A **bad** first candidate would be payments or the menu: the API needs them in the middle of placing an order, so every order would become a network call that can fail.

## Step 2: a Cargo workspace
<!-- bite: dea32936-88d2-4370-8aa3-6bd7248876f4 -->

In Node, a second service is a second project with its own `package.json`. In Rust, the natural shape is a **workspace**: several crates in one repository, each with its own `Cargo.toml` and its own dependencies, built together.

The API stays exactly where it is, as the workspace's root package. Two new crates sit beside it. The top of the root `Cargo.toml`:

```toml
[workspace]
# The API is this package; the others are their own crates, with their own dependencies.
members = ["contracts", "notifications"]

[package]
name = "mama-put"
version = "0.1.0"
edition = "2024"
```

```text
mama-put/
├── Cargo.toml              ← the API's package, and the workspace's list of members
├── Cargo.lock · target/    ← one of each, shared by every crate
├── src/ · tests/ · migrations/ · proto/      ← the API, as since lesson 1
├── contracts/              ← NEW: event names and shapes, and how to read the stream
└── notifications/          ← NEW: the notifications service: its own code, settings and database
```

1. **`members`** lists the other crates. The root package is a member without being listed.
2. **One `Cargo.lock`** means every crate uses the same version of each dependency. For one small team, that's a gift.
3. **Commands take `-p`**: `cargo build -p notifications`, `cargo test -p contracts`. `cargo test --workspace` runs everything.
4. **Each crate builds its own program.** `cargo build` makes `target/debug/mama-put`, `target/debug/worker` and `target/debug/notifications`, three programs that run as three processes, and in lesson 38, in three containers.

The API still depends on `contracts`, by path, at the top of its dependencies:

```toml
contracts = { path = "contracts" }
```

## Step 3: a boundary the compiler checks
<!-- bite: 1be2efe9-fab0-44a4-9db4-981e21f33f2f -->

In the Go version of this lesson, every service lived in one Go module, and nothing stopped the notifications code importing the API's `orders` package. It needed a test that listed every import to catch it.

In a workspace, **a crate can only use crates its `Cargo.toml` names.** The notifications crate's dependencies are `contracts`, NATS, sqlx, tonic and a few more. `mama_put`, the API, isn't there. So a line like this in the notifications code:

```rust
use mama_put::orders::Order;
```

isn't a style problem; it doesn't compile. The compiler answers that there's no crate called `mama_put`. Nobody can tie the two services' code together by accident.

Someone *could* still do it on purpose, by adding the API to notifications' `Cargo.toml`, "just to reuse the `Order` type". Then any change to the API's code would change notifications too, and the two could never be deployed apart again. So one test guards the dependency list itself. `notifications/tests/boundary.rs`:

```rust
//! The notifications service must never depend on the API's crate. Cargo already refuses a `use mama_put::…`
//! without the dependency; this test refuses the dependency itself, however it arrives.

use std::process::Command;

#[test]
fn notifications_does_not_depend_on_the_api() {
    let cargo = std::env::var("CARGO").unwrap_or_else(|_| "cargo".into());
    let tree = Command::new(cargo)
        .args(["tree", "--package", "notifications", "--edges", "normal,build", "--prefix", "none", "--format", "{p}"])
        .output()
        .expect("cargo tree runs");
    assert!(tree.status.success(), "{}", String::from_utf8_lossy(&tree.stderr));
    let tree = String::from_utf8(tree.stdout).unwrap();
    assert!(tree.lines().any(|line| line.starts_with("contracts ")), "it does use the contracts");
    let api: Vec<&str> = tree.lines().filter(|line| line.starts_with("mama-put ")).collect();
    assert!(api.is_empty(), "the notifications service depends on the API: {api:?}");
}
```

**`cargo tree`** prints every crate a crate depends on, directly or not. `--edges normal,build` leaves out dev-dependencies (tests may use anything), and `--format {p}` prints just "name version". The test checks the list has `contracts` in it and not `mama-put`.

I tried it by adding `mama-put = { path = ".." }` to notifications' dependencies:

```text
thread 'notifications_does_not_depend_on_the_api' panicked at notifications/tests/boundary.rs:17:5:
the notifications service depends on the API: ["mama-put v0.1.0 (/home/you/mama-put)"]
test result: FAILED. 0 passed; 1 failed
```

Removed again, it passes. Lesson 39's pipeline runs it on every change. That's lesson 4's one-way rule, written down where the computer checks it.

`contracts` is the one crate both may use, and it must stay small and neutral: it depends on neither service. If it ever needed the API's `Kobo` type, it would have to depend on the API, and the boundary would be gone. So it uses plain `i64` for money (part 2).

## Step 4: a database of its own
<!-- bite: d5d68acc-fa22-461d-9c9c-2a162a9caf8c -->

The most important rule in this topic: **a service's database is private.** The notifications service never reads the API's tables, and the API never reads notifications'. Everything goes through events or APIs.

Why so strict? Because a shared table is a hidden contract. If notifications read `users.email` directly, renaming that column in the API would break notifications, with no warning, and the two services could never deploy separately again. You'd have a monolith with network problems.

So the notifications service gets its own database, on the same Postgres server for now, with its own user:

```sql
CREATE USER notifications CREATEDB;
CREATE DATABASE mamaput_notifications OWNER notifications;
REVOKE CONNECT ON DATABASE mamaput FROM PUBLIC;
```

1. **Its own user and database.** In production the user gets a password and no `CREATEDB`; here it has `CREATEDB` because `#[sqlx::test]` makes a fresh database for each test.
2. **`REVOKE CONNECT … FROM PUBLIC`**: Postgres lets every user connect to every database unless you take that away. After it, only the API's own user (and superusers) can connect to `mamaput`.

Proof, on my machine:

```bash
psql -h localhost -p 5544 -U notifications -d mamaput -c 'select 1'
```

```text
psql: error: connection to server at "localhost" (::1), port 5544 failed: FATAL:  permission denied for database "mamaput"
DETAIL:  User does not have CONNECT privilege.
```

Lesson 38 puts these lines in the setup script Docker Compose runs.

The notifications database will hold:

1. **`sent_notifications`**: every message sent, so the same one is never sent twice, and support can see what a customer got.
2. **`preferences`**: whether each customer wants texts, emails or both. The API doesn't need to know.

It does **not** hold customers' email addresses and phone numbers. Those belong to the API, where people edit them. When notifications needs them, it asks (part 4).

## The Rust in this part
<!-- bite: e9bf007f-c6ba-439b-8914-451a933d8bbd -->

1. **`[workspace]` with `members`**: several crates in one repository, one `Cargo.lock`, one `target` folder. A root `Cargo.toml` can be both a package and the workspace.
2. **A path dependency**, `contracts = { path = "contracts" }`: a crate from the same repository, built from its source, no publishing needed.
3. **`cargo … -p <crate>`** and **`--workspace`**: run a command for one crate, or for all of them.
4. **`std::process::Command`** in a test: runs another program (here `cargo tree`) and reads what it printed.
5. **`std::env::var("CARGO")`**: when Cargo runs your tests, it says where the `cargo` program is, so the test runs the same one.

## Your project so far
<!-- bite: bbac0dcf-672f-4730-8700-f33b0867da85 -->

```text
mama-put/
├── Cargo.toml              ← [workspace] members = ["contracts", "notifications"]; contracts as a path dependency
├── contracts/              ← NEW crate (filled in parts 2 and 3)
└── notifications/          ← NEW crate (filled in part 4)
    └── tests/boundary.rs   ← NEW: the service never depends on the API
```

## Common mistakes
<!-- bite: 7a15b222-7d62-4b8a-bd3b-c12bc5839a1f -->

1. **Splitting too early, or splitting the wrong thing.** Something the main flow waits on becomes a network call that can fail. Split what can be late.
2. **Sharing a database "for now".** It becomes the hidden contract that stops either side changing. Each service owns its data.
3. **Adding the other service as a dependency** to reuse one type. Put shared shapes in `contracts`, and keep the boundary test.
4. **Letting `contracts` depend on a service.** Then it drags that service into everyone who uses it. Plain types only.

## Check your understanding
<!-- bite: 66d676d3-7f41-4d41-bf3e-ff2f0a8411db -->

1. Why is notifications a good first service to split out, and payments a bad one?
2. What stops the notifications code using the API's `Order` type, and what does the boundary test add to that?
3. Why mustn't `contracts` use the API's `Kobo` type?
4. Why does each service get its own database, and what does `REVOKE CONNECT … FROM PUBLIC` change?

<details>
<summary>Answers, after your attempt</summary>

1. Nothing waits for notifications: a receipt a minute late is fine, it has clear edges, and its outside providers fail in ways we want kept away from orders. Payments is needed in the middle of placing and paying for an order, so splitting it would turn the main flow into network calls that can fail.
2. Cargo: the notifications crate doesn't list the API as a dependency, so `use mama_put::…` doesn't compile. The test stops someone adding that dependency, by checking `cargo tree` for `mama-put`.
3. Because `contracts` would then depend on the API, and every crate that uses `contracts`, notifications included, would depend on the API too. The boundary would be gone.
4. A shared table is a hidden contract: changing it in one service breaks the other without warning. Revoking `CONNECT` from `PUBLIC` means a user can only connect to the databases it's been given, so the notifications user can't even open the API's.

</details>

## Practice
<!-- bite: c432fad1-bb8a-4330-a049-8226f894f161 -->

1. Run `cargo tree -p notifications --edges normal --depth 1` and read the list: everything notifications depends on directly.
2. Try the forbidden line, `use mama_put::orders::Order;`, in `notifications/src/lib.rs`, read the compiler's error, and remove it.
3. Write down two parts of Mama Put that would be bad candidates for their own service, and why.

**Done when** `cargo build --workspace` builds all three crates, the boundary test passes, and the notifications user can't connect to the API's database.

## Before moving on
<!-- bite: 9d845249-220d-474d-badb-2f14ea775b24 -->

There's a line now: two crates that can't reach into each other, and two databases that can't either. But the API still has to tell notifications when an order is paid, and the obvious way ("after the commit, send a message") can lose that news or invent it. Part 2 builds the outbox, so "the order is paid" and "tell everyone it's paid" can never come apart.

## Related
<!-- bite: c911581a-8af7-4832-8c46-2599789c8aeb -->

- [[backend/frameworks/axum/30-splitting-out-a-microservice-2|Next: Splitting Out a Microservice 2: Events and the Outbox]]
- [[backend/frameworks/net-http/25-splitting-out-a-microservice|The same topic in net/http]] — one Go module, and an import test with `go list -deps`
- [[backend/frameworks/axum/04-structuring-an-axum-service|Structuring an Axum Service]] — the one-way rule this makes into a crate boundary

## About this lesson
<!-- bite: 09c9264e-583d-4586-a2c3-71a7929c645b -->

**Level:** Advanced. Part 1 of 4 on splitting out a microservice, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), NATS Server 2.10 or later with JetStream on. Covers when to split a service and good first candidates, a Cargo workspace with the API as its root package, a boundary the compiler enforces and a `cargo tree` test that guards it, a neutral contracts crate, and a private database per service with `REVOKE CONNECT`.
