# Integrated application and DevSecOps

The application and its current UI originate from the GitHub `main` branch.
The GitLab DevSecOps history is joined with a real two-parent merge. Updated
dependencies, the container build, scanner jobs, and regression tests are retained.
Security fixes cover booking redirects and action validation, password validation,
email verification, request timeouts, and integrity checks for CDN stylesheets.
The current sidebar logo, application templates, and admin action links are kept.

## CI and local deployment

GitLab CI validates Docker Hub credentials, lints and tests the application, scans
source and dependencies, builds the image, scans it and evaluates the security gate.
DAST starts a disposable application plus PostgreSQL inside the CI job's service
network. It never connects to the LAN host or the former public deployment target.
All SSH deployment jobs and `DEPLOY_*` variable requirements have been removed.
The database password and Django key in the DAST job are disposable test values.
The baseline DAST warnings remain advisory, as in the original pipeline.

The service on `ssh 160` is deployed manually after CI passes. It continues to use
the existing PostgreSQL database and systemd service behind nginx. Keep a database
dump and the old virtual environment before applying migrations or replacing the
runtime. After installation run `pip check`, `manage.py check`,
`manage.py migrate --plan`, migrations and collectstatic, restart
`thrdlabapp.service`, and verify the main, furnace, booking and admin pages.

Use `requirements.txt` for runtime, `requirements-test.txt` for tests,
`requirements-lint.txt` for linting, and `requirements-dev.txt` for all developer
tools. Python 3.10 or newer is required; the CI runtime uses Python 3.12.

Read GitLab credentials from the host's untracked `.env`; never commit or print
`GITLAB_TOKEN`. Both `.gitignore` and `.dockerignore` exclude `.env`.

The diploma reports in README-en.md, SECURITY-REMEDIATION.md and img/ are historical
documentation, not instructions to redeploy the former public environment.
