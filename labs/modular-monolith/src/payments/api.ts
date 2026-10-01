// src/payments/api.ts — the only file other modules may import from payments/
import type { EventBus } from "../shared/bus.ts";

export function makePayments(bus: EventBus) {
  let n = 0;
  return {
    async recordSuccess(orderId: string, amountKobo: number) {
      n++;
      await bus.publish({ type: "PaymentSucceeded", eventId: `evt_${n}`, orderId, amountKobo });
    },
  };
}
