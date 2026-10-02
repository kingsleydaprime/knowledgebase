// src/shared/bus.ts — the seam between modules. In-process today; a broker later.
export type PaymentSucceeded = { type: "PaymentSucceeded"; eventId: string; orderId: string; amountKobo: number };
export type Event = PaymentSucceeded;
export type Handler = (event: Event) => Promise<void>;

export interface EventBus {
  publish(event: Event): Promise<void>;
  subscribe(type: Event["type"], handler: Handler): void;
}

export function inProcessBus(): EventBus {
  const handlers: Handler[] = [];
  return {
    subscribe: (_type, handler) => { handlers.push(handler); },
    publish: async (event) => { for (const h of handlers) await h(event); },
  };
}

// What a message broker really promises: at-least-once. This one delivers every event twice.
export function atLeastOnceBus(): EventBus {
  const inner = inProcessBus();
  return {
    subscribe: inner.subscribe,
    publish: async (event) => { await inner.publish(event); await inner.publish(event); },
  };
}
