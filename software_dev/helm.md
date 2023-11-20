# Helm
Helm is a package manager for Kubernetes applications. Helm charts are packages of pre-configured Kubernetes resources that can be easily deployed to a Kubernetes cluster. They provide a convenient way to define, install, and upgrade even the most complex Kubernetes applications.

Here are the key components of Helm charts:

1. **Chart**: A Helm chart is a collection of files that describe a Kubernetes application. It contains a directory structure with files such as `Chart.yaml` (chart metadata), `values.yaml` (default configuration values), and a set of Kubernetes manifest files that define the resources needed for the application.

2. **Template Engine**: Helm uses Go templates to generate Kubernetes manifests based on user-provided values and the chart's templates. This allows users to parameterize their manifests, making charts highly customizable. Values can be specified in the `values.yaml` file or overridden at installation time.

3. **Release**: When you install a Helm chart into a Kubernetes cluster, it creates a release. A release is an instance of a chart deployed on a Kubernetes cluster, with a specific configuration and a unique release name. You can manage releases, upgrade them, roll them back, or uninstall them using Helm commands.

4. **Repository**: Helm charts can be distributed and shared through Helm repositories. A Helm repository is a collection of packaged charts along with an `index.yaml` file that contains metadata about the available charts. Public repositories like the official Helm Hub or private repositories can be used to distribute and consume charts.

Here's a brief overview of how you might use Helm:

- **Create a Chart**: You create a Helm chart to package your Kubernetes application. This involves organizing your Kubernetes manifests and creating template files for customization.

- **Package the Chart**: Once your chart is ready, you package it into a compressed archive (`.tgz` file). This archive contains the entire chart, including the templates and metadata.

- **Distribute the Chart**: You can distribute your packaged chart through a Helm repository. This could be a public repository like the Helm Hub or a private repository that you maintain.

- **Install the Chart**: Users can then use Helm to install your chart into their Kubernetes cluster. During installation, they can customize the deployment by providing values or using default values specified in the chart.

- **Manage Releases**: Helm tracks releases, making it easy to upgrade, roll back, or uninstall applications. Users can manage their deployed applications using Helm commands.

Helm simplifies the deployment and management of Kubernetes applications by providing a standardized way to package, share, and deploy applications on Kubernetes clusters.

## Commands

``` sh
helm repo add trino https://trinodb.github.io/charts
helm install example-trino-cluster trino/trino

helm create <chart_name>
helm install <release_name> <chart>

helm upgrade <release_name> <chart>
helm rollback <release_name> <revision_number>

helm ls

helm uninstall <release_name>

helm repo add <repo_name> <repo_url>

helm repo update

helm show chart <chart>

helm --help
```