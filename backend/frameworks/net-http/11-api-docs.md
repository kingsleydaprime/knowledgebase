---
id: ceaacfef-ba1e-486a-b357-9084f2db3c45
---

# API Docs with OpenAPI

**OpenAPI is a standard way to describe an HTTP API in one file: every route, every parameter, every field of every request and response, and every error, written so both people and programs can read it.** From that one file, tools draw interactive docs, generate client code for the phone app, and check that your server really answers the way the file says. In Go, the usual way is to write the file first and **generate** Go types from it, so the code and the docs can't quietly disagree.

## Before you start
<!-- bite: 80f36195-71c9-4af2-b38b-83f2f9b5b872 -->

You should have:

1. Finished [[backend/frameworks/net-http/10-versioning|lesson 10]], so v1 and v2 run side by side and v2 has its own wire types.
2. Seen YAML before, or be ready to: it's JSON written with indentation instead of brackets.

After this lesson you will be able to:

1. Explain the two ways to keep docs and code in step, code-first and spec-first, and why Go teams usually choose spec-first.
2. Write an OpenAPI document for v2 of the menu: routes, parameters, schemas, errors and the staff key.
3. Generate Go types from it with oapi-codegen, run as a Go tool, and use them as v2's wire types.
4. Serve the document and interactive docs for both versions.
5. Keep it honest: a linter, committed generated code, and a test that checks real responses against the document.

## Where we stopped
<!-- bite: b56f8e16-3d94-4836-91f0-82a2cd2015a4 -->

The phone team is building the new app on v2. Today, the only way to learn what `POST /v2/menu` accepts is to read our Go structs, or try things with `curl` and read the errors. They want a document: every route, every field, which fields are required, what every error looks like. Their tools can turn such a document into a ready-made client, with a function for every route, so they never type a URL by hand.

And whatever we give them must stay **true**. A document that says `price` is required, when the code was changed last week to make it optional, is worse than no document: it's a confident lie.

## The kid version
<!-- bite: 00b802e4-783d-41d0-89aa-88a91a988a41 -->

Mama's new menu board lists every dish, its price, and what comes with it. The new helper reads the board and knows exactly what to serve. Customers read it and know exactly what to order.

But if Mama changes the jollof price in the pot and forgets the board, the board lies. Customers are charged one thing and told another. So Mama has a rule: **the board is written first**, and the cooking follows the board. If she wants to change a price, she changes the board, and the kitchen copies from it.

**Where the picture stops working.** Mama's helper can still misread the board. A program can check, every time, that what the kitchen hands out matches what the board says. That's step 6.

## Terms used in this lesson
<!-- bite: 7b3b8fb7-c399-447c-b82e-1780c7f4acff -->

1. **OpenAPI**: This is the standard format for describing HTTP APIs, written in YAML or JSON. It used to be called **Swagger**, which is why you'll see both names.
2. **Spec**: This is short for **specification**: the OpenAPI document for one version of the API.
3. **Schema**: This is the description of one shape of data inside the spec, like "a Dish has an id (text), a name (text, at most 80 characters) and a price (Money)". OpenAPI schemas use JSON Schema.
4. **Operation**: This is one method on one path, like `GET /v2/menu`. Each has an `operationId`, a name tools use for the client function.
5. **Code-first**: This means writing the code and generating the spec from it.
6. **Spec-first**: This is also called **design-first**. It means writing the spec and generating code (types, sometimes more) from it.
7. **Code generation**: This means a program writing Go source files for you, from some input. The files are ordinary Go, committed like any other, but never edited by hand.
8. **Contract test**: This is a test that checks the real API's responses match the spec.

## Code-first or spec-first?
<!-- bite: a0fc362d-6bad-4851-8f12-6c8b3b06c17c -->

There are two ways to keep docs and code in step, and the language you use pushes you towards one.

**Code-first** means the code is the truth and the spec is generated from it. The [[backend/frameworks/express/11-api-docs|Express]] subject does this, because its zod schemas exist while the program runs, and a library can read them and write the spec. Go's equivalents are weaker. The best-known Go tool, `swag`, reads specially formatted **comments** above each handler, and comments are exactly what people forget to update. Other tools read struct types by reflection, but they can't see `validate` tags, so limits like "at most 80 characters" go missing from the docs.

