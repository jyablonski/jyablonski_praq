"""
Statsmodels Forecasting Test Suite

Tests ARIMA, Exponential Smoothing (Holt-Winters), and Seasonal Decomposition
for game revenue forecasting.

Gotchas and Notes:
- ARIMA requires stationary data; may need differencing
- Seasonal ARIMA (SARIMA) can be very slow to fit with long seasonal periods
- Holt-Winters works well with clear seasonal patterns
- auto_arima from pmdarima is more convenient than manual order selection
- Missing data must be handled before fitting (interpolation or forward-fill)
"""

import time
import warnings
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Optional: pmdarima for auto ARIMA
try:
    from pmdarima import auto_arima

    PMDARIMA_AVAILABLE = True
except ImportError:
    PMDARIMA_AVAILABLE = False
    print("Warning: pmdarima not installed. Auto ARIMA will not be available.")

from base import (
    generate_all_games_data,
    time_series_split,
    evaluate_forecast,
    prepare_for_statsmodels,
)

warnings.filterwarnings("ignore")


# =============================================================================
# DIAGNOSTIC FUNCTIONS
# =============================================================================


def check_stationarity(series: pd.Series, name: str = "Series") -> Dict:
    """
    Perform Augmented Dickey-Fuller test for stationarity.

    Returns
    -------
    dict
        Test results including test statistic, p-value, and conclusion
    """
    result = adfuller(series.dropna(), autolag="AIC")

    output = {
        "name": name,
        "test_statistic": result[0],
        "p_value": result[1],
        "lags_used": result[2],
        "n_observations": result[3],
        "critical_values": result[4],
        "is_stationary": result[1] < 0.05,
    }

    return output


def plot_diagnostics(
    series: pd.Series, lags: int = 40, figsize: Tuple[int, int] = (14, 10)
) -> plt.Figure:
    """
    Plot time series diagnostics including ACF and PACF.

    Useful for determining ARIMA orders.
    """
    fig, axes = plt.subplots(3, 2, figsize=figsize)

    # Original series
    axes[0, 0].plot(series)
    axes[0, 0].set_title("Original Series")
    axes[0, 0].set_xlabel("Date")
    axes[0, 0].set_ylabel("Value")

    # Distribution
    axes[0, 1].hist(series, bins=50, edgecolor="black", alpha=0.7)
    axes[0, 1].set_title("Distribution")
    axes[0, 1].set_xlabel("Value")
    axes[0, 1].set_ylabel("Frequency")

    # ACF
    plot_acf(series, lags=lags, ax=axes[1, 0])
    axes[1, 0].set_title("Autocorrelation Function (ACF)")

    # PACF
    plot_pacf(series, lags=lags, ax=axes[1, 1])
    axes[1, 1].set_title("Partial Autocorrelation Function (PACF)")

    # First difference
    diff = series.diff().dropna()
    axes[2, 0].plot(diff)
    axes[2, 0].set_title("First Difference")
    axes[2, 0].set_xlabel("Date")

    # ACF of differenced series
    plot_acf(diff, lags=lags, ax=axes[2, 1])
    axes[2, 1].set_title("ACF of First Difference")

    plt.tight_layout()
    return fig


# =============================================================================
# SEASONAL DECOMPOSITION
# =============================================================================


def run_seasonal_decomposition(
    series: pd.Series, period: int = 7, model: str = "additive"
) -> Tuple[object, plt.Figure]:
    """
    Perform classical seasonal decomposition.

    Parameters
    ----------
    series : pd.Series
        Time series data
    period : int
        Seasonal period (7 for daily data with weekly seasonality)
    model : str
        'additive' or 'multiplicative'

    Returns
    -------
    decomposition result and figure
    """
    decomposition = seasonal_decompose(series, model=model, period=period)

    fig, axes = plt.subplots(4, 1, figsize=(14, 12))

    decomposition.observed.plot(ax=axes[0])
    axes[0].set_title("Observed")
    axes[0].set_ylabel("Revenue")

    decomposition.trend.plot(ax=axes[1])
    axes[1].set_title("Trend")
    axes[1].set_ylabel("Revenue")

    decomposition.seasonal.plot(ax=axes[2])
    axes[2].set_title("Seasonal")
    axes[2].set_ylabel("Revenue")

    decomposition.resid.plot(ax=axes[3])
    axes[3].set_title("Residual")
    axes[3].set_ylabel("Revenue")

    plt.tight_layout()

    return decomposition, fig


