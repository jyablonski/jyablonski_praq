# Comprehensive Time Series Forecasting Guide

## Part 1: Core Concepts

### Stationarity

What it means: A time series is stationary when its statistical properties—mean, variance, and autocovariance—don't change over time. Intuitively, a stationary series "looks the same" regardless of when you observe it. There's no trend pushing values up or down, no expanding or contracting variance, and the relationship between observations at fixed intervals stays consistent.

Why it matters: Classical forecasting methods like ARIMA assume stationarity because they model the series as fluctuations around a stable mean with consistent dynamics. When you violate this assumption, your model is essentially trying to learn a moving target—the relationships it captures from history won't apply to future data.

Testing for stationarity:

The Augmented Dickey-Fuller (ADF) test checks whether the series has a unit root (non-stationarity). The null hypothesis is that the series is non-stationary; a p-value below your threshold (typically 0.05) lets you reject this and conclude stationarity. The test fits an autoregressive model and examines whether the coefficient on the lagged level is significantly different from zero in a way that implies mean-reversion.

```python
from statsmodels.tsa.stattools import adfuller

result = adfuller(series, autolag='AIC')
print(f'ADF Statistic: {result[0]:.4f}')
print(f'p-value: {result[1]:.4f}')
# p < 0.05 suggests stationarity
```

The KPSS test flips the hypothesis—it tests whether the series is stationary around a deterministic trend. The null hypothesis is stationarity, so a low p-value suggests non-stationarity. Using both tests together provides more confidence:

| ADF Result | KPSS Result | Interpretation |
| ------------------------------- | ---------------------------- | ------------------------------------------------------------------ |
| Reject null (stationary) | Fail to reject (stationary) | Series is stationary |
| Fail to reject (non-stationary) | Reject null (non-stationary) | Series is non-stationary |
| Reject null | Reject null | Series is difference-stationary (has unit root but no trend) |
| Fail to reject | Fail to reject | Series is trend-stationary (stationary around deterministic trend) |

Addressing non-stationarity:

Differencing removes stochastic trends by computing the change between consecutive observations: y'_t = y_t - y_{t-1}. If the first difference isn't stationary, you can difference again (second-order differencing), though needing more than two differences is rare and often signals a different problem.

Detrending works when there's a deterministic trend—fit a regression against time and work with residuals. This is appropriate when you believe the trend is a fixed function (like steady 3% annual growth) rather than a random walk.

The choice between differencing and detrending depends on whether the trend is stochastic or deterministic. In practice, differencing is more robust because it handles both cases reasonably well.

______________________________________________________________________

### Decomposition

Time series decomposition separates a series into interpretable components:

- Trend (T): Long-term direction and level changes
- Seasonal (S): Regular, repeating patterns at fixed intervals
- Residual (R): Everything else—noise, irregular fluctuations, unexplained variation

Additive decomposition assumes components sum together: Y_t = T_t + S_t + R_t. This works when seasonal fluctuations have roughly constant magnitude regardless of the level—e.g., always ±100 units.

Multiplicative decomposition assumes components multiply: Y_t = T_t × S_t × R_t. This is appropriate when seasonal variation scales with the level—e.g., December sales are always 20% higher, whether your baseline is 1,000 or 10,000 units.

A useful heuristic: plot the series. If the seasonal swings grow as the level grows, use multiplicative. You can also take logs to convert multiplicative structure to additive (log(T×S×R) = log(T) + log(S) + log(R)), which sometimes simplifies modeling.

Classical decomposition uses moving averages to estimate trend and derives seasonal indices from detrended data. It's intuitive but has drawbacks: estimates aren't available for the first and last few observations, and it assumes seasonal patterns are constant.

STL (Seasonal and Trend decomposition using Loess) is more flexible—it handles changing seasonality, is robust to outliers, and works with any seasonal period. It's generally the better choice for exploratory analysis.

```python
from statsmodels.tsa.seasonal import STL

stl = STL(series, period=12, robust=True)
result = stl.fit()
result.plot()
```

Decomposition serves multiple purposes: understanding your data (is growth coming from trend or improving seasonality?), identifying anomalies (large residuals warrant investigation), and informing model choice (strong seasonality suggests Holt-Winters or SARIMA).

______________________________________________________________________

### Autocorrelation

Autocorrelation measures how a series relates to lagged versions of itself. This relationship is central to time series modeling because it captures the "memory" in the data.

The Autocorrelation Function (ACF) measures correlation between y_t and y\_{t-k} for various lags k. It includes both direct effects and indirect effects through intermediate lags.

The Partial Autocorrelation Function (PACF) isolates the direct relationship between y_t and y\_{t-k} after removing the effects of intermediate lags. It answers: "What's the unique predictive value of the observation k periods ago, beyond what's already captured by closer observations?"

Interpreting ACF and PACF plots:

The blue shaded region represents the 95% confidence interval under the null hypothesis of no correlation. Spikes outside this region are statistically significant.

For AR processes (current value depends on past values):

- ACF decays gradually (exponentially or in damped sinusoids)
- PACF cuts off sharply after lag p

For MA processes (current value depends on past errors):

- ACF cuts off sharply after lag q
- PACF decays gradually

For seasonal patterns:

