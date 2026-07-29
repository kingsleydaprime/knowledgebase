# NextVibe Frontend — Presigned Uploads, Error Handling & Network Status

Split out from the original flat `frontend-learning.md` (kept untouched in the project root).
See also `learning/frontend-forms-ui.md` (the zod file-validation patterns that gate these
uploads), `learning/frontend-state-management.md` (RTK Query mutations these upload flows call
into), `learning/backend-core.md` Part 32 (the backend side of the multipart→presigned-URL
migration), and `learning/devops.md` Part 34/35 (MinIO configuration and how the presigned URL
signature itself works).

This file covers: the full presigned-upload architecture (why routing files through NestJS was
wrong, and the get-URL / PUT-direct / submit-JSON three-step flow using `XMLHttpRequest` for
progress events), the universal `errorHandler()` function used in every `catch` block in this
codebase, browser online/offline detection, the fire-and-forget error logging pattern (with an
NDJSON log file and its Vercel-ephemeral-filesystem caveat), and the "immediate upload on file
selection" UX state machine — including client-side image compression and video format
validation.

---

## 22. Presigned Upload URLs — Streaming Files Directly to Storage

### The problem with the old approach

The original event creation sent files through the NestJS server as `multipart/form-data`:

```
Browser ──── POST (FormData, 200MB video) ──→ NestJS ──→ MinIO
```

Every byte of the file occupied NestJS process memory. A 350MB video would:
- Exhaust server memory on concurrent uploads (OOM kills)
- Hit Nginx/NestJS payload size limits
- Block the event loop for seconds

### The presigned URL architecture

The backend generates a short-lived signed URL that authorises the browser to write directly to MinIO:

```
Browser ─── POST /upload-intent ──→ NestJS (tiny JSON, fast)
Browser ←── { uploadUrl, fileUrl } ── NestJS
Browser ─────── PUT (binary) ──────→ MinIO  (NestJS never sees the file)
Browser ─── POST /v1/events (JSON) → NestJS  (fileUrl is now a plain string)
```

### Step A — request the presigned URL

```ts
// eventApi.ts
uploadIntent: builder.mutation<
  { success: boolean; data: { uploadUrl: string; fileUrl: string } },
  { filename: string; contentType: string; folder: string }
>({
  query: (body) => ({
    url: "/v1/events/upload-intent",
    method: "POST",
    body,
  }),
}),
```

```ts
const intent = await uploadIntent({
  filename: file.name,
  contentType: file.type,  // e.g. "video/mp4"
  folder: "events",
}).unwrap();

// intent.data.uploadUrl — sign PUT to MinIO
// intent.data.fileUrl   — the final CDN URL to store in the database
```

### Step B — stream the binary directly to storage

`fetch` cannot report upload progress. Use `XMLHttpRequest`:

```ts
const uploadFile = (
  file: File,
  uploadUrl: string,
  onProgress?: (pct: number) => void
): Promise<void> =>
  new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", uploadUrl);
    xhr.setRequestHeader("Content-Type", file.type); // must match contentType from Step A

    if (onProgress) {
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable)
          onProgress(Math.round((e.loaded * 100) / e.total));
      };
    }

    xhr.onload = () =>
      xhr.status >= 200 && xhr.status < 300
        ? resolve()
        : reject(new Error(`Upload failed: ${xhr.status}`));
    xhr.onerror = () => reject(new Error("Upload network error"));
    xhr.send(file);
  });
```

> **Why XHR and not fetch?** `fetch` only has `response.body` (a readable stream for downloads). `XMLHttpRequest.upload` exposes progress events for uploads. There is no native upload progress API in the Fetch standard as of 2026.

### Step C — submit plain JSON

Once both uploads resolve, the event body is clean text:

```ts
const body = {
  name: "Tech Summit 2026",
  mode: "ONSITE",
  flierUrl: "https://cdn.nextvibe.com/events/17164-flier.jpg",    // from Step A
  promoVideoUrl: "https://cdn.nextvibe.com/events/17164-promo.mp4",
};

await createEvent(body).unwrap();
```

