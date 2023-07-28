# Git Strategies
2 flows

## Trunk Based Development
Trunk Based Development revolves around 1 long-lived branch: `master`.
- Nobody can push directly to master, all changes must be made through code-reviewed PRs
- All developers develop in short-lived feature branches and then make pull requests into master
- Constant deployments are happening because everybody is merging their stuff into the 1 branch
- Small frequent updates
- Feature flags are extremely common to push code to master that you may still want to test or potentially disable
- Leads to more nimble, agile development processes

This workflow is generally seen as "best practice" for Git Branching strategies
- Code needs to be properly code reviewed and QA'd for bugs and regression testing; this is even more important because there is only 1 long lived branch
- CI CD must be top notch to catch bugs and ensure the application still performs fine.

Typically, PRs into `master` branch trigger Staging builds.  To trigger a production build, you branch of master and create a Release Branch that undergoes thorough QA + Regression testing.
- This seems just like Gitflow except with tags instead of branches.


```
name: Trunk-based Production Deploy

on:
  workflow_dispatch: # Manual trigger

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest

    steps:
      - name: Check if branch includes "release"
        run: |
          # Get the branch name from the GITHUB_REF environment variable
          branch_name=${GITHUB_REF#refs/heads/}
          if [[ $branch_name == *"release"* ]]; then
            echo "Branch includes 'release'. Proceeding with the deployment."
            exit 0
          else
            echo "Branch does not include 'release'. Skipping deployment."
            exit 1
          fi

      - name: Checkout code
        uses: actions/checkout@v2

      - name: Install and build (replace this with your build steps)
        run: |
          # Replace these commands with your build and setup steps
          npm install
          npm run build

      - name: Deploy to Production (replace this with your deployment steps)
        run: |
          # Replace this command with your deployment process to the production environment
          echo "Deployment to production completed."

```

## Gitflow
Gitflow revolves around multiple long-lived branches for development, staging, production, release, hotfix etc.
- Some companies pick different ones of these that they want
- Large infrequent updates
- Suitable for more conservative approaches to releases where rigorous testing and stability are critical
- Requires more effort to keep branches in sync to avoid merge conflicts and diverging long lived branches

All PRs must go into development, and then once things look good you merge from development upwards.