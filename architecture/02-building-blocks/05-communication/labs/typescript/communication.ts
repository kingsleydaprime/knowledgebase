// communication.ts — what an API style costs, counted: requests, round trips and bytes for one screen fetched with
// REST and with a GraphQL-style query; the N+1 queries a naive resolver makes and the batching that fixes them;
// how Protocol Buffers encode a message in fewer bytes than JSON; and what calling services in a chain does.

export interface Customer { id: string; name: string; email: string; address: string }
export interface Product { id: string; name: string; pricePence: number; description: string }
export interface Order { id: string; customerId: string; items: { productId: string; quantity: number }[]; totalPence: number }

/** A tiny shop database that counts its queries. */
export class Db {
  queries = 0;
  customers = new Map<string, Customer>();
  products = new Map<string, Product>();
  orders = new Map<string, Order>();

  findOrders(ids: readonly string[]): Order[] {
    this.queries++;
    return ids.map((id) => this.orders.get(id)!);
  }

  /** One query for any number of customers: SELECT … WHERE id IN (…). */
  findCustomers(ids: readonly string[]): Customer[] {
    this.queries++;
    return ids.map((id) => this.customers.get(id)!);
  }

  findProducts(ids: readonly string[]): Product[] {
    this.queries++;
    return ids.map((id) => this.products.get(id)!);
  }
}

/** A REST API over the database: one resource per URL, always returned whole. It counts requests and bytes sent. */
export class RestApi {
  requests = 0;
  bytes = 0;
  #db: Db;

  constructor(db: Db) {
    this.#db = db;
  }

  get(path: string): unknown {
    const [, kind, id] = path.split("/"); // "/orders/o1" → "orders", "o1"
    const body =
      kind === "orders" ? this.#db.findOrders([id])[0]
      : kind === "customers" ? this.#db.findCustomers([id])[0]
      : kind === "products" ? this.#db.findProducts([id])[0]
      : undefined;
    if (body === undefined) throw new Error(`404 ${path}`);
    this.requests++;
    this.bytes += JSON.stringify(body).length;
    return body;
  }
}

/** What the order screen shows: the order, who placed it, and each item's name and quantity. */
export interface OrderScreen {
  id: string;
  totalPence: number;
  customer: { name: string };
  items: { quantity: number; product: { name: string } }[];
}

/**
 * The order screen over REST. The order must arrive before we know which customer and products to ask for, so
 * that's one round trip; the rest can then go out together, a second round trip. Done one at a time, it's five.
 */
export function orderScreenRest(api: RestApi, orderId: string): { screen: OrderScreen; roundTrips: number } {
  const order = api.get(`/orders/${orderId}`) as Order; // round trip 1
  const customer = api.get(`/customers/${order.customerId}`) as Customer; // round trip 2, sent together with...
  const products = order.items.map((i) => api.get(`/products/${i.productId}`) as Product); // ...these
  const screen = {
    id: order.id,
    totalPence: order.totalPence,
    customer: { name: customer.name },
    items: order.items.map((item, n) => ({ quantity: item.quantity, product: { name: products[n].name } })),
  };
  return { screen, roundTrips: 2 };
}

/** A selection of fields, GraphQL-style: `true` for a plain field, a nested selection for an object or a list. */
export type Selection = { [field: string]: true | Selection };

/** How to fetch a field that isn't stored on the object itself: a customer from an order's customerId, and so on. */
export type Resolvers = Record<string, (parent: any) => Promise<unknown>>;

/**
 * Runs a selection against a value, returning only the fields asked for. A field with a resolver is fetched;
 * otherwise it's read from the object. Lists are resolved element by element, all at once.
 */
