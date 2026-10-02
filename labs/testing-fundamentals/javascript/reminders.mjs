// reminders.mjs — email users whose free trial ends tomorrow.

// Dates are "YYYY-MM-DD" strings in UTC, so comparisons are plain string equality.
export function dayAfter(date) {
  const next = new Date(date.getTime());
  next.setUTCDate(next.getUTCDate() + 1); // rolls over months and years correctly
  return next.toISOString().slice(0, 10);
}

// BUG, kept on purpose: reads the real clock and does date arithmetic by hand.
export function tomorrowBuggy() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${now.getUTCFullYear()}-${pad(now.getUTCMonth() + 1)}-${pad(now.getUTCDate() + 1)}`;
}

export function endingTomorrow(users, today) {
  const target = dayAfter(today);
  return users.filter((user) => user.trialEndsOn === target);
}

// Everything it touches is passed in: where users come from, how mail is sent, what "now" is.
export async function sendTrialReminders({ users, mailer, clock }) {
  const due = endingTomorrow(await users.listOnTrial(), clock.now());
  for (const user of due) {
    await mailer.send(user.email, "Your trial ends tomorrow");
  }
  return due.length;
}
