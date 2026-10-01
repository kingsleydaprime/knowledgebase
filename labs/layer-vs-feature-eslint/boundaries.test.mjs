// boundaries.test.mjs — runs ESLint in each sub-project and checks exactly which files fail.
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));

function failingFiles(project) {
  const cwd = path.join(here, project);
  const run = spawnSync("npx", ["eslint", "src", "--format", "json"], { cwd, encoding: "utf8" });
  const results = JSON.parse(run.stdout);
  return results
    .filter((r) => r.errorCount > 0)
    .map((r) => path.relative(cwd, r.filePath))
    .sort();
}

test("express: deep imports and shared→feature imports fail; index.ts imports pass", () => {
  assert.deepEqual(failingFiles("express"), [
    "src/features/orders/bad-alias.ts",
    "src/features/orders/bad.ts",
    "src/shared/bad-shared.ts",
  ]);
});

test("react: a feature importing another feature fails; composing them in app/ passes", () => {
  assert.deepEqual(failingFiles("react"), ["src/features/products/components/Bad.tsx"]);
});
