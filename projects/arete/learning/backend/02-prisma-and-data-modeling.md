# Arete Backend — Prisma & Data Modeling

Split out from the original single-file `backend-learning.md`. See also
`01-fundamentals-and-nestjs.md`.

---

## Part 3 — Prisma & Data Modeling

### The schema is the contract

```prisma
model DailyQuest {
  id        String  @id @default(uuid())
  userId    String
  taskId    String
  variantId String?

  questDate   DateTime @db.Date
  isCompleted Boolean  @default(false)
  xpEarned    Int      @default(0)

  user    User         @relation(fields: [userId], references: [id], onDelete: Cascade)
  task    Task         @relation(fields: [taskId], references: [id])
  variant TaskVariant? @relation(fields: [variantId], references: [id])

  @@unique([userId, taskId, questDate])   // ← THE key design decision
  @@map("daily_quests")
}
```

Design decisions to study in this one model:

1. **`@@unique([userId, taskId, questDate])`** — the database itself guarantees "one quest per user per task per day". Application code *tries* to prevent duplicates; constraints *guarantee* it. This is what makes `upsert` possible.
2. **`onDelete: Cascade`** on user — delete a user, their quests vanish. But tasks have *no* cascade — you must not delete a task that history references.
3. **`@db.Date`** vs `DateTime` — quest dates are calendar days, not instants. (Gotcha: Prisma returns them as UTC midnight — compare them as dates, never as local times.)
4. **`variantId String?`** — nullable, because old rows predate the feature. New columns on live tables must be nullable or defaulted, or your migration breaks existing rows.

### Migrations — how schema changes ship

```bash
# development: edit schema.prisma, then
bunx prisma migrate dev --name add_task_variants   # generates SQL + applies + regenerates client

# production: apply already-generated migrations, never generate there
bunx prisma migrate deploy

# after any schema change:
bunx prisma generate                                # regenerate the typed client
```

Migrations are numbered SQL files in `prisma/migrations/` and are **append-only history** — never edit an applied one; write a new migration to fix a mistake. (For the variants migration we generated the SQL offline with `prisma migrate diff` — see devops notes.)

### The queries you'll use daily

```ts
// upsert = insert-or-do-nothing/update. Idempotent by construction.
await prisma.dailyQuest.upsert({
  where: { userId_taskId_questDate: { userId, taskId, questDate } }, // compound unique key
  create: { userId, taskId, pillarId, questDate, variantId },
  update: {},                                   // exists already? touch nothing
});

// include = join related rows in one query (avoids N+1):
const quests = await prisma.dailyQuest.findMany({
  where: { userId, questDate: today },
  include: { task: true, pillar: true, variant: true },
});

// aggregate without loading rows:
const stillOpen = await prisma.dailyQuest.count({
  where: { userId, questDate, isOptional: false, isCompleted: false },
});
```

**N+1 warning:** a loop that queries per item (`for (task of tasks) await prisma.taskVariant.findMany({where:{taskId: task.id}})`) fires N queries. Batch instead — one `findMany({ where: { taskId: { in: ids } } })` then group in memory (see `getVariantsByTask` in quests.service.ts).

### Transactions — all or nothing

```ts
// Array form: independent writes that must succeed together
await this.prisma.$transaction([
  prisma.dailyQuest.update({ ... }),          // mark complete
  prisma.xpTransaction.create({ ... }),       // ledger entry
  prisma.userPillar.update({ ... }),          // pillar XP
  prisma.user.update({ ... }),                // total XP + gems
]);

// Interactive form: when a later step depends on an earlier result
await this.prisma.$transaction(async (tx) => {
  const result = await tx.user.updateMany({
    where: { id: userId, gems: { gte: SHIELD_COST } },  // guard inside the txn
    data: { gems: { decrement: SHIELD_COST } },
  });
  if (result.count === 0) throw new BadRequestException('Not enough gems');
  await tx.streakEvent.create({ ... });
});
```

If completing a quest wrote XP but crashed before writing gems, the user's economy silently corrupts. Transactions make partial writes impossible.

---

