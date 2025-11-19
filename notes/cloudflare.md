# Cloudflare

Cloudflare is a content delivery network (CDN) and internet security company that sits between your users and your application servers. It's a protective and performance-enhancing layer that handles requests before they reach your actual infrastructure.

Core Services:

1. CDN - When users visit your app, instead of connecting directly to your server (which is probably in 1 location), they connect to Cloudflare's nearest data center of their 300+ global locations. From here Cloudflare caches static content like images, CSS, and JS and serves it to the user, reducing load times

2. DDOS Protection - Cloudflare absorbs and filters out malicious traffic trying to overwhelm your servers. Without it, a DDOS attack could knock your application servers offline by flooding them with requests

3. DNS Management - Cloudflare acts as your DNS provider, translating domain names (yourapp.com) into IP addresses. Their DNS is one of the fastest globally, and they include security features to protect against DNS-based attacks

4. Web Application Firewall (WAF) - This filters out malicious HTTP requests before they reach your application, blocking SQL injection attempts, cross-site scripting, and other web exploits

5. SSL/TLS Encryption - Cloudflare provides free SSL certificates and handles the encryption between users and your site, ensuring secure HTTPS connections without you needing to manage certificates yourself.

When you use Cloudflare:

1. You point your domain's DNS to Cloudflare
2. Cloudflare becomes the "front door" to your application
3. All traffic flows through them first
4. They apply security rules, serve cached content, and optimize connections
5. Only legitimate, clean traffic reaches your actual servers

By default, it automatically caches a handful of files and objects such as:

- JPG, PNG, CSS, JS, MP4, PDF, ICO etc
- HTML is not cached by default since a lot of times it's dynamic
- You can setup rules to cache, set TTL, or to bypass cache on whatever endpoints or pages you want

## Setup

Current AWS Architecture:

```text
jyablonski.dev (Route53 DNS)
         ↓
   AWS Load Balancer
         ↓
   EC2 Target Group
         ↓
    Your App
```

The actual process involves:

1. Create a Cloudflare account
2. Add `jyablonski.dev` as a site
3. Cloudflare will scan your existing DNS records from Route53
   - You can either import the ones it scans, or create new DNS records manually
   - It'll look something like below

```text
Type    Name                 Value
A       jyablonski.dev      52.1.2.3 (your ALB IP)
CNAME   www                 jyablonski.dev
CNAME   api                 your-alb-123.us-east-1.elb.amazonaws.com
```

4. Update your Nameservers

   - Cloudflare provides nameservers like `ns1.cloudflare.com` etc
   - You have to go to the provider you bought the domain from (Squarespace) and replace the Route53 nameservers with Cloudflare's ones
   - Before: `ns-123.awsdns-12.com`
   - After: `ns1.cloudflare.com`

5. Configure Cloudflare Settings
   - Some settings you configure are proxy status, SSL/TLS mode, caching rules, security rules like WAF and rate limiting etc
   - Cloudflare's orange cloud option for the proxy status means you get CDN, security, caching benefits etc. This is typically what you want.

New architecture:

```text
User Request
     ↓
Cloudflare DNS (ns1.cloudflare.com)
     ↓
Cloudflare Edge Network (proxied traffic)
     ↓
AWS Load Balancer (your-alb.elb.amazonaws.com)
     ↓
EC2 Target Group
     ↓
Your App
```

## Billing

They have a generous free-tier, along with pro, business, and enterprise plans

- Most websites are small and can be covered in the free-tier
- Enterprises pay for security, hands-on support, and advanced features

Cloudflare has multiple advantages over AWS for CDNs:

- No bandwidth/data transfer charges - Serve 1GB or 1TB, same price
- No per-request charges - 1 million requests or 1 billion, same price
- No egress fees - Unlike AWS where data leaving costs money
- No charges for DDoS attacks - Even if you get hit with 100TB of attack traffic

## My projects

- CloudFront is better for: Pure static S3 sites, AWS-native setups, wanting private S3 access
- Cloudflare is better for: Apps with APIs, needing real security (DDoS/WAF), multiple services, predictable billing
- For my projects: Keep CloudFront for S3 static sites, use Cloudflare for your main app with the ALB for the best of both worlds

## Under the hood

Cloudflare uses Anycast - a routing technique where the same IP address (like 104.26.10.123) is announced from 300+ locations worldwide.

- This allows cloudflare to serve content for `https://jyablonski.dev` from 300+ locations worldwide using the same IP
- You don't configure it - it's just how Anycast works. The internet's routing protocols (BGP) naturally send traffic to the nearest location announcing that IP.

When Cloudflare is setup & it starts taking user requests, here's what happens:

1. User types `https://jyablonski.dev` from NYC
2. DNS lookup goes to Cloudflare nameservers
3. Cloudflare returns an IP `104.26.10.123` (Cloudflare's Anycast IP)
4. User connects to: `104.26.10.123` (Cloudflare edge server in NYC)
   - Note: for all subsequent steps, your backend architecture interacts with this specific Cloudflare edge server for the remainder of the flow
5. Cloudflare returns any cacheable content to the user that's available at that edge location
6. Cloudflare reaches out to ALB to fetch any other content it needs
7. ALB reaches out to backend servers on EC2 to get whatever content
8. ALB returns results back to Cloudflare
9. Cloudflare returns results back to the user

Cloudflare also forwards request headers along to the origin servers, like the real user IP, user's country etc.

- Your backend no longer gets these details because the user request is hitting Cloudflare first, and your ALB's only see the requests that Cloudflare has forwarded along. So that's why they need to be included in the header

## Gotchas

1. WebSocket Connections require additional setup & configuration in Cloudflare
2. ALB Health checks still work normally - they bypass Cloudflare
3. Cloudflare IPs will show up in your application logs, not user IPs
