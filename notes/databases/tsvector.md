# tsvector

tsvector is PostgreSQL's data type for full-text search. It's a sorted list of distinct lexemes - normalized words stripped of suffixes, lowercased, and deduplicated. Each lexeme can optionally store position information (where in the original text it appeared).

For example, the sentence "The quick brown foxes jumped quickly" becomes something like:

- `'brown':3 'fox':4 'jump':5 'quick':2,6`
- Notice: "foxes" -> "fox", "jumped" -> "jump", "quickly" -> "quick", and "The" (a stop word) is removed entirely.

tsvector is purely for keyword search. Semantic search would use embeddings (vectors like [0.12, -0.34, 0.56, ...]) and similarity measures (cosine distance). That's what pgvector does. tsvector is purely lexical, it just cares whether the normalized words are present, not what they mean.

Postgres works fine for full text search when starting out, but eventually gets outscaled because it's fundamentally a single-node system. Elasticsearch is purpose-built for search and scales horizontally because it's a distributed system by nature, you add more nodes as data grows.

- The tradeoff here is operational complexity.
- Leverage Postgres while you can, having to introduce Elasticsearch means another system to deploy, monitor, and keep in sync w/ your source of truth.

## Why use it?

1. Speed - Instead of `LIKE '%keyword%'` which scans every row, you can build a GIN index on `tsvector` columns for fast lookups
1. Linguistic smarts - Stemming means searching "run" matches "running", "runs", "ran"
1. Ranking - You can score results by relevance using `ts_rank()`
1. Phrase and proximity search - Find words near each other, in order, etc.

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
1. Assign weights by field (title=A, summary=B, body=C, can only go A-D)
1. Store it all in one tsvector column: lexemes + positions + weight tags
1. GIN index enables fast lookups, weights enable ranking

### GIN Index

GIN stands for Generalized Inverted Index. Think of it like a book index--instead of scanning every page for "machine", you flip to the back and see "machine: pages 12, 47, 203".

A GIN index does the same thing for your tsvector column:

```sh
'machin' -> row 1, row 87
'learn'  -> row 1, row 51, row 53, row 55
'neural' -> row 1, row 17
'data'   -> row 1, row 6, row 58, row 68
```

So when you search for 'machin' & 'learn', Postgres looks up both terms in the index, finds the intersection (row 1), and returns that - without scanning every row.

### Index Downside

