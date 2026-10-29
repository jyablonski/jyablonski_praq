"""An interpretable binomial GLM, inventory rollout, and chronological evaluation."""

from dataclasses import dataclass
from datetime import date, timedelta
from math import ceil

import numpy as np
import pandas as pd

from generate_data import FORECAST_DAYS, REFERENCE_PRICE, price_for_day

FEATURE_NAMES = [
    "intercept",
    "log_price_ratio",
    "high_profile",
    "weekend_game",
    "urgency",
]


def design_matrix(rows):
    return np.column_stack(
        [
            np.ones(len(rows)),
            np.log(np.asarray(rows["price_usd"], dtype=float) / REFERENCE_PRICE),
            rows["high_profile"],
            rows["weekend_game"],
            np.log(43 / (np.asarray(rows["days_out"], dtype=float) + 1)),
        ]
    )


def sigmoid(values):
    return 1 / (1 + np.exp(-np.clip(values, -30, 30)))


@dataclass
class SalesModel:
    coefficients: np.ndarray

    @classmethod
    def fit(cls, daily):
        usable = daily.loc[daily["remaining_before"] > 0]
        if usable.empty:
            raise ValueError("Training needs rows with available inventory.")
        x = design_matrix(usable)
        trials = usable["remaining_before"].to_numpy(dtype=float)
        sold = usable["tickets_sold"].to_numpy(dtype=float)
        rate = np.clip(sold.sum() / trials.sum(), 1e-6, 1 - 1e-6)
        beta = np.array([np.log(rate / (1 - rate)), 0, 0, 0, 0])
        penalty = np.diag([0, 0.01, 0.01, 0.01, 0.01])
        for _ in range(60):
            probability = sigmoid(x @ beta)
            weights = trials * probability * (1 - probability)
            gradient = x.T @ (sold - trials * probability) - penalty @ beta
            information = (x.T * weights) @ x + penalty
            step = np.linalg.solve(information, gradient)
            beta += step
            if np.max(np.abs(step)) < 1e-8:
                return cls(beta)
        raise RuntimeError("Binomial fit did not converge.")

    def probabilities(self, rows):
        return sigmoid(design_matrix(rows) @ self.coefficients)


def observed_history(daily, game_id):
    return daily.loc[
        (daily["game_id"] == game_id) & (daily["days_out"] > FORECAST_DAYS)
    ]


def rollout(
    model, game, observed, price=None, high_profile=None, sale_days=FORECAST_DAYS
):
    if price is not None and (not np.isfinite(price) or price <= 0):
        raise ValueError("Price must be finite and positive.")
    if not 1 <= sale_days <= FORECAST_DAYS:
        raise ValueError("Sale duration must be between 1 and 14 days.")
    if observed.empty or (observed["days_out"] <= FORECAST_DAYS).any():
        raise ValueError("Only sales before the 14-day forecast cutoff are allowed.")
    sold = float(observed.iloc[-1]["cumulative_sold"])
    revenue = float(observed["revenue_usd"].sum())
    event_date = date.fromisoformat(game["event_date"])
    future = []
    for days_out in range(FORECAST_DAYS, 0, -1):
        active_offer = price is not None and days_out > FORECAST_DAYS - sale_days
        day_price = price if active_offer else price_for_day(game, days_out)
        future.append(
            {
                "days_out": days_out,
                "sale_date": (event_date - timedelta(days=days_out)).isoformat(),
                "price_usd": float(day_price),
                "high_profile": game["high_profile"]
                if high_profile is None
                else int(high_profile),
                "weekend_game": game["weekend_game"],
            }
        )
    probabilities = model.probabilities(pd.DataFrame(future))
    for row, probability in zip(future, probabilities, strict=True):
        remaining = max(0.0, game["capacity"] - sold)
        sales = remaining * float(probability)
        sold += sales
        revenue += sales * row["price_usd"]
        row.update(
            {
                "tickets_sold": sales,
                "cumulative_sold": sold,
                "cumulative_revenue_usd": revenue,
            }
        )
    return future


