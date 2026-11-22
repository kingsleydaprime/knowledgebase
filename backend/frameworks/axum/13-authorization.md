---
id: 44ea9e19-e886-4efa-a03f-ebb092bfeee7
---

# Authorization

**Authorization means deciding what someone may do, once you know who they are: Ada may read her own order but not Bayo's, the cook may change the menu, only Mama may make someone staff.** The rules are a **policy**, and the best place for a policy is one place, written down, tested cell by cell. In Rust, each permission can also be a **type**. A handler that takes `Can<MenuWrite>` can't run for anyone without that permission, exactly as lesson 12's `AuthUser` can't run for anyone logged out.

## Before you start
<!-- bite: bb9d4026-ea9a-4b49-8b8c-801c8c0c4060 -->

You should have:

1. Finished [[backend/frameworks/axum/12-authentication|lesson 12]], so customers can sign up and log in, and v2 orders need an `AuthUser`.
2. Met generics with trait bounds, and lesson 10's associated types.

After this lesson you will be able to:

1. Write a policy as one function over roles, actions and owners, and test every cell.
2. Turn permissions into types, with a `Can<P>` extractor.
3. Give each API version its own kitchen guard, with a **generic associated type**.
4. Check ownership in the service, and answer 404, not 403, for someone else's order.
5. Say when an API should answer 401, 403 or 404.
6. Change roles safely.

## Where we stopped
<!-- bite: a6c290ed-98c0-486b-ac2e-b5a545822077 -->

Three holes:

1. **Ada can read Bayo's order.** She's logged in, so `GET /v2/orders/7` works for her, even though order 7 is Bayo's. Orders are numbered, so she can read every order by counting.
2. **The kitchen shares one key.** The cook who started yesterday has the same power as Mama, and when one person leaves, the key has to change for everyone.
3. **There's no "my orders".** `GET /v2/orders` is the kitchen's list or nothing.

## The kid version
<!-- bite: f5e42671-22ce-42ce-aae8-97d71b60b764 -->

Mama's stall has three kinds of people. Customers order and collect their own food. Staff cook, and can change the menu board. Mama, the owner, can also decide who's staff.

A customer can ask "is my jollof ready?", but not "what did the man before me order?". If he asks, the answer is "I don't know what you mean", not "that's private", because "that's private" tells him there *was* a man before him, with an order.

**Where the picture stops working.** At the stall, Mama recognises faces. Our server only sees tokens, so the role must be in the token, and a promotion only reaches the token at the next refresh, within 15 minutes.

## Terms used in this lesson
<!-- bite: 6aab4b2c-cd9b-45b2-81a7-ce4bc629cc96 -->

1. **Policy**: This is the full set of rules for who may do what.
2. **Role**: This is a label on a user that the policy reads: customer, staff or admin. It's a coarse grouping; real systems often add finer permissions later.
3. **Action**: This is one thing that might be allowed, like "change the menu" or "read an order".
4. **Route-level check**: This is a check that only needs to know *who* is asking: "is this staff?". It can happen before the handler runs.
5. **Object-level check**: This is a check that needs the thing itself: "is this Ada's order?". It can only happen after it's loaded.
6. **Generic associated type**: This is an associated type that takes its own type parameter, like `type Kitchen<P>`. Each implementation says what it is for every `P`.

## Step 1: write the policy down, in one place
<!-- bite: 3ce08fbe-157c-4a1d-82b6-f59b6069dcc9 -->

Before code, the table. This is the conversation to have with Mama, not with the compiler:

