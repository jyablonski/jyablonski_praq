# Kubernetes
Kubernetes, often abbreviated as K8s, is an open-source container orchestration platform. It automates the deployment, scaling, and management of containerized applications. Kubernetes provides a robust framework for deploying and managing containers at scale in production environments.

Kubernetes abstracts away the underlying infrastructure and allows you to define how your applications should run, scale, and self-heal through declarative configuration (using YAML files).

Kubernetes manages clusters of nodes (physical or virtual machines) and orchestrates the placement and scaling of containers within those nodes.

It provides features like load balancing, service discovery, rolling updates, and health checks to ensure the reliability and availability of applications.

Kubernetes can work with any container runtime, not just Docker. Other container runtimes like containerd and CRI-O are also compatible with Kubernetes.

## K8s Components
Kubernetes is a powerful container orchestration platform used to deploy, manage, and scale containerized applications. It consists of various components that work together to provide a robust and scalable container management environment. Let's walk through the different components of Kubernetes:

1. **Master Node Components:**

   - **API Server:** The API server is the entry point for all interactions with the Kubernetes cluster. It processes RESTful API requests, enforces authentication and authorization, and acts as the front-end to the control plane.

   - **etcd:** This is a distributed key-value store that stores the configuration data of the cluster. It serves as Kubernetes' primary database, storing information about nodes, pods, and other cluster objects.

   - **Controller Manager:** The controller manager is responsible for regulating the state of the cluster. It ensures that the desired state of cluster objects matches the actual state. Various controllers, like the Replication Controller and the Node Controller, are part of this component.

   - **Scheduler:** The scheduler assigns work to nodes, based on resource requirements, constraints, and other policies. It decides where to place new pods based on the available resources and optimization goals.

2. **Node (Worker) Components:**

   - **Kubelet:** The Kubelet is an agent that runs on each node in the cluster. It is responsible for managing and maintaining the health of containers running on that node. It communicates with the API server and reports the node's status.

   - **Container Runtime:** The container runtime, such as Docker or containerd, is responsible for pulling and running containers. Kubernetes is compatible with multiple container runtimes.

   - **Kube Proxy:** Kube Proxy maintains network rules on nodes. It helps manage network connectivity between the pods and services within the cluster. It handles routing and load balancing for service endpoints.

   - **Pod:** A pod is the smallest deployable unit in Kubernetes. It can contain one or more containers that share the same network namespace and storage volumes. Pods are scheduled and run on nodes.

3. **Add-Ons and Supporting Components:**

   - **Ingress Controller:** An Ingress controller manages external access to services within the cluster. It handles routing, load balancing, and SSL termination for incoming traffic.

   - **Cluster DNS:** Cluster DNS provides DNS-based service discovery and name resolution within the cluster. It allows pods to communicate with each other and with services using meaningful domain names.

   - **Dashboard:** The Kubernetes Dashboard is a web-based user interface for managing and monitoring the cluster. It provides a graphical view of cluster resources and allows administrators to perform common operations.

   - **Monitoring and Logging Tools:** Various monitoring and logging tools, such as Prometheus, Grafana, and ELK Stack, can be integrated with Kubernetes to gather performance metrics and monitor the health of applications.

   - **Storage Solutions:** Kubernetes supports various storage solutions, including Persistent Volumes (PVs) and Persistent Volume Claims (PVCs), to provide storage for applications.

These are the key components of a typical Kubernetes cluster. Understanding their roles and interactions is essential for effectively managing and operating containerized applications in a Kubernetes environment.


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

## eksctl
`eksctl` is a command-line tool used for creating, managing, and interacting with Amazon Elastic Kubernetes Service (Amazon EKS) clusters. Amazon EKS is a managed Kubernetes service provided by Amazon Web Services (AWS) that simplifies the process of running Kubernetes clusters on AWS infrastructure. `eksctl` is a separate open-source tool developed by Weaveworks and is designed to make it easier to work with Amazon EKS.

