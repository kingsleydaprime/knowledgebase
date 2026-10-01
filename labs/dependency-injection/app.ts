// app.ts — a manual composition root, and the scope bug it makes visible
import { AsyncLocalStorage } from "node:async_hooks";

const tick = () => new Promise((resolve) => setTimeout(resolve, 5));

// ---- the dependencies ----
export type AuditLog = { entries: string[] };

// BUG: built once at startup, but holds per-request data.
export class AuditServiceWithUserField {
  log: AuditLog;
  currentUser = "nobody";
  constructor(log: AuditLog) {
    this.log = log;
  }
  setUser(user: string) {
    this.currentUser = user;
  }
  async record(action: string) {
    await tick(); // any await lets another request run in between
    this.log.entries.push(`${this.currentUser}: ${action}`);
  }
}

// FIX 1: request data is a method argument.
export class AuditService {
  log: AuditLog;
  constructor(log: AuditLog) {
    this.log = log;
  }
  async record(user: string, action: string) {
    await tick();
    this.log.entries.push(`${user}: ${action}`);
  }
}

// FIX 2: ambient per-request context, for things every layer needs (trace IDs, the current user).
export const requestContext = new AsyncLocalStorage<{ user: string }>();
export class ContextAuditService {
  log: AuditLog;
  constructor(log: AuditLog) {
    this.log = log;
  }
  async record(action: string) {
    await tick();
    this.log.entries.push(`${requestContext.getStore()?.user ?? "nobody"}: ${action}`);
  }
}

// ---- the composition root: the only place that knows concrete types ----
export function compose() {
  const log: AuditLog = { entries: [] };
  return {
    log,
    buggy: new AuditServiceWithUserField(log),
    audit: new AuditService(log),
    contextAudit: new ContextAuditService(log),
  };
}
