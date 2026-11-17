# Deploy a tested Docker Hub artifact to ssh 160

CI builds and scans `sergemmikh/thrdlabapp-devsecops-diploma:<commit-short-sha>`.
The image contains the application, pinned dependencies and collected static files.
The host only pulls the image, checks its revision label, pins its SHA-256 digest,
backs up PostgreSQL, applies migrations and starts the container. The Docker build
and Python dependency installation run exclusively in CI.

The application uses one Gunicorn worker by default, matching the prior service.
It runs as the image's unprivileged `django` user with a read-only root filesystem,
no Linux capabilities and a temporary `/tmp`. Only nginx can reach its published
port at `127.0.0.1:8000`. The existing `pg-standalone` container and database volume
are used via their existing external Docker network; no second database is created.
The image digest is pinned rather than following the mutable `latest` tag.

## Update

After all jobs of the GitLab main pipeline succeed:

```sh
ssh 160
cd /home/smm/thrdlabapp
git pull --ff-only gitlab main
python3 scripts/deploy_lan.py --pipeline PIPELINE_ID
```

Prerequisites: Docker Engine, Compose 2.30 or newer, Python 3.10 or newer, Docker
access for `smm`, and permission to manage `thrdlabapp.service` with `sudo -n`.
GitLab CI does not connect to or deploy into the LAN automatically.

The token is read from `GITLAB_TOKEN` in the host's untracked `.env`. Only an explicit
allowlist of Django/database/email settings enters the private runtime env file.
The GitLab token and CI credentials are never passed to the application container.
`/home/smm/thrdlabapp/.deployment/` is excluded from Git and Docker builds and
has mode 700.

The script keeps the existing database settings and SECRET_KEY semantics. If
SECRET_KEY is absent, set a private stable key in `.env` as a separate planned
configuration change; changing it invalidates existing signed sessions.

## Status and rollback

```sh
python3 scripts/deploy_lan.py --status
systemctl status thrdlabapp.service
docker compose --project-name thrdlabapp-lan --env-file .deployment/active.env \
  -f .deployment/active.compose.yaml ps
python3 scripts/deploy_lan.py --rollback
```

The active Compose configuration is snapshotted alongside the image digest, so a
later git pull cannot change a running release or its rollback configuration.
The systemd service keeps its existing name. A drop-in replaces the host Gunicorn
command with foreground Compose using `--no-build --pull never`. The application's
container restart policy and systemd start it after reboot. Logs stay bounded and
are visible through `journalctl -u thrdlabapp.service` or Docker Compose logs.

Before each switch a mode-600 `postgres-all.sql.gz` and the previous service/image
configuration are stored in `.deployment/<timestamp>-<commit>/`. Runtime failures
automatically restore the prior service, image and static files. A manual rollback
performs the same operation. Database migrations are not automatically reversed:
the full dump is available for an explicitly planned database restore if a future
migration is incompatible with the previous application version.

The initial migration to containers also retains the former host Python environment
and systemd unit for rollback. Business record counts are checked before and after
migrations; the deployment stops if they change.

Compose's external-network behavior is documented in the
[Docker networking reference](https://docs.docker.com/compose/how-tos/networking/).
