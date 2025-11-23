# Web Application Firewall (WAF)

Web Application Firewalls are a security layer that protects web apps from common threats such as SQL Injection, cross-site scripting, and DDOS attacks by monitoring and filtering incoming HTTP(s) requests based on pre-defined rules.

WAFs can:

- Block / Allow IP Addresses
- Offer rate limiting services to only allow x amount of requests by certain IPs in a given time window
- Perform geo-blocking and restrict access by location
- Detect and block malicious queries

Some examples of what WAFs prevent are:

- SQL Injection is when attackers inject malicious SQL into a web app that runs database queries, such as something like `' OR '1'='1`
  - WAFs can block requests containing these SQL keywords like UNION, SELECT, ' OR ', DROP TABLE
- Cross Site Scripting (XSS) is when attackers inject malicious JavaScript into a website, and it runs on a victim's browser.
  - This can steal cookies, session tokens, or credentials
  - WAFs can block requests containing these JavaScript keywords like `<script>, <iframe>, onerror=,` etc.
- DDoS attacks flood a server with massive amounts of traffic from multiple compromised machines (botnets) to make the service slow or unavailable.
  - Volumetric Attacks – Overwhelm bandwidth (e.g., UDP floods, DNS amplification)
  - Protocol Attacks – Target weaknesses in protocols (e.g., SYN floods)
  - Application-Layer Attacks – Mimic real user behavior (e.g., slow HTTP requests)
  - WAF can limit high volumes of requests from 1 IP and help mitigate some of this behavior

Some CDNs like Cloudfront provide build in WAFs that may be more cost effective than AWS WAF

- A CDN (Content Delivery Network) sits between users and your origin server and filters traffic at the edge before it reaches your infrastructure.
- Either have flat rate, per-request, or custom plans

## When not to use one

Don't need WAFs when it doesn't provide significant value or when you don't have security needs for it. Some of these cases include:

- When you don't need to process user input, such as static web apps hosted on S3 + Cloudfront
- When the web app is internal & not exposed to the internet, or that only runs in your private VPC that requires you to connect to a VPN to use it
- When the web app is already properly secured with Authentication & Authorization (OAuth, JWT), has Rate Limiting capabilities, or proper input validation to prevent SQL injection + XSS
- When the web app has low traffic volumes and is not a high-value target, like a personal blog
- If you already have other security solutions in place, like AWS Shield Advanced for DDOS Protection and AWS Network Firewall for Layer 3/4 Security

## What to use in Combination with WAF

Network Firewalls can be used in combo w/ WAF to provide a more complete layer of protection. These firewalls block traffic at Layer 3/4 (TCP), so they can stop malicious traffic before it ever reaches your servers.
