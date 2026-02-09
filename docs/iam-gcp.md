# GCP IAM + Auth Setup (Staging + Production)

This doc defines recommended IAM and auth setup for QADMS deployments on Google Cloud Run.

## Environments

- Staging project: `notional-radio-474312-d4`
- Production project: define when ready (use a separate GCP project for isolation)
- Region: `us-central1`

## Service Accounts

Create separate service accounts per environment:

```bash
gcloud iam service-accounts create "qadms-api-staging" \
  --project "notional-radio-474312-d4" \
  --display-name "QADMS API (staging)"

gcloud iam service-accounts create "qadms-web-staging" \
  --project "notional-radio-474312-d4" \
  --display-name "QADMS Web (staging)"
```

For production, use analogous service accounts in the production project:

- `qadms-api-prod`
- `qadms-web-prod`

## IAM Roles (Runtime)

Minimum roles for Cloud Run services:

```bash
# API runtime
gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-api-staging@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/run.invoker"

# Web runtime (if it calls API directly)
gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-web-staging@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/run.invoker"
```

If using Artifact Registry for images:

```bash
gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-api-staging@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/artifactregistry.reader"

gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-web-staging@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/artifactregistry.reader"
```

## Deploy Service Account (CI/CD)

Use a dedicated deployer for GitHub Actions, as described in `docs/deploy-gcp.md`:

- `qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com`

Roles for deployer:

```bash
gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/run.admin"

gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding "notional-radio-474312-d4" \
  --member "serviceAccount:qadms-deployer@notional-radio-474312-d4.iam.gserviceaccount.com" \
  --role "roles/artifactregistry.writer"
```

## Service-to-Service Auth Options

Option A (simple): Public Cloud Run services
- Use `--allow-unauthenticated` in deploy
- Protect via app-level auth and rate limiting

Option B (recommended for production): Private Cloud Run + IAM
- Do not use `--allow-unauthenticated`
- Web service uses IAM identity to call API
- Issue service account identity tokens from web and call API

## Firebase Auth

- Firebase client auth is used in web UI for gated actions.
- For production, configure Firebase project to match domain and set allowed origins.

## Notes

- Use separate projects for staging/production to reduce blast radius.
- Avoid granting `roles/editor` or owner-like roles to runtime service accounts.
