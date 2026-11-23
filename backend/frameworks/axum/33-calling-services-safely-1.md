---
id: 197a94f3-44b8-4e84-8a84-489d166b1999
---

# Calling Services Safely 1: Deadlines, Retries and the Breaker

**Calling another service safely means never waiting long, trying again only when it can help, and stopping calling a service that's unwell, so one slow service can't drag every service that calls it down with it.**

## Before you start
<!-- bite: f81880a3-bfac-4596-96d0-bcf5913b776e -->

You should have finished [[backend/frameworks/axum/32-splitting-out-a-microservice-4|Splitting Out a Microservice 4]]: the notifications service reads events and asks the API for contact details over gRPC. This topic leans on lesson 17 (backoff with jitter for webhooks), lesson 19 (a lock that's cancel-safe because of `Drop`) and lesson 22 (deadlines sent with a gRPC call).

This topic comes in two parts:

1. **Deadlines, retries and the breaker**: how notifications calls the API without being dragged down by it.
2. **Who's calling?**: how the API knows the caller really is notifications, and what it may ask for.

After this part you will be able to:

1. Explain why a slow service is often worse than one that's down.
2. Give every call a deadline, and carry the time left through retries.
3. Retry only what's worth it: the right errors, few times, with growing waits and jitter.
4. Build a circuit breaker, and make it safe when a call is abandoned half-way.
5. Choose a fallback, or decide there isn't one.

## Where we stopped
<!-- bite: 105c8144-308e-4bc6-93bc-1da5da062c60 -->

`GrpcApi::contact` asks the API for Ada's contact details with a 500 ms deadline, and anything but `NotFound` makes the event come back later. That's a start. But think about the bad days. The API restarts during a deploy: one call fails that would have worked 50 ms later. The API is overloaded for a minute: every event waits its full deadline, fails, comes back, waits again, and every one of those calls adds load to a service that's already struggling. Notifications is making the API's bad minute worse.

## The kid version
<!-- bite: 2fe9b774-a7f4-406c-ba5b-26af6274ad53 -->

Bayo's brother runs to Mama's stall to ask Ada's phone number. The stall is shut: Mama's gone to the market.

A sensible boy doesn't stand at the shut stall all afternoon. He waits a moment (maybe she's just behind the counter), knocks once more, and if it's still shut, he stops running there every five minutes. He checks again in a quarter of an hour. Meanwhile he does what he can without the number.

Standing at the stall is a call with no deadline. Knocking once more is a retry. Not running back every five minutes is the circuit breaker. Doing what he can without the number is the fallback.

**Where the picture stops working.** The boy can see the stall is shut. Our service can't: a busy API and a dead one look the same from outside, a call that doesn't answer. All we can do is count how often calls fail, and decide from that.

## Terms used in this part
<!-- bite: 05e9a3c7-dba0-4314-acdc-b31184bc7c91 -->

1. **Deadline**: This is the moment after which nobody's waiting for the answer any more, so the work should stop.
2. **Retry**: This is trying a failed call again, in case the failure was brief.
3. **Jitter**: This is a random extra wait added to each retry, so callers that failed together don't all try again at the same instant.
4. **Retry storm**: This is retries piling onto a service that's already struggling, until it can't recover.
5. **Circuit breaker**: This is a switch in front of calls to one service. After enough failures it **opens**, and calls fail at once without being made; later it lets a trial call through to see if the service is back.
6. **Fallback**: This is what to do instead when a call can't succeed: a plainer answer, a kept copy, or failing clearly.

## Step 1: why waiting is the enemy
<!-- bite: 17b92d79-c8b7-4905-aaec-0c590a0b93a3 -->

Every call that's waiting holds something: a task, memory, a reader's place in the stream, a database connection, a person waiting for an answer. Waiting calls pile up faster than you'd think.

