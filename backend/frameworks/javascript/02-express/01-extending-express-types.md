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