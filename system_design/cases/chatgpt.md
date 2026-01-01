# ChatGPT

## Core Requirements

- Users should be able to ask questions in a prompt format and be given responses via an LLM Model
- Users should be able to select a series of different models to use for their prompts
- Users should be able to view past chats

## Non-functional Requirements

- Application should be low latency and provide results within 10 seconds
- Follow up prompts should consider previous context

## Out of Scope

- Voice input or voice output
- Model creation & training
- Pro tier; assume everything is free and we're just building up market share
- Other advanced features like Codex

## Core Entities

- Prompts
- Chats
- Models

## API

Use REST to allow users to browse their chat history, use Websocket for live streaming of LLM responses for fast performance and low latency

Chat Management (REST)

- POST /chats { modelId, title? }
- GET /chats
- GET /chats/:chatId/messages
- DELETE /chats/:chatId

Live Messaging (WebSocket)

- Connection: `/ws/chats/:chatId`
- Send: `send_message` event with message text
- Receive: Streaming response tokens in real-time

## High Level Design (to satisfy functional requirements)

- API Gateway for user authentication, rate limiting, service routing
  - This is where clients get authenticated and start a websocket connection for their chats
- Message Processing Service which handles chat logic, context assembly, validation
- Model Router/Gateway to handle routes to appropriate model endpoints
  - Messages are passed here and then flow through to the right model service
- Multiple Model Services - one per model type, horizontally scaled
- Model Serving Infrastructure requires significant GPU compute
- Redis Database to cache recently chats & messages
- Postgres Database to track prompts, chats, users, all interaction history etc

```sh
Client (WebSocket) 
  ↕
API Gateway (WebSocket termination, auth, rate limiting)
  ↕  
Message Processing Service (chat logic, context assembly)
  ↕
Model Router/Gateway (model selection, load balancing)
  ↕
Model Service (LLM API calls)
  ↕
External LLM APIs (OpenAI, Anthropic, etc.)
```

## Database DDL

- chats chatId, userId, title?, createdAt, updatedAt
- messages messageId, chatId, role, content, modelId, parentMessageId?, createdAt
- models modelId, modelName, createdAt
- users userId, email, createdAt, modifiedAt

## Deep Dives

- Batching prompts up and processing them in bulk to assist w/ GPU utilization
- Model updates (like ChatGPTv5 on the site has like 50+ updates over the course of 6+ months, how to handle that on a data level?)

## Napkin Math

- 10 M DAU
- 50 Prompts per day
- 500 M total prompts / day
- 10^8 / 10^5 = 10^3 or 1000 prompts per second
