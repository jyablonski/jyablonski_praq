"""
Facebook Prophet Forecasting Test Suite

Tests baseline Prophet and Prophet with sale events as regressors
for game revenue forecasting.

Gotchas and Notes:
- Prophet is designed for business time series with strong seasonality
- Handles missing data and outliers well
- Easy to add custom regressors (sale events, holidays)
- Can be slow with many regressors or long time series
- Default parameters often work well but can be tuned
"""

import time
import warnings
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

from base import (
    generate_all_games_data,
    time_series_split,
    create_holdout_splits,
    evaluate_forecast,
    compare_forecasts,
    prepare_for_prophet,
    plot_forecast_comparison,
    plot_train_test_split,
    get_default_sale_events,
    SaleEvent,
    mape,
    rmse,
    smape,
)

warnings.filterwarnings("ignore")


# =============================================================================
# PROPHET CONFIGURATION
# =============================================================================


@dataclass
class ProphetConfig:
    """Configuration for Prophet model."""

    name: str
    growth: str = "linear"  # 'linear' or 'logistic'
    yearly_seasonality: bool = True
    weekly_seasonality: bool = True
    daily_seasonality: bool = False
    seasonality_mode: str = "additive"  # 'additive' or 'multiplicative'
    changepoint_prior_scale: float = 0.05
    seasonality_prior_scale: float = 10.0
    holidays_prior_scale: float = 10.0
    interval_width: float = 0.80
    add_sale_events: bool = False


def get_prophet_configs() -> List[ProphetConfig]:
    """Get a list of Prophet configurations to test."""
    return [
        ProphetConfig(
            name="Prophet-Baseline",
            growth="linear",
            yearly_seasonality=True,
            weekly_seasonality=True,
            seasonality_mode="additive",
        ),
        ProphetConfig(
            name="Prophet-Multiplicative",
            growth="linear",
            yearly_seasonality=True,
            weekly_seasonality=True,
            seasonality_mode="multiplicative",
        ),
        ProphetConfig(
            name="Prophet-HighChangepoints",
            growth="linear",
            yearly_seasonality=True,
            weekly_seasonality=True,
            seasonality_mode="additive",
            changepoint_prior_scale=0.15,  # More flexible trend
        ),
        ProphetConfig(
            name="Prophet-WithSales",
            growth="linear",
            yearly_seasonality=True,
            weekly_seasonality=True,
            seasonality_mode="multiplicative",
            add_sale_events=True,
        ),
        ProphetConfig(
            name="Prophet-HighSalesWeight",
            growth="linear",
            yearly_seasonality=True,
            weekly_seasonality=True,
            seasonality_mode="multiplicative",
            add_sale_events=True,
            holidays_prior_scale=15.0,  # Higher weight on sale events
        ),
    ]


# =============================================================================
# SALE EVENTS HANDLING
# =============================================================================


def create_sale_events_df(sale_events: List[SaleEvent]) -> pd.DataFrame:
    """
    Convert sale events to Prophet holidays format.

    Prophet expects a DataFrame with columns:
    - holiday: name of the holiday/event
    - ds: date
    - lower_window: days before to include
    - upper_window: days after to include
    """
    events_data = []

    for event in sale_events:
        start = pd.to_datetime(event.start_date)
        end = pd.to_datetime(event.end_date)

        # Add each day of the sale as a separate entry
        dates = pd.date_range(start=start, end=end, freq="D")

        for date in dates:
            events_data.append(
                {
                    "holiday": event.name,
                    "ds": date,
                    "lower_window": 0,
                    "upper_window": 0,
                }
            )

    return pd.DataFrame(events_data)


def add_sale_regressors(
    model: Prophet, train_df: pd.DataFrame, sale_events: List[SaleEvent]
) -> Tuple[Prophet, pd.DataFrame]:
    """
    Add sale event flags as regressors to Prophet model.

    This approach gives more control than using holidays,
    allowing the model to learn the sale effect magnitude.
    """
    # Create sale event flags
    df = train_df.copy()
    df["is_sale"] = 0
    df["sale_intensity"] = 0.0  # Can vary by sale magnitude

    for event in sale_events:
        start = pd.to_datetime(event.start_date)
        end = pd.to_datetime(event.end_date)

        mask = (df["ds"] >= start) & (df["ds"] <= end)
        df.loc[mask, "is_sale"] = 1
        df.loc[mask, "sale_intensity"] = event.revenue_multiplier - 1

    # Add regressors to model
    model.add_regressor("is_sale", mode="multiplicative")

    return model, df