| Action | customer | staff | admin |
|---|---|---|---|
| read the menu | yes (even logged out) | yes | yes |
| `MenuWrite` (add, change, remove dishes) | no | yes | yes |
| `OrderRead` one order | **only their own** | yes | yes |
| `OrderListAll` (everyone's orders) | no | yes | yes |
| `OrderUpdateStatus` | no | yes | yes |
| `UserChangeRole` | no | no | yes |

Reading the menu isn't in the policy, because it isn't protected. Placing an order isn't either: who may order is the version's `Customer` (lesson 12).

Now the table as code, exactly. `src/auth/policy.rs`:

```rust
/// Everything someone might be allowed to do. Reading the menu and placing an order aren't here:
/// anyone may read the menu, and who may order is the version's `Customer`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Action {
    MenuWrite,
    OrderRead,
    OrderListAll,
    OrderUpdateStatus,
    UserChangeRole,
}

/// May `who` do `action` to something owned by `owner` (`None`: owned by nobody, like the menu)?
pub fn allows(who: Identity, action: Action, owner: Option<i64>) -> bool {
    let staff = matches!(who.role, Role::Staff | Role::Admin);
    let owns = owner == Some(who.user_id);
    match action {
        Action::MenuWrite | Action::OrderListAll | Action::OrderUpdateStatus => staff,
        Action::OrderRead => staff || owns,
        Action::UserChangeRole => who.role == Role::Admin,
    }
}
```

1. **One function, one `match`.** The whole policy is eight lines anyone can read, and Mama could check it against the table.
2. **The `match` must cover every action.** Add `Action::RefundOrder` next month, and this function won't compile until you've decided who may.
3. **`owner == Some(who.user_id)`**: an order with no customer (`None`, from v1) is owned by nobody, so only staff may read it.

And the test that holds it to the table, every cell:

```rust
    /// The policy table from the lesson, every cell of it.
    #[test]
    fn the_policy_is_the_table() {
        let ada = Identity { user_id: 1, role: Role::Customer };
        let cook = Identity { user_id: 2, role: Role::Staff };
        let mama = Identity { user_id: 3, role: Role::Admin };
        let adas_order = Some(1);

        for action in Action::ALL {
            let (customer, staff, admin) = match action {
                Action::MenuWrite | Action::OrderListAll | Action::OrderUpdateStatus => (false, true, true),
                Action::OrderRead => (false, true, true), // someone else's order
                Action::UserChangeRole => (false, false, true),
            };
            assert_eq!(allows(ada, action, Some(99)), customer, "customer, {action:?}");
            assert_eq!(allows(cook, action, Some(99)), staff, "staff, {action:?}");
            assert_eq!(allows(mama, action, Some(99)), admin, "admin, {action:?}");
        }
        assert!(allows(ada, Action::OrderRead, adas_order), "a customer may read their own order");
        assert!(!allows(ada, Action::OrderListAll, adas_order), "owning an order doesn't make you the kitchen");
    }
```

The test's `match` is the table, written a second time, independently of `allows`. If someone "simplifies" `allows` and changes a cell, this fails and says which one. (`Action::ALL` is a constant array of every action, like lesson 8's `Status::ALL`.)

## Step 2: permissions as types
<!-- bite: 0a07ec93-0e6a-4fd1-8a6c-343439d2a535 -->

Route-level checks need only the caller, so they can be extractors, like `AuthUser`. But there are several permissions, and writing an extractor for each would be four copies of the same code. Instead, each permission becomes a small type, and one extractor takes it as a parameter:

```rust
/// A permission as a type, so a route can ask for it in its arguments.
pub trait Permission: Send + Sync + 'static {
    const ACTION: Action;
}

pub struct MenuWrite;
pub struct OrderListAll;
pub struct OrderUpdateStatus;
pub struct UserChangeRole;

impl Permission for MenuWrite {
    const ACTION: Action = Action::MenuWrite;
}
```

(and the same three-line `impl` for the other three.) Then:

```rust
/// A logged-in user who may do `P`. A handler that takes `Can<MenuWrite>` can't run for anyone else:
/// no token is a 401, a token without the permission is a 403.
pub struct Can<P: Permission>(pub Identity, PhantomData<P>);

impl<S, P> FromRequestParts<S> for Can<P>
where
    S: Send + Sync,
    Keys: FromRef<S>,
    P: Permission,
{
    type Rejection = ApiError;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let AuthUser(who) = AuthUser::from_request_parts(parts, state).await?;
        if allows(who, P::ACTION, None) {
            Ok(Can(who, PhantomData))
        } else {
            Err(ApiError::new(StatusCode::FORBIDDEN, "forbidden", "Not allowed", "Your account can't do that."))
        }
    }
}
```

1. **It runs `AuthUser` first.** No token, or a bad one, is lesson 12's 401.
2. **Then the policy, with `P::ACTION`.** `Can<MenuWrite>` checks `Action::MenuWrite`; `Can<UserChangeRole>` checks `Action::UserChangeRole`. One extractor, any permission.
3. **`PhantomData<P>`**, as in lesson 10: `Can` is *about* `P` but stores nothing of it. Because that field is private, code outside `policy.rs` can't build a `Can` by hand (`Can(fake_admin, PhantomData)` doesn't compile there), so the only way to get one is through the extractor, which checked.
4. **The permission is in the type.** The `MenuWrite` in a handler's arguments is the documentation, the check and the guarantee, all at once.

