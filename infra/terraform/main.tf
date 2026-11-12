data "aws_availability_zones" "available" { state = "available" }
locals { name = "${var.project}-${var.environment}"; azs = slice(data.aws_availability_zones.available.names, 0, 2) }

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  name = local.name
  cidr = var.vpc_cidr
  azs = local.azs
  private_subnets = [cidrsubnet(var.vpc_cidr, 4, 0), cidrsubnet(var.vpc_cidr, 4, 1)]
  public_subnets  = [cidrsubnet(var.vpc_cidr, 4, 8), cidrsubnet(var.vpc_cidr, 4, 9)]
  enable_nat_gateway = true
  single_nat_gateway = var.environment != "prod"
  enable_dns_hostnames = true
  public_subnet_tags = { "kubernetes.io/role/elb" = 1 }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }
}

module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"
  cluster_name = local.name
  cluster_version = var.cluster_version
  cluster_endpoint_public_access = true
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  enable_cluster_creator_admin_permissions = true
  eks_managed_node_groups = {
    default = {
      instance_types = var.node_instance_types
      min_size = var.min_nodes
      max_size = var.max_nodes
      desired_size = var.desired_nodes
    }
  }
}

resource "aws_s3_bucket" "rag" { bucket_prefix = "${local.name}-rag-" }
resource "aws_ecr_repository" "api" { name = "${local.name}-api"; image_scanning_configuration { scan_on_push = true } }
resource "aws_ecr_repository" "ui" { name = "${local.name}-ui"; image_scanning_configuration { scan_on_push = true } }
