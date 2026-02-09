output "api_service_name" {
  value       = google_cloud_run_service.api.name
  description = "API Cloud Run service name"
}

output "web_service_name" {
  value       = google_cloud_run_service.web.name
  description = "Web Cloud Run service name"
}
