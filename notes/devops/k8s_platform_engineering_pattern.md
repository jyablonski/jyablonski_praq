# Kubernetes Platform Engineering Pattern

An abstraction layer that sits between application developers and Kubernetes infrastructure. Rather than requiring every team to understand Helm, Kubernetes manifests, and deployment intricacies, the platform team provides a simplified interface (the `k8s_spec.yaml`) that captures only the application-specific configuration.

- This is basically like a `values.yaml` for a shared Helm chart, but with an even higher level of abstraction.

The pattern is sometimes called:

- Golden Path or Paved Road (Spotify popularized this terminology)
- Platform Abstraction Layer
- Internal Developer Platform (IDP)
- Self-Service Infrastructure

It's a core practice within the broader Platform Engineering movement.

---

### Why use it?

For application developers:

- No need to learn Helm, Helmfile, or Kubernetes resource specs
- Fewer files to maintain (just `k8s_spec.yaml` instead of a full `helm/` directory for their application)
- Guardrails prevent misconfiguration (the platform enforces standards)
- Consistent deployment experience across all services (local dev, CI, staging, prod)

For the platform team:

- Single place to enforce conventions (resource limits, labels, annotations, security contexts)
- Easier to roll out infrastructure changes across all services
- Reduced drift between environments
- Centralized ownership of "how deploys work"

For the organization:

- Faster onboarding for new developers
- Reduced cognitive load on app teams
- Consistent observability (all services get the same labels, making dashboards and alerts uniform)
- Security and compliance controls applied uniformly

---

### The tradeoff

Flexibility decreases. If an app needs something the platform doesn't support, either the platform has to evolve or the app has to work around it. This is usually acceptable because most services fit the common pattern, and edge cases can be handled by extending the shared chart.

---

### Core components

1. Simplified App Config (`k8s_spec.yaml`) – The only infrastructure file app developers touch. Contains just the knobs they care about: replicas, resource limits, environment variables, feature flags for sidecars.

2. Shared Base Chart (`spec-chart/`) – A Helm chart owned by the platform team that knows how to render all the Kubernetes resources a service might need: Deployment, Service, Ingress, HPA, PDB, ServiceAccount, ConfigMaps, sidecar containers, etc.

3. Helmfile Template (`helmfile.yaml.gotmpl`) – The glue layer. Reads the app's `k8s_spec.yaml`, detects the target environment, computes derived values (image URIs, cluster context, environment-specific overrides), and assembles the final Helmfile release.

4. Reusable GitHub Action – Wraps the entire deploy process (validate -> diff -> apply) so app repos just call one action with minimal inputs.

5. Spec Validator – A tool (in this case, a Go program) that validates `spec.yaml` against a schema before deployment. Catches errors early with clear messages rather than cryptic Helm failures.

### How It Works End-to-End

1. Developer writes a `k8s_spec.yaml` in their application directory or repo

   - This is the only infrastructure file they maintain. It contains application-specific configuration like resource limits, environment variables, replicas, and feature flags for optional sidecars. Environment-specific values can be defined using match rules.

2. Developer pushes code and opens a PR

   - CI runs tests, linting, and builds a Docker image tagged with the git SHA. The image is pushed to a container registry (e.g., ECR). Importantly, this image is built once and will be promoted through all environments unchanged.

3. CI validates the `k8s_spec.yaml`

   - A validator (custom tooling, JSON Schema, etc.) checks the spec against the platform's schema. This catches configuration errors early with clear messages, before any Helm or Kubernetes tooling runs.

4. PR merges to main

   - This triggers the deployment workflow.

5. The deployment action runs

   - The reusable GitHub Action is invoked with inputs like namespace, spec path, and the image version (git SHA). The action sets up tooling (kubectl, Helm, Helmfile) and prepares environment variables that identify which repo/image to deploy.

6. Helmfile template resolves the full configuration

The `helmfile.yaml.gotmpl` template executes and does the heavy lifting:

- Reads the app's `spec.yaml`
- Detects the target environment from the namespace name
- Selects the correct cluster context (prod vs staging)
- Computes derived values: full image URI, region, account ID, architecture, environment labels
- Merges in cluster-specific overrides from the platform's values files
- Assembles a complete Helmfile release pointing at the shared base chart

7. `helmfile diff` shows what will change

   - Before applying anything, the diff output shows exactly what Kubernetes resources will be created, modified, or deleted. This provides visibility and a safety check.

8. `helmfile sync` applies the release

   - The shared base chart is rendered with all the assembled values and applied to the cluster. Helm manages the release lifecycle, including rollback capabilities if something fails.

9. Post-deploy (optional)

   - The action can output metadata like deploy start time for linking to observability dashboards. Slack notifications, deployment annotations, and status updates can be wired in as additional steps.

---

### How to recreate it

Phase 1: Build the shared chart

Start by extracting commonality from your existing services. What does every service need? Likely a Deployment, Service, and maybe Ingress. Create a Helm chart with sensible defaults and values that cover the 80% case.

```
spec-chart/
├── Chart.yaml
├── values.yaml              # defaults
├── values-prod.yaml         # prod overrides
├── values-staging.yaml      # staging overrides
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    └── _helpers.tpl
```

