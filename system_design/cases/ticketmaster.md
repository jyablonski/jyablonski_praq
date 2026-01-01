# Template

## Core Requirements

- Users should be able to search & for events
- Users should be able to view events like event date, location, and see potential pricing options for tickets
- Users should be able to book tickets for events

## Non-functional Requirements

- Booking tickets should be strongly consistent
- Searching and viewing events should be eventually consistent
- Users should have low latency for search events
- Scalability to handle surges from popular events

## Out of Scope

- Venues / seat mapping
-

## Core Entities

- Events
- Users
- Bookings

## API

Assume every API Request will come from a logged in user w/ a JWT or token included in the `Authorization` Header

- GET /events/:eventId -> {event, venue, performer, tickets[]}
- GET /search&term={term}&location={lat,long}&category={category}&date={date} -> Partial<Event>
- POST /booking/reserve {ticketId}
- POST /booking/confirm {ticketId, paymentDetails}

## High Level Design (to satisfy functional requirements)

- API Gateway to handle routing, rate limiting, authentication etc
- Search Service to handle all user searches
- Event CRUD Service to create and edit events
- Booking Service to handle ticket reserve & confirmation workflow
- Redis Database connected to the Booking Service to store the tickets that have been reserved, but havent completed the confirmation workflow
- Postgres Database to store core entities

## Database DDL

- Events - id, tickets[], venueId, performerId, eventDate, eventDescription
- EventTickets - id, eventId, seatId, price, status
- Performers - id, ...
- Users - id, email
- Venues - id, location, seatMap
- Assume createdAt, modifiedAt timestamps are on all tables

## Deep Dives

- Implement Elasicsearch and setup CDC to enable faster text search for events w/ the Search Service
- Implement a CDN in front of the API Gateway - this would typically support hot events and searches
  - This would improve search latency if you had a lot of simple, repeatable queries, but not as useful if you have a lot of permutations for your search queries
- Implement a virtual waiting queue for hot events like Taylor Swift concerts
- Can implement another Redis Database for the Event CRUD Service so we're always reading from the warm cache
  - If we ever update event details in Postgres then invalidate the cache, pull from Postgres, and update the Cache afterwards
- Asynchronous booking confirmation notifications to reduce user-facing latency
  - If you have 50,000 people who just bought tickets and your notification service is slow, you don't want that impacting the user experience

## Napkin Math

- 100 M Users
- 10 M DAU
- Peak usage - 500,000 Users
- Search Queries per Second - 50 million total per day divided by 86,400 seconds = 580 QPS
- Booking - 100k bookings per day divided by 86,400 seconds = 11 QPS
- Hot events - could have up to a million users trying to book tickets for a single event in a 5 minute window
  - ~3,000 QPS for booking reserve and confirmation steps
  - Search would be even higher
