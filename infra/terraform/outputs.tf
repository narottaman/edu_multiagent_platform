output "cluster_name" { value = module.eks.cluster_name }
output "cluster_endpoint" { value = module.eks.cluster_endpoint }
output "rag_bucket" { value = aws_s3_bucket.rag.bucket }
output "api_ecr" { value = aws_ecr_repository.api.repository_url }
output "ui_ecr" { value = aws_ecr_repository.ui.repository_url }
