// Unit tests: one module, every collaborator replaced by a test double.
import { test, mock } from "node:test";
import assert from "node:assert/strict";
import { dayAfter, endingTomorrow, sendTrialReminders, tomorrowBuggy } from "./reminders.mjs";

const oct31 = new Date("2026-10-31T12:00:00Z");
const users = [
  { email: "ada@x.com", trialEndsOn: "2026-11-01" },
  { email: "bayo@x.com", trialEndsOn: "2026-11-05" },
];

test("dayAfter rolls over month and year boundaries", () => {
  assert.equal(dayAfter(oct31), "2026-11-01");
  assert.equal(dayAfter(new Date("2026-12-31T23:00:00Z")), "2027-01-01");
  assert.equal(dayAfter(new Date("2028-02-28T00:00:00Z")), "2028-02-29"); // leap year
});

test("endingTomorrow picks only trials ending the day after today", () => {
  assert.deepEqual(endingTomorrow(users, oct31), [users[0]]);
});

test("sendTrialReminders, with a stub, a spy and a fake clock", async () => {
  const stubUsers = { listOnTrial: async () => users };      // STUB: returns canned data
  const mailer = { send: mock.fn(async () => {}) };          // SPY: records every call
  const fakeClock = { now: () => oct31 };                    // FAKE: a working, controllable clock

  const sent = await sendTrialReminders({ users: stubUsers, mailer, clock: fakeClock });

  assert.equal(sent, 1);
  assert.equal(mailer.send.mock.callCount(), 1);
  assert.deepEqual(mailer.send.mock.calls[0].arguments, ["ada@x.com", "Your trial ends tomorrow"]);
});

test("FLAKY: code that reads the real clock passes 30 days a month, then fails", () => {
  mock.timers.enable({ apis: ["Date"], now: new Date("2026-10-14T12:00:00Z") });
  assert.equal(tomorrowBuggy(), "2026-10-15"); // a normal day: looks fine
  mock.timers.setTime(oct31.getTime());
  assert.equal(tomorrowBuggy(), "2026-10-32"); // the 31st: a date that doesn't exist
  mock.timers.reset();
});