## Step 3: a kitchen guard per version
<!-- bite: 70f1d20c-23d0-47f8-a5d3-3ddf3da253dd -->

v2's kitchen should use roles. v1 is frozen: its kitchen screen sends the shared staff key, and taking that away is a breaking change. So the kitchen guard differs per version, and it's lesson 10's tool again: an associated type in `ApiVersion`. With one new twist, because each kitchen route needs a *different* permission. In `src/version.rs`:

```rust
    /// Who may do kitchen work `P` (change the menu, move orders on): v1's shared staff key,
    /// or, in v2, a logged-in user whose role allows `P`.
    type Kitchen<P: Permission>: Send;
```

```rust
impl ApiVersion for V1 {
    const PREFIX: &'static str = "/v1";
    type Customer = Anyone;
    type Kitchen<P: Permission> = StaffKeyHeader;
}

impl ApiVersion for V2 {
    const PREFIX: &'static str = "/v2";
    type Customer = AuthUser;
    type Kitchen<P: Permission> = Can<P>;
}
```

**`type Kitchen<P: Permission>`** is a **generic associated type**: an associated type with a parameter of its own. For v2, `Kitchen<MenuWrite>` is `Can<MenuWrite>` and `Kitchen<OrderUpdateStatus>` is `Can<OrderUpdateStatus>`. For v1, every `Kitchen<P>` is `StaffKeyHeader`, ignoring `P`: the staff key could always do everything.

`StaffKeyHeader` is lesson 3's `kitchen_only` middleware, turned into an extractor, in `src/http/mod.rs`:

```rust
/// v1's kitchen: whoever sends the shared staff key. v2 uses roles instead (lesson 13).
pub struct StaffKeyHeader;

impl<S> FromRequestParts<S> for StaffKeyHeader
where
    S: Send + Sync,
    StaffKey: FromRef<S>,
{
    type Rejection = ApiError;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let key = StaffKey::from_ref(state);
        let given = parts.headers.get("x-staff-key").map(|v| v.as_bytes()).unwrap_or_default();
        if given.ct_eq(key.0.as_bytes()).into() {
            Ok(StaffKeyHeader)
        } else {
            Err(ApiError::new(StatusCode::UNAUTHORIZED, "staff-only", "Kitchen staff only", "Send the staff key in X-Staff-Key."))
        }
    }
}
```

Same constant-time comparison, same answer. It finds the key in `AppState` with `FromRef`, so the routers no longer need the key passed in.

### The menu router, simpler than before

```rust
/// The menu's routes for one API version: reads for everyone, writes for the version's kitchen.
/// The same handlers serve every version; `V` decides the shapes at the door.
pub fn router<S, V>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    MenuService: FromRef<S>,
    V: MenuVersion,
    V::Kitchen<MenuWrite>: FromRequestParts<S>,
{
    Router::new()
        .route("/menu", get(list::<V>).post(add::<V>))
        .route("/menu/specials", get(specials::<V>))
        .route("/menu/{id}", get(get_one::<V>).patch(change::<V>).delete(remove::<V>))
}
```

The public and kitchen routers from lesson 3, merged and with a `route_layer` on one, are gone. There's one router, because the guard isn't a layer any more: it's in each handler's arguments.

```rust
async fn add<V: MenuVersion>(
    _kitchen: V::Kitchen<MenuWrite>,
    State(menu): State<MenuService>,
    ValidatedJson(new): ValidatedJson<V::NewDish>,
) -> Result<impl IntoResponse, ApiError> {
```

**`_kitchen: V::Kitchen<MenuWrite>`**: the underscore says "we don't use the value, only the fact that it exists". `add::<V2>` can't run without a user allowed `MenuWrite`; `add::<V1>` can't run without the staff key. `change` and `remove` take the same argument. A new kitchen route without it would be open to everyone, so that's the one line to look for in a review; but at least it's visible in the function's signature, not hidden in a layer somewhere else.

The `where` line `V::Kitchen<MenuWrite>: FromRequestParts<S>` promises Axum the guard can be extracted, whatever the version. Lesson 3's `kitchen_only` and `route_layer` are deleted.

