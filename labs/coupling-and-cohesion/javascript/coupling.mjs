// coupling.mjs — measure coupling between the top-level modules of a src/ folder.
// Usage: node coupling.mjs path/to/src
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

const SOURCE = /\.(m?[jt]sx?)$/;
const IMPORT = /(?:import|export)\s[^'"]*?from\s*["']([^"']+)["']|import\s*\(\s*["']([^"']+)["']\s*\)|import\s+["']([^"']+)["']/g;

function filesUnder(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = path.join(dir, name);
    if (name === "node_modules") return [];
    return statSync(full).isDirectory() ? filesUnder(full) : SOURCE.test(name) ? [full] : [];
  });
}

// The module a path belongs to is its first folder under src/ ("orders/x.ts" -> "orders").
// An import of a folder ("../users") belongs to that folder's module too.
function moduleOf(src, file) {
  const parts = path.relative(src, file).split(path.sep);
  const isFolder = existsSync(file) && statSync(file).isDirectory();
  return parts.length > 1 || isFolder ? parts[0] : "(root)";
}

// Turn an import string into a path under src/, or null for packages like "express".
function resolve(src, fromFile, specifier) {
  if (specifier.startsWith("@/")) return path.join(src, specifier.slice(2));
  if (specifier.startsWith(".")) return path.resolve(path.dirname(fromFile), specifier);
  return null;
}

export function analyse(src) {
  src = path.resolve(src);
  const edges = new Map(); // module -> Set of modules it imports
  const modules = new Set();
  for (const file of filesUnder(src)) {
    const from = moduleOf(src, file);
    modules.add(from);
    edges.set(from, edges.get(from) ?? new Set());
    for (const match of readFileSync(file, "utf8").matchAll(IMPORT)) {
      const target = resolve(src, file, match[1] ?? match[2] ?? match[3]);
      if (!target || path.relative(src, target).startsWith("..")) continue;
      const to = moduleOf(src, target);
      if (to !== from) edges.get(from).add(to);
    }
  }

  const rows = [...modules].sort().map((name) => {
    const efferent = edges.get(name).size; // Ce: modules this one depends on
    const afferent = [...edges.values()].filter((deps) => deps.has(name)).length; // Ca: modules depending on it
    const instability = afferent + efferent === 0 ? null : efferent / (afferent + efferent);
    return { module: name, afferent, efferent, instability };
  });
  return { rows, cycles: cycles(edges) };
}

// Tarjan's algorithm: every strongly connected component bigger than one module is a cycle.
function cycles(edges) {
  let index = 0;
  const stack = [], onStack = new Set(), indexOf = new Map(), low = new Map(), found = [];
  const visit = (v) => {
    indexOf.set(v, index); low.set(v, index); index++;
    stack.push(v); onStack.add(v);
    for (const w of edges.get(v) ?? []) {
      if (!indexOf.has(w)) { visit(w); low.set(v, Math.min(low.get(v), low.get(w))); }
      else if (onStack.has(w)) low.set(v, Math.min(low.get(v), indexOf.get(w)));
    }
    if (low.get(v) === indexOf.get(v)) {
      const component = [];
      let w;
      do { w = stack.pop(); onStack.delete(w); component.push(w); } while (w !== v);
      if (component.length > 1) found.push(component.sort());
    }
  };
  for (const v of [...edges.keys()].sort()) if (!indexOf.has(v)) visit(v);
  return found;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const src = process.argv[2] ?? "src";
  const { rows, cycles: found } = analyse(src);
  console.log("module".padEnd(16) + "Ca  Ce  instability");
  for (const r of rows) {
    const i = r.instability === null ? "  -" : r.instability.toFixed(2);
    console.log(r.module.padEnd(16) + String(r.afferent).padStart(2) + String(r.efferent).padStart(4) + "  " + i);
  }
  console.log(found.length ? `\ncycles: ${found.map((c) => c.join(" <-> ")).join("; ")}` : "\nno cycles");
}
