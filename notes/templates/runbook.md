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

## Dashboards

- Grafana Link 1
- Grafana Link 2
- {Any other relevant monitoring dashboards}

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

## Rollback Plan (If Necessary)

> Ideally you just have a dedicated rollback runbook for how to handle rollbacks that you can link. If not, write out the steps here.

If service continues to be degraded after mitigation, consider rolling back the bad change.

- If this is a feature flag, disable it in xyz and monitor for recovery.
- If this is a code change, follow the steps below.

Rollback Steps:

1. Revert change in K8s for the deployment `kubectl rollout undo service-x/1e23456ffd118db9dc04caf40a442040e5ec99f9`
   1. This will put out the fire, but the state of `main` will still be broken.
1. Open a new PR that reverts the offending commit(s) and merge it to `main` to prevent future incidents.
   1. If the change was a feature flag, open a PR to remove the flag and merge it to `main`.
1. End state should be that the bad change is no longer running in production and the codebase reflects that change has been rolled back.

If the bad change is related to a database migration that cannot be easily rolled back, there is additional triage you need to do; use your best judgement, escalate if needed.

## Notes

- {Anything else useful, e.g. "This tends to happen after large batch ingestions on Mondays"}
