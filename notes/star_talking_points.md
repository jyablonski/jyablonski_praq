# Intro
Hi I'm Jacob.  I'm a Data Engineer with about 3 years experience.  Currently based out of Chicago but originally from Southern California, looking to move back which is why I'm kind of on the job hunt right now.  

Been with Campspot for almost 2 years as a Data Engineer on the Data Platform team.  Campspot primarily provides Campground Management Software to Parks to help them manage their day to day operations and also offers a Marketplace App for Customers like you or i to make bookings at some of these Campgrounds.  My role has just been doing everything I can to provide a stable & efficient reporting experience for our parks and providing them with the data they need to understand their business & make more data-driven decisions.  I've owned quite a bit since I've been here: managed the Snowflake Data Warehouse, introduced Airflow, dbt, and Terraform Repos for our Data Platform Work.  Implemented CI / CD for that new tooling & managed Releases for those Repos.  Had my hands in a couple new product offerings, some of which for our Enterprise Clients which is where we get the big bucks.  Happy to go into more detail about any of those.

In terms of the job hunt I plan to move back to California early August and I don't think Campspot will be able to offer employment there. I also feel ready for a bit of change of scenery for a couple different reasons, we can get into that if you want. It's not the best market right now but i still think there are good opportunities out there and i'd really prefer to find a long term spot for myself where i can grow for the next 3-4+ years in a tech stack i want to work in and a situation im a bit more comfortable with.  

Outside of that, I'm a big sports guy NBA fan as I'm sure you can tell, also into video games & computers stuff like that. Used to be big into pool & beach days and being outside, not so much since I've been in Chicago, but hoping to get back to that once I'm able to move back.

Primary reasons for wanting to leave include:
- It's a very heavy Java Backend company, like 98% Java. It's not my style, I don't know Java, I don't want to switch, it doesnt make a lot of sense from a DE perspective.  In the beginning there was a ton of data warehouse and airflow work to do to get things running in a stable and performant way but nowadays im really feeling it just not be a great fit for either.
- Not as much new emerging work to tackle.  Not learning that much from anybody because all of our microservices are in Java.  A lot of the Data Platform Side Snowflake, AWS Infra, Airflow Data Ingestion / Export stuff has been re-built and stabilized so there's not much else.
- Kinda a weird one but i don't feel like i see myself having much control or influence moving forward here.  there's some bad workflows, bad practices, we've added new things and the team just isnt picking up on them.  it's a weird dynamic for me to be my age. im not a manager or a team lead or a staff engineer but im seeing senior engineers just continue the bad habits of the company and it's just frustrating.  

## What to Use Data For
Companies use data to make more informed decisions and help them gain a competitive advantage.  Every company, business, and industry uses or can use data in some way for the following purpoess:

1. Business Intelligence for things like past performance, current trends, future predictions to make more informed business decisions
2. Customer Insights, figuring out their behavior & preferences to tune your product or service appropriately, analyzing user churn etc
3. Marketing - targeting customer segments, personalizing campaigns, trying to acquire new leads or market to existing customers as efficiently as possible

Data has only gotten bigger and bigger in the last 20 years as the internet boom came around and more companies became digital.  It will continue to grow, for better or worse.
- Lots of apps now are offering that "personalized ads" popup based on other app usage on your phone
- More digital products
- More ways of tracking user activity and interest with the goal of ultimately using those metrics and that data to market more to them

# STAR
The STAR method is a structured technique used in job interviews to effectively answer behavioral interview questions. The acronym "STAR" stands for Situation, Task, Action, and Result. Here's what each component entails:

1. **Situation**: Begin by describing the context or situation you were in. Provide enough detail for the interviewer to understand the background of your story.

2. **Task**: Explain the specific task or challenge you were facing in that situation. This helps to clarify what you were responsible for or what goal you were trying to achieve.

3. **Action**: Detail the actions you took to address the task or challenge. Focus on what you did rather than what your team or others did. Be specific about the steps you took and the skills you applied.

4. **Result**: Finally, describe the outcome of your actions. What happened as a result of your efforts? This could include quantifiable achievements, lessons learned, or the impact of your actions on the situation.

By using the STAR method, you can provide structured and concise responses that showcase your abilities and experiences in a clear and organized manner. It helps interviewers understand how you approach problems, the actions you take, and the results you achieve, providing them with concrete examples of your skills and competencies.


## Data Warehouse at Campspot
**Situation**
   1. When I joined Campspot we were currently using Redshift which had been around for about ~3 years, and it was a mess.
   2. Permissions were all over the place, performance wasn't great, JSON support was lacking etc.
   3. Ultimately everybody I talked to complained about it for one reason or another and it seemed like a good opportunity to maybe start fresh.

**Task**
   1. Both Data Managers at the time had been interested in Snowflake for awhile but never pulled the trigger, so we did a POC of Snowflake to figure out whether it better fit our needs.
   2. I was tasked with testing out data ingestion, assessing costs, figuring out permissions etc.  Basically seeing if Snowflake did all the things Redshift did but better.
   3. About a month into my time w/ the company we started that project.

**Action**
   1. Implemented Batch & Stream Pipelines POCs to load data from all our internal databases to the Warehouse
   2. Did some Airflow + dbt testing that connected to the Warehouse and ingested & transformed the data
   3. Built out Snowflake Infra manually, but quickly realized this would turn into a mess like Redshift did
   4. Developed Custom Terraform Modules to build all Snowflake Infrastructure
      1. Databases
      2. Schemas
      3. Roles
      4. Users
      5. Permissions

**Result**
   1. Snowflake performed much better, met our needs well
   2. Integrated it with our Campspot Analytics Product Offering; performance was much improved and it auto scaled based on the usage.
   3. Managed Costs extremely well, had an internal dashboard we used to track Warehouse Usage + monitor costs on a weekly / monthly basis
   4. Terraform Modules worked flawlessly, will use this moving forward for any database infrastructure management

## Streaming
**Situation**
   1. We originally just did Batch once-a-day Pipelines to ingest data into the Warehouse
   2. While this worked, there was a growing need from both customers and internal stakeholders for faster data refreshes
   3. There was a noticeable gap here between what we offered and what our customers wanted.

**Task**
   1. Had to figure out a way to enable faster data refreshes into the Warehouse while managing cost

**Action**
   1. Explored & Implemented Debezium + Apache Kafka on AWS MSK to tap into our database and read all inserts, updates, and deletes.
   2. Wrote these to S3 where they got picked up by Snowpipe and ingested into Snowflake
   3. Airflow DAG to upsert data from the Landing Tables to the Production tables every 1 hr; could be moved up to every 20 or 30 minutes

**Result**  
   1. Our most important tables were now being streamed to the Warehouse via a different pipeline + process
   2. No data disruptions or downtime from the increased complexity
   3. Estimated the Cost going into the project and it matched what we ended up paying

## Data Lake Product Offering
**Situation**
   1. One of our biggest Park Groups wanted to replace an aging ETL Service we provided them with a new Data Lake Product so that they can ingest data themselves and build out their own reporting off of it.
   2. Dealt with some ambiguous requirements, had to make some judgement calls along the way with how I believed this should be implemented and what they would be comfortable with.

**Task**
   1. Develop a Data Lake Product Offering for this Park Group, but also make it modular enough so that we could extend it to other partners in the future

**Action**
   1. Used Snowflake Unload Functionality so that we could pull data from our Warehouse and send it off to S3 into files based on each table and partitioned it by date.
   2. Build out functionality for full backfills if the customer ever requests it.
   3. Ensured we're only sending them their own data by filtering on Organization ID and writing various checks around this.

**Result**  
   1. Managed cost well; costs < $1 for us to perform this on a daily basis but it's something we can charge parks much more than that.
   2. Easy to manage, little to no downtime because of how stable it is
   3. Learned how to deal with ambiguous requirements, while also being given the autonomy and independence to build the solution out in a future proof and extendable way.


