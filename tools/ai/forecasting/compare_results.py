"""
Forecasting Comparison Script

Reads results from the output/ directory and creates a unified comparison report.
Run this after running the individual test files.

Usage:
    python compare_results.py
    python compare_results.py --run-missing  # Also run experiments for missing results
"""

import os
import sys
import warnings
from datetime import datetime
from typing import Dict, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# Paths
OUTPUT_DIR = "output"
RESULTS_DIR = "output"


def load_all_results() -> Dict[str, pd.DataFrame]:
    """
    Load all available result files from output directory.

    Expected files:
    - results_statsmodels_arima.csv
    - results_statsmodels_holtwinters.csv
    - results_prophet.csv
    - results_statsforecast.csv
    - results_lightgbm.csv
    - results_ensemble.csv
    """
    results = {}

    # Map of result files to library names
    file_mapping = {
        "results_statsmodels_arima.csv": "statsmodels_arima",
        "results_statsmodels_holtwinters.csv": "statsmodels_hw",
        "results_prophet.csv": "prophet",
        "results_prophet_sale_impact.csv": "prophet_impact",
        "results_statsforecast.csv": "statsforecast",
        "results_statsforecast_multi.csv": "statsforecast_multi",
        "results_lightgbm.csv": "lightgbm",
        "results_lightgbm_ablation.csv": "lightgbm_ablation",
        "results_ensemble.csv": "ensemble",
    }

    for filename, name in file_mapping.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                results[name] = df
                print(f"  Loaded {filename}: {len(df)} rows")
            except Exception as e:
                print(f"  Error loading {filename}: {e}")

    return results


