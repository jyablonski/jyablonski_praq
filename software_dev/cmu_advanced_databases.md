# Advanced Databases 
[Youtube Link](https://www.youtube.com/watch?v=lGRAq98ejWs)

## Columnar Databases - PAX
"PAX" stands for Partition Attributes Across (X) and is a technique used for organizing and storing data within a columnar database system.  Most Columnar Stores use this.

1. **Partitioning the Data**:
   - Partitioning involves dividing the dataset into smaller, more manageable parts called segments. Each segment contains a subset of the dataset.
   - In the context of PAX storage, the data within a column is partitioned into multiple segments based on certain attributes or criteria. These attributes could be specific values, ranges of values, or other characteristics of the data.

2. **Spreading it Across Multiple Segments**:
   - Once the data is partitioned, it is spread across multiple segments. This means that different portions of the data are stored in different locations or storage devices.
   - Spreading the data across multiple segments helps distribute the workload and enables parallel processing. Each segment can be processed independently, allowing for better utilization of resources and improved performance.

3. **Enhancing Query Performance**:
   - By partitioning the data and spreading it across multiple segments, PAX storage aims to enhance query performance.
   - When a query is executed, the database system can often determine which segments contain relevant data based on the query criteria. This allows the system to access and process only the necessary segments, rather than the entire dataset.
   - Minimizing the amount of data that needs to be accessed and processed for a given query reduces the computational overhead and improves query execution times.

4. **Minimizing Data Access and Processing**:
   - PAX storage minimizes the amount of data that needs to be accessed and processed for a given query by selectively accessing only the relevant segments.
   - Since each segment contains a subset of the dataset, the system can focus its resources on processing only those segments that are relevant to the query. This reduces the overall data access and processing overhead, leading to faster query performance.

By partitioning the data into segments and spreading it across multiple segments, PAX storage optimizes query performance by minimizing the amount of data that needs to be accessed and processed. This selective access to relevant segments helps reduce computational overhead and improves query execution times in columnar database systems.