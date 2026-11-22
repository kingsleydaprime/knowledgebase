---
id: dfcbe950-5574-4e0c-a32e-aba3c1191404
---

# Authentication

**Authentication is how your backend finds out *who* is making a request: the customer proves who they are once, by logging in, and from then on every request carries proof that it comes from them.** Every app you've ever logged into does this. You type your email and password once, and after that the app just *knows* it's you, on every screen, for days, until you log out or it asks you to log in again.

## Before you start
<!-- bite: 309e74cb-fd13-4e21-8682-8e0a36b58786 -->

You should have:

1. Finished [[backend/frameworks/net-http/11-api-docs|lesson 11]], so v1 and v2 run side by side on Postgres, with docs.
2. Met `context.Context` values in [[backend/frameworks/net-http/07-errors|lesson 7]], where the request ID and the logger ride in the context.

After this lesson you will be able to:

1. Store passwords safely with argon2id, so even a stolen database doesn't give away anyone's password.
2. Explain sessions and tokens, and choose between them.
3. Sign and check access tokens with golang-jwt, closing the holes each option exists for.
4. Build sign-up, log-in, refresh and log-out, with refresh tokens that rotate and catch thieves.
5. Put the logged-in user in the request's context, read it safely in any handler, and require a login on the routes that need one.

## Where we stopped
<!-- bite: f0512c31-a84f-4f0b-8f92-c6c9674ef2a5 -->

Lesson 11 ended by looking at our only lock: `X-Staff-Key: mama-secret`.

1. It's **one shared secret**. Every cook knows it. When a cook leaves, every other cook needs a new key.
2. It **never expires**. Anyone who sees it once, in a log or over a shoulder, has it for good.
3. **Customers have no accounts.** Anyone can place an order, and nothing records whose order it is.

From this lesson, every new order belongs to a customer, and the API knows which customer is calling. Who is *allowed* to do what ("only staff can change the menu", "you can only see your own orders") is the next lesson, authorization. First we need to know who's who.

## The kid version
<!-- bite: 83a0985a-48f1-45e7-84b3-6ee834af64c0 -->

When you first join Mama Put's regulars, you show your face and give your name (signing up). She writes you in her book. Next time, you show your face again and she checks the book (logging in).

But showing your face for every single plate would be slow. So once she recognises you, she gives you a **wristband** for the day. Every time you order, you just show the wristband. It's only good for a short while (it **expires**), so if you lose it, nobody can use it for long.

When it runs out, you can trade it for a fresh one without showing your face again, as long as you also hand in a special **card** she gave you. Each card can only be traded once, and you get a new card each time.

The wristband is an **access token**. The card is a **refresh token**.

**Where the picture stops working.** Mama can see if someone else is wearing your wristband. A server can't: whoever holds a valid token *is* you, as far as the server knows. That's why tokens expire quickly and must be kept secret.

## Terms used in this lesson
<!-- bite: 2219be0a-147f-40b2-b9a1-288f2f002ef6 -->