def chronological_split(games):
    completed = games.loc[~games["is_target"]].sort_values("event_date")
    train_count = int(len(completed) * 0.55)
    calibration_count = max(3, int(len(completed) * 0.14))
    # Three six-day event gaps keep completed labels before the next forecast cutoff.
    train = completed.iloc[:train_count]
    calibration = completed.iloc[train_count + 3 : train_count + 3 + calibration_count]
    test = completed.iloc[train_count + calibration_count + 6 :]
    if calibration.empty or test.empty:
        raise ValueError("Not enough completed games for chronological evaluation.")
    for earlier, later in [(train, calibration), (calibration, test)]:
        latest_label = date.fromisoformat(earlier["event_date"].max())
        first_cutoff = date.fromisoformat(later["event_date"].min()) - timedelta(
            days=FORECAST_DAYS
        )
        if latest_label >= first_cutoff:
            raise ValueError(
                "Evaluation labels would not exist before the next forecast cutoff."
            )
    return train, calibration, test


def interval_radius(errors, capacity=1000, coverage=0.8):
    if not len(errors):
        raise ValueError("Calibration requires completed games.")
    rank = ceil((len(errors) + 1) * coverage)
    # With very few calibration games, a finite empirical quantile cannot support 80%.
    return float(capacity if rank > len(errors) else np.sort(np.abs(errors))[rank - 1])


def evaluate(data):
    games, daily = data["games"], data["daily_sales"]
    train, calibration, test = chronological_split(games)
    train_daily = daily.loc[daily["game_id"].isin(train["game_id"])]
    model = SalesModel.fit(train_daily)
    train_final = train_daily.groupby("game_id")["cumulative_sold"].max()
    train_cutoff = train_daily.loc[
        train_daily["days_out"] == FORECAST_DAYS + 1
    ].set_index("game_id")["cumulative_sold"]
    pacing_fraction = float((train_cutoff / train_final).median())

    def replay(partition):
        records = []
        for game in partition.to_dict("records"):
            observed = observed_history(daily, game["game_id"])
            final = rollout(model, game, observed)[-1]["cumulative_sold"]
            actual = float(game["final_sold"])
            baseline = min(
                game["capacity"],
                float(observed.iloc[-1]["cumulative_sold"]) / pacing_fraction,
            )
            records.append(
                {
                    "game_id": game["game_id"],
                    "event_date": game["event_date"],
                    "forecast_date": (
                        date.fromisoformat(game["event_date"])
                        - timedelta(days=FORECAST_DAYS)
                    ).isoformat(),
                    "high_profile": game["high_profile"],
                    "actual_final_sold": actual,
                    "forecast_final_sold": final,
                    "pacing_baseline": baseline,
                    "error": final - actual,
                    "sold_at_cutoff": float(observed.iloc[-1]["cumulative_sold"]),
                }
            )
        return pd.DataFrame(records)

    calibration_results = replay(calibration)
    radius = interval_radius(calibration_results["error"].to_numpy())
    results = replay(test)
    results["lower_80"] = np.maximum(
        results["sold_at_cutoff"], results["forecast_final_sold"] - radius
    )
    results["upper_80"] = np.minimum(1000, results["forecast_final_sold"] + radius)
    metrics = {
        "train_games": len(train),
        "calibration_games": len(calibration),
        "test_games": len(test),
        "embargo_games": len(games) - 1 - len(train) - len(calibration) - len(test),
        "mae_tickets": float(results["error"].abs().mean()),
        "baseline_mae_tickets": float(
            (results["pacing_baseline"] - results["actual_final_sold"]).abs().mean()
        ),
        "bias_tickets": float(results["error"].mean()),
        "coverage_80": float(
            (
                (results["actual_final_sold"] >= results["lower_80"])
                & (results["actual_final_sold"] <= results["upper_80"])
            ).mean()
        ),
        "interval_radius": radius,
        "training_last_event": train["event_date"].max(),
        "calibration_first_event": calibration["event_date"].min(),
        "calibration_last_event": calibration["event_date"].max(),
        "test_first_event": test["event_date"].min(),
        "test_last_event": test["event_date"].max(),
    }
    return model, results, calibration_results, metrics
