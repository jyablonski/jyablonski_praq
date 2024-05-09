# Git
Git is a Version Control Software used to help you manage source code for your software applications. It helps coordinate work among multiple team members to enable you to collaboratively contribute to the same project at once and safely & consistently push updates out to your code.

A repository is a central location where files and data for a project are stored and managed. It contains the files for the source code, commit history, and any branches. Repositories can exist locally on 1 person's computer, or remotely when hosted on a Platform like GitHub or Gitlab which enables multiple people to collaboratively work on the same project.

Branches a line of development that diverges from the main branch of the Git repository. Branches allow you or other developers to progress independently of each other from within the same repository.  Each branch has its own commit history that starts with some base shared commit from the parent (or main) branch.

Git uses commits which are snapshots of the project at a specific point in time. As you make changes you can save your files and create commits to record those changes permanently in your branch. Under the hood Git creates a commit by hashing the state of the project which serves as a unique identifier and also stores some metadata related to the commit like the timestamp, the author, and a commit message. Together this enables an immutable workflow and a linear history of commits so you can also know the most recent version of the code and also go back to a certain point of time if needed.

When a Branch is ready to be merged to another branch, the `git merge` command is used. This command automatically combines the changes from the new branch onto the source branch, creating a new commit that incorporates both sets of changes.

Rebasing is a Git operation that allows you to change the base of a branch and move the entire branch to begin at a different commit, effectively changing its commit history.  It's useful for:
- Squash Merging
- Resolving Merge Conflicts
- Keeping a Clean History
- Squash Merge on GitHub works by combining all commits on a PR into 1 commit.

A pull request is a mechanism to propose new changes to a repository. It allows developers to notify eachother about potential changes they've made and request feedback, review, and integrate those changes back into the main codebase. Pull requests can be approved by other people, have various tests run when they're created to check if the proposed changes still allow the application to function, and ultimately merged back into the codebase.

``` sh
git checkout your_branch_name

# replace n with the number of commits you want to squash
# -i means interactively, which allows you to choose which commits to squash and how to combine them.
git rebase -i HEAD~n
git push origin your_branch_name --force

```

Tags are references to specific pointesr in a repository's commit history.  They are often used to mark release points in a project's history, allowing users to quickly and easily identify and checkout specific releases.  There are 2 types of Tags:
- Lightweight Tags - Simple pointers to specific commits and are created from the `git tag` command followed by a tag name
- Annotated Tags - Include information such as tagger name, email, date, and tag message created from `git tag -a` followed by a tag name
- Tags are pushed with the `git push --tags` command

Hooks are scripts that Git executes automatically after certain events, typically when commiting code changes. When setup properly, they can run various Scripts for things like Code Linters, Formatters, and even Unit Tests as you try to commit your changes. If the hooks fail, then you'd be blocked from commiting the changes. The goal of these would be to lint & format your code before you ever check it into version control.

More advanced Git Topics:
- Cherry-picking
- Forks
- Stash
- Revert
- Reset

## Why Squash Merging
- Concise commit history. You can more easily see the changes that have gone into a repo, who made them, and what they were for (features, bug fixes etc). If you have dozens of small commits, this becomes much more difficult to track.
- Enables a standardized commit workflow.  Some devs might prefer writing dozens of small commits to make 1 line code changes, others may write code for days and commit all their changes at once only when they're confident the work is ready to go.  If the code ultimately gets squash merged into `main`, then the either commit workflow here ultimately looks the same.
- Once squash merged, each commit on the `main` branch can have a meaningful title, ticket number and proper detail that is inherited from the PR. Nobody will do this for every single commit, but they can do it for every single PR.
- This workflow behvaes the exact same if the pull requests weren't squash merged.  Need to go commit-by-commit to find a regression?  you can still do that.
- Rollbacks are much more simple and intuitive.  Each commit on the `main` branch is from a feature branch that was squash merged into `main`.
  - Release `v1.6.4` broke the App ?  Just rollback 1 commit to `v1.6.3`
- Enables solid CI best practice.  You *want* to commit your code changes and get a PR up to have the CI running as fast as possible so you can have confidence your proposed changes work as early in the process as you can.  
  - If you work on a feature for 3 days and then get it on a PR on day 4 just to find out half the tests broke from a change you made on day 1 that you built your work upon, then that's dumb as fuck.