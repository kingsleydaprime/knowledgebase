"""Prompts as files, rendered with Jinja2. The files are shared with every other language's lab."""
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader, StrictUndefined

SHARED = Path(__file__).parent.parent / "shared"

# StrictUndefined: a missing value raises instead of quietly rendering as "". autoescape stays off:
# this is a prompt, not HTML, so "&" and quotes must reach the model unchanged.
templates = Environment(loader=FileSystemLoader(SHARED / "prompts"), undefined=StrictUndefined,
                        autoescape=False, keep_trailing_newline=True)

Label = Literal["positive", "negative", "mixed"]


def render(name: str, **values: str) -> str:
    return templates.get_template(f"{name}.md").render(**values)


def fence_user_text(text: str) -> str:
    """Stop user text from closing the <review> tag early. Lowers injection risk; doesn't remove it."""
    return re.sub(r"</?review>", lambda m: m.group(0).replace("<", "&lt;", 1), text, flags=re.I)


def format_examples(examples: list[dict]) -> str:
    """Few-shot examples in exactly the format of the real question."""
    return "\n\n".join(f"<review>\n{fence_user_text(e['review'])}\n</review>\n{e['label']}" for e in examples)


def parse_label(reply: str) -> Label | None:
    found = set(re.findall(r"\b(positive|negative|mixed)\b", reply.lower()))
    return found.pop() if len(found) == 1 else None


def load_reviews() -> tuple[list[dict], list[dict]]:
    data = json.loads((SHARED / "reviews.json").read_text())
    return data["examples"], data["cases"]


def evaluate(ask: Callable[[str], str], prompt: str, cases: list[dict], examples: list[dict]) -> dict:
    """Score a prompt against labelled cases, so "this wording feels better" becomes a number."""
    failures, correct = [], 0
    for case in cases:
        values = {"review": fence_user_text(case["review"])}
        if prompt == "classify-few-shot":
            values["examples"] = format_examples(examples)
        reply = ask(render(prompt, **values))
        got = parse_label(reply)
        if got == case["label"]:
            correct += 1
        else:
            failures.append({"review": case["review"], "expected": case["label"], "got": got, "reply": reply})
    return {"correct": correct, "total": len(cases), "accuracy": correct / len(cases), "failures": failures}
