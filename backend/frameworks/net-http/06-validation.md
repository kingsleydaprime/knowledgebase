---
id: 2b795344-e5ab-4de3-8003-d10da39c5995
---

# Input Validation

**Input validation means checking everything a request brings in (the body, the path, the query) at the door, before any of it reaches your rules or your data, and refusing it with a clear message if it's the wrong shape.** Go's standard library gives you a JSON decoder that can be made strict and a way to cap the body's size. For checking the values themselves, almost every Go team adds one package, `go-playground/validator`.

## Before you start
<!-- bite: 9fe4cac2-672a-4123-bd40-0c35d2588655 -->

You should have:

1. Finished [[backend/frameworks/net-http/05-wiring-dependencies|lesson 5]], so Mama Put API has services behind small interfaces and `go test ./...` passes.
2. Read [[backend/06-cross-cutting/01-validation-and-dtos|Validation and DTOs]] if you want the idea before the Go version. It's not required.

After this lesson you will be able to:

1. Decode a JSON body strictly: size-capped, one object, no unknown fields.
2. Turn every decoding failure into a message a client developer can act on.
3. Check values with struct tags, and report every bad field at once.
4. Parse path and query values into real types, and refuse bad ones.
5. Say which checks belong at the door and which belong in the service.

## Where we stopped
<!-- bite: a2ff2072-7f65-4058-8875-494714ebbc2a -->

The handlers decode bodies with a plain `json.NewDecoder(r.Body).Decode(&in)`. Here's what gets through today:

```bash
# a field that doesn't exist: silently ignored
curl -X POST localhost:8080/menu -H "X-Staff-Key: mama-secret" \
  -d '{"name":"Moi moi","priceNaira":800,"isFree":true}'

# a typo: also silently ignored, so the price is 0 and the service says "bad dish"
curl -X POST localhost:8080/menu -H "X-Staff-Key: mama-secret" \
  -d '{"name":"Moi moi","pricenaira":800}'

# a 2 GB body: read until the server runs out of memory
# an ID that can't be an ID: GET /menu/abc is looked up like any other
```

None of these are Mama's rules. They're about the **shape** of what came in. They need checking before the service ever sees them.

## The kid version
<!-- bite: c7b51101-3c4b-4738-9543-3326b463b709 -->

At Mama's stand, her son at the gate checks every order slip before it reaches her. Is it actually an order slip, not a shopping list? Is it readable? Is there a dish name and a number of plates? If not, he hands it straight back: "you forgot to say how many plates".

He doesn't decide if Mama has enough jollof left. That's Mama's job, because only she knows. He only checks that the slip makes sense.

**Where the picture stops working.** The son reads every slip with his eyes. Your server will meet slips written by programs that try to break it: slips the size of a library, slips with a thousand extra lines. The checks at the door have to be strict in ways no human gate-keeper would need.

## Terms used in this lesson
<!-- bite: 1aa25d0b-a9a7-4eef-a69e-e8b79e239c77 -->

1. **Validation**: This means checking that input has the right shape and sensible values: a name that's present and not too long, a price that's a positive number.
2. **Business rule**: This is a rule that needs to know the state of the app to check: "the dish is available", "the shop is open". It lives in the service, not at the door.
3. **Decoding**: This means turning the JSON text of a body into a Go value, like a `menu.NewDish`.
4. **Unknown field**: This is a field in the JSON that the Go struct doesn't have. By default Go ignores it. That's how typos hide.
5. **Struct tag**: This is the little label in backticks after a field, like `` `json:"name" validate:"required"` ``. Packages read the tags meant for them.
6. **Generic function**: This is a function that works with many types, given as a **type parameter** in square brackets, like `Decode[menu.NewDish]`.

## What to install
<!-- bite: c4fab0f1-4f71-462b-b308-a0fc7f1b8097 -->

One package, for checking values:

```bash
go get github.com/go-playground/validator/v10
```

