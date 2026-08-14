# The STL Containers

**[Intermediate]** — What to reach for, what each costs, and the invalidation rules that turn a container into a dangling pointer.

## `std::vector` — the default

```cpp
#include <vector>

std::vector<int> v;
std::vector<int> v(10);              // 10 elements, value-initialised to 0
std::vector<int> v(10, 5);           // 10 elements, all 5
std::vector<int> v{1, 2, 3};         // three elements — NOTE the brace trap below

v.push_back(4);
v.emplace_back(4);                   // constructs in place — prefer for non-trivial types
v.pop_back();
v[0];                                 // NO bounds check
v.at(0);                              // throws std::out_of_range
v.front(); v.back();
v.size(); v.empty(); v.capacity();
v.reserve(1000);                      // preallocate — the biggest easy win
v.shrink_to_fit();
v.clear();                            // size 0, capacity unchanged
v.insert(v.begin() + 2, 99);          // O(n)
v.erase(v.begin());                   // O(n)
v.data();                             // raw pointer, for C APIs
```

> **Use `std::vector` unless you have a specific reason not to.** Contiguous memory means it beats `std::list` and `std::deque` for almost every real workload — even for middle insertion at small sizes — because cache locality dominates asymptotic complexity until *n* is large.

Growth is amortised O(1): when capacity is exceeded, it allocates a larger buffer (typically 1.5× or 2×) and moves everything. `reserve()` when you know the size:

```cpp
std::vector<int> v;
v.reserve(n);                         // one allocation instead of log(n)
for (int i = 0; i < n; ++i) v.push_back(i);
```

**The brace trap**, from [[languages/05-cpp/03-classes-and-raii|Classes and RAII]]:

```cpp
std::vector<int> a(5, 0);            // 5 elements of 0
std::vector<int> b{5, 0};            // TWO elements: 5 and 0
```

**`std::vector<bool>` is not a vector.** It's a bit-packed specialisation whose `operator[]` returns a proxy, so `auto& b = v[0]` and `&v[0]` don't work. Use `std::vector<char>`, `std::deque<bool>`, or `std::bitset<N>`.

## The sequence containers

```cpp
std::array<int, 5> a{1,2,3,4,5};     // fixed size, ON THE STACK, no allocation
std::deque<int> d;                    // fast push/pop at BOTH ends; not contiguous
std::list<int> l;                     // doubly linked; O(1) splice; terrible locality
std::forward_list<int> fl;            // singly linked; minimal overhead
```

**`std::array` over a C array**, always — it knows its size, doesn't decay ([[languages/04-c/06-arrays-strings-and-decay|unlike C arrays]]), and works with algorithms.

**`std::list` is almost never the answer.** Its selling point is O(1) insertion given an iterator, but every node is a separate allocation and traversal is a pointer chase. Benchmarks consistently show `vector` winning even for workloads that theoretically favour a list. Use it when you need iterators that stay valid across insertion, or `splice`.

## Associative containers

```cpp
#include <map>
#include <unordered_map>

std::map<std::string, int> m;                 // red-black tree — SORTED, O(log n)
std::unordered_map<std::string, int> um;      // hash table — O(1) average

m["key"] = 1;                                  // INSERTS a default if absent
m.at("key");                                   // throws if absent
m.insert({"key", 1});                          // no-op if the key exists
m.insert_or_assign("key", 1);                  // C++17
m.try_emplace("key", 1);                        // C++17 — constructs only if inserting
m.contains("key");                              // C++20 — clearer than .count()
m.find("key");                                  // iterator, or end()
m.erase("key");

for (const auto &[key, value] : m) { }         // structured bindings — C++17
```

**`operator[]` inserts.** On a `const map` it doesn't compile, and on a non-const one, `if (m["missing"] == 0)` silently creates the entry. Use `find`, `contains`, or `at` to look up without inserting.

**`map` vs `unordered_map`:**

| | `map` | `unordered_map` |
|---|---|---|
| Structure | red-black tree | hash table |
| Lookup | O(log n) | O(1) average, O(n) worst |
| Ordered iteration | **yes** | no |
| Range queries | yes (`lower_bound`) | no |
| Requires | `operator<` | `std::hash` + `operator==` |
| Cache behaviour | poor (pointer chasing) | better |

**Default to `unordered_map`** unless you need sorted iteration or range queries. Note the constant factors are large enough that for small *n* (< ~30) a sorted `vector` of pairs beats both.

Also: `std::set`, `std::unordered_set`, `std::multimap`, `std::multiset`.

