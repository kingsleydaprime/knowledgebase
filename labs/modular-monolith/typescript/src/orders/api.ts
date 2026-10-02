// src/orders/api.ts — orders reacts to payments without importing payments/ at all
import type { EventBus } from "../shared/bus.ts";

export function makeOrders(bus: EventBus, options: { idempotent: boolean }) {
  const paidKobo = new Map<string, number>(); // orders' own table: nobody else touches it
  const seen = new Set<string>();

  bus.subscribe("PaymentSucceeded", async (event) => {
    if (options.idempotent) {
      if (seen.has(event.eventId)) return; // already handled this exact event
      seen.add(event.eventId);
    }
    paidKobo.set(event.orderId, (paidKobo.get(event.orderId) ?? 0) + event.amountKobo);
  });

  return { paidSoFar: (orderId: string) => paidKobo.get(orderId) ?? 0 };
}
