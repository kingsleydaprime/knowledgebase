# Multimodal

> **[Intermediate]** · Covers working with more than text: images as input to a model that can see, images, audio and video as output, and speech in and out. For an AI engineer most of this is the same call with more kinds of content, so the lesson spends its time on the engineering around it: checking what an uploaded file really is, what an image costs in tokens and how to cut that, sending it in each provider's format, and checking data read from an image as strictly as data read from text. The worked example reads an invoice from a photo.

## Before you start

You can already:

- Call a model through a port, with messages → [[ai-ml/03-ai-engineer/04-calling-models/index|calling models]].
- Validate a model's structured output against a schema and invariants → [[ai-ml/03-ai-engineer/11-structured-output/index|structured output]].
- Work out a call's cost from its tokens → [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|cost, caching and latency]].

After this lesson you will be able to:

1. Decide an uploaded file's type from its bytes, and explain why the file name and Content-Type can't be trusted.
2. Estimate what an image costs in tokens, and cut it by sending only the detail you need.
3. Send an image to a model in the Anthropic, OpenAI and Ollama formats.
4. Extract data from an image with the same checks as text, and name the generation, speech and video models an engineer reaches for.

**Study route.** Read §1–4, stop at the prediction in §3, then §5–6 and the lab.

## The kid version

Until recently, you could only talk to these models by writing notes. Now you can also hand them a photo, a drawing or a recording, and some can draw a picture or speak back. Showing a model a photo is like showing a friend a picture of a broken bike and asking "what's wrong?": quicker than describing it. But big photos take longer to look at and cost more, so you crop them to the part that matters. And a friend can misread a blurry number, so you check the arithmetic.

**Where the analogy stops working.** A friend looks at a photo the same way whatever its size. A model's cost grows with the number of pixels it's sent, so sending a huge photo of a small receipt pays for detail nobody needed.

## 1. Why this exists

A customer emails a photo of a receipt to claim a refund, or uploads a screenshot of an error. Typing the details out is slow and error-prone; asking the model to read the image is a single call. But the upload might not be an image at all, a 12-megapixel phone photo costs several times what the job needs, each provider wants the image in a different shape, and a model reading a blurry photo can misread a digit. The model call is the easy part; the rest is this lesson.

## Terms used in this lesson

1. **Multimodal**: This describes a model that works with more than one kind of data, such as text and images, or audio.
2. **Vision model**: This is a model that accepts images as input and reasons about them, such as describing a photo or reading text in a screenshot. Most current frontier language models are vision models.
3. **Magic bytes**: These are the first few bytes of a file, which identify its format. A PNG always starts with the same eight bytes; a JPEG starts with `FF D8 FF`.
4. **Base64**: This is a way of writing binary data, such as an image, as plain text, so it can travel inside JSON. It makes the data about a third larger.
5. **Image tokens**: These are the tokens an image is counted as for pricing and context limits. The number depends on the image's size after the provider scales it.
6. **OCR (optical character recognition)**: The letters stand for those words. It means reading text from an image. Vision models do it as part of understanding the image.
7. **Diffusion model**: This is a model that generates an image (or video or audio) by starting from random noise and removing it step by step towards something that matches the prompt.
8. **ASR and TTS**: ASR (automatic speech recognition) turns speech into text; TTS (text to speech) turns text into speech.

## 2. Check what the file really is

An upload arrives with a file name (`receipt.png`) and a Content-Type header (`image/png`). **Both are chosen by the sender**, so both can lie. Decide the type from the file's own first bytes, the magic bytes, and refuse anything that isn't an image type you accept. The lab's `sniff` recognises PNG, JPEG, GIF and WebP and reads the width and height from the file's header, so you know the size before deciding what to send. A shell script renamed `photo.png` is refused, and so is SVG, which is text that can carry scripts.

This matters beyond the model: the same file may be stored, shown to staff in a browser, or passed to other tools. Treat it as untrusted input, like any other ([[ai-ml/03-ai-engineer/10-safety-and-production/index|safety and production]]: an image can also carry an injected instruction as visible text).

## 3. What an image costs

An image is counted as tokens, and the count grows with its pixels. Anthropic documents the approximation:

$$\text{tokens} \approx \frac{\text{width} \times \text{height}}{750}$$

