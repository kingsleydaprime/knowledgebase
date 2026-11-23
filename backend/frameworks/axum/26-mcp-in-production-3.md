---
id: c663696f-1d31-4f52-bc18-221bf7a840b4
---

# MCP in Production 3: Quotes and Asking the Person

**An AI assistant must never spend someone's money on a guess, so ordering through MCP takes three layers: the assistant can't pay, it can only place what it was quoted, and the person is asked on their own screen.**

## Before you start
<!-- bite: 977806a5-a249-459b-ad53-f4397ba80fc1 -->

You should have finished [[backend/frameworks/axum/25-mcp-in-production-2|part 2]]: tools get a `Caller` and check scopes. This part leans on lesson 15 (idempotency keys), lesson 17 (Paystack checkout links) and lesson 20 (one-use rows deleted with `DELETE … RETURNING`).

After this part you will be able to:

1. Explain why one tool that orders and pays is dangerous, however good the model.
2. Build a quote that a second tool places exactly once.
3. Ask the person a question from a server with no sessions, with MCP's 2026-07-28 protocol, and fall back safely when the host can't ask.
4. Put the three layers together in one tool, in the right order.

## Where we stopped
<!-- bite: 2ff2efa0-b39f-4aae-8479-6c5f5fcc52e0 -->

The assistant arrives as Bayo, with his scopes, and can check his orders. Now Bayo asks it: "Order me two plates of jollof." Models misunderstand. "Is the jollof good there? Maybe two plates for me and Ada?" is a question, not an order. A model that orders anyway has spent Bayo's money on a guess. So before writing `place_order`, we decide what has to be true before money moves.

## Terms used in this part
<!-- bite: 83315a9b-3c0b-42c3-b7da-674e55f2e137 -->

1. **Elicitation**: This is an MCP feature where the server asks the person a question through the host's own screen ("Place this order?") and gets their answer, without the model being able to answer for them.
2. **Blast radius**: This is how much damage one mistake can do. We can't make the model perfect, so we make its blast radius small.

## Step 1: don't let one call spend money
<!-- bite: 7067b119-31f3-4c3f-97f7-28e7dff89a0d -->

Now the tool everyone's waiting for. Here's how **not** to write it:

```rust
// DON'T: one call, and money is committed
#[tool]
async fn order_food(&self, caller: Caller, Parameters(input): Parameters<OrderFood>) -> Result<String, String> {
    let order = self.orders.place(new_order(input), Some(caller.who.user_id), None).await?;
    // ...and charge a saved card
}
```

One misunderstanding, one injected sentence, one loop, and money moves. We'll build three layers instead, each one strong on its own.

## Step 2: layer 1, the AI can't pay
<!-- bite: aea4a923-a338-49ee-9851-76b914256f04 -->

The most important design decision costs nothing: **no tool can complete a payment.** `place_order` creates an unpaid order and returns lesson 17's Paystack checkout link. Bayo opens it and pays on Paystack's page, himself. If the AI misunderstood, the worst case is an unpaid order, and lesson 17's rule means the kitchen doesn't cook unpaid orders.

There's no saved-card tool, and there never will be one on this server. If Mama Put ever adds saved cards to the app, they stay out of MCP's reach.

## Step 3: layer 2, a quote, then an order
<!-- bite: 5dd3a41b-91e0-49f0-bd3f-f15be84654f1 -->

Ordering takes **two tools**:

1. **`prepare_order`** checks everything (the shop is open, the dish exists and is available, the quantity is allowed, the price) and returns a **quote**: a short summary and a `quoteId`, good for 5 minutes. It changes nothing.
2. **`place_order`** takes only the `quoteId`. It places exactly what the quote said, once.

