"""Reproducible fictional basketball sales; price plans are assigned before sales."""

from datetime import date, timedelta

import numpy as np
import pandas as pd

CAPACITY = 1_000
SALES_DAYS = 42
FORECAST_DAYS = 14
REFERENCE_PRICE = 40.0


def price_for_day(game, days_out):
    end = game["offer_start_days_out"] - game["offer_duration_days"]
    if end < days_out <= game["offer_start_days_out"]:
        return float(game["offer_price_usd"])
    return float(game["base_price_usd"])


def generate_data(history_games=90, seed=42):
    if history_games < 30 or history_games % 30:
        raise ValueError("Use at least 30 games, in complete 30-game seasons.")

    rng = np.random.default_rng(seed)
    games, daily, orders, price_changes = [], [], [], []
    seasons = history_games // 30
    opponents = ["Harbor Owls", "Valley Bears", "Coastal Foxes", "Metro Monarchs"]

    for index in range(history_games + 1):
        target = index == history_games
        season = seasons if target else index // 30 + 1
        game_number = 31 if target else index % 30 + 1
        season_start = date(2024 + season - 1, 1, 6)
        event_date = season_start + timedelta(
            days=29 * 6 + 21 if target else (game_number - 1) * 6
        )
        high_profile = 0 if target else int(rng.random() < 0.30)
        base_price = 40.0 if target else float(rng.choice([32, 40, 48]))
        offer_multiplier = 1.0 if target else float(rng.choice([0.5, 0.75, 1.0, 1.25]))
        game = {
            "game_id": index + 1,
            "season": season,
            "game_number": game_number,
            "event_date": event_date.isoformat(),
            "opponent": "Metro Monarchs"
            if high_profile
            else opponents[int(rng.integers(3))],
            "capacity": CAPACITY,
            "high_profile": high_profile,
            "weekend_game": int(event_date.weekday() >= 5),
            "base_price_usd": base_price,
            "offer_price_usd": base_price * offer_multiplier,
            "offer_start_days_out": 14 if target else int(rng.choice([7, 14, 21])),
            "offer_duration_days": 14 if target else int(rng.choice([3, 7, 14])),
            "plan_known_at": (event_date - timedelta(days=SALES_DAYS + 1)).isoformat(),
            "is_target": target,
        }
        # Unobserved event interest and daily shocks prevent perfectly predictable sales.
        event_interest = 0.0 if target else rng.normal(0, 0.23)
        sold, revenue, previous_price = 0, 0.0, None
        last_day = FORECAST_DAYS + 1 if target else 1
        for days_out in range(SALES_DAYS, last_day - 1, -1):
            sale_date = (event_date - timedelta(days=days_out)).isoformat()
            price = price_for_day(game, days_out)
            if price != previous_price:
                price_changes.append(
                    {
                        "game_id": game["game_id"],
                        "effective_date": sale_date,
                        "known_at": game["plan_known_at"],
                        "old_price_usd": previous_price,
                        "new_price_usd": price,
                    }
                )
                previous_price = price
            remaining = CAPACITY - sold
            log_odds = (
                -5.0
                - 1.8 * np.log(price / REFERENCE_PRICE)
                + 0.65 * high_profile
                + 0.22 * game["weekend_game"]
                + 0.65 * np.log(43 / (days_out + 1))
                + event_interest
                + rng.normal(0, 0.16)
            )
            sales = int(rng.binomial(remaining, 1 / (1 + np.exp(-log_odds))))
            daily.append(
                {
                    "game_id": game["game_id"],
                    "sale_date": sale_date,
                    "days_out": days_out,
                    "capacity": CAPACITY,
                    "high_profile": high_profile,
                    "weekend_game": game["weekend_game"],
                    "price_usd": price,
                    "remaining_before": remaining,
                    "tickets_sold": sales,
                    "cumulative_sold": sold + sales,
                    "revenue_usd": sales * price,
                }
            )
            tickets_left, order_number = sales, 0
            while tickets_left:
                quantity = min(
                    tickets_left,
                    int(rng.choice([1, 2, 3, 4], p=[0.25, 0.5, 0.15, 0.1])),
                )
                orders.append(
                    {
                        "order_id": f"G{index + 1:03d}-D{days_out:02d}-{order_number:03d}",
                        "game_id": game["game_id"],
                        "sale_date": sale_date,
                        "quantity": quantity,
                        "unit_price_usd": price,
                        "revenue_usd": quantity * price,
                    }
                )
                tickets_left -= quantity
                order_number += 1
            sold += sales
            revenue += sales * price
        game.update(
            {
                "observed_sold": sold,
                "observed_revenue_usd": revenue,
                "final_sold": None if target else sold,
                "sellthrough": None if target else sold / CAPACITY,
            }
        )
        games.append(game)

    return {
        "games": pd.DataFrame(games),
        "daily_sales": pd.DataFrame(daily),
        "orders": pd.DataFrame(orders),
        "price_changes": pd.DataFrame(price_changes),
    }
