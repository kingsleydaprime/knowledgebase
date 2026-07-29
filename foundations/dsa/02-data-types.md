# Data Types

A data type tells the language (and the machine underneath it) two things: how many bits to set aside for a value, and what those bits mean. The same 32 bits are a completely different thing depending on whether the type says "this is an integer" or "this is a float" — the bits don't carry meaning on their own, the type is what gives them meaning.

## Why it exists

Without types, a computer just sees bytes. Types let the compiler/interpreter:

- Allocate the right amount of memory up front (a fixed-size type like an `int32` always takes 4 bytes; the CPU can jump straight to any element in an array of them).
- Know which operations are legal (`"a" + 1` should behave differently — or fail — depending on what `"a"` and `1` actually are).
- Catch mistakes before they become bugs (adding a string to a number by accident).

## The core primitive types

Almost every language builds on some version of these:

| Type | What it holds | Typical size |
|---|---|---|
| Integer | Whole numbers | 4 or 8 bytes (fixed-width in most languages; Python ints are arbitrary-precision) |
| Float / double | Numbers with a fractional part | 4 or 8 bytes (IEEE 754) |
| Boolean | `true` / `false` | 1 byte (often stored as a whole word for alignment) |
| Character | A single character | 1–4 bytes depending on encoding |
| Null / None | The absence of a value | N/A — a marker, not a value |

Everything else — strings, arrays, objects, structs — is built out of these primitives combined with some structure (see [[03-data-type-classification|data-type-classification]] for how that split actually works).

## How it works under the hood

Take a 32-bit integer. In memory it's just 4 bytes: `00000000 00000000 00000000 00101010`. The type system is what tells the CPU "interpret these 32 bits as a two's-complement signed integer" instead of "interpret these as 4 separate ASCII characters" or "interpret this as an IEEE-754 float." Same bytes, different meaning, entirely dependent on the declared type.

This is also why type punning / unsafe casts are dangerous in languages like C — you can force the compiler to reinterpret those bits as the wrong type, and you'll get a value that "works" but means nothing.

## Static vs dynamic — the short version

- **Statically typed** (Java, C, Go, TypeScript): the type of a variable is fixed at compile time and checked before the program runs.
- **Dynamically typed** (Python, JavaScript, Ruby): the type lives with the *value*, not the variable — a variable can point to an int now and a string later, and the check happens at runtime.

Full breakdown of this and the other classification axes lives in [[03-data-type-classification|data-type-classification]].

## Gotchas

- **Integer overflow**: in fixed-width languages, `2147483647 + 1` silently wraps to `-2147483648` (32-bit signed int). Python sidesteps this entirely — ints grow arbitrarily, so this class of bug doesn't exist there, but it means you can't assume Python's int behaves like C's.
- **Float imprecision**: `0.1 + 0.2 != 0.3` in almost every language, because 0.1 and 0.2 can't be represented exactly in binary floating point. Never compare floats with `==`; compare within an epsilon.
- **Implicit coercion**: JavaScript's `"5" + 3` gives `"53"` (string concatenation) but `"5" - 3` gives `2` (numeric coercion). The rules for *when* coercion happens are inconsistent across operators — this is a classic source of bugs in loosely typed languages.

## Related
- [[03-data-type-classification|data-type-classification]]
- [[01-algorithms|algorithms]] — complexity analysis assumes primitive operations (comparisons, arithmetic) are O(1), which is really an assumption about fixed-width data types