- Spikes at seasonal lags (12, 24, 36 for monthly data with annual seasonality)
- Pattern repeats at multiples of the seasonal period

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
plot_acf(series, lags=40, ax=axes[0])
plot_pacf(series, lags=40, ax=axes[1])
```

These plots directly inform ARIMA parameter selection:

- Significant PACF spikes suggest AR terms (the lag at which PACF cuts off suggests p)
- Significant ACF spikes suggest MA terms (the lag at which ACF cuts off suggests q)
- Seasonal spikes suggest seasonal components

______________________________________________________________________

### Seasonality Types

Daily seasonality: Patterns within a single day—call center volumes peaking mid-morning, restaurant traffic at mealtimes. Period = 24 if hourly data.

Weekly seasonality: Day-of-week effects—retail peaks on weekends, B2B activity drops on Fridays. Period = 7.

Monthly seasonality: Day-of-month effects—paychecks driving spending around the 1st and 15th. Period = approximately 30.

Annual seasonality: Month-of-year effects—holiday retail spikes, summer travel patterns. Period = 12 for monthly data, 52 for weekly, 365 for daily.

Handling multiple overlapping seasonalities:

This is where things get tricky. A retail time series might have daily patterns (busy lunch hour), weekly patterns (weekend peaks), and annual patterns (holiday surge) simultaneously.

Classical methods struggle here—SARIMA handles one seasonal period well but becomes unwieldy with multiple. Options include:

1. Fourier terms: Represent seasonality as sine/cosine pairs. You can include multiple seasonal periods by adding Fourier terms for each. The number of terms controls flexibility—more terms capture complex patterns but risk overfitting.

```python
import numpy as np

def fourier_features(t, period, n_terms):
    features = {}
    for k in range(1, n_terms + 1):
        features[f'sin_{period}_{k}'] = np.sin(2 * np.pi * k * t / period)
        features[f'cos_{period}_{k}'] = np.cos(2 * np.pi * k * t / period)
    return pd.DataFrame(features)

# For daily data with weekly and annual seasonality
weekly = fourier_features(np.arange(len(series)), period=7, n_terms=3)
annual = fourier_features(np.arange(len(series)), period=365.25, n_terms=10)
```

2. Prophet-style decomposition: Facebook Prophet was designed for this exact problem—it models trend with changepoints and seasonality with Fourier series, handling daily, weekly, and annual patterns simultaneously.

1. ML approaches: Tree-based models don't care about multiple seasonalities—they're just features. Include day-of-week, month, hour, and let the model figure out interactions.

______________________________________________________________________

## Part 2: Classical Methods Deep Dive

### Exponential Smoothing Family

Exponential smoothing methods forecast by computing weighted averages of past observations, with weights decaying exponentially as observations get older. The beauty is that recent data matters most, but older data still contributes.

Simple Exponential Smoothing (SES):

Used for data with no trend or seasonality—just level fluctuations. The forecast is a weighted average where the smoothing parameter α controls how fast weights decay.

Forecast equation: ŷ\_{t+1} = αy_t + α(1-α)y\_{t-1} + α(1-α)²y\_{t-2} + ...

Higher α means more weight on recent observations (more responsive to changes, but also more reactive to noise). Lower α means more stable forecasts that adapt slowly.

```python
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

model = SimpleExpSmoothing(series).fit(smoothing_level=0.3, optimized=False)
# or let it optimize: model = SimpleExpSmoothing(series).fit()
```

Holt's Linear Method (Double Exponential Smoothing):

Extends SES to handle trend. It maintains two components: level (ℓ) and trend (b), each with its own smoothing parameter.

Level: ℓ_t = αy_t + (1-α)(ℓ\_{t-1} + b\_{t-1})
Trend: b_t = β(ℓ_t - ℓ\_{t-1}) + (1-β)b\_{t-1}
Forecast: ŷ\_{t+h} = ℓ_t + hb_t

The damped trend variant multiplies the trend by a damping parameter φ < 1 for each step ahead, preventing forecasts from shooting off to infinity. In practice, damped trends almost always perform better—pure linear extrapolation is rarely realistic.

```python
from statsmodels.tsa.holtwinters import Holt

model = Holt(series, damped_trend=True).fit()
```

Holt-Winters (Triple Exponential Smoothing):

Adds seasonality to Holt's method. Maintains level, trend, and seasonal components.

Additive version (for constant seasonal amplitude):

- Level: ℓ_t = α(y_t - s\_{t-m}) + (1-α)(ℓ\_{t-1} + b\_{t-1})
- Trend: b_t = β(ℓ_t - ℓ\_{t-1}) + (1-β)b\_{t-1}
- Seasonal: s_t = γ(y_t - ℓ_t) + (1-γ)s\_{t-m}
- Forecast: ŷ\_{t+h} = ℓ_t + hb_t + s\_{t+h-m}

Multiplicative version (for proportional seasonal amplitude):

- Seasonal component multiplies rather than adds

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

model = ExponentialSmoothing(
    series,
    trend='add',
    seasonal='mul',  # or 'add'
    seasonal_periods=12,
    damped_trend=True
).fit()
```

When to use each:

- SES: No trend, no seasonality, just noisy level (rare in practice)
- Holt: Clear trend but no seasonality
- Holt-Winters: Both trend and seasonality (very common)

______________________________________________________________________

### ARIMA

ARIMA stands for AutoRegressive Integrated Moving Average. It's the workhorse of classical forecasting, flexible enough to model many patterns while maintaining interpretability.

The parameters p, d, q:

d (Integration order): How many times you difference the series to achieve stationarity. d=1 means working with first differences (changes), d=2 means differencing twice. This is the "I" in ARIMA—the original series is "integrated" (cumulative sum) of the differenced series.

p (AR order): Number of autoregressive terms—how many lagged values of y directly enter the model. AR(p) models the current value as a linear combination of the past p values plus noise.

y_t = c + φ₁y\_{t-1} + φ₂y\_{t-2} + ... + φ_py\_{t-p} + ε_t

q (MA order): Number of moving average terms—how many lagged forecast errors enter the model. MA(q) models the current value as a function of past forecast errors.

y_t = c + ε_t + θ₁ε\_{t-1} + θ₂ε\_{t-2} + ... + θ_qε\_{t-q}

ARIMA combines these: the AR component captures momentum and mean-reversion, the MA component captures shocks that persist briefly, and differencing handles non-stationarity.

Manual selection using ACF/PACF:

1. Difference until stationary (check with ADF/KPSS), counting differences for d
1. Look at PACF of stationary series—significant spikes suggest AR order p
1. Look at ACF—significant spikes suggest MA order q
1. Fit candidate models, compare using AIC/BIC
1. Check residuals—they should look like white noise (no significant autocorrelation)

Auto-selection tradeoffs:

`auto_arima` from pmdarima searches over parameter combinations using information criteria. It's convenient but has pitfalls:

- Can miss the best model if search bounds are too narrow
- Slower than fitting a known good specification
- Sometimes selects unnecessarily complex models
- Doesn't capture domain knowledge (you might know d should be 1)

In practice, I use auto_arima for initial exploration, then verify the selection makes sense and often fit a few nearby specifications to check stability.

```python
from pmdarima import auto_arima

model = auto_arima(
    series,
    start_p=0, max_p=3,
    start_q=0, max_q=3,
    d=None,  # let it determine
    seasonal=False,
    stepwise=True,
    trace=True  # see the search progress
)
```

______________________________________________________________________

### SARIMA

SARIMA extends ARIMA with seasonal components. The notation is ARIMA(p,d,q)(P,D,Q)[m] where:

- (p,d,q): non-seasonal orders
- (P,D,Q): seasonal orders
- m: seasonal period

The seasonal components work similarly to non-seasonal:

- P: seasonal AR terms (lags at multiples of m)
- D: seasonal differencing (y_t - y\_{t-m})
- Q: seasonal MA terms

For monthly data with annual seasonality (m=12), SARIMA(1,1,1)(1,1,1)[12] includes:

- AR(1): dependence on last month
- First differencing: model changes month-to-month
- MA(1): shock persistence for one month
- Seasonal AR(1): dependence on same month last year
- Seasonal differencing: model year-over-year changes
- Seasonal MA(1): annual shocks persist one season

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

model = SARIMAX(
    series,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12)
).fit()
```

Practical tips:

- Seasonal differencing (D=1) is often enough to handle annual patterns
- Keep seasonal orders low (P, Q ≤ 2)—higher orders rarely help and increase estimation difficulty
- If the seasonal period is long (like 365 for daily data), SARIMA becomes computationally painful—consider alternatives like Prophet or Fourier features

______________________________________________________________________

### When Classical Methods Outperform ML

Classical methods aren't outdated—they win in specific situations:

Short history: Tree-based models need lots of data to learn complex relationships. With only 2-3 years of monthly data (24-36 observations), exponential smoothing or ARIMA will likely outperform because they have fewer parameters to estimate.

Clean, regular patterns: If your series has textbook trend and seasonality without structural breaks or complex interactions with external factors, Holt-Winters elegantly captures exactly what's there without overfitting.

Interpretability requirements: When stakeholders need to understand *why* the forecast is what it is, exponential smoothing parameters have clear meanings. "We're smoothing with α=0.3 and the seasonal index for December is 1.4" is easier to explain than "the gradient boosted trees learned that lag 7 interacts with holiday proximity."

Forecasting many series with varied characteristics: If you're forecasting thousands of SKUs with varying data quality and lengths, a robust method like ETS (exponential smoothing state space model) with automatic model selection is reliable. ML models need more careful tuning per series.

Computational constraints: Classical methods fit in milliseconds. This matters when you're forecasting at scale or need real-time updates.

______________________________________________________________________

## Part 3: Machine Learning for Forecasting

### Why Tree-Based Methods Work

Random forests and gradient boosting aren't designed for sequential data, but they work well for forecasting when you reframe the problem as supervised learning.

Instead of modeling temporal dynamics directly, you create a tabular dataset where each row is a prediction target with engineered features describing the past. The model learns: "Given these characteristics of the past and current context, what's the likely value?"

This works because:

1. Trees naturally handle nonlinear relationships and interactions—they don't care if the relationship between lag_7 and the target is linear or not
1. Feature engineering lets you encode temporal structure explicitly—the model doesn't need to discover that weekly patterns exist; you tell it by including day-of-week features
1. Regularization through bagging (random forest) or boosting with early stopping prevents overfitting
1. They handle mixed feature types gracefully—combining lagged values, categorical calendar features, and external regressors without scaling concerns

```python
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit

# Assuming df has features and 'target' column
X = df.drop('target', axis=1)
y = df['target']

model = lgb.LGBMRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=20,
    random_state=42
)

# Use time-aware CV (discussed later)
tscv = TimeSeriesSplit(n_splits=5)
# ... fit and validate
```

______________________________________________________________________

### Feature Engineering: The Core Skill

Feature engineering is where you win or lose with ML forecasting. The model only knows what you tell it through features.

Lag features:

Include past values of the target. Which lags depend on your data:

- For daily data with weekly seasonality: lags 1, 7, 14, 21, 28
- For monthly data with annual seasonality: lags 1, 2, 3, 12, 13
- Include the minimum forecast horizon lag—if predicting 7 days ahead, lag 7 is the most recent available

```python
for lag in [1, 7, 14, 21, 28]:
    df[f'lag_{lag}'] = df['target'].shift(lag)
```

Rolling statistics:

Capture recent dynamics without including every lag:

- Rolling mean captures recent level
- Rolling std captures recent volatility
- Rolling min/max capture recent range

```python
for window in [7, 14, 28]:
    df[f'rolling_mean_{window}'] = df['target'].shift(1).rolling(window).mean()
    df[f'rolling_std_{window}'] = df['target'].shift(1).rolling(window).std()
```

The `.shift(1)` is critical—you compute the rolling stat from data available *before* the prediction point to avoid leakage.

Calendar features:

Encode time-based patterns:

- Day of week (0-6 or one-hot encoded)
- Month (1-12)
- Day of month (1-31)
- Week of year (1-52)
- Quarter
- Is weekend
- Is month start/end
- Holidays (requires a holiday calendar)

```python
df['day_of_week'] = df.index.dayofweek
df['month'] = df.index.month
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
```

Cyclical encoding can help for calendar features since day 6 and day 0 are adjacent:

```python
df['day_sin'] = np.sin(2 * np.pi * df.index.dayofweek / 7)
df['day_cos'] = np.cos(2 * np.pi * df.index.dayofweek / 7)
```

External regressors:

Incorporate other information that might drive the target:

- Marketing spend
- Price
- Weather (temperature, precipitation)
- Economic indicators
- Competitor actions
- Events and promotions

These are powerful but introduce complexity—you need forecasts of these features to use them for future prediction, or they must be known in advance (like scheduled promotions).

Feature selection:

Not all engineered features help. I typically:

1. Start with a comprehensive feature set
1. Train a model and examine feature importances
1. Remove features with near-zero importance or high correlation with more important features
1. Validate that removing features doesn't hurt performance

______________________________________________________________________

### Recursive vs Direct Forecasting

When you need to forecast multiple steps ahead, you have strategic choices.

Recursive (iterative) forecasting:

Train one model to predict one step ahead. To forecast further, use predictions as inputs for subsequent steps.

```python
# Simplified recursive forecast
preds = []
history = list(series[-max_lag:])  # need lag features

for step in range(horizon):
    features = create_features(history)
    pred = model.predict([features])[0]
    preds.append(pred)
    history.append(pred)  # use prediction for next iteration
```

Pros:

- Only need one model
- Can generate arbitrary length forecasts

Cons:

- Errors compound—early mistakes propagate and amplify
- Not well-calibrated for longer horizons since it was only trained on one-step prediction

Direct forecasting:

Train separate models for each forecast horizon—one model for 1-step ahead, another for 2-step ahead, etc.

```python
# Train separate models
models = {}
for h in range(1, horizon + 1):
    df[f'target_h{h}'] = df['target'].shift(-h)
    # Create features (all using data available at prediction time)
    X = df[feature_cols].dropna()
    y = df[f'target_h{h}'].dropna()
    models[h] = train_model(X, y)
