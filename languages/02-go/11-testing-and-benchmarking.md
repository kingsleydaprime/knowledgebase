# Testing and Benchmarking

**[Intermediate]** — Table-driven tests, benchmarks that don't lie, fuzzing, and the assertion-library argument.

## The built-in testing package

Tests live beside the code, in `_test.go` files:

```go
// math.go        → package calc
// math_test.go   → package calc  (internal) or calc_test (external)

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    if got != 5 {
        t.Errorf("Add(2, 3) = %d; want 5", got)
    }
}
```

```bash
go test ./...
go test -v ./...              # per-test output
go test -run TestAdd ./...    # regex filter
go test -race ./...           # ALWAYS in CI
go test -cover ./...
go test -coverprofile=c.out ./... && go tool cover -html=c.out
```

`t.Errorf` records a failure and continues; `t.Fatalf` stops the test immediately. Use `Fatalf` when continuing would panic (a nil result), `Errorf` when you want all the failures at once.

**There is no assertion library in the standard library.** You write `if got != want`. That's deliberate, and it's the thing newcomers push back on hardest.

## Table-driven tests

The dominant Go idiom, and the reason the missing assertion library matters less than it sounds:

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    float64
        want    float64
        wantErr bool
    }{
        {"simple", 10, 2, 5, false},
        {"negative", -10, 2, -5, false},
        {"by zero", 10, 0, 0, true},
        {"fraction", 1, 3, 0.333, false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Divide(tt.a, tt.b)
            if (err != nil) != tt.wantErr {
                t.Fatalf("Divide() error = %v, wantErr %v", err, tt.wantErr)
            }
            if !tt.wantErr && math.Abs(got-tt.want) > 0.001 {
                t.Errorf("Divide() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

`t.Run` creates a **subtest** with its own name, so failures report as `TestDivide/by_zero` and you can run one with `-run 'TestDivide/by_zero'`.

Adding a case is one line. That's the payoff: the pressure is toward more cases, which is where test value actually comes from.

`t.Parallel()` inside the subtest runs cases concurrently — useful for slow I/O tests, and a good way to shake out shared-state bugs.

## Helpers, cleanup, and fixtures

```go
func setupDB(t *testing.T) *sql.DB {
    t.Helper()                 // failures report the CALLER's line, not this one
    db, err := sql.Open("postgres", testDSN)
    if err != nil { t.Fatalf("open: %v", err) }
    t.Cleanup(func() { db.Close() })    // runs at test end, even on failure
    return db
}
```

`t.Helper()` and `t.Cleanup()` are both underused. `Cleanup` is better than `defer` in a helper, because the helper returns before the test does.

```go
func TestMain(m *testing.M) {      // package-level setup/teardown
    code := m.Run()
    os.Exit(code)
}
```

## Test doubles need no framework

Because interfaces are satisfied implicitly ([[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]]), a fake is just a struct:

```go
type fakeStore struct {
    users map[int]*User
    err   error
}

func (f *fakeStore) GetUser(ctx context.Context, id int) (*User, error) {
    if f.err != nil { return nil, f.err }
    u, ok := f.users[id]
    if !ok { return nil, ErrNotFound }
    return u, nil
}

svc := NewService(&fakeStore{users: map[int]*User{1: {Name: "K"}}})
```

No Mockito, no `jest.mock`, no annotations. This is the practical payoff of consumer-declared interfaces — and it pushes you toward small interfaces, because a fake for a 12-method interface is miserable to write.

For HTTP, `net/http/httptest` covers both directions:

```go
srv := httptest.NewServer(handler)     // a real server on a random port
defer srv.Close()

rec := httptest.NewRecorder()          // or test a handler directly
req := httptest.NewRequest("GET", "/users/1", nil)
handler.ServeHTTP(rec, req)
if rec.Code != http.StatusOK { t.Errorf("got %d", rec.Code) }
```

## The assertion-library argument

`stretchr/testify` is the most-used Go package that isn't in the stdlib:

```go
assert.Equal(t, 5, got)
require.NoError(t, err)      // require stops the test; assert continues
```

**For it:** far less boilerplate, much better failure diffs on structs and maps, and `require.NoError` is genuinely nicer than four lines of `if err != nil`.

**Against it:** it's a dependency in every test file, `assert.Equal(t, a, b)` gives no hint which is expected and which is actual, and the Go team's position is that a test failure should print exactly what you chose to print.

**The pragmatic position:** stdlib for libraries you publish, testify for application code if the team likes it. What you should not do is mix both in one codebase. For comparing structs without testify, `google/go-cmp` is the standard answer and is better at diffs than `reflect.DeepEqual`:

```go
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("mismatch (-want +got):\n%s", diff)
}
```

## Benchmarks

```go
func BenchmarkConcat(b *testing.B) {
    for b.Loop() {              // Go 1.24+; older code uses for i := 0; i < b.N; i++
        var s string
        for j := range 100 { s += strconv.Itoa(j) }
    }
}
```

```bash
go test -bench=. -benchmem ./...
go test -bench=Concat -benchtime=10s -count=5 ./...
```

```
BenchmarkConcat-8    12345    97234 ns/op    54321 B/op    99 allocs/op
```

`-benchmem` is the column that usually matters — allocations per operation is the number you can actually act on in Go, more than raw nanoseconds.

Two rules for benchmarks that mean anything:

**Reset the timer after setup:**
```go
data := buildLargeInput()
b.ResetTimer()
```

**Stop the compiler optimising your work away** by assigning to a package-level variable:
```go
var result int      // package level
func BenchmarkX(b *testing.B) {
    var r int
    for b.Loop() { r = compute() }
    result = r      // now compute() can't be eliminated as dead code
}
```

Compare runs properly with `benchstat` rather than eyeballing:

```bash
go test -bench=. -count=10 > old.txt
# make the change
go test -bench=. -count=10 > new.txt
benchstat old.txt new.txt      # reports deltas with statistical significance
```

## Fuzzing

Built in since 1.18, and genuinely worth using on any parser or decoder:

```go
func FuzzParse(f *testing.F) {
    f.Add("valid input")          // seed corpus
    f.Add("")
    f.Fuzz(func(t *testing.T, s string) {
        got, err := Parse(s)
        if err != nil { return }              // errors are fine; panics are not
        if _, err := Parse(got.String()); err != nil {
            t.Errorf("round-trip failed for %q", s)
        }
    })
}
```

```bash
go test -fuzz=FuzzParse -fuzztime=60s
```

Failing inputs are written to `testdata/fuzz/` and become permanent regression tests automatically. Round-trip properties like the one above are the easiest high-value fuzz target.

## Example tests

```go
func ExampleAdd() {
    fmt.Println(Add(2, 3))
    // Output: 5
}
```

Compiled, run as a test *and* rendered in the generated docs. Documentation that cannot go stale, because CI fails when it does.

---

## Related
- [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]] — `-race` belongs in every test run
- [[languages/02-go/13-performance-and-runtime|Performance and the Runtime]] — pprof, after benchmarks tell you where to look
- [[devops/06-ci-cd/08-ci-pipelines|CI Pipelines]] — wiring `go test -race ./...` into a gate
- [[languages/01-java/03-tooling/04-testing|Java: Testing]] — JUnit and Mockito, the framework-heavy alternative
- [[languages/02-go/README|Go course map]]
