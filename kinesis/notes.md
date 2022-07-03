# Kinesis Notes
Kinesis allows you to collect and process large streams of records in real time.  Data Streams are what the actual streams are, and they cost $0.15 cents per hr even if 0 volume is coming through.

Firehose is a separate, optional feature that allows you to tap into a data stream and then write those records to some AWS specific source like S3, Redshift, or Opensearch.  It aggregates and batches the records automatically for you, so it waits every 60s to store all records in that timespan to the source so you're not making 1000s of storage calls for individual files.


### Streaming into Snowflake
[Article](https://towardsdatascience.com/streaming-real-time-data-into-snowflake-with-amazon-kinesis-firehose-74af6fe4409)
[Terraform Implementation](https://servian.dev/terraforming-an-auto-ingest-pipeline-from-s3-into-snowflake-using-snowpipe-part-2-ab2d07ad35c0)

Write data to Firehose, set up a destination for Firehose to store messages to S3, then use Snowpipe to continuously read messages from that S3 bucket to load them into Snowflake.
    * It costs $ (0.06 credits per 1000 files), but it's less $ then using a warehouse using COPY statements.
    * In this scenario, I think you could have many messages batched by Firehose into 1 S3 file, and that only counts as 1 file when it gets loaded into Snowflake via Snowpipe.


```
create or replace stage twitter_stream.public.twitter_stage
url='s3://<BUCKET NAME>/'
credentials = (AWS_KEY_ID='<YOUR KEY>' AWS_SECRET_KEY='<YOUR SECRET KEY>');
```
    * Side note - Storage integrations are used in Snowflake to avoid storing AWS Access and Secret keys in Snowflake.  Doesn't impact performance.
    * So your S3 external stage would point to a storage integration you previously set up, which doesn't have the credentials embedded into it.
      * You provide the ARN of an IAM role in YOUR AWS account with access to those S3 buckets you want to use.
      * Then a Snowflake IAM user ARN and external ID is generated to set up a trust relationship so it can access those S3 buckets.

```
create or replace pipe twitter_stream.public.snowpipe auto_ingest=true as
copy into twitter_stream.public.tweets
from @twitter_stream.public.twitter_stage
file_format = (type = 'JSON');
```