1. **Authentication**: This is also written **authn**. It's proving who you are. Logging in is authentication.
2. **Authorization**: This is also written **authz**. It's deciding what you're allowed to do, once we know who you are. That's lesson 13.
3. **Credential**: This is the thing you prove yourself with. Here, an email and a password.
4. **Password hash**: This is a scrambled version of a password, made by a one-way function. You can check a password against it, but you can't turn it back into the password. We store hashes, **never** passwords.
5. **Salt**: This is a random value mixed into each password before hashing, and stored next to the hash. It makes two people with the same password get different hashes.
6. **Session**: This is a record the *server* keeps saying "this browser belongs to Ada", with a random session ID that the browser sends back, usually in a cookie.
7. **Token**: This is a piece of text the *client* keeps and sends with every request, usually in the `Authorization: Bearer <token>` header.
8. **JWT**: This stands for **JSON Web Token**. It's a token that carries information (like "user 42, role customer, expires at 3pm") plus a signature, so the server can check it wasn't changed, without looking anything up.
9. **Claim**: This is one piece of information inside a JWT, like `sub` (who it's about) or `exp` (when it expires).
10. **Access token**: This is a short-lived token (ours lasts 15 minutes) sent with every request.
11. **Refresh token**: This is a long-lived, single-use token used only to get a new access token, so the customer doesn't have to log in every 15 minutes.
12. **Identity**: This is our name for "who is calling": a user ID and a role, worked out from the access token and kept in the request's context.

## What to install
<!-- bite: 11a3dc7a-cfa1-4609-bcc4-5cad1de0a76a -->

Two packages. `golang.org/x/crypto` is maintained by the Go team but kept outside the standard library; it has argon2. `golang-jwt` is the JWT library almost every Go project uses.

```bash
go get golang.org/x/crypto
go get github.com/golang-jwt/jwt/v5
```

And a long random secret for signing tokens. Any of these makes one:

```bash
openssl rand -base64 32
# or, with no openssl:
head -c 32 /dev/urandom | base64
```

Add it to `.env` (and a placeholder to `.env.example`):

```text
JWT_SECRET=<paste it here>
```

Anyone with this secret can make tokens for any user, including staff. Treat it like the database password: never in git, never in a log, different on every server.

## Step 1: never store passwords
<!-- bite: d7d50cd6-a194-43eb-a423-a0f212292db4 -->

Here's the rule everything else rests on: **if your database is stolen, nobody's password should come with it.** People reuse passwords. If Ada's Mama Put password is also her email password, a leak from us empties her bank account.

So we store a **hash**. And not just any hash: a *slow* one, made for passwords. Fast hashes like SHA-256 are built to run billions of times a second, which is exactly what an attacker guessing passwords wants. A password hash like **argon2id** is deliberately slow and memory-hungry, so each guess costs real time and real memory, and it mixes in a random salt, so a table of pre-computed hashes is useless.

Go's argon2 package gives us the raw function, `argon2.IDKey`, and nothing else: no salt, no storage format, no checking. We write those, once. `internal/auth/password.go`:

```go
package auth

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"errors"
	"fmt"
	"strings"

	"golang.org/x/crypto/argon2"
)

// Argon2 hashes passwords with argon2id. The settings are stored inside
// every hash, so they can be raised later without breaking old hashes.
type Argon2 struct {
	Memory  uint32 // in KiB
	Time    uint32 // passes over the memory
	Threads uint8
}

// DefaultArgon2 is OWASP's recommended minimum: 19 MiB, 2 passes, 1 thread.
var DefaultArgon2 = Argon2{Memory: 19 * 1024, Time: 2, Threads: 1}

const saltLen, keyLen = 16, 32

var errBadHash = errors.New("password hash is not in the expected format")

func (p Argon2) Hash(password string) (string, error) {
	salt := make([]byte, saltLen)
	rand.Read(salt) // never fails since Go 1.24; it crashes the program instead

	key := argon2.IDKey([]byte(password), salt, p.Time, p.Memory, p.Threads, keyLen)

	b64 := base64.RawStdEncoding
	return fmt.Sprintf("$argon2id$v=%d$m=%d,t=%d,p=%d$%s$%s",
		argon2.Version, p.Memory, p.Time, p.Threads,
		b64.EncodeToString(salt), b64.EncodeToString(key)), nil
}

func (Argon2) Verify(encoded, password string) (bool, error) {
	// "$argon2id$v=19$m=19456,t=2,p=1$<salt>$<key>" splits into 6 parts; the first is empty.
	parts := strings.Split(encoded, "$")
	if len(parts) != 6 || parts[1] != "argon2id" {
		return false, errBadHash
	}
	var version int
	if _, err := fmt.Sscanf(parts[2], "v=%d", &version); err != nil || version != argon2.Version {
		return false, errBadHash
	}
	var p Argon2
	if _, err := fmt.Sscanf(parts[3], "m=%d,t=%d,p=%d", &p.Memory, &p.Time, &p.Threads); err != nil {
		return false, errBadHash
	}
	b64 := base64.RawStdEncoding
	salt, err := b64.DecodeString(parts[4])
	if err != nil {
		return false, errBadHash
	}
	want, err := b64.DecodeString(parts[5])
	if err != nil {
		return false, errBadHash
	}

	got := argon2.IDKey([]byte(password), salt, p.Time, p.Memory, p.Threads, uint32(len(want)))
	return subtle.ConstantTimeCompare(got, want) == 1, nil
}
```

Read what `Hash` produces:

```text
$argon2id$v=19$m=19456,t=2,p=1$k3Jd0Vx8m1QZ2yYp4wHn9A$3q0Z...
```

That one line of text holds everything `Verify` needs: the algorithm, its version, the settings, the salt and the result. This is the standard way to write an argon2 hash (it's called the **PHC string format**), so other languages' libraries can check our hashes too, and if we ever raise the memory setting, old hashes still say what *they* were made with.

`Verify` takes the salt and settings out of the stored hash, hashes the password the customer just typed with exactly those, and compares the two results. Two details:

1. **`subtle.ConstantTimeCompare`**: An ordinary `==` on bytes stops at the first difference, so it answers slightly faster for a guess that's wrong early. That tiny timing difference can leak information. The constant-time compare always looks at every byte. You met it in lesson 3 for the staff key.
2. **It returns an error separately from `false`.** "Wrong password" is a normal answer. "This stored hash is broken" is a bug we want in the logs. Two outcomes, so two return values.

**Why OWASP's 19 MiB, when argon2's own paper suggests 64 MiB?** Because the memory is used **per login, at the same time**. Twenty customers logging in at once at 64 MiB each is 1.3 GB, which is the whole of a small server. 19 MiB is the recommended floor that still makes guessing very expensive. A bigger server can raise it, and because the settings live inside each hash, raising them breaks nothing. (Lesson 14 also rate-limits the login route, so nobody can make us hash all day.)

Try it in a scratch test, `internal/auth/password_test.go`:

```go
package auth

import "testing"

func TestArgon2(t *testing.T) {
	h := DefaultArgon2
	hash, err := h.Hash("jollof-is-life")
	if err != nil {
		t.Fatal(err)
	}
	t.Log(hash)

	if ok, _ := h.Verify(hash, "jollof-is-life"); !ok {
		t.Error("the right password was refused")
	}
	if ok, _ := h.Verify(hash, "jollof-is-lyf"); ok {
		t.Error("a wrong password was accepted")
	}
}
```

```bash
go test -v -run TestArgon2 ./internal/auth/
```

Run it twice. Predict: is the logged hash the same both times? It's different every time, because the salt is random. Yet `Verify` works for both, because each hash carries its own salt.

## Step 2: sessions or tokens?
<!-- bite: 97b9c5de-8e4b-4eea-8a7a-9608a5cd49e8 -->

Once Ada has logged in, how does the next request prove it's her? Two main ways.

**Sessions.** The server creates a record ("session `a8f3...` belongs to user 42"), stores it (in Postgres or Redis), and gives the browser the random ID in a cookie. Every request sends the cookie, and the server looks the session up.

1. Easy to end: delete the record and that login is over, immediately.
2. Needs a lookup on every request.
3. Fits websites best, because browsers send cookies automatically.

**Tokens (JWTs).** The server signs a small message ("user 42, customer, expires 15:00") and gives it to the client. Every request sends it in a header. The server checks the signature, with no lookup.

1. No lookup per request, and any service with the key can check it, which matters when we add a second service in lesson 25.
2. Fits phone apps and other programs best.
3. Hard to end early: a signed token stays valid until it expires, even if you change your mind.

Mama Put's main client is a **phone app**, and we'll soon have more than one service. So we use tokens, and we fix their weakness by making them **short-lived**: an access token lasts 15 minutes. To avoid logging in every 15 minutes, the app also gets a **refresh token**, which we *do* store, so we can cancel it. That pair (a short JWT plus a stored, cancellable refresh token) gives most of the benefits of both.

If you were building a website only, sessions in an `HttpOnly` cookie are often the simpler, better choice. In Go, the `alexedwards/scs` package does them well, with Postgres or Redis behind it. Neither choice is wrong. Choose for your clients.

## Step 3: the tables
<!-- bite: 284e5baa-ce85-4f88-8e45-3845b8d95752 -->

`migrations/006_create_users.sql`:

```sql
CREATE TABLE users (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email         text NOT NULL,
  name          text NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
  password_hash text NOT NULL,
  role          text NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'staff', 'admin')),
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX users_email_idx ON users (lower(email));
```

The unique index is on `lower(email)`, so `Ada@Example.com` and `ada@example.com` can't be two accounts.

`migrations/007_create_refresh_tokens.sql`:

```sql
CREATE TABLE refresh_tokens (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  token_hash  text NOT NULL UNIQUE,
  expires_at  timestamptz NOT NULL,
  used_at     timestamptz,
  revoked_at  timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX refresh_tokens_user_id_idx ON refresh_tokens (user_id);
```

`migrations/008_orders_belong_to_customers.sql`:

```sql
ALTER TABLE orders ADD COLUMN customer_id bigint REFERENCES users (id);
CREATE INDEX orders_customer_id_idx ON orders (customer_id);
```

`customer_id` can be empty (`NULL`), because the orders placed before this lesson have no customer, and, as you'll see in step 8, v1 clients still place orders without logging in.

Notice `refresh_tokens` stores a **hash** of each token too, not the token. If the table leaks, the tokens in it are useless. The index on `user_id` is for "revoke every token this user has", which step 6 needs.

```bash
make migrate
```

## Step 4: the auth package's types
<!-- bite: 52e7a5fc-7c59-49ae-980d-112a8d22bffd -->

Everything about accounts lives in a new feature package, `internal/auth`. `internal/auth/auth.go`:

```go
// Package auth is accounts, passwords and tokens: who is calling.
package auth

import (
	"time"

	"mamaput/internal/apperr"
)

type Role string

const (
	RoleCustomer Role = "customer"
	RoleStaff    Role = "staff"
	RoleAdmin    Role = "admin"
)

func (r Role) Valid() bool {
	return r == RoleCustomer || r == RoleStaff || r == RoleAdmin
}

type User struct {
	ID           int64
	Email        string
	Name         string
	PasswordHash string
	Role         Role
	CreatedAt    time.Time
}

// Identity is who is calling, as proved by their access token.
type Identity struct {
	UserID int64
	Role   Role
}

type NewUser struct {
	Email    string `json:"email" validate:"required,email,max=254"`
	Name     string `json:"name" validate:"required,min=1,max=80"`
	Password string `json:"password" validate:"required,min=10,max=128"`
}

type Login struct {
	Email    string `json:"email" validate:"required,max=254"`
	Password string `json:"password" validate:"required,max=128"`
}

type RefreshRequest struct {
	RefreshToken string `json:"refreshToken" validate:"required,min=20,max=200"`
}

var (
	ErrUserNotFound  = apperr.New(apperr.NotFound, "user-not-found", "There's no such account.")
	ErrEmailTaken    = apperr.New(apperr.Conflict, "email-taken", "An account with this email already exists. Try logging in.")
	ErrWrongLogin    = apperr.New(apperr.Unauthenticated, "wrong-email-or-password", "The email or password is wrong.")
	ErrLoginRequired = apperr.New(apperr.Unauthenticated, "login-required", "Please log in first.")
	ErrInvalidToken  = apperr.New(apperr.Unauthenticated, "invalid-token", "Your login has expired or is not valid. Please refresh or log in again.")
	ErrBadRefresh    = apperr.New(apperr.Unauthenticated, "invalid-refresh-token", "Please log in again.")
	ErrRefreshReused = apperr.New(apperr.Unauthenticated, "refresh-token-reused", "Please log in again.")
	errTokenNotFound = apperr.New(apperr.NotFound, "refresh-token-not-found", "No such refresh token.")
)
```

Three things to see:

1. **`User` has `PasswordHash` and no `json` tags.** It's a domain type, the lesson 10 rule. Nothing ever encodes a `User` straight into a response, so the hash can't leak by accident.
2. **`NewUser`, `Login` and `RefreshRequest` *do* have tags.** They're what the client sends, read with lesson 6's `httpx.Decode`. The auth routes are new in v2 and only exist in v2, so they have only one wire shape.
3. **The password has a maximum, 128, and no "must contain a symbol" rules.** Length beats complexity: `jollof-is-life-every-day` is far harder to guess than `P@ss1`. The maximum keeps requests small and predictable; nobody needs a 5,000-character password.

`Login` doesn't use the `email` check on purpose. If someone types a badly formed email at login, the honest answer is still "the email or password is wrong", not a validation error that teaches them our rules.

## Step 5: signing and checking access tokens
<!-- bite: 2e16bc79-ff7c-4f39-baf6-93abe2dbda11 -->

A JWT is three pieces of base64url joined by dots:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 . eyJyb2xlIjoiY3VzdG9tZXIiLCJzdWIiOiI0MiIs... . 8xQm3k...
          header                                    payload (the claims)                  signature
```

The **header** says which algorithm signed it (`{"alg":"HS256"}`). The **payload** holds the claims (`{"sub":"42","role":"customer","exp":1795...}`). The **signature** is made from the first two plus our secret key. Change one letter of the payload, like `"role":"admin"`, and the signature no longer matches.

Paste a token into any JWT decoder website and you'll see the payload in plain text. **A JWT is signed, not encrypted.** Never put anything secret in it. A user ID and a role are fine.

`internal/auth/tokens.go`:

```go
package auth

import (
	"errors"
	"strconv"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

const (
	issuer         = "mama-put-api"
	audience       = "mama-put-app"
	AccessTokenTTL = 15 * time.Minute
)

type claims struct {
	Role Role `json:"role"`
	jwt.RegisteredClaims
}

type Tokens struct {
	key []byte
	now func() time.Time
}

func NewTokens(secret string, now func() time.Time) (*Tokens, error) {
	if len(secret) < 32 {
		return nil, errors.New("JWT_SECRET must be at least 32 characters")
	}
	return &Tokens{key: []byte(secret), now: now}, nil
}

func (t *Tokens) Sign(id Identity) (string, error) {
	now := t.now()
	c := claims{
		Role: id.Role,
		RegisteredClaims: jwt.RegisteredClaims{
			Subject:   strconv.FormatInt(id.UserID, 10),
			Issuer:    issuer,
			Audience:  jwt.ClaimStrings{audience},
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(now.Add(AccessTokenTTL)),
		},
	}
	return jwt.NewWithClaims(jwt.SigningMethodHS256, c).SignedString(t.key)
}

func (t *Tokens) Verify(token string) (Identity, error) {
	var c claims
	_, err := jwt.ParseWithClaims(token, &c,
		func(*jwt.Token) (any, error) { return t.key, nil },
		jwt.WithValidMethods([]string{jwt.SigningMethodHS256.Alg()}),
		jwt.WithIssuer(issuer),
		jwt.WithAudience(audience),
		jwt.WithExpirationRequired(),
		jwt.WithTimeFunc(t.now),
		jwt.WithLeeway(30*time.Second),
	)
	if err != nil {
		return Identity{}, err
	}

	userID, err := strconv.ParseInt(c.Subject, 10, 64)
	if err != nil || userID <= 0 || !c.Role.Valid() {
		return Identity{}, errors.New("token claims are not in the expected shape")
	}
	return Identity{UserID: userID, Role: c.Role}, nil
}
```

`claims` **embeds** `jwt.RegisteredClaims`, the standard ones (`sub`, `iss`, `aud`, `exp`, `iat`), and adds our own `role`. Embedding puts the standard fields at the top level of the JSON, next to `role`, which is where the JWT rules want them.

Every option passed to `ParseWithClaims` closes a real hole:

1. **`WithValidMethods`**: Only accept the one algorithm we sign with. A token's header *says* which algorithm to check it with, and the attacker writes the header. Old libraries in several languages accepted `"alg": "none"` and skipped the check, or let a token signed with a public key be checked as if the key were an HS256 secret. Pinning the method makes the header's claim irrelevant.
2. **`WithIssuer` and `WithAudience`**: Only accept tokens *we* made *for this app*. When lesson 25 adds a second service with its own tokens, this stops one service's tokens working at another.
3. **`WithExpirationRequired`**: golang-jwt checks `exp` when it's there, but a token **without** an `exp` would otherwise be accepted for ever. This makes it required.
4. **`WithTimeFunc(t.now)`**: The library uses our clock, not `time.Now`, so tests can check "a token from 16 minutes ago is refused" without waiting 16 minutes. The lesson 5 clock again.
5. **`WithLeeway(30*time.Second)`**: Servers' clocks are never exactly the same. Thirty seconds of slack stops a token being refused because one machine's clock is a little ahead.

And then we still check the claims ourselves: the subject must be a positive number, the role must be one we know. The signature proves *we* made the token; our check proves it has the shape our code expects. Belt and braces.

The `func(*jwt.Token) (any, error)` is the **key function**. golang-jwt asks it for the key to check this token with. We have one key, so it always returns it. When you rotate keys one day, it'll look at the token's `kid` header to pick which one.

## Step 6: refresh tokens, and the auth service
<!-- bite: 019872e1-2b9a-4216-a43a-6d724cec4fe7 -->

A refresh token doesn't need to carry information. It just needs to be impossible to guess. So it's 32 random bytes, and we keep only its hash. `internal/auth/refresh.go`:

```go
package auth

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"time"
)

const RefreshTokenTTL = 30 * 24 * time.Hour

type RefreshToken struct {
	ID        int64
	UserID    int64
	ExpiresAt time.Time
	UsedAt    *time.Time
	RevokedAt *time.Time
}

func newRefreshToken() string {
	b := make([]byte, 32)
	rand.Read(b)
	return base64.RawURLEncoding.EncodeToString(b)
}

func hashToken(token string) string {
	sum := sha256.Sum256([]byte(token))
	return hex.EncodeToString(sum[:])
}
```

Wait, didn't step 1 say "never use a fast hash"? For **passwords**, yes, because people choose guessable passwords and an attacker can try millions. A refresh token is 32 *random* bytes: there are more possible tokens than atoms in the planet, so guessing is hopeless however fast the hash. A fast hash is right here, and it lets us find a token by its hash in one indexed lookup.

The service needs two stores. Declared where they're used, the lesson 5 way, in `internal/auth/service.go`:

```go
package auth

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"time"
)

type Users interface {
	Create(ctx context.Context, email, name, passwordHash string) (User, error)
	FindByEmail(ctx context.Context, email string) (User, error)
	Find(ctx context.Context, id int64) (User, error)
}

type RefreshTokens interface {
	Create(ctx context.Context, userID int64, tokenHash string, expiresAt time.Time) error
	FindByHash(ctx context.Context, tokenHash string) (RefreshToken, error)
	MarkUsed(ctx context.Context, id int64) (bool, error)
	Revoke(ctx context.Context, id int64) error
	RevokeAllForUser(ctx context.Context, userID int64) error
}

type Hasher interface {
	Hash(password string) (string, error)
	Verify(hash, password string) (bool, error)
}

// Session is what logging in gives the client.
type Session struct {
	AccessToken  string
	RefreshToken string
	ExpiresIn    time.Duration
}

type Service struct {
	users     Users
	refresh   RefreshTokens
	tokens    *Tokens
	hasher    Hasher
	dummyHash string
	now       func() time.Time
}

func NewService(users Users, refresh RefreshTokens, tokens *Tokens, hasher Hasher, now func() time.Time) (*Service, error) {
	dummy, err := hasher.Hash("not-a-real-password")
	if err != nil {
		return nil, fmt.Errorf("make dummy hash: %w", err)
	}
	return &Service{users: users, refresh: refresh, tokens: tokens, hasher: hasher, dummyHash: dummy, now: now}, nil
}

func normalEmail(email string) string {
	return strings.ToLower(strings.TrimSpace(email))
}

func (s *Service) issue(ctx context.Context, u User) (Session, error) {
	access, err := s.tokens.Sign(Identity{UserID: u.ID, Role: u.Role})
	if err != nil {
		return Session{}, fmt.Errorf("sign access token: %w", err)
	}
	refresh := newRefreshToken()
	if err := s.refresh.Create(ctx, u.ID, hashToken(refresh), s.now().Add(RefreshTokenTTL)); err != nil {
		return Session{}, err
	}
	return Session{AccessToken: access, RefreshToken: refresh, ExpiresIn: AccessTokenTTL}, nil
}

func (s *Service) Signup(ctx context.Context, in NewUser) (Session, error) {
	hash, err := s.hasher.Hash(in.Password)
	if err != nil {
		return Session{}, err
	}
	u, err := s.users.Create(ctx, normalEmail(in.Email), strings.TrimSpace(in.Name), hash)
	if err != nil {
		return Session{}, err // ErrEmailTaken comes from the store
	}
	return s.issue(ctx, u)
}

func (s *Service) Login(ctx context.Context, in Login) (Session, error) {
	u, err := s.users.FindByEmail(ctx, normalEmail(in.Email))
	if err != nil && !errors.Is(err, ErrUserNotFound) {
		return Session{}, err
	}
	found := err == nil

	hash := s.dummyHash
	if found {
		hash = u.PasswordHash
	}
	ok, err := s.hasher.Verify(hash, in.Password)
	if err != nil {
		return Session{}, err
	}
	if !found || !ok {
		return Session{}, ErrWrongLogin
	}
	return s.issue(ctx, u)
}

func (s *Service) Refresh(ctx context.Context, token string) (Session, error) {
	rt, err := s.refresh.FindByHash(ctx, hashToken(token))
	if errors.Is(err, errTokenNotFound) {
		return Session{}, ErrBadRefresh
	}
	if err != nil {
		return Session{}, err
	}
	if rt.RevokedAt != nil || s.now().After(rt.ExpiresAt) {
		return Session{}, ErrBadRefresh
	}

	first, err := s.refresh.MarkUsed(ctx, rt.ID)
	if err != nil {
		return Session{}, err
	}
	if !first {
		if err := s.refresh.RevokeAllForUser(ctx, rt.UserID); err != nil {
			return Session{}, err
		}
		return Session{}, ErrRefreshReused
	}

	u, err := s.users.Find(ctx, rt.UserID)
	if errors.Is(err, ErrUserNotFound) {
		return Session{}, ErrBadRefresh
	}
	if err != nil {
		return Session{}, err
	}
	return s.issue(ctx, u)
}

func (s *Service) Logout(ctx context.Context, token string) error {
	rt, err := s.refresh.FindByHash(ctx, hashToken(token))
	if errors.Is(err, errTokenNotFound) {
		return nil // already logged out, or never logged in: either way, done
	}
	if err != nil {
		return err
	}
	return s.refresh.Revoke(ctx, rt.ID)
}

func (s *Service) Me(ctx context.Context, id Identity) (User, error) {
	return s.users.Find(ctx, id.UserID)
}
```

Four careful decisions are hiding in there. Each one is a real attack being stopped.

**1. Login never says which part was wrong.** "No account with that email" tells an attacker which emails are customers, and then which ones to try passwords on. So both cases give the same answer: "The email or password is wrong."

**2. Login takes the same time either way.** If the email doesn't exist and we answered straight away, the reply would take 1 ms; a real account with a wrong password takes about 30 ms, because argon2 runs. An attacker can *time* the answers and learn which emails exist anyway. So when there's no user, we still run `Verify` against a **dummy hash**, made once when the service is built. Both paths do the same work.

**3. Refresh tokens are single-use, and they rotate.** Every refresh gives back a *new* refresh token and marks the old one used. So a stolen refresh token stops working the moment the real app uses it.

**4. Reuse means theft.** If a refresh token that has *already been used* comes back, two parties have it: the real app and a thief. We can't tell which is which, so we revoke **every** refresh token that user has. Both are logged out; the real customer logs in again with their password, and the thief can't. This is called **refresh token rotation with reuse detection**.

And `MarkUsed` is where that "first or not" is decided, safely. In `internal/auth/postgres.go`:

```go
func (s *PostgresRefreshTokens) MarkUsed(ctx context.Context, id int64) (bool, error) {
	tag, err := s.pool.Exec(ctx,
		"UPDATE refresh_tokens SET used_at = now() WHERE id = $1 AND used_at IS NULL", id)
	if err != nil {
		return false, fmt.Errorf("mark refresh token used: %w", err)
	}
	return tag.RowsAffected() == 1, nil
}
```

Recognise it? It's the last-plate trick from [[backend/frameworks/net-http/08-data-with-postgres|lesson 8]]: the check is inside the `UPDATE`. If two requests use the same refresh token at the same moment, Postgres lets one `UPDATE` match `used_at IS NULL`; the other finds it already set and changes no rows. Checking `rt.UsedAt` in Go first, then updating, would leave a gap for both to slip through.

The rest of `postgres.go` is ordinary pgx, like lesson 8's stores. The one new idea is in `Users.Create`:

```go
package auth

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

const uniqueViolation = "23505"

type PostgresUsers struct{ pool *pgxpool.Pool }

func NewPostgresUsers(pool *pgxpool.Pool) *PostgresUsers { return &PostgresUsers{pool: pool} }

const userColumns = "id, email, name, password_hash, role, created_at"

func scanUser(row pgx.Row) (User, error) {
	var u User
	err := row.Scan(&u.ID, &u.Email, &u.Name, &u.PasswordHash, (*string)(&u.Role), &u.CreatedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		return User{}, ErrUserNotFound
	}
	return u, err
}

func (s *PostgresUsers) Create(ctx context.Context, email, name, passwordHash string) (User, error) {
	u, err := scanUser(s.pool.QueryRow(ctx,
		"INSERT INTO users (email, name, password_hash) VALUES ($1, $2, $3) RETURNING "+userColumns,
		email, name, passwordHash))

	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) && pgErr.Code == uniqueViolation {
		return User{}, ErrEmailTaken
	}
	return u, err
}

