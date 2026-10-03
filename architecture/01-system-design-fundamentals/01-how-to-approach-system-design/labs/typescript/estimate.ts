// estimate.ts — back-of-the-envelope arithmetic for a design, with every assumption written down.
// The answers only need to be right to within a factor of a few: they decide between designs, not budgets.

export const SECONDS_PER_DAY = 86_400; // "about 100,000" is close enough when estimating in your head

export interface Assumptions {
  dailyActiveUsers: number;
  writesPerUserPerDay: number;
  readsPerUserPerDay: number;
  peakToAverage: number; // how much busier the busiest hour is than the day's average
  bytesPerWrite: number; // what each write adds to storage
  keptForDays: number;
  bytesPerRead: number; // the size of one response
}

export interface Estimate {
  writesPerSecond: { average: number; peak: number };
  readsPerSecond: { average: number; peak: number };
  readsPerWrite: number;
  storageBytes: number;
  peakEgressBytesPerSecond: number; // bytes sent to clients a second, at peak
}

export function estimate(a: Assumptions): Estimate {
  const writes = (a.dailyActiveUsers * a.writesPerUserPerDay) / SECONDS_PER_DAY;
  const reads = (a.dailyActiveUsers * a.readsPerUserPerDay) / SECONDS_PER_DAY;
  return {
    writesPerSecond: { average: writes, peak: writes * a.peakToAverage },
    readsPerSecond: { average: reads, peak: reads * a.peakToAverage },
    readsPerWrite: a.readsPerUserPerDay / a.writesPerUserPerDay,
    storageBytes: a.dailyActiveUsers * a.writesPerUserPerDay * a.bytesPerWrite * a.keptForDays,
    peakEgressBytesPerSecond: reads * a.peakToAverage * a.bytesPerRead,
  };
}

/** Bytes to two significant figures, in powers of 1,000 as disks and networks are sold: 912,500,000,000 → "910 GB". */
export function humanBytes(bytes: number): string {
  const units = ["B", "KB", "MB", "GB", "TB", "PB"];
  let i = 0;
  while (bytes >= 1000 && i < units.length - 1) {
    bytes /= 1000;
    i++;
  }
  return `${Number(bytes.toPrecision(2))} ${units[i]}`;
}
