use role accountadmin;
use database production;
use schema source;

show procedures;

drop procedure clone_dev_database();

CREATE OR REPLACE PROCEDURE clone_dev_database()
  RETURNS STRING
  LANGUAGE JAVASCRIPT
  EXECUTE AS OWNER
AS
$$
try {
    var sql_commands = [
        `CREATE OR REPLACE DATABASE development CLONE production`,

        `REVOKE ALL PRIVILEGES ON DATABASE development FROM ROLE airflow_role_dev`,
        `REVOKE ALL PRIVILEGES ON DATABASE development FROM ROLE dbt_role_dev`,
        `REVOKE ALL PRIVILEGES ON DATABASE development FROM ROLE metabase_role_dev`,
        `REVOKE ALL PRIVILEGES ON DATABASE development FROM ROLE PUBLIC`,

        `GRANT USAGE ON DATABASE development TO ROLE airflow_role_dev`,
        `GRANT USAGE ON DATABASE development TO ROLE dbt_role_dev`,
        `GRANT USAGE ON DATABASE development TO ROLE metabase_role_dev`,

        `GRANT USAGE ON SCHEMA development.TEST_SCHEMA TO ROLE airflow_role_dev`,
        `GRANT USAGE ON SCHEMA development.TEST_SCHEMA TO ROLE dbt_role_dev`,
        `GRANT USAGE ON SCHEMA development.TEST_SCHEMA TO ROLE metabase_role_dev`,
        `GRANT SELECT ON ALL TABLES IN SCHEMA development.TEST_SCHEMA TO ROLE metabase_role_dev`,
        `GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA development.TEST_SCHEMA TO ROLE airflow_role_dev`,
        `GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA development.TEST_SCHEMA TO ROLE dbt_role_dev`,

        `GRANT USAGE ON SCHEMA development.DIM TO ROLE airflow_role_dev`,
        `GRANT USAGE ON SCHEMA development.DIM TO ROLE dbt_role_dev`,
        `GRANT USAGE ON SCHEMA development.DIM TO ROLE metabase_role_dev`,
        `GRANT SELECT ON ALL TABLES IN SCHEMA development.DIM TO ROLE metabase_role_dev`,
        `GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA development.DIM TO ROLE airflow_role_dev`,

        `GRANT USAGE ON SCHEMA development.FACT TO ROLE airflow_role_dev`,
        `GRANT USAGE ON SCHEMA development.FACT TO ROLE dbt_role_dev`,
        `GRANT USAGE ON SCHEMA development.FACT TO ROLE metabase_role_dev`,
        `GRANT SELECT ON ALL TABLES IN SCHEMA development.FACT TO ROLE metabase_role_dev`,
        `GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA development.FACT TO ROLE airflow_role_dev`,

        `GRANT USAGE ON SCHEMA development.SOURCE TO ROLE airflow_role_dev`,
        `GRANT USAGE ON SCHEMA development.SOURCE TO ROLE dbt_role_dev`,
        `GRANT USAGE ON SCHEMA development.SOURCE TO ROLE metabase_role_dev`,
        `GRANT SELECT ON ALL TABLES IN SCHEMA development.SOURCE TO ROLE metabase_role_dev`,
        `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA development.SOURCE TO ROLE airflow_role_dev`,

        `GRANT USAGE ON SCHEMA development.EXPERIMENTAL TO ROLE airflow_role_dev`,
        `GRANT USAGE ON SCHEMA development.EXPERIMENTAL TO ROLE dbt_role_dev`,
        `GRANT USAGE ON SCHEMA development.EXPERIMENTAL TO ROLE metabase_role_dev`,
        `GRANT SELECT ON ALL TABLES IN SCHEMA development.EXPERIMENTAL TO ROLE metabase_role_dev`,
        `GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA development.EXPERIMENTAL TO ROLE airflow_role_dev`,

        `GRANT USAGE ON SCHEMA development.MARTS TO ROLE airflow_role_dev`,
        `GRANT USAGE ON SCHEMA development.MARTS TO ROLE dbt_role_dev`,
        `GRANT USAGE ON SCHEMA development.MARTS TO ROLE metabase_role_dev`,
        `GRANT SELECT ON ALL TABLES IN SCHEMA development.MARTS TO ROLE metabase_role_dev`,
        `GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA development.MARTS TO ROLE airflow_role_dev`,

        `GRANT USAGE ON SCHEMA development.STAGING TO ROLE airflow_role_dev`,
        `GRANT USAGE ON SCHEMA development.STAGING TO ROLE dbt_role_dev`,
        `GRANT USAGE ON SCHEMA development.STAGING TO ROLE metabase_role_dev`
    ];

    for (var i = 0; i < sql_commands.length; i++) {
        snowflake.execute({sqlText: sql_commands[i]});
    }

    return 'Clone and permission grants completed successfully.';
} catch (err) {
    return 'Failed: ' + err.message;
}
$$;

CALL clone_dev_database();


show roles;

use role accountadmin;
GRANT USAGE ON PROCEDURE production.source.clone_dev_database() TO ROLE airflow_role_prod;


grant role airflow_role_prod to user jyablonski;
use role airflow_role_prod;
use database production;
use schema source;
use warehouse airflow_role_prod_warehouse;

CALL clone_dev_database();

drop database development;

use role airflow_role_dev;
use warehouse airflow_role_dev_warehouse;

select *
from development.source.boxscores;

