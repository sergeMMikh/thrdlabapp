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

The service on `ssh 160` runs the ready-made Docker Hub image after CI passes.
Deployment verifies the pipeline and OCI revision label, pins the image digest,
backs up the database, applies migrations, and checks health and main pages.
PostgreSQL remains the existing external container; nginx stays on the host.
Static files are collected during the CI image build and copied from that exact
artifact. No image build, pip installation or collectstatic runs on the LAN host.
See [LAN-DEPLOYMENT.md](LAN-DEPLOYMENT.md) for update and rollback commands.

Use `requirements.txt` for runtime, `requirements-test.txt` for tests,
`requirements-lint.txt` for linting, and `requirements-dev.txt` for all developer
tools. Python 3.10 or newer is required; the CI runtime uses Python 3.12.

Read GitLab credentials from the host's untracked `.env`; never commit or print
`GITLAB_TOKEN`. Both `.gitignore` and `.dockerignore` exclude `.env`.

The diploma reports in README-en.md, SECURITY-REMEDIATION.md and img/ are historical
documentation, not instructions to redeploy the former public environment.

The first integrated audit found three new advisories in DRF 3.18.1
(CVE-2026-114136, CVE-2026-114137, CVE-2026-114138). DRF is updated to
3.18.2, the fixed version reported by pip-audit. Dependency findings now block
the security gate instead of being report-only. CI DAST uses a per-build network
so the disposable application and PostgreSQL can resolve each other's aliases.
