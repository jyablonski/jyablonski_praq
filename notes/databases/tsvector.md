# tsvector

tsvector is PostgreSQL's data type for full-text search. It's a sorted list of distinct lexemes—normalized words stripped of suffixes, lowercased, and deduplicated. Each lexeme can optionally store position information (where in the original text it appeared).

For example, the sentence "The quick brown foxes jumped quickly" becomes something like:

- `'brown':3 'fox':4 'jump':5 'quick':2,6`
- Notice: "foxes" -> "fox", "jumped" -> "jump", "quickly" -> "quick", and "The" (a stop word) is removed entirely.

tsvector is purely for keyword search. Semantic search would use embeddings (vectors like [0.12, -0.34, 0.56, ...]) and similarity measures (cosine distance). That's what pgvector does. tsvector is purely lexical, it just cares whether the normalized words are present, not what they mean.

Postgres works fine for full text search when starting out, but eventually gets outscaled because it's fundamenetally a single-node system. Elasticsearch is purpose-built for search and scales horizontally because it's a distributed system by nature, you add more nodes as data grows.

- The tradeoff here is operational complexity.
- Leverage Postgres while you can, having to introduce Elasticsearch means another system to deploy, monitor, and keep in sync w/ your source of truth.

## Why use it?

1. Speed — Instead of `LIKE '%keyword%'` which scans every row, you can build a GIN index on `tsvector` columns for fast lookups
1. Linguistic smarts — Stemming means searching "run" matches "running", "runs", "ran"
1. Ranking — You can score results by relevance using `ts_rank()`
1. Phrase and proximity search — Find words near each other, in order, etc.

It's ideal for things like article search, product catalogs, or anywhere you need "Google-like" search over text.

## Initial Example

```sql
SELECT id, title
FROM articles
WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('english', 'machine & learning');
```

- This is keyword search, not semantic search.

The @@ operator checks whether the lexemes in the tsquery exist in the tsvector. It's doing:

1. Normalize "machine" -> machin (stem)
1. Normalize "learning" -> learn (stem)
1. Check: does the tsvector contain both machin AND learn?

But, this is inefficient. The query computes `to_tsvector()` for every row on every search, no index can help.

## Index Performance Improvement

To improve performance, we can add an index here. This involves:

1. Creating a new `tsvector` column on the table; 1 column for all of the text fields you want searchable
   - 1 Column here makes queries very simple. If separate columns, your queries start involving a lot of `OR` conditions and ranking becomes harder
1. Backfill the values for that tsvector column
1. Create a `GIN` index on that column
1. Now the tsvector is pre-computed and indexed. Queries hit the GIN index instead of recomputing on every row.

```sql
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Populate with weighted fields (A = title, B = body)
-- Weight A is highest priority, D is lowest
UPDATE articles SET search_vector =
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(body, '')), 'B');

-- Create GIN index for fast lookups
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);
```

In plain english, the process looks like:

1. Normalize words from the text fields you include
1. ssign weights by field (title=A, summary=B, body=C, can only go A-D)
1. Store it all in one tsvector column: lexemes + positions + weight tags
1. GIN index enables fast lookups, weights enable ranking

### GIN Index

GIN stands for Generalized Inverted Index. Think of it like a book index—instead of scanning every page for "machine", you flip to the back and see "machine: pages 12, 47, 203".

A GIN index does the same thing for your tsvector column:

```sh
'machin' -> row 1, row 87
'learn'  -> row 1, row 51, row 53, row 55
'neural' -> row 1, row 17
'data'   -> row 1, row 6, row 58, row 68
```

So when you search for 'machin' & 'learn', Postgres looks up both terms in the index, finds the intersection (row 1), and returns that - without scanning every row.

### Index Downside

The only downside here is this index is not automatically kept up to date. Because we're creating an index on a derived `tsvector` columm, the index will only be kept up to date when we add new values for this derived column.

