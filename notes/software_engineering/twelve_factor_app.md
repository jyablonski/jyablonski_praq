# Twelve Factor App
[Article](https://12factor.net/)

Twelve Factor App is a methodology for building software-as-a-serivce apps in any programming language that:
- Use Declarative Formats for setup automation for easy onboarding for new devs
- Are suitable for Deployment on modern cloud platforms
- Minimize divergence from Dev & Prod environments, enabling continuous deployment for agility
- Can Scale up without significant changes to tooling, architecture, or dev practices

This is relevant for any Dev who writes application code or Ops Egnineer who deploys or manages such applications.

## Codebase
Application Code should always be tracked in a version control system like Git. 
- If multiple codebases contribute to an app, then it's a distributed system.  All of those codebases should comply with twelve-factor.
- Multiple apps sharing the same code is a violation of twelve-factor.  The shared code should be split into libraries and included through dependency / package manager
- 1 codebase per app

There will be many deploys of an app over time.  A deploy is typically something like a production site, or one or more staging sites. Devs can also have copies of the app running in their local dev environment.  The codebase should be the same across all deploys, but versions may change ex. a dev has some recent commits for changes on their local app that aren't pushed up to staging or prod yet.

## Dependencies
Twelve Factor apps should never rely on implicit existence of system-wide packages. Declare all dependencies via a declaration manifest, and make sure no external dependencies leak in somehow.  
- Example: Pip for declaration and virtualenv or poetry for isolation.

This simplifies setup for new devs.  They can clone the codebase and only need the language runtime and the dependencyh manager installed to get started.

## Config
An app's config is anything that is likely to vary between environments such as credentials, environment name, database connections etc. Config values shoulds never stored as constants in the code.  An easy test for this is if the codebase was made open source - would any secrets or credentials be compromised? 

Twelve Factor apps should store config in environment variables, which can change between deploys without changing code. These should never be grouped as environments in a config file (like separate configs for dev, stg, prod).

## Backing Services
A Backing Service is any service that the app consumes over the network during normal operations.  Think Databases, Cache Stores, S3 etc. You should be able to swap these out for any other resource by changing the connection details stored in the config without needing sweeping changes in the codebase.

If the current MySQL Database is misbehaving due to a hardware issue, you shoulds be able to spin a new one up and swap over to it without needing code changes.

## Build, Release, Run
- Build Stage transforms the code repo into an executable bundle known as a build using a version of the code at the commit during the deploy process.
- Release Stage takes the build and combines it with the deploy's current config to contain both the build and the config so its ready for immediate execution
- Run stage runs the app in the execution environment

Other Notes:
- Code should be immutable after the build stage.
- Each release should have its own unique release ID (such as SemVar Versioning etc)
- Any code change must require a new release

## Processes
In simplest cases, an app could just run a single process like so `python my_script.py`.  In other cases, a sophisticated app might use many processes and require many different running processes.

Twelve Factor processes should be stateless and share nothing.  Any data that needs to persist must be stored in a stateful backing service like a database. Memory on the server running the app can be used for a brief cache but it should never be assumed that the app has anything cached in memory.

You should be able to restart the app at any time and things should just work.

## Port Binding
Twelve Factor apps should be self contained and export services via port binding. You shouldn't host your ecommerce websites at like `http://my-store.com:5000`.  Webservers typically run on certain ports which are appended to the domain name, but this isn't user-friendly and can be confusing for customers.

## Concurrency
Your apps eventually might hit performance limits and require you to horizontally scale. If you're following the share-nothing model and you're not storing any session or user data on any app server, this should be a simple and reliable operation.  This approach allows you to scale modern web apps to handle a large number of users and requests simultaneously.

## Disposability
Twelve Factor app's processes are disposable, they should be able to be started and stopped at a moment's notice to facilitate easy scaling, rapid deployment of code or config changes, and robust production deploys.

The lower your startup time the better.  This provides more agility to your release process. 

Shutdown should also be handled gracefully, like if you scaled out to meet demand for peak hrs then have a bunch of workers spin down during off hrs.

## Dev / Prod Parity
Sometimes gaps exist in between dev and prod environments
- Time gap - dev works on code that takes weeks / months to go into production
- Personnel gap - devs write application code, ops engineers deploy it
- Tools gap - devs use Nginx, SQLite, Windows etc while prod uses Apache, MySQL, and Linux

Twelve Factor apps are designed for continuous deployment by keeping that gap between dev and prod small. 
- Make the time gap small - release smaller feature branches more often to production
- Make the personnel gap small - devs who write the code should be closely involved with deploying it and watching its behavior in prod
- Make the tools gap small - keep the tooling the same as much as possible

Backing services like databases or caches are an area where it's especially important to keep dev and prod similar.  Try to use the same backing services for every environment, dont try cutting corners or you'll get burned.

## Logs
Logs are the stream of aggregated, time-ordered events collected from the output streams of all running processes and backing services.

Don't use log files or spend resources managing that.  In local dev, developers can just view the log stream in their terminal.  In hosted environments, the process' log stream can be captured by the execution environment and routed to some final destination for viewing such as Cloudwatch, Elasticsearch, Graylog etc.

Monitoring systems can be hooked up to these logs to assess the app's performance over time, and alert developers if certain thresholds are being passed.

## Admin processes
Devs often need to perform various one-off admin or maintenance dtasks for an app, such as:
- Database migrations
- Small Scripts `php scripts/fix_bad_records.php`

These processes should be run in an identical environment as the long running process of the app.  They should run against a release, using the same codebase and config.