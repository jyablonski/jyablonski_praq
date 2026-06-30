"""
Game Revenue Forecasting Test Suite

A comprehensive test suite comparing different forecasting libraries
for game revenue prediction.

Modules:
- base: Synthetic data generation, evaluation metrics, visualization
- test_statsmodels: ARIMA, Holt-Winters, seasonal decomposition
- test_prophet: Facebook Prophet with/without sale events
- test_statsforecast: Nixtla's AutoARIMA, AutoETS
- test_lightgbm: Feature engineering with gradient boosting
- test_ensemble: Simple and weighted ensemble methods

Usage:
    from forecast.base import generate_all_games_data
    df = generate_all_games_data()

    # Run specific test suite
    from forecast.test_prophet import run_all_prophet_experiments
    results = run_all_prophet_experiments(df)
"""

from .base import (
    generate_all_games_data,
    generate_game_revenue,
    get_default_game_configs,
    get_default_sale_events,
    time_series_split,
    create_holdout_splits,
    walk_forward_split,
    evaluate_forecast,
    compare_forecasts,
    mape,
    rmse,
    smape,
    mae,
    plot_forecast_comparison,
    plot_train_test_split,
    plot_residuals,
    plot_metrics_comparison,
    plot_game_revenue_overview,
    prepare_for_prophet,
    prepare_for_statsmodels,
    add_calendar_features,
    add_lag_features,
    add_rolling_features,
    GameConfig,
    SaleEvent,
)

__all__ = [
    # Data generation
    "generate_all_games_data",
    "generate_game_revenue",
    "get_default_game_configs",
    "get_default_sale_events",
    "GameConfig",
    "SaleEvent",
    # Train/test splits
    "time_series_split",
    "create_holdout_splits",
    "walk_forward_split",
    # Evaluation
    "evaluate_forecast",
    "compare_forecasts",
    "mape",
    "rmse",
    "smape",
    "mae",
    # Visualization
    "plot_forecast_comparison",
    "plot_train_test_split",
    "plot_residuals",
    "plot_metrics_comparison",
    "plot_game_revenue_overview",
    # Data preparation
    "prepare_for_prophet",
    "prepare_for_statsmodels",
    "add_calendar_features",
    "add_lag_features",
    "add_rolling_features",
]

__version__ = "0.1.0"
