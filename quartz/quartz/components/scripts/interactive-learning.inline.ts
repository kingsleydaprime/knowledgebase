// Quartz Client Interactive Script — Kingsleys Knowledge Base
// Handles Quizzes, Checkbox Persistence, Code Actions, & Keyboard Shortcuts

const STORAGE_QUIZ = "kb_quiz_progress_v1"
const STORAGE_CHECKBOX = "kb_gate_progress_v1"

interface QuizRecord {
  status: "mastered" | "needs-review"
  timestamp: number
}

function getQuizStorage(): Record<string, QuizRecord> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_QUIZ) || "{}")
  } catch {
    return {}
  }
}

function saveQuizStorage(data: Record<string, QuizRecord>) {
  try {
    localStorage.setItem(STORAGE_QUIZ, JSON.stringify(data))
  } catch (e) {
    console.error("Failed to save quiz progress to localStorage", e)
  }
}

function getCheckboxStorage(): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_CHECKBOX) || "{}")
  } catch {
    return {}
  }
}

function saveCheckboxStorage(data: Record<string, boolean>) {
  try {
    localStorage.setItem(STORAGE_CHECKBOX, JSON.stringify(data))
  } catch (e) {
    console.error("Failed to save checkbox progress to localStorage", e)
  }
}

// ── 1. Interactive Quizzes & Callouts ───────────────────────────────────────
function setupInteractiveQuizzes() {
  const quizCallouts = document.querySelectorAll('.callout[data-callout="quiz"]')
  const quizData = getQuizStorage()

  quizCallouts.forEach((callout, index) => {
    const titleInner = callout.querySelector(".callout-title-inner")
    const titleText = titleInner?.textContent?.trim() || `Quiz #${index + 1}`
    const pageSlug = document.body.dataset.slug || window.location.pathname
    const quizKey = `${pageSlug}::${titleText}`

    // Ensure controls container exists
    let controls = callout.querySelector(".quiz-controls")
    if (!controls) {
      const content = callout.querySelector(".callout-content") || callout
      controls = document.createElement("div")
      controls.className = "quiz-controls"
      controls.innerHTML = `
        <span>Self Rating:</span>
        <button class="quiz-btn btn-mastered" type="button">✓ Mastered</button>
        <button class="quiz-btn btn-review" type="button">⚡ Needs Review</button>
        <span class="quiz-status-badge"></span>
      `
      content.appendChild(controls)
    }

    const btnMastered = controls.querySelector(".btn-mastered") as HTMLButtonElement
    const btnReview = controls.querySelector(".btn-review") as HTMLButtonElement
    const statusBadge = controls.querySelector(".quiz-status-badge") as HTMLElement

    function updateBadgeUI() {
      const rec = quizData[quizKey]
      btnMastered.classList.remove("active-mastered")
      btnReview.classList.remove("active-review")
      if (rec?.status === "mastered") {
        btnMastered.classList.add("active-mastered")
        statusBadge.textContent = "✓ Mastered"
        statusBadge.style.color = "#09ad7a"
      } else if (rec?.status === "needs-review") {
        btnReview.classList.add("active-review")
        statusBadge.textContent = "⚡ Needs Review"
        statusBadge.style.color = "#db8942"
      } else {
        statusBadge.textContent = "Unseen"
        statusBadge.style.color = "var(--gray)"
      }
    }

    updateBadgeUI()

    const onMastered = (e: Event) => {
      e.stopPropagation()
      quizData[quizKey] = { status: "mastered", timestamp: Date.now() }
      saveQuizStorage(quizData)
      updateBadgeUI()
    }

    const onReview = (e: Event) => {
      e.stopPropagation()
      quizData[quizKey] = { status: "needs-review", timestamp: Date.now() }
      saveQuizStorage(quizData)
      updateBadgeUI()
    }

    btnMastered.addEventListener("click", onMastered)
    btnReview.addEventListener("click", onReview)

    window.addCleanup(() => {
      btnMastered.removeEventListener("click", onMastered)
      btnReview.removeEventListener("click", onReview)
    })
  })
}

// ── 2. Checkbox Persistence & Progress Bar ─────────────────────────────────
function setupCheckboxPersistence() {
  const checkboxes = document.querySelectorAll<HTMLInputElement>('article input[type="checkbox"]')
  if (checkboxes.length === 0) return

  const checkboxData = getCheckboxStorage()
  const pageSlug = document.body.dataset.slug || window.location.pathname

  // Restore stored states
  checkboxes.forEach((cb, i) => {
    const text = cb.parentElement?.textContent?.trim() || `cb-${i}`
    const key = `${pageSlug}::${text}`

    if (checkboxData[key] !== undefined) {
      cb.checked = checkboxData[key]
    }

    const onChange = () => {
      checkboxData[key] = cb.checked
      saveCheckboxStorage(checkboxData)
      updateDomainProgressBar()
    }

    cb.addEventListener("change", onChange)
    window.addCleanup(() => cb.removeEventListener("change", onChange))
  })

  updateDomainProgressBar()
}

