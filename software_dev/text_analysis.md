# Text Analysis

Analyzing text data has a wide range of applications, common use sases include:

### 1. Sentiment Analysis
- **Customer Feedback**: Analyzing reviews, surveys, and feedback forms to understand customer sentiments and opinions about products or services.
- **Social Media Monitoring**: Gauging public sentiment on social media platforms about specific topics, brands, or events.

### 2. Text Classification
- **Spam Detection**: Classifying emails or messages as spam or non-spam.
- **Document Categorization**: Automatically categorizing documents (e.g., legal documents, news articles) into predefined categories.

### 3. Topic Modeling
- **Content Discovery**: Identifying topics within large sets of text data to discover trends and patterns.
- **Document Organization**: Organizing large collections of documents by their topics for easier navigation and retrieval.

### 4. Content Moderation
- **PII Data**: Text Data that contains PII Data such as names, emails, phone numbers typically should be removed
- **Profanity Filtering**: Analyze text data to perform filtering of profanity and other harsh language

### 5. Fuzzy String Matching
- **String Matching**: Match Data from 2 different sources up using various algorithms such as Levenshtein Distance, which is a number that tells you how different 2 strings are

## Common Preprocessing Steps

Pre-processing text data is a crucial step before running any analysis or machine learning models. The goal is to clean and standardize the text data to improve the performance and accuracy of the models. Here are some common pre-processing steps:

1. **Lowercasing**:
   - Depending on the use case, convert all text to lowercase to ensure uniformity (e.g., "Apple" and "apple" are treated the same).
   - For official documents, this is a good idea.
   - For social media text data, this is probably a bad idea

2. **Removing Punctuation**:
   - Strip out punctuation marks such as commas, periods, exclamation points, etc., as they are usually not meaningful for text analysis.

3. **Tokenization**:
   - Split the text into individual words or tokens. This can be done by splitting on spaces or using more sophisticated tokenization techniques that handle contractions and punctuation.
   - Before: `text = "Tokenization is a fundamental step in natural language processing."`
   - After: `['Tokenization', 'is', 'a', 'fundamental', 'step', 'in', 'natural', 'language', 'processing', '.']`

4. **Removing Stop Words**:
   - Eliminate common words that do not carry significant meaning, such as "the," "and," "is," etc. Libraries like NLTK or spaCy provide lists of stop words.

5. **Stemming and Lemmatization**:
   - **Stemming**: Reduce words to their base or root form (e.g., "running" to "run").
   - **Lemmatization**: Convert words to their base or dictionary form (e.g., "running" to "run"), which is more accurate than stemming.

6. **Removing Special Characters**:
   - Strip out special characters (e.g., "@", "#", "$") unless they hold specific significance for the analysis (e.g., hashtags in social media analysis).

7. **Removing Whitespace**:
   - Eliminate extra whitespace, including leading and trailing spaces.

8. **Handling Negations**:
   - Treat negations carefully (e.g., "not happy" should be treated differently from "happy"). Some methods involve tagging negated words or creating bigrams that capture the negation context.

9.  **Spelling Correction**:
    - Correct spelling mistakes to ensure consistency. This can be done using libraries like TextBlob or autocorrect.

10. **Text Normalization**:
    - Normalize text by converting all characters to their canonical forms (e.g., converting accented characters to their unaccented counterparts).

11. **Removing HTML Tags**:
    - Remove HTML tags if the text data is scraped from web pages.

12. **N-grams Creation**:
    - Create n-grams (combinations of adjacent words) to capture more context (e.g., bigrams like "new york").

13. **Vectorization**:
    - Convert text data into numerical vectors using techniques like Bag of Words (BoW), Term Frequency-Inverse Document Frequency (TF-IDF), or word embeddings (e.g., Word2Vec, GloVe, BERT).


## Sentiment Analyis

Packages: `textblob` and `nltk`

NLTK comes with a pre-built Sentiment Analysis Model called VADER that's trained on social media data and has heavy influence towards that kind of language (short sentences, slang, emojis etc).

## Text Classification

Package: `https://github.com/adamspd/spam-detection-project`

## Topic Modeling

Package: `gensim` and `nltk`

The Latent Dirichlet Allocation (LDA) model is a generative probabilistic model used for topic modeling in text analysis. Its primary goal is to discover the underlying topics that are present in a collection of documents.

- Documents are mixtures of topics: Each document in a corpus is considered to be generated from a mixture of various topics.
- Topics are mixtures of words: Each topic is defined as a distribution over words.

Generative Process:
 - **Choose the number of topics \( K \)**.
 - For each topic \( k \), choose a distribution over words \(\beta_k\) from a Dirichlet prior.
 - For each document \( d \):
   - Choose a distribution over topics \(\theta_d\) from a Dirichlet prior.
   - For each word \( w \) in document \( d \):
     - Choose a topic \( z \) from the topic distribution \(\theta_d\).
     - Choose a word \( w \) from the word distribution corresponding to topic \( z \).

LDA basically takes a ton of text data and is able to identify logical groups or sets in that text data, and reports back the results it finds. Documents that frequently use words from a particular topic will have higher probabilities for that topic.

- Common stop words (e.g., "the," "is," "and") generally get lower probabilities because they are evenly distributed across all topics and do not contribute uniquely to any single topic.

The Results of LDA are:

- For each topic, LDA provides a distribution over the vocabulary, highlighting which words are more important (higher probability) for each topic.
- For each document, LDA provides a distribution over topics, showing which topics are more prominent in each document.

LDA Models are evaluated by coherence score, which is a measure used to describe the semantic similarity of words within a topic. A high coherence score indicates that the topics are more meaningful and interpretable to humans.

## Content Moderation

Package: `https://github.com/dimitrismistriotis/alt-profanity-check`

Something you could do is run 3 different checks using 3 separate packages or models on the text data you have. Then, if 2 out of those 3 checks believe the input text is offensive or has profanity, then mark it as offensive. Else, mark it as not offensive.

These tools aren't perfect. There will be false positives. There will be misses.

- b*tch - b1tch etc.

From the Author - "This library is far from perfect. For example, it has a hard time picking up on less common variants of swear words like "f4ck you" or "you b1tch" because they don't appear often enough in the training corpus. Never treat any prediction from this library as unquestionable truth, because it does and will make mistakes. Instead, use this library as a heuristic."