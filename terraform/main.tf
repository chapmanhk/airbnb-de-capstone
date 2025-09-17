provider "aws" {
  region                  = var.aws_region
  access_key              = var.aws_access_key
  secret_key              = var.aws_secret_key
}

# Generate a unique suffix from the AWS account ID and region
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  bucket_suffix = "${data.aws_caller_identity.current.account_id}-${data.aws_region.current.region}"
}

resource "aws_s3_bucket" "raw_data" {
  bucket = "airbnb-la-raw-data-${local.bucket_suffix}"
  force_destroy = true
  tags = {
    Name        = "airbnb-raw-data"
    Environment = "dev"
    Project     = "decapstone"
    Owner       = "hannah-ofstedahl"
  }
}

resource "aws_s3_bucket" "cleaned_data" {
  bucket = "airbnb-la-cleaned-data-${local.bucket_suffix}"
  force_destroy = true
  tags = {
    Name        = "airbnb-cleaned-data"
    Environment = "dev"
    Project     = "decapstone"
    Owner       = "hannah-ofstedahl"
  }
  
}

resource "aws_s3_bucket" "models" {
  bucket = "airbnb-la-models-${local.bucket_suffix}"
  force_destroy = true
  tags = {
    Name        = "airbnb-models"
    Environment = "dev"
    Project     = "decapstone"
    Owner       = "hannah-ofstedahl"
  }
  
}

resource "aws_s3_bucket" "predictions" {
  bucket = "airbnb-la-predictions-${local.bucket_suffix}"
  force_destroy = true
  tags = {
    Name        = "airbnb-predictions"
    Environment = "dev"
    Project     = "decapstone"
    Owner       = "hannah-ofstedahl"
  }
}
