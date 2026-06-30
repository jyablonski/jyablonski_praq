"""
E-Commerce Forecast Engine

End-to-end forecasting pipeline for e-commerce product sales:
1. Generate synthetic daily sales data for 4 products with configurable history
2. Evaluate data quality (sufficient / limited / insufficient)
3. Select forecasting model based on data characteristics
4. Dynamically assess Prophet hyperparameters per product (log-transform,
   changepoint flexibility, seasonality Fourier orders, etc.)
5. Train Prophet model with exogenous regressors (sales events, marketing pushes)
6. Generate forecasts with prediction intervals
7. Create decay-curve features for event aftereffects

Gotchas and Notes:
- Prophet requires at least ~14 days of data for any useful signal
- Weekly seasonality is strong in e-commerce (weekend spikes)
- Sales events and marketing pushes are modeled as binary regressors
- Decay curves capture the lingering effect after an event ends
- Model selection tiers: simple_trend (<90d), holt_winters (90-179d),
  prophet/sarima (>=180d with seasonality)
- Dynamic tuning adapts to each product's volume, noise, trend strength,
  and available history length via _assess_prophet_hyperparams()
"""

import time
import warnings
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

warnings.filterwarnings("ignore")

# Set random seed for reproducibility
np.random.seed(42)


# =============================================================================
# DATA CLASSES AND CONFIGURATION
# =============================================================================


class HistoryLength(str, Enum):
    """Available history lengths for sample data generation."""

    THIRTY_DAYS = "30d"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"


class DataQuality(str, Enum):
    """Data quality tiers from evaluate_data_quality."""

    SUFFICIENT = "sufficient"
    LIMITED = "limited"
    INSUFFICIENT = "insufficient"


class ModelType(str, Enum):
    """Available model types from select_model."""

    PROPHET = "prophet"
    SARIMA = "sarima"
    HOLT_WINTERS = "holt_winters"
    SIMPLE_TREND = "simple_trend"


@dataclass
class ProductConfig:
    """Configuration for a synthetic e-commerce product."""

    product_id: str
    name: str
    category: str
    base_daily_sales: float
    weekend_boost: float = 0.20
    noise_level: float = 0.12
    trend_slope: float = 0.0  # daily trend (positive = growing)
    seasonality_amplitude: float = 0.10  # strength of yearly seasonality


@dataclass
class EventConfig:
    """Configuration for a sales event or marketing push."""

    name: str
    event_type: str  # 'sales_event' or 'marketing_push'
    start_date: str
    end_date: str
    boost_multiplier: float = 1.5


@dataclass
class ProphetConfig:
    """Dynamically-determined Prophet hyperparameters.

    Populated by _assess_prophet_hyperparams() based on data
    characteristics rather than hard-coded values.
    """

    changepoint_prior_scale: float = 0.05
    seasonality_prior_scale: float = 10.0
    seasonality_mode: str = "multiplicative"
    yearly_seasonality: bool = True
    yearly_fourier_order: int = 10
    weekly_seasonality: bool = True
    weekly_fourier_order: int = 3
    use_log_transform: bool = False
    n_changepoints: int = 25
    interval_width: float = 0.90


@dataclass
class ForecastResult:
    """Container for forecast output."""

    product_id: str
    product_name: str
    model_type: str
    data_quality: str
    forecast_df: pd.DataFrame
    train_df: Optional[pd.DataFrame] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    train_time_sec: float = 0.0


# =============================================================================
# SAMPLE DATA GENERATION
# =============================================================================


def get_default_products() -> List[ProductConfig]:
    """
    Get default configurations for 4 e-commerce products.

    Returns
    -------
    List[ProductConfig]
        Configurations spanning different product archetypes:
        1. Wireless Headphones - steady seller, moderate weekend boost
        2. Running Shoes - growing trend, strong seasonality
        3. Coffee Maker - stable, low noise, mild weekend effect
        4. Phone Case - high volume, high variance, strong weekends
    """
    return [
        ProductConfig(
            product_id="SKU-001",
            name="Wireless Headphones",
            category="Electronics",
            base_daily_sales=150.0,
            weekend_boost=0.18,
            noise_level=0.10,
            trend_slope=0.05,
            seasonality_amplitude=0.08,
        ),
        ProductConfig(
            product_id="SKU-002",
            name="Running Shoes",
            category="Footwear",
            base_daily_sales=85.0,
            weekend_boost=0.25,
            noise_level=0.14,
            trend_slope=0.12,
            seasonality_amplitude=0.15,
        ),
        ProductConfig(
            product_id="SKU-003",
            name="Coffee Maker",
            category="Home & Kitchen",
            base_daily_sales=45.0,
            weekend_boost=0.10,
            noise_level=0.08,
            trend_slope=-0.02,
            seasonality_amplitude=0.12,
        ),
        ProductConfig(
            product_id="SKU-004",
            name="Phone Case",
            category="Accessories",
            base_daily_sales=320.0,
            weekend_boost=0.30,
            noise_level=0.18,
            trend_slope=0.08,
            seasonality_amplitude=0.05,
        ),
    ]


def _history_length_to_days(history: HistoryLength) -> int:
    """Convert a HistoryLength enum to an integer day count."""
    mapping = {
        HistoryLength.THIRTY_DAYS: 30,
        HistoryLength.SIX_MONTHS: 183,
        HistoryLength.ONE_YEAR: 365,
        HistoryLength.TWO_YEARS: 730,
    }
    return mapping[history]


