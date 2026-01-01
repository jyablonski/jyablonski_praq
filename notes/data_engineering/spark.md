## Apache Spark

Apache Spark is an open-source distributed computing system designed for big data processing and analytics. Apache Spark is widely used in various industries for big data processing, analytics, and machine learning due to its performance, scalability, and versatility in handling diverse data processing workloads.

Key features of Apache Spark include:

1. **In-Memory Processing**: Apache Spark processes data in-memory, allowing for faster data processing and iterative analytics. It keeps data in memory rather than persisting it to disk after each operation, which enhances performance.

1. **Distributed Computing**: Spark distributes data and computation across a cluster of machines, enabling parallel processing and efficient utilization of resources.

1. **Versatile Data Processing**: Spark supports various data processing workloads, including batch processing, real-time streaming, machine learning, and graph processing. It provides a unified platform for these diverse workloads.

1. **Resilient Distributed Datasets (RDDs)**: RDDs are the fundamental data structure in Spark that represents a distributed collection of objects. RDDs are fault-tolerant and can be operated on in parallel. They can be created from HDFS files, distributed over a cluster, and operated upon using transformations and actions.

1. **Streaming Data Processing**: Spark Streaming allows processing of real-time streaming data and integrates with various sources like Kafka, Flume, or TCP sockets. It processes data in micro-batches, making it suitable for real-time analytics.

1. **Machine Learning (MLlib)**: MLlib is Spark's machine learning library, providing a wide range of machine learning algorithms and tools for scalable machine learning tasks.

1. **SQL and DataFrames**: Spark provides SQL and DataFrame APIs for working with structured data, making it easier for users familiar with SQL to query and manipulate data.

1. **Integration with Hadoop Ecosystem**: Spark can run on Hadoop YARN, can read data from HDFS, and can integrate with Hadoop components like Hive and HBase.

1. **Ease of Use**: Spark offers user-friendly APIs in various programming languages like Scala, Java, Python, and R. It also provides interactive shells for easy experimentation and development.

## Key Components

1. **Spark Core**:

   - The foundational component of Spark that provides the basic functionality for distributed data processing.

   - It includes the fundamental data structures (like RDDs), parallel processing capabilities, and APIs for distributed computing.

1. **Resilient Distributed Datasets (RDDs)**:

   - RDDs are the primary data abstraction in Spark, representing an immutable, fault-tolerant distributed collection of objects.

   - They serve as the basis for distributed transformations and actions in Spark applications.

1. **Spark SQL**:

   - Provides a programming interface to work with structured data using SQL and supports querying data with SQL-like queries.

   - It also supports working with DataFrames, which are structured collections of data, similar to tables in a relational database.

1. **Cluster Manager (e.g., Standalone, Apache Mesos, YARN)**:

   - Spark can run on various cluster management systems, including its standalone cluster manager, Apache Mesos, and Apache Hadoop YARN. These manage resources and scheduling across the cluster.

1. **Driver Program and Executors**:

   - The driver program is the main application that runs the user's Spark job. Executors are processes launched by the driver on worker nodes to perform computations and store data for RDDs.

1. **Spark Packages and Libraries**:

   - In addition to the core components, Spark has a vibrant ecosystem of libraries and packages developed by the community, addressing various use cases such as data connectors, visualization, integration with other systems, and more.

## Data Structures

1. **RDD (Resilient Distributed Dataset)**:

   - RDD is the fundamental data structure in Spark, representing an immutable distributed collection of objects that can be processed in parallel.

   - It provides low-level transformation and action operations, allowing users to perform operations at the element level.

   - RDDs are dynamically typed and can hold any type of Python object. This flexibility allows for more complex and unstructured data processing.

   - However, RDDs lack the optimization capabilities that come with DataFrames and Datasets due to their unstructured nature.

1. **DataFrame**:

   - DataFrame is a structured collection of data, similar to a table in a relational database or a spreadsheet. It has rows and columns.

   - DataFrames were introduced in Spark 1.3 and provide a more user-friendly, structured API for working with data.

   - DataFrames are built on top of RDDs but provide a schema (structure) and can be thought of as RDDs with schema information.

   - DataFrame operations benefit from the Catalyst optimizer, which optimizes the execution plan based on the provided operations, improving performance.

   - DataFrames can be created from various sources like structured data files, Hive tables, external databases, and RDDs.

