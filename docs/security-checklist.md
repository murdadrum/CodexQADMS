# Security Preflight Checklist

Use this checklist before live deployment.

## Secrets and Config
- Ensure `.env.local` exists only on developer machines and never committed.
- Verify GitHub secrets are set:
  - `GCP_WORKLOAD_IDENTITY_PROVIDER`
  - `GCP_SERVICE_ACCOUNT`
- Store Firebase config in `.env.local` (web) and `web_env` deploy input if needed.
- Confirm no secrets are in repo history (scan with `rg` or `git grep`).

## Access Control
- Cloud Run services:
  - Staging can be `--allow-unauthenticated` for internal testing.
  - Production should use IAM or API gateway if sensitive.
- Firebase Auth gating is enabled in the UI when env vars are set.

## IAM
- Deployer account has only required roles:
  - `roles/run.admin`
  - `roles/iam.serviceAccountUser`
  - `roles/artifactregistry.writer`
- Runtime service accounts have minimal roles (see `docs/iam-gcp.md`).

## Dependencies
- Run:
  - `python3 -m unittest -v`
  - `cd /Users/murdadrum/QADMS/apps/web && npm run test:ci && npm run build`
  - `./scripts/smoke_test.sh`
- Address npm audit warnings before production.

## Artifacts
- Use Artifact Registry tags with immutable versions (avoid `latest` for production).
- Record image digests in release notes.

## Logging & Monitoring
- Enable Cloud Run request logs.
- Add error alerts and latency SLOs (Cloud Monitoring).

## TLS + Domains
- Ensure domains are configured and TLS is enforced.
- If using Firebase Auth, configure authorized domains.
