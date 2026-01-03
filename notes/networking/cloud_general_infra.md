# General Cloud Infrastructure

## Availability Zones and Regions

Availability Zones (AZs):

- Physically separate data centers within a region
- Independent power, cooling, and networking
- Connected via low-latency private fiber (single-digit ms latency)
- AZ identifiers (us-west-2a) are mapped randomly per account

Regional failures:

- Rare but possible—correlated failures from network backbone issues, power grid failures, or natural disasters
- Control plane failures can prevent provisioning even if compute is running
- US-East-1 has had region-wide degradations multiple times

Multi-region considerations:

- Required for true HA against regional outages
- Expensive and complex (async replication, DNS failover, conflict resolution)
- Most workloads accept regional outage risk given low probability

______________________________________________________________________

## Pricing: Multi-AZ and Data Transfer

Infrastructure costs:

- Pay for each resource in each AZ (3 instances across 3 AZs = 3x cost)
- RDS Multi-AZ is roughly 2x single instance pricing

Cross-AZ data transfer:

- ~$0.01/GB in each direction ($0.02/GB round trip)
- Applies to: app servers talking to databases, load balancer distribution, Kafka/Elasticsearch replication, Kubernetes pod communication across nodes

Cross-region data transfer:

- More expensive (~$0.02/GB or more)
- Higher latency (tens to hundreds of ms)
- Usually requires async replication

What's free/cheaper:

- Traffic within the same AZ is free
- S3 is regional, no cross-AZ charges for S3 access

High data transfer cost scenarios:

- Analytics pipelines moving large datasets (S3 to EMR/Spark)
- Heavy ETL workloads
- Distributed systems with replication (Kafka, Elasticsearch, Cassandra)
- Chatty microservices architectures
- Internet egress (~$0.09/GB)
- NAT Gateway traffic ($0.045/GB processing fee + data transfer)
- Cross-region backups and DR replication

Cost optimization:

- Compression (gzip, brotli, lz4, zstd) - text compresses 70-90%
- Binary serialization (protobuf, avro) instead of JSON
- AZ-aware routing to keep traffic local
- Caching to avoid redundant transfers

______________________________________________________________________

## HA Cost-Benefit Analysis

The decision framework: compare mitigation cost against expected risk cost.

Example calculation:

- Regional outages: ~2-3 hours/year average
- Cost per hour of outage: $50k
- Expected annual loss: $100-150k
- If multi-region costs $500k/year, it doesn't make financial sense purely on numbers

Additional factors:

- Reputational damage (hard to quantify)
- Contractual SLA penalties
- Regulatory requirements for geographic redundancy
- Customer concentration risk

Tiered approach:

- Tier 1 (revenue-critical): Consider multi-region
- Tier 2 (important, can tolerate short outages): Multi-AZ
- Tier 3 (internal tools, batch jobs): Single AZ acceptable

______________________________________________________________________

## VPC and Networking Fundamentals

VPC (Virtual Private Cloud):

- Isolated network within AWS
- Defined by CIDR block (e.g., 10.0.0.0/16 = 65,536 IPs)
- Everything you deploy lives inside a VPC

Subnet:

- Subdivision of VPC's IP range, tied to a single AZ
- Example: 10.0.1.0/24 = 256 IPs in us-east-2a

Public subnet:

- Has route to Internet Gateway (IGW)
- Resources can have public IPs
- Where you put: load balancers, bastion hosts, NAT gateways

Private subnet:

- No direct internet route
- Outbound access via NAT Gateway
- Where you put: application servers, databases, worker nodes

Key components:

- Route table — Rules for where traffic goes
- Internet Gateway (IGW) — Door between VPC and public internet
- NAT Gateway — Lets private resources make outbound connections without being directly reachable
- Security Groups — Stateful firewalls on resources (by port and source)
- NACLs — Stateless firewalls at subnet level
- VPC Peering / Transit Gateway — Connect multiple VPCs
- Endpoints — Talk to AWS services without going through public internet

