import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import string
import matplotlib.pyplot as plt

# Download stopwords
nltk.download("stopwords")

# Load the dataset
df = pd.read_csv("text_analysis/example_text.csv")


# Define a preprocessing function
def preprocess_text(text: str) -> str:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    stop_words = set(stopwords.words("english"))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    return " ".join(words)


# Apply preprocessing
df["cleaned_text"] = df["text"].apply(preprocess_text)

# Create a CountVectorizer
vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words="english")
text_data = vectorizer.fit_transform(df["cleaned_text"])
words = vectorizer.get_feature_names_out()

# Create the LDA model
n_topics = 5
lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
lda.fit(text_data)


# Display top words per topic
def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print(f"Topic {topic_idx}:")
        print(
            " ".join(
                [feature_names[i] for i in topic.argsort()[: -n_top_words - 1 : -1]]
            )
        )


n_top_words = 10
print_top_words(lda, words, n_top_words)

# Get the document-topic matrix
doc_topic_matrix = lda.transform(text_data)
df["dominant_topic"] = doc_topic_matrix.argmax(axis=1)

# Show the dominant topic for each document
print(df[["text", "dominant_topic"]].head())

# Plot the distribution of topics
plt.hist(df["dominant_topic"], bins=n_topics, align="left")
plt.xlabel("Topic")
plt.ylabel("Number of Documents")
plt.title("Topic Distribution")
plt.show()
