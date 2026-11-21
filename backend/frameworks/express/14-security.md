---
id: 5f112f78-4c8a-49ed-9ec3-96de19adb9ee
---

# Security

**Security, for a backend, means making sure the API still behaves correctly when the people calling it are trying to break it: guessing passwords, flooding it with requests, calling it from someone else's website, or sending "files" that are really attacks.** Everything so far assumed our own app was the caller. This lesson assumes the internet is.

## Before you start
<!-- bite: 20389142-13de-435d-9eec-22162266b198 -->

You should have authentication and authorization from [[backend/frameworks/express/13-authorization|lesson 13]].

After this lesson you will be able to:

1. Add the security headers every API should send, with `helmet`.
2. Explain what CORS is (and isn't), and allow only Mama Put's own websites.
3. Rate-limit the whole API, and the login route much more strictly.
4. Accept a photo upload safely: size limits, real type checks, safe names.
5. Set limits and timeouts so slow or huge requests can't tie the server up.

## Where we stopped
<!-- bite: 23f9a7b7-762a-4199-a805-98746435a45d -->

Lesson 13 ended with three attacks we haven't stopped:

1. **Password guessing.** Nothing stops someone trying 10,000 passwords against `ada@example.com`.
2. **Other websites calling our API.** A page on `evil.example` runs JavaScript in Ada's browser. Can it call our API as her?
3. **Uploads.** Mama wants a photo for each dish. A "photo" could be 2 GB, or an HTML page, or a program.

And a few we haven't even mentioned: requests that dribble in one byte a minute to hold connections open, and responses that let a browser guess what kind of content they are.

## The kid version
<!-- bite: 0dc2d07b-1f42-4843-88e5-5c67f99f0a9a -->

Mama Put's stand is now on a busy road, not in a quiet street. So she does what any sensible seller on a busy road does:

1. She puts up clear **signs**: "No smoking near the pots. Pay before you eat." (Security headers tell browsers the rules.)
2. She only takes **phone orders from numbers she knows**: her own shop's line and her sister's. (CORS.)
3. If one person asks for "just one more taste" fifty times, she stops serving them for a while. (Rate limiting.)
4. When a supplier brings a sack "of rice", she opens it and looks, and she doesn't accept sacks bigger than her store. (Upload checks.)
5. If someone stands at the counter for ten minutes saying nothing, she serves the next person. (Timeouts.)

**Where the picture stops working.** Mama can *see* a troublemaker. A server only sees requests, often thousands a second, and attackers rotate addresses. Each defence makes attacks slower and more expensive; none makes them impossible. That's why there are several, layered.

## Terms used in this lesson
<!-- bite: 6f8f5277-5960-43f5-880c-99a26303d75f -->

1. **Security header**: This is a response header that tells the browser how to treat our content safely, like "never guess this file's type" or "only ever talk to me over HTTPS".
2. **Origin**: This is a website's scheme, domain and port together, like `https://kitchen.mamaput.example`. Two pages have the same origin only if all three match.
3. **CORS**: This stands for **cross-origin resource sharing**. Browsers stop a page from one origin reading responses from another origin, unless that other server says it's allowed. CORS is how our server says so.
4. **Rate limiting**: This is capping how many requests one caller can make in a time window, and answering **429 Too Many Requests** past the cap.
5. **Brute force**: This is guessing, again and again, until something works, like trying passwords one after another.
6. **Magic bytes**: These are the first few bytes of a file, which say what kind of file it really is. A JPEG always starts with `FF D8 FF`, whatever its name says.
7. **Reverse proxy**: This is a server in front of ours, like nginx or a cloud load balancer, that receives requests from the internet and passes them on. It changes who our app thinks the caller is.

## Step 1: security headers with helmet
<!-- bite: a42979d7-c698-4808-8481-ea236d083227 -->

```bash
npm install helmet cors express-rate-limit multer file-type
npm install --save-dev @types/cors @types/multer
```

In `app.ts`, near the very top, after `requestId`:

```ts
import helmet from "helmet";

app.disable("x-powered-by");
app.use(helmet());
```

Now compare the headers before and after:

```bash
curl -sI http://localhost:3000/v2/menu
```

You'll see a handful of new headers. The ones that matter most for an API:

1. **`X-Content-Type-Options: nosniff`**: "Don't guess what this is; believe my `Content-Type`." Without it, a browser might decide an uploaded "image" is really HTML and run it.
2. **`Strict-Transport-Security`**: "For the next year, only ever talk to me over HTTPS." After one visit, the browser refuses plain HTTP, so nobody on the café Wi-Fi can read tokens.
3. **`Content-Security-Policy`**: "Only run scripts and load things from these places." It matters most for HTML pages, like our Swagger docs.
4. **`X-Frame-Options` / `frame-ancestors`**: "Don't let other sites put me in a frame", which stops tricks where your page is hidden under someone else's button.

And `X-Powered-By: Express` is gone. It helped nobody but attackers looking for apps on a framework version with a known bug.

(If `/docs` shows a blank page after this, the Content Security Policy is blocking something Swagger UI needs. Give the docs route its own, looser `helmet({ contentSecurityPolicy: ... })`, or mount `/docs` before `helmet` and keep it behind the staff login. Don't turn the policy off for the whole API.)

## Step 2: CORS, and what it isn't
<!-- bite: 9e47b506-c45f-491b-835b-3912d9f29f20 -->

First, the most important sentence about CORS: **CORS is not a lock on your API.** It only affects JavaScript running in a **browser**. `curl`, a phone app, Postman and an attacker's script ignore it entirely. Every real protection, authentication, authorization and rate limits, must work without it.

So what *is* it for? Browsers have a rule called the **same-origin policy**: a page from `evil.example` can *send* requests to `api.mamaput.example`, but it can't *read* the responses, unless our server says that origin is allowed. That protects Ada: if she's logged in to a Mama Put website, a random site she visits can't quietly read her orders through her browser.

Mama Put's phone app isn't a browser, so it needs no CORS at all. But the kitchen has a web dashboard at `https://kitchen.mamaput.example`, and that one does:

```ts
import cors from "cors";

const ALLOWED_ORIGINS = ["https://kitchen.mamaput.example", "https://mamaput.example"];

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || ALLOWED_ORIGINS.includes(origin)) callback(null, true);
      else callback(null, false);
    },
    methods: ["GET", "POST", "PATCH", "DELETE"],
    allowedHeaders: ["Authorization", "Content-Type", "Idempotency-Key", "Api-Version"],
    exposedHeaders: ["X-Request-Id", "Deprecation", "Sunset"],
    maxAge: 600,
  }),
);
```

1. **`origin`**: an allow-list. A request with no `Origin` header isn't from a browser page (it's `curl` or the phone app), so CORS doesn't apply and we let it through to the normal checks. A browser page from an origin not on the list gets no CORS headers, so its JavaScript can't read the answer.
2. **`allowedHeaders`**: the request headers a browser page may send. `Authorization` is needed for tokens, and `Idempotency-Key` for [[backend/frameworks/express/15-idempotency|lesson 15]].
3. **`exposedHeaders`**: by default, browser code can only read a few response headers. We let the dashboard read the request ID and the deprecation headers.
4. **`maxAge: 600`**: before a "non-simple" request (one with `Authorization`, say), the browser sends an `OPTIONS` **preflight** asking "may I?". `maxAge` lets it remember the answer for 10 minutes instead of asking every time.

Never write `origin: "*"` together with credentials. And move the origin list to config in [[backend/frameworks/express/28-production-config-and-docker|lesson 28]], since staging and production have different websites.

## Step 3: rate limiting
<!-- bite: a59e0729-ef59-4167-8578-8a7676d8ae4a -->

Two limits, for two different dangers.

**A general limit for everything**, so one caller can't flood the API:

```ts
// src/shared/rate-limits.ts
import { rateLimit } from "express-rate-limit";
import type { Request, Response } from "express";

function tooMany(req: Request, res: Response) {
  res.status(429).type("application/problem+json").json({
    type: "https://mamaput.example/problems/too-many-requests",
    title: "Too many requests",
    status: 429,
    detail: "You're sending requests too quickly. Wait a little and try again.",
    code: "too-many-requests",
    requestId: res.locals.requestId,
  });
}

export const generalLimit = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 600,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  handler: tooMany,
});
```

**A strict limit for logging in**, so password guessing becomes hopeless:

```ts
export const loginLimit = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 5,
  standardHeaders: "draft-8",
  legacyHeaders: false,
  skipSuccessfulRequests: true,
  handler: tooMany,
});
```

```ts
app.use(generalLimit);                                   // in app.ts, early
router.post("/login", loginLimit, async (req, res) => { ... });  // in auth.routes.ts
```

Five failed logins per 15 minutes means an attacker gets 480 guesses a day, not millions. Against a 10-character password, that's nothing. `skipSuccessfulRequests` means a successful login doesn't count, so Ada isn't locked out by her own good logins.

With `standardHeaders: "draft-8"`, every response tells the client where it stands (a `RateLimit` header with how many are left and when the window resets), and a 429 says how long to wait. Well-behaved clients slow down by themselves.

These limits count per **IP address** by default. Two things about that:

1. **Behind a reverse proxy, every request seems to come from the proxy.** Then *everyone* shares one limit, and one busy minute locks out all customers. The proxy puts the real address in the `X-Forwarded-For` header, and you tell Express to trust exactly one proxy:

   ```ts
   app.set("trust proxy", 1);
   ```

   Exactly one, the number of proxies you really have. Set `true` and an attacker can send their own `X-Forwarded-For` with a fake address, giving them a fresh limit on every request.

2. **The counts live in this app's memory.** Run two copies of the app and each counts separately, so the real limit is double. Restart, and the counts reset. In [[backend/frameworks/express/19-caching|lesson 19]], with Redis running, the limiter gets a shared store.

For login, attackers spread guesses across many addresses, so per-address limits aren't enough by themselves. A good next step is a second limit keyed on the **email** being tried, so one account can't get 5 guesses from each of a thousand addresses. (The library's docs show how to write a key that combines both; newer versions warn if you use `req.ip` directly in a custom key, and offer a helper that handles IPv6 addresses correctly.)

## Step 4: size limits and timeouts
<!-- bite: 4ec68c48-c304-4184-8a2b-05fc73de3369 -->

Every limit is a promise about what the server will put up with. Write them down on purpose instead of accepting defaults.

**Body size.** `express.json()` accepts 100 KB by default. A dish or an order is a few hundred bytes:

```ts
app.use(express.json({ limit: "20kb" }));
```

A bigger body gets the 413 problem from [[backend/frameworks/express/07-errors|lesson 7]], before any of our code runs.

**Time.** A slow client can open a connection and send one byte a minute, holding it open forever. Enough of those and the server runs out of connections. In `server.ts`:

```ts
const server = createApp(deps).listen(3000);
server.requestTimeout = 30_000;   // the whole request must arrive within 30 s
server.headersTimeout = 10_000;   // the headers within 10 s
```

A proxy in front usually has its own timeouts too. Ours are the backstop.

## Step 5: dish photos, uploaded safely
<!-- bite: c595fd71-2790-4d76-adc4-52756b54d3b4 -->

Mama wants a photo for each dish: `POST /v2/menu/:id/photo`, a normal form upload with one file called `photo`.

Uploads are where many apps get hurt. Every part of an upload is chosen by the person sending it: the file's name, the type it *claims* to be, its size, and what's actually inside. We trust none of it.

```ts
// src/menu/menu.photos.ts
import multer from "multer";
import { fileTypeFromBuffer } from "file-type";
import { randomUUID } from "node:crypto";
import { writeFile } from "node:fs/promises";
import { AppError } from "../shared/errors.ts";

export const photoUpload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 2 * 1024 * 1024, files: 1, fields: 0 },
}).single("photo");

const ALLOWED = { "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp" } as const;

export async function savePhoto(buffer: Buffer, folder: URL): Promise<string> {
  const type = await fileTypeFromBuffer(buffer);
  if (!type || !(type.mime in ALLOWED)) {
    throw new AppError("invalid", "unsupported-image", "The photo must be a JPEG, PNG or WebP image.");
  }
  const name = `${randomUUID()}.${ALLOWED[type.mime as keyof typeof ALLOWED]}`;
  await writeFile(new URL(name, folder), buffer);
  return name;
}
```

The route:

```ts
router.post("/:id/photo", requirePermission("menu:write"), photoUpload, async (req, res) => {
  const { id } = validate(DishIdSchema, req.params, "params");
  if (!req.file) throw new AppError("invalid", "photo-required", "Send the image in a field called 'photo'.");
  const fileName = await savePhoto(req.file.buffer, photosFolder);
  const dish = await menuService.setPhoto(req.user!, id, fileName);
  res.json({ data: version.presentDish(dish, req.user) });
});
```

(`photosFolder` is `new URL("../../uploads/photos/", import.meta.url)`, built in `server.ts` and passed to the router through `deps` like everything else. `menuService.setPhoto` stores the file name in a new `photo` column on `dishes`, from migration 009.)

Each line stops a real attack:

1. **`requirePermission` comes before `photoUpload`.** Otherwise anyone could make the server read 2 MB before being told no. Check who they are first, then accept their bytes.
2. **`fileSize: 2 MB`, `files: 1`, `fields: 0`**: no 2 GB "photos", no 500 files at once.
3. **`fileTypeFromBuffer` reads the magic bytes.** The client says `Content-Type: image/jpeg` and names it `jollof.jpg`. Both are just claims. An HTML page renamed to `.jpg` starts with `<html>`, not `FF D8 FF`, and is refused.
4. **We make the file name** with `randomUUID()`. A client-chosen name like `../../server.ts` could write *outside* the photos folder and overwrite our code. A random name can't, and nobody can guess other photos' names either.
5. **The extension comes from the real type**, not from what was uploaded.

Too-big files raise a multer error. Teach the error handler about it, next to the body-parser door from lesson 7:

```ts
import multer from "multer";

if (err instanceof multer.MulterError) {
  const tooBig = err.code === "LIMIT_FILE_SIZE";
  sendProblem(res, tooBig ? 413 : 400, tooBig ? "file-too-large" : "bad-upload",
    tooBig ? "File too large" : "Bad upload",
    tooBig ? "Photos can be at most 2 MB." : "The upload was not in the expected shape.");
  return;
}
```

Serve the photos as plain files from their own folder: `app.use("/photos", express.static("uploads/photos"))`. Because of `nosniff`, a browser treats each one as exactly the image type the server says.

Two steps further, for later. Real systems **re-encode** every uploaded image (with a library like `sharp`), which throws away anything hidden inside it and strips the location data phones put in photos. And they store files in **object storage** (Amazon S3, Cloudflare R2, Google Cloud Storage), not on the server's own disk, so every copy of the app sees every photo. When we put the app in containers in [[backend/frameworks/express/28-production-config-and-docker|lesson 28]], the local disk stops being a safe place for anything that must last.

## Step 6: the boring things that matter
<!-- bite: b55e579e-9313-44a2-ba6f-c487820b9c9a -->

1. **HTTPS everywhere.** Tokens and passwords travel in every request. In production, the proxy handles HTTPS, and HSTS (from helmet) keeps browsers on it.
2. **Never log secrets.** No `Authorization` headers, no passwords, no refresh tokens in logs. When we add a real logger in lesson 27, we'll tell it to hide those fields.
3. **Keep dependencies patched.** `npm audit` lists packages with known holes. Most attacks on small companies use bugs that already have fixes. In lesson 29, a bot opens a pull request when an update is available.
4. **Commit the lockfile.** `package-lock.json` makes sure production installs exactly what you tested, not "whatever's newest today".
5. **Give each part the least power it needs.** The app's database user should not be allowed to drop tables. (Lesson 28 does this with a separate migration user.)

## The TypeScript in this lesson
<!-- bite: aeba8bcf-54e9-4b12-a233-d73d1aa19b77 -->

1. **`import { rateLimit } from "express-rate-limit"`** and **`import helmet from "helmet"`**: Some packages offer a named export (braces), some a default export (no braces). The package's docs tell you which.
2. **`origin: (origin, callback) => { ... }`**: Instead of a fixed value, `cors` accepts a function it calls for every request. You answer by calling `callback(error, allowed)`. This **callback style** is older than promises, and you'll still meet it in many packages.
3. **`callback(null, true)`**: In callback style, the first argument is an error (`null` means "no error") and the second is the answer.
4. **`server.requestTimeout = 30_000`**: `listen()` returns Node's `http.Server`, and you set its options as fields.
5. **`multer({...}).single("photo")`**: Builds one middleware that reads exactly one file from the form field called `photo` and puts it on `req.file`. multer adds `file` to Express's `Request` type for you, through the same declaration merging you used for `req.user`.
6. **`2 * 1024 * 1024`**: Two megabytes in bytes (a kilobyte is 1024 bytes in this kind of limit).
7. **`type.mime in ALLOWED`**: `in` checks whether the object has that key. It's how we ask "is this one of the allowed types?".
8. **`ALLOWED[type.mime as keyof typeof ALLOWED]`**: `keyof typeof ALLOWED` is `"image/jpeg" | "image/png" | "image/webp"`. We've just checked `type.mime` is one of them, so we tell TypeScript, and get the right extension.
9. **`err instanceof multer.MulterError`**: multer's errors are their own class, so the error handler can recognise them, exactly like `AppError`.

## Your project so far
<!-- bite: 96598b12-7426-42ef-88c2-5a763545088b -->

```text
mama-put-api/
├── .env · .env.example · .gitignore · tsconfig.json
├── package.json                  ← helmet, cors, express-rate-limit, multer, file-type
├── migrations/
│   ├── 001 … 008
│   └── 009_dish_photos.sql       ← NEW: dishes.photo text (the file name)
├── uploads/
│   └── photos/                   ← NEW: uploaded photos (git-ignored; object storage later)
├── openapi/      v1.json · v2.json (429, 413 and the photo upload documented)
└── src/
    ├── server.ts                 ← requestTimeout and headersTimeout
    ├── app.ts                    ← trust proxy, helmet, cors, generalLimit, json 20kb, /photos
    ├── api.ts · types/express.d.ts
    ├── auth/                     ← auth.routes.ts uses loginLimit on /login
    ├── admin/ · docs/ · db/ · orders/
    ├── menu/
    │   ├── menu.photos.ts        ← NEW: photoUpload, savePhoto (magic bytes, random names)
    │   └── menu.routes.ts        ← POST /:id/photo
    └── shared/
        ├── rate-limits.ts        ← NEW: generalLimit, loginLimit, the 429 problem
        └── error-handler.ts      ← now also handles multer errors (413 / 400)
```

## Common mistakes
<!-- bite: 11196784-aa36-446c-bfa9-11253549e557 -->

1. **Thinking CORS protects the API.** It only stops browser pages reading responses. Everything else ignores it.
2. **`cors({ origin: "*" })` with credentials.** Either browsers refuse it, or you've let every site in.
3. **`trust proxy` set to `true`.** Attackers fake `X-Forwarded-For` and get unlimited fresh limits. Set the real number of proxies.
4. **Rate-limiting login like everything else.** Login needs a much stricter limit than reading the menu.
5. **Trusting an upload's name, size or claimed type.** Check the magic bytes, set limits, and make your own name.
6. **Accepting an upload before checking permission.** Check who they are, then read their bytes.
7. **Saving uploads where the app serves code, or with the client's file name.** That's how files get overwritten or run.
8. **Logging tokens or passwords.** Logs get shared, copied and leaked far more casually than databases.
9. **No limits at all, "because the defaults are fine".** Choose every limit on purpose.

## Check your understanding
<!-- bite: 535351e9-03e1-4118-84f6-8a884dc5df21 -->

1. A phone app and `curl` both call `GET /v2/orders` with Ada's token. Does CORS affect either?
2. Why does `loginLimit` use `skipSuccessfulRequests: true`?
3. You deploy behind a load balancer and forget `trust proxy`. What do customers notice at lunchtime?
4. Someone uploads `photo.jpg` with `Content-Type: image/jpeg`, but the file is an HTML page. Which line stops it, and what would have happened without `nosniff`?

<details>
<summary>Answers, after your attempt</summary>

1. No. CORS only applies to JavaScript in a browser page reading a response from another origin. The phone app and `curl` aren't browser pages, so only authentication and authorization apply to them.
2. So that only *failed* logins count towards the limit. A customer who logs in correctly several times (on two phones, say) isn't locked out; an attacker guessing wrong burns through 5 attempts fast.
3. Every request seems to come from the load balancer's address, so all customers share one general limit, and at lunchtime everyone starts getting 429s together.
4. `fileTypeFromBuffer` finds no image signature, so `savePhoto` refuses it with `unsupported-image`. Without the check *and* without `nosniff`, a browser opening that "photo" might sniff it as HTML and run any script inside it, on our domain.

</details>

## Practice
<!-- bite: 3ce2e466-76e1-44d1-87a7-c54ca3aa9297 -->

1. Add a second login limit keyed on the email address (10 failures per hour per email), so one account can't be guessed from many addresses.
2. Move `ALLOWED_ORIGINS`, the rate limit numbers and the upload size into `.env`, read in `server.ts` and passed in through `createApp`.
3. Run `npm audit`. Read what it reports, and update anything it can fix without breaking changes.

**Done when** the sixth wrong password in 15 minutes gets 429 with a `RateLimit` header; a browser page on an unlisted origin can't read `/v2/orders` (try it from the browser console on any other website, with `fetch`); a renamed HTML file is refused as `unsupported-image`; a 3 MB photo gets 413; and `curl -sI` shows `nosniff` and `Strict-Transport-Security`.

## Before moving on
<!-- bite: 27109b3c-2f4f-4fed-b14c-bb608b6ee191 -->

Mama Put API can now stand on a busy road: headers that keep browsers safe, CORS for its own websites only, rate limits that make guessing hopeless, uploads it actually checks, and limits on everything.

But there's one attack that isn't an attack at all. Ada's phone goes into a tunnel just as she taps "Place order". The request reaches us, we create the order, but the answer never reaches her phone. Her app does what good apps do: it tries again. Now Ada has two orders, and in lesson 17, she'll have paid twice. No firewall stops this. The fix is making "place order" safe to repeat, and that's idempotency, the next lesson.

## Related
<!-- bite: c16c2234-77d3-4c2f-92f4-f3e894110a21 -->

- [[backend/frameworks/express/15-idempotency|Next: Idempotency]]
- [[backend/06-cross-cutting/06-security-headers-and-cors|Security Headers and CORS]] · [[backend/06-cross-cutting/04-rate-limiting|Rate Limiting]] · [[backend/06-cross-cutting/07-file-uploads|File Uploads]] — the ideas in any framework
- [[cybersecurity/index|Cybersecurity]] — the attacks in more depth

## About this lesson
<!-- bite: 91f67c23-49ff-4e6b-ac0b-4a9c34f9b05b -->

**Level:** Intermediate → Advanced. Lesson 14 of [[backend/frameworks/express/index|Express]]. Covers helmet's security headers, what CORS is and isn't (same-origin policy, allow-lists, preflights, exposed headers), general and login rate limits with standard `RateLimit` headers and a 429 problem, `trust proxy`, body size limits, request and header timeouts, safe photo uploads with multer (limits, magic bytes with file-type, random names, permission before bytes), multer errors, and the everyday basics: HTTPS, secret-free logs, patched dependencies and least privilege.
