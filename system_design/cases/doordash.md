# Template

## Core Requirements

- Users should be able to see available restaurants near them and place delivery orders
- Drivers should be able to fulfill orders placed by customers

## Non-functional Requirements

- Placing an order should be eventually consistent (it's fine if there's a 15-30 second delay before riders can see new orders - it'll be a 40 minute wait anyways)
- Drivers fulfilling orders should be strongly consistent (to avoid multiple drivers getting the same order etc)
- Driver Location should be updated on a consistent basis (every 30 seconds)

## Out of Scope

- API Integration with each individual restaurant
- Refunds
- Reviews
- No order updates after initial order
- Payment Processing
- Recommendations

## Core Entities

- Users
- Restaurants
- Orders
- Drivers

## API

- Assume all user requests use JWT for Auth and their current location

- GET /restaurants/?lat={lat}&long={long}&distance={distance}&category={category}

  - Get a list of restaurants within x distance of the user, can optionally specify food category

- GET /restaurants/:restaurant_id/menu

  - To see menu

- GET /restaurants/:restaurant_id

  - To get location, name, category, rating, estimated dellivery time etc
  - Returns lat long

- POST /orders {restaurant_id, location_id, user_location, [] order_items}

  - Place an order at a restaurant at a specific location, with the order information
  - Async wait for order confirmed from the 3rd party ?

- POST /orders/:order_id {status: accepted}

  - For a Driver to accept an Order

- POST /driver_location {lat, long}

  - Update Driver Location
  - Runs automatically every 30 seconds while working
  - Not using /drivers/:driver_id/location because a driver will only ever update their own location using the JWT token to automatically identify them

- GET /drivers/?lat={lat}&long={long}&distance={distance}

  - Get a list of all drivers within a specific lat long location

## High Level Design (to satisfy functional requirements)

- CDN for caching all static content, menu information etc
- API Gateway for routing, authentication, load balancing
- Read Service to handle all incoming user read requests
  - Makes geospatial queries to Postgres to serve requests
  - Reads from both Postgres and Redis to serve content and location data to users
- Order Service which handles all incoming orders, waiting for restaurant confirmation, and placing them in the Order Queue
- Order Fulfillment Service which uses a complex algorithm to take orders out of the Order Queue and find a suitable Driver to fulfill them, storing the information in Redis
- Order Queue which sits in front of the Order Service so we handle User Orders FIFO to handle surges and have fair order matches. Used by the Fulfillment Service
- Location Service to handle updating all active driver information in real-time (< 30 seconds)
- Notification Service to notify users of an accepted or delivered orders
- Redis for use with the Location Service to store active driver location information in real time
- Redis for locking Order Fulfillment Service w/ available Drivers
- Postgres w/ PostGIS Extension for geospatial queries

## Database DDL

- users
  - skipping ddl because it's not important to this problem
- orders
  - id, user_id, restaurant_id, driver_id, created_at
  - 1 row per user order
  - composite index on (user_id, created_at)
- order_details
  - id, order_id, product_id, price, user_id, created_at
  - 1 row per item in the order
  - index on order_id
- order_status
  - order_id, is_fulfilled, cancellation_reason?, created_at
  - maybe after the order is fulfilled, we fill in this table w/ information from redis and then clear the record in redis for long term storage
- restaurants
  - id, restaurant_chain_id, lat, long, category, created_at, modified_at
  - 1 row per individual restaurant
  - INDEX using GIST on `(ST_MakePoint(long, lat))`
- restaurant_chains
  - 1 row per restaurant chain (applebees)
  - not filling ddl because it's not important
- drivers
  - id, primary_location, last_name, date_of_birth, license_id, profile_pic_s3_location, created_at, modified_at
  - maybe when they initially sign up we collect basic info on them

## Deep Dives

- Order Fulfillment service should wait 15-30 seconds for a driver response to verify if they can accept the order or not. If not, move on to next driver.
- How to handle drivers being active or inactive so we dont send requests to people who won't accept.
- Can make location updates dynamic - if you're in the boonies or a delivery will be > 1 hour, maybe slow down the updates. but if you're in NYC you could even speed them up.
- Can store driver states in Redis. AVAILABLE, ON_DELIVERY, OFFLINE, with drivers sending heartbeat statuses.
- Order Status Database table could be improved

## Napkin Math

1 million DAU

1 million orders per day

- 1,000,000 10^6 / 10^5 = 10 orders per second
- Postgres and Redis can easily handle this workload
- Do we have enough drivers to fulfill demand is the question, but not a software problem

Location Service

- 100k drivers, assume 50% are active at a time
- 50,000 drivers updating location every 30 seconds.
- 1667 requests per second to Redis, which is fine.

## What I Missed

- WebSocket Service or Server-sent Events for live updates for users
- Driver App should maintain persistent connection to receive orders in real time
- User App receives driver location updates during delivery
- GiST or SP-GiST indexes on geometry columns
- Redis for caching popular queries
- Driver states during order fulfillment (en_route, picked_up, en_route, delivered, cancelled) etc
- After a user submits order, establish Websocket connection between them and the Notification Servicew to provide real-time updates for status of order and driver location
