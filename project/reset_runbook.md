# Reset Runbook
NBA ELT Project must be reset once a year to swap to a new AWS Account to exploit free tier ;-)

1. Use the `sql/sql_extracts.py` Script to Save *all* source data from
   1. `nba_source` Schema Tables
   2. `ml_models` Schema Tables
   3. `public` Schema Tables
   4. Specific `nba_prod` Schema Tables
2. Run `terraform destroy` to delete Infra in Old Account
3. Run `aws-nuke -c aws_nuke.yml --no-dry-run` to delete all additional resources in old account
   1. Make sure all fkn s3 buckets are deleted that was a bitch last time
      1. Either run `aws s3 rm s3://aws-cloudtrail-logs-288364792694-bc528206 --recursive` or manually press `Empty` on each bucket.
4. Make new `jyablonski_aws_x@gmail.com` email
5. Make new AWS Account w/ new email
6. Add Root MFA onto new AWS Account
7. Create jacob sign-in user
8. Add MFA onto jacob sign-in user
9.  Create Access / Secret Keys for jacob user
10. Create `jacobs-terraform-user` and grant `AdministratorAccess` Policy
11. Create Access / Secret Keys for Terraform User
12. Update Keys in Terraform Repo & Terraform Cloud
13. Run `terraform apply` to build Infra in New Account
14. Update `jyablonski.dev` Route53 Record to point to provided Google Domain DNS Endpoints
15. Use the `sql/sql_refresh.py` Script to load all necessary source data
16. Update all of the tables to reset the id sequence otherwise all the REST API actions will fail
    1.  NEXT YEAR figure out proper liquibase shit for this part
17. Update GitHub Actions Secrets on the following Repos:
    1.  [python_docker](https://github.com/jyablonski/python_docker)
    2.  [aws_terraform](https://github.com/jyablonski/aws_terraform)
    3.  [nba_elt_dbt](https://github.com/jyablonski/nba_elt_dbt)
    4.  [nba_elt_rest_api](https://github.com/jyablonski/nba_elt_rest_api)
    5.  [nba_elt_mlflow](https://github.com/jyablonski/nba_elt_mlflow)
    6.  [jyablonski_liquibase](https://github.com/jyablonski/jyablonski_liquibase)
18. Re-run CD Pipelines on the 6 Repos to update shit on new infra.


Process took 5 hours in August 2023 - ran into the following issues:
- AWS changed default S3 Permissions between August 2022 and August 2023.  A lot of my buckets didnt work in August 2023 when i tried to create them, something related to ACLs.  This took probably 2 extra hours of bs to figure out and finally get it working.
- Various S3 Buckets in old account didnt get deleted before I deactivated the account; had to rename these buckets in the new account.
- Backfilling the `id` serial tables that the REST API uses was a bitch without liquibase
- Like half the Repos still had Access/Secret Key Auth for CI CD instead of the IAM Role so this took like an extra hour to build that on the fly so it's doing it the right way
- The SQL code needed is now in `project/runbook_code.sql`