def _generate_events_for_range(
    start_date: pd.Timestamp, end_date: pd.Timestamp
) -> List[EventConfig]:
    """
    Generate realistic sales events and marketing pushes for a date range.

    Creates events that fall within the given range, including recurring
    seasonal sales and sporadic marketing pushes.

    Parameters
    ----------
    start_date : pd.Timestamp
        First date in the dataset
    end_date : pd.Timestamp
        Last date in the dataset

    Returns
    -------
    List[EventConfig]
        Events that overlap with [start_date, end_date]
    """
    # Define a pool of recurring annual events
    annual_events = [
        ("Valentine's Day Sale", "02-10", "02-15", "sales_event", 1.6),
        ("Spring Clearance", "03-20", "03-27", "sales_event", 1.4),
        ("Summer Sale", "06-20", "07-04", "sales_event", 1.8),
        ("Back to School", "08-15", "08-25", "sales_event", 1.5),
        ("Black Friday", "11-24", "11-30", "sales_event", 2.2),
        ("Holiday Season Sale", "12-15", "12-31", "sales_event", 2.0),
        ("New Year Push", "01-02", "01-10", "marketing_push", 1.3),
        ("Spring Launch Campaign", "04-01", "04-07", "marketing_push", 1.4),
        ("Mid-Year Marketing Blitz", "07-10", "07-17", "marketing_push", 1.3),
        ("Fall Product Launch", "09-15", "09-22", "marketing_push", 1.5),
    ]

    events = []
    for year in range(start_date.year, end_date.year + 1):
        for name, mm_dd_start, mm_dd_end, etype, boost in annual_events:
            try:
                evt_start = pd.Timestamp(f"{year}-{mm_dd_start}")
                evt_end = pd.Timestamp(f"{year}-{mm_dd_end}")
            except ValueError:
                continue

            # Only include if the event overlaps with our date range
            if evt_end >= start_date and evt_start <= end_date:
                events.append(
                    EventConfig(
                        name=f"{name} {year}",
                        event_type=etype,
                        start_date=max(evt_start, start_date).strftime("%Y-%m-%d"),
                        end_date=min(evt_end, end_date).strftime("%Y-%m-%d"),
                        boost_multiplier=boost,
                    )
                )

    return events


def generate_product_data(
    config: ProductConfig,
    history: HistoryLength = HistoryLength.ONE_YEAR,
    end_date: str = "2026-01-31",
    events: Optional[List[EventConfig]] = None,
) -> pd.DataFrame:
    """
    Generate synthetic daily sales data for a single product.

    Combines:
    - Linear trend
    - Yearly sinusoidal seasonality
    - Day-of-week effects (weekend boost)
    - Sales event / marketing push multipliers
    - Random noise

    Parameters
    ----------
    config : ProductConfig
        Product configuration
    history : HistoryLength
        How many days of history to generate
    end_date : str
        End date for the series (YYYY-MM-DD)
    events : List[EventConfig], optional
        Events to overlay. Auto-generated if None.

    Returns
    -------
    pd.DataFrame
        Columns: date, product_id, product_name, category, sales,
        is_sales_event, is_marketing_push, day_of_week, month
    """
    n_days = _history_length_to_days(history)
    end = pd.Timestamp(end_date)
    start = end - pd.Timedelta(days=n_days - 1)
    dates = pd.date_range(start=start, end=end, freq="D")
    n = len(dates)
    t = np.arange(n, dtype=float)

    # --- base curve: trend + yearly seasonality ---
    trend = config.base_daily_sales + config.trend_slope * t
    yearly = (
        config.seasonality_amplitude
        * config.base_daily_sales
        * np.sin(2 * np.pi * t / 365)
    )
    sales = trend + yearly

    # --- day-of-week seasonality ---
    dow_factors = np.ones(n)
    for i, d in enumerate(dates):
        dow = d.weekday()
        if dow == 4:  # Friday
            dow_factors[i] = 1 + config.weekend_boost * 0.5
        elif dow == 5:  # Saturday
            dow_factors[i] = 1 + config.weekend_boost
        elif dow == 6:  # Sunday
            dow_factors[i] = 1 + config.weekend_boost * 0.8
        elif dow == 0:  # Monday dip
            dow_factors[i] = 1 - config.weekend_boost * 0.3
    sales = sales * dow_factors

    # --- events ---
    if events is None:
        events = _generate_events_for_range(start, end)

    is_sales_event = np.zeros(n, dtype=int)
    is_marketing_push = np.zeros(n, dtype=int)

    for evt in events:
        evt_start = pd.Timestamp(evt.start_date)
        evt_end = pd.Timestamp(evt.end_date)
        mask = (dates >= evt_start) & (dates <= evt_end)

        sales[mask] *= evt.boost_multiplier

        if evt.event_type == "sales_event":
            is_sales_event[mask] = 1
        elif evt.event_type == "marketing_push":
            is_marketing_push[mask] = 1

    # --- noise ---
    noise = np.random.normal(1.0, config.noise_level, n)
    noise = np.clip(noise, 0.5, 2.0)
    sales = sales * noise
    sales = np.maximum(sales, 0).round(0).astype(int)

    df = pd.DataFrame(
        {
            "date": dates,
            "product_id": config.product_id,
            "product_name": config.name,
            "category": config.category,
            "sales": sales,
            "is_sales_event": is_sales_event,
            "is_marketing_push": is_marketing_push,
            "day_of_week": dates.dayofweek,
            "month": dates.month,
        }
    )

    return df


