use database production;
use schema source;

create or replace table production.source.test_table (

id integer,
price number,
store_id integer,
created_at timestamp,
loaded_at timestamp
);

create or replace table production.source.test_table_csv (

id integer,
price number,
store_id integer,
created_at timestamp,
loaded_at timestamp
);

alter table production.source.test_table_csv set ENABLE_SCHEMA_EVOLUTION = true;

create or replace table production.source.test_table_json (

id integer,
price number,
store_id integer,
created_at timestamp,
loaded_at timestamp
);

describe file format test_schema.csv_format_tf;
select * from production.source.test_table;

select * from production.source.test_table_csv;
select * from production.source.test_table_json;

SELECT id, price, store_id, CAST(created_at AS TIMESTAMP_NTZ) AS created_at
FROM production.source.test_table;

alter table source.test_table_csv drop column test;

truncate table production.source.test_table;    
truncate table production.source.test_table_csv;    
truncate table production.source.test_table_json;    

show pipes;


select *
from production.information_schema.pipes;

-- {"executionState":"RUNNING","pendingFileCount":0,"lastIngestedTimestamp":"2024-11-14T21:21:53.605Z","lastIngestedFilePath":"try2.parquet","notificationChannelName":"arn:aws:sqs:us-east-1:180294178125:sf-snowpipe-AIDAST6S62VG7K5YEGEMJ-W8G_D2O3c8qSSipex68RLA","numOutstandingMessagesOnChannel":2,"lastReceivedMessageTimestamp":"2024-11-14T21:23:48.557Z","lastForwardedMessageTimestamp":"2024-11-14T21:23:48.616Z","lastPulledFromChannelTimestamp":"2024-11-14T21:23:53.486Z","lastForwardedFilePath":"jyablonski-nba-elt-prod/test_table/try2.json"}

-- {"executionState":"RUNNING","pendingFileCount":0,"notificationChannelName":"arn:aws:sqs:us-east-1:180294178125:sf-snowpipe-AIDAST6S62VG7K5YEGEMJ-W8G_D2O3c8qSSipex68RLA","numOutstandingMessagesOnChannel":1,"lastReceivedMessageTimestamp":"2024-11-14T21:23:58.561Z","lastPulledFromChannelTimestamp":"2024-11-14T21:26:38.487Z"}

-- {"executionState":"RUNNING","pendingFileCount":0,"lastIngestedTimestamp":"2024-11-14T21:26:53.852Z","lastIngestedFilePath":"try3.parquet","notificationChannelName":"arn:aws:sqs:us-east-1:180294178125:sf-snowpipe-AIDAST6S62VG7K5YEGEMJ-W8G_D2O3c8qSSipex68RLA","numOutstandingMessagesOnChannel":2,"lastReceivedMessageTimestamp":"2024-11-14T22:11:13.643Z","lastForwardedMessageTimestamp":"2024-11-14T21:26:54.004Z","lastPulledFromChannelTimestamp":"2024-11-14T22:11:23.487Z","lastForwardedFilePath":"jyablonski-nba-elt-prod/test_table/try3.parquet"}
select SYSTEM$PIPE_STATUS('production.source.test_pipe');

-- {"executionState":"RUNNING","pendingFileCount":0,"notificationChannelName":"arn:aws:sqs:us-east-1:180294178125:sf-snowpipe-AIDAST6S62VG7K5YEGEMJ-W8G_D2O3c8qSSipex68RLA","numOutstandingMessagesOnChannel":1,"lastReceivedMessageTimestamp":"2024-11-14T21:26:53.685Z","lastPulledFromChannelTimestamp":"2024-11-14T22:01:33.485Z"}

-- {"executionState":"RUNNING","pendingFileCount":0,"lastIngestedTimestamp":"2024-11-14T22:04:20.293Z","lastIngestedFilePath":"try3.csv","notificationChannelName":"arn:aws:sqs:us-east-1:180294178125:sf-snowpipe-AIDAST6S62VG7K5YEGEMJ-W8G_D2O3c8qSSipex68RLA","numOutstandingMessagesOnChannel":5,"lastReceivedMessageTimestamp":"2024-11-14T22:04:18.765Z","lastForwardedMessageTimestamp":"2024-11-14T22:04:21.021Z","lastPulledFromChannelTimestamp":"2024-11-14T22:11:08.487Z","lastForwardedFilePath":"jyablonski-nba-elt-prod/test_table_csv/try3.csv"}
select SYSTEM$PIPE_STATUS('production.source.test_pipe_csv');


select *
from table(snowflake.information_schema.copy_history(TABLE_NAME=>'test_table_csv', START_TIME=> DATEADD(hours, -1, CURRENT_TIMESTAMP())));

select *
from table(snowflake.information_schema.copy_history(TABLE_NAME=>'test_table_json', START_TIME=> DATEADD(hours, -1, CURRENT_TIMESTAMP())));

show pipes in account;

copy into production.source.test_table_json
from @production.test_schema.NBA_ELT_STAGE_PROD/test_table_json/try6.json
file_format = production.test_schema.json_format_tf
match_by_column_name = 'case_insensitive';

COPY INTO PRODUCTION.SOURCE.TEST_TABLE_JSON
FROM @"PRODUCTION"."TEST_SCHEMA"."NBA_ELT_STAGE_PROD"/test_table_json/try6.json
FILE_FORMAT = "PRODUCTION"."TEST_SCHEMA"."JSON_FORMAT_TF"
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
INCLUDE_METADATA = (LOADED_AT = METADATA$START_SCAN_TIME);

COPY INTO PRODUCTION.SOURCE.TEST_TABLE_CSV
FROM @"PRODUCTION"."TEST_SCHEMA"."NBA_ELT_STAGE_PROD"/test_table_csv/try10.csv
FILE_FORMAT = "PRODUCTION"."TEST_SCHEMA"."CSV_FORMAT_TF"
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
INCLUDE_METADATA = (LOADED_AT = METADATA$START_SCAN_TIME);

show stages in account;
show file formats in account;

select *
from production.information_schema.copy_;


SELECT *
FROM INFORMATION_SCHEMA.PIPE_USAGE_HISTORY(
    PIPE_NAME => 'production.source.test_pipe',
    START_TIME => DATEADD('day', -7, CURRENT_TIMESTAMP()),
    END_TIME => CURRENT_TIMESTAMP()
);

-- csv
CREATE TABLE production.source.create_table_csv
  USING TEMPLATE (
    SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
      FROM TABLE(
        INFER_SCHEMA(
          LOCATION=>'@production.test_schema.NBA_ELT_STAGE_PROD/test_table_csv/try6.csv',
          FILE_FORMAT=>'production.test_schema.csv_format_tf'
        )
      ));

-- json
CREATE TABLE production.source.create_table_json
  USING TEMPLATE (
    SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
      FROM TABLE(
        INFER_SCHEMA(
          LOCATION=>'@production.test_schema.NBA_ELT_STAGE_PROD/test_table_json/try2.json',
          FILE_FORMAT=>'production.test_schema.json_format_tf'
        )
      ));

-- parquet
CREATE TABLE production.source.create_table_parquet
  USING TEMPLATE (
    SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
      FROM TABLE(
        INFER_SCHEMA(
          LOCATION=>'@production.test_schema.NBA_ELT_STAGE_PROD/test_table/try1.parquet',
          FILE_FORMAT=>'production.test_schema.parquet_format_tf'
        )
      ));


select *
from production.source.create_table_csv;