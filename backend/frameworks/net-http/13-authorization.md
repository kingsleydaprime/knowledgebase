---
id: 60a3c1a1-33ac-49fb-81b8-b3fa35cb9a88
---

# Authorization

**Authorization is deciding what a person is *allowed* to do, once you know who they are.** Authentication (lesson 12) answers "who are you?". Authorization answers "may you do *this*, to *that*?". A customer may see her own order but not her neighbour's; a cook may mark orders ready but not make himself the boss. Every "no" your API ever gives a logged-in person is authorization.

## Before you start
<!-- bite: 889e4561-bd22-45a0-aa68-4b9d28ff0943 -->

You should have:

1. Finished [[backend/frameworks/net-http/12-authentication|lesson 12]], so every request's identity (user ID and role) is in its context, and orders record their customer.
2. Made yourself staff with `UPDATE users SET role = 'staff' ...`, from lesson 12's practice 2.

After this lesson you will be able to:

1. Write a permission policy once, as a table in code, with a test that proves no action was forgotten.
2. Check roles at the route with `RequirePermission`, and finally delete the shared staff key.
3. Check ownership in the service, where the object is loaded, so no caller can skip it.
4. Choose between 401, 403 and 404 for each "no", and explain why the wrong one leaks information.
5. Let an admin change roles safely, and show each role only the fields it should see.

## Where we stopped
<!-- bite: f289ddc0-c20b-4782-b683-7f5068593fdc -->

Lesson 12 ended with two holes:

1. **Ada can read Bayo's order.** She's logged in, so `GET /v2/orders/7` works for her, even though order 7 is Bayo's.
2. **Every staff member can do everything.** The cook who started yesterday can delete the whole menu, or (once we add it) make himself an admin.

The first hole has a famous name. When an API checks that you're logged in, but not that the *thing* you asked for is yours, attackers just change the ID in the URL and walk through everyone's data. It's called **broken object level authorization**, and it's number one on OWASP's list of API security risks. Real companies have leaked millions of records this way, by counting `/orders/1`, `/orders/2`, `/orders/3`.

## The kid version
<!-- bite: 7bc2a2dc-a5b7-4e30-a11e-5ea9d1151af4 -->

At Mama Put, everyone who comes in has a wristband now (lesson 12). But wristbands have colours:

1. **Green** for customers. You can order food and ask about **your own** order.
2. **Blue** for kitchen staff. You can see every order, mark them ready, and change the menu.
3. **Gold** for Mama herself. Everything, including giving people blue wristbands.

When Ada (green) asks "where's order 7?", the helper doesn't just check she has *a* wristband. She checks the colour, and then checks that order 7 is Ada's. If it's Bayo's, she says "I don't know any order 7", so Ada doesn't even learn it exists.

**Where the picture stops working.** A helper might forget to check once, on a busy day. In code we make forgetting hard, by building the check into the only way to reach the data.

## Terms used in this lesson
<!-- bite: d35b0c0c-fc86-4cf3-ab3c-5aaf0c8d1975 -->

1. **Role**: This is a named group of permissions, like `customer`, `staff` or `admin`. Each user has one.
2. **Permission**: This is also called an **action**. It's one thing someone may do, written like `order:read` or `menu:write`.
3. **Role-based access control**: This is also called **RBAC**. It means deciding permissions by role: "staff may write the menu".
4. **Ownership check**: This is deciding by the thing itself: "a customer may read an order *if it's theirs*". Rules that look at the thing, not just the role, are sometimes called **attribute-based**.
5. **Policy**: This is the written-down set of rules: who may do what, under which conditions. Ours is one file.
6. **Actor**: This is the person (or program) doing something. Service methods will take the actor as an argument.
7. **Default deny**: This is the rule that anything not explicitly allowed is refused.
8. **Fail closed**: This means that when a check breaks or is missing, the answer is "no". Lesson 12's `Current` fails closed.

## Step 1: write the policy down, in one place
<!-- bite: c4a91cfc-6996-4882-9aaf-be0acad91379 -->

Before code, write the table. This is the conversation to have with Mama, not with the compiler:

