# Composite Types

**[Beginner → Intermediate]** — Arrays, slices, maps and structs. Slices are the one that causes real bugs, so most of this note is about them.

## Arrays are not what you use

```go
var a [5]int          // length is part of the TYPE
b := [3]string{"x", "y", "z"}
c := [...]int{1, 2, 3}  // compiler counts it: [3]int
```

`[5]int` and `[3]int` are **different types**. Arrays are values — assigning one copies it. Because the length is baked into the type, arrays are almost useless for real work, and you'll see them mostly as the backing store for slices or as fixed-size buffers like `[32]byte` for a hash.

## Slices — the important one

A slice is a three-field struct pointing at a backing array:

```
slice = { pointer → backing array, len, cap }
```

```go
s := []int{1, 2, 3}          // literal
s := make([]int, 5)          // len 5, cap 5, all zeros
s := make([]int, 0, 100)     // len 0, cap 100 — preallocated
var s []int                  // nil slice; len 0, usable with append
```

`len(s)` is how many elements you can index; `cap(s)` is how many fit before reallocation.

### `append` and the reallocation rule

```go
s := make([]int, 0, 2)
s = append(s, 1)      // len 1, cap 2
s = append(s, 2)      // len 2, cap 2
s = append(s, 3)      // cap exceeded → NEW backing array allocated, contents copied
```

**You must assign the result of `append`.** `append(s, x)` without assignment is a bug the compiler won't always catch, because `append` may return a slice with a different pointer.

Preallocate when you know the size — it's the single easiest Go performance win:

```go
out := make([]string, 0, len(in))   // one allocation instead of log(n) reallocations
for _, v := range in {
    out = append(out, transform(v))
}
```

### The aliasing trap

This is the bug. Slicing does **not** copy — it creates a new slice header pointing into the *same* backing array:

```go
a := []int{1, 2, 3, 4, 5}
b := a[1:3]          // len 2, cap 4 — shares memory with a
b[0] = 99
fmt.Println(a)       // [1 99 3 4 5]  ← a changed
```

Worse, because `b` has spare capacity, appending to it **overwrites `a`**:

```go
b = append(b, 100)   // writes into a[3]
fmt.Println(a)       // [1 99 3 100 5]
```

Two defences:

```go
b := a[1:3:3]              // three-index slice: caps it, so append must reallocate
b := slices.Clone(a[1:3])  // explicit copy (Go 1.21+); or copy() manually
```

The three-index form `a[low:high:max]` sets capacity to `max-low`. It looks obscure and it's the correct fix when you hand a sub-slice to code you don't control.

The same trap in reverse: a function taking `[]byte` can mutate the caller's data. If a function shouldn't retain or mutate a slice, say so in its doc comment — Go has no `const`.

### Other slice facts

```go
copy(dst, src)               // copies min(len(dst), len(src)); returns count
s = append(s[:i], s[i+1:]...)   // delete index i (order preserved)
s = slices.Delete(s, i, i+1)    // Go 1.21+, clearer

// A nil slice is fine to append to and ranges over zero times
var s []int
s = append(s, 1)             // works
fmt.Println(s == nil)        // false now
```

Prefer returning a nil slice over an empty one; `len()` treats them identically and it avoids a pointless allocation. Note `encoding/json` marshals a nil slice as `null` and an empty slice as `[]`, which does matter for API responses.

## Maps

```go
m := map[string]int{"a": 1}
m := make(map[string]int)
var m map[string]int         // nil map — reads OK, WRITES PANIC
```

```go
v := m["missing"]        // zero value, no error
v, ok := m["missing"]    // the comma-ok idiom — ok is false if absent
delete(m, "key")
len(m)
```

The comma-ok form is the only way to distinguish "absent" from "present and zero".

Three things that catch people:

**Iteration order is randomised, deliberately.** Not unspecified — actively randomised per run, so you can't accidentally depend on it. To iterate in order, collect and sort the keys:

```go
keys := make([]string, 0, len(m))
for k := range m { keys = append(keys, k) }
slices.Sort(keys)
```

**Maps are not safe for concurrent use.** Concurrent read+write panics with a runtime error rather than corrupting silently — a deliberate and helpful choice. Guard with a mutex, or use `sync.Map` for the specific case of many reads and few writes. → [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]]

**You cannot take the address of a map element.** `&m["k"]` doesn't compile, and `m["k"].Field = x` fails for struct values, because the element isn't addressable. Store pointers (`map[string]*User`) if you need to mutate in place.

Map keys must be comparable: no slices, maps, or functions as keys. A struct of comparable fields works fine, which is a nice way to key on a composite.

## Structs

```go
type User struct {
    ID    int
    Name  string
    Email string
}

u := User{ID: 1, Name: "Kingsley"}   // field names — always use this form
u := User{1, "Kingsley", ""}         // positional — breaks when fields are added
p := &User{ID: 1}                    // pointer to a new struct
```

**Structs are values.** Assigning or passing one copies every field. That's cheap for small structs and not for large ones — pass a pointer when the struct is big or when you need to mutate it.

### Tags

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`
    pass  string `json:"-"`
}
```

Struct tags are raw-string metadata read by reflection at runtime. `encoding/json` uses them for field naming; database and validation libraries use their own keys. Same mechanism as Java annotations, but stringly-typed — a typo in a tag is silent, which is the obvious downside.

### Embedding

```go
type Base struct { ID int; CreatedAt time.Time }

type User struct {
    Base            // embedded — no field name
    Name string
}

u.ID = 1            // promoted from Base
u.Base.ID = 1       // the same field, explicitly
```

Embedding **promotes** the embedded type's fields and methods. This is composition that reads like inheritance — but there is no subtyping: a `User` is not a `Base`, and you cannot pass one where the other is expected. It's the mechanism behind Go's "composition over inheritance" claim, and it works well until two embedded types have a field with the same name, at which point the ambiguity is a compile error you resolve by qualifying.

### Comparability and the empty struct

Structs are comparable with `==` if all their fields are. That makes them usable as map keys.

`struct{}` — the empty struct — occupies **zero bytes**, which gives the idiomatic set:

```go
set := map[string]struct{}{}
set["a"] = struct{}{}
_, exists := set["a"]
```

`map[string]bool` is more readable and wastes one byte per entry. Use whichever; know why you see the ugly one.

---

## Related
- [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]] — attaching behaviour to these
- [[languages/02-go/13-performance-and-runtime|Performance and the Runtime]] — why preallocating matters
- [[foundations/dsa/04-data-structures/02-dynamic-arrays|Dynamic Arrays]] and [[foundations/dsa/04-data-structures/03-hash-maps|Hash Maps]] — what a slice and a map are underneath
- [[languages/02-go/README|Go course map]]
