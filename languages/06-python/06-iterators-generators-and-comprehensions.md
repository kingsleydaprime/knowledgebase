# Iterators, Generators and Comprehensions

> Intermediate Python · Self-study lesson on the mechanism behind `for`, suspended functions, and processing data one item at a time.

## 1. Before you begin

### Prerequisites

You should be able to write functions with parameters and `return`, use `for` and `while`, work with lists and tuples, and read basic `if` and `try`/`except` statements. The file example also uses `with open(...)` to close a file reliably; see [[languages/06-python/07-decorators-and-context-managers|context managers]] if that syntax is unfamiliar.

You need Python 3 and a terminal. All examples use only the standard library; no packages or downloaded data are required. Run scripts without `-O`, which disables assertions.

### Learning outcomes

By the end, you should be able to:

- Distinguish an iterable from an iterator, and predict what a second traversal will do.
- Trace `next()` through a generator, including suspension and exhaustion.
- Choose between a comprehension, a generator expression, and a generator function.
- Build a file-processing pipeline with explicit resource ownership.
- Implement and test a lazy running-total generator independently.
- Explain when materialising data is preferable to streaming it.

Study sections 2–7 first. Section 8 is an optional extension reference; sections 9–11 contain hints, answers, and completion checks.

## 2. Why process one item at a time?

Imagine checking a stack of delivery receipts for failed deliveries. You can copy every receipt into a second stack before counting failures, or inspect each receipt, update a counter, and move on. If you only need the count, the second stack does not help.

The same choice appears when reading a log file larger than available memory. A list of every line retains the whole input; a streaming calculation can retain only the current line and a small amount of working state. This is a memory and control-flow choice, not a promise of faster execution. A single very large line, retained results, or a buffering stage can still use substantial memory.

### Small glossary

| Term                | Plain-language meaning                                                              | Python example                     |
| :------------------ | :---------------------------------------------------------------------------------- | :--------------------------------- |
| Iterable            | An object from which you can request an iterator.                                   | A list, a `range`, or a generator. |
| Iterator            | A cursor that remembers progress and supplies the next value.                       | `iter([10, 20])`.                  |
| Consume             | Request values, advancing that cursor.                                              | `next(cursor)` or `list(cursor)`.  |
| Exhausted           | No values remain; the iterator raises `StopIteration`.                              | The cursor after its last value.   |
| Eager / materialise | Compute and retain results now in a collection.                                     | `list(cursor)`.                    |
| Lazy                | Produce results when the consumer requests them.                                    | A generator expression.            |
| Generator           | An iterator created by a function containing `yield`, or by a generator expression. | `countdown(3)` below.              |

An iterable is not necessarily repeatable: every iterator is also iterable. A list normally gives you a fresh cursor each time you call `iter(list_object)`. An iterator returns itself from `iter(iterator)` and continues from its current position. Reusing an exhausted generator does not restart it; call its generator function again to obtain a new one.

## 3. The mechanism: `iter()`, `next()`, and `yield`

### The iterator protocol

A protocol is a small set of operations an object agrees to support:

- An iterable normally implements `__iter__()` to return an iterator.
- An iterator implements `__iter__()` returning itself, and `__next__()` returning one item or raising `StopIteration`.
- Use the built-ins `iter()` and `next()` rather than calling these special methods directly. Python also supports a legacy sequence fallback for `iter()` using integer `__getitem__()` access starting at zero.

Conceptual fragment — this expands the essential behaviour of `for item in items`; `items` and `process` stand for your own input and loop body. It is not a standalone script.

```python
cursor = iter(items)
while True:
    try:
        item = next(cursor)
    except StopIteration:
        break
    process(item)
```

The `try` covers fetching, not processing: an error in `process` should not be mistaken for normal exhaustion. A `for` loop handles this exhaustion for you.

### A generator is a suspended function

Calling a generator function creates a generator object without executing its body. Argument expressions are still evaluated at the call. When you request a value, the body runs until `yield`, hands back that value, and suspends. Local variables and the execution position remain available for the next request; this is not a deep copy of objects referenced by those variables.

