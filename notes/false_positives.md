# False Positives

The basis of all classification problems is are you trying to minimize false negatives or false positives. This depends on use case, context, and what you're trying to classify

### Definitions

Suppose you're building a model to detect if someone has a disease. The possible actual conditions are:

* The person has the disease (Positive)
* The person does not have the disease (Negative)

And your model's predictions are:

* The model predicts they have the disease (Positive)
* The model predicts they don't (Negative)

|                        | Actual Positive (Has disease) | Actual Negative (No disease) |
| ---------------------- | --------------------------------- | -------------------------------- |
| Predicted Positive | ✅ True Positive (TP)              | ❌ False Positive (FP)            |
| Predicted Negative | ❌ False Negative (FN)             | ✅ True Negative (TN)             |

---

### Easy Examples

#### 1. Medical Test for Cancer

* True Positive (TP): Test says person has cancer, and they actually have it.
* False Positive (FP): Test says person has cancer, but they don’t   (Unnecessary anxiety, maybe more tests.)
* True Negative (TN): Test says person doesn’t have cancer, and th  y don’t.
* False Negative (FN): Test says person doesn’t have cancer, but t  ey do. (Very dangerous.)

#### 2. Spam Filter

* True Positive: Model flags a spam email, and it’s actually spam.  
* False Positive: Model flags a real email as spam. (You might mis   important info.)
* True Negative: Real email is correctly not flagged.
* False Negative: Spam email sneaks into your inbox.

### Mental Trick

Think of "positive" and "negative" as the model claiming something is true or not, and "true" and "false" as whether that claim is correct.

> * False Positive: Model cries wolf, but there’s no wolf.
> * False Negative: Model misses the wolf when it’s there.

---

### Numerical Example

Suppose you're testing 100 people:

* 20 people actually have the disease.
* Your model predicts 25 people have it.

Now break it down:

* 18 of the 20 sick people are predicted positive → True Positives = 18
* 2 of the sick people are predicted negative → False Negatives = 2
* Of the 80 healthy people, 5 are incorrectly predicted to have the disease → False Positives = 5
* The other 75 are correctly predicted as healthy → True Negatives = 75

|                    | Actual Positive | Actual Negative |
| ------------------ | --------------- | --------------- |
| Predicted Positive | 18 (TP)         | 5 (FP)          |
| Predicted Negative | 2 (FN)          | 75 (TN)         |


### Summary Table

| Term                    | What it means                                                     |
| ----------------------- | ----------------------------------------------------------------- |
| True Positive (TP)  | Correctly predicted positive (model says “yes,” and it’s true)    |
| False Positive (FP) | Incorrectly predicted positive (model says “yes,” but it’s false) |
| True Negative (TN)  | Correctly predicted negative (model says “no,” and it’s true)     |
| False Negative (FN) | Incorrectly predicted negative (model says “no,” but it’s false)  |

## How Businesses Think About It

They weigh:

* Cost of a False Positive (FP): Taking unnecessary action.
* Cost of a False Negative (FN): Failing to act when you should have.

The key is context and consequence.

## Critical Examples (Where Getting It Wrong Has Serious Impact)

### 1. Medical Diagnosis

* Goal: Detect serious diseases (e.g., cancer, sepsis, HIV).
* False Negative (FN) is worse: Missed diagnosis could mean no treatment, and the patient may die.
* Tolerate some False Positives: More tests can rule them out.

> Businesses (hospitals, diagnostic labs) prefer high recall (catch all positives).

### 2. Credit Card Fraud Detection

* False Negative (FN): Fraud not caught → huge losses, chargebacks, eroded customer trust.
* False Positive (FP): Legitimate transaction flagged → user frustrated, possible churn.

> Must balance both carefully. Banks often lean slightly toward false positives and then ask for confirmation (e.g., text alerts).

### 3. Spam Filtering (Email Providers)

* False Positive (FP): A real email goes to spam — could mean lost job offers, clients, etc.
* False Negative (FN): Spam hits your inbox — annoying, but less critical.

> Email providers try to minimize false positives even if some spam gets through.

### 4. Criminal Justice (Facial Recognition, Predictive Policing)

* False Positive: Innocent person flagged or arrested — huge ethical/legal issues.
* False Negative: Criminal not flagged — public safety risk.

> In practice, false positives are seen as more dangerous due to civil rights concerns.

### 5. Autonomous Vehicles

* False Negative (FN): Fails to detect a pedestrian or stop sign → deadly.
* False Positive (FP): Stops for a shadow → annoying but safe.

> Must minimize false negatives, even if it results in more false positives and conservative driving.

### 6. Cybersecurity (Intrusion Detection)

* False Negative: Misses a real threat → data breach, loss of IP, legal damage.
* False Positive: Flags benign activity → noise, wasted IT time.

> Enterprises often favor catching all threats, even if noisy (more FPs), then tune later.


### 7. Hiring & Resume Screening (Automated Systems)

* False Positive: Unqualified person gets through.
* False Negative: Qualified person gets rejected.

> Many companies risk false negatives without realizing it, leading to missed top talent — a growing concern in DEI (diversity, equity, inclusion) efforts.


## Summary Table

| Domain            | Prefer to Minimize | Why                                             |
| ----------------- | --------------- | ----------------------------------------------- |
| Healthcare        | False Negatives | Missing a diagnosis could kill someone          |
| Finance           | False Negatives | Missed fraud = real money loss                  |
| Email Spam        | False Positives | Don’t want to miss real messages                |
| Criminal Justice  | False Positives | Wrongful accusation is very costly              |
| Self-driving Cars | False Negatives | Safety-critical (e.g., not detecting obstacles) |
| Cybersecurity     | False Negatives | Breaches are worse than alert fatigue           |
| Hiring Systems    | False Negatives | Losing great candidates is bad for business     |
