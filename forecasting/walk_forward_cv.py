"""
Walk-Forward Cross-Validation for Time Series Forecasting

Provides robust metric estimation with confidence intervals by running
multiple train/test splits across the time series.

Key Features:
- Multiple CV strategies (expanding window, rolling window)
- Aggregated metrics with confidence intervals
- Parallel execution support
- Integration with all forecasting methods

Usage:
    from walk_forward_cv import WalkForwardCV, run_cv_comparison

    # Simple usage with forecaster
    cv = WalkForwardCV(n_splits=5, test_size=30)
    results = cv.evaluate(train_df, forecaster_func)

    # Compare multiple methods
    comparison = run_cv_comparison(df, game_name, methods=['holt_winters', 'prophet'])
"""

import time
import warnings
from typing import Dict, List, Tuple, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import pandas as pd
from scipy import stats

from base import (
    generate_all_games_data,
    mape,
    rmse,
    smape,
    mae,
    evaluate_forecast,
    walk_forward_split,
)

warnings.filterwarnings("ignore")


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class CVFoldResult:
    """Results from a single CV fold."""

    fold: int
    train_size: int
    test_size: int
    train_end_date: pd.Timestamp
    test_start_date: pd.Timestamp
    test_end_date: pd.Timestamp
    y_true: np.ndarray
    y_pred: np.ndarray
    mape: float
    rmse: float
    smape: float
    mae: float
    fit_time: float


