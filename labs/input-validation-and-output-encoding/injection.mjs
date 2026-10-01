// injection.mjs — SQL injection, and the two fixes: parameters for values, allowlists for names.
import { DatabaseSync } from "node:sqlite";

export function openDb() {
  const db = new DatabaseSync(":memory:");
  db.exec(`
    CREATE TABLE users (username TEXT PRIMARY KEY, role TEXT NOT NULL, created_at TEXT NOT NULL);
    INSERT INTO users VALUES ('admin', 'admin', '2026-01-01'), ('ada', 'member', '2026-03-01'), ('bayo', 'member', '2026-02-01');
  `);
  return db;
}

// VULNERABLE: the input is pasted into the SQL text, so it can change the query's structure.
export function findUserUnsafe(db, username) {
  return db.prepare(`SELECT username, role FROM users WHERE username = '${username}'`).all();
}

// SAFE: the SQL text is fixed; the input travels separately as a value and can never become syntax.
export function findUserSafe(db, username) {
  return db.prepare("SELECT username, role FROM users WHERE username = ?").all(username);
}

// Column names can't be parameters — only values can. So names come from an allowlist.
const SORTABLE = { newest: "created_at DESC", name: "username ASC" };
export function listUsers(db, sort) {
  const orderBy = SORTABLE[sort];
  if (!orderBy) throw new Error(`cannot sort by "${sort}"`);
  return db.prepare(`SELECT username FROM users ORDER BY ${orderBy}`).all().map((r) => r.username);
}
