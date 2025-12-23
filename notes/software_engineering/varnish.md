# Varnish as a Reverse Proxy

## What It Is

Varnish is an HTTP accelerator, essentially a caching reverse proxy that sits between your clients and your backend servers. It stores copies of responses in memory and serves them directly without hitting your origin servers, which makes it extremely fast (we're talking microsecond response times for cached content).

The core idea is simple: HTTP responses that don't change frequently shouldn't require a full round-trip to your application every time. Varnish intercepts requests, checks if it has a valid cached copy, and either serves that immediately or forwards the request to your backend.

This is great for serving static content like blog posts, media articles, and other API responses that can be cached safely. Varnish stores the complete HTTP response, and subsequent requests get that stored response directly from memory without the backend ever knowing about them.

- The key insight is that a huge portion of web traffic is actually this kind of content. Think about it: a news site might have millions of readers hitting the same article. Without caching, that's millions of identical database queries returning identical results, millions of identical template renders producing identical HTML.

## What Purpose It Serves

The primary value is reducing load on your origin servers while dramatically improving response times. Your application servers, whether Django, Rails, Node, whatever, typically do expensive work: database queries, template rendering, API calls. Varnish lets you skip all of that for cacheable content.

Secondary benefits include:

- Traffic shaping and load balancing across multiple backends
- Grace mode - serving stale content while fetching fresh copies, so users never see errors during backend hiccups
- Edge-side logic via VCL (Varnish Configuration Language), letting you manipulate requests and responses, do A/B testing, handle redirects, normalize headers, etc.

## With vs Without Varnish

Without Varnish:

```
Client -> Load Balancer -> App Server -> Database -> App Server -> Load Balancer -> Client
```

Every request hits your application. A popular blog post getting 10,000 requests means 10,000 database queries, 10,000 template renders. Your app servers need to scale horizontally to handle traffic spikes, which gets expensive.

With Varnish:

```
Client -> Varnish (cache hit) -> Client                    [~1ms]
Client -> Varnish (cache miss) -> App Server -> ... -> Varnish -> Client
```

That popular blog post gets fetched once, cached, and the next 9,999 requests are served from memory. Your app servers stay idle while Varnish handles the load. A single Varnish instance can serve tens of thousands of requests per second.

## Competitors and Alternatives

NGINX is the most common alternative. It started as a web server but has robust caching and reverse proxy capabilities. Less specialized than Varnish but more versatile: you can terminate TLS, serve static files, and cache all in one process. Configuration is more familiar (nginx.conf vs VCL).

HAProxy focuses more on load balancing than caching, but it's often mentioned in the same breath. You might use HAProxy for TCP/HTTP load balancing and Varnish specifically for HTTP caching.

CDNs (Cloudflare, Fastly, CloudFront) are essentially Varnish-at-the-edge. Fastly literally runs Varnish under the hood. These push caching to geographically distributed PoPs, adding latency benefits from physical proximity. The tradeoff is less control and ongoing costs.

- Varnish becomes relevant when you outgrow what CDNs offer in terms of flexibility, cost, or control.

Squid is an older caching proxy, more commonly used for forward proxying these days but still capable of reverse proxy caching.

Apache Traffic Server (from Yahoo, now Apache) is another option, used at scale by companies like Apple and Yahoo.

Redis is not an appropriate alternative because Redis caching happens at the backend application layer. 10,000 requests for the same content still hit your app server, which then queries Redis. Varnish eliminates those backend hits entirely for cached content.

## Production Hosting Patterns

Typical architecture:

```
Internet -> CDN (optional) -> Load Balancer -> Varnish cluster -> App Servers
```

Varnish itself doesn't handle TLS, so you need something in front of it for HTTPS termination—commonly NGINX, HAProxy, or a cloud load balancer (ALB/NLB in AWS).

Single-region setup:
You'd run multiple Varnish instances behind a load balancer for redundancy. Each instance maintains its own cache (they don't share state by default), so you either accept cache duplication or use consistent hashing at the load balancer to route the same URLs to the same Varnish instance.

Multi-region:

Each region gets its own Varnish cluster. Cache invalidation becomes more complex—you need to purge across all regions when content changes. Some teams use a message queue or webhook system to broadcast purge requests.

On Kubernetes (relevant to your setup):

Varnish runs fine in containers, but there are considerations:

- Memory allocation needs to be explicit since Varnish pre-allocates its cache
- Pod restarts mean cold caches, so you want stability and might use a DaemonSet or dedicated node pools
- Some teams run Varnish outside K8s entirely to avoid cache churn from pod rescheduling

Cache invalidation is the hard part in production. Strategies include:

- TTL-based expiration (simple but imprecise)
- Purge endpoints that your app calls when content changes
- Ban expressions that invalidate based on patterns
- Soft purges that serve stale while revalidating

## Proposed Implementation

### Phase 1: CDN in Front, No Varnish

```
Internet -> Cloudflare -> Your Load Balancer (Traefik/ALB) -> App Services
```

At this stage you're relying entirely on the CDN for caching. Your backend sets appropriate cache headers and Cloudflare respects them.

Backend changes needed:

Your app needs to return proper cache-control headers. This is the only backend work required and it's necessary regardless of whether you use a CDN, Varnish, or both.

```python
# Django example
from django.views.decorators.cache import cache_control

@cache_control(public=True, max_age=3600, s_maxage=86400)
def blog_post(request, slug):
    # s-maxage tells shared caches (CDN/Varnish) to cache for 24h
    # max-age tells browsers to cache for 1h
    ...
```

For an API:

```python
response = JsonResponse(data)
response['Cache-Control'] = 'public, max-age=60, s-maxage=300'
response['Vary'] = 'Accept-Encoding'  # if response varies by header
return response
```

You also want to think about:

- `Surrogate-Key` or `Cache-Tag` headers if your CDN supports tag-based purging
- `Vary` headers for content that differs by Accept-Language, Accept-Encoding, etc.
- `ETag` or `Last-Modified` for conditional requests

Infrastructure:

No special K8s changes. Cloudflare sits in front of whatever public endpoint you already have. You point DNS to Cloudflare, configure caching rules in their dashboard, done.

### Phase 2: Adding Varnish When You Outgrow the CDN

Signals that you might need this:

- CDN costs are getting painful
- You need complex cache logic the CDN can't express
- Cache miss thundering herds are hammering your backend
- You want request coalescing or grace mode behavior

New architecture:

```
Internet -> Cloudflare -> Traefik (ingress) -> Varnish -> App Services
                                 │
                                 └-> Non-cached services (bypass Varnish)
```

Kubernetes changes:

You're adding Varnish as a deployment that sits between your ingress and your app services.

- You specify in `.vcl` how to route requests: which paths to cache, which to bypass and what your backend endpoints are.

```yaml
# varnish-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: varnish
spec:
  replicas: 2
  selector:
    matchLabels:
      app: varnish
  template:
    metadata:
      labels:
        app: varnish
    spec:
      containers:
        - name: varnish
          image: varnish:7.4
          args:
            - "-f"
            - "/etc/varnish/default.vcl"
            - "-s"
            - "malloc,1G" # 1GB cache in memory
          ports:
            - containerPort: 80
          resources:
            requests:
              memory: "1.5Gi" # slightly more than cache size
              cpu: "500m"
            limits:
              memory: "2Gi"
          volumeMounts:
            - name: varnish-config
              mountPath: /etc/varnish
      volumes:
        - name: varnish-config
          configMap:
            name: varnish-vcl
---
apiVersion: v1
kind: Service
metadata:
  name: varnish
spec:
  selector:
    app: varnish
  ports:
    - port: 80
      targetPort: 80
```

```yaml
# varnish-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: varnish-vcl
data:
  default.vcl: |
    vcl 4.1;

    backend default {
      .host = "your-app-service";
      .port = "80";
    }

    sub vcl_recv {
      # Strip cookies for static/cacheable paths
      if (req.url ~ "^/api/public/" || req.url ~ "^/blog/") {
        unset req.http.Cookie;
      }
      
      # Pass authenticated requests directly to backend
      if (req.http.Authorization) {
        return (pass);
      }
    }

    sub vcl_backend_response {
      # Grace mode - serve stale content for 1h while fetching
      set beresp.grace = 1h;
      
      # Default TTL if backend doesn't set Cache-Control
      if (beresp.ttl <= 0s) {
        set beresp.ttl = 60s;
      }
    }

    sub vcl_deliver {
      # Debug header to see cache status
      if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
      } else {
        set resp.http.X-Cache = "MISS";
      }
    }
```

Traefik/Ingress changes:

You need to route cacheable traffic through Varnish and let other traffic bypass it. With Traefik IngressRoutes:

```yaml
# Route blog/public API through Varnish
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: cached-routes
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`yourdomain.com`) && (PathPrefix(`/blog`) || PathPrefix(`/api/public`))
      kind: Rule
      services:
        - name: varnish
          port: 80
---
# Direct to backend for everything else
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: direct-routes
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`yourdomain.com`) && PathPrefix(`/api/private`)
      kind: Rule
      services:
        - name: your-app-service
          port: 80
```
