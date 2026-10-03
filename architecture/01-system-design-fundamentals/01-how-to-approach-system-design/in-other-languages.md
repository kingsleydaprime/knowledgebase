# How to Approach System Design in Other Languages

> **[Intermediate]** · A companion to [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|how to approach system design]], which estimates a game leaderboard's load and storage and then answers "what's my rank?" among millions of players with a Fenwick tree in about 20 steps. This page does the same in Python, Go, Java, Rust and C#, with the same numbers in every language. The method is language-free; what changes is the arithmetic underneath it. Numbers that fit easily in a JavaScript number overflow a 32-bit integer, printing "910" without an exponent takes a different trick in each language, and the Fenwick tree's `i & -i` needs rewriting where integers can't be negative.

## Before you start

You can already:

- Run the five-step design method and do a back-of-the-envelope estimate → [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|the main lesson]].
- Explain what a Fenwick tree stores and why its `rank` takes about log₂(maxScore) steps (same lesson).
- Run tests in at least one of the languages here.

After this lesson you will be able to:

1. Say which integer type an estimate needs in your language before it overflows, and what your language does when it does overflow.
2. Format a number to two significant figures without an exponent, and round a half the way you mean to.
3. Write the Fenwick tree's lowest-set-bit step in a language with unsigned sizes.

## The kid version

Five friends each do the same sum on a different calculator. Four get 173,600,000,000. One gets 1,801,308,160, and the calculator doesn't beep or flash; it just shows the wrong number with full confidence. That calculator has only ten digits of room and quietly threw the rest away. Before trusting an estimate, know how much room your calculator has.

**Where the analogy stops working.** A calculator usually shows an error when a number won't fit. Most languages don't: Java and C# wrap round silently, Rust panics only in a debug build, and Go silently wraps too, but its `int` is 64 bits on most machines, so you rarely see it. Only Python's integers simply grow.

## 1. The tools, by ecosystem

| Language | Integer for big estimates | What overflow does | Round half up | Two significant figures |
|---|---|---|---|---|
| TypeScript | `number` (exact to 2⁵³) | loses precision past 2⁵³ | `Math.round` | `toPrecision(2)` |
| Python | `int` | can't happen: ints grow | `math.floor(x + 0.5)` (`round` goes to even) | `f"{x:.2g}"`, then reprint |
| Go | `int64` (`int` is 32 bits on 32-bit platforms) | wraps silently | `math.Round` | `strconv.FormatFloat(x, 'g', 2, 64)`, then reprint |
| Java | `long` | `int` wraps silently; `Math.multiplyExact` throws | `Math.round` | `BigDecimal` with `MathContext(2)` |
| Rust | `u64` | panics in debug, wraps in release; `checked_mul` returns `None` | `f64::round` | `{:.1e}`, then reprint |
| C# | `long` | wraps unless inside `checked(...)` | `Math.Round(x, MidpointRounding.AwayFromZero)` | `ToString("G2")`, then reprint |

C and C++ would use `int64_t` or `long long` and `printf("%.2g")`. Signed overflow there is undefined behaviour, not just a wrong number, so the compiler may assume it never happens. Neither is a language you'd write a leaderboard service in, so they have no lab here.

**For a real leaderboard,** none of these languages would hand-write the tree. Redis sorted sets (`ZADD`, `ZREVRANK`) do this in a skip list, and every language has a Redis client. The labs write the tree so you can see why the deep dive's answer is about 20 steps.

## 2. What changes between languages

### How much room an estimate needs

The main lesson's "why the scan can't work" multiplies 3,472 peak reads a second by 50 million players: 173,600,000,000. That's about 1.7 × 10¹¹, and a signed 32-bit integer stops at about 2.1 × 10⁹. TypeScript and Python never notice. Java and C# compute `int × int` in 32 bits and wrap round to 1,801,308,160, a wrong answer with no error. The labs show it happening, then fix it by widening one side to `long` before multiplying. Rust's `u32::checked_mul` returns `None`, and Go uses `int64` explicitly because Go's `int` is only 32 bits on 32-bit platforms.

The labs keep the estimate itself in `float64`/`double`, like JavaScript's numbers. That's the right type for an estimate: it's never exact, and a float doesn't overflow until about 10³⁰⁸.

### Printing "910 GB"

`humanBytes` rounds to two significant figures. JavaScript's `toPrecision(2)` gives "910" for 912.5, but most languages' two-figure format gives scientific notation for anything of three or more digits: Python's `.2g` gives `9.1e+02`, as do Go's `'g'` and C#'s `"G2"`. Each lab rounds with that format, parses the result back into a number, and prints the number plainly. Java's `BigDecimal` rounds to a `MathContext` of two figures and prints without an exponent via `toPlainString`. C# also needs `CultureInfo.InvariantCulture`, or a machine set to German prints "6,9 MB".

### Rounding a half