## Resume
- Led integration effort to introduce foundational tooling to our data tech stack including Airflow, dbt, Kafka, and Snowflake to address scalability issues & gain flexibility as the company continues to grow.
  - When I joined there was no Version Control for our Data Pipelines, no CI CD, kinda things you'd consider red flags.  They had just signed up with Astronomer and were deploying things locally so I stepped in and helped introduce a number of best practices to help our ability to deliver software better.  This is something I knew how to do which enabled me to make an impact on day 1.
- Implemented a CDC pipeline using Debezium & Apache Kafka to stream data from our application databases into the Data Warehouse, enabling near real-time analytics for our customers.
  - See STAR
- Utilized custom Terraform modules to build 100% of Data Warehouse Infrastructure & permissions as well as to deploy various AWS resources while operating in a multi-account cloud environment.
  - This was a big one that I want to carry with me in every Database Environment I ever work on.
  - Databases, Schemas, Users, Roles, and Permissions are created in Version Control using these Modules.  Permissions for current and future resources are set from day 1.
  - It allows for a very consistent and reliable database usage experience.
  - Even for Postgres or MySQL I'd want to do this.
  - Continue using a tool like Liquibase for Table Migrations and things like that.
  - Inspired from my Job as a Data Analyst where they did this with Snowflake; I like picking up good habits + workflows and incorporating them into my skillset.
- Built & maintained a Data Lake product offering which moved customer data into our Enterprise client’s AWS S3 & Azure Blob Storage buckets on a daily cadence to meet their business requirements.
  - We serve tons of different ranges of park groups, some mom & pops, some park groups with 100+ different campgrounds they manage.  These are the whales that bring in the most revenue that we want to provide services for.
  - They had a growing need to ingest data into their own ecosystem; they have large business portfolios so while we offer this suite of reports, they don't actually need the help they want the raw data to build out their own stuff.
  - This data lake project involved querying our raw & transformed tables, filtering it down to their organization data, then unloading it into their S3 Buckets.  
  - Partitioned by day, orchestrated with Airflow, automatic Backfill Functionality available if they ever requested it.
  - Cool to see us build a product for a specific client in mind, but also be able to extend it to other park groups & customers if needed.
- Consolidated & optimized existing reporting patterns by moving legacy ETL jobs to the Data Warehouse using dbt, which led to a 10-15x performance improvement for our customers when pulling reports. 
  - An unbelievable amount of ETL was just being done in our MySQL Database.
  - This is bad for a number of reasons; heavy ETL on the transactional database negatively impacts performance for the application, backfills are tricky, performance is bad, scaling these ETL jobs is difficult, they were triggered from Node JS off of AWS Batch jobs like it was wild stuff.
  - From day 1 I pushed for us to move literally all of this off of the MySQL Database and into the Data Warehouse
  - We did some of it but not everything
  - 40,000 line Node JS Files
  - Just poor Engineering Management from day 1 to allow this to happen and for it to continue.  Years of technical debt that isn't going away anytime soon.
- Created new documentation, incident response runbooks, and architecture diagrams to preserve knowledge and ultimately improve our ability to continue delivering & maintaining our software.
  - This might seem low impact and not that impressive but imo it's probably one of the most important bullets on the resume
  - It's so valuable having a simple Diagram to show how an Application or Workflow works, or to have a document to guide you on what to do when an incident comes up.
  - Helps with onboarding to get new people up to speed on how things work, is greatly appreciated during times of incident response, helps to establish order & structure
  - These are important to a business to keep the software running and to keep the engineers working on that software up to speed on how things work so that they can continue maintaining it over time as people come & go.
  - Tribal knowledge is a no-no.

## Personal NBA Project
- Built an end-to-end data pipeline which sources data from multiple sites + APIs to power a Web Dashboard on the current NBA Season, displaying metrics, trends, fan sentiment, and other stats.
- Used AWS ECS to run the containerized Ingestion Script daily which scrapes the data, validates the schema, and stores it to an RDS PostgreSQL Database as well S3 for historical re-ingestion if needed.
- Utilized dbt to execute transformations & model the source data into enriched tables, and used SQLFluff and Pre-Commit Hooks to automatically manage SQL formatting & syntax.
- Implemented an ML pipeline using scikit-learn to predict team win probability percentages for upcoming games, and built UI components to offer betting suggestions based on odds value.
  - Interesting use case, made sense for the project, took the initiative to build out some kind of pipeline to implement it into the project.
  - I'm not a Data Scientist, I don't have a Masters Degree in Mathematics or Data Science.  The Model isn't perfect but you can get the idea of where it fits in.
  - I did just enough here to figure out that this isn't my area of expertise.
  - Would love to pair with Data Scientists with the future and help get them what they need to do their experiementation and build models etc but I do not want to be building ML Models.  It's not for me.
- Built a REST API to publicly expose the transformed data, and implemented OpenTelemetry for traffic & trace monitoring which gets served over Honeycomb where metrics can be viewed & alerted on.
  - Originally was just going to be a REST API to expose endpoints to query the Data, ended up creating some Web Forms and User Management Pages on there to turn it into an amateur Web App
  - Also made a GraphQL API first idea was to compare GraphQL vs REST API And see what I liked more. 
    - Caching is kinda just a different problem than you're used to solving becasue you're not dealing with endpoints you're dealing with POST Requests etc.  So things like that pop up.
- Integrated separate CI / CD workflows across all project codebases to test changes and release new deployments after PR merges exclusively through GitHub Actions.
   - This looks different across different Software Languages & the Application
   - For Terraform the Test Pipeline runs Terraform Plan, the Deploy Pipeline runs Terraform Apply
   - For dbt I build my entire project in a Docker Postgres Database with Bootstrap Data, and the Deploy Pipeline just builds a Docker Image of my Project


### Interview Talking Points
1. Python
   1. Main Packages:
      1. Pandas
      2. Boto3
      3. SQLAlchemy
      4. Requests
      5. Pytest
      6. Polars
      7. PySpark 
      8. Airflow
   2. Used Python since about Spring 2021
   3. Async Code
      1. Special Code where you tell Python to go run other stuff while waiting for certain I/O bound tasks like network requests or disk read/writes etc.
      2. Asynchronously as opposed to synchronously where you're waiting for each task to complete.
      3. Haven't needed to build anything custom where stuff like this is that necessary.
2. Spark
   1. Haven't used it in Production or in a Workplace Setting, so if you guys are big on Spark you're probably thinking "oh jeez here we go that's strike 1" or something which seems reasonable in all honesty given the complexity of the tool.  
   2. I recognize its importance and I've tinkered around in a pretty considerable amount of areas with it just locally.  
      1. Have some scripts with general transformation logic along with some Spark SQL stuff.
      2. Setup a Docker Image for it, a couple tests and some GitHub Actions stuff to run those tests on PRs using the Docker Image. 
      3. Have Iceberg, Delta Lake Examples where I'm reading & writing to those. 
      4. Have a Docker Compose Example which spins up Kafka, Cassandra, and a Python Script which generates data and writes it to Kafka.  Then I connect to Kafka and set up a streaming client in PySpark to read from a Topic and stream the changes in as they come.  And then Cassandra ,,, just because.  Why not, I heard about it a few times and was interested.  Don't think I'll ever use it.  Distributed NoSQL Warehouse, only for like .0001% of use cases like FAANG level data volume or something.
      5. Try to study up with the internals as well like the Spark Cluster Manager, Worker Nodes, Partitions, Shuffles, Lazy Evaluation, Narrow vs Wide Transformations etc
         1. Narrow Transformations are operations where each input partition contributes to only 1 output partition
            1. Filter, Map(func) to apply a function, Union etc.
         2. Wide Transformations are operations multiple partititons are needed to compute the output partition and involve data shuffling or data redistribution across the cluster which incurs overhead.
            1. Group by, Order by, Joins etc.
         3. Partition - logicial division of data in a RDD or Dataframe.
         4. Lazy Evaluation - Transformations are not immediately executed, it delays them and figures out the most optimal execution path to take before you call an operation like `.collect()` or something on a Dataframe or RDD.
         5. Spark Cluster Manager - Allocates resources and coordinates execution of spark apps on the cluster.  Responsible for launching and monitoring spark executors on worker nodes, managing resources, and handling task scheduling.
         6. Spark Executor - Worker processes responsible for executing tasks.  They run on worker nodes and perform the actual data processing tasks of executing transformations on dataframes or RDDs.  Managed by the Cluster Manager.
         7. Spark Driver - Main control process for a spark app.  Runs the user code, creates RDDs, defines transformations, and orchestrates execution of the app.  Communicates with the Cluster Manager to request resources and coordinate execution of tasks. 
         8. Shuffles - Shuffles are the process of redistributing data acros partitions during certain operations such as wide transformations.  Lots of overhead because of network i/o and disk i/o here. 
            1. Moves data between partitions across the cluster to ensure records are co-located on the same executor.  This involves serialization/deserialization of data and network communication between nodes.
         9. Partition Pruining - optimization technique to reduce the amount of data processed during query exeuction by removing unneccessary partitions based on query predicates.
         10. Predicate Pushdown - optimization technique that pushes query predicates (filters) down to the source, so they can be applied early during data retrieval instead of doing it all in memory after the data has already been fetched.
         11. Broadcast join - optimization technique to improve performance of joins by replicating the table to be joined to all executors in the cluster to avoid shuffling or redistributing data.
   3. 
