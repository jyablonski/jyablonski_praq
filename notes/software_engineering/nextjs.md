# Next.js

Next.js is a React framework that enables server-side rendering, static site generation, and hybrid rendering for building modern web apps. It's designed to improve performance, SEO, and developer experience. It offers:

- File based routing: pages are created based on file structure inside `app` directory and `page.tsx` files
- Server-side rendering: pages are generated dynamically on the server for each request
- Static site generation: pages are pre-rendered at build time for faster performance
- API Routes: backend-like functionality can be added using API endpoints inside the project
- Incremental static regeneration: static pages can be updated after deployment without rebuilding the entire site

## Project Files

These files are typically found in the root of a Next.js project.

- `package.json` – Defines project dependencies, scripts, and metadata.
- `next.config.js` – Configuration file for customizing Next.js behavior (e.g., redirects, rewrites, images, etc.).
- `.env` / `.env.local` – Stores environment variables (e.g., API keys, database URLs).
- `tsconfig.json` (if using TypeScript) – TypeScript configuration file.

______________________________________________________________________

## 2. Directories

### a) `app/` (New in Next.js 13+ with the App Router)

- Introduced in Next.js 13, this directory follows a React Server Components model.
- Uses file-based routing, where folders and files define routes.
- Supports layouts, loading states, and error handling.

Example structure:

```
app/
├── layout.js     # Shared layout for all pages
├── page.js       # Default homepage (index)
├── about/
│   ├── page.js   # `/about` page
│   ├── loading.js # Custom loading UI for about page
├── api/
│   ├── route.js  # API endpoint (Replaces `pages/api`)
```

______________________________________________________________________

### c) `public/` (Static Assets)

- Stores images, fonts, icons, and other static files.
- Files in `public/` are served directly.

Example:

```
/public/logo.png → Accessible at `https://yourdomain.com/logo.png`
```

______________________________________________________________________

### d) `components/` (Reusable Components)

- Stores UI components that can be reused across pages.
- Component names follow PascalCase by convention to distinguish them as custom components

Example:

```
components/
├── Navbar.tsx
├── Footer.tsx
```

______________________________________________________________________

### e) `styles/` (Global & Component Styles)

- Stores styles, which can be:
  - Global CSS (`styles/globals.css`)
  - CSS Modules (`Component.module.css`)
  - Tailwind CSS (if configured)

Example:

```
styles/
├── globals.css  # Global styles
├── Home.module.css # Scoped styles for Home component
```

______________________________________________________________________

### f) `api/` (Serverless API Routes)

- Located in `pages/api/` (Old API) or `app/api/` (New API).
- Allows writing backend logic.

Example (`pages/api/hello.js`):

```js
export default function handler(req, res) {
  res.status(200).json({ message: "Hello World" });
}
```

Example (`app/api/route.js` in Next.js 13+):

```js
export async function GET() {
  return Response.json({ message: "Hello World" });
}
```

______________________________________________________________________

### g) `middleware.js` (Optional)

- Runs before every request.
- Useful for authentication, redirects, and rewrites.

Example (`middleware.js`):

```js
export function middleware(req) {
  if (!req.cookies.authToken) {
    return Response.redirect("/login");
  }
}
```

______________________________________________________________________

## 3. Special Files

Some files have special meanings in Next.js:

| File Name | Purpose |
| -------------- | --------------------------------------------------- |
| `layout.js` | Defines shared layout for nested pages (App Router) |
| `page.js` | Defines a page in the App Router (`/route`) |
| `loading.js` | Creates a loading state for a route |
| `error.js` | Handles errors within a route |
| `not-found.js` | Custom 404 page |
| `head.js` | Defines metadata (title, description) |
| `route.js` | API handler in App Router (`/api/...`) |
| `_app.js` | Customizes global app behavior (for `pages/` only) |
| `_document.js` | Custom HTML document structure (for `pages/` only) |
