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


``` sh

liquibase update-sql --username=jyablonski --password=example
liquibase update --username=jyablonski --password=example
```