Unlike `return`, `yield` allows execution to continue later. Falling off the end, or using a bare `return`, finishes the generator. Do not manually raise `StopIteration` inside a generator to end it.

Runnable example — save this entire block as `iterator_trace.py` in a scratch directory and run `python3 iterator_trace.py`.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1


values = [10, 20]
cursor = iter(values)
assert iter(cursor) is cursor
assert next(cursor) == 10
assert list(cursor) == [20]
assert list(cursor) == []
assert list(values) == [10, 20]
assert list(values) == [10, 20]

g = countdown(3)
assert iter(g) is g
assert next(g) == 3
assert next(g) == 2
assert next(g) == 1
try:
    next(g)
except StopIteration:
    pass
else:
    raise AssertionError("countdown should be exhausted")
assert list(g) == []
assert list(countdown(3)) == [3, 2, 1]
assert list(countdown(0)) == []
print("iterator trace: all assertions passed")
```

Trace the generator independently of the assertions:

| Action             | Work performed                                         | Result                        | State after the action                                       |
| :----------------- | :----------------------------------------------------- | :---------------------------- | :----------------------------------------------------------- |
| `g = countdown(3)` | Create generator; body has not started.                | Generator object.             | Ready to start with argument `n = 3`.                        |
| First `next(g)`    | Test `n > 0`; reach `yield n`.                         | `3`                           | Suspended at `yield`, with `n = 3`; subtraction has not run. |
| Second `next(g)`   | Resume after `yield`; subtract to `2`; loop and yield. | `2`                           | Suspended with `n = 2`.                                      |
| Third `next(g)`    | Subtract to `1`; loop and yield.                       | `1`                           | Suspended with `n = 1`; not yet exhausted.                   |
| Fourth `next(g)`   | Subtract to `0`; loop condition fails; function ends.  | Raises `StopIteration`.       | Exhausted.                                                   |
| Another `next(g)`  | No body execution.                                     | Raises `StopIteration` again. | Still exhausted.                                             |

Before continuing, explain why the generator is not yet exhausted immediately after yielding `1`.

## 4. Comprehensions versus generator expressions

A comprehension describes a transformation, an input traversal, and an optional filter. Read `[x * x for x in numbers if x > 0]` as: “for each number, keep it if positive, then square it.” The filter runs before the result expression for each item.

| Form                           | Result     | When work happens | Useful when                                                           |
| :----------------------------- | :--------- | :---------------- | :-------------------------------------------------------------------- |
| `[expression for x in source]` | List       | Immediately       | You need order, indexing, or repeated traversal.                      |
| `{expression for x in source}` | Set        | Immediately       | You need unique values.                                               |
| `{key: value for x in source}` | Dictionary | Immediately       | You need a lookup table; later duplicate keys replace earlier values. |
| `(expression for x in source)` | Generator  | As consumed       | You need one pass without retaining every result.                     |

A generator expression evaluates its leftmost iterable expression and obtains its iterator when created. Its per-item work is deferred. In particular, putting `open(...)` there opens the file immediately, even if no lines have been read. Manage the file with `with` instead of relying on cleanup later.

The next runnable example includes all four forms. With `sum(x.price for x in items)`, no extra parentheses are needed because the generator expression is the sole argument; this is a syntax illustration, not executable here because `items` is not defined.

`sum` consumes its entire finite input. `any` stops at the first truthy value; `all` stops at the first falsy value. With a list comprehension, every element has already been computed before either check starts. For empty inputs, `any` is `False`, `all` is `True`, and `sum` is `0`.

## 5. Worked example: a small log-processing pipeline

A pipeline connects processing stages: each stage requests input from the previous stage. Our contract is deliberately small: each nonblank log line contains exactly two whitespace-separated fields, an integer HTTP status and a path. Malformed lines raise `ValueError` during consumption; this is not a general web-server log parser.

We will strip lines, discard blanks, parse records, retain status `500`, and count the matches. A record is a `(status, path)` tuple. The fixture contains two errors, and the program creates and removes its own temporary directory.

Runnable example — save this entire block as `log_pipeline.py` and run `python3 log_pipeline.py`.

```python
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory


def parse(line):
    status, path = line.split()
    return int(status), path


def error_records(lines):
    cleaned = (line.strip() for line in lines)
    nonblank = (line for line in cleaned if line)
    records = (parse(line) for line in nonblank)
    return (record for record in records if record[0] == 500)


def read_lines(path):
    with open(path, encoding="utf-8") as source:
        for line in source:
            yield line.strip()


numbers = [-2, 0, 1, 2, 2, 3]
assert [x * x for x in numbers if x > 0] == [1, 4, 4, 9]
assert {x * x for x in numbers if x > 0} == {1, 4, 9}
assert {x: x * x for x in numbers if x > 0} == {1: 1, 2: 4, 3: 9}
squares = (x * x for x in numbers if x > 0)
assert sum(squares) == 18
assert list(squares) == []

cursor = iter([0, 7, 9])
assert any(x > 0 for x in cursor) is True
assert next(cursor) == 9  # any stopped after inspecting 7.
cursor = iter([2, 0, 9])
assert all(x > 0 for x in cursor) is False
assert next(cursor) == 9
assert any([]) is False
assert all([]) is True
assert sum([]) == 0

fixture = "200 /\n\n500 /checkout\n404 /missing\n500 /api\n"
with TemporaryDirectory() as directory:
    path = Path(directory) / "access.log"
    path.write_text(fixture, encoding="utf-8")

    with path.open(encoding="utf-8") as source:
        errors = error_records(source)
        assert next(errors) == (500, "/checkout")
        assert list(errors) == [(500, "/api")]
        assert list(errors) == []

    # A second pass needs a fresh source, not the exhausted generator.
    with path.open(encoding="utf-8") as source:
        error_count = sum(1 for _ in error_records(source))
    assert error_count == 2

    # read_lines owns its file; closing handles intentional early termination.
    with closing(read_lines(path)) as lines:
        assert next(lines) == "200 /"

bad_records = error_records(["not-a-status /broken"])
try:
    next(bad_records)
except ValueError:
    pass
else:
    raise AssertionError("bad status should fail during consumption")

