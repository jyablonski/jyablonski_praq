# Template

## Core Requirements

- Users should be able to follow other people & be followed
- Users should be able to post tweets
- Users should be able to read other people's tweets on a timeline

## Non-functional Requirements

- Users should have low latency for read and write events
- Reading tweets should be eventually consistent (it's fine if we have a small delay until people see new content)

## Out of Scope

- Videos / Media as part of the tweet; assume text only tweets for now
- All other fluff Twitter features
- Assume tweets cannot be edited, but can be deleted
- No location stuff

## Core Entities

- Tweets
- Follows
- Timeline

## API

All API operations are assume to have a JWT in the Headers from the logged-in user that we'll use for Auth to see who the request came from

- POST /tweets {text}
  - To post a tweet
- DELETE /tweets/:tweet_id
  - To delete a tweet
- DELETE /follows/:user_id
  - To unfollow somebody
- POST /follows {user_id_to_follow}
  - To follow another user
- GET /timeline
  - Query params: ?limit=50&cursor=xyz
  - To get your personal timeline and view tweets from other people
  - This doesnt need to be in the form of `/users/:user_id/timeline` because you'll never go get somebody else's timeline.
- GET /users/:user_id/tweets
  - Query params: ?limit=50&cursor=xyz
  - To get specific tweets for a user on their profile
- GET /tweets/:tweet_id
  - Get a single tweet
- GET /users/:user_id/followers
- GET/users/:user_id/following

## High Level Design (to satisfy functional requirements)

- CDN for serving static content + assets
- API Gateway for rate limiting, authentication, and routing
- Write Service to handle writing new events and saving them to the database
  - \*\* Improvement - can implement a message queue here for async fan-out writes after users publish tweets
  - So the write service would:
    - Write new tweets to Postgres and returns 201 to the client
    - Afterwards, write the tweet to the message queue
    - Fan out workers update follower timeline's in Redis based on the criteria above
- Read Service for simple, direct reads if a user is viewing somebody's profile etc.
  - Has different scaling needs than the timeline service, so separating them out seems appropriate
- Timeline Service to handle generating appropriate timelines for users (based on their follows etc)
  - Check Redis for timeline:{user_id}
  - If cache hit: fetch tweet details from Redis + Postgres, query celebrity profiles separately, merge and sort by timestamp and return top N tweets
  - If cache miss: query userSubscriptions for followers, separate into normal vs celebrity users, fetch tweets from both, merge, and return. Async backfill Redis cache afterwards
- Redis for storing User Timelines and for serving recently used content
  - LRU Cache eviction policy because recency matters, inactive users don't need timelines in memory, and the performance penalty for falling back to postgres is fine for these types of users
  - For timelines, use TTL so that timelines expire after 7 days
- Postgres as primary database backend

### Timeline Service

For normal users (< 10k followers):

- Fan-out on write: When posting, write tweet_id to all followers' timeline caches
- Pre-computed timelines in Redis sorted sets (sorted by timestamp)

For celebrities (> 10k followers):

- Fan-out on read: When user requests timeline, query the celebrity's tweets directly
- Mix pre-computed timeline with celebrity tweets at read time

Redis Timeline Storage:

- Key: timeline:{user_id}
- Structure: Sorted Set (ZSET)
- Score: tweet timestamp (for ordering)
- Value: tweet_id
- TTL: 7 days (keep recent tweets only)
- Max size: Top 1000 tweets per timeline

Why this works:

- O(log N) insert for fan-out writes
- O(log N) range queries for timeline reads
- Natural time-ordering
- Easy pagination with ZRANGE

## Database DDL

- users
  - user_id, email, password?, salt?, oauth_provider?, created_at, modified_at
- tweets
  - tweet_id, user_id, content, created_at
  - tweet_id is a UUID to avoid scalability or distributed system issues
  - Index on (user_id, created_at) for profile page queries
  - Index on (created_at) for recent tweets
- userSubscriptions
  - user_id, user_id_subscribed_to, created_at
  - user_id is the id of the user who followed somebody, `user_id_subscribed_to` is who they followed
  - PK on user_id and user_id_subscribed_to to ensure only 1 row for each combination here
  - Index on (user_id_subscribed_to) for fan-out writes

## Deep Dives

Celebrity User Detection:

- Threshold: 10k+ followers (configurable)

- Updated via nightly batch job that queries userSubscriptions

- Store in Redis SET: celebrity_users

- Check this set during fan-out decisions

- Trade-off: Celebrity tweets have slight read latency vs avoiding millions of fan-out writes

- Postgres scalability - at what point do we move off it for better scalability options from something like Cassandra or a NoSQL database

- Tweet archival - at some point you probably want to move data off the database and into long term storage in S3

### Fan Out

Fan-out = When one action triggers multiple subsequent actions

In Twitter's case: One person tweets -> that tweet must appear in many people's timelines

- If you have a celebrity with 150 million followers tweet, that tweet has to show up in the timeline of 150 million followers. How do you do that?

2 Approaches: Fan out on Write (Push Model) and Fan out on Read (Pull model).

- Twitter uses a hybrid strategy where they do the push model for people w/ low amounts of followers, and the pull model for the celebrities

#### Fan Out on Writer

When a user tweets, immediately write that tweet to all of their followers' timelines.

Alice posts: "Hello world!"
Alice has 3 followers: Bob, Charlie, David

System immediately does:

1. Write tweet to Postgres
1. Add tweet to Bob's timeline in Redis
1. Add tweet to Charlie's timeline in Redis
1. Add tweet to David's timeline in Redis

Now when Bob/Charlie/David open Twitter, their timeline is already pre-computed and ready to serve from Redis.

```sh
ZADD timeline:bob {timestamp} {tweet_id_123}
ZADD timeline:charlie {timestamp} {tweet_id_123}
ZADD timeline:david {timestamp} {tweet_id_123}
```

This enables fast reads and is relatively simple, but slow for write operations. You must update all follower timelines, and this doesn't scale for people w/ large amounts of followers

#### Fan Out on Read

When a user tweets, just save it. When someone requests their timeline, fetch tweets from all the people they follow on-demand.

Alice posts: "Hello world!"
System does:

1. Write tweet to Postgres
1. Done! (no fan-out)

Later, Bob opens Twitter. The System does:

1. Query: "Who does Bob follow?" → [Alice, Eve, Frank]
1. Query: "Get recent tweets from Alice, Eve, Frank"
1. Merge and sort by timestamp
1. Return timeline to Bob

```sql
SELECT t.* FROM tweets t
JOIN userSubscriptions s ON t.user_id = s.user_id_subscribed_to
WHERE s.user_id = 'bob'
ORDER BY t.created_at DESC
LIMIT 50;
```

This leads to slower reads, but scales better for those hot users w/ millions of followers.

## Napkin Math

- 10 M DAU
- Assume 5 tweets a day, for 50 M tweets per day
  - 5 * 10^7 / 10^5 = 500 tweets writes / second
  - Assume 30% higher during peak load, so this could be up to 650 tweets / second
  - Postgres is still fine here
- Assume 100 read events a day, for 1 B reads
  - 10^9 / 10^5 = 10,000 read events per second
- Assume 30% higher during peak load, so this could be up to 13,000 reads / second
  - We definitely need caching and a separate service to handle this

Storage per tweet: ~500 bytes (text + metadata)
50M tweets/day × 500 bytes = 25 GB/day = 9 TB/year

### Redis timeline storage:

- 10M users × 1000 tweets × 8 bytes (tweet_id) = 80 GB
- With overhead + hot tweet cache: ~150 GB Redis needed

### Postgres:

- Year 1: ~10 TB
- Need partitioning strategy by created_at (monthly partitions)

Average user has 200 followers
500 tweets/sec × 200 followers = 100k Redis writes/sec
Peak: 650 × 200 = 130k writes/sec

Redis can handle 100k+ writes/sec, but need:

- Redis cluster (sharded by user_id)
- Multiple fan-out workers (horizontal scaling)
