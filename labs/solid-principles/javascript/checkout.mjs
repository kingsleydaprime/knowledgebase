// checkout.mjs — Dependency Inversion: the rule asks for what it needs
import { fee } from "./fees.mjs";

export function makeCheckout({ payments, receipts }) {
  return async function checkout(order) {
    const charge = order.totalPence + fee(order.payment);
    const ref = await payments.charge(order.customerId, charge);
    await receipts.send(order.customerId, `Charged ${charge}p (ref ${ref})`);
    return { charge, ref };
  };
}
