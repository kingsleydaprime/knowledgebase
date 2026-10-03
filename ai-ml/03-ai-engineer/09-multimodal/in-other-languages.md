# Multimodal in Other Languages

> **[Intermediate]** · A companion to [[ai-ml/03-ai-engineer/09-multimodal/index|multimodal]], which checks an upload's real type, estimates an image's token cost, builds the message in three providers' formats and extracts a checked invoice from an image in TypeScript. This page does the same in Python, Go, Java, Rust and C#, with the same results, and each lab's extraction reuses **that language's structured-output lab**. Reading binary formats is where languages differ most visibly here: byte order, unsigned types, how bytes are written in source code, and even how each language rounds a half.

## Before you start

You can already:

- Explain magic bytes, the image token estimate and the extraction checks → [[ai-ml/03-ai-engineer/09-multimodal/index|the main lesson]].
- Read your language's structured-output lab → [[ai-ml/03-ai-engineer/11-structured-output/in-other-languages|structured output in other languages]].

After this lesson you will be able to:

1. Read big-endian and little-endian integers from a byte buffer in your language.
2. Name your ecosystem's image libraries, and why you might not need them just to identify a file.
3. Say how your language rounds a half, and when that changes a result.

## The kid version

Every image file starts with a short secret handshake: a PNG always begins with the same eight bytes, a JPEG with three others. Six people check the handshake, each reading the bytes with their own tools. Some read numbers starting from the biggest end, some from the smallest, depending on the file type, and they all have to read them the same way to get the same width and height.

**Where the analogy stops working.** A handshake is easy to fake. Magic bytes tell you what format a file claims to be, not that it's a safe or complete one; a real decoder can still find a broken file inside.

## 1. The tools, by ecosystem

| Language | Read integers from bytes | Base64 | Image libraries | Identify a file |
|---|---|---|---|---|
| TypeScript | `Buffer.readUInt32BE` | `Buffer.toString("base64")` | sharp | by hand, or `file-type` |
| Python | **`struct.unpack(">II", …)`** | `base64` | **Pillow** | by hand, or Pillow's `Image.open` |
| Go | **`encoding/binary`** | `encoding/base64` | `image`, `image/png`, `image/jpeg` | **`http.DetectContentType`** |
| Java | **`ByteBuffer`** (big-endian by default) | `java.util.Base64` | ImageIO | ImageIO, Apache Tika |
| Rust | **`u32::from_be_bytes`** | the **`base64`** crate (none in the standard library) | the **`image`** crate | by hand, or `infer` |
| C# | **`BinaryPrimitives`** | `Convert.ToBase64String` | ImageSharp, SkiaSharp | by hand |
| C, C++ | — | — | — | — |

For resizing before upload, use the library in bold: shrinking an image needs a real decoder and encoder. To *identify* a file and read its size, the labs read the header by hand, which is a few lines and needs no dependency. Go's standard library can already identify a file from its first 512 bytes, but only returns the type, not the size. There's no C or C++ section, for the same reason as in the other AI-engineering companions; in C, libpng or stb_image are the usual way in.

## 2. What changes between languages

### Byte order and unsigned numbers

A PNG stores its width and height as **big-endian** 32-bit integers (most significant byte first); a GIF stores its as **little-endian** 16-bit ones. Every language can read both, and every lab says which it means: `struct.unpack(">II")` and `"<HH"` in Python, `binary.BigEndian` and `binary.LittleEndian` in Go, `from_be_bytes` and `from_le_bytes` in Rust, `BinaryPrimitives.ReadUInt32BigEndian` in C#. Java's `ByteBuffer` is big-endian unless told otherwise, and Java has no unsigned `short`, so reading a 16-bit size needs `& 0xffff` to keep values over 32,767 from turning negative.

### Bytes in source code

Python's `b"\x89PNG"`, Rust's `b"\x89PNG"`, C#'s `"GIF8"u8` and Go's `[]byte("\x89PNG")` all write bytes directly. Java has no byte-string literal, so its lab writes signatures as `byte[]` arrays: building them from a `String` would mean choosing a character encoding, and getting it wrong changes the bytes.

### Rounding a half

Shrinking an image to a target size rounds. Languages disagree on halves: JavaScript's `Math.round` and Java's `Math.round` round 2.5 up to 3; Go's `math.Round` and Rust's `round` round halves away from zero; Python's `round` and C#'s `Math.Round` round **to the nearest even number** by default, so 2.5 becomes 2. The lab's sizes never land on a half, so every language agrees, but a resize that lands on 767.5 pixels would give 768 in one language and 767 in another. The C# lab passes `MidpointRounding.AwayFromZero` to match the others.

## 3. The same results, in every language

| Check | Expected in every language |
|---|---|
| a PNG header | `image/png`, 1200 × 800 |
| a JPEG header | `image/jpeg`, 4000 × 3000 |
| a GIF header | `image/gif`, 320 × 240 |
| a shell script, an SVG | refused |
| 4000 × 3000 on a high-resolution model | 2187 × 1640, 4,783 tokens |
| the same on an earlier model | 1264 × 948, 1,598 tokens |
| shrunk to 1,024 px first | 1024 × 768, 1,049 tokens |
| extraction with a misread total | `line items add up to 1730 cents but total_cents is 1780` |
| `{"unreadable": "due_date"}` | `unreadable: due_date` |

The message JSON is the same data in every language, but not always the same bytes: Go's `json.Marshal` sorts map keys, so its `source` object comes out as `data`, `media_type`, `type`.

## Terms used in this lesson

1. **Endianness**: This is the order of bytes in a multi-byte number. **Big-endian** puts the most significant byte first; **little-endian** puts the least significant first.
2. **Unsigned integer**: This is an integer type with no negative values, so all its bits hold magnitude. Java has unsigned arithmetic helpers but no unsigned 16-bit type.
3. **Byte-string literal**: This is source code that writes raw bytes directly, such as `b"\x89PNG"`, rather than text that must be encoded into bytes.
4. **Banker's rounding**: This is also called **round half to even**. It rounds a number exactly halfway between two integers to the even one, so 2.5 becomes 2 and 3.5 becomes 4.

## 4. Python

`struct.unpack` reads the sizes with a format string: `>` for big-endian, `<` for little-endian, `I` for a 32-bit and `H` for a 16-bit unsigned integer. Extraction reuses the structured-output lab's Pydantic `Invoice`, whose validator checks the arithmetic; Pydantic prefixes its message with "Value error, ", so the test checks that the message contains the shared wording. Python's `round` rounds halves to even, which `shrink_to` never hits with these sizes.

```python
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
```

