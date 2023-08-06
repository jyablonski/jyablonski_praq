# Liquibase Notes
[Article](https://mycloudjourney.medium.com/liquibase-series-automating-database-changes-with-liquibase-f93d1d9e795f)

`liquibase --changeLogFile=jacobdb_changelog.xml generateChangeLog`

`liquibase update --changelog-file=update.xml`

`liquibase update-sql` - run this first to double check the SQL to be ran before actually wanting to run it.
`liquibase update`


`liquibase rollback-count --count=1` to rollback 1 changelog
- this will run the `<rollback>` in the that changelog file, and remove the entire row from the `DATABASECHANGELOG` table.

`liquibase --output-file=snapshot_2023-06-18.json snapshot --snapshot-format=json`

`liquibase generate-changelog --changelog-file=changelog_2023-06-18.xml`

`liquibase --output-file=mySnapshot.json snapshot --snapshot-format=json`