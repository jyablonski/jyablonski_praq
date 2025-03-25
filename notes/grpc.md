# gRPC

gRPC (Google Remote Procedure Call) is an open-source framework developed by Google for building high-performance, language-agnostic distributed systems. It is commonly used in microservice architectures to enable efficient & highly performant service-to-service communication. gRPC leverages HTTP/2 for transport and Protocol Buffers (protobuf) as its interface definition and serialization format.

gRPC uses Protobuf as the serialization format, which is:

- Smaller than JSON or XML
- Faster for serialization & deserialization for getting data from memory into bytes that can be sent over the network to some other service
  - Serialize from in-memory object into bytes ➡️ Send over network ➡️ Deserialize back into in-memory object.
- Ensures data integrity by defined types and required fields

## Pros & Cons

It's a competitor to REST and has major advantages at scale over its counterpart:

1. Performance & efficiency due to HTTP/2 and Protobuf
2. Strongly Typed contracts / endpints through the .proto files
3. Auto-generated code to reduce boilerplate
4. Backwards-compatability w/ how the fields & their field numbers are setup

But, it also has disadvantages over REST:

1. Less human readable, debugging is a bit trickier
2. Testing is more difficult compared to REST w/ curl or Postman
3. gRPC doesn't work natively in browsers because they don't support HTTP/2, so you need gRPC-web which is an additional proxy layer that adds complexity
4. Steeper learning curve with protocol buffers and the proto files
5. gRPC is optimized for internal service to service communication and not so much for public-facing APIs
6. For lightweight services where speed isn't critical or where human-readability (JSON) is important, the binary efficiency of gRPC might not justify the added complexity.

## Internals 

With Proto Files you define the structure and contract of the communication between client and server. Specifically, the Proto Files define:

- The gRPC Services (`UserService`)
- The available Methods on the gRPC Service (`GetUser`)
- The Inputs & Outputs of the Methods (`UserRequest` and `UserResponse`)
- The fields + their types for the Requests + Responses

In the proto file the fields have field numbers which uniquely identify each field within a message. Because of how Protobuf serializes the data as a compact binary format in a key value pair, these field numbers end up being the key.

- During serialization, only the field numbers and values are stored, **not** the field names, making the message more compact and efficient.
    - The field names are stored in the client + server code / memory, and aren't send along in the request like they are in JSON
    - This makes parsing extremely efficient, compared to text-based formats like JSON or XML.
- Field numbers also make messages backward and forward compatible; new fields can be added without breaking older clients, as they will simply be ignored. 
    - If a field is removed, the field number should never be reused, ensuring compatibility with older messages that might still contain that field. 
    - If an older client receives a message with field numbers it doesn't know about, it simply skips those fields.
    - If a newer client receives a message from an older gRPC server with a field, you can choose whether to error out or to simply null it out

Example proto file:

``` protobuf
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
}

message UserRequest {
  int32 user_id = 1;
}

message UserResponse {
  int32 user_id = 1;
  string name = 2;
  string email = 3;
}
```

Proto files are language agnostic and work with many different supported programming languages such as Python & Go.

After defining your services & requests in the proto file, you generate data structures & stubs for the client + server to use in your code. You must use the protoc compiler to generate language-specific code from the proto file.

- Stubs are auto-generated pieces of code that act as a bridge between your application code and the gRPC framework
- The generated code automatically handles the **serialization** of request objects into binary format for transmission over HTTP/2 and **deserialization** of response objects back to their respective classes.
- The generated code enforces the **contract** defined in the proto file to ensure the client requests data in an expected format, the server responds w/ correct fields + data types, and incompatibilities are caught at compile time, not runtime.

The gRPC stub handles all the network communication and data serialization, but you are responsible for implementing the actual business logic on the server side such as:

- Processing the Request
- Performing operations such as database queries, calling other services, performing calculations etc
- Constructing the Response with the required data

### **How It Fits Together**  
1. **Client Side:**  
   - The client calls a method on the **client stub**.  
   - The stub **serializes** the request and sends it over the network.  
   - It **waits** for the server's response, then **deserializes** it into a usable object.  

2. **Server Side:**  
   - The **server stub** (generated from the `.proto` file) **receives** the request and deserializes it.  
   - It **calls the appropriate method** in your service implementation class.  
   - You write the logic to **process the request** and **return a response**.  
   - The server stub **serializes** the response and sends it back to the client.  

## Caveats

Web browsers don't natively support gRPC since it uses HTTP/2 and a binary format (Protobuf). But there are several ways to bridge this gap:

1. gRPC-Web is a JavaScript Client Library that allows web apps to communicate with gRPC services using HTTP/1.1 or HTTP/2. It translates gRPC requests into HTTP requests that browsers can work with
    - You need a gRPC Web proxy (like Envoy) to convert web requests to regular gRPC Requests that your backend can understand
    - Browser (gRPC-Web) --> Envoy Proxy --> gRPC Server
    - The proxy keeps the Protobuf binary format intact but wraps it in an HTTP/1.1 or HTTP/2-compatible way.
2. REST Gateway which exposes your gRPC services as RESTful APIs by gRPC - JSON transcoding to translate REST requests to gRPC methods
    - This uses Envoy or a grpc-gateway to convert REST calls (example: `GET users/123`) into gRPC
    - Browser (HTTP/JSON) --> Envoy Proxy / grpc-gateway --> gRPC Server
    - No changes needed on the frontend since you make standard HTTP requests, but JSON serialization adds overhead compared to Protobuf.
    - This involves converting between JSON and Protobuf for each request and response.


``` typescript
import { UserServiceClient } from './generated/user_grpc_web_pb';
import { UserRequest } from './generated/user_pb';

// the grpc-web route
// Initialize gRPC-Web client
const client = new UserServiceClient('http://localhost:8080', null, null);  // gRPC-Web Proxy URL

const request = new UserRequest();
request.setUserId(123);

client.getUser(request, {}, (err, response) => {
  if (err) {
    console.error('Error:', err);
    return;
  }
  console.log('User:', response.getName(), response.getEmail());
});

// The REST gateway route
// Make a RESTful API request to the backend (which is mapped to gRPC behind the scenes)
fetch('http://localhost:8080/users/123', {
  method: 'GET',
})
  .then((response) => response.json())
  .then((data) => {
    console.log('User:', data.name, data.email);
  })
  .catch((err) => console.error('Error:', err));
```

## Protoc

Protoc is the Protocal Buffers Compiler, a tool used to generate source code from the proto files

``` sh
# Generate Python files from proto
protoc --python_out=. --grpc_python_out=. user.proto
```

## Protocol Buffers

Protocol Buffers is a binary serialization format developed by Google to efficiently encode and decode data in a platform and language agnostic way. gRPC uses Protocol Buffers as its serialization format