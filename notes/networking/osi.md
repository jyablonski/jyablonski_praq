# The OSI Model

The OSI (Open Systems Interconnection) model is a conceptual framework developed by ISO in the late 1970s/early 1980s that standardizes how different networking systems communicate. It splits networking into 7 layers, each with a specific job, where each layer only talks to the layers directly above and below it. Data flows down through the layers on the sending side (getting wrapped with headers at each step — "encapsulation") and back up on the receiving side.

The key insight: it's a *mental model*, not how the internet actually runs. Real networking uses the TCP/IP model (4-5 layers), and the OSI layers don't map perfectly onto real protocols. But it remains the universal vocabulary engineers use to discuss networking — when someone says "that's a Layer 7 problem" or "we need an L4 load balancer," they mean OSI.

## The 7 Layers (bottom to top)

Layer 1 — Physical: The actual hardware moving bits as electrical signals, light pulses, or radio waves. Think Ethernet cables, fiber optics, Wi-Fi radios, voltage levels. Concerned with "is there a 1 or a 0 on the wire?"

Layer 2 — Data Link: Moves frames between two directly connected nodes on the same network. Handles MAC addresses, error detection on the local segment, and switching. Ethernet and Wi-Fi (802.11) live here. A network switch is an L2 device.

Layer 3 — Network: Routes packets across different networks. This is where IP addresses live (IPv4, IPv6) and where routers operate. Figures out the path from your machine to a server across the world.

Layer 4 — Transport: Provides end-to-end communication between processes. Handles ports, reliability, ordering, and flow control. TCP (reliable, connection-oriented) and UDP (fast, connectionless) are the two big ones. QUIC is a newer one worth knowing.

Layer 5 — Session: Manages sessions/dialogues between applications — opening, maintaining, and tearing them down. Honestly, this layer barely exists in practice; most session concerns are handled in L4 or L7 in real protocols.

Layer 6 — Presentation: Translates data formats — encryption, compression, character encoding (UTF-8), serialization. TLS technically lives here, though people often lump it into L7.

Layer 7 — Application: What your code actually talks to. HTTP, gRPC, DNS, SMTP, WebSockets, Kafka protocol, Postgres wire protocol. This is where APIs and application logic live.

## What Actually Matters for Software Engineers

For most application-level work, you live almost entirely at L7, with L4 mattering whenever performance, networking infrastructure, or load balancing comes into play. L3 matters when you're dealing with cloud networking. The others are mostly abstracted away unless you're doing systems or network engineering.

### Layer 7 (Application) — your daily life

Every API call, every database query going over the wire, every webhook. Things you actually tune at L7:

- Choosing between HTTP/1.1, HTTP/2, and HTTP/3 (huge throughput differences for fan-out workloads — relevant if your data pipelines make many parallel calls to APIs like Airtable's or Gmail's)
- gRPC vs REST vs GraphQL — you've already been picking gRPC for `lotus`, which is an L7 decision (binary protobuf + HTTP/2 multiplexing vs JSON over HTTP/1.1)
- L7 load balancers (nginx, Envoy, Traefik, AWS ALB) that route based on URL paths, headers, or hostnames — useful when you want `/api/v2/*` going to a different service than `/api/v1/*`
- Application-aware proxies and service meshes (Istio, Linkerd) that do retries, circuit breaking, and tracing based on request semantics

### Layer 4 (Transport) — when performance or infra matters

- Choosing TCP vs UDP — TCP for anything where you can't lose data (your gRPC backend, Postgres connections), UDP for things like metrics, logs at scale, or real-time audio/video where latency beats reliability
- L4 load balancers (AWS NLB, HAProxy in TCP mode) — these just forward TCP/UDP without inspecting payloads. Faster, cheaper, and necessary when you can't decrypt traffic at the LB. Useful in front of Postgres or gRPC services where you don't need URL-based routing.
- Connection pooling — keeping TCP connections alive (PgBouncer for Postgres, HTTP keep-alive) avoids the 3-way handshake cost on every request, which adds up fast in a polling pipeline
- Tuning kernel-level stuff like TCP keepalive, `SO_REUSEPORT`, or buffer sizes when you're hitting throughput limits
- This is also where K8s Services operate by default (`ClusterIP`, `NodePort` are L4) — your preStop hook refactor matters here because connection draining at L4 is fundamentally different from graceful HTTP shutdown at L7

### Layer 3 (Network) — cloud and infra work

- VPC design, subnets, CIDR blocks, route tables — anytime you're in AWS/GCP networking
- Security groups and NACLs filter at L3/L4
- VPNs, peering, Cloudflare Tunnel (which you've used for homelab self-hosting) — these are tunneling L3/L4 traffic over L7
- Diagnosing routing issues with `traceroute`, `mtr`

### Layers 1, 2, 5, 6 — usually invisible

You generally don't touch these unless you're doing data center work, building network hardware, or implementing low-level protocols. TLS at L6 is the exception — you'll deal with cert management, but the protocol itself is abstracted away.

## A Concrete Example That Ties It Together

When your Go service polls an example REST API:

1. Your code calls `http.Get(...)` — L7
1. The HTTP library serializes it, TLS encrypts it — L6/L7
1. TCP wraps it, assigns ports, handles retransmits — L4
1. IP routes it across the internet via your router and the API server's — L3
1. Ethernet/Wi-Fi frames it for the local hop — L2
1. The NIC turns it into electrical or radio signals — L1
