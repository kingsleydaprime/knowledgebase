# Build Your Own Compressor

> **[Intermediate]** · Huffman coding → LZ77 → DEFLATE → a real `.gz` file. **A weekend, and `gunzip` decompresses your output.**

## What you're building

**A compressor that produces genuine gzip files.** Not a gzip-like format, not a toy container — a byte stream that the `gunzip` already installed on your machine reads without complaint, and that round-trips to the original file exactly.

**And what you're deliberately not:** beating `gzip -9` on ratio, implementing Brotli or Zstandard, or going fast. **The target is the format's correctness, because that is what is verifiable**, and verifiability against a real tool is what makes this guide worth doing.

**This is the smallest project in the folder with the strongest ending.** The whole thing is a weekend, and `information-theory/` currently has nowhere for its nine notes to go.

## What you need first

- **Entropy, and what it is a limit on** — this guide is the applied half of that note → [[information-theory/02-entropy-joint-conditional-and-mutual|entropy]]
- **Source coding, prefix codes and the Kraft inequality** → [[information-theory/03-source-coding-and-compression|source coding and compression]]
- **A priority queue**, for building the Huffman tree → [[dsa/02-data-structures/08-heaps|heaps]]
- **Hash tables**, for finding matches → [[dsa/02-data-structures/03-hash-maps|hash maps]]
- **Comfort with bit manipulation and byte order** → [[mathematics/01-core/01-numbers/01-number-bases/02-binary|binary]]

**Any language works.** C and Rust are the natural fit for the bit twiddling. Python is perfectly good for the whole thing and lets you check yourself against `zlib` in the same process, which is genuinely useful.

## The build order

**1. Measure the entropy first, before writing any compressor.**
Count symbol frequencies in your test file and compute $H = -\sum p_i \log_2 p_i$ bits per symbol. Multiply by the file length.

**That number is the floor for any coder that treats bytes independently** — and knowing it in advance turns the rest of the project from guesswork into measurement. For English text it is usually around 4.5 bits per byte, so about 56% of the original size.
*Works when:* you can state, for your test file, the size no Huffman coder can beat.

**2. A bit writer and a bit reader.**
Everything downstream is built on these and everyone underestimates them. Accumulate bits into a buffer, flush whole bytes, and pad the final byte.
*Works when:* writing the bit sequence `1, 01, 001, 0001` and reading it back gives the same sequence. **Write this test. You will come back to it.**

**3. Huffman coding.**
Put every symbol in a priority queue keyed by frequency, repeatedly merge the two smallest into a parent, and the tree that remains gives each symbol a prefix-free code whose length is its depth. Frequent bytes get short codes.
*Works when:* your compressed size lands just above the entropy floor from step 1 — **and if it lands below, your bit writer is losing bits.**

**4. Canonical Huffman, so you can transmit the tree cheaply.**
The decoder needs your code table, and shipping a tree is wasteful. **If both sides agree to sort symbols by code length and then by symbol value, the codes can be reconstructed from the lengths alone.** So you transmit only a list of lengths.

This is not an optimisation you can skip — DEFLATE requires it, and it is a small, satisfying piece of code.
*Works when:* your decoder rebuilds an identical code table from lengths only.

**5. LZ77 — a different model entirely.**
Huffman cannot beat the entropy floor because it treats each byte independently. LZ77 changes the model: replace a repeated run with a **back-reference** to where it appeared before, as a `(length, distance)` pair. `the cat sat on the mat` becomes literals plus "go back 15 bytes and copy 4".

Keep a 32 KB sliding window. Find candidate matches by hashing the next **three** bytes into a chain of previous positions with the same hash, then extend the best candidate — matches run to 258 bytes.
*Works when:* a file of one repeated sentence compresses to almost nothing, and your output decompresses correctly with a decoder you wrote.

**6. Put them together — that combination is DEFLATE.**
LZ77 first, then Huffman over the result. Literals and match lengths share one alphabet of 0–285 — values 0–255 are literal bytes, 256 means end-of-block, and 257–285 encode length ranges with **extra bits** following. Distances use a second alphabet of 0–29, also with extra bits.
*Works when:* both stages run in sequence and you can decode your own output.

**7. Emit a fixed-Huffman block, and get to a valid file fastest.**
DEFLATE has three block types: **stored** (raw, for incompressible data), **fixed** (a code table defined by the specification, so you transmit none), and **dynamic** (your own table). **Do fixed first.** It skips the fiddliest part of the format and gets you to something real in an afternoon.
*Works when:* your decoder handles all three types.

