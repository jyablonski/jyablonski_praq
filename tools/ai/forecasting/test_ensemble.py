"""
Ensemble Forecasting Test Suite

Combines predictions from multiple models using simple average
and weighted average approaches.

Gotchas and Notes:
- Ensembles often outperform individual models
- Diversity of models is key (don't ensemble similar models)
- Weighted averages can be optimized on validation data
- Simple averages are more robust to overfitting
"""

import time
import warnings
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Import individual forecasters
try:
    from statsforecast import StatsForecast
    from statsforecast.models import AutoARIMA, AutoETS, SeasonalNaive

    STATSFORECAST_AVAILABLE = True
except ImportError:
    STATSFORECAST_AVAILABLE = False
    print("Warning: statsforecast not available")

try:
    from prophet import Prophet

    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: prophet not available")

try:
    import lightgbm as lgb

    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("Warning: lightgbm not available")

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("Warning: statsmodels not available")

from base import (
    generate_all_games_data,
    time_series_split,
    evaluate_forecast,
    compare_forecasts,
    prepare_for_prophet,
    prepare_for_statsmodels,
    add_calendar_features,
    add_lag_features,
    add_rolling_features,
    get_default_sale_events,
    SaleEvent,
    plot_forecast_comparison,
    mape,
    rmse,
    smape,
)

warnings.filterwarnings("ignore")


# =============================================================================
# INDIVIDUAL MODEL WRAPPERS
# =============================================================================


class BaseForecaster:
    """Base class for forecasters."""

    def __init__(self, name: str):
        self.name = name
        self.train_time = None

    def fit(self, train_df: pd.DataFrame) -> "BaseForecaster":
        raise NotImplementedError

    def predict(self, n_periods: int) -> np.ndarray:
        raise NotImplementedError


class SeasonalNaiveForecaster(BaseForecaster):
    """Simple seasonal naive baseline (last week's values)."""

    def __init__(self, season_length: int = 7):
        super().__init__("SeasonalNaive")
        self.season_length = season_length
        self.last_season = None

    def fit(self, train_df: pd.DataFrame) -> "SeasonalNaiveForecaster":
        start = time.time()
        self.last_season = train_df["revenue"].values[-self.season_length :]
        self.train_time = time.time() - start
        return self

    def predict(self, n_periods: int) -> np.ndarray:
        predictions = []
        for i in range(n_periods):
            idx = i % self.season_length
            predictions.append(self.last_season[idx])
        return np.array(predictions)


class HoltWintersForecaster(BaseForecaster):
    """Holt-Winters exponential smoothing."""

    def __init__(self, seasonal_periods: int = 7):
        super().__init__("HoltWinters")
        self.seasonal_periods = seasonal_periods
        self.model = None

    def fit(self, train_df: pd.DataFrame) -> "HoltWintersForecaster":
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")

        start = time.time()
        series = prepare_for_statsmodels(train_df)

        self.model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal="add",
            seasonal_periods=self.seasonal_periods,
            damped_trend=True,
        ).fit()

        self.train_time = time.time() - start
        return self

    def predict(self, n_periods: int) -> np.ndarray:
        return self.model.forecast(n_periods)


class StatsForecastForecaster(BaseForecaster):
    """StatsForecast AutoARIMA or AutoETS."""

    def __init__(self, model_type: str = "AutoARIMA", season_length: int = 7):
        super().__init__(f"SF_{model_type}")
        self.model_type = model_type
        self.season_length = season_length
        self.sf = None
        self.train_data = None

    def fit(self, train_df: pd.DataFrame) -> "StatsForecastForecaster":
        if not STATSFORECAST_AVAILABLE:
            raise ImportError("statsforecast not available")

        start = time.time()

        # Prepare data
        self.train_data = pd.DataFrame(
            {"unique_id": "game", "ds": train_df["date"], "y": train_df["revenue"]}
        )

        # Select model
        if self.model_type == "AutoARIMA":
            models = [AutoARIMA(season_length=self.season_length)]
        elif self.model_type == "AutoETS":
            models = [AutoETS(season_length=self.season_length)]
        else:
            models = [SeasonalNaive(season_length=self.season_length)]

        self.sf = StatsForecast(models=models, freq="D", n_jobs=1)

        self.train_time = time.time() - start
        return self

    def predict(self, n_periods: int) -> np.ndarray:
        forecast = self.sf.forecast(df=self.train_data, h=n_periods)
        # Get first (and only) model column
        model_col = [c for c in forecast.columns if c not in ["unique_id", "ds"]][0]
        return forecast[model_col].values


