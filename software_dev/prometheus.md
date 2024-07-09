# Prometheus

Open Source monitoring tool written in Go that's used to collect metrics data & store it in a time-series like database.

Originally built by SoundCloud in 2012, then opened sourced a few years later. It is now maintained independently of any company.

It collects and stores metrics which are numeric data points stored as time series data. These are based on key value pairs and each metric can have multiple labels which allow you to slice and dice the data. This data is stored for 15 days by default, but can be changed by the `--storage.tsdb.retention.time=30d` flag.

Common metrics include:

- Number of HTTP requests received by API endpoints
- Request duration + latency
- Error Rates
- API Endpoint Health + Availability
- Server resource usage such as CPU + Memory

Prometheus server periodically scrapes data from applications or services that exposes the metrics via HTTP endpoints `/metrics`, where the data is then stored in a custom time-series databased optimized for fast querying. This is known as a pull-based model.

Exporters can convert metrics from third party systems into a format that Prometheus can ingest.

- Node Exporter collects hardware and OS metrics
- MySQL Exporter collects metrics from a MySQL Database
- These Exporters are often ran in a separate container.

Prometheus has its own query language called PromQL which is used to query the time series data, allowing for complex aggregations and transformations.

Alerting can be setup by defining alert rules based on PromQL queries which, when conditions are met, can send alerts to the Alertmanager component of Prometheus which then manages and routest the alerts to targets like Slack or PagerDuty. Alertmanager is often ran in a separate container service.

- You typically have more complex, fine-grained control setting up alerts this way over Grafana

## Grafana

Grafana is an open source visualization platform tool used for monitoring, visualization, and analyzing time-series data. It's often hooked up to Prometheus to display dashboards and other visualizations of the metrics data provided by Prometheus. Grafana can query Prometheus data using PromQL, and there are pre-built dashboards available via Grafana.

- Prometheus must first be added as a Data Source

Grafana can also setup alerts for you. This is a bit easier to do in Grafana than Prometheus and you can do it via a GUI tool, but you don't have as much flexibility

Can also hook up to Databases, Elasticsearch, AWS Cloudwatch etc to connect multiple data sources together and query them simultaneously.