`go get` downloads the package and records it in `go.mod`, with the exact version, under a new `require` line. It also writes `go.sum`, a list of fingerprints for every downloaded file, so anyone who builds the project later gets exactly the same code, or a loud error. Commit both files.

The `/v10` at the end is part of the import path. When a Go package makes a breaking change, its import path gets a new version number, so old code that imports `/v9` keeps working.

Everything else in this lesson is from the standard library.

## Step 1: one strict decoder for every handler
<!-- bite: cb04ffb4-d0ae-4507-bc80-55fafd8c8d4d -->

Every handler that reads a body will use the same function, so the rules are the same everywhere. Replace `ReadJSON` in `internal/httpx/json.go` with this:

```go
package httpx

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime"
	"net/http"
	"strings"
)

const maxBodyBytes = 1 << 20 // 1 MB

// InputError means the request itself was wrong: bad JSON, a bad value, a bad ID.
type InputError struct {
	Message string       `json:"error"`
	Fields  []FieldError `json:"fields,omitempty"`
}

type FieldError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

func (e *InputError) Error() string { return e.Message }

func decodeJSON(w http.ResponseWriter, r *http.Request, dst any) error {
	mediaType, _, _ := mime.ParseMediaType(r.Header.Get("Content-Type"))
	if mediaType != "application/json" {
		return &InputError{Message: "send the body as JSON, with Content-Type: application/json"}
	}

	dec := json.NewDecoder(http.MaxBytesReader(w, r.Body, maxBodyBytes))
	dec.DisallowUnknownFields()

	if err := dec.Decode(dst); err != nil {
		return &InputError{Message: describeJSONError(err)}
	}
	if err := dec.Decode(&struct{}{}); !errors.Is(err, io.EOF) {
		return &InputError{Message: "the body must hold one JSON object, and nothing after it"}
	}
	return nil
}
```

Four protections, in the order they happen:

1. **The content type.** A client must say it's sending JSON. `mime.ParseMediaType` reads `application/json; charset=utf-8` correctly, so we compare only the type itself. This replaces the `onlyJSON` middleware from lesson 3's practice: the check now lives where bodies are read.
2. **`http.MaxBytesReader`** wraps the body so that reading more than 1 MB fails with an error instead of carrying on. Without it, a client can send gigabytes and your server will try to hold it all. A menu item is a few hundred bytes; 1 MB is generous. It also tells the server to close the connection, so the client can't keep pushing.
3. **`DisallowUnknownFields`** makes the decoder fail on any field the struct doesn't have. `"pricenaira"` with a small n is now an error that names it, instead of a silent zero.
4. **One object only.** After decoding, we try to decode again into an empty struct, and expect `io.EOF`, which means "nothing left". A body like `{"name":"Moi moi"}{"name":"Akara"}` would otherwise be half-read without anyone noticing.

The error messages are the other half of the job. Go's JSON errors are written for Go programmers (`json: cannot unmarshal string into Go struct field NewDish.priceNaira of type int`). The person reading yours is building a phone app. Add this:

```go
func describeJSONError(err error) string {
	var syntaxErr *json.SyntaxError
	var typeErr *json.UnmarshalTypeError
	var tooBig *http.MaxBytesError

	switch {
	case errors.Is(err, io.EOF):
		return "the body is empty"
	case errors.Is(err, io.ErrUnexpectedEOF):
		return "the JSON is cut off before the end"
	case errors.As(err, &syntaxErr):
		return fmt.Sprintf("the JSON is broken near character %d", syntaxErr.Offset)
	case errors.As(err, &typeErr):
		return fmt.Sprintf("%q must be a %s", typeErr.Field, typeErr.Type)
	case errors.As(err, &tooBig):
		return fmt.Sprintf("the body is larger than %d bytes", tooBig.Limit)
	case strings.HasPrefix(err.Error(), "json: unknown field "):
		field := strings.TrimPrefix(err.Error(), "json: unknown field ")
		return fmt.Sprintf("%s is not a field we accept", field)
	default:
		return "the body isn't valid JSON"
	}
}
```

