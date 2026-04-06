# ngrok and HTTP(S) Tunneling

## The Problem

Local development services listen on `localhost` (or `127.0.0.1`), which means they're only reachable from your own machine. No one else on the internet can hit `localhost:8080` on your laptop -- it's not routable. This makes developing the following scenarios tricky:

- A third-party service (Stripe, GitHub, Twilio) needs to POST a webhook to your local handler
- You're developing a mobile app that needs to reach a local API
- You need to test OAuth flows that require a public redirect URI

The traditional workarounds -- port forwarding on your router, deploying to staging, spinning up a cloud VM -- are all friction-heavy and slow.

## What HTTP Tunneling Actually Does

An HTTP tunnel punches a hole outward from your machine through NAT and firewalls by establishing an outbound connection to a relay server. Because the connection is initiated from inside your network (outbound), it bypasses the firewall restrictions that would block inbound connections.

The flow looks like this:

```
External client
      |
      v
[ngrok cloud edge]  <-- public URL lives here
      |
  (secure tunnel, initiated outbound by the agent)
      |
      v
[ngrok agent on your machine]
      |
      v
localhost:8080  <-- your actual service
```

No port forwarding. No firewall rules. No public IP needed. The agent establishes and maintains a long-lived connection to ngrok's cloud, and ngrok proxies inbound traffic through it.

## What ngrok Is

ngrok started as a simple tunnel tool and has grown into a full cloud networking platform. At its core it still does the tunneling thing, but it also handles:

- HTTP/HTTPS/TCP/TLS tunnels
- Traffic inspection (request/response headers, body, latency -- all in a web UI)
- Request replay (huge for webhook debugging)
- Traffic policy (routing, auth, rate limiting, IP restrictions, header modification)
- Load balancing across multiple tunnel agents
- A Kubernetes operator
- Native SDKs for Go, Python, Node, Java (so you can embed the tunnel directly in your app without a sidecar)

For local dev you mostly care about the core tunnel and the traffic inspector.

## Why It's Useful in Practice

### Webhook Development

This is the canonical use case. Services like Stripe, GitHub Actions, Twilio, and basically every SaaS that emits events do so via HTTP POST to a URL you register. That URL must be publicly reachable. With ngrok you run `ngrok http 8080`, get a public URL, paste it into the webhook config, and your local handler receives the events directly. The traffic inspector lets you see the raw payload and replay it without triggering the event again -- massively speeds up the dev/debug loop.

### OAuth and Third-Party Integrations

OAuth redirect URIs, SAML ACS URLs, and similar callback patterns all require a real public URL. ngrok gives you one instantly. Paid tiers also let you use a stable custom subdomain (e.g. `myapp.ngrok.io`) so you don't have to update your OAuth app config every time you restart the tunnel.

### Cross-Device Testing

Testing a web app on a physical phone against your local dev server is annoying -- you have to find your machine's LAN IP, make sure you're on the same network, etc. With ngrok you get a public HTTPS URL that works from any device anywhere.

### Sharing Previews

Demoing a feature to a stakeholder or designer without deploying anything. Run the tunnel, send the URL.

### Local MCP Servers

Relevant if you're running local MCP servers that need to be reachable by a remote client (e.g. Claude, ChatGPT). ngrok handles this cleanly.

## Basic Usage

```bash
# install (mac)
brew install ngrok/ngrok/ngrok

# authenticate (one-time)
ngrok config add-authtoken <token>

# expose a local HTTP service
ngrok http 8080

# expose with a stable domain (paid)
ngrok http --domain=myapp.ngrok.io 8080

# TCP tunnel (non-HTTP, e.g. Postgres, raw socket)
ngrok tcp 5432
```

When you run it, ngrok outputs the public URL and launches a local web UI at `http://127.0.0.1:4040` where you can inspect all traffic in real time.

## Traffic Policy (the more powerful stuff)

ngrok's traffic policy is a CEL-based rules engine that runs at the edge. You can attach it to any tunnel endpoint and do things like:

- Require OAuth before reaching your app
- Block by IP or geo
- Rate limit requests
- Modify request/response headers
- Route to different backends based on path or headers

For local dev you usually don't need this, but it's genuinely useful when ngrok is being used as a real API gateway in staging or production contexts.

## Free vs Paid

The free tier is enough for most webhook and preview work:

- 1 agent, 1 online endpoint
- Random-assigned subdomain (changes on restart)
- Traffic inspection included

Paid tiers add stable custom domains, multiple simultaneous tunnels, higher limits, and the policy features.

## Alternatives

- **Cloudflare Tunnel** -- free, integrates with Cloudflare's network, more config overhead
- **Telebit / localtunnel** -- lighter weight, less featureful
- **Tailscale Funnel** -- if you're already on Tailscale, lets you expose local services via Tailscale's relay; more trust-model friendly for team scenarios
- **bore / frp** -- self-hosted open source options if you have a public VPS
