# Recommendation Systems

Recommendation systems predict what users might like based on patterns in their behavior, preferences, and characteristics. Companies use them to increase engagement, drive sales, improve user experience, and help users discover relevant content they might otherwise miss.

## Core Approaches

### Collaborative Filtering

Collaborative filtering assumes that users who agreed in the past will agree in the future. If Customer A and B both like items X, Y, and Z, then if Customer A buys a new item, we can probably recommend that to Customer B.

Two main types:

- User-based: Find similar users based on their interaction patterns, then recommend items those similar users liked
- Item-based: Find similar items based on which users interacted with them, then recommend items similar to what the user already likes

Techniques:

- Matrix factorization (SVD, ALS)
- Nearest neighbors (KNN)
- Neural collaborative filtering

Strengths: Works without item metadata, discovers unexpected patterns

Weaknesses: Cold start problem (new users/items), sparsity issues, popularity bias

### Content-Based Filtering

Content-based filtering recommends items similar to what you've liked before by analyzing item features and building a user preference profile.

Example: If you watch a lot of action movies, it'll recommend other action movies based on genre, actors, directors, cinematography style, etc.

Techniques:

- TF-IDF for text content
- Feature engineering from metadata
- Embedding-based similarity (word2vec, BERT for text)

Strengths: No cold start for new users, explainable recommendations, works with limited interaction data

Weaknesses: Limited serendipity, filter bubbles, requires rich item metadata, can't capture quality signals

### Hybrid Systems

Combine multiple approaches to overcome individual limitations.

Common strategies:

- Weighted: Combine scores from different models
- Switching: Choose different models based on context (e.g., content-based for new users)
- Feature combination: Use collaborative features in content-based models
- Cascade: Use one model to filter, another to rank

## Modern Production Systems

Modern recommendation systems use multi-stage architectures with increasing complexity:

### 1. Candidate Generation (Retrieval)

Fast retrieval of hundreds/thousands of potentially relevant items from millions

- Collaborative filtering models
- Content-based retrieval
- Popularity/trending items
- Graph-based methods (items users like you interacted with)

### 2. Ranking

Score and rank candidates using more sophisticated models

- Gradient boosted trees (XGBoost, LightGBM)
- Deep learning (Wide & Deep, DeepFM, two-tower models)
- Learning-to-rank algorithms

### 3. Re-ranking & Business Logic

Apply final adjustments and constraints

- Diversity promotion
- Business rules (inventory, margins)
- Freshness boosting
- Filter bubbles mitigation
- Contextual adjustments (time of day, device)

## Data Pipeline

The data pipeline is critical for recommendation quality:

Data Collection:

- Implicit signals: clicks, watch time, scroll depth, hover events, add-to-cart
- Explicit feedback: ratings, likes, purchases, reviews
- Context: time, location, device, session information

Feature Engineering:

- User features: demographics, lifetime value, engagement history
- Item features: metadata, popularity, recency, content embeddings
- Interaction features: user-item history, co-occurrence patterns
- Contextual features: seasonality, trending topics

Processing:

- Real-time stream processing (for immediate signals like clicks)
- Batch processing (for compute-intensive embeddings)
- Feature stores for serving low-latency lookups

## Evaluation Metrics

Offline Metrics:

- Accuracy: Precision@K, Recall@K, MAP (Mean Average Precision)
- Ranking: NDCG (Normalized Discounted Cumulative Gain), MRR (Mean Reciprocal Rank)
- Coverage: Catalog coverage, diversity metrics
- Prediction: RMSE, MAE (for rating prediction)
- Basically measuring the results of these recommendation systems on historical data before deploying to real users

Online Metrics (most important):

- Click-through rate (CTR)
- Conversion rate
- Engagement time
- Revenue per user
- User retention
- These measure what your recommendation systems actually do: are they improving retention, conversions etc

Example scenario:

- Your new model has 15% better Precision
- You deploy it in an A/B test...
- But CTR only goes up 2%, and revenue actually drops slightly

## Experimentation & Iteration

A/B Testing:

- Randomly assign users to treatment/control groups
- Measure impact on key metrics over time (typically 1-2 weeks minimum)
- Watch for novelty effects and long-term trends
- Statistical significance testing (t-tests, bootstrap confidence intervals)

Common Experiments:

- Algorithm changes (new model architectures)
- Feature additions/removals
- Ranking weight adjustments
- UI/UX changes (how recommendations are displayed)
- Diversity vs relevance tradeoffs

Multi-armed Bandits:

- Epsilon-greedy, Thompson sampling, UCB
- Balance exploration vs exploitation
- Faster iteration than full A/B tests for some use cases

## Deployment Considerations

Infrastructure:

