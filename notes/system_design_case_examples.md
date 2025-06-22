# Design a System for Data Ingestion from an API

1. Business / Product Use Case + Requirements Gathering
   1. What's this data for?  Who needs it?  Who are the stakeholders gonna be for it?
      1. Maybe I'm just ingesting it for another Software Engineering Team to use it and have some business function for it
   2. Having some idea about how that all flows together is necessary here
   3. Project Timeline ?
   4. Budget for the System / Pipeline ?
2. What SLAs are we thinking about for it
   1. Does all data need to be ingested by some certain time in the morning ?
   2. Daily / Hourly / Real Time ?
3. Figure out how the API offers data scrapes
   1. For full backfills are various endpoints paginated so I can loop through by something like a page number or offset myself?
   2. For incremental runs can I query endpoints and pass in a date or timestamp to filter results by ?
4. Figure out what Endpoints can be scraped from the API
5. Develop a script that pulls data from each endpoint that is required
   1. Add in functionality to do backfills or incremental runs, maybe use an environment variable called `run_type` to determine this
   2. You'd have to see what the performance is like, maybe you'd need `asyncio` to really push the performance and speed of the script to meet your SLA.  Or maybe that's not necessary
   3. Might be able to use a 3rd Party Package that's already been built for the API. otherwise, will likely need to build your own in-house tooling.  Often a OOP approach is preferred here so you only have to setup credentials once to the REST API and then you can put all the scrape methods onto that same class.
6. Loop through the endpoints and write data out to S3 as the script pulls data.
   1. To avoid OOM issues you can either have the script write data out in chunks for each endpoint, or if the data is small enough you can just write 1 file out for each endpoint
   2. Parquet, CSV, or JSON can all work here in theory.
   3. Data from the REST API is returned as JSON but you could pull it into memory, get it into a Pandas or Polars DataFrame structure, then write it out to S3 as a Parquet.  Or you can go straight from python dictionary -> json.dumps to S3.
7. Package your dependencies up in a tool like poetry
8. Create a docker image of your script + dependencies
9. Run the docker image in a container on ECS that is scheduled & orchestrated by Airflow
   1.  Airflow can pass in environment variables to the ECS task
10. Follow up Task could load data from S3 into Database / Data Warehouse
11. Assess API Data Quality
   1. Keep track of primary keys, modified timestamps, duplicates, nulls etc things like that.
   2. If it's really bad you may wanna invest dev time into building a lot of checks and data quality tests.
   3. If it's pretty good then maybe you can be more lenient at this step.
   4. Also depends if you're paying for this API or if it's free; you might have dedicated support you can reach out to to help you debug the issue, or maybe you're on your own
   5. Ultimately you need to start ingesting it and having a look at the data yourself to know for sure
12. Add Various logging into the Script, write errors out to Slack and/or trigger PagerDuty Alerts if the Script is unable to pull what it needs
13. Write Unit + Integration Tests and mock out any HTTP Network Calls and AWS / S3 API Calls

IMPORTANT STOPPING POINT
1. From here the rest of the steps depend on what the goal is.
2. You could perform dimensional data modeling to turn that raw source data into fact / dim tables and eventually aggregate it up or transform it as needed.

Let's say you encounter a Spark pipeline performing poorly, how do you go about identifying the issues and optimizing?
How do you manage the complexity of a pipeline with tons of transformations?
How do you go about testing this pipeline?


# High Level Concepts

Storage is typically measured in:
- **Kilobytes (KB):** 1 KB = 1024 bytes
- **Megabytes (MB):** 1 MB = 1024 KB
- **Gigabytes (GB):** 1 GB = 1024 MB
- **Terabytes (TB):** 1 TB = 1024 GB


## Uber

