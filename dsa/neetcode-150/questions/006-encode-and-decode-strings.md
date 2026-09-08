# Encode and Decode Strings

**LeetCode 271** · Arrays & Hashing · concept: [[foundations/programming-fundamentals/15-how-types-actually-work|data-types]]

## Problem

Design `encode(list[str]) -> str` and `decode(str) -> list[str]` so that a list of strings survives a round trip through a single string. The strings can contain **any** characters — including whatever delimiter you might be tempted to use.

```
["neet","code","love","you"]  --encode-->  some string  --decode-->  ["neet","code","love","you"]
```

## The trap — why a delimiter fails

The obvious idea is to join with a separator like `"#"` and split on it. It breaks the moment a string *contains* `"#"`: `["a#b", "c"]` encodes to `"a#b#c"`, which decodes to `["a", "b", "c"]` — wrong. **No delimiter is safe** if the payload can contain arbitrary characters. Escaping the delimiter works but is fiddly.

## The fix — length prefixing (optimal)

Prefix each string with its **length and a separator**: `<len>#<string>`. Now decoding never guesses where a string ends — it *reads the length*, then takes exactly that many characters. The `#` is unambiguous because everything before it is guaranteed to be digits (the length), so a `#` inside the payload can never be mistaken for a delimiter.

```python
def encode(strs):
    return "".join(f"{len(s)}#{s}" for s in strs)

def decode(s):
    res, i = [], 0
    while i < len(s):
        j = i
        while s[j] != "#":          # read digits until the separator
            j += 1
        length = int(s[i:j])        # the length prefix
        word = s[j + 1 : j + 1 + length]   # take exactly `length` chars
        res.append(word)
        i = j + 1 + length          # jump past this word to the next length prefix
    return res
```

```
["a#b", "c"]  -> encode -> "3#a#bc"... wait: "3#a#b" + "1#c" = "3#a#b1#c"
decode: read "3" -> take 3 chars "a#b"; read "1" -> take 1 char "c"  ✓
```

The embedded `#` in `"a#b"` is now harmless — decoding is driven by the count, not by scanning for separators.

## Complexity

| Operation | Time | Space |
|---|---|---|
| encode | O(N) total characters | O(N) |
| decode | O(N) | O(N) |

Both are linear in the total length of all strings — you touch each character a constant number of times.

## Key insight

**When a delimiter can appear in the data, prefix with a length instead.** "Read the count, then read exactly that many bytes" is *the* framing protocol — it's how HTTP `Content-Length`, TLV (type-length-value) encodings, and most network wire formats delimit variable-length fields. This problem is really a tiny serialization-format design exercise disguised as a string problem.

## Related
- concept: [[foundations/programming-fundamentals/15-how-types-actually-work|data-types]] — encoding and representation
- the same "length-prefix a serialization" idea shows up in [[03-hash-maps|hashing]]-based design problems
- prev: [[005-top-k-frequent-elements|Top K Frequent Elements]] · next: [[007-product-of-array-except-self|Product of Array Except Self]]
