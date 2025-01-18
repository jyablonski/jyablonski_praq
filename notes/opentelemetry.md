# OpenTelemetry

OpenTelemetry is an open-source observability framework for cloud-native software that provides tools, APIs, and SDKs for generating, collecting, and exporting telemetry data (traces, metrics, and logs) to help developers and operators understand the performance and behavior of their applications.

#### Key Features of OpenTelemetry:
1. **Tracing**: Helps track the flow of requests through various services in a distributed system.
2. **Metrics**: Collects data about the performance of applications, such as latency, error rates, and resource usage.
3. **Logs**: Records discrete events that occur during the execution of a program.
4. **Interoperability**: Integrates with various backend observability systems like Prometheus, Jaeger, Zipkin, Datadog, and others.
5. **Language Support**: Offers SDKs for multiple programming languages, including Java, Python, JavaScript, Go, and more.

### Example REST API Endpoint

Let's assume we have an endpoint `GET /api/user/{id}` which fetches user details by user ID.

### Log

Logs are discrete events that happen during the execution of the application. They are useful for debugging and understanding what happened at a particular point in time.

```json
{
  "timestamp": "2024-06-21T12:00:00Z",
  "level": "INFO",
  "message": "Fetching user details",
  "request_id": "abcd-1234-efgh-5678",
  "endpoint": "GET /api/user/{id}",
  "user_id": "42"
}
```

### Trace

Traces represent the journey of a request through the system, providing insight into the flow and performance of each component involved.

1. **Trace ID**: A unique identifier for the entire trace.
2. **Span**: Represents a single unit of work within the trace. Spans can have parent-child relationships.

```json
{
  "trace_id": "abcd-1234-efgh-5678",
  "spans": [
    {
      "span_id": "span-1",
      "name": "HTTP GET /api/user/{id}",
      "start_time": "2024-06-21T12:00:00Z",
      "end_time": "2024-06-21T12:00:05Z",
      "attributes": {
        "http.method": "GET",
        "http.url": "/api/user/42",
        "http.status_code": 200,
        "user_id": "42"
      }
    },
    {
      "span_id": "span-2",
      "parent_span_id": "span-1",
      "name": "DB Query - Get User",
      "start_time": "2024-06-21T12:00:02Z",
      "end_time": "2024-06-21T12:00:04Z",
      "attributes": {
        "db.system": "postgresql",
        "db.statement": "SELECT * FROM users WHERE id = 42",
        "db.response_time": "2ms"
      }
    }
  ]
}
```

### Metric

Metrics provide numerical data about the performance and usage of the system, often aggregated over time.

1. **Counter**: A cumulative metric that represents a single monotonically increasing counter.
2. **Gauge**: A metric that represents a single numerical value that can arbitrarily go up and down.
3. **Histogram**: A metric that samples observations and counts them in configurable buckets.

#### Example of Counter Metric

```json
{
  "name": "http_requests_total",
  "description": "Total number of HTTP requests",
  "type": "counter",
  "labels": {
    "method": "GET",
    "endpoint": "/api/user/{id}",
    "status": "200"
  },
  "value": 1024
}
```

#### Example of Gauge Metric

```json
{
  "name": "http_request_duration_seconds",
  "description": "HTTP request duration in seconds",
  "type": "gauge",
  "labels": {
    "method": "GET",
    "endpoint": "/api/user/{id}"
  },
  "value": 0.005
}
```

#### Example of Histogram Metric

```json
{
  "name": "http_request_duration_histogram_seconds",
  "description": "HTTP request duration distribution",
  "type": "histogram",
  "labels": {
    "method": "GET",
    "endpoint": "/api/user/{id}"
  },
  "buckets": {
    "0.001": 100,
    "0.005": 500,
    "0.01": 800,
    "0.1": 1000,
    "1": 1024
  }
}
```

### Putting It All Together

Here's an example of how these might look in practice using OpenTelemetry in Python for a Flask application:

```python
from flask import Flask, request
from opentelemetry import trace, metrics, logs
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.logs import LoggerProvider

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

trace.set_tracer_provider(TracerProvider())
meter_provider = MeterProvider()
metrics.set_meter_provider(meter_provider)
logger_provider = LoggerProvider()
logs.set_logger_provider(logger_provider)

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
logger = logs.get_logger(__name__)

request_counter = meter.create_counter(
    "http_requests_total", "Total number of HTTP requests"
)
request_duration = meter.create_histogram(
    "http_request_duration_histogram_seconds", "HTTP request duration distribution"
)

@app.route("/api/user/<int:user_id>")
def get_user(user_id):
    with tracer.start_as_current_span("HTTP GET /api/user/{id}") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.url", f"/api/user/{user_id}")
        span.set_attribute("user_id", user_id)
        
        # Simulate fetching user details
        user_details = {"id": user_id, "name": "John Doe"}  # Placeholder for actual DB call
        
        span.add_event("Fetching user details from database")
        
        # Simulate a DB span
        with tracer.start_as_current_span("DB Query - Get User", parent=span) as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.statement", "SELECT * FROM users WHERE id = 42")
        
        request_counter.add(1, {"method": "GET", "endpoint": "/api/user/{id}", "status": "200"})
        request_duration.record(0.005, {"method": "GET", "endpoint": "/api/user/{id}"})
        
        logger.info("Fetching user details", extra={"request_id": span.context.trace_id, "user_id": user_id})
        
        return user_details

if __name__ == "__main__":
    app.run(debug=True)
```

P90, P95, and P99 are common percentiles used in performance monitoring to understand the distribution of response times or latency in your application. They help identify the performance experienced by the majority of users, especially focusing on the tail end of the distribution, which can be critical for identifying outliers and ensuring a good user experience.

### Percentiles Overview

- **Percentile**: A percentile is a value below which a given percentage of observations in a group of observations falls. For example, the 90th percentile (P90) is the value below which 90% of the observations may be found.

### P90, P95, and P99 Explained

1. **P90 (90th Percentile)**:
   - **Definition**: The value below which 90% of the observations fall.
   - **Usage**: It indicates that 90% of your requests or users experience a response time that is less than or equal to this value.
   - **Example**: If P90 response time is 200ms, it means that 90% of the requests are completed in 200ms or less, and 10% take longer than 200ms.

2. **P95 (95th Percentile)**:
   - **Definition**: The value below which 95% of the observations fall.
   - **Usage**: It highlights the response time experienced by the slowest 5% of requests. It's a more stringent measure compared to P90.
   - **Example**: If P95 response time is 300ms, it means that 95% of the requests are completed in 300ms or less, and 5% take longer than 300ms.

3. **P99 (99th Percentile)**:
   - **Definition**: The value below which 99% of the observations fall.
   - **Usage**: It focuses on the tail end of the distribution, showing the response time for the slowest 1% of requests. This is useful for identifying outliers and understanding the worst-case performance.
   - **Example**: If P99 response time is 500ms, it means that 99% of the requests are completed in 500ms or less, and 1% take longer than 500ms.

### Importance of Percentiles in Performance Monitoring

1. **User Experience**: Percentiles give a more comprehensive picture of user experience compared to averages. Averages can be misleading, as they may be skewed by extreme outliers.
2. **Performance Tuning**: Understanding the performance for different percentiles helps in identifying and addressing performance bottlenecks that affect a significant portion of users.
3. **SLAs and SLOs**: Service Level Agreements (SLAs) and Service Level Objectives (SLOs) often use percentiles to define acceptable performance thresholds. For example, an SLA might specify that 95% of requests should complete within 300ms.

### Visual Example

Imagine the response times for an API endpoint in milliseconds: [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000].

- **P90**: The 90th percentile value is 200ms, meaning 90% of requests are faster than 200ms.
- **P95**: The 95th percentile value is 500ms, meaning 95% of requests are faster than 500ms.
- **P99**: The 99th percentile value is 900ms, meaning 99% of requests are faster than 900ms.

### How to Calculate Percentiles

1. **Sort the Data**: Arrange the response times in ascending order.
2. **Rank Calculation**: Calculate the rank for the desired percentile using the formula `rank = (percentile / 100) * (number of values + 1)`.
3. **Interpolation**: If the rank is not an integer, interpolate between the two closest ranks.

#### Example with P95 Calculation:

For the above dataset with 20 values:

1. **Sort the Data**: Already sorted in the example.
2. **Rank Calculation**: For P95, rank = (95/100) * (20 + 1) = 19.95.
3. **Interpolation**: The 19th value is 900ms, and the 20th value is 1000ms. Interpolating between these values, P95 is approximately 900 + 0.95 * (1000 - 900) = 995ms.


# Logs vs Traces vs Metrics

