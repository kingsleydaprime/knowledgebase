// fees.mjs — Open/Closed: adding a payment method adds an entry, edits no rule
export const feeRules = {
  card: (amountPence) => Math.round(amountPence * 0.029),
  transfer: () => 50,
};

export function fee(payment, rules = feeRules) {
  const rule = rules[payment.type];
  if (!rule) throw new Error(`no fee rule for ${payment.type}`);
  return rule(payment.amountPence);
}