This can be solved with a database trigger, or handled on the application side so whenever we add rows to the table, we're automatically filling in the `tsvector` field values as well so the index can be kept up to date.

- Another option here is a CRON route where it's refreshed every x cadence.
- Database trigger is the most straightforward solution here.

## Operation Summary

| Concept | What it does |
| ------------------------ | ---------------------------------------------------------- |
| `to_tsvector()` | Converts text -> normalized lexemes with positions |
| `to_tsquery()` | Creates search query with operators (`&`, ` `, `!`, `<->`) |
| `websearch_to_tsquery()` | User-friendly query parsing (handles quotes, OR, `-`) |
| `@@` operator | Matches tsvector against tsquery |
| `ts_rank()` | Scores relevance |
| `ts_headline()` | Generates snippets with highlighted matches |
| `setweight()` | Assigns importance (A > B > C > D) to different fields |
| GIN index | Makes searches fast on large tables |

## tsvector Storage Tradeoffs

A `tsvector` column doesn't just store normalized words, it stores:

- Lexemes (stemmed words like "learn" from "learning")
- Positions (where each word appeared in the original text)
- Weights (A/B/C/D priority tags you assigned)

This metadata enables phrase search (`<->`) and ranking (`ts_rank`), but it takes storage space both in terms of raw bytes in the table for that column, and also the index

### Example storage breakdown

For a table with 100 articles:

| Column | Size |
| ------------- | ------ |
| title | 2.5 KB |
| body | 13 KB |
| search_vector | 24 KB |
| GIN index | 96 KB |

The `search_vector` column is roughly 1.5x the size of the source text, and the GIN index is substantial because it builds an inverted index mapping every lexeme to its matching rows.

You're paying storage cost upfront to avoid computation cost at query time.

| Approach | Storage | Query speed |
| ---------------------------------- | ------- | ---------------------- |
| Stored tsvector + GIN index | Higher | Fast (index lookup) |
| Compute `to_tsvector()` on the fly | None | Slow (full table scan) |

### When each makes sense

Use stored tsvector + GIN index when:

- Search is a frequent operation
- Table has many rows
- You need ranking with weights

Compute on the fly when:

- Storage is constrained
- Searches are rare
- Table is small (hundreds of rows)

## tsvector vs pgvector

### What's the difference?

| | tsvector | pgvector |
| ------------------------------ | --------------------------------- | ----------------------------------------------------- |
| Search type | Keyword/lexical | Semantic/similarity |
| Stores | Normalized word stems + positions | Float arrays (embeddings) |
| Matches on | Exact words present | Conceptual meaning |
| "ML" finds "machine learning"? | No | Yes |
| "happy" finds "joyful"? | No | Yes |
| Index type | GIN | HNSW or IVFFlat |
| External dependency | None | Embedding model (OpenAI, sentence-transformers, etc.) |
| Storage per row | ~1-2x source text | Fixed (e.g., 1536 floats for OpenAI = 6KB) |

### When to use tsvector

- Exact keyword matching ("find articles mentioning PostgreSQL")
- Filtering by specific terms
- Phrase search ("neural network" as adjacent words)
- No external API dependency
- Lower storage/complexity requirements

### When to use pgvector

- Semantic search ("find articles about database performance" matches "SQL optimization")
- Finding similar content
- RAG applications (retrieval-augmented generation)
- When synonyms and related concepts should match
- Multilingual search without separate dictionaries

### Using both together

Many production systems combine them:

1. pgvector for semantic similarity (find conceptually related content)
1. tsvector for keyword filters (must contain "PostgreSQL")

Example: "Find articles similar to this one, but only if they mention Kubernetes"

```sql
SELECT id, title
FROM articles
WHERE search_vector @@ to_tsquery('english', 'kubernetes')  -- keyword filter
ORDER BY embedding <=> query_embedding  -- semantic ranking
LIMIT 10;
```
