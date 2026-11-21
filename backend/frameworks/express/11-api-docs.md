---
id: 75dd18e8-b769-4092-9da5-ad6103ff870e
---

# API Docs with OpenAPI

**API documentation tells the people who use your API what it can do: every route, what to send, what comes back, and what each error means. OpenAPI is the standard file format for that description, so tools can read it too: they can draw a docs website, let you try requests in the browser, and even write client code for you.** If you've ever used a "Try it out" button on a developer website, or seen a page with every endpoint listed in green and blue boxes, that was almost certainly drawn from an OpenAPI file.

## Before you start
<!-- bite: 9ac25ed8-5aa7-45a1-ba4d-485d2ec6d6ac -->

You should have v1 and v2 running side by side from [[backend/frameworks/express/10-versioning|lesson 10]], including its first practice task, which stores prices in kobo (`priceKobo`). The code below uses it.

After this lesson you will be able to:

1. Describe your API in an OpenAPI document: paths, parameters, bodies, responses and errors.
2. Generate that document from the same zod schemas that validate requests, so the docs can't drift from the code.
3. Serve interactive docs for both versions, and mark v1's routes as deprecated.
4. Save the document as a file that other tools (linters, client generators, tests) can use.

## Where we stopped
<!-- bite: bdcc8c05-e9d3-40c8-ac6f-c6d94b5a0ec0 -->

Lesson 10 ended with the phone app team asking us on WhatsApp what v2 looks like. Count what they'd have to know, just for the menu:

1. Six routes, in two versions.
2. Eight query parameters on `GET /menu`, each with its own type, default and maximum.
3. Two body shapes for creating a dish.
4. The `{ data, meta }` envelope and the problem shape for errors.
5. Which routes need `X-Staff-Key`.
6. Every error `code` they might want to check.

All of that exists already, just scattered across `*.schemas.ts`, `*.versions.ts` and `*.routes.ts`. The danger with docs written by hand isn't writing them. It's that the code changes on Tuesday and the docs still say Monday's thing, and someone builds on Monday's thing.

## The kid version
<!-- bite: 75b81a06-3391-4b59-bbb9-9009a6b44162 -->

Mama Put's new menu card is printed from her notebook. When she adds ofada rice to the notebook, the next card printed has ofada rice on it. She never writes the card by hand, so the card is never wrong.

OpenAPI is the card. Our zod schemas are the notebook. We'll print the card from the notebook.

**Where the picture stops working.** A schema says what the data *looks like*, but not what a route is *for*, or when to use it. So we still write a short sentence per route by hand. Only the shapes are printed automatically.

## Terms used in API docs
<!-- bite: e279d216-37f6-4ff6-906d-048045003754 -->

1. **OpenAPI**: This is a standard way to describe an HTTP API in one JSON or YAML document. It was once called **Swagger**, and you'll still hear that name.
2. **Path**: In OpenAPI, this is one route pattern, like `/menu/{id}`. Under it go its **operations**: `get`, `post`, `patch`, `delete`.
3. **Operation**: This is one method on one path, with its summary, parameters, request body and responses.
4. **JSON Schema**: This is a standard way to describe the shape of JSON data: "an object with a `name` that's a string of at most 80 characters". OpenAPI uses it for every body and parameter. zod can write JSON Schema for us.
5. **Component**: This is a reusable piece of the document, like the `Problem` schema, written once and referred to by `$ref` wherever it's needed.
6. **Security scheme**: This is how the document describes authentication, like "send a key in the `X-Staff-Key` header".
7. **Swagger UI**: This is a web page that reads an OpenAPI document and shows interactive docs, with a "Try it out" button for every operation.

## Step 1: let the schemas describe themselves
<!-- bite: fafa850a-9c08-4e25-b949-14b2bd4f613c -->

zod schemas can carry a description and examples, which go straight into the docs. In `menu.schemas.ts`:

```ts
export const NewDishSchema = z.object({
  name: z.string().trim().min(1).max(80).meta({
    description: "What the customer sees on the menu.",
    examples: ["Jollof rice"],
  }),
  priceNaira: z.number().int().positive().max(100_000).meta({
    description: "Price of one plate, in whole naira.",
    examples: [1500],
  }),
  portionsLeft: z.number().int().min(0).max(500).meta({
    description: "How many plates the kitchen has cooked and not yet sold.",
    examples: [40],
  }),
});
```

`.meta()` changes nothing about validation. It's only extra information for anything that reads the schema.

Our presenters from lesson 10 were plain functions, and plain functions can't describe themselves. So we give each version a **response schema** too, and type the presenter from it, so the two can't disagree. In `menu.versions.ts`:

```ts
export const DishV2Schema = z.object({
  id: z.string().meta({ examples: ["1"] }),
  name: z.string(),
  price: z.object({
    amount: z.number().int().meta({ description: "In kobo. 150000 is ₦1,500." }),
    currency: z.literal("NGN"),
  }),
  available: z.boolean(),
  portionsLeft: z.number().int(),
});

export type MenuVersion = {
  DishSchema: z.ZodType;
  presentDish(dish: Dish): Record<string, unknown>;
  NewDishBody: z.ZodType<NewDish>;
};

export const menuV2 = {
  DishSchema: DishV2Schema,
  presentDish: (dish: Dish): z.infer<typeof DishV2Schema> => ({
    id: dish.id,
    name: dish.name,
    price: { amount: dish.priceKobo, currency: "NGN" },
    available: dish.available,
    portionsLeft: dish.portionsLeft,
  }),
  NewDishBody: /* as in lesson 10 */,
} satisfies MenuVersion;
```

Look at the presenter's return type, `z.infer<typeof DishV2Schema>`. If someone adds a field to the presenter but not the schema, or the other way round, TypeScript refuses to compile. The docs can't silently go stale, because the compiler checks them against the code. (`DishV1Schema` and `menuV1` follow the same pattern.)

## Step 2: zod writes JSON Schema
<!-- bite: 7efb65a5-170b-433b-9319-528dcc2b3636 -->

zod 4 has a built-in converter:

```ts
import { z } from "zod";
import { NewDishSchema } from "./src/menu/menu.schemas.ts";

console.log(JSON.stringify(z.toJSONSchema(NewDishSchema), null, 2));
```

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "name": { "type": "string", "minLength": 1, "maxLength": 80,
              "description": "What the customer sees on the menu.", "examples": ["Jollof rice"] },
    "priceNaira": { "type": "integer", "exclusiveMinimum": 0, "maximum": 100000, "...": "..." },
    "portionsLeft": { "type": "integer", "minimum": 0, "maximum": 500, "...": "..." }
  },
  "required": ["name", "priceNaira", "portionsLeft"],
  "additionalProperties": false
}
```

Every rule you wrote for validation is there: the limits, the required fields, the descriptions. OpenAPI 3.1 uses exactly this flavour of JSON Schema, so it drops straight in.

One thing to know: some schemas look different going in and coming out. `ListMenuQuerySchema`'s `sort` goes in as text (`"priceNaira,-name"`) and comes out as a list. For docs about *requests*, we want the input side, and zod gives it with `{ io: "input" }`.

## Step 3: build the document
<!-- bite: ffbe8342-f457-40de-aaf1-8d9e6400c2a0 -->

`src/docs/openapi.ts`:

```ts
import { z } from "zod";
import type { MenuVersion } from "../menu/menu.versions.ts";
import { ListMenuQuerySchema, DishIdSchema, DishChangesSchema } from "../menu/menu.schemas.ts";

type JsonSchema = Record<string, any>;

const json = (schema: z.ZodType, io: "input" | "output" = "output"): JsonSchema => {
  const { $schema, ...rest } = z.toJSONSchema(schema, { io }) as JsonSchema;
  return rest;
};

function queryParameters(schema: z.ZodType) {
  const s = json(schema, "input");
  return Object.entries(s.properties ?? {}).map(([name, prop]) => ({
    name,
    in: "query",
    required: (s.required ?? []).includes(name),
    description: (prop as JsonSchema).description,
    schema: prop,
  }));
}