after the provider has scaled the image to fit the model's limits. Those limits differ by model. Anthropic's high-resolution models (Opus 4.7 and later, Sonnet 5 and later) accept up to 2,576 pixels on the long edge and about 4,784 tokens per image; earlier models, 1,568 pixels and about 1,600 tokens. Other providers use other formulas (OpenAI's counts 512-pixel tiles), so check the documentation, or the provider's token-counting endpoint, for exact numbers.

**Predict before reading on.** A phone photo of a receipt is 4,000 × 3,000 pixels. Roughly how many tokens is it on a high-resolution model, and how many if you shrink it to 1,024 pixels wide first?

The lab's answer: the provider scales it to 2,187 × 1,640, about **4,783 tokens**: the per-image maximum. Shrunk to 1,024 × 768 before sending, it's **1,049 tokens**, under a quarter. At $2 per million input tokens, a thousand receipts cost $9.57 one way and $2.10 the other. If 1,024 pixels is enough to read the text, the rest is detail you pay for and don't use. Keep full resolution for what needs it: dense charts, small print, screenshots where positions matter.

## 4. Sending it

An image goes into the user message as one more content part, beside the text. Each API spells it differently:

- **Anthropic** (Messages API): a content block `{ type: "image", source: { type: "base64", media_type, data } }`.
- **OpenAI** (Chat Completions): `{ type: "image_url", image_url: { url: "data:image/png;base64,..." } }`.
- **Ollama** (its own `/api/chat`): an `images` list of base64 strings beside the message's text.

Most APIs also accept a URL or a previously uploaded file instead of base64, which saves sending the same image again. As with text, keep these differences behind a port ([[ai-ml/03-ai-engineer/04-calling-models/index|calling models]]), so the rest of your code says "image plus question" once.

## 5. Read an image like you'd read a stranger's handwriting

Reading text from a photo is less reliable than reading text you were given. Glare, blur and odd layouts produce misreadings that look perfectly plausible. So the extraction pipeline in the lab is the structured-output pipeline, unchanged, with one addition:

1. Check the file is an image.
2. Ask for JSON in the invoice schema, and allow an explicit answer for "I can't read this field" (`{"unreadable": "due_date"}`). A model told it may not guess is less likely to.
3. Validate the shape against the schema.
4. **Check the invariants.** The line items must add up to the total. A misread digit, such as 1780 for 1730, usually breaks that sum, which is the cheapest error detector there is.
5. Anything that fails goes to a person, with the image.

## 6. Generation, speech and video

**Images out.** Diffusion models generate images from a prompt. Hosted options include OpenAI's image models, Google's Imagen and Midjourney; open-weight options such as Stable Diffusion and Flux run locally and can be customised with fine-tuned add-ons (LoRAs) and layout controls. Judging them is different from judging text: does the image follow the prompt, does it look right, does it stay consistent across edits?

**Speech.** Speech recognition (ASR) turns audio into text; Whisper is the well-known open-weight model. Text to speech (TTS) turns text into natural voices, including cloned ones. Together, speech recognition, a language model and speech synthesis make a voice agent; latency becomes the main constraint ([[ai-ml/03-ai-engineer/17-voice-and-realtime|voice and realtime]]).

**Video.** Generating video from text or images, and reasoning over a video's frames, are the newest and fastest-moving capabilities. Check current capabilities and limits before relying on either.

**The extra risks.** Generated images, voices and video raise questions text doesn't: likenesses of real people, cloned voices used for fraud, and provenance — showing that media was generated. Providers increasingly attach provenance metadata, such as C2PA content credentials; keep it intact if your product passes generated media on.

## Worked example — an invoice from a photo

The file checks and the cost estimate:

```ts
// image.ts — what an uploaded file really is, how big it is, and what it will cost to send.

export type ImageInfo = { type: "image/png" | "image/jpeg" | "image/gif" | "image/webp"; width?: number; height?: number };

/** Decide the type from the file's first bytes, never from its name or the upload's Content-Type, which
 *  the sender controls. Anything that isn't a known image is refused. */
export function sniff(bytes: Uint8Array): ImageInfo | null {
  const b = Buffer.from(bytes);
  if (b.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) {
    return { type: "image/png", width: b.readUInt32BE(16), height: b.readUInt32BE(20) }; // from the IHDR chunk
  }
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return { type: "image/jpeg", ...jpegSize(b) };
  if (b.subarray(0, 4).toString("latin1") === "GIF8") return { type: "image/gif", width: b.readUInt16LE(6), height: b.readUInt16LE(8) };
  if (b.subarray(0, 4).toString("latin1") === "RIFF" && b.subarray(8, 12).toString("latin1") === "WEBP") return { type: "image/webp" };
  return null;
}

/** A JPEG's size is in its "start of frame" segment; walk the segments until we find it. */
function jpegSize(b: Buffer): { width?: number; height?: number } {
  for (let i = 2; i + 9 < b.length; ) {
    if (b[i] !== 0xff) return {};
    const marker = b[i + 1];
    const length = b.readUInt16BE(i + 2);
    const isFrame = marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker);
    if (isFrame) return { height: b.readUInt16BE(i + 5), width: b.readUInt16BE(i + 7) };
    i += 2 + length;
  }
  return {};
}

/** A model's image limits, from its documentation: the longest side it accepts, and the most tokens one
 *  image can use. Larger images are scaled down by the provider, and you pay for what's left. */
export type VisionLimits = { maxLongEdge: number; maxTokens: number };

// Anthropic's documentation, 2026-10: high-resolution models (Opus 4.7 and later, Sonnet 5 and later) take
// up to 2576 px on the long edge and about 4784 tokens; earlier models 1568 px and about 1600 tokens.
export const HIGH_RES: VisionLimits = { maxLongEdge: 2576, maxTokens: 4784 };
export const STANDARD: VisionLimits = { maxLongEdge: 1568, maxTokens: 1600 };

/** The size an image will be after scaling, and its approximate cost. Anthropic documents the
 *  approximation tokens ≈ width × height / 750; use the provider's token-counting endpoint for exact numbers.
 *  Other providers use other formulas (OpenAI's, for example, counts 512-pixel tiles). */
export function fit(width: number, height: number, limits: VisionLimits) {
  let scale = Math.min(1, limits.maxLongEdge / Math.max(width, height));
  const tokensAt = (s: number) => (width * s * (height * s)) / 750;
  if (tokensAt(scale) > limits.maxTokens) scale *= Math.sqrt(limits.maxTokens / tokensAt(scale));
  const w = Math.floor(width * scale), h = Math.floor(height * scale);
  return { width: w, height: h, tokens: Math.ceil((w * h) / 750) };
}

/** The scale to send at, if you choose: anything bigger than the detail you need is tokens for nothing. */
export const shrinkTo = (width: number, height: number, longEdge: number) => {
  const s = Math.min(1, longEdge / Math.max(width, height));
  return { width: Math.round(width * s), height: Math.round(height * s) };
};
```

The three message formats, and the extraction pipeline, which reuses the structured-output lab's schema and invariant checks:

```ts
// messages.ts — the same image and question in three providers' formats, and an extraction pipeline.
import { checkInvariants, type Invoice, validateInvoice } from "../../../11-structured-output/labs/typescript/invoice.ts";
import { parseModelJson } from "../../../11-structured-output/labs/typescript/extract.ts";
import { sniff } from "./image.ts";

/** An image goes in the user message as one more content part, next to the text. Each API spells it differently. */
export function imageMessage(bytes: Uint8Array, question: string, format: "anthropic" | "openai" | "ollama") {
  const info = sniff(bytes);
  if (!info) throw new Error("not a supported image");
  const data = Buffer.from(bytes).toString("base64");
  switch (format) {
    case "anthropic": // Messages API: a content block with a base64 source
      return { role: "user", content: [{ type: "image", source: { type: "base64", media_type: info.type, data } }, { type: "text", text: question }] };
    case "openai": // Chat Completions: the image as a data URL
      return { role: "user", content: [{ type: "text", text: question }, { type: "image_url", image_url: { url: `data:${info.type};base64,${data}` } }] };
    case "ollama": // Ollama's own /api/chat: a list of base64 images beside the text
      return { role: "user", content: question, images: [data] };
  }
}

export type See = (bytes: Uint8Array, prompt: string) => Promise<string>;

export const EXTRACT_PROMPT = `Read this invoice and reply with JSON only:
{"vendor": string, "invoice_number": string, "currency": "GBP"|"USD"|"EUR"|"NGN", "due_date": "YYYY-MM-DD",
 "line_items": [{"description": string, "amount_cents": integer}], "total_cents": integer}
If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.`;

/** Image in, checked data out. Reading an image is less reliable than reading text, so the same checks
 *  as the structured-output lesson apply, and "unreadable" is an answer, not an error. */
export async function extractInvoice(see: See, bytes: Uint8Array):
  Promise<{ ok: true; invoice: Invoice } | { ok: false; reason: string }> {
  if (!sniff(bytes)) return { ok: false, reason: "not a supported image" };
  let parsed: unknown;
  try {
    parsed = parseModelJson(await see(bytes, EXTRACT_PROMPT));
  } catch {
    return { ok: false, reason: "no JSON in the reply" };
  }
  if (parsed && typeof parsed === "object" && "unreadable" in parsed) return { ok: false, reason: `unreadable: ${(parsed as { unreadable: string }).unreadable}` };
  const shape = validateInvoice(parsed);
  if (!shape.ok) return { ok: false, reason: shape.errors.join("; ") };
  const sums = checkInvariants(shape.value); // a misread digit usually breaks the arithmetic
  return sums.ok ? { ok: true, invoice: sums.value } : { ok: false, reason: sums.errors.join("; ") };
}
```

The tests build real images in memory (a valid PNG, checked with an independent image library while this lesson was written, and the header of a JPEG), so they need no image files:

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { crc32, deflateSync } from "node:zlib";
import { fit, HIGH_RES, shrinkTo, sniff, STANDARD } from "./image.ts";
import { extractInvoice, imageMessage } from "./messages.ts";

/** A real, valid PNG of any size, built in memory: signature, IHDR, one IDAT of grey pixels, IEND. */
function png(width: number, height: number): Buffer {
  const chunk = (type: string, data: Buffer) => {
    const body = Buffer.concat([Buffer.from(type, "latin1"), data]);
    const out = Buffer.alloc(8 + data.length + 4);
    out.writeUInt32BE(data.length, 0);
    body.copy(out, 4);
    out.writeUInt32BE(crc32(body), 8 + data.length);
    return out;
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr.set([8, 0, 0, 0, 0], 8); // 8-bit greyscale
  const rows = Buffer.alloc((width + 1) * height, 0x80); // each row: a filter byte, then grey pixels
  for (let y = 0; y < height; y++) rows[y * (width + 1)] = 0;
  return Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]), chunk("IHDR", ihdr), chunk("IDAT", deflateSync(rows)), chunk("IEND", Buffer.alloc(0))]);
}

