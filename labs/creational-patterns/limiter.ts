// limiter.ts — the same rate limiter, as a singleton and as a factory

// ---- Singleton: one hidden, global instance ----
export class SingletonLimiter {
  static instance: SingletonLimiter | undefined;
  used = new Map<string, number>();
  limit = 3;
  private constructor() {}
  static getInstance(): SingletonLimiter {
    SingletonLimiter.instance ??= new SingletonLimiter();
    return SingletonLimiter.instance;
  }
  allow(userId: string): boolean {
    const n = (this.used.get(userId) ?? 0) + 1;
    this.used.set(userId, n);
    return n <= this.limit;
  }
}

// Business code that reaches for the global — its dependency is invisible in its signature.
export function sendOtpWithSingleton(userId: string): "sent" | "rate-limited" {
  return SingletonLimiter.getInstance().allow(userId) ? "sent" : "rate-limited";
}

// ---- Factory + injection: create as many as you need, pass them in ----
export type Limiter = { allow(userId: string): boolean };

export function createLimiter(limit: number): Limiter {
  const used = new Map<string, number>();
  return {
    allow(userId) {
      const n = (used.get(userId) ?? 0) + 1;
      used.set(userId, n);
      return n <= limit;
    },
  };
}

export function sendOtp(limiter: Limiter, userId: string): "sent" | "rate-limited" {
  return limiter.allow(userId) ? "sent" : "rate-limited";
}
