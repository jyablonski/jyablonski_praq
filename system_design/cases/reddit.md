# Template

## Core Requirements

- Users should be able to join specific communities called subreddits and make posts
- Users should be able to make comments on posts
- Users should be able to reply to other people's comments on posts
- Users should be able to upvote / downvote posts, as well as comments on posts

## Non-functional Requirements

- System should scale to 10 million DAU
- Post/comment creation latency: <500ms (p95)
- Feed/post view latency: <200ms (p95)
- Upvotes/downvotes: eventual consistency acceptable (~1-5 sec delay)
- System availability: 99.9% uptime
- Data durability: no vote/post/comment loss

## Out of Scope

- Search
- Images / external Links on posts
- Reddit Awards
- Moderator actions
- Content reporting / moderation
- Any other UI / UX stuff

## Core Entities

- Subreddits
- Posts
- Comments
- Upvotes / Downvotes

## API

### Subscriptions

- POST /subreddits/:subredditId/members
- DELETE /subreddits/:subredditId/members/:userId

### Posts

- POST /subreddits/:subredditId/posts { title, content }
- GET /subreddits/:subredditId/posts?page=1&limit=25&sort=hot
- GET /posts/:postId
- DELETE /posts/:postId

### Comments

- POST /posts/:postId/comments { text, parentCommentId? }
- GET /posts/:postId/comments?sort=top&limit=50
- DELETE /comments/:commentId

### Votes

- POST /posts/:postId/votes { value: 1 or -1 }
- POST /comments/:commentId/votes { value: 1 or -1 }
- DELETE /posts/:postId/votes (to remove vote)
- DELETE /comments/:commentId/votes

### User Feed

- GET /users/:userId/feed?page=1&limit=25

## High Level Design (to satisfy functional requirements)

- CDN for content caching at the edge
- API Gateway for auth, rate limiting, routing etc
- Write Service to handle all incoming Post / Comment write requests, publishes to Queue
- Read Service to handle all incoming read requests, reads from cache/replicas
- Vote Service to handle all incoming vote requests, works directly w/ Kafka and Postgres
- Kafka for async processing of votes and updating total post/comment counts in batches.
- Postgres for primary backend database for everything
- Redis to serve as caching layer (hot posts, subreddit feeds, vote counts)

## Key Flows

Key Flows:

1. Write: API -> Write Service -> Postgres
2. Read: API -> Read Service -> Redis (cache hit)
   -> Postgres replica (cache miss) -> cache -> return
3. Vote: API -> Vote Service -> then in parallel:
   - -> Postgres (write individual vote row)
   - -> Kafka
   - Then aggregate results on a batch basis every 30 seconds - "post X got +47 votes, post Y got -12 votes"
   - Postgres Batch update `UPDATE posts SET score = score + 47 WHERE id = X` and update Redis cache

## Database DDL

- posts {id, subbreddit_id, name, score, created_at, modified_at}
  - INDEX on (subreddit_id, created_at) -- for subreddit feeds
  - INDEX on (subreddit_id, score) -- for hot/top sorting
- comments {id, post_id, user_id, content, score, parent_comment_id?, created_at, modified_at}
- subreddits (id, name, description, created_at)
- users {id, name, email, created_at}
- userSubscriptions (user_id, subreddit_id, created_at)
  - PRIMARY KEY (user_id, subreddit_id)
- votes (user_id, vote_type post/comment, vote_value, created_at)

## Deep Dives

- User Feed Generation (use simple sort queries to start, but eventually you want something more powerful)
- Scaling (move up to Cassandra)
- Vote processing

## Napkin Math

- 10 M DAU
- Assume 10% of them make posts - 1 M posts / day
  - 10^6 / 10^5 = 10 posts per second
- Assume 50 M comments per day
  - 5 \* 10^7 / 10^5 = 10^2 or 500 comments per second
- Assume 50 votes per user per day, or 500 M votes
  - 500,000,000
  - 5 \* 10^8 / 10^5 = 5 \* 10^3 or 5k votes per second
  - This is right at Postgres' limit to scale

## Best Practice Approach

Postgres (Strong Consistency):

- users (low write volume)
- subreddits (low write volume)
- subscriptions (moderate write)
- posts metadata (moderate write, need ACID)

Cassandra (High Throughput, Eventual Consistency):

- votes (extremely high write - 150K/sec)
- comments (very high write - 15K/sec)
- view_counts, analytics

Redis:

- Caching layer for everything
- Real-time score aggregation

Rationale:

- Postgres and Kafka can handle this scale up to 10 M DAU
- After that, you want to move more things out of Postgres and leverage something like Cassandra
