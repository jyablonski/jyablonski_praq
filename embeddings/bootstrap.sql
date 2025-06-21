-- extension needs to be installed in the database first
CREATE EXTENSION IF NOT EXISTS vector;

-- If your embedding has ~384 values, that means it exists in a 384-dimensional vector space. 
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding VECTOR(384) -- if using pgvector extension
);