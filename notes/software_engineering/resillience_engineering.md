# Resillience Engineering

Resilience engineering is about designing systems that can adapt, recover, and continue functioning when things go wrong - not if, but when. It accepts that failures are inevitable in complex systems and focuses on building software that degrades gracefully rather than catastrophically.

The fundamental shift is from trying to prevent all failures (impossible in complex systems) to building systems that can absorb and adapt to them. This means embracing uncertainty and designing for partial failure rather than assuming everything will work perfectly.

Resilience engineering recognizes that modern distributed systems are inherently complex - with numerous dependencies, network partitions, hardware failures, and unexpected load patterns. The goal is to maintain acceptable service levels even when components fail.

## Design Philosophy

Resilience engineering encourages designing for operational visibility, making it easy to understand what's happening when things go wrong. It also emphasizes the importance of learning from incidents through blameless post-mortems that focus on improving systems rather than punishing individuals.

The paradigm also recognizes that humans are part of the system - operators need good tools, clear runbooks, and systems that provide actionable information during incidents. Automation helps, but human judgment remains essential for handling novel failures.

## Common Patterns

### Circuit Breakers

Circuit Breakers act like electrical circuit breakers for service calls. When a downstream service fails repeatedly, the circuit "opens" and immediately returns errors without attempting the call, preventing cascade failures. After a timeout, it enters a "half-open" state to test if the service has recovered. This prevents your system from wasting resources on calls that will likely fail.

These can be implemented either in Memory or using some 3rd party service like Redis to act as a source of truth for a horizontally scaled application with many worker nodes

- If in memory, simpler implementation but a bit more waste if your app is horizontally scaled as every worker node has to manage its own circuit breaker and discover the failure
- If using Redis, all worker nodes rely upon it as a source of truth for the circuit breaker functionality
- You only need Redis once you have multiple instances of your service. For example, if one instance detects a downstream service is failing, you want all instances to stop calling it immediately rather than each discovering the failure independently.

### Bulkheads

Bulkheads isolate resources into separate pools so that failure in one area doesn't exhaust resources needed by others. For example, you might have separate thread pools for different types of operations, so a slow database query doesn't prevent your system from handling API requests.

These are typically implemented using your programming language's built in concurrency primitives. You create separate thread pools for different operations

```java
database_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="db")
api_pool = ThreadPoolExecutor(max_workers=20, thread_name_prefix="api")
```

If you have any background jobs or multiple types of I/O, separate thread pools prevent one slow operation from blocking everything else.

### Timeouts

Timeouts and Deadlines seem simple but are crucial. Every network call should have a reasonable timeout. Without them, threads can hang indefinitely waiting for responses that never come, eventually exhausting your resources.

These are purely configured in your HTTP client application code, no additional infra is needed.

- `requests.get(url, timeout=5.0)  # That's it`

Every application should set timeouts, because if the default is "wait forever" then it very easily can lead to resource exhaustion.

### Retries

Retries with Exponential Backoff handle transient failures by retrying operations, but with increasing delays between attempts. This prevents overwhelming a struggling service while giving it time to recover. Adding jitter (randomness) to retry intervals prevents thundering herds where many clients retry simultaneously.

These are typically implemented entirely in application code with no external dependencies. Most HTTP client libraries support this functionality.

```py
for attempt in range(max_retries):
    try:
        return make_request()
    except TransientError:
        sleep(base_delay * (2 ** attempt) + random_jitter())
```

### Rate Limiting

Rate Limiting and Load Shedding protect your system from being overwhelmed. Rate limiting controls how many requests you accept from clients, while load shedding involves deliberately rejecting or degrading some requests when you're at capacity, rather than failing completely.

This can be implemented either in memory or utilizing a 3rd party service such as Redis to act as a source of truth for a horizontally scaled application

- If in memory, it works fine for a single server to track rate limiting at a user level with simple a data structure
- Once you have multiple application instances and are horizontally scaling the app, you need shared state.
- Redis is the standard choice here because it's fast and has atomic operations perfect for rate limiting.
- At even higher scale, you can move rate limiting to API Gateways to handle this before requests ever reach your application

```py
# Redis-based rate limiting
pipe = redis.pipeline()
pipe.incr(f"rate_limit:{user_id}")
pipe.expire(f"rate_limit:{user_id}", window_seconds)
count, _ = pipe.execute()

if count > limit:
    return rate_limit_error()
```

### Fallbacks & Caching

Fallback Mechanisms provide alternative responses when primary operations fail. This might mean serving cached data, returning default values, or offering degraded functionality rather than complete failure.

If operations fail or data is unavailable, you might want to fallback on some default values served from a cache.

- Python's LRU Cache works great for this

```py
@lru_cache(maxsize=1000)
def get_user_data(user_id):
    return fetch_from_database(user_id)
```

Once again, once you have multiple applications instances you should move to Redis instead for caching where it acts as the source of truth for all the instances.

CDNs can cache static content at specific geographic locations and serve it directly to users - this is cheap, lower latency, and best practice for almost all applications.

### Health Checks

Health Checks and Monitoring go beyond simple uptime checks. Proper health endpoints verify that your service can perform its core functions and reach its dependencies. Deep observability through metrics, logs, and tracing helps you understand system behavior under stress.

```py
@app.route('/health')
def health_check():
    if database.ping() and cache.ping():
        return {'status': 'healthy'}, 200
    return {'status': 'unhealthy'}, 503
```

- Not just returning a simple `{'status': 'healthy'}` message if the API is up, but it actually pings its external dependencies to verify they return valid responses as well
- For APIs that interact with LLMs or ML Workloads, you can also verify your clients for these external services are functioning correctly as well

### Chaos Engineering

Chaos Engineering involves deliberately injecting failures into production systems to verify resilience. Netflix's Chaos Monkey randomly terminates instances, forcing teams to build systems that can handle these failures. This proactive approach reveals weaknesses before they cause real incidents.

This is typically only done by sophisticated tech teams with large applications and many horizontally scaled services. It does not make sense for smaller teams or startups just getting off the ground.

The order probably goes something like:

1. Startup - deploy fast, handle user-errors fast
2. Mid-level company - implement staging environments and try to catch most issues there
3. Large scale company - perform chaos engineering on production-like staging instances to try and catch bugs or find bottlenecks before you hit a production incident.

### Graceful Degradation

Graceful Degradation means your system continues providing core functionality even when some features fail. For example, a social media feed might still display posts even if the "like" counter service is down.

Feature flags are a fantastic way of doing this. They enable you to ship new functionality quickly, while also giving you the flexibility to turn it off without requiring a code change or re-deploy.

Below is an example where you might be serving recommendations to users, and if they're not available or if a feature flag for the feature is disabled, then just return some default instead.

```py
class FeatureFlags:
    def __init__(self):
        self.flags = {
            'recommendations': True,
            'real_time_updates': True,
            'comments': True
        }

    def is_enabled(self, feature):
        return self.flags.get(feature, False)

# In your application
if feature_flags.is_enabled('recommendations'):
    recommendations = get_personalized_recommendations(user)
else:
    recommendations = get_default_recommendations()
```
