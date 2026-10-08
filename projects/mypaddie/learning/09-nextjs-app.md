# 09 — The Next.js app: server components, actions and small client islands

*MyPaddie (written up 2026-10-08). Next.js 16, React 19. Files: `src/app/(app)/app/*`,
`src/features/*/ui/*`, `src/features/*/*.actions.ts`, `src/shared/ui/*`, `src/proxy.ts`.*
See also: [[05-mcp-server]] (the other client of the same repos) · [[08-data-modelling-choices]]

## Feature folders, thin routes

```
src/app/(app)/app/tasks/page.tsx        ← 5 lines: auth, then render the feature's screen
src/features/tasks/ui/tasks-screen.tsx  ← the screen (a server component)
src/features/tasks/overview.ts          ← pure logic (tested)
src/features/tasks/overview.repo.ts     ← database reads
src/features/tasks/tasks.actions.ts     ← server actions (writes from forms/buttons)
src/features/tasks/tasks.tools.ts       ← MCP tools (writes from Paddie)
```

A route file only does auth and render:

```tsx
export default async function TasksPage() {
  return <TasksScreen db={await requireDb("/app/tasks")} />;
}
```

So moving a screen to a different URL (the Quests → Life list rework) touches
the route and the links, not the logic. **Route groups** `(app)`, `(auth)` and
`(marketing)` share layouts without appearing in the URL. Next 16 renamed
`middleware.ts` to **`proxy.ts`**, which is worth knowing when following older
tutorials.

## Server components do the reading

Screens are `async` server components that query directly:

```tsx
export async function TasksScreen({ db }: { db: Db }) {
  const [around, overview, schedule] = await Promise.all([loadTasksAroundToday(db, now), loadTaskOverview(db, now), loadSchedule(db)]);
  …
}
```

- No API layer and no client fetch: the component *is* the server.
- **`Promise.all`** for independent reads. Sequential awaits add up the network
  round trips.
- `requireDb()` checks the session (`auth.getClaims`) and redirects to login,
  then sets up the per-user context (time zone, plan) before any query runs.

## Server actions do the writing

```ts
"use server";
export async function startTaskAction(id: string, pause: boolean): Promise<TaskFormState> {
  const db = await requireDb(`/app/tasks/${id}`);
  const r = await startTask(db, id, new Date(), pause);
  revalidatePath(`/app/tasks/${id}`);
  if (r.result === "busy") return { error: `“${r.running.title}” is in progress. One at a time: pause or finish it first.` };
  return { ok: "Started." };
}
```

- A `"use server"` function can be imported straight into a client component or
  passed to `<form action>`. Next turns it into a POST endpoint.
- **Re-check auth inside every action.** It's a public endpoint, whatever page
  rendered the button.
- **`revalidatePath`** tells Next the page's server data is stale, so the next
  render re-queries.
- **Return refusals as data** (`{ error }`), not thrown errors, so the UI can show
  *why* ("is in progress…"). This is the same idea as the MCP result shapes.
- Two ways to wire one:
  - `form action={fn.bind(null, id)}` with a `SubmitButton` that uses
    `useFormStatus` for its spinner. No client code of your own.
  - A client component calling the action inside `useTransition` (below).

## Client components only where there's interaction

Most of the UI is server-rendered. Small `"use client"` islands handle the
interactive bits:

```tsx
"use client";
export function TaskButtons({ taskId, title, running, spentMinutes }) {
  const router = useRouter();
  const [pending, run] = useTransition();
  const [error, setError] = useState<string | null>(null);
  const label = running ? "Pause" : spentMinutes > 0 ? "Resume" : "Start";
  const toggle = () => run(async () => {
    const r = await startTaskAction(taskId, running);
    setError(r && "error" in r ? r.error : null);
    router.refresh();             // re-run the server components with fresh data
  });
  …
}
```

- **`useTransition`** gives a `pending` flag while the action runs (disable the
  button, show "…").
- **`router.refresh()`** re-renders the server tree without a full reload, so
  the list re-sorts with the task now in progress.
- `DoneButton` waits 900 ms before refreshing, so "+10 XP · took 55m" is seen
  before the item disappears.
- Props are plain data (`running: boolean`, not a `Date` object from the server
  component), so they serialise cleanly across the server/client boundary.

### A form field whose default follows another field

The add-event form's "Self-care" box should follow the chosen kind (a wedding
ticks it) **until the user touches it**:

```tsx
const [kind, setKind] = useState<EventKind>("other");
const [selfCare, setSelfCare] = useState<boolean | null>(null);   // null = "they haven't chosen"
<input type="checkbox" name="self_care" checked={selfCare ?? selfCareByDefault(kind)} onChange={(e) => setSelfCare(e.target.checked)} />
```

`null` means "not chosen yet", which a plain boolean can't express. To reset the
form after a successful add, **bump a `key`** on the inner component, so React
remounts it with fresh state.

## Typed routes

`next typegen` generates `PageProps<"/app/quests">`, so `searchParams` and
`params` are typed from the folder structure. The project's `typecheck` script
runs it before `tsc`, so a new page's types exist before they're checked.

## One shared component per repeated thing

The line under a task's title ("In progress · 25m · 2/5 steps · Engineer · Org")
appears on Today and on the Tasks tab. It's **one** component, `TaskMeta`, and
the "for" label comes from **one** pure function (`forLabelOf`). When the user
asked for the organisation to show next to the role, that was one change in one
place. Before that, two hand-written copies had already started to drift.
**Duplicate UI is fine until it has rules in it. Then extract it.**

## Design tokens, not colours

All colour comes from tokens (`bg-gold`, `text-muted`, `border-line`, `text-red`)
defined once in `globals.css`, with light and dark values. Gold is the only
accent; green and red carry meaning (done/overdue) and are never decoration.
New UI written this way gets dark mode for free.
