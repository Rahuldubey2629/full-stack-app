output "vpc_id" {
  description = "VPC ID."
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  description = "Private subnet IDs."
  value       = [for subnet in aws_subnet.private : subnet.id]
}

output "internet_gateway_id" {
  description = "Internet Gateway ID."
  value       = aws_internet_gateway.this.id
}

output "nat_gateway_ids" {
  description = "NAT Gateway IDs."
  value       = [for nat in aws_nat_gateway.this : nat.id]
}