**8. Wrap it in the gzip container.**
Ten bytes of header, the deflate stream, then eight bytes of trailer:

```
1f 8b        magic
08           compression method: deflate
00           flags
xx xx xx xx  mtime, little-endian
00           extra flags
03           OS (3 = Unix)
...          the deflate data
xx xx xx xx  CRC-32 of the uncompressed data, little-endian
xx xx xx xx  original size mod 2^32, little-endian
```
The checksum is CRC-32 with the reflected polynomial `0xEDB88320`, which is thirty lines with a lookup table.
*Works when:*
```bash
./mycompress input.txt > out.gz
gunzip -c out.gz | diff - input.txt && echo "IT WORKS"
```
**That `diff` producing nothing is the whole project.** A tool you did not write, which predates you, read a file you generated byte by byte and agreed with it.

**9. Dynamic Huffman blocks.**
Now the fiddly part, and the only real ratio win left. You transmit your own code lengths — but those lengths are themselves compressed, with a **third** Huffman code over a code-length alphabet that includes run-length symbols 16, 17 and 18 for repeats. A Huffman code describing a Huffman code.
*Works when:* your output is within ~10% of `gzip -9` on the Canterbury corpus, and still decompresses.

**10. Optional: measure where the wins came from.**
Compress the same file three ways — Huffman alone, LZ77 alone, both — and tabulate. **The result is the lesson of the whole guide**, and it is not the one most people expect.

## The parts that will bite you

**DEFLATE's bit order is mixed, deliberately.** Values other than Huffman codes are packed **least-significant bit first**; Huffman codes are packed **most-significant bit first**. This is stated in one sentence of RFC 1951 and it is where nearly everyone loses their first evening. Your bit writer needs both modes.

**Overlapping back-references are legal and useful.** A match at distance 1 with length 200 means "repeat the previous byte 200 times" — the copy reads bytes it is itself writing. **Your decoder must copy one byte at a time**; a `memcpy` gets the right answer only by accident and usually not at all.

**Incompressible input must not be allowed to expand much.** Random data grows under any coder, which is why the *stored* block type exists. Encode a block three ways and pick the smallest; without that, your compressor on a `.jpg` is a compressor that makes files bigger.

**Two distinct checksums exist.** gzip uses CRC-32; zlib streams use Adler-32. Reaching for the wrong one gives you a file that decodes perfectly and then fails its integrity check at the very last byte.

**The hash chain determines everything about your speed and ratio.** Search too few candidates and you miss matches; search all of them and a 10 MB file takes minutes. This single tunable is what `gzip -1` through `gzip -9` actually changes.

**Lazy matching is worth the twenty lines.** Before committing to a match at position `i`, check whether position `i+1` has a longer one; if it does, emit a literal and take the better match. It is a small change with a surprisingly large effect.

## How to know it works

1. **`gunzip` round-trips it**, byte-identical, for text, source code, a binary and an already-compressed file
2. **`python3 -c "import zlib, sys; sys.stdout.buffer.write(zlib.decompress(sys.stdin.buffer.read(), 31))"`** as a second independent decoder — two implementations agreeing is much stronger evidence than one
3. **Compression ratios against `gzip -9`** on a standard corpus, tabulated per file type
4. **Your measured Huffman-only size sits just above the entropy floor** you computed in step 1
5. **Pathological inputs:** an empty file, one byte, a file of a single repeated byte, and 10 MB from `/dev/urandom`

## Where to stop

**Stop once dynamic blocks work and you have the comparison table.**

**Not worth it here:** arithmetic or range coding (genuinely interesting and genuinely a second project), the Burrows–Wheeler transform behind bzip2, Zstandard's finite-state entropy, or any optimisation for speed.

**You will have learned** why compression has a floor and what sets it, that beating that floor means changing your *model* rather than your *code*, and why a format from 1996 is still what your browser negotiates on every request. **The entropy note stops being a formula and becomes a number you have watched a program fail to beat** — and [[information-theory/index|information theory]] afterwards reads as engineering rather than mathematics.

## Related

- [[information-theory/03-source-coding-and-compression|Source coding and compression]] — the reference note for this guide
- [[information-theory/02-entropy-joint-conditional-and-mutual|Entropy]] — the limit you will measure against
- [[dsa/03-algorithms/10-greedy-algorithms|Greedy algorithms]] — Huffman's tree construction is the classic proof-carrying greedy algorithm
- [[build-your-own-shit/06-your-own-database|Your Own Database]] — where you would use this next, on pages
- [[build-your-own-shit/index|Build Your Own Shit index]]

*Source: [reference] — build guide, Sep 2026.*
