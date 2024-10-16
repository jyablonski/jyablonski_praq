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

``` yaml
image:
  repository: your-docker-registry/nba_elt_rest_api
  tag: latest
service:
  port: 8080
```

`templates/deployment.yml`

``` yaml
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

commands

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

In a traditional CI CD Pipeline to K8s without Argo CD, you have to update a Docker Image for your App, update the K8s Deployment File to point to the new Image, and run `kubectl apply` to apply the changes. But, your GitHub Actions or Jenkins tool running the CD really has no idea what happens to the App after that, whether it's in a functional state or if it's failing, and all that. At scale across many microservices, this doesn't scale well.

Argo CD is a part of your K8s Cluster. An Argo CD agent pulls changes from the Git Repository where it's hooked up to look for changes. Any changes will force Argo CD to pull those changes and apply them.

- Your App CD Pipeline might now push a new Docker Image for the codebase, adn update the K8s Manifest File in that Repo. Then, Argo CD will pull those changes on the manifest file and apply them in your K8s Cluster.
- Argo CD is essentially de-coupled here
- Best Practice to have separate repos for Application Source Code and Application Configuration Code (K8s manifest files) which can be changed independently of source code
- If you want to change 1 of these, the other 1 shouldnt have to be affected.

Argo CD has support for Kubernetes YAML Files, Helm Charts, or Kustomize Files. It also guaratnees that the K8s Manifests from the Git Repo remain the source of truth so people cant make manual direct changes.

If a new version fails to start, Argo CD can immediately rollback to the previous working version. It can also re-create 100% of resources in a new EKS Cluster if you swap regions or the existing K8s Cluster goes down, it can do this because everything about the cluster is defined in Git through code.

Example Argo CD File

``` yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-argo-application
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://gitlab.com/nanuchi/argocd-app-config.git
    targetRevision: HEAD
    path: dev
  destination: 
    server: https://kubernetes.default.svc
    namespace: myapp

  syncPolicy:
    syncOptions:
    - CreateNamespace=true

    automated:
      selfHeal: true
      prune: true

```
## K8s Files

1. `deployment.yaml` - Config files used to define and manage deployments.  You typically specify a container image to run, give it a name, how many replicas it should have, and what port it will run on

2. `service.yaml` - Config files used to specify what ports should be exposed on the pods running your application

3. `ingress.yaml` - Config files used to define rules for routing eternal HTTP(S) traffic to your pods

- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/568cfab1-2b6f-44d5-8c1d-ab9a8024ac35)

1. `secrets.yaml` - Config file used to define sensitive data such as passwords, API Tokens, SSH keys etc in key value pairs to be used in your applications running in K8s via environment variables.

2. `config_map.yaml` - Config file used to define non-sensitive data in key value pairs to be used in your applications running in K8s via environment variables.

## Required Fields in K8s Files

1. `apiVersion` - The Version of the Kubernetes API to create the object

2. `kind` - The kind of Object to create `Deployment`, `Service` etc

3. `metadata` - Data to uniquely identify the object like a `name`, `namespace` etc

4. `spec` - The desired state for the object

## Service Accounts vs Worker Node Permissioning

[Article](https://shipit.dev/posts/setting-up-eks-with-irsa-using-terraform.html)

Service Accounts are a type of Kubernetes resource used to provide an identity for pods running within the cluster. They are particularly useful for granting specific permissions to pods that need to interact with the Kubernetes API or other AWS services securely.

IAM Role for Service Accounts (IRSA) is a mechanism to allow EKS Pods to assume an IAM Role for various AWS Permissions.  The idea here is you might have multiple different pods running on a worker node in EKS; if you assigned an IAM Role at the worker node level then all pods would be forced to use the same IAM Role which may or may not be ideal.  Service Accounts enable a finer grain of detail and allow you to separate out the IAM Role being used by Pod / Deployment.


``` yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_IAM_ROLE_NAME
```

``` yaml
apiVersion: v1
kind: Deployment
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account
  containers:
  - name: my-container
    image: my-image
