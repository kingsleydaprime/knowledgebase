---
id: f16430dc-8803-4126-8b8a-a3b7ba1689ab
---

# What Express Is, and Your First App

**Express is a small library for Node.js that makes it easy to answer web requests: you say "when someone asks for this address, run this function", and Express does the rest.** If you have ever opened a website or an app that loaded a list of things from a server, a backend somewhere took that request and sent the list back. Express is one of the most common ways to write that backend in JavaScript.

## Before you start
<!-- bite: 903a8fbf-2d8d-42a9-b9b1-d8cb6507b221 -->

You should be able to:

1. Write and run a small JavaScript or TypeScript file with Node.js (`node hello.ts`).
2. Explain what a request and a response are, in a sentence. If you can't yet, read [[backend/01-foundations/01-what-a-backend-is|What a Backend Is]] first.

After this lesson you will be able to:

1. Create an Express project from an empty folder and start it.
2. Say what happens, step by step, when a request reaches your app.
3. Send back text, JSON and a status code.

## The app we will build in this subject
<!-- bite: 528c8900-03d7-4fec-8c99-37f1309444cc -->

Every lesson in this subject adds to one app, so you never start from zero again.

Imagine a **Mama Put**: the woman by the roadside with the big pots, selling jollof, beans, plantain and stew. Her customers are now ordering on their phones, so she needs a backend. That backend is what we will build, and we will call it **Mama Put API**.

By the last lesson it will:

1. Show the menu, and let the kitchen add, change and remove dishes.
2. Let customers sign up, log in, place orders and pay for them with Paystack.
3. Let only kitchen staff mark an order as "ready", and show new orders live on a kitchen screen.
4. Store everything in PostgreSQL, and keep the busy parts fast with Redis.
5. Send receipts and "your food is ready" messages from a **second, separate service**, so you learn how microservices talk to each other.
6. Check every request, handle every error, have tests, logs and metrics, and run on a real server, deployed automatically when you push.

That's a real production backend, the kind a small company would actually run. We get there one lesson at a time.

Today we just get the pot on the fire: an app that starts and answers its first request.

## The kid version
<!-- bite: fe262719-ba70-4bc7-a923-aad78b46efa3 -->

Think of Mama Put's stand. A customer walks up and says "one plate of jollof". Mama listens, picks the right pot, dishes the food and hands it over.

An Express app is Mama for the internet. A request comes in ("give me the menu"). Express looks at what was asked for, picks the function you wrote for that request, and that function hands back a response (the menu).

**Where the picture stops working.** Mama serves one customer at a time with her own hands. A server can have hundreds of requests waiting at once. Node handles them by never standing still while it waits for something slow, like a database. We'll come back to that in [[backend/frameworks/node/index|Node.js]].

## Why Express exists
<!-- bite: 4b986279-e0b2-4ae8-b7e3-58361ff0a9b7 -->

Node.js can already answer web requests on its own. It has a built-in module called `http`. Here is a server with nothing but Node:

```ts
import http from "node:http";

const server = http.createServer((req, res) => {
  if (req.method === "GET" && req.url === "/menu") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify([{ name: "Jollof rice", priceNaira: 1500 }]));
    return;
  }
  res.writeHead(404);
  res.end("Not found");
});

server.listen(3000);
```

It works. But look at what you had to do by hand: check the method, check the address, set the header, turn the object into text, and remember the "not found" case. Now imagine 40 addresses, some with an ID inside them (`/menu/7`), some needing a login, some receiving JSON that must be read in pieces. That one function turns into a big mess of `if` statements.

Express takes all that repeated work away. The same server in Express:

```ts
import express from "express";

const app = express();

app.get("/menu", (req, res) => {
  res.json([{ name: "Jollof rice", priceNaira: 1500 }]);
});

app.listen(3000);
```