1. **Dataset**:

   - Dataset is an extension of DataFrames introduced in Spark 1.6, aiming to combine the type safety of RDDs with the optimization and performance benefits of DataFrames.

   - Datasets are strongly typed, allowing for safe and efficient processing, as the type information is preserved during transformations and actions.

   - Like DataFrames, Datasets are built on top of RDDs, and they also leverage the Catalyst optimizer for better performance.

   - Datasets can be created from DataFrames or from structured data sources.

**Key Differences**:

- RDDs are the most basic and unstructured data abstraction in Spark.

- DataFrames add structure to the data and provide an API similar to SQL tables.

- Datasets provide the benefits of both RDDs (type safety, functional transformations) and DataFrames (optimization, query optimization).

- In terms of performance, Datasets and DataFrames usually outperform RDDs due to the optimization opportunities offered by their structured nature and the Catalyst optimizer.

- RDDs are more suitable for unstructured data or when you need more fine-grained control over the data.

- DataFrames and Datasets are recommended for structured data, and Datasets are preferred when you need strong typing and the benefits of optimization.

## Key Terms

In Apache Spark, a **partition** refers to a portion of a larger distributed dataset (such as an RDD, DataFrame, or Dataset) that is stored on a single machine in a Spark cluster. Partitions are the basic units of parallelism in Spark and play a crucial role in enabling parallel processing across the nodes of the cluster.

Here's how partitions relate to tasks:

1. **Partitioning Data**:

   - When a distributed dataset (e.g., an RDD) is created in Spark, it is divided into smaller logical units called partitions. Each partition contains a subset of the overall data.

   - The number of partitions is determined during the dataset's creation and often depends on the input data source, the parallelism level desired, or any custom partitioning logic.

1. **Task Execution**:

   - In Spark, tasks are units of work that are executed on each partition of the data in parallel across the cluster.

   - When a Spark job is triggered, tasks are created to process each partition of the data. Each task processes one partition independently.

1. **Parallel Execution**:

   - In a typical Spark application, multiple tasks (corresponding to the number of partitions) are executed concurrently on different worker nodes in the cluster.

   - This parallel execution allows for efficient and distributed processing of the dataset, improving the overall performance and throughput of the application.

1. **Task Per Partition**:

   - Each task operates on a single partition of the data, processing the elements within that partition using the specified transformations and actions.

   - The relationship between partitions and tasks is one-to-one: each partition is processed by exactly one task.

1. **Task**:

   - A task is the smallest unit of work in Spark. It represents a single unit of computation that is executed on a partition of data.

   - Tasks are created for each partition of the data and are sent to worker nodes for execution in parallel.

1. **Job**:

   - A job in Spark refers to a set of tasks that are launched in response to a Spark action, such as `collect()`, `count()`, or any other action that triggers computation and brings data from RDDs or DataFrames to the driver program.

   - Each action usually triggers one job, although some complex actions can trigger multiple jobs.

   - The set of tasks that comprise a job corresponds to the transformations that lead to the action being executed.

1. **Stage**:

   - A stage is an intermediate computational step within a job. A job may be divided into multiple stages based on the presence of shuffling operations (e.g., `reduceByKey` or `join`), which require data to be shuffled across the cluster.

   - Stages are constructed based on the transformations in the lineage of RDDs. Each stage represents a set of tasks that can be executed in parallel, and these tasks do not require data shuffling.

   - A stage is defined by the partitions of the data that are input to the stage (the partitions that were the result of the previous stage).

In summary:

- **Task** is the smallest unit of work, representing computation on a single partition of data.

- **Job** is a set of tasks triggered by a Spark action and is typically associated with one or more transformations.

- **Stage** is an intermediate step in a job, defined by the presence of shuffling operations, and is constructed based on the transformations and partitions of data.

In Apache Spark, a **shuffle** refers to the process of redistributing and reorganizing data across the nodes in a cluster during certain types of operations. This process is essential when data needs to be moved or exchanged between different nodes for further processing, particularly when a transformation involves grouping or aggregating data from multiple sources.

Here's a more detailed explanation of a shuffle in Spark:

1. **Why Shuffling Occurs**:

   - Shuffling is needed when a transformation requires data from multiple partitions to be combined, such as during a group-by operation, a join, or an aggregation like a reduce operation.

