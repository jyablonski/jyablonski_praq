# Advanced Databases 
[Youtube Link](https://www.youtube.com/watch?v=lGRAq98ejWs)

## Storage
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/1b5c6628-1308-4887-a9a9-30ee040b101b)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/9fcb96ad-9038-4a98-adc3-23401f383438)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/b6a7ac6a-6c1c-467d-97a7-feb8a5772484)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/06dcb5ce-cb82-438f-bbc6-90d513da5ac2)
- Volatile Data will be lost when you power the machine off
- Non-Volatile Data means it will be persistent if we turn the machine off & on
- Can't let OS manage virtual memory; it works fine for read-only but bunch of problems pop up when multiple writes.
  - `mmap` - take contents of file on disk and map it into virtual memory of your process, and now the process can jump around to the file's contents.  os manages all of it
  - Transaction Safety & ordering is a problem
  - The OS is not your friend for a lot of things.  DBMS should do all the storage handling, process scheduling etc.

DBMS store data in proprietary file formats; you can't open MySQL Files in Postgres.
- Portable File Formats do exist though

The Storage Manager is responsible for maintaining a database's files.  It organizes the files as a collection of Pages.
- Tracks data read & written to the pages
- Tracks the available space

A Page is fixed-size block of data
- Contains tuples, meta-data, indexes, log records
- Most systems don't mix page types; 1 page belongs to 1 specific table or object
- Some systems require a page to be self-contained and have all of the metadata and headers for whatever table its for.
  - Less needed today because hard drives are generally more stable nowadays
- Each page has an identifier and the DBMS has ways of mapping those IDs to physical locations
- The DBMS maintains special pages which track the location of all other data pages in the database files.
- Also records metadata about available space like free slots per page, or list of free / empty pages
- Every Page contains a Header of metadata about the page's contents such as:
  - Page Size
  - Checksum (to make sure nothings changed or is corrupted)
  - DBMS Version
  - Compression / Encoding
  - Schema info
  - Data Summary Stats
- Most common strategy for pages is to use slotted pages.  The slot array maps "slots" to the tuples' starting offset positions


Different page concepts though:
- Hardware Page (4 kb)
- OS Page (usually 4 kb, can be x64 2 mb / 1 gb)
- Database Page (512 b - 32 kb)

A DBMS typically does not maintain multiple copies of a page on disk, lot of extra work for something you can solve in other areas of the process.

DBMS want to maximize sequential access, it's much faster than random acces.  Data wants to be stored in contiguous blocks.

Reading & Writing to disk is expensive, must be carefully managed to avoid large stalls or performance degration.  

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