| Action | customer | staff | admin |
|---|---|---|---|
| read the menu | yes (even logged out) | yes | yes |
| `menu:write` (add, change, remove dishes) | no | yes | yes |
| `order:read` one order | **only their own** | yes | yes |
| `order:list-all` (everyone's orders) | no | yes | yes |
| `order:update-status` | no | yes | yes |
| `user:change-role` | no | no | admin only |

Reading the menu isn't in the policy, because it isn't protected: anyone may, logged in or not. Placing an order isn't either: any logged-in user may (v2), and lesson 12 decided v1 lets anyone.

Now turn the table into code, exactly. `internal/auth/policy.go`:

```go
package auth

// Action is one thing someone may be allowed to do.
type Action string

const (
	MenuWrite         Action = "menu:write"
	OrderRead         Action = "order:read"
	OrderListAll      Action = "order:list-all"
	OrderUpdateStatus Action = "order:update-status"
	UserChangeRole    Action = "user:change-role"
)

// AllActions lists every action. The policy test checks each has a rule.
var AllActions = []Action{MenuWrite, OrderRead, OrderListAll, OrderUpdateStatus, UserChangeRole}

// Resource is what the action is done to, when that matters.
type Resource struct {
	OwnerID *int64 // who it belongs to; nil when it belongs to nobody
}

type rule func(actor Identity, res Resource) bool

func isStaff(actor Identity) bool { return actor.Role == RoleStaff || actor.Role == RoleAdmin }

func owns(actor Identity, res Resource) bool {
	return actor.UserID > 0 && res.OwnerID != nil && *res.OwnerID == actor.UserID
}

var rules = map[Action]rule{
	MenuWrite:         func(a Identity, _ Resource) bool { return isStaff(a) },
	OrderRead:         func(a Identity, r Resource) bool { return isStaff(a) || owns(a, r) },
	OrderListAll:      func(a Identity, _ Resource) bool { return isStaff(a) },
	OrderUpdateStatus: func(a Identity, _ Resource) bool { return isStaff(a) },
	UserChangeRole:    func(a Identity, _ Resource) bool { return a.Role == RoleAdmin },
}

// Can says whether actor may do action to res. Anything without a rule is refused.
func Can(actor Identity, action Action, res Resource) bool {
	allow, ok := rules[action]
	return ok && allow(actor, res)
}
```

Four things make this good:

1. **It's the table.** Mama could read `rules` next to the table and check every line. When she changes her mind, one line changes.
2. **Default deny.** If someone asks `Can` about an action that has no rule, the map lookup finds nothing, `ok` is `false`, and the answer is no. A missing rule can never mean "yes".
3. **`owns` is careful.** Orders placed before lesson 12, and v1's orders, have no owner. A zero `Identity` (nobody logged in) has `UserID` 0. No real user has ID 0 today, so leaving out `actor.UserID > 0` would *probably* be fine. But a permission rule should never rest on "that can't happen". If either side is missing, `owns` says no.
4. **The actor is a plain value.** `Can` takes an `Identity`, the same one `Authenticate` put in the context. No database lookup, no network: it's fast enough to call anywhere, as often as needed.

**What Go can't check for us.** In a language like TypeScript, you can write the rules as "an object with exactly one entry for every action", and the compiler refuses a missing one. Go's maps can't promise that. Default deny keeps a gap *safe*; a test makes it *visible*. `internal/auth/policy_test.go`:

```go
package auth

import "testing"

func TestEveryActionHasARule(t *testing.T) {
	for _, a := range AllActions {
		if _, ok := rules[a]; !ok {
			t.Errorf("action %q has no rule", a)
		}
	}
}

func TestPolicy(t *testing.T) {
	ada := Identity{UserID: 1, Role: RoleCustomer}
	cook := Identity{UserID: 2, Role: RoleStaff}
	mama := Identity{UserID: 3, Role: RoleAdmin}
	nobody := Identity{}

	adas := Resource{OwnerID: ptr(int64(1))}
	bayos := Resource{OwnerID: ptr(int64(9))}
	unowned := Resource{}

	tests := []struct {
		name   string
		actor  Identity
		action Action
		res    Resource
		want   bool
	}{
		{"customer reads own order", ada, OrderRead, adas, true},
		{"customer reads someone else's order", ada, OrderRead, bayos, false},
		{"customer reads an order with no owner", ada, OrderRead, unowned, false},
		{"nobody reads an order with no owner", nobody, OrderRead, unowned, false},
		{"staff reads any order", cook, OrderRead, bayos, true},
		{"customer writes the menu", ada, MenuWrite, unowned, false},
		{"staff writes the menu", cook, MenuWrite, unowned, true},
		{"staff changes roles", cook, UserChangeRole, unowned, false},
		{"admin changes roles", mama, UserChangeRole, unowned, true},
		{"an action with no rule", mama, Action("menu:eat"), unowned, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := Can(tt.actor, tt.action, tt.res); got != tt.want {
				t.Errorf("Can = %v, want %v", got, tt.want)
			}
		})
	}
}

func ptr[T any](v T) *T { return &v }
```

Look at the test table. It's the policy table from the top of this step, written a second way. If the code and the table ever disagree, this fails. And notice the last row: even Mama, the admin, can't do an action nobody wrote a rule for.

```bash
go test ./internal/auth/
```

## Step 2: route-level checks, as middleware
<!-- bite: 76953f26-6693-48b5-8292-d6f710d16b88 -->

Some checks only need the role: "may this person write the menu **at all**?". The route knows the answer before any dish is loaded, so a middleware fits. Add to `internal/auth/middleware.go`:

```go
var ErrNotAllowed = apperr.New(apperr.Forbidden, "not-allowed", "You don't have permission to do this.")

// RequirePermission lets the request through only if the caller may do action.
// It's for checks that don't depend on which object is asked for.
func RequirePermission(action Action) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			who, ok := IdentityFrom(r.Context())
			if !ok {
				httpx.WriteError(w, r, ErrLoginRequired)
				return
			}
			if !Can(who, action, Resource{}) {
				httpx.WriteError(w, r, ErrNotAllowed)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}
```

Not logged in is 401 ("log in first"); logged in but not allowed is 403. Step 4 is about why those are different.

And now `KitchenOnly`, the shared staff key from lesson 3, is **deleted**: the function in `httpx/middleware.go`, the `StaffKey` field in `app.Deps`, `STAFF_KEY` in `.env` and `.env.example`, and the check in `run`. In `app.New`:

```go
menuWrite := auth.RequirePermission(auth.MenuWrite)
kitchen := auth.RequirePermission(auth.OrderUpdateStatus)

menu.NewHandler(d.Menu, menu.V2, "/v2").Register(mux, menuWrite)
orders.NewHandler(d.Orders, orders.V2, "/v2").Register(mux, kitchen, auth.RequireUser)
```

The menu's `Register` didn't change at all: it always took "the middleware that guards writes" as an argument, since lesson 4. It used to be given the staff-key check; now it's given a permission check. That's why lesson 4 passed the guard in instead of letting the menu package build its own.

**And v1?** v1's kitchen routes used the staff key too. Removing it is a breaking change, and lesson 10 said v1 is frozen. But the only v1 client that ever sent a staff key is Mama's own kitchen tablet, which we control and update the same day. And a shared key that never expires is a security hole. **A security fix is the one good reason to break a frozen version.** So v1 gets the same guards as v2. (Step 3 has one more such fix, and it's harder.)

## Step 3: object-level checks, in the service
<!-- bite: 9347ee6f-46c4-43f3-b001-c8c99fef48d0 -->

Now the harder hole: Ada and order 7. A middleware can't check it, because it runs *before* the order is loaded. It knows the ID in the URL, not whose order that is.

So the check goes where the order is loaded: the service. And here's what makes it hard to forget: **every service method that touches protected data takes the actor as an argument.** In `internal/orders/service.go`:

```go
var ErrNotAllowed = apperr.New(apperr.Forbidden, "not-allowed", "Only kitchen staff can change an order's status.")

func (s *Service) Get(ctx context.Context, actor auth.Identity, id int64) (Order, error) {
	o, err := s.store.Find(ctx, id)
	if err != nil {
		return Order{}, err
	}
	if !auth.Can(actor, auth.OrderRead, auth.Resource{OwnerID: o.CustomerID}) {
		return Order{}, ErrOrderNotFound
	}
	return o, nil
}

func (s *Service) List(ctx context.Context, actor auth.Identity, q ListQuery) ([]Order, error) {
	if !auth.Can(actor, auth.OrderListAll, auth.Resource{}) {
		q.CustomerID = &actor.UserID // a customer's list is only ever their own
	}
	return s.store.List(ctx, q)
}

func (s *Service) SetStatus(ctx context.Context, actor auth.Identity, id int64, to Status) (Order, error) {
	if !auth.Can(actor, auth.OrderUpdateStatus, auth.Resource{}) {
		return Order{}, ErrNotAllowed
	}
	// ... the status rules from lessons 4 and 8, unchanged
}
```

`orders` now imports `auth`. That's fine, and it's one way: `auth` knows nothing about orders. The policy is small and stable, and a feature package asking "may this person do this?" is exactly the dependency you want to be visible.

Look at what this buys:

1. **You can't call `Get(ctx, id)` any more.** The compiler requires `Get(ctx, actor, id)`. Every caller (today's REST handler, the GraphQL API in lesson 21, the MCP tools in lesson 23, a background job) has to say *who* is asking, and the check runs every time. You can forget to wrap a route in `RequirePermission`; you can't forget an argument the compiler demands.
2. **Lists are scoped, not filtered afterwards.** A customer's list sets `CustomerID` on the **query**, and the Postgres `List` from lesson 9 adds one more condition with the same `add` closure:

```go
if q.CustomerID != nil {
	add(fmt.Sprintf("customer_id = $%d", len(args)+1), *q.CustomerID)
}
```

We never load everyone's orders and then throw some away in Go. A list that's filtered after loading is one bug away from leaking, and it breaks pagination too: a page of 20 orders filtered down to Ada's 2 is a strange page.

3. **`SetStatus` checks too, even though the route has `RequirePermission`.** The route is the visible lock; the service is the lock that still holds when the route is wired wrongly, or when the call comes from somewhere with no route at all. Checking twice is cheap. Missing once is a leak.

4. **Ada gets 404 for Bayo's order, not 403.** Step 4.

The handlers read the actor with lesson 12's `auth.Current`, and pass it on:

```go
func (h *Handler) get(w http.ResponseWriter, r *http.Request) error {
	who, err := auth.Current(r.Context())
	if err != nil {
		return err
	}
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	order, err := h.svc.Get(r.Context(), who, id)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, h.version.Present(order))
}
```

And the orders `Register` changes to match:

```go
func (h *Handler) Register(mux *http.ServeMux, kitchen, customer func(http.Handler) http.Handler) {
	p := h.prefix
	mux.Handle("POST "+p+"/orders", customer(httpx.HandlerFunc(h.place)))
	mux.Handle("GET "+p+"/orders/{id}", auth.RequireUser(httpx.HandlerFunc(h.get)))
	mux.Handle("GET "+p+"/orders", auth.RequireUser(httpx.HandlerFunc(h.list)))
	mux.Handle("PATCH "+p+"/orders/{id}/status", kitchen(httpx.HandlerFunc(h.setStatus)))
}
```

`GET /orders` used to be the kitchen's alone. Now it serves two people: the kitchen screen gets every pending order; Ada's phone gets Ada's orders. One route, one policy, scoped in the database.

**The second v1 fix.** `GET /v1/orders/{id}` was the hole itself: anyone, logged in or not, could read any order by counting. So v1 gets the same `RequireUser` and ownership check. That means a v1 customer, who places orders without logging in, can no longer look their order up later; their app shows the order from the `POST` response, and they collect at the counter as before. That's a real loss for v1 clients, and the right trade: a hole that leaks every customer's orders doesn't get to stay open because closing it is inconvenient. Tell v1's users, through the deprecation `Link` from lesson 10, and point them to v2.

## Step 4: 401, 403 or 404?
<!-- bite: c2ee715c-d6b1-45f0-b65d-2a90cab3b028 -->

Three different "no"s, and clients treat them differently:

1. **401 Unauthorized**: "I don't know who you are." No token, or a bad one. The app should send the user to log in. (The name is old and confusing; it really means *unauthenticated*.)
2. **403 Forbidden**: "I know who you are, and you're not allowed." A customer trying to change the menu. The app should say "you can't do that", not ask them to log in again, because logging in again won't help.
3. **404 Not Found**: "There's no such thing, as far as you're concerned."

For Ada and Bayo's order, we use **404**, on purpose. A 403 would say "order 7 exists, but it's not yours", which tells Ada that order 7 is real, and lets anyone count how many orders Mama Put gets a day by trying IDs. A 404 tells her nothing she didn't already know. So `Get` returns the very same `ErrOrderNotFound` for "no such order" and "not yours": same status, same code, same message. If they differed in any way at all, even in the wording, the difference would leak.

The rule of thumb: **if the person shouldn't even know the thing exists, answer 404. If its existence isn't secret, but the action isn't allowed, answer 403.** The menu is public, so a customer trying to delete a dish gets 403. Orders are private, so other people's orders are 404.

(IDs that count up, 1, 2, 3, make guessing easy even with 404s. Many APIs use random IDs, like UUIDs, for private things, so there's nothing to count. That's **defence in depth**: the policy is what keeps Ada out; random IDs just give attackers less to work with. Never the other way round: a random ID with no ownership check is still a hole, only a harder one to find.)

Try all three:

```bash
# Nobody: 401
curl -s localhost:8080/v2/orders/1 | grep -o '"code":"[^"]*"'
# "code":"login-required"

# Ada, Bayo's order: 404
curl -s localhost:8080/v2/orders/7 -H "Authorization: Bearer $ADA" | grep -o '"code":"[^"]*"'
# "code":"order-not-found"

# Ada, deleting a dish: 403
curl -s -X DELETE localhost:8080/v2/menu/3 -H "Authorization: Bearer $ADA" | grep -o '"code":"[^"]*"'
# "code":"not-allowed"
```

`grep -o` prints only the part of each line that matches the pattern, so you see just the code.

## Step 5: changing roles, safely
<!-- bite: 81b4ec99-e1d6-4cb9-8000-6cd1647eea77 -->

Mama needs to make new cooks into staff without opening `psql`. The users store gains `SetRole(ctx, id int64, role Role) (User, error)`, an `UPDATE ... RETURNING` like every other. Then, in `internal/auth/service.go`:

```go
var ErrCannotDemoteSelf = apperr.New(apperr.RuleBroken, "cannot-demote-self",
	"You can't remove your own admin role. Ask another admin.")

func (s *Service) ChangeRole(ctx context.Context, actor Identity, userID int64, role Role) (User, error) {
	if !Can(actor, UserChangeRole, Resource{}) {
		return User{}, ErrNotAllowed
	}
	if userID == actor.UserID && role != RoleAdmin {
		return User{}, ErrCannotDemoteSelf
	}
	u, err := s.users.SetRole(ctx, userID, role)
	if err != nil {
		return User{}, err
	}
	if err := s.refresh.RevokeAllForUser(ctx, userID); err != nil {
		return User{}, err
	}
	return u, nil
}
```

`Users` in the interface gains `SetRole`, and the route goes in `auth`'s `Register`:

```go
mux.Handle("PATCH /v2/admin/users/{id}/role", RequirePermission(UserChangeRole)(httpx.HandlerFunc(h.changeRole)))
```

```go
type roleChange struct {
	Role Role `json:"role" validate:"required,oneof=customer staff admin"`
}

func (h *Handler) changeRole(w http.ResponseWriter, r *http.Request) error {
	who, err := Current(r.Context())
	if err != nil {
		return err
	}
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	in, err := httpx.Decode[roleChange](w, r)
	if err != nil {
		return err
	}
	u, err := h.svc.ChangeRole(r.Context(), who, id, in.Role)
	if err != nil {
		return err
	}
	httpx.LoggerFrom(r.Context()).Info("role changed", "by", who.UserID, "user", u.ID, "role", u.Role)
	return httpx.WriteData(w, http.StatusOK, presentMe(u))
}
```

(`presentMe` is the `meV2` building from lesson 12's `me` handler, moved into a function so two handlers can share it.)

Three details that matter:

1. **The role is inside the access token**, from lesson 12. So after Mama demotes a cook, his *current* token still says `staff` for up to 15 minutes. Revoking his refresh tokens means that when it runs out, he can't quietly get a new one with the old role; he must log in again, and gets a token with his new role. If even 15 minutes is too long for some action, check the role from the database for that action. Short tokens are a trade between speed and how quickly changes take effect.
2. **An admin can't demote themselves**, so Mama Put can never end up with no admins by accident.
3. **Role changes are logged**, with who did it, through the request logger, so the line carries the request ID too. Who changed permissions, and when, is exactly what you need to know after something goes wrong. Lesson 27 turns this into a proper audit log.

How does the first admin get made? Once, by hand:

```bash
docker exec -it mama-put-db psql -U postgres mama_put \
  -c "UPDATE users SET role = 'admin' WHERE email = 'mama@example.com';"
```

Never a route that anyone can call "if there are no admins yet". That route will be found.

## Step 6: what each role sees
<!-- bite: d9948a44-b612-4159-9a5a-4edff545ea91 -->

Authorization can also decide *which fields* someone sees. Customers don't need `portionsLeft` (Mama would rather they didn't know the pot is nearly empty; it makes people rush), but the kitchen does.

First, a check against lesson 10: **removing a field from v2's responses is a breaking change**, and lesson 11's spec lists `portionsLeft` as required. We can only make this change because v2 has one client, the phone team's app, which isn't released yet and never shows the number. Once v2 is public, this would have to wait for v3. So: in `openapi/v2.yaml`, take `portionsLeft` out of `Dish`'s `required` list, and regenerate. `apiv2.Dish.PortionsLeft` becomes a `*int`.

The menu package shouldn't need to know about roles to present a dish. It just needs to know which **view** to show. In `internal/menu/versions.go`:

```go
// View is how much of a dish the viewer may see.
type View struct {
	Kitchen bool // stock levels
}
```

`Version.Present` becomes `func(Dish, View) any`, and v2's presenter sets the field only for the kitchen:

```go
if view.Kitchen {
	out.PortionsLeft = &d.PortionsLeft
}
```

v1's presenter ignores the view and keeps sending `portionsLeft` to everyone, because v1 is frozen and its clients expect it. (It's not a security fix, just a preference, so v1 doesn't break for it.)

The menu handler is the one place that knows both: who's asking, and which view that means:

```go
func viewFor(r *http.Request) View {
	who, _ := auth.IdentityFrom(r.Context()) // the menu is public; nobody logged in is fine
	return View{Kitchen: auth.Can(who, auth.MenuWrite, auth.Resource{})}
}
```

Ignoring `ok` here is safe, and it's the one place in this lesson where it is: a zero `Identity` has no role, so `Can` says no, and an anonymous visitor gets the customer view. That's failing closed again, by design: the *less* privileged view is what you get when we don't know who you are.

## The Go in this lesson
<!-- bite: 5c04b203-736f-4c6f-beb0-d5de64388ad9 -->

1. **`type Action string`** with constants: A named string type, so an `Action` can't be mixed up with any other string by accident, and `Action("menu:eat")` is how a test makes one that isn't in the list.
2. **`type rule func(actor Identity, res Resource) bool`**: A named **function type**. Every rule in the policy has this shape, so they can all live in one map.
3. **`map[Action]rule{ MenuWrite: func(...) bool {...}, ... }`**: A map whose values are functions, written inline. Looking one up and calling it is `rules[action](actor, res)`.
4. **`allow, ok := rules[action]`**: Reading a map with `, ok` tells "no such key" apart from "the zero value". For a map of functions the zero value is `nil`, and calling `nil` would crash, so the `ok` matters twice.
5. **`func(a Identity, _ Resource) bool`**: `_` as a parameter name means "this argument is passed, and I don't use it". The function still has the shape `rule` needs.
6. **`*res.OwnerID == actor.UserID`**: `*` in front of a pointer reads the value it points at. Always check the pointer isn't `nil` first; `owns` does, with `res.OwnerID != nil &&` before it. `&&` stops at the first `false`, so the `*` never runs on a nil pointer.
7. **`q.CustomerID = &actor.UserID`**: `&` takes the address of a value, making a pointer to it. `q` is a copy (a struct passed by value), so setting a field here doesn't change the caller's `q`.
8. **`func ptr[T any](v T) *T { return &v }`**: A small generic helper for tests. Go won't let you write `&int64(1)` directly, because a constant has no address; `ptr(int64(1))` copies it into a variable `v`, which does.
9. **`t.Run(tt.name, ...)`**: Runs each table row as its own named **subtest**. A failure prints the row's name, and `go test -run 'TestPolicy/customer'` runs only the rows whose names match.
10. **`who, _ := auth.IdentityFrom(...)`**: Throwing away the `ok` on purpose. Only do it where the zero value is the safe answer, and say so in a comment.

## Your project so far
<!-- bite: 7d0e7ef8-4759-4629-91cd-15ba594d0569 -->

```text
mama-put/
├── .env                           ← STAFF_KEY is gone
├── .env.example                   ← STAFF_KEY is gone
├── openapi/
│   └── v2.yaml                    ← portionsLeft no longer required; admin route added
├── cmd/
│   └── api/main.go                ← no staff key to read or check
└── internal/
    ├── apiv2/
    │   └── models.gen.go          ← regenerated: Dish.PortionsLeft is *int
    ├── app/
    │   └── app.go                 ← RequirePermission guards instead of KitchenOnly, for v1 and v2
    ├── auth/
    │   ├── policy.go              ← NEW: Action, Resource, the rules table, Can (default deny)
    │   ├── policy_test.go         ← NEW: every action has a rule; the table, tested row by row
    │   ├── middleware.go          ← RequirePermission (401 if nobody, 403 if not allowed)
    │   ├── service.go             ← ChangeRole: admin only, never demote yourself, revoke tokens
    │   ├── postgres.go            ← Users.SetRole
    │   └── handlers.go            ← PATCH /v2/admin/users/{id}/role; presentMe
    ├── httpx/
    │   └── middleware.go          ← KitchenOnly deleted
    ├── menu/
    │   ├── versions.go            ← View; v2 shows portionsLeft to the kitchen only
    │   └── handlers.go            ← viewFor(r)
    └── orders/
        ├── service.go             ← Get, List and SetStatus take the actor; Get answers 404 for not-yours
        ├── postgres.go            ← ListQuery.CustomerID; List filters by customer_id when asked
        └── handlers.go            ← get and list need a login, and pass auth.Current along
```

## Common mistakes
<!-- bite: 992729b4-56df-4a62-b3b8-fa236b361298 -->

1. **Checking login but not ownership.** The number one API risk. Every object a person asks for by ID must be checked against who's asking.
2. **Ownership checks in the handler.** Then the next caller (GraphQL, a job, an MCP tool) skips them. Put them in the service, and make the actor an argument.
3. **Filtering lists after loading them.** Scope the query instead. It's safer, and pagination stays right.
4. **403 for things whose existence is secret.** It confirms they exist. Use 404, with exactly the same body as a real "not found".
5. **Permission checks scattered as `if role == "staff"`.** Then nobody can say what staff may do. One policy; ask it everywhere.
6. **A map of rules with no test that it's complete.** Go won't catch a missing rule. Default deny makes the gap safe; a test makes it visible.
7. **Trusting the role in a token for dangerous actions straight after a role change.** It can be up to 15 minutes old. Revoke refresh tokens, and check the database where minutes matter.
8. **A "make me admin if there's no admin" route.** Make the first admin by hand.
9. **Removing a field from a released version for a preference.** Breaking changes wait for the next version. Only security fixes jump the queue.

## Check your understanding
<!-- bite: 142f1a05-2185-47ef-80a2-b6bd6e1f4a42 -->

1. Why can't `RequirePermission` stop Ada from reading Bayo's order?
2. Ada asks for order 7 (Bayo's) and order 9999 (doesn't exist). What does she get for each, and why must they be identical?
3. A teammate adds a GraphQL resolver for orders in lesson 21. Why can't it accidentally show Ada someone else's order?
4. The policy map is missing its `OrderListAll` rule. What does a customer see on `GET /v2/orders`? What does the kitchen see? Which test fails?
5. Mama demotes a cook at 2:00pm. Until when can he still change the menu, and why?
6. `viewFor` ignores the `ok` from `IdentityFrom`. Why is that safe here, when lesson 12 warned against it?

<details>
<summary>Answers, after your attempt</summary>

1. Because it runs before the order is loaded. It knows Ada's role, and the ID in the URL, but not whose order 7 is. Only code that has the order can check ownership, which is why that check lives in the service.
2. Both get the same 404 `order-not-found`, same status, same code, same message. If "not yours" looked different from "doesn't exist" in any way, Ada could tell which orders exist, and count them.
3. Because `orders.Service.Get` requires the actor, and checks ownership itself. The resolver has to pass an identity to call it at all, and the service refuses anything that isn't theirs, whatever called it.
4. Default deny: `Can` finds no rule and says no for everyone. A customer still sees only their own orders, as intended. The kitchen also sees only its *own* orders (none), so the kitchen screen goes empty: a bug, but a safe one, nothing leaks. `TestEveryActionHasARule` fails and names the action.
5. Until his access token expires, at most 15 minutes after it was made, so no later than about 2:15pm. The token carries `role: staff`, and checking it needs no database lookup. His refresh tokens are revoked, so he can't get a fresh `staff` token after that.
6. Because the zero `Identity` has no role, so `Can` says no, and nobody-logged-in gets the less privileged customer view. Ignoring `ok` is only wrong where a zero value would be treated as *more* access; here it's treated as less.

</details>

## Practice
<!-- bite: caf04a94-7c76-45b0-b5c8-9d50a2e7d57c -->

1. Add `GET /v2/admin/users` for admins: a cursor-paginated list of users (ID, email, name, role, joined), using lesson 9's cursor. Never include `password_hash` in the query's columns, let alone the response.
2. Give anonymous v1 orders a way back: when `POST /v1/orders` has no customer, return a random `trackingCode` (lesson 12's `newRefreshToken` style, stored as a hash). `GET /v1/orders/{id}?code=...` shows the order if the code's hash matches. Is this a breaking change for v1? (It isn't: it adds a field and an optional parameter.)
3. Add a `customer:cancel-own-order` action: a customer may cancel their own order while it's still `pending`. Write the rule, the test rows, the service method, and the route. Which "no" does a customer get for cancelling someone else's order? For cancelling their own order that's already `ready`?
4. Write a test for `orders.Service.Get` with a fake store: Ada gets her order; Ada gets `ErrOrderNotFound` for Bayo's; staff get Bayo's.
5. Update the spec: `security` on the orders and admin routes, `403` responses where `RequirePermission` can refuse, and a description on `GET /v2/orders` saying it's scoped for customers.

**Done when** `TestPolicy` and `TestEveryActionHasARule` pass, the three `curl` checks in step 4 give 401, 404 and 403, the staff key is gone from the whole project (`grep -rn -i "staff.key\|STAFF_KEY" .` finds nothing in the Go code), and a customer's menu has no `portionsLeft` while the kitchen's does.

## Before moving on
<!-- bite: 61d8e3d3-c41d-421c-9e26-d7378bbaf039 -->

Mama Put API now knows who may do what. The policy is one table in code, tested row by row; roles are checked at the route, ownership in the service; customers can't see each other's orders, or even learn they exist; only admins change roles; and each role sees what it should. The shared staff key is gone.

But all of this assumes requests come from honest apps at a sensible rate. What about a script trying ten thousand passwords a minute on `/login`? A web page on another site quietly calling our API with a customer's browser? A "photo" upload that's really a program? That's security, the next lesson.

## Related
<!-- bite: 64c00605-12d0-437b-8a72-d8dea8e9a11b -->

- [[backend/frameworks/net-http/14-security|Next: Security]]
- [[backend/05-auth/02-authorization|Authorization]] — RBAC, ownership and attribute-based rules in any framework
- [[backend/frameworks/express/13-authorization|The same lesson in Express]] — the policy as a `Record` the compiler checks
- [[cybersecurity/index|Cybersecurity]] — broken object level authorization and the OWASP API risks

## About this lesson
<!-- bite: 07cc1e14-1367-4c14-b245-8b5270f102be -->

**Level:** Intermediate → Advanced. Lesson 13 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later. Covers a policy as a map of rule functions with default deny and a completeness test, `RequirePermission` for role checks, ownership checks in services that take the actor, lists scoped in SQL, 401 versus 403 versus 404, breaking a frozen version only for security fixes, safe role changes with token revocation, and role-based views.
