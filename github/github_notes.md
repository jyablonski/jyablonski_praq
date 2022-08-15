# GitHub OpenID Connect
GitHub Actions is often used for CI CD workflows in cloud providers like AWS.  To access those resources, you have to hard code in credentials in GitHub, effectively duplicating them in both the cloud provider and now on GitHub.  

OpenID Connect takes a different approach where you instead request short-lived access tokens when you need them.  Both GitHub and the Cloud Provider need to support OIDC for this to work.  A Trust Relationship is then established to authorize the credentials.

Cloud Provider settings - you must add conditions to your trust policy for incoming requests, so untrusted workflows or repositories cann't sneak their way in.

## Benefits of OIDC
1. You don't store Cloud Secrets
2. More authentication and authorization management
3. Short lived tokens allow for better security.


