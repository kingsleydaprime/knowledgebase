# Methods and Interfaces

**[Intermediate]** — Receivers and the pointer/value decision, implicit interface satisfaction, and why Go interfaces are declared by the consumer rather than the producer.

## Methods

```go
type Rectangle struct{ Width, Height float64 }

func (r Rectangle) Area() float64 {          // value receiver
    return r.Width * r.Height
}

func (r *Rectangle) Scale(f float64) {       // pointer receiver
    r.Width *= f
    r.Height *= f
}
```

A method is a function with a **receiver** — the parameter before the name. There are no classes; methods can be attached to any named type you defined in the same package, including non-structs:

```go
type Celsius float64
func (c Celsius) Fahrenheit() Celsius { return c*9/5 + 32 }
```

You cannot add methods to types from other packages. To extend `time.Time`, define `type MyTime time.Time` or embed it.

## Value vs pointer receivers

The rule that actually matters:

```go
func (r Rectangle) Area() float64   // gets a COPY — mutations are lost
func (r *Rectangle) Scale(f float64) // gets a pointer — mutations stick
```

**Use a pointer receiver if:** the method mutates the receiver, the struct is large enough that copying costs, or the type contains a `sync.Mutex` (copying a mutex is a bug — `go vet` catches it).

**Use a value receiver if:** the type is small and immutable-ish, or it's a map/slice/chan wrapper where the header copy is already a reference.

**Be consistent within a type.** If any method needs a pointer receiver, give them all pointer receivers. Mixed receivers are the most common Go style complaint in review, and they cause the method-set problem below.

Go auto-dereferences for convenience, so calling looks the same either way:

```go
r := Rectangle{2, 3}
r.Scale(2)      // compiler rewrites to (&r).Scale(2)
p := &r
p.Area()        // rewrites to (*p).Area()
```

That convenience hides a rule that bites with interfaces:

> **The method set of `T` includes only value-receiver methods. The method set of `*T` includes both.**

```go
type Shape interface{ Scale(float64) }

var s Shape = Rectangle{}    // COMPILE ERROR — Scale has a pointer receiver
var s Shape = &Rectangle{}   // fine
```

The auto-dereference works on a concrete variable because the compiler knows it's addressable. An interface value isn't addressable, so the rule applies strictly. When "my type doesn't implement the interface" makes no sense to you, this is nearly always why — you passed a value where a pointer was needed.

## Interfaces

```go
type Writer interface {
    Write(p []byte) (n int, err error)
}
```

**Satisfaction is implicit.** There is no `implements` keyword. Any type with a matching method set satisfies the interface, including types written before the interface existed — and by authors who've never heard of it.

This is the single biggest structural difference from Java, and it inverts where interfaces live:

> **Define interfaces in the package that *consumes* them, not the one that implements them.**

In Java, `UserRepository` (the interface) ships with the persistence layer and the service depends on it. In Go, the *service* declares the small interface it needs, and the persistence package just has concrete types:

```go
// package service — declares what IT needs
type UserStore interface {
    GetUser(ctx context.Context, id int) (*User, error)
}

func NewService(store UserStore) *Service { ... }
```

The `postgres` package never imports `service` and never mentions `UserStore`. It just has a `*Postgres` with a `GetUser` method. Dependency direction stays clean without anyone arranging it, and testing needs no mocking framework — a struct with the right method is a test double.

This is [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal architecture]] falling out of the language rather than being imposed on it. Compare with [[languages/01-java/03-tooling/02-dependency-injection|Java's DI container]], which achieves the same inversion with a runtime framework.

### Keep interfaces small

> *"The bigger the interface, the weaker the abstraction."* — Rob Pike

The standard library's most-used interfaces have one method:

```go
type Stringer interface{ String() string }
type error interface{ Error() string }
type Reader interface{ Read(p []byte) (int, error) }
type Writer interface{ Write(p []byte) (int, error) }
```

`io.Reader` and `io.Writer` are why Go composes so well: a file, a network connection, an HTTP body, a gzip stream, a hash, and an in-memory buffer are all `io.Reader`s, so `io.Copy(dst, src)` works across every combination. Learning to reach for these two before writing your own abstraction is most of learning idiomatic Go.

### The empty interface and `any`

```go
var x any            // Go 1.18+; alias for interface{}
```

Satisfied by everything, so it carries no information. Getting the value back out needs a type assertion:

```go
s, ok := x.(string)      // comma-ok form — never panics
s := x.(string)          // panics if x isn't a string

switch v := x.(type) {   // type switch
case string: fmt.Println("string", v)
case int:    fmt.Println("int", v)
default:     fmt.Println("other")
}
```

Since generics landed, most former uses of `any` should be type parameters. → [[languages/02-go/09-generics|Generics]]

## The nil interface trap

The sharpest edge in the language:

```go
type MyErr struct{}
func (e *MyErr) Error() string { return "boom" }

func doThing() error {
    var p *MyErr = nil
    return p            // returning a nil POINTER as an error
}

if err := doThing(); err != nil {
    fmt.Println("error!")   // THIS RUNS
}
```

An interface value is a pair: **(type, value)**. It's `nil` only when *both* halves are nil. Returning a nil `*MyErr` produces `(*MyErr, nil)` — a non-nil interface holding a nil pointer.

The fix is to never declare a typed nil and return it:

```go
func doThing() error {
    if bad { return &MyErr{} }
    return nil          // an untyped nil — genuinely nil
}
```

Every Go programmer meets this once. It's the reason `if err != nil` can be true when you're certain nothing failed.

---

## Related
- [[languages/02-go/05-errors|Errors]] — `error` is just an interface
- [[languages/02-go/10-the-standard-library|The Standard Library]] — `io.Reader`/`io.Writer` in practice
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal Architecture]] — what consumer-side interfaces give you for free
- [[languages/01-java/01-language/02-oop|Java: OOP]] — inheritance and explicit `implements`, for contrast
- [[languages/02-go/README|Go course map]]