def generate_ecommerce_dataset(
    history: HistoryLength = HistoryLength.ONE_YEAR,
    end_date: str = "2026-01-31",
    products: Optional[List[ProductConfig]] = None,
    events: Optional[List[EventConfig]] = None,
) -> pd.DataFrame:
    """
    Generate synthetic daily sales for all 4 e-commerce products.

    Parameters
    ----------
    history : HistoryLength
        How many days of history per product
    end_date : str
        End date for all series
    products : List[ProductConfig], optional
        Custom product configs (uses defaults if None)
    events : List[EventConfig], optional
        Custom events (auto-generated per range if None)

    Returns
    -------
    pd.DataFrame
        Combined dataset for all products
    """
    if products is None:
        products = get_default_products()

    frames = []
    for cfg in products:
        df = generate_product_data(
            cfg, history=history, end_date=end_date, events=events
        )
        frames.append(df)

    return pd.concat(frames, ignore_index=True)


# =============================================================================
# DATA QUALITY EVALUATION
# =============================================================================


def evaluate_data_quality(
    df: pd.DataFrame, date_col: str = "date", target_col: str = "sales"
) -> DataQuality:
    """
    Check whether a product's history is sufficient for forecasting.

    Criteria
    --------
    - insufficient: fewer than 14 rows, or >20 % missing dates in the range
    - limited:      14-89 rows (enough for trend, not seasonality)
    - sufficient:   90+ rows

    Parameters
    ----------
    df : pd.DataFrame
        Single-product data sorted by date
    date_col : str
        Date column name
    target_col : str
        Target column name

    Returns
    -------
    DataQuality
        One of 'sufficient', 'limited', 'insufficient'
    """
    row_count = len(df)

    if row_count < 14:
        return DataQuality.INSUFFICIENT

    # Check for gaps
    date_range = (df[date_col].max() - df[date_col].min()).days + 1
    coverage = row_count / date_range if date_range > 0 else 0

    if coverage < 0.80:
        return DataQuality.INSUFFICIENT

    # Check for excessive NaN / zero in target
    bad_rows = df[target_col].isna().sum() + (df[target_col] == 0).sum()
    if bad_rows / row_count > 0.30:
        return DataQuality.INSUFFICIENT

    if row_count < 90:
        return DataQuality.LIMITED

    return DataQuality.SUFFICIENT


# =============================================================================
# MODEL SELECTION
# =============================================================================


def _detect_weekly_seasonality(
    df: pd.DataFrame, target_col: str = "sales", threshold: float = 0.03
) -> bool:
    """
    Detect whether a series has meaningful weekly seasonality.

    Uses two complementary tests and returns True if either passes:

    1. **MAD ratio**: mean absolute deviation of day-of-week group means
       divided by the overall mean. Catches broad weekend-vs-weekday shifts.
    2. **Weekend-vs-weekday t-like ratio**: difference of weekend and weekday
       means divided by pooled std-error. Catches concentrated Fri/Sat/Sun
       effects even when the MAD across all 7 DOW groups is mild.

    The ``threshold`` applies to the MAD ratio test. The t-ratio test uses
    a fixed threshold of 2.0 (roughly p < 0.05 for moderate sample sizes).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'day_of_week' and `target_col` columns
    target_col : str
        Column to analyse
    threshold : float
        Minimum MAD-ratio to declare weekly seasonality present

    Returns
    -------
    bool
    """
    if "day_of_week" not in df.columns:
        return False

    overall_mean = df[target_col].mean()
    if overall_mean == 0:
        return False

    dow_means = df.groupby("day_of_week")[target_col].mean()
    mad = (dow_means - overall_mean).abs().mean()

    if (mad / overall_mean) > threshold:
        return True

    # Fallback: weekend (Fri-Sun) vs weekday (Mon-Thu) comparison
    weekend_mask = df["day_of_week"].isin([4, 5, 6])
    weekday_mask = ~weekend_mask
    weekend_vals = df.loc[weekend_mask, target_col]
    weekday_vals = df.loc[weekday_mask, target_col]

    if len(weekend_vals) < 5 or len(weekday_vals) < 5:
        return False

    diff = weekend_vals.mean() - weekday_vals.mean()
    pooled_se = np.sqrt(
        weekend_vals.var() / len(weekend_vals) + weekday_vals.var() / len(weekday_vals)
    )
    if pooled_se > 0 and abs(diff) / pooled_se > 2.0:
        return True

    return False


