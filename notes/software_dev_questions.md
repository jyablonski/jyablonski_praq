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