## Step 4: object-level checks, in the service
<!-- bite: 2b307e1e-c4ec-463e-abe6-a5c6c1fa3e1b -->

"Is this Ada's order?" can't be checked before the order is loaded. So it goes in the service, in `src/orders/service.rs`:

```rust
    /// One order, if `who` may see it. Someone else's order is "not found", not "forbidden":
    /// a customer shouldn't even learn that order 7 exists.
    pub async fn get(&self, id: i64, who: Identity) -> Result<Order, OrderError> {
        match self.store.find(id).await? {
            Some(order) if allows(who, Action::OrderRead, order.customer_id) => Ok(order),
            _ => Err(OrderError::NotFound(id)),
        }
    }
```

1. **The same `allows`**, with the order's owner. The policy stays in one place; the service only asks it.
2. **`Some(order) if ... =>`**: a match guard. A missing order and someone else's order both fall to `_`, and both are `NotFound`.
3. **`get` takes the `Identity`**, so there's no way to call it without saying who's asking. A background job that needs any order would get its own method, named for what it does.

The handler asks for the user, in both versions:

```rust
async fn get_one<V: OrderVersion>(
    AuthUser(who): AuthUser,
    State(orders): State<OrderService>,
    Path(id): Path<i64>,
) -> Result<Data<V::Order>, ApiError> {
    Ok(Data(orders.get(id, who).await?.into()))
}
```

**This is a breaking change for v1, made on purpose.** `GET /v1/orders/{id}` was the hole itself: anyone, logged in or not, could read any order by counting. A v1 customer, who orders without logging in, can no longer look their order up later; their app shows the order from the `POST` response, and they collect at the counter as before. That's a real loss for v1 clients, and the right trade: a hole that leaks every customer's orders doesn't stay open because closing it is inconvenient. Tell v1's users through the deprecation `Link` from lesson 10, and point them to v2.

### Lists, scoped in the database

`GET /orders` now serves two people: the kitchen gets every order; Ada's phone gets Ada's. v1's list stays the kitchen's, behind the staff key. So the list has a per-version type too, in `src/orders/versions.rs`:

```rust
pub trait OrderVersion: ApiVersion {
    type Order: Serialize + From<Order> + Send;
    /// Who may list orders, and which they see: v1's kitchen sees all; in v2, anyone logged in,
    /// with customers seeing only their own.
    type Lister: Lister + Send;
}

impl OrderVersion for V1 {
    type Order = OrderV1;
    type Lister = StaffKeyHeader;
}

impl OrderVersion for V2 {
    type Order = OrderV2;
    type Lister = AuthUser;
}

/// Someone asking for the list of orders.
pub trait Lister {
    /// `None`: every order. `Some(id)`: only that customer's.
    fn only_customer(&self) -> Option<i64>;
}

impl Lister for StaffKeyHeader {
    fn only_customer(&self) -> Option<i64> {
        None
    }
}

impl Lister for AuthUser {
    fn only_customer(&self) -> Option<i64> {
        if allows(self.0, crate::auth::Action::OrderListAll, None) { None } else { Some(self.0.user_id) }
    }
}
```

`OrderFilter` gains `customer_id: Option<i64>`, the handler fills it with `lister.only_customer()`, and the store adds one optional condition to lesson 9's checked query:

```rust
               WHERE ($1::text IS NULL OR status = $1) AND ($4::bigint IS NULL OR customer_id = $4) AND id > $2
```

The scoping is in the SQL, not a filter in Rust after loading. A customer's request never reads anyone else's rows, and the cursor and page size work exactly as before. `set_status` takes `_kitchen: V::Kitchen<OrderUpdateStatus>`. And the orders router lists what its handlers need:

```rust
pub fn router<S, V>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    OrderService: FromRef<S>,
    Keys: FromRef<S>,
    V: OrderVersion,
    V::Customer: FromRequestParts<S>,
    V::Lister: FromRequestParts<S>,
    V::Kitchen<OrderUpdateStatus>: FromRequestParts<S>,
{
    Router::new()
        .route("/orders", post(place::<V>).get(list::<V>))
        .route("/orders/{id}", get(get_one::<V>))
        .route("/orders/{id}/status", patch(set_status::<V>))
}
```

Read the `where` lines as the orders feature's security summary: who may place, who may list, who may move orders on.

