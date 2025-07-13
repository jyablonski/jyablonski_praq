# Template

## Core Requirements

- Users should be able to make profiles w/ various preferences
- Users should be able to view a stack of potential matches within some max distance of their current location
- Users should be able to match with other users

## Non-functional Requirements

- System should be able to scale to 20 million DAU
- System should have strong consistency for swiping (to get immediate notification if you've both swiped each other)
- System should load the matches stack w/ low latency <300 ms
- System should avoid showing matches that user has already passed on


## Out of Scope

- Chatting
- Image upload
- Live Video
- Supermatch
- Premium features

## Core Entities

- Profiles
- Matches

## API

- All endpoints require authentication from a logged in user, where JWT will be used in the header to verify requests

- POST /profiles {email}

{
  "age_min": 20,
  "age_max": 30,
  "distance": 10,
  "interestedIn": "female" | "male" | "both",
  ... 
}

- GET /feed?lat={}&long={}&distance={} -> User[]

- POST /swipes/{userId}

{
  decision: "yes" | "no"
}

## High Level Design (to satisfy functional requirements)

- API Gateway
    - Provides routing, authentication, and rate limiting
- Profile Service
    - Profile Service takes incoming requests for new profiles or preference changes, and saves them to the Postgres Database
    - It can also take in requests for incoming users looking for new matches, making SQL queries based on the preferences and geo location data
- Postgres Database (Profiles)
- Swipe Service
    - By separating this out, we can independently scale this separately from the Profile Service
- Cassandra Database (Swipe)s
    - Also separating the Database out makes sense because of the high volume of swipes we expect to receive
    - Partitioning on `swiping_user_id` enables an access pattern where you can very quickly find the users that somebody has already swiped left or right for
    - During each `/swipe` POST request, the Swipe Service checks if there is an inverse swipe in the Swipe Database and, if so, returns a match to the client.
- APNS (Apple Push Notification Service) and FCM (Firebase Cloud Messaging) can be used to send users notifications of when they have a match

## Database DDL

- Profiles

## Deep Dives

- How to ensure strong consistency with matches?
    - Sharded Cassandra w/ single-partition transactions
    - Or use Redis to temporarily store and manage swipes, and then flush data out to Cassandra every so often for durable storage
- How to ensure low latency on the user feed?
    - Can implement Elasticsearch and CDC to move profile data over and allow users to query from here
    - Can aggressively pre-compute a list of matches for each user for fast querying. But, they could very quickly blow through the entire precomputed cache here and we're back to running slow queries
    - Best solution is to use both: Elasticsearch, smart indexes on database tables, and pre-computing matches for users as often as we can
- How to ensure low latency on swipe feed when finding new potential matches for users?
    - Can implement Postgres <> PostGIS Extension to improve geospatial query performance
    - Could also introduce Elasticsearch & setup CDC to keep it updated, but this is more complex

## Napkin Math