3. Polars
   1. Seems like a drop-in replacement for Pandas, just an immediate performance improvement and seems like the gold-standard for data frames in python moving foward.
      1. Which makes sense.  Pandas came first, the author of Pandas has a whole blog post where he admits it's not great in certain areas, we've had over 15+ years to make an improvement now.
      2. Polars gets to build on everything Pandas already did but with dramatic performance and efficiency improvement.
   2. Only downside is it only runs on 1 machine, so if you run into OOM issues you either have to start chunking out your data or you have to move to a distributed computing platform like Spark or a Data Warehouse.
   3. Lazy Evaluation, will wait to calculate and figure out the most optimal execution path for you.
4. Airflow
   1. Data Orchestration Tool to build complex workflows and data pipelines
   2. Used it since Summer 2021
   3. Used it for both running Python Code in Tasks in Airflow or the DAG itself, and also used it to just orchestrate containers that run in something like ECS.  Purely as an orchestration tool and not to actually run the code on the worker nodes.
   4. Setup Slack + PagerDuty Alerting, added some basic scheduling and environment checking functions so that our schedules are turned off in non staging + prod environments.  Added various tests at a DAG-level for those so we can check that those are being utilized.
5. Terraform
   1. Infrastructure as code, without it you have to build resources via the Console or the CLI which is a complete mess and not reproducible.
   2. Built my own Modules for things that kept coming up such as S3 Buckets, Python Lambda Functions, IAM Roles for GitHub Actions, Snowflake etc.
   3. Also utilize Terragrunt at work which is kind of a fancy wrapper around Terraform to help enable DRY Code.
6. AWS
   1. Been using AWS since Spring 2021, when I added RDS for my NBA Project.
   2. Built resources for about 4 months before I got hired as an Analyst and saw they were using Terraform, so I swapped to that.
   3. Honestly I've worked w/ pretty much most relevant resources:
      1. S3
      2. IAM
      3. Lambda
      4. ECS
      5. Batch
      6. RDS
      7. DMS
   4. Limited exposure to Glue + EMR
   5. Would love to chat more in whichever areas make sense here.
7. Debezium
   1. Change Data Capture Tool written in Java to capture database changes and stream them to message brokers or data streaming platforms.
   2. Needed faster data refreshes and also better consistency to track things like delete statements, which isn't possible with traditional query-based approaches.
   3. Have an entire Repo of mine w/ a Docker Compose example with MySQL and Postgres which I used for thorough testing for both Databases.
8. Kafka
   1. Honestly didn't use it extensively a whole lot, just enough
   2. The concept is pretty straight forward; Pub Sub System where you store messages into Topics and then Consumers can independently read from those Topics to process messages and do various operations with them.
   3. Distributed System so you can have multiple Brokers in the event of failover which enables high availability, at the price of cost.
   4. Used S3 Sink to dump messages from the Topics to S3 on a specified cadence.
9.  Liquibase
   1. Database Schema Change Management Tool to automate and track database schema changes.
   2. Enables database versioning, continuous integration, and smooth deployment processes.
   3. Rollbacks if disaster recovery is needed.
   4. Pretty standard stuff, something I'd like to continue using for Transactional Databases moving forward.
10. GitHub Actions
   1. Platform to Automate Workflows in GitHub Repositories
   2. Enables you to build CI CD Pipelines
      1. Continuous Integration - Testing your changes, checking for regressions, make sure you're not about to deploy something that doesn't work so that the codebase always remains in a working state
      2. Continuous Deployment
11. Kimball Data Modeling
    1.  Data Modeling technique which uses concept of Fact Tables to logically separate your data into the quantifiable data from business events or transactions, and Dim Tables for their more static, descriptive data and additional details about the business entities in these events.
        1.  Fact - Sales, Orders etc with a date or timestamp
        2.  Dimension - Product, Store, Customer etc.
    2.  Star Schema - Multi-dimensional data model used to organize data into a database. 
        1.  Separate your data into individual tables and then join them together
        2.  Foreign Key relationships which allow you to join tables together - Foreign Key in 1 table might be the Primary Key in another table.
    3.  Normalization - organizing data to minimize redundancy and reduce data duplication, thereby improving data integrity and performance for non-reporting Applications.
        1.  Various 1st Normal Form, Boyce-Codd etc.  I don't remember them off the top of my head.
        2.  Main Idea is to reduce data duplication and improve data integrity at all costs.
    4.  Denormalization - adding redundant columns to dimensional tables to make querying and working with the data faster and easier.
        1.  Often used when read performance is a priority, such as in data warehousing + reporting.
        2.  Reduces the need for joins which improves query execution times.
        3.  Leads to larger storage costs, more data redundancy, and potential data inconsistency if not properly managed.
    5.  My dbt project doesn't use kimball modeling but if i had to do it over again i probably absolutely would go that route.  both for the experience and also just the structure of things.  it's very easy to onboard people onto projects like that if they know exactly where to go to find the data.
12. Database Administration
    1.  Did a little bit of this, mainly MySQL Maintenance for our primary Application Database.
    2.  Worked with developers to figure out various MySQL Parameters we needed to set for various functionality we were working on such as Logical Replication and Binlog Retention Time for our Streaming Applications.
    3.  Did a little bit of Database Health Reporting as well but not a whole lot; we had over 400+ tables, tons of indexes, it's a lot to manage.
    4.  Index - Database Structure that improves speed of select queries on a database tables.  You apply it on 1 or more columns and under the hood it stores a sorted copy of their data using pointers to the corresponding rows, and then it uses that for select queries. But it costs storage space and leads to decreased insert, update, delete performance because it needs to get updated after data changes.  Add them when you know query patterns.
13. Software Development Lifecycle
    1.  Plan
        1.  Define purpose & goal of the Project
        2.  Requirements gathering from Stakeholders and Management
        3.  Project Planning, figure out a timeline and deadline
        4.  Assemble teams, hire for positions etc.
        5.  Assess Costs + Revenue Projections
    2.  Design
        1.  Define the overall architecture for the software.  
        2.  Figure out Tooling, Data Models, various Microservices, Permissions etc. 
        3.  Seeing if your technical estimates match the budget that the business provided you with
    3.  Build
        1.  Implement the proposed Software
    4.  Test
        1.  Test the Software, via unit / integration tests as well as full on in a Staging or Non-prod Environment as well as QA
    5.  Deploy
        1.  Deploy the Software
        2.  Release it to customers
        3.  Start generating revenue off of it
    6.  Monitor
        1.  Monitor those changes, observe before & after, alert on any metrics that aren't meeting expectations.