`errors.As` is the partner of `errors.Is`. `errors.Is` asks "is it this exact error?"; `errors.As` asks "is it an error of this **type**, and if so, give it to me", so you can read its fields, like `syntaxErr.Offset`. The unknown-field error has no type of its own in the standard library, so we read its message. That's the one ugly line in this lesson, and it's the usual way Go code handles it.

## Step 2: checking values with tags
<!-- bite: 69007366-e864-42f0-b0e0-4122cad267cd -->

The decoder now guarantees the JSON has the right **fields** with the right **types**. It doesn't check the **values**: an empty name, a price of -500, a name of 4,000 characters all decode fine.

That's what `validator` is for. You describe the rules in a `validate` tag on each field. Update the input types in `internal/menu/menu.go`:

```go
type NewDish struct {
	Name       string `json:"name"       validate:"required,max=80"`
	PriceNaira int    `json:"priceNaira" validate:"required,gt=0,lte=1000000"`
	Special    bool   `json:"special"`
}

type DishChanges struct {
	Name       *string `json:"name"       validate:"omitempty,min=1,max=80"`
	PriceNaira *int    `json:"priceNaira" validate:"omitempty,gt=0,lte=1000000"`
	Available  *bool   `json:"available"`
	Special    *bool   `json:"special"`
}
```

Read the tags like a sentence. A new dish's name is **required** and at **most 80** characters. Its price is required, **greater than 0**, and **less than or equal to** a million naira (a typo guard: nobody's jollof costs ₦15,000,000). For `DishChanges`, `omitempty` means "if this field wasn't sent (the pointer is nil), skip the other rules". When a field is sent, the rules apply to the value it points at.

And in `internal/orders/orders.go`:

```go
type NewOrder struct {
	DishID   string `json:"dishId"   validate:"required,numeric"`
	Quantity int    `json:"quantity" validate:"required,min=1,max=20"`
}

type StatusChange struct {
	Status Status `json:"status" validate:"required,oneof=pending ready collected"`
}
```

`oneof` lists the only values allowed. `numeric` means only digits, since our dish IDs are numbers written as text.

Now the code that runs the checks. Add to `internal/httpx/json.go`:

```go
var validate = newValidator()

func newValidator() *validator.Validate {
	v := validator.New(validator.WithRequiredStructEnabled())
	v.RegisterTagNameFunc(func(f reflect.StructField) string {
		name, _, _ := strings.Cut(f.Tag.Get("json"), ",")
		return name
	})
	return v
}

// Decode reads a JSON body into a T and checks its validate tags.
func Decode[T any](w http.ResponseWriter, r *http.Request) (T, error) {
	var v T
	if err := decodeJSON(w, r, &v); err != nil {
		return v, err
	}
	if err := validate.Struct(v); err != nil {
		return v, toInputError(err)
	}
	return v, nil
}

func toInputError(err error) error {
	var invalid validator.ValidationErrors
	if !errors.As(err, &invalid) {
		return err
	}
	fields := make([]FieldError, 0, len(invalid))
	for _, fe := range invalid {
		fields = append(fields, FieldError{Field: fe.Field(), Message: describeRule(fe)})
	}
	return &InputError{Message: "some fields are not valid", Fields: fields}
}

func describeRule(fe validator.FieldError) string {
	switch fe.Tag() {
	case "required":
		return "is required"
	case "max":
		return "must be at most " + fe.Param() + " long"
	case "min":
		return "must be at least " + fe.Param()
	case "gt":
		return "must be more than " + fe.Param()
	case "lte":
		return "must be at most " + fe.Param()
	case "oneof":
		return "must be one of: " + fe.Param()
	case "numeric":
		return "must be a number"
	default:
		return "is not valid (" + fe.Tag() + ")"
	}
}
```

