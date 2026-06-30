import hdbscan
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import umap
from sentence_transformers import SentenceTransformer
from typing import Any, List, Dict

model = SentenceTransformer("distilbert-base-nli-mean-tokens")


def encode_text_to_embeddings(text_data: List[str]) -> np.ndarray:
    """
    Encode a list of text documents into 512-dimensional embeddings.
    """
    return model.encode(text_data, show_progress_bar=True)


def reduce_dimensionality(embeddings: np.ndarray, n_components: int = 5) -> np.ndarray:
    """
    Reduce dimensionality of the embeddings using UMAP.
    """
    umap_embeddings = umap.UMAP(
        n_neighbors=15, n_components=n_components, metric="cosine"
    ).fit_transform(embeddings)
    return umap_embeddings


def apply_hdbscan(umap_embeddings: np.ndarray) -> hdbscan.HDBSCAN:
    """
    Apply HDBSCAN clustering on the reduced embeddings.
    """
    cluster = hdbscan.HDBSCAN(
        min_cluster_size=15, metric="euclidean", cluster_selection_method="eom"
    ).fit(umap_embeddings)
    return cluster


def create_clustered_df(
    text_data: List[str], cluster_labels: np.ndarray
) -> pd.DataFrame:
    """
    Create a DataFrame with text documents and their corresponding cluster labels.
    """
    docs_df = pd.DataFrame(text_data, columns=["Doc"])
    docs_df["Topic"] = cluster_labels
    docs_df["Doc_ID"] = range(len(docs_df))
    return docs_df


def c_tf_idf(documents: List[str], m: int, ngram_range: tuple = (1, 1)) -> tuple:
    """
    Compute the term frequency-inverse document frequency (TF-IDF) of a set of documents.
    """
    count = CountVectorizer(ngram_range=ngram_range, stop_words="english").fit(
        documents
    )
    t = count.transform(documents).toarray()
    w = t.sum(axis=1)
    tf = np.divide(t.T, w)
    sum_t = t.sum(axis=0)
    idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
    tf_idf = np.multiply(tf, idf)
    return tf_idf, count


def extract_top_n_words_per_topic(
    tf_idf: np.ndarray,
    count: CountVectorizer,
    docs_per_topic: pd.DataFrame,
    n: int = 20,
) -> Dict:
    """
    Extract the top N words for each topic based on their TF-IDF scores.
    """
    words = count.get_feature_names_out()
    labels = list(docs_per_topic.Topic)
    tf_idf_transposed = tf_idf.T
    indices = tf_idf_transposed.argsort()[:, -n:]
    top_n_words = {
        label: [(words[j], tf_idf_transposed[i][j]) for j in indices[i]][::-1]
        for i, label in enumerate(labels)
    }
    return top_n_words


def assign_topic_labels(top_n_words: Dict[Any, List[tuple]]) -> Dict[str, str]:
    """
    Assign human-readable labels to topics based on predefined sets of keywords.
    """
    predefined_labels = {
        "Technology": [
            "computer",
            "software",
            "program",
            "system",
            "internet",
            "AI",
            "machine",
            "algorithm",
            "data",
            "network",
        ],
        "Sports": [
            "game",
            "team",
            "player",
            "score",
            "match",
            "tournament",
            "league",
            "coach",
            "championship",
            "athlete",
        ],
        "Politics": [
            "government",
            "election",
            "policy",
            "president",
            "vote",
            "senate",
            "congress",
            "law",
            "democracy",
            "campaign",
        ],
        "Business & Finance": [
            "market",
            "stock",
            "investment",
            "company",
            "economy",
            "trade",
            "entrepreneur",
            "revenue",
            "business",
            "profit",
        ],
        "Science": [
            "physics",
            "biology",
            "chemistry",
            "experiment",
            "research",
            "theory",
            "scientific",
            "quantum",
            "genetics",
            "molecule",
        ],
        "Health & Medicine": [
            "doctor",
            "hospital",
            "medicine",
            "disease",
            "surgery",
            "treatment",
            "vaccine",
            "virus",
            "diagnosis",
            "therapy",
        ],
    }

    topic_labels = {}
    for topic, words in top_n_words.items():
        topic_words = [word for word, _ in words]
        assigned_label = "Unknown"  # Default label
        for label, keywords in predefined_labels.items():
            if any(word in topic_words for word in keywords):
                assigned_label = label
                break  # Assign the first matching label
        topic_labels[topic] = assigned_label

    return topic_labels


def process_text_data(text_data: List[str]) -> pd.DataFrame:
    """
    Complete pipeline: Encode text, reduce dimensions, apply clustering, and label topics.
    """
    # Step 1: Encode text data into embeddings
    embeddings = encode_text_to_embeddings(text_data)

    # Step 2: Reduce dimensionality of embeddings using UMAP
    umap_embeddings = reduce_dimensionality(embeddings, n_components=5)

    # Step 3: Apply HDBSCAN clustering on reduced embeddings
    cluster = apply_hdbscan(umap_embeddings)

    # Step 4: Create a DataFrame with documents and their corresponding topics
    docs_df = create_clustered_df(text_data, cluster.labels_)

    # Step 5: Extract TF-IDF and top words per topic
    tf_idf, count = c_tf_idf(documents=docs_df["Doc"].values, m=len(text_data))
    top_n_words = extract_top_n_words_per_topic(tf_idf, count, docs_df, n=20)

    # Step 6: Assign human-readable topic labels
    topic_labels = assign_topic_labels(top_n_words)

    # Add the topic labels to the DataFrame
    docs_df["Topic_Label"] = docs_df["Topic"].map(topic_labels)

    return docs_df, top_n_words, topic_labels


if __name__ == "__main__":
    text_data = list(pd.read_csv("text_analysis/example_text.csv")["text"])

    docs_df, top_n_words, topic_labels = process_text_data(text_data)

    print(docs_df)
    print("Top words per topic:", top_n_words)
    print("Topic labels:", topic_labels)
