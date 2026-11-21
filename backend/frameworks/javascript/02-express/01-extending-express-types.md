---
id: 73b7dfa1-7c7c-45ed-aeb2-c50d1c436dea
---

# Extending express types

`express.d.ts`

```ts
declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        email: string;
        role?: "sponsor" | "attendee" | "organizer";
        serverRole?: "user" | "admin";
        // sub: string;
      };
    }
  }
}

export {};

```