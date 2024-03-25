# Advanced Databases 
[Youtube Link](https://www.youtube.com/watch?v=lGRAq98ejWs)

## Storage
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/1b5c6628-1308-4887-a9a9-30ee040b101b)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/9fcb96ad-9038-4a98-adc3-23401f383438)
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/b6a7ac6a-6c1c-467d-97a7-feb8a5772484)


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
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/06dcb5ce-cb82-438f-bbc6-90d513da5ac2)
- Every Page contains a Header of metadata about the page's contents such as:
  - Page Size
  - Checksum (to make sure nothings changed or is corrupted)
  - DBMS Version
  - Compression / Encoding
  - Schema info
  - Data Summary Stats
- Most common strategy for pages is to use slotted pages.  The slot array maps "slots" to the tuples' starting offset positions

Tuple Oriented Storage
- To insert a new tuple - check page dsirectory to find a page with a free slot, retrieve the page from disk, and check slot array to find empty spcae in page that will fit
- To update an existing tuple using its record id - check page directory to find location of page, retrieve page from disk, find offset in page using slot array, if new data fits then overwrite.  otherwise, mark existing tuple as deleted and insert new record version in different page.
  - Can lead to page fragmentation (pages arent fully utilized, empty slots)
  - DBMS must fetch entire page to update one tuple
  - Worst case - you have to update a bunch of tuples in random pages which is bad news bears for performance

Log Structured Storage
- Instead of storing tuples in pages, the DBMS maintains a log that records changes to tuples
- Each log entry represents a tuple put/delete operation
- The DBMS appends new log entries to an in-memory buffer and then writes out the changes sequentially to disk
- Each log record must contain the tuple's unique identifier
- As app makes changes to database, the DBMS appends log records to end of file without checking the previous log records
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/5b3a5ab6-933e-4d8f-9dd5-29cef31a967b)
- When the page gets full, the DBMS writes it out to disk and starts filling up the next page with records.
- All disk writes are sequential and on-disk pages are immutable
- DBMS may also flush partially full pages for transactions but more to come on this
- Writes are much faster than tuple storage
- Reads are a little slower than tuple storage
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/8b219a6a-8b96-4c49-9958-a098cbc4cbde)
- DBMS periodically compacts pages to reduce wasted space (Log Structured Compaction)
- After compacting a page, the DBMS does not need to maintain a temporal ordering of records within the page
- The DBMS instead sorts the page based on id to improve efficiency of future lookups (Sorted String Tables)
- 2 kinds of compaction methods:
  - ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/c77cdb06-c780-46aa-a079-62c822fc25be)
  - Universal compaction - compacting adjacent log files together
  - Level compaction - cascading down and creating larger and larger log files
  - Analogous to driving on bad/low oil in your car.  it can work, but best-practice wise you should change your oil (and in DBMS case - compact your log files)

Index Organized Storage
- DBMS stores a table's tuples as the value of an index data structure, still uses a page layout that looks like slotted page
- Tuples are typically sroted in page based on key
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/1d98addc-82d4-4727-a7d2-d7d70ff2e151)
- Word aligned tuples - all attributes in a tuple must be word aligned to allow the CPU to access it without any unexpected behavior or additional work
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/d496207e-c418-42e6-b76e-31763cf7b82b)
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/038db2be-a734-4892-9afa-879142115ade)


Data Types
1. **Floating Point/Real Data Types**:
   - These data types are designed to represent approximate numeric values.
   - They are used when the precision of the value is not critical or when the value can have a wide range of magnitudes.
   - Examples of floating point/real data types include FLOAT and REAL.
   - Floating point numbers are stored in a binary representation, typically using the IEEE 754 standard.
   - Floating point numbers have limited precision, which means that operations involving them can result in rounding errors.

2. **Fixed Precision/Decimal Data Types**:
   - These data types are designed to represent exact numeric values with a fixed precision and scale.
   - They are suitable for representing values where precision is crucial, such as monetary amounts or exact measurements.
   - Examples of fixed precision/decimal data types include DECIMAL, NUMERIC, and MONEY.
   - Decimal numbers are stored in a binary-coded decimal (BCD) format, which allows for precise representation of decimal numbers without the rounding errors associated with floating point numbers.
   - Decimal data types store both the precision (total number of digits) and scale (number of digits to the right of the decimal point) explicitly, providing control over the exact representation of numeric values.

Nulls
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/a859db5f-5617-44e7-aca4-845c320b80e9)

Large Values
- Most DBMS wont allow a tuple to exceed the size of a single page
- All pages have the same size
- To store larger values then, the DBMS uses separate overflow storage pages
  - Postgres: TOST (> 2 KB)
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/5f15fbe1-5111-4fd6-bf6c-6fad682e7960)
- Overflow Pages can have pointers to the next overflow page if required

External Value Storage
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/8536a506-da8e-40c0-bdde-dcc2a76311c3)


Storage Models
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/b2e6a760-0e8b-418c-82a5-8d8a5e18c625)
- OLTP are typically N-ary Storage Model (NSM) - DBMS stores all attributes for a single tuple contigously in a single page aka row store.  Ideal for OLTP workloads where queries are likely to acces individual entities and execute write-heavy workloads
- OLAP are PAX

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