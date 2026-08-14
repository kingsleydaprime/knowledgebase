# Language Fundamentals

**[Beginner]** — Declarations, the type system's strictness, functions with multiple returns, and the three control structures Go bothered to keep.

## Variables

```go
var x int = 5      // full form
var x = 5          // type inferred
x := 5             // short form — only inside a function
var x int          // zero value: 0

const Pi = 3.14159 // constants are compile-time only
```

`:=` is what you'll write 95% of the time. It cannot appear at package level — top-level declarations need `var` or `const`.

**Every type has a zero value, and it's always usable.** This is a deliberate design decision that shows up everywhere:

| Type | Zero value |
|---|---|
| numeric | `0` |
| `string` | `""` |
| `bool` | `false` |
| pointer, slice, map, chan, func, interface | `nil` |
| struct | every field at its own zero value |

There is no `undefined`, no uninitialised memory, and no "variable might not have been initialised" error. `var buf bytes.Buffer` is immediately usable — the zero value is an empty buffer. Types that are useful at their zero value are considered good Go design; `sync.Mutex` is the canonical example.

**An unused local variable is a compile error**, like unused imports. Package-level variables are exempt.

## The type system is stricter than you expect

```go
var i int = 5
var f float64 = i        // COMPILE ERROR
var f float64 = float64(i)  // explicit conversion required
```

No implicit numeric conversion at all — not even `int` → `int64`. This catches real bugs and is tedious in arithmetic-heavy code.

```go
type UserID int
type OrderID int

var u UserID = 1
var o OrderID = u    // COMPILE ERROR — distinct types
```

`type X Y` creates a genuinely new type, not an alias. This is the cheapest safety mechanism in the language and it's underused: making `UserID` and `OrderID` distinct types means you cannot pass one where the other is expected, which is a bug class that Java's `Long`-everywhere style permits freely.

(`type X = Y` with an equals sign *is* an alias, and is rare — it exists mainly for gradual refactors.)

### Basic types

```go
bool
string                                  // immutable, UTF-8, NOT a []rune
int  int8  int16  int32  int64          // int is 64-bit on modern platforms
uint uint8 uint16 uint32 uint64 uintptr
byte    // alias for uint8
rune    // alias for int32 — one Unicode code point
float32 float64
complex64 complex128
```

`byte` and `rune` are the two that matter. Indexing a string gives you a **byte**, not a character:

```go
s := "héllo"
fmt.Println(len(s))       // 6 — bytes, not characters
fmt.Println(s[1])         // 195 — the first byte of é
for i, r := range s {     // range over a string decodes UTF-8
    fmt.Println(i, string(r))   // r is a rune
}
```

`len()` on a string is bytes. This is correct and it will bite you the first time you slice user input.

## Functions

```go
func add(a int, b int) int { return a + b }
func add(a, b int) int      { return a + b }   // shared type
```

**Multiple return values** are the feature that shapes the rest of the language:

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

result, err := divide(10, 2)
if err != nil {
    return err
}
```

This is why Go doesn't need exceptions — the error is just the second return value. It's also why you'll type `if err != nil` more than any other line. → [[languages/02-go/05-errors|Errors]]

`_` discards a value you don't want:

```go
result, _ := divide(10, 2)   // ignoring an error — do this deliberately, rarely
```

### Named returns

```go
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return          // "naked return" — returns x, y
}
```

Naked returns hurt readability in anything longer than a few lines and are widely discouraged. But *naming* the returns is genuinely useful for documentation, and it's required if you want `defer` to modify the return value:

```go
func doThing() (err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("recovered: %v", r)   // modifies the named return
        }
    }()
    // ...
}
```

### Functions are values

```go
func apply(nums []int, f func(int) int) []int {
    out := make([]int, len(nums))
    for i, n := range nums { out[i] = f(n) }
    return out
}

doubled := apply(nums, func(n int) int { return n * 2 })
```

Closures capture by reference, which is the source of the classic loop-variable bug — **fixed in Go 1.22**, where each iteration gets a fresh variable. Before 1.22, every goroutine in a loop saw the final value. If you read older Go code with `i := i` shadowing at the top of a loop body, that's what it was for.

## `defer`

```go
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil { return err }
    defer f.Close()      // runs when readFile returns, whatever the path out

    // ... use f
    return nil
}
```

Deferred calls run **LIFO** when the surrounding *function* returns — not at end of block. Putting `defer f.Close()` immediately after the successful open is the idiom; it keeps acquisition and release adjacent, which is exactly what `try-with-resources` and RAII achieve differently.

Two traps:

```go
for _, path := range paths {
    f, _ := os.Open(path)
    defer f.Close()      // BUG: nothing closes until the whole loop finishes
}
```

```go
i := 0
defer fmt.Println(i)   // prints 0 — arguments evaluate NOW, the call runs later
i = 5
```

## Control flow

Go has `if`, `for`, and `switch`. That's it — no `while`, no `do-while`.

```go
if x > 5 { ... } else if x > 2 { ... } else { ... }

if err := doThing(); err != nil {   // statement then condition; err is scoped to the if
    return err
}
```

That scoped-initialiser form is extremely common — it keeps short-lived error variables out of the enclosing scope.

**`for` is the only loop keyword**, in four shapes:

```go
for i := 0; i < 10; i++ { }        // classic
for x < 10 { }                     // "while"
for { break }                      // infinite
for i, v := range collection { }   // range
```

**`switch` doesn't fall through** — no `break` needed. Use `fallthrough` explicitly if you want it.

```go
switch day {
case "sat", "sun":  fmt.Println("weekend")
default:            fmt.Println("weekday")
}

switch {                    // no expression = switch true; a clean if/else chain
case score >= 90: grade = "A"
case score >= 80: grade = "B"
}
```

## Pointers

```go
x := 5
p := &x          // *int
fmt.Println(*p)  // 5
*p = 10          // x is now 10
```

Pointers exist, **pointer arithmetic does not**. You cannot do `p++`. That removes the entire class of buffer-overrun bugs while keeping the ability to share and mutate.

`new(T)` allocates a zeroed T and returns `*T`, but you'll rarely use it — `&StructName{}` is idiomatic.

Whether the value lives on the stack or the heap is decided by **escape analysis**, not by `new` vs `&`. → [[languages/02-go/13-performance-and-runtime|Performance and the Runtime]]

---

## Related
- [[languages/02-go/03-composite-types|Composite Types]] — slices, maps, structs
- [[languages/02-go/05-errors|Errors]] — what that second return value is for
- [[languages/01-java/01-language/README|Java: the language]] — the same ground, in a language that made opposite choices
- [[languages/02-go/README|Go course map]]
