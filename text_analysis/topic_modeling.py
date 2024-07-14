import gensim
import gensim.corpora as corpora
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim.models import CoherenceModel
import nltk

# Download stopwords from NLTK
nltk.download("stopwords")
nltk.download("punkt")

# Sample text data
documents = [
    "The economy is showing signs of improvement.",
    "The stock market is doing well.",
    "Inflation is on the rise.",
    "Employment numbers are up.",
    "The new policy will affect the economy.",
    "Companies are hiring more employees.",
]

# Preprocess the data
stop_words = set(stopwords.words("english"))


def preprocess(text):
    tokens = word_tokenize(text.lower())
    tokens = [
        word for word in tokens if word.isalpha()
    ]  # Remove punctuation and numbers
    tokens = [word for word in tokens if word not in stop_words]  # Remove stopwords
    return tokens


# Tokenize and clean the documents
texts = [preprocess(doc) for doc in documents]

# Create a dictionary representation of the documents
id2word = corpora.Dictionary(texts)

# Create a corpus from the dictionary representation
corpus = [id2word.doc2bow(text) for text in texts]

# Train the LDA model
lda_model = gensim.models.LdaModel(
    corpus=corpus,
    id2word=id2word,
    num_topics=3,
    random_state=42,
    update_every=1,
    chunksize=10,
    passes=10,
    alpha="auto",
    per_word_topics=True,
)

# Iterate through the topics and print the most significant words for each topic.

for idx, topic in lda_model.print_topics(-1):
    print(f"Topic: {idx}\nWords: {topic}\n")

# Compute coherence score
coherence_model_lda = CoherenceModel(
    model=lda_model, texts=texts, dictionary=id2word, coherence="c_v"
)
coherence_lda = coherence_model_lda.get_coherence()
print(f"\nCoherence Score: {coherence_lda}")
