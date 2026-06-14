# Astro

## What Astro Is

Astro is a web framework for building content-driven websites: blogs, marketing sites, docs, portfolios, and static apps. Its defining characteristic is that it ships zero JavaScript by default. Pages render to static HTML at build time, and interactivity is opted into per-component rather than assumed for the whole page.

This is a deliberate inversion of the SPA model (Next.js, SvelteKit, etc.), where the framework hydrates the entire page into a client-side app. Astro treats JS as a cost you pay only where you actually need it.

## The Core Idea

Astro renders everything to HTML on the server/at build, then lets you mark specific interactive components as "islands" that hydrate independently in the browser.

```astro
---
import Header from '../components/Header.astro';      // static, no JS
import SearchBox from '../components/SearchBox.jsx';   // interactive island
---
<Header />
<SearchBox client:load />   <!-- only this ships JS -->
```

The `client:*` directives control *when* an island hydrates:

- `client:load` — hydrate immediately
- `client:idle` — hydrate when the browser is idle
- `client:visible` — hydrate when scrolled into view
- `client:media` — hydrate at a breakpoint

Everything without a directive stays as plain HTML. A page with one interactive widget ships the JS for that widget and nothing else.

## Framework-Agnostic

Astro components (`.astro` files) are its native format, but you can drop in React, Vue, Svelte, Solid, or Preact components, even mixing several in the same project. This means you're not locked into one component ecosystem, and you can reuse existing components rather than rewriting them.

## Why It's Good for Blogs

Blogs are where Astro is strongest, because the content is mostly static and the JS-heavy SPA approach is pure overhead for reading text.

- Content Collections — a typed API for managing local Markdown/MDX content. You define a schema (via Zod), and Astro validates frontmatter and gives you type-safe queries over your posts. This catches missing fields and typos at build time instead of in production.
- MDX support — write Markdown with embedded interactive components where you want them (a chart, a live demo) without making the whole post a client app.
- Static generation — posts compile to flat HTML files, so they're trivially cacheable on a CDN, fast to serve, and resilient. No server round-trip to render an article.
- Excellent Core Web Vitals — because there's little to no JS on a typical post, time-to-interactive and largest-contentful-paint are very low without extra optimization work.
- SEO-friendly — fully rendered HTML on first response, plus built-in helpers for sitemaps, RSS feeds, and canonical URLs.

## Why It's Good for Static Site Apps

- Output flexibility — defaults to fully static (`output: 'static'`) for pure SSG, but supports SSR and hybrid rendering when a few routes need to be dynamic. You can render most of a site statically and make just the dynamic endpoints server-rendered.
- Adapter ecosystem — deploy to Vercel, Netlify, Cloudflare, Node, or static hosts (S3, GitHub Pages) via swappable adapters. The static path means it'll run anywhere that serves files.
- Build-time data fetching — fetch from APIs, CMSs, or databases during the build and bake the results into HTML, so the live site has no runtime dependency on those sources.
- Vite-based — fast dev server, HMR, and a modern build pipeline out of the box.
- Low maintenance surface — static output has no server to keep alive, patch, or scale, which keeps hosting cheap and the security/ops footprint small.

## Trade-offs to Be Aware Of

Astro is optimized for content, not for highly interactive, app-like experiences. If you're building something where most of the page is stateful and dynamic — a dashboard, an editor, a real-time tool — a full SPA framework is a more natural fit. The islands model shines when the interactive surface is a minority of the page; it works against you when nearly everything is interactive.

## When to Reach for It

- Blogs, documentation sites, marketing pages, portfolios
- Content-heavy sites where load speed and SEO matter
- Projects where you want to mix-and-match component frameworks
- Static-first sites with a handful of dynamic routes

For a mostly-static site with islands of interactivity, Astro gives you near-optimal performance with minimal effort. For a mostly-dynamic app, a traditional SPA framework is usually the better tool.
