// encoding.mjs — output encoding depends on where the value lands.

// HTML body and quoted attributes: the five characters that can end text and start markup.
export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export const greetingUnsafe = (name) => `<p>Welcome, ${name}</p>`;
export const greetingSafe = (name) => `<p>Welcome, ${escapeHtml(name)}</p>`;

// A denylist: tries to remove "bad" input. Shown to fail.
export const stripScriptTags = (value) => value.replace(/<script>.*?<\/script>/g, "");

// A URL in an href: escaping is not enough — "javascript:" contains no special characters.
// So the scheme is checked against an allowlist.
export function safeHref(url) {
  let parsed;
  try { parsed = new URL(url); } catch { return "#"; }
  return ["https:", "http:", "mailto:"].includes(parsed.protocol) ? escapeHtml(parsed.href) : "#";
}
export const profileLink = (url) => `<a href="${safeHref(url)}">website</a>`;

// Data inside a <script> block: JSON.stringify makes valid JavaScript, but "</script>" in a
// string still ends the block in the HTML parser. Escaping "<" as \u003c prevents that.
export const inlineDataUnsafe = (data) => `<script>window.DATA = ${JSON.stringify(data)}</script>`;
export const inlineDataSafe = (data) => `<script>window.DATA = ${JSON.stringify(data).replaceAll("<", "\\u003c")}</script>`;