- Model serving infrastructure (TensorFlow Serving, Seldon, custom services)
- Caching layers (Redis, Memcached) for frequently accessed recommendations
- Load balancing and horizontal scaling
- Latency budgets (typically 50-200ms for recommendation serving)

Monitoring:

- Model performance degradation
- Data drift detection
- System health (latency, error rates, throughput)
- Business metrics dashboards

Refresh Strategy:

- How often to retrain models (daily, weekly)
- When to update user/item embeddings
- Real-time vs batch prediction

## Common Challenges

Cold Start Problem:

- New users: Use content-based methods, popular items, or onboarding questionnaires
- New items: Promote to exploratory users, use content features, or bootstrap with contextual bandits

Scalability:

- Approximate nearest neighbors (FAISS, Annoy, ScaNN) for large catalogs
- Model compression and quantization
- Distributed training and serving

Bias & Fairness:

- Popularity bias (over-recommending popular items)
- Position bias (users click top results regardless of quality)
- Feedback loops (recommending -> clicking -> more recommendations)
- Filter bubbles and echo chambers

Explainability:

- Why was this recommended? (crucial for user trust)
- Regulatory requirements in some domains

## Key Technical Concepts

### Embeddings

Embeddings capture relationships between items (or users) as vectors (arrays of integers) in a multi-dimensional space where the position and distance between vectors represents similarity.

Example: The movie "Inception" might be represented as [0.8, 0.2, 0.9, ...] where the dimensions loosely capture concepts like "sci-fi-ness", "complexity", "action level" (learned automatically, not manually defined).

Why they matter:

- Enable finding similar items even without direct user interactions
- Power modern deep learning recommendation systems
- Can represent text, images, users, or items in the same mathematical space

```text
"Inception":        [0.9, 0.1, 0.8, 0.2] -> High sci-fi, low romance
"Interstellar":     [0.85, 0.15, 0.75, 0.3]  -> Very close to Inception!
"The Notebook":     [0.1, 0.9, 0.2, 0.1]  -> Low sci-fi, high romance (far away)
```

- The distance between "Inception" and "Interstellar" is small -> they're similar.
- The distance between "Inception" and "The Notebook" is large -> they're different.

Instead of just 4 numbers, real embeddings might have 128, 256, or 512 dimensions. Mpre dimensions allow more nuanced relationships to be captured. But, we cant visualize beyond 3D, so we just work with the math.

pgvector extension in Postgres enables vector storage and similarity search capabilities. Performance can be improved with indexes.

- End results allows for similarity search or recommendation type queries to be made.

Embeddings come from an ML Model being trained on a set of input data where the output is a set of embeddings for everything in the training set.

- This output data is then stored in Postgres and used for similarity search etc

### K-Nearest Neighbors (KNN)

KNN finds the K most similar items (or users) based on a similarity metric, then uses their data to make recommendations. The intuition: "Show me what people similar to me liked" or "Show me items similar to what I already like"

- In practice, item-based is more common because items change less frequently than user preferences (more stable, easier to precompute).

Examples:

- Find the 10 users most similar to you (based on viewing history), then recommend movies those 10 users watched that you haven't.
- Users like you also watched...

Simple but effective - still used in production systems, especially for explainability

But, some limitations exist such as:

- With 1M items, you have ~1 trillion possible pairs to compute
- Cold start: New items have no interaction data yet

### Matrix Factorization

Breaks down the user-item interaction matrix into simpler patterns by finding hidden "factors" that explain preferences.

Think of it like: Instead of storing "User A rated Movie B: 5 stars" for millions of combinations, find ~50 hidden factors (like "action lover", "prefers indie films") that describe both users and movies, then multiply them to predict ratings.

Classic algorithms: SVD, ALS (Alternating Least Squares)

Why it works: Most preferences can be explained by a small number of underlying patterns

### Two-Tower Models

Modern architecture with separate neural networks for users and items that create embeddings, then measures how well they match.

Structure:

- User tower: Takes user features -> produces user embedding
- Item tower: Takes item features -> produces item embedding
- Match score: How similar are these embeddings? (dot product)

Big advantage: You can pre-compute all item embeddings once, then only compute the user embedding at request time -> super fast recommendations even with millions of items

### Approximate Nearest Neighbors (ANN)

Algorithms that quickly find "similar enough" items without checking every single one - crucial for scaling to massive catalogs.

The problem: Finding exact nearest neighbors in millions of items takes too long (seconds)

The solution: Trade a tiny bit of accuracy for massive speed gains (milliseconds)

Popular tools: FAISS (Facebook), Annoy (Spotify), ScaNN (Google)

Real-world example: Spotify has 100M+ songs - they can't compare your taste to every song in real-time, so ANN finds the ~1000 most promising candidates in milliseconds, then a more sophisticated model ranks those.
