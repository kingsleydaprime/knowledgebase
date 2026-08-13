# SocioBoom Frontend — Create-Post, AI Features & Cross-Page Wiring

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
`learning/frontend/04-architecture.md` (the structural pattern these follow),
`learning/frontend/05-data-fetching.md` (the query and polling layer they use), and
`learning/backend/07-feature-case-studies.md` (the server side of the same two AI features).

This file covers: a full walkthrough of the Create-Post page — platform selection, the content
editor, per-platform variants, media, preview and scheduling — the AI features (Review Poster and
Pain-Point Discovery) from the UI side, and the URL-params pattern that connects the AI pages to the
scheduler without a global store.

---

## 13. The Create-Post Page: A Full Walkthrough

`src/features/posts/pages/create-post.page.tsx` is the most important feature page in the app. Walk through it line by line.

### File Structure

```typescript
"use client"  // Must be first: this is a client component
import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import PlatformSelector from "../components/PlatformSelector";
import PostScheduler from "../components/PostScheduler";
import PostContent from "../components/PostContent";
import PostPreview from "../components/PostPreview";
import { useRouter } from "next/navigation";
```

All shadcn/ui imports use the short `@/components/ui/...` alias. Sub-components (PlatformSelector, PostScheduler, etc.) are imported with relative paths since they are siblings in the same feature folder.

### State Declaration

```typescript
const CreatePostPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [postContent, setPostContent] = useState("");
  const [postDate, setPostDate] = useState<Date>();
  const [postTime, setPostTime] = useState<string>("12:00");
  const [tabValue, setTabValue] = useState("compose");
  const [mediaPreview, setMediaPreview] = useState<string | null>(null);
  const [postLink, setPostLink] = useState<string>("");
  const [displayLinks, setDisplayLinks] = useState<string[]>([]);
```

All form state lives at this component level and is passed down to sub-components. This is **lifting state up** — state is kept at the lowest common ancestor of all components that need it. PlatformSelector needs `selectedPlatforms`; PostPreview also needs it; therefore it must live in their shared parent (CreatePostPage).

### The URL Param Effect

```typescript
useEffect(() => {
  const prefill = searchParams.get("content");
  if (prefill) setPostContent(decodeURIComponent(prefill));
}, [searchParams]);
```

This effect runs whenever `searchParams` changes. When the user navigates to `/posts/new?content=Hello%20World`, `searchParams.get("content")` returns `"Hello World"`, which pre-fills the textarea. `decodeURIComponent` converts URL encoding (`%20` → space, `%0A` → newline).

This is the bridge between the AI features and the scheduler.

### Validation and Submission

```typescript
const handleSchedulePost = () => {
  if (selectedPlatforms.length === 0) {
    toast({
      variant: "destructive",
      title: "Error",
      description: "Please select at least one platform to post to.",
    });
    return;
  }
  // ... more validation
  toast({
    title: "Post Scheduled",
    description: `Your post has been scheduled for ${postDate?.toLocaleDateString()} at ${postTime}`,
  });
  router.push("/");
};
```

The validation pattern: check the condition, show an error toast, and `return` early. All validations run before the actual submit. After success, navigate with `router.push("/")`.

Note: This uses `useToast()` from `@/hooks/use-toast` (the older toast hook from shadcn). The newer AI feature pages use `toast` from `sonner` directly (`import { toast } from "sonner"`). Both work; the newer pages use the simpler API.

### The Two-Column Grid Layout

```typescript
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  {/* Main card: takes 2 of 3 columns */}
  <Card className="md:col-span-2">
    {/* Post content + tabs */}
  </Card>

  {/* Sidebar card: takes 1 of 3 columns */}
  <Card>
    {/* Platform selection + scheduling */}
  </Card>
</div>
```

On mobile (1 column): both cards stack vertically. On medium+ screens (3 columns): the main card takes 2 columns and the settings card takes 1.

### Sub-Component Communication

PlatformSelector needs to both display state and update it:

```typescript
// Parent passes state + setter
<PlatformSelector
  selectedPlatforms={selectedPlatforms}
  onPlatformToggle={handlePlatformToggle}
/>

// handlePlatformToggle is defined in the parent
const handlePlatformToggle = (platform: string) => {
  if (selectedPlatforms.includes(platform)) {
    setSelectedPlatforms(selectedPlatforms.filter((p) => p !== platform));
  } else {
    setSelectedPlatforms([...selectedPlatforms, platform]);
  }
};
```

The `filter` removes a platform; `[...selectedPlatforms, platform]` adds one. Never mutate the array directly — always create a new array.

---

## 14. The AI Features: Review Poster and Pain-Point Discovery

Both AI features follow the same architectural pattern. Understanding one means understanding both.

### Review Poster Architecture (`src/features/reviews/pages/review-poster.page.tsx`)

The page is divided into three sequential steps, each gated on the previous:

```
Step 1: Fetch Reviews (always visible)
  ├── Search by business name (Google, Yelp, Twitter, Reddit buttons)
  └── Or paste manually

Step 2: Select Reviews (visible only when fetchedReviews.length > 0)
  └── ReviewCard for each fetched review (click to select)

Step 3: Generate Posts (visible only when selectedReviews.length > 0)
  ├── Tone selector (Tabs: professional / casual / excited)
  └── Generate button

Right Column: Generated Posts (empty state or GeneratedPostCard list)
```

This progressive disclosure pattern guides users through the workflow without overwhelming them.

### Axios for API Calls

