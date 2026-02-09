variable "project_id" {
  type        = string
  description = "Cloud project id"
}

variable "region" {
  type        = string
  description = "Primary region"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
}

variable "api_image" {
  type        = string
  description = "API container image"
}

variable "web_image" {
  type        = string
  description = "Web container image"
}

variable "api_env_vars" {
  type        = map(string)
  description = "Environment variables for API"
  default     = {}
}

variable "web_env_vars" {
  type        = map(string)
  description = "Environment variables for web"
  default     = {}
}
