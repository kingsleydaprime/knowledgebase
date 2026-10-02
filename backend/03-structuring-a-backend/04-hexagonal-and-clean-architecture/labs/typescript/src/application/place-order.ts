// src/application/place-order.ts — one use case. Depends only on the domain.
import { newOrder, PaymentDeclinedError, type Order, type OrderRepository, type PaymentGateway } from "../domain/order.ts";

export function makePlaceOrder(deps: { orders: OrderRepository; payments: PaymentGateway; nextId: () => string }) {
  return async function placeOrder(customerId: string, totalKobo: number): Promise<Order> {
    const order = newOrder(deps.nextId(), customerId, totalKobo);
    const result = await deps.payments.charge(customerId, order.totalKobo);
    if (!result.ok) throw new PaymentDeclinedError(order.id);
    const paid: Order = { ...order, status: "paid" };
    await deps.orders.save(paid);
    return paid;
  };
}
