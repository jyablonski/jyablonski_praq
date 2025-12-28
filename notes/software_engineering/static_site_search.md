# Static Site Search

Static site search enables users to quickly find content on documentation sites, blogs, and other content-heavy websites. Unlike dynamic sites with databases, static sites need a different approach to search functionality since there's no backend to query.

## Why We Need It

- User Experience: Visitors need to find specific information quickly without manually browsing
- Large Content Sites: Documentation sites with hundreds/thousands of pages become unusable without search
- Navigation: Search complements site navigation and often becomes the primary way users find content
- Discoverability: Helps users find content they didn't know existed

## Search Options for Static Sites

### 1. Pagefind (Self-Hosted, Free)

What it is: A static search library that generates a search index at build time and runs entirely in the browser.

How it works:

1. Build time: Crawls your static HTML files
2. Generates compressed search index (chunked `.pff` files)
3. Deploys as static files alongside your site
4. Search runs client-side in browser (lazy-loads index chunks)

Architecture:
```
npm install pagefind (contains Rust CLI + JS runtime)
  ↓
Build process:
  npm run build        → Generates static HTML
  npx pagefind --site out  → CLI crawls HTML, builds index
  ↓
Outputs:
  out/pagefind/pagefind.js    (browser search engine)
  out/pagefind/index/*.pff    (compressed index chunks)
  ↓
Deploy to S3/CDN as static files
  ↓
Client searches → Fetches relevant index chunks → Searches in browser
```

- The key point here is when searching, only the necessary index chunks are downloaded, keeping initial load small.
- Otherwise on initial load, you'd be forced to download the entire index, which could be huge like > 5 MB

Indexing process:

- Parses HTML, extracts text content
- Tokenizes and normalizes text ("Running" → "run")
- Builds inverted index: `{word: [page1, page3, page7]}`
- Compresses and chunks by letter ranges
- Includes metadata (titles, URLs, excerpts)
- Weights words (title matches > body matches)

Pros:

- Completely free
- Zero infrastructure to manage
- Privacy-friendly (no external tracking)
- Lazy loading (only downloads needed chunks)
- Small footprint (~10KB initial load)
- Works offline once cached

Cons:

- Limited to static sites
- Index built at build time (not real-time)
- Client-side search (slower for huge sites)
- Basic features compared to hosted solutions
- Index size grows with content

Best for:

- Documentation sites
- Blogs and marketing sites
- Privacy-conscious projects
- Projects wanting zero external dependencies
- Small-to-medium content (< 10,000 pages)

### 2. Algolia (Hosted, Paid)

What it is: Hosted search-as-a-service platform with advanced features and infrastructure.

How it works:

1. Content indexed on Algolia's servers (via API or crawler)
2. Your site makes API calls to Algolia for searches
3. Algolia returns results in milliseconds
4. React/JS components display results

Pricing:

- Free tier: 10,000 search requests/month, 10,000 records
- DocSearch program: Free for open-source documentation
- Paid plans: Start ~$1/month, scale based on:
  - Search requests
  - Number of records
  - Advanced features

Pros:

- Extremely fast (optimized infrastructure)
- Advanced typo tolerance
- Real-time indexing (update content instantly)
- Rich features: faceting, filtering, geo-search
- Analytics and insights
- A/B testing
- Superior relevance ranking algorithms
- Handles millions of records
- Great developer experience

Cons:

- Costs money for commercial use
- External dependency (service outage = no search)
- Privacy concerns (searches tracked externally)
- Vendor lock-in
- Overkill for simple sites

Best for:

- Large documentation sites (1000+ pages)
- High-traffic commercial sites
- Sites needing advanced search features
- Projects with budget for hosted services
- Teams wanting managed infrastructure

### 3. Astro Starlight (Built-in Options)

What it is: Astro's documentation framework with integrated search options.

Two search options:

#### Option A: Pagefind (Default)

- Built-in, zero-config
- Same as standalone Pagefind above
- Good for most documentation sites
- Completely self-hosted

#### Option B: Algolia (Opt-in)

- Easy config swap in `astro.config.mjs`
- All Algolia benefits listed above
- UI stays consistent (Starlight abstracts the component)

Why Starlight is great:
- Sensible defaults (Pagefind works out of the box)
- Easy upgrade path (switch to Algolia with config change)
- No need to build search UI yourself
- Optimized for documentation use cases

Configuration example:
```javascript
// astro.config.mjs

// Default (Pagefind)
export default defineConfig({
  integrations: [starlight({
    title: 'My Docs',
    // Pagefind is default, no config needed
  })],
});

// Switch to Algolia
export default defineConfig({
  integrations: [starlight({
    title: 'My Docs',
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_API_KEY',
      indexName: 'YOUR_INDEX',
    },
  })],
});
```

## Comparison Matrix

| Feature            | Pagefind           | Algolia           | Starlight               |
| ------------------ | ------------------ | ----------------- | ----------------------- |
| Cost               | Free               | Free tier / Paid  | Depends on choice       |
| Infrastructure     | Self-hosted        | External service  | Self-hosted or external |
| Setup complexity   | Low                | Medium            | Very low                |
| Performance        | Good               | Excellent         | Depends on choice       |
| Real-time indexing | No (build time)    | Yes               | Depends on choice       |
| Privacy            | Full control       | External tracking | Depends on choice       |
| Features           | Basic              | Advanced          | Depends on choice       |
| Best for           | Small-medium sites | Large/commercial  | Documentation sites     |

## Alternative Self-Hosted Options

Meilisearch:

- More powerful than Pagefind
- Self-hosted server (not static)
- Docker/K8s deployment
- Good for larger sites

Typesense:

- Similar to Meilisearch
- Self-hosted or managed cloud
- Good performance
- More control than Algolia

Fuse.js / Lunr.js:

- Lightweight client-side search libraries
- Simpler than Pagefind
- Load entire index upfront (not chunked)
- Good for small sites

## Decision Guide

Choose Pagefind if:

- Static site deployment (S3, Netlify, etc.)
- Want zero infrastructure
- Privacy is important
- Budget is $0
- Content < 10,000 pages

Choose Algolia if:

- Large site (1000+ pages) with high traffic
- Need advanced features (faceting, analytics)
- Have budget for hosted services
- Want best-in-class search experience
- Open-source docs (free DocSearch program)

Choose Starlight if:

- Building documentation site
- Want sensible defaults
- Like easy upgrade path
- Don't want to build search UI

Choose Meilisearch/Typesense if:

- Want more power than Pagefind
- Comfortable managing infrastructure
- Have existing K8s/Docker setup
- Want control without external dependencies

## Integration with Next.js + S3 Deployment

Current workflow:
```bash
npm run build          # Next.js static export to out/
aws s3 sync out/ s3://bucket --delete
```

With Pagefind:
```bash
# package.json
{
  "scripts": {
    "build": "next build",
    "postbuild": "npx pagefind --site out"
  }
}

# Deploy
npm run build          # Runs build + pagefind automatically
aws s3 sync out/ s3://bucket --delete  # Uploads everything including index
```

No changes to deployment process - Pagefind output is just more static files.

## Summary

Static site search has evolved from simple client-side libraries to sophisticated solutions. For most personal projects and small-to-medium documentation sites, Pagefind offers the best balance of simplicity, performance, and cost (free). For large commercial sites or projects needing advanced features, Algolia's hosted solution provides best-in-class search at a price. Astro Starlight makes the decision easier by providing both options with a simple config change, letting you start simple and upgrade when needed.