@dataclass
class CVResult:
    """Aggregated results from walk-forward cross-validation."""

    method: str
    n_splits: int
    test_size: int
    fold_results: List[CVFoldResult]

    # Aggregated metrics (computed lazily)
    _metrics_cache: Dict = field(default_factory=dict, repr=False)

    @property
    def mape_mean(self) -> float:
        return np.mean([f.mape for f in self.fold_results])

    @property
    def mape_std(self) -> float:
        return np.std([f.mape for f in self.fold_results])

    @property
    def mape_ci(self) -> Tuple[float, float]:
        """95% confidence interval for MAPE."""
        mapes = [f.mape for f in self.fold_results]
        return self._compute_ci(mapes)

    @property
    def rmse_mean(self) -> float:
        return np.mean([f.rmse for f in self.fold_results])

    @property
    def rmse_std(self) -> float:
        return np.std([f.rmse for f in self.fold_results])

    @property
    def smape_mean(self) -> float:
        return np.mean([f.smape for f in self.fold_results])

    @property
    def mae_mean(self) -> float:
        return np.mean([f.mae for f in self.fold_results])

    @property
    def total_fit_time(self) -> float:
        return sum(f.fit_time for f in self.fold_results)

    @property
    def avg_fit_time(self) -> float:
        return np.mean([f.fit_time for f in self.fold_results])

    def _compute_ci(
        self, values: List[float], confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Compute confidence interval using t-distribution."""
        n = len(values)
        if n < 2:
            return (values[0], values[0])

        mean = np.mean(values)
        se = stats.sem(values)
        h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
        return (max(0, mean - h), mean + h)

    def summary(self) -> pd.DataFrame:
        """Return summary DataFrame with all metrics."""
        return pd.DataFrame(
            [
                {
                    "method": self.method,
                    "n_splits": self.n_splits,
                    "test_size": self.test_size,
                    "mape_mean": self.mape_mean,
                    "mape_std": self.mape_std,
                    "mape_ci_lower": self.mape_ci[0],
                    "mape_ci_upper": self.mape_ci[1],
                    "rmse_mean": self.rmse_mean,
                    "rmse_std": self.rmse_std,
                    "smape_mean": self.smape_mean,
                    "mae_mean": self.mae_mean,
                    "avg_fit_time": self.avg_fit_time,
                    "total_fit_time": self.total_fit_time,
                }
            ]
        )

    def fold_details(self) -> pd.DataFrame:
        """Return detailed DataFrame with all fold results."""
        return pd.DataFrame(
            [
                {
                    "fold": f.fold,
                    "train_size": f.train_size,
                    "test_size": f.test_size,
                    "train_end_date": f.train_end_date,
                    "test_start_date": f.test_start_date,
                    "test_end_date": f.test_end_date,
                    "mape": f.mape,
                    "rmse": f.rmse,
                    "smape": f.smape,
                    "mae": f.mae,
                    "fit_time": f.fit_time,
                }
                for f in self.fold_results
            ]
        )

    def __repr__(self) -> str:
        return (
            f"CVResult(method='{self.method}', n_splits={self.n_splits}, "
            f"mape={self.mape_mean:.1f}% +/- {self.mape_std:.1f}%)"
        )


# =============================================================================
# WALK-FORWARD CROSS-VALIDATION
# =============================================================================


class WalkForwardCV:
    """
    Walk-forward cross-validation for time series.

    Parameters
    ----------
    n_splits : int
        Number of CV folds
    test_size : int
        Size of each test set in days
    gap : int
        Gap between train and test (useful for avoiding leakage)
    strategy : str
        'expanding' (default) or 'rolling'
        - expanding: training set grows with each fold
        - rolling: training set stays fixed size
    min_train_size : int, optional
        Minimum training size (for rolling strategy)
    verbose : bool
        Print progress information

    Example
    -------
    >>> cv = WalkForwardCV(n_splits=5, test_size=30)
    >>> results = cv.evaluate(df, forecast_func)
    >>> print(results.summary())
    """

    def __init__(
        self,
        n_splits: int = 5,
        test_size: int = 30,
        gap: int = 0,
        strategy: str = "expanding",
        min_train_size: Optional[int] = None,
        verbose: bool = True,
    ):
        self.n_splits = n_splits
        self.test_size = test_size
        self.gap = gap
        self.strategy = strategy
        self.min_train_size = min_train_size or test_size * 2
        self.verbose = verbose

    def split(
        self,
        df: pd.DataFrame,
        date_col: str = "date",
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Generate train/test splits.

        Parameters
        ----------
        df : pd.DataFrame
            Input data
        date_col : str
            Name of date column

        Returns
        -------
        List of (train_df, test_df) tuples
        """
        df = df.sort_values(date_col).copy()
        dates = df[date_col].unique()
        n_dates = len(dates)

        # Calculate required data length
        total_test = self.n_splits * self.test_size
        total_gap = self.n_splits * self.gap
        min_required = total_test + total_gap + self.min_train_size

        if n_dates < min_required:
            raise ValueError(
                f"Not enough data: have {n_dates} days, need at least {min_required} "
                f"for {self.n_splits} splits with test_size={self.test_size}"
            )

        splits = []

        for i in range(self.n_splits):
            # Calculate indices for this fold (from end backwards)
            test_end_idx = n_dates - i * self.test_size
            test_start_idx = test_end_idx - self.test_size
            train_end_idx = test_start_idx - self.gap

            # For rolling strategy, limit train start
            if self.strategy == "rolling" and self.min_train_size:
                train_start_idx = max(0, train_end_idx - self.min_train_size)
            else:
                train_start_idx = 0

            # Get dates
            test_end_date = dates[test_end_idx - 1]
            test_start_date = dates[test_start_idx]
            train_end_date = dates[train_end_idx - 1]
            train_start_date = dates[train_start_idx]

            # Create splits
            train = df[
                (df[date_col] >= train_start_date) & (df[date_col] <= train_end_date)
            ].copy()

            test = df[
                (df[date_col] >= test_start_date) & (df[date_col] <= test_end_date)
            ].copy()

            splits.append((train, test))

        # Return in chronological order
        return splits[::-1]

    def evaluate(
        self,
        df: pd.DataFrame,
        forecast_func: Callable,
        method_name: str = "method",
        date_col: str = "date",
        target_col: str = "revenue",
    ) -> CVResult:
        """
        Run walk-forward CV and return aggregated results.

        Parameters
        ----------
        df : pd.DataFrame
            Input data for a single game
        forecast_func : Callable
            Function that takes (train_df, horizon) and returns predictions array
        method_name : str
            Name for this method
        date_col : str
            Date column name
        target_col : str
            Target column name

        Returns
        -------
        CVResult with aggregated metrics
        """
        splits = self.split(df, date_col)
        fold_results = []

        for i, (train, test) in enumerate(splits):
            if self.verbose:
                print(
                    f"  Fold {i + 1}/{self.n_splits}: "
                    f"train={len(train)} days, test={len(test)} days"
                )

            # Time the fit + predict
            start_time = time.time()

            try:
                predictions = forecast_func(train, len(test))
                fit_time = time.time() - start_time

                # Ensure predictions are numpy array
                if isinstance(predictions, pd.Series):
                    predictions = predictions.values
                predictions = np.array(predictions).flatten()

                # Get actual values
                y_true = test[target_col].values

                # Handle length mismatch
                min_len = min(len(y_true), len(predictions))
                y_true = y_true[:min_len]
                predictions = predictions[:min_len]

                # Calculate metrics
                fold_result = CVFoldResult(
                    fold=i + 1,
                    train_size=len(train),
                    test_size=len(test),
                    train_end_date=train[date_col].max(),
                    test_start_date=test[date_col].min(),
                    test_end_date=test[date_col].max(),
                    y_true=y_true,
                    y_pred=predictions,
                    mape=mape(y_true, predictions),
                    rmse=rmse(y_true, predictions),
                    smape=smape(y_true, predictions),
                    mae=mae(y_true, predictions),
                    fit_time=fit_time,
                )

            except Exception as e:
                if self.verbose:
                    print(f"    Error in fold {i + 1}: {e}")
                # Create a failed fold result with NaN metrics
                fold_result = CVFoldResult(
                    fold=i + 1,
                    train_size=len(train),
                    test_size=len(test),
                    train_end_date=train[date_col].max(),
                    test_start_date=test[date_col].min(),
                    test_end_date=test[date_col].max(),
                    y_true=test[target_col].values,
                    y_pred=np.full(len(test), np.nan),
                    mape=np.nan,
                    rmse=np.nan,
                    smape=np.nan,
                    mae=np.nan,
                    fit_time=time.time() - start_time,
                )

            fold_results.append(fold_result)

        return CVResult(
            method=method_name,
            n_splits=self.n_splits,
            test_size=self.test_size,
            fold_results=fold_results,
        )


# =============================================================================
# BUILT-IN FORECASTER FUNCTIONS
# =============================================================================


def make_holt_winters_forecaster(
    seasonal_periods: int = 7,
    trend: str = "add",
    seasonal: str = "mul",
    damped_trend: bool = True,
) -> Callable:
    """Create a Holt-Winters forecaster function for CV."""

    def forecast(train_df: pd.DataFrame, horizon: int) -> np.ndarray:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        y = train_df["revenue"].values

        model = ExponentialSmoothing(
            y,
            seasonal_periods=seasonal_periods,
            trend=trend,
            seasonal=seasonal,
            damped_trend=damped_trend,
            initialization_method="estimated",
        )
        fitted = model.fit(optimized=True)
        return fitted.forecast(horizon)

    return forecast


def make_autoets_forecaster() -> Callable:
    """Create an AutoETS forecaster function for CV."""

    def forecast(train_df: pd.DataFrame, horizon: int) -> np.ndarray:
        from statsforecast import StatsForecast
        from statsforecast.models import AutoETS

        sf_df = pd.DataFrame(
            {
                "unique_id": "game",
                "ds": train_df["date"],
                "y": train_df["revenue"],
            }
        )

        sf = StatsForecast(
            models=[AutoETS(season_length=7)],
            freq="D",
        )
        sf.fit(sf_df)

        forecast_df = sf.predict(h=horizon)
        return forecast_df["AutoETS"].values

    return forecast


def make_autoarima_forecaster() -> Callable:
    """Create an AutoARIMA forecaster function for CV."""

    def forecast(train_df: pd.DataFrame, horizon: int) -> np.ndarray:
        from statsforecast import StatsForecast
        from statsforecast.models import AutoARIMA

        sf_df = pd.DataFrame(
            {
                "unique_id": "game",
                "ds": train_df["date"],
                "y": train_df["revenue"],
            }
        )

        sf = StatsForecast(
            models=[AutoARIMA(season_length=7)],
            freq="D",
        )
        sf.fit(sf_df)

        forecast_df = sf.predict(h=horizon)
        return forecast_df["AutoARIMA"].values

    return forecast


def make_prophet_forecaster(
    yearly_seasonality: bool = True,
    weekly_seasonality: bool = True,
) -> Callable:
    """Create a Prophet forecaster function for CV."""

    def forecast(train_df: pd.DataFrame, horizon: int) -> np.ndarray:
        from prophet import Prophet

        prophet_df = pd.DataFrame(
            {
                "ds": train_df["date"],
                "y": train_df["revenue"],
            }
        )

        model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=False,
        )
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=horizon)
        forecast_df = model.predict(future)

        return forecast_df["yhat"].tail(horizon).values

    return forecast