The only downside here is this index is not automatically kept up to date. Because we're creating an index on a derived `tsvector` column, the index will only be kept up to date when we add new values for this derived column.

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
WHERE search_vector @@ to_tsquery('english', 'kubernetes')  - keyword filter
ORDER BY embedding <=> query_embedding  - semantic ranking
LIMIT 10;
```

______________________________________________________________________

# Semantic Search Deep Dive

## How Embeddings Work

Semantic search relies on embedding models - pre-trained neural networks that have been trained on massive text corpora to understand meaning and relationships between words and phrases. The model learns that "delicious" and "tasty" are semantically close while "delicious" and "bankruptcy" are far apart.

When you pass text into an embedding model, it outputs an array of floats (not integers) like `[0.0231, -0.0892, 0.1534, ...]`. The decimal precision is what gives it the ability to represent fine-grained differences in meaning. Each text input becomes a point in high-dimensional space, and texts with similar meaning end up near each other.

### What are dimensions?

Each dimension captures some learned feature of meaning. These features are abstract and emerge from training - no one designed dimension 742 to mean "food-related." The model figured out its own internal representation.

A simplified analogy: imagine you only had 3 dimensions to represent restaurant reviews, and those 3 dimensions happened to correspond to something like food quality (0.0 to 1.0), service quality (0.0 to 1.0), and sentiment (-1.0 to 1.0). "The pasta was incredible" might embed as `[0.9, 0.1, 0.8]` (very food-related, not about service, very positive). "Our waiter was rude" might be `[0.05, 0.9, -0.7]`. Cosine similarity between these two vectors would be low since they're pointing in very different directions.

In practice, models use far more dimensions - 384, 768, 1536, etc. More dimensions means more expressive power to capture subtle distinctions in tone, topic, specificity, sentiment, formality, domain, and abstract features that don't map neatly to human concepts. Three dimensions wouldn't work for a real system for the same reason you can't describe every restaurant review meaningfully with just three numbers.

### Dimensionality and model choice

The model determines the dimensionality. When you pick `text-embedding-3-small` from OpenAI, you get 1536 dimensions. Pick `sentence-transformers/all-MiniLM-L6-v2` and you get 384. It's baked into the model architecture.

One exception: OpenAI's newer embedding models let you truncate the output to fewer dimensions. They trained the model so the most important information is front-loaded into the earlier dimensions (a technique called Matryoshka representation learning), so you can request 512 instead of 1536 and it degrades gracefully rather than falling apart. Most other models give you a fixed output size.

More dimensions generally allows more room to capture meaning, but with diminishing returns. Going from 384 to 768 is a meaningful jump. Going from 1536 to 3072 might barely move the needle while doubling storage and slowing queries. There's also a ceiling tied to the model itself - a small, mediocre model outputting 1536 dimensions might waste many of them on noise, while a well-trained model at 384 dimensions could outperform it. The dimensions are only as useful as what the model learned to encode in them.

In practice, you're choosing a model (based on quality, speed, cost, local vs API) and the dimensions come with it.

### What gets stored

Each review/record gets an array of floats equal to the model's dimensionality. For a 1536-dimension model, that's 1536 floats per record. Each float is 4 bytes, so one embedding is roughly 6KB.

| Records | Dimensions | Vector storage |
| ----------- | ---------- | -------------- |
| 1 million | 1536 | ~6 GB |
| 1 million | 384 | ~1.5 GB |
| 100 million | 1536 | ~600 GB |

This is just the vector column. HNSW or IVFFlat indexes on top add more memory.

## Implementation Flow

The typical setup for semantic search in Postgres with pgvector:

1. Install the pgvector extension and add a `vector(N)` column to your existing table (where N is your model's dimensionality). No need for a separate embedding table - keeping it on the same table simplifies joins and lets you filter on other columns in the same query.
1. Generate embeddings for each record using your chosen model (OpenAI API, Cohere, a local model like sentence-transformers, etc.) - typically done in Python or another application layer.
1. Store the resulting float arrays back into the vector column.
1. Create an HNSW or IVFFlat index on the vector column for fast approximate nearest-neighbor search.
1. At query time, embed the search query using the same model, then find nearest neighbors using distance operators (`<=>` for cosine distance, `<->` for L2 distance, etc.).

```sql
-- Add vector column to existing table
ALTER TABLE reviews ADD COLUMN embedding vector(1536);

-- After populating embeddings from your application layer...

-- Create HNSW index for fast approximate nearest-neighbor search
CREATE INDEX idx_reviews_embedding ON reviews USING hnsw (embedding vector_cosine_ops);

-- Query: embed the search text with the same model, then find nearest neighbors
SELECT id, review_text, embedding <=> '[0.0231, -0.0892, ...]'::vector AS distance
FROM reviews
ORDER BY embedding <=> '[0.0231, -0.0892, ...]'::vector
LIMIT 10;
```

## Hybrid Search

Hybrid search runs both keyword and semantic search on the same query and combines the results. The idea is keyword search catches exact matches that semantic might underrank, and semantic catches conceptual matches that keyword would miss entirely.

A search for "slow service" could keyword-match reviews containing those exact words while also semantically matching reviews saying "waited 45 minutes for our entrees."

The basic approach:

1. Run tsvector search, get results ranked by text relevance (ts_rank)
1. Run pgvector cosine similarity search, get results ranked by semantic closeness
1. Combine the scores with some weighting, like `0.4 * keyword_score + 0.6 * semantic_score`, and return the final ranked list

One challenge is that keyword scores and semantic scores are on different scales, making raw score combination tricky. Reciprocal Rank Fusion (RRF) is a common technique that merges the two ranked lists based on position rather than raw scores, sidestepping the normalization problem.

```sql
-- Simple hybrid: keyword filter + semantic ranking
SELECT id, review_text
FROM reviews
WHERE search_vector @@ to_tsquery('english', 'slow & service')
ORDER BY embedding <=> query_embedding
LIMIT 10;