1. **Process of Shuffling**:

   - When a shuffle is required, the data from various partitions is collected, sorted (if needed), and then distributed or "shuffled" across the nodes in the cluster based on the partitioning key or criteria.

   - Shuffling involves writing intermediate data to disk and transferring it over the network, making it a resource-intensive operation.

1. **Stages Involving Shuffling**:

   - Shuffling usually creates a boundary between stages in a Spark application. The stage before the shuffle is often referred to as the "map stage," and the stage after the shuffle is the "reduce stage."

   - In the "map stage," data is mapped based on some criteria (e.g., keys for a join). In the "reduce stage," the shuffled and aggregated data is further processed.

1. **Performance Implications**:

   - Shuffling can be a performance bottleneck due to the need for extensive data movement and disk I/O, especially when dealing with large datasets.

   - Effective management and optimization of shuffling operations are crucial for improving the performance and efficiency of Spark applications.

   - Techniques such as reducing the amount of shuffled data (e.g., by using appropriate partitioning), using combiners, and optimizing the Spark application's execution plan can help mitigate the performance impact of shuffling.

In summary, a shuffle in Spark involves the redistribution and reorganization of data across nodes in the cluster during certain transformations. It's a critical operation for computations that involve combining data from multiple partitions, but it also comes with performance considerations due to the need for data movement and disk I/O. Optimal usage and management of shuffling operations are essential for efficient Spark application performance.

## PySpark

PySpark, which is the Python library for Apache Spark, indeed utilizes the Java Virtual Machine (JVM) under the hood. When using PySpark, the majority of the Spark functionality is implemented in Scala and runs on the JVM.

Here's how it works:

1. **Py4J Integration**:

   - PySpark uses Py4J, a popular library for connecting Python programs with Java objects, to facilitate communication between the Python environment and the JVM.

1. **JVM Execution**:

   - The actual Spark processing, including data processing, transformations, and actions, happens in the JVM. When you call PySpark methods or functions from Python, these requests are translated and executed in the JVM.

1. **Python as a Driver Program**:

   - In a typical PySpark application, the Python code serves as the driver program, coordinating and orchestrating the Spark application's flow. However, the actual data processing occurs within the JVM.

1. **Serialization and Deserialization**:

   - Data serialization and deserialization are handled efficiently by the JVM, even though the initial call originates from Python. This helps in effective data exchange between the Python environment and the JVM.

In PySpark, `SparkSession` is the entry point and central interface for interacting with Apache Spark. It is a higher-level API that encapsulates the functionality of the older SparkContext, SQLContext, and HiveContext, providing a unified entry point for reading data, executing SQL queries, and interacting with Spark features.

Here are the main aspects and functionalities of `SparkSession` in PySpark:

1. **Unified Entry Point**:

   - `SparkSession` combines functionalities previously provided by `SQLContext` and `HiveContext`, simplifying the usage of Spark by consolidating various contexts into a single entry point.

1. **DataFrame API**:

   - `SparkSession` provides the DataFrame API, which allows for working with structured data in a tabular format, similar to a relational database or a spreadsheet.

1. **SQL Execution**:

   - Users can execute SQL queries directly on DataFrames registered as temporary tables, making it easy to leverage SQL for data processing.

1. **Data Loading and Saving**:

   - `SparkSession` supports reading data from various sources (e.g., Parquet, CSV, JSON) and saving DataFrames to different formats.

1. **Configuration and Properties**:

   - Users can configure Spark properties and settings through the `SparkSession` object, allowing for customization and optimization of Spark application behavior.

1. **Application Context**:

   - `SparkSession` is designed to be a single point of entry for the application. When using `SparkSession`, the underlying SparkContext, SQLContext, and HiveContext are automatically created and managed, ensuring proper initialization and handling.

1. **Resource Management**:

   - `SparkSession` helps manage resources, including memory allocation and cluster resources, providing better control over Spark application execution.

**Creating a SparkSession**:

To create a `SparkSession` in PySpark, you can use the `pyspark.sql.SparkSession` class and its `builder` method:

```python
from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder \
    .appName('MySparkApp') \
    .getOrCreate()
```

Once you have the `SparkSession` object (`spark` in the above example), you can use it to perform various data processing operations, execute SQL queries, load and save data, and more.

