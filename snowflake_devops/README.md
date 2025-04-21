# Snowflake 

``` sql
use database dev;
use role accountadmin;
use warehouse compute_wh;

CREATE OR REPLACE API INTEGRATION git_api_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/jyablonski')
  ENABLED = TRUE;

CREATE OR REPLACE GIT REPOSITORY dev.public.jyablonski_repo
  API_INTEGRATION = git_api_integration
  ORIGIN = 'https://github.com/jyablonski/jyablonski_praq.git';
```

``` sh
snow git execute \
    "@jyablonski_repo/branches/jacob/snowflake_devops/migrations/*" \
    -D "environment='dev'"
```

- Set environment variables in `~/.bashrc` or `~/.zshrc`

``` sh
export SNOWFLAKE_USER=example_user
export SNOWFLAKE_PASSWORD=zzzpassword123!
```

``` sh

# performs a dry run to show what migrations will be ran & their raw sql
liquibase update-sql --username=jyablonski --password=example

# runs the migrations
liquibase update --username=jyablonski --password=example

# reference env vars 
liquibase update \
  --username=$SNOWFLAKE_USER \
  --password=$SNOWFLAKE_PASSWORD

liquibase update-sql \
  --username=$SNOWFLAKE_USER \
  --password=$SNOWFLAKE_PASSWORD

liquibase rollbackCount 1 \
  --username=$SNOWFLAKE_USER \
  --password=$SNOWFLAKE_PASSWORD

# can also pass in url if needed
liquibase rollbackCount 1 \
  --username=$SNOWFLAKE_USER \
  --password=$SNOWFLAKE_PASSWORD \
  --url=stopthecap
```


``` sql
-- liquibase formatted sql

-- changeset git_username:20250421_test_table_name
CREATE OR REPLACE TABLE test_table_name (
  id INTEGER
);

-- rollback DROP TABLE test_table_name;
```