**Spec-first** means the spec is the truth and Go code is generated from it. The tool almost every Go team uses is **oapi-codegen**. You write `openapi/v2.yaml`, oapi-codegen writes Go structs for every schema in it, and your handlers use those structs. Now if the spec says `price` is required, the generated `Price` field is not a pointer; if the spec changes, you regenerate, and the compiler shows you every place in the code that no longer fits.

We'll go spec-first. It also changes how the team works, in a good way: the phone team and the backend agree on the spec **before** anyone writes the code, so both can start at once.

oapi-codegen can generate much more than types: a whole server interface that your handlers must satisfy, or a client. We'll only generate the **types**. Our handlers, middleware and error handling from lessons 3 to 10 stay exactly as they are, and only v2's wire types come from the spec.

## What to install
<!-- bite: 485e6b6b-bc44-41f3-8f19-69bb93949438 -->

Two Go modules. The generator, as a **tool** of this module:

```bash
go get -tool github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@latest
```

`go get -tool` (new in Go 1.24) records the generator in `go.mod` under a `tool` line, at an exact version. Anyone who clones the project runs it with `go tool oapi-codegen`, and gets the same version you did, with nothing to install globally. A generator that's different on each laptop writes different code on each laptop.

And a library for reading specs in tests:

```bash
go get github.com/getkin/kin-openapi
```

Optionally, for linting the spec (step 6), Node's `npx` runs Redocly's linter with no install. If you don't have Node, skip that part.

## Step 1: the spec for v2 of the menu
<!-- bite: f0636126-7c19-4b16-b961-597bf93ed809 -->

Make a folder `openapi/` in the project root. Here's `openapi/v2.yaml`, for the menu. Read it slowly once; it's long because it's complete, not because it's hard.

