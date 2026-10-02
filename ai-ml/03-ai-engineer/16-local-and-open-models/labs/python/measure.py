"""measure.py — time one prompt through Ollama's HTTP API and report what decides the speed.
Needs Ollama running locally. Usage:
    python3 measure.py qwen3.5:4b                 # Ollama decides where layers go
    python3 measure.py qwen3.5:4b --cpu           # force CPU only (num_gpu 0)
    python3 measure.py qwen3.5:4b --think         # let the model think first
"""
import json
import sys
import urllib.request

PROMPT = "Explain a token bucket in two sentences."


def measure(model: str, cpu_only: bool, think: bool) -> dict:
    body = {"model": model, "prompt": PROMPT, "stream": False, "think": think,
            "options": {"num_gpu": 0} if cpu_only else {}}
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        r = json.load(resp)
    ns = 1e9  # Ollama reports durations in nanoseconds
    return {
        "load_s": round(r["load_duration"] / ns, 1),
        "prompt_tokens": r["prompt_eval_count"],
        "prompt_rate": round(r["prompt_eval_count"] / (r["prompt_eval_duration"] / ns), 1),
        "output_tokens": r["eval_count"],
        "output_rate": round(r["eval_count"] / (r["eval_duration"] / ns), 2),
        "total_s": round(r["total_duration"] / ns, 1),
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    print(measure(args[0], cpu_only="--cpu" in args, think="--think" in args))
