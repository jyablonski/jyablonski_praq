# SQL Proxies

## What They Are

A SQL proxy is a standalone, long-running process that sits between your application and your database. It accepts connections on a TCP port, speaks the database's native wire protocol (Postgres, MySQL, etc.), and forwards queries to the real backend. Your app connects to the proxy exactly like it would connect to the database itself, no special client libraries or SDK changes required.

Think of it like Nginx for database traffic. Nginx accepts HTTP requests and routes them to backend web servers. PgBouncer accepts Postgres connections and routes them to backend Postgres instances. Same architectural pattern, different protocol.

These are typically small compiled binaries written in C or C++. PgBouncer is a few MB, uses a few KB of memory per connection, and adds sub-millisecond latency. They're designed to be boring infrastructure you deploy once and forget about.

## What They Do

Connection pooling is the most common use case. Databases like Postgres spawn a process per connection, each eating ~10MB of memory. If you have 20 microservices each opening 100 connections, that's 2,000 backend connections and ~20GB of RAM just for connection overhead. A proxy accepts all 2,000 client connections but maintains only 50-100 real connections to Postgres, multiplexing queries across them.

Read/write splitting lets the proxy inspect queries and route SELECTs to read replicas while sending writes to the primary. Your application code stays simple with a single connection string, and the proxy handles replica awareness.

Failover and backend switching is where proxies shine for migrations and high availability. The proxy health-checks its backends and can reroute traffic in milliseconds if the primary dies. For database migrations, you reconfigure the proxy's backend target and traffic moves to the new database without an app redeploy.

Query-level features like caching, rewriting, rate limiting, and routing rules are available in more advanced proxies like ProxySQL.

## Common Tools

| Tool | Database | Strengths |
| -------------------------- | -------------- | -------------------------------------------------------------- |
| PgBouncer | Postgres | Lightweight pooling, battle-tested, does one thing well |
| PgCat | Postgres | Pooling + read/write splitting + sharding in one binary |
| ProxySQL | MySQL | Pooling, query routing, caching, rewriting, failover |
| Vitess (vtgate) | MySQL | Full sharding/orchestration layer, built at Google for YouTube |
| AWS RDS Proxy | Postgres/MySQL | Managed service, integrates with IAM and Secrets Manager |
| Azure SQL Managed Instance | SQL Server | Built-in proxy with connection redirection |

## When to Use One

You're hitting connection limits. Serverless functions (Lambda, Cloud Functions) and large microservice fleets open connections aggressively. Postgres starts rejecting connections or OOMing. A pooling proxy is the standard fix.

You're adding read replicas. Rather than refactoring your ORM layer to route reads and writes to different hosts, put a proxy in front and let it handle the split transparently.

You're planning a database migration or version upgrade. Deploy the proxy ahead of time so your app connects to a stable endpoint. On cutover day, reconfigure the proxy's backend from old-db to new-db. No app changes, no redeployment.

You want automated failover. Without a proxy, your app needs retry logic, primary discovery, and reconnection handling. With a proxy, it just reconnects to the same endpoint and the proxy has already found the new primary.

You're in Kubernetes with many pods. Each pod opening its own direct database connection multiplies fast. A PgBouncer sidecar in each pod, or a centralized proxy service, keeps connection counts sane.

## How They're Deployed

Sidecar container (Kubernetes): Run PgBouncer as a second container in the same pod. Your app connects to `localhost:6432`. The proxy lives and dies with the app instance. This is the most common pattern in K8s.

Centralized service: Run one or more proxy instances on dedicated VMs or containers behind a load balancer. All services connect to `proxy.internal:6432`. Good when you want a single place to manage routing rules and connection limits.

Systemd daemon (traditional VMs): `apt install pgbouncer`, edit the config, `systemctl start pgbouncer`. It runs like any other system service.

Managed service: AWS RDS Proxy, Google Cloud SQL Auth Proxy. You configure it in the console, get an endpoint, point your app at it. No infrastructure to manage.

## Example: PgBouncer Config

```ini
;; pgbouncer.ini
[databases]
mydb = host=db-primary.internal port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 5000
default_pool_size = 50
```

Your app's connection string changes from:

```
postgresql://user:pass@db-primary.internal:5432/mydb
```

to:

```
postgresql://user:pass@pgbouncer.internal:6432/mydb
```

That's it. No code changes. The proxy handles the rest.

## When NOT to Use One

Small scale, single service. If you have one app server talking to one database with a few hundred connections, your ORM's built-in connection pool is fine. The proxy adds an operational dependency for no real benefit.

Analytical/warehouse workloads. Systems like Snowflake, BigQuery, and Redshift handle concurrency and scaling internally. They don't benefit from external connection pooling.

When you need session-level state. Some applications rely on Postgres session variables, temp tables, or advisory locks that must persist across multiple queries. PgBouncer's `transaction` pool mode will break this because it reassigns the backend connection after each transaction. You'd need `session` pool mode, which reduces the pooling benefit significantly.

Latency-critical single-query paths. The proxy adds a network hop (~0.1-0.5ms typically). For the vast majority of workloads this is invisible, but if you're micro-optimizing sub-millisecond query paths, it's worth measuring.

You're already on a managed proxy. If you're on RDS Proxy or Cloud SQL Proxy, don't layer PgBouncer on top. Two proxies in series creates debugging nightmares and doesn't help.