The backend no longer needs `FileFieldsInterceptor` — it just receives a JSON object. (See `learning/backend-core.md` Part 32 for the full backend-side migration this replaced, including why `flierUrl` had to become optional in the DTO.)

### Showing upload progress in the UI

```tsx
const [uploadProgress, setUploadProgress] = useState<number | null>(null);

// In onSubmit:
setUploadProgress(0);
await uploadFile(file, intent.data.uploadUrl, setUploadProgress);
setUploadProgress(null);

// In JSX:
{uploadProgress !== null && (
  <div className="space-y-1">
    <div className="flex justify-between text-xs text-muted-foreground">
      <span>Uploading video…</span>
      <span>{uploadProgress}%</span>
    </div>
    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
      <div
        className="h-full bg-primary transition-all duration-150"
        style={{ width: `${uploadProgress}%` }}
      />
    </div>
  </div>
)}
```

The submit button should be `disabled={isLoading || uploadProgress !== null}` so the user can't double-submit while the upload is in progress.

### Full onSubmit flow

```ts
const onSubmit = async (values: FormValues) => {
  try {
    let flierUrl: string | undefined;
    let promoVideoUrl: string | undefined;

    if (values.flier) {
      const intent = await uploadIntent({
        filename: values.flier.name,
        contentType: values.flier.type,
        folder: "events",
      }).unwrap();
      await uploadFile(values.flier, intent.data.uploadUrl);
      flierUrl = intent.data.fileUrl;
    }

    if (values.promoVideo) {
      setUploadProgress(0);
      const intent = await uploadIntent({
        filename: values.promoVideo.name,
        contentType: values.promoVideo.type,
        folder: "events",
      }).unwrap();
      await uploadFile(values.promoVideo, intent.data.uploadUrl, setUploadProgress);
      promoVideoUrl = intent.data.fileUrl;
      setUploadProgress(null);
    }

    await createEvent({
      name: values.name,
      mode: values.eventMode,
      ...(flierUrl && { flierUrl }),
      ...(promoVideoUrl && { promoVideoUrl }),
    }).unwrap();

  } catch (err: any) {
    setUploadProgress(null);
    toast.error(err?.data?.message ?? err?.message ?? "Failed to create event");
  }
};
```

(See Part 31 below for the more advanced version of this flow — uploading immediately on file selection instead of waiting for form submit, plus client-side image compression and video validation.)

---

## 28. Universal Error Handler — Full Implementation

A single function that accepts any `unknown` error and returns a human-readable string. Used everywhere a `catch` block needs to show a message.

### Why one central handler?

Without it, every `catch` block has its own ad-hoc logic:
```ts
// Scattered everywhere — inconsistent, hard to maintain
toast.error(err?.data?.message ?? err?.message ?? "Something went wrong");
```

A central handler means: fix the logic in one place, every caller benefits.

### Full implementation (`src/utils/errorHandler.ts`)