def run_stl_decomposition(
    series: pd.Series, period: int = 7, robust: bool = True
) -> Tuple[object, plt.Figure]:
    """
    Perform STL (Seasonal-Trend decomposition using LOESS).

    More robust than classical decomposition, handles outliers better.
    """
    stl = STL(series, period=period, robust=robust)
    result = stl.fit()

    fig = result.plot()
    fig.set_size_inches(14, 12)

    return result, fig


# =============================================================================
# ARIMA FORECASTING
# =============================================================================


class ARIMAForecaster:
    """
    ARIMA forecaster with automatic or manual order selection.

    Gotchas:
    - ARIMA requires stationary data
    - High seasonal periods (e.g., 365 for yearly) are computationally expensive
    - Use auto_arima from pmdarima for automatic order selection
    - For daily data with weekly seasonality, consider SARIMA with m=7
    """

    def __init__(
        self,
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
        use_auto: bool = True,
    ):
        self.order = order
        self.seasonal_order = seasonal_order
        self.use_auto = use_auto
        self.model = None
        self.fitted = None
        self.train_time = None

    def fit(self, series: pd.Series) -> "ARIMAForecaster":
        """Fit the ARIMA model."""
        start_time = time.time()

        if self.use_auto and PMDARIMA_AVAILABLE:
            # Auto ARIMA finds optimal orders automatically
            self.fitted = auto_arima(
                series,
                start_p=0,
                start_q=0,
                max_p=5,
                max_q=5,
                m=7,  # Weekly seasonality
                start_P=0,
                start_Q=0,
                max_P=2,
                max_Q=2,
                seasonal=True,
                d=None,  # Auto-detect differencing
                D=None,  # Auto-detect seasonal differencing
                trace=False,
                error_action="ignore",
                suppress_warnings=True,
                stepwise=True,  # Faster search
                n_fits=50,
            )
            self.order = self.fitted.order
            self.seasonal_order = self.fitted.seasonal_order
        else:
            # Manual ARIMA
            if self.seasonal_order:
                self.model = ARIMA(
                    series, order=self.order, seasonal_order=self.seasonal_order
                )
            else:
                self.model = ARIMA(series, order=self.order)
            self.fitted = self.model.fit()

        self.train_time = time.time() - start_time
        return self

    def predict(self, steps: int) -> np.ndarray:
        """Generate forecasts for specified number of steps."""
        if self.use_auto and PMDARIMA_AVAILABLE:
            return self.fitted.predict(n_periods=steps)
        else:
            return self.fitted.forecast(steps=steps)

    def get_summary(self) -> str:
        """Get model summary."""
        if self.fitted is not None:
            if self.use_auto and PMDARIMA_AVAILABLE:
                return self.fitted.summary().as_text()
            else:
                return str(self.fitted.summary())
        return "Model not fitted"


