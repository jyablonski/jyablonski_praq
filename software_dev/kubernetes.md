# Kubernetes
Kubernetes, often abbreviated as K8s, is an open-source container orchestration platform. It automates the deployment, scaling, and management of containerized applications. Kubernetes provides a robust framework for deploying and managing containers at scale in production environments.

Kubernetes abstracts away the underlying infrastructure and allows you to define how your applications should run, scale, and self-heal through declarative configuration (using YAML files).

Kubernetes manages clusters of nodes (physical or virtual machines) and orchestrates the placement and scaling of containers within those nodes.

It provides features like load balancing, service discovery, rolling updates, and health checks to ensure the reliability and availability of applications.

Kubernetes can work with any container runtime, not just Docker. Other container runtimes like containerd and CRI-O are also compatible with Kubernetes.

## Helm
Helm is a package manager for Kubernetes applications. It provides a way to define, install, and upgrade even the most complex Kubernetes applications.  Helm uses what are called Helm Charts which are `.yml` based files used to declaritively state every part about how to deploy the Kubernetes application.  Helm charts are used to simplify and standardize the deployment of Kubernetes applications by encapsulating all the necessary Kubernetes resources and configurations into a single, reusable package.

Here's a breakdown of what Helm charts are for in the Kubernetes world:

1. **Package Management**: Helm charts package all the Kubernetes resources needed to deploy an application, including pods, services, config maps, secrets, and more. This packaging simplifies application deployment by bundling everything into a single unit.

2. **Configuration Management**: Helm charts allow you to parameterize your Kubernetes configurations. You can define values and templates within a chart, making it possible to customize deployments for different environments or use cases. This makes it easier to manage configurations for different stages of the development lifecycle (e.g., development, testing, production) without duplicating YAML files.

3. **Version Control**: Helm charts can be versioned, which enables you to track changes to your application deployments over time. This is particularly useful when you need to roll back to a previous version or audit changes.

4. **Reusability**: Helm charts can be shared and reused across different projects and organizations. This promotes best practices, reduces duplication of effort, and accelerates the deployment of applications in a consistent manner.

5. **Dependency Management**: Helm supports dependencies between charts. This means you can create a chart that relies on other charts, simplifying complex application architectures by breaking them down into smaller, manageable components.

6. **Upgrades and Rollbacks**: Helm simplifies the process of upgrading and rolling back applications. It tracks release history, making it easy to revert to a previous known good state if an upgrade introduces issues.

7. **Community and Ecosystem**: Helm has a large and active community, which results in a rich ecosystem of available charts for popular applications and services. You can find Helm charts for databases, web servers, monitoring tools, and much more on the Helm Hub and other community repositories.

8. **Customization and Templating**: Helm charts use Go templating to allow dynamic generation of Kubernetes resources based on user-defined values. This makes it easy to reuse charts with different configurations and adapt them to specific needs.

In summary, Helm charts are a critical tool in the Kubernetes ecosystem for simplifying application deployment, configuration management, and version control. They help streamline the process of managing complex applications in Kubernetes and are widely used in Kubernetes deployments to promote consistency and repeatability.

## How to Use Helm
1. `helm create nba-elt-rest-api`
2. Edit the `values.yml` File

`values.yml`
```
image:
  repository: your-docker-registry/nba_elt_rest_api
  tag: latest
service:
  port: 8080
```

`templates/deployment.yml`
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "nba-elt-rest-api.fullname" . }}
  labels:
    {{- include "nba-elt-rest-api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "nba-elt-rest-api.selectorLabels" . | nindent 8 }}
  template:
    metadata:
      labels:
        {{- include "nba-elt-rest-api.selectorLabels" . | nindent 12 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
```

## Followup Articles
[Article 1](https://opensource.com/article/20/5/helm-chartssss)