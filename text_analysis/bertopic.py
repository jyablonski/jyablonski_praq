from bertopic import BERTopic
import pandas as pd
from sklearn.datasets import fetch_20newsgroups

# load in the sample dataset to generate topics for
data = fetch_20newsgroups(subset="all")["data"]

topic_model = BERTopic()

topics, probs = topic_model.fit_transform(data)

# -1 topics mean outliers
# topic id and then top n words
topic_model.get_topic_info()

topic_labels = topic_model.generate_topic_labels(
    nr_words=6, topic_prefix=False, word_length=15, separator=" - "
)

topic_model.set_topic_labels(topic_labels)

# override & set custom label
topic_model.set_topic_labels({0: "Cars"})
topic_model.get_topic_info().head(5)
topic_model.reduce_topics(docs=data, nr_topics=25)

topic_model.visualize_barchart(width=280, height=330, top_n_topics=12, n_words=10)

# get the topics back onto the row level datas
df = pd.DataFrame({"Document": data, "Topic": topics})

# Get the topic representation (top words per topic)
topic_info = topic_model.get_topic_info()

# Print topic summary
print(topic_info.head(10))

# Map each topic to its most representative words
topic_labels = topic_model.get_topic_info().set_index("Topic")["Name"].to_dict()
df["Topic_Label"] = df["Topic"].map(topic_labels)
