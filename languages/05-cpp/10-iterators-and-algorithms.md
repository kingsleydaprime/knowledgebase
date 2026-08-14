# Iterators and Algorithms

**[Intermediate]** — The design that made the STL famous: containers and algorithms that know nothing about each other, connected by iterators.

## The idea

Without a common interface, *m* containers and *n* algorithms need *m × n* implementations. The STL's insight was to put an abstraction between them:

```
containers ──→ ITERATORS ──→ algorithms
```

An algorithm takes iterators, not containers. So `std::sort` works on a `vector`, an `array`, a raw C array, or anything else that provides the right iterators — and it never mentions any of them.

```cpp
std::sort(v.begin(), v.end());
std::sort(arr, arr + n);                     // raw C array
std::sort(std::begin(a), std::end(a));       // generic form
```

That's *m + n* implementations instead of *m × n*, and it's the reason the STL is considered a landmark design.

## Iterators

An iterator generalises a pointer. The core operations are deliberately pointer-shaped:

```cpp
*it        // dereference
++it       // advance
it != end  // compare
```

```cpp
auto it = v.begin();
auto end = v.end();                  // ONE PAST the last element — never dereference it

while (it != end) { std::cout << *it; ++it; }

v.cbegin(); v.cend();                // const iterators
v.rbegin(); v.rend();                // reverse
```

Ranges are **half-open**: `[begin, end)`. That's why `end()` isn't a valid element, why `end - begin` is the size, and why an empty range is `begin == end`. Every off-by-one convention in the library follows from it.

### The categories

Which algorithms work depends on what an iterator supports:

| Category | Supports | Example |
|---|---|---|
| **Input** | read, `++`, single pass | `istream_iterator` |
| **Output** | write, `++` | `back_insert_iterator` |
| **Forward** | read/write, `++`, multi-pass | `forward_list` |
| **Bidirectional** | `--` too | `list`, `map`, `set` |
| **Random access** | `+n`, `-n`, `[]`, `<` | `vector`, `deque`, `array` |
| **Contiguous** (C++17) | elements are adjacent in memory | `vector`, `array`, `string` |

This is why `std::sort` doesn't work on `std::list` — sorting needs random access, and a list only offers bidirectional. `list` provides its own `.sort()` member instead. When "no matching function for call to `sort`" appears on a `list`, that's the reason.

## `<algorithm>`

```cpp
#include <algorithm>
#include <numeric>

// searching
std::find(b, e, value);
std::find_if(b, e, pred);
std::count(b, e, value);            std::count_if(b, e, pred);
std::any_of / all_of / none_of(b, e, pred);
std::binary_search(b, e, value);    // requires a SORTED range
std::lower_bound(b, e, value);      // first >= value
std::upper_bound(b, e, value);      // first > value

// modifying
std::copy(b, e, dest);              std::copy_if(b, e, dest, pred);
std::transform(b, e, dest, fn);     // map
std::fill(b, e, value);             std::generate(b, e, fn);
std::replace(b, e, old, new);
std::remove(b, e, value);           // shuffles; see the erase-remove note below
std::reverse(b, e);                 std::rotate(b, mid, e);
std::unique(b, e);                  // removes CONSECUTIVE duplicates — sort first

// sorting
std::sort(b, e);                    std::sort(b, e, cmp);
std::stable_sort(b, e);             // preserves relative order of equal elements
std::partial_sort(b, mid, e);       // only the first k, cheaper than a full sort
std::nth_element(b, nth, e);        // O(n) selection — nth is in its final position
std::is_sorted(b, e);

// numeric
std::accumulate(b, e, init);            // fold
std::accumulate(b, e, init, op);
std::reduce(b, e);                      // C++17 — parallelisable, unordered
std::inner_product(b, e, b2, init);
std::iota(b, e, start);                 // fill with start, start+1, ...
std::partial_sum(b, e, dest);

// min/max
std::min_element(b, e);             std::max_element(b, e);
std::minmax_element(b, e);
std::clamp(v, lo, hi);              // C++17
```

**`std::nth_element`** is under-used: it puts the *n*th element where it would be if sorted, in O(n), which is the right tool for medians and top-k. → [[foundations/dsa/06-patterns/07-top-k-elements|Top-K Elements]]

**`std::lower_bound`** is binary search that returns a position rather than a bool — the building block for sorted-vector lookups and insert-in-order.

## Predicates and lambdas

```cpp
std::sort(v.begin(), v.end(), [](const auto &a, const auto &b) {
    return a.score > b.score;                     // descending
});

auto it = std::find_if(v.begin(), v.end(), [target](const auto &x) {
    return x.id == target;
});

int n = std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });
```

