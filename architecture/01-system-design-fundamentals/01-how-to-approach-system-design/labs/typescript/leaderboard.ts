// leaderboard.ts — the deep dive: "what's my rank?" among millions of players, answered in about 20 steps.
// Scores are whole numbers from 0 to maxScore. A Fenwick tree (binary indexed tree) keeps, for each score,
// how many players have it, arranged so that "how many players scored at most s" takes log2(maxScore) steps.

export class Leaderboard {
  private readonly best = new Map<string, number>(); // each player's best score
  private readonly tree: number[];
  private readonly maxScore: number;
  steps = 0; // the work the last rank() did, to compare with scanning every player

  constructor(maxScore: number) {
    this.maxScore = maxScore;
    this.tree = new Array<number>(maxScore + 2).fill(0);
  }

  get players(): number {
    return this.best.size;
  }

  /** Records a score. Only a player's best counts, so a lower score changes nothing and returns false. */
  submit(player: string, score: number): boolean {
    if (!Number.isInteger(score) || score < 0 || score > this.maxScore) {
      throw new RangeError(`score must be a whole number from 0 to ${this.maxScore}, got ${score}`);
    }
    const old = this.best.get(player);
    if (old !== undefined && score <= old) return false;
    if (old !== undefined) this.add(old, -1);
    this.add(score, +1);
    this.best.set(player, score);
    return true;
  }

  /** 1 + the number of players with a strictly higher best score, so tied players share a rank. */
  rank(player: string): number | undefined {
    const score = this.best.get(player);
    if (score === undefined) return undefined;
    this.steps = 0;
    return 1 + this.players - this.countAtMost(score);
  }

  private add(score: number, delta: number): void {
    for (let i = score + 1; i < this.tree.length; i += i & -i) this.tree[i] += delta;
  }

  private countAtMost(score: number): number {
    let count = 0;
    for (let i = score + 1; i > 0; i -= i & -i) {
      count += this.tree[i];
      this.steps++;
    }
    return count;
  }
}

/** The obvious way, and what `SELECT COUNT(*) … WHERE score > $mine` does without help: look at everyone. */
export function rankByScan(scores: Iterable<number>, mine: number): { rank: number; steps: number } {
  let higher = 0;
  let steps = 0;
  for (const s of scores) {
    steps++;
    if (s > mine) higher++;
  }
  return { rank: 1 + higher, steps };
}