def select_model(
    df: pd.DataFrame,
    data_quality: DataQuality,
    target_col: str = "sales",
) -> Optional[ModelType]:
    """
    Pick a forecasting model based on data characteristics.

    Decision tree
    -------------
    1. insufficient data  -> None (skip)
    2. < 90 rows          -> simple_trend (exponential smoothing, no seasonality)
    3. 90-179 rows        -> holt_winters (weekly seasonality, no yearly)
    4. >= 180 rows + weekly seasonality + has events -> prophet
    5. >= 180 rows + weekly seasonality, no events   -> sarima
    6. otherwise          -> holt_winters

    The Prophet threshold is 180 days (not 365) because
    ``_assess_prophet_hyperparams`` dynamically adapts Fourier orders and
    disables yearly seasonality when history is too short for it.

    Parameters
    ----------
    df : pd.DataFrame
        Single-product data
    data_quality : DataQuality
        Result of evaluate_data_quality
    target_col : str
        Target column name

    Returns
    -------
    ModelType or None
    """
    if data_quality == DataQuality.INSUFFICIENT:
        return None

    row_count = len(df)

    if row_count < 90:
        return ModelType.SIMPLE_TREND

    if row_count >= 180:
        has_weekly = _detect_weekly_seasonality(df, target_col)
        if has_weekly:
            has_events = (
                df.get("is_sales_event", pd.Series(dtype=int)).sum() > 0
                or df.get("is_marketing_push", pd.Series(dtype=int)).sum() > 0
            )
            return ModelType.PROPHET if has_events else ModelType.SARIMA

    return ModelType.HOLT_WINTERS


# =============================================================================
# EXOGENOUS FEATURE CREATION (DECAY CURVES)
# =============================================================================


def _default_decay_curve(peak: float = 1.0, length: int = 14) -> np.ndarray:
    """
    Generate an exponential decay curve.

    Parameters
    ----------
    peak : float
        Initial effect magnitude on event day
    length : int
        Number of days the effect lingers

    Returns
    -------
    np.ndarray
        Array of length `length` with exponentially decaying values
    """
    t = np.arange(length)
    return peak * np.exp(-t / (length / 3))


def create_exog_features(
    dates: pd.DatetimeIndex,
    events: List[EventConfig],
    decay_length: int = 14,
) -> pd.DataFrame:
    """
    Convert events into continuous decay variables.

    For each event type ('sales_event', 'marketing_push'), creates a
    column whose value is the additive sum of all overlapping decay
    curves on each date.

    Parameters
    ----------
    dates : pd.DatetimeIndex
        Full date index (train + forecast horizon)
    events : List[EventConfig]
        Events to convert
    decay_length : int
        How many days the aftereffect lasts

    Returns
    -------
    pd.DataFrame
        Columns: date, sales_event_effect, marketing_push_effect
    """
    features = pd.DataFrame({"date": dates})
    features["sales_event_effect"] = 0.0
    features["marketing_push_effect"] = 0.0

    decay_curves = {
        "sales_event": _default_decay_curve(peak=1.0, length=decay_length),
        "marketing_push": _default_decay_curve(peak=0.7, length=decay_length),
    }

    for evt in events:
        curve = decay_curves.get(evt.event_type, _default_decay_curve())
        col = f"{evt.event_type}_effect"

        evt_end = pd.Timestamp(evt.end_date)

        for i, d in enumerate(dates):
            days_since_end = (d - evt_end).days
            if 0 <= days_since_end < len(curve):
                features.loc[i, col] += curve[days_since_end]

    return features


# =============================================================================
# DYNAMIC PROPHET HYPERPARAMETER ASSESSMENT
# =============================================================================