`Math.round(2.5)` is 3 in JavaScript. Python's `round(2.5)` is 2, and C#'s `Math.Round(2.5)` is 2 as well: both round a half to the even neighbour (banker's rounding), which avoids a bias when adding many rounded numbers. Go's `math.Round` and Rust's `round` round halves away from zero, which matches JavaScript for positive numbers. None of this lesson's numbers lands exactly on a half, but the labs that compare with JavaScript say which rounding they mean anyway: Python with `math.floor(x + 0.5)`, C# with `MidpointRounding.AwayFromZero`.

### The Fenwick tree's lowest set bit

`i & -i` keeps only the lowest set bit of `i`: for 12 (binary 1100) it's 4. It relies on two's complement, where `-i` flips every bit and adds one. It works as written in Python, Go, Java and C#. Rust indexes with `usize`, which can't be negative, so it writes `i & i.wrapping_neg()`, which is the same bits.

### A score that isn't a whole number

TypeScript's `submit` checks `Number.isInteger(score)`, because `number` covers 2.5. In Go, Java, Rust and C#, `score` is an integer type, so 2.5 can't be passed at all: the check disappears into the type. Rust goes one step further with `u32`, which also rules out negatives. Python checks `isinstance(score, int)`, and also rejects `True`, because `bool` is a subclass of `int`, so `True` would otherwise pass as a score of 1.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| writes a second, average and peak | 579 and 1,736 |
| reads a second at peak; reads per write | 3,472; 2 |
| a year of score history; peak traffic out | "910 GB"; "6.9 MB" a second |
| comparisons a second for a full-scan rank | 173,600,000,000 |
| ranks of bo, cy, ada and di | 1, 1, 3, 4 (ties share a rank) |
| after ada scores 300 | ada 1, bo 2, cy 2, di 4 |
| rank among 200,000 players | the same as the scan, in at most 20 steps |

## Terms used in this lesson

1. **Overflow**: This is a calculation whose result doesn't fit in the type that holds it. Depending on the language, it wraps round to a wrong number, stops the program, or can't happen.
2. **Wrap round**: This means keeping only the lowest bits of a result that is too big, so counting past the largest value starts again from the smallest. The answer is wrong, but nothing reports it.
3. **Widening**: This means converting a value to a bigger type, such as `int` to `long`, before a calculation, so the result has room.
4. **Banker's rounding**: This is also known as **round half to even**. It rounds a value exactly halfway between two whole numbers to the even one, so 2.5 becomes 2 and 3.5 becomes 4.
5. **Two's complement**: This is the way almost every computer stores negative integers: flip every bit of the positive value and add one. It's why `i & -i` picks out the lowest set bit.
6. **Culture**: In .NET this is also called the **locale**. It's the set of conventions, such as whether a decimal point is a dot or a comma, that formatting functions use unless told otherwise.

## 4. Python

Python's `int` grows as needed, so the overflow in the main lesson's arithmetic can't happen, and the lab only notes it. `human_bytes` formats with `.2g`, parses the result back with `float`, and prints it with `:g`, which drops the exponent and the trailing zeros. The tests round with `math.floor(x + 0.5)`, because `round()` rounds halves to even. `submit` rejects `True` explicitly, because `bool` is a subclass of `int`.

```python
"""Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps.
The same numbers as the TypeScript lab."""
from dataclasses import dataclass

SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class Assumptions:
    daily_active_users: int
    writes_per_user_per_day: float
    reads_per_user_per_day: float
    peak_to_average: float
    bytes_per_write: int
    kept_for_days: int
    bytes_per_read: int


def estimate(a: Assumptions) -> dict:
    writes = a.daily_active_users * a.writes_per_user_per_day / SECONDS_PER_DAY
    reads = a.daily_active_users * a.reads_per_user_per_day / SECONDS_PER_DAY
    return {
        "writes_per_second": {"average": writes, "peak": writes * a.peak_to_average},
        "reads_per_second": {"average": reads, "peak": reads * a.peak_to_average},
        "reads_per_write": a.reads_per_user_per_day / a.writes_per_user_per_day,
        "storage_bytes": a.daily_active_users * a.writes_per_user_per_day * a.bytes_per_write * a.kept_for_days,
        "peak_egress_bytes_per_second": reads * a.peak_to_average * a.bytes_per_read,
    }


def human_bytes(n: float) -> str:
    """Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB"."""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while n >= 1000 and i < len(units) - 1:
        n /= 1000
        i += 1
    # f"{910.0:.2g}" is "9.1e+02": round to two figures first, then print without an exponent.
    return f"{float(f'{n:.2g}'):g} {units[i]}"


class Leaderboard:
    """Each player's best score, and a Fenwick tree of how many players have each score."""

    def __init__(self, max_score: int):
        self.max_score = max_score
        self._best: dict[str, int] = {}
        self._tree = [0] * (max_score + 2)
        self.steps = 0

    @property
    def players(self) -> int:
        return len(self._best)

    def submit(self, player: str, score: int) -> bool:
        # bool is a subclass of int in Python, so True would otherwise pass as a score of 1.
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= self.max_score:
            raise ValueError(f"score must be a whole number from 0 to {self.max_score}, got {score!r}")
        old = self._best.get(player)
        if old is not None and score <= old:
            return False
        if old is not None:
            self._add(old, -1)
        self._add(score, +1)
        self._best[player] = score
        return True

    def rank(self, player: str) -> int | None:
        score = self._best.get(player)
        if score is None:
            return None
        self.steps = 0
        return 1 + self.players - self._count_at_most(score)

    def _add(self, score: int, delta: int) -> None:
        i = score + 1
        while i < len(self._tree):
            self._tree[i] += delta
            i += i & -i

    def _count_at_most(self, score: int) -> int:
        count, i = 0, score + 1
        while i > 0:
            count += self._tree[i]
            self.steps += 1
            i -= i & -i
        return count


def rank_by_scan(scores, mine: int) -> tuple[int, int]:
    higher = steps = 0
    for s in scores:
        steps += 1
        if s > mine:
            higher += 1
    return 1 + higher, steps
```

```python
import unittest

from approach import Assumptions, Leaderboard, estimate, human_bytes, rank_by_scan

GAME = estimate(Assumptions(daily_active_users=10_000_000, writes_per_user_per_day=5, reads_per_user_per_day=10,
                            peak_to_average=3, bytes_per_write=50, kept_for_days=365, bytes_per_read=2_000))


def round_half_up(x: float) -> int:
    return int(x + 0.5)  # Python's round() sends halves to the even number; JavaScript's Math.round goes up


class Approach(unittest.TestCase):
    def test_estimate(self):
        self.assertEqual(round_half_up(GAME["writes_per_second"]["average"]), 579)
        self.assertEqual(round_half_up(GAME["writes_per_second"]["peak"]), 1736)
        self.assertEqual(round_half_up(GAME["reads_per_second"]["peak"]), 3472)
        self.assertEqual(GAME["reads_per_write"], 2)
        self.assertEqual(human_bytes(GAME["storage_bytes"]), "910 GB")
        self.assertEqual(human_bytes(GAME["peak_egress_bytes_per_second"]), "6.9 MB")

    def test_why_the_scan_cannot_work(self):
        players = 50_000_000
        self.assertEqual(round_half_up(GAME["reads_per_second"]["peak"]) * players, 173_600_000_000)  # ints never overflow
        self.assertEqual(human_bytes(players * 100), "5 GB")

    def test_ranks_ties_and_best_scores(self):
        board = Leaderboard(1_000)
        for player, score in [("ada", 100), ("bo", 250), ("cy", 250), ("di", 90)]:
            board.submit(player, score)
        self.assertEqual([board.rank(p) for p in ["bo", "cy", "ada", "di"]], [1, 1, 3, 4])
        self.assertFalse(board.submit("ada", 80))
        self.assertEqual(board.rank("ada"), 3)
        self.assertTrue(board.submit("ada", 300))
        self.assertEqual([board.rank(p) for p in ["ada", "bo", "cy", "di"]], [1, 2, 2, 4])
        self.assertIsNone(board.rank("nobody"))
        for bad in [1_001, 2.5, True]:
            with self.assertRaises(ValueError):
                board.submit("ed", bad)

    def test_about_20_steps_instead_of_one_per_player(self):
        max_score = 1_000_000
        board = Leaderboard(max_score)
        scores = [(i * 7_919) % (max_score + 1) for i in range(200_000)]
        for i, score in enumerate(scores):
            board.submit(f"p{i}", score)
        for i in [0, 1, 12_345, 199_999]:
            rank, steps = rank_by_scan(scores, scores[i])
            self.assertEqual(board.rank(f"p{i}"), rank)
            self.assertLessEqual(board.steps, 20)
            self.assertEqual(steps, 200_000)


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/01-how-to-approach-system-design/labs/python). `python3 labs/run.py how-to-approach-system-design/python`.

## 5. Go

The assumptions are `float64`, so the estimate's arithmetic matches JavaScript's. The scan-cost check uses `int64` on purpose: Go's `int` is 64 bits on a 64-bit machine but 32 on a 32-bit one, and wraps silently either way. `Rank` returns `(rank, ok)`, Go's usual way of saying "maybe absent", and `Submit` returns an error rather than throwing. The function is called `Compute`, because Go doesn't allow a function and a type with the same name, `Estimate`, in one package.

```go
// Package approach: back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about
// 20 steps. The same numbers as the TypeScript lab.
package approach

import (
	"fmt"
	"strconv"
)

const SecondsPerDay = 86_400

// Assumptions are float64 so the arithmetic matches JavaScript's numbers; an estimate is never exact anyway.
type Assumptions struct {
	DailyActiveUsers, WritesPerUserPerDay, ReadsPerUserPerDay, PeakToAverage float64
	BytesPerWrite, KeptForDays, BytesPerRead                                 float64
}

type Rate struct{ Average, Peak float64 }

type Estimate struct {
	WritesPerSecond, ReadsPerSecond                       Rate
	ReadsPerWrite, StorageBytes, PeakEgressBytesPerSecond float64
}

func Compute(a Assumptions) Estimate {
	writes := a.DailyActiveUsers * a.WritesPerUserPerDay / SecondsPerDay
	reads := a.DailyActiveUsers * a.ReadsPerUserPerDay / SecondsPerDay
	return Estimate{
		WritesPerSecond:          Rate{writes, writes * a.PeakToAverage},
		ReadsPerSecond:           Rate{reads, reads * a.PeakToAverage},
		ReadsPerWrite:            a.ReadsPerUserPerDay / a.WritesPerUserPerDay,
		StorageBytes:             a.DailyActiveUsers * a.WritesPerUserPerDay * a.BytesPerWrite * a.KeptForDays,
		PeakEgressBytesPerSecond: reads * a.PeakToAverage * a.BytesPerRead,
	}
}

// HumanBytes gives two significant figures in powers of 1,000: 912,500,000,000 → "910 GB".
func HumanBytes(n float64) string {
	units := []string{"B", "KB", "MB", "GB", "TB", "PB"}
	i := 0
	for n >= 1000 && i < len(units)-1 {
		n /= 1000
		i++
	}
	// 'g' with 2 figures gives "9.1e+02" for 910; parse it back and print the shortest plain form.
	rounded, _ := strconv.ParseFloat(strconv.FormatFloat(n, 'g', 2, 64), 64)
	return fmt.Sprintf("%s %s", strconv.FormatFloat(rounded, 'f', -1, 64), units[i])
}

// Leaderboard keeps each player's best score, and a Fenwick tree of how many players have each score.
type Leaderboard struct {
	maxScore int
	best     map[string]int
	tree     []int
	Steps    int // the work the last Rank did
}

func NewLeaderboard(maxScore int) *Leaderboard {
	return &Leaderboard{maxScore: maxScore, best: map[string]int{}, tree: make([]int, maxScore+2)}
}

func (b *Leaderboard) Players() int { return len(b.best) }

// Submit records a score; only a player's best counts. A score can't be 2.5: the int type rules it out.
func (b *Leaderboard) Submit(player string, score int) (bool, error) {
	if score < 0 || score > b.maxScore {
		return false, fmt.Errorf("score must be from 0 to %d, got %d", b.maxScore, score)
	}
	old, seen := b.best[player]
	if seen && score <= old {
		return false, nil
	}
	if seen {
		b.add(old, -1)
	}
	b.add(score, +1)
	b.best[player] = score
	return true, nil
}

// Rank is 1 + the number of players with a strictly higher best; ok is false for an unknown player.
func (b *Leaderboard) Rank(player string) (rank int, ok bool) {
	score, ok := b.best[player]
	if !ok {
		return 0, false
	}
	b.Steps = 0
	return 1 + b.Players() - b.countAtMost(score), true
}

func (b *Leaderboard) add(score, delta int) {
	for i := score + 1; i < len(b.tree); i += i & -i {
		b.tree[i] += delta
	}
}

func (b *Leaderboard) countAtMost(score int) int {
	count := 0
	for i := score + 1; i > 0; i -= i & -i {
		count += b.tree[i]
		b.Steps++
	}
	return count
}

// RankByScan is the obvious way: look at every player.
func RankByScan(scores []int, mine int) (rank, steps int) {
	higher := 0
	for _, s := range scores {
		steps++
		if s > mine {
			higher++
		}
	}
	return 1 + higher, steps
}
```

```go
package approach

import (
	"fmt"
	"math"
	"slices"
	"testing"
)

var game = Compute(Assumptions{
	DailyActiveUsers: 10_000_000, WritesPerUserPerDay: 5, ReadsPerUserPerDay: 10, PeakToAverage: 3,
	BytesPerWrite: 50, KeptForDays: 365, BytesPerRead: 2_000,
})

func TestEstimate(t *testing.T) {
	got := []float64{math.Round(game.WritesPerSecond.Average), math.Round(game.WritesPerSecond.Peak), math.Round(game.ReadsPerSecond.Peak), game.ReadsPerWrite}
	if !slices.Equal(got, []float64{579, 1736, 3472, 2}) {
		t.Fatal(got)
	}
	if s, e := HumanBytes(game.StorageBytes), HumanBytes(game.PeakEgressBytesPerSecond); s != "910 GB" || e != "6.9 MB" {
		t.Fatal(s, e)
	}
}

func TestWhyTheScanCannotWork(t *testing.T) {
	var players int64 = 50_000_000 // int64, not int: int is only 32 bits on 32-bit platforms
	if got := int64(math.Round(game.ReadsPerSecond.Peak)) * players; got != 173_600_000_000 {
		t.Fatal(got)
	}
	if got := HumanBytes(float64(players * 100)); got != "5 GB" {
		t.Fatal(got)
	}
}

func TestRanksTiesAndBestScores(t *testing.T) {
	b := NewLeaderboard(1_000)
	for _, p := range []struct {
		name  string
		score int
	}{{"ada", 100}, {"bo", 250}, {"cy", 250}, {"di", 90}} {
		b.Submit(p.name, p.score)
	}
	ranks := func(names ...string) []int {
		var out []int
		for _, n := range names {
			r, _ := b.Rank(n)
			out = append(out, r)
		}
		return out
	}
	if got := ranks("bo", "cy", "ada", "di"); !slices.Equal(got, []int{1, 1, 3, 4}) {
		t.Fatal(got)
	}
	if changed, _ := b.Submit("ada", 80); changed {
		t.Fatal("a lower score changed ada's best")
	}
	if changed, _ := b.Submit("ada", 300); !changed {
		t.Fatal("a higher score was ignored")
	}
	if got := ranks("ada", "bo", "cy", "di"); !slices.Equal(got, []int{1, 2, 2, 4}) {
		t.Fatal(got)
	}
	if _, ok := b.Rank("nobody"); ok {
		t.Fatal("an unknown player has a rank")
	}
	if _, err := b.Submit("ed", 1_001); err == nil {
		t.Fatal("a score above the maximum was accepted")
	}
}

func TestAbout20StepsInsteadOfOnePerPlayer(t *testing.T) {
	const maxScore = 1_000_000
	b := NewLeaderboard(maxScore)
	scores := make([]int, 200_000)
	for i := range scores {
		scores[i] = (i * 7_919) % (maxScore + 1)
		b.Submit(fmt.Sprintf("p%d", i), scores[i])
	}
	for _, i := range []int{0, 1, 12_345, 199_999} {
		want, steps := RankByScan(scores, scores[i])
		if got, _ := b.Rank(fmt.Sprintf("p%d", i)); got != want || b.Steps > 20 || steps != 200_000 {
			t.Fatal(i, got, want, b.Steps, steps)
		}
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/01-how-to-approach-system-design/labs/go). `python3 labs/run.py how-to-approach-system-design/go`.

## 6. Java

Records hold the assumptions and results. The check shows the overflow plainly: `peakReads * players` in `int` gives 1,801,308,160, with no error; casting one side to `long` first gives the right answer, and `Math.multiplyExact` throws rather than wrapping. `humanBytes` rounds with `BigDecimal`, which works on the exact value of the double, the same way JavaScript's `toPrecision` does. `rank` returns `OptionalInt`, so a missing player can't be mistaken for rank 0.

```java
package approach;

import java.math.BigDecimal;
import java.math.MathContext;
import java.util.HashMap;
import java.util.Map;
import java.util.OptionalInt;

/** Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps. */
public final class Approach {
    private Approach() {}

    public static final double SECONDS_PER_DAY = 86_400;

    public record Assumptions(double dailyActiveUsers, double writesPerUserPerDay, double readsPerUserPerDay,
            double peakToAverage, double bytesPerWrite, double keptForDays, double bytesPerRead) {}

    public record Rate(double average, double peak) {}

    public record Estimate(Rate writesPerSecond, Rate readsPerSecond, double readsPerWrite, double storageBytes,
            double peakEgressBytesPerSecond) {}

    public static Estimate estimate(Assumptions a) {
        double writes = a.dailyActiveUsers() * a.writesPerUserPerDay() / SECONDS_PER_DAY;
        double reads = a.dailyActiveUsers() * a.readsPerUserPerDay() / SECONDS_PER_DAY;
        return new Estimate(
                new Rate(writes, writes * a.peakToAverage()),
                new Rate(reads, reads * a.peakToAverage()),
                a.readsPerUserPerDay() / a.writesPerUserPerDay(),
                a.dailyActiveUsers() * a.writesPerUserPerDay() * a.bytesPerWrite() * a.keptForDays(),
                reads * a.peakToAverage() * a.bytesPerRead());
    }

    /** Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB". */
    public static String humanBytes(double n) {
        String[] units = {"B", "KB", "MB", "GB", "TB", "PB"};
        int i = 0;
        while (n >= 1000 && i < units.length - 1) {
            n /= 1000;
            i++;
        }
        // BigDecimal rounds the exact value to 2 figures; toPlainString avoids "9.1E+2".
        return new BigDecimal(n).round(new MathContext(2)).stripTrailingZeros().toPlainString() + " " + units[i];
    }

    /** Each player's best score, and a Fenwick tree of how many players have each score. */
    public static final class Leaderboard {
        private final int maxScore;
        private final Map<String, Integer> best = new HashMap<>();
        private final int[] tree;
        public int steps; // the work the last rank() did

        public Leaderboard(int maxScore) {
            this.maxScore = maxScore;
            this.tree = new int[maxScore + 2];
        }

        public int players() {
            return best.size();
        }

        /** Only a player's best counts. A score can't be 2.5: the int type rules it out. */
        public boolean submit(String player, int score) {
            if (score < 0 || score > maxScore) {
                throw new IllegalArgumentException("score must be from 0 to " + maxScore + ", got " + score);
            }
            Integer old = best.get(player);
            if (old != null && score <= old) return false;
            if (old != null) add(old, -1);
            add(score, +1);
            best.put(player, score);
            return true;
        }

        public OptionalInt rank(String player) {
            Integer score = best.get(player);
            if (score == null) return OptionalInt.empty();
            steps = 0;
            return OptionalInt.of(1 + players() - countAtMost(score));
        }

        private void add(int score, int delta) {
            for (int i = score + 1; i < tree.length; i += i & -i) tree[i] += delta;
        }

        private int countAtMost(int score) {
            int count = 0;
            for (int i = score + 1; i > 0; i -= i & -i) {
                count += tree[i];
                steps++;
            }
            return count;
        }
    }

    public record Scan(int rank, int steps) {}

    public static Scan rankByScan(int[] scores, int mine) {
        int higher = 0;
        int steps = 0;
        for (int s : scores) {
            steps++;
            if (s > mine) higher++;
        }
        return new Scan(1 + higher, steps);
    }
}
```

```java
package approach;

import java.util.List;
import java.util.OptionalInt;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class ApproachCheck {
    private ApproachCheck() {}

    public static void main(String[] args) {
        var game = Approach.estimate(new Approach.Assumptions(10_000_000, 5, 10, 3, 50, 365, 2_000));
        assert Math.round(game.writesPerSecond().average()) == 579;
        assert Math.round(game.writesPerSecond().peak()) == 1736;
        assert Math.round(game.readsPerSecond().peak()) == 3472;
        assert game.readsPerWrite() == 2;
        assert Approach.humanBytes(game.storageBytes()).equals("910 GB") : Approach.humanBytes(game.storageBytes());
        assert Approach.humanBytes(game.peakEgressBytesPerSecond()).equals("6.9 MB");

        // Why the scan can't work. In int arithmetic the product wraps round silently to a wrong number.
        int peakReads = (int) Math.round(game.readsPerSecond().peak());
        int players = 50_000_000;
        assert peakReads * players == 1_801_308_160; // wrong, and no error
        assert (long) peakReads * players == 173_600_000_000L; // widen first
        try {
            Math.multiplyExact(peakReads, players);
            throw new AssertionError("expected an overflow");
        } catch (ArithmeticException expected) {
            // multiplyExact refuses instead of wrapping
        }
        assert Approach.humanBytes(players * 100.0).equals("5 GB");

        var board = new Approach.Leaderboard(1_000);
        board.submit("ada", 100);
        board.submit("bo", 250);
        board.submit("cy", 250);
        board.submit("di", 90);
        assert ranks(board, "bo", "cy", "ada", "di").equals(List.of(1, 1, 3, 4));
        assert !board.submit("ada", 80);
        assert board.submit("ada", 300);
        assert ranks(board, "ada", "bo", "cy", "di").equals(List.of(1, 2, 2, 4));
        assert board.rank("nobody").equals(OptionalInt.empty());
        try {
            board.submit("ed", 1_001);
            throw new AssertionError("expected a rejected score");
        } catch (IllegalArgumentException expected) {
            // above the maximum
        }

        int maxScore = 1_000_000;
        var big = new Approach.Leaderboard(maxScore);
        int[] scores = new int[200_000];
        for (int i = 0; i < scores.length; i++) {
            scores[i] = i * 7_919 % (maxScore + 1); // at most 1.6 billion: fits in an int
            big.submit("p" + i, scores[i]);
        }
        for (int i : new int[] {0, 1, 12_345, 199_999}) {
            var scan = Approach.rankByScan(scores, scores[i]);
            assert big.rank("p" + i).getAsInt() == scan.rank();
            assert big.steps <= 20 : big.steps;
            assert scan.steps() == 200_000;
        }
        System.out.println("all approach checks passed");
    }

    private static List<Integer> ranks(Approach.Leaderboard board, String... names) {
        return java.util.Arrays.stream(names).map(n -> board.rank(n).getAsInt()).toList();
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/01-how-to-approach-system-design/labs/java). `python3 labs/run.py how-to-approach-system-design/java`.

## 7. Rust

Scores are `u32`, which rules out both 2.5 and −1 at compile time, so `submit` checks only the maximum. The overflow test uses `checked_mul`, which returns `None`; plain `*` would panic in a debug build and wrap in a release build. The tree indexes with `usize`, so the lowest set bit is `i & i.wrapping_neg()`. `rank` takes `&mut self` because it records `steps`, and Rust makes that visible in the signature.

```rust
//! Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps.
//! The same numbers as the TypeScript lab.
use std::collections::HashMap;

pub const SECONDS_PER_DAY: f64 = 86_400.0;

pub struct Assumptions {
    pub daily_active_users: f64,
    pub writes_per_user_per_day: f64,
    pub reads_per_user_per_day: f64,
    pub peak_to_average: f64,
    pub bytes_per_write: f64,
    pub kept_for_days: f64,
    pub bytes_per_read: f64,
}

pub struct Rate {
    pub average: f64,
    pub peak: f64,
}

pub struct Estimate {
    pub writes_per_second: Rate,
    pub reads_per_second: Rate,
    pub reads_per_write: f64,
    pub storage_bytes: f64,
    pub peak_egress_bytes_per_second: f64,
}

pub fn estimate(a: &Assumptions) -> Estimate {
    let writes = a.daily_active_users * a.writes_per_user_per_day / SECONDS_PER_DAY;
    let reads = a.daily_active_users * a.reads_per_user_per_day / SECONDS_PER_DAY;
    Estimate {
        writes_per_second: Rate {
            average: writes,
            peak: writes * a.peak_to_average,
        },
        reads_per_second: Rate {
            average: reads,
            peak: reads * a.peak_to_average,
        },
        reads_per_write: a.reads_per_user_per_day / a.writes_per_user_per_day,
        storage_bytes: a.daily_active_users
            * a.writes_per_user_per_day
            * a.bytes_per_write
            * a.kept_for_days,
        peak_egress_bytes_per_second: reads * a.peak_to_average * a.bytes_per_read,
    }
}

/// Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB".
pub fn human_bytes(mut n: f64) -> String {
    let units = ["B", "KB", "MB", "GB", "TB", "PB"];
    let mut i = 0;
    while n >= 1000.0 && i < units.len() - 1 {
        n /= 1000.0;
        i += 1;
    }
    // {:.1e} gives "9.1e2" for 910; parse it back, and Display prints the plain "910".
    let rounded: f64 = format!("{n:.1e}")
        .parse()
        .expect("a float we just formatted");
    format!("{rounded} {}", units[i])
}

/// Each player's best score, and a Fenwick tree of how many players have each score.
pub struct Leaderboard {
    max_score: u32,
    best: HashMap<String, u32>,
    tree: Vec<i64>,
    pub steps: u32, // the work the last rank() did
}

impl Leaderboard {
    pub fn new(max_score: u32) -> Self {
        Leaderboard {
            max_score,
            best: HashMap::new(),
            tree: vec![0; max_score as usize + 2],
            steps: 0,
        }
    }

    pub fn players(&self) -> usize {
        self.best.len()
    }

    /// Only a player's best counts. A score can't be 2.5 or negative: u32 rules both out.
    pub fn submit(&mut self, player: &str, score: u32) -> Result<bool, String> {
        if score > self.max_score {
            return Err(format!(
                "score must be from 0 to {}, got {score}",
                self.max_score
            ));
        }
        let old = self.best.get(player).copied();
        if old.is_some_and(|old| score <= old) {
            return Ok(false);
        }
        if let Some(old) = old {
            self.add(old, -1);
        }
        self.add(score, 1);
        self.best.insert(player.to_string(), score);
        Ok(true)
    }

    pub fn rank(&mut self, player: &str) -> Option<usize> {
        let score = *self.best.get(player)?;
        self.steps = 0;
        Some(1 + self.players() - self.count_at_most(score) as usize)
    }

    // usize has no negative, so the lowest set bit is i & i.wrapping_neg() rather than i & -i.
    fn add(&mut self, score: u32, delta: i64) {
        let mut i = score as usize + 1;
        while i < self.tree.len() {
            self.tree[i] += delta;
            i += i & i.wrapping_neg();
        }
    }

    fn count_at_most(&mut self, score: u32) -> i64 {
        let (mut count, mut i) = (0, score as usize + 1);
        while i > 0 {
            count += self.tree[i];
            self.steps += 1;
            i -= i & i.wrapping_neg();
        }
        count
    }
}

/// The obvious way: look at every player. Returns (rank, steps).
pub fn rank_by_scan(scores: &[u32], mine: u32) -> (usize, usize) {
    let higher = scores.iter().filter(|&&s| s > mine).count();
    (1 + higher, scores.len())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn game() -> Estimate {
        estimate(&Assumptions {
            daily_active_users: 10_000_000.0,
            writes_per_user_per_day: 5.0,
            reads_per_user_per_day: 10.0,
            peak_to_average: 3.0,
            bytes_per_write: 50.0,
            kept_for_days: 365.0,
            bytes_per_read: 2_000.0,
        })
    }

    #[test]
    fn the_estimate() {
        let g = game();
        let got = [
            g.writes_per_second.average,
            g.writes_per_second.peak,
            g.reads_per_second.peak,
        ]
        .map(f64::round);
        assert_eq!(got, [579.0, 1736.0, 3472.0]);
        assert_eq!(g.reads_per_write, 2.0);
        assert_eq!(human_bytes(g.storage_bytes), "910 GB");
        assert_eq!(human_bytes(g.peak_egress_bytes_per_second), "6.9 MB");
    }

    #[test]
    fn why_the_scan_cannot_work() {
        let peak_reads = game().reads_per_second.peak.round() as u32;
        let players: u32 = 50_000_000;
        assert_eq!(peak_reads.checked_mul(players), None); // too big for u32; plain * would panic in a debug build
        assert_eq!(u64::from(peak_reads) * u64::from(players), 173_600_000_000);
        assert_eq!(human_bytes(f64::from(players) * 100.0), "5 GB");
    }

    #[test]
    fn ranks_ties_and_best_scores() {
        let mut b = Leaderboard::new(1_000);
        for (p, s) in [("ada", 100), ("bo", 250), ("cy", 250), ("di", 90)] {
            b.submit(p, s).unwrap();
        }
        let ranks = |b: &mut Leaderboard, names: [&str; 4]| names.map(|n| b.rank(n).unwrap());
        assert_eq!(ranks(&mut b, ["bo", "cy", "ada", "di"]), [1, 1, 3, 4]);
        assert_eq!(b.submit("ada", 80), Ok(false));
        assert_eq!(b.submit("ada", 300), Ok(true));
        assert_eq!(ranks(&mut b, ["ada", "bo", "cy", "di"]), [1, 2, 2, 4]);
        assert_eq!(b.rank("nobody"), None);
        assert!(b.submit("ed", 1_001).is_err());
    }

    #[test]
    fn about_20_steps_instead_of_one_per_player() {
        let max_score = 1_000_000;
        let mut b = Leaderboard::new(max_score);
        let scores: Vec<u32> = (0..200_000)
            .map(|i| (i * 7_919) % (max_score + 1))
            .collect();
        for (i, &s) in scores.iter().enumerate() {
            b.submit(&format!("p{i}"), s).unwrap();
        }
        for i in [0, 1, 12_345, 199_999] {
            let (rank, steps) = rank_by_scan(&scores, scores[i]);
            assert_eq!(b.rank(&format!("p{i}")), Some(rank));
            assert!(b.steps <= 20, "{} steps", b.steps);
            assert_eq!(steps, 200_000);
        }
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/01-how-to-approach-system-design/labs/rust). `python3 labs/run.py how-to-approach-system-design/rust`.

## 8. C#

`Leaderboard` uses a primary constructor, and `Rank` returns `int?`. The check shows both overflow behaviours: `unchecked(peakReads * players)` wraps to the same wrong number as Java, and `checked(...)` throws an `OverflowException`. C# is unchecked by default unless the project turns on `CheckForOverflowUnderflow`. `HumanBytes` formats with `InvariantCulture`, because number formatting in .NET follows the machine's culture otherwise. It runs in the .NET SDK container.

```csharp
// Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps.
// The same numbers as the TypeScript lab.
using System.Globalization;

public record Assumptions(double DailyActiveUsers, double WritesPerUserPerDay, double ReadsPerUserPerDay,
    double PeakToAverage, double BytesPerWrite, double KeptForDays, double BytesPerRead);

public record Rate(double Average, double Peak);

public record Estimate(Rate WritesPerSecond, Rate ReadsPerSecond, double ReadsPerWrite, double StorageBytes,
    double PeakEgressBytesPerSecond);

public static class Sizing
{
    public const double SecondsPerDay = 86_400;

    public static Estimate Estimate(Assumptions a)
    {
        var writes = a.DailyActiveUsers * a.WritesPerUserPerDay / SecondsPerDay;
        var reads = a.DailyActiveUsers * a.ReadsPerUserPerDay / SecondsPerDay;
        return new(
            new(writes, writes * a.PeakToAverage),
            new(reads, reads * a.PeakToAverage),
            a.ReadsPerUserPerDay / a.WritesPerUserPerDay,
            a.DailyActiveUsers * a.WritesPerUserPerDay * a.BytesPerWrite * a.KeptForDays,
            reads * a.PeakToAverage * a.BytesPerRead);
    }

    /// <summary>Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB".</summary>
    public static string HumanBytes(double n)
    {
        string[] units = ["B", "KB", "MB", "GB", "TB", "PB"];
        var i = 0;
        while (n >= 1000 && i < units.Length - 1)
        {
            n /= 1000;
            i++;
        }
        // "G2" gives "9.1E+02" for 910; parse it back. InvariantCulture, or a German machine prints "6,9".
        var inv = CultureInfo.InvariantCulture;
        return $"{double.Parse(n.ToString("G2", inv), inv).ToString(inv)} {units[i]}";
    }
}

/// <summary>Each player's best score, and a Fenwick tree of how many players have each score.</summary>
public sealed class Leaderboard(int maxScore)
{
    private readonly Dictionary<string, int> _best = [];
    private readonly int[] _tree = new int[maxScore + 2];
    public int Steps { get; private set; } // the work the last Rank did

    public int Players => _best.Count;

    /// <summary>Only a player's best counts. A score can't be 2.5: the int type rules it out.</summary>
    public bool Submit(string player, int score)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(score);
        ArgumentOutOfRangeException.ThrowIfGreaterThan(score, maxScore);
        var seen = _best.TryGetValue(player, out var old);
        if (seen && score <= old) return false;
        if (seen) Add(old, -1);
        Add(score, +1);
        _best[player] = score;
        return true;
    }

    public int? Rank(string player)
    {
        if (!_best.TryGetValue(player, out var score)) return null;
        Steps = 0;
        return 1 + Players - CountAtMost(score);
    }

    private void Add(int score, int delta)
    {
        for (var i = score + 1; i < _tree.Length; i += i & -i) _tree[i] += delta;
    }

    private int CountAtMost(int score)
    {
        var count = 0;
        for (var i = score + 1; i > 0; i -= i & -i)
        {
            count += _tree[i];
            Steps++;
        }
        return count;
    }

    /// <summary>The obvious way: look at every player.</summary>
    public static (int Rank, int Steps) RankByScan(int[] scores, int mine) =>
        (1 + scores.Count(s => s > mine), scores.Length);
}
```

```csharp
// Checks: the same numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Math.Round sends halves to the even number by default; JavaScript's Math.round goes up. Say which you mean.
static double Round(double x) => Math.Round(x, MidpointRounding.AwayFromZero);

var game = Sizing.Estimate(new(10_000_000, 5, 10, 3, 50, 365, 2_000));
Check(Round(game.WritesPerSecond.Average) == 579 && Round(game.WritesPerSecond.Peak) == 1736, game.WritesPerSecond);
Check(Round(game.ReadsPerSecond.Peak) == 3472 && game.ReadsPerWrite == 2, game.ReadsPerSecond);
Check(Sizing.HumanBytes(game.StorageBytes) == "910 GB", Sizing.HumanBytes(game.StorageBytes));
Check(Sizing.HumanBytes(game.PeakEgressBytesPerSecond) == "6.9 MB", Sizing.HumanBytes(game.PeakEgressBytesPerSecond));

// Why the scan can't work. int arithmetic wraps silently unless you ask for checked.
var peakReads = (int)Round(game.ReadsPerSecond.Peak);
var players = 50_000_000;
Check(unchecked(peakReads * players) == 1_801_308_160, "wraps to a wrong number");
Check((long)peakReads * players == 173_600_000_000, "widen first");
try
{
    _ = checked(peakReads * players);
    Check(false, "expected an overflow");
}
catch (OverflowException)
{
    // checked refuses instead of wrapping
}
Check(Sizing.HumanBytes(players * 100.0) == "5 GB", "5 GB");

var board = new Leaderboard(1_000);
foreach (var (p, s) in new[] { ("ada", 100), ("bo", 250), ("cy", 250), ("di", 90) }) board.Submit(p, s);
int?[] Ranks(params string[] names) => names.Select(board.Rank).ToArray();
Check(Ranks("bo", "cy", "ada", "di").SequenceEqual(new int?[] { 1, 1, 3, 4 }), "ties share a rank");
Check(!board.Submit("ada", 80) && board.Submit("ada", 300), "only the best counts");
Check(Ranks("ada", "bo", "cy", "di").SequenceEqual(new int?[] { 1, 2, 2, 4 }), "after a new best");
Check(board.Rank("nobody") is null, "unknown player");
try
{
    board.Submit("ed", 1_001);
    Check(false, "expected a rejected score");
}
catch (ArgumentOutOfRangeException)
{
    // above the maximum
}

const int maxScore = 1_000_000;
var big = new Leaderboard(maxScore);
var scores = Enumerable.Range(0, 200_000).Select(i => i * 7_919 % (maxScore + 1)).ToArray();
for (var i = 0; i < scores.Length; i++) big.Submit($"p{i}", scores[i]);
foreach (var i in new[] { 0, 1, 12_345, 199_999 })
{
    var scan = Leaderboard.RankByScan(scores, scores[i]);
    Check(big.Rank($"p{i}") == scan.Rank && big.Steps <= 20 && scan.Steps == 200_000, (i, big.Steps));
}
Console.WriteLine("all approach checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/01-system-design-fundamentals/01-how-to-approach-system-design/labs/csharp). `python3 labs/run.py how-to-approach-system-design/csharp`.

## Common pitfalls

1. **Multiplying two `int`s into a `long`.** `long x = a * b` multiplies in `int` first, wraps, then widens the wrong answer. Widen one side before multiplying: `(long) a * b`.
2. **Trusting the language to report overflow.** Java, C# and Go wrap silently; Rust wraps silently in release builds. Use `multiplyExact`, `checked`, or `checked_mul` where a wrong number would matter.
3. **`round()` in Python or `Math.Round` in C# when comparing with JavaScript.** Both round halves to even. Say which rounding you mean.
4. **Formatting with the machine's locale.** C# and Java format numbers with the current culture unless told otherwise, so a test that passes on your laptop fails on a server set to French.
5. **`i & -i` on unsigned types.** It doesn't compile in Rust. Use `wrapping_neg`.

## Check your understanding

1. In Java, `long total = peakReads * players;` with both `int`. Why is `total` wrong, although it's a `long`?
2. Why does Python never hit the overflow, and what does that cost?
3. Why does `f"{910.0:.2g}"` give `9.1e+02`, and how does the lab get "910"?
4. Why would `submit("ed", True)` succeed in Python without the extra check?
5. A Rust program multiplies 3,472 by 50,000,000 as `u32`s with `*`. Built for debugging it panics; built with `--release` it prints a wrong number. Why the difference?

<details>
<summary>Answers — after your attempt</summary>

1. The multiplication happens in `int`, because both operands are `int`. It wraps to 1,801,308,160 first, and only then is the wrong value widened to `long`. Cast one operand first.
2. Python's `int` is arbitrary precision: it grows to whatever size the value needs. The cost is speed and memory: each int is an object, and big ones need more than one machine word.
3. Two significant figures of 910 can't be written as a plain integer without implying a third figure, so `g` format switches to scientific notation. The lab parses `9.1e+02` back to 910.0 and prints that with `:g`, which drops the exponent and the trailing ".0".
4. `bool` is a subclass of `int`, and `True == 1`, so it would pass `isinstance(score, int)` and the range check, and record a score of 1.
5. Debug builds check integer arithmetic and panic on overflow. Release builds leave the check out for speed, so the same multiplication wraps silently. Use `checked_mul` when overflow is possible, or `u64` when the value needs the room.

</details>

## Practice — independent task

**Add a percentile to the leaderboard, in a language other than TypeScript.**

1. Add `percentile(player)` to your language's `Leaderboard`: the share of players whose best score is below the player's, as a number from 0 to 100.
2. It must take about log₂(maxScore) steps, like `rank`, not one per player.
3. Test it with the four players from the ranks test, and with 200,000 players against a scan. Decide and test what a player with the lowest score gets, and what an unknown player gets.

**Done when:** your tests pass, `steps` stays at or below 20 for 200,000 players, and you can say which integer type held the counts and why it can't overflow.

<details>
<summary>Hints — after your attempt</summary>

- Players below a score is `countAtMost(score - 1)`. Watch the boundary at score 0, where `score - 1` is −1 and, in Rust, doesn't exist for `u32`.
- Divide as floating point: in Java, C# and Go, `below / players` with two integers truncates to 0.

</details>

## Before moving on

You can say how much room an estimate needs in your language and what happens when it runs out, format and round numbers to match another language, and write the Fenwick tree where sizes are unsigned.

**Recap.** The design method is the same in every language; the arithmetic isn't. Python's ints grow; Java, C# and Go wrap silently; Rust panics in debug and wraps in release, so use `long`, `int64` or `u64` and the checked operations where it matters. Two significant figures without an exponent takes a format-then-reparse step everywhere except JavaScript and Java's `BigDecimal`. Python and C# round halves to even by default. Typed languages turn "is the score a whole number?" into a type, and Rust's unsigned sizes turn `i & -i` into `i & i.wrapping_neg()`.

## Related

- [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|How to approach system design]]: the main lesson
- [[architecture/01-system-design-fundamentals/02-scalability-and-performance/in-other-languages|Scalability and performance in other languages]]: the same languages measuring latency
- [[dsa/02-data-structures/01-arrays|Arrays]]: what the Fenwick tree is built on
