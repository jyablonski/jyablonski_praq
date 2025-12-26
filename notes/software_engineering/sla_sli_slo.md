# SLA, SLI, SLO

## SLAs

Service Level Agreements (SLAs) are formal agreements between a service provider and a customer that outline the expected level of service. They usually include metrics such as uptime, response time, and resolution time.

Responsibilities:

- Defined by Executive Management: The overall objectives and parameters of the SLA are typically defined by executive management in collaboration with key stakeholders. This includes setting targets for service quality and availability that align with business goals and customer expectations.
- Technical Engineers' Role: Technical engineers play a crucial role in ensuring that the services meet the requirements outlined in the SLA. They are responsible for implementing, monitoring, and maintaining the systems and processes necessary to achieve the agreed-upon service levels.

Example: A cloud service provider offers an SLA guaranteeing 99.99% uptime for their platform. This means that they commit to ensuring that their service will be available for at least 99.99% of the time within a specified period, such as a month or a year. If they fail to meet this uptime guarantee, they may offer compensation or credits to the customer.

Example 2: Alternatively, could also work in clauses to handle unplanned downtime outages like below:

- Cloud Service Company X commits to restoring service within 1 hour (60 minutes) of detecting the outage.
- Company X further guarantees that in the event of prolonged downtime beyond 1 hour, compensatory measures such as service credits or refunds will be provided to Company Y.
- TL:DR we want 24/7 uptime but if there is an issue it needs to be resolved within 1 hour or there will be consequences.
- SLAs are a binding agreement between a service provider and 1 or more customers

## SLOs

Service Level Objectives (SLOs) are specific, measurable goals set for individual aspects of a service, such as response time, availability, or throughput. They are used to define the acceptable level of performance for a service.

Responsibilities:

- Defined by Executive Management: While executive management may provide input on overall business objectives and priorities, SLOs are often defined by technical teams in collaboration with stakeholders who understand the technical aspects of the service. Executive management may review and approve these objectives to ensure they align with broader business goals.
- Technical Engineers' Role: Technical engineers are primarily responsible for setting realistic and achievable SLOs based on the capabilities of the systems and infrastructure they manage. They monitor performance against these objectives and take corrective actions when necessary to meet or exceed them.

Example: A software-as-a-service (SaaS) company sets an SLO for their API response time, aiming for 95% of requests to be processed within 100 milliseconds. This means that they have defined a performance target for the speed at which their API responds to incoming requests. They monitor their system continuously to ensure that it meets or exceeds this response time target.

- SLOs are specific, measurable KPIs set by a service provider for a specific service of theirs

## SLIs

Service Level Indicators (SLIs) are specific metrics used to measure the performance of a service. They provide the data needed to assess whether SLOs and SLAs are being met.

- Error Budgets: Error budgets represent the acceptable level of service degradation or downtime within a given timeframe. They are often used in conjunction with SLOs to balance the need for innovation and reliability.
- Example: A website hosting company uses SLIs such as server response time, error rate, and request throughput to measure the performance of their hosting service. They collect data on these metrics continuously and use them to evaluate the health and reliability of their infrastructure.

### Example

| Layer | Example                                         |
| ----- | ----------------------------------------------- |
| SLI   | Measured latency p99 = 180ms; error rate = 0.3% |
| SLO   | p99 latency < 200ms; error rate < 0.5%          |
| SLA   | "99.9% availability per month or 10% credit"    |

The relationship flows upward: you measure SLIs, set internal SLOs against them (with error budgets for when you can deploy risky changes vs. focus on reliability), and your SLA is the external promise you're confident you can keep because your SLOs have margin built in.

- SLAs are the external commitment (with teeth—penalties, credits, contract terms)
- SLOs are the internal targets you set tighter than your SLAs so you have breathing room
- SLIs are the internal measurements you use to track whether you're hitting your SLOs

## Do you need SLOs and SLIs without SLAs?

SLOs and SLIs can absolutely exist without formal SLAs. They give you a framework for making engineering decisions. Without them, you're flying blind on questions like:

- Is this service "healthy enough" or do we need to prioritize reliability work?
- Can we ship this risky feature or should we stabilize first?
- How do we balance velocity vs. reliability?

That's where error budgets come in. If your SLO is 99.5% availability, you have a 0.5% error budget per period. Burning through it fast? Slow down deployments and fix things. Plenty of budget left? Ship faster, take risks.

They allow you to make data-driven decisions about trade-offs between reliability and feature velocity, even without formal SLAs in place.

## What Services need Each

| Layer | When you need it                                                   |
| ----- | ------------------------------------------------------------------ |
| SLIs  | Always - if it runs, measure it                                    |
| SLOs  | When someone depends on the service                                |
| SLAs  | When there's a contractual/business relationship with consequences |

## SLI Metrics

Latency — how long requests take

- p50, p90, p99 response times
- Example: "99th percentile API response time is under 200ms"

Error rate — how often requests fail

- Percentage of 5xx responses, failed jobs, exceptions
- Example: "Less than 0.5% of requests return errors"

Traffic/Throughput — how much demand you're handling

- Requests per second, messages processed, jobs run
- Example: "System handles 10k requests/sec"

Saturation — how "full" your resources are

- CPU utilization, memory pressure, queue depth, connection pool usage
- Example: "Database connection pool stays below 80% utilization"

Example: You might be tracking all of these metrics for a specific service, but only have an SLO for error rate because you have an SLA that promises 99.5% availability to customers.

## How to Track

SLIs live in your metrics & monitoring layer - Prometheus, Datadog, NewRelic, CloudWatch, etc. You define dashboards and alerts based on your SLIs to keep an eye on service health.

- You're instrumenting your services, shipping metrics to Prometheus, and visualizing in Grafana.

The SLO is just the target line you draw on top of that data. It's not a separate system - it's a threshold you define and then compare your SLIs against.

So in Grafana, you'd have:

- A panel showing your SLI (e.g., "current availability is 99.7%")
- A static threshold representing your SLO (e.g., a horizontal line at 99.5%)
- Error budget calculations derived from the gap between them

Error budget is the key part - it's how you operationalize SLOs. You can set up alerts to notify you when you're close to burning through your error budget, prompting action before you violate your SLOs.

## p90 vs p99 Syntax

p90 means 90% of requests were faster than this value. So if your p90 is 150ms, 90% of requests completed in under 150ms, and 10% were slower.

p99 means 99% of requests were faster than this value. If your p99 is 400ms, only 1% of requests took longer than 400ms.

These are used instead of averages because averages can be skewed by outliers. p90 and p99 give you a better sense of the "typical worst-case" performance your users experience.

- The goal is to surface the tail latencies that impact user experience - what are your slowest users experiencing.
