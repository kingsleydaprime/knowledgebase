# NextVibe — Frontend Testing Strategy

Created 2026-10-13. See also `learning/frontend/01-routing.md` through
`learning/frontend/12-rtk-query-and-api-slices.md` for the rest of the frontend
architecture, and the backend testing notes at [[projects/nextvibe/learning/backend/09-testing|09 — Backend Testing]].

---

## 1. Frontend Testing Layers

NextVibe's frontend is built with **Next.js 16 (App Router)**, **React 19**, **Redux Toolkit & RTK Query**, **Tailwind CSS 4**, and **react-hook-form + Zod**.

Testing this architecture requires three complementary tiers:

```
        / \
       /   \        E2E Tests (Playwright)
      / E2E \       Full user journeys in a real browser: auth, RSVP, payment flows
     /-------\
    /         \     Component / Integration Tests (Vitest + React Testing Library)
   / Component \    Form validation feedback, modal behaviors, store integration
  /-------------\
 /               \  Unit Tests (Vitest)
/      Unit       \ Pure business logic: Zod schemas, Redux reducers, formatters
-------------------
```

---

## 2. Setting Up Vitest for Next.js

Vitest is preferred over Jest for modern Next.js App Router applications because:
- Native ESM support without complex Babel or SWC transform configuration.
- Shares configuration plugins with Vite.
- Fast watch mode and multithreading.
- Identical `describe`/`it`/`expect` API as Jest.

### Installation
```bash
cd frontend
pnpm add -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Configuration (`vitest.config.ts`)
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: false, // Skip CSS parsing for speed
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### Test Setup (`src/test/setup.ts`)
```typescript
import '@testing-library/jest-dom/vitest';
```

---

## 3. Tier 1: Unit Testing Schemas & State

Pure functions represent high-confidence, low-maintenance testing wins.

### 1. Zod Validation Schemas
Form schemas protect endpoints from invalid client submissions. Testing these confirms error messaging and field constraints without touching React components:

```typescript
// src/features/auth/__tests__/login-schema.test.ts
import { describe, it, expect } from 'vitest';
import { z } from 'zod';

// Example matching schema definition
const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

describe('loginSchema validation', () => {
  it('accepts valid credentials', () => {
    const result = loginSchema.safeParse({
      email: 'user@example.com',
      password: 'SecurePassword123!',
    });
    expect(result.success).toBe(true);
  });

  it('rejects malformed email addresses', () => {
    const result = loginSchema.safeParse({
      email: 'invalid-email',
      password: 'SecurePassword123!',
    });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toMatch(/valid email/i);
    }
  });
});
```

### 2. Redux Slice Reducers
Testing slices ensures state transitions behave deterministically:

```typescript
// src/store/slices/__tests__/user.test.ts
import { describe, it, expect } from 'vitest';
import userReducer, { setUser, clearUser } from '../user';

describe('user slice reducer', () => {
  it('handles initial state', () => {
    expect(userReducer(undefined, { type: 'unknown' })).toEqual({
      user: null,
      isAuthenticated: false,
    });
  });

  it('sets user payload and sets isAuthenticated to true', () => {
    const mockUser = { id: 'u1', email: 'test@example.com', name: 'Alex' };
    const state = userReducer(undefined, setUser(mockUser));
    expect(state.user).toEqual(mockUser);
    expect(state.isAuthenticated).toBe(true);
  });

  it('clears user data on logout', () => {
    const activeState = { user: { id: 'u1' }, isAuthenticated: true };
    const state = userReducer(activeState as any, clearUser());
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });
});
```

---

## 4. Tier 2: Component Testing with React Testing Library

The core principle of Testing Library is:
> *The more your tests resemble the way your software is used, the more confidence they can give you.*

Never assert private component state or internal hooks. Query elements via user-visible accessibility roles (`getByRole`, `getByLabelText`, `getByText`).

### Rendering Components with Redux & RTK Query
Components consuming RTK Query hooks need a Redux `Provider` wrapping them:

```tsx
// src/test/test-utils.tsx
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { baseApi } from '@/store/api/baseApi';
import userReducer from '@/store/slices/user';

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) {
  const store = configureStore({
    reducer: {
      [baseApi.reducerPath]: baseApi.reducer,
      user: userReducer,
    },
    middleware: (gDM) => gDM().concat(baseApi.middleware),
  });

  function Wrapper({ children }: { children: React.ReactNode }) {
    return <Provider store={store}>{children}</Provider>;
  }

  return { store, ...render(ui, { wrapper: Wrapper, ...options }) };
}
```

---

## 5. Mocking APIs with MSW (Mock Service Worker)

Instead of mocking RTK Query hooks directly, intercept HTTP calls at the network layer using **MSW**:
- Tests verify full serialization, caching, error transforms, and RTK Query state lifecycle (`isLoading`, `isError`, `data`).

```typescript
// src/test/mocks/server.ts
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('*/v1/events', () => {
    return HttpResponse.json({
      data: [
        { id: 'evt-1', title: 'Afrobeats Festival', date: '2026-12-01' },
      ],
    });
  }),
];

export const server = setupServer(...handlers);
```

Hook it into test lifecycles in `src/test/setup.ts`:
```typescript
import { server } from './mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

---

## 6. Tier 3: End-to-End Testing with Playwright

Playwright runs real Chromium, WebKit, and Firefox engines against your deployed or local build.

### Installation
```bash
pnpm add -D @playwright/test
npx playwright install
```

### Core Playwright Test: Discovery to RSVP Flow
```typescript
// e2e/events.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Event Discovery and Details', () => {
  test('unauthenticated visitor can browse events and open an event page', async ({ page }) => {
    // Navigate to events index
    await page.goto('/events');

    // Confirm heading is rendered
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

    // Select the first event card
    const firstCard = page.locator('article, [data-testid="event-card"]').first();
    await expect(firstCard).toBeVisible();
    await firstCard.click();

    // Verify detail route navigation
    await expect(page).toHaveURL(/\/events\/[a-zA-Z0-9-]+/);
    await expect(page.getByRole('button', { name: /rsvp|buy ticket/i })).toBeVisible();
  });
});
```

---

## 7. What NOT to Test on the Frontend

1. **Third-party component internals**: Do not test Radix UI's keyboard navigation or Tailwind's CSS rule generation.
2. **Next.js internals**: Do not test whether App Router correctly handles server-side streaming or cookie serialization.
3. **Pixel-perfect layout in unit tests**: Assert presence, accessibility states, and text content. Use Playwright visual regression snapshots for pixel checks if strictly necessary.

---

## Related
- [[projects/nextvibe/learning/frontend/02-state-management|02 — Frontend State Management]]
- [[projects/nextvibe/learning/frontend/12-rtk-query-and-api-slices|12 — RTK Query & API Slices]]
- [[projects/nextvibe/learning/backend/09-testing|09 — Backend Testing]]
- [[backend/07-practices/03-load-and-performance-testing|Load & Performance Testing]]