The comparator must be a **strict weak ordering**: irreflexive (`!cmp(a,a)`), asymmetric, and transitive. Using `<=` instead of `<` violates it and `std::sort` may read out of bounds — a genuine crash, not just a wrong order. Debug STL builds (`-D_GLIBCXX_DEBUG`) catch it.

## The erase-remove idiom

```cpp
v.erase(std::remove(v.begin(), v.end(), value), v.end());
v.erase(std::remove_if(v.begin(), v.end(), pred), v.end());
```

Algorithms take iterators, so they **cannot resize a container** — they have no access to it. `std::remove` shuffles unwanted elements toward the end and returns the new logical end; `erase` does the actual removal.

```cpp
std::erase(v, value);                             // C++20 — do this instead
std::erase_if(v, pred);
```

## Ranges (C++20)

The biggest quality-of-life change since C++11:

```cpp
#include <ranges>
namespace rv = std::views;

std::ranges::sort(v);                             // no .begin()/.end()
auto it = std::ranges::find(v, 42);

auto result = v
    | rv::filter([](int n) { return n % 2 == 0; })
    | rv::transform([](int n) { return n * n; })
    | rv::take(5);

for (int x : result) { }                          // LAZY — nothing runs until iterated
```

Two real improvements: **algorithms take containers directly**, removing the `begin()/end()` noise, and **views compose lazily** so a chain does one pass with no intermediate containers.

```cpp
rv::filter  rv::transform  rv::take  rv::drop  rv::reverse
rv::take_while  rv::drop_while  rv::join  rv::split
rv::iota  rv::keys  rv::values  rv::enumerate (C++23)
```

Same model as [[languages/03-rust/11-collections-and-iterators|Rust's iterator adapters]] and [[languages/02-go/README|far ahead of Go]], which has none. Caveats: ranges compile slowly, error messages are still rough, and `views::filter` has surprising requirements on its predicate (it must be pure and cheap — it's evaluated more than once).

To materialise:

```cpp
auto v2 = result | std::ranges::to<std::vector>();   // C++23
```

## Custom iterators

For your own container to work with algorithms:

```cpp
class Range {
    int begin_, end_;
public:
    class iterator {
        int v_;
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = int;
        using difference_type = std::ptrdiff_t;
        using pointer = const int *;
        using reference = const int &;

        explicit iterator(int v) : v_(v) {}
        int operator*() const { return v_; }
        iterator &operator++() { ++v_; return *this; }
        bool operator==(const iterator &o) const = default;
    };

    iterator begin() const { return iterator(begin_); }
    iterator end()   const { return iterator(end_); }
};
```

The five `using` declarations are what algorithms query to decide which implementation to use. Miss them and you get a template error from inside `<algorithm>` — one of the classic bad C++ error messages, and one that [[languages/05-cpp/08-templates-and-concepts|concepts]] now diagnose properly.

Defining `begin()`/`end()` is also all you need for range-based `for`:

```cpp
for (int x : Range(0, 10)) { }
```

## Are they as fast as a loop?

Yes, and often faster. They're templates, fully inlined, and the standard implementations use tricks you wouldn't bother with — `std::sort` is introsort (quicksort, switching to heapsort on bad pivots, insertion sort for small ranges), and `std::copy` on trivially-copyable types becomes `memmove`.

**Prefer the algorithm over a hand-written loop.** It says *what* rather than *how*, it's harder to get wrong, and it's at least as fast.

```cpp
// C++17 parallel execution
#include <execution>
std::sort(std::execution::par, v.begin(), v.end());
std::transform(std::execution::par_unseq, b, e, dest, fn);
```

One argument, and it's parallel — though `libstdc++` needs Intel TBB linked for it to actually parallelise.

## Practical rules

1. **Algorithm over hand-written loop.**
2. **`std::erase`/`erase_if` (C++20)** over the erase-remove idiom.
3. **Ranges where available** — less noise, lazy composition.
4. **Comparators must be strict weak orderings** — `<`, never `<=`.
5. **`nth_element` for selection, `partial_sort` for top-k.**
6. **`const auto&` in range-for** unless modifying.
7. **`-D_GLIBCXX_DEBUG`** in debug builds — it catches invalidation and bad comparators.

---

## Related
- [[languages/05-cpp/09-the-stl-containers|The STL Containers]] — what iterators point into, and invalidation
- [[languages/05-cpp/08-templates-and-concepts|Templates and Concepts]] — how all of this is implemented
- [[foundations/dsa/05-algorithms/01-algorithms|Algorithms]] — what these implement
- [[languages/03-rust/11-collections-and-iterators|Rust: Iterators]] — the same design, memory-safe
- [[languages/05-cpp/README|C++ course map]]