```rust
    /// Checks a possible order and returns a quote with the total. Nothing is ordered or paid.
    /// Show the summary to the person, and only call place_order if they clearly say yes.
    #[tool(annotations(title = "Prepare an order (doesn't place it)", read_only_hint = true, open_world_hint = false))]
    async fn prepare_order(&self, caller: Caller, Parameters(input): Parameters<PrepareOrder>) -> Result<Json<PreparedOrder>, String> {
        let who = caller.may(Scope::OrdersWrite)?;
        // Before anything else: a quote the person says yes to, and then "closed", is no use to them.
        if !self.orders.is_open() {
            return Err(tool_error(OrderError::ShopClosed, ""));
        }
        if !(1..=MAX_AI_PLATES).contains(&input.quantity) {
            return Err(format!("An assistant can order 1 to {MAX_AI_PLATES} plates at a time."));
        }
        let dish = self.menu.get(input.dish_id).await.map_err(|e| tool_error(e, "Use search_menu to find dish ids."))?;
        if !dish.available || dish.portions_left < input.quantity {
            return Err(format!("{} has only {} plates left today.", dish.name, dish.portions_left.max(0)));
        }
        let quote = Quote {
            dish_id: dish.id,
            dish_name: dish.name,
            quantity: input.quantity,
            total: Kobo(dish.price.0 * i64::from(input.quantity)),
        };
        let quote_id = self.quotes.save(who.user_id, &quote).await.map_err(unexpected)?;
        Ok(Json(PreparedOrder {
            quote_id,
            summary: quote.describe(),
            total: format!("₦{}", quote.total.naira_text()),
            valid_for: "5 minutes".into(),
        }))
    }
```

The first check, `is_open`, wasn't in my first version. Running it for real at 5 a.m. Lagos time, `prepare_order` happily gave a quote, and `place_order` then said "The shop is closed; Mama Put opens at 7am." With a host that asks the person (layer 3, step 4), Bayo would have tapped "Place this order" and *then* been told no. So the opening-hours rule moved out of `OrderService::place` into a method both can use:

```rust
    /// Whether Mama Put takes orders right now: from 7am to 9pm in Lagos.
    pub fn is_open(&self) -> bool {
        let hour = self.clock.now().to_zoned_datetime(self.lagos.clone()).hour();
        (7..21).contains(&hour)
    }
```

The quotes live in Postgres, in the table the rest of `migrations/0012_mcp.sql` makes:

```sql
-- A quote: what an assistant may place, checked and priced by us, for five minutes, once.
CREATE TABLE mcp_quotes (
  id          text PRIMARY KEY,
  user_id     bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  dish_id     bigint NOT NULL REFERENCES dishes (id),
  quantity    integer NOT NULL,
  total_kobo  bigint NOT NULL,
  expires_at  timestamptz NOT NULL
);
```

and `src/mcp/spending.rs` keeps them:

```rust
/// Quotes, for five minutes each, for one person each.
#[derive(Clone)]
pub struct Quotes {
    pool: PgPool,
}

impl Quotes {
    pub fn new(pool: PgPool) -> Self {
        Quotes { pool }
    }

    /// Keeps a quote for `user_id`, and returns its id: 32 random characters, far too many to guess.
    pub async fn save(&self, user_id: i64, quote: &Quote) -> Result<String, StoreError> {
        let mut bytes = [0u8; 16];
        getrandom::fill(&mut bytes).expect("the operating system gives random bytes");
        let id = hex::encode(bytes);
        sqlx::query!(
            "INSERT INTO mcp_quotes (id, user_id, dish_id, quantity, total_kobo, expires_at)
             VALUES ($1, $2, $3, $4, $5, now() + interval '5 minutes')",
            id,
            user_id,
            quote.dish_id,
            quote.quantity,
            quote.total.0
        )
        .execute(&self.pool)
        .await?;
        Ok(id)
    }

    /// The quote, if it's this person's and still good. Leaves it where it is.
    pub async fn peek(&self, user_id: i64, id: &str) -> Result<Option<Quote>, StoreError> {
        let quote = sqlx::query_as!(
            Quote,
            r#"SELECT q.dish_id, d.name AS dish_name, q.quantity, q.total_kobo AS "total: Kobo"
               FROM mcp_quotes q JOIN dishes d ON d.id = q.dish_id
               WHERE q.id = $1 AND q.user_id = $2 AND q.expires_at > now()"#,
            id,
            user_id
        )
        .fetch_optional(&self.pool)
        .await?;
        Ok(quote)
    }

    /// Takes the quote: reads and deletes it in one statement, so it can be placed only once.
    pub async fn take(&self, user_id: i64, id: &str) -> Result<Option<Quote>, StoreError> {
        let quote = sqlx::query_as!(
            Quote,
            r#"WITH taken AS (
                 DELETE FROM mcp_quotes WHERE id = $1 AND user_id = $2 AND expires_at > now()
                 RETURNING dish_id, quantity, total_kobo
               )
               SELECT t.dish_id, d.name AS dish_name, t.quantity, t.total_kobo AS "total: Kobo"
               FROM taken t JOIN dishes d ON d.id = t.dish_id"#,
            id,
            user_id
        )
        .fetch_optional(&self.pool)
        .await?;
        Ok(quote)
    }
}
```

