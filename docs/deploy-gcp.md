# GCP Deploy Setup (OIDC + Cloud Run)

This doc wires the deploy workflow (`.github/workflows/deploy.yml`) to Google Cloud using GitHub OIDC.

## 1) Create Workload Identity Pool + Provider

Example (adjust names and org policy):

```bash
gcloud iam workload-identity-pools create "qadms-github" \
  --project "notional-radio-474312-d4" \
  --location "global" \
  --display-name "QADMS GitHub Actions"

gcloud iam workload-identity-pools providers create-oidc "qadms-provider" \
  --project "notional-radio-474312-d4" \
  --location "global" \
  --workload-identity-pool "qadms-github" \
  --display-name "QADMS GitHub Provider" \
  --attribute-mapping "google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri "https://token.actions.githubusercontent.com"
```

## 2) Create Deploy Service Account

```bash
gcloud iam service-accounts create "qadms-deployer" \
  --project "notional-radio-474312-d4" \
  --display-name "QADMS GitHub Deployer"
```

## 3) Grant Required IAM Roles

Minimum roles for Cloud Run deploy (adjust as needed):

```bash
gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/run.admin"

gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/iam.serviceAccountUser"
```

If you push images to Artifact Registry/GCR, also grant:

```bash
gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/artifactregistry.writer"
```

## 4) Allow GitHub OIDC to Impersonate the Service Account

```bash
gcloud iam service-accounts add-iam-policy-binding \
  "qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/iam.workloadIdentityUser" \
  --member "principalSet://iam.googleapis.com/projects/779175721635/locations/global/workloadIdentityPools/qadms-github/attribute.repository/murdadrum/CodexQADMS"
```

## 5) Add GitHub Secrets

In repo settings, add:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
  - `projects/779175721635/locations/global/workloadIdentityPools/qadms-github/providers/qadms-provider`
- `GCP_SERVICE_ACCOUNT`
  - `qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com`

## 6) Run Deploy Workflow

Use the `Deploy Scaffold` workflow:
- `project_id`: `notional-radio-474312-d4`
- `region`: `us-central1`
- `api_image`, `web_image`: fully-qualified image tags
- `dry_run`: set to `false` when ready

## Notes

- The workflow expects prebuilt container images.
- Use `us-central1` for GCP (not `us-central-1`).
- The deploy job uses `gcloud run deploy` and supports `--set-env-vars` via comma-separated input strings.
