# Software Development Questions

### **General Programming & Algorithms**
1. Explain the differences between an array and a linked list. When would you use one over the other?

- An array is a fixed-size data structure that allows random access
- A linked list is a dynamically-sized data structure with nodes that require sequential access to perform insertions or deletions

2. What is the time complexity of quicksort, mergesort, and bubble sort?

- quicksort is a varying O(n log n) best case, O(n^2) worst case time complexity, depending on how good or bad you set your pivot point

3. Explain the concept of recursion and give an example of a problem best solved using recursion.

- Recursion is a technique where you use a function to call itself until it hits some base case
- Traversing a nested tree or list structure is a good application for this

4. What is dynamic programming, and can you provide an example where it is useful?

- Dynamic programming is used for problems with overlapping subproblems, like the Fibonacci sequence.

5. What are hash tables, and how do they work?

-  Data structures that store key-value pairs for O(1) average lookup time.

### **Data Structures**
6. What are the different types of trees in computer science (e.g., binary trees, AVL trees, B-trees)?

- A tree is a hierarchical data structure where each node has a parent and 0 or more children called leaf nodes.
- Binary tree just has normal nodes and children
- Binary Search Tree is a sorted binary tree left < root < right
- AVL Tree is a BST that auto balances to maintain O(log n) operations
- B tree is a generalized BST for disk-based storage systems (databases, file systems)

7. Explain how a graph can be represented in code. What are adjacency lists and adjacency matrices?


- Adjacency matrix is a 2d matrix where n is number of nodes on the graph and is used to represent the connections between verticies of a graph
```python
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C']
}
```

8. What is the difference between a stack and a queue?

- Stacks are LIFO (last in, first out) for things like recursion, backtracking
- Queues are FIFO (first in, first out)

9.  How does a priority queue work, and where is it used?

- Uses a heap to process elements with priority-based order.


10. What are Bloom filters, and when would you use them?

- A probabilistic data structure that checks membership efficiently but may have false positives.

### **Object-Oriented Programming (OOP)**
11. What are the four pillars of OOP (encapsulation, inheritance, polymorphism, abstraction)?

- Encapsulation refers to bundling up variables and methods that operate on that data into 1 class and restrict direct access to enforce data integrity
- Inheritance refers to allowing a class (child) to derive from another class (parent) to inherit its attributes and methods. Such as a Car class inheriting from a Vehicle class
- Polymorphism refers to the ability of a function or object to take on multiple forms, such as a `draw()` method behaving differently for a Circle or Rectangle classes
- Abstraction refers to hiding implmentation detail and only exposing necessary parts, such as an `Animal()` interface with a `makeSound()` method thats implemented different for Dog and Cat clases

12. What is the difference between composition and inheritance?

- Inheritance - A class derives from a parent class and inherits its behavior (A Bird class inherits from Animal)
- Composition - A class contains an instance of another class instead of inheriting from it (A Car has an Engine (instead of Car inheriting from Engine))

13. What is the SOLID principle in software engineering?

- S - Single Responsibility Principle (SRP): A class should have only one reason to change.
- O - Open/Closed Principle (OCP): Classes should be open for extension but closed for modification.
- L - Liskov Substitution Principle (LSP): Subtypes should be replaceable for their base types without altering behavior.
- I - Interface Segregation Principle (ISP): Clients shouldn’t be forced to depend on interfaces they don’t use.
- D - Dependency Inversion Principle (DIP): High-level modules should not depend on low-level modules; both should depend on abstractions.

14. What is dependency injection, and why is it useful?

- Dependency Injection (DI) is a design pattern where dependencies (objects) are provided to a class instead of the class creating them itself.

15. Explain the difference between method overloading and method overriding.

- lol

### **Databases & SQL**
16. What is normalization, and why is it important in relational databases?

- Normalization is the practice of reducing data redunancy and minimizing
- It's important because it improves performance for applications using the databas

17. How do indexes work in databases, and what are their trade-offs?