```ts
import axios, { AxiosError } from "axios";
import { ZodError } from "zod";

// HTTP status codes → user-friendly messages
const HTTP_STATUS_MESSAGES: Record<number, string> = {
  400: "Bad request. Please check your input.",
  401: "You are not authenticated. Please log in.",
  403: "You do not have permission to perform this action.",
  404: "The requested resource was not found.",
  405: "This action is not allowed.",
  408: "The request timed out. Please try again.",
  409: "A conflict occurred. The resource may already exist.",
  410: "This resource no longer exists.",
  422: "Validation failed. Please check your input.",
  429: "Too many requests. Please slow down and try again.",
  500: "An internal server error occurred. Please try again later.",
  502: "Bad gateway. The server is temporarily unavailable.",
  503: "Service unavailable. Please try again later.",
  504: "Gateway timeout. The server took too long to respond.",
};

// Walks common API response shapes to find a human-readable message.
function extractMessage(data: unknown): string | null {
  if (typeof data === "string" && data) return data;
  if (!data || typeof data !== "object") return null;
  const d = data as Record<string, any>;

  if (typeof d.message === "string" && d.message) return d.message;
  if (typeof d.error === "string" && d.error) return d.error;
  // { error: { message } } — RTK Query / this project's backend shape
  if (d.error && typeof d.error === "object") {
    const nested = d.error as Record<string, any>;
    if (typeof nested.message === "string" && nested.message) return nested.message;
  }
  // { errors: [] } — validation arrays
  if (Array.isArray(d.errors) && d.errors.length > 0) {
    const first = d.errors[0];
    if (typeof first === "string") return first;
    if (typeof first?.message === "string") return first.message;
    if (typeof first?.msg === "string") return first.msg;
  }
  if (typeof d.detail === "string" && d.detail) return d.detail;       // FastAPI / DRF
  if (typeof d.details === "string" && d.details) return d.details;
  if (typeof d.err === "string" && d.err) return d.err;
  if (typeof d.statusMessage === "string" && d.statusMessage) return d.statusMessage; // Nuxt/H3
  return null;
}

// Fire-and-forget log to /api/log-error. Never throws, never blocks.
function fireLog(message: string, error: unknown): void {
  if (typeof fetch === "undefined") return;
  fetch("/api/log-error", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      context: error instanceof Error
        ? { name: error.name, stack: error.stack }
        : undefined,
    }),
  }).catch(() => {});
}

// Inner detection — pure sync, all branches return a string.
function detectMessage(error: unknown): string {
  try {
    // ── RTK Query: { status, data } ─────────────────────────────────────────
    if (error !== null && typeof error === "object" && "status" in error && "data" in error) {
      const e = error as { status: number | string; data: unknown; error?: string };
      const extracted = extractMessage(e.data);
      if (extracted) return extracted;
      const status = typeof e.status === "number" ? e.status : null;
      if (status && HTTP_STATUS_MESSAGES[status]) return HTTP_STATUS_MESSAGES[status];
      if (typeof e.error === "string" && e.error) return e.error; // FETCH_ERROR
      if (e.status === "PARSING_ERROR") return "Failed to parse server response.";
      if (e.status === "TIMEOUT_ERROR") return "Request timed out. Please try again.";
      return "Request failed. Please try again.";
    }

    // ── Axios ────────────────────────────────────────────────────────────────
    if (axios.isAxiosError(error)) {
      const e = error as AxiosError<unknown>;
      if (e.response) {
        const extracted = extractMessage(e.response.data);
        if (extracted) return extracted;
        return HTTP_STATUS_MESSAGES[e.response.status] ?? `Request failed with status ${e.response.status}.`;
      }
      if (e.code === "ECONNABORTED" || e.message.toLowerCase().includes("timeout"))
        return "Request timed out. Please try again.";
      if (e.code === "ERR_NETWORK") return "Network error. Please check your connection.";
      if (e.code === "ERR_CANCELED") return "Request was cancelled.";
      if (e.request) return "No response from the server. Please check your connection.";
      return e.message || "An unknown network error occurred.";
    }

    // ── Zod ──────────────────────────────────────────────────────────────────
    if (error instanceof ZodError) {
      const first = error.issues?.[0];
      if (first?.message) return first.message;
      return "Validation failed. Please check your input.";
    }

    // ── DOM exceptions (AbortError, QuotaExceededError, etc.) ────────────────
    if (error instanceof DOMException) {
      if (error.name === "AbortError") return "Request was cancelled.";
      if (error.name === "QuotaExceededError") return "Storage quota exceeded.";
      if (error.name === "NotAllowedError") return "Permission denied.";
      return error.message || "A browser error occurred.";
    }

    // ── TypeError (fetch failures, network errors) ───────────────────────────
    if (error instanceof TypeError) {
      const msg = error.message.toLowerCase();
      if (msg.includes("failed to fetch") || msg.includes("fetch"))
        return "A network error occurred. Please check your connection.";
      if (msg.includes("networkerror")) return "Network error. Please try again.";
      if (msg.includes("load")) return "Failed to load the resource. Please try again.";
    }

    // ── Generic Error ────────────────────────────────────────────────────────
    if (error instanceof Error) {
      const msg = error.message.toLowerCase();
      if (msg.includes("timeout")) return "Request timed out. Please retry.";
      if (msg.includes("json") || msg.includes("parse")) return "Failed to parse the server response.";
      if (msg.includes("unauthorized") || msg.includes("unauthenticated"))
        return "You are not authenticated. Please log in.";
      if (msg.includes("forbidden")) return "You do not have permission to perform this action.";
      return error.message || "An unexpected error occurred.";
    }

    // ── Custom error-like objects ─────────────────────────────────────────────
    if (typeof error === "object" && error !== null) {
      const extracted = extractMessage(error);
      if (extracted) return extracted;
    }

    if (typeof error === "string" && error) return error;

    return "Something went wrong. Please try again later.";
  } catch {
    return "An unexpected error occurred while handling another error.";
  }
}

// Public API — checks offline first, then detects, then logs.
export function errorHandler(error: unknown): string {
  if (typeof navigator !== "undefined" && !navigator.onLine) {
    return "You are offline. Please check your internet connection.";
  }
  const message = detectMessage(error);
  fireLog(message, error);
  return message;
}
```

