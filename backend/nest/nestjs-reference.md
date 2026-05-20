# NestJS Personal Reference

> Written from experience building Nextvibe. Start here on every new project.

---

## Table of Contents

### Foundation
- [01 — Project Setup](#01--project-setup)
- [02 — Prisma Setup (v7+)](#02--prisma-setup-v7)
- [03 — Folder Structure](#03--folder-structure)

### Core Concepts
- [04 — Modules](#04--modules)
- [05 — Controllers](#05--controllers)
- [06 — Services](#06--services)
- [07 — DTOs](#07--dtos)
- [08 — Pipes](#08--pipes)

### Request Pipeline
- [09 — Guards](#09--guards)
- [10 — Interceptors](#10--interceptors)
- [11 — Exception Filters](#11--exception-filters)
- [12 — Decorators](#12--decorators)

### Production
- [13 — Security & CORS](#13--security--cors)
- [14 — API Versioning](#14--api-versioning)
- [15 — Error Handling](#15--error-handling)
- [16 — Performance](#16--performance)
- [17 — Swagger Docs](#17--swagger-docs)
- [18 — TypeScript Tips](#18--typescript-tips)

### Testing
- [19 — Testing Overview](#19--testing-overview)
- [20 — Unit Tests](#20--unit-tests)
- [21 — Integration Tests](#21--integration-tests)
- [22 — End-to-End Tests](#22--end-to-end-tests)

### Senior Concepts
- [23 — DB Design Patterns](#23--db-design-patterns)
- [24 — Common Issues](#24--common-issues)
- [25 — Monorepos](#25--monorepos)
- [26 — Advanced Patterns](#26--advanced-patterns)
- [27 — Scaling & Sharding](#27--scaling--sharding)

---

## 01 — Project Setup

Every new NestJS project follows this exact sequence. Don't skip steps.

### 1. Install CLI and create project

```bash
npm install -g @nestjs/cli
nest new project-name
# pick npm or pnpm — be consistent with your team
cd project-name
```

### 2. Install core dependencies

```bash
# Auth
npm install @nestjs/jwt @nestjs/passport passport passport-jwt
npm install -D @types/passport-jwt

# Config
npm install @nestjs/config

# Validation
npm install class-validator class-transformer

# Database
npm install @prisma/client @prisma/adapter-pg
npm install -D prisma

# Redis + Queues
npm install ioredis @nestjs/bullmq bullmq

# Storage
npm install @aws-sdk/client-s3 @aws-sdk/s3-request-presigner

# Utilities
npm install argon2 uuid
npm install -D @types/uuid
```

### 3. Delete NestJS boilerplate

```bash
rm src/app.controller.ts
rm src/app.service.ts
rm src/app.controller.spec.ts
```

### 4. Set up folder structure

```
src/
  modules/       # feature modules (auth, users, events...)
  shared/        # injectable infrastructure (prisma, redis, storage)
  common/        # NestJS mechanics (guards, interceptors, filters, decorators)
  utils/         # pure functions (no NestJS dependencies)
  config/        # environment config files
  workers/       # BullMQ job processors
```

### 5. Create .env and .env.example

```bash
# .env — your real secrets, NEVER commit this
NODE_ENV=development
PORT=3000
API_PREFIX=v1
DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_ACCESS_SECRET=generate-with-crypto
JWT_REFRESH_SECRET=generate-with-crypto
JWT_ACCESS_EXPIRES_IN=15m
JWT_REFRESH_EXPIRES_IN=30d
```

> **Generate JWT secrets:** `node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"` — run twice, use different secrets for access and refresh.

### 6. Set up main.ts

```typescript
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const reflector = app.get(Reflector);

  app.setGlobalPrefix('v1');               // all routes prefixed /v1
  app.useGlobalGuards(new JwtGuard(reflector)); // protect all routes by default
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,             // strip unknown fields
    forbidNonWhitelisted: true,  // throw on unknown fields
    transform: true,             // auto-transform types
  }));
  app.useGlobalInterceptors(new ResponseInterceptor());
  app.useGlobalFilters(new HttpExceptionFilter());
  app.enableCors({ origin: ['http://localhost:3001'], credentials: true });

  await app.listen(process.env.PORT ?? 3000);
}
```

---

## 02 — Prisma Setup (v7+)

Prisma 7 changed how configuration works. The connection URL no longer goes in schema files.

### 1. Initialize Prisma

```bash
npx prisma init
# creates prisma/ folder and .env with DATABASE_URL
```

### 2. Create prisma.config.ts at project root

```typescript
// prisma.config.ts
import path from 'node:path'
import { defineConfig } from 'prisma/config'

export default defineConfig({
  schema: path.join('prisma', 'schema.prisma'), // single file
  // OR for multi-file schema:
  // schema: path.join('prisma', 'schema'),
  datasource: {
    url: process.env.DATABASE_URL,
  },
})
```

> **Warning:** Do NOT put a datasource block in schema.prisma anymore. Prisma 7 throws an error if you do.

### 3. Set up base.prisma (generator only)

```prisma
// prisma/schema/base.prisma (if using multi-file)
generator client {
  provider     = "prisma-client-js"
  output       = "../../src/generated/prisma"
  moduleFormat = "cjs"  // required — prevents ESM/CJS conflict
}
```

> **Critical:** The `moduleFormat = "cjs"` is critical. Without it you get `exports is not defined` at runtime because NestJS is CommonJS but Prisma 7 defaults to ESM output.

### 4. PrismaService

```typescript
// src/shared/prisma/prisma.service.ts
import { PrismaClient } from '../../generated/prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

@Injectable()
export class PrismaService extends PrismaClient
  implements OnModuleInit, OnModuleDestroy {

  constructor() {
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL!,
      ssl: { rejectUnauthorized: false }, // needed for Aiven/managed DBs
    });
    const adapter = new PrismaPg(pool);
    super({ adapter });
  }

  async onModuleInit() { await this.$connect(); }
  async onModuleDestroy() { await this.$disconnect(); }
}
```

### 5. PrismaModule — mark @Global()

```typescript
@Global()  // makes PrismaService available everywhere — import once in AppModule
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
```

### 6. Add to .gitignore

```
src/generated/   # regenerated with: npx prisma generate
.env
```

### 7. Common Prisma commands

```bash
npx prisma validate                      # check schema for errors before migrating
npx prisma migrate dev --name init       # create + apply migration in development
npx prisma generate                      # regenerate TypeScript client after schema changes
npx prisma migrate deploy                # apply pending migrations in production (no new migration created)
npx prisma studio                        # open a visual database browser at localhost:5555
npx prisma db seed                       # run your seed file to populate default data
```

**`migrate dev` vs `migrate deploy`:**
- `migrate dev` — creates a new migration file from your schema changes and applies it. For development only.
- `migrate deploy` — only applies migration files that already exist. Never creates new migrations. Use in production/CI.

> **Warning:** After any schema change always run `npx prisma migrate dev` then `npx prisma generate`. Skipping generate means your TypeScript types are stale.

---

## 03 — Folder Structure

| Folder | What goes here | Rule |
|--------|---------------|------|
| `modules/` | Feature modules — auth, users, events | One folder per domain. If it has business logic, it's a module. |
| `shared/` | Injectable infrastructure — PrismaModule, RedisModule, StorageModule | Has a `.module.ts`. Mark `@Global()` if used everywhere. |
| `common/` | NestJS mechanics — guards, interceptors, filters, pipes, decorators, types | No business logic. Plugs into the NestJS request pipeline. |
| `utils/` | Pure functions — slug, geo, hash, pagination helpers | Zero NestJS dependency. No `@Injectable()`. |
| `config/` | Environment config files using `registerAs()` | One file per concern. |
| `workers/` | BullMQ job processors | Not part of the HTTP cycle. |

### Inside each feature module

```
events/
  events.module.ts      ← wires everything together
  events.controller.ts  ← HTTP layer only, calls service
  events.service.ts     ← all business logic and DB calls
  events.service.spec.ts
  dto/
    create-event.dto.ts
    update-event.dto.ts
```

---

## 04 — Modules

A module is a self-contained unit of your application. Every feature lives in a module. NestJS uses modules to manage dependency injection.

```typescript
@Module({
  imports: [OtherModule],         // modules this module depends on
  controllers: [EventsController], // HTTP handlers
  providers: [EventsService],      // services available inside this module
  exports: [EventsService],        // services other modules can use
})
export class EventsModule {}
```

### When to export a service

Export a service when another module needs to call its methods.

```typescript
// users.module.ts
@Module({
  providers: [UsersService],
  exports: [UsersService],  // ← export it
})

// messaging.module.ts
@Module({
  imports: [UsersModule],  // ← import the module (not the service directly)
  providers: [MessagingService],
})

// messaging.service.ts — now you can inject it
constructor(private usersService: UsersService) {}
```

> **Note:** You always import the **Module**, never the service directly. NestJS resolves which services are available based on what modules are imported.

### @Global() modules

Use `@Global()` for infrastructure that every module needs — database, Redis, config. Import it once in AppModule and it's available everywhere without re-importing.

---

## 05 — Controllers

Controllers handle HTTP requests. They call services and return data. Zero business logic — no database calls, no calculations.

```typescript
// imports you'll always need at the top of a controller
import {
  Controller, Get, Post, Patch, Delete,
  Body, Param, Query, Headers,
  HttpCode, HttpStatus, UseGuards,
} from '@nestjs/common';
import { EventsService } from './events.service';
import { CreateEventDto } from './dto/create-event.dto';
import { Public } from '../../common/decorators/public.decorator';
import { CurrentUser } from '../../common/decorators/current-user.decorator';
import type { JwtPayload } from '../../common/types/jwt-payload.type';

@Controller('events')  // base path: /v1/events
export class EventsController {
  constructor(private eventsService: EventsService) {}

  @Public()              // skip JWT check for this route
  @Get(':id')            // GET /v1/events/:id
  findOne(
    @Param('id') id: string,
    @CurrentUser() user: JwtPayload,
  ) {
    return this.eventsService.findById(id, user?.sub);
  }

  @Post()                // POST /v1/events
  @HttpCode(HttpStatus.CREATED)
  create(
    @CurrentUser() user: JwtPayload,
    @Body() dto: CreateEventDto,
  ) {
    return this.eventsService.create(user.sub, dto);
  }
}
```

### Why parameter decorators go before the parameter name

```typescript
findOne(
  @Param('id')      id: string,     // ← extract 'id' from route params
  @Body()           dto: CreateDto,  // ← extract entire body
  @CurrentUser()    user: JwtPayload, // ← extract user from request.user
  @Query('page')    page: number,    // ← extract 'page' from query string
)
// decorator → variable name → type annotation
```

### Multiple query params

Each query param gets its own `@Query()` decorator:

```typescript
@Get()
discoverEvents(
  @Query('page')     page: number = 1,
  @Query('limit')    limit: number = 20,
  @Query('lat')      lat?: number,
  @Query('lng')      lng?: number,
  @Query('vibeTag')  vibeTag?: string,
  @Query('status')   status?: string,
) {
  // client calls: GET /v1/discover/events?page=1&lat=6.4&lng=3.4&vibeTag=afrobeats
}
```

### Parameter decorators reference

| Decorator | What it extracts | Example |
|-----------|-----------------|---------|
| `@Body()` | Entire request body | `@Body() dto: CreateEventDto` |
| `@Body('field')` | Single field from body | `@Body('email') email: string` |
| `@Param('id')` | Route parameter | `@Param('id') id: string` from `/events/:id` |
| `@Query('page')` | Single query param | `@Query('page') page: number` from `?page=1` |
| `@Query()` | All query params as object | `@Query() query: Record<string, string>` |
| `@Headers('key')` | Specific request header | `@Headers('authorization') auth: string` |
| `@CurrentUser()` | Logged-in user (custom) | `@CurrentUser() user: JwtPayload` |

---

## 06 — Services

Services contain all business logic. They talk to the database, call other services, throw exceptions, and return data.

### Dependency injection — done in the constructor

NestJS reads the TypeScript types on constructor parameters and automatically creates and provides those instances. You never call `new SomeService()` yourself.

```typescript
// imports you'll always need at the top of a service
import { Injectable, NotFoundException, ForbiddenException,
         BadRequestException, ConflictException, UnauthorizedException
} from '@nestjs/common';
import { PrismaService } from '../../shared/prisma/prisma.service';
import { RedisService } from '../../shared/redis/redis.service';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class EventsService {
  constructor(
    private prisma: PrismaService,     // ← NestJS injects PrismaService
    private redis: RedisService,       // ← NestJS injects RedisService
    private config: ConfigService,     // ← NestJS injects ConfigService
  ) {}
  // you never write: new PrismaService() — NestJS handles it
}
```

> **Note:** For injection to work: the class being injected is marked `@Injectable()`, it's listed in `providers` of its module, and that module either exports it or is `@Global()`.

### NestJS built-in HTTP exceptions

| Exception | HTTP Status | When to use |
|-----------|------------|-------------|
| `NotFoundException` | 404 | Resource doesn't exist |
| `UnauthorizedException` | 401 | Not logged in / bad token |
| `ForbiddenException` | 403 | Logged in but not allowed |
| `BadRequestException` | 400 | Invalid input not caught by DTO |
| `ConflictException` | 409 | Resource already exists (duplicate) |
| `InternalServerErrorException` | 500 | Unexpected server error |

---

## 07 — DTOs

DTOs define the shape of request bodies and validate them automatically using `class-validator` decorators. They are TypeScript **classes**, not interfaces — because decorators only work on classes.

```typescript
// imports you'll always need at the top of a DTO file
import {
  IsString, IsNotEmpty, IsOptional, IsEmail, IsUUID,
  IsEnum, IsArray, IsNumber, IsDateString, IsBoolean,
  MinLength, MaxLength, Min, Max, ValidateNested,
} from 'class-validator';
import { Type } from 'class-transformer'; // needed for nested objects

export class CreateEventDto {
  @IsString()
  @IsNotEmpty()
  title: string;

  @IsDateString()
  startsAt: string;

  @IsNumber()
  @IsOptional()
  capacity?: number;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => CreateTicketTierDto)  // needed for nested object validation
  ticketTiers: CreateTicketTierDto[];
}
```

### Common class-validator decorators

| Decorator | What it does |
|-----------|-------------|
| `@IsString()` | Must be a string |
| `@IsNotEmpty()` | Cannot be empty string |
| `@IsOptional()` | Field is not required — skips other validators if missing |
| `@IsEmail()` | Must be valid email format |
| `@IsUUID()` | Must be a valid UUID |
| `@IsEnum(MyEnum)` | Must be one of the enum values |
| `@IsArray()` | Must be an array |
| `@MinLength(8)` | Minimum string length |
| `@MaxLength(100)` | Maximum string length |
| `@IsDateString()` | Must be ISO date string |
| `@IsNumber()` | Must be a number |
| `@Min(0)` | Minimum numeric value |
| `@ValidateNested()` | Validate nested object — always pair with `@Type()` |

> **Tip:** Always use `transform: true` in ValidationPipe. It converts `@Query('page')` from string "1" to number 1 automatically. Without it, pagination breaks.

---

## 08 — Pipes

Pipes run after guards. They validate and transform incoming data before it hits your controller. Set globally in `main.ts`.

```typescript
// main.ts — set once, applies to all routes
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,             // strips unknown fields from body
  forbidNonWhitelisted: true,  // throws 400 if unknown fields sent
  transform: true,             // auto-converts types (string → number)
}));
```

### Built-in pipes for route params

```typescript
// parse and validate a UUID param
@Get(':id')
findOne(@Param('id', ParseUUIDPipe) id: string) {}

// parse page number from query string
@Get()
findAll(@Query('page', ParseIntPipe) page: number) {}
```

---

## 09 — Guards

Guards run first in the request pipeline. They decide whether to allow the request through. Return `true` = proceed, `false` = block with 403.

### Where to define guards

| Scope | How | When |
|-------|-----|------|
| Global | `app.useGlobalGuards()` in main.ts | JwtGuard — protects every route by default |
| Global (DI) | `APP_GUARD` provider in AppModule | ThrottlerGuard — needs to inject other services |
| Controller | `@UseGuards(RolesGuard)` on class | All routes in that controller need the guard |
| Route | `@UseGuards(RolesGuard)` on method | Only one specific route needs the guard |

### What is Reflector?

`Reflector` is a NestJS utility that reads metadata attached to routes by decorators. When you put `@Public()` on a route, that decorator stamps invisible data onto the route handler. `Reflector` is how guards read that stamp.

```typescript
// @Public() stamps metadata onto the route:
export const Public = () => SetMetadata('isPublic', true);

// Reflector reads that metadata inside the guard:
const isPublic = this.reflector.getAllAndOverride('isPublic', [
  context.getHandler(),  // check the method first
  context.getClass(),    // then check the controller class
]);
// getAllAndOverride checks both and returns the first truthy value found
```

### What is AuthGuard and why extend it?

`AuthGuard('jwt')` is a pre-built Passport guard that already knows how to extract a JWT from the Authorization header, verify it, call your `JwtStrategy.validate()`, and attach the result to `request.user`. You extend it only to add the `@Public()` skip logic on top.

```typescript
// imports for guards
import { Injectable, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { AuthGuard } from '@nestjs/passport';
import { IS_PUBLIC_KEY } from '../../../common/decorators/public.decorator';

@Injectable()
export class JwtGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) {
    super(); // ← must call super() when extending
  }

  canActivate(context: ExecutionContext) {
    // step 1: check if this route is marked @Public()
    const isPublic = this.reflector.getAllAndOverride(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    // step 2: if public, skip all JWT checks entirely
    if (isPublic) return true;

    // step 3: run AuthGuard's built-in JWT verification
    // super.canActivate() does: extract token → verify → call JwtStrategy.validate()
    return super.canActivate(context);
  }
}
```

> **Note:** 401 = not authenticated (no valid token). 403 = authenticated but not authorized (valid token, wrong permissions).

---

## 10 — Interceptors

Interceptors wrap around the request/response cycle. They run before and after the controller. Almost always global.

```typescript
// imports for interceptors
import {
  Injectable, NestInterceptor, ExecutionContext, CallHandler
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

// ResponseInterceptor — wraps ALL responses in { success: true, data: ... }
@Injectable()
export class ResponseInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    // next.handle() = the controller method running
    // .pipe(map(...)) = transform what comes back from it
    return next.handle().pipe(
      map((data) => ({ success: true, data })),
    );
  }
}

// main.ts
app.useGlobalInterceptors(new ResponseInterceptor());
```

> **Tip:** Because the interceptor wraps everything in `{ success: true, data }`, your controllers just return the raw data — no need to manually wrap responses anywhere.

---

## 11 — Exception Filters

Filters catch errors thrown anywhere in your app and format them into a consistent error response.

```typescript
// imports for exception filters
import {
  ExceptionFilter, Catch, ArgumentsHost,
  HttpException, HttpStatus,
} from '@nestjs/common';
import { Request, Response } from 'express';

@Catch()  // catches everything — not just HttpException
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let code = 'INTERNAL_SERVER_ERROR';
    let message = 'Something went wrong';

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === 'object') {
        const res = exceptionResponse as any;
        // handles class-validator errors (array of messages)
        message = Array.isArray(res.message)
          ? res.message[0]
          : res.message ?? message;
        code = res.error?.toUpperCase().replace(/ /g, '_') ?? code;
      } else {
        message = exceptionResponse as string;
        code = HttpStatus[status] ?? code;
      }
    }

    if (status === HttpStatus.INTERNAL_SERVER_ERROR) {
      this.logger.error(exception);
    }

    response.status(status).json({
      success: false,
      error: { code, message },
    });
  }
}

// main.ts — always global
app.useGlobalFilters(new HttpExceptionFilter());
```

### Where errors come from

| Source | Example |
|--------|---------|
| Your services | `throw new NotFoundException('Event not found')` |
| ValidationPipe | Automatically throws 400 when DTO validation fails |
| JwtGuard | Automatically throws 401 when token is missing or invalid |
| ThrottlerGuard | Automatically throws 429 when rate limit exceeded |
| Prisma errors | Unique constraint violations, connection errors |

---

## 12 — Decorators

### Custom parameter decorator

```typescript
// @CurrentUser() — extracts request.user (set by Passport)
export const CurrentUser = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    return request.user;
  },
);

// usage in controller
getMe(@CurrentUser() user: JwtPayload) {}
```

### Custom metadata decorator

```typescript
// @Public() — tells JwtGuard to skip authentication
export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
```

### All decorators you'll use regularly

| Decorator | Where | What it does |
|-----------|-------|-------------|
| `@Injectable()` | Service, Guard, Pipe, Interceptor | Marks class as manageable by NestJS DI |
| `@Module()` | Module class | Defines a NestJS module |
| `@Controller()` | Controller class | Defines base route path |
| `@Global()` | Module class | Makes module available everywhere |
| `@Get/Post/Patch/Delete()` | Controller method | Maps HTTP method + path |
| `@HttpCode()` | Controller method | Overrides default status code |
| `@UseGuards()` | Class or method | Apply guard to specific scope |
| `@Public()` | Class or method | Custom — skip JWT auth |
| `@CurrentUser()` | Method parameter | Custom — inject logged-in user |

---

## 13 — Security & CORS

### CORS

```typescript
// main.ts
app.enableCors({
  origin: [
    'http://localhost:3001',    // local web dev
    'https://yourapp.com',      // production web
  ],
  methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
  credentials: true,            // allow cookies/auth headers
});
```

### Helmet — security headers

```bash
npm install helmet
```

```typescript
// main.ts
import helmet from 'helmet';
app.use(helmet());  // sets X-Frame-Options, CSP, HSTS, etc.
```

### Rate limiting

```bash
npm install @nestjs/throttler
```

```typescript
// app.module.ts
ThrottlerModule.forRoot([{ ttl: 60000, limit: 100 }]),

providers: [{ provide: APP_GUARD, useClass: ThrottlerGuard }]

// Tighter limits on auth routes
@Throttle({ default: { ttl: 60000, limit: 5 } })
@Post('login')
login() {}

// Skip rate limiting on specific routes
@SkipThrottle()
@Get('health')
health() {}
```

### Global prefix

```typescript
// main.ts — all routes become /v1/...
app.setGlobalPrefix('v1');
```

---

## 14 — API Versioning

### URI versioning — running v1 and v2 side by side

```typescript
// main.ts — enable versioning
import { VersioningType } from '@nestjs/common';

app.enableVersioning({
  type: VersioningType.URI,
});

// v1 controller
@Controller({ path: 'events', version: '1' })
export class EventsControllerV1 {}
// routes: /v1/events

// v2 controller — new behaviour
@Controller({ path: 'events', version: '2' })
export class EventsControllerV2 {}
// routes: /v2/events
```

> **Tip:** Use `app.enableVersioning()` from day one. It's one line to add and saves a painful migration later.

---

## 15 — Error Handling

### Handling Prisma errors in the filter

```typescript
import { Prisma } from '../generated/prisma/client';

if (exception instanceof Prisma.PrismaClientKnownRequestError) {
  if (exception.code === 'P2002') {
    // unique constraint violation
    status = 409;
    message = 'A record with this value already exists';
  }
  if (exception.code === 'P2025') {
    // record not found
    status = 404;
    message = 'Record not found';
  }
}
```

### Common Prisma error codes

| Code | Meaning |
|------|---------|
| `P2002` | Unique constraint violation (duplicate email, username, etc.) |
| `P2025` | Record not found (update/delete on non-existent record) |
| `P2003` | Foreign key constraint failed |
| `P2014` | Relation violation |

---

## 16 — Performance

### Caching with Redis

```typescript
// In any service — cache hot data
async getVibeTags() {
  const cached = await this.redis.get('vibe-tags:all');
  if (cached) return JSON.parse(cached);

  const tags = await this.prisma.vibeTag.findMany();
  await this.redis.set('vibe-tags:all', JSON.stringify(tags), 3600);
  return tags;
}

// Cache invalidation — delete when data changes
await this.redis.del('vibe-tags:all');
```

### Async jobs with BullMQ

```typescript
// Don't do heavy work in the request cycle — queue it
await this.mediaQueue.add('process-image', { fileKey, postcardId });
return { status: 'processing' };  // respond immediately

// Worker picks it up separately
@Processor('media')
export class MediaWorker {
  @Process('process-image')
  async handle(job: Job) {
    // resize, optimize, update DB
  }
}
```

### Database performance checklist

| Rule | Why |
|------|-----|
| Index foreign keys | `@@index([userId])` on every FK column |
| Index sort columns | `@@index([createdAt])` if you ORDER BY it |
| Composite indexes for filters+sorts | `@@index([gameId, score])` for leaderboard queries |
| Use `select` not `include` when possible | Only fetch columns you need |
| Use `Promise.all()` for parallel queries | Don't await sequentially if queries are independent |
| Use transactions for multi-step writes | `prisma.$transaction()` ensures atomicity |
| Counter cache counts | Store `likeCount` on the record instead of COUNT(*) every time |

---

## 17 — Swagger Docs

```bash
npm install @nestjs/swagger swagger-ui-express
```

### Setup in main.ts

```typescript
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

const config = new DocumentBuilder()
  .setTitle('Nextvibe API')
  .setDescription('The Nextvibe backend API')
  .setVersion('1.0')
  .addBearerAuth(
    { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
    'access-token',
  )
  .build();

const document = SwaggerModule.createDocument(app, config);
SwaggerModule.setup('docs', app, document, {
  swaggerOptions: { persistAuthorization: true },
});
// now live at: http://localhost:3000/docs
```

### Decorate your controllers

```typescript
import { ApiTags, ApiBearerAuth, ApiOperation, ApiResponse, ApiParam, ApiQuery } from '@nestjs/swagger';

// public controller
@ApiTags('Auth')
@Controller('auth')
export class AuthController {}

// protected controller
@ApiTags('Events')
@ApiBearerAuth('access-token')  // shows lock icon on every route
@Controller('events')
export class EventsController {}

// document individual endpoints
@ApiOperation({ summary: 'Create a new event' })
@ApiResponse({ status: 201, description: 'Event created' })
@ApiResponse({ status: 401, description: 'Unauthorized' })
@Post()
create() {}

// document query params
@ApiQuery({ name: 'lat', required: false, description: 'Latitude' })
@ApiQuery({ name: 'vibeTag', required: false })
@Get()
discover() {}
```

### Document your DTOs

```typescript
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateEventDto {
  @ApiProperty({ example: 'Detty December Kickoff' })
  @IsString()
  title: string;

  @ApiPropertyOptional({ example: 'The biggest party in Lagos' })
  @IsOptional()
  caption?: string;
}
```

> **Minimum useful setup:** just add `@ApiTags()` and `@ApiBearerAuth()` to every controller. That alone gives your frontend developer a browsable, authenticated API explorer.

---

## 18 — TypeScript Tips

### The types you'll see constantly

| Type | Where it comes from | What it is |
|------|--------------------|-----------| 
| `ExecutionContext` | `@nestjs/common` | Wraps the current request context — used in guards/interceptors |
| `CallHandler` | `@nestjs/common` | Represents the next handler in the pipeline — used in interceptors |
| `Observable` | `rxjs` | NestJS uses RxJS streams internally — interceptors work with Observables |
| `ArgumentsHost` | `@nestjs/common` | Used in exception filters to access request/response |
| `Reflector` | `@nestjs/core` | Reads metadata set by decorators — used in JwtGuard to check @Public() |
| `JwtPayload` | Your own type | Shape of the decoded JWT — { sub, email, username } |

### Use import type for type-only imports

```typescript
// When you only use something as a TypeScript type annotation
import type { JwtPayload } from '../../common/types/jwt-payload.type';

// Use regular import when you use the value at runtime
import { JwtPayload } from '../../common/types/jwt-payload.type';
```

### Prisma enum imports (v7+)

```typescript
// Enums are in $Enums, not exported directly
import { $Enums } from '../../generated/prisma/client';

// Or cast your DTO enum to the Prisma enum
gameType: dto.gameType as GameType

// Or use $Enums directly
gameType: dto.gameType as $Enums.GameType
```

### When VS Code shows stale errors

```
Ctrl + Shift + P → TypeScript: Restart TS Server
# or
Ctrl + Shift + P → Developer: Reload Window
```

---

## 19 — Testing Overview

NestJS comes with Jest pre-configured. Three levels of testing — you need all three.

### The three levels

| Level | What it tests | Speed | Where it lives |
|-------|--------------|-------|---------------|
| **Unit** | One class in isolation. All dependencies are mocked. | Milliseconds | `*.service.spec.ts` next to the file |
| **Integration** | Multiple layers together with a real database. No mocks for tested things. | Seconds | `*.integration.spec.ts` |
| **E2E** | The full HTTP request/response cycle. | Seconds | `test/*.e2e-spec.ts` |

### Running tests

```bash
# run all unit tests
npm run test

# run in watch mode
npm run test:watch

# run with coverage report
npm run test:cov

# run e2e tests
npm run test:e2e

# run a specific file
npm run test -- auth.service.spec.ts

# run tests matching a name pattern
npm run test -- --testNamePattern="should register"
```

> **Tip:** Write tests for the things that could break in production. Auth logic, business rules, edge cases. Don't test NestJS itself or Prisma — test your logic.

---

## 20 — Unit Tests

A unit test tests one class in complete isolation. Every dependency is replaced with a mock.

```typescript
// src/modules/auth/auth.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { AuthService } from './auth.service';
import { PrismaService } from '../../shared/prisma/prisma.service';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { RedisService } from '../../shared/redis/redis.service';
import { ConflictException, UnauthorizedException } from '@nestjs/common';

describe('AuthService', () => {
  let service: AuthService;

  // mock objects — replace real dependencies with fakes you control
  const mockPrisma = {
    user: {
      findFirst:  jest.fn(),
      findUnique: jest.fn(),
      create:     jest.fn(),
      update:     jest.fn(),
    },
    userPreference: { create: jest.fn() },
    $transaction: jest.fn((cb) => cb(mockPrisma)), // execute callback immediately
  };

  const mockJwt = {
    sign: jest.fn().mockReturnValue('mock-token'),
    verify: jest.fn(),
  };

  const mockConfig = {
    get: jest.fn((key: string) => {
      const values: Record<string, string> = {
        JWT_ACCESS_SECRET:      'test-access-secret',
        JWT_REFRESH_SECRET:     'test-refresh-secret',
        JWT_ACCESS_EXPIRES_IN:  '15m',
        JWT_REFRESH_EXPIRES_IN: '30d',
        GOOGLE_CLIENT_ID:       'test-client-id',
        WEB_APP_URL:            'http://localhost:3001',
      };
      return values[key];
    }),
  };

  const mockRedis = {
    set:    jest.fn(),
    get:    jest.fn(),
    del:    jest.fn(),
    exists: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        { provide: PrismaService, useValue: mockPrisma },
        { provide: JwtService,    useValue: mockJwt },
        { provide: ConfigService, useValue: mockConfig },
        { provide: RedisService,  useValue: mockRedis },
      ],
    }).compile();

    service = module.get<AuthService>(AuthService);
  });

  afterEach(() => {
    jest.clearAllMocks(); // reset all mock call counts between tests
  });

  describe('register', () => {
    it('should register a new user and return tokens', async () => {
      // arrange
      mockPrisma.user.findFirst.mockResolvedValue(null);
      mockPrisma.user.create.mockResolvedValue({
        id: 'user-uuid',
        email: 'test@nextvibe.com',
        username: 'testuser',
        displayName: 'Test User',
      });
      mockRedis.set.mockResolvedValue('OK');

      // act
      const result = await service.register({
        email: 'test@nextvibe.com',
        username: 'testuser',
        displayName: 'Test User',
        password: 'password123',
      });

      // assert
      expect(result).toHaveProperty('accessToken');
      expect(result).toHaveProperty('refreshToken');
      expect(result.user.email).toBe('test@nextvibe.com');
      expect(mockPrisma.user.create).toHaveBeenCalledTimes(1);
    });

    it('should throw ConflictException when email already exists', async () => {
      mockPrisma.user.findFirst.mockResolvedValue({ id: 'existing-user' });

      await expect(
        service.register({
          email: 'test@nextvibe.com',
          username: 'testuser',
          displayName: 'Test User',
          password: 'password123',
        }),
      ).rejects.toThrow(ConflictException);
    });
  });
});
```

### Useful Jest matchers

```typescript
// equality
expect(result).toBe('exact same value')        // strict equality (===)
expect(result).toEqual({ id: '1' })            // deep equality (objects)
expect(result).toMatchObject({ id: '1' })      // partial match — extra fields OK

// truthiness
expect(result).toBeTruthy()
expect(result).toBeFalsy()
expect(result).toBeNull()
expect(result).toBeDefined()

// properties
expect(result).toHaveProperty('accessToken')
expect(arr).toHaveLength(3)
expect(arr).toContain('value')

// errors
expect(fn).toThrow(NotFoundException)
await expect(asyncFn()).rejects.toThrow('message')
await expect(asyncFn()).resolves.toEqual({ id: '1' })

// mock assertions
expect(mockFn).toHaveBeenCalled()
expect(mockFn).toHaveBeenCalledTimes(1)
expect(mockFn).toHaveBeenCalledWith({ id: 'uuid' })
expect(mockFn).not.toHaveBeenCalled()
```

### Mocking patterns

```typescript
// mock return value once
mockFn.mockResolvedValueOnce({ id: '1' });

// mock return value always
mockFn.mockResolvedValue({ id: '1' });

// mock implementation
mockFn.mockImplementation((id) => ({ id, name: 'test' }));

// mock to throw
mockFn.mockRejectedValue(new Error('DB connection failed'));

// spy on a real method
const spy = jest.spyOn(service, 'generateTokens');
expect(spy).toHaveBeenCalledWith({ sub: 'uuid' });
```

---

## 21 — Integration Tests

Integration tests use a real database. They verify your code actually works with real Postgres.

### Setup — test database

```bash
# .env.test
DATABASE_URL=postgresql://postgres:password@localhost:5432/nextvibe_test
JWT_ACCESS_SECRET=test-access-secret-long-enough
JWT_REFRESH_SECRET=test-refresh-secret-long-enough
```

```typescript
// src/modules/users/users.service.integration.spec.ts
import { Test } from '@nestjs/testing';
import { UsersService } from './users.service';
import { PrismaService } from '../../shared/prisma/prisma.service';

describe('UsersService (integration)', () => {
  let service: UsersService;
  let prisma: PrismaService;

  beforeAll(async () => {
    const module = await Test.createTestingModule({
      providers: [UsersService, PrismaService],
    }).compile();

    service = module.get(UsersService);
    prisma  = module.get(PrismaService);
    await prisma.onModuleInit();
  });

  afterAll(async () => {
    await prisma.onModuleDestroy();
  });

  beforeEach(async () => {
    // clean up test data before each test — order matters (FK constraints)
    await prisma.follow.deleteMany();
    await prisma.userPreference.deleteMany();
    await prisma.user.deleteMany();
  });

  it('should follow and unfollow a user', async () => {
    const [userA, userB] = await Promise.all([
      prisma.user.create({ data: { email: 'a@test.com', username: 'usera', displayName: 'User A' } }),
      prisma.user.create({ data: { email: 'b@test.com', username: 'userb', displayName: 'User B' } }),
    ]);

    const followResult = await service.follow(userA.id, userB.id);
    expect(followResult.following).toBe(true);
    expect(followResult.isMutual).toBe(false);
  });
});
```

> **Warning:** Always clean up in `beforeEach` — not `afterEach`. If a test fails before cleanup, the next test starts with dirty data.

---

## 22 — End-to-End Tests

E2E tests boot the entire NestJS application and send real HTTP requests — exactly like your frontend would.

```typescript
// test/app.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Auth (e2e)', () => {
  let app: INestApplication;
  let accessToken: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();

    // apply the same global config as main.ts
    app.setGlobalPrefix('v1');
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
    app.useGlobalInterceptors(new ResponseInterceptor());
    app.useGlobalFilters(new HttpExceptionFilter());

    await app.init();
  });

  afterAll(async () => { await app.close(); });

  it('POST /v1/auth/register — should register a user', () => {
    return request(app.getHttpServer())
      .post('/v1/auth/register')
      .send({ email: 'e2e@nextvibe.com', username: 'e2euser', displayName: 'E2E User', password: 'password123' })
      .expect(201)
      .expect((res) => {
        expect(res.body.success).toBe(true);
        expect(res.body.data).toHaveProperty('accessToken');
        accessToken = res.body.data.accessToken;
      });
  });

  it('GET /v1/users/me — should return 401 without token', () => {
    return request(app.getHttpServer())
      .get('/v1/users/me')
      .expect(401);
  });

  it('GET /v1/users/me — should return profile with valid token', () => {
    return request(app.getHttpServer())
      .get('/v1/users/me')
      .set('Authorization', `Bearer ${accessToken}`)
      .expect(200);
  });
});
```

### Coverage targets

| Layer | Target | Notes |
|-------|--------|-------|
| Services | 80%+ | Where your business logic lives |
| Controllers | Covered by E2E | Don't unit test controllers directly |
| Utils | 100% | Pure functions, easy to test exhaustively |
| Guards/Interceptors/Filters | Core paths | Happy path + main error case |

---

## 23 — DB Design Patterns

### Never store arrays as columns

```typescript
// ❌ wrong — array column, can't query, can't scale
model User {
  followers String[]  // array of user IDs
}

// ✅ correct — join table, fully queryable
model Follow {
  followerId   String
  followingId  String
  createdAt    DateTime  @default(now())

  @@unique([followerId, followingId])
}
```

### Polymorphic tables — one table for many targets

```prisma
model Like {
  userId      String
  targetType  LikeTarget  // EVENT | POSTCARD
  targetId    String      // polymorphic FK

  @@unique([userId, targetType, targetId])
  @@index([targetType, targetId])
}
```

### Self-referencing models — comment threads

```prisma
model Comment {
  id        String   @id
  parentId  String?  // null = top-level comment

  parent   Comment?  @relation("CommentReplies", fields: [parentId], references: [id])
  replies  Comment[] @relation("CommentReplies")
  // named relation required because it's self-referencing
}
```

### Counter cache — never COUNT(*) on hot data

```typescript
// ❌ expensive — COUNT on every feed load
SELECT COUNT(*) FROM likes WHERE post_id = $1

// ✅ denormalized counter
// store likeCount on the record, increment/decrement atomically
await this.prisma.postcard.update({
  where: { id: targetId },
  data: { likeCount: { increment: 1 } },
});
```

### Soft delete

```prisma
model Post {
  deletedAt  DateTime?  // null = active, set = deleted at X
}
```

```typescript
// all queries filter soft-deleted records
await prisma.post.findMany({ where: { deletedAt: null } })
```

### Symmetric relationship ordering

```typescript
// enforce ordering so UNIQUE constraint prevents duplicates
const [userAId, userBId] = userId < dto.userId
  ? [userId, dto.userId]
  : [dto.userId, userId];
```

### JSONB for flexible schema

```prisma
model Game {
  gameType  GameType
  config    Json     // shape depends on gameType
}
// TRIVIA:  { questions: [...], timePerQuestion: 20 }
// PUZZLE:  { words: [...], timePerWord: 30 }
```

---

## 24 — Common Issues

### UnknownDependenciesException

```
Error: Nest can't resolve dependencies of AuthService (?, JwtService)
```

Fix checklist:
1. Is the class marked `@Injectable()`?
2. Is it in the `providers` array of its module?
3. If from another module — is that module imported AND does it export the service?
4. Is it a plain class (like `OAuth2Client`)? Don't inject it — instantiate with `new` inside the constructor body.

### Circular dependency

```typescript
// Fix — use forwardRef()
@Module({
  imports: [forwardRef(() => UsersModule)],
})

// In the service constructor:
constructor(
  @Inject(forwardRef(() => UsersService))
  private usersService: UsersService,
) {}
```

### Prisma: id is undefined in where clause

```
Error: Argument where needs at least one argument. id: undefined
```

Check: what does `JwtStrategy.validate()` return? Is the token payload using `sub` or `id`? Be consistent everywhere.

### ValidationPipe not working

```typescript
// Cause: using interface instead of class for DTO
export class CreateEventDto {}    // ✅ decorators work
export interface CreateEventDto {} // ❌ decorators don't work on interfaces
```

### OOM on Render / Railway free tier

```json
// package.json
"start": "node --max-old-space-size=400 dist/src/main.js"
```

Also set environment variable: `NODE_OPTIONS=--max-old-space-size=400`

### Prisma ESM/CJS conflict

```prisma
generator client {
  provider     = "prisma-client-js"
  moduleFormat = "cjs"  // ← this fixes it
}
```

### Route param conflicts — static vs dynamic

```typescript
// static routes MUST come before dynamic ones
@Get('me/created')   // ← define first
getMyEvents() {}

@Get(':id')          // ← define after
findOne() {}
```

### TLS error with managed databases (Aiven, etc.)

```typescript
// In PrismaService constructor — pass Pool directly
const pool = new Pool({
  connectionString: process.env.DATABASE_URL!,
  ssl: { rejectUnauthorized: false },
});
const adapter = new PrismaPg(pool);
super({ adapter });
```

---

## 25 — Monorepos

### When to use a monorepo

| Use monorepo when | Use separate repos when |
|------------------|------------------------|
| Multiple apps share the same DTOs/types | Teams are completely independent |
| A worker process and API share Prisma schema | Apps have different deployment cadences |
| Small to medium team working across all apps | Apps are in different languages |

### Convert existing project to monorepo

```bash
nest generate app worker-app     # adds a second app
nest generate app admin-api      # adds a third app
nest generate library shared     # adds a shared library
```

Structure becomes:

```
apps/
  nextvibe-api/    ← your main API
  worker-app/      ← BullMQ workers as a separate app
libs/
  shared/          ← shared code imported by all apps
    src/
      dto/
      types/
      utils/
```

### Run each app separately

```bash
nest start nextvibe-api --watch
nest start worker-app --watch

nest build nextvibe-api
nest build worker-app
```

### Import from shared library

```typescript
import { CreateEventDto } from '@app/shared/dto/create-event.dto';
import { JwtPayload } from '@app/shared/types/jwt-payload.type';
```

---

## 26 — Advanced Patterns

### Event-driven architecture with NestJS EventEmitter

```bash
npm install @nestjs/event-emitter
```

```typescript
// app.module.ts
EventEmitterModule.forRoot()

// events.service.ts — emit after RSVP
this.eventEmitter.emit('rsvp.created', { userId, eventId, organizerId });

// notifications.service.ts — listen
@OnEvent('rsvp.created')
async handleRsvpCreated(payload: { userId: string, organizerId: string }) {
  await this.create({ recipientId: payload.organizerId, actorId: payload.userId });
}
```

### Custom repository pattern

```typescript
@Injectable()
export class EventsRepository {
  constructor(private prisma: PrismaService) {}

  async findPublishedNearLocation(lat: number, lng: number, radiusKm: number) {
    // complex geo query lives here, not in the service
    return this.prisma.$queryRaw`
      SELECT * FROM events
      WHERE status = 'PUBLISHED'
      AND ST_DWithin(location_point, ST_MakePoint(${lng}, ${lat})::geography, ${radiusKm * 1000})
    `;
  }
}
```

### Health checks

```bash
npm install @nestjs/terminus
```

```typescript
@Controller('health')
export class HealthController {
  constructor(private health: HealthCheckService,
              private db: PrismaHealthIndicator) {}

  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.db.pingCheck('database'),
    ]);
  }
}
// GET /health → { status: 'ok', info: { database: { status: 'up' } } }
```

### Config validation on startup

```bash
npm install joi
```

```typescript
// app.module.ts
ConfigModule.forRoot({
  isGlobal: true,
  validationSchema: Joi.object({
    DATABASE_URL:       Joi.string().required(),
    JWT_ACCESS_SECRET:  Joi.string().min(32).required(),
    JWT_REFRESH_SECRET: Joi.string().min(32).required(),
    PORT:               Joi.number().default(3000),
    NODE_ENV:           Joi.string().valid('development', 'production', 'test'),
  }),
})
```

### Idempotency — safe to call multiple times

```typescript
// ❌ throws ConflictException if called twice
await prisma.follow.create({ data: { followerId, followingId } });

// ✅ safe to call multiple times
await prisma.follow.upsert({
  where: { followerId_followingId: { followerId, followingId } },
  create: { followerId, followingId },
  update: {},  // empty update = do nothing if exists
});
```

---

## 27 — Scaling & Sharding

### The scaling journey

| Stage | Users | What changes |
|-------|-------|-------------|
| MVP | 0 – 10k | Single server, single DB, single Redis. PaaS (Render/Railway). Focus on shipping. |
| Growth | 10k – 500k | Add Postgres read replicas. Redis cluster. CDN for media. Horizontal API scaling. Redis adapter for WebSockets. |
| Scale | 500k – 5M | Extract hot services. PgBouncer connection pooling. Queue-based architecture everywhere. |
| Hyperscale | 5M+ | Database sharding. Multi-region. Microservices. Event sourcing. Dedicated infra team. |

### Read replicas

```bash
npm install @prisma/extension-read-replicas
```

```typescript
const prisma = new PrismaClient().$extends(
  readReplicas({
    url: [process.env.DATABASE_READ_URL_1, process.env.DATABASE_READ_URL_2],
  })
);
// reads automatically go to replicas, writes go to primary
```

### Horizontal scaling — what breaks and how to fix it

```
Client → Load Balancer → [API instance 1]
                       → [API instance 2]
                       → [API instance 3]

1. WebSockets — users on different instances can't talk
   Fix: Redis pub/sub adapter (already implemented)

2. Rate limiting — each instance has its own counter
   Fix: Redis-backed throttler (already implemented)

3. In-memory cache — each instance caches independently
   Fix: use Redis for all caching (already implemented)
```

### Database sharding

```
# Vertical partitioning — different tables on different DBs
DB1: users, follows, user_preferences   (identity data)
DB2: events, rsvps, check_ins           (event data)
DB3: messages, conversations            (messaging data)

# Horizontal sharding — same table split across DBs by shard key
DB1: events where organizer_id starts with 0-3
DB2: events where organizer_id starts with 4-7
DB3: events where organizer_id starts with 8-f

# Shard key rules:
# 1. High cardinality (userId is good, status is bad)
# 2. Queries should rarely cross shards
# 3. Don't shard prematurely — it's a last resort
```

### Message queues at scale

```
MVP:    BullMQ + Redis       — fine up to ~10k jobs/day
Growth: RabbitMQ             — proper message broker, acks, dead letters
Scale:  Kafka                — distributed log, millions of events/second

NestJS supports all three natively.
Migration path: BullMQ → RabbitMQ → Kafka
Each step is a module swap, not a rewrite.
```

### Microservices with NestJS

```typescript
// main.ts of a microservice
const app = await NestFactory.createMicroservice(AppModule, {
  transport: Transport.REDIS,
  options: { host: 'localhost', port: 6379 },
});

// in the receiving microservice
@MessagePattern({ cmd: 'get_user' })
getUser(@Payload() id: string) {
  return this.usersService.findById(id);
}

// calling from the API gateway
return this.client.send({ cmd: 'get_user' }, userId);
```

> **Note:** The right time to extract a microservice: when one domain has genuinely different scaling requirements, has a separate team, or needs to be deployed independently. A well-structured modular monolith outperforms a badly designed microservice architecture every time.

---

*Written from experience building Nextvibe — kingsleydaprime*