- Indexes are data structures that store pointers to a column's actual values in some sorted order
- This improves read performance on any subsequent queries on that column, because they can use the index to retrieve the data much faster
- This lowers insert, update, and delete performance as the index has to constantly be maintained as the data changes in the table

18.  What are the different types of database joins (INNER, LEFT, RIGHT, FULL OUTER)?

- Inner joins only return rows found in the source table and the table being joined
- Left + Right joins only return rows found in the respective table
- Full Outer joins will return all rows found in both tables even if they didn't have a match

19.  Explain ACID properties in database transactions.

- Atomic. Transactions will complete all-or-nothing; you'll never be left in an invalid state where only part of something was completed.
- Consistent. The database will always behave the same way and uphold the constraints you tell it to, and it wont enter a corrupted state
- Isolated. Database transactions will commit one at a time, even if 2+ users are making simultaneous queries
- Durable. Once transactions are committed the changes are saved to disk and are permanent even in the event of system failure


20.  What is the difference between SQL and NoSQL databases?

- SQL databases are relational databases with structured schemas, tables, ACID compliance, and adhere to ANSI SQL standards. Typically harder to horizontally scale
- NoSQL databases are non-relational databases that are schema-less and typically used for semi-structured or unstructured data. Typically easier to horizontally scale

### **Systems Design & Scalability**
21. How would you design a URL shortener like Bit.ly?

- Use base62 encoding on an autoincrementing ID from a serial column in postgres to guarantee uniqueness for every short -> long url
- Use Redis for caching and improving performance
- Use Postgres to store the short_code and long url information for each request
- Read heavy system all things considered

1.  How do load balancers work, and what types are there?

- Load Balancers receive incoming traffic and distribute requests across multiple servers to improve performance, availability, and reliability to ensure no single server is overwhelmed, and to maximize the end user experience
- Layer 4 load balancers distributes traffic based on IP and TCP/UDP ports	
- Layer 7 load balancers routes traffic based on HTTP headers, cookies, or content
- Nginx, Traefik are software load balancers
- AWS ELB is a fully managed cloud load balancer
- Different algorithms for deciding which server, such as round robin, least connections, least response time, etc.

23. What are microservices, and how do they compare to monolithic architectures?

- Microservices are individual services that perform a specific function
- These microservices are typically smaller in nature and can independently scale up & down to changes in load
- Becomes more challenging to develop in when you have multiple services involved for your application to function correctly
- Monolithic architectures house the entire application in 1 codebase (tightly coupled), and are typically harder to scale properly as the different components all run on the same hardware

24.  What is CAP theorem, and how does it apply to distributed systems?

- CAP Theorem is consistency, availability, and partition tolerance.
- Have to choose between consistency or availability, because you will always need partition tolerance because they are inevitable due to failures, latency, or disconnected nodes.
- For something like an `Add to Cart` button, you'd want to prioritize availability so users can always add items to their cart, with the idea that you'll have eventual consistency a few seconds or minutes later when they're ready to order
- For something like `Submit Order` or `Pay Now`, you want to prioritize consistency. If User A books ticket #1000 and User B also books ticket #1000, you could hand out the same ticket to 2 different people because your system didn't prioritize consistency.

25.  How would you handle millions of concurrent users in a web application?

- I would add a Load Balancer to route users to a Server w/ the least load
- I would add CDN caching so I can improve latency and reduce server load on static content as much as possible
- I would horizontally scale my Primary Server so it can scale up & down depending on the traffic
- I'd add caching to my static content, and between my Primary Server + my Database to increase performance as much as possible

### **Networking & Security**
26. What is the difference between TCP and UDP?

- TCP is a handshake where each party sends ACKs everytime they exchange data
- UDP also allows 2 parties to exchange data, but there are no ACKs. It's all free baby

27. How does HTTPS work, and why is it more secure than HTTP?

- HTTPS adds encryption to every page and the content you put on that page as you make HTTP requests
- It ensures nobody on your network can see your content or the data you're sending except you

28. What are JWTs (JSON Web Tokens), and how are they used in authentication?

