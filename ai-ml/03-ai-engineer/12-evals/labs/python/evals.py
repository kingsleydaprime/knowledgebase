"""An eval harness: golden set, exact-match scoring, error bars, case-by-case comparison, a CI gate,
baselines, and the checks on an LLM judge. Reads the same golden set as every other language."""
import json
import math
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

GOLDEN = Path(__file__).parent.parent / "shared" / "golden.jsonl"
LABELS = ("bug", "billing", "feature", "other")
Classify = Callable[[str], str]  # ticket -> raw reply


def load_golden(path: Path = GOLDEN) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def parse_label(reply: str) -> str | None:
    found = set(re.findall(r"\b(bug|billing|feature|other)\b", reply.lower()))
    return found.pop() if len(found) == 1 else None


def wilson(passed: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Where the true pass rate probably lies (95%), given a small sample."""
    if total == 0:
        return 0.0, 1.0
    p = passed / total
    centre = p + z * z / (2 * total)
    spread = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
    return (centre - spread) / (1 + z * z / total), (centre + spread) / (1 + z * z / total)


@dataclass
class Result:
    results: list[dict]
    by_tag: dict[str, list[int]] = field(default_factory=dict)  # tag -> [passed, total]

    @property
    def passed(self) -> int:
        return sum(r["pass"] for r in self.results)

    @property
    def rate(self) -> float:
        return self.passed / len(self.results)

    @property
    def interval(self) -> tuple[float, float]:
        return wilson(self.passed, len(self.results))


def run_eval(classify: Classify, cases: list[dict]) -> Result:
    result = Result([])
    for case in cases:
        reply = classify(case["ticket"])
        got = parse_label(reply)
        result.results.append({"id": case["id"], "expected": case["label"], "got": got, "reply": reply,
                               "pass": got == case["label"]})
        for tag in case["tags"]:
            counts = result.by_tag.setdefault(tag, [0, 0])
            counts[0] += got == case["label"]
            counts[1] += 1
    return result


def compare(before: Result, after: Result) -> dict[str, list[str]]:
    was = {r["id"]: r["pass"] for r in before.results}
    return {"fixed": [r["id"] for r in after.results if r["pass"] and was.get(r["id"]) is False],
            "broke": [r["id"] for r in after.results if not r["pass"] and was.get(r["id"]) is True]}


def gate(result: Result, min_rate: float, baseline: Result | None = None, must_pass: tuple[str, ...] = ()) -> list[str]:
    """The reasons to fail the build; an empty list means the change may merge."""
    reasons = []
    if result.rate < min_rate:
        reasons.append(f"pass rate {result.rate:.0%} is below the floor of {min_rate:.0%}")
    if baseline and (broke := compare(baseline, result)["broke"]):
        reasons.append(f"regressed on {', '.join(broke)}")
    passed = {r["id"] for r in result.results if r["pass"]}
    reasons += [f"must-pass case {case_id} failed" for case_id in must_pass if case_id not in passed]
    return reasons


def majority(cases: list[dict]) -> Classify:
    top = Counter(c["label"] for c in cases).most_common(1)[0][0]
    return lambda _ticket: top


def keywords(ticket: str) -> str:
    t = ticket.lower()
    if re.search(r"charg|refund|invoice|pay|price|subscription|discount|receipt", t):
        return "billing"
    if re.search(r"crash|error|broken|bug|blank|empty|doesn't work|not working", t):
        return "bug"
    if re.search(r"add|would be great|should support|could you|please support", t):
        return "feature"
    return "other"


def pairwise(ask: Callable[[str], str], ticket: str, a: str, b: str) -> str:
    """Ask in both orders; a judge that prefers whatever comes first is caught, not trusted."""
    def prompt(first: str, second: str) -> str:
        return (f"Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n{ticket}\n"
                f"</ticket>\n<first>\n{first}\n</first>\n<second>\n{second}\n</second>")

    def pick(answer: str) -> str | None:
        return "first" if re.search(r"\bfirst\b", answer, re.I) else "second" if re.search(r"\bsecond\b", answer, re.I) else None

    forward, backward = pick(ask(prompt(a, b))), pick(ask(prompt(b, a)))
    return {("first", "second"): "a", ("second", "first"): "b"}.get((forward, backward), "inconsistent")


def agreement(judge_says: list[bool], human_says: list[bool]) -> tuple[float, float]:
    """(agreement, Cohen's kappa). Kappa removes the agreement you'd expect by chance."""
    n = len(judge_says)
    agree = sum(j == h for j, h in zip(judge_says, human_says)) / n
    judge_yes, human_yes = sum(judge_says) / n, sum(human_says) / n
    chance = judge_yes * human_yes + (1 - judge_yes) * (1 - human_yes)
    return agree, 1.0 if chance == 1 else (agree - chance) / (1 - chance)