```yaml
openapi: 3.0.3
info:
  title: Mama Put API
  version: "2"
  description: |
    Order food from Mama Put. Prices are in kobo: 150000 is ₦1,500.
    Every success is `{ "data": ... }`; every error is a problem (RFC 9457).
servers:
  - url: http://localhost:8080

tags:
  - name: Menu

components:
  securitySchemes:
    staffKey:
      type: apiKey
      in: header
      name: X-Staff-Key

  schemas:
    Money:
      type: object
      required: [amount, currency]
      properties:
        amount:
          type: integer
          format: int64
          minimum: 1
          maximum: 100000000
          description: In kobo. 150000 is ₦1,500.
          x-oapi-codegen-extra-tags:
            validate: required,gt=0,lte=100000000
        currency:
          type: string
          enum: [NGN]
          x-oapi-codegen-extra-tags:
            validate: required,eq=NGN

    Dish:
      type: object
      required: [id, name, price, available, special, portionsLeft, createdAt]
      properties:
        id: { type: string, example: "1" }
        name: { type: string, maxLength: 80, example: Jollof rice }
        price: { $ref: "#/components/schemas/Money" }
        available: { type: boolean }
        special: { type: boolean }
        portionsLeft: { type: integer, minimum: 0 }
        description: { type: string, maxLength: 300 }
        createdAt: { type: string, format: date-time }

    NewDish:
      type: object
      required: [name, price]
      additionalProperties: false
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 80
          x-oapi-codegen-extra-tags: { validate: "required,max=80" }
        price:
          $ref: "#/components/schemas/Money"
        special: { type: boolean }
        portionsLeft:
          type: integer
          minimum: 0
          maximum: 1000
          x-oapi-codegen-extra-tags: { validate: "omitempty,gte=0,lte=1000" }
        description:
          type: string
          maxLength: 300
          x-oapi-codegen-extra-tags: { validate: "omitempty,max=300" }

    DishPage:
      type: object
      required: [data, meta]
      properties:
        data:
          type: array
          items: { $ref: "#/components/schemas/Dish" }
        meta:
          type: object
          required: [limit, offset, total]
          properties:
            limit: { type: integer }
            offset: { type: integer }
            total: { type: integer }

    DishResponse:
      type: object
      required: [data]
      properties:
        data: { $ref: "#/components/schemas/Dish" }

    Problem:
      type: object
      required: [type, title, status, detail, code, requestId]
      properties:
        type: { type: string, format: uri }
        title: { type: string }
        status: { type: integer }
        detail: { type: string }
        code: { type: string, example: dish-not-found }
        requestId: { type: string }
        errors:
          type: array
          items:
            type: object
            required: [field, message]
            properties:
              field: { type: string }
              message: { type: string }

  parameters:
    DishID:
      name: id
      in: path
      required: true
      schema: { type: string, pattern: "^[1-9][0-9]*$" }

  responses:
    Problem:
      description: Something went wrong. Check `code`, never `detail`.
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }

paths:
  /v2/menu:
    get:
      operationId: listDishes
      tags: [Menu]
      summary: List the menu
      parameters:
        - { name: available, in: query, schema: { type: boolean } }
        - { name: special, in: query, schema: { type: boolean } }
        - { name: minPrice, in: query, description: In kobo, schema: { type: integer, minimum: 1 } }
        - { name: maxPrice, in: query, description: In kobo, schema: { type: integer, minimum: 1 } }
        - { name: q, in: query, description: Name contains, any case, schema: { type: string, maxLength: 50 } }
        - name: sort
          in: query
          description: Comma-separated. A leading `-` means highest first.
          schema: { type: string, example: "price,-name" }
        - name: fields
          in: query
          description: Only these fields (id is always sent).
          schema: { type: string, example: "name,price" }
        - { name: limit, in: query, schema: { type: integer, minimum: 1, maximum: 100, default: 20 } }
        - { name: offset, in: query, schema: { type: integer, minimum: 0, maximum: 10000, default: 0 } }
      responses:
        "200":
          description: One page of dishes.
          content:
            application/json:
              schema: { $ref: "#/components/schemas/DishPage" }
        "400": { $ref: "#/components/responses/Problem" }
    post:
      operationId: addDish
      tags: [Menu]
      summary: Add a dish (kitchen staff)
      security: [{ staffKey: [] }]
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/NewDish" }
      responses:
        "201":
          description: Added. `Location` says where it lives.
          headers:
            Location: { schema: { type: string } }
          content:
            application/json:
              schema: { $ref: "#/components/schemas/DishResponse" }
        "400": { $ref: "#/components/responses/Problem" }
        "401": { $ref: "#/components/responses/Problem" }

  /v2/menu/{id}:
    parameters:
      - $ref: "#/components/parameters/DishID"
    get:
      operationId: getDish
      tags: [Menu]
      summary: Get one dish
      responses:
        "200":
          description: The dish.
          content:
            application/json:
              schema: { $ref: "#/components/schemas/DishResponse" }
        "400": { $ref: "#/components/responses/Problem" }
        "404": { $ref: "#/components/responses/Problem" }
    delete:
      operationId: removeDish
      tags: [Menu]
      summary: Remove a dish (kitchen staff)
      security: [{ staffKey: [] }]
      responses:
        "204": { description: Removed. }
        "401": { $ref: "#/components/responses/Problem" }
        "404": { $ref: "#/components/responses/Problem" }
```

`PATCH /v2/menu/{id}`, with a `DishChanges` schema where nothing is required, is the practice.

The parts that matter most:

1. **`components`** holds the pieces used in many places: schemas, parameters, responses, and the security scheme. `$ref: "#/components/schemas/Money"` means "the `Money` schema, from the components of this file". Write a shape once, use it everywhere.
2. **`required` lists** say which fields are always there. They are the most important lines in the file for a client developer: a field missing from `required` is one their code must check for.
3. **`securitySchemes`** describes the staff key once, and `security: [{ staffKey: [] }]` on an operation says "this one needs it". Interactive docs show a padlock, and a box to paste the key in.
4. **Every operation lists its error responses**, all pointing at one shared `Problem`. The document says, for every route, which statuses can come back, and that they all have the same shape.
5. **`x-oapi-codegen-extra-tags`** is not part of OpenAPI. It's an **extension** (anything starting `x-` is allowed and ignored by tools that don't know it) that tells oapi-codegen "add this struct tag to the generated field". It's how lesson 6's `validate` tags get onto generated types. Yes, `maxLength: 80` and `max=80` say the same thing twice. The first is for people and tools reading the spec; the second is what our Go code checks. Keeping them next to each other in one file is what keeps them in step.