### Usage

```ts
} catch (err) {
  toast.error(errorHandler(err));
}
```

### What each branch covers

| Branch | Catches |
|---|---|
| `navigator.onLine` | Any error while the device is offline |
| RTK Query `{ status, data }` | All RTK Query errors including `FETCH_ERROR`, `PARSING_ERROR` |
| Axios | `AxiosError` with response, timeout, network, cancellation |
| Zod | Validation errors from form schemas |
| `DOMException` | `AbortError` (cancelled fetch/XHR), storage quota, permissions |
| `TypeError` | Native `fetch` network failures |
| `Error` | Any thrown `new Error(...)` |
| Plain object | Custom API errors thrown as objects |
| String | Errors thrown as plain strings |

---

## 29. Network Status Detection — Online / Offline

### How browsers know the connection status

The browser tracks network interface availability and exposes it in two ways:

```ts
navigator.onLine  // boolean — true if any network interface is up
```

And two window events:
```ts
window.addEventListener("online", handler);   // fires when connection is restored
window.addEventListener("offline", handler);  // fires when connection is lost
```

### Important limitation

`navigator.onLine: true` only means a network interface exists — **not** that the internet is reachable. A device connected to a WiFi router that has no upstream internet will still show `onLine: true`. The only way to confirm real connectivity is to ping a known endpoint.

### The hook — `src/hooks/useNetworkStatus.ts`

```ts
"use client";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(
    typeof window !== "undefined" ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success("Connection restored", { description: "You're back online" });
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast.error("No internet connection", {
        description: "Please check your network",
        duration: Infinity,  // stays until they come back online
      });
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return { isOnline };
};
```

### The banner — `src/components/network-status-banner.tsx`

```tsx
"use client";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";
import { WifiOff } from "lucide-react";

export const NetworkStatusBanner = () => {
  const { isOnline } = useNetworkStatus();
  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-red-600 text-white px-4 py-2 text-center text-sm font-medium flex items-center justify-center gap-2">
      <WifiOff className="w-4 h-4" />
      <span>No internet connection. Some features may not work.</span>
    </div>
  );
};
```

The banner renders at the very top of the screen (`fixed top-0 z-50`) and disappears automatically when the `online` event fires.

### How this ties into errorHandler

`errorHandler` checks `navigator.onLine` as its very first step. Any error thrown while the device is offline returns "You are offline…" regardless of the actual error shape — the root cause is obvious and the message is the most useful one.

### Extending to real connectivity checks (ping pattern)

```ts
async function checkRealConnectivity(): Promise<boolean> {
  try {
    await fetch("/api/healthz", { method: "HEAD", cache: "no-store" });
    return true;
  } catch {
    return false;
  }
}
```

Use this when you need to distinguish "no interface" from "interface up, internet down".

---

## 30. Error Logging — Fire-and-Forget Pattern

### The problem

`console.log` errors disappear when devtools is closed. In production, you have no visibility into what errors users are seeing.

### The pattern

**Fire-and-forget** means: start an async operation but don't `await` it. The operation runs in the background and the calling code continues immediately.

```ts
// Fire-and-forget — returns void, never blocks
function fireLog(message: string, error: unknown): void {
  fetch("/api/log-error", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  }).catch(() => {}); // swallow log failures — never let logging crash the app
  // ↑ No await — execution continues immediately
}
```

