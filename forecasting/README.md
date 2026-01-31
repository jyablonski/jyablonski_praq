# Forecasting Library Comparison

A comprehensive benchmarking suite for time series forecasting methods applied to revenue prediction. Tests multiple approaches (statistical, ML, deep learning) on synthetic game data with realistic patterns.

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run quick comparison
python walk_forward_cv.py

# Use the unified forecaster API
python forecaster.py
```

## Project Structure

```
forecasting/
├── base.py                    # Core: data generation, metrics, utilities
├── forecaster.py              # Unified API for production use
├── prediction_intervals.py    # Confidence interval estimation
├── walk_forward_cv.py         # Cross-validation framework
├── compare_results.py         # Comparison report generator
│
├── test_statsmodels.py        # ARIMA, Holt-Winters experiments
├── test_statsforecast.py      # AutoETS, AutoARIMA (Nixtla)
├── test_prophet.py            # Facebook Prophet experiments
├── test_lightgbm.py           # ML gradient boosting approach
├── test_ensemble.py           # Ensemble methods
│
├── requirements.txt           # Dependencies
└── output/                    # Results and plots
    ├── cv_final_summary.csv   # Walk-forward CV results
    ├── unified_comparison.csv # Single-split comparison
    └── *.png                  # Visualizations
```

## Methods Tested

| Method | Library | Description | Avg Fit Time |
| --------------------------- | ------------- | ---------------------------------------------- | ------------ |
| output/Holt-Wintersoutput/ | statsmodels | Exponential smoothing with trend + seasonality | ~0.12s |
| output/AutoETSoutput/ | statsforecast | Automatic ETS model selection | ~0.41s |
| output/AutoARIMAoutput/ | statsforecast | Automatic ARIMA order selection | ~6.4s |
| output/Prophetoutput/ | prophet | Facebook's decomposable model | ~0.15s |
| output/LightGBMoutput/ | lightgbm | Gradient boosting with lag features | ~0.34s |
| output/SeasonalNaiveoutput/ | custom | Baseline: repeat last week | ~0.00s |

## Results Summary

### Walk-Forward Cross-Validation Results (4 folds, 30-day test)

Tested across 5 synthetic games with different lifecycles:

| Method | Avg MAPE | Std | 95% CI | Recommendation |
| --------------------------- | -------- | ------ | --------------- | ---------------------- |
| output/HW-Mul-Dampedoutput/ | 21.4% | 4.1% | [11.7%, 31.2%] | Best overall |
| output/AutoETSoutput/ | 21.6% | 4.2% | [11.4%, 31.7%] | Good alternative |
| output/HW-Add-Dampedoutput/ | 21.7% | 4.2% | [12.1%, 31.4%] | Very consistent |
| output/SeasonalNaiveoutput/ | 23.7% | 5.3% | [14.7%, 32.7%] | Solid baseline |
| output/LightGBMoutput/ | 31.7% | 18.8% | [9.2%, 65.0%] | High variance |
| output/AutoARIMAoutput/ | 50.0% | 56.9% | [37.3%, 62.7%] | Struggles w/ new games |
| output/Prophetoutput/ | 98.1% | 159.0% | [30.7%, 165.6%] | Very inconsistent |

### Key Findings

1. output/Holt-Winters dominatesoutput/: Simple exponential smoothing with multiplicative seasonality and damped trend consistently outperforms more complex methods.

1. output/Prophet struggles with new launchesoutput/: Games with short history and rapid decay cause Prophet to produce wildly inaccurate forecasts (300%+ MAPE on Galaxy Conquest).

1. output/LightGBM is inconsistentoutput/: While it wins on some stable games, recursive multi-step prediction causes error accumulation. Best reserved for games with rich external features.

1. output/AutoARIMA is slow and unreliableoutput/: 50x slower than Holt-Winters with worse average performance.

1. output/Baselines are hard to beatoutput/: SeasonalNaive (just repeat last week) is only ~2% worse than the best statistical methods.

## Synthetic Data Characteristics

Five game types with different revenue patterns:

| Game | Type | History | Pattern |
| --------------- | ------------ | --------- | ------------------------------ |
| Galaxy Conquest | New Launch | 307 days | High spike, fast decay |
| Eternal Legends | Mature | 1111 days | Stable, slow decline |
| Battle Royale X | Live Service | 746 days | Content drop bumps |
| Pixel Adventure | Indie | 503 days | Moderate launch, gradual decay |
| Dungeon Depths | Struggling | 960 days | Low base, high noise |

All games include:

- Weekly seasonality (weekend boosts)
- Sale events (Summer Sale, Black Friday, etc.)
- Random noise (8-20% depending on game)

## Usage Examples

### Quick Forecast with Default Settings

```python
from forecaster import quick_forecast
from base import generate_all_games_data