[Video](https://www.youtube.com/watch?v=lsKU38RKQSo)
[Guide](https://www.hellointerview.com/learn/system-design/answer-keys/uber)

Goal of System Design is to move quickly and build out the core features of the system. Be able to identify what are core features and what are nice-to-haves that you probably don't need to dive in detail during a system design interview

- When Uber was built, they obviously didn't offer all the features that they now offer in 2024.

Functional Requirements:

- Riders should be able to input their current location and desired destination to get an estimate cost to get driven somewhere
- Riders should be able to request a ride and get matched with a nearby driver
- Drivers should be able to accept rider request & navigate to their location and destination

Non-functional Requirements:

- System should be low latency (< 1 minute to match, and if it passes 1 minute then maybe there's no drivers in the area)
- System should ensure strong consistency so drivers don't get matched with multiple rides simultaneously (1 - 1 match for rider + driver)
- System should be reliable and available 24/7
- System should be able to handle high throughput, surges during peak hours like 7-10pm or around Events like sports games or concerts

Out of Scope (User Features + Backend Infra):

- Riders + Drivers rating each other post-ride
- Riders scheduling rides in advance
- Riders requesting different categories (XL, Comfort etc)
- CI / CD Pipelines
- Monitoring + Logging Systems

Core Entities are more valuable than a data schema because we don't know 100% of the columns or tables that we need yet at this stage. But, we do know the general core objects that we'll absolutely need.

- Rider - any User using the Platform to make Ride Requests
- Driver - any User registered as a Driver on the Platform
- Ride Requests - all Requests being made from the moment a Rider requests an estimated fare til its completion
- Driver Location Status - Real Time location of drivers, lat / long coordinates and timestamp of last update


API 

1. Fare Estimate
   1. Endpoint for when Users request a price estimate for a ride. 
   2. Takes a pickup and destination location
   3. `POST /fare-estimates` {pickupLocation, destination}`
   4. Returns {ride_id, estimated_price, estimated_pickup_time}
2. Ride Request
   1. Endpoint for when Users request a ride. 
   2. Takes a Ride ID returned from the Fare Estimate
   3. `PATCH /rides/:rideId`, passing in the ride_id returned from the Fare Estimate
   4. Patch because we might edit the Fare Estimate row and turn it from `is_booked` from false to true or something
3. Driver Location Update Request
   1. Endpoint that is continuously called by Drivers on the clock to get their location update. 
   2. Takes a Lat Long
   3. `POST /drivers/:driverId/location` {latitude, longitude}
   - Better to make this per-driver (/drivers/:id/location) to avoid needing to pull it from auth headers.
4. Driver Accept Ride Request
   1. Endpoint that allows Drivers to accept or deny a ride request.
   2. Takes a Ride ID and a true / false value for yes or no
   3. If accepted, returns Lat / Long coordinates for pickup.
   4. `POST /rides/:rideId/acceptance` {accepted: true}
   - Backend extracts driverId from the authenticated user (JWT, session).
5. Update Ride Status 
   1. Endpoint that updates Ride Status for a specific Ride ID
   2. Status -> "picked_up_rider" | "completed"
   3. `PATCH /rides/:rideId/status` {status: picked_up_rider}
   - Potential Status values: "requested" → "accepted" → "picked_up_rider" → "completed"


High Level Design

- Riders make requests on iOS + Android Devices to a single AWS Managed API Gateway
  - The Gateway enables Load Balancing, Routing, Authentication, SSL Termination, and Rate Limiting
- Ride Service (microservice) - handles Fare Estimation
  - This microservice might hit some 3rd party service to view traffic in the area and adjust the fare estimate accordingly
  - Afterwards, this estimate gets stored in an OLTP Database to store the estimate permanently
  - `ride` table: id, rider_id, estimated_fare, eta, source, destination, status Columns
  - `rider` table: id, other metadata + payment info etc ... (not that important for this system design)
- Ride Matching Service (microservice)
  - Separate Service because it's different than the Ride Estimate Service.
  - Enables a separate team to own implementation of this aspect of the system
  - Allows scaling separately as well.
  - Uses a complex algorithm to match requests to best available drivers based on a number of factors like proximity, availability, driver rating etc.
  - Talks to the Ride Service microservice to get the status of a specific Ride
- Location Service + Database that manages storing real-time location of all drivers
  - Drivers will automatically make location updates every n seconds (< 30) to update their location.
- Notification Service (native mobile push notifications)
  - Driver will be prompted with a push notification if they want to accept a ride request


Deep Dive

1. Uber has ~6 million drivers, assuming ~3 million drivers are active at any given time, and the Location Service updates location every 5 seconds, then there's potentially 3 million / 5 = 600k request per second of load on this Service.
  - You can further optimize this down from 600k though by doing more dynamic updates. 
  - You dont need to get driver updates for rides in progress, because that driver is already servicing a ride and in route.
  - If the driver updates havent changed in ~20 minutes (like they're parked someplace), then maybe start exponential backoff of the updates for that driver.
  - If they're in the boonies then dont update at a high frequency because we dont need that precision. But if they're in NYC then you probably still need high frequency location updates
2. Location Database + Service
  - Postgres is a bad solution to implement the Location Database. 2-4k transactions per second is fine, 600k is not.
  - Even if you used `postgis` and a geospatial index, the amount of writes and having to re-update the index everytime would make this a not efficient solution for Uber-level scale
  - Quadtree for geospatial data are great when you have areas of high density (like NYC) and other areas where you dont give a shit about (the atlantic ocean) and where it doesnt have a high frequency of updates. This makes it great for something like Yelp + reviews, less so for something real time like Uber
  - but, if you had 1/1000 of the scale then this might be a fine solution
  - Redis can handle anywhere from 100k - 1 million requests per second
  - Redis supports geohashing to do geospatial queries, which is fast efficient and a good solution for this problem
  - Geohashing is indiscriminate to density, but great for high frequency of writes
3. Ride Matching Service
  - Don't send out more than 1 request at a time for a given ride. Send a request out to a driver, wait 15-20 seconds, if they dont answer then move on to next driver etc.
    - The Ride Match Service might have dozens of servers running at a single time if it's horizontally scaled.
    - One option is to introduce an additional status field that can be managed in a database that records whether a driver has a pending request available to them or not. That way, we avoid a driver getting pinged with multiple ride requests at the same time.
    - I think you could just make it so if the driver responds with yes or no then record that appropriately.  If the driver doesn't respond then set the status to declined.
    - Could also make a lock service that hooks up to the ride matching service so that when a request is sent to a driver there's a lock placed on them so they cant take more requests until they provide an answer
    - Another Redis database could be used here to implement this lock service.
  - Don't send any driver more than 1 request at a time
4. Handling High Throughput
  - Introduce a Queue to match Riders to Drivers during surges with high traffic and request volume.
  - It might feel bad from the customer perspective to wait x minutes to be served by a driver, but ultimately if you don't have enough available drivers then a queue is just about as good as you can do in this situation.
  - First in, first out queue. Partitioned by location (heavy traffic in Atlanta, no traffic in the boonies etc).


## Ticketmaster

[Video](https://www.youtube.com/watch?v=fhdPyoO6aXI&t=3056s)
[Guide](https://www.hellointerview.com/learn/system-design/answer-keys/ticketmaster)
![image](https://github.com/user-attachments/assets/6fed1e04-87e4-410c-8c04-6667b084ac22)


Core Requirements

- App should provide Events that Users can view and book tickets for.
- Users should be able to book tickets for a particular Event
- Users should be able to search for events

Non-functional Requirements

- Booking tickets should be highly consistent (don't book 2 customers the same seat etc)
- Want high availability for search and viewing events
  - Different components in any system prefer consistency or availability for various reasons, it's not some general "ticketmaster should prioritize consistency"
- App should be able to handle surges of high traffic
- Lot more search events than booking or buying events
- Booking is actually a 2-phase process. When you click your seat, it's reserved for a short time while you go through the checkout process. So you first reserve a seat and it's temporarily locked to you for a small time window, and then once you pay it's actually confirmed and locked in.

Core Entities

- Event
- Ticket
- Performer
- Venue

Important not to map out the schema at this point. You may not know all of the fields yet, and it may evolve as you get into the high level design. Put the schema in the high level design when you map out the database. And that way you can add onto it as you build out that architecture.

Also don't implement any napkin math if you don't have a purpose for it yet. Do it only if your napkin math estimations will have a direct influence on how you'll design or architect your solution.

API

- `GET /event/:eventId -> Event & Venue & Performer & Ticket[]`
- `GET /search?term={term}&location={location}&type={type}&date={date} ...` -> Partial<Event>[]
  - term - generic search term
  - location - location for the event. could be city, could be lat / long. depends
  - type - sporting event, concert etc
  - date - date of the event
  - `Partial<Event>[]` - return a limited amount of info for the event to show the search results
- `POST /booking/reserve`
  - Header: JWT | SessionToken
  - Body: {ticketId}
- `POST /booking/confirm`
  - Header: JWT | SessionToken
  - Body: {ticketId, paymentDetails (Stripe)}

High Level Design (that satisifes the Functional Requirements)

- Users will make requests from their client (Mobile Device, Web Browser) to an API Gateway which will forward along their request to the appropriate service
  - The Gateway enables Load Balancing, Routing, Authentication, SSL Termination, and Rate Limiting
- Event CRUD Service which will take requests and read + write to some OLTP Database
  - Database will store all the Core Entities that were mentioned previously
  - One-to-many relationship between event and tickets.
  - Because of these relationships, OLTP is typically fine
- Search Service which will take search requests and return list of results based on user search
  - Initially, start out by just having it query the OLTP Database for search. This will be super slow and is not gonna cut it, but for now just finish mapping out the rest of the architecture and come back to it.
- Booking Service which will handle the 2-phase booking process.
  - On Reserve, it will update the `status` column in the `ticket`  table to `reserved`.
    - Issue with this is after ~10 minute temporary hold, it will stay reserved forever.
    - Could use a CRON job to run updates to these that run every minute or something. But this introduces a delta time where a seat would become available again, but the CRON job just hasnt ran again. This is valuable time that a ticket could have been booked but isnt available to users. 
    - Could also add additional `reserve_timestamp` column to track that. But this adds a ton of complexity
    - Can use Redis to implement a Ticket Temporary Lock where it will keep track of it via a TTL. After 10 mins where the user reserved the ticket but didn't purchase, then it will be removed from Redis and new searches will immediately show the seat available again.
      - This changes the Event CRUD Service, which will now have to query Postgres and Redis now to check that it's not reserving the same seat to 2 users.
      - Separated out into its own Service because the Booking Service might have 50+ servers running in parallel; they all need access to the same information. Can't keep this in the Booking Service Worker memory.
  - On Confirm, it will take in some payment details so you can make API Calls to Stripe to take the user's payment info and charge them.
    - If successful payment, it will update the `status` column to `booked`
    - If failed payment, it will

Deep Dives (to handle edge cases, critical performance implications, improvements to the system that can be made)

- Find 1-3 places where you can significantly improve the system and solve the non-functional requirements.
- Search can be improved, use a CDC Solution to move data from Postgres to Elasticsearch so it has all the recent data available, but offers a much faster low-latency search solution for users.
- How to deal with Hot data (taylor swift concerts) - implement caching. This would work really well because the experience is the exact same user-to-user, we're not implementing any user-specific recommendations or anything that might change and not be great for cache.
  - Opensearch has node query caching which caches the top queries
  - Could add another Redis database here to cache the search term <-> search results
  - CDN can cache API calls for search, so can utilize that as well. Super fast, great for popular events. But less useful if you have a ton of different search queries with a lot of parameters.
- Could improve Seat Map process to update in real time.
  - Implement Long Polling where for 30-60 seconds it keeps an open connection and continually updates
  - If they sit on this page for >= 10 mins, this isnt a great solution.
  - Websockets are an option.
  - This is above my paygrade, im tapping out on this one
- For Superbowl or Taylor swift, you need to introduce a Queue service to the booking flow.
  - Virtual Waiting Queue could be only enabled for really popular events.
  - Instead of seeing the Event Page, they're entered into a Queue and they have to wait for their turn to view seats and book a ticket.
  - Queue could be Redis sorted set, could be random etc. Depends.
  - Event driven logic to allow chunks of 100 people in at a time or something.

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

## Whatsapp

[Video](https://www.youtube.com/watch?v=cr6p0n0N-VA)
[Guide](https://www.hellointerview.com/learn/system-design/deep-dives/realtime-updates)


Core Requirements

- Users should be able to start chats with 1 or more users
- Users should be able to send & receive messages & media
- Users should be able to access messages after they've been offline


Non-functional Requirements

- Service should deliver messages with a medium amount of latency (~500 ms)
- Service should scale to 1+ Billion Users, which requires high throughput
- Messages from users should not be stored unnecessarily, for liability and PII reasons
- All systems should be fault tolerant; 1 part of the system failing shouldn't cause everything to go down

Out of Scope

- Things like Audio / Video Calling


Core Entities

- Users
- Chats
- Messages
- Client / Device Tracking


API

- Create Chat userId, targetUserIds []
- Create Message userId, targetChatId, message
- Create Attachment
- Modify Participants (on Chat)

- New Message Notifications
- Chat Updates

RESTful API may not make as much sense here as opposed to using Websockets to ferry messages back & forth. There's no real great way of outlining these Websocket API commands, so just doing high level for now. 


High Level Design (that satisifes the Functional Requirements)

- Client which makes connections to a Chat Server
- Chat Server that communicates with Clients and a Backend Database (such as DynamoDB or Postgres)
  - The Chat Server establishes WebSocket connections with Clients and manages these connections by tracking active ones and ensuring availability for new user connections.
- DynamoDB
- Can also utilize Blob Storage like S3 to store large attachments like videos or bulk photo upload
  - Pre-signed URLs are URLs with embedded authentication and a time-to-live (TTL).
  - When a client needs to upload large media, the Chat Server processes the request and generates a pre-signed URL from S3, which it returns to the client. The client then uses this URL to upload the media directly to S3.
  - After the upload, the client can send a message in the chat containing the URL of the uploaded media. This allows other participants to access the attachment or data directly if needed.

Database DDL

- Chat Table - id, name, metadata cols
- Chat Participant Table - chatId, participantId
- Messages Table - id, contents, creatorId, timestamp
- Inbox Table - recipientId, messageId
  - This can be used to provide notifications to users of new chats they haven't read yet.
  - Once they've read them, remove them from the Inbox Table


Deep Dives (to handle edge cases, critical performance implications, improvements to the system that can be made)

- Horizontally Scale the Chat Service
- Add a Load Balancer between the Client and your Chat Server(s).
  - WebSocket connections differ from traditional HTTP requests because they are stateful and persistent, rather than stateless.
  - A Layer 4 Load Balancer is used to maintain the connection between the Client, the Load Balancer (LB), and the Chat Server, ensuring the WebSocket connection stays active.
- Add a Redis Pub/Sub setup for Chat Server to help reach that non-functional requirement of < 500 ms real time delivery of messages
  - When a client sends a chat message, the Chat Server publishes the message to a Redis channel. The message is immediately made available to any subscribers of that channel.
  - Each Chat Server instance subscribes to the relevant Redis channels for the clients its serving
  - When a new message is published to a channel, Redis pushes it directly to all subscribed Chat Servers.
  - The subscribing Chat Servers then forward the message to the connected clients over their respective WebSocket connections. Since the message is handled in-memory by Redis, the process is extremely fast, ensuring minimal latency.
- Add a new Cleanup Microservice which deletes records out of inboxes + messages tables in DynamoDB


Napkin Math

- 1 Billion DAU
- 100 messages / day per user, so 100 Billion messages per day (10^11 KB / day)
  - 10^11 KB / 10^3 = 10^8 MB
  - 10^8 MB / 10^3 = 10^5 GB
  - 10^5 GB / 10^3 = 10^2 TB or 100 TB / day
- 10^5 Seconds in a day
- So about 10^6 Messages or 1 million per second, with peaks and valleys beyond that.


## YouTube


Core Requirements

- Users should be able to upload videos
- Users should be able to watch videos
- Users should be able to subscribe to other users to view their videos


Non-functional Requirements

- Service should support international users
- Video size should be limited to 1 GB

Out of Scope

- YouTube Live Streaming


Core Entities

- Users
- Videos
- Video Metadata
- Subscriptions
- Client / Device Tracking


API

- POST /videos {videoBytes, videoMetadata}                 # upload a new video
- GET /videos/:videoId -> videoBytes, videoMetadata        # watch a new video
- POST /users/:userId/subscriptions -> {subscribeToUserId} # new subscription
- GET /users/:userId/subscriptions -> subscribedUserIds [] # get subscriptions

High Level Design (that satisifes the Functional Requirements)

- Use S3 to host all original video content being uploaded
- Utilize Backend API Servers to handle incoming requests for video upload. Ensure they're stateless so we can horizontally scale
- Utilize Load Balancer to distribute incoming traffic equally among API Servers
- Use Postgres to store metadata about the videos being stored, user IDs, Subscriptions etc
- Use Redis as an additional layer between the API Servers & Postgres to cache video metadata and user objects
- Setup a Transcoding Service which converts the original video format to other formats to provide the best possible stream for different devices + bandwidth capabilities
- Use S3 to store these transcoded videos
- Utilize a queueing service to transcode all original video content 1 by 1
- Use CDN to serve videos to users

Database DDL

- videos
  - id, userId, video_title, video_description, s3_key, file_size, format, createdAt
- users
  - userId, email, createdAt
- userSubscriptions
  - id PK, subscriberId, subscribedToId
  - 1 row for every subscription in the system 


Deep Dives (to handle edge cases, critical performance implications, improvements to the system that can be made)

- To ensure users watch high-quality videos while maintaining smooth playback, it is a good idea to deliver higher resolution video to users who have high network bandwidth and lower resolution video to users who have low bandwidth.
- Video quality should automatically change depending on the network conditions to ensure a smooth user experience and minimal buffering.
- Place upload centers at specific geographical regions so users around the globe upload videos to these upload centers and have reduced latency.
- Message queues make the system more loosely coupled to improve efficiency and reduce bottlenecks
- To reduce CDN costs, you can identify popular videos and only cache those on the CDN, and serve all other videos from an interal video server
- Less popular content that is also short might just be able to be encoded on demand
- Some videos might only be popular in certain regions, so you don't nmeed to distribute them to other regions at all
- Build your own CDN like Netflix, but this is a massive undertaking
- build a chunker service to take a completed large file from a user from multi-part upload in s3, and build 2-10 second video clips of it that are stored back to S3. Then when users go to watch videos on youtube, we can immediately serve them content at a much faster pace by incrementally pulling & serving those chunks 1 at a time, as opposed to pulling an entire 5 GB video at once.
  - this chunking process is what enables your low latency non-functional requirements so videos can start playing for users much faster



Napkin Math

- 5 million daily active users DAU
- Average user watches ~ 5 videos per day
  - 25 million videos being watched
- 10% of users upload 1 video per day
  - 500k videos uploaded per day
- Average video size is 300 MB
  - 500k * 300 MB is 150,000,000 MB or 150k GB or 150 TB per day
- CDN Cloudfront charges $0.02 per GB
  - 5 million users * 5 videos * 0.3 GB * 0.02 = $150,000 per day in CDN costs

# Yelp


Core Requirements

- Companies should be able to claim & edit various information about their business
  - Basic information like business name, address, owner
- Users should be able to search for businesses in a specific area
- Users should be able to leave reviews (text, and potentially images) for businesses and rate their experience
- Users should be able to view businesses and reviews that other users have created


Non-functional Requirements

- Companies should be able to verify they own business
- A certain amount of latency should be allowed on review and image upload before it's shown on the website to avoid harmful content issues

Out of Scope

- Industry specific context for each business like restaurant menus, dentistry pricing etc
- The Business claiming process


Core Entities

- Companies
- Users
- Reviews


API

- GET /companies?category={}&location={}&name={} # these are optional parameters
- POST /companies/:id/reviews {rating, text} userId, reviewId
- GET /companies/:id/reviews companyId
- POST /companies {name, address, ...} companyId (new company)
- PATCH /companies/:id (edit existing company details)
- POST /reviews/:id/images {images []} companyId userId reviewId images []
- POST /companies/:id/claim

High Level Design (that satisifes the Functional Requirements)

- API Gateway to handle all incoming requests
- Backend Service to handle all API requests, storing reviews etc to database and also fetching them and returning them to the user
- Postgres Database to store all data related to companies, reviews, and users
- Redis Database to cache recent responses and improve performance for high activity businesses
- Separate Review Image Servie which uses a Queue to manage image upload
  - Use SQS to store the messages
  - build another backend service to exclusively handle this functionality
  - Has to be done to manage storing images in various sizes, then compression etc
  - Moderate the content coming through (ensure no NSFW)
  - Flag for manual QA review potentially**


Database DDL

- reviews
  - reviewId, companyId, userId, reviewText, rating, createdAt, updatedAt
- reviewImages
  - imageId, reviewId, userId, s3_location, image_size, is_harmful, createdAt, updatedAt
  - s3://yelp-review-images/business_id/year=yyyy/month=mm/day=dd/photo_id.jpg
  - separating this out because a user could upload multiple images, and tracking that hierarchy in the reviews table is tricky
- users
  - userId, email, createdAt, updatedAt
- company
  - companyId, userId, address, phone, owner, lat/long, avgRating, numReviews, createdAt, updatedAt



Deep Dives (to handle edge cases, critical performance implications, improvements to the system that can be made)

- Add Redis to improve response times
- CRON job to update companyDetails every ~1 hours w/ average rating and total number of reviews (this is fine if it's not real time)
- CDN *** - not as useful for serving global content globally, but still help serve static assets quicker things like images
- Image NSFW / harmful content - probably has to run through some ML process to classify each image and flag it as harmful or not before we serve it to the public
- Can introduce PostGIS extension for Postgres to enable improved text and geospatial search querying
  - Could also use Elasticsearch for full text searching to improve search latency, but there's more overhead here and requires CDC to keep data updated from Postgres (the source of truth)
  - Only a handful of million businesses, not a huge concern
- Add tags for companies 
- Can put unique key on review table on userId and companyId to only allow 1 review per user per business (if desired)

Napkin Math