The `.catch(() => {})` at the end is critical. Without it, a failed log write would become an unhandled promise rejection.

### The API route — `src/app/api/log-error/route.ts`

```ts
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "fs";
import { join } from "path";
import { NextRequest, NextResponse } from "next/server";

const LOG_DIR = join(process.cwd(), "logs");
const LOG_FILE = join(LOG_DIR, "errors.log");

// GET /api/log-error — view all logged errors in the browser
export async function GET() {
  try {
    if (!existsSync(LOG_FILE)) return NextResponse.json({ entries: [] });
    const raw = readFileSync(LOG_FILE, "utf8");
    const entries = raw
      .split("\n")
      .filter(Boolean)
      .map((line) => {
        try { return JSON.parse(line); }
        catch { return { raw: line }; }
      });
    return NextResponse.json({ total: entries.length, entries });
  } catch {
    return NextResponse.json({ error: "Could not read log file." }, { status: 500 });
  }
}

// POST /api/log-error — write a new log entry
export async function POST(req: NextRequest) {
  try {
    const { message, context } = await req.json();
    const line = JSON.stringify({
      ts: new Date().toISOString(),
      message,
      ...(context && { context }),
    });
    mkdirSync(LOG_DIR, { recursive: true });
    appendFileSync(LOG_FILE, line + "\n", "utf8"); // sync — fast for a single append
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ ok: false });
  }
}
```

### Log format

Each entry is newline-delimited JSON (NDJSON):
```
{"ts":"2026-05-22T10:23:01.123Z","message":"You are not authenticated.","context":{"name":"Error","stack":"Error: ..."}}
{"ts":"2026-05-22T10:24:15.456Z","message":"Request timed out. Please try again."}
```

Visit `/api/log-error` in the browser while the dev server is running to see all entries.

### Why `appendFileSync` and not `appendFile` (async)?

For a single log line append, the synchronous version is:
- Fast enough (microseconds for one line)
- Simpler — no `await`, no promise
- Safe — the response is only sent after the write completes, so the line is guaranteed to be written

For high-throughput production logging, use a proper log sink (Logtail, Sentry, Datadog) instead of the filesystem.

### Production caveat

Platforms like Vercel use **ephemeral filesystems** — writes to `logs/` don't survive function restarts. On such platforms, swap `appendFileSync` for a database insert or an external logging service. The `fireLog` function in `errorHandler.ts` doesn't need to change at all.

---

## 31. Immediate Upload on File Selection — UX State Machine

### The old UX (bad)

1. User picks a file → nothing visible happens
2. User fills in all other fields
3. User clicks "Create Event"
4. Only now does the upload start
5. Button shows a spinner for 30+ seconds on a large video
6. User has no idea if the upload is working

### The new UX (good)

1. User picks a file → upload starts immediately
2. Progress bar overlaid on the preview — user can see 23%... 47%... 91%... ✓
3. User fills in other fields **while upload runs in the background**
4. Submit button becomes active once upload finishes
5. Clicking Create Event is instant — URLs are already stored

### The state machine

Each file field has its own `UploadState`:

```ts
interface UploadState {
  status: "idle" | "uploading" | "done" | "error";
  progress: number;    // 0–100
  url: string | null;  // the CDN URL returned by the backend
}

const IDLE: UploadState = { status: "idle", progress: 0, url: null };
```

State transitions:
```
idle ──(file selected)──→ uploading ──(XHR done)──→ done
                                    ──(XHR error)──→ error ──(retry)──→ uploading
idle ←──────────────────────────────────────(remove)──────────────────────────
```

### The handler — called directly from onChange