func (s *PostgresUsers) FindByEmail(ctx context.Context, email string) (User, error) {
	return scanUser(s.pool.QueryRow(ctx,
		"SELECT "+userColumns+" FROM users WHERE lower(email) = lower($1)", email))
}

func (s *PostgresUsers) Find(ctx context.Context, id int64) (User, error) {
	return scanUser(s.pool.QueryRow(ctx, "SELECT "+userColumns+" FROM users WHERE id = $1", id))
}

type PostgresRefreshTokens struct{ pool *pgxpool.Pool }

func NewPostgresRefreshTokens(pool *pgxpool.Pool) *PostgresRefreshTokens {
	return &PostgresRefreshTokens{pool: pool}
}

func (s *PostgresRefreshTokens) Create(ctx context.Context, userID int64, tokenHash string, expiresAt time.Time) error {
	_, err := s.pool.Exec(ctx,
		"INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
		userID, tokenHash, expiresAt)
	if err != nil {
		return fmt.Errorf("save refresh token: %w", err)
	}
	return nil
}

func (s *PostgresRefreshTokens) FindByHash(ctx context.Context, tokenHash string) (RefreshToken, error) {
	var rt RefreshToken
	err := s.pool.QueryRow(ctx,
		"SELECT id, user_id, expires_at, used_at, revoked_at FROM refresh_tokens WHERE token_hash = $1",
		tokenHash).Scan(&rt.ID, &rt.UserID, &rt.ExpiresAt, &rt.UsedAt, &rt.RevokedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		return RefreshToken{}, errTokenNotFound
	}
	return rt, err
}

