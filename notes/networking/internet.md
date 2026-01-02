# Internet

A comprehensive overview of how internet connectivity works, from your local network to global infrastructure.

## NetworkManager and Getting Connected

NetworkManager is a Linux orchestration layer that automates the multi-step process of connecting to a network. It abstracts away the complexity of manual configuration.

For ethernet connections, the process involves detecting the physical link, requesting an IP via DHCP, configuring the interface with IP/subnet/gateway, setting up DNS resolution, and adding routing table entries.

For WiFi, there's additional complexity: scanning for networks, authenticating to the access point (via wpa_supplicant for the 802.11 handshake), associating with the AP, then all the same DHCP/IP/DNS/routing steps.

On Arch Linux, the base install is intentionally minimal — no network service is enabled by default. The expected workflow is to install and enable NetworkManager while still in the live environment before rebooting: `pacman -S networkmanager && systemctl enable NetworkManager`.

## DHCP (Dynamic Host Configuration Protocol)

DHCP is how your device automatically gets the network configuration it needs to communicate. The process follows the DORA sequence:

1. Discover — device broadcasts looking for a DHCP server
1. Offer — DHCP server (usually your router) responds with available configuration
1. Request — device accepts the offered configuration
1. Acknowledge — server confirms and finalizes the lease

DHCP provides your device with an IP address, subnet mask, default gateway, DNS server addresses, and a lease duration. The lease concept means IPs are temporary — your device periodically renews, and disconnected IPs can be reassigned.

## Private vs Public IP Addresses

Private IP ranges (`192.168.x.x`, `10.x.x.x`, `172.16.x.x` through `172.31.x.x`) are reserved for internal use and reused on millions of networks worldwide. Your home network, your neighbor's network, and every coffee shop all use these same ranges.

Your public IP is assigned by your ISP to your router's external interface and is globally unique at any given time. All devices on your home network share this single public IP when communicating with the internet.

## NAT (Network Address Translation)

NAT is how your router multiplexes many internal devices through one public IP address. When you make a request to the internet:

1. Your machine (`192.168.1.47`) sends a request to an external server
1. The router rewrites the source address to its public IP and tracks the mapping
1. The response comes back to the public IP
1. The router translates it back and forwards to your internal IP

From the internet's perspective, all devices on your home network appear as a single public IP. This is why port forwarding is required to expose internal services — inbound traffic needs explicit rules to know which internal device should receive it.

NAT types (Open, Moderate, Strict) describe how permissive your router is about accepting inbound connections. Strict NAT historically caused issues with hosting game lobbies or peer-to-peer connections since it drops unsolicited inbound traffic.

## DNS (Domain Name System)

DNS translates human-readable domain names to IP addresses. It's a lookup that happens before the actual request:

1. Your machine wants to reach `google.com`
1. It asks the DNS server for the IP
1. DNS responds with the address (e.g., `142.250.80.46`)
1. Your machine caches that result
1. Subsequent requests go directly to that IP

DNS caching happens at multiple layers: your machine, your router, and upstream resolvers. Each cached entry has a TTL (time to live) specified by the domain owner in their DNS records. Once TTL expires, the entry is evicted and a fresh lookup occurs.

DNS record types include A (domain -> IPv4), AAAA (domain -> IPv6), CNAME (domain -> another domain), MX (mail servers), TXT (arbitrary text), and NS (nameservers). Each record type has its own TTL.

Pi-hole and similar tools work by acting as a filtering proxy in front of a real DNS resolver. They intercept queries, check against blocklists, and either return null responses for blocked domains or forward legitimate queries upstream.

## Subnet Masks

A subnet mask defines which portion of an IP address identifies the network versus the individual device.

With IP `192.168.1.47` and subnet mask `255.255.255.0`:

- First three octets (`192.168.1`) = network portion
- Last octet (`.47`) = host portion

Your machine uses this to determine if a destination is local or remote. Matching network portions mean direct local communication; non-matching means traffic goes to the default gateway.

CIDR notation expresses this more concisely: `192.168.1.0/24` means the first 24 bits are the network portion. Different masks create different sized networks — `/24` allows 254 hosts, `/16` allows 65,534 hosts.