function updateDomainProgressBar() {
  const checkboxes = Array.from(
    document.querySelectorAll<HTMLInputElement>('article input[type="checkbox"]'),
  )
  if (checkboxes.length === 0) return

  const checkedCount = checkboxes.filter((cb) => cb.checked).length
  const totalCount = checkboxes.length
  const percentage = Math.round((checkedCount / totalCount) * 100)

  let container = document.querySelector(".domain-progress-container")
  const article = document.querySelector("article")

  if (!container && article) {
    container = document.createElement("div")
    container.className = "domain-progress-container"
    article.insertBefore(container, article.firstChild)
  }

  if (container) {
    container.innerHTML = `
      <div class="domain-progress-header">
        <span>Track Progress: ${checkedCount}/${totalCount} Completed</span>
        <span>${percentage}%</span>
      </div>
      <div class="domain-progress-track">
        <div class="domain-progress-fill" style="width: ${percentage}%"></div>
      </div>
    `
  }
}

// ── 3. Code Block Actions (Copy & Playground Links) ────────────────────────
function setupCodeActions() {
  const codeBlocks = document.querySelectorAll("article pre")

  codeBlocks.forEach((pre) => {
    if (pre.querySelector(".code-actions-overlay")) return

    const code = pre.querySelector("code")
    if (!code) return

    const className = code.className || ""
    const match = className.match(/language-(\w+)/)
    const lang = match ? match[1].toLowerCase() : ""

    const overlay = document.createElement("div")
    overlay.className = "code-actions-overlay"

    // Copy Button
    const copyBtn = document.createElement("button")
    copyBtn.className = "code-action-btn"
    copyBtn.type = "button"
    copyBtn.innerHTML = "📋 Copy"

    const onCopy = async () => {
      try {
        await navigator.clipboard.writeText(code.textContent || "")
        copyBtn.innerHTML = "✓ Copied!"
        setTimeout(() => {
          copyBtn.innerHTML = "📋 Copy"
        }, 2000)
      } catch (err) {
        console.error("Failed to copy text", err)
      }
    }
    copyBtn.addEventListener("click", onCopy)
    window.addCleanup(() => copyBtn.removeEventListener("click", onCopy))
    overlay.appendChild(copyBtn)

    // Playground Links
    let playgroundUrl = ""
    let playgroundLabel = ""

    if (lang === "rust") {
      playgroundUrl = `https://play.rust-lang.org/?code=${encodeURIComponent(code.textContent || "")}`
      playgroundLabel = "🚀 Rust Play"
    } else if (lang === "go") {
      playgroundUrl = `https://play.golang.org/`
      playgroundLabel = "🚀 Go Play"
    } else if (lang === "c" || lang === "cpp") {
      playgroundUrl = `https://godbolt.org/`
      playgroundLabel = "⚡ Godbolt"
    } else if (lang === "python" || lang === "py") {
      playgroundUrl = `https://python.org/shell/`
      playgroundLabel = "🐍 Python REPL"
    }

    if (playgroundUrl) {
      const playBtn = document.createElement("a")
      playBtn.className = "code-action-btn"
      playBtn.href = playgroundUrl
      playBtn.target = "_blank"
      playBtn.rel = "noopener noreferrer"
      playBtn.innerHTML = playgroundLabel
      overlay.appendChild(playBtn)
    }

    pre.appendChild(overlay)
  })
}