1. **Why Postgres, not Redis?** It's lesson 20's stream tickets again: tiny rows that live for minutes and are used once. Postgres never throws a row away to save memory (our cache Redis would), it's already in every test, and a quote can join `dishes` for its name.
2. **`take` is one statement.** `DELETE … RETURNING` reads and deletes together, so two calls with the same quote can't both get it. The `WITH` wraps the delete so the result can join `dishes`.
3. **The id is 16 random bytes**, far too many to guess. And every query has `user_id = $2` in it, so even a leaked quote id only works for its owner: Ada's assistant asking for Bayo's quote finds nothing.
4. **`peek` and `take`** are both there for a reason you'll see in step 4.

## Step 4: layer 3, asking the person
<!-- bite: c29ad70f-9889-4355-b900-4cbc88eef5b0 -->

Before placing, the server asks **Bayo**, not the model, through **elicitation**. The host shows Bayo a real question on its own screen, and only Bayo can answer it. The model can't press "yes" for him: its tool call carries arguments, and the answer comes back from the host in a separate field the model never writes.

There's a catch for our server. In older MCP versions, elicitation was the server sending a request to the client *in the middle of* a tool call, over an open session. Lesson 23 made our server **stateless**: no sessions, so nowhere for that request to go. The newest protocol version, **2026-07-28**, solved exactly this. Instead of asking mid-call, the tool **answers** "I need input first", with the question. The host asks the person, then makes the same call again with the answer attached. No session needed. rmcp supports both sides; rmcp's own docs call it a *multi round-trip request*.

Not every host speaks 2026-07-28, or supports elicitation, so we check first:

```rust
/// Can this host show the person a question and send back their answer? Asking without a session
/// needs protocol 2026-07-28 or later, and a host that says it supports elicitation.
fn can_ask_person(context: &RequestContext<RoleServer>) -> bool {
    let new_enough = context.protocol_version().is_some_and(|v| v.as_str() >= ProtocolVersion::V_2026_07_28.as_str());
    let can_elicit = context.client_capabilities().is_some_and(|c| c.elicitation.is_some());
    new_enough && can_elicit
}

/// "I need the person's answer first": the question, and which quote it's about.
fn ask_to_confirm(quote_id: &str, quote: &Quote) -> InputRequiredResult {
    let schema = ElicitationSchema::builder()
        .required_bool_with("confirm", |b| b.title("Place this order"))
        .build()
        .expect("a valid schema");
    let question = ElicitRequest::new(ElicitRequestParams::FormElicitationParams {
        meta: None,
        message: format!("Place this Mama Put order? {}. You'll pay on the next screen.", quote.describe()),
        requested_schema: schema,
    });
    let requests = BTreeMap::from([("confirm".to_owned(), InputRequest::Elicitation(question))]);
    InputRequiredResult::new(Some(requests), Some(format!("quote:{quote_id}")))
}
```

1. **`context.protocol_version()`** is the version this request was made with. In 2026-07-28 there's no `initialize` handshake: every request carries its version and the client's capabilities in its own `_meta`. rmcp reads them for us. Protocol versions are dates written `YYYY-MM-DD`, so comparing them as text puts them in date order.
2. **`context.client_capabilities()`** says what the host can do. Asking only makes sense if it has `elicitation`.
3. **`InputRequiredResult`** is the "I need input first" answer: a map of questions (here one, called `confirm`) and a **request state**, a string the host must send back unchanged with the answer.
4. **The question is a small form**: one required yes/no field. `ElicitationSchema::builder()` writes its JSON Schema, which the host turns into a checkbox or a button.
5. **The request state is `quote:<id>`**, so an answer can only be used for the quote it was asked about. rmcp's docs warn that the client echoes it back *as it likes*, so a server must never trust what's in it. We don't: it only says which quote, and the quote itself is checked against the person in Postgres.