def standardize_results(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Standardize all results into a unified format.

    Required columns: method, library, game, holdout_days, mape, rmse, smape, train_time_sec
    """
    standardized = []

    for source, df in results.items():
        if df.empty:
            continue

        df = df.copy()

        # Determine library from source name
        if "statsmodels" in source:
            df["library"] = "statsmodels"
        elif "prophet" in source and "impact" not in source:
            df["library"] = "prophet"
        elif "statsforecast" in source:
            df["library"] = "statsforecast"
        elif "lightgbm" in source and "ablation" not in source:
            df["library"] = "lightgbm"
        elif "ensemble" in source:
            df["library"] = "ensemble"
        else:
            continue  # Skip non-main results

        # Standardize method column
        if "method" not in df.columns:
            if "name" in df.columns:
                df["method"] = df["name"]
            elif "configuration" in df.columns:
                df["method"] = df["configuration"]
            else:
                df["method"] = source

        # Select standard columns
        std_cols = [
            "method",
            "library",
            "game",
            "holdout_days",
            "mape",
            "rmse",
            "smape",
            "train_time_sec",
        ]
        available_cols = [c for c in std_cols if c in df.columns]

        if "mape" not in available_cols:
            continue

        standardized.append(df[available_cols])

    if not standardized:
        return pd.DataFrame()

    return pd.concat(standardized, ignore_index=True)


def generate_summary_tables(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generate summary tables for the report."""

    tables = {}

    # 1. Overall summary by method
    if not df.empty:
        tables["by_method"] = (
            df.groupby(["library", "method"])
            .agg(
                {
                    "mape": ["mean", "std", "min", "max", "count"],
                    "train_time_sec": ["mean", "sum"],
                }
            )
            .round(2)
        )
        tables["by_method"].columns = [
            "MAPE_avg",
            "MAPE_std",
            "MAPE_min",
            "MAPE_max",
            "n_tests",
            "Time_avg",
            "Time_total",
        ]
        tables["by_method"] = tables["by_method"].sort_values("MAPE_avg")

    # 2. By holdout period
    if "holdout_days" in df.columns:
        tables["by_holdout"] = (
            df.groupby(["holdout_days", "method"])
            .agg({"mape": "mean"})
            .round(2)
            .unstack()
        )
        tables["by_holdout"].columns = tables["by_holdout"].columns.droplevel()

    # 3. By game
    if "game" in df.columns:
        tables["by_game"] = (
            df.groupby(["game", "method"])["mape"].mean().round(2).unstack()
        )

    # 4. Best method per scenario
    if "game" in df.columns and "holdout_days" in df.columns:
        best_methods = []
        for (game, holdout), group in df.groupby(["game", "holdout_days"]):
            if not group.empty:
                best_idx = group["mape"].idxmin()
                best = group.loc[best_idx]
                best_methods.append(
                    {
                        "game": game,
                        "holdout_days": holdout,
                        "best_method": best["method"],
                        "best_library": best["library"],
                        "mape": best["mape"],
                    }
                )
        tables["best_per_scenario"] = pd.DataFrame(best_methods)

    return tables


def print_report(df: pd.DataFrame, tables: Dict[str, pd.DataFrame]):
    """Print formatted comparison report."""

    print("\n" + "=" * 80)
    print("FORECASTING LIBRARY COMPARISON REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    if df.empty:
        print("\nNo results available. Please run the test files first:")
        print("  python test_statsmodels.py")
        print("  python test_prophet.py")
        print("  python test_statsforecast.py")
        print("  python test_lightgbm.py")
        print("  python test_ensemble.py")
        return

    # Data summary
    print(f"\nData Summary:")
    print(f"  Total test runs: {len(df)}")
    print(f"  Libraries tested: {df['library'].nunique()}")
    print(f"  Methods tested: {df['method'].nunique()}")
    if "game" in df.columns:
        print(f"  Games: {df['game'].nunique()}")
    if "holdout_days" in df.columns:
        print(f"  Holdout periods: {sorted(df['holdout_days'].unique())}")

    # Overall ranking
    print("\n" + "-" * 80)
    print("1. OVERALL METHOD RANKING (by average MAPE)")
    print("-" * 80)
    if "by_method" in tables:
        print(tables["by_method"].to_string())

    # By holdout
    if "by_holdout" in tables:
        print("\n" + "-" * 80)
        print("2. MAPE BY HOLDOUT PERIOD")
        print("-" * 80)
        print(tables["by_holdout"].to_string())

    # By game
    if "by_game" in tables:
        print("\n" + "-" * 80)
        print("3. MAPE BY GAME (averaged across holdout periods)")
        print("-" * 80)
        print(tables["by_game"].to_string())

    # Best method per scenario
    if "best_per_scenario" in tables:
        print("\n" + "-" * 80)
        print("4. BEST METHOD PER SCENARIO")
        print("-" * 80)
        print(tables["best_per_scenario"].to_string(index=False))

        # Count wins per library
        wins = tables["best_per_scenario"].groupby("best_library").size()
        print("\n  Wins by library:")
        for lib, count in wins.sort_values(ascending=False).items():
            print(f"    {lib}: {count}")

    # Recommendations
    print("\n" + "-" * 80)
    print("5. RECOMMENDATIONS")
    print("-" * 80)

    if "by_method" in tables and len(tables["by_method"]) > 0:
        best_method = tables["by_method"]["MAPE_avg"].idxmin()
        best_mape = tables["by_method"]["MAPE_avg"].min()

        fastest_idx = tables["by_method"]["Time_avg"].idxmin()
        fastest_time = tables["by_method"]["Time_avg"].min()

        print(f"""
  Best Accuracy: {best_method[1]} ({best_method[0]}) - MAPE: {best_mape:.2f}%
  Fastest:       {fastest_idx[1]} ({fastest_idx[0]}) - Time: {fastest_time:.3f}s
  
  Quick decision guide:
  - Need best accuracy? → Check the top method above
  - Need speed?         → Use statsforecast (fast) or simple baseline
  - Need interpretability? → Use statsmodels Holt-Winters
  - Have sale events?   → Use Prophet with holidays or LightGBM with features
  - Production at scale? → Use statsforecast (handles many series efficiently)
""")


def create_comparison_plots(df: pd.DataFrame, save_path: Optional[str] = None):
    """Create comparison visualizations."""

    if df.empty:
        print("No data to plot")
        return

    # Filter to main methods only (avoid clutter)
    if df["method"].nunique() > 10:
        # Keep only top 10 methods by average MAPE
        top_methods = df.groupby("method")["mape"].mean().nsmallest(10).index
        df = df[df["method"].isin(top_methods)]

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 1. MAPE by method
    ax1 = axes[0, 0]
    method_mape = df.groupby("method")["mape"].agg(["mean", "std"]).sort_values("mean")
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(method_mape)))
    bars = ax1.barh(
        method_mape.index,
        method_mape["mean"],
        xerr=method_mape["std"],
        color=colors,
        capsize=3,
    )
    ax1.set_xlabel("MAPE (%)")
    ax1.set_title("Average MAPE by Method (with std dev)")

    # 2. Training time
    ax2 = axes[0, 1]
    if "train_time_sec" in df.columns:
        time_by_method = df.groupby("method")["train_time_sec"].mean().sort_values()
        ax2.barh(time_by_method.index, time_by_method.values, color="steelblue")
        ax2.set_xlabel("Training Time (seconds)")
        ax2.set_title("Average Training Time by Method")

    # 3. MAPE by holdout period
    ax3 = axes[1, 0]
    if "holdout_days" in df.columns:
        holdout_data = df.groupby(["holdout_days", "library"])["mape"].mean().unstack()
        holdout_data.plot(kind="bar", ax=ax3, width=0.8)
        ax3.set_xlabel("Holdout Period (days)")
        ax3.set_ylabel("MAPE (%)")
        ax3.set_title("MAPE by Holdout Period and Library")
        ax3.legend(title="Library", loc="upper left")
        ax3.tick_params(axis="x", rotation=0)

    # 4. Accuracy vs Speed
    ax4 = axes[1, 1]
    if "train_time_sec" in df.columns:
        method_summary = (
            df.groupby(["method", "library"])
            .agg({"mape": "mean", "train_time_sec": "mean"})
            .reset_index()
        )

        library_colors = {
            "statsmodels": "blue",
            "prophet": "orange",
            "statsforecast": "green",
            "lightgbm": "red",
            "ensemble": "purple",
        }

        for lib in method_summary["library"].unique():
            lib_data = method_summary[method_summary["library"] == lib]
            ax4.scatter(
                lib_data["train_time_sec"],
                lib_data["mape"],
                c=library_colors.get(lib, "gray"),
                label=lib,
                s=100,
                alpha=0.7,
            )

        ax4.set_xlabel("Training Time (seconds)")
        ax4.set_ylabel("MAPE (%)")
        ax4.set_title("Accuracy vs Speed Tradeoff")
        ax4.legend(title="Library")

        # Add Pareto frontier hint
        ax4.axhline(
            y=method_summary["mape"].min() * 1.1,
            color="gray",
            linestyle="--",
            alpha=0.3,
        )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved plot to {save_path}")
    else:
        plt.show()

    return fig


