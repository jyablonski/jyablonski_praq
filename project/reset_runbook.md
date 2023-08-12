# Reset Runbook
1. Use the `sql/sql_extracts.py` Script to Save *all* source data from
   1. `nba_source` Schema Tables
   2. `ml_models` Schema Tables
   3. `public` Schema Tables
   4. Specific `nba_prod` Schema Tables
2. Run `terraform destroy` on old infra
3. Run `` to delete all resources in old account
4. Make new `jyablonski_aws_x@gmail.com` email
5. Make new AWS Account w/ new email
6. Add Root MFA onto new AWS Account
7. Create jacob sign-in user
8. Add MFA onto jacob sign-in user
9.  Create Access / Secret Keys for jacob user
10. Update Keys in Terraform Repo & Terraform Cloud
11. Run `terraform apply` on new infra
12. Update `jyablonski.dev` Route53 Record to point to provided Google Domain DNS Endpoints
13. Use the `sql/sql_refresh.py` Script to load all necessary source data
14. Update GitHub Actions Secrets on the following Repos:
    1.  [python_docker](https://github.com/jyablonski/python_docker)
    2.  [aws_terraform](https://github.com/jyablonski/aws_terraform)
    3.  [nba_elt_dbt](https://github.com/jyablonski/nba_elt_dbt)
    4.  [nba_elt_rest_api](https://github.com/jyablonski/nba_elt_rest_api)
    5.  [nba_elt_mlflow](https://github.com/jyablonski/nba_elt_mlflow)
    6.  [jyablonski_liquibase](https://github.com/jyablonski/jyablonski_liquibase)
15. Re-run CD Pipelines on the 6 Repos to update shit on new infra.