The introduction of `SparkSession` in PySpark simplifies the code and provides a more efficient and user-friendly way to work with structured data using DataFrames and SQL.

## UDFs

Spark User-Defined Functions (UDFs) are custom functions created by users to perform transformations on data in Apache Spark. UDFs allow users to apply their custom business logic or computations to one or more columns in a DataFrame or RDD, providing flexibility and extensibility in data processing.

Here are the key aspects of Spark UDFs:

1. **Custom Logic**:

   - UDFs allow users to define their own custom logic or computations that need to be applied to each element or row in a column of the DataFrame or RDD.

1. **Data Transformation**:

   - UDFs are used to transform data at a row-wise level, often applying the same transformation to multiple rows or elements within a column.

1. **Supported in Various Languages**:

   - Spark UDFs can be implemented using different programming languages supported by Spark, including Scala, Python, Java, and R.

1. **Types of UDFs**:

   - UDFs can be either scalar functions, which operate on a single input item and return a single output item, or aggregate functions, which take multiple input items and return a single output.

1. **Application to DataFrames and RDDs**:

   - UDFs can be applied to both DataFrames (structured, tabular data) and RDDs (distributed collections of data). However, UDFs in DataFrames are often preferred due to the Catalyst optimizer's optimization capabilities.

1. **Usage in DataFrame Operations**:

   - In DataFrames, UDFs can be applied using the `withColumn()` method to add a new column with the transformed data based on the UDF.

1. **Python Example**:

   - For instance, in PySpark, a simple Python UDF could be used to convert a DataFrame column to uppercase:

   ```python
   from pyspark.sql.functions import udf
   from pyspark.sql.types import StringType

   # Define the UDF
   def to_upper(s):
       if s is not None:
           return s.upper()
       return None

   # Register the UDF
   udf_to_upper = udf(to_upper, StringType())

   # Apply the UDF to a DataFrame column
   df = df.withColumn('uppercase_column', udf_to_upper(df['original_column']))
   ```

Spark UDFs provide a powerful way to customize data transformations and processing in Spark applications, enabling users to tailor their data processing to specific business requirements and use cases. However, it's important to use UDFs judiciously and consider the performance implications, especially for complex or resource-intensive computations.

## Spark SQL vs non-Spark SQL

In Apache Spark, there can be performance differences between using Spark SQL (SQL-based operations) and using non-SQL operations (programmatic operations using DataFrames or RDDs). These differences stem from various factors related to the execution and optimization of the respective operations. Let's delve into the key aspects that can influence performance:

1. **Optimization and Catalyst Optimizer**:

   - Spark SQL uses the Catalyst Optimizer, which leverages query optimization techniques to optimize SQL-based operations. The Catalyst Optimizer can apply advanced optimizations like predicate pushdown, projection pruning, and join reordering, leading to more efficient query plans and potentially improved performance.

   - Non-SQL operations do not benefit from the Catalyst Optimizer's specific SQL-related optimizations.

1. **Query Plan Execution**:

   - SQL-based operations follow a declarative approach, where users define the desired results, and the Spark SQL engine generates an optimized query plan to achieve those results.

   - Non-SQL operations are more programmatic and imperative, requiring users to define the specific steps for data transformations and actions. While this provides flexibility, the engine may not be able to optimize the steps as effectively as with a declarative query plan.

1. **Code Complexity and Efficiency**:

   - SQL-based operations often lead to more concise and readable code, reducing the potential for human error and improving development efficiency.

   - Non-SQL operations, especially complex ones, may require more code and be harder to optimize manually, potentially impacting efficiency and introducing more room for optimization errors.

1. **Data Locality and Shuffling**:

   - Depending on the nature of the operations, SQL-based operations can sometimes introduce additional shuffling of data, which could affect performance.

   - Non-SQL operations allow for more fine-grained control over data processing, potentially enabling optimizations that reduce or eliminate shuffling.

1. **Complexity of Operations**:

   - The complexity and nature of the operations can significantly impact performance. Some operations may be more naturally expressed and optimized using SQL, while others may be better suited to programmatic approaches.

   - Simple transformations and filters can often be equally efficient in both SQL and non-SQL operations.