// ── 4. Global Keyboard Shortcuts ───────────────────────────────────────────
function setupKeyboardShortcuts() {
  let modalBackdrop = document.querySelector(".keyboard-modal-backdrop") as HTMLElement

  if (!modalBackdrop) {
    modalBackdrop = document.createElement("div")
    modalBackdrop.className = "keyboard-modal-backdrop"
    modalBackdrop.innerHTML = `
      <div class="keyboard-modal">
        <h3>⌨️ Keyboard Navigation Shortcuts</h3>
        <div class="shortcut-list">
          <div><kbd>/</kbd> or <kbd>Cmd+K</kbd></div><div>Open Global Search</div>
          <div><kbd>g</kbd> <kbd>h</kbd></div><div>Go to Home (index)</div>
          <div><kbd>g</kbd> <kbd>p</kbd></div><div>Go to Primetechie Path</div>
          <div><kbd>j</kbd> / <kbd>k</kbd></div><div>Next / Previous Course Note</div>
          <div><kbd>?</kbd></div><div>Toggle Shortcuts Legend</div>
          <div><kbd>Esc</kbd></div><div>Close Modals</div>
        </div>
      </div>
    `
    document.body.appendChild(modalBackdrop)

    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) {
        modalBackdrop.classList.remove("active")
      }
    })
  }

  let lastKey = ""

  const onKeyDown = (e: KeyboardEvent) => {
    // Ignore input targets
    const target = e.target as HTMLElement
    if (
      target &&
      (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)
    ) {
      return
    }

    if (document.documentElement.classList.contains("su-practice-open")) return

    if (e.key === "?") {
      e.preventDefault()
      modalBackdrop.classList.toggle("active")
      return
    }

    if (e.key === "Escape") {
      modalBackdrop.classList.remove("active")
      return
    }

    // Two-key chord navigation (e.g. g h, g p)
    if (lastKey === "g") {
      lastKey = ""
      // The site lives under a sub-path on GitHub Pages, so "/" is the wrong root:
      // the page-title link always points at this site's home.
      const home = document.querySelector<HTMLAnchorElement>(".page-title a")?.href ?? "/"
      if (e.key === "h") {
        e.preventDefault()
        window.location.href = home
        return
      }
      if (e.key === "p") {
        e.preventDefault()
        window.location.href = new URL("primetechie", home).href
        return
      }
    }

    if (e.key === "g") {
      lastKey = "g"
      setTimeout(() => {
        lastKey = ""
      }, 1000)
      return
    }

    // Note navigation j / k
    if (e.key === "j" || e.key === "k") {
      // The pager knows the real next/previous note in folder order.
      const pagerLink = document.querySelector<HTMLAnchorElement>(
        `.su-pager a[data-su-nav="${e.key === "j" ? "next" : "prev"}"]`,
      )
      if (pagerLink) {
        e.preventDefault()
        pagerLink.click()
        return
      }
      const courseLinks = Array.from(
        document.querySelectorAll<HTMLAnchorElement>(".explorer a.internal, article a.internal"),
      )
      if (courseLinks.length === 0) return

      const currentPath = window.location.pathname
      const currentIndex = courseLinks.findIndex((a) => a.pathname === currentPath)

      if (currentIndex !== -1) {
        const nextIndex = e.key === "j" ? currentIndex + 1 : currentIndex - 1
        if (nextIndex >= 0 && nextIndex < courseLinks.length) {
          e.preventDefault()
          courseLinks[nextIndex].click()
        }
      }
    }
  }

  window.addEventListener("keydown", onKeyDown)
  window.addCleanup(() => window.removeEventListener("keydown", onKeyDown))
}

// ── 5. Note progress, pager, home dashboard, subjects sheet ─────────────────
// The HTML for all of this is written at build time by plugins/transformers/studyNav.ts;
// this only fills in what depends on the reader: what they've finished and where they were.
const STORAGE_DONE = "kb_done_v1" // slug → { t: when, href: page path }
const STORAGE_LAST = "kb_last_v1" // the last note opened

interface DoneRecord {
  t: number
  href: string
}
interface LastVisit {
  slug: string
  href: string
  title: string
}

function readStore<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function writeStore(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // private window or storage full: progress just isn't remembered
  }
}

function getDone(): Record<string, DoneRecord> {
  return readStore<Record<string, DoneRecord>>(STORAGE_DONE, {})
}

function countDone(done: Record<string, DoneRecord>, prefix: string): number {
  let n = 0
  for (const slug of Object.keys(done)) {
    if (slug === prefix + "index" || slug === "index") continue
    if (prefix === "" || slug.startsWith(prefix)) n++
  }
  return n
}

function refreshProgressBars() {
  const done = getDone()
  document.querySelectorAll<HTMLElement>(".su-progress").forEach((bar) => {
    const prefix = bar.dataset.prefix ?? ""
    const total = Number(bar.dataset.total ?? 0)
    const n = Math.min(countDone(done, prefix), total)
    const pct = total ? Math.round((n / total) * 100) : 0
    const fill = bar.querySelector<HTMLElement>(".su-progress-fill")
    const label = bar.querySelector<HTMLElement>(".su-progress-label")
    if (fill) fill.style.width = `${pct}%`
    if (label) label.textContent = n === total && total > 0 ? `All ${total} done 🎉` : `${n} of ${total} done`
    bar.classList.toggle("is-started", n > 0)
    bar.classList.toggle("is-complete", n === total && total > 0)
  })

  // Folder pages: "Start here" becomes "Continue" with the first unfinished note.
  document.querySelectorAll<HTMLElement>(".su-folder-hero").forEach((hero) => {
    const order = JSON.parse(hero.dataset.order ?? "[]") as [string, string, string][]
    const btn = hero.querySelector<HTMLAnchorElement>(".su-continue")
    if (!btn || order.length === 0) return
    const started = order.some(([slug]) => done[slug])
    const next = order.find(([slug]) => !done[slug])
    const [, href, title] = next ?? order[0]
    btn.href = href
    btn.querySelector(".su-continue-label")!.textContent = !started
      ? "Start here"
      : next
        ? "Continue"
        : "All done. Review"
    btn.querySelector(".su-continue-title")!.textContent = title
  })
}