func (s *PostgresRefreshTokens) Revoke(ctx context.Context, id int64) error {
	_, err := s.pool.Exec(ctx,
		"UPDATE refresh_tokens SET revoked_at = now() WHERE id = $1 AND revoked_at IS NULL", id)
	return err
}

func (s *PostgresRefreshTokens) RevokeAllForUser(ctx context.Context, userID int64) error {
	_, err := s.pool.Exec(ctx,
		"UPDATE refresh_tokens SET revoked_at = now() WHERE user_id = $1 AND revoked_at IS NULL", userID)
	return err
}
```

**Why no "is this email taken?" check before the insert?** Because it can't be trusted. Two sign-ups with the same email at the same moment would both find it free, then both insert. The unique index is the only thing that really knows. So we just insert, and when Postgres refuses with error code `23505` (unique violation), we turn that into our own `ErrEmailTaken`. `pgconn.PgError` is pgx's type for an error that came from Postgres itself, with its code, the table and the constraint.

`UsedAt *time.Time` scans a `NULL` as `nil`. A pointer is Go's usual way to say "this column can be empty".

## Step 7: the user in the context
<!-- bite: a91e59b7-cdb0-4753-b07a-58803b054e7b -->

Now the part every request goes through. The access token arrives in a header; something must check it and leave the answer where any handler can find it. In Express, that's `req.user`. Go's request has no spare field to hang things on, and you can't add one. It has something better: the **context**, which you used in lesson 7 for the request ID and the logger.

`internal/auth/middleware.go`:

```go
package auth