export async function execute(value: any, selection: Selection, resolvers: Resolvers, type: string): Promise<any> {
  if (Array.isArray(value)) return Promise.all(value.map((v) => execute(v, selection, resolvers, type)));
  const out: Record<string, unknown> = {};
  await Promise.all(
    Object.entries(selection).map(async ([field, sub]) => {
      const resolver = resolvers[`${type}.${field}`];
      const child = resolver ? await resolver(value) : value[field];
      out[field] = sub === true ? child : await execute(child, sub, resolvers, FIELD_TYPES[`${type}.${field}`]);
    }),
  );
  return Object.fromEntries(Object.keys(selection).map((f) => [f, out[f]])); // fields in the order asked for
}

const FIELD_TYPES: Record<string, string> = { "Order.customer": "Customer", "Order.items": "Item", "Item.product": "Product" };

/**
 * Collects every key asked for while the current work is running, then fetches them all in one batch. This is
 * the DataLoader pattern: a resolver still asks for one customer, but the database sees one query for all of them.
 */
export class DataLoader<V> {
  #fetch: (keys: string[]) => V[];
  #waiting: { key: string; resolve: (v: V) => void }[] = [];

  constructor(fetch: (keys: string[]) => V[]) {
    this.#fetch = fetch;
  }

  load(key: string): Promise<V> {
    return new Promise((resolve) => {
      this.#waiting.push({ key, resolve });
      if (this.#waiting.length === 1) setImmediate(() => this.#dispatch()); // after everything already queued has run
    });
  }

  #dispatch(): void {
    const batch = this.#waiting;
    this.#waiting = [];
    const keys = [...new Set(batch.map((w) => w.key))]; // each key once, however many asked for it
    const fetched = this.#fetch(keys);
    const values = new Map(keys.map((k, i) => [k, fetched[i]]));
    for (const w of batch) w.resolve(values.get(w.key)!);
  }
}

/** Resolvers that fetch one row at a time (the N+1 problem), or through DataLoaders (one query per kind). */
export function resolvers(db: Db, batched: boolean): Resolvers {
  if (!batched) {
    return {
      "Order.customer": async (o: Order) => db.findCustomers([o.customerId])[0],
      "Item.product": async (i: { productId: string }) => db.findProducts([i.productId])[0],
    };
  }
  const customers = new DataLoader((ids) => db.findCustomers(ids));
  const products = new DataLoader((ids) => db.findProducts(ids));
  return {
    "Order.customer": (o: Order) => customers.load(o.customerId),
    "Item.product": (i: { productId: string }) => products.load(i.productId),
  };
}

/** A base-128 varint, as Protocol Buffers write integers: 7 bits a byte, low bits first, top bit set if more follow. */
export function varint(n: number): number[] {
  if (!Number.isInteger(n) || n < 0) throw new RangeError("varint takes a whole number from 0");
  const bytes: number[] = [];
  do {
    let byte = n % 128;
    n = Math.floor(n / 128); // not >>> 7, which would cut n to 32 bits
    if (n > 0) byte += 128;
    bytes.push(byte);
  } while (n > 0);
  return bytes;
}

/**
 * Encodes `message OrderSummary { uint32 id = 1; string customer = 2; uint32 total_pence = 3; }`. Each field is
 * a tag (field number × 8 + wire type: 0 for a varint, 2 for length-prefixed bytes) followed by its value.
 */
export function encodeOrderSummary(m: { id: number; customer: string; totalPence: number }): number[] {
  const text = [...new TextEncoder().encode(m.customer)];
  return [
    ...varint((1 << 3) | 0), ...varint(m.id),
    ...varint((2 << 3) | 2), ...varint(text.length), ...text,
    ...varint((3 << 3) | 0), ...varint(m.totalPence),
  ];
}

/** Calls one after another: all must be up (availabilities multiply) and their times add up. */
export function chain(services: readonly { availability: number; ms: number }[]) {
  return {
    availability: services.reduce((a, s) => a * s.availability, 1),
    sequentialMs: services.reduce((t, s) => t + s.ms, 0),
    parallelMs: Math.max(...services.map((s) => s.ms)), // only if the calls don't depend on each other
  };
}
