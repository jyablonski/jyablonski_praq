import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import string


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

# Convert text to a document-term matrix
vectorizer = CountVectorizer(max_features=1000, stop_words="english")
doc_term_matrix = vectorizer.fit_transform(df["cleaned_text"])

# Train LDA model
num_topics = 7  # You can adjust this based on the dataset
lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
lda_model.fit(doc_term_matrix)

# # Get topic keywords
words = vectorizer.get_feature_names_out()
topic_keywords = []
for topic_idx, topic in enumerate(lda_model.components_):
    top_keywords = [words[i] for i in topic.argsort()[-10:]]  # Top 5 words per topic
    topic_keywords.append(top_keywords)


# Function to assign topic and subtopics
def get_topic(text):
    text_vectorized = vectorizer.transform([text])
    topic_distribution = lda_model.transform(text_vectorized)[0]
    topic_index = topic_distribution.argmax()  # Most dominant topic
    return f"Topic {topic_index + 1}", topic_keywords[topic_index]


# Apply topic modeling
df["Topic"], df["Subtopics"] = zip(*df["cleaned_text"].apply(get_topic))

# Display results
print(df[["cleaned_text", "Topic", "Subtopics"]].head())
