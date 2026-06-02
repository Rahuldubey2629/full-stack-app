locals {
  tags = var.tags
}

resource "aws_ecr_repository" "this" {
  for_each = toset(var.repository_names)

  name                 = each.value
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  tags = merge(local.tags, {
    "Name" = each.value
  })
}

resource "aws_ecr_lifecycle_policy" "expire_older_images" {
  for_each   = aws_ecr_repository.this
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire images older than 10 days"
        selection = {
          tagStatus   = "any"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