const ref = (name: string) => ({ $ref: `#/components/schemas/${name}` });
const problem = (description: string) => ({
  description,
  content: { "application/problem+json": { schema: ref("Problem") } },
});
const wrapped = (description: string, data: JsonSchema, meta?: JsonSchema) => ({
  description,
  content: {
    "application/json": {
      schema: {
        type: "object",
        required: meta ? ["data", "meta"] : ["data"],
        properties: meta ? { data, meta } : { data },
      },
    },
  },
});

export function buildOpenApi(name: "v1" | "v2", menu: MenuVersion, opts: { deprecated: boolean }) {
  const dish = ref("Dish");
  const staffOnly = [{ staffKey: [] }];
  const deprecated = opts.deprecated;

  return {
    openapi: "3.1.0",
    info: {
      title: "Mama Put API",
      version: name,
      description: deprecated
        ? "**v1 is deprecated** and stops working on 1 June 2027. Please move to v2."
        : "Menu and orders for Mama Put. Every success is `{ data }`; every error is a problem.",
    },
    servers: [{ url: `/${name}` }],
    tags: [{ name: "Menu" }, { name: "Orders" }],
    components: {
      securitySchemes: {
        staffKey: { type: "apiKey", in: "header", name: "X-Staff-Key", description: "Kitchen staff only." },
      },
      schemas: {
        Dish: json(menu.DishSchema),
        NewDish: json(menu.NewDishBody, "input"),
        DishChanges: json(DishChangesSchema, "input"),
        PageMeta: {
          type: "object",
          properties: {
            page: { type: "integer" }, limit: { type: "integer" },
            total: { type: "integer" }, totalPages: { type: "integer" },
          },
        },
        Problem: {
          type: "object",
          required: ["type", "title", "status", "code"],
          properties: {
            type: { type: "string", format: "uri" },
            title: { type: "string" },
            status: { type: "integer" },
            detail: { type: "string" },
            code: { type: "string", description: "Check this in code, e.g. `dish-unavailable`." },
            requestId: { type: "string" },
            errors: {
              type: "array",
              description: "Only for `invalid-request`: everything that was wrong.",
              items: {
                type: "object",
                properties: { in: { type: "string" }, path: { type: "string" }, message: { type: "string" } },
              },
            },
          },
        },
      },
    },
    paths: {
      "/menu": {
        get: {
          tags: ["Menu"], operationId: "listDishes", deprecated,
          summary: "List dishes, a page at a time",
          parameters: queryParameters(ListMenuQuerySchema),
          responses: {
            200: wrapped("A page of dishes", { type: "array", items: dish }, ref("PageMeta")),
            400: problem("A query parameter is not valid"),
          },
        },
        post: {
          tags: ["Menu"], operationId: "addDish", deprecated, security: staffOnly,
          summary: "Add a dish to the menu",
          requestBody: { required: true, content: { "application/json": { schema: ref("NewDish") } } },
          responses: {
            201: wrapped("The new dish", dish),
            400: problem("The body is not valid"),
            401: problem("Missing or wrong staff key"),
          },
        },
      },
      "/menu/{id}": {
        parameters: [{ name: "id", in: "path", required: true, schema: json(DishIdSchema).properties.id }],
        get: {
          tags: ["Menu"], operationId: "getDish", deprecated, summary: "Get one dish",
          responses: { 200: wrapped("The dish", dish), 404: problem("No dish with that id") },
        },
        patch: {
          tags: ["Menu"], operationId: "changeDish", deprecated, security: staffOnly,
          summary: "Change some fields of a dish",
          requestBody: { required: true, content: { "application/json": { schema: ref("DishChanges") } } },
          responses: {
            200: wrapped("The changed dish", dish),
            400: problem("The body is not valid"), 401: problem("Missing or wrong staff key"),
            404: problem("No dish with that id"),
          },
        },
        delete: {
          tags: ["Menu"], operationId: "removeDish", deprecated, security: staffOnly,
          summary: "Remove a dish",
          responses: {
            204: { description: "Removed" },
            401: problem("Missing or wrong staff key"), 404: problem("No dish with that id"),
            409: problem("The dish has orders (`dish-has-orders`); mark it unavailable instead"),
          },
        },
      },
      // "/orders" and "/orders/{id}" follow the same pattern: see the practice.
    },
  };
}
```

Yes, it's long. But read what's written by hand and what isn't:

1. **By hand:** each route's summary, which errors it can give and what they mean, and which routes need the staff key. These are *decisions*, and only a person knows them.
2. **Generated:** every shape. The dish, the bodies, all eight query parameters with their limits and defaults, the id pattern. Change a schema and the docs change with it.

The `Problem` schema and `PageMeta` are **components**: written once, used everywhere with `ref(...)`. And `deprecated` comes from the same flag that decides the `Deprecation` header, so the docs and the headers always agree about v1.

## Step 4: serve it
<!-- bite: 2ecbf12d-e110-4654-8635-b9dac392f15e -->

```bash
npm install swagger-ui-express
npm install --save-dev @types/swagger-ui-express
```

In `app.ts`, **before** the API routers and the v1 alias:

```ts
import swaggerUi from "swagger-ui-express";
import { buildOpenApi } from "./docs/openapi.ts";
import { menuV1, menuV2 } from "./menu/menu.versions.ts";