def run_arima_experiment(
    df: pd.DataFrame,
    game_name: str,
    holdout_periods: List[int] = [30, 60, 90],
    use_auto: bool = True,
) -> pd.DataFrame:
    """
    Run ARIMA experiments for a specific game.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    game_name : str
        Name of the game to forecast
    holdout_periods : list
        List of holdout periods to test
    use_auto : bool
        Whether to use auto ARIMA

    Returns
    -------
    pd.DataFrame
        Results for each holdout period
    """
    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    results = []

    for period in holdout_periods:
        train, test = time_series_split(game_df, period)

        # Prepare time series
        train_ts = prepare_for_statsmodels(train)

        # Fit model
        forecaster = ARIMAForecaster(use_auto=use_auto)
        forecaster.fit(train_ts)

        # Predict
        predictions = forecaster.predict(len(test))

        # Evaluate
        metrics = evaluate_forecast(
            test["revenue"].values, predictions, f"ARIMA ({forecaster.order})"
        )
        metrics["holdout_days"] = period
        metrics["train_time_sec"] = forecaster.train_time
        metrics["order"] = str(forecaster.order)
        metrics["seasonal_order"] = str(forecaster.seasonal_order)
        metrics["game"] = game_name

        results.append(metrics)

        print(
            f"{game_name} | {period}-day holdout | "
            f"ARIMA{forecaster.order} | MAPE: {metrics['mape']:.2f}% | "
            f"Time: {forecaster.train_time:.2f}s"
        )

    return pd.DataFrame(results)


# =============================================================================
# EXPONENTIAL SMOOTHING (HOLT-WINTERS)
# =============================================================================


class HoltWintersForecaster:
    """
    Holt-Winters Exponential Smoothing forecaster.

    Gotchas:
    - Requires at least 2 full seasonal cycles of data
    - 'mul' trend/seasonal can fail with zeros/negatives in data
    - Initialization method affects results significantly
    - For irregular seasonality, consider STL decomposition first
    """

    def __init__(
        self,
        trend: str = "add",
        seasonal: str = "add",
        seasonal_periods: int = 7,
        damped_trend: bool = True,
        use_boxcox: bool = False,
    ):
        self.trend = trend
        self.seasonal = seasonal
        self.seasonal_periods = seasonal_periods
        self.damped_trend = damped_trend
        self.use_boxcox = use_boxcox
        self.model = None
        self.fitted = None
        self.train_time = None

    def fit(self, series: pd.Series) -> "HoltWintersForecaster":
        """Fit the Holt-Winters model."""
        start_time = time.time()

        # Ensure positive values for multiplicative models
        if self.seasonal == "mul" or self.trend == "mul":
            series = series.clip(lower=0.01)

        self.model = ExponentialSmoothing(
            series,
            trend=self.trend,
            seasonal=self.seasonal,
            seasonal_periods=self.seasonal_periods,
            damped_trend=self.damped_trend,
            use_boxcox=self.use_boxcox,
            initialization_method="estimated",
        )

        self.fitted = self.model.fit(optimized=True, remove_bias=True)

        self.train_time = time.time() - start_time
        return self

    def predict(self, steps: int) -> np.ndarray:
        """Generate forecasts."""
        return self.fitted.forecast(steps=steps)

    def get_components(self) -> Dict[str, np.ndarray]:
        """Get fitted components (level, trend, season)."""
        return {
            "level": self.fitted.level,
            "trend": self.fitted.trend if self.trend else None,
            "season": self.fitted.season if self.seasonal else None,
        }