-- Weighted hybrid: combine both scores
SELECT id, review_text,
    0.4 * ts_rank(search_vector, to_tsquery('english', 'slow & service')) +
    0.6 * (1 - (embedding <=> query_embedding)) AS combined_score
FROM reviews
ORDER BY combined_score DESC
LIMIT 10;
```

## Good and Bad Use Cases

### Good use cases for semantic search

Semantic search shines when users search by intent or concept rather than exact terms. Product reviews are a classic - someone searching "comfortable for long walks" should match reviews mentioning "wore these on a 10-mile hike with no blisters." Customer support ticket routing works well too, matching incoming tickets to similar resolved ones even when the wording is completely different. RAG is probably the most common use case right now, finding relevant documentation chunks to feed into an LLM. Recommendation systems also benefit ("find me articles similar to this one").

The common thread: meaning matters more than exact wording, and there's enough semantic variety in the data that keyword matching would miss a lot.

### Bad use cases for semantic search

If users are searching for exact, specific things - SKU numbers, error codes, names, legal clause references - keyword search is faster, cheaper, and more reliable. Same for structured data queries where you're filtering on known attributes like "4-star reviews from the last 30 days." That's a WHERE clause, not a search problem.

It's also a poor fit when your dataset is small. If you have 500 reviews, a simple ILIKE or basic full-text search works fine and you're adding real complexity (embedding pipeline, vector storage, model dependency) for marginal gain. The ROI scales with data volume and semantic diversity.

Another antipattern is when precision is critical and you can't tolerate fuzzy results. In legal or compliance contexts where someone searches for a specific regulation, returning a "semantically similar but different" regulation could be actively harmful. Keyword search is more predictable and auditable.

## Scaling Considerations

pgvector on a single Postgres node works fine up to a few million records. Beyond that, things get challenging.

At 100 million records with 1536 dimensions, vector storage alone is ~600GB. The HNSW index, which needs to hold a graph structure in memory, can push into terabytes depending on index parameters. A single Postgres node will struggle with that.

At that scale, most teams move to purpose-built vector databases like Pinecone, Weaviate, Milvus, or Qdrant. These are designed to shard and distribute vector indexes across multiple nodes, handle memory management more efficiently, and optimize specifically for nearest-neighbor queries. Same concept as outgrowing Postgres full-text search and moving to Elasticsearch.

There's also the embedding generation cost. Embedding 100 million records through an API is a significant upfront expense. And whenever your embedding model changes or improves, you'd ideally re-embed everything, making that cost recurring.

### Practical strategies at scale

You don't always need to embed everything. Common approaches include only embedding recent data (last 2 years of reviews), only embedding records above a certain length or quality threshold, and using smaller dimension models (384 vs 1536) to cut storage by 75%.

Tiered search is another approach: use keyword search or metadata filters to narrow down to a candidate set (maybe 50,000 records), then run semantic search only within that subset. This dramatically reduces the vector index size you need to maintain.

Production search systems at scale are rarely just one technique. It's usually a pipeline - metadata filters narrow the scope, keyword search produces candidates, semantic ranking reorders them, and there might be a separate ML model on top doing final ranking based on helpfulness, recency, and other signals. Each layer reduces the problem size for the next layer so you're never doing an expensive vector search across the full dataset.
