# Design a System for Data Ingestion from an API

1. Business / Product Use Case + Requirements Gathering
   1. What's this data for?  Who needs it?  Who are the stakeholders gonna be for it?
      1. Maybe I'm just ingesting it for another Software Engineering Team to use it and have some business function for it
   2. Having some idea about how that all flows together is necessary here
   3. Project Timeline ?
   4. Budget for the System / Pipeline ?
2. What SLAs are we thinking about for it
   1. Does all data need to be ingested by some certain time in the morning ?
   2. Daily / Hourly / Real Time ?
3. Figure out how the API offers data scrapes
   1. For full backfills are various endpoints paginated so I can loop through by something like a page number or offset myself?
   2. For incremental runs can I query endpoints and pass in a date or timestamp to filter results by ?
4. Figure out what Endpoints can be scraped from the API
5. Develop a script that pulls data from each endpoint that is required
   1. Add in functionality to do backfills or incremental runs, maybe use an environment variable called `run_type` to determine this
   2. You'd have to see what the performance is like, maybe you'd need `asyncio` to really push the performance and speed of the script to meet your SLA.  Or maybe that's not necessary
   3. Might be able to use a 3rd Party Package that's already been built for the API. otherwise, will likely need to build your own in-house tooling.  Often a OOP approach is preferred here so you only have to setup credentials once to the REST API and then you can put all the scrape methods onto that same class.
6. Loop through the endpoints and write data out to S3 as the script pulls data.
   1. To avoid OOM issues you can either have the script write data out in chunks for each endpoint, or if the data is small enough you can just write 1 file out for each endpoint
   2. Parquet, CSV, or JSON can all work here in theory.
   3. Data from the REST API is returned as JSON but you could pull it into memory, get it into a Pandas or Polars DataFrame structure, then write it out to S3 as a Parquet.  Or you can go straight from python dictionary -> json.dumps to S3.
7. Package your dependencies up in a tool like poetry
8. Create a docker image of your script + dependencies
9. Run the docker image in a container on ECS that is scheduled & orchestrated by Airflow
   1.  Airflow can pass in environment variables to the ECS task
10. Follow up Task could load data from S3 into Database / Data Warehouse
11. Assess API Data Quality
   1. Keep track of primary keys, modified timestamps, duplicates, nulls etc things like that.
   2. If it's really bad you may wanna invest dev time into building a lot of checks and data quality tests.
   3. If it's pretty good then maybe you can be more lenient at this step.
   4. Also depends if you're paying for this API or if it's free; you might have dedicated support you can reach out to to help you debug the issue, or maybe you're on your own
   5. Ultimately you need to start ingesting it and having a look at the data yourself to know for sure
12. Add Various logging into the Script, write errors out to Slack and/or trigger PagerDuty Alerts if the Script is unable to pull what it needs
13. Write Unit + Integration Tests and mock out any HTTP Network Calls and AWS / S3 API Calls

IMPORTANT STOPPING POINT
1. From here the rest of the steps depend on what the goal is.
2. You could perform dimensional data modeling to turn that raw source data into fact / dim tables and eventually aggregate it up or transform it as needed.

Let's say you encounter a Spark pipeline performing poorly, how do you go about identifying the issues and optimizing?
How do you manage the complexity of a pipeline with tons of transformations?
How do you go about testing this pipeline?