```ts
const handleFlierChange = async (file: File) => {
  // 1. Set in form (for validation + preview)
  setValue("flier", file, { shouldValidate: true });

  // 2. Transition to uploading
  setFlierUpload({ status: "uploading", progress: 0, url: null });

  try {
    // 3. Get presigned URL from backend
    const intent = await uploadIntent({
      filename: file.name,
      contentType: file.type,
      folder: "events",
    }).unwrap();

    // 4. Stream to storage with live progress
    await uploadFile(file, intent.data.uploadUrl, (pct) =>
      setFlierUpload((prev) => ({ ...prev, progress: pct }))
    );

    // 5. Transition to done — store the final CDN URL
    setFlierUpload({ status: "done", progress: 100, url: intent.data.fileUrl });

  } catch {
    setFlierUpload({ status: "error", progress: 0, url: null });
    toast.error("Flyer upload failed. You can retry.");
  }
};
```

Note: the handler is called directly from `onChange` — not inside a `useEffect`. This is intentional. User action triggers upload; reactive effects would cause double-uploads when the component re-renders.

### Inline progress overlay

The file preview shows a dark overlay with spinner + progress bar while uploading:

```tsx
{flierUpload.status === "uploading" && (
  <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center gap-3 p-6">
    <Loader2 className="h-7 w-7 text-white animate-spin" />
    <div className="w-4/5 space-y-1.5">
      <div className="flex justify-between text-white text-xs font-medium">
        <span>Uploading…</span>
        <span>{flierUpload.progress}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-white/30 overflow-hidden">
        <div
          className="h-full bg-white transition-all duration-150"
          style={{ width: `${flierUpload.progress}%` }}
        />
      </div>
    </div>
  </div>
)}

{flierUpload.status === "done" && (
  <div className="absolute top-2 right-2 bg-green-500/90 backdrop-blur-sm rounded-full p-1">
    <CheckCircle2 className="h-4 w-4 text-white" />
  </div>
)}

{flierUpload.status === "error" && (
  <div className="absolute inset-0 bg-red-900/60 flex flex-col items-center justify-center gap-3">
    <AlertCircle className="h-7 w-7 text-white" />
    <p className="text-white text-sm font-medium">Upload failed</p>
    <Button type="button" size="sm" variant="secondary"
      onClick={() => handleFlierChange(flier)}>  {/* retry with same file */}
      Retry
    </Button>
  </div>
)}
```

### Submit uses stored URLs — no re-upload

```ts
const onSubmit = async (values: BasicInfoFormValues) => {
  // Guard: don't submit while uploading
  if (flierUpload.status === "uploading" || videoUpload.status === "uploading") {
    toast.warning("Please wait for uploads to finish.");
    return;
  }
  // Guard: don't submit if upload failed
  if ((values.flier && flierUpload.status === "error") ||
      (values.promoVideo && videoUpload.status === "error")) {
    toast.error("Some uploads failed. Please retry before submitting.");
    return;
  }

  const body = {
    name: values.name,
    // ...other fields
    ...(flierUpload.url && { flierUrl: flierUpload.url }),       // already uploaded
    ...(videoUpload.url && { promoVideoUrl: videoUpload.url }),  // already uploaded
  };

  await createEventMutation(body).unwrap(); // instant — just JSON
};
```

### Button state

```tsx
<Button
  type="submit"
  disabled={isLoading || anyUploading}
>
  {isLoading ? "Creating event…"
   : anyUploading ? "Uploading files…"
   : "Create Event"}
</Button>
```

### Image Compression Before Upload — `browser-image-compression`

Large phone photos (5–10 MB) make uploads slow regardless of the storage backend. Compressing client-side before the XHR reduces a typical photo from 5 MB to ~200–400 KB — a 10–15× improvement with no perceptible quality loss for event fliers.

```bash
npm install browser-image-compression
```

```ts
import imageCompression from "browser-image-compression";

const handleFlierChange = async (file: File) => {
  if (file.size > 10 * 1024 * 1024) {
    toast.warning("Flyer must be 10 MB or less.");
    return;
  }
  setValue("flier", file, { shouldValidate: true });
  setFlierUpload({ status: "uploading", progress: 0, url: null });

  try {
    // Compress images; pass non-image files straight through
    const toUpload = file.type.startsWith("image/")
      ? await imageCompression(file, {
          maxSizeMB: 1,             // target ≤ 1 MB output
          maxWidthOrHeight: 1920,   // cap at 1920px — enough for any flier
          useWebWorker: true,       // runs off the main thread, UI stays responsive
          fileType: "image/jpeg",   // always output JPEG for best size/quality ratio
        })
      : file;

    const intent = await uploadIntent({
      filename: file.name,
      contentType: toUpload.type,
      folder: "events",
    }).unwrap();

    await uploadFile(toUpload, intent.data.uploadUrl, (pct) =>
      setFlierUpload((prev) => ({ ...prev, progress: pct }))
    );
    setFlierUpload({ status: "done", progress: 100, url: intent.data.fileUrl });
  } catch {
    setFlierUpload({ status: "error", progress: 0, url: null });
    toast.error("Flyer upload failed. You can retry.");
  }
};
```