/** The start of a JPEG: just enough header (APP0, then a start-of-frame segment) to read its size. */
function jpegHeader(width: number, height: number): Buffer {
  const app0 = Buffer.from([0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00]);
  const sof = Buffer.from([0xff, 0xc0, 0x00, 0x11, 0x08, height >> 8, height & 255, width >> 8, width & 255, 0x03, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1]);
  return Buffer.concat([Buffer.from([0xff, 0xd8]), app0, sof]);
}

test("the type comes from the bytes, not the name", () => {
  assert.deepEqual(sniff(png(1200, 800)), { type: "image/png", width: 1200, height: 800 });
  assert.deepEqual(sniff(jpegHeader(4000, 3000)), { type: "image/jpeg", width: 4000, height: 3000 });
  assert.deepEqual(sniff(Buffer.from("GIF89a\x40\x01\xf0\x00", "latin1")), { type: "image/gif", width: 320, height: 240 });
  // A script renamed photo.png is still a script:
  assert.equal(sniff(Buffer.from("#!/bin/sh\nrm -rf /\n")), null);
  assert.equal(sniff(Buffer.from("<svg onload=alert(1)>")), null); // SVG is text that can carry code: not accepted here
});

test("what a 12-megapixel photo costs, and what shrinking it saves", () => {
  // A high-resolution model scales it to fit 2576 px and about 4784 tokens; an earlier model, 1568 px and about 1600.
  assert.deepEqual(fit(4000, 3000, HIGH_RES), { width: 2187, height: 1640, tokens: 4783 });
  assert.deepEqual(fit(4000, 3000, STANDARD), { width: 1264, height: 948, tokens: 1598 });
  // If 1024 px is enough detail to read a receipt, send that instead: under a quarter of the tokens.
  const small = shrinkTo(4000, 3000, 1024);
  assert.deepEqual(fit(small.width, small.height, HIGH_RES), { width: 1024, height: 768, tokens: 1049 });
  const dollars = (tokens: number) => Math.round(((1000 * tokens * 2) / 1_000_000) * 100) / 100; // 1,000 images at $2 per million input tokens
  assert.deepEqual([dollars(4783), dollars(1049)], [9.57, 2.1]);
  assert.deepEqual(fit(1920, 1080, HIGH_RES), { width: 1920, height: 1080, tokens: 2765 }); // a screenshot fits as it is
});

