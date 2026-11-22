# Single writer
Only orchestrator workflow controller may mutate the execution plan. Specialists have read-only plan access. Filesystem/GitLab permissions must enforce this in deployment; local code alone is not an access-control boundary.
