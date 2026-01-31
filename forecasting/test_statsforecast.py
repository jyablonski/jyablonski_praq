"""
Nixtla StatsForecast Test Suite

Tests AutoARIMA, ETS, and other models from Nixtla's statsforecast library.
Compares speed and accuracy against statsmodels implementations.

Gotchas and Notes:
- StatsForecast is optimized for speed (10-100x faster than statsmodels)
- Designed for multiple time series (scales well)
- Uses numba for JIT compilation
- Different API than statsmodels (DataFrame-based)
"""

import time
import warnings
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import (
    AutoARIMA,
    AutoETS,
    AutoCES,
    AutoTheta,
    SeasonalNaive,
    Naive,
    HistoricAverage,
    WindowAverage,
    SeasonalWindowAverage,
    MSTL,
    ADIDA,
    CrostonOptimized,
    IMAPA,
)

from base import (
    generate_all_games_data,
    time_series_split,
    evaluate_forecast,
    mape,
)

warnings.filterwarnings("ignore")


# =============================================================================
# DATA PREPARATION
# =============================================================================


def prepare_for_statsforecast(
    df: pd.DataFrame,
    game_name: str,
    date_col: str = "date",
    target_col: str = "revenue",
) -> pd.DataFrame:
    """
    Prepare data for StatsForecast.

    StatsForecast expects a DataFrame with columns:
    - unique_id: identifier for the time series
    - ds: date column
    - y: target variable
    """
    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values(date_col)

    sf_df = pd.DataFrame(
        {"unique_id": game_name, "ds": game_df[date_col], "y": game_df[target_col]}
    )

    return sf_df


def prepare_all_games_for_statsforecast(
    df: pd.DataFrame, date_col: str = "date", target_col: str = "revenue"
) -> pd.DataFrame:
    """
    Prepare all games for StatsForecast (multi-series format).

    This is the recommended format for forecasting multiple series
    simultaneously, which StatsForecast handles efficiently.
    """
    sf_df = pd.DataFrame(
        {"unique_id": df["game_name"], "ds": df[date_col], "y": df[target_col]}
    )

    return sf_df.sort_values(["unique_id", "ds"])


# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================


def get_baseline_models() -> List:
    """
    Get simple baseline models for comparison.

    These provide reference points to understand if complex
    models are actually adding value.
    """
    return [
        Naive(),
        SeasonalNaive(season_length=7),
        HistoricAverage(),
        WindowAverage(window_size=7),
        SeasonalWindowAverage(season_length=7, window_size=4),
    ]


def get_statistical_models(season_length: int = 7) -> List:
    """
    Get main statistical models from StatsForecast.

    Parameters
    ----------
    season_length : int
        Seasonal period (7 for daily data with weekly pattern)
    """
    return [
        AutoARIMA(season_length=season_length),
        AutoETS(season_length=season_length),
        AutoTheta(season_length=season_length),
        AutoCES(season_length=season_length),
        MSTL(season_length=season_length),
    ]


def get_intermittent_demand_models() -> List:
    """
    Models for sparse/intermittent data.

    These can be useful for:
    - New games with limited history
    - Low-volume titles
    - Sparse event-based revenue
    """
    return [
        ADIDA(),
        CrostonOptimized(),
        IMAPA(),
    ]


def get_all_models(season_length: int = 7) -> List:
    """Get all available models."""
    return get_baseline_models() + get_statistical_models(season_length)


# =============================================================================
# STATSFORECAST WRAPPER
# =============================================================================


class StatsForecastWrapper:
    """
    Wrapper for StatsForecast with convenient methods.

    Gotchas:
    - First run may be slow due to numba compilation
    - Parallel fitting can be memory-intensive
    - Some models may fail on certain data patterns
    """

    def __init__(self, models: List, freq: str = "D", n_jobs: int = 1):
        self.models = models
        self.freq = freq
        self.n_jobs = n_jobs
        self.sf = None
        self.train_time = None
        self.fitted_df = None

    def fit(self, df: pd.DataFrame) -> "StatsForecastWrapper":
        """
        Fit all models to the data.

        Parameters
        ----------
        df : pd.DataFrame
            Data in StatsForecast format (unique_id, ds, y)
        """
        start_time = time.time()

        self.sf = StatsForecast(models=self.models, freq=self.freq, n_jobs=self.n_jobs)

        self.fitted_df = df.copy()

        self.train_time = time.time() - start_time
        return self

    def predict(self, h: int) -> pd.DataFrame:
        """
        Generate forecasts for h periods ahead.

        Returns DataFrame with columns for each model's predictions.
        """
        start_time = time.time()

        forecast = self.sf.forecast(df=self.fitted_df, h=h)

        forecast_time = time.time() - start_time

        return forecast

    def cross_validate(
        self, df: pd.DataFrame, h: int, n_windows: int = 3, step_size: int = 30
    ) -> pd.DataFrame:
        """
        Perform time series cross-validation.

        Parameters
        ----------
        df : pd.DataFrame
            Data in StatsForecast format
        h : int
            Forecast horizon
        n_windows : int
            Number of cross-validation windows
        step_size : int
            Step size between windows

        Returns
        -------
        pd.DataFrame
            Cross-validation results with actuals and predictions
        """
        cv_results = self.sf.cross_validation(
            df=df, h=h, n_windows=n_windows, step_size=step_size
        )

        return cv_results

    def get_model_names(self) -> List[str]:
        """Get names of all fitted models."""
        return [str(model) for model in self.models]