test("the same image and question, in three providers' formats", () => {
  const image = png(4, 4);
  const data = image.toString("base64");
  assert.deepEqual(imageMessage(image, "What is this?", "anthropic"), {
    role: "user",
    content: [{ type: "image", source: { type: "base64", media_type: "image/png", data } }, { type: "text", text: "What is this?" }],
  });
  assert.deepEqual(imageMessage(image, "What is this?", "openai").content[1], { type: "image_url", image_url: { url: `data:image/png;base64,${data}` } });
  assert.deepEqual(imageMessage(image, "What is this?", "ollama"), { role: "user", content: "What is this?", images: [data] });
  assert.throws(() => imageMessage(Buffer.from("not an image"), "?", "openai"), /not a supported image/);
});

test("image in, checked data out: a misread digit breaks the arithmetic", async () => {
  const receipt = png(8, 8);
  const reply = (json: object) => async () => `Here you go: ${JSON.stringify(json)}`;
  const good = { vendor: "Paper Co", invoice_number: "INV-7", currency: "GBP", due_date: "2026-10-15",
    line_items: [{ description: "A4 paper", amount_cents: 1250 }, { description: "Pens", amount_cents: 480 }], total_cents: 1730 };
  assert.deepEqual(await extractInvoice(reply(good), receipt), { ok: true, invoice: good });
  // The model read 1780 for 1730, the kind of slip a blurry photo causes; the line items don't add up to it.
  assert.deepEqual(await extractInvoice(reply({ ...good, total_cents: 1780 }), receipt), {
    ok: false,
    reason: "line items add up to 1730 cents but total_cents is 1780",
  });
  assert.deepEqual(await extractInvoice(reply({ unreadable: "due_date" }), receipt), { ok: false, reason: "unreadable: due_date" });
  assert.deepEqual(await extractInvoice(async () => "I can't see an invoice.", receipt), { ok: false, reason: "no JSON in the reply" });
  assert.deepEqual(await extractInvoice(reply(good), Buffer.from("%PDF-1.7")), { ok: false, reason: "not a supported image" });
});
```

### With a real vision model

```ts
// live.ts — extract an invoice from a photo or scan of your own, with a local vision model.
// Not run by the lab runner. Needs Ollama and a vision-capable model (qwen3.5:4b and gemma4 both are); 1 call.
//   node live.ts path/to/receipt.jpg              # qwen3.5:4b
//   node live.ts path/to/receipt.jpg gemma4:latest
import { readFileSync } from "node:fs";
import { fit, HIGH_RES, sniff } from "./image.ts";
import { extractInvoice } from "./messages.ts";