def _assess_prophet_hyperparams(
    df: pd.DataFrame, target_col: str = "sales"
) -> ProphetConfig:
    """
    Inspect a product's time series and dynamically choose Prophet
    hyperparameters based on data characteristics.

    Assessed signals
    ----------------
    - **Volume & scale**: mean daily sales. Low-volume series benefit from
      log-transform to stabilise variance and let Prophet learn proportional
      patterns.
    - **Coefficient of variation (CV)**: std/mean. High CV means noisy data;
      we loosen the changepoint prior so the model can track shifts, and
      tighten seasonality prior so it doesn't overfit noise as season.
    - **History length**: with < 2 full annual cycles, yearly seasonality
      is underfit; we reduce Fourier order to avoid overfitting the single
      cycle and increase n_changepoints so the model can still track
      structural shifts.
    - **Weekend effect strength**: measured as ratio of weekend mean to
      weekday mean. Strong effects get higher weekly Fourier order.
    - **Trend strength**: slope of OLS fit relative to mean. Strong trends
      need a looser changepoint prior so Prophet doesn't smooth them away.

    Parameters
    ----------
    df : pd.DataFrame
        Single-product training data with ``date``, ``target_col``,
        ``day_of_week`` columns.
    target_col : str
        Name of the target column.

    Returns
    -------
    ProphetConfig
        Dynamically-tuned configuration ready for ``_fit_prophet``.
    """
    config = ProphetConfig()
    series = df[target_col].astype(float)
    n_rows = len(df)
    mean_sales = series.mean()
    std_sales = series.std()
    cv = std_sales / mean_sales if mean_sales > 0 else 0.0

    # --- Log transform decision ---
    # Low-volume products benefit from log space: Prophet learns
    # multiplicative patterns more cleanly and prediction intervals
    # scale proportionally instead of being constant-width.
    if mean_sales < 200 and mean_sales > 0:
        config.use_log_transform = True

    # --- Changepoint prior scale ---
    # Default 0.05 is too tight for noisy / trending series.
    # Scale it by CV so noisy products get a more flexible trend.
    if cv > 0.25:
        config.changepoint_prior_scale = 0.15
    elif cv > 0.15:
        config.changepoint_prior_scale = 0.10
    else:
        config.changepoint_prior_scale = 0.05

    # Strong linear trend also warrants a looser prior
    if n_rows >= 30:
        t = np.arange(n_rows, dtype=float)
        slope = np.polyfit(t, series.values, 1)[0]
        trend_ratio = abs(slope * n_rows) / mean_sales if mean_sales > 0 else 0
        if trend_ratio > 0.20:
            config.changepoint_prior_scale = max(config.changepoint_prior_scale, 0.12)

    # --- Number of changepoints ---
    # More changepoints for longer series, fewer for short ones
    if n_rows >= 500:
        config.n_changepoints = 35
    elif n_rows >= 365:
        config.n_changepoints = 25
    else:
        config.n_changepoints = max(10, n_rows // 15)

    # --- Yearly seasonality ---
    # Need at least ~300 days for yearly to be meaningful.
    # With < 2 full cycles, use a low Fourier order to avoid overfitting.
    if n_rows < 300:
        config.yearly_seasonality = False
        config.yearly_fourier_order = 0
    elif n_rows < 600:
        config.yearly_fourier_order = 6  # conservative with 1 cycle
    else:
        config.yearly_fourier_order = 10  # 2+ cycles, can use more

    # --- Weekly seasonality ---
    # Measure weekend vs weekday strength to set Fourier order
    if "day_of_week" in df.columns:
        weekend_mask = df["day_of_week"].isin([5, 6])
        weekday_mask = df["day_of_week"].isin([0, 1, 2, 3, 4])
        weekend_mean = series[weekend_mask].mean()
        weekday_mean = series[weekday_mask].mean()

        if weekday_mean > 0:
            weekend_ratio = weekend_mean / weekday_mean
        else:
            weekend_ratio = 1.0

        if weekend_ratio > 1.15:
            config.weekly_fourier_order = 4  # strong DOW pattern
        elif weekend_ratio > 1.05:
            config.weekly_fourier_order = 3
        else:
            config.weekly_fourier_order = 2  # weak weekend effect
    else:
        config.weekly_fourier_order = 3

    # --- Seasonality prior scale ---
    # High CV = noisy; tighten seasonality so it doesn't overfit noise
    # Low CV  = clean signal; loosen so seasonality can express fully
    if cv > 0.25:
        config.seasonality_prior_scale = 5.0
    elif cv < 0.12:
        config.seasonality_prior_scale = 15.0
    else:
        config.seasonality_prior_scale = 10.0

    # --- Seasonality mode ---
    # When log-transforming, the data is already in "additive-like" space
    # (log turns multiplicative relationships into additive ones), so we
    # MUST use additive seasonality to avoid Jensen's inequality bias that
    # inflates forecasts after expm1 back-transform.
    # Without log-transform, multiplicative handles scale-proportional
    # patterns better, but very low volume products still benefit from
    # additive to avoid instability.
    if config.use_log_transform:
        config.seasonality_mode = "additive"
    elif mean_sales < 50:
        config.seasonality_mode = "additive"

    return config


# =============================================================================
# TRAIN AND FORECAST
# =============================================================================


def _fit_simple_trend(
    train_df: pd.DataFrame, horizon: int, target_col: str = "sales"
) -> pd.DataFrame:
    """
    Simple exponential smoothing forecast (no seasonality).

    Used when history is too short for seasonal models.

    Parameters
    ----------
    train_df : pd.DataFrame
        Training data
    horizon : int
        Forecast horizon in days
    target_col : str
        Target column

    Returns
    -------
    pd.DataFrame
        Columns: ds, yhat, yhat_lower, yhat_upper
    """
    from statsmodels.tsa.holtwinters import SimpleExpSmoothing

    series = train_df.set_index("date")[target_col].astype(float)
    series.index = pd.DatetimeIndex(series.index)
    series.index.freq = "D"

    model = SimpleExpSmoothing(series).fit(optimized=True)
    forecast_values = model.forecast(horizon)

    last_date = train_df["date"].max()
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D"
    )

    # Simple interval: +/- 1.5 * residual std
    residuals = series.values - model.fittedvalues.values
    sigma = np.std(residuals)

    return pd.DataFrame(
        {
            "ds": future_dates,
            "yhat": forecast_values.values,
            "yhat_lower": forecast_values.values - 1.5 * sigma,
            "yhat_upper": forecast_values.values + 1.5 * sigma,
        }
    )


def _fit_holt_winters(
    train_df: pd.DataFrame,
    horizon: int,
    target_col: str = "sales",
    seasonal_period: int = 7,
) -> pd.DataFrame:
    """
    Holt-Winters additive model with weekly seasonality.

    Parameters
    ----------
    train_df : pd.DataFrame
        Training data
    horizon : int
        Forecast horizon in days
    target_col : str
        Target column
    seasonal_period : int
        Seasonal period (7 for weekly)

    Returns
    -------
    pd.DataFrame
        Columns: ds, yhat, yhat_lower, yhat_upper
    """
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    series = train_df.set_index("date")[target_col].astype(float)
    series.index = pd.DatetimeIndex(series.index)
    series.index.freq = "D"

    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=seasonal_period,
        damped_trend=True,
    ).fit()

    forecast_values = model.forecast(horizon)

    last_date = train_df["date"].max()
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D"
    )

    residuals = series.values - model.fittedvalues.values
    sigma = np.std(residuals)

    return pd.DataFrame(
        {
            "ds": future_dates,
            "yhat": forecast_values.values,
            "yhat_lower": forecast_values.values - 1.96 * sigma,
            "yhat_upper": forecast_values.values + 1.96 * sigma,
        }
    )