Design the values schema around what app developers actually need to specify, not around Kubernetes resource structure.

Phase 2: Define the spec format

Create a simple, opinionated schema for `k8s_spec.yaml`. Keep it minimal initially:

```yaml
# Example minimal k8s_spec.yaml
name: my-service
replicas: 2
port: 8080
resources:
  cpu: 500m
  memory: 512Mi
env:
  - name: LOG_LEVEL
    value: info
```

Document what each field does. This is your contract with app developers.

Phase 3: Write the helmfile template

Create `helmfile.yaml.gotmpl` that reads the spec, detects environment from namespace, and wires everything together. Start simple:

```yaml
releases:
  - name: { { $spec.name } }
    chart: path/to/infra-chart
    namespace: { { .Namespace } }
    values:
      - spec: { { toYaml $spec | nindent 10 } }
    set:
      - name: image.repository
        value: { { computed from environment } }
      - name: image.tag
        value: { { from REPOSITORIES env var } }
```

Phase 4: Build the deployment action

Wrap the workflow in a composite GitHub Action:

```yaml
# action.yml
inputs:
  namespace:
    required: true
  spec-path:
    default: spec.yaml
  version:
    required: true

runs:
  using: composite
  steps:
    - name: Setup tools
      # install helm, helmfile, kubectl

    - name: Validate spec
      # run schema validation

    - name: Diff
      run: helmfile diff

    - name: Apply
      run: helmfile sync
```

Phase 5: Add validation

Build a validator that checks `k8s_spec.yaml` against your schema before any Helm templating happens. This gives developers fast, clear feedback. JSON Schema works, or a custom tool in Go/Python if you need richer validation logic.

Phase 6: Iterate based on real needs

As teams adopt the platform, they'll request features. Add them to the shared chart and spec schema. Common additions include: sidecar containers (Redis, etc.), cron jobs, multiple deployment targets, canary/blue-green configuration, custom health checks.

---

### Key design principles

Convention over configuration – Provide strong defaults so most specs are tiny.

Escape hatches – Allow passing through raw values for edge cases, but make it obvious when someone's going off the golden path.

Environment parity – Same spec deploys to dev, staging, and prod with environment-specific values computed automatically.

Immutable artifacts – Build the image once, promote through environments by changing only configuration.

Fail fast with clear errors – Validate early, surface problems before they hit the cluster.

## Monitoring and SLO Integration

The platform can automatically generate observability infrastructure from the same `k8s_spec.yaml` that defines the application. Since all services deploy through the shared chart with consistent metric labels, we can template Grafana dashboards and Prometheus alerting rules without per-service customization.

### Spec format

```yaml
name: payments-api
replicas: 3
port: 8080

monitoring:
  slos:
    availability: 99.9 # percentage of non-5xx responses
    latency:
      p95: 300ms # 95th percentile threshold
      p99: 1s # 99th percentile threshold
      target: 99.0 # percentage of requests meeting latency threshold
    window: 30d # SLO evaluation window (default: 30d)
```

If `monitoring` is omitted, the platform still generates a standard dashboard with common SLIs (request rate, error rate, latency percentiles) but without SLO-specific panels or alerting.

### What gets generated

From the monitoring block, the shared chart emits:

1. PrometheusRule (recording rules) — pre-computes error ratios and latency percentiles as named metrics, reducing query complexity in dashboards and alerts

2. PrometheusRule (alerts) — multi-window burn rate alerts following the Google SRE model. A fast burn (14.4x) over a short window pages immediately; slower burns over longer windows create tickets

3. GrafanaDashboard CRD — a templated dashboard showing error budget remaining, burn rate, SLI trends over time, and request volume for context

4. ServiceMonitor — ensures Prometheus scrapes the service's metrics endpoint with appropriate labels

### Standard dashboard panels

Every generated dashboard includes:

| Panel                  | Description                                           |
| ---------------------- | ----------------------------------------------------- |
| Error budget remaining | Percentage of budget left in the current window       |
| Burn rate              | Current consumption rate relative to sustainable pace |
| Availability over time | Rolling success rate with SLO target line             |
| Latency percentiles    | p50, p95, p99 with threshold markers                  |
| Request rate           | Traffic volume for context                            |
| Recent SLO breaches    | Annotations marking threshold violations              |

### How alerting works

Rather than alerting on instantaneous threshold breaches (noisy), the platform uses burn rate alerting:

- Critical (pages): Burning 2% of monthly budget in 1 hour (14.4x burn rate sustained for 5 minutes)
- Warning (tickets): Burning 5% of monthly budget in 6 hours (6x burn rate sustained for 30 minutes)

This catches real incidents while ignoring brief spikes that don't meaningfully impact users.

### Customization escape hatches

For services needing additional monitoring beyond the standard template:

```yaml
monitoring:
  slos:
    availability: 99.9
  extra_dashboards:
    - path: dashboards/custom-business-metrics.json
  extra_alerts:
    - path: alerts/custom-rules.yaml
```

These are applied alongside (not instead of) the generated resources, allowing teams to extend without forking the platform.

---

### When not to use this

If you only have a handful of services, the overhead of building and maintaining the platform layer may not be worth it. This pattern pays off at scale when you have dozens of services and multiple teams, or when you need strong consistency for compliance/security reasons.
