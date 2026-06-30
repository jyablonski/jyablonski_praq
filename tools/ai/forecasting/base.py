"""
Base module for game revenue forecasting experiments.

Contains:
- Synthetic game revenue data generators with realistic patterns
- Evaluation metrics (MAPE, RMSE, SMAPE)
- Time-aware train/test split utilities
- Visualization helpers for comparing predictions
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional, Callable
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dataclasses import dataclass
import warnings

# Set random seed for reproducibility
np.random.seed(42)


# =============================================================================
# DATA CLASSES AND CONFIGURATION
# =============================================================================


@dataclass
class GameConfig:
    """Configuration for synthetic game revenue generation."""

    name: str
    game_type: str  # 'new_launch', 'mature', 'live_service'
    start_date: str
    base_revenue: float
    launch_multiplier: float = 5.0
    decay_rate: float = 0.003
    weekend_boost: float = 0.15
    noise_level: float = 0.1
    sale_boost: float = 0.4
    content_drop_boost: float = 0.25
    content_drop_interval_days: int = 45  # For live service games


@dataclass
class SaleEvent:
    """Represents a sale event that boosts revenue."""

    name: str
    start_date: str
    end_date: str
    discount_pct: float
    revenue_multiplier: float


# =============================================================================
# SYNTHETIC DATA GENERATION
# =============================================================================


def generate_base_revenue_curve(
    days: int,
    base_revenue: float,
    launch_multiplier: float,
    decay_rate: float,
    game_type: str,
) -> np.ndarray:
    """
    Generate the base revenue curve based on game type.

    - New launch: High initial spike with exponential decay
    - Mature: Stable with slow decline
    - Live service: Periodic bumps from content drops
    """
    t = np.arange(days)

    if game_type == "new_launch":
        # Sharp launch spike with exponential decay, stabilizing at ~30% of base
        spike = launch_multiplier * np.exp(-decay_rate * t)
        floor = 0.3
        revenue = base_revenue * (spike + floor)

    elif game_type == "mature":
        # Stable with very slow decline (mature title past its peak)
        slow_decay = 1.0 - (t / days) * 0.2  # 20% decline over period
        seasonal_trend = 0.05 * np.sin(2 * np.pi * t / 365)  # Yearly seasonality
        revenue = base_revenue * (slow_decay + seasonal_trend)

    elif game_type == "live_service":
        # Base with periodic content drop bumps
        base = np.ones(days) * base_revenue
        # Add gradual engagement decay between content drops
        micro_decay = 0.95 + 0.05 * np.cos(2 * np.pi * t / 45)
        revenue = base * micro_decay

    else:
        revenue = np.ones(days) * base_revenue

    return revenue


def add_weekly_seasonality(
    revenue: np.ndarray, start_date: datetime, weekend_boost: float
) -> np.ndarray:
    """Add day-of-week seasonality (weekends are higher)."""
    days = len(revenue)
    seasonality = np.ones(days)

    for i in range(days):
        date = start_date + timedelta(days=i)
        dow = date.weekday()

        if dow == 4:  # Friday
            seasonality[i] = 1 + weekend_boost * 0.5
        elif dow == 5:  # Saturday
            seasonality[i] = 1 + weekend_boost
        elif dow == 6:  # Sunday
            seasonality[i] = 1 + weekend_boost * 0.8
        elif dow == 0:  # Monday (post-weekend dip)
            seasonality[i] = 1 - weekend_boost * 0.3

    return revenue * seasonality


def add_sale_events(
    revenue: np.ndarray, dates: pd.DatetimeIndex, sale_events: List[SaleEvent]
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Add revenue bumps during sale events.

    Returns modified revenue and a DataFrame of sale event flags.
    """
    sale_flags = pd.DataFrame(index=dates)
    sale_flags["is_sale"] = 0
    sale_flags["sale_name"] = ""

    modified_revenue = revenue.copy()

    for event in sale_events:
        start = pd.to_datetime(event.start_date)
        end = pd.to_datetime(event.end_date)

        mask = (dates >= start) & (dates <= end)
        modified_revenue[mask] *= event.revenue_multiplier
        sale_flags.loc[mask, "is_sale"] = 1
        sale_flags.loc[mask, "sale_name"] = event.name

    return modified_revenue, sale_flags