class ProphetForecaster(BaseForecaster):
    """Facebook Prophet forecaster."""

    def __init__(self, with_sales: bool = False, sale_events: List = None):
        name = "Prophet_Sales" if with_sales else "Prophet"
        super().__init__(name)
        self.with_sales = with_sales
        self.sale_events = sale_events
        self.model = None

    def fit(self, train_df: pd.DataFrame) -> "ProphetForecaster":
        if not PROPHET_AVAILABLE:
            raise ImportError("prophet not available")

        start = time.time()

        # Prepare holidays if using sales
        holidays_df = None
        if self.with_sales and self.sale_events:
            events_data = []
            for event in self.sale_events:
                dates = pd.date_range(event.start_date, event.end_date)
                for date in dates:
                    events_data.append(
                        {
                            "holiday": event.name,
                            "ds": date,
                            "lower_window": 0,
                            "upper_window": 0,
                        }
                    )
            holidays_df = pd.DataFrame(events_data)

        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            holidays=holidays_df,
        )

        prophet_df = prepare_for_prophet(train_df)
        self.model.fit(prophet_df)

        self.train_time = time.time() - start
        return self

    def predict(self, n_periods: int) -> np.ndarray:
        future = self.model.make_future_dataframe(periods=n_periods)
        forecast = self.model.predict(future)
        return forecast["yhat"].values[-n_periods:]