Key features and capabilities of `eksctl` include:

1. **Cluster Creation:** `eksctl` simplifies the process of creating an EKS cluster. It can create and configure the necessary AWS resources, such as Amazon Elastic Compute Cloud (EC2) instances for worker nodes and Amazon Virtual Private Cloud (VPC) components, and set up the EKS control plane.

2. **Cluster Configuration:** You can use `eksctl` to customize the configuration of your EKS cluster, including the type and size of worker nodes, node groups, and VPC settings.

3. **Scaling:** `eksctl` allows you to easily scale the number of worker nodes in your cluster to meet the demands of your applications.

4. **High Availability:** It helps configure your EKS cluster for high availability by spreading worker nodes across multiple Availability Zones.

5. **Integration:** `eksctl` integrates with AWS Identity and Access Management (IAM) for setting up roles and permissions, as well as AWS CloudFormation for managing AWS resources.

6. **Simplified CLI:** The `eksctl` command-line interface offers a simplified and user-friendly way to interact with EKS clusters, abstracting many of the complex AWS resource setup tasks.

7. **Updates and Upgrades:** It assists with cluster updates and upgrades, such as upgrading the Kubernetes version or applying changes to the cluster configuration.

8. **Add-ons:** `eksctl` supports the addition of various Kubernetes add-ons like VPC CNI, and it can deploy them as part of cluster creation.

By using `eksctl`, developers and administrators can accelerate the setup and management of EKS clusters, making it easier to run containerized applications on AWS with Kubernetes. It abstracts much of the underlying AWS infrastructure complexity, allowing users to focus on their applications and workloads.

## Argo CD
Argo CD is an open-source, declarative, GitOps continuous delivery tool for Kubernetes. It is designed to automate the deployment and management of applications on Kubernetes clusters by leveraging Git repositories as the source of truth for defining the desired state of your applications and environments.

Key features and concepts of Argo CD include:

1. **Declarative Configuration:** With Argo CD, you define the desired state of your applications and environments using declarative configuration files, which are typically stored in a Git repository. This approach makes it easy to version, audit, and manage your application configurations.

2. **GitOps:** Argo CD follows the GitOps operational model, where the Git repository serves as the single source of truth for your application configurations. Changes in the Git repository trigger automated deployment and synchronization of the desired state to your Kubernetes clusters.

3. **Multi-Cluster Support:** Argo CD can manage multiple Kubernetes clusters, making it suitable for multi-environment or multi-region deployments. It allows you to define applications once and deploy them consistently across various clusters.

4. **Application Definitions:** In Argo CD, applications are defined using a Kubernetes Custom Resource called `Application`. You specify the source repository, target cluster, and other configuration details in an `Application` resource.

5. **Health Status and Rollbacks:** Argo CD continuously monitors the health and synchronization status of applications. If a deviation from the desired state is detected, it provides insights into what went wrong and allows for easy rollbacks to previous configurations.

6. **Extensibility:** Argo CD can be extended through plugins and hooks, allowing you to integrate with external tools and services, customize workflows, and automate various tasks within your deployment pipeline.

7. **Secure and Access Control:** Argo CD provides features for securing access to your Git repositories and Kubernetes clusters. It integrates with Kubernetes RBAC for fine-grained access control.

8. **Web UI and CLI:** Argo CD offers both a user-friendly web-based interface and a command-line interface (CLI) for managing applications, monitoring deployments, and reviewing synchronization status.

Argo CD is a popular choice for organizations adopting GitOps practices to streamline Kubernetes application delivery. It simplifies the deployment process, enforces version control for configurations, and provides visibility into the state of your applications, making it easier to maintain a reliable and automated deployment pipeline.

## Resources
[Article 1](https://opensource.com/article/20/5/helm-charts)
[Examples Repo](https://github.com/argoproj/argocd-example-apps/tree/master)