```python
import base64
import json
import struct
import unittest

from multimodal import HIGH_RES, STANDARD, extract_invoice, fit, image_message, shrink_to, sniff

# Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
PNG = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 1200, 800) + bytes(5)
JPEG = (b"\xff\xd8" + b"\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", 3000, 4000) + b"\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01")
GOOD = {"vendor": "Paper Co", "invoice_number": "INV-7", "currency": "GBP", "due_date": "2026-10-15",
        "line_items": [{"description": "A4 paper", "amount_cents": 1250}, {"description": "Pens", "amount_cents": 480}], "total_cents": 1730}


def reply(value):
    async def see(data, prompt):
        return value if isinstance(value, str) else f"Here you go: {json.dumps(value)}"
    return see


class Multimodal(unittest.IsolatedAsyncioTestCase):
    def test_the_type_comes_from_the_bytes(self):
        self.assertEqual(sniff(PNG), {"type": "image/png", "width": 1200, "height": 800})
        self.assertEqual(sniff(JPEG), {"type": "image/jpeg", "width": 4000, "height": 3000})
        self.assertEqual(sniff(b"GIF89a\x40\x01\xf0\x00"), {"type": "image/gif", "width": 320, "height": 240})
        self.assertIsNone(sniff(b"#!/bin/sh\nrm -rf /\n"))
        self.assertIsNone(sniff(b"<svg onload=alert(1)>"))

    def test_what_a_photo_costs(self):
        self.assertEqual(fit(4000, 3000, HIGH_RES), {"width": 2187, "height": 1640, "tokens": 4783})
        self.assertEqual(fit(4000, 3000, STANDARD), {"width": 1264, "height": 948, "tokens": 1598})
        self.assertEqual(fit(*shrink_to(4000, 3000, 1024), HIGH_RES), {"width": 1024, "height": 768, "tokens": 1049})
        self.assertEqual(fit(1920, 1080, HIGH_RES), {"width": 1920, "height": 1080, "tokens": 2765})

    def test_three_formats(self):
        b64 = base64.b64encode(PNG).decode()
        self.assertEqual(image_message(PNG, "What is this?", "anthropic")["content"][0],
                         {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}})
        self.assertEqual(image_message(PNG, "What is this?", "openai")["content"][1]["image_url"]["url"], f"data:image/png;base64,{b64}")
        self.assertEqual(image_message(PNG, "What is this?", "ollama"), {"role": "user", "content": "What is this?", "images": [b64]})
        with self.assertRaisesRegex(ValueError, "not a supported image"):
            image_message(b"not an image", "?", "openai")

    async def test_checked_extraction(self):
        ok = await extract_invoice(reply(GOOD), PNG)
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["invoice"].total_cents, 1730)
        misread = await extract_invoice(reply({**GOOD, "total_cents": 1780}), PNG)
        self.assertFalse(misread["ok"])
        self.assertIn("line items add up to 1730 cents but total_cents is 1780", misread["reason"])  # Pydantic adds "Value error, "
        self.assertEqual(await extract_invoice(reply({"unreadable": "due_date"}), PNG), {"ok": False, "reason": "unreadable: due_date"})
        self.assertEqual(await extract_invoice(reply("I can't see an invoice."), PNG), {"ok": False, "reason": "no JSON in the reply"})
        self.assertEqual(await extract_invoice(reply(GOOD), b"%PDF-1.7"), {"ok": False, "reason": "not a supported image"})


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/09-multimodal/labs/python). `python3 labs/run.py multimodal/python`.

## 5. Go

`encoding/binary` reads both byte orders, and `http.DetectContentType` identifies a file from its first bytes with no code at all, though it doesn't report the size. The message is built as `map[string]any`, and `json.Marshal` writes map keys in sorted order, which the test spells out. The `"unreadable"` answer is decoded into a small struct rather than picked out of the text. Extraction calls the structured-output lab's `invoice.Parse`, imported with a `replace` directive.

```go
// Package multimodal: what an uploaded file really is, what an image costs, the three providers' formats,
// and checked extraction. The same results as the TypeScript lab; reuses the structured-output lab's Parse.
package multimodal

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"errors"
	"math"
	"net/http"
	"strings"

	"invoice"
)

type Info struct {
	Type          string
	Width, Height int
}

// Sniff decides the type from the file's first bytes, never its name or Content-Type.
func Sniff(b []byte) (Info, bool) {
	switch {
	case bytes.HasPrefix(b, []byte("\x89PNG\r\n\x1a\n")) && len(b) >= 24:
		return Info{"image/png", int(binary.BigEndian.Uint32(b[16:])), int(binary.BigEndian.Uint32(b[20:]))}, true
	case bytes.HasPrefix(b, []byte{0xff, 0xd8, 0xff}):
		w, h := jpegSize(b)
		return Info{"image/jpeg", w, h}, true
	case bytes.HasPrefix(b, []byte("GIF8")) && len(b) >= 10:
		return Info{"image/gif", int(binary.LittleEndian.Uint16(b[6:])), int(binary.LittleEndian.Uint16(b[8:]))}, true
	case len(b) >= 12 && string(b[:4]) == "RIFF" && string(b[8:12]) == "WEBP":
		return Info{Type: "image/webp"}, true
	}
	return Info{}, false
}

func jpegSize(b []byte) (width, height int) {
	for i := 2; i+9 < len(b); {
		if b[i] != 0xff {
			return 0, 0
		}
		marker, length := b[i+1], int(binary.BigEndian.Uint16(b[i+2:]))
		if marker >= 0xc0 && marker <= 0xcf && marker != 0xc4 && marker != 0xc8 && marker != 0xcc { // start of frame
			return int(binary.BigEndian.Uint16(b[i+7:])), int(binary.BigEndian.Uint16(b[i+5:]))
		}
		i += 2 + length
	}
	return 0, 0
}

// The standard library's own sniffer reads magic bytes too, but returns only a type, and recognises
// more formats than you may want to accept.
func StdlibType(b []byte) string { return http.DetectContentType(b) }

type Limits struct{ MaxLongEdge, MaxTokens float64 }

var (
	HighRes  = Limits{2576, 4784} // Anthropic, 2026-10: Opus 4.7+ and Sonnet 5+
	Standard = Limits{1568, 1600} // earlier models
)

type Fitted struct{ Width, Height, Tokens int }

// Fit scales to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation).
func Fit(width, height float64, l Limits) Fitted {
	scale := math.Min(1, l.MaxLongEdge/math.Max(width, height))
	if t := width * scale * (height * scale) / 750; t > l.MaxTokens {
		scale *= math.Sqrt(l.MaxTokens / t)
	}
	w, h := math.Floor(width*scale), math.Floor(height*scale)
	return Fitted{int(w), int(h), int(math.Ceil(w * h / 750))}
}

func ShrinkTo(width, height, longEdge float64) (float64, float64) {
	s := math.Min(1, longEdge/math.Max(width, height))
	return math.Round(width * s), math.Round(height * s)
}

