## Bitly

[Video](https://www.youtube.com/watch?v=iUU4O1sWtJA)
[Guide](https://www.hellointerview.com/learn/system-design/answer-keys/ticketmaster)


Core Requirements

- Users should be able to create Short URLs from a given Long URL
  - Optionally support custom URL Aliases
  - Optionally support an Expiration Time for the Short URL
- Users should be able to redirect to the original URL from the short one


Non-functional Requirements

- Service should have low latency on redirects (~200 ms)
- Service should scale to 100 million daily active users and 1 Billion URLs
- Service should guarantee uniqueness of Short URLs


Core Entities

- Original URL
- Short URL
- User creating the short URLs


API

``` sh
# shorten URL
POST /urls -> shortURL
{
  originalURL,
  alias?,
  expirationTime?
}

# redirection
GET /{shortURL} -> redirectToOriginal
```


High Level Design (that satisifes the Functional Requirements)

- Client can make `shortURL()` requests and receive a response
- Primary Service can accept requests from the client, read from a backend Database, and deliver the response
  - Response should be a 302 redirect
- Backend Database (Postgres) can be used to store data in a table with:
  - shortUrl
  - userId
  - longUrl
  - created_at

Database should have an index on `shortUrl` if it's not already the Primary Key (primary keys are indexed by default) for improved query performance

- This will slow down inserts updates and deletes, but improve read performance which is still ideal

Can handle the long -> short URL in a couple of ways:

1. Can generate a random x digit number, base64 encode it, and get some random short-character string and store it in the database so it deterministically always points back to that long url.
2. Can has the long url, base64 encode it, and grab the first 6 characters of it.
   1. Both of these can run into collisions. This requires you to check the database if the random value already exists for a short url yet before you store it in the database, and if it does then you try again.


Deep Dives (to handle edge cases, critical performance implications, improvements to the system that can be made)

- Can introduce Redis to sit in between Postgres + the Backend Service and cache any recently queried URLs
  - Use Least Recently Used (LRU) policy to remove cache on any URLs not being used recently
  - Key = short URL, value = long URL
- Probably way more Read Usage on this type of Application than Write
  - Lot more users using the short URLs than users that are creating long -> short URLs
- Can separate Backend Service out into a Read Microservice and a Write Microservice
  - Can horizontally scale them both out as needed
  - Maybe you need 25 Read Services spun up to handle peak traffic, and only 2 Write Services
  - Write Service only needs to connect to Postgres
  - Read Service only needs to connect to Redis
  - This is probably overkill but it's still an option
- Can create a Global Counter Redis database to keep track of how many short URLs have been created
  - Can deterministically create hashes based off a monotonically increasing number like this via functions like sqids.org

Napkin Math

- 10 ^ 8 = 100 million users
- 10 ^ 5 = 100k ~ (86k seconds in a day)
- This means about 10 ^ 3 or 1000 transactions per second
- Probably have peaks and valleys, peaks can go up to 10k or 100k transactions per second
- t3.medium EC2 instance can handle about 1000 transactions per second
- To handle the peaks, we have to scale horizontally