"When someone sends a GET request to `/menu`, run this function." That's it. Express matched the address, set the header, turned the array into JSON, and will answer "404 not found" for anything you didn't define.

So Express is not doing magic. It is the same Node `http` server underneath, with the boring parts done for you. That matters, because everything true about Node (one thread, never block it) is still true in Express.

## Terms used in this lesson
<!-- bite: 2625361a-1b52-408f-81dc-8b4ea27deeee -->

1. **Request**: This is the message a client (a phone app, a browser, another server) sends to your backend. It says what it wants (the **method**, like GET or POST), where (the **path**, like `/menu`), and sometimes carries extra data (the **body**).
2. **Response**: This is the message your backend sends back. It has a **status code** (a number saying how it went, like 200 for "fine" or 404 for "not found"), some **headers** (labels about the response, like "this is JSON"), and usually a body.
3. **Route**: This is one rule in your app that says "for this method and this path, run this function". `app.get("/menu", ...)` is a route.
4. **Handler**: This is also called a **route handler**. It is the function a route runs. It receives the request and the response, and it must send something back.
5. **Port**: This is a number that tells the computer which program a network message is for. Your app "listens" on a port, like 3000, so messages sent to that port reach it.

## Setting up the project
<!-- bite: 70f6ad1e-3a96-4189-b880-5b813922a4e6 -->

We'll write TypeScript, which is JavaScript with types. Node.js 23.6 or later can run `.ts` files directly, so there's no build step to set up. Check your version first:

```bash
node --version   # needs v23.6.0 or later
```

Now make the project:

```bash
mkdir mama-put-api
cd mama-put-api
npm init -y
npm install express
npm install --save-dev @types/express @types/node typescript
```

`express` is the library. The `@types/...` packages only teach your editor what Express and Node look like, so it can catch mistakes. `typescript` gives us the `tsc` command for checking types.

Open `package.json` and add two things: `"type": "module"`, so we can use `import`, and two scripts:

```json
{
  "name": "mama-put-api",
  "type": "module",
  "scripts": {
    "dev": "node --watch src/server.ts",
    "check": "tsc --noEmit"
  }
}
```

(Keep the `dependencies` that `npm install` added; only add these lines.)

`node --watch` restarts the app every time you save a file. `npm run check` asks TypeScript to look for type mistakes without producing any files.

Last, a small `tsconfig.json` so TypeScript understands how Node is running our code:

```json
{
  "compilerOptions": {
    "target": "es2023",
    "module": "nodenext",
    "strict": true,
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "erasableSyntaxOnly": true
  },
  "include": ["src"]
}
```

You don't need to understand every line yet. The last three are there because Node runs TypeScript by simply **removing** the types. So we must write imports with the `.ts` ending, mark type-only imports with `import type`, and avoid the few TypeScript features (like `enum`) that can't be removed that simply.

## Your first app
<!-- bite: 7a9d847c-897b-4f14-9dee-550dd00afdb0 -->

Create `src/server.ts`:

```ts
import express from "express";

const app = express();

app.get("/", (req, res) => {
  res.send("Mama Put is open!");
});

app.get("/menu", (req, res) => {
  res.json([
    { id: "1", name: "Jollof rice", priceNaira: 1500 },
    { id: "2", name: "Beans and plantain", priceNaira: 1200 },
  ]);
});

const port = 3000;
app.listen(port, () => {
  console.log(`Mama Put API listening on http://localhost:${port}`);
});
```

Run it:

```bash
npm run dev
```

You should see `Mama Put API listening on http://localhost:3000`. Now, in a second terminal:

```bash
curl http://localhost:3000/
# Mama Put is open!

curl http://localhost:3000/menu
# [{"id":"1","name":"Jollof rice","priceNaira":1500},{"id":"2","name":"Beans and plantain","priceNaira":1200}]

curl -i http://localhost:3000/suya
# HTTP/1.1 404 Not Found
# ...
# Cannot GET /suya
```

