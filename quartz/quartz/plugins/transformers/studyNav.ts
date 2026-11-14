/**
 * StudyNav: build-time navigation for every note.
 *
 * Adds, as plain HTML (no fetch, so it works before the explorer has loaded):
 *   - real titles: a note with no frontmatter `title` takes its first `# Heading`,
 *     instead of the filename ("01-what-a-database-is" becomes "What a database is");
 *   - the end-of-note card: "Mark as done", previous/next in folder order, and "back to";
 *   - on folder index pages: a progress bar and a "Start" / "Continue" button;
 *   - on the home page: a dashboard of subjects as coloured cards with progress;
 *   - on every other page: a floating "Subjects" button that opens a quick-jump sheet;
 *   - flashcards: every "Answer" toggle becomes a card. Each note and folder gets a deck,
 *     written by the StudyDecks emitter (bottom of this file) to static/decks/ and
 *     static/cards/, and a "Practise" button that opens it.
 *
 * Progress itself lives in the browser (localStorage) and is drawn by
 * components/scripts/interactive-learning.inline.ts, which reads the data-*
 * attributes this file writes.
 *
 * Runs after every other transformer (see config-loader.ts), so crawl-links never
 * sees the pager links and they don't show up in backlinks or the graph.
 */
import fs from "fs"
import path from "path"
import { visit, SKIP } from "unist-util-visit"
import type { Root, Element, ElementContent } from "hast"
import { find, html as htmlSchema, svg as svgSchema } from "property-information"
import { QuartzEmitterPlugin, QuartzTransformerPlugin } from "../types"
import { ProcessedContent } from "../vfile"
import { write } from "../emitters/helpers"
import { BuildCtx } from "../../util/ctx"
import { FullSlug, resolveRelative } from "../../util/path"

// ── Subjects on the home page ────────────────────────────────────────────────
// Folder → [emoji, group]. A top-level folder with an index.md that isn't listed
// still appears, under "More".
const GROUPS: { name: string; hue: number }[] = [
  { name: "Software engineering", hue: 217 },
  { name: "Infrastructure & security", hue: 262 },
  { name: "AI & data", hue: 160 },
  { name: "Computer science", hue: 195 },
  { name: "Hardware & engineering", hue: 28 },
  { name: "More", hue: 330 },
]
const SUBJECTS: Record<string, [string, number]> = {
  "software-engineering": ["🧭", 0],
  "programming-fundamentals": ["🌱", 0],
  languages: ["🗣️", 0],
  dsa: ["🧩", 0],
  backend: ["⚙️", 0],
  frontend: ["🎨", 0],
  mobile: ["📱", 0],
  desktop: ["🖥️", 0],
  databases: ["🗄️", 0],
  architecture: ["🏛️", 0],
  concepts: ["💡", 0],
  git: ["🌿", 0],
  "build-your-own-shit": ["🛠️", 0],
  "game-development": ["🎮", 0],
  tools: ["🧰", 0],
  devops: ["🚀", 1],
  networking: ["🌐", 1],
  os: ["🐧", 1],
  cybersecurity: ["🔐", 1],
  web3: ["⛓️", 1],
  "ai-ml": ["🧠", 2],
  "using-ai": ["🤖", 2],
  "ai-automation": ["⚡", 2],
  "data-analysis": ["📊", 2],
  "data-engineering": ["🏗️", 2],
  "operations-research": ["📈", 2],
  "how-computers-work": ["🔌", 3],
  "computer-architecture": ["🧮", 3],
  compilers: ["🔤", 3],
  "theory-of-computation": ["♾️", 3],
  "information-theory": ["📡", 3],
  "programming-language-theory": ["λ", 3],
  "gpu-and-parallel-computing": ["🎛️", 3],
  "computer-graphics": ["🖌️", 3],
  mathematics: ["∑", 3],
  hardware: ["🔧", 4],
  robotics: ["🦾", 4],
  "control-theory": ["🎚️", 4],
  "continuum-mechanics": ["🌊", 4],
  "digital-signal-processing": ["〰️", 4],
  "systems-engineering": ["🧱", 4],
  astronomy: ["🔭", 4],
  research: ["📝", 5],
  projects: ["📓", 5],
  learning: ["🎓", 5],
}
const HIDDEN_SUBJECTS = new Set(["sources", "tags"])
const FEATURED = ["learning/swe-101", "learning/swe-102", "learning/swe-103"]

