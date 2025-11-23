# ML Notes

High level flow:

1. Load/Generate Data
2. Prepare Features
3. Split Data
4. Train Model (with MLflow tracking)
5. Evaluate
6. Save to MLflow

**Must-have methods:**

1. `load_data()` or `generate_data()`
2. `prepare_features()` - transforms + returns encoders
3. `train_model()` - wrapped in `mlflow.start_run()`
4. `main()` - orchestrates everything

**MLflow essentials:**

- `mlflow.set_tracking_uri()` - connect to server
- `mlflow.set_experiment()` - organize runs
- `mlflow.start_run()` - start tracking
- `mlflow.log_param()` - log hyperparameters
- `mlflow.log_metric()` - log performance
- `mlflow.sklearn.log_model()` - save model

## Model Input

Definition Location: Feature preparation/engineering function (e.g., `prepare_features()`)

Model inputs must be explicitly defined, transformed, and combined before training. Raw data needs to be converted into numerical features that machine learning models can process.

Common Input Transformation Pipeline:

1. Identify raw inputs - Determine what data the model will receive

   - Categorical data (text, IDs, categories)
   - Numerical data (integers, floats)
   - Text data (strings, documents)

2. Feature engineering - Transform raw inputs into model-ready features:

   - One-hot encoding: Converts categorical data into binary vectors
     - Categorical value -> Binary columns (1 = present, 0 = absent)
     - Example: `"category_A"` -> `[1, 0, 0, 0]`
   - Normalization/Scaling: Standardizes numerical values to similar ranges
     - Prevents features with large values from dominating
     - Common methods: z-score normalization, min-max scaling
   - Embedding: Converts high-dimensional categorical data to dense vectors (for text, IDs)
   - Binning: Groups continuous values into discrete buckets

3. Combine features - Concatenate all transformed features into a single vector
   - Creates the final input that gets fed into the model
   - Example: `[categorical_features + numerical_features + text_features]`

Key Point: Models only understand numbers. Feature engineering bridges the gap between human-readable data and machine-readable numerical vectors. The way you define and transform inputs directly impacts model performance.

Example - Article Recommendation System:

- Raw inputs: `article_ids_read` (list), `favorite_topics` (list), `time_on_site` (int)
- Transformed: 50 one-hot features + 10 one-hot features + 1 normalized feature = 61-dimensional vector

## Model Output

Definition Location: Prediction/inference function (e.g., `predict()` method)

Model outputs are the raw predictions from the trained model, which typically need post-processing to be human-readable and useful for applications.

Prediction Pipeline:

1. Raw model output - What the model actually produces:

   - Classification: Probability scores for each possible class
   - Regression: Continuous numerical values
   - Multi-label classification: Probability scores for multiple labels simultaneously

2. Post-processing - Transform raw outputs into actionable results:

   - Thresholding: Convert probabilities to binary decisions (e.g., >0.5 = positive class)
   - Argmax: Select the class with highest probability
   - Top-K selection: Return the K items with highest scores
   - Filtering: Remove invalid/unwanted predictions
   - Sorting/Ranking: Order results by confidence/relevance

3. Return format - Convert to API-friendly format:
   - Map from internal representation (indices, vectors) back to human-readable labels
   - Format as JSON, list, or structured object

Common Prediction Methods:

- `model.predict()`: Returns the most likely class (already processed)
- `model.predict_proba(X)`: Returns probability scores for all classes
  - Used when you want to see confidence levels, not just final decision
  - Example: `[0.1, 0.8, 0.05, 0.05]` means 80% confidence in class 2
  - Extract single prediction: `model.predict_proba(X)[0]` (first row of results)

Key Point: Raw model outputs are often numerical probabilities or scores. The `predict()` method wraps the model with business logic to convert these numbers into the specific format your application needs.

Example - Article Recommendation System:

- Raw output: 50 probability scores (one per article) -> `[0.92, 0.03, 0.87, ...]`
- Post-processing: Sort by score, filter out already-read articles, select top 5
- Final output: `["article_15", "article_20", "article_25", "article_30", "article_35"]`

## Model Parameters

Training loop:

1. Take 32 samples (batch_size)
2. Make predictions
3. Calculate error
4. Update weights by 0.001 (learning_rate)
5. Repeat for all batches
6. That's 1 epoch
7. Do this 50 times (epochs)

### model_type: "pytorch_nn"

- Just a label saying you used PyTorch neural network
- vs scikit-learn, TensorFlow, etc.
- Helps you remember what framework you used

### epochs: 50

- How many times the model saw the entire training dataset
- 50 passes through all 2000 samples
- More epochs = more learning (but can overfit)
- 50 is standard for this size dataset

### batch_size: 32

- How many samples processed before updating weights
- Your model sees 32 examples -> calculates error -> adjusts weights -> repeat
- Smaller = more updates, noisier learning
- Larger = fewer updates, smoother learning
- 32 is a common default

### learning_rate: 0.001

- How much to adjust weights after each batch
- Too high (0.1) = learning too fast, might miss optimal solution
- Too low (0.00001) = learning too slow, takes forever
- 0.001 is a safe starting point for Adam optimizer

## Model Performance

### val_loss: 0.223 (Lower is better)

- This is Binary Cross-Entropy loss on validation data
- Measures how "wrong" the model's predictions are
- 0.223 is pretty good for multi-label classification
- Range: 0 (perfect) to ∞ (terrible)

### precision: 0.624 (62.4%)

- Of the articles the model recommends, 62.4% are actually relevant
- "When the model says yes, how often is it right?"
- Higher = fewer false positives (bad recommendations)

### recall: 0.367 (36.7%)

- Of all the relevant articles, the model finds 36.7% of them
- "How many of the good articles did we catch?"
- Lower = missing some good recommendations

### f1_score: 0.444 (44.4%)

- Harmonic mean of precision and recall
- Overall quality score
- Balances "accuracy" vs "coverage"

### Experiment vs Model

```
Experiment: "article_recommendations"
├── Run 1 (Nov 20, lr=0.001, F1=0.42)
│   └── Model artifact (not registered)
├── Run 2 (Nov 21, lr=0.01, F1=0.38)
│   └── Model artifact (not registered)
└── Run 3 (Nov 21, lr=0.001, epochs=100, F1=0.47) ✓ BEST
    └── Model artifact -> Register as "article_recommender_v1"

Model Registry:
└── "article_recommender_v1"
    ├── Version 1 (from Run 3) -> Stage: Production
    └── Version 2 (from future run) -> Stage: Staging
```

Training script:

- Logs to experiment "article_recommendations"
- Creates many runs while tuning
- Registers best model to Model Registry

API:

- Loads from Model Registry by name
- Pulls "Production" stage version
- Doesn't care which experiment it came from

## Model Training vs Inference

Two distinct phases in the ML lifecycle with different purposes and constraints.

### Training Phase

Goal: Learn patterns from historical data

Process:

1. Load large dataset (thousands/millions of samples)
2. Apply feature transformations and fit encoders/scalers
3. Feed batches through model repeatedly (epochs)
4. Calculate loss, backpropagate, update weights
5. Validate performance on held-out data
6. Save trained model + all preprocessing artifacts

Characteristics:

- Computationally expensive (minutes to hours)
- Uses GPU acceleration when available
- Requires labeled data (inputs + correct outputs)
- Iterative - run many experiments to tune hyperparameters
- Happens offline (not real-time)

### Inference Phase (Production)

Goal: Make predictions on new, unseen data

Process:

1. Receive single request (one user, one data point)
2. Apply same feature transformations (using saved encoders/scalers)
3. Single forward pass through model (no training)
4. Post-process output to human-readable format
5. Return prediction immediately

Characteristics:

- Computationally cheap (<5-50ms per request)
- Often runs on CPU
- No labels needed (just inputs)
- Single execution per request
- Happens online (real-time)

Typically served via a `predict()` method.

### Critical Rule: Identical Transformations

The exact same feature engineering must be applied in both phases:

- Use the same encoders fit during training
- Use the same scaler fit during training
- Apply transformations in the same order

Why: If training saw normalized data [0-1] but inference gets raw data [0-1000], predictions will be garbage.

Example - Article Recommendation:

- Training: Fit `MultiLabelBinarizer` on all 50 articles, fit `StandardScaler` on time values
- Inference: Use those same fitted objects to transform new data
- Both must produce 61-dimensional vectors

## Model Artifacts & Serialization

What gets saved when you "save a model" and why each piece matters.

### What Is a Model Artifact?

A model artifact is the complete package needed to make predictions, not just the trained neural network weights.

Components:

1. Trained model - Neural network with learned weights
2. Preprocessors - Encoders, scalers, tokenizers (already fitted)
3. Metadata - Input/output schema, feature names, model version
4. Code/dependencies - Sometimes the model class definition itself

### Why Preprocessors Must Be Saved

The model doesn't know what "article_5" means - it only knows position 5 in a 50-dimensional vector.

Without saved preprocessors:

```python
# Training: articles were encoded as [article_1, article_2, ..., article_50]
# Inference: new data might encode as [article_3, article_1, ..., article_49]
# Result: Model receives completely wrong features -> bad predictions
```

With saved preprocessors:

```python
# Training: mlb_articles.fit(["article_1", "article_2", ...])
# Inference: mlb_articles.transform(["article_5"]) -> always position 5
# Result: Consistent feature representation
```

### Serialization Methods

Pickle (.pkl)

```python
# Save
model_data = {
    'model': self.model,
    'mlb_articles': self.mlb_articles,  # Fitted encoder
    'scaler': self.scaler,              # Fitted scaler
    'metadata': {...}
}
pickle.dump(model_data, file)

# Load
model_data = pickle.load(file)
model = model_data['model']
encoder = model_data['mlb_articles']  # Still fitted!
```

Pros: Simple, everything in one file
Cons: Python-specific, version-sensitive, security risks

MLflow (Recommended)

```python
# Save
mlflow.pytorch.log_model(model, "model")
# MLflow automatically packages model + dependencies

# Load
model = mlflow.pyfunc.load_model("models:/article_recommender/Production")
```

Pros: Version tracking, language-agnostic, deployment-ready
Cons: Requires MLflow server

### What Happens If You Forget Preprocessors?

```python
# Training
scaler.fit([100, 200, 300])  # Learns mean=200, std=82
X_train = scaler.transform([150])  # Returns [-0.61]

# Inference (without saved scaler)
X_new = [150]  # Raw value, not scaled
model.predict(X_new)  # Model expects scaled value -> wrong prediction!
```

Key Point: Saving just the model is like saving a calculator without the instruction manual. You need the preprocessing "instructions" to feed data in the right format.

Example - Article Recommendation:
Saved artifacts include:

- `model`: PyTorch neural network (weights + architecture)
- `mlb_articles`: Knows mapping of 50 articles to positions
- `mlb_topics`: Knows mapping of 10 topics to positions
- `mlb_recommended`: Knows how to decode predictions back to article IDs
- `scaler`: Knows how to normalize time_on_site
- `article_topic_map`: Internal data for topic lookups
- `user_favorite_topics`: Internal data for user preferences

## Data Preparation & Splits

How to divide your dataset for training and evaluation.

### Why Split Data?

Problem: If you train and test on the same data, the model just memorizes answers. You need to test on data it's never seen to measure real performance.

Analogy: Teaching to the test - if students practice with the exact questions from the exam, high scores don't mean they understand the material.

### Common Split Ratios

Train/Validation/Test: 70/15/15 or 80/10/10

- Training set (70-80%): Model learns from this data
- Validation set (10-15%): Tune hyperparameters, check progress during training
- Test set (10-15%): Final evaluation, never touch during training

Train/Validation: 80/20 (simpler, used when data is limited)

- Training set (80%): Model learns from this data
- Validation set (20%): Evaluate performance during and after training

### The Process

```python
# Example with 2000 samples
from sklearn.model_selection import train_test_split

# First split: 80% train, 20% validation
X_train, X_val, y_train, y_val = train_test_split(
    X, y,
    test_size=0.2,      # 20% for validation
    random_state=42     # Reproducible split
)

# Result:
# X_train: 1600 samples (80%)
# X_val: 400 samples (20%)
```