def run_holtwinters_experiment(
    df: pd.DataFrame,
    game_name: str,
    holdout_periods: List[int] = [30, 60, 90],
    configurations: Optional[List[Dict]] = None,
) -> pd.DataFrame:
    """
    Run Holt-Winters experiments with multiple configurations.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    game_name : str
        Name of the game
    holdout_periods : list
        Holdout periods to test
    configurations : list
        List of configuration dicts for different HW settings

    Returns
    -------
    pd.DataFrame
        Results for all configurations and holdout periods
    """
    if configurations is None:
        configurations = [
            {
                "trend": "add",
                "seasonal": "add",
                "damped_trend": True,
                "name": "HW-Add-Damped",
            },
            {
                "trend": "add",
                "seasonal": "mul",
                "damped_trend": True,
                "name": "HW-Mul-Damped",
            },
            {
                "trend": "add",
                "seasonal": "add",
                "damped_trend": False,
                "name": "HW-Add",
            },
            {
                "trend": None,
                "seasonal": "add",
                "damped_trend": False,
                "name": "SES-Seasonal",
            },
        ]

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    results = []

    for period in holdout_periods:
        train, test = time_series_split(game_df, period)
        train_ts = prepare_for_statsmodels(train)

        for config in configurations:
            config_name = config.pop("name", "HW")

            try:
                forecaster = HoltWintersForecaster(seasonal_periods=7, **config)
                forecaster.fit(train_ts)
                predictions = forecaster.predict(len(test))

                metrics = evaluate_forecast(
                    test["revenue"].values, predictions, config_name
                )
                metrics["holdout_days"] = period
                metrics["train_time_sec"] = forecaster.train_time
                metrics["configuration"] = config_name
                metrics["game"] = game_name

                print(
                    f"{game_name} | {period}-day | {config_name} | "
                    f"MAPE: {metrics['mape']:.2f}% | "
                    f"Time: {forecaster.train_time:.3f}s"
                )

            except Exception as e:
                print(f"Error with {config_name}: {str(e)}")
                metrics = {
                    "name": config_name,
                    "mape": np.nan,
                    "rmse": np.nan,
                    "smape": np.nan,
                    "mae": np.nan,
                    "holdout_days": period,
                    "train_time_sec": np.nan,
                    "configuration": config_name,
                    "game": game_name,
                    "error": str(e),
                }

            # Restore name for next iteration
            config["name"] = config_name
            results.append(metrics)

    return pd.DataFrame(results)


# =============================================================================
# COMBINED EXPERIMENTS
# =============================================================================


