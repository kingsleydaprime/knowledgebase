---
id: ab1362b5-0b08-47a1-a692-2143729b4aaf
---

# Production Config and Docker

**Getting a backend ready for production means making it predictable: every setting checked the moment the program starts, a way for machines to ask "are you alive, and can you take work?", a polite way to stop without dropping anyone's request, and the whole system packaged so it runs the same everywhere with one command.** Docker does the packaging: each program goes into a small image, and Docker Compose starts all of them, with their databases and helpers, together.

## Before you start
<!-- bite: 89507b59-314c-40e9-99c9-0086fb091300 -->

You should have finished [[backend/frameworks/net-http/27-observability|lesson 27]]. This lesson gathers up promises made all along the way: lesson 1's server timeouts, lesson 8's migrations, lesson 20's streams that need ending, lesson 22's `GracefulStop`, lesson 25's separate databases, and lesson 27's admin port.

After this lesson you will be able to:

1. Read every setting once into a typed `Config`, report every problem at once, and keep secrets out of logs.
2. Serve `/livez` and `/readyz`, and know which one a machine should ask when.
3. Stop a Go service politely: stop being ready, drain, finish running requests, end streams, then stop everything else, in order.
4. Give the app a database role that can change rows but never drop tables.
5. Build each program into a tiny Docker image with nothing in it but the program.
6. Run the whole system (API, worker, notifications, Postgres, two Redis, NATS, Caddy, Jaeger, Prometheus) with Docker Compose.

## What to install
<!-- bite: fa058fdc-1ff2-49ed-98df-b114b9e267d1 -->

**Docker Compose.** It comes with Docker Desktop; on Linux it's the `docker-compose-plugin` package from Docker's own repository. Check it's there:

```bash
docker compose version
```

You want version 2 or later (it prints `Docker Compose version v2...` or higher). Note it's `docker compose`, with a space: the old `docker-compose` program with a hyphen is retired.

Nothing new for Go. Everything in this lesson's code is standard library, plus the modules you already have.

## Where we stopped
<!-- bite: b157616f-a36e-438d-8a9d-befddb7a26ee -->

Count what it takes to run Mama Put on your laptop today:

1. Postgres, two Redis servers, NATS, Jaeger and Prometheus, each started with its own `docker run` and flags you have to remember.
2. `go run ./cmd/migrate`, then `./cmd/api`, `./cmd/worker` and `./cmd/notifications`, each in its own terminal, each with a dozen environment variables.
3. A typo in one of those variables (`DATABSE_URL`) and the program starts anyway, then fails on the first request, or worse, uses a default nobody meant.

And on a real server it gets worse. When you deploy a new version, the old one is killed: what happens to the order being placed at that instant? To the kitchen screens' streams? To the event notifications was halfway through?

## The kid version
<!-- bite: e550a92a-b8fe-401c-90e9-0186f0300c3b -->

Mama is opening a second stall, and her cousin will run it. Mama can't be there, so she packs everything into one box: the pots, the gas, the recipes, the price list. Her cousin opens the box anywhere and the stall works exactly the same.

Before opening each morning, the cousin checks the list taped inside the lid: gas? Yes. Rice? Yes. Change for the till? No: then don't open yet. That's checking the config, and the health check.

At closing time, she doesn't just walk away. She stops taking new customers, finishes the plates already being served, tells the people still waiting "we're closing, come back tomorrow", and only then turns off the gas. That's stopping politely.

**Where the picture stops working.** A stall closes once a day. Our programs are stopped and started every time we deploy, maybe several times a day, while customers are still ordering. So closing politely isn't a nicety: it's what decides whether every deploy drops a few orders.

## Terms used in this lesson
<!-- bite: bfb88733-7487-4472-ad49-af5827dcd54b -->

1. **Config**: This is every setting a program needs (addresses, URLs, limits, secrets), read from its environment when it starts.
2. **Secret**: This is a setting that grants access (passwords, keys, tokens), which must never be logged, printed or committed to git.
3. **Liveness**: This answers "is the process running at all?". If not, restart it.
4. **Readiness**: This answers "can it take work right now?". If not, send work elsewhere, but don't restart it.
5. **Graceful shutdown**: This is stopping in order: stop accepting new work, finish what's in progress, then exit.
6. **`SIGTERM`**: This is the signal Docker (and most systems) send a program to ask it to stop. If it hasn't stopped after a grace period, they send `SIGKILL`, which can't be caught.
7. **Image**: This is a packaged program and everything it needs to run, built from a `Dockerfile`. A **container** is one running copy of an image.
8. **Multi-stage build**: This is a `Dockerfile` that builds in one image (with the Go compiler) and copies only the result into a second, small image.
9. **Distroless**: This is a base image with no shell, no package manager and no tools: just what a program needs to run, and nothing an attacker could use.
10. **Docker Compose**: This is a tool that starts several containers together from one file, `compose.yaml`, with their networks, volumes and secrets.

## Step 1: config, checked once
<!-- bite: d05ce1cf-2a92-46a0-9d3e-97ed8132852a -->

Every program has been calling `getenv("SOMETHING")` wherever it needed something, since lesson 5 made `run(getenv, stdout)` the composition root. That was right for learning. For production, three things are wrong with it:

1. **Mistakes show up late.** A missing `PAYSTACK_SECRET_KEY` is only noticed when the first customer pays.
2. **Mistakes show up one at a time.** Fix one, restart, find the next.
3. **Secrets can be printed** by any code that logs what it was given.

So each program reads all its settings once, at the top of `run`, into a typed struct, and refuses to start if anything's wrong. `internal/config/config.go`:

```go
// Package config reads and checks every setting once, when a program starts.
package config

import (
	"errors"
	"fmt"
	"log/slog"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

// Reader collects every problem with the settings, so one start shows them all.
type Reader struct {
	getenv func(string) string
	errs   []error
}

func NewReader(getenv func(string) string) *Reader { return &Reader{getenv: getenv} }

func (r *Reader) fail(name, format string, args ...any) {
	r.errs = append(r.errs, fmt.Errorf("%s: "+format, append([]any{name}, args...)...))
}

// String is a required setting.
func (r *Reader) String(name string) string {
	v := strings.TrimSpace(r.getenv(name))
	if v == "" {
		r.fail(name, "is required")
	}
	return v
}

// Optional is a setting with a default.
func (r *Reader) Optional(name, def string) string {
	if v := strings.TrimSpace(r.getenv(name)); v != "" {
		return v
	}
	return def
}

// Secret reads NAME, or the file named by NAME_FILE (how Docker and most platforms hand over secrets).
func (r *Reader) Secret(name string) Secret {
	if path := r.getenv(name + "_FILE"); path != "" {
		b, err := os.ReadFile(path)
		if err != nil {
			r.fail(name+"_FILE", "can't read %s: %v", path, err)
			return ""
		}
		return Secret(strings.TrimSpace(string(b)))
	}
	v := r.getenv(name)
	if v == "" {
		r.fail(name, "is required (or set %s_FILE)", name)
	}
	return Secret(v)
}

func (r *Reader) Duration(name string, def time.Duration) time.Duration {
	v := r.getenv(name)
	if v == "" {
		return def
	}
	d, err := time.ParseDuration(v)
	if err != nil || d <= 0 {
		r.fail(name, "must be a duration like 30s or 5m, not %q", v)
	}
	return d
}

// Int, Float, URL and OneOf follow the same pattern: parse, check the range or the
// allowed values, and on any problem call r.fail with a message that says what's wanted.

// Err is every problem found, joined, or nil.
func (r *Reader) Err() error { return errors.Join(r.errs...) }

// Secret is a string that never prints itself.
type Secret string

func (s Secret) String() string               { return "[secret]" }
func (s Secret) GoString() string             { return "[secret]" }
func (s Secret) LogValue() slog.Value         { return slog.StringValue("[secret]") }
func (s Secret) MarshalText() ([]byte, error) { return []byte("[secret]"), nil }
func (s Secret) Reveal() string               { return string(s) }
```

