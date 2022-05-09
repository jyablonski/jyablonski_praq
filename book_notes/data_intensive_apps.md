# Chapter 1 Foundations of Data Systems
Systems should be Reliable, Scalable, and Maintainable.

Find out the proper percentiles to optimize performance / latency for.  It might make sense to optimize the 95th percentile to maximize customer satisfaction + sales, but 99.9% would be too expensive and not worthwhile.

Service Level Objectives (SLO) and Service Level Agreements (SLA) define the expected performance and availability of a serivce. 
    * Service is considered up if it has median response time of less than 200ms and 99th percentile under 1 second.

It's hard to scale architectures.  If your load is x and the new load is 10x then the original architecture might not hold up.
    * Elastic systems can automatically scale in & out to match this load and continue operating at peak performance.  
    * Others have to be manually adjusted by a human and are slower to change and generally more error prone.
    * Scaling out to multiple systems introduces a shit ton of complexity, so try to stick to single machine processes until you're forced to make it distributed.

Maintainability - there's a cost to maintenance, fixing bugs, keeping systems operational, and investigating failures.  
    * Make systems that focus on operability, simplicity, and evolvability.
      * Operability - Easily view the health of the system, keep software up to date, establish good practices for testing + deployment.
      * Simplicity - manage the complexity, don't have hidden assumptions, reuse code instead of reimplementing it multiple times.

# Chapter 2 Data Models and Query Languages
Data Models - Relational vs Documents

SQL is very popular for relational which is consisted of tables of columns and rows.  It has better support for joins and many-to-many and many-to-one relationships.

NoSQL offers different benefits from the relational model.
    * Offers greater scalability.
    * Generally more open source than historically with company's like Oracle in the SQL space.
    * Specialized query operations different rfom those with the relational model.
    * Schemaless freedom that you don't get with relational model.

SQL historically had issues with XML + JSON and the schemaless nature of these data formats, which made NoSQL formats more enticing.  Nowadays that's not the case, and both frameworks are moving closer to supporting the same features more or less.

## Many-to-One and Many-to_Many Relationships
These relationships fit in SQL but are hard to implement in NoSQL.

Relational DB the query optimizer automatically figures out which parts of the query to execute in which order, creating the "access path" for you.  SQL is a declarative language so we just define the pattern of data we want and what conditions must be met, but not HOW to do it.  That's the query optimizer's job.  This format also allows parallel processing to be easily implemented across multiple machines.

`Schema on read` means the structure of the data is only interpreted when the data is read, so is essentially schemaless when you store it.

`Schema on write` means the structure of the data is defined when you store it.  Think `CREATE TABLE sales as day DATE, sales INT, owner CHAR` etc.

Schema changes screw a lot of things up and both approaches have their upside + downside.
    * For schema on read, you may have a schema change that you never know about because you don't enforce it.
    * For schema on write, your code may fail when a new column appears.

## Graph-like Data Models
SQL can handle many to many relationships, NoSQL has a hard time, so if you want the NoSQL and have a lot of many to many relationships think about using graph data models.

Graph consists of vertices (nodes or entities) and edges (the relationships).
    * Social graphs - verticies are people with the edges being the people they're friends with.
    * Web graphs - verticies are pages, and the edges are the HTML links to other pages.

Graphs can also link data that aren't typically associated with each other.

Graph Models typically don't enforce a schema for the data they store, so it can easily adapt to changing business requirements.

# Chapter 3 Storage and Retrieval
Indexes are used to basically store a small amount of metadata about how to query the data you want.  They slow down writes, but improve query times.  So you usually shouldn't index everything.  Know your query patterns before hand.

# Chapter 4 Encoding and Evolution
Staged rollout - server side technique when you update a very large application base so only a few nodes at a time get the new version.  In client side apps this won't work, bc you can't really force the client to update.
    * Old and new versions of code and releases might co-exist at the same time.
    * Backwards Compatibility - Newer code can read data written by older code
    * Forward Compatibility - Older code can read data written by newer code.

Encoding - when you want to send data over a network, you have to encode it as some kind of self-contained sequence of bytes.  You can't use your personal PCs internal pointers anymore where the data sits in memory, which is why this sequence of bytes look different than what we're used to.
    * Serialization - Turning in memory objects into a series of bytes to store it or transmit it somewhere.
    * Deserialization - Turning an unreadable series of bytes into an object you can interact with in memory.
      * Takes time for the CPU to deserialize the bytes.
    * Python example - `pickle` library
      * Stores in memory objects as a sequence of bytes.
      * It becomes difficult to share these things across programming languages.

File Types
    * XML used to be used a lot but it's very verbose and complicated
    * JSON used a lot bc it's natively supported by web browsers, can distinguish numbers and strings but precision (float values etc) can get fkd up.
      * Uses a lot of space compared to binary formats.
    * CSV used a lot but everything is represented as strings

## Binary Encoding
Protocol buffers are binary encoding libraries that require a schema for any data encoded.  Comes with a code generation tool in your respective programming language to create the classes + schemas for you.  Array / list fields - `repeated` object type.
    * Lightweight and compact bc field names are ommitted from the encoded data.
    * Schema is a valid form of documentation to see what the message is made up of.

Avro is similar but different to protobufs, it has a schema and has 2 versions for humans to read and machines to read.

Service Oriented Architecture - decomposing a large application into smaller services by area of functionality so they request things they need from each other.
    * Goal is to make application easier to change and maintain by making each service independently deployable and evolvable.

Web Service - when HTTP is the protocol for talking to a service.

REST is a design philosophy to emphasize simple data formats, using URLs to identify resources, and using standard HTTP features for authentication and requests.
    * Commonly use JSON.

Remote Procedure Protocol (RPC) - make a request to a network service look the same as calling a function in a programming language
    * Flawed bc networks are inherently unpredictable.  
      * Can be unavailable, no internet, inconsistent response times, or timeout.

Message Broker - messages get sent to a queue or topic, and the broker ensures the message is delivered to one or more consumers or subscribers to that topic.
    * Rabbit MQ, Kafka etc.
    * Pub / Sub architecture.

# Chapter 5 Distributed Data