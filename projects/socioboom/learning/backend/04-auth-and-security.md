# SocioBoom Backend — Auth, Security, Secrets & OAuth Token Lifecycles

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/02-architecture-and-modules.md` (where the JWT guard is mounted in the middleware
chain), `learning/backend/05-queues-and-jobs.md` (the worker that consumes these tokens at publish
time), and `learning/backend/08-devops-and-deployment.md` (getting secrets into a deployed
environment).

This file covers: Passport JWT authentication and how the strategy is wired, Helmet, CORS and rate
limiting, environment variables and secret management, the Reddit app-only OAuth token flow,
encrypting user API keys at rest, and the cross-platform OAuth refresh story — why Twitter,
LinkedIn, Reddit and Facebook each need different refresh handling, and why Facebook's
`fb_exchange_token` has to run *before* expiry rather than after.

---

## 8. Authentication with Passport JWT

### What is JWT?

JWT (JSON Web Token) is a string that encodes a payload (like `{ userId: 42 }`) and signs it with a secret key. The server creates the token when the user logs in and sends it to the client. The client includes it in every subsequent request. The server verifies the signature to confirm the token came from itself and was not tampered with.

A JWT looks like: `header.payload.signature` — three base64-encoded segments separated by dots.

### Why JWTs?

JWTs are **stateless**. The server does not need to store session data in a database or Redis — it just checks the signature. This makes horizontal scaling (multiple server instances) trivial.

### Passport JWT Strategy

`src/config/auth.ts` registers the strategy (implementation details TBD in the codebase, but the pattern is):

```ts
// src/config/auth.ts
import passport from 'passport';
import { Strategy as JwtStrategy, ExtractJwt } from 'passport-jwt';
import prisma from '@/config/prisma';

passport.use(
  new JwtStrategy(
    {
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      secretOrKey: process.env.JWT_SECRET!,
    },
    async (payload, done) => {
      try {
        const user = await prisma.user.findUnique({ where: { id: payload.sub } });
        if (!user) return done(null, false);
        return done(null, user); // Attaches user to req.user
      } catch (err) {
        return done(err, false);
      }
    },
  ),
);
```

The `ExtractJwt.fromAuthHeaderAsBearerToken()` extractor reads the `Authorization: Bearer <token>` header from each request.

In `main.ts`, this line protects all `/api/v1` routes:

```ts
apiV1.use(passport.authenticate('jwt', { session: false }));
```

`{ session: false }` disables Passport's session middleware (you do not need sessions when using JWTs). If the token is missing or invalid, Passport sends a `401 Unauthorized` response before your controller ever runs.

The `import '@/config/auth'` at the top of `main.ts` is a side-effect import — it runs the file for its side effect (registering the strategy) without importing anything from it.

---

## 9. Security: Helmet, CORS, Rate Limiting

### Helmet

```ts
app.use(helmet());
```

Helmet sets several HTTP response headers that protect against common web vulnerabilities:

| Header | Protection against |
|---|---|
| `X-DNS-Prefetch-Control: off` | DNS prefetch leaking |
| `X-Frame-Options: SAMEORIGIN` | Clickjacking |
| `X-Content-Type-Options: nosniff` | MIME type sniffing |
| `Strict-Transport-Security` | Protocol downgrade attacks |
| `Content-Security-Policy` | XSS, data injection |
| `X-XSS-Protection: 0` | Turns off the buggy browser XSS filter |

Without Helmet, none of these headers are set. Browsers use them as defense layers. Attackers who find other vulnerabilities have fewer avenues to exploit.

### CORS

CORS (Cross-Origin Resource Sharing) is a browser security feature. When JavaScript at `https://app.socioboom.com` tries to call `https://api.socioboom.com`, the browser first asks the API: "do you allow requests from this origin?" The API responds with `Access-Control-Allow-Origin: https://app.socioboom.com`. Only then does the browser allow the request.

```ts
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true, // Allows cookies and Authorization headers
}));
```

CORS protection is enforced by the browser. Server-to-server requests (like from Postman or curl) are not subject to CORS. This is fine — the JWT authentication handles server-level access control.

### Rate Limiting

