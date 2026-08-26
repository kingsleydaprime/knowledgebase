# SocioBoom Frontend — Foundations: TypeScript, React & JSX

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
`learning/frontend/frameworks/nextjs-app-router.md` (the framework these fundamentals sit inside),
`learning/frontend/03-styling-and-ui.md` (how these components get styled), and
`learning/backend/01-foundations.md` (the TypeScript notes that overlap on the server side).

This file covers: the mental model of what a frontend actually does and where the boundary with the
backend sits, TypeScript fundamentals as they apply to React (props typing, generics, unions,
`Record<>`), React fundamentals — components, props, state, effects, the rules of hooks, and
re-render behavior — and what JSX really compiles down to.

---

## 1. Mental Model: What is the Frontend Doing?

SocioBoom is a social media scheduling SaaS. The frontend is a **Next.js application** that lets users:

- Create and schedule posts to multiple social platforms at once
- View analytics, a calendar of posts, team settings
- Use AI to turn customer reviews into social posts (Review Poster)
- Use AI to find pain points on Reddit/Twitter and respond to them (Pain-Point Discovery)

Think of the frontend as three distinct zones rendered by three distinct URL groups:

| Zone | URLs | Purpose |
|---|---|---|
| Marketing | `/`, `/features`, `/pricing`, `/faq`, etc. | Public landing pages for non-logged-in visitors |
| Auth | `/login`, `/register`, `/verify-email` | Authentication flows |
| App | `/dashboard`, `/posts/new`, `/settings`, `/reviews`, `/discovery`, etc. | The actual product, for logged-in users |

Every zone has its own layout, which means different wrapping UI (the app zone has a sidebar + navbar; the marketing zone has a marketing navbar; the auth zone has no nav at all).

---

## 2. TypeScript Fundamentals

The project uses TypeScript 5 with `"strict": true`. You cannot escape TypeScript here. Here is what you need to know.

### Types and Interfaces

TypeScript lets you describe the shape of data. An interface describes an object:

```typescript
interface Review {
  reviewerName?: string;   // optional (can be undefined)
  reviewText: string;      // required
  rating?: number;
  source: "google" | "yelp" | "manual";  // union type: only these three strings
  businessName?: string;
}
```

The `?` suffix means a property can be absent. Without it the property is required and TypeScript will error if you forget it.

### Generics

Generics let you write code that works for any type while preserving type information:

```typescript
// useState<string[]> means: state is an array of strings
const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);

// useState<Date | undefined> means: state is either a Date or undefined
const [postDate, setPostDate] = useState<Date>();
```

Without the generic, TypeScript would infer the type from the initial value. `useState([])` would infer `never[]` which is almost never what you want.

### React.FC and Props

Every component accepts typed props:

```typescript
interface PlatformSelectorProps {
  selectedPlatforms: string[];
  onPlatformToggle: (platform: string) => void;  // a function that receives a string
}

const PlatformSelector = ({
  selectedPlatforms,
  onPlatformToggle,
}: PlatformSelectorProps) => {
  // ...
};
```

The `(platform: string) => void` syntax means "a function that takes one string argument and returns nothing."

### Type Assertions and Non-null

When TypeScript cannot prove something is not null, you use `!`:

```typescript
// TypeScript knows .generatedResponse might be undefined
// The ! tells TS "trust me, it exists at this point"
navigator.clipboard.writeText(painPoint.generatedResponse!);
```

Use this sparingly. It is a promise to TypeScript that you have checked the value is not null elsewhere.

### Record Type

`Record<KeyType, ValueType>` is a typed dictionary:

```typescript
const platformColors: Record<string, string> = {
  reddit: "bg-orange-500",
  twitter: "bg-sky-500",
};
```

This says: an object whose keys are strings and whose values are strings.

---

## 3. React Fundamentals

React is a library for building user interfaces. The core idea is simple: **your UI is a function of your state**.

```
UI = f(state)
```

When state changes, React re-runs the function (your component) and figures out what changed in the output, then updates only those parts of the real DOM. This is called reconciliation.

### Components

A component is a JavaScript function that returns JSX (covered in the next section). Here is the simplest possible component:

```typescript
function Hello() {
  return <h1>Hello, World</h1>;
}
```

Components can be composed — you use one component inside another:

```typescript
function App() {
  return (
    <div>
      <Hello />
      <Hello />
    </div>
  );
}
```

### State: `useState`

State is data that belongs to a component and can change over time. When it changes, React re-renders the component.

```typescript
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);  // initial value is 0

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}
```

`useState` returns a pair: the current value, and a function to update it. Always use the setter function — never mutate state directly (`count = count + 1` will not cause a re-render).

### Effects: `useEffect`

Effects let you run code in response to renders or state changes — things like fetching data, subscribing to events, or reading from localStorage.

```typescript
useEffect(() => {
  const prefill = searchParams.get("content");
  if (prefill) setPostContent(decodeURIComponent(prefill));
}, [searchParams]);  // runs when searchParams changes
```

The second argument is the **dependency array**. The effect runs:
- Once on mount if the array is `[]`
- Every render if you omit the array entirely (almost never what you want)
- Whenever any value in the array changes

### Props

Props are how components communicate. A parent passes data to a child via props:

```typescript
// Parent passes the values
<OverviewCard
  title="Total Engagement"
  value="28.4k"
  icon={<Activity className="h-4 w-4" />}
  trend={{ value: 12, positive: true }}
/>

// Child receives them as a typed object
const OverviewCard = ({ title, value, icon, trend }: OverviewCardProps) => {
  return (
    <Card>
      <CardTitle>{title}</CardTitle>
      {/* ... */}
    </Card>
  );
};
```

Props flow down. For data to go up (child to parent), you pass a function as a prop:

```typescript
// Parent defines the function and passes it down
<PlatformSelector
  selectedPlatforms={selectedPlatforms}
  onPlatformToggle={handlePlatformToggle}  // function prop
/>

// Child calls it when the user interacts
onClick={() => onPlatformToggle(platform)}
```

### Custom Hooks

A custom hook is just a function whose name starts with `use` and that calls other hooks. It is a way to extract reusable stateful logic:

```typescript
// src/shared/hooks/use-mobile.tsx
export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined);

  React.useEffect(() => {
    const mql = window.matchMedia(`(max-width: 767px)`);
    const onChange = () => setIsMobile(window.innerWidth < 768);
    mql.addEventListener("change", onChange);
    setIsMobile(window.innerWidth < 768);
    return () => mql.removeEventListener("change", onChange);
  }, []);

  return !!isMobile;
}
```

Usage anywhere in the app:

```typescript
const isMobile = useIsMobile();
if (isMobile) { /* render mobile layout */ }
```

---

## 4. JSX: What You're Actually Writing

JSX is not HTML. It is a syntax extension that compiles to `React.createElement(...)` calls. Here are the key differences to remember:

| HTML | JSX | Reason |
|---|---|---|
| `class="foo"` | `className="foo"` | `class` is a reserved JS keyword |
| `for="id"` | `htmlFor="id"` | `for` is a reserved JS keyword |
| `<br>` | `<br />` | JSX requires all tags to be self-closed |
| Inline styles as string | Inline styles as object | `style={{ color: "red" }}` |
| Event: `onclick` | Event: `onClick` | camelCase in JSX |

### Expressions in JSX

Curly braces `{}` let you embed any JavaScript expression inside JSX:

```typescript
// Displaying a value
<div>{count}</div>

// Calling a function
<div>{formatDate(postDate)}</div>

// Conditional rendering
{trend && <span>{trend.value}%</span>}

// Ternary
{isLoading ? <Spinner /> : <Content />}

// Mapping arrays to JSX
{platforms.map((platform) => (
  <div key={platform}>{platform}</div>
))}
```

The `key` prop on mapped elements is required — it tells React how to identify each element when the list changes. Use a stable unique identifier, never the array index if the list can be reordered.

### Fragments

Components must return a single root element. Wrap siblings in a Fragment when you do not want a real DOM node:

```typescript
// Long form
return (
  <React.Fragment>
    <Header />
    <Main />
  </React.Fragment>
);

// Short form (same thing)
return (
  <>
    <Header />
    <Main />
  </>
);
```

---