function samePath(a: string, b: string): boolean {
  const norm = (p: string) => decodeURI(p).replace(/\.html$/, "").replace(/\/index$/, "/").replace(/\/$/, "")
  return norm(a) === norm(b)
}

function markExplorer() {
  const done = Object.values(getDone()).map((r) => r.href)
  document.querySelectorAll<HTMLAnchorElement>(".explorer a").forEach((a) => {
    a.classList.toggle("su-explorer-done", done.some((href) => samePath(href, a.pathname)))
  })
}

function setupExplorerTicks() {
  const explorer = document.querySelector(".explorer")
  if (!explorer) return
  markExplorer()
  // the explorer draws itself after its data arrives, so watch for it
  let queued = false
  const observer = new MutationObserver(() => {
    if (queued) return
    queued = true
    requestAnimationFrame(() => {
      queued = false
      observer.disconnect()
      markExplorer()
      observer.observe(explorer, { childList: true, subtree: true })
    })
  })
  observer.observe(explorer, { childList: true, subtree: true })
  window.addCleanup(() => observer.disconnect())
}

function setupDoneButtons() {
  document.querySelectorAll<HTMLButtonElement>(".su-done-btn").forEach((btn) => {
    if (btn.dataset.bound) return // "render" fired again on the same page
    btn.dataset.bound = "1"
    const slug = btn.dataset.slug ?? ""
    const label = btn.querySelector<HTMLElement>(".su-done-label")
    const render = () => {
      const on = !!getDone()[slug]
      btn.classList.toggle("is-done", on)
      btn.setAttribute("aria-pressed", String(on))
      if (label) label.textContent = on ? "Done" : "Mark as done"
      document.querySelector(".su-pager-card.next")?.classList.toggle("is-suggested", on)
    }
    const onClick = () => {
      const done = getDone()
      if (done[slug]) {
        delete done[slug]
      } else {
        done[slug] = { t: Date.now(), href: window.location.pathname }
        btn.classList.add("su-pop")
        setTimeout(() => btn.classList.remove("su-pop"), 600)
      }
      writeStore(STORAGE_DONE, done)
      render()
      refreshProgressBars()
      markExplorer()
    }
    render()
    btn.addEventListener("click", onClick)
    window.addCleanup(() => btn.removeEventListener("click", onClick))
  })
}

function rememberVisit() {
  const slug = document.body.dataset.slug ?? ""
  if (!slug || slug === "index" || slug === "404") return
  const title = document.querySelector(".article-title")?.textContent?.trim() || document.title
  writeStore(STORAGE_LAST, { slug, href: window.location.pathname, title } satisfies LastVisit)
}

function setupHomeResume() {
  const btn = document.querySelector<HTMLAnchorElement>(".su-resume")
  if (!btn) return
  const last = readStore<LastVisit | null>(STORAGE_LAST, null)
  if (!last) return
  btn.href = last.href
  btn.querySelector(".su-continue-title")!.textContent = last.title
  btn.hidden = false
}

function setupLauncher() {
  // Move the launcher out of the article so position: fixed isn't trapped by a
  // transformed ancestor, and drop the previous page's copy after SPA navigation.
  // "render" can fire again on the same page, so a launcher already set up for this
  // page is kept; one left over from another page is removed.
  const slug = document.body.dataset.slug ?? ""
  const launcher = document.querySelector<HTMLElement>(".su-launcher:not(.is-moved)")
  document.querySelectorAll<HTMLElement>(".su-launcher.is-moved").forEach((old) => {
    if (launcher || old.dataset.forSlug !== slug) old.remove()
  })
  if (!launcher) return
  launcher.classList.add("is-moved")
  launcher.dataset.forSlug = slug
  document.body.appendChild(launcher)

  const btn = launcher.querySelector<HTMLButtonElement>(".su-launcher-btn")!
  const sheet = launcher.querySelector<HTMLElement>(".su-sheet")!
  const close = launcher.querySelector<HTMLButtonElement>(".su-sheet-close")!
  const setOpen = (open: boolean) => {
    sheet.hidden = !open
    btn.setAttribute("aria-expanded", String(open))
    document.documentElement.classList.toggle("su-sheet-open", open)
    if (open) sheet.querySelector<HTMLElement>(".su-chip")?.focus()
  }
  const onBtn = () => setOpen(sheet.hidden)
  const onClose = () => setOpen(false)
  const onBackdrop = (e: MouseEvent) => {
    if (e.target === sheet) setOpen(false)
  }
  const onKey = (e: KeyboardEvent) => {
    if (e.key === "Escape" && !sheet.hidden) setOpen(false)
  }
  const onChip = (e: Event) => {
    if ((e.target as HTMLElement).closest(".su-chip")) setOpen(false)
  }
  btn.addEventListener("click", onBtn)
  close.addEventListener("click", onClose)
  sheet.addEventListener("click", onBackdrop)
  sheet.addEventListener("click", onChip)
  document.addEventListener("keydown", onKey)
  window.addCleanup(() => {
    btn.removeEventListener("click", onBtn)
    close.removeEventListener("click", onClose)
    sheet.removeEventListener("click", onBackdrop)
    sheet.removeEventListener("click", onChip)
    document.removeEventListener("keydown", onKey)
    document.documentElement.classList.remove("su-sheet-open")
  })
}