# =============================================================================
# EXPERIMENTS
# =============================================================================


def run_statsforecast_experiment(
    df: pd.DataFrame,
    game_name: str,
    holdout_periods: List[int] = [30, 60, 90],
    models: Optional[List] = None,
    season_length: int = 7,
) -> pd.DataFrame:
    """
    Run StatsForecast experiments for a specific game.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    game_name : str
        Name of the game
    holdout_periods : list
        Holdout periods to test
    models : list
        Models to test (uses all if None)
    season_length : int
        Seasonal period

    Returns
    -------
    pd.DataFrame
        Results for all models and holdout periods
    """
    if models is None:
        models = get_all_models(season_length)

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    results = []

    for period in holdout_periods:
        print(f"\n  {period}-day holdout:")

        train, test = time_series_split(game_df, period)

        # Prepare for StatsForecast
        train_sf = prepare_for_statsforecast(train, game_name, "date", "revenue")

        # Create wrapper and fit
        start_time = time.time()
        wrapper = StatsForecastWrapper(models=models, freq="D", n_jobs=1)
        wrapper.fit(train_sf)

        # Predict
        forecast = wrapper.predict(h=len(test))
        total_time = time.time() - start_time

        # Evaluate each model
        y_true = test["revenue"].values

        # Get model columns (exclude unique_id and ds)
        model_cols = [col for col in forecast.columns if col not in ["unique_id", "ds"]]

        for model_name in model_cols:
            predictions = forecast[model_name].values

            metrics = evaluate_forecast(y_true, predictions, model_name)
            metrics["holdout_days"] = period
            metrics["train_time_sec"] = total_time / len(model_cols)  # Approximate
            metrics["game"] = game_name
            metrics["library"] = "statsforecast"

            results.append(metrics)

            print(f"    {model_name}: MAPE = {metrics['mape']:.2f}%")

    return pd.DataFrame(results)


def run_speed_comparison(
    df: pd.DataFrame, game_name: str, test_days: int = 30, n_runs: int = 3
) -> Dict:
    """
    Compare training speed between statsforecast and statsmodels.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    game_name : str
        Game to use for comparison
    test_days : int
        Holdout period
    n_runs : int
        Number of runs for timing

    Returns
    -------
    dict
        Timing results for each library
    """
    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")
    train, test = time_series_split(game_df, test_days)

    results = {
        "statsforecast": {"times": [], "mape": None},
        "statsmodels": {"times": [], "mape": None},
    }

    # StatsForecast timing
    train_sf = prepare_for_statsforecast(train, game_name, "date", "revenue")

    print(f"Running StatsForecast AutoARIMA ({n_runs} runs)...")
    for i in range(n_runs):
        start = time.time()

        sf = StatsForecast(models=[AutoARIMA(season_length=7)], freq="D", n_jobs=1)
        forecast = sf.forecast(df=train_sf, h=len(test))

        elapsed = time.time() - start
        results["statsforecast"]["times"].append(elapsed)
        print(f"  Run {i + 1}: {elapsed:.3f}s")

    # Calculate MAPE for StatsForecast
    predictions_sf = forecast["AutoARIMA"].values
    results["statsforecast"]["mape"] = mape(test["revenue"].values, predictions_sf)

    # Statsmodels timing (using pmdarima's auto_arima for fair comparison)
    print(f"\nRunning statsmodels/pmdarima auto_arima ({n_runs} runs)...")

    try:
        from pmdarima import auto_arima

        train_ts = train.set_index("date")["revenue"]

        for i in range(n_runs):
            start = time.time()

            model = auto_arima(
                train_ts, m=7, seasonal=True, stepwise=True, suppress_warnings=True
            )
            predictions_sm = model.predict(n_periods=len(test))

            elapsed = time.time() - start
            results["statsmodels"]["times"].append(elapsed)
            print(f"  Run {i + 1}: {elapsed:.3f}s")

        results["statsmodels"]["mape"] = mape(test["revenue"].values, predictions_sm)

    except ImportError:
        print("  pmdarima not installed, skipping statsmodels comparison")
        results["statsmodels"]["times"] = [np.nan] * n_runs
        results["statsmodels"]["mape"] = np.nan

    # Summary
    sf_avg = np.mean(results["statsforecast"]["times"])
    sm_avg = np.mean(results["statsmodels"]["times"])

    print(f"\n--- Speed Comparison Summary ---")
    print(
        f"StatsForecast: {sf_avg:.3f}s avg, MAPE = {results['statsforecast']['mape']:.2f}%"
    )
    if not np.isnan(sm_avg):
        print(
            f"Statsmodels:   {sm_avg:.3f}s avg, MAPE = {results['statsmodels']['mape']:.2f}%"
        )
        print(f"Speedup:       {sm_avg / sf_avg:.1f}x faster")

    return results


