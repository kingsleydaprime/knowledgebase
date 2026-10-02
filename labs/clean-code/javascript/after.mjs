// after.mjs
const LOYAL_CUSTOMER_MIN_ORDERS = 10;
const LOYALTY_DISCOUNT = 0.1;

export function validateOrder(order) {
  if (!order || order.items.length === 0) throw new Error("bad order");
}

export function subtotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function isLoyal(customer) {
  return customer.active && customer.orderCount > LOYAL_CUSTOMER_MIN_ORDERS;
}

export function applyLoyaltyDiscount(amount, customer) {
  if (!isLoyal(customer)) return amount;
  return amount * (1 - LOYALTY_DISCOUNT);
}

// Store money in whole pence: floating-point pounds drift (0.1 + 0.2 !== 0.3).
export function toPence(pounds) {
  return Math.round(pounds * 100);
}

export function placeOrder(order, { orders, mailer }) {
  validateOrder(order);
  const totalPence = toPence(applyLoyaltyDiscount(subtotal(order.items), order.customer));
  orders.push({ id: order.id, totalPence });
  mailer.push({ to: order.customer.email, body: `Your total is ${totalPence}p` });
  return totalPence;
}
