# End-to-End Testing Overview

End-to-end (E2E) testing validates your entire application flow from the user's perspective, testing the complete stack - frontend, backend, database, APIs, and third-party services - working together as a system.

## When to Use E2E Tests

Use E2E tests for:

- Critical user journeys (signup, checkout, authentication)
- Multi-step workflows that span multiple pages/components
- Integration between frontend and real backend services
- Validating third-party service integrations
- Smoke tests for production deployments

Don't use E2E tests for:

- Unit-level logic (use unit tests)
- Component behavior in isolation (use component tests)
- Edge cases that are expensive to set up (mock these in integration tests)

E2E tests are slower and more brittle than other test types, so you want fewer of them covering critical paths rather than trying to test everything.

## Best Practice Workflow

1. Test Structure

```
tests/
├── e2e/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   └── signup.spec.ts
│   ├── checkout/
│   │   └── purchase-flow.spec.ts
│   └── fixtures/
│       └── test-data.ts
```

2. Writing Tests

- Test user flows, not implementation details
- Use data attributes (`data-testid`) rather than CSS selectors
- Avoid hard-coded waits; use smart waiting mechanisms
- Make tests independent - each test should set up and tear down its own state
- Use Page Object Model pattern for maintainability

3. Test Execution Strategy

- Run E2E tests against staging/test environments
- Parallel execution to reduce CI time
- Retry flaky tests automatically (but fix flakiness root causes)
- Run smoke tests on every deploy, full suite on schedule or pre-release

4. Data Management

- Seed test database with known state before tests
- Use factory functions to generate test data
- Clean up after tests (or use transaction rollbacks)
- Consider using separate test accounts/data for parallel runs

## Tools for Next.js

Primary Options:

Playwright (recommended for most cases)

- Built by Microsoft, excellent Next.js support
- Fast, reliable, great debugging tools
- Multi-browser testing (Chromium, Firefox, WebKit)
- Built-in test runner with parallelization
- API testing capabilities

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  webServer: {
    command: 'npm run dev',
    port: 3000,
  },
  use: {
    baseURL: 'http://localhost:3000',
  },
});

// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('user can log in', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'user@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

Cypress

- Popular, mature ecosystem
- Great developer experience with time-travel debugging
- Excellent documentation and community
- More opinionated than Playwright
- Historically had some architectural limitations (improving with newer versions)

```typescript
// cypress/e2e/login.cy.ts
describe('Login', () => {
  it('allows user to log in', () => {
    cy.visit('/login');
    cy.get('[data-testid="email"]').type('user@example.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});
```

Supporting Tools:

- Testing Library - Use alongside Playwright/Cypress for better selectors and assertions
- MSW (Mock Service Worker) - Mock API responses for deterministic tests
- Faker.js - Generate realistic test data
- Testcontainers - Spin up real dependencies (databases, Redis) in Docker for tests

## Example Best-Practice Setup

```typescript
// tests/e2e/fixtures/auth.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // Login once and reuse authentication state
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="submit"]');
    await page.waitForURL('/dashboard');
    
    await use(page);
  },
});

// tests/e2e/checkout.spec.ts
import { test } from './fixtures/auth';
import { expect } from '@playwright/test';

test('complete checkout flow', async ({ authenticatedPage: page }) => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart-1"]');
  await page.click('[data-testid="cart-icon"]');
  await page.click('[data-testid="checkout"]');
  
  // Fill shipping info
  await page.fill('[name="address"]', '123 Main St');
  await page.fill('[name="city"]', 'San Francisco');
  
  // Complete payment
  await page.fill('[name="cardNumber"]', '4242424242424242');
  await page.click('[data-testid="submit-payment"]');
  
  // Verify success
  await expect(page.locator('[data-testid="order-confirmation"]'))
    .toBeVisible();
});
```

The key is balancing coverage with maintainability - focus on critical paths, keep tests stable and fast, and supplement with lower-level tests for detailed logic.

## Tagging

You can tag tests w/ `@smoke` etc to run subsets of e2e tests as needed.

- This is ideal in CI workflows where you want fast feedback on critical paths after each commit, but not run the full suite.
- When you merge to `main`, you can run the full suite to ensure everything is solid before deploying.

``` typescript
// tests/e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';

// Critical smoke test - runs on every PR
test('user can log in @smoke', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="submit"]');
  await expect(page).toHaveURL('/dashboard');
});

// Full test - only runs on merge
test('shows validation errors for invalid credentials', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'wrong@example.com');
  await page.fill('[data-testid="password"]', 'wrongpass');
  await page.click('[data-testid="submit"]');
  await expect(page.locator('[data-testid="error"]'))
    .toContainText('Invalid credentials');
});
```

## Environment Strategies

There are 2 strategies for running e2e tests in a CI / CD pipeline:

1. Local Test Environment
2. Deployed Environment (Staging, Production etc)

A local test environment is spun up as part of the CI process. This can be done using Docker Compose, Testcontainers, or similar tools to create a full stack environment that mimics production.

- This is simple and allows for fast feedback on PRs, but may not catch environment-specific issues.

A deployed environment involves running e2e tests against a staging or production deployment. This ensures tests run in a real-world environment w/ real integrations, catching deployment-specific issues.

- This is more complex and slower, so it's often reserved for smoke tests on every deploy and full suites on scheduled runs or pre-release.

The sweet spot is often a hybrid approach: run critical smoke tests against a local test environment on every PR, and run the full suite against a deployed staging environment on merges or scheduled runs.

- You can also set up ephemeral staging environments per PR using tools like Vercel or Netlify for more realistic testing as needed. 
- If you have a complex PR with significant changes, simply label the PR w/ `ephemeral` and CI can spin up a full staging environment for that PR only.