def _fit_prophet(
    train_df: pd.DataFrame,
    horizon: int,
    target_col: str = "sales",
    events: Optional[List[EventConfig]] = None,
) -> pd.DataFrame:
    """
    Facebook Prophet with dynamically-assessed hyperparameters.

    Uses ``_assess_prophet_hyperparams`` to inspect the series and choose
    changepoint flexibility, seasonality orders, log-transform, etc.
    Adds ``is_sales_event`` and ``is_marketing_push`` as extra regressors
    when events are provided.

    Parameters
    ----------
    train_df : pd.DataFrame
        Training data (must contain 'date', target_col,
        'is_sales_event', 'is_marketing_push')
    horizon : int
        Forecast horizon in days
    target_col : str
        Target column
    events : List[EventConfig], optional
        Events used to populate future regressor values

    Returns
    -------
    pd.DataFrame
        Columns: ds, yhat, yhat_lower, yhat_upper
    """
    from prophet import Prophet

    # --- dynamic assessment ---
    pcfg = _assess_prophet_hyperparams(train_df, target_col)

    prophet_df = train_df[["date", target_col]].copy()
    prophet_df.columns = ["ds", "y"]

    # Log-transform for low-volume / high-variance series
    if pcfg.use_log_transform:
        prophet_df["y"] = np.log1p(prophet_df["y"])

    has_event_cols = (
        "is_sales_event" in train_df.columns and "is_marketing_push" in train_df.columns
    )

    model = Prophet(
        growth="linear",
        yearly_seasonality=False,  # added manually below with Fourier order
        weekly_seasonality=False,  # added manually below with Fourier order
        daily_seasonality=False,
        seasonality_mode=pcfg.seasonality_mode,
        changepoint_prior_scale=pcfg.changepoint_prior_scale,
        seasonality_prior_scale=pcfg.seasonality_prior_scale,
        n_changepoints=pcfg.n_changepoints,
        interval_width=pcfg.interval_width,
    )

    # Add seasonalities with assessed Fourier orders
    if pcfg.yearly_seasonality:
        model.add_seasonality(
            name="yearly",
            period=365.25,
            fourier_order=pcfg.yearly_fourier_order,
            mode=pcfg.seasonality_mode,
        )

    if pcfg.weekly_seasonality:
        model.add_seasonality(
            name="weekly",
            period=7,
            fourier_order=pcfg.weekly_fourier_order,
            mode=pcfg.seasonality_mode,
        )

    if has_event_cols:
        prophet_df["is_sales_event"] = train_df["is_sales_event"].values
        prophet_df["is_marketing_push"] = train_df["is_marketing_push"].values
        model.add_regressor("is_sales_event", mode=pcfg.seasonality_mode)
        model.add_regressor("is_marketing_push", mode=pcfg.seasonality_mode)

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=horizon)

    if has_event_cols:
        future["is_sales_event"] = 0
        future["is_marketing_push"] = 0

        if events:
            for evt in events:
                evt_start = pd.Timestamp(evt.start_date)
                evt_end = pd.Timestamp(evt.end_date)
                mask = (future["ds"] >= evt_start) & (future["ds"] <= evt_end)
                if evt.event_type == "sales_event":
                    future.loc[mask, "is_sales_event"] = 1
                elif evt.event_type == "marketing_push":
                    future.loc[mask, "is_marketing_push"] = 1

    forecast = model.predict(future)
    forecast_future = forecast[forecast["ds"] > train_df["date"].max()].copy()

    # Reverse log-transform if applied
    if pcfg.use_log_transform:
        forecast_future["yhat"] = np.expm1(forecast_future["yhat"])
        forecast_future["yhat_lower"] = np.expm1(forecast_future["yhat_lower"])
        forecast_future["yhat_upper"] = np.expm1(forecast_future["yhat_upper"])

    return forecast_future[["ds", "yhat", "yhat_lower", "yhat_upper"]].reset_index(
        drop=True
    )


def train_and_forecast(
    df: pd.DataFrame,
    model_type: ModelType,
    horizon: int = 90,
    target_col: str = "sales",
    events: Optional[List[EventConfig]] = None,
) -> pd.DataFrame:
    """
    Train the selected model and generate predictions + intervals.

    Parameters
    ----------
    df : pd.DataFrame
        Training data
    model_type : ModelType
        Which model to fit
    horizon : int
        Number of days to forecast
    target_col : str
        Target column name
    events : List[EventConfig], optional
        Events for Prophet regressors

    Returns
    -------
    pd.DataFrame
        Columns: ds, yhat, yhat_lower, yhat_upper
    """
    if model_type == ModelType.SIMPLE_TREND:
        return _fit_simple_trend(df, horizon, target_col)

    if model_type == ModelType.HOLT_WINTERS:
        return _fit_holt_winters(df, horizon, target_col)

    if model_type in (ModelType.PROPHET, ModelType.SARIMA):
        # Use Prophet for both; SARIMA placeholder routes here too for
        # demonstration purposes. In production you'd swap in pmdarima.
        return _fit_prophet(df, horizon, target_col, events)

    raise ValueError(f"Unsupported model_type: {model_type}")


# =============================================================================
# EVALUATION HELPERS
# =============================================================================


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error (filters zeros)."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    mask = y_true != 0
    if mask.sum() == 0:
        return np.nan
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


