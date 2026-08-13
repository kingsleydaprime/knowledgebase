# SocioBoom Frontend — TailwindCSS v4, shadcn/ui & Dark Mode

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
`learning/frontend/01-foundations.md` (the components being styled),
`learning/frontend/04-architecture.md` (the sidebar and navigation these styles drive), and
`learning/frontend/06-feature-walkthroughs.md` (these primitives assembled into real screens).

This file covers: TailwindCSS v4 concepts and what changed from v3, the utility-first mental model,
what shadcn/ui actually is (copied source, not a dependency) and why that trade-off was chosen, the
`cn()` helper and `clsx`/`tailwind-merge`, the CSS-variable theming system, and building dark mode
with a custom theme toggle.

---

## 6. TailwindCSS v4 Concepts

Tailwind is a utility-first CSS framework. Instead of writing custom CSS, you compose small single-purpose classes directly in your JSX.

### The Utility-First Philosophy

Traditional CSS:

```css
.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  background-color: white;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

Tailwind equivalent:

```typescript
<div className="p-6 rounded-lg bg-white border border-slate-200 shadow-sm">
```

The classes encode the CSS properties directly. You read the JSX and immediately see the styles.

### TailwindCSS v4 Differences from v3

SocioBoom uses Tailwind v4, which has meaningful differences from v3:

**No `tailwind.config.js`**: Configuration moved entirely into the CSS file. Design tokens are defined using CSS custom properties inside `@theme {}`:

```css
/* src/app/globals.css */
@import "tailwindcss";
@plugin "tailwindcss-animate";

@theme {
  --font-family-sans: "Inter", sans-serif;
  --font-family-heading: "Poppins", sans-serif;
  --breakpoint-2xl: 1400px;
  --color-brand-purple: var(--brand-purple);
  /* All design tokens live here */
}
```

**CSS Variables for colors**: Colors are defined as HSL CSS variables in `:root` and `.dark`, then wired into Tailwind's color system via `@theme`:

```css
:root {
  --primary: 252 100% 69%;   /* HSL values without hsl() wrapper */
}

@theme {
  --color-primary: hsl(var(--primary));  /* Tailwind now generates bg-primary, text-primary, etc. */
}
```

This is why changing `--primary` in CSS immediately updates every `bg-primary`, `text-primary`, `ring-primary` utility across the app — and switching to dark mode just redefines those variables.

**`@layer` still works**: You can still define components and base styles in layers:

```css
@layer base {
  body {
    @apply bg-background text-foreground font-sans;
  }
}

@layer components {
  .card-hover {
    @apply transition-all duration-200 hover:shadow-md hover:-translate-y-1;
  }
}
```

### Common Utility Patterns Used in SocioBoom

**Layout:**
```
flex items-center justify-between  → horizontal centering with space-between
grid grid-cols-1 md:grid-cols-3   → 1 column on mobile, 3 on medium screens
gap-4                              → gap between grid/flex children
space-y-6                         → vertical spacing between children
min-h-screen                      → at least full viewport height
```

**Sizing:**
```
h-4 w-4    → 1rem × 1rem (16px)
h-8 w-8    → 2rem × 2rem (32px)
max-w-4xl  → max-width: 56rem
w-full     → width: 100%
```

**Responsive prefixes:**
```
md:p-6     → applies p-6 on medium screens (≥768px) and up
lg:col-span-2  → applies col-span-2 on large screens (≥1024px) and up
hidden md:block  → hidden on mobile, block on md+
```

**Semantic color utilities (from CSS variables):**
```
bg-background       → var(--background), changes with dark mode
text-foreground     → var(--foreground)
text-muted-foreground  → dimmed text
bg-primary          → brand purple
bg-card             → card background
border-border       → standard border color
```

**Tailwind Merge and clsx:**

When combining conditional classes, naive string concatenation fails:

```typescript
// WRONG: both classes applied even when isActive is false
className={"flex " + (isActive ? "bg-accent" : "")}
```

SocioBoom uses the `cn()` utility from `src/shared/lib/utils.ts`:

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

`clsx` handles conditional class logic (arrays, objects, booleans). `twMerge` resolves Tailwind conflicts — if you pass `p-4` and `p-6`, twMerge keeps only `p-6` instead of generating two conflicting padding declarations.

Usage:

```typescript
className={cn(
  "flex items-center gap-3 w-full",        // always applied
  isActive === item.path && "bg-accent text-accent-foreground",  // conditional
)}
```

---

## 7. shadcn/ui: What It Is and Why We Use It

### What shadcn/ui Actually Is

shadcn/ui is **not a component library you install as a package**. It is a collection of component source code that you copy into your project. When you run `npx shadcn-ui@latest add button`, it copies `button.tsx` into your project (in SocioBoom's case, `src/shared/components/ui/`).

You own the code. You can read it, modify it, understand exactly what it does. There is no black box.

### Why Not Raw Radix UI?

Radix UI provides fully accessible, unstyled primitives — keyboard navigation, focus management, ARIA attributes all handled correctly. The trade-off is they ship with zero styles, so they are invisible by default.

shadcn/ui layers Tailwind CSS onto Radix UI primitives, giving you accessible + styled components:

```typescript
// src/shared/components/ui/tabs.tsx
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

