# Trino
[Guide](https://github.com/trinodb/trino/tree/master/core/docker)
[AWS K8s Trino Guide](https://trino.io/episodes/31.html)

## How It Works
Trino is a distributed SQL query engine designed for querying and analyzing large volumes of data across multiple data sources. It provides a unified interface for querying data stored in various sources, such as data lakes, relational databases, and more. Trino's basic layout consists of several key components:

1. Coordinator Node:
   - The Coordinator Node is responsible for managing query execution. When a query is submitted to Trino, the Coordinator Node receives the query, plans its execution, and coordinates with other nodes to execute the query efficiently.
   - It maintains metadata about the system, including information about the available worker nodes and data sources.

2. Worker Nodes:
   - Worker Nodes are responsible for executing the actual tasks associated with a query. These tasks include scanning data, filtering, aggregating, and more.
   - Trino can have multiple Worker Nodes that can be horizontally scaled to handle large workloads.

3. Query Execution:
   - When a query is submitted, the Coordinator Node parses it, optimizes the execution plan, and distributes the tasks across the Worker Nodes.
   - Trino's query engine is designed for parallel and distributed processing, allowing it to execute queries quickly, especially when dealing with large datasets.

4. Connectors:
   - Trino supports a variety of data connectors, also known as connectors or plugins, which allow it to access data stored in various sources. Some common connectors include connectors for HDFS (Hadoop Distributed File System), Hive, MySQL, PostgreSQL, and many others.
   - Connectors are responsible for translating SQL queries into source-specific operations and fetching the data from the underlying data source.

5. Storage Systems:
   - Trino can query data stored in a wide range of storage systems, including data lakes (e.g., HDFS and S3), relational databases (e.g., MySQL, PostgreSQL), NoSQL databases, and more.
   - Trino's architecture allows it to query data across multiple data sources simultaneously, making it suitable for federated queries.

6. SQL Interface:
   - Trino provides a SQL-like query language that allows users to interact with and query the data stored in various sources using familiar SQL syntax. This SQL interface simplifies data analysis and retrieval.

7. Security:
   - Trino offers security features such as authentication and authorization, allowing organizations to control who can access and query their data.

8. Extensibility:
   - Trino is highly extensible and can be customized using connectors and functions to meet specific requirements and integrate with various data sources.

In summary, the basic layout of Trino includes a Coordinator Node that manages query execution and multiple Worker Nodes responsible for performing the actual query tasks. It connects to various data sources via connectors and provides a SQL interface for querying and analyzing data across these sources. Trino's distributed and parallel processing capabilities make it a powerful tool for big data analytics and querying data from diverse data stores.

### Glue Catalog
[Link](https://trino.io/docs/current/connector/metastores.html#aws-glue-catalog-configuration-properties)
[Link2](https://tabular.io/blog/docker-spark-and-iceberg/)
[Link3](https://github.com/myfjdthink/starrocks-iceberg-docker)

Dont fucking exec and run the trino CLI in a terminal lmfao, use a dedicated db management tool like datagrip or dbeaver
``` sh
docker exec -it trino-trino-1 trino


```


### Apache Iceberg
I guess they separate out the Glue & S3 Credentials incase you have 1 or the other in different accounts?

`etc/catalog/iceberg.properties`
```
connector.name=iceberg
iceberg.file-format=parquets
iceberg.catalog.type=glue
iceberg.file-format=parquet
hive.metastore.glue.region=us-east-1
hive.metastore.glue.aws-access-key=zzz
hive.metastore.glue.aws-secret-key=aaa
hive.metastore.glue.default-warehouse-dir=s3://jyablonski2-iceberg/
hive.metastore.glue.catalogid=717791819289
hive.s3.aws-access-key=zzz
hive.s3.aws-secret-key=aaa
```



## K8s Example
[Guide](https://www.youtube.com/watch?v=v9-mf69xMa0&t=4940s)

[eksctl Install](https://eksctl.io/installation/)

eksctl is the CLI Tool for creating & managing EKS Clusters.  When you create EKS Clusters using it, it autumatically adds an entry to your `~/.kube/config` file so that if `kubectl` is in your PATH, you will be able to use kubectl commands with the EKS Cluster.

From there you can just add a Helm Repo and run a `helm install` to boot up those resources on the new EKS Cluster.

This specific example then port forwards our own Port 8080 to the Coordinator Pod so that we can talk to that Pod and connect, make queries etc.  The normal way to do this is provision a dedicated Load Balancer Endpoint so you can connect that way instead.

This command boots up an EKS Cluster w/ 2 Worker Nodes ran in EC2.  At this point they aren't running anything yet or considered "Pods" yet, because we haven't told EKS to go run any applications yet.
``` sh
eksctl create cluster \
 --name tcb-cluster \
 --version 1.28 \
 --region us-east-1 \
 --nodegroup-name k8s-tcb-cluster \
 --node-type t2.large \
 --nodes 2

# wait for it to come up
# you'll see the 2 ec2 instances
# eksctl does some cool shit for u m8
kubectl get nodes

helm repo add trino https://trinodb.github.io/charts
helm install example-trino-cluster trino/trino

export POD_NAME=$(kubectl get pods --namespace default -l "app=trino,release=tcb,component=coordinator" -o jsonpath="{.items[0].metadata.name}")
echo $POD_NAME
# example-trino-cluster-coordinator-78976565-k8d5z
kubectl port-forward $POD_NAME 8080:8080

kubectl get deployments

kubectl delete service --all
kubectl delete deployment --all
kubectl delete configmap --all

eksctl delete cluster --name test-cluster --region us-east-1
```

![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/ee47cc03-2310-4739-a083-abe84195121c)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/83818f96-5b66-4eaa-b34f-87056f5c401c)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/de07fb11-09d3-46e2-a4bb-c6d68a03b76d)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/6d2ed064-ad24-4b07-8d81-04900c8740e9)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/d8cf1e29-a677-4c29-976b-6ce3643bbfb4)
