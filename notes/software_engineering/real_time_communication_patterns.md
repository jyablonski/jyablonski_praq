# Real-Time Communication Patterns

## The Problem

Standard HTTP is request/response: the client asks, the server answers. If the server has new data, it has no way to push it to the client. Historically, clients would poll (repeatedly asking "anything new?"), which is inefficient and adds latency.

WebSockets and SSE solve this by keeping a persistent connection open so the server can push data when it's available.

- Both of these work on modern browsers, mobile apps, and server-to-server.

______________________________________________________________________

## Server-Sent Events (SSE)

What it is: A unidirectional channel where the server pushes data to the client. Built on plain HTTP with a `text/event-stream` content type.

Characteristics:

- Server -> client only
- Uses standard HTTP (works through proxies, load balancers)
- Browser handles reconnection automatically
- Supports event IDs for resumption after disconnect
- Simple to implement

Good use cases:

- Live dashboards and monitoring
- Notification streams
- Stock tickers, sports scores
- Progress updates for long-running jobs
- Streaming LLM responses

Server example (FastAPI):

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def event_generator():
    count = 0
    while True:
        count += 1
        yield f"data: {json.dumps({'count': count})}\n\n"
        await asyncio.sleep(1)

@app.get("/events")
async def sse_endpoint():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

Client example (browser):

```javascript
const source = new EventSource("/events");
source.onmessage = (event) => {
    console.log(JSON.parse(event.data));
};
```

`EventSource` is a browser API specifically for SSE. It handles:

- Parsing the SSE format
- Automatic reconnection
- Event dispatching

Limitation: `EventSource` is GET-only and doesn't support custom headers. For auth tokens or more control, you can use `fetch()` with a readable stream instead.

______________________________________________________________________

## WebSockets

What it is: A full-duplex, bidirectional communication channel over a persistent TCP connection. Both client and server can send messages at any time.

Characteristics:

- Bidirectional (client \<-> server)
- Starts as HTTP, then upgrades to WebSocket protocol (`ws://` or `wss://`)
- Lower per-message overhead than HTTP
- No automatic reconnection (must implement yourself)
- Slightly more complex to scale

Good use cases:

- Real-time chat and messaging
- Multiplayer games
- Collaborative editing
- Live trading platforms
- Any high-frequency bidirectional communication

Server example (FastAPI):

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You said: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

Client example (browser):

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = () => {
    ws.send("Hello server");
};

ws.onmessage = (event) => {
    console.log(event.data);
};
```

The `ws://` scheme triggers a WebSocket handshake. The browser sends an HTTP upgrade request, the server agrees, and the connection switches protocols.

______________________________________________________________________

## How They Scale

FastAPI (via Starlette) handles both using async coroutines, not threads. Each connection is a lightweight task managed by the event loop. Hundreds of connections use minimal resources.

Limiting factors:

- File descriptors: Each connection uses one. Default is 1024 per process (tunable via `ulimit -n`).
- Memory: Base connection cost is a few KB. Application state per connection adds up.
- CPU: Idle connections cost almost nothing. Load comes from message processing.

At small scale (hundreds of connections), a single server handles it fine.

______________________________________________________________________

## Scaling WebSockets Across Multiple Nodes

This is where WebSockets get complicated.

The problem:

WebSocket connections are stateful and pinned to a specific server. If you have two backend instances behind a load balancer:

- User A connects -> lands on Server 1
- User B connects -> lands on Server 2
- User A sends a message
- Server 1 only knows about its own connections
- User B never receives the message

The servers don't share memory.

Single server broadcasting (works fine):

```python
connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            for client in connected_clients:
                await client.send_text(message)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
```

Multi-server solution: Pub/Sub

Introduce a shared message broker (Redis, NATS, Kafka). All servers subscribe to a channel.

Flow:

1. User A sends a message via WebSocket to Server 1
1. Server 1 publishes the message to Redis
1. Redis broadcasts to all subscribers
1. Server 1 and Server 2 both receive it
1. Each server pushes to their local WebSocket clients
1. User B (on Server 2) receives the message

The pub/sub layer coordinates between stateful connections spread across stateless, horizontally-scaled backend nodes.

SSE has the same challenge, but reconnection is cleaner—clients can reconnect to a different server and resume via `Last-Event-ID`.

A single Redis cluster works for: Pub/sub, session storage, shared caching, coordination between nodes to act as the source of truth for what data needs to be sent to which clients.

______________________________________________________________________

## When to Use Which

| Scenario | Choice |
| ----------------------------------------------------- | ---------- |
| Server pushes updates, client just listens | SSE |
| Client and server both send messages frequently | WebSockets |
| Need simple implementation, standard HTTP infra | SSE |
| Need low-latency bidirectional communication | WebSockets |
| Building chat, multiplayer games, collaborative tools | WebSockets |
| Building dashboards, notifications, progress updates | SSE |

Both beat polling. SSE is simpler when unidirectional is enough. WebSockets are necessary when you need true bidirectional communication.

______________________________________________________________________

## Infrastructure Considerations

Proxies and load balancers:

- WebSockets require connection upgrade support
- SSE requires disabling response buffering (`proxy_buffering off` in nginx)

Sticky sessions:

- WebSocket connections are inherently sticky (pinned to one server)
- Scaling requires external coordination (pub/sub)

CORS:

- SSE follows standard HTTP CORS rules
- WebSockets have origin validation during handshake (server-side check)