A database test for ownership, in the service's tests:

```rust
        let adas = orders.place(NewOrder { dish_id: 1, quantity: 1 }, Some(ada.user_id)).await.unwrap();

        assert!(orders.get(adas.id, ada).await.is_ok());
        assert!(matches!(orders.get(adas.id, bayo).await, Err(OrderError::NotFound(_))), "not 403: Bayo mustn't learn it exists");
        assert!(orders.get(adas.id, cook).await.is_ok());
```

## Step 5: 401, 403 or 404?
<!-- bite: 48afbe47-a5fe-4fcb-bbbe-042418f8b37c -->

Three answers that are easy to mix up:

1. **401 Unauthorized** means "I don't know who you are". No token, a bad one, an expired one. The fix is to log in. (The name is old and wrong; it really means unauthenticated.)
2. **403 Forbidden** means "I know who you are, and you may not". Ada changing the menu. The fix is a different account.
3. **404 Not Found** means "there's nothing here *for you*". Use it instead of 403 when even admitting the thing exists would leak something. Bayo asking for Ada's order gets 404, because "403" would tell him order 6 exists and belongs to someone.

So: a route that's forbidden for your role (the kitchen's routes) is 403, because everyone knows the menu can be changed. A *thing* you may not see (someone's order) is 404.

## Step 6: changing roles, safely
<!-- bite: 8a5178ed-0eec-4c4d-8e2e-327b43cdac8b -->

Someone has to make the cook staff. A new route, admins only, in `src/auth/handlers.rs`:

```rust
async fn change_role(
    admin: Can<UserChangeRole>,
    State(auth): State<AuthService>,
    Path(id): Path<i64>,
    ValidatedJson(body): ValidatedJson<RoleChange>,
) -> Result<Data<UserV2>, ApiError> {
    Ok(Data(auth.change_role(admin.0, id, body.role).await?.into()))
}
```

at `PATCH /v2/admin/users/{id}/role`, with a `RoleChange { role: Role }` body. (`admin.0` and not a pattern, because `Can`'s second field is private.) The service:

```rust
    /// Gives a user a new role. The caller has already been checked: only admins get here.
    /// Nobody changes their own, so the last admin can't lock everyone out by accident.
    pub async fn change_role(&self, admin: Identity, user_id: i64, role: Role) -> Result<User, AuthError> {
        if admin.user_id == user_id {
            return Err(AuthError::OwnRole);
        }
        let user = self.store.set_role(user_id, role).await?.ok_or(AuthError::NoSuchUser(user_id))?;
        // Their refresh tokens still work; the next refresh reads the new role (within 15 minutes).
        tracing::info!(admin = admin.user_id, user_id, ?role, "role changed");
        Ok(user)
    }
```

1. **Nobody changes their own role.** An admin who demotes themselves by mistake, when they're the only admin, leaves nobody able to fix it. And a role change is a decision two people should agree on.
2. **It's logged**, with who did it. Role changes are exactly the events someone will ask about later.
3. **The new role reaches the user within 15 minutes**, at their next refresh, because lesson 12's `refresh` reads the role from the database. To take power away *now* (a cook who's just been fired), also revoke their refresh tokens: practice 2.

The very first admin can't be made through the API (nobody's an admin yet to do it). That's done once, by hand, by whoever runs the database:

```sql
UPDATE users SET role = 'admin' WHERE email = 'mama@example.com';
```

### The docs

In `docs.rs`, v2's kitchen routes change from `staff_key` to `bearer` security, with a 403 response each; `get_order` and `list_orders` say they need a login, and `list_orders` says customers see only their own; `change_role` is described; and the `staff_key` scheme goes, because only undocumented v1 uses it. The docs test now checks 15 operations.

## Trying it
<!-- bite: 0defb1c0-0600-40e5-ba8b-8b9dd67b71c7 -->

From a run of this lesson's code, with Ada and Bayo as customers and Mama made admin by hand:

```text
Ada adds a dish                    → 403 forbidden
Mama adds a dish                   → 201
v1 kitchen with the staff key      → 200
v1 kitchen, no key                 → 401 staff-only
Bayo reads Ada's order 6           → 404 order-not-found     ← not 403
Ada reads her order 6              → 200
Ada's list                         → {"data":[{"id":6,...}],"meta":{"limit":20}}
Mama's list                        → orders 1, 2, 3, 4, 5, 6, 7
Ada moves an order on              → 403 forbidden
Mama makes Bayo staff              → 200 {"data":{"id":2,"email":"bayo@example.com","name":"bayo","role":"staff"}}
Mama changes her own role          → 409 own-role
Ada tries admin                    → 403 forbidden
```

