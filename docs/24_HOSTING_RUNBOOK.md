# Single-owner hosting candidate — 2026-10-05

No cloud account, server, domain or deployment has been created. This runbook makes the eventual deployment reviewable. Empirical/model/retention gates in docs/23 still apply. Hosting the app does not validate its AI quality or complete the six-month course.

## Prepared topology

`compose.hosted.yaml` exposes only Caddy ports 80/443. The web, API and PostgreSQL services have no host ports. Caddy terminates TLS and forwards to Next.js. Next uses a fixed HTTPS browser origin and Secure HttpOnly session cookie. API connects as `career_runtime`, which has table DML permissions but does not own the tables and cannot change schema or disable raw immutability triggers. A separate migration service uses the owner credential.

The database role initialization script runs only on a **new** PostgreSQL volume. It deliberately refuses duplicate role creation. For an existing volume, perform a reviewed role migration; do not delete the volume to make initialization run again. Application sessions expire server-side after eight hours; rotating the master key invalidates old sessions. This is a single-owner service, not multi-tenant SaaS.

## Prepare without deploying

Requires a Linux server with Docker/Compose, an owned domain and DNS control. Review the target before incurring charges.

```sh
python3 scripts/init_hosted.py career.your-domain.example
docker compose --env-file .env.hosted -f compose.hosted.yaml config --quiet
```

The script generates distinct random database and access credentials into a new mode-0600 `.env.hosted`, refuses overwrite and prints no secrets. Never commit or paste this file. AI remains disabled by default. Configure its provider/model/call limit only after accepting the provider's data handling and cost.

## Deployment after target approval

Point DNS to the approved server and permit TCP 80/443. Then, on that server:

```sh
docker compose --env-file .env.hosted -f compose.hosted.yaml up --build -d --wait
```

Public certificate issuance depends on real DNS/port reachability and has **not** been tested here. CI validates the Compose configuration and Caddy configuration only. Before personal use, verify HTTPS, certificate renewal storage, login/logout, restart persistence, private service ports and backup restoration on the actual target. Configure external uptime/error/disk monitoring and notifications with the account owner. Do not send application content or secrets to logs.

## Backups and upgrades

Use the hosted Compose target explicitly with the backup/restore scripts:

```sh
CAREER_COMPOSE_FILE=compose.hosted.yaml CAREER_COMPOSE_ENV_FILE=.env.hosted \
  python3 scripts/backup.py backups/pre-upgrade.dump
CAREER_COMPOSE_FILE=compose.hosted.yaml CAREER_COMPOSE_ENV_FILE=.env.hosted \
  python3 scripts/restore_drill.py backups/pre-upgrade.dump career_restore_preupgrade
```

Backups are not encrypted by these scripts. Encrypt and schedule offsite copies using the owner's chosen storage/key management; test retrieval and restoration there. Retain Caddy data volume for TLS account/certificate continuity. Keep source-retention policy consistent across primary data, derived snapshots and backups.

For an upgrade: take and restore-test a backup, pin the reviewed commit, stop API/web, run migrations as the owner, then start the runtime services and verify readiness. On an unexpected schema failure, keep services stopped and inspect; never downgrade a live database blindly. A rollback that needs a prior schema uses a separately restored database and reviewed cutover.

## Verification sources

- [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https), checked 2026-10-05.
- [PostgreSQL default privileges](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html) and [psql](https://www.postgresql.org/docs/current/app-psql.html), checked 2026-10-05.

CI checks the restricted role can read raw data and cannot disable its immutability trigger. It does not prove every production security property. Live TLS, offsite encrypted backup, alert delivery and final user acceptance remain deployment gates.
