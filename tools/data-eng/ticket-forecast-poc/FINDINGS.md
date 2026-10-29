# Ticket sales forecast: PoC findings

## Business problem

Unsold seats lose their value when a game starts. Teams need to spot weak sales early and decide whether a discount could bring in enough buyers to justify the lower price. Popular games create a different question: will tickets sell at full price?

## What we forecast and why

We estimate how many tickets Game 31 will sell before tipoff and how much ticket revenue it will bring in under different prices and matchup conditions. This helps compare keeping prices steady, running a sale, or raising prices.

The game has 213 tickets sold, $8,520 collected, 787 seats left, and 14 selling days remaining. Every scenario starts there. Price changes affect future buyers, and the high-profile scenario assumes new matchup or star-player news today.

## How the script works

1. Generate 90 fictional basketball games across three seasons, each with 1,000 seats and 42 selling days. The data contains 25,149 orders, price changes, and daily sales. Games finish with 24%–91% of seats sold. Using 90 games gives us more examples of different prices and matchups than 30 alone.
1. Learn how price, matchup, weekends, and time left relate to daily sales. Each day, estimate the chance that an unsold seat sells, add those purchases, and reduce the seats left. Total sales cannot exceed 1,000.
1. Use 49 earlier games to learn the model, 12 later games to set an error range, and 23 later games to test it. Six games separate those groups so earlier results are known before later forecasts are made.
1. Forecast Game 31 using that same model. Past purchases stay fixed, and the script never generates the game's future actual sales. Historical price plans were known in advance, so the test does not rely on future information.

## Results

| Scenario | Expected final sold | Sales in next 3 days | Total ticket revenue |
| --- | ---: | ---: | ---: |
| Keep $40 | 428 | 33 | $17,111 |
| High-profile matchup at $40 | 535 | 53 | $21,415 |
| Cut price to $20 for 14 days | 731 | 106 | $18,875 |
| High profile plus $20 for 14 days | 862 | 166 | $21,496 |
| Cut price to $20 for 3 days, then return to $40 | 483 | 106 | $17,217 |
| Raise price to $60 for 14 days | 326 | 16 | $15,296 |

Values are rounded. Revenue includes past purchases and excludes costs, fees, taxes, and refunds.

- **Accuracy:** Across the 23 test games, forecasts missed final sales by 34 tickets on average. A simpler method based on typical sales progress missed by 54, so this model reduced average error by about 37%. It still predicted about 18 too few tickets on average.
- **Uncertainty:** The $40 forecast is 428 tickets, with an estimated 80% range of 356–499. The ranges contained actual sales for 22 of 23 test games. That small sample does not guarantee the same coverage for future games or each scenario.

## Final findings

- **Price changes matter:** A sustained 50% cut raises expected final sales from 428 to 731. Expected purchases over the next three days rise from 33 to 106.
- **Matchup matters:** A high-profile game adds about 108 final sales at the same $40 price. The model learns this pattern from historical examples.
- **Sale length matters:** A three-day discount creates a fast sales spike but finishes at 483 tickets, well below the sustained discount's 731.
- **More buyers can add little revenue:** For a high-profile game, halving the price adds roughly 326 sales but only about $82 in revenue, using unrounded estimates. The best option depends on whether the goal is ticket revenue, attendance, or both.
- **Trust is limited to this example:** The dummy data was built with strong price and matchup effects. Real teams often discount games because sales are weak, which makes the true price effect harder to separate. Before using this for decisions, test it on real games and run price experiments. This example also leaves out seating tiers, refunds, costs, and buyers switching between games.

Open the [interactive report](output/report.html) to change inputs and inspect forecasts, sales records, and test results. All 14 automated checks passed, including checks that orders add up, future sales stay out of forecast inputs, and the report matches the Python forecasts.

Run from the repository root:

```bash
.venv/bin/python tools/data-eng/ticket-forecast-poc/run.py
```