```

## Managing EKS Cluster Access

Managing access to an EKS cluster involves a combination of several strategies to ensure security, appropriate access levels, and efficient operations. Here are the primary methods to control access to an EKS cluster:

### 1. **Kubernetes Role-Based Access Control (RBAC)**
Kubernetes RBAC allows you to define roles and bind them to users or groups, controlling what actions they can perform within the cluster.

- **Roles and ClusterRoles**: Define sets of permissions. Roles are namespace-scoped, while ClusterRoles are cluster-scoped.
- **RoleBindings and ClusterRoleBindings**: Bind roles to users, groups, or service accounts.

Example Role and RoleBinding:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: "example-user" # Username or group from your identity provider
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 2. **AWS Identity and Access Management (IAM)**
IAM roles and policies control who can perform actions on AWS resources, including EKS clusters.

- **Cluster Creation IAM Role**: When creating an EKS cluster, you specify an IAM role that EKS uses to manage AWS resources.
- **IAM Users and Roles for Kubernetes API Access**: Configure IAM users and roles to have permissions to interact with the Kubernetes API.

To map IAM roles and users to Kubernetes RBAC, use the `aws-auth` ConfigMap in the `kube-system` namespace:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::ACCOUNT_ID:role/EKSAdminRole
      username: eks-admin
      groups:
        - system:masters
  mapUsers: |
    - userarn: arn:aws:iam::ACCOUNT_ID:user/admin
      username: admin
      groups:
        - system:masters
```

### 3. **Amazon EKS Managed Policies**
EKS provides managed IAM policies that you can attach to IAM roles to grant necessary permissions for interacting with the cluster.

- **AmazonEKSClusterPolicy**: Grants permissions needed by EKS to manage the cluster.
- **AmazonEKSServicePolicy**: Grants permissions needed by EKS managed services.
- **AmazonEKSCNIPolicy**: Grants permissions for the Amazon VPC CNI plugin to modify network interfaces.

### 4. **Network Access Control**
Control network access to the EKS cluster using security groups and network policies.

- **Security Groups**: Control inbound and outbound traffic to the worker nodes and the control plane.
- **Network Policies**: Use Kubernetes Network Policies to control traffic between pods within the cluster.

Example Network Policy:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-nginx
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: nginx
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: client
    ports:
    - protocol: TCP
      port: 80
```

### 5. **Private Endpoint Access**
Restrict access to the EKS cluster API endpoint to specific CIDR blocks or make it private so that it can only be accessed from within the VPC.

- **Public Access**: The API server endpoint is accessible from the internet. You can restrict it by specifying allowed IP CIDR blocks.
- **Private Access**: The API server endpoint is accessible only from within the VPC.

Configure endpoint access when creating the cluster or update it later using the AWS Management Console, CLI, or API.

### 6. **AWS Single Sign-On (SSO)**
Integrate AWS SSO with EKS to manage user access through your identity provider.

- **Configure AWS SSO**: Set up SSO and link it with your directory (e.g., Active Directory, Google Workspace).
- **IAM Identity Provider**: Configure EKS to recognize users authenticated via AWS SSO.

## Scaling

The Kubernetes Horizontal Pod Autoscaler (HPA) is the Kubernetes Resource that defines how pods should be horizontally scaled in a Deployment. When the conditions are met the HPA will create new Pods, and when the load decreases and the # of pods is < the configured minimum, the HPA scales the pods back down.

- **NOTE** that if some of the Pod's containers do not have the relevant resource request set, CPU utilization for the Pod will not be defined and the autoscaler will not take any action for that metric

Below is an example where we're defining a Deployment and setting some CPU + Memory Limits

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: my-image
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```

```
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: my-deployment-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 65
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 75
```

## Simple Definitions

- ConfigMap: Storage for simple key-value data
- Container: Process Isolation
- CronJob: Run Jobs on a schedule
- DaemonSet: Run a Pod on every node
- Deployment: Smoothly making changes to a set of Pods
- Docker Image: Delivery of programs and files
- HorizontalPodAutoscaler: Use metrics data to scale up or down a Deployment
- Ingress: Network traffic entry point
- Job: Run a Pod until exit
- PersistentVolumeClaim: Disk
- Pod: Runable, one or more containers and configuration
- ReplicaSet: Scales up and down a set of Pods
- Secret: Storage for complex key-value data
- Service: DNS name and load balancer
- StatefulSet: Run `n` Pods with consistent names

## Resources

[Article 1](https://opensource.com/article/20/5/helm-charts)

[Examples Repo](https://github.com/argoproj/argocd-example-apps/tree/master)

[Example Repo v2](https://github.com/ghik/kubernetes-the-harder-way)
