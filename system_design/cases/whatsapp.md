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
