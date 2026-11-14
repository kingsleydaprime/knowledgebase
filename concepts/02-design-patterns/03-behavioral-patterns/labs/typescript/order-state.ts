// order-state.ts — State (which actions are legal now) + Observer (who hears about changes)
export type Status = "pending" | "paid" | "shipped" | "delivered" | "cancelled";
export type Action = "pay" | "ship" | "deliver" | "cancel";

// The State pattern, table form: each state lists the actions it allows and where they lead.
// A state missing from an action's row means "not allowed here".
const transitions: Record<Status, Partial<Record<Action, Status>>> = {
  pending: { pay: "paid", cancel: "cancelled" },
  paid: { ship: "shipped", cancel: "cancelled" },
  shipped: { deliver: "delivered" },
  delivered: {},
  cancelled: {},
};

export class IllegalTransitionError extends Error {}

type Listener = (event: { orderId: string; from: Status; to: Status }) => void;

export class Order {
  id: string;
  status: Status = "pending";
  #listeners: Listener[] = [];

  constructor(id: string) {
    this.id = id;
  }

  // Observer: subscribers register; the order never knows what they do.
  onChange(listener: Listener) {
    this.#listeners.push(listener);
  }

  apply(action: Action) {
    const next = transitions[this.status][action];
    if (!next) throw new IllegalTransitionError(`cannot ${action} an order that is ${this.status}`);
    const from = this.status;
    this.status = next;
    for (const listener of this.#listeners) listener({ orderId: this.id, from, to: next });
  }

  allowedActions(): Action[] {
    return Object.keys(transitions[this.status]) as Action[];
  }
}