function setupStudyNav() {
  rememberVisit()
  setupDoneButtons()
  refreshProgressBars()
  setupHomeResume()
  setupLauncher()
  setupExplorerTicks()
  setupFlashcards()
}

// ── 6. Flashcards ───────────────────────────────────────────────────────────
// The cards are found at build time (studyNav.ts). static/decks/<node>.json lists a folder's
// card ids; static/cards/<note>.json holds one note's cards. Content loads only when practised.
// What's stored here is only how well *you* know each card, in boxes (Leitner system):
// a new card you get right goes to box 1 and comes back tomorrow; each "Got it" moves it
// up a box and pushes it further out; "Again" sends it back to box 0, due now.
const STORAGE_CARDS = "kb_cards_v1" // card id → CardRecord
const DAY = 86_400_000
const INTERVALS = [0, 1, 3, 7, 16, 35] // days until a card comes back, by box
const SESSION_SIZE = 20

interface CardRecord {
  b: number // box, 0 to 5
  d: number // due, ms since epoch
  n: string // the note it lives in, so "Review due cards" knows which deck to load
}
interface Card {
  id: string
  q: string
  a: string
  s: string
  t: string
}
type Entry = [id: string, note: string]
interface Deck {
  title: string
  cards: Entry[]
}
interface NoteCards {
  title: string
  cards: Card[]
}

const getCardRecords = () => readStore<Record<string, CardRecord>>(STORAGE_CARDS, {})

function homeUrl(): URL {
  const a = document.querySelector<HTMLAnchorElement>(".page-title a")
  const url = new URL(a?.href ?? "/", window.location.href)
  if (!url.pathname.endsWith("/")) url.pathname += "/"
  return url
}

const nodeOfPath = (s: string) => s.replace(/\/$/, "")

function fetchJson<T>(path: string): Promise<T | null> {
  return fetch(new URL(encodeURI(path), homeUrl()))
    .then((r) => (r.ok ? (r.json() as Promise<T>) : null))
    .catch(() => null)
}

const deckCache = new Map<string, Promise<Deck | null>>()
function loadDeck(node: string): Promise<Deck | null> {
  let p = deckCache.get(node)
  if (!p) {
    // on disk each card points into a list of notes; expand that to [id, note]
    p = fetchJson<{ title: string; notes: string[]; cards: [string, number][] }>(`static/decks/${node}.json`).then(
      (d) => d && { title: d.title, cards: d.cards.map(([id, i]): Entry => [id, d.notes[i]]) },
    )
    deckCache.set(node, p)
  }
  return p
}

const noteCache = new Map<string, Promise<Card[]>>()
function loadNoteCards(note: string): Promise<Card[]> {
  let p = noteCache.get(note)
  if (!p) {
    p = fetchJson<NoteCards>(`static/cards/${note}.json`).then((f) => {
      const cards = f?.cards ?? []
      if (f) forgetRemovedCards(note, cards)
      return cards
    })
    noteCache.set(note, p)
  }
  return p
}

/** Turns ids into cards, loading each note involved once. Cards that no longer exist drop out. */
async function hydrate(entries: Entry[]): Promise<Card[]> {
  const notes = [...new Set(entries.map(([, n]) => n))]
  const byId = new Map<string, Card>()
  for (const cards of await Promise.all(notes.map(loadNoteCards))) for (const c of cards) byId.set(c.id, c)
  return entries.map(([id]) => byId.get(id)).filter((c): c is Card => !!c)
}

/** A card deleted from its note leaves a record behind; drop it so it isn't "due" forever. */
function forgetRemovedCards(note: string, cards: Card[]) {
  const ids = new Set(cards.map((c) => c.id))
  const records = getCardRecords()
  let changed = false
  for (const [id, r] of Object.entries(records)) {
    if (r.n === note && !ids.has(id)) {
      delete records[id]
      changed = true
    }
  }
  if (changed) writeStore(STORAGE_CARDS, records)
}