```

Pros:

- No error propagation
- Each model optimized for its specific horizon

Cons:

- Need multiple models (computational cost, maintenance burden)
- Models don't share information about temporal structure

Hybrid approaches:

Direct-recursive: Use a mix—train models for key horizons, interpolate between them.

Multi-output models: Single model that outputs all horizons simultaneously. This shares parameters across horizons while avoiding error propagation. Some implementations support this natively; alternatively, you can frame it as multiple targets.

My recommendation: For shorter horizons (1-14 steps), direct often works well and avoids compounding errors. For longer horizons where training many models is impractical, recursive with robust models (like gradient boosting) works reasonably. Always compare both on your specific problem.

______________________________________________________________________

### Global vs Individual Models

When forecasting many related series (thousands of SKUs, multiple store locations, etc.), you choose between:

Individual models: Train a separate model for each series.

Pros:

- Captures each series' unique patterns
- No risk of one series polluting another's model

Cons:

- Requires sufficient history per series (sparse series can't learn much)
- No information sharing—can't learn that "holiday patterns look similar across products"
- More models to maintain

Global models: Train one model on all series, using series identifiers as features.

Pros:

- Pools data across series, helpful for sparse ones
- Learns shared patterns automatically
- One model to maintain

Cons:

- May smooth over important differences between series
- Dominant series can overwhelm rare ones
- Series identifier encoding matters (embedding vs one-hot)

Practical approach:

Global models have become the default recommendation, especially in modern implementations. A global model with categorical series identifiers lets the model learn what's shared and what's series-specific. Libraries like MLForecast and Nixtla's implementations are built around this.

For the best of both worlds, consider:

- Global model with per-series embeddings
- Grouped models (one model per category)
- Global model for sparse series, individual for data-rich ones

______________________________________________________________________

## Part 4: Evaluation and Validation

### Why Random Splits Are Invalid

In classification or regression, random train/test splits ensure the test set is representative and prevents leakage. For time series, this fundamentally breaks:

1. Temporal leakage: With random splits, training data might include observations *after* test data. Your model learns from the future to predict the past, giving deceptively good results.

1. Autocorrelation: Nearby observations are similar. If you randomly sample, training and test sets are highly correlated—the test set isn't meaningfully "held out."

1. Doesn't match reality: In production, you always predict the future using only past data. Evaluation should simulate this.

Always use temporal splits: Training data comes before test data with no overlap.

______________________________________________________________________

### Walk-Forward Validation

Walk-forward validation simulates production forecasting by repeatedly:

1. Train on data up to time t
1. Forecast from t to t+h
1. Move forward and repeat

Expanding window: Training set grows each iteration (1 to t, then 1 to t+1, etc.). Uses all available history.

Sliding window: Training set stays fixed size (t-w to t, then t-w+1 to t+1). Assumes recent data is most relevant.

```python
from sklearn.model_selection import TimeSeriesSplit

# Expanding window
tscv = TimeSeriesSplit(n_splits=5)

for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    # Train and evaluate
```

For sliding window, implement manually or set `max_train_size` in TimeSeriesSplit.

Key considerations:

- Gap: Leave a gap between train and test if you won't have immediately recent data in production (e.g., data arrives with a 2-day lag)
- Fold size: Test periods should match your production forecast horizon
- Number of folds: More folds give better estimates but cost computation; 3-5 is typical

______________________________________________________________________

### Forecast Horizon Selection

The horizon you validate on must match how the forecast will be used:

- If business planning happens monthly for the next quarter, evaluate 3-month ahead forecasts
- If inventory decisions happen weekly for 2 weeks out, evaluate 2-week horizons
- If real-time demand prediction updates hourly, evaluate 1-hour ahead

Mismatch is expensive: If you validate on 1-month horizons but the business uses 6-month forecasts, your evaluation doesn't reflect actual performance—the model might look great at 1 month and terrible at 6.

Also consider:

- Prediction frequency: How often you'll retrain and predict
- Data latency: How fresh your data is when predicting
- Decision timing: When decisions based on forecasts are made

______________________________________________________________________

### Metric Selection

No single metric captures everything. Each makes tradeoffs.

MAE (Mean Absolute Error): Average absolute deviation. Linear penalty—a 10-unit error is 10x as bad as a 1-unit error. Robust to outliers. Easy to interpret ("on average, we're off by X units").

MAE = (1/n) Σ|y_i - ŷ_i|

RMSE (Root Mean Squared Error): Square root of average squared deviation. Quadratic penalty—large errors hurt disproportionately. Same units as target. Sensitive to outliers.

RMSE = √[(1/n) Σ(y_i - ŷ_i)²]

MAPE (Mean Absolute Percentage Error): Average absolute percentage deviation. Scale-independent—useful when comparing across series with different magnitudes. Undefined when actuals are zero. Asymmetric—over-predictions and under-predictions of equal magnitude give different MAPE.

MAPE = (100/n) Σ|y_i - ŷ_i|/|y_i|

SMAPE (Symmetric Mean Absolute Percentage Error): Attempts to fix MAPE's asymmetry. Still has issues (different definitions exist, behavior near zero).

SMAPE = (100/n) Σ|y_i - ŷ_i|/((|y_i| + |ŷ_i|)/2)

When to use which:

| Metric | Good for | Avoid when |
| ------ | --------------------------------- | ------------------------------------------------------ |
| MAE | General purpose, interpretability | Large errors are especially costly |
| RMSE | Large errors are especially bad | Outliers are common and acceptable |
| MAPE | Comparing across different scales | Actuals near or at zero |
| SMAPE | When you want relative error | Actuals near zero; when definition consistency matters |

For business alignment, consider what matters:

- If over-predicting and under-predicting are equally bad: symmetric metrics
- If over-predicting is worse (spoiled inventory): asymmetric loss
- If large errors are catastrophic: RMSE or quantile-weighted metrics

______________________________________________________________________

### Baseline Models

Always compare against baselines. A model isn't useful if it doesn't beat simple heuristics.

Naive (last value): Forecast equals the most recent observation. ŷ\_{t+h} = y_t

Seasonal naive: Forecast equals the value from the same season last cycle. For monthly data with annual seasonality: ŷ\_{t+h} = y\_{t+h-12}

Mean: Forecast equals the historical average. Often surprisingly competitive for stationary series.

```python
# Naive
naive_forecast = series.iloc[-1]