```typescript
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001/api/v1";

const fetchGoogle = async () => {
  if (!businessName.trim()) return;  // guard: do nothing if no input
  setFetching(true);
  try {
    const { data } = await axios.post(`${API}/reviews/fetch-google`, { businessName });
    setFetchedReviews(data.reviews ?? []);  // ?? [] means "use [] if null/undefined"
    if (!data.reviews?.length) toast.info("No Google reviews found.");
  } catch {
    toast.error("Failed to fetch Google reviews.");
  } finally {
    setFetching(false);  // always runs, even if try threw
  }
};
```

`axios.post(url, body)` makes a POST request. The response body is automatically parsed as JSON and available as `data`. The `finally` block ensures `setFetching(false)` always runs — even if the request threw an error — so the loading spinner never gets stuck.

### Sonner Toast API

Review Poster and Pain-Point Discovery use `sonner` (not the older shadcn toast):

```typescript
import { toast } from "sonner";

toast.success("Copied to clipboard");
toast.error("AI generation failed. Check your API key.");
toast.info("No Google reviews found for that business name.");
toast.warning("Something might be wrong");
toast("Plain message with no icon");
```

Sonner toasts appear in the bottom-right of the screen. They auto-dismiss after ~4 seconds. Unlike the older shadcn `useToast()`, you just call `toast.*()` directly — no hook needed.

For sonner to work, you need the `<Toaster>` component mounted once. It is typically placed in the root layout. If you see toasts not appearing, check that `<Toaster />` is in the component tree.

### The `loading/disabled` Pattern

Buttons that trigger async operations follow a consistent pattern:

```typescript
<Button onClick={generate} disabled={generating} className="w-full">
  {generating ? (
    <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Generating...</>
  ) : (
    "Generate Social Posts"
  )}
</Button>
```

- `disabled={generating}` prevents double-clicks while the request is in flight
- `Loader2` with `animate-spin` is the Lucide spinner icon
- The button text changes to provide feedback

### Pain-Point Discovery Architecture (`src/features/discovery/pages/pain-point.page.tsx`)

The same progressive pattern, but simpler:

```
Describe your app (Textarea)
Select platforms (Reddit / Twitter toggle buttons)
Search button → calls /api/v1/discovery/search
  → returns painPoints[]

For each pain point:
  PainPointCard
    ├── Shows platform badge, author, post content
    └── "Generate Reply" button → calls /api/v1/discovery/generate-response
          → fills in generatedResponse on the pain point
          └── Shows "Copy" + "Schedule" buttons
```

The `updateResponse` pattern is worth studying:

```typescript
const updateResponse = (id: number, response: string) => {
  setPainPoints((prev) => prev.map((p) => (p.id === id ? { ...p, generatedResponse: response } : p)));
};
```

This immutably updates one item in an array. `prev.map(...)` creates a new array. For the matching item, `{ ...p, generatedResponse: response }` creates a new object with all the same properties but with `generatedResponse` updated. For non-matching items, it returns them unchanged. This is the standard pattern for updating an item in a state array.

---

## 15. The URL Params Pattern: How AI and Scheduler Connect

The most elegant design decision in the codebase: the AI features communicate with the post scheduler through URL parameters instead of shared state or an event bus.

### The Problem

The Review Poster and Pain-Point Discovery features generate text content. That content needs to get into the Create Post form so the user can schedule it. How?

Options:
1. **Global state (Redux/Zustand/Context)**: Complex. Requires setting up a store, connecting both pages, cleaning up when done.
2. **Clipboard + manual paste**: Requires user action. Error-prone.
3. **URL params**: Simple. Works across page navigations. No state management overhead.

### How It Works

In the AI feature (sender):

```typescript
// In GeneratedPostCard (inside review-poster.page.tsx)
const copyAndSchedule = () => {
  router.push(`/posts/new?content=${encodeURIComponent(post.content)}`);
};

// In PainPointCard (inside pain-point.page.tsx)
const scheduleResponse = () => {
  if (!painPoint.generatedResponse) return;
  router.push(`/posts/new?content=${encodeURIComponent(painPoint.generatedResponse)}`);
};
```

`encodeURIComponent` converts the text to URL-safe encoding:
- Spaces → `%20`
- Newlines → `%0A`
- Colons → `%3A`
- etc.

In the scheduler (receiver):

```typescript
// In create-post.page.tsx
useEffect(() => {
  const prefill = searchParams.get("content");
  if (prefill) setPostContent(decodeURIComponent(prefill));
}, [searchParams]);
```

`decodeURIComponent` reverses the encoding, restoring the original text.

### Why This Works Well

- **No coupling**: The AI features do not import anything from the scheduler. The scheduler does not import anything from the AI features.
- **Bookmarkable**: Users could bookmark `/posts/new?content=Hello` and return to a pre-filled form.
- **Shareable**: A teammate could send a link with pre-filled content.
- **No cleanup needed**: When the user edits the content and schedules the post, the URL param is irrelevant. When they navigate away, the state is garbage collected naturally.
- **Works with Next.js navigation**: `router.push()` updates the URL client-side without a full page reload.

### The Suspense Requirement

This is why `useSearchParams()` requires Suspense. The Next.js page at `app/(app)/posts/new/page.tsx`:

```typescript
import { Suspense } from "react";
import CreatePostPage from "@/features/posts/pages/create-post.page";
import { Skeleton } from "@/components/ui/skeleton";

export default function CreatePost() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full rounded-lg" />}>
      <CreatePostPage />
    </Suspense>
  );
}
```

During SSR (server-side rendering), the server does not know the URL params the client will have. Next.js throws if `useSearchParams()` is called in a component not wrapped in `<Suspense>`. The Suspense boundary tells Next.js: "Render the fallback skeleton on the server. When the client hydrates and knows the actual URL, render the real component."

---


