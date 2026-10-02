// support-tools.ts — three tools over a small order store: two that read, one that pays out money.
import { readFileSync } from "node:fs";
import type { JsonSchema, Tool } from "./tools.ts";

type Refund = { status: string; amount: number; requested?: string; paid?: string } | null;
export type Order = { status: string; total: number; tracking?: string; refund: Refund; note?: string };

export function loadOrders(): Record<string, Order> {
  return JSON.parse(readFileSync(new URL("../shared/orders.json", import.meta.url), "utf8"));
}

const orderIdField: JsonSchema = { type: "string", pattern: "^[A-Z][0-9]{3}$", description: "Like A123: one capital letter, three digits" };
const orderId: JsonSchema = { type: "object", properties: { order_id: orderIdField }, required: ["order_id"], additionalProperties: false };

export function supportTools(orders: Record<string, Order>): Tool[] {
  const find = (id: unknown) => {
    const order = orders[id as string];
    if (!order) throw new Error(`no order ${id}`);
    return order;
  };
  return [
    {
      name: "get_order",
      description: "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
      inputSchema: orderId,
      sideEffects: false,
      run: ({ order_id }) => {
        const { refund, ...order } = find(order_id); // return only what this tool is for
        return order;
      },
    },
    {
      name: "get_refund",
      description: "Look up the refund on an order, if there is one: its status, amount and dates.",
      inputSchema: orderId,
      sideEffects: false,
      run: ({ order_id }) => find(order_id).refund ?? { status: "none" },
    },
    {
      name: "issue_refund",
      description: "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
      inputSchema: {
        type: "object",
        properties: { order_id: orderIdField, amount: { type: "number", minimum: 0.01 } },
        required: ["order_id", "amount"],
        additionalProperties: false,
      },
      sideEffects: true,
      run: ({ order_id, amount }) => {
        const order = find(order_id);
        if (order.refund) throw new Error(`order ${order_id} already has a refund`);
        if ((amount as number) > order.total) throw new Error(`refund ${amount} is more than the order total ${order.total}`);
        order.refund = { status: "processing", amount: amount as number, requested: "today" };
        return order.refund;
      },
    },
  ];
}