# =============================================================================
# PROPHET FORECASTER
# =============================================================================


class ProphetForecaster:
    """
    Prophet forecaster with configurable options.

    Gotchas:
    - Prophet requires columns named 'ds' and 'y'
    - Missing dates are handled automatically
    - Uses Stan for optimization (can be slow)
    - Trend changepoints are detected automatically
    """

    def __init__(
        self, config: ProphetConfig, sale_events: Optional[List[SaleEvent]] = None
    ):
        self.config = config
        self.sale_events = sale_events
        self.model = None
        self.train_time = None
        self.train_df = None

    def _build_model(self) -> Prophet:
        """Build Prophet model from config."""
        holidays_df = None

        if self.config.add_sale_events and self.sale_events:
            holidays_df = create_sale_events_df(self.sale_events)

        model = Prophet(
            growth=self.config.growth,
            yearly_seasonality=self.config.yearly_seasonality,
            weekly_seasonality=self.config.weekly_seasonality,
            daily_seasonality=self.config.daily_seasonality,
            seasonality_mode=self.config.seasonality_mode,
            changepoint_prior_scale=self.config.changepoint_prior_scale,
            seasonality_prior_scale=self.config.seasonality_prior_scale,
            holidays_prior_scale=self.config.holidays_prior_scale,
            interval_width=self.config.interval_width,
            holidays=holidays_df,
        )

        return model

    def fit(self, df: pd.DataFrame) -> "ProphetForecaster":
        """
        Fit the Prophet model.

        Parameters
        ----------
        df : pd.DataFrame
            Data with 'ds' and 'y' columns (use prepare_for_prophet)
        """
        start_time = time.time()

        self.model = self._build_model()
        self.train_df = df.copy()

        # Suppress Stan output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model.fit(df)

        self.train_time = time.time() - start_time
        return self

    def predict(self, periods: int, include_history: bool = False) -> pd.DataFrame:
        """
        Generate forecasts.

        Parameters
        ----------
        periods : int
            Number of periods to forecast
        include_history : bool
            Whether to include historical fitted values

        Returns
        -------
        pd.DataFrame
            Forecast DataFrame with columns: ds, yhat, yhat_lower, yhat_upper
        """
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods)

        # Add regressor values for future dates if needed
        if self.config.add_sale_events and self.sale_events:
            future["is_sale"] = 0
            for event in self.sale_events:
                start = pd.to_datetime(event.start_date)
                end = pd.to_datetime(event.end_date)
                mask = (future["ds"] >= start) & (future["ds"] <= end)
                future.loc[mask, "is_sale"] = 1

        forecast = self.model.predict(future)

        if not include_history:
            # Return only future predictions
            cutoff = self.train_df["ds"].max()
            forecast = forecast[forecast["ds"] > cutoff]

        return forecast

    def plot_components(self) -> plt.Figure:
        """Plot forecast components (trend, weekly, yearly)."""
        future = self.model.make_future_dataframe(periods=30)
        forecast = self.model.predict(future)
        return self.model.plot_components(forecast)

    def cross_validate(
        self,
        initial: str = "365 days",
        period: str = "30 days",
        horizon: str = "30 days",
    ) -> pd.DataFrame:
        """
        Perform Prophet's built-in cross-validation.

        Parameters
        ----------
        initial : str
            Initial training period
        period : str
            Spacing between cutoff dates
        horizon : str
            Forecast horizon

        Returns
        -------
        pd.DataFrame
            Cross-validation results
        """
        df_cv = cross_validation(
            self.model, initial=initial, period=period, horizon=horizon
        )
        return df_cv

    def get_performance_metrics(self, cv_results: pd.DataFrame) -> pd.DataFrame:
        """Calculate performance metrics from cross-validation results."""
        return performance_metrics(cv_results)