function TabsList({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      className={cn(
        "bg-muted text-muted-foreground inline-flex h-9 items-center justify-center rounded-lg p-[3px]",
        className  // caller can override or extend
      )}
      {...props}
    />
  );
}
```

The Radix primitive handles all the accessibility (keyboard navigation, ARIA roles, focus trapping). The Tailwind classes handle appearance. `cn(baseClasses, className)` allows callers to extend or override.

### The `cva` Pattern (Class Variance Authority)

Components with multiple visual variants use `cva()` to manage the class combinations cleanly:

```typescript
// src/shared/components/ui/button.tsx
const buttonVariants = cva(
  // Base classes applied to every button
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
        destructive: "bg-destructive text-white shadow-xs hover:bg-destructive/90",
        outline: "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md gap-1.5 px-3",
        lg: "h-10 rounded-md px-6",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);
```

Usage is type-safe:

```typescript
<Button variant="outline" size="sm">Cancel</Button>
<Button variant="destructive">Delete</Button>
<Button>Submit</Button>  // uses defaultVariants: default, default
```

TypeScript will error if you pass a variant that doesn't exist.

### The `asChild` Prop

Several shadcn/ui components support `asChild`. This uses Radix's `Slot` component to forward all props and behavior to the child element instead of rendering a default element:

```typescript
// Without asChild: renders a <button> wrapping a <Link>
<Button>
  <Link href="/posts/new">Create Post</Link>
</Button>

// With asChild: the Button's styles apply to the Link directly (single element)
<Button asChild>
  <Link href="/posts/new">Create Post</Link>
</Button>
```

`asChild` is commonly used when you want a `Link` to look like a `Button`, or a `label` to work like a `Button`. SocioBoom uses it extensively in the sidebar and navbar.

### How to Add New shadcn/ui Components

```bash
cd frontend
npx shadcn-ui@latest add <component-name>
```

This copies the component source into `src/shared/components/ui/`. You then import it with `@/components/ui/<name>`.

Currently available in the project (in `src/shared/components/ui/`):
`accordion`, `alert`, `avatar`, `badge`, `button`, `calendar`, `card`, `checkbox`, `dialog`, `dropdown-menu`, `input`, `label`, `navigation-menu`, `popover`, `select`, `separator`, `sheet`, `sidebar`, `skeleton`, `sonner`, `switch`, `tabs`, `textarea`, `toast`, `tooltip`

### Real Usage Examples from the Codebase

**Card with header, content, footer:**
```typescript
<Card>
  <CardHeader>
    <CardTitle>Post Content</CardTitle>
    <CardDescription>Create and preview your post</CardDescription>
  </CardHeader>
  <CardContent>
    {/* content goes here */}
  </CardContent>
  <CardFooter>
    <Button variant="outline">Save as Draft</Button>
    <Button>Schedule Post</Button>
  </CardFooter>
