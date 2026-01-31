"""
Prediction Intervals Module

Provides methods for generating prediction intervals (confidence bounds)
for time series forecasts. Supports multiple approaches:

1. Conformal Prediction - Distribution-free, uses residuals from calibration set
2. Bootstrap - Resamples residuals to simulate forecast distribution
3. Quantile Regression - Direct quantile estimation (for ML models)
4. Parametric - Assumes error distribution (normal, etc.)

Usage:
    from prediction_intervals import ConformalInterval, BootstrapInterval

    # Conformal prediction (recommended for general use)
    ci = ConformalInterval(coverage=0.90)
    ci.fit(y_train_holdout, predictions_on_holdout)
    lower, upper = ci.predict_interval(new_predictions)
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional, Dict, Callable
from dataclasses import dataclass
import warnings


# =============================================================================
# PREDICTION INTERVAL CLASSES
# =============================================================================


class ConformalInterval:
    """
    Conformal prediction intervals.

    A distribution-free method that uses calibration residuals to construct
    intervals with guaranteed coverage (under exchangeability assumption).

    How it works:
    1. Fit on a calibration set (recent historical data)
    2. Calculate residuals on calibration set
    3. Use quantile of absolute residuals for interval width

    Advantages:
    - No distributional assumptions
    - Guaranteed coverage under mild conditions
    - Simple to implement and understand

    Parameters
    ----------
    coverage : float
        Desired coverage probability (e.g., 0.90 for 90% CI)
    symmetric : bool
        If True, uses symmetric intervals (+/- q)
        If False, uses separate lower/upper quantiles
    """

    def __init__(self, coverage: float = 0.90, symmetric: bool = True):
        if not 0 < coverage < 1:
            raise ValueError("Coverage must be between 0 and 1")
        self.coverage = coverage
        self.symmetric = symmetric
        self.calibration_residuals = None
        self.interval_width = None
        self.lower_quantile = None
        self.upper_quantile = None

    def fit(self, y_true: np.ndarray, y_pred: np.ndarray) -> "ConformalInterval":
        """
        Fit the conformal predictor on calibration data.

        Parameters
        ----------
        y_true : array-like
            Actual values from calibration set
        y_pred : array-like
            Predictions for calibration set
        """
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        if len(y_true) != len(y_pred):
            raise ValueError("y_true and y_pred must have same length")
        if len(y_true) < 10:
            warnings.warn(
                "Conformal prediction works best with at least 10 calibration samples"
            )

        residuals = y_true - y_pred
        self.calibration_residuals = residuals

        if self.symmetric:
            # Symmetric interval: use quantile of |residuals|
            abs_residuals = np.abs(residuals)
            self.interval_width = np.quantile(abs_residuals, self.coverage)
        else:
            # Asymmetric interval: separate lower and upper quantiles
            alpha = 1 - self.coverage
            self.lower_quantile = np.quantile(residuals, alpha / 2)
            self.upper_quantile = np.quantile(residuals, 1 - alpha / 2)

        return self

    def predict_interval(self, y_pred: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate prediction intervals for new predictions.

        Parameters
        ----------
        y_pred : array-like
            Point predictions

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            (lower_bound, upper_bound)
        """
        y_pred = np.asarray(y_pred)

        if self.symmetric:
            if self.interval_width is None:
                raise ValueError("Must call fit() before predict_interval()")
            lower = y_pred - self.interval_width
            upper = y_pred + self.interval_width
        else:
            if self.lower_quantile is None:
                raise ValueError("Must call fit() before predict_interval()")
            # residual = y_true - y_pred, so:
            # y_true = y_pred + residual
            # lower = y_pred + lower_quantile (which is negative)
            # upper = y_pred + upper_quantile
            lower = y_pred + self.lower_quantile
            upper = y_pred + self.upper_quantile

        return lower, upper

    def get_coverage_info(self) -> Dict:
        """Get information about the fitted intervals."""
        if self.calibration_residuals is None:
            return {"status": "not fitted"}

        info = {
            "n_calibration_samples": len(self.calibration_residuals),
            "coverage": self.coverage,
            "symmetric": self.symmetric,
            "mean_residual": np.mean(self.calibration_residuals),
            "std_residual": np.std(self.calibration_residuals),
        }

        if self.symmetric:
            info["interval_width"] = self.interval_width
        else:
            info["lower_quantile"] = self.lower_quantile
            info["upper_quantile"] = self.upper_quantile

        return info


