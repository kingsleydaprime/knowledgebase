/**
 * Abbreviations — a Quartz transformer.
 *
 * Authors write the bare acronym in markdown. At build time every occurrence is
 * wrapped in <abbr title="...">, so the full meaning appears on hover without
 * putting 167 KB of markup into the notes.
 *
 * Skips anything inside code, pre, a, abbr, headings and KaTeX output, at any depth
 * (so `[the **API** docs](...)` and `## Why *TLS* matters` stay untouched), and
 * identifiers such as a variable called `dfs` or a filename are never touched.
 */
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { visit, SKIP } from "unist-util-visit";

const here = dirname(fileURLToPath(import.meta.url));
const GLOSSARY = JSON.parse(readFileSync(join(here, "glossary.json"), "utf8"));

const SKIP_TAGS = new Set(["code", "pre", "abbr", "a", "script", "style",
                           "h1", "h2", "h3", "h4", "h5", "h6"]);
const SKIP_CLASSES = ["katex", "katex-display"];

// An element whose whole subtree is left alone. Checking here, while walking down,
// covers every depth: a term inside <a><strong>…</strong></a> is never reached.
function isSkipped(node) {
  if (SKIP_TAGS.has(node.tagName)) return true;
  const cls = node.properties?.className;
  const classes = Array.isArray(cls) ? cls : typeof cls === "string" ? cls.split(/\s+/) : [];
  return classes.some((c) => SKIP_CLASSES.includes(c));
}

// longest first, so "SCCs" is matched before "SCC"
const TERMS = Object.keys(GLOSSARY).sort((a, b) => b.length - a.length);
// A word boundary (\b) only makes sense next to a letter or digit. Symbols such as "§"
// get no boundary on that side, so "§4" still matches; "API" still won't match inside "APIs".
const isWordChar = (c) => /\w/.test(c);
const bounded = (t) =>
  (isWordChar(t[0]) ? "\\b" : "") + escapeRe(t) + (isWordChar(t[t.length - 1]) ? "\\b" : "");
const PATTERN = new RegExp(`(${TERMS.map(bounded).join("|")})`, "g");

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export const Abbreviations = (opts = {}) => {
  const glossary = { ...GLOSSARY, ...(opts.extra || {}) };
  return {
    name: "Abbreviations",
    htmlPlugins() {
      return [
        () => (tree) => {
          visit(tree, (node, index, parent) => {
            if (node.type === "element" && isSkipped(node)) return SKIP;
            if (node.type !== "text" || !parent) return;
            const value = node.value;
            if (!PATTERN.test(value)) return;
            PATTERN.lastIndex = 0;

            const out = [];
            let last = 0;
            let m;
            while ((m = PATTERN.exec(value)) !== null) {
              const expansion = glossary[m[1]];
              if (!expansion) continue;
              if (m.index > last) {
                out.push({ type: "text", value: value.slice(last, m.index) });
              }
              out.push({
                type: "element",
                tagName: "abbr",
                properties: { title: expansion, className: ["abbr-term"] },
                children: [{ type: "text", value: m[1] }],
              });
              last = m.index + m[1].length;
            }
            if (!out.length) return;
            if (last < value.length) {
              out.push({ type: "text", value: value.slice(last) });
            }
            parent.children.splice(index, 1, ...out);
            return index + out.length;
          });
        },
      ];
    },
  };
};

export default Abbreviations;
