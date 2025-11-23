# Homelab Setup

[GitHub Link](https://github.com/dreamsofautonomy/homelab)

## Hardware

[Beelink Machines](https://www.amazon.com/Beelink-Lake-N100-Mini-Computer-Supports-Home-Server/dp/B0C339KVH9?crid=EQ0ZS9IJIVY3&dib=eyJ2IjoiMSJ9.14XD7vNJqMpk6Q7CHMy1vpjo9EXS5DV6pEtWUE-pUdJT7S6J-HtgdLxYwl7i5BHsCXVXRlwlfFQTmMP-AUZ-NBbdRu4ZDpDzONRF7praT_QVyIpwFN7RktSvogMTxV_VuWKgB1eil8wESOxwd3SEzmcWNc9uRPVvGhmNMfb-Z4MsF2mqVRGZg0ou7KFpCOLi679lQbKLXmg5_9w5vNWSYTz9WQkTkVVH6N2ZSCPDKf8.JhsWHDjC_QIFUWOAdfkCRxBGni0Wk_AWu-DfmXP6VCM&dib_tag=se&keywords=beelink%2Beq12&qid=1720927908&sprefix=beelink%2Beq12%2Caps%2C120&sr=8-3&th=1&linkCode=sl1&tag=dreamsof02-20&linkId=9dd812aeea649fe86a11aadb36763854&language=en_US&ref_=as_li_ss_tl)

You need bare metal machines to host K8s Master node and the Worker Nodes to run the services in the cluster. Buying 3 is recommended.

- One of the Beelink EQ14 Mini PCs can serve as the control plane node (master node) in your Kubernetes setup. This node will run the Kubernetes control plane components such as kube-apiserver, kube-scheduler, kube-controller-manager, etc.
- The other two Beelink EQ14 Mini PCs would serve as worker nodes, which will run your application workloads, such as containers, pods, services, etc.
- While three nodes are enough for a basic setup, this configuration is not highly available (HA) for the control plane.
- In production or for more fault-tolerant setups, you would typically run at least 3 control plane nodes with etcd replication across the nodes to prevent downtime in case of failures.

## Software

### Home Assistant

Home Assistant is an open source platform for managing smart home devices and automating tasks. It acts as the hub for all the devices to connect to, and enables you to manage all of them via 1 app + interface.

It integrates with:

- Lights
- Thermostats
- Cameras
- Sensors
- Speakers

You can create advanced automation scripts and workflows to trigger based on things like time of day, device states, or user presence

- Example: Turn off all lights when no one is home, or adjust the thermostat based on outdoor weather conditions.

Also features a customizable dashboard for monitoring and controlling devices.

### Longhorn

Longhorn is a distributed storage solution for K8s Clusters. It provides persistent storage for containerized workloads and can be paired with a Database like Postgres

- Longhorn creates distributed storage volumes across multiple nodes in your Kubernetes cluster.
- Volumes are exposed as PersistentVolumes (PVs) in the cluster
- This ensures data is not lost even if pods or nodes fail
- Each volume is backed by multiple replicas spread across different nodes, ensuring high availability and resilience to node failures.
- Pods then claim the PVs with PersistentVolumeClaims (PVCs)
- Has automated scheduled backup functionality
- Has a UI for managing storage, and a CLI and API for advanced operations

[Blog Post](https://medium.com/@camphul/cloudnative-pg-in-the-homelab-with-longhorn-b08c40b85384)

### MetalLB

MetalLB is a load balancer for Kubernetes clusters that provides external access to services by assigning IP addresses to services. It is particularly useful for environments like home labs, where you may not have access to a cloud provider's load balancer service (e.g., AWS, GCP, Azure), but still need to expose Kubernetes services to the external network.

It also assigns IP Addresses to Services after you define a pool of available IPs

---

### Pi-hole

Pi-hole enables you to setup local DNS records on your homelab, so you can hit your services at something like `http://pihole.home` instead of `192.168.1.15`.

---

### NGINX

The Ingress NGINX Controller is a Kubernetes Ingress Controller that uses NGINX as a reverse proxy and load balancer to manage external access to services within a Kubernetes cluster. It acts as the gateway for all incoming HTTP(S) traffic, routing the traffic to the appropriate backend services based on the rules defined in Kubernetes Ingress resources.

NGINX-internal can be used so it's only enabled for your local area network (LAN).

## Cluster Architecture

- 1 node runs as master (server), hosting control plane.
- 2 nodes run as workers to run workloads.
- Total RAM for workloads depends on whether master is tainted (which means it exclusively runs the cluster, and doesn't host any workloads):
  - Master tainted (dedicated control plane): workloads use ~64GB (2 workers × ~32GB).
  - Master untainted (mixed roles): workloads use ~96GB (all nodes).

## Networking

- All nodes connect via Ethernet to the same router or switch (same LAN).
- Master node IP (e.g., 192.168.1.10) used by workers to join cluster.
- Kubernetes API server runs on port 6443 on master node.
- Ensure firewall allows traffic between nodes on required ports.

## Master Node Setup

- Install k3s server on master node:
  ```bash
  curl -sfL https://get.k3s.io | sh -
  ```

````

* Retrieve the node join token:

  ```bash
  sudo cat /var/lib/rancher/k3s/server/node-token
````

## Worker Node Setup

- On each worker, install k3s agent and join cluster:

  ```bash
  curl -sfL https://get.k3s.io | K3S_URL=https://<MASTER_IP>:6443 K3S_TOKEN=<NODE_TOKEN> sh -
  ```

- Replace `<MASTER_IP>` and `<NODE_TOKEN>` with master node IP and join token.

## Tainting Master Node

- By default, k3s does not taint the master node.
- To dedicate master node and prevent workloads scheduling there:

  ```bash
  kubectl taint nodes <master-node-name> node-role.kubernetes.io/master=:NoSchedule
  ```

- To allow workloads on master node (remove taint):

  ```bash
  kubectl taint nodes <master-node-name> node-role.kubernetes.io/master:NoSchedule-
  ```

## Summary

- Connect all nodes physically via Ethernet on the same LAN.
- Master runs k3s server; workers run k3s agent.
- Workers join cluster using master IP and token.
- Decide on tainting master based on workload/resource needs.
