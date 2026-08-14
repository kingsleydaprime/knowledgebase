# Ways to handle errors in Node.js

## Process-level error events

Every Node.js process emits these events. Always handle them — unhandled, they crash the process with no useful log or, worse, silently swallow errors.

| Event | When it fires | Fatal? |
|---|---|---|
| `uncaughtException` | Synchronous throw not caught anywhere | Yes — exit 1 |
| `unhandledRejection` | Promise rejection with no `.catch()` | Yes — exit 1 |
| `SIGTERM` | Docker/K8s kill signal, `kill <pid>` | Graceful shutdown |
| `SIGINT` | Ctrl+C in terminal | Graceful shutdown |
| `SIGHUP` | Terminal window closed (Unix) | Graceful shutdown |
| `SIGUSR2` | nodemon restart | Cleanup + re-raise |
| `warning` | Node.js deprecation/experimental notices | Log only |

---

## Plain Node.js (no framework)

```js
// error-handler.js
const http = require('http');

function registerProcessErrorHandlers(server) {
  function shutdown(signal, code = 0) {
    console.log(`\n[${signal}] Shutting down gracefully...`);

    // Force exit if server.close() hangs (stuck connection, etc.)
    const timer = setTimeout(() => {
      console.error('[shutdown] Timed out — forcing exit');
      process.exit(1);
    }, 10_000);
    timer.unref();

    server.close((err) => {
      if (err) {
        console.error('[shutdown] Error closing server:', err);
        process.exit(1);
      }
      console.log('[shutdown] Server closed. Exiting.');
      process.exit(code);
    });
  }

  // Synchronous throw not caught anywhere — always fatal
  process.on('uncaughtException', (err) => {
    console.error(`[uncaughtException] ${err.message}\n${err.stack}`);
    process.exit(1);
  });

  // Promise rejection with no .catch() — treat as fatal
  process.on('unhandledRejection', (reason) => {
    const message = reason instanceof Error ? reason.stack : String(reason);
    console.error(`[unhandledRejection] ${message}`);
    process.exit(1);
  });

  // Docker/Kubernetes sends SIGTERM before force-killing
  process.on('SIGTERM', () => shutdown('SIGTERM'));

  // Ctrl+C in terminal
  process.on('SIGINT', () => shutdown('SIGINT'));

  // Terminal closed (Unix)
  process.on('SIGHUP', () => shutdown('SIGHUP'));

  // nodemon uses SIGUSR2 to restart — clean up then re-raise
  process.once('SIGUSR2', () => {
    console.log('[SIGUSR2] nodemon restart — closing server');
    server.close(() => process.kill(process.pid, 'SIGUSR2'));
  });

  // Node.js internal warnings (deprecations, experimental features)
  process.on('warning', (warning) => {
    console.warn(`[warning:${warning.name}] ${warning.message}`);
  });
}

// Usage
const server = http.createServer(app);
registerProcessErrorHandlers(server);
server.listen(3000);
```

---

## Express.js

Express has its own error middleware convention on top of the process handlers above.

```js
// express-error-handler.js

// 404 — must be placed after all routes
function notFoundHandler(req, res, next) {
  res.status(404).json({
    success: false,
    error: { code: 'NOT_FOUND', message: `Cannot ${req.method} ${req.path}` },
  });
}

// Global error handler — must have exactly 4 args so Express recognises it
function globalErrorHandler(err, req, res, next) {
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  // Log with request context
  console.error(
    `[error] ${req.method} ${req.url} — ${status}: ${message}`,
    process.env.NODE_ENV !== 'production' ? err.stack : '',
  );

  res.status(status).json({
    success: false,
    error: {
      code: err.code || 'INTERNAL_ERROR',
      message,
      // Only expose stack in dev
      ...(process.env.NODE_ENV !== 'production' && { stack: err.stack }),
    },
  });
}

// Usage
const express = require('express');
const app = express();

app.use('/api', yourRouter);

app.use(notFoundHandler);          // catch unmatched routes
app.use(globalErrorHandler);       // catch everything thrown via next(err)

const server = app.listen(3000);
registerProcessErrorHandlers(server); // from the plain Node.js section above
```

### Triggering the global error handler from a route

```js
// Option 1: throw inside async route (requires express-async-errors or Express 5)
app.get('/users/:id', async (req, res) => {
  const user = await db.findUser(req.params.id);
  if (!user) {
    const err = new Error('User not found');
    err.status = 404;
    throw err;
  }
  res.json(user);
});

// Option 2: pass to next() manually (Express 4 without async error patch)
app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await db.findUser(req.params.id);
    if (!user) return next(Object.assign(new Error('User not found'), { status: 404 }));
    res.json(user);
  } catch (err) {
    next(err);
  }
});
```

---

## NestJS

NestJS wraps this in its own lifecycle, but the same process events apply.

```ts
// src/common/process-error-handler.ts
import { INestApplication, Logger } from '@nestjs/common';

const logger = new Logger('Process');

export function registerProcessErrorHandlers(app: INestApplication) {
  async function shutdown(signal: string, code = 0) {
    logger.log(`${signal} received — closing application`);

    // Force-exit if graceful close hangs
    const timer = setTimeout(() => {
      logger.error('Graceful shutdown timed out — forcing exit');
      process.exit(1);
    }, 10_000);
    timer.unref();

    await app.close(); // triggers OnApplicationShutdown hooks
    process.exit(code);
  }

  process.on('uncaughtException', (err: Error) => {
    logger.error(`Uncaught Exception: ${err.message}`, err.stack);
    process.exit(1);
  });

  process.on('unhandledRejection', (reason: unknown) => {
    const message = reason instanceof Error ? reason.stack : String(reason);
    logger.error(`Unhandled Rejection: ${message}`);
    process.exit(1);
  });

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT',  () => shutdown('SIGINT'));
  process.on('SIGHUP',  () => shutdown('SIGHUP'));

  // nodemon restart — re-raise after cleanup so nodemon can proceed
  process.once('SIGUSR2', async () => {
    logger.log('SIGUSR2 received (nodemon restart)');
    await app.close();
    process.kill(process.pid, 'SIGUSR2');
  });

  process.on('warning', (warning: Error) => {
    logger.warn(`[${warning.name}] ${warning.message}`);
  });
}
```

```ts
// src/main.ts
import { registerProcessErrorHandlers } from './common/process-error-handler';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  // ... setup ...
  registerProcessErrorHandlers(app);
  await app.listen(3000);
}
bootstrap();
```

**NestJS-specific:** `app.close()` calls `OnApplicationShutdown` hooks on every provider, which is how you cleanly close DB connections, flush message queues, etc. without this, those connections leak on restart.

---

## Key rules across all frameworks

1. **Always exit after `uncaughtException`** — the process state is undefined after an uncaught throw. Trying to continue is dangerous.
2. **Always exit after `unhandledRejection`** — Node.js will do it for you in future versions anyway (it's already a warning by default).
3. **Always set a force-exit timeout on shutdown** — `server.close()` / `app.close()` only stops accepting new connections; existing ones must drain. If one hangs, your process hangs. The timeout is your safety net.
4. **Use `timer.unref()`** — without it, the timeout itself keeps the event loop alive even if everything else has closed.
5. **`SIGUSR2` is for nodemon** — re-raise it after cleanup instead of exiting, otherwise nodemon's restart breaks.