def make_lightgbm_forecaster(
    lags: List[int] = [1, 7, 14, 28],
    rolling_windows: List[int] = [7, 14, 28],
) -> Callable:
    """Create a LightGBM forecaster function for CV (recursive prediction)."""

    def forecast(train_df: pd.DataFrame, horizon: int) -> np.ndarray:
        import lightgbm as lgb
        from base import add_calendar_features, add_lag_features, add_rolling_features

        # Prepare features
        df = train_df.copy()
        df = add_calendar_features(df, "date")
        df = add_lag_features(df, "revenue", lags)
        df = add_rolling_features(df, "revenue", rolling_windows)

        # Define feature columns
        feature_cols = [
            "day_of_week",
            "day_of_month",
            "week_of_year",
            "month",
            "quarter",
            "is_weekend",
            "is_month_start",
            "is_month_end",
        ]
        for lag in lags:
            feature_cols.append(f"revenue_lag_{lag}")
        for window in rolling_windows:
            feature_cols.extend(
                [
                    f"revenue_rolling_mean_{window}",
                    f"revenue_rolling_std_{window}",
                    f"revenue_rolling_min_{window}",
                    f"revenue_rolling_max_{window}",
                ]
            )

        # Drop rows with NaN features
        df_clean = df.dropna(subset=feature_cols)

        X = df_clean[feature_cols]
        y = df_clean["revenue"]

        # Train model
        model = lgb.LGBMRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            num_leaves=31,
            verbose=-1,
        )
        model.fit(X, y)

        # Recursive prediction
        predictions = []
        current_df = train_df.copy()

        last_date = current_df["date"].max()

        for i in range(horizon):
            next_date = last_date + pd.Timedelta(days=i + 1)

            # Create next row
            new_row = pd.DataFrame(
                {
                    "date": [next_date],
                    "revenue": [np.nan],
                    "game_name": [current_df["game_name"].iloc[0]],
                    "is_sale": [0],
                    "is_content_drop": [0],
                }
            )

            # Add to working df
            working_df = pd.concat([current_df, new_row], ignore_index=True)
            working_df = add_calendar_features(working_df, "date")
            working_df = add_lag_features(working_df, "revenue", lags)
            working_df = add_rolling_features(working_df, "revenue", rolling_windows)

            # Get features for prediction
            X_pred = working_df[feature_cols].iloc[[-1]]

            # Predict
            pred = model.predict(X_pred)[0]
            predictions.append(max(0, pred))

            # Update for next iteration
            current_df = working_df.copy()
            current_df.loc[current_df.index[-1], "revenue"] = pred

        return np.array(predictions)

    return forecast