- A JWT is a token handed out by an auth server after you've logged in, and is typically set as a cookie in a User's browser
- This JWT can be used for auth to prove that the user is who they say they are, and allow access to protected endpoints or web pages
- The JWT includes username and TTL info on when the JWT will expire, and is encrypted with a key only found on the server
- Nobody can tamper with the JWT unless they have that key
- But, if somebody does modify the JWT it will remain usable until it's expired. So typically want to set JWTs for like <30 days

29.  Explain SQL injection and how to prevent it.

- SQL injection is the practice of attacking services by running SQL through a particular exploit

30.  What is the difference between symmetric and asymmetric encryption?

- Symmetric encryption involves 1 Key to encrypt & decrypt something
- Asymmetric encryption involves a key pair of 2 keys, a public and private one. Everybody can know the public one to encrypt some data, but only the private key can be used to de-crypt it.
- This means you can put your public key on github or whatever, it doesn't matter unless someone also have the private key (which should be kept secret)

### **DevOps & Cloud Computing**
31. What are containers, and how do they differ from virtual machines?

- Containers are lightweight environments taht package an app + its dependencies together. It shares the host OS kernel which makes it more efficient than a VM, and allows you to run multiple containers simultaneously for multiple apps.

32. Explain the benefits of using Kubernetes for container orchestration.

- K8s manages the automating, scaling, and operation of containerized apps. You define the desired state of your app in YAML files, and it automatically manages your app to that desired state
- It also has capabilities to perform load balancing, high availability, horizontal scaling, and simplified rollouts and rollbacks.

33. What are Infrastructure as Code (IaC) tools like Terraform and Ansible?

- IaC tools like Terraform build infrastructure on platforms like AWS or GCP via code, rather than through a CLI or a web console
- You view your potential changes via `terraform plan`, and build them via `terraform apply`
- The tool keeps track of whats been built in a State file, which can be put on remote storage such as S3 so multiple users or accounts can use & access it
- Everytime it plans and builds resources, it looks at your code changes vs what's already in the state file

34. How does CI/CD work, and why is it important?

- CI CD refers to a set of practices to deliver code changes reliabily and frequently
- CI refers to automatically building and testing your code as you commit changes to a shared repository in Git before it's merged into `main`. The goal is to promote early bug detection and a faster development cycle
- CD refers to automatically deploying the changes to some environment after your changes have been approved & merged into `main`. This reduces the risk of deployment issues, creates a faster time to market, and improves the overall quality of your software development environment

35. What is serverless computing, and what are its advantages and disadvantages?

- Serverless computing always has servers behind it, but it just means that the developers paying for it don't have to actually manage the infrastructure
- Typically a pay as you go model where you only pay for your execution time and resources used by your app
- Can trivially scale up & down on demand 
- Good for event driven workloads, microservice architectures, and variable workloads

### **Concurrency & Parallelism**
36. What are threads and processes, and how do they differ?

- Threads are an execution unit within a process
- A process is an independent execution with its own memory space

37.  What is a race condition, and how can you prevent it?

- A race condition occurs when multiple threads try to modify the same resource without proper synchronization

38. What are deadlocks, and how can they be avoided?

- Deadlock occurs when 2 or more threads/processes are waiting for each other to release resources

39. What is the difference between synchronous and asynchronous programming?

- Synchronous programming is running code that goes from left to right. It executes code in 1 direction and never stops until everything is completed.
- Asynchronous programming refers to code that can be started & stopped to go execute other code while it waits for something, such as a Network or Database call. Enables tasks to run concurrently

### **Language-Specific Questions (Python, Java, JavaScript, etc.)**
41. What is the difference between Python’s `deepcopy()` and `copy()`?

- `copy()` is a shallow copy, and share references with the data structure it's being copied from
- `deepcopy()` creates a new, genuine data structure with its own pointers

42. Explain Java’s garbage collection mechanism.

- Java has automatic memory management to reclaim unused objects
- When new objects are instantiated, memory is allocated on the heap
- Objects without references are considered garbage
- The garbage collector removes unreferenced objects to prevent memory leaks


43. What are closures in JavaScript, and why are they useful?

- Function that retains access to its outer scope variables even after the outer function has executed