## Step 2: generate the types
<!-- bite: 34a295c7-3451-40cc-a45c-0696f4ea86fb -->

oapi-codegen reads a small config file. `internal/apiv2/oapi-codegen.yaml`:

```yaml
package: apiv2
output: models.gen.go
generate:
  models: true
output-options:
  skip-prune: true
```

And a Go file in the same folder that holds the instruction to run it, `internal/apiv2/generate.go`:

```go
// Package apiv2 holds the v2 wire types, generated from openapi/v2.yaml.
package apiv2

//go:generate go tool oapi-codegen -config oapi-codegen.yaml ../../openapi/v2.yaml
```

`//go:generate` is another directive, like `//go:embed`. It does nothing when you build. It runs only when you type:

```bash
go generate ./...
```

Then `go generate` finds every `//go:generate` line in the module and runs its command, from that file's folder. Ours runs oapi-codegen on the spec and writes `internal/apiv2/models.gen.go`. Open it. You'll see something like this (trimmed):

```go
// Package apiv2 provides primitives to interact with the openapi HTTP API.
//
// Code generated by github.com/oapi-codegen/oapi-codegen/v2 version v2.x.x DO NOT EDIT.
package apiv2

type MoneyCurrency string

const (
	NGN MoneyCurrency = "NGN"
)

type Money struct {
	// Amount In kobo. 150000 is ₦1,500.
	Amount   int64         `json:"amount" validate:"required,gt=0,lte=100000000"`
	Currency MoneyCurrency `json:"currency" validate:"required,eq=NGN"`
}

type Dish struct {
	Available    bool      `json:"available"`
	CreatedAt    time.Time `json:"createdAt"`
	Description  *string   `json:"description,omitempty"`
	Id           string    `json:"id"`
	Name         string    `json:"name"`
	PortionsLeft int       `json:"portionsLeft"`
	Price        Money     `json:"price"`
	Special      bool      `json:"special"`
}

type NewDish struct {
	Description  *string `json:"description,omitempty" validate:"omitempty,max=300"`
	Name         string  `json:"name" validate:"required,max=80"`
	PortionsLeft *int    `json:"portionsLeft,omitempty" validate:"omitempty,gte=0,lte=1000"`
	Price        Money   `json:"price"`
	Special      *bool   `json:"special,omitempty"`
}
```

Look at how the spec turned into Go:

1. **Required fields are plain values; optional fields are pointers.** `Description` isn't in `Dish`'s `required` list, so it's a `*string` with `omitempty`. The spec's "maybe" became Go's "maybe", the same pointer trick as lesson 2.
2. **The `enum` became a type with constants.** `apiv2.NGN` is the only `MoneyCurrency` the spec allows.
3. **The comment says `DO NOT EDIT`.** If you change this file by hand, the next `go generate` throws your change away. Change the spec instead.
4. **`Id`, not `ID`.** Generated names don't always follow Go's style for short words. It's the price of generated code; live with it.

Commit `models.gen.go`. Generated code goes into git like any other code, so the project builds without running the generator, and so a pull request shows exactly how a spec change changed the Go types.

## Step 3: v2 uses the generated types
<!-- bite: c8c78361-c9a1-4236-962f-8504df5ea702 -->

In lesson 10, `menu/versions.go` had hand-written `dishV2` and `newDishV2`. Delete them, and make v2 use the generated ones:

```go
var V2 = Version{
	Present: func(d Dish) any {
		out := apiv2.Dish{
			Id:           strconv.FormatInt(d.ID, 10),
			Name:         d.Name,
			Price:        apiv2.Money{Amount: int64(d.Price), Currency: apiv2.NGN},
			Available:    d.Available,
			Special:      d.Special,
			PortionsLeft: d.PortionsLeft,
			CreatedAt:    d.CreatedAt,
		}
		if d.Description != "" {
			out.Description = &d.Description
		}
		return out
	},
	ReadNew: func(w http.ResponseWriter, r *http.Request) (NewDish, error) {
		in, err := httpx.Decode[apiv2.NewDish](w, r)
		if err != nil {
			return NewDish{}, err
		}
		return NewDish{
			Name:         in.Name,
			Price:        money.Kobo(in.Price.Amount),
			Special:      deref(in.Special),
			PortionsLeft: deref(in.PortionsLeft),
			Description:  deref(in.Description),
		}, nil
	},
	// ReadChanges, Fields, Sortable, PriceInFilter as before
}

// deref gives the value a pointer points at, or the zero value for nil.
func deref[T any](p *T) T {
	if p == nil {
		var zero T
		return zero
	}
	return *p
}
```

The presenter fills in an `apiv2.Dish`. If you forget a field the spec requires, nothing stops you at compile time (Go fills it with a zero value), but the contract test in step 6 does. If the spec **renames** a field, the generated struct changes, and this code stops compiling until you fix it. That's the point: the spec now drives the code.

`money.Amount` from lesson 10 isn't used by v2 any more. Its job moved to the generated `apiv2.Money`. Delete it if nothing else uses it.

`deref` is a tiny generic helper. Generated code gives you lots of pointers for optional fields, and you'll write some version of this in every project that uses oapi-codegen.

## Step 4: serve the spec and the docs
<!-- bite: 3652923d-509b-499e-b270-778c0d4da547 -->

The spec files must be inside the program, like the migrations, so the served document always matches the build. `openapi/openapi.go`:

```go
// Package openapi holds the API documents, embedded in the program.
package openapi

import "embed"

//go:embed *.yaml
var FS embed.FS
```

In `internal/app/app.go`, before the versions are registered:

```go
mux.Handle("GET /v2/openapi.yaml", serveSpec("v2.yaml"))
mux.Handle("GET /v1/openapi.yaml", serveSpec("v1.yaml"))
mux.HandleFunc("GET /docs", func(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Write(docsPage)
})
```

`/v1/openapi.yaml` is registered on the **main** mux, so it's more specific than `/v1/` and isn't sent through the v1 mux and its deprecation headers. (`v1.yaml` is in the practice.) And the two helpers:

```go
func serveSpec(name string) http.Handler {
	return httpx.HandlerFunc(func(w http.ResponseWriter, r *http.Request) error {
		b, err := fs.ReadFile(openapi.FS, name)
		if err != nil {
			return apperr.New(apperr.NotFound, "spec-not-found", "There's no document for that version yet.")
		}
		w.Header().Set("Content-Type", "application/yaml")
		w.Write(b)
		return nil
	})
}

var docsPage = []byte(`<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Mama Put API docs</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css">
</head>
<body>
  <div id="docs"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      dom_id: "#docs",
      urls: [
        { url: "/v2/openapi.yaml", name: "v2" },
        { url: "/v1/openapi.yaml", name: "v1 (deprecated)" },
      ],
    });
  </script>
</body>
</html>`)
```

The docs page is a small HTML file that loads **Swagger UI**, a widely used docs viewer, from a CDN, and points it at both specs. The version in the URL is pinned exactly (`@5.17.14`), so the page doesn't change under you when a new Swagger UI is released.

Open `http://localhost:8080/docs` in a browser. You'll see every menu route, grouped under "Menu", with a version picker at the top. Click `GET /v2/menu`, then "Try it out": every query parameter has its own box, its default filled in, and its limits shown. Click "Execute" and the page sends a real request to your app. Click the padlock, paste the staff key, and you can add a dish from the browser.

