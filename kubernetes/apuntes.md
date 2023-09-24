# Kubernetes
[Tutorial Video](https://www.youtube.com/watch?v=X48VuDVv0do)

Orchestration tool developed by Google to manage containers at scale.  Its growth came from the following developments:
- Trend from Monolith Applications to Microservices
- Widespread increased usage of Containers from Docker

Kubernetes enables:
- High Availability
- Scalability
- Disaster Recovery

## Kubectl
Kubectl is a command-line tool to interact with Kubernetes Clusters.  
- Allows users to perform various operations on K8s Clusters like deploying applications, managing pods, creating and managing services, managing configurations, and more.

Common Commands include:
``` sh
kubectl create: Creates resources such as deployments, services, or pods.
kubectl get: Retrieves information about resources.
kubectl describe: Provides detailed information about a specific resource.
kubectl apply: Applies configurations from a file to create or update resources.
kubectl delete: Deletes resources.
kubectl scale: Changes the number of replicas for a deployment or replication controller.
kubectl logs: Retrieves the logs of a pod.
```

## Pods
A Pod is the smallest unit of K8s, it's an abstraction over a Docker Container
- It creates a layer on top of a Docker Container so K8s can abstract away Container runtime so you can interact with the containers via Kubernetes Layer instead.
- Usually 1 Application per Pod
- Each Pod gets its own IP Address, not the container
- Pods communicate with each other via IP Address
- Pods are ephemeral; they can die or crash but a new one will get created in its place & gets assigned a new IP Address.
- Pods are usually built through an abstraction called **deployments**

## Deployments
A Deployment in Kubernetes is a resource that allows you to describe, declare, and manage how your application should be deployed and updated. It defines a desired state for a set of replica pods and manages the deployment, scaling, and updating of these pods. Deployments help in ensuring that a specified number of pod replicas are running at any given time, and it also supports rolling updates and rollbacks to application versions.

Key features of a Deployment:
   - **Pod Management:** Manages a set of replica pods based on a template.
   - **Rolling Updates:** Allows updating the application without downtime using a rolling update strategy.
   - **Rollback:** Enables rolling back to a previous version in case of issues with the new update.

Example use case: Deploying a web application with a specified number of replicas and managing updates without affecting service availability.

## Service
A Service in Kubernetes is a resource that defines a logical set of pods and a policy by which to access them. Services provide a stable endpoint (an IP address and a port) for accessing the application pods, abstracting away the individual pod IP addresses and providing load balancing across the pods. There are different types of services, such as ClusterIP, NodePort, LoadBalancer, and ExternalName, each serving different purposes for accessing the application.

Key features of a Service:
   - **Service Discovery:** Allows other parts of the application to discover and communicate with the service.
   - **Load Balancing:** Distributes incoming requests across the pods associated with the service.
   - **Stable Network Endpoint:** Provides a stable network address for accessing the application.

Example use case: Exposing a web application to the outside world, allowing clients to access the application via a defined IP address and port.

Service is a static, permanent IP Address that can be attached to each Pod
- Even if Pod dies, its IP Address will stay the same when the new Pod gets spun up
- Also acts as a load balancer.  It can take incoming requests and forward them to a Pod that is the least busy.

2 Kinds: External and Internal

External Services allows for Pods to serve Applications publicly over the Internet
- Initial URL looks like `http://124.42.43.2:8080`
- But you want a URL to look like `https://api.jyablonski.dev`
- To get the Proper URL to need to use Ingress to forward users that hit the proper URL to the External Service

Internal Service
- Example: a Database

If you wanted a Service with 2 Nodes to serve traffic, you don't want to create 2 Pods. You create a blueprint for Pods and specify how many **replicas** you want for that Pod.
- These are called **deployments**
- Things like Databases can have replicas, but they can't be done through deployments because a Database has a State
- All Clones or Replicas all need access to same shared Database and which Pods are currently reading or writing to that storage to avoid data inconsistencies.
- StatefulSet is built to handle this
  - Things like ElasticSearch or MongoDB should be built with this
  - Not an easy process however
  - Another reason why DBs are often hosted outside of K8s Cluster

## Ingress
An API Object that manages external access to services in a cluster, typically HTTP.
- Provides load balancing, SSL termination, routing rules, and other networking goodies

## Config Map
External configuration for your application
- URLs for your Databases
- Connect the Config Map to your Pod so your Service can use these configuration parameters that are set in this file.
- Credentials do **NOT** go into the Config Map
- Config Map is used for non-sensitive configuration data
- Values are stored in plaintext

## Secret
Just like Config Map except it's used to store Sensitive Information such as Credentials, Keys, Certificates etc.
- Not stored in plaintext, it's **Base64 Encoded**

## Volumes
Volumes are used for Data Storage
- If the Pod for a Database gets restarted, then the data would be gone
- The way to get around this is to use Volumes

Volumes attaches a physical storage to your Pod
- Could be physical storage on the local machine
- Or could be remote, outside of the K8s Cluster
- Storage can either be local or remote storage
- K8s **doesn't** manage data persistance

## Nodes
Nodes are the Kubernetes Worker Nodes where things run.
- Each Node can have multiple Pods in it

Each Node has 3 processes that must be installed on it:
- Container Runtime (Python, Java, etc)
- Kubelet which interacts with both the Container Runtime and the Node
- Kube Proxy forwards requests in a performant way w/ low overhead

Master Node - control Cluster State and the worker nodes.  They have 4 processes inside:
- API Server which K8s Users can interact with
  - Main Entrypoint into the K8s Cluster
- Cluster Gateway - acts as a gatekeeper for authentication in order to execute certain actions
- Scheduler - Takes validated requests and figures out where to schedule new Pods among the Worker Nodes
  - For Example, if Node 1 is at 30% utilization and Node 2 is at 60% utilization, the Scheduler will start a new Pod in Node 1
- Controller Manager - It detects State changes like Pods dying, and it'll try to recover the Cluster state ASAP
  - It reaches out to the Scheduler and figures out Pods need to be restarted
- etcd - Key Value Store.  The Cluster Brain.
  - All Cluster changes get stored in this key value store
- Can have multiple Master Nodes in a Cluster, running on separate machines


Slave Node - The Worker Nodes that actually run the Applications & Workloads

## Replicas
You never have to edit or change Replicas directly, you just work w/ them through deployments.
- Can configure the Pod Blueprint directly and do all the configuration there

## Namespaces
In Kubernetes, a namespace is a way to divide cluster resources between multiple users, projects, or teams. It provides a scope for names and allows different sets of objects to have the same names within different namespaces. This helps in organizing and isolating various resources within a cluster.

Key points about Kubernetes namespaces:

1. **Isolation and Scope:**
   - Namespaces provide a level of isolation for cluster resources. Objects within a namespace can have names that collide with the names of objects in other namespaces, but they are unique within the namespace.

2. **Resource Quotas and Limits:**
   - Resource quotas can be set at the namespace level to limit the amount of CPU, memory, and other resources that can be used by the objects within that namespace.

3. **Access Control:**
   - Kubernetes RBAC (Role-Based Access Control) can be applied at the namespace level, allowing for fine-grained control over who can access and modify resources within a specific namespace.

4. **Use Cases:**
   - **Multi-tenancy:** Different teams or projects can use their own namespaces, allowing for isolation and management of their own resources without interfering with others.
   - **Development, Staging, Production:** Namespaces can be used to separate environments, making it easier to manage resources for development, testing, staging, and production.

5. **Default Namespace:**
   - When resources are created without specifying a namespace, they are placed in the "default" namespace by default.

6. **Listing and Switching:**
   - You can list all namespaces in a cluster using the `kubectl get namespaces` command. To switch to a different namespace, you can use `kubectl config set-context --current --namespace=<namespace>`.

Example use cases:
- Company "A" might have a namespace called "prod" for their production environment, and another namespace called "dev" for their development environment.
- Company "B" might have their own set of namespaces named "stage" and "test" for different stages of their application.

Namespaces help in organizing and managing resources within a Kubernetes cluster, especially in environments where multiple applications or teams are using the same cluster.

## Helm
Helm is an open-source package manager for Kubernetes, which streamlines the deployment, management, and scaling of applications. It allows you to define, install, and upgrade even the most complex Kubernetes applications in a consistent and efficient manner.

Here are the key components and functionalities of Helm:

1. **Charts:**
   - Helm packages are called "charts." A chart is a collection of pre-configured Kubernetes resources, such as deployments, services, ConfigMaps, and more, packaged together for a specific application.

2. **Templates:**
   - Charts contain templates, which are essentially Kubernetes manifest files with placeholders (in Go templating format) for values that can be customized during installation.

3. **Values:**
   - Values are customizable parameters that can be provided to the templates. These values can be specified during installation or stored in a separate file. Values allow you to customize the behavior and configuration of the application.

4. **Repositories:**
   - Helm repositories are locations (local or remote) where Helm charts are stored. Users can pull charts from these repositories to install applications.

5. **Commands:**
   - Helm provides a set of CLI commands to interact with charts and Kubernetes. For example, you can use commands like `helm install`, `helm upgrade`, `helm delete`, etc., to manage the lifecycle of applications.

Key benefits of using Helm include:
- **Reusability:** Helm charts can be shared and reused, saving time and effort in setting up applications.
- **Consistency:** Helm ensures consistent application deployments by packaging all the necessary resources and configurations into a single chart.
- **Versioning and Rollbacks:** Helm enables versioning of releases, making it easy to roll back to previous versions if needed.
- **Customization:** Users can customize Helm charts using values to fit their specific requirements.
- **Community and Ecosystem:** Helm has a vibrant community that contributes to the creation and maintenance of Helm charts, enhancing the ecosystem and making it easier to find and use existing charts.

In summary, Helm simplifies the process of managing Kubernetes applications by providing a standardized way to package, deploy, and manage applications in Kubernetes clusters using charts and customizable values.

## How It All Works
1. You create a Deployment
2. The Deployment creates a ReplicaSet
3. The ReplicaSet creates Pods
4. Pods, which actually run the workloads, are abstractions of a Container


## Minikube
1 Node Cluster where Master + Worker Node processes can run on 1 machine for people to practice & gain experience.
- It creates a VirtualBox on your machine where everything runs.

