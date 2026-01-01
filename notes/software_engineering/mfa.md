# MFA

## How TOTP Works

MFA apps use TOTP (Time-based One-Time Password) to generate rotating 6-digit codes. The system relies on two components:

- A shared secret key
- The current time

## Initial Setup Process

When you scan a QR code:

- The QR code contains a secret key (a long random string)
- This secret gets stored locally in your authenticator app
- The same secret is stored on the service's server
- This is the only time your app and the server need to communicate

## Code Generation

Every 30 seconds, both your phone and the server independently generate the same code:

Inputs:

- The shared secret key
- Current time (rounded to 30-second intervals)

Process:

- Run these through a cryptographic hash function (typically HMAC-SHA1)
- Algorithm outputs a 6-digit number

Key insight: Since both sides have identical inputs, they produce identical outputs - without any communication between them.

## Why It Works Offline

Your phone only needs:

- The secret (stored from initial QR scan)
- An accurate internal clock

No internet connection required. The server performs the same calculation independently.

## Authentication Flow

When a user logs in with 100 million users in the system:

1. User enters username and password
1. Server looks up user account in database
1. Server retrieves that specific user's MFA secret key (a field in the database record)
1. Server runs TOTP algorithm (secret + current time)
1. User enters code from their app
1. Server compares codes - if they match, authentication succeeds

Database storage: Each user has a unique secret key stored as a field in their account record, alongside username, password hash, email, etc.

## Security Features

Time-based rotation: Codes expire every 30 seconds, making intercepted codes quickly useless

Unpredictable: Cryptographic hashing means you can't predict the next code from the current one

No transmission: Since codes are generated locally, nothing is sent over the network to intercept

Clock drift tolerance: Servers typically accept codes from ±1 time window (±30 seconds) to account for minor clock differences

## Standardization

The TOTP algorithm is standardized as RFC 6238, which is why:

- Any authenticator app works with any service
- You can switch between Google Authenticator, Authy, 1Password, etc.
- All apps "speak the same language"

## Performance Considerations

- Generating a TOTP code is computationally cheap (just a hash function)
- Database lookup for the user's secret key is the main overhead
- This lookup already happens during normal authentication anyway
- Scales well even with millions of concurrent users
