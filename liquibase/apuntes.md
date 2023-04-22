# Liquibase Notes

`liquibase --changeLogFile=jacobdb_changelog.xml generateChangeLog`

`liquibase update --changelog-file=update.xml`

`liquibase update-sql` - run this first to double check the SQL to be ran before actually wanting to run it.
`liquibase update`