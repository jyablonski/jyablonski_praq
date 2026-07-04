# Contract Testing

## What problem contract testing solves

In a system made of multiple services, the risky part isn't whether each service works in isolation, it's whether they still agree on their interfaces when they talk to each other. Service A calls Service B; if B changes a field name, a status code, or a response shape, A breaks. Nothing in B's own unit tests will catch this, because B looks perfectly healthy on its own.

The obvious way to catch integration breaks is to stand up both services together and exercise them end-to-end. That works, but it's the slowest and most expensive tier of testing: you assemble the stack, run migrations, boot every service, and pay for network hops and flakiness. It also doesn't scale, it's often very expensive or complex to spin up every team's stack to validate one interface.

Contract testing replaces "run both services together" with two cheap, independent checks connected by a shared contract, a description of the requests one side makes and the responses the other side promises. Each side tests against the contract alone, so neither service ever needs the other actually running.

## Why teams use it

- Integration confidence without e2e cost. You verify two services agree without co-locating them in one environment.
- Fast, functional CI. Both sides' tests run at unit-test speed, in separate pipelines, at separate times.
- Catches breaking changes before merge. A change that violates the interface fails a build, not production.
- Decouples teams. A provider learns it's about to break a consumer it may never talk to directly.

## What Pact is

Pact is an open-source tool and specification for consumer-driven contract testing. You pull a Pact library into your existing test suites (pact-jvm, pact-go, pact-js, etc.). The contracts are owned by *your* teams, Pact is the machinery, not an authority that authors contracts.

The key inversion: in the classic model, the consumer defines the contract. The consumer's expectations *are* the contract, produced as a byproduct of the consumer's own tests.

## How consumers and providers use it

### Consumer side

1. The consumer writes a test against a mock provider that Pact stands up locally.
1. In that test it declares expectations: "when I call `GET /users/123`, I expect a 200 with this shape."
1. As those tests pass, Pact generates a pact file (JSON) recording each interaction. Matchers (type/regex) are used so contracts pin *shape*, not exact values.
1. The consumer publishes the pact file to a shared registry (the Broker).

The consumer never spins up the real provider. Note the direction: the contract is an output of consumer tests, not an input.

### Provider side

1. The provider pulls the relevant pacts from the Broker.
1. It runs verification: Pact replays each recorded interaction against the *real running provider* and checks the actual response satisfies what the consumer recorded.
1. The provider publishes the verification result (pass/fail for that provider version) back to the Broker.

The provider runs only itself, never the real consumer. Here the contract is an input.

### The asymmetry to remember

- Consumer: contract is an output; it never reads from the Broker during tests, only publishes afterward.
- Provider: contract is an input; it reads from the Broker and verifies against it.

Truth is split: the consumer owns *what's expected*; the provider's verification result owns *whether the expectation is met*. The Broker holds both halves.

## What Pact tests, and what it doesn't

Pact verifies the interface: shape, status, presence of fields, not deep business logic. It confirms "the provider returns what the consumer expects for this request," not that the computation behind it is semantically correct. Keep matchers loose so contracts don't become brittle.

## How it's hosted

Two distinct components, easy to conflate:

- The Pact Broker (or hosted PactFlow) is a long-running, always-on service, a Ruby web app you run 24/7 in your infra (k8s Deployment, ECS service) or pay PactFlow to host. It's the shared registry different pipelines hit at different times. It's backed by a relational database — Postgres is standard for production (MySQL supported; SQLite for local/throwaway).
- The CLIs (`pact-broker publish`, `pact-verify`, `can-i-deploy`) are short-lived invocations — HTTP clients that spin up for a few seconds inside a CI job, hit the Broker's REST API, and exit.

So: one persistent server, many transient CLI clients calling it from various pipelines.

### What the Broker stores

- The pact files (interactions + matchers).
- Every consumer and provider version (keyed by git SHA / app version).
- Verification results per (consumer version, provider version) pair.
- Environment tags, which versions are live in `prod`, `staging`, etc.

Mentally: a database of "which versions of who have been proven to work with which versions of whom, and where each is deployed."

## Gating deploys with `can-i-deploy`

`can-i-deploy` is a CLI step run before deploy in each side's pipeline. It queries the Broker: "for the version I'm about to ship, has it been verified against whatever is *currently live* on the other side?" If not → the deploy is blocked.

This guards a timing/versioning problem that test-time checks can't see:

- Stale verification. Tests proved provider X satisfies consumer contract Y — but is Y actually what's in prod right now? The consumer may have shipped a newer contract since. `can-i-deploy` re-checks against what's live.
- Independent deploy ordering. A consumer ships a new expectation before the provider that satisfies it is deployed. Both suites passed individually; neither run knew the other's deploy timing. Only the deploy gate catches this.

## Where the value actually sits

Most of the protection comes at CI/test time, not the deploy gate:

- Provider verification failing the build is what catches "did I break my consumers?" — this needs no `can-i-deploy`.
- Consumer tests still pin and document expectations as a hermetic artifact.

`can-i-deploy` adds protection specifically for independent, high-frequency, out-of-order deploys across teams — the scenario Pact was built for. If both sides are owned by one team and deploy in lockstep, the timing gap barely exists, and test-time verification alone is a reasonable place to stop.

Adoption can be incremental: run verification in CI first; add the deploy gate later, when independent deploy cadence starts to make the timing gap hurt.

## Moving-parts inventory (self-hosted)

- Always on: Broker container + its Postgres (the source-of-truth state to back up).
- Per pipeline (ephemeral CLI steps):
  - Consumer: `publish` the pact.
  - Provider: pull pacts → `verify` → publish results.
  - Both, pre-deploy (optional): `can-i-deploy`.