(Should the docs be public? The phone team, Paystack's reviewers and future you all need them. For a private API, put `/docs` behind the staff key. For a public one, open docs are a feature. Lesson 14 adds a security policy that will need to allow the CDN for this one page.)

## Step 5: what the phone team gets for free
<!-- bite: e870d23e-cf7d-4416-9a26-02bb1dcf1e61 -->

With a spec, the phone team doesn't need to hand-write a client. Generators exist for every language their app might use. For a TypeScript app, for example, `openapi-typescript` turns `http://localhost:8080/v2/openapi.yaml` into TypeScript types for every route, and their code editor then checks every request they write against our API. For a Kotlin or Swift app, `openapi-generator` writes a whole client library.

That's the bigger reason for writing a spec. It isn't just docs for people to read. It's a contract that both sides' **compilers** check.

## Step 6: keep the spec honest
<!-- bite: 07c036f2-d42d-44e6-93dd-d31e5fdec573 -->

Generating the types stops most drift: a renamed field won't compile. Three more habits stop the rest.

**1. Lint it.** A linter checks the spec follows the OpenAPI rules and good practice (every operation has an `operationId`, every response a description, no unused schemas):

```bash
npx @redocly/cli lint openapi/v2.yaml
```

**2. Never let generated code fall behind the spec.** Add a target to the `Makefile`:

```makefile
generate:
	go generate ./...
```

In lesson 29, CI runs `make generate` and fails the build if that changes any file, meaning someone edited the spec and forgot to regenerate (or edited the generated code by hand).

**3. Test the real responses against the spec.** This is the final lock. A test sends real requests to the app, and checks every response (status, headers, body) against what the spec says that operation may return. If a presenter forgets a required field, or a route returns a status the spec doesn't list, the test fails.

`internal/app/contract_test.go`:

```go
package app

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/getkin/kin-openapi/openapi3"
	"github.com/getkin/kin-openapi/openapi3filter"
	"github.com/getkin/kin-openapi/routers/gorillamux"
)

func TestV2MatchesItsSpec(t *testing.T) {
	doc, err := openapi3.NewLoader().LoadFromFile("../../openapi/v2.yaml")
	if err != nil {
		t.Fatal(err)
	}
	if err := doc.Validate(context.Background()); err != nil {
		t.Fatalf("the spec itself is invalid: %v", err)
	}
	router, err := gorillamux.NewRouter(doc)
	if err != nil {
		t.Fatal(err)
	}

	handler := newTestApp(t) // the app with in-memory stores and a known menu

	requests := []*http.Request{
		httptest.NewRequest("GET", "http://localhost:8080/v2/menu", nil),
		httptest.NewRequest("GET", "http://localhost:8080/v2/menu?maxPrice=200000&sort=-price&limit=2", nil),
		httptest.NewRequest("GET", "http://localhost:8080/v2/menu/1", nil),
		httptest.NewRequest("GET", "http://localhost:8080/v2/menu/999", nil),
		httptest.NewRequest("GET", "http://localhost:8080/v2/menu?limit=500", nil),
	}

	for _, req := range requests {
		t.Run(req.Method+" "+req.URL.RequestURI(), func(t *testing.T) {
			rec := httptest.NewRecorder()
			handler.ServeHTTP(rec, req)

			route, params, err := router.FindRoute(req)
			if err != nil {
				t.Fatalf("the spec has no operation for this request: %v", err)
			}
			err = openapi3filter.ValidateResponse(context.Background(), &openapi3filter.ResponseValidationInput{
				RequestValidationInput: &openapi3filter.RequestValidationInput{
					Request: req, PathParams: params, Route: route,
				},
				Status: rec.Code,
				Header: rec.Header(),
				Body:   io.NopCloser(rec.Body),
			})
			if err != nil {
				t.Errorf("status %d does not match the spec: %v", rec.Code, err)
			}
		})
	}
}
```

`kin-openapi` loads the spec, checks the spec itself is valid, then for each request finds the operation it belongs to, and checks the response the app gave against that operation's schemas. The 404 and the bad `limit` are in the list on purpose: errors are part of the contract too.

`newTestApp` builds the app with in-memory stores, the same way `run` builds it with Postgres. Write it in the test file, using `menu.NewMemoryStore` from lesson 8's practice with two or three dishes in it. Lesson 16 makes a proper helper of it, and adds this test to the rest.

Run it:

```bash
make test
```

Now break something on purpose: in v2's `Present`, leave out `Price`. The code still compiles. The test fails, saying `price` is missing its required `amount`. Put it back.

## The Go in this lesson
<!-- bite: c88c6dc6-35fa-4b38-845b-1efa544c9047 -->

1. **`go get -tool ...`** and **`go tool oapi-codegen`**: Since Go 1.24, a module can list the tools it needs in `go.mod`, at exact versions, and run them with `go tool`. No global installs.
2. **`//go:generate go tool oapi-codegen ...`**: A directive that `go generate ./...` runs, from the file's own folder. `go build` ignores it.
3. **Generated files and `DO NOT EDIT`**: Go tools recognise a comment of the form `// Code generated ... DO NOT EDIT.` and treat the file as generated (linters skip it, editors warn you). Never edit one; change the input and regenerate.
4. **`type MoneyCurrency string`** with **`const NGN MoneyCurrency = "NGN"`**: An enum, the Go way: a named string type and its allowed values as constants.
5. **Optional fields as pointers**: `Description *string` in generated code. `out.Description = &d.Description` points it at the domain value's description.
6. **`func deref[T any](p *T) T`**: A generic helper. `var zero T` makes the zero value of whatever type `T` is, which is the only way to write "zero" for a type you don't know.
7. **Package-level `[]byte` with a raw string**: `var docsPage = []byte(`...`)` holds the HTML. The backticks mean the quotes inside don't need escaping.
8. **`fs.ReadFile(openapi.FS, name)`**: Reads one embedded file, exactly like reading from disk.
9. **`httptest.NewRequest`** and **`httptest.NewRecorder()`**: Build a request without a network, and a `ResponseWriter` that records what the handler wrote, so a test can call `handler.ServeHTTP(rec, req)` and inspect `rec.Code`, `rec.Header()` and `rec.Body`.
10. **`io.NopCloser(rec.Body)`**: Wraps a reader so it also has a `Close` method that does nothing, because the validator wants an `io.ReadCloser`.
11. **`req.URL.RequestURI()`**: The path and query of a URL, like `/v2/menu?limit=2`, used here as a readable test name.

## Your project so far
<!-- bite: b40d5875-eee2-47fa-a60d-33631da5250f -->

```text
mama-put/
├── Makefile                      ← generate target added
├── go.mod                        ← tool line for oapi-codegen; kin-openapi required
├── openapi/
│   ├── openapi.go                ← NEW: //go:embed *.yaml into FS
│   ├── v2.yaml                   ← NEW: the v2 spec: the source of truth for v2's shapes
│   └── v1.yaml                   ← NEW (practice): v1, every operation marked deprecated
├── migrations/
├── cmd/
└── internal/
    ├── apiv2/
    │   ├── generate.go           ← NEW: the //go:generate line
    │   ├── oapi-codegen.yaml     ← NEW: generate models only
    │   └── models.gen.go         ← NEW, generated: Dish, NewDish, Money, Problem, ... (never edit)
    ├── app/
    │   ├── app.go                ← serves /v1/openapi.yaml, /v2/openapi.yaml and /docs
    │   └── contract_test.go      ← NEW: real responses checked against the spec
    ├── menu/
    │   ├── versions.go           ← V2 uses apiv2.Dish and apiv2.NewDish; deref
    │   └── ...
    ├── money/
    │   └── money.go              ← Kobo stays; Amount is gone (apiv2.Money replaced it)
    └── ...
```

## Common mistakes
<!-- bite: 25e8be4f-c084-4df7-bf90-4a198ed6b2bf -->

1. **Editing generated code.** The next `go generate` erases it. Change the spec.
2. **Not committing generated code.** Then the project doesn't build without the generator, and reviews can't see how a spec change affected the code.
3. **A spec that only lists the happy path.** Clients need the errors too. Every operation lists its problem responses.
4. **Forgetting `required`.** Every field left out of `required` is a field the client must treat as optional. If it's always there, say so.
5. **A different generator version on each laptop.** Use `go get -tool`, so everyone runs the version in `go.mod`.
6. **Hand-written docs comments.** They drift the first week. Generate from the spec, or the spec from something the compiler checks, never from comments.
7. **Trusting the compiler alone.** A missing required field still compiles; it's the zero value. The contract test is what catches it.
8. **An unpinned CDN script on the docs page.** A new release can change or break the page. Pin the exact version.

## Check your understanding
<!-- bite: 477322d2-de48-4d41-80e8-874e532b5c63 -->

1. Why does Go lean towards spec-first, when the Express subject generates its spec from code?
2. In `apiv2.Dish`, why is `Description` a `*string` but `Name` a `string`?
3. Someone renames `portionsLeft` to `portions` in `v2.yaml`, runs `go generate`, and commits. What happens next, and is it good news or bad news?
4. A presenter forgets to set `CreatedAt`. Does the code compile? What sends the client, and what catches it?

<details>
<summary>Answers, after your attempt</summary>

1. Because Go has no rich schemas that exist while the program runs, the way zod schemas do. Go's code-first tools read comments (which drift) or reflect on structs (which can't see `validate` limits). Generating types from a spec gives the compiler something to check instead.
2. `name` is in the schema's `required` list, so oapi-codegen makes it a plain value. `description` isn't, so it's optional, and optional fields become pointers, so "not there" (`nil`) can be told from "empty" (`""`).
3. The generated field is renamed to `Portions`, so the code that sets `PortionsLeft` stops compiling. That's good news about the code (it can't silently disagree with the spec), and it's a signal about the API: renaming a field in v2 is a **breaking change**. The compile error is the moment to ask whether that should be v3.
4. It compiles: the field is a `time.Time`, filled with its zero value. The client gets `"createdAt": "0001-01-01T00:00:00Z"`, a wrong but valid-looking date. The contract test won't catch that one either, since it's a valid date-time. A test that checks values, not just shapes, does (lesson 16). Shapes are what contract tests guarantee; correct values need ordinary tests.

