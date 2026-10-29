"""Run: .venv/bin/python tools/data-eng/ticket-forecast-poc/run.py"""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from forecasting import FEATURE_NAMES, evaluate, observed_history, rollout
from generate_data import FORECAST_DAYS, generate_data


def build_report(data, model, test, calibration, metrics, seed, custom=None):
    target = data["games"].iloc[-1].drop(["final_sold", "sellthrough"]).to_dict()
    observed = observed_history(data["daily_sales"], target["game_id"])
    sold = int(target["observed_sold"])
    past_revenue = float(target["observed_revenue_usd"])
    radius = metrics["interval_radius"]
    specs = [
        ("Keep $40", 40, False, 14),
        ("High-profile matchup", 40, True, 14),
        ("50% price cut", 20, False, 14),
        ("High profile + 50% cut", 20, True, 14),
        ("3-day flash sale", 20, False, 3),
        ("Raise to $60", 60, False, 14),
    ]
    if custom:
        specs.append(("Custom CLI scenario", *custom))
    scenarios, forecasts = [], []
    for name, price, high_profile, sale_days in specs:
        curve = rollout(model, target, observed, price, high_profile, sale_days)
        final = curve[-1]
        final_sold = float(final["cumulative_sold"])
        scenarios.append(
            {
                "scenario": name,
                "price_usd": price,
                "high_profile": high_profile,
                "sale_days": sale_days,
                "final_sold": final_sold,
                "additional_sold": final_sold - sold,
                "first_3_day_sales": float(
                    sum(row["tickets_sold"] for row in curve[:3])
                ),
                "sellthrough": final_sold / target["capacity"],
                "lower_80": max(sold, final_sold - radius),
                "upper_80": min(target["capacity"], final_sold + radius),
                "total_revenue_usd": float(final["cumulative_revenue_usd"]),
                "additional_revenue_usd": float(
                    final["cumulative_revenue_usd"] - past_revenue
                ),
            }
        )
        forecasts.extend({"scenario": name, **row} for row in curve)

    history = data["games"].loc[~data["games"]["is_target"]].copy()
    cohort_counts = []
    for high_profile in [0, 1]:
        for price_cut in [False, True]:
            cohort = history.loc[
                (history["high_profile"] == high_profile)
                & (
                    (history["offer_price_usd"] < history["base_price_usd"])
                    == price_cut
                )
            ]
            cohort_counts.append(
                {
                    "high_profile": bool(high_profile),
                    "price_cut": price_cut,
                    "games": len(cohort),
                }
            )
    payload = {
        "seed": seed,
        "target": target,
        "forecast_date": (
            date.fromisoformat(target["event_date"]) - timedelta(days=FORECAST_DAYS)
        ).isoformat(),
        "coefficients": dict(
            zip(FEATURE_NAMES, model.coefficients.tolist(), strict=True)
        ),
        "metrics": metrics,
        "summary": {
            "history_games": len(history),
            "daily_rows": len(data["daily_sales"]),
            "order_rows": len(data["orders"]),
            "price_changes": len(data["price_changes"]),
            "min_sellthrough": float(history["sellthrough"].min()),
            "max_sellthrough": float(history["sellthrough"].max()),
            "min_price": float(data["daily_sales"]["price_usd"].min()),
            "max_price": float(data["daily_sales"]["price_usd"].max()),
        },
        "observed": observed.to_dict("records"),
        "scenarios": scenarios,
        "backtest": test.to_dict("records"),
        "calibration": calibration.to_dict("records"),
        "history": history.to_dict("records"),
        "cohorts": cohort_counts,
    }
    return payload, pd.DataFrame(scenarios), pd.DataFrame(forecasts)


def run(output_dir, history_games=90, seed=42, custom=None):
    data = generate_data(history_games=history_games, seed=seed)
    model, test, calibration, metrics = evaluate(data)
    payload, scenarios, forecasts = build_report(
        data, model, test, calibration, metrics, seed, custom
    )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in data.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    scenarios.to_csv(output_dir / "scenarios.csv", index=False)
    forecasts.to_csv(output_dir / "daily_forecasts.csv", index=False)
    test.to_csv(output_dir / "backtest.csv", index=False)
    calibration.to_csv(output_dir / "calibration.csv", index=False)
    serialized = json.dumps(payload, indent=2, allow_nan=False)
    (output_dir / "model_and_results.json").write_text(serialized + "\n")
    template = Path(__file__).with_name("report_template.html").read_text()
    # Escape '<' so embedded data can never terminate its application/json script.
    report = template.replace("__FORECAST_DATA__", serialized.replace("<", "\\u003c"))
    (output_dir / "report.html").write_text(report)

    print(
        f"Synthetic basketball: {history_games} completed games, 1,000 seats each; seed {seed}."
    )
    print(
        f"{len(data['orders']):,} orders; {len(data['daily_sales']):,} daily sales rows; {len(data['price_changes'])} price records."
    )
    print(f"Game 31: {payload['target']['observed_sold']} sold, 14 selling days left.")
    display = scenarios[
        [
            "scenario",
            "final_sold",
            "additional_sold",
            "first_3_day_sales",
            "total_revenue_usd",
        ]
    ].copy()
    print(display.round(0).to_string(index=False))
    print(
        f"\nChronological holdout ({metrics['test_games']} games): MAE {metrics['mae_tickets']:.1f} tickets; pacing baseline {metrics['baseline_mae_tickets']:.1f}."
    )
    print(
        f"Empirical 80% range: ±{metrics['interval_radius']:.0f} tickets; holdout coverage {metrics['coverage_80']:.0%}; bias {metrics['bias_tickets']:+.1f} tickets."
    )
    print(
        "The same frozen model is used in the holdout and Game 31. No Game 31 future outcomes are generated."
    )
    print(
        "Synthetic price assignments are independent of demand. Real pricing decisions require credible price experiments."
    )
    print(f"\nOpen interactive report: {output_dir.resolve() / 'report.html'}")
    return payload


def main():
    parser = argparse.ArgumentParser(
        description="Generate ticket orders, learn sales drivers, and forecast Game 31."
    )
    parser.add_argument(
        "--history-games",
        type=int,
        default=90,
        help="Completed games in 30-game seasons; default 90.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).with_name("output")
    )
    parser.add_argument(
        "--price",
        type=float,
        help="Also evaluate a custom future price between $16 and $60.",
    )
    parser.add_argument(
        "--high-profile",
        action="store_true",
        help="Make the custom scenario high profile from the cutoff.",
    )
    parser.add_argument(
        "--sale-days",
        type=int,
        default=14,
        help="Custom price duration, starting now (1–14 days).",
    )
    args = parser.parse_args()
    if args.history_games < 30 or args.history_games % 30:
        parser.error("--history-games must be at least 30 and a multiple of 30")
    if not 1 <= args.sale_days <= 14:
        parser.error("--sale-days must be between 1 and 14")
    if args.price is not None and (
        not np.isfinite(args.price) or not 16 <= args.price <= 60
    ):
        parser.error(
            "--price must be finite and between $16 and $60 (the synthetic price range)"
        )
    custom = None
    if args.price is not None or args.high_profile or args.sale_days != 14:
        custom = (
            40 if args.price is None else args.price,
            args.high_profile,
            args.sale_days,
        )
    run(args.output_dir, args.history_games, args.seed, custom)


if __name__ == "__main__":
    main()
