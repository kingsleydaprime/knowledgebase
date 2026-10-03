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