14. Software Development Best Practices
    1.  Version Control
    2.  Testing
        1.  Unit Testing
            1.  Any individual piece of code like a function or class
            2.  Make assertions on if it produces the correct output given specific inputs, or if it raises the correct errors etc
        2.  Integration Testing
            1.  Anything that's touching an external service or network endpoint like a Database, HTTP Endpoint etc
            2.  I mock everything using fixtures and use Docker for the Postgres + Source Table bits.  For my purposes this works, but for other applications you may have valid use cases for wanting to actually hit real external services or network endpoints during integration testing.
        3.  Data Quality Testing
            1.  dbt Tests
            2.  Enables confidence in your models + transformations
            3.  Use these extensively but they are not Unit + Integration Tests and i still think that's a hole in dbt that's not fully fleshed out yet, although people are working on it and there are active discussions on how to implement that stuff.
        4.  Pre Commit Hooks for Linter + Code Formatter
            1.  SQLFluff for SQL, Black + Ruff for Python
            2.  Unbelievable how night & day the difference was for SQL here, much more readable and maintainable and it's a very low barrier to entry.
    3.  CI CD
        1.  Trunk Based Development - the Codebase should be in a deployable state at all times.
        2.  Small Feature branches into `main`
        3.  CI Test Pipeline runs on every PR Commit to make sure it integrates smoothly with the latest version of the `main` branch
        4.  Feature Flags to manage releases of new features and pullbacks if necesary
        5.  Add Lots of small changes continuously vs larger infrequent releases where more can go wrong
        6.  Smaller Code Review, automated labeling with GitHub Actions and `CODEOWNERS`
        7.  Scales well for both small + large teams.
        8.  I use GitHub Actions.  GitLab CI seems to be very equivalent.

### Data Lingo
Can use data for:
- Business Reporting.  Dashboards & reports on various performance metrics such as daily / weekly / monthly sales, revenue, profit.
- Gain a deeper understanding of customer insight.  figure out their behavior & preferences, then leverage that to create customized marketing campaigns + product recommendations.
- Optimize existing business patterns to achieve better operational efficiency.  Analyze data related to supply chain management, inventory, resource allocations to identify bottlenecks, streamline workflows etc.
- Predictive analytics and forecasting to be prepared for future trends and outcomes based on historical data.  anticipate market trends + customer demand.

Main ideas are:
- Report on how the business is doing *today*
  - Can also compare it to how the business is performing relative to the *past*, or how it might do in the *future*
- Understand customers better to figure out their preferences and sell more to them.
- Optimize existing patterns to gain efficiency in various areas
- Predict how the business might perform under xyz conditions