// ── Small hast builder ───────────────────────────────────────────────────────
type Child = ElementContent | string | null | undefined | false | Child[]
function h(tag: string, props: Record<string, unknown>, ...children: Child[]): Element {
  const kids: ElementContent[] = []
  for (const c of (children as unknown[]).flat(Infinity) as Child[]) {
    if (c === null || c === undefined || c === false) continue
    kids.push(typeof c === "string" ? { type: "text", value: c } : (c as ElementContent))
  }
  return { type: "element", tagName: tag, properties: props as Element["properties"], children: kids }
}

// ── The note tree, built once per build from ctx.allFiles ────────────────────
interface NoteInfo {
  slug: FullSlug
  node: string // slug without a trailing "/index"; "" for the home page
  title: string
  explicitTitle: boolean
  hasAnswers: boolean // the raw markdown has an "Answer" toggle, so it will have cards
}
interface Tree {
  notes: Map<string, NoteInfo> // by node
  bySlug: Map<string, NoteInfo>
  children: Map<string, string[]> // node → ordered child nodes
  totals: Map<string, number> // node → number of notes under it
  withCards: Set<string> // nodes with at least one card in them or below them
}

let cache: { key: unknown; tree: Tree } | undefined

function nodeOf(slug: string): string {
  if (slug === "index") return ""
  return slug.endsWith("/index") ? slug.slice(0, -"/index".length) : slug
}

function parentOf(node: string): string {
  const i = node.lastIndexOf("/")
  return i === -1 ? "" : node.slice(0, i)
}

