# NextVibe Frontend — Forms, UI Layer & Assets

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`).
See also `learning/frontend/01-routing.md`, `learning/frontend/02-state-management.md`,
`learning/frontend/05-uploads-errors.md` (file inputs feed into the presigned-upload flow covered
there), and `learning/frontend/07-payments-games.md` (the wizard forms that build on these
patterns).

This file covers: `react-hook-form` + `zod` for forms (including the shadcn/ui `Form` component
wiring and useful zod schema patterns), the shadcn/ui + Tailwind UI layer (what shadcn/ui actually
is, the `cn()` utility, Tailwind v4's CSS-based configuration), and fonts/images/scripts via
`next/font`, `next/image`, and `next/script`.

---

## 14. Forms — react-hook-form + zod

### Why react-hook-form?

The native `<form>` with `useState` for every field is verbose and re-renders on every keystroke. `react-hook-form` uses uncontrolled inputs internally — it only re-renders when validation state changes.

### Basic setup

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email({ message: "Invalid email" }),
  password: z.string().min(8, { message: "At least 8 characters" }),
});

type FormValues = z.infer<typeof schema>;  // ← derive type from schema

function LoginForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (values: FormValues) => {
    // values is fully typed and validated
    await login(values);
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input {...form.register("email")} />
      {form.formState.errors.email && (
        <p>{form.formState.errors.email.message}</p>
      )}
      <button type="submit">Login</button>
    </form>
  );
}
```

### With shadcn/ui Form components

shadcn provides `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage` that wire into react-hook-form automatically:

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <FormField
      control={form.control}
      name="email"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <Input {...field} />
          </FormControl>
          <FormMessage />  {/* auto-shows validation error */}
        </FormItem>
      )}
    />
  </form>
</Form>
```

### Zod schema tips

```ts
// Optional fields
z.string().optional()

// With transformation
z.string().trim().toLowerCase().email()

// Nested objects
z.object({
  address: z.object({
    city: z.string(),
    country: z.string(),
  }),
})

// Arrays
z.array(z.object({ tierId: z.string(), quantity: z.number().int().min(1) }))

// Conditional validation
z.object({
  hasTickets: z.boolean(),
  ticketPrice: z.number().optional(),
}).refine(
  (data) => !data.hasTickets || data.ticketPrice !== undefined,
  { message: "Price required when selling tickets", path: ["ticketPrice"] }
)
```

(See `learning/frontend/05-uploads-errors.md` Part 31 for a real-world example of chaining two `.refine()` calls on a `z.instanceof(File)` field — one for file type, one for file size — so each failure mode gets its own distinct error message.)

---

## 15. UI Layer — shadcn/ui + Tailwind

### What shadcn/ui is (and is not)

shadcn/ui is **not** an npm package. It's a collection of copy-paste components built on Radix UI primitives and styled with Tailwind. When you run `npx shadcn add button`, it copies `src/components/ui/button.tsx` into your project.

This means:
- You own the component — edit it however you like
- No version lock-in
- The component is Radix UI under the hood (fully accessible, keyboard-navigable)

### `cn()` — the utility you'll use everywhere

```ts
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

`clsx` handles conditionals. `twMerge` resolves Tailwind conflicts (e.g. `"p-4 p-2"` → `"p-2"`).

```tsx
<div className={cn(
  "rounded-xl border p-3",                    // always
  selected && "border-primary bg-primary/5",  // conditional
  className                                   // override from props
)} />
```

### Tailwind v4 (used in this project)

Tailwind v4 is configured via CSS, not `tailwind.config.js`:

```css
/* globals.css */
@import "tailwindcss";
@import "tw-animate-css";
```

Custom variables are defined in `@layer base` as CSS custom properties and referenced as Tailwind utilities.

### Component patterns from this project

**Skeleton loading:**
```tsx
if (isLoading) return <Skeleton className="h-16 w-full rounded-xl" />;
```

**Conditional badge:**
```tsx
<Badge className={cn(
  "text-xs",
  status === "PUBLISHED" ? "bg-green-500/10 text-green-600" : "bg-amber-500/10 text-amber-600"
)}>
  {status}
</Badge>
```

**Toast notifications** (via sonner):
```tsx
import { toast } from "sonner";

toast.success("Event published!");
toast.error("Payment failed. Try again.");
```

(See `learning/frontend/05-uploads-errors.md` for the universal `errorHandler()` function whose output is almost always passed straight into `toast.error(...)`.)

---

## 16. Fonts, Images, and Scripts

### Fonts — `next/font`

```ts
// src/app/layout.tsx
import { Nunito_Sans } from "next/font/google";

const nunitoSans = Nunito_Sans({
  weight: ["400", "600", "700"],
  variable: "--font-nunito-sans",
  subsets: ["latin"],
});
```

`next/font` downloads the font at build time and self-hosts it. No request to Google Fonts at runtime = better privacy and performance. The `variable` option creates a CSS custom property, used as `font-[--font-nunito-sans]` in Tailwind.

### Images — `next/image`

```tsx
import Image from "next/image";

<Image
  src="https://res.cloudinary.com/..."
  alt="Event banner"
  width={800}
  height={400}
  className="rounded-xl object-cover"
/>
```

`next/image` automatically:
- Lazy-loads (off-screen images don't load until near the viewport)
- Resizes to the needed dimensions
- Converts to WebP
- Prevents Cumulative Layout Shift (CLS) via `width`/`height`

External domains must be whitelisted in `next.config.ts`:

```ts
images: {
  remotePatterns: [{ protocol: "https", hostname: "res.cloudinary.com" }],
}
```

> This project has `unoptimized: true` — skipping image optimisation for faster builds. Remove this in production for real performance gains. (See `learning/frontend/08-performance-debugging.md` for the rest of this project's performance trade-offs, including why this flag is on the list.)

### Scripts — `next/script`

```tsx
import Script from "next/script";

// Load before any page rendering (blocks)
<Script src="https://..." strategy="beforeInteractive" />

// Load after page is interactive (default, good for analytics)
<Script src="https://..." strategy="afterInteractive" />

// Load during browser idle time
<Script src="https://..." strategy="lazyOnload" />
```

This project loads Google Maps and the old Juicyway script as `beforeInteractive` because they need to be available immediately. Analytics (Google Tag Manager) is `afterInteractive`.