class LightGBMForecaster(BaseForecaster):
    """LightGBM with feature engineering."""

    def __init__(self, sale_events: List = None):
        super().__init__("LightGBM")
        self.sale_events = sale_events
        self.model = None
        self.feature_cols = None
        self.last_train_df = None

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for LightGBM."""
        df = df.copy()
        df = add_calendar_features(df, "date")
        df = add_lag_features(df, "revenue", [1, 7, 14, 28])
        df = add_rolling_features(df, "revenue", [7, 14, 28])

        if self.sale_events:
            df["is_sale"] = 0
            for event in self.sale_events:
                start = pd.to_datetime(event.start_date)
                end = pd.to_datetime(event.end_date)
                mask = (df["date"] >= start) & (df["date"] <= end)
                df.loc[mask, "is_sale"] = 1

        return df

    def fit(self, train_df: pd.DataFrame) -> "LightGBMForecaster":
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("lightgbm not available")

        start = time.time()

        # Create features
        df = self._create_features(train_df)
        df = df.dropna(subset=["revenue_lag_7"])

        # Define features
        exclude = ["date", "revenue", "game_name", "day_name", "sale_name"]
        self.feature_cols = [c for c in df.columns if c not in exclude]

        X = df[self.feature_cols]
        y = df["revenue"]

        # Train
        train_data = lgb.Dataset(X, label=y)

        params = {
            "objective": "regression",
            "metric": "mape",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.8,
            "verbosity": -1,
        }

        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            callbacks=[lgb.log_evaluation(period=0)],
        )

        self.last_train_df = train_df.copy()
        self.train_time = time.time() - start
        return self

    def predict(self, n_periods: int) -> np.ndarray:
        """Recursive prediction."""
        predictions = []
        history = self.last_train_df.copy()
        last_date = history["date"].max()

        for i in range(n_periods):
            next_date = last_date + pd.Timedelta(days=i + 1)

            # Create new row
            new_row = pd.DataFrame(
                {
                    "date": [next_date],
                    "revenue": [np.nan],
                    "game_name": [history["game_name"].iloc[0]],
                }
            )

            # Combine and create features
            combined = pd.concat([history, new_row], ignore_index=True)
            combined = self._create_features(combined)

            # Predict
            X_new = combined[combined["date"] == next_date][self.feature_cols].fillna(0)
            pred = max(0, self.model.predict(X_new)[0])
            predictions.append(pred)

            # Update history
            new_row["revenue"] = pred
            history = pd.concat([history, new_row], ignore_index=True)

        return np.array(predictions)


# =============================================================================
# ENSEMBLE METHODS
# =============================================================================


class SimpleAverageEnsemble:
    """
    Simple average of multiple forecasters.

    Most robust approach, doesn't overfit to validation data.
    """

    def __init__(self, forecasters: List[BaseForecaster]):
        self.forecasters = forecasters
        self.name = "SimpleAverage"
        self.train_time = None

    def fit(self, train_df: pd.DataFrame) -> "SimpleAverageEnsemble":
        """Fit all component forecasters."""
        start = time.time()

        for forecaster in self.forecasters:
            try:
                forecaster.fit(train_df)
            except Exception as e:
                print(f"  Warning: {forecaster.name} failed to fit: {e}")

        self.train_time = time.time() - start
        return self

    def predict(self, n_periods: int) -> np.ndarray:
        """Average predictions from all forecasters."""
        all_predictions = []

        for forecaster in self.forecasters:
            try:
                preds = forecaster.predict(n_periods)
                all_predictions.append(preds)
            except Exception as e:
                print(f"  Warning: {forecaster.name} failed to predict: {e}")

        if not all_predictions:
            raise ValueError("No forecasters produced predictions")

        return np.mean(all_predictions, axis=0)

    def get_individual_predictions(self, n_periods: int) -> Dict[str, np.ndarray]:
        """Get predictions from each component."""
        predictions = {}

        for forecaster in self.forecasters:
            try:
                predictions[forecaster.name] = forecaster.predict(n_periods)
            except Exception:
                pass

        return predictions


class WeightedAverageEnsemble:
    """
    Weighted average of multiple forecasters.

    Weights can be:
    - Specified manually
    - Optimized on validation data
    - Based on inverse error
    """

    def __init__(
        self, forecasters: List[BaseForecaster], weights: Optional[List[float]] = None
    ):
        self.forecasters = forecasters
        self.weights = weights
        self.name = "WeightedAverage"
        self.train_time = None
        self.optimized_weights = None

    def fit(self, train_df: pd.DataFrame) -> "WeightedAverageEnsemble":
        """Fit all component forecasters."""
        start = time.time()

        for forecaster in self.forecasters:
            try:
                forecaster.fit(train_df)
            except Exception as e:
                print(f"  Warning: {forecaster.name} failed to fit: {e}")

        self.train_time = time.time() - start
        return self

    def optimize_weights(self, val_df: pd.DataFrame, y_true: np.ndarray) -> np.ndarray:
        """
        Optimize weights to minimize MAPE on validation data.

        Uses constrained optimization where weights sum to 1
        and are non-negative.
        """
        n_forecasters = len(self.forecasters)
        n_periods = len(y_true)

        # Get individual predictions
        predictions = []
        valid_idx = []

        for i, forecaster in enumerate(self.forecasters):
            try:
                preds = forecaster.predict(n_periods)
                predictions.append(preds)
                valid_idx.append(i)
            except Exception:
                pass

        if not predictions:
            return np.array([1.0 / n_forecasters] * n_forecasters)

        predictions = np.array(predictions)  # shape: (n_models, n_periods)

        def objective(weights):
            """Minimize MAPE."""
            weighted_pred = np.sum(weights[:, np.newaxis] * predictions, axis=0)
            return mape(y_true, weighted_pred)

        # Constraints: weights sum to 1
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}

        # Bounds: weights between 0 and 1
        bounds = [(0, 1) for _ in range(len(predictions))]

        # Initial guess: equal weights
        x0 = np.array([1.0 / len(predictions)] * len(predictions))

        # Optimize
        result = minimize(
            objective, x0, method="SLSQP", bounds=bounds, constraints=constraints
        )

        # Map back to full weight vector
        full_weights = np.zeros(n_forecasters)
        for i, idx in enumerate(valid_idx):
            full_weights[idx] = result.x[i]

        self.optimized_weights = full_weights
        return full_weights

    def predict(self, n_periods: int) -> np.ndarray:
        """Weighted average of predictions."""
        weights = self.weights or self.optimized_weights

        if weights is None:
            # Fall back to equal weights
            weights = [1.0 / len(self.forecasters)] * len(self.forecasters)

        all_predictions = []
        all_weights = []

        for forecaster, weight in zip(self.forecasters, weights):
            if weight > 0:
                try:
                    preds = forecaster.predict(n_periods)
                    all_predictions.append(preds)
                    all_weights.append(weight)
                except Exception:
                    pass

        if not all_predictions:
            raise ValueError("No forecasters produced predictions")

        # Normalize weights
        all_weights = np.array(all_weights)
        all_weights = all_weights / all_weights.sum()

        # Weighted average
        weighted_sum = np.zeros(n_periods)
        for preds, weight in zip(all_predictions, all_weights):
            weighted_sum += weight * preds

        return weighted_sum


class InverseErrorEnsemble:
    """
    Ensemble where weights are proportional to inverse error.

    Models with lower MAPE get higher weights automatically.
    """

    def __init__(self, forecasters: List[BaseForecaster]):
        self.forecasters = forecasters
        self.name = "InverseError"
        self.train_time = None
        self.weights = None

    def fit(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame] = None,
        val_days: int = 30,
    ) -> "InverseErrorEnsemble":
        """
        Fit forecasters and calculate weights based on validation error.

        If val_df is not provided, uses last val_days of train_df.
        """
        start = time.time()

        if val_df is None:
            # Create validation split
            cutoff = train_df["date"].max() - pd.Timedelta(days=val_days)
            actual_train = train_df[train_df["date"] <= cutoff].copy()
            val_df = train_df[train_df["date"] > cutoff].copy()
        else:
            actual_train = train_df.copy()

        # Fit each forecaster on actual_train
        errors = []

        for forecaster in self.forecasters:
            try:
                forecaster.fit(actual_train)
                preds = forecaster.predict(len(val_df))
                error = mape(val_df["revenue"].values, preds)
                errors.append(error)
            except Exception as e:
                print(f"  Warning: {forecaster.name} failed: {e}")
                errors.append(np.inf)

        # Calculate inverse error weights
        errors = np.array(errors)
        valid_mask = errors < np.inf

        if not valid_mask.any():
            self.weights = np.ones(len(self.forecasters)) / len(self.forecasters)
        else:
            # Add small epsilon to avoid division by zero
            inv_errors = 1.0 / (errors + 0.01)
            inv_errors[~valid_mask] = 0
            self.weights = inv_errors / inv_errors.sum()

        # Re-fit on full training data
        for forecaster in self.forecasters:
            try:
                forecaster.fit(train_df)
            except Exception:
                pass

        self.train_time = time.time() - start
        return self

    def predict(self, n_periods: int) -> np.ndarray:
        """Weighted average using inverse error weights."""
        all_predictions = []
        all_weights = []

        for forecaster, weight in zip(self.forecasters, self.weights):
            if weight > 0:
                try:
                    preds = forecaster.predict(n_periods)
                    all_predictions.append(preds)
                    all_weights.append(weight)
                except Exception:
                    pass

        if not all_predictions:
            raise ValueError("No forecasters produced predictions")

        # Normalize weights
        all_weights = np.array(all_weights)
        all_weights = all_weights / all_weights.sum()

        weighted_sum = np.zeros(n_periods)
        for preds, weight in zip(all_predictions, all_weights):
            weighted_sum += weight * preds

        return weighted_sum


# =============================================================================
# EXPERIMENTS
# =============================================================================


def get_available_forecasters(
    sale_events: List[SaleEvent] = None,
) -> List[BaseForecaster]:
    """Get list of available forecasters based on installed packages."""
    forecasters = [
        SeasonalNaiveForecaster(season_length=7),
    ]

    if STATSMODELS_AVAILABLE:
        forecasters.append(HoltWintersForecaster(seasonal_periods=7))

    if STATSFORECAST_AVAILABLE:
        forecasters.append(StatsForecastForecaster("AutoARIMA", season_length=7))
        forecasters.append(StatsForecastForecaster("AutoETS", season_length=7))

    if PROPHET_AVAILABLE:
        forecasters.append(ProphetForecaster(with_sales=False))
        if sale_events:
            forecasters.append(
                ProphetForecaster(with_sales=True, sale_events=sale_events)
            )

    if LIGHTGBM_AVAILABLE:
        forecasters.append(LightGBMForecaster(sale_events=sale_events))

    return forecasters


def run_ensemble_experiment(
    df: pd.DataFrame,
    game_name: str,
    holdout_periods: List[int] = [30, 60, 90],
    sale_events: Optional[List[SaleEvent]] = None,
) -> pd.DataFrame:
    """
    Run ensemble experiments for a specific game.

    Compares:
    - Individual models
    - Simple average ensemble
    - Weighted average ensemble
    - Inverse error ensemble
    """
    if sale_events is None:
        sale_events = get_default_sale_events()

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    results = []

    for period in holdout_periods:
        print(f"\n  {period}-day holdout:")

        train, test = time_series_split(game_df, period)
        y_true = test["revenue"].values

        # Get forecasters
        forecasters = get_available_forecasters(sale_events)

        print(f"    Testing {len(forecasters)} individual models + ensembles")

        # Individual model results
        individual_preds = {}

        for forecaster in forecasters:
            try:
                start = time.time()
                forecaster.fit(train)
                preds = forecaster.predict(len(test))
                train_time = time.time() - start

                metrics = evaluate_forecast(y_true, preds, forecaster.name)
                metrics["holdout_days"] = period
                metrics["train_time_sec"] = train_time
                metrics["game"] = game_name
                metrics["model_type"] = "individual"

                results.append(metrics)
                individual_preds[forecaster.name] = preds

                print(f"      {forecaster.name}: MAPE = {metrics['mape']:.2f}%")

            except Exception as e:
                print(f"      {forecaster.name}: FAILED - {str(e)[:50]}")

        # Simple Average Ensemble
        if len(individual_preds) >= 2:
            print("    --- Ensembles ---")

            # Simple average
            try:
                forecasters_fresh = get_available_forecasters(sale_events)
                simple_ensemble = SimpleAverageEnsemble(forecasters_fresh)

                start = time.time()
                simple_ensemble.fit(train)
                preds = simple_ensemble.predict(len(test))
                train_time = time.time() - start

                metrics = evaluate_forecast(y_true, preds, "SimpleAverage")
                metrics["holdout_days"] = period
                metrics["train_time_sec"] = train_time
                metrics["game"] = game_name
                metrics["model_type"] = "ensemble"

                results.append(metrics)
                print(f"      SimpleAverage: MAPE = {metrics['mape']:.2f}%")

            except Exception as e:
                print(f"      SimpleAverage: FAILED - {str(e)[:50]}")

            # Weighted average (optimized)
            try:
                forecasters_fresh = get_available_forecasters(sale_events)
                weighted_ensemble = WeightedAverageEnsemble(forecasters_fresh)

                # Use internal validation split
                val_days = min(30, len(train) // 5)
                val_cutoff = train["date"].max() - pd.Timedelta(days=val_days)
                train_for_opt = train[train["date"] <= val_cutoff]
                val_for_opt = train[train["date"] > val_cutoff]

                start = time.time()
                weighted_ensemble.fit(train_for_opt)
                weighted_ensemble.optimize_weights(
                    val_for_opt, val_for_opt["revenue"].values
                )

                # Refit on full training data
                weighted_ensemble.fit(train)
                preds = weighted_ensemble.predict(len(test))
                train_time = time.time() - start

                metrics = evaluate_forecast(y_true, preds, "WeightedAverage")
                metrics["holdout_days"] = period
                metrics["train_time_sec"] = train_time
                metrics["game"] = game_name
                metrics["model_type"] = "ensemble"

                # Add weight info
                if weighted_ensemble.optimized_weights is not None:
                    weight_str = ", ".join(
                        [
                            f"{f.name}:{w:.2f}"
                            for f, w in zip(
                                forecasters_fresh, weighted_ensemble.optimized_weights
                            )
                            if w > 0.01
                        ]
                    )
                    metrics["weights"] = weight_str

                results.append(metrics)
                print(f"      WeightedAverage: MAPE = {metrics['mape']:.2f}%")

            except Exception as e:
                print(f"      WeightedAverage: FAILED - {str(e)[:50]}")

            # Inverse Error Ensemble
            try:
                forecasters_fresh = get_available_forecasters(sale_events)
                inverse_ensemble = InverseErrorEnsemble(forecasters_fresh)

                start = time.time()
                inverse_ensemble.fit(train, val_days=30)
                preds = inverse_ensemble.predict(len(test))
                train_time = time.time() - start

                metrics = evaluate_forecast(y_true, preds, "InverseError")
                metrics["holdout_days"] = period
                metrics["train_time_sec"] = train_time
                metrics["game"] = game_name
                metrics["model_type"] = "ensemble"

                results.append(metrics)
                print(f"      InverseError: MAPE = {metrics['mape']:.2f}%")

            except Exception as e:
                print(f"      InverseError: FAILED - {str(e)[:50]}")

    return pd.DataFrame(results)


def run_all_ensemble_experiments(
    df: pd.DataFrame,
    games: Optional[List[str]] = None,
    holdout_periods: List[int] = [30, 60, 90],
    sale_events: Optional[List[SaleEvent]] = None,
    save_results: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Run all ensemble experiments.
    """
    if games is None:
        games = df["game_name"].unique().tolist()
    if sale_events is None:
        sale_events = get_default_sale_events()

    all_results = []

    for game in games:
        print(f"\n{'=' * 60}")
        print(f"Processing: {game}")
        print("=" * 60)

        results = run_ensemble_experiment(df, game, holdout_periods, sale_events)
        all_results.append(results)

    final_results = pd.concat(all_results, ignore_index=True)

    if save_results:
        final_results.to_csv("output/results_ensemble.csv", index=False)
        print("\nResults saved to output/results_ensemble.csv")

    return {"main_results": final_results}