### What Each Set Does

Training Set:

- Model sees this data during backpropagation
- Weights are updated based on training errors
- Model will perform best on this data (by design)

Validation Set:

- Model never trains on this
- Used to evaluate after each epoch
- Helps detect overfitting (train good, validation bad)
- Used to decide when to stop training
- Metrics reported here (precision, recall, F1)

Test Set (when used):

- Completely held out until final evaluation
- Single evaluation after all training is done
- Reports the "true" performance on unseen data

### Random State / Seed

```python
random_state=42  # Magic number
```

Why: Ensures the same split every time you run the code

- Reproducible experiments
- Fair comparison between model versions
- Debugging (same data each run)

Without it: Every run creates different splits -> different results -> can't compare experiments

### Stratification (Advanced)

For imbalanced datasets, ensure each split has similar class distributions:

```python
train_test_split(X, y, test_size=0.2, stratify=y)
```

Example: If 90% of data is class A and 10% is class B, stratification ensures:

- Training set: 90% A, 10% B
- Validation set: 90% A, 10% B

### Common Mistakes

- Training on validation data: Leaks information, inflates performance metrics
- Not splitting: Can't tell if model generalizes or just memorizes
- Too small validation set: Unreliable metrics (high variance)
- Data leakage: Using information from validation set during preprocessing

Example - Article Recommendation:

- 2000 total samples
- 1600 training samples (80%)
- 400 validation samples (20%)
- Validation metrics reported: val_loss, precision, recall, F1

## Overfitting vs Underfitting

The fundamental trade-off in machine learning: model complexity vs generalization.

### Underfitting (Too Simple)

Problem: Model is too simple to capture patterns in the data

Symptoms:

- High training loss
- High validation loss
- Training and validation losses are similar
- Poor performance everywhere

Example: Using a straight line to fit data that curves

```
Data: Curved relationship
Model: Straight line
Result: Can't capture the curve, always wrong
```

Causes:

- Model too small (not enough layers/neurons)
- Not enough training (too few epochs)
- Features don't contain useful information
- Learning rate too high (can't converge)

Solutions:

- Increase model capacity (more layers, more neurons)
- Train longer (more epochs)
- Add better features
- Decrease learning rate

### Overfitting (Too Complex)

Problem: Model memorizes training data instead of learning general patterns

Symptoms:

- Low training loss (model does great on training data)
- High validation loss (model does poorly on new data)
- Large gap between training and validation performance
- Model performs worse on real data than in training

Example: Drawing a line through every single data point

```
Data: 100 points with some noise
Model: Curve that hits every point exactly
Result: Perfect on training data, terrible on new data
```

Causes:

- Model too large (too many layers/neurons)
- Training too long (too many epochs)
- Not enough training data
- No regularization

Solutions:

- Dropout: Randomly disable neurons during training
- Early stopping: Stop training when validation loss stops improving
- Regularization: Penalize large weights (L1, L2)
- More training data: Harder to memorize with more examples
- Data augmentation: Create variations of existing data
- Reduce model size: Fewer parameters to overfit with

### The Sweet Spot

Goal: Model complex enough to learn patterns but simple enough to generalize

```
Underfitting ←──────── Sweet Spot ──────────-> Overfitting
Too simple              Just right              Too complex
High train error        Low train error         Very low train error
High val error          Low val error           High val error
```

### Dropout Explained

What it does: Randomly "turns off" a percentage of neurons during each training batch

```python
nn.Dropout(0.3)  # 30% of neurons randomly disabled
```

Why it works:

- Prevents neurons from co-adapting (relying on specific other neurons)
- Forces network to learn redundant representations
- Acts like training an ensemble of smaller networks
- Only active during training (disabled during inference)

Example - Article Recommendation:

```python
nn.Dropout(0.3)  # First layer: 30% dropout
nn.Dropout(0.2)  # Second layer: 20% dropout
```

Higher dropout in early layers, lower in later layers is common practice.

### Monitoring During Training

Signs of overfitting:

```
Epoch 10: train_loss=0.25, val_loss=0.28  ✓ Good
Epoch 20: train_loss=0.15, val_loss=0.22  ✓ Good
Epoch 30: train_loss=0.08, val_loss=0.19  ✓ Good
Epoch 40: train_loss=0.03, val_loss=0.25  ⚠️ Warning
Epoch 50: train_loss=0.01, val_loss=0.35  - Overfitting
```

Training loss keeps decreasing, but validation loss increases -> Stop training!

Signs of underfitting:

```
Epoch 10: train_loss=0.45, val_loss=0.48  ⚠️ Both high
Epoch 20: train_loss=0.43, val_loss=0.46  ⚠️ Not improving much
Epoch 30: train_loss=0.42, val_loss=0.45  ⚠️ Plateau
```

Both losses are high and not improving -> Model too simple!

### Practical Tips

1. Start simple: Small model, few epochs
2. Monitor validation loss: Your early warning system
3. Use dropout: Default 0.2-0.5 between layers
4. Early stopping: Stop when val_loss stops improving for N epochs
5. More data > bigger model: Always collect more data if possible

Key Point: The goal isn't perfect training accuracy - it's good performance on data the model has never seen. A model with 95% training accuracy and 60% validation accuracy is worse than one with 85% on both.

Example - Article Recommendation:

- Uses Dropout(0.3) and Dropout(0.2) to prevent overfitting
- Validation metrics tracked every 10 epochs to monitor overfitting
- 50 epochs chosen as reasonable balance (could stop earlier if val_loss increases)

## ML Models vs LLM Classification

### Traditional ML Models (what we built)

Pros:

- Fast: <5ms inference, can handle thousands of requests/second
- Cheap: Pennies per million predictions once trained
- Consistent: Same input = same output, deterministic
- Controllable: You define features, tune exactly how it behaves
- Lightweight: Runs on CPU, small model size (~500KB)
- Privacy: Runs locally, no data leaves your infrastructure
- Explainable: Can see feature importance, understand why it predicted X

Cons:

- Requires training data: Need thousands of labeled examples
- Domain-specific: Trained for ONE task, can't generalize
- Manual feature engineering: You decide what features matter
- Retraining needed: Must retrain when patterns change
- Can't handle novel inputs: Trained on 50 articles, can't recommend article 51

---

### LLM Classification (GPT-4, Claude, etc.)

Pros:

- Zero-shot capable: Can classify without training examples
- Flexible: Same model handles spam, sentiment, categorization, etc.
- Understands context: Can read full text, nuance, sarcasm
- Rapid prototyping: Get started in minutes with a prompt
- Handles novelty: Can classify things it's never seen before
- Natural language reasoning: Can explain its decisions

Cons:

- Slow: 500-2000ms per request (100-400x slower than ML)
- Expensive: $0.01-$1.00 per 1000 predictions (vs $0.0001 for ML)
- Non-deterministic: Same input might give different outputs
- Rate limits: APIs throttle requests (1000/min vs unlimited local)
- Privacy concerns: Sending data to external API
- Black box: Harder to debug why it made a decision
- Overkill: Using a sledgehammer to crack a nut

---

## When to Use Each

Use Traditional ML when:

- High volume (>1000 requests/sec)
- Low latency required (<50ms)
- Clear, structured input (IDs, numbers, categories)
- Task is well-defined and stable
- Budget-constrained
- Privacy-sensitive data
- Example: Fraud detection on every transaction

Use LLM when:

- Low volume (<100 requests/min)
- Complex reasoning needed
- Unstructured text input
- Task changes frequently
- Don't have training data
- Need explanations
- Example: Content moderation with nuanced context

Hybrid Approach:

- ML model for initial filtering (fast, cheap)
- LLM for edge cases (complex, needs reasoning)
- Example: Spam filter (ML blocks 95%, LLM reviews borderline cases)

---

## Cost Comparison Example

1 million predictions:

- Traditional ML: $0.10 (inference cost)
- GPT-4 API: $10,000-$30,000
- Claude API: $3,000-$15,000

For your article recommender:
If serving 10,000 users/day with 5 recommendations each:

- ML model: ~$0.05/month
- LLM API: ~$1,500/month

Bottom line: ML models are production workhorses. LLMs are powerful prototyping/special case tools.
