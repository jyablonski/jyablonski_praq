# Hashing

Hashing is the process of mapping data of arbitrary size (like a string or object) to a fixed-size value using a mathematical function called a hash function. Properties of a good hash function include:

* Deterministic: Same input always produces the same output.
* Fast: Computation is quick and efficient.
* Uniform Distribution: Avoids clustering by spreading values evenly.
* Low Collision Rate: Different inputs should rarely produce the same hash.
* Irreversible: Hard to reverse-engineer the original input from the hash (important in cryptographic hashes).

This concept is used in data structures and data systems so we can take some data and reliably store it in some place in memory, where we can access it in `o(1)` time because we just have to run the hash function on the key again wehn we want it and bam there it is.

Hash-based partitioning works especially well in distributed systems like DynamoDB or Cassandra, which can horizontally scale across many nodes. These systems allow for efficient point lookups, often in constant time, by routing requests based on partition keys. In contrast, traditional relational databases usually rely on a single writer node, making horizontal scaling and high write throughput more difficult to achieve.

You can hash almost anything - strings, integers, booleans, or even complex objects as long as you can turn them into a sequence of bytes. The goal of any hash function is to take this arbitray input and deterministically turn it into a fixed-size integer which makes it easier for indexing, partitioning, and distributing data.

## Applications of Hashing

1. Hash Tables / Hash Maps - Fast lookup, insert, delete in `O(1)` average time.

2. Checksums and Fingerprints - Detecting changes to data (e.g., MD5, SHA-256).

3. Data Partitioning in Distributed Systems - Deciding which server or node stores a given piece of data.

4. Cryptography - Securing passwords, verifying integrity, digital signatures.


## Simple Hashing

### Example: Hash Table Storage

Let’s say you want to store users in a table using their usernames as keys.

```python
def simple_hash(key: str, table_size: int) -> int:
    return sum(ord(char) for char in key) % table_size
```

- `ord(char)` turns a character into a numerical representation (Unicode code point)
- Then sum them all together
- Then run modulo against the storage size of your hash table, to ensure we always get a valid result in our hash table and we don't go out of bounds

If `table_size = 10`:

* `simple_hash("alice") -> 2`
* `simple_hash("bob") -> 5`

But, simple modulo-based hashing also has problems:

```python
node = hash(key) % num_nodes
```
- hash("alice") % 3 = 0
- If you go from 3 → 4 nodes, almost all keys need to be remapped.
- This is because of the `num_nodes` value. All existing keys were mapped using the current `num_nodes` value, so they'll only be spread across nodes 1, 2, and 3
- If you add a 4th node, all of those existing keys are still in the first 3 nodes, and now your subsequent hashes are going to be mapped to different nodes
    - hash("alice") % 4 = 2

### Problems with Simple Hashing

* Collisions: Different keys mapping to the same index.
* Poor Distribution: If hash function isn’t uniform, clusters occur.
* Fixed Size: Rehashing is needed when the table grows.
* Not suitable for distributed systems: Changes in nodes affect too many mappings.

## Consistent Hashing

In distributed systems (e.g., a cache like Memcached), you want to:

* Spread data evenly across many nodes.
* Handle node joins and leaves without rehashing all keys.
* Have fast, predictable access to data by key

Consistent Hashing uses a (conceptual) hash ring (0 to 2³² - 1), where both nodes and keys are hashed to points on the ring.

- A key is stored in the first node clockwise from its position on the ring.
- When a node joins or leaves:

   * Only a fraction of keys are affected.
   * No need to rehash everything.

You still use a hash function to place each key somewhere on the ring, but you also place each node (server) on the ring as well. 

Keys are assigned to the next node in the ring moving clockwise. Example:

* Key `K` hashes to position 1234.
* Nodes:

  * Node A → 1000
  * Node B → 2000
  * Node C → 3000

Since 1234 is between A and B, key `K` goes to Node B.

### Virtual Nodes

The concept of virtual nodes enables a physical node to be placed at multiple positions around the ring. The purpose is to assist w/ evenly distributing the load, regardless of how many physical nodes you actually have.

Let’s say we have 3 physical nodes: A, B, C. If we assign:

- Node A → positions 1000, 4000, 7000
- Node B → positions 2000, 5000, 8000
- Node C → positions 3000, 6000, 9000
- Now we have 9 evenly spaced vnodes instead of 3 clumped real nodes.
- When a key lands somewhere on the ring, it still finds the next node clockwise — but that might be a vnode for A, B, or C.
- This gives better spread and finer-grained balancing
- These are stored in a sorted data structure like a balanced tree for quick lookup
- If we wanted to store a key that had a hash value of 9100, then you do wrap-around where it actually ends up going to the first node at 1000 in this case

If all your servers are equally powerful, then all should get the same amount of vnodes to ensure equal distribution.

- But, if your server types are mixed and some are more powerful then others, then it makes sense to dish out varying amounts of vnodes to each
- Server A is old / slower, Server B is newer / faster. 
- Server A gets 50 vnodes, Server B gets 200 vnodes
- Now Server B will handle ~4x more data and traffic than A and that’s okay, because it’s 4x more capable.


## What Real Hashing Functions look like

Advanced hashing functions perform complex mathematical operations such as bit shifts, rotations, and XORs to thoroughly scramble the input while maintaining deterministic behavior.

- For cryptographic hash functions (like SHA-256), even more complex operations are involved to ensure the hash is non-reversible and collision-resistant. This added complexity makes them slower but much more secure.
- The primary goals of hashing functions are to evenly distribute data, minimize collisions, and produce consistent, repeatable results.


## How Applications use Hashing

Suppose you have some request to see if user `user123` exists or not.

- `nodes = [100, 500, 1000, 1500, 2000, 2500, 3000, 3500]` - could be 8 vnodes over 2 servers, or 8 servers.

1. Compute the hash of the key `hash("user123") = 1789`
2. Perform binary search on the sorted nodes to find the first node hash that is greater than or equal to the key hash output
3. Store the `1789` hash at the `2000` node

### Summary Table

| Feature            | Simple Hashing             | Consistent Hashing               |
| ------------------ | -------------------------- | -------------------------------- |
| Used in        | Hash tables, basic caching | Distributed caches, sharding     |
| Scalability    | Poor                       | Good                             |
| Key remapping  | Many keys change on resize | Minimal keys change              |
| Load balancing | Can be uneven              | More balanced with virtual nodes |
| Implementation | Easy                       | More complex                     |

## Real-World Systems Using Consistent Hashing

| System              | Use Case                           |
| ------------------- | ---------------------------------- |
| Cassandra       | Partitioning rows across nodes     |
| Kafka           | Mapping partitions to brokers      |
| Redis Cluster   | Distributing keys to shards        |
| Amazon DynamoDB | Behind the scenes for partitioning |
| Ringpop (Uber)  | Service discovery and routing      |