Traffic flow pattern:

```
Inbound:  Internet → Load Balancer (public) → Pods (private)
Outbound: Pods (private) → NAT Gateway (public) → Internet
```

______________________________________________________________________

## EKS Architecture

Control plane (AWS-managed):

- API server, etcd, scheduler, controller manager run in AWS's account
- You don't see or pay for those EC2 instances directly (baked into EKS fee)
- AWS puts ENIs into your subnets for control plane ↔ worker communication

Worker nodes (your VPC):

- EC2 instances or Fargate tasks in your subnets
- Where pods actually run
- You pay for these directly

EKS is regional:

- Cluster can only provision resources in its region
- Multi-region requires separate clusters with your own coordination layer

Subnet configuration:

- You specify VPC and subnets when creating cluster
- Subnet selection determines AZ spread
- EKS requires subnets in at least 2 AZs for control plane HA

AWS VPC CNI:

- Default CNI for EKS
- Each pod gets a real VPC IP address (not overlay network)
- Pod IPs are routable within VPC like EC2 IPs
- No encapsulation overhead
- Can burn through IPs fast with many pods

Networking setup:

- `eksctl` with defaults creates VPC, subnets, NAT gateways automatically
- Bring-your-own-VPC requires proper route tables and NAT gateway configuration
- Without NAT gateway, pods can't reach external APIs or pull images

______________________________________________________________________

## EKS Costs (Minimal Idle Cluster)

| Component | Hourly | Monthly |
| ------------------------- | ------- | --------- |
| EKS control plane | $0.10 | ~$73 |
| NAT Gateway (per gateway) | $0.045 | ~$32 |
| Worker node (t3.medium) | $0.0416 | ~$30 |
| EBS root volumes | - | ~$0.10/GB |
| ALB (if created) | $0.0225 | ~$16 |

Often overlooked:

- CloudWatch Logs (if control plane logging enabled)
- Elastic IPs (free while attached to NAT)

Realistic minimums:

- Single-AZ, one node, one NAT: ~$130-150/month idle
- Multi-AZ, multiple NAT gateways, few nodes: ~$250-400/month idle

______________________________________________________________________

## Logging with Prometheus/Grafana/Loki Stack

Loki architecture:

- Runs in your cluster (ingester, querier, compactor pods)
- Stores chunks and indexes to S3
- Promtail or Fluent Bit ships logs to Loki

S3 costs:

- Storage: ~$0.023/GB/month (Standard)
- 30-day retention with 10GB/day = ~300GB stored = ~$7/month
- PUT requests: $0.005 per 1,000
- GET requests: $0.0004 per 1,000

Compliance/permanent logs:

- Glacier Instant Retrieval: ~$0.004/GB/month
- Glacier Deep Archive: ~$0.00099/GB/month

Sneaky costs:

- CloudWatch ingestion: $0.50/GB (avoid double-shipping)
- Cross-AZ traffic if Loki components spread across AZs
- EBS for ingester write-ahead logs

Disabling CloudWatch logging:

EKS control plane logs:

```bash
aws eks update-cluster-config \
  --name your-cluster \
  --logging '{"clusterLogging":[{"types":["api","audit","authenticator","controllerManager","scheduler"],"enabled":false}]}'
```

Terraform:

```hcl
enabled_cluster_log_types = []
```

Container logs only go to CloudWatch if you installed something that ships them there (Fluent Bit with CloudWatch output, CloudWatch agent). If using Loki, ensure Fluent Bit config only has Loki output.

Check for existing log groups:

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/eks/
aws logs describe-log-groups --log-group-name-prefix /aws/containerinsights/
```

Cost control tips:

- Be selective about log levels (skip debug in prod)
- Drop high-cardinality fields
- Sample verbose logs
- Verify retention policies are working