</Card>
```

**Tabs:**
```typescript
<Tabs value={tabValue} onValueChange={setTabValue}>
  <TabsList className="grid w-full grid-cols-2">
    <TabsTrigger value="compose">Compose</TabsTrigger>
    <TabsTrigger value="preview">Preview</TabsTrigger>
  </TabsList>
  <TabsContent value="compose" className="pt-4">
    {/* compose panel */}
  </TabsContent>
  <TabsContent value="preview" className="pt-4">
    {/* preview panel */}
  </TabsContent>
</Tabs>
```

Note that `value` + `onValueChange` makes it a **controlled** component — the parent holds the active tab in state. You can also use `defaultValue` for an uncontrolled component where you don't need to know which tab is active from the parent.

**Badge:**
```typescript
<Badge variant="secondary">{selectedReviews.length} selected</Badge>
<Badge variant="outline">Draft</Badge>
<Badge variant="destructive">Error</Badge>
<Badge>Default (primary)</Badge>
```

**Input with icon:**
```typescript
<div className="relative">
  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
  <Input
    type="search"
    placeholder="Search..."
    className="pl-8"  // padding-left to make room for the icon
  />
</div>
```

**Popover (used for date picker):**
```typescript
<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline" className={cn(!postDate && "text-muted-foreground")}>
      <CalendarIcon className="mr-2 h-4 w-4" />
      {postDate ? format(postDate, "PPP") : "Select date"}
    </Button>
  </PopoverTrigger>
  <PopoverContent className="w-auto p-0">
    <Calendar
      mode="single"
      selected={postDate}
      onSelect={setPostDate}
      disabled={(date) => date < new Date()}
    />
  </PopoverContent>
</Popover>
```

---


## 12. Dark Mode with Custom Theme Toggle

SocioBoom implements dark mode without next-themes (despite it being in `package.json`). Instead it uses a custom implementation in `src/shared/components/theme/ModeToggle.tsx`.

### How It Works

The mechanism:
1. CSS variables in `globals.css` define two sets of values: `:root` (light) and `.dark` (dark)
2. Adding or removing the `dark` class on `<html>` switches between them
3. The `ModeToggle` component manages this class and persists the choice in `localStorage`

```typescript
const setMode = (newTheme: "light" | "dark" | "system") => {
  localStorage.setItem("theme", newTheme);
  setTheme(newTheme);

  if (
    newTheme === "dark" ||
    (newTheme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches)
  ) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
};
```

On mount, it reads the stored preference and applies it:

```typescript
useEffect(() => {
  const storedTheme = localStorage.getItem("theme") as "light" | "dark" | "system" | null;
  const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const initialTheme = storedTheme || (systemPrefersDark ? "dark" : "light");
  
  setTheme(initialTheme as "light" | "dark" | "system");
  
  if (initialTheme === "dark" || (initialTheme === "system" && systemPrefersDark)) {
    document.documentElement.classList.add("dark");
  }
}, []);
```

### The CSS Dark Mode Variant

In `globals.css`, Tailwind's dark variant is configured:

```css
@custom-variant dark (&:is(.dark *));
```

This means the `dark:` prefix in Tailwind classes activates when the element is inside a `.dark` element. Since we add/remove `dark` on `<html>`, every element on the page is affected:

```typescript
// These classes change with dark mode automatically
<div className="bg-white dark:bg-gray-900">
<p className="text-gray-900 dark:text-gray-100">

// For semantic color utilities, dark mode is already handled by CSS variables:
<div className="bg-background">  // automatically light or dark
```

### Why the ModeToggle Has Two Icons

```typescript
<Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
<Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
```

Both icons are always in the DOM. In light mode: Sun is visible (`scale-100`), Moon is hidden (`scale-0`). In dark mode: Sun shrinks and rotates away, Moon grows and rotates in. The `absolute` positioning on Moon makes them overlay each other. This is an animated icon swap — pure CSS, zero JavaScript.

---


