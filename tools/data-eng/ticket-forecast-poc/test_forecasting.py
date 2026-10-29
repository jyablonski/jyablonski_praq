import json
import subprocess
import numpy as np
import pandas as pd
import pytest

from forecasting import (
    SalesModel,
    chronological_split,
    evaluate,
    interval_radius,
    observed_history,
    rollout,
)
from generate_data import FORECAST_DAYS, generate_data
from run import run


@pytest.fixture(scope="module")
def data():
    return generate_data()


@pytest.fixture(scope="module")
def evaluated(data):
    return evaluate(data)


def test_orders_reconcile_to_daily_inventory_and_revenue(data):
    daily = data["daily_sales"]
    orders = data["orders"]
    assert orders["order_id"].is_unique
    assert not daily.duplicated(["game_id", "sale_date"]).any()
    quantities = orders.groupby(["game_id", "sale_date"])["quantity"].sum()
    revenue = orders.groupby(["game_id", "sale_date"])["revenue_usd"].sum()
    indexed = daily.set_index(["game_id", "sale_date"])
    np.testing.assert_array_equal(
        quantities.reindex(indexed.index, fill_value=0), indexed["tickets_sold"]
    )
    np.testing.assert_array_equal(
        revenue.reindex(indexed.index, fill_value=0), indexed["revenue_usd"]
    )
    assert (daily["tickets_sold"] <= daily["remaining_before"]).all()
    assert (daily["cumulative_sold"] <= daily["capacity"]).all()
    np.testing.assert_array_equal(
        daily["remaining_before"] + daily["cumulative_sold"] - daily["tickets_sold"],
        daily["capacity"],
    )
    assert (
        data["price_changes"]["known_at"] < data["price_changes"]["effective_date"]
    ).all()


def test_game_31_has_no_future_sales_or_final_label(data):
    game = data["games"].iloc[-1]
    observed = data["daily_sales"].loc[
        data["daily_sales"]["game_id"] == game["game_id"]
    ]
    assert game["game_number"] == 31
    assert pd.isna(game["final_sold"])
    assert len(observed) == 28
    assert observed["days_out"].min() == FORECAST_DAYS + 1


def test_price_and_profile_changes_have_substantial_learned_effect(data, evaluated):
    model = evaluated[0]
    game = data["games"].iloc[-1]
    observed = observed_history(data["daily_sales"], game["game_id"])
    base = rollout(model, game, observed, 40, False)
    discount = rollout(model, game, observed, 20, False)
    profile = rollout(model, game, observed, 40, True)
    flash = rollout(model, game, observed, 20, False, 3)
    assert -2.2 < model.coefficients[1] < -1.4
    assert model.coefficients[2] > 0
    assert discount[-1]["cumulative_sold"] > base[-1]["cumulative_sold"] + 200
    assert profile[-1]["cumulative_sold"] > base[-1]["cumulative_sold"] + 75
    assert sum(r["tickets_sold"] for r in discount[:3]) > 2.5 * sum(
        r["tickets_sold"] for r in base[:3]
    )
    assert (
        base[-1]["cumulative_sold"]
        < flash[-1]["cumulative_sold"]
        < discount[-1]["cumulative_sold"]
    )
    assert [r["price_usd"] for r in flash] == [20] * 3 + [40] * 11
    for curve in [base, discount, profile, flash]:
        totals = [float(game["observed_sold"])] + [r["cumulative_sold"] for r in curve]
        assert all(a <= b <= 1000 for a, b in zip(totals, totals[1:]))
        expected_revenue = game["observed_revenue_usd"] + sum(
            r["tickets_sold"] * r["price_usd"] for r in curve
        )
        assert curve[-1]["cumulative_revenue_usd"] == pytest.approx(expected_revenue)


def test_fit_learns_price_sign_from_sales_instead_of_hardcoding_it():
    rows = []
    for price in [20, 40, 60]:
        for high_profile in [0, 1]:
            for weekend in [0, 1]:
                for days_out in [7, 21, 35]:
                    rows.append(
                        {
                            "price_usd": price,
                            "high_profile": high_profile,
                            "weekend_game": weekend,
                            "days_out": days_out,
                            "remaining_before": 1000,
                            "tickets_sold": price,
                        }
                    )
    # This deliberately reversed synthetic relationship must produce a positive slope.
    model = SalesModel.fit(pd.DataFrame(rows))
    assert model.coefficients[1] > 0