print("log pipeline: all assertions passed; errors =", error_count)
```

### Why this works

1. Calling `error_records(source)` constructs stages but does not parse a line. Unlike `read_lines`, this is an ordinary function returning a generator expression; it has no `yield` in its own body.
2. The consumer's first `next(errors)` asks for a matching record. That request propagates backwards through parsing, blank filtering, and stripping to the file iterator.
3. `200 /` is parsed and rejected. The blank line is skipped before parsing. `500 /checkout` is parsed and yielded. One request for output can consume several input lines.
4. The next request resumes the stages at their saved positions. The `404` record is rejected, and the next `500` record reaches the consumer.
5. `sum(1 for _ in ...)` counts without storing all matching records. The `list(errors)` assertion above materialises a tiny remainder only for testing.

This resembles Unix pipes → [[devops/01-linux/12-bash-scripting|bash scripting]], but here the stages run synchronously in one Python process. Laziness does not create concurrency.

For `n` lines of bounded length, this pipeline takes O(n) total work and retains only a bounded number of intermediate records. More precisely, memory depends on current line/record size and file buffering, not just on the number of lines. A pipeline is not automatically buffer-free: sorting, collecting results, or using buffering tools changes that cost.

The outer `with` owns the file in the main example, so early `break` or exceptions still close it when the block exits. `read_lines` demonstrates the alternative where the generator owns the file: once started, it may keep that file open while suspended. `closing` calls its `close()` method on exit, causing its internal `with` to release the file. Do not rely on garbage collection, or assume that `break` closes a generator. Consume file-backed stages within the resource's lifetime.

## 6. Choosing the right representation

| Need or constraint                                      | Choice and consequence                                                                           |
| :------------------------------------------------------ | :----------------------------------------------------------------------------------------------- |
| Small results, multiple traversals, indexing, or length | Materialise with `list()`. It consumes the source and stores the results.                        |
| One-pass transformation or reduction                    | Generator expression for a simple expression; generator function for multi-step state.           |
| Large or infinite input                                 | Stream it, and bound consumption of infinite inputs explicitly.                                  |
| Two passes over a restartable source                    | Create fresh iterators or reopen the source. Changes to the source can change the second result. |
| Failure timing matters                                  | Generator body errors occur on consumption, possibly far from construction.                      |

Generators do not offer `len()`, indexing, or slicing. The iterator protocol itself does not require these operations, though a custom object could support additional methods. `list(generator)` does not reset it, and it will not finish on an infinite generator. Laziness is a useful trade-off, not a default virtue; it can add overhead and complicate resource lifetimes.

## 7. Practice: from a guided change to an independent generator

### Guided task

Work in scratch copies of the scripts, not in the lesson:

1. Before running `countdown(2)`, write down the result of each of three `next()` calls and the value of `n` at each suspension. Check your prediction by adapting the assertions.
2. Change the log example to select status `404` instead of `500`. Predict the matching tuple and total, then update the corresponding assertions and run it.
3. Restore status `500`. Explain why counting `errors` after `list(errors)` produces zero, and demonstrate a fresh file traversal that produces two.

### Independent task: running totals

Create `running_totals.py` and implement `running_totals(values)` without consulting the hints first. A running total is the sum of all values seen so far: input `[3, -1, 4]` yields `3`, then `2`, then `6`.

Contract:

- Accept an iterable of Python integers, including a single-use iterator or an infinite source. Input validation for non-integers is outside this task.
- Return an iterator that yields one cumulative sum per input item, preserving input order. Empty input yields nothing; there is no initial zero output.
- Do not consume input when the function is called. Each requested output consumes exactly one input item, with no look-ahead.
- Accept negative numbers and zero. Use no list conversion or other collection of prior inputs or outputs.
- Keep a constant number of working values: a total and the iteration state. Python integers can grow in size, so this is not a promise of constant bytes for arbitrarily large sums.
- Once exhausted, the returned iterator stays exhausted. Each separate call has its own total, initially zero.

Exercise contract tests — this block is not a core worked example and requires your implementation. Save it separately as `test_running_totals.py` alongside `running_totals.py`, then run `python3 test_running_totals.py`. Running it before implementing the function will fail; do not append it to the worked scripts.

```python
from itertools import count, islice

from running_totals import running_totals


assert list(running_totals([])) == []
assert list(running_totals([5])) == [5]
assert list(running_totals([3, -1, 4])) == [3, 2, 6]
assert list(running_totals([0, 0, -2, 2])) == [0, 0, -2, 0]
assert list(running_totals(iter([2, 5]))) == [2, 7]

seen = []


def tracked_source():
    for value in [2, -1, 4]:
        seen.append(value)
        yield value


result = running_totals(tracked_source())
assert seen == []
assert iter(result) is result
assert next(result) == 2
assert seen == [2]
assert next(result) == 1
assert seen == [2, -1]
assert list(result) == [5]
assert seen == [2, -1, 4]
assert list(result) == []

left = running_totals([1, 2])
right = running_totals([10, 20])
assert next(left) == 1
assert next(right) == 10
assert next(left) == 3
assert next(right) == 30

