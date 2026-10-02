// src/adapters/in-memory.ts — driven adapters. They import the domain; never the reverse.
import type { Order, OrderRepository, PaymentGateway } from "../domain/order.ts";

export class InMemoryOrders implements OrderRepository {
  saved: Order[] = [];
  async save(order: Order) {
    this.saved.push(order);
  }
}

export class FakePayments implements PaymentGateway {
  declineAbove: number;
  constructor(declineAbove: number) {
    this.declineAbove = declineAbove;
  }
  async charge(_customerId: string, amountKobo: number) {
    return amountKobo > this.declineAbove ? { ok: false as const } : { ok: true as const, reference: "ref_1" };
  }
}
