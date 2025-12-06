# Embeddings

An embedding is a mapping from discrete, often symbolic data (like words, images, or nodes) to points in a continuous vector space (usually ℝⁿ). Instead of dealing with raw, discrete data, embeddings let you represent entities as numeric vectors, enabling math operations, similarity calculations, and machine learning algorithms.

Embeddings allow you to take things like words which don't have natural numerical representation, and put them into higher-dimensional space (up to 50-1000+ dimensions) to:

- Capture semantic relationships (king is similar to queen)
- Allow use of linear algebra (dot products, distances, projections)
- Enable generalization (similar inputs get similar vectors)

Embeddings are learned from neural networks that use a large corpus of data and have specific training objectives that encourage similar items to have nearby vectors

## How It Works

1. Gather a dataset of data points that you want to build embeddings on
2. Create product embeddings for each item using a pretrained or custom embedding model
3. Create user embeddings based on user behavior like purchase, view/browser history, categories of interest etc
4. Store both embeddings in a vector database to enable fast similarity search
5. For each user, retrieve the most similar product embeddings by calculating similarity scores against stored embeddings
6. Serve the top-k closest products as personalized recommendations.

Computing similarity scores for all documents doesn't really make sense because it's very slow and expensive as data volume increases.

- Instead, you typically take a user embedding `u` and a catalog of product embeddings `Vi`, and compute similarity between `u` and `Vi` so you can return the top-k products with the highest scores

## Embedding Use Cases

1. Natural Language Processing - turn words or documents into vectors for things like sentiment analysis and similarity search
2. Semantic Search - Find documents or items related to a relevant query
3. Recommendation Systems - represent users and items as embedding vectors, compute similarities, and recommend items whose embeddings are closest to the user's embedding
4. Image Search - represent images as vectors to compare, classify, or search images

## Embedding Example Workflows

1. Google Search - semantic search w/ word & sentence embeddings

   - Google uses approximate nearest neighbor search to find pages whose embeddings are close to the query embedding, returning results semantically related, not just keyword matches.
   - Users get more relevant results for ambiguous or complex queries.

2. Spotify - Music Recommendations

   - Spotify collects user interaction data like play counts and skips, learns embeddings for users and songs in the same vector space, computes similarity scores for user's embedding and song embeddings, and then recommends them the most similar ones
   - This enables a highly personalized playlist that feels intuitive and custom

3. LinkedIn - Job Matching

   - LinkedIn creates embeddings for job descriptions, skills, and user profiles
   - Both candidates and jobs are mapped into a shared vector space
   - Matches are performed by measuring embedding similarity between candidate profiles and job postings
   - Users get better matches, improved candidate engagement.

4. Amazon - Product Search and Recommendations
   - Amazon generates embeddings for product descriptions, titles, and user queries
   - Embeddings help search ranking by semantic relevance
   - User purchase and browsing history is used to build user embeddings
   - Recommendations use embedding similarity to suggest complementary or alternative products
   - Leads to higher conversion rates and user satisfaction

## Generating Embeddings

### Step 1: The Model (The "Translator")

Actually taking input data and generating embeddings involves using a Transformer Model (like BERT or OpenAI's text-embedding-3).

- This model is essentially a massive, pre-trained neural network that has learned over billions of sentence pairs to learn which sentences usually share the same meaning.
  - It "knows" that "cellular phone" and "mobile device" are semantically identical, even though they share no common words.
- You feed it raw text ("The quick brown fox").
- It passes that text through layers of math operations.
- The final layer outputs a fixed-length list of floating-point numbers (e.g., `[0.1, -0.9, 0.4 ...]`).
- Code Level: In Python, this is often just an API call to OpenAI or a local library like `sentence-transformers` or `HuggingFace`.

### Step 2: The Storage (Postgres + pgvector)

Postgres by itself doesn't understand vector math. You need to install the `pgvector` extension.

- This allows Postgres to store a new data type: `vector(1536)`.
- It allows you to run special SQL queries like "Find the 5 rows whose vector is mathematically closest to this query vector."

### Real-time Code Example

```python
@app.post("/reviews")
def upload_reviews(payload: UserInput):

   review = payload.review_text

   # do something like write a review - like normal
   write_review_to_database(review=review)

   # also send the review to an embedding queue for async processing
   send_review_to_embedding_queue(review=review)

   return {"status": "success"}
```

### The Comparison: Event-Driven vs. Batch Polling

| Feature      | Event-Driven (Queue)                                             | Batch Polling (Cron)                                                      |
| :----------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------ |
| Latency      | Near Real-time: Embeddings exist seconds after upload.           | High Latency: Embeddings appear whenever the job runs (e.g., every hour). |
| Complexity   | High: Requires a Broker (Redis/RabbitMQ) and worker maintenance. | Low: Just a script and a scheduler (cron, Airflow).                       |
| API Costs    | Higher/Inefficient: You make 1 API call per review.              | Lower/Optimized: You send 100 reviews in 1 API call (batching).           |
| Failure Mode | If the queue fills up or crashes, you might lose messages.       | If the job fails, it just picks up the same pending rows next time.       |

### 2\. When to use which?

- Use the Queue (Real-time) if the user needs immediate feedback.
  - _Example:_ A user types a review and immediately sees "Here are 3 other reviews similar to yours\!"
- Use Batching (Polling) for almost everything else.
  - _Example:_ You are building a recommendation engine that updates nightly, or internal analytics dashboards. If the user doesn't see the result immediately, Batch is best practice because it puts less load on your database and saves money on API calls.

---