Add `"reflect"` and `"github.com/go-playground/validator/v10"` to the imports.

What each part does:

1. **`validate` is a package-level variable.** Lesson 5 said "no globals for dependencies", and this is the exception that proves the rule: the validator holds no data about your app, it's safe to use from many goroutines at once, and it caches what it learns about each struct, so building one per request would be slow. One shared copy is what its authors recommend.
2. **`RegisterTagNameFunc`** makes error messages use the JSON name (`priceNaira`) instead of the Go name (`PriceNaira`). The client never sees Go names.
3. **`Decode[T any]`** is a **generic** function. `T` is a type the caller picks: `httpx.Decode[menu.NewDish](w, r)` returns a `menu.NewDish`. One function, the same strict rules, for every input type in the app.
4. **`toInputError`** collects **every** failing field, not just the first. A client who sent an empty name and a negative price learns about both in one round trip.

## Step 3: handlers that use it
<!-- bite: d93776e4-5c59-4692-9b89-df66aa484ddb -->

The `add` handler in `internal/menu/handlers.go` becomes:

```go
func (h *Handler) add(w http.ResponseWriter, r *http.Request) {
	in, err := httpx.Decode[NewDish](w, r)
	if err != nil {
		httpx.WriteInputError(w, err)
		return
	}
	dish, err := h.svc.Add(in)
	if err != nil {
		writeError(w, err)
		return
	}
	w.Header().Set("Location", "/menu/"+dish.ID)
	httpx.WriteJSON(w, http.StatusCreated, dish)
}
```

And `WriteInputError`, in `internal/httpx/json.go`:

```go
func WriteInputError(w http.ResponseWriter, err error) {
	var in *InputError
	if errors.As(err, &in) {
		WriteJSON(w, http.StatusBadRequest, in)
		return
	}
	http.Error(w, "something went wrong on our side", http.StatusInternalServerError)
}
```

Do the same for `change` (with `DishChanges`), `place` (with `NewOrder`) and `setStatus` (with `StatusChange`). Now try the bad requests again:

```bash
curl -s -X POST localhost:8080/menu -H "X-Staff-Key: mama-secret" \
  -H "Content-Type: application/json" -d '{"name":"Moi moi","pricenaira":800}'
# {"error":"\"pricenaira\" is not a field we accept"}

curl -s -X POST localhost:8080/menu -H "X-Staff-Key: mama-secret" \
  -H "Content-Type: application/json" -d '{"name":"","priceNaira":-5}'
# {"error":"some fields are not valid","fields":[
#   {"field":"name","message":"is required"},
#   {"field":"priceNaira","message":"must be more than 0"}]}

curl -s -X POST localhost:8080/menu -H "X-Staff-Key: mama-secret" \
  -H "Content-Type: application/json" -d '{"name":"Moi moi","priceNaira":"800"}'
# {"error":"\"priceNaira\" must be a int"}
```

"Must be a int" is Go's type name leaking out. Fixing it is the practice.

## Step 4: path and query values are input too
<!-- bite: 7b7d6316-56be-4a2f-b473-db49b52dcbdf -->

`r.PathValue("id")` and `r.URL.Query().Get(...)` are strings the client typed. They need the same care.

Our IDs are positive whole numbers. Add to `internal/httpx/json.go`:

```go
// PathID reads a path value that must be a positive whole number.
func PathID(r *http.Request, name string) (string, error) {
	raw := r.PathValue(name)
	n, err := strconv.ParseInt(raw, 10, 64)
	if err != nil || n < 1 {
		return "", &InputError{Message: name + " must be a positive whole number"}
	}
	return raw, nil
}

// QueryBool reads an optional true/false query value. Missing means false.
func QueryBool(r *http.Request, name string) (bool, error) {
	raw := r.URL.Query().Get(name)
	if raw == "" {
		return false, nil
	}
	b, err := strconv.ParseBool(raw)
	if err != nil {
		return false, &InputError{Message: name + " must be true or false"}
	}
	return b, nil
}
```