Before you run that last one, predict: what will Express send back for a path you never wrote? Then run it. The `-i` flag shows the status line and headers too.

Okay!!!!! The pot is on the fire.

## What just happened, step by step
<!-- bite: 290f47ee-d6f9-4ed3-b710-69978ecc3ceb -->

Let's follow one request, `GET /menu`, from your terminal to the answer. This picture is the one to keep in your head for the whole subject.

1. **`curl` sends a request** to port 3000: method GET, path `/menu`.
2. **Node's `http` server receives it.** Express created that server for you inside `app.listen`.
3. **Express builds two objects**: `req`, which describes the request, and `res`, which you use to answer.
4. **Express walks down your routes in the order you wrote them.** `GET /` doesn't match. `GET /menu` does.
5. **It runs your handler** with `req` and `res`.
6. **Your handler calls `res.json(...)`.** That sets the status to 200, sets the header `Content-Type: application/json`, turns the array into text and sends it.
7. **The response goes back to `curl`**, and the request is finished.

If no route matches, Express reaches the end of the list and sends its own 404. Remember step 4, "in the order you wrote them". In the next lesson it explains a bug you'll meet, and in the middleware lesson it becomes the whole idea.

## Sending things back
<!-- bite: fcd94776-458f-44d7-9c15-614bcac75f2d -->

`res` has a few methods you'll use all the time:

```ts
res.send("plain text");                 // text (or HTML)
res.json({ ok: true });                 // JSON, with the right header
res.status(201).json({ id: "3" });      // choose the status, then send
res.sendStatus(204);                    // just a status, no body
```

`res.status()` only *sets* the status. It sends nothing. You chain it with `.json()` or `.send()` to actually reply.

And this is the one rule you must never break: **every request gets exactly one response.** If your handler forgets to send anything, the client waits until it gives up. If it tries to send twice, Express throws the error "Cannot set headers after they are sent to the client". You'll see that error one day, and now you'll know what it means.

## The TypeScript in this lesson
<!-- bite: 6030e65c-26d4-4f44-ad38-3b5264fa9acc -->

If you haven't written much TypeScript, here is everything this lesson used, in the order it appeared.

1. **`import express from "express"`**: This brings code from another file or package into this one. `express` is the name we chose for what the package gives us. It only works because `package.json` says `"type": "module"`, which tells Node to use this modern `import` style instead of the older `require(...)`.
2. **`import http from "node:http"`**: The same thing, for a module built into Node. The `node:` part makes it clear it's built in, not something from npm.
3. **`const app = express()`**: `const` makes a name that can't be pointed at something else later. Use `const` by default; you'll meet `let`, the changeable version, in the next lesson.
4. **`(req, res) => { ... }`**: This is an **arrow function**, a short way to write a function. It's the same as `function (req, res) { ... }`. We pass it to `app.get`, and Express calls it later, when a request arrives. A function you hand over to be called later is called a **callback**.
5. **`{ id: "1", name: "Jollof rice" }`**: This is an **object**, a bundle of named values. `[ ..., ... ]` is an **array**, a list. `res.json` turns them into JSON text for you.
6. **`` `listening on http://localhost:${port}` ``**: The backticks make a **template string**. Anything inside `${ }` is worked out and dropped into the text, so this prints `listening on http://localhost:3000`.
7. **Where are the types?** We didn't write any, and TypeScript still knew `req` and `res` are Express's request and response, because `app.get` says what its callback receives. TypeScript working types out by itself is called **type inference**. You only write types where it can't work them out, which is most of what the coming lessons show.

## Common mistakes
<!-- bite: 6a74c028-4786-4d8e-a793-8d7a35c66868 -->