@pytest.mark.parametrize("history_games", [30, 90])
def test_splits_preserve_entire_games_and_label_availability(history_games):
    data = generate_data(history_games=history_games)
    train, calibration, test = chronological_split(data["games"])
    partitions = [set(frame["game_id"]) for frame in [train, calibration, test]]
    assert not partitions[0] & partitions[1]
    assert not partitions[0] & partitions[2]
    assert not partitions[1] & partitions[2]
    for earlier, later in [(train, calibration), (calibration, test)]:
        assert pd.Timestamp(earlier["event_date"].max()) < pd.Timestamp(
            later["event_date"].min()
        ) - pd.Timedelta(days=14)


def test_holdout_beats_pacing_baseline_and_has_useful_error_range(evaluated):
    _, test, calibration, metrics = evaluated
    assert len(test) == 23
    assert len(calibration) == 12
    assert metrics["mae_tickets"] < metrics["baseline_mae_tickets"]
    assert metrics["mae_tickets"] < 60
    assert 0.75 <= metrics["coverage_80"] <= 1
    assert (test["lower_80"] >= test["sold_at_cutoff"]).all()
    assert (test["upper_80"] <= 1000).all()
    assert interval_radius(np.array([1, 2, 3])) == 1000


def test_report_and_exports_are_reproducible(tmp_path):
    payload = run(tmp_path)
    restored = json.loads((tmp_path / "model_and_results.json").read_text())
    assert restored == payload
    assert "__FORECAST_DATA__" not in (tmp_path / "report.html").read_text()
    for filename in [
        "orders.csv",
        "price_changes.csv",
        "daily_sales.csv",
        "scenarios.csv",
        "daily_forecasts.csv",
        "backtest.csv",
    ]:
        assert (tmp_path / filename).stat().st_size > 0


def test_report_javascript_matches_python_and_controls_work(tmp_path):
    run(tmp_path)
    # Execute the actual offline report with a minimal DOM to check every preset and input.
    harness = r"""
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const html = fs.readFileSync(process.argv[1], 'utf8');
const json = html.match(/<script id="forecast-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const data = JSON.parse(json), nodes = new Map(), buttons = [];
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {value: id === 'price' ? '40' : '14', checked: false, textContent: '', innerHTML: '', listeners: {}, addEventListener(name, fn) {this.listeners[name] = fn;}});
  return nodes.get(id);
}
node('forecast-data').textContent = json;
const presets = ['baseline', 'discount', 'profile', 'flash'].map(preset => ({...node(`preset-${preset}`), dataset: {preset}}));
const scenarios = data.scenarios.map((_, i) => ({...node(`scenario-${i}`), dataset: {scenario: String(i)}}));
buttons.push(...presets, ...scenarios);
const document = {getElementById: node, querySelectorAll: selector => selector === '[data-preset]' ? presets : scenarios};
const context = vm.createContext({document, Intl, Math, Number, JSON});
vm.runInContext(script, context);
for (const row of data.scenarios) {
  const curve = vm.runInContext(`forecast(${row.price_usd}, ${row.high_profile}, ${row.sale_days})`, context);
  assert.ok(Math.abs(curve[13].cumulative_sold - row.final_sold) < 1e-8);
  assert.ok(Math.abs(curve[13].revenue - row.total_revenue_usd) < 1e-8);
}
const baseline = node('final').textContent;
presets[1].listeners.click();
assert.notEqual(node('final').textContent, baseline);
assert.ok(node('curve').innerHTML.includes('<path'));
presets[0].listeners.click();
assert.equal(node('final').textContent, baseline);
presets[2].listeners.click();
assert.equal(node('profile').checked, true);
presets[3].listeners.click();
assert.equal(node('duration').value, 3);
for (const button of scenarios) button.listeners.click();
for (const id of ['price', 'duration', 'profile']) node(id).listeners.input();
assert.ok(!node('curve').innerHTML.includes('NaN'));
assert.ok(!node('equation').textContent.includes('undefined'));
console.log('Report JS: Python parity, presets, scenario buttons, sliders, chart passed.');
"""
    result = subprocess.run(
        ["node", "-e", harness, str(tmp_path / "report.html")],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "passed" in result.stdout


@pytest.mark.parametrize("price", [0, -1, np.nan, np.inf])
def test_invalid_price_is_rejected(data, evaluated, price):
    game = data["games"].iloc[-1]
    with pytest.raises(ValueError, match="positive"):
        rollout(
            evaluated[0],
            game,
            observed_history(data["daily_sales"], game["game_id"]),
            price,
        )


def test_future_sales_cannot_enter_forecast(data, evaluated):
    game = data["games"].iloc[0]
    future_included = data["daily_sales"].loc[
        data["daily_sales"]["game_id"] == game["game_id"]
    ]
    with pytest.raises(ValueError, match="cutoff"):
        rollout(evaluated[0], game, future_included)
