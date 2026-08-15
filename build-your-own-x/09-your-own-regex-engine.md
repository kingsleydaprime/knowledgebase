# Your Own Regex Engine

**[Intermediate]** — Compile a pattern into an automaton and run it. **A few hundred lines, one evening, and it makes an entire chapter of theory concrete.**

## What you're building

**A regular expression engine** that compiles a pattern into an NFA, optionally determinises it, and matches input in **guaranteed linear time** — no backtracking, no catastrophic blowup.

**By the end you'll have** `match(pattern, text)` supporting concatenation, alternation `|`, Kleene star `*`, `+`, `?`, character classes, anchors, and capture groups.

**What you're deliberately not building:** backreferences (`\1`), lookahead/lookbehind, or lazy quantifiers. **Not because they're too hard — because they're not regular.** They're exactly what forces real engines into exponential backtracking, and leaving them out is what buys you the linear-time guarantee. → [[foundations/theory-of-computation/03-regular-languages|Regular Languages]]

> **This is the one build guide where the theory tells you the answer in advance.** Kleene's theorem says regex ≡ NFA ≡ DFA, and the constructions are known and small. **You're not inventing an algorithm; you're implementing three that fit on a page each** — and watching them turn out to actually work is the point.

## What you need first

**Required:**
- **Recursive descent parsing** — the pattern is a small grammar → [[foundations/compilers/03-parsing|Parsing]]
- **Graphs and traversal** — an NFA is a graph, and simulation is a BFS → [[foundations/dsa/05-algorithms/03-bfs|BFS]]
- **Sets** — the subset construction is literally sets of states

**Strongly recommended, and it's what makes this build land:**
- [[foundations/theory-of-computation/02-finite-automata|Finite Automata]] — Thompson's construction and the subset construction are described there
- [[foundations/theory-of-computation/03-regular-languages|Regular Languages]] — why backreferences change the complexity class

**Honest note:** you can build this without reading either, and you'll re-derive worse versions of both constructions. **Read those two notes first; they're an hour.**

## The build order

### Milestone 1 — Match a literal string

**No metacharacters.** `match("abc", "xxabcxx")` → true.

**Just to get the interface, the test harness, and the loop over start positions in place.**

**Test:** literals match where they occur and nowhere else. Empty pattern matches everything.

### Milestone 2 — A parser for the pattern

**Pattern → syntax tree.** The grammar, in precedence order (lowest first):

```
alternation := concat ('|' concat)*
concat      := repeat*
repeat      := atom ('*' | '+' | '?')?
atom        := CHAR | '.' | '(' alternation ')' | class
class       := '[' '^'? (CHAR | CHAR '-' CHAR)* ']'
```

**Recursive descent, one function per level.** ~80 lines.

> **Note the grammar encodes precedence exactly as an arithmetic grammar does** — alternation binds loosest, then concatenation, then the postfix quantifiers. **Same structure as `E → E + T`.** → [[foundations/theory-of-computation/04-context-free-languages|Context-Free Languages]]

**Test:** parse `a(b|c)*d` and print the tree. Confirm `ab|cd` parses as `(ab)|(cd)`, not `a(b|c)d`.

### Milestone 3 — Thompson's construction

**Syntax tree → NFA.** **The heart of the project, and it's beautifully small.**

Each node type builds a fragment with one start state and one dangling out-arrow:

```
 literal 'a':     ──a──►○

 concat  ab:      ──a──►──b──►○

 alternation a|b:      ┌─ε─►──a──►─ε─┐
                  ──►○─┤             ├─►○
                       └─ε─►──b──►─ε─┘

 star    a*:      ──►○◄─┐
                    │ε  │ε
                    ▼   │
                    ──a──
```

**Represent a state as:** a transition character (or ε, or "split"), and one or two out-pointers.

**~60 lines for the whole construction**, and it's a fold over the syntax tree.

**Test:** build the NFA for `a(b|c)*` and count states. Thompson's produces **at most 2× the pattern length** — verify that bound holds.

### Milestone 4 — Simulate the NFA

**The milestone that gives you the linear-time guarantee.**

```
current = ε-closure({start})
for each char c in input:
    next = ∅
    for each state s in current:
        if s transitions on c:
            next += ε-closure(s.out)
    current = next
    if accept ∈ current: record a match
```

> **The key idea: track the *set* of states you could be in, all at once.** You never backtrack, because you never commit to a choice — you follow every alternative simultaneously.
>
> **That's why it's $O(nm)$** — $n$ input characters × $m$ states — **and why it cannot blow up.** A backtracking engine explores paths one at a time and re-explores on failure; this explores them in parallel and never repeats work.