- **Logs** provide detailed event data useful for debugging.
- **Traces** represent the flow and performance of individual requests through the system.
- **Metrics** offer aggregated performance data useful for monitoring and alerting.


### Logs

- **Definition**: Logs are discrete records of events that happen within your application. They provide detailed information about what happened, where, and when.
- **Content**: Each log entry typically includes a timestamp, log level (e.g., INFO, ERROR), a message, and potentially additional contextual information (e.g., request IDs, user IDs).
- **Usage**: Logs are used for debugging, auditing, and understanding the state of the application at specific points in time.

**Example Log Entry**:
```json
{
  "timestamp": "2024-06-21T12:00:00Z",
  "level": "INFO",
  "message": "Fetching user details",
  "request_id": "abcd-1234-efgh-5678",
  "endpoint": "GET /api/user/{id}",
  "user_id": "42"
}
```

### Traces

- **Definition**: Traces represent the journey of a single request through the various components of your system. They help you understand the flow and performance of requests across different services.
- **Content**: A trace consists of multiple spans. Each span represents a unit of work (e.g., an HTTP request, a database query) and contains information such as start time, end time, attributes, and parent-child relationships between spans.
- **Usage**: Traces are used to analyze request flows, measure latencies, and identify bottlenecks in distributed systems.

**Example Trace**:
```json
{
  "trace_id": "abcd-1234-efgh-5678",
  "spans": [
    {
      "span_id": "span-1",
      "name": "HTTP GET /api/user/{id}",
      "start_time": "2024-06-21T12:00:00Z",
      "end_time": "2024-06-21T12:00:05Z",
      "attributes": {
        "http.method": "GET",
        "http.url": "/api/user/42",
        "http.status_code": 200,
        "user_id": "42"
      }
    },
    {
      "span_id": "span-2",
      "parent_span_id": "span-1",
      "name": "DB Query - Get User",
      "start_time": "2024-06-21T12:00:02Z",
      "end_time": "2024-06-21T12:00:04Z",
      "attributes": {
        "db.system": "postgresql",
        "db.statement": "SELECT * FROM users WHERE id = 42",
        "db.response_time": "2ms"
      }
    }
  ]
}
```

### Metrics

- **Definition**: Metrics are aggregated numerical data that represent the performance and usage of your system. They provide a quantitative measure of how your system is behaving over time.
- **Content**: Metrics are typically captured as counters, gauges, and histograms.
  - **Counter**: A cumulative value that only increases (e.g., number of requests).
  - **Gauge**: A value that can go up or down (e.g., current memory usage).
  - **Histogram**: A distribution of values (e.g., response time distribution).
- **Usage**: Metrics are used for monitoring system health, capacity planning, and triggering alerts when certain thresholds are breached.

**Example Metrics**:
```json
{
  "name": "http_requests_total",
  "type": "counter",
  "labels": {
    "method": "GET",
    "endpoint": "/api/user/{id}",
    "status": "200"
  },
  "value": 1024
}
```
```json
{
  "name": "http_request_duration_seconds",
  "type": "histogram",
  "labels": {
    "method": "GET",
    "endpoint": "/api/user/{id}"
  },
  "buckets": {
    "0.001": 100,
    "0.005": 500,
    "0.01": 800,
    "0.1": 1000,
    "1": 1024
  }
}
```

### Relationships Between Logs, Traces, and Metrics

1. **Logs**:
   - Logs capture detailed information about specific events. They are not necessarily tied to traces but can be correlated using identifiers like request IDs.

2. **Traces**:
   - Traces provide a high-level view of a single request's journey through the system, composed of multiple spans. Each span can contain logs and attributes but traces are not just collections of logs. They are structured to show the relationships and timing between different spans of work.

3. **Metrics**:
   - Metrics are aggregated data points that provide a summary of system performance and behavior. They are often derived from events and traces but are stored and analyzed separately. Metrics are used for monitoring trends over time rather than providing detailed, event-specific information.

### Example Workflow

1. **Log Entry**:
   - A log entry is created when the `GET /api/user/{id}` endpoint is called.

2. **Trace Creation**:
   - A trace is initiated for the request, with spans created for each significant operation (e.g., handling the HTTP request, querying the database).

3. **Metric Aggregation**:
   - Metrics are recorded for the number of requests, request duration, and database query performance. These metrics are aggregated over time to provide insights into the application's performance.