def run_all_statsmodels_experiments(
    df: pd.DataFrame,
    games: Optional[List[str]] = None,
    holdout_periods: List[int] = [30, 60, 90],
    save_results: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Run all statsmodels experiments (ARIMA, Holt-Winters, decomposition).

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset with all games
    games : list, optional
        List of game names to test (uses all if None)
    holdout_periods : list
        Holdout periods to evaluate
    save_results : bool
        Whether to save results to CSV

    Returns
    -------
    dict
        Dictionary with results DataFrames for each method
    """
    if games is None:
        games = df["game_name"].unique().tolist()

    all_results = {"arima": [], "holtwinters": [], "decomposition": []}

    for game in games:
        print(f"\n{'=' * 60}")
        print(f"Processing: {game}")
        print("=" * 60)

        # ARIMA
        print("\n--- ARIMA ---")
        arima_results = run_arima_experiment(df, game, holdout_periods)
        all_results["arima"].append(arima_results)

        # Holt-Winters
        print("\n--- Holt-Winters ---")
        hw_results = run_holtwinters_experiment(df, game, holdout_periods)
        all_results["holtwinters"].append(hw_results)

        # Decomposition analysis
        print("\n--- Seasonal Decomposition ---")
        game_df = df[df["game_name"] == game].copy()
        game_df = game_df.sort_values("date")
        series = prepare_for_statsmodels(game_df)

        try:
            stl_result, _ = run_stl_decomposition(series, period=7)

            # Calculate strength of seasonality and trend
            var_resid = np.var(stl_result.resid.dropna())
            var_seasonal = np.var(stl_result.seasonal)
            var_trend = np.var(stl_result.trend.dropna())

            seasonal_strength = max(0, 1 - var_resid / (var_resid + var_seasonal))
            trend_strength = max(0, 1 - var_resid / (var_resid + var_trend))

            decomp_result = {
                "game": game,
                "seasonal_strength": seasonal_strength,
                "trend_strength": trend_strength,
                "resid_variance": var_resid,
            }
            all_results["decomposition"].append(decomp_result)

            print(f"Seasonal strength: {seasonal_strength:.3f}")
            print(f"Trend strength: {trend_strength:.3f}")
        except Exception as e:
            print(f"Decomposition failed: {e}")

    # Combine results
    results = {
        "arima": pd.concat(all_results["arima"], ignore_index=True),
        "holtwinters": pd.concat(all_results["holtwinters"], ignore_index=True),
        "decomposition": pd.DataFrame(all_results["decomposition"]),
    }

    if save_results:
        for name, df_result in results.items():
            df_result.to_csv(f"output/results_statsmodels_{name}.csv", index=False)
            print(f"Saved results to output/results_statsmodels_{name}.csv")

    return results


# =============================================================================
# DOCUMENTATION AND GOTCHAS
# =============================================================================

STATSMODELS_GOTCHAS = """
=============================================================================
STATSMODELS FORECASTING - GOTCHAS AND RECOMMENDATIONS
=============================================================================

1. ARIMA
--------
Pros:
- Well-established, interpretable model
- Good for stationary time series with autocorrelation
- Can handle trend through differencing

Cons:
- Manual order selection (p, d, q) can be tedious
- Seasonal ARIMA very slow with large seasonal periods
- Requires stationary data

Recommendations:
- Use pmdarima's auto_arima for automatic order selection
- Check stationarity with ADF test first
- For weekly seasonality, use m=7 (manageable)
- For yearly seasonality in daily data (m=365), consider alternatives

Missing Data Handling:
- ARIMA does NOT handle missing data automatically
- Must interpolate or forward-fill before fitting
- Gaps in dates will cause issues

2. HOLT-WINTERS (Exponential Smoothing)
----------------------------------------
Pros:
- Interpretable components (level, trend, season)
- Good for data with clear seasonal patterns
- Faster than ARIMA for most cases

Cons:
- Requires at least 2 seasonal cycles
- Multiplicative models fail with zeros/negatives
- Fixed seasonal period (no irregular seasonality)

Recommendations:
- Use additive model for data with consistent seasonal amplitude
- Use multiplicative when seasonal amplitude grows with level
- Damped trend usually improves long-term forecasts
- Initialize with 'estimated' for best results

Missing Data Handling:
- Does NOT handle missing data
- Requires continuous time series
- Interpolate gaps before fitting

3. SEASONAL DECOMPOSITION
--------------------------
Classical vs STL:
- STL (LOESS) is more robust to outliers
- STL handles irregular seasonality better
- Classical decomposition is simpler, faster

Use Cases:
- Understanding data structure before modeling
- Detrending for stationarity
- Feature engineering for ML models

4. GENERAL OBSERVATIONS
------------------------
Exogenous Variables:
- ARIMA supports exogenous variables (ARIMAX)
- Exponential Smoothing does NOT support exogenous variables
- For sale events, consider:
  * ARIMAX with binary sale indicators
  * Separate modeling of baseline and sale effects
  * Switching to Prophet or ML approaches

Training Time (typical for daily data, 2 years):
- Manual ARIMA: 1-5 seconds
- Auto ARIMA: 10-60 seconds
- Holt-Winters: 0.1-1 second
- STL decomposition: 0.1-0.5 seconds

Best Accuracy Scenarios:
- ARIMA: Complex autocorrelation patterns
- Holt-Winters: Clear trend + regular seasonality
- Neither handles irregular events well (use Prophet or ML)

=============================================================================
"""


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("Statsmodels Forecasting Test Suite")
    print("=" * 60)

    # Generate synthetic data
    print("\nGenerating synthetic game revenue data...")
    df = generate_all_games_data()

    print(f"Data shape: {df.shape}")
    print(f"Games: {df['game_name'].unique().tolist()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    # Run experiments
    print("\n" + "=" * 60)
    print("Running Experiments")
    print("=" * 60)

    results = run_all_statsmodels_experiments(
        df,
        games=None,  # All games
        holdout_periods=[30, 60, 90],
        save_results=True,
    )

    # Summary
    print("\n" + "=" * 60)
    print("ARIMA Results Summary")
    print("=" * 60)
    print(results["arima"].groupby(["game", "holdout_days"])["mape"].mean())

    print("\n" + "=" * 60)
    print("Holt-Winters Results Summary")
    print("=" * 60)
    print(
        results["holtwinters"].groupby(["configuration", "holdout_days"])["mape"].mean()
    )

    print("\n" + "=" * 60)
    print("Decomposition Analysis")
    print("=" * 60)
    print(results["decomposition"])

    # Print gotchas
    print(STATSMODELS_GOTCHAS)
