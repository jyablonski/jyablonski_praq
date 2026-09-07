# Dynamic Pricing

Dynamic pricing adjusts the price of an offer as demand, available supply, time, or market conditions change. For a booking platform, the offer might be a hotel room for a particular night, a concert seat, or a venue time slot. Prices can move up or down, and updates can happen on a schedule or in response to events; neither real-time infrastructure nor machine learning is required.

This note focuses on booking and capacity-constrained businesses, with comparisons to retail and marketplaces. The rollout guidance is a practical synthesis of the linked sources, not a universal sequence tied to company age or funding round.

## The Business Use Case

A fixed price can leave a business with two problems: selling scarce capacity too cheaply when demand is strong and leaving capacity unused when demand is weak. A hotel cannot sell last night's empty room tomorrow. Dynamic pricing helps decide how much to charge now while preserving the opportunity to sell remaining capacity later.

The business objective should be explicit. Revenue, profit, occupancy, and marketplace reliability are related, but optimizing one does not automatically optimize the others. Contribution is the revenue the business keeps minus variable costs; it still needs to cover fixed costs before the business earns a profit.

| Business | Problem pricing can address | Outcome to measure |
| --- | --- | --- |
| Hotels, venues, flights, and ticketed events | Capacity is limited and expires at a particular time | Contribution from available capacity over the full booking window |
| Ride-hailing and delivery marketplaces | Demand can exceed available service capacity in a location | Completed transactions, wait times, supplier participation, and contribution |
| Retail | Stock, competing offers, and demand change; seasonal inventory loses value | Contribution after returns and fulfillment costs, plus sell-through |
| B2B quoting | Costs and deal characteristics vary, while manual quoting is slow | Deal contribution, win rate, and quote turnaround time |

