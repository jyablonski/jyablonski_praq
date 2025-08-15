# Helm

Helm is a package manager for Kubernetes applications. Helm charts are packages of pre-configured Kubernetes resources that can be easily deployed to a Kubernetes cluster. They provide a convenient way to define, install, and upgrade Kubernetes applications. It:

- Reduces boilerplate code for complex apps
- Allows for versioning & rollbacks
- Enables parametrization for different environments. Ex:
    - Turn public ingress off for Dev, on for Prod
    - Turn autoscaling off for Dev, on for Prod
    - Set higher CPU + Memory limits for Prod

Helm effectively packages up all of the Deployment, Service, Load Balancer etc type Files for a typical app with K8s which enables them to be re-creatable by others with minimal effort.

## Components

1. Chart: A Helm chart is a collection of files that describe a Kubernetes application. It contains a directory structure with files such as `Chart.yaml` (chart metadata), `values.yaml` (default configuration values), and a set of Kubernetes manifest files that define the resources needed for the application.

2. Template Engine: Helm uses Go templates to generate Kubernetes manifests based on user-provided values and the chart's templates. This allows users to parameterize their manifests, making charts highly customizable. Values can be specified in the `values.yaml` file or overridden at installation time.

3. Release: When you install a Helm chart into a Kubernetes cluster, it creates a release. A release is an instance of a chart deployed on a Kubernetes cluster, with a specific configuration and a unique release name. You can manage releases, upgrade them, roll them back, or uninstall them using Helm commands.

4. Repository: Helm charts can be distributed and shared through Helm repositories. A Helm repository is a collection of packaged charts along with an `index.yaml` file that contains metadata about the available charts. Public repositories like the official Helm Hub or private repositories can be used to distribute and consume charts.

## Files

``` graphql
mychart/
├─ Chart.yaml
├─ values.yaml
├─ values-dev.yaml
├─ values-prod.yaml
├─ values.schema.json        # optional, JSON Schema for values validation
├─ .helmignore               # optional, ignore patterns (like .gitignore)
├─ charts/                   # optional, packaged subcharts
├─ crds/                     # optional, Kubernetes CRDs installed first
├─ templates/
│  ├─ _helpers.tpl          # helper/partial templates (named templates)
│  ├─ deployment.yaml       # typical resource manifests...
│  ├─ service.yaml
│  ├─ ingress.yaml
│  ├─ configmap.yaml
│  ├─ secret.yaml
│  ├─ hpa.yaml
│  ├─ serviceaccount.yaml
│  ├─ NOTES.txt             # post-install/upgrade tips shown to user
│  ├─ tests/                # Helm “test” hooks (e.g., test-connection)
│  │  └─ test-connection.yaml
│  └─ *.tpl                 # optional extra partials
└─ README.md                # optional, docs for humans

```

- `templates/` Holds the Go-template files for the Kubernetes manifests your chart will generate.
    - They’re full of `{{ ... }}` (Go template syntax) for variable substitution, logic, and loops.
    - When you run `helm install` or `helm upgrade`, Helm merges the chart’s `values.yaml` (plus any overrides you pass with -f or --set) into these templates.
    - Helm then renders the templates into pure Kubernetes YAML manifests and applies them to your cluster.
    - All the resources generated together in one install form a Helm release, and Helm tracks release history so you can `helm rollback` to a previous version.

- `templates/_helpers.tpl` includes helper variables used across all the templates. 
    - If you change a label once in _helpers.tpl, it updates everywhere.
    - Keeps repetitive blocks like labels, annotations, or name formatting in one place.

- `values*.yaml` files are the actual config values you're setting 
    - `values.yaml` in the chart sets defaults; you can override them by supplying your own YAML file(s) or --set flags.

- `crds/` holds CustomResourceDefinition YAML files that define new Kubernetes resource types your chart needs.
    - Helm installs these before rendering any templates.
    - Used for prerequisites like defining a KafkaTopic CRD before you can create KafkaTopic resources.

- `charts/` stores versioned dependency charts that your chart needs as part of its deployment

## Helmfile

Helmfile is basically a wrapper and orchestrator for Helm that lets you define and manage multiple Helm releases (and even multiple environments) from a single declarative YAML file.

Helm is great for deploying a single chart at a time, but in real projects you often have multiple charts across many services + applications.

- Helmfile solves this by letting you define all Helm releasese into 1 YAML File
- It helps keep your values.yaml files and secrets organized
- Provides a single command to apply all changes


``` yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami

releases:
  - name: redis
    namespace: cache
    chart: bitnami/redis
    version: 19.1.0
    values:
      - values/redis.yaml

  - name: myapp
    namespace: app
    chart: ./charts/myapp
    values:
      - values/dev.yaml
```

## Commands

``` sh
# 1. Helm

helm repo add trino https://trinodb.github.io/charts
helm install example-trino-cluster trino/trino

# Add a chart repo
helm repo add bitnami https://charts.bitnami.com/bitnami

# Search for a chart
helm search repo redis

# Install the chart
helm install my-redis bitnami/redis --set auth.password=secretpass

# Upgrade it later
helm upgrade my-redis bitnami/redis --set auth.password=newpass

# Uninstall it
helm uninstall my-redis

# ----------------------------------------------------------------------
# 2. Helmfile

# Sync all releases to match helmfile.yaml
helmfile sync

# Diff what will change before applying
helmfile diff

# Apply changes (install/upgrade/delete as needed)
helmfile apply

# Destroy everything defined in the helmfile
helmfile destroy

# Target a specific release
helmfile -l name=myapp apply

```