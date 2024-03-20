# CAP Theorem
The CAP Theorem is a fundamental concept in distributed systems design. It states that a distributed data store can only guarantee two out of the following three properties:

* **Consistency:** Every read receives the most recent write or an error. This means all clients see the same data at the same time, regardless of which node they connect to.
* **Availability:** Every request receives a (non-error) response, without necessarily containing the most recent write. The system guarantees a response even if some nodes are unavailable.
* **Partition tolerance:** The system continues to operate despite network failures that partition the system (i.e. 2 of your 6 nodes in the system go down for a period of time)

Network partitions are inevitable.  Your Nodes will become unavailable or go down.  **Partition tolerance** ensures the system can still operate in some capacity, even in a degraded state.  Without partition tolerance, you could end up in a situation where only 1 node is active and it dies mid-way through a write and you have data loss.

That means, you can't sacrifice **Partition tolereance**.  You have to choose whether to remain **Available** or **Consistent**.  Choosing which one to go for is a decision you must assess the trade-offs for.  For Example:
- CP Systems: Banking applications, financial ledgers – data integrity is paramount.
- AP Systems: Social media feeds, shopping carts – temporary inconsistencies are acceptable.

In CP systems you may also have multiple services simultaneously working with the data - such as right when you press the order button at Checkout (credit card processing, shipping & handling, reporting).  If you get it wrong and double charge or something then you're in a world of pain.

On the flip side, for something like when a user is adding items to a shopping cart, you want to go for AP because it's revenue producing.  You always want to take that request and if you encounter any consistency errors you can just hide them from the customer and deal with it later.

## Levels of Consistency
Weak consistency
- After a write, reads may or may not see it. A best effort approach is taken.
- This approach is seen in systems such as memcached. Weak consistency works well in real time use cases such as VoIP, video chat, and realtime multiplayer games. For example, if you are on a phone call and lose reception for a few seconds, when you regain connection you do not hear what was spoken during connection loss.

Eventual consistency
- After a write, reads will eventually see it (typically within milliseconds). Data is replicated asynchronously.
- This approach is seen in systems such as DNS and email. Eventual consistency works well in highly available systems.

Strong consistency
- After a write, reads will see it. Data is replicated synchronously.
- This approach is seen in file systems and RDBMSes. Strong consistency works well in systems that need transactions.