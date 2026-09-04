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
      if (e.key === "h") {
        e.preventDefault()
        window.location.href = "/"
        return
      }
      if (e.key === "p") {
        e.preventDefault()
        window.location.href = "/PRIMETECHIE"
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

// ── Master Setup ────────────────────────────────────────────────────────────
function setupInteractiveFeatures() {
  setupInteractiveQuizzes()
  setupCheckboxPersistence()
  setupCodeActions()
  setupKeyboardShortcuts()
}

document.addEventListener("nav", setupInteractiveFeatures)
document.addEventListener("render", setupInteractiveFeatures)
