import psycopg2
from psycopg2.extensions import connection as PGConnection
from sentence_transformers import SentenceTransformer


def get_pg_connection() -> PGConnection:
    """
    Establishes a PostgreSQL connection with autocommit enabled.

    Returns:
        A psycopg2 connection object.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
    )
    conn.autocommit = True
    return conn


def clear_embeddings_table(conn: PGConnection) -> None:
    """
    Deletes all rows from the embeddings table.

    Args:
        conn: A psycopg2 PostgreSQL connection.
    """
    with conn.cursor() as cur:
        cur.execute("DELETE FROM embeddings;")


def insert_reviews(
    conn: PGConnection, model: SentenceTransformer, reviews: list[str]
) -> None:
    """
    Creates embeddings for each review and inserts them into the database

    Args:
        conn: A psycopg2 PostgreSQL connection.
        model: A SentenceTransformer model used for encoding.
        reviews: A list of review strings to embed and insert.
    """
    embeddings = model.encode(reviews)
    with conn.cursor() as cur:
        for review, emb in zip(reviews, embeddings):
            cur.execute(
                "INSERT INTO embeddings (text, embedding) VALUES (%s, %s);",
                (review, emb.tolist()),
            )


def query_similar_reviews(
    conn: PGConnection, model: SentenceTransformer, query: str, limit: int = 5
) -> list[tuple[int, str, float]]:
    """
    Finds the most similar reviews to the given query using pgvector similarity search.

    Args:
        conn: A psycopg2 PostgreSQL connection.
        model: A SentenceTransformer model used for encoding the query.
        query: The input text to compare against stored reviews.
        limit: The number of similar results to return.

    Returns:
        A list of (id, text, distance) tuples ordered by similarity.
    """
    query_embedding = model.encode([query])[0].tolist()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, text, embedding <-> %s::vector AS distance
            FROM embeddings
            ORDER BY distance
            LIMIT %s;
            """,
            (query_embedding, limit),
        )
        return cur.fetchall()


def print_similar_reviews(title: str, results: list[tuple[int, str, float]]) -> None:
    """
    Pretty-prints the top similar reviews.

    Args:
        title: The title for the result section.
        results: List of (id, text, distance) tuples.
    """
    print(f"\n{title}")
    for id, text, distance in results:
        print(f"ID: {id} | Distance: {distance:.4f} | Text: {text}")


if __name__ == "__main__":
    REVIEWS = [
        "Great product, very useful and easy to use.",
        "Terrible customer service, I'm very disappointed.",
        "I love the design and the performance is excellent.",
        "Not worth the price, it broke after a week.",
        "Fantastic experience, will buy again!",
        "Poor quality and bad packaging.",
        "Amazing features and great battery life.",
        "The product does not match the description.",
        "Five stars, highly recommend to everyone.",
        "Worst purchase I've made this year.",
        "Superb quality and quick delivery.",
        "The instructions were confusing and unclear.",
        "Exceeded my expectations in every way.",
        "The item arrived damaged and late.",
        "Customer support resolved my issue quickly.",
        "Disappointed with the durability of the product.",
        "Works perfectly and very intuitive to use.",
        "Cheap materials, feels fragile.",
        "Love it! The color and style are perfect.",
        "Stopped working after a month.",
        "Very happy with my purchase.",
        "Not as described, will return it.",
        "Excellent value for the price.",
        "Shipping took too long.",
        "I am impressed with the quality and service.",
    ]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    conn = get_pg_connection()

    clear_embeddings_table(conn=conn)
    insert_reviews(conn=conn, model=model, reviews=REVIEWS)

    pos_query = "I love this product, very high quality!"
    neg_query = "Disappointed with my purchase, wouldn't do it again"

    pos_results = query_similar_reviews(conn=conn, model=model, query=pos_query)
    print_similar_reviews("Similar to Positive Review:", pos_results)

    neg_results = query_similar_reviews(conn=conn, model=model, query=neg_query)
    print_similar_reviews("Similar to Negative Review:", neg_results)

    conn.close()