44. What is TypeScript, and how does it improve JavaScript?

- Typescript adds types to JavaScript and effectively makes it a statically typed language
- These languages have multiple advantages and are generally preferrable when making critical applications

45.  How do you handle memory management in C++?

- Requires manual memory management via Stack Allocation or Heap Allocation


### **Testing & Debugging**
46. What are the different types of software testing (unit, integration, functional, regression)?

- Unit testing refers to testing specific pieces of code in isolation
- Integration testing refers to testing how your application works with external services or tools
- Functional testing refers to testing user-facing features (end-to-end) w/ tools like selenium, playwright etc
- Regression testing refers to testing an entire application after a big change to ensure the new code doesn't break functionality


47. What is mocking in unit testing, and why is it useful?

- Mocking is the practice of overriding some specific piece of code to return something else
- It's commonly used to mock out network or database calls, and instead return some static value
- This improves the performance of the test, makes it more consistent, removes the external dependency on the resource being mocked, and allows you to test exactly your code and not some external service
- Stub: Returns hardcoded responses.
  
48. How do you debug a memory leak in a running application?

- Look for common causes such as loading too much data, not closing database connections, leaving some process running etc
- Run a memory profiler on the code in question

49.  What is test-driven development (TDD)?

- Test driven development is the practice of writing tests before you actually write your code
- This ensures the code & applications you actually end up writing will be thoroughly tested
- You write your test to fail, then write just enough code for it to pass, then refactor for clarity

50. How can logging and monitoring help in debugging production issues?

- Logging can be used to identify where an application failed, when a specific piece of code was ran, or when a user ran into a specific bug
- Logging captures all of the information you need to understand what your application is doing
- Monitoring can capture high level statistics of how your servers are performing, what traffic looks like, and enables you to setup alerting based on various thresholds you want to set

## Data Engineering

---

### **1. Systems Design & Scalability**
1. How would you design a **real-time analytics platform** that processes millions of events per second?  

- first ask the business if they truly even require this, as this is significantly expensive and requires AAA software + data engineering talent to support
- prioritize low latency, scalability to handle spikes, fault tolerance to prevent data loss
- utilize kafka to serve as a distributed log that buffers and streams real time events
- utilize spark for real-time transformations and aggregations of the incoming data

2. You need to build a **data lake architecture** for a large e-commerce company. What storage formats, partitioning strategies, and processing frameworks would you use?  

- if using spark then can explore a lakehouse architecture w/ apache iceberg or delta lake. files would be stored in parquet w/ metadata files also associated with them. can partition out by tables, month, day, and put a query engine such as apache trino or aws athena on top of it to query 
- cons of this approach are its harder for data analysts, juniors, and analytics engineers to grok. you really need to make sure you have clear instructions & documentation for how to query the data and build on it


3. Given a **500TB dataset**, how would you optimize queries for **low-latency analytics**?  

- identify what we're running analytics for
- perform as much filtering as possible (only including what columns are needed, utilizing `WHERE` clause as much as possible)
- utilize a data warehouse like snowflake which can effectively partition the data so you only grab what's needed
- build ELT jobs to pre-compute the analytics aggregations in advance so stakeholders have a fast, efficient user experience


4. How would you design a **CDC (Change Data Capture) pipeline** for ingesting updates from a relational database into a data warehouse?  

- enable WAL on the relational database and setup debezium to read from it and capture all database changes
- setup kafka for debezium to send database changes to topics. 1 topic per table
- setup an s3 or warehouse sink if it's available in kafka to periodically dump new records from the table topics to the respective destination
    - if using warehouse sink, data will be dumped by the sink directly to the warewhouse
    - if using s3 sink, you can setup snowpipe or some other streaming ingestion tool to load the data from s3 to warehouse as the files land
- you now have streaming data in snowflake. but still need to run transformations or other pipelines afterwards on a continuous basis to enrich it for reporting and analytics

5. You need to handle **slowly changing dimensions (SCD Type 2)** in a distributed environment. How would you implement this efficiently?  

