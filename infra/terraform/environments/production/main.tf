module "qadms" {
  source = "../../"

  project_id  = var.project_id
  region      = var.region
  environment = "production"

  api_image = var.api_image
  web_image = var.web_image

  api_env_vars = var.api_env_vars
  web_env_vars = var.web_env_vars
}