# islice bounds the test: never materialise this infinite source directly.
assert list(islice(running_totals(count(1)), 4)) == [1, 3, 6, 10]
print("running totals: all contract tests passed")
```

Here `count(1)` supplies integers forever, and `islice(iterator, 4)` requests at most four outputs. The next section expands on those tools. Besides passing tests, explain why your code cannot fetch a second input before returning the first output. Tests illustrate the contract; reviewing the implementation is still necessary to check the storage constraint.

## 8. Optional extensions: delegation and `itertools`

These tools extend the same pull-based model. They are not prerequisites for implementing the exercise.

### Delegation with `yield from`

`yield from iterable` forwards values from another iterable. For basic composition, it replaces a loop that yields each item. The example below concatenates two inputs; it does not recursively flatten nested data. More advanced generator communication is outside this lesson.

### Standard-library toolkit and its limits

| Tool                       | Purpose                                   | Important constraint                                                                      |
| :------------------------- | :---------------------------------------- | :---------------------------------------------------------------------------------------- |
| `chain(a, b, c)`           | Traverse inputs end to end.               | Does not restart consumed iterators.                                                      |
| `islice(source, 10)`       | Take up to ten items.                     | Advances the original iterator; it is not a non-consuming peek.                           |
| `islice(source, 100, 110)` | Skip 100 items, then yield up to ten.     | Skipped items are consumed too; no negative indices.                                      |
| `count(1)`                 | Generate `1, 2, 3, ...`.                  | Infinite; use a stopping condition.                                                       |
| `cycle(source)`            | Repeat input values.                      | Caches input values; an infinite source makes that cache grow. Empty input stays empty.   |
| `product(a, b)`            | Generate all pairs as nested loops would. | Pools its inputs in memory before producing combinations; inputs must be finite.          |
| `combinations(items, 2)`   | Choose pairs without replacement.         | Pools the input; combinations are based on positions, not distinct values.                |
| `groupby(source, key=f)`   | Group adjacent items with equal keys.     | Groups share the source iterator; consume each group before advancing the outer iterator. |
| `tee(source, 2)`           | Give two independently advancing views.   | Buffers values when one view falls behind; do not also advance the original source.       |

`groupby` does not require sorted input. For `A, A, B, A`, it produces three runs: `AA`, `B`, `A`. That is correct when you want consecutive runs, like Unix `uniq`. If you want a single group for every distinct key across the entire dataset, first make equal keys contiguous, usually with `sorted(data, key=f)` followed by `groupby(..., key=f)`. Sorting materialises the input and changes its order; it is not a streaming operation. Use the same key function for sorting and grouping.

Runnable example — save this entire block as `iterator_extensions.py` and run `python3 iterator_extensions.py`.

```python
from itertools import chain, combinations, count, cycle, groupby, islice, product, tee


def concatenate(a, b):
    yield from a
    yield from b


assert list(concatenate([1, 2], [3])) == [1, 2, 3]
assert list(chain([1], [2], [3])) == [1, 2, 3]
source = iter(range(6))
assert list(islice(source, 2)) == [0, 1]
assert next(source) == 2
assert list(islice(iter(range(120)), 100, 110)) == list(range(100, 110))
assert list(islice(count(1), 4)) == [1, 2, 3, 4]
assert list(islice(cycle(["a", "b"]), 5)) == ["a", "b", "a", "b", "a"]
assert list(product([1, 2], ["a", "b"])) == [
    (1, "a"), (1, "b"), (2, "a"), (2, "b")
]
assert list(combinations([1, 2, 3], 2)) == [(1, 2), (1, 3), (2, 3)]

rows = [("A", 1), ("A", 2), ("B", 3), ("A", 4)]


def category(row):
    return row[0]


runs = [(key, list(group)) for key, group in groupby(rows, key=category)]
assert runs == [("A", [("A", 1), ("A", 2)]), ("B", [("B", 3)]), ("A", [("A", 4)])]
groups = [
    (key, list(group))
    for key, group in groupby(sorted(rows, key=category), key=category)
]
assert groups == [("A", [("A", 1), ("A", 2), ("A", 4)]), ("B", [("B", 3)])]