def add_content_drops(
    revenue: np.ndarray,
    start_date: datetime,
    interval_days: int,
    boost: float,
    decay_days: int = 14,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Add content drop bumps for live service games.

    Returns modified revenue and content drop flag array.
    """
    days = len(revenue)
    modified_revenue = revenue.copy()
    content_flags = np.zeros(days)

    # Content drops happen at regular intervals
    drop_days = list(range(0, days, interval_days))

    for drop_day in drop_days:
        for i in range(decay_days):
            if drop_day + i < days:
                # Exponential decay from content drop boost
                bump = boost * np.exp(-i / (decay_days / 3))
                modified_revenue[drop_day + i] *= 1 + bump
                if i == 0:
                    content_flags[drop_day] = 1

    return modified_revenue, content_flags


def add_noise(revenue: np.ndarray, noise_level: float) -> np.ndarray:
    """Add realistic noise to revenue data."""
    noise = np.random.normal(1.0, noise_level, len(revenue))
    noise = np.clip(noise, 0.5, 2.0)  # Prevent extreme values
    return revenue * noise


def generate_game_revenue(
    config: GameConfig, end_date: str, sale_events: Optional[List[SaleEvent]] = None
) -> pd.DataFrame:
    """
    Generate synthetic daily revenue data for a game.

    Parameters
    ----------
    config : GameConfig
        Configuration for the game
    end_date : str
        End date for the data (YYYY-MM-DD)
    sale_events : List[SaleEvent], optional
        List of sale events to include

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: date, revenue, game_name, is_sale,
        is_content_drop, day_of_week
    """
    start = pd.to_datetime(config.start_date)
    end = pd.to_datetime(end_date)
    days = (end - start).days + 1

    dates = pd.date_range(start=start, end=end, freq="D")

    # Generate base curve
    revenue = generate_base_revenue_curve(
        days=days,
        base_revenue=config.base_revenue,
        launch_multiplier=config.launch_multiplier,
        decay_rate=config.decay_rate,
        game_type=config.game_type,
    )

    # Add weekly seasonality
    revenue = add_weekly_seasonality(revenue, start, config.weekend_boost)

    # Add content drops for live service games
    content_flags = np.zeros(days)
    if config.game_type == "live_service":
        revenue, content_flags = add_content_drops(
            revenue, start, config.content_drop_interval_days, config.content_drop_boost
        )

    # Add sale events
    sale_flags = pd.DataFrame({"is_sale": np.zeros(days), "sale_name": ""}, index=dates)
    if sale_events:
        revenue, sale_flags = add_sale_events(revenue, dates, sale_events)

    # Add noise
    revenue = add_noise(revenue, config.noise_level)

    # Ensure non-negative
    revenue = np.maximum(revenue, 0)

    # Build DataFrame
    df = pd.DataFrame(
        {
            "date": dates,
            "revenue": revenue,
            "game_name": config.name,
            "is_sale": sale_flags["is_sale"].values,
            "is_content_drop": content_flags,
            "day_of_week": dates.dayofweek,
            "day_name": dates.day_name(),
            "month": dates.month,
            "year": dates.year,
        }
    )

    return df


def get_default_sale_events() -> List[SaleEvent]:
    """Get standard sale events for testing."""
    return [
        SaleEvent("Summer Sale 2023", "2023-06-22", "2023-07-06", 0.50, 1.8),
        SaleEvent("Halloween Sale 2023", "2023-10-26", "2023-11-02", 0.33, 1.5),
        SaleEvent("Black Friday 2023", "2023-11-22", "2023-11-27", 0.60, 2.2),
        SaleEvent("Winter Sale 2023", "2023-12-21", "2024-01-04", 0.50, 2.0),
        SaleEvent("Lunar New Year 2024", "2024-02-08", "2024-02-15", 0.40, 1.4),
        SaleEvent("Spring Sale 2024", "2024-03-14", "2024-03-21", 0.33, 1.3),
        SaleEvent("Summer Sale 2024", "2024-06-27", "2024-07-11", 0.50, 1.7),
        SaleEvent("Halloween Sale 2024", "2024-10-24", "2024-10-31", 0.33, 1.5),
        SaleEvent("Black Friday 2024", "2024-11-27", "2024-12-02", 0.60, 2.1),
        SaleEvent("Winter Sale 2024", "2024-12-19", "2025-01-02", 0.50, 1.9),
    ]


def get_default_game_configs() -> List[GameConfig]:
    """
    Get default configurations for 5 synthetic games.

    Returns games with different lifecycles:
    1. New launch (recent, high decay)
    2. Mature AAA title (stable, slow decline)
    3. Live service (content drops)
    4. Indie hit (modest launch, good retention)
    5. Struggling title (low base, high variance)
    """
    return [
        GameConfig(
            name="Galaxy Conquest",
            game_type="new_launch",
            start_date="2024-03-15",
            base_revenue=50000,
            launch_multiplier=8.0,
            decay_rate=0.015,
            weekend_boost=0.20,
            noise_level=0.12,
        ),
        GameConfig(
            name="Eternal Legends",
            game_type="mature",
            start_date="2022-01-01",
            base_revenue=75000,
            launch_multiplier=1.0,  # Already past launch
            decay_rate=0.0001,
            weekend_boost=0.12,
            noise_level=0.08,
        ),
        GameConfig(
            name="Battle Royale X",
            game_type="live_service",
            start_date="2023-01-01",
            base_revenue=120000,
            launch_multiplier=1.0,
            decay_rate=0.0,
            weekend_boost=0.25,
            noise_level=0.10,
            content_drop_boost=0.35,
            content_drop_interval_days=42,
        ),
        GameConfig(
            name="Pixel Adventure",
            game_type="new_launch",
            start_date="2023-09-01",
            base_revenue=15000,
            launch_multiplier=4.0,
            decay_rate=0.005,
            weekend_boost=0.18,
            noise_level=0.15,
        ),
        GameConfig(
            name="Dungeon Depths",
            game_type="mature",
            start_date="2022-06-01",
            base_revenue=8000,
            launch_multiplier=1.0,
            decay_rate=0.0003,
            weekend_boost=0.10,
            noise_level=0.20,
        ),
    ]


def generate_all_games_data(
    end_date: str = "2025-01-15",
    configs: Optional[List[GameConfig]] = None,
    sale_events: Optional[List[SaleEvent]] = None,
) -> pd.DataFrame:
    """
    Generate synthetic revenue data for all games.

    Parameters
    ----------
    end_date : str
        End date for all data
    configs : List[GameConfig], optional
        Custom game configurations (uses defaults if None)
    sale_events : List[SaleEvent], optional
        Custom sale events (uses defaults if None)

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with all games' revenue data
    """
    if configs is None:
        configs = get_default_game_configs()
    if sale_events is None:
        sale_events = get_default_sale_events()

    all_data = []
    for config in configs:
        df = generate_game_revenue(config, end_date, sale_events)
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)


# =============================================================================
# EVALUATION METRICS
# =============================================================================


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean Absolute Percentage Error.

    Handles zero values by filtering them out with a warning.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Filter out zeros to avoid division by zero
    mask = y_true != 0
    if not mask.all():
        n_zeros = (~mask).sum()
        warnings.warn(f"MAPE: Filtered out {n_zeros} zero values from y_true")

    if mask.sum() == 0:
        return np.nan

    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Symmetric Mean Absolute Percentage Error.

    More robust than MAPE when values are near zero.
    Range: 0% to 200%
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2

    # Avoid division by zero
    mask = denominator != 0
    if mask.sum() == 0:
        return np.nan

    return np.mean(np.abs(y_true[mask] - y_pred[mask]) / denominator[mask]) * 100


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return np.mean(np.abs(np.array(y_true) - np.array(y_pred)))


def evaluate_forecast(
    y_true: np.ndarray, y_pred: np.ndarray, name: str = ""
) -> Dict[str, float]:
    """
    Calculate all evaluation metrics for a forecast.

    Parameters
    ----------
    y_true : array-like
        Actual values
    y_pred : array-like
        Predicted values
    name : str
        Optional name for the forecast method

    Returns
    -------
    dict
        Dictionary with all metrics
    """
    return {
        "name": name,
        "mape": mape(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "smape": smape(y_true, y_pred),
        "mae": mae(y_true, y_pred),
        "n_samples": len(y_true),
    }


def compare_forecasts(
    y_true: np.ndarray, forecasts: Dict[str, np.ndarray]
) -> pd.DataFrame:
    """
    Compare multiple forecasts against actual values.

    Parameters
    ----------
    y_true : array-like
        Actual values
    forecasts : dict
        Dictionary mapping method names to predictions

    Returns
    -------
    pd.DataFrame
        Comparison table with all metrics
    """
    results = []
    for name, y_pred in forecasts.items():
        results.append(evaluate_forecast(y_true, y_pred, name))

    df = pd.DataFrame(results)
    df = df.set_index("name")
    return df.sort_values("mape")


# =============================================================================
# TRAIN/TEST SPLIT UTILITIES
# =============================================================================


def time_series_split(
    df: pd.DataFrame,
    test_days: int,
    date_col: str = "date",
    target_col: str = "revenue",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split time series data into train and test sets.

    Uses the last `test_days` as the test set.

    Parameters
    ----------
    df : pd.DataFrame
        Input data with date column
    test_days : int
        Number of days to use for testing
    date_col : str
        Name of the date column
    target_col : str
        Name of the target column

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (train_df, test_df)
    """
    df = df.sort_values(date_col).copy()

    cutoff_date = df[date_col].max() - timedelta(days=test_days)

    train = df[df[date_col] <= cutoff_date].copy()
    test = df[df[date_col] > cutoff_date].copy()

    return train, test


def create_holdout_splits(
    df: pd.DataFrame, holdout_periods: List[int] = [30, 60, 90], date_col: str = "date"
) -> Dict[int, Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Create multiple train/test splits for different holdout periods.

    Parameters
    ----------
    df : pd.DataFrame
        Input data
    holdout_periods : List[int]
        List of holdout period lengths in days
    date_col : str
        Name of the date column

    Returns
    -------
    dict
        Dictionary mapping holdout period to (train, test) tuples
    """
    splits = {}
    for period in holdout_periods:
        train, test = time_series_split(df, period, date_col)
        splits[period] = (train, test)
    return splits


def walk_forward_split(
    df: pd.DataFrame,
    n_splits: int = 5,
    test_size: int = 30,
    gap: int = 0,
    date_col: str = "date",
) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Create walk-forward validation splits.

    Parameters
    ----------
    df : pd.DataFrame
        Input data
    n_splits : int
        Number of splits to create
    test_size : int
        Size of each test set in days
    gap : int
        Gap between train and test (useful for avoiding leakage)
    date_col : str
        Name of the date column

    Returns
    -------
    List[Tuple[pd.DataFrame, pd.DataFrame]]
        List of (train, test) tuples
    """
    df = df.sort_values(date_col).copy()
    dates = df[date_col].unique()
    n_dates = len(dates)

    # Calculate sizes
    total_test = n_splits * test_size
    min_train = n_dates - total_test - gap * n_splits

    if min_train < test_size:
        raise ValueError(
            f"Not enough data for {n_splits} splits with test_size={test_size}"
        )

    splits = []
    for i in range(n_splits):
        test_end_idx = n_dates - i * test_size
        test_start_idx = test_end_idx - test_size
        train_end_idx = test_start_idx - gap

        test_end_date = dates[test_end_idx - 1]
        test_start_date = dates[test_start_idx]
        train_end_date = dates[train_end_idx - 1]

        train = df[df[date_col] <= train_end_date].copy()
        test = df[
            (df[date_col] >= test_start_date) & (df[date_col] <= test_end_date)
        ].copy()

        splits.append((train, test))

    return splits[::-1]  # Return in chronological order


# =============================================================================
# VISUALIZATION HELPERS
# =============================================================================


def plot_forecast_comparison(
    dates: pd.DatetimeIndex,
    y_true: np.ndarray,
    forecasts: Dict[str, np.ndarray],
    title: str = "Forecast Comparison",
    figsize: Tuple[int, int] = (14, 6),
    show_metrics: bool = True,
) -> plt.Figure:
    """
    Plot actual values against multiple forecasts.

    Parameters
    ----------
    dates : pd.DatetimeIndex
        Dates for x-axis
    y_true : array-like
        Actual values
    forecasts : dict
        Dictionary mapping method names to predictions
    title : str
        Plot title
    figsize : tuple
        Figure size
    show_metrics : bool
        Whether to show MAPE in legend

    Returns
    -------
    plt.Figure
        The matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot actual
    ax.plot(dates, y_true, "k-", linewidth=2, label="Actual", alpha=0.8)

    # Plot forecasts
    colors = plt.cm.tab10(np.linspace(0, 1, len(forecasts)))
    for (name, y_pred), color in zip(forecasts.items(), colors):
        label = name
        if show_metrics:
            m = mape(y_true, y_pred)
            label = f"{name} (MAPE: {m:.1f}%)"
        ax.plot(dates, y_pred, "--", color=color, linewidth=1.5, label=label, alpha=0.8)

    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.set_title(title)
    ax.legend(loc="upper right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def plot_train_test_split(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    predictions: Optional[np.ndarray] = None,
    date_col: str = "date",
    target_col: str = "revenue",
    title: str = "Train/Test Split",
    figsize: Tuple[int, int] = (14, 6),
) -> plt.Figure:
    """
    Visualize train/test split with optional predictions.

    Parameters
    ----------
    train_df : pd.DataFrame
        Training data
    test_df : pd.DataFrame
        Test data
    predictions : array-like, optional
        Predictions for test period
    date_col : str
        Name of date column
    target_col : str
        Name of target column
    title : str
        Plot title
    figsize : tuple
        Figure size

    Returns
    -------
    plt.Figure
        The matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot training data
    ax.plot(train_df[date_col], train_df[target_col], "b-", label="Training", alpha=0.7)

    # Plot test data
    ax.plot(
        test_df[date_col], test_df[target_col], "g-", label="Test (Actual)", linewidth=2
    )

    # Plot predictions if provided
    if predictions is not None:
        ax.plot(test_df[date_col], predictions, "r--", label="Predictions", linewidth=2)

        # Add metrics annotation
        metrics = evaluate_forecast(test_df[target_col].values, predictions, "Forecast")
        metrics_text = (
            f"MAPE: {metrics['mape']:.1f}%\n"
            f"RMSE: ${metrics['rmse']:,.0f}\n"
            f"SMAPE: {metrics['smape']:.1f}%"
        )
        ax.annotate(
            metrics_text,
            xy=(0.02, 0.98),
            xycoords="axes fraction",
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    # Add vertical line at split point
    split_date = test_df[date_col].min()
    ax.axvline(x=split_date, color="gray", linestyle="--", alpha=0.7)
    ax.annotate(
        "Train/Test Split",
        xy=(split_date, ax.get_ylim()[1]),
        xytext=(10, -10),
        textcoords="offset points",
        fontsize=9,
        alpha=0.7,
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.set_title(title)
    ax.legend(loc="upper right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def plot_residuals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    dates: Optional[pd.DatetimeIndex] = None,
    title: str = "Forecast Residuals",
    figsize: Tuple[int, int] = (14, 8),
) -> plt.Figure:
    """
    Plot residual analysis for a forecast.

    Creates a 2x2 grid with:
    - Residuals over time
    - Residual histogram
    - Residuals vs predicted
    - Q-Q plot

    Parameters
    ----------
    y_true : array-like
        Actual values
    y_pred : array-like
        Predicted values
    dates : pd.DatetimeIndex, optional
        Dates for x-axis (uses index if None)
    title : str
        Main title
    figsize : tuple
        Figure size

    Returns
    -------
    plt.Figure
        The matplotlib figure
    """
    residuals = np.array(y_true) - np.array(y_pred)

    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14)

    # Residuals over time
    ax1 = axes[0, 0]
    if dates is not None:
        ax1.plot(dates, residuals, "b-", alpha=0.7)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    else:
        ax1.plot(residuals, "b-", alpha=0.7)
    ax1.axhline(y=0, color="r", linestyle="--", alpha=0.5)
    ax1.set_xlabel("Date" if dates is not None else "Index")
    ax1.set_ylabel("Residual")
    ax1.set_title("Residuals Over Time")

    # Histogram
    ax2 = axes[0, 1]
    ax2.hist(residuals, bins=30, edgecolor="black", alpha=0.7)
    ax2.axvline(x=0, color="r", linestyle="--", alpha=0.5)
    ax2.set_xlabel("Residual")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Residual Distribution")

    # Residuals vs Predicted
    ax3 = axes[1, 0]
    ax3.scatter(y_pred, residuals, alpha=0.5)
    ax3.axhline(y=0, color="r", linestyle="--", alpha=0.5)
    ax3.set_xlabel("Predicted Value")
    ax3.set_ylabel("Residual")
    ax3.set_title("Residuals vs Predicted")

    # Q-Q plot (simplified)
    ax4 = axes[1, 1]
    sorted_residuals = np.sort(residuals)
    theoretical_quantiles = np.random.normal(
        np.mean(residuals), np.std(residuals), len(residuals)
    )
    theoretical_quantiles = np.sort(theoretical_quantiles)
    ax4.scatter(theoretical_quantiles, sorted_residuals, alpha=0.5)
    lims = [
        min(theoretical_quantiles.min(), sorted_residuals.min()),
        max(theoretical_quantiles.max(), sorted_residuals.max()),
    ]
    ax4.plot(lims, lims, "r--", alpha=0.5)
    ax4.set_xlabel("Theoretical Quantiles")
    ax4.set_ylabel("Sample Quantiles")
    ax4.set_title("Q-Q Plot")

    plt.tight_layout()
    return fig


def plot_metrics_comparison(
    results_df: pd.DataFrame,
    metric: str = "mape",
    title: str = None,
    figsize: Tuple[int, int] = (10, 6),
) -> plt.Figure:
    """
    Bar chart comparing metrics across different methods.

    Parameters
    ----------
    results_df : pd.DataFrame
        DataFrame with methods as index and metrics as columns
    metric : str
        Which metric to plot
    title : str, optional
        Plot title
    figsize : tuple
        Figure size

    Returns
    -------
    plt.Figure
        The matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    values = results_df[metric].sort_values()
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(values)))

    bars = ax.barh(values.index, values.values, color=colors)

    # Add value labels
    for bar, val in zip(bars, values.values):
        ax.text(
            val + max(values) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}",
            va="center",
            fontsize=10,
        )

    ax.set_xlabel(metric.upper())
    ax.set_title(title or f"{metric.upper()} Comparison by Method")
    plt.tight_layout()

    return fig


def plot_game_revenue_overview(
    df: pd.DataFrame,
    date_col: str = "date",
    target_col: str = "revenue",
    game_col: str = "game_name",
    figsize: Tuple[int, int] = (14, 10),
) -> plt.Figure:
    """
    Plot overview of all games' revenue data.

    Parameters
    ----------
    df : pd.DataFrame
        Combined data for all games
    date_col : str
        Name of date column
    target_col : str
        Name of target column
    game_col : str
        Name of game identifier column
    figsize : tuple
        Figure size

    Returns
    -------
    plt.Figure
        The matplotlib figure
    """
    games = df[game_col].unique()
    n_games = len(games)

    fig, axes = plt.subplots(n_games, 1, figsize=figsize, sharex=True)
    if n_games == 1:
        axes = [axes]

    colors = plt.cm.tab10(np.linspace(0, 1, n_games))

    for ax, game, color in zip(axes, games, colors):
        game_data = df[df[game_col] == game].sort_values(date_col)

        ax.plot(game_data[date_col], game_data[target_col], color=color, alpha=0.8)
        ax.fill_between(
            game_data[date_col], 0, game_data[target_col], color=color, alpha=0.2
        )

        # Highlight sale events
        sale_mask = game_data["is_sale"] == 1
        if sale_mask.any():
            ax.scatter(
                game_data.loc[sale_mask, date_col],
                game_data.loc[sale_mask, target_col],
                color="red",
                s=10,
                alpha=0.5,
                label="Sale Events",
            )

        ax.set_ylabel("Revenue ($)")
        ax.set_title(game, loc="left", fontsize=11)
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f"${x / 1000:.0f}K")
        )

    axes[-1].set_xlabel("Date")
    fig.suptitle("Game Revenue Overview", fontsize=14, y=1.02)
    plt.tight_layout()

    return fig


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def prepare_for_prophet(
    df: pd.DataFrame, date_col: str = "date", target_col: str = "revenue"
) -> pd.DataFrame:
    """
    Prepare data for Facebook Prophet.

    Prophet expects columns named 'ds' and 'y'.
    """
    prophet_df = df[[date_col, target_col]].copy()
    prophet_df.columns = ["ds", "y"]
    return prophet_df


def prepare_for_statsmodels(
    df: pd.DataFrame, date_col: str = "date", target_col: str = "revenue"
) -> pd.Series:
    """
    Prepare data for statsmodels.

    Returns a Series with DatetimeIndex.
    """
    ts = df.set_index(date_col)[target_col].copy()
    ts.index = pd.DatetimeIndex(ts.index)
    ts.index.freq = "D"
    return ts


def add_calendar_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Add calendar-based features for ML models.

    Features added:
    - day_of_week (0-6)
    - day_of_month (1-31)
    - week_of_year (1-52)
    - month (1-12)
    - quarter (1-4)
    - is_weekend (0/1)
    - is_month_start (0/1)
    - is_month_end (0/1)
    """
    df = df.copy()
    dates = pd.to_datetime(df[date_col])

    df["day_of_week"] = dates.dt.dayofweek
    df["day_of_month"] = dates.dt.day
    df["week_of_year"] = dates.dt.isocalendar().week.astype(int)
    df["month"] = dates.dt.month
    df["quarter"] = dates.dt.quarter
    df["is_weekend"] = (dates.dt.dayofweek >= 5).astype(int)
    df["is_month_start"] = dates.dt.is_month_start.astype(int)
    df["is_month_end"] = dates.dt.is_month_end.astype(int)

    return df


def add_lag_features(
    df: pd.DataFrame, target_col: str = "revenue", lags: List[int] = [1, 7, 14, 28]
) -> pd.DataFrame:
    """
    Add lagged features for ML models.

    Parameters
    ----------
    df : pd.DataFrame
        Input data (must be sorted by date)
    target_col : str
        Column to create lags for
    lags : List[int]
        Lag periods to create

    Returns
    -------
    pd.DataFrame
        DataFrame with lag features added
    """
    df = df.copy()
    for lag in lags:
        df[f"{target_col}_lag_{lag}"] = df[target_col].shift(lag)
    return df


def add_rolling_features(
    df: pd.DataFrame, target_col: str = "revenue", windows: List[int] = [7, 14, 28]
) -> pd.DataFrame:
    """
    Add rolling statistics for ML models.

    Parameters
    ----------
    df : pd.DataFrame
        Input data (must be sorted by date)
    target_col : str
        Column to calculate rolling stats for
    windows : List[int]
        Window sizes

    Returns
    -------
    pd.DataFrame
        DataFrame with rolling features added
    """
    df = df.copy()
    for window in windows:
        df[f"{target_col}_rolling_mean_{window}"] = (
            df[target_col].rolling(window=window, min_periods=1).mean()
        )
        df[f"{target_col}_rolling_std_{window}"] = (
            df[target_col].rolling(window=window, min_periods=1).std()
        )
        df[f"{target_col}_rolling_min_{window}"] = (
            df[target_col].rolling(window=window, min_periods=1).min()
        )
        df[f"{target_col}_rolling_max_{window}"] = (
            df[target_col].rolling(window=window, min_periods=1).max()
        )
    return df


# =============================================================================
# QUICK START / DEMO
# =============================================================================

if __name__ == "__main__":
    print("Generating synthetic game revenue data...")

    # Generate data
    df = generate_all_games_data()

    print(f"\nGenerated {len(df):,} records for {df['game_name'].nunique()} games")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    print("\nSample data:")
    print(df.head(10))

    print("\nRevenue statistics by game:")
    print(df.groupby("game_name")["revenue"].agg(["mean", "std", "min", "max"]))

    # Demo train/test split
    print("\n" + "=" * 60)
    print("Demo: Train/Test Split for 'Battle Royale X'")
    print("=" * 60)

    game_df = df[df["game_name"] == "Battle Royale X"].copy()
    train, test = time_series_split(game_df, test_days=30)

    print(
        f"Training set: {len(train)} days ({train['date'].min()} to {train['date'].max()})"
    )
    print(f"Test set: {len(test)} days ({test['date'].min()} to {test['date'].max()})")

    # Demo evaluation metrics
    print("\n" + "=" * 60)
    print("Demo: Evaluation Metrics")
    print("=" * 60)

    y_true = test["revenue"].values
    y_naive = np.full_like(y_true, train["revenue"].mean())  # Naive baseline

    metrics = evaluate_forecast(y_true, y_naive, "Naive Mean")
    print(f"Naive Mean Forecast Metrics:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")

    print("\n" + "=" * 60)
    print("To visualize the data, call:")
    print("  fig = plot_game_revenue_overview(df)")
    print("  plt.show()")
    print("=" * 60)