</details>

## Practice
<!-- bite: 27bfe0a3-d2cb-4648-b070-2a61eb0f8715 -->

1. Add `PATCH /v2/menu/{id}` to the spec, with a `DishChanges` schema where no field is required. Regenerate, and make `readChangesV2` use the generated type. Add a PATCH request to the contract test.
2. Write `openapi/v1.yaml` for v1's menu, with `priceNaira`, and mark every operation `deprecated: true`. Swagger UI greys them out. v1 is frozen, so you don't need to generate types from it: v1's hand-written wire types already exist, and they'll never change. Add a contract test for v1 too.
3. Add the orders routes to `v2.yaml`: `POST /v2/orders`, `GET /v2/orders/{id}`, and the kitchen's `GET /v2/orders` with its cursor in `meta`.
4. Run the linter (`npx @redocly/cli lint openapi/v2.yaml`) and fix every warning it gives.

**Done when** `make generate` changes nothing, `make test` passes including both contract tests, and `/docs` shows both versions with v1 greyed out.

## Before moving on
<!-- bite: a0df8466-1742-44a2-9fdc-b4f6c2760636 -->

Mama Put API now has a spec for each version: v2's wire types are generated from it, both are served with interactive docs, and a test checks the real responses against them. The phone team can generate a client, and the docs can't quietly drift from the code.

Look at the docs page, though, and something stands out. The only lock on anything is one shared staff key, pasted into a box. Every cook uses the same one. When one leaves, the key must change for everyone. And customers have no identity at all: anyone can see any order by guessing its number. Mama Put needs real accounts: customers and staff who sign up, log in, and are recognised on every request. That's authentication, and it's the next lesson.

## Related
<!-- bite: 987260f0-49e4-41e0-a017-36bb9b5c2bc3 -->

- [[backend/frameworks/net-http/12-authentication|Next: Authentication]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — what the spec describes
- [[backend/frameworks/express/11-api-docs|The same lesson in Express]] — code-first, from zod schemas

## About this lesson
<!-- bite: 9bb945b8-0737-4ebc-8a59-c89cb41f5db9 -->

**Level:** Intermediate. Lesson 11 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (`go get -tool` needs 1.24), oapi-codegen v2, kin-openapi and OpenAPI 3.0.