import (
	"context"
	"net/http"
	"strings"

	"mamaput/internal/apperr"
	"mamaput/internal/httpx"
)

type identityKey struct{}

func WithIdentity(ctx context.Context, id Identity) context.Context {
	return context.WithValue(ctx, identityKey{}, id)
}

// IdentityFrom says who is calling, if anyone is logged in.
func IdentityFrom(ctx context.Context) (Identity, bool) {
	id, ok := ctx.Value(identityKey{}).(Identity)
	return id, ok
}

// Current is for handlers that need a logged-in user. It never returns a zero Identity.
func Current(ctx context.Context) (Identity, error) {
	id, ok := IdentityFrom(ctx)
	if !ok {
		return Identity{}, ErrLoginRequired
	}
	return id, nil
}

// Authenticate reads the access token, if there is one, and records who is calling.
// No header means "anonymous": the request carries on. A bad header or token is a 401.
func Authenticate(tokens *Tokens) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			header := r.Header.Get("Authorization")
			if header == "" {
				next.ServeHTTP(w, r)
				return
			}

			scheme, token, ok := strings.Cut(header, " ")
			if !ok || !strings.EqualFold(scheme, "Bearer") || token == "" {
				httpx.WriteError(w, r, apperr.New(apperr.Unauthenticated, "bad-authorization-header",
					"Send the header as: Authorization: Bearer <token>"))
				return
			}

			id, err := tokens.Verify(token)
			if err != nil {
				httpx.WriteError(w, r, ErrInvalidToken)
				return
			}
			httpx.LoggerFrom(r.Context()).Debug("authenticated", "user", id.UserID)
			next.ServeHTTP(w, r.WithContext(WithIdentity(r.Context(), id)))
		})
	}
}

// RequireUser goes on routes that need a logged-in user.
func RequireUser(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if _, ok := IdentityFrom(r.Context()); !ok {
			httpx.WriteError(w, r, ErrLoginRequired)
			return
		}
		next.ServeHTTP(w, r)
	})
}
```

Three pieces, three jobs.

1. **`Authenticate`** runs on every request. No header means "nobody is logged in, carry on": the menu doesn't need a login, so a missing token isn't an error. A header that's there but wrong *is* an error, because the client clearly meant to log in and something's broken, and they deserve to know.
2. **`RequireUser`** goes on the routes that need a login. You can see it in `Register`, so a reader of the routes knows which ones are locked.
3. **`Current`** is how a handler reads the user. It returns an error, not a zero `Identity`, if nobody's there.

Why both `RequireUser` *and* `Current`? Because people forget things. If someone adds a route and forgets `RequireUser`, a handler that used `IdentityFrom` and ignored the `ok` would carry on with `UserID: 0`. A handler that uses `Current` refuses instead. That's called **failing closed**: when a check is missing, the answer is "no", not "yes". The middleware is the visible lock; `Current` is the lock that still works when the visible one was forgotten.

**The typed key.** `identityKey struct{}` is a type with no fields, used only as the key. It's not exported, so no other package can make one, which means no other package can read or overwrite the identity by accident, or on purpose. And `IdentityFrom` is the only reader, so the `.(Identity)` type assertion is written once and every caller gets a proper `Identity`, not an `any`. That's Go's answer to Express's "add `user` to the `Request` type": you don't change the request's type; you give the context a typed door.

One more detail for 401s. The HTTP rules say a 401 must tell the client how to authenticate. In `internal/httpx/errors.go`, in `WriteError`, just before `w.WriteHeader(status)`:

```go
if appErr.Kind == apperr.Unauthenticated {
	w.Header().Set("WWW-Authenticate", `Bearer realm="mama-put"`)
}
```

`httpx` doesn't import `auth`, and mustn't: `auth` imports `httpx` (for `WriteError`), and Go refuses import cycles. The `WWW-Authenticate` rule only needs the error's kind, which lives in `apperr`, so it fits in `httpx` with no cycle.

## Step 8: the routes, and wiring
<!-- bite: 0e17cf32-11df-47ef-9cd7-648e1a677397 -->

`internal/auth/handlers.go`:

```go
package auth

