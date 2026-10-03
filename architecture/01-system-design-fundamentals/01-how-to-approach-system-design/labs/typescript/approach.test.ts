import { test } from "node:test";
import assert from "node:assert/strict";
import { estimate, humanBytes } from "./estimate.ts";
import { Leaderboard, rankByScan } from "./leaderboard.ts";

// The worked example: a leaderboard for a mobile game with 10 million daily players.
const game = estimate({
  dailyActiveUsers: 10_000_000,
  writesPerUserPerDay: 5, // five games a day, one score each
  readsPerUserPerDay: 10, // the leaderboard opened ten times a day
  peakToAverage: 3, // evenings are three times the daily average
  bytesPerWrite: 50, // player id, score, time, and some overhead
  keptForDays: 365, // a year of score history
  bytesPerRead: 2_000, // the top 100, about 20 bytes each
});

test("the estimate: order of magnitude, not precision", () => {
  assert.equal(Math.round(game.writesPerSecond.average), 579);
  assert.equal(Math.round(game.writesPerSecond.peak), 1736);
  assert.equal(Math.round(game.readsPerSecond.peak), 3472);
  assert.equal(game.readsPerWrite, 2); // read-heavy, but not overwhelmingly
  assert.equal(humanBytes(game.storageBytes), "910 GB"); // history fits on one disk
  assert.equal(humanBytes(game.peakEgressBytesPerSecond), "6.9 MB"); // a second: small
});

test("why the obvious rank query can't work at this scale", () => {
  const players = 50_000_000; // everyone who has ever played has a best score
  const comparisonsPerSecond = Math.round(game.readsPerSecond.peak) * players; // a full scan per rank lookup
  assert.equal(comparisonsPerSecond, 173_600_000_000); // 1.7 × 10^11 a second: no single database does this
  assert.equal(humanBytes(players * 100), "5 GB"); // best scores at ~100 bytes each fit in memory on one machine
});

test("ranks: ties share a rank, and only a player's best score counts", () => {
  const board = new Leaderboard(1_000);
  board.submit("ada", 100);
  board.submit("bo", 250);
  board.submit("cy", 250);
  board.submit("di", 90);
  assert.deepEqual(["bo", "cy", "ada", "di"].map((p) => board.rank(p)), [1, 1, 3, 4]);
  assert.equal(board.submit("ada", 80), false); // lower than her best: ignored
  assert.equal(board.rank("ada"), 3);
  assert.equal(board.submit("ada", 300), true);
  assert.deepEqual(["ada", "bo", "cy", "di"].map((p) => board.rank(p)), [1, 2, 2, 4]);
  assert.equal(board.rank("nobody"), undefined);
  assert.throws(() => board.submit("ed", 1_001), RangeError);
  assert.throws(() => board.submit("ed", 2.5), RangeError);
});

test("the deep dive pays off: about 20 steps instead of one per player", () => {
  const maxScore = 1_000_000;
  const board = new Leaderboard(maxScore);
  const scores: number[] = [];
  for (let i = 0; i < 200_000; i++) {
    const score = (i * 7_919) % (maxScore + 1); // spread out, and the same on every run
    scores.push(score);
    board.submit(`p${i}`, score);
  }
  for (const i of [0, 1, 12_345, 199_999]) {
    const scan = rankByScan(scores, scores[i]);
    assert.equal(board.rank(`p${i}`), scan.rank); // the same answer...
    assert.ok(board.steps <= 20, `${board.steps} steps`); // ...in at most log2(1,000,001) ≈ 20 steps
    assert.equal(scan.steps, 200_000); // ...where the scan looks at every player
  }
});
