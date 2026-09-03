output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "Endpoint URL of the EKS cluster"
  value       = aws_eks_cluster.main.endpoint
}

output "rds_endpoint" {
  description = "Connection endpoint of the RDS database"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "ecr_frontend_url" {
  description = "ECR URL for the frontend image"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_backend_url" {
  description = "ECR URL for the backend image"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_ai_service_url" {
  description = "ECR URL for the AI microservice image"
  value       = aws_ecr_repository.ai_service.repository_url
}