// dns.ts — DNS on the wire, and the behaviour of the resolvers that cache it: building and reading DNS packets by
// hand, a tiny authoritative server over UDP, the iterative walk from the root, TTL and negative caching through a
// migration, and the query count a Kubernetes-style search list adds.
import dgram from "node:dgram";

export const TYPE = { A: 1, NS: 2, CNAME: 5, SOA: 6, TXT: 16 } as const;

/** A name on the wire is a list of labels, each prefixed by its length, ending with a zero: 3www7example3com0. */
export function encodeName(name: string): Buffer {
  const parts = name.replace(/\.$/, "").split(".").filter(Boolean);
  const bytes: number[] = [];
  for (const label of parts) {
    if (label.length > 63) throw new RangeError(`label too long: ${label}`);
    bytes.push(label.length, ...Buffer.from(label, "ascii"));
  }
  bytes.push(0);
  return Buffer.from(bytes);
}

/** A query: a 12-byte header (ID, flags, four counts), then one question (name, type, class IN = 1). */
export function buildQuery(id: number, name: string, type: number): Buffer {
  const header = Buffer.alloc(12);
  header.writeUInt16BE(id, 0);
  header.writeUInt16BE(0x0100, 2); // flags: RD, "recursion desired"
  header.writeUInt16BE(1, 4); // one question
  const tail = Buffer.alloc(4);
  tail.writeUInt16BE(type, 0);
  tail.writeUInt16BE(1, 2); // class IN
  return Buffer.concat([header, encodeName(name), tail]);
}

/** Reads a name, following compression pointers: two bytes starting 11 mean "the rest is at this offset". */
function readName(buf: Buffer, offset: number): [string, number] {
  const labels: string[] = [];
  let end = -1; // where the name ends in the place we started reading, once we've followed a pointer
  for (let jumps = 0; ; ) {
    const length = buf[offset];
    if (length === 0) {
      return [labels.join("."), end === -1 ? offset + 1 : end];
    }
    if ((length & 0xc0) === 0xc0) {
      if (end === -1) end = offset + 2;
      offset = buf.readUInt16BE(offset) & 0x3fff;
      if (++jumps > 20) throw new Error("compression loop");
      continue;
    }
    labels.push(buf.toString("ascii", offset + 1, offset + 1 + length));
    offset += 1 + length;
  }
}

export interface Answer {
  name: string;
  type: number;
  ttl: number;
  data: string;
}

export interface Message {
  id: number;
  truncated: boolean;
  authoritative: boolean;
  rcode: number; // 0 = no error, 3 = NXDOMAIN (the name doesn't exist)
  question: { name: string; type: number };
  answers: Answer[];
}

export function parseMessage(buf: Buffer): Message {
  const flags = buf.readUInt16BE(2);
  const [qname, afterName] = readName(buf, 12);
  const message: Message = {
    id: buf.readUInt16BE(0),
    truncated: (flags & 0x0200) !== 0,
    authoritative: (flags & 0x0400) !== 0,
    rcode: flags & 0x000f,
    question: { name: qname, type: buf.readUInt16BE(afterName) },
    answers: [],
  };
  let offset = afterName + 4;
  for (let i = 0; i < buf.readUInt16BE(6); i++) {
    const [name, next] = readName(buf, offset);
    const type = buf.readUInt16BE(next);
    const ttl = buf.readUInt32BE(next + 4);
    const length = buf.readUInt16BE(next + 8);
    const rdata = next + 10;
    const data = type === TYPE.A ? [...buf.subarray(rdata, rdata + 4)].join(".") : type === TYPE.CNAME ? readName(buf, rdata)[0] : buf.toString("hex", rdata, rdata + length);
    message.answers.push({ name, type, ttl, data });
    offset = rdata + length;
  }
  return message;
}

export interface ZoneRecord {
  type: number;
  ttl: number;
  data: string; // an IPv4 address for A, a name for CNAME
}

/**
 * A tiny authoritative server on 127.0.0.1 over UDP. It answers from `zone`, follows one CNAME, says NXDOMAIN for
 * unknown names, and sets the TC ("truncated") bit when the answer won't fit in 512 bytes, as classic DNS over UDP must.
 */