class BootstrapInterval:
    """
    Bootstrap prediction intervals.

    Generates intervals by resampling residuals and simulating
    multiple forecast paths.

    How it works:
    1. Fit on calibration data to get residual distribution
    2. For new predictions, add resampled residuals
    3. Use quantiles of simulated values for intervals

    Parameters
    ----------
    coverage : float
        Desired coverage probability
    n_bootstraps : int
        Number of bootstrap samples
    random_state : int, optional
        Random seed for reproducibility
    """

    def __init__(
        self,
        coverage: float = 0.90,
        n_bootstraps: int = 1000,
        random_state: Optional[int] = None,
    ):
        self.coverage = coverage
        self.n_bootstraps = n_bootstraps
        self.random_state = random_state
        self.residuals = None

    def fit(self, y_true: np.ndarray, y_pred: np.ndarray) -> "BootstrapInterval":
        """
        Fit by storing calibration residuals.

        Parameters
        ----------
        y_true : array-like
            Actual values
        y_pred : array-like
            Predictions
        """
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        self.residuals = y_true - y_pred
        return self

    def predict_interval(self, y_pred: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate bootstrap prediction intervals.

        Parameters
        ----------
        y_pred : array-like
            Point predictions

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            (lower_bound, upper_bound)
        """
        if self.residuals is None:
            raise ValueError("Must call fit() before predict_interval()")

        y_pred = np.asarray(y_pred)
        n_pred = len(y_pred)

        rng = np.random.default_rng(self.random_state)

        # Generate bootstrap samples
        bootstrap_preds = np.zeros((self.n_bootstraps, n_pred))
        for i in range(self.n_bootstraps):
            # Sample residuals with replacement
            sampled_residuals = rng.choice(self.residuals, size=n_pred, replace=True)
            bootstrap_preds[i] = y_pred + sampled_residuals

        # Calculate quantiles
        alpha = 1 - self.coverage
        lower = np.quantile(bootstrap_preds, alpha / 2, axis=0)
        upper = np.quantile(bootstrap_preds, 1 - alpha / 2, axis=0)

        return lower, upper

    def predict_samples(self, y_pred: np.ndarray, n_samples: int = 100) -> np.ndarray:
        """
        Generate sample forecast paths.

        Useful for simulating scenarios.

        Parameters
        ----------
        y_pred : array-like
            Point predictions
        n_samples : int
            Number of sample paths to generate

        Returns
        -------
        np.ndarray
            Shape (n_samples, len(y_pred))
        """
        if self.residuals is None:
            raise ValueError("Must call fit() before predict_samples()")

        y_pred = np.asarray(y_pred)
        n_pred = len(y_pred)

        rng = np.random.default_rng(self.random_state)

        samples = np.zeros((n_samples, n_pred))
        for i in range(n_samples):
            sampled_residuals = rng.choice(self.residuals, size=n_pred, replace=True)
            samples[i] = y_pred + sampled_residuals

        return samples


class ParametricInterval:
    """
    Parametric prediction intervals assuming normal errors.

    Simple approach that assumes residuals follow a normal distribution.
    Uses mean and standard deviation to construct intervals.

    Parameters
    ----------
    coverage : float
        Desired coverage probability
    """

    def __init__(self, coverage: float = 0.90):
        self.coverage = coverage
        self.mean_residual = None
        self.std_residual = None
        self._z_score = None

    def fit(self, y_true: np.ndarray, y_pred: np.ndarray) -> "ParametricInterval":
        """
        Fit by estimating residual distribution parameters.
        """
        from scipy import stats

        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        residuals = y_true - y_pred
        self.mean_residual = np.mean(residuals)
        self.std_residual = np.std(residuals, ddof=1)

        # Z-score for desired coverage
        alpha = 1 - self.coverage
        self._z_score = stats.norm.ppf(1 - alpha / 2)

        return self

    def predict_interval(self, y_pred: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate parametric prediction intervals.
        """
        if self.std_residual is None:
            raise ValueError("Must call fit() before predict_interval()")

        y_pred = np.asarray(y_pred)

        # Adjust predictions for bias
        adjusted_pred = y_pred + self.mean_residual

        # Calculate intervals
        margin = self._z_score * self.std_residual
        lower = adjusted_pred - margin
        upper = adjusted_pred + margin

        return lower, upper


class ExpandingWindowInterval:
    """
    Prediction intervals that widen over forecast horizon.

    For multi-step forecasts, uncertainty typically grows with horizon.
    This class scales interval width based on forecast step.

    Parameters
    ----------
    coverage : float
        Desired coverage probability
    growth_rate : float
        How much intervals expand per step (multiplicative)
        Default 1.05 = 5% wider each step
    """

    def __init__(
        self,
        coverage: float = 0.90,
        growth_rate: float = 1.05,
        base_interval: Optional["ConformalInterval"] = None,
    ):
        self.coverage = coverage
        self.growth_rate = growth_rate
        self.base_interval = base_interval or ConformalInterval(coverage)

    def fit(self, y_true: np.ndarray, y_pred: np.ndarray) -> "ExpandingWindowInterval":
        """
        Fit the base interval estimator.
        """
        self.base_interval.fit(y_true, y_pred)
        return self

    def predict_interval(
        self, y_pred: np.ndarray, horizon_steps: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate expanding prediction intervals.

        Parameters
        ----------
        y_pred : array-like
            Point predictions
        horizon_steps : array-like, optional
            Forecast step number for each prediction (1, 2, 3, ...)
            If None, assumes sequential steps
        """
        y_pred = np.asarray(y_pred)
        n_pred = len(y_pred)

        if horizon_steps is None:
            horizon_steps = np.arange(1, n_pred + 1)

        # Get base intervals
        lower, upper = self.base_interval.predict_interval(y_pred)

        # Expand based on horizon
        expansion_factors = self.growth_rate ** (horizon_steps - 1)

        # Center and scale
        center = (lower + upper) / 2
        half_width = (upper - lower) / 2

        expanded_half_width = half_width * expansion_factors

        return center - expanded_half_width, center + expanded_half_width


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def evaluate_coverage(
    y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray
) -> Dict[str, float]:
    """
    Evaluate prediction interval coverage and width.

    Parameters
    ----------
    y_true : array-like
        Actual values
    lower : array-like
        Lower bounds
    upper : array-like
        Upper bounds

    Returns
    -------
    dict
        Coverage metrics
    """
    y_true = np.asarray(y_true)
    lower = np.asarray(lower)
    upper = np.asarray(upper)

    # Coverage: fraction of actual values within bounds
    in_interval = (y_true >= lower) & (y_true <= upper)
    coverage = np.mean(in_interval)

    # Interval width
    widths = upper - lower
    mean_width = np.mean(widths)

    # Interval score (proper scoring rule for intervals)
    # Lower is better
    alpha = 0.1  # Assuming 90% coverage target
    interval_score = np.mean(
        (upper - lower)
        + (2 / alpha) * (lower - y_true) * (y_true < lower)
        + (2 / alpha) * (y_true - upper) * (y_true > upper)
    )

    return {
        "coverage": coverage,
        "mean_width": mean_width,
        "median_width": np.median(widths),
        "min_width": np.min(widths),
        "max_width": np.max(widths),
        "interval_score": interval_score,
        "n_samples": len(y_true),
        "n_below_lower": np.sum(y_true < lower),
        "n_above_upper": np.sum(y_true > upper),
    }


def plot_prediction_intervals(
    dates: pd.DatetimeIndex,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    title: str = "Forecast with Prediction Intervals",
    coverage: float = 0.90,
    figsize: Tuple[int, int] = (14, 6),
):
    """
    Plot forecast with prediction intervals.

    Parameters
    ----------
    dates : DatetimeIndex
        Dates for x-axis
    y_true : array-like
        Actual values
    y_pred : array-like
        Point predictions
    lower : array-like
        Lower bounds
    upper : array-like
        Upper bounds
    title : str
        Plot title
    coverage : float
        Nominal coverage for legend
    figsize : tuple
        Figure size
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    fig, ax = plt.subplots(figsize=figsize)

    # Plot prediction interval
    ax.fill_between(
        dates,
        lower,
        upper,
        alpha=0.3,
        color="blue",
        label=f"{coverage * 100:.0f}% Prediction Interval",
    )

    # Plot predictions
    ax.plot(dates, y_pred, "b-", linewidth=2, label="Forecast")

    # Plot actuals
    ax.plot(dates, y_true, "k.", markersize=8, label="Actual", alpha=0.7)

    # Mark points outside interval
    outside = (y_true < lower) | (y_true > upper)
    if outside.any():
        ax.scatter(
            dates[outside],
            y_true[outside],
            c="red",
            s=50,
            marker="x",
            label=f"Outside interval ({outside.sum()})",
        )

    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue ($)")
    ax.set_title(title)
    ax.legend(loc="upper right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


# =============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON USE CASES
# =============================================================================


def create_conformal_intervals(
    train_predictions: np.ndarray,
    train_actuals: np.ndarray,
    test_predictions: np.ndarray,
    coverage: float = 0.90,
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Convenience function to create conformal prediction intervals.

    Parameters
    ----------
    train_predictions : array-like
        Predictions on training/calibration data
    train_actuals : array-like
        Actual values for training/calibration data
    test_predictions : array-like
        Predictions to create intervals for
    coverage : float
        Desired coverage probability

    Returns
    -------
    Tuple
        (lower_bounds, upper_bounds, interval_info)
    """
    ci = ConformalInterval(coverage=coverage, symmetric=True)
    ci.fit(train_actuals, train_predictions)
    lower, upper = ci.predict_interval(test_predictions)

    info = ci.get_coverage_info()

    return lower, upper, info


def add_intervals_to_forecast(
    forecast_df: pd.DataFrame,
    calibration_df: pd.DataFrame,
    pred_col: str = "prediction",
    actual_col: str = "actual",
    coverage: float = 0.90,
) -> pd.DataFrame:
    """
    Add prediction intervals to a forecast DataFrame.

    Parameters
    ----------
    forecast_df : pd.DataFrame
        DataFrame with forecasts (must have pred_col)
    calibration_df : pd.DataFrame
        DataFrame with calibration data (must have pred_col and actual_col)
    pred_col : str
        Name of prediction column
    actual_col : str
        Name of actual values column
    coverage : float
        Desired coverage

    Returns
    -------
    pd.DataFrame
        Original DataFrame with lower/upper columns added
    """
    result = forecast_df.copy()

    lower, upper, _ = create_conformal_intervals(
        calibration_df[pred_col].values,
        calibration_df[actual_col].values,
        forecast_df[pred_col].values,
        coverage,
    )

    result["lower"] = lower
    result["upper"] = upper
    result["interval_width"] = upper - lower

    return result


# =============================================================================
# DOCUMENTATION
# =============================================================================

PREDICTION_INTERVALS_GOTCHAS = """
=============================================================================
PREDICTION INTERVALS - GOTCHAS AND RECOMMENDATIONS
=============================================================================

1. COVERAGE INTERPRETATION
--------------------------
- 90% coverage means ~90% of future observations should fall within bounds
- This is different from confidence intervals for parameters!
- Prediction intervals are always wider than confidence intervals

2. CHOOSING A METHOD
--------------------
Conformal Prediction (Recommended for most cases):
- No distributional assumptions
- Works with any point forecaster
- Requires calibration set (recent data)
- Best for stationary residuals

Bootstrap:
- Good for generating scenario simulations
- Can capture non-normal residual distributions
- Computationally more expensive
- Also requires calibration data

Parametric:
- Fast and simple
- Assumes normal residuals (often violated)
- May give poor coverage for skewed errors

Expanding Window:
- Use for multi-step forecasts
- Captures growing uncertainty over horizon
- Requires tuning growth_rate parameter

3. CALIBRATION SET SELECTION
-----------------------------
- Use recent historical data (last 30-90 days)
- Should be representative of forecast period
- Avoid data from unusual periods (holidays, anomalies)
- Minimum ~30 samples for reliable quantile estimation

4. COMMON PITFALLS
------------------
- Using training residuals (will underestimate uncertainty!)
- Ignoring non-stationarity (residuals should be stable)
- Symmetric intervals when errors are skewed
- Not validating actual coverage

5. VALIDATING INTERVALS
-----------------------
Check:
- Actual coverage matches nominal (90% should cover ~90%)
- Coverage is consistent across subgroups
- Interval width is reasonable for business use
- No systematic under/over coverage at horizon ends

6. PRACTICAL CONSIDERATIONS
----------------------------
- Intervals must be non-negative for revenue (clip at 0)
- Consider asymmetric intervals for skewed data
- Business users may prefer round numbers
- Document the coverage level clearly

=============================================================================
"""


# =============================================================================
# MAIN / DEMO
# =============================================================================

if __name__ == "__main__":
    print("Prediction Intervals Demo")
    print("=" * 60)

    # Generate synthetic data
    np.random.seed(42)
    n = 100
    x = np.linspace(0, 10, n)
    y_true = 50 + 5 * x + np.random.normal(0, 5, n)
    y_pred = 50 + 5 * x  # Perfect trend, but no noise

    # Split into calibration and test
    cal_idx = n // 2

    print("\n1. Conformal Prediction Intervals:")
    ci = ConformalInterval(coverage=0.90)
    ci.fit(y_true[:cal_idx], y_pred[:cal_idx])
    lower, upper = ci.predict_interval(y_pred[cal_idx:])

    # Evaluate
    metrics = evaluate_coverage(y_true[cal_idx:], lower, upper)
    print(f"   Actual coverage: {metrics['coverage']:.1%}")
    print(f"   Mean width: {metrics['mean_width']:.2f}")

    print("\n2. Bootstrap Intervals:")
    bi = BootstrapInterval(coverage=0.90, n_bootstraps=500)
    bi.fit(y_true[:cal_idx], y_pred[:cal_idx])
    lower_boot, upper_boot = bi.predict_interval(y_pred[cal_idx:])

    metrics_boot = evaluate_coverage(y_true[cal_idx:], lower_boot, upper_boot)
    print(f"   Actual coverage: {metrics_boot['coverage']:.1%}")
    print(f"   Mean width: {metrics_boot['mean_width']:.2f}")

    print("\n3. Parametric Intervals:")
    pi = ParametricInterval(coverage=0.90)
    pi.fit(y_true[:cal_idx], y_pred[:cal_idx])
    lower_param, upper_param = pi.predict_interval(y_pred[cal_idx:])

    metrics_param = evaluate_coverage(y_true[cal_idx:], lower_param, upper_param)
    print(f"   Actual coverage: {metrics_param['coverage']:.1%}")
    print(f"   Mean width: {metrics_param['mean_width']:.2f}")

    print("\n4. Expanding Window Intervals:")
    ewi = ExpandingWindowInterval(coverage=0.90, growth_rate=1.03)
    ewi.fit(y_true[:cal_idx], y_pred[:cal_idx])
    lower_exp, upper_exp = ewi.predict_interval(y_pred[cal_idx:])

    metrics_exp = evaluate_coverage(y_true[cal_idx:], lower_exp, upper_exp)
    print(f"   Actual coverage: {metrics_exp['coverage']:.1%}")
    print(f"   Mean width: {metrics_exp['mean_width']:.2f}")
    print(f"   Width at start: {(upper_exp[0] - lower_exp[0]):.2f}")
    print(f"   Width at end: {(upper_exp[-1] - lower_exp[-1]):.2f}")

    print("\n" + PREDICTION_INTERVALS_GOTCHAS)
