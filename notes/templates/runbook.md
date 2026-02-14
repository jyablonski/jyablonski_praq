# Runbook: {Title of the Incident or Procedure}

> **Service:** {service name, link to service doc}
> **Severity:** {P1 / P2 / P3 / Informational}
> **Owner:** {team or individual}
> **Last tested:** {date}

## Summary

{1-2 sentences. What is this runbook for? When should someone reach for it?}

## Symptoms

How you know this is happening:

- {e.g. "Alert fires in #alerts-prod: `service-x-high-error-rate`"}
- {e.g. "Users report 500 errors on the dashboard"}
- {e.g. "Latency spikes above 2s on the `/api/ingest` endpoint"}

## Impact

{What breaks if this is not addressed? Who is affected? Is data loss possible?}

## Prerequisites

- Access to {e.g. AWS console, kubectl, specific Slack channel}
- Permissions: {e.g. admin role in production environment}
- Tools: {e.g. awscli, psql, specific CLI}

## Steps

### 1. Confirm the issue

```bash
# Example: check service health
curl -s https://{service-url}/health | jq .
```

{What to look for in the output. What does "confirmed" look like vs. a false alarm?}

### 2. {Next diagnostic or action step}

```bash
# Example: check recent logs
kubectl logs -n {namespace} deploy/{service} --tail=100 --since=10m
```

{Explain what you are looking for and what the output means.}

### 3. {Mitigation or fix}

```bash
# Example: restart the service
kubectl rollout restart deploy/{service} -n {namespace}
```

{Expected recovery time. How to verify the fix worked.}

### 4. Verify resolution

- {e.g. "Error rate returns to baseline on the dashboard"}
- {e.g. "Health check returns `{"status": "ok"}`"}
- {e.g. "Confirm with the reporter that the issue is resolved"}

## Escalation

If the above steps do not resolve the issue:

1. Page {on-call team or individual} via {PagerDuty, Slack, etc.}
1. Escalate in {Slack channel}
1. {Any other escalation paths}

## Root Causes (Known)

| Date | Cause | Resolution | Post-mortem |
| ------ | ------------------- | --------------- | ----------- |
| {date} | {brief description} | {what fixed it} | {link} |

## Notes

- {Anything else useful, e.g. "This tends to happen after large batch ingestions on Mondays"}
- {e.g. "The staging version of this service does not have the same resource limits, so this issue is not reproducible there"}
