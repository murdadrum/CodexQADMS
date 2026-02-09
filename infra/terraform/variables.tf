variable "project_id" {
  type        = string
  description = "Cloud project id"
}

variable "region" {
  type        = string
  description = "Primary region"
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "staging"
}

variable "api_image" {
  type        = string
  description = "Container image for API"
  default     = "gcr.io/example/qadms-api:latest"
}

variable "web_image" {
  type        = string
  description = "Container image for web"
  default     = "gcr.io/example/qadms-web:latest"
}

variable "api_env_vars" {
  type        = map(string)
  description = "Environment variables for API service"
  default     = {}
}

variable "web_env_vars" {
  type        = map(string)
  description = "Environment variables for web service"
  default     = {}
}