def run_multi_series_experiment(
    df: pd.DataFrame, holdout_days: int = 30, models: Optional[List] = None
) -> pd.DataFrame:
    """
    Run StatsForecast on all games simultaneously.

    This demonstrates StatsForecast's ability to efficiently
    forecast multiple time series in a single call.
    """
    if models is None:
        models = [
            AutoARIMA(season_length=7),
            AutoETS(season_length=7),
            SeasonalNaive(season_length=7),
        ]

    print("Preparing multi-series data...")

    # Split each game's data
    train_dfs = []
    test_data = {}

    for game in df["game_name"].unique():
        game_df = df[df["game_name"] == game].copy()
        game_df = game_df.sort_values("date")

        train, test = time_series_split(game_df, holdout_days)

        train_sf = pd.DataFrame(
            {"unique_id": game, "ds": train["date"], "y": train["revenue"]}
        )
        train_dfs.append(train_sf)
        test_data[game] = test["revenue"].values

    all_train = pd.concat(train_dfs, ignore_index=True)

    print(f"Total training records: {len(all_train)}")
    print(f"Number of series: {all_train['unique_id'].nunique()}")

    # Fit and predict
    print("\nFitting models...")
    start_time = time.time()

    sf = StatsForecast(models=models, freq="D", n_jobs=1)

    forecasts = sf.forecast(df=all_train, h=holdout_days)

    total_time = time.time() - start_time
    print(f"Total fit + predict time: {total_time:.2f}s")
    print(f"Average per series: {total_time / len(test_data):.3f}s")

    # Evaluate
    results = []
    model_cols = [col for col in forecasts.columns if col not in ["unique_id", "ds"]]

    for game in test_data.keys():
        game_forecast = forecasts[forecasts["unique_id"] == game]
        y_true = test_data[game]

        for model_name in model_cols:
            predictions = game_forecast[model_name].values

            metrics = evaluate_forecast(y_true, predictions, model_name)
            metrics["game"] = game
            metrics["holdout_days"] = holdout_days

            results.append(metrics)

    results_df = pd.DataFrame(results)

    print("\n--- Multi-Series Results ---")
    print(results_df.groupby("name")["mape"].agg(["mean", "std", "min", "max"]))

    return results_df


# =============================================================================
# RUN ALL EXPERIMENTS
# =============================================================================