[Reddit Link](https://www.reddit.com/r/cscareerquestions/comments/4ce2s3/resource_interview_questions_my_massive/)

Interview Questions
1. What kinds of opportunities for impact will I have in this role?
   1. Is it delivering new product features, is it fixing existing problems, is it re-architecting some major workflow or process?
2. What's the engineering culture like?
   1. DevOps as a Culture vs DevOps as a Service
   2. Can devs write their own infra, how much autonomy is there
   3. What's the Code Review and Branching Strategy look like
3. What are some of the biggest unsolved problems right now?
4. Can you describe your biggest mistake at the company so far?
   1. Did you break prod, did you go with the wrong solution, pick a bad vendor etc.
5. Is there on-call?  What's the rotation like?  How often do incidents happen?
6. What are the "stress points" times of the year for the Company?
   1. Is it end of Month, is it a certain quarter, is it the holiday season, when is business at its peak and you're on high alert to deliver?
7. What has been the most satisfying project you've worked on at this Company?

![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/b2846124-c45c-430c-abb8-7635d8db5df7)

What i bring to the table:

- I bring proven experience and sound judgement on how to build these apps & products in terms of cost, architecture, design etc.
- i can work independently and also thrive in team environments, there's solid workflows and ideas i can bring to the table
- i want to learn, i want to pickup new skills & techniques from those around me. And I wanna give it back as well and improve workflows + processes where I can




calm
[Article](https://www.forbes.com/health/mind/calm-app-review/)
- looks like you offer exercises for people to help practice mindfulness, lower stress + anxiety, relax, and achieve an overall more focused and calm self.
- the app caters to basically everybody target-audience wise, i think this something that could be beneficial to 100% of people. 
- it is interesting it's an app on your phone. ive never worked with a primarily ios based product before so that sounds interesting
- tons of popups to sign up which i dont know if i like being spammed to go spend $15 on something taht i havent even gotten to try out yet.  but the trial is there, you can signup and get elevated access without actually paying anything
- tons of interesting data here:
  - user retention - are users signing up for premium staying on?  if they're leaving, why are they leaving and not coming back?
  - what exercises, audios, or content are most popular / receive the most engagement?  which ones are the worst?  how + why do people gravitate to certain content more than others.
  - everything about your product revolves around providing custom personalized content to users based on their wants, interests, and history so id imagine ML 
  - ultimately that's what we use the data for.  figure out what's working and what's not, scrap the bad stuff, iterate on the good stuff, have hard data evidence to backup whatever business strategy we want to 
- what are narrator / authors?  is that content you pull from 3rd party?  are those people directly working with you to produce content on there?  is there a rev sharing going on there?



- for me the conversation has to start at around ~ $133k - 145k is what im aiming for, anything below that just does not make sense for me.  so if we can get there then great, i'd be very excited to continue this interview process and explore this opportunity more to see if it's the right fit for both of us.  and if that's out of the range then all good, best of luck in filling the position but i'd have to respectfully withdraw from continuing further here.  so ya just let me know where you're at, no hard feelingss.

What have I done to show senior capabilities:

- Ownership over Data Products.  Airflow, Batch + Streaming Pipelines, our dbt project, Snowflake.  I'm the go-to person for 100% of any issues that arise from those domains whether it's in production or in the CI pipeline or in our deploy process
- Introduced new tooling into our Data Platform Architecture to help meet the team & companies' needs.  Created repos for Airflow + dbt, incorporated Terraform into some of our Data Platform Infra, and setup Debezium + MSK to stream data from our OLTP Databases into Snowflake
- Definitely have a feeling that I'm the "adult in the room" for a lot of design, infra, and cost considerations.  I'm very familiar with how much our tooling costs and our cloud infra and permissioning works.
  - One example is when a Batch Pipeline that ran in MySQL broke, it was running for over 2+ hrs a day to insert data into a very basic occupancy table. The team's first consideration is to go fix that data in MySQL and update the code that runs it, but that involves maintenance windows, staging testing, multi-day backfills, and a code fix to some very ugly Node JS and SQL code in our monolith database where we only do releases a few times a month.  What should be a simple fix turns into weeks of dev time which costs us. The solution is to just re-write it in Snowflake.
- Obviously biased but i feel like i have good intuition and a solid understanding for most things that fall under the data engineering or data platform domain.  i trust my instincts to make the right decision, manage risks + costs. i learn quick, im constantly trying to improve myself, my pipelines, my code, and the processes i use to build these data products.
  - I big piece of that confidence comes from the personal projects, i learned a lot going that route and have put hundreds of hours into that. my experience is not just oh he has 3+ years experience that's a red flag.  it's not just oh i worked 8-5 for those 3 years i've put in thousands of hours after work and on the weekends to upskill and get myself here and i still have more work to do.
- Independent.  don't need a team lead or somebody else to hold my hand, i like being self-sufficient and versatile.
- Mentorship and leading people. 
- Not afraid to speak out on. and not just complain about it but actively introduce a solution or workaround to fix the problem and put us in a better position moving forward.

## STAR - Conflict
1. Situation: I had introduced
2. Task:
3. Action:
4. Result: 

## STAR - Review Moderation Pipeline
1. Situation: We send out reviews to campers a few days after they stay at a park and they can leave text, ratings etc on how their stay was.  We wanted to start showing these on our marketplace.
2. Task: Building the Pipeline to run the these reviews through a content moderation api, store the results to our application db, and accommodate this really hacky workflow to get user feedback on the reviews.
3. Action: Developed the Pipeline, Added functionality to pull data from sheets and write that back as well, worked with multiple teams to develop some processes to keep this running and make sure these reviews are valid.
4. Result: Successfully pushed it out, it's been chugging away since September, it's always cool to push a new feature out

Dealt with kinda just being handed a project that I wasn't involved in the technical planning or discussion for. Pipeline absolutely needed to be made but these extra bits to point users to Looker to click into a Dashboard to click into a Google Form to leave review responses is just objectively not a great customer experience that I never would've signed off on but that's the position I'm in as you know not a senior or staff or team lead role.  I expressed by dislike of this route and was basically told "that's what we're doing".

That's just who I am. Prepared to give my opinion on things but I can also tell when a workflow or process doesn't pass the smell test, and I'm not exactly thrilled to be handed projects that I'm not involved from day 1 on.  Prime example of why I want a bigger role and more responsibility & opportunity because I cannot stand when I'm asked to work on things that I lack context for.

If you're taking shortcuts on every feature you're pushing out then that's just asking for tech debt to keep getting accumulated and it's going to catch up to you.

## STAR - Data Lake
1. Situation: Was given pretty ambiguous requirements
2. Task: Turn those business requirements into a technical solution
3. Action: Build a pipeline with airflow that looped through the list of tables, filtered data down by Park ID to only the park's for that specific customer, and then dumped the data out to blob storage partitioned by date so they can easily see what we sent, what day it's for etc.
4. Result: Successful product launch, added documentation so people can maintain it after me

Dealt with ambiguous business requirements from our biggest enterprise customer, built things in a way such that this could be a feature we offer to other parks, satisfied that enterprise client while opening up a new product offering that is a really easy win for us.  It's not a pipeline that takes 2 hours to run everyday or costs $1000s / month, it's an efficient solution that takes only a few minutes.

## Salary Negotiation Conversation
I'm looking for somewhere between (low_mid_level - high_mid_level) salary. I have a couple reasons for that:
- I have extensive experience implementing & owning data products from pipelines, REST APIs, Dashboards, and ML Products from the ground up.
  - I did this at Campspot, I've done it for my personal projects, I think there's something to be said to design, architect, and implement it 100% yourself.  That's experience that I'm able to bring in on day 1.a
- The reason for the range is I'd like to explore the tech responsibilites a bit more with the hiring manager.  If my skill set aligns really well with what they're already using or what technologies they plan to move to, then I'd feel fairly confident that I'd be able to come in and immediately start delivering business value early on.  In that scenario I'd prefer to be on the higher end of my range
- If my skill set has some pretty glaring things missing then it could still be a good fit but it'd probably take a few months to get my feet under me and start making an impact.  In that case it's reasonable to me to be on the lower end of that range while I pick that knowledge up and I'd also be gaining that experience, some of which I didn't have before which is something I'd value.
- I don't have as much experience with xyz business industry which is valid, but we have a Leadership Team and Product Manager for a reason.  They control the direction of the company and what features to priortize and we, as developers, turn those business requirements into technical solutions.

### Initial HR Interview Response

Hi,

Thank you for reaching out!  I'm very interested in the opportunity and I'm eager to move forward with the process.  I'm available any weekday from 11am - 1pm CT to chat more, let me know a time that works for you & I'll make myself available.

I want to mention that while I'm currently in Chicago, I will be moving to California in August this year which is one of the reasons I'm on the job hunt right now.  If xyz_company offers employment there then fantastic, but if that's a no-go then I regret to say that I'll need to withdraw from the interview process at this time.

Thank you again for considering my application, and I look forward to hearing back from you soon.

Jacob


### Rejection Response
Hi,

I totally understand your_name, thank you for the quick response and I wish you and xyz_company the best of luck in filling the position!

Jacob


### Take Home Assessment Misdirect Response

- Optionally, add a line about I hope your xyz event went well, or hope you had fun at the game if the interviewer mentioned plans of theirs.


Hi,

Thank you for getting back to me so quickly! I appreciate the opportunity to move forward in the application process.

Regarding the take-home assessment, while I fully understand its importance in evaluating candidates' skills, I'm currently juggling several commitments and projects that demand my attention in addition to preparing for my move. I'm concerned that within the given timeframe, I may not be able to produce work of the quality I strive for.

If possible, I kindly request if we could explore alternatives to this assessment. I am eager to showcase my skills and commitment to the role through other means such as a technical interview or discussing relevant projects in my portfolio. However, if this isn't feasible, I regret to say that I will need to withdraw from the process at this time.

Thank you once again for considering my application. I look forward to hearing from you soon.


Jacob


### Salary Email 

Hi,

Thanks for getting back to me xyz. I wanted to take a moment to discuss my salary expectations for the position.

After careful consideration of factors such as my experience, skills, and industry standards, I have determined that my ideal salary range for this role falls between $137,000 and $145,000 annually.

I believe this range is reflective of the value I can bring to the team and the responsibilities associated with the position. Additionally, it aligns with market rates for similar roles I'm experiencing on the job market right now.

I am open to discussing this further and exploring any benefits or perks that may be offered in addition to the base salary.

Thank you for considering my application, and I look forward to the opportunity to discuss this matter further during our next conversation.


## My Intro
Ya I'm Jacob, have about 3+ years professional experience, currently based out of Chicago but I'm looking to move back to California which is the primary reason I'm on the job hunt right now.

Been interested in pursuing data as a career since I was in my 2nd year of college, so that's been the goal the entire time.  Been working on various personal projects since 2019 but my first role came in 2021 as a Data Analyst and that job hunt was brutal, lots of one-and-dones, no responses after submitting take homes.  In the moment it sucked but it's really motivated me to push myself and be beteter. I've kept this edge of always wanting to learn and improve and become better so that im never put in that position again.  But ya I think that's a big part of my story and where I'm at now.

After about a year of being an analyst i moved into campspot as a DE where i've been hands on in re-architecting a lot of what our data platform looks like and doing everything i can to provide a stable and efficient reporting experience for our parks. Had quite a few data initaitives going on when i joined, involved in a migration from Redshift to Snowflake where I've managed 100% of that data warehouse now, introduced new tooling like dbt to the team's tech stack, built Airflow, dbt, and Terraform repos for our Data Platform resources.  Added CI / CD for the Airflow + dbt Repos.  Managed the Releases for those code bases. Big piece of all that has been selling these changes to the team and getting them to adopt the practices that i've implemented which has gone well but also has its challenges too. And of course been involved with all the bullet points on the resume which I'm more than happy to dive into.

Ya that's me so far, in this next role I'm more or less just looking to continue where I'm leaving off. Looking for more responsibility in my next role, new projects, new challenges, and to be honest just a fresh perspective on delivering software.  It's crazy how different things can be company-to-company and that's a cool part about a new opportunity to me is just getting to experience a whole new way of doing things and the ability to pick new things up.

But ya that's enough of me rambling.  happy to pass it back to you.

In my free time i'm an avid gamer, big sports fan, 



## Tool Experience:

dbt

- Introduced to it when I was an Analyst at Mintel
- Implemented it into my NBA Project, built my own Repo, my own docker Image, used the open source libraries, and ran it with ECS
- Because I did that with my personal project, I was able to immediately stand it up at Campspot within a sprint.
- Batteries-included tool.  Comes with so many nice to haves such as Data Lineage, Data Quality Testing, Jinja templating for the Staging / Production builds, and Incremental Models.


PySpark

- No professional Work Experience, both places I've worked at were Snowflake + dbt based
- I absolutely recognize how important Spark is, especially at larger tech companies dealing with true big data / large data volume
- Have a Personal Repo where I have a bunch of scratch scripts I tinker with
- Tested out various data operations reading & writing to sources like Postgres and S3, as well as pulling data from my REST API.  All typical use cases
- Window Functions, Wide Transformations triggered by Group By Aggregations, some Spark SQL testing, all straight forward stuff.  It's the same thing as SQL under the hood we're doing the same kinds of operations
- Did a POC of both Apache Iceberg and Delta Lake, got setup on real deal S3 with AWS Glue Data Catalog - I hate how AWS names their services Glue means like 15 different things.
- Encountered a bug where tables I built with Iceberg in Spark couldn't be read by DuckDB.  There's an active GitHub Issue on this. DuckDB couldn't read the `s3a://` metadata files because they're just `s3://` instead of `s3a`.
- Implemented a Spark Kafka Cassandra Example where a Python Script writes data to some Kafka topics, and then a Spark worder connects to those topics and streams those messages to Cassandra. Completely overkill, Cassandra should only be used for 0.01% of use cases like at Meta but still good knowledge and hands on experience.
- DataFrames are the new Data Structure to use, RDDs are old news. Datasets aren't available in PySpark
- Spark generates a DAG of operations to run for your Spark Jobs, that's why they're idempotent and fault-tolerant. If anything fails it can just follow the lineage to go re-try the step it failed at
- Spark is lazy-evaluated, which means it doesn't run operations until it's requested to by operations like Write Save or Collect. This allows it to optimize the series of operations and build a logical execution plan and waits until it actually needs to go execute the transformations. 
- Spark Jobs are triggered after running commands like Write, Save, or Collect 
- Jobs are divided into Stages which are a set of tasks that can be ran in parallel. Stages are separated by shuffle operations
- Shuffles are when the Cluster has to re-organize all the data partitions amongst the workers.  This is an expensive operation, it's possible but you'd like to avoid it where possible.  Triggered by operations like Group by or Order by.
- Data Skew is a common issue in Spark.  Can view the Spark UI to monitor your jobs and see your longest running tasks and compare vs the median task runtime to get an idea of if there are long running tasks that might be affected by skew that you should go fix.
- Couple ways to fix skew: create a new derived column to distribute the partitions evenly
- Broadcast join ships an entire Table to each worker node's memory to improve performance. Downside is this will eat up memory in each worker node. Use it when you can, but watchout for OOM issues.
- Narrow transformations are ones that can be executed without a shuffle, such as filter or map (applying a function to every row) or flatmap
- Wide transformations require shuffle operations, such as groupby, join, or order by
- Watchout for Python UDFs, slow things down because you have to serialize data into Python Types and then run the UDF and serialize back into Java

Airflow

- Experience building batch pipelines
- Adding Monitoring & Alerting
- Data Validation Checks post-ingestion, checking things like row counts
- Quite Param-heavy for things like Manual Backfills
- Setup our Streaming Pipeline which basically took a microbatching approach to refresh our data every 1 hr. That could have been moved up to every 15 or 20 minutes if needed.
- 

Terraform / AWS

- Experience building cloud infra at both work and personal projects
- RDS, S3, EC2, S3, ECS, ECR, Route53, ELB, Lambdas, EventBridge, Cloudwatch
- RDS Aurora Maintenance - spinning up new Read Replicas, MySQL Upgrades, System Variables etc
- Custom Terraform Modules to spin up Scheduled ECS Tasks, Lambda Functions, Pagerduty SNS Alarms where ECS Failures can be routed to, and IAM Roles for GitHub Actions Runners.

Duck DB + Polars

- New Tools on the block, only run on a single machine. They aren't distributed computed yet
- Duck DB is really powerful more as a drop-in computation engine than as a Database or Data Warehouse Solution
- Polars seems like a good 1-1 replacement for Pandas, although it still uses Pandas under the hood for various operations like writing to SQL Databases
- Duck DB is written in C++, Polars is written primarily in Rust
- These lower level languages offer extreme performance boosts.
- Data Engineers like myself will never write jobs in C++ or Rust, those Languages are used to built the tools and frameworks we use not to write actual code for data products or something


### Talking Points

Hi XYZ !  How's it going ?  Thanks for reaching out, appreciate that you're interested and I'm excited about learning more about the opportunity

Ya so I have about 3+ years professional experience, been wanting to be in data since my 3rd year of college and I've been doing this pretty much every day since I graduated. Was an Analyst for about a year and most recently been at Campspot as a Data Engineer on the Data Platform Team for the past 2 years.  Campspot makes Campground Management Software for parks to manage their business and make bookings and do everything they need to do in their day-to-day, and we offer a Marketplace for consumers like you or I to make bookings at these Campgrounds.

My role mainly involves building pipelines to feed data into our warehouse, managing our platform infrastructure for things like the Warehouse, Airflow, and our dbt Project, and helping unblock other analyst + devs on the team. I've introduced and implemented a lot of new Data Platform Infrastructure since I've been here, working with a ton of cloud resources, tools like Airflow, dbt, and Snowflake, and owning a lot of the day-to-day things involved with the Warehouse. I built Repos for Airflow, dbt, and Terraform from the ground up, I manage most of the releases for our code deploys, I've implemented CI CD for us to get deploys out in a consistent way, and I'm the go-to person for all of our Snowflake infrastructure and most of the pipelines that are feeding data into there. Had my hands in a lot and I've really enjoyed it. It's fulfilling, challenging, and rewarding to me.

We use data to serve internal stakeholder needs and we offer over 150+ Reports to Park Owners on both our Platform Application as well as Looker, where we offer the Parks the chance to login to Looker and view pre-built dashboards for their business.  Just doing everything I can to get data into their hands so they can make more data-driven decisions.

I'm moving to California at the end of my lease here in early August so that's why I'm on the job hunt. Leaving on good terms, I'd stay if i could but this is something I'd like to do. In my next role I'm really just looking for something that's on a similar tech stack and that can provide me challenging projects to tackle. I enjoy working on complex problems and fixing things and improving workflows + processes where I can and I'd like to continue doing that.

Timeline wise - I move early August, if needed I believe I could stay on at my company for a few more weeks but ya I'm looking to have something lined up by then.  Currently in Chicago but I have some family in Michigan that I'd like to visit before I leave so it's just tough juggling quite a few moving pieces right now.

- New Job
- Visit Family in Michigan
- Move to California

Regarding Salary Expectations - could you please confirm the salary range for this role? That's in line with what I'm seeing on the Market right now, I'm aiming for something in the range of $137,000 to $145,000, I know everyone just wants as much as they can get but I fully believe the value I deliver is worth something in that range. I'd also appreciate the opportunity to chat more about it with Hiring Manager and other Technical Stakeholders to understand how my current skills fit in with the team and the company's goals. The Job market isn't great right now but I feel very competitive with my current skill set so I'd like to hold firm on that range.



- I have the know-how for how to use these tools, the cloud experience, implementing these tools & technologies from the ground up
- I'm independent, self-sufficient
- Good instincts for delivering business value while managing cost + expectations

### STAR

#### 1. MySQL Invoice Charge Audit Bigint

Situation

- Background: when I joined Campspot we almost immediately had a mjaor incident where we hit the integer limit on an ETL table of ours which impacted 1 specific Report, and it tooks weeks to fix and the report was down the entire time.  Not good, but also the impact was contained and not widespread.
- In July 2023 almost a year later, I identified our main Audit Table for all Charges on our Invoices was 80 million rows away from hitting its integer limit.  Based on recent daily activity I estimated we'd hit this limit within 3 weeks and every data operation on that table would fail.
- This is a core table to every part of our invoicing, payments, accounting, and reporting needs.  If we can't write to it then we're losing valuable information for our customers. 
- If the trigger cant perform its insert onto the child table then the entire transaction on the parent table could end up getting rolled back.

Task

- As soon as I found out, I pulled the team together and brought in some outside help from other platform architects to get the conversation started.
- I put the meeting together, I invited the right people to get the conversation started, and I laid out the timeline of when it'd fail and also some initial options and plan of attack.
- I knew roughly what we'd need to do, but in these situations it's always good to gather insights from seniors and other managers and listen to their advice on how to proceed as this touches one of the biggest core pieces of our application.
- The next steps were simple, we have to complete a 0 downtime migration on that table because we cannot have a >= 8 hour maintenance window on a table that important.

Action

- I ended up implementing the solution along with one of our senior engineers which involved using Gh-ost to perform an online schema migration to migrate the integer column to a bigint with 0 customer downtime
- It creates a new table with the bigint column, backfills it slowly over a handful of days, uses the binlog to capture any new changes, and then performs the table swap.
- If you just ran a alter table statement on the table it'd be locked for hours, so this is an option 100% of companies have to do to perform these kinds of large scale migrations without having customer impact.
- Immediately got working on that and got to testing on staging because this takes days to run.

Result

- Gh-ost took almost a week to run but we got it done in time in that 3 week deadline, didn't have any issues throughout the process, tested thoroughly on staging beforehand, and helped avoid a major company catastrophe.
- I think it shows that I try to ask the right questions, I'm proactive, and I have the knowledge and know-how to solve some of these more difficult problems that a DE or any other software engineer would face.
- The cool thing is that 100% of companies deal with problems like this in OLTP Databases, and being able to successfully identify and handle it gives me confidence that I can do this work


Tags:

- Tell me about a time you had to learn a new technology quickly.
- Give an example of a time when you identified a bug in a system
- Tell me about a time when you had to debug a difficult problem.


#### 2. Snowflake Terraform for Governance + Infra

Situation

- Background: my first company I was an Analyst in Summer 2021 at a Market Research Tech Company which used Terraform + Terragrunt to manage their Cloud Infra, and also to build their Snowflake Infra
- I thought this system worked really well and I heard the engineers praise it quite a bit, but I didn't understand Terragrunt or why it was used
- Over the next 12 months I learned Terraform on my own time outside of work among other tools and skills, and it ended up helping me land the job at Campspot.
- When I joined Campspot and we chose to move to Snowflake and scrap Redshift, I immediately saw an opportunity to implement things the same way they did.
- Redshift was a mess, permissions were all over the place, nothing was in code. Terraform solves all of these if we build the infra with that instead.

Task

- I introduced the idea to my manager at the time who was fully onboard with me exploring this as a solution to managing the infrastruture and governance of our new Data Warehouse
- Tasked with implementing these Terraform Modules to ensure we build all of our Snowflake infra this way

Action

- Implemented Terraform Modules to build out basically all of the Infra.  Users, Roles, Warehouses, Databases, Schemas, Stages, and Permissions.
- I built and implemented and maintained 100% of that
- The Modules took about 2 sprints to build and they're still in use today to manage all of the Snowflake Infra

Result

- Worked really well.  Very easy to maintain, add new schemas, change permissions etc.
- The Modules build the infra and it's in code, it can go through code review, it can be approved etc.
- Permissions are all handled gracefully.  Grants are set for all current + future resources so I've basically never had to touch grants after I create a schema.
- I'd love to use this for other Databases like MySQL + Postgres as well, I have a Postgres Module that implements a lot of this.
- One downside that I think is a fascinating technical discussion is nobody on the Data Platform Team had or has Terraform experience. 
- Using this is better than writing it manually, but it's a tricky spot to be in because it is kinda more advanced than just writing SQL Commands.
- Not quite sure how to navigate that: to use best practices that nobody on the team has the skill set for, or to do things "the old school way" of just writing raw sql and not keeping anything in code ?


Tags:

- Describe a time when you improved an existing process or system.

#### 3. Snowflake Streaming

Situation

- After we migrated from Redshift to Snowflake, we wanted to explore faster data refresh cadences for our more important tables as once-a-day loads weren't cutting it.
- Snowflake is notoriously expensive and streaming is a difficult thing to setup, but this sounded like the exact cha

Task

- I was asked to tackle this problem, propose various options to the team, and implement a solution that enables a faster refresh cadence while helping to maintain cost

Action

- Proposed various options to the team including Debezium which was something we hadn't used before, had rough cost breakdown
- The implementation took a few months but it involved setting up Debezium on our Application Databases, and an MSK Cluster to receive those data changes.
- An S3 sink was used to pump data out of the topics and into S3 Folders where they were automatically loaded into Snowflake via Snowpipe
- Lots of Infra, moving pieces, and different technologies used to pull the entire solution together.

Result

- Has worked flawlessly since it was introduced.
- Flexibility to add new Tables to the Pipeline
- Product is happy with the data refresh cadence and it fits our budget for what we're willing to spend for this kind of functionality
- Shows my ability to tackle new challenges with technologies I haven't used before and also those external elements of managing cost and balancing those things.

Tags:

- Owning implementation end-to-end
- Learning a new Tool
- Most difficult thing I've tackled in my career


#### 4. Review Content Moderation Pipeline

Situation

- We send out a Post Stay Survey to consumers after they stay at a Campground via our Marketplace.
- This is feedback they provide to Campspot, not the Campground
- Product wanted to start displaying some of these positive reviews on the Marketplace Sites for these Campgrounds to use them as testimonials for other campers to come stay.
- But obviously some of these reviews are nasty, people saying bad things, harsh language, we don't want something negative on display of these sites

Task

- Developing a Content Moderation Pipeline to moderate 100% of these reviews and write various metrics back to the OLTP database so our frontend Marketplace App can pull that data to figure out which reviews are eligible for display

Action

- Developed the Pipeline, used a Moderation API from Microsoft to process the Reviews which recommended whether we should have a human review it. 
- Worked with QA to provide them a list of reviews every week to go through and make sure the Moderation API is doing its job and reliably marking some of these reviews
- Added other elements as well like we pulled Park Feedback off of Google Forms and loaded that into the OLTP Database as well.

Result

- Project eventually got completed and the Moderation Pipeline and the Product Feature worked as intended on our Marketplace App. Always good to have a new product launch go out
- The conflict came from additional work that kept creeping up on the project.
- Product then wanted Parks an option to leave feedback to these reviews, but it was decided they wouldn't have dev time to create a Page in our Platform App for this, so as a stopgap we made a dashboard of all the reviews in Looker which forwarded parks to a Google Form where they could reply to the customer reviews and we would end up displaying the customer review and the park response to that review on the site.
- It required me to backtrack on some of my implementation details and kind of just wasted time
- Respectfully argued my point of how we need better planning for these types of projects. There's no reason we should be scrambling
- I also wasn't invited to the Event Storms for these projects, I wasn't even invited to the little bit of planning that did take place. like why is this work being handed to me if I'm not in charge of planning it out ?
- Bit frustrating, but had productive conversations with my manager and product to help re-iterate that we'd save time by planning a bit better and that it's okay to include me and they were open to hearing that. I'd rather be invited to these meetings than be left off in fear that it'd be a "waste of time"
- Another reason I want to be in a senior role, I feel like I need to be at the table to be aware of the projects we're working on and making sure we're implementing things in the proper way and allowing ourselves enough time to plan and get the work done.


Tags:

- Can you describe a time when you had to handle a conflict within your team?
- Can you describe a time when you had to handle unexpected changes during a project?

#### 5. Introducing dbt to the Team

Situation

- When I joined campspot there was no tooling being used in our Redshift Database.
- They had a SQL Repo where they dumped raw files but nothing ran them, no linting, no tests
- I saw a gap here to bring in dbt and get the team to start using it, i think it immediately brings a lot of benefits and best-practices for very cheap
- I had experience from my past company and experience in my personal project of building a new dbt project and implementing it hands-on, so I immediately saw that this was a gap that I could help bridge

Task

- Took it upon myself to put a meeting together to introduce the tool to our data science + data platform teams
- Laid out what would enable us, what the implementation process would look like, how it basically costs us $0 because we dont have to signup with dbt Cloud if I can nail the implementation using the open source package and Docker.

Action

- After we migrated to Snowflake I ended up starting the dbt project
- Implemented it myself, created a Docker image, created an Airflow dag to run the docker image via ECS, implemented CI CD to automatically release deployments via PR merges, and created some documentation to help onboard the rest of the team on how they can contribute and get their models built

Result

- Immediately became a huge benefit and a drop in replacement to our old manual method of just saving raw SQL Files to a repo.
- We now have almost 150+ models and hundreds of tests.  
- Tons of time is saved
- We're using it to port over legacy batch jobs in MySQL
- Shows how I'm able to drive change and positively impact the places I work at. I want to add the right tooling for the job, I want to improve our processes, and I have the technical skill set and leadership abilities to take those projects on and execute them from inception through til completion regardless of my title. 
- And doing it without being asked?  I'm independent, autonomous, you dont need to hold my hand


Tags:

- Tell me about a time when you had to advocate for a technical decision.
- Tell me about a time you took initiative and improved operational efficiency for your team

#### 6. Introducing Pre Commit Hooks

Situation

- Our SQL Code Quality was a mess and it was all over the place
- 40,000 Lines of Javascript in our Monolith Repo
- My Manager wanted to help solve this problem moving forward but was working way too hard, he was writing raw SQL into a confluence document and we were spending 15 minutes after every standup to walk us through examples
- I had background implementing SQLFluff on my own personal project like over a year ago.  To me this was a solved problem

Task

- Took it upon myself to respectfully kind of steer the conversation from going through these examples to talking about SQLFluff as a Tool and what it could enable us
- Talking about it is one thing, but implementing it is another

Action

- Ended up making some tickets to add SQLFluff to our dbt Repository, it has some opinions on how to format the SQL so i shifted the conversation over to those like Join Indents, Where clause indents that sort of thing and implemented whatever the majority of our team wanted the format to be
- Also added SQLFluff as Pre Commit Hooks which run before you commit your SQL code to the repository.  This makes it so it's always formatted before you're ever even able to check it into the Repository

Result

- Saved us a bit of time there at the end of standups, but just used my knowledge and understanding to introduce another tool + technique to the team to help automate a solved problem for us
- Our entire dbt Repo is formatted by this tool now, it does exactly what it's supposed to do, we don't need to reference some confluence document we just go with whatever this Formatter implements for us because that's what it's designed to do
- Shows I'm able to respectfully challenge a bad idea when I see one, I'm not afraid to speak my mind, and if I do speak my mind I typically feel strongly about it and when it involves a technical tool I almsot always have the means to implement it as well.
- Led us to adding Black as a Pre Commit Hook in our Python Repos as well, just a no brainer.


Tags:

- Tell me about a time you improved code quality in your team.
- Tell me about a time when you had to advocate for a technical decision.
- Driving Innovation 

#### 7. Path of Totality Marketing Campaign

Situation

- Leading upto April 2024 there was going to be a Solar Eclipse
- This is obviously pretty relevant to Campgrounds, big marketing opportunity for both the Campgrounds and Campspot to work together and get the Campgrounds filled up at the right rates
- The issue was Marketing didn't have a great way of knowing exactly which Parks still had availability; this information was only available monthly due to the size of the job that ran this kind of reporting at the time

Task

- I was tasked with delivering a solution we could throw into our BI Tool that enabled the Marketing folks to pull this data at any given moment so they could have accurate read on which Campgrounds they could market that had availability for customers.

Action

- Quickly pulled together an efficient complex query on which Campgrounds still had availability.
- The tough part about that is we have a ton of occupancy and booking rules in place so just because there might be some available campsites doesn't mean they're available to book.
- These rules have different start and end dates to factor in, in addition to the occupancy of the Campsites
- Marketing could then use this to go run targeted campaigns at people who previously camped at these places to get them to go round out their occupancy on the Marketplace
- We take a cut of the reservations when people book on the Marketplace, so it's a win win.

Result

- Got the Metrics Marketing needed, we got it into our BI Tool for them to pull everyday instead of Monthly
- Worked with them to track these Campgrounds as the number of parks in the path of totality that still had occupancy went down over time.
- At first it was 50 of them, then 35, then 20 etc as the days til the Solar Eclipse kept coming down.
- Cool opportunity to work directly with Marketing on a difficult problem and be able to track that progress on a successful campaign
- Was able to re-use this moving forward to effectively replace the old monthly-style report that was previously used for this use case.

Tags:

- Can you give an example of a time when you had to collaborate with a cross-functional team?


#### 8. Mentoring Heather + Jonathan on Incremental Models

Situation

- Heather was our Data Analyst on the Data Platform Team, she's fantastic just the nicest person you'll ever meet but she was on the struggle bus quite a bit on typical day-to-day things.
- She was good with SQL and Reporting, but there we were introducing more and more incremental models into your system for performance, efficiency etc to drive reporting, but they were struggling to pickup on some of the concepts

Task

- My Manager recommended I pick up some 1 on 1 time with her talk through specifics

Action

- I organized a few weekly sessions with her to go over my process.  
- Start with the basics: this is what local development looks like, this is how our cloud instances get permissions from AWS, this is how the deployments are going out, and here's what I look out for in Code Reviews and things like that.
- We worked with a lot of integrations and secrets so it's a pretty basic flow of like grab secrets for the thing you need, pull data from the API or vendor, typically get it into a Pandas DataFrame if it'll fit, and write it to S3.  And then from there you just copy every other pipeline flow that we've set up already.

Result

- She asked a ton of questions and learned a lot.  It was really cool to see her improvement and picking up on the things I directly worked with her on.
- Also taught me a lot about just getting 1 on 1 time with people can be really impactful to built rapport and trust with one another. It's hard to remember to do this when working in Remote companies.  It's easy to just be like oh I don't have any meetings for the rest of the afternoon heck ya.  Heads down time is good but when it's like every day of the sprint somethings probably not right.

Tags:

- Tell me about a time when you had to mentor a junior developer.





I've been executing on various senior points at Campspot

- Introducing new technologies & tooling to our team to increase productivity and efficiency
  - Tools like dbt for our transformation workloads, Debezium for a CDC workflow to extract data from our Application Databases
  - Implemented nice-to-haves like Pre Commit Hooks to lint & format our code, and CI Pipelines on our Airflow + dbt Repos
  - Stood up Repos for our Airflow, dbt, and Terraform work because they didn't exist.
- Independently and autonomously solving complex problems
  - Moving some batch workloads to streaming which was requested by Product wanting a faster data refresh cadence
  - InvoiceChargeAudit MySQL Bigint Migration
  - Data Lake Project - ambiguous requirements from Product & the Enterprise Customer we were working with
- Ownership of major projects and components in our Data Platform infrastructure. 
  - I've managed 100% of our Snowflake Warehouse down to the Roles, Users, Warehouses, and cost. And I was the primary engineer involved in that migration from Redshift to Snowflake.
  - Our Airflow Instances
  - Our dbt Project
  - Data Lake Product Offering
- Building documentation, diagramming, and incident response runbooks
  - Documenting every piece of the infrastructure and how it all flows together
  - This is often way overlooked, but I like preparing myself and the team I'm on for various things that can go wrong.
  - If we're on-call then I expect some standard procedure to be set & in place to respond to these incidents


These are things I'd like to continue doing & executing on regardless of what my title or next role is. 


- Introducing new technologies & tooling to our team to increase productivity and efficiency
- Independently and autonomously solving complex problems
- Ownership of major projects and components in our Data Platform infrastructure. 
- Influencing our high-level architecture
- Managing cost, security, and governance of Cloud Infrastructure and Databases
- Building documentation, diagramming, and incident response runbooks

Things I'm missing that I'd like to hit more on:

- Mentoring others such as junior and mid-level engineers
- Cross-functional team collaboration
  - This was difficult because of the company being primarily Java
  - I'm doing some of it like assisting our Operations Team with migrating a Databse from Postgres into our Primary MySQL Database, but I'm not really collaborating as much as I'm unblocking them
- Stakeholder Communication - I worked well with product but not with any executives