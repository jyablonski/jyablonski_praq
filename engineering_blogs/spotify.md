# Spotify Data Platform

[Article 1](https://engineering.atspotify.com/2024/04/data-platform-explained)
[Article 2](https://engineering.atspotify.com/2024/5/data-platform-explained-part-ii)

## Goals of the Platform

- Business drivers: Fuel and support various teams like payments, experimentation etc w/ data
- Data Volume / Scale: Over 1 trillion events generated daily, over 1000 microservices, over 38,000 data pipelines

They mention specific triggers that might prompt an org to invest in a data platform:

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

## Release Process

[Article](https://engineering.atspotify.com/2025/4/how-we-release-the-spotify-app-part-1)

Spotify's user base is primarily on mobile apps for iOS and Android, and their releases go out to 675+ million people when do they make updates. Mitigating issues and streamlining the release process is incredibly important for a stable user experience.

The Release Team's responsibility involves:

- Minimizing the time when a developer merges code to when it's available to users
- Ensuring quality standards

Things to balance:

- Not all bugs are created equal. A crash during signup is much more important than an intermittent failure every 12 hrs or something
- They do extensive A/B testing and if they identify a bug in 1 test group, they can temporarily route all users to the working test group while they work on the fix for the upcoming release
- Acting quickly when necessary to fix bugs or address bad user experience

They use trunk-based development at Spotify. All code is tested w/ CI, peer reviewed, and merged into `main` after approval. But they do not go directly to production, instead they do weekly or biweekly production releases

- Large scale or infrastructure updates are merged earlier in the week to identify and fix issues here early.
- For example, when they released Audiobooks it was available behind a feature flag for some time, and given out for internal use for testing. It was an important feature which required marketing efforts and events to be coordinated together with its full scale launch.
- Release Manager made sure Audiobooks was the primary feature getting released for this update. Any other big features would get rescheduled for the following week
- Feature flag usage for other code getting merged is highly recommended here, and if not then they were asked to delay their high-risk changes that week
- The `main` branch is rebuilt nightly and sent out to internal and alpha users, while crash rates and other metrics are tracked for each build automaticawlly and manually

They also have a Release Manager dashboard which collects relevant information for each release in the same place. This includes:

- The Release name (`android 8.9.2`)
- Date of planned production release
- Metrics such as daily active users and crash rates
- Latest build commit
- Any blocking bugs

On Fridays they cut a release and each team performs manual regression testing, reporting their own results.

- Teams with high confidence in their automated tests and pre-merge routines can opt out of manual testing.
- Release is given out to beta users for metrics and data gathering

On Mondays, they aim to get the new release submitted to app stores. For final checkoff, they make sure the following critera are met:

- All commits on the release branch are included in the latest build and have passed automated tests.
- No blocking bug tickets remain open.
- All teams have signed off and approved.
- Crash rates and other key metrics are below our defined thresholds.
- The app version to be released has been used to play a sufficient amount of content.

If submitted, the release rollout starts on Tuesday in 2 phases: first to small percfentage of users (1%), and then to 100% of users.

- They monitor the release dashboard throughout this process
- The 1% rollout affects >= 300k users and they get the same metrics they did as previously mentioned on this dashboard

## $0.02

A lot of fluff in the posts. I pay for premium but i don't see or feel any of these complex analytics workflows or user personalization workloads they boast about.

My actual usage pattern: I consume content almost exclusively through my own playlists with songs that I've added or liked.

Where personalization falls short:

- The Song radio feature is probably the most useful one on the entire app, but it can be delivered with pretty basic methods rather than the complex infrastructure they describe
- It takes like 4 clicks and almost 45-60 seconds for me to find the top charts playlist to see popular songs. What the fuck. Is it that hard to make a dashboard that I can customize myself with what I want?
- Even if I open up "Made for You" playlists on my home page, half of the songs are already ones i've added to my playlists and 90% of the content is from artists I'm familiar with. This is not meaningfully improving my user experience or driving me to engage with more content for more ad revenue
- My Premium subscription is justified by one feature: ad-free listening. That's it. I can't use ad blockers in the mobile app, so I pay to avoid interruptions
- The auto video playing on supported podcasts is objectively fucking stupid. It adds 0 value as a listener who's been using the App for 8+ years and actively annoys me that I have to then find out how to turn off the video portion so I can just listen ,,, audio only ,,, on a podcast.

Broader concerns:

- They also started streaming advertisements for ICE (fucking lol) because what does that say about your company and what you stand for? This raises serious ethical questions that are hard to look past and will stain their reputation for years.
- The Padlock service might become necessary at a certain scale, but I have my doubts. Your `users` table which contains username, email etc is the only table that should contain PII data until you build downstream rETL marts to send data up to CDPs. Every table can just include `user_id` as a foreign key for user analytics or tracking so PII data can be locked down to a few tables in the transactional database and the warehouse. If hundreds of tables contain PII, that's a data architecture problem, not a security solution

What I like:

- They clearly define what the goals of the data platform are and what falls under their domain
- They've built out internal tooling to make creating new services and ingesting data streamlined and consistent (which it should be)
- Robust release process, which is required for an app with this scale of user base where 90% of the traffic is coming from mobile devices and they have to release their App through App stores which has more limitations