def run_prophet_experiment(
    df: pd.DataFrame,
    game_name: str,
    holdout_periods: List[int] = [30, 60, 90],
    configs: Optional[List[ProphetConfig]] = None,
    sale_events: Optional[List[SaleEvent]] = None,
) -> pd.DataFrame:
    """
    Run Prophet experiments for a specific game.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    game_name : str
        Name of the game
    holdout_periods : list
        Holdout periods to test
    configs : list
        Prophet configurations to test
    sale_events : list
        Sale events for regressor models

    Returns
    -------
    pd.DataFrame
        Results for all configurations and holdout periods
    """
    if configs is None:
        configs = get_prophet_configs()
    if sale_events is None:
        sale_events = get_default_sale_events()

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    results = []

    for period in holdout_periods:
        train, test = time_series_split(game_df, period)

        # Prepare for Prophet
        train_prophet = prepare_for_prophet(train)

        for config in configs:
            print(f"  Testing {config.name}...", end=" ")

            try:
                forecaster = ProphetForecaster(
                    config=config,
                    sale_events=sale_events if config.add_sale_events else None,
                )
                forecaster.fit(train_prophet)

                # Predict
                forecast = forecaster.predict(periods=len(test))
                predictions = forecast["yhat"].values

                # Evaluate
                metrics = evaluate_forecast(
                    test["revenue"].values, predictions, config.name
                )
                metrics["holdout_days"] = period
                metrics["train_time_sec"] = forecaster.train_time
                metrics["configuration"] = config.name
                metrics["game"] = game_name
                metrics["seasonality_mode"] = config.seasonality_mode
                metrics["has_sale_events"] = config.add_sale_events

                print(f"MAPE: {metrics['mape']:.2f}%")

            except Exception as e:
                print(f"ERROR: {str(e)[:50]}")
                metrics = {
                    "name": config.name,
                    "mape": np.nan,
                    "rmse": np.nan,
                    "smape": np.nan,
                    "mae": np.nan,
                    "holdout_days": period,
                    "train_time_sec": np.nan,
                    "configuration": config.name,
                    "game": game_name,
                    "error": str(e),
                }

            results.append(metrics)

    return pd.DataFrame(results)


def run_prophet_with_custom_seasonality(
    df: pd.DataFrame, game_name: str, test_days: int = 30
) -> Dict:
    """
    Demo: Prophet with custom seasonality components.

    Useful for capturing game-specific patterns like:
    - Bi-weekly content drops
    - Monthly events
    - Custom holiday calendars
    """
    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")
    train, test = time_series_split(game_df, test_days)

    train_prophet = prepare_for_prophet(train)

    # Build custom model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
    )

    # Add custom bi-weekly seasonality (for content drops)
    model.add_seasonality(name="biweekly", period=14, fourier_order=3)

    # Add monthly seasonality
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

    # Fit
    start = time.time()
    model.fit(train_prophet)
    train_time = time.time() - start

    # Predict
    future = model.make_future_dataframe(periods=test_days)
    forecast = model.predict(future)

    predictions = forecast[forecast["ds"] > train["date"].max()]["yhat"].values

    metrics = evaluate_forecast(test["revenue"].values, predictions, "Prophet-Custom")
    metrics["train_time_sec"] = train_time

    return {"model": model, "forecast": forecast, "metrics": metrics}


# =============================================================================
# COMPARISON: WITH VS WITHOUT SALE EVENTS
# =============================================================================