Custom types as keys:

```cpp
struct Point { int x, y; bool operator==(const Point&) const = default; };

template <>
struct std::hash<Point> {
    size_t operator()(const Point &p) const noexcept {
        return std::hash<int>{}(p.x) ^ (std::hash<int>{}(p.y) << 1);
    }
};
```

(That XOR-shift combine is the common example and it's mediocre; use `boost::hash_combine`'s formula for anything real.)

## Container adaptors

```cpp
std::stack<int> s;                    // LIFO — wraps deque by default
std::queue<int> q;                    // FIFO
std::priority_queue<int> pq;          // MAX-heap by default

std::priority_queue<int, std::vector<int>, std::greater<int>> min_heap;   // MIN-heap
```

The `std::greater` incantation for a min-heap is worth memorising — it's needed constantly in [[foundations/dsa/04-data-structures/08-heaps|heap]] problems.

## Iterator and reference invalidation

The rules that turn a container into a dangling pointer. **This is the C++ equivalent of a use-after-free, and it compiles silently.**

| Container | Operation | Invalidates |
|---|---|---|
| `vector` | `push_back`, `insert`, `reserve` **causing reallocation** | **everything** |
| `vector` | `erase` | everything at/after the erase point |
| `deque` | insert/erase at ends | iterators yes, references **no** |
| `deque` | insert/erase in the middle | everything |
| `list` | insert | nothing |
| `list` | erase | only the erased element |
| `map`/`set` | insert | nothing |
| `map`/`set` | erase | only the erased element |
| `unordered_*` | insert **causing rehash** | iterators yes, references **no** |

```cpp
std::vector<int> v{1, 2, 3};
int &r = v[0];
v.push_back(4);                       // may reallocate
r = 10;                                // DANGLING — use-after-free
```

```cpp
for (auto it = v.begin(); it != v.end(); ++it) {
    if (*it == 2) v.erase(it);        // UB — it is now invalid
}
```

The correct erase loop:

```cpp
for (auto it = v.begin(); it != v.end(); ) {
    if (*it == 2) it = v.erase(it);   // erase RETURNS the next valid iterator
    else ++it;
}

std::erase(v, 2);                      // C++20 — just do this
std::erase_if(v, [](int x){ return x > 5; });
```

Pre-C++20, that last one was the erase-remove idiom, which you'll see everywhere:

```cpp
v.erase(std::remove(v.begin(), v.end(), 2), v.end());
```

`std::remove` doesn't remove — it shuffles unwanted elements to the end and returns the new logical end. `erase` then trims. It's unintuitive and it's why `std::erase` was added.

**Node-based containers are stable.** References into a `map` or `list` survive other insertions, which is genuinely useful when you need long-lived handles.

## Strings

```cpp
#include <string>

std::string s = "hello";
s += " world";
s.substr(0, 5);
s.find("world");                       // std::string::npos if absent
s.c_str();                             // NUL-terminated, for C APIs
std::stoi("42"); std::to_string(42);

std::string_view sv = s;               // C++17 — non-owning view, no allocation
```

**`std::string_view` for read-only parameters:**

```cpp
void process(std::string_view s);      // accepts string, const char*, literal — no copy
```

But **it doesn't own**, so the same lifetime rules as a reference apply:

```cpp
std::string_view sv = get_string();    // DANGLING if that returns by value
std::string_view sv = "literal";       // fine — literals are static
```

Also: a `string_view` is not guaranteed NUL-terminated, so you can't pass `.data()` to a C API expecting a C string.

## Choosing

| Need | Use |
|---|---|
| Almost anything | `std::vector` |
| Fixed size, known at compile time | `std::array` |
| Push/pop at both ends | `std::deque` |
| Key → value, fast | `std::unordered_map` |
| Key → value, sorted or range queries | `std::map` |
| Membership test | `unordered_set` |
| Stable references across insertion | `list`, `map`, `deque` |
| Top-N / priority | `priority_queue` |
| Read-only string parameter | `std::string_view` |
| Read-only array parameter | `std::span` (C++20) |

---

## Related
- [[languages/05-cpp/10-iterators-and-algorithms|Iterators and Algorithms]] — what operates on these
- [[foundations/dsa/04-data-structures/03-hash-maps|Hash Maps]] and [[foundations/dsa/04-data-structures/08-heaps|Heaps]] — what these are underneath
- [[languages/03-rust/11-collections-and-iterators|Rust: Collections]] — the same set, with invalidation made impossible
- [[languages/05-cpp/README|C++ course map]]