fast, slow = tee(iter([10, 20, 30]), 2)
assert next(fast) == 10
assert next(fast) == 20  # tee must retain these values for slow.
assert list(slow) == [10, 20, 30]
assert list(fast) == [30]
print("iterator extensions: all assertions passed")
```

`tee` is not a free replacement for a list: if one consumer reads everything before the other starts, the buffer may retain the entire stream. Materialising a small dataset is often clearer. Likewise, use `islice` rather than `gen[:10]` on a generator, but remember that sampling changes the generator's position.

## 9. Hints — read only after attempting the tasks

### Guided-task hints

- The subtraction in `countdown` happens after resumption, not before suspension.
- Selecting a different status changes the final filter, not how lines are parsed.
- A generator is a cursor, not a saved query result. Ask which object owns the source and whether that source is still open.

### Independent-task hints

1. Start with an ordinary loop that maintains `total = 0` and updates it for each value.
2. Replace the step that would append a total to a list with a step that yields it.
3. Place the update before suspension so the output includes the current item. Let the loop's natural end finish the generator.
4. Keep state local to the function; shared state would cause the interleaved `left` and `right` tests to interfere.

## 10. Conceptual answers and self-assessment

Attempt these questions before reading the answers below:

1. Why can a list be traversed twice while a generator object cannot restart itself?
2. After `countdown(3)` yields `1`, why does it take another request to finish?
3. What does the first request for an error record consume in the fixture? What changes if there are no errors?
4. Does `islice` let you inspect values without changing the source position?
5. When would `groupby` legitimately produce multiple groups with the same key?
6. What invariant makes a running-total generator correct? An invariant is a statement that remains true at a chosen point on every iteration.

### Answers

1. Each traversal of a list can use a fresh iterator over the retained elements. A generator object holds one advancing execution state. It is itself iterable, but that does not make it repeatable. A new generator function call creates a separate state.
2. It is suspended at `yield n`. The next request runs `n -= 1`, observes zero, and exits the loop. Only then is it exhausted. For the guided `countdown(2)` task, the requests yield `2`, yield `1`, then raise `StopIteration`.
3. It consumes `200 /`, the blank line, and `500 /checkout`. If there are no errors, even the first request must scan to the end before reporting exhaustion. With a `404` filter, the sole matching tuple is `(404, "/missing")` and the count is one.
4. No. It consumes yielded and skipped items. Reuse the source only if advancing it is intended, or create a fresh traversal if the source supports that.
5. When equal keys occur in separated runs, as with `A, A, B, A`. Sort by the same key only when you want global grouping rather than original-order runs.
6. Immediately before each yield, the total equals the sum of exactly the inputs consumed so far, and the next input has not been requested. Starting at zero and adding one input per iteration preserves that statement. An empty input never enters the loop and produces no output.

For the independent task, use this invariant to explain your implementation rather than treating the tests as the entire specification. A materialised list of the right numbers would still violate the laziness contract.

## 11. Completion criteria

- [ ] I can explain iterable versus iterator without claiming that every iterable is repeatable.
- [ ] I can reproduce the `next()`/`yield` trace, including the final exhaustion request.
- [ ] Both core scripts run and print their assertion-success messages.
- [ ] I completed the guided status-filter change and checked its predicted result.
- [ ] My independent implementation passes `python3 test_running_totals.py` and I can justify its no-look-ahead and storage properties.
- [ ] I can explain where parsing errors occur and who closes the log file after early termination.
- [ ] I can choose between a list and a generator for a concrete task and explain the trade-off.
- [ ] If studying the extensions, I ran their script and can explain `groupby` runs and `tee` buffering.

## Related

- [[languages/06-python/03-built-in-types-and-collections|built-in types]] — the eager versions
- [[languages/06-python/12-concurrency-and-the-gil|concurrency]] — `async` generators
- [[languages/06-python/07-decorators-and-context-managers|context managers]] — the `with` in `read_lines`
- [[dsa/01-loops-and-what-they-cost|loops and what they cost]] — what iteration costs, and the hidden loops behind `in`

## References

- [Python tutorial: iterators and generators](https://docs.python.org/3/tutorial/classes.html#iterators)
- [Python tutorial: list comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [Python expression reference: generator expressions](https://docs.python.org/3/reference/expressions.html#generator-expressions)
- [Python standard library: itertools](https://docs.python.org/3/library/itertools.html)
