# Headshot Pro

## Core Requirements

- Users should be able to upload selfies & other pictures of themselves
- Users should be able to select various outfits and backgrounds for their headshots
- Users should be able to receive AI headshots based on their uploaded pictures

## Non-functional Requirements

- Picture Upload should be low latency
- After submitting their request, AI headshots should be delivered within 1-2 hours

## Out of Scope

- Picture Editing / re-submission
- Payments processing

## Core Entities

- User Images
- AI Images (headshots)
- Ancillary system resources (backgrounds, outfits etc)

## API

Assume all endpoints are using JWT authentication and require appropriate headers to use

- POST /users/:userId/images/upload-url (generates a pre-signed URL and returns it to the client)

``` json

// request params
{
  "fileName": "selfie.jpg",
  "contentType": "image/jpeg"
}

// response
{
  "uploadUrl": "https://s3.amazonaws.com/headshot-pro-images/users/abc123/user_images/3f8a32f1-selfie.jpg?...",
  "s3Key": "users/abc123/user_images/3f8a32f1-selfie.jpg"
}

```

- The client then uses that pre-signed URL to make a PUT request to S3 w/ the image
- Afterwards, the client does another POST request to images to register it in the backend

PUT https://s3.amazonaws.com/your-bucket-name/users/abc123/user_images/selfie.jpg?AWSAccessKeyId=...
Content-Type: image/jpeg
Body: <binary image data>

- POST /users/:userId/images (this gets called after image upload to generate metadata in database)

{
  "s3Key": "users/abc123/user_images/selfie.jpg",
  "fileName": "selfie.jpg",
  "contentType": "image/jpeg",
  "fileSize": 4839230
}

- GET /system/backgrounds [] background images
- GET /system/outfits [] outfit images
- GET /users/:userId/headshots [] headshot images
    - Implement pagination to grab images x amount at a time
    - Optional batchId parameter to allow users to pull specifically from a recent batch of headshots
- POST /users/:userId/headshot-batches (start a headshot generation batch)

{
  "userImageIds": ["img1", "img2"],
  "backgroundIds": ["bg1", "bg2"],
  "outfitIds": ["outfit1", "outfit2"]
}

- GET /users/:userId/headshot-batches/:batchId/status

{
  "status": "processing" | "completed" | "failed",
  "startedAt": "...",
  "completedAt": "...",
  "headshotCount": 6,
  "headshotsGenerated": 4
}

## High Level Design (to satisfy functional requirements)

- API Gateway for auth, rate limiting, routing etc
- Backend Service to handle image + headshot fetching and to submit queue requests for new AI Headshots
    - When submitting a new queue request, it will store the details in the Postgres database and then create the message to put in the queue
- Queue to store all new AI Headshot requests from users
    - Message contains: `userId, batchId`
- Queue Consumer Service to continuously process messages off the queue for users requesting new AI Headshots
    - This Queue service will read the userId and batchId from the message, go fetch more details in the database, and then generate AI headshots based on the parameters specified by the user
    - Each headshot will have an outfit and background, along with a base userImageId that it used as a reference for the user (this could potentially be implemented differently - depends on how you utilize AI to generate the headshots)
    - After submitting LLM requests to generate the images, it will store them to S3, generate new records in Postgres to track them before completing the job and moving onto the next request
- S3 to store all User Images & future AI Headshots
    - Can split this up by user id ex: `s3://headshot-pro-images-prod/user=xyz/user_images/...` or `users=xyz/headshot_images/...`
    - Should utilize pre-signed URLs here so users can upload images directly to S3 for latency + performance reasons. If we have to upload first to backend service and then do the S3 upload on our behalf, this adds a lot of wasted time
- Postgres Database to store all user information, system resources, and also link tables between user images or AI Headshots and their respective location in S3
- Stripe for payments processing etc (not a huge focus)

## Database DDL

- users             - userId, email, createdAt, modifiedAt
- userImages        - imageId, userId, s3Location, createdAt, modifiedAt (1 record per image)
- userHeadshotBatch - batchId, userId, createdAt, modifiedAt (1 record per submission / purchase)
- userHeadshots     - headshotId, batchId, backgroundId, outfitId, userId, userImageId, s3Location, createdAt, modifiedAt (1 record per headshot image)
    - Index on batchId as this is how we will pull records for users
- systemBackgrounds - backgroundId, s3Location, createdAt, modifiedAt (1 record per background)
- systemOutfits     - outfitId, s3Location, createdAt, modifiedAt (1 record per outfit)

## Deep Dives

- Notification Service to notify customers when their headshots are available
- AI Image Generation implementation - choosing different LLM tools, guaging their quality, doing A/B testing on customer satisfaction with the headshots etc
- Re-try logic or dead letter queue stuff if the headshot batch submission fails
- Image Quality + more A/B testing stuff. Basically a lot of this is going to depend on what are competitor services doing, how you want to differentiate yourself etc

## Napkin Math

- Not too relevant here. even if we had 100+ million users, they wouldn't be purchasing headshots all the time, and even fetching past headshots would be extremely infrequent. This is typically a once-every-5-years type of transaction
