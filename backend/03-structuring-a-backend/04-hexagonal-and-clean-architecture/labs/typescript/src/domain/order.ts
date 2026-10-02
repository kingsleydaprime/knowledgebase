// src/domain/order.ts — entities, rules and ports. Imports nothing outside domain/.
export type Order = { id: string; customerId: string; totalKobo: number; status: "pending" | "paid" };

export class InvalidTotalError extends Error {}
export class PaymentDeclinedError extends Error {}

export function newOrder(id: string, customerId: string, totalKobo: number): Order {
  if (!Number.isInteger(totalKobo) || totalKobo <= 0) throw new InvalidTotalError(`bad total: ${totalKobo}`);
  return { id, customerId, totalKobo, status: "pending" };
}

// Ports: the domain says what it needs, in its own words.
export interface OrderRepository {
  save(order: Order): Promise<void>;
}
export interface PaymentGateway {
  charge(customerId: string, amountKobo: number): Promise<{ ok: true; reference: string } | { ok: false }>;
}
