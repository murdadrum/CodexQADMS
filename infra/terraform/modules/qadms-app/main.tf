locals {
  api_env = var.api_env_vars
  web_env = var.web_env_vars
}

resource "google_cloud_run_service" "api" {
  name     = "qadms-api-${var.environment}"
  location = var.region

  template {
    spec {
      containers {
        image = var.api_image
        dynamic "env" {
          for_each = local.api_env
          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service" "web" {
  name     = "qadms-web-${var.environment}"
  location = var.region

  template {
    spec {
      containers {
        image = var.web_image
        dynamic "env" {
          for_each = local.web_env
          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
