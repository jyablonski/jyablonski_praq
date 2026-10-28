## sailthru model conversion

i want to separate out the new content subscriptions and user subscriptions models into a separate pipeline chain in sailthru to not interrupt the existing mart models.

tessa created most of these new ones; plesae identify them and double check

lets update the tags on them to change it to a subscriptinos and sailthru combination. then we'll add 3 new dbt tasks in the sailthru pipeline to update these models in parallel with the existing stg intermediate mart ones.

create a ticket for this work in this epic and please proceed.

## governance spike doc

i fully completed an end to end example of a chatgpt snowflake-powered analytics assistant plugin powered by a snowflake mcp and cortex agents. the details are in this repo.

can we put together a summary specific to axios that i can bring back to the team on how to proceed.

## ga4 attribution inveestigation

my colleague recently setup new ga4 tagging on this axios newsletter signup page. can we see if these events are landing in whichever relevant ga4 table we should go look at?

we're particularly interseted in seeing attribution information which preivously wasnt available on this page since it took users off the site and we didnt transfer anything.

---

> if needed, go in monorepo and ask

my colleague recently setup new ga4 tagging on this axios newsletter signup page. can we see how user attribution like how they got on the page or when they clicked on a link to put in their inforamtion is tracked in ga4? im not sure the specific service here, but i think it's services/axios-web

## ga4 attribution dbt modeling

i want to scope out an epic of work to handle reporting onthis newsletter signup attribution data. we want to track both users who signed up, and users who were approved, and do attribution on both, probably with a filter selection of 4 choices (all, approved, pending, denied)

i dont know the exact work thats needed, but we want to be able to report on xyz.

dont create tickets yet, but please scope out the necessary tickets you'd expect for the work to be able to handle this with strong accuracy.

## cleanup epic

my team deprecated redshift 4 months ago and still has many reosurces up, like old s3 buckets, the dbt/ directory, axdbt is a dbt package internal to us that we use which is still in dbt/ directory, as well as various airflow references like hydra and pulsar still.

i'd like to clean up most of this where possible. can we do a comprehensive audit of everything and see what was only connected to redshift that we can now get rid of?

a lot of other things like glue

please break it down in terms of potential tickets in a new jira epic, but dont make those resources yet.

---

please make a new jira epic with the x tickets for the work. keep the tickets brief but informative with suggested code files, bucket names, or other useful information.

## fides fix

my colleague was having a hard time with the fides-validation ci/cd workflow this week where it was failing in PRs. i impelemnted tihs last friday and it worked fine, but on some PRs like this one, it errors out and i dont know what the issue is.

please review and investigate.

## pipeline doc epic

can you please make a new jira epic to create pipelines docs in pipelines/dags/docs for each of the following pipelines if not already created or setup with the existing template:

- sailthru
- recurly
- ga4
- hubspot
- predicthq
- pac to snowflake
- retention ones
- sailthru ads report
- user profile
- airflow failure logs
- domain to snowflake

dont make a ticket for a pipeline that already has a doc that's using the template.