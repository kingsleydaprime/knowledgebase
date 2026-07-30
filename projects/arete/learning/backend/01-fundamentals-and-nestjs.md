# Arete Backend — Fundamentals & NestJS Basics

Split out from the original single-file `backend-learning.md` (NestJS 11 + Prisma + PostgreSQL +
Redis + BullMQ). See also `02-prisma-and-data-modeling.md`, `03-patterns-worth-stealing.md`,
`04-auth.md`, `05-product-logic-case-studies.md`, `06-advanced-habits-and-bug-postmortems.md`,
and `07-study-path.md`.

---

# Backend Engineering — Beginner to Advanced
### Everything used in the Arete backend (NestJS 11 + Prisma + PostgreSQL + Redis + BullMQ), and why

---

---

## Part 1 — Absolute Beginner

### What a backend actually does

The mobile app is a face. The backend is the brain and the vault:
- **Owns the truth** (database) — the app only holds copies.
- **Enforces rules** — the app can be decompiled and faked; the server cannot. That's why Arete's "5-minute minimum before completing a quest" lives in `quests.service.ts`, not in the app.
- **Does work while nobody's watching** — cron jobs generate quests at midnight and evaluate streaks at 23:59.

### HTTP in five lines

```
GET    /quests/today          → read (no side effects, safe to repeat)
POST   /quests/optional/start → create
PATCH  /quests/:id/complete   → partial update
DELETE /users/me              → remove
Status: 200 ok · 201 created · 400 your fault · 401 not logged in · 404 missing · 500 my fault
```

Requests and responses carry JSON. The client sends `Authorization: Bearer <token>` to prove identity.

### The Arete stack at a glance

| Piece | Role |
|---|---|
| **NestJS** | HTTP framework — routing, validation, dependency injection |
| **Prisma** | ORM — typed database access + migrations |
| **PostgreSQL** | The database — the single source of truth |
| **Redis** | Fast in-memory store — caching + BullMQ's backbone |
| **BullMQ** | Job queues — cron jobs and background work |
| **bun** | JS runtime & package manager (faster npm/node) |

---

## Part 2 — NestJS: the shape of everything

NestJS organizes code into **modules**, each containing **controllers** (HTTP in/out) and **services** (business logic). Arete: `auth`, `quests`, `tasks`, `progression`, `pillars`, `messages`, `notifications`, `onboarding`, `jobs`, `redis`, `prisma`, `users`, `email`.

### Controller → Service → Database

```ts
// quests.controller.ts — thin. Parses HTTP, delegates, returns.
@Controller('quests')
@UseGuards(JwtAuthGuard)                       // every route requires a valid JWT
export class QuestsController {
  constructor(private quests: QuestsService) {} // ← dependency injection

  @Get('today')
  getToday(@Request() req: any) {
    return this.quests.getTodayQuests(req.user.id);
  }

  @Patch(':id/complete')
  complete(@Request() req: any, @Param('id') id: string) {
    return this.quests.completeQuest(req.user.id, id);
  }
}
```

```ts
// quests.service.ts — fat. All the rules live here.
@Injectable()
export class QuestsService {
  constructor(
    private prisma: PrismaService,      // injected automatically
    private xpService: XpService,
    private notifications: NotificationService,
  ) {}
  // ...
}
```

**Dependency injection (DI)** means you never write `new QuestsService(...)`. Nest builds the object graph from constructor signatures. Why care: services are swappable in tests, and wiring is declared, not hand-assembled. A service must be listed in its module's `providers`, and `exports` if other modules need it — forgetting this is the classic Nest error ("Nest can't resolve dependencies of...").

### Guards, DTOs, validation

```ts
// A guard runs before the handler. JwtAuthGuard verifies the token
// and attaches the user to the request.
@UseGuards(JwtAuthGuard)

// A DTO declares and validates input shape:
export class CompleteOnboardingDto {
  @IsString() timezone: string;
  @IsOptional() @IsString() faithBackground?: string;
  @IsOptional() @IsString() equipmentAccess?: string;
}
```

Rule: **never trust the client**. Validate at the edge (DTOs), enforce in the service.

---