/** Records an answer. `again` is true if this card was missed earlier in the same session. */
function rateCard(id: string, n: string, good: boolean, missedThisSession = false): CardRecord {
  const records = getCardRecords()
  const now = Date.now()
  const old = records[id]
  let rec: CardRecord
  if (!good) rec = { b: 0, d: now, n }
  else if (old && old.b >= 1 && old.d > now) rec = old // not due yet: knowing it again doesn't move it
  else {
    const b = missedThisSession ? 1 : Math.min((old?.b ?? 0) + 1, INTERVALS.length - 1)
    rec = { b, d: now + INTERVALS[b] * DAY, n }
  }
  records[id] = rec
  writeStore(STORAGE_CARDS, records)
  return rec
}

function deckStats(entries: Entry[]) {
  const records = getCardRecords()
  const now = Date.now()
  let learned = 0
  let due = 0
  for (const [id] of entries) {
    const r = records[id]
    if (!r) continue
    if (r.b >= 1) learned++
    if (r.d <= now) due++
  }
  return { total: entries.length, learned, due }
}

/** Due cards first (oldest first), then new ones in reading order. */
function pickSession(entries: Entry[], extra = false): Entry[] {
  const records = getCardRecords()
  const now = Date.now()
  const dueAt = ([id]: Entry) => records[id]?.d ?? 0
  const due = entries.filter(([id]) => records[id] && records[id].d <= now).sort((a, b) => dueAt(a) - dueAt(b))
  const fresh = entries.filter(([id]) => !records[id])
  const picked = [...due, ...fresh].slice(0, SESSION_SIZE)
  if (picked.length || !extra) return picked
  // everything is learned and nothing is due: practise the ones coming up soonest
  return [...entries].sort((a, b) => dueAt(a) - dueAt(b)).slice(0, SESSION_SIZE)
}

