# NOTES ON THE UPSERT FUNCTION
The Logic in `postgres_upsert.ipynb` successfully works to implement the equivalent of `pd.DataFrame.to_sql(..., if_exists='update')` (which doesn't exist).

The issue I was having was having to constantly rescrape the schedule data when games got rescheduled.  The concept of Upsert fixes this.

Basically, you have to do some dumb bullshit with python indexes and create the primary_key index for that table and then NAME that index the exact same as the column names.  Then you make a temp table of this dataframe and do some ON CONFLICT UPDATE SET stuff.

The idea is that if `start_time` changes on basketball-reference, then it will update that value for the existing record instead of just appending an entirely new record.

The example I did in the script changes the same game of DAL @ GSW from 7:00p start_time to 7:30p.


You don't actually need the INDEX in sql. 
```
select * from jacob_db.nba_source_dev.nba_schedule order by proper_date desc limit 100;

select count(*) from jacob_db.nba_source_dev.nba_schedule;


SELECT EXISTS (
            SELECT * FROM information_schema.tables 
            WHERE table_schema = 'nba_source_dev' AND table_name = 'nba_schedule'
    );
```

# The Tables for Project
Should be used for Schedule, Transaction, Injury Scrapes bc I don't care if there were historical errors with these records, if there's new data then replace it and delete the error.

# See Storage Usage for Postgres
`SELECT datname as db_name, pg_size_pretty(pg_database_size(datname)) as db_usage FROM pg_database;`

This command will show each database in your RDS Server and the storage (in MBs) that it's using.