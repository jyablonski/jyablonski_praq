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