# Security

## HTTP Headers

HTTP Headers are a list of strings sent & received by client requests and server responses. They're hidden from end-users and only used by clients & servers.

- Content-Type - Tells the browser how to interpret results. `text/html; charset=UTF-8` or `application/pdf` etc.
- Request - The Get/Put/Post Request, the URL used for it, and the HTTP Version.
- Cookies - Comma separated key value pairs.
- Referer - The webpage you were sent from if you clicked a URL on there.
- Accept-Language - Default language setting for the user. If you're french a website might return french characters if it's been designed for that.
- Authorization - Used to provide credentials to authenticate with a server
- Encoding - gzip, deflate. Most modern browsers support gzip so information will be sent over the internet in a compressed format to save bandwidth and time.
- Connection - `keep-alive` or `close` depending on whether the network connection should stay open after a transaction or close.
- Keep-Alive - Defines settings for the network connection, like how long an idle connection should remain open for or what the max number of requests should be.
- Host - Simple header specifying the host. if no port is listed, it defaults to 80 or 443 depending on whether it's HTTP or HTTPS
- User Agent - Client Browser & Operating System information.
- Cache - Stuff like `max-age=3600` to specify how long to cache results for to reduce server load and improve load times in the browser.
  - Can also be set to `no-cache`.
- If-Modified-Since - If a web page is already cached in your browser it will compare against this timestamp field to see if you can use the cache again, or retrieve new results.

## Auth

### SAML

Old school XML Based standard used for authentication and authorization, traditionally used for Single Sign On (SSO).

Used for authentication and authorization using a Service Provider (G Suite, Salesforce) and an Identity Provider (Okta, OneLogin etc).

- The Service Provider agrees to trust the Identity Provider in the authentication process.

### Basic

Basic Authentication uses basic username / email and password pairs and sends them over in the HTTP Header to allow you to sign into servers + websites.

- The credentials are base64 encoded before being sent over.
- base64 is used to ensure that your username + password are appropriate ASCII values. It's basically just a format that every computer can understand.
- It also adds some form of obfuscation to the clear-text username + password.
- This is _NOT_ an encryption and does not mean your credentials are secure.
- Fine for testing and prototyping, but not for production.
- `Authorization Basic anlhYmxvbnNraTpwYXNzd29yZA==`

### Bearer

More advanced and secure form of authentication uses tokens instead of credentials.

- The basic idea is users still sign in, but you return them an access token which is what actually allows access to what they're authorized to do as that user.
- The token is separate identification than their username + password, and it can have an expiration timestamp (like 30 mins etc).
- The token can also be encrypted so that it cannot be tampered with.

### JWT

JSON Web Token

- Self-contained mechanism to verify and authenticate users, and is trusted because it's digitally signed using a secret key that only the server application code knows
- When the JWT is created it is signed using the secret key, and only the secret key can decode a token & use it.
- Helps in stateless architectures; don't need to do database lookups for session IDs anymore.
- Uses a Secret Key to encrypt things; if this secret is exposed then that's bad news bears for your website.

### OAuth2

How do you let an app access your data without necessarily giving it your password

Open standard used for authorization, it allows apps to provide an application with delegated authorization.

- It only authorizes devices, APIs, and servers with access tokens rather than credentials and works over HTTPS.
- Similar to hotel key cards, but for apps. You can only get a card through an authentication process like the front desk, but then you can use the card as much as you want to get in and out of your room.

Example is allowing Facebook to access your data from a 3rd party app.

### OpenID Connect

Builds on top of OAuth2 and adds Federated Authentication.

Example is logging into Spotify using your Google GMail Credentials.

- This is federated authentication.

I use it in GitHub Actions workflows to allow runners to assume IAM Roles in my AWS Account to have S3 + ECR permissions to enable CI / CD.

- IDP is `https://token.actions.githubusercontent.com`
- The Audience is STS `sts.amazonaws.com`
- The IAM Policies can be whatever, such as S3 or ECR Permissions.
- The Trust Policy is where the magic happens.

GitHub Actions Workflow

```
permissions:
      id-token: write
      contents: read
```