import (
	"net/http"
	"strconv"
	"time"

	"mamaput/internal/httpx"
)

type sessionV2 struct {
	AccessToken  string `json:"accessToken"`
	RefreshToken string `json:"refreshToken"`
	ExpiresIn    int    `json:"expiresIn"` // seconds
}

func presentSession(s Session) sessionV2 {
	return sessionV2{AccessToken: s.AccessToken, RefreshToken: s.RefreshToken, ExpiresIn: int(s.ExpiresIn.Seconds())}
}

type meV2 struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
	Role      Role      `json:"role"`
	CreatedAt time.Time `json:"createdAt"`
}

type Handler struct{ svc *Service }

func NewHandler(svc *Service) *Handler { return &Handler{svc: svc} }

func (h *Handler) Register(mux *http.ServeMux) {
	mux.Handle("POST /v2/auth/signup", httpx.HandlerFunc(h.signup))
	mux.Handle("POST /v2/auth/login", httpx.HandlerFunc(h.login))
	mux.Handle("POST /v2/auth/refresh", httpx.HandlerFunc(h.refreshSession))
	mux.Handle("POST /v2/auth/logout", httpx.HandlerFunc(h.logout))
	mux.Handle("GET /v2/auth/me", RequireUser(httpx.HandlerFunc(h.me)))
}

func (h *Handler) signup(w http.ResponseWriter, r *http.Request) error {
	in, err := httpx.Decode[NewUser](w, r)
	if err != nil {
		return err
	}
	s, err := h.svc.Signup(r.Context(), in)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusCreated, presentSession(s))
}

func (h *Handler) login(w http.ResponseWriter, r *http.Request) error {
	in, err := httpx.Decode[Login](w, r)
	if err != nil {
		return err
	}
	s, err := h.svc.Login(r.Context(), in)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, presentSession(s))
}

func (h *Handler) refreshSession(w http.ResponseWriter, r *http.Request) error {
	in, err := httpx.Decode[RefreshRequest](w, r)
	if err != nil {
		return err
	}
	s, err := h.svc.Refresh(r.Context(), in.RefreshToken)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, presentSession(s))
}

func (h *Handler) logout(w http.ResponseWriter, r *http.Request) error {
	in, err := httpx.Decode[RefreshRequest](w, r)
	if err != nil {
		return err
	}
	if err := h.svc.Logout(r.Context(), in.RefreshToken); err != nil {
		return err
	}
	w.WriteHeader(http.StatusNoContent)
	return nil
}

func (h *Handler) me(w http.ResponseWriter, r *http.Request) error {
	who, err := Current(r.Context())
	if err != nil {
		return err
	}
	u, err := h.svc.Me(r.Context(), who)
	if err != nil {
		return err
	}
	return httpx.WriteData(w, http.StatusOK, meV2{
		ID: strconv.FormatInt(u.ID, 10), Email: u.Email, Name: u.Name, Role: u.Role, CreatedAt: u.CreatedAt,
	})
}
```

`/me` never sends `PasswordHash`. It can't by accident, because `meV2` has no field for it. Choosing the fields that go out, every time, is the lesson 10 habit paying off.

**Orders now belong to whoever places them.** In `internal/orders`, `Order` gets `CustomerID *int64` (a pointer, because the column can be `NULL`), the store's `orderColumns` gains `customer_id`, `scanOrder` scans it as `&o.CustomerID`, and `PlaceTakingPortions` takes the customer and inserts it:

```go
func (s *PostgresStore) PlaceTakingPortions(ctx context.Context, customerID *int64, dishID int64, quantity int) (Order, error) {
	// ... the same transaction as lesson 8, and the insert becomes:
	//   INSERT INTO orders (customer_id, dish_id, quantity, total_kobo) VALUES ($1, $2, $3, $4)
}
```

A `nil` `*int64` is sent to Postgres as `NULL`. pgx does that for any nil pointer.

`Service.Place(ctx, customerID *int64, in NewOrder)` passes it through. And the place handler reads who's calling:

```go
func (h *Handler) place(w http.ResponseWriter, r *http.Request) error {
	in, err := httpx.Decode[NewOrder](w, r)
	if err != nil {
		return err
	}
	var customer *int64
	if who, ok := auth.IdentityFrom(r.Context()); ok {
		customer = &who.UserID
	}
	order, err := h.svc.Place(r.Context(), customer, in)
	// ... the rest as before
}
```

Here `IdentityFrom` with its `ok` is right, not `Current`, because there are two versions with two different rules:

1. **v2 requires a login to order.** Its `POST /v2/orders` is wrapped in `RequireUser`, so by the time `place` runs, there's always a customer.
2. **v1 doesn't.** Requiring a login is a **breaking change**: every v1 app in customers' pockets would stop being able to order. v1 is frozen and on its way out (lesson 10), so it keeps taking orders with no customer until its sunset date. Those orders get a `NULL` `customer_id`, like the old ones.

So the orders `Register` takes one more guard, the way it already takes `staff`:

```go
func (h *Handler) Register(mux *http.ServeMux, staff, customer func(http.Handler) http.Handler) {
	p := h.prefix
	mux.Handle("POST "+p+"/orders", customer(httpx.HandlerFunc(h.place)))
	mux.Handle("GET "+p+"/orders/{id}", httpx.HandlerFunc(h.get))
	mux.Handle("GET "+p+"/orders", staff(httpx.HandlerFunc(h.list)))
	mux.Handle("PATCH "+p+"/orders/{id}/status", staff(httpx.HandlerFunc(h.setStatus)))
}
```

v2's presenter adds `"customerId"` (as a string, or left out when there's none). v1's doesn't change, because v1 is frozen.

In `internal/app/app.go`, `Deps` gains `Auth *auth.Service` and `Tokens *auth.Tokens`, and `New` becomes:

```go
func New(d Deps) http.Handler {
	staff := httpx.KitchenOnly(d.StaffKey)
	anyone := func(h http.Handler) http.Handler { return h }

	mux := http.NewServeMux()
	// ... "/", the docs and the specs, as before

	v1 := http.NewServeMux()
	menu.NewHandler(d.Menu, menu.V1, "/v1").Register(v1, staff)
	orders.NewHandler(d.Orders, orders.V1, "/v1").Register(v1, staff, anyone)
	mux.Handle("/v1/", httpx.Deprecated(d.V1Policy)(httpx.MuxProblems(v1)))

	menu.NewHandler(d.Menu, menu.V2, "/v2").Register(mux, staff)
	orders.NewHandler(d.Orders, orders.V2, "/v2").Register(mux, staff, auth.RequireUser)
	auth.NewHandler(d.Auth).Register(mux)

	return httpx.Chain(httpx.MuxProblems(mux),
		httpx.RequestID, httpx.LogRequests(d.Logger), httpx.RecoverPanic, auth.Authenticate(d.Tokens))
}
```

`anyone` is a middleware that does nothing: it hands back the handler it was given. It lets v1 and v2 share one `Register` with different rules.

`Authenticate` goes **last** in the chain, so it runs after the request ID, logging and panic recovery are in place: a 401 from a bad token still gets a request ID, is still logged, and a bug in token checking is still caught by `RecoverPanic`. Order is behaviour, as lesson 3 said.

And in `run`, in `cmd/api/main.go`, after the pool is open:

```go
tokens, err := auth.NewTokens(getenv("JWT_SECRET"), time.Now)
if err != nil {
	return err
}
authService, err := auth.NewService(
	auth.NewPostgresUsers(pool), auth.NewPostgresRefreshTokens(pool),
	tokens, auth.DefaultArgon2, time.Now)
