# Profanity Filtering

Profanity filtering is commonly implemented in user-facing reviews, testimonials, or other user-generated text that might be put in front of other users at a large scale.

At a high level, profanity filtering involves a series of steps to actually take text and see if it contains bad or sensitive words

### 1. Input: Receive Arbitrary Text

- Source: User input (e.g. chat, username, post, comment, etc.)
- Format: Unstructured plain text (e.g. `"you’re such a b1tch!"`)

### 2. Preprocessing

Before checking for profanity, the system normalizes the text to make detection more effective:

- Lowercasing: `"B1tCh"` → `"b1tch"`

From there, there are multiple options to actually handle special characters and punctuation:

1. Strip punctuation/special chars (optional): `"b!tch"` → `"btch"` or `"bitch"`

- This is much simpler to implement
- You risk false negatives being introduced where you have some bad text that isn't getting filtereds

2. Character normalization: Replace common substitutions like:

- `1 → i`, `! → i`, `@ → a`, `3 → e`, etc.
- This is typically more processing, requires a mapping of all special characters to consider, and can lead to false positives
- But, it directly leads to higher detection accuracy by not stripping anything out

### 3. Detection

This is the core logic that identifies offensive language, and also has multiple approaches:

1. Dictionary/wordlist lookup:

- Exact match: `"bitch"` found in profanity list
- Simple to setup a hash / set lookup, good performance
- Deterministic results: guaranteed to get yes or no answers back
- Low false positive rate because we only flag exact known bad words
- But, high potential false negative rate because things like "biatch" might not get flagged at all

2. Fuzzy match:

- You compare each input word with each word in your banned list using similarity metrics like Levenshtein distance, Jaro Winkler etc
- `"b1tch"` matches `"bitch"` with tolerance
- Poorer performance because we have much more to check now
- You need to tune similarity thresholds depending on what you're comfortable with (high threshold -> you potentially catch more words, but end up with more false positives)

3. ML/heuristic-based detection (optional for advanced systems):

- Context-aware: Distinguishes `"ass"` in `"assistant"` vs `"you're an ass"`
- Accounts for obfuscation and cultural variations
- The most advanced option, but can help catch scenarios that you wouldn't otherwise be able to do with the first 2 options

### 4. Replacement or Action

After running the text through the profanity filtering, there are various options for what you can do with the results:

- Redact/replace:

  - Replace whole word: `"bitch"` → `"*****"`
  - Mask vowels or partial: `"bitch"` → `"b*tch"`

- Reject input (e.g., a user submitted an offensive review that you don't allow)
- Flag for moderation (human review / QA to go take a look)

### Summary Workflow

```text
User Input
   ↓
Normalize the Text
   ↓
Perform the Profanity Check
   ↓
If match:
    → Replace/Mask/Reject/Flag
Else:
    → Accept as is
```