`cargo test` runs 22.

## The Rust in this lesson
<!-- bite: 4bb54383-7569-4094-a190-7acd063f0ae8 -->

1. **A policy as one `match`** over an enum, and **a test that restates it** independently.
2. **Marker types and a trait with an associated constant**, `struct MenuWrite;` and `const ACTION: Action`, so a permission can be a type parameter.
3. **A generic extractor, `Can<P: Permission>`**, using `P::ACTION`.
4. **A private `PhantomData` field**, so a value can only be built where it's checked.
5. **Generic associated types, `type Kitchen<P: Permission>: Send;`**, and the bound `V::Kitchen<MenuWrite>: FromRequestParts<S>`.
6. **An extractor that calls another**, `AuthUser::from_request_parts(parts, state).await?` inside `Can`'s.
7. **`_kitchen: ...`**: an argument kept only for what extracting it proves.
8. **Match guards with an `Option` pattern**, `Some(order) if allows(...) =>`.
9. **`?role` in `tracing::info!`**: record a field with its `Debug` text.

## Your project so far
<!-- bite: 4c692db9-eaed-46ea-8e42-e1c6888ba27f -->

```text
mama-put/
└── src/
    ├── lib.rs             ← routers no longer take the staff key
    ├── version.rs         ← + type Kitchen<P: Permission>: StaffKeyHeader in v1, Can<P> in v2
    ├── docs.rs            ← bearer on v2's kitchen routes, 403s, change_role; checks 15
    ├── http/mod.rs        ← StaffKeyHeader extractor; kitchen_only gone
    ├── auth/
    │   ├── policy.rs      ← Action, allows, Permission, the four permissions, Can<P>; the table test
    │   ├── store.rs       ← + set_role
    │   ├── service.rs     ← + change_role, OwnRole
    │   └── handlers.rs    ← + PATCH /admin/users/{id}/role
    ├── menu/handlers.rs   ← one router; add, change, remove take V::Kitchen<MenuWrite>
    └── orders/
        ├── versions.rs    ← + type Lister; Lister for StaffKeyHeader and AuthUser
        ├── model.rs       ← OrderFilter.customer_id
        ├── store.rs       ← list scoped by customer_id in SQL
        ├── service.rs     ← get(id, who) with the ownership check; 1 more test
        └── handlers.rs    ← get_one takes AuthUser; list takes V::Lister; set_status takes V::Kitchen
```

## Common mistakes
<!-- bite: 018824dd-aade-4960-adb6-11cf53f57080 -->

1. **Checks scattered through handlers.** `if user.role == "staff"` in twelve places, slightly different in two. One policy function.
2. **Checking the role but not the owner.** "Any logged-in user may read orders" reads every order.
3. **403 for things that shouldn't be known to exist.** Say 404.
4. **Scoping a list in Rust after loading it.** It reads everyone's rows, and paging breaks. Scope in the SQL.
5. **Trusting a role sent by the client.** The role comes from our token, which came from our database.
6. **Letting users change their own role.** The last admin locks everyone out, or a staff member makes themselves admin.
7. **A permission check that can be forgotten.** Put it in the handler's arguments, as a type.
8. **Keeping a hole open for compatibility.** A frozen version still gets security fixes, even breaking ones.

## Check your understanding
<!-- bite: b64e7e19-94c3-4690-a8b3-af4b913db356 -->

1. Why write the policy as one function with one `match`, and why does its test restate the table instead of calling a helper?
2. What does `Can<MenuWrite>` check, in what order, and what does each failure answer?
3. Why can't code outside `policy.rs` make a `Can<UserChangeRole>` without going through the extractor?
4. What is `type Kitchen<P: Permission>`, and why does v1's ignore `P`?
5. Why is "is this Ada's order?" checked in the service and not in an extractor?
6. Bayo asks for Ada's order. Why 404 and not 403?
7. Why does a customer's `GET /v2/orders` filter by `customer_id` in SQL rather than in Rust?
8. Why may nobody change their own role?

