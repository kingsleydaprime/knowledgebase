"""What an uploaded file really is, what an image costs, the three providers' formats, and checked extraction.
The same results as the TypeScript lab; reuses the structured-output lab's Pydantic invoice."""
import base64
import json
import math
import struct
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "11-structured-output" / "labs" / "python"))
from pydantic import ValidationError  # noqa: E402

from invoice import Invoice, describe, json_object_text  # noqa: E402


def sniff(data: bytes) -> dict | None:
    """The type from the file's first bytes, never its name or Content-Type, which the sender controls."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])  # big-endian, from the IHDR chunk
        return {"type": "image/png", "width": width, "height": height}
    if data[:3] == b"\xff\xd8\xff":
        return {"type": "image/jpeg", **jpeg_size(data)}
    if data[:4] == b"GIF8":
        width, height = struct.unpack("<HH", data[6:10])  # little-endian
        return {"type": "image/gif", "width": width, "height": height}
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return {"type": "image/webp"}
    return None


def jpeg_size(data: bytes) -> dict:
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            return {}
        marker, length = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):  # a start-of-frame segment
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return {"width": width, "height": height}
        i += 2 + length
    return {}


HIGH_RES = {"max_long_edge": 2576, "max_tokens": 4784}  # Anthropic, 2026-10: Opus 4.7+ and Sonnet 5+
STANDARD = {"max_long_edge": 1568, "max_tokens": 1600}  # earlier models


def fit(width: int, height: int, limits: dict) -> dict:
    """Scaled to the model's limits, and tokens ≈ width × height / 750 (Anthropic's documented approximation)."""
    scale = min(1, limits["max_long_edge"] / max(width, height))
    if width * scale * (height * scale) / 750 > limits["max_tokens"]:
        scale *= math.sqrt(limits["max_tokens"] / (width * scale * (height * scale) / 750))
    w, h = math.floor(width * scale), math.floor(height * scale)
    return {"width": w, "height": h, "tokens": math.ceil(w * h / 750)}


def shrink_to(width: int, height: int, long_edge: int) -> tuple[int, int]:
    s = min(1, long_edge / max(width, height))
    return round(width * s), round(height * s)


def image_message(data: bytes, question: str, provider: str) -> dict:
    info = sniff(data)
    if not info:
        raise ValueError("not a supported image")
    b64 = base64.b64encode(data).decode()
    if provider == "anthropic":
        return {"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": info["type"], "data": b64}},
                                            {"type": "text", "text": question}]}
    if provider == "openai":
        return {"role": "user", "content": [{"type": "text", "text": question},
                                            {"type": "image_url", "image_url": {"url": f"data:{info['type']};base64,{b64}"}}]}
    return {"role": "user", "content": question, "images": [b64]}  # Ollama's own /api/chat


EXTRACT_PROMPT = """Read this invoice and reply with JSON only, in the invoice schema.
If you can't read a value, don't guess: reply {"unreadable": "<which field>"}."""

See = Callable[[bytes, str], Awaitable[str]]


async def extract_invoice(see: See, data: bytes) -> dict:
    """Image in, checked data out: the structured-output lab's Pydantic model checks shape and arithmetic."""
    if not sniff(data):
        return {"ok": False, "reason": "not a supported image"}
    try:
        text = json_object_text(await see(data, EXTRACT_PROMPT))
    except ValueError:
        return {"ok": False, "reason": "no JSON in the reply"}
    if "unreadable" in (parsed := json.loads(text)):
        return {"ok": False, "reason": f"unreadable: {parsed['unreadable']}"}
    try:
        return {"ok": True, "invoice": Invoice.model_validate_json(text)}
    except ValidationError as error:
        return {"ok": False, "reason": describe(error)}