/** Card HTML was written for its own note, so its relative links are resolved against that note. */
function cardFragment(html: string, card: Card): DocumentFragment {
  const tpl = document.createElement("template")
  tpl.innerHTML = html
  const base = new URL(card.s, homeUrl())
  tpl.content.querySelectorAll<HTMLElement>("[href], [src]").forEach((el) => {
    for (const attr of ["href", "src"]) {
      const v = el.getAttribute(attr)
      if (v && !/^([a-z]+:|#|\/)/i.test(v)) el.setAttribute(attr, new URL(v, base).href)
    }
  })
  return tpl.content
}

// The practice screen: one card at a time, flip, then Again or Got it.
let closePractice: (() => void) | null = null

function openPractice(title: string, deck: Entry[], startWith?: Entry[]) {
  closePractice?.()
  let queue: Card[] = []
  let i = 0
  let flipped = false
  let good = 0
  let again = 0
  const missed = new Set<string>()

  const el = document.createElement("div")
  el.className = "su-pr"
  el.setAttribute("role", "dialog")
  el.setAttribute("aria-modal", "true")
  el.setAttribute("aria-label", `Practise: ${title}`)
  el.innerHTML = `
    <div class="su-pr-top">
      <button type="button" class="su-pr-close" aria-label="Close">✕</button>
      <div class="su-pr-head"><span class="su-pr-title"></span><span class="su-pr-count"></span></div>
      <div class="su-pr-track"><div class="su-pr-fill"></div></div>
    </div>
    <div class="su-pr-stage"></div>
    <div class="su-pr-actions"></div>
    <p class="su-pr-keys">Space: flip · 1 or ←: again · 2 or →: got it · Esc: close</p>`
  el.querySelector(".su-pr-title")!.textContent = title
  const stage = el.querySelector<HTMLElement>(".su-pr-stage")!
  const actions = el.querySelector<HTMLElement>(".su-pr-actions")!
  const count = el.querySelector<HTMLElement>(".su-pr-count")!
  const fill = el.querySelector<HTMLElement>(".su-pr-fill")!

  const button = (cls: string, label: string, onClick: () => void) => {
    const b = document.createElement("button")
    b.type = "button"
    b.className = cls
    b.textContent = label
    b.addEventListener("click", onClick)
    return b
  }

  const showCard = () => {
    const card = queue[i]
    flipped = false
    count.textContent = `${i + 1} / ${queue.length}`
    fill.style.width = `${Math.round((i / queue.length) * 100)}%`
    stage.innerHTML = ""
    const box = document.createElement("div")
    box.className = "su-pr-card su-pr-enter"
    box.tabIndex = 0
    const q = document.createElement("div")
    q.className = "su-pr-q"
    q.append(cardFragment(card.q, card))
    const hint = document.createElement("p")
    hint.className = "su-pr-hint"
    hint.textContent = "Say your answer, then tap to check"
    const a = document.createElement("div")
    a.className = "su-pr-a"
    a.hidden = true
    a.append(cardFragment(card.a, card))
    const src = document.createElement("a")
    src.className = "su-pr-source"
    src.href = new URL(card.s, homeUrl()).href
    src.textContent = `From: ${card.t}`
    if (missed.has(card.id)) box.classList.add("is-retry")
    box.append(q, hint, a, src)
    stage.append(box)
    box.addEventListener("click", (e) => {
      if (!flipped && !(e.target as HTMLElement).closest("a")) flip()
    })
    setupSwipe(box)
    actions.innerHTML = ""
    actions.append(button("su-btn su-btn-primary su-pr-reveal", "Show answer", flip))
    box.focus({ preventScroll: true })
  }

  const flip = () => {
    if (flipped) return
    flipped = true
    const box = stage.querySelector<HTMLElement>(".su-pr-card")!
    box.classList.add("is-flipped")
    box.querySelector<HTMLElement>(".su-pr-a")!.hidden = false
    box.querySelector<HTMLElement>(".su-pr-hint")!.hidden = true
    actions.innerHTML = ""
    actions.append(
      button("su-pr-rate again", "↺ Again", () => answer(false)),
      button("su-pr-rate good", "✓ Got it", () => answer(true)),
    )
  }

  const answer = (ok: boolean) => {
    if (!flipped) return
    const card = queue[i]
    rateCard(card.id, nodeOfPath(card.s), ok, missed.has(card.id))
    if (ok) good++
    else {
      again++
      missed.add(card.id)
      // see it again in a few cards' time, this session
      queue = [...queue.slice(0, i + 1), ...queue.slice(i + 1, i + 4), card, ...queue.slice(i + 4)]
    }
    const box = stage.querySelector<HTMLElement>(".su-pr-card")
    box?.classList.add(ok ? "su-pr-out-right" : "su-pr-out-left")
    setTimeout(() => {
      i++
      if (i < queue.length) showCard()
      else finish()
    }, 220)
  }

  const finish = () => {
    count.textContent = ""
    fill.style.width = "100%"
    const firstTry = good - missed.size
    stage.innerHTML = `
      <div class="su-pr-card su-pr-done su-pr-enter">
        <p class="su-pr-done-emoji">🎉</p>
        <p class="su-pr-done-title">Session done</p>
        <p class="su-pr-done-stats"></p>
      </div>`
    stage.querySelector(".su-pr-done-stats")!.textContent =
      `${Math.max(firstTry, 0)} right first time · ${missed.size} needed another go`
    const s = deckStats(deck)
    const more = pickSession(deck)
    actions.innerHTML = ""
    actions.append(button("su-btn su-btn-ghost su-pr-finish", "Close", close))
    if (more.length)
      actions.append(button("su-btn su-btn-primary", `Next ${more.length} cards`, () => start(more)))
    const note = document.createElement("p")
    note.className = "su-pr-done-note"
    note.textContent = `${s.learned} of ${s.total} cards learned in this deck.`
    stage.querySelector(".su-pr-done")!.append(note)
  }

  // Swipe right for "Got it", left for "Again", once the answer is showing.
  const setupSwipe = (box: HTMLElement) => {
    let x0 = 0
    let dx = 0
    let dragging = false
    box.addEventListener("pointerdown", (e) => {
      if (!flipped || (e.target as HTMLElement).closest("a, button")) return
      dragging = true
      x0 = e.clientX
      dx = 0
    })
    box.addEventListener("pointermove", (e) => {
      if (!dragging) return
      dx = e.clientX - x0
      if (Math.abs(dx) > 8) {
        box.style.transform = `translateX(${dx}px) rotate(${dx / 25}deg)`
        box.classList.toggle("is-leaning-right", dx > 40)
        box.classList.toggle("is-leaning-left", dx < -40)
      }
    })
    const end = () => {
      if (!dragging) return
      dragging = false
      box.style.transform = ""
      box.classList.remove("is-leaning-right", "is-leaning-left")
      if (Math.abs(dx) > 90) answer(dx > 0)
    }
    box.addEventListener("pointerup", end)
    box.addEventListener("pointercancel", end)
  }

  const onKey = (e: KeyboardEvent) => {
    e.stopPropagation() // the page's own shortcuts (j, k, …) stay quiet while practising
    if (e.key === "Escape") close()
    else if ((e.key === " " || e.key === "Enter") && !flipped && i < queue.length) {
      e.preventDefault()
      flip()
    } else if (e.key === "1" || e.key === "ArrowLeft") answer(false)
    else if (e.key === "2" || e.key === "ArrowRight") answer(true)
  }

  const close = () => {
    document.removeEventListener("keydown", onKey, true)
    document.documentElement.classList.remove("su-practice-open")
    el.remove()
    closePractice = null
    refreshFlashcards()
  }
  closePractice = close

  el.querySelector(".su-pr-close")!.addEventListener("click", close)
  el.addEventListener("click", (e) => {
    // following a link inside a card leaves practice; Quartz then navigates as usual
    if ((e.target as HTMLElement).closest(".su-pr a")) close()
  })
  document.addEventListener("keydown", onKey, true)
  document.documentElement.classList.add("su-practice-open")
  document.body.append(el)

  const start = async (entries: Entry[]) => {
    stage.innerHTML = `<p class="su-pr-loading">Shuffling the cards…</p>`
    actions.innerHTML = ""
    queue = await hydrate(entries)
    if (closePractice !== close) return // closed while loading
    i = good = again = 0
    missed.clear()
    if (queue.length) showCard()
    else {
      stage.innerHTML = `<div class="su-pr-card su-pr-done"><p class="su-pr-done-title">No cards here yet</p></div>`
      actions.append(button("su-btn su-btn-ghost", "Close", close))
    }
  }
  start(startWith ?? pickSession(deck, true))
}

/** Counts on every Practice button, "Review due cards" on home, and learned marks in the note. */
function refreshFlashcards() {
  document.querySelectorAll<HTMLButtonElement>(".su-practice-btn").forEach((btn) => {
    const node = btn.dataset.deck ?? ""
    const meta = btn.parentElement?.querySelector<HTMLElement>(".su-practice-meta")
    loadDeck(node).then((deck) => {
      if (!deck || deck.cards.length === 0) {
        btn.parentElement!.hidden = true
        return
      }
      const s = deckStats(deck.cards)
      btn.querySelector(".su-practice-label")!.textContent = s.due
        ? `Review ${s.due} due card${s.due === 1 ? "" : "s"}`
        : `Practise ${s.total.toLocaleString()} card${s.total === 1 ? "" : "s"}`
      btn.classList.toggle("has-due", s.due > 0)
      if (meta) meta.textContent = s.learned ? `${s.learned.toLocaleString()} of ${s.total.toLocaleString()} learned` : ""
    })
  })

  const records = getCardRecords()
  const now = Date.now()
  const review = document.querySelector<HTMLButtonElement>(".su-review-btn")
  if (review) {
    const due = Object.values(records).filter((r) => r.d <= now).length
    review.hidden = due === 0
    review.querySelector(".su-practice-label")!.textContent = `Review ${due} due card${due === 1 ? "" : "s"}`
  }

  document.querySelectorAll<HTMLElement>("[data-su-card]:not(.su-rate)").forEach((el) => {
    const r = records[el.dataset.suCard ?? ""]
    el.classList.toggle("su-card-learned", !!r && r.b >= 1)
    el.classList.toggle("su-card-due", !!r && r.d <= now)
  })
}

function setupFlashcards() {
  closePractice?.() // a practice screen left open from the previous page
  refreshFlashcards()

  document.querySelectorAll<HTMLButtonElement>(".su-practice-btn").forEach((btn) => {
    if (btn.dataset.bound) return
    btn.dataset.bound = "1"
    const onClick = () =>
      loadDeck(btn.dataset.deck ?? "").then((deck) => {
        if (deck) openPractice(btn.dataset.title || deck.title, deck.cards)
      })
    btn.addEventListener("click", onClick)
    window.addCleanup(() => btn.removeEventListener("click", onClick))
  })

  const review = document.querySelector<HTMLButtonElement>(".su-review-btn")
  if (review && !review.dataset.bound) {
    review.dataset.bound = "1"
    const onClick = () => {
      const records = getCardRecords()
      const now = Date.now()
      const due = Object.entries(records)
        .filter(([, r]) => r.d <= now)
        .sort((a, b) => a[1].d - b[1].d)
      const entries = due.map(([id, r]): Entry => [id, r.n])
      openPractice("Due cards", entries, entries.slice(0, SESSION_SIZE))
    }
    review.addEventListener("click", onClick)
    window.addCleanup(() => review.removeEventListener("click", onClick))
  }

  // "Again / Got it" under each answer in the note itself
  const slug = document.body.dataset.slug ?? ""
  const node = slug === "index" ? "" : slug.replace(/\/index$/, "")
  document.querySelectorAll<HTMLElement>(".su-rate").forEach((row) => {
    if (row.dataset.bound) return
    row.dataset.bound = "1"
    const onClick = (e: Event) => {
      const b = (e.target as HTMLElement).closest<HTMLButtonElement>(".su-rate-btn")
      if (!b) return
      rateCard(row.dataset.suCard ?? "", node, b.dataset.rate === "good")
      b.classList.add("su-pop")
      setTimeout(() => b.classList.remove("su-pop"), 600)
      refreshFlashcards()
    }
    row.addEventListener("click", onClick)
    window.addCleanup(() => row.removeEventListener("click", onClick))
  })
}

// ── Master Setup ────────────────────────────────────────────────────────────
function setupInteractiveFeatures() {
  setupInteractiveQuizzes()
  setupCheckboxPersistence()
  setupCodeActions()
  setupKeyboardShortcuts()
  setupStudyNav()
}

document.addEventListener("nav", setupInteractiveFeatures)
document.addEventListener("render", setupInteractiveFeatures)
