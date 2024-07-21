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


## Design Uber

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
   3. `POST /fare-estimate?pickupLocation={pickup}&destination={destination}`
   4. Returns {ride_id, estimated_price, estimated_pickup_time}
2. Ride Request
   1. Endpoint for when Users request a ride. 
   2. Takes a Ride ID returned from the Fare Estimate
   3. `PATCH /ride/request`, passing in the ride_id returned from the Fare Estimate
   4. Patch because we might edit the Fare Estimate row and turn it from `is_booked` from false to true or something
3. Driver Location Update Request
   1. Endpoint that is continuously called by Drivers on the clock to get their location update. 
   2. Takes a Lat Long
   3. `POST /drivers/location/update`
4. Driver Accept Ride Request
   1. Endpoint that allows Drivers to accept or deny a ride request.
   2. Takes a Ride ID and a true / false value for yes or no
   3. If accepted, returns Lat / Long coordinates for pickup.
5. Update Ride Status 
   1. Endpoint that updates Ride Status for a specific Ride ID
   2. Status -> "picked_up_rider" | "completed"


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


## Design Ticketmaster

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

# Common Elements

Using an API gateway to route requests to various services rather than having the frontend directly call your microservices offers numerous benefits:

### 1. **Centralized Control and Management**
- **Single Entry Point**: An API gateway acts as a single entry point for all client requests, simplifying the architecture and making it easier to manage and secure.
- **Security**: Centralizes security features such as authentication, authorization, rate limiting, and SSL termination, reducing the attack surface and simplifying the enforcement of security policies.

### 2. **Traffic Management**
- **Load Balancing**: Distributes incoming traffic across multiple instances of your microservices, improving availability and reliability.
- **Rate Limiting and Throttling**: Protects backend services from being overwhelmed by too many requests, ensuring better performance and stability.

### 3. **Performance Optimization**
- **Caching**: Can cache responses from services to reduce load and latency for frequently requested data.
- **Compression**: Compresses responses to reduce the amount of data transferred, speeding up communication with clients.

### 4. **Protocol Transformation**
- **Protocol Handling**: Translates between different protocols (e.g., HTTP, WebSocket, gRPC), allowing services to use the protocols most suited to their needs while presenting a unified interface to clients.

### 5. **Simplified Client Interface**
- **API Aggregation**: Combines multiple service calls into a single API call, reducing the number of requests the client needs to make and simplifying the client-side code.
- **Version Management**: Handles API versioning, allowing multiple versions of the API to coexist and facilitating smooth transitions between API versions.

### 6. **Improved Developer Experience**
- **Consistency**: Provides a consistent API for all services, making it easier for frontend developers to interact with the backend.
- **Documentation and Discovery**: Often integrates with tools to automatically generate API documentation, making it easier for developers to understand and use the available APIs.

### 7. **Security Enhancements**
- **Authentication and Authorization**: Centralizes authentication and authorization, ensuring that all requests are properly authenticated and authorized before reaching the services.
- **Data Validation**: Validates incoming requests and responses to ensure they meet the required formats and constraints, enhancing security and stability.

### 8. **Service Discovery and Flexibility**
- **Service Discovery**: Integrates with service discovery mechanisms to dynamically route requests to the appropriate service instances, supporting scalability and flexibility.
- **Flexible Routing**: Routes requests based on various criteria (e.g., URL paths, request headers, or user roles), allowing for more complex and customizable routing logic.

### 9. **Monitoring and Analytics**
- **Centralized Logging**: Aggregates logs from multiple services, providing a unified view of all incoming and outgoing traffic.
- **Metrics and Monitoring**: Collects metrics and provides monitoring capabilities, helping to identify performance bottlenecks and other issues more easily.

### Conclusion

An API gateway offers significant benefits over direct frontend-to-microservice communication by providing centralized management, improved security, performance optimization, and a simplified client interface. It enables better scalability, reliability, and maintainability of a microservices architecture, making it an essential component in modern distributed systems.