In summary, there can be performance differences, but it heavily depends on the specific use case, the nature of the data processing, and the complexity of the operations. Both SQL and non-SQL approaches have their merits and are optimized differently. It's important to choose the appropriate approach based on the specific requirements, readability, maintainability, and the ability to leverage the optimization capabilities provided by Spark's query optimizer. It's also common to use a mix of both SQL and non-SQL operations to strike a balance between performance and ease of use.

## Rapid Fire

spark is a distributed in-memory processing framework for working with big data.

- it is lazily evaluated and builds a DAG of all steps to be ran when certain action operations are executed like .write or .collect etc
- you have a master spark node which runs the driver program, and worker nodes which run executors or processes triggered by the master node to run jobs
- Example: 10 spark workers (aka 10 executor JVM processes), 4 cores per worker, 40 total cores that can run in parallel on 40 partitions at the same time.
- jobs consist of all of the work needed for a spark workload to run.
- jobs consist of stages, which are when you need to re-shuffle the data across nodes for specific operations like group by aggs or repartitioning events etc
- within stages are spark tasks, which are individual units of work on a single partition
- shuffles are expensive because they involve disk I/O, network I/O, and serialization
  - serialization: Convert in-memory objects to bytes for network transfer (CPU intense)
  - disk IO: each executor has to write shuffle data to local disk
  - network IO: data going back and forth across the network to appropriate executors. network bandwidth becomes the bottleneck
  - deserialization:c onvert bytes back to in memory objects (CPU intense)
  - so the data during shuffles is serialized to bytes, written to disk, sent over the network, read back from disk, and deserialized into in-memory objects on the executors
  - The disk write serves a purpose for fault tolerance and avoiding all data sitting in memory at once
- a partition is 1 slice of the data. many parittions develop many tasks which can be executed in parallel across all worker nodes
- if you have 200 partitions, you'll have 200 tasks. try to balance partitions at around < 128 MB each and have an appropraite amount of worker nodes avaialble ot paralleize the work.
  - too few partitions and you wont get good parallism
  - too many partitions and you end up with a lot of overhead which could affect performance
- broadcast joins allow a table to be placed in memory on every worker node to avoid reshuffling operations and improve performance, at the cost of taking up memroy across every node. typically used for small tables relative to the total size of the data, like joining a 1 TB table with a 5 GB broadcast join table would bew appropriate.
- spark operates in-memory. if too much data comes into the worker node and causes it to hit its limits, the worker node can spill to disk to complete the job. this works, but is a serious performance penalty
- narrow transaformations are simple operations like filter or creating a new column that adds 1 to an integer column and can be executed locally in memory
- wide transformations require data to be redistributed across partitions and trigger a shuffle, such as a group by aggregation
- repartition does a full shuffle and can increase or decrease partitions
  - can be useful to fix data skew, or increase # of partitions for better parallelism
- coalesce simplly decreases partitions without a shuffle.
  - useful when you're about to write data, and only want to write 1 file instead of 1000
- optimizing a slow running spark job involves checking for data skew, minimizing shuffles, potentially using broadcast joins, adjusting partition counts etc
- Data skew happens when certain partitions have way more data than others (e.g., NULL keys, popular user IDs). This causes some tasks to take much longer. Solutions: salting keys, custom partitioning, or AQE can help.
- since spark is lazily evaluated and has DAG, if a partition is lost or a task fails spark can recompute it using the transformation history.
- the mechanism that optimizes spark query plans is called the catalyst optimizer, it basically runs under the hood
- adaptive query execution is a runtime optimization feature that dynamically adjusts query execution plans based on actual runtime statistics after each stage during spark jobs so it can optimize the remaining stage steps
  - it does things like: dynamically update partition counts, automatically switching join strategies to broadcast, detects data skew and creates sub-partitions to enable further parallelization
- Caching stores computed results in memory to avoid recomputation when a DataFrame is used multiple times in a job.
- parquet is a preferred file format because it is columnar focused, has a strict data type schema, and has good compression ratios for efficient storage.
- predicate pushdown involves pushing filters down to the data source level when possible so you only read in the minimal amount of data you need.
  - Example: select from parquet file where date = '2025-01-01\` - spark can read parquet metadata and skip entire row groups based on min max statistics, so it doesnt need to read in the whole file and then do the filter in memory, it can apply the filter when it fetches the data
