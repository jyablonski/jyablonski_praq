# Kubernetes
[Tutorial Video](https://www.youtube.com/watch?v=X48VuDVv0do)

Orchestration tool developed by Google to manage containers at scale.  Its growth came from the following developments:
- Trend from Monolith Applications to Microservices
- Widespread increased usage of Containers from Docker

Kubernetes enables:
- High Availability
- Scalability
- Disaster Recovery

## Pods
A Pod is the smallest unit of K8s, it's an abstraction over a Docker Container
- It creates a layer on top of a Docker Container so K8s can abstract away Container runtime so you can interact with the containers via Kubernetes Layer instead.
- Usually 1 Application per Pod
- Each Pod gets its own IP Address, not the container
- Pods communicate with each other via IP Address
- Pods are ephemeral; they can die or crash but a new one will get created in its place & gets assigned a new IP Address.
- Pods are usually built through an abstraction called **deployments**

## Service
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

## Secret
Just like Config Map except it's used to store Secret Data such as Credentials, Keys, Certificates etc.
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


## How It All Works
1. You create a Deployment
2. The Deployment creates a ReplicaSet
3. The ReplicaSet creates Pods
4. Pods, which actually run the workloads, are abstractions of a Container


## Minikube
1 Node Cluster where Master + Worker Node processes can run on 1 machine for people to practice & gain experience.
- It creates a VirtualBox on your machine where everything runs.