And each program's settings, `internal/config/api.go`:

```go
// API is everything the API program needs. Built once in run, passed down; nothing else reads the environment.
type API struct {
	Env             string // development, test, production
	Addr            string
	AdminAddr       string
	GRPCAddr        string
	PublicURL       string
	DatabaseURL     Secret
	QueueRedisURL   Secret
	CacheRedisURL   Secret
	NATSURL         string
	JWTSecret       Secret
	PaystackSecret  Secret
	OTELEndpoint    string
	TraceSampling   float64
	ShutdownTimeout time.Duration
	DBMaxConns      int
}

func LoadAPI(getenv func(string) string) (API, error) {
	r := NewReader(getenv)
	c := API{
		Env:             r.OneOf("APP_ENV", "development", "development", "test", "production"),
		Addr:            r.Optional("ADDR", ":8080"),
		AdminAddr:       r.Optional("ADMIN_ADDR", ":9100"),
		GRPCAddr:        r.Optional("GRPC_ADDR", "127.0.0.1:50051"),
		PublicURL:       r.URL("PUBLIC_URL", "https", "http"),
		DatabaseURL:     r.Secret("DATABASE_URL"),
		QueueRedisURL:   r.Secret("QUEUE_REDIS_URL"),
		CacheRedisURL:   r.Secret("CACHE_REDIS_URL"),
		NATSURL:         r.Optional("NATS_URL", "nats://127.0.0.1:4222"),
		JWTSecret:       r.Secret("JWT_SECRET"),
		PaystackSecret:  r.Secret("PAYSTACK_SECRET_KEY"),
		OTELEndpoint:    r.Optional("OTEL_ENDPOINT", ""),
		TraceSampling:   r.Float("TRACE_SAMPLING", 1, 0, 1),
		ShutdownTimeout: r.Duration("SHUTDOWN_TIMEOUT", 20*time.Second),
		DBMaxConns:      r.Int("DB_MAX_CONNS", 10, 1, 100),
	}
	if c.Env == "production" {
		if len(c.JWTSecret) < 32 {
			r.fail("JWT_SECRET", "must be at least 32 characters in production")
		}
		if len(c.PublicURL) < 8 || c.PublicURL[:8] != "https://" {
			r.fail("PUBLIC_URL", "must be https:// in production")
		}
		if c.TraceSampling == 1 && getenv("TRACE_SAMPLING") == "" {
			c.TraceSampling = 0.1
		}
	}
	return c, r.Err()
}
```

(`config.Notifications` and `config.Worker` are the same shape, with their own fields.) What a start with a messy environment prints, from the test:

```text
APP_ENV: must be one of development, test, production, not "prod"
PUBLIC_URL: is not a URL
DATABASE_URL: is required (or set DATABASE_URL_FILE)
QUEUE_REDIS_URL: is required (or set QUEUE_REDIS_URL_FILE)
CACHE_REDIS_URL: is required (or set CACHE_REDIS_URL_FILE)
JWT_SECRET: is required (or set JWT_SECRET_FILE)
PAYSTACK_SECRET_KEY: is required (or set PAYSTACK_SECRET_KEY_FILE)
SHUTDOWN_TIMEOUT: must be a duration like 30s or 5m, not "20"
DB_MAX_CONNS: must be a whole number from 1 to 100, not "500"
```

Nine problems, one start. Look at what makes it work:

1. **The reader keeps going.** Each method records a problem and returns something, so `LoadAPI` reads every setting before it gives up. `errors.Join` turns the list into one error that prints as one problem per line (Go 1.20).
2. **Messages say what's wanted.** "must be a duration like 30s or 5m, not "20"" fixes itself; "invalid SHUTDOWN_TIMEOUT" sends you to the code.
3. **Production is stricter.** A short JWT secret is fine on a laptop and a disaster on the internet, so the check only bites when `APP_ENV=production`. The default trace sampling drops from 100% to 10% there too (lesson 27).
4. **`run` reads the environment, and nothing else does.** `cfg, err := config.LoadAPI(getenv)` is the first line of `run`; everything below gets values from `cfg`. Tests pass a map for `getenv`, as since lesson 5.

### Secrets that can't leak

`Secret` is a `string` underneath, so it costs nothing, but it has five methods that change how it behaves:

1. **`String()` and `GoString()`** make `fmt.Println(cfg.JWTSecret)`, `%v`, `%+v` and `%#v` all print `[secret]`.
2. **`LogValue()`** makes slog print `[secret]` (lesson 27's trick).
3. **`MarshalText()`** makes `encoding/json` write `"[secret]"`, so even a config dumped as JSON is safe.
4. **`Reveal()`** is the only way to get the real value, and it's a word you can search the code for. `pgxpool.New(ctx, cfg.DatabaseURL.Reveal())` is honest about what it's doing.

So the API can log its whole config at start-up, which is wonderful when something's misconfigured:

```go
logger.Info("starting", "config", cfg)
```

```json
{"msg":"starting","config":{"Env":"production","Addr":":8080","AdminAddr":":9100","GRPCAddr":"127.0.0.1:50051","PublicURL":"https://api.mamaput.ng","DatabaseURL":"[secret]","QueueRedisURL":"[secret]","CacheRedisURL":"[secret]","NATSURL":"nats://127.0.0.1:4222","JWTSecret":"[secret]","PaystackSecret":"[secret]","OTELEndpoint":"","TraceSampling":0.1,"ShutdownTimeout":20000000000,"DBMaxConns":10}}
```

(Database URLs are secrets because they contain the password.)

### `_FILE`: secrets as files

Environment variables are easy to leak: `docker inspect` shows them, crash reports copy them, child processes inherit them. Docker Compose, Kubernetes and most hosting platforms can instead put each secret in a **file** that only the container can read, usually under `/run/secrets/`. `Secret("JWT_SECRET")` reads `JWT_SECRET_FILE` first, if it's set, so the same program works both ways: a plain variable on your laptop, a file in production. (Official images like Postgres follow the same `_FILE` convention, which is where it comes from.)

## Step 2: health checks
<!-- bite: fe6da00c-06b7-4205-af74-0f8d0c5869cb -->

Machines will ask our programs two different questions, and they need two different answers. `internal/health/health.go`:

```go
// Package health answers "are you alive?" and "can you take work?", and stops a program politely.
package health

// Check is one thing a program needs in order to take work, like its database.
type Check func(ctx context.Context) error

// Handler serves GET /livez (the process is running) and GET /readyz (it can take work right now).
func Handler(ready *atomic.Bool, checks map[string]Check) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /livez", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("ok\n"))
	})
	mux.HandleFunc("GET /readyz", func(w http.ResponseWriter, r *http.Request) {
		if !ready.Load() {
			writeStatus(w, http.StatusServiceUnavailable, map[string]string{"status": "stopping"})
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), time.Second)
		defer cancel()
		var (
			mu     sync.Mutex
			wg     sync.WaitGroup
			failed = map[string]string{}
		)
		for name, check := range checks {
			wg.Add(1)
			go func() {
				defer wg.Done()
				if err := check(ctx); err != nil {
					mu.Lock()
					failed[name] = "unavailable" // the detail goes to the log, not to whoever asked
					mu.Unlock()
				}
			}()
		}
		wg.Wait()
		if len(failed) > 0 {
			writeStatus(w, http.StatusServiceUnavailable, failed)
			return
		}
		writeStatus(w, http.StatusOK, map[string]string{"status": "ready"})
	})
	return mux
}

func writeStatus(w http.ResponseWriter, code int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(body)
}
```

1. **`/livez` checks nothing but itself.** If the process can answer HTTP at all, it's alive. If it can't, Docker should restart it. It must **never** check the database: if Postgres is down for a minute, restarting every API container would only add to the trouble, and they'd all come back to the same down database.
2. **`/readyz` checks what's needed to do the job**: for the API, a Postgres `pool.Ping`, a Redis `PING` on the queue Redis, and NATS's `nc.Status() == nats.CONNECTED`. A proxy or orchestrator asks it to decide **where to send work**, not whether to restart. (Not the cache Redis: lesson 19 made the API work without it, so it isn't needed to be ready.)
3. **The checks run at the same time**, each with the same 1-second budget, so `/readyz` answers in at most about a second even if every dependency hangs.
4. **It says which check failed, but not how.** From the test, with NATS down: `503 {"nats":"unavailable"}`. The error itself goes to the log; the health endpoint might be asked by things we don't fully control.
5. **`ready` is an `atomic.Bool`**, which step 3 flips to `false` the moment shutdown begins, before anything else stops.
6. **Both live on the admin port** (lesson 27's `:9100`), beside `/metrics`, never on the public one.

### A health check with no tools

Docker can run a command inside a container to check its health. The usual command is `curl http://localhost:9100/livez`. But step 5's image has **no curl, no shell, nothing**: just our program. So the program checks itself. At the very top of each `main`:

```go
func main() {
	if len(os.Args) > 1 && os.Args[1] == "healthcheck" {
		os.Exit(healthcheck(os.Getenv("ADMIN_ADDR")))
	}
	// ... the normal start
}

// healthcheck asks this program's own admin server whether it's alive. Docker runs it inside the container.
func healthcheck(addr string) int {
	if addr == "" {
		addr = ":9100"
	}
	_, port, _ := net.SplitHostPort(addr)
	c := http.Client{Timeout: 2 * time.Second}
	res, err := c.Get("http://127.0.0.1:" + port + "/livez")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return 1
	}
	return 0
}
```

`/app healthcheck` starts a second copy of the same binary, which makes one HTTP request to the first and exits 0 (healthy) or 1 (not). The Go standard library has an HTTP client built in, so this costs a few lines and no extra file in the image.

## Step 3: stopping politely
<!-- bite: 5faf07f8-b59d-4604-bf4f-29de1b1d3a66 -->

When Docker stops a container (every deploy, every restart), it sends **`SIGTERM`**, waits a grace period, then sends **`SIGKILL`**, which ends the process instantly, mid-request. Our job is to finish properly inside the grace period.

First, `main` turns the signal into a cancelled context:

```go
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
defer stop()
if err := run(ctx, os.Getenv, os.Stdout); err != nil {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}
```

`signal.NotifyContext` gives a context that's cancelled when the program gets `SIGTERM` (from Docker) or `os.Interrupt` (Ctrl+C in your terminal). That context has been the `ctx` passed to `run` since lesson 5, so every goroutine already watching `ctx.Done()` (lesson 20's event listener, lesson 25's relay and consumer) starts stopping by itself.

Then the order matters. `health.Serve` runs the servers and stops them in the right order:

```go
// Server is an HTTP server and the listener it serves on.
type Server struct {
	Name string
	HTTP *http.Server
	Lis  net.Listener
}

type Options struct {
	Public     []Server // stopped first
	Admin      Server   // health and metrics: stopped last
	Ready      *atomic.Bool
	DrainDelay time.Duration // how long "not ready" is shown before we stop taking requests
	Timeout    time.Duration // how long running requests get to finish
	Stop       []func(ctx context.Context) error // other things to stop: gRPC, consumers, the tracer
}

// Serve runs every server until ctx is cancelled (or one fails), then stops them politely, in order.
func Serve(ctx context.Context, log *slog.Logger, o Options) error {
	g, gctx := errgroup.WithContext(ctx)
	for _, s := range append([]Server{o.Admin}, o.Public...) {
		g.Go(func() error {
			log.Info("listening", "server", s.Name, "addr", s.Lis.Addr().String())
			if err := s.HTTP.Serve(s.Lis); !errors.Is(err, http.ErrServerClosed) {
				return err
			}
			return nil
		})
	}
	o.Ready.Store(true)

	g.Go(func() error {
		<-gctx.Done()
		log.Info("stopping: no longer ready")
		o.Ready.Store(false)
		time.Sleep(o.DrainDelay) // load balancers see /readyz fail and send new requests elsewhere

		sctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), o.Timeout)
		defer cancel()
		var errs []error
		for _, s := range o.Public {
			if err := s.HTTP.Shutdown(sctx); err != nil {
				errs = append(errs, err) // the timeout passed with requests still running
				s.HTTP.Close()
			}
		}
		for _, stop := range o.Stop {
			errs = append(errs, stop(sctx))
		}
		errs = append(errs, o.Admin.HTTP.Shutdown(sctx))
		log.Info("stopped")
		return errors.Join(errs...)
	})
	return g.Wait()
}
```

Step by step, when `SIGTERM` arrives:

1. **Stop being ready.** `/readyz` starts answering 503 `stopping`. Nothing else changes yet: we're still serving.
2. **Wait a moment (`DrainDelay`, 5 seconds in production).** The proxy in front is still sending us requests; it only stops when it notices. That takes a health-check interval or a failed request. Shutting the listener at once would turn those requests into connection errors. So we keep answering normally for a few seconds while traffic moves away.
3. **`Shutdown` the public servers.** `http.Server.Shutdown` closes the listener (no new connections), closes idle connections, and **waits for running requests to finish**, up to the context's deadline. If the deadline passes first, `Close` cuts the rest off.
4. **Stop everything else**, in the order given: lesson 22's gRPC server, lesson 25's consumer, lesson 18's asynq worker, the tracer's last batch (lesson 27).
5. **Stop the admin server last**, so health checks and metrics keep answering until the very end.

From the test, with a 200 ms drain and a 2-second timeout:

```text
readyz: 503 Service Unavailable {"nats":"unavailable"}
during drain readyz: 503 Service Unavailable {"status":"stopping"}
slow request during drain: 200 OK done
stream ended after 250ms
Serve returned <nil> after 470ms
after: dial tcp 127.0.0.1:38125: connect: connection refused
```

A request that arrived during the drain was answered normally. Then nothing new was accepted.

Some Go details hold this together:

1. **`errgroup.WithContext`** (from `golang.org/x/sync`) runs each server in its own goroutine. If any of them fails (say the port is taken), `gctx` is cancelled, which starts the same orderly stop, and `g.Wait()` returns the first error. One goroutine per server, and they all live or die together.
2. **`http.ErrServerClosed`** is what `Serve` returns after a `Shutdown`: the normal ending, not an error.
3. **`context.WithoutCancel(ctx)`** for the shutdown deadline: `ctx` is already cancelled (that's why we're stopping), so a timeout made from it would be over before it began. Lesson 15's trick again.
4. **The listeners are made in `run`** with `net.Listen` and passed in. That's what lets a test use `127.0.0.1:0` (any free port) and find out which port it got.

### Streams, which never finish

`Shutdown` waits for running requests, and lesson 20's kitchen streams never finish by themselves. They'd hold the shutdown for the whole timeout, then be cut off. The standard library has a hook for exactly this. In `run`:

```go
publicSrv := &http.Server{Handler: handler /* ... lesson 1's timeouts */}
publicSrv.RegisterOnShutdown(hub.CloseAll)
```

`RegisterOnShutdown` runs a function the moment `Shutdown` begins. `hub.CloseAll` (a few lines in lesson 20's hub: lock, close every listener's channel, empty the map) ends every stream at once. Each stream's handler sees its channel closed and returns, the request finishes, and `Shutdown` stops waiting for it. The screens' `EventSource` reconnects in 3 seconds, to a server that's still running. In the test, the stream ended 250 ms after the signal: the drain delay, plus a moment.

### gRPC, which waits too

`GracefulStop` on the gRPC server waits for every call, including lesson 22's `WatchPortions` streams, with no timeout of its own. So it goes in `Stop` with one:

```go
func stopGRPC(srv *grpc.Server) func(context.Context) error {
	return func(ctx context.Context) error {
		done := make(chan struct{})
		go func() { srv.GracefulStop(); close(done) }()
		select {
		case <-done:
			return nil
		case <-ctx.Done():
			srv.Stop() // out of time: end the rest now
			return ctx.Err()
		}
	}
}
```

Polite while there's time, firm when there isn't.

### The grace period

Docker's default grace period is **10 seconds**. Our stop takes up to 5 seconds of drain plus up to 20 of shutdown timeout. So each Go service in Compose gets `stop_grace_period: 30s`, a little more than we need. If the grace period is shorter than the shutdown, `SIGKILL` arrives in the middle of it and all this care is wasted.

The worker and notifications use the same `health.Serve` (they have only the admin server, plus their consumers and relay in `Stop`), and the same grace period. A message being handled when notifications stops is either finished and acked during the drain, or left un-acked and redelivered to another copy after lesson 25's ack wait. Either way, nothing is lost.

## Step 4: a database user that can't drop tables
<!-- bite: 8a5b3be8-04e9-4cfa-9c40-49422e4e5a40 -->

Since lesson 8, the API has connected to Postgres as a user that owns everything and could `DROP TABLE orders`. A SQL injection we missed, a bug, or a stolen password would have the same power. The app only ever needs to read and write **rows**; changing the **schema** is migrations' job.

So we use two roles. `deploy/postgres-init.sh`, which the Postgres image runs once, when its data volume is first created:

```sh
#!/bin/sh
# Runs once, when the Postgres volume is first created. Makes the databases and the roles that use them.
set -eu

psql -v ON_ERROR_STOP=1 --username postgres \
  -v migrate_pw="$(cat /run/secrets/migrate_db_password)" \
  -v api_pw="$(cat /run/secrets/api_db_password)" \
  -v notifications_pw="$(cat /run/secrets/notifications_db_password)" <<'SQL'
-- The API's database: one role that owns the tables and runs migrations, one that the app uses.
CREATE ROLE mamaput_migrate LOGIN PASSWORD :'migrate_pw';
CREATE ROLE mamaput_app LOGIN PASSWORD :'api_pw';
CREATE DATABASE mamaput OWNER mamaput_migrate;
REVOKE ALL ON DATABASE mamaput FROM PUBLIC;
GRANT CONNECT ON DATABASE mamaput TO mamaput_app;

\connect mamaput
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO mamaput_app;
-- Every table and sequence mamaput_migrate creates from now on: read and write rows, nothing more.
ALTER DEFAULT PRIVILEGES FOR ROLE mamaput_migrate IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO mamaput_app;
ALTER DEFAULT PRIVILEGES FOR ROLE mamaput_migrate IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO mamaput_app;

-- The notifications service's own database, which nobody else can open.
\connect postgres
CREATE ROLE notifications LOGIN PASSWORD :'notifications_pw';
CREATE DATABASE mamaput_notifications OWNER notifications;
REVOKE ALL ON DATABASE mamaput_notifications FROM PUBLIC;
SQL
```

1. **`mamaput_migrate` owns the database** and runs `cmd/migrate`. It creates every table.
2. **`mamaput_app`** is what the API and the worker connect as. **`ALTER DEFAULT PRIVILEGES`** means every table the migrate role creates *in future* automatically gives the app role `SELECT, INSERT, UPDATE, DELETE`, and nothing else. No grant to remember in each migration. (`USAGE, SELECT ON SEQUENCES` is what `bigserial` IDs need.)
3. **`REVOKE CREATE ON SCHEMA public FROM PUBLIC`**: by default, anyone may create tables in `public`. Not any more.
4. **`REVOKE ALL ... FROM PUBLIC`** on each database: by default every role can connect to every database. Now the app role can't open notifications' database, and notifications can't open the API's (lesson 25's rule, enforced by Postgres).
5. **Passwords as psql variables** (`-v api_pw=...` and `:'api_pw'` in the SQL): psql quotes them correctly, so a password with a `'` in it can't break the SQL. The quoted `<<'SQL'` stops the shell touching anything inside.

I ran this script against a real Postgres and tried each role:

```text
mamaput_migrate: CREATE TABLE dishes ...                    → CREATE TABLE
mamaput_app:     INSERT INTO dishes ... RETURNING id        → INSERT 0 1
mamaput_app:     DROP TABLE dishes                          → ERROR:  must be owner of table dishes
mamaput_app:     CREATE TABLE x ...                         → ERROR:  permission denied for schema public
mamaput_app:     connect to mamaput_notifications           → User does not have CONNECT privilege.
notifications:   connect to mamaput                         → User does not have CONNECT privilege.
```

Exactly the powers each needs, and no more.

One catch: lesson 15's and lesson 18's clean-up jobs use `DELETE`, which the app role has. Lesson 8's migration runner keeps its own bookkeeping table, which it creates as the migrate role, so the app never needs to touch it.

## Step 5: the Dockerfile
<!-- bite: 11ffb246-24d3-4b48-8d9a-5652bece266c -->

One `Dockerfile` builds any of our programs, chosen with a build argument:

```dockerfile
# syntax=docker/dockerfile:1

# ---- build: compile one of the programs in cmd/ ----
FROM golang:1.26-alpine AS build
WORKDIR /src

# Dependencies first: this layer is reused until go.mod or go.sum change.
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download

COPY . .
ARG CMD=api
ARG VERSION=dev
RUN --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -ldflags="-s -w -X main.version=${VERSION}" -o /out/app ./cmd/${CMD}

# ---- run: just the program, on an image with nothing else in it ----
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/app /app
USER nonroot:nonroot
EXPOSE 8080 9100
ENTRYPOINT ["/app"]
```

Two stages:

1. **The build stage** has the Go compiler (`golang:1.26-alpine`, about 300 MB). It's thrown away afterwards.
2. **The run stage** gets one file: our program. `gcr.io/distroless/static-debian12:nonroot` contains CA certificates (so HTTPS to Paystack works), time zone data, a `/etc/passwd` with a `nonroot` user, and **nothing else**: no shell, no package manager, no `curl`. If someone breaks into the container, there are no tools to use.

The build line, flag by flag:

1. **`CGO_ENABLED=0`**: build pure Go, with no C libraries linked in, so the program runs on an image that has no C libraries. Every library we use is pure Go.
2. **`-trimpath`**: leave the build machine's folder names out of the binary, so builds are the same everywhere.
3. **`-ldflags="-s -w"`**: leave out the debugging symbol tables, which makes the binary about a third smaller. (Stack traces from panics still have function names and line numbers.)
4. **`-X main.version=${VERSION}`**: sets the string variable `version` in package `main` at build time. Each `main.go` has `var version = "dev"`, which lesson 27's logs and traces report. Lesson 29 passes the git commit.
5. **`./cmd/${CMD}`**: `--build-arg CMD=notifications` builds notifications; the default builds the API.

And the speed tricks:

1. **`COPY go.mod go.sum` before `COPY .`**, with `go mod download` in between. Docker reuses a step if nothing it depends on changed, so downloading modules is skipped until the dependencies change, not every time you change a line of code.
2. **`--mount=type=cache`** keeps Go's module and build caches between builds, so rebuilding after a small change takes seconds.

A `.dockerignore` keeps things out of the build that don't belong:

```text
.git
**/*_test.go
*.md
.env*
*.pem
secrets/
```

`*.pem` and `secrets/` matter most: lesson 26's private keys must never be copied into an image, where anyone who can pull it can read them.

Build and look:

```bash
docker build --build-arg CMD=api --build-arg VERSION=dev -t mamaput-api:dev .
docker images mamaput-api:dev
```

The test image I built this way was **9.81 MB**. The whole program, with everything it needs to run. (If Docker says "No output specified with docker-container driver", your builder is the newer `buildx` one; add `--load` to put the image into Docker's image list.)

**Time zones.** Lesson 4's `time.LoadLocation("Africa/Lagos")` needs time zone data. Distroless has it, and lesson 4 also imported `time/tzdata`, which embeds a copy in the binary (about 450 KB), so it works even on an empty `scratch` image. Belt and braces, for the one thing (shop hours, Lagos days for lesson 24's cap) that would silently go wrong without it.

**No `HEALTHCHECK` line.** You might expect one in the Dockerfile. I added one while testing, and two things went wrong. Newer Docker builders write images in the standard OCI format, which has no place for a health check, so the line was quietly dropped. And the short form (`HEALTHCHECK CMD /app healthcheck`) runs through `/bin/sh`, which distroless doesn't have, so the check failed every time. So health checks go in `compose.yaml` (step 6), in the list form that runs the program directly. There, I checked, the container goes `healthy`.

## Step 6: the whole system in Compose
<!-- bite: 38d561e8-8550-4828-9611-e36eb622be64 -->

`compose.yaml`, at the root of the repository:

```yaml
name: mama-put

x-go-service: &go-service
  restart: unless-stopped
  stop_grace_period: 30s
  read_only: true
  security_opt: ["no-new-privileges:true"]
  healthcheck:
    test: ["CMD", "/app", "healthcheck"]
    interval: 10s
    timeout: 3s
    retries: 3
    start_period: 10s
  networks: [backend, edge] # backend: the data stores; edge: the internet (Paystack, email, SMS)

services:
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./deploy/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
    depends_on:
      api: { condition: service_healthy }
    networks: [edge]

  migrate:
    image: ${IMAGE_PREFIX:-mamaput}-migrate:${VERSION:-dev}
    build: { context: ., args: { CMD: migrate, VERSION: "${VERSION:-dev}" } }
    environment:
      DATABASE_URL_FILE: /run/secrets/migrate_database_url
    secrets: [migrate_database_url]
    depends_on:
      postgres: { condition: service_healthy }
    restart: "no"
    networks: [backend]

  api:
    <<: *go-service
    image: ${IMAGE_PREFIX:-mamaput}-api:${VERSION:-dev}
    build: { context: ., args: { CMD: api, VERSION: "${VERSION:-dev}" } }
    env_file: [deploy/api.env]
    environment:
      DATABASE_URL_FILE: /run/secrets/api_database_url
      JWT_SECRET_FILE: /run/secrets/jwt_secret
      PAYSTACK_SECRET_KEY_FILE: /run/secrets/paystack_secret_key
    secrets: [api_database_url, jwt_secret, paystack_secret_key]
    deploy: { replicas: 2 }
    depends_on:
      migrate: { condition: service_completed_successfully }
      redis-queue: { condition: service_healthy }
      redis-cache: { condition: service_started }
      nats: { condition: service_healthy }

  worker:
    <<: *go-service
    image: ${IMAGE_PREFIX:-mamaput}-worker:${VERSION:-dev}
    build: { context: ., args: { CMD: worker, VERSION: "${VERSION:-dev}" } }
    env_file: [deploy/api.env]
    environment:
      ADMIN_ADDR: ":9101"
      DATABASE_URL_FILE: /run/secrets/api_database_url
      PAYSTACK_SECRET_KEY_FILE: /run/secrets/paystack_secret_key
    secrets: [api_database_url, paystack_secret_key]
    depends_on:
      migrate: { condition: service_completed_successfully }
      redis-queue: { condition: service_healthy }
      nats: { condition: service_healthy }

  notifications:
    <<: *go-service
    image: ${IMAGE_PREFIX:-mamaput}-notifications:${VERSION:-dev}
    build: { context: ., args: { CMD: notifications, VERSION: "${VERSION:-dev}" } }
    env_file: [deploy/notifications.env]
    environment:
      ADMIN_ADDR: ":9102"
      NOTIFICATIONS_DATABASE_URL_FILE: /run/secrets/notifications_database_url
      NOTIFICATIONS_PRIVATE_KEY_FILE: /run/secrets/notifications_private_key
    secrets: [notifications_database_url, notifications_private_key]
    depends_on:
      postgres: { condition: service_healthy }
      nats: { condition: service_healthy }
      api: { condition: service_healthy }

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    secrets: [postgres_password, migrate_db_password, api_db_password, notifications_db_password]
    volumes:
      - pg-data:/var/lib/postgresql/data
      - ./deploy/postgres-init.sh:/docker-entrypoint-initdb.d/10-init.sh:ro
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      retries: 10
    networks: [backend]

  redis-queue:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes", "--maxmemory-policy", "noeviction"]
    volumes: [redis-queue-data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
    networks: [backend]

  redis-cache:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--save", "", "--appendonly", "no", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru"]
    networks: [backend]

  nats:
    image: nats:2-alpine
    restart: unless-stopped
    command: ["-js", "-sd", "/data", "-m", "8222"]
    volumes: [nats-data:/data]
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8222/healthz?js-enabled-only=true"]
      interval: 5s
    networks: [backend]

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports: ["127.0.0.1:16686:16686"]
    networks: [backend, edge] # edge only so its page can be published, on 127.0.0.1

  prometheus:
    image: prom/prometheus:latest
    ports: ["127.0.0.1:9090:9090"]
    volumes:
      - ./deploy/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./deploy/alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus-data:/prometheus
    networks: [backend, edge]

networks:
  edge: {}
  backend: { internal: true } # no way in or out except through other containers

volumes:
  pg-data: {}
  redis-queue-data: {}
  nats-data: {}
  prometheus-data: {}
  caddy-data: {}

secrets:
  postgres_password: { file: ./secrets/postgres_password }
  migrate_db_password: { file: ./secrets/migrate_db_password }
  api_db_password: { file: ./secrets/api_db_password }
  notifications_db_password: { file: ./secrets/notifications_db_password }
  migrate_database_url: { file: ./secrets/migrate_database_url }
  api_database_url: { file: ./secrets/api_database_url }
  notifications_database_url: { file: ./secrets/notifications_database_url }
  jwt_secret: { file: ./secrets/jwt_secret }
  paystack_secret_key: { file: ./secrets/paystack_secret_key }
  notifications_private_key: { file: ./secrets/notifications_private_key }
```

`docker compose config --quiet` checks a file like this without starting anything; this one passes. Reading it in parts:

**`x-go-service` and `<<: *go-service`.** Anything starting `x-` is ignored by Compose, so it's a place to keep shared settings. `&go-service` names that block, and `<<: *go-service` pastes it into each Go service. That's YAML's own feature (anchors and merge keys), so the four lines of health check and the security settings are written once.

**Every Go service gets:**

1. **`healthcheck`** in the list form, `["CMD", "/app", "healthcheck"]`, which runs our program directly, no shell needed (step 5).
2. **`stop_grace_period: 30s`** for step 3's polite stop.
3. **`read_only: true`**: the container's files can't be changed. Our programs write nothing to disk (logs go to stdout, data to Postgres), so this costs nothing and stops an attacker from saving anything.
4. **`no-new-privileges`**: a process inside can never gain more rights than it started with.

**Order, with `depends_on` conditions.** `migrate` waits until Postgres is `service_healthy`; the API waits until `migrate` is `service_completed_successfully`, so the API never starts against an old schema. Notifications waits for the API to be healthy, since it calls it. And Caddy waits for the API, so the first visitor doesn't get a 502.

**Migrations as their own container.** `migrate` runs `cmd/migrate` as the owner role, then exits; `restart: "no"` means it isn't restarted when it finishes. The API never runs migrations itself, so two API copies starting together can't race to change the schema, and the API's role doesn't need the power to.

**Two networks.** `backend` is `internal: true`: containers on it can talk to each other, but nothing on it can reach the internet, and nothing outside can reach it. Postgres, both Redis servers and NATS live **only** there. `edge` is ordinary: Caddy is on it to receive visitors, and the Go services are on it too, because the API must reach Paystack and notifications must reach email and SMS providers. Prometheus and Jaeger join `edge` only so their pages can be published, and only on `127.0.0.1`, so they're reachable from the server itself (through an SSH tunnel, lesson 29) and nowhere else.

**Secrets.** Each file in `./secrets/` becomes `/run/secrets/<name>` inside only the containers that list it. The API never sees notifications' private key; notifications never sees Paystack's. The `secrets/` folder is in `.gitignore` and `.dockerignore`; lesson 29 shows how the server gets its copies. Plain settings that aren't secret (`APP_ENV=production`, `PUBLIC_URL`, `NATS_URL=nats://nats:4222`, and so on) go in `deploy/api.env` and `deploy/notifications.env`, which are committed.

**Inside Compose, services find each other by name.** `postgres:5432`, `redis-queue:6379`, `nats:4222`, `api:50051` for gRPC. So `GRPC_ADDR` becomes `:50051` in `api.env` (listening on every interface of the container, which is fine now that the `backend` network is private), and notifications' `API_GRPC_ADDR` is `api:50051`.

**Two copies of the API** (`deploy: { replicas: 2 }`). Everything since lesson 19 was built for this: shared rate limits in Redis, stateless MCP, Redis pub/sub for the kitchen, `SKIP LOCKED` everywhere. One API copy can be replaced while the other serves.

**The two Redis servers** are lesson 19's: the queue one keeps everything on disk and never evicts; the cache one keeps nothing on disk and evicts the least recently used keys when it reaches 128 MB.

### Caddy, in front

`deploy/Caddyfile`:

```text
{
	email ops@mamaput.ng
}

api.mamaput.ng {
	@compressible not path /v2/kitchen/orders/stream /v2/orders/*/stream
	encode @compressible zstd gzip

	reverse_proxy {
		dynamic a {
			name api
			port 8080
			refresh 2s
		}
		lb_policy round_robin
		lb_try_duration 5s
		fail_duration 10s
		flush_interval -1
	}
}
```

1. **`api.mamaput.ng {`**: Caddy gets and renews a free HTTPS certificate for this name from Let's Encrypt, by itself. That's most of why we chose it. (`email` is where Let's Encrypt writes if something's wrong.)
2. **`dynamic a { name api  port 8080  refresh 2s }`**: ask Docker's DNS for every address of `api`, and spread requests across them: both API copies, found by name. **`refresh 2s`** matters more than it looks. Caddy's default is to ask again only once a minute, so during a deploy it would keep sending requests to copies that have already gone, and ignore the new ones for up to a minute. Lesson 29's deploy script waits longer than this before stopping the old copies.
3. **`lb_try_duration 5s` and `fail_duration 10s`**: if a copy refuses a connection (it's in the middle of step 3's shutdown), try the other one for up to 5 seconds, and avoid the failed one for 10. Together with step 3's drain, a deploy drops nothing.
4. **`flush_interval -1`**: pass every byte on at once, without buffering. Lesson 20's server-sent events need it, or the kitchen screen's events would wait in Caddy.
5. **`encode @compressible zstd gzip`**: compress responses for clients that accept it, except on the stream routes. Lesson 20 warned that compression buffers what it compresses, so a stream's events would wait to be squeezed. `@compressible` is a **named matcher**: every path *except* the two streams.

`caddy validate` accepts this file. Caddy only listens on `edge`, and only it publishes ports to the world: 80 (which it redirects to HTTPS) and 443. Nothing else in the system can be reached from the internet. Not the admin ports, not gRPC, not Postgres.

### Prometheus, with two API copies

Lesson 27's `prometheus.yml` pointed at `host.docker.internal`. Inside Compose, use the service names, and DNS discovery so both API copies are scraped:

```yaml
scrape_configs:
  - job_name: api
    dns_sd_configs: [{ names: ["api"], type: A, port: 9100 }]
  - job_name: worker
    static_configs: [{ targets: ["worker:9101"] }]
  - job_name: notifications
    static_configs: [{ targets: ["notifications:9102"] }]
rule_files: ["/etc/prometheus/alerts.yml"]
```

`OTEL_ENDPOINT=jaeger:4317` in the env files sends traces to Jaeger.

## Step 7: running it
<!-- bite: 3ae9de94-e8e6-42f5-b009-6ff9615a6018 -->

Make the secrets once (random passwords and keys; never reuse a real one on a laptop):

```bash
mkdir -p secrets
for name in postgres_password migrate_db_password api_db_password notifications_db_password; do
  openssl rand -base64 24 | tr -d '/+=' > "secrets/$name"
done
openssl rand -base64 48 > secrets/jwt_secret
echo "sk_test_your_paystack_test_key" > secrets/paystack_secret_key
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out secrets/notifications_private_key
echo "postgres://mamaput_migrate:$(cat secrets/migrate_db_password)@postgres:5432/mamaput" > secrets/migrate_database_url
echo "postgres://mamaput_app:$(cat secrets/api_db_password)@postgres:5432/mamaput" > secrets/api_database_url
echo "postgres://notifications:$(cat secrets/notifications_db_password)@postgres:5432/mamaput_notifications" > secrets/notifications_database_url
```

(The database URL files repeat the passwords. A small script, `deploy/make-secrets.sh`, keeps them in step; lesson 29's server uses the same script.)

Then:

```bash
docker compose build                # build the four Go images
docker compose up -d                # start everything, in order, in the background
docker compose ps                   # each service and its health
docker compose logs -f api          # follow the API's logs (both copies)
```

`docker compose ps` should show `migrate` as `exited (0)` and every Go service as `healthy` within half a minute. On a laptop, `api.mamaput.ng` won't point at you, so add a `compose.override.yaml` (Compose reads it automatically, and it stays out of git) that publishes the API's port directly for development:

```yaml
services:
  api:
    deploy: { replicas: 1 }
    ports: ["127.0.0.1:8080:8080"]
```

```bash
curl -s localhost:8080/
```

Okay!!!!! "Mama Put is open!", from a 10 MB container, with the whole system behind it.

Now try the things this lesson was for:

1. **Stop politely.** `docker compose stop api` while running `curl` in a loop against it: no failed requests. Look at the logs: `stopping: no longer ready`, then `stopped`, well inside 30 seconds.
2. **A broken setting.** Set `DB_MAX_CONNS=500` in `deploy/api.env` and `docker compose up -d api`: it refuses to start, and `docker compose logs api` shows exactly why.
3. **A dependency down.** `docker compose stop nats`: the API stays *alive* (no restarts), and `/readyz` on its admin port says `{"nats":"unavailable"}`. Start NATS again, and it's ready again.
4. **Data survives.** `docker compose down` then `docker compose up -d`: orders are still there, because the volumes stay. (`docker compose down -v` **deletes the volumes**, and every order with them. On a server, never.)

## The Go in this lesson
<!-- bite: 9df7c599-38b0-4dd6-b603-3c82d8f82efc -->

1. **`errors.Join(errs...)`** (Go 1.20): One error made of many, printed one per line; `nil` if the list is empty.
2. **A named string type with methods, `type Secret string`**: Costs nothing, behaves like a string, but prints, logs and marshals as `[secret]`.
3. **`fmt.Stringer`, `fmt.GoStringer`, `slog.LogValuer`, `encoding.TextMarshaler`**: The four interfaces that decide how a value is shown by `fmt`, slog and `encoding/json`.
4. **`atomic.Bool`**: A true/false many goroutines can read and set safely; here, "ready".
5. **`sync.WaitGroup` with `Add` and `Done`**: Waits for a group of goroutines, here the health checks running at once. (Go 1.25 adds `wg.Go(func)`, which does both for you.)
6. **`signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)`**: A context cancelled when the program is asked to stop.
7. **`errgroup.WithContext`**: Runs goroutines that live and die together: the first error cancels the shared context, and `Wait` returns it.
8. **`http.Server.Shutdown(ctx)`** and **`RegisterOnShutdown(f)`**: Stop accepting, wait for running requests until `ctx` ends; run `f` the moment shutdown starts, to end streams.
9. **`http.ErrServerClosed`**: What `Serve` returns after `Shutdown`: the normal ending.
10. **`os.Args`**: The program's command-line words; `os.Args[1] == "healthcheck"` makes a subcommand.
11. **`-ldflags "-X main.version=..."`**: Sets a package-level string variable when building.
12. **`CGO_ENABLED=0`**: A pure-Go binary with no C libraries, so it runs on an empty image.

## Your project so far
<!-- bite: cafbad9f-4079-40a3-b36c-1cd148e79ccd -->

```text
mama-put/
├── Dockerfile                     ← NEW: two stages, any cmd/ by build argument, distroless nonroot
├── .dockerignore                  ← NEW: no .git, tests, .env or keys in images
├── compose.yaml                   ← NEW: the whole system: 4 Go services, migrate, Postgres, 2 Redis, NATS, Caddy, Jaeger, Prometheus
├── compose.override.yaml          ← (not committed) one API copy, port 8080 published, for your laptop
├── secrets/                       ← (not committed) one file per secret
├── deploy/
│   ├── Caddyfile                  ← NEW: HTTPS, both API copies, retries during deploys, no buffering for SSE
│   ├── postgres-init.sh           ← NEW: migrate and app roles, default privileges, separate notifications database
│   ├── make-secrets.sh            ← NEW: makes the passwords, keys and URLs together
│   ├── api.env · notifications.env       ← NEW: settings that aren't secret
│   ├── prometheus.yml             ← service names, DNS discovery for the API copies, alert rules
│   └── alerts.yml
├── cmd/
│   ├── api/main.go                ← healthcheck subcommand; NotifyContext; config.LoadAPI; health.Serve with stops in order
│   ├── worker/main.go · notifications/main.go · migrate/main.go   ← the same shape
└── internal/
    ├── config/                    ← NEW: Reader (every problem at once), Secret, LoadAPI, LoadWorker, LoadNotifications
    ├── health/                    ← NEW: /livez, /readyz, Serve: ready off, drain, shutdown, stops, admin last
    └── kitchen/hub.go             ← CloseAll, for RegisterOnShutdown
```

## Common mistakes
<!-- bite: 77d2ee28-178d-438d-885a-52a56612ef8c -->

1. **Reading the environment all over the code.** Mistakes show up on the first request that needs the setting. Load and check everything at the top of `run`.
2. **Stopping at the first config error.** Fix, restart, repeat. Collect them all.
3. **Logging the config with secrets in it.** Give secrets a type that can't print itself.
4. **A liveness check that checks the database.** A database blip restarts every container. Liveness checks only the process.
5. **Shutting the listener the instant `SIGTERM` arrives.** Requests still on their way get connection errors. Stop being ready, wait, then shut down.
6. **No timeout on shutdown, or a grace period shorter than it.** Either it hangs forever on a stream, or `SIGKILL` lands mid-shutdown.
7. **Streams left open on shutdown.** They hold `Shutdown` for its whole timeout. `RegisterOnShutdown`.
8. **The app connecting as the database owner.** One injection and the tables can be dropped. A role for rows, another for schema.
9. **Migrations run by the API at start-up.** Two copies race, and the app role needs schema power. A separate one-off container.
10. **A Go compiler, a shell and root in the production image.** Two stages, distroless, `nonroot`.
11. **`HEALTHCHECK CMD curl ...` on a distroless image.** There's no curl and no shell. The program checks itself, in the list form.
12. **Private keys copied into images.** `.dockerignore` them, and hand them over as secrets.
13. **Data stores on a network the internet can reach.** Keep them on an `internal` network.
14. **`docker compose down -v` on a server.** It deletes the volumes, and the data with them.

## Check your understanding
<!-- bite: 6b8104b4-bb9c-4b73-80e7-0de2bf3231a5 -->

1. Why does `LoadAPI` keep reading settings after it finds a problem, and how does the caller get all of them?
2. Name three ways `Secret` stops a password being printed, and the one way to get it out on purpose.
3. NATS is down for two minutes. What should `/livez` and `/readyz` say, and what would go wrong if `/livez` checked NATS?
4. Walk through what happens between Docker sending `SIGTERM` to an API container and the process exiting, for a request that arrives one second after the signal.
5. Why does `migrate` run as its own container, with a different database role from the API?
6. Why is there no `HEALTHCHECK` line in the Dockerfile?
7. Which services are on the `backend` network only, and what can't happen because of it?

<details>
<summary>Answers, after your attempt</summary>

1. So one start reports every problem, instead of one per restart. Each `Reader` method records a problem and returns a value anyway; `r.Err()` at the end joins them all with `errors.Join`, which prints one per line.
2. Any three of: `String()` (and so `%v`, `%s`, `Println`), `GoString()` (`%#v`), `LogValue()` (slog), `MarshalText()` (`encoding/json`), all printing `[secret]`. `Reveal()` is the one way to get the real value, and it's easy to search for.
3. `/livez` should say 200: the process is fine. `/readyz` should say 503 with `{"nats":"unavailable"}`, so work goes elsewhere if it can. If `/livez` checked NATS, Docker would restart every API container during the outage, adding load and start-up work, and they'd all come back to the same missing NATS.
4. `signal.NotifyContext` cancels `ctx`; `health.Serve` sets `ready` to false, so `/readyz` says `stopping`, and waits the drain delay. The request arriving one second in is still accepted and answered normally, because the listener is still open. After the drain, `Shutdown` closes the listener, `RegisterOnShutdown` ends the kitchen streams, and `Shutdown` waits for running requests (including that one, if it's still going). Then gRPC, the consumers and the tracer are stopped, the admin server last, and `run` returns. All inside the 30-second grace period, so `SIGKILL` never comes.
5. So schema changes happen once, before any API copy starts (the `service_completed_successfully` condition), instead of two copies racing to migrate. And so the API's own role only needs row powers: a bug or injection in the API can't drop or change tables.
6. Because newer Docker builders write OCI-format images, which have no place for a health check, so the line is dropped; and its shell form needs `/bin/sh`, which distroless doesn't have. The check goes in `compose.yaml` instead, in the list form that runs `/app healthcheck` directly.
7. Postgres, both Redis servers and NATS. Because `backend` is `internal`, nothing on the internet can connect to them, and they can't connect out to the internet either: only the other containers on `backend` can reach them.

</details>

## Practice
<!-- bite: e2a9ee2e-a761-4fce-b44e-a4876942caa0 -->

1. Write `internal/config` with `Int`, `Float`, `URL` and `OneOf`, `LoadAPI`, `LoadWorker` and `LoadNotifications`, and a test that a messy environment reports every problem and a logged config shows no secret.
2. Write `internal/health` and the shutdown test from step 3, using `net.Listen("tcp", "127.0.0.1:0")`, a slow route and a stream.
3. Add `hub.CloseAll` to lesson 20's hub and register it with `RegisterOnShutdown`; check a `curl -N` kitchen stream ends straight away when you `docker compose stop api`.
4. Build all four images and compare their sizes. Then try `FROM scratch` instead of distroless for one of them: what breaks (try a Paystack call), and why?
5. Write `deploy/make-secrets.sh` from step 7's commands, so it refuses to overwrite existing secrets.
6. Bring the whole system up with `docker compose up -d`, pay for an order with lesson 17's signed webhook, and find the receipt line in `docker compose logs notifications` and the trace in Jaeger.

**Done when** `docker compose up -d` starts everything with every Go service `healthy`; a broken setting stops a service with a message naming every problem; no log line contains a secret; `docker compose stop api` during a `curl` loop drops no requests; the app's database role can't drop a table; the images are around 10 to 20 MB each; and nothing but Caddy can be reached from outside.

## Before moving on
<!-- bite: 928f9a9a-425a-41e6-9cac-fe22d864d9b2 -->

Mama Put is packaged. Each program checks its settings before it does anything, tells machines whether it's alive and whether it can take work, stops politely in a fixed order inside its grace period, connects to the database with only the powers it needs, and ships as a 10 MB image with nothing in it to attack. One `docker compose up -d` brings up the entire system, in order, on two private networks, with secrets that only reach the containers that need them.

One step left: getting it from your laptop to a real server, safely, every time. Tests run on every push, images are built and published, a server pulls the new version and replaces the old one without dropping an order, migrations run in the right order, and when something goes wrong, going back to the last good version is one command. That's the last lesson.

## Related
<!-- bite: 5e88509d-6fb7-4d07-b2fe-7c8882a1e0ec -->

- [[backend/frameworks/net-http/29-ci-and-deployment|Next: CI and Deployment]]
- [[backend/frameworks/express/28-production-config-and-docker|The same lesson in Express]] — zod-checked config and a Node image
- [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|What net/http Is]] — the server timeouts that started this
- [[backend/frameworks/net-http/20-real-time|Real-time Updates]] — the streams that shutdown must end
- [[backend/frameworks/net-http/27-observability|Observability]] — the admin port the health checks share

## About this lesson
<!-- bite: 88e6f5d2-04e4-4918-9e1f-9519bbd45a5c -->

**Level:** Advanced. Lesson 28 of the [[backend/frameworks/net-http/index|net/http]] subject. Written for Go 1.24 or later, Docker with BuildKit, and Docker Compose v2 or later. Covers typed config loaded once with every problem reported via `errors.Join`, a `Secret` type that can't print, log or marshal itself, secrets from `_FILE` paths, liveness versus readiness with concurrent checks, a self-check subcommand for images with no tools, graceful shutdown with `signal.NotifyContext`, a readiness flag, a drain delay, `http.Server.Shutdown`, `RegisterOnShutdown` for streams, a time-limited `GracefulStop`, and `errgroup`, matching Docker's grace period, separate migrate and app database roles with default privileges, a two-stage Dockerfile with cache mounts, `CGO_ENABLED=0`, `-trimpath`, `-ldflags` and a distroless nonroot image, why the health check lives in Compose, a Compose file with anchors, ordered `depends_on` conditions, a one-off migrate container, internal and edge networks, file secrets, read-only containers and two API replicas, Caddy with automatic HTTPS, DNS-discovered upstreams and unbuffered streams, and running and checking the whole system.
