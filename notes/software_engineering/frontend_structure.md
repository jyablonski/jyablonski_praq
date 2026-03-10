# Frontend Structure

______________________________________________________________________

## Zod: Runtime Validation + Static Types

Zod is a schema declaration and validation library for TypeScript. The core problem it solves: TypeScript's type system only exists at compile time. Once code is running, types are gone. Zod bridges that gap by letting you define a schema once and get both runtime validation and a static TypeScript type from the same source.

### Basic Usage

```ts
import { z } from "zod";

const UserSchema = z.object({
  name: z.string(),
  age: z.number().min(0),
  email: z.string().email(),
});

// Runtime validation — throws on invalid data
const user = UserSchema.parse(someUnknownData);

// Safe alternative — returns { success, data, error } instead of throwing
const result = UserSchema.safeParse(someUnknownData);

// Static type inference — no need to write a separate type
type User = z.infer<typeof UserSchema>;
// => { name: string; age: number; email: string }
```

### Why It Matters

- **API response validation**: Instead of `response.json() as User` (blind cast, no runtime safety), parse through a Zod schema and get both validation and type inference.
- **Form validation**: First-class integration with React Hook Form and similar libraries.
- **Environment variables**: Validate `process.env` at startup so missing/malformed config fails fast.
- **Trust boundaries**: Any time data enters your system from an external source, Zod ensures it matches expectations.

### Additional Features

- **Transforms**: Parse a string into a number, trim whitespace, etc. during validation.
- **Defaults**: Provide fallback values for optional fields.
- **Unions / Discriminated unions**: Model data that can be one of several shapes.
- **Composition**: Merge schemas, pick/omit fields (like TypeScript `Pick`/`Omit`), extend object schemas.
- **Custom error messages**: Per-field or per-constraint error messages.
- **Recursive types**: Self-referencing schemas for tree structures, etc.

### Ecosystem Integration

Zod has become a de facto standard in the TypeScript ecosystem. Libraries with first-class Zod support include tRPC, Next.js server actions, React Hook Form, and many others. The "single source of truth for validation and types" pattern is the killer feature — it eliminates drift between what code expects and what it actually receives.

______________________________________________________________________

## Shared `lib` Architecture

When running multiple Next.js apps serving different domains, shared code should live in a central `lib` directory. Each app consumes it via symlinks or path aliases.

### Directory Structure

```
project/
├── lib/                        # shared code
│   ├── schemas/                # zod schemas, shared types
│   ├── utils/                  # pure utility functions
│   ├── hooks/                  # shared React hooks
│   ├── components/             # shared UI components
│   ├── api/                    # shared API client logic
│   └── constants/              # enums, config values
├── apps/
│   ├── marketing/              # next.js app — marketing.example.com
│   │   ├── lib -> ../../lib    # symlink
│   │   └── ...
│   └── dashboard/              # next.js app — app.example.com
│       ├── lib -> ../../lib    # symlink
│       └── ...
```

### What Goes Where

The guiding principle: **`lib` holds anything that has no knowledge of which app it's running in.** If it references app-specific routes, env vars, or business logic, it belongs in the app.

#### `lib/schemas/`

Zod schemas and inferred types. One of the highest-value things to share — keeps validation and types consistent across apps. Shared API request/response shapes, domain models like `UserSchema`, `PaginationParamsSchema`, etc. Any app hitting the same backend should agree on what the data looks like.

#### `lib/utils/`

Pure functions with no side effects or framework dependencies. Date formatting, string manipulation, currency formatting, slug generation, etc. If it takes an input and returns an output with no imports from `next` or `react`, it belongs here.

#### `lib/hooks/`

React hooks that are genuinely reusable: `useDebounce`, `useLocalStorage`, `useMediaQuery`. Hooks that depend on app-specific context providers don't belong in `lib`.

#### `lib/components/`

Shared UI primitives: buttons, modals, form inputs, layout shells. Should be styled generically (accepting `className` or variant props) rather than hard-coding app-specific design decisions. If there's a shared design system, this is where it lives.

#### `lib/api/`

API client wrappers. A configured fetch wrapper, typed API call functions, error handling utilities. Examples: `fetchWithAuth` that handles token refresh, typed functions like `getUser(id): Promise<User>`.

#### `lib/constants/`

Shared enums, role definitions, feature flag shapes, config values that are truly universal.