# Seasonal naive (annual)
seasonal_naive_forecast = series.iloc[-12]

# Mean
mean_forecast = series.mean()
```

If your fancy model doesn't beat seasonal naive, something is wrong. Either the data doesn't support better forecasts (too noisy, no learnable patterns) or your model is broken.

______________________________________________________________________

## Part 5: Uncertainty and Communication

### Point Forecasts vs Prediction Intervals

A point forecast (single number) hides how confident you are. For planning, uncertainty matters enormously:

- If demand will be "around 1000 units" with tight certainty, you stock 1000
- If demand could be anywhere from 500 to 2000, your stocking decision is very different

Prediction intervals provide a range expected to contain the true value with some probability. A 95% interval should contain the actual outcome 95% of the time across many forecasts.

Classical methods generate intervals from the assumed error distribution:

```python
# ARIMA intervals
forecast = model.get_forecast(steps=12)
conf_int = forecast.conf_int(alpha=0.05)  # 95% interval
```

For ML models, options include:

- Quantile regression (directly estimate quantiles)
- Conformal prediction (distribution-free intervals with coverage guarantees)
- Bootstrapping residuals

______________________________________________________________________

### Quantile Regression and Probabilistic Forecasting

Instead of predicting the mean (E[Y|X]), quantile regression predicts specific percentiles of the conditional distribution.

For demand planning, you might want:

- 50th percentile (median forecast)
- 10th percentile (conservative low estimate)
- 90th percentile (conservative high estimate)

```python
import lightgbm as lgb

# Train models for multiple quantiles
quantiles = [0.1, 0.5, 0.9]
models = {}

for q in quantiles:
    model = lgb.LGBMRegressor(
        objective='quantile',
        alpha=q,  # the quantile to predict
        n_estimators=500
    )
    model.fit(X_train, y_train)
    models[q] = model

# Predictions form a distribution
preds_10 = models[0.1].predict(X_test)
preds_50 = models[0.5].predict(X_test)
preds_90 = models[0.9].predict(X_test)
```

Probabilistic forecasting goes further, producing full predictive distributions. This enables:

- Any quantile you need
- Expected shortfall calculations
- Simulation-based planning

______________________________________________________________________

### Communicating Uncertainty

Non-technical stakeholders often struggle with prediction intervals. Strategies that work:

Scenarios over intervals: Instead of "95% CI: [800, 1200]", say "Our best guess is 1000. In an optimistic scenario (85% chance of being below), we'd see 1150. In a pessimistic scenario (85% chance of being above), we'd see 850."

Visual emphasis: In charts, show intervals prominently (shaded regions), not just the point forecast line.

Historical performance: "Our 90% intervals have contained the actual value 88% of the time historically" builds trust and calibrates expectations.

Avoid false precision: Don't report "1,247.38" when uncertainty is ±200. Round appropriately.

Acknowledge limitations: "This forecast assumes no major market disruptions. A recession would invalidate these estimates."

______________________________________________________________________

### When to Trust vs Flag

Forecasts deserve more skepticism when:

- Recent data looks unusual (outliers, missing values, sudden changes)
- You're forecasting further ahead than you've validated
- External factors have changed (new competitor, policy change)
- The series has behaved erratically historically (high residual variance)
- Training data is sparse or old

Consider automated flags:

- Uncertainty interval wider than X% of forecast
- Residuals in recent periods larger than historical norms
- Key external features outside training range (extrapolation)
- Model performance degraded in recent validation windows

```python
# Simple flagging example
interval_width = forecast_90 - forecast_10
relative_width = interval_width / forecast_50

if relative_width > 0.5:  # interval is >50% of forecast
    flag = "HIGH_UNCERTAINTY"
```

______________________________________________________________________

## Part 6: Production Considerations

### Concept Drift

The world changes. Patterns in historical data may not hold:

- Consumer behavior shifts
- Competitors enter or exit
- Regulations change
- Economic conditions fluctuate

Detecting drift:

- Monitor forecast errors over time—increasing errors suggest drift
- Track feature distributions—significant shifts indicate regime change
- Compare recent performance to historical baseline

Retraining strategies:

- Scheduled: Retrain weekly/monthly regardless of performance
- Triggered: Retrain when error metrics exceed thresholds
- Continuous: Online learning with each new observation (more complex)

The right cadence depends on how fast your domain changes. Retail demand might need weekly updates; infrastructure capacity planning might be stable for months.

______________________________________________________________________

### Monitoring in Production

Track these continuously:

- Forecast accuracy by horizon: Is day-1 accuracy holding? Day-7?
- Error distribution: Are errors still centered around zero or is there systematic bias?
- Prediction intervals calibration: Are 90% intervals containing ~90% of actuals?
- Extreme errors: Count of forecasts off by more than X

Set alerts for:

- Accuracy worse than baseline for X consecutive periods
- Mean error significantly different from zero (indicates systematic bias)
- Interval coverage below acceptable threshold

```python
# Simple monitoring logic
def check_forecast_health(actual, predicted, threshold_mape=0.15):
    mape = np.mean(np.abs(actual - predicted) / actual)
    bias = np.mean(predicted - actual)
    
    alerts = []
    if mape > threshold_mape:
        alerts.append(f"MAPE {mape:.2%} exceeds threshold")
    if abs(bias) > np.std(actual) * 0.2:
        alerts.append(f"Systematic bias detected: {bias:.2f}")
    
    return alerts