def make_naive_forecaster() -> Callable:
    """Create a seasonal naive forecaster (baseline)."""

    def forecast(train_df: pd.DataFrame, horizon: int) -> np.ndarray:
        # Use last week's values repeated
        last_week = train_df["revenue"].tail(7).values
        predictions = np.tile(last_week, (horizon // 7) + 1)[:horizon]
        return predictions

    return forecast


# =============================================================================
# COMPARISON FUNCTIONS
# =============================================================================


def get_default_forecasters() -> Dict[str, Callable]:
    """Get dictionary of default forecaster functions."""
    return {
        "SeasonalNaive": make_naive_forecaster(),
        "HW-Mul-Damped": make_holt_winters_forecaster(
            seasonal="mul", damped_trend=True
        ),
        "HW-Add-Damped": make_holt_winters_forecaster(
            seasonal="add", damped_trend=True
        ),
    }


def get_full_forecasters() -> Dict[str, Callable]:
    """Get dictionary of all forecaster functions (slower)."""
    forecasters = get_default_forecasters()
    forecasters.update(
        {
            "AutoETS": make_autoets_forecaster(),
            "AutoARIMA": make_autoarima_forecaster(),
            "Prophet": make_prophet_forecaster(),
            "LightGBM": make_lightgbm_forecaster(),
        }
    )
    return forecasters


def run_cv_comparison(
    df: pd.DataFrame,
    game_name: str,
    methods: Optional[List[str]] = None,
    n_splits: int = 5,
    test_size: int = 30,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Run walk-forward CV comparison for multiple methods on a single game.

    Parameters
    ----------
    df : pd.DataFrame
        Combined data with multiple games
    game_name : str
        Name of the game to evaluate
    methods : List[str], optional
        List of method names to include (uses defaults if None)
    n_splits : int
        Number of CV folds
    test_size : int
        Test set size in days
    verbose : bool
        Print progress

    Returns
    -------
    pd.DataFrame with comparison results
    """
    # Filter to single game
    game_df = df[df["game_name"] == game_name].copy()

    if len(game_df) == 0:
        raise ValueError(f"No data found for game: {game_name}")

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Walk-Forward CV: {game_name}")
        print(f"{'=' * 60}")
        print(f"Data: {len(game_df)} days")
        print(f"CV: {n_splits} folds, {test_size}-day test periods")

    # Get forecasters
    if methods is None:
        forecasters = get_default_forecasters()
    else:
        all_forecasters = get_full_forecasters()
        forecasters = {k: v for k, v in all_forecasters.items() if k in methods}

    # Run CV
    cv = WalkForwardCV(n_splits=n_splits, test_size=test_size, verbose=False)

    results = []
    for name, forecast_func in forecasters.items():
        if verbose:
            print(f"\nEvaluating {name}...")

        try:
            cv_result = cv.evaluate(game_df, forecast_func, name)
            results.append(cv_result.summary())

            if verbose:
                print(
                    f"  MAPE: {cv_result.mape_mean:.1f}% +/- {cv_result.mape_std:.1f}%"
                )
                print(
                    f"  95% CI: [{cv_result.mape_ci[0]:.1f}%, {cv_result.mape_ci[1]:.1f}%]"
                )
                print(f"  Avg fit time: {cv_result.avg_fit_time:.2f}s")

        except Exception as e:
            if verbose:
                print(f"  Error: {e}")

    if not results:
        return pd.DataFrame()

    comparison_df = pd.concat(results, ignore_index=True)
    comparison_df["game"] = game_name
    comparison_df = comparison_df.sort_values("mape_mean")

    return comparison_df


def run_full_cv_comparison(
    df: pd.DataFrame,
    methods: Optional[List[str]] = None,
    n_splits: int = 5,
    test_size: int = 30,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Run walk-forward CV for all games and methods.

    Parameters
    ----------
    df : pd.DataFrame
        Combined data with multiple games
    methods : List[str], optional
        Methods to include
    n_splits : int
        Number of CV folds
    test_size : int
        Test set size
    verbose : bool
        Print progress

    Returns
    -------
    pd.DataFrame with all results
    """
    games = df["game_name"].unique()
    all_results = []

    for game in games:
        try:
            game_results = run_cv_comparison(
                df, game, methods, n_splits, test_size, verbose
            )
            all_results.append(game_results)
        except Exception as e:
            if verbose:
                print(f"Error processing {game}: {e}")

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


def summarize_cv_results(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize CV results across all games.

    Returns DataFrame with average metrics per method across games.
    """
    summary = (
        results_df.groupby("method")
        .agg(
            {
                "mape_mean": ["mean", "std"],
                "mape_ci_lower": "mean",
                "mape_ci_upper": "mean",
                "rmse_mean": "mean",
                "smape_mean": "mean",
                "avg_fit_time": "mean",
            }
        )
        .round(2)
    )

    # Flatten column names
    summary.columns = ["_".join(col).strip("_") for col in summary.columns]
    summary = summary.rename(
        columns={
            "mape_mean_mean": "mape_mean",
            "mape_mean_std": "mape_std_across_games",
        }
    )

    return summary.sort_values("mape_mean")


# =============================================================================
# VISUALIZATION
# =============================================================================


def plot_cv_comparison(
    results_df: pd.DataFrame,
    metric: str = "mape_mean",
    figsize: Tuple[int, int] = (12, 6),
):
    """
    Plot CV results comparison with confidence intervals.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize)

    methods = results_df["method"].unique()
    games = results_df["game"].unique()

    x = np.arange(len(methods))
    width = 0.8 / len(games)

    for i, game in enumerate(games):
        game_data = results_df[results_df["game"] == game]
        game_data = game_data.set_index("method").reindex(methods)

        bars = ax.bar(
            x + i * width,
            game_data[metric],
            width,
            label=game,
            alpha=0.8,
        )

        # Add error bars if CI available
        if "mape_ci_lower" in game_data.columns:
            errors = [
                game_data[metric] - game_data["mape_ci_lower"],
                game_data["mape_ci_upper"] - game_data[metric],
            ]
            ax.errorbar(
                x + i * width,
                game_data[metric],
                yerr=errors,
                fmt="none",
                color="black",
                capsize=3,
            )

    ax.set_xlabel("Method")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title("Walk-Forward CV Comparison")
    ax.set_xticks(x + width * (len(games) - 1) / 2)
    ax.set_xticklabels(methods, rotation=45, ha="right")
    ax.legend(title="Game", bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.tight_layout()
    return fig


def plot_cv_fold_details(
    cv_result: CVResult,
    figsize: Tuple[int, int] = (14, 8),
):
    """
    Plot detailed results for each CV fold.
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=figsize)

    folds = cv_result.fold_details()

    # MAPE by fold
    ax1 = axes[0, 0]
    ax1.bar(folds["fold"], folds["mape"], color="steelblue", alpha=0.8)
    ax1.axhline(cv_result.mape_mean, color="red", linestyle="--", label="Mean")
    ax1.fill_between(
        [0.5, len(folds) + 0.5],
        cv_result.mape_ci[0],
        cv_result.mape_ci[1],
        alpha=0.2,
        color="red",
        label="95% CI",
    )
    ax1.set_xlabel("Fold")
    ax1.set_ylabel("MAPE (%)")
    ax1.set_title(f"MAPE by Fold ({cv_result.method})")
    ax1.legend()

    # RMSE by fold
    ax2 = axes[0, 1]
    ax2.bar(folds["fold"], folds["rmse"], color="darkorange", alpha=0.8)
    ax2.axhline(cv_result.rmse_mean, color="red", linestyle="--", label="Mean")
    ax2.set_xlabel("Fold")
    ax2.set_ylabel("RMSE ($)")
    ax2.set_title("RMSE by Fold")
    ax2.legend()

    # Training size by fold
    ax3 = axes[1, 0]
    ax3.bar(folds["fold"], folds["train_size"], color="forestgreen", alpha=0.8)
    ax3.set_xlabel("Fold")
    ax3.set_ylabel("Training Days")
    ax3.set_title("Training Set Size by Fold")

    # Fit time by fold
    ax4 = axes[1, 1]
    ax4.bar(folds["fold"], folds["fit_time"], color="purple", alpha=0.8)
    ax4.axhline(cv_result.avg_fit_time, color="red", linestyle="--", label="Mean")
    ax4.set_xlabel("Fold")
    ax4.set_ylabel("Fit Time (s)")
    ax4.set_title("Fit Time by Fold")
    ax4.legend()

    plt.tight_layout()
    return fig


# =============================================================================
# MAIN / DEMO
# =============================================================================


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    print("=" * 60)
    print("Walk-Forward Cross-Validation Demo")
    print("=" * 60)

    # Generate data
    print("\nGenerating synthetic game data...")
    df = generate_all_games_data()

    # Run quick comparison (just baseline methods, faster)
    print("\n" + "=" * 60)
    print("Quick CV Comparison (Baseline Methods)")
    print("=" * 60)

    results = run_cv_comparison(
        df,
        game_name="Battle Royale X",
        methods=None,  # Uses defaults: SeasonalNaive, HW-Mul-Damped, HW-Add-Damped
        n_splits=5,
        test_size=30,
    )

    print("\n" + "-" * 60)
    print("Results Summary:")
    print("-" * 60)
    print(results.to_string(index=False))

    # Run detailed CV for one method and show fold details
    print("\n" + "=" * 60)
    print("Detailed Fold Analysis")
    print("=" * 60)

    game_df = df[df["game_name"] == "Battle Royale X"].copy()
    cv = WalkForwardCV(n_splits=5, test_size=30, verbose=True)

    hw_result = cv.evaluate(
        game_df,
        make_holt_winters_forecaster(seasonal="mul", damped_trend=True),
        "HW-Mul-Damped",
    )

    print("\nFold Details:")
    print(hw_result.fold_details().to_string(index=False))

    # Run full comparison if time permits
    print("\n" + "=" * 60)
    print("Full Comparison Across All Games")
    print("=" * 60)

    full_results = run_full_cv_comparison(
        df,
        methods=["SeasonalNaive", "HW-Mul-Damped", "HW-Add-Damped"],
        n_splits=5,
        test_size=30,
        verbose=True,
    )

    print("\n" + "-" * 60)
    print("Summary Across All Games:")
    print("-" * 60)
    summary = summarize_cv_results(full_results)
    print(summary.to_string())

    # Save results
    output_dir = "output"
    import os

    os.makedirs(output_dir, exist_ok=True)

    full_results.to_csv(f"{output_dir}/cv_results.csv", index=False)
    summary.to_csv(f"{output_dir}/cv_summary.csv")
    print(f"\nResults saved to {output_dir}/")

    # Plot
    fig = plot_cv_fold_details(hw_result)
    fig.savefig(f"{output_dir}/cv_fold_details.png", dpi=150, bbox_inches="tight")
    print(f"Plot saved to {output_dir}/cv_fold_details.png")

    plt.close("all")

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nKey takeaways:")
    print("- Walk-forward CV provides more robust metrics than single splits")
    print("- Confidence intervals help understand metric uncertainty")
    print("- Use run_cv_comparison() for quick method comparisons")
    print("- Use run_full_cv_comparison() for comprehensive analysis")