## Default Gateway

The default gateway is where your machine sends traffic that isn't destined for the local network. In home setups, this is your router's internal IP (typically `192.168.1.1`).

The gateway and DNS server are separate concerns provided by DHCP:

- Default gateway — "send non-local traffic here"
- DNS server — "ask this server to translate domain names"

They can be the same device (many routers act as both), but they're conceptually distinct roles.

## Routing and Internet Infrastructure

Traffic from your machine doesn't go directly to the internet — it passes through your ISP's infrastructure:

1. Your machine -> your router
1. Your router -> ISP's network (through modem/ONT)
1. ISP's internal backbone -> peering points / upstream providers
1. Destination server's network

The "internet" is a mesh of interconnected networks. BGP (Border Gateway Protocol) determines routing paths — each network (Autonomous System) announces reachability, and routers build tables of where to forward traffic.

"Optimal" paths in BGP terms factor in business relationships, network policies, link capacity, and AS hop counts — not necessarily shortest physical distance. Traffic to another continent traverses undersea fiber optic cables, with routing determined by these complex relationships.

## Bandwidth vs Latency

These are independent properties of a connection:

Bandwidth is the rate of data transfer (bits per second) — how much data your connection can handle. Download and upload are often asymmetric on residential connections. Your slowest link is the bottleneck for the entire path.

Latency is how long for a packet to make the round trip. This is cumulative across every hop but less affected by your local connection type than bandwidth is.

A highway analogy: bandwidth is how many lanes (cars per hour), latency is how fast each car travels. High bandwidth means more data in flight simultaneously; low latency means each piece completes its trip quickly.

Streaming cares more about bandwidth; gaming and video calls care more about latency.

## Asymmetric Connections

ISPs typically offer higher download than upload speeds due to:

- Technical constraints — cable (DOCSIS) and DSL allocated more capacity to download by design
- Infrastructure management — prevents upstream congestion on shared neighborhood infrastructure
- Business model — discourages home servers, creates product differentiation
- Historical assumptions — users traditionally downloaded more than uploaded

Fiber doesn't have inherent asymmetry but ISPs may artificially cap upload on residential plans.

## IPv6

IPv6 is the successor to IPv4, designed to solve address exhaustion.

IPv4 addresses are 32 bits (~4.3 billion addresses). We've run out, and NAT has been the workaround. IPv6 addresses are 128 bits — enough for every device on earth to have billions of unique public addresses.

Format comparison:

- IPv4: `192.168.1.47`
- IPv6: `2607:f8b0:4004:800::200e`

Key differences:

- No more NAT needed — every device can have a globally unique address with direct peer-to-peer connectivity
- SLAAC — devices can auto-generate their own address from network prefix and MAC address
- IPsec built in — encryption designed into the protocol
- Simpler headers — more efficient router processing

Adoption is slow because IPv4 and IPv6 don't directly interoperate (requiring dual-stack or translation), everything needs updating, and NAT works well enough that there's no urgent forcing function.

## MAC Addresses

A MAC (Media Access Control) address is a 48-bit hardware identifier burned into your network interface (e.g., `a4:83:e7:2f:9b:01`). It operates at a lower level than IP.

When devices communicate on the same local network, they use MAC addresses to send frames to each other. ARP (Address Resolution Protocol) bridges MAC and IP — broadcasting "who has this IP?" to discover the corresponding MAC.

MAC addresses are only relevant within a local network segment and don't traverse routers. Each hop strips the old MAC header and adds a new one.

Private IPs aren't stable enough to identify hardware — they're assigned dynamically and can change. MAC provides a stable, hardware-level identity that exists independently of IP configuration.

While MACs are burned in at manufacturing, they can be spoofed in software for privacy (avoiding tracking across networks), bypassing restrictions, or testing. Modern phones randomize MACs when scanning for WiFi networks to prevent tracking.

## The Layered Model

Each layer solves a different addressing problem:

- MAC — which physical interface on this local segment
- IP — which logical host on which network
- Port — which application/service on that host