const docs = {
  v1: buildOpenApi("v1", menuV1, { deprecated: true }),
  v2: buildOpenApi("v2", menuV2, { deprecated: false }),
};

app.get("/v1/openapi.json", (req, res) => res.json(docs.v1));
app.get("/v2/openapi.json", (req, res) => res.json(docs.v2));
app.use(
  "/docs",
  swaggerUi.serve,
  swaggerUi.setup(undefined, {
    explorer: true,
    swaggerOptions: {
      urls: [
        { url: "/v2/openapi.json", name: "v2" },
        { url: "/v1/openapi.json", name: "v1 (deprecated)" },
      ],
    },
  }),
);
```

Open `http://localhost:3000/docs` in a browser. You'll see every menu route, grouped under "Menu", with a version picker at the top. Click `GET /menu`, then "Try it out": every query parameter has its own box, its default filled in, and its limits shown. Click "Execute" and the page sends a real request to your app. Switch to v1, and every operation is greyed out and marked deprecated.

The documents are built **once**, when the app starts, not on every request. They only change when the code changes.

(Why not mount the docs only in development? Because the phone team, Paystack's reviewers and future you all need them. For a private API you might put `/docs` behind the staff key. For a public one, open docs are a feature.)

## Step 5: keep the document honest
<!-- bite: 7e51b65a-bc8d-43cc-91e2-0c66f35fae09 -->

Generating from schemas stops most drift. Three more habits stop the rest.

**1. Save it as a file, and commit it.** Add a script that writes the documents to disk:

```ts
// src/docs/write.ts
import { writeFile, mkdir } from "node:fs/promises";
import { buildOpenApi } from "./openapi.ts";
import { menuV1, menuV2 } from "../menu/menu.versions.ts";

await mkdir("openapi", { recursive: true });
await writeFile("openapi/v1.json", JSON.stringify(buildOpenApi("v1", menuV1, { deprecated: true }), null, 2) + "\n");
await writeFile("openapi/v2.json", JSON.stringify(buildOpenApi("v2", menuV2, { deprecated: false }), null, 2) + "\n");
console.log("wrote openapi/v1.json and openapi/v2.json");
```

```json
"openapi": "node src/docs/write.ts"
```

Now every change to the API shows up as a change to `openapi/v2.json` in your git diff. A reviewer can see "this pull request removes `portionsLeft` from v2", which is a breaking change, before it ships. In [[backend/frameworks/express/29-ci-and-deployment|lesson 29]], CI fails if the committed file doesn't match the code.

**2. Lint it.** A linter checks the document follows the OpenAPI rules and common good practice:

```bash
npx @redocly/cli lint openapi/v2.json
```

**3. Test the real responses against it.** In [[backend/frameworks/express/16-testing|lesson 16]], our tests check that what the API actually sends matches the document. That's the final lock: the docs, the schemas and the running code all have to agree.

## What the phone team gets for free
<!-- bite: 865df3b8-ccfb-43eb-a140-4051b9a2ec5c -->

Because the document is a standard, other tools can use it. The phone team can generate TypeScript types for every request and response:

```bash
npx openapi-typescript http://localhost:3000/v2/openapi.json -o mama-put-api.d.ts
```

Now their code knows `price.amount` is a number and `priceNaira` doesn't exist in v2, without anyone sending a WhatsApp message. Tools exist for Kotlin, Swift and Dart too. Your API's shape has become something other people's compilers can check.

## The TypeScript in this lesson
<!-- bite: 28c87d96-fdc0-48c6-b69d-cbc0eb5889ff -->

1. **`.meta({ description, examples })`**: Attaches information to a schema for tools like docs generators. It never changes what passes or fails validation.
2. **`satisfies MenuVersion`**: Checks that the object fits the `MenuVersion` type, **without** losing the more exact types inside it. With `const menuV2: MenuVersion = ...`, TypeScript would forget that `presentDish` returns exactly a v2 dish. With `satisfies`, it checks and remembers.
3. **`(dish: Dish): z.infer<typeof DishV2Schema> => ({ ... })`**: An arrow function with its return type written after the brackets. TypeScript checks the object we build is exactly a v2 dish, no missing or extra fields.
4. **`const { $schema, ...rest } = ...`**: Take the `$schema` field out (OpenAPI doesn't want it inside each schema) and keep everything else in `rest`.
5. **`Record<string, any>`**: An object with any keys and values we won't check. We use it here because the OpenAPI document is a big free-form structure, and typing every corner of it would be more code than the document itself. It's a deliberate, local choice.
6. **`s.properties ?? {}`**: If there are no properties, use an empty object, so `Object.entries` still works.
7. **`(prop as JsonSchema).description`**: `Object.entries` gives each value as `any` here, and the assertion just makes our intention clear.
8. **Object keys like `200:` and `"/menu/{id}":`**: Object keys can be numbers or any text in quotes. OpenAPI uses status codes and paths as keys.
9. **`import swaggerUi from "swagger-ui-express"`**: A default import from a package written in older JavaScript. Node and TypeScript let you import it like a modern one.
10. **`mkdir("openapi", { recursive: true })`**: Create the folder, and don't fail if it already exists.

## Your project so far
<!-- bite: 8a78b2ea-4895-49ab-ba9a-88d057c41164 -->

```text
mama-put-api/
├── .env  ·  .env.example  ·  .gitignore  ·  tsconfig.json
├── package.json                  ← swagger-ui-express added; new "openapi" script
├── migrations/   001 … 005
├── openapi/
│   ├── v1.json                   ← NEW: generated, committed, reviewed in diffs
│   └── v2.json                   ← NEW
└── src/
    ├── server.ts
    ├── app.ts                    ← /v1/openapi.json, /v2/openapi.json and /docs, before the API routers
    ├── api.ts
    ├── docs/
    │   ├── openapi.ts            ← NEW: buildOpenApi(name, menu, { deprecated })
    │   └── write.ts              ← NEW: npm run openapi writes the files
    ├── db/        pool.ts · transaction.ts · migrate.ts · seed.ts
    ├── menu/
    │   ├── menu.schemas.ts       ← fields now carry .meta() descriptions and examples
    │   ├── menu.versions.ts      ← DishV1Schema, DishV2Schema; presenters typed from them
    │   └── menu.routes.ts · menu.types.ts · menu.repository.ts · menu.pg-repository.ts · menu.service.ts
    ├── orders/    (unchanged)
    └── shared/    deprecated.ts · choose-version.ts · cursor.ts · pick.ts · errors.ts · request-id.ts
                   validate.ts · log-requests.ts · kitchen-only.ts · not-found.ts · error-handler.ts
```

## Common mistakes
<!-- bite: 949c04bc-caab-498e-8954-395ab2f304f9 -->

1. **Docs written by hand, separate from the code.** They're right on the day you write them and wrong a month later. Generate the shapes.
2. **Documenting only the happy path.** The errors are what client developers struggle with most. List every error each route can give, with its `code`.
3. **Mounting `/docs` after the v1 alias or the 404 handler.** Something else answers first. Docs go before the routers.
4. **Building the document on every request.** It only changes when the code does. Build it once.
5. **One document for two versions.** Each version has its own shapes; each gets its own document.
6. **Never looking at the diff.** The committed `openapi/*.json` is your early warning for breaking changes. Read it in reviews.

## Check your understanding
<!-- bite: 0c917d9d-63d2-4c4b-b0ad-33a819f9eb1f -->

1. Which parts of the OpenAPI document are written by hand, and which are generated? Why the split?
2. You add `spiceLevel` to `DishV2Schema` but forget the presenter. What happens?
3. Why does `queryParameters` use `{ io: "input" }`?
4. How does committing `openapi/v2.json` help catch a breaking change?

<details>
<summary>Answers, after your attempt</summary>

1. Summaries, which errors each route returns and what they mean, and security requirements are written by hand, because they're decisions only a person knows. Every data shape (bodies, responses, parameters) is generated from the zod schemas, because those already exist and must stay in step with the code.
2. TypeScript refuses to compile: the presenter's return type is `z.infer<typeof DishV2Schema>`, which now requires `spiceLevel`. The mistake is caught before anything runs.
3. Because the client sends the *input* form. `sort` goes in as text like `"priceNaira,-name"`; the output (a list of objects) is what our code sees after parsing, which the client never sends.
4. Any change to the API changes the file, so it shows up in the pull request's diff. A reviewer sees a field removed or renamed and can stop it, or insist on a new version, before it reaches customers.

</details>

## Practice
<!-- bite: 128b5682-7442-41bf-a101-89401e342aee -->

1. Document `/orders` and `/orders/{id}`, including `GET /orders` with its cursor (`meta.nextCursor`), and every error code `POST /orders` can give (`invalid-request`, `dish-not-found`, `dish-unavailable`, `too-many-plates`, `not-enough-portions`).
2. Add the `Deprecation` and `Sunset` response headers to every v1 operation's 200 response in the v1 document.
3. Run `npm run openapi`, then `npx @redocly/cli lint openapi/v2.json`, and fix every error it reports.

**Done when** `/docs` shows menu and orders for both versions, the "Try it out" button works for placing an order, the linter reports no errors, and `git diff openapi/` after adding a field to `DishV2Schema` shows exactly that field.

## Before moving on
<!-- bite: 0b3c9245-8fc3-4dc4-b0e4-cd7907e03e54 -->

Mama Put API now describes itself. The docs come from the same schemas that guard the door, they're served for both versions, and every change shows up in review.

Look at the `security` lines you just wrote, though: `X-Staff-Key`. One shared secret, the same for every cook, that never expires, written into the docs for anyone to see is in the header. And customers have no accounts at all: anyone can see any order by guessing its id. Real backends know *who* is calling. That's authentication, the next lesson.

## Related
<!-- bite: efe75c32-000e-4ed0-ac2b-af4a7000377d -->

- [[backend/frameworks/express/12-authentication|Next: Authentication]]
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — what makes an API easy to document in the first place
- [[backend/frameworks/fastapi/index|FastAPI]] — generates OpenAPI from type hints automatically, for comparison

## About this lesson
<!-- bite: ef89df85-da3b-4323-ae41-e0672851c750 -->

**Level:** Intermediate. Lesson 11 of [[backend/frameworks/express/index|Express]]. Covers OpenAPI 3.1 and JSON Schema, `.meta()` on zod schemas, `z.toJSONSchema` with input and output forms, response schemas that type the presenters, `satisfies`, a hand-written document skeleton with generated shapes, components and `$ref`, security schemes, deprecated operations, Swagger UI for several versions, committed spec files, linting with Redocly, and client type generation with openapi-typescript.