Rate limiting prevents a single user or IP from overwhelming the server.

```ts
// Global: 200 requests per 15 minutes
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes in milliseconds
  max: 200,
  standardHeaders: true,    // Send RateLimit-* headers (RFC 6585)
  legacyHeaders: false,     // Do not send X-RateLimit-* headers
  message: { error: 'Too many requests, please try again later.' },
});

// AI endpoints: 15 requests per minute
const aiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 15,
  message: { error: 'AI rate limit reached. Please wait a moment.' },
});
```

**Why stricter limits on AI endpoints?** Each AI request calls Anthropic or OpenRouter, which costs money and takes 2–10 seconds. Without a limit, a single user (or attacker who steals a JWT) could run up a huge API bill in seconds. 15 AI requests per minute is generous for real use but stops abuse.

The `windowMs` is a sliding window — each request is tracked with a timestamp. When the window resets, old requests fall off. `express-rate-limit` stores counts in memory by default. For a multi-server deployment, you would use the `redis` store option so all instances share the same counter.

---


## 16. OAuth: Reddit App-Only Token Flow

Reddit requires OAuth even for public read-only data. SocioBoom uses the "app-only" flow (also called "client credentials") which does not require a user to log in — it just authenticates the application itself.

### The Flow

```
SocioBoom server
  → POST https://www.reddit.com/api/v1/access_token
      Authorization: Basic base64(clientId:clientSecret)
      Body: grant_type=client_credentials

Reddit
  → { access_token: "xyz", expires_in: 3600, token_type: "bearer" }

SocioBoom server
  → GET https://oauth.reddit.com/search
      Authorization: Bearer xyz
      User-Agent: SocioBoom/1.0
```

### Token Caching

Making an OAuth token request before every API call wastes time and hits Reddit's rate limits. Instead, SocioBoom caches the token in memory:

```ts
private static redditToken: string | null = null;
private static redditTokenExpiry = 0; // Unix timestamp in ms

private static async getRedditToken(): Promise<string> {
  // If we have a valid cached token, return it immediately
  if (DiscoveryService.redditToken && Date.now() < DiscoveryService.redditTokenExpiry) {
    return DiscoveryService.redditToken;
  }

  // Otherwise, fetch a new token
  const { data } = await axios.post(
    'https://www.reddit.com/api/v1/access_token',
    'grant_type=client_credentials',
    {
      auth: {
        username: process.env.REDDIT_CLIENT_ID!,
        password: process.env.REDDIT_CLIENT_SECRET!,
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'SocioBoom/1.0',
      },
    },
  );

  // Cache the token. The - 60_000 gives a 1-minute buffer before expiry.
  DiscoveryService.redditToken = data.access_token as string;
  DiscoveryService.redditTokenExpiry = Date.now() + (data.expires_in as number) * 1000 - 60_000;

  return DiscoveryService.redditToken;
}
```

`expires_in` is in seconds (typically 3600 = 1 hour). Converting: `expires_in * 1000` = milliseconds. Subtracting `60_000` (1 minute) means the token is considered expired 1 minute before Reddit actually expires it — a safety buffer for clock skew and slow network calls.

**Important:** This cache is in the Node.js process memory. If you run multiple instances of the server, each has its own cached token. This is fine because each token is independently valid. For very high traffic, you could move the cache to Redis to share it across instances, but it is unnecessary here.

Both `ReviewService` and `DiscoveryService` implement this pattern independently. In a larger codebase, you would extract this into a shared `RedditAuthService`.

### Why `'grant_type=client_credentials'` as a String?

Reddit's token endpoint uses `application/x-www-form-urlencoded` encoding, not JSON. This means the body is a URL-encoded key-value string like `key=value&key2=value2`. Axios sends a string body as-is. If you passed an object `{ grant_type: 'client_credentials' }` without the right headers, Axios would serialize it as JSON, and Reddit's server would reject it.

---

## 17. Environment Variables and Secret Management

### The `.env` File

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/socioboom

# Server
PORT=3001
FRONTEND_URL=http://localhost:3000
JWT_SECRET=your-long-random-secret-string

