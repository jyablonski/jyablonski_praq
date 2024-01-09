# Aurora
Aurora by default can replicate itself in 1 region across multiple Availability Zones for redundancy & high availability.

Read Replicas don't duplicate the Storage when you create them.  They just read from the Existing Storage.

Aurora can split into 3 AZs for Redundancy.  If 1 AZ goes down where the Primary is then it will failover to 1 of the other ones.

Can mix & match different Instance Sizes across a single Aurora Cluster.

Can failover to 1 of the Read Replica Nodes if the Writer goes down.

Aurora Storage scales automatically, either up or down.  After you drop data, it will asynchronously drop that storage so you don't get charged extra.

Pay as you go for I/O, except for I/O AWS Aurora Optimized Instance

Original Postgres does a lot of log writing for various database operations, Aurora cleans some of this up to remove excess checkpoints and other log writing operations to minimize the number of writes.
- This mechanism is just about the same in MySQL.

Fast Cloning available for Reporting / Read stuff.  You aren't paying for any additional storage when you do this until you modify it.
- When you read data, even though it looks like you're connected to the Replica and querying from that you're actually jsut pulling from the shared Aurora Storage.
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/d890650e-fe24-4269-80b5-3b8cb5610d51)
- Clones are much faster than Snapshots because

Aurora backs up your cluster volume automatically and retains restore data for the length of the backup retention period.  These automated backups are continuous and incremental, so you can restore to any point within the retention period which can be set anywhere between 1 - 35 days. 
- You are charged for having a retention period > 1 day.


[Trusted Language Extensions](https://github.com/aws/pg_tle) provides an extension framework to add more functionality to your PostgreSQL Instance without having to fork the codebase yourself.
- Examples include Login Lockout after 5 failed login attempts, or enforcement of password expiration if your password is older then x days and needs to be reset.

Blue Green Deployment - uses Binlog Replication to switchover in progress.  Makes sure everything with the new cluster is good.  Writes then get blocked, replication gets caught up, and the switchover beginsd.  
- Ensure RDS Aurora Cluster has Logical Replication / Binlog enabled
- Ensure RDS Aurora Cluster is on a Version that's compatible with AWS Blue/Green Deployments
- Create Blue Green Deployment
- Wait for Blue Green Deployment Checks to all return successful
- Switchover Blue Green Deployment
- After everything looks good, manually delete old Blue Green Deployment.

## I/O Optimized Cluster
Relatively new configuartion that provides improving pricing for I/O Intensive Applications.  
- You only pay for the compute and storage usage, with no additional charges for I/O operations.
- Enables heavy I/O Applications to run at a predictable, lower cost.
- You pay a higher price (20-30% more), but your I/O Costs are now fixed instead of pay-as-you-go.
- For some customers, this saves a significant amount of money.  But, those fixed costs are now higher up front.
- AWS recommends this option when >= 25% of your Aurora costs are from I/O Operations
- [Link](https://aws.amazon.com/blogs/database/estimate-cost-savings-for-the-amazon-aurora-i-o-optimized-feature-using-amazon-cloudwatch/)

## Global Database
Aurora Global Database replicates an Aurora Cluster across multiple Regions and provides high availability + fast recovery in the event of an outage on an entire AWS Region.
- 1 Primary Aurora Cluster where your data is written, and up to 5 read-only secondary AWS Regions.
- All write operations write directly tothe primary DB Cluster in the primary AWS Region.
- Serves applications with a worldwide footprint.
- Latency is higher than normal Aurora for obvious reasons, but it's still low.
- Can have a fully mirrored configuration in this 2nd Region, same as the main Region.
- ![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/6b7bb6bc-d210-4fa6-8fbd-57c3a588029c)
- Can promote Region B to primary Cluster, simple command.  This leaves the original Cluster there as well, so they become 2 distinct Clusters.
- Also functionality in place to do the samew thing but to Failover to Region B so that it becomes the primary Region, and Region A becomes the Reader.
  - Basically like Promoting Region B to the Primary.
  - Region A is now the Failover Cluster.
- Can select `--enable-global-write-forwarding` to save you from implementing own mechanism to send write operations from a secondary AWS Region to the primary Region.  Aurora handles everything for you.
  - This way, the Primary Cluster is always the source of truth and will always have an up-to-date copy of the data.