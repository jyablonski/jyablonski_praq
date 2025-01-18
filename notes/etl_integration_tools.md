# Airbyte
An Open Source Tool that allows you to move your data from sources to destinations, such as Postgres to Snowflake.

Postgres -> Snowflake is essentially the same as a CDC Framework with Postgres WAL, Debezium, Kafka, and Snowflake. 
    * Airbyte needs a Postgres user, a Snowflake User, and an S3 bucket.
    * Postgres source with user credentials and the DB itself
    * Snowflake Destination with user credentials, and a DB + Schema to write the data to.
    * S3 credentials for Airbyte to write the data to, which Snowflake can then read from and copy in to its database.
    * You select the data you want to sync and the source / destination names. 
      * You can sync on a batch basis or manually trigger it.
      * Full refresh or incremental load capabilities are offered.
    * This example used the Airbyte GUI tool to create everything which is very eh.

Airbyte can be self hosted or used via their Cloud offering (expensive).  Self hosted you're primarily using the local GUI tool to create everything you need.

# Meltano
An Open Source tool to move data from sources to destinations, like the above example.  No official cloud offering.

Compared to Airbyte, Meltano is heavily dependent upon building `.yaml` files to define your configurations and all of your options, and also their CLI tool to trigger jobs and runs.
    * You install plugins that community has created and supply your credentials to connect to whatever you're using, and various parameter options (start / end dates, incremental vs full refresh load types etc).
    * Can store secrets / private credentials in environment variables so they aren't in the `.yaml` file.
      *  `GITLAB_API_TOKEN`
      *  `TARGET_POSTGRES_PASSWORD`
    * This solution can be version controlled, containerized, and ran in Airflow DAGs as needed.

# Fivetran
A Managed (Paid) Solution compared to the 2 previous open source tools.  They do most of the setup and configuration, you just have to provide the same types of credentials and various configuration options like incremental vs full refresh load types etc.

Required maintenance is much lower than the 2 previous tools.  Savings that you could have by using other tools might be made up for the lack of developer maintenance needed.

Expensive alternative, but can help get companies up & running to start driving business value instead of waiting for developers to implement custom solutions themselves for these "trivial" tasks (you're not yet creating any value by moving raw data from point A to point B).