const [path, model = "qwen3.5:4b"] = process.argv.slice(2);
if (!path) throw new Error("usage: node live.ts <image> [model]");
const bytes = readFileSync(path);
const info = sniff(bytes);
console.log(`${path}: ${info?.type ?? "not an image"} ${info?.width ?? "?"}×${info?.height ?? "?"}`);
if (info?.width && info.height) console.log(`on a high-resolution hosted model this would be about ${fit(info.width, info.height, HIGH_RES).tokens} tokens`);

const started = performance.now();
const result = await extractInvoice(async (image, prompt) => {
  const res = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    body: JSON.stringify({ model, stream: false, think: false, options: { temperature: 0 },
      messages: [{ role: "user", content: prompt, images: [Buffer.from(image).toString("base64")] }] }),
  });
  return (await res.json()).message.content;
}, bytes);
console.log(JSON.stringify(result, null, 2));
console.log(`(${((performance.now() - started) / 1000).toFixed(1)} s)`);
```

**Not measured yet.** Photograph a real receipt or invoice, and predict first: will the local model read every field? Which is most likely to come back wrong — the date, a total, the vendor's name? Will the invariant check catch it? How long does one image take on the laptop, compared with a text classification? Then run `node live.ts your-photo.jpg` on a quiet laptop and record the result here.

**Lab:** the code is in [`ai-ml/03-ai-engineer/09-multimodal/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/09-multimodal/labs/typescript). From the vault root, `python3 labs/run.py multimodal/typescript` runs the tests and checks this page still shows the same code. `live.ts` needs Ollama and an image of your own.

