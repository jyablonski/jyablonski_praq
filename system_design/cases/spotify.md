# Spotify

## Core Requirements

- Company should be able to store songs (audio content, and metadata) on the platform
- Company should be able to play songs for users
- Users should be able to listen to songs available on the platform
- Users should be able to make playlists of songs they select


## Non-functional Requirements

- Service should be able to play songs for users at low latency
- Storing songs should be strongly consistent (if a user just added a song to their playlist, it should immediately show up and be playable)
- Service should scale to x million daily active users and y billion songs

Out of Scope

- Recommendation Service
- Premium / payment processing
- Ads management 
- In-app video content


Core Entities

- Songs
- Users
- Playlists

## API

- Assume users are authenticated using JWTs, and each request will include a token in the `Authorization` Header which the backend validates before handling the request
- Never include userId or timestamps in the request body, as these can be manipulated by the client

- GET /songs/:songId -> get metadata + presigned S3 URL for a given song
- POST /songs {artistId, songName, audioContent} -> create a new song
- POST /users/:userId/playlists {playlistName} -> create a new playlist
- GET /users/:userId/playlists -> get all playlists for a user
- GET /playlists/:playlistId/songs playlistId, [] songIds -> get all songs in a playlist
- POST /playlists/:playlistId {songId} -> add a new song to an existing playlist
- DELETE /playlists/:playlistId/songs {songId} -> to delete a song from a playlist

## High Level Design (to satisfy functional requirements)

- CDN for audio caching at the edge for faster response times
- API Gateway to handle all incoming requests, provide rate limiting + auth, and route client requests to the appropriate service
- Write Service to handle all incoming write requests for new songs, users, playlists, or updates to existing playlists to add new songs
    - Can be horizontally scalable and scaled independently from the Read Service
- Read Service to handle all incoming requests to listen to songs so we can fetch that content and return it to the user if it's not provided already by the CDN
    - Can be horizontally scalable and scaled independently from the Write Service
    - Use Pre-Signed URLs for S3 Access so we arent going S3 -> Read Service -> Client and instead we can just go S3 -> Client
- Postgres to store all metadata related to songs, users, and user playlists
    - Song audio content will be stored in S3 (blob storage), with metadata related to its file location stored in the songs table in Postgres
    - Thumbnails or album banners can be stored here as well
    - `s3://.../artistId/albumId/banner/resolution_xyz/banner.png`
- Redis as an in-memory cache to keep track of things like a song play count, or to serve s3 location for hot songs getting a lot of listens
    - Could even use multiple different redis databases here for this
    - Then flush to Postgres in batch every X hours:
- Setup a Search service using Elasticsearch to enable fast user search for songs, artists etc. 
    - This involves setting up CDC from Postgres to Elasticsearch to keep content up to date


## Database DDL

- Songs (songId, artistId, albumId, songName, songLength (int), s3Location, playCount, createdAt, updatedAt)
- Albums (albumId, artistId, albumName, albumCreatedAt, createdAt, updatedAt)
- Artists (artistId, artistName, category, createdAt, updatedAt)
- Playlists (playlistId, userId, createdAt, updatedAt)
- PlaylistSongs (playlistId, songId, position, createdAt, updatedAt)
    - So we keep a parent table for the playlists, and another table for 1 record per song in a playlist, and then when i want to serve that content to users i just make a query w/ a join ?
- Users (userId, userEmail, createdAt, updatedAt)


## Deep Dives

- Setup a Transcoding Service so we can serve audio content at different bitrates depending on user's internet connection or their desired settings
    - s3://.../artistId/albumId/songId/bit_rate_xyz/audio_content.mp3
- Setup audio content streaming to stream portions of songs in 2-10 second increments for faster response times for users as they flip around songs, similar to HLS or DASH for video content
- Setup some mechanism for updating playCount
    - This can be eventually consistent as we dont need to see live updates of a song's playcount
    - Honestly, a cron job that runs every x hours or even once a day to update the playCount seems appropriate
    - This is something we definietely want to track, but doing so in real time is completely unnecessary to the end user experience
- Setup thumbnail service to resize images and things like album banners depending on user device (desktop, mobile, ipad etc)
- Setup a search service for songs and content (Elasticsearch? this would involve CDC from Postgres to Elasticsearch to keep content up to date)
- Setup a user session state service so users can swap between songs on their phones, computers, and pickup where they left off at

## Napkin Math

- 100 M users (100 KB each) -> 10^8 * 10^2 -> 10^10 or 10 TB
- 2 B songs played per day (3 mins / each) -> 2 * 10^9 
- 1 B songs (~ 5 MB each) -> 10^9 * 10^6 * 5 = 5 PB of storage space
- 2B plays/day × 5 MB = 10 * 10^9 * 10^6 = 10 PB/day egress bandwidth