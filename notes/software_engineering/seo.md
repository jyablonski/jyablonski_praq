# SEO Notes

## The core mental model

SEO for a personal technical blog is not the same problem as SEO for a news site or e-commerce. The leverage is long-tail specificity, not ranking factor optimization. You will not outrank dbt Labs on "dbt tutorial." You can absolutely rank page one for "dbt incremental model dedup snowflake regex" because almost no one is writing about that exact intersection.

Write the post you wanted to find when you were stuck on the problem. That's the strategy.

## Title tag vs H1

These are two separate fields and they should usually differ.

- `<title>` is what Google shows as the blue clickable link in search results, what appears in the browser tab, and what defaults into social shares. Write it search-forward: specific, keyword-bearing, exactly the phrase someone would type when stuck on the problem.
- `<h1>` is what readers see at the top of the article. Write it for voice and engagement.

Example split:

- Title: `Debugging dbt Test Failures with Snowflake Regex Behavior`
- H1: `Why my dbt tests kept failing on Snowflake regex (and how I fixed it)`

Google sometimes rewrites your title in the SERP based on the H1 or page content if it thinks yours is keyword-stuffed. The H1 still matters for search even when it's not the official SEO title.

## URL structure

For a personal blog: go flat and evergreen.

- `jacobsite.com/snowflake-regex-debugging` (flat)
- `jacobsite.com/posts/snowflake-regex-debugging` (flat with a single prefix)

Skip dates in URLs. Skip categories until there are enough posts to justify hierarchy. Date-in-URL and deep category structures are news-site patterns. Flat URLs are the lowest-regret choice because they survive every future reorganization.

Lowercase, hyphens (not underscores), no special characters, short slug.

## SERP

SERP = Search Engine Results Page. The page Google shows after a search. When SEO writing references "the SERP" it means that whole results layout: blue links, AI Overview, People Also Ask, image carousels, ads, the lot.

## Schema (structured data)

Schema is JSON-LD embedded in the page head that tells search engines explicitly what the content is, rather than making them infer.

For a technical blog, the minimum is:

- `Article` schema with `headline`, `author`, `datePublished`, `dateModified`
- `Person` schema for the author with name and a bio link

Breadcrumb schema only matters if the site has real hierarchy. Skip it on a flat blog.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Debugging dbt Test Failures with Snowflake Regex Behavior",
  "author": { "@type": "Person", "name": "Jacob ..." },
  "datePublished": "2026-05-17",
  "dateModified": "2026-05-17"
}
</script>
```

## Open Graph (link previews)

Open Graph is the de facto standard for link previews everywhere: Facebook, LinkedIn, Slack, Discord, iMessage, WhatsApp, Bluesky, Mastodon, RSS readers, Notion. X/Twitter falls back to OG when Twitter Card tags aren't present.

Minimum per post:

```html
<meta property="og:title" content="..." />
<meta property="og:description" content="..." />
<meta property="og:image" content="https://jacobsite.com/og/post-slug.png" />
<meta property="og:url" content="https://jacobsite.com/post-slug" />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
```

OG image must be 1200x630px. Wrong size or aspect ratio gets cropped badly on LinkedIn and Slack. Auto-generate per post at build time using `@vercel/og`, Astro's image generator, or equivalent. Don't hand-design these.

Cache gotcha: Facebook, LinkedIn, and Slack aggressively cache previews. Use each platform's debugger to force a re-scrape after edits, or append a `?v=2` query param.

## What actually matters for a zero-traffic blog

In rough priority order:

1. Write specific, lived-experience posts that solve real problems with real code. This is 80% of long-term traffic.
1. Title tag is the exact phrase someone would Google when stuck on the same problem.
1. URL is flat, lowercase, hyphenated, slug only.
1. Code blocks are real text in `<pre><code>`, never images. Both Google and LLMs need to parse them.
1. Visible author byline, publish date, last-updated date.
1. Link out to primary sources (official docs, GitHub issues, original posts).
1. OG tags templated once into the layout, auto-populated from frontmatter.
1. Basic `Article` schema templated once into the layout.
1. Distribution: post to Hacker News, dbt Slack, r/dataengineering, relevant Discords. A single front-page HN hit beats six months of SEO at this scale.

## What does not matter yet

- Breadcrumb schema (no hierarchy to describe)
- Internal linking strategy (not enough posts)
- Core Web Vitals tuning beyond using a fast static generator
- Keyword density
- Meta keywords tag (dead for 15+ years)
- Full Twitter Card tag set (OG fallback is enough)
- Sitemap optimization (any static generator handles this)

## LLM citation (the new layer)

AI search is now a real distribution channel. The same things that help with Google help with LLM citation, with two additions:

- Headlines that directly answer the implied question get cited noticeably more often than clever or oblique ones.
- Specific, structured content with clear claims and primary-source links is what gets pulled into AI Overviews and ChatGPT citations.

Boring, specific, clear headlines win on both surfaces. Clever print-style headlines lose on both.