**Test:** `(a+)+b` against 30 `a`s followed by `X`. **A backtracking engine (Python's `re`, PCRE) hangs. Yours returns instantly.** Time both — **this is the single most satisfying moment in the build.**

### Milestone 5 — Character classes, anchors, dot

`[a-z]`, `[^0-9]`, `.`, `^`, `$`.

**Classes are just a transition that tests a predicate** rather than equality — a small change to the state representation, and it doesn't affect the simulation at all.

**Anchors are conditions on position**, not characters. `^` matches only at offset 0.

**Test:** `^[a-z]+@[a-z]+\.[a-z]{2,}$` on a handful of strings. (Not a correct email validator — [[foundations/theory-of-computation/03-regular-languages|nothing is]] — but a good exercise.)

### Milestone 6 — Subset construction (NFA → DFA)

**Each DFA state is a *set* of NFA states.** Build them lazily as you encounter them, cache in a hash map.

**Now matching is one table lookup per input character** — $O(n)$, independent of pattern size.

**Test:** verify the DFA and NFA agree on a corpus of random patterns and inputs. **Then measure: the DFA should be several times faster on long inputs.**

**Watch for the exponential blowup.** Construct `(a|b)*a(a|b){20}` and count DFA states — **this is the $2^n$ case the theory warns about**, and seeing it happen is worth the five minutes.

> **The production answer is a *lazy* DFA with a bounded cache** — build states on demand, and when the cache fills, flush it and continue. **You get DFA speed with NFA memory bounds.** That's exactly what RE2 and Rust's `regex` do, and now you know why.

### Milestone 7 — Capture groups

**The hardest remaining piece.** Track submatch boundaries through the simulation.

**The straightforward approach:** carry a vector of capture positions alongside each state in the current set. **Costs memory, and it's how Pike's VM works** — Thompson's construction plus capture tracking.

**Test:** `(\d{4})-(\d{2})-(\d{2})` against a date, extracting all three groups.

**Where to stop if you're done:** this milestone is genuinely fiddly, and **milestones 1–6 already contain the whole lesson.** Skipping 7 is a legitimate choice.

## Per-language toolkit

| Language | Notes |
|---|---|
| **C** | The classic. Russ Cox's articles use ~400 lines of C. Manual state allocation is instructive |
| **Rust** | Enums model the syntax tree perfectly; `HashSet` for state sets. Compare against the `regex` crate, which is this design industrialised |
| **Go** | Straightforward; `regexp` in the stdlib is RE2 — **read its source afterwards** |
| **Python** | Fastest to prototype. **Then benchmark against `re` on the pathological case and enjoy the result** |
| **JS/TS** | Fine; note that JS's own `RegExp` is backtracking, so the contrast is available in the same runtime |
| **C++** | `std::variant` for nodes; `std::bitset` for state sets is a genuinely fast representation |

**No libraries needed for any of it.** That's part of the appeal — it's pure algorithm.

## The parts that will bite you

**ε-closure loops.** `(a*)*` creates ε-cycles. **Your closure computation must track visited states** or it recurses forever. This will happen on roughly your third test.

**Empty matches.** `a*` matches the empty string at every position. **Decide your semantics early** — most engines advance one character after an empty match to guarantee progress, and without that a global search loops forever.

**Greedy vs lazy.** Thompson's is naturally "match any", not "match longest". **For leftmost-longest semantics you must keep scanning after reaching an accept state** and record the last accept position.

**Character class parsing.** `[]]`, `[a-]`, `[^]]` are all legal and irregular. **Handle `]` as the first character specially**, as the standard does.

**Off-by-one on anchors.** `$` matches at end-of-input, which is *after* the last character.

**State explosion in the DFA.** Expected — bound the cache rather than trying to prevent it.

## How to know it works

**Differential testing against a real engine** is the strongest signal available here, and it's easy:

```python
import re, random
for _ in range(100000):
    pattern = random_pattern()      # from your supported subset
    text = random_text()
    assert my_match(pattern, text) == bool(re.search(pattern, text))
```

**Generate random patterns and inputs, compare against your language's stdlib.** Any disagreement is a bug in one of you, and it's almost always you. **This finds edge cases you'd never write by hand.**

**The performance test is the headline:** `(a+)+b` against `"a" * 30 + "X"`.

| Engine | Time |
|---|---|
| Python `re` / PCRE | **minutes to hours** |
| Yours | **microseconds** |

**That single comparison is the whole argument** for why RE2, Go's `regexp` and Rust's `regex` exist, and why you should never run a user-supplied pattern through a backtracking engine. → [[foundations/theory-of-computation/02-finite-automata|ReDoS]]

**Also test:** the empty pattern, patterns matching empty strings, nested stars, long alternations, and Unicode if you're feeling brave (it's a genuine complication — character classes over code points, not bytes).

## Where to stop

**Stop after milestone 6.** You'll have a linear-time engine that demonstrably beats production backtracking engines on adversarial input, and you'll have implemented three classical constructions that are now permanently concrete.

**Reasonable extensions if you're enjoying it:**

- **Capture groups** (milestone 7) — the Pike VM
- **A lazy DFA with a bounded cache** — the actual production design
- **Leftmost-longest semantics** properly
- **A bytecode VM** instead of a graph walk — compile to instructions (`char`, `split`, `jmp`, `match`) and write an interpreter. **Russ Cox's series covers this**, and it connects directly to [[build-your-own-x/04-your-own-language|your own language]]

**Don't build:** backreferences (not regular, needs backtracking, defeats the purpose), full PCRE compatibility (enormous), or Unicode property classes (a data problem, not an algorithm problem).

**The reference implementations to read afterwards:** **Russ Cox's "Regular Expression Matching Can Be Simple And Fast"** is the definitive article and short enough to read in one sitting. Then **RE2** or **Rust's `regex`** for how it's done in production.

---

## Related
- [[foundations/theory-of-computation/02-finite-automata|Finite Automata]] — the constructions, explained
- [[foundations/theory-of-computation/03-regular-languages|Regular Languages]] — why the limits are where they are
- [[foundations/compilers/02-lexical-analysis|Lexical Analysis]] — the same machinery, industrially
- [[build-your-own-x/README|build-your-own-x]]