def run_all_statsforecast_experiments(
    df: pd.DataFrame,
    games: Optional[List[str]] = None,
    holdout_periods: List[int] = [30, 60, 90],
    save_results: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Run all StatsForecast experiments.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    games : list
        List of game names to test
    holdout_periods : list
        Holdout periods to evaluate
    save_results : bool
        Whether to save results to CSV

    Returns
    -------
    dict
        Results DataFrames
    """
    if games is None:
        games = df["game_name"].unique().tolist()

    all_results = []

    for game in games:
        print(f"\n{'=' * 60}")
        print(f"Processing: {game}")
        print("=" * 60)

        results = run_statsforecast_experiment(df, game, holdout_periods)
        all_results.append(results)

    main_results = pd.concat(all_results, ignore_index=True)

    # Multi-series experiment
    print(f"\n{'=' * 60}")
    print("Multi-Series Experiment (All Games Together)")
    print("=" * 60)
    multi_results = run_multi_series_experiment(df, holdout_days=30)

    # Speed comparison
    print(f"\n{'=' * 60}")
    print("Speed Comparison vs Statsmodels")
    print("=" * 60)
    speed_results = run_speed_comparison(df, games[0])

    if save_results:
        main_results.to_csv("output/results_statsforecast.csv", index=False)
        multi_results.to_csv("output/results_statsforecast_multi.csv", index=False)
        print("\nResults saved to output/results_statsforecast*.csv")

    return {
        "main_results": main_results,
        "multi_series": multi_results,
        "speed_comparison": speed_results,
    }


# =============================================================================
# DOCUMENTATION AND GOTCHAS
# =============================================================================

STATSFORECAST_GOTCHAS = """
=============================================================================
NIXTLA STATSFORECAST - GOTCHAS AND RECOMMENDATIONS
=============================================================================

1. SPEED ADVANTAGE
------------------
StatsForecast is significantly faster than statsmodels:
- AutoARIMA: 10-50x faster
- AutoETS: 5-20x faster
- Can process hundreds of series in seconds

Why it's faster:
- Numba JIT compilation
- Optimized algorithms (different from statsmodels)
- Designed for production use

First-run caveat:
- Initial run may be slow due to numba compilation
- Subsequent runs are much faster
- Use n_jobs=1 for single series to avoid overhead

2. DATA FORMAT
--------------
Required columns:
- unique_id: Series identifier (string)
- ds: Date column (datetime)
- y: Target variable (float)

Multi-series support:
- Can forecast multiple series in one call
- Efficient for panel data
- Each series identified by unique_id

3. AUTOARIMA DIFFERENCES
-------------------------
StatsForecast AutoARIMA vs pmdarima auto_arima:
- Different default search strategy
- May select different orders
- Generally similar accuracy
- StatsForecast much faster

Default behavior:
- Automatic differencing
- Seasonal detection
- Stepwise search (faster)

4. AUTOETS
-----------
Automatic Exponential Smoothing selection:
- Tests multiple ETS configurations
- Selects best by AIC
- Handles additive/multiplicative automatically

Compared to statsmodels ExponentialSmoothing:
- More automated model selection
- Similar core algorithms
- Faster execution

5. BASELINE MODELS
------------------
Always include baselines for comparison:
- Naive: Last value repeated
- SeasonalNaive: Same value from last season
- HistoricAverage: Mean of all history

These help validate if complex models add value.

6. MISSING DATA HANDLING
-------------------------
StatsForecast behavior:
- Does NOT automatically handle missing dates
- Expects continuous time series
- Missing values (NaN) will cause issues

Recommendation:
- Resample data to fill missing dates
- Interpolate or forward-fill missing values
- Ensure data is sorted by date

7. EXOGENOUS VARIABLES
-----------------------
Current limitations:
- AutoARIMA supports exogenous via futr_df
- Not as seamless as Prophet
- Requires careful alignment of dates

For sale events:
- Consider using Prophet or LightGBM
- Or add pre-processing to adjust for events
- Can use futr_df for known future events

8. PRODUCTION CONSIDERATIONS
-----------------------------
Scaling:
- Efficient for thousands of series
- Use n_jobs > 1 for parallel processing
- Memory-efficient compared to alternatives

Deployment:
- Easy to serialize models
- Consistent API
- Good for batch forecasting

9. MODEL SELECTION
-------------------
For game revenue:
- AutoARIMA: Good for trending data
- AutoETS: Good for level + seasonality
- AutoTheta: Good for short-term forecasts
- SeasonalNaive: Baseline with weekly pattern

Ensemble approach:
- Combine multiple models for robustness
- StatsForecast makes this easy

10. COMMON ISSUES
-----------------
Issue: Slow first run
- Normal due to numba compilation
- Cache persists in session

Issue: Different results than statsmodels
- Different algorithm implementations
- Both are valid, may have different biases

Issue: Errors with short series
- Some models need minimum history
- Use simpler models for short series

=============================================================================
"""


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("Nixtla StatsForecast Test Suite")
    print("=" * 60)

    # Generate synthetic data
    print("\nGenerating synthetic game revenue data...")
    df = generate_all_games_data()

    print(f"Data shape: {df.shape}")
    print(f"Games: {df['game_name'].unique().tolist()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    # Run experiments
    print("\n" + "=" * 60)
    print("Running StatsForecast Experiments")
    print("=" * 60)

    results = run_all_statsforecast_experiments(
        df,
        games=None,  # All games
        holdout_periods=[30, 60, 90],
        save_results=True,
    )

    # Summary
    print("\n" + "=" * 60)
    print("Main Results Summary (by Model)")
    print("=" * 60)
    summary = (
        results["main_results"]
        .groupby("name")["mape"]
        .agg(["mean", "std", "min", "max"])
    )
    print(summary.sort_values("mean"))

    print("\n" + "=" * 60)
    print("Best Model per Game (30-day holdout)")
    print("=" * 60)
    best = results["main_results"][results["main_results"]["holdout_days"] == 30]
    best_idx = best.groupby("game")["mape"].idxmin()
    print(best.loc[best_idx][["game", "name", "mape"]])

    # Print gotchas
    print(STATSFORECAST_GOTCHAS)