def compare_sale_event_impact(
    df: pd.DataFrame,
    game_name: str,
    holdout_days: int = 30,
    sale_events: Optional[List[SaleEvent]] = None,
) -> Dict:
    """
    Compare Prophet performance with and without sale events.

    This demonstrates the value of including domain knowledge
    about promotional periods.
    """
    if sale_events is None:
        sale_events = get_default_sale_events()

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")
    train, test = time_series_split(game_df, holdout_days)
    train_prophet = prepare_for_prophet(train)

    results = {}

    # Without sale events
    print("  Training without sale events...")
    config_no_sales = ProphetConfig(name="No-Sales", seasonality_mode="multiplicative")
    forecaster_no_sales = ProphetForecaster(config_no_sales)
    forecaster_no_sales.fit(train_prophet)
    forecast_no_sales = forecaster_no_sales.predict(len(test))

    results["no_sales"] = {
        "predictions": forecast_no_sales["yhat"].values,
        "metrics": evaluate_forecast(
            test["revenue"].values, forecast_no_sales["yhat"].values, "No Sale Events"
        ),
        "train_time": forecaster_no_sales.train_time,
    }

    # With sale events
    print("  Training with sale events...")
    config_with_sales = ProphetConfig(
        name="With-Sales", seasonality_mode="multiplicative", add_sale_events=True
    )
    forecaster_with_sales = ProphetForecaster(config_with_sales, sale_events)
    forecaster_with_sales.fit(train_prophet)
    forecast_with_sales = forecaster_with_sales.predict(len(test))

    results["with_sales"] = {
        "predictions": forecast_with_sales["yhat"].values,
        "metrics": evaluate_forecast(
            test["revenue"].values,
            forecast_with_sales["yhat"].values,
            "With Sale Events",
        ),
        "train_time": forecaster_with_sales.train_time,
    }

    # Calculate improvement
    improvement = (
        results["no_sales"]["metrics"]["mape"]
        - results["with_sales"]["metrics"]["mape"]
    )

    print(f"\n  Results for {game_name}:")
    print(f"    Without sales: MAPE = {results['no_sales']['metrics']['mape']:.2f}%")
    print(f"    With sales:    MAPE = {results['with_sales']['metrics']['mape']:.2f}%")
    print(f"    Improvement:   {improvement:.2f} percentage points")

    results["improvement_pct_points"] = improvement
    results["test_dates"] = test["date"].values
    results["actuals"] = test["revenue"].values

    return results


# =============================================================================
# RUN ALL EXPERIMENTS
# =============================================================================