if err != nil {
	return err
}
```

Then `Auth: authService` and `Tokens: tokens` in `app.Deps`. If `JWT_SECRET` is missing or short, the program refuses to start, with the reason. A server that starts with an empty secret would sign tokens anyone could forge; refusing to start is the safe failure.

## Trying it
<!-- bite: c621e743-1383-44f9-b556-a9849ed7c02d -->

```bash
make migrate
make run
```

In another terminal:

```bash
# Sign up
curl -s -X POST localhost:8080/v2/auth/signup -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","name":"Ada","password":"jollof-is-life"}'
# {"data":{"accessToken":"eyJhbGciOi...","refreshToken":"q3Zt...","expiresIn":900}}

TOKEN=eyJhbGciOi...     # paste your access token
REFRESH=q3Zt...         # and your refresh token

curl -s localhost:8080/v2/auth/me -H "Authorization: Bearer $TOKEN"
# {"data":{"id":"1","email":"ada@example.com","name":"Ada","role":"customer","createdAt":"..."}}

# Order, logged in
curl -s -X POST localhost:8080/v2/orders -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"dishId":"1","quantity":2}'
# ..."customerId":"1"...

# Order, not logged in: 401 login-required, with a WWW-Authenticate header
curl -si -X POST localhost:8080/v2/orders -H "Content-Type: application/json" \
  -d '{"dishId":"1","quantity":2}' | grep -E "^HTTP|^Www-Authenticate"
```

(Go writes header names in a standard capitalisation, so `WWW-Authenticate` comes out as `Www-Authenticate`. Header names don't care about case, so both are correct.)

Then try the attacks:

1. Change one character in the middle of `$TOKEN` and call `/me`. Predict the answer: 401 `invalid-token`.
2. Log in with a wrong password, then with an email that doesn't exist. Same answer both times, in about the same time. Put `time` in front of each `curl` to see.
3. Sign up again as `ADA@example.com`. Predict: 409 `email-taken`, because the index is on `lower(email)`.
4. Refresh:

```bash
curl -s -X POST localhost:8080/v2/auth/refresh -H "Content-Type: application/json" \
  -d "{\"refreshToken\":\"$REFRESH\"}"
```

It works, and gives you a new pair. Now run **exactly the same command again**, with the old refresh token. Predict: 401 `refresh-token-reused`, and now the *new* refresh token is dead too. Okay!!!!! That's a thief caught.

## The Go in this lesson
<!-- bite: 9fcc8d1e-5203-4af8-a48c-46347760d09a -->

1. **`golang.org/x/...`**: Packages maintained by the Go team outside the standard library. They're versioned like any module, which lets them change faster than the standard library can.
2. **`rand.Read(b)`** from `crypto/rand`: Fills a byte slice with secure random bytes. Since Go 1.24, it never returns an error; if the operating system can't give randomness, the program stops, because carrying on with weak randomness would be worse. Never use `math/rand` for anything secret.
3. **`fmt.Sscanf(s, "m=%d,t=%d,p=%d", &a, &b, &c)`**: The reverse of `Sprintf`: reads values out of text that follows a pattern, into the variables you point it at.
4. **`uint32`, `uint8`**: Unsigned (never negative) whole numbers of a fixed size. argon2's settings use them, so our struct does too. `uint32(len(want))` converts an `int` to one.
5. **`sha256.Sum256(b)`** and **`sum[:]`**: `Sum256` returns a fixed-size **array**, `[32]byte`, not a slice. `sum[:]` makes a slice that views the whole array, which is what `hex.EncodeToString` wants.
6. **Embedding `jwt.RegisteredClaims` in `claims`**: A field with a type but no name. Its fields and methods become `claims`'s own, so `claims` satisfies `jwt.Claims` without writing any methods, and the JSON fields appear at the top level.
7. **Functional options**: `jwt.WithIssuer(...)`, `jwt.WithLeeway(...)` are functions that return an option, passed as extra arguments. It's the common Go way to give a function many optional settings without a huge struct.
8. **`strings.Cut(header, " ")`**: Splits text at the first `" "` into before and after, and says whether it was found. Cleaner than `Split` when you only want two pieces.
9. **`strings.EqualFold(a, b)`**: Compares text ignoring upper and lower case. `Bearer` and `bearer` are the same scheme.
10. **`type identityKey struct{}`** as a context key: A private empty type, so no other package can make the same key. `context.WithValue` returns a **new** context; contexts are never changed in place.
11. **`ctx.Value(identityKey{}).(Identity)`** with `, ok`: A type assertion. `Value` returns `any`; `.(Identity)` says "this should be an `Identity`". The `ok` form gives `false` instead of crashing when it isn't.
12. **`r.WithContext(ctx)`**: Makes a copy of the request with a new context. The middleware passes the copy on; the original is untouched.
13. **`errors.As(err, &pgErr)`** with **`*pgconn.PgError`**: Finds an error of a particular type anywhere in the wrapped chain and puts it in `pgErr`, so you can read its `Code`. `errors.Is` asks "is it this exact error?"; `errors.As` asks "is it this *kind* of error, and if so, give it to me".
14. **`tag.RowsAffected()`**: `Exec` returns a **command tag**, Postgres's summary of what happened (`UPDATE 1`). `RowsAffected` is the number in it.
15. **`anyone := func(h http.Handler) http.Handler { return h }`**: A function value that matches the middleware shape and does nothing. Passing "no guard" is easier than writing two `Register` functions.

## Your project so far
<!-- bite: 75b01914-dc91-4527-afee-3d2d6c21253d -->

```text
mama-put/
├── .env                           ← now also JWT_SECRET
├── .env.example                   ← JWT_SECRET=change-me-to-32-random-characters
├── go.mod                         ← golang.org/x/crypto, golang-jwt/jwt/v5
├── migrations/
│   ├── 001 … 005
│   ├── 006_create_users.sql             ← NEW: users, roles, unique lower(email)
│   ├── 007_create_refresh_tokens.sql    ← NEW: hashed, expiring, single-use refresh tokens
│   └── 008_orders_belong_to_customers.sql ← NEW: orders.customer_id (NULL allowed)
├── openapi/
├── cmd/
│   ├── api/main.go                ← builds Tokens (refuses a short secret) and auth.Service
│   └── migrate/main.go
└── internal/
    ├── auth/                      ← NEW package: who is calling
    │   ├── auth.go                ← Role, User, Identity, NewUser, Login, RefreshRequest, errors
    │   ├── password.go            ← argon2id Hash and Verify, PHC string format
    │   ├── password_test.go       ← NEW: right password yes, wrong password no
    │   ├── tokens.go              ← sign and verify access tokens, every option pinned
    │   ├── refresh.go             ← random refresh tokens and their SHA-256 hashes
    │   ├── service.go             ← Signup, Login (dummy hash), Refresh (rotation, reuse), Logout, Me
    │   ├── postgres.go            ← users (23505 → email-taken), refresh tokens (MarkUsed is atomic)
    │   ├── middleware.go          ← Authenticate, RequireUser, IdentityFrom, Current
    │   └── handlers.go            ← /v2/auth/signup, login, refresh, logout, me
    ├── app/
    │   └── app.go                 ← Authenticate last in the chain; orders get a customer guard
    ├── httpx/
    │   └── errors.go              ← WWW-Authenticate on every 401
    ├── orders/
    │   ├── orders.go              ← Order.CustomerID *int64
    │   ├── postgres.go            ← stores customer_id
    │   ├── handlers.go            ← place reads IdentityFrom; Register takes a customer guard
    │   └── versions.go            ← v2 shows customerId; v1 unchanged
    └── ...                        (apiv2, apperr, db, listing, menu, money unchanged)
