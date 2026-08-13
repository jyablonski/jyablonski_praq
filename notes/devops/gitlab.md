# GitLab

## What It Is

[GitLab](https://docs.gitlab.com/) is a web-based software development platform built around Git repositories. A GitLab project combines a repository with code review, issue tracking, planning, CI/CD, package and container registries, releases, security scanning, and operational tooling.

GitLab describes itself as a DevSecOps platform because it attempts to cover the complete software delivery lifecycle in one product: plan work, write and review code, build and test it, scan it, deploy it, and monitor the result. Teams can use only the source-control features or gradually adopt the rest of the platform.

A project is the main unit of work and contains the repository and its related development resources. Projects live in user namespaces or groups; groups can contain nested subgroups and apply membership and settings across related projects.

The main deployment offerings are:

- GitLab.com: GitLab's managed, multi-tenant SaaS service.
- GitLab Self-Managed: GitLab installed and operated on infrastructure controlled by the customer.
- GitLab Dedicated: A managed, single-tenant GitLab environment intended for organizations with stronger isolation, networking, residency, or compliance requirements.

GitLab uses an open-core model. [Community Edition is MIT-licensed, while Enterprise Edition includes code under GitLab's more restrictive EE license](https://docs.gitlab.com/development/licensing/). Free, Premium, and Ultimate subscriptions determine which features are enabled; exact entitlements change, so consult the [current feature comparison](https://about.gitlab.com/pricing/feature-comparison/).

## Differences From GitHub

Both platforms host Git repositories and provide issues, code review, access control, automation, releases, package registries, security features, APIs, and hosted or self-hosted enterprise options. Git commands and repository data remain portable, but platform-specific issues, permissions, automation, and metadata require migration work.

| Area | GitLab | GitHub |
| --- | --- | --- |
| Proposed code change | Merge request (MR) | Pull request (PR) |
| Organization | Projects inside groups and nested subgroups | Repositories owned by users or organizations; teams organize access |
| Product emphasis | Broad, integrated planning-to-production DevSecOps platform | Code collaboration platform with first-party products and a large app and Actions ecosystem |
| Native automation | GitLab CI/CD | GitHub Actions |
| SaaS | GitLab.com | GitHub.com / GitHub Enterprise Cloud |
| Self-hosted platform | Self-Managed Free, Premium, or Ultimate editions | GitHub Enterprise Server, available with an Enterprise plan |
| Source model | Open-core, with an MIT-licensed Community Edition | Proprietary service and Enterprise Server appliance |

GitLab's nested groups are useful when permissions, compliance settings, CI configuration, and reporting should follow a business hierarchy. GitHub organizations use teams and repository roles for access, while enterprise accounts centrally manage multiple organizations.

GitLab generally exposes more of the delivery lifecycle inside the same project navigation. GitHub covers much of the same ground through GitHub Actions, Projects, Packages, Environments, Code Security, Secret Protection, and Marketplace integrations, but the experience is more repository- and ecosystem-centered.

Neither platform is universally better. GitLab is often attractive to teams seeking one integrated platform, deep CI/CD orchestration, or flexible self-management. GitHub is often attractive when public open-source reach, developer familiarity, GitHub-native integrations, or the Actions marketplace matter most. Plan and tier comparisons should be made against current pricing pages because paid feature placement and usage allowances change.

## CI/CD Differences

GitLab CI/CD normally starts with one `.gitlab-ci.yml` file at the repository root. It defines jobs, scripts, images, services, variables, caches, artifacts, environments, and deployment behavior. Jobs are grouped into ordered stages and jobs within a stage run in parallel by default; `needs` can instead form a dependency graph that starts jobs as soon as their dependencies finish.

GitHub Actions uses one or more YAML workflow files in `.github/workflows/`. An `on` block selects events, each workflow contains jobs, and jobs contain steps that run shell commands or reusable actions. `needs` expresses job dependencies and `strategy.matrix` expands a job across operating systems, runtime versions, or other dimensions.

| Concern | GitLab CI/CD | GitHub Actions |
| --- | --- | --- |
| Default configuration | `.gitlab-ci.yml` | One or more `.github/workflows/*.yml` files |
| Trigger logic | `workflow:rules`, job `rules`, schedules, API, and manual pipelines | `on` events, filters, schedules, API, and manual dispatch |
| Execution host | GitLab-hosted or self-managed GitLab Runners | GitHub-hosted or self-hosted Actions runners |
| Reuse | `include`, templates, CI/CD components, and the CI/CD Catalog | Actions, reusable workflows, workflow templates, and Marketplace |
| Large systems | Parent-child and multi-project pipelines | Reusable and callable workflows across repositories |
| Dependency graph | Ordered `stages` plus `needs` DAGs | Jobs are parallel by default and ordered with `needs` |
| Pull/merge integration | Merge request, merged-results, and merge-train pipelines | Pull-request workflows, required checks, and merge queues |

[GitLab Runners](https://docs.gitlab.com/ci/runners/) and GitHub Actions runners serve the same basic purpose: they claim queued jobs, prepare an execution environment, run commands, and return logs and status. Both platforms offer hosted runners and allow runners on private infrastructure for custom hardware, private-network access, or stronger control.

GitLab's pipeline model is especially explicit about cross-project delivery flows and visualizes upstream and downstream pipelines together. GitHub Actions has a particularly large ecosystem of reusable actions, although third-party actions should be pinned to immutable commit SHAs and reviewed because workflow code can access repository data and credentials.

Secrets should be stored in protected CI/CD variables or an external secrets manager, never in pipeline YAML. On either platform, restrict token permissions, isolate untrusted code, protect production environments, and be cautious when forks or external contributions can trigger automation.

References: [GitLab pipeline concepts](https://docs.gitlab.com/ci/pipelines/), [GitLab CI/CD YAML reference](https://docs.gitlab.com/ci/yaml/), [GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), and [GitHub runner selection](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job).

## Self-Hosted Options

[GitLab Self-Managed](https://docs.gitlab.com/install/) can run on-premises, in a private cloud, or in a public-cloud account. Self-hosting provides control over data location, networking, identity, upgrade timing, runners, and integrations, but transfers responsibility for availability, security patches, backups, monitoring, capacity, and disaster recovery to the operator.

Supported installation approaches include:

- Linux package: The most mature and generally preferred installation; it bundles GitLab and required services and is the basis of GitLab.com's deployment.
- Docker: Convenient for evaluation and smaller deployments, but persistent volumes, backups, upgrades, and container operations still require planning.
- Helm chart or GitLab Operator: Kubernetes-native approaches suited to teams already capable of operating stateful, production Kubernetes workloads.
- Reference architectures: Validated starting points for larger or highly available deployments, with components separated and scaled according to load.
- GitLab Environment Toolkit: Opinionated Terraform and Ansible automation for deploying selected reference architectures on major cloud providers.
- Self-compiled installation: Available for unusual platforms or development needs, but more complex and normally a last resort.

GitLab is not a lightweight Git server. The [current requirements](https://docs.gitlab.com/install/requirements/) list 8 vCPU as the baseline for a single-node installation, and storage performance matters because repository service Gitaly is I/O intensive. Size from measured workload rather than user count alone, especially with large monorepos, heavy API usage, registries, security scans, or many CI jobs.

GitLab Runner is installed separately from the GitLab application. Runners may use shell, Docker, Kubernetes, or other executors and can be scoped to an instance, group, or project. A self-managed GitLab instance can also use runners on separate infrastructure so CI workloads do not exhaust the application node.

Before production use, plan TLS and DNS, email, authentication and SSO, object storage, registry storage, backups and restore tests, observability, upgrades, runner isolation, and disaster recovery. High availability adds PostgreSQL, Redis, object-storage, repository-storage, load-balancing, quorum, and low-latency networking concerns; start from GitLab's [reference architectures](https://docs.gitlab.com/administration/reference_architectures/) rather than designing these relationships from scratch.

For a personal lab or small trusted team, a single Linux-package or Docker deployment is usually the simplest starting point. For a business-critical service, choose the deployment only after assigning operational ownership and estimating the total cost of maintenance; GitLab.com or GitLab Dedicated may be cheaper than operating a resilient Self-Managed installation.
