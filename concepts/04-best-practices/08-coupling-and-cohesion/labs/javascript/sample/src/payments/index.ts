import { db } from "../shared/db";
import { markPaid } from "../orders"; // payments reaches back into orders: a cycle
export const charge = (orderId: string) => { markPaid(orderId); return db; };
