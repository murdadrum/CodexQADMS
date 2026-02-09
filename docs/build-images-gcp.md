# Build and Push Images (GCP Artifact Registry)

This guide uses GitHub Actions `Build Images` workflow and GCP Artifact Registry.

## 1) Create Artifact Registry repo

```bash
gcloud artifacts repositories create "qadms" \
  --project "notional-radio-474312-d4" \
  --location "us-central1" \
  --repository-format "docker" \
  --description "QADMS containers"
```

## 2) Configure GitHub Secrets

Same as `docs/deploy-gcp.md`:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

The service account must have:
- `roles/artifactregistry.writer`

## 3) Run workflow

Use `Build Images` workflow:
- `project_id`: `notional-radio-474312-d4`
- `region`: `us-central1`
- `repository`: `qadms`
- `api_tag`: e.g. `v0.1.0`
- `web_tag`: e.g. `v0.1.0`
- `dry_run`: `false` to push

## 4) Image tags produced

- `us-central1-docker.pkg.dev/notional-radio-474312-d4/qadms/qadms-api:<tag>`
- `us-central1-docker.pkg.dev/notional-radio-474312-d4/qadms/qadms-web:<tag>`

## Local build (optional)

```bash
# API
cd /Users/murdadrum/QADMS
docker build -f docker/Dockerfile.api -t qadms-api:local .

# Web
cd /Users/murdadrum/QADMS
docker build -f docker/Dockerfile.web -t qadms-web:local .
```