// ImageMessage builds the user message in each provider's shape, as a map ready for json.Marshal.
func ImageMessage(b []byte, question, provider string) (map[string]any, error) {
	info, ok := Sniff(b)
	if !ok {
		return nil, errors.New("not a supported image")
	}
	data := base64.StdEncoding.EncodeToString(b)
	switch provider {
	case "anthropic":
		return map[string]any{"role": "user", "content": []any{
			map[string]any{"type": "image", "source": map[string]any{"type": "base64", "media_type": info.Type, "data": data}},
			map[string]any{"type": "text", "text": question},
		}}, nil
	case "openai":
		return map[string]any{"role": "user", "content": []any{
			map[string]any{"type": "text", "text": question},
			map[string]any{"type": "image_url", "image_url": map[string]any{"url": "data:" + info.Type + ";base64," + data}},
		}}, nil
	}
	return map[string]any{"role": "user", "content": question, "images": []string{data}}, nil // Ollama's own /api/chat
}

const ExtractPrompt = `Read this invoice and reply with JSON only, in the invoice schema.
If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.`

type See func(ctx context.Context, image []byte, prompt string) (string, error)

// ExtractInvoice: image in, checked data out. The structured-output lab's Parse checks shape and arithmetic.
func ExtractInvoice(ctx context.Context, see See, b []byte) (invoice.Invoice, error) {
	if _, ok := Sniff(b); !ok {
		return invoice.Invoice{}, errors.New("not a supported image")
	}
	reply, err := see(ctx, b, ExtractPrompt)
	if err != nil {
		return invoice.Invoice{}, err
	}
	var probe struct { // "I can't read this" is an answer, not an error
		Unreadable string `json:"unreadable"`
	}
	if start, end := strings.Index(reply, "{"), strings.LastIndex(reply, "}"); start >= 0 && end > start &&
		json.Unmarshal([]byte(reply[start:end+1]), &probe) == nil && probe.Unreadable != "" {
		return invoice.Invoice{}, errors.New("unreadable: " + probe.Unreadable)
	}
	inv, err := invoice.Parse(reply)
	if err != nil && err.Error() == "no JSON object in the reply" {
		return inv, errors.New("no JSON in the reply")
	}
	return inv, err
}
```

```go
package multimodal

import (
	"context"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"strings"
	"testing"
)

// Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
func pngHeader(w, h uint32) []byte {
	b := append([]byte("\x89PNG\r\n\x1a\n"), 0, 0, 0, 13)
	b = append(b, "IHDR"...)
	b = binary.BigEndian.AppendUint32(b, w)
	b = binary.BigEndian.AppendUint32(b, h)
	return append(b, 8, 0, 0, 0, 0)
}

func jpegHeader(w, h uint16) []byte {
	b := []byte{0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 'J', 'F', 'I', 'F', 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0xff, 0xc0, 0x00, 0x11, 0x08}
	b = binary.BigEndian.AppendUint16(b, h)
	b = binary.BigEndian.AppendUint16(b, w)
	return append(b, 3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1)
}

func TestTheTypeComesFromTheBytes(t *testing.T) {
	if info, _ := Sniff(pngHeader(1200, 800)); info != (Info{"image/png", 1200, 800}) {
		t.Error(info)
	}
	if info, _ := Sniff(jpegHeader(4000, 3000)); info != (Info{"image/jpeg", 4000, 3000}) {
		t.Error(info)
	}
	if info, _ := Sniff([]byte("GIF89a\x40\x01\xf0\x00")); info != (Info{"image/gif", 320, 240}) {
		t.Error(info)
	}
	for _, bad := range []string{"#!/bin/sh\nrm -rf /\n", "<svg onload=alert(1)>"} {
		if _, ok := Sniff([]byte(bad)); ok {
			t.Errorf("accepted %q", bad)
		}
	}
	if got := StdlibType(pngHeader(1, 1)); got != "image/png" {
		t.Error(got) // the standard library agrees on the type, but doesn't give the size
	}
}

func TestWhatAPhotoCosts(t *testing.T) {
	cases := map[Fitted]Fitted{
		Fit(4000, 3000, HighRes):  {2187, 1640, 4783},
		Fit(4000, 3000, Standard): {1264, 948, 1598},
		Fit(1920, 1080, HighRes):  {1920, 1080, 2765},
	}
	for got, want := range cases {
		if got != want {
			t.Errorf("got %v, want %v", got, want)
		}
	}
	if w, h := ShrinkTo(4000, 3000, 1024); Fit(w, h, HighRes) != (Fitted{1024, 768, 1049}) {
		t.Error(w, h)
	}
}

func TestThreeFormats(t *testing.T) {
	png := pngHeader(4, 4)
	data := base64.StdEncoding.EncodeToString(png)
	anthropic, _ := ImageMessage(png, "What is this?", "anthropic")
	openai, _ := ImageMessage(png, "What is this?", "openai")
	ollama, _ := ImageMessage(png, "What is this?", "ollama")
	a, _ := json.Marshal(anthropic["content"].([]any)[0])
	o, _ := json.Marshal(openai["content"].([]any)[1])
	l, _ := json.Marshal(ollama)
	if string(a) != `{"source":{"data":"`+data+`","media_type":"image/png","type":"base64"},"type":"image"}` { // json.Marshal sorts map keys
		t.Error(string(a))
	}
	if string(o) != `{"image_url":{"url":"data:image/png;base64,`+data+`"},"type":"image_url"}` {
		t.Error(string(o))
	}
	if string(l) != `{"content":"What is this?","images":["`+data+`"],"role":"user"}` {
		t.Error(string(l))
	}
	if _, err := ImageMessage([]byte("not an image"), "?", "openai"); err == nil {
		t.Error("should refuse")
	}
}