**Key options:**
- `maxSizeMB: 1` — the library targets this size; it's a goal, not a guarantee
- `useWebWorker: true` — compression runs in a background thread; no UI freeze even for large files
- `fileType: "image/jpeg"` — forces JPEG output regardless of input (PNG → JPEG, WEBP → JPEG). Don't use for logos/icons with transparency — alpha channel is lost.

**Why `intent.data.uploadUrl` (not `intent.uploadUrl`)?** The backend wraps all responses in a global `ResponseInterceptor` as `{ success: true, data: { ... } }`. RTK Query resolves the full response, so you access the payload at `result.data.uploadUrl`. Every successful API call from this backend follows this `{ success, data }` envelope shape.

**No video compression client-side:** `browser-image-compression` only handles images. Video compression in the browser is too slow (minutes for large files). Users must pre-compress or stay within the size limit. (See `learning/devops.md` Part 34 for the server-side short-term fix — this same compression library — and the longer-term Cloudflare R2 migration recommended alongside it.)

### Video Format Validation

Two checks before attempting a video upload — format first, then size:

```ts
const MAX_VIDEO_SIZE = 350 * 1024 * 1024; // 350 MB
const ACCEPTED_VIDEO_TYPES = ["video/mp4", "video/quicktime", "video/webm"];

const handleVideoChange = async (file: File) => {
  // Format check first — an unsupported format is completely unrecoverable
  if (!ACCEPTED_VIDEO_TYPES.includes(file.type)) {
    toast.error("Please upload an MP4, MOV, or WebM video.");
    return;
  }
  // Size check second — a large MP4 is at least redeemable (user can re-encode it)
  if (file.size > MAX_VIDEO_SIZE) {
    toast.error("Video must be 350 MB or less.");
    return;
  }
  // proceed with upload (same presigned URL pattern, no compression)
};
```

**Format before size:** surface the more actionable error first. An unsupported format can't be uploaded at all; a large MP4 can be re-encoded.

**Restrict the file picker:**
```tsx
<input type="file" accept="video/mp4,video/quicktime,video/webm" />
```

This filters the OS file dialog, but the `file.type` check in the handler is still required — users can bypass `accept` by typing a path directly.

**Zod schema with two refines (separate error messages):**
```ts
promoVideo: z
  .instanceof(File)
  .optional()
  .nullable()
  .refine(
    (f) => !f || ACCEPTED_VIDEO_TYPES.includes(f.type),
    { message: "Video must be MP4, MOV, or WebM format" }
  )
  .refine(
    (f) => !f || f.size <= MAX_VIDEO_SIZE,
    { message: "Video must be 350 MB or less" }
  ),
```

Two `.refine()` calls produce two distinct error messages. One combined refine would give a generic message for both failure modes.

---

## Updated Quick Reference

### Presigned upload flow

```ts
// 1. Get permission
const intent = await uploadIntent({ filename, contentType, folder }).unwrap();

// 2. Stream to storage (with progress)
await new Promise((resolve, reject) => {
  const xhr = new XMLHttpRequest();
  xhr.open("PUT", intent.data.uploadUrl);
  xhr.setRequestHeader("Content-Type", file.type);
  xhr.upload.onprogress = (e) => setProgress(Math.round(e.loaded * 100 / e.total));
  xhr.onload = () => resolve();
  xhr.onerror = () => reject();
  xhr.send(file);
});

// 3. Submit JSON
await createEvent({ flierUrl: intent.data.fileUrl, ... }).unwrap();
```
