"""
LightGBM Forecasting Test Suite

Tests feature engineering approach with lags, rolling stats, calendar features,
and sale event flags for game revenue forecasting.

Gotchas and Notes:
- ML approach requires explicit feature engineering
- Handles complex non-linear relationships
- Easily incorporates exogenous variables (sale events, etc.)
- Need to be careful about data leakage with lag features
- Requires more data preparation than statistical methods
"""

import time
import warnings
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import lightgbm as lgb
from base import (
    generate_all_games_data,
    time_series_split,
    evaluate_forecast,
    add_calendar_features,
    add_lag_features,
    add_rolling_features,
    get_default_sale_events,
    SaleEvent,
    mape,
)

warnings.filterwarnings("ignore")


# =============================================================================
# FEATURE ENGINEERING
# =============================================================================


def create_target_encoding(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    group_col: str,
    target_col: str = "revenue",
    prefix: str = "te",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create target encoding features based on historical means.

    This is a simple target encoding that uses the training set mean
    for each group. More sophisticated versions could use smoothing.
    """
    train = train_df.copy()
    test = test_df.copy()

    # Calculate mean per group from training data
    means = train.groupby(group_col)[target_col].mean()

    # Apply to both train and test
    train[f"{prefix}_{group_col}"] = train[group_col].map(means)
    test[f"{prefix}_{group_col}"] = test[group_col].map(means)

    # Fill missing values with global mean
    global_mean = train[target_col].mean()
    train[f"{prefix}_{group_col}"] = train[f"{prefix}_{group_col}"].fillna(global_mean)
    test[f"{prefix}_{group_col}"] = test[f"{prefix}_{group_col}"].fillna(global_mean)

    return train, test


def create_sale_event_features(
    df: pd.DataFrame, sale_events: List[SaleEvent], date_col: str = "date"
) -> pd.DataFrame:
    """
    Create comprehensive sale event features.

    Features created:
    - is_sale: Binary indicator
    - sale_intensity: Expected revenue multiplier
    - days_since_sale: Days since last sale started
    - days_to_sale: Days until next sale starts
    - sale_day_number: Which day of the current sale (1, 2, 3...)
    """
    df = df.copy()

    # Initialize columns
    df["is_sale"] = 0
    df["sale_intensity"] = 1.0
    df["sale_day_number"] = 0

    # Track sale dates for proximity features
    sale_start_dates = []
    sale_end_dates = []

    for event in sale_events:
        start = pd.to_datetime(event.start_date)
        end = pd.to_datetime(event.end_date)

        sale_start_dates.append(start)
        sale_end_dates.append(end)

        # Mark sale days
        mask = (df[date_col] >= start) & (df[date_col] <= end)
        df.loc[mask, "is_sale"] = 1
        df.loc[mask, "sale_intensity"] = event.revenue_multiplier

        # Calculate day number within sale
        if mask.any():
            sale_days = (df.loc[mask, date_col] - start).dt.days + 1
            df.loc[mask, "sale_day_number"] = sale_days

    # Days since/to sale
    sale_start_dates = sorted(sale_start_dates)

    def days_since_last_sale(date, starts):
        past = [s for s in starts if s <= date]
        if past:
            return (date - max(past)).days
        return 365  # Default if no past sales

    def days_to_next_sale(date, starts):
        future = [s for s in starts if s > date]
        if future:
            return (min(future) - date).days
        return 365  # Default if no future sales

    df["days_since_sale"] = df[date_col].apply(
        lambda x: days_since_last_sale(x, sale_start_dates)
    )
    df["days_to_sale"] = df[date_col].apply(
        lambda x: days_to_next_sale(x, sale_start_dates)
    )

    # Clip extreme values
    df["days_since_sale"] = df["days_since_sale"].clip(upper=90)
    df["days_to_sale"] = df["days_to_sale"].clip(upper=90)

    return df


def create_all_features(
    df: pd.DataFrame,
    target_col: str = "revenue",
    date_col: str = "date",
    sale_events: Optional[List[SaleEvent]] = None,
    lag_periods: List[int] = [1, 7, 14, 28],
    rolling_windows: List[int] = [7, 14, 28],
) -> pd.DataFrame:
    """
    Create comprehensive feature set for LightGBM.

    Parameters
    ----------
    df : pd.DataFrame
        Input data
    target_col : str
        Target column name
    date_col : str
        Date column name
    sale_events : list
        Sale events for creating event features
    lag_periods : list
        Lag periods for lag features
    rolling_windows : list
        Window sizes for rolling features

    Returns
    -------
    pd.DataFrame
        DataFrame with all features
    """
    df = df.copy()
    df = df.sort_values(date_col)

    # Calendar features
    df = add_calendar_features(df, date_col)

    # Lag features
    df = add_lag_features(df, target_col, lag_periods)

    # Rolling features
    df = add_rolling_features(df, target_col, rolling_windows)

    # Sale event features
    if sale_events:
        df = create_sale_event_features(df, sale_events, date_col)

    # Interaction features
    df["weekend_x_lag1"] = df["is_weekend"] * df.get(f"{target_col}_lag_1", 0)

    # Ratio features
    df["lag1_to_lag7_ratio"] = (
        df[f"{target_col}_lag_1"] / df[f"{target_col}_lag_7"].replace(0, np.nan)
    ).fillna(1)

    # Trend indicator
    df["short_term_trend"] = (
        df[f"{target_col}_rolling_mean_7"] - df[f"{target_col}_rolling_mean_28"]
    )

    return df


def prepare_lgb_data(
    df: pd.DataFrame,
    target_col: str = "revenue",
    date_col: str = "date",
    exclude_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Prepare data for LightGBM training.

    Returns features, target, and feature names.
    """
    if exclude_cols is None:
        exclude_cols = []

    # Columns to exclude from features
    non_feature_cols = [
        target_col,
        date_col,
        "game_name",
        "day_name",
        "sale_name",
    ] + exclude_cols

    feature_cols = [c for c in df.columns if c not in non_feature_cols]

    X = df[feature_cols].copy()
    y = df[target_col].copy()

    return X, y, feature_cols


# =============================================================================
# LIGHTGBM FORECASTER
# =============================================================================


class LightGBMForecaster:
    """
    LightGBM-based forecaster with recursive prediction.

    Gotchas:
    - Requires feature engineering (lags, rolling stats, etc.)
    - Need to handle future predictions carefully (recursive)
    - Data leakage is a risk with lag features
    - Works best with sufficient history for lag features
    """

    def __init__(
        self,
        params: Optional[Dict] = None,
        num_boost_round: int = 1000,
        early_stopping_rounds: int = 50,
        feature_cols: Optional[List[str]] = None,
    ):
        self.params = params or self._get_default_params()
        self.num_boost_round = num_boost_round
        self.early_stopping_rounds = early_stopping_rounds
        self.feature_cols = feature_cols
        self.model = None
        self.train_time = None
        self.feature_importance = None

    @staticmethod
    def _get_default_params() -> Dict:
        """Get default LightGBM parameters."""
        return {
            "objective": "regression",
            "metric": "mape",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "min_child_samples": 20,
            "min_data_in_leaf": 20,
            "lambda_l1": 0.1,
            "lambda_l2": 0.1,
            "verbosity": -1,
            "random_state": 42,
        }

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> "LightGBMForecaster":
        """
        Fit the LightGBM model.

        Parameters
        ----------
        X_train : pd.DataFrame
            Training features
        y_train : pd.Series
            Training target
        X_val : pd.DataFrame, optional
            Validation features for early stopping
        y_val : pd.Series, optional
            Validation target
        """
        start_time = time.time()

        if self.feature_cols is None:
            self.feature_cols = X_train.columns.tolist()

        train_data = lgb.Dataset(X_train, label=y_train)

        callbacks = [lgb.log_evaluation(period=0)]  # Suppress output

        if X_val is not None and y_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            callbacks.append(lgb.early_stopping(self.early_stopping_rounds))

            self.model = lgb.train(
                self.params,
                train_data,
                num_boost_round=self.num_boost_round,
                valid_sets=[train_data, val_data],
                valid_names=["train", "valid"],
                callbacks=callbacks,
            )
        else:
            self.model = lgb.train(
                self.params,
                train_data,
                num_boost_round=self.num_boost_round,
                callbacks=callbacks,
            )

        self.train_time = time.time() - start_time

        # Store feature importance
        self.feature_importance = pd.DataFrame(
            {
                "feature": self.feature_cols,
                "importance": self.model.feature_importance(importance_type="gain"),
            }
        ).sort_values("importance", ascending=False)

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate predictions."""
        return self.model.predict(X)

    def predict_recursive(
        self,
        last_known_data: pd.DataFrame,
        n_periods: int,
        target_col: str = "revenue",
        date_col: str = "date",
        sale_events: Optional[List[SaleEvent]] = None,
    ) -> np.ndarray:
        """
        Generate recursive forecasts for multiple periods.

        This handles the challenge of forecasting when features
        depend on lagged values of the target.

        Parameters
        ----------
        last_known_data : pd.DataFrame
            Historical data with all features
        n_periods : int
            Number of periods to forecast
        target_col : str
            Target column name
        date_col : str
            Date column name
        sale_events : list
            Sale events for future dates

        Returns
        -------
        np.ndarray
            Array of predictions
        """
        predictions = []
        history = last_known_data.copy()

        last_date = history[date_col].max()

        for i in range(n_periods):
            # Create next date
            next_date = last_date + pd.Timedelta(days=i + 1)

            # Create new row with calendar features
            new_row = pd.DataFrame(
                {
                    date_col: [next_date],
                    target_col: [np.nan],  # Will be filled with prediction
                    "game_name": [history["game_name"].iloc[0]],
                }
            )

            # Add calendar features
            new_row = add_calendar_features(new_row, date_col)

            # Add sale event features
            if sale_events:
                new_row = create_sale_event_features(new_row, sale_events, date_col)

            # Calculate lag and rolling features from history + previous predictions
            combined = pd.concat([history, new_row], ignore_index=True)
            combined = combined.sort_values(date_col)

            # Recalculate lag features
            combined = add_lag_features(combined, target_col, [1, 7, 14, 28])
            combined = add_rolling_features(combined, target_col, [7, 14, 28])

            # Add interaction features
            combined["weekend_x_lag1"] = combined["is_weekend"] * combined.get(
                f"{target_col}_lag_1", 0
            )
            combined["lag1_to_lag7_ratio"] = (
                combined[f"{target_col}_lag_1"]
                / combined[f"{target_col}_lag_7"].replace(0, np.nan)
            ).fillna(1)
            combined["short_term_trend"] = (
                combined[f"{target_col}_rolling_mean_7"]
                - combined[f"{target_col}_rolling_mean_28"]
            )

            # Get the last row (our prediction target)
            X_new = combined[combined[date_col] == next_date][self.feature_cols]

            # Fill any remaining NaN with 0
            X_new = X_new.fillna(0)

            # Predict
            pred = self.model.predict(X_new)[0]
            pred = max(0, pred)  # Ensure non-negative
            predictions.append(pred)

            # Update history with prediction
            new_row[target_col] = pred
            history = pd.concat([history, new_row], ignore_index=True)

        return np.array(predictions)

    def plot_feature_importance(
        self, top_n: int = 20, figsize: Tuple[int, int] = (10, 8)
    ) -> plt.Figure:
        """Plot feature importance."""
        fig, ax = plt.subplots(figsize=figsize)

        top_features = self.feature_importance.head(top_n)

        ax.barh(top_features["feature"], top_features["importance"])
        ax.set_xlabel("Importance (Gain)")
        ax.set_title(f"Top {top_n} Feature Importance")
        ax.invert_yaxis()

        plt.tight_layout()
        return fig


# =============================================================================
# EXPERIMENTS
# =============================================================================


def run_lightgbm_experiment(
    df: pd.DataFrame,
    game_name: str,
    holdout_periods: List[int] = [30, 60, 90],
    sale_events: Optional[List[SaleEvent]] = None,
    use_recursive: bool = True,
) -> pd.DataFrame:
    """
    Run LightGBM experiments for a specific game.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    game_name : str
        Name of the game
    holdout_periods : list
        Holdout periods to test
    sale_events : list
        Sale events for features
    use_recursive : bool
        Whether to use recursive prediction (slower but more accurate)

    Returns
    -------
    pd.DataFrame
        Results for all holdout periods
    """
    if sale_events is None:
        sale_events = get_default_sale_events()

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    results = []

    for period in holdout_periods:
        print(f"\n  {period}-day holdout:")

        train_raw, test_raw = time_series_split(game_df, period)

        # Create features for full dataset
        full_df = create_all_features(game_df, "revenue", "date", sale_events)

        # Split back into train/test
        train = full_df[full_df["date"] <= train_raw["date"].max()].copy()
        test = full_df[full_df["date"] > train_raw["date"].max()].copy()

        # Drop rows with NaN in key lag features (beginning of series)
        train = train.dropna(subset=["revenue_lag_7", "revenue_rolling_mean_7"])

        # Prepare LightGBM data
        X_train, y_train, feature_cols = prepare_lgb_data(train)
        X_test, y_test, _ = prepare_lgb_data(test)

        # Create validation set from end of training
        val_size = min(30, len(train) // 5)
        X_val = X_train.iloc[-val_size:]
        y_val = y_train.iloc[-val_size:]
        X_train_fit = X_train.iloc[:-val_size]
        y_train_fit = y_train.iloc[:-val_size]

        # Fit model
        forecaster = LightGBMForecaster(feature_cols=feature_cols)
        forecaster.fit(X_train_fit, y_train_fit, X_val, y_val)

        if use_recursive:
            # Use recursive prediction (realistic for production)
            # This is slower but doesn't use future information
            predictions = forecaster.predict_recursive(
                train,
                n_periods=len(test),
                target_col="revenue",
                date_col="date",
                sale_events=sale_events,
            )
        else:
            # Direct prediction (features from test set)
            # WARNING: This uses actual lag values which are NOT available
            # in true forecasting scenarios - only use for ablation studies
            X_test = X_test.fillna(0)
            predictions = forecaster.predict(X_test)

        # Evaluate
        y_true = test_raw["revenue"].values

        metrics = evaluate_forecast(y_true, predictions, "LightGBM")
        metrics["holdout_days"] = period
        metrics["train_time_sec"] = forecaster.train_time
        metrics["game"] = game_name
        metrics["prediction_method"] = "recursive" if use_recursive else "direct"
        metrics["n_features"] = len(feature_cols)

        results.append(metrics)

        print(
            f"    LightGBM: MAPE = {metrics['mape']:.2f}% | "
            f"Time: {forecaster.train_time:.2f}s"
        )

        # Print top features
        print("    Top 5 features:")
        for _, row in forecaster.feature_importance.head(5).iterrows():
            print(f"      - {row['feature']}: {row['importance']:.1f}")

    return pd.DataFrame(results)


def run_feature_ablation(
    df: pd.DataFrame,
    game_name: str,
    test_days: int = 30,
    sale_events: Optional[List[SaleEvent]] = None,
) -> pd.DataFrame:
    """
    Run feature ablation study to understand feature importance.

    Tests model performance with different feature subsets:
    - All features
    - No lag features
    - No rolling features
    - No sale event features
    - No calendar features
    - Only lag features
    """
    if sale_events is None:
        sale_events = get_default_sale_events()

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    train_raw, test_raw = time_series_split(game_df, test_days)

    feature_sets = {
        "all_features": {
            "lags": [1, 7, 14, 28],
            "rolling": [7, 14, 28],
            "calendar": True,
            "sales": True,
        },
        "no_lags": {
            "lags": [],
            "rolling": [7, 14, 28],
            "calendar": True,
            "sales": True,
        },
        "no_rolling": {
            "lags": [1, 7, 14, 28],
            "rolling": [],
            "calendar": True,
            "sales": True,
        },
        "no_sales": {
            "lags": [1, 7, 14, 28],
            "rolling": [7, 14, 28],
            "calendar": True,
            "sales": False,
        },
        "no_calendar": {
            "lags": [1, 7, 14, 28],
            "rolling": [7, 14, 28],
            "calendar": False,
            "sales": True,
        },
        "only_lags": {
            "lags": [1, 7, 14, 28],
            "rolling": [],
            "calendar": False,
            "sales": False,
        },
    }

    results = []

    for set_name, config in feature_sets.items():
        print(f"\n  Testing: {set_name}")

        # Create features based on config
        df_temp = game_df.copy()
        df_temp = df_temp.sort_values("date")

        if config["calendar"]:
            df_temp = add_calendar_features(df_temp, "date")

        if config["lags"]:
            df_temp = add_lag_features(df_temp, "revenue", config["lags"])

        if config["rolling"]:
            df_temp = add_rolling_features(df_temp, "revenue", config["rolling"])

        if config["sales"]:
            df_temp = create_sale_event_features(df_temp, sale_events, "date")

        # Split
        train = df_temp[df_temp["date"] <= train_raw["date"].max()].copy()
        test = df_temp[df_temp["date"] > train_raw["date"].max()].copy()

        # Drop rows with NaN (if using lags/rolling)
        if config["lags"] or config["rolling"]:
            cols_to_check = []
            if config["lags"]:
                cols_to_check.append("revenue_lag_7")
            if config["rolling"]:
                cols_to_check.append("revenue_rolling_mean_7")
            train = train.dropna(subset=cols_to_check)

        # Prepare data
        X_train, y_train, feature_cols = prepare_lgb_data(train)
        X_test, _, _ = prepare_lgb_data(test)

        if len(feature_cols) == 0:
            print("    Skipped: No features")
            continue

        # Fit
        forecaster = LightGBMForecaster(feature_cols=feature_cols)

        # Create validation split
        val_size = min(30, len(X_train) // 5)
        if val_size > 10:
            forecaster.fit(
                X_train.iloc[:-val_size],
                y_train.iloc[:-val_size],
                X_train.iloc[-val_size:],
                y_train.iloc[-val_size:],
            )
        else:
            forecaster.fit(X_train, y_train)

        # Predict
        X_test = X_test.fillna(0)
        predictions = forecaster.predict(X_test)

        # Evaluate
        metrics = evaluate_forecast(test_raw["revenue"].values, predictions, set_name)
        metrics["feature_set"] = set_name
        metrics["n_features"] = len(feature_cols)
        metrics["game"] = game_name

        results.append(metrics)

        print(f"    MAPE = {metrics['mape']:.2f}% | Features: {len(feature_cols)}")

    return pd.DataFrame(results)


def run_hyperparameter_tuning(
    df: pd.DataFrame,
    game_name: str,
    test_days: int = 30,
    sale_events: Optional[List[SaleEvent]] = None,
) -> Dict:
    """
    Run simple hyperparameter search for LightGBM.

    Tests different combinations of key parameters.
    """
    if sale_events is None:
        sale_events = get_default_sale_events()

    game_df = df[df["game_name"] == game_name].copy()
    game_df = game_df.sort_values("date")

    # Create features
    full_df = create_all_features(game_df, "revenue", "date", sale_events)

    train_raw, test_raw = time_series_split(game_df, test_days)
    train = full_df[full_df["date"] <= train_raw["date"].max()].copy()
    test = full_df[full_df["date"] > train_raw["date"].max()].copy()

    train = train.dropna(subset=["revenue_lag_7", "revenue_rolling_mean_7"])

    X_train, y_train, feature_cols = prepare_lgb_data(train)
    X_test, _, _ = prepare_lgb_data(test)

    # Validation split
    val_size = 30
    X_val = X_train.iloc[-val_size:]
    y_val = y_train.iloc[-val_size:]
    X_train_fit = X_train.iloc[:-val_size]
    y_train_fit = y_train.iloc[:-val_size]

    # Parameter grid (simplified)
    param_grid = {
        "num_leaves": [15, 31, 50],
        "learning_rate": [0.01, 0.05, 0.1],
        "min_data_in_leaf": [10, 20, 50],
    }

    results = []

    for num_leaves in param_grid["num_leaves"]:
        for lr in param_grid["learning_rate"]:
            for min_data in param_grid["min_data_in_leaf"]:
                params = LightGBMForecaster._get_default_params()
                params["num_leaves"] = num_leaves
                params["learning_rate"] = lr
                params["min_data_in_leaf"] = min_data

                forecaster = LightGBMForecaster(
                    params=params, feature_cols=feature_cols
                )
                forecaster.fit(X_train_fit, y_train_fit, X_val, y_val)

                X_test_filled = X_test.fillna(0)
                predictions = forecaster.predict(X_test_filled)

                mape_score = mape(test_raw["revenue"].values, predictions)

                results.append(
                    {
                        "num_leaves": num_leaves,
                        "learning_rate": lr,
                        "min_data_in_leaf": min_data,
                        "mape": mape_score,
                    }
                )

    results_df = pd.DataFrame(results)
    best = results_df.loc[results_df["mape"].idxmin()]

    print(f"\nBest parameters for {game_name}:")
    print(f"  num_leaves: {int(best['num_leaves'])}")
    print(f"  learning_rate: {best['learning_rate']}")
    print(f"  min_data_in_leaf: {int(best['min_data_in_leaf'])}")
    print(f"  MAPE: {best['mape']:.2f}%")

    return {"all_results": results_df, "best_params": best.to_dict(), "game": game_name}


# =============================================================================
# RUN ALL EXPERIMENTS
# =============================================================================


def run_all_lightgbm_experiments(
    df: pd.DataFrame,
    games: Optional[List[str]] = None,
    holdout_periods: List[int] = [30, 60, 90],
    sale_events: Optional[List[SaleEvent]] = None,
    save_results: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Run all LightGBM experiments.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset
    games : list
        List of game names to test
    holdout_periods : list
        Holdout periods to evaluate
    sale_events : list
        Sale events for features
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
    ablation_results = []

    for game in games:
        print(f"\n{'=' * 60}")
        print(f"Processing: {game}")
        print("=" * 60)

        # Main experiments
        results = run_lightgbm_experiment(
            df, game, holdout_periods, sale_events, use_recursive=True
        )
        all_results.append(results)

        # Feature ablation
        print("\n--- Feature Ablation Study ---")
        ablation = run_feature_ablation(df, game, 30, sale_events)
        ablation_results.append(ablation)

    main_results = pd.concat(all_results, ignore_index=True)
    ablation_df = pd.concat(ablation_results, ignore_index=True)

    if save_results:
        main_results.to_csv("output/results_lightgbm.csv", index=False)
        ablation_df.to_csv("output/results_lightgbm_ablation.csv", index=False)
        print("\nResults saved to output/results_lightgbm*.csv")

    return {"main_results": main_results, "ablation": ablation_df}


# =============================================================================
# DOCUMENTATION AND GOTCHAS
# =============================================================================

LIGHTGBM_GOTCHAS = """
=============================================================================
LIGHTGBM FORECASTING - GOTCHAS AND RECOMMENDATIONS
=============================================================================

1. FEATURE ENGINEERING
----------------------
Critical features for time series:
- Lag features: Yesterday, last week, last month
- Rolling statistics: Moving average, std, min, max
- Calendar features: Day of week, month, holidays
- Domain features: Sale events, content drops

Gotchas:
- Lag features cause NaN at the start of series
- Rolling features need minimum window history
- Must be careful about data leakage

Recommendation:
- Start with lag_1, lag_7, rolling_mean_7
- Add more features iteratively
- Monitor feature importance

2. DATA LEAKAGE
---------------
Common leakage sources:
- Using future data in lag calculations
- Target encoding without proper CV
- Rolling stats calculated on full series

Prevention:
- Always calculate features on train only
- Use walk-forward validation
- Be explicit about feature timing

3. RECURSIVE VS DIRECT PREDICTION
---------------------------------
Direct prediction:
- Uses actual lag values from test set
- Faster, simpler
- NOT realistic for true forecasting
- Only use for benchmarking

Recursive prediction:
- Uses predicted values for future lags
- Slower, more complex
- REALISTIC for production
- Errors can compound

Recommendation:
- Use recursive for final evaluation
- Use direct for quick experiments
- Always note which method used

4. HANDLING EXOGENOUS VARIABLES
-------------------------------
Sale events:
- Easy to include as features
- Can use binary flags or intensity
- Future values must be known

Content drops:
- Similar to sale events
- Can encode as scheduled indicators

Weather/external data:
- Requires forecasted values
- Consider using lagged versions

5. HYPERPARAMETER TUNING
-------------------------
Important parameters:
- num_leaves: Model complexity (start 31)
- learning_rate: Step size (start 0.05)
- min_data_in_leaf: Overfitting control (start 20)

Less important for time series:
- feature_fraction: Can help with noise
- bagging: Less useful than for i.i.d. data

Time series specific:
- Use early stopping with validation
- Validation should be recent data, not random

6. MISSING DATA
---------------
LightGBM handles missing values:
- NaN values are accepted
- Model learns to split on missing

Recommendations:
- Fill obvious missings (weekends, etc.)
- Let model handle sporadic missings
- Be careful with lag feature NaNs

7. COMPARING TO STATISTICAL METHODS
------------------------------------
When LightGBM wins:
- Complex patterns (non-linear)
- Many exogenous variables
- Sufficient history

When statistical methods win:
- Short history
- Simple patterns
- Need prediction intervals

Typical accuracy comparison:
- Similar for simple series
- LightGBM better with complex features
- Statistical better for uncertainty

8. PRODUCTION CONSIDERATIONS
-----------------------------
Model storage:
- Save model with joblib/pickle
- Store feature list and transformations
- Version control features and model together

Inference:
- Feature calculation is the bottleneck
- Pre-calculate what you can
- Recursive prediction is slow

Monitoring:
- Track feature drift
- Monitor prediction accuracy
- Re-train on schedule (weekly/monthly)

=============================================================================
"""


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("LightGBM Forecasting Test Suite")
    print("=" * 60)

    # Generate synthetic data
    print("\nGenerating synthetic game revenue data...")
    df = generate_all_games_data()

    print(f"Data shape: {df.shape}")
    print(f"Games: {df['game_name'].unique().tolist()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    # Run experiments
    print("\n" + "=" * 60)
    print("Running LightGBM Experiments")
    print("=" * 60)

    results = run_all_lightgbm_experiments(
        df,
        games=None,  # All games
        holdout_periods=[30, 60, 90],
        save_results=True,
    )

    # Summary
    print("\n" + "=" * 60)
    print("Main Results Summary")
    print("=" * 60)
    print(
        results["main_results"]
        .groupby("holdout_days")["mape"]
        .agg(["mean", "std", "min", "max"])
    )

    print("\n" + "=" * 60)
    print("Feature Ablation Summary")
    print("=" * 60)
    print(results["ablation"].groupby("feature_set")["mape"].agg(["mean", "std"]))

    # Print gotchas
    print(LIGHTGBM_GOTCHAS)