# AI
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-opus-4-8
APP_URL=http://localhost:3001

# Social platforms
GOOGLE_PLACES_API_KEY=...
YELP_API_KEY=...
TWITTER_BEARER_TOKEN=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

### How `dotenv` Works

```ts
import dotenv from 'dotenv';
dotenv.config(); // Reads .env and adds each variable to process.env
```

`dotenv.config()` must be called before any code reads `process.env`. That is why it is at the top of `main.ts`.

`.env` is in `.gitignore`. It is never committed to version control. Each developer and each deployment environment has its own `.env` file. This ensures:
- Development keys are never in production
- Production secrets are never in git history
- Different developers can use different API keys

### The `!` Non-Null Assertion

```ts
const token = data.access_token as string;
const clientId = process.env.REDDIT_CLIENT_ID!;
```

The `!` tells TypeScript "I know this value cannot be null or undefined at runtime." It suppresses the TypeScript error `Object is possibly 'undefined'`. Use it only when you are genuinely certain — if `REDDIT_CLIENT_ID` is not set, the code will fail at runtime with a confusing error. In production-quality code, you would validate all required environment variables at startup:

```ts
// At startup, fail loudly if required env vars are missing
const required = ['DATABASE_URL', 'JWT_SECRET', 'ANTHROPIC_API_KEY'];
for (const key of required) {
  if (!process.env[key]) throw new Error(`Missing required env var: ${key}`);
}
```

---


## 27. Tokens at Rest and OAuth Refresh Across Platforms

### Encrypt at the model boundary

User API keys were AES-256-GCM encrypted, but the OAuth `accessToken`/`refreshToken` in `accounts` — arguably *more* sensitive, they can post as the user — were plaintext. The fix lives entirely in `AccountModel`, so no caller changes:

```ts
// iv:authTag:ciphertext hex triplet produced by config/encryption.ts
const ENCRYPTED_SHAPE = /^[0-9a-f]{32}:[0-9a-f]{32}:[0-9a-f]+$/i;

function open(value: string | null) {
  if (!value || !ENCRYPTED_SHAPE.test(value)) return value;  // legacy plaintext row
  try { return decrypt(value); } catch { return value; }
}
```

Two patterns here: **encrypt/decrypt at a single choke point** (every read/write already went through `AccountModel`, so the change is invisible everywhere else), and **tolerate legacy data** — rows written before encryption still decrypt as themselves and get sealed on their next write. No migration script, no downtime.

### Refresh is different on every platform

| Platform | Mechanism | Catch |
|---|---|---|
| Twitter | standard `refresh_token` grant | rotates the refresh token — store the new one |
| LinkedIn | `refresh_token` grant | only if your app has refresh enabled |
| Facebook | **no refresh token at all** — exchange the current token for a new long-lived one | exchange only works while the token is **still valid** |

Facebook's catch drives the design: you must refresh *proactively, before* expiry. Hence per-platform refresh windows:

```ts
const REFRESH_WINDOW_MS: Record<string, number> = {
  facebook: 7 * 24 * 60 * 60 * 1000,   // a week early — can't refresh after expiry
  twitter: 60_000,
  linkedin: 60_000,
};
```

And when refresh fails and the token is truly dead, **fail loudly**: create a notification telling the user to reconnect. The silent version of this bug is brutal — every scheduled post just quietly fails about 60 days after the user connected LinkedIn, and nobody knows why.

### Closing the analytics loop

The worker used to throw away the API responses after publishing. But those responses contain the platform's post ID — the key you need to *ever* fetch real engagement. Now each publisher returns it (`res.data.data.id` for Twitter, the `x-restli-id` header for LinkedIn, `json.data.name` for Reddit with `api_type: 'json'`), it's stored on `PostAnalytic.externalId`, and an hourly repeatable job pulls real like/share/comment counts:

```ts
engagementQueue.add('refresh', {}, { repeat: { every: 60 * 60 * 1000 } });
// BullMQ dedupes repeatable jobs by their repeat key — safe to run on every boot
```

Lesson: when you call an external API that *creates* something, always persist the returned ID, even if you don't need it yet. It's unrecoverable later.

---