export async function startServer(zone: Map<string, ZoneRecord[]>): Promise<{ port: number; queries: number; close: () => void }> {
  const socket = dgram.createSocket("udp4");
  const state = { port: 0, queries: 0, close: () => socket.close() };
  socket.on("message", (query, peer) => {
    state.queries++;
    const { id, question } = parseMessage(query);
    const records: { name: string; record: ZoneRecord }[] = [];
    let name = question.name.toLowerCase();
    for (const r of zone.get(name) ?? []) {
      records.push({ name, record: r });
      if (r.type === TYPE.CNAME && question.type !== TYPE.CNAME) {
        name = r.data;
        for (const target of zone.get(name) ?? []) records.push({ name, record: target });
      }
    }
    const wanted = records.filter((r) => r.record.type === question.type || r.record.type === TYPE.CNAME);
    const body = wanted.map(({ name: n, record }) => {
      const rdata = record.type === TYPE.A ? Buffer.from(record.data.split(".").map(Number)) : encodeName(record.data);
      const fixed = Buffer.alloc(10);
      fixed.writeUInt16BE(record.type, 0);
      fixed.writeUInt16BE(1, 2);
      fixed.writeUInt32BE(record.ttl, 4);
      fixed.writeUInt16BE(rdata.length, 8);
      return Buffer.concat([encodeName(n), fixed, rdata]);
    });
    const questionBytes = query.subarray(12, readName(query, 12)[1] + 4); // exactly the question: anything after it (EDNS0) isn't echoed
    let answerBytes = Buffer.concat(body);
    const truncated = 12 + questionBytes.length + answerBytes.length > 512;
    if (truncated) answerBytes = Buffer.alloc(0); // a truncated UDP reply carries no answers: "ask again over TCP"
    const header = Buffer.alloc(12);
    header.writeUInt16BE(id, 0);
    header.writeUInt16BE(0x8400 | (truncated ? 0x0200 : 0) | (zone.has(question.name.toLowerCase()) ? 0 : 3), 2); // QR, AA, TC, RCODE
    header.writeUInt16BE(1, 4);
    header.writeUInt16BE(truncated ? 0 : body.length, 6);
    socket.send(Buffer.concat([header, questionBytes, answerBytes]), peer.port, peer.address);
  });
  await new Promise<void>((resolve) => socket.bind(0, "127.0.0.1", resolve));
  state.port = socket.address().port;
  return state;
}

/** Sends one query over UDP and waits for the answer. */
export function ask(port: number, query: Buffer): Promise<Message> {
  const socket = dgram.createSocket("udp4");
  return new Promise((resolve, reject) => {
    socket.on("message", (reply) => {
      socket.close();
      resolve(parseMessage(reply));
    });
    socket.on("error", reject);
    socket.send(query, port, "127.0.0.1");
  });
}

/**
 * The iterative walk, against in-memory servers. Each server knows either the answer, or which server to ask next
 * (a delegation). The resolver caches both answers and delegations, so later lookups skip steps.
 */
export class IterativeResolver {
  queries = 0;
  #servers: Map<string, Map<string, string>>; // server → (name or zone → answer, or "→next-server")
  #cache = new Map<string, string>(); // name or zone → answer or delegation

  constructor(servers: Map<string, Map<string, string>>) {
    this.#servers = servers;
  }

  resolve(name: string): string {
    if (this.#cache.has(name)) return this.#cache.get(name)!; // answered from cache: no queries at all
    let server = "root";
    for (const zone of zonesAbove(name)) {
      const delegation = this.#cache.get(zone); // the closest cached delegation saves the walk above it
      if (delegation) server = delegation;
    }
    for (;;) {
      this.queries++;
      const knows = this.#servers.get(server)!;
      const exact = knows.get(name);
      if (exact) {
        this.#cache.set(name, exact);
        return exact;
      }
      const zone = zonesAbove(name).find((z) => knows.has(z))!; // the most specific zone this server delegates
      server = knows.get(zone)!.slice(1);
      this.#cache.set(zone, server);
    }
  }
}

/** "www.example.com" → ["com", "example.com"]: the zones above a name, from the top down. */
function zonesAbove(name: string): string[] {
  const labels = name.split(".");
  return labels.slice(1).map((_, i) => labels.slice(labels.length - 1 - i).join(".")).filter((z) => z !== name);
}

/** A caching stub resolver with a clock: answers live for their TTL, "no such name" for the negative TTL. */
export class CachingResolver {
  upstreamQueries = 0;
  #now: () => number;
  #upstream: (name: string) => { address?: string; ttl: number };
  #cache = new Map<string, { address?: string; expires: number }>();

  constructor(now: () => number, upstream: (name: string) => { address?: string; ttl: number }) {
    this.#now = now;
    this.#upstream = upstream;
  }

  lookup(name: string): string | undefined {
    const hit = this.#cache.get(name);
    if (hit && hit.expires > this.#now()) return hit.address; // fresh: the cached answer wins, right or wrong
    this.upstreamQueries++;
    const { address, ttl } = this.#upstream(name);
    this.#cache.set(name, { address, expires: this.#now() + ttl * 1000 });
    return address;
  }
}

/**
 * The names a resolver tries for `name` with a search list, the way /etc/resolv.conf's `ndots` works: a name with
 * fewer dots than `ndots` is tried with each search domain appended first. A trailing dot means "exactly this name".
 */
export function searchCandidates(name: string, ndots: number, search: string[]): string[] {
  if (name.endsWith(".")) return [name.slice(0, -1)];
  const dots = name.split(".").length - 1;
  const expanded = search.map((domain) => `${name}.${domain}`);
  return dots >= ndots ? [name, ...expanded] : [...expanded, name];
}