If a service gets 100 calls a second and each takes 5 ms, about **half a call** is in progress at any moment. If each takes 4 seconds, **400 calls** are in progress at once, each holding its resources. Same traffic, 800 times the resources, just from slowness.

That's why **slow is often worse than down**. A service that's down fails in a millisecond, and callers move on. A service that's slow holds every caller for as long as it's allowed to.

So the rules come down to: **don't wait long, don't wait for things that won't come, and don't make it worse.**

## Step 2: deadlines, and carrying the time left
<!-- bite: 20fea78f-2b1c-4389-b9f3-fcf90cbadc28 -->

How long should a deadline be? Look at how long the call takes when things are healthy (lesson 37's metrics will tell you exactly), and set it at a few times the slow end of normal. `GetContact` normally takes 5 ms, and on a bad day 50 ms; **300 ms** gives plenty of room, and turns a 4-second disaster into a quick, clear failure.

Lesson 22 showed that tonic sends the deadline **with** the call, as a `grpc-timeout` header, so the API stops working on an answer nobody's waiting for. But here Rust differs from Go. In Go, a deadline travels in a `context.Context` through every call a handler makes, by itself. **In Rust, nothing carries it for you.** If notifications retries, each try needs the time *left*, not a fresh 300 ms; if the API's handler called a third service, it would have to read the `grpc-timeout` it was given and pass on what remained.

So we carry it by hand: one `Instant` for the whole call, and each try's own timeout worked out from it. From `notifications/src/api.rs`:

```rust
/// Each call, retries included, gets this long in all. `GetContact` takes about 5 ms; 300 ms is plenty.
const DEADLINE: Duration = Duration::from_millis(300);
```

```rust
/// The time left until `deadline`, for the next try's own `grpc-timeout`.
fn left(deadline: Instant) -> Duration {
    deadline.saturating_duration_since(Instant::now())
}
```

`saturating_duration_since` gives zero instead of panicking when the deadline has already passed. A call sent with a zero timeout fails at once, which is right: there's no time left.

The reader adds one more layer: part 3 of the microservice topic gave each event's handler 20 seconds in all, so even a handler making several calls can't hold a message past its ack wait.

## Step 3: retry carefully, or not at all
<!-- bite: e1f042e3-6677-43e5-983f-1153bb33ce53 -->

Retries fix brief blips: a restart, a dropped connection. They also cause retry storms. So every retry needs four answers:

1. **Is the call safe to repeat?** `GetContact` and `GetDish` only read, so yes. A call that *does* something (charge a card, send a text) is only safe to retry if it's idempotent, with a key, like lesson 15.
2. **Is the error worth retrying?** Only temporary ones: `UNAVAILABLE` (lesson 22 kept that code for exactly this) and `RESOURCE_EXHAUSTED` ("I'm overloaded, back off"). Never `NOT_FOUND`, `INVALID_ARGUMENT` or `PERMISSION_DENIED`: they'll fail the same way every time. And not a timeout: the deadline has passed, so there's no time left to try again.
3. **How many times?** Few: two retries at most. Three layers each retrying three times means one failure becomes 27 calls at the bottom.
4. **How long to wait?** A little, growing, with jitter: about 50 ms, then about 100 ms, each plus a random amount.

`notifications/src/resilience.rs` starts:

```rust
/// Calls `call` up to 1 + `retries` times, while it fails with an error `worth_retrying` accepts.
/// Waits `base`, then 2 × `base`, …, each plus up to the same again at random, and never past `deadline`.
pub async fn retry<T, E, F, Fut>(
    deadline: Instant,
    retries: u32,
    base: Duration,
    worth_retrying: impl Fn(&E) -> bool,
    mut call: F,
) -> Result<T, E>
where
    F: FnMut() -> Fut,
    Fut: Future<Output = Result<T, E>>,
{
    let mut attempt = 0;
    loop {
        let result = call().await;
        let Err(error) = &result else { return result };
        if attempt == retries || !worth_retrying(error) {
            return result;
        }
        let wait = base * 2u32.pow(attempt);
        let wait = wait + wait.mul_f64(rand::random::<f64>()); // jitter: callers that failed together don't retry together
        if Instant::now() + wait >= deadline {
            return result; // no time left for another try: give up now, with the real error
        }
        tokio::time::sleep(wait).await;
        attempt += 1;
    }
}
```

1. **Generic over the call**: `call` is any closure that makes a future of `Result<T, E>`, so it works for any gRPC method, or anything else.
2. **`FnMut() -> Fut`**: each try calls the closure again, to make a *new* future. A future can only be awaited once, so "try again" means "make another".
3. **`worth_retrying` decides**, so the same function serves gRPC (by status code) and anything else.
4. **Jitter**: `wait.mul_f64(rand::random::<f64>())` adds between nothing and the same again. Two hundred copies that all failed at 12:40:00.000 retry spread across 50 milliseconds instead of at once.
5. **It won't sleep past the deadline.** If there's 30 ms left and the next wait is 60 ms, there's no point waiting; it returns the real error now.

And what's worth retrying, for gRPC, in `api.rs`:

```rust
/// Worth another try: the API may answer next time.
pub fn temporary(status: &Status) -> bool {
    matches!(status.code(), Code::Unavailable | Code::ResourceExhausted)
}
```

**Remember the retries we already have.** The reader naks a message whose handler failed, and JetStream gives it back later, with growing delays (microservice part 3). That's a slow outer retry, seconds to minutes apart. So the inner retry only needs to cover a blip of a few hundred milliseconds; anything longer is the stream's job. Two layers, each doing the job it's good at.

## Step 4: the circuit breaker
<!-- bite: 93e38aec-48e1-4ccd-a7c7-6860a5a1151d -->

Retries help with blips. When the API is properly down or struggling for minutes, every call still waits for its deadline and fails, and every one of them adds load. Better to notice, and **stop calling for a while**.

A circuit breaker has three states:

```text
            5 unwell failures in a row
  CLOSED ─────────────────────────────────► OPEN
 (normal:                                  (every call fails at once,
  calls go through)                         without touching the network)
     ▲                                           │
     │ the trial call worked                     │ after 15 seconds
     │                                           ▼
     └──────────────────────────────────── HALF-OPEN
                  the trial call failed:   (one trial call goes through)
                  back to OPEN
```

The Go version of this lesson used a library, gobreaker. Rust has breaker crates too, but the logic is small enough to own, and writing it shows the one subtle part. The rest of `resilience.rs`:

```rust
/// A circuit breaker: after `trip_after` unwell failures in a row it opens, and every call fails at once,
/// without touching the network. After `open_for`, one trial call goes through; if it works, it closes.
pub struct Breaker {
    name: &'static str,
    trip_after: u32,
    open_for: Duration,
    state: Mutex<State>,
}

#[derive(Clone, Copy, Debug, PartialEq)]
enum State {
    Closed { failures: u32 },
    Open { until: Instant },
    /// One trial call is out; everyone else waits for its answer.
    HalfOpen,
}

#[derive(Debug, PartialEq, thiserror::Error)]
pub enum Refused<E> {
    #[error("the breaker is open: not calling")]
    Open,
    #[error(transparent)]
    Failed(E),
}

impl Breaker {
    pub fn new(name: &'static str, trip_after: u32, open_for: Duration) -> Self {
        Breaker { name, trip_after, open_for, state: Mutex::new(State::Closed { failures: 0 }) }
    }

    /// Runs `call`, unless the breaker is open. `unwell` says which errors count against the other
    /// service: "no such customer" is a healthy answer, "unavailable" isn't.
    pub async fn call<T, E>(&self, unwell: impl Fn(&E) -> bool, call: impl Future<Output = Result<T, E>>) -> Result<T, Refused<E>> {
        self.before()?;
        // If this future is dropped half-way (our caller gave up), the guard still reports, so a
        // trial call can't leave the breaker half-open for ever.
        let mut guard = Report { breaker: self, outcome: None };
        let result = call.await;
        guard.outcome = Some(match &result {
            Err(e) if unwell(e) => Outcome::Unwell,
            _ => Outcome::Healthy,
        });
        drop(guard);
        result.map_err(Refused::Failed)
    }

    fn before<E>(&self) -> Result<(), Refused<E>> {
        let mut state = self.state.lock().unwrap();
        match *state {
            State::Closed { .. } => Ok(()),
            State::Open { until } if Instant::now() >= until => {
                self.change(&mut state, State::HalfOpen); // this call is the trial
                Ok(())
            }
            State::Open { .. } | State::HalfOpen => Err(Refused::Open),
        }
    }

    fn after(&self, outcome: Option<Outcome>) {
        let mut state = self.state.lock().unwrap();
        let next = match (*state, outcome) {
            (_, Some(Outcome::Healthy)) => State::Closed { failures: 0 },
            (State::Closed { failures }, Some(Outcome::Unwell)) if failures + 1 < self.trip_after => State::Closed { failures: failures + 1 },
            (_, Some(Outcome::Unwell)) => State::Open { until: Instant::now() + self.open_for },
            // Cancelled: it says nothing about the other service. A trial is simply allowed again.
            (State::HalfOpen, None) => State::Open { until: Instant::now() },
            (current, None) => current,
        };
        self.change(&mut state, next);
    }

    fn change(&self, state: &mut State, to: State) {
        let (from, to_name) = (name(*state), name(to));
        if from != to_name {
            tracing::warn!(breaker = self.name, from, to = to_name, "circuit breaker changed");
        }
        *state = to;
    }

    pub fn is_open(&self) -> bool {
        matches!(*self.state.lock().unwrap(), State::Open { .. })
    }
}

fn name(state: State) -> &'static str {
    match state {
        State::Closed { .. } => "closed",
        State::Open { .. } => "open",
        State::HalfOpen => "half-open",
    }
}

#[derive(Clone, Copy)]
enum Outcome {
    Healthy,
    Unwell,
}

/// Tells the breaker how a call went, when it's dropped: finished, or abandoned half-way.
struct Report<'a> {
    breaker: &'a Breaker,
    outcome: Option<Outcome>,
}

impl Drop for Report<'_> {
    fn drop(&mut self) {
        self.breaker.after(self.outcome);
    }
}
```

1. **`State` is an enum**, so the breaker is always exactly one of the three, and `Open` carries the moment it may try again. The whole state sits behind one `Mutex`, held only for a moment at the start and end of a call, never across the `.await`.
2. **`before` decides**: closed lets the call through; open refuses it, unless its time is up, in which case *this* call becomes the trial (half-open); half-open refuses everyone but the trial.
3. **`unwell` decides what counts.** A `NOT_FOUND` means the API is working fine and answered "no such customer". Counting it as a failure would let five deleted customers in a row shut off all notifications. So only errors that mean "unwell" count; anything else resets the count, like a success.
4. **Five unwell failures in a row** open it. One success in between resets the count, so a service that's merely a bit flaky stays usable.
5. **Every change is logged.** "Breaker `api-customers` went from closed to open" is one of the most useful lines your logs will ever hold; lesson 37 turns it into a metric and an alert.

**The subtle part: a call that never finishes.** A Rust future can be dropped half-way: the reader's 20-second timeout, or the service shutting down, simply stops polling it. If that happens to the *trial* call, nobody ever reports back, and a breaker that waits for the trial's answer is half-open for ever, refusing every call. That's why the report is a **`Drop` guard**, the trick lesson 19's cache lines used. `Report` is made before the call and dropped after it, or when the whole future is dropped, whichever comes first. If it's dropped with no outcome, the call was abandoned: it says nothing about the API's health, so the breaker just allows another trial.

### What counts as unwell, and a surprise

```rust
/// Says the API is struggling, not that it answered "no".
pub fn unwell(status: &Status) -> bool {
    matches!(status.code(), Code::Unavailable | Code::DeadlineExceeded | Code::Internal | Code::ResourceExhausted | Code::Unknown | Code::Cancelled)
}
```

Look at `Code::Cancelled` in that list. You'd expect a timed-out call to fail with `DEADLINE_EXCEEDED`. tonic, the client, ends a call whose own timeout ran out with **`CANCELLED`, "Timeout expired"** (lesson 22 noticed the same thing). Without `Cancelled` in the list, a paused API would make every call time out, none of them would count, and the breaker would never open. The live run in step 6 shows exactly those messages.

### Putting it together

```rust
#[async_trait]
impl Customers for GrpcApi {
    async fn contact(&self, customer_id: i64) -> Result<Contact, Failure> {
        let deadline = Instant::now() + DEADLINE;
        // The breaker outside, the retries inside: one call to the breaker is one whole attempt.
        let answer = self
            .customers_breaker
            .call(
                unwell,
                retry(deadline, 2, Duration::from_millis(50), temporary, || {
                    let mut client = self.customers.clone();
                    async move {
                        let mut request = Request::new(GetContactRequest { customer_id });
                        request.set_timeout(left(deadline));
                        client.get_contact(request).await
                    }
                }),
            )
            .await;
        match answer {
            Ok(answer) => {
                let c = answer.into_inner();
                Ok(Contact { first_name: c.first_name, email: c.email, phone: c.phone })
            }
            // They deleted their account: they'll never come back, so don't try again.
            Err(Refused::Failed(status)) if status.code() == Code::NotFound => Err(Failure::Skip(format!("customer {customer_id} is gone"))),
            // No fallback for an address: the event waits in the stream, and comes back in a few seconds.
            Err(refused) => Err(retry_later(refused)),
        }
    }
}
```

The order matters: **the deadline outside everything, the breaker outside the retries.** One call through the breaker is a whole attempt, retries and all. If the retries were outside the breaker, one message could count as three failures and trip it three times as fast. And the deadline covers the whole thing: 300 ms in total, not 300 ms per try.

**One breaker per service you call, shared by every call to it.** `GrpcApi::new` makes `api-customers` and `api-menu` once, in `Arc`s, and every clone shares them. A breaker made per call would remember nothing.

## Step 5: fallbacks
<!-- bite: c5e03655-68e5-48f6-ab98-04516016cef2 -->

When a call fails after its deadline, retries and the breaker, what then? It depends on what the data is for:

1. **The dish name** in "Thank you, Ada! 2 × Jollof rice, ₦3,000." Nice to have. If `GetDish` fails, say "2 plates, ₦3,000.00". A slightly plainer receipt now is better than a perfect one in ten minutes.
2. **The customer's email or phone number.** Essential: we can't send without it. No fallback: return the error, the reader naks, and the stream tries again in a few seconds.
3. **Keep what changes rarely.** Dish names change a few times a year. Keep them in notifications' memory for 10 minutes, and most messages won't call `GetDish` at all. Contact details change more and are personal, so don't keep them longer than one message needs.

The menu side, with all of it:

```rust
#[async_trait]
impl Menu for GrpcApi {
    async fn dish_name(&self, dish_id: i64) -> String {
        if let Some((name, until)) = self.names.lock().unwrap().get(&dish_id)
            && Instant::now() < *until
        {
            return name.clone();
        }
        let deadline = Instant::now() + DEADLINE;
        let answer = self
            .menu_breaker
            .call(
                unwell,
                retry(deadline, 2, Duration::from_millis(50), temporary, || {
                    let mut client = self.menu.clone();
                    async move {
                        let mut request = Request::new(GetDishRequest { id: dish_id });
                        request.set_timeout(left(deadline));
                        client.get_dish(request).await
                    }
                }),
            )
            .await;
        match answer {
            Ok(answer) => {
                let name = answer.into_inner().dish.map(|d| d.name).unwrap_or_default();
                self.names.lock().unwrap().insert(dish_id, (name.clone(), Instant::now() + NAMES_FOR));
                name
            }
            // The fallback: a plainer message, sent now, beats a perfect one in ten minutes.
            Err(refused) => {
                tracing::warn!(dish_id, cause = %refused, "no dish name; the message goes without it");
                String::new()
            }
        }
    }
}
```

`dish_name` now returns a plain `String`, never an error: an empty name *is* the fallback, and the handler words the receipt without it ("2 plates"). Its trait says so in its comment, so nobody "fixes" it later by making it fail.

**Bulkheads.** The reader handles **one event at a time** for each copy of the service, so each copy has at most one or two calls to the API in flight. That's a bulkhead already, and a tight one: however slow the API gets, notifications can't pile hundreds of calls onto it. If a service ever calls another in parallel (a handler that loads ten dishes at once), give it a limit of its own: a `tokio::sync::Semaphore`, like lesson 18's photo jobs' concurrency of one.

## Step 6: testing, and trying it
<!-- bite: 6301deeb-5423-4c2f-8054-c68a8221cd0d -->

The breaker and the retries have unit tests in `resilience.rs`, with pretend calls that count how often they ran:

```rust
    #[tokio::test]
    async fn opens_after_five_unwell_failures_and_tries_again_later() {
        let breaker = Breaker::new("test", 5, Duration::from_millis(50));
        let calls = AtomicU32::new(0);
        let unwell = |e: &Answer| *e == Answer::Down;
        let down = || async {
            calls.fetch_add(1, Ordering::SeqCst);
            Err::<(), _>(Answer::Down)
        };
        for _ in 0..5 {
            assert_eq!(breaker.call(unwell, down()).await, Err(Refused::Failed(Answer::Down)));
        }
        assert_eq!(breaker.call(unwell, down()).await, Err(Refused::Open));
        assert_eq!(calls.load(Ordering::SeqCst), 5, "the sixth call never reached the service");

        tokio::time::sleep(Duration::from_millis(60)).await;
        assert_eq!(breaker.call(unwell, async { Ok::<_, Answer>("back") }).await, Ok("back"), "the trial call");
        assert!(!breaker.is_open());
    }
```

The others check: two `Down`s then success makes 3 calls and succeeds; a `NoSuchThing` makes exactly 1; with 60 ms left and a 50–100 ms wait coming, it gives up at once; seven "no such thing" answers leave a breaker closed; and an abandoned trial (its caller gives up after 5 ms) leaves the breaker ready for the next call, not stuck.

And by hand, the way it matters. Notifications is stopped while six orders are paid; then the API's process is **paused** (`kill -STOP`, so it's there but answers nothing, like a server that's stuck) and notifications starts. Its log:

```text
06:11:05.890 WARN contracts::stream: event failed; will try again … why=code: 'The operation was cancelled', message: "Timeout expired"
06:11:06.197 WARN contracts::stream: event failed; will try again … why=code: 'The operation was cancelled', message: "Timeout expired"
06:11:06.502 WARN contracts::stream: event failed; will try again … why=code: 'The operation was cancelled', message: "Timeout expired"
06:11:06.805 WARN contracts::stream: event failed; will try again … why=code: 'The operation was cancelled', message: "Timeout expired"
06:11:07.111 WARN notifications::resilience: circuit breaker changed breaker="api-customers" from="closed" to="open"
06:11:07.113 WARN contracts::stream: event failed; will try again … why=the breaker is open: not calling attempt=1
06:11:07.114 WARN contracts::stream: event failed; will try again … why=the breaker is open: not calling attempt=2
```

Five calls, 300 ms apart, each giving up at its deadline (tonic's `Cancelled`, "Timeout expired"). Then the breaker opens, and the next calls fail in a millisecond without touching the API. Each event goes back to the stream with its growing delay. Then the API carries on (`kill -CONT`):

```text
06:11:22.129 WARN notifications::resilience: circuit breaker changed breaker="api-customers" from="open" to="half-open"
06:11:22.201 WARN notifications::resilience: circuit breaker changed breaker="api-customers" from="half-open" to="closed"
06:11:22.211 INFO notifications::providers: email (not really sent) to="tola@example.com" subject="Mama Put receipt for order 25" …
06:11:22.228 INFO notifications::providers: email (not really sent) to="tola@example.com" subject="Mama Put receipt for order 26" …
```

Fifteen seconds after opening, one trial call; it worked, so the breaker closed, and the receipts went out. Counting them in the log afterwards: orders 21 to 26, **one receipt each**.

## The Rust in this part
<!-- bite: 2da3fde4-070f-4125-b00b-1779981c19cd -->

1. **`Instant` and `saturating_duration_since`**: a moment on the computer's own clock, and the time until it, or zero once it's passed.
2. **A generic async function taking a closure that makes futures**, `F: FnMut() -> Fut, Fut: Future<Output = Result<T, E>>`: call it again for each try, because a future can only be awaited once.
3. **`impl Fn(&E) -> bool` as a parameter**: any function or closure that answers a question about an error.
4. **`Duration::mul_f64`** and `rand::random::<f64>()`: a duration times a random number between 0 and 1, for jitter.
5. **An enum with data for a state machine**, `State::Open { until }`, and `match` on a tuple, `(*state, outcome)`, to decide the next state in one place.
6. **A `Drop` guard**: `Report` runs its `drop` when the call finishes *or* when the future is dropped half-way, so the breaker always hears back.
7. **`std::sync::Mutex` in async code**: fine when it's held for a moment and never across an `.await`.
8. **`Arc<Breaker>` in a `Clone` struct**: every clone of `GrpcApi` shares the same two breakers and the same name cache.
9. **`#[derive(thiserror::Error)]` on a generic enum**, `Refused<E>`, with `#[error(transparent)]` for the inner error.

## Your project so far
<!-- bite: d3af4b24-2021-4e05-b84b-4ee7855a353a -->

```text
mama-put/notifications/
├── Cargo.toml              ← rand
└── src/
    ├── resilience.rs       ← NEW: retry (deadline, jitter), Breaker (closed, open, half-open; a Drop guard), tests
    ├── api.rs              ← 300 ms per call in all, retries, a breaker per service, dish names kept 10 minutes
    └── handlers.rs         ← dish_name can't fail: an empty name is the fallback
```

## Common mistakes
<!-- bite: b9f8a2ad-0f3c-48c4-9bbe-75696fbce89d -->

1. **No deadline.** One slow service holds every caller for as long as it likes.
2. **A fresh deadline for every retry.** Three tries of 300 ms is 900 ms. Carry one deadline through.
3. **Retrying everything.** `NOT_FOUND` fails the same way every time; a timeout has no time left. Retry only what's temporary.
4. **Retries without jitter**, or without a limit. Every caller hammers the service at the same moments.
5. **Retries outside the breaker.** One message counts as several failures.
6. **A breaker that counts "no" as a failure.** A run of deleted customers shuts off every message.
7. **A breaker whose trial can be abandoned with no report.** It stays half-open for ever. Report from a `Drop` guard.
8. **Assuming a timeout is `DEADLINE_EXCEEDED`.** tonic's client says `CANCELLED`. Check what your library really sends.
9. **A new breaker per call.** It remembers nothing. One per service you call, shared.

## Check your understanding
<!-- bite: 516474dc-e8d0-4189-b356-0cb78f89e358 -->

1. Why is a slow service often worse than one that's down?
2. In Go, a deadline travels by itself. What do we do instead in Rust, and why one `Instant` for the whole call?
3. Which gRPC errors does `temporary` retry, and why not `NOT_FOUND`, or a timeout?
4. Why is the breaker outside the retries, and the deadline outside both?
5. A trial call is under way when the reader's 20-second timeout drops the whole handler. What happens to the breaker, and why?
6. Why does `unwell` include `Code::Cancelled`?

<details>
<summary>Answers, after your attempt</summary>

1. A service that's down fails at once and callers move on. A slow one holds every caller for as long as it's allowed, so waiting calls, and everything they hold, pile up.
2. Nothing carries the deadline for us, so we make one `Instant` when the call starts and give each try the time left (`left(deadline)`) as its own timeout. A fresh 300 ms per try would let three tries take 900 ms.
3. `UNAVAILABLE` and `RESOURCE_EXHAUSTED`: the service may answer next time. `NOT_FOUND` will be the same answer next time; a timeout means the deadline has passed, so there's no time left to retry.
4. So one call through the breaker is one whole attempt, retries included, and one failing message counts once. The deadline outside both means the whole thing, retries included, has 300 ms in all.
5. The future is dropped, so `Report` is dropped with no outcome. `after` sees a half-open breaker with no outcome and sets it open with "try again now", so the next call becomes a new trial instead of the breaker being stuck half-open.
6. Because tonic ends a call whose own timeout ran out with `CANCELLED`, "Timeout expired", not `DEADLINE_EXCEEDED`. Without it, timeouts wouldn't count, and a stuck API would never open the breaker.

</details>

## Practice
<!-- bite: e7d51d94-064f-42aa-b17b-a5a3095302f0 -->

1. Pause the API with `kill -STOP` while notifications is running, and watch the breaker's log lines. Then try it with `unwell` not counting `Cancelled`, and see the difference.
2. Make the breaker's settings (5 failures, 15 seconds) come from notifications' `.env`, with those as defaults.
3. Add a breaker to lesson 17's Paystack client, counting 5xx answers and timeouts but not 4xx. When it's open, `start_checkout` should answer 502 at once. Is there a fallback for taking money? (No: fail fast and say so.)

**Done when** the five `resilience` tests pass, a paused API opens the breaker within a few seconds and it closes again once the API carries on, and every paid order still gets exactly one receipt.

## Before moving on
<!-- bite: 102ddde4-4bea-40a9-9f7c-69cf288ae7de -->

Notifications now calls the API like a good neighbour: it never waits long, retries only blips, backs off when the API is unwell, and sends a plainer message rather than none. But the API still answers anyone who can reach port 50051, and `GetContact` hands out customers' phone numbers. Part 2 makes every call prove which service it comes from, and what it's allowed to ask.

## Related
<!-- bite: 7e42e5f9-0f41-4f8e-94cd-d668aef223b4 -->

- [[backend/frameworks/axum/34-calling-services-safely-2|Next: Calling Services Safely 2: Who's Calling?]]
- [[backend/frameworks/net-http/26-calling-services-safely|The same topic in net/http]] — gobreaker, and a deadline that travels in `context.Context`
- [[backend/frameworks/axum/22-grpc|gRPC]] — deadlines sent with the call, and tonic's `Cancelled`
- [[backend/frameworks/axum/19-caching|Caching]] — the `Drop` guard trick, first time round

## About this lesson
<!-- bite: 14a9af15-06c5-42b7-ae0d-664617ca138b -->

**Level:** Advanced. Part 1 of 2 on calling services safely, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96) and tonic 0.14. Covers why slow is worse than down, deadlines carried by hand as one `Instant` through every try, retries only for temporary errors with a small limit, growing waits and jitter, never sleeping past the deadline, a circuit breaker written as an enum state machine with a `Drop` guard for abandoned trials, which errors count as unwell (including tonic's `Cancelled` for client timeouts), the order of deadline, breaker and retries, fallbacks and kept copies, bulkheads, and testing it all, including a paused API, by hand.
