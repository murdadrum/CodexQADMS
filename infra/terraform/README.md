# Terraform Skeleton

This directory contains the baseline Terraform layout for QADMS.

## Structure
- `environments/` per-environment root modules
- `modules/` reusable module definitions
- `versions.tf` provider/version pins

## Usage (scaffold)

```bash
cd /Users/murdadrum/QADMS/infra/terraform/environments/staging
cp backend.tf.example backend.tf
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
```

Replace the backend and provider configuration with your cloud details.
