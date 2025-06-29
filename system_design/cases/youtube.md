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
