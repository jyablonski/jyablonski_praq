# Helm
A package manager for Kubernetes Applications

Apps require all different kinds of services, configurations, and settings.  Helm helps manage that complexity and introduces reusability.

Bundles YAML files and stores them in public or private Helm Repositories.  Some application developers create their own Helm charts for others to use their software.

Helm is also a templating engine that uses Jinja `{{ .values }}` in the `values.yaml` file.

Useful for CI / CD when you can replace values depending upon whether build is in Dev, Staging, or Prod.

Can deploy same Application across different Kubernetes Clusters (Dev, Staging, or Prod).