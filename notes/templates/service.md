# {Service Name}

> **Owner:** {team or individual}
> **Repo:** {link to repo}
> **Last reviewed:** {date}

## Overview

{2-3 sentence description of what this service does and why it exists. What business problem does it solve? Who are the primary consumers/users?}

## Architecture

{Brief description of how the service works at a high level. Include a diagram link if one exists.}

- **Language/framework:** {e.g. Python/FastAPI, Go, Node/Express}
- **Infrastructure:** {e.g. ECS Fargate, Kubernetes, Lambda}
- **Data stores:** {e.g. Postgres, Redis, S3}
- **Key dependencies:** {other internal services or external APIs this relies on}

## Environments

| Environment | URL | Notes |
| ----------- | ----- | --------------- |
| Production | {url} | |
| Staging | {url} | |
| Dev | {url} | {if applicable} |

## CI/CD

**Pipeline:** {link to CI/CD config or dashboard, e.g. GitHub Actions, CircleCI}

### Build and deploy flow

1. {Describe the trigger, e.g. "Push to `main` triggers a build"}
1. {Describe the build steps, e.g. "Runs linting, unit tests, integration tests"}
1. {Describe the deploy steps, e.g. "Auto-deploys to staging; prod requires manual approval"}

### Rollback

{How to roll back a bad deploy. Include specific commands or links to runbooks if relevant.}

## Configuration

{Where are environment variables and secrets managed? e.g. AWS SSM, Vault, .env files}

Key config values to be aware of:

- `{VAR_NAME}`: {what it controls}
- `{VAR_NAME}`: {what it controls}

## Gotchas

- {Thing that has bitten someone before or is non-obvious. Be specific.}
- {e.g. "The health check endpoint returns 200 even when the DB connection is down because it only checks the webserver process."}
- {e.g. "Staging shares a database with the QA environment, so test data can bleed between them."}

## Monitoring and Alerting

- **Logs:** {where to find them, e.g. CloudWatch log group, Datadog, Grafana/Loki}
- **Metrics/dashboards:** {link}
- **Alerts:** {where alerts fire, e.g. PagerDuty, Slack channel}

## Related Resources

- {Link to runbook}
- {Link to architecture decision records}
- {Link to API docs or OpenAPI spec}
- {Link to relevant Slack channel}