def is_comparison_clean() -> str:
    """
    Document why these comparisons are/aren't clean.
    """
    return """
================================================================================
ARE THESE COMPARISONS CLEAN?
================================================================================

YES, the comparisons are fair because:
✓ Same synthetic data generated from base.py
✓ Same train/test splits (30, 60, 90 day holdouts)
✓ Same evaluation metrics (MAPE, RMSE, SMAPE)
✓ Same games and time periods

CAVEATS to consider:

1. PREDICTION APPROACH
   - Statistical methods: Native multi-step forecasting
   - LightGBM (in quick comparison): Uses test features directly (optimistic)
   - For fair ML comparison, use recursive prediction
   
2. FEATURE ADVANTAGE
   - LightGBM gets engineered features (lags, rolling stats, sale flags)
   - Other methods get raw time series only
   - This is realistic but not apples-to-apples

3. HYPERPARAMETER TUNING
   - All methods use reasonable defaults or auto-selection
   - Results could improve with careful tuning

4. TRAINING TIME
   - Includes one-time compilation overhead (statsforecast, numba)
   - Not a precise benchmark

INTERPRETATION GUIDE:
- Focus on relative rankings, not absolute MAPE values
- Consider your specific needs (speed vs accuracy vs interpretability)
- Always validate on YOUR actual data before choosing
================================================================================
"""


def main():
    """Main comparison function."""

    print("=" * 80)
    print("LOADING FORECASTING RESULTS")
    print("=" * 80)

    # Check if output directory exists
    if not os.path.exists(OUTPUT_DIR):
        print(f"\nOutput directory '{OUTPUT_DIR}' not found.")
        print("Please run the test files first to generate results.")
        return

    # Load results
    print(f"\nLoading results from {OUTPUT_DIR}/")
    results = load_all_results()

    if not results:
        print("\nNo result files found. Please run the test files first:")
        print("  python test_statsmodels.py")
        print("  python test_prophet.py")
        print("  python test_statsforecast.py")
        print("  python test_lightgbm.py")
        print("  python test_ensemble.py")
        return

    # Standardize
    print("\nStandardizing results...")
    unified_df = standardize_results(results)

    if unified_df.empty:
        print("Could not standardize results. Check file formats.")
        return

    print(f"Unified {len(unified_df)} test runs from {len(results)} result files")

    # Save unified results
    unified_path = os.path.join(OUTPUT_DIR, "unified_comparison.csv")
    unified_df.to_csv(unified_path, index=False)
    print(f"Saved unified results to {unified_path}")

    # Generate tables
    tables = generate_summary_tables(unified_df)

    # Print report
    print_report(unified_df, tables)

    # Print comparison validity
    print(is_comparison_clean())

    # Create plots
    print("\nGenerating comparison plots...")
    try:
        plot_path = os.path.join(OUTPUT_DIR, "comparison_plots.png")
        create_comparison_plots(unified_df, plot_path)
    except Exception as e:
        print(f"Could not create plots: {e}")

    return unified_df


if __name__ == "__main__":
    main()
