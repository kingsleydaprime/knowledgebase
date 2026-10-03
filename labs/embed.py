"""Fill a lesson's {{path}} placeholder lines with that lab file's contents, fenced.

    python3 labs/embed.py ai-ml/03-ai-engineer/02-how-llms-work/in-other-languages.md

Paths are relative to the lesson's labs/ folder, e.g. {{python/decoding.py}}, alone on a line.
Run it once after writing a lesson; after that, `labs/run.py --sync` keeps the code in step.
"""
import pathlib, re, sys

FENCE = {".ts": "ts", ".proto": "protobuf", ".py": "python", ".go": "go", ".java": "java", ".rs": "rust", ".c": "c",
         ".cpp": "cpp", ".cs": "csharp", ".json": "json", ".jsonl": "json", ".md": "markdown", ".sh": "sh", ".yml": "yaml"}

lesson = pathlib.Path(sys.argv[1])
labs = lesson.parent / "labs"

def fenced(m: re.Match) -> str:
    f = labs / m.group(1)
    return f"```{FENCE.get(f.suffix, '')}\n{f.read_text().rstrip()}\n```"

lesson.write_text(re.sub(r"^\{\{([\w./-]+)\}\}$", fenced, lesson.read_text(), flags=re.M))