Add `"strconv"` to the imports. `PathID` still returns the ID as a string, because that's what our stores use; lesson 8's database will want the number, and it changes then.

The `get` and `list` handlers use them:

```go
func (h *Handler) get(w http.ResponseWriter, r *http.Request) {
	id, err := httpx.PathID(r, "id")
	if err != nil {
		httpx.WriteInputError(w, err)
		return
	}
	dish, err := h.svc.Get(id)
	if err != nil {
		writeError(w, err)
		return
	}
	httpx.WriteJSON(w, http.StatusOK, dish)
}

func (h *Handler) list(w http.ResponseWriter, r *http.Request) {
	onlyAvailable, err := httpx.QueryBool(r, "available")
	if err != nil {
		httpx.WriteInputError(w, err)
		return
	}
	httpx.WriteJSON(w, http.StatusOK, h.svc.List(onlyAvailable))
}
```

Now `GET /menu/abc` is a 400 that says why, instead of a 404 that pretends we looked. And `?available=yes` is a 400, instead of quietly showing everything. `strconv.ParseBool` accepts `true`, `false`, `1`, `0`, `t`, `f` and a few more, which is friendly enough.

Should a bad ID be 400 or 404? Teams disagree. We use **400**, because `abc` can never be a dish's ID: it's a mistake in the request, not a missing thing. `GET /menu/999` is a 404, because it could exist and doesn't.

## The line between validation and rules
<!-- bite: dedf4a05-fb4e-4997-a819-8f1ae60585af -->

Now there are two layers of checks, and it matters which check goes where.

**At the door (the handler, through `Decode`):** anything you can check by looking at the request alone. Is it JSON? Are the fields known? Is the name present and short enough? Is the quantity between 1 and 20? Is the ID a number? These give **400 Bad Request**.

**In the service:** anything that needs to know the state of the world. Does dish 7 exist? Is it available? Is the shop open? Is this status change going forwards? These give 404, 409 or **422 Unprocessable Content** ("I understood you, and the answer is no").

Should the service still check that a price is positive, when `Decode` already did? **Yes.** The service will be called from other places that don't go through `Decode`: a background job, the GraphQL API in lesson 21, the MCP server in lesson 23, a test. The rule "a dish's price is positive" is Mama's rule, and the service must hold it no matter who calls. The door check is there to give a clear, early, field-by-field answer to HTTP clients. It's a kindness, and an early defence, not the only line.

Two small extras that belong in the service too, because every caller needs them:

