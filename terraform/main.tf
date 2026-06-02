module "vpc" {
  source = "./modules/vpc"

  name_prefix        = var.name_prefix
  vpc_cidr           = var.vpc_cidr
  azs                = var.azs
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway
  tags               = local.tags
}

module "eks" {
  source = "./modules/eks"

  cluster_name       = var.cluster_name
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  cluster_role_arn   = module.iam.cluster_role_arn
  node_role_arn      = module.iam.node_role_arn
  node_instance_type = var.node_instance_type
  node_count         = var.node_count
  environment        = var.environment
  tags               = local.tags
}

module "iam" {
  source = "./modules/iam"

  cluster_name = var.cluster_name
  environment  = var.environment
  tags         = local.tags
}

module "ecr" {
  source = "./modules/ecr"

  repository_names = var.ecr_repository_names
  tags             = local.tags
}