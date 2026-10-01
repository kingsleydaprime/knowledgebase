// orders.ts — three layers, no framework. Run the tests with: node --test
export type Item = { sku: string; quantity: number };
export type Order = { id: number; userId: string; items: Item[] };

// ---- domain errors: the service's vocabulary, not HTTP's ----
export class EmptyOrderError extends Error {}
export class OutOfStockError extends Error {
  sku: string;
  constructor(sku: string) {
    super(`out of stock: ${sku}`);
    this.sku = sku;
  }
}

// ---- repository: the only code that knows how data is stored ----
export interface OrdersRepository {
  stockOf(sku: string): number;
  reserve(sku: string, quantity: number): void;
  create(userId: string, items: Item[]): Order;
}

export function inMemoryRepository(stock: Record<string, number>): OrdersRepository {
  const orders: Order[] = [];
  return {
    stockOf: (sku) => stock[sku] ?? 0,
    reserve: (sku, quantity) => { stock[sku] -= quantity; },
    create: (userId, items) => {
      const order = { id: orders.length + 1, userId, items };
      orders.push(order);
      return order;
    },
  };
}

// ---- service: the business rules; knows nothing about HTTP ----
export function makeOrdersService(repo: OrdersRepository) {
  return {
    place(userId: string, items: Item[]): Order {
      if (items.length === 0) throw new EmptyOrderError("an order needs at least one item");
      for (const item of items) {
        if (repo.stockOf(item.sku) < item.quantity) throw new OutOfStockError(item.sku);
      }
      for (const item of items) repo.reserve(item.sku, item.quantity);
      return repo.create(userId, items);
    },
  };
}

// ---- controller: HTTP in, HTTP out; maps domain errors to status codes ----
type HttpRequest = { userId: string; body: { items?: Item[] } };
type HttpResponse = { status: number; body: unknown };

export function makeOrdersController(service: ReturnType<typeof makeOrdersService>) {
  return {
    create(req: HttpRequest): HttpResponse {
      try {
        const order = service.place(req.userId, req.body.items ?? []);
        return { status: 201, body: { id: order.id } };
      } catch (err) {
        if (err instanceof EmptyOrderError) return { status: 400, body: { error: err.message } };
        if (err instanceof OutOfStockError) return { status: 409, body: { error: err.message, sku: err.sku } };
        throw err; // unknown errors are bugs: let the framework turn them into a 500
      }
    },
  };
}