def run_all_prophet_experiments(
    df: pd.DataFrame,
    games: Optional[List[str]] = None,
    holdout_periods: List[int] = [30, 60, 90],
    sale_events: Optional[List[SaleEvent]] = None,
    save_results: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Run all Prophet experiments.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    games : list
        List of game names to test
    holdout_periods : list
        Holdout periods to evaluate
    sale_events : list
        Sale events for experiments
    save_results : bool
        Whether to save results to CSV

    Returns
    -------
    dict
        Results DataFrames
    """
    if games is None:
        games = df["game_name"].unique().tolist()
    if sale_events is None:
        sale_events = get_default_sale_events()

    all_results = []
    sale_impact_results = []

    for game in games:
        print(f"\n{'=' * 60}")
        print(f"Processing: {game}")
        print("=" * 60)

        # Main experiments
        results = run_prophet_experiment(
            df, game, holdout_periods, sale_events=sale_events
        )
        all_results.append(results)

        # Sale event impact analysis
        print("\n--- Sale Event Impact Analysis ---")
        impact = compare_sale_event_impact(df, game, 30, sale_events)
        sale_impact_results.append(
            {
                "game": game,
                "mape_without_sales": impact["no_sales"]["metrics"]["mape"],
                "mape_with_sales": impact["with_sales"]["metrics"]["mape"],
                "improvement_pct_points": impact["improvement_pct_points"],
            }
        )

    results_df = pd.concat(all_results, ignore_index=True)
    impact_df = pd.DataFrame(sale_impact_results)

    if save_results:
        results_df.to_csv("output/results_prophet.csv", index=False)
        impact_df.to_csv("output/results_prophet_sale_impact.csv", index=False)
        print("\nResults saved to output/results_prophet*.csv")

    return {"main_results": results_df, "sale_impact": impact_df}


# =============================================================================
# DOCUMENTATION AND GOTCHAS
# =============================================================================

PROPHET_GOTCHAS = """
=============================================================================
FACEBOOK PROPHET - GOTCHAS AND RECOMMENDATIONS
=============================================================================

1. DATA REQUIREMENTS
--------------------
Pros:
- Handles missing data automatically (fills gaps)
- Robust to outliers with built-in uncertainty quantification
- Works well with irregular time series

Cons:
- Requires columns named 'ds' and 'y' (use prepare_for_prophet)
- Assumes at least ~1 year of data for yearly seasonality
- Very short series (<60 days) may not have reliable seasonality

2. SEASONALITY MODES
--------------------
Additive:
- Seasonal effect is constant regardless of trend level
- Good for data where seasonal variation is consistent
- Example: +$10K every weekend regardless of baseline

Multiplicative:
- Seasonal effect scales with trend level
- Better for data where seasonal variation grows with level
- Example: +15% every weekend (more when baseline is higher)

Recommendation:
- Start with multiplicative for revenue data
- Additive works better for stable, mature products

3. REGRESSORS VS HOLIDAYS
--------------------------
Holidays (built-in):
- Easier to use for one-time or recurring events
- Less control over the effect magnitude
- Prophet learns the effect from data

Regressors:
- More flexible, allows custom features
- Must provide future values for forecasting
- Good for known future events (planned sales, content drops)

For Sale Events:
- Use holidays for standard sales (Black Friday, etc.)
- Use regressors for custom events or varying intensities
- Multiplicative mode works better for sales

4. TUNING PARAMETERS
---------------------
changepoint_prior_scale (default 0.05):
- Higher = more flexible trend (overfitting risk)
- Lower = smoother trend (underfitting risk)
- Increase for volatile revenue patterns

seasonality_prior_scale (default 10):
- Higher = stronger seasonality
- Lower = weaker seasonality
- Adjust if seasonality seems over/under-estimated

holidays_prior_scale (default 10):
- Controls strength of holiday/event effects
- Increase if sales have strong, known effects
- Decrease if uncertain about event impacts

5. PERFORMANCE
--------------
Training Time:
- Typical: 2-10 seconds for daily data, 2 years
- Slower with many regressors or custom seasonalities
- Cross-validation can be very slow

Speed Tips:
- Reduce n_changepoints if trend is stable
- Use weekly data if daily isn't necessary
- Disable yearly_seasonality if <2 years of data

6. MISSING DATA HANDLING
-------------------------
Prophet handles gaps automatically:
- Missing dates are interpolated
- NaN values in 'y' can be included (prophet will impute)
- Useful for sparse data or new products

Important:
- Provide all dates even if some 'y' values are missing
- Prophet will estimate missing values during fitting

7. COMMON ISSUES
-----------------
Issue: Forecasts are flat
- Check if changepoint_prior_scale is too low
- Verify data has actual trend

Issue: Seasonality looks wrong
- Try switching between additive/multiplicative
- Check if you have enough data for the seasonal period

Issue: Sales events not captured
- Ensure dates in holidays_df match exactly
- Consider multiplicative mode for sales

=============================================================================
"""


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("Prophet Forecasting Test Suite")
    print("=" * 60)

    # Generate synthetic data
    print("\nGenerating synthetic game revenue data...")
    df = generate_all_games_data()

    print(f"Data shape: {df.shape}")
    print(f"Games: {df['game_name'].unique().tolist()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    # Run experiments
    print("\n" + "=" * 60)
    print("Running Prophet Experiments")
    print("=" * 60)

    results = run_all_prophet_experiments(
        df,
        games=None,  # All games
        holdout_periods=[30, 60, 90],
        save_results=True,
    )

    # Summary
    print("\n" + "=" * 60)
    print("Main Results Summary (by Configuration)")
    print("=" * 60)
    print(
        results["main_results"]
        .groupby("configuration")["mape"]
        .agg(["mean", "std", "min", "max"])
    )

    print("\n" + "=" * 60)
    print("Sale Event Impact Summary")
    print("=" * 60)
    print(results["sale_impact"])

    # Best configuration per game
    print("\n" + "=" * 60)
    print("Best Configuration per Game (30-day holdout)")
    print("=" * 60)
    best = results["main_results"][results["main_results"]["holdout_days"] == 30]
    best_idx = best.groupby("game")["mape"].idxmin()
    print(best.loc[best_idx][["game", "configuration", "mape", "train_time_sec"]])

    # Print gotchas
    print(PROPHET_GOTCHAS)
