---
id: 2b218d5d-dbfb-44e1-81ae-f387517cf41e
---

# Security

**Security, for a backend, is making every way in as hard to abuse as you can: telling browsers the safe rules, limiting how fast anyone can knock, refusing anything too big or too slow, and trusting nothing a client sends, not even a file's name.** Authentication and authorization (lessons 12 and 13) decide who may do what. This lesson is about everything around them: the attacks that don't need a password at all.

## Before you start
<!-- bite: 0ce520f2-d773-4653-ba01-63e2938613e0 -->

You should have:

1. Finished [[backend/frameworks/net-http/13-authorization|lesson 13]], so logins, roles and ownership checks all work.
2. Met the `http.Server` timeouts from [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|lesson 1]] and `MaxBytesReader` from [[backend/frameworks/net-http/06-validation|lesson 6]].

After this lesson you will be able to:

1. Send security headers, and explain what each one protects against.
2. Write CORS by hand, and explain what it does and what it doesn't.
3. Rate-limit with `golang.org/x/time/rate`: a general limit for everyone, and a strict one for logging in.
4. Find the real client address behind a proxy without letting clients fake it.
5. Accept dish photos safely: size, real type, image dimensions, and a file name we choose, written inside a folder they can't escape.

## Where we stopped
<!-- bite: ba3ae5bf-f805-4543-ba7a-96d4b00de9f8 -->

Lesson 13 ended with three attacks we haven't stopped:

1. **Password guessing.** Nothing stops someone trying 10,000 passwords against `ada@example.com`.
2. **Other websites calling our API.** A page on `evil.example` runs JavaScript in Ada's browser. Can it call our API as her?
3. **Uploads.** Mama wants a photo for each dish. A "photo" could be 2 GB, or an HTML page, or a tiny file that unpacks into a picture the size of a football field.

Some we already handle, from earlier lessons: request bodies are capped at 1 MB (lesson 6), and the server has timeouts, so a client that dribbles in one byte a minute is cut off (lesson 1). This lesson adds the rest, and tightens those.

## The kid version
<!-- bite: 2903d779-aaff-4a8f-bdf4-d7ca5e68ded7 -->

Mama Put's stand is now on a busy road, not in a quiet street. So she does what any sensible seller on a busy road does:

1. She puts up clear **signs**: "No smoking near the pots. Pay before you eat." (Security headers tell browsers the rules.)
2. She only takes **phone orders from numbers she knows**: her own shop's line and her sister's. (CORS.)
3. If one person asks for "just one more taste" fifty times, she stops serving them for a while. (Rate limiting.)
4. When a supplier brings a sack "of rice", she opens it and looks, and she doesn't accept sacks bigger than her store. (Upload checks.)
5. If someone stands at the counter for ten minutes saying nothing, she serves the next person. (Timeouts.)

**Where the picture stops working.** Mama can *see* a troublemaker. A server only sees requests, often thousands a second, and attackers change addresses. Each defence makes attacks slower and more expensive; none makes them impossible. That's why there are several, in layers.

## Terms used in this lesson
<!-- bite: 14c4ea3f-bed0-4432-896f-233b34648e93 -->

1. **Security header**: This is a response header that tells the browser how to treat our content safely, like "never guess this file's type" or "only ever talk to me over HTTPS".
2. **Origin**: This is a website's scheme, domain and port together, like `https://kitchen.mamaput.example`. Two pages have the same origin only if all three match.
3. **CORS**: This stands for **cross-origin resource sharing**. Browsers stop a page from one origin reading responses from another origin, unless that other server says it's allowed. CORS is how our server says so.
4. **Preflight**: This is the `OPTIONS` request a browser sends before some cross-origin requests, asking "may I send this?".
5. **Rate limiting**: This is capping how many requests one caller can make in a time, and answering **429 Too Many Requests** past the cap.
6. **Token bucket**: This is the way `x/time/rate` counts. Each caller has a bucket of tokens that refills at a steady rate; each request takes one; an empty bucket means "wait".
7. **Brute force**: This is guessing, again and again, until something works, like trying passwords one after another.
8. **Reverse proxy**: This is a server in front of ours, like nginx or a cloud load balancer, that receives requests from the internet and passes them on. It changes who our app thinks the caller is.
9. **Magic bytes**: These are the first few bytes of a file, which say what kind of file it really is. A JPEG always starts with `FF D8 FF`, whatever its name says.
10. **Path traversal**: This is an attack where a file name like `../../cmd/api/main.go` escapes the folder it was meant to stay in.

## What to install
<!-- bite: 411251db-ff7f-4d6b-9b16-376df2cb0cd1 -->

Go's standard library already has most of what this lesson needs: there's no helmet or cors package to add, because the code is short enough to write and read yourself. Two packages from the Go team fill the gaps: a rate limiter, and a WebP image reader (the standard library reads JPEG and PNG, but not WebP).

```bash
go get golang.org/x/time/rate
go get golang.org/x/image
```

And `govulncheck`, the Go team's tool for finding known security holes in your dependencies, as a tool in `go.mod`, the way lesson 11 added oapi-codegen:

```bash
go get -tool golang.org/x/vuln/cmd/govulncheck@latest
```

## Step 1: security headers
<!-- bite: d1eb20d8-78a9-485b-840e-f3f636d58f48 -->

In Express, the `helmet` package sets a dozen headers at once. In Go, it's a middleware you write, and it's short. `internal/httpx/security.go`:

```go
package httpx

import "net/http"

// apiCSP is for JSON: nothing on our responses should ever run or load anything.
const apiCSP = "default-src 'none'; frame-ancestors 'none'"

func SecurityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		h := w.Header()
		h.Set("X-Content-Type-Options", "nosniff")
		h.Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		h.Set("Content-Security-Policy", apiCSP)
		h.Set("X-Frame-Options", "DENY")
		h.Set("Referrer-Policy", "no-referrer")
		h.Set("Cross-Origin-Resource-Policy", "same-site")
		next.ServeHTTP(w, r)
	})
}
```