## Step 5: `place_order`, all three layers together
<!-- bite: 752504cc-7834-4ccc-8de7-78297c5cc519 -->

```rust
    /// Places an order from a quote made by prepare_order, after the person has said yes.
    /// Returns a payment link the person must open to pay. The order isn't cooked until it's paid.
    #[tool(
        annotations(title = "Place a prepared order", read_only_hint = false, destructive_hint = false, idempotent_hint = false, open_world_hint = true),
        output_schema = schema_for_output::<PlacedOrder>()
    )]
    async fn place_order(
        &self,
        caller: Caller,
        context: RequestContext<RoleServer>,
        InputResponses(answers): InputResponses,
        RequestState(state): RequestState,
        Parameters(input): Parameters<PlaceOrder>,
    ) -> Result<CallToolResponse, String> {
        let who = caller.may(Scope::OrdersWrite)?;
        let quote = self.quotes.peek(who.user_id, &input.quote_id).await.map_err(unexpected)?;
        let quote = quote.ok_or(QUOTE_GONE)?;

        // Layer 3: ask the person, through the host, where the model can't answer for them.
        if can_ask_person(&context) {
            let asked_about_this = state.as_deref() == Some(format!("quote:{}", input.quote_id).as_str());
            let answer = answers.as_ref().and_then(|a| a.get("confirm")).filter(|_| asked_about_this);
            let Some(answer) = answer else {
                return Ok(ask_to_confirm(&input.quote_id, &quote).into());
            };
            if !said_yes(answer) {
                return Err("The person said no, so nothing was ordered.".into());
            }
        }

        // Layer 2: the quote is used exactly once, at the price we worked out.
        let quote = self.quotes.take(who.user_id, &input.quote_id).await.map_err(unexpected)?;
        let quote = quote.ok_or(QUOTE_GONE)?;
        let dish = self.menu.get(quote.dish_id).await.map_err(|e| tool_error(e, ""))?;
        if dish.price.0 * i64::from(quote.quantity) != quote.total.0 {
            return Err("The price changed since the quote. Use prepare_order again and show the person the new total.".into());
        }
        self.cap.reserve(who.user_id, quote.total).await.map_err(|e| match e {
            CapError::Reached => "That's more than an assistant may order in one day. The person can still order in the Mama Put app.".to_owned(),
            CapError::Store(e) => unexpected(e), // can't check the cap: no order
        })?;
        let new = NewOrder { dish_id: quote.dish_id, quantity: quote.quantity, source: Source::Mcp { client: caller.client.clone() } };
        let key = format!("mcp-{}", input.quote_id);
        let order = match self.orders.place(new, Some(who.user_id), Some(&key)).await {
            Ok(order) => order,
            Err(e) => {
                if let Err(e) = self.cap.give_back(who.user_id, quote.total).await {
                    tracing::error!(cause = %e, "couldn't give back an assistant's reservation");
                }
                return Err(tool_error(e, ""));
            }
        };

        // Layer 1: the assistant can't pay. The person opens the link.
        let checkout = self
            .payments
            .start_checkout(who, order.id)
            .await
            .map_err(|e| tool_error(e, "The order was placed; the person can pay for it in the Mama Put app."))?;
        let placed = PlacedOrder {
            order_id: order.id,
            total: format!("₦{}", order.total.naira_text()),
            pay_here: checkout.checkout_url,
            note: "Give the person this link to pay. The order is cooked once it's paid.".into(),
        };
        Ok(CallToolResult::structured(serde_json::to_value(placed).expect("plain data")).into())
    }
}
```

A tool can return `CallToolResponse`, rmcp's "either a finished result or a request for input". `ask_to_confirm(…).into()` makes the second, and `CallToolResult::structured(…).into()` the first. Because the return type no longer says what a finished result looks like, `output_schema = schema_for_output::<PlacedOrder>()` tells the model by hand.

Follow Bayo's order through it, as a test does:

1. The model calls `prepare_order` with dish 1, quantity 2, and gets back `"summary": "2 × Jollof rice, total ₦3,000.00"` and a quote id.
2. It shows Bayo the summary; he says "yes". It calls `place_order` with the quote id.
3. The host speaks 2026-07-28 and supports elicitation, and there's no answer yet, so the tool returns the question. **Nothing is placed.** The host shows Bayo: *Place this Mama Put order? 2 × Jollof rice, total ₦3,000.00. You'll pay on the next screen.* He taps "Place this order".
4. The host calls `place_order` again, with the answer and the request state. Now the quote is **taken** (gone from the table), the price is checked again, the daily cap is checked, the order is placed, and a Paystack link comes back.
5. If the model calls `place_order` with the same quote again, the quote is gone: "That quote has expired or was already used. Use prepare_order to make a new one."

Look at what each detail buys:

1. **`place_order` takes only a quote id.** The model can't slip in a different dish or quantity at the last step; the server places exactly what was quoted.
2. **`peek` before asking, `take` after.** If Bayo says no, or the host never sends an answer, the quote isn't used up; it just runs out after 5 minutes. Only a yes uses it.
3. **The price is checked again after `take`.** The quote promised Bayo ₦3,000. If the kitchen changed the price in those minutes, `place` would charge the new one, and Bayo would have said yes to a different total. So: a new quote, and a new yes.
4. **The idempotency key is `mcp-` plus the quote id.** `take` already stops a second placing; if something ever gets past it, lesson 15's unique `(customer_id, idempotency_key)` index still means one order at most.
5. **At most 5 plates, `MAX_AI_PLATES`**, lower than the app's 20. AI orders get tighter limits than people tapping buttons.
6. **The description says "only call place_order if they clearly say yes".** That's an instruction to the model, and good models follow it. But we don't *rely* on it: layers 1 and 3 hold even if the model ignores it, and layer 2 holds even if the host can't ask.
7. **Annotations**: `place_order` says `read_only_hint = false` and `open_world_hint = true` (it reaches out to Paystack). Many hosts ask the person before running such a tool anyway, which is one more check, from the host's side.
8. **Without elicitation**, layers 1 and 2 remain: the model must have made a quote, shown it, and used it once, and Bayo still has to pay on Paystack's page himself.

## The Rust in this part
<!-- bite: 82336afa-7e6f-4899-82f2-b0e4b53c8d3d -->

1. **More extractors**: `context: RequestContext<RoleServer>`, `InputResponses(answers): InputResponses` and `RequestState(state): RequestState`. rmcp fills each from the call, in any order.
2. **`Result<CallToolResponse, String>`**: a tool that may finish, or may ask for input first. `ask_to_confirm(…).into()` and `CallToolResult::structured(…).into()` both become a `CallToolResponse`, through rmcp's `From` impls.
3. **`output_schema = schema_for_output::<PlacedOrder>()`** in `#[tool(...)]`: says by hand what a finished result looks like, when the return type can't.
4. **`Option::filter`**: `answers…get("confirm").filter(|_| asked_about_this)` keeps the answer only if it's about this quote.
5. **`let … else`**: `let Some(answer) = answer else { return …; };` takes the value out, or leaves the function.
6. **`BTreeMap::from([(key, value)])`**: a map from an array of pairs, for the questions.
7. **`ok_or(QUOTE_GONE)?` with a `&str` constant**: turns "no quote" into the tool's error, a `String`, through `?`'s `From`.

## Your project so far
<!-- bite: f9c659c1-4196-463a-b642-e6b9f6361b19 -->

```text
mama-put/
├── migrations/
│   └── 0012_mcp.sql              ← mcp_quotes
└── src/
    ├── orders/service.rs         ← is_open(), used by place and by prepare_order
    └── mcp/
        ├── orders.rs             ← prepare_order, place_order, can_ask_person, ask_to_confirm, said_yes
        └── spending.rs           ← NEW: Quote, Quotes (save, peek, take) (the daily cap comes in part 4)
```

## Common mistakes
<!-- bite: 0ac853b1-ec4b-42ec-a3bc-3ebf1251f2c2 -->

