"""
Unified Forecaster API

A simple, production-ready interface for game revenue forecasting.
Wraps the best methods discovered in our experiments and provides:

1. Easy-to-use API with sensible defaults
2. Automatic method selection based on data characteristics
3. Built-in prediction intervals
4. Ensemble capabilities

Usage:
    from forecaster import GameRevenueForecaster

    # Simple usage
    forecaster = GameRevenueForecaster()
    forecaster.fit(train_df)
    predictions = forecaster.predict(30)  # 30-day forecast

    # With prediction intervals
    result = forecaster.predict_with_intervals(30, coverage=0.90)

    # Ensemble
    forecaster = GameRevenueForecaster(method='ensemble')
    forecaster.fit(train_df)
    predictions = forecaster.predict(30)
"""

import time
import warnings
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd

# Import prediction intervals
from prediction_intervals import ConformalInterval, evaluate_coverage

warnings.filterwarnings("ignore")


class ForecastMethod(str, Enum):
    """Available forecasting methods."""

    AUTO = "auto"
    HOLT_WINTERS = "holt_winters"
    AUTOETS = "autoets"
    AUTOARIMA = "autoarima"
    PROPHET = "prophet"
    LIGHTGBM = "lightgbm"
    ENSEMBLE = "ensemble"


@dataclass
class ForecastResult:
    """Container for forecast results with metadata."""

    dates: pd.DatetimeIndex
    predictions: np.ndarray
    lower: Optional[np.ndarray] = None
    upper: Optional[np.ndarray] = None
    coverage: Optional[float] = None
    method: str = ""
    train_time: float = 0.0

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame."""
        df = pd.DataFrame({"date": self.dates, "forecast": self.predictions})
        if self.lower is not None:
            df["lower"] = np.maximum(0, self.lower)  # Revenue can't be negative
        if self.upper is not None:
            df["upper"] = self.upper
        return df

    def __repr__(self) -> str:
        return (
            f"ForecastResult(n_periods={len(self.predictions)}, "
            f"method='{self.method}', "
            f"coverage={self.coverage})"
        )


class GameRevenueForecaster:
    """
    Unified forecaster for game revenue prediction.

    Wraps multiple forecasting methods with a consistent interface.
    Supports automatic method selection, ensembles, and prediction intervals.

    Parameters
    ----------
    method : str or ForecastMethod
        Forecasting method to use:
        - 'auto': Automatically select based on data characteristics
        - 'holt_winters': Exponential smoothing (fast, good baseline)
        - 'autoets': Automatic ETS selection (via statsforecast)
        - 'autoarima': Automatic ARIMA (via statsforecast)
        - 'prophet': Facebook Prophet (good for seasonality + events)
        - 'lightgbm': ML with features (best with external data)
        - 'ensemble': Combine multiple methods

    date_col : str
        Name of date column
    target_col : str
        Name of target column
    sale_events : list, optional
        Sale events for Prophet/LightGBM

    Examples
    --------
    >>> from forecaster import GameRevenueForecaster
    >>> forecaster = GameRevenueForecaster(method='auto')
    >>> forecaster.fit(train_df)
    >>> predictions = forecaster.predict(30)
    >>> print(predictions.head())
    """

    def __init__(
        self,
        method: Union[str, ForecastMethod] = "auto",
        date_col: str = "date",
        target_col: str = "revenue",
        sale_events: Optional[List] = None,
        seasonal_period: int = 7,
        verbose: bool = False,
    ):
        if isinstance(method, str):
            method = ForecastMethod(method.lower())

        self.method = method
        self.date_col = date_col
        self.target_col = target_col
        self.sale_events = sale_events
        self.seasonal_period = seasonal_period
        self.verbose = verbose

        # Internal state
        self._fitted_model = None
        self._train_df = None
        self._train_time = 0.0
        self._interval_estimator = None
        self._selected_method = None

    def _log(self, msg: str):
        """Print message if verbose."""
        if self.verbose:
            print(f"[Forecaster] {msg}")

    def _select_method(self, df: pd.DataFrame) -> ForecastMethod:
        """
        Automatically select best method based on data characteristics.

        Selection logic:
        - Short series (< 60 days): Holt-Winters (robust)
        - With sale events: Prophet or LightGBM
        - Stable mature games: AutoETS
        - New launch / high variance: Ensemble
        """
        n_days = len(df)
        has_sales = self.sale_events is not None and len(self.sale_events) > 0

        # Check data variance
        daily_returns = df[self.target_col].pct_change().dropna()
        volatility = daily_returns.std()

        self._log(f"Data analysis: {n_days} days, volatility={volatility:.3f}")

        if n_days < 60:
            self._log("Short series -> Holt-Winters")
            return ForecastMethod.HOLT_WINTERS

        if has_sales:
            self._log("Has sale events -> Prophet")
            return ForecastMethod.PROPHET

        if volatility > 0.3:
            self._log("High volatility -> Ensemble")
            return ForecastMethod.ENSEMBLE

        self._log("Default -> AutoETS")
        return ForecastMethod.AUTOETS

    def _fit_holt_winters(self, df: pd.DataFrame):
        """Fit Holt-Winters exponential smoothing."""
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        series = df.set_index(self.date_col)[self.target_col]
        series.index = pd.DatetimeIndex(series.index)
        series.index.freq = "D"

        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal="add",
            seasonal_periods=self.seasonal_period,
            damped_trend=True,
        ).fit()

        return model

    def _fit_autoets(self, df: pd.DataFrame):
        """Fit AutoETS via statsforecast."""
        from statsforecast import StatsForecast
        from statsforecast.models import AutoETS

        sf_df = pd.DataFrame(
            {"unique_id": "game", "ds": df[self.date_col], "y": df[self.target_col]}
        )

        sf = StatsForecast(
            models=[AutoETS(season_length=self.seasonal_period)], freq="D", n_jobs=1
        )

        # Store for prediction
        return {"sf": sf, "df": sf_df, "model_type": "autoets"}

    def _fit_autoarima(self, df: pd.DataFrame):
        """Fit AutoARIMA via statsforecast."""
        from statsforecast import StatsForecast
        from statsforecast.models import AutoARIMA

        sf_df = pd.DataFrame(
            {"unique_id": "game", "ds": df[self.date_col], "y": df[self.target_col]}
        )

        sf = StatsForecast(
            models=[AutoARIMA(season_length=self.seasonal_period)], freq="D", n_jobs=1
        )

        return {"sf": sf, "df": sf_df, "model_type": "autoarima"}

    def _fit_prophet(self, df: pd.DataFrame):
        """Fit Facebook Prophet."""
        from prophet import Prophet

        prophet_df = df[[self.date_col, self.target_col]].copy()
        prophet_df.columns = ["ds", "y"]

        # Prepare holidays if sale events provided
        holidays_df = None
        if self.sale_events:
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

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            holidays=holidays_df,
        )
        model.fit(prophet_df)

        return model

    def _fit_lightgbm(self, df: pd.DataFrame):
        """Fit LightGBM with feature engineering."""
        import lightgbm as lgb
        from base import add_calendar_features, add_lag_features, add_rolling_features

        # Create features
        feat_df = df.copy()
        feat_df = add_calendar_features(feat_df, self.date_col)
        feat_df = add_lag_features(feat_df, self.target_col, [1, 7, 14, 28])
        feat_df = add_rolling_features(feat_df, self.target_col, [7, 14, 28])

        # Add sale features
        if self.sale_events:
            feat_df["is_sale"] = 0
            for event in self.sale_events:
                start = pd.to_datetime(event.start_date)
                end = pd.to_datetime(event.end_date)
                mask = (feat_df[self.date_col] >= start) & (
                    feat_df[self.date_col] <= end
                )
                feat_df.loc[mask, "is_sale"] = 1

        # Drop NaN rows from lag features
        feat_df = feat_df.dropna(subset=[f"{self.target_col}_lag_7"])

        # Define features
        exclude = [self.date_col, self.target_col, "game_name", "day_name", "sale_name"]
        feature_cols = [c for c in feat_df.columns if c not in exclude]

        X = feat_df[feature_cols]
        y = feat_df[self.target_col]

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

        model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            callbacks=[lgb.log_evaluation(period=0)],
        )

        return {
            "model": model,
            "feature_cols": feature_cols,
            "last_df": df.copy(),
        }

    def _fit_ensemble(self, df: pd.DataFrame):
        """Fit ensemble of multiple methods."""
        models = {}

        # Fit individual methods
        try:
            self._log("Fitting Holt-Winters...")
            models["holt_winters"] = self._fit_holt_winters(df)
        except Exception as e:
            self._log(f"Holt-Winters failed: {e}")

        try:
            self._log("Fitting AutoETS...")
            models["autoets"] = self._fit_autoets(df)
        except Exception as e:
            self._log(f"AutoETS failed: {e}")

        try:
            self._log("Fitting Prophet...")
            models["prophet"] = self._fit_prophet(df)
        except Exception as e:
            self._log(f"Prophet failed: {e}")

        if len(models) == 0:
            raise ValueError("All ensemble methods failed to fit")

        return {"models": models, "weights": None}  # Equal weights by default

    def fit(self, df: pd.DataFrame) -> "GameRevenueForecaster":
        """
        Fit the forecaster on training data.

        Parameters
        ----------
        df : pd.DataFrame
            Training data with date and revenue columns

        Returns
        -------
        self
        """
        start_time = time.time()

        df = df.sort_values(self.date_col).copy()
        self._train_df = df

        # Select method if auto
        if self.method == ForecastMethod.AUTO:
            self._selected_method = self._select_method(df)
        else:
            self._selected_method = self.method

        self._log(f"Using method: {self._selected_method.value}")

        # Fit the selected method
        if self._selected_method == ForecastMethod.HOLT_WINTERS:
            self._fitted_model = self._fit_holt_winters(df)
        elif self._selected_method == ForecastMethod.AUTOETS:
            self._fitted_model = self._fit_autoets(df)
        elif self._selected_method == ForecastMethod.AUTOARIMA:
            self._fitted_model = self._fit_autoarima(df)
        elif self._selected_method == ForecastMethod.PROPHET:
            self._fitted_model = self._fit_prophet(df)
        elif self._selected_method == ForecastMethod.LIGHTGBM:
            self._fitted_model = self._fit_lightgbm(df)
        elif self._selected_method == ForecastMethod.ENSEMBLE:
            self._fitted_model = self._fit_ensemble(df)
        else:
            raise ValueError(f"Unknown method: {self._selected_method}")

        self._train_time = time.time() - start_time
        self._log(f"Fit completed in {self._train_time:.2f}s")

        return self

    def _predict_holt_winters(self, n_periods: int) -> np.ndarray:
        """Generate Holt-Winters predictions."""
        return self._fitted_model.forecast(n_periods)

    def _predict_statsforecast(self, n_periods: int) -> np.ndarray:
        """Generate statsforecast predictions."""
        forecast = self._fitted_model["sf"].forecast(
            df=self._fitted_model["df"], h=n_periods
        )
        # Get the model column
        model_col = [c for c in forecast.columns if c not in ["unique_id", "ds"]][0]
        return forecast[model_col].values

    def _predict_prophet(self, n_periods: int) -> np.ndarray:
        """Generate Prophet predictions."""
        future = self._fitted_model.make_future_dataframe(periods=n_periods)
        forecast = self._fitted_model.predict(future)
        return forecast["yhat"].values[-n_periods:]

    def _predict_lightgbm(self, n_periods: int) -> np.ndarray:
        """Generate recursive LightGBM predictions."""
        import lightgbm as lgb
        from base import add_calendar_features, add_lag_features, add_rolling_features

        model = self._fitted_model["model"]
        feature_cols = self._fitted_model["feature_cols"]
        history = self._fitted_model["last_df"].copy()

        predictions = []
        last_date = history[self.date_col].max()

        for i in range(n_periods):
            next_date = last_date + pd.Timedelta(days=i + 1)

            # Create new row
            new_row = pd.DataFrame(
                {
                    self.date_col: [next_date],
                    self.target_col: [np.nan],
                    "game_name": [history["game_name"].iloc[0]]
                    if "game_name" in history.columns
                    else [""],
                }
            )

            # Combine and create features
            combined = pd.concat([history, new_row], ignore_index=True)
            combined = add_calendar_features(combined, self.date_col)
            combined = add_lag_features(combined, self.target_col, [1, 7, 14, 28])
            combined = add_rolling_features(combined, self.target_col, [7, 14, 28])

            if self.sale_events:
                combined["is_sale"] = 0
                for event in self.sale_events:
                    start = pd.to_datetime(event.start_date)
                    end = pd.to_datetime(event.end_date)
                    mask = (combined[self.date_col] >= start) & (
                        combined[self.date_col] <= end
                    )
                    combined.loc[mask, "is_sale"] = 1

            # Predict
            X_new = combined[combined[self.date_col] == next_date][feature_cols].fillna(
                0
            )
            pred = max(0, model.predict(X_new)[0])
            predictions.append(pred)

            # Update history
            new_row[self.target_col] = pred
            history = pd.concat([history, new_row], ignore_index=True)

        return np.array(predictions)

    def _predict_ensemble(self, n_periods: int) -> np.ndarray:
        """Generate ensemble predictions (simple average)."""
        models = self._fitted_model["models"]
        all_preds = []

        for name, model in models.items():
            try:
                if name == "holt_winters":
                    preds = model.forecast(n_periods)
                elif name in ["autoets", "autoarima"]:
                    forecast = model["sf"].forecast(df=model["df"], h=n_periods)
                    model_col = [
                        c for c in forecast.columns if c not in ["unique_id", "ds"]
                    ][0]
                    preds = forecast[model_col].values
                elif name == "prophet":
                    future = model.make_future_dataframe(periods=n_periods)
                    forecast = model.predict(future)
                    preds = forecast["yhat"].values[-n_periods:]
                else:
                    continue
                all_preds.append(preds)
            except Exception as e:
                self._log(f"Ensemble {name} prediction failed: {e}")

        if not all_preds:
            raise ValueError("All ensemble methods failed to predict")

        return np.mean(all_preds, axis=0)

    def predict(self, n_periods: int) -> np.ndarray:
        """
        Generate point forecasts.

        Parameters
        ----------
        n_periods : int
            Number of periods to forecast

        Returns
        -------
        np.ndarray
            Point forecasts
        """
        if self._fitted_model is None:
            raise ValueError("Must call fit() before predict()")

        if self._selected_method == ForecastMethod.HOLT_WINTERS:
            preds = self._predict_holt_winters(n_periods)
        elif self._selected_method in [
            ForecastMethod.AUTOETS,
            ForecastMethod.AUTOARIMA,
        ]:
            preds = self._predict_statsforecast(n_periods)
        elif self._selected_method == ForecastMethod.PROPHET:
            preds = self._predict_prophet(n_periods)
        elif self._selected_method == ForecastMethod.LIGHTGBM:
            preds = self._predict_lightgbm(n_periods)
        elif self._selected_method == ForecastMethod.ENSEMBLE:
            preds = self._predict_ensemble(n_periods)
        else:
            raise ValueError(f"Unknown method: {self._selected_method}")

        # Ensure non-negative
        return np.maximum(0, preds)

    def predict_with_intervals(
        self,
        n_periods: int,
        coverage: float = 0.90,
        calibration_size: int = 30,
    ) -> ForecastResult:
        """
        Generate forecasts with prediction intervals.

        Parameters
        ----------
        n_periods : int
            Number of periods to forecast
        coverage : float
            Coverage probability (default 0.90)
        calibration_size : int
            Number of recent periods to use for calibration

        Returns
        -------
        ForecastResult
            Forecast with prediction intervals
        """
        if self._fitted_model is None:
            raise ValueError("Must call fit() before predict_with_intervals()")

        # Generate forecast dates
        last_date = self._train_df[self.date_col].max()
        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1), periods=n_periods, freq="D"
        )

        # Use a portion of training data for calibration
        train_df = self._train_df.copy()
        if len(train_df) > calibration_size:
            cal_df = train_df.iloc[-calibration_size:].copy()
            fit_df = train_df.iloc[:-calibration_size].copy()
        else:
            # Not enough data, use full train for both
            cal_df = train_df.copy()
            fit_df = train_df.copy()

        # Refit on fit_df and predict on cal_df for calibration
        temp_forecaster = GameRevenueForecaster(
            method=self._selected_method,
            date_col=self.date_col,
            target_col=self.target_col,
            sale_events=self.sale_events,
            seasonal_period=self.seasonal_period,
        )
        temp_forecaster.fit(fit_df)
        cal_preds = temp_forecaster.predict(len(cal_df))
        cal_actuals = cal_df[self.target_col].values

        # Fit interval estimator
        interval_est = ConformalInterval(coverage=coverage, symmetric=True)
        interval_est.fit(cal_actuals, cal_preds)

        # Generate forecast
        predictions = self.predict(n_periods)
        lower, upper = interval_est.predict_interval(predictions)

        return ForecastResult(
            dates=forecast_dates,
            predictions=predictions,
            lower=lower,
            upper=upper,
            coverage=coverage,
            method=self._selected_method.value,
            train_time=self._train_time,
        )

    def get_method_info(self) -> Dict[str, Any]:
        """Get information about the fitted model."""
        return {
            "selected_method": self._selected_method.value
            if self._selected_method
            else None,
            "requested_method": self.method.value,
            "train_time": self._train_time,
            "train_samples": len(self._train_df) if self._train_df is not None else 0,
            "fitted": self._fitted_model is not None,
        }


# =============================================================================
# QUICK FORECAST FUNCTIONS
# =============================================================================


def quick_forecast(
    df: pd.DataFrame,
    n_periods: int = 30,
    date_col: str = "date",
    target_col: str = "revenue",
    method: str = "auto",
    with_intervals: bool = True,
    coverage: float = 0.90,
) -> Union[np.ndarray, ForecastResult]:
    """
    Quick forecasting function for simple use cases.

    Parameters
    ----------
    df : pd.DataFrame
        Historical data
    n_periods : int
        Forecast horizon
    date_col : str
        Date column name
    target_col : str
        Target column name
    method : str
        Forecasting method
    with_intervals : bool
        Whether to include prediction intervals
    coverage : float
        Coverage for intervals

    Returns
    -------
    np.ndarray or ForecastResult
        Forecasts, optionally with intervals

    Examples
    --------
    >>> from forecaster import quick_forecast
    >>> preds = quick_forecast(df, n_periods=30, with_intervals=False)
    >>> result = quick_forecast(df, n_periods=30, with_intervals=True)
    >>> print(result.to_dataframe())
    """
    forecaster = GameRevenueForecaster(
        method=method,
        date_col=date_col,
        target_col=target_col,
    )
    forecaster.fit(df)

    if with_intervals:
        return forecaster.predict_with_intervals(n_periods, coverage)
    else:
        return forecaster.predict(n_periods)


def forecast_all_games(
    df: pd.DataFrame,
    n_periods: int = 30,
    game_col: str = "game_name",
    date_col: str = "date",
    target_col: str = "revenue",
    method: str = "auto",
    with_intervals: bool = True,
    coverage: float = 0.90,
) -> Dict[str, ForecastResult]:
    """
    Forecast for all games in a dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Historical data for all games
    n_periods : int
        Forecast horizon
    game_col : str
        Column identifying different games
    date_col : str
        Date column name
    target_col : str
        Target column name
    method : str
        Forecasting method
    with_intervals : bool
        Whether to include prediction intervals
    coverage : float
        Coverage for intervals

    Returns
    -------
    Dict[str, ForecastResult]
        Dictionary mapping game name to forecast result
    """
    results = {}

    for game in df[game_col].unique():
        game_df = df[df[game_col] == game].copy()

        try:
            result = quick_forecast(
                game_df,
                n_periods=n_periods,
                date_col=date_col,
                target_col=target_col,
                method=method,
                with_intervals=with_intervals,
                coverage=coverage,
            )

            if isinstance(result, ForecastResult):
                results[game] = result
            else:
                # Wrap plain predictions
                last_date = game_df[date_col].max()
                dates = pd.date_range(
                    start=last_date + pd.Timedelta(days=1), periods=n_periods, freq="D"
                )
                results[game] = ForecastResult(
                    dates=dates,
                    predictions=result,
                    method=method,
                )
        except Exception as e:
            print(f"Warning: Failed to forecast {game}: {e}")

    return results


# =============================================================================
# MAIN / DEMO
# =============================================================================

if __name__ == "__main__":
    from base import generate_all_games_data, time_series_split

    print("Game Revenue Forecaster Demo")
    print("=" * 60)

    # Generate data
    print("\nGenerating synthetic data...")
    df = generate_all_games_data()

    # Pick one game
    game_name = "Eternal Legends"
    game_df = df[df["game_name"] == game_name].copy()

    print(f"\nForecasting for: {game_name}")
    print(f"Data: {len(game_df)} days")

    # Split
    train, test = time_series_split(game_df, 30)

    print("\n1. Auto Method Selection:")
    print("-" * 40)
    forecaster = GameRevenueForecaster(method="auto", verbose=True)
    forecaster.fit(train)

    result = forecaster.predict_with_intervals(30)
    print(f"\nResult: {result}")
    print(f"\nForecast DataFrame:")
    print(result.to_dataframe().head(10))

    # Evaluate
    y_true = test["revenue"].values
    y_pred = result.predictions

    from base import mape, rmse

    print(f"\nEvaluation on 30-day holdout:")
    print(f"  MAPE: {mape(y_true, y_pred):.2f}%")
    print(f"  RMSE: ${rmse(y_true, y_pred):,.0f}")

    # Check interval coverage
    metrics = evaluate_coverage(y_true, result.lower, result.upper)
    print(
        f"  Interval coverage: {metrics['coverage']:.1%} (target: {result.coverage:.0%})"
    )

    print("\n2. Quick Forecast for All Games:")
    print("-" * 40)

    results = forecast_all_games(df, n_periods=30, method="holt_winters")
    for game, res in results.items():
        print(f"  {game}: method={res.method}, first_pred=${res.predictions[0]:,.0f}")

    print("\n3. Specific Method Comparison:")
    print("-" * 40)

    for method in ["holt_winters", "autoets", "prophet"]:
        try:
            forecaster = GameRevenueForecaster(method=method)
            forecaster.fit(train)
            preds = forecaster.predict(30)
            print(f"  {method}: MAPE = {mape(y_true, preds):.2f}%")
        except Exception as e:
            print(f"  {method}: FAILED - {str(e)[:50]}")

    print("\n" + "=" * 60)
    print("Forecaster API Usage Summary:")
    print("=" * 60)
    print("""
# Simple usage:
forecaster = GameRevenueForecaster()
forecaster.fit(train_df)
predictions = forecaster.predict(30)

# With intervals:
result = forecaster.predict_with_intervals(30, coverage=0.90)
print(result.to_dataframe())

# Quick one-liner:
result = quick_forecast(df, n_periods=30)

# All games at once:
results = forecast_all_games(df, n_periods=30)
""")
