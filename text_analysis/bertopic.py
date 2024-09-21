# use bertopic
from bertopic import BERTopic
import pandas as pd
from sklearn.datasets import fetch_20newsgroups

topic_model = BERTopic()

df = pd.read_csv("text_analysis/example_text.csv")

topics, _ = topic_model.fit_transform(df["text"])
df["topic"] = topics

print(topic_model.get_topic_info())

topic_model.visualize_topics()

docs = fetch_20newsgroups(subset="all", remove=("headers", "footers", "quotes"))["data"]

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(docs)

topic_model.get_topic_info()