1. **One tool that orders and pays.** Quote, then order; and payment only on the person's own screen.
2. **Letting `place_order` take a dish and a quantity.** Then the model can change them at the last step. Take only the quote.
3. **Using up the quote before asking.** A "no" or a host that never answers would waste it. `peek` first, `take` after a yes.
4. **Asking "the user" through the model.** A steered model reports a yes. Ask through the host, with elicitation.
5. **Assuming every host can ask.** Check the protocol version and capabilities, and make the other layers enough on their own.
6. **Trusting the request state.** The client sends it back as it likes. Use it only to say which quote, and check the quote itself.
7. **A quote that can go stale silently.** Check the shop is open before quoting, and the price again before placing.

## Check your understanding
<!-- bite: abad04ac-2dc1-4926-bb23-4131e91489c3 -->

1. Why does `place_order` take only a quote id?
2. Why does it `peek` before asking and `take` after?
3. Our server is stateless. How can it still ask Bayo "Place this order?", and what happens with a host that can't?
4. Why does `can_ask_person` check the protocol version as well as the capabilities?
5. The price of jollof changes between the quote and the yes. What happens, and why?

<details>
<summary>Answers, after your attempt</summary>

1. So the model can't change the dish, quantity or price at the last step: the server places exactly what it quoted, at the price it worked out.
2. `peek` leaves the quote unused while we ask, so a "no", or a host that never sends an answer, doesn't waste it; it just runs out. `take` (`DELETE … RETURNING`) after a yes means it can be placed only once.
3. With protocol 2026-07-28's "input required" answer: the tool returns the question instead of placing anything; the host asks Bayo and calls the tool again with his answer and the request state, no session needed. A host without it gets no question, and the quote, the 5-plate limit, the cap and the Paystack page still stand.
4. Because the "input required" answer only exists in 2026-07-28 and later. An older host may support elicitation the old way (mid-call, over a session), which our stateless server can't do, and rmcp won't send an "input required" answer to it.
5. `place_order` checks the price again after taking the quote, sees the total differs, and refuses: "The price changed since the quote". Bayo said yes to ₦3,000, not to the new price, so he needs a new quote and a new yes.

</details>

## Practice
<!-- bite: 616db002-f567-40f0-9487-1f99212212db -->

1. Add a scheduled job (lesson 18) that finds `placed_via = 'mcp'` orders still unpaid after 30 minutes and gives their plates back, so a confused assistant can't hold the last plates of jollof.
2. Add `cancel_order(orderId)` for unpaid orders only, with its own scope, and decide: does it need the person's confirmation? Write down why.
3. Change the question so the person can also change the quantity on the host's screen. What would `place_order` then have to check?

**Done when** you can follow Bayo's order through the five steps in step 5, and say which layer still holds when the model ignores the description, and which when the host can't ask. The code runs and is tested in part 5.

## Before moving on
<!-- bite: 644e25d4-217f-43ac-87b1-f5097387c252 -->

A model can no longer spend Bayo's money on a misunderstanding: it can't pay, it can only place what it was quoted, and the person says yes on their own screen. But a misunderstanding isn't the only danger. Someone else's words can end up in the model's input and try to steer it, and a model stuck in a loop can call us a thousand times. Part 4 is about both.

## Related
<!-- bite: 7c48681d-3670-468c-91a9-dff6a1be021b -->

- [[backend/frameworks/axum/27-mcp-in-production-4|Next: MCP in Production 4: Prompt Injection and Limits]]
- [[backend/frameworks/axum/17-payments-and-webhooks|Payments and Webhooks]] — the checkout link the assistant hands over instead of paying
- [[backend/frameworks/axum/20-real-time|Real-time Updates]] — stream tickets, the first one-use rows
- [[backend/frameworks/axum/15-idempotency|Idempotency]] — the unique key that backs up `take`

## About this lesson
<!-- bite: 36277fdd-509b-412f-8802-0868f641624e -->

**Level:** Advanced. Part 3 of 5 on MCP in production, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96) and rmcp 3.11 (protocol 2026-07-28 for asking the person without sessions). Covers why one call must never spend money, three layers against spending on a guess (no payment by the AI, one-use quotes in Postgres, elicitation through multi round-trip requests on a stateless server, with a check for hosts that can't ask), checking opening hours before quoting and the price again before placing, and the order of the checks inside `place_order`.
