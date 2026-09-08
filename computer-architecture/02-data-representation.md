# Data Representation

**[Beginner → Intermediate]** — Two's complement, floating point, endianness, and alignment. What your data actually looks like in memory.

## Integers

**Unsigned** is plain binary: $n$ bits hold $0$ to $2^n - 1$.

**Signed uses two's complement**, and the reason is worth knowing.

$$\text{negate: invert all bits, add 1}$$

For 8-bit: $5 = 00000101$, so $-5 = 11111011$.

**Range is $-2^{n-1}$ to $2^{n-1}-1$** — asymmetric, one more negative than positive.

> **Why two's complement won over the alternatives:** there's **exactly one zero** (sign-magnitude and ones' complement both have $+0$ and $-0$), and **subtraction is just addition of the negation.** The same adder circuit handles signed and unsigned. **No separate hardware, no special cases** — it's a genuinely elegant piece of design.

**The asymmetry causes real bugs:**

```c
int x = INT_MIN;
abs(x)   // still INT_MIN — undefined behaviour
-x       // overflows
```

**$|{-2^{31}}|$ is not representable in 32 bits.** This has produced real CVEs.

### Overflow

**Unsigned overflow wraps**, and it's defined behaviour — modular arithmetic mod $2^n$.

**Signed overflow is undefined behaviour in C and C++.** Not "wraps", not "implementation-defined" — **undefined**, which means the optimiser may assume it never happens:

```c
if (x + 1 < x)   // optimised to `false` — signed overflow can't happen
```

**The check is deleted.** → [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]]

**Other languages choose differently:** Rust panics in debug and wraps in release (with explicit `wrapping_*`, `checked_*`, `saturating_*` methods); Java wraps, defined; Python has arbitrary precision integers and doesn't overflow at all.

**Classic overflow bugs:**

- **Ariane 5, 1996** — a 64-bit float converted to a 16-bit signed integer overflowed. **$370M rocket destroyed**
- **`(low + high) / 2`** in binary search overflows for large arrays. Java's `Arrays.binarySearch` carried this for nine years. **Use `low + (high - low) / 2`**
- **2038** — 32-bit `time_t` overflows on 19 January 2038

## Floating point

**IEEE 754**, and the format is worth being able to picture:

```
 float (32-bit):
 ┌─┬────────┬───────────────────────┐
 │S│  exp   │       mantissa        │
 └─┴────────┴───────────────────────┘
  1     8              23
```

$$\text{value} = (-1)^S \times 1.\text{mantissa} \times 2^{\text{exp}-127}$$

| | Bits | Precision | Range |
|---|---|---|---|
| `float` | 32 | ~7 digits | $10^{\pm38}$ |
| `double` | 64 | ~15 digits | $10^{\pm308}$ |
| `float16` | 16 | ~3 digits | $10^{\pm5}$ |
| `bfloat16` | 16 | ~2 digits | **$10^{\pm38}$** |

> **`bfloat16` is float32 with the mantissa truncated** — same exponent range, less precision. **That's exactly the right trade for neural networks**, where gradients span enormous ranges but individual values don't need precision. It's why it's the ML default. → [[ai-ml/02-ml-engineer/05-deep-learning/README|Deep Learning]]

### The things that surprise people

**$0.1 + 0.2 \neq 0.3$.**

**Not a bug.** 0.1 is not representable in binary — it's $1/10$, and 10 isn't a power of 2, exactly as $1/3$ isn't representable in decimal. The stored value is slightly off, and the errors compound.

$$\texttt{0.1 + 0.2 == 0.30000000000000004}$$

**Never compare floats with `==`.** Use a tolerance — and choose between absolute and relative depending on magnitude.

**Never use floats for money.** Use integer cents, or a decimal type. **Financial systems that used doubles have lost real money.**

**Addition is not associative:**

$$(10^{20} + 1) - 10^{20} = 0 \qquad 10^{20} + (1 - 10^{20}) = 1$$

**So the compiler cannot reorder float arithmetic** without changing results — which is why `-ffast-math` is dangerous, and why **parallel reductions give different answers depending on thread scheduling.** A real reproducibility problem in ML training.

**Special values:**

- **`NaN`** — and **`NaN != NaN`**, which is the only value not equal to itself. It breaks sorting comparators and hash lookups
- **`±Inf`** — from overflow or division by zero
- **`-0.0`** — equals `+0.0` but `1/(-0.0) == -Inf`
- **Denormals** — tiny values near zero that can be **10–100× slower** on some hardware, which is why audio code flushes them to zero

**Catastrophic cancellation** — subtracting nearly-equal numbers destroys precision. The classic fix is rewriting the quadratic formula to avoid it, and the general lesson is that **the algebra you learned isn't numerically equivalent in floating point.**

