terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket       = "devpulse-terraform-state-167535219723" # your bucket name
    key          = "devpulse/terraform.tfstate"            # path inside bucket e.g. "devpulse/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
    encrypt      = true
    # profile      = "devpulse-infra" # optional if you have multiple AWS profiles configured
  }
}
