terraform {
  required_version = ">= 1.16.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.36"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.17"
    }
  }

  backend "s3" {
    bucket  = "ai-log-analyser-tfstate-jecinta"
    key     = "terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }

}

provider "aws" {
  region  = var.aws_region
  profile = "aws"
}