## Text

**ASCII** — 7 bits, 128 characters. English only.

**Unicode** assigns a **code point** to every character (over 149,000). **An encoding maps code points to bytes:**

| Encoding | Size | Notes |
|---|---|---|
| **UTF-8** | 1–4 bytes | **ASCII-compatible.** The web default, and the right choice |
| UTF-16 | 2 or 4 bytes | Java, C#, Windows, JS strings. Surrogate pairs |
| UTF-32 | 4 bytes | fixed width, wasteful |

**UTF-8 won because it's backwards compatible** — valid ASCII is valid UTF-8 — and self-synchronising: you can find character boundaries from any position.

> **The trap that catches everyone: "length" is ambiguous.** For "👨‍👩‍👧" — bytes: 18, UTF-16 units: 8, code points: 5, **user-perceived characters: 1.**
>
> **Never assume one byte is one character**, never index into a string by byte offset, and never truncate a string at a byte boundary. → [[languages/03-rust/02-language-fundamentals|Rust's string types]] make this distinction explicit and are unpopular for it, but they're right.

**Normalisation** matters for comparison: `é` can be one code point or `e` + combining accent. **Two strings that look identical can differ byte-for-byte.** Normalise (NFC) before comparing or hashing — this is a real security issue in username handling.

## Endianness

**The byte order of a multi-byte value.**

For `0x12345678` at address 100:

```
 Little-endian (x86, ARM default):    Big-endian (network order):
 100: 78  101: 56  102: 34  103: 12   100: 12  101: 34  102: 56  103: 78
```

**Little-endian** — least significant byte first. x86, ARM (usually), RISC-V.

**Big-endian** — most significant first. **Network byte order**, and some older architectures.

**Where it bites:**

- **Network protocols.** Always convert: `htons`, `htonl`, `ntohs`, `ntohl` → [[foundations/networking/03-ip-addressing-and-subnetting|IP]]
- **Binary file formats.** Specify the byte order or the file isn't portable
- **Casting a struct to bytes** and writing it out. Works on your machine, not necessarily elsewhere
- **Debugging a hex dump** — bytes appear "backwards" on little-endian, which is confusing the first hundred times

**Test it:**

```c
int x = 1;
bool little_endian = *(char*)&x == 1;
```

## Alignment and layout

**A type of size $n$ typically must sit at an address divisible by $n$.**

**Why:** memory is fetched in aligned blocks. **An unaligned access spans two blocks and needs two fetches** — or faults entirely on ARM and older architectures. x86 tolerates it with a penalty.

**The consequence is padding**, and it's why struct field order matters:

```c
struct Bad  { char a; int b; char c; };  // 12 bytes
//            a  ...pad3...  bbbb  c  ...pad3...

struct Good { int b; char a; char c; };  // 8 bytes
//            bbbb  a  c  pad2
```

> **Order fields largest-to-smallest and you get the packing for free.** On a struct allocated millions of times this is a real memory saving — and a real *cache* saving, which usually matters more. → [[foundations/computer-architecture/08-the-memory-hierarchy|Memory Hierarchy]]

**`#pragma pack(1)`** removes padding for wire formats — at the cost of unaligned access. **Use it for serialisation, not for hot data.**

**Cache line alignment** is the other side: two variables written by different cores should be on **different** 64-byte lines, or you get false sharing. → [[foundations/computer-architecture/11-multicore-and-memory-models|False Sharing]]

## Practical notes

**Use fixed-width types** in anything that crosses a boundary: `uint32_t`, not `int`. **`int` is 32 bits on most platforms and `long` is 32 on Windows and 64 on Linux** — a genuine portability trap.

**Prefer unsigned for bit manipulation**, since signed right-shift is implementation-defined and signed overflow is UB.

**Check for overflow explicitly** where it matters — `__builtin_add_overflow`, Rust's `checked_add`.

**Never use floats for money, or for equality, or for accumulating many values** without considering error. Kahan summation exists for the third case.

**Always UTF-8**, and never index strings by byte.

**Reorder struct fields** largest-first. Free memory savings.

**Sanitizers find these.** `-fsanitize=undefined` catches signed overflow, misaligned access and more at runtime. **Run your tests under it** — it's the cheapest bug-finding available. → [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]]

---

## Related
- [[languages/04-c/04-types-and-integers|C: Types and Integers]] — the language-level view
- [[foundations/computer-architecture/08-the-memory-hierarchy|The Memory Hierarchy]] — why layout matters so much
- [[foundations/computer-architecture/03-instruction-sets|Instruction Sets]] — what operates on this data
- [[foundations/computer-architecture/README|Architecture map]]
