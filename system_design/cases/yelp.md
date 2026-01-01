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
  - Flag for manual QA review potentially\*\*

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
- CDN \*\*\* - not as useful for serving global content globally, but still help serve static assets quicker things like images
- Image NSFW / harmful content - probably has to run through some ML process to classify each image and flag it as harmful or not before we serve it to the public
- Can introduce PostGIS extension for Postgres to enable improved text and geospatial search querying
  - Could also use Elasticsearch for full text searching to improve search latency, but there's more overhead here and requires CDC to keep data updated from Postgres (the source of truth)
  - Only a handful of million businesses, not a huge concern
- Add tags for companies
- Can put unique key on review table on userId and companyId to only allow 1 review per user per business (if desired)

Napkin Math
