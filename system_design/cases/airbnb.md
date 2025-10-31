# Template

## Core Requirements

- Hosts should be able to list their own properties for short term rental in exchange for payment
- Users should be able to search for listings in a particular area
- Users should be able to make bookings for available listings and have seamless payment experience
- Users should be able to chat with their host after making a confirmed booking

## Non-functional Requirements

- Search and initial host availability should be eventually consistent
- Bookings should be strongly consistent
- Search should be fast <500 ms
- Chats should be low latency

## Out of Scope

- Reviews
- Refunds
- Disputes
- Pricing (No way you could fit this in a 30-45 minute interview, it would touch every service)
- Trust & Safety, because fuck em

## Core Entities

- Hosts
- Users
- Listings
- Bookings
- Chats

## API

Assume all signed-in users use JWT for authentication to identify each request

- GET /listings?lat={lat}&long={long}&distance={distance}&checkin_date={checkin_date}&checkout_date={checkout_date} ...
  - Can also filter by price and sort by xyz etc
  - Amentities should be searchable parameters here too, but not listing them all out
  - For users to search for listings in a specific area
  - Page & limit as well, has to be paginated
- GET /listings/{listing_id}
  - Get all details for a specific listing
- POST /listings { lat={lat}, long={long}, price={price}, amentities={xyz} }
  - For hosts to put their listing up
  - More options: title, description, max_guests, bedrooms, bathrooms, photos, house_rules, cancellation_policy
- PUT /listings/:listing_id { ... }
  - Update price on your listing or something
- POST /bookings/reserve { listing_id, checkin_date, checkout_date }
  - Returns { reservation_id, listing_id, extra_details ...}
- POST /bookings/confirm { reservation_id, payment_method_id }
  - For users to make bookings at a specific location for a
- POST /bookings/:booking_id/cancel
- GET /bookings?page={page}&sort={sort}
  - View past, present, or future bookings
- GET /bookings/:booking_id/chat
  - View chats with past or present hosts / users
- POST /bookings/:booking_id/chat { message }
  - Host or User can send chat message

## High Level Design (to satisfy functional requirements)

- CDN to cache static content at the edge
- API Gateway for load balancing, auth, rate limiting etc
- Search Service for managing all search requests for listings
  - Handles GET /listings with geospatial + filter queries
  - Queries Postgres (PostGIS) for location-based search
  - Checks Redis cache for popular searches (Manhattan, SF)
  - Returns paginated results with availability hints
- Listing Service manages creating or updating existing listings
- Chat Service to manage chats between hosts and users
  - Utilizes Websocket for fast response and low latency
- Booking Service to manage booking workflow

  - User searches -> Search Service queries Postgres + Redis cache
  - User selects dates -> Booking Service checks availability
  - User clicks "Reserve" - Acquire Redis lock booking:lock:{listing_id}:{dates} TTL=10min
  - User enters payment -> Call Stripe, store payment_intent_id
  - Stripe webhook confirms -> Insert booking, release lock, invalidate cache
  - Create conversation for chat

- Postgres for primary backend database
  - PostGIS extension setup to enable better search capabilities and geospatial queries
- Redis for caching recent searches or popular content

## Database DDL

- users
  - ignoring as its not necessary
- hosts
  - id, name, email, created_at, modified_at
- locations
  - id, host_id, no_bedrooms, no_bathrooms, sq_ft, price, lat, long, city, state, created_at, modified_at
  - INDEX using GIST on `(ST_MakePoint(long, lat))`
- listings
  - id, host_id, title, description, lat, long, price_per_night, max_guests, num_bedrooms, num_bathrooms, amenities (JSONB), created_at, modified_at
  - INDEX GIST (ST_MakePoint(long, lat))
- bookings
  - id, listing_id, user_id, checkin_date, checkout_date, total_price, status (pending/confirmed/cancelled), stripe_payment_intent_id, created_at
  - UNIQUE INDEX on (listing_id, checkin_date, checkout_date) WITH overlapping date check constraint
- conversations
  - id, user_id, host_id, booking_id, created_at
- messages
  - id, conversation_id, sender_id, message, created_at
  - index on (conversation_id, created_at)

## Deep Dives

- Is search w/ PostGIS good enough, or have to pivot to something like Elasticsearch for full text search and better scalability
  - Postgres should scale fine to start off with. PostGIS offers enough geospatial capability to get the job done and it fits within the napkin math that's been laid out.
  - As we approach 10M+ listings or need more complex full-text search capabilities, we'd migrate to Elasticsearch - which is actually what Airbnb uses in production."
- Pricing Service would be a big undertaking, but what does that look like
- Booking Process:
  - Two-step process: reserve then confirm. Reserve checks availability, creates a temporary lock in Redis with a 10-minute TTL, and returns the total price.
  - This prevents double-booking via race conditions. Confirm validates the reservation still exists, charges via Stripe using the reservation_id as an idempotency key, then creates the booking in Postgres and cleans up Redis.
  - If the reservation expires or payment fails, the user can try again without losing the listing.
  - 10-min timer encourages completion
- Host can exchange temporary code to get into the property for users via the Chat system
  - There are other alternatives here though. Can integrate with smart lock APIs, setup a calendar integration to send a smart lock code on the day of checkin etc

## Napkin Math

- Assume 10 M DAU
- Assume 25 read events per day, or 250 M read events per day
  - 250,000,000 = 25 \_ 10^7 / 10^5 = 100 \* 25 or 2500 read events per second
- Assume 2 M bookings per day,
  - 2,000,000 or 10^6 / 10^5 = 100 bookings per second.
- All fine for Postgres