```

______________________________________________________________________

### Backtest vs Live Performance Gap

Models almost always perform worse in production than backtests suggest. Reasons include:

Data quality: Backtests use cleaned historical data. Live data has delays, missing values, and errors you discover only after they've affected forecasts.

Feature freshness: Features might be computed slightly differently in production pipelines, or arrive later than assumed.

Regime changes: The future will differ from the past in ways not captured by historical validation.

Overfitting to validation structure: If you tuned hyperparameters extensively on walk-forward validation, you've implicitly fit to those specific splits.

Mitigation:

- Hold out a truly final test period not used for any model selection
- Be conservative with performance expectations (expect 10-20% degradation)
- Monitor aggressively after deployment
- Plan for faster intervention if live performance disappoints

______________________________________________________________________

### Handling Missing Data and Outliers

Missing data:

Detection: Look for NaNs, but also placeholder values (0, -1, 9999) that might indicate missingness.

Strategies:

- Forward-fill: Use last known value (assumes persistence)
- Interpolation: Linear or spline between known values
- Model-based: Predict missing values using other features
- Flag and exclude: Include indicator feature that value was missing

```python
# Forward fill with limit
df['target_filled'] = df['target'].fillna(method='ffill', limit=3)
df['was_missing'] = df['target'].isna().astype(int)
```

Outliers:

Detection:

- Statistical: Values beyond X standard deviations
- Domain: Values outside physically possible range
- Model-based: Large residuals from fitted model

Handling:

- Investigate first—outliers often indicate real events (promotions, outages)
- If truly erroneous: remove or impute
- If real but non-repeating: consider downweighting or using robust methods
- Add features explaining the outlier if you can identify the cause

```python
# Winsorizing extreme values
lower = series.quantile(0.01)
upper = series.quantile(0.99)
series_clipped = series.clip(lower=lower, upper=upper)
```

______________________________________________________________________

### Feature Freshness

Production prediction requires features to be available when you predict. This sounds obvious but causes many problems.

Common issues:

- You train with features computed from full history, but in production you compute them from data that arrives with delay
- Rolling statistics at training time see the full window; at prediction time you might have partial data
- External data (weather forecasts, economic indicators) might not be available at the granularity or timeliness you assumed

Audit your features:

- For each feature, document: When is it available? How is it computed? What's the data lag?
- Ensure training feature computation matches production exactly
- Test prediction pipeline with production-realistic data availability

______________________________________________________________________

### Avoiding Data Leakage

Leakage means information from the future contaminates your training, giving unrealistically good backtests.

Feature leakage:

- Using a feature that wouldn't be available at prediction time
- Including target-derived features without appropriate lag

Target leakage:

- Labels somehow contain information about the future

Rolling calculation edge cases:

- At the boundary, rolling windows might extend into the prediction period

Prevention checklist:

1. Every feature must be computable using only data strictly before the prediction point
1. Rolling calculations must use `.shift(1)` or equivalent
1. External features need their own availability timeline
1. Validation splits must respect time—no random shuffling
1. When in doubt, walk through manually: "At time T, what data do I actually have?"

```python
# WRONG: uses future data
df['rolling_mean'] = df['target'].rolling(7).mean()

# RIGHT: only uses past data
df['rolling_mean'] = df['target'].shift(1).rolling(7).mean()
```

______________________________________________________________________

## Part 7: Hierarchical and Multi-Series Patterns

### Forecasting at Multiple Granularities

Often you need coherent forecasts at different levels:

- Individual SKU and store location
- Aggregated to SKU across all stores
- Aggregated to category within a store
- Total across everything

The coherence problem: Forecasts at different levels should add up, but independently generated forecasts typically don't. You might forecast 100 units for Product A at Store 1, 100 at Store 2, but only 180 total for Product A (which should be 200).

Reconciliation approaches:

Bottom-up: Forecast at the lowest level, aggregate up. Guarantees coherence. Works well when low-level patterns are strong.

Top-down: Forecast at the top, allocate down using historical proportions. Simple but ignores low-level patterns.

Middle-out: Forecast at an intermediate level, then go both directions.

Optimal reconciliation: Generate forecasts at all levels independently, then adjust them to be coherent while minimizing the adjustment. The MinT (Minimum Trace) method is popular—it finds the coherent set of forecasts closest to the original ones, weighted by estimated forecast variances.

```python
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.methods import MinTrace