# =============================================================================
# VISUALIZATION
# =============================================================================


def plot_product_forecast(
    train_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    product_name: str,
    target_col: str = "sales",
    figsize: Tuple[int, int] = (14, 6),
) -> plt.Figure:
    """
    Plot historical data alongside the forecast with prediction intervals.

    Parameters
    ----------
    train_df : pd.DataFrame
        Training data with 'date' and target columns
    forecast_df : pd.DataFrame
        Forecast output from train_and_forecast (ds, yhat, yhat_lower, yhat_upper)
    product_name : str
        Product name for the title
    target_col : str
        Target column in train_df
    figsize : tuple
        Figure dimensions

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Historical
    ax.plot(
        train_df["date"],
        train_df[target_col],
        color="steelblue",
        linewidth=1,
        alpha=0.8,
        label="Historical Sales",
    )

    # Highlight events
    if "is_sales_event" in train_df.columns:
        evt_mask = train_df["is_sales_event"] == 1
        if evt_mask.any():
            ax.scatter(
                train_df.loc[evt_mask, "date"],
                train_df.loc[evt_mask, target_col],
                color="red",
                s=12,
                alpha=0.6,
                label="Sales Event",
                zorder=5,
            )
    if "is_marketing_push" in train_df.columns:
        mkt_mask = train_df["is_marketing_push"] == 1
        if mkt_mask.any():
            ax.scatter(
                train_df.loc[mkt_mask, "date"],
                train_df.loc[mkt_mask, target_col],
                color="orange",
                s=12,
                alpha=0.6,
                label="Marketing Push",
                zorder=5,
            )

    # Forecast
    ax.plot(
        forecast_df["ds"],
        forecast_df["yhat"],
        color="darkgreen",
        linewidth=2,
        label="Forecast",
    )
    ax.fill_between(
        forecast_df["ds"],
        forecast_df["yhat_lower"],
        forecast_df["yhat_upper"],
        color="green",
        alpha=0.15,
        label="90% Interval",
    )

    # Split line
    split_date = train_df["date"].max()
    ax.axvline(x=split_date, color="gray", linestyle="--", alpha=0.6)

    ax.set_xlabel("Date")
    ax.set_ylabel("Units Sold")
    ax.set_title(f"{product_name} — Sales Forecast")
    ax.legend(loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_all_forecasts(
    results: List[ForecastResult],
    target_col: str = "sales",
    figsize: Tuple[int, int] = (16, 5),
    save_path: Optional[str] = None,
) -> List[plt.Figure]:
    """
    Plot every product's forecast from a pipeline run.

    Creates one figure per product showing historical data, the forecast
    line, the 90 % prediction interval band, and event markers.

    Parameters
    ----------
    results : List[ForecastResult]
        Output of run_forecast_pipeline
    target_col : str
        Target column in the training data
    figsize : tuple
        Dimensions of each individual figure
    save_path : str, optional
        If provided, save each figure as
        ``{save_path}/{product_id}_forecast.png``

    Returns
    -------
    List[plt.Figure]
        One figure per product that had a valid forecast
    """
    import os

    figs = []

    for r in results:
        if r.forecast_df.empty or r.train_df is None:
            print(f"  Skipping {r.product_id} ({r.product_name}) — no forecast")
            continue

        fig = plot_product_forecast(
            train_df=r.train_df,
            forecast_df=r.forecast_df,
            product_name=f"{r.product_name} [{r.model_type}]",
            target_col=target_col,
            figsize=figsize,
        )
        figs.append(fig)

        if save_path:
            os.makedirs(save_path, exist_ok=True)
            filepath = os.path.join(save_path, f"{r.product_id}_forecast.png")
            fig.savefig(filepath, dpi=150)
            print(f"  Saved {filepath}")

    return figs


# =============================================================================
# MAIN WORKFLOW
# =============================================================================


def run_forecast_pipeline(
    history: HistoryLength = HistoryLength.ONE_YEAR,
    end_date: str = "2026-01-31",
    horizon: int = 90,
    products: Optional[List[ProductConfig]] = None,
    verbose: bool = True,
) -> List[ForecastResult]:
    """
    Run the full e-commerce forecast pipeline for all products.

    Steps
    -----
    1. Generate (or receive) sample data
    2. For each product:
       a. Evaluate data quality
       b. Select model
       c. Train and forecast
       d. Collect results

    Parameters
    ----------
    history : HistoryLength
        Length of historical data to generate
    end_date : str
        End date for the data
    horizon : int
        Forecast horizon in days
    products : List[ProductConfig], optional
        Custom product configs
    verbose : bool
        Print progress

    Returns
    -------
    List[ForecastResult]
        One result per product
    """
    if products is None:
        products = get_default_products()

    # Generate dataset
    dataset = generate_ecommerce_dataset(
        history=history, end_date=end_date, products=products
    )

    # Derive events from the date range for future regressor values
    start_date = dataset["date"].min()
    end_horizon = pd.Timestamp(end_date) + pd.Timedelta(days=horizon)
    all_events = _generate_events_for_range(start_date, end_horizon)

    results: List[ForecastResult] = []

    for cfg in products:
        product_df = (
            dataset[dataset["product_id"] == cfg.product_id]
            .copy()
            .sort_values("date")
            .reset_index(drop=True)
        )

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Product: {cfg.name} ({cfg.product_id})")
            print(
                f"  Rows: {len(product_df)}  |  "
                f"Date range: {product_df['date'].min().date()} → "
                f"{product_df['date'].max().date()}"
            )

        # Step 1: evaluate quality
        quality = evaluate_data_quality(product_df)
        if verbose:
            print(f"  Data quality: {quality.value}")

        if quality == DataQuality.INSUFFICIENT:
            if verbose:
                print("  SKIPPED — insufficient data")
            results.append(
                ForecastResult(
                    product_id=cfg.product_id,
                    product_name=cfg.name,
                    model_type="none",
                    data_quality=quality.value,
                    forecast_df=pd.DataFrame(),
                    train_df=product_df,
                )
            )
            continue

        # Step 2: select model
        model_type = select_model(product_df, quality)
        if model_type is None:
            if verbose:
                print("  SKIPPED — no suitable model")
            results.append(
                ForecastResult(
                    product_id=cfg.product_id,
                    product_name=cfg.name,
                    model_type="none",
                    data_quality=quality.value,
                    forecast_df=pd.DataFrame(),
                    train_df=product_df,
                )
            )
            continue

        if verbose:
            print(f"  Selected model: {model_type.value}")

        # Log assessed hyperparams for Prophet / SARIMA (both use Prophet)
        if verbose and model_type in (ModelType.PROPHET, ModelType.SARIMA):
            pcfg = _assess_prophet_hyperparams(product_df)
            series = product_df["sales"].astype(float)
            cv = series.std() / series.mean() if series.mean() > 0 else 0
            print("  Assessed config:")
            print(f"    mean_sales={series.mean():.0f}  CV={cv:.3f}")
            print(
                f"    changepoint_prior={pcfg.changepoint_prior_scale}  "
                f"n_changepoints={pcfg.n_changepoints}"
            )
            print(
                f"    yearly_fourier={pcfg.yearly_fourier_order}  "
                f"weekly_fourier={pcfg.weekly_fourier_order}"
            )
            print(
                f"    seasonality_prior={pcfg.seasonality_prior_scale}  "
                f"mode={pcfg.seasonality_mode}"
            )
            print(f"    log_transform={pcfg.use_log_transform}")

        # Step 3: train and forecast
        start_time = time.time()
        forecast_df = train_and_forecast(
            df=product_df,
            model_type=model_type,
            horizon=horizon,
            events=all_events,
        )
        elapsed = time.time() - start_time

        if verbose:
            print(
                f"  Train + forecast in {elapsed:.2f}s  |  "
                f"Horizon: {len(forecast_df)} days"
            )
            print(
                f"  Forecast range: {forecast_df['ds'].min().date()} → "
                f"{forecast_df['ds'].max().date()}"
            )
            print(f"  Mean predicted sales: {forecast_df['yhat'].mean():.1f}")

        results.append(
            ForecastResult(
                product_id=cfg.product_id,
                product_name=cfg.name,
                model_type=model_type.value,
                data_quality=quality.value,
                forecast_df=forecast_df,
                train_df=product_df,
                train_time_sec=elapsed,
            )
        )

    return results


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("E-Commerce Forecast Engine")
    print("=" * 60)

    # ---- run pipeline for 1-year history and plot all products ----
    print("\nRunning pipeline with 1-year history...")
    results_1y = run_forecast_pipeline(
        history=HistoryLength.ONE_YEAR, horizon=90, verbose=True
    )

    print(f"\n{'=' * 60}")
    print("Generating forecast plots with prediction intervals...")
    print("=" * 60)
    figs = plot_all_forecasts(results_1y, save_path="output")
    print(f"\n{len(figs)} plots saved to output/")

    # ---- also run a quick comparison across all history lengths ----
    print(f"\n{'=' * 60}")
    print("Model selection across history lengths:")
    print("=" * 60)
    for hl in HistoryLength:
        n_days = _history_length_to_days(hl)
        results = run_forecast_pipeline(history=hl, horizon=90, verbose=False)
        print(f"\n  {hl.value} ({n_days} days):")
        for r in results:
            print(
                f"    {r.product_id} {r.product_name:>22s}  "
                f"quality={r.data_quality:<12s}  model={r.model_type}"
            )

    # ---- show a sample of the generated data ----
    print(f"\n{'=' * 60}")
    print("Sample generated data (Wireless Headphones, 1 year):")
    print("=" * 60)
    sample = generate_ecommerce_dataset(history=HistoryLength.ONE_YEAR)
    headphones = sample[sample["product_id"] == "SKU-001"].copy()
    print(headphones.head(15).to_string(index=False))

    print(f"\nSales events present: {headphones['is_sales_event'].sum()} days")
    print(f"Marketing pushes present: {headphones['is_marketing_push'].sum()} days")

    # ---- show exogenous decay features ----
    print(f"\n{'=' * 60}")
    print("Exogenous decay features (first 20 rows with non-zero effect):")
    print("=" * 60)
    end_ts = pd.Timestamp("2026-01-31")
    start_ts = end_ts - pd.Timedelta(days=364)
    dates = pd.date_range(start=start_ts, end=end_ts, freq="D")
    events = _generate_events_for_range(start_ts, end_ts)
    exog = create_exog_features(dates, events)
    print(exog[exog["sales_event_effect"] > 0].head(20).to_string(index=False))

    # ---- show the plots if running interactively ----
    plt.show()

    print("\nDone.")
