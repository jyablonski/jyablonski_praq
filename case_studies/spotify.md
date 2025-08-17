# Spotify

[Blog Post](https://engineering.atspotify.com/2024/5/data-platform-explained-part-ii)

- Business drivers: Fuel and support various teams like payments, experimentation etc w/ data
- Data Volume / Scale: Over 1 trillion events generated daily, over 1000 microservices, over 38,000 data pipelines

They mention specific triggers that my prompt an org to invest in a data platform:

- Having more searchable and usable data that's easy to access for engineers, product, and business teams
- Satisfying internal reporting requirements, specifically around financial reporting
- Ensuring data quality and predictable results
- Supporting an efficient development lifecycle for things, specifically for experimentation
- Enabling ML capabilities and initiatives with well-classified data

Key components involve:

- Source Data Collection from various clients & services
- Data processing to transform & enrich that data
- Data management focusing on data attribution and privacy to ensure the integrity and security of the company's data

Data collection is needed to:

- Understand what content is relevant to Spotify users
- Directly respond to user feedback
- Have a deeper understanding of user interactions to enhance their experience

Key things to help them scale:

- Maintain data lineage, searchability (metadata), and accessibility
- Implementing access controls and retention policies to manage storage costs and comply with regulations
- Enable Spotify to extract the maximum value from its data assets while upholding operational efficiency and adhereing to regulatory standards

They built custom K8s operators to manage workflows and event streams

- When a team wants to build a new event delivery system, they define the schemas for the events and the infrastructure automatically deploys specific resources like PubSub queues, anonymization pipelines, and streaming jobs to support it.

Data Platform needs:

- Flexible enough to support a variety of use cases and align with cost effectiveness and return-on-investment goals
- Easy to onboard to
- Have seamless upgrade paths
- Reliable

They built and open sourced adocumentation tool [Backstage](https://backstage.io/blog/2020/03/16/announcing-backstage/) to help them manage their software and onboard people. It's known for:

- Software catalog to store information on every service, data pipeline, and app at Spotify, along with metadata such as its owner, lifecycle stage, docs etc
- Plugin capability to extend the site and surface multiple components in it such as CI / CD builds, monitoring dashboards, cost reports etc
- TechDocs which allows technical documentation to be stored in Git Repos but hosted on the site
- Scaffolder which lets teams create new services / pipelines using predefined templates, enforcing best practices from day 1

## Padlock

[Blog Post](https://engineering.atspotify.com/2018/09/scalable-user-privacy)

Spotify designed a privacy management system called Padlock to only persist user information when it is encrypted, where each user has its own specific key. This allows:

- If data is ever leaked, the attacker can't do shit because the data needs to be decrypted
- All data for a specific user can be deleted when you delete that user's keychain
- Teams can now use user data as they need and have autonomy to build out whatever, without having to worry about PII concerns every time
- Ensures compliance and helps uphold our privacy standards with minimal overhead

When services need to process personal data, they query Padlock to get the keychain to encrypt or decrypt the data

- For example, when a user looks at their own playlist, the playlist service makes a call to Padlock to get the keychain of the playlist owner and decrypt the playlist
- Each service that calls Padlock gets its own set of keys to reduce impact of a single service getting compromised
- Padlock knows each key that every service at Spotify has, so it takes the key used in the input request, and returns a derived key that it will use for encryption & decryption if it's a valid match
- Other important user information like opting-out of targeted ads etc is stored in Padlock, so Spotify can easily block access to that specific category if that's what a user selected

Because Padlock is queried so often by services, it needs notable requirements:

- It needs to scale to handle the load of all these services querying from it, especially core ones like login, playlist and spotify-connect
- It needs to have low latency
- It needs to be highly available. They currently have this set to an SLO of 99.95% availability, and are considering pushing it to 99.99%

But, this service is heavily read-dominated, with only 0.1% of requests being writes or updates. And, getting a user's key only requires consistency of fetching 1 row.

Spotify utilizes Cassandra for globally replicated highly available storage, and are on GCP. They also use Memcached

- A Cassandra read request taktes about 15 ms
- A Memcached read requests takes between 2-4 ms
- All Cassandra reads are done wtih `LOCAL_ONE` consistency, and if the read fails then it's retried with `LOCAL_QUORUM` consistency. The idea here is to first try 1 node for low latency, and then query multiple of them if needed to find the user's key.
- Only newly signed up user operations have to be readable instantly since there keys are used by other services during the initial signup process
- Read repair was disabled to support the `LOCAL_ONE` performance needs
- No row caching since it's handled by Memcached
- Avoiding tombstones by not using multi-value data types like maps or lists
- Padlock doesn't implement any retries internally, instead it just fails fast and leaves it up to the client to decide if it should retry.

Because it's such a critical system, they have various strategies for keeping up its high reliability:

- All changes are always deployed first to a staging environment with no real user traffic, but with all of the other services to ensure Padlock changes behave well here
- Then, there's a 3 stage rollout process for prod deployment that requires manual approval. It starts with a single canary machine, then a single region (we call this the “albatross”) and finally global.
- Padlock runs globally in America, Europe, and Asia in 3 zones per region, so if 1 region goes down the other 2 will automatically take over will slightly reduced latency for users
- They also duplicate their setup within regions in 2 separate deployment groups: padlock and padlock-mirror with enough resources to takeover production traffic from the other group if needed.
    - Both deployment groups share a Cassandra Cluster, but have separate Memcached instances
    - Trust Cassandra to be highly available
- They periodically run disaster-recovery tests (DiRTs) simulating service or storage failures