- create `valid_from` and `valid_to` columns on the tables you want to enable scd2 on
- create `is_enabled` column based on the date set to `valid_to` to clearly label the active records
- insert a new row for every record change, and update the `valid_to` and `is_enabled` as needed
---

### **2. SQL & Optimization**
6. Given the following query, how would you optimize it for **better performance in Redshift/Snowflake/BigQuery**?  

  ```sql
  SELECT user_id, COUNT(*) 
  FROM user_events 
  WHERE event_type = 'purchase' 
  GROUP BY user_id 
  HAVING COUNT(*) > 10;
  ```

- There's not much to optimize here.
- Suggestion is just "Redshift Distkey or Snowflake cluster by user_id" lmfao
  
7. How would you **identify and fix slow queries** in a distributed data warehouse?  

- Look at the Query Profile for it and see the most expensive steps and if there's any disk spillage
- Check for `row_number()` type window functions or join explosions
- Perform more filtering if needed, remove unused columns


8. What are the trade-offs between using **partitioning, and indexing** in a big data system?  

- Partitioning splits up the data to help filter it and enable faster scans
- Indexing enables fast lookups, slows inserts updates deletes because it has to maintain the index

9. Suppose you have a **skewed join** in a large Spark job. How would you optimize it?  

- Use broadcast tables to avoid shuffle operations
- Salt technique where you add a random string to what you're grouping by to evenly distribute the load
- Spark distributes the workload evenly, avoiding a single overloaded partition.


``` python

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, lit, rand, monotonically_increasing_id

spark = SparkSession.builder.appName("SaltingExample").getOrCreate()

# Large transactions table (skewed on customer_id = 123)
transactions = spark.createDataFrame([
    (1, 123, 100), (2, 123, 200), (3, 123, 300),  # Highly skewed customer_id = 123
    (4, 456, 400), (5, 789, 500)
], ["transaction_id", "customer_id", "amount"])

# Smaller dimension table
customers = spark.createDataFrame([
    (123, "Alice"), (456, "Bob"), (789, "Charlie")
], ["customer_id", "customer_name"])

NUM_SALTS = 5  # Number of salt buckets (tune based on skew severity)

# add salt to the transactions table with value between 0 -4
transactions_salted = transactions.withColumn("salt", (monotonically_increasing_id() % NUM_SALTS))

# Duplicate small table rows for each salt value
customers_salted = customers.crossJoin(spark.range(NUM_SALTS).withColumnRenamed("id", "salt"))

joined_df = transactions_salted.join(
    customers_salted,
    on=["customer_id", "salt"],  # Now joins on both customer_id & salt
    how="inner"
)

joined_df.show()

# can also go the hash route to ensure the same key always gets the same salt
from pyspark.sql.functions import hash

transactions_salted = transactions.withColumn("salt", hash(col("customer_id")) % NUM_SALTS)
customers_salted = customers.withColumn("salt", hash(col("customer_id")) % NUM_SALTS)
```

10. Given two large tables (1 billion+ rows), one transactional and one dimensional, which **join strategy** would you use in Snowflake/Redshift?  \

- Broadcast joins are helpful when data is small <10 GB
- Hash join used for distributed joins in snowflake + redshift
- merge join used when both tables are sorted

---

### **3. Distributed Computing (Spark, Kafka, Airflow)**
11. How does **data shuffling** work in Spark, and how can you minimize it?  

- Shuffling is when a join, merge, or sort is requested and requires all data partitions to be re-distributed across all spark worker nodes
- This requires all data to be serialized, sent over the network, and deserialized
- Involves using Disk IO if data doesnt fit into memory
- Ways around it are things like broadcast joins, where you load a table to memory for all spark worker nodes to avoid the shuffle operation from happening
- Use narrow transformations like filter etc that dont require shuffle operations

12. Explain how **Kafka handles message durability** and how you’d design a **high-throughput Kafka consumer**.  

- Kafka is a log-based distributed store, meaning it stores messages in topics for x amount of hours or days
- These topics can be replicated across brokers so messages arent lost if 1 of them fails
- Consumers pull data from the topics at their own pace, and keep track of where they left off with their own offset
- A high throughput Kafka consumer can periodically poll a topic for new data, bring the new data into memory, perform some operation on it, and then save it someplace else like S3