function cleanInline(s: string): string {
  return s
    .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2")
    .replace(/\[\[([^\]]+)\]\]/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/[*_`]/g, "")
    .trim()
}

function prettyStem(stem: string): string {
  const s = stem.replace(/^\d+[-_.]\s*/, "").replace(/[-_]+/g, " ").trim()
  return s ? s[0].toUpperCase() + s.slice(1) : stem
}

/** Title from the raw markdown: frontmatter `title`, else the first `# H1` outside code, else the filename. */
const ANSWER_SUMMARY = /<summary>\s*Answers?\b/i

function readNote(file: string, fallback: string): { title: string; explicit: boolean; hasAnswers: boolean } {
  let text = ""
  try {
    text = fs.readFileSync(file, "utf8")
  } catch {
    return { title: fallback, explicit: false, hasAnswers: false }
  }
  return { ...readTitle(text, fallback), hasAnswers: ANSWER_SUMMARY.test(text) }
}

function readTitle(full: string, fallback: string): { title: string; explicit: boolean } {
  const text = full.slice(0, 20000)
  const fm = text.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (fm) {
    const t = fm[1].match(/^title:\s*(.+?)\s*$/m)
    if (t) return { title: t[1].replace(/^["']|["']$/g, ""), explicit: true }
  }
  let inFence = false
  for (const line of text.split(/\r?\n/)) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence
    else if (!inFence && /^# \S/.test(line)) return { title: cleanInline(line.slice(2)), explicit: false }
  }
  return { title: fallback, explicit: false }
}

function sortKey(node: string): [number, string] {
  const name = node.slice(node.lastIndexOf("/") + 1)
  const m = name.match(/^(\d+)/)
  return [m ? parseInt(m[1], 10) : Number.MAX_SAFE_INTEGER, name]
}

function buildTree(ctx: BuildCtx): Tree {
  const notes = new Map<string, NoteInfo>()
  const bySlug = new Map<string, NoteInfo>()
  ctx.allFiles.forEach((fp, i) => {
    if (!fp.endsWith(".md")) return
    const slug = ctx.allSlugs[i]
    const node = nodeOf(slug)
    const stem = path.basename(fp, ".md")
    const fallback = prettyStem(stem === "index" ? path.basename(path.dirname(fp)) : stem)
    const { title, explicit, hasAnswers } = readNote(path.join(ctx.argv.directory, fp), fallback)
    const info = { slug, node, title, explicitTitle: explicit, hasAnswers }
    notes.set(node, info)
    bySlug.set(slug, info)
  })

  const children = new Map<string, string[]>()
  const totals = new Map<string, number>()
  const withCards = new Set<string>()
  for (const [node, info] of notes) {
    if (info.hasAnswers) {
      for (let p = node; ; p = parentOf(p)) {
        withCards.add(p)
        if (p === "") break
      }
    }
    if (node === "") continue
    // count this note toward every folder above it
    let p = parentOf(node)
    for (;;) {
      totals.set(p, (totals.get(p) ?? 0) + 1)
      if (p === "") break
      p = parentOf(p)
    }
    // attach to the nearest ancestor that is itself a note (folders without index.md are skipped)
    let parent = parentOf(node)
    while (parent !== "" && !notes.has(parent)) parent = parentOf(parent)
    if (!children.has(parent)) children.set(parent, [])
    children.get(parent)!.push(node)
  }
  for (const list of children.values()) {
    list.sort((a, b) => {
      const [na, sa] = sortKey(a)
      const [nb, sb] = sortKey(b)
      return na - nb || sa.localeCompare(sb)
    })
  }
  return { notes, bySlug, children, totals, withCards }
}

function getTree(ctx: BuildCtx): Tree {
  if (!cache || cache.key !== ctx.allSlugs) cache = { key: ctx.allSlugs, tree: buildTree(ctx) }
  return cache.tree
}

// ── Flashcards: turning "Answer" toggles into cards ──────────────────────────
// Notes write checks in three ways, and all three become cards:
//   1. a question paragraph, then <details><summary>Answer</summary>…</details>;
//   2. a list item holding the question and its own <details>;
//   3. a numbered list of questions, then one <details><summary>Answers</summary> holding a
//      numbered list of answers. Question 1 pairs with answer 1, and so on.
export interface StudyCard {
  id: string // stable while the question text and the note stay the same
  q: string // question, as HTML
  a: string // answer, as HTML
  s: string // the note's path from the site root ("databases/03-b-trees", "databases/")
  t: string // the note's title
}

declare module "vfile" {
  interface DataMap {
    studyCards: StudyCard[]
  }
}

const isEl = (n: unknown): n is Element => (n as Element)?.type === "element"
const isBlank = (n: ElementContent) => n.type === "text" && n.value.trim() === ""
const STOP_TAGS = new Set(["h1", "h2", "h3", "h4", "h5", "h6", "hr", "details"])

function textOf(n: ElementContent | Root): string {
  if (n.type === "text") return n.value
  if (n.type === "element" || n.type === "root") return (n.children as ElementContent[]).map(textOf).join("")
  return ""
}

/** FNV-1a, 32-bit, as base 36: short and stable. */
function hash(s: string): string {
  let x = 0x811c9dc5
  for (let i = 0; i < s.length; i++) {
    x ^= s.charCodeAt(i)
    x = Math.imul(x, 0x01000193)
  }
  return (x >>> 0).toString(36)
}

const VOID = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"])
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

/** hast → HTML string, for the deck files. */
function toHtml(nodes: ElementContent[], inSvg = false): string {
  let out = ""
  for (const n of nodes) {
    if (n.type === "text") out += esc(n.value)
    else if (n.type === "element") {
      const svg = inSvg || n.tagName === "svg"
      let attrs = ""
      for (const [k, v] of Object.entries(n.properties ?? {})) {
        if (v === null || v === undefined || v === false) continue
        if (k === "id") continue // heading ids would clash with the page the deck opens on
        const info = find(svg ? svgSchema : htmlSchema, k)
        if (v === true) {
          attrs += ` ${info.attribute}`
          continue
        }
        const val = Array.isArray(v) ? v.join(info.commaSeparated ? "," : " ") : String(v)
        attrs += ` ${info.attribute}="${esc(val).replace(/"/g, "&quot;")}"`
      }
      out += `<${n.tagName}${attrs}>`
      if (VOID.has(n.tagName)) continue
      out += toHtml(n.children as ElementContent[], svg && n.tagName !== "foreignObject")
      out += `</${n.tagName}>`
    } else if ((n as { type: string }).type === "raw") out += (n as unknown as { value: string }).value
  }
  return out
}

function answerSummary(d: Element): string | null {
  const summary = d.children.find((c) => isEl(c) && c.tagName === "summary")
  if (!summary) return null
  const text = textOf(summary as Element).trim()
  return /^answers?\b/i.test(text) ? text : null
}

const listItems = (ol: Element) => ol.children.filter((c): c is Element => isEl(c) && c.tagName === "li")

function rateRow(id: string): Element {
  return h(
    "div",
    { className: ["su-rate"], dataSuCard: id },
    h("button", { type: "button", className: ["su-rate-btn", "again"], dataRate: "again" }, "↺ Again"),
    h("button", { type: "button", className: ["su-rate-btn", "good"], dataRate: "good" }, "✓ Got it"),
  )
}

/**
 * Finds the cards in one page, marks each answer with data-su-card (so the page and
 * the deck agree on ids) and adds "Again / Got it" buttons under each answer.
 */
function extractCards(root: Root, me: NoteInfo): StudyCard[] {
  const cards: StudyCard[] = []
  const seen = new Map<string, number>()
  const s = me.slug === "index" ? "" : me.slug.replace(/\/index$/, "/")
  const add = (q: ElementContent[], a: ElementContent[], mark: Element) => {
    const qText = q.map(textOf).join(" ").replace(/\s+/g, " ").trim()
    if (qText.length < 3 || a.every(isBlank)) return
    let id = hash(me.node + "|" + qText)
    const n = seen.get(id) ?? 0 // the same question twice on one page
    seen.set(id, n + 1)
    if (n) id += "-" + n
    cards.push({ id, q: toHtml(q), a: toHtml(a), s, t: me.title })
    mark.properties = { ...mark.properties, dataSuCard: id }
    mark.children.push(rateRow(id))
  }

  const walk = (parent: Element | Root) => {
    const kids = parent.children as ElementContent[]
    for (let i = 0; i < kids.length; i++) {
      const d = kids[i]
      if (!isEl(d)) continue
      if (d.tagName !== "details") {
        walk(d)
        continue
      }
      const summaryText = answerSummary(d)
      if (summaryText === null) continue
      const body = d.children.filter((c) => !(isEl(c) && c.tagName === "summary") && !isBlank(c))
      const innerOl = body.length === 1 && isEl(body[0]) && body[0].tagName === "ol" ? body[0] : null

      // previous element siblings, nearest first, up to a heading or another answer
      const before: Element[] = []
      for (let j = i - 1; j >= 0 && before.length < 4; j--) {
        const c = kids[j]
        if (!isEl(c)) continue
        if (STOP_TAGS.has(c.tagName)) break
        before.push(c)
      }

      // pattern 3: numbered questions, numbered answers
      if (innerOl) {
        const answers = listItems(innerOl)
        const qs = before.find((c) => c.tagName === "ol" && listItems(c).length === answers.length)
        if (qs) {
          const questions = listItems(qs)
          answers.forEach((li, k) => add(questions[k].children, [...li.children], li))
          continue
        }
      }
      // pattern 2: the question and its answer share a list item
      if (isEl(parent) && parent.tagName === "li") {
        add(kids.slice(0, i).filter((c) => !isBlank(c)), body, d)
        continue
      }
      // pattern 1: the question is the paragraph (or list) just before
      if (before[0]) add([before[0]], body, d)
    }
  }
  walk(root)
  return cards
}

// ── Pieces of UI ─────────────────────────────────────────────────────────────
function progressBar(node: string, total: number, extra = ""): Element {
  return h(
    "div",
    { className: ["su-progress", extra].filter(Boolean), dataPrefix: node === "" ? "" : node + "/", dataTotal: total },
    h("div", { className: ["su-progress-track"] }, h("div", { className: ["su-progress-fill"] })),
    h("span", { className: ["su-progress-label"] }, `0 of ${total} done`),
  )
}

function parentLink(tree: Tree, node: string): string {
  let p = parentOf(node)
  while (p !== "" && !tree.notes.has(p)) p = parentOf(p)
  return p
}

function siblingsOf(tree: Tree, node: string): string[] {
  return tree.children.get(parentLink(tree, node)) ?? []
}

function pagerCard(tree: Tree, from: FullSlug, node: string | undefined, dir: "prev" | "next", label: string) {
  if (node === undefined) return h("span", { className: ["su-pager-card", "su-pager-empty", dir] })
  const info = tree.notes.get(node)!
  return h(
    "a",
    { className: ["su-pager-card", dir], href: resolveRelative(from, info.slug), dataSuNav: dir },
    h("span", { className: ["su-pager-dir"] }, label),
    h("span", { className: ["su-pager-title"] }, info.title),
  )
}

function lessonEnd(tree: Tree, me: NoteInfo, cardCount: number, hasHero: boolean): Element {
  const sibs = siblingsOf(tree, me.node)
  const i = sibs.indexOf(me.node)
  const prev = i > 0 ? sibs[i - 1] : undefined
  let next = i >= 0 && i < sibs.length - 1 ? sibs[i + 1] : undefined
  let nextLabel = "Next →"
  // a folder's own page continues into its first child
  const kids = tree.children.get(me.node)
  if (kids?.length) {
    next = kids[0]
    nextLabel = "Start →"
  } else if (next === undefined) {
    // end of this folder: continue into the parent's next sibling
    const parent = parentLink(tree, me.node)
    if (parent !== "") {
      const up = siblingsOf(tree, parent)
      const j = up.indexOf(parent)
      if (j >= 0 && j < up.length - 1) {
        next = up[j + 1]
        nextLabel = "Next section →"
      }
    }
  }
  const parent = parentLink(tree, me.node)
  const parentInfo = tree.notes.get(parent)
  return h(
    "section",
    { className: ["su-lesson-end"], dataSlug: me.slug },
    cardCount && !hasHero ? practiceButton(me.node, me.title, cardCount) : null,
    h(
      "button",
      { className: ["su-done-btn"], type: "button", dataSlug: me.slug },
      h("span", { className: ["su-done-icon"], ariaHidden: "true" }, "✓"),
      h("span", { className: ["su-done-label"] }, "Mark as done"),
    ),
    h(
      "nav",
      { className: ["su-pager"], ariaLabel: "Previous and next note" },
      pagerCard(tree, me.slug, prev, "prev", "← Previous"),
      pagerCard(tree, me.slug, next, "next", nextLabel),
    ),
    parentInfo
      ? h(
          "a",
          { className: ["su-up"], href: resolveRelative(me.slug, parentInfo.slug) },
          `↑ Back to ${parentInfo.title}`,
        )
      : null,
  )
}

/** "Practice" opens the deck for `node`. The script fills in the counts once the deck has loaded. */
function practiceButton(node: string, title: string, count?: number): Element {
  return h(
    "div",
    { className: ["su-practice"] },
    h(
      "button",
      { className: ["su-btn", "su-btn-cards", "su-practice-btn"], type: "button", dataDeck: node, dataTitle: title },
      h("span", { ariaHidden: "true" }, "🃏"),
      h("span", { className: ["su-practice-label"] }, count ? `Practise ${count} card${count === 1 ? "" : "s"}` : "Practise cards"),
    ),
    h("span", { className: ["su-practice-meta"] }),
  )
}

function folderHero(tree: Tree, me: NoteInfo): Element | null {
  const kids = tree.children.get(me.node)
  const total = tree.totals.get(me.node) ?? 0
  if (!kids?.length || total < 2) return null
  // every note under this folder, in reading order, for the "Continue" button
  const order: string[][] = []
  const walk = (n: string) => {
    for (const k of tree.children.get(n) ?? []) {
      const info = tree.notes.get(k)!
      order.push([info.slug, resolveRelative(me.slug, info.slug), info.title])
      walk(k)
    }
  }
  walk(me.node)
  return h(
    "div",
    { className: ["su-folder-hero"], dataOrder: JSON.stringify(order) },
    progressBar(me.node, total),
    h(
      "a",
      { className: ["su-btn", "su-btn-primary", "su-continue"], href: order[0][1] },
      h("span", { className: ["su-continue-label"] }, "Start here"),
      h("span", { className: ["su-continue-title"] }, order[0][2]),
    ),
    tree.withCards.has(me.node) ? practiceButton(me.node, me.title) : null,
  )
}

interface Subject {
  info: NoteInfo
  emoji: string
  group: number
  total: number
}

function subjects(tree: Tree): Subject[] {
  const out: Subject[] = []
  for (const node of tree.children.get("") ?? []) {
    if (node.includes("/") || HIDDEN_SUBJECTS.has(node) || !(tree.children.get(node)?.length)) continue
    const [emoji, group] = SUBJECTS[node] ?? ["📁", GROUPS.length - 1]
    out.push({ info: tree.notes.get(node)!, emoji, group, total: tree.totals.get(node) ?? 0 })
  }
  return out
}

function shortTitle(t: string): string {
  return t.split(/\s+[—–-]\s+/)[0]
}

function subjectCard(from: FullSlug, s: Subject, hue: number): Element {
  return h(
    "a",
    { className: ["su-card"], href: resolveRelative(from, s.info.slug), style: `--su-hue: ${hue}` },
    h("span", { className: ["su-card-emoji"], ariaHidden: "true" }, s.emoji),
    h("span", { className: ["su-card-title"] }, shortTitle(s.info.title)),
    h("span", { className: ["su-card-meta"] }, `${s.total} notes`),
    progressBar(s.info.node, s.total, "su-progress-mini"),
  )
}

function homeDashboard(tree: Tree, me: NoteInfo): Element {
  const all = subjects(tree)
  const featured = FEATURED.map((n) => tree.notes.get(n)).filter((x): x is NoteInfo => !!x)
  const total = tree.totals.get("") ?? 0
  return h(
    "div",
    { className: ["su-home"] },
    h(
      "div",
      { className: ["su-hero"] },
      h("p", { className: ["su-hero-kicker"] }, "Welcome back"),
      h("p", { className: ["su-hero-title"] }, "Pick up where you left off, or start something new."),
      h(
        "div",
        { className: ["su-hero-actions"] },
        h(
          "a",
          { className: ["su-btn", "su-btn-primary", "su-resume"], href: "#", hidden: true },
          h("span", { className: ["su-continue-label"] }, "Continue"),
          h("span", { className: ["su-continue-title"] }),
        ),
        featured[0]
          ? h(
              "a",
              { className: ["su-btn", "su-btn-ghost"], href: resolveRelative(me.slug, featured[0].slug) },
              "Open SWE 101",
            )
          : null,
      ),
      h(
        "button",
        { className: ["su-btn", "su-btn-cards", "su-review-btn"], type: "button", hidden: true },
        h("span", { ariaHidden: "true" }, "🃏"),
        h("span", { className: ["su-practice-label"] }, "Review due cards"),
      ),
      progressBar("", total, "su-progress-hero"),
    ),
    featured.length
      ? [
          h("h2", { className: ["su-section-title"], id: "su-courses" }, "Your courses"),
          h(
            "div",
            { className: ["su-grid", "su-grid-featured"] },
            featured.map((f, i) =>
              h(
                "a",
                { className: ["su-card", "su-card-featured"], href: resolveRelative(me.slug, f.slug), style: `--su-hue: ${[217, 160, 262][i % 3]}` },
                h("span", { className: ["su-card-emoji"], ariaHidden: "true" }, "🎓"),
                h("span", { className: ["su-card-title"] }, shortTitle(f.title)),
                h("span", { className: ["su-card-meta"] }, f.title.split(/\s+[—–]\s+/)[1] ?? "Course"),
              ),
            ),
          ),
        ]
      : null,
    GROUPS.map((g, gi) => {
      const items = all.filter((s) => s.group === gi)
      if (!items.length) return null
      return [
        h("h2", { className: ["su-section-title"], id: `su-group-${gi}` }, g.name),
        h("div", { className: ["su-grid"] }, items.map((s) => subjectCard(me.slug, s, g.hue))),
      ]
    }),
    h("h2", { className: ["su-section-title"], id: "su-about" }, "About this knowledge base"),
  )
}

function launcher(tree: Tree, me: NoteInfo): Element {
  const all = subjects(tree)
  return h(
    "div",
    { className: ["su-launcher"] },
    h(
      "button",
      { className: ["su-launcher-btn"], type: "button", ariaLabel: "Jump to a subject", ariaExpanded: "false" },
      h("span", { ariaHidden: "true" }, "▦"),
      h("span", { className: ["su-launcher-btn-label"] }, "Subjects"),
    ),
    h(
      "div",
      { className: ["su-sheet"], role: "dialog", ariaLabel: "Subjects", hidden: true },
      h(
        "div",
        { className: ["su-sheet-inner"] },
        h(
          "div",
          { className: ["su-sheet-head"] },
          h("span", { className: ["su-sheet-title"] }, "Jump to a subject"),
          h("button", { className: ["su-sheet-close"], type: "button", ariaLabel: "Close" }, "✕"),
        ),
        GROUPS.map((g, gi) => {
          const items = all.filter((s) => s.group === gi)
          if (!items.length) return null
          return h(
            "div",
            { className: ["su-sheet-group"] },
            h("p", { className: ["su-sheet-group-title"] }, g.name),
            h(
              "div",
              { className: ["su-chips"] },
              items.map((s) =>
                h(
                  "a",
                  { className: ["su-chip"], href: resolveRelative(me.slug, s.info.slug), style: `--su-hue: ${g.hue}` },
                  `${s.emoji} ${shortTitle(s.info.title)}`,
                ),
              ),
            ),
          )
        }),
      ),
    ),
  )
}

// ── The plugin ───────────────────────────────────────────────────────────────
export const StudyNav: QuartzTransformerPlugin = () => {
  return {
    name: "StudyNav",
    htmlPlugins(ctx) {
      return [
        () => (tree: Root, file) => {
          const slug = file.data.slug as FullSlug | undefined
          if (!slug) return
          const notes = getTree(ctx)
          const me = notes.bySlug.get(slug)
          if (!me) return

          // Real title: drop the first top-level <h1> and use it as the page title,
          // unless the frontmatter already set one.
          if (!me.explicitTitle) {
            let removed = false
            visit(tree, "element", (node: Element, index, parent) => {
              if (removed || node.tagName !== "h1" || !parent || index === undefined) return
              removed = true
              parent.children.splice(index, 1)
              return [SKIP, index]
            })
            const fm = (file.data.frontmatter ?? {}) as Record<string, unknown>
            fm.title = me.title
            file.data.frontmatter = fm as typeof file.data.frontmatter
          }

          if (me.node === "") {
            tree.children.unshift(homeDashboard(notes, me))
            return
          }
          const cards = me.hasAnswers ? extractCards(tree, me) : []
          file.data.studyCards = cards
          const hero = folderHero(notes, me)
          if (hero) tree.children.unshift(hero)
          tree.children.push(lessonEnd(notes, me, cards.length, !!hero), launcher(notes, me))
        },
      ]
    },
  }
}

// ── The deck files ───────────────────────────────────────────────────────────
// Two kinds, so a page only downloads what it shows:
//   static/cards/<note>.json  the note's own cards, with their HTML: { title, cards }
//   static/decks/<node>.json  every card id in a note or folder, in reading order, and the
//                             note each lives in: { title, notes: [note, …], cards: [[id, i], …] }
//                             where i points into notes (each path is written once, not per card)
// A folder page loads its deck (ids only, small even for 2,000 cards) to show counts, and a
// practice session then loads just the notes its 20 cards come from.
async function* writeDecks(ctx: BuildCtx, content: ProcessedContent[]) {
  const tree = getTree(ctx)
  const own = new Map<string, StudyCard[]>()
  for (const [, file] of content) {
    const info = file.data.slug ? tree.bySlug.get(file.data.slug) : undefined
    if (info && file.data.studyCards?.length) own.set(info.node, file.data.studyCards)
  }
  for (const [node, cards] of own) {
    if (node === "") continue
    yield write({
      ctx,
      slug: `static/cards/${node}` as FullSlug,
      ext: ".json",
      content: JSON.stringify({ title: tree.notes.get(node)?.title ?? node, cards }),
    })
  }

  const decks = new Map<string, [string, string][]>()
  const deckOf = (node: string): [string, string][] => {
    let d = decks.get(node)
    if (!d) {
      const mine = (own.get(node) ?? []).map((c): [string, string] => [c.id, node])
      d = [...mine, ...(tree.children.get(node) ?? []).flatMap(deckOf)]
      decks.set(node, d)
    }
    return d
  }
  deckOf("")
  for (const [node, entries] of decks) {
    if (node === "" || entries.length === 0) continue
    const notes: string[] = []
    const index = new Map<string, number>()
    const cards = entries.map(([id, note]) => {
      if (!index.has(note)) index.set(note, notes.push(note) - 1)
      return [id, index.get(note)!]
    })
    yield write({
      ctx,
      slug: `static/decks/${node}` as FullSlug,
      ext: ".json",
      content: JSON.stringify({ title: tree.notes.get(node)?.title ?? node, notes, cards }),
    })
  }
}

export const StudyDecks: QuartzEmitterPlugin = () => ({
  name: "StudyDecks",
  emit: (ctx, content) => writeDecks(ctx, content),
  partialEmit: (ctx, content) => writeDecks(ctx, content),
})
