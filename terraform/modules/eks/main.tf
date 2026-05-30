locals {
  tags = merge(var.tags, {
    "Name"        = var.cluster_name
    "Environment" = var.environment
  })
}

resource "aws_security_group" "cluster" {
  name        = "${var.cluster_name}-cluster-sg"
  description = "EKS cluster security group"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_eks_cluster" "this" {
  name     = var.cluster_name
  version  = "1.34"
  role_arn = var.cluster_role_arn

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.cluster.id]
  }

  tags = local.tags

}

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids

  scaling_config {
    desired_size = var.node_count
    max_size     = var.node_count + 1
    min_size     = 1
  }

  instance_types = [var.node_instance_type]

  tags = local.tags

}
