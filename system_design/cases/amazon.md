# Template

## Core Requirements

- Company should be able to place products up for sale
- Users should be able to search for items
- Users should be able to purchase items that will be delivered

## Non-functional Requirements

- Adding items to cart should be eventually consistent
- Submitting orders should be strongly consistent
- Search should be low latency (< 500 ms)

## Out of Scope

- Delivery process
- Vendors putting listings up
- Reviews

## Core Entities

- Users
- Products
- Orders

## API

Assume JWT is handling authentication and every request will be signed with it to identify the user

- GET /products?search={search}&category?={category}&page={page}&limit={limit}&sort={price_asc,price_desc,popularity}
- GET /products/:product_id
- POST /cart/items { product_id, quantity}
- PUT /cart/items/:product_id {quantity}
- DELETE /cart/items/:product_id
- GET /cart
- POST /orders
  - Body: {
    cart_items: [
    { product_id, quantity, price_at_add_to_cart }
    ]
    }
- GET /orders [] orders

Best practice is to use cart_item_id here incase you add 2 of the same product w/ different colors or something. I didn't do this here though because I didn't know.

## High Level Design (to satisfy functional requirements)

- CDN to cache static content
- API Gateway for Load Balancing, routing, authentication
- Read Service to handle all searches and product viewing information, connects directly to databases to serve content
- Write Service to handle all add-to-carts and order submissions
  - Utilizes Redis to manage adding items to carts so we can satisfy our eventual consistency requirement, and to keep the cart up-to-date incase inventory account drops to display warnings to user or lock the order submission entirely if inventory count drops to 0.
  - Utilizes Database lock w/ Postgres to check inventory counts, decrement them, and update Redis carts in 1 go to avoid race conditions incase 2 users are trying to purchase the last item of something.
- Stripe for Payment Flow (assume they manage taking user payment information, verification, we jsut get a simple confirm / fail)
- Postgres for storing products, orders, content, inventory etc
  - Can setup PostGIS as well for potentially other SQL type geospatial queries in addition to Elasticsearch, but Elasticsearch is what will primarily serve the frontend.
- Elasticsearch for fast text-search, autocompletion etc
- CDC process to take recent data in Postgres, read off the WAL, and get it over into Elasticsearch
  - Assume for sake of time that this Debezium & Kafka and we're using an Elasticsearch Sink for this purpose
- Redis for caching popular products or recent searches
- Redis for storing user's carts
  - Assume we clear out this data after x cadence of inactivity (maybe 1 or 7 days)

## Database DDL

- users
  - ignoring ddl for sake of time
- products
  - id, price, name, description, vendor, category, created_at, modified_at
- orders
  - id, user_id, is_cancelled, created_at
  - index on (user_id, created_at)
- cart_items
  - id, user_id, product_id, quantity, price_snapshot, created_at, modified_at
- order_details
  - id, order_id, user_id, product_id, created_at
  - index on order_id
  - index on (user_id, created_at)
- inventory
  - Stores inventory counts for every product
  - Stored separately for performance so
  - product_id, inventory_count, created_at
- price_history
  - id, product_id, old_price, new_price, created_at, modified_at

```
carts (in Redis)
- user_id (key)
- items: [
    {
      product_id,
      quantity,
      price_snapshot,  // Price when added
      added_at
    }
  ]
- updated_at
- expires_at
```

## Deep Dives

- Inventory management / count
- Updating Carts in Redis (idk the exact Redis-features we could utilize here)
- User -> Cart -> Order flow, can this be improved

## Napkin Math

- Assume 10 million DAU
- Assume 100 million searches total
  - 100,000,000 or 10^8 / 10^5 = 1000 searches per second, peak 3x or 3000 per second
  - Can be handled by Elasticsearch and Redis
- Assume 5 million purchases
  - 5,000,000 or 5 \* 10^6 / 10^5 = 50 purchases per second, peak 3x or 150 per second
  - Can be handled by Postgres

## What I Missed

Order flow was way too simple (Which makes sense - i don't do this fucking shit). Better flow is:

Saga Pattern

1. Reserve inventory (set status: RESERVED)
2. Create pending order
3. Call Stripe (async)
4. On success: Commit reservation -> SOLD
5. On failure: Release reservation -> AVAILABLE

- The idea here is you're doing it asynchronously and/or with webhooks so you have a proper flow of user submits order -> pending payment -> payment_confirmed / payment_failed / payment_cancelled -> inventory released back

Reddis Carts:

- `HSET cart:{user_id}:items` {product_id} {quantity}
- `EXPIRE cart:{user_id}:items` 604800 # 7 days

Elasticsearch was way too generalized. Elasticsearch Index Structure should look like:

- products
  - id (keyword)
  - name (text, edge_ngram for autocomplete)
  - description (text)
  - category (keyword, for faceting)
  - price (double, for range filters)
  - inventory_count (integer)
  - popularity_score (double, for ranking)
  - created_at (date)

Can also use Postgres w/ GIN Indexes for text search, this is fine until interviewer's start pushing for better performance or lower latency.

Implement Price history table for analytics and auditing. You should never refer to current product price for historical transactions.