IAM Trust Policy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::288364792694:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:jyablonski/nba_elt_rest_api:*"
                }
            }
        }
    ]
}
```

The full OIDC Token

```
{
  "typ": "JWT",
  "alg": "RS256",
  "x5t": "example-thumbprint",
  "kid": "example-key-id"
}
{
  "jti": "example-id",
  "sub": "repo:octo-org/octo-repo:environment:prod",
  "environment": "prod",
  "aud": "https://github.com/octo-org",
  "ref": "refs/heads/main",
  "sha": "example-sha",
  "repository": "octo-org/octo-repo",
  "repository_owner": "octo-org",
  "actor_id": "12",
  "repository_visibility": "private",
  "repository_id": "74",
  "repository_owner_id": "65",
  "run_id": "example-run-id",
  "run_number": "10",
  "run_attempt": "2",
  "runner_environment": "github-hosted"
  "actor": "octocat",
  "workflow": "example-workflow",
  "head_ref": "",
  "base_ref": "",
  "event_name": "workflow_dispatch",
  "ref_type": "branch",
  "job_workflow_ref": "octo-org/octo-automation/.github/workflows/oidc.yml@refs/heads/main",
  "iss": "https://token.actions.githubusercontent.com",
  "nbf": 1632492967,
  "exp": 1632493867,
  "iat": 1632493567
}
```

## OpenID Connect vs OAuth2

OpenID Connect (OIDC) and OAuth 2.0 (OAuth2) are related but serve different purposes in the realm of authentication and authorization.

**OAuth 2.0 (OAuth2):**

1. **Purpose:** OAuth2 is an authorization framework that allows one application to access the resources of another application on behalf of the user, without sharing the user's credentials. It is primarily used for securing APIs and granting limited access to resources.

1. **Scenarios:** OAuth2 is commonly used for scenarios like enabling a mobile app to access a user's Google Drive files without the app having the user's Google password. It's also used for securing APIs for third-party access.

1. **Components:** OAuth2 has roles like the Resource Owner (the user), Client (the application making requests), Authorization Server (responsible for user authentication and consent), and Resource Server (where the user's data or resources are stored).

1. **Grant Types:** OAuth2 defines multiple grant types, such as Authorization Code, Implicit, Resource Owner Password Credentials, and Client Credentials, each suitable for different use cases.

1. **Tokens:** OAuth2 generates access tokens that represent a user's permission to access certain resources for a specific period. These tokens are typically short-lived.

**OpenID Connect (OIDC):**

1. **Purpose:** OIDC is an identity layer built on top of OAuth2. Its primary purpose is to provide a standardized way for applications to authenticate users and obtain their identity information (e.g., name, email) in a secure and interoperable manner.

1. **Scenarios:** OIDC is commonly used in scenarios where a website or application wants to allow users to log in with their existing accounts from identity providers like Google, Facebook, or a company's own identity service.

1. **Components:** OIDC extends OAuth2 by introducing an ID Token, which contains identity information about the user. It also adds an Identity Provider (a trusted party that authenticates users) as a new component.

1. **Tokens:** OIDC introduces the ID Token in addition to access tokens and refresh tokens. The ID Token contains user information and is used for user authentication.

**Key Differences:**

- **Purpose:** OAuth2 is focused on authorization, allowing applications to access resources. OIDC is focused on authentication and user identity.

- **Tokens:** OAuth2 primarily uses access tokens to authorize access to resources. OIDC introduces the ID Token for user authentication.

- **Components:** OAuth2 involves the Resource Owner, Client, Authorization Server, and Resource Server. OIDC adds the Identity Provider and ID Token.

- **Use Cases:** OAuth2 is used for securing APIs and granting access to resources. OIDC is used for user authentication and obtaining user identity information.

In many cases, OIDC is used alongside OAuth2. For example, a web application may use OAuth2 to secure API access and OIDC to authenticate users using their Google or Facebook accounts. This combination allows for a secure and user-friendly experience in web and mobile applications.

## CVE

Common Vulnerabilities and Exposures (CVE) is a standard identifier for known security vulnerabilities. These are things that attackers or bad actors can exploit within your application or service to disrupt operations, access sensitive data, take advantage of the service.

In the context of containers and docker images, CVEs track vulnerabilities in:

- Base operation system packages (Ubuntu, Alpine)
- Programming language packages (Python, Node.js)
- System libraries (OpenSSL, glibc)

Security Engineers focus on these because containers often run in production directly exposed to the internet, making any vulnerability a potential entry point for damage. Many frameworks (SOC 2, PCI-DSS, HIPAA) require vulnerability management programs.

The goal isn't zero CVEs - it's zero exploitable attack vectors in your actual production context. A well-architected system with 10 unexploitable CVEs is more secure than a poorly designed one with zero reported vulnerabilities. Getting to absolutely zero CVEs though is practically impossible for several reasons:

- False Positives: Vulnerability scanners often flag issues that don't actually exist in your specific configuration or version.
- OS Package Bloat: Base images include hundreds of packages. Even minimal images like Alpine contain utilities you'll never use, each with their own CVE history.
- Informational CVEs: Not every CVE is exploitable. Many are theoretical, require local access, or apply to specific use cases.
- The Math Problem: A typical Ubuntu base image might have 200+ packages. If each has a 1% chance of having an open CVE at any moment, you're statistically guaranteed to have multiple CVEs.

There are situations where a CVE exists, but poses no danger to your application:

- Unused binaries: your image has `curl` with a CVE, but your app uses Python's `requests` library. Or `bash` has a vulnerability, but your app never spawns shells or processes user input w/ bash
- Unexposed services: your image has a vulnerability in `nginx`, but you use it as a reverse proxy on a private network, and the vulnerability requires direct internet access
- Inaccessible code paths: a function in your app has a vulnerability, but the function is never called

### CVSS Scores

Common Vulnerability Scoring System (CVSS) is a standardized framework for rating the severity of security vulnerabilities. Think of it as a report card that gives each CVE a numerical score from 0.0 to 10.0, where 10.0 is the most critical.

- While effective, a high CVSS score for a package that your app doesn't use is less dangerous than a CVSS 6.0 in your authentication system for example

The score is calculated from multiple factors and impact metrics:

- Attack Vector: Can it be exploited remotely (network) or does it require local access?
- Attack Complexity: Is it easy to exploit or does it require specific conditions?
- Privileges Required: Does the attacker need admin rights or no authentication at all?
- User Interaction: Does a user need to do something (click a link) or is it automatic?
- Confidentiality: Can the attacker read sensitive data?
- Integrity: Can they modify data?
- Availability: Can they crash the system or cause denial of service?

Examples:

- CVSS 9.8 (Critical): Remote code execution vulnerability in a web server that requires no authentication, no user interaction, and gives full system access. Think Log4Shell.
- CVSS 5.3 (Medium): Information disclosure vulnerability that requires an authenticated user to access specific configuration files but can't modify anything.
- CVSS 3.1 (Low): Local privilege escalation that requires the attacker to already have user access and specific system conditions to be met.

Smart teams combine CVSS with:

- EPSS (Exploit Prediction Scoring System): Probability the vulnerability will actually be exploited
- KEV (Known Exploited Vulnerabilities): CISA's catalog of actively exploited CVEs
- Reachability Analysis: Is the vulnerable code actually executed in your application?

## SOC 2

SOC 2 (Service Organization Control 2) is a security audit framework that verifies a company has proper controls to protect customer data. It has become the minimum viable security credential for B2B SaaS selling to enterprises.

Why it matters: Many enterprise buyers won't even start procurement without SOC 2 Type II. Without it, you face 3-6 month security reviews, 200+ question questionnaires, and deals that stall indefinitely.

Type I vs Type II:

- Type I: Point-in-time assessment (~$15K-$40K, 1-3 months) - rarely accepted by enterprises
- Type II: Operating effectiveness over 6-12 months (~$25K-$100K+, 6-12+ months) - this is what enterprises require, must be renewed annually

Trust Service Criteria (choose which to include):

- Security (mandatory): Access controls, vulnerability management, change management, monitoring
- Availability (optional): Uptime, disaster recovery, system monitoring
- Confidentiality (optional): Data classification, encryption
- Processing Integrity (optional): Data accuracy, error handling
- Privacy (optional): Privacy notices, data retention, disposal

Most companies pursue Security only or Security + Availability.

Who audits: Licensed CPA firms with cybersecurity practices (Big 4 accounting firms like Deloitte/PwC/EY/KPMG, or specialized firms like Prescient Assurance, A-LIGN). Your company hires and pays for the auditor.

When to get it:

- When actively pursuing enterprise deals
- Series A/B stage ($3M-$10M ARR)
- When prospects explicitly require it
- When competitors have it and you're losing deals

The reality: SOC 2 doesn't guarantee security - it verifies you have documented controls operating consistently. It's compliance theater to some extent, but it's necessary theater that signals "we're enterprise-ready" and provides standardized assurance that enterprises trust.

So really it's just following best practices and having good processes and workflows in place to build and maintain your software, and then having engineers and the company actually follow those processes, and then writing all of it down in the form of documentation, policies, and procedures so you're prepared for when auditors come.

## Keycloak

Keycloak is a self-hosted Identity and Access Management tool that competes with something like Okta to provide:

- SSO
- MFA
- User federation and management
- OAuth 2.0 and OpenID Connect support

The key differences compared to Okta are:

- Open Source
- Self hosted on your own infrastructure (K8s + EC2 etc)
- No license fee
- Full control + customization
- Requires internal engineering effort to implement, build, and manage

Typically, you should use managed services for things you don't specialize in, so you can focus on your own core value proposition. So, it normally makes more sense for orgs to go with Okta and just pay the SaaS fee in order to gain access to the functionality provided by these tools.

When does it make sense to go with Keycloak?

- When you're selling software to enterprises that they expect to integrate with their SSO provider, you need a custom identity layer that can handle this
- When you have 1000s of users at scale, the Okta per-user cost would become untenable.
- When you have highly custom authentication flows that go beyond standard OAuth / OIDC
- When you have compliance requirements that require it, like government contracts requiring on-prem deployment etc or industry regulations that require data can't leave certain jurisdictions

Self-hosting Keycloak isn't just "spin up a container":

- High availability setup means multiple nodes and load balancing
- Database management and backups
- Security patches and updates
- Monitoring and incident response
- Testing auth flows (you really don't want bugs here)

Auth/identity is absolutely critical infrastructure. If it breaks, everything breaks. This is exactly the kind of thing you want someone else to be responsible for unless you have a compelling reason otherwise.