1. **Trim the name.** `"   "` passes `required` (it isn't empty), and a name of only spaces is useless. In `menu.Service.Add`, start with `in.Name = strings.TrimSpace(in.Name)`, then check it isn't empty.
2. **Don't trust totals.** We already work out `TotalNaira` in the service from the menu's price. A client can't even send a total now: `"totalNaira"` is an unknown field.

## The Go in this lesson
<!-- bite: dd904c99-99aa-4d77-831d-048135350350 -->

1. **`const maxBodyBytes = 1 << 20`**: `<<` shifts the bits of 1 left by 20 places, which is 2 to the power 20, 1,048,576. It's the usual way to write "one megabyte" in Go.
2. **`type InputError struct { ... }` with `func (e *InputError) Error() string`**: Any type with an `Error() string` method satisfies the built-in `error` interface. So you can make your own error types that carry extra data, like a list of fields.
3. **`` `json:"fields,omitempty"` ``**: `omitempty` in a **json** tag means "leave this field out of the JSON when it's empty". Not the same as `omitempty` in a **validate** tag, which means "skip the rules when it's empty".
4. **`return &InputError{...}`**: We return a pointer to the error, because the `Error` method has a pointer receiver. Then `errors.As(err, &in)` with `var in *InputError` finds it.
5. **`mediaType, _, _ := mime.ParseMediaType(...)`**: The function returns three values; we only want the first. Each `_` throws one away.
6. **`dec.Decode(&struct{}{})`**: `struct{}` is the empty struct type, and `struct{}{}` is a value of it. We decode into it just to see whether anything is left.
7. **`var syntaxErr *json.SyntaxError` then `errors.As(err, &syntaxErr)`**: `errors.As` needs the address of a variable of the error type you're looking for. If the error matches, it fills the variable in and returns true.
8. **`fmt.Sprintf("... %d", syntaxErr.Offset)`**: Like `Errorf`, but returns a string instead of an error.
9. **`strings.HasPrefix`, `strings.TrimPrefix`, `strings.Cut`, `strings.TrimSpace`**: Text helpers from the standard `strings` package. `Cut(s, ",")` splits at the first comma, giving the part before, the part after, and whether a comma was found.
10. **`func Decode[T any](w, r) (T, error)`**: A **generic** function. `[T any]` declares a type parameter called `T` that can be any type. Inside, `var v T` makes a zero value of whatever type the caller chose. The caller writes `httpx.Decode[NewDish](w, r)`.
11. **`func(f reflect.StructField) string`**: `reflect` is the package for looking at types while the program runs. The validator uses it to read your tags; here we only read the `json` tag of a field.
12. **`make([]FieldError, 0, len(invalid))`**: `make` builds a slice with a length (0, empty) and a **capacity** (room for `len(invalid)` items), so `append` won't need to grow it.
13. **`strconv.ParseInt(raw, 10, 64)`** and **`strconv.ParseBool(raw)`**: Turn text into a number (in base 10, fitting in 64 bits) or a boolean, returning an error if the text isn't one.
14. **`"github.com/go-playground/validator/v10"`**: Outside packages are imported by their full path. You use the name the package declares, here `validator`, even though the path ends in `v10`.

## Your project so far
<!-- bite: ef55587e-59fc-48ea-9bd2-4dbe840a63ca -->

```text
mama-put/
├── .gitignore
├── go.mod                       ← now requires github.com/go-playground/validator/v10
├── go.sum                       ← NEW: fingerprints of every downloaded package (commit it)
├── cmd/
│   └── api/
│       └── main.go
└── internal/
    ├── app/
    │   └── app.go
    ├── httpx/
    │   ├── json.go              ← InputError, Decode[T], PathID, QueryBool, WriteInputError
    │   └── middleware.go
    ├── menu/
    │   ├── menu.go              ← validate tags on NewDish and DishChanges
    │   ├── store.go
    │   ├── service.go           ← trims the name; still checks the price
    │   ├── service_test.go
    │   └── handlers.go          ← every body through Decode, every ID through PathID
    └── orders/
        ├── orders.go            ← validate tags on NewOrder; StatusChange
        ├── store.go
        ├── service.go
        ├── service_test.go
        └── handlers.go          ← the same
```

## Common mistakes
<!-- bite: aa4f6275-0109-47d2-8fe8-0d54d0162d33 -->

1. **No size limit on the body.** Every body goes through `MaxBytesReader`. Without it, one request can take your server's memory.
2. **Forgetting `DisallowUnknownFields`.** Typos become silent zeros. A price of 0 that should have been 800 is a bad day.
3. **Only reporting the first bad field.** Collect them all. Clients fix everything in one go.
4. **Sending Go's error text.** `cannot unmarshal string into Go struct field` means nothing to a phone developer. Translate it.
5. **Trusting path and query values.** `r.PathValue` is whatever the client typed. Parse it into the type you need.
6. **Rules only at the door.** The service is called from places that never pass the door. Mama's rules live in the service.
7. **Business rules at the door.** "Is the dish available?" can't be a struct tag. It needs the store, so it's the service's job.
8. **A new validator per request.** It's slow and throws away its cache. One shared `*validator.Validate`.

## Check your understanding
<!-- bite: 1d179a80-d9fa-444d-8d5d-592bf0b7cbaf -->

1. A client sends `{"dishId":"2","quantity":3,"quantity":5}`. Go decodes it without an error. What value does `Quantity` end up with, and is that a problem?
2. Why does `Decode` try to decode a second time after the first one worked?
3. `PATCH /menu/1` with `{}`. Does validation pass? What does the dish look like afterwards?
4. The quantity must be between 1 and 20. That's checked in the `validate` tag. Should `orders.Service.Place` check it too? Why?

<details>
<summary>Answers, after your attempt</summary>

1. 5. Go's decoder takes the last value for a repeated key. It's not dangerous here, because 5 is still checked by the tag, but it's why you should never rely on the decoder to catch odd JSON: always validate the values you end up with.
2. To make sure the body holds exactly one JSON value. If something comes after it, like a second object, the second decode returns something other than `io.EOF`, and we refuse the request instead of silently using half of it.
3. Yes, it passes: every field is a nil pointer, and `omitempty` skips their rules. Nothing changes, and the dish is sent back as it was. (You could decide that an empty PATCH is a 400. Either is defensible; just choose on purpose.)
4. Yes. The service is called from places that don't use `Decode` (jobs, GraphQL, MCP, tests), and the 20-plate limit is Mama's rule. The tag gives HTTP clients a clear, early answer; the service makes sure the rule is never broken.

</details>

## Practice
<!-- bite: 03662fd2-bb9d-4679-b119-598fcd378a2d -->

1. Make `describeJSONError` say "must be a number" for numeric Go types and "must be text" for `string`, instead of "must be a int". Hint: `typeErr.Type.Kind()` tells you the kind, like `reflect.Int` or `reflect.String`.
2. Add a `note` field to `NewOrder`, at most 200 characters, optional ("extra pepper, abeg"). Make sure a note of 201 characters gets a 400 naming the field.
3. Write a test for `httpx.Decode` in `internal/httpx/json_test.go`. Use `httptest.NewRequest` to build a request with a body, and `httptest.NewRecorder()` as the `ResponseWriter`. Test: unknown field, two objects, wrong content type, a 2 MB body, and a good body.

**Done when** `go test ./...` passes, `{"priceNaira":"800"}` answers "must be a number", and a 201-character note gets a 400 that names `note`.

## Before moving on
<!-- bite: dc5c42ce-a9e6-493f-93d7-01de4eed23f3 -->

Everything a request brings in is now checked at the door. Bodies are capped, strict and fully validated, every bad field is reported at once, and IDs and query values are parsed into real types. The service still holds Mama's rules, for every caller.

But look at the answers Mama Put API sends now. A bad body gives `{"error": "...", "fields": [...]}`. A missing dish gives plain text from `http.Error`. A panic gives a different plain text. Success gives a bare object, or a bare array. A phone app has to handle four shapes, and none of them carry anything you could use to find the request in your logs. Every handler also repeats the same `if err != nil { write...; return }` dance. In the next lesson, handlers return errors, one function turns every error into one standard shape, and every response gets an ID.

## Related
<!-- bite: 45b0a2ff-116d-4e7d-b5e8-fc8e2347bf58 -->

- [[backend/frameworks/net-http/07-errors|Next: Errors and Structured Responses]]
- [[backend/06-cross-cutting/01-validation-and-dtos|Validation and DTOs]] — the idea behind this lesson
- [[languages/02-go/09-generics|Generics]] — type parameters in the Go course
- [[backend/frameworks/express/06-validation|The same lesson in Express]] — zod instead of struct tags

## About this lesson
<!-- bite: 65562b51-d19e-459a-8017-fa7563cc624d -->

**Level:** Intermediate. Lesson 6 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later and `go-playground/validator` v10.