<details>
<summary>Answers, after your attempt</summary>

1. So the whole policy is in one place, readable against the table, and the compiler forces a decision for every new action. The test restates the table independently so that a change to `allows` that alters a cell fails the test; a test that called the same logic would agree with any mistake.
2. First `AuthUser`: no token or a bad one is a 401. Then `allows(who, Action::MenuWrite, None)`: a role without the permission is a 403. Only then does the handler run.
3. Because `Can`'s second field, the `PhantomData`, is private to `policy.rs`, so `Can(identity, PhantomData)` can't be written elsewhere. The only way to get one is the extractor, which checks.
4. A generic associated type: an associated type that takes its own parameter. For v2 it's `Can<P>`, a different permission check per route. v1's is `StaffKeyHeader` for every `P`, because the shared staff key always could do every kitchen job.
5. Because it needs the order itself: who owns it is only known after loading it. Route-level checks need only the caller; object-level checks need the object.
6. Because 403 says "this exists and you may not see it", which tells Bayo there's an order 6 and that it belongs to someone. 404 says nothing at all.
7. So the query only ever reads that customer's rows, and the cursor and page size work on the right set. Filtering in Rust would load everyone's orders, and a page could come back nearly empty.
8. An admin who demotes themselves by mistake could leave nobody able to fix it, and a role change should be a decision by someone other than the person it benefits.

</details>

## Practice
<!-- bite: 5616b92d-0aef-445c-b047-b87dabc581ce -->

1. Add `GET /v2/admin/users` for admins: a cursor-paginated list of users (id, email, name, role), using lesson 9's cursor. Never select `password_hash`.
2. When a role changes, also revoke that user's refresh tokens, so a demotion takes effect at once instead of within 15 minutes. What does the user see?
3. Give anonymous v1 orders a way back: return a random `trackingCode` from `POST /v1/orders` (lesson 12's `new_refresh_token` style, stored as a hash), and let `GET /v1/orders/{id}?code=...` show the order if it matches. Is this a breaking change for v1?
4. Add a `Role::Cashier` who may move orders to "collected" but not change the menu. What does the compiler make you decide?
5. Write a `oneshot` test that `PATCH /v2/menu/1` answers 401 with no token, 403 for a customer's token and 200 for staff.

**Done when** the policy is one tested function, v2's kitchen routes take `Can<...>` and v1's take the staff key through the same handlers, customers read only their own orders (404 for others') and list only their own, staff see everything, admins can change roles but not their own, and `cargo test` passes.

## Before moving on
<!-- bite: 2748319c-2e6c-40a6-8d32-9c121097e0f5 -->

Mama Put knows who may do what. The policy is one function Mama could read, permissions are types the compiler holds every handler to, each version has its own kitchen guard, and a customer can't even learn that someone else's order exists.

But everything so far has trusted the network. Any website can make a visitor's browser call our API. Nothing stops someone trying a million passwords. Every response leaves out the headers browsers use to protect people. And soon the kitchen wants to upload a photo of each dish, which means accepting files from strangers. Next lesson: security, with security headers, CORS, rate limiting, knowing the client's real address, and uploads done safely.

## Related
<!-- bite: 42758f59-2e9f-4140-b07f-6339739c97ec -->

- [[backend/frameworks/axum/14-security|Next: Security]]
- [[backend/frameworks/net-http/13-authorization|The same lesson in net/http]] — a policy map, middleware for routes, and checks in the service
- [[backend/05-auth/index|Authentication and Authorization]] — roles, ownership and the 401/403/404 question
- [[backend/frameworks/axum/10-versioning|Versioning]] — the version traits this lesson extends

## About this lesson
<!-- bite: 5622c0e1-6814-4e09-b082-59c6277e6593 -->

**Level:** Advanced. Lesson 13 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96) and Axum 0.8. Covers a policy as one exhaustive `match` with a table test, permissions as marker types with associated constants, a generic `Can<P>` extractor built on `AuthUser` with a private `PhantomData` so it can't be forged, per-version kitchen guards with a generic associated type (`StaffKeyHeader` in v1, `Can<P>` in v2) replacing lesson 3's route layer, object-level ownership in the service answering 404, a per-version `Lister` scoping the order list in SQL, the v1 security fix as a justified breaking change, 401 versus 403 versus 404, and changing roles with the own-role rule and a log line.
