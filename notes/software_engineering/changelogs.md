# Changelog

A changelog is a file which contains a curated, chronologically ordered list of notable changes for each version of a project. It helps users and contributors understand what has changed between releases.

Changelogs are typically set up for software projects w/ external users, but can also be useful for internal projects to track changes over time.

- SaaS platforms like Slack, GitHub, Figma to help users understand new features, bug fixes, and breaking changes.
- Developer toolsssssssss lioke React, Python Packages which are critical for dependency management and migration plannig
- APIs, essential for communicating breaking changes
- Open source projects - documents contributions and evolution for contributors and users

The main purposes are:

- Communication to create a single source of truth of what changed & when, rather than relying on commit history or memory
- Trust and Transparency to show active development and help users feel confident about stability and adoption
- Migration planning gives downstream consumers advance notice of breaking changes so they can plan updates
- Marketing to highlight new features and improvements to attract and retain users

## Example

``` md
## [1.2.0] - 2024-12-29

### Features
- **battery**: add low battery notifications
- **config**: add custom polling interval setting

### Bug Fixes
- **tray**: correct icon rendering on Wayland
- **arctis**: handle device disconnect gracefully

### Documentation
- update README with systemd setup

## [1.1.0] - 2024-11-15

### Features
- **arctis**: add support for SteelSeries Arctis headsets
- **config**: add config file support

### Bug Fixes
- **battery**: fix percentage calculation for some headsets

### Documentation
- add AUR installation instructions
```
  
## Implementation Tools

Conventional Commits + automated tools

- semantic-release (Node.js) - Fully automated: analyzes commits, determines version bump, generates changelog, creates release
- release-please (Google) - Creates PRs with changelog and version bumps based on conventional commits
- standard-version - Generates changelog and bumps version, less opinionated than semantic-release
- commitizen - CLI tool to help write conventional commits interactively

These rely on commit message formats like:

```
feat: add battery level notifications
fix: correct percentage calculation for Arctis headset
docs: update README with installation steps
```

Keep a Changelog format

- changelog-cli - CLI tool for manually maintaining CHANGELOG.md in the standard format
- You just run `changelog added "New feature"` and it updates the file

GitHub-specific

- github-changelog-generator - Pulls from GitHub issues/PRs/tags to generate changelog
- auto - Full release workflow tool with plugin system

For Go specifically

- goreleaser - Handles releases, changelogs, and distribution (works great with GitHub Actions)
- Can integrate with conventional commits or pull from git tags/release notes

Git Cliff

- Rust-based changelog generator that's very fast and highly configurable
- Works with any git repo, not language-specific

### Conventional Commits

Conventional commits are a standardized format for writing commit messages that makes them machine-readable. The basic structure is:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

For PR titles it's just `type(scope): description`. Since Squash Merging and Trunk Based Development are objectively the right way to go now, this works great for generating changelogs from PR titles.

- This means you don't have to follow rigid commit message rules for every single commit, just the PR title when merging
- This makes sense since the PR is the logical unit of change that gets reviewed and merged. If you merge commit 50 commits from a PR into `main`, it would be a mess and not very useful to have all those individual commit messages in the changelog. You also would never revert just one of those commits after a merge, you'd revert the whole PR. 
  - There are no scenarios here where squash merging and trunk based development don't make sense.

Common types:
- `feat:` - New feature (triggers minor version bump)
- `fix:` - Bug fix (triggers patch version bump)
- `docs:` - Documentation changes
- `style:` - Code style/formatting (no logic changes)
- `refactor:` - Code restructuring without changing behavior
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks, dependency updates
- `ci:` - CI/CD configuration changes
- `build:` - Build system or external dependency changes

Scope is optional and specifies what part of the codebase changed:

```
feat(battery): add notification when level drops below 20%
fix(tray): correct icon rendering on Wayland
docs(readme): add AUR installation instructions
```

## TLDR

- Use changelogs to document notable changes in your project, typically for external users or applications serving that purpose
- Follow "Keep a Changelog" principles for clarity
- Auto-generate the changelog using a specific tool that works for your flowssss