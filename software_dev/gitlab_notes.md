# GitLab
[GitLab Link](https://gitlab.com/jyablonski1/jyablonski_project)
[Youtube video](https://www.youtube.com/watch?v=PGyhBwLyK2U)

CI CD File must be called `.gitlab-ci.yml` in the project root.

Pipeline is set of jobs organized into stages that either pass or fail in response to events (merge requests etc).
    * Directions are stored in the yml file.

GitLab Pipelines are ran on `Runners`, which are the compute resources for your job.
    * You can either configure specific runners like your own, with your personal PC, EC2, or some other registry.
    * Or use shared GitLab-provided ones.
    * These runners are ephemeral containers and run their jobs and then immediately gets destroyed.

Artifacts are things you want to save in these ephemeral runners.

Variables can be defined in each job/stage or globally at the beginning.