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