df = generate_all_games_data()
game_df = df[df['game_name'] == 'Battle Royale X']

# Get 30-day forecast with automatic method selection
result = quick_forecast(game_df, horizon=30)
print(result.to_dataframe())
```

### Walk-Forward Cross-Validation

```python
from walk_forward_cv import WalkForwardCV, make_holt_winters_forecaster

cv = WalkForwardCV(n_splits=5, test_size=30)
result = cv.evaluate(
    game_df, 
    make_holt_winters_forecaster(seasonal='mul', damped_trend=True),
    'HW-Mul-Damped'
)

print(f"MAPE: {result.mape_mean:.1f}% +/- {result.mape_std:.1f}%")
print(f"95% CI: [{result.mape_ci[0]:.1f}%, {result.mape_ci[1]:.1f}%]")
```

### Prediction Intervals

```python
from forecaster import GameRevenueForecaster

forecaster = GameRevenueForecaster(method='holt_winters')
forecaster.fit(train_df)
result = forecaster.predict_with_intervals(30, coverage=0.90)

# Returns forecast with lower/upper bounds
print(result.to_dataframe())
```

### Compare Multiple Methods

```python
from walk_forward_cv import run_cv_comparison

results = run_cv_comparison(
    df,
    game_name='Eternal Legends',
    methods=['HW-Mul-Damped', 'AutoETS', 'Prophet', 'LightGBM'],
    n_splits=5,
    test_size=30
)
print(results.sort_values('mape_mean'))
```

## Recommendations for Production

### Method Selection by Game Type

| Game Type | Recommended Method | Reason |
| ------------------------------------- | ------------------ | ---------------------------------------- |
| output/New Launchoutput/ (< 6 months) | HW-Mul-Damped | Robust to short history, handles decay |
| output/Mature/Stableoutput/ | AutoETS or HW | Both work well, AutoETS slightly better |
| output/Live Serviceoutput/ | HW-Mul-Damped | Handles content drop volatility |
| output/High Noiseoutput/ | HW-Add-Damped | Additive seasonality more robust |
| output/Rich External Dataoutput/ | LightGBM | Can leverage sale flags, marketing spend |

### Implementation Checklist

1. output/Start with Holt-Wintersoutput/: Use `HW-Mul-Damped` as your default. It's fast, robust, and hard to beat.

1. output/Add prediction intervalsoutput/: Use conformal prediction (see `prediction_intervals.py`) for honest uncertainty quantification.

1. output/Use walk-forward CVoutput/: Don't trust single train/test splits. CV gives confidence intervals on your metrics.

1. output/Monitor for regime changesoutput/: Track forecast errors over time. Sudden increases may indicate game lifecycle changes.

1. output/Consider ensembles for critical forecastsoutput/: Simple average of top 3 methods often beats any single method.

### What NOT to Do

- Don't use Prophet for games with < 1 year of history
- Don't use LightGBM with "direct" multi-step prediction (use recursive)
- Don't trust AutoARIMA on games with structural breaks
- Don't skip the baseline comparison (SeasonalNaive)

## Future Improvements

1. output/Neural Methodsoutput/: Add N-BEATS, Temporal Fusion Transformer
1. output/Hyperparameter Tuningoutput/: All methods currently use defaults
1. output/Real Data Validationoutput/: Test on actual game revenue data
1. output/Hierarchical Forecastingoutput/: Forecast by platform/region and reconcile
1. output/Anomaly Detectionoutput/: Flag unusual revenue patterns automatically

## Dependencies

```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
scipy>=1.7.0
statsmodels>=0.13.0
pmdarima>=2.0.0
prophet>=1.1.0
statsforecast>=1.4.0
lightgbm>=3.3.0
scikit-learn>=1.0.0
```
