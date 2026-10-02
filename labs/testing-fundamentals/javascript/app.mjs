// app.mjs — a tiny HTTP API over a real database. Nothing to install: node:http + node:sqlite.
import { createServer } from "node:http";
import { DatabaseSync } from "node:sqlite";

export function openDb() {
  const db = new DatabaseSync(":memory:");
  db.exec(`CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    trial_ends_on TEXT NOT NULL
  )`);
  return db;
}

const json = (res, status, body) => {
  res.writeHead(status, { "content-type": "application/json" });
  res.end(JSON.stringify(body));
};

export function createApp(db) {
  return createServer(async (req, res) => {
    if (req.method === "POST" && req.url === "/users") {
      let raw = "";
      for await (const chunk of req) raw += chunk;
      const { email, trialEndsOn } = JSON.parse(raw);
      if (!email?.includes("@")) return json(res, 400, { error: "invalid email" });
      try {
        const { lastInsertRowid } = db
          .prepare("INSERT INTO users (email, trial_ends_on) VALUES (?, ?)")
          .run(email, trialEndsOn);
        return json(res, 201, { id: Number(lastInsertRowid) });
      } catch (err) {
        if (String(err.message).includes("UNIQUE")) return json(res, 409, { error: "email taken" });
        throw err;
      }
    }
    json(res, 404, { error: "not found" });
  });
}
