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