The headers are set **before** `next` runs, because once a handler writes its status, headers can't change (lesson 1). A handler that needs a different value just sets its own, which replaces ours. That's exactly what the docs page does, below.

What each one says to the browser:

1. **`X-Content-Type-Options: nosniff`**: "Don't guess what this is; believe my `Content-Type`." Without it, a browser might decide an uploaded "image" is really HTML, and run the script inside it.
2. **`Strict-Transport-Security`**: "For the next year, only ever talk to me over HTTPS." After one visit, the browser refuses plain HTTP, so nobody on the café Wi-Fi can read tokens off the wire. It only counts when it arrives over HTTPS, so it's harmless on `localhost`.
3. **`Content-Security-Policy`**: "Only run scripts and load things from these places." For JSON, the answer is "nowhere": `default-src 'none'`. It matters most for HTML pages.
4. **`X-Frame-Options: DENY`** and **`frame-ancestors 'none'`**: "Don't let other sites put me in a frame." This stops **clickjacking**, where your page is hidden under someone else's button. The first is for old browsers, the second for new ones.
5. **`Referrer-Policy: no-referrer`**: "When someone follows a link from my page, don't tell the other site where they came from." URLs can carry IDs or cursors that are nobody else's business.
6. **`Cross-Origin-Resource-Policy: same-site`**: "Other websites may not embed my responses", so a page elsewhere can't use our photos or JSON as if they were its own.

Notice what's **not** there. Express adds `X-Powered-By: Express` to every response, and step one of helmet is removing it. Go's server never sends one, nor a `Server` header with its version. There's nothing to take away.

**The docs page is HTML**, and it loads Swagger UI from a CDN (lesson 11). Under `default-src 'none'`, the browser would refuse the script and show a blank page. So the docs handler sets its own, looser policy, naming exactly what it needs:

```go
const docsCSP = "default-src 'none'; " +
	"script-src https://cdn.jsdelivr.net 'unsafe-inline'; " +
	"style-src https://cdn.jsdelivr.net; " +
	"img-src 'self' data:; " +
	"connect-src 'self'; " +
	"frame-ancestors 'none'"

mux.HandleFunc("GET /docs", func(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Security-Policy", docsCSP)
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Write(docsPage)
})
```

`'unsafe-inline'` is needed because the page has one small `<script>` block of its own. It's acceptable on a page with no user content. Loosen the policy for the one page that needs it, never for the whole API.

## Step 2: CORS, and what it isn't
<!-- bite: de753031-ab1d-4dca-9786-8ce53317bd05 -->

First, the most important sentence about CORS: **CORS is not a lock on your API.** It only affects JavaScript running in a **browser**. `curl`, a phone app, Postman and an attacker's script ignore it entirely. Every real protection (authentication, authorization, rate limits) must work without it.

So what *is* it for? Browsers have a rule called the **same-origin policy**: a page from `evil.example` can *send* requests to `api.mamaput.example`, but it can't *read* the responses, unless our server says that origin is allowed. That protects Ada: if she's logged in to a Mama Put website, a random site she visits can't quietly read her orders through her browser.

Mama Put's phone app isn't a browser, so it needs no CORS at all. But the kitchen has a web dashboard at `https://kitchen.mamaput.example`, and that one does. `internal/httpx/cors.go`:

```go
package httpx

import (
	"net/http"
	"slices"
	"strings"
)

type CORSPolicy struct {
	Origins []string // exact origins, like "https://kitchen.mamaput.example"
}

var (
	corsMethods = "GET, POST, PATCH, DELETE"
	corsHeaders = "Authorization, Content-Type, Idempotency-Key, Api-Version"
	corsExpose  = "X-Request-Id, Deprecation, Sunset, Link, Retry-After"
)

func CORS(p CORSPolicy) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Add("Vary", "Origin")
			origin := r.Header.Get("Origin")
			allowed := origin != "" && slices.Contains(p.Origins, origin)

			if allowed {
				w.Header().Set("Access-Control-Allow-Origin", origin)
				w.Header().Set("Access-Control-Expose-Headers", corsExpose)
			}

			// A preflight: answer it here. The mux would answer 405, since no route has OPTIONS.
			if r.Method == http.MethodOptions && r.Header.Get("Access-Control-Request-Method") != "" {
				w.Header().Add("Vary", "Access-Control-Request-Method, Access-Control-Request-Headers")
				if allowed {
					w.Header().Set("Access-Control-Allow-Methods", corsMethods)
					w.Header().Set("Access-Control-Allow-Headers", corsHeaders)
					w.Header().Set("Access-Control-Max-Age", "600")
				}
				w.WriteHeader(http.StatusNoContent)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

func originsFrom(list string) []string { return strings.Fields(strings.ReplaceAll(list, ",", " ")) }
```

Read it as the browser's conversation:

1. **No `Origin` header**: the request isn't from a browser page on another site. It's `curl`, the phone app, or a page on our own origin. CORS doesn't apply; the request carries on to the normal checks.
2. **An origin on the list**: we answer with `Access-Control-Allow-Origin` set to **that exact origin**, so the browser lets that page's JavaScript read the response. `Expose-Headers` lets it read the request ID and the deprecation headers too; by default, browser code can see only a handful of response headers.
3. **An origin not on the list**: we add nothing. The request still runs (CORS never stops a request reaching you; that's authorization's job), but the browser hides the response from the page.
4. **A preflight**: before a request with `Authorization` or a JSON body, the browser asks first with `OPTIONS`. We answer with which methods and headers are allowed, and `Max-Age: 600` lets the browser remember the answer for 10 minutes instead of asking before every request.

Two Go details:

1. **The preflight must be answered before the mux.** Our routes are `POST /v2/orders`, `GET /v2/menu` and so on. An `OPTIONS` request matches none of them, so Go 1.22's mux would answer **405 Method Not Allowed**, and the browser would give up. That's why `CORS` is a middleware in the chain, outside the mux, and returns without calling `next` for preflights.
2. **`Vary: Origin`**: The answer now depends on the `Origin` header, so caches must keep a separate copy per origin. Without it, a cache could hand the kitchen's "allowed" answer to `evil.example`. It's the same reason as `Vary` in lesson 10's header versioning.

Never answer `Access-Control-Allow-Origin: *` on an API that uses logins. And never **echo back** whatever `Origin` arrives without checking it against the list; that's `*` with extra steps.

(There's a well-used package, `github.com/rs/cors`, that does all this with more options. Our version is small enough to read in a minute, and you now know what any CORS package is doing inside.)

The allowed origins come from settings, since staging and production have different websites. In `.env`:

```text
CORS_ORIGINS=http://localhost:5173
```

and in `run`, `httpx.CORSPolicy{Origins: originsFrom(getenv("CORS_ORIGINS"))}` goes into `app.Deps`. (Move `originsFrom` next to `run` if you prefer; lesson 28 gathers every setting into one validated config.)

**What about CSRF?** **Cross-site request forgery** tricks a browser into *sending* a request that rides on the cookies it already has. It's the big danger for cookie sessions. Our API doesn't use cookies: the token is in a header that the app adds itself, and a page on another site can't make Ada's browser add it. So CSRF doesn't reach us. If you ever move to cookie sessions, Go 1.25 added `http.NewCrossOriginProtection()`, a middleware that refuses cross-site form posts using headers that modern browsers send.

## Step 3: rate limiting
<!-- bite: 217c4374-5d8d-4996-a7c6-4bb8d0981118 -->

Two limits, for two different dangers: a **general limit** so one caller can't flood the API, and a **strict login limit** so password guessing becomes hopeless.

`x/time/rate` gives us one bucket: `rate.NewLimiter(r, b)` makes a bucket that holds `b` tokens and refills at `r` tokens a second. `lim.Allow()` takes a token if there is one and says yes, or says no. But we need one bucket **per caller**, so we keep a map of them. `internal/httpx/ratelimit.go`:

```go
package httpx

import (
	"net/http"
	"strconv"
	"sync"
	"time"

	"golang.org/x/time/rate"

	"mamaput/internal/apperr"
)

// Limiters keeps one token bucket per key (an address, an email).
type Limiters struct {
	mu        sync.Mutex
	every     rate.Limit
	burst     int
	buckets   map[string]*bucket
	lastSweep time.Time
}

type bucket struct {
	lim      *rate.Limiter
	lastSeen time.Time
}

// NewLimiters allows burst requests at once, then one every `per`.
func NewLimiters(burst int, per time.Duration) *Limiters {
	return &Limiters{every: rate.Every(per), burst: burst, buckets: map[string]*bucket{}}
}

func (l *Limiters) For(key string) *rate.Limiter {
	l.mu.Lock()
	defer l.mu.Unlock()

	now := time.Now()
	if now.Sub(l.lastSweep) > time.Minute {
		for k, b := range l.buckets {
			if now.Sub(b.lastSeen) > 30*time.Minute {
				delete(l.buckets, k)
			}
		}
		l.lastSweep = now
	}

	b, ok := l.buckets[key]
	if !ok {
		b = &bucket{lim: rate.NewLimiter(l.every, l.burst)}
		l.buckets[key] = b
	}
	b.lastSeen = now
	return b.lim
}

// RetryAfter is how long until one more request is allowed.
func (l *Limiters) RetryAfter() time.Duration {
	return time.Duration(float64(time.Second) / float64(l.every))
}

var ErrTooManyRequests = apperr.New(apperr.TooManyRequests, "too-many-requests",
	"You're sending requests too quickly. Wait a little and try again.")

func WriteTooMany(w http.ResponseWriter, r *http.Request, wait time.Duration) {
	w.Header().Set("Retry-After", strconv.Itoa(int(wait.Seconds()+0.999)))
	WriteError(w, r, ErrTooManyRequests)
}

// RateLimit is the general limit, per client address.
func RateLimit(l *Limiters, clientIP func(*http.Request) string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if !l.For(clientIP(r)).Allow() {
				WriteTooMany(w, r, l.RetryAfter())
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}
```

Three things in there are easy to get wrong:

1. **The map is shared by every request's goroutine**, so `For` locks it. Each `rate.Limiter` is safe to use from many goroutines by itself; it's only our map that needs the mutex. Lesson 2's rule: shared data needs a lock.
2. **The map would grow for ever.** Every new address adds a bucket. An attacker sending from a million addresses would fill our memory with buckets. So once a minute, `For` sweeps out buckets nobody has used for 30 minutes. A bucket left alone that long is full again anyway, so forgetting it loses nothing.
3. **`Retry-After`** tells a well-behaved client how many seconds to wait. Good clients slow down by themselves; the phone team's HTTP library reads it.

In `run`, the general limit allows a burst of 60, then one more a second, per address:

```go
general := httpx.NewLimiters(60, time.Second)
```

**The login limit is different**, in two ways. It should count only **failed** logins, so Ada isn't locked out by her own good ones. And it must key on two things: the address, and the **email** being tried. Attackers spread guesses across thousands of addresses, so a per-address limit alone gives them 5 guesses per address per account; a per-email limit caps the guesses on Ada's account, however many addresses they use.

In `internal/auth/handlers.go`, the `Handler` gets two `*httpx.Limiters` and the client-address function, and `login` becomes:

```go
func (h *Handler) login(w http.ResponseWriter, r *http.Request) error {
	in, err := httpx.Decode[Login](w, r)
	if err != nil {
		return err
	}
	byIP := h.loginByIP.For(h.clientIP(r))
	byEmail := h.loginByEmail.For(normalEmail(in.Email))
	if byIP.Tokens() < 1 || byEmail.Tokens() < 1 {
		return tooManyLogins(h.loginByEmail.RetryAfter())
	}

	s, err := h.svc.Login(r.Context(), in)
	if errors.Is(err, ErrWrongLogin) {
		byIP.Allow() // only failures use up a token
		byEmail.Allow()
	}
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, presentSession(s))
}
```

`Tokens()` looks into the bucket without taking anything. We take a token only when the password was wrong. With both limiters made by `httpx.NewLimiters(5, 3*time.Minute)`, that's 5 wrong tries straight away, then one more every 3 minutes: about 480 guesses a day on any one account. Against a 10-character password, that's nothing.

`tooManyLogins` returns an error, so it fits the handler pattern. The `Retry-After` header needs setting too; give `apperr.Error` a `RetryAfter time.Duration` field, and have `WriteError` set the header when it's there. Write both; the practice checks them.

(Returning 429 when the *email's* bucket is empty also means an attacker can lock Ada out of logging in, by failing on purpose. That's the trade every login limit makes. The 3-minute refill keeps the lockout short, and Ada still has her refresh token, so her phone stays logged in.)

**These buckets live in this app's memory.** Run two copies of the app and each counts separately, so the real limit is double; restart, and the counts reset. That's fine for now. In lesson 19, with Redis running, the limits move to a shared store.

## Step 4: who is the client, really?
<!-- bite: 1a2c7362-4640-4173-bd4d-9acf72552749 -->

Every limit above is keyed on "the client's address". Getting that right is harder than it looks.

`r.RemoteAddr` is the address of whatever opened the TCP connection to us, as `"ip:port"`. On your laptop, that's the client. In production, there's almost always a **reverse proxy** in front (nginx, a cloud load balancer), and then `RemoteAddr` is the **proxy**, for every request. Key the limits on that, and *everyone shares one bucket*: one busy minute locks out every customer.

The proxy writes the real address in the `X-Forwarded-For` header. But here's the trap: **the client can send `X-Forwarded-For` too.** If we believe the first address in it, an attacker sends a fresh fake one with every request, and gets a fresh bucket every time. The limits become useless.

The safe rule: each proxy **adds** the address it saw to the **end** of the list. So only the entries added by proxies *we* run can be trusted, and we know how many of those there are. `internal/httpx/clientip.go`:

```go
package httpx

import (
	"net"
	"net/http"
	"net/netip"
	"strings"
)

// ClientIP returns a function that finds the caller's address, trusting
// exactly `hops` proxies in front of us (0 on your laptop).
func ClientIP(hops int) func(*http.Request) string {
	return func(r *http.Request) string {
		ip := remoteIP(r)
		if hops > 0 {
			var all []string
			for _, h := range r.Header.Values("X-Forwarded-For") {
				for _, part := range strings.Split(h, ",") {
					all = append(all, strings.TrimSpace(part))
				}
			}
			if len(all) >= hops {
				ip = all[len(all)-hops]
			}
		}
		return limitKey(ip)
	}
}

func remoteIP(r *http.Request) string {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}

// limitKey groups IPv6 addresses by their /64, which usually means one household or phone.
func limitKey(ip string) string {
	addr, err := netip.ParseAddr(ip)
	if err != nil {
		return "unknown"
	}
	if addr.Is4() || addr.Is4In6() {
		return addr.Unmap().String()
	}
	prefix, _ := addr.Prefix(64)
	return prefix.String()
}
```

With one proxy (`hops` = 1), we take the **last** address in the list, the one our proxy added: the address it actually saw. Anything the client wrote is further to the left, and ignored. With two proxies, the second from the end, and so on.

**IPv6** needs one more thought. A single phone or home internet connection is usually given a whole block of IPv6 addresses (a "/64", which is 18 billion billion of them), and can pick a new one whenever it likes. Keying on the full address would give an attacker a fresh bucket per request, all from one phone. So we key IPv6 on the /64 block. `netip` is the modern standard-library package for addresses: small, fast values that can be compared and used as map keys.

`hops` comes from settings, because it depends on where the app runs:

```text
TRUSTED_PROXY_HOPS=0
```

Zero on your laptop. On a server behind one load balancer, 1. Get it wrong in the "too trusting" direction (2 when there's 1), and clients can fake their address again. Get it wrong in the other direction (0 when there's 1), and everyone shares the proxy's bucket. Count your proxies; it's a setting worth writing a comment next to.

## Step 5: size limits and timeouts
<!-- bite: 1dfe1d8f-23e6-479d-983b-93ecf6434b94 -->

Every limit is a promise about what the server will put up with. Write each one down on purpose, instead of accepting a default.

**Body size.** Lesson 6 capped JSON bodies at 1 MB. A dish or an order is a few hundred bytes, and a sign-up a little more, so tighten it. In `internal/httpx/json.go`:

```go
const maxBodyBytes = 64 << 10 // 64 KB
```

**Header size.** Go's server accepts up to 1 MB of headers by default. A real request's headers are a few kilobytes, even with a long token. In `run`'s `http.Server`:

```go
MaxHeaderBytes: 32 << 10, // 32 KB
```

**Time.** Lesson 1 already set the four timeouts, and they're worth reading again now, knowing what they stop:

```go
ReadHeaderTimeout: 5 * time.Second,   // slowloris: headers sent one byte at a time
ReadTimeout:       10 * time.Second,  // a body sent one byte at a time
WriteTimeout:      30 * time.Second,  // a client that reads our answer very slowly
IdleTimeout:       120 * time.Second, // kept-alive connections doing nothing
```

A proxy in front usually has its own timeouts too. Ours are the backstop. What none of these limit is how long **our** code takes: a slow database query holds a goroutine and a connection from the pool. That's a context deadline on each call, which is lesson 26.

## Step 6: dish photos, uploaded safely
<!-- bite: d5c9d9e6-ca0a-4d40-a880-8e5ad51ff6b3 -->

Mama wants a photo for each dish: `POST /v2/menu/{id}/photo`, a normal form upload with one file in a field called `photo`.

Uploads are where many apps get hurt. Every part of an upload is chosen by the person sending it: the file's name, the type it *claims* to be, its size, and what's actually inside. We trust none of it.

`migrations/009_dish_photos.sql`:

```sql
ALTER TABLE dishes ADD COLUMN photo text;
```

`internal/menu/photos.go`:

```go
package menu

import (
	"bytes"
	"crypto/rand"
	"errors"
	"fmt"
	"image"
	_ "image/jpeg" // these blank imports teach image.DecodeConfig each format
	_ "image/png"
	"io"
	"net/http"
	"os"
	"regexp"

	_ "golang.org/x/image/webp"

	"mamaput/internal/apperr"
)

const (
	maxPhotoBytes  = 2 << 20 // 2 MB
	maxPhotoPixels = 4000
)

var photoTypes = map[string]string{"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}

var (
	ErrUnsupportedImage = apperr.New(apperr.Invalid, "unsupported-image", "The photo must be a JPEG, PNG or WebP image.")
	ErrImageTooLarge    = apperr.New(apperr.Invalid, "image-too-large", "Photos can be at most 4000 pixels wide and high.")
	ErrPhotoRequired    = apperr.New(apperr.Invalid, "photo-required", "Send the image in a form field called 'photo'.")
	ErrFileTooLarge     = apperr.New(apperr.TooLarge, "file-too-large", "Photos can be at most 2 MB.")
)

// Photos stores dish photos inside one folder, and nowhere else.
type Photos struct {
	root *os.Root
}

func OpenPhotos(dir string) (*Photos, error) {
	if err := os.MkdirAll(dir, 0o750); err != nil {
		return nil, err
	}
	root, err := os.OpenRoot(dir)
	if err != nil {
		return nil, fmt.Errorf("open photos folder: %w", err)
	}
	return &Photos{root: root}, nil
}

// ReadUpload reads the one "photo" file from a multipart form, at most 2 MB.
func ReadUpload(w http.ResponseWriter, r *http.Request) ([]byte, error) {
	r.Body = http.MaxBytesReader(w, r.Body, maxPhotoBytes+64<<10) // the photo plus the form's own lines
	mr, err := r.MultipartReader()
	if err != nil {
		return nil, ErrPhotoRequired
	}
	part, err := mr.NextPart()
	if err != nil || part.FormName() != "photo" {
		return nil, ErrPhotoRequired
	}
	data, err := io.ReadAll(io.LimitReader(part, maxPhotoBytes+1))
	var tooBig *http.MaxBytesError
	if errors.As(err, &tooBig) || len(data) > maxPhotoBytes {
		return nil, ErrFileTooLarge
	}
	if err != nil {
		return nil, fmt.Errorf("read upload: %w", err)
	}
	return data, nil
}

// Save checks the bytes are really a small enough image, and writes them
// under a name we choose. It returns that name.
func (p *Photos) Save(data []byte) (string, error) {
	ext, ok := photoTypes[http.DetectContentType(data)]
	if !ok {
		return "", ErrUnsupportedImage
	}
	cfg, _, err := image.DecodeConfig(bytes.NewReader(data))
	if err != nil {
		return "", ErrUnsupportedImage
	}
	if cfg.Width > maxPhotoPixels || cfg.Height > maxPhotoPixels {
		return "", ErrImageTooLarge
	}

	name := rand.Text() + "." + ext
	f, err := p.root.OpenFile(name, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o640)
	if err != nil {
		return "", fmt.Errorf("create photo: %w", err)
	}
	if _, err := f.Write(data); err != nil {
		f.Close()
		return "", fmt.Errorf("write photo: %w", err)
	}
	return name, f.Close()
}

var photoName = regexp.MustCompile(`^[A-Z2-7]{26}\.(jpg|png|webp)$`)

// Serve sends one photo, by the name Save gave it.
func (p *Photos) Serve(w http.ResponseWriter, r *http.Request) {
	name := r.PathValue("name")
	if !photoName.MatchString(name) {
		http.NotFound(w, r)
		return
	}
	w.Header().Set("Cache-Control", "public, max-age=31536000, immutable")
	http.ServeFileFS(w, r, p.root.FS(), name)
}
```

`ErrFileTooLarge` uses a new kind, `apperr.TooLarge`. Add it to the kinds, and `apperr.TooLarge: http.StatusRequestEntityTooLarge` (413) to `statusFor`. While you're there, give lesson 6's JSON decoding the same treatment: when the error is an `*http.MaxBytesError`, return a `TooLarge` error (`body-too-large`) instead of the general 400, so a too-big JSON body is a 413 as well.

Every line there stops a real attack:

1. **`MaxBytesReader` and `LimitReader`.** No 2 GB "photos". We read the stream part by part with `MultipartReader`, rather than `r.ParseMultipartForm`, which would accept every field and spill big files to temporary files on disk before we'd looked at anything.
2. **Only the first part, and it must be `photo`.** No 500 files in one request.
3. **`http.DetectContentType` reads the magic bytes.** The client says `Content-Type: image/jpeg` and names it `jollof.jpg`. Both are just claims, and we never even read them. An HTML page renamed to `.jpg` starts with `<html>`, not `FF D8 FF`, and is refused. It's the standard library's own sniffer, the same one the server would use if you forgot to set a type.
4. **`image.DecodeConfig` reads only the image's header**, its width and height, without decoding the pixels. That catches files that *start* like a JPEG but aren't one, and it stops a **decompression bomb**: a 50 KB PNG that claims to be 100,000 by 100,000 pixels would need 40 GB of memory to open. We refuse it from its header, before anything tries.
5. **We choose the file name**, with `crypto/rand.Text()`, the same random text as lesson 7's request IDs. A client-chosen name like `../../cmd/api/main.go` could write *outside* the photos folder. A random name can't, and nobody can guess other photos' names either.
6. **`os.Root` makes escaping impossible anyway.** New in Go 1.24, `os.OpenRoot(dir)` gives a handle that can only reach files **inside** that folder. Ask it for `../anything`, or follow a symbolic link that points outside, and it refuses. Our names are already safe, so this is the second lock: if some later change lets a bad name through, it still can't escape.
7. **`O_EXCL`** means "fail if a file with this name already exists". Random names never collide in practice; if one ever did, we'd rather fail than overwrite a photo.
8. **The extension comes from the real type**, not from the upload.
9. **`Serve` checks the name against the exact shape `Save` makes**, before it touches the disk. And it uses `http.ServeFileFS` on the root, not `http.FileServer`, which would happily list every file in the folder if asked for the folder itself.

The handler and route, in the menu package:

```go
mux.Handle("POST "+p+"/menu/{id}/photo", staff(httpx.HandlerFunc(h.uploadPhoto)))
mux.HandleFunc("GET /photos/{name}", h.photos.Serve)
```

```go
func (h *Handler) uploadPhoto(w http.ResponseWriter, r *http.Request) error {
	id, err := httpx.PathID(r, "id")
	if err != nil {
		return err
	}
	data, err := ReadUpload(w, r)
	if err != nil {
		return err
	}
	name, err := h.photos.Save(data)
	if err != nil {
		return err
	}
	dish, err := h.svc.SetPhoto(r.Context(), id, name)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, h.version.Present(dish, viewFor(r)))
}
```

**The permission check comes before the upload is read.** `staff` (lesson 13's `RequirePermission(auth.MenuWrite)`) wraps the handler, so a customer is refused before the server reads a single byte of their file. Check who they are first, then accept their bytes.

`SetPhoto` is an `UPDATE dishes SET photo = $2 WHERE id = $1 RETURNING ...` in the store, and `Dish` gets a `Photo string`. v2's presenter sends `"photoUrl": "/photos/<name>"` when there is one (add it to the spec as an optional field). `menu.NewHandler` takes the `*Photos`, built in `run` with `menu.OpenPhotos(getenv("PHOTOS_DIR"))` (`PHOTOS_DIR=./uploads/photos` in `.env`, and `uploads/` in `.gitignore`).

The served photos get `SecurityHeaders` too, so `nosniff` tells the browser to treat each one exactly as the image type `ServeFileFS` says. `immutable` caching is safe because a photo's name never points at different bytes: a new photo is a new name.

Try it:

```bash
curl -s -X POST localhost:8080/v2/menu/1/photo -H "Authorization: Bearer $STAFF" \
  -F "photo=@jollof.jpg"
# {"data":{...,"photoUrl":"/photos/K7Q3...ZQ.jpg"}}

echo '<script>alert(1)</script>' > fake.jpg
curl -s -X POST localhost:8080/v2/menu/1/photo -H "Authorization: Bearer $STAFF" \
  -F "photo=@fake.jpg" | grep -o '"code":"[^"]*"'
# "code":"unsupported-image"
```

`-F "photo=@jollof.jpg"` makes `curl` send a form upload, with the file `jollof.jpg` in the field `photo`.

Two steps further, for later. Real systems **re-encode** every uploaded image (decode it fully and save a fresh copy), which throws away anything hidden inside it and strips the location data phones put in photos. And they store files in **object storage** (Amazon S3, Cloudflare R2, Google Cloud Storage), not on the server's own disk, so every copy of the app sees every photo. When we put the app in containers in lesson 28, the local disk stops being a safe place for anything that must last. `Photos` is the one type that would change.

## Step 7: the boring things that matter
<!-- bite: cce37a6d-8a92-419c-a316-9e0b20a360aa -->

1. **HTTPS everywhere.** Tokens and passwords travel in every request. In production, the proxy handles HTTPS, and `Strict-Transport-Security` keeps browsers on it.
2. **Never log secrets.** No `Authorization` headers, passwords or refresh tokens in logs. Our request logger only logs the method, path, status and time; keep it that way. Lesson 27 adds a `slog` setting that blanks out any field called `password` or `token`, in case someone logs one by accident.
3. **Check dependencies for known holes.** Run:

   ```bash
   go tool govulncheck ./...
   ```

   `govulncheck` is smarter than most tools of its kind: it checks whether your code actually **calls** the broken function, not only whether the package is in `go.mod`, so it rarely cries wolf. Most attacks on small companies use bugs that already have fixes. Lesson 29 runs it on every push.
4. **Commit `go.sum`.** It holds a checksum for every module version you use, so a build anywhere gets exactly the code you tested, and a module that changed after you first downloaded it fails the build instead of quietly running.
5. **Give each part the least power it needs.** The app's database user should not be allowed to drop tables. Lesson 28 does this with a separate user for migrations.

The full chain in `app.New`, outermost first:

```go
return httpx.Chain(httpx.MuxProblems(mux),
	httpx.RequestID,
	httpx.LogRequests(d.Logger),
	httpx.RecoverPanic,
	httpx.SecurityHeaders,
	httpx.CORS(d.CORS),
	httpx.RateLimit(d.GeneralLimit, d.ClientIP),
	auth.Authenticate(d.Tokens),
)
```

Read why each is where it is. Security headers go on **every** response, even errors and 429s, so they come early. CORS answers preflights before the rate limit, so a browser's "may I?" doesn't use up a token; and before `Authenticate`, because a preflight never carries a token. The rate limit comes before `Authenticate`, so a flood of bad tokens is stopped cheaply, before we spend time checking signatures.

## The Go in this lesson
<!-- bite: c8aa810b-1ef3-4976-b87a-61540e650343 -->

1. **Setting headers before `next.ServeHTTP`**: Middleware can only add headers before the handler writes its status. A handler that sets the same header later replaces the middleware's value.
2. **`w.Header().Add("Vary", ...)`** versus **`Set`**: `Add` appends another value, keeping the ones already there; `Set` replaces them all. `Vary` can be set by several middleware, so it uses `Add`.
3. **`rate.NewLimiter(rate.Every(per), burst)`**: A token bucket. `rate.Every(3*time.Minute)` turns "one every 3 minutes" into a rate per second. `Allow()` takes a token or says no; `Tokens()` looks without taking.
4. **A struct holding a mutex and a map**: `Limiters` is the lesson 2 pattern: lock, use the map, unlock with `defer`. A `*rate.Limiter` itself is already safe to share.
5. **`delete(l.buckets, k)` while ranging**: Removing keys from a map during `range` over it is allowed.
6. **`r.Header.Values("X-Forwarded-For")`**: All the values of a header that may appear more than once. `Get` would give only the first.
7. **`net.SplitHostPort`**: Splits `"203.0.113.7:51234"` into host and port, and handles IPv6's `"[2001:db8::1]:51234"` form correctly. Never split on `:` yourself.
8. **`netip.ParseAddr`**, **`addr.Unmap()`** and **`addr.Prefix(64)`**: The modern address type. `Unmap` turns an IPv4 address written in IPv6 form back into plain IPv4; `Prefix(64)` gives the /64 block an IPv6 address belongs to.
9. **Blank imports, `_ "image/png"`**: Import a package only for what it does when it loads. Each image package **registers** its format with `image` as it loads, so `image.DecodeConfig` can recognise it. Without the import, PNGs would be "unknown format".
10. **`r.MultipartReader()`** and **`part.FormName()`**: Reads a form upload as a stream of parts, one at a time, so nothing is accepted before you've looked at it.
11. **`io.LimitReader(part, n+1)`**: Reads at most `n+1` bytes. If you get `n+1`, it was too big. That's the standard trick for "read up to the limit and know if it went over".
12. **`http.DetectContentType(data)`**: The standard library's sniffer. It looks at up to the first 512 bytes and names the type.
13. **`os.OpenRoot(dir)`**, **`root.OpenFile`** and **`root.FS()`** (Go 1.24): A handle on a folder that can't be escaped with `..` or symbolic links. `FS()` gives an `fs.FS` of the same folder for serving.
14. **`os.O_WRONLY|os.O_CREATE|os.O_EXCL`** and **`0o640`**: Flags combined with `|`: write only, create, fail if it exists. `0o640` is the file's permissions written in octal: the owner can read and write, the group can read, everyone else nothing.
15. **`http.ServeFileFS(w, r, fsys, name)`** (Go 1.22): Sends one file from an `fs.FS`, with the right `Content-Type`, `Last-Modified` and range support.
16. **`go tool govulncheck ./...`**: Runs a tool listed in `go.mod`, like lesson 11's oapi-codegen.

## Your project so far
<!-- bite: 6ca4f782-5807-418c-a95c-baeed894706d -->

```text
mama-put/
├── .env                           ← CORS_ORIGINS, TRUSTED_PROXY_HOPS, PHOTOS_DIR
├── .env.example                   ← the same three, with safe examples
├── .gitignore                     ← uploads/
├── go.mod                         ← x/time, x/image; govulncheck as a tool
├── migrations/
│   └── 009_dish_photos.sql        ← NEW: dishes.photo
├── uploads/photos/                ← photos land here (never committed)
├── cmd/
│   └── api/main.go                ← limiters, ClientIP(hops), CORS policy, OpenPhotos, MaxHeaderBytes
└── internal/
    ├── apperr/
    │   └── apperr.go              ← TooLarge kind; RetryAfter on Error
    ├── app/
    │   └── app.go                 ← the full chain; /docs sets its own CSP
    ├── auth/
    │   └── handlers.go            ← login limited by address and by email, failures only
    ├── httpx/
    │   ├── security.go            ← NEW: SecurityHeaders
    │   ├── cors.go                ← NEW: CORS, answers preflights before the mux
    │   ├── ratelimit.go           ← NEW: Limiters (per-key buckets, swept), RateLimit, WriteTooMany
    │   ├── clientip.go            ← NEW: ClientIP(hops), IPv6 grouped by /64
    │   ├── errors.go              ← TooLarge → 413; Retry-After from the error
    │   └── json.go                ← bodies capped at 64 KB
    └── menu/
        ├── photos.go              ← NEW: ReadUpload, Save (sniff, dimensions, random name, os.Root), Serve
        ├── handlers.go            ← POST /v2/menu/{id}/photo, GET /photos/{name}
        ├── postgres.go            ← SetPhoto; photo column
        └── versions.go            ← v2 shows photoUrl
```

## Common mistakes
<!-- bite: 94cd1247-9b5a-4d14-9b68-318b60af6487 -->

1. **Thinking CORS protects the API.** It only stops browsers *reading* answers. Anything that isn't a browser ignores it.
2. **Echoing any `Origin` back.** That allows every website. Check it against the list.
3. **Forgetting preflights.** With Go's mux, an `OPTIONS` request gets 405 unless the CORS middleware answers it first.
4. **Rate-limiting on `RemoteAddr` behind a proxy.** Everyone shares one bucket. Count your proxies and use `ClientIP`.
5. **Trusting the first `X-Forwarded-For` address.** The client wrote it. Trust only the ones your proxies added, from the right.
6. **A map of buckets that's never cleaned.** Memory grows with every address that ever called. Sweep it.
7. **Keying IPv6 on the full address.** One phone has billions. Group by /64.
8. **Believing the upload's name or `Content-Type`.** Sniff the bytes; choose the name.
9. **Decoding a whole image to check it.** A decompression bomb takes all your memory. Check the dimensions with `DecodeConfig` first.
10. **`http.FileServer` on an upload folder.** It lists the folder's files. Serve one checked name at a time.
11. **Reading the upload before checking permission.** Put the guard on the route, so a refused caller's bytes are never read.
12. **Turning the security policy off for the whole API because one HTML page needs a looser one.** Loosen it on that page only.

## Check your understanding
<!-- bite: 490cd64e-f5f5-489d-89a1-2b7ee5f07a7d -->

1. A script on `evil.example` calls `GET /v2/orders` in Ada's browser, with no token. Our CORS doesn't list `evil.example`. Does the request reach our handler? What does the script see? What actually protects Ada's orders?
2. Our app runs behind one load balancer with `TRUSTED_PROXY_HOPS=0`. What goes wrong? And with `TRUSTED_PROXY_HOPS=2`?
3. Why does the login limiter only take a token when the password was wrong?
4. Someone uploads `menu.png`: a real, valid PNG of 300 bytes that says it's 60,000 by 60,000 pixels. Which line stops it, and what would happen without that line?
5. `Save` makes its own random names, so why use `os.Root` as well?
6. Why does `CORS` come before `RateLimit` in the chain, and why does `RateLimit` come before `Authenticate`?

<details>
<summary>Answers, after your attempt</summary>

1. Yes, it reaches the handler: CORS never stops a request arriving. With no token, `RequireUser` answers 401. Even if it had worked, the browser would hide the answer from the script, because there's no `Access-Control-Allow-Origin` for `evil.example`. But what really protects the orders is that the token is in a header the page can't add, and that `GET /v2/orders` needs a login and is scoped to the caller. CORS is a second wall for browsers, not the main one.
2. With 0, every request seems to come from the load balancer, so all customers share one bucket, and a busy minute gets everyone 429s. With 2, we take the second address from the right, which is one the **client** wrote, so an attacker can fake their address and get a fresh bucket each time.
3. So that Ada's own successful logins never count against her, and so the limit measures exactly what it's there to stop: wrong guesses.
4. The `cfg.Width > maxPhotoPixels` check, after `image.DecodeConfig` reads only the header. Without it, anything that later opens the image fully (a thumbnail maker, the re-encoding step) would need about 14 GB of memory for its pixels, and the server would crash or be killed.
5. Defence in depth. Today the names are safe because we make them. If a later change ever lets a client influence the name, or a symbolic link appears in the folder, `os.Root` still refuses to touch anything outside it. Two locks, so one mistake isn't a breach.
6. A browser's preflight carries no token and shouldn't cost the user a rate-limit token, so CORS answers it first. And checking a rate limit is a map lookup, far cheaper than checking a JWT's signature, so a flood of bad tokens is turned away before we spend effort on each one.

</details>

## Practice
<!-- bite: d93d4abe-4ecc-47f8-a209-597942b7fc32 -->

1. Finish the `Retry-After` work from step 3: a `RetryAfter time.Duration` field on `apperr.Error`, `WriteError` setting the header when it's there, and `tooManyLogins`. Check with `curl -i` after six wrong logins.
2. Write `TestClientIP` as a table test: no proxy; one proxy with a client-written fake address on the left; two proxies; an IPv6 address grouped into its /64; and a `RemoteAddr` with no port.
3. Write `TestCORS` with `httptest`: an allowed origin gets `Access-Control-Allow-Origin`; an unknown one doesn't; a preflight gets 204 and never reaches the mux; and every response has `Vary: Origin`.
4. Re-encode photos: decode JPEGs and PNGs fully with `image.Decode` (after the dimension check), and save a fresh copy with `jpeg.Encode` at quality 85. Compare the sizes before and after, and notice that a phone photo's location data is gone.
5. Add `DELETE /v2/menu/{id}/photo`, which clears the column and removes the file with `root.Remove(name)`.

**Done when** `curl -sI localhost:8080/v2/menu` shows the security headers; the kitchen dashboard's origin gets CORS headers and others don't; the seventh wrong login in a row gets 429 with `Retry-After`; a fake photo gets `unsupported-image`; `go tool govulncheck ./...` reports no vulnerabilities your code calls; and `make test` passes.

## Before moving on
<!-- bite: 840ab09b-2573-4176-bc7a-d06004351c69 -->

Mama Put API is now much harder to abuse. Browsers get the safe rules, other websites can't read our answers, guessing passwords is hopelessly slow, the real client address can't be faked, nothing too big or too slow gets in, and photos are checked down to their pixels and kept in a folder they can't escape.

One danger is left from the real world, and it's not an attacker at all. Ada taps "Pay" on a slow network. Nothing seems to happen, so she taps again. Or her phone retries by itself. Did she just order, and pay, twice? That's idempotency, the next lesson.

## Related
<!-- bite: b0cd39df-160b-49db-89f7-b7d0624c3734 -->

- [[backend/frameworks/net-http/15-idempotency|Next: Idempotency]]
- [[backend/frameworks/express/14-security|The same lesson in Express]] — helmet, cors, express-rate-limit and multer
- [[cybersecurity/index|Cybersecurity]] — the attacks behind each defence
- [[backend/frameworks/net-http/06-validation|Lesson 6]] — where the body limit started

## About this lesson
<!-- bite: cc5a92be-8b89-41b5-a3db-2ea51ec54b11 -->

**Level:** Intermediate → Advanced. Lesson 14 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (`os.Root`, `crypto/rand.Text`), with `golang.org/x/time/rate`, `golang.org/x/image/webp` and govulncheck. Covers hand-written security headers and CORS (including preflights before the mux), per-key token buckets with sweeping, failure-only login limits by address and by email, trusting a fixed number of proxies in `X-Forwarded-For`, IPv6 grouping, body and header limits, and safe uploads: streaming multipart, magic-byte sniffing, dimension checks against decompression bombs, random names and `os.Root`.
