# REST API Auth

Access Tokens and Refresh Tokens are commonly used in authentication and authorization mechanisms for Websites, REST APIs, and other Applications

Access Tokens:

- Grant access to protected resources or APIs on behalf of the user or client
- Are usually short-lived, expiring minutes or hours after use. This is a security feature to limit the time a stolen token can be used.
- Clients send their Access Tokens to the REST API for every request in the authorization header of the request.
  - `Authorization: Bearer <access_token>`

Refresh Tokens:

- Used to obtain a new access token without requiring the user to re-authenticate. This allows for a smooth user experience, as the client can refresh its access tokens when they expire
- Are usually long-lived and can last hours or days or even longer depending on the server's configuration
- When an Access Token expires, the client can send the refresh token to the authorization server for a new access token.

Client ID and Client Secret are unique identifiers per Client that's interacting with the API. They're used by the authorization server to identify the client making the request.


## The Flow

1. Initial Authentication
   1. Client provides its Client ID, Client Secret, and any other user creds to the authorization server
   2. The Authorization server returns an access token and a refresh token
2. Accessing Resources
   1. The Client is able to use the access token to access protected resources
3. Token Expiration
   1. When the access token expires, the client uses the refresh token to request a new access token from the authorization server

## Why a Refresh Token

A refresh token is necessary to limit exposure of your Client ID + Secret credentials to obtain a new access token every time. You're minimizing the number of requests being made with sensitive credentials over the network.

The refresh token workflow also allows seamless re-authentication for clients. This enables them to have continuous access without frequent interruptions and can stay logged in for longer periods of time.

The load on the authentication server is less as well, because you don't constantly need to check Client IDs + Secrets anymore.

- Basically imagine the refresh token as a JWT. To issue a refresh token, you have to make database calls to verify the client id + secret are valid. To validate a refresh token, you just have to verify that the JWT hasn't been tampered with; you don't have to make a database call. 
- This means faster operations for the client + server when checking refresh tokens, and fewer database calls than if you avoided the refresh token route all together
- Imagine Uber or Facebook here. You cannot be doing this when you have millions of users and 100k requests / minute coming in to your services.

When refresh tokens are used to issue new access tokens, you can potentially set things up where you offer clients the ability to change the scope of their permissions if they need to re-evaluate their permissions so they can change them as needed.