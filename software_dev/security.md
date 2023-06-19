# Security

## HTTP Headers

HTTP Headers are a list of strings sent & received by client requests and server responses.  They're hidden from end-users and only used by clients & servers.
- Content-Type - Tells the browser how to interpret results.  `text/html; charset=UTF-8` or `application/pdf` etc.
- Request - The Get/Put/Post Request, the URL used for it, and the HTTP Version.
- Cookies - Comma separated key value pairs.
- Referer - The webpage you were sent from if you clicked a URL on there.
- Accept-Language - Default language setting for the user.  If you're french a website might return french characters if it's been designed for that.
- Authorization - Used to provide credentials to authenticate with a server
- Encoding - gzip, deflate.  Most modern browsers support gzip so information will be sent over the internet in a compressed format to save bandwidth and time.
- Connection - `keep-alive` or `close` depending on whether the network connection should stay open after a transaction or close.
- Keep-Alive - Defines settings for the network connection, like how long an idle connection should remain open for or what the max number of requests should be.
- Host - Simple header specifying the host.  if no port is listed, it defaults to 80 or 443 depending on whether it's HTTP or HTTPS
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
- base64 is used to ensure that your username + password are appropriate ASCII values.  It's basically just a format that every computer can understand.
- It also adds some form of obfuscation to the clear-text username + password.
- This is *NOT* an encryption and does not mean your credentials are secure.
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
- Similar to hotel key cards, but for apps.  You can only get a card through an authentication process like the front desk, but then you can use the card as much as you want to get in and out of your room.

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