For example, Uber describes surge pricing as a way to shift rider demand and encourage drivers toward busy areas, improving availability. That is a marketplace balancing problem as well as a revenue decision; the exact mechanics vary by market. [Uber: surge pricing](https://www.uber.com/us/en/marketplace/pricing/surge-pricing/).

For a platform, distinguish the customer's total booking value from the platform's own economics. A higher room price may increase commission per booking but reduce completed bookings or host retention. Decide who controls the price, who funds discounts, and whether the objective belongs to the supplier, the platform, or both.

### A Simple Example

Suppose a venue has 100 comparable time slots in a month. These are invented outcomes to illustrate the tradeoff, not predicted results:

| Policy | Slots sold | Revenue | Variable cost at $20 per booking | Contribution before fixed costs |
| --- | --- | --- | --- | --- |
| Fixed price of $100 | 70 | $7,000 | $1,400 | $5,600 |
| $130 for 40 peak slots; $80 for 40 off-peak slots | 80 | $8,400 | $1,600 | $6,800 |
| Discount everything to $70 | 100 | $7,000 | $2,000 | $5,000 |

Full occupancy produces less contribution than either alternative here. Scheduled peak and off-peak prices capture predictable differences; a dynamic policy would also revise future offers when actual bookings differ from expectations. Whether either approach creates incremental profit requires a credible comparison with what would have happened otherwise.

Dynamic pricing is most useful when demand varies, price influences purchase decisions, and the business can reliably change offers. When the real problem is poor product fit, limited awareness, or unreliable service, changing prices may do little. Predictable subscriptions or negotiated contracts may be better served by stable plans and periodic pricing reviews.

## Related Concepts

- **Scheduled or tiered pricing:** Predetermined weekend rates, early-bird deadlines, or blocks of tickets at different prices. These can be a first step; a fixed calendar alone does not react to unexpected demand.
- **Revenue management:** The broader discipline of managing price and availability, including which inventory to offer, minimum stays, and booking restrictions. Dynamic pricing is one tool within it.
- **Price fences:** Explicit conditions that separate offers, such as refundable versus non-refundable bookings, advance purchase, or bundles. They let customers choose different terms; they do not automatically make a policy fair or profitable.
- **Personalized pricing:** Different prices based on information about an individual shopper. Dynamic pricing can instead give everyone shopping for the same offer under the same conditions the same current price. Personal data is not a prerequisite. [IATA: dynamic pricing, continuous pricing, and dynamic bundling](https://www.iata.org/contentassets/0688c780d9ad4a4fadb461b479d64e0d/dynamic-pricing_continuous-pricing_dynamic-bundling.pdf).

## How It Works

The operational loop is: observe the market, estimate what might sell, choose a permitted price, publish it, and measure the outcome. Recalculating prices and retraining a model are separate activities; a system can reprice frequently using a model trained less often.

### 1. Define the Offer and Collect Signals

Start with a clear pricing unit: for example, one room type on one stay date with a specified cancellation policy. Keep the product, terms, currency, taxes, and fees identifiable so comparisons mean something.

| Signal | Examples | Main limitation |
| --- | --- | --- |
| Demand | Booking pace, searches, quote-to-book conversion, comparable booking history | Page views may include bots, repeat visits, or low-intent traffic |
| Supply | Sellable units, temporary holds, cancellations, closures | Stale inventory can create false scarcity |
| Time | Days until the booking date, day of week, season, holidays | Compare bookings at the same lead time |
| Market context | Local events and comparable public competitor offers | A different room, refund policy, or fee structure is not an equivalent offer |
| Economics | Variable service costs, commissions, payment costs, funded discounts | Gross sales can rise while contribution falls |

A **booking curve** tracks cumulative bookings against time remaining before the service date. If comparable Saturdays are usually 40% booked four weeks out and this Saturday is 70% booked, that is a reason to investigate stronger demand. The same 70% occupancy one day before arrival could imply a very different decision.

Log the prices people actually saw, the available inventory and terms, and subsequent purchases, cancellations, or refunds. Sales records alone omit unsuccessful offers. A non-purchase is useful evidence only when exposure is known; it does not prove that price caused the rejection. Stockouts also hide demand that could not be fulfilled.

### 2. Choose a Pricing Method

**Rules** map conditions to prices or bounded adjustments. An illustrative daily policy could raise a future date's price by 5% when net booking pace is materially ahead of comparable dates, reduce it by 5% when behind, and otherwise hold. Apply floors, ceilings, a minimum observation volume, and a cooldown between changes. Those thresholds are examples to calibrate, not industry defaults. A single occupancy threshold without lead time or recent price history can repeatedly raise prices without new evidence.

**Forecasting and optimization** estimate demand at candidate prices, then select a price under business constraints. Price elasticity describes how demand changes in percentage terms when price changes. A simplified model for one selling interval is:

```text
expected_contribution(price) =
    (net_revenue_per_sale(price) - variable_cost_per_sale)
    * expected_units_sold(price)

Choose the allowed price with the highest expected contribution.
Expected units sold cannot exceed available inventory.
```

For expiring capacity, optimizing only the next interval is incomplete. Selling the last room cheaply today can displace a more valuable booking tomorrow. A fuller optimizer accounts for the expected future value of remaining inventory, often called its opportunity cost. This also explains why last-minute prices need not always drop. [Fiig, Le Guen, and Gauchet: dynamic pricing of airline offers](https://www.iata.org/contentassets/0688c780d9ad4a4fadb461b479d64e0d/dynamic-pricing--of-airline-offers.pdf).

**Machine learning** can improve forecasts and estimates of customer response across many dates or products. It does not remove the need to specify the objective and constraints. Historical prices are often already higher on busy dates, so a naive model may conclude that higher prices cause more demand. This is price endogeneity: the factors driving demand also influenced historical pricing. Research on hotel pricing explicitly addresses this problem and sparse observations. [Zhu et al.: modeling price elasticity for hotel dynamic pricing](https://arxiv.org/abs/2208.03135).

**Bandits and reinforcement learning** additionally consider how pricing decisions generate information or affect future outcomes. They are options for specific learning problems, not prerequisites for a mature pricing system. Research illustrates the difficulty of jointly learning demand and maximizing revenue; ordinary forecasting plus constrained optimization remains a valid design. [Qiang and Bayati: dynamic pricing with demand covariates](https://arxiv.org/abs/1604.07463).

### 3. Apply Controls, Publish, and Learn

Validate the proposed price against business rules, then publish an identifiable price version with an effective time. Keep an audit trail linking inputs, the recommendation, any human override, the displayed quote, and the final charge.

Measure outcomes over the relevant booking window, including cancellations and displaced demand, before deciding whether a policy improved results. A retrospective can identify forecast errors; it cannot establish that the chosen prices were optimal because outcomes under alternative prices are unobserved.

## What Early Versus Late Stage Companies Usually Roll Out

The useful distinction is **pricing maturity**: repeatable transactions, usable data, operational capacity, and proven economic value. The table is a planning guide, not an empirical claim that every startup or enterprise follows these stages. In retail, McKinsey describes starting with a subset of pricing capabilities and expanding through pilots; its B2B work emphasizes business ownership and adoption alongside analytics. [McKinsey: retail dynamic pricing](https://www.mckinsey.com/industries/retail/our-insights/how-retailers-can-drive-profitable-growth-through-dynamic-pricing), [McKinsey: B2B dynamic pricing](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/what-really-matters-in-b2b-dynamic-pricing).

| Stage | Typical rollout pattern | What should justify the next step |
| --- | --- | --- |
| Early business, limited history | Base prices, peak/off-peak schedules, simple inventory or booking-pace rules, manual review, or an existing vendor tool | Repeated evidence of missed pricing opportunities and trustworthy offer/booking data |
| Growing, repeatable business | Automated rules, comparable-date forecasts, recommendations for operators, and controlled pilots in selected inventory | Measured contribution improvement, dependable publishing, and manageable exceptions |
| Mature pricing operation | Elasticity or choice models, constrained optimization, coordination across related products and channels, and automated routine decisions | Additional value beyond the existing rules after operating costs and customer effects |
| Specialized high-volume operation | Faster market feedback, richer demand/supply models, and possibly bandits or reinforcement learning | A specific sequential decision problem, enough observations, and a safe way to evaluate learning policies |

### Early Stage Priorities

Give a commercial or operations owner responsibility for the policy, supported by engineering or analytics as needed. Start with a narrow scope such as one venue category or room type, a base rate, a few explainable rules, a preview, manual override, and a fallback price. A scheduled job that writes approved future prices can be sufficient; a separate real-time service is not automatically necessary.

Instrument the current experience before introducing complicated models. Google’s production ML guidance recommends establishing metrics, using simple heuristics when data is missing, and keeping the first model and pipeline simple. Applied here, that means proving the price can be served and measured correctly before trying to optimize every contextual signal. [Google: rules of machine learning](https://developers.google.com/machine-learning/guides/rules-of-ml).

Buying a tool can bring sophisticated pricing to a small operator. Airbnb's Smart Pricing, for example, adjusts nightly prices while allowing hosts to set a range and override specific dates. A small business using such a product does not need to reproduce the underlying models. [Airbnb: Smart Pricing](https://www.airbnb.com/help/article/1168).

### Later Stage Priorities

Invest in better estimates of price response, cancellation behavior, substitution between offers, and the value of holding capacity. Expand automation where outcomes are predictable, retaining review for unusual events or weak data. Mature airline offer systems illustrate the broader integration challenge: changing pricing can also require changes to distribution, order handling, accounting, and reporting. [IATA: Dynamic Offers](https://www.iata.org/en/programs/airline-distribution/retailing/dynamic-offers/).

Assign clear ownership across commercial teams, data science, engineering, finance, and support. Commercial teams own objectives and exceptions; analysts estimate impact; engineers own reliable execution. More mature operations need those responsibilities covered, even if they do not each require a separate team.

There is no universal transaction count or company size that makes ML worthwhile. Look for enough observations across comparable offers and price levels, evidence that current rules miss valuable patterns, and benefits that exceed development or vendor costs. A mature low-volume business may sensibly retain rules and human judgment.

For build versus buy, evaluate integration quality, override controls, data access, auditability, experimentation support, and total cost. Building is easier to justify when pricing depends on unusual inventory constraints or is central to the product's differentiation.

## A Practical Rollout Sequence

1. **Establish the baseline.** Define the primary economic metric, customer and supplier guardrails, price authority, and the current policy to compare against. Audit offer, inventory, and transaction data.
1. **Run in shadow mode.** Generate recommendations without publishing them. Investigate unexpected prices, stale inputs, discount interactions, and operational exceptions. This checks behavior, not revenue uplift.
1. **Pilot with review.** Let operators inspect a limited set of recommendations. Record why they override them and adjust rules where the business context is missing.
1. **Evaluate a controlled rollout.** Compare policies using suitable randomized groups where feasible, with a preplanned duration and analysis. Include enough of the booking and cancellation cycle to avoid mistaking earlier purchases for additional demand.
1. **Expand selectively.** Automate routine cases after showing economic value and meeting guardrails. Keep a holdout where feasible, monitor longer-term outcomes, and retain a tested rollback.

Ordinary user-level A/B tests can be misleading when both groups compete for the same rooms, seats, or drivers. DoorDash describes randomizing geographic areas and time windows through switchback experiments to reduce marketplace interference. For advance bookings, effects can persist as inventory sells, so short switchbacks may be unsuitable; separate inventory/date clusters or other designs may be needed. Choose the design and statistical analysis around those dependencies. [DoorDash: switchback experiments](https://careersatdoordash.com/blog/switchback-tests-and-randomized-experimentation-under-network-effects-at-doordash/).

## Best Practices

### Protect Economics and Customer Trust

- **Optimize contribution over a meaningful horizon.** Include commissions, variable fulfillment costs, discounts, refunds, and displacement of other purchases. Check whether apparent growth merely shifts bookings between dates, products, or channels.
- **Enforce bounds on the final offer.** Check discount stacking and minimum margins after adjustments. Airbnb specifically notes that discounts can push a guest's price below the configured Smart Pricing minimum, illustrating why an engine-level floor may not be a final-price floor. [Airbnb: discount interactions](https://www.airbnb.com/help/article/1168).
- **Make the buying experience predictable.** Explain that future offers may change, honor confirmed bookings, and define a clear quote-validity window. Avoid repeatedly changing an active checkout price. Use genuine reference prices and availability claims; artificial crossed-out prices or scarcity messages undermine trust.
- **Use understandable offer differences.** Refundability, purchase timing, and included services can explain price differences. Review cancellation-and-rebooking incentives and whether repeated discounts teach customers to postpone purchases. An upward-only policy is not automatically fairer or more profitable.

### Make the System Reliable

- **Match cadence to the market.** Daily updates may suit advance bookings; a rapidly changing local marketplace may need much faster decisions. Reprice when new information warrants it, with change limits and cooldowns to prevent noisy oscillation.
- **Treat checkout as a transaction.** Validate quote expiry and reserve inventory with concurrency controls. A locked price alone does not reserve a room; define whether both price and inventory are guaranteed and for how long.
- **Coordinate channels explicitly.** Third-party updates can be delayed or rejected; do not assume one atomic update across independent platforms. Use versioning, acknowledgments, retries, reconciliation, and alerts for stale offers. Deliberate channel differences should reflect an approved policy and applicable agreements.
- **Keep a fallback and an accountable operator.** If inventory, demand inputs, or the pricing service are unreliable, stop automatic changes and use an approved safe policy. Retain manual overrides, reason codes, and a way to disable or roll back the policy without breaking checkout.
- **Treat weak data conservatively.** Group comparable offers where justified, represent uncertainty, filter bots, and avoid treating sold-out periods as zero demand. Test price response carefully rather than extrapolating far beyond observed prices.

### Set Data and Legal Boundaries

Dynamic pricing does not require profiling a person's income, browsing history, or sensitive traits. Prefer offer and market signals unless there is a clear, reviewed reason to use individual data. The FTC's January 2025 staff findings describe intermediaries capable of using granular consumer data for individualized prices and promotions; the published examples are hypothetical, not proof that every retailer uses those practices. [FTC: surveillance pricing findings](https://www.ftc.gov/news-events/news/press-releases/2025/01/ftc-surveillance-pricing-study-indicates-wide-range-personal-data-used-set-individualized-consumer).

Make total prices and fee explanations accurate. In the US, the FTC's rule effective May 12, 2025 requires covered live-event ticket and short-term lodging offers to show mandatory fees upfront, with specified exclusions such as government charges. Its guidance expressly permits non-misleading dynamic pricing; it is not a blanket ban on changing prices. Check the rules for the actual market and product. [FTC: unfair or deceptive fees FAQ](https://www.ftc.gov/business-guidance/resources/rule-unfair-or-deceptive-fees-frequently-asked-questions).

Set emergency pricing controls and review local restrictions before rollout. Airbnb documents that it may suspend Smart Pricing during emergencies. Independently determine prices and scrutinize vendors that pool competitors' nonpublic pricing information; algorithmic recommendations do not remove competition-law concerns. [Airbnb: emergency controls](https://www.airbnb.com/help/article/1168), [DOJ: RealPage pricing and information-sharing enforcement](https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and).

## Metrics to Monitor

| Metric | What it tells you |
| --- | --- |
| Incremental contribution versus the baseline | Whether pricing creates economic value after variable costs |
| Revenue or contribution per available slot/room-night | Combines price and utilization instead of rewarding occupancy alone |
| Conversion, booking pace, and final sell-through | Whether demand is changing and capacity is selling too early or remaining unused |
| Cancellations, refunds, repeat bookings, complaints, and supplier retention | Whether short-term gains carry customer or marketplace costs |
| Wait times and fulfillment rates, where relevant | Whether pricing improves service availability |
| Override rate, bound hits, stale quotes, and publish failures | Whether recommendations are trusted and prices execute correctly |

Review results by product, location, booking lead time, and channel as well as in aggregate. Expand the policy when improvement survives a credible comparison and customer, supplier, and operational guardrails remain acceptable.