13. How would you implement **exactly-once processing** in Kafka and Spark?  

- enable idempotency on kafka w/ `enable.idempotence=true` so duplicate messages are ignored

14. What’s the difference between **Spark’s narrow and wide transformations**, and how does it impact performance?  

- narrow transformations are operations that dont require a shuffle operation, such as filtering. performance impact is minimal
- wide transformations are operations that require a shuffle operation & moving data between partitions, like a group by count. this impacts performance because data has to be re-distributed across all worker nodes, slowing performance.

15. How do you handle **backfilling** data in an Airflow DAG without rerunning everything?  

- Parameterize Airflow DAG to allow `run_date` or `start_date` and `end_date` variables to be set.
- You can then manually run the DAG, pass in the dates you want to run for, and have it only pull data for that specific date range
- Then save it to S3 and merge it to warehouse to ensure you're not introducing duplicate data and making the pipeline idempotent

---

### **4. Data Modeling & Warehousing**
16. How would you design a **dimensional model** for a rideshare company's trip data?  

- tables: `dim_riders`, `dim_locations`, `dim_vehicles`, `dim_drivers` `fact_trips`
- `fact_trips` has foreign keys for things like `rider_id`, `location_id`, `vehicle_id`, `driver_id`,
- can then make aggregations very easily, group by any of the ID columns, look up `sum(fare_amount)` or how many ride transactions occurred during a certain timeframe or around a certain location

17. What are the trade-offs between **Star Schema vs. Snowflake Schema** in a data warehouse?  

- Star Schema things are more denormalized 
    - `dim_location(city, state, country)`
- Snowflake schema your dims can reference other dims, more joins and relationships are required. better for hierarchies
    - `dim_city(city_id, city_name, state_id), dim_state(state_id, state_name, country_id)`

18. How would you handle **schema evolution** in a production environment?  

- instead of deleting columns, soft delete them by adding nulls
- can utilize versioned tables instead of altering existing tables
- utilize functionality on the warehouse itself to automatically add new columns it finds in data files it's loading

19. Suppose your data warehouse is **growing too fast**. What techniques would you use to **reduce storage costs** without affecting query performance?  

- add or utilize partitioning to automatically prune data that isnt needed for the query
- add filters to all existing queries to only look at recent data or to filter down based on new column values or something
- archive data older than x years to some other system such as s3

20. Explain how you’d model **multi-tenancy** in a cloud data warehouse (e.g., Snowflake, BigQuery).  

- can separate out either by schemas or by database, only give permissions to whichever schemas or databases are needed by the user so they cant see sensitive information in another database or schema

---

### **5. Cloud & Data Pipelines (AWS, GCP, Terraform, CI/CD)**
21. How would you design a **serverless ETL pipeline** using AWS Lambda, S3, and Glue?  

- raw data at `s3://my-bucket/raw-data/`
- pull that data & perform data transformation or enrichment process
- save processed data to `s3://-my-bucket/processed-data/`

22. Explain how you’d implement **incremental loading** in a BigQuery/Snowflake pipeline.  

- using timestamps to only load new or changed data, `insert into target from select * from source where created_at > (select max(created_at from source))`
- these can be set either by the source system, or if you're generating `record_loaded_at` timestamps within the warehouse during your ingestion process

23. How do you ensure **data quality checks** in an Airflow pipeline?  

- can check things like # of records pulled, # of records in a table before & after ingestion occurs, and send alerts out if these row count checks dont match your expectations

25. How would you **secure data pipelines** when working with PII in a cloud environment?  

- can hash PII data, but this introduces issues
- can implement row-level masking policies so specific users can only see PII data if they're admins or have permission
- this enables the data to be stored accurately in the database, but means that the PII data is protected from most people for viewing


``` sql
CREATE MASKING POLICY mask_email
AS (val STRING) RETURNS STRING ->
CASE WHEN CURRENT_ROLE() = 'analyst' THEN '*****@email.com' ELSE val END;
```