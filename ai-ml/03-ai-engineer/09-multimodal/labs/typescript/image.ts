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