func TestCheckedExtraction(t *testing.T) {
	good := `{"vendor":"Paper Co","invoice_number":"INV-7","currency":"GBP","due_date":"2026-10-15",` +
		`"line_items":[{"description":"A4 paper","amount_cents":1250},{"description":"Pens","amount_cents":480}],"total_cents":1730}`
	reply := func(text string) See {
		return func(context.Context, []byte, string) (string, error) { return "Here you go: " + text, nil }
	}
	png, ctx := pngHeader(8, 8), context.Background()
	if inv, err := ExtractInvoice(ctx, reply(good), png); err != nil || inv.TotalCents != 1730 {
		t.Fatal(inv, err)
	}
	misread := strings.Replace(good, `"total_cents":1730`, `"total_cents":1780`, 1)
	for text, want := range map[string]string{
		misread:                      "line items add up to 1730 cents but total_cents is 1780",
		`{"unreadable": "due_date"}`: "unreadable: due_date",
		"I can't see an invoice.":    "no JSON in the reply",
	} {
		if _, err := ExtractInvoice(ctx, reply(text), png); err == nil || err.Error() != want {
			t.Errorf("got %v, want %q", err, want)
		}
	}
	if _, err := ExtractInvoice(ctx, reply(good), []byte("%PDF-1.7")); err == nil || err.Error() != "not a supported image" {
		t.Error(err)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/09-multimodal/labs/go). `python3 labs/run.py multimodal/go`.

## 6. Java

`ByteBuffer.wrap(bytes).getInt(16)` reads a big-endian integer at an offset; `.order(ByteOrder.LITTLE_ENDIAN)` switches for GIF, and `& 0xffff` turns Java's signed `short` into the unsigned size. Signatures are `byte[]` arrays, since Java has no byte-string literal. The messages use Jackson 2's `ObjectNode`, the same Jackson the structured-output lab's `Invoices.parse` uses, so the two compile together.

```java
package multimodal;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import invoice.Invoices;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;
import java.util.function.BiFunction;

/** What an uploaded file really is, what an image costs, the three providers' formats, and checked extraction.
 *  The same results as the TypeScript lab; reuses the structured-output lab's Invoices.parse. */
public final class Multimodal {
    private Multimodal() {}

    static final ObjectMapper JSON = new ObjectMapper();

    /** type is null when the bytes aren't a supported image; width and height are 0 when unknown. */
    public record Info(String type, int width, int height) {}

    static final byte[] PNG_SIGNATURE = {(byte) 0x89, 'P', 'N', 'G', '\r', '\n', 0x1a, '\n'};

    static boolean startsWith(byte[] b, byte... prefix) {
        return b.length >= prefix.length && Arrays.equals(Arrays.copyOf(b, prefix.length), prefix);
    }

    static boolean startsWith(byte[] b, String prefix) {
        return startsWith(b, prefix.getBytes(StandardCharsets.ISO_8859_1));
    }

    /** The type from the file's first bytes, never its name or Content-Type. */
    public static Info sniff(byte[] b) {
        if (startsWith(b, PNG_SIGNATURE) && b.length >= 24) {
            var be = ByteBuffer.wrap(b); // big-endian by default
            return new Info("image/png", be.getInt(16), be.getInt(20));
        }
        if (startsWith(b, (byte) 0xff, (byte) 0xd8, (byte) 0xff)) return jpeg(b);
        if (startsWith(b, "GIF8") && b.length >= 10) {
            var le = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN);
            return new Info("image/gif", le.getShort(6) & 0xffff, le.getShort(8) & 0xffff); // Java has no unsigned short
        }
        if (startsWith(b, "RIFF") && b.length >= 12 && new String(b, 8, 4, StandardCharsets.ISO_8859_1).equals("WEBP")) return new Info("image/webp", 0, 0);
        return new Info(null, 0, 0);
    }

    static Info jpeg(byte[] b) {
        var be = ByteBuffer.wrap(b);
        for (int i = 2; i + 9 < b.length; ) {
            if ((b[i] & 0xff) != 0xff) break;
            int marker = b[i + 1] & 0xff, length = be.getShort(i + 2) & 0xffff;
            if (marker >= 0xc0 && marker <= 0xcf && marker != 0xc4 && marker != 0xc8 && marker != 0xcc) {
                return new Info("image/jpeg", be.getShort(i + 7) & 0xffff, be.getShort(i + 5) & 0xffff);
            }
            i += 2 + length;
        }
        return new Info("image/jpeg", 0, 0);
    }

    public record Limits(double maxLongEdge, double maxTokens) {}

    public static final Limits HIGH_RES = new Limits(2576, 4784); // Anthropic, 2026-10: Opus 4.7+ and Sonnet 5+
    public static final Limits STANDARD = new Limits(1568, 1600); // earlier models

    public record Fitted(int width, int height, int tokens) {}

    /** Scaled to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation). */
    public static Fitted fit(double width, double height, Limits l) {
        double scale = Math.min(1, l.maxLongEdge() / Math.max(width, height));
        double tokens = width * scale * (height * scale) / 750;
        if (tokens > l.maxTokens()) scale *= Math.sqrt(l.maxTokens() / tokens);
        double w = Math.floor(width * scale), h = Math.floor(height * scale);
        return new Fitted((int) w, (int) h, (int) Math.ceil(w * h / 750));
    }

    public static double[] shrinkTo(double width, double height, double longEdge) {
        double s = Math.min(1, longEdge / Math.max(width, height));
        return new double[] {Math.round(width * s), Math.round(height * s)};
    }

    public static ObjectNode imageMessage(byte[] b, String question, String provider) {
        var info = sniff(b);
        if (info.type() == null) throw new IllegalArgumentException("not a supported image");
        String data = Base64.getEncoder().encodeToString(b);
        var message = JSON.createObjectNode().put("role", "user");
        switch (provider) {
            case "anthropic" -> {
                var content = message.putArray("content");
                content.addObject().put("type", "image").putObject("source").put("type", "base64").put("media_type", info.type()).put("data", data);
                content.addObject().put("type", "text").put("text", question);
            }
            case "openai" -> {
                var content = message.putArray("content");
                content.addObject().put("type", "text").put("text", question);
                content.addObject().put("type", "image_url").putObject("image_url").put("url", "data:" + info.type() + ";base64," + data);
            }
            default -> message.put("content", question).putArray("images").add(data); // Ollama's own /api/chat
        }
        return message;
    }

    public static final String EXTRACT_PROMPT = """
            Read this invoice and reply with JSON only, in the invoice schema.
            If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.""";

    /** invoice is null when the extraction failed, and reason says why. */
    public record Extracted(Invoices.Invoice invoice, String reason) {}

    /** Image in, checked data out. The structured-output lab's parse checks shape and arithmetic. */
    public static Extracted extractInvoice(BiFunction<byte[], String, String> see, byte[] b) {
        if (sniff(b).type() == null) return new Extracted(null, "not a supported image");
        String reply = see.apply(b, EXTRACT_PROMPT);
        int start = reply.indexOf('{'), end = reply.lastIndexOf('}');
        if (start == -1 || end < start) return new Extracted(null, "no JSON in the reply");
        try {
            JsonNode probe = JSON.readTree(reply.substring(start, end + 1));
            if (probe.has("unreadable")) return new Extracted(null, "unreadable: " + probe.get("unreadable").asText());
        } catch (Exception e) {
            return new Extracted(null, "no JSON in the reply");
        }
        try {
            return new Extracted(Invoices.parse(reply), null);
        } catch (IllegalArgumentException e) {
            return new Extracted(null, e.getMessage());
        }
    }
}
```

```java
package multimodal;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import multimodal.Multimodal.Fitted;
import multimodal.Multimodal.Info;

/** Checks, run with `java -ea`. The same results as every other language. */
public final class MultimodalCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    /** Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.) */
    static byte[] pngHeader(int w, int h) {
        return ByteBuffer.allocate(29).put(Multimodal.PNG_SIGNATURE)
                .putInt(13).put("IHDR".getBytes(StandardCharsets.ISO_8859_1)).putInt(w).putInt(h).put(new byte[] {8, 0, 0, 0, 0}).array();
    }

    static byte[] jpegHeader(int w, int h) {
        var b = ByteBuffer.allocate(39);
        b.put(new byte[] {(byte) 0xff, (byte) 0xd8, (byte) 0xff, (byte) 0xe0, 0, 0x10, 'J', 'F', 'I', 'F', 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, (byte) 0xff, (byte) 0xc0, 0, 0x11, 8});
        return b.putShort((short) h).putShort((short) w).put(new byte[] {3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1}).array();
    }

    public static void main(String[] args) {
        check(Multimodal.sniff(pngHeader(1200, 800)).equals(new Info("image/png", 1200, 800)), "png");
        check(Multimodal.sniff(jpegHeader(4000, 3000)).equals(new Info("image/jpeg", 4000, 3000)), Multimodal.sniff(jpegHeader(4000, 3000)));
        byte[] gif = {'G', 'I', 'F', '8', '9', 'a', 0x40, 0x01, (byte) 0xf0, 0x00}; // 320 × 240, little-endian
        check(Multimodal.sniff(gif).equals(new Info("image/gif", 320, 240)), "gif");
        check(Multimodal.sniff("#!/bin/sh\nrm -rf /\n".getBytes()).type() == null && Multimodal.sniff("<svg onload=alert(1)>".getBytes()).type() == null, "refused");

        check(Multimodal.fit(4000, 3000, Multimodal.HIGH_RES).equals(new Fitted(2187, 1640, 4783)), Multimodal.fit(4000, 3000, Multimodal.HIGH_RES));
        check(Multimodal.fit(4000, 3000, Multimodal.STANDARD).equals(new Fitted(1264, 948, 1598)), "standard");
        double[] small = Multimodal.shrinkTo(4000, 3000, 1024);
        check(Multimodal.fit(small[0], small[1], Multimodal.HIGH_RES).equals(new Fitted(1024, 768, 1049)), "shrunk");
        check(Multimodal.fit(1920, 1080, Multimodal.HIGH_RES).equals(new Fitted(1920, 1080, 2765)), "screenshot");

        byte[] png = pngHeader(4, 4);
        String data = Base64.getEncoder().encodeToString(png);
        check(Multimodal.imageMessage(png, "What is this?", "anthropic").get("content").get(0).toString()
                .equals("{\"type\":\"image\",\"source\":{\"type\":\"base64\",\"media_type\":\"image/png\",\"data\":\"" + data + "\"}}"), "anthropic");
        check(Multimodal.imageMessage(png, "What is this?", "openai").get("content").get(1).get("image_url").get("url").asText()
                .equals("data:image/png;base64," + data), "openai");
        check(Multimodal.imageMessage(png, "What is this?", "ollama").toString()
                .equals("{\"role\":\"user\",\"content\":\"What is this?\",\"images\":[\"" + data + "\"]}"), "ollama");

        String good = "{\"vendor\":\"Paper Co\",\"invoice_number\":\"INV-7\",\"currency\":\"GBP\",\"due_date\":\"2026-10-15\","
                + "\"line_items\":[{\"description\":\"A4 paper\",\"amount_cents\":1250},{\"description\":\"Pens\",\"amount_cents\":480}],\"total_cents\":1730}";
        check(Multimodal.extractInvoice((b, p) -> "Here you go: " + good, png).invoice().totalCents() == 1730, "good");
        String misread = good.replace("\"total_cents\":1730", "\"total_cents\":1780");
        check(Multimodal.extractInvoice((b, p) -> misread, png).reason().equals("line items add up to 1730 cents but total_cents is 1780"), "misread");
        check(Multimodal.extractInvoice((b, p) -> "{\"unreadable\": \"due_date\"}", png).reason().equals("unreadable: due_date"), "unreadable");
        check(Multimodal.extractInvoice((b, p) -> "I can't see an invoice.", png).reason().equals("no JSON in the reply"), "no JSON");
        check(Multimodal.extractInvoice((b, p) -> good, "%PDF-1.7".getBytes()).reason().equals("not a supported image"), "pdf");

        System.out.println("all multimodal checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/09-multimodal/labs/java). `check.sh` compiles the structured-output lab's `Invoices.java` alongside and downloads its jars on the first run. `python3 labs/run.py multimodal/java`.

## 7. Rust

`sniff` is a `match` on slice patterns: `[0xff, 0xd8, 0xff, ..]` is a JPEG, and `[b'G', b'I', b'F', b'8', _, _, w0, w1, h0, h1, ..]` is a GIF whose size bytes are bound by name in the pattern. `u16::from_le_bytes` and `u32::from_be_bytes` turn them into numbers. Rust's standard library has no base64, so the lab uses the `base64` crate. Extraction calls the structured-output lab's `invoice::parse`, a path dependency.

```rust
//! What an uploaded file really is, what an image costs, the three providers' formats, and checked extraction.
//! The same results as the TypeScript lab; reuses the structured-output lab's `invoice::parse`.
use base64::Engine;
use base64::engine::general_purpose::STANDARD as BASE64;
use serde_json::{Value, json};

#[derive(Debug, PartialEq)]
pub struct Info {
    pub kind: &'static str,
    pub width: u32,
    pub height: u32,
}

const PNG_SIGNATURE: &[u8] = b"\x89PNG\r\n\x1a\n";

/// The type from the file's first bytes, never its name or Content-Type. Slice patterns read like the format.
pub fn sniff(b: &[u8]) -> Option<Info> {
    match b {
        _ if b.starts_with(PNG_SIGNATURE) && b.len() >= 24 => {
            let be = |i: usize| u32::from_be_bytes(b[i..i + 4].try_into().unwrap());
            Some(Info {
                kind: "image/png",
                width: be(16),
                height: be(20),
            })
        }
        [0xff, 0xd8, 0xff, ..] => Some(jpeg(b)),
        [b'G', b'I', b'F', b'8', _, _, w0, w1, h0, h1, ..] => Some(Info {
            kind: "image/gif",
            width: u16::from_le_bytes([*w0, *w1]).into(),
            height: u16::from_le_bytes([*h0, *h1]).into(),
        }),
        [
            b'R',
            b'I',
            b'F',
            b'F',
            _,
            _,
            _,
            _,
            b'W',
            b'E',
            b'B',
            b'P',
            ..,
        ] => Some(Info {
            kind: "image/webp",
            width: 0,
            height: 0,
        }),
        _ => None,
    }
}

fn jpeg(b: &[u8]) -> Info {
    let be16 = |i: usize| u32::from(u16::from_be_bytes([b[i], b[i + 1]]));
    let mut i = 2;
    while i + 9 < b.len() && b[i] == 0xff {
        let marker = b[i + 1];
        if (0xc0..=0xcf).contains(&marker) && ![0xc4, 0xc8, 0xcc].contains(&marker) {
            return Info {
                kind: "image/jpeg",
                width: be16(i + 7),
                height: be16(i + 5),
            };
        }
        i += 2 + be16(i + 2) as usize;
    }
    Info {
        kind: "image/jpeg",
        width: 0,
        height: 0,
    }
}

pub struct Limits {
    pub max_long_edge: f64,
    pub max_tokens: f64,
}

pub const HIGH_RES: Limits = Limits {
    max_long_edge: 2576.0,
    max_tokens: 4784.0,
}; // Anthropic, 2026-10: Opus 4.7+, Sonnet 5+
pub const STANDARD: Limits = Limits {
    max_long_edge: 1568.0,
    max_tokens: 1600.0,
}; // earlier models

/// Scaled to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation).
pub fn fit(width: f64, height: f64, l: &Limits) -> (u32, u32, u32) {
    let mut scale = (l.max_long_edge / width.max(height)).min(1.0);
    let tokens = width * scale * (height * scale) / 750.0;
    if tokens > l.max_tokens {
        scale *= (l.max_tokens / tokens).sqrt();
    }
    let (w, h) = ((width * scale).floor(), (height * scale).floor());
    (w as u32, h as u32, (w * h / 750.0).ceil() as u32)
}

pub fn shrink_to(width: f64, height: f64, long_edge: f64) -> (f64, f64) {
    let s = (long_edge / width.max(height)).min(1.0);
    ((width * s).round(), (height * s).round())
}

pub fn image_message(b: &[u8], question: &str, provider: &str) -> Result<Value, String> {
    let info = sniff(b).ok_or("not a supported image")?;
    let data = BASE64.encode(b); // Rust's standard library has no base64: the `base64` crate is the usual choice
    Ok(match provider {
        "anthropic" => json!({ "role": "user", "content": [
            { "type": "image", "source": { "type": "base64", "media_type": info.kind, "data": data } },
            { "type": "text", "text": question } ] }),
        "openai" => json!({ "role": "user", "content": [
            { "type": "text", "text": question },
            { "type": "image_url", "image_url": { "url": format!("data:{};base64,{data}", info.kind) } } ] }),
        _ => json!({ "role": "user", "content": question, "images": [data] }), // Ollama's own /api/chat
    })
}

pub const EXTRACT_PROMPT: &str = "Read this invoice and reply with JSON only, in the invoice schema.\n\
    If you can't read a value, don't guess: reply {\"unreadable\": \"<which field>\"}.";

/// Image in, checked data out. The structured-output lab's `parse` checks shape and arithmetic.
pub fn extract_invoice(
    see: impl Fn(&[u8], &str) -> String,
    b: &[u8],
) -> Result<invoice::Invoice, String> {
    sniff(b).ok_or("not a supported image")?;
    let reply = see(b, EXTRACT_PROMPT);
    let (Some(start), Some(end)) = (reply.find('{'), reply.rfind('}')) else {
        return Err("no JSON in the reply".into());
    };
    if let Ok(Value::Object(probe)) = serde_json::from_str(&reply[start..=end]) {
        if let Some(field) = probe.get("unreadable").and_then(Value::as_str) {
            return Err(format!("unreadable: {field}"));
        }
    }
    invoice::parse(&reply)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
    fn png_header(w: u32, h: u32) -> Vec<u8> {
        [
            PNG_SIGNATURE,
            &13u32.to_be_bytes(),
            b"IHDR",
            &w.to_be_bytes(),
            &h.to_be_bytes(),
            &[8, 0, 0, 0, 0],
        ]
        .concat()
    }

    fn jpeg_header(w: u16, h: u16) -> Vec<u8> {
        let app0 = [
            0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, b'J', b'F', b'I', b'F', 0, 1, 1, 0, 0, 1, 0, 1, 0,
            0,
        ];
        [
            &app0[..],
            &[0xff, 0xc0, 0x00, 0x11, 0x08],
            &h.to_be_bytes(),
            &w.to_be_bytes(),
            &[3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1],
        ]
        .concat()
    }

    #[test]
    fn the_type_comes_from_the_bytes() {
        assert_eq!(
            sniff(&png_header(1200, 800)),
            Some(Info {
                kind: "image/png",
                width: 1200,
                height: 800
            })
        );
        assert_eq!(
            sniff(&jpeg_header(4000, 3000)),
            Some(Info {
                kind: "image/jpeg",
                width: 4000,
                height: 3000
            })
        );
        assert_eq!(
            sniff(b"GIF89a\x40\x01\xf0\x00"),
            Some(Info {
                kind: "image/gif",
                width: 320,
                height: 240
            })
        );
        assert_eq!(sniff(b"#!/bin/sh\nrm -rf /\n"), None);
        assert_eq!(sniff(b"<svg onload=alert(1)>"), None);
    }

    #[test]
    fn what_a_photo_costs() {
        assert_eq!(fit(4000.0, 3000.0, &HIGH_RES), (2187, 1640, 4783));
        assert_eq!(fit(4000.0, 3000.0, &STANDARD), (1264, 948, 1598));
        let (w, h) = shrink_to(4000.0, 3000.0, 1024.0);
        assert_eq!(fit(w, h, &HIGH_RES), (1024, 768, 1049));
        assert_eq!(fit(1920.0, 1080.0, &HIGH_RES), (1920, 1080, 2765));
    }

    #[test]
    fn three_formats() {
        let png = png_header(4, 4);
        let data = BASE64.encode(&png);
        assert_eq!(
            image_message(&png, "What is this?", "anthropic").unwrap()["content"][0],
            json!({ "type": "image", "source": { "type": "base64", "media_type": "image/png", "data": data } })
        );
        assert_eq!(
            image_message(&png, "What is this?", "openai").unwrap()["content"][1]["image_url"]["url"],
            format!("data:image/png;base64,{data}")
        );
        assert_eq!(
            image_message(&png, "What is this?", "ollama").unwrap(),
            json!({ "role": "user", "content": "What is this?", "images": [data] })
        );
        assert_eq!(
            image_message(b"not an image", "?", "openai"),
            Err("not a supported image".into())
        );
    }

    #[test]
    fn checked_extraction() {
        let good = r#"{"vendor":"Paper Co","invoice_number":"INV-7","currency":"GBP","due_date":"2026-10-15","line_items":[{"description":"A4 paper","amount_cents":1250},{"description":"Pens","amount_cents":480}],"total_cents":1730}"#;
        let png = png_header(8, 8);
        let reply = |text: &str| {
            let text = format!("Here you go: {text}");
            move |_: &[u8], _: &str| text.clone()
        };
        assert_eq!(
            extract_invoice(reply(good), &png).unwrap().total_cents,
            1730
        );
        let misread = good.replace(r#""total_cents":1730"#, r#""total_cents":1780"#);
        assert_eq!(
            extract_invoice(reply(&misread), &png).unwrap_err(),
            "line items add up to 1730 cents but total_cents is 1780"
        );
        assert_eq!(
            extract_invoice(reply(r#"{"unreadable": "due_date"}"#), &png).unwrap_err(),
            "unreadable: due_date"
        );
        assert_eq!(
            extract_invoice(|_, _| "I can't see an invoice.".into(), &png).unwrap_err(),
            "no JSON in the reply"
        );
        assert_eq!(
            extract_invoice(reply(good), b"%PDF-1.7").unwrap_err(),
            "not a supported image"
        );
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/09-multimodal/labs/rust). `python3 labs/run.py multimodal/rust`.

## 8. C#

`BinaryPrimitives` reads either byte order from a `Span<byte>`, and `"GIF8"u8` is a UTF-8 byte literal, so header checks need no allocation. `ShrinkTo` passes `MidpointRounding.AwayFromZero`, because `Math.Round`'s default rounds halves to even. The messages are `JsonObject` trees. Extraction calls the structured-output lab's `Invoices.Parse`, whose file the project links.

```csharp
// What an uploaded file really is, what an image costs, the three providers' formats, and checked extraction.
// The same results as the TypeScript lab; links the structured-output lab's Invoices.Parse.
using System.Buffers.Binary;
using System.Text.Json;
using System.Text.Json.Nodes;

public sealed record ImageInfo(string Type, int Width, int Height);
public sealed record Limits(double MaxLongEdge, double MaxTokens);
public sealed record Fitted(int Width, int Height, int Tokens);

public static class Multimodal
{
    static ReadOnlySpan<byte> PngSignature => [0x89, (byte)'P', (byte)'N', (byte)'G', 0x0d, 0x0a, 0x1a, 0x0a];

    /// <summary>The type from the file's first bytes, never its name or Content-Type. Null if it isn't a supported image.</summary>
    public static ImageInfo? Sniff(byte[] b)
    {
        var s = b.AsSpan();
        if (s.StartsWith(PngSignature) && s.Length >= 24)
            return new("image/png", (int)BinaryPrimitives.ReadUInt32BigEndian(s[16..]), (int)BinaryPrimitives.ReadUInt32BigEndian(s[20..]));
        if (s.StartsWith((ReadOnlySpan<byte>)[0xff, 0xd8, 0xff])) return Jpeg(s);
        if (s.StartsWith("GIF8"u8) && s.Length >= 10)
            return new("image/gif", BinaryPrimitives.ReadUInt16LittleEndian(s[6..]), BinaryPrimitives.ReadUInt16LittleEndian(s[8..]));
        if (s.StartsWith("RIFF"u8) && s.Length >= 12 && s[8..12].SequenceEqual("WEBP"u8)) return new("image/webp", 0, 0);
        return null;
    }

    static ImageInfo Jpeg(ReadOnlySpan<byte> s)
    {
        for (var i = 2; i + 9 < s.Length && s[i] == 0xff;)
        {
            var marker = s[i + 1];
            if (marker is >= 0xc0 and <= 0xcf and not (0xc4 or 0xc8 or 0xcc))
                return new("image/jpeg", BinaryPrimitives.ReadUInt16BigEndian(s[(i + 7)..]), BinaryPrimitives.ReadUInt16BigEndian(s[(i + 5)..]));
            i += 2 + BinaryPrimitives.ReadUInt16BigEndian(s[(i + 2)..]);
        }
        return new("image/jpeg", 0, 0);
    }

    public static readonly Limits HighRes = new(2576, 4784); // Anthropic, 2026-10: Opus 4.7+ and Sonnet 5+
    public static readonly Limits Standard = new(1568, 1600); // earlier models

    /// <summary>Scaled to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation).</summary>
    public static Fitted Fit(double width, double height, Limits l)
    {
        var scale = Math.Min(1, l.MaxLongEdge / Math.Max(width, height));
        var tokens = width * scale * (height * scale) / 750;
        if (tokens > l.MaxTokens) scale *= Math.Sqrt(l.MaxTokens / tokens);
        double w = Math.Floor(width * scale), h = Math.Floor(height * scale);
        return new((int)w, (int)h, (int)Math.Ceiling(w * h / 750));
    }

    /// <summary>MidpointRounding.AwayFromZero, because .NET's Math.Round rounds 0.5 to even by default.</summary>
    public static (double, double) ShrinkTo(double width, double height, double longEdge)
    {
        var s = Math.Min(1, longEdge / Math.Max(width, height));
        return (Math.Round(width * s, MidpointRounding.AwayFromZero), Math.Round(height * s, MidpointRounding.AwayFromZero));
    }

    public static JsonObject ImageMessage(byte[] b, string question, string provider)
    {
        var info = Sniff(b) ?? throw new ArgumentException("not a supported image");
        var data = Convert.ToBase64String(b);
        return provider switch
        {
            "anthropic" => new JsonObject
            {
                ["role"] = "user",
                ["content"] = new JsonArray(
                    new JsonObject { ["type"] = "image", ["source"] = new JsonObject { ["type"] = "base64", ["media_type"] = info.Type, ["data"] = data } },
                    new JsonObject { ["type"] = "text", ["text"] = question }),
            },
            "openai" => new JsonObject
            {
                ["role"] = "user",
                ["content"] = new JsonArray(
                    new JsonObject { ["type"] = "text", ["text"] = question },
                    new JsonObject { ["type"] = "image_url", ["image_url"] = new JsonObject { ["url"] = $"data:{info.Type};base64,{data}" } }),
            },
            _ => new JsonObject { ["role"] = "user", ["content"] = question, ["images"] = new JsonArray(data) }, // Ollama's own /api/chat
        };
    }

    public const string ExtractPrompt = """
        Read this invoice and reply with JSON only, in the invoice schema.
        If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.
        """;

    /// <summary>Image in, checked data out. The structured-output lab's Parse checks shape and arithmetic.</summary>
    public static async Task<(Invoice? Invoice, string? Reason)> ExtractInvoice(Func<byte[], string, Task<string>> see, byte[] b)
    {
        if (Sniff(b) is null) return (null, "not a supported image");
        var reply = await see(b, ExtractPrompt);
        int start = reply.IndexOf('{'), end = reply.LastIndexOf('}');
        if (start == -1 || end < start) return (null, "no JSON in the reply");
        try
        {
            if (JsonNode.Parse(reply[start..(end + 1)]) is JsonObject probe && probe["unreadable"]?.GetValue<string>() is { } field)
                return (null, $"unreadable: {field}");
            return (Invoices.Parse(reply), null);
        }
        catch (Exception e) when (e is FormatException or JsonException)
        {
            return (null, e.Message);
        }
    }
}
```

```csharp
// Checks: the same results as every other language.
using System.Buffers.Binary;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
static byte[] PngHeader(uint w, uint h)
{
    var b = new byte[29];
    new byte[] { 0x89, (byte)'P', (byte)'N', (byte)'G', 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13, (byte)'I', (byte)'H', (byte)'D', (byte)'R' }.CopyTo(b, 0);
    BinaryPrimitives.WriteUInt32BigEndian(b.AsSpan(16), w);
    BinaryPrimitives.WriteUInt32BigEndian(b.AsSpan(20), h);
    return b;
}

static byte[] JpegHeader(ushort w, ushort h)
{
    byte[] head = [0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, (byte)'J', (byte)'F', (byte)'I', (byte)'F', 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0xff, 0xc0, 0x00, 0x11, 0x08];
    var size = new byte[4];
    BinaryPrimitives.WriteUInt16BigEndian(size, h);
    BinaryPrimitives.WriteUInt16BigEndian(size.AsSpan(2), w);
    return [.. head, .. size, 3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1];
}

Check(Multimodal.Sniff(PngHeader(1200, 800)) == new ImageInfo("image/png", 1200, 800), "png");
Check(Multimodal.Sniff(JpegHeader(4000, 3000)) == new ImageInfo("image/jpeg", 4000, 3000), "jpeg");
Check(Multimodal.Sniff([(byte)'G', (byte)'I', (byte)'F', (byte)'8', (byte)'9', (byte)'a', 0x40, 0x01, 0xf0, 0x00]) == new ImageInfo("image/gif", 320, 240), "gif");
Check(Multimodal.Sniff("#!/bin/sh\nrm -rf /\n"u8.ToArray()) is null && Multimodal.Sniff("<svg onload=alert(1)>"u8.ToArray()) is null, "refused");

Check(Multimodal.Fit(4000, 3000, Multimodal.HighRes) == new Fitted(2187, 1640, 4783), Multimodal.Fit(4000, 3000, Multimodal.HighRes));
Check(Multimodal.Fit(4000, 3000, Multimodal.Standard) == new Fitted(1264, 948, 1598), "standard");
var (sw, sh) = Multimodal.ShrinkTo(4000, 3000, 1024);
Check(Multimodal.Fit(sw, sh, Multimodal.HighRes) == new Fitted(1024, 768, 1049), "shrunk");
Check(Multimodal.Fit(1920, 1080, Multimodal.HighRes) == new Fitted(1920, 1080, 2765), "screenshot");

var png = PngHeader(4, 4);
var data = Convert.ToBase64String(png);
Check(Multimodal.ImageMessage(png, "What is this?", "anthropic")["content"]![0]!.ToJsonString() ==
    $$$"""{"type":"image","source":{"type":"base64","media_type":"image/png","data":"{{{data}}}"}}""", "anthropic");
Check(Multimodal.ImageMessage(png, "What is this?", "openai")["content"]![1]!["image_url"]!["url"]!.GetValue<string>() == $"data:image/png;base64,{data}", "openai");
Check(Multimodal.ImageMessage(png, "What is this?", "ollama").ToJsonString() == $$"""{"role":"user","content":"What is this?","images":["{{data}}"]}""", "ollama");

const string Good = """{"vendor":"Paper Co","invoice_number":"INV-7","currency":"GBP","due_date":"2026-10-15","line_items":[{"description":"A4 paper","amount_cents":1250},{"description":"Pens","amount_cents":480}],"total_cents":1730}""";
static Func<byte[], string, Task<string>> Reply(string text) => (_, _) => Task.FromResult($"Here you go: {text}");
Check((await Multimodal.ExtractInvoice(Reply(Good), png)).Invoice?.TotalCents == 1730, "good");
Check((await Multimodal.ExtractInvoice(Reply(Good.Replace("\"total_cents\":1730", "\"total_cents\":1780")), png)).Reason
    == "line items add up to 1730 cents but total_cents is 1780", "misread");
Check((await Multimodal.ExtractInvoice(Reply("""{"unreadable": "due_date"}"""), png)).Reason == "unreadable: due_date", "unreadable");
Check((await Multimodal.ExtractInvoice((_, _) => Task.FromResult("I can't see an invoice."), png)).Reason == "no JSON in the reply", "no JSON");
Check((await Multimodal.ExtractInvoice(Reply(Good), "%PDF-1.7"u8.ToArray())).Reason == "not a supported image", "pdf");

Console.WriteLine("all multimodal checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/09-multimodal/labs/csharp). `container.sh` copies the linked file into the .NET SDK container. `python3 labs/run.py multimodal/csharp` (needs Podman).

## Common pitfalls

1. **Reading with the wrong byte order.** A PNG's 1200 read as little-endian is 2,953,052,160. Name the order every time.
2. **Signed types for unsigned data.** In Java, a 16-bit size over 32,767 reads as negative without `& 0xffff`.
3. **Building bytes from a string.** Encoding choices change the bytes. Use byte literals or arrays.
4. **Assuming every language rounds the same.** Python and C# round halves to even by default.
5. **Trusting magic bytes as proof of a valid image.** They identify the claimed format; decode with a real library before processing further.

## Check your understanding

1. Why does the PNG code read big-endian and the GIF code little-endian?
2. Why does the Java lab use `& 0xffff` on a value read with `getShort`?
3. What does Python's `round(2.5)` return, and why might that matter when shrinking an image?
4. Why does the Go lab's Anthropic message JSON have its keys in a different order from the others?
5. Go's `http.DetectContentType` identifies a PNG. Why does the lab still read the header itself?

<details>
<summary>Answers — after your attempt</summary>

1. Because the formats define them that way: the PNG specification stores integers big-endian, the GIF specification little-endian. Reading either the other way gives a nonsense number.
2. Java's `short` is signed, so a 16-bit value over 32,767 reads as negative. Masking with `0xffff` turns it into the unsigned value as an `int`.
3. `2`: Python rounds halves to the nearest even number. A resize that lands exactly on a half would round differently from JavaScript or Java, giving a one-pixel difference between languages.
4. `json.Marshal` writes the keys of a `map` in sorted order, where the other languages keep the order the code added them.
5. `DetectContentType` returns only the type. The cost estimate needs the width and height, which come from the header.

</details>

## Practice — independent task

**Add WebP sizes.**

1. Read the WebP format's header layout (the `VP8X` chunk stores the canvas width and height as 24-bit little-endian values, minus one).
2. Extend your language's `sniff` to return the size for `VP8X` WebP files.
3. Make a WebP with an image tool, check your size against the tool's, and add a test with a header-only fixture like the labs'.

**Done when:** your `sniff` returns the right width and height for a real WebP file, and a test pins it down.

## Before moving on

You can read binary headers in your language with the right byte order and sign, choose between hand-reading a header and an image library, and say how your language rounds halves.

**Recap.** Identifying a file and reading its size is a few lines in any language: check the magic bytes, then read the size with the format's byte order. Name the order every time, watch Java's signed types, and write signatures as bytes, not strings. Resize with a real image library. Python and C# round halves to even by default; JavaScript, Java, Go and Rust don't. Reuse your structured-output checks for whatever a model reads from an image.

## Related
- [[ai-ml/03-ai-engineer/09-multimodal/index|Multimodal]] — the main lesson
- [[ai-ml/03-ai-engineer/11-structured-output/in-other-languages|Structured output in other languages]] — the parsers the extraction reuses
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/in-other-languages|Cost, caching and latency in other languages]] — other ways languages produce different bytes