## Common pitfalls

1. **Trusting the file name or Content-Type.** The sender chooses both. Read the magic bytes.
2. **Sending every image at full size.** Pay for the detail the task needs, and shrink the rest.
3. **Assuming one token formula.** Providers and model generations count images differently. Check, or use the token-counting endpoint.
4. **Trusting what the model read.** Validate the schema and check invariants; route failures to a person.
5. **No way to say "unreadable".** Without one, the model guesses.
6. **Forgetting an image can carry an instruction.** Text in an image is untrusted input, like text in a document.
7. **Stripping provenance from generated media.** Keep content credentials intact.

## Check your understanding

1. Why decide a file's type from its bytes rather than its name or Content-Type?
2. Roughly how many tokens is a 1,920 × 1,080 screenshot on a high-resolution model, and why isn't it scaled?
3. When should you keep an image at full resolution, despite the cost?
4. The model reads a receipt's total as 1780, but the items add up to 1730. Which check catches it, and what should happen next?
5. What do ASR and TTS do, and what do they make possible together?

<details>
<summary>Answers — after your attempt</summary>

1. The name and the header are chosen by whoever uploads the file, so they can claim anything. The magic bytes are part of the file itself, so they tell you what it actually is.
2. About 1,920 × 1,080 ÷ 750 ≈ 2,765 tokens. Its long edge is under 2,576 pixels and its tokens are under the per-image maximum, so it's sent as it is.
3. When the detail matters to the task: small print, dense charts or tables, or screenshots where the positions of things are important.
4. The invariant check: the line items must add up to the total. The extraction fails, and the image goes to a person to check, or the model is asked again.
5. ASR turns speech into text; TTS turns text into speech. With a language model between them, they make voice agents: speech in, an answer spoken back.

</details>

## Practice — independent task

**Read a document from an image, and measure the cost of detail.**

1. Photograph three receipts or invoices, one of them deliberately blurry.
2. Run the lab's pipeline on each, at full size and shrunk to 1,024 pixels on the long edge.
3. Record, for each: the fields read correctly, whether the invariant check passed, the estimated tokens, and the time.

**Done when:** you have a table showing whether shrinking changed accuracy, how much it saved, and whether the blurry receipt was caught by a check rather than accepted with a wrong value.

## Before moving on

You can check an upload's real type, estimate and cut an image's token cost, send an image in each provider's format, and extract data from an image with the checks you'd use for text.

**Recap.** Multimodal is mostly the same call with more kinds of content. Decide a file's type from its magic bytes, never its name. An image costs tokens in proportion to its pixels, after the provider scales it to the model's limits; shrink what doesn't need the detail. Each API spells an image part differently, so hide that behind a port. Treat what a model reads from an image as a stranger's handwriting: validate it, check its arithmetic, and let it say "unreadable". Generation, speech and video follow the same pattern, with extra risks around likeness and provenance.

**Next.** Back to week 5's core lessons if you came from there; speech gets its own lesson in [[ai-ml/03-ai-engineer/17-voice-and-realtime|voice and realtime]].

## Related
- [[ai-ml/03-ai-engineer/11-structured-output/index|Structured output]] — the schema and invariant checks the pipeline reuses
- [[ai-ml/03-ai-engineer/04-calling-models/index|Calling models]] — the same call, with more content types
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The model landscape]] — generation and speech models as kinds of model
- [[ai-ml/03-ai-engineer/17-voice-and-realtime|Voice and realtime]] — speech in and out
- [[ai-ml/02-ml-engineer/06-computer-vision/index|Computer vision (ML engineer)]] — training vision models yourself

*Source: the roadmap.sh AI-engineer multimodal branch; image limits from Anthropic's documentation, October 2026.*