```

## Common mistakes
<!-- bite: ef42c71a-5574-45de-8de9-84e257fe031a -->

1. **Storing passwords, or fast hashes of them.** Use argon2id (or bcrypt). Never MD5, SHA-1 or plain SHA-256 for passwords.
2. **Comparing hashes with `==` or `bytes.Equal`.** Use `subtle.ConstantTimeCompare`.
3. **"No account with that email."** It tells attackers who your customers are. One message for both cases, and the same work.
4. **Secrets in JWTs.** Anyone can read them. IDs and roles only.
5. **Not pinning the algorithm.** Always pass `jwt.WithValidMethods`. The token's own header is written by whoever sent it.
6. **Forgetting `WithExpirationRequired`.** A token with no `exp` is otherwise valid for ever.
7. **A weak, shared or committed `JWT_SECRET`.** Anyone with it can sign in as anyone. Long, random, in `.env`, never in git, and the program refuses to start without it.
8. **Checking for a taken email with a `SELECT` first.** Two sign-ups at once both pass. Let the unique index decide, and map `23505`.
9. **Using `math/rand` for tokens or salts.** It's predictable. `crypto/rand` only.
10. **Reading the identity with `IdentityFrom` and ignoring `ok`.** Then a missing guard means user `0`. Use `Current`, which fails closed.
11. **Using a string as a context key.** Another package using the same string reads or overwrites your value. Use a private type.
12. **Making v1 require a login.** That breaks every old app. New rules go in new versions.

## Check your understanding
<!-- bite: 83537cce-6916-462f-ab83-fcf5a3668c55 -->

1. Why does Mama Put use argon2id for passwords but SHA-256 for refresh tokens?
2. A thief copies Ada's refresh token. Ada's app refreshes first. What happens when the thief tries to use it?
3. Someone decodes their access token, changes `"role":"customer"` to `"role":"staff"`, and sends it. What happens, and which line stops it?
4. Why does login run `Verify` against a dummy hash when there's no such user?
5. Two `POST /v2/auth/refresh` requests with the same token arrive in the same millisecond. Why can't both succeed?
6. Why does a handler use `auth.Current` instead of `IdentityFrom`, when `RequireUser` already checked?

<details>
<summary>Answers, after your attempt</summary>

1. Passwords are chosen by people and often guessable, so each guess must be made slow and expensive: argon2id. Refresh tokens are 32 random bytes, impossible to guess however fast the hash, so a fast hash is fine and lets us look them up quickly.
2. Ada's refresh marked the token used and gave her a new pair. The thief's attempt finds a used token, so we treat it as theft: every refresh token Ada has is revoked, and the thief gets 401 `refresh-token-reused`. Ada logs in again with her password; the thief can't.
3. The signature no longer matches the changed payload, so `jwt.ParseWithClaims` returns an error and `Authenticate` answers 401 `invalid-token`. Without our secret, nobody can make a valid signature for the changed payload.
4. So that "no such email" and "wrong password" do the same work and take the same time. Otherwise an attacker could time the answers and learn which emails have accounts.
5. Because `MarkUsed` is one `UPDATE ... WHERE used_at IS NULL`. Postgres lets one of them change the row; the other finds `used_at` already set, changes nothing, and gets `false`, so it's treated as reuse.
6. Because the check might be missing one day: a new route, a refactor, a copy-paste. `Current` refuses with 401 when there's no identity, so a forgotten guard fails closed instead of running as user `0`.

</details>

## Practice
<!-- bite: e0abba44-540a-496c-9629-871889a18b14 -->

1. Add `PATCH /v2/auth/me` to change your name, and `POST /v2/auth/change-password`, which needs the current password, and revokes all refresh tokens afterwards, so other phones are logged out. Add `POST /v2/auth/logout-everywhere` while you're there.
2. Replace `KitchenOnly`'s shared key with a check that the caller's role is `staff` or `admin`. Make yourself staff with `UPDATE users SET role = 'staff' WHERE email = 'ada@example.com';` in `psql`. Then remove `STAFF_KEY` from `.env` and `Deps`. (Lesson 13 turns this into a proper system; this is the first step.)
3. Update `openapi/v2.yaml`: a `bearerAuth` security scheme (`type: http`, `scheme: bearer`, `bearerFormat: JWT`), the auth routes, and `security` on `POST /v2/orders`. Regenerate, and add the auth routes to the contract test.
4. Write `TestTokens` in `internal/auth/tokens_test.go` using a fake clock: a token signed now is accepted; the same token checked 16 minutes later is refused; a token signed with a different secret is refused.
5. Add `NeedsRehash(hash string) bool` to `Argon2`, true when the hash's settings are lower than the current ones. In `Login`, after a successful check, re-hash the password and save it. This is how you raise argon2's settings on a live system: each customer's hash is upgraded the next time they log in.

**Done when** sign-up, login, `/me`, refresh, reuse detection and logout all behave as in "Trying it"; the staff key is gone; `make test` passes; and the Swagger page's "Authorize" button lets you paste a token and place an order from the browser.

## Before moving on
<!-- bite: 7c854c8a-7442-4ad0-b258-f57b2c04525f -->

Mama Put API now knows who's calling. Passwords are hashed with argon2id, access tokens are short and signed with every option pinned, refresh tokens rotate and catch thieves, and every handler can ask the context who's there, safely.

But knowing *who* someone is doesn't say what they *may do*. Right now, Ada is logged in, so she can call `GET /v2/orders/7`, which is Bayo's order. And after practice 2, any staff member can delete the whole menu, including the cook who only started yesterday. That's authorization, the next lesson.

## Related
<!-- bite: b04a61a4-0ee6-40ca-a2b0-772d71078946 -->

- [[backend/frameworks/net-http/13-authorization|Next: Authorization]]
- [[backend/05-auth/01-authentication-flows|Authentication Flows]] — the idea in any framework
- [[backend/05-auth/03-oauth-provider-integrations|OAuth Provider Integrations]] — "Log in with Google", built on the same pieces
- [[backend/frameworks/express/12-authentication|The same lesson in Express]] — argon2 and jose, and `req.user` by declaration merging
- [[cybersecurity/index|Cybersecurity]] — why these attacks work

## About this lesson
<!-- bite: 6591a556-3b52-4f0f-9fac-4051969c81ac -->

**Level:** Intermediate → Advanced. Lesson 12 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later (for `crypto/rand.Read` never failing), `golang.org/x/crypto/argon2`, golang-jwt v5 and pgx v5. Covers argon2id hashing in the PHC string format, sessions versus tokens, signing and verifying JWTs with every option pinned, refresh-token rotation with reuse detection, a dummy hash against timing attacks, mapping Postgres's unique violation, the identity in the context with a private key type, `Authenticate`, `RequireUser` and `Current`, and keeping v1 unbroken.