1. **Forgetting `"type": "module"`.** Node then refuses `import express from "express"`. Add it to `package.json`.
2. **Writing `import { Request } from "express"` for a type.** With Node running TypeScript directly, a type must be imported with `import type { Request } from "express"`.
3. **Not sending a response in some branch.** An `if` that returns early without `res.send` leaves the client hanging.
4. **Sending two responses.** Usually a missing `return` after the first `res.json(...)`.
5. **Port already in use.** `EADDRINUSE` means another program (often your app from an earlier run) is already on port 3000. Stop it, or use another port.

## Check your understanding
<!-- bite: 773dc85e-fa07-4a1f-bac5-475fc665de09 -->

1. In your own words, what does Express add on top of Node's `http` module?
2. A request for `POST /menu` arrives, and you only wrote `app.get("/menu", ...)`. What does the client get back, and why?
3. What's wrong with this handler?

   ```ts
   app.get("/menu", (req, res) => {
     res.status(200);
   });
   ```

<details>
<summary>Answers, after your attempt</summary>

1. Matching the method and path to the right function, reading the request, setting headers, turning objects into JSON, and a default 404. It's the same Node server underneath.
2. A 404, "Cannot POST /menu". Routes match on the method **and** the path together, and no route matches POST.
3. It sets the status but never sends a response, so the client waits forever. It needs `res.status(200).json(...)`, or just `res.json(...)`.

</details>

## Practice
<!-- bite: 1a48eb6b-08dd-4eed-b91f-fa3e96699569 -->

Add two routes to Mama Put API:

1. `GET /hours` returns `{ "opens": "07:00", "closes": "21:00" }`.
2. `GET /health` returns status 200 with the text `ok`. Real servers have a route like this so other programs can check the app is alive. We'll make it proper in the production lesson.

**Done when** `curl -i` against both shows status 200 with the right body, and `curl -i http://localhost:3000/hourz` still shows a 404.

## Your project so far
<!-- bite: 91fedbcd-8ffc-4f2d-bf85-c84342e1ce40 -->

```text
mama-put-api/
├── node_modules/        ← packages npm installed (never edit, never commit)
├── package.json         ← project name, "type": "module", scripts, dependencies
├── package-lock.json    ← the exact package versions installed (commit it)
├── tsconfig.json        ← how TypeScript checks the code
└── src/
    └── server.ts        ← the whole app: two routes and app.listen
```

1. **`package.json`**: says what the project is, that it uses `import` (`"type": "module"`), the `dev` and `check` scripts, and which packages it needs.
2. **`package-lock.json`**: written by npm. It pins exact versions so everyone who installs gets the same thing.
3. **`tsconfig.json`**: tells TypeScript and your editor how to check the code. Nothing runs from it.
4. **`src/server.ts`**: creates the app, defines `GET /` and `GET /menu`, and starts listening on port 3000.

Also add a `.gitignore` file with one line, `node_modules/`, so the installed packages never go into git.

## Before moving on
<!-- bite: 4f117284-465c-4fdf-bd14-13bf72054153 -->

You can start an Express app, and you know the path a request takes: in through Node, matched against your routes in order, handled, and answered exactly once.

Right now our menu is written straight into the route, and there's only one way to ask for it. A real menu needs to fetch one dish by its ID, add new dishes and remove old ones. That means different methods, IDs inside the path, and data in the body, and that's what routing is about. That's the next lesson.

## Related
<!-- bite: a59e3d6b-5b41-48dc-b148-a26c21a947d6 -->
- [[backend/frameworks/express/02-routing|Next: Routing]]
- [[backend/01-foundations/02-http-servers|HTTP Servers]] — what's underneath every framework
- [[backend/frameworks/node/index|Node.js]] — the runtime Express sits on

## About this lesson
<!-- bite: 33c127ef-edf5-4a24-9304-5095dec59dc1 -->

**Level:** Beginner. Lesson 1 of the [[backend/frameworks/express/index|Express]] subject, which teaches the whole backend course by building one app, Mama Put API. Written for Express 5 and Node.js 23.6 or later, which runs TypeScript directly.