reconcilers = [MinTrace(method='ols')]
hrec = HierarchicalReconciliation(reconcilers=reconcilers)
reconciled = hrec.reconcile(base_forecasts, S, tags)
```

______________________________________________________________________

### Global vs Individual Models (Revisited)

For hierarchical structures, global models shine because they:

- Learn shared patterns across the hierarchy naturally
- Handle sparse low-level series by borrowing strength from aggregate patterns
- Produce more coherent forecasts implicitly (though explicit reconciliation still helps)

Encoding hierarchy in global models:

- Include hierarchy identifiers as features (category, subcategory, item)
- Consider embeddings for high-cardinality identifiers
- Include aggregate features (category-level statistics) as features for item-level forecasts

______________________________________________________________________

### Cold Start Strategies

New products/series have no history. Options:

Similar-item priors: Find the most similar existing series and use its model/forecasts as a starting point. Similarity might be based on product attributes (category, price point, target demographic).

Category-level forecasts: Use the aggregate forecast for the category, scaled down by expected share.

Meta-learning: Train a model to predict forecast parameters based on item attributes, then apply those parameters to new items.

Simple heuristics: For many new products, "assume average within category" or "assume 10% of category leader" is surprisingly hard to beat.

Ramp-up curves: New products often follow predictable patterns (initial spike, settling, growth or decay). Model the typical lifecycle and fit the new product onto it as data accumulates.

```python
# Simple similar-item approach
def cold_start_forecast(new_item_attributes, existing_items, existing_forecasts):
    similarities = compute_similarity(new_item_attributes, existing_items)
    top_k = similarities.nlargest(5)
    weighted_forecast = (existing_forecasts[top_k.index] * top_k).sum() / top_k.sum()
    return weighted_forecast
```

______________________________________________________________________

## Part 8: Common Pitfalls

### Overfitting to Historical Patterns

The trap: Historical data shows a pattern → model learns it → pattern doesn't repeat → bad forecasts.

Examples:

- A one-time event (pandemic, viral moment) creates a spike you overweight
- Seasonal patterns are learned too precisely when they actually vary year to year
- Trend is extrapolated beyond where it makes sense

Mitigation:

- Regularization (penalize model complexity)
- Validation on multiple holdout periods, not just the most recent
- Sanity check: "Would I believe this forecast if I saw it?"
- Damped trends, not linear extrapolation

______________________________________________________________________

### Ignoring External Factors

The trap: Past performance was driven by factors that won't repeat, but the model doesn't know this.

Examples:

- Sales spiked because of a promotion → model expects similar future spikes without promotions
- Growth was driven by expansion into new markets → model expects growth to continue after expansion ends
- Performance depended on favorable economic conditions → model doesn't account for recession

Mitigation:

- Include external factors as features when possible
- Document known drivers of historical anomalies
- Adjust forecasts manually for known upcoming differences
- Build separate models for "normal" periods vs promotional/event periods

______________________________________________________________________

### Over-Engineering

The trap: Complex ensemble of deep learning models when a simple model would work as well or better.

Signs you're over-engineering:

- Model improvement is marginal over baselines
- Training time is excessive relative to business value
- Model is fragile—small changes cause large performance swings
- Nobody can explain how it works

Right-sizing:

- Start simple (exponential smoothing, linear models)
- Add complexity only when it demonstrably improves validated performance
- Consider maintenance burden—will this model still work when you're not around?

______________________________________________________________________

### Validation Period Mismatch

The trap: Testing on 1 month when forecasts are used for 6 months.

Why this matters: Performance often degrades with horizon. A model that's great at 1 month might be terrible at 6 months, but you'd never know if you only tested 1 month.

Fix: Validation horizons must match production horizons. If you make 6-month forecasts, validate on 6-month horizons.

______________________________________________________________________

### Confusing Precision with Accuracy

The trap: Tight prediction intervals that miss actuals are worse than wide honest ones.

A model that reports 95% confidence intervals that only contain actuals 60% of the time is miscalibrated and dangerous—decisions based on false certainty lead to bad outcomes.

Fix:

- Evaluate interval coverage, not just point accuracy
- Prefer wider, well-calibrated intervals over narrow, overconfident ones
- When uncertain, say so—don't pretend otherwise

______________________________________________________________________

## Part 9: Resources

### Essential Reading

"Forecasting: Principles and Practice" (Hyndman & Athanasopoulos): Free online textbook covering fundamentals thoroughly. Start here. Available at otexts.com/fpp3.

Prophet paper: "Forecasting at Scale" by Taylor and Letham. Excellent for understanding decomposition-based approaches and practical considerations at scale. Even if you don't use Prophet, the framing is valuable.

### Modern Practical Tools

Nixtla ecosystem:

- `statsforecast`: Fast implementations of classical methods (ETS, ARIMA, Theta)
- `mlforecast`: ML methods with proper time series feature engineering
- `hierarchicalforecast`: Reconciliation methods

These are well-documented and production-ready.

Darts: Unified interface for classical, ML, and deep learning forecasting methods. Good for experimentation.

sktime: scikit-learn compatible API for time series. Extensive algorithm coverage.

### Competition Resources

Kaggle time series competitions: M5 (retail demand), Store Sales (Ecuadorian retail), Web Traffic (Wikipedia views). Top solutions often contain creative feature engineering ideas transferable to other domains.

M competitions: Academic forecasting competitions with well-documented methods and results. M4 and M5 are particularly informative.

### Staying Current

Time series forecasting is evolving rapidly. Foundation models for time series (like TimeGPT) are emerging, and transfer learning approaches are becoming practical. Keep an eye on:

- Nixtla blog and GitHub
- Papers from Uber, Amazon, Google on forecasting at scale
- Hyndman's blog (robjhyndman.com)