# =============================================================================
# DOCUMENTATION AND GOTCHAS
# =============================================================================

ENSEMBLE_GOTCHAS = """
=============================================================================
ENSEMBLE FORECASTING - GOTCHAS AND RECOMMENDATIONS
=============================================================================

1. WHY ENSEMBLES WORK
---------------------
Benefits:
- Reduce variance by averaging out individual model errors
- More robust to different data patterns
- Often outperform best individual model

Key insight:
- Diversity is more important than individual accuracy
- Models with different biases complement each other
- Correlated errors cancel less effectively

2. SIMPLE VS WEIGHTED AVERAGE
------------------------------
Simple Average:
- Most robust, doesn't overfit
- Works well when models have similar accuracy
- Recommended default approach

Weighted Average:
- Can improve if model quality varies
- Risk of overfitting to validation data
- Requires careful cross-validation

Inverse Error:
- Automatic weight assignment
- Based on validation performance
- Good balance of simplicity and adaptation

3. MODEL SELECTION FOR ENSEMBLES
---------------------------------
Good combinations:
- Statistical (ARIMA/ETS) + ML (LightGBM)
- Different seasonal models (Prophet + HW)
- Baseline + sophisticated models

Avoid:
- Multiple similar models (e.g., 3 ARIMA variants)
- Models that always fail on your data type
- Too many models (diminishing returns >5-7)

4. IMPLEMENTATION CONSIDERATIONS
---------------------------------
Training time:
- Increases linearly with number of models
- Consider parallel fitting for speed
- LightGBM often slowest due to feature engineering

Prediction time:
- Also linear in number of models
- Recursive predictions are slowest
- Cache intermediate results if possible

5. WHEN TO USE ENSEMBLES
-------------------------
Good scenarios:
- Production systems requiring reliability
- Uncertain which model type will work best
- Sufficient computational resources

Bad scenarios:
- Prototyping/exploration
- Very limited compute budget
- Need for model interpretability

6. WEIGHT OPTIMIZATION GOTCHAS
-------------------------------
Overfitting risk:
- Validation set must be representative
- Use time-based validation, not random
- Consider walk-forward optimization

Numerical issues:
- Constrained optimization can fail
- Initialize with equal weights
- Use regularization if needed

7. PRACTICAL TIPS
-----------------
1. Start with simple average as baseline
2. Add weighted average if significant improvement
3. Monitor individual model performance over time
4. Re-calibrate weights periodically
5. Track model contributions to final forecast

8. COMMON PATTERNS
------------------
For game revenue:
- Prophet handles seasonality well
- LightGBM captures sale effects
- Statistical models provide stability

Typical weights (after optimization):
- LightGBM: 30-40% (good with events)
- Prophet: 20-30% (good seasonality)
- Statistical: 20-30% (stable baseline)
- Naive: 10-20% (regularization)

=============================================================================
"""


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("Ensemble Forecasting Test Suite")
    print("=" * 60)

    # Check available libraries
    print("\nAvailable libraries:")
    print(f"  statsforecast: {STATSFORECAST_AVAILABLE}")
    print(f"  prophet: {PROPHET_AVAILABLE}")
    print(f"  lightgbm: {LIGHTGBM_AVAILABLE}")
    print(f"  statsmodels: {STATSMODELS_AVAILABLE}")

    # Generate synthetic data
    print("\nGenerating synthetic game revenue data...")
    df = generate_all_games_data()

    print(f"Data shape: {df.shape}")
    print(f"Games: {df['game_name'].unique().tolist()}")

    # Run experiments
    print("\n" + "=" * 60)
    print("Running Ensemble Experiments")
    print("=" * 60)

    results = run_all_ensemble_experiments(
        df,
        games=None,  # All games
        holdout_periods=[30, 60, 90],
        save_results=True,
    )

    # Summary
    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)

    summary = (
        results["main_results"]
        .groupby(["model_type", "name"])["mape"]
        .agg(["mean", "std", "min", "max"])
    )
    print(summary.sort_values("mean"))

    print("\n" + "=" * 60)
    print("Ensemble vs Best Individual (30-day holdout)")
    print("=" * 60)

    holdout_30 = results["main_results"][results["main_results"]["holdout_days"] == 30]

    for game in holdout_30["game"].unique():
        game_results = holdout_30[holdout_30["game"] == game]

        individual = game_results[game_results["model_type"] == "individual"]
        ensemble = game_results[game_results["model_type"] == "ensemble"]

        if len(individual) > 0 and len(ensemble) > 0:
            best_individual = individual.loc[individual["mape"].idxmin()]
            best_ensemble = ensemble.loc[ensemble["mape"].idxmin()]

            improvement = best_individual["mape"] - best_ensemble["mape"]

            print(f"\n{game}:")
            print(
                f"  Best Individual: {best_individual['name']} = {best_individual['mape']:.2f}%"
            )
            print(
                f"  Best Ensemble:   {best_ensemble['name']} = {best_ensemble['mape']:.2f}%"
            )
            print(f"  Improvement:     {improvement:+.2f} percentage points")

    # Print gotchas
    print(ENSEMBLE_GOTCHAS)