#### What Stays in the App

- Route definitions and page components
- App-specific layouts and middleware
- `next.config.ts`
- Environment variable access (though `lib` can export a Zod schema for validating them)
- App-specific API routes
- Anything importing from `next/navigation` or `next/headers` in an app-specific way

### Practical Tips

- **Avoid barrel exports at scale.** A single `lib/index.ts` that re-exports everything kills tree-shaking. Import directly from subpaths: `@lib/schemas/user` not `@lib`.
- **Keep `lib` free of `next` imports.** Coupling `lib` to Next.js internals ties it to a framework version across all apps. If you need server-only code, split into `lib/server/` and `lib/client/`.
- **Dependency management.** In a simple setup, `lib` doesn't have its own `package.json` — it uses packages from the consuming app's `node_modules`. Works fine as long as apps share compatible versions. If they diverge, graduate to proper workspaces (npm workspaces, Turborepo, etc.).
- **This pattern scales well for 2–4 apps.** Beyond that, or when you need independent versioning of the shared lib, monorepo tooling starts earning its complexity.

______________________________________________________________________

## Next.js Config for Symlinks

### Webpack Approach (Legacy)

```js
const nextConfig = {
  webpack: (config) => {
    config.resolve.symlinks = false; // resolve through symlinks to real paths
    return config;
  },
};
```

Setting `symlinks = false` tells webpack to resolve through the symlink to the real file path. This avoids issues with duplicate React instances and module resolution.

### Turbopack Approach (Current)

```ts
import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {
    // Set root to monorepo root so turbopack can resolve files outside the app directory
    root: path.join(__dirname, "../../../"),
    // Clean import aliases for symlinked shared libraries
    resolveAlias: {
      "@axios-ui-theme": path.resolve(__dirname, "lib/axios-ui-theme"),
      "@axios-api-client": path.resolve(__dirname, "lib/axios-api-client"),
    },
  },
};
```

Key points:

- **`root`**: Tells turbopack that files outside the app directory are legitimate sources. Without this, turbopack refuses to resolve anything above the app's own directory.
- **`resolveAlias`**: Maps clean import paths to the symlinked directories. The alias resolves through the symlink to the real files, and the `root` setting ensures turbopack is allowed to read them.
- **`output: 'standalone'`**: Produces a self-contained build that bundles its own server and dependencies. Used for containerized deployments (Docker/K8s) — the standalone output copies only what's needed into `.next/standalone` so the image stays small.

### TypeScript Path Aliases (Complement to Symlinks)

Can be used alongside symlinks for cleaner imports:

```json
{
  "compilerOptions": {
    "paths": {
      "@lib/*": ["../../lib/*"]
    }
  }
}
```

This gives you `import { UserSchema } from "@lib/schemas/user"` instead of relative imports through a symlink. Next.js respects tsconfig paths natively.

### Build Implications

With `resolveAlias`, shared libraries are compiled as part of each app's build (not pre-built). This means consistent transpilation settings across apps, but build times scale with the size of shared libs. If they get large, pre-building and consuming the output is an option, but inline compilation is simpler for most cases.

______________________________________________________________________

## Turbopack

Turbopack is the Rust-based bundler Vercel built to replace webpack in Next.js. As of Next.js 15, it's the default bundler for the dev server. Production builds still use webpack, though the plan is to move production to turbopack as well.

### Why It Exists

Webpack's hot module replacement (HMR) gets noticeably slow as projects grow. Turbopack's main selling point is speed, particularly in development.

### How It's Different

The architecture difference from webpack:

- **Webpack**: Bundles everything eagerly on startup. Every module in the dependency graph gets processed before the dev server is ready.
- **Turbopack**: Incremental computation. Only processes modules actually needed for the current request. Caches the dependency graph at a granular level. First page load compiles just what that page needs, subsequent changes only recompile what actually changed.

The speed gains come from this incremental architecture, not just from being written in Rust (though that helps).

### Practical Impact

- Dev server starts faster.
- HMR updates are near-instant even in large codebases.
- Bundler-level config (aliases, resolution, module rules) needs to be expressed in the `turbopack` config block for dev.
- Some webpack-specific plugins don't have turbopack equivalents yet.
- During the transition period, you may need dual config: `turbopack` block for dev, `webpack` callback for production. This is temporary.
